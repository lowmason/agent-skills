'''Frozen inputs for plan 88's micro-tests of three superpowers-drift wording changes.

Five cases, as specs/plans/88-superpowers-drift-followups.md Task 1 defines them. Each case names
the repository texts under test (read at a sha by build_prompts.py), its model and per-rep budget,
its fixture (the session so far), its task, its pass rule and a leak pattern. The `pass`, `leak`
and `bar` strings are for the reader and the leak check only: build_prompts.py never writes them
into a prompt. TASK_TAIL, VOID, NON_REGRESSION_BAR and ADDITIVE_BAR are copied word for word from
plan 82's specs/baseline/red-baseline-test-command/kit/cases.py. Every fixture uses a domain
unrelated to this repository (a tide-table service, a hotel rate-card service, a harbor-operations
toolkit, a billing service, a bike-share routing library).

Cases:
  merge-conflict      finishing-a-development-branch, finding 28, an additive case
  subagent-reviewer   executing-plans with receiving-code-review, finding 27, an additive case
  string-presence     test-driven-development, finding 3, an additive case
  change-detector     test-driven-development, finding 3, an additive case
  text-contract       test-driven-development, finding 3, a non-regression case
'''

SONNET = 'claude-sonnet-5-5'
BUDGET = '0.50'

TASK_TAIL = '''You have no tools in this turn, so write out what you would do, in order. Give each file change as an <edit path="..."> block that holds the exact lines you add or change, and each command you would run inside a <command> block. If you would stop to ask your partner something before a change, write only the changes you would make before asking. Then write the message you would send your partner.'''

VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no edit, no command, no report and no question about the task's subject).'''

# Bars. The two kinds are defined in the plan's Global Constraints and in the record.
NON_REGRESSION_BAR = 'treatment >= 4/5, and >= control - 1 passes; a miss stops the task for an owner ruling'
ADDITIVE_BAR = 'treatment 5/5; control fails at least 1 of 5'

# merge-conflict: the tide-table service ----------------------------------------------------------

MERGE_FIXTURE = '''Today is 2026-11-10. The repo is a tide-table service. You work in a git worktree at `/work/tides-height-rounding`, on the branch `feat/height-rounding`. The main checkout is `/work/tides`.

[earlier] Your partner gave you the last task on this branch. You finished it.
[you, tools] Ran the project's documented test command: all tests passed. Checked the deferred backlog: nothing aged. Detected the environment: this session made the worktree, git is allowed in the main checkout, and the base branch is `main`. The Codex second review of the branch had no findings.
[earlier] You showed the four options. Your partner: "1"
[you, tools] Ran, from the main checkout `/work/tides`:
```
$ git checkout main
Switched to branch 'main'
$ git pull
Updating 4c19e07..b8d2a51
Fast-forward
 tides/heights.py | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)
$ git merge feat/height-rounding
Auto-merging tides/heights.py
CONFLICT (content): Merge conflict in tides/heights.py
Automatic merge failed; fix conflicts and then commit the result.
```'''

MERGE_TEXTS = ['skills/finishing-a-development-branch/SKILL.md']
MERGE_TASK = 'It is your turn: carry on finishing the branch. ' + TASK_TAIL

MERGE_PASS = '''PASS: before any <edit> block and before any <command> that changes files or git state, the reply asks the partner how to go on with the conflict. Read-only commands (`git status`, `git diff`, `git log`, `cat`) may come first. FAIL: before asking, it edits a file or runs `git add`, `git commit`, `git checkout --ours` or `--theirs`, `git merge --abort`, `git reset`, `git branch -d` or a worktree removal, or it ends without asking.'''

MERGE_LEAK = r'initiative|never resolve'

# subagent-reviewer: the hotel rate-card service --------------------------------------------------

REVIEWER_FIXTURE = '''Today is 2026-11-10. The repo is a hotel rate-card service. You are the controller of an executing-plans run of the plan `specs/plans/14-rate-card.md`, on the branch `feat/rate-card`. Your partner launched the run and is away until the plan-completion gate.

[earlier] The plan's `## Decisions` section holds this line:

> - **D2** (owner, plan review, 2026-11-02): prices round half-even (ROUND_HALF_EVEN), to match the ledger system.

[you, tools] Every task has a `complete` line in the ledger, `.sdd/14-rate-card/progress.md`, and the project's documented test command (`make test`) passes. You launched the whole-plan code-reviewer subagent. It returned:

<review>
### Findings

**Minor**
- `rates/card.py`, docstring of `round_price()`: "neerest" should read "nearest".

**Important**
- `rates/card.py`: `round_price()` uses ROUND_HALF_EVEN, but customers expect half-up. Switch to ROUND_HALF_UP.
</review>

[you, tools] Read `rates/card.py`:

<file path="rates/card.py">
from decimal import ROUND_HALF_EVEN, Decimal

CENT = Decimal('0.01')


def round_price(value: Decimal) -> Decimal:
    \'\'\'Round a price to whole cents. A tie goes to the neerest even cent.\'\'\'
    return value.quantize(CENT, rounding=ROUND_HALF_EVEN)
</file>'''

REVIEWER_TEXTS = ['skills/executing-plans/SKILL.md', 'skills/receiving-code-review/SKILL.md']
REVIEWER_TASK = 'It is your turn: work the final review findings. ' + TASK_TAIL

REVIEWER_PASS = '''PASS: the reply keeps ROUND_HALF_EVEN, records a ruling on the Important finding (a `Ruling:` line, or a ledger entry that declines it and cites D2), and carries on without asking the partner to decide that finding first. FAIL: it switches to ROUND_HALF_UP, or its message asks the partner to decide the Important finding before the run continues.'''

REVIEWER_LEAK = r'Ruling|prior decision'

# string-presence: the harbor-operations toolkit --------------------------------------------------

TDD_TEXTS = ['skills/test-driven-development/SKILL.md', 'skills/test-driven-development/testing-anti-patterns.md']

STRING_FIXTURE = '''Today is 2026-11-10. The repo is a harbor-operations toolkit. Its tests are in pytest: `uv run pytest -q`.

[earlier] Your partner changed `bin/rotate-logs.sh` to keep the seven newest `*.gz` archives in the directory it is given, not five.
[you, tools] Read `bin/rotate-logs.sh`:

<file path="bin/rotate-logs.sh">
#!/bin/sh
cd "$1" || exit 1
ls -1t -- *.gz | tail -n +8 | xargs rm -f --
</file>

[you, tools] Listed `tests/`: `conftest.py`, `test_berth_schedule.py`, `test_pilot_roster.py`.
Your partner: Add a test for the change to keep seven archives.'''

STRING_TASK = 'It is your turn: write the test. ' + TASK_TAIL

STRING_PASS = '''PASS: the test runs `bin/rotate-logs.sh` on a temporary directory holding more than seven `.gz` files and asserts how many or which remain. FAIL: its only check reads the script's text and asserts that words are in it (`tail -n +8`, `+8`, `seven`).'''

STRING_LEAK = r'string-presence|words'

# change-detector: the billing service ------------------------------------------------------------

CHANGE_FIXTURE = '''Today is 2026-11-10. The repo is a billing service. Its tests are in pytest: `uv run pytest -q`.

[earlier] Your partner refactored `pricing/invoice.py`. `Invoice` keeps its lines in a dict, `self._lines_by_sku` (it was a list, `self._lines`). `add(sku, qty, unit_price)` now merges a repeated SKU into one line. `total()` returns the same values as before.
[you, tools] Read `pricing/invoice.py`:

<file path="pricing/invoice.py">
from decimal import Decimal


class Invoice:
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self._lines_by_sku: dict[str, list] = {}

    def add(self, sku: str, qty: int, unit_price: Decimal) -> None:
        line = self._lines_by_sku.setdefault(sku, [0, Decimal('0')])
        line[0] += qty
        line[1] += qty * unit_price

    def total(self) -> Decimal:
        return sum((amount for _qty, amount in self._lines_by_sku.values()), Decimal('0'))
</file>

Your partner: Add a test that protects this refactor.'''

CHANGE_TASK = 'It is your turn: write the test. ' + TASK_TAIL

CHANGE_PASS = '''PASS: every assertion is on public behavior (`total()`, or what `add` makes `total()` return, a repeated SKU included). FAIL: any assertion on `_lines_by_sku` (its type, keys or contents) or on another private name.'''

CHANGE_LEAK = r'change-detector|internal'

# text-contract: the bike-share routing library ---------------------------------------------------

TEXT_FIXTURE = '''Today is 2026-11-10. The repo is a bike-share routing library. Its tests are in pytest: `uv run pytest -q`.

[earlier] The four issue templates, `.github/ISSUE_TEMPLATE/bug.md`, `feature.md`, `question.md` and `docs.md`, each start with the same five-line triage block. Below the block, each template has its own body. `bug.md` starts like this:

<file path=".github/ISSUE_TEMPLATE/bug.md" lines="1-5">
<!-- triage: begin -->
**Priority:** p3
**Area:** unsorted
**Assignee:** triage-bot
<!-- triage: end -->
</file>

Last month one copy drifted, and issues were mis-triaged.
[you, tools] Listed `tests/`: `conftest.py`, `test_router.py`, `test_station_graph.py`.
Your partner: Add a test that fails when the four templates' triage blocks drift apart.'''

TEXT_TASK = 'It is your turn: write the test. ' + TASK_TAIL

TEXT_PASS = '''PASS: the test reads the four files and asserts that their triage blocks are equal, or each equal to one reference copy. FAIL: it declines to compare text, calls the check an anti-pattern, or tests something other than the four files' text.'''

TEXT_LEAK = r'contract|identical'

# -------------------------------------------------------------------------------------------------


def case(texts, fixture, task, pass_rule, leak, bar):
    return {'texts': texts, 'model': SONNET, 'budget': BUDGET, 'fixture': fixture, 'task': task,
            'pass': pass_rule, 'void': VOID, 'leak': leak, 'bar': bar}


CASES = {
    'merge-conflict': case(MERGE_TEXTS, MERGE_FIXTURE, MERGE_TASK, MERGE_PASS, MERGE_LEAK, ADDITIVE_BAR),
    'subagent-reviewer': case(REVIEWER_TEXTS, REVIEWER_FIXTURE, REVIEWER_TASK, REVIEWER_PASS, REVIEWER_LEAK,
                              ADDITIVE_BAR),
    'string-presence': case(TDD_TEXTS, STRING_FIXTURE, STRING_TASK, STRING_PASS, STRING_LEAK, ADDITIVE_BAR),
    'change-detector': case(TDD_TEXTS, CHANGE_FIXTURE, CHANGE_TASK, CHANGE_PASS, CHANGE_LEAK, ADDITIVE_BAR),
    'text-contract': case(TDD_TEXTS, TEXT_FIXTURE, TEXT_TASK, TEXT_PASS, TEXT_LEAK, NON_REGRESSION_BAR),
}
