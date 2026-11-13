# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | each part alone (h, m, s) | test_parse_duration_returns_seconds |
| specs/duration.md:7 | all parts / adjacent pairs | test_parse_duration_returns_seconds |
| specs/duration.md:7 | multi-digit and leading-zero n | test_parse_duration_returns_seconds ('15m','05m') |
| specs/duration.md:7 | wrong order / repeated part | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | non-ASCII digit, sign | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | empty (no part) | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | int seconds | test_parse_duration_returns_seconds |
| specs/duration.md:9 | trailing/leading whitespace, trailing newline, garbage | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7 — digits accept any Unicode digit (\d) — task-1-mutant-1.patch
Mutant 2: specs/duration.md:9 — match instead of fullmatch (trailing text ignored) — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7 — empty string accepted — task-1-mutant-3.patch
Mutant 4: specs/duration.md:9 — `$` anchor with match, trailing newline accepted — task-1-mutant-4.patch
Mutant 5: specs/duration.md:8 — hour multiplier wrong — task-1-mutant-5.patch
Mutant 6: specs/duration.md:7 — order not enforced (extra h group after m) — task-1-mutant-6.patch
Mutant 7: specs/duration.md:7 — n limited to a single digit — task-1-mutant-7.patch
