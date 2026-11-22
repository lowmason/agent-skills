# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult between the bands | test_an_adult_pays_full_price |
| specs/tickets.md:7 | the first full-price age, 12 | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:7 | the last full-price age, 64 | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:9 | a child well under 12 | test_a_child_pays_half_price |
| specs/tickets.md:9 | the boundary, 11 | test_a_visitor_aged_11_pays_half_price |
| specs/tickets.md:9 | the lowest age, 0 | test_a_newborn_pays_half_price |
| specs/tickets.md:11 | the boundary, 65 | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | well over 65 | test_a_visitor_over_65_pays_half_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_visitor_aged_12_pays_full_price, test_a_visitor_aged_64_pays_full_price — the full price is 24 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_visitor_aged_12_pays_full_price — a 12-year-old counts as a child (`<=`) — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:9, test_a_visitor_aged_11_pays_half_price — the child limit is 11 — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — seniors start over 65 (`>`) — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_visitor_aged_64_pays_full_price — seniors start at 64 — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:11, test_a_visitor_over_65_pays_half_price, test_a_visitor_aged_65_pays_half_price — no senior discount — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price — no child discount — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, specs/tickets.md:11, test_a_child_pays_half_price — the discount is not applied (full price returned) — task-1-mutant-8.patch
