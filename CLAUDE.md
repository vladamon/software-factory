# Software factory

How a shaped change becomes a verified, released change with agents on the line. The contract for every
file here is `docs/conventions.md`; read it before adding or changing a recipe.

## Rules for editing this repo

- **Public and generic.** No company, product, person, ticket key, hostname or internal repo name.
  A lesson with a local half is split: the principle here, the instance in that repo's profile.
- **Earned lines only.** A trap names a real incident (*what happened → the rule*). A recipe step
  exists because the practice has run on at least two real changes.
- **One home per rule.** Before adding, grep the recipes and `docs/`. Link rather than repeat.
- **Recipes before skills.** A `factory:*` skill is a thin runner over its recipe and is written only
  after the recipe exists.
- Recipe shape, profile headings, and how rules get in and out: `docs/conventions.md` §2–§5.
- Authority tiers: `docs/authority.md`. Nothing moves out of *never*.

## Layout

- `docs/`: conventions, the line and its measures, authority.
- `recipes/NN-station.md`: one per station; a missing number means not yet extracted.
- `templates/`: the profile skeleton and the PR body.

Commit subjects: `type(scope): plain-English sentence`.
