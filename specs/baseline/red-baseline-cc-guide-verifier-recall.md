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

## Gate A (audit): FAIL

Ten reps ran in two waves of the audit packet, five in each arm. The first wave was 2 pairs (r017 to r020). `grade.py stop gateA1` printed `continue`, so the second wave ran 3 more pairs (r021 to r026). Every rep finished with exit 0 in 578 to 841 seconds. No rep was void and none was pending, so no spare ran. The ten reps cost $34.28 (control $15.86, changed $18.42). The ratings were entered by hand from the sheets before `grade.py unblind A`. The sheets stay in the private cache (`$K/sheets/`), and no docs text is committed here.

**Ratings.**
- **Kept corrections.** I checked every kept A row against the docs at the fixture commit. All of them are SUPPORTED, so each rep has 0 UNSUPPORTED rows. The rows that repeat across reps are the retirement scope of Haiku 4.5 (L211), the Explore model under Fable and the reach of `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` (L218), the one-hour helper requests (L405), `/compact` under Safe now (L410), the effort-change cache caveat and the saved-per-model level (L426), `ANTHROPIC_DEFAULT_MODEL` in the precedence list (L429) and the direction of the tokenizer comparison (L441).
- **P11 and P8.** P11 is a B row on `changelog.md:1288`, or a SUPPORTED C row that names `deniedModels` as blocking a model that `availableModels` permits. P8 is a B row on `changelog.md:1702`. Both lines of each sheet are mechanical. The C rows on `deniedModels` (`model-config.md:361-364`) gave P11 to r021, r023 and r025. In r018, r019 and r025 the B row gave it as well.
- **Borderline rulings.** Each is in the ledger with its cost if wrong. A row stays SUPPORTED when (1) its main correction holds and a subordinate clause leaves out an exception (the Explore exception to FORCE alone, the `CLAUDE_CODE_EFFORT_LEVEL` exception for `max`, the HIPAA and `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` exclusions); (2) its scope comes from the guide line it corrects (the subscription scope of L405); (3) its figures follow from the docs' 30% and the price rows (7.7x against 10x at L441); (4) it gives the real URL of `llms.txt` (L485). A row that says the `sonnet` alias is Sonnet 4.5 or 4.6 on the partner platforms counts as P10, wherever the verifier filed it. If every one of these rulings were the other way, a rep would read 1 or 2 UNSUPPORTED rows. Neither failed clause below depends on any of them.

| Rep | Wave | Arm | Cost | P11 | P8 | Unsupported | Listed items: B row, none, unanswered |
|---|---|---|---|---|---|---|---|
| r017 | 1 | control | $3.19 | no | no | 0 | 0, 0, 206 |
| r018 | 1 | changed | $4.20 | yes | no | 0 | 14, 192, 0 |
| r019 | 1 | changed | $3.30 | yes | yes | 0 | 15, 191, 0 |
| r020 | 1 | control | $3.07 | no | yes | 0 | 4, 0, 202 |
| r021 | 2 | changed | $3.14 | yes | yes | 0 | 10, 196, 0 |
| r022 | 2 | control | $3.18 | no | no | 0 | 3, 0, 203 |
| r023 | 2 | changed | $4.07 | yes | no | 0 | 2, 204, 0 |
| r024 | 2 | control | $3.42 | no | no | 0 | 2, 0, 204 |
| r025 | 2 | changed | $3.71 | yes | no | 0 | 4, 202, 0 |
| r026 | 2 | control | $3.00 | no | no | 0 | 0, 0, 206 |

**Clauses of the Pre-registration.** The control column for P8, DF7 and the DF8 labels is the baseline of the clause. Plan 45's DF8 allows the changed arm to keep one fewer than the control.

| Clause | Changed arm | Control arm | Met |
|---|---|---|---|
| P11: changed in at least 4 of 5 valid reps | 5 of 5 | - | yes |
| P8: changed in at least 4 of 5 valid reps | 2 of 5 | 1 of 5 (reported) | **no** |
| P11: control in at most 1 of 5 valid reps | - | 0 of 5 | yes |
| DF7: changed UNSUPPORTED total at most control's + 3 | 0 | 0 (reported) | yes |
| DF7: no changed rep above 2 | at most 0 | - | yes |
| DF8 P1 (Haiku 4.5 retirement scope, L211) | 1 | 2 | yes |
| DF8 P2 (Explore under Fable, L218) | 5 | 5 | yes |
| DF8 P3 (reach of FORCE, L218) | 5 | 5 | yes |
| DF8 P4 (one-hour helper requests, L405) | 5 | 5 | yes |
| DF8 P5 (`/compact` rebuilds, L410) | 4 | 4 | yes |
| DF8 P6 (effort-change cache caveat, L426) | 5 | 4 | yes |
| DF8 P9 (`ANTHROPIC_DEFAULT_MODEL` in the precedence list, L429) | 5 | 4 | yes |
| DF8 P13 (tokenizer comparison direction, L441) | 1 | 4 | **no** |
| DF8 P14 (`CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL`) | 1 | 2 | yes |
| P7, P10, P12 (reported) | 4, 1, 0 of 5 | 0, 3, 0 of 5 | - |
| Corrections kept (DF21, reported) | median 7, total 37 | median 7, total 37 | - |

**Result: FAIL.** Two clauses are not met: P8 (2 of 5, where 4 are needed) and the DF8 retention of P13 (1 against 4). The rule is "FAIL otherwise", and there is no rerun without the owner's word.

**What the result does and does not show.**
- **P11 separates the arms cleanly.** The changed arm met it in 5 of 5 valid reps and the control in 0 of 5. The change lifted the recall of the `deniedModels` omission, which is the case it was built for. The result does not take that back.
- **The listed-item answers separate the arms too.** The changed arm left 0 of 206 listed items unanswered in all 5 reps. The control left 202 to 206 unanswered in all 5 reps. Both arms kept B rows (changed 4 to 18, control 0 to 8). This is the mechanism the change added, and it works.
- **P8 does not separate the arms.** The changed arm kept a B row on `changelog.md:1702` in 2 of 5 reps (r019, r021) and the control in 1 of 5 (r020). In the other three changed reps (r018, r023, r025) the verifier answered that listed item with none. The mechanism does not make the verifier keep this B row.
- **P13 is a loss.** The changed arm kept a correction on L441 in 1 of 5 reps (r023), and the control in 4 of 5. The sheets do not say why. The record does not claim a cause.
- **Gate scope.** P8 and P13 are single items in a 206-item packet. The gate counts them as clauses, so two misses give FAIL even though the changed arm kept every other label at least as often as the control and met P11 in every rep. A new round with a changed arm is a different test and needs the owner's word.

## Decision

- **Gate F passed.** Task 5's commits stay (`ac0552f`, `e86c273` and `d827dd4`: B3 with B5, and C1 with C2).
- **Gate A failed, so Part A reverts whole** (spec E1). Task 2 came out first, as commit `7d4fc08` (it reverts `97c3028`, `2670468` and `965ab3d`). Task 1 followed as commit `3b0ee55` (it reverts `3690bad`, `c0e2569` and `a745566`). The audit text in `SKILL.md` ("about $2.50 to $5.30") does not change, because only a gate A pass edits it. For the record, the valid changed audit reps cost $3.14 to $4.20, which would round out to $3.10 to $4.20.
- **Part B's code stays** (spec E2): Tasks 3 and 4, with their tests.
- **A plan defect, and the owner's ruling (D7).** The plan expected every check to pass after a revert. The kit's audit fixture builder calls `packets.listed_bullets`, which is Part A's code, so 16 kit tests failed once Part A was reverted. The owner chose a new `kit/conftest.py` that skips those 16 tests with a reason while that function is absent. The file is not one of the 12 frozen kit files. The tests run again when the two revert commits are reverted.
- **Checks after the revert** (each count as a change from just before it):
  - `cc_guide` suite: 908 passed, down from 938. The 30 missing tests are Part A's.
  - Kit suite: 325 passed and 16 skipped, against 341 passed. The 16 skips are the D7 tests.
  - `cli.py lint`: the same three STALE lines as before the revert. `check_conformance.py` and `sync_runtime_assets.py --check` report nothing. `build/run_commit_lints.sh` passed on each commit of this task.

## Disposition

| Item | Clause that closes it | State |
|---|---|---|
| I3: the audit verifier writes no B row for the changelog entries behind P11 | Gate A passes | **Stays open.** Gate A failed. `→ progress` note: the changed arm answered every listed item (0 of 206 unanswered in 5 of 5 reps, against 202 to 206 unanswered in 5 of 5 control reps), and it missed P8 (2 of 5) and P13 retention (1 against 4). |
| I4: the audit verifier's omission recall was 3 of 7 known positives | The changed arm meets P11 in at least 4 of 5 valid reps | **Stays open, and the owner rules at the completion gate.** The clause is met (5 of 5, against 0 of 5 for the control). The change that met it is reverted, and the item's own done-when asks for a change in the repo that lets an audit report `deniedModels`. |
| I5: the files rule has no precision fixture | Gate F's precision counts are reported for both arms | **Closes.** Changed arm: 2 UNSUPPORTED rows in total, at most 1 in a rep. Control arm: 0. |
| I6: the files rule must take its reference case from the component the file describes | C1 landed with its C2 test, and gate F's readme clause is met | **Closes.** C1 (`d827dd4`) landed with its test. No valid readme rep kept a `contradicts` row on line 89 (0 of 3 in each arm). |
| I1 and I2: the files pass of the covered files | E3's fresh `/cc-guide files` pass | **Stay open** with a `→ progress` note. Part B and its tests landed. E3's pass, run in its own session, closes both. |
| The three next-kit items | Plan 100 (D1) | No note from this plan. |

**Next step.** After the plan merges, run E3's `/cc-guide files` pass on each citing skill whose covered files state Claude Code facts. It runs in its own session and alone, under the machinery rule. Gate A needs a decision of its own: a new round with a different changed arm needs the owner's word, and so does closing I4. The kit and its freezes stay in the cache for that round.
