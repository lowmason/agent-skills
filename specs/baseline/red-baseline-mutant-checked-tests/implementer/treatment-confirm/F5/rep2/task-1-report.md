# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch on `(?:([0-9]+)h)?(?:([0-9]+)m)?(?:([0-9]+)s)?`, empty rejected). Tests: plan tests verbatim plus 3 added tests (multi-digit, wrong order/repeats, uppercase units).
TDD: RED = ImportError for parse_duration at collection; GREEN = 34 passed, later 38 passed full suite.
Mutants: .sdd/plan/task-1-mutants-2.log — caught 9, survived 0, invalid 0 (first run: mutant 8, uppercase S, survived; fixed by new test).
Files: duration.py, tests/test_duration.py, .sdd/plan/task-1-mutant-*.patch, task-1-mutants.md.
Commits: "Add parse_duration", "Test uppercase units are rejected".
Concerns: none; no plan test conflicts with the spec. Plan said 22 passed; plan tests alone give 22 (9+13), extras add 16.
