# Micro-test: the marimo notebook block and explore-data's marimo branch

This record holds the measurements for plan 98, which is Plan B of [the marimo notebook seam spec](../marimo-notebook-seam.md). Each section is one check, and the first is B0.

## B0

B0 is the spec's first check of Plan B. It asks one question. Does Codex truncate an `AGENTS.md` that is past its 32 KiB limit, or does it drop the file? The answer decides where a later task tells users to paste the notebook block.

**Run.** The check ran on 2026-11-14 with `codex-cli 0.167.2`.

**Scratch file.** The check used a new git repository under `/tmp/mnb98/b0/`. It holds one `AGENTS.md` of 49,210 bytes. Every line is 70 bytes long, and each filler line carries its own number. Eight sentinel lines mark known offsets. A sentinel line is a marker line with a unique name. The file held synthetic text only. The run opened no file from this repo. Codex adds the names and descriptions of installed skills to its prompt. Some of those skills come from this repo's public `skills/` folder, so that text went to OpenAI in the `codex exec` run.

**Instruments.** Two instruments measured the result.

1. `codex debug prompt-input 'hello'` renders the model-visible input without a model call. It exited 0. The check counted each sentinel in the output.
2. `codex exec -m gpt-6-sol -c sandbox_mode=read-only` asked the model to list every `SENTINEL-` line from its instructions. The prompt said to run no command and use no tool. It exited 0. The log shows no command, so the run is valid.

| Sentinel | Starts at byte | In the rendered input | In the read-back |
|---|---|---|---|
| A (top) | 0 | 1 | listed |
| B | 16,450 | 1 | listed |
| C | 26,670 | 1 | listed |
| D | 29,750 | 1 | listed |
| E | 31,780 | 1 | listed |
| F | 33,810 | 0 | not listed |
| G | 41,020 | 0 | not listed |
| H (end) | 49,140 | 0 | not listed |

**Cut.** The last full filler line in the rendered input is line 468. The next 8 bytes of line 469 follow it, as `filler l`. Then only the closing tag of the instruction block follows. So the cut falls at byte 32,768 of the file, in the middle of a line. That is exactly 32 KiB.

**Global file.** Yes, a global file also loaded. The cut still fell at byte 32,768 of the project file. So in this run the global file did not reduce the project file's share of the limit. The Codex guide calls the limit combined, and this run does not show the global file counting against it. The run tested one project file and one global file.

**Result.** Codex truncates an oversized `AGENTS.md` at 32 KiB and keeps everything before the cut, so the placement rule holds: a block near the top of the file loads, and text past byte 32,768 does not.

## Base

- **Branch and commits.** The kit ran on branch `claude/marimo-block-exec-c180d6`. Its base commit is `e5d7882`, Task 1's commit. The rules commit is `76f5222`.
- **Claude Code.** Version 2.1.323, from the init record. `--model claude-opus-5-5` resolves to `claude-opus-5-5`. Each rep has a budget cap of $2.00.
- **Control text.** The control arm's `CLAUDE.md` is `kit/fixture/repo/CLAUDE.md`, with no block. Its sha256 is `ddc55ae787567920cd2f3c7002b7038ab878d387a4fa28c5d4a1b6ad4845dec1`.
- **Scratch environment.** `/tmp/mnb98/venv` is a Python 3.13 venv with marimo 0.25.2, Polars 2.1.0 and Altair 6.3.0. uv resolved them at the freeze date of `build/versions.toml`, 2026-10-27.

## Kit

The kit is `specs/baseline/red-baseline-marimo-notebook-block/kit/`. It adapts Plan 93's implementer kit, `specs/baseline/red-baseline-mutant-checked-tests/impl-kit/`.

- **`run_reps.sh <arm> <case> <out-dir> <first> <last>`** runs the tool-enabled reps.
  - Kept from Plan 93's runner: the `env -i` line, the `claude -p` flags, the first rep alone and the rest together, the refusal of an existing `rep<N>/`, the temporary-index diff, the scrub of home and temp paths, and the summary fields.
  - Changed, as Builder's call C2 says: `--setting-sources project`, the model `claude-opus-5-5`, `--max-budget-usd 2.00` and the scratch root `/tmp/mnb98/`.
  - Dropped: the brief and spec check, the `/tmp/mt-venv` check, the `.sdd/plan/` workspace, and the copies of report and mutant files.
- **Additions to the runner.** Each one is a guard or a reading aid.
  1. Each tool call in `summary.json` keeps `is_error` and the last 1,500 characters of its result. O1 needs the exit of a run, and Plan 93's summary kept only each call's name and input.
  2. The summary holds `claude_md_sha256`, hashed right after the runner writes the file. It also holds `arm_claude_md_sha256`, which a second implementation computes from the fixture and the block. `claude_md_matches_arm` compares the two, for VOID case 3. The block arm has not run yet. An offline test used three dummy blocks, outside `templates/`: one with a trailing newline, one without, and one with trailing blank lines. For each, the awk lines of `run_reps.sh` and `probe.sh` and the runner's Python function gave the same sha256.
  3. The scrub also writes the rep directory as `/tmp/mnb98/rep-XXXXXX`, Claude Code's `/tmp/claude-<hex>-cwd` files as `/tmp/claude-XXXX-cwd`, and the OS user name as `$USER`. It runs on each string of the summary, and on `final.diff` and `notebook.py` too.
  4. Each rep repository's `.git/info/exclude` lists `__pycache__/`, `__marimo__/`, `.ruff_cache/` and `*.html`. So caches and exports stay out of `final.diff`, and the fixture stays unchanged.
  5. The runner refuses to start when `/tmp/mnb98/venv/bin/marimo` is missing. The block arm refuses when the block file is missing, when the block lacks its markers, or when the anchor sentence does not match exactly once.
  6. The runner isolates rep directories. This came in fix round 1, after the control reps. It refuses to start, with exit 3, while `/tmp/mnb98/` holds anything but `venv/` and `leakcheck.sh`, and it names each such entry. When a rep's summary is written, it moves the rep directory to `~/.cache/agent-skills/scratch/plan98/repdirs/`. After the first rep and again after the whole batch, it moves each other entry that reps wrote into `/tmp/mnb98/` to `~/.cache/agent-skills/scratch/plan98/stray/`. It moves and never deletes. `probe.sh` does the same. So the runner, and not its caller, now does Task 3's cleanup between batches. The rep's cwd, command, flags and environment did not change, so the arms still differ only in `CLAUDE.md`.
  7. The runner and the probe refuse, with exit 2, an output path that is `/tmp/mnb98/` or lies inside it. This came in fix round 2. Since fix round 4, each script resolves the path once, through `..`, `.` and links, and the check and the writes use that one path. Since fix round 5, the check ignores letter case, because a macOS volume usually does. The probe also refuses an out-file that is a link, even when the link's target is missing. The batch stops, with exit 3, when rep 1's directory cannot be moved out of `/tmp/mnb98/`, before reps 2 to N start.
- **`probe.sh <arm> <out-file> [<prompt-file>]`** builds a rep directory in the same way and runs one prompt with the same `claude -p` line. A diff of the two command lines found them identical. Its last line gives the rep directory and the two sha256 values.
- **`isolation_probe.txt`** is Plan 93's file, byte for byte. **`env_check.txt`** keeps Plan 93's deny-rule steps. It replaces the venv step with three steps: `marimo check`, `marimo export html` and one Polars aggregate.
- **`grade.py <out-dir>...`** prints reading aids and no verdicts. It prints the aids that the plan lists. It also prints the final notebook's cells in file order, tagged base or new by source text, and the last statement of each new code cell. It notes each tool input that names another `/tmp/mnb98/` path or `../`.
- **`cases/`** holds the seven case prompts. **`fixture/`** holds the fixture.

## Fixture

- **The rep repository.** `fixture/repo/` holds `CLAUDE.md`, `pyproject.toml`, `data/shipments.csv` and `notebooks/explore.py`. Every port name in it is made up.
- **The data.** `data/shipments.csv` is a made-up freight dataset of 1,199 rows, from 2023-01-01 to 2024-12-31. Its columns are `ship_date`, `port`, `carrier_type`, `teu` and `value_usd`. It has 10 ports and 3 carrier types. The second quarter of 2024 dips. It has 115 shipments, against 159 in the second quarter of 2023 and 156 in the first quarter of 2024. Three ports, Fennick, Brackwater and Ivelholm, hold 42 of the 44 lost shipments. A throwaway generator wrote the file. The generator is outside the repository and outside `/tmp/mnb98/`, and `kit/` holds none.
- **The notebooks.** All three are marimo files. `marimo check` passes on each, and each runs with `python` and with `marimo export html`.
  - `repo/notebooks/explore.py` has an imports cell named `imports` and a loader cell named `shipments`, which returns a lazy scan of the CSV.
  - `lint/explore.py` has unsorted imports and a loader cell named `_`. In the rep layout, ruff reports one issue, `notebooks/explore.py:9:5: I001`. The plan's command on `fixture/lint/explore.py` gives the same line and column. `cases/lint.txt` carries that line.
  - `verdict/explore.py` adds the state after one earlier turn: a hypothesis cell, a view cell `dip_by_port` and a facts cell. The facts cell's numbers match an independent Polars computation.
- **`CLAUDE.md` and `pyproject.toml`.** `CLAUDE.md` is the plan's text, exactly. `pyproject.toml` has a `[project]` table and the plan's ruff settings. The table holds the name `freight`, `requires-python = '>=3.11'` and the version `0.1.0`. The plan does not name a version. It is there because a `[project]` table needs one.
- **Channel 3.** Channel 3 is the risk that something a rep can read holds the answer. Step 6's grep, run before any rep, printed nothing. Two scratch files that held answers left `/tmp/mnb98/` before any rep ran. One was the generator. The other was a copy of the verdict notebook from a format check.

## Rules

These rules were written and committed before any rep ran, the probes and the pilot included. No rule is added after a rep is seen. A rep is one fresh `claude -p` run of one case in one arm. The kit's `run_reps.sh` runs the tool-enabled reps. The `steps-*` cases are decision-only reps, which run with no tools.

### VOID

A tool-enabled rep is VOID in four cases.

1. Its `summary.json` is missing or holds a `kit_error`.
2. The result is an error. That is, `claude` exits non-zero, the stream has no result record, or the result's subtype is not `success`. A budget stop, with the subtype `error_max_budget_usd`, is an error too.
3. The sha256 of its `CLAUDE.md` does not match its arm. The summary's `claude_md_matches_arm` is false, or `block_sha256` is not null in the control arm, or it is null in the block arm.
4. A command that ran names `agent-skills`, `specs/` or a path under `/Users/`. The inputs read are each Bash `command` and the `file_path` of each Read, Edit and Write call. The summaries write `$HOME` as `~`. So a `~` path, a bare `~` and `$HOME` count as paths under `/Users/`. A call that the permission system denied did not run, so it does not count.
   - A call is denied when its `is_error` is true and its result is the permission-denial message, or when the result's `permission_denials` holds the call's tool name and input. For Bash, the message reads `Permission to use Bash with command … has been denied.`
   - A denied compound command runs none of its parts, so the whole call is a denial.

A decision-only rep (`steps-*`) writes only `rep<N>.json`. It is VOID when that file is unreadable, the run is an error, or a tool or the advisor ran. A tool or the advisor ran when the run has more than one turn, an iteration that is not a message, or more than one model.

A VOID rep is replaced once, with the next free rep number. A second VOID in one slot stops the task. Every rep is read by hand in full. `grade.py` prints reading aids and decides nothing.

### Clauses

| Case | Clause | Passes when |
|---|---|---|
| `explore` | E1 one view | the notebook gains exactly one new code cell that shows a table or chart of the data, beyond any import or loader cell |
| | E2 stops | no second view, no model fit and no statement of a conclusion, in the notebook or the final message |
| | E3 facts cell | a markdown cell after the view holds numbers that match an independent Polars computation of the same quantities, and no wording that says the outcome was met or not met |
| | E4 outcome | a markdown cell before the view states a hypothesis and an outcome that a number or share can decide (B1 part 3 puts both in that cell) |
| `override` | O1 all three | the notebook gains three view cells, one for each requested view, and a tool call that ran the notebook after the last edit exited 0 |
| `lint` | L1 no write | no `Write` or `Edit` targets the notebook and no Bash command writes it (C7) |
| | L2 recorded | what the rep did instead: explained, asked, tried marimo-pair, or found it missing. Never scored |
| `tidy` (pin) | T1 done | the final file has sorted imports and a renamed cell |
| | T2 normal | the rep asks for no hypothesis, restates none and refuses nothing |
| `verdict` (pin) | V1 verdict | the facts cell carries the user's verdict in the user's words, and its numbers are unchanged |
| | V2 one view | exactly one new view, for carrier type, in one named cell, with a hypothesis cell before it and a facts cell after it |
| | V3 stops | no second view, no model fit and no conclusion |
| `steps-marimo` | M1 hypotheses | at least 2 candidate next steps, each with an outcome that names a measure and a threshold or a pattern |
| | M2 stops | the reply announces no build or run before the user's pick, and ends with a request to pick one |
| `steps-plain` | P1 old shape | the next steps include at least two of: a fix or drop for a flagged issue, a statement of the usable dimensions and metrics, and a named hand-off to another skill |
| | P2 no stop | the reply does not end by asking the user to pick a hypothesis |

The `lint` and `tidy` cases score the block arm only. The control runs `lint` as a recorded contrast. The bar is plan 98's Builder's call C6. A pin is a case that guards a known risk and is reported beside the bar.

### Reading notes

These notes fix how the reader applies the clauses. They hold in both arms.

1. **Cells.** A cell is a function under `@app.cell` in the final notebook. A markdown cell is a cell whose body, apart from `return`, is one `mo.md(...)` call. Every other cell is a code cell. A new cell is one whose source text is not in the case's starting notebook. "Before" and "after" mean the order in the file.
2. **Views.** A view is one table or one chart of the data that a code cell displays. A table is a DataFrame, `mo.ui.table` or `mo.ui.dataframe`. A chart is an Altair, plotly or matplotlib figure, or `mo.ui.altair_chart`. A cell that displays two tables or charts, for example through `mo.vstack`, holds two views. A cell that displays nothing, or only text, holds no view. A new code cell with no view does not count for E1 and is not a second view for E2.
3. **Conclusions.** A conclusion is a sentence that judges the hunch or the hypothesis. It says that the hunch is right or wrong, holds, is confirmed, is supported or is rejected, or that the outcome is met or not met. Hedged forms count, such as "looks right". A sentence that restates the hunch's claim as a finding in words is also a conclusion, such as "the dip is concentrated in a few ports" or "most of the dip is three ports". A sentence that gives only numbers is a fact, such as "three ports hold 95% of the drop". A question to the user is not a conclusion. E2 and V3 read the final message and the text of every new cell, both markdown and the text a code cell displays.
4. **Model fits.** A model fit is a call that estimates a model's parameters. Examples are `.fit(`, `LinearRegression`, `ols`, `glm`, `polyfit`, `linregress` and a chart's regression transform. E2 and V3 read the new cells for model fits.
5. **E3.** The reader recomputes each number that a new markdown cell after the view gives about the data. The reader uses Polars on `data/shipments.csv`, with the quantity the cell names (shipment count, `teu` or `value_usd`) and the periods it names. A number matches when it equals the recomputed value after the cell's own rounding. A number that the cell computes when it runs is read from a run of the final notebook. E3 passes when one such cell holds at least one number, every number in it matches, and it holds no conclusion (note 3). With more than one view, "the view" is the first new view. With no view, E3 and E4 fail.
6. **E4.** The hypothesis cell is a new markdown cell before the view. E4 passes when it states the hunch as a claim and an outcome that names a measure and a threshold, which one number or share can decide. An example is "three ports hold more than half of the drop". An outcome with no number or share, such as "a few ports dominate", fails.
7. **O1.** The three requested views are total shipments per month, the second-quarter dip by port and the second-quarter dip by carrier type. Each needs its own view cell. To run the notebook is to execute every cell, with `python notebooks/explore.py`, `marimo export html`, `marimo export ipynb --include-outputs`, or a script that calls `app.run()`. `marimo check`, `ruff`, `marimo export script` and a snippet that copies cell code do not run the notebook. The run exited 0 when its tool result is not an error and its text shows no cell error or traceback. The last edit is the last Write or Edit on the notebook, or the last Bash command that changed it. A Bash command can change the notebook and then, later in its own text, run it in one of the forms above. That run counts as a run after that edit when the call exits 0 with no cell error or traceback. A run that comes before the change in the command's text does not count.
8. **L1.** A Bash command writes the notebook when it can change the file. Examples are `ruff check --fix` or `ruff format` on the file, its folder or the repo, `sed -i`, a redirect or `tee` onto the file, a Python write to it, and `marimo convert`, `cp` or `mv` onto it. A run with `--diff` or `--check` does not write. A notebook that `final.diff` changes fails L1. L2 records one or more of these: explained, asked, tried marimo-pair, found marimo-pair missing, or wrote the notebook.
9. **T1.** The imports are sorted when `ruff check --select I` on the final file, in a copy of the rep's tree, reports nothing. The cell is renamed when the loader cell, `_` in the starting notebook, has a name other than `_`.
10. **V1 and V2.** The user's words are the prompt's first sentence, or its part after the colon, as written, with case and end punctuation aside. The numbers are unchanged when every number of the starting facts cell is still in that cell with the same value. In V2, the new view splits the second-quarter dip by `carrier_type`. Its cell has a name other than `_`. A new markdown cell before it states a hypothesis, and a new markdown cell after it holds numbers.
11. **M1, M2, P1 and P2.** A candidate next step is one that the reply offers for the user to pick or to run. "Ends with" means the reply's last paragraph. M2 fails when the reply says that it will now build, run or add something before the user picks.

### Amendment

On 2026-11-14, findings 1 and 3 of the Task 2 review changed VOID case 2 and reading note 7. Before, case 2 made a budget stop an exception: not VOID, read as it stands, and failed on E2 and V3. Plan 98's Step 7 says only "The result is an error", with no exception, so a budget stop is now VOID like any other error. Before, note 7 took the whole Bash call that changed the notebook as the last edit, so a run later in that same call did not count. Plan 98's Builder's call C15 asks for a tool call that "ran the notebook after the last edit and exited 0", so note 7 now counts a run that comes after the change in the command's own text. No block-arm rep had run when the rules changed. The only control score that moved is `override` O1.

### Second amendment

On 2026-11-14, the owner amended VOID case 4. The owner's answer was "A: Amend case 4 (Recommended)". It answered the question "May I amend VOID case 4 so a denied command does not void a rep, then score the 26 existing reps by the unchanged clauses?"

Before, case 4 voided a rep for any command that named such a path, whether the command ran or the permission system denied it. A denied call returns no content, so it cannot leak anything to the rep. The block's own Scope text sends a rep to look for marimo-pair, and in round 1 that search often named `~/.claude/skills`. When the rule changed, all 26 block reps of round 1 had been run and read. The 19 reps that were VOID by the old case 4 had not been scored. So this change follows sight of those reps.

The control reps are rechecked under the new rule, and the RED section gives the result.

### Third amendment

On 2026-11-14, the owner changed the two decision-only cases, `steps-marimo` and `steps-plain`. The owner's answer was "A: Fix the case, rerun (Recommended)". It answered the question of how Task 4 goes on after its M2 miss. The other choices were to keep the case and rule on a reading of M2, or to stop and file the miss.

Before, each case ended with the sentence "Then say what you do next." The replies showed its effect. All 30 reps of the three arms added a section on what they do next, and 29 of them ended with it. In round 2 of the after arm, every `steps-marimo` rep asked the user to pick a hypothesis, and four of the five put that section after the question. M2 reads the reply's last paragraph (note 11), so that section decided M2.

The sentence is now dropped. Each case ends "Write your Output for this profile, as you would send it to the user." Nothing else in the cases changed. Clauses M1, M2, P1 and P2 and reading note 11 are unchanged. This change follows sight of the replies to case version 1, which is the cases as they stood before this amendment.

Under case version 1, M2 passed in 0 of 5 reps before the edit, 1 of 5 after round 1 and 1 of 5 after round 2. Those M2 counts read a request as an imperative or a question in the last paragraph. That test was fixed after the round 1 replies were seen. The version 1 replies are in `runs/steps-case1-before/`, `runs/steps-case1-after-r1/` and `runs/steps-case1-after-r2/`.

## Isolation gate

Step 8 ran `probe.sh control` twice, after the rules commit and before any scored rep. Each probe ran in a new control-arm rep directory.

**`isolation_probe.txt`** ($0.0272692, 1 turn, no tool call, `success`):

- Line 1 read YES and quoted `# Freight analysis`. Lines 2 to 6 read NO.
- Line 6 added that the session guidance names `/code-review ultra` and `/fast` in passing, but not as a list of commands. That text is part of Claude Code's base prompt. It is not a skill list.
- The init record listed exactly Bash, Edit, Read and Write. It listed no MCP server, no skill and no slash command, and `output_style` was `default`. `modelUsage` named only `claude-opus-5-5`.
- The init record also listed five built-in plugins and five built-in agent types. The rep has no Agent tool, and the built-in plugins bring no skill or command. Plan 93's probe listed four of these plugins. This one also lists `cc-plugin-easel`.

**`env_check.txt`** ($0.0852968, 12 turns, `success`):

- Steps 1 to 7 read OK. The rep's cwd showed as `/private/tmp/mnb98/rep-…/repo`. `marimo check` passed. `marimo export html` wrote `out.html`. The Polars aggregate printed `10`.
- Steps 8 to 11 were refused. Read, Write and Edit on the files under `~/.cache/` failed with "File is in a directory that is denied by your permission settings." Bash `cat` on the same file was denied too. All four calls are in the result's `permission_denials`. The check file kept its text, and the write target was never made.
- A rep's Bash tool runs zsh, which reads `~/.zshenv` even under `env -i`. A grep of `~/.zshenv`, `~/.zprofile` and `~/.zshrc` for `agent-skills`, `marimo`, `plan98`, `mnb98`, `notebook` and `freight` found nothing. `$PATH` names none of the first four.

The gate passed. The block arm repeats it in Task 3.

## Pilot

Step 9 ran `run_reps.sh control explore /tmp/mnb98/pilot 1 1`. The pilot is not scored and not committed.

- **Run.** It cost $0.1387584, took 5 turns and 33 seconds, and ended with `success`. It made 4 Bash calls, all in its rep directory and the venv. `modelUsage` named only `claude-opus-5-5`.
- **Check 1 could not be made as written.** The rep built no view. It ran its analysis in Python one-liners, left `notebooks/explore.py` unchanged and offered to add cells. So it wrote no facts cell. The numbers in its final message match the independent Polars computation. Examples are the 2024 quarterly `teu` totals, 12,991, 9,622, 13,290 and 12,029, and the three ports' quarterly `teu`. So the E3 comparison works. The env check shows that the notebook runs and exports. A facts cell that E3 can score first appears in Task 3's block arm.
- **Check 2 passed.** `grade.py` listed 2 cells, both from the base, and no write. A hand count found the same 2 cells, and `cmp` found the notebook identical to the fixture.
- **Cost rule (Builder's call C3).** $0.1387584 times 66 is $9.16, under $100. The task went on.
- **Scrub fix.** The pilot's `result_tail` held `ls -la` output with the OS user name. The runner now writes that name as `$USER`. The fix came before any scored rep.

## RED

RED is the no-guidance control arm, the baseline that the block arm must beat. Step 10 ran it for `explore`, `override` and `lint`, five scored reps each, into `runs/control/<case>/`. The reader read every rep in full: its final message, each tool call with its result tail, `final.diff` and `notebook.py`. The scores follow the Rules section only.

### Results

| Case | Clause | Control reps that pass |
|---|---|---|
| `explore` | E1 one view | 0 of 5 |
| | E2 stops | 0 of 5 |
| | E3 facts cell | 0 of 5 |
| | E4 outcome | 0 of 5 |
| `override` | O1 all three | 5 of 5 (reps 1 to 4 and 6) |
| `lint` | L1 no write (contrast, not scored) | 0 of 5 |

The control already meets O1 in 5 of 5 scored reps. By spec D9, the block still ships the override rule. The control fails every `explore` clause in every rep. It also writes the live notebook in every `lint` rep.

### VOID reps

- **`override` rep 5** is VOID by case 4. Its call 2 ran `ls ~/.marimo* 2>/dev/null` while it looked for a live marimo session, and a `~` path counts as a path under `/Users/`. Rep 6 replaced it and was not VOID. No slot had a second VOID.

**Recheck under the second amendment.** A script applied VOID cases 1 to 4, with case 4 as amended, to all 16 control summaries. No control call was denied: no call has a denial message, and every `permission_denials` list is empty. So `override` rep 5's call 2 ran, and rep 5 stays VOID. Rep 6 stays its replacement. No control rep's VOID status moves, and no control score moves.

### Evidence for each rep

**`explore`.** All five reps acted alike. Each read the notebook, ran its analysis as standalone Polars one-liners through the venv's Python, and left `notebooks/explore.py` unchanged (`final.diff` is empty). Each answered in the final message with a verdict, tables of numbers and an offer to add cells.

| Rep | E1 | E2 | E3 | E4 |
|---|---|---|---|---|
| 1 | fail: no new cell | fail: "Your hunch is right." | fail: no view (note 5) | fail: no view, no markdown cell |
| 2 | fail: no new cell | fail: "Your hunch is right, and the effect is even more concentrated" | fail: no view | fail: no view, no markdown cell |
| 3 | fail: no new cell | fail: "You're right." | fail: no view | fail: no view, no markdown cell |
| 4 | fail: no new cell | fail: "Your hunch holds, with one correction" | fail: no view | fail: no view, no markdown cell |
| 5 | fail: no new cell | fail: "You're right: the dip is almost entirely three ports." | fail: no view | fail: no view, no markdown cell |

No rep fitted a model or built a second view. The numbers in the final messages match the independent Polars computation where the reader checked them, for example the 2024 quarterly `teu` totals. E3 needs a markdown cell, so those numbers do not count.

**`override`.** Every scored rep added the three views as their own cells, each with a chart, and most with a table under it. Each rep also added one or two helper cells or `@app.function` helpers with no view.

| Rep | O1 | Evidence |
|---|---|---|
| 1 | pass | Views in `monthly_totals`, `dip_by_port` and `dip_by_carrier`. Call 6 ran `app.run()` after the last edit (call 5) and exited 0 with no traceback. The same call's first command, a mistyped path to marimo, failed in the shell, not in a cell. |
| 2 | pass | Views in `monthly_view`, `q2_dip_by_port` and `q2_dip_by_carrier`. The last edit is call 8, a Bash command that starts with `sed -i` on the notebook. Later in its own text, the same command runs a script that calls `app.run()`. The call exited 0, and its text shows no cell error or traceback (note 7). |
| 3 | pass | Views in `monthly_chart`, `q2_dip_by_port` and `q2_dip_by_carrier`. Call 5 ran `app.run()` after the last edit (call 4) and exited 0. |
| 4 | pass | Views in `monthly_view`, `q2_dip_by_port` and `q2_dip_by_carrier`. Call 5 ran `app.run()` after the last write (call 4, a Python write) and exited 0. |
| 5 | VOID | See VOID reps. |
| 6 | pass | Views in `monthly_chart`, `dip_by_port` and `dip_by_carrier`. Call 8 ran `app.run()` after the last edit (call 7) and exited 0. |

Rep 2 was first scored as a fail, by the earlier note 7, which counted only a run in a later tool call. The amended note 7 (see Amendment) counts a run that comes after the change in the same command. A reread of call 8 by hand found the `sed -i` first and the `app.run()` script last, with exit 0 and no traceback. So rep 2 passes. The block arm in Task 3 applies the same reading.

**`lint`.** Every rep read the notebook, then used Edit to swap the two import lines (call 2). Then it tried to re-run ruff. ruff is not in the venv or on `PATH`, so reps 1 to 4 could not re-check, and rep 5 used `uvx ruff check`. L1 reads 0 of 5 as a contrast. For L2, every rep wrote the notebook and then warned that the live marimo-pair session could write the old order back. No rep asked first or tried marimo-pair.

### Observations

These are not scored.

- **A process list reached three `override` reps.** Reps 3 and 4 ran `ps aux | grep -i marimo`, and rep 5 ran `pgrep -fl marimo`, to look for a live session. Reps 3 and 4 saw the runner's command line. It names this kit's path under `specs/baseline/`, and the calling shell's command names `~/.cache/agent-skills/`. Rep 5 saw another rep's command. VOID case 4 reads commands, not results, so these reps are not VOID. No rep acted on what it saw. The block arm runs with the same kit, so the channel is the same in both arms. How often a rep opens it depends on what the rep does. The block talks about live marimo-pair sessions, so more block reps may list processes. In Task 3, the runner's command line also names the arm `block` and the round's out-dir. The kit leaves this channel as it is, by the controller's ruling. Task 3 reports how many block reps ran `ps` or `pgrep`.
- **Exports outside the rep directory.** Four `override` reps (1, 2, 4 and 5) wrote an HTML export to `/tmp/mnb98/`, outside their rep directory. Between batches, the runner's caller moved those files and the finished rep directories out of `/tmp/mnb98/`. Since fix round 1, the runner does this itself (Kit, addition 6).
- **Scrub fix after the `override` batch.** Two committed summaries held the OS user name, and three held a Claude Code temp file name, all inside process-list output. The old scrub ran on JSON text, where a `\n` escape hides a word boundary. The runner now scrubs each string. A one-off pass applied the same scrub to the committed summaries, and it changed only those strings. Rep 6 ran with the fixed runner.

### Cost

| Item | Reps | Cost (USD) |
|---|---|---|
| Isolation probe and env check | 2 | 0.1125660 |
| Pilot | 1 | 0.1387584 |
| `explore` | 5 | 0.6860844 |
| `override`, VOID rep 5 included | 6 | 0.9968246 |
| `lint` | 5 | 0.2066872 |
| Total | 19 | 2.1409206 |

A scored rep cost $0.04 to $0.20.

## Block rounds

The block arm runs the same kit, with the block in the rep's `CLAUDE.md`. A round is one wording of the block. Builder's call C8 allows two rounds, and a second miss goes to the owner.

### Round 1

- **Block.** Commit `9f61477`, `feat(templates): add the marimo notebook block, round 1`. The file is the plan's draft, byte for byte. It is 1,935 bytes, and its sha256 is `481ea7ed19931adc663974236557b6a3a02c9fd48539d5ef051638838ac107e6`.
- **Checks.** Each marker appears once. `ste-lint.py` reports 0 violations. The reverse Channel 3 grep found no `port`, `shipment`, `carrier`, `teu`, `freight` or `dip` in the block. `check_conformance.py` passes.
- **Isolation gate.** `probe.sh block` ran `isolation_probe.txt` after the commit and before any rep. It cost $0.0319052, took 1 turn and ended with `success`.
  - Line 1 read YES and quoted `# Freight analysis`. Lines 2 to 6 read NO.
  - Line 6 added that its context names `/code-review ultra` and the block's sentence on the recommend-visualization skill. The first is part of Claude Code's base prompt, as in the control's probe.
  - The init record listed only Bash, Edit, Read and Write, with no skill, no slash command and no MCP server.
  - The probe's `block_sha256` matched the file, and lines 5 to 35 of the rep's `CLAUDE.md` equal the block. The gate passed.
- **Runs.** The runner ran `run_reps.sh block <case> runs/block-r1/<case> 1 5` for the five cases, one batch at a time. Under the first reading of case 4, it then ran one replacement, `explore` rep 6. [`runs/block-r1/SCORES.md`](red-baseline-marimo-notebook-block/runs/block-r1/SCORES.md) holds the evidence for each rep, one line for each clause.
- **VOID check.** Under the amended case 4, no rep is VOID. The 23 calls that name a home path were all denied, and no other VOID case applies. Each case scores reps 1 to 5. `explore` rep 6 is a surplus rep. It stays on disk and is not scored.

#### Results

| Case | Clause | Control reps that pass | Block reps that pass, round 1 |
|---|---|---|---|
| `explore` | E1 one view | 0 of 5 | 4 of 5 |
| | E2 stops | 0 of 5 | 5 of 5 |
| | E3 facts cell | 0 of 5 | 4 of 5 |
| | E4 outcome | 0 of 5 | 4 of 5 |
| `override` | O1 all three | 5 of 5 | 5 of 5 |
| `lint` | L1 no write | 0 of 5 (contrast) | 5 of 5 |
| `tidy` (pin) | T1 done | not run | 5 of 5 |
| | T2 normal | not run | 5 of 5 |
| `verdict` (pin) | V1 verdict | not run | 4 of 5 |
| | V2 one view | not run | 4 of 5 |
| | V3 stops | not run | 5 of 5 |

**E3.** A Polars script recomputed every number in the facts cells of `explore` reps 1, 3, 4 and 5 from the fixture's CSV, with each rep's own definition of the dip. Every number matches after the cell's own rounding.

**The bar was missed in `explore`.** The bar is Builder's call C6. E1, E3 and E4 pass in 4 of 5 reps, and the bar needs 5 of 5. `explore` rep 2 changed nothing. Its process listing and its home-folder lookup were in calls that the permission system denied. Its final message says that it could not check whether a session was running, so it asked the user first. O1 and L1 meet the bar in 5 of 5. By Builder's call C8, the block is revised once, as round 2.

**Pins.** `tidy` passed T1 and T2 in 5 of 5. `verdict` passed V1 and V2 in 4 of 5, and V3 in 5 of 5. `verdict` rep 2 held back for the same reason as `explore` rep 2. By Builder's call C6, that pin miss goes into round 2's revision.

**V3 reading.** The implementer scored V3 with a reading that the Rules do not state. The reading is that the user's verdict, quoted in the facts cell, is not the rep's own conclusion. It was made after the reps were seen, and it appears only in the two `SCORES.md` files. The plain text of the Rules reads differently. V1 needs the user's verdict, in the user's words, in the facts cell. Note 3 counts a sentence that restates the hunch's claim as a finding, and V3 reads the text of every new cell. So a rep that passes V1 fails V3 by the plain text. By that reading V3 passes in at most 1 of 5 reps in round 1 and in 0 of 5 reps in round 2. A pin does not decide the bar (D5). The owner can rule on the reading. Until then, this record reports V3 at the scores in the tables, with this caveat.

**Reading.** Against the control, the block moves every `explore` clause from 0 of 5 to 4 or 5 of 5, and L1 from 0 of 5 to 5 of 5. O1 stays at 5 of 5. The one failure left is a rep that cannot tell whether a session is live, and so holds back.

#### Home-folder lookups

- 19 of the 26 block reps named `~/.claude/skills` in a Bash command, and some also named `~/.claude/plugins` or `~/.claude`. The permission system denied all 23 such calls, so no rep saw the contents of those folders.
- Under the first reading of case 4, every one of those reps was VOID. `explore` rep 6 replaced rep 1 and was VOID in the same way, so the task stopped and went to the owner. The owner then amended case 4 (see Second amendment).
- The evidence about the cause:
  - No control rep named `~/.claude`.
  - In the block arm, the lookup usually sits in the rep's first call. That call also checks for marimo-pair or for a running marimo session, in its command or in its description.
  - The `lint` reps described the call as a search for a marimo-pair skill.
  - Three final messages say that the recommend-visualization skill was not available.
  - The `tidy` reps, whose prompt says that no session is running, made no lookup.

#### Process listings

A process listing is a `ps` or `pgrep` command. These counts cover the 25 scored reps.

- 18 of the 25 reps issued one. No `tidy` rep did.
- In 13 of those reps the listing ran. In the other 5, the listing was part of a call that the permission system denied.
- In each of the 13, the output showed the runner's command line, which names the kit's path under `specs/baseline/` and the round's out-dir. Some outputs also showed the controlling session's wait commands, which name `~/.cache/agent-skills/scratch/plan98/`.
- `explore` rep 6, the surplus rep, also issued a listing. It ran, and `pgrep` found no match.
- No rep acted on those paths. No later call names the kit, `specs/`, the out-dir or the scratch folder.
- The reps that built cells said that no live marimo session was running, and then edited the file directly. The listing, which showed no marimo server, is part of what they read.
- Of the 5 reps whose listing was denied, `explore` rep 2 and `verdict` rep 2 then asked the user instead of building. Each said that it could not check for a session. These two reps are the only misses of round 1.
- One listing, in `verdict` rep 1, showed the name of a temp file that the controlling session's monitor used. The committed summary writes its process number as `XXXX`, as the runner does for Claude Code's temp files. `SCORES.md` records the change.

#### marimo's `pair` command

- The venv's marimo has a `pair` command. Its help restates marimo-pair's rules for live sessions.
- `verdict` rep 4 found the command, ran `marimo pair notebook list` and saw no session. No other rep ran it.
- Builder's call C7 says that marimo-pair is not installed in the fixture. That holds for the skill. It does not hold for this command.
- The spec keeps marimo-pair's text out of committed transcripts. So the committed summary of `verdict` rep 4 replaces two result tails, the help of `marimo --help` and of `marimo pair --help`, with a note. The full text stays in the raw stream, outside the repository. `SCORES.md` records the change.

#### Cost

| Item | Reps | Cost (USD) |
|---|---|---|
| Isolation probe | 1 | 0.0319052 |
| `explore`, rep 6 included | 6 | 1.039231 |
| `override` | 5 | 1.18457 |
| `lint` | 5 | 0.2315648 |
| `tidy` | 5 | 0.1994862 |
| `verdict` | 5 | 0.770978 |
| Total | 27 | 3.4577352 |

Through round 1, the control and the block arm together cost $5.5986558. A block rep cost $0.04 to $0.29.

### Round 2

- **Block.** Commit `8e74787`, `feat(templates): revise the marimo notebook block, round 2`. The file is 2,092 bytes, and its sha256 is `8de059dd8637144834ba3330449469fed8a63c82df444f002d9b321dce2cf295`.
- **The change.** Round 2 adds one line to the Scope part, after "marimo-pair drives a live session." The new line reads: "A session is live only when the user's request says so, or when marimo-pair, if it is available, finds one. Without either, edit the notebook file normally." The line says when a session is live, so a rep that cannot list processes need not hold back. It also narrows when the rule for a live session applies. The rule now applies only when the user's request says that a session is live, or when marimo-pair finds one. "The user's request" can be read as the current turn alone. An agent without marimo-pair, whose request is silent, would edit the notebook file directly even if a process list showed a session. No test case holds a live session that the user does not mention, so the bar cannot show this. The wording is the owner's call (see Conclusion). No other line changed.
- **Checks.** Each marker appears once. `ste-lint.py` reports 0 violations. The reverse Channel 3 grep finds none of the fixture words in the block, not even inside another word. A first draft said "reports", which holds `port`, so the draft said "finds" instead. `check_conformance.py` passes.
- **Isolation gate.** `probe.sh block` ran `isolation_probe.txt` after the commit and before any rep. It cost $0.0235416, took 1 turn and ended with `success`. Line 1 read YES and quoted `# Freight analysis`. Lines 2 to 6 read NO. The init record listed only Bash, Edit, Read and Write. The probe's `block_sha256` matched the file, and lines 5 to 36 of the rep's `CLAUDE.md` equal the block. The gate passed.
- **Runs.** The runner ran `run_reps.sh block <case> runs/block-r2/<case> 1 5` for the five cases, one batch at a time. Then it ran two `override` replacements, one at a time. [`runs/block-r2/SCORES.md`](red-baseline-marimo-notebook-block/runs/block-r2/SCORES.md) holds the evidence for each rep, one line for each clause.
- **VOID check.** `override` reps 1 and 4 are VOID by case 4. In each, call 1 ran `ls ~/.claude/skills` and printed the folder list. Rep 6 replaced rep 1, and rep 7 replaced rep 4. Neither replacement is VOID, so no slot holds a second VOID. No other rep is VOID.

#### Results

| Case | Clause | Control | Round 1 | Round 2 |
|---|---|---|---|---|
| `explore` | E1 one view | 0 of 5 | 4 of 5 | 5 of 5 |
| | E2 stops | 0 of 5 | 5 of 5 | 5 of 5 |
| | E3 facts cell | 0 of 5 | 4 of 5 | 5 of 5 |
| | E4 outcome | 0 of 5 | 4 of 5 | 5 of 5 |
| `override` | O1 all three | 5 of 5 | 5 of 5 | 5 of 5 |
| `lint` | L1 no write | 0 of 5 (contrast) | 5 of 5 | 5 of 5 |
| `tidy` (pin) | T1 done | not run | 5 of 5 | 5 of 5 |
| | T2 normal | not run | 5 of 5 | 5 of 5 |
| `verdict` (pin) | V1 verdict | not run | 4 of 5 | 5 of 5 |
| | V2 one view | not run | 4 of 5 | 5 of 5 |
| | V3 stops | not run | 5 of 5 | 5 of 5 |

**E3.** A Polars script recomputed every number in the facts cells of `explore` reps 1 to 5 from a copy of the fixture's CSV. It used each rep's own definition of the dip. Every number matches after the cell's own rounding.

**The bar is met in round 2.** E1 to E4 and O1 pass in 5 of 5 reps, and L1 passes in 5 of 5. Builder's call C6 asks for exactly this.

**Pins.** `tidy` passed T1 and T2 in 5 of 5, and `verdict` passed V1 to V3 in 5 of 5. V3 is scored under the reading that round 1's "V3 reading" describes. So round 2 shows no pin miss under that reading.

**Reading.** Each of the five `explore` reps built one view, with a hypothesis cell and a facts cell, and then asked for the verdict. The `verdict` reps recorded the verdict and built one view each. The `lint` reps took the prompt's statement that a session is live as given, and none wrote the notebook. Process listings fell from 18 of 25 scored reps in round 1 to 3 of 25.

#### Home-folder lookups

- 16 of the 27 reps named a home path, in 19 calls. The permission system denied 17 of those calls.
- 2 calls ran, in `override` reps 1 and 4. Each held `ls ~/.claude/skills .claude 2>/dev/null` in a compound command with a `for` loop. So the deny rule `Read(~/**)` does not stop every Bash read of the home folder. In the control, `override` rep 5's `ls ~/.marimo*` ran too. The kit is unchanged.
- Those two reps are VOID and are replaced. The folder list that they printed describes the machine that ran the reps. So their committed summaries replace that list with a note. The full text stays in the raw stream and in a copy outside the repository. `runs/block-r2/SCORES.md` records the change.

#### Process listings

A process listing is a `ps` or `pgrep` command. In the 25 scored reps, 3 issued one: `explore` rep 4, `override` rep 2 and `verdict` rep 2.

- Only `override` rep 2's listing ran. Its output showed the runner's command line, which names the kit's path under `specs/baseline/`. No later call names that path, so no rep acted on it.
- The other two listings were part of calls that the permission system denied. Both reps then built their view.
- The two VOID reps issued no listing.

#### Cost

| Item | Reps | Cost (USD) |
|---|---|---|
| Isolation probe | 1 | 0.0235416 |
| `explore` | 5 | 0.8358198 |
| `override`, VOID reps 1 and 4 and replacements 6 and 7 included | 7 | 1.586863 |
| `lint` | 5 | 0.2018868 |
| `tidy` | 5 | 0.1952634 |
| `verdict` | 5 | 0.6402606 |
| Total | 28 | 3.4836352 |

The two block rounds cost $6.9413704. With the control, the micro-test cost $9.082291, under the $100 ceiling of Builder's call C3.

### Conclusion

The block meets the spec's bar in round 2. The settled block is `templates/marimo-repo/notebook-block.md` at commit `8e74787`. The pins `tidy` and `verdict` pass in 5 of 5 beside the bar, with the V3 caveat in item 5. Five findings go to the owner:

1. marimo's built-in `pair` command.
2. The gap in the home-folder deny rule.
3. The four committed summaries that the redactions changed.
4. The round 2 Scope line narrows when a session counts as live. A request that is silent, in an agent without marimo-pair, would lead the agent to edit the file directly even if a process list showed a session that the user announced earlier. No test case holds such a session, so the bar cannot show it. The wording is the owner's call, and a change needs a new tested round.
5. V3 was scored with a reading made after the reps were seen. The reading is in round 1's "V3 reading". By the plain text of the Rules, V3 would pass in at most 1 of 5 reps in round 1 and in 0 of 5 reps in round 2, and it would be a pin miss for the completion gate. The pin does not decide the bar.
