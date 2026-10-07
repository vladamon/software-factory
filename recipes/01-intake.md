# 01 · Intake

Whose is this, and is it one ticket?

Agents make building cheap, so the expensive mistakes move upstream: work that nobody owns, a half of
a feature that nobody will build, a ticket that is really three, a question disguised as a task. This
station turns incoming work into tickets that each have one owner, one layer, one acceptance line, and
an explicit place in the chain.

## When to use

Whenever work arrives:

- a ready brief from upstream (`product-dev-os`'s `product:build` with `readiness: ready`; its
  `product:plan` tasks when the author ran one);
- a meeting, a thread, or a customer report;
- a review follow-up (recipe 06);
- an answer you gave that implies work.

## Inputs I need before starting

- The request in its original words, with its source linked.
- The profile's **Reviewers and ground**: who owns which layer, whose core ground is whose.
- The tracker's view of the area: open tickets, their owners, and what blocks what.

## Steps

### Decide whether it is a ticket

1. **Send undecided questions back.** If the request still hides a product decision (which of two
   behaviours, whether to build it at all), it isn't ready for a ticket. Upstream, that's `product:shape`
   or a conversation with the decision owner. A ticket built on an open question gets built twice.
2. **Take upstream acceptance verbatim, ids included.** A ready brief already carries appetite, done
   criteria and no-gos. Copy them into the tickets rather than paraphrasing them, and keep the brief's
   ids (`DC1…`, `screen/state`) on each ticket's acceptance line, so Review can check every one by
   name (recipe 06, step 12). A brief that comes with a `product:plan` is split along its tasks; one
   without is split here, one ticket per layer.

### Split

3. **One ticket per layer, all filed at once.** A vertical feature becomes a backend ticket, a UI
   ticket, and so on, filed together and linked with *blocked by*, so the chain is visible in the
   tracker. Filing only the half you will build leaves the other half to memory.
4. **Write the contract where the halves meet.** Field names, types, and what absent means (an
   explicit null and a reason, never a zero that looks like data). Get it agreed with the other half's
   owner before either side builds.
5. **Set the landing order.** A UI control never lands before the endpoint it calls is *released*,
   unless it's behind a flag that stays off in production until then. Merged in the other repo isn't
   enough: production runs that repo's last release ([`docs/trunk.md`](../docs/trunk.md)). State the
   order in both tickets.
6. **Size each ticket to one PR.** About 5 to 20 files, or two working sessions. Anything bigger is
   several tickets that stack (store → CRUD → wire-up).

### Own

7. **Every ticket gets a named owner.** "Unassigned" means nobody will build it. An ask filed into
   another team's backlog without an owner is a wish.
8. **Ownership follows the feature, not the layer.** The feature owner delivers every half, end to end,
   and each layer's expert reviews their half. When your half is blocked by an unowned half in another
   layer, take it yourself if you specified it and can verify it from your own layer. Stay out of the
   expert's core ground (the profile names it): there, file and ask, and review rather than lead.
9. **Ask before taking an assigned ticket.** If someone else's name is on it, even when nothing has
   started, ask first and move the assignment in the tracker once they agree. Built-but-unclaimed work
   leaves two people each thinking they own it.
10. **Say the norm up front.** "The feature owner goes full stack" is stated once, as how the team
    works, never as a reaction to one person's queue.
11. **Welcome teammates in your repo.** When someone else ships in the repo you own, review with the
    gates and don't take the ticket back. Owning the standards doesn't mean being the only implementer.

### Record

12. **An answer that implies work ends as a ticket.** When you answer a teammate's technical question,
    give the mechanism and the evidence in the thread, then file the ticket the answer implies, with an
    owner, and link it there.
13. **Name things so automations behave.** Your own ticket key goes in your branch and commit subjects.
    Other people's keys go only in prose, because tracker automations act on any mention (recipe 07).
    Verify every tracker write by reading it back.

## What good output looks like

```
source:  brief docs/specs/2026-09-24-versions-build.md (readiness: ready), appetite 3 sessions
split:   T-41 api: GET versions per agent (owner: me; not the backend lead's core ground; they review)
         T-42 ui: Versions figure (owner: me), blocked by T-41, lands behind the flag until it ships
         T-43 ui: version chip on rows (owner: me), blocked by T-42
contract: {version: string|null, reason: "not_reported"|null}. Agreed in T-41's thread.
out:     comparing versions across agents → T-44, parked
```

## Done means

- Every piece of the request is a ticket with an owner, or was sent back as a decision.
- Every cross-layer chain is linked with *blocked by*, and the landing order is stated.
- The contract between the halves is written down and agreed by both owners.
- No ticket is bigger than one PR.

## Traps

- **The control with no backend.** A UI control was built mock-first against a contract written by
  the UI owner, and the backend ticket was never picked up. It shipped, returned 422 on staging, and was
  removed. Both tickets were cancelled. → Steps 5 and 7: an assigned backend ticket, and a landing order.
- **Asks that sat.** Backend asks filed from the UI side sat unassigned while the UI queue waited on them.
  Backend throughput, not UI, was the team's constraint. → Step 8: the feature owner takes the half.
- **The ticket built under someone else's name.** A ticket assigned to a teammate who hadn't started
  was built by someone else. The tracker kept the teammate's name, and the message asking to take it
  was drafted but never sent. → Step 9.
