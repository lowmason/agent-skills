# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | `#` at column 0 | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | spaces before `#` | test_count_words_skips_a_comment_after_spaces |
| specs/wordcount.md:7 | a tab before `#` | test_count_words_skips_a_comment_after_a_tab_or_other_blank |
| specs/wordcount.md:7 | other whitespace before `#`: a form feed, a vertical tab, a lone `\r`, `\x1c` to `\x1e`, `\x85`, `\u2028`, `\u2029`, the no-break space `\u00a0`, the ideographic space `\u3000` | test_count_words_skips_a_comment_after_a_tab_or_other_blank |
| specs/wordcount.md:7 | no blank after `#` | test_count_words_skips_a_comment_with_no_blank_after_the_hash |
| specs/wordcount.md:7 | a line that is only `#` | test_count_words_skips_a_comment_with_no_blank_after_the_hash |
| specs/wordcount.md:7 | a comment on the last line, with no newline after it | test_count_words_skips_a_comment_on_the_last_line |
| specs/wordcount.md:7 | several comment lines in a row, and text that is only comments | test_count_words_skips_several_comment_lines |
| specs/wordcount.md:7 | a comment line that ends with `\r\n` | test_count_words_skips_a_comment_line_that_ends_with_crlf |
| specs/wordcount.md:7 | other whitespace inside a comment line (a vertical tab, a form feed, a lone `\r`, `\x85`, `\u2028`): only a newline ends the line | test_count_words_skips_a_whole_comment_line_past_other_whitespace |
| specs/wordcount.md:7 | `#` after a word, so not the first non-blank character | test_count_words_counts_a_hash_after_a_word |
| specs/wordcount.md:7 | `#` after a word and a form feed, a lone `\r` or `\u2028` in the same line | test_count_words_counts_a_hash_after_other_whitespace_in_a_line |
| specs/wordcount.md:8 | one space | test_count_words_skips_comment_lines |
| specs/wordcount.md:8 | a run of spaces | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a tab | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a run of spaces and tabs | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a newline | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a blank line, so two newlines in a row | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a carriage return before a newline | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | punctuation with no whitespace (`well-known`, `a,b`): it never separates words | test_count_words_splits_on_any_run_of_whitespace |
| specs/wordcount.md:8 | a vertical tab, a form feed or a lone `\r` between words: each separates words and never ends a line | test_count_words_splits_on_other_whitespace_inside_a_line |
| specs/wordcount.md:8 | other Unicode whitespace between words (`\x1c` to `\x1e`, `\x85`, `\u2028`, `\u2029`, the no-break space `\u00a0`, the ideographic space `\u3000`) | test_count_words_splits_on_other_whitespace_inside_a_line |
| specs/wordcount.md:8 | whitespace at the start and end of a line, Unicode whitespace too (`\u3000`, `\x85`) | test_count_words_ignores_whitespace_at_the_ends |
| specs/wordcount.md:8 | empty text, and whitespace only | test_count_words_ignores_whitespace_at_the_ends |

## Mutants

Mutant 1: specs/wordcount.md:8, test_count_words_splits_on_any_run_of_whitespace, test_count_words_splits_on_other_whitespace_inside_a_line, test_count_words_ignores_whitespace_at_the_ends — splits each line on single spaces, not on any run of whitespace — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:7, test_count_words_skips_comment_lines, test_count_words_skips_a_comment_after_spaces, test_count_words_skips_a_comment_after_a_tab_or_other_blank, test_count_words_skips_a_comment_with_no_blank_after_the_hash, test_count_words_skips_a_comment_on_the_last_line, test_count_words_skips_several_comment_lines, test_count_words_skips_a_comment_line_that_ends_with_crlf, test_count_words_skips_a_whole_comment_line_past_other_whitespace — comment lines are not skipped, so their words count — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:7, test_count_words_counts_a_hash_after_a_word, test_count_words_counts_a_hash_after_other_whitespace_in_a_line — a line with `#` anywhere in it is skipped as a comment — task-1-mutant-3.patch
