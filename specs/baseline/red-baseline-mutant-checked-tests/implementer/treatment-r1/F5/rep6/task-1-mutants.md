# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each single part (h, m, s) | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts, two-part combos, leading zero, zeros | test_parse_duration_returns_seconds |
| specs/duration.md:7 | parts out of order / repeated | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | no part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int seconds | test_parse_duration_returns_seconds |
| specs/duration.md:9 | missing unit, unknown unit, case, whitespace, trailing newline | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — \d instead of [0-9] accepts non-ASCII digits — task-1-mutant-1.patch
Mutant 2: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch accepts trailing junk — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, test_parse_duration_rejects_other_text — empty text accepted — task-1-mutant-3.patch
Mutant 4: specs/duration.md:8, test_parse_duration_returns_seconds — hours multiplier wrong — task-1-mutant-4.patch
Mutant 5: specs/duration.md:8, test_parse_duration_returns_seconds — minutes multiplier wrong — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, test_parse_duration_rejects_other_text — order m before h — task-1-mutant-6.patch
Mutant 7: specs/duration.md:8, test_parse_duration_returns_seconds — seconds off by one — task-1-mutant-7.patch
