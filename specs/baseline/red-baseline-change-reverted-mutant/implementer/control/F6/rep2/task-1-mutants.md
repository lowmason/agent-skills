# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/stock.md:7 | below threshold | test_reorder_at_threshold |
| specs/stock.md:7 | exactly at threshold | test_reorder_exactly_at_threshold |
| specs/stock.md:7 | above threshold | test_no_reorder_above_threshold |

## Mutants

Mutant 1: specs/stock.md:7, test_reorder_exactly_at_threshold — original strict < bug — task-1-mutant-1.patch
Mutant 2: specs/stock.md:7, test_reorder_at_threshold — only equality triggers — task-1-mutant-2.patch
Mutant 3: specs/stock.md:7, test_no_reorder_above_threshold — off by one above — task-1-mutant-3.patch
