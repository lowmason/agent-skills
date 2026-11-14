# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | two spaces | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | single space | test_slugify_single_space_becomes_one_hyphen |
| specs/slugs.md:7 | long run | test_slugify_collapses_long_run |
| specs/slugs.md:7 | mixed whitespace run | test_slugify_collapses_mixed_whitespace_run |
| specs/slugs.md:7 | tab / newline | test_slugify_each_whitespace_kind_becomes_hyphen |
| specs/slugs.md:7 | several runs | test_slugify_separate_runs_each_become_one_hyphen |
| specs/slugs.md:8 | capital first letter | test_slugify_lowercases |
| specs/slugs.md:8 | mixed case with runs | test_slugify_lowercases_mixed_case_words |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_each_whitespace_kind_becomes_hyphen — only spaces count as whitespace — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_space_runs — each space replaced separately (no collapsing) — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — lowercasing dropped — task-1-mutant-3.patch
Mutant 4: specs/slugs.md:7, test_slugify_collapses_mixed_whitespace_run — newlines not whitespace — task-1-mutant-4.patch
