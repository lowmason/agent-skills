# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | run of spaces | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | mixed whitespace run | test_slugify_collapses_mixed_whitespace_runs |
| specs/slugs.md:7 | single tab / single space | test_slugify_single_tab_becomes_hyphen, test_slugify_single_space_becomes_hyphen |
| specs/slugs.md:8 | capitals, one and several words | test_slugify_lowercases, test_slugify_lowercases_across_words |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_collapses_mixed_whitespace_runs, test_slugify_single_tab_becomes_hyphen — only spaces collapse — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:8, test_slugify_lowercases — no lowercasing — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:7, test_slugify_collapses_space_runs — each whitespace char replaced separately — task-1-mutant-3.patch
