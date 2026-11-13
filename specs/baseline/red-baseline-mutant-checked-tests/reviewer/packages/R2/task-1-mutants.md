# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | `#` at column 0 | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | spaces before `#` | test_count_words_skips_a_comment_after_spaces |
| specs/wordcount.md:7 | a tab before `#` | test_count_words_skips_a_comment_after_a_tab |
| specs/wordcount.md:7 | no blank after `#` | test_count_words_skips_a_comment_with_no_blank_after_the_hash |
| specs/wordcount.md:7 | a comment on the last line, with no newline after it | test_count_words_skips_a_comment_on_the_last_line |
| specs/wordcount.md:7 | `#` after a word, so not the first non-blank character | test_count_words_counts_a_hash_after_a_word |
| specs/wordcount.md:8 | one space | test_count_words_skips_comment_lines |
| specs/wordcount.md:8 | a run of spaces | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a tab | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a run of spaces and tabs | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a newline | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a blank line, so two newlines in a row | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a carriage return before a newline | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | whitespace at the start and end of a line | test_count_words_ignores_whitespace_at_the_ends |
| specs/wordcount.md:8 | empty text, and whitespace only | test_count_words_ignores_whitespace_at_the_ends |

## Mutants

Mutant 1: test_count_words_splits_on_any_run_of_whitespace, test_count_words_ignores_whitespace_at_the_ends — returns 0 at the top of `count_words` — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:7, test_count_words_skips_comment_lines, test_count_words_skips_a_comment_after_spaces, test_count_words_skips_a_comment_after_a_tab, test_count_words_skips_a_comment_with_no_blank_after_the_hash, test_count_words_skips_a_comment_on_the_last_line — comment lines are not skipped, so their words count — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:7, test_count_words_counts_a_hash_after_a_word — a line with `#` anywhere in it is skipped as a comment — task-1-mutant-3.patch
