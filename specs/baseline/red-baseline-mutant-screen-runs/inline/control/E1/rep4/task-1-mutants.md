# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult, mid-range | test_an_adult_pays_full_price |
| specs/tickets.md:7 | an adult at the lower boundary (12) | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:7 | an adult at the upper boundary (64) | test_a_sixty_four_year_old_pays_full_price |
| specs/tickets.md:9 | a child, mid-range | test_a_child_pays_half_price |
| specs/tickets.md:9 | the youngest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | the boundary just under 12 (11) | test_an_eleven_year_old_pays_half_price |
| specs/tickets.md:9 | the boundary at 12, not under | test_a_twelve_year_old_pays_full_price |
| specs/tickets.md:11 | the boundary at 65 | test_a_sixty_five_year_old_pays_half_price |
| specs/tickets.md:11 | the boundary just under 65 (64) | test_a_sixty_four_year_old_pays_full_price |
| specs/tickets.md:11 | a senior well over 65 | test_an_older_senior_pays_half_price |
| brief: Produces `price(age: int) -> int` | an integer result | test_an_adult_pays_full_price |

## Mutants

Mutant 1: specs/tickets.md:9, test_a_twelve_year_old_pays_full_price — child test is `age <= 12` — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_an_eleven_year_old_pays_half_price — child test is `age < 11` — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:11, test_a_sixty_five_year_old_pays_half_price — senior test is `age > 65` — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_sixty_four_year_old_pays_full_price — senior test is `age >= 64` — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:11, test_an_older_senior_pays_half_price — no senior discount at all — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price — no child discount at all — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:7, test_an_adult_pays_full_price — full price is 24 — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, specs/tickets.md:11 — discounted visitors pay full price — task-1-mutant-8.patch
