# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult, mid-range | test_an_adult_pays_full_price |
| specs/tickets.md:7 | first full-price age (12) | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:7 | last full-price age (64) | test_a_sixty_four_year_old_pays_full_price |
| specs/tickets.md:9 | a child, mid-range | test_a_child_pays_half_price |
| specs/tickets.md:9 | lowest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | boundary below 12 (11) | test_an_eleven_year_old_pays_half_price |
| specs/tickets.md:9 | boundary at 12 (not under) | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:11 | boundary at 65 | test_a_sixty_five_year_old_pays_half_price |
| specs/tickets.md:11 | boundary below 65 (64) | test_a_sixty_four_year_old_pays_full_price |
| specs/tickets.md:11 | a senior well over 65 | test_a_senior_pays_half_price |
| brief: `price(age: int) -> int` | integer result for half price | test_a_child_pays_half_price |

## Mutants

Mutant 1: specs/tickets.md:9, test_a_twelve_year_old_pays_full_price — a 12-year-old counts as under 12 (`<=`) — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_an_eleven_year_old_pays_half_price — the child limit is 11 instead of 12 — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:11, test_a_sixty_five_year_old_pays_half_price — a 65-year-old is not a senior (`>`) — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_sixty_four_year_old_pays_full_price — the senior limit is 64 instead of 65 — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_a_senior_pays_half_price, test_a_sixty_five_year_old_pays_half_price — seniors get no discount — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price, test_an_eleven_year_old_pays_half_price — children get no discount — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_twelve_year_old_pays_full_price, test_a_sixty_four_year_old_pays_full_price — the full price is 25 — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, test_a_newborn_pays_half_price — age 0 is excluded from the child discount — task-1-mutant-8.patch
Mutant 9: specs/tickets.md:9, specs/tickets.md:11, brief: `price(age: int) -> int`, test_a_child_pays_half_price — the discounted branch returns full price — task-1-mutant-9.patch
