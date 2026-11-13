# Task 1 report
Implemented `parse_duration` in duration.py (ASCII regex fullmatch, empty rejected, returns int seconds); tests/test_duration.py as given in the plan.
TDD: RED = ImportError for parse_duration at collection; GREEN = `pytest -q tests/test_duration.py` -> 22 passed.
Mutants: .sdd/plan/task-1-mutants-2.log — caught 5, survived 0, invalid 0 (first run: 2 survivors were equivalent mutants, rewritten).
Files: duration.py, tests/test_duration.py (committed); mutant files under .sdd/plan.
Self-review: no concerns; no plan-test/spec conflicts.
