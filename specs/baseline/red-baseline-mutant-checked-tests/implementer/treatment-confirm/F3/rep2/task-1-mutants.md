# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at line start | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment | test_indented_comment_line_is_skipped |
| specs/wordcount.md:7 | `#` directly followed by word | test_comment_marker_without_space_is_skipped |
| specs/wordcount.md:7 | `#` mid-line (not a comment) | test_hash_mid_line_is_not_a_comment |
| specs/wordcount.md:7 | only comments | test_comment_only_text_has_no_words |
| specs/wordcount.md:8 | multiple spaces, tabs, newline runs | test_words_split_on_any_whitespace_run |
| specs/wordcount.md:8 | empty / blank text | test_empty_and_blank_text_has_no_words |

## Mutants

Mutant 1: specs/wordcount.md:7, test_indented_comment_line_is_skipped — indentation not stripped before comment check — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:8, test_words_split_on_any_whitespace_run — split on single space only — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:7, test_count_words_skips_comment_lines — comment lines not skipped — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_hash_mid_line_is_not_a_comment — any '#' makes a comment — task-1-mutant-4.patch
Mutant 5: specs/wordcount.md:7, test_comment_marker_without_space_is_skipped — comment detected by trailing '#' instead — task-1-mutant-5.patch
