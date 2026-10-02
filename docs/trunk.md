# Main is releasable

Every commit on main can go to production today. That is the invariant the whole line protects, in
the spirit of trunk-based development: short branches into one main, unfinished work behind flags,
and a main that is never "mostly fine". A main that isn't releasable is an **incident**, not a normal
state: it is noticed at once, owned by one person, and restored before anything else is merged.

## Releasable, precisely

Main is releasable when both hold:

1. **Every gate job is green on its head**, including the suites that run only after merge (the profile
   names them under *The gate*).
2. **Everything on it could ship to production now**, against what production actually runs of every
   other component: their latest *releases*, not their main.

The second clause is the one that bites in a multi-repo product. A UI change that calls a new endpoint
is releasable once the endpoint is *released*, not when it is merged in the other repo.

## A merge is allowed in exactly two cases

- **Complete.** Everything the change depends on is already released, or ships in the same release of
  the same component. Nothing on main breaks because of it, and it does what it says in production.
- **Dark.** Its user-visible effect sits behind a flag that is off in production, and the flag-off
  path is the one the gate tests.

Anything else waits on its branch. "The other half lands tomorrow" is a dirty main from now until then.

## What a flag can't hide

A flag hides behaviour. It can't hide a change to the data or the contract, because those apply
whatever the flag says:

- **Schema migrations, API contract changes and removals are backward compatible.** Expand (add the
  new thing beside the old), migrate (move readers and writers over, one release at a time), contract
  (remove the old thing once nothing released uses it). Each step is releasable on its own.
- **Every flag has an owner and a removal ticket**, filed when the flag is added. A flag nobody removes
  turns into permanent configuration that nobody understands.
- **The flag-off path is tested, not just the new path.** It is what production runs.

## The merger owns it until main is releasable

Whoever merges is responsible for main until it is releasable again, and for pushing every piece the
change depends on through to main and to a release. Concretely:

1. **Before merging:** the two cases above, checked against production's versions; recipe 07, steps 2 and 4
   (releasable, then merge the checked sha).
2. **After merging:** watch main's post-merge run to green, every job by name. The merge isn't
   finished until that run is green. Don't merge what you can't stay to watch.
3. **If main goes dirty:** it's an incident, and the merger acts on it now.

## A dirty main is an incident

**Dirty** means any gate job red on main's head, or anything on main that couldn't ship to production
today.

1. **Say so.** One line where the team sees it: what broke, which merge, who owns it. Others hold
   their merges until it's restored, because a merge onto a dirty main hides the cause and adds to it.
2. **Revert first; fix forward only when it is faster.** If a fix isn't on main within the profile's
   time box, revert the merge. A revert is the fastest known-good state; the fix lands again later,
   through the line, as a new change.
3. **Who may revert.** The merger, without waiting for anyone's word. Anyone on the team, when the
   merger can't be reached within the time box. This is a written policy (`authority.md`, *Moving a line
   between tiers*); the profile records it with its date and who agreed.
4. **Close it through the ratchet.** Each episode gets a line in the incident log: what broke, how long
   main was dirty, revert or fix. Then recipe 09: the lesson becomes a gate or a rule, so the same kind
   of merge can't dirty main twice.

## Short branches, no long-lived feature branches

A feature branch that collects merged PRs for weeks is a second main nobody releases. Unfinished work
goes to main dark instead. Stacks are fine, provided each PR in the stack is releasable on its own when
it lands (recipe 07, *A stack*).

## Release follows

A main that is always releasable can be released often, and should be. Distance to production (recipe
08, step 1) shrinks on its own. When releases are held back "until main is clean again", the hold is
the symptom, and the dirty main is the cause to fix.
Where main runs on its way to production, and what "released" means as opposed to "enabled":
[`environments.md`](environments.md).

## Measured

- **Dirty-main episodes and time to restore**, per repo: from the first red (or the first unshippable
  merge) to releasable again. `docs/line.md`, *Measures*.
- **Red rate per gate job on main.** A job red most of the time trains everyone to merge onto red.

## Why this is a rule

Each clause has already happened:

- A performance job sat red on main for 110 of 129 runs. Everyone merged onto red, and real layout
  shifts hid behind it.
- A backend's integration suite runs only after merge, and went red on main 18 times in 30 days. Each
  one was a defect the pre-merge gate couldn't see.
- 15 backend PRs in 30 days merged into stack bases and a long-lived feature branch instead of main,
  where no release would carry them.
- A UI message that depended on a new backend field was merged while that backend change sat
  unreleased. Production, running the backend's last release, couldn't support it. Main was green
  and still not releasable.
