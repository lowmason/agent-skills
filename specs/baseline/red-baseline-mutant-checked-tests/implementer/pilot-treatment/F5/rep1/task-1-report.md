# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch with ASCII [0-9], empty rejected) and tests/test_duration.py as given by the plan.
TDD: RED: `pytest -q tests/test_duration.py` -> ImportError cannot import name 'parse_duration' (collection error, expected: function absent). GREEN: 22 passed.
Mutants: /private/tmp/mt-rep-GPQCFu/repo/.sdd/plan/task-1-mutants-2.log — caught 8, survived 0, invalid 0. (First run: mutant 1 patch did not apply, mutant 4 was equivalent — `$` with fullmatch; both redone.)
Files: duration.py, tests/test_duration.py (committed); .sdd/plan mutant files (uncommitted).
Concerns: none; no plan-test/spec conflict.
