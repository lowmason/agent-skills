# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | run of spaces | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | single space | test_slugify_single_space_becomes_one_hyphen |
| specs/slugs.md:7 | tab / newline | test_slugify_collapses_tab_and_newline_alone |
| specs/slugs.md:7 | mixed run | test_slugify_collapses_mixed_whitespace_runs |
| specs/slugs.md:7 | at the ends | test_slugify_collapses_runs_at_the_ends |
| specs/slugs.md:7 | several runs | test_slugify_collapses_each_run_separately |
| specs/slugs.md:8 | uppercase | test_slugify_lowercases |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_collapses_tab_and_newline_alone — only spaces collapse — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_space_runs — each whitespace char becomes its own hyphen — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — no lowercasing — task-1-mutant-3.patch
Mutant 4: specs/slugs.md:7, test_slugify_single_space_becomes_one_hyphen — runs are removed instead of hyphenated — task-1-mutant-4.patch
