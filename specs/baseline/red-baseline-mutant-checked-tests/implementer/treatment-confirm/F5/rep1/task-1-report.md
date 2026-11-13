# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch on ASCII digits, empty rejected) and plan tests in tests/test_duration.py, unchanged.
RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration' (collection error).
GREEN: 22 passed, output pristine.
Mutants: .sdd/plan/task-1-mutants-2.log — caught 7, survived 0, invalid 0 (list in task-1-mutants.md).
Files: duration.py, tests/test_duration.py (committed a57be3a); mutant patches/mutants file under .sdd/plan.
No concerns; no plan-test/spec conflict.
