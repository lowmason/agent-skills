#!/bin/bash
# E2: the GREEN commit, three mutants, the first mutant run (no --screen) with one survivor, mutant 2,
# and a ledger with no line for Task 1.
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/../seed_lib.sh"
SEED="$HERE/seed"
FOCUS=tests/test_bills.py
mkdir -p tests && cp "$SEED/bills.py" bills.py && cp "$SEED/plan_tests.py" "$FOCUS" || fail 'copy failed'
expect_pass 2 "$FOCUS"
commit 'Add bill splits'
make_patch 1 bills.py "$SEED/mutant_1.py"
make_patch 2 bills.py "$SEED/mutant_2.py"
make_patch 3 bills.py "$SEED/mutant_3.py"
cp "$SEED/mutants.md" "$WORKSPACE/task-1-mutants.md" || fail 'copy failed'
seed_run full 1 task-1-mutants.log "$FOCUS" '^result: caught 2, survived 1, invalid 0$' '^mutant 2: SURVIVED ' \
  '^mutant 1: CAUGHT ' '^mutant 3: CAUGHT '
ledger
