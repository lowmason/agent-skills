# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult well inside the full-price range | test_an_adult_pays_full_price |
| specs/tickets.md:7 | the lowest full-price age (12) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:7 | the highest full-price age (64) | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:9 | a child well under 12 | test_a_child_pays_half_price |
| specs/tickets.md:9 | the boundary just under 12 (11) | test_a_visitor_aged_11_pays_half_price |
| specs/tickets.md:9 | the boundary at 12 (not under) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:11 | the boundary at 65 | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | the boundary just under 65 (64) | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:11 | a senior well over 65 | test_a_senior_over_65_pays_half_price |
| brief: `price(age: int) -> int` in `tickets.py` | any age | every test |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_visitor_aged_12_pays_full_price, test_a_visitor_aged_64_pays_full_price — the full price is 30, not 20 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_visitor_aged_12_pays_full_price — a visitor aged 12 also pays half (<= instead of <) — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — a visitor aged 65 pays full (> instead of >=) — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price, test_a_senior_over_65_pays_half_price — the senior discount is missing — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:9, test_a_child_pays_half_price, test_a_visitor_aged_11_pays_half_price — the child discount is missing — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:11, test_a_senior_over_65_pays_half_price — only age exactly 65 gets the senior discount — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:9, test_a_visitor_aged_11_pays_half_price — the child limit is 11, so an 11-year-old pays full — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:11, test_a_visitor_aged_64_pays_full_price — the senior limit is 64, so a 64-year-old pays half — task-1-mutant-8.patch
