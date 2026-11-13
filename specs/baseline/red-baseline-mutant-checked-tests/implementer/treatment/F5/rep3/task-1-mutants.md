# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each single part h, m, s | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts, two parts, skipped middle part | test_parse_duration_returns_seconds |
| specs/duration.md:7 | multi-digit and leading-zero numbers, zero | test_parse_duration_returns_seconds |
| specs/duration.md:7 | out of order, repeated part | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | at least one part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:9 | missing unit, bare unit, unknown unit, wrong case, sign, whitespace, trailing newline | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | integer seconds | test_parse_duration_returns_seconds |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — \d accepts non-ASCII digits — task-1-mutant-1.patch
Mutant 2: specs/duration.md:8, test_parse_duration_returns_seconds — hours multiplied by 360 — task-1-mutant-2.patch
Mutant 3: specs/duration.md:8, test_parse_duration_returns_seconds — minutes multiplied by 6 — task-1-mutant-3.patch
Mutant 4: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch — task-1-mutant-4.patch
Mutant 5: specs/duration.md:7, test_parse_duration_rejects_other_text — empty text accepted — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, test_parse_duration_rejects_other_text — s before m order — task-1-mutant-6.patch
Mutant 7: specs/duration.md:7, test_parse_duration_returns_seconds — single digit only — task-1-mutant-7.patch
Mutant 8: specs/duration.md:8, test_parse_duration_returns_seconds — off by one second — task-1-mutant-8.patch
Mutant 9: specs/duration.md:9, test_parse_duration_rejects_other_text — $ anchor lets trailing newline through — task-1-mutant-9.patch
