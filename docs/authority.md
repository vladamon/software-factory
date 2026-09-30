# Authority

What an agent may do alone, what waits for a person's word, and what never happens. The question is
never "is the agent good enough"; it is "can this be undone, and does anyone outside the room see it".

## Three tiers

| Tier | What | Examples |
|---|---|---|
| **Alone** | Local, reversible, invisible to others | Read anything; edit and commit in its own worktree; run the gate; run tests and mutations; draft messages, PR bodies, tickets |
| **On the word** | Visible to others, or hard to undo | Push a branch or open a PR; post a message, comment or review; change a ticket's state or owner; merge; delete a branch; start a staging deploy |
| **Never** | Can't be undone, or skips a human decision that's there on purpose | Deploy production from a merge; hand-write a change a bot is responsible for producing; stop a process it didn't start; force-push someone else's branch |

"On the word" means **per action**. The person's word covers the message, the merge or the batch it
was given for. It doesn't carry over to the next one, including follow-ups to the same work.

## Rules with a history

- **Approval does not carry.** A one-off "merge on green" was reused on a later PR by a script that
  checked CI only. It merged 41 minutes after the reviewer posted "not approving yet". Any automated
  merge checks review state (no changes requested, no withheld approval) as well as CI.
- **An approval covers a sha.** A PR was merged on an approval given ten commits earlier. Before
  merging, compare the approved sha with the head.
- **Production is human-authored.** A merge to main applies staging only. Production takes a separate
  change a person wrote, plus a dispatch with a typed confirmation.
- **Draft first, in the team's voice.** Anything outward is drafted and shown before it's sent. The
  voice (tone, length, how requests are phrased) belongs in the profile, because it belongs to the team.
- **Stop only your own processes.** Killing by process name matches every server of that kind,
  including the developer's own dev servers. Stop a process by the port you started it on, and only that one.
- **Memory leaving the machine is on the word.** An agent that built a memory-sync store tried to
  make its first push to the remote itself and was stopped: memory carries internal names and people,
  and sending it off the machine is outward. The person made the first push and switched on the sync
  hooks. From then on the hooks the person installed carry it; that setup is the written policy
  (below) that moves this one line to *alone*.
- **Before deleting, write down how to undo it.** Remote branch deletions leave no local trace. Record
  branch, sha and PR number first, and restore from the PR's permanent ref (`refs/pull/<N>/head`).

## Moving a line between tiers

A line moves from *on the word* to *alone* by a written policy, not by habit. Example: "the repo owner
reviews and merges a teammate's PR when it has no blocker in another layer". The policy goes in the profile
under *Reviewers and ground*, with its date and who agreed to it. Nothing moves out of *never*.
