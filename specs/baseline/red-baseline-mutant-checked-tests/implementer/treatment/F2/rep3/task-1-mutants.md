# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/checkconf.md:7 | one unknown key among known | test_main_reports_an_unknown_key |
| specs/checkconf.md:7 | several unknown keys | test_main_reports_every_unknown_key_in_order |
| specs/checkconf.md:7 | each known key (name, port, debug) | test_main_accepts_all_known_keys |
| specs/checkconf.md:7 | case variant of a known key | test_main_treats_key_names_as_case_sensitive |
| specs/checkconf.md:8 | unknown key present | test_main_returns_1_for_an_unknown_key |
| specs/checkconf.md:8 | no unknown key / empty file | test_main_accepts_all_known_keys, test_main_accepts_an_empty_file |

## Mutants

Mutant 1: specs/checkconf.md:8, test_main_returns_1_for_an_unknown_key — always returns 0 — task-1-mutant-1.patch
Mutant 2: specs/checkconf.md:7, test_main_accepts_all_known_keys — debug not a known key — task-1-mutant-2.patch
Mutant 3: specs/checkconf.md:7, test_main_reports_every_unknown_key_in_order — stops after first unknown key — task-1-mutant-3.patch
Mutant 4: specs/checkconf.md:8, test_main_accepts_all_known_keys, test_main_accepts_an_empty_file — always returns 1 — task-1-mutant-4.patch
Mutant 5: specs/checkconf.md:7, test_main_treats_key_names_as_case_sensitive — key compared lowercased — task-1-mutant-5.patch
Mutant 6: specs/checkconf.md:7, test_main_reports_an_unknown_key — colour treated as known — task-1-mutant-6.patch
