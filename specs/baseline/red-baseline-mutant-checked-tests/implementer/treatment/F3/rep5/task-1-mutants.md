# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/wordcount.md:7 | comment at column 0 | test_count_words_skips_comment_lines |
| specs/wordcount.md:7 | indented comment | test_count_words_skips_indented_comment_line |
| specs/wordcount.md:7 | # not first non-blank | test_count_words_counts_hash_inside_a_line |
| specs/wordcount.md:7 | only comments / comment without trailing newline | test_count_words_only_comments |
| specs/wordcount.md:8 | runs of spaces and tabs | test_count_words_splits_on_any_whitespace_run |
| specs/wordcount.md:8 | empty / blank text | test_count_words_empty_and_blank_text |

## Mutants

Mutant 1: specs/wordcount.md:7, test_count_words_skips_indented_comment_line — indentation not stripped before comment check — task-1-mutant-1.patch
Mutant 2: specs/wordcount.md:8, test_count_words_splits_on_any_whitespace_run — split on single space only — task-1-mutant-2.patch
Mutant 3: specs/wordcount.md:7, test_count_words_counts_hash_inside_a_line — any line containing '#' is a comment — task-1-mutant-3.patch
Mutant 4: specs/wordcount.md:7, test_count_words_skips_comment_lines — comment stops counting everything after (break) — task-1-mutant-4.patch
Mutant 5: specs/wordcount.md:8, test_count_words_empty_and_blank_text — blank lines count as one word — task-1-mutant-5.patch
