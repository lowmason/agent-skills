# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | a typical adult | test_an_adult_pays_full_price |
| specs/tickets.md:7 | the first full-price age, 12 | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:7 | the last full-price age, 64 | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:9 | a typical child | test_a_child_pays_half_price |
| specs/tickets.md:9 | the lowest age, 0 | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | the boundary just under 12, 11 | test_a_visitor_aged_11_pays_half_price |
| specs/tickets.md:9 | the boundary 12 itself (not under) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:11 | the boundary 65 itself ("or over") | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | the age just below, 64 | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:11 | well over 65 | test_a_senior_well_over_65_pays_half_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_child_pays_half_price — the full price is 24, not 20 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, specs/tickets.md:11, test_a_child_pays_half_price, test_a_newborn_pays_half_price, test_a_senior_well_over_65_pays_half_price — the discount returns the full price instead of half — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:9, test_a_visitor_aged_12_pays_full_price — the child test uses <= 12, so a 12-year-old pays half — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:9, test_a_visitor_aged_11_pays_half_price — the child limit is 11, so an 11-year-old pays full — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — the senior test uses > 65, so a 65-year-old pays full — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:11, test_a_visitor_aged_64_pays_full_price — the senior limit is 64, so a 64-year-old pays half — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:11, test_a_senior_well_over_65_pays_half_price, test_a_visitor_aged_65_pays_half_price — the senior discount is missing — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price, test_a_visitor_aged_11_pays_half_price — the child discount is missing — task-1-mutant-8.patch
Mutant 9: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — the senior discount starts at over 70 — task-1-mutant-9.patch
Mutant 10: specs/tickets.md:9, test_a_newborn_pays_half_price — age 0 is excluded from the child discount — task-1-mutant-10.patch
