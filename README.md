# Software factory

How a shaped piece of work becomes a verified, released change when agents do most of the typing.
It is written from one engineer's practice across a UI, a Go backend, databases and a Helm/Pulumi
release chain on a small team, and kept product-agnostic so it runs on any repo that fills in a profile.

Every rule here caused a real problem once before it was written down. Anything that sounds like general
advice but never caused a problem doesn't belong here.

## Where it sits

| Repo | Question | Relation |
|---|---|---|
| [`product-dev-os`](https://github.com/vladamon/product-dev-os) | *What* to build, and whether to | Upstream. Its `product:build` brief is the factory's intake. |
| **`software-factory`** | *How* a shaped change is built, proven, landed and released | This repo. |
| `harness-optimisation` (private) | How well the agent harness runs (context, tokens, subagents) | Tunes the machine; the factory tunes the line. |
| `machine-setup` (private) | Can any machine become the working one in one command? | Installs both plugins and the rule files, clones every repo. |
| `personal-field-manual` (private) | What am I getting good at, and where is the proof? | Sets direction; takes the others' output as dated evidence. |
| `brain` (private) | What do I understand, and where did I learn it? | Durable knowledge as Markdown notes; agents read it before researching. |
| A product repo's `CLAUDE.md` | How *this* repo does it | The **profile**: the factory applied to one repo. |

How the six fit together, what passes between them and the rules they share: [`docs/system.md`](docs/system.md).

## The idea in four rules

1. **Procedure is generic; the profile is local.** Recipes here never name a repo, a command or a
   person. Each repo's `CLAUDE.md` carries the same headings (`templates/profile.md`), and the recipes
   read the gate command, the change shapes and the release chain from there.
2. **The ratchet only turns one way.** A problem becomes a rule. A rule that has a signature becomes a
   gate. A rule the code made unnecessary gets deleted. Quality rises while agents do the typing,
   because nothing depends on anyone remembering.
3. **Agents act; humans authorise what leaves the room.** Three tiers, written down:
   [`docs/authority.md`](docs/authority.md).
4. **Main is releasable at every commit.** A merge is either complete (its dependencies are already
   released) or dark (behind a flag that is off in production). A dirty main is an incident the merger
   owns until it's restored: [`docs/trunk.md`](docs/trunk.md).

## The line

Nine stations. Each asks one question; each has one recipe. See [`docs/line.md`](docs/line.md).

| # | Station | Question | Recipe |
|---|---|---|---|
| 01 | Intake | Whose is this, and is it one ticket? | [`01-intake`](recipes/01-intake.md) |
| 02 | Map | What actually exists, hop by hop? | [`02-map`](recipes/02-map.md) |
| 03 | Build | Which files does this kind of change touch? | [`03-build`](recipes/03-build.md) |
| 04 | Prove | Would the tests fail if the code were wrong? | [`04-prove`](recipes/04-prove.md) |
| 05 | Gate | Does one command say yes, with no job allowed to stay red? | [`05-gate`](recipes/05-gate.md) |
| 06 | Review | Can the reviewer check it in the order they read? | [`06-review`](recipes/06-review.md) |
| 07 | Land | Is it on main, and is everything around it still true? | [`07-land`](recipes/07-land.md) |
| 08 | Release | Is it running where users are, and how far behind is prod? | [`08-release`](recipes/08-release.md) |
| 09 | Ratchet | What did this teach, and where does that go? | [`09-ratchet`](recipes/09-ratchet.md) |

A recipe is written once its practice has run on at least two real changes. Every station now has
one, and `scripts/line-audit.py` measures the line (`docs/line.md`, *Measures*). Skills follow the
numbers: the first is `factory:release`.

## Layout

| Path | What it holds |
|---|---|
| `docs/system.md` | The six repos as one system: departments, what passes between them, the shared rules. |
| `docs/conventions.md` | The contract: recipe shape, profile headings, generic vs local, how rules get in and out. |
| `docs/line.md` | The stations, what enters and leaves each, and what the line measures. |
| `docs/trunk.md` | Main is releasable: when a merge is allowed, flags, and a dirty main as an incident. |
| `docs/environments.md` | Proposal: which environments, one job each, deploy vs release vs enable, release on a schedule. |
| `docs/authority.md` | What an agent does alone, on the word, and never. |
| `recipes/` | One file per station. The authoritative procedure. |
| `templates/` | `profile.md` (a repo's `CLAUDE.md` skeleton), `pr-body.md`. |
| `skills/` | One directory per `factory:*` skill; each is a thin runner over its recipe. |
| `.claude-plugin/` | Plugin and marketplace manifests. |
| `scripts/` | `line-audit.py`: lead time, review wait, in-flight, red rate and release distance from the code host. |

Skills (`factory:*`) come after the recipes they run, as in `product-dev-os`: improve the recipe and
the skill improves with it. The repo is a Claude Code plugin (`factory`, marketplace
`software-factory-local`); add it as a directory marketplace and enable `factory@software-factory-local`.

| Skill | Runs | Chosen because |
|---|---|---|
| [`factory:release`](skills/release/SKILL.md) | [`08-release`](recipes/08-release.md): `status`, `cut`, `walk`, `verify` | The first line audit put the longest wait between merge and release |

## Status

Started 2026-09-29 from a harvest of 96 rules across one product's repos. 75 of them turned out to be
generic procedure and 15 stayed as repo profile. The rest went to the harness or the design system.
All nine recipes written 2026-09-29. The line was first measured on 2026-09-30, across five repos.

## License

MIT
