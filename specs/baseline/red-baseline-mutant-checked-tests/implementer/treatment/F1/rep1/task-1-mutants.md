# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/picker.md:7 | two reports, later in name order | test_latest_report_returns_the_latest_dated_report |
| specs/picker.md:7 | dates across year/month boundaries, three reports | test_date_is_compared_as_a_date_not_by_file_order |
| specs/picker.md:7 | same month, different days | test_reports_in_the_same_month_are_ordered_by_day |
| specs/picker.md:7 | date line first or last | test_date_line_may_come_before_other_lines |
| specs/picker.md:8 | latest report first in name order | test_file_names_carry_no_order |
| brief: .txt file directly in folder | non-txt, nested | test_only_txt_files_directly_in_the_folder_count |

## Mutants

Mutant 1: specs/picker.md:7, test_latest_report_returns_the_latest_dated_report — picks earliest — task-1-mutant-1.patch
Mutant 2: brief: directly in folder, test_only_txt_files_directly_in_the_folder_count — recursive glob — task-1-mutant-2.patch
Mutant 3: brief: .txt, test_only_txt_files_directly_in_the_folder_count — any extension — task-1-mutant-3.patch
Mutant 4: specs/picker.md:8, test_file_names_carry_no_order — orders by file name — task-1-mutant-4.patch
Mutant 5: specs/picker.md:7, test_reports_in_the_same_month_are_ordered_by_day — drops the day — task-1-mutant-5.patch
