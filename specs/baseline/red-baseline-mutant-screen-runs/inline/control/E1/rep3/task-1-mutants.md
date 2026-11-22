# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/tickets.md:7 | an adult, well inside the full-price range | test_an_adult_pays_full_price |
| specs/tickets.md:7 | full price at the child boundary (12) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:7 | full price at the senior boundary (64) | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:9 | a child well under 12 | test_a_child_pays_half_price |
| specs/tickets.md:9 | the lowest age (0) | test_a_newborn_pays_half_price |
| specs/tickets.md:9 | just under the boundary (11) | test_a_visitor_aged_11_pays_half_price |
| specs/tickets.md:9 | at the boundary, not under (12) | test_a_visitor_aged_12_pays_full_price |
| specs/tickets.md:11 | exactly 65 | test_a_visitor_aged_65_pays_half_price |
| specs/tickets.md:11 | just under 65 (64) | test_a_visitor_aged_64_pays_full_price |
| specs/tickets.md:11 | well over 65 | test_an_older_senior_pays_half_price |

## Mutants

Mutant 1: specs/tickets.md:7, test_an_adult_pays_full_price, test_a_child_pays_half_price — the ticket costs 24, not 20 — task-1-mutant-1.patch
Mutant 2: specs/tickets.md:9, test_a_visitor_aged_12_pays_full_price — a 12-year-old counts as a child (<= instead of <) — task-1-mutant-2.patch
Mutant 3: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — 65 itself pays full (> instead of >=) — task-1-mutant-3.patch
Mutant 4: specs/tickets.md:11, test_an_older_senior_pays_half_price, test_a_visitor_aged_65_pays_half_price — no senior discount at all — task-1-mutant-4.patch
Mutant 5: specs/tickets.md:9, test_a_child_pays_half_price, test_a_newborn_pays_half_price — no child discount at all — task-1-mutant-5.patch
Mutant 6: specs/tickets.md:9, test_a_visitor_aged_11_pays_half_price — the child limit is 11, so an 11-year-old pays full — task-1-mutant-6.patch
Mutant 7: specs/tickets.md:11, test_a_visitor_aged_65_pays_half_price — the senior limit is 66 — task-1-mutant-7.patch
Mutant 8: specs/tickets.md:9, specs/tickets.md:11, test_a_child_pays_half_price, test_an_older_senior_pays_half_price — the discount returns full price instead of half — task-1-mutant-8.patch
Mutant 9: specs/tickets.md:11, test_a_visitor_aged_64_pays_full_price — the senior limit is 64 — task-1-mutant-9.patch
