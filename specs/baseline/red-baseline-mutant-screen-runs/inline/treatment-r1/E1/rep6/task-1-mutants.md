# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult, mid-range | test_an_adult_pays_full_price |
| specs/tickets.md:7 | lower full-price boundary (12) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:7 | upper full-price boundary (64) | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:9 | a child, mid-range | test_a_child_pays_half_price |
| specs/tickets.md:9 | the youngest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | boundary just under 12 (11) | test_a_visitor_aged_11_pays_half_price |
| specs/tickets.md:9 | boundary at 12 (not under) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:11 | boundary at 65 | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | boundary just under 65 (64) | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:11 | a senior, well over 65 | test_a_senior_pays_half_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_child_pays_half_price — full price is 25 instead of 20 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_visitor_aged_12_pays_full_price — child rule uses <= 12 — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — senior rule uses > 65 — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_senior_pays_half_price — senior discount dropped — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:9, test_a_child_pays_half_price, test_a_visitor_aged_11_pays_half_price — child discount dropped — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:9, test_a_visitor_aged_11_pays_half_price — child threshold 11 instead of 12 — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — senior threshold 66 instead of 65 — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:7, test_a_visitor_aged_12_pays_full_price — child threshold 13 instead of 12 — task-1-mutant-8.patch
Mutant 9: specs/tickets.md:7, test_a_visitor_aged_64_pays_full_price — senior threshold 64 instead of 65 — task-1-mutant-9.patch
Mutant 10: specs/tickets.md:9, test_a_newborn_pays_half_price — age 0 excluded from the child rule — task-1-mutant-10.patch
