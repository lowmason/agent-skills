#!/bin/bash
# Run implementer reps for plan 97's micro-test. Each rep is a fresh `claude -p` with the tools Bash,
# Read, Edit and Write, run from its own new git repository under /tmp, outside every other
# repository. `env -i` keeps only HOME, USER, LOGNAME, PATH, SHELL, TMPDIR and LANG, plus the two
# disable flags, so nothing from the calling session reaches the rep.
# `--setting-sources ""` keeps user-level context out of the reps: the output style, plugin
# SessionStart hooks, ~/.claude/CLAUDE.md and ~/.claude/rules/. CLAUDE_CODE_DISABLE_AUTO_MEMORY
# drops the auto-memory section. --disable-slash-commands keeps every installed skill and command
# out of the reps. The --settings value denies Read, Edit and Write under ~/. Check a new Claude
# Code version with isolation_probe.txt and env_check.txt first (probe.sh).
# Usage: run_reps.sh <prompt-dir> <fixture> <out-dir> <first> <last>
# <prompt-dir> is build_prompts.py's output. Each rep copies fixtures/<fixture>/repo/ into a new
# /tmp/mt-rep-XXXXXX/repo, commits it, and puts brief.md and spec.md into .sdd/plan/ as
# task-1-brief.md and task-1-spec.md. That first commit is the rep's BASE: the prompt's @REPO@
# becomes the repository path and @BASE@ the commit's full sha, and a prompt that still holds
# either token is refused. Into <out-dir>/rep<N>/ it writes final.diff, the copied workspace files,
# and summary.json last. The copies and summary.json write $TMPDIR (in its /private form too) as
# `$TMPDIR`, pytest's `pytest-of-<user>` as `pytest-of-$USER`, and $HOME as `~`, because a mutant run
# log holds pytest's tmp_path in its failure output. They also write the user's identity forms
# (kit_identity.py: the name, its parts, the email address, its local part and $USER, read from local
# config at run time) as tokens, final.diff included, so no such value reaches a file that gets
# committed. The raw stream, and unscrubbed copies of final.diff and the workspace files in
# rep<N>-orig/, go to ~/.cache/agent-skills/scratch/plan97/<out-dir's parent name>/<out-dir name>/,
# outside the repository.
# The first rep runs alone and writes the prompt cache; the others then run together.
# Three fixes from the report-source-match runner (specs/baseline/red-baseline-report-source-match/
# kit/run_reps.sh:18-50): the rep range is checked before the overwrite guard, each rep's status
# (its `claude` exit status, or 2 for a kit error) reaches the script's exit status, and a failed
# first rep stops the batch.
set -u
[ "$#" -eq 5 ] || { echo "usage: run_reps.sh <prompt-dir> <fixture> <out-dir> <first> <last>"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
PROMPT="$(cd "$1" && pwd)/$2.txt" || exit 2
FIXTURE="$2"
FIX="$KIT/fixtures/$FIXTURE"
OUT="$(mkdir -p "$3" && cd "$3" && pwd)" || exit 2
FIRST="$4"
LAST="$5"
SCRATCH="$HOME/.cache/agent-skills/scratch/plan97/$(basename "$(dirname "$OUT")")/$(basename "$OUT")"
DENY='{"permissions":{"deny":["Read(~/**)","Edit(~/**)","Write(~/**)"]}}'
[ -f "$PROMPT" ] || { echo "refusing: no prompt $PROMPT"; exit 2; }
[ -d "$FIX/repo" ] && [ -f "$FIX/brief.md" ] && [ -f "$FIX/spec.md" ] || { echo "refusing: no fixture $FIX"; exit 2; }
[ -x /tmp/mt-venv/bin/python ] || { echo "refusing: /tmp/mt-venv/bin/python is missing (see the record's Kits section)"; exit 2; }
# Check the range before the overwrite guard: a reversed or non-numeric range would skip the guard.
for n in "$FIRST" "$LAST"; do
  case "$n" in
    '' | *[!0-9]*) echo "refusing: first and last must be positive integers"; exit 2 ;;
  esac
done
[ "$FIRST" -ge 1 ] && [ "$FIRST" -le "$LAST" ] || { echo "refusing: need 1 <= first <= last"; exit 2; }
mkdir -p "$SCRATCH" || exit 2
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i" ] && { echo "refusing: $OUT/rep$i exists"; exit 2; }
  [ -e "$SCRATCH/rep$i.jsonl" ] && { echo "refusing: $SCRATCH/rep$i.jsonl exists"; exit 2; }
  i=$((i + 1))
done

kit_failed() {
  printf '{"fixture": "%s", "rep": %s, "kit_error": "%s"}\n' "$FIXTURE" "$1" "$2" > "$OUT/rep$1/summary.json.tmp"
  mv "$OUT/rep$1/summary.json.tmp" "$OUT/rep$1/summary.json"
  echo "rep$1 kit error: $2"
}

rep() {
  local n="$1" run repo base text start status
  mkdir "$OUT/rep$n" || return 2
  run="$(mktemp -d /tmp/mt-rep-XXXXXX)" || { kit_failed "$n" 'mktemp failed'; return 2; }
  (cd "$run" && git rev-parse --show-toplevel > /dev/null 2>&1) \
    && { kit_failed "$n" "$run is inside a git repository"; return 2; }
  repo="$run/repo"
  cp -R "$FIX/repo" "$repo" \
    && git -C "$repo" init -q \
    && git -C "$repo" config user.name 'Developer' \
    && git -C "$repo" config user.email 'developer@example.invalid' \
    && git -C "$repo" config commit.gpgsign false \
    && git -C "$repo" add -A \
    && git -C "$repo" commit -q -m 'Start the project' \
    || { kit_failed "$n" 'repository setup failed'; return 2; }
  base="$(git -C "$repo" rev-parse HEAD)"
  mkdir -p "$repo/.sdd/plan" && printf '*\n' > "$repo/.sdd/.gitignore" \
    && cp "$FIX/brief.md" "$repo/.sdd/plan/task-1-brief.md" \
    && cp "$FIX/spec.md" "$repo/.sdd/plan/task-1-spec.md" \
    || { kit_failed "$n" 'workspace setup failed'; return 2; }
  text="$(cat "$PROMPT")"
  text="${text//@REPO@/$repo}"
  text="${text//@BASE@/$base}"
  case "$text" in
    *@REPO@* | *@BASE@*) kit_failed "$n" 'the prompt still holds @REPO@ or @BASE@'; return 2 ;;
  esac
  printf '%s\n' "$text" > "$SCRATCH/rep$n.prompt.txt"
  start="$(date +%s)"
  (
    cd "$repo" || exit 2
    env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" SHELL="$SHELL" TMPDIR="$TMPDIR" LANG="${LANG-}" \
      CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      claude -p --model sonnet --tools Bash,Read,Edit,Write --allowedTools Bash,Read,Edit,Write \
      --strict-mcp-config --setting-sources "" --disable-slash-commands --no-session-persistence \
      --settings "$DENY" --max-budget-usd 1.50 --output-format stream-json --verbose \
      < "$SCRATCH/rep$n.prompt.txt" > "$SCRATCH/rep$n.jsonl" 2> "$SCRATCH/rep$n.err"
  )
  status=$?
  (cd "$KIT" && uv run --no-project -q python - "$SCRATCH/rep$n.jsonl" "$SCRATCH/rep$n.err" "$OUT/rep$n" \
    "$FIXTURE" "$n" "$run" "$repo" "$base" "$SCRATCH/rep$n.prompt.txt" "$status" "$(($(date +%s) - start))" <<'EOF'
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.getcwd())
import kit_identity  # noqa: E402 (the kit's directory is the cwd)

stream, err, dest, fixture, rep, run_dir, repo, base, prompt, status, wall = sys.argv[1:12]
home = os.environ['HOME']
dest, repo = Path(dest), Path(repo)
orig = Path(prompt).parent / f'rep{rep}-orig'
orig.mkdir()
IDENTITY = kit_identity.forms()
INIT_KEYS = ('cwd', 'tools', 'mcp_servers', 'model', 'permissionMode', 'slash_commands', 'skills',
             'output_style', 'claude_code_version')
RESULT_KEYS = ('subtype', 'is_error', 'num_turns', 'duration_ms', 'total_cost_usd', 'modelUsage')


def scrub(text):
    tmpdir, user = os.environ.get('TMPDIR', '').rstrip('/'), os.environ.get('USER', '')
    if tmpdir:
        text = text.replace('/private' + tmpdir, '$TMPDIR').replace(tmpdir, '$TMPDIR')
    if user:
        text = text.replace(f'pytest-of-{user}', 'pytest-of-$USER')
    return kit_identity.scrub(text.replace(home, '~'), IDENTITY)


def tilde(value):
    return json.loads(scrub(json.dumps(value)))


def git(*args, env=None):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, env=env)


init, result, calls, texts = None, None, [], []
for line in Path(stream).read_text().splitlines():
    try:
        record = json.loads(line)
    except json.JSONDecodeError:
        continue
    kind = record.get('type')
    if kind == 'system' and record.get('subtype') == 'init':
        init = {key: record.get(key) for key in INIT_KEYS}
    elif kind == 'assistant':
        for item in record['message'].get('content') or []:
            if item.get('type') == 'tool_use':
                calls.append({'name': item.get('name'), 'input': item.get('input')})
            elif item.get('type') == 'text':
                texts.append(item.get('text', ''))
    elif kind == 'result':
        result = {key: record.get(key) for key in RESULT_KEYS}
        usage = record.get('usage') or {}
        result['iterations'] = [it.get('type') for it in usage.get('iterations') or []]
        result['permission_denials'] = [{'tool_name': d.get('tool_name'), 'tool_input': d.get('tool_input')}
                                        for d in record.get('permission_denials') or []]
        result['final_message'] = record.get('result')

index = Path(run_dir) / 'final.index'
shutil.copy(repo / '.git' / 'index', index)
env = dict(os.environ, GIT_INDEX_FILE=str(index))
git('add', '-A', env=env)
diff = git('diff', '--cached', '--binary', base, env=env).stdout
(orig / 'final.diff').write_text(diff)
(dest / 'final.diff').write_text(scrub(diff))
index.unlink()

workspace = repo / '.sdd' / 'plan'
copied = []
for path in sorted(workspace.glob('task-1-report.md')) + sorted(workspace.glob('task-1-mutants*')):
    if path.name.endswith('.md') or path.name.endswith('.log'):
        text = path.read_text(errors='replace')
        (orig / path.name).write_text(text)
        (dest / path.name).write_text(scrub(text))
        copied.append(path.name)

err_lines = Path(err).read_text(errors='replace').splitlines() if Path(err).exists() else []
summary = {
    'fixture': fixture,
    'rep': int(rep),
    'rep_dir': run_dir,
    'base': base,
    'prompt_sha256': hashlib.sha256(Path(prompt).read_bytes()).hexdigest(),
    'claude_exit': int(status),
    'wall_seconds': int(wall),
    'init': init,
    'result': result,
    'final_message': result['final_message'] if result else (texts[-1] if texts else None),
    'tool_calls': calls,
    'commits': git('log', '--format=%h %s', f'{base}..HEAD').stdout.splitlines(),
    'status_porcelain': git('status', '--porcelain', '--untracked-files=normal').stdout.splitlines(),
    'copied': copied,
    'stderr_tail': err_lines[-20:],
}
if result:
    del result['final_message']
(dest / 'summary.json.tmp').write_text(json.dumps(tilde(summary), indent=2) + '\n')
os.replace(dest / 'summary.json.tmp', dest / 'summary.json')
cost = result['total_cost_usd'] if result else None
print(f'rep{rep} exit={status} subtype={result and result["subtype"]} cost={cost} wall={wall}s')
EOF
  ) || { kit_failed "$n" 'summary step failed'; return 2; }
  return "$status"
}

# The first rep writes the prompt cache for the others, so a failure there stops the batch.
rep "$FIRST" || { echo "rep$FIRST failed, so the other reps did not run"; exit 1; }
pids=()
i=$((FIRST + 1))
while [ "$i" -le "$LAST" ]; do
  rep "$i" &
  pids+=("$!")
  i=$((i + 1))
done
failed=0
for pid in ${pids[@]+"${pids[@]}"}; do
  wait "$pid" || failed=$((failed + 1))
done
[ "$failed" -eq 0 ] || { echo "$failed rep(s) failed"; exit 1; }
