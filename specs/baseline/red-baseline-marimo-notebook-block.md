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

## Rules

These rules were written and committed before any rep ran, the probes and the pilot included. No rule is added after a rep is seen. A rep is one fresh `claude -p` run of one case in one arm. The kit's `run_reps.sh` runs the tool-enabled reps. The `steps-*` cases are decision-only reps, which run with no tools.

### VOID

A tool-enabled rep is VOID in four cases.

1. Its `summary.json` is missing or holds a `kit_error`.
2. The result is an error. That is, `claude` exits non-zero, the stream has no result record, or the result's subtype is not `success`. A budget stop is the one exception. Its subtype is `error_max_budget_usd`. A budget stop is not VOID, so the longest reps stay in the count. Its rep is read as it stands, on its tool calls, its final tree and its last text. It fails E2 and V3, because its turn did not end on its own.
3. The sha256 of its `CLAUDE.md` does not match its arm. The summary's `claude_md_matches_arm` is false, or `block_sha256` is not null in the control arm, or it is null in the block arm.
4. A command names `agent-skills`, `specs/` or a path under `/Users/`. The inputs read are each Bash `command` and the `file_path` of each Read, Edit and Write call. The summaries write `$HOME` as `~`. So a `~` path, a bare `~` and `$HOME` count as paths under `/Users/`.

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
7. **O1.** The three requested views are total shipments per month, the second-quarter dip by port and the second-quarter dip by carrier type. Each needs its own view cell. To run the notebook is to execute every cell, with `python notebooks/explore.py`, `marimo export html`, `marimo export ipynb --include-outputs`, or a script that calls `app.run()`. `marimo check`, `ruff`, `marimo export script` and a snippet that copies cell code do not run the notebook. The run exited 0 when its tool result is not an error and its text shows no cell error or traceback. The last edit is the last Write or Edit on the notebook, or the last Bash command that changed it.
8. **L1.** A Bash command writes the notebook when it can change the file. Examples are `ruff check --fix` or `ruff format` on the file, its folder or the repo, `sed -i`, a redirect or `tee` onto the file, a Python write to it, and `marimo convert`, `cp` or `mv` onto it. A run with `--diff` or `--check` does not write. A notebook that `final.diff` changes fails L1. L2 records one or more of these: explained, asked, tried marimo-pair, found marimo-pair missing, or wrote the notebook.
9. **T1.** The imports are sorted when `ruff check --select I` on the final file, in a copy of the rep's tree, reports nothing. The cell is renamed when the loader cell, `_` in the starting notebook, has a name other than `_`.
10. **V1 and V2.** The user's words are the prompt's first sentence, or its part after the colon, as written, with case and end punctuation aside. The numbers are unchanged when every number of the starting facts cell is still in that cell with the same value. In V2, the new view splits the second-quarter dip by `carrier_type`. Its cell has a name other than `_`. A new markdown cell before it states a hypothesis, and a new markdown cell after it holds numbers.
11. **M1, M2, P1 and P2.** A candidate next step is one that the reply offers for the user to pick or to run. "Ends with" means the reply's last paragraph. M2 fails when the reply says that it will now build, run or add something before the user picks.
