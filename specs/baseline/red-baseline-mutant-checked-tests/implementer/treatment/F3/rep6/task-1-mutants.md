# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at line start | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment | test_count_words_skips_indented_comment_lines |
| specs/wordcount.md:7 | # not first non-blank | test_count_words_hash_not_first_is_not_comment |
| specs/wordcount.md:7 | # directly followed by text | test_count_words_hash_without_space_is_comment |
| specs/wordcount.md:8 | runs of spaces/tabs/newlines | test_count_words_separated_by_any_whitespace_run |
| specs/wordcount.md:8 | empty / blank | test_count_words_empty_and_blank |

## Mutants

Mutant 1: specs/wordcount.md:7, test_count_words_skips_indented_comment_lines — indent not stripped before comment check — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:8, test_count_words_separated_by_any_whitespace_run — split on single space only — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:7, test_count_words_hash_not_first_is_not_comment — any '#' makes a comment — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_count_words_skips_comment_lines — comments not skipped — task-1-mutant-4.patch
Mutant 5: specs/wordcount.md:8, test_count_words_separated_by_any_whitespace_run — counts lines, not words — task-1-mutant-5.patch
