'''Frozen inputs for plan 93's reviewer micro-test (specs/plans/93-mutant-checked-tests.md, Task 6).

Three cases, R1 to R3. Each case is one package of seven files in ../reviewer/packages/R<n>/, which
build_packages.py makes with this worktree's scripts. This module holds what build_prompts.py needs
to frame a prompt (the frames, the tasks, the dispatch's fill values and the control arm's fixed
line) and the names that build_packages.py gives the repository the packages show. The `bar` and
`leak` strings are for the reader and the leak check only: build_prompts.py never writes them into
a prompt.

VOID, REVIEWER_FRAME and REVIEWER_TASK are copied word for word from plan 84's
specs/baseline/red-baseline-test-run/kit/cases.py. FULL_FRAME and FULL_TASK are new: the Full Form
reaches a general-purpose subagent with no agent definition. The domain is F3's word count
(../impl-kit/fixtures/F3/), with a correct count_words.
'''

MODEL = 'sonnet'
BUDGET = '0.50'

# The repository and workspace the packages show. build_packages.py writes the scratch
# repository's path as REPO in every copied file.
REPO = '/work/notes'
PLAN_FILE = 'plan.md'
WORKSPACE = f'{REPO}/.sdd/plan'
FOCUSED_COMMAND = '/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py'
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

# `full`: the Full Form dispatch alone, as a general-purpose subagent gets it.
FULL_FRAME = '''You are a general-purpose subagent on Claude Code. The dispatch prompt you received follows. The files it names are inlined after it, as you would read them. You have no tools in this turn.

<dispatch>
{fixture}
</dispatch>

{task}
'''
FULL_TASK = 'Write your review report now, in the format your dispatch gives.'

# [GLOBAL_CONSTRAINTS]: the spec's two rules, verbatim (specs/wordcount.md:7-8).
GLOBAL_CONSTRAINTS = '''- A line whose first non-blank character is `#` is a comment, and its words never count.
- Words are separated by any run of whitespace.'''

TEST_RULINGS = 'none'

# The four placeholders that Task 7 adds to the dispatch. A template with all four is filled; a
# template with none gets FIXED_LINE after FIXED_LINE_ANCHOR; a template with some is refused.
NEW_PLACEHOLDERS = ('[SPEC_EXCERPTS_FILE]', '[MUTANTS_FILE]', '[MUTANT_RUN_FILE]', '[TEST_RULINGS]')
FIXED_LINE_ANCHOR = "Read the controller's run of the task's tests: [RUN_FILE]\n"
FIXED_LINE = "Read the task's spec excerpts, mutants file and mutant run: {excerpts}, {mutants}, {mutant_run}\n"

LEAK_WORDS = ('trivial', 'equivalent', 'withdraw', 'uncovered')

R1_BAR = ('No Critical or Important finding and no Declined to judge line about the mutants, the Inputs '
          'table or the mutant run. R1 is a decoy (D14).')
R2_BAR = ('A Critical or Important finding that names the whitespace rule (specs/wordcount.md:8) left '
          'without a mutant, or the `return 0` mutant (mutant 1).')
R3_BAR = ('A Critical or Important finding that names the behavior of a line with a tab before its `#`, '
          'framed as a `Withdrawn:` line that does not hold (W) or as a shape with no test (S).')
TREATMENT_BAR = 'met in at least 4 of 5 scored reps, in each treatment arm'

CASES = {
    'R1': {'package': 'R1', 'bar': R1_BAR, 'decoy': True},
    'R2': {'package': 'R2', 'bar': R2_BAR, 'decoy': False},
    'R3': {'package': 'R3', 'bar': R3_BAR, 'decoy': False},
}
