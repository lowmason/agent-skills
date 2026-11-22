# Helpers for the fixtures' setup.sh scripts. Source it. bash 3.2.
# run_reps.sh runs setup.sh from the rep's repository, under the rep's own `env -i` environment, with
# REPO, BASE, WORKSPACE, SKILL, FIXTURES and VENV_PY set. A commit takes the repository's own user,
# Developer <developer@example.invalid>. Each seeded run is the real mutant-run of the skill copy, on
# the brief's focused command, and setup.sh exits 1 when a run does not give the result its fixture
# expects, so run_reps.sh records a kit error and runs no rep.
set -u
if [ -x "$SKILL/scripts/mutant-run" ]; then
  SDD="$SKILL"
else
  SDD="$SKILL/subagent-driven-development"
fi
MUTANT_RUN="$SDD/scripts/mutant-run"

fail() {
  echo "setup: $*" >&2
  exit 1
}

commit() {
  git add -A && git commit -q -m "$1" || fail "commit failed: $1"
}

# expect_pass COUNT TESTS: the focused command on TESTS passes with COUNT passed.
expect_pass() {
  local out
  out=$("$VENV_PY" -m pytest -q "$2" 2>&1) || fail "the tests failed: $out"
  case "$out" in
    *"$1 passed"*) ;;
    *) fail "expected $1 passed: $out" ;;
  esac
}

# make_patch K FILE MUTATED: mutant K's patch is `git diff` of MUTATED over FILE; git checkout restores FILE.
make_patch() {
  cp "$3" "$2" && git diff -- "$2" > "$WORKSPACE/task-1-mutant-$1.patch" && git checkout -q -- "$2" \
    || fail "patch $1 failed"
  [ -s "$WORKSPACE/task-1-mutant-$1.patch" ] || fail "patch $1 is empty"
}

# seed_run MODE WANT NAME TESTS PATTERN...: mutant-run, with --screen when MODE is screen, on the focused
# command for TESTS. Fails unless it exits WANT and writes NAME, and NAME has a line for each PATTERN (ERE).
seed_run() {
  local mode="$1" want="$2" name="$3" tests="$4" status=0 pattern
  shift 4
  if [ "$mode" = screen ]; then
    "$MUTANT_RUN" --screen plan.md 1 "$BASE" -- "$VENV_PY" -m pytest -q "$tests" || status=$?
  else
    "$MUTANT_RUN" plan.md 1 "$BASE" -- "$VENV_PY" -m pytest -q "$tests" || status=$?
  fi
  [ "$status" -eq "$want" ] || fail "$name: mutant-run exited $status, not $want"
  [ -f "$WORKSPACE/$name" ] || fail "$name was not written"
  for pattern in "$@"; do
    grep -qE "$pattern" "$WORKSPACE/$name" || fail "$name has no line that matches: $pattern"
  done
}

# fill TEMPLATE NAME: TEMPLATE with @RUN_FILE@ as run file NAME's path and @COUNTS@ as its result: counts.
fill() {
  local counts
  counts=$(sed -n 's/^result: //p' "$WORKSPACE/$2" | head -n 1)
  [ -n "$counts" ] || fail "$2 has no result: line"
  sed -e "s|@RUN_FILE@|$WORKSPACE/$2|g" -e "s|@COUNTS@|$counts|g" "$1"
}

# ledger: the inline ledger, with no line for Task 1.
ledger() {
  printf 'Plan: %s\nPre-flight: no shared interfaces\n' "$REPO/plan.md" > "$WORKSPACE/progress.md"
}
