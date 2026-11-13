# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each single part h, m, s | test_parse_duration_returns_seconds |
| specs/duration.md:7 | parts combined, subsets, leading zero, zero values | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated part, missing unit, no digits | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign, case, whitespace, trailing newline | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | empty (no part present) | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | seconds arithmetic, int type | test_parse_duration_returns_seconds |
| specs/duration.md:9 | other text raises ValueError | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, rejects test — \d accepts non-ASCII digits — task-1-mutant-1.patch
Mutant 2: specs/duration.md:9, rejects test — match instead of fullmatch — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, rejects test — empty string accepted — task-1-mutant-3.patch
Mutant 4: specs/duration.md:8, returns test — minutes multiplier wrong — task-1-mutant-4.patch
Mutant 5: specs/duration.md:7, rejects test — hours part may repeat — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, rejects test — case-insensitive units — task-1-mutant-6.patch
Mutant 7: specs/duration.md:8, returns test — hours multiplier wrong — task-1-mutant-7.patch
