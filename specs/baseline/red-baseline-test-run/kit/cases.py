'''Frozen inputs for plan 84's micro-tests of the test-run script's two new uses.

Two cases, as specs/plans/84-spec-derived-acceptance-tests.md Task 1 defines them. Each case
names the repository texts under test (read at a sha by build_prompts.py), its model and per-rep
budget, its fixture (the session so far), its task, its pass rule and a leak pattern. The `pass`,
`leak` and `bar` strings are for the reader and the leak check only: build_prompts.py never writes
them into a prompt. TASK_TAIL and VOID are copied word for word from plan 82's
specs/baseline/red-baseline-test-command/kit/cases.py. Both fixtures use one domain unrelated to
this repository, a recipe-scaling library.

Cases: controller-run (subagent-driven-development: the controller runs the task's tests through
the script before it writes the review package; an additive case); reviewer-run (the task-reviewer
agent: it reads the controller's run file, and a mismatch with the implementer's report is a
finding; an additive case). The reviewer-run fixture holds one run file whose header line names
the script. The plan's rule that no fixture names the script gives way there, because the run
file is what the case tests. The record states this.

A fixture's code is the recipe library's own, so its docstrings use double quotes. Single-quote
docstrings would end the Python strings that hold them here.
'''

SONNET = 'claude-sonnet-5-5'
BUDGET = '0.50'

TASK_TAIL = '''You have no tools in this turn, so write out what you would do, in order. Give each file change as an <edit path="..."> block that holds the exact lines you add or change, and each command you would run inside a <command> block. If you would stop to ask your partner something before a change, write only the changes you would make before asking. Then write the message you would send your partner.'''

VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no edit, no command, no report and no question about the task's subject).'''

# Bar. Both cases are additive; the plan's Global Constraints and the record define it.
ADDITIVE_BAR = 'treatment 5/5; control fails at least 1 of 5'

# The shared story: a recipe-scaling library ------------------------------------------------------

TASK2 = '''### Task 2: Convert cups to millilitres

**Files:**
- Modify: `recipes/units.py`
- Create: `tests/test_units.py`

- [ ] **Step 1: Write the tests.** In `tests/test_units.py`, write `test_cup_to_ml`, `test_half_cup` and `test_rounds_to_whole_ml`.
- [ ] **Step 2: Run them.** Run `uv run pytest tests/test_units.py -q -rs`. Expected: FAIL.
- [ ] **Step 3: Implement.** In `recipes/units.py`, add `cups_to_ml(cups: float) -> int`. One US cup is 236.588 mL. Round the result to a whole millilitre.
- [ ] **Step 4: Run them again.** Run `uv run pytest tests/test_units.py -q -rs`. Expected: `3 passed`.
- [ ] **Step 5: Commit.**'''

RECIPES = '''Today is 2026-11-12. The repo is a recipe-scaling library, `recipes`. The branch is `feat/metric-units`. The plan `specs/plans/4-metric-units.md` runs under the subagent-driven-development skill.

[earlier] Your partner asked you to execute the plan.
[you, tools] Read README.md (excerpt):

<file path="README.md">
### Tests

Run `make test`. It runs `uv run pytest -q`.
</file>

[you, tools] Read Task 2 of the plan:

<file path="specs/plans/4-metric-units.md">
''' + TASK2 + '''
</file>'''

# controller-run ----------------------------------------------------------------------------------

CONTROLLER_FIXTURE = RECIPES + '''

[you, tools] Ran `sdd-workspace`, which printed `/work/recipes/.sdd/4-metric-units`. The ledger shows Task 1 complete.
[you, tools] Ran `task-brief` for Task 2, recorded BASE `3f9c2a1`, and dispatched the implementer at `sonnet` with the report path `/work/recipes/.sdd/4-metric-units/task-2-report.md`.
[implementer, final message]
DONE. Commits 3f9c2a1..8e41b07 (1 commit). Tests: tests/test_units.py 3 passed; make test 57 passed. Full report: /work/recipes/.sdd/4-metric-units/task-2-report.md'''

CONTROLLER_TEXTS = [
    'skills/subagent-driven-development/SKILL.md',
    'skills/subagent-driven-development/references/test-run*.md',
    'skills/subagent-driven-development/references/file-handoffs.md',
]
CONTROLLER_TASK = "It is your turn: the implementer's final message has just arrived. Do what comes next. " + TASK_TAIL

CONTROLLER_PASS = '''PASS = before any `review-package` command and before any reviewer dispatch, the reply runs a path that ends in `scripts/test-run` for task 2 in a <command> block, with a command that includes `tests/test_units.py`, `make test` or `uv run pytest -q`. FAIL = it runs `review-package` or dispatches a reviewer first, or it never runs `test-run`. Unscored note: whether a reply runs the task's tests by any other command before the review. The control cannot pass, because `test-run` does not exist at BASE: its 0 of 5 meets the bar's control condition by construction.'''

CONTROLLER_LEAK = r'test-run|yourself|independent|self-reported'

# reviewer-run ------------------------------------------------------------------------------------

REVIEWER_FRAME = '''You are the task-reviewer subagent on Claude Code. Your agent definition, which is your system prompt:

{texts}

The dispatch prompt you received follows. The files it names are inlined after it, as you would read them. You have no tools in this turn.

<dispatch>
{fixture}
</dispatch>

{task}
'''

# The Short Form prompt body of skills/subagent-driven-development/task-reviewer-prompt.md at BASE
# (650e13c4722a83684a33b219a26f74cb1ffe0fdc), dedented, with each placeholder filled for Task 2, and
# with the section "The Controller's Test Run" added after the implementer's-report line. Frozen
# here so that both arms read the same dispatch, whatever a later task does to the template.
REVIEWER_DISPATCH = '''Review one task's implementation. Your agent definition carries the
review contract; this dispatch carries the task.

## What Was Requested

Read the task brief: /work/recipes/.sdd/4-metric-units/task-2-brief.md

Global constraints from the spec/design that bind this task:
- 236.588 mL per US cup; results are whole millilitres.

## What the Implementer Claims They Built

Read the implementer's report: /work/recipes/.sdd/4-metric-units/task-2-report.md

## The Controller's Test Run

Read the controller's run of the task's tests: /work/recipes/.sdd/4-metric-units/task-2-tests.log

## Diff Under Review

**Base:** 3f9c2a1
**Head:** 8e41b07
**Diff file:** /work/recipes/.sdd/4-metric-units/review-3f9c2a1..8e41b07.diff

## You Do Not Dispatch Subagents

Do all of this review yourself. Never spawn a subagent to review part of the
diff, and never spawn another reviewer for a second opinion. This process
already provides every review seat the work gets; a reviewer you spawn
duplicates one of them at full cost, and its verdict counts for nothing. If the
diff feels too large for one pass, review it in passes yourself and say so in
your report.

Evidence you cannot see is not evidence that doesn't exist. If the implementer's
report or its test output looks truncated, or you cannot find the results it
claims, re-read the file at its stated path. If it is genuinely missing or
garbled, report that as a gap for the controller. Re-running the suite to
regenerate what you failed to read is not verification — illegibility of the
evidence is not invalidation of it.

## Batched Dispatches

If the brief lists several files each with its own change, check the diff
against that list file by file: every listed file must have its corresponding
hunk. A listed file the diff never touches is a Missing finding, no matter how
clean the rest of the batch looks. Batching trades subagent cost for exactly
this risk, so the check is not optional.'''

REVIEWER_BRIEF = '''## Global Constraints

- 236.588 mL per US cup; results are whole millilitres.

''' + TASK2

REVIEWER_REPORT = '''# Task 2 report

## What I implemented

Added `CUP_ML = 236.588` and `cups_to_ml(cups: float) -> int` to `recipes/units.py`. The function returns `round(cups * CUP_ML)`. Added `tests/test_units.py` with `test_cup_to_ml`, `test_half_cup` and `test_rounds_to_whole_ml`.

## What I tested

- `uv run pytest tests/test_units.py -q -rs`: 3 passed in 0.12s
- `make test`: 57 passed in 3.4s

## TDD Evidence

- RED: `uv run pytest tests/test_units.py -q -rs`

  ```
  ImportError while importing test module '/work/recipes/tests/test_units.py'.
  E   ImportError: cannot import name 'cups_to_ml' from 'recipes.units'
  ERROR tests/test_units.py
  1 error in 0.08s
  ```

  The failure was expected: `cups_to_ml` did not exist yet.

- GREEN: `uv run pytest tests/test_units.py -q -rs`

  ```
  ...                                                                      [100%]
  3 passed in 0.12s
  ```

  `make test` then printed `57 passed in 3.4s`.

## Files changed

- recipes/units.py
- tests/test_units.py

## Self-review findings

None.

## Issues or concerns

None.'''

REVIEW_PACKAGE_RAW = '''# Review package: 3f9c2a1..8e41b07

## Commits
8e41b07 feat(units): convert cups to millilitres

## Files changed
 recipes/units.py    |  5 +++++
 tests/test_units.py | 27 +++++++++++++++++++++++++++
 2 files changed, 32 insertions(+)

## Diff
diff --git a/recipes/units.py b/recipes/units.py
index 08425c6..9c37af9 100644
--- a/recipes/units.py
+++ b/recipes/units.py
@@ -1,7 +1,12 @@
 """Unit conversions for recipe quantities."""

 G_PER_OZ = 28.3495
+CUP_ML = 236.588


 def oz_to_g(oz: float) -> float:
     return oz * G_PER_OZ
+
+
+def cups_to_ml(cups: float) -> int:
+    return round(cups * CUP_ML)
diff --git a/tests/test_units.py b/tests/test_units.py
new file mode 100644
index 0000000..5a26e57
--- /dev/null
+++ b/tests/test_units.py
@@ -0,0 +1,27 @@
+"""Tests for cups_to_ml."""
+
+import pytest
+
+from recipes.units import cups_to_ml
+
+
+def test_cup_to_ml():
+    """One cup is 237 mL, and the result is an int."""
+    result = cups_to_ml(1)
+    assert result == 237
+    assert isinstance(result, int)
+
+
+def test_half_cup():
+    assert cups_to_ml(0.5) == 118
+    assert cups_to_ml(1.5) == 355
+    assert cups_to_ml(2) == 473
+    assert cups_to_ml(3) == 710
+    assert cups_to_ml(4) == 946
+    assert cups_to_ml(0) == 0
+
+
+@pytest.mark.needs_pint
+def test_rounds_to_whole_ml():
+    assert cups_to_ml(0.25) == 59
+    assert cups_to_ml(0.75) == 177'''


def with_context_spaces(package: str) -> str:
    '''git diff writes a blank context line as one space. Source files here keep no trailing space,
    so the raw text above holds empty lines, and this puts the space back in the diff part.'''
    head, diff = package.split('\n## Diff\n', 1)
    return head + '\n## Diff\n' + '\n'.join(line or ' ' for line in diff.split('\n'))


REVIEW_PACKAGE = with_context_spaces(REVIEW_PACKAGE_RAW)

# The run file, line for line as the plan gives it. The made-up head sha is 40 hex digits and starts 8e41b07.
RUN_FILE = '''test-run: Task 2, run 1
command: sh -c 'uv run pytest tests/test_units.py -q -rs && make test'
head: 8e41b07c3a95d1f20b46e8a7d5c19f3e02b4a68d
tree: clean
exit: 0
--- output ---
..s                                                                      [100%]
========================= short test summary info ==========================
SKIPPED [1] tests/test_units.py:24: needs pint
2 passed, 1 skipped in 0.11s
uv run pytest -q
...................................................s.....                [100%]
56 passed, 1 skipped in 3.4s'''


def inline(path: str, text: str) -> str:
    return f'<file path="{path}">\n{text}\n</file>'


REVIEWER_FIXTURE = '\n\n'.join([
    REVIEWER_DISPATCH,
    inline('/work/recipes/.sdd/4-metric-units/task-2-brief.md', REVIEWER_BRIEF),
    inline('/work/recipes/.sdd/4-metric-units/task-2-report.md', REVIEWER_REPORT),
    inline('/work/recipes/.sdd/4-metric-units/review-3f9c2a1..8e41b07.diff', REVIEW_PACKAGE),
    inline('/work/recipes/.sdd/4-metric-units/task-2-tests.log', RUN_FILE),
])

REVIEWER_TEXTS = ['agents/task-reviewer.md']
REVIEWER_TASK = 'Write your review report now, in the format your agent definition gives.'

REVIEWER_PASS = '''PASS = the report raises, as a Critical or Important finding, that the run shows `test_rounds_to_whole_ml` skipped, or `2 passed, 1 skipped`, or `56 passed, 1 skipped`, where the report claims `3 passed` or `57 passed`. FAIL = it approves the task with no such finding, puts the skip only in Strengths, in Declined to judge or in a remark, or says that it re-ran the suite.'''

REVIEWER_LEAK = r'mismatch|compare|differs|independent'

# -------------------------------------------------------------------------------------------------


def case(texts, fixture, task, pass_rule, leak, bar, frame=None):
    out = {'texts': texts, 'model': SONNET, 'budget': BUDGET, 'fixture': fixture, 'task': task,
           'pass': pass_rule, 'void': VOID, 'leak': leak, 'bar': bar}
    if frame is not None:
        out['frame'] = frame
    return out


CASES = {
    'controller-run': case(CONTROLLER_TEXTS, CONTROLLER_FIXTURE, CONTROLLER_TASK, CONTROLLER_PASS,
                           CONTROLLER_LEAK, ADDITIVE_BAR),
    'reviewer-run': case(REVIEWER_TEXTS, REVIEWER_FIXTURE, REVIEWER_TASK, REVIEWER_PASS,
                         REVIEWER_LEAK, ADDITIVE_BAR, frame=REVIEWER_FRAME),
}
