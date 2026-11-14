# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | two spaces | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | single space | test_slugify_single_space_is_one_hyphen |
| specs/slugs.md:7 | long run | test_slugify_collapses_long_runs |
| specs/slugs.md:7 | mixed whitespace (tab/newline) | test_slugify_collapses_mixed_whitespace_runs |
| specs/slugs.md:7 | several runs; leading/trailing | test_slugify_collapses_each_run_separately, test_slugify_collapses_leading_and_trailing_runs |
| specs/slugs.md:8 | uppercase | test_slugify_lowercases, test_slugify_lowercases_with_whitespace_runs |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_collapses_mixed_whitespace_runs — only spaces collapse, not other whitespace — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_space_runs — each whitespace char becomes its own hyphen — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — no lowercasing — task-1-mutant-3.patch
Mutant 4: specs/slugs.md:7, test_slugify_collapses_leading_and_trailing_runs — edge whitespace stripped before collapsing — task-1-mutant-4.patch
