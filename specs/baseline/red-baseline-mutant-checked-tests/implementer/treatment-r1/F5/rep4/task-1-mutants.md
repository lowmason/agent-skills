# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | single parts h, m, s | test_parse_duration_returns_seconds |
| specs/duration.md:7 | combinations, leading zero, zeros | test_parse_duration_returns_seconds |
| specs/duration.md:7 | at least one part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | wrong order / repeated | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign, whitespace, newline, case, no unit, bare unit | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int seconds | test_parse_duration_returns_seconds |
| specs/duration.md:9 | other text raises ValueError | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — digits matched with \d, accepting non-ASCII — task-1-mutant-1.patch
Mutant 2: specs/duration.md:8, test_parse_duration_returns_seconds — hours multiplier wrong — task-1-mutant-2.patch
Mutant 3: specs/duration.md:8, test_parse_duration_returns_seconds — minutes multiplier wrong — task-1-mutant-3.patch
Mutant 4: specs/duration.md:7, test_parse_duration_rejects_other_text — empty string accepted — task-1-mutant-4.patch
Mutant 5: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch — task-1-mutant-5.patch
Mutant 6: specs/duration.md:8, test_parse_duration_returns_seconds — off by one — task-1-mutant-6.patch
Mutant 7: specs/duration.md:7, test_parse_duration_rejects_other_text — digits optional ([0-9]*) — task-1-mutant-7.patch
Mutant 8: specs/duration.md:7, test_parse_duration_rejects_other_text — order of h and m swapped — task-1-mutant-8.patch
