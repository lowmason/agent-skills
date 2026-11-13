# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each single part, all parts, subsets | test_parse_duration_returns_seconds |
| specs/duration.md:7 | multi-digit n, leading zero | test_parse_duration_multi_digit_parts, test_parse_duration_returns_seconds |
| specs/duration.md:7 | wrong order, repeated part | test_parse_duration_rejects_wrong_order_or_repeats, test_parse_duration_rejects_other_text |
| specs/duration.md:7 | empty text (no part) | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign, whitespace, trailing newline, uppercase | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | seconds value, int type | test_parse_duration_returns_seconds |
| specs/duration.md:9 | other text raises ValueError | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:9, test_parse_duration_rejects_other_text — prefix match instead of full match — task-1-mutant-1.patch
Mutant 2: specs/duration.md:7, test_parse_duration_rejects_other_text — \d accepts non-ASCII digits — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, test_parse_duration_rejects_other_text — empty text accepted as 0 — task-1-mutant-3.patch
Mutant 4: specs/duration.md:8, test_parse_duration_returns_seconds — hour factor 360 — task-1-mutant-4.patch
Mutant 5: specs/duration.md:8, test_parse_duration_returns_seconds — minute factor 6 — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, test_parse_duration_rejects_wrong_order_or_repeats — s before m — task-1-mutant-6.patch
Mutant 7: specs/duration.md:7, test_parse_duration_rejects_other_text — hours part may repeat — task-1-mutant-7.patch
Mutant 8: specs/duration.md:7, test_parse_duration_rejects_uppercase_units — uppercase S accepted — task-1-mutant-8.patch
Mutant 9: specs/duration.md:7, test_parse_duration_multi_digit_parts — minutes limited to one digit — task-1-mutant-9.patch
