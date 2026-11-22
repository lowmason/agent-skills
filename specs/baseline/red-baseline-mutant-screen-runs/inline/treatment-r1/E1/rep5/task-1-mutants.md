# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult between the bands | test_an_adult_pays_full_price |
| specs/tickets.md:9 | a typical child | test_a_child_pays_half_price |
| specs/tickets.md:9 | the lowest age, 0 | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | the last age under the boundary, 11 | test_a_visitor_aged_11_pays_half_price |
| specs/tickets.md:9 | the boundary itself, 12 (not under) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:11 | the last age before the boundary, 64 | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:11 | the boundary itself, 65 | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | a typical senior, over 65 | test_a_senior_pays_half_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_child_pays_half_price — the full price is 24, not 20 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_visitor_aged_12_pays_full_price — a visitor aged 12 counts as a child (<= instead of <) — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — only visitors over 65 pay half (> instead of >=) — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_senior_pays_half_price — seniors get no discount — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price — children get no discount — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:9, specs/tickets.md:11 — half price returns the full price — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:9, test_a_visitor_aged_11_pays_half_price — the child boundary is 11 — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:11, test_a_visitor_aged_64_pays_full_price — the senior boundary is 64 — task-1-mutant-8.patch
