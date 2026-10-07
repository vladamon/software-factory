# 06 · Review

Can the reviewer check it in the order they read?

When agents write the code, review is where throughput goes. The gate already proved what a machine
can prove, so a reviewer's time should go only to what a machine can't: whether the reasoning is right,
whether the change fits how the system really runs, and what isn't in the diff. This station covers both
sides: preparing a change so a review is fast and worth having, and reviewing someone else's.

## When to use

- As author: after the gate is green on the sha you're asking about.
- As reviewer: on a teammate's PR, or on an agent's branch before it becomes a PR.
- After any finding, until every finding has an answer.

## Inputs I need before starting

- A green gate on a named sha (recipe 05) and the teeth table (recipe 04).
- The profile's **Reviewers and ground**: who reviews which layer, whose ground it is, the merge policy.
- The PR body template (`templates/pr-body.md`).

## Steps

### Before asking

1. **Run the agent review first.** It's advisory and covers only what a linter can't prove: the wrong
   layer for a component, a rule followed to the letter but not the intent, a query that is correct and
   still unbounded. It never reruns the gate. The author reads the findings and decides; the human
   reviewer never sees a finding the author could have fixed first.
2. **Write the body in the order the reviewer reads.** What changed (one paragraph per non-obvious
   decision, each naming the alternative rejected); what deliberately did not change (and which ticket
   holds it); tests have teeth; verification on a named sha; checked and clear. Prose, not a changes list.
3. **Answer the reviewer's questions before they ask.** Study how this reviewer has reviewed before, in
   their merged PRs and comments. The questions they always ask go into *checked and clear*: other
   implementations of a changed interface and their fakes, every consumer that spells the payload,
   generated artifacts, column and scan order, timeouts, migration numbers against main.
4. **Name the review range.** When the branch contains work that isn't under review (a merged-in base,
   a dependency PR), write the exact range to read: `review <sha>..HEAD`. For a stack, each PR is
   reviewed as its delta against its base's head.
5. **Ask early and small.** One ticket per PR, contract first. A draft PR with a clear question gets a
   useful answer sooner than a finished stack gets a review. Ask the layer's reviewer by name, not the
   channel.

### Receiving findings

6. **Answer every finding in its thread, with a decision.** Fix, disagree with a reason, or defer to a
   named ticket, and say which one. A thread left open is a question the reviewer will have to ask again.
7. **Every listed follow-up becomes a ticket with an owner.** Anything the reviewer said "later" about
   goes into the tracker the same day, linked from the thread.
8. **When a finding refutes the PR's reasoning, rewrite the reasoning.** Fixing the code isn't enough.
   The body and commit message state the real reason, and a test encodes that reason, so the next
   reader doesn't inherit the refuted one.
9. **Re-request on the new sha.** An approval covers the sha it was given on. After changes, say what
   moved and ask again. Don't merge on the old approval.
10. **When main moves under an open PR**, and the reviewer points it out or offers to push the fix,
    answer in the thread, decide, and say who does it.

### Reviewing someone else's

11. **Read the teeth table, then test it.** Apply one of the listed breaks yourself, or one that isn't
    listed. "I mutated X and four tests failed" is a review; "tests look good" isn't.
12. **Check the brief's done criteria by id.** When the ticket came from a ready brief (`product:build`,
    `contract_version: 0`), its acceptance line lists `DC` ids. For each id the PR claims, find the test
    or the check that proves it and name it in the thread. An id with no check is a finding; a criterion
    the body doesn't mention is a question (built, cut, or deferred to which ticket?). "Done criteria
    met" without ids is not an answer.
13. **Look for silent failure first.** Every error path: does it log or return, or does it become a
    plausible default? A `default:` branch, a "not found" on a decode error, a timeout that produces no
    wrong output and only a log line.
14. **Ask how it runs in production.** Deployment mode, replica count, statelessness, the real transport.
    An in-process test harness can't catch a bug that only exists across processes.
15. **Stay on your ground.** Review with the depth your layer knowledge supports. On another expert's
    ground, ask questions instead of prescribing.
16. **Merge only as the profile's merge policy says.** Some repos let the reviewer merge a teammate's
    PR once no blocker remains; others keep the merge with the author. Either way the policy is written
    down, and an automated merge checks review state as well as CI (see `docs/authority.md`).

### A sweep that cuts or rewrites

17. **Review the combined diff of the whole sweep, against what was removed.** When a stack of PRs
    shortens copy, deletes code paths or simplifies config, review each removed line for the one fact it
    carried that nothing else says: a caveat on a figure, a warning, an edge case. Per-PR review misses
    these because each cut looks reasonable on its own. Run it adversarially (an agent asked only "what
    did the reader lose?") before the bottom PR merges, and grep the tests for every phrase you restore
    or change.

## What good output looks like

As author, the ask:

```
Ready for review: #418 (store half of version history), review 2d88866..HEAD, the base is merged in.
Gate green on 7c01e4a; integration 'Versions' ran by hand, 9 tests. Teeth: 5 breaks, all caught.
Checked and clear: both Store implementations and the fake, the two clients that decode the payload,
no committed OpenAPI golden, migration 000032 is main's next at a71b0d4.
```

As reviewer, a finding:

```
Blocking: sessions are keyed on the per-connection object, but production runs stateless across
replicas (chart default), so every call gets a fresh one and session_id is always null. The
in-process test transport keeps one connection and can't catch this. Needs a decision before the
multi-tenant PR below it merges, because that one resolves differently depending on it.
```

## Done means

- Every finding has an answer in its thread: fixed, disagreed with a reason, or deferred to a ticket.
- Every follow-up is a ticket with an owner.
- The approval is on the head sha, and the body states the reasoning that survived review.
- Every `DC` id on the ticket has a named check in the thread, or a decision: cut, or deferred to a ticket.
- For a sweep that removes, the combined diff was read for what the reader lost.

## Traps

- **The stale approval.** A PR was merged on an approval given ten commits earlier. The ten commits went
  to main unreviewed. → Step 9; Land checks approved sha against head (recipe 07).
- **Merge on green, reused.** A one-off "merge when green" was reused by a script that checked CI only.
  It merged a PR 41 minutes after the reviewer had written "not approving yet". → Step 16.
- **The reasoning that was wrong.** A PR withheld a field from public payloads "because it carries
  content". Review showed the write path already deletes content keys. The real reason was identity:
  identity keys deliberately stay in that field so a storage default can match them. The key-level tests
  were blind to identity nested inside the map, and a new test asserts on the whole serialised body.
  → Step 8.
- **The bug the harness can't see.** Session tracking keyed on a per-connection object worked in every
  test, because the in-process transport keeps one connection. Production runs stateless across
  replicas, so every row was an orphan. Review found it; no test could have. → Step 14.
- **The misdiagnosis in public.** A team message called a teammate's approval premature. The actual
  problem was CI being down for billing. → Diagnose (recipe 05, step 5) before attributing a failure to a person.
- **The caveat that got shortened away.** Three stacked PRs cut explanatory UI text to fit a new length
  cap, each reviewed and green. One pass over their combined diff, asking only what the reader lost,
  found seven dropped caveats: among them that a delegated credential keeps acting until it's revoked,
  and that a missing figure shows a dash, not a zero. All seven went back in, within the cap, before
  anything merged. → Step 17.
