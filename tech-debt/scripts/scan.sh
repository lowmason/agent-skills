#!/usr/bin/env bash
# scan.sh — sweep a research/data repo for technical-debt signals.
#
# Prints a grouped, file:line report of the signals described in SKILL.md. Each
# hit is a *candidate*, not a verdict — the skill's triage step decides DELETE
# vs HARDEN. Read-only: it greps and lists, never edits.
#
# Usage:
#   scripts/scan.sh [ROOT]        # ROOT defaults to the current directory
#
# Designed for the user's stack (Polars / NumPyro / PyMC / BLS ETL → parquet).
# Tries ripgrep (rg) and falls back to grep -r so it runs anywhere.

set -uo pipefail
ROOT="${1:-.}"

if command -v rg >/dev/null 2>&1; then
  SEARCH() { rg -n --no-heading -S "$@" "$ROOT" 2>/dev/null; }
  FILES()  { rg --files "$ROOT" 2>/dev/null; }
else
  SEARCH() { grep -rnI "$@" "$ROOT" 2>/dev/null; }
  FILES()  { find "$ROOT" -type f 2>/dev/null; }
fi

section() { printf '\n========== %s ==========\n' "$1"; }

# --- Reproducibility / correctness risk -----------------------------------
section "Magic seeds (prefer sum(map(ord, 'name')) — see bayesian-workflow)"
SEARCH -e 'random_state\s*=\s*42' -e 'seed\s*=\s*42' -e 'PRNGKey\(42\)' -e 'np\.random\.seed\(' \
       -e 'default_rng\(42\)' -g '!**/archive/**' 2>/dev/null || \
SEARCH -e 'random_state *= *42' -e 'seed *= *42' -e 'PRNGKey(42)' -e 'np.random.seed('

section "Hardcoded absolute / home paths (breaks on every other machine)"
SEARCH -e '/Users/' -e '/home/' -e 'C:\\\\' -e 'read_parquet\("/' -e 'read_csv\("/' || true

section "as-of / vintage correctness (wall-clock time leaking into a pipeline)"
# Wall-clock calls inside an ETL/model make the same code produce different output on
# different days — the enemy of vintage/as-of reproducibility. Scoped to .py to avoid
# matching prose in docs. join_asof is flagged so you can confirm its 'by'/tolerance.
SEARCH -g '*.py' -e 'datetime\.now\(' -e 'date\.today\(' -e 'pd\.Timestamp\("now"' \
       -e 'pl\..*\.now\(' -e 'join_asof' 2>/dev/null || \
SEARCH --include='*.py' -e 'datetime.now(' -e 'date.today(' -e 'join_asof'

# --- Maintainability ------------------------------------------------------
section "Duplicated v1/v2 scripts & abandoned approaches (DELETE candidates)"
FILES | grep -iE '(_v[0-9]+|_old|_new|_final|_copy|_backup|_bak|/archive/|/scratch/|/deprecated/|/tmp/|\.bak$)' || true

section "Scratch / scratchpad notebooks beside production code"
FILES | grep -iE '(scratch|sandbox|playground|untitled|test_notebook).*\.ipynb$|scratchpad' || true

section "Type-checker-silenced regions (an ignore is a deferred decision)"
# These suppress the checker rather than fix the type. `Optional[...]` and `Any` are
# fine in moderation — count them, don't crusade. Polars `.cast()` is NOT a type smell.
SEARCH -g '*.py' -e 'type:\s*ignore' -e 'mypy:\s*ignore-errors' -e ':\s*Any\b' \
       -e '#\s*noqa' -e 'cast\(Any' 2>/dev/null || \
SEARCH --include='*.py' -e 'type: ignore' -e 'mypy: ignore-errors' -e '# noqa'

section "Unimplemented placeholders (load-bearing gaps vs throwaway stubs)"
# Scoped to source files: notebook JSON embeds base64 PNGs that match 'XXX' etc.
SEARCH -g '*.py' -g '!**/*.ipynb' -e 'raise NotImplementedError' -e 'TODO' \
       -e 'FIXME' -e 'HACK' -e 'pass\s*#\s*TODO' 2>/dev/null || \
SEARCH --include='*.py' -e 'raise NotImplementedError' -e 'TODO' -e 'FIXME' -e 'HACK'

# --- Onboarding / docs ----------------------------------------------------
section "Empty or placeholder READMEs"
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if [ ! -s "$f" ]; then echo "$f: EMPTY"; fi
done < <(FILES | grep -iE 'readme(\.md|\.rst|\.txt)?$')

section "Placeholder pyproject descriptions"
SEARCH -e 'Add your description here' -e 'description = ""' -e "description = ''" || true

# --- Security -------------------------------------------------------------
section "Committed secrets / credentials (verify against .gitignore!)"
FILES | grep -iE '(\.env$|\.env\.|secrets?\.|credentials|\.pem$|\.key$|id_rsa)' | grep -vE '\.env\.example|\.env\.template' || true
SEARCH -e 'api_key\s*=\s*["'"'"']' -e 'API_KEY\s*=\s*["'"'"']' -e 'password\s*=\s*["'"'"']' \
       -e 'token\s*=\s*["'"'"']' -e 'aws_secret' -e 'BLS_API_KEY\s*=\s*["'"'"']' \
       -g '!**/*.example' 2>/dev/null || true

# --- Test coverage gaps ---------------------------------------------------
section "Source modules with no obvious test (heuristic — confirm manually)"
mods=$(FILES | grep -E '\.py$' | grep -ivE '(/tests?/|test_|conftest|__init__|/archive/|/scratch/)')
tests=$(FILES | grep -E '\.py$' | grep -E '(/tests?/|test_)')
for m in $mods; do
  base=$(basename "$m" .py)
  if ! echo "$tests" | grep -q "test_${base}\|${base}_test"; then
    echo "$m"
  fi
done | sort -u

printf '\nDone. Each hit is a candidate — triage DELETE vs HARDEN per SKILL.md.\n'
