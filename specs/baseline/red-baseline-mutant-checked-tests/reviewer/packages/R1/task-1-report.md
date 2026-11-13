# Task 1 report

## What I implemented

`count_words(text: str) -> int` in `wordcount.py`. It splits the text into lines, skips each line whose first non-blank character is `#`, and counts the words of every other line with `str.split()`, so any run of whitespace separates two words.

## What I tested

- `/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py`: 8 passed in 0.00s
- `/tmp/mt-venv/bin/python -m pytest -q`: 8 passed in 0.00s

The plan's test is unchanged. I added 7 tests in a second commit, one for each input shape of the two rules that the plan's test does not use. The Inputs table in the mutants file lists each shape and its test.

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

`/work/notes/.sdd/plan/task-1-mutants.log`: caught 3, survived 0, invalid 0.

## Files changed

- wordcount.py
- tests/test_wordcount.py

## Self-review findings

None.

## Issues or concerns

None.
