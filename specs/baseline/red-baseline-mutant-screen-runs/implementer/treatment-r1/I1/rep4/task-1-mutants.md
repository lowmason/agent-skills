# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | well under the limit | test_a_short_stay_is_free |
| specs/parking.md:7 | exactly 30 minutes | test_thirty_minutes_is_still_free |
| specs/parking.md:9 | just over 30 minutes | test_just_over_thirty_minutes_costs_one_hour |
| specs/parking.md:9 | partial hour | test_each_started_hour_costs_2 |
| specs/parking.md:9 | exact whole hour | test_a_whole_hour_costs_one_hour |
| specs/parking.md:9 | one minute past a whole hour | test_one_minute_into_a_second_hour_costs_two_hours |

## Mutants

Mutant 1: specs/parking.md:7, test_thirty_minutes_is_still_free — 30 minutes is charged — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2 — hours rounded down — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_each_started_hour_costs_2 — rate 1 per hour — task-1-mutant-3.patch
Mutant 4: specs/parking.md:7, test_just_over_thirty_minutes_costs_one_hour — free period is 60 minutes — task-1-mutant-4.patch
Mutant 5: specs/parking.md:9, test_a_whole_hour_costs_one_hour, test_one_minute_into_a_second_hour_costs_two_hours — hours as floor+1 — task-1-mutant-5.patch
