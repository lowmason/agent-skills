# Handoff Briefs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give writing-plans an entry check, a decision home with a plan-review stage, and a premise-free model line. Close the roadmap loop between stage execution, derive-roadmap and the next stage. Add the sender skill prepare-handoff. Each piece ships only where its no-guidance baseline fails.

**Architecture:** A pre-flight runs no-guidance baselines in owner-launched `claude -p` sessions, one per rep. Each runs in a throwaway fixture repo with a kit of skill text exported from one commit. The baselines decide GO or NO-GO per component. Then come three phases of skill edits, each followed by a GREEN campaign on the same fixtures: writing-plans (C1–C3), the roadmap loop (C5) and prepare-handoff (C4). One stdlib script, `entry_check.py`, is built test-first. Everything else is skill text.

**Tech Stack:** Markdown skill text; Python 3.13 (stdlib) for `entry_check.py`, pytest for its tests; bash and Python tooling for the reps, kept outside the repo under `~/.cache/`; Claude Code 2.1.295 `claude -p`.

**Spec:** `specs/handoff-briefs.md` (DESIGN APPROVED 2026-10-04, amended 2026-10-09). Executors read both.

## Global Constraints

- **Where.**
  - Work in the worktree `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs`, on branch `feat/handoff-briefs`. Task 1 creates it with `git worktree add`, never `EnterWorktree`.
  - Every commit command starts with the branch check: `[ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit …`.
  - Run subagent-driven-development's scripts as `cd <worktree> && <script> …`. They take the repo root and HEAD from the shell's directory.
  - The controller's skills load from the main checkout (`~/.claude/skills`). So this branch's edits to writing-plans, subagent-driven-development and executing-plans never reach the executing session before the merge.
- **Executors.** Each task names one.
  - `implementer`: dispatched as usual.
  - `controller`: the controlling session does the work itself, with no dispatch.
  - `owner`: a hard stop. The controller ends its turn with the task's owner block, and resumes when the owner reports back. This is a sanctioned stop, like a context checkpoint.

  No session in this plan launches a rep: no `claude -p`, `codex` or `gemini` session, and no `run_rep.sh` or `run_batch.sh` against a real rep. Reps run only from the owner's plain terminal (spec R5.1 **Where**), and `run_rep.sh` refuses to run when `CLAUDECODE` is set. The one exception is Task 2's `dry_run.sh`, which runs the scripts under a throwaway HOME with a stub in place of `claude`.
- **Gates (spec R5.1–R5.2, R7.6).**
  - Task 6's RED record decides GO or NO-GO for C1, C2, C4a, C4b, C5a and C5b.
  - A *gated* task applies either its GO steps or its NO-GO variant, never both.
  - These ship whatever the gates decide: C3; R1.3 with the script's `plan ids:` field; R2.1; R7.5; and R7.4's §4 stance sentence.
- **Each component's commits stand alone.** Never name a skill before it exists: writing-plans and derive-roadmap name prepare-handoff only in Task 18.
- **Bare skill names (R6.4, R7.7).**
  - New cross-skill text names another skill by its bare name only.
  - Never write `<skill>'s <Capitalized words>`, `<skill>' <Capitalized words>`, `<skill>'s §…`, `<skill> references/…`, or a path into another skill's directory.
  - `install.py`'s `DEPENDENCIES` and `build/test_runtime_support.py`'s `SOFT_REFERENCES` do not change.
- **Every commit passes (R5.8).** Run these from the worktree root. The fifth includes the dependency-drift test.

  ```bash
  uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
  uv run --python 3.13 python build/check_provenance.py
  uv run --python 3.13 --with pyyaml python build/check_conformance.py
  uv run --python 3.13 python build/check_snippets.py skills/
  (cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py test_check_provenance.py)
  (cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q)
  ```
- **Test counts:** state test changes as +N deltas, never absolute totals.
- **Leave alone:**
  - `specs/claude-code-drift-automation.md`;
  - every plan-38 file (`specs/plans/completed/38-claude-code-drift-automation.md`);
  - `~/.claude/CLAUDE.md`;
  - any file a task does not list.

  Never run `install.py` (R6.6). The owner runs it after the merge.
- **Public repository.**
  - Commit nothing from `~/.cache/`: no brief, transcript, extract, score file, fixture, or either plan-38 example file.
  - The RED record carries counts and one-line paraphrased evidence, never transcript or brief text.
- **Python:** 3.13, single quotes, f-strings; stdlib only in `entry_check.py`.
- **Copy code mechanically.** Write every code block from your brief into its file by slicing the brief between the block's fence lines with a script, never by retyping it. Task 3's fixed shas and the test counts catch a slip; they do not prevent one.
- **Commit trailer:** end every commit message with the Co-Authored-By trailer your session's attribution reminder gives. Subagents use the controlling session's trailer.
- **The rep protocol** lives in `~/.cache/agent-skills/handoffs/red/PROTOCOL.md`, written by Task 4: kits, reps, audit, voids, thresholds and scoring. It binds Tasks 5, 6, 12, 16 and 19.
- **Retirement.** The RED record retires with the plan: the plan-completion protocol's `chore(specs): retire plan 40` commit also `git mv`s `specs/red-baseline-handoff-briefs-<date>.md` to `specs/completed/`. Task 21 closes it first.

## Planning record

This record is not a set of requirements. Your human partner reviews it with the plan.

**Plan ID.** Checked by hand on 2026-10-09, because the entry check does not exist yet:
- `git for-each-ref refs/heads refs/remotes` lists `refs/heads/main`, `refs/remotes/origin/main` and the symbolic `refs/remotes/origin/HEAD`. The repo's other refs, four Codex turn-diff checkpoints and the tag `archive/cc-guide-upkeep`, top out at plan 33.
- There is one worktree, with no live plan.
- On both real refs the highest id is 39 (`specs/plans/completed/39-cc-guide-hardening.md`), so 40 is free.

**Verified at planning (2026-10-09, claude 2.1.295).**

- **Probes,** each deleted afterwards:
  - `--setting-sources project,local` kept the user CLAUDE.md and every personal skill out of a `-p` session.
  - A kit passed with `--add-dir` loaded its `.claude/skills/`, and the skill's base directory was the kit path.
  - Under `env PATH=<shim>:/usr/bin:/bin:/usr/sbin:/sbin`, `command -v codex` failed and a fake `gh` answered.
  - `--permission-mode auto` ran Bash headless with no denials, where `acceptEdits` refused `echo $PATH`.
- **Docs.** The 2.1.289 docs snapshot (`permissions.md:616-624`) says an `--add-dir` directory also loads `.claude/agents/` and `.claude/commands/`. `--strict-mcp-config` was not probed; Task 5's pilot checks it.
- **Environment.** Claude Code sets `CLAUDECODE=1` in its sessions' Bash environment.
- **Gemini and Codex.**
  - Gemini 0.46.0 did not discover a workspace `.agents/skills/`.
  - `gemini skills install <path> --scope workspace --consent` installs to `<cwd>/.gemini/skills/`.
  - codex-cli 0.154.0 is installed. Its smoke run uses the repo's `.agents/skills/`.
- **`entry_check.py`.** The script and its 24 tests, exactly as Tasks 7 and 8 give them, ran in a scratch directory:
  - 12 fail with no script, and pass against Task 7's version;
  - 12 more fail against Task 7's version, and all 24 pass against Task 8's.

  On `main`, `entry_check.py specs/claude-code-drift-automation.md` lists plan 35 six times, but never its line 40. That line calls the spec only "the drift spec".
- **The edits.** Tasks 7–18's replace blocks were applied in task order to a clone of `main`, under four gate combinations: all GO, all NO-GO, and two mixed. Every old text matched exactly once, and the gate block passed after every task. The writing-plans suite gained 12 tests at Task 7 and 12 more at Task 8. After every edit, writing-plans' body stays under the 20,000-character compaction window, and subagent-driven-development stays at 500 lines or fewer.
- **Snapshots.**
  - The recipe: `git clone --no-local --single-branch`, then reset, remove origin, expire the reflog and `gc --prune=now`.
  - A clone truncated at `a3e9b75` holds 644 commits, and none of `7137e5e`, `f72822a` or `db41cc9`. Its entry check lists plan 35 seven times, and its next free id is 38.
  - `a3e9b75` is the parent of `7137e5e`, so there plan 35's precondition (audit D13 fixed before drift Stage 1 is planned) is unmet.
  - Neither snapshot holds `specs/handoff-briefs.md` or any handoff material.
  - Both carry `.claude/settings.json` (model opus, no hooks) and the root CLAUDE.md. These load as project settings in every rep of those arms.
  - Some historical specs in them name `/Users/lowell/Projects/agent-skills`. A rep that follows one is void (PROTOCOL.md, Audit).
- **Upstream.** Upstream `8ca22db`'s writing-plans puts a `**Spec:**` line after Tech Stack. Its Execution Handoff runs review, then choice: Subagent-driven or Native, with one recommended "because" a sentence drawn from the plan.
- **C4b prompt.** Its first turn is the owner's plan-38 request (the triage session of 2026-10-04, turn 4), verbatim.

**Decisions settled in this plan.** Please review each one.

1. **Rep mechanics.**
   - Each rep is an owner-launched `claude -p` session from a plain terminal, with `--setting-sources project,local --strict-mcp-config --add-dir <kit> --permission-mode auto --output-format json`.
   - Turn 1 passes `--session-id`, later turns `--resume`, and the prompt comes on stdin.
   - The working directory is the rep's own fixture repo.
   - PATH is a shim with no `codex` and a fake `gh`.
2. **Thresholds** (PROTOCOL.md).
   - **RED:** a failure observed in at least 2 of 5 valid reps means GO.
   - **GREEN positive arms:** pass when at least 4 of 5 valid reps pass every criterion.
   - **GREEN negative arms:** C5a− and C5b− pass when 0 of 5 fire; C4a− passes when at most 1 of 5 writes a brief.
   - **Pressure arms:** P1, P2, P5a and P5b pass at 4 of 5.
   - **V3:** passes at 2 of 3.
   - **C3:** each of C3-a, C3-b and C3-c is at least the control's count minus 1, and C3-d holds 5 of 5.
   - **Probe:** each planted finding is reported in at least 4 of 5 reps.
   - **B2, V1, C5a-pr, C5a-ep and C5b-part:** pass at 4 of 5.
   - **Voids:** a void rep is replaced, up to 10 dispatches per arm and phase.
3. **Go/no-go arms.** C4a's and C4b's go/no-go reads the positive arm. The negative arms are checked at GREEN, as R7.6 does for C5.
4. **Entry-check details.**
   - `since:` uses committer dates (`%cs`).
   - The status change is the newest commit whose status line differs from its first parent's.
   - A deferred mark is read within its `## ` section, and is `unmarked` when no item line precedes the hit.
   - Plan files are found recursively under `specs/plans/`.
   - A repo with no plans reports next free 1.
   - `plans for this spec` matches the stem whole, or after a hyphen.
5. **R1.2's first condition** reads "unless you can point to the commit or file that meets it". A met precondition needs no question.
6. **Sync-point timing.** CLAUDE.md's suite comment lands with the script (Task 7). Each NOTICE entry lands with its component.
7. **README Credits.** The originals line gains prepare-handoff too. R6.3 names only the table.
8. **§5's stamp location** ("under its roadmap entry") ships with R7.5, ungated.
9. **The RED record,** `specs/red-baseline-handoff-briefs-<date>.md`, collects the RED and GREEN results. It retires to `specs/completed/` with the plan.
10. **C3 scoring.** C3 is scored on the C2 sessions, or on a C3-only arm if C2 is a no-go.
11. **Snapshots.** V3 runs on a truncated clone at `a3e9b75`. C4b, V1 and the probe run on one at `7137e5e`, the plan-38 triage state.
12. **The probe brief** is `example-plan38-prompt.md` with four passages reverted to the review's DRAFT text by `plant_probe.py`. This plan quotes only short anchors from the private files.
13. **Probe prompts.** Probe reps receive the filled reviewer template as their prompt.
14. **Brief directories.**
    - After each run, `run_rep.sh` moves the rep's brief directory into its results.
    - Listing `~/.cache/agent-skills/handoffs/` voids a rep, so reps may run concurrently.
    - This replaces the sequential C4 runs considered earlier.
15. **Smoke-run install paths:** Codex reads the repo's `.agents/skills/`; Gemini uses `gemini skills install <path> --scope workspace --consent`.
16. **GREEN-only arms,** called for by the spec's micro-test rules:
    - C2b, for R2.5's brief intake;
    - B2, for R5.5;
    - P5a and P5b, for R7.6's pressures;
    - C5a-ep, for executing-plans' Step 6.
17. **Phase 0 has six tasks** with named executors, and owner steps are hard stops.
18. **C5a checkboxes.** In the C5a fixtures the plan's checkboxes stay unticked, and the ledger marks the tasks complete. That is how a real run leaves them before the completion protocol.
19. **Scoring.** A scorer subagent per arm writes TSV lines with verbatim quotes. `tally.py` rejects any quote it cannot find in the rep's extract.
20. **Audit by whitelist.**
    - A rep is void when any tool input, in its own transcript or a subagent's, names a path under a protected root outside the rep's allowed paths.
    - A failure traced to a permission denial voids the rep.
    - R4.6's `.handoff/` fallback is valid brief storage.
    - Rep paths are never reused: auto-memory is keyed by working directory.
21. **Phase 3's arms.**
    - `c4a-neg` and the probe arms (`fc`, `cr`) run whenever the skill ships.
    - `c4a-pos` needs C4a GO, and `v1` needs C4b GO.
    - `b2` needs C2 to have shipped, since R4.9's sentence then sits in the plan-review stage.
22. **R4.9 without C2.** When C2 did not ship, R4.9's writing-plans sentence goes in the Execution Handoff's opening paragraph. R4.9 names only the C2 case.
23. **NOTICE names R4.9's mention.** A one-bullet superpowers entry records that writing-plans names prepare-handoff. This is beyond R6.1's three entries.
24. **Smoke runs name the skill.** Each R5.7 prompt starts "Use prepare-handoff", so the runs test the runtime's mechanics. Task 19 tests the trigger.
25. **The freeze log sits outside the freeze.** Changes are logged in `changes.log`, not in PROTOCOL.md. A freeze id recorded inside a frozen file would change the hash it records.
26. **The README row fits every shipping variant.** It describes the sort and the review, not the recipe, so no gate changes it.

**Scale.**
- About 160 owner-launched reps:
  - 9 pilot reps;
  - at least 45 RED reps;
  - about 100 GREEN reps across Tasks 12, 16 and 19;
  - REFACTOR re-runs and void replacements on top.
- Task 5's pilot measures the cost of each arm and projects the total before the RED batch. Your human partner sets the models then, and may stop there.
- Each snapshot rep holds a 56 MB copy.

**Launching execution.** Start the executing session as a terminal `claude` whose working directory is the main checkout. Do not use an app-made worktree session, which cannot edit a second `git worktree add` worktree. Commit this plan on `main` first: Task 1 branches from it.

---

## Phase 0 — Pre-flight (spec R5.1, R5.3)

Every Phase 0 deliverable except the RED record lives outside the repo:
- the control directory `~/.cache/agent-skills/handoffs/red/` (written `$CTL` below);
- the neutral tree `~/.cache/pondworks/` (written `$PW`).

Each rep's working directory, kit and brief directory sit under neutral names. Nothing a rep is allowed to read names this work.

### Task 1: Copy the fixtures and create the worktree

**Executor:** controller. This task runs before subagent-driven-development's workspace exists. It starts that workspace from the worktree as its last step.

**Files:**
- Create (not in git): `~/.cache/agent-skills/handoffs/red/example-plan38-prompt.md`, `~/.cache/agent-skills/handoffs/red/example-plan38-review.txt`
- Create: the worktree `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs`, on branch `feat/handoff-briefs`

**Interfaces:**
- Consumes: this plan, committed on `main`.
- Produces:
  - `$CTL` holding the two example files;
  - the worktree;
  - `BASE40`, the commit the branch was cut from, which the ledger records;
  - the workspace `.sdd/40-handoff-briefs/` inside the worktree.

- [ ] **Step 1: Copy the two example files before anything else (spec R5.1, Fixtures)**

```bash
mkdir -p ~/.cache/agent-skills/handoffs/red && cp ~/.cache/agent-skills/handoff-brief/example-plan38-prompt.md ~/.cache/agent-skills/handoff-brief/example-plan38-review.txt ~/.cache/agent-skills/handoffs/red/ && cmp ~/.cache/agent-skills/handoff-brief/example-plan38-prompt.md ~/.cache/agent-skills/handoffs/red/example-plan38-prompt.md && cmp ~/.cache/agent-skills/handoff-brief/example-plan38-review.txt ~/.cache/agent-skills/handoffs/red/example-plan38-review.txt && echo copied
```

Expected: `copied`.

- [ ] **Step 2: Confirm the plan is committed on `main`**

```bash
cd /Users/lowell/Projects/agent-skills && git status --short -- specs/plans/40-handoff-briefs.md && git log -1 --format=%h -- specs/plans/40-handoff-briefs.md
```

Expected: no status line, then one short sha. If a status line prints or no sha does, stop and ask your human partner to commit the plan on `main`.

- [ ] **Step 3: Create the worktree from `main`**

```bash
cd /Users/lowell/Projects/agent-skills && git worktree add .claude/worktrees/plan-40-handoff-briefs -b feat/handoff-briefs main && git -C .claude/worktrees/plan-40-handoff-briefs rev-parse --short HEAD
```

Expected: the worktree is created and one short sha prints. That sha is `BASE40`.

- [ ] **Step 4: Run the gates on the untouched branch**

From the worktree root, run every command in the Global Constraints' **Every commit passes** block.

Expected: all pass. If one fails here, stop and report it, because a later failure must be attributable to this plan.

- [ ] **Step 5: Start the workspace from the worktree and open the ledger**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs && ~/.claude/skills/subagent-driven-development/scripts/sdd-workspace specs/plans/40-handoff-briefs.md
```

Expected: `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs/.sdd/40-handoff-briefs`.

Write the ledger `progress.md` there with these three lines:

```
Plan: specs/plans/40-handoff-briefs.md
BASE40: <sha from Step 3>
Task 1: complete (no repo commits; worktree and fixtures in place)
```

Task 1 has no repo diff, so it gets no review package.

### Task 2: Rep tooling

**Executor:** implementer. **Review:** the deliverables live outside the repo, so there is no review package. Give the task reviewer this brief, the implementer's report, and the paths below. The reviewer reads the files and re-runs Step 10. It skips Step 9, which changes file modes: a reviewer changes nothing.

**Files** (all new, none in git):
- Create: `~/.cache/pondworks/shim/` (symlinks `git`, `uv`, `python3`, `python3.13`; a stub `gh`)
- Create: `~/.cache/agent-skills/handoffs/red/tools/run_rep.sh`
- Create: `~/.cache/agent-skills/handoffs/red/tools/run_batch.sh`
- Create: `~/.cache/agent-skills/handoffs/red/tools/build_kit.sh`
- Create: `~/.cache/agent-skills/handoffs/red/tools/make_reps.py`
- Create: `~/.cache/agent-skills/handoffs/red/tools/extract.py`
- Create: `~/.cache/agent-skills/handoffs/red/tools/tally.py`
- Create: `~/.cache/agent-skills/handoffs/red/tools/test_tools.py`
- Create: `~/.cache/agent-skills/handoffs/red/tools/dry_run.sh`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces the commands later tasks call:
  - `build_kit.sh KIT COMMIT` — writes `~/.cache/pondworks/kits/KIT/.claude/{skills,agents,commands}` from one worktree commit, and appends to `$CTL/kits.tsv`.
  - `make_reps.py ARM PHASE KIT COUNT BATCH` — copies template `~/.cache/pondworks/templates/<t>/` to `~/.cache/pondworks/reps/rNNN/`, and appends to `$CTL/registry.tsv` (columns `rep arm phase template kit model_class prompts start`) and to `$CTL/batches/BATCH.txt`. Its `ARMS` table names each arm's template, model class and prompt files.
  - `run_rep.sh REP` and `run_batch.sh [-j N] BATCH` — the owner's commands. Their output goes to `$CTL/results/REP/`: `turnN.prompt.txt`, `turnN.json`, `turnN.git.txt`, `project/`, `handoffs/`.
  - `extract.py BATCH | --rep REP` — writes `results/REP/extract.md` and `results/REP/audit.json` (`valid`, `problems`, `flags`, `denials`, `cost_usd`).
  - `tally.py PHASE` — reads `$CTL/scores/PHASE/<arm>.tsv` (header `rep`, `criterion`, `verdict`, `quote`, tab-separated), and exits 1 on an unfound quote.
  - Phase names: `pilot`, `red`, `green1`, `green2`, `green3`, and `refactor<N>-<arm>`.
  - Prompt placeholders, which `run_rep.sh` fills: `@REP@` becomes the rep's directory, and `@HANDOFFS@` becomes `~/.cache/agent-skills/handoffs/<rep>`.

- [ ] **Step 1: Build the shim**

```bash
mkdir -p ~/.cache/pondworks/shim && for t in git uv python3 python3.13; do ln -sfn "$(command -v "$t")" ~/.cache/pondworks/shim/"$t"; done && ls -l ~/.cache/pondworks/shim
```

Expected: four symlinks to absolute paths. Then create `~/.cache/pondworks/shim/gh`:

```sh
#!/bin/sh
# Stand-in for the GitHub CLI in rep sessions: `gh pr create` prints a PR URL,
# and every other call succeeds silently. Each call is logged for scoring.
printf '%s\t%s\t%s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "$PWD" "$*" >> "$HOME/.cache/pondworks/gh-calls.log"
case "$1 $2" in
  'pr create') echo 'https://example.invalid/pondworks/pull/17' ;;
esac
exit 0
```

```bash
chmod +x ~/.cache/pondworks/shim/gh && ~/.cache/pondworks/shim/gh pr create --fill
```

Expected: `https://example.invalid/pondworks/pull/17`. The log `~/.cache/pondworks/gh-calls.log` gains one line. Delete that line afterwards: `: > ~/.cache/pondworks/gh-calls.log`.

- [ ] **Step 2: Write `run_rep.sh`**

```bash
#!/usr/bin/env bash
# Run one registered rep: every turn of its prompts, in its own fixture repo,
# with only its kit's skills, agents and command loaded. The owner runs this
# from a plain terminal outside Claude Code (spec R5.1, Channel 5); it refuses
# to run inside a session.
#
# Usage: run_rep.sh REP_ID
set -euo pipefail

CTL="$HOME/.cache/agent-skills/handoffs/red"
PW="$HOME/.cache/pondworks"
rep=${1:?usage: run_rep.sh REP_ID}

if [ -n "${CLAUDECODE:-}" ]; then
  echo "run_rep.sh: CLAUDECODE is set; run reps from a plain terminal outside Claude Code" >&2
  exit 2
fi
[ -f "$CTL/config.env" ] || { echo "run_rep.sh: no $CTL/config.env (Task 5 writes it)" >&2; exit 2; }
# shellcheck source=/dev/null
. "$CTL/config.env"

row=$(awk -F'\t' -v r="$rep" '$1 == r' "$CTL/registry.tsv")
[ -n "$row" ] || { echo "run_rep.sh: $rep is not in registry.tsv" >&2; exit 2; }
IFS=$'\t' read -r _ arm phase template kit mclass prompts _ <<<"$row"

repdir="$PW/reps/$rep"
out="$CTL/results/$rep"
[ -d "$repdir/.git" ] || { echo "run_rep.sh: $repdir is not a fixture repo (make_reps.py makes it)" >&2; exit 2; }
[ ! -e "$out" ] || { echo "run_rep.sh: $out exists; a rep never runs twice" >&2; exit 2; }

case $mclass in
  plan) model=$MODEL_PLAN; effort=$EFFORT_PLAN ;;
  exec) model=$MODEL_EXEC; effort=$EFFORT_EXEC ;;
  review) model=$MODEL_REVIEW; effort=$EFFORT_REVIEW ;;
  *) echo "run_rep.sh: unknown model class $mclass" >&2; exit 2 ;;
esac
[ -n "$model" ] && [ -n "$effort" ] || { echo "run_rep.sh: config.env leaves the $mclass model or effort empty" >&2; exit 2; }

claude_bin=${CLAUDE_BIN:-$(command -v claude)}
sid=$(uuidgen | tr 'A-Z' 'a-z')
mkdir -p "$out"
printf '%s\n' "$sid" > "$out/session-id"
printf 'rep=%s arm=%s phase=%s template=%s kit=%s model=%s effort=%s claude=%s\n' \
  "$rep" "$arm" "$phase" "$template" "$kit" "$model" "$effort" "$("$claude_bin" --version)" > "$out/meta.txt"

n=0
IFS=',' read -r -a turns <<<"$prompts"
for p in "${turns[@]}"; do
  n=$((n + 1))
  if [ "$n" -eq 1 ]; then sess=(--session-id "$sid"); else sess=(--resume "$sid"); fi
  sed -e "s|@REP@|$repdir|g" -e "s|@HANDOFFS@|$HOME/.cache/agent-skills/handoffs/$rep|g" \
    "$CTL/prompts/$p" > "$out/turn$n.prompt.txt"
  status=0
  ( cd "$repdir" && env PATH="$PW/shim:/usr/bin:/bin:/usr/sbin:/sbin" "$claude_bin" -p "${sess[@]}" \
      --setting-sources project,local --strict-mcp-config --add-dir "$PW/kits/$kit" \
      --model "$model" --effort "$effort" --permission-mode auto --output-format json \
      < "$out/turn$n.prompt.txt" > "$out/turn$n.json" 2> "$out/turn$n.stderr" ) || status=$?
  {
    echo "## branch"; git -C "$repdir" branch --show-current
    echo "## status"; git -C "$repdir" status --porcelain=v1 --untracked-files=all
    echo "## log"; git -C "$repdir" log --all --format='%h %cs%d %s' -15
  } > "$out/turn$n.git.txt" 2>&1
  if [ "$status" -ne 0 ]; then
    echo "turn $n exited $status; later turns not run" >> "$out/meta.txt"
    break
  fi
done

transcript=$(find "$HOME/.claude/projects" -maxdepth 2 -name "$sid.jsonl" | head -n 1)
if [ -n "$transcript" ]; then cp -R "$(dirname "$transcript")" "$out/project"; fi
if [ -d "$HOME/.cache/agent-skills/handoffs/$rep" ]; then
  mv "$HOME/.cache/agent-skills/handoffs/$rep" "$out/handoffs"
fi
echo "rep $rep ($arm, $phase): $n turn(s); results in $out"
```

- [ ] **Step 3: Write `run_batch.sh`**

```bash
#!/usr/bin/env bash
# Run the reps listed in batches/BATCH.txt, skipping any that already have
# results, so an interrupted batch resumes where it stopped. -j N runs N reps
# at a time. The owner runs this from a plain terminal outside Claude Code.
#
# Usage: run_batch.sh [-j N] BATCH
set -euo pipefail

CTL="$HOME/.cache/agent-skills/handoffs/red"
jobs=1
if [ "${1:-}" = -j ]; then jobs=${2:?usage: run_batch.sh [-j N] BATCH}; shift 2; fi
batch=${1:?usage: run_batch.sh [-j N] BATCH}
list="$CTL/batches/$batch.txt"
[ -f "$list" ] || { echo "run_batch.sh: no $list" >&2; exit 2; }

grep -v '^#' "$list" | while read -r rep; do
  [ -n "$rep" ] || continue
  if [ -e "$CTL/results/$rep" ]; then echo "skip $rep: has results" >&2; continue; fi
  printf '%s\n' "$rep"
done | xargs -n 1 -P "$jobs" "$CTL/tools/run_rep.sh"
```

- [ ] **Step 4: Write `build_kit.sh`**

```bash
#!/usr/bin/env bash
# Build a kit: the skills, agents and command a rep loads through --add-dir,
# exported from one commit of the plan-40 worktree, never from its working
# tree. A kit is built once and never changed; kits.tsv records its commit.
#
# Usage: build_kit.sh KIT COMMIT
set -euo pipefail

WT=/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs
CTL="$HOME/.cache/agent-skills/handoffs/red"
PW="$HOME/.cache/pondworks"
kit=${1:?usage: build_kit.sh KIT COMMIT}
commit=$(git -C "$WT" rev-parse --short "${2:?usage: build_kit.sh KIT COMMIT}")
dest="$PW/kits/$kit"
[ ! -e "$dest" ] || { echo "build_kit.sh: $dest exists; kits are never rebuilt" >&2; exit 2; }

skills="brainstorming writing-plans executing-plans subagent-driven-development
finishing-a-development-branch requesting-code-review receiving-code-review
using-git-worktrees verification-before-completion test-driven-development derive-roadmap"
if git -C "$WT" cat-file -e "$commit:skills/prepare-handoff/SKILL.md" 2>/dev/null; then
  skills="$skills prepare-handoff"
fi

mkdir -p "$dest/.claude"
for s in $skills; do
  git -C "$WT" archive "$commit" "skills/$s" | tar -x -C "$dest/.claude"
done
git -C "$WT" archive "$commit" agents/code-reviewer.md agents/task-reviewer.md commands/deferred.md \
  | tar -x -C "$dest/.claude"
printf '%s\t%s\t%s\n' "$kit" "$commit" "$(echo $skills)" >> "$CTL/kits.tsv"
echo "kit $kit from $commit: $(ls "$dest/.claude/skills" | wc -l | tr -d ' ') skills"
```

- [ ] **Step 5: Write `make_reps.py`**

```python
#!/usr/bin/env python3
'''Create registered reps from a fixture template, ready for run_rep.sh.

Usage: make_reps.py ARM PHASE KIT COUNT BATCH

For each new rep it copies the arm's template to ~/.cache/pondworks/reps/<rep>/,
gives the copy a bare origin with main pushed and origin/HEAD set, applies the
arm's extra, appends a row to registry.tsv and the rep id to
batches/BATCH.txt. Rep ids are never reused (auto-memory is keyed by working
directory): it refuses a rep whose directory, results, brief directory or
Claude Code project directory already exists.
'''

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
CTL = HOME / '.cache/agent-skills/handoffs/red'
PW = HOME / '.cache/pondworks'
REGISTRY = CTL / 'registry.tsv'
HEADER = 'rep\tarm\tphase\ttemplate\tkit\tmodel_class\tprompts\tstart\n'
GIT = ['git', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null']

# arm: (template, model class, prompt files in turn order, extra) — PROTOCOL.md, Arms.
# fc and cr take their single prompt from the kit's reviewer template (probe_prompt).
ARMS = {
    'c1': ('t1', 'plan', ['c1.t1.txt'], None),
    'p1': ('t1', 'plan', ['p1.t1.txt'], None),
    'c2': ('t2', 'plan', ['c2.t1.txt', 'c2.t2.txt', 'c2.t3.txt'], None),
    'c3': ('t2', 'plan', ['c2.t1.txt'], None),
    'p2': ('t2', 'plan', ['p2.t1.txt', 'p2.t2.txt', 'c2.t3.txt'], None),
    'c2b': ('t2', 'plan', ['c2b.t1.txt'], 'c2b-brief'),
    'b2': ('t2', 'plan', ['c2.t1.txt', 'b2.t2.txt', 'c2.t3.txt'], None),
    'c4a-pos': ('t3', 'plan', ['c4a-pos.t1.txt', 'c4a.t2.txt'], None),
    'c4a-neg': ('t3', 'plan', ['c4a-neg.t1.txt', 'c4a.t2.txt'], None),
    'c4b': ('t9', 'plan', ['c4b.t1.txt', 'c4b.t2.txt'], None),
    'v1': ('t9', 'plan', ['c4b.t1.txt', 'c4b.t2.txt'], None),
    'fc': ('t9', 'review', [], 'probe-brief'),
    'cr': ('t9', 'review', [], 'probe-brief'),
    'v3': ('t10', 'plan', ['v3.t1.txt'], None),
    'c5a-pos': ('t4', 'exec', ['c5a-pos.t1.txt', 'c5a.t2-merge.txt'], None),
    'c5a-pr': ('t4', 'exec', ['c5a-pr.t1.txt', 'c5a.t2-pr.txt'], None),
    'c5a-ep': ('t4', 'exec', ['c5a-ep.t1.txt', 'c5a.t2-merge.txt'], None),
    'p5a': ('t4', 'exec', ['p5a.t1.txt', 'c5a.t2-merge.txt'], None),
    'c5a-neg': ('t5', 'exec', ['c5a-neg.t1.txt', 'c5a.t2-merge.txt'], None),
    'c5b-pos': ('t6', 'plan', ['c5b.t1.txt', 'c5b.t2.txt'], None),
    'p5b': ('t6', 'plan', ['p5b.t1.txt', 'c5b.t2.txt'], None),
    'c5b-neg': ('t7', 'plan', ['c5b.t1.txt', 'c5b.t2.txt'], None),
    'c5b-part': ('t8', 'plan', ['c5b.t1.txt'], None),
}
PROBE_TEMPLATES = {'fc': 'fact-checker.md', 'cr': 'cold-reader.md'}


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run([*GIT, *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def project_dir(path: Path) -> Path:
    '''Claude Code's per-directory project folder: every non-alphanumeric character becomes a hyphen.'''
    return HOME / '.claude/projects' / re.sub(r'[^A-Za-z0-9]', '-', str(path.resolve()))


def next_ids(count: int) -> list[str]:
    if not REGISTRY.exists():
        REGISTRY.write_text(HEADER)
    used = [int(line.split('\t', 1)[0][1:]) for line in REGISTRY.read_text().splitlines()[1:] if line]
    first = max(used, default=0) + 1
    return [f'r{n:03d}' for n in range(first, first + count)]


def probe_prompt(arm: str, kit: str) -> str:
    out = CTL / 'prompts' / f'{arm}.{kit}.t1.txt'
    if not out.exists():
        template = PW / 'kits' / kit / '.claude/skills/prepare-handoff/references' / PROBE_TEMPLATES[arm]
        text = template.read_text()
        if '[BRIEF_PATH]' not in text:
            sys.exit(f'make_reps.py: {template} has no [BRIEF_PATH] slot')
        out.write_text(text.replace('[BRIEF_PATH]', '@REP@/.handoff/plan-38-handoff.md'))
    return out.name


def add_origin(rep: str, repdir: Path) -> None:
    origin = PW / 'origins' / f'{rep}.git'
    origin.parent.mkdir(parents=True, exist_ok=True)
    run('init', '-q', '--bare', '-b', 'main', str(origin))
    run('-C', str(repdir), 'remote', 'add', 'origin', str(origin))
    run('-C', str(repdir), 'push', '-q', 'origin', 'main')
    run('-C', str(repdir), 'fetch', '-q', 'origin')
    run('-C', str(repdir), 'remote', 'set-head', 'origin', 'main')


def apply_extra(extra: str | None, rep: str, repdir: Path) -> None:
    if extra == 'c2b-brief':
        sha = run('-C', str(repdir), 'rev-parse', '--short', 'main')
        dest = HOME / '.cache/agent-skills/handoffs' / rep / '2026-10-08-site-report-plan.md'
        dest.parent.mkdir(parents=True)
        text = (CTL / 'briefs/c2b-site-report.md').read_text()
        dest.write_text(text.replace('@SHA@', sha).replace('@HANDOFFS@', str(dest.parent)))
    elif extra == 'probe-brief':
        held = repdir / '.handoff'
        held.mkdir()
        (held / '.gitignore').write_text('*\n')
        shutil.copy(CTL / 'briefs/plan-38-planted.md', held / 'plan-38-handoff.md')


def make(arm: str, phase: str, kit: str, count: int, batch: str) -> list[str]:
    template, model_class, prompts, extra = ARMS[arm]
    if arm in PROBE_TEMPLATES:
        prompts = [probe_prompt(arm, kit)]
    if not (PW / 'kits' / kit / '.claude/skills').is_dir():
        sys.exit(f'make_reps.py: no kit {kit} (build_kit.sh builds it)')
    reps = next_ids(count)
    for rep in reps:
        repdir = PW / 'reps' / rep
        taken = [p for p in (repdir, CTL / 'results' / rep, HOME / '.cache/agent-skills/handoffs' / rep,
                             project_dir(repdir)) if p.exists()]
        if taken:
            sys.exit(f'make_reps.py: {rep} is taken: {taken[0]} exists')
        shutil.copytree(PW / 'templates' / template, repdir, symlinks=True)
        add_origin(rep, repdir)
        apply_extra(extra, rep, repdir)
        start = run('-C', str(repdir), 'for-each-ref', '--format=%(refname:short)=%(objectname:short)', 'refs/heads')
        row = [rep, arm, phase, template, kit, model_class, ','.join(prompts), ','.join(start.split())]
        with REGISTRY.open('a') as f:
            f.write('\t'.join(row) + '\n')
    (CTL / 'batches').mkdir(exist_ok=True)
    with (CTL / 'batches' / f'{batch}.txt').open('a') as f:
        f.write(''.join(f'{rep}\n' for rep in reps))
    return reps


def main() -> int:
    parser = argparse.ArgumentParser(description='Create registered reps from a fixture template.')
    parser.add_argument('arm', choices=sorted(ARMS))
    parser.add_argument('phase')
    parser.add_argument('kit')
    parser.add_argument('count', type=int)
    parser.add_argument('batch')
    args = parser.parse_args()
    reps = make(args.arm, args.phase, args.kit, args.count, args.batch)
    print(f'{args.arm} ({args.phase}, kit {args.kit}): {" ".join(reps)} -> batches/{args.batch}.txt')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 6: Write `extract.py`**

```python
#!/usr/bin/env python3
'''Build each rep's extract and audit from what run_rep.sh saved.

Usage: extract.py BATCH                 (every rep in batches/BATCH.txt)
       extract.py --rep REP [--rep REP ...]

Writes results/<rep>/extract.md, which the scorer reads, and
results/<rep>/audit.json. A rep is void (PROTOCOL.md, Audit) when a turn is
missing, failed or reports an error, or when any tool input, in its own
transcript or a subagent's, names a path under a protected root outside the
rep's allowed paths, or names one of the contamination fragments. Permission
denials are listed for the scorer, who voids a rep whose failure traces to one.
'''

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
CTL = HOME / '.cache/agent-skills/handoffs/red'
PW = HOME / '.cache/pondworks'
PROTECTED = tuple(HOME / p for p in (
    '.cache/agent-skills', '.claude', 'Projects', '.cache/pondworks', '.agents', '.codex', '.gemini',
))
FRAGMENTS = (
    'handoffs/red', 'agent-skills/handoff-brief', 'plan40-draft', 'Projects/agent-skills',
    'specs/handoff-briefs', 'red-baseline-handoff',
)
SNAPSHOT_TEMPLATES = ('t9', 't10')
PATH_TOKEN = re.compile(r'''(?:(?<![\w.~$}-])/|~|\$HOME|\$\{HOME\})[^\s'"`;|&<>(){}]*''')
DOTDOT_TOKEN = re.compile(r'''[^\s'"`;|&<>(){}=]*\.\.(?:/[^\s'"`;|&<>(){}]*)?''')
FILE_KEYS = ('file_path', 'path', 'notebook_path')
CAP = 800


# --- audit -------------------------------------------------------------------


def project_dir(path: Path) -> Path:
    return HOME / '.claude/projects' / re.sub(r'[^A-Za-z0-9]', '-', str(path.resolve()))


def allowed_paths(rep: str, template: str, kit: str) -> list[Path]:
    paths = [PW / 'reps' / rep, PW / 'kits' / kit, PW / 'shim', PW / 'origins' / f'{rep}.git',
             HOME / '.cache/agent-skills/handoffs' / rep, project_dir(PW / 'reps' / rep)]
    if template in SNAPSHOT_TEMPLATES:
        paths.append(HOME / '.cache/agent-skills/cc-guide')
    return paths


def normalize(token: str, cwd: Path) -> Path:
    for prefix in ('${HOME}', '$HOME', '~'):
        if token == prefix or token.startswith(prefix + '/'):
            token = str(HOME) + token[len(prefix):]
            break
    path = Path(token)
    return Path(os.path.normpath(path if path.is_absolute() else cwd / path))


def within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def tool_uses(record: dict) -> list[tuple[str, dict]]:
    content = (record.get('message') or {}).get('content')
    if not isinstance(content, list):
        return []
    return [(c.get('name', ''), c.get('input') or {}) for c in content
            if isinstance(c, dict) and c.get('type') == 'tool_use']


def scanned(name: str, data: dict) -> list[str]:
    '''The strings of one tool input that can reach a file: a Bash command (not a
    heredoc's body, which is content), or a tool's path fields.'''
    if name == 'Bash':
        command = str(data.get('command', ''))
        return [command.split('\n', 1)[0] if '<<' in command else command]
    strings = [str(data[k]) for k in FILE_KEYS if k in data]
    if name == 'Glob' and 'pattern' in data:
        strings.append(str(data['pattern']))
    return strings


def flags_for(text: str, cwd: Path, ok: list[Path]) -> list[str]:
    found = []
    tokens = PATH_TOKEN.findall(text) + DOTDOT_TOKEN.findall(text)
    for token in tokens:
        path = normalize(token, cwd)
        if any(within(path, root) for root in PROTECTED) and not any(within(path, a) for a in ok):
            found.append(f'path {path}')
    found += [f'fragment {frag!r}' for frag in FRAGMENTS if frag in text]
    return found


def audit_transcripts(transcripts: list[Path], cwd: Path, ok: list[Path]) -> list[str]:
    flags = set()
    for transcript in transcripts:
        for line in transcript.read_text(errors='replace').splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            for name, data in tool_uses(record):
                for text in scanned(name, data):
                    flags.update(f'{transcript.name}: {name}: {flag}' for flag in flags_for(text, cwd, ok))
    return sorted(flags)


def turn_problems(out: Path, turns: int) -> list[str]:
    problems = []
    for n in range(1, turns + 1):
        f = out / f'turn{n}.json'
        if not f.is_file() or not f.read_text().strip():
            problems.append(f'turn {n}: no output')
            continue
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError:
            problems.append(f'turn {n}: output is not JSON')
            continue
        if data.get('is_error') or data.get('subtype') != 'success':
            problems.append(f'turn {n}: {data.get("subtype")}')
    return problems


# --- extract -----------------------------------------------------------------


def git(repdir: Path, *args: str) -> str:
    done = subprocess.run(['git', '-C', str(repdir), *args], capture_output=True, text=True, check=False)
    return done.stdout if done.returncode == 0 else f'(git {" ".join(args)} failed: {done.stderr.strip()})\n'


def capped(text: str, limit: int = CAP) -> str:
    lines = text.splitlines()
    if len(lines) <= limit:
        return text if text.endswith('\n') or not text else text + '\n'
    return '\n'.join(lines[:limit]) + f'\n[... {len(lines) - limit} more lines cut]\n'


def tool_line(name: str, data: dict) -> str:
    if name in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit'):
        target = data.get('file_path') or data.get('notebook_path', '')
        size = len(str(data.get('content', data.get('new_string', ''))))
        return f'{name}: {target} ({size} chars)'
    if name in ('Agent', 'Task'):
        prompt = ' '.join(str(data.get('prompt', '')).split())[:300]
        return f'{name}: {data.get("subagent_type", "")}: {data.get("description", "")} | {prompt}'
    if name == 'Skill':
        return f'Skill: {data.get("skill", "")} {data.get("args", "")}'.rstrip()
    text = data.get('command', '') if name == 'Bash' else json.dumps(data, ensure_ascii=False)
    return f'{name}: {" ".join(str(text).split())[:300]}'


def transcript_lines(transcript: Path, prompts: list[str]) -> list[str]:
    lines = []
    for raw in transcript.read_text(errors='replace').splitlines():
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            continue
        content = (record.get('message') or {}).get('content')
        if record.get('type') == 'user' and isinstance(content, str):
            for n, prompt in enumerate(prompts, start=1):
                if prompt and content.strip().startswith(prompt.strip()[:60]):
                    lines.append(f'--- turn {n} prompt ---')
        lines += [tool_line(name, data) for name, data in tool_uses(record)]
    return lines


def file_text(path: Path, limit: int = 400) -> str:
    try:
        return capped(path.read_text(errors='replace'), limit)
    except OSError as e:
        return f'(unreadable: {e})\n'


def repo_section(repdir: Path, start: str) -> list[str]:
    starts = dict(pair.split('=', 1) for pair in start.split(',') if pair)
    base = starts.get('main', '')
    parts = ['## Repo at the end\n',
             '### Branches\n', git(repdir, 'for-each-ref', '--format=%(refname:short) %(objectname:short)', 'refs/heads'),
             '### Uncommitted\n', git(repdir, 'status', '--porcelain=v1', '--untracked-files=all') or '(clean)\n',
             '### New commits\n', git(repdir, 'log', '--all', '--format=%h %cs%d %s', '--not', *starts.values()) or '(none)\n']
    for branch in git(repdir, 'for-each-ref', '--format=%(refname:short)', 'refs/heads').split():
        frm = starts.get(branch, base)
        parts += [f'### {branch}: changes since {frm}\n', git(repdir, 'diff', '--stat', '-M', frm, branch),
                  capped(git(repdir, 'diff', '-M', frm, branch, '--', 'specs/'))]
    parts += ['### Uncommitted changes under specs/\n', capped(git(repdir, 'diff', 'HEAD', '--', 'specs/')) or '(none)\n']
    for rel in git(repdir, 'ls-files', '--others', '--exclude-standard').split() + git(
            repdir, 'ls-files', '--others', '--ignored', '--exclude-standard', '--', '.handoff').split():
        if rel.endswith('.md'):
            parts += [f'### Untracked: {rel}\n', file_text(repdir / rel)]
    return parts


def build(rep: str) -> dict:
    row = next(line.split('\t') for line in (CTL / 'registry.tsv').read_text().splitlines() if line.split('\t', 1)[0] == rep)
    _, arm, phase, template, kit, _, prompts, start = row
    out = CTL / 'results' / rep
    repdir = PW / 'reps' / rep
    turns = prompts.split(',')
    transcripts = sorted((out / 'project').rglob('*.jsonl')) if (out / 'project').is_dir() else []
    problems = turn_problems(out, len(turns))
    if not transcripts:
        problems.append('no transcript copied')
    flags = audit_transcripts(transcripts, repdir, allowed_paths(rep, template, kit))
    denials, cost = [], 0.0
    for n in range(1, len(turns) + 1):
        try:
            data = json.loads((out / f'turn{n}.json').read_text())
        except (OSError, json.JSONDecodeError):
            continue
        denials += data.get('permission_denials') or []
        cost += data.get('total_cost_usd') or 0.0
    audit = {'rep': rep, 'arm': arm, 'phase': phase, 'valid': not problems and not flags,
             'problems': problems, 'flags': flags, 'denials': denials, 'cost_usd': round(cost, 4)}
    (out / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n')

    prompt_texts = [(out / f'turn{n}.prompt.txt').read_text() if (out / f'turn{n}.prompt.txt').exists() else ''
                    for n in range(1, len(turns) + 1)]
    parts = [f'# {rep} — {arm} ({phase}; template {template}, kit {kit})\n\n',
             (out / 'meta.txt').read_text() if (out / 'meta.txt').exists() else '', '\n## Audit\n',
             f'- verdict: {"valid" if audit["valid"] else "VOID"}\n',
             f'- problems: {"; ".join(problems) or "none"}\n',
             f'- flags: {"; ".join(flags) or "none"}\n',
             f'- permission denials: {json.dumps(denials) if denials else "none"}\n',
             f'- cost: ${audit["cost_usd"]}\n']
    for n, prompt in enumerate(prompt_texts, start=1):
        result = ''
        try:
            result = json.loads((out / f'turn{n}.json').read_text()).get('result', '')
        except (OSError, json.JSONDecodeError):
            result = '(no result)'
        git_state = (out / f'turn{n}.git.txt').read_text() if (out / f'turn{n}.git.txt').exists() else ''
        parts += [f'\n## Turn {n}\n\n### Prompt\n\n{prompt}\n### Final message\n\n{result}\n\n',
                  f'### Repo after turn {n}\n\n{git_state}\n']
    parts.append('\n## Tool calls, in order\n\n')
    for transcript in transcripts:
        parts.append(f'### {transcript.relative_to(out / "project")}\n')
        parts += [f'- {line}\n' for line in transcript_lines(transcript, prompt_texts)]
    parts.append('\n')
    if repdir.is_dir():
        parts += repo_section(repdir, start)
    for root, label in ((out / 'handoffs', 'Brief directory'), (out / 'project' / 'memory', 'Memory')):
        if root.is_dir():
            for f in sorted(p for p in root.rglob('*') if p.is_file()):
                parts += [f'\n## {label}: {f.relative_to(root)}\n\n', file_text(f)]
    (out / 'extract.md').write_text(''.join(parts))
    return audit


def main() -> int:
    parser = argparse.ArgumentParser(description='Build rep extracts and audits.')
    parser.add_argument('batch', nargs='?')
    parser.add_argument('--rep', action='append', default=[])
    args = parser.parse_args()
    reps = list(args.rep)
    if args.batch:
        reps += [r for r in (CTL / 'batches' / f'{args.batch}.txt').read_text().split() if not r.startswith('#')]
    if not reps:
        parser.error('give a batch or --rep')
    for rep in reps:
        if not (CTL / 'results' / rep).is_dir():
            print(f'{rep}: no results yet')
            continue
        audit = build(rep)
        verdict = 'valid' if audit['valid'] else f'VOID: {"; ".join(audit["problems"] + audit["flags"])}'
        print(f'{rep} {audit["arm"]}: {verdict} (${audit["cost_usd"]}, {len(audit["denials"])} denial(s))')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 7: Write `tally.py`**

```python
#!/usr/bin/env python3
'''Check scores against extracts, then report each arm's verdict.

Usage: tally.py PHASE

Reads scores/PHASE/<arm>.tsv (columns: rep, criterion, verdict, quote; verdict
PASS, FAIL, NA or VOID) and each scored rep's results/<rep>/audit.json and
extract.md. Exits 1, listing the lines, when a PASS, FAIL or VOID line's quote
is empty or not found in its rep's extract (whitespace runs compared as one
space): rescore those. Otherwise prints, per arm, the valid reps counted, the
failures per criterion, and the verdict by PROTOCOL.md's Thresholds.
'''

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

CTL = Path.home() / '.cache/agent-skills/handoffs/red'
GATING = {  # RED arm -> its component and the criteria whose failure gates it
    'c1': ('C1', ('F-a', 'F-b')),
    'c2': ('C2', ('F-log', 'F-spec')),
    'c4a-pos': ('C4a', ('F-lost',)),
    'c4b': ('C4b', ('F-restate', 'F-reading', 'F-unchecked', 'F-gates')),
    'c5a-pos': ('C5a', ('F-handoff', 'F-stamp', 'F-timing', 'F-next')),
    'c5b-pos': ('C5b', ('F-read', 'F-amend', 'F-commit', 'F-line', 'F-scope')),
}
NEGATIVE = {'c4a-neg': 1, 'c5a-neg': 0, 'c5b-neg': 0}  # most failing reps a GREEN negative arm allows
PROBE = {'fc': ('P-f0', 'P-f1'), 'cr': ('P-rt0', 'P-rt13')}
C3 = ('C3-a', 'C3-b', 'C3-c', 'C3-d')
COUNTED = {'v3': 3}  # valid reps counted per arm; every other arm counts 5
RED_GO_AT = 2
GREEN_PASS_AT = 4
V3_PASS_AT = 2


def squash(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def read_scores(path: Path) -> list[dict]:
    with path.open(newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))


def bad_quotes(rows: list[dict], extracts: dict[str, str]) -> list[str]:
    bad = []
    for row in rows:
        if row['verdict'] == 'NA':
            continue
        quote = squash(row.get('quote') or '')
        if not quote or quote not in extracts.get(row['rep'], ''):
            bad.append(f'{row["rep"]} {row["criterion"]} {row["verdict"]}: quote not found')
    return bad


def counted_reps(rows: list[dict], valid: dict[str, bool], arm: str) -> list[str]:
    void = {r['rep'] for r in rows if r['criterion'] == 'VOID'}
    reps = sorted({r['rep'] for r in rows} - void, key=lambda rep: int(rep[1:]))
    return [rep for rep in reps if valid.get(rep, False)][:COUNTED.get(arm, 5)]


def failures(rows: list[dict], reps: list[str], criteria: tuple[str, ...] | None) -> dict[str, set[str]]:
    '''criterion -> reps failing it, among the counted reps.'''
    out: dict[str, set[str]] = {}
    for r in rows:
        if r['rep'] in reps and r['verdict'] == 'FAIL' and (criteria is None or r['criterion'] in criteria):
            out.setdefault(r['criterion'], set()).add(r['rep'])
    return out


def passes(rows: list[dict], reps: list[str], criterion: str) -> int:
    return len({r['rep'] for r in rows if r['rep'] in reps and r['criterion'] == criterion and r['verdict'] == 'PASS'})


def verdict(phase: str, arm: str, rows: list[dict], reps: list[str], red_c3: dict[str, int] | None) -> str:
    need = COUNTED.get(arm, 5)
    if phase == 'pilot':
        return 'pilot (not counted)'
    if len(reps) < need:
        return f'UNSETTLED ({len(reps)} of {need} valid)'
    if phase == 'red':
        if arm not in GATING:
            return 'recorded'
        component, criteria = GATING[arm]
        failing = set().union(*failures(rows, reps, criteria).values())
        return f'{component} {"GO" if len(failing) >= RED_GO_AT else "NO-GO"} ({len(failing)} of {need} failing)'
    if arm in PROBE:
        counts = {c: passes(rows, reps, c) for c in PROBE[arm]}
        ok = all(n >= GREEN_PASS_AT for n in counts.values())
        return f'{"PASS" if ok else "FAIL"} ({", ".join(f"{c} {n}/{need}" for c, n in counts.items())})'
    gating_rows = [r for r in rows if r['criterion'] not in C3]
    failing = set().union(*failures(gating_rows, reps, None).values())
    if arm in NEGATIVE:
        ok = len(failing) <= NEGATIVE[arm]
    elif arm == 'v3':
        ok = need - len(failing) >= V3_PASS_AT
    else:
        ok = need - len(failing) >= GREEN_PASS_AT
    text = f'{"PASS" if ok else "FAIL"} ({len(failing)} of {need} failing)'
    if red_c3 is not None and any(r['criterion'] in C3 for r in rows):
        c3 = {c: passes(rows, reps, c) for c in C3}
        c3_ok = all(c3[c] >= red_c3.get(c, 0) - 1 for c in C3[:3]) and c3['C3-d'] == need
        text += f'; C3 {"PASS" if c3_ok else "FAIL"} (' + ', '.join(
            f'{c} {c3[c]} vs red {red_c3.get(c, 0)}' for c in C3) + ')'
    return text


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: tally.py PHASE', file=sys.stderr)
        return 2
    phase = sys.argv[1]
    files = sorted((CTL / 'scores' / phase).glob('*.tsv'))
    if not files:
        print(f'tally.py: no scores/{phase}/*.tsv', file=sys.stderr)
        return 2
    table = {f.stem: read_scores(f) for f in files}
    reps = {r['rep'] for rows in table.values() for r in rows}
    extracts, valid = {}, {}
    for rep in reps:
        out = CTL / 'results' / rep
        extracts[rep] = squash((out / 'extract.md').read_text()) if (out / 'extract.md').exists() else ''
        valid[rep] = json.loads((out / 'audit.json').read_text())['valid'] if (out / 'audit.json').exists() else False
    bad = [line for rows in table.values() for line in bad_quotes(rows, extracts)]
    if bad:
        print('\n'.join(bad))
        return 1
    red_c3 = None
    red_c2 = CTL / 'scores' / 'red' / 'c2.tsv'
    if phase != 'red' and red_c2.exists():
        red_rows = read_scores(red_c2)
        red_valid = {r: json.loads((CTL / 'results' / r / 'audit.json').read_text())['valid']
                     for r in {row['rep'] for row in red_rows} if (CTL / 'results' / r / 'audit.json').exists()}
        red_reps = counted_reps(red_rows, red_valid, 'c2')
        red_c3 = {c: passes(red_rows, red_reps, c) for c in C3}
    for arm, rows in table.items():
        counted = counted_reps(rows, valid, arm)
        fails = failures(rows, counted, None)
        detail = ' '.join(f'{c}:{len(rs)}' for c, rs in sorted(fails.items())) or '-'
        print(f'{arm:10} counted {",".join(counted) or "-":30} fails {detail:40} {verdict(phase, arm, rows, counted, red_c3)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 8: Write the self-tests and the dry run**

`test_tools.py`:

```python
'''Self-tests for the rep tooling: extract.py's audit and tally.py's checks.

Run: cd ~/.cache/agent-skills/handoffs/red/tools && uv run --python 3.13 --with pytest python -m pytest -q
'''
from __future__ import annotations

import json
from pathlib import Path

import extract
import tally

HOME = Path.home()
PW = HOME / '.cache/pondworks'
REP = PW / 'reps' / 'r001'
OK = extract.allowed_paths('r001', 't1', 'k-a')


def flags(command: str, name: str = 'Bash', key: str = 'command') -> list[str]:
    return extract.flags_for(extract.scanned(name, {key: command})[0], REP, OK)


def test_own_paths_are_allowed():
    assert flags('ls ~/.cache/pondworks/reps/r001/specs') == []
    assert flags(f'cat {PW}/kits/k-a/.claude/skills/writing-plans/SKILL.md') == []
    assert flags('mkdir -p ~/.cache/agent-skills/handoffs/r001') == []
    assert flags(str(extract.project_dir(REP) / 'memory/notes.md'), 'Read', 'file_path') == []


def test_other_protected_paths_are_flagged():
    assert flags('cat ~/.cache/agent-skills/handoffs/red/rubric.md')
    assert flags('ls ~/.cache/agent-skills/handoffs')
    assert flags('ls $HOME/.claude/skills')
    assert flags(f'cat {PW}/reps/r002/specs/x.md')
    assert flags('cat ../r002/specs/x.md')
    assert flags(str(HOME / 'Projects/agent-skills/CLAUDE.md'), 'Read', 'file_path')


def test_fragments_catch_relative_reach():
    assert flags('cd ~ && cat .cache/agent-skills/handoffs/red/rubric.md')


def test_heredoc_body_and_ranges_are_not_accesses():
    assert flags('cat > notes.md <<EOF\nsee ~/.claude/projects/x\nEOF') == []
    assert flags('git log --oneline main..HEAD -- specs/plans') == []
    assert flags('curl -s https://example.invalid/x') == []


def test_snapshot_templates_may_read_the_docs_cache():
    ok = extract.allowed_paths('r001', 't9', 'k-a')
    assert extract.flags_for('ls ~/.cache/agent-skills/cc-guide/2.1.288/docs', REP, ok) == []
    assert extract.flags_for('ls ~/.cache/agent-skills/cc-guide/2.1.288/docs', REP, OK)


def test_audit_reads_tool_uses_from_transcripts(tmp_path):
    record = {'type': 'assistant', 'message': {'content': [
        {'type': 'tool_use', 'name': 'Read', 'input': {'file_path': str(HOME / '.claude/CLAUDE.md')}},
        {'type': 'text', 'text': 'see ~/.claude/CLAUDE.md'},
    ]}}
    transcript = tmp_path / 'session.jsonl'
    transcript.write_text(json.dumps(record) + '\nnot json\n')
    found = extract.audit_transcripts([transcript], REP, OK)
    assert len(found) == 1
    assert found[0].startswith('session.jsonl: Read: path ')


def rows(*specs: tuple[str, str, str]) -> list[dict]:
    return [{'rep': rep, 'criterion': c, 'verdict': v, 'quote': f'{rep} {c}'} for rep, c, v in specs]


def test_bad_quotes_are_reported():
    scored = rows(('r001', 'F-a', 'PASS'), ('r002', 'F-a', 'NA'))
    assert tally.bad_quotes(scored, {'r001': 'r001 F-a here'}) == []
    assert tally.bad_quotes(scored, {'r001': 'something else'}) == ['r001 F-a PASS: quote not found']


def red_rows(failing: int) -> list[dict]:
    reps = [f'r00{n}' for n in range(1, 6)]
    return rows(*[(rep, 'F-a', 'FAIL' if n < failing else 'PASS') for n, rep in enumerate(reps)],
                *[(rep, 'F-b', 'PASS') for rep in reps])


def test_red_go_needs_two_failing_reps():
    valid = {f'r00{n}': True for n in range(1, 6)}
    for failing, word in ((2, 'C1 GO'), (1, 'C1 NO-GO')):
        scored = red_rows(failing)
        reps = tally.counted_reps(scored, valid, 'c1')
        assert tally.verdict('red', 'c1', scored, reps, None).startswith(word)


def test_green_and_negative_thresholds():
    valid = {f'r00{n}': True for n in range(1, 6)}
    one_fail = red_rows(1)
    reps = tally.counted_reps(one_fail, valid, 'c1')
    assert tally.verdict('green1', 'c1', one_fail, reps, None).startswith('PASS')
    assert tally.verdict('green2', 'c5a-neg', one_fail, reps, None).startswith('FAIL')
    assert tally.verdict('green3', 'c4a-neg', one_fail, reps, None).startswith('PASS')
    two_fail = red_rows(2)
    assert tally.verdict('green1', 'c1', two_fail, reps, None).startswith('FAIL')


def test_void_and_invalid_reps_are_not_counted():
    scored = red_rows(0) + rows(('r006', 'F-a', 'PASS'), ('r002', 'VOID', 'VOID'))
    valid = {f'r00{n}': True for n in range(1, 7)}
    valid['r003'] = False
    assert tally.counted_reps(scored, valid, 'c1') == ['r001', 'r004', 'r005', 'r006']
    assert tally.verdict('red', 'c1', scored, tally.counted_reps(scored, valid, 'c1'), None).startswith('UNSETTLED')
```

`dry_run.sh`:

```bash
#!/usr/bin/env bash
# Dry run of the rep pipeline: make_reps.py, run_batch.sh, run_rep.sh,
# extract.py and tally.py against a throwaway HOME, with a stub in place of
# claude. It launches no session. Prints "dry run: ok" or stops at the first
# failed check.
#
# Usage: dry_run.sh
set -euo pipefail

TOOLS=$(cd "$(dirname "$0")" && pwd)
F=$(mktemp -d)
trap 'rm -rf "$F"' EXIT
C="$F/.cache/agent-skills/handoffs/red"
P="$F/.cache/pondworks"
mkdir -p "$C/tools" "$C/prompts" "$P/templates/t1/specs" "$P/kits/k-a/.claude/skills/writing-plans" "$P/shim"
cp "$TOOLS"/*.sh "$TOOLS"/*.py "$C/tools/"
chmod +x "$C/tools/"*.sh "$C/tools/"*.py
printf -- '---\nname: writing-plans\ndescription: Use when testing.\n---\n' > "$P/kits/k-a/.claude/skills/writing-plans/SKILL.md"
printf '# Spec\n' > "$P/templates/t1/specs/sensor-export.md"
git -C "$P/templates/t1" init -q -b main
git -C "$P/templates/t1" add -A
git -C "$P/templates/t1" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -qm fixture
printf 'Use writing-plans on specs/sensor-export.md.\n' > "$C/prompts/c1.t1.txt"
printf 'MODEL_PLAN=m\nEFFORT_PLAN=low\nMODEL_EXEC=m\nEFFORT_EXEC=low\nMODEL_REVIEW=m\nEFFORT_REVIEW=low\n' > "$C/config.env"

# The stub answers --version, appends two records to the session transcript,
# and prints a success result. Its Bash call reaches the rep's own specs/ when
# run in r001, and r001's from any other rep, which the audit must flag.
cat > "$F/stub-claude" <<'EOF'
#!/bin/bash
if [ "$1" = --version ]; then echo "0.0.0 (stub)"; exit 0; fi
sid=""; while [ $# -gt 0 ]; do case $1 in --session-id|--resume) sid=$2; shift 2;; *) shift;; esac; done
prompt=$(cat)
d="$HOME/.claude/projects/$(pwd -P | sed 's/[^A-Za-z0-9]/-/g')"; mkdir -p "$d"
python3 - "$d/$sid.jsonl" "$prompt" <<'PY'
import json, sys
with open(sys.argv[1], 'a') as f:
    f.write(json.dumps({'type': 'user', 'message': {'role': 'user', 'content': sys.argv[2]}}) + '\n')
    f.write(json.dumps({'type': 'assistant', 'message': {'content': [
        {'type': 'tool_use', 'name': 'Bash', 'input': {'command': 'ls ~/.cache/pondworks/reps/r001/specs'}}]}}) + '\n')
PY
printf '{"type":"result","subtype":"success","is_error":false,"result":"Stub reply.","session_id":"%s","total_cost_usd":0.25,"permission_denials":[]}\n' "$sid"
EOF
chmod +x "$F/stub-claude"

HOME="$F" python3 "$C/tools/make_reps.py" c1 pilot k-a 2 dry > /dev/null
[ "$(tail -n +2 "$C/registry.tsv" | cut -f1,2,3 | tr '\t\n' ' ')" = 'r001 c1 pilot r002 c1 pilot ' ]
[ "$(git -C "$P/reps/r001" symbolic-ref --short refs/remotes/origin/HEAD)" = origin/main ]
env -u CLAUDECODE HOME="$F" CLAUDE_BIN="$F/stub-claude" bash "$C/tools/run_batch.sh" dry > /dev/null
[ -f "$C/results/r001/turn1.json" ] && [ -d "$C/results/r001/project" ]
HOME="$F" python3 "$C/tools/extract.py" dry > /dev/null
python3 -c "import json,sys; a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); assert a['valid'] and not b['valid'], (a, b)" \
  "$C/results/r001/audit.json" "$C/results/r002/audit.json"
grep -q '^### Final message' "$C/results/r001/extract.md"
if env -u CLAUDECODE HOME="$F" CLAUDE_BIN="$F/stub-claude" bash "$C/tools/run_rep.sh" r001 2> /dev/null; then exit 1; fi
if CLAUDECODE=1 HOME="$F" CLAUDE_BIN="$F/stub-claude" bash "$C/tools/run_rep.sh" r002 2> /dev/null; then exit 1; fi
mkdir -p "$C/scores/dry"
printf 'rep\tcriterion\tverdict\tquote\nr001\tF-a\tFAIL\tinvented quote\n' > "$C/scores/dry/c1.tsv"
if HOME="$F" python3 "$C/tools/tally.py" dry > /dev/null; then exit 1; fi
printf 'rep\tcriterion\tverdict\tquote\nr001\tF-a\tFAIL\tStub reply.\n' > "$C/scores/dry/c1.tsv"
HOME="$F" python3 "$C/tools/tally.py" dry | grep -q 'UNSETTLED (1 of 5 valid)'
echo 'dry run: ok'
```

- [ ] **Step 9: Make the scripts executable and check their syntax**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && chmod +x run_rep.sh run_batch.sh build_kit.sh dry_run.sh make_reps.py extract.py tally.py && bash -n run_rep.sh && bash -n run_batch.sh && bash -n build_kit.sh && bash -n dry_run.sh && python3 -m py_compile make_reps.py extract.py tally.py && echo syntax-ok
```

Expected: `syntax-ok`.

- [ ] **Step 10: Run the self-tests and the dry run**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && uv run --python 3.13 --with pytest python -m pytest -q test_tools.py && ./dry_run.sh
```

Expected: `10 passed`, then `dry run: ok`. The dry run launches no session: it uses a stub in place of `claude`, under a throwaway HOME that it deletes on exit.

- [ ] **Step 11: Record completion**

There is nothing to commit; nothing here is in git. In the ledger, write `Task 2: complete (no repo commits; tools in ~/.cache/agent-skills/handoffs/red/tools)` once review is clean.

### Task 3: Fixture templates

**Executor:** implementer. **Review:** no review package. The reviewer reads `build_fixtures.py`, re-runs Step 3, and compares the shas.

**Files:**
- Create (not in git): `~/.cache/agent-skills/handoffs/red/tools/build_fixtures.py`
- Create (not in git): `~/.cache/pondworks/templates/t1` … `t10`

**Interfaces:**
- Consumes: the real repo at `/Users/lowell/Projects/agent-skills`, read-only. t9 and t10 are clones of it.
- Produces the templates `make_reps.py` copies. Each template's role is in the script's docstring. The facts later tasks rely on:
  - t4 is checked out on `feat/s2a-csv-export`. Its live plan is `specs/plans/4-pondwatch-v2-s2a.md`, and its ledger is `.sdd/4-pondwatch-v2-s2a/progress.md`.
  - t5's live plan is `specs/plans/4-log-rotation.md`, on `feat/log-rotation`.
  - In t6–t8, plan 4 is retired to `specs/plans/completed/4-pondwatch-v2-s2a.md` and the roadmap is `specs/pondwatch-v2-roadmap.md`.

- [ ] **Step 1: Write `build_fixtures.py`**

````python
#!/usr/bin/env python3
'''Build the fixture templates the reps copy: ~/.cache/pondworks/templates/t1-t10.

Usage: build_fixtures.py            build every template that does not exist yet
       build_fixtures.py --verify   only check the built templates

t1-t8 are hand-written pondwatch repositories (spec R7.6: nothing is copied
from alt-nfp-stats). t9 and t10 are clones of agent-skills truncated at
7137e5e and a3e9b75. Every pondwatch commit has a fixed author and date, so a
rebuild reproduces the same shas. Templates are built before any rep is made
and never rebuilt after: it refuses to overwrite one.

  t1  C1, P1      a DRAFT spec, and a completed plan whose constraint names it
                  only by nickname
  t2  C2 and kin  an approved spec whose R4 the owner overturns at plan review
  t3  C4a+, C4a-  an approved spec, decisions held after approval
  t4  C5a+ etc.   roadmap stage S2a executed on a branch, with one deviation
                  that S2b consumes
  t5  C5a-        a plan that is not a stage, executed, with a live roadmap
  t6  C5b+, P5b   S2a stamped; its Handoff section changes S2b's Consumes
  t7  C5b-        S2a stamped; its Handoff section reads None
  t8  C5b-part    S2a stamped; its Handoff section asks for a new stage
  t9  C4b, V1, probe   agent-skills at 7137e5e
  t10 V3          agent-skills at a3e9b75
'''

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATES = Path.home() / '.cache/pondworks/templates'
AGENT_SKILLS = Path('/Users/lowell/Projects/agent-skills')
SNAPSHOTS = {'t9': ('7137e5e', ('f72822a', 'db41cc9')), 't10': ('a3e9b75', ('7137e5e', 'f72822a', 'db41cc9'))}
WHO = {'GIT_AUTHOR_NAME': 'Pond Works', 'GIT_AUTHOR_EMAIL': 'dev@pondworks.example',
       'GIT_COMMITTER_NAME': 'Pond Works', 'GIT_COMMITTER_EMAIL': 'dev@pondworks.example'}
SDD_HEADER = ('> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via '
              'subagent-driven-development (the default) — or executing-plans when your human partner chose '
              'inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.')
ROADMAP_LINE = ('> Roadmap: specs/pondwatch-v2-roadmap.md, Stage {stage} — on plan completion, tick the '
                'stage and re-validate later stages against what shipped.')


class Repo:
    def __init__(self, root: Path):
        self.root = root
        root.mkdir(parents=True)
        self.git('init', '-q', '-b', 'main')

    def git(self, *args: str, date: str | None = None) -> str:
        env = {**os.environ, **WHO}
        if date:
            env['GIT_AUTHOR_DATE'] = env['GIT_COMMITTER_DATE'] = f'{date}T10:00:00+00:00'
        done = subprocess.run(['git', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null',
                               '-C', str(self.root), *args], env=env, capture_output=True, text=True, check=True)
        return done.stdout.strip()

    def write(self, files: dict[str, str]) -> None:
        for rel, text in files.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def move(self, src: str, dst: str) -> None:
        (self.root / dst).parent.mkdir(parents=True, exist_ok=True)
        self.git('mv', src, dst)

    def commit(self, message: str, date: str, files: dict[str, str] | None = None) -> str:
        self.write(files or {})
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message, date=date)
        return self.git('rev-parse', '--short', 'HEAD')


# --- the pondwatch project every t1-t8 template starts from -------------------

README = '''# pondwatch

Reads water-quality readings from pond sensors (CSV) and reports on them.

## Development

    uv run --no-project --python 3.13 --with pytest python -m pytest -q

Specs live in `specs/`, implementation plans in `specs/plans/`.
'''

PYPROJECT = '''[project]
name = "pondwatch"
version = "0.3.0"
requires-python = ">=3.13"
dependencies = []
'''

READINGS = """'''Load sensor readings from CSV.'''
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Reading:
    site: str
    taken_at: str
    temp_c: float
    ph: float | None
    do_mg_l: float


def load_readings(path: Path) -> list[Reading]:
    with path.open(newline='') as f:
        return [
            Reading(
                site=row['site'],
                taken_at=row['taken_at'],
                temp_c=float(row['temp_c']),
                ph=float(row['ph']) if row['ph'] else None,
                do_mg_l=float(row['do_mg_l']),
            )
            for row in csv.DictReader(f)
        ]
"""

READINGS_VALIDATED = """'''Load sensor readings from CSV, rejecting values outside their physical range.'''
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

RANGES = {'temp_c': (-5.0, 40.0), 'ph': (0.0, 14.0), 'do_mg_l': (0.0, 20.0)}


class ReadingError(ValueError):
    '''A row with a value outside its physical range.'''


@dataclass(frozen=True)
class Reading:
    site: str
    taken_at: str
    temp_c: float
    ph: float | None
    do_mg_l: float


def check_ranges(row_number: int, reading: Reading) -> Reading:
    for name, (low, high) in RANGES.items():
        value = getattr(reading, name)
        if value is not None and not low <= value <= high:
            raise ReadingError(f'row {row_number}: {name} {value} is outside {low}..{high}')
    return reading


def load_readings(path: Path) -> list[Reading]:
    with path.open(newline='') as f:
        return [
            check_ranges(n, Reading(
                site=row['site'],
                taken_at=row['taken_at'],
                temp_c=float(row['temp_c']),
                ph=float(row['ph']) if row['ph'] else None,
                do_mg_l=float(row['do_mg_l']),
            ))
            for n, row in enumerate(csv.DictReader(f), start=2)
        ]
"""

CLI = """'''Command line for pondwatch.'''
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from pondwatch.readings import load_readings


def summary(path: Path) -> None:
    counts = Counter(reading.site for reading in load_readings(path))
    for site in sorted(counts):
        print(f'{site}  {counts[site]}')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='pondwatch')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('summary', help='count readings per site')
    p.add_argument('csv', type=Path)
    args = parser.parse_args(argv)
    if args.command == 'summary':
        summary(args.csv)
    return 0


if __name__ == '__main__':
    sys.exit(main())
"""

TEST_READINGS = """from pathlib import Path

from pondwatch.readings import load_readings

ROWS = 'site,taken_at,temp_c,ph,do_mg_l\\nnorth,2026-09-01T08:00,14.5,7.2,8.1\\nsouth,2026-09-01T08:00,15.0,,7.9\\n'


def test_load_readings_parses_rows(tmp_path: Path):
    data = tmp_path / 'r.csv'
    data.write_text(ROWS)
    rows = load_readings(data)
    assert [r.site for r in rows] == ['north', 'south']
    assert rows[1].ph is None


def test_header_only_file_loads_no_rows(tmp_path: Path):
    data = tmp_path / 'r.csv'
    data.write_text('site,taken_at,temp_c,ph,do_mg_l\\n')
    assert load_readings(data) == []
"""

TEST_RANGES = """from pathlib import Path

import pytest

from pondwatch.readings import ReadingError, load_readings


def test_out_of_range_ph_names_the_row(tmp_path: Path):
    data = tmp_path / 'r.csv'
    data.write_text('site,taken_at,temp_c,ph,do_mg_l\\nnorth,2026-09-01T08:00,14.5,15,8.1\\n')
    with pytest.raises(ReadingError, match='row 2: ph 15.0'):
        load_readings(data)
"""

TEST_CLI = """from pathlib import Path

from pondwatch.cli import main

ROWS = ('site,taken_at,temp_c,ph,do_mg_l\\n'
        'north,2026-09-01T08:00,14.5,7.2,8.1\\nnorth,2026-09-02T08:00,15.5,7.0,8.3\\n'
        'south,2026-09-01T08:00,15.0,,7.9\\n')


def test_summary_counts_readings_per_site(tmp_path: Path, capsys):
    data = tmp_path / 'r.csv'
    data.write_text(ROWS)
    assert main(['summary', str(data)]) == 0
    assert capsys.readouterr().out == 'north  2\\nsouth  1\\n'
"""

SPEC_LOADER = '''# Readings loader — Design Spec

**Status: COMPLETE (2026-09-10)** — implemented by plan 1.

## Requirements

**R1.** `load_readings(path)` returns one `Reading` per CSV row, with `site`,
`taken_at`, `temp_c`, `ph` and `do_mg_l`.

**R2.** An empty `ph` loads as `None`.
'''

PLAN_LOADER = f'''# Readings Loader Implementation Plan

**Status: COMPLETE (2026-09-10)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

{SDD_HEADER}

**Goal:** Load sensor readings from CSV into typed records.

**Architecture:** One module, `pondwatch/readings.py`, over the stdlib `csv` reader.

**Tech Stack:** Python 3.13, stdlib, pytest.

## Global Constraints

- Columns: `site`, `taken_at`, `temp_c`, `ph`, `do_mg_l`; an empty `ph` loads as `None`.
- Stdlib only.

---

### Task 1: load_readings

- [x] **Step 1: Write the failing test** for two rows, one with an empty `ph`.
- [x] **Step 2: Run it and see it fail.**
- [x] **Step 3: Implement `Reading` and `load_readings`.**
- [x] **Step 4: Run the tests.**
- [x] **Step 5: Commit.**
'''

SPEC_SUMMARY = '''# Site summary — Design Spec

**Status: COMPLETE (2026-09-18)** — implemented by plan 2.

## Requirements

**R1.** `pondwatch summary <csv>` prints one line per site, sorted by name:
the site and its number of readings, separated by two spaces.
'''

PLAN_SUMMARY = f'''# Site Summary Implementation Plan

**Status: COMPLETE (2026-09-18)** — executed via subagent-driven-development; nothing deferred

{SDD_HEADER}

**Goal:** `pondwatch summary <csv>` prints the number of readings per site.

**Architecture:** An argparse subcommand in `pondwatch/cli.py` over `load_readings`.

**Tech Stack:** Python 3.13, stdlib, pytest.

## Global Constraints

- Output: `<site>  <count>`, two spaces, sorted by site.

---

### Task 1: summary subcommand

- [x] **Step 1: Write the failing CLI test.**
- [x] **Step 2: Run it and see it fail.**
- [x] **Step 3: Implement `summary` and `main`.**
- [x] **Step 4: Run the tests.**
- [x] **Step 5: Commit.**
'''

DEFERRED = '''# Deferred items

## 1-readings-loader — 2026-09-10
- [x] Review Minor: no test covers a file with only a header row (reviewer
      report, triaged defer). Size: quick-fix. Done when:
      tests/test_readings.py covers it. → done in plan 2
'''


def base(repo: Repo) -> None:
    repo.commit('feat: load readings from CSV (plan 1)', '2026-09-10', {
        'README.md': README,
        'pyproject.toml': PYPROJECT,
        '.gitignore': '__pycache__/\n.pytest_cache/\n.venv/\nuv.lock\n',
        'pondwatch/__init__.py': "'''pondwatch: water-quality readings from pond sensors.'''\n",
        'pondwatch/readings.py': READINGS,
        'tests/test_readings.py': TEST_READINGS,
        'specs/completed/readings-loader.md': SPEC_LOADER,
        'specs/plans/completed/1-readings-loader.md': PLAN_LOADER,
        'specs/deferred_items.md': DEFERRED,
    })
    repo.commit('feat: count readings per site (plan 2)', '2026-09-18', {
        'pondwatch/cli.py': CLI,
        'tests/test_cli.py': TEST_CLI,
        'specs/completed/site-summary.md': SPEC_SUMMARY,
        'specs/plans/completed/2-site-summary.md': PLAN_SUMMARY,
    })


# --- t1: a DRAFT spec, and a nickname precondition in a completed plan ------

ALERTS = """'''Alert codes for readings outside safe ranges.'''
from __future__ import annotations

from pondwatch.readings import Reading


def alert_codes(reading: Reading) -> list[str]:
    codes = []
    if reading.temp_c > 25:
        codes.append('temp_high')
    if reading.ph is not None and reading.ph < 6.5:
        codes.append('ph_low')
    if reading.ph is not None and reading.ph > 8.5:
        codes.append('ph_high')
    if reading.do_mg_l < 5:
        codes.append('do_low')
    return codes


def alert_flags(reading: Reading) -> str:
    return ';'.join(alert_codes(reading))
"""

TEST_ALERTS = """from pondwatch.alerts import alert_flags
from pondwatch.readings import Reading


def test_flags_join_codes_in_order():
    reading = Reading('north', '2026-09-01T08:00', 26.0, 6.0, 4.0)
    assert alert_flags(reading) == 'temp_high;ph_low;do_low'


def test_no_codes_is_empty():
    assert alert_flags(Reading('north', '2026-09-01T08:00', 14.0, 7.0, 8.0)) == ''
"""

SPEC_EXPORT_DRAFT = '''# Sensor export — Design Spec

**Status: DRAFT (2026-09-20).** Not yet reviewed.

## Purpose

Field teams want the readings as a CSV they can open in a spreadsheet, with
each reading's alert codes beside it.

## Requirements

**R1.** `pondwatch export <csv> --out <path>` writes every reading as one CSV
row.

**R2.** Columns, in order: `site`, `taken_at`, `temp_c`, `ph`, `do_mg_l`,
`alerts`.

**R3.** `alerts` holds the reading's alert codes from `pondwatch/alerts.py`,
joined with `;`, or is empty.

**R4.** An empty `ph` is written as an empty field.

## Out of scope

- Spreadsheet formats other than CSV.
- Filtering by site or date.
'''


def plan_alerts(exporter_precondition: bool) -> str:
    constraint = ('- The exporter spec still lists the retired `alerts` column. It must switch to\n'
                  '  `alert_flags`, and be approved again, before anyone plans it.\n') if exporter_precondition else ''
    notes = '\n## Notes\n\n- Related spec: `specs/sensor-export.md`.\n' if exporter_precondition else ''
    return f'''# Alert Flags Implementation Plan

**Status: COMPLETE (2026-09-24)** — executed via subagent-driven-development; nothing deferred

{SDD_HEADER}

**Goal:** Compute alert codes for readings outside safe ranges.

**Architecture:** `pondwatch/alerts.py` computes codes from one `Reading`;
callers join them into the `alert_flags` column.

**Tech Stack:** Python 3.13, stdlib, pytest.

## Global Constraints

- The column is `alert_flags`. The draft name `alerts` is retired everywhere.
- Codes: `temp_high` above 25 °C, `ph_low` below 6.5, `ph_high` above 8.5,
  `do_low` below 5 mg/L, joined with `;` in that order.
{constraint}- Stdlib only.

---

### Task 1: alert_codes

- [x] **Step 1: Write the failing tests** for each code and for none.
- [x] **Step 2: Run them and see them fail.**
- [x] **Step 3: Implement `alert_codes`.**
- [x] **Step 4: Run the tests.**
- [x] **Step 5: Commit.**

### Task 2: alert_flags

- [x] **Step 1: Write the failing test** for the joined order.
- [x] **Step 2: Run it and see it fail.**
- [x] **Step 3: Implement `alert_flags`.**
- [x] **Step 4: Run the tests.**
- [x] **Step 5: Commit.**
{notes}'''


def build_t1(root: Path) -> None:
    repo = Repo(root)
    base(repo)
    repo.commit('docs(specs): draft the sensor export spec', '2026-09-20', {'specs/sensor-export.md': SPEC_EXPORT_DRAFT})
    repo.commit('feat: alert flags (plan 3)', '2026-09-24', {
        'pondwatch/alerts.py': ALERTS,
        'tests/test_alerts.py': TEST_ALERTS,
        'specs/plans/completed/3-alert-flags.md': plan_alerts(exporter_precondition=True),
    })


# --- t2: an approved spec the owner amends at plan review --------------------

SPEC_REPORT = '''# Site report — Design Spec

**Status: DESIGN APPROVED (2026-10-02).** Approved by the owner after review.

## Purpose

`pondwatch report <csv>` prints one line per site with the mean temperature,
pH and dissolved oxygen of its readings, so a field team sees at a glance which
ponds drift.

## Requirements

**R1.** `pondwatch report <csv>` reads the readings with `load_readings`.

**R2.** It prints a header line, `site  temp_c  ph  do_mg_l`, then one line per
site, sorted by site name, with the mean of each column over that site's
readings.

**R3.** Columns are separated by two spaces.

**R4.** A reading with a missing pH is left out of its site's pH mean, and a
warning naming the site and the reading's time goes to stderr. Its temperature
and dissolved oxygen still count.

**R5.** A file with only a header row prints the report header and exits 0.

## Out of scope

- Charts, export formats and alerts.

## Testing

Unit tests for the means and the missing-pH rule, and one CLI test through
`main`.
'''


def build_t2(root: Path) -> None:
    repo = Repo(root)
    base(repo)
    repo.commit('docs(specs): approve the site report spec', '2026-10-02', {'specs/site-report.md': SPEC_REPORT})


# --- t3: an approved spec; the owner's later decisions are held in the session

SPEC_ALERT_EMAIL = '''# Site alert email — Design Spec

**Status: DESIGN APPROVED (2026-10-03).**

## Purpose

When a reading carries alert codes, email the site's contact so someone checks
the pond the same day.

## Requirements

**R1.** `pondwatch alerts <csv>` finds the readings whose alert codes
(`pondwatch/alerts.py`) are not empty.

**R2.** It sends one email per alerting reading to the site's contact, read
from `sites.toml`.

**R3.** The subject is `pondwatch: <site> <codes>`; the body lists the
reading's values.

**R4.** The sender address is read from `pondwatch.toml`, key
`[email] sender`.

**R5.** If sending an email fails, it falls back to an SMS to the contact's
phone number from `sites.toml`.

**R6.** `--dry-run` prints the emails instead of sending them.

## Out of scope

- Scheduling: the command runs from cron.
'''


def build_t3(root: Path) -> None:
    repo = Repo(root)
    base(repo)
    repo.commit('feat: alert flags (plan 3)', '2026-09-24', {
        'pondwatch/alerts.py': ALERTS,
        'tests/test_alerts.py': TEST_ALERTS,
        'specs/plans/completed/3-alert-flags.md': plan_alerts(exporter_precondition=False),
    })
    repo.commit('docs(specs): approve the site alert email spec', '2026-10-03', {'specs/site-alert-email.md': SPEC_ALERT_EMAIL})


# --- t4-t8: the pondwatch v2 roadmap -------------------------------------------

SPEC_V2 = '''# pondwatch v2 — Design Spec

**Status: DESIGN APPROVED (2026-09-20).**

## Purpose

Make pondwatch's output trustworthy and shareable: validate readings, export
them, report per site, and email the sites that drift.

## Requirements

**R1. Validation.** `load_readings` rejects a row whose `temp_c`, `ph` or
`do_mg_l` is outside its physical range, naming the row.

**R2. Raw export.** Readings export to CSV through one function in
`pondwatch/export.py` that later commands reuse.

**R3. Site report export.** `pondwatch report <csv> --out <path>` writes each
site's mean temperature, pH and dissolved oxygen as CSV, through R2's export
function.

**R4. Alert emails.** Sites whose means cross a threshold get an email built
from R3's report.
'''


def roadmap(s1_stamp: str, s2a_box: str = ' ', s2a_stamp: str = '') -> str:
    return f'''# pondwatch v2 — Roadmap

> For agentic workers: REQUIRED SKILL: derive-roadmap — resume via its
> reconcile step; route each unticked stage per its ROUTING line; never plan
> this document wholesale.

Source: `specs/pondwatch-v2.md`.

## Gap analysis

| Req | Verdict | Evidence |
|---|---|---|
| R1 | missing | `load_readings` accepts any float |
| R2 | missing | no `pondwatch/export.py` |
| R3 | missing | no `report` command |
| R4 | missing | no email code |

## Stages

- [x] Stage S1: Range validation
      Objective: reject out-of-range readings when they load.
      Spec: §R1
      Gap closed: R1
      Consumes: nothing
      Produces: `load_readings` raises `ReadingError` naming the row
      Exit: a row with `ph` 15 fails to load, and the error names row 2
      ROUTING: writing-plans
{s1_stamp}
- [{s2a_box}] Stage S2a: Raw CSV export
      Objective: one CSV writer that later commands reuse.
      Spec: §R2
      Gap closed: R2
      Consumes: S1's validated readings
      Produces: `export_csv(rows, path)` in `pondwatch/export.py`, header row from the first row's keys
      Exit: `export_csv` round-trips the fixture readings through `csv.DictReader`
      ROUTING: brainstorming
{s2a_stamp}
- [ ] Stage S2b: Site report export
      Objective: write the per-site report as CSV.
      Spec: §R3
      Gap closed: R3
      Consumes: `export_csv(rows, path)` from S2a
      Produces: `pondwatch report <csv> --out <path>`
      Exit: the command writes one row per site with three means
      ROUTING: writing-plans

- [ ] Stage S3: Alert emails
      Objective: email the sites whose means cross a threshold.
      Spec: §R4
      Gap closed: R4
      Consumes: S2b's report rows
      Produces: `pondwatch alerts <csv>`
      Exit: a site over threshold yields one email in `--dry-run` output
      ROUTING: brainstorming

## Stage-spec stamp

Each stage spec's Rollout note carries:

> Roadmap: specs/pondwatch-v2-roadmap.md, Stage N — on plan completion, tick the
> stage and re-validate later stages against what shipped.

## Completion

Once every stage is ticked, re-run the gap rubric over R1–R4 on the accumulated
system.
'''


S1_STAMP = ('\n> Stage S1: COMPLETE (2026-09-30) — implemented by plan 3 '
            '(specs/plans/completed/3-pondwatch-v2-s1.md).\n> Next: resume the roadmap.\n')

PLAN_S1 = f'''# S1 Range Validation Implementation Plan

**Status: COMPLETE (2026-09-30)** — executed via subagent-driven-development; nothing deferred

{SDD_HEADER}

{ROADMAP_LINE.format(stage='S1')}

**Goal:** Reject out-of-range readings when they load.

**Architecture:** `check_ranges` in `pondwatch/readings.py`, called per row by `load_readings`.

**Tech Stack:** Python 3.13, stdlib, pytest.

## Global Constraints

- Ranges: `temp_c` -5 to 40, `ph` 0 to 14, `do_mg_l` 0 to 20.
- The error names the CSV row number, counting the header as row 1.

---

### Task 1: check_ranges

- [x] **Step 1: Write the failing test** for `ph` 15 on row 2.
- [x] **Step 2: Run it and see it fail.**
- [x] **Step 3: Implement `ReadingError` and `check_ranges`.**
- [x] **Step 4: Run the tests.**
- [x] **Step 5: Commit.**
'''

SPEC_S2A = '''# S2a Raw CSV export — Design Spec

**Status: DESIGN APPROVED (2026-10-01).**

## Purpose

One CSV writer that the site report (S2b) and the alert emails (S3) reuse
(`specs/pondwatch-v2.md` §R2).

## Requirements

**R1.** `pondwatch/export.py` defines `export_csv(rows, path)`. `rows` is a
list of dicts; the header row comes from the first row's keys; it returns the
number of rows written.

**R2.** An empty `rows` writes nothing and returns 0.

**R3.** `pondwatch export <csv> --out <path>` writes the loaded readings through
`export_csv`.

## Rollout

> Roadmap: specs/pondwatch-v2-roadmap.md, Stage S2a — on plan completion, tick the
> stage and re-validate later stages against what shipped.
'''


def plan_s2a(done: bool, deviation: bool, handoff: str = '') -> str:
    box = 'x' if done else ' '
    status = '**Status: COMPLETE (2026-10-05)** — executed via subagent-driven-development; nothing deferred\n\n' if done else ''
    note = ('> Deviation: shipped `write_table(rows, path, columns=None)` — the Task 1 review asked for a name\n'
            '> that fits any table, and `columns` fixes the header order.\n\n') if done and deviation else ''
    return f'''# S2a Raw CSV Export Implementation Plan

{status}{SDD_HEADER}

{ROADMAP_LINE.format(stage='S2a')}

**Goal:** One CSV export function that later stages reuse.

**Architecture:** A single module, `pondwatch/export.py`, over `csv.DictWriter`,
and an `export` subcommand that writes loaded readings through it.

**Tech Stack:** Python 3.13, stdlib, pytest.

## Global Constraints

- The function is `export_csv(rows, path)` in `pondwatch/export.py` (S2a spec R1).
- Rows are dicts; the header row comes from the first row's keys.
- Stdlib only.

---

### Task 1: export_csv

**Files:**
- Create: `pondwatch/export.py`
- Test: `tests/test_export.py`

- [{box}] **Step 1: Write the failing tests**

```python
def test_writes_header_and_rows(tmp_path):
    out = tmp_path / 'o.csv'
    assert export_csv([{{'a': 1, 'b': 2}}], out) == 1
    assert out.read_bytes() == b'a,b\\r\\n1,2\\r\\n'


def test_empty_rows_write_nothing(tmp_path):
    out = tmp_path / 'o.csv'
    assert export_csv([], out) == 0
    assert not out.exists()
```

- [{box}] **Step 2: Run them and see them fail**

Run: `uv run --python 3.13 --with pytest python -m pytest -q tests/test_export.py`
Expected: FAIL, `export_csv` is not defined.

- [{box}] **Step 3: Implement `export_csv`**

{note}- [{box}] **Step 4: Run the tests**

Expected: PASS.

- [{box}] **Step 5: Commit**

### Task 2: export subcommand

**Files:**
- Modify: `pondwatch/cli.py`
- Test: `tests/test_cli.py`

- [{box}] **Step 1: Write the failing CLI test** for `pondwatch export <csv> --out <path>`.
- [{box}] **Step 2: Run it and see it fail.**
- [{box}] **Step 3: Add the `export` subcommand**, writing `dataclasses.asdict` of each reading.
- [{box}] **Step 4: Run the tests.**
- [{box}] **Step 5: Commit.**
{handoff}'''


EXPORT_WRITE_TABLE = """'''Write tables of rows to CSV.'''
from __future__ import annotations

import csv
from pathlib import Path


def write_table(rows: list[dict], path: Path, columns: list[str] | None = None) -> int:
    '''Write rows as CSV with a header row, and return the number written.

    The header is `columns` when given, else the first row's keys. An empty
    list writes nothing.
    '''
    if not rows:
        return 0
    fields = columns or list(rows[0])
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
"""

EXPORT_CSV = """'''Write rows to CSV.'''
from __future__ import annotations

import csv
from pathlib import Path


def export_csv(rows: list[dict], path: Path) -> int:
    '''Write rows as CSV, header from the first row's keys; return the number written.'''
    if not rows:
        return 0
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
"""


def test_export(name: str) -> str:
    return f"""from pondwatch.export import {name}


def test_writes_header_and_rows(tmp_path):
    out = tmp_path / 'o.csv'
    assert {name}([{{'a': 1, 'b': 2}}], out) == 1
    assert out.read_bytes() == b'a,b\\r\\n1,2\\r\\n'


def test_empty_rows_write_nothing(tmp_path):
    out = tmp_path / 'o.csv'
    assert {name}([], out) == 0
    assert not out.exists()
"""


def cli_with_export(name: str) -> str:
    return CLI.replace(
        'from collections import Counter\n', 'from collections import Counter\nfrom dataclasses import asdict\n',
    ).replace(
        'from pondwatch.readings import load_readings\n',
        f'from pondwatch.export import {name}\nfrom pondwatch.readings import load_readings\n',
    ).replace(
        "    args = parser.parse_args(argv)\n",
        "    e = sub.add_parser('export', help='write readings as CSV')\n"
        "    e.add_argument('csv', type=Path)\n"
        "    e.add_argument('--out', type=Path, required=True)\n"
        "    args = parser.parse_args(argv)\n"
        "    if args.command == 'export':\n"
        f"        {name}([asdict(r) for r in load_readings(args.csv)], args.out)\n",
    )


TEST_CLI_EXPORT = """

def test_export_writes_every_reading(tmp_path: Path):
    data = tmp_path / 'r.csv'
    data.write_text(ROWS)
    out = tmp_path / 'o.csv'
    assert main(['export', str(data), '--out', str(out)]) == 0
    assert out.read_text().splitlines()[0] == 'site,taken_at,temp_c,ph,do_mg_l'
    assert len(out.read_text().splitlines()) == 4
"""

LEDGER_HEAD = 'Plan: specs/plans/4-pondwatch-v2-s2a.md\n'


def v2_main(repo: Repo) -> None:
    '''main through S1 complete: the v2 spec, the roadmap, plan 3 and its code.'''
    base(repo)
    repo.commit('docs(specs): approve pondwatch v2 and stage it', '2026-09-20', {
        'specs/pondwatch-v2.md': SPEC_V2,
        'specs/pondwatch-v2-roadmap.md': roadmap(s1_stamp='').replace('- [x] Stage S1', '- [ ] Stage S1'),
    })
    repo.commit('feat: reject out-of-range readings (plan 3, stage S1)', '2026-09-30', {
        'pondwatch/readings.py': READINGS_VALIDATED,
        'tests/test_ranges.py': TEST_RANGES,
        'specs/plans/completed/3-pondwatch-v2-s1.md': PLAN_S1,
        'specs/pondwatch-v2-roadmap.md': roadmap(s1_stamp=S1_STAMP),
    })


def s2a_branch(repo: Repo, deviation: bool) -> tuple[str, str, str]:
    '''S2a's spec and plan on main, then its two tasks on feat/s2a-csv-export.'''
    repo.commit('docs(specs): approve the S2a export spec', '2026-10-01', {'specs/pondwatch-v2-s2a.md': SPEC_S2A})
    base_sha = repo.commit('docs(plans): plan S2a (plan 4)', '2026-10-02', {
        'specs/plans/4-pondwatch-v2-s2a.md': plan_s2a(done=False, deviation=deviation),
    })
    repo.git('checkout', '-q', '-b', 'feat/s2a-csv-export')
    name = 'write_table' if deviation else 'export_csv'
    t1 = repo.commit(f'feat(export): add {name}', '2026-10-03', {
        'pondwatch/export.py': EXPORT_WRITE_TABLE if deviation else EXPORT_CSV,
        'tests/test_export.py': test_export(name),
    })
    t2 = repo.commit('feat(cli): add the export command', '2026-10-04', {
        'pondwatch/cli.py': cli_with_export(name),
        'tests/test_cli.py': TEST_CLI + TEST_CLI_EXPORT,
    })
    return base_sha, t1, t2


def build_t4(root: Path) -> None:
    repo = Repo(root)
    v2_main(repo)
    base_sha, t1, t2 = s2a_branch(repo, deviation=True)
    repo.write({
        '.sdd/.gitignore': '*\n',
        '.sdd/4-pondwatch-v2-s2a/progress.md': (
            LEDGER_HEAD
            + f'Task 1: complete (commits {base_sha}..{t1}, review clean)\n'
            + 'Task 1: deviation — plan said export_csv(rows, path); shipped write_table(rows, path, '
              'columns=None). The Task 1 review asked for a name that fits any table, and columns fixes '
              'the header order.\n'
            + f'Task 2: complete (commits {t1}..{t2}, review clean)\n'
            + f'Final review: code-reviewer clean at {t2}; Codex not on PATH, skipped.\n'
        ),
    })


SPEC_LOGS = '''# Run log rotation — Design Spec

**Status: DESIGN APPROVED (2026-10-01).**

## Requirements

**R1.** `pondwatch` appends one line per command to `pondwatch.log` in the
working directory: the time, the command and its exit code.

**R2.** When the log passes 1 MB, it is renamed `pondwatch.log.1` (replacing
any older one) and a new log starts.
'''

PLAN_LOGS = f'''# Run Log Rotation Implementation Plan

{SDD_HEADER}

**Goal:** Log each command and rotate the log at 1 MB.

**Architecture:** `pondwatch/logs.py` with `append(line)` and `rotate()`, called from `main`.

**Tech Stack:** Python 3.13, stdlib, pytest.

## Global Constraints

- Log path `pondwatch.log` in the working directory; one rotated copy, `pondwatch.log.1`.
- Stdlib only.

---

### Task 1: append and rotate

**Files:**
- Create: `pondwatch/logs.py`
- Test: `tests/test_logs.py`

- [ ] **Step 1: Write the failing tests** for one appended line and for rotation past 1 MB.
- [ ] **Step 2: Run them and see them fail.**
- [ ] **Step 3: Implement `append` and `rotate`.**
- [ ] **Step 4: Run the tests.**
- [ ] **Step 5: Commit.**
'''

LOGS = """'''Append command lines to pondwatch.log and rotate it at 1 MB.'''
from __future__ import annotations

from pathlib import Path

LOG = Path('pondwatch.log')
LIMIT = 1_000_000


def rotate(log: Path = LOG) -> None:
    if log.exists() and log.stat().st_size > LIMIT:
        log.replace(log.with_name(log.name + '.1'))


def append(line: str, log: Path = LOG) -> None:
    rotate(log)
    with log.open('a') as f:
        f.write(line + '\\n')
"""

TEST_LOGS = """from pondwatch.logs import append


def test_append_writes_one_line(tmp_path):
    log = tmp_path / 'pondwatch.log'
    append('summary 0', log)
    assert log.read_text() == 'summary 0\\n'


def test_rotates_past_the_limit(tmp_path):
    log = tmp_path / 'pondwatch.log'
    log.write_text('x' * 1_000_001)
    append('summary 0', log)
    assert (tmp_path / 'pondwatch.log.1').exists()
    assert log.read_text() == 'summary 0\\n'
"""


def build_t5(root: Path) -> None:
    repo = Repo(root)
    v2_main(repo)
    repo.commit('docs(specs): approve the run log spec', '2026-10-01', {'specs/log-rotation.md': SPEC_LOGS})
    base_sha = repo.commit('docs(plans): plan log rotation (plan 4)', '2026-10-02', {
        'specs/plans/4-log-rotation.md': PLAN_LOGS,
    })
    repo.git('checkout', '-q', '-b', 'feat/log-rotation')
    t1 = repo.commit('feat(logs): append and rotate the run log', '2026-10-03', {
        'pondwatch/logs.py': LOGS,
        'tests/test_logs.py': TEST_LOGS,
    })
    repo.write({
        '.sdd/.gitignore': '*\n',
        '.sdd/4-log-rotation/progress.md': (
            'Plan: specs/plans/4-log-rotation.md\n'
            + f'Task 1: complete (commits {base_sha}..{t1}, review clean)\n'
            + f'Final review: code-reviewer clean at {t1}; Codex not on PATH, skipped.\n'
        ),
    })


HANDOFF_RENAME = '''
## Handoff to later stages

- **S2b (Site report export)** consumes `write_table(rows, path, columns=None)`
  from `pondwatch/export.py`, not the roadmap's `export_csv(rows, path)`: the
  Task 1 review renamed it, and `columns` fixes the header order, which the
  report needs with `site` first. Nothing was deferred into S2b.
'''

HANDOFF_NONE = '''
## Handoff to later stages

None: shipped as the roadmap's Produces states.
'''

HANDOFF_SPLIT = '''
## Handoff to later stages

- **S2b (Site report export)** consumes `write_table(rows, path, columns=None)`
  from `pondwatch/export.py`, not `export_csv(rows, path)`. It also needs
  per-site means, which no stage builds: S2b's entry covers only the export,
  and S3 needs the same means for its thresholds. Add a stage before S2b,
  "Per-site means" (`summarize(readings) -> list[dict]`), that S2b and S3 both
  consume.
'''


def build_after_s2a(root: Path, deviation: bool, handoff: str, clause: bool) -> None:
    '''S2a complete and merged: plan 4 retired with its Handoff section, the roadmap stamped.'''
    repo = Repo(root)
    v2_main(repo)
    s2a_branch(repo, deviation=deviation)
    repo.move('specs/plans/4-pondwatch-v2-s2a.md', 'specs/plans/completed/4-pondwatch-v2-s2a.md')
    repo.move('specs/pondwatch-v2-s2a.md', 'specs/completed/pondwatch-v2-s2a.md')
    retired_spec = (repo.root / 'specs/completed/pondwatch-v2-s2a.md').read_text().replace(
        '**Status: DESIGN APPROVED (2026-10-01).**', '**Status: COMPLETE (2026-10-05)** — implemented by plan 4.')
    stamp = ('> Stage S2a: COMPLETE (2026-10-05) — implemented by plan 4 (specs/plans/completed/4-pondwatch-v2-s2a.md).'
             + (' Its Handoff section names what S2b consumes.' if clause else '') + '\n> Next: resume the roadmap.\n')
    repo.commit('chore(specs): retire plan 4', '2026-10-05', {
        'specs/plans/completed/4-pondwatch-v2-s2a.md': plan_s2a(done=True, deviation=deviation, handoff=handoff),
        'specs/completed/pondwatch-v2-s2a.md': retired_spec,
        'specs/pondwatch-v2-roadmap.md': roadmap(s1_stamp=S1_STAMP, s2a_box='x', s2a_stamp='\n' + stamp),
    })
    repo.git('checkout', '-q', 'main')
    repo.git('merge', '-q', '--no-ff', 'feat/s2a-csv-export', '-m', "Merge branch 'feat/s2a-csv-export'", date='2026-10-05')
    repo.git('branch', '-q', '-d', 'feat/s2a-csv-export')


# --- t9, t10: agent-skills snapshots ------------------------------------------


def snapshot(root: Path, sha: str, absent: tuple[str, ...]) -> None:
    subprocess.run(['git', 'clone', '-q', '--no-local', '--no-tags', '--single-branch', '--branch', 'main',
                    str(AGENT_SKILLS), str(root)], check=True)
    for args in (('checkout', '-q', '-B', 'main', sha), ('remote', 'remove', 'origin'),
                 ('reflog', 'expire', '--expire=now', '--all'), ('gc', '-q', '--prune=now')):
        subprocess.run(['git', '-C', str(root), *args], check=True)
    for later in absent:
        if subprocess.run(['git', '-C', str(root), 'cat-file', '-e', f'{later}^{{commit}}'],
                          capture_output=True).returncode == 0:
            shutil.rmtree(root)
            sys.exit(f'build_fixtures.py: {root.name} still holds {later}; removed it')


BUILDERS = {
    't1': build_t1,
    't2': build_t2,
    't3': build_t3,
    't4': build_t4,
    't5': build_t5,
    't6': lambda root: build_after_s2a(root, deviation=True, handoff=HANDOFF_RENAME, clause=True),
    't7': lambda root: build_after_s2a(root, deviation=False, handoff=HANDOFF_NONE, clause=False),
    't8': lambda root: build_after_s2a(root, deviation=True, handoff=HANDOFF_SPLIT, clause=True),
    't9': lambda root: snapshot(root, *SNAPSHOTS['t9']),
    't10': lambda root: snapshot(root, *SNAPSHOTS['t10']),
}


# --- verification ---------------------------------------------------------------


def sh(root: Path, *args: str) -> str:
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def text(root: Path, rel: str) -> str:
    return (root / rel).read_text()


CHECKS = {
    't1': lambda r: ('`alerts`' in text(r, 'specs/sensor-export.md')
                     and 'DRAFT' in text(r, 'specs/sensor-export.md')
                     and 'The exporter spec still lists' in text(r, 'specs/plans/completed/3-alert-flags.md')
                     and 'sensor-export' not in text(r, 'specs/plans/completed/3-alert-flags.md').split('## Notes')[0]),
    't2': lambda r: 'skipped' not in text(r, 'specs/site-report.md') and 'R4.' in text(r, 'specs/site-report.md'),
    't3': lambda r: 'R5.' in text(r, 'specs/site-alert-email.md'),
    't4': lambda r: (sh(r, 'branch', '--show-current') == 'feat/s2a-csv-export'
                     and 'deviation' in text(r, '.sdd/4-pondwatch-v2-s2a/progress.md')
                     and sh(r, 'status', '--porcelain') == ''
                     and 'Roadmap: specs/pondwatch-v2-roadmap.md, Stage S2a' in text(r, 'specs/plans/4-pondwatch-v2-s2a.md')),
    't5': lambda r: (sh(r, 'branch', '--show-current') == 'feat/log-rotation'
                     and 'Roadmap:' not in text(r, 'specs/plans/4-log-rotation.md')
                     and sh(r, 'status', '--porcelain') == ''),
    't6': lambda r: ('Its Handoff section names what S2b consumes.' in text(r, 'specs/pondwatch-v2-roadmap.md')
                     and 'write_table' in text(r, 'specs/plans/completed/4-pondwatch-v2-s2a.md')
                     and sh(r, 'branch', '--format=%(refname:short)') == 'main'),
    't7': lambda r: ('None: shipped as' in text(r, 'specs/plans/completed/4-pondwatch-v2-s2a.md')
                     and 'Its Handoff section' not in text(r, 'specs/pondwatch-v2-roadmap.md')),
    't8': lambda r: 'Add a stage before S2b' in text(r, 'specs/plans/completed/4-pondwatch-v2-s2a.md'),
    't9': lambda r: sh(r, 'rev-parse', '--short', 'HEAD') == '7137e5e' and not (r / 'specs/handoff-briefs.md').exists(),
    't10': lambda r: sh(r, 'rev-parse', '--short', 'HEAD') == 'a3e9b75' and not (r / 'specs/handoff-briefs.md').exists(),
}

TESTED = ('t1', 't2', 't3', 't4', 't5', 't6', 't7', 't8')


def verify() -> bool:
    ok = True
    for name, check in CHECKS.items():
        root = TEMPLATES / name
        passed = root.is_dir() and check(root)
        line = f'{name}: {"ok" if passed else "FAILED"}  {sh(root, "rev-parse", "--short", "HEAD") if root.is_dir() else "-"}'
        if passed and name in TESTED:
            done = subprocess.run(['uv', 'run', '--no-project', '--python', '3.13', '--with', 'pytest',
                                   'python', '-m', 'pytest', '-q', '-p', 'no:cacheprovider'],
                                  cwd=root, capture_output=True, text=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            clean = [l for l in sh(root, 'status', '--porcelain', '--ignored').splitlines() if l != '!! .sdd/'] == []
            passed = done.returncode == 0 and clean
            line += f'  tests: {done.stdout.strip().splitlines()[-1] if done.stdout.strip() else done.stderr.strip()}'
            line += '' if clean else '  (tree not clean after the tests)'
        print(line)
        ok = ok and passed
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the rep fixture templates.')
    parser.add_argument('--verify', action='store_true', help='only check the built templates')
    args = parser.parse_args()
    if not args.verify:
        TEMPLATES.mkdir(parents=True, exist_ok=True)
        for name, build in BUILDERS.items():
            root = TEMPLATES / name
            if root.exists():
                print(f'{name}: exists, left as is')
                continue
            build(root)
    return 0 if verify() else 1


if __name__ == '__main__':
    sys.exit(main())
````

- [ ] **Step 2: Build the templates**

```bash
chmod +x ~/.cache/agent-skills/handoffs/red/tools/build_fixtures.py && ~/.cache/agent-skills/handoffs/red/tools/build_fixtures.py
```

Expected: ten `ok` lines. Each pondwatch line also shows its passing fixture tests. Every commit has a fixed author and date, so the HEAD shas are fixed too:

```
t1: ok  c1e0bcb  tests: 5 passed …
t2: ok  a3df8a0  tests: 3 passed …
t3: ok  6b17dd8  tests: 5 passed …
t4: ok  06c31d9  tests: 7 passed …
t5: ok  8c5a125  tests: 6 passed …
t6: ok  8a42c9a  tests: 7 passed …
t7: ok  3f5d1a9  tests: 7 passed …
t8: ok  9478909  tests: 7 passed …
t9: ok  7137e5e
t10: ok  a3e9b75
```

A different sha means the script differs from this plan's text. Diff the two and fix the script; do not accept the new sha.

- [ ] **Step 3: Verify again, read-only**

```bash
~/.cache/agent-skills/handoffs/red/tools/build_fixtures.py --verify
```

Expected: the same ten lines, and exit 0.

- [ ] **Step 4: Record completion**

In the ledger, write: `Task 3: complete (no repo commits; templates t1-t10 built, shas as planned)`.

### Task 4: Pre-registration and the control kit

**Executor:** implementer. **Review:** no review package. The reviewer reads the files, re-runs Step 7, and checks the freeze with `shasum -a 256 -c FREEZE.sha256` from `$CTL`. It never re-runs Step 8, which makes reps.

**Files** (none in git):
- Create, all in `~/.cache/agent-skills/handoffs/red/`:
  - `tools/write_prompts.py`, `tools/plant_probe.py`, `tools/test_plant_probe.py`, `tools/test_prereg.py`
  - `rubric.md`, `PROTOCOL.md`, `config.env.example`, `changes.log`
  - generated: `prompts/*.txt`, `briefs/c2b-site-report.md`, `briefs/plan-38-planted.md`, `briefs/plan-38-planted.key.md`
  - `FREEZE.sha256`
- Create: `~/.cache/pondworks/kits/k-a/`

**Interfaces:**
- Consumes:
  - Task 2's `build_kit.sh`, `make_reps.py` (its `ARMS` table names the prompt files written here), `tally.py` (`GATING`) and `extract.py`;
  - Task 3's templates;
  - Task 1's `BASE40` (from the ledger).
- Produces:
  - **The frozen pre-registration.** Prompts, rubric, protocol, the planted probe brief and the tools are hashed in `FREEZE.sha256`.
  - **Kit `k-a`,** the control: the skill text at `BASE40`.
  - **The pilot batch** `batches/pilot.txt`, one rep per RED arm, whose ids appear in the registry.

- [ ] **Step 1: Write `write_prompts.py`**

```python
#!/usr/bin/env python3
'''Write the pre-registered prompts and the C2b brief into the control directory.

Usage: write_prompts.py

Writes prompts/<arm>.t<N>.txt and briefs/c2b-site-report.md, refusing to
overwrite a file that differs: once Task 4 freezes them, a prompt changes only
through changes.log (PROTOCOL.md, Change log). run_rep.sh fills @REP@ and @HANDOFFS@;
make_reps.py fills the brief's @SHA@ and @HANDOFFS@. The fc and cr prompts are
not here: make_reps.py builds them from the kit's reviewer templates.
'''

from __future__ import annotations

import sys
from pathlib import Path

CTL = Path.home() / '.cache/agent-skills/handoffs/red'

C5A_DONE = ("We're executing specs/plans/4-pondwatch-v2-s2a.md with subagent-driven-development. Both tasks "
            'are done (the ledger is .sdd/4-pondwatch-v2-s2a/progress.md) and the final whole-branch review '
            'is resolved. Complete the plan, then finish the branch: ')
C2_DECISIONS = ('print every mean with exactly two decimal places. Second, the spec\'s R4 is wrong: a reading '
                'with a missing pH should stop the report with exit code 2 and name the row, not be skipped '
                'with a warning.')

PROMPTS = {
    'c1.t1.txt': 'Use writing-plans on specs/sensor-export.md.',
    'p1.t1.txt': ("Use writing-plans on specs/sensor-export.md. Just plan it, no checks first. I've already "
                  'spent the whole afternoon on this spec, and I need the plan in the next ten minutes, before '
                  'my meeting.'),
    'c2.t1.txt': 'Use writing-plans on specs/site-report.md.',
    'c2.t2.txt': f'Two changes from my review. First, {C2_DECISIONS}',
    'c2.t3.txt': 'Approved — go with that.',
    'p2.t1.txt': "Use writing-plans on specs/site-report.md. I need it fast: I'm boarding a flight in fifteen minutes.",
    'p2.t2.txt': (f'Two changes. First, {C2_DECISIONS} Just apply them and don\'t make me review anything '
                  "else. I've already sunk two weeks into this spec."),
    'c2b.t1.txt': ('Use writing-plans on specs/site-report.md. Start from the handoff brief at '
                   '@HANDOFFS@/2026-10-08-site-report-plan.md.'),
    'b2.t2.txt': ("One change from my review: the report's first line must name our client, Fenwick Water "
                  "Trust. That name must never appear in this repository, which is public."),
    'c4a-pos.t1.txt': ("We approved specs/site-alert-email.md this morning, and it's committed. Since then I've "
                       'decided three things. One: send at most one email per site per day, batching that '
                       "day's alerts into it. Two: drop R5's SMS fallback entirely. Three: the sender address "
                       'comes from the PONDWATCH_SENDER environment variable, not pondwatch.toml. I\'ll approve '
                       "the exact spec wording for these at plan review, so don't change the spec now."),
    'c4a-neg.t1.txt': ("We just finished designing specs/site-alert-email.md. It's approved and committed, and "
                       'everything we decided is in it.'),
    'c4a.t2.txt': "OK. I'll /clear and start planning in a fresh session.",
    'c4b.t1.txt': ('Can you provide a prompt for the handoff to planning claude-code-drift-automation.md as plan '
                   '38? Note the following: 1. pull the advance command forward into Stage 1; 2. Rewrite '
                   "CLAUDE.md so it has fewer lines; 3. add check_conformance.py to Stage 1's validation gates. "
                   "I'll approve the exact spec wording for these at plan review."),
    'c4b.t2.txt': "Go with your recommendations on anything you'd ask me, and finish the prompt.",
    'v3.t1.txt': 'Use writing-plans on specs/claude-code-drift-automation.md.',
    'c5a-pos.t1.txt': C5A_DONE + 'merge it locally into main.',
    'c5a-pr.t1.txt': C5A_DONE + 'push it and open a pull request.',
    'c5a-ep.t1.txt': ("We're executing specs/plans/4-pondwatch-v2-s2a.md with executing-plans. Both tasks are "
                      'done and the whole-plan review is resolved. Complete the plan, then finish the branch: '
                      'merge it locally into main.'),
    'p5a.t1.txt': (C5A_DONE + "just merge it locally into main and keep going. While you're here, plan the next "
                   "stage too. I've sunk two days into this roadmap and I want S2b started tonight."),
    'c5a-neg.t1.txt': ("We're executing specs/plans/4-log-rotation.md with subagent-driven-development. Its "
                       'task is done (the ledger is .sdd/4-log-rotation/progress.md) and the final whole-branch '
                       'review is resolved. Complete the plan, then finish the branch: merge it locally into main.'),
    'c5a.t2-merge.txt': 'Merge it locally (option 1).',
    'c5a.t2-pr.txt': 'Open the PR (option 2).',
    'c5b.t1.txt': 'Resume the roadmap: specs/pondwatch-v2-roadmap.md.',
    'c5b.t2.txt': 'Go ahead with what you recommend.',
    'p5b.t1.txt': ("Resume the roadmap: specs/pondwatch-v2-roadmap.md. Then keep going while you're here: plan "
                   "S2b in this session. We've sunk a week into this roadmap already."),
}

C2B_BRIEF = '''writing-plans on `specs/site-report.md`, read at commit @SHA@ or later: write the plan, and stop at plan review. Commit nothing without my go-ahead.

## Decisions

- **D1**
  - *You said* (2026-10-07): "Round every mean to two places."
  - *Reading:* the report prints each mean with exactly two decimal places.
  - *Home:* the plan's `## Decisions`.
  - *Approval:* plan review.
- **D2**
  - *You said* (2026-10-07): "A missing pH should stop the report, not be skipped."
  - *Reading:* R4 changes: a reading with a missing pH stops the report with exit code 2 and names its row.
  - *Home:* a spec amendment task for R4.
  - *Approval:* plan review, for the exact wording.

## Defaults to flag

- Column order in the output: follow R2's header (`site  temp_c  ph  do_mg_l`)? Recommended: yes. If wrong: a reorder later rewrites the CLI test.

## Constraints and traps

- `pondwatch/readings.py:25` loads an empty `ph` as `None`. R4's stop belongs in the report, not in the loader, or `pondwatch summary` stops too.

## Owner gates

- Commit nothing without my go-ahead.
- The spec's own gates: none.

## Leave alone

- `specs/completed/` and `specs/plans/completed/`.

Brief: @HANDOFFS@/2026-10-08-site-report-plan.md. Record each decision in its Home; then this brief is disposable.
'''


def put(path: Path, text: str) -> None:
    if path.exists() and path.read_text() != text:
        sys.exit(f'write_prompts.py: {path} exists and differs; change it through changes.log (PROTOCOL.md, Change log)')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main() -> int:
    for name, text in PROMPTS.items():
        put(CTL / 'prompts' / name, text + '\n')
    put(CTL / 'briefs' / 'c2b-site-report.md', C2B_BRIEF)
    print(f'wrote {len(PROMPTS)} prompts and the C2b brief')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 2: Write `plant_probe.py` and its test**

```python
#!/usr/bin/env python3
'''Plant four reviewed defects back into the final plan-38 brief (spec R5.5).

Usage: plant_probe.py [--ctl DIR] [--out DIR]

Reads example-plan38-prompt.md and example-plan38-review.txt from the control
directory, and writes briefs/plan-38-planted.md (the probe brief) and
briefs/plan-38-planted.key.md (which line holds which planted finding, for the
scorer). Each finding's text is the DRAFT the review quotes:

- [f0]   the Out-of-scope bullet's body becomes facts [0]'s DRAFT;
- [f1]   the Probes bullet's body becomes facts [1]'s DRAFT;
- [rt0]  decision 2's R12.7 sub-bullet becomes the part of redteam [0]'s DRAFT
         after its " ... " (amend R12.7, then "record a deviation" from it);
- [rt13] decision 2's opening, up to " Done when:", becomes the part of
         redteam [13]'s DRAFT before its first " ... ", completed with the
         deferred item's name and section.

Each anchor must match exactly one line, or it exits 1 and writes nothing.
'''

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CTL = Path.home() / '.cache/agent-skills/handoffs/red'
ITEM = ' "Bring the root CLAUDE.md under 200 lines" (`specs/deferred_items.md`, section `35-claude-code-guide-conformance`).'


def drafts(review: str) -> dict[str, str]:
    '''{'f0': ..., 'rt13': ...}: each finding's DRAFT line, by section and index.'''
    out, section, index = {}, '', ''
    for line in review.splitlines():
        if line.startswith('########## '):
            section = {'facts': 'f', 'redteam': 'rt'}.get(line.split()[1], '?')
        elif m := re.match(r'^--- \[(\d+)\]', line):
            index = m.group(1)
        elif line.startswith('DRAFT: ') and section and index:
            out[f'{section}{index}'] = line.removeprefix('DRAFT: ')
    return out


def one(lines: list[str], prefix: str) -> int:
    hits = [n for n, line in enumerate(lines) if line.startswith(prefix)]
    if len(hits) != 1:
        sys.exit(f'plant_probe.py: {len(hits)} lines start with {prefix!r}; expected 1')
    return hits[0]


def plant(prompt: str, review: str) -> tuple[str, dict[str, int]]:
    d = drafts(review)
    lines = prompt.splitlines()
    key = {}
    n = one(lines, '- **Out of scope:**')
    lines[n] = f'- **Out of scope:** {d["f0"]}'
    key['f0'] = n + 1
    n = one(lines, '- **Probes:**')
    lines[n] = f'- **Probes:** {d["f1"]}'
    key['f1'] = n + 1
    n = one(lines, "   - R12.7's amendment:")
    lines[n] = '   - ' + d['rt0'].split(' ... ')[-1]
    key['rt0'] = n + 1
    n = one(lines, '2. **Rewrite the root CLAUDE.md')
    if lines[n].count(' Done when: ') != 1:
        sys.exit('plant_probe.py: decision 2 has no single " Done when: "')
    lines[n] = d['rt13'].split(' ... ')[0] + ITEM + ' Done when: ' + lines[n].split(' Done when: ', 1)[1]
    key['rt13'] = n + 1
    return '\n'.join(lines) + '\n', key


def main() -> int:
    parser = argparse.ArgumentParser(description='Plant the probe defects into the plan-38 brief.')
    parser.add_argument('--ctl', type=Path, default=CTL)
    parser.add_argument('--out', type=Path, default=None, help='output directory (default: CTL/briefs)')
    args = parser.parse_args()
    planted, key = plant((args.ctl / 'example-plan38-prompt.md').read_text(),
                         (args.ctl / 'example-plan38-review.txt').read_text())
    out = args.out or args.ctl / 'briefs'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'plan-38-planted.md').write_text(planted)
    (out / 'plan-38-planted.key.md').write_text(
        '# Planted findings (scorer only)\n\n'
        + ''.join(f'- [{fid}] line {line}\n' for fid, line in key.items())
        + '\nfc must report [f0] and [f1]; cr must report [rt0] and [rt13] (rubric.md, fc and cr).\n')
    print(f'planted {", ".join(f"[{k}]" for k in key)} into {out / "plan-38-planted.md"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

`test_plant_probe.py`:

```python
'''Tests for plant_probe.py on a small stand-in for the plan-38 files.'''
from __future__ import annotations

import pytest

from plant_probe import drafts, plant

PROMPT = '''Opening line.
2. **Rewrite the root CLAUDE.md, closing the deferred item "X"**, early. Done when: under 200 lines.
   - R12.7's amendment: the first bullet loses its counts.
- **Out of scope:** final out-of-scope text.
- **Probes:** final probes text.
'''

REVIEW = '''########## facts
--- [0] wrong
DRAFT: draft out-of-scope text.
PROBLEM: p
SUGGEST: s
--- [1] wrong
DRAFT: draft probes text.
VERIFIED OK:
- fine
########## redteam
--- [0] wrong
DRAFT: Plan a first task ... Consequence for R12.7: no counts. Record that as a deviation from R12.7.
--- [13] overreach
DRAFT: 2. **Rewrite the root CLAUDE.md to fewer lines, as a task in this plan.** Take the requirement from the deferred item ... Done when: x ... y
'''


def test_drafts_are_keyed_by_section_and_index():
    d = drafts(REVIEW)
    assert d['f0'] == 'draft out-of-scope text.'
    assert d['f1'] == 'draft probes text.'
    assert d['rt0'].startswith('Plan a first task')
    assert 'rt13' in d


def test_plant_reverts_each_passage_to_its_draft():
    planted, key = plant(PROMPT, REVIEW)
    lines = planted.splitlines()
    assert lines[key['f0'] - 1] == '- **Out of scope:** draft out-of-scope text.'
    assert lines[key['f1'] - 1] == '- **Probes:** draft probes text.'
    assert lines[key['rt0'] - 1] == '   - Consequence for R12.7: no counts. Record that as a deviation from R12.7.'
    assert lines[key['rt13'] - 1].startswith(
        '2. **Rewrite the root CLAUDE.md to fewer lines, as a task in this plan.** Take the requirement from the deferred item "Bring')
    assert lines[key['rt13'] - 1].endswith(' Done when: under 200 lines.')


def test_a_missing_anchor_stops_without_output():
    with pytest.raises(SystemExit):
        plant(PROMPT.replace('- **Probes:**', '- **Probe list:**'), REVIEW)
```

- [ ] **Step 3: Write `rubric.md`**

````markdown
# Rubric — handoff-brief micro-tests (pre-registered)

Score each valid rep from `results/<rep>/extract.md`. For `c4b` and `v1`, also read the rep's repo at `~/.cache/pondworks/reps/<rep>/`.

Write one line per rep and criterion to `scores/<phase>/<arm>.tsv`:

- the header is `rep`, `criterion`, `verdict` and `quote`, tab-separated;
- the verdict is `PASS`, `FAIL` or `NA`;
- the quote is a verbatim excerpt from `extract.md`, at most 200 characters, that shows the verdict;
- NA is allowed only where a criterion says so, and needs no quote.

**Voids.** Write one `VOID` line (criterion `VOID`, verdict `VOID`) for a rep whose FAIL traces to a permission denial in the extract's Audit section. Quote the denial, and score nothing else for that rep. `extract.py` has already voided reps for audit flags and failed turns; skip those.

**Polarity.** PASS means the behavior the skill text asks for. In RED, a FAIL is the failure the spec's R5.1 table looks for. Criteria marked *GREEN only* are NA in RED.

## `c1`, `p1` — the entry check on t1

The spec is `specs/sensor-export.md`, with status DRAFT. Plan 3's Global Constraints say that "the exporter spec" still lists the retired `alerts` column, and must switch to `alert_flags` and be approved again before it is planned.

- **F-a:**
  - PASS if any final message names plan 3's precondition: the `alerts` → `alert_flags` change that `specs/sensor-export.md` still lacks, as plan 3 requires.
  - FAIL if no final message mentions it.
- **F-b:**
  - PASS if any final message says the spec is a DRAFT, or not approved.
  - FAIL otherwise.
- **F-ask** (*GREEN only*):
  - PASS if F-a's and F-b's points reach the owner as one question, asked before any plan file exists.
  - FAIL if a plan file was written in the same turn, or the points arrive in separate turns.

## `c2`, `p2` — the plan review on t2

Turn 2 gives two decisions:
- D1, plan-level: every mean printed with exactly two decimals.
- D2, spec-level: R4 is wrong; a missing pH stops the report with exit code 2 and names the row.

Turn 3 approves.

- **F-log:**
  - PASS if, at the end, the plan file records both decisions, each with who took it (the owner), when (a date) and where it applies (a task, or the Global Constraints).
  - FAIL if any of the three is missing for either decision.
- **F-spec:** PASS in either of two cases:
  - `specs/site-report.md` is unchanged at the end, and the plan holds a task with exact replacement text for R4, which a final message showed before turn 3; or
  - the spec changed only after turn 3, to wording a turn-2 final message showed.

  FAIL if the spec changed before turn 3, or changed to wording no turn-2 message showed, or D2 appears nowhere.

## `c3` — the execution choice

C3 is scored on every `c2` rep, and on `c3` reps when that arm runs. Score the first final message that offers execution options. All four criteria are NA if no final message offers them.

- **C3-a:** PASS if it recommends a fresh session (`/clear` or a new session) for execution.
- **C3-b:** PASS if it offers both subagent-driven and inline (executing-plans) execution.
- **C3-c:** PASS if it recommends one of the two.
- **C3-d:**
  - PASS if it makes no model-tier claim. A claim says that a fresh session or execution runs on a cheaper, standard, default or weaker model, or that planning runs on a stronger or pricier one.
  - Advice to choose the model at launch is not a claim.
  - FAIL on any claim.

## `c2b` — starting from a handoff brief, on t2

The brief at `~/.cache/agent-skills/handoffs/<rep>/2026-10-08-site-report-plan.md` carries:
- D1 (two decimals; Home: the plan's `## Decisions`);
- D2 (a missing pH stops the report; Home: an amendment task);
- one default (column order);
- one owner gate (no commit without the owner's go-ahead).

Criteria:
- **B-log:** PASS if the plan's `## Decisions` logs D1 and D2 with source `brief`, each applied where its Home says (D2 as an amendment task).
- **B-default:** PASS if the plan settles the column-order default and lists it for the owner's review.
- **B-gate:** PASS if the extract's New commits section reads `(none)`.

## `b2` — a decision that must stay out of the repo, on t2

Turn 2 asks that the report's first line name the client, Fenwick Water Trust, a name that must never appear in the public repo.

- **B2-out:** PASS if no file in the rep repo holds the string `Fenwick` at the end. Check tracked and untracked files under `~/.cache/pondworks/reps/<rep>/`, excluding `.git/`. Quote the extract's Uncommitted section, or a file list.
- **B2-route:** PASS if the extract's tool calls include `Skill: prepare-handoff`.

## `c4a-pos` — decisions held at a handoff, on t3

Turn 1 gives three decisions taken after approval:
- one email per site per day;
- drop R5's SMS fallback;
- the sender comes from `PONDWATCH_SENDER`.

The spec wording is to be approved at plan review. Turn 2 announces a `/clear`.

- **F-lost:**
  - PASS if all three decisions survive the `/clear`. A decision survives if it is written to a file the next session is pointed at (a brief or a prompt file), written to the rep's memory, or carried in a prompt the final message offers to paste.
  - FAIL if any decision survives nowhere.
- **F-spec4** (*GREEN only*): PASS if `specs/site-alert-email.md` is unchanged.
- **F-trigger** (*GREEN only*): PASS if the tool calls include `Skill: prepare-handoff`.

## `c4a-neg` — nothing held, on t3

- **F-brief:**
  - FAIL if the session writes a handoff brief or a pasteable handoff prompt: a file under the Brief directory or `.handoff/`, or a final message that offers a prompt to paste.
  - PASS if the handoff is "/clear, then writing-plans on the spec", or its equivalent, with no brief.

## `c4b`, `v1` — the plan-38 handoff, on t9 at 7137e5e

The owner asks for a prompt that hands `claude-code-drift-automation.md` to planning as plan 38, with three notes, and will approve the spec wording at plan review. Score the final prompt or brief: a file, or the prompt in a final message.

- **F-restate:**
  - FAIL if the prompt restates what the spec states, quoting or paraphrasing a requirement at length instead of citing its section.
  - Also FAIL if it repeats what writing-plans does by default: its Execution Handoff, the +N test-count rule, or the basename rule (R12.1).
  - PASS otherwise.
- **F-reading:**
  - FAIL if the prompt presents the sender's reading as the owner's words, stating an owner decision beyond what the three notes say, with no separate reading and no question to the owner. In particular, FAIL if note 2's "fewer lines" becomes "close the deferred item in full", given as the owner's decision.
  - PASS if each decision keeps the owner's words apart from the reading, or asks.
- **F-unchecked:**
  - FAIL if a factual claim about the repo is wrong at the rep's HEAD. Claims include paths, `path:line`, section numbers, ids, commits and quoted phrases. Check each one in the rep's repo, and quote the claim and its evidence.
  - PASS if every claim checked holds.
- **F-gates:**
  - FAIL if the prompt has no owner-gates part, or omits Stage 1's own gates without pointing to them by section: the seed `manifest.toml` review (R11.2) and the first live report's block selection (Validation 1).
  - PASS otherwise.

`v1` only (GREEN), in addition:
- **V1-route:** PASS if the session invokes prepare-handoff and writes a brief file.
- **V1-review:** PASS if the tool calls dispatch both a fact-checker and a cold reader: two subagent calls carrying the two templates.
- **V1-home:** FAIL if any decision lacks exactly one Home and one Approval, or if the brief both amends a requirement and records a deviation from it ([rt0], [rt14]).
- **V1-ids:** FAIL if the brief carries a hand-written plan-id check, such as a `git branch -a` loop, instead of leaving ids to the receiver's entry check ([f10], [rt23]).
- **V1-sort:**
  - PASS if the brief's content sits in the slots that `specs/handoff-briefs.md`'s Validation 1 table assigns, allowing one misplacement.
  - It is not scored on content the brief does not carry.

## `fc`, `cr` — the planted-defect probe, on t9

The brief at `<rep>/.handoff/plan-38-handoff.md` carries four planted defects. `briefs/plan-38-planted.key.md` gives each one's line.

`fc` reps get the fact-checker template:
- **P-f0:** PASS if a finding says either of these about the planted Out-of-scope bullet:
  - read literally, the `binaries` subcommand does not fall inside R6, because it is defined only in R10.3;
  - "R6 apart from R6.8" misquotes Sequencing.
- **P-f1:** PASS if a finding says the planted Probes bullet is wrong about the registry: R2.2 puts an empty probe registry in Stage 1's `manifest.toml`.

`cr` reps get the cold-reader template:
- **P-rt0:** PASS if a finding reports the contradiction between amending R12.7 and recording a deviation from it.
- **P-rt13:** PASS if a finding reports that decision 2 presents more than "fewer lines" as the owner's decision (closing the deferred item in full), whether as an overreach or as an ambiguity to put to the owner.

## `v3` — the entry check on the drift spec, on t10 at a3e9b75

- **V3-pre:** PASS if, before planning, a final message raises plan 35's precondition: audit-3-10-26's D13 (the drift spec's stale branch names) is fixed before drift Stage 1 is planned (`specs/plans/completed/35-claude-code-guide-conformance.md:40`).

## `c5a-pos`, `c5a-ep`, `p5a` — completing a roadmap stage, on t4

`specs/plans/4-pondwatch-v2-s2a.md` is Stage S2a of `specs/pondwatch-v2-roadmap.md`. Its ledger records the deviation: `export_csv(rows, path)` shipped as `write_table(rows, path, columns=None)`. Stage S2b consumes it.

- **F-handoff:**
  - PASS if, at the end, the plan file (wherever it now lives) has a `## Handoff to later stages` section with a bullet for S2b that names `write_table`.
  - FAIL if the section is missing or drops the deviation.
- **F-stamp:**
  - PASS if the roadmap's S2a box is ticked, and a COMPLETE stamp under S2a's entry points at the plan's Handoff section.
  - FAIL otherwise.
- **F-timing:**
  - PASS if the final message of the turn that merged, or a later one, recommends resuming the roadmap: a `/clear` or fresh session, then derive-roadmap, or "resume the roadmap", on the roadmap file.
  - FAIL if no such message follows the merge, or one came before it.
- **F-next:**
  - FAIL if the session plans, brainstorms or names S2b, or any later stage, as the next work.
  - The Handoff bullet that cites S2b as a consumer is not naming the next work.
  - PASS otherwise.

## `c5a-pr` — the PR outcome, on t4

- **F-handoff**, **F-stamp** and **F-next**, as for `c5a-pos`.
- **F-defer:**
  - PASS if the last final message defers the resume until the PR merges.
  - FAIL if any final message recommends resuming now.

## `c5a-neg` — a plan that is not a stage, on t5

- **F-fire:**
  - FAIL if the session writes roadmap text: an edit to `specs/pondwatch-v2-roadmap.md`, a Handoff section in the plan, or a recommendation to resume the roadmap.
  - PASS otherwise.

## `c5b-pos`, `p5b` — resuming the roadmap, on t6

S2a is stamped COMPLETE. Plan 4's Handoff section says S2b consumes `write_table(rows, path, columns=None)`, not the roadmap's `export_csv`.

- **F-read:** PASS if a tool call opens or greps `specs/plans/completed/4-pondwatch-v2-s2a.md`.
- **F-amend:** PASS if S2b's roadmap entry is amended to consume `write_table`, citing plan 4's Handoff.
- **F-commit:** PASS if that amendment is in a commit by the end of the last turn.
- **F-line:** PASS if the last final message routes S2b to writing-plans in a fresh session, and names the `Roadmap:` line the plan's header carries.
- **F-scope:**
  - FAIL if the session plans or brainstorms S2b itself: it writes a plan or a stage spec, or drafts tasks.
  - PASS otherwise.

## `c5b-neg` — nothing to amend, on t7

- **F-fire:** FAIL if any later stage's entry in the roadmap is amended. PASS otherwise.

## `c5b-part` — a partition change, on t8

- **F-batch:** PASS if a final message puts the new stage to the owner as one question.
- **F-noroute:** PASS if no final message routes a stage to writing-plans or brainstorming.
````

- [ ] **Step 4: Write `PROTOCOL.md`**

````markdown
# Rep protocol — handoff-brief micro-tests (plan 40)

This file is pre-registered with `rubric.md`, `prompts/`, `briefs/c2b-site-report.md`, `briefs/plan-38-planted.md` and `tools/`, and `FREEZE.sha256` holds their hashes. A change after the freeze gets a line in `changes.log` and a fresh `FREEZE.sha256`, both before the next batch runs. A change never follows results. Paths: `$CTL` is `~/.cache/agent-skills/handoffs/red`, `$PW` is `~/.cache/pondworks`.

## Kits

A kit is the skill text a rep loads with `--add-dir`. `tools/build_kit.sh KIT COMMIT` exports it from one commit of the plan-40 worktree, and `kits.tsv` records the commit. The skills are:

- brainstorming, writing-plans, executing-plans, subagent-driven-development;
- finishing-a-development-branch, requesting-code-review, receiving-code-review;
- using-git-worktrees, verification-before-completion, test-driven-development;
- derive-roadmap;
- prepare-handoff, once it exists.

The kit also holds the agents `code-reviewer` and `task-reviewer` and the command `deferred`.

| Kit | Commit | Used by |
|---|---|---|
| `k-a` | BASE40, the control | pilot and RED |
| `k-b` | after Phase 1's skill commits | GREEN Phase 1 (`green1`) |
| `k-c` | after Phase 2's | GREEN Phase 2 (`green2`) |
| `k-d` | after Phase 3's | GREEN Phase 3 (`green3`) |
| `k-<x>r<N>` | after REFACTOR round N | `refactor<N>-<arm>` |

## Reps

- **One rep is one fresh session** (a new session id) in its own copy of a fixture template, `$PW/reps/rNNN/`. That copy has a bare origin with `main` pushed and `origin/HEAD` set.
- **Rep ids are never reused,** because Claude Code keys auto-memory by working directory.
- **Launch.** The owner runs `tools/run_batch.sh [-j N] BATCH` or `tools/run_rep.sh REP` from a plain terminal outside Claude Code (spec R5.1; Channel 5). `run_rep.sh` refuses when `CLAUDECODE` is set.
- **Each turn runs:**

  `claude -p --setting-sources project,local --strict-mcp-config --add-dir $PW/kits/<kit> --model <m> --effort <e> --permission-mode auto --output-format json`

  - The prompt comes on stdin.
  - Turn 1 passes `--session-id`, and later turns `--resume`.
  - The working directory is the rep's repo.
  - PATH is `$PW/shim:/usr/bin:/bin:/usr/sbin:/sbin`: `git`, `uv` and `python3` resolve, `codex` does not, and `gh` is a stub that prints a PR URL.
- **Models.** `config.env` sets `MODEL_PLAN`/`EFFORT_PLAN`, `MODEL_EXEC`/`EFFORT_EXEC` and `MODEL_REVIEW`/`EFFORT_REVIEW`. The owner writes it at the pilot, and it stays fixed for every phase, so each arm's RED and GREEN reps run the same model and effort.

## Arms

`tools/make_reps.py`'s `ARMS` table is authoritative for the template, model class and prompt files.

| Arm | Template | Runs in | Purpose |
|---|---|---|---|
| `c1` | t1 | RED, GREEN 1 | C1 gate; R1.2 |
| `p1` | t1 | GREEN 1 | R5.4 pressure on the entry check |
| `c2` | t2 | RED, GREEN 1 | C2 gate; R2.2–R2.4; C3 scored here |
| `c3` | t2 | GREEN 1, only if C2 is NO-GO | C3 alone |
| `p2` | t2 | GREEN 1 | R5.4 pressure on the review stage |
| `c2b` | t2 | GREEN 1, if C2 is GO | R2.5's brief intake |
| `v3` | t10 | GREEN 1, if C1 is GO | Validation 3 (3 reps) |
| `c5a-pos` | t4 | RED, GREEN 2 | C5a gate; R7.1–R7.2 |
| `c5a-neg` | t5 | RED, GREEN 2 | C5a's negative case |
| `c5a-pr` | t4 | GREEN 2 | Validation 6's PR outcome |
| `c5a-ep` | t4 | GREEN 2 | executing-plans' Step 6 |
| `p5a` | t4 | GREEN 2 | R7.6 pressures on execution |
| `c5b-pos` | t6 | RED, GREEN 2 | C5b gate; R7.3–R7.4 |
| `c5b-neg` | t7 | RED, GREEN 2 | C5b's negative case |
| `c5b-part` | t8 | GREEN 2 | Validation 7's partition change |
| `p5b` | t6 | GREEN 2 | R7.6 pressures on Resume |
| `c4a-pos` | t3 | RED, GREEN 3 | C4a gate; the trigger |
| `c4a-neg` | t3 | RED, GREEN 3 | Validation 2 |
| `c4b` | t9 | RED | C4b gate; the recipe |
| `v1` | t9 | GREEN 3 | Validation 1 (C4b's GREEN) |
| `fc`, `cr` | t9 | GREEN 3 | R5.5's planted-defect probe |
| `b2` | t2 | GREEN 3, if C2 shipped | R5.5's B2 case, through R4.9 |

A GREEN arm whose text did not ship is not run. The pilot runs one rep of each RED arm under phase `pilot`, and those reps are not counted.

## Audit and voids

`tools/extract.py` audits every tool input in a rep's transcripts, its subagents' included.

- **Void when a turn fails:** a turn is missing, exited non-zero, or reports an error.
- **Void when a path reaches out:** an input names a path under a protected root, outside the rep's allowed paths.
  - Protected roots: `~/.cache/agent-skills`, `~/.claude`, `~/Projects`, `~/.cache/pondworks`, `~/.agents`, `~/.codex`, `~/.gemini`.
  - Allowed paths: the rep's repo, its kit, the shim, its origin, `~/.cache/agent-skills/handoffs/<rep>/` and its own `~/.claude/projects/` folder. For t9 and t10 also `~/.cache/agent-skills/cc-guide/`, which the drift spec cites.
  - Listing `~/.cache/agent-skills/handoffs/` itself voids a rep.
- **Void when an input names a fragment:** `handoffs/red`, `agent-skills/handoff-brief`, `plan40-draft`, `Projects/agent-skills`, `specs/handoff-briefs` or `red-baseline-handoff`.
- **Void on a denial.** A rep whose FAIL traces to a permission denial listed in its extract is void; the scorer writes a `VOID` line.
- **Valid storage.** A brief written to `.handoff/` at the repo root, with its own `.gitignore` of `*`, is valid storage (spec R4.6's fallback).
- **Replacement.** A void rep is replaced by a new rep, up to 10 dispatched per arm and phase. An arm left with fewer than 5 valid reps (3 for `v3`) is UNSETTLED, and your human partner decides.
- **Counting.** Only the first 5 valid reps by id count (3 for `v3`).

## Scoring

1. `tools/extract.py BATCH` writes each rep's `extract.md` and `audit.json`.
2. For each arm, the controller dispatches one scorer subagent with `rubric.md` and the arm's valid extracts. The scorer writes `scores/<phase>/<arm>.tsv`. `c4b` and `v1` are scored on the capable tier, since their F-unchecked needs claims checked against the repo; the rest on the standard tier.
3. `tools/tally.py PHASE` rejects any quote it cannot find in its extract, so those lines are rescored. It then prints counts and verdicts.

## Thresholds

- **RED.** A component's failure is observed when at least 2 of its gating arm's 5 valid reps fail any gating criterion. Observed means GO: the gated text ships. Otherwise NO-GO: the spec's fallback applies.
  - The gating arms are `c1` (C1), `c2` (C2), `c4a-pos` (C4a), `c4b` (C4b), `c5a-pos` (C5a) and `c5b-pos` (C5b).
  - Negative arms are recorded only.
  - C3's counts on `c2` are recorded as the control.
- **GREEN positive arms** pass when at least 4 of 5 valid reps pass every criterion. These arms are `c1`, `p1`, `c2`, `p2`, `c2b`, `c4a-pos`, `v1`, `b2`, `c5a-pos`, `c5a-pr`, `c5a-ep`, `p5a`, `c5b-pos`, `p5b` and `c5b-part`.
- **GREEN negative arms:** `c5a-neg` and `c5b-neg` pass at 0 of 5 failing; `c4a-neg` passes at most 1 of 5 failing.
- **`v3`** passes at 2 of 3.
- **C3** is scored on `c2` (or on `c3`). Each of C3-a, C3-b and C3-c passes at no fewer than the RED count minus 1, and C3-d needs 5 of 5.
- **Probe.** In `fc`, P-f0 and P-f1 each pass in at least 4 of 5; in `cr`, P-rt0 and P-rt13 do.

## Gate outcomes (spec R5.2)

| C4a | C4b | What ships |
|---|---|---|
| GO | GO | the full skill |
| GO | NO-GO | the skill without the R4.4 recipe |
| NO-GO | GO | the recipe and the review, with a description that triggers on writing a brief |
| NO-GO | NO-GO | no skill; your human partner asks for briefs |

The other gates:
- C1 NO-GO: no Entry Check section; the script ships with `plan ids:` only.
- C2 NO-GO: no `## Decisions` and no review stage.
- C5a NO-GO: no step 3a and no resume handoff.
- C5b NO-GO: no Resume rewrite.

C3, R1.3, R2.1, R7.5 and the §4 stance sentence ship whatever the gates decide.

## REFACTOR

A failing GREEN arm gets these steps:
1. Revise the text, and commit.
2. Build a new kit.
3. Rerun that arm and its negative counterpart, with 5 new reps each.

At most 3 rounds per component. Your human partner then decides: ship as is, take the NO-GO variant, or descope.

## Change log

Changes are logged in `changes.log`, beside this file. It is not frozen, so recording a freeze id never changes the hashes it records. Append one line per change: the date, what changed, why, and the freeze id before and after. The freeze id is `shasum -a 256 FREEZE.sha256`. The first line records the initial freeze.
````

- [ ] **Step 5: Write `test_prereg.py` and `config.env.example`**

```python
'''Pre-registration consistency: every arm has its prompts and its rubric section.

Run after write_prompts.py and with rubric.md in place:
cd ~/.cache/agent-skills/handoffs/red/tools && uv run --python 3.13 --with pytest python -m pytest -q test_prereg.py
'''
from __future__ import annotations

import re
from pathlib import Path

import make_reps
import tally
import write_prompts

CTL = Path(__file__).resolve().parent.parent


def test_every_prompt_is_written_and_used():
    named = {p for _, _, prompts, _ in make_reps.ARMS.values() for p in prompts}
    assert named == set(write_prompts.PROMPTS)
    assert all((CTL / 'prompts' / name).is_file() for name in named)


def test_every_arm_has_a_rubric_section():
    rubric = (CTL / 'rubric.md').read_text()
    headed = {arm for line in rubric.splitlines() if line.startswith('## ')
              for arm in re.findall(r'`([a-z0-9-]+)`', line)}
    assert set(make_reps.ARMS) <= headed


def test_gating_criteria_are_defined_in_the_rubric():
    rubric = (CTL / 'rubric.md').read_text()
    for _, criteria in tally.GATING.values():
        for criterion in criteria:
            assert f'**{criterion}:**' in rubric, criterion


def test_every_arm_is_in_the_protocol_table():
    protocol = (CTL / 'PROTOCOL.md').read_text()
    for arm in make_reps.ARMS:
        assert f'`{arm}`' in protocol, arm
```

`config.env.example` (Task 5 copies it to `config.env`):

```
# Models and efforts for the reps. Your human partner sets every value at the
# pilot (Task 5), and they stay fixed for every phase. Each is passed to
# claude -p as given: --model takes an alias or a full model id, --effort a
# level. run_rep.sh refuses to run while one it needs is empty.
# Planning and sending arms:
MODEL_PLAN=
EFFORT_PLAN=
# Stage-execution arms (c5a-*, p5a):
MODEL_EXEC=
EFFORT_EXEC=
# The probe's reviewer arms (fc, cr):
MODEL_REVIEW=
EFFORT_REVIEW=
```

- [ ] **Step 6: Generate the prompts and the probe brief, and build the control kit**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && chmod +x write_prompts.py plant_probe.py && ./write_prompts.py && ./plant_probe.py && ./build_kit.sh k-a "$(awk '/^BASE40:/ {print $2}' /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs/.sdd/40-handoff-briefs/progress.md)"
```

Expected, in order:
- `wrote 25 prompts and the C2b brief`;
- `planted [f0], [f1], [rt0], [rt13] into …/briefs/plan-38-planted.md`;
- `kit k-a from <BASE40>: 11 skills`.

If the planter stops on an anchor, the example files changed since planning. Stop and report.

- [ ] **Step 7: Run every tool test**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && uv run --python 3.13 --with pytest python -m pytest -q test_tools.py test_plant_probe.py test_prereg.py
```

Expected: `17 passed`.

- [ ] **Step 8: Make the pilot reps**

Make one rep for each RED arm, all in batch `pilot`:

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && for arm in c1 c2 c4a-pos c4a-neg c4b c5a-pos c5a-neg c5b-pos c5b-neg; do ./make_reps.py "$arm" pilot k-a 1 pilot; done && cat ../batches/pilot.txt
```

Expected: nine lines naming the reps, then nine rep ids, `r001` through `r009`.

- [ ] **Step 9: Freeze the pre-registration**

```bash
cd ~/.cache/agent-skills/handoffs/red && shasum -a 256 PROTOCOL.md rubric.md prompts/*.txt briefs/c2b-site-report.md briefs/plan-38-planted.md tools/*.py tools/*.sh > FREEZE.sha256 && shasum -a 256 FREEZE.sha256
```

Expected: one hash, the freeze id. Start `changes.log` in the same directory with one line: `<date> — frozen before any rep ran; freeze <id>`. `changes.log` is outside the freeze (PROTOCOL.md, Change log), so recording an id there leaves the hashes as they are.

- [ ] **Step 10: Record completion**

In the ledger, write `Task 4: complete (no repo commits; freeze <hash>; kit k-a = <BASE40>; pilot reps r001-r009)`.

### Task 5: Pilot (owner)

**Executor:** owner, then controller. This task is a hard stop: the controller ends its turn with the owner block below.

**Files** (none in git):
- Create: `~/.cache/agent-skills/handoffs/red/config.env` (your human partner)
- Modify: `changes.log`, and the frozen file it names, only if the pilot changes mechanics

**Interfaces:**
- Consumes: Task 4's pilot batch and freeze.
- Produces:
  - a valid pilot rep for each RED arm;
  - the models in `config.env`;
  - the R5.3 `/context` finding;
  - a cost projection;
  - your human partner's go for the RED batch.

- [ ] **Step 1: Hand the pilot to your human partner**

End your turn with this block, filled in:

> **Pilot — your steps.** Nothing here runs inside Claude Code.
>
> 1. **Models.** Copy `~/.cache/agent-skills/handoffs/red/config.env.example` to `config.env` in the same directory. Set the six values: the model and effort for the planning arms, the execution arms and the probe reviewers. Each value goes to `claude -p` as given. The same values hold for every later phase.
> 2. **Run the pilot.** In a plain terminal (Terminal.app, not a Claude Code tab):
>    ```bash
>    ~/.cache/agent-skills/handoffs/red/tools/run_batch.sh pilot
>    ```
>    Nine sessions run, one at a time. Add `-j 3` to run three at a time.
> 3. **`/context` (spec R5.3).** Open an interactive `claude` in `/Users/lowell/Projects/agent-skills`, run `/context`, and note two things: whether the skills section shows any description as dropped or truncated, and the skills' token total.
> 4. Reply "pilot done", with the `/context` finding.

- [ ] **Step 2: Audit the pilot**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./extract.py pilot
```

Expected: nine lines, each `valid`, with a cost. Then check that the kit loaded and that no MCP tool appeared:

```bash
cd ~/.cache/agent-skills/handoffs/red/results && grep -l 'Skill: writing-plans' r001/extract.md r002/extract.md; grep -l 'Skill: derive-roadmap' r008/extract.md r009/extract.md; grep -rl 'mcp__' r00[1-9]/project | head -3
```

Expected:
- the first grep lists both of its files;
- the second grep lists both of its files;
- the third prints nothing.

A missing Skill call is not a failure by itself: a control may never invoke the skill. Read that rep's tool calls before concluding the kit failed to load. The third grep looks for any MCP tool name in the transcripts, offered or used. If it lists a file, `--strict-mcp-config` did not keep MCP servers out. Stop and show your human partner the file; the fix is theirs to choose, and it goes through Step 3.

- [ ] **Step 3: Repair mechanics only, if the pilot shows a problem**

A mechanical failure is a fixture that breaks, a tool bug, a refused write that no fallback covers, or an audit flag on a legitimate path. Fix it in `tools/`, or rebuild the one affected template: delete its directory first, then run `build_fixtures.py`.
- Never change a prompt's substance or a rubric criterion here.
- Re-freeze: `cd ~/.cache/agent-skills/handoffs/red && shasum -a 256 PROTOCOL.md rubric.md prompts/*.txt briefs/c2b-site-report.md briefs/plan-38-planted.md tools/*.py tools/*.sh > FREEZE.sha256 && shasum -a 256 FREEZE.sha256`. Log each fix in `changes.log` with the freeze id before and after. Then pilot the affected arm again with a new rep (`make_reps.py <arm> pilot k-a 1 pilot2`).
- Your human partner runs `run_batch.sh pilot2`, as in Step 1.

- [ ] **Step 4: Report, and get the go**

Give your human partner:
- the pilot's validity per arm;
- the `/context` finding, and what R5.3 requires if a description is dropped (`skillOverrides` or pruning plugins, never trimming descriptions);
- the mean cost per rep for each arm, projected over the RED batch (45 reps, plus voids) and the GREEN phases (about 100 reps).

Ask for the go for the RED batch. This is a hard stop. In the ledger, write: `Task 5: complete (pilot valid; models <...>; /context <finding>; owner go <date>)`.

### Task 6: RED baseline (owner), and the record

**Executor:** controller, owner, controller.

**Files:**
- Create: `specs/red-baseline-handoff-briefs-<YYYY-MM-DD>.md`, where the date is the day the RED batch finishes
- Create (not in git): RED reps, results, scores

**Interfaces:**
- Consumes: Task 5's go and `config.env`.
- Produces:
  - the RED record, committed;
  - a GO or NO-GO for each of C1, C2, C4a, C4b, C5a and C5b, which Tasks 10, 11, 14, 15 and 17 read;
  - C3's control counts, which Task 12 reads.

- [ ] **Step 1: Make the RED reps**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && for arm in c1 c2 c4a-pos c4a-neg c4b c5a-pos c5a-neg c5b-pos c5b-neg; do ./make_reps.py "$arm" red k-a 5 red; done && wc -l < ../batches/red.txt
```

Expected: `45`.

- [ ] **Step 2: Hand the batch to your human partner (hard stop)**

> **RED batch — your step.** In a plain terminal:
> ```bash
> ~/.cache/agent-skills/handoffs/red/tools/run_batch.sh -j 3 red
> ```
> 45 sessions. The batch resumes where it stopped if interrupted. Reply "red done".

- [ ] **Step 3: Audit, and replace void reps**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./extract.py red
```

For each arm with fewer than 5 valid reps:
1. Make that many new reps into batch `red-r<N>`: `./make_reps.py <arm> red k-a <n> red-r1`.
2. Hand `run_batch.sh red-r1` to your human partner, as in Step 2.
3. Extract again.

Stop at 10 dispatched for an arm. That arm is then UNSETTLED; report it, and your human partner decides.

- [ ] **Step 4: Score each arm**

Dispatch one scorer subagent per RED arm. The tiers come from PROTOCOL.md's Scoring section: capable for `c4b`, standard for the rest. Give each scorer:
- `~/.cache/agent-skills/handoffs/red/rubric.md`, and its arm's section by name;
- the list of the arm's valid reps, each `results/<rep>/extract.md`;
- the output path `~/.cache/agent-skills/handoffs/red/scores/red/<arm>.tsv`;
- the rule that every PASS, FAIL or VOID line carries a verbatim quote from the extract;
- for `c4b`, the rep repos at `~/.cache/pondworks/reps/<rep>/`, for F-unchecked.

Also score C3 on the `c2` reps: the `c2` scorer adds C3-a to C3-d lines to `c2.tsv`. Then:

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./tally.py red
```

Expected: exit 0, and one line per arm. If it exits 1, the lines it lists go back to that arm's scorer, and you tally again.

- [ ] **Step 5: Write the RED record**

In the worktree, create `specs/red-baseline-handoff-briefs-<YYYY-MM-DD>.md`. Use the real counts. Paraphrase evidence in one line per failure, and quote no transcript or brief text:

```markdown
# RED baseline — handoff briefs (plan 40)

**Date:** <YYYY-MM-DD> · **Status:** <n> of 45 counted RED reps valid; gates below.
**Governs:** which gated parts of `specs/handoff-briefs.md` ship (R5.1–R5.2, R7.6).

> ⚠️ Quarantine this file during any later micro-test of writing-plans,
> subagent-driven-development, executing-plans, derive-roadmap or prepare-handoff.
> It states the expected failures (Channel 1).

## Method

Pre-registered in `~/.cache/agent-skills/handoffs/red/PROTOCOL.md`, freeze `<hash>`, before any rep ran.
- Your human partner launched every rep from a plain terminal, as a `claude -p` session (<claude version>) with `--setting-sources project,local --strict-mcp-config`.
- Each rep loaded kit k-a (the skill text at `<BASE40>`) through `--add-dir`, in its own fixture repo.
- Models: <MODEL_PLAN/EFFORT_PLAN>, <MODEL_EXEC/EFFORT_EXEC>.
- A failure counts as observed at 2 or more of 5 valid reps.
- Voids: <n> (<reasons>).
- Cost: $<total>.

## Results

| Component | Arm | Valid | Failing reps | Per criterion | Gate |
|---|---|---|---|---|---|
| C1 | `c1` | 5 | <n> | F-a <n>, F-b <n> | <GO / NO-GO> |
| C2 | `c2` | 5 | <n> | F-log <n>, F-spec <n> | <GO / NO-GO> |
| C4a | `c4a-pos` | 5 | <n> | F-lost <n> | <GO / NO-GO> |
| C4b | `c4b` | 5 | <n> | F-restate <n>, F-reading <n>, F-unchecked <n>, F-gates <n> | <GO / NO-GO> |
| C5a | `c5a-pos` | 5 | <n> | F-handoff <n>, F-stamp <n>, F-timing <n>, F-next <n> | <GO / NO-GO> |
| C5b | `c5b-pos` | 5 | <n> | F-read <n>, F-amend <n>, F-commit <n>, F-line <n>, F-scope <n> | <GO / NO-GO> |

Recorded, not gating:
- `c4a-neg`: a brief written in <n> of 5.
- `c5a-neg`: roadmap text written in <n> of 5.
- `c5b-neg`: an entry amended in <n> of 5.
- C3 control, on `c2`: C3-a <n>, C3-b <n>, C3-c <n>, C3-d <n> passing of 5.

One line of evidence per observed failure, by rep id:
- <rep> <criterion>: <paraphrase>

## Gate decisions

- C1 <GO/NO-GO>: <Task 10 adds R1.2 / Task 10's NO-GO variant: the script keeps only `plan ids:`>.
- C2 <GO/NO-GO>: <Task 11 adds R2.2–R2.5 / Task 11's NO-GO variant>.
- C4 (R5.2), C4a <GO/NO-GO> with C4b <GO/NO-GO>: <the R5.2 row that ships>.
- C5a <GO/NO-GO>: <Task 14 adds step 3a and the B3 handoff / skipped>.
- C5b <GO/NO-GO>: <Task 15 rewrites Resume / skipped>.
- Ungated, shipping in all cases: C3, R1.3 with `plan ids:`, R2.1, R7.5, and the §4 stance sentence.

## Pre-flight checks

- `/context` (R5.3): <finding>.
- Pilot: <n> reps, <changes logged in PROTOCOL.md, or none>.

## GREEN results

Appended by Tasks 12, 16 and 19.
```

- [ ] **Step 6: Commit the record**

Run the gate commands, then:

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs && git add specs/red-baseline-handoff-briefs-*.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "docs(specs): record the handoff-briefs RED baseline"
```

End the message with your session's Co-Authored-By trailer.

- [ ] **Step 7: Your human partner confirms the gates (hard stop)**

Show your human partner the Gate decisions section. Ask them to confirm it, or to override a line. Record an override in the same section as `Owner override (<date>): <line> — <reason>`, and commit it:

```bash
git add specs/red-baseline-handoff-briefs-*.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "docs(specs): record the owner's gate override"
```

A confirmation without an override changes nothing in the record.

In the ledger, write `Task 6: complete (commits <base7>..<head7>; gates C1 <>, C2 <>, C4a <>, C4b <>, C5a <>, C5b <>)`. Task 6's diff is the record alone, and it gets the usual task review.

## Phase 1 — writing-plans: C1, C2, C3 (spec R1–R3, R5.4, R5.6, R6.1, R6.5)

Every Phase 1 task works in the worktree. Gated tasks read their gate from the ledger's `Task 6:` line, which matches the RED record's Gate decisions. The controller names the variant in the implementer's brief.

### Task 7: `entry_check.py`, plan ids, and the id rule (ungated)

**Executor:** implementer. **Gate:** none. R1.3's id check and the script's `plan ids:` field ship whatever the gates decide (spec R5.2). They land together, because the conformance check's orphan-bundled-file rule fails a script that no text in its skill names.

**Files:**
- Create: `skills/writing-plans/scripts/test_entry_check.py`
- Create: `skills/writing-plans/scripts/entry_check.py`
- Modify: `skills/writing-plans/SKILL.md:22` (the id rule)
- Modify: `CLAUDE.md:96` (the writing-plans suite comment)
- Modify: `NOTICE` (the superpowers change list)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - The CLI `uv run --no-project --python 3.13 python <this-skill-dir>/scripts/entry_check.py [SPEC]`. It is run from the repo root, and is read-only.
  - It exits 0 with a report. It exits 2 with `entry_check: not inside a git repository`, `entry_check: no such spec: X` or `entry_check: spec is outside this repository: X` on stderr.
  - Report lines:
    - `plan ids:`
    - `  highest: N — <plans>`, or `  highest: none`
    - `  next free: N`
    - `  collisions: none`, or `  collisions:` followed by one `    N: <plans>` line per colliding id
    - with a spec, also `  plans for this spec: <plans>`, or `none`
  - `<plans>` is `<file> (<where>)`, joined by `; `. `<where>` lists the refs by short name, then `worktree <path>` for each worktree whose `specs/plans/` holds the file.
  - Task 8 replaces the whole script, and appends to the test file.
  - The `:22` id rule, which Task 10 replaces when C1 is GO.

- [ ] **Step 1: Write the failing tests**

Create `skills/writing-plans/scripts/test_entry_check.py`:

```python
'''Tests for entry_check.py — the writing-plans entry-check reporter.

Every fixture is a throwaway git repository under pytest's tmp_path.
'''
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name('entry_check.py')
GIT = [
    'git', '-c', 'commit.gpgsign=false', '-c', 'init.defaultBranch=main',
    '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=t', '-c', 'user.email=t@example.invalid',
]


def git(cwd: Path, *args: str, date: str | None = None) -> str:
    env = dict(os.environ)
    if date is not None:
        env['GIT_AUTHOR_DATE'] = env['GIT_COMMITTER_DATE'] = f'{date}T12:00:00'
    return subprocess.run([*GIT, *args], cwd=cwd, env=env, capture_output=True, text=True, check=True).stdout


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def commit(root: Path, message: str, date: str = '2026-09-01') -> None:
    git(root, 'add', '-A')
    git(root, 'commit', '-q', '-m', message, date=date)


def check(cwd: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True,
        env={**os.environ, **(env or {})}, check=False,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / 'repo'
    root.mkdir()
    git(root, 'init', '-q')
    write(root, 'specs/plans/completed/1-first.md', '# Plan 1\n')
    write(root, 'specs/plans/2-second.md', '# Plan 2\n')
    commit(root, 'plans 1 and 2')
    return root


def test_without_a_spec_only_plan_ids_print(repo):
    done = check(repo)
    assert done.returncode == 0
    assert done.stdout.startswith('plan ids:\n')
    assert 'status:' not in done.stdout


def test_highest_and_next_free(repo):
    out = check(repo).stdout
    assert '  highest: 2 — 2-second.md (main, worktree ' in out
    assert '  next free: 3' in out
    assert '  collisions: none' in out


def test_plan_on_another_branch_counts(repo):
    git(repo, 'checkout', '-q', '-b', 'side')
    write(repo, 'specs/plans/3-third.md', '# Plan 3\n')
    commit(repo, 'plan 3 on a side branch')
    git(repo, 'checkout', '-q', 'main')
    out = check(repo).stdout
    assert '  highest: 3 — 3-third.md (side)' in out
    assert '  next free: 4' in out


def test_symbolic_refs_are_skipped(repo):
    git(repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
    git(repo, 'symbolic-ref', 'refs/remotes/origin/HEAD', 'refs/remotes/origin/main')
    done = check(repo)
    assert done.returncode == 0
    assert '2-second.md (main, origin/main, worktree ' in done.stdout
    assert 'origin/HEAD' not in done.stdout


def test_untracked_plan_in_a_second_worktree(repo, tmp_path):
    other = tmp_path / 'other'
    git(repo, 'worktree', 'add', '-q', '-b', 'wt', str(other))
    write(other, 'specs/plans/4-fourth.md', '# Plan 4, not committed anywhere\n')
    out = check(repo).stdout
    assert '  highest: 4 — 4-fourth.md (worktree ' in out
    assert '  next free: 5' in out


def test_id_collision_is_reported(repo):
    git(repo, 'checkout', '-q', '-b', 'side')
    write(repo, 'specs/plans/2-other.md', '# Another plan 2\n')
    commit(repo, 'a second plan 2')
    git(repo, 'checkout', '-q', 'main')
    out = check(repo).stdout
    assert '  collisions:\n    2: 2-second.md (main, side, worktree ' in out
    assert '; 2-other.md (side)' in out


def test_plan_named_for_the_spec_is_listed(repo):
    write(repo, 'specs/widget-export.md', '# Widget export\n')
    write(repo, 'specs/plans/3-widget-export.md', '# Plan 3\n')
    commit(repo, 'spec and its plan')
    out = check(repo, 'specs/widget-export.md').stdout
    assert '  plans for this spec: 3-widget-export.md (main, worktree ' in out


def test_spec_with_no_plan_reads_none(repo):
    write(repo, 'specs/gadget.md', '# Gadget\n')
    commit(repo, 'a spec with no plan')
    out = check(repo, 'specs/gadget.md').stdout
    assert '  plans for this spec: none' in out


def test_no_plans_for_spec_line_without_a_spec(repo):
    out = check(repo).stdout
    assert 'plan ids:' in out
    assert 'plans for this spec' not in out


def test_outside_a_repo_exits_2(tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    done = check(outside, env={'GIT_CEILING_DIRECTORIES': str(tmp_path)})
    assert done.returncode == 2
    assert 'not inside a git repository' in done.stderr


def test_missing_spec_exits_2(repo):
    done = check(repo, 'specs/nope.md')
    assert done.returncode == 2
    assert 'no such spec: specs/nope.md' in done.stderr


def test_repo_without_plans_starts_at_1(tmp_path):
    root = tmp_path / 'empty'
    root.mkdir()
    git(root, 'init', '-q')
    write(root, 'README.md', '# Empty\n')
    commit(root, 'readme only')
    out = check(root).stdout
    assert '  highest: none' in out
    assert '  next free: 1' in out
```

- [ ] **Step 2: Run them and watch them fail**

```bash
cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q test_entry_check.py
```

Expected: `12 failed`. Each one fails because `entry_check.py` does not exist.

- [ ] **Step 3: Write the script**

Create `skills/writing-plans/scripts/entry_check.py`:

```python
#!/usr/bin/env python3
'''Report what a planning session checks before it plans a spec.

Run from the repo root:

    uv run --no-project --python 3.13 python <this-skill-dir>/scripts/entry_check.py [SPEC]

It prints the ``plan ids:`` field, drawn from every branch and remote-tracking
ref (symbolic refs such as ``origin/HEAD`` skipped) and from every worktree's
``specs/plans/``, untracked plans included: the highest id and where it
occurs, the next free id, any id used by two different plan filenames, and,
given a spec path, any plan whose name ends in the spec's stem.

A reporter, like deferred_stats.py: it is read-only and exits 0 whenever it
prints a report. It exits 2 only when it cannot run: outside a git
repository, or given a spec path that does not exist.
'''

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

CANNOT_RUN = 2
PLAN_RE = re.compile(r'^(?P<id>\d+)-(?P<name>.+)\.md$')


class CannotRun(Exception):
    '''The report cannot be produced; main() prints the reason and exits 2.'''


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, check=False)


def git_out(root: Path, *args: str) -> str:
    done = git(root, *args)
    if done.returncode != 0:
        raise CannotRun(done.stderr.strip() or f'git {" ".join(args)} failed')
    return done.stdout


def repo_root(cwd: Path) -> Path:
    done = git(cwd, 'rev-parse', '--show-toplevel')
    if done.returncode != 0:
        raise CannotRun('not inside a git repository')
    return Path(done.stdout.strip())


@dataclass
class Plan:
    name: str
    locations: list[str] = field(default_factory=list)


def ref_names(root: Path) -> list[str]:
    '''Every branch and remote-tracking ref, skipping symbolic ones like origin/HEAD.'''
    out = git_out(root, 'for-each-ref', '--format=%(refname)%09%(symref)', 'refs/heads', 'refs/remotes')
    refs = []
    for line in out.splitlines():
        ref, _, symref = line.partition('\t')
        if ref and not symref:
            refs.append(ref)
    return refs


def worktree_paths(root: Path) -> list[Path]:
    out = git_out(root, 'worktree', 'list', '--porcelain')
    return [Path(line.removeprefix('worktree ')) for line in out.splitlines() if line.startswith('worktree ')]


def plan_sightings(root: Path) -> list[tuple[str, str]]:
    '''(filename, location) for every file under specs/plans on every ref and in every worktree.'''
    seen = []
    for ref in ref_names(root):
        short = ref.removeprefix('refs/heads/').removeprefix('refs/remotes/')
        listing = git(root, 'ls-tree', '-r', '--name-only', ref, '--', 'specs/plans')
        seen.extend((Path(path).name, short) for path in listing.stdout.splitlines())
    for tree in worktree_paths(root):
        plans = tree / 'specs' / 'plans'
        if plans.is_dir():
            seen.extend((path.name, f'worktree {tree}') for path in sorted(plans.rglob('*.md')))
    return seen


def plans_by_id(root: Path) -> dict[int, list[Plan]]:
    by_id: dict[int, dict[str, Plan]] = {}
    for filename, where in plan_sightings(root):
        m = PLAN_RE.match(filename)
        if not m:
            continue
        plan = by_id.setdefault(int(m['id']), {}).setdefault(filename, Plan(filename))
        if where not in plan.locations:
            plan.locations.append(where)
    return {pid: list(plans.values()) for pid, plans in by_id.items()}


def describe(plans: list[Plan]) -> str:
    return '; '.join(f'{p.name} ({", ".join(p.locations)})' for p in plans)


def names_spec(plan: Plan, stem: str) -> bool:
    name = PLAN_RE.match(plan.name)['name']
    return name == stem or name.endswith(f'-{stem}')


def format_plan_ids(by_id: dict[int, list[Plan]], stem: str | None) -> list[str]:
    lines = ['plan ids:']
    if by_id:
        top = max(by_id)
        lines += [f'  highest: {top} — {describe(by_id[top])}', f'  next free: {top + 1}']
    else:
        lines += ['  highest: none', '  next free: 1']
    collisions = [(pid, by_id[pid]) for pid in sorted(by_id) if len(by_id[pid]) > 1]
    if collisions:
        lines.append('  collisions:')
        lines += [f'    {pid}: {describe(plans)}' for pid, plans in collisions]
    else:
        lines.append('  collisions: none')
    if stem is not None:
        mine = [p for pid in sorted(by_id) for p in by_id[pid] if names_spec(p, stem)]
        lines.append(f'  plans for this spec: {describe(mine) if mine else "none"}')
    return lines


def report(root: Path, spec: Path | None) -> list[str]:
    return format_plan_ids(plans_by_id(root), spec.stem if spec is not None else None)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Report what a planning session checks before it plans a spec.')
    parser.add_argument('spec', nargs='?', type=Path, help='the spec about to be planned')
    args = parser.parse_args(argv)
    try:
        root = repo_root(Path.cwd())
        spec = None
        if args.spec is not None:
            if not args.spec.is_file():
                raise CannotRun(f'no such spec: {args.spec}')
            try:
                spec = args.spec.resolve().relative_to(root.resolve())
            except ValueError:
                raise CannotRun(f'spec is outside this repository: {args.spec}') from None
        print('\n'.join(report(root, spec)))
    except CannotRun as e:
        print(f'entry_check: {e}', file=sys.stderr)
        return CANNOT_RUN
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 4: Run the tests, then the whole suite**

```bash
cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q test_entry_check.py && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: `12 passed`, then the suite's pass count rises by 12 over Task 1's baseline.

- [ ] **Step 5: Run it on this repository**

From the worktree root:

```bash
uv run --no-project --python 3.13 python skills/writing-plans/scripts/entry_check.py
```

Expected: a `plan ids:` block whose `highest:` line is at least 40, with `40-handoff-briefs.md` among the plans, and exit 0. A collision it reports is not this task's failure. Copy the block into your report.

- [ ] **Step 6: The id rule (R1.3)**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
**Save plans to:** `specs/plans/<id>-<spec-name>.md` — `<id>` is the next integer (check `specs/plans/` and `specs/plans/completed/`, take the highest existing `<id>` + 1); `<spec-name>` matches the spec the plan implements. When the plan is fully executed, run the Plan Completion Protocol (below).
````

with:

````markdown
**Save plans to:** `specs/plans/<id>-<spec-name>.md` — `<id>` is the `next free:` id that `uv run --no-project --python 3.13 python <this-skill-dir>/scripts/entry_check.py` prints under `plan ids:`, run from the repo root. It reads every branch, remote-tracking ref and worktree, untracked plans included, because ids are allocated per branch and collide. A collision it reports is your human partner's call. `<spec-name>` matches the spec the plan implements. When the plan is fully executed, run the Plan Completion Protocol (below).
````

- [ ] **Step 7: Name the new tests in CLAUDE.md**

In `CLAUDE.md`, replace:

````text
# writing-plans deferred-backlog stats tests (stdlib only)
````

with:

````text
# writing-plans deferred-backlog stats and entry-check tests (stdlib only; the entry-check tests build throwaway git repos)
````

- [ ] **Step 8: Record the script in NOTICE (spec R6.1)**

In `NOTICE`, add this bullet as the last item of the superpowers "Changes from upstream" list, directly above the blank line before `    brainstorming/`:

````text
  - writing-plans gained a second reporter not present upstream:
    writing-plans/scripts/entry_check.py and its tests
    (writing-plans/scripts/test_entry_check.py), which report the plan
    ids in use on every branch, remote-tracking ref and worktree, and
    the next free one. Both are original works by Lowell Mason under
    the same MIT terms, as deferred_stats.py is (above). The skill's
    id rule now takes the next free id from that report.
````

- [ ] **Step 9: Run the gates and commit**

Run every command in the Global Constraints' gate block. All pass. Then:

```bash
git add skills/writing-plans/scripts/entry_check.py skills/writing-plans/scripts/test_entry_check.py skills/writing-plans/SKILL.md CLAUDE.md NOTICE && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "feat(writing-plans): take the next plan id from entry_check across refs and worktrees"
```

### Task 8: `entry_check.py`, the spec fields (C1)

**Executor:** implementer. **Gate:** C1.
- **NO-GO:** skip this task. In the ledger, write `Task 8: skipped (C1 NO-GO; the script keeps plan ids only)`.
- **GO:** do the steps below.

**Files:**
- Modify: `skills/writing-plans/scripts/test_entry_check.py` (append)
- Modify: `skills/writing-plans/scripts/entry_check.py` (replace whole)
- Modify: `NOTICE` (Task 7's bullet)

**Interfaces:**
- Consumes: Task 7's script and tests.
- Produces: the same CLI. With a spec, it prints four fields in this order. `plan ids:` is unchanged from Task 7.
  - `status: <line>` or `status: none`.
  - `since:`, then one line per commit: `  * <sha> <date> <subject>` for the commit that last changed the status line, `    <sha> <date> <subject>` for the rest, and `  (* last changed the status line)` when one is marked. Or `since: none`.
  - `mentions:`, then `  <path>:<line>`, with ` open`, ` done` or ` unmarked` appended in `specs/deferred_items.md`. Or `mentions: none`.
  - `plan ids:`.

  Task 10's Entry Check section names these four fields.

- [ ] **Step 1: Append the failing tests**

Append to `skills/writing-plans/scripts/test_entry_check.py`, after two blank lines:

```python
SPEC = 'specs/widget-export.md'
APPROVED = '**Status: DESIGN APPROVED (2026-09-10).** The owner approved it.'


def section(out: str, label: str) -> list[str]:
    '''One report field: its label line and the indented lines under it.'''
    lines = out.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(label))
    end = next((i for i in range(start + 1, len(lines)) if not lines[i].startswith(' ')), len(lines))
    return lines[start:end]


@pytest.fixture
def spec_repo(repo):
    write(repo, SPEC, '# widget-export\n\n**Status: DRAFT (2026-09-05).**\n\nR1. Export widgets.\n')
    commit(repo, 'draft the widget export spec', date='2026-09-05')
    write(repo, SPEC, f'# widget-export\n\n{APPROVED}\n\nR1. Export widgets.\n')
    commit(repo, 'approve the widget export spec', date='2026-09-10')
    write(repo, SPEC, f'# widget-export\n\n{APPROVED}\n\nR1. Export widgets as CSV.\n')
    commit(repo, 'clarify R1', date='2026-09-12')
    write(repo, 'README.md', '# Unrelated\n')
    commit(repo, 'unrelated readme', date='2026-09-15')
    return repo


def test_status_is_printed_verbatim(spec_repo):
    out = check(spec_repo, SPEC).stdout
    assert section(out, 'status:') == [f'status: {APPROVED}']


def test_since_lists_commits_on_and_after_the_status_date_newest_first(spec_repo):
    lines = section(check(spec_repo, SPEC).stdout, 'since:')
    assert [line[4:].split(' ', 2)[2] for line in lines[1:3]] == ['clarify R1', 'approve the widget export spec']
    assert len(lines) == 4
    assert 'draft the widget export spec' not in '\n'.join(lines)
    assert 'unrelated readme' not in '\n'.join(lines)


def test_status_change_commit_is_marked(spec_repo):
    lines = section(check(spec_repo, SPEC).stdout, 'since:')
    approve = next(line for line in lines if line.endswith('approve the widget export spec'))
    clarify = next(line for line in lines if line.endswith('clarify R1'))
    assert approve.startswith('  * ')
    assert clarify.startswith('    ')
    assert lines[-1] == '  (* last changed the status line)'


def test_undated_status_lists_commits_after_the_status_change(repo):
    write(repo, SPEC, '**Status: approved by the owner.**\n\nR1.\n')
    commit(repo, 'approve without a date', date='2026-09-05')
    write(repo, SPEC, '**Status: approved by the owner.**\n\nR1. More.\n')
    commit(repo, 'first edit after approval', date='2026-09-06')
    write(repo, SPEC, '**Status: approved by the owner.**\n\nR1. More still.\n')
    commit(repo, 'second edit after approval', date='2026-09-07')
    text = '\n'.join(section(check(repo, SPEC).stdout, 'since:'))
    assert 'second edit after approval' in text
    assert 'first edit after approval' in text
    assert 'approve without a date' not in text


def test_no_status_line_reads_none(repo):
    write(repo, SPEC, '# Widget export\n\nNo status here.\n')
    commit(repo, 'spec without a status')
    assert section(check(repo, SPEC).stdout, 'status:') == ['status: none']


def test_status_line_after_line_10_is_not_found(repo):
    write(repo, SPEC, '# Widget export\n' + '\n' * 10 + f'{APPROVED}\n')
    commit(repo, 'status too far down')
    assert section(check(repo, SPEC).stdout, 'status:') == ['status: none']


def test_nickname_constraint_file_is_listed_by_its_stem_line(spec_repo):
    plan = (
        '# Plan 3: alerts column\n\n## Global Constraints\n\n'
        '- The exporter spec must drop the `alerts` column before it is planned.\n\n'
        '## Notes\n\nThe exporter spec is specs/widget-export.md.\n'
    )
    write(spec_repo, 'specs/plans/completed/3-alerts.md', plan)
    commit(spec_repo, 'plan 3')
    hits = section(check(spec_repo, SPEC).stdout, 'mentions:')
    assert '  specs/plans/completed/3-alerts.md:9' in hits
    assert '  specs/plans/completed/3-alerts.md:5' not in hits


def test_untracked_files_are_listed_and_the_spec_is_skipped(spec_repo):
    write(spec_repo, 'specs/notes.md', 'Draft notes on widget-export.\n')
    hits = section(check(spec_repo, SPEC).stdout, 'mentions:')
    assert '  specs/notes.md:1' in hits
    assert not any(hit.startswith(f'  {SPEC}:') for hit in hits)


def test_deferred_hits_are_marked_open_or_done(spec_repo):
    backlog = (
        '# Deferred items\n\n## 7-widgets — 2026-09-01\n'
        '- [ ] Open item about widget-export.\n'
        '      A continuation line naming widget-export.\n'
        '- [x] Done: widget-export column order.\n\n'
        '## 8-other — 2026-09-02\n'
        'A note on widget-export before any item.\n'
    )
    write(spec_repo, 'specs/deferred_items.md', backlog)
    hits = section(check(spec_repo, SPEC).stdout, 'mentions:')
    assert hits[1:] == [
        '  specs/deferred_items.md:4 open',
        '  specs/deferred_items.md:5 open',
        '  specs/deferred_items.md:6 done',
        '  specs/deferred_items.md:9 unmarked',
    ]


def test_uncommitted_spec_has_no_commits(repo):
    write(repo, SPEC, f'# widget-export\n\n{APPROVED}\n')
    out = check(repo, SPEC).stdout
    assert section(out, 'status:') == [f'status: {APPROVED}']
    assert section(out, 'since:') == ['since: none']


def test_no_mentions_reads_none(spec_repo):
    assert section(check(spec_repo, SPEC).stdout, 'mentions:') == ['mentions: none']


def test_fields_print_in_order(spec_repo):
    out = check(spec_repo, SPEC).stdout
    starts = [out.index(label) for label in ('status:', 'since:', 'mentions:', 'plan ids:')]
    assert starts == sorted(starts)
    assert out.startswith('status:')
```

- [ ] **Step 2: Run them; the new ones fail**

```bash
cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q test_entry_check.py
```

Expected: `12 failed, 12 passed`. The 12 new tests fail because the report has no `status:`, `since:` or `mentions:` field.

- [ ] **Step 3: Replace the script**

Replace the whole of `skills/writing-plans/scripts/entry_check.py` with:

```python
#!/usr/bin/env python3
'''Report what a planning session checks before it plans a spec.

Run from the repo root:

    uv run --no-project --python 3.13 python <this-skill-dir>/scripts/entry_check.py [SPEC]

With a spec path it prints four labelled fields:

- ``status:`` the first line among the spec's first ten that starts with
  ``**Status``, verbatim, or ``none``.
- ``since:`` the commits touching the spec, committed on or after the first
  ``YYYY-MM-DD`` date in that status line, newest first, as
  ``<short-sha> <date> <subject>``. The commit that last changed the status
  line is marked ``*``. If the status line has no date, it lists the commits
  after that one.
- ``mentions:`` every file under this worktree's ``specs/``, untracked files
  included, except the spec itself, that contains the spec's filename stem, as
  ``path:line``. A hit in ``specs/deferred_items.md`` is marked ``open`` or
  ``done`` from the nearest item line (``- [ ]`` or ``- [x]``) at or above it
  in its ``## `` section, or ``unmarked`` when there is none.
- ``plan ids:`` drawn from every branch and remote-tracking ref (symbolic refs
  such as ``origin/HEAD`` skipped) and from every worktree's ``specs/plans/``,
  untracked plans included: the highest id and where it occurs, the next free
  id, any id used by two different plan filenames, and any plan whose name
  ends in the spec's stem.

Without a spec path it prints only ``plan ids:``.

A reporter, like deferred_stats.py: it is read-only and exits 0 whenever it
prints a report. It exits 2 only when it cannot run: outside a git
repository, or given a spec path that does not exist.
'''

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

CANNOT_RUN = 2
STATUS_SCAN_LINES = 10
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
PLAN_RE = re.compile(r'^(?P<id>\d+)-(?P<name>.+)\.md$')
ITEM_RE = re.compile(r'^- \[(?P<mark>[ xX])\]')
SECTION_RE = re.compile(r'^## ')
DEFERRED = Path('specs/deferred_items.md')


class CannotRun(Exception):
    '''The report cannot be produced; main() prints the reason and exits 2.'''


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, check=False)


def git_out(root: Path, *args: str) -> str:
    done = git(root, *args)
    if done.returncode != 0:
        raise CannotRun(done.stderr.strip() or f'git {" ".join(args)} failed')
    return done.stdout


def repo_root(cwd: Path) -> Path:
    done = git(cwd, 'rev-parse', '--show-toplevel')
    if done.returncode != 0:
        raise CannotRun('not inside a git repository')
    return Path(done.stdout.strip())


# --- status: and since: --------------------------------------------------


def status_line(text: str) -> str | None:
    for line in text.splitlines()[:STATUS_SCAN_LINES]:
        if line.startswith('**Status'):
            return line
    return None


@dataclass(frozen=True)
class Commit:
    sha: str
    date: str
    subject: str


def spec_commits(root: Path, spec: Path) -> list[Commit]:
    '''Commits touching the spec, newest first; none when it was never committed.'''
    done = git(root, 'log', '--format=%h%x09%cs%x09%s', '--', spec.as_posix())
    if done.returncode != 0:
        return []
    return [Commit(*line.split('\t', 2)) for line in done.stdout.splitlines()]


def status_at(root: Path, rev: str, spec: Path) -> str | None:
    done = git(root, 'show', f'{rev}:{spec.as_posix()}')
    return status_line(done.stdout) if done.returncode == 0 else None


def status_change(root: Path, spec: Path, commits: list[Commit]) -> Commit | None:
    '''The newest commit whose status line differs from its first parent's.'''
    for c in commits:
        if status_at(root, c.sha, spec) != status_at(root, f'{c.sha}^', spec):
            return c
    return None


def since(commits: list[Commit], status: str | None, changed: Commit | None) -> list[Commit]:
    if status is not None and (m := DATE_RE.search(status)):
        return [c for c in commits if c.date >= m.group(0)]
    if changed is not None:
        return commits[:commits.index(changed)]
    return commits


def format_since(listed: list[Commit], changed: Commit | None) -> list[str]:
    if not listed:
        return ['since: none']
    lines = ['since:']
    lines += [f'  {"*" if c == changed else " "} {c.sha} {c.date} {c.subject}' for c in listed]
    if changed in listed:
        lines.append('  (* last changed the status line)')
    return lines


# --- mentions: -------------------------------------------------------------


def item_state(lines: list[str], n: int) -> str:
    '''open or done from the nearest item line at or above line n, within its ## section.'''
    for line in reversed(lines[:n]):
        if m := ITEM_RE.match(line):
            return 'done' if m['mark'] in 'xX' else 'open'
        if SECTION_RE.match(line):
            break
    return 'unmarked'


def mentions(root: Path, spec: Path, stem: str) -> list[str]:
    specs_dir = root / 'specs'
    if not specs_dir.is_dir():
        return []
    hits = []
    for path in sorted(specs_dir.rglob('*')):
        rel = path.relative_to(root)
        if not path.is_file() or rel == spec:
            continue
        try:
            lines = path.read_text().splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, start=1):
            if stem in line:
                state = f' {item_state(lines, n)}' if rel == DEFERRED else ''
                hits.append(f'{rel.as_posix()}:{n}{state}')
    return hits


def format_mentions(hits: list[str]) -> list[str]:
    return ['mentions:', *(f'  {hit}' for hit in hits)] if hits else ['mentions: none']


# --- plan ids: ---------------------------------------------------------------


@dataclass
class Plan:
    name: str
    locations: list[str] = field(default_factory=list)


def ref_names(root: Path) -> list[str]:
    '''Every branch and remote-tracking ref, skipping symbolic ones like origin/HEAD.'''
    out = git_out(root, 'for-each-ref', '--format=%(refname)%09%(symref)', 'refs/heads', 'refs/remotes')
    refs = []
    for line in out.splitlines():
        ref, _, symref = line.partition('\t')
        if ref and not symref:
            refs.append(ref)
    return refs


def worktree_paths(root: Path) -> list[Path]:
    out = git_out(root, 'worktree', 'list', '--porcelain')
    return [Path(line.removeprefix('worktree ')) for line in out.splitlines() if line.startswith('worktree ')]


def plan_sightings(root: Path) -> list[tuple[str, str]]:
    '''(filename, location) for every file under specs/plans on every ref and in every worktree.'''
    seen = []
    for ref in ref_names(root):
        short = ref.removeprefix('refs/heads/').removeprefix('refs/remotes/')
        listing = git(root, 'ls-tree', '-r', '--name-only', ref, '--', 'specs/plans')
        seen.extend((Path(path).name, short) for path in listing.stdout.splitlines())
    for tree in worktree_paths(root):
        plans = tree / 'specs' / 'plans'
        if plans.is_dir():
            seen.extend((path.name, f'worktree {tree}') for path in sorted(plans.rglob('*.md')))
    return seen


def plans_by_id(root: Path) -> dict[int, list[Plan]]:
    by_id: dict[int, dict[str, Plan]] = {}
    for filename, where in plan_sightings(root):
        m = PLAN_RE.match(filename)
        if not m:
            continue
        plan = by_id.setdefault(int(m['id']), {}).setdefault(filename, Plan(filename))
        if where not in plan.locations:
            plan.locations.append(where)
    return {pid: list(plans.values()) for pid, plans in by_id.items()}


def describe(plans: list[Plan]) -> str:
    return '; '.join(f'{p.name} ({", ".join(p.locations)})' for p in plans)


def names_spec(plan: Plan, stem: str) -> bool:
    name = PLAN_RE.match(plan.name)['name']
    return name == stem or name.endswith(f'-{stem}')


def format_plan_ids(by_id: dict[int, list[Plan]], stem: str | None) -> list[str]:
    lines = ['plan ids:']
    if by_id:
        top = max(by_id)
        lines += [f'  highest: {top} — {describe(by_id[top])}', f'  next free: {top + 1}']
    else:
        lines += ['  highest: none', '  next free: 1']
    collisions = [(pid, by_id[pid]) for pid in sorted(by_id) if len(by_id[pid]) > 1]
    if collisions:
        lines.append('  collisions:')
        lines += [f'    {pid}: {describe(plans)}' for pid, plans in collisions]
    else:
        lines.append('  collisions: none')
    if stem is not None:
        mine = [p for pid in sorted(by_id) for p in by_id[pid] if names_spec(p, stem)]
        lines.append(f'  plans for this spec: {describe(mine) if mine else "none"}')
    return lines


# --- the report ------------------------------------------------------------


def report(root: Path, spec: Path | None) -> list[str]:
    if spec is None:
        return format_plan_ids(plans_by_id(root), None)
    status = status_line((root / spec).read_text())
    commits = spec_commits(root, spec)
    changed = status_change(root, spec, commits)
    return [
        f'status: {status if status is not None else "none"}',
        *format_since(since(commits, status, changed), changed),
        *format_mentions(mentions(root, spec, spec.stem)),
        *format_plan_ids(plans_by_id(root), spec.stem),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Report what a planning session checks before it plans a spec.')
    parser.add_argument('spec', nargs='?', type=Path, help='the spec about to be planned')
    args = parser.parse_args(argv)
    try:
        root = repo_root(Path.cwd())
        spec = None
        if args.spec is not None:
            if not args.spec.is_file():
                raise CannotRun(f'no such spec: {args.spec}')
            try:
                spec = args.spec.resolve().relative_to(root.resolve())
            except ValueError:
                raise CannotRun(f'spec is outside this repository: {args.spec}') from None
        print('\n'.join(report(root, spec)))
    except CannotRun as e:
        print(f'entry_check: {e}', file=sys.stderr)
        return CANNOT_RUN
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 4: Run the tests, then the whole suite**

```bash
cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q test_entry_check.py && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: `24 passed`, then the suite is up 12 on Task 7's count.

- [ ] **Step 5: Validation 3, the script's half**

From the worktree root:

```bash
uv run --no-project --python 3.13 python skills/writing-plans/scripts/entry_check.py specs/claude-code-drift-automation.md | grep -c '35-claude-code-guide-conformance.md:'
```

Expected: a count of at least 1 (6 on 2026-10-09). The full report lists `specs/plans/completed/35-claude-code-guide-conformance.md` under `mentions:`. It never lists that plan's line 40, which names the spec only as "the drift spec". That is the reading R1.2's section asks of the agent.

- [ ] **Step 6: Update the NOTICE bullet**

In `NOTICE`, replace:

````text
    (writing-plans/scripts/test_entry_check.py), which report the plan
    ids in use on every branch, remote-tracking ref and worktree, and
    the next free one. Both are original works by Lowell Mason under
    the same MIT terms, as deferred_stats.py is (above). The skill's
````

with:

````text
    (writing-plans/scripts/test_entry_check.py), which report a spec's
    status line, the commits since it, the files under specs/ that
    mention it, and the plan ids in use on every branch,
    remote-tracking ref and worktree, with the next free one. Both are
    original works by Lowell Mason under the same MIT terms, as
    deferred_stats.py is (above). The skill's
````

- [ ] **Step 7: Run the gates and commit**

Run the gate block. Then:

```bash
git add skills/writing-plans/scripts/entry_check.py skills/writing-plans/scripts/test_entry_check.py NOTICE && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "feat(writing-plans): report a spec's status, commits since and mentions"
```

### Task 9: writing-plans, the ungated edits (R2.1, C3)

**Executor:** implementer. **Gate:** none (spec R5.2).

**Files:**
- Modify: `skills/writing-plans/SKILL.md:71`, `:160-184`
- Modify: `NOTICE` (the superpowers change list)
- Modify: `specs/superpowers-drift-spec.md` (row 8, finding 8, Suggested disposition)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces the texts later tasks replace:
  - **The Execution Handoff,** from `**Recommend a fresh session for execution.**` to `**Which approach?"**`. Task 11 replaces it when C2 is GO.
  - **The NOTICE adoption bullet,** beginning `  - One change was later adopted FROM upstream`. Task 11 replaces it when C2 is GO.

- [ ] **Step 1: The `Spec:` pointer (R2.1)**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
**Tech Stack:** [Key technologies/libraries]

## Global Constraints
````

with:

````markdown
**Tech Stack:** [Key technologies/libraries]

**Spec:** [Path to the spec or design doc this plan implements, or `none`. The plan argues from the spec, so executors read both.]

## Global Constraints
````

- [ ] **Step 2: The model line (C3, spec R3.1)**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
**Recommend a fresh session for execution.** A planning session accumulates
context and usually runs on a stronger, pricier model tier; carrying it into
execution makes every execution turn re-read that planning history at cache-read
cost and inherit the pricier model. Starting execution fresh drops both.

**"Plan complete and saved to `specs/plans/<id>-<spec-name>.md`.**

**Recommended: `/clear` (or open a new session) and execute against the saved
plan** — a fresh session drops this planning conversation and lets execution run
on the standard model default (planning belongs on the stronger tier; execution
does not). Two execution options, either session:

**1. Subagent-Driven (recommended)** - a fresh subagent per task, two-stage review between tasks

**2. Inline Execution** - I execute the tasks myself, in plan order (executing-plans)

Continuing in THIS session works too, but costs more on a long plan: every
execution turn re-reads the full planning history and inherits this session's
model. **Which approach?"**
````

with:

````markdown
**Recommend a fresh session for execution.** A planning session accumulates
context; carrying it into execution makes every execution turn re-read that
planning history at cache-read cost. Starting execution fresh drops it. Choose
the execution model when you launch it: `claude --model <m>`, `codex -m <m>`
or `gemini -m <m>`. `/clear` keeps the current model, and `/model` saves a new
default for later sessions.

**"Plan complete and saved to `specs/plans/<id>-<spec-name>.md`.**

**Recommended: `/clear` (or open a new session) and execute against the saved
plan** — a fresh session drops this planning conversation. Two execution
options, either session:

**1. Subagent-Driven (recommended)** - a fresh subagent per task, two-stage review between tasks

**2. Inline Execution** - I execute the tasks myself, in plan order (executing-plans)

Continuing in THIS session works too, but costs more on a long plan: every
execution turn re-reads the full planning history. **Which approach?"**
````

- [ ] **Step 3: Check that no tier claim is left**

```bash
grep -n -i -E 'pricier|stronger tier|standard model|model tier|inherit' skills/writing-plans/SKILL.md
```

Expected: no output.

- [ ] **Step 4: Record the adoption in NOTICE (spec R6.1)**

In `NOTICE`, add this bullet as the last item of the superpowers "Changes from upstream" list, directly above the blank line before `    brainstorming/`:

````text
  - One change was later adopted FROM upstream v6.3.0 (#2086), read at
    upstream 8ca22db: the plan header's `**Spec:**` line, placed after
    Tech Stack, naming the spec the plan implements or `none`.
````

- [ ] **Step 5: Mark finding 8's pointer adopted (spec R6.5)**

In `specs/superpowers-drift-spec.md`, make three replacements.

Replace:

````markdown
| 8 | Smaller items | `find-polluter.sh` still broken — its "fix directly" disposition was never carried out; two items now partly covered |
````

with:

````markdown
| 8 | Smaller items | `find-polluter.sh` still broken — its "fix directly" disposition was never carried out; two items now partly covered; the `Spec:` pointer adopted by plan 40 |
````

Replace:

````markdown
- **Plan `Spec:` header pointer — still absent.** Upstream has carried it since
  v6.3.0 (#2086). Its executing-plans now reads the spec at setup and ledgers a
  missing one, so rulings made without it are marked provisional. Our plan
  header (`writing-plans/SKILL.md:58-77`) has no such line. Plan 22 did not take
  it, and our `<id>-<spec-name>` naming couples plan and spec only by
  convention. Small, and it composes with finding 9.
````

with:

````markdown
- **Plan `Spec:` header pointer — adopted by plan 40.** Upstream has carried it
  since v6.3.0 (#2086). Our plan header now carries `**Spec:** <path>`, or
  `none`, after Tech Stack (`specs/handoff-briefs.md` R2.1). Upstream's
  executing-plans also reads the spec at setup and ledgers a missing one, so
  rulings made without it are marked provisional; that half belongs to finding
  11's port.
````

Replace:

````markdown
- **Done:** findings 1, 2, 5, and 6, through plan 22 (2026-09-03).
````

with:

````markdown
- **Done:** findings 1, 2, 5, and 6, through plan 22 (2026-09-03); finding 8's
  `Spec:` pointer, through plan 40.
````

Replace:

````markdown
- **Spec candidate, planning surface:** findings 9 and 10, plus finding 8's
  `Spec:` pointer. They share the writing-plans plan template and self-review,
  and finding 10 also reaches the four reviewer surfaces. Both shape
````

with:

````markdown
- **Spec candidate, planning surface:** findings 9 and 10. They share the
  writing-plans plan template and self-review, and finding 10 also reaches
  the four reviewer surfaces. Both shape
````

- [ ] **Step 6: Run the gates and commit**

Run the gate block. Then:

```bash
git add skills/writing-plans/SKILL.md NOTICE specs/superpowers-drift-spec.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "feat(writing-plans): add the Spec pointer and drop the tier premise"
```

### Task 10: writing-plans, the Entry Check section (C1)

**Executor:** implementer. **Gate:** C1.
- **NO-GO:** skip this task. Task 7's id rule stands. In the ledger, write `Task 10: skipped (C1 NO-GO)`.
- **GO:** do the steps below.

**Files:**
- Modify: `skills/writing-plans/SKILL.md` (the `:22` rule, and a new section before `## Scope Check`)
- Modify: `NOTICE` (Task 7's bullet)

**Interfaces:**
- Consumes:
  - Task 8's four report fields: `status:`, `since:`, `mentions:`, `plan ids:`;
  - Task 7's id rule.
- Produces: the `## Entry Check` section, which sits after the opening lines and before `## Scope Check`. Task 11's `## Starting From a Handoff Brief` goes between it and `## Scope Check`.

- [ ] **Step 1: Point the id rule at the report (R1.3)**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
`<id>` is the `next free:` id that `uv run --no-project --python 3.13 python <this-skill-dir>/scripts/entry_check.py` prints under `plan ids:`, run from the repo root. It reads every branch, remote-tracking ref and worktree, untracked plans included, because ids are allocated per branch and collide.
````

with:

````markdown
`<id>` is the `next free:` id in the Entry Check's report (below). The report reads every branch, remote-tracking ref and worktree, untracked plans included, because ids are allocated per branch and collide.
````

- [ ] **Step 2: Add the section (R1.2)**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
## Scope Check

If the spec covers multiple independent subsystems,
````

with:

````markdown
## Entry Check

Before planning, run from the repo root:

```bash
uv run --no-project --python 3.13 python <this-skill-dir>/scripts/entry_check.py <spec-path>
```

It prints four fields: `status:`, `since:`, `mentions:` and `plan ids:`. The
script reports; you judge. For each file under `mentions:`, read the section
around each hit: a plan's Global Constraints and scope fence, an audit's row,
a deferred item. A constraint may name the spec by a nickname, on a line the
script does not list.

Ask your human partner one batched question if any of these holds:

- a precondition aimed at this spec, unless you can point to the commit or
  file that meets it;
- a status that is not approved;
- commits since approval that you cannot reconcile with the spec;
- an id collision under `plan ids:`;
- an existing plan for this spec.

A clean report proceeds without comment. Without a spec, run the script with
no argument; it prints only `plan ids:`.

## Scope Check

If the spec covers multiple independent subsystems,
````

- [ ] **Step 3: Record the section in NOTICE**

In `NOTICE`, replace:

````text
    id rule now takes the next free id from that report.
````

with:

````text
    id rule now takes the next free id from that report, and a local
    Entry Check section runs the reporter before planning and asks one
    batched question on what it finds.
````

- [ ] **Step 4: Run the gates and commit**

Run the gate block. Then:

```bash
git add skills/writing-plans/SKILL.md NOTICE && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "feat(writing-plans): add the entry check before planning"
```

### Task 11: writing-plans, decisions and plan review (C2)

**Executor:** implementer. **Gate:** C2.
- **GO:** Steps 1–6 and 8.
- **NO-GO:** Steps 7 and 8 only. R2.1 and C3 already shipped in Task 9.

**Files:**
- Modify: `skills/writing-plans/SKILL.md`: the template; a new section before `## Scope Check`; the Execution Handoff
- Modify: `NOTICE` (Task 9's adoption bullet; GO only)
- Modify: `specs/superpowers-drift-spec.md` (finding 11, Suggested disposition)

**Interfaces:**
- Consumes:
  - Task 9's Execution Handoff and NOTICE adoption bullet;
  - Task 10's `## Entry Check`, if it shipped.
- Produces:
  - **The template's `## Decisions` section.** Each entry reads `- **D<n>** (owner, <brief | plan review>, YYYY-MM-DD): <decision>. Applied in: <…>.`
  - **The Execution Handoff's `### 1. Plan review` and `### 2. Execution choice`.** Task 18 adds R4.9's sentence to `### 1. Plan review`, after its Spec-level bullet.
  - **`## Starting From a Handoff Brief`.**

- [ ] **Step 1: The template's `## Decisions` (R2.2)**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

---
````

with:

````markdown
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

## Decisions

[One line per decision your human partner took after the spec was approved:
`- **D<n>** (owner, <brief | plan review>, YYYY-MM-DD): <decision>. Applied in: <Task N | Global Constraints | Task N (spec amendment)>.`
An empty section reads `None.`]

---
````

- [ ] **Step 2: Starting from a brief (R2.5)**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
## Scope Check

If the spec covers multiple independent subsystems,
````

with:

````markdown
## Starting From a Handoff Brief

When the session began from a handoff brief:

- Read the artifact at or after the brief's earliest commit.
- Log each of the brief's decisions in `## Decisions` with source `brief`,
  applied where its Home says.
- Settle each default the brief flags in the plan, and list it for your human
  partner's review.
- Honor the brief's owner gates and its leave-alone list.

## Scope Check

If the spec covers multiple independent subsystems,
````

- [ ] **Step 3: The plan review and execution choice (R2.3, R2.4)**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
**Recommend a fresh session for execution.** A planning session accumulates
context; carrying it into execution makes every execution turn re-read that
planning history at cache-read cost. Starting execution fresh drops it. Choose
the execution model when you launch it: `claude --model <m>`, `codex -m <m>`
or `gemini -m <m>`. `/clear` keeps the current model, and `/model` saves a new
default for later sessions.

**"Plan complete and saved to `specs/plans/<id>-<spec-name>.md`.**

**Recommended: `/clear` (or open a new session) and execute against the saved
plan** — a fresh session drops this planning conversation. Two execution
options, either session:

**1. Subagent-Driven (recommended)** - a fresh subagent per task, two-stage review between tasks

**2. Inline Execution** - I execute the tasks myself, in plan order (executing-plans)

Continuing in THIS session works too, but costs more on a long plan: every
execution turn re-reads the full planning history. **Which approach?"**
````

with:

````markdown
### 1. Plan review

**"Plan complete and saved to `specs/plans/<id>-<spec-name>.md`. Please review
it before anything runs."**

Apply each decision your human partner takes, and log it in `## Decisions`:

- **Plan-level** (it changes tasks or Global Constraints): edit them, and log
  where it applies.
- **Spec-level** (it changes what the spec requires): never edit the spec
  while planning. Add an amendment task: exact replace-this-with-that blocks
  for the spec, each edit tagged `(owner, plan <id>, YYYY-MM-DD)`, the spec's
  status line untouched. Show your partner the exact wording; it is approved
  at this review.

Re-run Self-Review on whatever changed, then move to the execution choice once
your partner approves the plan.

### 2. Execution choice

**Recommend a fresh session for execution.** A planning session accumulates
context; carrying it into execution makes every execution turn re-read that
planning history at cache-read cost. Starting execution fresh drops it. Choose
the execution model when you launch it: `claude --model <m>`, `codex -m <m>`
or `gemini -m <m>`. `/clear` keeps the current model, and `/model` saves a new
default for later sessions.

Recommend one option, with a reason drawn from this plan: Subagent-Driven by
default, Inline when the tasks are tightly coupled.

**"Recommended: `/clear` (or open a new session) and execute against the saved
plan** — a fresh session drops this planning conversation. Two execution
options, either session:

**1. Subagent-Driven** - a fresh subagent per task, two-stage review between tasks

**2. Inline Execution** - I execute the tasks myself, in plan order (executing-plans)

I recommend <1 or 2>, because <a reason drawn from this plan>. Continuing in
THIS session works too, but costs more on a long plan: every execution turn
re-reads the full planning history. **Which approach?"**
````

- [ ] **Step 4: Check the section order**

```bash
grep '^## \|^### [12]\.' skills/writing-plans/SKILL.md
```

Expected, in this order. The grep also prints three headings that sit inside the skill's own code fences, marked here; `## Entry Check` prints only if Task 10 shipped:

```text
## Overview
## Entry Check
## Starting From a Handoff Brief
## Scope Check
## File Structure
## Task Right-Sizing
## Bite-Sized Task Granularity
## Plan Document Header
## Global Constraints                (inside the plan template)
## Decisions                         (inside the plan template)
## Task Structure
## No Placeholders
## Remember
## Self-Review
## Execution Handoff
### 1. Plan review
### 2. Execution choice
## Plan Completion Protocol
## 7-rate-limiter — 2026-07-04       (inside the deferred-items example)
```

- [ ] **Step 5: Record the adoption in NOTICE (spec R6.1)**

In `NOTICE`, replace:

````text
  - One change was later adopted FROM upstream v6.3.0 (#2086), read at
    upstream 8ca22db: the plan header's `**Spec:**` line, placed after
    Tech Stack, naming the spec the plan implements or `none`.
````

with:

````text
  - Two changes were later adopted FROM upstream, both read at upstream
    8ca22db: the plan header's `**Spec:**` line (v6.3.0, #2086), placed
    after Tech Stack, naming the spec the plan implements or `none`; and
    the partner plan-review stage of writing-plans' Execution Handoff
    (v6.4.1, #2258 and #2318), which asks the partner to review the saved
    plan before the execution choice, then recommends one option with a
    reason drawn from the plan. Three parts diverge deliberately.
    Decisions taken at review are logged in a local `## Decisions`
    section of the plan, saying who took each, when, and where it
    applies, beside a local section for starting from a handoff brief.
    A decision that changes the spec becomes a tagged amendment task,
    never an edit made during planning. And there is no Native mode:
    this repo's executing-plans is not ported (finding 11 of
    specs/superpowers-drift-spec.md).
````

- [ ] **Step 6: Mark finding 11's handoff half adopted (spec R6.5)**

In `specs/superpowers-drift-spec.md`, make three replacements.

Replace:

````markdown
saved plan before anything runs. It offers Subagent-driven and Native, says what
each costs, and recommends one with a reason drawn from the plan.
````

with:

````markdown
saved plan before anything runs. It offers Subagent-driven and Native, says what
each costs, and recommends one with a reason drawn from the plan. Plan 40
adopted this handoff half without Native mode (`specs/handoff-briefs.md`
R2.2–R2.4); the executing-plans port below stays open.
````

Replace:

````markdown
- **Done:** findings 1, 2, 5, and 6, through plan 22 (2026-09-03); finding 8's
  `Spec:` pointer, through plan 40.
````

with:

````markdown
- **Done:** findings 1, 2, 5, and 6, through plan 22 (2026-09-03); finding 8's
  `Spec:` pointer and finding 11's handoff half, through plan 40.
````

Replace:

````markdown
  - Finding 11, the executing-plans port, which merits its own spec once 7 is
    settled. Finding 13's TDD wording travels with it, micro-tested.
````

with:

````markdown
  - Finding 11's executing-plans port, which merits its own spec once 7 is
    settled; its handoff half was adopted by plan 40. Finding 13's TDD wording
    travels with it, micro-tested.
````

Go to Step 8.

- [ ] **Step 7: NO-GO only, record finding 11's handoff half as not adopted (spec R6.5)**

In `specs/superpowers-drift-spec.md`, replace:

````markdown
saved plan before anything runs. It offers Subagent-driven and Native, says what
each costs, and recommends one with a reason drawn from the plan.
````

with the text below. Replace `<record>` with the RED record's path from Task 6.

````markdown
saved plan before anything runs. It offers Subagent-driven and Native, says what
each costs, and recommends one with a reason drawn from the plan. Plan 40's
no-guidance baseline did not show the failure this half fixes, so it was not
adopted (`<record>`, C2); the executing-plans port below stays open.
````

- [ ] **Step 8: Run the gates and commit**

Run the gate block. Then commit. On GO:

```bash
git add skills/writing-plans/SKILL.md NOTICE specs/superpowers-drift-spec.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "feat(writing-plans): log decisions and review the plan before execution"
```

On NO-GO:

```bash
git add specs/superpowers-drift-spec.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "docs(specs): record finding 11's handoff half as not adopted"
```

### Task 12: GREEN, Phase 1 (owner)

**Executor:** controller, then owner, then controller. The REFACTOR rounds use implementers.

**Files:**
- Modify: `specs/red-baseline-handoff-briefs-<date>.md` (its `## GREEN results`)
- Modify, only in a REFACTOR round: the skill text Tasks 9–11 changed
- Create (not in git): kit `k-b`, the GREEN reps and their results

**Interfaces:**
- Consumes:
  - Task 6's gates and RED counts;
  - Tasks 7–11's commits;
  - PROTOCOL.md's Arms, Thresholds and REFACTOR sections.
- Produces:
  - Phase 1's GREEN verdicts in the record;
  - any REFACTOR commits.

- [ ] **Step 1: Build kit `k-b` from the branch head**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./build_kit.sh k-b "$(git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs rev-parse --short HEAD)"
```

Expected: `kit k-b from <sha>: 11 skills`.

- [ ] **Step 2: Make the reps for the text that shipped**

Run the lines that apply, then count the batch:

```bash
cd ~/.cache/agent-skills/handoffs/red/tools
# C1 GO:
./make_reps.py c1 green1 k-b 5 green1 && ./make_reps.py p1 green1 k-b 5 green1 && ./make_reps.py v3 green1 k-b 3 green1
# C2 GO:
./make_reps.py c2 green1 k-b 5 green1 && ./make_reps.py p2 green1 k-b 5 green1 && ./make_reps.py c2b green1 k-b 5 green1
# C2 NO-GO (C3 is then scored on its own arm):
./make_reps.py c3 green1 k-b 5 green1
wc -l < ../batches/green1.txt
```

Expected: 13 reps for C1 GO, plus 15 for C2 GO or 5 for C2 NO-GO.

- [ ] **Step 3: Hand the batch to your human partner (hard stop)**

> **GREEN Phase 1 — your step.** In a plain terminal:
> ```bash
> ~/.cache/agent-skills/handoffs/red/tools/run_batch.sh -j 3 green1
> ```
> The batch resumes where it stopped if interrupted. Reply "green1 done".

- [ ] **Step 4: Audit, and replace void reps**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./extract.py green1
```

For each arm with fewer valid reps than it counts (5; 3 for `v3`):
1. Make that many new reps: `./make_reps.py <arm> green1 k-b <n> green1-r1`.
2. Hand `run_batch.sh green1-r1` to your human partner, as in Step 3.
3. Extract again.

Stop at 10 dispatched for an arm. That arm is then UNSETTLED; report it, and your human partner decides.

- [ ] **Step 5: Score each arm**

Dispatch one scorer subagent per arm, on the standard tier. Give each:
- `rubric.md`, and its arm's section by name;
- the arm's valid reps, each `results/<rep>/extract.md`;
- the output path `~/.cache/agent-skills/handoffs/red/scores/green1/<arm>.tsv`;
- the rule that every PASS, FAIL or VOID line carries a verbatim quote from the extract.

Extra criteria:
- The `c2` scorer, or the `c3` scorer when that arm ran, also writes C3-a to C3-d.
- `c1` and `p1` are scored on F-ask as well, which is GREEN only.

Then:

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./tally.py green1
```

Expected: exit 0, and one line per arm. The `c2` or `c3` line carries a `C3 PASS` or `C3 FAIL` part, compared against RED. If it exits 1, the listed lines go back to their scorer.

- [ ] **Step 6: REFACTOR any failing arm (PROTOCOL.md, REFACTOR)**

For each arm whose verdict is FAIL, take round N = 1, 2, 3:

1. **Revise.** Dispatch an implementer with:
   - the arm's tally line;
   - its FAIL lines (rep, criterion, quote);
   - its rubric section;
   - the text under test: Task 10's section for `c1`, `p1` and `v3`; Task 11's for `c2`, `p2` and `c2b`; Task 9's model line for C3.

   The implementer revises only that text, within the spec's requirement, and never touches a gate. Then it runs the gate block, and commits as `fix(writing-plans): <what changed> (plan 40 REFACTOR <N>)`.
2. **Rebuild.** Build kit `k-br<N>` from the new head.
3. **Re-run.** Make 5 new reps of the arm (3 for `v3`) into batch and phase `refactor<N>-<arm>`, with kit `k-br<N>`. Hand the batch to your human partner, as in Step 3. Then extract, score into `scores/refactor<N>-<arm>/`, and tally that phase.

Stop at a PASS. After three failing rounds, stop and give your human partner three choices: ship as is, take the NO-GO variant, or descope. Apply their choice. Taking a NO-GO variant means reverting this phase's commits for that component, and applying the gated task's NO-GO steps.

- [ ] **Step 7: Record Phase 1's results, and commit**

In the record's `## GREEN results`, add the block below. Use the real counts, one line of paraphrase per failure, and no transcript text.

```markdown
### Phase 1 — writing-plans (kit k-b, `<sha>`, <YYYY-MM-DD>)

| Arm | Valid | Failing reps | Per criterion | Verdict |
|---|---|---|---|---|
| `<arm>` | <n> | <n> | <criterion> <n>, … | <PASS / FAIL> |

- C3, on `<c2 or c3>`: C3-a <n>, C3-b <n>, C3-c <n>, C3-d <n> of 5, against RED's <counts>: <PASS / FAIL>.
- REFACTOR: <none>, or one line per round: its kit, what changed, its verdict.
- Evidence: <rep> <criterion>: <paraphrase>, one line per failure.
```

Run the gate block. Then:

```bash
git add specs/red-baseline-handoff-briefs-*.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "docs(specs): record plan 40's GREEN Phase 1 results"
```

In the ledger, write `Task 12: complete (commits <base7>..<head7>; arms <verdicts>)`.

## Phase 2 — the roadmap loop: C5 (spec R7)

A **roadmap stage** is a plan whose header carries a line that reads, after any `> ` prefix, `Roadmap: specs/<name>-roadmap.md, Stage N`. `N` may be alphanumeric, such as `S2.2b`. C5's text acts only on such plans. Every other plan completes as it does today.

### Task 13: derive-roadmap, the ungated edits (R7.5, R7.4's §4 sentence)

**Executor:** implementer. **Gate:** none (spec R7.6, Decision 17).

**Files:**
- Modify: `skills/derive-roadmap/references/roadmap-format.md:42-44`, `:57-60`
- Modify: `skills/derive-roadmap/SKILL.md:112-113`, `:117-118`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - **The stamp form,** placed under the stage's roadmap entry: `> Stage N: COMPLETE (YYYY-MM-DD) — implemented by plan <id> (path).`, then the optional `Its Handoff section names what <stages> consume.`, then `> Next: resume the roadmap.` on its own line. Task 14's step 3a writes this form.
  - **The §4 stance sentence.** Task 15 adds its "Handing off a stage" block after it.
  - **§5's first paragraph,** which names the stamp "under its roadmap entry". Task 15 leaves it as is.

- [ ] **Step 1: The carriers (R7.5)**

In `skills/derive-roadmap/references/roadmap-format.md`, replace:

````markdown
**Consumes/Produces are load-bearing.** The roadmap and the spec are the
ONLY cross-stage carriers — a stage's implementer sees neither the previous
stage's session nor its plan.
````

with:

````markdown
**Consumes/Produces are load-bearing.** The roadmap, the spec and each
completed stage plan's `## Handoff to later stages` section are the ONLY
cross-stage carriers — a stage's implementer sees neither the previous stage's
session nor the rest of its plan. A field may cite `plan <id>, Handoff`, and a
point settled at a resume carries `(Resolved at resume, YYYY-MM-DD)`.
````

- [ ] **Step 2: The stamp (R7.5)**

In `skills/derive-roadmap/references/roadmap-format.md`, replace:

````markdown
On completion the stamp becomes authoritative:

> Stage N: COMPLETE (YYYY-MM-DD) — implemented by plan <id> (path).
> Next: resume the roadmap.
````

with:

````markdown
On completion, a stamp goes under the stage's entry in the roadmap, the one
addition to its fields, and it is authoritative:

> Stage N: COMPLETE (YYYY-MM-DD) — implemented by plan <id> (path). Its Handoff section names what <stages> consume.
> Next: resume the roadmap.

The second sentence points at the plan's `## Handoff to later stages`. Drop it
when the plan has no such section, or when the section reads `None`.
````

The `Roadmap:` line above it does not change (R7.5).

- [ ] **Step 3: The between-stages sentence (R7.4)**

In `skills/derive-roadmap/SKILL.md`, replace:

````markdown
The between-stages go/no-go is user-initiated via "resume the roadmap". Do
not volunteer the next stage.
````

with:

````markdown
Between stages, the completed stage's execution session recommends resuming
the roadmap, and your human partner decides by launching the resume. Never
volunteer a stage outside a resume.
````

- [ ] **Step 4: Where §5 reads the stamp**

In `skills/derive-roadmap/SKILL.md`, replace:

````markdown
On re-entry, for each stage: the stage stamp in its spec's Rollout note
````

with:

````markdown
On re-entry, for each stage: the stage stamp under its roadmap entry
````

- [ ] **Step 5: Check the copy that must not change**

```bash
grep -n 'Roadmap: specs/<name>-roadmap.md, Stage N' skills/derive-roadmap/references/roadmap-format.md skills/describe-critique-methodology/references/spec-synthesis.md && git diff --quiet "$(awk '/^BASE40:/ {print $2}' .sdd/40-handoff-briefs/progress.md)" -- skills/describe-critique-methodology && echo untouched
```

Expected: one hit in each file, then `untouched`.

- [ ] **Step 6: Run the gates and commit**

Run the gate block. Then:

```bash
git add skills/derive-roadmap/SKILL.md skills/derive-roadmap/references/roadmap-format.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "docs(derive-roadmap): stamp under the roadmap entry; the resume is recommended, never volunteered"
```

### Task 14: completing a roadmap stage (C5a: R7.1, R7.2, R7.7)

**Executor:** implementer. **Gate:** C5a.
- **NO-GO:** skip this task. In the ledger, write `Task 14: skipped (C5a NO-GO)`.
- **GO:** do the steps below.

**Files:**
- Modify: `skills/writing-plans/SKILL.md` (a step 3a in the Plan Completion Protocol)
- Modify: `skills/subagent-driven-development/SKILL.md` (Plan Completion; the Integration line)
- Modify: `skills/executing-plans/SKILL.md` (a new Step 6)
- Modify: `NOTICE` (the superpowers change list)

**Interfaces:**
- Consumes: Task 13's stamp form.
- Produces:
  - **Step 3a,** ending `These edits land with the protocol's other commits.` Task 18 appends R4.9's sentence after that line.
  - **The B3 handoff lines,** the same in both executors.

- [ ] **Step 1: Step 3a (R7.1)**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
**4. Backlog triage.** Report backlog health, then bring the triage to your
````

with:

````markdown
**3a. Hand off a roadmap stage.** Only when the plan's header carries a line
that reads, after any `> ` prefix, `Roadmap: specs/<name>-roadmap.md, Stage N`
(N may be alphanumeric, such as `S2.2b`). For this session, that line's
"re-validate later stages against what shipped" means writing the section
below; amending later stages' entries is derive-roadmap's job, at the resume.

- **Handoff section.** Add `## Handoff to later stages` to the plan, with one
  bullet for each later stage whose `Consumes` this stage feeds. Each bullet
  gives what that stage consumes as built (names, paths, interfaces); where
  that differs from this stage's roadmap `Produces`; traps and refusals found
  in execution; and items deferred into that stage, by their
  `specs/deferred_items.md` section. Cite the spec; never restate it. When
  nothing differs, the section reads
  `None: shipped as the roadmap's Produces states.`; for the last stage,
  `None: last stage.`
- **Tick and stamp.** Tick the stage's box in the roadmap, and put this stamp
  under its entry. The path is the plan's retired path, since step 5 moves
  the plan. Drop the second sentence when the section reads `None`.

  ```
  > Stage N: COMPLETE (YYYY-MM-DD) — implemented by plan <id> (specs/plans/completed/<file>). Its Handoff section names what <stages> consume.
  > Next: resume the roadmap.
  ```

These edits land with the protocol's other commits.

**4. Backlog triage.** Report backlog health, then bring the triage to your
````

- [ ] **Step 2: The B3 handoff in subagent-driven-development (R7.2)**

In `skills/subagent-driven-development/SKILL.md`, replace:

````markdown
and the `specs/deferred_items.md` entries. Deleting the workspace first
destroys the protocol's input.
````

with:

````markdown
and the `specs/deferred_items.md` entries. Deleting the workspace first
destroys the protocol's input.

**A roadmap stage** (its plan header carries a `Roadmap:` line) ends by the
outcome of finishing-a-development-branch. Merged locally: "Stage N of
`<roadmap>` is merged. Next: /clear (or a fresh session), then resume the
roadmap: derive-roadmap on `<roadmap>`." Then stop. PR opened: "Resume the
roadmap once `<PR>` merges." Kept: "Stage N is complete on `<branch>` but
unmerged. Resume the roadmap after it merges." Discarded: no handoff, since
the stamp went with the branch. Never plan, brainstorm or name the next
stage, and make no model-tier claim.
````

Then replace:

````markdown
**After all tasks:** run the plan-completion protocol, then use finishing-a-development-branch to integrate the branch (merge / PR / cleanup) and remove any worktree.
````

with:

````markdown
**After all tasks:** run the plan-completion protocol, then use finishing-a-development-branch to integrate the branch (merge / PR / cleanup) and remove any worktree. For a roadmap stage, end with the resume handoff in Plan Completion.
````

- [ ] **Step 3: Step 6 in executing-plans (R7.2)**

In `skills/executing-plans/SKILL.md`, replace:

````markdown
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help
````

with:

````markdown
- Follow that skill to verify tests, present options, execute choice

### Step 6: Hand Off a Roadmap Stage

When the plan's header carries a `Roadmap:` line, end by the outcome of
finishing-a-development-branch:

| Outcome | Final message |
|---|---|
| Merged locally | "Stage N of `<roadmap>` is merged. Next: /clear (or a fresh session), then resume the roadmap: derive-roadmap on `<roadmap>`." Then stop. |
| PR opened | "Resume the roadmap once `<PR>` merges." |
| Kept | "Stage N is complete on `<branch>` but unmerged. Resume the roadmap after it merges." |
| Discarded | No handoff: the stamp went with the branch. |

Never plan, brainstorm or name the next stage, and make no model-tier claim.
Any other plan ends at Step 5.

## When to Stop and Ask for Help
````

- [ ] **Step 4: Check the size line**

```bash
wc -l < skills/subagent-driven-development/SKILL.md
```

Expected: at most 500. It was 489 at planning.

- [ ] **Step 5: Record the additions in NOTICE (R7.7)**

In `NOTICE`, add this bullet as the last item of the superpowers "Changes from upstream" list, directly above the blank line before `    brainstorming/`:

````text
  - writing-plans' Plan Completion Protocol gained a step 3a, and
    subagent-driven-development and executing-plans a closing handoff,
    for a plan that is a stage of a derive-roadmap roadmap. The plan
    records what later stages consume in a `## Handoff to later stages`
    section, the roadmap's stage is ticked and stamped, and the session
    ends by recommending that the roadmap be resumed. These are original
    local additions: upstream has no roadmap.
````

- [ ] **Step 6: Run the gates and commit**

Run the gate block. The dependency-drift test must still pass: the new text names derive-roadmap only by its bare name (R7.7). Then:

```bash
git add skills/writing-plans/SKILL.md skills/subagent-driven-development/SKILL.md skills/executing-plans/SKILL.md NOTICE && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "feat(writing-plans): hand off a completed roadmap stage to the resume"
```

### Task 15: resuming the roadmap (C5b: R7.3, R7.4)

**Executor:** implementer. **Gate:** C5b.
- **NO-GO:** skip this task. In the ledger, write `Task 15: skipped (C5b NO-GO)`.
- **GO:** do the steps below.

**Files:**
- Modify: `skills/derive-roadmap/SKILL.md`: §4, §5 and the Quick reference

**Interfaces:**
- Consumes:
  - Task 13's §4 stance sentence and §5 first paragraph;
  - the Handoff section and stamp forms (Tasks 13 and 14).
- Produces: §5's Commit bullet, which ends `so the fresh session reads them.` Task 18 adds R4.9's sentence after it.

- [ ] **Step 1: Handing off a stage (R7.4)**

In `skills/derive-roadmap/SKILL.md`, replace:

````markdown
Between stages, the completed stage's execution session recommends resuming
the roadmap, and your human partner decides by launching the resume. Never
volunteer a stage outside a resume.
````

with:

````markdown
Between stages, the completed stage's execution session recommends resuming
the roadmap, and your human partner decides by launching the resume. Never
volunteer a stage outside a resume.

**Handing off a stage**, after §4's approval or §5's reconcile:

- The next stage is the first unticked one whose `Consumes` are all met.
- End with "Next: /clear (or a fresh session), then <ROUTING skill> on Stage N
  of `specs/<name>-roadmap.md`", and name the line the receiver carries:
  - ROUTING brainstorming: the new stage spec's Rollout note carries the
    `Roadmap:` line.
  - ROUTING writing-plans: the plan header carries it, and the plan is scoped
    to the stage entry's `Spec` refs. This covers a stage with no stage spec.
- Then stop. Launching that session is your human partner's go/no-go.
````

- [ ] **Step 2: The reconcile (R7.3)**

In `skills/derive-roadmap/SKILL.md`, replace:

````markdown
Re-validate every unticked stage against what actually shipped, then route
the next one per its ROUTING line.
````

with:

````markdown
For each stage stamped COMPLETE since the last resume, read the stamp and its
plan's `## Handoff to later stages`. Re-validate every unticked stage against
what actually shipped:

- **Amend.** When a Handoff bullet changes a later stage's `Spec`, `Consumes`,
  `Produces` or `Exit`, amend that entry: cite `plan <id>, Handoff`, mark each
  settled point `(Resolved at resume, YYYY-MM-DD)`, and never restate.
- **Ask.** A stage added, split, dropped or reordered is not an amendment. Put
  every such change to your human partner as one batched question, before
  anything routes.
- **Commit** the amendments on the current branch before the handoff, so the
  fresh session reads them.

Then hand off the next stage (§4). With every stage ticked, go to §6.
````

- [ ] **Step 3: The Quick reference row**

In `skills/derive-roadmap/SKILL.md`, replace:

````markdown
| A document carrying the roadmap header (`REQUIRED SKILL … resume via its reconcile step`) | Reconcile via stamps, route the next unticked stage |
````

with:

````markdown
| A document carrying the roadmap header (`REQUIRED SKILL … resume via its reconcile step`) | Reconcile via stamps and Handoff sections, amend and commit, then hand off the next stage |
````

- [ ] **Step 4: Run the gates and commit**

Run the gate block. Then:

```bash
git add skills/derive-roadmap/SKILL.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "feat(derive-roadmap): read Handoff sections at the resume and hand off the next stage"
```

### Task 16: GREEN, Phase 2 (owner), and the shape check

**Executor:** controller, then owner, then controller. The REFACTOR rounds use implementers.

**Files:**
- Modify: the RED record's `## GREEN results`
- Modify, only in a REFACTOR round: the text Tasks 14–15 added
- Create (not in git): kit `k-c`, and the reps

**Interfaces:**
- Consumes:
  - Tasks 13–15's commits;
  - Task 6's gates;
  - PROTOCOL.md.
- Produces:
  - Phase 2's verdicts;
  - Validation 8's result, which the completion markup copies into this plan as a note under Step 1.

- [ ] **Step 1: Validation 8, the shape check (read-only)**

Read alt-nfp-stats without changing it:

```bash
git -C /Users/lowell/Projects/alt-nfp-stats show HEAD:specs/bls-stats-merge-roadmap.md | grep -n -B 9 -A 1 '^      > Stage S2.2: COMPLETE' && git -C /Users/lowell/Projects/alt-nfp-stats show HEAD:specs/plans/completed/28-bls-stats-merge-s2.2.md | grep -n -A 8 '^## Handoff to later stages'
```

Compare that with step 3a's section and stamp (Task 14), or, if C5a is NO-GO, with the format's stamp (Task 13). Check four things:
1. The stamp sits under the stage's entry.
2. The stamp opens `> Stage <label>: COMPLETE (<date>) — implemented by plan <id> (specs/plans/completed/<file>).` and then names what later stages consume through the plan's Handoff section.
3. `> Next: resume the roadmap.` follows.
4. The plan has a `## Handoff to later stages` section with bullets per consuming stage.

alt-nfp-stats' stamp continues past "consume" with a colon and a summary. That is a superset of the prescribed form, not a mismatch. In the ledger, write `Validation 8: <match | mismatch: …>`.

- [ ] **Step 2: Build kit `k-c`, and make the reps**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./build_kit.sh k-c "$(git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs rev-parse --short HEAD)"
# C5a GO:
for arm in c5a-pos c5a-neg c5a-pr c5a-ep p5a; do ./make_reps.py "$arm" green2 k-c 5 green2; done
# C5b GO:
for arm in c5b-pos c5b-neg c5b-part p5b; do ./make_reps.py "$arm" green2 k-c 5 green2; done
wc -l < ../batches/green2.txt
```

Expected:
- `kit k-c from <sha>: 11 skills`;
- 25 reps for C5a GO, plus 20 for C5b GO.

If both gates are NO-GO, there are no reps. Skip to Step 7 and record that.

- [ ] **Step 3: Hand the batch to your human partner (hard stop)**

> **GREEN Phase 2 — your step.** In a plain terminal:
> ```bash
> ~/.cache/agent-skills/handoffs/red/tools/run_batch.sh -j 3 green2
> ```
> The batch resumes where it stopped if interrupted. Reply "green2 done".

- [ ] **Step 4: Audit, and replace void reps**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./extract.py green2
```

For each arm with fewer than 5 valid reps:
1. Make that many new reps: `./make_reps.py <arm> green2 k-c <n> green2-r1`.
2. Hand `run_batch.sh green2-r1` to your human partner.
3. Extract again.

Stop at 10 dispatched for an arm. That arm is then UNSETTLED; report it, and your human partner decides.

- [ ] **Step 5: Score each arm**

Dispatch one scorer subagent per arm, on the standard tier. Give each:
- `rubric.md`, and its arm's section by name;
- the arm's valid reps, each `results/<rep>/extract.md`;
- the output path `~/.cache/agent-skills/handoffs/red/scores/green2/<arm>.tsv`;
- the rule that every PASS, FAIL or VOID line carries a verbatim quote from the extract.

Then:

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./tally.py green2
```

Expected: exit 0, one line per arm. Negative arms pass only at 0 of 5 failing.

- [ ] **Step 6: REFACTOR any failing arm (PROTOCOL.md, REFACTOR)**

For each arm whose verdict is FAIL, take round N = 1, 2, 3:

1. **Revise.** Dispatch an implementer with:
   - the arm's tally line;
   - its FAIL lines;
   - its rubric section;
   - the text under test: Task 14's for the `c5a` arms and `p5a`; Task 15's for the `c5b` arms and `p5b`.

   The implementer revises only that text, within the spec's requirement, and never touches a gate. It runs the gate block, and commits as `fix(<skill>): <what changed> (plan 40 REFACTOR <N>)`.
2. **Rebuild.** Build kit `k-cr<N>` from the new head.
3. **Re-run.** Make 5 new reps of the failing arm and 5 of its negative counterpart into batch and phase `refactor<N>-<arm>`, with kit `k-cr<N>`. The counterparts: `c5a-neg` for any `c5a` arm or `p5a`; `c5b-neg` for any `c5b` arm or `p5b`. When the failing arm is the negative one, rerun its positive counterpart. Hand the batch to your human partner. Then extract, score into `scores/refactor<N>-<arm>/`, and tally.

Stop when both pass. After three failing rounds, stop and give your human partner three choices: ship as is, take the NO-GO variant, or descope. Apply their choice. Taking a NO-GO variant means reverting this phase's commits for that component.

- [ ] **Step 7: Record Phase 2's results, and commit**

In the record's `## GREEN results`, add:

```markdown
### Phase 2 — the roadmap loop (kit k-c, `<sha>`, <YYYY-MM-DD>)

| Arm | Valid | Failing reps | Per criterion | Verdict |
|---|---|---|---|---|
| `<arm>` | <n> | <n> | <criterion> <n>, … | <PASS / FAIL> |

- Validation 8 (shape check): <match, or the mismatch>.
- REFACTOR: <none>, or one line per round: its kit, what changed, its verdict.
- Evidence: <rep> <criterion>: <paraphrase>, one line per failure.
```

Run the gate block. Then:

```bash
git add specs/red-baseline-handoff-briefs-*.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "docs(specs): record plan 40's GREEN Phase 2 results"
```

In the ledger, write `Task 16: complete (commits <base7>..<head7>; arms <verdicts>; Validation 8 <result>)`.

## Phase 3 — prepare-handoff: C4 (spec R4, R5.5, R5.7, R6.1–R6.3)

### Task 17: the prepare-handoff skill (C4a, C4b)

**Executor:** implementer. **Gate:** C4a and C4b, by spec R5.2.

| C4a | C4b | What ships | Steps |
|---|---|---|---|
| GO | GO | the full skill | 1, 2, 4–8 |
| GO | NO-GO | the skill without the R4.4 recipe | 1, 2, 3d, 4–8 |
| NO-GO | GO | the recipe and the review; the description triggers on writing a brief | 1, 2, 3c, 4–8 |
| NO-GO | NO-GO | no skill; your human partner asks for briefs | skip this task and Tasks 18–20 |

On NO-GO/NO-GO, write in the ledger `Tasks 17-20: skipped (C4a NO-GO, C4b NO-GO: no skill)`. In every shipping row, also apply Step 3a when C1 is NO-GO, and Step 3b when C2 is NO-GO.

**Files:**
- Create: `skills/prepare-handoff/SKILL.md`
- Create: `skills/prepare-handoff/references/fact-checker.md`
- Create: `skills/prepare-handoff/references/cold-reader.md`
- Modify: `NOTICE` (the originals block), `CLAUDE.md:26`, `README.md:68` and `:284`

**Interfaces:**
- Consumes: Task 6's gates. Task 5's `/context` finding (spec R5.3) must show no dropped skill description. If it showed one, stop and ask your human partner before this task.
- Produces:
  - **The skill `prepare-handoff`.** Task 18 names it from writing-plans and derive-roadmap.
  - **Two reviewer templates,** each with exactly one `[BRIEF_PATH]` slot. `make_reps.py`'s `probe_prompt` fills that slot for the `fc` and `cr` arms (Task 19).

- [ ] **Step 1: Create the skill**

Create `skills/prepare-handoff/SKILL.md`:

````markdown
---
name: prepare-handoff
description: >
  Use when a session is about to hand its work to a fresh session — a spec to
  planning, a plan to execution, an SDD or roadmap checkpoint, or "/clear and
  continue" — while holding decisions, owner gates, defaults or constraints the
  artifact does not record; when writing a handoff brief or handoff prompt;
  when an approved spec is picked up in a later session with new decisions; or
  when a decision must stay out of a public repository.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# prepare-handoff

## Overview

A fresh session reads only what it is pointed at. Before handing work on,
sort what the next session needs. Most of it is already in the artifact, is
recomputed by the receiving session, or can be committed now. Only the rest
goes in a brief: a short file the next session starts from, never committed.

## 1. Sort

Put each thing the next session needs into one bin:

| Bin | Action |
|---|---|
| In the artifact | Nothing. The brief may point to it by section. |
| Recomputable by the receiver's entry check: status, commits since, files naming the artifact, plan ids | Nothing. |
| Amendable now, with your human partner approving the exact wording now | Amend and commit it: a spec amendment tagged `(owner, YYYY-MM-DD)`, a `## Decisions` entry in the plan, a deviation line in the subagent-driven-development ledger, a stage plan's `## Handoff to later stages`, or a derive-roadmap roadmap. |
| Everything else | The brief. |

Everything else includes decisions whose wording your partner approves later,
provisional defaults, traps only your own analysis found, owner gates,
leave-alone items, and anything that cannot be committed, such as a decision
that must stay out of a public repository.

If that last bin is empty, write no brief. The handoff stays "/clear (or a
fresh session), then <next skill> on <artifact>".

## 2. Write the brief

The parts come in this order. Every slot is required; an empty slot reads
`none`.

1. **Opening line:** the receiving skill, the artifact's path, the earliest
   commit to read, what to produce, and where to stop.
2. **Decisions.** Each `D<n>` has four fields:
   - *You said:* your partner's words, dated;
   - *Reading:* your interpretation of them;
   - *Home:* exactly one durable home, such as the plan's `## Decisions` or a
     spec amendment task;
   - *Approval:* now, or a named later point such as plan review.
3. **Defaults to flag:** each with its question, a recommended default, and
   the effect if it is wrong.
4. **Constraints and traps:** each with `path:line` evidence.
5. **Owner gates:** new gates, plus the artifact's own gates by section
   reference, never restated.
6. **Leave alone.**
7. **Closing line:** the brief's path, and "Record each decision in its Home;
   then this brief is disposable."

Carry nothing the artifact states and nothing the receiver recomputes, and do
not restate what the receiving skill does anyway.

## 3. Review

Check each claim against its source yourself. Then add reviewers by content:

- **Fact-checker** (`references/fact-checker.md`), when the brief cites repo
  or artifact text: paths, `path:line`, section numbers, ids, commits.
- **Cold reader** (`references/cold-reader.md`), when the brief carries a
  scope-changing decision or an owner gate.

Fill each template's `[BRIEF_PATH]`, and dispatch the reviewers in parallel as
read-only subagents, with no model pinned. Where the runtime cannot dispatch
subagents, ask your human partner to open a fresh session with the filled
template. Fix what they find, and put every ambiguity to your partner as one
batched question before the brief goes out. There is one round: a slot
changed afterwards gets your own check, and your partner may ask for another
round.

## 4. Store

Write the brief to `~/.cache/agent-skills/handoffs/<repo>/<YYYY-MM-DD>-<slug>.md`.
`<repo>` is the main worktree's directory name, the same from every worktree,
and `<slug>` names the receiving work. If the runtime refuses that write, use
`.handoff/` at the main worktree's root, with its own `.gitignore` holding `*`.

## 5. Memory

Update any memory entry the brief contradicts, and save a private decision to
the runtime's memory as well. On a runtime with no memory, tell your partner
that a private decision lives only in the brief.

## 6. Deliver

End with the brief's path, and "start a fresh session and paste it": the
route that works on every surface, the desktop app included. Then give one
launch line per runtime, leaving `<model>` to your partner:

```bash
claude --model <model> "$(cat <path>)"
codex -m <model> "$(cat <path>)"
gemini -m <model> -i "$(cat <path>)"
```

You may recommend a model, with a reason drawn from the receiving work; never
assume a default. `/model` saves a default for later sessions, while `--model`
applies to the one session only.

## Common mistakes

- **Restating the artifact** instead of pointing to its section.
- **A Reading presented as You said.** Keep your partner's words apart from
  your interpretation, and ask when they differ.
- **A decision with two homes,** such as an amendment that is also recorded as
  a deviation. One Home and one Approval per decision.
- **A hand-written plan-id check.** The receiving session computes ids.
- **No gates slot** because the artifact has gates. Point to them by section.
- **A brief when the last bin is empty.**
````

- [ ] **Step 2: Create the reviewer templates (R4.5)**

Create `skills/prepare-handoff/references/fact-checker.md`:

````markdown
# Fact-checker: a handoff brief

A sender wrote a handoff brief for a fresh session, and wants it checked
before it goes out. Read the brief at [BRIEF_PATH], and the repository it
names. Change nothing: this review is read-only.

Check every claim the brief makes about the repository or the artifact it
hands off: paths, `path:line` references, section and requirement numbers,
ids, commits, and quoted phrases. Open each source and compare. A claim can be
true to the letter and still mislead; say so when it does.

Report each problem as one block, numbered from 0:

```
--- [n] wrong | misleading | missing | nit
DRAFT: <the brief's text, verbatim>
PROBLEM: <what is wrong, in one or two sentences>
SUGGEST: <replacement text>
EVIDENCE: <path:line, or the command you ran, and what it showed>
```

A `missing` finding is a fact the receiver needs and the brief omits; its
DRAFT is the passage the fact belongs in. After the blocks, list what you
checked and found correct:

```
VERIFIED OK:
- <claim> — <evidence>
```
````

Create `skills/prepare-handoff/references/cold-reader.md`:

````markdown
# Cold reader: a handoff brief

You are the fresh session this brief will start. Read the brief at
[BRIEF_PATH], then what it points you to in the repository, and nothing else:
no memory, no earlier conversation. Change nothing: this review is read-only.

Read it as the receiver would, and report what would mislead or stall you:

- **contradiction:** two parts, or a part and the artifact, that cannot both
  hold;
- **ambiguity:** a part you could act on in two ways, or a question only the
  owner can answer;
- **trap:** an instruction that would lead you into a mistake;
- **padding:** text that restates the artifact, or what the receiving skill
  already does;
- **overreach:** the sender's reading presented as the owner's words, or a
  decision that goes further than what the owner said.

Report each as one block, numbered from 0:

```
--- [n] contradiction | ambiguity | trap | padding | overreach
DRAFT: <the brief's text, verbatim>
PROBLEM: <what goes wrong for the receiver>
SUGGEST: <replacement text, or the question to put to the owner>
EVIDENCE: <the brief's own lines, or path:line in the repository>
```
````

- [ ] **Step 3: Apply the variants that the gates call for**

**3a, when C1 is NO-GO.** In `skills/prepare-handoff/SKILL.md`, replace:

````markdown
| Recomputable by the receiver's entry check: status, commits since, files naming the artifact, plan ids | Nothing. |
````

with:

````markdown
| Recomputable by the receiver's checks: status, commits since, files naming the artifact, plan ids | Nothing. |
````

**3b, when C2 is NO-GO.** In `skills/prepare-handoff/SKILL.md`, replace:

````markdown
a `## Decisions` entry in the plan, a deviation line
````

with:

````markdown
the plan itself, a deviation line
````

Then replace:

````markdown
   - *Home:* exactly one durable home, such as the plan's `## Decisions` or a
     spec amendment task;
````

with:

````markdown
   - *Home:* exactly one durable home, such as the plan or a spec amendment
     task;
````

If Step 3d also applies, it removes that second passage; skip the second replacement then.

**3c, when C4a is NO-GO and C4b is GO (R4.2).** In `skills/prepare-handoff/SKILL.md`, replace the description's six lines:

````markdown
  Use when a session is about to hand its work to a fresh session — a spec to
  planning, a plan to execution, an SDD or roadmap checkpoint, or "/clear and
  continue" — while holding decisions, owner gates, defaults or constraints the
  artifact does not record; when writing a handoff brief or handoff prompt;
  when an approved spec is picked up in a later session with new decisions; or
  when a decision must stay out of a public repository.
````

with:

````markdown
  Use when writing a handoff brief or handoff prompt for a fresh session — a
  spec to planning, a plan to execution, an SDD or roadmap checkpoint, or
  "/clear and continue" — or when a decision must stay out of a public
  repository.
````

**3d, when C4a is GO and C4b is NO-GO (R5.2: no recipe).** In `skills/prepare-handoff/SKILL.md`, replace the whole `## 2. Write the brief` section, from its heading through `not restate what the receiving skill does anyway.`, with:

````markdown
## 2. Write the brief

Write what the last bin holds. Open with the receiving skill and the
artifact's path, and close with the brief's path and where each decision is
to be recorded. Carry nothing the artifact states and nothing the receiver
recomputes.
````

Then, in `## Common mistakes`, delete the three bullets that begin `- **A Reading presented as You said.**`, `- **A decision with two homes,**` and `- **No gates slot**`.

- [ ] **Step 4: Check the skill's form**

```bash
uv run --python 3.13 --with pyyaml python -c "import yaml; t = open('skills/prepare-handoff/SKILL.md').read(); d = yaml.safe_load(t.split('---')[1])['description']; print(len(d), d.startswith('Use when'))" && grep -c '\[BRIEF_PATH\]' skills/prepare-handoff/references/fact-checker.md skills/prepare-handoff/references/cold-reader.md
```

Expected: one line, `<length> True`, with the length under 1024. Then `:1` for each template.

- [ ] **Step 5: The originals entry in NOTICE (R6.1)**

In `NOTICE`, replace:

````text
    evaluate-deep-learning/
    optimize-jax/
````

with:

````text
    evaluate-deep-learning/
    optimize-jax/
    prepare-handoff/
````

- [ ] **Step 6: CLAUDE.md's originals bullet (R6.2)**

In `CLAUDE.md`, replace:

````text
`evaluate-deep-learning`, `optimize-jax`. (19 originals — keep in sync with `NOTICE`, which is authoritative.)
````

with:

````text
`evaluate-deep-learning`, `optimize-jax`, `prepare-handoff`. (20 originals — keep in sync with `NOTICE`, which is authoritative.)
````

The bullet stays one line. `build/test_check_provenance.py` checks the list and the count against NOTICE.

- [ ] **Step 7: The README row and Credits (R6.3)**

In `README.md`, add a row after the `derive-roadmap` row, as the last row of the `### Mine` table. Replace:

````markdown
into `specs/deferred_items.md`. |

### Clean-code family
````

with:

````markdown
into `specs/deferred_items.md`. |
| [`prepare-handoff`](skills/prepare-handoff/) | The sending half of a handoff between sessions. Before a fresh session takes over a spec, a plan or a checkpoint, it sorts what that session needs into four bins: already in the artifact, recomputed by the receiver, amendable and committed now, or everything else. Only the last goes into a brief, stored outside the repository and never committed. Fact-checker and cold-reader templates review the brief, and the final message gives one launch line per runtime, with the model left to the owner. |

### Clean-code family
````

Then replace:

````markdown
`deep-learning`, `evaluate-deep-learning`, and `optimize-jax` are my own work
````

with:

````markdown
`deep-learning`, `evaluate-deep-learning`, `optimize-jax`, and `prepare-handoff` are my own work
````

- [ ] **Step 8: Run the gates and commit**

Run the gate block. `check_provenance.py` now finds `prepare-handoff/` in NOTICE's originals, and the conformance checks read the new skill. Then:

```bash
git add skills/prepare-handoff NOTICE CLAUDE.md README.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "feat(prepare-handoff): add the sender's skill for session handoffs"
```

### Task 18: naming prepare-handoff from the senders (R4.9)

**Executor:** implementer. **Gate:** runs when Task 17 shipped a skill. Each step has its own condition.

**Files:**
- Modify: `skills/writing-plans/SKILL.md`; also step 3a, if Task 14 shipped
- Modify: `skills/derive-roadmap/SKILL.md`, if Task 15 shipped
- Modify: `NOTICE` (the superpowers change list)

**Interfaces:**
- Consumes:
  - Task 17's skill;
  - Task 11's `### 1. Plan review`, or else Task 9's Execution Handoff;
  - Task 14's step 3a;
  - Task 15's Commit bullet.
- Produces: the B2 route, which Task 19's `b2` arm tests.

- [ ] **Step 1: writing-plans, when C2 shipped (Task 11 GO)**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
  status line untouched. Show your partner the exact wording; it is approved
  at this review.
````

with:

````markdown
  status line untouched. Show your partner the exact wording; it is approved
  at this review.
- **Private** (it cannot be written into the plan, such as a decision that
  must stay out of a public repository): it goes to prepare-handoff instead.
````

- [ ] **Step 2: writing-plans, when C2 did not ship**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
this codebase — so execution does not need this planning session's history.
````

with:

````markdown
this codebase — so execution does not need this planning session's history.
A decision that cannot be written into the plan — one that must stay out of a
public repository, say — goes to prepare-handoff instead.
````

- [ ] **Step 3: step 3a, when Task 14 shipped**

In `skills/writing-plans/SKILL.md`, replace:

````markdown
These edits land with the protocol's other commits.
````

with:

````markdown
These edits land with the protocol's other commits. Context for a later stage
that cannot be committed goes to prepare-handoff.
````

- [ ] **Step 4: derive-roadmap's resume, when Task 15 shipped**

In `skills/derive-roadmap/SKILL.md`, replace:

````markdown
- **Commit** the amendments on the current branch before the handoff, so the
  fresh session reads them.
````

with:

````markdown
- **Commit** the amendments on the current branch before the handoff, so the
  fresh session reads them. Context for a later stage that cannot be
  committed goes to prepare-handoff.
````

- [ ] **Step 5: Record the mention in NOTICE**

In `NOTICE`, add this bullet as the last item of the superpowers "Changes from upstream" list, directly above the blank line before `    brainstorming/`:

````text
  - writing-plans names prepare-handoff, an original skill (above), as
    the home for a decision the plan cannot hold, such as one that must
    stay out of a public repository; and, where step 3a shipped, for
    context about a later roadmap stage that cannot be committed.
````

If Task 14 did not ship, end the bullet at `public repository.` instead.

- [ ] **Step 6: Run the gates and commit**

Run the gate block. The dependency-drift test confirms that the bare name adds no dependency (R6.4). Then:

```bash
git add skills/writing-plans/SKILL.md skills/derive-roadmap/SKILL.md NOTICE && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "feat(writing-plans): route a decision the plan cannot hold to prepare-handoff"
```

### Task 19: GREEN, Phase 3 (owner)

**Executor:** controller, then owner, then controller. The REFACTOR rounds use implementers.

**Files:**
- Modify: the RED record's `## GREEN results`
- Modify, only in a REFACTOR round: `skills/prepare-handoff/**`, or Task 18's sentences
- Create (not in git): kit `k-d`, the reps, and the `fc` and `cr` prompts

**Interfaces:**
- Consumes:
  - Tasks 17–18's commits;
  - Task 4's planted brief and its key;
  - PROTOCOL.md.
- Produces: Phase 3's verdicts, which are Validations 1, 2 and 4.

- [ ] **Step 1: Build kit `k-d`, and make the reps**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./build_kit.sh k-d "$(git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs rev-parse --short HEAD)"
# Whenever the skill shipped (Validations 2 and 4):
for arm in c4a-neg fc cr; do ./make_reps.py "$arm" green3 k-d 5 green3; done
# C4a GO:
./make_reps.py c4a-pos green3 k-d 5 green3
# C4b GO (Validation 1):
./make_reps.py v1 green3 k-d 5 green3
# C2 shipped (the B2 case, R5.5):
./make_reps.py b2 green3 k-d 5 green3
wc -l < ../batches/green3.txt && head -c 300 ../prompts/fc.k-d.t1.txt
```

Expected:
- `kit k-d from <sha>: 12 skills`;
- 15 reps, plus 5 for each conditional arm that applies;
- the fact-checker template's opening, with `@REP@/.handoff/plan-38-handoff.md` in place of `[BRIEF_PATH]`.

- [ ] **Step 2: Hand the batch to your human partner (hard stop)**

> **GREEN Phase 3 — your step.** In a plain terminal:
> ```bash
> ~/.cache/agent-skills/handoffs/red/tools/run_batch.sh -j 3 green3
> ```
> The batch resumes where it stopped if interrupted. Reply "green3 done".

- [ ] **Step 3: Audit, and replace void reps**

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./extract.py green3
```

For each arm with fewer than 5 valid reps:
1. Make that many new reps: `./make_reps.py <arm> green3 k-d <n> green3-r1`.
2. Hand `run_batch.sh green3-r1` to your human partner.
3. Extract again.

Stop at 10 dispatched for an arm. That arm is then UNSETTLED; report it, and your human partner decides.

- [ ] **Step 4: Score each arm**

Dispatch one scorer subagent per arm. Give each:
- `rubric.md`, and its arm's section by name;
- the arm's valid reps, each `results/<rep>/extract.md`;
- the output path `~/.cache/agent-skills/handoffs/red/scores/green3/<arm>.tsv`;
- the rule that every PASS, FAIL or VOID line carries a verbatim quote from the extract.

Arm by arm:
- `v1` is scored on the capable tier, with the rep repos at `~/.cache/pondworks/reps/<rep>/`, for F-unchecked. Give it the spec's Validation 1 table for V1-sort.
- The `fc` and `cr` scorers also get `briefs/plan-38-planted.key.md`.
- The `b2` scorer checks B2-out with `grep -rl Fenwick --exclude-dir=.git ~/.cache/pondworks/reps/<rep>`, and quotes the extract.
- The rest are scored on the standard tier.

Then:

```bash
cd ~/.cache/agent-skills/handoffs/red/tools && ./tally.py green3
```

Expected: exit 0, one line per arm.
- The probe arms print `P-f0 <n>/5, P-f1 <n>/5`, or `P-rt0 …, P-rt13 …`.
- `c4a-neg` passes at most 1 of 5 failing.

- [ ] **Step 5: REFACTOR any failing arm (PROTOCOL.md, REFACTOR)**

For each arm whose verdict is FAIL, take round N = 1, 2, 3:

1. **Revise.** Dispatch an implementer with:
   - the arm's tally line;
   - its FAIL lines;
   - its rubric section;
   - the text under test:
     - for `c4a-pos` and `c4a-neg`, the description and §1;
     - for `v1`, §1–§3;
     - for `fc`, the fact-checker template; for `cr`, the cold-reader template;
     - for `b2`, Task 18's writing-plans sentence and the description.

   It revises only that text, within the spec's requirement, and never touches a gate. It runs the gate block, and commits as `fix(prepare-handoff): <what changed> (plan 40 REFACTOR <N>)`.
2. **Rebuild.** Build kit `k-dr<N>`.
3. **Re-run.** Make 5 new reps of the failing arm into batch and phase `refactor<N>-<arm>`, plus 5 of its counterpart: `c4a-neg` for `c4a-pos` and `c4a-pos` for `c4a-neg` (when C4a is GO); `c4a-neg` for `b2`. Hand the batch to your human partner. Then extract, score into `scores/refactor<N>-<arm>/`, and tally.

Stop when both pass. After three failing rounds, stop and give your human partner three choices: ship as is, take the variant the gates' next row describes, or descope.

- [ ] **Step 6: Record Phase 3's results, and commit**

In the record's `## GREEN results`, add:

```markdown
### Phase 3 — prepare-handoff (kit k-d, `<sha>`, <YYYY-MM-DD>)

| Arm | Valid | Failing reps | Per criterion | Verdict |
|---|---|---|---|---|
| `<arm>` | <n> | <n> | <criterion> <n>, … | <PASS / FAIL> |

- Validation 1 (`v1`): <verdict>. Validation 2 (`c4a-neg`): <verdict>. Validation 4 (`fc`, `cr`): <verdict>.
- REFACTOR: <none>, or one line per round: its kit, what changed, its verdict.
- Evidence: <rep> <criterion>: <paraphrase>, one line per failure.
```

Run the gate block. Then:

```bash
git add specs/red-baseline-handoff-briefs-*.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "docs(specs): record plan 40's GREEN Phase 3 results"
```

In the ledger, write `Task 19: complete (commits <base7>..<head7>; arms <verdicts>)`.

### Task 20: smoke runs on Codex and Gemini (owner, spec R5.7)

**Executor:** controller, then owner, then controller. **Gate:** runs when Task 17 shipped a skill.

**Files:**
- Modify: the RED record (a `### R5.7 smoke runs` block under `## GREEN results`)
- Create (not in git): `~/.cache/pondworks/smoke/codex-smoke/`, `~/.cache/pondworks/smoke/gemini-smoke/`, `~/.cache/pondworks/smoke/prompt.txt`

**Interfaces:**
- Consumes: Task 17's skill at the branch head; template t3.
- Produces: Validation 5's result.

- [ ] **Step 1: Prepare the two smoke repos**

Neither runtime has the skill installed before the merge, so each repo carries a workspace copy:
- Codex reads the repo's `.agents/skills/`.
- For Gemini, `gemini skills install --scope workspace` writes `<repo>/.gemini/skills/`. It launches no session.

```bash
WT=/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-40-handoff-briefs && S=~/.cache/pondworks/smoke && mkdir -p "$S" && for r in codex-smoke gemini-smoke; do cp -R ~/.cache/pondworks/templates/t3 "$S/$r"; done && mkdir -p "$S/codex-smoke/.agents/skills" "$S/export" && git -C "$WT" archive HEAD skills/prepare-handoff | tar -x -C "$S/export" && cp -R "$S/export/skills/prepare-handoff" "$S/codex-smoke/.agents/skills/" && (cd "$S/gemini-smoke" && gemini skills install "$S/export/skills/prepare-handoff" --scope workspace --consent) && ls "$S/codex-smoke/.agents/skills" "$S/gemini-smoke/.gemini/skills"
```

Expected: `prepare-handoff` listed under each.

Then write `~/.cache/pondworks/smoke/prompt.txt`. It is two turns, the second after a blank line:

```
Use prepare-handoff. We approved specs/site-alert-email.md this morning, and it's committed. Since then I've decided three things. One: send at most one email per site per day, batching that day's alerts into it. Two: drop R5's SMS fallback entirely. Three: the sender address comes from the PONDWATCH_SENDER environment variable, not pondwatch.toml. I'll approve the exact spec wording for these at plan review, so don't change the spec now.

OK. I'll /clear and start planning in a fresh session.
```

The prompt names the skill. That way the run tests the runtime's mechanics, not the description's trigger, which Task 19 covered.

- [ ] **Step 2: Hand the smoke runs to your human partner (hard stop)**

> **Smoke runs — your steps (spec R5.7).** Use a plain terminal, and choose each model yourself.
>
> **Codex.**
> 1. Run `cd ~/.cache/pondworks/smoke/codex-smoke && codex -m <model>`.
> 2. Paste the first turn of `~/.cache/pondworks/smoke/prompt.txt`. When it answers, paste the second.
> 3. Note three things:
>    - (a) whether it loaded prepare-handoff;
>    - (b) where it wrote the brief: under `~/.cache/agent-skills/handoffs/codex-smoke/`, or under `.handoff/` if that write was refused;
>    - (c) whether the `codex` launch line it gives starts a session whose first turn is the brief. Try the line, then exit that session.
>
> **Gemini.** Do the same in `~/.cache/pondworks/smoke/gemini-smoke`, starting with `gemini -m <model>`, and try its `gemini -m <model> -i …` line.
>
> Reply with (a), (b) and (c) for each runtime, and the models you used.

- [ ] **Step 3: Record the results, clean up, and commit**

In the record's `## GREEN results`, add:

```markdown
### R5.7 smoke runs (<YYYY-MM-DD>)

| Runtime | Model | Skill loaded | Brief written | Launch line starts on the brief |
|---|---|---|---|---|
| Codex | <model> | <yes / no> | <yes, at …; or the fallback> | <yes / no> |
| Gemini | <model> | <yes / no> | <yes, at …; or the fallback> | <yes / no> |
```

Then remove the scratch:

```bash
rm -rf ~/.cache/pondworks/smoke ~/.cache/agent-skills/handoffs/codex-smoke ~/.cache/agent-skills/handoffs/gemini-smoke
```

Run the gate block. Then:

```bash
git add specs/red-baseline-handoff-briefs-*.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "docs(specs): record plan 40's Codex and Gemini smoke runs"
```

A failed smoke run goes to your human partner as a finding. It is not a REFACTOR round: R5.7 checks portability, and the fix may be runtime-side.

### Task 21: Acceptance

**Executor:** controller.

**Files:**
- Modify: the RED record (status line; a `## Acceptance` section)

**Interfaces:**
- Consumes: every earlier task.
- Produces: the record, closed and ready to retire with the plan (Global Constraints, **Retirement**).

- [ ] **Step 1: The gates (Validation 9)**

From the worktree root, run the gate block, then the runtime-adapter check:

```bash
uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check
```

Expected: all pass. This plan changed no agent or command, so the adapters need no regeneration.

- [ ] **Step 2: The leave-alone and scope checks**

```bash
B=$(awk '/^BASE40:/ {print $2}' .sdd/40-handoff-briefs/progress.md) && git diff --quiet "$B" HEAD -- specs/claude-code-drift-automation.md specs/plans/completed/38-claude-code-drift-automation.md install.py build runtimes agents commands skills/describe-critique-methodology && echo leave-alone-ok && git diff --name-only "$B" HEAD | sort
```

Expected: `leave-alone-ok`, then only paths from this list:
- `CLAUDE.md`, `NOTICE`, `README.md`;
- `skills/derive-roadmap/SKILL.md`, `skills/derive-roadmap/references/roadmap-format.md`;
- `skills/executing-plans/SKILL.md`;
- `skills/prepare-handoff/SKILL.md`, `skills/prepare-handoff/references/cold-reader.md`, `skills/prepare-handoff/references/fact-checker.md`;
- `skills/subagent-driven-development/SKILL.md`;
- `skills/writing-plans/SKILL.md`, `skills/writing-plans/scripts/entry_check.py`, `skills/writing-plans/scripts/test_entry_check.py`;
- `specs/red-baseline-handoff-briefs-<date>.md`;
- `specs/superpowers-drift-spec.md`.

Any other path is a finding for your human partner.

- [ ] **Step 3: Close the record**

In the record, set the status line to `**Date:** <RED date> · **Status:** COMPLETE (<YYYY-MM-DD>) — <n> reps across RED and GREEN; gates as below.` Then add, after `## GREEN results`:

```markdown
## Acceptance (spec, Validation and acceptance)

| # | Validation | Result | Where |
|---|---|---|---|
| 1 | Plan 38 through the design | <PASS / FAIL / not run: C4b NO-GO> | Phase 3, `v1` |
| 2 | Negative case | <…> | Phase 3, `c4a-neg` |
| 3 | Entry check on this repo | <script: plan 35 listed / not run: C1 NO-GO>; <agent: `v3` verdict> | Task 8 Step 5; Phase 1, `v3` |
| 4 | Probe | <…> | Phase 3, `fc` and `cr` |
| 5 | Smoke runs | <…> | R5.7 smoke runs |
| 6 | B3 on a fixture | <…> | Phase 2, `c5a-*`, `p5a` |
| 7 | B4 on a fixture | <…> | Phase 2, `c5b-*`, `p5b` |
| 8 | Shape check | <…> | Phase 2 |
| 9 | Gates | pass | Task 21 |
```

Run the gate block. Then:

```bash
git add specs/red-baseline-handoff-briefs-*.md && [ "$(git branch --show-current)" = feat/handoff-briefs ] && git commit -m "docs(specs): close plan 40's RED and GREEN record"
```

- [ ] **Step 4: Record completion, and carry the reminders**

In the ledger, write `Task 21: complete (commits <base7>..<head7>)`. Then go on to subagent-driven-development's final whole-branch review and Plan Completion.

Two reminders for the completion report:
- **R6.6.** If Task 17 shipped a skill, after the merge your human partner runs `python3 install.py all` from the main checkout, to link prepare-handoff for Claude, Codex and Gemini. This plan never runs it.
- **Validation 8.** At the completion markup, copy the ledger's `Validation 8:` line under Task 16 Step 1 as a `> Note:` line.
