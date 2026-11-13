# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/picker.md:7 | two reports, later date has later name | test_latest_report_returns_the_latest_dated_report |
| specs/picker.md:7 | three reports, date order differs from name order | test_file_names_carry_no_order |
| specs/picker.md:7 | date: line not first | test_date_line_need_not_be_first |
| specs/picker.md:8 | names opposed to date order | test_file_names_carry_no_order |
| brief: .txt file directly in folder | non-.txt file, nested file | test_only_txt_files_directly_in_folder_count |

## Mutants

Mutant 1: specs/picker.md:8, test_file_names_carry_no_order — picks max by path name — task-1-mutant-1.patch
Mutant 2: specs/picker.md:7, test_latest_report_returns_the_latest_dated_report — picks the earliest date — task-1-mutant-2.patch
Mutant 3: brief: directly in folder, test_only_txt_files_directly_in_folder_count — recurses into subfolders — task-1-mutant-3.patch
Mutant 4: brief: .txt file, test_only_txt_files_directly_in_folder_count — accepts any extension — task-1-mutant-4.patch
Mutant 5: specs/picker.md:7, test_date_line_need_not_be_first — never finds the date line — task-1-mutant-5.patch
