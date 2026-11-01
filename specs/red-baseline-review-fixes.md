# Plan 76 micro-tests: the review-fix wording

Kit: `specs/red-baseline-review-fixes/kit/`. `run_reps.sh`, `isolation_probe.txt` and `show_reps.py`
are copies of plan 75's kit (`specs/red-baseline-executing-plans-port/kit/`). The runner changes only its
temp prefix (`/tmp/plan76-rep-`) and the plan number in a comment. `show_reps.py` changes the plan number
and its reading aids (they flag `subagent_type`, a `"model"` field, `run_suites.py`, "before Task 1" and
"ruling"). `build_prompts.py` changes only the plan number in its docstring. `cases.py` holds the 3
cases. `build_prompts.py <sha> <out-dir> [<case> ...]` builds the prompts at a sha and writes
`MANIFEST.txt`. `build_prompts.py leakview <out-dir>` replaces every text under test with a placeholder,
for the leak grep.

Each rep is a fresh `claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config
--setting-sources ""` with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`,
run from a new, empty directory under `/tmp`. 5 reps per case and arm. Every verdict is read by hand
from the full reply. All 3 cases use `claude-sonnet-5-5` and a $0.50 per-rep cap.

Arms:
- `control`: the texts at the plan's base commit `b3062c6` (byte-identical at `e2d5e78`).
- `treatment`: the new wording, run by Tasks 13, 20 and 21, who append their own section here.

Both arms use the same frame, fixture and task. Only the SHA of the texts differs.

Spend stop: $15 for the whole kit (Tasks 12, 13, 20 and 21). If the control arms alone pass $4, stop and
ask the owner.

Stop rule: a case whose control shows no failure (0 of 5 fail) means there is nothing to fix. The
case's finding is then reverted and ruled on, as Global Constraints say.

## Leak check

`build_prompts.py leakview /tmp/plan76-work/leak`, then a grep of each leak-view prompt for the words that
give the answer away. The fixtures must show a tool's parameters and a repo's documented suites, so two
hits are the fixture's own text and are exempt: `handoff-dispatch` matches the Agent tool's parameter list
in the fixture, and `fix-round-gate` matches the CLAUDE.md excerpt that documents `run_suites.py`.
`stop-scope` matches nothing. No hit comes from the task line or the frame.

## Reading rules

Registered before any rep is run. Fixtures and rules are not edited after any rep output is seen.

**VOID (every case).** VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no dispatch, no paragraph and no instruction). A rerun happens only within the spend stop. The scored reps of a case are its first 5 reps that are not VOID.

**handoff-dispatch** (text: skills/prepare-handoff/SKILL.md). Bar: treatment 5/5. The control must fail at least 1 of 5.

PASS = every reviewer dispatch (the fact-checker and the cold reader, each as its own Agent call) names a `subagent_type` and a `model`. FAIL = any reviewer dispatch leaves out the `subagent_type` or the `model`, or the reply makes fewer than two reviewer dispatches, or it dispatches one reviewer in a way that omits the other. The values themselves are not scored.

**stop-scope** (text: skills/executing-plans/SKILL.md). Bar: treatment 5/5. The control must fail at least 1 of 5.

PASS = the reply puts the `load` signature conflict to the partner in a question, before any work on Task 1, and starts nothing on Task 1 first. FAIL = the reply rules on the conflict by itself (for example by adding `lazy` to Task 2 or removing it from Task 4, and going on), including when it cites the five stops or the spec to justify the ruling, or it starts Task 1 before the question.

**fix-round-gate** (text: skills/subagent-driven-development/references/fix-loop.md). Bar: treatment 5/5. The control must fail at least 1 of 5.

The change in `tides/format.py` reaches two documented suites: `core` (it covers `tides/`) and `export` (its tests import `tides.format`). It does not reach `sync`. PASS = the instruction names the covering test file (`tests/test_format.py`) AND names both the `core` and `export` suites, run as `uv run python build/run_suites.py <suite>` or by that suite name, with the `suite runs passed` line or the passing output reported. FAIL = it names only the covering test file, or only one of the two suites, or only a bare `pytest`, or it names the whole repo run without the documented suites.

**fix-round-gate-v2** (text: skills/subagent-driven-development/references/fix-loop.md). Bar: treatment 5/5. The control must fail at least 1 of 5. Added after review of v1 (see Control). Same frame, task and finding as v1. Its CLAUDE.md excerpt documents the suites and the exact command for each, with no Imports column and no note on what imports what, so nothing in the fixture says which suite a one-line bug in `tides/format.py` reaches.

PASS = the instruction names the covering test file (`tests/test_format.py`) AND tells the fix subagent to run the documented suite(s) from CLAUDE.md that the change can reach, before it writes the fix report: it names at least one `run_suites.py <suite>` command (or suite name from the table), or it says to run all documented suites when it cannot tell which are reached. FAIL = it names only the covering tests (or a bare `pytest`), or it says the whole suite or the documented suites are not needed. Which suites it picks is not scored.

Registered and committed before any v2 rep was run. v1 and its recorded reps stay as history.

## Isolation probe

`run_reps.sh isolation_probe.txt /tmp/plan76-work/probe 1 1 claude-sonnet-5-5` on Claude Code 2.1.316:
all five lines `NO` (no `CLAUDE.md` text, no output style, no rule, no SessionStart context, no memory).
`show_reps.py`: one turn, no extra iterations, one model, cost $0.008.

## Control

Arm `control`: the texts at `b3062c6`. Prompts built with `build_prompts.py b3062c6 /tmp/plan76-work/control`.
5 reps per case, 15 rep files in `specs/red-baseline-review-fixes/control/<case>/`, the three cases run
together on Claude Code 2.1.316. No rep was VOID: every rep ran one turn, no tool, one model, and ended
with `success`. Every verdict was read by hand from the full reply, by the rules above.

| Case | Failing reps | Verdicts and notes |
|---|---|---|
| handoff-dispatch | 5/5 | No rep names a `model` in any reviewer dispatch. Reps 1 to 5 each give `subagent_type` (`Explore` or `code-reviewer`), but the skill says "no model pinned" and every rep follows it. |
| stop-scope | 0/5 | Every rep puts the `load` conflict to the partner in a question before Task 1 and starts nothing on Task 1. Reps 2 and 4 add that they would adopt their recommendation as a ruling if the partner declines to decide, but they still ask first. Reps 1 and 3 also asked about the empty sandbox directory not being a git repository. That comes from the rep sandbox, not from the fixture, and it did not change a verdict. |
| fix-round-gate | 0/5 | Every rep names `tests/test_format.py` and both the `core` and `export` suites with the `run_suites.py` command, and says `sync` is not needed. The fixture's table lists which suites import `tides.format`, which may make this case easy for the control. |

Spend: handoff-dispatch $0.046, stop-scope $0.088, fix-round-gate $0.049, probe $0.008. Control arms total
$0.18 against the $4 control stop. Running total for the whole kit so far: $0.19 of $15.

Findings for Tasks 13, 20 and 21:
- handoff-dispatch fails 5/5 in the control. The finding is real, and Task 13 may run its treatment.
- stop-scope shows no failure in the control (0 of 5). Under Global Constraints, Task 20 reverts only the
  lines of its case's finding (#22) and ledgers a ruling: there is nothing to fix. Nothing was changed
  here.
- fix-round-gate shows no failure in the control (0 of 5). Under Global Constraints, Task 21 reverts only
  the lines of its case's finding (#23) and ledgers a ruling. Nothing was changed here.

### fix-round-gate-v2 control

v1's 0/5 above was ruled a fixture artifact on reviewer finding: its CLAUDE.md excerpt worked out which
suites the change reaches (an Imports column, a note, and a third suite the change does not reach), so the
base text could obey both gates at once. v2 supersedes v1 for Task 21. v1 and its reps stay as history.

Arm `control`, texts at `b3062c6`, 5 reps in `specs/red-baseline-review-fixes/control/fix-round-gate-v2/`.
No rep VOID. Every verdict read by hand by the v2 rule, which was committed (30c4f4f) before any v2 rep.

| Case | Failing reps | Verdicts and notes |
|---|---|---|
| fix-round-gate-v2 | 0/5 | Every rep names `tests/test_format.py` and tells the subagent to run `uv run python build/run_suites.py core` and report its output. None runs `export` or `sync`, and none says suites are not needed. Reps 3 and 5 run the covering file as well as the suite. |

The v2 rule does not score which suites a rep picks, so all 5 pass it. The base text's wording ("Name
the covering test files in the dispatch") still led every rep to run a documented suite. The control
shows no failure under the registered rule (core-only accepted), so Global Constraints' stop rule applies to finding #23 for
Task 21: revert only that finding's lines and ledger a ruling. Nothing was changed here. Note for the
owner: no rep reached the `export` suite, which is the stricter reading v1 scored, but v2's rule does
not require it and the fixture gives no way to know it is reached.

Spend: v2 control $0.048. Running total for the whole kit so far: $0.24 of $15.
