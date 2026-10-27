#!/usr/bin/env bash
# The nine commit lints that CLAUDE.md lists under Commands. Fails closed: exit 1
# when any check fails or cannot run. Runs every check, then names the failures.
# Run by build/githooks/pre-commit and by .github/workflows/lints.yml.
set -uo pipefail
root="$(git rev-parse --show-toplevel)" || exit 1
cd "$root" || exit 1
# Git exports GIT_DIR, GIT_INDEX_FILE and the like to hooks; a check that runs
# git in another repository must not inherit them.
unset $(git rev-parse --local-env-vars)
failed=()
run() {
  local name="$1"
  shift
  echo "== $name"
  if ! "$@"; then
    failed+=("$name")
  fi
}
run check_frontmatter uv run --with pyyaml python build/check_frontmatter.py
run check_provenance uv run python build/check_provenance.py
run check_snippets uv run python build/check_snippets.py skills/
run check_conformance uv run --with pyyaml python build/check_conformance.py
run declared_dependencies bash -c 'cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies'
run sync_runtime_assets uv run --with pyyaml python build/sync_runtime_assets.py --check
run cc_guide_lint uv run python build/cc_guide/cli.py lint
run critical_placement bash -c 'cd build && uv run --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill'
run suite_registry uv run python build/run_suites.py --check
if [ "${#failed[@]}" -gt 0 ]; then
  echo "commit lints failed: ${failed[*]}" >&2
  exit 1
fi
echo 'commit lints passed'
