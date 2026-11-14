# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/stock.md:7 | level below threshold | test_reorder_at_threshold |
| specs/stock.md:7 | level equal to threshold | test_reorder_when_level_equals_threshold |
| specs/stock.md:7 | level above threshold | test_no_reorder_above_threshold |

## Mutants

Mutant 1: specs/stock.md:7, test_reorder_when_level_equals_threshold — strict `<` again — task-1-mutant-1.patch
Mutant 2: specs/stock.md:7, test_no_reorder_above_threshold — off by one above (`<= threshold + 1`) — task-1-mutant-2.patch
Mutant 3: specs/stock.md:7, test_no_reorder_above_threshold — always True — task-1-mutant-3.patch
Strengthened: test_reorder_at_threshold — by test_reorder_when_level_equals_threshold
Keeps: test_no_reorder_above_threshold — a level above the threshold still does not reorder, as before the task
