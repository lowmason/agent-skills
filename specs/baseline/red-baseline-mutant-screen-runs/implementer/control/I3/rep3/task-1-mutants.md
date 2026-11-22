# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/loyalty.md:9 | a purchase of exactly $100 | test_exactly_100_dollars_earns_double_points |
| specs/loyalty.md:9 | a purchase just under $100 | test_just_under_100_dollars_earns_single_points |
| specs/loyalty.md:9 | a purchase above $100 | test_double_points_from_100_dollars |

## Mutants

Mutant 1: specs/loyalty.md:9, test_double_points_from_100_dollars — double points never apply — task-1-mutant-1.patch
Mutant 2: specs/loyalty.md:9, test_exactly_100_dollars_earns_double_points, test_double_points_from_100_dollars — boundary uses > instead of >= (the original bug) — task-1-mutant-2.patch
Mutant 3: specs/loyalty.md:9, test_just_under_100_dollars_earns_single_points — threshold is $99 — task-1-mutant-3.patch
Strengthened: test_double_points_from_100_dollars — by test_exactly_100_dollars_earns_double_points
Keeps: test_just_under_100_dollars_earns_single_points — below $100 earns one point per dollar, behavior from before the task that the fix keeps
