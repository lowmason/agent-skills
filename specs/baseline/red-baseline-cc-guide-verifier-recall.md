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
