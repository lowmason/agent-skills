# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | short stay | test_a_short_stay_is_free |
| specs/parking.md:7 | at the 30 boundary | test_exactly_30_minutes_is_free |
| specs/parking.md:7 | zero | test_zero_minutes_is_free |
| specs/parking.md:9 | just over 30 | test_one_minute_over_30_costs_one_hour |
| specs/parking.md:9 | whole hours | test_a_whole_hour_costs_one_hour |
| specs/parking.md:9 | partial hour after full | test_each_started_hour_costs_2, test_one_minute_into_the_second_hour_costs_two_hours |

## Mutants

Mutant 1: specs/parking.md:7, test_exactly_30_minutes_is_free — 30 minutes is charged — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2 — started hours rounded down — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_a_whole_hour_costs_one_hour — an extra hour is always charged — task-1-mutant-3.patch
Mutant 4: specs/parking.md:7, test_one_minute_over_30_costs_one_hour — free limit too low — task-1-mutant-4.patch
Mutant 5: specs/parking.md:9, test_each_started_hour_costs_2 — wrong rate — task-1-mutant-5.patch
