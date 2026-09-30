# 03 · Build

Which files does this kind of change touch?

An agent can write any single file well. What it misses is the file it didn't know was part of the
change: the fake that has to grow a method, the registration, the doc line, the allowlist test. This
station makes that list explicit before the code starts, and keeps parallel work out of each other's way.

## When to use

Every ticket that changes code, from the moment it leaves Map until the branch goes to Prove.

## Inputs I need before starting

- One ticket with an owner, and the map (the area's design doc read, or written first as its own PR).
- The profile's **The shape of a change** and **Code rules with a history** sections.
- Who else is working in this repo right now: other people, other agent sessions.

## Steps

### Set up the workspace

1. **One worktree per ticket.** Create it from `origin/main` (or from the base branch for a stacked
   child) in a sibling directory. Never switch branches in the main checkout, because someone else's
   work, dev server or test run lives there. Read other refs with `git show <ref>:<path>` and
   `git grep <pattern> <ref>`.
2. **Claim a column when agents run in parallel.** Split the work into disjoint columns (by project, by
   PR stack) and write the split down. All sessions append to one shared log. Before touching a PR, a
   branch or a thread in another session's column, read the log's tail and check the branch head on the
   remote.

### Before writing code

3. **List the files first.** Find the change's kind in the profile's *shape of a change* and write the
   file list into the session before editing. A diff missing one of those files is incomplete, however
   small it looks. When the kind isn't in the profile, get the list from the last merged PR of that kind
   and add the entry to the profile (recipe 09).
4. **Grep for the existing definition.** Before writing a helper, a predicate or a computed column,
   search for the one that already exists. Two live definitions of one concept will disagree eventually.
   A numerator and its denominator use the same definition.
5. **Read the decision behind the precedent.** Before copying a sibling's type, index or pattern, read
   why it was chosen (its commit body, the header comment). The precedent may have been a choice for a
   case that isn't yours.
6. **Check shared sequence numbers against main.** Migrations, schema versions and anything else
   numbered by hand: `git fetch`, list main's latest, and pick the next one. Land rechecks this (recipe 07).
7. **Contract first.** Types, interface, schema or API shape before the implementation. A new design doc
   goes out as its own PR, and the feature commits cite it by section.

### While writing code

8. **Every fallback logs or errors.** A decode error mapped to "not found", a `default:` branch that
   quietly treats an unknown value as a known one, a background pass that times out without saying so:
   each must log at least once or return an error.
9. **Enforce with structure, not comments.** A helper that can produce a wrong result when called alone
   is unexported or inlined. A doc comment asking callers to remember is not enforcement.
10. **Tests go in the same PR.** Never a follow-up. They go to Prove next (recipe 04).
11. **A rename is finished when the prose is.** Grep doc comments, API doc annotations and user-facing
    docs for the old name. When changing user-facing text, grep the tests that assert on it first.
12. **The doc moves with the contract.** A change to a documented contract updates the doc in the same PR.
13. **Format with the repo's formatter.** The profile names it, or says there is none. An agent's
    default formatter rewrites files in a style the repo doesn't use.

### Before handing to Prove

14. **Size check.** One PR per ticket, roughly 5 to 20 files. Bigger means two tickets. Split a
    vertical slice into a stack (store → CRUD → wire-up), each PR one ticket.
15. **Check the artifact's build context.** When the change imports across a boundary the shipped
    artifact's build excludes (container ignore files, package `files` lists), the gate's build in a
    full checkout passes and only the artifact build fails.

## What good output looks like

At the start of the session:

```
ticket: add per-agent version history (store half)
worktree: ../repo-ticket-997 from origin/main a71b0d4
shape "Postgres table": up.sql, down.sql, store pkg + integration test, pinned latest-version test
migration: main's latest = 000031 → using 000032 (checked a71b0d4)
existing: versionCompare() already in pkg/semver, reusing
column: none claimed by the other session (log tail 16:02)
```

At handoff: a branch whose diff covers every file on that list, plus tests, in one worktree.

## Done means

- Every file in the change shape is in the diff, or its absence is explained in the PR body.
- No new definition duplicates an existing one.
- No silent fallback: every error path logs or returns.
- Sequence numbers checked against main on a named sha.
- The PR is one ticket, and prose and docs match the new names.

## Traps

- **The shared checkout.** A session detached the main checkout "just to read main" while another session
  was working on a branch there, moving files under its dev server and tests. → Step 1: read with `git show`, edit in a worktree.
- **Two sessions, one task.** Two parallel sessions both drafted the same message to a teammate and
  prepared the same rebase, because each read the shared memory but not the other's context. → Step 2.
- **Three definitions of one concept.** By the time it caused a bug, a codebase had three live
  definitions of the same span predicate.
  → Step 4.
- **The number that raced.** A base PR's migrations were renumbered to clear a collision with main, and
  the stacked child cut before the renumbering went dirty. A child that is clean against its base can
  still collide with main. → Step 6, and again at Land.
- **The docstring that lied.** A tool's description told agents to read a field from a column that
  didn't exist, and the next PR had to fix it. → Step 11: grep prose, not only code.
- **Gate green, image red.** A source import from a directory the container build excludes passed
  every gate job and failed only the image workflow, on both architectures. → Step 15.
- **The helpful formatter.** Running the default formatter in a repo with its own hand-kept style
  rewrote unrelated lines in every touched file. → Step 13.
