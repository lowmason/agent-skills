# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/window.md:8 | a day on the end date | test_window_holds_its_start_and_end_dates |
| specs/window.md:8 | a window of one day, whose start date is its end date | test_window_holds_its_start_and_end_dates |
| specs/window.md:8 | a window that runs across a year end, on its end date | test_window_holds_its_start_and_end_dates |
| specs/window.md:8 | the day after the end date | test_window_includes_end_date |

## Mutants

Mutant 1: specs/window.md:8, test_window_holds_its_start_and_end_dates — leaves out the end date (`start <= day < end`) — task-1-mutant-1.patch
Mutant 2: specs/window.md:8, test_window_includes_end_date — drops the end check, so a day after the end date is in the window (`start <= day`) — task-1-mutant-2.patch
