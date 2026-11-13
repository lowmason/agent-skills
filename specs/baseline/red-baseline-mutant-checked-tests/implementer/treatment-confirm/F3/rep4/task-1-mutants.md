# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at line start | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment | test_indented_comment_line_is_skipped |
| specs/wordcount.md:7 | # after a word (not comment) | test_hash_after_a_word_is_not_a_comment |
| specs/wordcount.md:7 | only comments | test_only_comments_count_zero |
| specs/wordcount.md:8 | runs of spaces/tabs | test_words_separated_by_runs_of_whitespace |
| specs/wordcount.md:8 | empty/blank | test_empty_and_blank_text_has_no_words |

## Mutants

Mutant 1: specs/wordcount.md:7, test_indented_comment_line_is_skipped — comment check without lstrip — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:7, test_hash_after_a_word_is_not_a_comment — any '#' makes line a comment — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:8, test_words_separated_by_runs_of_whitespace — split on single space only — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_count_words_skips_comment_lines — comments are not skipped — task-1-mutant-4.patch
