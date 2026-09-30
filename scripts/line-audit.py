#!/usr/bin/env python3
"""Measure the line (docs/line.md, Measures) for one or more GitHub repos.

Reads only through the `gh` CLI, so it sees what the logged-in account can see.
Nothing is written anywhere; the report goes to stdout (Markdown, or JSON with --json).

    scripts/line-audit.py owner/repo [owner/repo ...] [--days 30] [--runs 40] [--json]

What it measures, per repo:
  lead time      PR opened -> merged, and merged -> first release that contains the merge
  review wait    ready for review -> first review by someone other than the author
  in flight      open PRs per author, drafts counted apart
  red rate       per CI job, over the last --runs completed push runs on the default branch
  distance       commits on the default branch since the latest release, and the oldest one's age

What it doesn't: time to each environment (that lives in the deploy repo and differs per
profile), defects found after merge, and rules added or deleted (both need the tracker).
"""

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Completed runs and published releases never change, so their API reads are kept on disk and a
# weekly audit only pays for what is new. The reserve is left for everything else on the account.
CACHE = Path(os.environ.get('LINE_AUDIT_CACHE', Path.home() / '.cache' / 'line-audit'))
RESERVE = 1000

PR_QUERY = """
query($q: String!, $after: String) {
  search(query: $q, type: ISSUE, first: 50, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        number title createdAt mergedAt baseRefName
        author { login __typename }
        mergeCommit { oid }
        timelineItems(itemTypes: [READY_FOR_REVIEW_EVENT], last: 1) {
          nodes { ... on ReadyForReviewEvent { createdAt } }
        }
        reviews(first: 30) { nodes { createdAt author { login } } }
      }
    }
  }
}
"""


def gh(*args, tries=4):
    """Run gh; retry the server errors a long audit meets (HTTP 5xx), fail on anything else."""
    for attempt in range(tries):
        out = subprocess.run(['gh', *args], capture_output=True, text=True)
        if out.returncode == 0:
            return out.stdout
        if 'HTTP 5' not in out.stderr or attempt == tries - 1:
            raise RuntimeError(f"gh {' '.join(args[:3])}: {out.stderr.strip()}")
        time.sleep(2 ** attempt)
    return ''


def gh_json(*args):
    return json.loads(gh(*args) or 'null')


def gh_pages(path, key=None):
    """REST list endpoint, every page, flattened. `key` names the list inside a wrapped page."""
    out = gh('api', '--paginate', '--slurp', path)
    return [item for page in json.loads(out) for item in (page[key] if key else page)]


def cached(key, fetch):
    path = CACHE / f'{key}.json'
    if path.exists():
        return json.loads(path.read_text())
    value = fetch()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))
    return value


def rest_remaining():
    """Requests left, read from a real response's headers. The `rate_limit` endpoint can report the
    next window's full budget while requests are still refused."""
    out = subprocess.run(['gh', 'api', '-i', 'user'], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.lower().startswith('x-ratelimit-remaining:'):
            return int(line.split(':')[1])
    return 0


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def hours(a, b):
    return (b - a).total_seconds() / 3600


def spread(values):
    """p50 / p90 / n of a list of hours, or None when empty."""
    if not values:
        return None
    v = sorted(values)
    p90 = v[min(len(v) - 1, int(round(0.9 * (len(v) - 1))))]
    return {'p50': statistics.median(v), 'p90': p90, 'n': len(v)}


def merged_prs(repo, since):
    prs, after = [], None
    q = f'repo:{repo} is:pr is:merged merged:>={since:%Y-%m-%d}'
    while True:
        args = ['api', 'graphql', '-f', f'query={PR_QUERY}', '-f', f'q={q}']
        if after:
            args += ['-f', f'after={after}']
        page = gh_json(*args)['data']['search']
        prs += [n for n in page['nodes'] if n]
        if not page['pageInfo']['hasNextPage']:
            return prs
        after = page['pageInfo']['endCursor']


def releases(repo):
    rel = [r for r in gh_pages(f'repos/{repo}/releases?per_page=100')
           if not r['draft'] and r.get('published_at')]
    return sorted(rel, key=lambda r: r['published_at'])


def release_of_commit(repo, rels, since):
    """Map each commit to the first release that shipped it: one compare per consecutive pair of
    releases published since the window opened, instead of one per PR."""
    shipped = {}
    for prev, cur in zip(rels, rels[1:]):
        if ts(cur['published_at']) < since:
            continue
        a, b = prev['tag_name'], cur['tag_name']
        shas = cached(f"{repo}/compare/{a}...{b}".replace('/', '_'), lambda: [
            c['sha'] for c in gh_pages(f'repos/{repo}/compare/{a}...{b}?per_page=100', 'commits')])
        for sha in shas:
            shipped.setdefault(sha, cur)
    return shipped


def review_wait(pr):
    author = (pr.get('author') or {}).get('login')
    ready_ev = pr['timelineItems']['nodes']
    ready = ts(ready_ev[0]['createdAt']) if ready_ev else ts(pr['createdAt'])
    others = [ts(r['createdAt']) for r in pr['reviews']['nodes']
              if (r.get('author') or {}).get('login') != author]
    first = min((t for t in others if t >= ready), default=None)
    return hours(ready, first) if first else None, bool(others)


def is_bot(pr):
    return (pr.get('author') or {}).get('__typename') == 'Bot'


def red_rate(repo, default, n_runs, since):
    # Filter on status here, not in the query: with `status=` the API returns an older slice of
    # history instead of the newest runs.
    listed = gh_pages(f'repos/{repo}/actions/runs?branch={default}&event=push'
                      f'&created=>={since:%Y-%m-%d}&per_page=100', 'workflow_runs')
    done = sorted((r for r in listed if r['status'] == 'completed'),
                  key=lambda r: r['created_at'], reverse=True)[:n_runs]
    runs = [r['id'] for r in done]
    span = (done[-1]['created_at'][:10], done[0]['created_at'][:10]) if done else None
    tally = defaultdict(Counter)

    def key(run_id):
        return f"{repo}/jobs/{run_id}".replace('/', '_')

    uncached = sum(not (CACHE / f'{key(r)}.json').exists() for r in runs)
    budget = rest_remaining() - RESERVE
    if uncached > budget:
        print(f'{repo}: {uncached} runs to fetch, {budget} requests above the reserve; '
              'rerun after the rate limit resets', file=sys.stderr)
        raise RuntimeError('rate budget')

    def jobs(run_id):
        return cached(key(run_id), lambda: [
            [j['name'], j['conclusion']]
            for j in gh_pages(f'repos/{repo}/actions/runs/{run_id}/jobs?per_page=100', 'jobs')])

    with ThreadPoolExecutor(8) as pool:
        for job_list in pool.map(jobs, runs):
            for name, conclusion in job_list:
                if conclusion in ('success', 'failure', 'timed_out'):
                    tally[name]['runs'] += 1
                    tally[name]['red'] += conclusion != 'success'
    table = {name: {'runs': c['runs'], 'red': c['red'], 'rate': c['red'] / c['runs']}
             for name, c in tally.items()}
    jobs_by_rate = dict(sorted(table.items(), key=lambda kv: -kv[1]['rate']))
    return {'branch': default, 'runs': len(runs), 'span': span, 'jobs': jobs_by_rate}


def distance(repo, rels, default):
    if not rels:
        return None
    latest = rels[-1]['tag_name']
    cmp = gh_json('api', f'repos/{repo}/compare/{latest}...{default}',
                  '--jq', '{ahead: .ahead_by, first: (.commits[0].commit.committer.date // null)}')
    age = 0.0
    if cmp['ahead'] and cmp['first']:
        age = hours(ts(cmp['first']), datetime.now(timezone.utc)) / 24
    return {'since': latest, 'commits': cmp['ahead'], 'oldest_days': age}


def in_flight(repo):
    open_prs = gh_pages(f'repos/{repo}/pulls?state=open&per_page=100')
    per = defaultdict(lambda: {'ready': 0, 'draft': 0})
    for p in open_prs:
        per[p['user']['login']]['draft' if p['draft'] else 'ready'] += 1
    return dict(sorted(per.items(), key=lambda kv: -sum(kv[1].values())))


def audit(repo, days, n_runs):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    default = gh_json('api', f'repos/{repo}', '--jq', '{b: .default_branch}')['b']
    merged, rels = merged_prs(repo, since), releases(repo)
    # A PR merged into another branch (a stack base, a feature branch) reaches the default branch
    # through a later PR, so only PRs merged to the default branch are measured.
    # The search filters by date only; trim to the exact window so its edge matches the releases'.
    merged = [p for p in merged if ts(p['mergedAt']) >= since]
    prs = [p for p in merged if p['baseRefName'] == default]

    if rest_remaining() < RESERVE:
        raise RuntimeError(f'fewer than {RESERVE} REST requests left; rerun after the reset')
    shipped = release_of_commit(repo, rels, since)
    released = [shipped.get((p.get('mergeCommit') or {}).get('oid')) for p in prs]

    open_to_merge, merge_to_release, waits = [], [], []
    unreviewed = unreleased = bots = 0
    for pr, rel in zip(prs, released):
        open_to_merge.append(hours(ts(pr['createdAt']), ts(pr['mergedAt'])))
        if rel:
            merge_to_release.append(hours(ts(pr['mergedAt']), ts(rel['published_at'])))
        else:
            unreleased += 1
        if is_bot(pr):
            bots += 1
            continue
        wait, reviewed = review_wait(pr)
        if wait is not None:
            waits.append(wait)
        if not reviewed:
            unreviewed += 1

    rr = red_rate(repo, default, n_runs, since)
    return {
        'repo': repo, 'days': days, 'merged': len(prs), 'releases': len(rels),
        'merged_elsewhere': len(merged) - len(prs),
        'open_to_merge_h': spread(open_to_merge),
        'merge_to_release_h': spread(merge_to_release),
        'merged_not_released': unreleased if rels else None,
        'review_wait_h': spread(waits),
        'merged_by_bots': bots,
        'merged_without_review': unreviewed,
        'in_flight': in_flight(repo),
        'distance': distance(repo, rels, rr['branch']),
        'red_rate': rr,
    }


def fmt_spread(s):
    if not s:
        return 'n/a'
    def unit(h):
        return f'{h * 60:.0f} min' if h < 1 else f'{h:.1f} h' if h < 48 else f'{h / 24:.1f} d'
    return f"p50 {unit(s['p50'])}, p90 {unit(s['p90'])} (n={s['n']})"


def markdown(r):
    lines = [f"## {r['repo']}", '',
             f"Window: last {r['days']} days, {r['merged']} PRs merged to `{r['red_rate']['branch']}`, "
             f"{r['merged_elsewhere']} merged into other branches ({r['releases']} releases all time).", '',
             '| Measure | Value |', '|---|---|',
             f"| Lead time, opened → merged | {fmt_spread(r['open_to_merge_h'])} |"]
    if r['releases']:
        lines.append(f"| Lead time, merged → released | {fmt_spread(r['merge_to_release_h'])} |")
        lines.append(f"| Merged in window, not yet released | {r['merged_not_released']} |")
    else:
        lines.append('| Lead time, merged → released | no releases |')
    people = r['merged'] - r['merged_by_bots']
    lines.append(f"| Review wait, ready → first review (people's PRs) | {fmt_spread(r['review_wait_h'])} |")
    lines.append(f"| People's PRs merged with no review by anyone else | {r['merged_without_review']} of {people} |")
    lines.append(f"| Bot PRs merged | {r['merged_by_bots']} |")
    d = r['distance']
    if d:
        lines.append(f"| On {r['red_rate']['branch']}, not released | {d['commits']} commit(s) since "
                     f"`{d['since']}`, oldest {d['oldest_days']:.1f} d |")
    fl = r['in_flight']
    total = sum(sum(v.values()) for v in fl.values())
    who = ', '.join(f"{k} {v['ready']}+{v['draft']}d" for k, v in fl.items()) or 'none'
    lines.append(f"| In flight (open PRs, ready+draft) | {total}: {who} |")
    rr = r['red_rate']
    span = f", {rr['span'][0]} to {rr['span'][1]}" if rr['span'] else ''
    lines += ['', f"Red rate per job, last {rr['runs']} completed push runs on `{rr['branch']}`{span}"
              ' (cancelled and skipped jobs not counted):', '',
              '| Job | Red | Runs | Rate |', '|---|---|---|---|']
    lines += [f"| {name} | {j['red']} | {j['runs']} | {j['rate']:.0%} |" for name, j in rr['jobs'].items()]
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description='Measure the line for one or more GitHub repos.')
    ap.add_argument('repos', nargs='+', help='owner/repo')
    ap.add_argument('--days', type=int, default=30, help='merged-PR window (default 30)')
    ap.add_argument('--runs', type=int, default=300, help='newest push runs inside --days for red rate (default 300)')
    ap.add_argument('--json', action='store_true', help='JSON instead of Markdown')
    a = ap.parse_args()

    results = []
    for repo in a.repos:
        try:
            results.append(audit(repo, a.days, a.runs))
        except RuntimeError as e:
            print(f'{repo}: {e}', file=sys.stderr)
    if a.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        print(f'# Line audit, {stamp}\n')
        print('\n\n'.join(markdown(r) for r in results))
    return 1 if len(results) < len(a.repos) else 0


if __name__ == '__main__':
    sys.exit(main())
