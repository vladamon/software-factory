# <repo> — conventions for agents and humans

<!-- The factory profile. Headings are fixed: recipes refer to them by name. Keep each section to rules
     that caused a real problem once; delete a line when the code makes it unnecessary. No state (PR
     numbers, ticket status) here. That goes in memory or the tracker. -->

<Stack in one line.>

## The gate

`<one command>` runs, in order: <jobs>. Every job is a hard gate; none is "expected red".

Preconditions: <runtime version, env vars that must be off, services that must be up>.

**Not in the gate:** <suites the command skips, and when CI runs them>. Run them by hand for every
package you touch and name the run in the PR body (recipe 04, step 7).

## The shape of a change

<!-- One entry per kind of change. A diff missing one of its entry's files is incomplete, not small. -->

- **<kind>**: <file>, <file>, <test file>, <registration>, <doc line>.

## Code rules with a history

- <when X, do Y, because Z>

## Test rules with a history

- <harness trap → rule>

## Git and PRs

- Commit subject: `<format>`. Branch: `<format>`.
- Other people's ticket keys stay out of titles and branch names.
- <tool workaround, e.g. the REST call that replaces a broken CLI edit>

## Reviewers and ground

- <layer>: reviewed by <role>. <Whose ground to review, not to lead.>
- Merge policy: <who merges what, when; dated, with who agreed>.
- Voice for drafts to the team: <tone>.

## Release chain

<hop> → <hop> → <hop>. A merge can never deploy production: <how production is triggered>.

## Where things live

- <what>: `<path>`
