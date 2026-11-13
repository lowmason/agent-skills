# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each part alone, all parts, subsets | test_parse_duration_returns_seconds |
| specs/duration.md:7 | multi-digit, leading zero, zero | test_parse_duration_returns_seconds, test_parse_duration_multi_digit_parts |
| specs/duration.md:7 | wrong order, repeated, empty | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit | test_parse_duration_rejects_other_text |
| specs/duration.md:9 | missing unit, bad unit, case, sign, whitespace, trailing newline | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int seconds | test_parse_duration_returns_seconds |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_multi_digit_parts — hours limited to one digit — task-1-mutant-1.patch
Mutant 2: specs/duration.md:7, test_parse_duration_rejects_other_text — \d instead of [0-9] — task-1-mutant-2.patch
Mutant 3: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch — task-1-mutant-3.patch
Mutant 4: specs/duration.md:9, test_parse_duration_rejects_other_text — empty text accepted — task-1-mutant-4.patch
Mutant 5: specs/duration.md:8, test_parse_duration_returns_seconds — minutes multiplier wrong — task-1-mutant-5.patch
Mutant 6: specs/duration.md:8, test_parse_duration_returns_seconds — hours multiplier wrong — task-1-mutant-6.patch
Mutant 7: specs/duration.md:7, test_parse_duration_rejects_other_text — s unit optional — task-1-mutant-7.patch
Mutant 8: specs/duration.md:8, test_parse_duration_returns_seconds — seconds dropped — task-1-mutant-8.patch
