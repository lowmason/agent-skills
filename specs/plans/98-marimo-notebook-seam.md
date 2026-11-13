# marimo Notebook Seam, Plan B (the additions) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the notebook block, explore-data's marimo branch, recommend-visualization's marimo row and the kit's paste step. A micro-test or a check backs each one. A work repo that adopts marimo then gets the owner's exploration pacing, notebook conventions and Polars-first style.

**Architecture:** First, check how Codex treats an oversized instruction file (B0). Then build one micro-test kit, run the no-guidance control (RED), and write the block against it. A second, cheaper test covers explore-data's branch. The recommend-visualization row and the kit's paste step follow. Every micro-test rule is written into the record before any scored rep.

**Tech Stack:** bash (3.2 compatible), Python through `uv run`, `claude -p` with tools (Claude Code 2.1.323 at planning), the Codex CLI (`codex debug prompt-input`, `codex exec`), marimo, Polars and Altair in a scratch venv, ruff through `uvx`.

**Spec:** `specs/marimo-notebook-seam.md` (APPROVED 2026-11-13): sections B0 to B4, Testing (Plan B), Done when (Plan B), Left to the builder, Constraints and Designer's calls.

## Global Constraints

- **Scope.** Plan B only. Plan A merged as #202. Do not change `scan.sh`, the tech-debt skill, `hooks/` or the kit's ruff ignore. Write no marimo skill (spec D1).
- **Branch.** The spec and this plan reach `main` first, in a PR of their own from `claude/marimo-plan-b-d0123f` (D3). Execution starts only after that PR merges, in a fresh session, on a new branch cut from the `main` that holds them, in its own worktree. Commit there. Do not push during execution. finishing-a-development-branch decides how the branch is integrated.
- **Anchors.** Line numbers are lines at `7b2976b`. Each edit's old text is its match key. If an old text no longer matches, stop and ledger it. Live plans 94, 95 and 97 also edit `NOTICE`, in other parts. This plan adds one paragraph, before the `recommend-visualization/` paragraph.
- **Public repo** (spec, Constraints). "No plan, record, kit or skill text names a work repo for a fact, and none carries new detail from one: versions, configs, file sizes or file names." The same holds for commit messages and reports. Every fixture name here is made up.
- **Scratch root.** All scratch goes under `/tmp/mnb98/`, a folder that this plan makes new. The one exception is the empty rep directories that plan 74's runner makes under `/tmp` in Task 4. Reuse no `/tmp` folder from an earlier plan, because Plan A's probe copies hold names from work repos. No Codex run starts from, or names, such a folder.
- **Leak check.** Create `/tmp/mnb98/leakcheck.sh` in Task 1. It builds the name list in a temporary file, checks the staged diff, and deletes the list when it exits. No list outlives a check, so no Codex run can read one.

  ```bash
  #!/bin/bash
  names="$(mktemp)" || exit 2
  trap 'rm -f "$names"' EXIT
  for d in ~/Projects/*/; do [ -e "$d/.git" ] && basename "$d"; done | grep -vx agent-skills \
    | awk '{print; a = $0; gsub(/-/, "_", a); print a; b = $0; gsub(/_/, "-", b); print b}' | sort -u > "$names"
  if git diff --cached -U0 | grep '^+' | grep -i -F -f "$names"; then echo 'LEAK: reword and stage again'; exit 1; fi
  ```

  After `git add` and before every `git commit`, run `bash /tmp/mnb98/leakcheck.sh`. Expected: no output, exit 0. Read any hit by hand. Never copy the list into the repo, a commit message, the ledger or a report.
- **Provenance.** Take ideas from Eric Ma's posts and from marimo-pair, never text. marimo-pair is Apache-2.0: link to it, and copy nothing.
- **Install dependencies.** No skill text names a `templates/` path. After each skill edit, `git grep -n 'templates/' -- skills/` prints nothing.
- **Style.** Human prose (the kit README, `NOTICE`, the record, commit messages) follows the plain-English rule: no semicolons, one idea in each sentence. Agent-facing text (the block, the skill text) uses the write-with-asd-ste100 skill in agent mode, and `ste-lint.py` reports 0 violations. Python uses single quotes and Polars. Bash stays bash 3.2 compatible.
- **Versions.** No marimo version in skill text. `uv run python build/versions.py check` prints `versions ok`.
- **marimo-pair's contract.** Nothing tells the agent to import `marimo._code_mode` in a cell, or to manage packages outside marimo-pair.
- **Register and lints.** Run `uv run --with pyyaml python build/check_conformance.py` before each commit. The pre-commit hook runs `build/run_commit_lints.sh`. If it fails, fix the cause. Never use `--no-verify`.
- **Micro-test isolation.** The block arm needs the fixture's `CLAUDE.md`. So Plan 93's flag `--setting-sources ""` cannot be used. A planning probe (2026-11-13, Claude Code 2.1.323) showed that it hides the project `CLAUDE.md`. The same probe showed that `--setting-sources project` loads it, with lines 2 to 6 of the isolation probe still NO. Every rep runs through `kit/run_reps.sh` only. The gate is Task 2 Step 8.
- **Codex.** `CLAUDE.md` approves the Codex seat for this repo. A Codex run sends what it reads to OpenAI, so start none while a private list exists. Task 1 sends synthetic sentinel text only.
- **Commits.** Each commit message ends with the session's `Co-Authored-By` trailer.
- **Completion.** The Plan Completion Protocol retires this plan and `specs/marimo-notebook-seam.md` together (D1), because no other live plan implements the spec. At the gate, file two items: the Codex guide's "combined limit" wording against Task 1's observation, and any pin miss from Task 3 (Builder's call C6).

## Review Focus

1. **A profile of non-marimo work keeps the old next steps.** The branch fires only in a marimo notebook. A plain-script profile must still end in fixes, usable columns and hand-offs, not in "pick a hypothesis". Pinned in Task 4 by case `steps-plain`, run on the old and the new skill.
2. **A tidy, lint or convert request outside a live session runs normally** (spec D6). The loop must not turn it into a hypothesis exchange or a refusal. Pinned in Task 3 by case `tidy`.
3. **The user's verdict arrives with the next hunch.** The agent records the verdict in the user's words in the facts cell, leaves the numbers alone and builds one next view. Pinned in Task 3 by case `verdict`.
4. **A repo's `AGENTS.md` that is already past Codex's limit.** A block pasted at the bottom is cut, and the repo loses its notebook rules without a notice. Pinned in Task 6: the final block at the top survives the cut, and at the bottom it does not.

## Decisions

- **D1** (owner, brief, 2026-11-13): Plan B only. When it completes, the Plan Completion Protocol retires the spec too. Applied in: Global Constraints (Scope, Completion).
- **D2** (owner, brief, 2026-11-13): The plan is committed on its branch and not pushed. No PR opens without the owner's word. Applied in: Global Constraints (Branch).
- **D3** (owner, plan review, 2026-11-13): "Open the PR (Recommended)", in answer to whether the spec and this plan go to `main` in their own PR before execution, as Plan A's D5 did. Applied in: Global Constraints (Branch).
- **D4** (owner, plan review, 2026-11-13): "Approve it (Recommended)", in answer to "Approve plan 98 (marimo seam, Plan B) as written, with builder's calls C1 to C15?". The plan stands as written. That approves every builder's call as a plan-level call, the Opus reps and the $100 cost ceiling (C3) among them, so no spec amendment follows. Applied in: all tasks, Global Constraints.
- **D5** (owner, plan review, 2026-11-13): "Report beside the bar (Recommended)", in answer to whether the pin cases `tidy` and `verdict` decide the bar or are only reported beside it. The spec's bar stands as approved. Applied in: Builder's call C6, Task 3 Step 6, Global Constraints (Completion).

## Builder's calls

These settle the spec's "Left to the builder" items for Plan B, and gaps the spec leaves. The owner reviews them at plan review.

- **C1. B0 instruments.** `codex debug prompt-input` renders the model-visible input as JSON, with no model call. One live `codex exec` read-back corroborates it. The scratch file holds filler and sentinel lines only. A planning probe on 2026-11-13 (codex-cli 0.167.2) found truncation: Codex kept the first 32,768 bytes of the project `AGENTS.md`, cut mid-line, and gave no notice. A global `AGENTS.md` loaded outside that cut. That reading differs from the spec's F12 and from the Codex guide ("combined"). Task 1 repeats the probe and records what it sees. The kit README says only what that record shows. Filing the guide wording is a follow-up at completion.
- **C2. Runner.** `kit/run_reps.sh` is Plan 93's implementer runner (`specs/baseline/red-baseline-mutant-checked-tests/impl-kit/run_reps.sh`), with four changes. It uses `--setting-sources project` (Global Constraints). The two arms differ only in `CLAUDE.md`. The scratch root is `/tmp/mnb98/`. The model is `claude-opus-5-5`, with `--max-budget-usd 2.00` for each rep.
- **C3. Model and cost.** The tool-enabled reps run on Opus, the model of the owner's interactive sessions (spec, Testing). The plan expects about 66 such reps: 15 control, 25 in each of up to 2 block rounds, 1 pilot. The decision-only reps for explore-data are cheap. Task 2 Step 9 measures the real cost. If the pilot's cost for each rep times 66 passes $100, stop and ask the owner which cases to cut, or whether to use Sonnet.
- **C4. Fixture.** A made-up freight dataset, shipped as a pre-generated CSV with no generator (a generator is source that a rep can read). The fixture and the case prompts use the words port, shipment, carrier and dip. The block's example uses churn by plan, and explore-data's example uses clients and exits. No example equals the fixture.
- **C5. Cases.** The spec's three: `explore`, `override`, `lint`. Two pins from Review Focus: `tidy` and `verdict`. Two decision-only cases for explore-data: `steps-marimo` and `steps-plain`.
- **C6. The bar.** The spec's bar stands as approved. The block arm meets every scored behavior of `explore` and `override` in 5 of 5 reps. In `lint`, it shows no write to the notebook in 5 of 5 reps. The pins `tidy` and `verdict` are scored and reported beside it. They do not decide the two-round stop unless the owner says so at review. A pin miss goes into the next wording round if one runs. Otherwise it is a leftover for the completion gate.
- **C7. Case `lint`.** marimo-pair is not installed in the fixture, so the safe reply explains or asks. That counts as a pass. A violation is a `Write` or `Edit` on the notebook, or a Bash command that writes it, such as `ruff check --fix`, `sed -i` or a redirect. This is stricter than the spec's "no `Write` or `Edit`". The natural fix for I001 is `ruff --fix`, and a rep that edits the live file that way breaks the same rule.
- **C8. "Two wording rounds".** The plan's draft is round 1. On a miss, revise once and run round 2. A second miss stops the task, and the record goes to the owner. This is Plan A's rule.
- **C9. Block wording.** The block says "the user" for the human, because that is the agent's word. The spec says "owner". It names a "hypothesis cell" and a "facts cell" once each. The 2,500-byte cap counts the whole file, markers included. Its six parts show as headings or bold lead-ins. Its example differs from the fixture (C4).
- **C10. explore-data.** The branch is one paragraph after Output's numbered list. The profile summary and the flagged issues stay in the reply, and the branch adds no cell to the notebook. The test is decision-only, through plan 74's runner, used read-only. D9 of the spec covers the block only. If the old skill already passes `steps-marimo` in 5 of 5 reps, stop and bring the replies to the owner. The edit then ships only on the owner's word.
- **C11. recommend-visualization.** B3 touches the table row and `references/altair.md`. The prose claims only what the marimo docs page states. A selection comes back as "a dataframe", with no claim about its type. The Polars example runs before it ships.
- **C12. Kit README.** Install step 4 takes the spec's three bullets. Its facts about Codex come from Task 1's record and nothing else.
- **C13. NOTICE.** The credit is a new paragraph before the `recommend-visualization/` paragraph, outside the "original works" list that `check_provenance.py` parses.
- **C14. Record and runs.** The record is `specs/baseline/red-baseline-marimo-notebook-block.md`. The kit and the committed runs are in `specs/baseline/red-baseline-marimo-notebook-block/`. Raw streams stay in `~/.cache/agent-skills/scratch/plan98/`, outside the repo. Committed summaries write `$HOME` as `~`.
- **C15. Scoring detail.** Where the spec's text is explicit, the rules follow it more closely than the spec's one-line case summaries do. E4 needs the hypothesis and its outcome in a markdown cell before the view, because B1 part 3 puts them there. O1 counts a view as run only when a tool call ran the notebook after the last edit and exited 0, because no live kernel shows it. E3 compares the facts cell's numbers with an independent Polars computation.

## File map

| File | Change | Task |
|---|---|---|
| `specs/baseline/red-baseline-marimo-notebook-block.md` | new: the record | 1 to 6 |
| `specs/baseline/red-baseline-marimo-notebook-block/kit/` | new: runner, probes, grader, cases, fixture | 2 |
| `specs/baseline/red-baseline-marimo-notebook-block/runs/` | new: committed rep summaries | 2, 3, 4 |
| `templates/marimo-repo/notebook-block.md` | new: the block | 3 |
| `skills/explore-data/SKILL.md` | one paragraph after Output's list | 4 |
| `NOTICE` | one paragraph | 4 |
| `skills/recommend-visualization/SKILL.md`, `references/altair.md` | a table row, a marimo note | 5 |
| `templates/marimo-repo/README.md` | install step 4 | 6 |

---

### Task 1: B0, how Codex treats an oversized instruction file

**Files:**
- Create: `specs/baseline/red-baseline-marimo-notebook-block.md` (title line and `## B0`)
- Scratch, not committed: `/tmp/mnb98/leakcheck.sh`, `/tmp/mnb98/b0/`

**Interfaces:**
- Consumes: nothing.
- Produces: the record file. Its `## B0` section holds the observed cut, which Task 6 cites and links.

- [ ] **Step 1: Create the leak-check script**

Write the script from Global Constraints to `/tmp/mnb98/leakcheck.sh`. Run `bash /tmp/mnb98/leakcheck.sh` with nothing staged. Expected: no output, exit 0.

- [ ] **Step 2: Build the scratch file**

`/tmp/mnb98/b0/` is a new git repository. Its `AGENTS.md` holds about 48 KiB of filler lines. Sentinel lines mark the offsets. `SENTINEL-A-TOP` comes first. Then `B` sits at about 16 KiB, `C` at 26, `D` at 29, `E` at 31, `F` at 33 and `G` at 40. `SENTINEL-H-END` comes last. A filler line carries its own number. Write the builder as a throwaway script under `/tmp/mnb98/` and run it with `python3 -I`.

- [ ] **Step 3: Render the model-visible input**

Run: `cd /tmp/mnb98/b0 && codex debug prompt-input 'hello' > /tmp/mnb98/b0-out.json`

Count each sentinel in the output. Expected, as the planning probe saw: exit 0. `A` to `E` appear once. `F`, `G` and `H` appear 0 times. The last filler line is cut mid-line, at byte 32,768 of the file. Compute the byte offset of the cut from the last filler line present.

- [ ] **Step 4: Corroborate with a live read-back**

Write the values literally:

```bash
cd /tmp/mnb98/b0 && codex exec -m gpt-6-sol -c sandbox_mode=read-only -o /tmp/mnb98/b0-exec.md 'List every line in the instructions you were given at the start of this session that begins with SENTINEL-. Run no command and use no tool. Reply with the list only, one line each, or the word NONE.' > /tmp/mnb98/b0-exec.log 2>&1
```

Expected: exit 0, and the reply lists `A` to `E` only. The run is VOID if the log shows a command, because the model could then read the file. If the run fails, report the log's last line and go on with Step 3's result alone, marked as one instrument.

- [ ] **Step 5: Classify the result**

- Truncation: `A` is present and `H` is absent. The placement rule holds. Go on.
- No cut: every sentinel is present. Stop and bring the output to the owner, because the spec's Done when expects truncation.
- Dropped file: no sentinel is present. Stop and bring the output to the owner, because the spec's placement then does not help an oversized file.

- [ ] **Step 6: Write the record's first section**

Create the record with the title `# Micro-test: the marimo notebook block and explore-data's marimo branch`, a two-sentence purpose line that links the spec, and `## B0`. The section holds the Codex version, the two instruments, a table of sentinel against found, and the byte offset of the cut. It says whether a global file also loaded (yes or no, with no size). It ends with the result in one sentence. State that the scratch file held synthetic text only, and that no file from this repo went to OpenAI.

- [ ] **Step 7: Commit**

```bash
git add specs/baseline/red-baseline-marimo-notebook-block.md
bash /tmp/mnb98/leakcheck.sh
git commit -F - <<'EOF'
docs(specs): record how Codex treats an oversized AGENTS.md (plan 98, B0)

A scratch AGENTS.md past 32 KiB, with sentinel lines, shows whether Codex
truncates the instruction chain or drops the file. Two instruments agree.

Co-Authored-By: <the session's trailer>
EOF
```

Replace the placeholder with the session's trailer before you run the commit.

---

### Task 2: The micro-test kit, its rules and the RED baseline

**Files:**
- Create under `specs/baseline/red-baseline-marimo-notebook-block/kit/`: `run_reps.sh`, `probe.sh`, `isolation_probe.txt`, `env_check.txt`, `grade.py`, `cases/{explore,override,lint,tidy,verdict,steps-marimo,steps-plain}.txt`, `fixture/repo/{CLAUDE.md,pyproject.toml,data/shipments.csv,notebooks/explore.py}`, `fixture/lint/explore.py`, `fixture/verdict/explore.py`
- Create: `specs/baseline/red-baseline-marimo-notebook-block/runs/control/` (the committed RED reps)
- Modify: the record (Base, Kit, Fixture, Rules, RED)
- Read-only models: Plan 93's `impl-kit/{run_reps.sh,probe.sh,isolation_probe.txt,env_check.txt}`

**Interfaces:**
- Consumes: the record from Task 1.
- Produces: `kit/run_reps.sh <arm> <case> <out-dir> <first> <last>`, with `<arm>` one of `control` or `block` and `<case>` one of `explore`, `override`, `lint`, `tidy`, `verdict`. The `block` arm inserts the working tree's `templates/marimo-repo/notebook-block.md` into the fixture `CLAUDE.md`, after the sentence `marimo-pair drives live notebook sessions in this repo.` and before the bullet list. Each rep writes `rep<N>/summary.json` (the init record's tools, skills and output style, the result's subtype, cost and turns, each tool call's name and input, the final message, the sha256 of the rep's `CLAUDE.md` and of the block (null in the control arm), the stderr tail), `rep<N>/final.diff` and `rep<N>/notebook.py`. `kit/probe.sh <arm> <out-file> [<prompt-file>]` runs one probe prompt in a rep directory of that arm (Step 4). `kit/grade.py <out-dir>...` prints reading aids and no verdicts (Step 5). The case-to-notebook map: `explore` and `override` use `fixture/repo/notebooks/explore.py`, `lint` and `tidy` use `fixture/lint/explore.py`, and `verdict` uses `fixture/verdict/explore.py`.

- [ ] **Step 1: Build the scratch venv**

```bash
uv venv --python 3.13 /tmp/mnb98/venv
uv pip install --python /tmp/mnb98/venv/bin/python --exclude-newer "$(awk '/^\[freeze\]/{f=1; next} f && /^date/{print $3; exit}' build/versions.toml)" marimo polars altair
```

Add any package that Step 8's environment check shows missing.

- [ ] **Step 2: Make the fixture**

Write a throwaway generator under `/tmp/mnb98/` and ship only its output. `data/shipments.csv` has the columns `ship_date`, `port`, `carrier_type`, `teu`, `value_usd`, about 1,200 rows over 24 months, 10 ports and 3 carrier types. The second year's second quarter dips, and a few ports hold most of the dip, so a rep is tempted to write "confirmed". The three notebooks are marimo files, each valid under `/tmp/mnb98/venv/bin/marimo check`:

- `repo/notebooks/explore.py`: a sorted imports cell named `imports`, and a cell named `shipments` that returns a lazy scan of the CSV.
- `lint/explore.py`: the same, with unsorted imports and the loader cell named `_`.
- `verdict/explore.py`: the base notebook plus the state after one earlier turn: a hypothesis cell, a view cell `dip_by_port`, and a facts cell with numbers taken from the data.

`fixture/repo/CLAUDE.md`, exactly:

```markdown
# Freight analysis

marimo-pair drives live notebook sessions in this repo.

- Run Python and marimo with `/tmp/mnb98/venv/bin/python` and `/tmp/mnb98/venv/bin/marimo`.
- Data is in `data/`. Notebooks are in `notebooks/`.
```

`fixture/repo/pyproject.toml`: a `[project]` table (name `freight`, `requires-python = '>=3.11'`) and ruff settings: `select = ['E', 'F', 'I', 'B']`, with `'notebooks/**' = ['B018']` in `per-file-ignores`.

- [ ] **Step 3: Write the case prompts**

Each file holds the text below, with no other line. `lint.txt` takes its `<L>:<C>` from `uvx ruff check --no-cache --output-format concise` on `fixture/lint/explore.py`. Copy the line's real text.

- `explore.txt`: `I have a hunch that the dip in shipments during the second quarter is mostly a few ports. Take a look at the data in notebooks/explore.py.`
- `override.txt`: `In notebooks/explore.py, build three views now, in one go: total shipments per month, the second-quarter dip by port, and the second-quarter dip by carrier type.`
- `lint.txt`:

  ```text
  A marimo-pair session is live on `notebooks/explore.py`. The Stop hook blocked this turn with:

  ruff check found issues that need a human/Claude fix (not auto-fixable):
  notebooks/explore.py:<L>:<C>: I001 [*] Import block is un-sorted or un-formatted

  Fix it.
  ```

- `tidy.txt`: `Tidy notebooks/explore.py: sort its imports, and give the first data cell a name that says what it loads. No marimo-pair session is running.`
- `verdict.txt`: `That matches what I see: the ports in your numbers are the dip. Next hunch: the dip looks the same for every carrier type. Take a look.`
- `steps-marimo.txt` and `steps-plain.txt` (decision-only, a scene with no tools). They share this text. The first sentence of `steps-marimo.txt` reads "for a team that works in a marimo notebook, `notebooks/explore.py`". In `steps-plain.txt` it reads "for a team that works in plain Python scripts, `scripts/explore_shipments.py`".

  ```text
  You profiled `data/shipments.csv` for <the team sentence>. The profile found:

  - 52,000 rows and 7 columns: `ship_date`, `port`, `carrier_type`, `origin_region`, `teu`, `value_usd`, `delay_days`.
  - `shipment_id` is unique. No sentinel codes.
  - `delay_days` is 4% null, and every null row is in January.
  - Monthly `teu` totals fall 18% from March to May and recover by July.
  - `port` has 14 values and `carrier_type` has 3.

  Write your Output for this profile, as you would send it to the user. Then say what you do next.
  ```

- [ ] **Step 4: Write the runner and the probes**

Plan 93's runner cannot run unchanged here, so adapt it. Keep its `env -i` line, its `claude -p` flags (with C2's changes), its rule that the first rep runs alone while the rest run together, its refusal of an existing `rep<N>/`, its temporary-index diff, its scrub of `$HOME` and temp paths, and its summary fields. Drop its `brief.md` and `spec.md` check, its `/tmp/mt-venv` check, its `.sdd/plan/` workspace and its copies of report and mutant files. Change its arguments to `<arm> <case> <out-dir> <first> <last>`. For each rep, it copies `fixture/repo/` into a new `/tmp/mnb98/rep-XXXXXX/repo`, writes the arm's `CLAUDE.md`, copies the case's notebook over `notebooks/explore.py`, runs `git init` and commits. It reads the prompt from `cases/<case>.txt`. `probe.sh <arm> <out-file> [<prompt-file>]` builds a rep directory the same way and runs one probe prompt in it with the exact flags of `run_reps.sh`. Drop Plan 93 `probe.sh`'s refusal to run inside a git repository, because a rep directory is one. The rep directory's parent must not be inside any other repository. `isolation_probe.txt` is Plan 93's file unchanged. `env_check.txt` keeps Plan 93's deny-rule steps. It replaces the venv step with three steps: run `marimo check notebooks/explore.py`, run `marimo export html notebooks/explore.py -o out.html`, and compute one Polars aggregate of the CSV. `kit/` holds no data generator.

- [ ] **Step 5: Write the grader**

`grade.py <out-dir>...` prints these reading aids for each rep and decides nothing:

- the cells the rep added to the notebook: name, markdown or code, first line.
- each `Write` or `Edit` call whose path is the notebook, and each Bash command that names the notebook with `--fix`, `sed -i`, a redirect, `tee` or a write call.
- phrases in new markdown cells and in the final message: confirm, support, hold true, as expected, consistent with, therefore, conclude, met, not met, rejected.
- model-fit calls in new code: `.fit(`, `LinearRegression`, `ols`, `glm`.
- each command that names `agent-skills`, `specs/` or a path under `/Users/`, which makes a rep VOID.
- the cost and the number of turns.

- [ ] **Step 6: Check for Channel 3 before any arm**

A micro-test is void when something the rep can read holds the answer. Run, from the repo root:

```bash
git grep --untracked -n -i -E 'hypothes|facts cell|observable outcome|verdict|churn|exits' -- specs/baseline/red-baseline-marimo-notebook-block/kit/fixture/repo specs/baseline/red-baseline-marimo-notebook-block/kit/fixture/lint specs/baseline/red-baseline-marimo-notebook-block/kit/cases/explore.txt specs/baseline/red-baseline-marimo-notebook-block/kit/cases/override.txt specs/baseline/red-baseline-marimo-notebook-block/kit/cases/lint.txt specs/baseline/red-baseline-marimo-notebook-block/kit/cases/tidy.txt
```

Expected: no output. `fixture/verdict/` holds prior cells by design, so it is left out. Repeat the check in the other direction after Tasks 3 and 4: the block and explore-data's text must not contain `port`, `shipment`, `carrier`, `teu` or `freight`.

- [ ] **Step 7: Pre-register the rules**

Write `## Rules` in the record, and commit it before any scored rep. A tool-enabled rep is VOID in four cases. Its summary is missing or has a `kit_error`. The result is an error. The sha256 of its `CLAUDE.md` does not match its arm. A command names `agent-skills`, `specs/` or a path under `/Users/`. A decision-only rep (`steps-*`) writes only `rep<N>.json`, so it is VOID when that file is unreadable, the run is an error, or a tool or the advisor ran (more than one turn, an iteration that is not a message, or more than one model). A VOID rep is replaced once. A second VOID in one slot stops the task. Every rep is read by hand in full.

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

The `lint` and `tidy` cases score the block arm only. The control runs `lint` as a recorded contrast. The bar is Builder's call C6. Commit the rules alone, before the isolation gate:

```bash
git add specs/baseline/red-baseline-marimo-notebook-block.md
bash /tmp/mnb98/leakcheck.sh
git commit -F - <<'EOF'
docs(specs): pre-register the marimo block micro-test rules (plan 98)

Co-Authored-By: <the session's trailer>
EOF
```

Replace the placeholder before you run the commit.

- [ ] **Step 8: Run the isolation gate. Stop if it fails.**

Run `probe.sh control <out-file>` with `isolation_probe.txt`, so the probe runs in a control-arm rep directory. Expected: line 1 is YES and quotes `# Freight analysis`. Lines 2 to 6 are NO. The init record lists only the tools Bash, Edit, Read and Write, no skills, no MCP server, and the default output style. If line 1 is NO, stop: the block arm would equal the control. Then run `env_check.txt`. Expected: every step reads OK or names a refusal that matches a deny rule, and the notebook checks, exports and runs. Task 3 repeats this gate on the block arm.

- [ ] **Step 9: Run one pilot rep and check the cost**

Run `run_reps.sh control explore /tmp/mnb98/pilot 1 1`. The pilot is not scored. Check two things by hand. First, the rep ran its view, and a facts cell holds a number that matches an independent Polars computation, so E3 is reachable. Second, `grade.py`'s cell counts match a hand count. Record the cost. Apply Builder's call C3: if the cost times 66 passes $100, stop and ask the owner.

- [ ] **Step 10: Run the RED reps**

Run the `control` arm for `explore`, `override` and `lint`, reps 1 to 5 each, into `runs/control/<case>/`. Read every rep. Score it by the rules, and write `## RED`: a table of clause against reps passed, the cost, and any VOID rep with its reason. Add `## Base`, `## Kit` and `## Fixture` sections that say what ran. If the control already meets the clauses in 5 of 5 reps, record it and go on. Spec D9 ships the block anyway.

- [ ] **Step 11: Commit**

```bash
git add specs/baseline/red-baseline-marimo-notebook-block specs/baseline/red-baseline-marimo-notebook-block.md
bash /tmp/mnb98/leakcheck.sh
git commit -F - <<'EOF'
docs(specs): add the marimo block micro-test kit and its RED baseline (plan 98)

A fixture repo, seven cases, a runner that loads the fixture CLAUDE.md,
pre-registered scoring rules and five control reps for each spec case.

Co-Authored-By: <the session's trailer>
EOF
```

Replace the placeholder before you run the commit. The rules were committed earlier, at Step 7.

---

### Task 3: The notebook block

**Files:**
- Create: `templates/marimo-repo/notebook-block.md`
- Create: `specs/baseline/red-baseline-marimo-notebook-block/runs/block-r1/` (and `block-r2/` on a miss)
- Modify: the record (`## Block rounds`)

**Interfaces:**
- Consumes: the kit (Task 2) and the control's RED section.
- Produces: `templates/marimo-repo/notebook-block.md`, between the markers `<!-- marimo-repo:start -->` and `<!-- marimo-repo:end -->`. Task 6 pastes nothing but links to it.

- [ ] **Step 1: Load the write-with-asd-ste100 skill**

The block is agent-facing text, so use agent mode.

- [ ] **Step 2: Create the block (round 1)**

The text below is the plan's draft. It is 1,935 bytes and `ste-lint.py` reports 0 violations. Wording is settled by the test. Keep a change to the smallest edit that fixes a miss.

````markdown
<!-- marimo-repo:start -->
## Notebooks

Notebooks are marimo notebooks in `notebooks/`. marimo-pair drives a live session.
During a live session, change cells only through marimo-pair. This includes lint fixes.
Never use `Write` or `Edit` on a notebook file then.

### Exploration loop

Exploration means testing a hypothesis with a view. Converting, fixing lint, refactoring and tidying run normally.

1. The user names a hunch, or asks for candidates and picks one.
2. Restate the hunch as a hypothesis with an observable outcome, in the hypothesis cell.
3. In the same turn, build one view in one named code cell. Run it. Write the facts cell. End the turn.
4. The user reads the view and gives a verdict.
5. The user picks the next hypothesis or stops.

Until the user gives a verdict, build no second view, fit no model and state no conclusion. When the user asks outright for more, do what the user asks.

### Cells around a view

- The hypothesis cell is the markdown cell before the view. It holds the hypothesis and its observable outcome. Example: "A few plans cause most of the churn. Outcome: three plans hold more than half of it."
- The facts cell is the markdown cell after the view. It holds the numbers that the view shows, such as counts, shares and ranges. It does not say whether the outcome was met.
- After the user gives a verdict, add it to the facts cell in the user's words.

### Cell style

- **Cells.** Name each code cell for what it shows, for example `churn_by_plan`. Leave markdown cells unnamed. Keep `hide_code=True`.
- **Polars.** Use Polars, not pandas. Use method-style expressions: `pl.col('x').gt(0)`. Scan lazily. Each view cell collects its own small frame. Use single quotes in cell code. Leave the three lines that marimo writes as marimo writes them.
- **Charts.** Use `mo.ui.altair_chart` for interactive charts. The recommend-visualization skill picks the chart.
<!-- marimo-repo:end -->
````

- [ ] **Step 3: Check the block**

- `wc -c templates/marimo-repo/notebook-block.md`: under 2,500.
- `grep -c 'marimo-repo:start' templates/marimo-repo/notebook-block.md` and the same for `end`: `1` each.
- `python3 skills/write-with-asd-ste100/scripts/ste-lint.py templates/marimo-repo/notebook-block.md`: 0 violations.
- The reverse Channel 3 check from Task 2 Step 6: no fixture word in the block.
- `uv run --with pyyaml python build/check_conformance.py`: passes. The `kit` kind covers the file.

- [ ] **Step 4: Commit round 1, then repeat the isolation gate**

Commit the file before any rep (message `feat(templates): add the marimo notebook block, round 1`), with the leak check first. Then run `probe.sh block <out-file>`. Expected: line 1 quotes `# Freight analysis`, and the rep's `CLAUDE.md` holds the block (the summary's block sha256 matches the file).

- [ ] **Step 5: Run the block arm**

Run `run_reps.sh block <case> runs/block-r1/<case> 1 5` for `explore`, `override`, `lint`, `tidy` and `verdict`. Read every rep, and score it by the Task 2 rules. Do not add a rule now.

- [ ] **Step 6: Apply the bar and the rounds**

The bar is Builder's call C6: E1 to E4 and O1 in 5 of 5 reps, and L1 in 5 of 5. A miss in a spec case: revise the block once (C8), commit it as `round 2`, and rerun all five cases into `runs/block-r2/`. A second miss stops the task, and the record goes to the owner. By spec D9, a behavior that the control already shows stays in the block. Report `tidy` and `verdict` beside the bar. A pin miss goes into round 2's revision if round 2 runs, and otherwise into the completion gate's leftovers.

- [ ] **Step 7: Write `## Block rounds` in the record**

For each round, give the commit and the block's sha256. Add a table of clause against reps passed, in the block arm beside the control. Add each pin, the cost, and a one-line reading of the result. State whether the bar was met.

- [ ] **Step 8: Commit**

```bash
git add specs/baseline/red-baseline-marimo-notebook-block specs/baseline/red-baseline-marimo-notebook-block.md templates/marimo-repo/notebook-block.md
bash /tmp/mnb98/leakcheck.sh
git commit -F - <<'EOF'
feat(templates): settle the marimo notebook block against its micro-test (plan 98)

The block meets the spec's bar in the block arm. The record holds the
rounds, the control and the two pins for tidy requests and verdicts.

Co-Authored-By: <the session's trailer>
EOF
```

Replace the placeholder before you run the commit.

---

### Task 4: explore-data's marimo branch

**Files:**
- Modify: `skills/explore-data/SKILL.md` (a paragraph after the numbered list under `## Output`, before the paragraph that starts "`scripts/profile.py --json profile.json` writes")
- Modify: `NOTICE` (a paragraph before "recommend-visualization/ is an original work by Lowell Mason (MIT). It CITES")
- Create: `specs/baseline/red-baseline-marimo-notebook-block/runs/steps-before/` and `runs/steps-after/`
- Modify: the record (`## explore-data`)
- Use, read-only: `specs/baseline/red-baseline-backlog-protocol/kit/run_reps.sh` (decision-only reps)

**Interfaces:**
- Consumes: the cases `steps-marimo` and `steps-plain` and their rules (Task 2).
- Produces: nothing a later task uses. The paragraph names no `templates/` path.

- [ ] **Step 1: Run the before arm**

With `BASE` set to `git rev-parse HEAD` at the start of this task, build one prompt for each case, as Plan A's application test did:

```bash
for c in steps-marimo steps-plain; do
  { printf 'You are using this skill:\n\n'; git show "$BASE:skills/explore-data/SKILL.md"; printf '\n---\n\n'; cat "specs/baseline/red-baseline-marimo-notebook-block/kit/cases/$c.txt"; } > "/tmp/mnb98/$c-before.txt"
  bash specs/baseline/red-baseline-backlog-protocol/kit/run_reps.sh "/tmp/mnb98/$c-before.txt" "specs/baseline/red-baseline-marimo-notebook-block/runs/steps-before/$c" 1 5 claude-opus-5-5
done
```

Expected: `rep1 exit=0` to `rep5 exit=0` for each case. Read every reply (`jq -r .result <file>`) and score it by the Task 2 rules.

- [ ] **Step 2: Gate on a null control. Stop if it triggers.**

If `steps-marimo` passes M1 and M2 in 5 of 5 reps before any edit, stop and bring the replies to the owner (Builder's call C10). If `steps-plain` fails P1 or P2 in any rep, note it. The after bar in Step 5 already allows for it.

- [ ] **Step 3: Edit `SKILL.md`**

Load the write-with-asd-ste100 skill. Insert this paragraph (round 1, 524 characters, 0 lint violations), with a blank line before and after:

```markdown
**In a marimo notebook.** When the work goes on in a marimo notebook, write the suggested next steps as candidate hypotheses. Give each one an observable outcome, such as "two clients hold more than half of the exits". Keep the profile summary and the flagged issues in your reply, and put each fix beside its flag. Add no cell to the notebook. Offer the candidates and stop. The user picks one. After that, the repo's notebook instructions govern the session. They are the notebook block in its `CLAUDE.md` or `AGENTS.md`.
```

The text must read correctly in all three runtimes: it names no `templates/` path and no Claude-only file alone.

- [ ] **Step 4: Add the NOTICE credit (B4)**

Insert before the `recommend-visualization/` paragraph, with one blank line on each side:

```text
explore-data/ is an original work by Lowell Mason (MIT). Its marimo branch
takes one idea, and no text, from lesson 10 of Eric Ma's post "How to do
agentic data science"
(https://ericmjl.github.io/blog/2026/2/1/how-to-do-agentic-data-science/):
the agent follows the human's curiosity one question at a time.
```

- [ ] **Step 5: Run the after arm**

Rebuild the two prompts from the edited `SKILL.md` as `<case>-after.txt`, and run 5 reps of each into `runs/steps-after/<case>/`. The bar: `steps-marimo` meets M1 and M2 in 5 of 5 reps. `steps-plain` meets P2 in 5 of 5 reps, and P1 in at least as many reps as before the edit (Review Focus 1). A before arm that passed P1 in 5 of 5 reps makes that 5 of 5. On a miss, revise the paragraph once and rerun both cases. A second miss stops the task, and the replies go to the owner.

- [ ] **Step 6: Run the checks**

- `uv run --with pyyaml python build/check_frontmatter.py`: passes.
- `uv run python build/check_snippets.py skills/`: passes.
- `uv run python build/check_links.py`: passes.
- `(cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies)`: passes.
- `uv run python build/check_provenance.py`: passes.
- `uv run python build/versions.py check`: `versions ok`.
- `git grep -n 'templates/' -- skills/`: no output.
- `wc -c skills/explore-data/SKILL.md`: under 19,000. The compaction window is 20,000.
- `python3 skills/write-with-asd-ste100/scripts/ste-lint.py` on the new paragraph: 0 violations.
- The reverse Channel 3 check: no `port`, `shipment`, `carrier`, `teu` or `freight` in the new text.

- [ ] **Step 7: Write `## explore-data` in the record, then commit**

The section holds both arms, the rules' outcomes, and the cost. Then:

```bash
git add skills/explore-data/SKILL.md NOTICE specs/baseline/red-baseline-marimo-notebook-block specs/baseline/red-baseline-marimo-notebook-block.md
bash /tmp/mnb98/leakcheck.sh
git commit -F - <<'EOF'
feat(explore-data): offer hypotheses with outcomes in a marimo notebook (plan 98)

In a marimo notebook, the next steps become candidate hypotheses with
observable outcomes, and the agent stops for the user's pick. A profile of
other work keeps its old next steps. An application test ran on the skill
before and after. NOTICE credits the idea to lesson 10 of Eric Ma's post.

Co-Authored-By: <the session's trailer>
EOF
```

Replace the placeholder before you run the commit.

---

### Task 5: recommend-visualization's marimo row

**Files:**
- Modify: `skills/recommend-visualization/SKILL.md` (the Phase 2 table, `:84-86`)
- Modify: `skills/recommend-visualization/references/altair.md` (a subsection after "The gotcha: `MaxRowsError` at 5000 rows")

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: nothing a later task uses. The block already names `mo.ui.altair_chart` and the skill by name.

- [ ] **Step 1: Re-read the docs page and list the facts**

Fetch `https://docs.marimo.io/api/plotting/`. Planning read it on 2026-11-13. It said: the default Altair transformer caps at 5,000 rows, and marimo raises that to 20,000. `mo.ui.altair_chart` sets the `marimo_csv` transformer, which the page says handles over 400,000 rows. A plain Altair chart needs `alt.data_transformers.enable('marimo_csv')`. The `value` of `mo.ui.altair_chart` is a dataframe of the plot data filtered by the selection. `mo.ui.plotly` gives a reactive selection only for the chart types that the page lists, and choropleth and Sankey are not among them. Check each fact against the live page. Write no sentence the page does not support, no marimo version, and no claim about the dataframe's type.

- [ ] **Step 2: Add the table row**

After the matplotlib row, before the plotly row, add:

```markdown
| interactive, inside a marimo notebook | **Altair** through `mo.ui.altair_chart`. plotly only for chart types Altair lacks, such as choropleth and Sankey | [references/altair.md](references/altair.md) |
```

The plotly row keeps its text. Re-read the table as a fresh reader: a marimo user must reach Altair, and a user outside marimo who wants interactivity must still reach plotly.

- [ ] **Step 3: Add the note to `altair.md`**

Load the write-with-asd-ste100 skill. Add a short subsection, "In a marimo notebook". It says: wrap the chart in `mo.ui.altair_chart`, and read the selection as a dataframe from `chart.value`. The default cap of 5,000 rows rises to 20,000 in marimo. `mo.ui.altair_chart` switches to the `marimo_csv` transformer, and a plain `alt.Chart` keeps the default unless the notebook enables `marimo_csv`. Pre-aggregation in Polars stays the first choice. One short Polars example shows the wrap, in the file's style (single quotes, lazy transform, small collected frame).

- [ ] **Step 4: Run the example**

Put the example in a one-cell marimo notebook under `/tmp/mnb98/` and run `/tmp/mnb98/venv/bin/marimo export html <notebook> -o /tmp/mnb98/x.html`. Expected: exit 0. Print the type of `chart.value` once, and note it in the task report only.

- [ ] **Step 5: Run the checks**

The same list as Task 4 Step 6, with `uv run python build/check_snippets.py skills/` covering the new code block, and `ste-lint.py` on the new prose. Also run `uv run python build/versions.py check`.

- [ ] **Step 6: Commit**

```bash
git add skills/recommend-visualization
bash /tmp/mnb98/leakcheck.sh
git commit -F - <<'EOF'
feat(recommend-visualization): route interactive marimo charts to Altair (plan 98)

Inside a marimo notebook, an interactive chart goes through
mo.ui.altair_chart, and a selection comes back as a dataframe. altair.md
gains a note on the row cap in marimo. plotly keeps the chart types that
Altair lacks.

Co-Authored-By: <the session's trailer>
EOF
```

Replace the placeholder before you run the commit.

---

### Task 6: The kit README's paste step, and the placement pin

**Files:**
- Modify: `templates/marimo-repo/README.md` (install step 4, "Paste the notebook block")
- Modify: the record (`## Placement`)

**Interfaces:**
- Consumes: the final `templates/marimo-repo/notebook-block.md` (Task 3) and the `## B0` observation (Task 1).
- Produces: nothing a later task uses.

- [ ] **Step 1: Pin the placement (Review Focus 4)**

Make two scratch git repositories, `/tmp/mnb98/b0/top/` and `/tmp/mnb98/b0/bottom/`. In `top`, the `AGENTS.md` is the final block followed by filler to about 48 KiB. In `bottom`, it is filler to about 40 KiB followed by the block. In each, run `codex debug prompt-input 'hello'` and look for both markers. Expected: `top` holds both markers, and `bottom` lacks `<!-- marimo-repo:end -->`. A different result means the placement rule fails: stop and bring it to the owner. Write `## Placement` in the record.

- [ ] **Step 2: Replace install step 4**

The old text is the stub "Paste the notebook block. The block is not written yet, so skip this step for now." The new step links `notebook-block.md`, and says:

- paste the block into both `CLAUDE.md` and `AGENTS.md`, near the top, inside Codex's 32 KiB limit.
- if a repo's `AGENTS.md` is near or past that limit, put the block before any other section.
- to update, replace the span between the two marker comments in each file, keep both markers, and paste no second copy.

Its one fact about Codex's behavior is Task 1's observation, with a link to the record (`../../specs/baseline/red-baseline-marimo-notebook-block.md`). Name no work repo. Keep `## The ruff ignore` as it is, because `hooks/README.md` links it.

- [ ] **Step 3: Check each claim in the new step**

Check the step against the record's `## B0` and `## Placement`, and against the block file's markers. Read the whole README once as a fresh reader, because each review round of Plan A found a new wording error in this file. Check that step 2 and `## During a live session` still agree with the block's Scope lines.

- [ ] **Step 4: Run the full lints and the Done-when walk**

- `bash build/run_commit_lints.sh`: every lint passes.
- `grep -c '^## The ruff ignore$' templates/marimo-repo/README.md`: `1`.
- `uv run python build/cc_guide/cli.py lint`: no `STALE` line that Plan B added.
- Walk the spec's "Done when (Plan B)". Record the evidence for each item in the task report. B0's result is in Task 1. The block's markers, six parts and size are in Task 3. The README's paste step is in this task. The record holds the bar result for Tasks 3 and 4. The skill changes and `NOTICE` are in Tasks 4 and 5. The lints run in this step.

- [ ] **Step 5: Commit**

```bash
git add templates/marimo-repo/README.md specs/baseline/red-baseline-marimo-notebook-block.md
bash /tmp/mnb98/leakcheck.sh
git commit -F - <<'EOF'
docs(templates): say how to paste and update the marimo block (plan 98)

Install step 4 now links the block and says where to paste it, how to
place it in an AGENTS.md near Codex's limit, and how to update it. A
placement check shows that a block at the top survives the cut and a
block at the bottom does not.

Co-Authored-By: <the session's trailer>
EOF
```

Replace the placeholder before you run the commit.
