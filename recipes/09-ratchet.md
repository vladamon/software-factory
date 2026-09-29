# 09 — Ratchet

What did this teach, and where does that go?

Every other station produces incidents: a wasted hour, a false green, a review finding, a silent failure.
This station makes sure each one happens only once. A lesson that stays in a chat transcript or
someone's memory will be relearned by the next agent, at the same cost.

## When to use

- After anything took more than twenty minutes to understand.
- After a review finding that a rule could have prevented.
- When a convention has just been decided (a naming rule, a format, a threshold).
- On a cadence (weekly is enough): prune.

## Inputs I need before starting

- The incident in one line: *what happened → what it cost*.
- The profile, and this repo's recipes. The rule may already exist and have been missed, which is a
  different fix (see *Traps*).

## Steps

1. **Decide the lowest form that makes it impossible to repeat.**

   | If the lesson… | It becomes… | Where |
   |---|---|---|
   | has a machine-checkable signature | a gate: lint rule, contract test, budget, script | the repo, in the same PR as the fix |
   | holds for any repo | a trap line in the station's recipe, or a step once it has run twice | here |
   | names this repo's commands, paths, tools or domain | a line under the right profile heading | the repo's `CLAUDE.md` |
   | is about the agent harness (context, memory, hooks) | an audit, then a recipe line | `harness-optimisation` |
   | is today's state (who, which PR, what's blocked) | a memory entry | the agent's memory, not a rule file |

   Prefer the highest row that fits. Prose is the fallback, for lessons a machine can't check.
2. **Write it as *when X, do Y, because Z*.** The *because* names the incident. A rule without a *because*
   will be deleted by the next person who doesn't understand it.
3. **Land a convention with its codification.** When the lesson is a decided convention, one PR holds all
   of it: the code that follows it, the one-sentence rule in the short-form file, the longer reasoning,
   and the lint when there's a signature. A convention that exists only in a decision log gets broken
   by the next PR.
4. **Shrink the prose once a gate enforces it.** Replace the paragraph with one line naming the gate.
5. **Prune.** On the cadence, read each rule file top to bottom and delete:
   - rules the code made unnecessary (the workaround is gone, a gate now enforces it);
   - rules that misfire, especially any rule that teaches tolerating a failure;
   - state that crept into a rule file;
   - duplicates (the same rule in two files: keep the most general home, link from the other).

## What good output looks like

```
incident: e2e passed on a branch that broke the page; the harness served the previous build.
form:     profile line (the build command is repo-specific) + trap in recipe 04 (the lesson isn't).
profile:  "Playwright serves the last production build. Rebuild before trusting an e2e result."
recipe:   04-prove → Traps → "The stale artifact."
```

## Done means

- The rule exists in exactly one home, at the highest form that fits.
- It carries its *because*.
- If a gate now enforces it, the prose is one line long.
- Weekly: the count of rules added and deleted is recorded (`docs/line.md`, *Measures*). A ratchet that
  only adds rules is accumulating, not ratcheting.

## Traps

- **The rule that normalised a failure.** "This CI job is the expected red one" was a rule for weeks.
  It taught everyone to ignore red. The job was pointed at a single URL of the wrong route class, and a
  real layout-shift defect sat behind it unseen. → A rule that tolerates a failure is a misfire; replace
  it with "fix or re-scope the job".
- **The rule that existed and was missed.** The rule was in the file, but the file had grown past what
  gets read. → The fix isn't a second copy. Shorten the file, or turn the rule into a gate.
- **The index that became a tracker.** A memory index grew one-line hooks into paragraphs of PR numbers
  and dates, until reading the index cost more than reading the files. → Index lines are hooks; state
  goes in the file behind the hook.
- **The convention in the decision log.** A design critique found four formats for one timestamp, all
  introduced by people who didn't know the convention existed. It lived in a 50 KB decision log.
  → Step 3.
- **Learning a codebase's rules from scratch.** The fastest source of a codebase's unwritten rules turned out
  to be its reviewer's merged PRs and review comments: each comment is a trap that already happened.
  → When joining a repo, harvest the reviewer's history into the profile before the first PR.
