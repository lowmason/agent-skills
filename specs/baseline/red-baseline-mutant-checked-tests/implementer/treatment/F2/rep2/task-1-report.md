# Task 1 report

Implemented `main` in checkconf.py (reads file, prints `unknown key: <key>` per key not in name/port/debug, returns 1 if any else 0). Tests in tests/test_checkconf.py: the plan test plus return-code, known-key/empty-file, multiple-unknown and first-line tests.

TDD: RED — `ImportError: cannot import name 'main' from 'checkconf'`. GREEN — `6 passed`.
Mutants: /private/tmp/mt-rep-IhC02p/repo/.sdd/plan/task-1-mutants.log — caught 6, survived 0, invalid 0.
Files: checkconf.py, tests/test_checkconf.py (committed); .sdd/plan mutant files (uncommitted).
Concerns: none. Blank lines are reported as `unknown key: ` (spec silent).
