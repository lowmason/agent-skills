# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult between the bands | test_an_adult_pays_full_price |
| specs/tickets.md:7 | the first full-price age (12) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:7 | the last full-price age (64) | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:9 | a typical child | test_a_child_pays_half_price |
| specs/tickets.md:9 | the lowest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | the boundary below 12 (11) | test_a_visitor_aged_11_pays_half_price |
| specs/tickets.md:9 | the boundary at 12 (not under) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:11 | the boundary at 65 ("aged 65") | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | well over 65 ("or over") | test_a_visitor_well_over_65_pays_half_price |
| specs/tickets.md:11 | the boundary below 65 (64) | test_a_visitor_aged_64_pays_full_price |

## Mutants

Mutant 1: specs/tickets.md:9, test_a_visitor_aged_12_pays_full_price — child band uses `<=` 12 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_visitor_aged_11_pays_half_price — child limit is 11 — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — senior band uses `>` 65 — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_visitor_aged_64_pays_full_price — senior limit is 64 — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price, test_a_visitor_well_over_65_pays_half_price — senior discount missing — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price, test_a_visitor_aged_11_pays_half_price — child discount missing — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:9, test_a_newborn_pays_half_price — age 0 excluded from the child band — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, specs/tickets.md:11, test_a_child_pays_half_price — discount not applied (half price returns full price) — task-1-mutant-8.patch
Mutant 9: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_visitor_aged_12_pays_full_price, test_a_visitor_aged_64_pays_full_price — everyone pays half price — task-1-mutant-9.patch
Mutant 10: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_child_pays_half_price — base price is 24 — task-1-mutant-10.patch
