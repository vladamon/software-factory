# 02 — Map

What actually exists, hop by hop?

Agents build confidently on what they're told the system does. Docs, code comments and teammates'
memories all describe a system that existed at some point, and the wire often disagrees with all
three. This station traces the few facts a piece of work depends on through the real code, from where
each fact is born to where a user sees it, before anyone designs against them. A good map is often the
most valuable thing a month produces, even though no PR ships it.

## When to use

- Before a feature that crosses more than two components or repos.
- Before filing asks against another team's layer (Intake, recipe 01). Asks that cite a hop get
  answered; asks built on guesses get argued about.
- Before touching an area for the first time: at minimum, read its design doc (step 1).
- When two people describe the same behaviour differently.

## Inputs I need before starting

- The work's question, in the user's terms ("why does the Agent page show no history?").
- The 3 to 5 **facts** the work depends on, each named as something that travels, like "a heartbeat",
  "an error", "a tool call". More than five means the work is several pieces.
- Read access to every repo the facts pass through, each fetched and read at a named commit on main.

## Steps

### For a small change

1. **Read the area's design doc before touching it.** When the area has none and the change sets a
   contract, write the design doc first, as its own PR, and cite it by section from the feature commits.
2. **Read the decision behind a precedent before copying it.** The commit body or file header of the
   sibling you're imitating says why it was done that way (Build, recipe 03, step 5).

For a change inside one component, that's the whole station. The rest is for work that crosses
components.

### For a cross-cutting piece of work

3. **Pin the commits.** Record the repo and commit you read for every repo in the trace, in a table at the
   top. Read `origin/main` (or `git show <ref>:<path>`), not whatever branch the local checkout is on.
   Every line number in the map is only true at those commits.
4. **Trace one fact at a time, from birth to screen.** One hop table per fact, with these columns:

   | # | Hop | Where (repo/path:line) | Shape (names verbatim) | Storage + retention | Contract doc | What changes or is lost here |
   |---|---|---|---|---|---|---|

   The last column is the point. Stamped, renamed, dropped, recomputed, overwritten: each loss is
   noted at the hop where it happens.
5. **Read code before docs.** Trace the code first, then check each doc and comment against it, and list
   every disagreement under the fact with both locations. Docs that are cited but don't exist count as
   disagreements too.
6. **Check the side hops.** For each fact, check the components that *could* consume it but might not
   (alerting, the agent-facing API, the analytics store) and say explicitly "does not read this". An
   absence is a finding.
7. **Draw the flow.** One diagram per fact, following the hop table, with dotted edges for what's
   expected but missing.
8. **Put the findings that change the plan first.** Above the traces, list the few facts that
   contradict what the work assumed, each pointing to its evidence section.
9. **Map each ask to its hop.** For every capability the work needs, name the exact hop that has to
   change. Asks and tickets get written *afterwards*, citing the hop row. The map itself proposes no design.
10. **Collect questions by person.** Everything the code couldn't answer, grouped by who can answer
    it, so each person gets one short list.

### Keeping it true

11. **Date it, and add deltas instead of rewriting.** When the code moves (a merge the same evening, an
    SDK release the next week), append a dated delta section saying which findings changed. Mark a
    finding STALE where it's stated, with a pointer to the delta.
12. **Re-check before quoting.** Before citing a hop in a ticket or review, re-read those lines at
    current main. Line numbers drift; claims drift further.

## What good output looks like

A dated file in the repo's planning directory:

```markdown
# System map: four facts traced from SDK to console

Date. 2026-09-14. Method. Code read hop by hop, one trace per fact, then reconciled against the docs.

| Repo | Commit read |
|---|---|
| sdk-python | 3b7e0a2 |
| backend | 9c41f5d (main) |

The five findings that change the plan
1. No history of X exists anywhere: the store keeps one revision per key, and status is computed on read. (§1)
2. "Errors" means four different counts on the wire, and the page's headline and the list beneath it use different ones. (§3)

## 1. Fact: a heartbeat
### A. Hop table   ### B. Flow   ### C. Answers   ### D. Code vs docs   ### E. Open questions
…
## 5. Asks mapped to hops
## 6. Questions by person
## 8. Delta 2026-09-14 evening: <what merged, which findings moved>
```

## Done means

- Every fact the work depends on has a hop table from birth to screen, at pinned commits.
- Every loss is named at its hop, and every doc/code disagreement is listed with both locations.
- The findings that change the plan are at the top, each with evidence.
- Every ask is mapped to a hop, and every open question to a person.
- The map is dated, and stale claims are marked where they're stated.

## Traps

- **The contract doc that did not exist.** Three code comments pointed readers to a contract document
  for the heartbeat. No such file existed in any repo. → Step 5: a cited doc that's missing is a finding.
- **The comment that assumed the opposite.** A backend comment said the SDKs stamp the agent name on
  spans. Neither did; the name reached only the heartbeat, so two views of "the agent" disagreed as soon
  as anyone set it. → Step 5: trust the code, then check the comment against it.
- **One word, four counts.** "Errors" was four different counts on the wire (errored spans, errored
  root spans, exception events, traces with any error), and a page's headline and the list below it
  used different ones. → Step 4: names verbatim, per hop.
- **The stale checkout.** Mid-trace, the local backend checkout turned out to sit on an old feature
  branch with an unpushed commit: code main never had. → Step 3: read `origin/main` at a named commit.
- **The subagent that went quiet.** A subagent given the widest trace stalled for ten minutes and wrote
  nothing. Relaunched with "write the output file incrementally, section by section", it finished.
  → Give each fact its own agent, and have agents write as they go.
- **The finding that went stale.** A finding about what the SDKs send was true when mapped and false
  nine days later. The only flag was a note in the agent's memory; the map itself still stated it.
  → Step 11.
