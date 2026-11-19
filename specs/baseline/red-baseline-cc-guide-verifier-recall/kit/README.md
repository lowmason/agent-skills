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
5. Gate F: `build.py batch <name> readme 3` and `build.py batch <name> precision 3`, then `run.py <name>` for each batch.
6. Gate A, first wave: `build.py batch <name> audit 2`, then `run.py <name>`, then `grade.py stop <name>` (Task 7). Second wave, if the stop rules say continue: `build.py batch <name> audit 3`, then `run.py <name>`.
7. For each void rep: `build.py spare <rid>`, then `run.py <batch of that rep>`.

`build.py` prints each new rep id and its batch. `run.py` skips a rep that already has `$K/results/<rid>/`, so you can run a batch again after a spare joins it.

## build.py

- `batch <name> <packet> <pairs>` adds `<pairs>` (control, changed) pairs of one packet. Each pair's two arms take a random order from `secrets.randbelow` (DF15). A batch name is used once.
- `spare <rid>` adds one rep with the packet and arm of void rep `<rid>`, and appends it to that rep's batch file. A packet and arm get at most 2 spares. The refusal of a third names no arm.
- `probe` adds the probe rep to `$K/batches/probe.txt`. `pilot` adds the pilot to `$K/batches/pilot.txt`.

Rep ids run `r001`, `r002` and on, across every command, and are never reused. `$K/plan.json` holds `{"reps": [...]}`. Each rep has `rid`, `batch`, `packet` (`audit`, `readme`, `precision` or `probe`), `arm`, `role` (`counted`, `spare`, `probe` or `pilot`) and, for a spare, `replaces`. `$K/batches/<name>.txt` lists rep ids only, one on each line, in run order.

Exit 0 on success, 1 on a refusal, 2 on a usage error.

## run.py

`run.py <batch>` runs the reps of `$K/batches/<batch>.txt` in order. It skips each rep that already has a results folder. For every other rep, it does these steps:

1. It refuses (exit 3) while `R` holds anything.
2. It refuses (exit 4) when the held binary's sha256 differs from the one in `$K/binary.txt`.
3. It holds the rep and every later rep of the batch (exit 5) when the spend so far plus the rep's cap exceeds the ceiling. The spend counts each rep that has a results folder, at its `total_cost_usd`, or at its cap when it left no result. At equality the rep runs.
4. It builds the rep folder (below). A missing arm file, packet copy, docs copy or `probe.txt` refuses (exit 2) and leaves `R` empty.
5. It runs `command(rid)` in `R/<rid>/work/` with the prompt on stdin, and stops it at the rep's timeout.
6. It moves the session's files from `$HOME/.claude/projects/` to `$K/results/<rid>/project/<slug>/`. It finds them by the first init record's `session_id`.
7. It writes `result.json`, the stream's last `result` record.
8. It strips `credential_expires_at` from every `.json` and `.jsonl` file under `$K/results/<rid>/`. If the string is still in any file there, the rep is void (V6).
9. It writes `status.json` and moves `R/<rid>/` to `$K/homes/<rid>/`.

Steps 6 to 9 run even when the rep fails or times out.

The rep folder holds the arm's file as `.claude/agents/cc-guide-verifier.md` and the packet copy as `packet/`, without `report.md` or `settled.json`. An audit rep also gets the docs copy as `docs/`, and its `index.json` `docs` and `quotes.docs` name `R/<rid>/work/docs`. The probe rep gets the control arm's file, the kit's `vr-probe.md` as `.claude/agents/vr-probe.md` and the docs copy, but no packet.

The prompt is `common.MAIN`, which holds the dispatch of the cc-guide skill's step 1 for the rep's packet. The probe's prompt is the kit's `probe.txt`, with `{canary}` replaced by the absolute path of `$K/canary.txt`.

`command(rid)` gives this argv: `<held binary> -p --permission-mode auto --settings <SETTINGS> --max-budget-usd <cap> --output-format stream-json --verbose`. It has no `--model` (PC10) and no `--setting-sources`. The environment is built from scratch and holds only `HOME`, `USER`, `LOGNAME`, `SHELL`, `LANG`, `PATH`, `TMPDIR`, `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` and `DISABLE_AUTOUPDATER` (PC11).

| Packet kind | Cap (`--max-budget-usd`) | Timeout |
|---|---|---|
| audit | $10 | 60 minutes |
| files (readme, precision) | $4 | 20 minutes |
| probe | $1 | 10 minutes |

`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` is 4,200,000 (70 minutes), above the audit timeout (PC9).

## Formats of the files the owner or a later task writes

- `$K/binary.txt` (Task 8 Step 1) has three lines: `path: <absolute path of the held copy>`, `version: <its --version output>` and `sha256: <its sha256>`.
- `$K/ceiling.txt` (Task 8 Step 4) holds one number, the ceiling in USD, such as `130`.
- `$K/results/<rid>/status.json` holds `exit` (null after a timeout), `timed_out`, `seconds` and `strip_ok`. A `strip_ok` of false makes the rep void under V6.

## Blind reading

Plan 45's DF15 keeps the arm of each rep from the reader until every verdict is in. So `build.py`, `run.py` and `postprocess.py` print rep ids, statuses and costs only. A batch file names rep ids only. Only `$K/arms/`, `$K/plan.json` and `$K/homes/` name an arm. Do not read them before `grade.py unblind`.

## Tests

`uv run python build/run_suites.py cc-guide-verifier-recall-kit` runs the tests. Each test sets `HOME`, `common.R` and `common.KIT` to temporary folders and checks them before it runs a rep. The held binary is a stub `claude`, so no test reaches the real `$K`, `R` or `~/.claude/projects/`, and no test spends money.

On macOS, a Python process adds `__CF_USER_TEXT_ENCODING` to its own environment at startup. So the stub records the environment it got at exec, read through `KERN_PROCARGS2` (or `/proc/self/environ` on Linux), not `os.environ`.
