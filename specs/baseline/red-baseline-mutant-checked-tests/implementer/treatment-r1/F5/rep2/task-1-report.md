# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch on `[0-9]+` parts h/m/s, empty rejected) and tests/test_duration.py (plan tests verbatim).
RED: `pytest -q tests/test_duration.py` -> ImportError: cannot import name 'parse_duration'.
GREEN: 22 passed, output pristine.
Mutants: /private/tmp/mt-rep-Pn1SWg/repo/.sdd/plan/task-1-mutants.log — caught 7, survived 0, invalid 0.
Files: duration.py, tests/test_duration.py (committed 78f23c6); mutants file/patches in .sdd/plan.
Self-review: no spec/plan-test conflicts; no concerns.
