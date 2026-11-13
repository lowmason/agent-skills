# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/picker.md:7 | two reports, later one second | test_latest_report_returns_the_latest_dated_report |
| specs/picker.md:7 | date line not first; dates differ across month/year | test_date_line_need_not_be_first_and_dates_compare_as_dates |
| specs/picker.md:7 | only .txt files directly in folder | test_only_txt_files_directly_in_folder_count |
| specs/picker.md:8 | name order opposite to date order | test_file_names_carry_no_order |

## Mutants

Mutant 1: specs/picker.md:8, test_file_names_carry_no_order — picks by file name — task-1-mutant-1.patch
Mutant 2: specs/picker.md:7, test_latest_report_returns_the_latest_dated_report — returns earliest date — task-1-mutant-2.patch
Mutant 3: brief: directly in folder, test_only_txt_files_directly_in_folder_count — recursive glob — task-1-mutant-3.patch
Mutant 4: brief: .txt, test_only_txt_files_directly_in_folder_count — any extension — task-1-mutant-4.patch
Mutant 5: specs/picker.md:7, test_date_line_need_not_be_first_and_dates_compare_as_dates — compares only day of month — task-1-mutant-5.patch
Mutant 6: specs/picker.md:7, test_date_line_need_not_be_first_and_dates_compare_as_dates — only looks at first line for date — task-1-mutant-6.patch
