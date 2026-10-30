#!/bin/bash
# Run one plan 73 F1 rep in a scratch repository: an Opus session writes and commits the plan,
# then a Sonnet session executes it with subagent-driven-development. Sessions are persisted,
# so score_f1.py can audit every transcript.
# Usage, from the repository root: run_f1.sh <scratch> <out-dir>
set -u
S="$(cd "$1" && pwd)" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
F1="$(cd "$(dirname "$0")" && pwd)"
[ -e "$OUT/plan.jsonl" ] && { echo "refusing: $OUT/plan.jsonl exists"; exit 2; }
ENVS=(CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=5400000)
FLAGS=(--strict-mcp-config --setting-sources project --permission-mode acceptEdits --allowedTools Bash
       --output-format stream-json --verbose)
cd "$S" || exit 2
env "${ENVS[@]}" claude -p --model claude-opus-5-5 --max-budget-usd 6 "${FLAGS[@]}" \
  < "$F1/prompts/plan.txt" > "$OUT/plan.jsonl" 2> "$OUT/plan.err"
echo "plan exit=$?"
PLAN="$(git ls-files 'specs/plans/*.md' | head -n 1)"
[ -n "$PLAN" ] || { echo 'no committed plan'; exit 1; }
cp "$PLAN" "$OUT/plan.md"
sed "s|<PLAN>|$PLAN|" "$F1/prompts/execute.txt" | env "${ENVS[@]}" claude -p --model claude-sonnet-5-5 \
  --max-budget-usd 25 "${FLAGS[@]}" > "$OUT/execute.jsonl" 2> "$OUT/execute.err"
echo "execute exit=$?"
git log --oneline > "$OUT/git-log.txt"
