# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | single part h, m, s | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts, subsets, multi-digit, leading zero | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated parts | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | no parts (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | seconds as int | test_parse_duration_returns_seconds |
| specs/duration.md:9 | whitespace, trailing newline, missing unit, uppercase, unknown unit | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:9 — match instead of fullmatch (trailing junk) — task-1-mutant-1.patch
Mutant 2: specs/duration.md:7 — \d instead of [0-9] — task-1-mutant-2.patch
Mutant 3: specs/duration.md:8 — hour factor wrong — task-1-mutant-3.patch
Mutant 4: specs/duration.md:8 — minute factor wrong — task-1-mutant-4.patch
Mutant 5: specs/duration.md:7 — hours part may repeat — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7 — empty text accepted — task-1-mutant-6.patch
Mutant 7: specs/duration.md:8 — returns float — task-1-mutant-7.patch
Mutant 8: specs/duration.md:7 — single digit only — task-1-mutant-8.patch
Mutant 9: specs/duration.md:9 — input stripped — task-1-mutant-9.patch
Mutant 10: specs/duration.md:7 — s before m order — task-1-mutant-10.patch
