# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/loyalty.md:9 | a purchase of exactly $100 | test_exactly_100_dollars_earns_double_points |
| specs/loyalty.md:9 | a purchase above $100 | test_double_points_from_100_dollars |
| specs/loyalty.md:9 | a purchase just under $100 | test_just_under_100_dollars_earns_single_points |

## Mutants

Mutant 1: specs/loyalty.md:9, test_double_points_from_100_dollars — the boundary is `>` so exactly $100 earns single points — task-1-mutant-1.patch
Mutant 2: specs/loyalty.md:9, test_just_under_100_dollars_earns_single_points — threshold lowered by a dollar so $99.99 earns double — task-1-mutant-2.patch
Strengthened: test_double_points_from_100_dollars — by test_exactly_100_dollars_earns_double_points
Keeps: test_just_under_100_dollars_earns_single_points — below $100 a purchase earns single points, as before the task
