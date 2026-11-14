# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/slugs.md:7 | single space | test_slugify_single_space_becomes_one_hyphen |
| specs/slugs.md:7 | run of spaces (2, many) | test_slugify_collapses_space_runs, test_slugify_collapses_long_space_run |
| specs/slugs.md:7 | tab / newline runs | test_slugify_collapses_non_space_whitespace_runs |
| specs/slugs.md:7 | mixed whitespace run | test_slugify_collapses_mixed_whitespace_run |
| specs/slugs.md:7 | run at start/end | test_slugify_collapses_runs_at_the_edges |
| specs/slugs.md:7 | several runs | test_slugify_collapses_each_run_separately |
| specs/slugs.md:8 | letters lowercased | test_slugify_lowercases, test_slugify_lowercases_every_letter |

## Mutants

Mutant 1: specs/slugs.md:7, test_slugify_collapses_space_runs — pattern ' +' so only spaces collapse, no tabs/newlines — task-1-mutant-1.patch
Mutant 2: specs/slugs.md:7, test_slugify_collapses_space_runs — pattern \s, runs not collapsed — task-1-mutant-2.patch
Mutant 3: specs/slugs.md:8, test_slugify_lowercases — lowercasing dropped — task-1-mutant-3.patch
Mutant 4: specs/slugs.md:7, test_slugify_collapses_mixed_whitespace_run — pattern [ \t]+ misses newlines — task-1-mutant-4.patch
Mutant 5: specs/slugs.md:7, test_slugify_collapses_runs_at_the_edges — result is stripped — task-1-mutant-5.patch
Keeps: test_slugify_lowercases — letters were already lowercased before the task and the task keeps that (specs/slugs.md:8)
Keeps: test_slugify_single_space_becomes_one_hyphen — a single space already became one hyphen before the task and still does
