# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/checkconf.md:7 | one unknown key among known | test_main_reports_an_unknown_key |
| specs/checkconf.md:7 | several unknown keys | test_main_reports_each_unknown_key |
| specs/checkconf.md:7 | all three known keys | test_main_returns_0_and_prints_nothing_for_known_keys |
| specs/checkconf.md:8 | unknown key returns 1 | test_main_returns_1_for_an_unknown_key |
| specs/checkconf.md:8 | no unknown key returns 0 | test_main_returns_0_and_prints_nothing_for_known_keys |
| specs/checkconf.md:8 | empty file returns 0 | test_main_returns_0_for_an_empty_file |

## Mutants

Mutant 1: specs/checkconf.md:7, test_main_returns_0_and_prints_nothing_for_known_keys — `debug` treated as unknown — task-1-mutant-1.patch
Mutant 2: specs/checkconf.md:8, test_main_returns_1_for_an_unknown_key — unknown key leaves status 0 — task-1-mutant-2.patch
Mutant 3: specs/checkconf.md:7, test_main_reports_each_unknown_key — only first unknown key is reported — task-1-mutant-3.patch
Mutant 4: specs/checkconf.md:7, test_main_reports_each_unknown_key — stops after first unknown key — task-1-mutant-4.patch
Mutant 5: specs/checkconf.md:8, test_main_returns_0_for_an_empty_file — status starts at 1 — task-1-mutant-5.patch
