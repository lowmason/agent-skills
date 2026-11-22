# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | well inside the free period | test_a_short_stay_is_free |
| specs/parking.md:7 | zero minutes | test_zero_minutes_is_free |
| specs/parking.md:7 | exactly 30 minutes | test_exactly_30_minutes_is_free |
| specs/parking.md:9 | 31 minutes, just over | test_31_minutes_costs_one_started_hour |
| specs/parking.md:9 | exact hour multiple | test_exactly_one_hour_costs_2, test_exactly_two_hours_costs_4 |
| specs/parking.md:9 | one minute past an hour | test_one_minute_into_the_second_hour_costs_4 |
| specs/parking.md:9 | a partial hour | test_each_started_hour_costs_2 |

## Mutants

Mutant 1: specs/parking.md:7, test_exactly_30_minutes_is_free — 30 minutes is no longer free — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2 — started hours rounded down — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_exactly_one_hour_costs_2 — always adds an hour, so exact hours overcharge — task-1-mutant-3.patch
Mutant 4: specs/parking.md:9, test_each_started_hour_costs_2 — rate is 3 — task-1-mutant-4.patch
Mutant 5: specs/parking.md:7, test_31_minutes_costs_one_started_hour — free period is 60 minutes — task-1-mutant-5.patch
Mutant 6: specs/parking.md:7, test_31_minutes_costs_one_started_hour, test_a_short_stay_is_free — free period is 31 minutes — task-1-mutant-6.patch
Mutant 7: specs/parking.md:7, test_a_short_stay_is_free — only zero minutes is free — task-1-mutant-7.patch
