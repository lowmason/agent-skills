# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/loyalty.md:9 | a purchase of exactly $100 | test_double_points_from_100_dollars |
| specs/loyalty.md:9 | a purchase above $100 | test_double_points_from_100_dollars |
| specs/loyalty.md:9 | a purchase of exactly $100 | test_double_points_at_exactly_100_dollars |
| specs/loyalty.md:9 | a purchase just below $100 | test_single_points_just_below_100_dollars |

## Mutants

Mutant 1: specs/loyalty.md:9, test_double_points_from_100_dollars — double points never apply — task-1-mutant-1.patch
Mutant 2: specs/loyalty.md:9, test_double_points_at_exactly_100_dollars — the threshold is exclusive (> instead of >=) — task-1-mutant-2.patch
Mutant 3: specs/loyalty.md:9, test_single_points_just_below_100_dollars — the threshold is one cent too low — task-1-mutant-3.patch
Strengthened: test_double_points_from_100_dollars — by test_double_points_at_exactly_100_dollars
Keeps: test_single_points_just_below_100_dollars — purchases under $100 earn single points, as before the task
