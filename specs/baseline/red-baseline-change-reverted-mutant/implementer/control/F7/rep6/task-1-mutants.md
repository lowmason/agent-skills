# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | run of two spaces | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | single space | test_slugify_single_space_becomes_one_hyphen |
| specs/slugs.md:7 | long runs, several gaps | test_slugify_collapses_long_runs_per_gap |
| specs/slugs.md:7 | non-space whitespace, mixed | test_slugify_collapses_mixed_whitespace_runs |
| specs/slugs.md:8 | uppercase letters | test_slugify_lowercases |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_collapses_mixed_whitespace_runs — only spaces are matched, not all whitespace — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_space_runs — each whitespace char becomes its own hyphen — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — lowercasing dropped — task-1-mutant-3.patch
