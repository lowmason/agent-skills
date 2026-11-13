# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/checkconf.md:7 | one unknown key among known | test_main_reports_an_unknown_key |
| specs/checkconf.md:7 | several unknown keys | test_main_reports_each_unknown_key |
| specs/checkconf.md:7 | unknown key on first line, no trailing newline | test_main_reports_an_unknown_key_on_the_first_line |
| specs/checkconf.md:7 | each of name, port, debug known | test_main_accepts_known_keys_and_empty_file |
| specs/checkconf.md:8 | unknown key returns 1 | test_main_returns_1_for_an_unknown_key |
| specs/checkconf.md:8 | no unknown key / empty file returns 0 | test_main_accepts_known_keys_and_empty_file |

## Mutants

Mutant 1: specs/checkconf.md:7, test_main_accepts_known_keys_and_empty_file — `debug` treated as unknown — task-1-mutant-1.patch
Mutant 2: specs/checkconf.md:8, test_main_returns_1_for_an_unknown_key — returns 0 with unknown key — task-1-mutant-2.patch
Mutant 3: specs/checkconf.md:7, test_main_reports_each_unknown_key — stops after first unknown key — task-1-mutant-3.patch
Mutant 4: specs/checkconf.md:7, test_main_reports_an_unknown_key — known/unknown inverted — task-1-mutant-4.patch
Mutant 5: specs/checkconf.md:7, test_main_reports_an_unknown_key_on_the_first_line — first line skipped — task-1-mutant-5.patch
Mutant 6: specs/checkconf.md:7, test_main_accepts_known_keys_and_empty_file — `port` treated as unknown — task-1-mutant-6.patch
