# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/picker.md:7 | later date in later-named file | test_latest_report_returns_the_latest_dated_report |
| specs/picker.md:7 | date line after other lines, year boundary | test_date_line_may_follow_other_lines_and_dates_compare_by_year_first |
| specs/picker.md:7 | non-.txt and nested files ignored | test_only_txt_files_directly_in_the_folder_count |
| specs/picker.md:8 | latest date in earlier-named file | test_file_names_carry_no_order |

## Mutants

Mutant 1: specs/picker.md:7, test_latest_report_returns_the_latest_dated_report — picks earliest date — task-1-mutant-1.patch
Mutant 2: specs/picker.md:7, test_only_txt_files_directly_in_the_folder_count — recursive glob — task-1-mutant-2.patch
Mutant 3: specs/picker.md:7, test_only_txt_files_directly_in_the_folder_count — any extension — task-1-mutant-3.patch
Mutant 4: specs/picker.md:8, test_file_names_carry_no_order — orders by file name — task-1-mutant-4.patch
Mutant 5: specs/picker.md:8, test_file_names_carry_no_order — last sorted name — task-1-mutant-5.patch
Mutant 6: specs/picker.md:7, test_date_line_may_follow_other_lines_and_dates_compare_by_year_first — compares day of month only — task-1-mutant-6.patch
