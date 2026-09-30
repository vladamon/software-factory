# Conventions

The contract for recipes, profiles and templates. If a recipe contradicts this file, the recipe is wrong.

## 1. Generic here, local there

A line belongs in this repo when it holds for any repo with a gate, a reviewer and a release chain. It
belongs in the repo's profile when it names a command, a path, a tool quirk, a person or a domain rule.

| Belongs here | Belongs in the profile |
|---|---|
| Show each new test failing against the break it claims to catch. | The gate command, and which test suites it skips. |
| Shared sequence numbers race; re-check at open and at merge. | Where the migration directories are, and how to list them on main. |
| Verify after every write to the tracker. | Which tracker call returns success without doing anything. |
| A merge can never deploy production. | The release chain, hop by hop. |

When one lesson has both halves, split it: the principle comes here, and the instance stays in the profile
with a link to the recipe.

## 2. The profile

A repo joins the line by giving its `CLAUDE.md` these headings, in this order (`templates/profile.md`):

1. **What this is**: stack in one line.
2. **The gate**: the one command, its jobs, its preconditions, and what it does *not* run.
3. **The shape of a change**: for each kind of change, the files it touches.
4. **Code rules with a history**: domain rules, each one caused a problem once.
5. **Test rules with a history**: harness traps.
6. **Git and PRs**: commit subject, branch name, tool workarounds.
7. **Reviewers and ground**: who reviews which layer, whose ground is whose, the merge policy.
8. **Release chain**: hop by hop, and what can never be done from a merge.
9. **Where things live**.

Recipes refer to these headings by name ("run the gate from the profile"). A profile missing a heading
is a repo the factory can't run on yet. That's fine, as long as it's stated.

## 3. Recipe shape

```markdown
# NN · Station

The question this station answers, in one line.

## When to use
## Inputs I need before starting
## Steps
## What good output looks like
## Done means
## Traps
```

Each trap is written in the form *what happened → the rule*. It has to name a real incident, not a
hypothetical one.

## 4. How a rule gets in

- **It happened once.** A rule earns a line by causing a real problem once. General advice that never
  caused a problem stays out, however sensible it sounds.
- **It happened twice before it becomes a recipe step.** One incident gets a trap line; a practice
  that has run on two real changes gets steps.
- **If it has a signature, it becomes a lint.** A rule a machine can check (a pattern in the AST, a
  file that must exist, a number that must not rise) moves into the gate, and its prose shrinks to one line
  saying where the gate enforces it.

## 5. How a rule gets out

- **Deleted when the code makes it unnecessary**, e.g. the workaround is gone or a gate now enforces it.
- **Deleted when it misfires.** A rule that teaches you to tolerate a failure ("this job is expected to
  be red") is a misfire, however long it has been true.
- **Never kept for history.** Git keeps the history; the file keeps only what's true now.

## 6. Rules and state never share a file

Rules (*when X, do Y, because Z*) live in recipes and profiles and change rarely. State (open PRs, who is
waiting on whom, what merged yesterday) lives in the agent's memory or the tracker and changes daily.
A rule file that starts collecting PR numbers goes stale in a week, and an agent reading stale state
acts on it.

Memory has the same rule on a smaller scale. An index line is a hook that decides whether to open the
file. It isn't a status report.

## 7. Evidence

A change the line produces carries its own evidence in the PR body: the break/caught-by table (recipe 04),
the gate run on a named sha, and the suites run by hand. A claim about the line itself ("reviews are the
bottleneck") carries a measurement (`docs/line.md`, *Measures*).
