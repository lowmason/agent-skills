# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/checkconf.md:7 | one unknown key | test_main_reports_an_unknown_key |
| specs/checkconf.md:7 | several unknown keys | test_main_reports_each_unknown_key |
| specs/checkconf.md:7 | all of name, port, debug known | test_main_returns_0_and_prints_nothing_for_known_keys |
| specs/checkconf.md:8 | unknown key present | test_main_returns_1_for_an_unknown_key |
| specs/checkconf.md:8 | no unknown key | test_main_returns_0_and_prints_nothing_for_known_keys |
| specs/checkconf.md:8 | empty file | test_main_accepts_an_empty_file |

## Mutants

Mutant 1: specs/checkconf.md:7, test_main_returns_0_and_prints_nothing_for_known_keys — `debug` is treated as unknown — task-1-mutant-1.patch
Mutant 2: specs/checkconf.md:8, test_main_returns_1_for_an_unknown_key — always returns 0 — task-1-mutant-2.patch
Mutant 3: specs/checkconf.md:7, test_main_reports_each_unknown_key — stops after the first unknown key — task-1-mutant-3.patch
Mutant 4: specs/checkconf.md:8, test_main_returns_0_and_prints_nothing_for_known_keys, test_main_accepts_an_empty_file — always returns 1 — task-1-mutant-4.patch
Mutant 5: specs/checkconf.md:7, test_main_reports_an_unknown_key — `colour` is accepted as known — task-1-mutant-5.patch
