# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/checkconf.md:7 | one unknown key | test_main_reports_an_unknown_key |
| specs/checkconf.md:7 | every known key | test_main_accepts_every_known_key |
| specs/checkconf.md:7 | several unknown keys | test_main_reports_each_unknown_key |
| specs/checkconf.md:8 | unknown key returns 1 | test_main_returns_1_for_an_unknown_key |
| specs/checkconf.md:8 | no unknown key / empty file returns 0 | test_main_accepts_every_known_key, test_main_returns_0_for_an_empty_file |

## Mutants

Mutant 1: specs/checkconf.md:7, test_main_accepts_every_known_key — `debug` treated as unknown — task-1-mutant-1.patch
Mutant 2: specs/checkconf.md:8, test_main_returns_1_for_an_unknown_key — unknown key leaves status 0 — task-1-mutant-2.patch
Mutant 3: specs/checkconf.md:7, test_main_reports_an_unknown_key — `colour` accepted as known — task-1-mutant-3.patch
Mutant 4: specs/checkconf.md:7, test_main_reports_each_unknown_key — stops after first unknown key — task-1-mutant-4.patch
