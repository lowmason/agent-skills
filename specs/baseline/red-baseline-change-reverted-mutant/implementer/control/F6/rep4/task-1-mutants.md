# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/stock.md:7 | level below threshold | test_reorder_at_threshold |
| specs/stock.md:7 | level equal to threshold | test_reorder_when_level_equals_threshold |
| specs/stock.md:7 | level above threshold | test_no_reorder_above_threshold |
| specs/stock.md:7 | zero boundary | test_reorder_at_zero_threshold_boundary |

## Mutants

Mutant 1: specs/stock.md:7, test_reorder_when_level_equals_threshold — original strict `<` — task-1-mutant-1.patch
Mutant 2: specs/stock.md:7, test_reorder_at_threshold — only equality reorders — task-1-mutant-2.patch
Mutant 3: specs/stock.md:7, test_no_reorder_above_threshold — off by one high — task-1-mutant-3.patch
Mutant 4: specs/stock.md:7, test_no_reorder_above_threshold, test_reorder_at_zero_threshold_boundary — always True — task-1-mutant-4.patch
