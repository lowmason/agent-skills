# Task 1 report

## What I implemented

`count_words(text: str) -> int` in `wordcount.py`. It splits the text into lines at each newline, skips each line whose first non-blank character is `#`, and counts the words of every other line with `str.split()`. So any run of whitespace separates two words, and only a newline ends a line.

## What I tested

- `/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py`: 12 passed in 0.01s
- `/tmp/mt-venv/bin/python -m pytest -q`: 12 passed in 0.01s

The plan's test is unchanged. I added 11 tests in a second commit. Together they cover each input shape of the two rules that the plan's test does not use, and the Inputs table in the mutants file lists each shape and its test.

## TDD Evidence

- RED: `/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py`

  ```
      from wordcount import count_words
  E   ImportError: cannot import name 'count_words' from 'wordcount' (/work/notes/wordcount.py)
  =========================== short test summary info ============================
  ERROR tests/test_wordcount.py
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  1 error in 0.03s
  ```

  The failure was expected: `count_words` did not exist yet.

- GREEN: `/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py`

  ```
  .                                                                        [100%]
  1 passed in 0.00s
  ```

## Mutants

Run 1, `/work/notes/.sdd/plan/task-1-mutants.log`: caught 3, survived 1, invalid 0. Mutant 4 survived. It is equivalent, so I withdrew it: the mutants file has its `Withdrawn:` line, and its patch is renamed `task-1-mutant-4.patch.withdrawn`.

Run 2, `/work/notes/.sdd/plan/task-1-mutants-2.log`: caught 3, survived 0, invalid 0.

## Files changed

- wordcount.py
- tests/test_wordcount.py

## Self-review findings

None.

## Issues or concerns

None.
