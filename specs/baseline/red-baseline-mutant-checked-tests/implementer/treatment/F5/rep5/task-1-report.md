# Task 1 report

Implemented `parse_duration` in `duration.py` (regex `fullmatch` with `[0-9]`, empty string rejected, ValueError otherwise). Tests in `tests/test_duration.py` (plan tests verbatim, plus `('10h', 36000)`).

## TDD
- RED: `pytest -q tests/test_duration.py` -> `ImportError: cannot import name 'parse_duration' from 'duration'`.
- GREEN: 22 passed; after the added case, 23 passed.

## Mutants
Last run: /private/tmp/mt-rep-Tqijjw/repo/.sdd/plan/task-1-mutants-2.log — caught 8, survived 0, invalid 0.
First run: mutant 7 (hours limited to one digit) survived; fixed by adding `('10h', 36000)`.

## Files changed
duration.py, tests/test_duration.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md

## Self-review
No plan-test/spec conflicts. No concerns.
