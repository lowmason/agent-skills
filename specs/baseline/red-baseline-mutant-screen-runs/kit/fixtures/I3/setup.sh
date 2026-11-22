#!/bin/bash
# I3: the GREEN commit, mutant 1 and the first screen, clean, whose revert section lists the plan test as passed.
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/../seed_lib.sh"
SEED="$HERE/seed"
FOCUS=tests/test_loyalty.py
mkdir -p tests && cp "$SEED/loyalty.py" loyalty.py && cp "$SEED/plan_tests.py" "$FOCUS" || fail 'copy failed'
expect_pass 1 "$FOCUS"
commit 'Give double points from 100 dollars'
make_patch 1 loyalty.py "$SEED/mutant_1.py"
cp "$SEED/mutants.md" "$WORKSPACE/task-1-mutants.md" || fail 'copy failed'
seed_run screen 0 task-1-screen.log "$FOCUS" '^result: caught 1, survived 0, invalid 0$' \
  '^screen: carried 0 of 1 from earlier runs$' '^passed tests\.test_loyalty::test_double_points_from_100_dollars$'
