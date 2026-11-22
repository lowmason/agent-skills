# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult, well inside the full-price range | test_an_adult_pays_full_price |
| specs/tickets.md:7 | the first full-price age, just past the child boundary (12) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:7 | the last full-price age, just before the senior boundary (64) | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:9 | a typical child | test_a_child_pays_half_price |
| specs/tickets.md:9 | the lowest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | the boundary, last age under 12 (11) | test_a_visitor_aged_11_pays_half_price |
| specs/tickets.md:9 | the boundary, 12 is not under 12 | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:11 | the boundary, aged exactly 65 | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | the boundary, 64 is not 65 or over | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:11 | well over 65 (80) | test_a_senior_pays_half_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_visitor_aged_12_pays_full_price, test_a_visitor_aged_64_pays_full_price — the full price is 25, not 20 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_visitor_aged_12_pays_full_price — a 12-year-old counts as a child (`<=` for `<`) — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:9, test_a_visitor_aged_11_pays_half_price — the child limit is 11, so an 11-year-old pays full price — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — a 65-year-old is not a senior (`>` for `>=`) — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_visitor_aged_64_pays_full_price — the senior limit is 64 — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:11, test_a_senior_pays_half_price — seniors get no discount — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price — children get no discount — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, specs/tickets.md:11, test_a_child_pays_half_price, test_a_senior_pays_half_price — the half price is not halved — task-1-mutant-8.patch
