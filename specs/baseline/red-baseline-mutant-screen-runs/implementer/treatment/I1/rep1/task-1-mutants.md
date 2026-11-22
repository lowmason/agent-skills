# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | well under 30 | test_a_short_stay_is_free |
| specs/parking.md:7 | exactly 30 | test_exactly_30_minutes_is_free |
| specs/parking.md:9 | just over 30 | test_31_minutes_costs_one_started_hour |
| specs/parking.md:9 | whole hours | test_a_whole_hour_costs_one_hour |
| specs/parking.md:9 | partial hour | test_each_started_hour_costs_2, test_one_minute_into_the_next_hour_costs_another_hour |

## Mutants

Mutant 1: specs/parking.md:7, test_exactly_30_minutes_is_free — 30 minutes is no longer free — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_31_minutes_costs_one_started_hour — free up to 60 minutes — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_each_started_hour_costs_2 — started hours rounded down — task-1-mutant-3.patch
Mutant 4: specs/parking.md:9, test_a_whole_hour_costs_one_hour — a whole hour counts as an extra hour — task-1-mutant-4.patch
Mutant 5: specs/parking.md:9, test_each_started_hour_costs_2 — wrong rate of 3 per hour — task-1-mutant-5.patch
