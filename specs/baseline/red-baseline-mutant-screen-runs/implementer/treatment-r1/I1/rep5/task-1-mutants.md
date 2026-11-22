# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | short stay | test_a_short_stay_is_free |
| specs/parking.md:7 | zero minutes | test_a_zero_minute_stay_is_free |
| specs/parking.md:7 | exactly 30 (boundary) | test_a_stay_of_exactly_30_minutes_is_free |
| specs/parking.md:9 | 31 (just over free) | test_one_minute_over_the_free_limit_costs_one_hour |
| specs/parking.md:9 | exact hour | test_a_full_hour_costs_one_hour |
| specs/parking.md:9 | one minute into next hour | test_one_minute_into_a_second_hour_costs_two_hours |
| specs/parking.md:9 | multi-hour partial | test_each_started_hour_costs_2 |

## Mutants

Mutant 1: specs/parking.md:7, test_a_stay_of_exactly_30_minutes_is_free — 30 minutes is charged — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2, test_one_minute_into_a_second_hour_costs_two_hours — hours rounded down — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_a_full_hour_costs_one_hour — hours always rounded up by one — task-1-mutant-3.patch
Mutant 4: specs/parking.md:9, test_each_started_hour_costs_2 — rate is 1 — task-1-mutant-4.patch
Mutant 5: specs/parking.md:7, test_a_stay_of_exactly_30_minutes_is_free — free limit is 20 — task-1-mutant-5.patch
