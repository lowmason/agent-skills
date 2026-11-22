# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | well under 30 | test_a_short_stay_is_free |
| specs/parking.md:7 | zero | test_zero_minutes_is_free |
| specs/parking.md:7 | exactly 30 (boundary) | test_thirty_minutes_is_still_free |
| specs/parking.md:9 | 31 (just over) | test_just_over_free_period_costs_one_hour |
| specs/parking.md:9 | part hour | test_each_started_hour_costs_2 |
| specs/parking.md:9 | exact hour | test_exactly_one_hour_costs_2 |
| specs/parking.md:9 | one minute into next hour | test_one_minute_into_second_hour_costs_4 |

## Mutants

Mutant 1: specs/parking.md:7, test_thirty_minutes_is_still_free — 30 minutes is charged — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2 — hours rounded down — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_each_started_hour_costs_2 — wrong rate — task-1-mutant-3.patch
Mutant 4: specs/parking.md:7, test_a_short_stay_is_free — only zero is free — task-1-mutant-4.patch
Mutant 5: specs/parking.md:9, test_exactly_one_hour_costs_2 — exact hours charged an extra hour — task-1-mutant-5.patch
