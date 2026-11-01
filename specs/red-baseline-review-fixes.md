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
