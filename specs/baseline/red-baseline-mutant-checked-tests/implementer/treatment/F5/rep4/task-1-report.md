# Task 1 report
Implemented `parse_duration` in duration.py (regex fullmatch with [0-9], h/m/s in order, empty rejected). Tests in tests/test_duration.py: plan tests plus extra inputs (10h, 90s, 2m3s, 2h3s; rejects 1s1m, 1m1m, 1s1s, 1m1h, 1h2m3s4).
RED: pytest collection error before implementation (parse_duration missing). GREEN: 31 passed.
Mutants: /private/tmp/mt-rep-yqK65f/repo/.sdd/plan/task-1-mutants-2.log — caught 10, survived 0, invalid 0.
Files: duration.py, tests/test_duration.py, .sdd/plan/task-1-mutants.md and patches (uncommitted workspace files).
No plan/spec conflicts.
