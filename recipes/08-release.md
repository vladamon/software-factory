# 08 · Release

Is it running where users are, and how far behind is prod?

Merged isn't shipped. A change is done when it runs in production and someone has confirmed that by
looking at what's actually running, not at the config that says what should be. Between main and
production sits a chain of hops (tag, image, chart, environment pins), each run by a different
workflow, bot or person. This station walks the chain and checks each hop before the next one.

## When to use

- Whenever main holds user-visible work that production doesn't.
- On a cadence, even when nobody asks: the distance to production is itself a measure (`docs/line.md`).
- After any rollout, to verify.

## Inputs I need before starting

- The profile's **Release chain**: every hop, who or what performs it, and how production is triggered.
- The person's word for each outward hop (`docs/authority.md`). A merge to the deploy repo may apply an
  environment; production always needs its own word.
- Where the environment's actual state can be read: registry digests, the running workloads' image IDs.

## Steps

### Know the distance

1. **Measure what's waiting.** Per component, count the commits on main since the last release tag and
   list the user-visible changes among them. A feature that's merged but unreleased is invisible to
   users and can't be verified by them.

### Cut

2. **Claim the release, then tag a tree that was gated.** When more than one session or person can
   release, read the shared log and ask whoever holds the release thread before tagging; two parallel
   tags race on version numbers at every later hop. The tag's commit is on main, and its tree is the one the gate passed
   on: main's own CI run, or a PR head whose tree is byte-identical. Use annotated tags.
3. **Verify the artifact, not the workflow.** Confirm the image or package exists in the registry under
   its tag and digest, for every architecture. When the release workflow fails *after* publishing (a
   registry read-after-write lag, say), check the artifact by hand before rerunning.

### Walk the chain

4. **Each hop waits for the previous hop's artifact.** Don't merge a pin to a chart version that hasn't
   been published, or an environment bump to a chart that doesn't exist yet. A bump opened early fails its
   preview, which is expected and useful; merging it is the mistake.
5. **Re-read the version file before opening and before merging.** Version numbers in a shared chart or
   manifest race with every other releaser. On a collision, check what each published artifact actually
   contains; two PRs can each "win" a different half of the same version.
6. **Let bots do the bot hops.** When a hop belongs to automation (a bump PR raised by the chart's
   release), wait for it. If it doesn't arrive in the usual time, read the dispatch run before
   hand-writing a replacement. The usual cause is an expired credential, and it repeats silently on
   every later release until it's rotated.
7. **Roll out in dependency order.** A component that migrates on boot goes first and reaches ready. A
   component that verifies the schema and refuses to start on one it doesn't recognise goes after.
   Restarting them in the wrong order crash-loops the verifier.

### Verify each environment

8. **Verify by digest.** Compare the running workloads' image IDs with the registry digest of the
   release. Config says what should run; the digest says what does. How an environment picks images
   (pins vs a moving tag) changes over time, and the rule files lag behind.
9. **Smoke the user path, not the readiness probe.** Open the feature as a user would, on real data. A
   workload can be ready and still broken, if a dependency it binds at boot wasn't there yet and it
   degraded instead of failing readiness.
10. **Read the whole deploy log.** A step marked to continue on error can fail inside a green check
    (recipe 05, step 11).

### Production

11. **Production is a human-authored change plus a deliberate trigger.** A person writes the production
    change; the trigger is a manual dispatch with a typed confirmation. No merge, bot or schedule can
    deploy production. The production preview must plan only the intended change, and it fails closed
    when its output can't be read.
12. **Verify production by digest and user path**, as in steps 8 and 9.
13. **Record where each component now is.** Version per environment, and what is still waiting. That's
    state, so it goes to memory or the tracker, never into a rule file.

## What good output looks like

```
distance: ui 6 commits since v1.4.2 (2 user-visible), api 90 since v2.0.0 (one whole feature area).
cut:      ui v1.4.3 at 4e1b2c9 (tree = gated PR head); registry: v1.4.3 + sha-4e1b2c9, amd64+arm64 ✓
chain:    chart 3.2.0 published → bot bump arrived ~30 s later → merged on word → staging deploy green
verify:   staging ui pods imageID = v1.4.3 digest ✓; the new figure renders on real data ✓
prod:     not yet: prod PR drafted, waits for the word.
```

## Done means

- Every environment the release targeted runs the release's digest, checked on the running workloads.
- The user path was exercised in each, on real data.
- Production changed only through a human-authored change and a deliberate trigger.
- Distance to production is recorded per component, as state.

## Traps

- **Two releases, one version.** Two chart PRs each claimed the same version number minutes apart. The
  release asset carried one PR's content and the OCI push carried the other's. → Step 5: re-read before
  merging, and on a collision check what each artifact contains.
- **The bot that stopped coming.** The dispatch that raises the environment bump failed on an expired
  token for three chart releases in a row. No PR arrived and nothing alerted. → Step 6.
- **The posture that kept changing.** In three weeks an environment moved from a moving `main` tag
  to pinned versions, back to the moving tag, then to exact production pins for a release rehearsal.
  Both the rule file and the agent's memory described an earlier posture, so anyone who trusted
  them would "ship" by bumping a pin the environment ignored. → Step 8: digests, not config.
- **Ready but empty.** An API came up during a rollout before its message bus's DNS existed. It failed
  the bind once, kept running with a nil reader (the readiness probe couldn't see it), and returned 503 on one endpoint
  until restarted. → Step 9: exercise the user path.
- **The verifier restarted first.** A component that verifies the schema was restarted before the
  component that migrates it, and crash-looped against the old schema. → Step 7.
- **Merged for weeks, shipped to nobody.** A backend ran 217 commits past its last release, and a whole
  product area built and merged in that time was visible only on staging. → Step 1, on a cadence.
- **Two sessions, one release.** A sweep finished in one agent session while another session was mid-way
  through a release of the same component. Checking its log first showed the sweep was already live on
  staging through the moving tag, so the release went ahead once, from one place, instead of twice.
  → Step 2.
- **Same commit, different digest.** The release workflow rebuilt the tagged commit, so production's
  image had a different digest from the build staging had been running for hours, from the same source.
  → Step 8: compare against the release's digest, not the commit.
- **Red after publish.** A release workflow failed at its final inspect step on a registry
  read-after-write lag, after the image had already published correctly. The image was checked by hand
  first, and only then was the failed job rerun. → Step 3.
