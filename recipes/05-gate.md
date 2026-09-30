# 05 · Gate

Does one command say yes, with no job allowed to stay red?

The gate is where the team's standards are enforced by a machine, which matters most when the code is
written by agents that don't remember the standards. It has one job: a green result has to mean
something. The procedure keeps it that way, both when running it and when changing it.

## When to use

- Running: after Prove, before asking for review, and again after every rebase.
- Reading: every time CI is red, before rerunning anything.
- Changing: when a rule with a machine-checkable signature is decided (recipe 09), or when a gate's
  verdict and reality disagree.

## Inputs I need before starting

- The profile's **The gate** section: the command, its jobs in order, preconditions, and what it skips.
- The sha being gated.
- For a red CI job: the job's own log and annotations, and main's latest result for the same job.

## Steps

### Running the gate

1. **Meet the preconditions first.** Runtime version, env vars that must be off, services that must be
   up. A missed precondition fails with an error that looks unrelated.
2. **Run the one command, whole, on the sha you will push.** Not a subset, and not "build passes". Name
   the sha in the PR body.
3. **Read the gate's own result.** Its exit status, not a wrapper's, and its last lines. For the test jobs,
   the count of tests that ran (recipe 04).
4. **After every rebase, run it whole again.** A rename on main merges cleanly into the code and breaks
   only a test file, with no conflict marker. A behaviour change on main (a new special case, a new
   fallback) breaks nothing and gives a false green. Re-read what landed in the files you share, not
   just the conflicts.

### Reading red

5. **Classify before you rerun.**

   | Signature | Class | Action |
   |---|---|---|
   | No steps, a few seconds, no log | Infrastructure (billing, runner, quota) | Read the job's annotations. A rerun can't help until the account is fixed; tell the owner. |
   | Fails on main too, same job | Main is broken | Not yours to hide; fix or report, don't rerun |
   | Passes alone, fails under load, timing-shaped | Flake | Prove it passes alone, record it, ticket it with an owner |
   | Anything else | Real | Fix it |

6. **No expected red.** A job that stays red gets fixed or re-scoped within days, never learned as
   "the one that's always red". Once one job is allowed to stay red, people stop reading red at all.
7. **Budget failures: get main's baseline first.** Coarse budgets (total bundle size, total runtime)
   trip on whatever change comes next once they're nearly exhausted, regardless of that change's size.
   Read main's number from its CI log, measure your own delta locally, then decide.
8. **Raising a budget.** Bump the number and append one sentence to the budget's own comment: measured
   before and after, what was added, whether a dependency is new, and that the hard floor is unchanged.
   That comment is the decision log. Leave real headroom (a raise that leaves 2% repeats the trap for the
   next person). A raise that adds a dependency needs the owner's OK. When two branches raise the same
   line, keep the higher number and both rationales.

### Keeping the gate honest

9. **Audit coverage, not just the verdict.** For each job, check what it actually looks at: which URLs,
   which globs, which modules. A gate measures only what it's pointed at.
10. **Check that the tool saw the files.** Count them. A linter run from a directory with no module in it
    reports clean having linted nothing, and a glob by file extension waves through any stray file with
    a different one.
11. **`continue-on-error` is decoration.** A job marked that way can fail inside a green check. Grep its
    log for the step's own result before claiming it passed.

### Adding to the gate

12. **If it has a signature, it becomes a gate.** A pattern in the AST, a file that must exist, an import
    that must not cross a boundary, a number that must not rise. It hard-fails from commit one, before
    there is a precedent to point to.
13. **Land it with the rule.** One PR holds the gate, the code that satisfies it, and the one-line prose
    rule that now says "enforced by `<job>`" (recipe 09).
14. **Name it in the profile.** Add the job to the profile's gate list and to its precondition notes
    if it has any.

## What good output looks like

```
gate: <command> on 4e1b2c9, all 12 jobs green, exit 0 read from the gate itself.
not in gate: integration -run 'Versions' in the store pkg, 9 tests ran.
CI red on 4e1b2c9: e2e, 1 spec; passes alone 3/3; same spec timed out on main run 1182 → flake,
ticketed with owner. Not rerun blind.
```

## Done means

- The gate ran whole on the pushed sha and its own exit status was read.
- Every red job was classified, and none is waved off as "expected".
- Any budget raise carries its measured sentence in the config comment.
- A new gate hard-fails, ships with the rule it enforces, and is listed in the profile.

## Traps

- **The job that was always red.** A performance job was red for weeks and learned as "expected". It
  measured one URL (a redirect into the heaviest route) against the lightest route class's budget, on a
  mobile profile that failed every route. A real layout-shift defect on another route was only found by
  hand, because nothing in CI ever measured that route. → Steps 6 and 9.
- **Lint that saw nothing.** In a repo with one module per app and no root module, running the linter
  from the root reported clean and checked zero files. → Step 10.
- **The stray file.** A merge left `*.orig` files under the source tree. Every gate matched on extension,
  so all of them passed. → Step 10.
- **The green check with a red step.** A deployment preview job was marked `continue-on-error`, so the
  check was green while the staging preview inside it had failed. → Step 11.
- **Rerunning a billing failure.** CI jobs failed in three seconds with no steps, on every PR in the
  organisation, on several days. Reruns changed nothing, and the job annotations said why: the account's
  payment had failed. → Step 5.
- **The budget that trips everyone.** A coarse size guard sat about 1.3 kB under its limit and failed a
  1.4 kB feature with no new dependency. The config comment records the same thing at three earlier
  limits. → Steps 7 and 8.
- **The unrelated-looking error.** The dependency-graph check refused an odd-numbered runtime
  version with an error that pointed elsewhere. → Step 1: the profile states the runtime.
- **The clean merge that broke a test.** A rename on main merged into a branch with no conflict marker.
  The production code compiled, and only the test file broke. `build` passed; the full gate caught it.
  A behaviour change on main is worse, because not even the gate catches it. → Step 4, including the re-read.
