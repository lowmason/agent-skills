# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/checkconf.md:7 | one unknown key | test_main_reports_an_unknown_key |
| specs/checkconf.md:7 | several unknown keys | test_main_reports_every_unknown_key_in_order |
| specs/checkconf.md:7 | repeated unknown key | test_main_reports_a_repeated_unknown_key_each_time |
| specs/checkconf.md:7 | last line, no newline | test_main_reports_an_unknown_key_on_the_last_line_without_newline |
| specs/checkconf.md:7 | value containing = | test_main_reports_the_key_only_when_the_value_contains_equals |
| specs/checkconf.md:7 | near-miss keys | test_main_matches_known_keys_exactly |
| specs/checkconf.md:7 | all three known keys | test_main_returns_0_and_prints_nothing_for_known_keys |
| specs/checkconf.md:8 | unknown key | test_main_returns_1_for_an_unknown_key |
| specs/checkconf.md:8 | none / empty file | test_main_returns_0_for_an_empty_file |

## Mutants

Mutant 1: specs/checkconf.md:8, test_main_returns_1_for_an_unknown_key — status never becomes 1 — task-1-mutant-1.patch
Mutant 2: specs/checkconf.md:7, test_main_returns_0_and_prints_nothing_for_known_keys — debug treated as unknown — task-1-mutant-2.patch
Mutant 3: specs/checkconf.md:7, test_main_reports_every_unknown_key_in_order — stops after first unknown key — task-1-mutant-3.patch
Mutant 4: specs/checkconf.md:7, test_main_matches_known_keys_exactly — key compared case-insensitively — task-1-mutant-4.patch
Mutant 5: specs/checkconf.md:7, test_main_reports_the_key_only_when_the_value_contains_equals — key taken as first whitespace token — task-1-mutant-5.patch
Mutant 6: specs/checkconf.md:7, test_main_reports_an_unknown_key_on_the_last_line_without_newline — last line dropped — task-1-mutant-6.patch
Mutant 7: specs/checkconf.md:7, test_main_reports_a_repeated_unknown_key_each_time — only first unknown key printed — task-1-mutant-7.patch
Mutant 8: specs/checkconf.md:7, test_main_matches_known_keys_exactly — prefix of a known key accepted — task-1-mutant-8.patch
