<!-- Shaped the way the reviewer reads: what to look at, what not to, why to believe it. Prose, not
     "Changes:" bullets. 30–80 lines is normal for a real change. -->

<The user problem, in two or three sentences. Ticket key for your own ticket; other people's keys in
prose only.>

### What changed

<One paragraph per non-obvious decision. Each names the alternative rejected and why.>

### What deliberately did NOT change

<Scope held back, and the ticket that holds it. Consumers of the changed contract that were checked and
need nothing.>

### Tests have teeth

| Break applied | Caught by |
|---|---|
| <the break> | <test name(s)> |

### Verification

- Gate `<command>` green on `<sha>`.
- Ran by hand (not in the gate): `<suite / pattern>`, <N> tests ran.
- <Performance: rows / bytes / memory before → after over <fixture>; plan unchanged or explained.>

### Checked and clear

<The questions the reviewer would ask, answered in advance: other implementations of the changed
interface and their fakes, consumers that spell the payload, generated artifacts, scan and column order,
timeouts, migration numbers against main at <sha>.>
