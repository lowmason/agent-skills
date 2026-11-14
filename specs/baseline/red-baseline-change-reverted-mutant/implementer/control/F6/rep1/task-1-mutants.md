# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/stock.md:7 | level below threshold | test_reorder_at_threshold |
| specs/stock.md:7 | level equals threshold | test_reorder_when_level_equals_threshold |
| specs/stock.md:7 | level above threshold | test_no_reorder_above_threshold |
| specs/stock.md:7 | zero boundary | test_reorder_at_zero_threshold |
| specs/stock.md:7 | one below threshold | test_reorder_one_below_threshold |

## Mutants

Mutant 1: specs/stock.md:7, test_reorder_when_level_equals_threshold, test_reorder_at_zero_threshold — strict < (original bug) — task-1-mutant-1.patch
Mutant 2: specs/stock.md:7, test_no_reorder_above_threshold — off by one, <= threshold + 1 — task-1-mutant-2.patch
Mutant 3: specs/stock.md:7, test_reorder_one_below_threshold — level one below threshold not reordered — task-1-mutant-3.patch
