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
# The search tool is chosen once (rg when available, else grep/find); sections
# branch on it explicitly, so a zero-hit section is never re-run against the
# other tool's pattern dialect.

set -uo pipefail
ROOT="${1:-.}"
[ -d "$ROOT" ] || { echo "no such directory: $ROOT" >&2; exit 2; }
# Scan repo-relative paths: an absolute ROOT containing a signal-like component
# (/tmp/, scratch, _v2, /archive/) would otherwise match the path-signal
# regexes below and flag every file in the repo.
cd "$ROOT" || exit 2
ROOT=.

if command -v rg >/dev/null 2>&1; then HAVE_RG=1; else HAVE_RG=0; fi

# --hidden: committed dotfiles (.env!) must be visible to the scans.
RG()   { rg -n --no-heading -S --hidden -g '!.git' "$@" "$ROOT" 2>/dev/null; }
GREP() { grep -rnI --exclude-dir=.git "$@" "$ROOT" 2>/dev/null; }
FILES() {
  if [ "$HAVE_RG" = 1 ]; then
    rg --files --hidden -g '!.git' "$ROOT" 2>/dev/null
  else
    find "$ROOT" -name .git -prune -o -type f -print 2>/dev/null
  fi
}

section() { printf '\n========== %s ==========\n' "$1"; }

# --- Reproducibility / correctness risk -----------------------------------
section "Magic seeds (prefer sum(map(ord, 'name')) — see bayesian-workflow)"
if [ "$HAVE_RG" = 1 ]; then
  RG -e 'random_state\s*=\s*42' -e 'seed\s*=\s*42' -e 'PRNGKey\(42\)' \
     -e 'np\.random\.seed\(' -e 'default_rng\(42\)' -g '!**/archive/**'
else
  GREP -e 'random_state *= *42' -e 'seed *= *42' -e 'PRNGKey(42)' \
       -e 'np.random.seed(' -e 'default_rng(42)'
fi

section "Hardcoded absolute / home paths (breaks on every other machine)"
if [ "$HAVE_RG" = 1 ]; then
  RG -e '/Users/' -e '/home/' -e 'C:\\\\' -e 'read_parquet\("/' -e 'read_csv\("/'
else
  GREP -e '/Users/' -e '/home/' -e 'read_parquet("/' -e 'read_csv("/'
fi

section "as-of / vintage correctness (wall-clock time leaking into a pipeline)"
# Wall-clock calls inside an ETL/model make the same code produce different
# output on different days. Scoped to .py to avoid matching prose in docs.
# join_asof is flagged so you can confirm its 'by'/tolerance.
if [ "$HAVE_RG" = 1 ]; then
  RG -g '*.py' -e 'datetime\.now\(' -e 'date\.today\(' -e 'pd\.Timestamp\("now"' \
     -e 'pl\..*\.now\(' -e 'join_asof'
else
  GREP --include='*.py' -e 'datetime.now(' -e 'date.today(' -e 'join_asof'
fi

section "Polars joins with no cardinality contract (validate=)"
# A .join() without validate= accepts m:m silently. When a key that should be
# unique is duplicated upstream, rows fan out and every downstream array is
# misaligned -- with no error. Measured 2026-08-26: alt-nfp had 54 Polars join
# sites, 0 with validate= (the token appears nowhere in the workspace). The filter drops str.join()/os.path.join() false positives.
# A hit is a candidate, not a verdict: validate= is unnecessary where the
# cardinality is already guaranteed by construction upstream.
if [ "$HAVE_RG" = 1 ]; then
  RG -g '*.py' -e '\.join\(' | grep -vE "os\.path\.join|['\"][^'\"]*['\"]\.join\(|\bstr\.join" \
    | grep -v 'validate *=' || true
else
  GREP --include='*.py' -e '\.join(' | grep -vE "os\.path\.join|['\"][^'\"]*['\"]\.join\(|\bstr\.join" \
    | grep -v 'validate *=' || true
fi

# --- Maintainability ------------------------------------------------------
section "Duplicated v1/v2 scripts & abandoned approaches (DELETE candidates)"
FILES | grep -iE '(_v[0-9]+|_old|_new|_final|_copy|_backup|_bak|/archive/|/scratch/|/deprecated/|/tmp/|\.bak$)' || true

section "Scratch / scratchpad notebooks beside production code"
FILES | grep -iE '(scratch|sandbox|playground|untitled|test_notebook).*\.ipynb$|scratchpad' || true

section "Type-checker-silenced regions (an ignore is a deferred decision)"
# These suppress the checker rather than fix the type. `Optional[...]` and
# `Any` are fine in moderation — count them, don't crusade. Polars `.cast()`
# is NOT a type smell.
if [ "$HAVE_RG" = 1 ]; then
  RG -g '*.py' -e 'type:\s*ignore' -e 'mypy:\s*ignore-errors' -e ':\s*Any\b' \
     -e '#\s*noqa' -e 'cast\(Any'
else
  GREP --include='*.py' -e 'type: ignore' -e 'mypy: ignore-errors' -e '# noqa'
fi

section "Unimplemented placeholders (load-bearing gaps vs throwaway stubs)"
# Scoped to source files: notebook JSON embeds base64 PNGs that match 'XXX' etc.
if [ "$HAVE_RG" = 1 ]; then
  RG -g '*.py' -g '!**/*.ipynb' -e 'raise NotImplementedError' -e 'TODO' \
     -e 'FIXME' -e 'HACK' -e 'pass\s*#\s*TODO'
else
  GREP --include='*.py' -e 'raise NotImplementedError' -e 'TODO' -e 'FIXME' -e 'HACK'
fi

# --- Onboarding / docs ----------------------------------------------------
section "Empty or placeholder READMEs"
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if [ ! -s "$f" ] || ! grep -q '[^[:space:]]' "$f"; then echo "$f: EMPTY/placeholder"; fi
done < <(FILES | grep -iE 'readme(\.md|\.rst|\.txt)?$')

section "Placeholder pyproject descriptions"
if [ "$HAVE_RG" = 1 ]; then
  RG -e 'Add your description here' -e 'description = ""' -e "description = ''"
else
  GREP -e 'Add your description here' -e 'description = ""' -e "description = ''"
fi
true

# --- Security -------------------------------------------------------------
section "Committed secrets / credentials (verify against .gitignore!)"
# 'Committed' is the real predicate — prefer git's index over a filesystem
# walk (also immune to rg's ignore rules).
if git rev-parse --git-dir >/dev/null 2>&1; then
  git ls-files
else
  FILES
fi | grep -iE '(\.env$|\.env\.|secrets?\.|credentials|\.pem$|\.key$|id_rsa)' \
   | grep -vE '\.env\.example|\.env\.template' || true
if [ "$HAVE_RG" = 1 ]; then
  RG -e 'api_key\s*=\s*["'"'"']' -e 'API_KEY\s*=\s*["'"'"']' -e 'password\s*=\s*["'"'"']' \
     -e 'token\s*=\s*["'"'"']' -e 'aws_secret' -e 'BLS_API_KEY\s*=\s*["'"'"']' \
     -g '!**/*.example'
else
  GREP -e 'api_key[[:space:]]*=[[:space:]]*["'"'"']' -e 'API_KEY[[:space:]]*=[[:space:]]*["'"'"']' \
       -e 'password[[:space:]]*=[[:space:]]*["'"'"']' -e 'token[[:space:]]*=[[:space:]]*["'"'"']' \
       -e 'aws_secret' -e 'BLS_API_KEY[[:space:]]*=[[:space:]]*["'"'"']'
fi

# --- Test coverage gaps ---------------------------------------------------
section "Source modules with no obvious test (heuristic — confirm manually)"
mods=$(FILES | grep -E '\.py$' | grep -ivE '(/tests?/|test_|conftest|__init__|/archive/|/scratch/)')
tests=$(FILES | grep -E '\.py$' | grep -E '(/tests?/|test_)')
while IFS= read -r m; do
  [ -n "$m" ] || continue
  base=$(basename "$m" .py)
  if ! printf '%s\n' "$tests" | grep -q "test_${base}\|${base}_test"; then
    printf '%s\n' "$m"
  fi
done <<< "$mods" | sort -u

printf '\nDone. Each hit is a candidate — triage DELETE vs HARDEN per SKILL.md.\n'
