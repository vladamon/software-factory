# 07 · Land

Is it on main, and is everything around it still true?

Merging is one click. Landing means the commit is on main, the PRs stacked on it now point at main, the
tracker shows the right state, and each of those facts was confirmed by reading it back. On this station
the default failure is silent: a tool reports success and nothing changed.

## When to use

Every merge. For stacks, every merge in the stack, one at a time.

## Inputs I need before starting

- The person's word for **this** merge ([`docs/authority.md`](../docs/authority.md)).
- The approved sha, and the PR's head sha. They must match.
- The profile's **Git and PRs** section (tool workarounds) and **Reviewers and ground** (merge policy).

## Steps

### A single PR

1. **Check review state, not only CI.** No changes requested, no reviewer comment holding back approval,
   and the approval is on the head sha. If commits landed after the approval, it's stale.
2. **Re-check shared sequence numbers.** Fetch, and compare the branch's migration numbers (or version
   pins, or anything numbered by hand) against main's latest. Renumber on collision and say so in the
   commit.
3. **Merge.**
4. **Prove it landed.** `git fetch`, then `git grep <a symbol the PR added> origin/main`. The merge
   button isn't proof.
5. **Set tracker state after automations fire.** PR-open and merge automations change ticket state a
   second or so after the event. Set the state you want after that, then read it back.

### A stack

Merge the **bottom** PR only. Then, for its direct child:

6. **Don't delete the base branch with the merge.** Delete it only after the child is retargeted
   (step 9).
7. **Rebase the child on main.** The squash rewrote the base's commits; the child still carries the
   originals.
8. **Retarget explicitly** to main, through the API if the CLI's edit command is unreliable (see the
   profile).
9. **Read back the child's base** (`baseRefName`). Only when it says `main`, delete the old base
   branch.
10. **Run the gate on the child again.** Its earlier green was against the old base.
11. Repeat from the child. **Never merge a stack top-down:** a merged child whose base never landed
    leaves its code in a branch nobody will merge again.

### Every write

12. **Read back every write** to the code host or the tracker: title, body, base, state, assignee,
    description. Confirm a field that had to change has changed (an `updatedAt` that moved, a base
    that reads `main`).

## What good output looks like

A short landing note, in the session log or the PR:

```
#412 merged 3f9c2e1 (approved sha = head). origin/main grep: parseScope ✓.
#413 rebased on 3f9c2e1, PATCH base=main, baseRefName=main ✓, gate re-run green on a71b0d4.
old base deleted. ticket → Done (read back ✓).
```

## Done means

- The PR's own symbol greps on `origin/main`.
- Every child in the stack reads `baseRefName: main` and has a green gate on its new head.
- The tracker state was read back after the automations fired.
- No other person's ticket key appears in a title or branch you created (automations act on any mention).

## Traps

- **The dead base.** The code host retargets a child automatically only when its base branch is
  *deleted*. A merged base left in place kept the child pointed at it, with green checks.
  → Steps 6–9, in that order.
- **Top-down bulk merge.** Merging a stack from the top left the lower PRs' code merged only into
  branches that were never merged again. → Bottom only, one at a time; orphans are found with
  `git grep` on main.
- **The edit that prints an error and changes nothing.** The CLI's PR-edit command failed on an
  unrelated API field, printed the error, and left the PR untouched. → Use the REST call the profile
  names, then read back.
- **The patch that misses its anchor.** A tracker `patch` edit returned success and did nothing because
  its anchor text wasn't found. → Send the full field, then read back `updatedAt`.
- **Someone else's key in your title.** The tracker marked a teammate's ticket *Merged* because its
  key appeared in a workaround PR's title. → Other people's keys go in the body, as prose.
- **The automation that runs after you.** Setting *In Review* right after opening the PR was undone
  a second later by the PR-open automation. → Step 5.
- **The approval from ten commits ago.** A PR merged on a stale approval carried ten unreviewed commits
  to main. → Step 1.
