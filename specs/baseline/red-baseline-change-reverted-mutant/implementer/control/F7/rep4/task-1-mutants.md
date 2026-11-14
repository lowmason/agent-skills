# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | run of two spaces | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | single space | test_slugify_single_space_becomes_one_hyphen |
| specs/slugs.md:7 | long run | test_slugify_collapses_long_run |
| specs/slugs.md:7 | tabs, newlines, mixed | test_slugify_collapses_tabs_newlines_and_mixed_whitespace |
| specs/slugs.md:7 | run at start/end | test_slugify_collapses_runs_at_ends |
| specs/slugs.md:7 | several runs | test_slugify_collapses_each_run_separately |
| specs/slugs.md:8 | uppercase letters | test_slugify_lowercases |
| specs/slugs.md:8 | with whitespace runs | test_slugify_lowercases_with_whitespace_runs |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_collapses_space_runs — each whitespace char replaced, no collapse — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_tabs_newlines_and_mixed_whitespace — only spaces collapse — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — no lowercasing — task-1-mutant-3.patch
Mutant 4: specs/slugs.md:7, test_slugify_collapses_runs_at_ends — strips ends — task-1-mutant-4.patch
