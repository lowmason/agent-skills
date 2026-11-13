# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each part alone (h, m, s) | test_parse_duration_returns_seconds |
| specs/duration.md:7 | parts combined, parts skipped | test_parse_duration_returns_seconds |
| specs/duration.md:7 | multi-digit and leading-zero n | test_parse_duration_multi_digit_parts, test_parse_duration_returns_seconds |
| specs/duration.md:7 | non-ASCII digit | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | wrong order, repeated part | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | no part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:9 | trailing/leading garbage, whitespace, sign, case, unit-less | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | seconds value, int type | test_parse_duration_returns_seconds |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_multi_digit_parts — hours accept one digit only — task-1-mutant-1.patch
Mutant 2: specs/duration.md:7, test_parse_duration_multi_digit_parts — minutes accept one digit only — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, test_parse_duration_multi_digit_parts — seconds accept one digit only — task-1-mutant-3.patch
Mutant 4: specs/duration.md:7, test_parse_duration_rejects_other_text — \d accepts non-ASCII digits — task-1-mutant-4.patch
Mutant 5: specs/duration.md:7, test_parse_duration_rejects_other_text — empty text accepted as 0 — task-1-mutant-5.patch
Mutant 6: specs/duration.md:8, test_parse_duration_returns_seconds — hours multiplied by 60 — task-1-mutant-6.patch
Mutant 7: specs/duration.md:8, test_parse_duration_returns_seconds — minutes multiplied by 3600 — task-1-mutant-7.patch
Mutant 8: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch allows trailing text — task-1-mutant-8.patch
Mutant 9: specs/duration.md:7, test_parse_duration_rejects_other_text — m and s order swapped in the pattern — task-1-mutant-9.patch
