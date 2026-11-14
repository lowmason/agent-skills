# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | run of spaces (2) | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | single space | test_slugify_single_space |
| specs/slugs.md:7 | long run | test_slugify_collapses_long_run |
| specs/slugs.md:7 | mixed whitespace run | test_slugify_collapses_mixed_whitespace_runs |
| specs/slugs.md:7 | tab/newline singly | test_slugify_whitespace_other_than_space |
| specs/slugs.md:7 | run at start/end | test_slugify_run_at_edges_is_one_hyphen |
| specs/slugs.md:8 | uppercase | test_slugify_lowercases, test_slugify_lowercases_across_words |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_whitespace_other_than_space — only spaces are matched, not other whitespace — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_space_runs — each whitespace char gets its own hyphen — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — lowercasing dropped — task-1-mutant-3.patch
Mutant 4: specs/slugs.md:7, test_slugify_run_at_edges_is_one_hyphen — edges stripped — task-1-mutant-4.patch
Keeps: test_slugify_lowercases — lowercasing of letters, behavior from before the task that the task keeps
Keeps: test_slugify_single_space — a single space becomes one hyphen, behavior from before the task that the task keeps
