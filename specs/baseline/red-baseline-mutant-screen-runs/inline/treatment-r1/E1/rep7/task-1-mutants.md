# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult, mid-range age | test_an_adult_pays_full_price |
| specs/tickets.md:7 | just above the child boundary (12) | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:7 | just below the senior boundary (64) | test_a_sixty_four_year_old_pays_full_price |
| specs/tickets.md:9 | a child, mid-range age | test_a_child_pays_half_price |
| specs/tickets.md:9 | the lowest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | at the boundary, last child age (11) | test_an_eleven_year_old_pays_half_price |
| specs/tickets.md:9 | at the boundary, first non-child age (12) | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:11 | at the boundary, first senior age (65) | test_a_sixty_five_year_old_pays_half_price |
| specs/tickets.md:11 | at the boundary, last non-senior age (64) | test_a_sixty_four_year_old_pays_full_price |
| specs/tickets.md:11 | well over the boundary (80) | test_an_older_senior_pays_half_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_child_pays_half_price — the full price is 24 instead of 20 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_twelve_year_old_pays_full_price — the child cutoff is 13, so a 12-year-old pays half — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:9, test_a_twelve_year_old_pays_full_price — the child test is `<=` instead of `<` — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:9, test_an_eleven_year_old_pays_half_price — the child cutoff is 11, so an 11-year-old pays full — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_sixty_five_year_old_pays_half_price — the senior test is `>` instead of `>=` — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:11, test_a_sixty_four_year_old_pays_full_price — the senior cutoff is 64 — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:11, test_an_older_senior_pays_half_price — seniors get no discount — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price — children get no discount — task-1-mutant-8.patch
Mutant 9: specs/tickets.md:11, test_an_older_senior_pays_half_price — the senior discount stops at 80 — task-1-mutant-9.patch
Mutant 10: specs/tickets.md:9, test_a_newborn_pays_half_price — age 0 is not treated as a child — task-1-mutant-10.patch
