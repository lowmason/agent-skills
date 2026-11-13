# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each part alone, all parts, subsets, leading zeros, zero | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated part, missing unit, wrong unit/case | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign, spaces, trailing newline | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | no part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int result in seconds | test_parse_duration_returns_seconds |
| specs/duration.md:9 | other text raises ValueError | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — empty text accepted as 0 — task-1-mutant-1.patch
Mutant 2: specs/duration.md:7, test_parse_duration_rejects_other_text — \d without ASCII accepts Arabic-Indic digits — task-1-mutant-2.patch
Mutant 3: specs/duration.md:9, test_parse_duration_rejects_other_text — prefix match instead of full match — task-1-mutant-3.patch
Mutant 4: specs/duration.md:8, test_parse_duration_returns_seconds — hour multiplier wrong — task-1-mutant-4.patch
