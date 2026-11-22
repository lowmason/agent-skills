Plan: /private/tmp/msr104/rep5/repo/plan.md
Pre-flight: no shared interfaces
Task 1: Ruling: added test_each_cent_left_over_goes_to_a_different_person (split(1100, 3) == [367, 367, 366]) beyond the brief, plan tests untouched — mutant 2 (first person pays every cent left over) survived because the plan tests only cover one cent left over, and specs/split.md:9 says "one each" — if wrong, one extra test asserts behavior the spec already states
Task 1: complete (commits 395d750..5f98ddc, mutants: 3/3, tests: /private/tmp/msr104-venv/bin/python -m pytest -q → 3 passed in 0.00s)
