# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | two-space run | test_slugify_collapses_space_runs |
| specs/slugs.md:7 | single space | test_slugify_single_space |
| specs/slugs.md:7 | long run | test_slugify_long_space_run |
| specs/slugs.md:7 | tab / newline | test_slugify_collapses_other_whitespace |
| specs/slugs.md:7 | mixed run | test_slugify_collapses_mixed_whitespace_run |
| specs/slugs.md:7 | run at start/end | test_slugify_whitespace_run_at_ends_is_one_hyphen |
| specs/slugs.md:7 | several runs | test_slugify_collapses_each_run_separately |
| specs/slugs.md:8 | lowercase | test_slugify_lowercases |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_collapses_space_runs — each space is its own hyphen again — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_other_whitespace — only spaces collapse, not tabs/newlines — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — no lowercasing — task-1-mutant-3.patch
Mutant 4: specs/slugs.md:7, test_slugify_single_space — whitespace removed instead of hyphenated — task-1-mutant-4.patch
Keeps: test_slugify_lowercases — lowercasing, which worked before the task and is kept
Keeps: test_slugify_single_space — a single space becoming one hyphen, which worked before the task and is kept
