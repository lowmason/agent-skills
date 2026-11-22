# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult age well inside the full-price range | test_an_adult_pays_full_price |
| specs/tickets.md:7 | the lower boundary of full price (12) | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:7 | the upper boundary of full price (64) | test_a_64_year_old_pays_full_price |
| specs/tickets.md:9 | a child age inside the range | test_a_child_pays_half_price |
| specs/tickets.md:9 | the smallest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | the boundary just under 12 (11) | test_an_eleven_year_old_pays_half_price |
| specs/tickets.md:11 | exactly 65 | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | over 65 | test_a_visitor_over_65_pays_half_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_twelve_year_old_pays_full_price, test_a_64_year_old_pays_full_price — the full price is 25, not 20 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_twelve_year_old_pays_full_price — a 12-year-old counts as a child (`<=` for `<`) — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:9, test_an_eleven_year_old_pays_half_price — the child limit is 11, so an 11-year-old pays full — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — a 65-year-old pays full (`>` for `>=`) — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_64_year_old_pays_full_price — the senior age is 60, so a 64-year-old pays half — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:11, test_a_visitor_over_65_pays_half_price, test_a_visitor_aged_65_pays_half_price — seniors get no discount — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price, test_an_eleven_year_old_pays_half_price — children get no discount — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, specs/tickets.md:11, test_a_child_pays_half_price, test_a_visitor_aged_65_pays_half_price — the discounted price is 15, not half — task-1-mutant-8.patch
Mutant 9: specs/tickets.md:9, test_a_newborn_pays_half_price — age 0 is not treated as under 12 — task-1-mutant-9.patch
