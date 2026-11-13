# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each single part h, m, s | test_parse_duration_returns_seconds |
| specs/duration.md:7 | parts combined, a part skipped, leading zero, zeros | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated part, missing unit, empty | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign, whitespace, trailing newline, uppercase | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int result | test_parse_duration_returns_seconds |
| specs/duration.md:9 | other text raises ValueError | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, rejects_other_text — \d accepts non-ASCII digits — task-1-mutant-1.patch
Mutant 2: specs/duration.md:9, rejects_other_text — match instead of fullmatch — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, rejects_other_text — empty text allowed — task-1-mutant-3.patch
Mutant 4: specs/duration.md:7, rejects_other_text — match with a $ anchor lets a trailing newline through — task-1-mutant-4.patch
Mutant 5: specs/duration.md:8, returns_seconds — hours multiplier wrong — task-1-mutant-5.patch
Mutant 6: specs/duration.md:8, returns_seconds — minutes multiplier wrong — task-1-mutant-6.patch
Mutant 7: specs/duration.md:7, rejects_other_text — part order swapped — task-1-mutant-7.patch
Mutant 8: specs/duration.md:8, returns_seconds — absent part counts as 1 — task-1-mutant-8.patch
