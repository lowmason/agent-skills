# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/checkconf.md:7 | one unknown key | test_main_reports_an_unknown_key |
| specs/checkconf.md:7 | several unknown keys, among known ones | test_main_reports_every_unknown_key_in_order |
| specs/checkconf.md:7 | each known key (name, port, debug) | test_main_returns_0_and_prints_nothing_for_known_keys |
| specs/checkconf.md:8 | unknown key | test_main_returns_1_for_an_unknown_key |
| specs/checkconf.md:8 | only known keys | test_main_returns_0_and_prints_nothing_for_known_keys |
| specs/checkconf.md:8 | empty file | test_main_returns_0_for_an_empty_file |

## Mutants

Mutant 1: specs/checkconf.md:7, test_main_returns_0_and_prints_nothing_for_known_keys — `debug` treated as unknown — task-1-mutant-1.patch
Mutant 2: specs/checkconf.md:8, test_main_returns_1_for_an_unknown_key — status stays 0 on unknown key — task-1-mutant-2.patch
Mutant 3: specs/checkconf.md:7, test_main_reports_every_unknown_key_in_order — returns at first unknown key — task-1-mutant-3.patch
Mutant 4: specs/checkconf.md:8, test_main_returns_0_for_an_empty_file — status starts at 1 — task-1-mutant-4.patch
Mutant 5: specs/checkconf.md:7, test_main_reports_an_unknown_key — keys starting with c are ignored — task-1-mutant-5.patch
