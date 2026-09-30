---
name: release
description: Use this skill when the user invokes `/factory:release`, or asks how far behind production is, what is merged but not released, to release or ship a component, to cut a tag, to walk a release to staging or production, or to verify what an environment is actually running.
---
# factory:release

Is it running where users are, and how far behind is production?

This skill runs recipe [`recipes/08-release.md`](../../recipes/08-release.md) against the current
repo's profile. The recipe is the authority: read it before the first run in a session, and when this
file and the recipe disagree, the recipe wins. Improve the recipe, not this file.

## Modes

| Invocation | Does | Tier |
|---|---|---|
| `factory:release` or `status [component]` | Distance per component and what each environment runs | Alone |
| `cut <component>` | Claim the release, pick the version, tag a gated tree, verify the artifact | Tag push on the word |
| `walk <component> <version>` | Every hop of the chain after the tag, one at a time | Each outward hop on the word |
| `verify <environment> [component]` | Digest on the running workloads, then the user path | Alone (reads only) |

With no mode, run `status`, then offer the one next step it shows.

## Step 0: read the profile (gate)

Read every `CLAUDE.md` in scope (the repo's, and any parent directory's that the session loaded) and
find the **Release chain** section (`templates/profile.md`). It must name:

1. The components and where each is tagged (repo, tag format).
2. Every hop after the tag, in order, and who or what performs it (a workflow, a bot, a person).
3. How each environment picks its image, and where that is read (a pin, a moving tag, an override).
4. How production is triggered, and that a merge can't do it.

If the section is missing or leaves one of these out, stop:

```
✗ factory:release needs the profile's Release chain.

Missing: <which of the four>
Add a "## Release chain" section to CLAUDE.md (skeleton: templates/profile.md in software-factory).
A release walked from memory ships to an environment that moved on weeks ago.
```

Then read `docs/authority.md`. Every hop that is visible to others or hard to undo waits for the
person's word **for that hop**; a yes to the tag is not a yes to the merge after it.

## status

1. **Distance, per component.** Latest published release, then the commits on the default branch since
   it (`gh release list`, `gh api repos/<o>/<r>/compare/<tag>...<default>`). List the user-visible
   ones by subject. Merged into another branch doesn't count as waiting for release.
2. **Where each environment is.** Read the environment's image source from the profile's location on
   the deploy repo's default branch (not from memory, not from the rule file's description), then the
   digest actually running if the session can read the cluster (step 8 of the recipe).
3. **Open hops.** Open PRs of the chain (pin bumps, environment bumps), drafts, and their checks.
4. Report in the recipe's output shape, then one line: the next hop and whose it is.

## cut

1. **Claim it.** Read the shared session log the profile names (or `.remember/now.md`), list the other
   agent sessions, and ask anyone holding a release thread for this component before going on. If
   another session owns it, stop and say so; don't tag in parallel.
2. **Pick the version** from the tag format and the latest tag, re-read at this moment.
3. **Gated tree.** The commit is on the default branch and its CI run there is green, every job, by
   name (recipe 05, step 6). Name the run.
4. **Show the tag command and wait for the word.** Then push an annotated tag.
5. **Verify the artifact, not the workflow**: registry tag and digest, every architecture. Record the
   digest; it's what `verify` compares against. A rebuilt tag has a new digest even for the same commit.

## walk

For each hop after the tag, in the profile's order:

1. **Wait for the previous hop's artifact to exist.** A chart that isn't published yet can't be pinned
   in an environment; a draft PR may be opened early to see its preview fail, never merged early.
2. **Re-read the version file on the target repo's default branch** right before opening a PR and
   again right before merging. Versions race with every other releaser.
3. **If the hop belongs to a bot, wait for the bot** for its usual time; if nothing comes, read the
   dispatch run before writing the change by hand.
4. **Draft the PR body** from what the release carries (the commit subjects since the last tag), what
   the hop restarts, and what it deliberately doesn't change. Show it; open it on the word.
5. **Read back** every write (title, body, base, draft flag), and grep a preview job's log for the
   environment's own step before calling it green (recipe 05, step 11).
6. **Production** is a person-authored change plus a deliberate trigger. Prepare both; trigger nothing.

Stop at the first hop that waits on someone else, and say whose it is and what unblocks it.

## verify

1. Running workloads' image IDs against the release digest from `cut` (or the registry's digest for the
   tag), per component.
2. The user path on real data: open what the release changed, as a user would. Readiness probes don't count.
3. Record where each component now is, per environment, in memory or the tracker. That's state: it never
   goes into the profile or a recipe.

## Output

The recipe's block, filled in:

```
distance: <component> <n> commits since <tag> (<k> user-visible)
cut:      <tag> at <sha> (gated run <id>); registry: <tag> <digest>, <archs> ✓
chain:    <hop> ✓ · <hop> open (#n, waits on <whom>) · <hop> not started
verify:   <env> <component> imageID = release digest ✓ / ✗; user path ✓ / not checked
prod:     <where it is, and the one thing that moves it>
```

## When it bites

Anything that went wrong on this run goes through recipe 09 (Ratchet): a trap line in recipe 08 if it's
general, a line in the profile's Release chain if it's this repo's, never both.
