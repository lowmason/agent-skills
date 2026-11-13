# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at column 0 | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment | test_indented_comment_line_is_skipped |
| specs/wordcount.md:7 | # after first non-blank | test_hash_after_first_non_blank_is_not_a_comment |
| specs/wordcount.md:7 | words after comment line | test_count_words_skips_comment_lines |
| specs/wordcount.md:8 | tabs and runs | test_words_separated_by_any_whitespace_run |
| specs/wordcount.md:8 | empty / blank | test_empty_and_blank_text_has_no_words |
| specs/wordcount.md:8 | multi-line | test_words_across_lines_are_counted |

## Mutants

Mutant 1: specs/wordcount.md:7, test_indented_comment_line_is_skipped — indentation not stripped before comment check — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:7, test_hash_after_first_non_blank_is_not_a_comment — any '#' makes a comment — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:8, test_words_separated_by_any_whitespace_run — split only on single space — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_count_words_skips_comment_lines — comment stops counting instead of skipping the line — task-1-mutant-4.patch
Mutant 5: specs/wordcount.md:8, test_empty_and_blank_text_has_no_words — blank lines count as a word — task-1-mutant-5.patch
