#!/bin/bash
# E1: the GREEN commit and the ledger, at the start of the mutant step.
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/../seed_lib.sh"
SEED="$HERE/seed"
FOCUS=tests/test_tickets.py
mkdir -p tests && cp "$SEED/tickets.py" tickets.py && cp "$SEED/plan_tests.py" "$FOCUS" || fail 'copy failed'
expect_pass 2 "$FOCUS"
commit 'Add ticket prices'
ledger
