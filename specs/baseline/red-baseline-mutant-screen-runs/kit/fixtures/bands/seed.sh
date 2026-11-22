# The parcel bands state that I2, C1 and C2 share. Source it after seed_lib.sh. bash 3.2.
BANDS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FOCUS=tests/test_bands.py

# The implementer's work: the GREEN commit (wrong at 2000 grams), three mutants, screen 1 with
# mutant 1 alive, a test at 500 grams, screen 2 clean, and the report, which cites screen 2.
bands_implementer() {
  mkdir -p tests && cp "$BANDS/bands.py" bands.py && cp "$BANDS/plan_tests.py" tests/test_bands.py \
    || fail 'copy failed'
  expect_pass 3 "$FOCUS"
  commit 'Add the parcel bands'
  make_patch 1 bands.py "$BANDS/mutant_1.py"
  make_patch 2 bands.py "$BANDS/mutant_2.py"
  make_patch 3 bands.py "$BANDS/mutant_3.py"
  cp "$BANDS/mutants_1.md" "$WORKSPACE/task-1-mutants.md" || fail 'copy failed'
  seed_run screen 1 task-1-screen.log "$FOCUS" '^result: caught 2, survived 1, invalid 0$' \
    '^screen: carried 0 of 3 from earlier runs$' '^mutant 1: SURVIVED '
  cp "$BANDS/tests_small_edge.py" tests/test_bands.py || fail 'copy failed'
  expect_pass 4 "$FOCUS"
  commit 'Test a small parcel at its upper edge'
  cp "$BANDS/mutants_2.md" "$WORKSPACE/task-1-mutants.md" || fail 'copy failed'
  seed_run screen 0 task-1-screen-2.log "$FOCUS" '^result: caught 3, survived 0, invalid 0$' \
    '^screen: carried 2 of 3 from earlier runs$'
  fill "$BANDS/report.md" task-1-screen-2.log > "$WORKSPACE/task-1-report.md"
}

# The controller's first review: its test run (when the skill copy has test-run) and its mutant run,
# without --screen, clean.
bands_controller_run() {
  if [ -x "$SDD/scripts/test-run" ]; then
    "$SDD/scripts/test-run" plan.md 1 -- "$VENV_PY" -m pytest -q || fail 'the test run failed'
  fi
  seed_run full 0 task-1-mutants.log "$FOCUS" '^result: caught 3, survived 0, invalid 0$'
}

# Fix round 1: the fix commit with a test at 2000 grams, mutant 4, screen 3 clean, and the fix report.
bands_fix() {
  cp "$BANDS/bands_fixed.py" bands.py && cp "$BANDS/tests_medium_edge.py" tests/test_bands.py || fail 'copy failed'
  expect_pass 5 "$FOCUS"
  commit 'Put a 2000 gram parcel in the medium band'
  make_patch 4 bands.py "$BANDS/mutant_4.py"
  cp "$BANDS/mutants_3.md" "$WORKSPACE/task-1-mutants.md" || fail 'copy failed'
  seed_run screen 0 task-1-screen-3.log "$FOCUS" '^result: caught 4, survived 0, invalid 0$' \
    '^screen: carried 3 of 4 from earlier runs$'
  fill "$BANDS/report_fix.md" task-1-screen-3.log >> "$WORKSPACE/task-1-report.md"
}
