# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at line start | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment (spaces/tab) | test_indented_comment_line_is_skipped |
| specs/wordcount.md:7 | # after first non-blank | test_hash_after_first_non_blank_is_not_a_comment |
| specs/wordcount.md:7 | only comments, no trailing newline | test_only_comments_has_no_words |
| specs/wordcount.md:8 | runs of spaces/tabs | test_words_split_on_any_whitespace_run |
| specs/wordcount.md:8 | blank lines, newlines | test_words_split_across_lines_and_blank_lines |
| specs/wordcount.md:8 | empty | test_empty_text_has_no_words |

## Mutants

Mutant 1: specs/wordcount.md:7, test_indented_comment_line_is_skipped — comment must start at column 0 — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:7, test_hash_after_first_non_blank_is_not_a_comment — any '#' makes the line a comment — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:8, test_words_split_on_any_whitespace_run — split only on single spaces — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_only_comments_has_no_words — a comment stops counting altogether — task-1-mutant-4.patch
Mutant 5: specs/wordcount.md:7, test_indented_comment_line_is_skipped — only spaces are stripped, not tabs — task-1-mutant-5.patch
