# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | single space | test_slugify_single_space |
| specs/slugs.md:7 | run of two spaces | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | long run | test_slugify_long_space_run |
| specs/slugs.md:7 | mixed whitespace run | test_slugify_collapses_mixed_whitespace_runs |
| specs/slugs.md:7 | single tab / newline | test_slugify_single_tab_and_newline |
| specs/slugs.md:8 | uppercase | test_slugify_lowercases |
| specs/slugs.md:8 | uppercase around runs | test_slugify_lowercases_across_runs |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_collapses_space_runs — each whitespace char becomes its own hyphen — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_mixed_whitespace_runs — only spaces are matched, not tabs/newlines — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — lowercasing dropped — task-1-mutant-3.patch
Keeps: test_slugify_lowercases — lowercasing of letters, which slugify did before the task and keeps
Keeps: test_slugify_single_space — a lone space becomes one hyphen, as before the task
