# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each part alone (h, m, s) | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts, subsets, leading zeros | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated part | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign, case, spaces, newline, empty, missing digits/unit | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | integer seconds | test_parse_duration_returns_seconds |
| specs/duration.md:9 | other text raises ValueError | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — hour digits use \d, accepting non-ASCII digits — task-1-mutant-1.patch
Mutant 2: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, test_parse_duration_rejects_other_text — empty text accepted — task-1-mutant-3.patch
Mutant 4: specs/duration.md:8, test_parse_duration_returns_seconds — minutes multiplier wrong — task-1-mutant-4.patch
Mutant 5: specs/duration.md:7, test_parse_duration_rejects_other_text — case-insensitive units — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, test_parse_duration_rejects_other_text — hour digits optional — task-1-mutant-6.patch
Mutant 7: specs/duration.md:8, test_parse_duration_returns_seconds — hours multiplier wrong — task-1-mutant-7.patch
Mutant 8: specs/duration.md:8, test_parse_duration_returns_seconds — absent part counts as 1 — task-1-mutant-8.patch
