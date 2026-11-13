# Task 1 report
Implemented `main` in checkconf.py (reads argv[0], prints `unknown key: <key>` per key outside name/port/debug, returns 1 if any else 0). Tests in tests/test_checkconf.py: plan test unchanged plus 4 new (return 1, known keys, several unknown, empty file).
TDD: RED = ImportError for `main` (collection error); GREEN = 5 passed.
Mutants: /tmp/mt-rep-DgAxaR/repo/.sdd/plan/task-1-mutants.log — caught 4, survived 0, invalid 0.
Files: checkconf.py, tests/test_checkconf.py (+ .sdd/plan mutant files).
Concerns: none. Blank lines are not covered by the spec and are reported as unknown key ''.
