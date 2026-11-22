# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | well under 30 | test_a_short_stay_is_free |
| specs/parking.md:7 | zero | test_a_zero_minute_stay_is_free |
| specs/parking.md:7 | exactly 30 | test_a_stay_of_exactly_30_minutes_is_free |
| specs/parking.md:9 | just over 30 | test_a_stay_just_over_30_minutes_costs_one_hour |
| specs/parking.md:9 | exact hour multiple | test_a_stay_of_exactly_one_hour_costs_one_hour |
| specs/parking.md:9 | one minute into next hour | test_a_minute_into_the_second_hour_starts_it |
| specs/parking.md:9 | several hours, partial | test_each_started_hour_costs_2 |

## Mutants

Mutant 1: specs/parking.md:7, test_a_stay_of_exactly_30_minutes_is_free — 30 minutes is charged — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2 — partial hours are not rounded up — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_a_stay_of_exactly_one_hour_costs_one_hour — an exact hour is charged an extra hour — task-1-mutant-3.patch
Mutant 4: specs/parking.md:7, test_a_stay_just_over_30_minutes_costs_one_hour — free period lasts up to 60 — task-1-mutant-4.patch
Mutant 5: specs/parking.md:9, test_each_started_hour_costs_2 — hourly price is 3 — task-1-mutant-5.patch
