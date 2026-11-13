# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at line start | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment | test_indented_comment_line_is_skipped |
| specs/wordcount.md:7 | # after a word is not a comment | test_hash_after_first_word_is_not_a_comment |
| specs/wordcount.md:7 | comment-only / empty input | test_comment_only_and_empty_input_count_zero |
| specs/wordcount.md:8 | runs of spaces, tabs, blank lines | test_words_separated_by_any_whitespace_run |

## Mutants

Mutant 1: specs/wordcount.md:7, test_indented_comment_line_is_skipped — leading blanks not stripped before the # check — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:7, test_hash_after_first_word_is_not_a_comment — any # in line makes it a comment — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:8, test_words_separated_by_any_whitespace_run — split on single space only — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_count_words_skips_comment_lines — comment lines are still counted — task-1-mutant-4.patch
