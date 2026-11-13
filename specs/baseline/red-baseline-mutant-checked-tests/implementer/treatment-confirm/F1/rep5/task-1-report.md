# Task 1 report

Implemented `latest_report(folder)` in `latest.py`: globs `*.txt` files directly in the folder, parses the `date:` line as an ISO date, returns the max by date (file names ignored).

## TDD
- RED: `pytest -q tests/test_latest.py` -> `ImportError: cannot import name 'latest_report' from 'latest'` (expected: function not yet written).
- GREEN: `pytest -q` -> 5 passed (later 6 passed after the extra directory test).

## Mutants
Run: /tmp/mt-rep-2CzCCs/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.
First run had 1 survivor (directories not filtered); added test_a_directory_named_like_a_report_is_skipped, rerun all caught.

## Files changed
latest.py, tests/test_latest.py, .sdd/plan/task-1-mutants.md and mutant patches.

## Self-review
Plan test left as written; extra tests are new. Files with no `date:` line raise ValueError (spec silent).
