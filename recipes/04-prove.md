# 04 · Prove

Would the tests fail if the code were wrong?

A test that passes is only evidence when you've also seen it fail. Agents write tests that pass easily,
including tests that would still pass against the bug they were written for. This station makes each
new test show that it catches something.

## When to use

On every branch that adds or changes a test, before the gate and before asking for review. For a change
with no test, write down why in the PR body; "covered by existing tests" has to name those tests.

## Inputs I need before starting

- The branch, rebased on current main.
- The profile's **The gate** section: the command, and the suites it does *not* run.
- For every new test, the one-sentence claim: *"this fails if …"*.

## Steps

1. **Write the claim before the test.** One sentence per test: the break it catches. A test with no
   statable break is decoration; delete it or find the break.
2. **Apply the break and watch the test fail.** Revert the fix, flip the comparison, drop the guard,
   return the old value. Only this test (or a named few) should fail, and for the right reason. Restore.
   If nothing fails, the test has no teeth: fix the test, not the claim.
3. **Check that the fixture separates the bug from the fix.** A case that the fix and the bug both
   exclude, each for its own reason, asserts the same number either way. Give each case one reason to
   be in or out.
4. **Iterate the source of truth.** When the code has a registry, catalog or enum, the test walks it.
   A hand-written list lets the next entry skip the test.
5. **Take goldens from main's output.** Generate expected values by running main's code over the
   fixture. Never type them by hand, because a hand-typed golden asserts what you believe, not what the
   code does.
6. **Seed through the upstream path.** When a value is derived in two places (a write-path computation
   and a storage default, say), seed the raw input and let both derive it. The test then proves they
   agree, not only that the value round-trips.
7. **Run what the gate skips.** Every suite the profile lists as not in the gate (integration, tagged,
   slow, e2e against real services) that touches the changed packages is run by hand, and **the count
   of tests that ran is read**, not just the exit status.
8. **Carry numbers for performance claims.** A query or hot-path change states rows read, bytes read and
   memory, before and after, over a named fixture, plus the plan output unchanged or explained.
9. **Write the table** into the PR body.

## What good output looks like

```markdown
### Tests have teeth

| Break applied | Caught by |
|---|---|
| Drop the tenant filter from the list query | `lists only the caller's rows`, `share view withholds identity` |
| Return `found=false` on decode error | `decode error surfaces as 500` |
| Revert the NaN guard | `ratio with zero denominator is null` |

Ran by hand (not in the gate): `integration -run 'Spans|Share'` in the storage package, 14 tests,
all ran, all passed, on <sha>.
```

## Done means

- Every new test has a row in the table, and every row was actually applied and seen to fail.
- Every suite the gate skips that touches the change was run, with a non-zero count, and is named.
- No golden was typed by hand.

## Traps

- **"ok" with zero tests run.** Tagged integration tests that need a container runtime reported success
  with zero tests when the runtime was down, and the runtime's health command exited 0 anyway.
  → Read the count of tests run, and look for skip lines in the unfiltered output.
- **The wrapper's exit status.** A backgrounded gate reported success from its wrapper while the gate
  inside exited 2. → Read the gate's own exit status and its last lines.
- **The stale artifact.** The e2e harness serves the last production build, so a run on fresh code tested
  yesterday's build. → Rebuild before trusting an e2e result; the profile says how.
- **The same assertion both ways.** A fixture row excluded for two independent reasons asserted the
  same number with and without the fix. → Step 3.
- **The gate that does not run it.** The pre-push gate type-checks the integration tests but doesn't
  run them, and CI runs them only when certain paths change. A green PR hid a storage test that never ran.
  → Step 7.
- **The exemption that swallowed the rule.** A copy lint allowed one legitimate use of a glyph (alone
  in a table cell, as the no-value mark) and defined "alone" as "nothing but whitespace around it". A
  separator literal joining two interpolations (`${a} — ${b}`) is also nothing but whitespace around
  the glyph, so four real violations passed as exempt, and a reviewer found them by reading the code, not
  by the gate. → A gate with an exemption gets step 2 twice: once against the break, and once against
  the nearest case the exemption must *not* cover.
