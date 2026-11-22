# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult, well inside the full-price range | test_an_adult_pays_full_price |
| specs/tickets.md:7 | the first full-price age (12) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:7 | the last full-price age (64) | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:9 | a child well under 12 | test_a_child_pays_half_price |
| specs/tickets.md:9 | the boundary just under 12 (11) | test_a_visitor_aged_11_pays_half_price |
| specs/tickets.md:9 | the boundary at 12 (not under) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:9 | the lowest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:11 | the boundary at 65 | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | the boundary just under 65 (64) | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:11 | a senior well over 65 | test_a_senior_over_65_pays_half_price |

## Mutants

Mutant 1: specs/tickets.md:9, test_a_visitor_aged_12_pays_full_price — a visitor aged 12 counts as a child (`<=`) — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_visitor_aged_11_pays_half_price — the child limit is 11, so 11 pays full — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — seniors start above 65 (`>`) — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_visitor_aged_64_pays_full_price — seniors start at 64 — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_senior_over_65_pays_half_price, test_a_visitor_aged_65_pays_half_price — no senior discount at all — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:7, test_an_adult_pays_full_price — the full price is 25 — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:9, test_a_child_pays_half_price — no child discount at all — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, test_a_newborn_pays_half_price — age 0 is excluded from the child discount — task-1-mutant-8.patch
