# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each single part, all parts, subsets, leading zero, zeros | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated part, missing unit, unknown unit | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | at least one part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:9 | whitespace, trailing newline, uppercase | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int seconds | test_parse_duration_returns_seconds |

## Mutants

Mutant 1: specs/duration.md:7, rejects_other_text — \d accepts non-ASCII digits — task-1-mutant-1.patch
Mutant 2: specs/duration.md:8, returns_seconds — hours multiplied by 360 — task-1-mutant-2.patch
Mutant 3: specs/duration.md:8, returns_seconds — minutes multiplied by 6 — task-1-mutant-3.patch
Mutant 4: specs/duration.md:9, rejects_other_text — match instead of fullmatch — task-1-mutant-4.patch
Mutant 5: specs/duration.md:7, rejects_other_text — empty string accepted — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, rejects_other_text — m before h order — task-1-mutant-6.patch
