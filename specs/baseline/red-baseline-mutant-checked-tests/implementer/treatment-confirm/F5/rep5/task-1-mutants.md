# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/duration.md:7 | single parts, all parts, partial combos, leading zero, zeros | test_parse_duration_returns_seconds |
| specs/duration.md:7 | ASCII digits only (Arabic-Indic, sign) | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | at least one part (empty) | test_parse_duration_rejects_other_text |
| specs/duration.md:7 | order, repeats | test_parse_duration_rejects_other_text |
| specs/duration.md:8 | seconds as int | test_parse_duration_returns_seconds |
| specs/duration.md:9 | other text (bare number, unknown unit, case, whitespace, trailing newline) | test_parse_duration_rejects_other_text |

## Mutants

Mutant 1: specs/duration.md:7, test_parse_duration_rejects_other_text — \d without re.ASCII, so non-ASCII digits accepted — task-1-mutant-1.patch
Mutant 2: specs/duration.md:9, test_parse_duration_rejects_other_text — prefix match instead of full match — task-1-mutant-2.patch
Mutant 3: specs/duration.md:7, test_parse_duration_rejects_other_text — empty string accepted — task-1-mutant-3.patch
Mutant 4: specs/duration.md:8, test_parse_duration_returns_seconds — minutes multiplied wrongly — task-1-mutant-4.patch
Mutant 5: specs/duration.md:8, test_parse_duration_returns_seconds — hours multiplied wrongly — task-1-mutant-5.patch
Withdrawn: 5 (first draft) — replaced an empty alternation, which changes no behavior; superseded by the current mutant 5
