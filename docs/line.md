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
| 01 | **Intake** | A shaped brief | Tickets, one per layer, each with an owner; the chain explicit in the tracker | [Recipe](../recipes/01-intake.md) |
| 02 | **Map** | Tickets | What exists today, hop by hop; the area's design doc read or written | [Recipe](../recipes/02-map.md) |
| 03 | **Build** | A ticket + map | A branch in its own worktree, touching every file its change shape lists | [Recipe](../recipes/03-build.md) |
| 04 | **Prove** | A branch | Tests shown to fail against the breaks they claim to catch | [Recipe](../recipes/04-prove.md) |
| 05 | **Gate** | A proven branch | One command green on a named sha, plus the suites it skips run by hand | [Recipe](../recipes/05-gate.md) |
| 06 | **Review** | A green branch | Approval on *this* sha; every follow-up a ticket | [Recipe](../recipes/06-review.md) |
| 07 | **Land** | An approved PR | On main, stack retargeted, tracker in the right state, all verified by reading back | [Recipe](../recipes/07-land.md) |
| 08 | **Release** | Commits on main | Running where users are, verified by digest; distance to prod known | [Recipe](../recipes/08-release.md) |
| 09 | **Ratchet** | An incident, anywhere | A rule, a gate, or a deletion | [Recipe](../recipes/09-ratchet.md) |

The handoff from `product-dev-os` is its `product:build` brief (`readiness: ready`,
`contract_version: 0`): done criteria with stable `DC` ids, screen states as `screen/state`, no-gos
verbatim. Its `product:plan` tasks come along when the author ran one; they are optional at Intake,
which splits along them when present and one ticket per layer when not. Review checks each `DC` id
back (station 06). A brief with `readiness: blocked` does not enter the line. A brief with `readiness: blocked`
doesn't enter the line.

## Measures

The first audit sets a baseline for each number, and after that a recipe change is justified by the
number it moves, the same loop `harness-optimisation` uses. `scripts/line-audit.py` measures the rows
marked *script* from the code host alone; the rest need the tracker or the deploy repo.

| Measure | Station | How | Why it matters |
|---|---|---|---|
| Lead time: opened → merged → released | whole line | script | Shows where the time goes; the build step is rarely where it goes |
| Lead time: released → each environment | 08 | deploy repo | Differs per profile: a pin bump, a moving tag, a dispatch |
| Review wait: ready → first review, and PRs merged with none | 06 | script | When agents build fast, this becomes the constraint |
| PRs in flight per person | 03–07 | script | Too much work in flight is what makes stacks fall over |
| Dirty-main episodes, and time from first red to releasable again | 07 | script (runs on main); the incident log for unshippable merges | Main must be releasable at every commit (`trunk.md`); this is how long it wasn't |
| Red rate per gate job on main | 05 | script | A job red most of the time is ignored even when it's right |
| Defects found after merge | 04, 05 | tracker; red on main is the script's proxy | What the proofs and gates let through |
| Commits on main not yet released | 08 | script | "Merged" features users can't see |
| Rules added and deleted per week | 09 | `git log` on the profile and recipes | A ratchet that only adds rules is really an accumulating pile |

```
scripts/line-audit.py owner/app owner/api owner/charts --days 30          # Markdown to stdout
scripts/line-audit.py owner/app --json > audit.json                      # for diffing two audits
```

It reads through the `gh` CLI and writes nothing but a cache of immutable reads (completed runs,
compares between published releases) under `~/.cache/line-audit`, so a weekly rerun pays only for
what is new. A cold 30-day audit of five active repos costs a few thousand REST requests, out of the
same hourly budget every other session on the account uses; the script stops while 1,000 remain.
Its numbers are the baseline's, never the profile's: they are state, and go to the audit log.
