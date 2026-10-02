# Environments

How many environments, what each one is for, and how a commit travels from main to users. This is
the other half of [`trunk.md`](trunk.md): trunk says every commit on main *could* ship; this says
where it runs on the way, and what "shipped" means.

**Status: proposal (2026-10-02).** Unlike `trunk.md`, this has not been agreed by a team yet. The
*Open questions* at the end are the parts still being decided; refine it there, and move a line into
a profile only once it's agreed.

## Three events, kept apart

A change reaches users through three separate events. Most process arguments come from mixing them up.

| Event | What happens | Who triggers it |
|---|---|---|
| **Deploy to staging** | The commit runs next to everything else on main | Every merge, automatically |
| **Release** | A version of main runs in production | A person, on a schedule (recipe 08) |
| **Enable** | Users see the feature | A person flips a flag, per environment |

"Is everything merged ready for production?" has a precise answer: everything merged is *safe to
release* (trunk.md), not *released*, and not *enabled*. A merged, dark feature in production is
normal and is the point.

## Few environments, one job each

| Environment | Job | Runs | Posture |
|---|---|---|---|
| **Local** | Develop | The branch, against mocks or a local stack | Whatever the developer needs |
| **Staging** | Integrate: does main work as a whole, on real infrastructure? | Main, continuously (a moving `main` tag) | Never changes |
| **Production** | Serve users | Releases only, pinned | Never changes |

- **One job per environment, one posture per environment.** An environment that flips between a
  moving tag, pinned versions and production pins for a rehearsal is three environments sharing a name.
  Nothing written about it stays true, and anyone who trusts the rule file ships by bumping a pin the
  environment ignores (recipe 08, *The posture that kept changing*).
- **Each extra environment costs config that drifts.** Every environment is another stack of values,
  secrets, external accounts (auth, payments, mail) and migrations. Values copied between environments
  drift silently. Add an environment only for a job none of the existing ones can do.
- **Short-lived beats permanent.** If one feature needs a shared place to be tried before merge, give
  it a preview that lives as long as the PR, not a standing `dev` environment.

## When a dev environment earns its place

When staging has to stay stable for someone **outside the team**: customer trials, partner
integrations, sales demos, campaign testing against a real sign-up flow. Then:

- **dev** takes the integration job (main, continuously),
- **staging** becomes pre-production (release candidates, pinned, a dress rehearsal of the real release).

Decide this on purpose and record it in the profile with its date. Adding a dev environment because
"staging is broken a lot" treats the symptom: a broken staging is a dirty main (trunk.md), and the fix
is there.

## Build once, promote the digest

- **Production runs the artifact staging already ran**, identified by digest, not a rebuild of the same
  commit. A rebuild of the same commit can carry a different digest (recipe 08, *Same commit,
  different digest*), and then staging tested something production doesn't run.
- **A release rehearsal promotes, it doesn't repoint.** Don't move staging onto production's pins to
  rehearse; promote the candidate's digest along the chain. When a migration is risky enough to need a
  real rehearsal against production-shaped data, that is a short-lived environment for that migration,
  not a new posture for staging.

## Release on a schedule

- **A release train, from main.** On a fixed cadence (weekly, or twice weekly), cut every component
  that moved, together, as one release. One chart bump, one production change. Version files stop
  racing between people, because one person holds the release (recipe 08, step 2).
- **Rotate who drives it.** At least three people have released production from the runbook in the
  last month. A release that waits for the one person who knows the infra waits whenever that person
  is away.
- **Off-cycle releases stay possible** (main is always releasable); they're the exception, for a fix.
- **Production stays human-authored** (`authority.md`). The schedule removes coordination, not the gate.

## Relation to trunk-based development

This is scaled trunk-based development with continuous *delivery*: short PR branches into one main,
every commit releasable, unfinished work behind flags, one artifact promoted from staging to
production. It is not continuous *deployment*: a person still releases production. Moving to
continuous deployment would be a written policy that moves that line out of *on the word*, never a habit.

It asks for habits, not tools:

- **Branches live hours to a day or two.** A parked branch, a backup push with no PR, local commits
  waiting a week: each is a long-lived branch. Unfinished work merges dark instead.
- **Stacks stay shallow and land fast.** A deep stack waiting on review is a long-lived branch in
  pieces; that's where orphaned children come from (recipe 07).
- **Review answers within hours.** Short branches only work when review is fast. Where review capacity
  is the constraint, write down which changes may land without waiting (`authority.md`, *Moving a line
  between tiers*) rather than letting branches age.

## Measured

- **Posture changes per environment.** Target: zero. Each one is a decision, recorded in the profile.
- **Staging lag behind main**: minutes from merge to running on staging, by digest.
- **Digest match**: production's digest equals the one staging ran, per release.
- **Release drivers**: distinct people who released production in the last 30 days.
- **Branch age at merge**, and branches older than a week with no PR (`docs/line.md`, *Measures*).

## Why this is a rule

- In three weeks one staging environment moved from a moving tag to pins, back to the moving tag, then
  to production pins for a rehearsal. Rule files and agent memory described an earlier posture each time.
- Control-plane values were copied between environments and drifted, and the difference surfaced only
  when a feature behaved differently in one of them.
- The release workflow rebuilt a tagged commit, and production ran a digest staging had never run.
- Production releases depended on one infrastructure person, who was away for two weeks while
  finished work waited.
- Features merged and verified on staging stayed invisible to users for weeks, because nothing put
  releases on a cadence (recipe 08, *Merged for weeks, shipped to nobody*).

## Open questions

Refine these, then fold the answers into the sections above:

1. **Is staging used by anyone outside the team?** If yes, the dev environment above is warranted;
   if no, staging stays the integration environment.
2. **Per-PR previews:** worth their cost for UI-only changes, given local mocks already exist?
3. **Train cadence:** weekly or twice weekly; which day; who drives the first rotation.
4. **Promote by digest:** the release workflow needs to retag the built image instead of rebuilding it.
5. **Review-time policy:** which changes may land without waiting for a layer expert's review.
6. **Production data and migrations:** at what point does a risky migration need its own rehearsal
   environment, and who decides.
