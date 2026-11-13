# Task 1 report

Implemented `latest_report` in `latest.py` (max over `folder.glob('*.txt')` keyed by the parsed `date:` line). Added `tests/test_latest.py`: the plan test plus three tests (names carry no order, date line after other lines / year boundary, only direct .txt files).

## TDD
- RED: `pytest -q tests/test_latest.py` -> ImportError: cannot import name 'latest_report' from 'latest'.
- GREEN: `pytest -q` -> 4 passed.

## Mutants
Run: /private/tmp/mt-rep-6BOgJv/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.

## Files changed
latest.py, tests/test_latest.py (committed); .sdd/plan mutant files (uncommitted).

## Concerns
No plan/spec conflict. Unspecified: a report with no `date:` line raises ValueError; an empty folder raises ValueError (from max).
