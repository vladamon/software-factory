# The line

Nine stations, in the order a change meets them. They order *concerns*; a one-line fix still passes
through Prove, Gate and Land, it just passes through quickly.

```
 brief (product-dev-os)
   │
 01 Intake ─ 02 Map ─ 03 Build ─ 04 Prove ─ 05 Gate ─ 06 Review ─ 07 Land ─ 08 Release
                                                                                 │
   └──────────────────────────────── 09 Ratchet ◄──────────────────────────────┘
                      (every station's incidents feed back as rules or gates)
```

| # | Station | In | Out | Seeded by |
|---|---|---|---|---|
| 01 | **Intake** | A shaped brief | Tickets, one per layer, each with an owner; the chain explicit in the tracker | Feature owner goes end to end, layer expert reviews; cross layers only on work you specified and can verify; an answer that implies work ends as a ticket |
| 02 | **Map** | Tickets | What exists today, hop by hop; the area's design doc read or written | The map is a deliverable; contract first, design doc as its own PR; read the decision behind a precedent before copying it |
| 03 | **Build** | A ticket + map | A branch in its own worktree, touching every file its change shape lists | [Recipe](../recipes/03-build.md) |
| 04 | **Prove** | A branch | Tests shown to fail against the breaks they claim to catch | [Recipe](../recipes/04-prove.md) |
| 05 | **Gate** | A proven branch | One command green on a named sha, plus the suites it skips run by hand | [Recipe](../recipes/05-gate.md) |
| 06 | **Review** | A green branch | Approval on *this* sha; every follow-up a ticket | PR body shaped like the reviewer reads; an approval covers a sha; agent review is advisory and covers only what a linter can't |
| 07 | **Land** | An approved PR | On main, stack retargeted, tracker in the right state, all verified by reading back | [Recipe](../recipes/07-land.md) |
| 08 | **Release** | Commits on main | Running where users are, verified by digest; distance to prod known | A merge can never deploy prod; each hop waits for the previous artifact; merged is not shipped |
| 09 | **Ratchet** | An incident, anywhere | A rule, a gate, or a deletion | [Recipe](../recipes/09-ratchet.md) |

The handoff from `product-dev-os` is its `product:build` brief (`readiness: ready`) and its
`product:plan` tasks. Intake turns each task into one ticket per layer. A brief with `readiness: blocked`
doesn't enter the line.

## Measures

Nothing below is measured yet. The first audit sets a baseline for each number, and after that a
recipe change is justified by the number it moves, the same loop `harness-optimisation` uses.

| Measure | Station | Why it matters |
|---|---|---|
| Lead time: ticket opened → merged → staging → prod | whole line | Shows where the time goes; the build step is rarely where it goes |
| Review wait: ready → first review | 06 | When agents build fast, this becomes the constraint |
| PRs in flight per person | 03–07 | Too much work in flight is what makes stacks fall over |
| Red rate per gate job | 05 | A job red most of the time is ignored even when it's right |
| Defects found after merge | 04, 05 | What the proofs and gates let through |
| Commits on main not yet released | 08 | "Merged" features users can't see |
| Rules added and deleted per week | 09 | A ratchet that only adds rules is really an accumulating pile |
