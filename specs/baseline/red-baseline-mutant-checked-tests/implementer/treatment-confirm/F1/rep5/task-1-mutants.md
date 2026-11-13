# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/picker.md:7 | two reports, later is second | test_latest_report_returns_the_latest_dated_report |
| specs/picker.md:7 | dates differing in year/month/day | test_dates_compare_across_years_and_months |
| specs/picker.md:7 | date line not first | test_date_line_may_be_anywhere_in_the_file |
| specs/picker.md:8 | latest report has alphabetically first name | test_file_names_carry_no_order |
| brief: .txt file directly in folder | other extension, subfolder | test_only_txt_files_directly_in_the_folder_are_reports |
| brief: .txt file directly in folder | directory named *.txt | test_a_directory_named_like_a_report_is_skipped |

## Mutants

Mutant 1: specs/picker.md:8, test_file_names_carry_no_order — picks by file name — task-1-mutant-1.patch
Mutant 2: specs/picker.md:7, test_latest_report_returns_the_latest_dated_report — picks earliest — task-1-mutant-2.patch
Mutant 3: brief: .txt only, test_only_txt_files_directly_in_the_folder_are_reports — any extension — task-1-mutant-3.patch
Mutant 4: brief: directly in folder, test_only_txt_files_directly_in_the_folder_are_reports — recursive — task-1-mutant-4.patch
Mutant 5: brief: directly in folder, test_a_directory_named_like_a_report_is_skipped — directories not filtered — task-1-mutant-5.patch
Mutant 6: specs/picker.md:7, test_dates_compare_across_years_and_months — year ignored — task-1-mutant-6.patch
