# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/split.md:7 | a total that divides evenly | test_an_even_bill_splits_equally |
| specs/split.md:9 | one cent left over | test_the_first_person_pays_the_cent_left_over |
| specs/split.md:9 | several cents left over | test_several_cents_left_over_go_one_each_to_the_first_people |
| specs/split.md:7 | a total with cents left over, rounded down | test_the_first_person_pays_the_cent_left_over |

## Mutants

Mutant 1: specs/split.md:9, test_the_first_person_pays_the_cent_left_over — no one pays the cents left over — task-1-mutant-1.patch
Mutant 2: specs/split.md:9, test_the_first_person_pays_the_cent_left_over, test_several_cents_left_over_go_one_each_to_the_first_people — the first person pays every cent left over — task-1-mutant-2.patch
Mutant 3: specs/split.md:9, test_an_even_bill_splits_equally, test_the_first_person_pays_the_cent_left_over — one person too many pays a cent — task-1-mutant-3.patch
