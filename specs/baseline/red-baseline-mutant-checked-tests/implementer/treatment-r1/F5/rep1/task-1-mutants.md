# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each part alone (h, m, s) | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts, subsets, multi-digit, leading zero, zeros | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order / repeated part | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | ASCII digits only (non-ASCII, sign) | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | no digits for a part; at least one part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int seconds | test_parse_duration_returns_seconds |
| specs/duration.md:9 | missing unit, bad unit/case, whitespace, trailing newline | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:8, test_parse_duration_returns_seconds — hour multiplier 60 — task-1-mutant-1.patch
Mutant 2: specs/duration.md:8, test_parse_duration_returns_seconds — minute multiplier 3600 — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, test_parse_duration_rejects_other_text — \d instead of [0-9] — task-1-mutant-3.patch
Mutant 4: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch — task-1-mutant-4.patch
Mutant 5: specs/duration.md:7, test_parse_duration_rejects_other_text — empty text accepted — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, test_parse_duration_rejects_other_text — s before m order — task-1-mutant-6.patch
Mutant 7: specs/duration.md:7, test_parse_duration_rejects_other_text — hour digits optional — task-1-mutant-7.patch
Mutant 8: specs/duration.md:9, test_parse_duration_rejects_other_text — $ with match accepts trailing newline — task-1-mutant-8.patch
Mutant 9: specs/duration.md:8, test_parse_duration_returns_seconds — float result — task-1-mutant-9.patch
Mutant 10: specs/duration.md:8, test_parse_duration_returns_seconds — seconds ignored — task-1-mutant-10.patch
