# Task 1 report

Implemented `fee` in `parking.py` (free up to 30 min; else 2 per started hour) and plan tests in `tests/test_parking.py`.

## TDD
- RED: `pytest -q tests/test_parking.py` -> ModuleNotFoundError: No module named 'parking' (collection error), as expected.
- GREEN: 2 passed; after added boundary tests 8 passed, full suite 8 passed, output pristine.

## Commits
- Add the parking fee
- Test the fee at its boundaries (Mutant-step: task 1 input shape): 30, 0, 31, 60, 61, 120

Mutants: /private/tmp/msr104/rep3/repo/.sdd/plan/task-1-screen-2.log — caught 7, survived 0, invalid 0 (6 carried from screen 1, task-1-screen.log).
Revert: tests not loaded on the revert (parking missing), so every test fails on it.

Files: parking.py, tests/test_parking.py (+ .sdd/plan mutants files)
Concerns: none. No spec/plan-test conflict (fee(150)==6 matches the spec).
