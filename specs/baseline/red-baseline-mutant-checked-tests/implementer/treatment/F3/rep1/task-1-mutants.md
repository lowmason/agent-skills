# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at column 0 | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment | test_indented_comment_line_is_skipped |
| specs/wordcount.md:7 | '#' not first non-blank | test_hash_after_first_word_is_not_a_comment |
| specs/wordcount.md:7 | '#' directly followed by text | test_hash_without_space_is_a_comment |
| specs/wordcount.md:7 | only comments / CRLF / following lines | test_comment_only_text_counts_zero, test_comment_line_with_carriage_return_is_skipped, test_comment_does_not_hide_following_lines |
| specs/wordcount.md:8 | runs of spaces, tabs, newlines, CRLF | test_any_run_of_whitespace_separates_words |
| specs/wordcount.md:8 | empty / blank text | test_empty_and_blank_text_counts_zero |

## Mutants

Mutant 1: specs/wordcount.md:7, test_indented_comment_line_is_skipped — indentation not stripped before the '#' check — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:7, test_hash_after_first_word_is_not_a_comment — any '#' in the line makes it a comment — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:8, test_any_run_of_whitespace_separates_words — split on single spaces only — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_comment_does_not_hide_following_lines — comment stops counting entirely — task-1-mutant-4.patch
Mutant 5: specs/wordcount.md:7, test_count_words_skips_comment_lines — comments never detected — task-1-mutant-5.patch
Mutant 6: specs/wordcount.md:7, test_hash_without_space_is_a_comment — only '# ' counts as comment — task-1-mutant-6.patch
Mutant 7: specs/wordcount.md:7, test_unicode_line_separator_does_not_end_a_comment_line — lines split with splitlines() so U+2028 ends a comment line — task-1-mutant-7.patch
