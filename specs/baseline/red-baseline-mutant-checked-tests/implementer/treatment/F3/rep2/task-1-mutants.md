# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at column 0 | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment | test_count_words_skips_indented_comment_lines |
| specs/wordcount.md:7 | # mid-line is not a comment | test_count_words_hash_mid_line_is_not_a_comment |
| specs/wordcount.md:7 | comment-only / empty | test_count_words_empty_and_comment_only |
| specs/wordcount.md:8 | tabs, multiple spaces, blank lines, no trailing newline | test_count_words_splits_on_any_whitespace_run |

## Mutants

Mutant 1: specs/wordcount.md:7, test_count_words_skips_indented_comment_lines — indentation not stripped before comment check — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:8, test_count_words_splits_on_any_whitespace_run — split only on single space — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:7, test_count_words_hash_mid_line_is_not_a_comment — any line containing # skipped — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_count_words_skips_comment_lines, test_count_words_empty_and_comment_only — first line dropped instead of comment lines — task-1-mutant-4.patch
