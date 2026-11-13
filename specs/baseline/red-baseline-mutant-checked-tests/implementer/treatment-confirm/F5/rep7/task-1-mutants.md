# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each part alone (h, m, s) | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts / adjacent pairs, multi-digit, leading zero | test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated part | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign, uppercase, no unit, unknown unit | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | no parts (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | seconds as int | test_parse_duration_returns_seconds |
| specs/duration.md:9 | whitespace/newline around or inside | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — empty text accepted as 0 — task-1-mutant-1.patch
Mutant 2: specs/duration.md:7, test_parse_duration_rejects_other_text — \d accepts non-ASCII digits — task-1-mutant-2.patch
Mutant 3: specs/duration.md:9, test_parse_duration_rejects_other_text — prefix match instead of full match — task-1-mutant-3.patch
Mutant 4: specs/duration.md:8, test_parse_duration_returns_seconds — minutes multiplied by 3600 — task-1-mutant-4.patch
Mutant 5: specs/duration.md:7, test_parse_duration_rejects_other_text — m before h order — task-1-mutant-5.patch
Mutant 6: specs/duration.md:9, test_parse_duration_rejects_other_text — $ anchor lets trailing newline through — task-1-mutant-6.patch
Mutant 7: specs/duration.md:8, test_parse_duration_returns_seconds — hours multiplied by 60 — task-1-mutant-7.patch
Mutant 8: specs/duration.md:8, test_parse_duration_returns_seconds — missing part counts as 1 — task-1-mutant-8.patch
Mutant 9: specs/duration.md:7, test_parse_duration_rejects_other_text/returns_seconds — uppercase S unit — task-1-mutant-9.patch
Withdrawn: 10 — digits `*` for hours: 'h' still raises ValueError from int('')
