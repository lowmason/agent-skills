# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult between the bands | test_an_adult_pays_full_price |
| specs/tickets.md:7 | just above the child band (12) | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:7 | just below the senior band (64) | test_a_sixty_four_year_old_pays_full_price |
| specs/tickets.md:9 | a child inside the band | test_a_child_pays_half_price |
| specs/tickets.md:9 | the lowest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | the top of the band (11) | test_an_eleven_year_old_pays_half_price |
| specs/tickets.md:9 | just outside the band (12) | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:11 | the boundary age (65) | test_a_sixty_five_year_old_pays_half_price |
| specs/tickets.md:11 | well over (90) | test_an_older_senior_pays_half_price |
| specs/tickets.md:11 | just below (64) | test_a_sixty_four_year_old_pays_full_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_child_pays_half_price — the full price is 18 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_twelve_year_old_pays_full_price — the child band ends at 13 — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:9, test_a_twelve_year_old_pays_full_price — age <= 12 counts as a child — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_sixty_five_year_old_pays_half_price — only over 65 pays half — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_sixty_four_year_old_pays_full_price — the senior band starts at 64 — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:11, test_a_sixty_five_year_old_pays_half_price, test_an_older_senior_pays_half_price — no senior discount — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price, test_an_eleven_year_old_pays_half_price — no child discount — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, specs/tickets.md:11, test_a_child_pays_half_price — the discount takes 5 off instead of halving — task-1-mutant-8.patch
