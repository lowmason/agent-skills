# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at line start | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment | test_indented_comment_line_is_skipped |
| specs/wordcount.md:7 | # after words is not a comment | test_hash_after_words_is_not_a_comment |
| specs/wordcount.md:7 | only comments / no space after # | test_only_comments |
| specs/wordcount.md:7 | comment ended by CR / CRLF | test_comment_ends_at_any_line_break |
| specs/wordcount.md:8 | spaces, tabs, mixed runs, CRLF | test_words_separated_by_any_whitespace_run |
| specs/wordcount.md:8 | empty and blank text | test_empty_and_blank_text |

## Mutants

Mutant 1: specs/wordcount.md:7, test_indented_comment_line_is_skipped — no lstrip before startswith — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:7, test_hash_after_words_is_not_a_comment — any '#' in line makes comment — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:8, test_words_separated_by_any_whitespace_run — split on single space only — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_comment_ends_at_any_line_break — split lines on "\n" only (bare CR not a line break) — task-1-mutant-4.patch
Mutant 5: specs/wordcount.md:7, test_count_words_skips_comment_lines — comment lines not skipped — task-1-mutant-5.patch
