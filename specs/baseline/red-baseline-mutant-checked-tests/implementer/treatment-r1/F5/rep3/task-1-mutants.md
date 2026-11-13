# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each single part h, m, s | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts / adjacent pairs / h+s gap | test_parse_duration_returns_seconds |
| specs/duration.md:7 | leading zero, zero value | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated part | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | no part (empty), bare unit, missing unit | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign, uppercase unit, unknown unit | test_parse_duration_rejects_other_text |
| specs/duration.md:9 | leading/inner whitespace, trailing newline | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | seconds as int | test_parse_duration_returns_seconds |

## Mutants

Mutant 1: specs/duration.md:8, test_parse_duration_returns_seconds — hours multiplied by 60 — task-1-mutant-1.patch
Mutant 2: specs/duration.md:8, test_parse_duration_returns_seconds — minutes multiplied by 100 — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, test_parse_duration_rejects_other_text — unit s optional — task-1-mutant-3.patch
Mutant 4: specs/duration.md:7, test_parse_duration_rejects_other_text — empty text accepted — task-1-mutant-4.patch
Mutant 5: specs/duration.md:7, test_parse_duration_rejects_other_text — \d instead of [0-9] — task-1-mutant-5.patch
Mutant 6: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch — task-1-mutant-6.patch
Mutant 7: specs/duration.md:9, test_parse_duration_rejects_other_text — $ anchor (accepts trailing newline) — task-1-mutant-7.patch
Mutant 8: specs/duration.md:9, test_parse_duration_rejects_other_text — leading whitespace allowed — task-1-mutant-8.patch
Mutant 9: specs/duration.md:7, test_parse_duration_rejects_other_text — case-insensitive units — task-1-mutant-9.patch
Mutant 10: specs/duration.md:8, test_parse_duration_returns_seconds — absent parts count as 1 — task-1-mutant-10.patch
