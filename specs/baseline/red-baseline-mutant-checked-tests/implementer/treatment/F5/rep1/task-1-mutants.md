# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each single part (h, m, s) | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts; skipped middle part | test_parse_duration_returns_seconds |
| specs/duration.md:7 | multi-digit, leading zero, zero | test_parse_duration_returns_seconds |
| specs/duration.md:7 | non-ASCII digit, sign | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | wrong order, repeated part, no part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int seconds | test_parse_duration_returns_seconds |
| specs/duration.md:9 | trailing newline, spaces, unit without digits, no unit, unknown/uppercase unit | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — \d accepts non-ASCII digits — task-1-mutant-1.patch
Mutant 4: specs/duration.md:8, test_parse_duration_returns_seconds — minutes factor wrong — task-1-mutant-4.patch
Mutant 5: specs/duration.md:8, test_parse_duration_returns_seconds — hours factor wrong — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, test_parse_duration_rejects_other_text — empty string accepted — task-1-mutant-6.patch
Mutant 7: specs/duration.md:7, test_parse_duration_returns_seconds — seconds part required — task-1-mutant-7.patch
Mutant 8: specs/duration.md:7, test_parse_duration_returns_seconds — only one digit allowed — task-1-mutant-8.patch
Mutant 9: specs/duration.md:9, test_parse_duration_rejects_other_text — search instead of fullmatch — task-1-mutant-9.patch
