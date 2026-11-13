# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/checkconf.md:7 | one unknown key among known | test_main_reports_an_unknown_key |
| specs/checkconf.md:7 | several unknown keys | test_main_reports_each_unknown_key_in_order |
| specs/checkconf.md:7 | every known key (name, port, debug) | test_main_returns_0_and_prints_nothing_when_all_keys_are_known |
| specs/checkconf.md:8 | unknown key present | test_main_returns_1_when_a_key_is_unknown |
| specs/checkconf.md:8 | no unknown key / empty file | test_main_returns_0_for_an_empty_file |

## Mutants

Mutant 1: specs/checkconf.md:7, all_keys_are_known test — `debug` treated as unknown — task-1-mutant-1.patch
Mutant 2: specs/checkconf.md:8, returns_1 test — returns 0 despite unknown key — task-1-mutant-2.patch
Mutant 3: specs/checkconf.md:8, all_keys_are_known and empty tests — returns 1 when no unknown key — task-1-mutant-3.patch
Mutant 4: specs/checkconf.md:7, first test — prints the whole line, not the key — task-1-mutant-4.patch
Mutant 5: specs/checkconf.md:7, each_unknown_key test — stops after the first unknown key — task-1-mutant-5.patch
Mutant 6: specs/checkconf.md:7, first test — inverted membership check — task-1-mutant-6.patch
