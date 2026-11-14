# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | single space | test_slugify_single_space |
| specs/slugs.md:7 | run of two spaces | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | long run of spaces | test_slugify_collapses_long_space_run |
| specs/slugs.md:7 | tab / newline / mixed runs | test_slugify_collapses_tab_and_newline_runs |
| specs/slugs.md:7 | runs at start and end | test_slugify_collapses_runs_at_edges |
| specs/slugs.md:7 | several runs | test_slugify_collapses_each_run_separately |
| specs/slugs.md:8 | lowercase | test_slugify_lowercases, test_slugify_collapses_each_run_separately |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_collapses_tab_and_newline_runs — only spaces are collapsed — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_space_runs — each whitespace char becomes its own hyphen — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — no lowercasing — task-1-mutant-3.patch
Mutant 4: specs/slugs.md:7, test_slugify_collapses_runs_at_edges — edge whitespace stripped — task-1-mutant-4.patch
Keeps: test_slugify_lowercases — lowercasing, behavior from before the task that the task keeps
Keeps: test_slugify_single_space — a single space becomes one hyphen, behavior from before the task that the task keeps
