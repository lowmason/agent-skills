#!/usr/bin/env bash
# cc-guide: hooks.events hooks.exit-codes hooks.patterns @2.1.326
# PreToolUse(Bash) — enforce uv-first tooling. Blocks (exit 2) the clearest
# violations and injects the corrected form into Claude's context, so the model
# retries with the right command instead of you re-explaining it every session.
#
# Blocks:  pip install ...             -> use `uv add <pkg>`
#          <bare> python[3[.13[t]]] ... -> use `uv run python ...`
#          <bare> pytest ...           -> use `uv run pytest ...`
#          A command word counts by its last path part with backslashes removed
#          (.venv/bin/python and \python are python), and so does a prefix word
#          (/usr/bin/env is env).
# Allows:  anything already under `uv run` / `uvx`, and anything where those
#          tokens appear as non-leading words (echo, which, comments, etc.).
#
# Escape hatch: put the literal string `no-uv-guard` anywhere in the command.
#
# Heuristic, not a parser: it splits on && || ; | & and checks each subcommand's
# command word: its first token once the shell keywords then, do, else and elif,
# leading VAR=value assignments and the prefix words time, env and command are
# skipped. The & of a redirect (>&, <&, &>) does not split. Quotes are not read,
# so a separator inside a quoted string still splits. Good enough for the common
# cases; tune per-repo. Reads JSON stdin.
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

assign_re='^[A-Za-z_][A-Za-z0-9_]*='   # a VAR=value word
python_re='^python([0-9][0-9.]*t?)?$'  # python, python3, python3.13, python3.13t

# Hide the & of a redirect (2>&1, 0<&3, &> log) behind \001 so that it does not
# split, then turn it back into & once the separators are newlines.
amp=$'\001'
prot=${cmd//'>&'/">$amp"}
prot=${prot//'<&'/"<$amp"}
prot=${prot//'&>'/"$amp>"}

# check the command word of each subcommand
norm=$(printf '%s' "$prot" | sed -E 's/(\&\&|\|\||;|\||&)/\n/g' | tr "$amp" '&')
while IFS= read -r sub; do
  sub="${sub#"${sub%%[![:space:]]*}"}"          # ltrim
  sub="${sub%"${sub##*[![:space:]]}"}"          # rtrim
  [ -z "$sub" ] && continue
  lead=''                                       # skipped words, kept for the suggestion
  rest=$sub
  while [ -n "$rest" ]; do
    word=${rest%%[[:space:]]*}                  # raw: rest loses exactly this text
    if [[ $word =~ $assign_re ]]; then
      lead="$lead$word "
    else
      key=${word//\\/}                          # \env -> env
      key=${key##*/}                            # /usr/bin/env -> env
      case "$key" in
        then|do|else|elif) ;;                   # a keyword is not part of the command
        time|env|command) lead="$lead$word " ;;
        *) break ;;
      esac
    fi
    rest=${rest#"$word"}
    rest="${rest#"${rest%%[![:space:]]*}"}"     # ltrim
  done
  first=${rest%%[[:space:]]*}
  args=${rest#"$first"}
  base=${first//\\/}                            # \python -> python
  base=${base##*/}                              # .venv/bin/python -> python
  if [[ $base =~ $python_re ]]; then
    block "use '${lead}uv run ${base}${args}' instead of bare '${first}' (uv-managed project)."
  elif [ "$base" = pytest ]; then
    block "use '${lead}uv run pytest${args}' instead of bare '${first}'."
  fi
done <<EOF
$norm
EOF
exit 0
