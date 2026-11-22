# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | short stay | test_a_short_stay_is_free |
| specs/parking.md:7 | boundary 30 | test_exactly_30_minutes_is_free |
| specs/parking.md:9 | just over free limit | test_31_minutes_costs_one_started_hour |
| specs/parking.md:9 | whole hour | test_a_whole_hour_costs_one_hour |
| specs/parking.md:9 | partial hour | test_each_started_hour_costs_2 |
| specs/parking.md:9 | one minute over an hour | test_one_minute_over_an_hour_starts_a_second_hour |

## Mutants

Mutant 1: specs/parking.md:7, test_exactly_30_minutes_is_free — 30 minutes is charged — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2 — hours are floored, not rounded up — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_a_whole_hour_costs_one_hour — a whole hour is charged an extra hour — task-1-mutant-3.patch
Mutant 4: specs/parking.md:9, test_each_started_hour_costs_2 — wrong rate — task-1-mutant-4.patch
Mutant 5: specs/parking.md:7, test_31_minutes_costs_one_started_hour — free limit is 31 — task-1-mutant-5.patch
Mutant 6: specs/parking.md:7, test_a_short_stay_is_free — free limit is 10 minutes — task-1-mutant-6.patch
