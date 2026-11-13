#!/bin/bash
# Check the report-source-match isolation before any rep. This runs isolation_probe.txt once through `claude -p`
# with the environment variables and flags of run_reps.sh, except `--output-format stream-json
# --verbose` in place of `--output-format json`. The stream shows what the session loaded, such as
# its tools and its skills. Keep every other flag identical to run_reps.sh.
# The run starts in a new, empty directory under /tmp, outside every repository.
# Usage: probe.sh <out-file> <model>
# The stream holds home paths and a session id. Keep <out-file> under /tmp and never commit it.
set -u
[ "$#" -eq 2 ] || { echo "usage: probe.sh <out-file> <model>"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
PROMPT="$KIT/isolation_probe.txt"
OUTDIR="$(cd "$(dirname "$1")" && pwd)" || exit 2
OUT="$OUTDIR/$(basename "$1")"
MODEL="$2"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 2; }
run="$(mktemp -d /tmp/rsm-probe-XXXXXX)" || exit 2
(
  cd "$run" || exit 2
  git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
  env -i HOME="$HOME" USER="$USER" LOGNAME="${LOGNAME:-$USER}" PATH="$PATH" SHELL="$SHELL" \
      TMPDIR="${TMPDIR:-/tmp}" LANG="${LANG:-en_US.UTF-8}" CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
    claude -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" --disable-slash-commands \
    --no-session-persistence --output-format stream-json --verbose --max-budget-usd 0.50 \
    < "$PROMPT" > "$OUT"
)
exit $?
