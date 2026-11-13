# Branch Explainer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** finishing-a-development-branch gains Step 3b. Before the Step 4 menu, a fresh subagent writes an explainer of `BASE..HEAD`. After reading it, the owner can give a synopsis of the plan, the build and what the branch adds to the project. A baseline probe compares the new writer brief with no guidance first.

**Architecture:** A probe kit under `specs/baseline/red-baseline-branch-explainer/` builds an isolated repository for each fixture branch. In it, an Opus writer with repository tools writes an explainer, either with no guidance (control) or with the writer brief (treatment). A tool-less Opus reader writes a synopsis from the explainer, with the treatment's own Synopsis cut out. A tool-less Opus adjudicator scores bars B1 to B4, and the kit counts words for B5. The brief is tuned on three fixtures and then scored once on a held-out fourth. `SKILL.md` gets a short Step 3b pointer. The procedure goes into `references/branch-explainer.md` and the writer brief into `references/branch-explainer-prompt.md`. To make room in the body, Step 6's refused-removal detail moves to `references/refused-removal.md`. A decision-only micro-test checks Step 3b's wording and the move.

**Tech Stack:** Python 3.11+ standard library (a uv inline header), bash, `claude -p` 2.1.323 on `claude-opus-5-5` (probe) and `claude-sonnet-5-5` (micro-test), git, Markdown skill text, and the repo's commit lints.

**Spec:** `specs/branch-explainer.md` (APPROVED 2026-11-13). It has three commits: `18b708d` (the design), `3812b07` (`BASE` from the remote-tracking base) and `b414fe1` (the approval). Read it in full before Task 1. Where this plan is silent, its Design, Baseline probe, Testing and Constraints sections are authoritative.

## Owner review (answer at plan review)

F1 and F2 are defaults from the handoff brief. C2 and C3 (under Calls) depart from the spec's text, so each needed the owner's approval and a spec amendment (Task 1 Step 1). The owner answered all four at plan review: D1 to D4 under Decisions.

- **F1. Wait for plan 94: default yes.** The spec requires the two plans to run one at a time but fixes no order (`specs/branch-explainer.md:303-305`). Plan 94 (`specs/plans/94-copilot-pr-review-loop.md` on `refs/heads/claude/kind-kapitsa-bfb904`, approved) waits for plan 93 itself. Its body counts and its diff-stat check (its lines 19 and 40) assume a base at `af378ac`. Yes adds Base and order below, the refused-removal move (Task 4), and the body counts that start at 19,555. If "yes" is wrong, this plan waits behind plans 93 and 94 for nothing. If the answer is no, drop the wait and Task 4. The body then starts at 19,009, and plan 94's executor must stop and ledger at its own base.
- **F2. Live run after retirement: default yes.** Task 7 runs the new Step 3b on this plan's own branch, in the shape of plan 94's Task 8. It has no checkboxes and runs after the Plan Completion Protocol's retire commit. Only then does `BASE..HEAD` add or rename a plan into `specs/plans/completed/`, so only then does the plan-branch rule fire (`specs/branch-explainer.md:138-141`). It is a check beside the probe, not a pass bar. If "yes" is wrong, it costs one extra Opus subagent run. If "no" is wrong, no real branch checks the step.

## Global Constraints

### Base and order

- **Wait for plan 94 (F1).** Executions run one at a time. Start only when `git fetch origin` succeeds and `git cat-file -e origin/main:specs/plans/completed/94-copilot-pr-review-loop.md` exits 0. Plan 94 itself waits for plan 93, so both are on `origin/main` by then.
- **Base branch.** The spec and this plan reach `main` through their own PR before execution, as plan 92's did (#181). So start only when `git cat-file -e origin/main:specs/plans/95-branch-explainer.md` also exits 0, and cut the execution worktree from `origin/main` (EnterWorktree does this). If that check fails, stop and ask: never execute from `claude/branch-explainer-plan-9b2653`. Do not check out `claude/branch-explainer-pre-merge-fde7f8`, which worktree `bold-boyd-0eeb36` holds.
- **Anchors.** Each edit's old text is its match key, not its line number. Line numbers in this plan are lines of the files at `af378ac`. Plan 93 moves lines in `NOTICE`. Plan 94 moves lines in `NOTICE` and in finishing's `SKILL.md`. Once the worktree exists, run `git diff --stat af378ac HEAD -- skills/finishing-a-development-branch NOTICE`. Expected: plan 94's finishing files (`SKILL.md`, `references/copilot-review-loop.md`, `references/common-mistakes.md`, `scripts/`) and `NOTICE`, which plans 93 and 94 and PR #195 changed. For any other path, re-read each cited line before a task quotes it, and ledger a `Ruling:` for task text that no longer fits. If an old text in a step no longer matches exactly once, stop and ledger it.
- **EXEC_BASE.** Before Task 1 changes anything, `git rev-parse HEAD` is EXEC_BASE. Task 1 writes it in the record. The micro-test's control arm reads finishing's text at EXEC_BASE.
- **Self-modifying plan.** This plan edits finishing-a-development-branch. `~/.claude/skills/` serves the main checkout's copy, which has no Step 3b until this branch merges. Execute in the worktree. **The execution session never runs finishing-a-development-branch.** After the Plan Completion Protocol it ends with Task 7's handoff, and a fresh session runs the live run.

### Scope fence

- Unchanged: the Step 4 menu, its wording and its "Don't add explanation" line, the aged-tail gate (Step 1b), Step 4b, Options 1 to 4, the Copilot loop, the reviewers, `specs/history.md`'s format and the Plan Completion Protocol (spec, Non-goals).
- `install.py` and `build/test_runtime_support.py` do not change. Step 3b and the two new references name no other skill by path, `references/` path or section, and no Claude-only tool. The dependency-drift test proves it.
- Leave alone: plan 94's branches `claude/kind-kapitsa-bfb904` (worktree `peaceful-davinci-0a1696`) and `claude/copilot-pr-review-merge-e5714d` (worktree `loving-swanson-38fcea`); plan 93's branches `claude/cool-brahmagupta-88fa30` (worktree `deferred-probe-remaps-224445`), `claude/laughing-wright-00eeb6` (worktree `heuristic-stonebraker-8f62cb`), `claude/test-writer-subagent-sdd-666d94` and `claude/backlog-base-revert-mutant` (worktree `clever-cerf-bc46d2`); and `refs/heads/claude/branch-explainer-pre-merge-fde7f8` with worktree `bold-boyd-0eeb36`. The owner decides their cleanup.
- **The held-out fixture stays unread.** Until Task 6, nobody who writes or tunes the brief opens plan 84's plan, spec or history entry, or the range `650e13c..4cae5b2`. Task 1 builds that fixture only by its shas.

### Text, size and gates

- **finishing's body** (frontmatter excluded) must fit the `compaction-window` check: 19,700 characters. Measure after each `SKILL.md` edit with `uv run --with pyyaml python -c "import sys; sys.path.insert(0, 'build'); import check_conformance as c; b, _ = c.skill_body(open('skills/finishing-a-development-branch/SKILL.md').read()); print('body chars', len(b))"`.
  - Plan 94 projects 19,555 at EXEC_BASE. This plan's planning dry run applied plan 94's Task 1 and Task 5 edits to the `af378ac` file and measured 19,220 and then 19,555. Then it applied this plan's exact text: Task 4 gives −560 and Task 5 gives +383, so −177 in all, ending at 19,378.
  - If EXEC_BASE measures other than 19,555, ledger the difference, and check every later count as a delta from EXEC_BASE.
  - A wording round in Task 5 may change Step 3b's text. The Step 3b block stays at 400 characters or fewer, and the body stays at 19,600 or fewer, which leaves 100 characters of room.
- A description stays at 1,024 characters or fewer and holds no `<` or `>`. This plan does not change finishing's description.
- A new Markdown link points only to a file that exists in the same commit (`check_links.py`).
- **Orphan lint.** Every file in the skill directory is named by another non-test file of the skill in the same commit. So `SKILL.md` names `refused-removal.md` in Task 4's commit. `branch-explainer.md` and `branch-explainer-prompt.md` come in Task 5's commit with the `SKILL.md` line and the procedure text that name them.
- **Gates.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English, and end with the executing session's trailer, written below as `<the session's trailer>`.
- **Shell.** The Bash tool runs zsh. Use `/usr/bin/grep` for sweeps, absolute paths, and `"${REF}:path"` forms. Planning scratch and full writer streams go under `~/.cache/agent-skills/scratch/plan95/`. Rep folders go under `/tmp/plan95-*` from `mktemp -d`, never bare `/tmp`, and never under `~/.cache/agent-skills/`. An isolated worktree session refuses `$(…)`, `git -C` and `cd … &&` forms. So run `mktemp -d …` as its own call and write the folder it prints into the next command, and put a sequence of git commands in another repository into a script under the scratch folder, run with `bash`.

### The probe

- **Fixtures** (spec, Baseline probe). Each is an isolated repository, never a worktree (C2):

  | Name | Plan | Head | `BASE` | Branch | Commits | Role |
  |---|---|---|---|---|---|---|
  | `p80` | `80-development-history-record` | `325330a57ddff8196b40c253e016c05ebe0cd151` | `4d69454f51a548e242e5e830275303e0c7c09b74` | `claude/plan-80-execution-636c1e` | 21 | tuning |
  | `p90` | `90-readonly-guard-command-starts` | `d51bf645509b6a96db2673b9b423696363fce70c` | `84efc992b77a84d113bb15294b236e22c5349346` | `claude/quirky-golick-44b138` | 24 | tuning |
  | `p92` | `92-writing-skills-guide-rewrite` | `0b6d34f43d11adb5bce772e19073fd07241fa978` | `e382493700ea5bc7b44aa5048886a85a157f8dfd` | `claude/compassionate-jennings-98ff45` | 15 | tuning |
  | `p84` | `84-spec-derived-acceptance-tests` | `4cae5b24491392c64854ce7d31eaa2318befaa26` | `650e13c4722a83684a33b219a26f74cb1ffe0fdc` | `claude/musing-dhawan-59a2d0` | 16 | held out |

  The planning session checked each row: the head is the merge's second parent (merges `ca3404f`, `d686779`, `d58980b`, `58337f5`). `BASE` is the merge base. The range adds the plan under `specs/plans/completed/` and adds a history entry. The spec named in that entry exists at the head.
- **Writer command.** `run_writer.sh` runs each writer rep in `<rep>/repo` with exactly these flags. `<rep>` is a new `mktemp -d /tmp/plan95-rep-XXXXXX` folder. Treatment reps add `--add-dir <rep>/brief`. The write check (Task 2) drops `--add-dir <rep>/out`:

  ```bash
  env -i <HOME USER LOGNAME PATH SHELL TMPDIR LANG, each only when set> \
    CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
    "$CLAUDE_BIN" -p --model claude-opus-5-5 --tools "Bash,Read,Write,Grep,Glob" \
    --permission-mode acceptEdits --allowedTools Bash --permission-prompts none \
    --add-dir "<rep>/out" --strict-mcp-config --setting-sources "" --disable-slash-commands \
    --no-session-persistence --output-format stream-json --verbose --max-budget-usd "<cap>"
  ```

- **Reader, adjudicator and micro-test command.** `run_plain.sh` is plan 91's `specs/baseline/red-baseline-causal-design-heldout/kit/run_reps.sh`, copied. It is tool-less (`--tools "" --strict-mcp-config --setting-sources ""`, `env -i`, run from an empty `/tmp` folder outside every repository). It adds `--disable-slash-commands` and the temp prefix `/tmp/plan95-plain-`.
- **VOID.** A writer rep is VOID when its `audit.json` lists a void reason (C7), or when a file `rep<N>.VOID` holds the executor's reason. The executor reads every audit path hit by hand, as plan 73's F1 did. A rep that read or ran anything outside `<rep>`, apart from system tools, gets a `.VOID` file. VOID reps are rerun under the next free rep number. A fixture's scored reps are its first 3 reps that are not VOID. Two budget-stop VOIDs on one fixture: stop and ask the owner before you raise the cap.
- **Pass rules** (spec, exact). A bar holds on a fixture when it holds in at least 2 of 3 scored reps. **RED:** the control fails at least one bar on at least one fixture. **Shrink:** the control holds every bar on every fixture. **Treatment passes:** every bar holds on `p80`, `p90` and `p92`, and then on `p84`.
- **Wording rounds** (spec, owner-approved gate). At most two follow a failed treatment run. Before a round runs, the record states its estimated cost, from the measured mean costs. A treatment that fails after round 2 stops the work, and the results go to the owner. `p84` runs once, after the last round. If it fails, the work stops and the results go to the owner. No round tunes against it.
- **Public repository.** Commit explainers of this repository's public branches only. Full writer streams stay in `~/.cache/agent-skills/scratch/plan95/streams/`, and each rep's `result.json` records the stream's sha256 (C8). Before each commit of rep outputs, run `/usr/bin/grep -r -n -E '[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[a-z]{2,}|sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{12,}|xox[abp]-' <dir>`. Expected: no line, or only lines that the record explains, such as the public `noreply@anthropic.com` trailer.

### Cost (spec, owner-approved gate)

The basis: plan 73's tool-using Opus sessions cost $0.35 to $1.96 (`specs/baseline/red-baseline-reviewer-planning-contract/f1/runs/`). An adjudicator prompt is 200 to 260 KB, about 50,000 to 65,000 tokens. The table counts every adjudicator as uncached. The pilot measures an uncached one, and each round's estimate uses the measured mean costs, with no assumed cache discount.

| Item | Runs | Each (estimate) | Total |
|---|---|---|---|
| Pilots: isolation probe, write check, cost pilot (writer, reader, adjudicator) | 5 | — | about $4 |
| Control arm: writer, reader, adjudicator | 9 each | $1.50, $0.05, $0.40 | about $18 |
| Treatment round 0 | 9 each | $1.75, $0.05, $0.40 | about $20 |
| Each wording round | 9 each | the same | about $20 |
| Held-out (`p84`) | 3 each | the same | about $7 |
| Micro-test (Sonnet, decision-only) | about 60 | $0.08 | about $5 |
| VOID reruns | — | — | about $5 |

Expected: about **$59** with no wording round, and about **$99** with both. **Stops:** ask the owner when pilots and control together pass **$35**, or when spend plus the next step's estimate would pass **$120** for the plan. **The owner confirms the spend before the first `claude -p` call** (Task 2 Step 1). The cost pilot then replaces the estimate.

### Mutant step and who runs what

- Plan 93's mutant step is installed by then. No task here has a focused pytest command. Task 1's kit has a `selftest` subcommand, as plan 73's `score_f1.py` does, and no pytest suite. So no task is a mutant task. Where `task-done` asks, pass `--no-mutants 'probe kit with a selftest, no pytest suite'` (Task 1), `--no-mutants 'Markdown and probe records only'` (Tasks 4 and 5) or `--no-mutants 'controller task, no code change'` (Tasks 2, 3 and 6).
- Under subagent-driven-development, Tasks 1 and 4 may go to implementers. Tasks 2, 3, 5 and 6 are **controller** tasks: they spend on live runs, read every rep and stop for the owner. Task 7 runs in a **fresh session** after the plan retires.
- Under subagent-driven-development an implementer cannot ask the owner. "Stop and ask" then means: report BLOCKED with the quoted results.

### Calls made in this plan (for review)

The spec leaves these to the builder (Left to the builder) or does not settle them. The owner may overturn any of them at plan review.

- **C1. Held-out fixture: plan 84.** It must have a spec, a plan and a history entry, and be of a kind other than the three tuning fixtures: a script plus skill text (80), hook code plus tests (90), mostly skill text (92). Plans 82, 86, 87, 88, 89 and 91 have `Spec: none`. Plans 81 and 83 are probe-only branches whose diffs are 297,000 and 2,230,000 inserted lines of probe records. Plan 85 changes only derive-roadmap's skill text, which is fixture 92's kind. Plan 84 alone changes one contract across surfaces: an agent definition (`agents/task-reviewer.md`), its generated Codex and Gemini adapters, SDD prompt templates and references, and a new bash helper with tests.
- **C2. Isolated fixture repositories, not worktrees (a spec departure, approved as D3 and amended in Task 1 Step 1).** The spec says "a detached worktree". A worktree shares every ref of this repository, so `git branch -a` or `git log --all` from a rep would show this plan's branches (isolation Channel 1). The kit runs `git init`, fetches only the head's full sha, sets `main` to `BASE`, detaches `HEAD` at the head and deletes `.git/FETCH_HEAD`, which names this repository's path. A planning test of this recipe on `p92` found only `refs/heads/main`, 15 commits in `main..HEAD`, and no commit subject that holds "explainer".
- **C3. Two references, not one (a spec departure, approved as D4 and amended in Task 1 Step 1).** `references/branch-explainer-prompt.md` holds only the writer brief, and the subagent reads only that file. `references/branch-explainer.md` holds Step 3b's procedure for the finishing session. The spec says the procedure lives in the prompt file (Constraints, Compaction window). The split keeps finishing-session text out of the writer's context. The probe's treatment arm then reads exactly the bytes that ship.
- **C4. The treatment dispatch is by path.** The real dispatch tells the subagent to read the brief at its absolute path. The probe copies the round's brief to `<rep>/brief/branch-explainer-prompt.md` and sends the same dispatch text (`DISPATCH`, Task 1). No path into this repository reaches a rep.
- **C5. The adjudicator is tool-less, with its inputs inline**, as the spec lists them: spec, plan, history entry, diff, explainer and synopsis. Its diff leaves out `specs/baseline/**`, `specs/red-baseline-*/**`, and the plan and spec files (given apart), at both their `specs/` and `completed/` paths. The full `git diff --stat=200` lists every file. Without these cuts, `p92`'s diff alone is 953 KB.
- **C6. Models.** The reader and the adjudicator run on `claude-opus-5-5`, like the writer. The micro-test runs on `claude-sonnet-5-5`, the house micro-test model and the usual model of the execution sessions that run finishing.
- **C7. Word, synopsis and void rules.** A word is a whitespace-separated token with at least one letter or digit, code blocks included. The treatment's synopsis is the `## Synopsis` section. A control's synopsis is the first section whose heading reads "Synopsis", "Summary" or "TL;DR". A control with no such section is judged on the 2,000-word limit only: this tilts B5 toward the control, the safe direction. A treatment explainer with no `## Synopsis` fails B5. The audit's automatic void reasons: a result that is not `success`, a tool outside the writer's list, a model other than `claude-opus-5-5`, or no explainer file.
- **C8. Full writer streams stay outside the repository.** They hold every file the writer read, at 1 to 3 MB each. Each rep commits its explainer, `result.json` (the init record's tools, model and version, plus cost, turns, subtype, `permission_denials` and the stream's sha256) and `audit.json`.
- **C9. The write question** (Left to the builder). The subagent writes the explainer file. Task 2's write check runs the writer flags without `--add-dir` and records whether a write outside the working directory is refused under `-p`. Task 7's live run records what happens in the owner's own session. If a write is refused, the procedure reports it in one line and goes on to the menu.
- **C10. Output path.** `<repo>` is the last path component of MAIN_ROOT, so a worktree folder name never appears. The slug is the branch name with each character outside `A-Za-z0-9._-` replaced by `-`. On a detached HEAD the slug is `detached-<first 7 characters of HEAD>`. Example: `~/.cache/branch-explainers/agent-skills/2026-11-20-claude-branch-explainer-plan-9b2653.md`.
- **C11. The no-plan offer waits.** On a branch with no plan, Step 3b asks one line and waits for the answer, then shows the menu. It never puts the offer and the menu in one message.
- **C12. Core principle and Red Flags mention Step 3b. Quick Reference does not:** its rows are per option, and Step 3b runs before any option.
- **C13. The move** (F1 yes). Step 6's refused-removal detail moves to `references/refused-removal.md`. The stop and the ban on `--force` and unlock stay in the body and in Red Flags. It is a failure path, and the body's Common Mistakes pointer already sends failure detail to references. Plan 60's micro-test scenarios S5 and S6 re-run on the moved text.
- **C14. Micro-test design.** Plan 60's decision-only template (`~/.cache/agent-skills/scratch/plan60-micro/build.py`). M1 to M5 get `references/branch-explainer.md` as a file already read, to test the procedure's content. M6, S5 and S6 get the body only, to test that an agent opens the reference from its pointer. A Read of a reference is an allowed step, graded by what follows it. M1, M2, S5 and S6 run both arms. M3 to M6 run the treatment only. Each treatment scenario needs at least 4 of 5 PASS.
- **C15. Briefs per round** live in the kit as `brief-r<k>.md`. The shipped brief is byte-identical to the last round's. Wording rounds change only the brief, never `DISPATCH`, the fixtures or the scoring.
- **C16. The live run is report-only** (F2). After it, any commit to `main` falls outside this plan.

## Review Focus

1. **A local base branch behind `origin`.** `BASE` must come from `git merge-base origin/<base> HEAD` after a fetch, or the explainer covers other PRs' plans (spec §1). Micro-test M1's local `main` is 6 commits behind `origin/main`, and its row (a) requires `origin/main` (Task 5).
2. **A plan retired by a rename.** When the plan was on the base branch before execution, `BASE..HEAD` shows a rename into `specs/plans/completed/`, not an add. Fixture `p92` is such a branch (#181 merged plan 92 first, and its retire shows as `R094` without a pathspec), and so is this plan's own branch, since its PR merges before execution. The rule must still fire: `test the rule on a rename` (Task 5 Step 3) runs the procedure's exact command on a scratch repository with a rename, and with `diff.renames` off.
3. **The subagent cannot write its file.** The owner's session may refuse a write under `~/.cache`. The step must say so in one line and still show the menu unchanged, with no retry and no explainer text in the conversation: micro-test M3 (Task 5).
4. **A detached HEAD.** It has no branch name, so the slug rule must still give a path. The three-option menu follows: micro-test M4 (Task 5).
5. **The owner says to skip it.** "Finish the branch, skip the explainer" must run no fetch, give no dispatch and no offer, and leave the menu unchanged: micro-test M5 (Task 5).

## Decisions

- **D1** (owner, plan review, 2026-11-13): F1, "Yes, wait". Execution starts only once `origin/main` holds plan 94's retired plan, then merges `origin/main`, and this plan moves Step 6's refused-removal detail to make room. Applied in: Global Constraints (Base and order, Text, size and gates), Task 4.
- **D2** (owner, plan review, 2026-11-13): F2, "Yes, one live run". A fresh session runs Step 3b on this plan's own branch after retirement, report-only. Applied in: Task 7.
- **D3** (owner, plan review, 2026-11-13): C2, "Approve". The probe fixtures are isolated repositories, not worktrees, and the spec's Baseline probe sentence is amended. Applied in: Global Constraints (The probe), Task 1 (spec amendment).
- **D4** (owner, plan review, 2026-11-13): C3, "Approve". Step 3b's procedure lives in `references/branch-explainer.md`, the writer brief alone in `references/branch-explainer-prompt.md`, and the spec's Compaction window sentence is amended. Applied in: Tasks 3 and 5, Task 1 (spec amendment).

---

## File Structure

| File | Change | Task |
|---|---|---|
| `specs/baseline/red-baseline-branch-explainer/kit/kit.py` | new: fixtures, prompts, words, audit, scores, selftest | 1 |
| `specs/baseline/red-baseline-branch-explainer/kit/run_writer.sh` | new: writer reps | 1 |
| `specs/baseline/red-baseline-branch-explainer/kit/run_judges.sh` | new: reader, then adjudicator, per rep | 1 |
| `specs/baseline/red-baseline-branch-explainer/kit/run_plain.sh` | copy of plan 91's `run_reps.sh` | 1 |
| `specs/baseline/red-baseline-branch-explainer/kit/isolation_probe_tools.txt` | copy of plan 73's, one line added | 1 |
| `specs/baseline/red-baseline-branch-explainer/kit/brief-r<k>.md` | the writer brief per round | 3 |
| `specs/baseline/red-baseline-branch-explainer.md` | the record | 1 to 6 |
| `specs/baseline/red-baseline-branch-explainer/{pilot,control,treatment-r<k>,heldout}/` | rep outputs | 2, 3, 6 |
| `specs/baseline/red-baseline-branch-explainer/micro/` | micro-test kit, grading and reps | 4, 5 |
| `skills/finishing-a-development-branch/references/refused-removal.md` | new: the moved text | 4 |
| `skills/finishing-a-development-branch/SKILL.md` | the move (4); Step 3b, Core principle, Red Flags (5) | 4, 5 |
| `skills/finishing-a-development-branch/references/branch-explainer.md` | new: Step 3b's procedure | 5 |
| `skills/finishing-a-development-branch/references/branch-explainer-prompt.md` | new: the writer brief | 5 |
| `NOTICE` | one entry | 5 |

---

### Task 1: The probe kit and the record

**Files:**
- Create: `specs/baseline/red-baseline-branch-explainer/kit/kit.py`, `run_writer.sh`, `run_judges.sh`
- Create: `specs/baseline/red-baseline-branch-explainer/kit/run_plain.sh` (copy of `specs/baseline/red-baseline-causal-design-heldout/kit/run_reps.sh`, with the changes Step 7 lists)
- Create: `specs/baseline/red-baseline-branch-explainer/kit/isolation_probe_tools.txt` (copy of `specs/baseline/red-baseline-reviewer-planning-contract/f1/isolation_probe_tools.txt`, plus line 8 below)
- Create: `specs/baseline/red-baseline-branch-explainer.md`
- Modify: `specs/branch-explainer.md` (the C2 and C3 amendments, Step 1)

**Interfaces:**
- Consumes: nothing.
- Produces, in `kit.py` (uv inline header: `requires-python = '>=3.11'`, `dependencies = []`; standard library only, single quotes, named constants), run from the repo root as `uv run specs/baseline/red-baseline-branch-explainer/kit/kit.py <command>`:
  - `FIXTURES: dict[str, dict]`, keyed `p80`, `p90`, `p92` and `p84`, with the keys `plan`, `head`, `base`, `branch`, `commits` and `held_out`, from the Global Constraints table.
  - Exact-copy constants `CONTROL_REQUEST`, `DISPATCH`, `READER`, `ADJUDICATOR`, `TREATMENT_B4`, `WRITE_CHECK` (below). Also `WRITER_TOOLS = frozenset({'Bash', 'Read', 'Write', 'Grep', 'Glob'})`, `MODEL = 'claude-opus-5-5'`, `SYNOPSIS_LIMIT = 250`, `EXPLAINER_LIMIT = 2000`, `REPS = 3` and `HOLD = 2`.
  - `count_words(text: str) -> int`, `synopsis_span(text: str, arm: str) -> tuple[int, int] | None` (a half-open range of line indexes, from the heading line to the next heading of the same or a higher level), `reader_view(text: str, arm: str) -> str` and `length_bar(text: str, arm: str) -> dict` (keys `explainer`, `synopsis`, `B5`). `synopsis` counts the section's words without its heading line.
  - `history_entry(base: str, head: str, plan: str) -> str` (the section the range adds whose header starts `## <plan>`), `entry_paths(entry: str) -> tuple[str, str | None]` (the plan path, and the spec path or `None` for `Spec: none`) and `adjudicator_diff(base: str, head: str, plan: str, spec: str | None) -> tuple[str, str]` (the stat, the diff).
  - `parse_adjudication(text: str) -> dict[str, bool] | None` and `audit_hits(stream: Path, rep_dir: Path) -> dict` (keys `tools`, `models`, `subtype`, `cost`, `permission_denials`, `outside`, `void_reasons`).
  - `result_problem(path: Path) -> str | None`: `None` when the file parses as JSON, `is_error` is false, `subtype` is `success` and `result` is a string that is not empty. Otherwise a short reason: `no file`, `not JSON`, `is_error`, `subtype <value>` (a budget stop included) or `empty result`.
  - `arm_of(arm_dir: Path) -> str`: from the folder's last component, `control` gives `control`, and `heldout` or `treatment-r<k>` (`k` one or more digits) gives `treatment`. Any other name raises `ValueError`.
  - Commands: `selftest`; `fixture <name> <dest>` (builds `<dest>/repo` and prints its path); `writer-prompt <arm> <name> <rep-dir>` (arm `control`, `treatment`, `probe` or `permcheck`); `audit <stream> <rep-dir> <out-prefix>` (writes `<out-prefix>.audit.json` and `<out-prefix>.result.json` and prints the void reasons); `reader-prompt <arm> <explainer>`; `adjudicator-prompt <arm> <name> <explainer> <reader-json>`; `result-ok <json>` (exits 0 when `result_problem` gives `None`, else prints the reason and exits 1); `score <arm-dir>` (takes the arm from `arm_of`, and exits 2 before it scores anything when `arm_of` raises; writes `rep<N>.score.json` for each scored rep and prints, for each fixture and bar, the PASS count and `holds` or `fails`).
  - `bash kit/run_writer.sh <arm> <fixture> <out-dir> <first> <last> <cap> [<brief>]`: one writer rep per number. The first rep runs alone and the rest in parallel. Each rep writes `rep<N>.md`, `rep<N>.audit.json` and `rep<N>.result.json` in `<out-dir>`, and its stream to `~/.cache/agent-skills/scratch/plan95/streams/<out-dir's last two components>/rep<N>.jsonl`. It refuses when any `<out-dir>/rep<N>.*` exists. It removes `<rep>/repo` after the run, only when the path starts with `/tmp/plan95-rep-`.
  - `bash kit/run_judges.sh <arm> <fixture> <out-dir> <rep> [<rep> ...]`: for each rep, it builds the reader prompt and runs `run_plain.sh` into `<out-dir>/reader/rep<N>.json` (cap $0.50). Then it builds the adjudicator prompt and runs it into `<out-dir>/adj/rep<N>.json` (cap `ADJ_CAP`, from the environment, default `2.00`). It skips the reader when `kit.py result-ok reader/rep<N>.json` exits 0, so a retry reruns only the adjudicator and the synopsis under score stays the same. When that file exists but fails `result-ok`, the shell redirect made it before a run that failed: move it, and `reader/rep<N>.err` if present, to `reader/rep<N>.bad<k>.json` and `.bad<k>.err` (`k` the next free number), then rerun the reader. When a fresh reader fails `result-ok`, print the reason and run no adjudicator for that rep. After two bad readers on one rep, stop and ask. Prompts go to `~/.cache/agent-skills/scratch/plan95/prompts/`.

The exact-copy constants (Python strings; `{…}` fields are `str.format` fields):

`CONTROL_REQUEST`, the spec's control request:

```text
Explain the change in `{base}..HEAD` of this repository to me, its owner, before I merge it. Write it to `{path}`.
```

`DISPATCH`. Task 5 copies the same text into `references/branch-explainer.md`:

```text
Read {brief} and follow it to write a branch explainer.
BASE: {base}
HEAD: {head}
Branch: {branch}
Repository: {repo}
Plan branch: {plan_branch}
Output: {output}
```

In the probe: `{brief}` is `<rep>/brief/branch-explainer-prompt.md`, `{repo}` is `<rep>/repo`, `{output}` (and the control's `{path}`) is `<rep>/out/explainer.md`, and `{plan_branch}` is `yes`. `{base}` and `{head}` are full shas.

`READER`:

```text
Below is a document that explains one branch of a code repository to the repository's owner. Read it. Then, from what the document says, write a synopsis of the branch in your own words: three labeled parts, at most 250 words in all.

The plan: what the work set out to do, and why.
The build: how it was built: the main parts, in the order they depend on each other.
The project: what the branch adds to the project as a whole.

Reply with the three parts only.

<document>
{explainer}
</document>
```

`ADJUDICATOR`. The per-fixture materials come first, so reps 2 and 3 of a fixture reuse the cached prefix:

```text
You score one explainer of a code branch, and a synopsis that a reader wrote after reading only that explainer. You have no tools. Everything you need is below.

<spec>
{spec}
</spec>
<plan>
{plan}
</plan>
<history_entry>
{entry}
</history_entry>
<diff_stat>
{stat}
</diff_stat>
<diff note="Probe records under specs/baseline/ and specs/red-baseline-*/, and the plan and spec files, are left out of this diff. diff_stat lists every changed file.">
{diff}
</diff>
<explainer>
{explainer}
</explainer>
<synopsis>
{synopsis}
</synopsis>

Score four bars. A bar passes only when every part of it holds.

B1 Plan. The synopsis's first part states the plan's goal and the reason for it, and both agree with the spec.
B2 Build. The synopsis's second part names the main parts of the build in an order that fits their dependencies: no part comes before a part it needs. It also states at least two facts that come from the diff and that the spec does not state, such as a file, a function, a command, a check, a count or a behavior.
B3 Project. The synopsis's third part names at least one way the branch changes the project beyond the files it touches: a part of the project that now depends on the branch, or a step of a workflow that now runs differently. A list of changed files does not count.
B4 Accuracy. The explainer, every section of it, makes no claim about what the branch's code or text does that the diff contradicts. A claim that the diff does not cover is not a contradiction.{b4_extra}

Reply in exactly this form, and nothing else:
B1: PASS or FAIL
Why: <one or two sentences that quote the synopsis>
B2: PASS or FAIL
Why: <the order you checked, and the two diff facts, each with the file it comes from>
B3: PASS or FAIL
Why: <one or two sentences that quote the synopsis>
B4: PASS or FAIL
Contradicted: none, or one line per claim: "<quoted claim>" against <file>: <what the diff shows>
```

`{b4_extra}` is empty for the control. For the treatment it is `TREATMENT_B4`:

```text
 The explainer's own Synopsis section counts too: each of its three parts must agree with the spec and the diff, and a part that does not is a claim for the list.
```

`WRITE_CHECK`, the permcheck prompt:

```text
Write the single word ok to the file {path}. Then reply DONE, or reply REFUSED with the reason if the write was refused.
```

- [ ] **Step 1: Apply the spec amendments approved at plan review (D3, D4)**

Each old text must match exactly once in `specs/branch-explainer.md`. Leave its Status line as it is. In the Baseline probe section, replace:

```markdown
Each fixture is a detached worktree at the branch head before the merge, with `BASE` at its merge base.
```

with:

```markdown
Each fixture is an isolated repository that holds only the history of the branch head before the merge, with
a detached HEAD there and `BASE` at its merge base. A worktree would share every ref of this repository with
the reps (owner, plan 95, 2026-11-13).
```

In Constraints, Compaction window, replace:

```markdown
  some of them. Step 3b in `SKILL.md` is a short pointer, at most about 400 characters, and the procedure
  lives in the prompt file. If the two plans together pass the window, the plan that runs second moves
```

with:

```markdown
  some of them. Step 3b in `SKILL.md` is a short pointer, at most about 400 characters, and the procedure
  lives in `references/branch-explainer.md`, beside the prompt file, so the subagent reads only the prompt
  file (owner, plan 95, 2026-11-13). If the two plans together pass the window, the plan that runs second moves
```

Run `bash build/run_commit_lints.sh`. Expected: `commit lints passed`. Then `git add specs/branch-explainer.md` and `git commit -m "docs(specs): amend the branch explainer spec for plan 95" -m "<the session's trailer>"`.

- [ ] **Step 2: Record EXEC_BASE and the fixtures' state**

Create the record with a title, a Status line reading `in progress`, and EXEC_BASE from Global Constraints as one line, `EXEC_BASE: <the 40-character sha>` (Task 4's `build_micro.py` reads it). Run `git cat-file -e HEAD:specs/plans/95-branch-explainer.md`, then `claude --version`. Expected: exit 0, then `2.1.323 (Claude Code)` or later. Write both in the record.

- [ ] **Step 3: Write the selftest**

`kit.py selftest` asserts each case below, prints `selftest passed`, and exits 1 on the first failure:

```python
assert count_words('Hello, world! -- `x.py:12` | ## |') == 3
t = '# T\n\n## Synopsis\n\n**The plan:** a\n\n### Sub\nb\n\n## Background\nc\n'
assert reader_view(t, 'treatment') == '# T\n\n## Background\nc\n'
assert reader_view(t, 'control') == t
c = '# T\n## Summary:\nx y\n## Body\nz\n'
assert length_bar(c, 'control') == {'explainer': 6, 'synopsis': 2, 'B5': True}
assert reader_view(c, 'control') == c
assert synopsis_span(c, 'treatment') is None
assert length_bar(c, 'treatment')['B5'] is False
assert length_bar('# T\n' + 'w ' * 10, 'control') == {'explainer': 11, 'synopsis': None, 'B5': True}
assert length_bar('## Synopsis\n' + 'w ' * 251 + '\n## B\n', 'treatment')['B5'] is False
assert length_bar('w ' * 2001, 'control')['B5'] is False
good = 'B1: PASS\nWhy: x\nB2: FAIL\nWhy: y\nB3: PASS\nWhy: z\nB4: PASS\nContradicted: none\n'
assert parse_adjudication(good) == {'B1': True, 'B2': False, 'B3': True, 'B4': True}
assert parse_adjudication(good.replace('B3: PASS', 'B3: PASS or FAIL')) is None
assert parse_adjudication(good.replace('B3: PASS\n', '')) is None
assert arm_of(Path('x/control')) == 'control'
assert arm_of(Path('x/treatment-r12')) == 'treatment' and arm_of(Path('x/heldout')) == 'treatment'
for bad in ('pilot', 'treatment', 'treatment-r', 'heldout2'):
    try:
        arm_of(Path('x') / bad)
    except ValueError:
        pass
    else:
        raise AssertionError(bad)
f = FIXTURES['p90']
entry = history_entry(f['base'], f['head'], f['plan'])
assert entry.startswith('## 90-readonly-guard-command-starts')
plan, spec = entry_paths(entry)
assert plan == 'specs/plans/completed/90-readonly-guard-command-starts.md'
assert spec == 'specs/completed/readonly-guard-command-starts.md'
stat, diff = adjudicator_diff(f['base'], f['head'], plan, spec)
assert 'specs/plans/completed/90-readonly-guard-command-starts.md' in stat
assert '+++ b/specs/plans/completed/90-' not in diff and '+++ b/hooks/' in diff
f = FIXTURES['p80']
assert history_entry(f['base'], f['head'], f['plan']).startswith('## 80-development-history-record')
```

Add a `result_problem` case. In a temp folder, write `ok.json` as `{"is_error": false, "subtype": "success", "result": "x"}`, an empty `empty.json`, and `budget.json` as `{"is_error": true, "subtype": "error_max_budget_usd", "result": ""}`. Assert that `ok.json` gives `None`, `empty.json` gives `not JSON`, `budget.json` gives a reason that is not `None`, and a path that does not exist gives `no file`.

Add an `audit_hits` case. Write a three-line stream-json file to a temp folder: an init record with `tools: ['Bash', 'Read']`, then one assistant record with three `tool_use` parts, then a `result` record with `subtype: 'success'`. The three parts are `Read` of `/tmp/plan95-rep-abc/repo/README.md`, `Read` of `/Users/x/Projects/agent-skills/specs/branch-explainer.md`, and `Bash` with `cat ~/notes.md`. With `rep_dir=Path('/tmp/plan95-rep-abc')`, assert that `outside` holds the second and third inputs and not the first, and that `void_reasons` holds `no explainer file`. Add four more `tool_use` parts and assert their places. A `Read` of `os.path.realpath(rep_dir) + '/repo/x.md'` is not in `outside`: build that path in the test, never write `/private/tmp` into it, since only macOS maps `/tmp` there. A `Bash` with `cat ../../notes.md` is in `outside`. A `Bash` with `git diff --stat main..HEAD` and a `Bash` with `git log --oneline 4be1c9a..HEAD` are not: a revision range is no path component. Add a second assistant record with a `WebFetch` `tool_use`, and assert that `void_reasons` names `WebFetch`.

- [ ] **Step 4: Run the selftest to verify it fails**

Run: `uv run specs/baseline/red-baseline-branch-explainer/kit/kit.py selftest`
Expected: a non-zero exit with a `NameError` or an `AssertionError`.

- [ ] **Step 5: Implement `kit.py`**

- `fixture`: `git init -q -b main <dest>/repo`, then `git -C <dest>/repo fetch -q --no-tags <repo root> <head>`, where `<repo root>` is `git rev-parse --show-toplevel` of the working directory (short shas fail), `update-ref refs/heads/main <base>`, `checkout -q --detach <head>`, and delete `.git/FETCH_HEAD`. It checks `git rev-list --count main..HEAD` against `commits`, and that `git for-each-ref` prints only `refs/heads/main`. It exits 2 when either check fails.
- `writer-prompt`: control gives `CONTROL_REQUEST`, and treatment gives `DISPATCH`. Probe gives the file `isolation_probe_tools.txt`, and permcheck gives `WRITE_CHECK` with `{path}` set to `<rep>/out/check.txt`.
- `synopsis_span`: the heading match drops leading `#`s, the spaces and a trailing colon, and then compares lowercase text. The span runs from the heading line to the line before the next heading of the same or a higher level.
- `history_entry`: the lines that `git diff -U0 <base>..<head> -- specs/history.md` adds, from the added line that starts `## <plan>` up to the next added `## ` line. Each fixture range adds exactly one section (checked in planning). The second line reads `Plan: <path> · Spec: <path> (<state>)` or `Spec: none`.
- `adjudicator_diff`: the stat is `git diff --stat=200 <base>..<head>`. The diff uses the pathspecs `':/'`, `':(exclude,glob)specs/baseline/**'`, `':(exclude,glob)specs/red-baseline-*/**'`, and `':(exclude)'` for the plan and the spec at their `specs/` and `completed/` paths.
- `audit_hits`: copy `FORBIDDEN_RE` and `CD_HOME_RE` from `score_f1.py` and widen them. `outside` lists each `tool_use` input that names an absolute path under neither `rep_dir` nor `os.path.realpath(rep_dir)` (on macOS `/tmp` is `/private/tmp`, and Claude Code reports the real path), apart from `/dev/null` and the system folders `/usr/`, `/bin/`, `/opt/`, `/Library/` and `/System/`. It also lists an input that names a `~`, `$HOME` or `${HOME}` path, or that holds a `..` path component, such as `cd ../..` or `cat ../../x`. A `..` is a path component when the start of the input, whitespace, `/`, `=` or a quote comes before it, and `/`, whitespace, a quote or the end comes after it. So the `..` of a revision range such as `main..HEAD` or `4be1c9a..HEAD` is not one. `void_reasons` follows C7.
- `score`: a rep's bars are B1 to B4 from `adj/rep<N>.json`'s `.result`, read by `parse_adjudication`, and B5 from `length_bar`. A rep whose `adj/rep<N>.json` fails `result_problem`, or whose adjudication does not parse, exits 2 and names the rep. Move that file to `adj/rep<N>.bad<k>.json`, run `run_judges.sh` for the rep again, and after two bad parses stop and ask. For each fixture, `score` also prints how many scored reps passed all five bars at once. That count is reported in the record and is no bar: the spec's pass rule stays per bar.

- [ ] **Step 6: Run the selftest to verify it passes**

Run: `uv run specs/baseline/red-baseline-branch-explainer/kit/kit.py selftest`
Expected: `selftest passed`.

- [ ] **Step 7: Write the scripts and the probe file**

- `run_plain.sh`: copy plan 91's `run_reps.sh`. Change only the temp prefix to `/tmp/plan95-plain-`, the comments to name plan 95, and add `--disable-slash-commands`.
- `run_writer.sh` and `run_judges.sh`: as Interfaces says, with the writer command from Global Constraints. `run_writer.sh` drops `--add-dir "<rep>/out"` for `permcheck` and adds `--add-dir "<rep>/brief"` for `treatment`.
- `isolation_probe_tools.txt`: copy plan 73's file, change `Answer the seven numbered lines` to `Answer the eight numbered lines`, and add this line:

```text
8. Run `git for-each-ref --format='%(refname)'` with your Bash tool and quote its whole output.
```

- [ ] **Step 8: Build each fixture once and check the prompts for leaks**

For each of `p80`, `p90`, `p92` and `p84`, run `mktemp -d /tmp/plan95-fix-XXXXXX`, then `uv run specs/baseline/red-baseline-branch-explainer/kit/kit.py fixture <name> <the folder it printed>`. Expected: four repository paths and no exit 2. Leave the folders: they are a check only. Then write both writer prompts for `p80` with the rep folder `/tmp/plan95-rep-LEAK`:

```bash
mkdir -p ~/.cache/agent-skills/scratch/plan95/leak
uv run specs/baseline/red-baseline-branch-explainer/kit/kit.py writer-prompt control p80 /tmp/plan95-rep-LEAK > ~/.cache/agent-skills/scratch/plan95/leak/control.txt
uv run specs/baseline/red-baseline-branch-explainer/kit/kit.py writer-prompt treatment p80 /tmp/plan95-rep-LEAK > ~/.cache/agent-skills/scratch/plan95/leak/treatment.txt
/usr/bin/grep -n -i -E 'synopsis|background|dependency|question|250|2,000|2000|agent-skills|plan 95' ~/.cache/agent-skills/scratch/plan95/leak/control.txt ~/.cache/agent-skills/scratch/plan95/leak/treatment.txt
```

Expected: the grep prints no line. Neither prompt tells the writer the layout or the limits, and neither names this repository's path.

- [ ] **Step 9: Write the record skeleton**

The record holds EXEC_BASE, the Claude Code version and the fixture table, with C1's argument for `p84`. It holds the kit's files, with what each copied file changed from its source. It holds every exact-copy constant, the pass rules, the VOID rule, both run commands and the cost table with its stops. It holds the known limits: one model, 3 reps per arm, a reader who is a model, not the owner, a tool-less adjudicator who sees no code outside the diff, and no `Plan branch: no` or `Spec: none` case in the probe. Empty sections follow: Pilots, Control, Treatment, Held-out, Micro-test, Spend and Verdict.

- [ ] **Step 10: Commit before any live run**

Run: `bash build/run_commit_lints.sh`. Expected: `commit lints passed`.

```bash
git add specs/baseline/red-baseline-branch-explainer specs/baseline/red-baseline-branch-explainer.md
git commit -m "test(specs): branch explainer probe kit and record" -m "<the session's trailer>"
```

---

### Task 2 (controller): Spend confirmation, pilots and the control arm

**Files:**
- Create: `specs/baseline/red-baseline-branch-explainer/pilot/`, `specs/baseline/red-baseline-branch-explainer/control/<fixture>/`
- Modify: `specs/baseline/red-baseline-branch-explainer.md`

**Interfaces:**
- Consumes: Task 1's kit.
- Produces: the writer and adjudicator caps, the control scores and the RED or Shrink verdict that Task 3 reads.

- [ ] **Step 1: The owner confirms the spend**

Ask: "Plan 95's probe is ready. The plan estimates about $59 for the live runs, or about $99 with both wording rounds. It stops to ask at $35 for pilots and control, and at $120 in all. Do you confirm the spend?" Wait. Write the answer in the record, quoted. On a no, stop.

- [ ] **Step 2: Isolation probe and write check**

Run `bash specs/baseline/red-baseline-branch-explainer/kit/run_writer.sh probe p90 specs/baseline/red-baseline-branch-explainer/pilot/probe 1 1 1.00`. Then run `run_writer.sh permcheck p90 specs/baseline/red-baseline-branch-explainer/pilot/permcheck 1 1 1.00`.
Expected for the probe: lines 2 to 6 read NO. Line 8 quotes only `refs/heads/main`. The init record's `tools` is a subset of `WRITER_TOOLS` and holds `Bash`, `Read` and `Write`. Record lines 1 and 7 as they are: they show whether the fixture's `CLAUDE.md` loads and whether a read outside the folder is refused. For the write check, record the reply, `permission_denials` and whether `<rep>/out/check.txt` exists (C9). If lines 2 to 6 do not all read NO, or line 8 shows another ref, stop and ask.

- [ ] **Step 3: Cost pilot**

Run one unscored control writer rep on `p92`, the largest fixture: `run_writer.sh control p92 specs/baseline/red-baseline-branch-explainer/pilot/writer 1 1 6.00`. Then run `ADJ_CAP=3.00 bash specs/baseline/red-baseline-branch-explainer/kit/run_judges.sh control p92 specs/baseline/red-baseline-branch-explainer/pilot/writer 1`. Record each run's `total_cost_usd`. Do not score the pilot. Set the writer cap to twice the pilot's cost, rounded up to the next $0.50, with $3.00 as the floor. Set `ADJ_CAP` by the same rule from the pilot adjudicator, with $1.00 as the floor. If the writer cap passes $8.00, or the projection from the pilot for control, round 0 and held-out passes $90, stop and ask.

- [ ] **Step 4: Run the control arm**

For each of `p80`, `p90` and `p92`: `run_writer.sh control <fx> specs/baseline/red-baseline-branch-explainer/control/<fx> 1 3 <cap>`. Read each `audit.json`'s `outside` hits by hand and write a `.VOID` file where the VOID rule says. Rerun each VOID rep under the next number until there are 3 scored reps. Then `run_judges.sh control <fx> specs/baseline/red-baseline-branch-explainer/control/<fx> <scored reps>`.
Expected: 3 scored reps per fixture, each with a reader and an adjudication, and spend below $35.

- [ ] **Step 5: Score and decide RED or Shrink**

Run `uv run specs/baseline/red-baseline-branch-explainer/kit/kit.py score specs/baseline/red-baseline-branch-explainer/control`. Read every adjudication in full against its bar text. Mark any you dispute as contested in the record, with both readings. A contested reading goes to the owner only when it would flip a bar's result on a fixture. Write the bar table, the verdict (RED, with the failed bars and fixtures, or Shrink), each VOID and the spend.

- [ ] **Step 6: Scan and commit**

Run the Public repository scan over `pilot/` and `control/`. Expected: no line, or only lines the record explains.

```bash
git add specs/baseline/red-baseline-branch-explainer specs/baseline/red-baseline-branch-explainer.md
git commit -m "test(specs): branch explainer pilots and control arm" -m "<the session's trailer>"
```

---

### Task 3 (controller): The writer brief and the treatment rounds

**Files:**
- Create: `specs/baseline/red-baseline-branch-explainer/kit/brief-r0.md` (and `brief-r1.md`, `brief-r2.md` when rounds follow)
- Create: `specs/baseline/red-baseline-branch-explainer/treatment-r<k>/<fixture>/`
- Modify: `specs/baseline/red-baseline-branch-explainer.md`

**Interfaces:**
- Consumes: Task 2's verdict and caps.
- Produces: `brief-r<last>.md`, which Task 5 copies byte for byte to `references/branch-explainer-prompt.md`.

- [ ] **Step 1: Write `brief-r0.md`**

The brief is addressed to the writer and worded freely. It names no skill, no Claude-only tool and no fixture. It holds:
- **The values** it gets: the `DISPATCH` lines, and what `Plan branch: no` changes.
- **Inputs** (spec §4). The diff `BASE..HEAD` and its commit log. Read `git diff --stat` first, and skim probe records and generated files rather than reading them whole. The history entry the range adds to `specs/history.md`, and the plan and spec its second line names. With `Spec: none`, the plan alone gives the intent. The project map: the README, `CLAUDE.md` or `AGENTS.md`, any live `specs/*-roadmap.md` and earlier history entries. The code around the change, as far as needed. With `Plan branch: no`, the diff, the commit log and the project map are the only inputs, and the plan part says what the commits show the work set out to do.
- **The diff-versus-spec rule.** Where they differ, say so and cite the history entry's ruling or deviation. The diff says what was done.
- **The layout** (spec §5), with exact headings in this order: a `# ` title line, then `## Synopsis` with three paragraphs labeled `**The plan:**`, `**The build:**` and `**The project:**`, then `## Background`, `## The change`, `## What it adds to the project` and `## Questions`. Each section's content follows spec §5. Each claim about code names the file, and the line where it helps.
- **Limits.** The Synopsis is at most 250 words, and the whole explainer at most 2,000. A word is any token with a letter or a digit, code included.
- **Style.** Markdown in plain technical English, said in the brief's own words: short sentences, one idea each, the active voice, one name for each thing, no semicolons. No tutorial for beginners, because the owner wrote the project.
- **Output.** Create the output's folder if needed, write the file, and overwrite it if it exists. Return only the path and the word count. If the write is refused, return the refusal and write nothing elsewhere.
- **On RED.** For each bar the control failed, one instruction aimed at it. The record names that instruction beside the bar. **On Shrink:** only the values, inputs, layout, limits, style and output, with no instruction aimed at a bar (spec, Baseline probe).

- [ ] **Step 2: Leak check, then commit before any treatment rep**

Run: `/usr/bin/grep -n -i -E 'history-record|readonly|writing-skills-guide|acceptance|plan 8[04]|plan 9[02]|skills/' specs/baseline/red-baseline-branch-explainer/kit/brief-r0.md`. Expected: no line. Write round 0's estimate in the record: `9 × (mean_writer + mean_reader + mean_adjudicator)`, each mean over the runs measured so far. A round is 9 writer, 9 reader and 9 adjudicator runs.

```bash
git add specs/baseline/red-baseline-branch-explainer
git commit -m "test(specs): branch explainer writer brief, round 0" -m "<the session's trailer>"
```

On **Shrink**, skip Steps 3 to 5: the shrunk brief is final, and Task 6 still runs it on `p84` (spec, Done when 3).

- [ ] **Step 3: Run the treatment arm**

For each of `p80`, `p90` and `p92`: `run_writer.sh treatment <fx> specs/baseline/red-baseline-branch-explainer/treatment-r0/<fx> 1 3 <cap> specs/baseline/red-baseline-branch-explainer/kit/brief-r0.md`, with Task 2's VOID handling. Then run `bash specs/baseline/red-baseline-branch-explainer/kit/run_judges.sh treatment <fx> specs/baseline/red-baseline-branch-explainer/treatment-r0/<fx> <scored reps>` and `uv run specs/baseline/red-baseline-branch-explainer/kit/kit.py score specs/baseline/red-baseline-branch-explainer/treatment-r0`. Read every adjudication as in Task 2 Step 5.
Expected: 3 scored reps per fixture. Every bar holds on every fixture, or the record names each bar that fails.

- [ ] **Step 4: Wording rounds, only on a failed bar**

For round `k` = 1, then 2: write the round's estimate in the record, by Step 2's formula with the means updated. If spend plus that estimate passes $120, stop and ask. Write `brief-r<k>.md`, changed only in text aimed at the bars that failed. Put the diff from the last brief in the record. Run Step 2's leak grep on it and commit it. Then run Step 3 into `treatment-r<k>/`. If every bar holds, go to Step 5. After a failed round 2, stop: the record's Verdict says so, and the results go to the owner.

- [ ] **Step 5: Scan and commit**

Run the Public repository scan over `treatment-r*/`. Write the treatment tables and the spend.

```bash
git add specs/baseline/red-baseline-branch-explainer specs/baseline/red-baseline-branch-explainer.md
git commit -m "test(specs): branch explainer treatment rounds" -m "<the session's trailer>"
```

---

### Task 4: Make room: move Step 6's refused-removal detail

**Files:**
- Create: `skills/finishing-a-development-branch/references/refused-removal.md`
- Modify: `skills/finishing-a-development-branch/SKILL.md` (Step 6, `af378ac` lines 367-372)
- Create: `specs/baseline/red-baseline-branch-explainer/micro/` (`build_micro.py`, `tools.txt`, `GRADING.md`, `fixtures/S5-locked.txt`, `fixtures/S6-untracked.txt`)
- Modify: `specs/baseline/red-baseline-branch-explainer.md`

**Interfaces:**
- Consumes: the record's `EXEC_BASE:` line (Task 1 Step 2), and `kit/run_plain.sh` and `kit.py result-ok` (Task 1). Nothing from Tasks 2 and 3.
- Produces: `uv run specs/baseline/red-baseline-branch-explainer/micro/build_micro.py <arm> <out-dir> <scenario>...`, which writes `<scenario>.txt` and `MANIFEST.txt` (sha256 of each prompt). Task 5 adds scenarios to it.

- [ ] **Step 1: Build the micro-test kit**

Copy from `~/.cache/agent-skills/scratch/plan60-micro/`: `build.py`'s `TEMPLATE` and `fixture()` unchanged, `tools.txt` with one line added for an `Agent` tool (it starts a fresh subagent, takes `subagent_type`, `model` and `prompt`, and returns the subagent's final message), and fixtures `S5-locked.txt` and `S6-untracked.txt`. If that folder is gone, stop and ask. `build_micro.py` reads the skill body at EXEC_BASE for `control` and from the working tree for `treatment`. It takes EXEC_BASE from the record's `EXEC_BASE: <sha>` line, never from the environment. It exits 2, before it writes any prompt, when that line is missing, when the value is not 40 hexadecimal characters, or when `git cat-file -e <sha>^{commit}` fails. Then it runs `git show <sha>:skills/finishing-a-development-branch/SKILL.md`, with the sha written out. For `treatment`, it inserts the scenario's reference files after the `</skill>` line, as `<file path="references/<name>">…</file>` blocks under the line `Reference files of the skill that you have read:`. A scenario lists its files in a `files:` header line, and `files: none` inserts no block. S5 and S6 use `files: none`: the moved detail is then out of view, as it is for a real agent, so the scenarios show whether the graded behavior survives the move. A supplied file would hide that. They do not require a Read, since the person sees the stop and the question, not the Read. The record notes for each rep whether it read `references/refused-removal.md`. It refuses a fixture that still holds a `{redirect}` or `{noop}` marker.

`GRADING.md` copies plan 60's S5 and S6 rows, word for word, from that folder's `PREREGISTRATION.md`, and adds this rule for every scenario: `A TOOL Read of a file under references/ is an allowed read-only step. Grade the actions after it, IF lines included. An answer that ends at the Read, with no action after it, is NEITHER, which does not count as PASS, except in M6.` The bar: treatment PASS in at least 4 of 5 reps. The control arm (EXEC_BASE, before the move) runs the same two scenarios, with no bar.

- [ ] **Step 2: Commit the kit before any rep**

Run `bash build/run_commit_lints.sh`, then `git add specs/baseline/red-baseline-branch-explainer/micro`. Then `git commit -m "test(specs): micro-test kit for finishing's Step 6 move and Step 3b" -m "<the session's trailer>"`.

- [ ] **Step 3: Move the text**

Create `references/refused-removal.md` with this title and this opening line, then a blank line, then the moved text as it stands:

```markdown
# When `git worktree remove` refuses

Step 6 sends you here after a refused removal. You have stopped, with no `--force`, no `-f -f` and no unlock.
```

The moved text is everything in Step 6 from `A lock can belong to a session that is still running` through `Delete the branch only once the worktree is gone.`, with the two bullets. In `SKILL.md`, replace that text and the blank line after it with `Then follow [references/refused-removal.md](references/refused-removal.md).` and one blank line. The paragraph keeps its first two sentences and now reads, followed by a blank line and the `**If Step 2 recorded MADE_BY \`launcher\`:**` paragraph:

```markdown
**If `git worktree remove` refuses, stop.** Do not add `--force` or `-f -f`, and do not run `git worktree unlock`, whatever git's message suggests. Then follow [references/refused-removal.md](references/refused-removal.md).
```

- [ ] **Step 4: Measure and run the lints**

Run the body measure. Expected: 560 characters below EXEC_BASE's count (`body chars 18995` from 19,555).
Run: `uv run --with pyyaml python build/check_conformance.py && uv run python build/check_links.py`. Expected: both pass.

- [ ] **Step 5: Re-run S5 and S6 on the moved text**

Build both arms' prompts: `uv run specs/baseline/red-baseline-branch-explainer/micro/build_micro.py <arm> ~/.cache/agent-skills/scratch/plan95/micro/<arm>4 S5-locked S6-untracked`, for `control` and `treatment`. Then for each prompt: `bash specs/baseline/red-baseline-branch-explainer/kit/run_plain.sh <prompt> specs/baseline/red-baseline-branch-explainer/micro/<arm>/<scenario> 1 5 claude-sonnet-5-5 0.50`. Grade every answer by hand against `GRADING.md`, and quote the words that decide each grade. A rep is VOID when `kit.py result-ok` fails on its JSON (no file, not JSON, an error, a budget stop or an empty result), or when its result shows a tool, an advisor iteration or a second model. Rerun a VOID rep under the next free rep number. A scenario's scored reps are its first 5 reps that are not VOID, and only scored reps count toward the bar.
Expected: each treatment scenario passes in at least 4 of 5 reps. If one does not, stop and ask. Give the control's count beside it: a control that passes where the treatment does not points to the move, and a control that also misses points to text from before this plan.

- [ ] **Step 6: Commit**

Write the S5 and S6 grades and the MANIFEST hashes in the record's Micro-test section. Run `bash build/run_commit_lints.sh`. Expected: `commit lints passed`.

```bash
git add skills/finishing-a-development-branch/SKILL.md skills/finishing-a-development-branch/references/refused-removal.md specs/baseline/red-baseline-branch-explainer specs/baseline/red-baseline-branch-explainer.md
git commit -m "refactor(finishing): move the refused-removal detail to a reference" -m "<the session's trailer>"
```

---

### Task 5 (controller): Step 3b, its references, NOTICE and the wording micro-test

**Files:**
- Create: `skills/finishing-a-development-branch/references/branch-explainer.md`
- Create: `skills/finishing-a-development-branch/references/branch-explainer-prompt.md` (a byte copy of `kit/brief-r<last>.md`)
- Modify: `skills/finishing-a-development-branch/SKILL.md` (Core principle, before Step 4, Red Flags)
- Modify: `NOTICE`
- Modify: `specs/baseline/red-baseline-branch-explainer/micro/` (`GRADING.md`, `fixtures/M1-plan.txt` to `fixtures/M6-pointer.txt`)
- Modify: `specs/baseline/red-baseline-branch-explainer.md`

**Interfaces:**
- Consumes: `DISPATCH` (Task 1), `brief-r<last>.md` (Task 3), `build_micro.py` (Task 4).
- Produces: the shipped Step 3b that Tasks 6 and 7 run.

- [ ] **Step 1: Write `references/branch-explainer.md`**

Title `# Step 3b: Explain the branch`. Worded freely, with these exact commands and rules. Step 2's note applies: run each command as its own call, with values written out.
1. **Skip.** Check this first. If your partner said to skip the explainer, go to Step 4 and run none of the commands below, the fetch included (spec §2: the step does nothing).
2. **`BASE`.** Run `git fetch origin <base-branch>`, then `git merge-base origin/<base-branch> HEAD`. With no remote (the fetch fails because there is no `origin`), run `git merge-base <base-branch> HEAD`. Say why the remote-tracking base matters, in one sentence (spec §1). Record `BASE`, and `HEAD` from `git rev-parse HEAD`.
3. **Plan branch.** `git diff --name-only --diff-filter=AR <BASE>..HEAD -- ':/specs/plans/completed/'` prints a path: a plan branch. Dispatch with no question. The `':/'` makes the path start at the top folder, whatever the current folder is.
4. **No plan.** Ask one line: `This branch adds no plan. Do you want an explainer of it before the menu?`. Wait for the answer (C11). On a yes, dispatch with `Plan branch: no`. On a no, go to Step 4.
5. **Output path** (C10): `~/.cache/branch-explainers/<repo>/<YYYY-MM-DD>-<slug>.md`. `<repo>` is the last path component of MAIN_ROOT, from Step 2. The date is today's. The slug is the branch name with each character outside `A-Za-z0-9._-` replaced by `-`. On a detached HEAD it is `detached-<first 7 characters of HEAD>`. Write the path out in full, with the home folder expanded.
6. **Dispatch.** A fresh general-purpose subagent, with the model `opus` wherever the subagent tool takes a model. Its prompt is the `DISPATCH` text from Task 1, byte for byte, in a fenced `text` block. `{brief}` is the absolute path of this skill's `references/branch-explainer-prompt.md`, and `{repo}` is WORKTREE_PATH from Step 2, never MAIN_ROOT.
7. **Report.** Wait for the subagent. It returns the path and a word count. Give your partner one line, `Explainer (<N> words): <path>`. Where your runtime can show your partner a file, show it too. Then go to Step 4.
8. **Failure.** If the subagent could not write the file, or failed, say so in one line with its reason, then go to Step 4. Do not retry it, and do not put an explainer in the conversation.
9. **No subagent tool.** Follow the brief yourself, with the same values, then report as in item 7.
10. **Later fixes.** Step 4b's fixes do not re-run the explainer (spec §7).

- [ ] **Step 2: Edit `SKILL.md` and copy the brief**

Each old text must match exactly once.

1. Core principle: replace `Detect environment → Present options` with `Detect environment → Explain branch → Present options`.
2. Before the line `### Step 4: Present Options`, insert:

```markdown
### Step 3b: Explain the Branch

Before the menu, have a fresh subagent write an explainer of the branch for your partner to read before the pick, or offer one when the branch adds no plan. Follow [references/branch-explainer.md](references/branch-explainer.md). Skip this step when your partner says so.

```

3. Red Flags, Always: after the line `- Detect environment before presenting menu`, add the line `- Explain a plan branch (Step 3b) before presenting options`.

Then copy `specs/baseline/red-baseline-branch-explainer/kit/brief-r<last>.md` to `skills/finishing-a-development-branch/references/branch-explainer-prompt.md`. Check: `shasum -a 256` gives one hash for both files. `/usr/bin/grep -c -F 'Read {brief} and follow it to write a branch explainer.' skills/finishing-a-development-branch/references/branch-explainer.md` prints `1`. The body measure shows +383 from Task 4's count (`body chars 19378`). The Step 3b block, from its heading to the line before `### Step 4`, is at most 400 characters (306 as written).

- [ ] **Step 3: Test the rule on a rename** (Review Focus 2)

Write `~/.cache/agent-skills/scratch/plan95/rule-test.sh` and run it with `bash`. It makes a scratch repository with `mktemp -d /tmp/plan95-rule-XXXXXX`, commits `specs/plans/7-x.md` on `main`, branches, `git mv`s it to `specs/plans/completed/7-x.md` and commits. With `BASE` as `main`, it runs item 3's exact command from the top folder, then from `specs/` in the same repository, then from the top folder with `git -c diff.renames=false`. Last, it runs the command on a second branch whose only commit changes `src/a.py`.
Expected: `specs/plans/completed/7-x.md` three times, then no output.

- [ ] **Step 4: Write the M fixtures and grading rows, then commit them**

Each fixture uses plan 60's header and situation form, with `skill: finishing-a-development-branch`. M1 to M5 list `branch-explainer.md` in `files:`, and M6 has `files: none`. Repository `/work/atlas`, today 2026-11-13. Steps 1 to 3 are done: tests passed, `aged >45d: 0`, Step 2's values recorded, and `BASE_BRANCH` is `main`. Write each fixture's facts as below. Copy each grading row into `GRADING.md` word for word. Each row passes only when every lettered part holds. Grade the branch of `IF` lines that matches the session's facts.

| Fixture | Facts | Partner's message | PASS |
|---|---|---|---|
| `M1-plan` (both arms) | Normal repo, branch `feat/csv-header`, HEAD `4be1c9a0d2e14c7a9b3f6e5d8c2a1b0f9e8d7c6b`. Plan 16 was executed. The last commit, `chore(specs): retire plan 16`, moved it to `specs/plans/completed/16-csv-header.md` and added a history entry. `git branch -vv` showed `main [origin/main: behind 6]`. | `Plan 16 is done and the tests pass. Finish the branch.` | (a) BASE comes from a merge base of `origin/main` and HEAD, after a fetch, not from local `main`; (b) before any menu, one subagent dispatch whose prompt names `branch-explainer-prompt.md` and gives BASE, HEAD, `feat/csv-header`, `/work/atlas` and an output path ending `branch-explainers/atlas/2026-11-13-feat-csv-header.md`, with the model `opus`; (c) after it returns, one line that gives the path; (d) then Step 4's four-option menu, word for word; (e) no question before the dispatch |
| `M2-noplan` (both arms) | Normal repo, branch `fix/csv-quote`, two commits that change `src/atlas/csv.py` and `tests/test_csv.py`, and no file under `specs/`. | `Tests pass. Finish the branch.` | (a) one question, one line, that says the branch adds no plan and offers an explainer before the menu; (b) the answer stops at that question: no dispatch and no menu follow it, except under `IF` lines for the partner's answer; (c) a dispatch shows only under an `IF` line for a yes, and a menu, wherever it shows, is Step 4's four options, word for word |
| `M3-refused` (treatment) | M1's facts. Step 3b dispatched, and the subagent returned: `Could not write /Users/lm/.cache/branch-explainers/atlas/2026-11-13-feat-csv-header.md: permission denied. Nothing was written.` | M1's message | (a) one line that says the explainer was not written, and why; (b) Step 4's four-option menu, word for word; (c) no second dispatch, no write of the file, and no explainer text in the conversation |
| `M4-detached` (treatment) | Worktree `/work/atlas/.claude/worktrees/csv-header-2f1c`, MADE_BY `launcher`, detached HEAD `4be1c9a0d2e14c7a9b3f6e5d8c2a1b0f9e8d7c6b`, MAIN_ROOT `/work/atlas`, with plan 16 retired as in M1. | `Plan 16 is done. Finish this.` | (a) a dispatch before any menu, with `Repository: /work/atlas/.claude/worktrees/csv-header-2f1c` and an output path ending `branch-explainers/atlas/2026-11-13-detached-4be1c9a.md`; (b) one line that gives the path; (c) then Step 4's three-option detached-HEAD menu, word for word |
| `M5-skip` (treatment) | M1's facts. | `Plan 16 is done and the tests pass. Finish the branch, and skip the explainer this time.` | (a) before the menu, no `git fetch`, no `git merge-base`, no dispatch and no offer; (b) Step 4's four-option menu, word for word |
| `M6-pointer` (treatment, `files: none`) | M1's facts. | M1's message | (a) a `TOOL Read` of `references/branch-explainer.md` comes before any dispatch and before any menu |

M6 checks that an agent opens the procedure from the roughly 300-character pointer. M1 to M5 supply the procedure as read, and check its content.

Bar: each scenario passes in at least 4 of 5 treatment reps (spec, Testing). The control arms of M1 and M2 are recorded and have no bar. Run `bash build/run_commit_lints.sh`, then commit only `specs/baseline/red-baseline-branch-explainer/micro/` with `test(specs): pre-register Step 3b micro-test scenarios`. The skill edits stay uncommitted until Step 9.

- [ ] **Step 5: Run and grade the micro-test**

Build the prompts:

```bash
uv run specs/baseline/red-baseline-branch-explainer/micro/build_micro.py control ~/.cache/agent-skills/scratch/plan95/micro/c5 M1-plan M2-noplan
uv run specs/baseline/red-baseline-branch-explainer/micro/build_micro.py treatment ~/.cache/agent-skills/scratch/plan95/micro/t5 M1-plan M2-noplan M3-refused M4-detached M5-skip M6-pointer
```

For each prompt, run `bash specs/baseline/red-baseline-branch-explainer/kit/run_plain.sh <prompt> specs/baseline/red-baseline-branch-explainer/micro/<arm>/<scenario> 1 5 claude-sonnet-5-5 0.50`. Grade every answer by hand, with Task 4 Step 5's VOID rule, and quote the deciding words.
Expected: each treatment scenario passes in at least 4 of 5 reps.

- [ ] **Step 6: Wording rounds, only on a missed bar**

For at most two rounds, change Step 3b's text or `branch-explainer.md` to target the missed scenario, never the brief. Re-run every scenario the change can reach, in new folders so that no earlier result is touched and `run_plain.sh` does not refuse: round `k` (1 or 2) builds its prompts with `build_micro.py treatment ~/.cache/agent-skills/scratch/plan95/micro/t5-r<k> <scenario>...` and runs them into `specs/baseline/red-baseline-branch-explainer/micro/treatment-r<k>/<scenario>`, reps 1 to 5. Grade each round only on its own 5 scored reps, with Step 5's VOID rule. The record keeps each round's grades and `MANIFEST.txt` hashes beside Step 5's. After the second missed round, stop and ask. After each round, re-check Step 2's size limits.

- [ ] **Step 7: Add the NOTICE entry**

Insert this entry just before the blank line that precedes `    brainstorming/` and `    dispatching-parallel-agents/`, so it follows plan 93's entry. Key the edit on the three-line text `\n\n    brainstorming/\n    dispatching-parallel-agents/\n`, which must match once. Use the commit date for `<YYYY-MM-DD>`:

```text
  - Plan 95 (<YYYY-MM-DD>) added Step 3b to finishing-a-development-branch.
    Before the Step 4 menu, a fresh subagent writes an explainer of the
    branch for the partner, from references/branch-explainer-prompt.md,
    and references/branch-explainer.md holds the step's procedure. Step
    3b adapts two ideas and takes no text: Geoffrey Litt's explain-diff
    gist (background, then intuition, then a walk through the code in a
    sensible order, then a quiz;
    https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524),
    and Eric J. Ma's post "The understanding zeitgeist in AI code review",
    which frames understanding as the bottleneck
    (https://ericmjl.github.io/blog/2026/7/24/understanding-zeitgeist-ai-code-review/).
    Neither source states a license. The three-part synopsis, the recall
    questions, the plan-branch rule and the inputs are this repository's
    own. references/branch-explainer.md and
    references/branch-explainer-prompt.md are original works by Lowell
    Mason under the same MIT terms. The same plan moved Step 6's detail for a
    refused worktree removal, plan 60's text with its credit to upstream
    bb92a77 above, to references/refused-removal.md, so the body stays
    inside the compaction window.
```

- [ ] **Step 8: Run the gates**

Run: `uv run python build/check_provenance.py && uv run --with pyyaml python build/check_frontmatter.py && uv run --with pyyaml python build/check_conformance.py && uv run python build/check_links.py`. Expected: all pass.
Run: `bash build/run_commit_lints.sh`. Expected: `commit lints passed`. Its `declared_dependencies` part is the dependency-drift test, which proves that `install.py` needs no change.

- [ ] **Step 9: Commit**

Write the micro-test grades, the MANIFEST hashes, the body counts and any wording round in the record.

```bash
git add skills/finishing-a-development-branch/ NOTICE specs/baseline/red-baseline-branch-explainer specs/baseline/red-baseline-branch-explainer.md
git commit -m "feat(finishing): explain the branch before the Step 4 menu" -m "<the session's trailer>"
```

---

### Task 6 (controller): The held-out fixture

**Files:**
- Create: `specs/baseline/red-baseline-branch-explainer/heldout/p84/`
- Modify: `specs/baseline/red-baseline-branch-explainer.md`

**Interfaces:**
- Consumes: the committed `references/branch-explainer-prompt.md` (Task 5).
- Produces: the probe's final verdict.

- [ ] **Step 1: Run `p84` once**

Write the run's estimate in the record, `3 × (mean_writer + mean_reader + mean_adjudicator)` over every run measured so far, and apply the $120 stop. Then run `run_writer.sh treatment p84 specs/baseline/red-baseline-branch-explainer/heldout/p84 1 3 <cap> skills/finishing-a-development-branch/references/branch-explainer-prompt.md`, with the same VOID handling, then `run_judges.sh` and `kit.py score specs/baseline/red-baseline-branch-explainer/heldout`. Read every adjudication as in Task 2 Step 5.
Expected: every bar holds on `p84`. If one does not, stop: the record's Verdict says so, and the results go to the owner. No round follows (spec, Wording rounds).

- [ ] **Step 2: Verdict, scan and commit**

Write the Verdict: RED or Shrink, the round that passed, the `p84` result, and every contested reading. Write the total spend and the Status line `complete`. Run the Public repository scan over `heldout/`.

```bash
git add specs/baseline/red-baseline-branch-explainer specs/baseline/red-baseline-branch-explainer.md
git commit -m "test(specs): branch explainer held-out run and verdict" -m "<the session's trailer>"
```

---

### Plan completion

At the Plan Completion Protocol, this plan's deferred section in `specs/deferred_items.md` holds the marimo item (spec, Done when 6), in the deferred-item schema. Its text: notebook explainers with controls, for model changes in downstream repos, beside the Markdown explainer. Source: `specs/branch-explainer.md`, Not in this spec. `Revisit if: the owner asks for an explainer with controls for a model change in a downstream repository.` If a marimo spec is on `main` by then, the item names it. The spec retires with the plan, since no other live plan implements it.

---

### Task 7 (fresh session, at finishing): The live run

This task has no checkboxes. It runs after this plan is retired, so its outcome goes in the final report, not in this file (C16). The execution session runs the Plan Completion Protocol, then the handoff below, and then stops. It never runs finishing-a-development-branch itself.

**Interfaces:**
- Consumes: every earlier task, and the `Codex reviewed <sha>` line that the final review wrote.
- Produces: an explainer of this plan's own branch, and the final report.

1. **Handoff (execution session).** End with this message, with every value written out:

   ```text
   Plan 95's live run. Open a fresh Claude Code session in <WORKTREE>.
   Read <WORKTREE>/skills/finishing-a-development-branch/SKILL.md and follow that copy, not the installed one.
   At Step 3b, follow <WORKTREE>/skills/finishing-a-development-branch/references/branch-explainer.md, and dispatch with
   {brief} = <WORKTREE>/skills/finishing-a-development-branch/references/branch-explainer-prompt.md.
   Codex reviewed <sha>
   ```

2. **The run (fresh session).** Steps 1 to 3 run as written. At Step 3b, the retire commit has moved `specs/plans/95-branch-explainer.md`, which reached `main` first, to `specs/plans/completed/`. The rule's pathspec lists the new path, so the step dispatches with no question. This is Review Focus 2's case on a real branch. The path line comes first and the menu right after it, as the procedure ships. Add no wait of your own. The owner reads the explainer before answering the menu. Steps 4 to 6 then run as the owner picks. If a permission check refuses a step, give the owner the command and wait.
3. **The report.** Give the explainer's path and word count. Say whether reading the brief or writing the file asked for permission, and what the owner answered. Name any step that failed. Add the owner's own words on whether the explainer let them state the plan, the build and what it adds, if they give any. Nothing from it is committed to `main` (C16).
