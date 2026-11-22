# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | well under the limit | test_a_short_stay_is_free |
| specs/parking.md:7 | empty stay | test_a_zero_minute_stay_is_free |
| specs/parking.md:7 | exactly at the limit | test_a_stay_of_exactly_30_minutes_is_free |
| specs/parking.md:9 | just over the limit | test_a_stay_just_over_30_minutes_costs_one_hour |
| specs/parking.md:9 | partial hour | test_each_started_hour_costs_2 |
| specs/parking.md:9 | exact hour boundary | test_a_stay_of_exactly_one_hour_costs_one_hour |
| specs/parking.md:9 | one minute past an hour | test_one_minute_into_the_second_hour_costs_two_hours |

## Mutants

Mutant 1: specs/parking.md:7, test_a_stay_of_exactly_30_minutes_is_free — limit exclusive — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2 — floor instead of ceiling hours — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_a_stay_of_exactly_one_hour_costs_one_hour — floor+1 hours — task-1-mutant-3.patch
Mutant 4: specs/parking.md:9, test_each_started_hour_costs_2 — wrong price — task-1-mutant-4.patch
Mutant 5: specs/parking.md:7, test_a_short_stay_is_free, test_a_stay_just_over_30_minutes_costs_one_hour — free limit 60 — task-1-mutant-5.patch
