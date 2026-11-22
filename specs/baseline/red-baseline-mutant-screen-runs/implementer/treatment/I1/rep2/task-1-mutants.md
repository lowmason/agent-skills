# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | short stay | test_a_short_stay_is_free |
| specs/parking.md:7 | zero | test_zero_minutes_is_free |
| specs/parking.md:7 | boundary 30 | test_exactly_30_minutes_is_free |
| specs/parking.md:9 | just over 30 | test_one_minute_over_free_limit_costs_one_hour |
| specs/parking.md:9 | exact hour | test_exactly_one_hour_costs_2 |
| specs/parking.md:9 | just over an hour | test_one_minute_into_second_hour_costs_4 |
| specs/parking.md:9 | several hours, partial | test_each_started_hour_costs_2 |
| specs/parking.md:9 | several whole hours | test_exactly_whole_hours_are_not_rounded_up |

## Mutants

Mutant 1: specs/parking.md:7, test_exactly_30_minutes_is_free — 30 minutes is charged — task-1-mutant-1.patch
Mutant 2: specs/parking.md:7,9, test_one_minute_over_free_limit_costs_one_hour — free up to 60 minutes — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_each_started_hour_costs_2 — hours rounded down — task-1-mutant-3.patch
Mutant 4: specs/parking.md:9, test_exactly_one_hour_costs_2 — always adds an hour — task-1-mutant-4.patch
Mutant 5: specs/parking.md:9, test_each_started_hour_costs_2 — wrong rate — task-1-mutant-5.patch
Mutant 6: specs/parking.md:9, test_one_minute_into_second_hour_costs_4 — hours counted after the free 30 minutes — task-1-mutant-6.patch
