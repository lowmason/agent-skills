# Task 1 report
Implemented `latest_report` in latest.py: picks the *.txt file in the folder with the max ISO `date:` line (parsed as a date; file names ignored). Test added in tests/test_latest.py.
RED: ImportError for latest_report before implementation. GREEN: 1 passed.
Concerns: a report with no date: line raises ValueError; an empty folder raises ValueError (from max). Spec doesn't define either.
