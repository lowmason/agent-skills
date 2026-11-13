# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each part alone (h, m, s) | test_parse_duration_returns_seconds |
| specs/duration.md:7 | parts combined, in order, some omitted | test_parse_duration_returns_seconds |
| specs/duration.md:7 | multi-digit, leading zero, zero | test_parse_duration_returns_seconds |
| specs/duration.md:7 | at least one part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | out of order / repeated / no unit / unit without digits | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign | test_parse_duration_rejects_other_text |
| specs/duration.md:9 | whitespace, trailing newline, uppercase, other unit | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | seconds as int | test_parse_duration_returns_seconds |

## Mutants

Mutant 1: specs/duration.md:8, test_parse_duration_returns_seconds — hours weighted 60 — task-1-mutant-1.patch
Mutant 2: specs/duration.md:8, test_parse_duration_returns_seconds — minutes weighted 1 — task-1-mutant-2.patch
Mutant 3: specs/duration.md:8, test_parse_duration_returns_seconds — seconds dropped — task-1-mutant-3.patch
Mutant 4: specs/duration.md:7, test_parse_duration_rejects_other_text — \d instead of [0-9] — task-1-mutant-4.patch
Mutant 5: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, test_parse_duration_rejects_other_text — empty string accepted — task-1-mutant-6.patch
Mutant 7: specs/duration.md:7, test_parse_duration_returns_seconds — hours limited to one digit — task-1-mutant-7.patch
Mutant 8: specs/duration.md:9, test_parse_duration_rejects_other_text — trailing newline tolerated — task-1-mutant-8.patch
