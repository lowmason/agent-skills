# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at line start | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment | test_count_words_skips_indented_comment_lines |
| specs/wordcount.md:7 | # after first word is not a comment | test_count_words_counts_hash_after_first_word |
| specs/wordcount.md:7 | comment-only text, last line unterminated | test_count_words_comment_only_and_last_line_without_newline |
| specs/wordcount.md:8 | tabs and multiple spaces, across lines | test_count_words_splits_on_runs_of_mixed_whitespace |
| specs/wordcount.md:8 | empty / blank text | test_count_words_empty_and_blank_text |

## Mutants

Mutant 1: specs/wordcount.md:7, test_count_words_skips_indented_comment_lines — indent not stripped before checking '#' — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:8, test_count_words_splits_on_runs_of_mixed_whitespace — split on single space only — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:7, test_count_words_counts_hash_after_first_word — any '#' in line makes a comment — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_count_words_skips_comment_lines — comments never skipped — task-1-mutant-4.patch
Mutant 5: specs/wordcount.md:8, test_count_words_skips_comment_lines — total overwritten per line instead of summed — task-1-mutant-5.patch
