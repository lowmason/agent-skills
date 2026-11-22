# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult between the bands | test_an_adult_pays_full_price |
| specs/tickets.md:7 | lowest full-price age, 12 | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:7 | highest full-price age, 64 | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:9 | a typical child | test_a_child_pays_half_price |
| specs/tickets.md:9 | age 0, the start of the range | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | boundary below 12, age 11 | test_a_visitor_aged_11_pays_half_price |
| specs/tickets.md:9 | boundary at 12 (not under) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:11 | boundary at 65 ("aged 65") | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | well over 65 ("or over") | test_a_visitor_over_65_pays_half_price |
| specs/tickets.md:11 | boundary below 65, age 64 | test_a_visitor_aged_64_pays_full_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price — full price is 24, not 20 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_visitor_aged_12_pays_full_price — child test is `age <= 12` — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:9, test_a_visitor_aged_11_pays_half_price — child cutoff is 11 — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — senior test is `age > 65` — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_visitor_aged_64_pays_full_price — senior cutoff is 64 — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:11, test_a_visitor_over_65_pays_half_price — senior discount dropped — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:9, test_a_child_pays_half_price — child discount dropped — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, specs/tickets.md:11, test_a_child_pays_half_price — discount band charges full price — task-1-mutant-8.patch
Mutant 9: specs/tickets.md:9, test_a_newborn_pays_half_price — age 0 excluded from the child band (`0 < age < 12`) — task-1-mutant-9.patch
