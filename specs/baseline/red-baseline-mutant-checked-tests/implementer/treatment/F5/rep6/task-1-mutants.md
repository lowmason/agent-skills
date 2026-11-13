# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each part alone (h, m, s) | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts, subsets, leading zero, zeros | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated part, missing unit | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign, whitespace, trailing newline, uppercase | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | at least one part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int seconds | test_parse_duration_returns_seconds |
| specs/duration.md:9 | other text raises ValueError | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — \d instead of [0-9] accepts Arabic digits — task-1-mutant-1.patch
Mutant 2: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch accepts trailing text — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, test_parse_duration_rejects_other_text — empty string accepted — task-1-mutant-3.patch
Mutant 4: specs/duration.md:9, test_parse_duration_rejects_other_text — `$` anchor accepts trailing newline — task-1-mutant-4.patch
Mutant 5: specs/duration.md:8, test_parse_duration_returns_seconds — minutes weighted wrongly — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, test_parse_duration_rejects_other_text — order m before h — task-1-mutant-6.patch
