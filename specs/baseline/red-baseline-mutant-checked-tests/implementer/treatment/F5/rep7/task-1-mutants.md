# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each part alone (h, m, s) | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts, pairs, skipped middle part | test_parse_duration_returns_seconds |
| specs/duration.md:7 | multi-digit, leading zero, zero | test_parse_duration_returns_seconds |
| specs/duration.md:7 | out of order / repeated part | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | no part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign | test_parse_duration_rejects_other_text |
| specs/duration.md:9 | missing unit, bare unit, wrong/uppercase unit, whitespace, trailing newline | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int seconds | test_parse_duration_returns_seconds |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — \d accepts non-ASCII digits — task-1-mutant-1.patch
Mutant 2: specs/duration.md:9, test_parse_duration_rejects_other_text — match instead of fullmatch — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, test_parse_duration_rejects_other_text — empty text not rejected — task-1-mutant-3.patch
Mutant 4: specs/duration.md:8, test_parse_duration_returns_seconds — minutes weighted 30 — task-1-mutant-4.patch
Mutant 5: specs/duration.md:9, test_parse_duration_rejects_other_text — $ anchor allows trailing newline — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7, test_parse_duration_returns_seconds — only one digit allowed — task-1-mutant-6.patch
Mutant 8: specs/duration.md:8, test_parse_duration_returns_seconds — hours weighted 360 — task-1-mutant-8.patch
Mutant 9: specs/duration.md:8, test_parse_duration_returns_seconds — seconds doubled — task-1-mutant-9.patch
Withdrawn: 7 — no behavior changes (adds zero)
