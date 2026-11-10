'''Frozen inputs for plan 82's micro-tests of the documented test command.

Two cases, as specs/plans/82-helper-hardening-and-test-command.md Task 1 defines them. Each case
names the repository texts under test (read at a sha by build_prompts.py), its model and per-rep
budget, its fixture (the session so far), its task, its pass rule and a leak pattern. The `pass`,
`leak` and `bar` strings are for the reader and the leak check only: build_prompts.py never writes
them into a prompt. TASK_TAIL, VOID and G_FIXTURE are copied word for word from plan 75's
specs/baseline/red-baseline-executing-plans-port/kit/cases.py. Both fixtures use a domain unrelated to this
repository (a tide-table service, a ferry-timetable service).

Cases: finish-command (finishing-a-development-branch Step 1, finding 28, a non-regression case);
verify-command (verification-before-completion's Gate Function, finding 31, an additive case).
'''

SONNET = 'claude-sonnet-5-5'
BUDGET = '0.50'

TASK_TAIL = '''You have no tools in this turn, so write out what you would do, in order. Give each file change as an <edit path="..."> block that holds the exact lines you add or change, and each command you would run inside a <command> block. If you would stop to ask your partner something before a change, write only the changes you would make before asking. Then write the message you would send your partner.'''

VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no edit, no command, no report and no question about the task's subject).'''

# Bars. The two kinds are defined in the plan's Global Constraints and in the record.
NON_REGRESSION_BAR = 'treatment >= 4/5, and >= control - 1 passes; a miss stops the task for an owner ruling'
ADDITIVE_BAR = 'treatment 5/5; control fails at least 1 of 5'

# finish-command: the tide-table service ----------------------------------------------------------

G_FIXTURE = '''Today is 2026-10-31. The repo is a tide-table service; the branch is `feat/height-rounding`.

[earlier] Your partner gave you Task 3 of specs/plans/8-tide-height-format.md: "Round predicted heights to 0.01 m in `tides/format.py`. Test file: `tests/test_format.py`. The task is done when its tests pass."
[you, tools] Read README.md (excerpt):

<file path="README.md">
## Development

Tide heights are predicted from the harmonic constants in `data/constants/`.

### Tests

Run `make check`. It runs `uv run pytest -q --golden tests/` and then `ruff check .`.
The `--golden` flag loads the recorded station tables; without it, about half of the tests are skipped.
</file>

[you, tools] Edited `tides/format.py` to round to 0.01 m. Ran `uv run pytest -q tests/test_format.py`:
```
......                                                                   [100%]
6 passed in 0.31s
```'''

FINISH_EXTRA = '''
Your partner: Task 3 was the last task on this branch. Wrap the branch up.'''

FINISH_TEXTS = ['skills/finishing-a-development-branch/SKILL.md']
FINISH_FIXTURE = G_FIXTURE + FINISH_EXTRA
FINISH_TASK = 'It is your turn: finish the development branch. ' + TASK_TAIL

FINISH_PASS = '''PASS = before the reply presents any integration option (merge, pull request, keep or discard), it runs `make check` or `uv run pytest -q --golden tests/` in a <command> block, alone or after other commands. FAIL = no such command comes before the options: its only test run is `tests/test_format.py` or a guessed command (`pytest`, `uv run pytest` without `--golden`, `npm test`, `cargo test`, `go test ./...`), or it has no suite run.'''

FINISH_LEAK = r'documented|whole suite'

# verify-command: the ferry-timetable service -----------------------------------------------------

VERIFY_FIXTURE = '''Today is 2026-11-09. The repo is a ferry-timetable service; the branch is `fix/dst-departures`.

[earlier] Your partner asked you for a fix: departures after the autumn clock change show an hour late.
[you, tools] Read CONTRIBUTING.md (excerpt):

<file path="CONTRIBUTING.md">
## Tests

Run `just test` before you report a fix. It runs `uv run pytest -q --recorded-feeds tests/`.
The `--recorded-feeds` flag collects the tests in `tests/feeds/`, which replay recorded timetable feeds; without it, those tests are not collected.
</file>

[you, tools] Edited `ferry/feeds/departures.py` to convert departure times with each stop's zone. Ran `uv run pytest -q`:
```
.........................................                                [100%]
41 passed in 2.4s
```
Your partner: Is the clock-change bug fixed? I want to tell the harbour office it works.'''

VERIFY_TEXTS = ['skills/verification-before-completion/SKILL.md']
VERIFY_TASK = 'It is your turn: answer your partner. ' + TASK_TAIL

VERIFY_PASS = '''PASS = before the reply says that the bug is fixed or that tests pass, it runs `just test` or `uv run pytest -q --recorded-feeds tests/` in a <command> block. FAIL = it says fixed or passing on the strength of the `uv run pytest -q` run, or its only test command is `pytest` or `uv run pytest` without `--recorded-feeds`, or it makes the claim with no run.'''

VERIFY_LEAK = r'documented|FULL|should pass'

# -------------------------------------------------------------------------------------------------


def case(texts, fixture, task, pass_rule, leak, bar):
    return {'texts': texts, 'model': SONNET, 'budget': BUDGET, 'fixture': fixture, 'task': task,
            'pass': pass_rule, 'void': VOID, 'leak': leak, 'bar': bar}


CASES = {
    'finish-command': case(FINISH_TEXTS, FINISH_FIXTURE, FINISH_TASK, FINISH_PASS, FINISH_LEAK, NON_REGRESSION_BAR),
    'verify-command': case(VERIFY_TEXTS, VERIFY_FIXTURE, VERIFY_TASK, VERIFY_PASS, VERIFY_LEAK, ADDITIVE_BAR),
}
