# RED baseline and micro-test: cc-guide verifier recall and covered files (2026-11-19)

## Why

Plan 102 changes two verifier contracts. An audit packet now lists the changelog bullets that name its group's terms, and the verifier must answer each one. A files packet now copies the Markdown files its skill covers, and the files rule compares a statement with the component it describes. Two paid micro-tests gate these changes. Gate F tests the files change. Gate A tests the audit change. This record holds the design, the probe, the pilot, each gate's result and the decision.

Spec: `specs/cc-guide-verifier-recall-and-covered-files.md`. Plan: `specs/plans/102-cc-guide-verifier-recall-and-covered-files.md`. Kit: `specs/baseline/red-baseline-cc-guide-verifier-recall/kit/` (its README lists every command).

## Method

- **Arms.** The control arm is the verifier agent file at `START`, `d845fe873c787ae60a71c06d87235827fe9f9e82`. The changed arm is the same file at `ARM_COMMIT`, `e86c27317089176a2721506306217ae2b696e1ed`. The packets come from `FIXTURE_COMMIT`, `7ac62e68049b4ce1786b522d8f04ef8d1a1885a7`.
- **Binary.** Claude Code 2.1.325, sha256 `25fc2449e6a110a26e4bfa43a056ff5e7d4847d5cb6500a8c7b11bf93a130234`. Every rep runs it where the Claude Desktop app keeps it (D6). A copy of that binary does not run on this Mac, because macOS stops a copy whose bundle signature no longer matches. `run.py` checks the hash before every rep.
- **Command.** `claude -p --permission-mode auto --settings <SETTINGS> --max-budget-usd <cap> --output-format stream-json --verbose`. It has no `--model` (PC10). The environment holds nine variables and nothing else (PC11). Each rep runs in its own folder under `/private/tmp/vr102/`. The home folder is the real one (PC2).
- **`SETTINGS`** (PC2, as D5 changed it). It denies `Bash`, `Read(~/**)`, `ListAgents`, `SendMessage`, `PushNotification` and `RemoteTrigger`. It also blocks reads outside the working folder.
- **Reps** (PC9). Valid reps for each arm: audit 5, readme 3, precision 3. Spares: at most 2 for each packet and arm. Caps for each rep: audit $10, files $4, probe $1. Timeouts: audit 60 minutes, files 20, probe 10.
- **Void rules.** V1 to V8 are plan 45's, as the plan amends them. V9 is new (D5). It voids a rep when a record holds a peer-session origin that is not the hand-back of the rep's own verifier, or when the init record lists a cross-session tool.
- **Blind rating.** The controller rates each sheet before `grade.py unblind`. No sheet, printed line or error names an arm.
- **Ceiling.** $130 (D4).
- **Freeze.** `$K/FREEZE.sha256` holds 18 lines: the 12 kit files, both arm files, the fixture hash list, the precision key, the binary record and a copy of the plan's Pre-registration section. The probe and the pilot ran under freeze 2 (`7af01d5f…`). A grader fix then gave freeze 3 (`ad560633bde8fc3156e2f61dc1c93354cb6aeb4e842ed7ca34797cae29f0ffca`, kit at `a22e8b4`). The two freezes differ only in grader files. Freeze 1 was `b6c76273…`.

## Probe (3 reps, $1.15)

The probe is an uncounted rep. It asks the main session to run a denied Bash loop, to read a canary file, to dispatch a probe agent that reads the canary and a docs file, and to list its tools.

| Rep | Cost | Result |
|---|---|---|
| r001 | $0.31 | `Bash` absent from the tool list. The canary read was refused. The canary token appears in no file. A hook refused the Agent call, because the probe prompt named no model. The counted reps' prompt names `sonnet`. |
| r002 | $0.36 | The prompt now names the model. Both canary reads were refused (main session and probe agent). The docs read returned. The probe agent named `Read`, `Grep`, `Glob`, `SubagentHandback` and the advisor. No hook error. The init record still listed four cross-session tools. |
| r003 | $0.48 | Run under D5's `SETTINGS`. The init record lists none of the four cross-session tools and no `Bash`. The other outcomes match r002. |

The init record also carries a messaging socket path. The deny list closes the outbound half of the peer-session channel. V9 and one rule for the controller (no message to a rep session while reps run) guard the inbound half.

A background hand-back from the rep's own verifier arrives as a record whose origin has `kind` `peer`, `handback` true and `from` equal to `senderTaskId`. The last record of a clean run is a `task-notification` result. V9 treats both as normal.

## Pilot (1 changed-arm audit rep, $3.64)

- **Rep.** r004, one audit rep of the changed arm. It ran 744 seconds and exited 0.
- **Validity.** Valid under V1 to V9 after three rulings that the Pre-registration allows. The Agent parameter `run_in_background` is ruled in (the rep passed `false`, the default). The verifier's effort is `xhigh`. Its version is 2.1.325. Production's verifier had the same model (`claude-sonnet-5-5`), effort, version and advisor attachment.
- **Context read by hand (V3).** No marker appears in the verifier's injected context. Its system-prompt parts 1 and 2 equal production's. Part 0 is the arm body. The session context holds no git status.
- **Differences from production.** All of them are the same in both arms. The entrypoint is `sdk-cli` where production's is the desktop app. The dispatch was foreground where production's was background. The runs add a budget attachment. The docs copy sits inside the rep's folder, so the harness loads its `agents.md` page as nested instructions. The MCP instruction blocks come from other connectors.
- **Report.** 85 confirmed rows, 7 corrections, 14 owner's calls, 0 unverified.
- **Pilot check.** It does not trigger. Of 206 listed items, 15 were answered by a B row, 191 were answered none and 0 were left unanswered. The report has 18 kept B rows and none that settle lists as unparseable. P11 and P8 are not scored on the pilot (PC8).
- **A grader defect, found and fixed.** The first grade read 0 of 206 listed items answered. The grader had taken the harness's completion notice, "This agent's report was delivered to you as a message …", for the report. A foreground dispatch whose verifier hands back returns that notice. The grader now skips it, as it skips the launch notice that a background dispatch returns. The pilot was graded again offline from its saved files, so no rep was repeated.
- **Estimate again (D2).** The pilot cost $3.64, below the plan's $4 to $8. The expected total is now about $50 to $66 before spares, against $45 to $105 at planning. With every spare, the worst expected total is about $104. Both stay under the $130 ceiling. Spent so far: $4.79.

## Gate F (files): PASS

Twelve reps ran as one batch, six readme and six precision, three of each in each arm. Every rep finished with exit 0 in 232 to 419 seconds. The batch cost $14.76. No rep was void, so no spare ran. The ratings were entered by hand from the sheets before `grade.py unblind F`. The sheets stay in the private cache (`$K/sheets/`), and no docs text is committed here.

**Ratings.**
- **Readme reps.** Every kept `contradicts` row is on `hooks/README.md` line 97 or 99. These lines state a general rule about exit codes, and the guide qualifies that rule with `onFailure: "block"`. I rated each row SUPPORTED. No kept `contradicts` row covers line 89. Each rep that read line 89 kept a `not covered` row on it.
- **Precision reps.** The rows on `SKILL.md` lines 122 and 124 and on `references/discovery.md` line 13 are on the precision key, so they are SUPPORTED. Two reps (r011, changed arm, and r014, changed arm) each kept one more `contradicts` row, on `references/claude-code.md` line 29. The covered file lists four providers where `haiku` stays Haiku 4.5. The guide names a fifth. An omission from a list leaves the statement true for the four it names, so I rated both rows UNSUPPORTED. If the rating were the other way, the changed arm would show two key misses and no UNSUPPORTED rows. The gate result would not change.

| Rep | Packet | Arm | Cost | readme89 | reach | unsupported | key miss |
|---|---|---|---|---|---|---|---|
| r005 | readme | changed | $1.04 | no | - | 0 | - |
| r006 | readme | control | $1.15 | no | - | 0 | - |
| r007 | readme | control | $1.06 | no | - | 0 | - |
| r008 | readme | changed | $1.07 | no | - | 0 | - |
| r009 | readme | control | $1.17 | no | - | 0 | - |
| r010 | readme | changed | $1.01 | no | - | 0 | - |
| r011 | precision | changed | $1.53 | - | yes | 1 | 0 |
| r012 | precision | control | $1.36 | - | yes | 0 | 0 |
| r013 | precision | control | $1.10 | - | no | 0 | 0 |
| r014 | precision | changed | $1.43 | - | yes | 1 | 0 |
| r015 | precision | changed | $1.40 | - | yes | 0 | 0 |
| r016 | precision | control | $1.44 | - | yes | 0 | 0 |

**Clauses of the Pre-registration.**

| Clause | Changed arm | Control arm | Met |
|---|---|---|---|
| No valid readme rep keeps a `contradicts` row on `hooks/README.md:89` | 0 of 3 | 0 of 3 (reported) | yes |
| No readme rep has more than 2 UNSUPPORTED rows | total 0, at most 0 | total 0 (reported) | yes |
| No precision rep has more than 2 UNSUPPORTED rows | total 2, at most 1 | total 0 (reported) | yes |
| A covered file is named in at least 2 of 3 valid precision reps | 3 of 3 | 2 of 3 (reported) | yes |
| Key misses (reported) | 0 | 0 | - |
| Contradiction rows kept, median and total (DF21, reported) | readme 2 and 5, precision 4 and 11 | readme 1 and 4, precision 2 and 7 | - |

**Result: PASS.** Task 5's two commits stay.

**What the result does not show.**
- The control arm also kept no row on line 89 (0 of 3). The fixture did not separate the arms on that clause, so the clause was met without the control ever failing it.
- The control arm named a covered file in 2 of 3 precision reps, because the packet holds the covered files for both arms. The reach clause therefore separates the arms by one rep.
- The changed arm kept more `contradicts` rows than the control in both packets, and its two UNSUPPORTED rows came from the covered file. The precision cost of covered files is small here (at most 1 for each rep), but it is not zero.
