# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/stock.md:7 | level below threshold | test_reorder_at_threshold |
| specs/stock.md:7 | level equal to threshold | test_reorder_when_level_equals_threshold |
| specs/stock.md:7 | level above threshold | test_no_reorder_above_threshold |

## Mutants

Mutant 1: specs/stock.md:7, test_reorder_when_level_equals_threshold — strict comparison (original bug) — task-1-mutant-1.patch
Mutant 2: specs/stock.md:7, test_reorder_when_level_equals_threshold — threshold off by one — task-1-mutant-2.patch
Mutant 3: specs/stock.md:7, test_reorder_at_threshold, test_no_reorder_above_threshold — comparison inverted — task-1-mutant-3.patch
Mutant 4: specs/stock.md:7, test_no_reorder_above_threshold — always True — task-1-mutant-4.patch
