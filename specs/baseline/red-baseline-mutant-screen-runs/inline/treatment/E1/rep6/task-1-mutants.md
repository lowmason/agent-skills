# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult, full price | test_an_adult_pays_full_price |
| specs/tickets.md:7 | just past the child boundary (12) | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:7 | just under the senior boundary (64) | test_a_sixty_four_year_old_pays_full_price |
| specs/tickets.md:9 | a typical child | test_a_child_pays_half_price |
| specs/tickets.md:9 | the lowest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | at the boundary, under 12 (11) | test_an_eleven_year_old_pays_half_price |
| specs/tickets.md:9 | at the boundary, not under 12 (12) | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:11 | aged exactly 65 | test_a_sixty_five_year_old_pays_half_price |
| specs/tickets.md:11 | over 65 (80) | test_a_visitor_over_sixty_five_pays_half_price |
| specs/tickets.md:11 | just under 65 (64) | test_a_sixty_four_year_old_pays_full_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_twelve_year_old_pays_full_price, test_a_sixty_four_year_old_pays_full_price — the ticket costs 25, not 20 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_twelve_year_old_pays_full_price — a 12-year-old counts as a child (`<=` for `<`) — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:9, test_an_eleven_year_old_pays_half_price — the child limit is 11, so an 11-year-old pays full — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_sixty_five_year_old_pays_half_price — a 65-year-old pays full (`>` for `>=`) — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_sixty_four_year_old_pays_full_price — the senior limit is 64, so a 64-year-old pays half — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:11, test_a_visitor_over_sixty_five_pays_half_price, test_a_sixty_five_year_old_pays_half_price — no senior discount at all — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price — no child discount at all — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, specs/tickets.md:11, test_a_child_pays_half_price — the discount is a quarter of the price, not half — task-1-mutant-8.patch
