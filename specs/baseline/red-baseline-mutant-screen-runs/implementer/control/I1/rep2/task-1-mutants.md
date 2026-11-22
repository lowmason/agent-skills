# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/parking.md:7 | well under 30 | test_a_short_stay_is_free |
| specs/parking.md:7 | zero | test_zero_minutes_is_free |
| specs/parking.md:7 | boundary 30 | test_exactly_30_minutes_is_free |
| specs/parking.md:9 | just over free limit | test_31_minutes_costs_one_started_hour |
| specs/parking.md:9 | exact hour multiple | test_exactly_one_hour_costs_one_hour |
| specs/parking.md:9 | one past an hour | test_one_minute_past_an_hour_starts_another |
| specs/parking.md:9 | partial hours | test_each_started_hour_costs_2 |

## Mutants

Mutant 1: specs/parking.md:7, test_exactly_30_minutes_is_free — 30 minutes is charged — task-1-mutant-1.patch
Mutant 2: specs/parking.md:9, test_each_started_hour_costs_2 — hours floored not rounded up — task-1-mutant-2.patch
Mutant 3: specs/parking.md:9, test_exactly_one_hour_costs_one_hour — hours+1 instead of ceiling — task-1-mutant-3.patch
Mutant 4: specs/parking.md:9, test_each_started_hour_costs_2 — rate 3 — task-1-mutant-4.patch
Mutant 5: specs/parking.md:7, test_31_minutes_costs_one_started_hour — free limit 60 — task-1-mutant-5.patch
