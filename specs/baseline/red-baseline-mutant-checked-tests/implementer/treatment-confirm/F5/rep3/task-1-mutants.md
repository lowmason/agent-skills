# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each single part, all parts, subsets | test_parse_duration_returns_seconds |
| specs/duration.md:7 | leading zeros, zero values | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated part, unit missing, no parts | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign, whitespace, trailing newline | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int seconds | test_parse_duration_returns_seconds |
| specs/duration.md:9 | other text raises ValueError | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — digits matched with \d (accepts non-ASCII) — task-1-mutant-1.patch
Mutant 2: specs/duration.md:7, test_parse_duration_rejects_other_text — empty string no longer rejected — task-1-mutant-2.patch
Mutant 3: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch (trailing text accepted) — task-1-mutant-3.patch
Mutant 4: specs/duration.md:8, test_parse_duration_returns_seconds — hours multiplied by 60 — task-1-mutant-4.patch
Mutant 5: specs/duration.md:8, test_parse_duration_returns_seconds — minutes multiplied by 6 — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, test_parse_duration_rejects_other_text — hours part may repeat (1h1h accepted) — task-1-mutant-6.patch
