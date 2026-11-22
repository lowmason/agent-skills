# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | well under the limit | test_a_short_stay_is_free |
| specs/parking.md:7 | exactly at 30 | test_exactly_30_minutes_is_free |
| specs/parking.md:7 | zero minutes | test_a_zero_minute_stay_is_free |
| specs/parking.md:9 | just over 30 | test_31_minutes_costs_one_hour |
| specs/parking.md:9 | exact hour boundary | test_exactly_one_hour_costs_2 |
| specs/parking.md:9 | one minute into next hour | test_one_minute_into_the_second_hour_costs_4 |
| specs/parking.md:9 | partial hour in a multi-hour stay | test_each_started_hour_costs_2 |

## Mutants

Mutant 1: specs/parking.md:7, test_exactly_30_minutes_is_free — 30 minutes is charged (< instead of <=) — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2 — started hours floored instead of rounded up — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_each_started_hour_costs_2 — price 3 per hour — task-1-mutant-3.patch
Mutant 4: specs/parking.md:9, test_exactly_one_hour_costs_2 — floor plus one, so exact hours overcharged — task-1-mutant-4.patch
Mutant 5: specs/parking.md:7, test_a_short_stay_is_free — free stay costs 2 — task-1-mutant-5.patch
