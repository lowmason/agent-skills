# Grading: plan 94's Step 3b micro-test

Each rep is one tool-less `claude -p` answer on `claude-sonnet-5-5`, run by `kit/run_plain.sh` from a prompt that
`build_micro.py` builds. The answer is a numbered list of `RUN`, `TOOL`, `EDIT`, `ASK` and `REPORT` actions, with `IF`
lines for outcomes the agent has not seen. The executor grades every answer by hand and quotes the deciding words.

## Rules for every scenario

**Read rule.** A TOOL Read of a file under references/ is an allowed read-only step. Grade the actions after it, IF lines included. An answer that ends at the Read, with no action after it, is NEITHER, which does not count as PASS, except in M6.

**VOID rule.** A rep is VOID when `kit.py result-ok` fails on its JSON (no file, not JSON, an error, a budget stop or
an empty result), or when its result shows a tool, an advisor iteration or a second model. Rerun a VOID rep under the
next free rep number. A scenario's scored reps are its first 5 reps that are not VOID, and only scored reps count
toward the bar.

The screen for the second half of the VOID rule is plan 60's `exclusion_reason`: the JSON's `usage.iterations` holds a
type other than `message`, or `modelUsage` names more than one model, or either record is missing. A `num_turns`
above 1 or a non-empty `permission_denials` also shows a tool.

**Bar.** Each treatment scenario passes in at least 4 of 5 scored reps. The control arms of M1 and M2 are recorded
and have no bar.

## Scenarios

Copied word for word from plan 94, Task 5 Step 4. Each row passes only when every lettered part holds. Grade the branch of `IF` lines that matches the session's facts. M1 to M5 list `branch-explainer.md` in `files:`, and M6 has `files: none`.

| Fixture | Facts | Partner's message | PASS |
|---|---|---|---|
| `M1-plan` (both arms) | Normal repo, branch `feat/csv-header`, HEAD `4be1c9a0d2e14c7a9b3f6e5d8c2a1b0f9e8d7c6b`. Plan 16 was executed. The last commit, `chore(specs): retire plan 16`, moved it to `specs/plans/completed/16-csv-header.md` and added a history entry. `git branch -vv` showed `main [origin/main: behind 6]`. | `Plan 16 is done and the tests pass. Finish the branch.` | (a) BASE comes from a merge base of `origin/main` and HEAD, after a fetch, not from local `main`; (b) before any menu, one subagent dispatch whose prompt names `branch-explainer-prompt.md` and gives BASE, HEAD, `feat/csv-header`, `/work/atlas` and an output path ending `branch-explainers/atlas/2026-11-13-feat-csv-header.md`, with the model `opus`; (c) after it returns, one line that gives the path; (d) then Step 4's four-option menu, word for word; (e) no question before the dispatch |
| `M2-noplan` (both arms) | Normal repo, branch `fix/csv-quote`, two commits that change `src/atlas/csv.py` and `tests/test_csv.py`, and no file under `specs/`. | `Tests pass. Finish the branch.` | (a) one question, one line, that says the branch adds no plan and offers an explainer before the menu; (b) the answer stops at that question: no dispatch and no menu follow it, except under `IF` lines for the partner's answer; (c) a dispatch shows only under an `IF` line for a yes, and a menu, wherever it shows, is Step 4's four options, word for word |
| `M3-refused` (treatment) | M1's facts. Step 3b dispatched, and the subagent returned: `Could not write /Users/lm/.cache/branch-explainers/atlas/2026-11-13-feat-csv-header.md: permission denied. Nothing was written.` | M1's message | (a) one line that says the explainer was not written, and why; (b) Step 4's four-option menu, word for word; (c) no second dispatch, no write of the file, and no explainer text in the conversation |
| `M4-detached` (treatment) | Worktree `/work/atlas/.claude/worktrees/csv-header-2f1c`, MADE_BY `launcher`, detached HEAD `4be1c9a0d2e14c7a9b3f6e5d8c2a1b0f9e8d7c6b`, MAIN_ROOT `/work/atlas`, with plan 16 retired as in M1. | `Plan 16 is done. Finish this.` | (a) a dispatch before any menu, with `Repository: /work/atlas/.claude/worktrees/csv-header-2f1c` and an output path ending `branch-explainers/atlas/2026-11-13-detached-4be1c9a.md`; (b) one line that gives the path; (c) then Step 4's three-option detached-HEAD menu, word for word |
| `M5-skip` (treatment) | M1's facts. | `Plan 16 is done and the tests pass. Finish the branch, and skip the explainer this time.` | (a) before the menu, no `git fetch`, no `git merge-base`, no dispatch and no offer; (b) Step 4's four-option menu, word for word |
| `M6-pointer` (treatment, `files: none`) | M1's facts. | M1's message | (a) a `TOOL Read` of `references/branch-explainer.md` comes before any dispatch and before any menu |
