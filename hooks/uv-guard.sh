#!/usr/bin/env bash
# PreToolUse(Bash) — enforce uv-first tooling. Blocks (exit 2) the clearest
# violations and injects the corrected form into Claude's context, so the model
# retries with the right command instead of you re-explaining it every session.
#
# Blocks:  pip install ...        -> use `uv add <pkg>`
#          <bare> python[3] ...   -> use `uv run python ...`
#          <bare> pytest ...      -> use `uv run pytest ...`
# Allows:  anything already under `uv run` / `uvx`, and anything where those
#          tokens appear as non-leading words (echo, which, comments, etc.).
#
# Escape hatch: put the literal string `no-uv-guard` anywhere in the command.
#
# Heuristic, not a parser: it splits on && || ; | & and checks each subcommand's
# FIRST token. Good enough for the common cases; tune per-repo. Reads JSON stdin.
set -uo pipefail

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')
[ -z "$cmd" ] && exit 0

# opt-out
case "$cmd" in *no-uv-guard*) exit 0 ;; esac

block() { printf 'uv-guard: %s\n' "$1" >&2; exit 2; }

# pip install, anywhere in the command (incl. `python -m pip install`)
if printf '%s' "$cmd" | grep -Eq '(^|[^[:alnum:]_])pip[0-9]*[[:space:]]+install'; then
  block "this project is uv-managed — use 'uv add <pkg>' instead of 'pip install'."
fi

# check the leading token of each subcommand
norm=$(printf '%s' "$cmd" | sed -E 's/(\&\&|\|\||;|\||&)/\n/g')
while IFS= read -r sub; do
  sub="${sub#"${sub%%[![:space:]]*}"}"          # ltrim
  [ -z "$sub" ] && continue
  first=$(printf '%s' "$sub" | awk '{print $1}')
  case "$first" in
    python|python3)
      block "use 'uv run ${sub}' instead of bare '${first}' (uv-managed project)." ;;
    pytest)
      block "use 'uv run ${sub}' instead of bare 'pytest'." ;;
  esac
done <<EOF
$norm
EOF
exit 0
