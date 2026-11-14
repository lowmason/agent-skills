# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | single space | test_slugify_single_space_becomes_one_hyphen |
| specs/slugs.md:7 | run of two spaces | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | long run | test_slugify_collapses_long_space_run |
| specs/slugs.md:7 | mixed whitespace run | test_slugify_collapses_mixed_whitespace_run |
| specs/slugs.md:7 | single tab/newline | test_slugify_single_tab_and_newline_become_hyphens |
| specs/slugs.md:7 | several runs | test_slugify_collapses_each_run_separately |
| specs/slugs.md:7 | leading/trailing run | test_slugify_leading_and_trailing_runs_become_one_hyphen |
| specs/slugs.md:8 | lowercase | test_slugify_lowercases, test_slugify_lowercases_across_whitespace |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_collapses_space_runs — each space replaced separately — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_mixed_whitespace_run — only spaces count as whitespace — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — no lowercasing — task-1-mutant-3.patch
Mutant 4: specs/slugs.md:7, test_slugify_single_space_becomes_one_hyphen — run becomes two hyphens — task-1-mutant-4.patch
Mutant 5: specs/slugs.md:7, test_slugify_collapses_long_space_run — runs collapse only up to two — task-1-mutant-5.patch
Mutant 6: specs/slugs.md:7, test_slugify_leading_and_trailing_runs_become_one_hyphen — edges stripped — task-1-mutant-6.patch

Keeps: test_slugify_lowercases — lowercasing of letters, which slugify did before the task and still does
Keeps: test_slugify_single_space_becomes_one_hyphen — a lone space becomes one hyphen, as before the task
