#!/usr/bin/env bash
# Bisection script to find which test creates unwanted files/state
# Usage: ./find-polluter.sh <file_or_dir_to_check> <test_pattern>
# Example: ./find-polluter.sh 'packages/core/.git' '*/test_*.py'
#
# Test runner: defaults to `pytest`. Override with the TEST_CMD env var for
# another stack — the matched test file is appended as the final argument:
#   TEST_CMD=pytest        ./find-polluter.sh 'packages/core/.git' '*/test_*.py'   # default
#   TEST_CMD='npm test'    ./find-polluter.sh 'packages/core/.git' 'src/**/*.test.ts'
#   TEST_CMD='go test'     ./find-polluter.sh 'packages/core/.git' '*_test.go'
#
# The pattern is matched with find -path from the current directory, with or
# without a leading ./. Each '**/' may also match no directory, but with
# several only the all-or-none variants are tried: run mixed ones separately.
#
# Exit status: 1 when a test creates the pollution (or on a usage error), 2
# when no test file matches the pattern, so no test ran, 3 when the pollution
# already exists, so no test can be blamed for it, 0 when every test ran
# clean. Only a 0 prints the all-clear.

set -e

if [ $# -ne 2 ]; then
  echo "Usage: $0 <file_to_check> <test_pattern>"
  echo "Example: $0 'packages/core/.git' '*/test_*.py'"
  echo "Override the runner with TEST_CMD (default: pytest)"
  exit 1
fi

POLLUTION_CHECK="$1"
TEST_PATTERN="$2"
TEST_CMD="${TEST_CMD:-pytest}"

echo "🔍 Searching for test that creates: $POLLUTION_CHECK"
echo "Test pattern: $TEST_PATTERN"
echo "Test command: $TEST_CMD"
echo ""

# Get list of test files (find . emits ./-prefixed paths, so accept the
# pattern written with or without a leading ./)
TEST_PATTERN="${TEST_PATTERN#./}"
# find -path can't match '**/' against zero directory levels, so a pattern
# like src/**/*.test.ts would skip src/top.test.ts; also try the pattern
# with '**/' collapsed to cover files directly under the base directory.
# The bare pattern, as this script matched it before, stays a third
# alternative: a leading '*' still takes the '.', so '*/test_*.py' keeps
# finding a top-level ./test_x.py, which the ./ prefix alone would drop.
TEST_FILES=$(find . \( -path "./$TEST_PATTERN" -o -path "./${TEST_PATTERN//\*\*\//}" -o -path "$TEST_PATTERN" \) | sort -u)
if [ -z "$TEST_FILES" ]; then
  # An empty result is no files, not one, and nothing ran: never fall
  # through to the all-clear below.
  echo "Found 0 test files"
  echo ""
  echo "❌ No test files match that pattern, so no test ran. This is not an all-clear."
  echo "   find -path matches it from this directory, as in 'src/**/*.test.ts' or '*/test_*.py'."
  exit 2
fi
TOTAL=$(printf '%s\n' "$TEST_FILES" | wc -l | tr -d ' ')

echo "Found $TOTAL test files"
echo ""

# Pollution that exists before the first test has no polluter to find, and a
# run that skipped every test must not end on the all-clear.
if [ -e "$POLLUTION_CHECK" ]; then
  echo "❌ $POLLUTION_CHECK already exists before any test ran, so no test can be blamed for creating it."
  echo "   Confirm it is leftover pollution before you remove it. If it belongs there, as a"
  echo "   repository's own .git does at its root, check a path that should not exist instead"
  echo "   (for example packages/core/.git). This is not an all-clear."
  exit 3
fi

COUNT=0
for TEST_FILE in $TEST_FILES; do
  COUNT=$((COUNT + 1))

  # Pollution that appears between two tests (a test that left a background
  # process) cannot be blamed on either one. Stop rather than skip on.
  if [ -e "$POLLUTION_CHECK" ]; then
    echo "❌ $POLLUTION_CHECK appeared before test $COUNT/$TOTAL, after the previous test's check."
    echo "   A background process may have created it. This is not an all-clear."
    exit 3
  fi

  echo "[$COUNT/$TOTAL] Testing: $TEST_FILE"

  # Run the test
  $TEST_CMD "$TEST_FILE" > /dev/null 2>&1 || true

  # Check if pollution appeared
  if [ -e "$POLLUTION_CHECK" ]; then
    echo ""
    echo "🎯 FOUND POLLUTER!"
    echo "   Test: $TEST_FILE"
    echo "   Created: $POLLUTION_CHECK"
    echo ""
    echo "Pollution details:"
    ls -la "$POLLUTION_CHECK"
    echo ""
    echo "To investigate:"
    echo "  $TEST_CMD $TEST_FILE    # Run just this test"
    echo "  cat $TEST_FILE         # Review test code"
    exit 1
  fi
done

echo ""
echo "✅ No polluter found - all tests clean!"
exit 0
