# Task 1 report

Implemented `count_words` in wordcount.py: splitlines, skip lines whose lstripped text starts with '#', sum len(line.split()).

TDD: RED `/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py` -> ImportError: cannot import name 'count_words'. GREEN: 6 passed (7 after the later added test).

Extra tests (spec shapes): indented comment, '#' after words, whitespace runs/CRLF, empty/blank, only comments, CR line breaks.

Mutants: run /private/tmp/mt-rep-EO36f0/repo/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0. (Mutant 4 initially survived; added test_comment_ends_at_any_line_break and re-ran.)

Files: wordcount.py, tests/test_wordcount.py, .sdd/plan/task-1-mutants.md and patches.
Concern: the bare-CR test pins that '\r' is a line break (str.splitlines also treats \x0b, \x0c,   etc. as breaks); the spec doesn't say.
