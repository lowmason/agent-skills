# Task 1 report

Implemented `main` in checkconf.py (prints `unknown key: <key>` per unknown key, returns 1/0; skips blank lines).
Tests: plan test plus 10 added shape tests in tests/test_checkconf.py; 11 pass.

TDD: RED — `pytest -q tests/test_checkconf.py` gave ImportError: cannot import name 'main'. GREEN — all pass.

Mutants: /private/tmp/mt-rep-209lhZ/repo/.sdd/plan/task-1-mutants-2.log — caught 8, survived 0, invalid 0.
First run had 3 survivors: mutant 1 was a stale .pyc (same-size edit within one mtime second; rerun with PYTHONDONTWRITEBYTECODE=1), mutants 5 and 8 exposed missing shapes (`key=value` without spaces, prefix of a known key); tests added.

Commits: "Add checkconf.main", "Strengthen checkconf tests".
Files: checkconf.py, tests/test_checkconf.py.
Concerns: none. No plan/spec conflict.
