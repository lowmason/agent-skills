# Task 1 report

Implemented `main(argv)` in checkconf.py (prints `unknown key: <key>` per unknown key, returns 1/0). Blank lines are skipped.
Tests: plan test unchanged, plus 4 added (return 1, known keys -> 0 and no output, several unknown keys, empty file). 5/5 passing.

TDD
- RED: `pytest -q tests/test_checkconf.py` -> ImportError: cannot import name 'main' from 'checkconf' (expected, file empty).
- GREEN: same command -> 5 passed.

Mutants: /private/tmp/mt-rep-eIlXi4/repo/.sdd/plan/task-1-mutants-2.log — caught 5, survived 0, invalid 0

Files: checkconf.py, tests/test_checkconf.py (commit 20a49ce); mutant patches/mutants file in .sdd/plan (uncommitted).
Self-review: no plan/spec conflicts. Lines without `=` are treated as a key of the whole line (spec silent).
