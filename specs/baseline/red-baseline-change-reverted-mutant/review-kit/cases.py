'''Frozen inputs for plan 97's reviewer micro-test (specs/plans/97-change-reverted-mutant.md, Task 8).

Three cases, R4 to R6. Each case is one package of seven files in ../reviewer/packages/R<n>/, which
build_packages.py makes with the scripts at SCRIPT_SHA. This module holds what build_prompts.py
needs to frame a prompt (the frame, the task and the dispatch's fill values) and what
build_packages.py needs to name the repository that the packages show. The `bar` and `leak`
strings are for the reader and the leak check only: build_prompts.py never writes them into a
prompt.

VOID, REVIEWER_FRAME and REVIEWER_TASK are copied word for word from plan 93's review kit
(specs/baseline/red-baseline-mutant-checked-tests/review-kit/cases.py), which copied them from
plan 84's. Only the `short` arm is kept (D8). The domains are a date window (R4 and R5, new) and
F8's byte sizes (R6, ../impl-kit/fixtures/F8/, with its own rules).
'''

MODEL = 'sonnet'
BUDGET = '0.50'

# The scripts the packages are built with: Task 2's last commit, as the implementer micro-test uses.
SCRIPT_SHA = '60f33488d1a03decec18ba54b2f648d09e5dd879'

# The repository and workspace the packages show. build_packages.py writes the scratch
# repository's path as REPO in every copied file.
REPO = '/work/project'
PLAN_FILE = 'plan.md'
WORKSPACE = f'{REPO}/.sdd/plan'
SUITE_COMMAND = '/tmp/mt-venv/bin/python -m pytest -q'

VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no edit, no command, no report and no question about the task's subject).'''

# `short`: the agent definition is the system prompt, and the Short Form is the dispatch.
REVIEWER_FRAME = '''You are the task-reviewer subagent on Claude Code. Your agent definition, which is your system prompt:

{texts}

The dispatch prompt you received follows. The files it names are inlined after it, as you would read them. You have no tools in this turn.

<dispatch>
{fixture}
</dispatch>

{task}
'''
REVIEWER_TASK = 'Write your review report now, in the format your agent definition gives.'

# [GLOBAL_CONSTRAINTS]: each spec's rules, verbatim (specs/window.md:7-8, specs/sizes.md:7-9).
WINDOW_CONSTRAINTS = '''- A window starts on its start date: a day before the start date is outside it.
- A window includes its end date: a day after the end date is outside it.'''
SIZES_CONSTRAINTS = '''- `to_bytes` reads a size: a number of one or more digits `0` to `9`, then a unit, `B`, `KB` or `MB`, with nothing between them.
- 1 KB is 1024 B, and 1 MB is 1024 KB.
- `to_bytes` raises `ValueError` for any other text.'''

TEST_RULINGS = 'none'

# The template at the execution base holds all four; a template that lacks any of them is refused.
NEW_PLACEHOLDERS = ('[SPEC_EXCERPTS_FILE]', '[MUTANTS_FILE]', '[MUTANT_RUN_FILE]', '[TEST_RULINGS]')

# The leak check's words (the record, Reviewer leak check). Each is grepped with -i.
LEAK_WORDS = ('check 7', 'keeps', 'strengthen', 'pre-change', 'passes on', 'passing on', 'revert finding',
              'important finding', 'plan 97', 'plan 93', 'agent-skills', 'red-baseline', 'micro-test',
              'baseline', 'control', 'treatment', 'decoy', 'change-reverted', 'bar', 'R4', 'R5', 'R6')

R4_BAR = ('An Important finding that names test_window_includes_end_date as passing on the code from '
          'before the task (the revert), in at least 4 of 5 scored reps.')
R5_BAR = 'No revert finding, in at least 4 of 5 scored reps (treatment only, D9).'
R6_BAR = 'No revert finding, in at least 4 of 5 scored reps (treatment only, D9).'

CASES = {
    'R4': {'package': 'R4', 'bar': R4_BAR, 'constraints': WINDOW_CONSTRAINTS},
    'R5': {'package': 'R5', 'bar': R5_BAR, 'constraints': WINDOW_CONSTRAINTS},
    'R6': {'package': 'R6', 'bar': R6_BAR, 'constraints': SIZES_CONSTRAINTS},
}
