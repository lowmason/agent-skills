# Verifier-recall kit (plan 102)

This kit runs plan 102's micro-test of the cc-guide verifier contract. It runs paid `claude -p` reps one at a time, each in its own folder, and keeps their raw output out of the repo. Every rule here comes from plan 102, `specs/plans/102-cc-guide-verifier-recall-and-covered-files.md`: its Planning record (PC1 to PC14), its Pre-registration and its Tasks 6 to 8. Where plan 102 adopts plan 45's rules (V1 to V8, DF15), plan 45 is the source.

## Folders

- **`$K`** is `~/.cache/agent-skills/scratch/vr102/`. It holds everything a run writes. Nothing in it is committed, because packets, reports and transcripts hold docs text.
- **`R`** is `/private/tmp/vr102/`, the rep root. Rep `<rid>` runs in `R/<rid>/work/`, with `R/<rid>/tmp/` as its `TMPDIR`. When the rep ends, the runner moves `R/<rid>/` to `$K/homes/<rid>/`, so `R` is empty before each rep.

`common.py` sets both. `common.k_dir()` reads `HOME` when it is called, and `common.R` is a module attribute, so the tests move both to a temporary folder.

## Files

- `common.py` holds the paths, caps, timeouts, settings, prompts and packet table.
- `build.py` adds reps to `$K/plan.json` and their ids to batch files.
- `run.py` runs one batch, one rep at a time.
- `postprocess.py` removes the key `credential_expires_at` from saved `.json` and `.jsonl` files.
- `test_vr_runner.py` holds the no-model tests, which use a stub `claude`.

Plan 100's kit was not on `origin/main` (`1deb0ec`) when Task 6 ran. So `postprocess.py` is written to Task 6's Interfaces block, not copied from plan 100's kit. Task 7 adds `fixtures.py` and `grade.py`. Task 8 adds `probe.txt` and `vr-probe.md`.

## Commands, in order

Run each command from any folder, as `uv run python <kit>/<script>`. Do not start a rep before the owner approves the ceiling (Task 8 Step 4).

1. `fixtures.py build` (Task 7) writes the packet copies and the docs copy to `$K/fixtures/`.
2. Task 8 Step 1 holds the binary and writes `$K/binary.txt`. Task 8 Step 3 writes the arms to `$K/arms/control.md` and `$K/arms/changed.md`. Task 8 Step 4 writes the approved ceiling to `$K/ceiling.txt`.
3. `build.py probe`, then `run.py probe`. The probe is an uncounted rep. `build.py probe` writes a new random token to `$K/canary.txt`.
4. `build.py pilot`, then `run.py pilot`. The pilot is one uncounted changed-arm audit rep (PC8).
5. Gate F is one batch, `gateF`, built by two `batch` calls: `build.py batch gateF readme 3`, then `build.py batch gateF precision 3`. Then run `run.py gateF`.
6. Gate A, first wave: `build.py batch gateA1 audit 2`, then `run.py gateA1`, then `grade.py stop gateA1` (Task 7). Second wave, if the stop rules say continue: `build.py batch gateA2 audit 3`, then `run.py gateA2`.
7. For each void rep: `build.py spare <rid>`, then `run.py <batch of that rep>`.

`build.py` prints each new rep id and its batch. `run.py` skips a rep that already has `$K/results/<rid>/`, so you can run a batch again after a spare joins it.

## build.py

- `batch <name> <packet> <pairs>` adds `<pairs>` (control, changed) pairs of one packet. Each pair's two arms take a random order from `secrets.randbelow` (DF15). A second call with the same name appends to that batch, so one batch can hold two packets.
- A batch name holds letters, digits and hyphens, in upper or lower case. `probe` and `pilot` are reserved in any case. A name that differs from an existing batch only in case is refused, because the macOS disk takes `gateF.txt` and `gatef.txt` as one file.
- `spare <rid>` adds one rep with the packet and arm of void rep `<rid>`, and appends it to that rep's batch file. A packet and arm get at most 2 spares. The refusal of a third names no arm.
- `probe` adds the probe rep to `$K/batches/probe.txt`. `pilot` adds the pilot to `$K/batches/pilot.txt`.

Rep ids run `r001`, `r002` and on, across every command, and are never reused. `$K/plan.json` holds `{"reps": [...]}`. Each rep has `rid`, `batch`, `packet` (`audit`, `readme`, `precision` or `probe`), `arm`, `role` (`counted`, `spare`, `probe` or `pilot`) and, for a spare, `replaces`. `$K/batches/<name>.txt` lists rep ids only, one on each line, in run order.

Exit 0 on success, 1 on a refusal, 2 on a usage error.

## run.py

`run.py <batch>` runs the reps of `$K/batches/<batch>.txt` in order. It skips each rep that already has a results folder. For every other rep, it does these steps:

1. It refuses (exit 3) while `R` holds anything.
2. It refuses (exit 4) when the held binary's sha256 differs from the one in `$K/binary.txt`.
3. It holds the rep and every later rep of the batch (exit 5) when the spend so far plus the rep's cap exceeds the ceiling. The spend counts each rep that has a results folder, at its `total_cost_usd`, or at its cap when it left no result. At equality the rep runs.
4. It builds the rep folder (below). A missing arm file, packet copy, docs copy or `probe.txt` refuses (exit 2) and leaves `R` empty. A copy that fails also refuses (exit 2), and its message names no path.
5. It runs `command(rid)` in `R/<rid>/work/` with the prompt on stdin, and stops it at the rep's timeout.
6. It moves the session's files from `$HOME/.claude/projects/` to `$K/results/<rid>/project/<slug>/`. It finds them by the first init record's `session_id`.
7. It writes `result.json`, the stream's last `result` record.
8. It strips `credential_expires_at` from every `.json` and `.jsonl` file under `$K/results/<rid>/`. If the string is still in any file there, the rep is void (V6).
9. It writes `status.json` and moves `R/<rid>/` to `$K/homes/<rid>/`.

Steps 6 to 9 run even when the rep fails or times out.

When the runner itself stops while a rep runs, it stops the rep first. This covers Ctrl-C and SIGTERM, which the runner turns into a normal exit. It stops the rep's whole process group, then runs steps 6 to 9 and records the rep as interrupted. An interrupted rep leaves no result, so it counts at its cap, and it needs a spare. No later rep of the batch starts.

The rep folder holds the arm's file as `.claude/agents/cc-guide-verifier.md` and the packet copy as `packet/`, without `report.md` or `settled.json`. An audit rep also gets the docs copy as `docs/`, and its `index.json` `docs` and `quotes.docs` name `R/<rid>/work/docs`. The probe rep gets the control arm's file, the kit's `vr-probe.md` as `.claude/agents/vr-probe.md` and the docs copy, but no packet.

The prompt is `common.MAIN`, which holds the dispatch of the cc-guide skill's step 1 for the rep's packet. The probe's prompt is the kit's `probe.txt`, with `{canary}` replaced by the absolute path of `$K/canary.txt`.

`command(rid)` gives this argv: `<held binary> -p --permission-mode auto --settings <SETTINGS> --max-budget-usd <cap> --output-format stream-json --verbose`. It has no `--model` (PC10) and no `--setting-sources`. The environment is built from scratch and holds only `HOME`, `USER`, `LOGNAME`, `SHELL`, `LANG`, `PATH`, `TMPDIR`, `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` and `DISABLE_AUTOUPDATER` (PC11).

`SETTINGS` is PC2's, as D5 amends it. Its `permissions.deny` list holds `Bash`, `Read(~/**)` and the four tools of `common.CROSS_SESSION_TOOLS`: `ListAgents`, `SendMessage`, `PushNotification` and `RemoteTrigger`. It also sets `blockReadsOutsideWorkingDirectories`. A name-only deny rule takes a tool off the session's tool list, so the init record of a rep lists neither `Bash` nor any of the four. The deny list stops a rep reaching another session. It does not close the inbound half, because another session can still message a rep. Two things close that half: V9 (the grader voids a rep whose records hold a peer origin), and the rule that no controller session messages a rep session while reps run.

| Packet kind | Cap (`--max-budget-usd`) | Timeout |
|---|---|---|
| audit | $10 | 60 minutes |
| files (readme, precision) | $4 | 20 minutes |
| probe | $1 | 10 minutes |

`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` is 4,200,000 (70 minutes), above the audit timeout (PC9).

## Formats of the files the owner or a later task writes

- `$K/binary.txt` (Task 8 Step 1) has three lines: `path: <absolute path of the held copy>`, `version: <its --version output>` and `sha256: <its sha256>`.
- `$K/ceiling.txt` (Task 8 Step 4) holds one number, the ceiling in USD, such as `130`.
- `$K/results/<rid>/status.json` holds `exit` (null after a timeout or an interruption), `timed_out`, `interrupted`, `seconds` and `strip_ok`. A `strip_ok` of false makes the rep void under V6.

## Blind reading

Plan 45's DF15 keeps the arm of each rep from the reader until every verdict is in. So `build.py`, `run.py` and `postprocess.py` print rep ids, statuses and costs only. A batch file names rep ids only. Only `$K/arms/`, `$K/plan.json` and `$K/homes/` name an arm. Do not read them before `grade.py unblind`.

## Tests

`uv run python build/run_suites.py cc-guide-verifier-recall-kit` runs the tests. Each test sets `HOME`, `common.R` and `common.KIT` to temporary folders and checks them before it runs a rep. The held binary is a stub `claude`, so no test reaches the real `$K`, `R` or `~/.claude/projects/`, and no test spends money.

On macOS, a Python process adds `__CF_USER_TEXT_ENCODING` to its own environment at startup. So the stub records the environment it got at exec, read through `KERN_PROCARGS2` (or `/proc/self/environ` on Linux), not `os.environ`.

## Task 7: fixtures.py and grade.py

### fixtures.py build

`fixtures.py build` writes `$K/fixtures/` from the masters under `~/.cache/agent-skills/`. It only reads the masters, and every write goes under `$K`.

- `audit-control/` and `audit-changed/` are copies of the audit master. Only `audit-changed/` gets `listed.md` and an `index.json` `listed` key, just after `releases`. `packets.listed_bullets` computes the items from that copy's own `changelog.md` and `guide.md`, with the terms of group `models` under the `manifest.toml` of commit `5bd78a7`.
- `docs/` is a copy of the 2.1.296 docs snapshot.
- `readme/` is a copy of the readme master. Its `index.json` gets `"covered": {}`.
- `precision/` is a copy of the packet that Task 7 Step 1 built in `$K/masters/precision/`.

No packet copy holds its top-level `report.md` or `settled.json`. The script then writes `$K/fixtures.sha256`, a `shasum -a 256` listing of each file under `$K/fixtures/`. Each path in it starts at `$K`, so `cd $K && shasum -a 256 -c fixtures.sha256` checks the copies. The script prints the number of listed items.

The script refuses (exit 1) in these cases, and then writes no fixtures:

- `$K/fixtures/` exists. A second build cannot change fixtures that the freeze hashes.
- A master is missing. The message names the master (`audit`, `readme`, `precision` or `docs`).
- The listed items hold no item at changelog line 1288 (P11) or 1702 (P8).

It builds in `$K/fixtures.part/` and renames that folder only when every copy is done. Any other failure exits 2 and prints the exception type only.

### grade.py

1. `grade.py <batch>` writes a sheet for each rep of the batch that has results. It prints one line for each rep: its sheet, its void checks and its pending checks. `grade.py pilot` and `grade.py probe` grade the two reserved batches. It reads both arm files before it grades any rep. If one is missing or unreadable, it refuses the whole batch (exit 1) with `an arm file is missing or unreadable`, and it writes no sheet.
2. `grade.py stop <batch>` applies the first-wave stop rules of gate A. It prints exactly one line: `continue`, `stop: UNSETTLED` or `stop: FAIL`.
3. `grade.py unblind A` or `grade.py unblind F` prints the tables of that gate, with the arm of each rep from `$K/plan.json`.

Exit 0 on success. Exit 1 on a refusal, or when a rep cannot be graded. Exit 2 on a usage error or a failure. A failure prints the exception type and the rep id, never the exception message, because a message can name the file of an arm.

### The sheet

`$K/sheets/<rid>.txt` names no arm. It holds these lines, in this order:

- The VOID checks V1 to V8. Each check is `ok`, `void` with its reasons, or `pending` until `$K/pilot.json` gives the value that the check needs. V3 shows `hits` when a marker of `common.MARKERS` is in the injected context of the verifier. Trace each hit by hand.
- The calls that the read fence refused (V2 logs them, but they do not make a rep void), and the V3 hits in the main session (recorded only).
- The `void` and `pending` summary lines, the cost (`total_cost_usd` of `result.json`) and the duration (`seconds` of `status.json`).
- The report source, `reports/<rid>.md`, and the settle lines for that report.

The report is a finished Agent result that is not a launch notice. If there is no such result, the report is the last `SubagentHandback` message of the verifier. The last text of the verifier is never the report.

Settle runs on a copy of the packet in `$K/settle/<rid>/packet/`, with the report as `report.md`. Each audit rep of either arm settles against a copy of `audit-changed/` (DF15). In that copy, `docs` and `quotes.docs` name `$K/fixtures/docs`. The sheet shows `<packet copy>` in place of the folder. It leaves out the closing commands of settle and the `held, not cited:` line of a files packet.

An audit sheet also lists these items:

- each B row on `changelog.md:1288`, `:1702` or `:224`
- each row that names `deniedModels`
- each kept correction and C row, with its guide line and section (the P1 to P14 candidates)
- the listed-item line of settle, and the B-row counts (kept and unparseable)

A files sheet also lists these items:

- each kept `contradicts` row (a row on a covered file shows `covered file`)
- for a precision rep, whether each such row overlaps an entry of `$K/precision-key.tsv` (`on key`, `not on key`, or `key missing` when the file is absent)
- whether a kept row names a covered file, with those rows
- each row on `hooks/README.md` lines 85 to 93

`$K/sheets/<rid>.json` holds the measures that `unblind` reports: the void and pending checks, cost, seconds, the correction or contradiction count (DF21), the B-row counts and the listed-item line.

### V1 to V8 as the grader reads them

- **V1:** the stream has exactly one main-session Agent call and no other main-session tool call (a server tool, such as the advisor, does not count). The call names `cc-guide-verifier` and passes the exact dispatch of `common.DISPATCH`. It passes no parameter other than `description`, `subagent_type`, `prompt` and `model`, and `model` is `sonnet`. The session holds exactly one verifier transcript.
- **V2:** a Read, Grep or Glob of the verifier that names a path outside `R/<rid>/work/` and returned, or a Grep or Glob result that lists such a path. A path is resolved with `~` expanded, a relative path taken from the work folder, symlinks followed, and `/tmp` and `/System/Volumes/Data/private/tmp` read as `/private/tmp`. There is no exemption for the docs. One folder outside `work/` counts as inside: the rep's own session tool-results folder, `$HOME/.claude/projects/<slug>/<session>/tool-results/`, where `<session>` is the session id of the stream's init event and `<slug>` is a folder of the rep's results that holds `<session>.jsonl` (plan 45's ruling 6). A rep that reads back its own saved Grep output reads no answer. The match is exact and comes after the path is resolved, so a `..` out of that folder, another session's folder, another folder of the same session (such as `subagents/`), the session's own `.jsonl` and a `tool-results` folder under another slug are all still outside.
- **V3:** a marker in an attachment or a system record of the verifier. The first part of a prompt snapshot (the contract) is not screened.
- **V4:** an `instructions` attachment, or a `session_context` that holds `gitStatus`.
- **V5:** a prompt snapshot whose first part is not the body of the arm file, that is, the text after the frontmatter, stripped. No snapshot is also void.
- **V6:** a stream that does not parse, a line of a verifier transcript that does not parse (not strict UTF-8, not JSON, or JSON that is no object; a blank line does not count), no result record, a result that is an error, a budget stop, a failed or killed subagent, no `status.json`, an interruption, a timeout, a null or non-zero exit, `strip_ok` false, `credential_expires_at` anywhere in `$K/results/<rid>/`, or no report.
- **V7:** a verifier record whose model is not `claude-sonnet-5-5`, or whose effort or version differs from `pilot.json`. For the pilot rep, the check needs one effort and one version and shows both.
- **V8:** the advisor attachments of the verifier differ from the production comparison in `pilot.json`.

### $K/pilot.json

The controller writes this file after the pilot (Task 8 Step 6). Until it has a key, the checks that need that key show `pending`.

```json
{"effort": "xhigh", "version": "2.1.327", "advisor": true, "agent_params": ["run_in_background"]}
```

- `effort` and `version` are the effort and the transcript `version` of the pilot verifier (V7).
- `advisor` is true when the production verifier had an advisor attachment (V8).
- `agent_params` is optional. It lists the Agent parameters that the pilot ruled in (V1).

### $K/RESULTS.md

Each verdict is one line, `<rid> <verdict>`, with an optional `- ` or `* ` list marker. The grader skips each line that does not start with a rep id. It refuses a line that starts with a rep id but is not a verdict, and a verdict that a rep has twice.

| Rep | Required verdicts |
|---|---|
| every gate rep | `valid` or `void` |
| valid audit rep | `P11 yes` or `P11 no`, `P8 yes` or `P8 no`, `hits P1 P3 ...` or `hits none`, `unsupported <n>` |
| valid readme rep | `readme89 yes` or `readme89 no`, `unsupported <n>` |
| valid precision rep | `reach yes` or `reach no`, `keymiss <n>`, `unsupported <n>` |

A void rep needs only `void`. `hits` takes the labels P1 to P14, except P8 and P11, which have their own lines. `readme89 yes` means that the rep keeps a `contradicts` row that covers `hooks/README.md:89`.

### stop and unblind

`stop` and `unblind` refuse until each rep they read has a sheet, its measures file `$K/sheets/<rid>.json` and its verdicts. A rep with a `void` verdict needs none of them. A `valid` verdict is also refused while the sheet lists V1, V2 or V4 to V8 as void or pending, because a check the grader decides overrules the hand. A sheet graded before `$K/pilot.json` existed (`pending: V7, V8`) is refused until it is graded again. V3 stays a hand check, so a V3 line never blocks. A `void` verdict on a clean sheet is allowed. The refusal names rep ids only.

`stop <batch>` reads a batch of counted and spare audit reps, and counts valid reps only. It refuses (exit 1) while either arm has fewer than 2 valid reps. That is exactly when a void rep has no valid spare. The refusal names those void reps in id order, and nothing else, so it shows nothing the sheets do not. A spare counts for the void rep it `replaces`, and for any rep that rep replaced. Add a spare with `build.py spare <rid>`. After 2 spares for a packet and arm, an arm that is still short means the result is UNSETTLED, for the owner (plan:171), and `stop` keeps refusing. With 2 valid reps in each arm, these rules apply in this order:

1. `stop: UNSETTLED` when the control meets P11 in 2 valid reps. This rule wins when both stop rules hold.
2. `stop: FAIL` when the changed arm misses P11, or misses P8, in 2 valid reps.
3. `continue` otherwise.

`unblind A` reads every counted and spare audit rep. `unblind F` reads every counted and spare readme and precision rep. Each prints its reps with their arms, a table row for each clause (`clause | arm | requirement | observed | met`), the reported measures and a `result:` line. The pilot and the probe are in no gate.

- **Gate A** with 5 valid reps in each arm: PASS when the changed arm meets P11 and P8 in at least 4, the control meets P11 in at most 1, and DF7 and DF8 hold. FAIL otherwise.
- **Gate A** with fewer than 5 valid reps in an arm: UNSETTLED when the control meets P11 in 2. FAIL when each arm has at least 2 valid reps and the changed arm misses P11 or P8 in 2. UNSETTLED, for too few valid reps, otherwise (plan:171).
- **Gate F** with 3 valid reps in each packet and arm: PASS when no changed readme rep keeps a row on `hooks/README.md:89`, no changed readme or precision rep has more than 2 UNSUPPORTED rows, and the changed arm names a covered file in at least 2 precision reps. FAIL otherwise. The precision counts show for both arms.
- **Gate F** with fewer valid reps: UNSETTLED.

Before `unblind`, only `$K/arms/`, `$K/plan.json`, `$K/homes/`, `$K/fixtures/` and the verifier transcripts under `$K/results/` name or show an arm. Do not read them.
