# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | a short stay | test_a_short_stay_is_free |
| specs/parking.md:7 | exactly 30 minutes | test_a_stay_of_exactly_30_minutes_is_free |
| specs/parking.md:7 | zero minutes | test_a_zero_minute_stay_is_free |
| specs/parking.md:9 | 31 minutes, just over the limit | test_one_minute_over_the_free_limit_costs_one_hour |
| specs/parking.md:9 | exactly one hour | test_a_stay_of_exactly_one_hour_costs_one_hour |
| specs/parking.md:9 | one minute into a further hour | test_one_minute_into_a_second_hour_costs_two_hours |
| specs/parking.md:9 | a part-hour stay | test_each_started_hour_costs_2 |
| specs/parking.md:9 | exact whole hours | test_a_stay_of_exact_whole_hours_is_not_rounded_up |

## Mutants

Mutant 1: specs/parking.md:7, test_a_stay_of_exactly_30_minutes_is_free — 30 minutes is charged — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2 — a started hour is not charged (rounds down) — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_a_stay_of_exact_whole_hours_is_not_rounded_up — always adds an hour, even on exact hours — task-1-mutant-3.patch
Mutant 4: specs/parking.md:9, test_each_started_hour_costs_2 — rate is 3 per hour — task-1-mutant-4.patch
Mutant 5: specs/parking.md:7, test_one_minute_over_the_free_limit_costs_one_hour — free limit is 60 minutes — task-1-mutant-5.patch
