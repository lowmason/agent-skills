#!/bin/bash
# Run tool-enabled reps for plan 98's micro-test of the marimo notebook block. Each rep is a fresh
# `claude -p` with the tools Bash, Read, Edit and Write, run from its own new git repository under
# /tmp/mnb98/, outside every other repository. `env -i` keeps only HOME, USER, LOGNAME, PATH,
# SHELL, TMPDIR and LANG, plus the two disable flags, so nothing from the calling session reaches
# the rep.
# `--setting-sources project` loads the rep repository's CLAUDE.md, which the block arm needs, and
# keeps user-level context out of the reps: the output style, plugin SessionStart hooks,
# ~/.claude/CLAUDE.md and ~/.claude/rules/. CLAUDE_CODE_DISABLE_AUTO_MEMORY drops the auto-memory
# section. --disable-slash-commands keeps every installed skill and command out of the reps. The
# --settings value denies Read, Edit and Write under ~/. Check a new Claude Code version with
# isolation_probe.txt and env_check.txt first (probe.sh). Keep the `claude -p` lines identical to
# probe.sh's.
# Usage: run_reps.sh <arm> <case> <out-dir> <first> <last>
# <arm> is control or block. <case> is explore, override, lint, tidy or verdict, and the prompt is
# cases/<case>.txt. Each rep copies fixture/repo/ into a new /tmp/mnb98/rep-XXXXXX/repo, writes
# the arm's CLAUDE.md, copies the case's notebook over notebooks/explore.py, and commits. The
# control arm keeps fixture/repo/CLAUDE.md. The block arm inserts the working tree's
# templates/marimo-repo/notebook-block.md after the sentence `marimo-pair drives live notebook
# sessions in this repo.` and before the bullet list. Into <out-dir>/rep<N>/ it writes final.diff,
# notebook.py (the final notebooks/explore.py), and summary.json last. Those three files write
# $HOME as `~`, $TMPDIR (in its /private form too) as `$TMPDIR`, the rep directory as
# /tmp/mnb98/rep-XXXXXX, Claude Code's /tmp/claude-<hex>-cwd files as /tmp/claude-XXXX-cwd, and
# $USER as a word, as in `ls -l` or `ps` output, as `$USER`. Each tool call
# keeps whether its result was an error and the last 1,500 characters of the result, because O1
# needs the exit of a run. The raw stream goes to
# ~/.cache/agent-skills/scratch/plan98/<out-dir's parent name>/<out-dir name>/, outside the
# repository. The first rep runs alone and writes the prompt cache; the others then run together.
# Isolation of rep directories: the runner refuses to start, with exit 3, while /tmp/mnb98/ holds
# anything but venv/ and leakcheck.sh, and it names each such entry. When a rep's summary is
# written, the runner moves its rep directory to ~/.cache/agent-skills/scratch/plan98/repdirs/.
# After the first rep and again after the whole batch, it moves each other entry that reps wrote
# into /tmp/mnb98/, such as an HTML export, to ~/.cache/agent-skills/scratch/plan98/stray/. It
# moves and never deletes. So no rep can read an earlier rep's notebook or export. If rep 1's
# directory or a stray is still in /tmp/mnb98/ after rep 1, the batch stops with exit 3 before
# reps 2 to N start. The runner resolves <out-dir> once, the way `mkdir -p` follows `..`, `.` and
# links. It refuses that path, with exit 2, when it is /tmp/mnb98/ or lies inside it in any letter
# case, and it writes to that same path. So the check and the writes cannot disagree, and outputs
# stay outside.
set -u
[ "$#" -eq 5 ] || { echo "usage: run_reps.sh <arm> <case> <out-dir> <first> <last>"; exit 2; }
PARK="$HOME/.cache/agent-skills/scratch/plan98"

# Keep these six functions identical in run_reps.sh and probe.sh.
# Print the absolute, physical path that `mkdir -p` would reach for a path that need not exist yet.
# It walks the parts from left to right, as `mkdir -p` does. Each part that exists as a folder is
# resolved with `cd -P`, so a link counts where `mkdir -p` follows it, even after a part that does
# not exist yet. The current path is then always physical, so `..` is its parent. Call it in
# $(...), so that its set -f stays in a subshell.
resolve_path() {
  local path="$1" cur part
  set -f
  case "$path" in
    /*) cur=/ ;;
    *) cur="$(pwd -P)" || return 1 ;;
  esac
  local IFS=/
  for part in $path; do
    case "$part" in
      '' | .) ;;
      ..) cur="${cur%/*}"; [ -n "$cur" ] || cur=/ ;;
      *)
        cur="${cur%/}/$part"
        if [ -d "$cur" ]; then
          cur="$(cd -P "$cur" && pwd -P)" || return 1
        fi
        ;;
    esac
  done
  printf '%s\n' "$cur"
}

# Refuse, with exit 2, an output path that is /tmp/mnb98/ or lies inside it, because reps can read
# that folder. $1 is the path that resolve_path printed, and the caller writes to that same path.
# $2, when given, is the argument as the caller wrote it, for the message. The check ignores letter
# case, because a macOS volume usually does: there /tmp/MNB98 is the same folder as /tmp/mnb98.
# bash 3.2 has no ${var,,}, so tr lowers the case. When tr fails or prints nothing, it refuses.
refuse_inside() {
  local root lower
  root="$(cd -P /tmp/mnb98 2> /dev/null && pwd -P)" || root=/private/tmp/mnb98
  lower="$(printf '%s\n' "$1" | tr '[:upper:]' '[:lower:]')" && [ -n "$lower" ] \
    || { echo "refusing (exit 2): cannot check ${2:-$1}"; exit 2; }
  root="$(printf '%s\n' "$root" | tr '[:upper:]' '[:lower:]')"
  case "$lower" in
    /tmp/mnb98 | /tmp/mnb98/* | /private/tmp/mnb98 | /private/tmp/mnb98/* | "$root" | "$root"/*)
      echo "refusing (exit 2): ${2:-$1} is inside /tmp/mnb98/. Use a path outside it, for example under ~/.cache/agent-skills/scratch/plan98/."
      exit 2
      ;;
  esac
}

# Print each top-level entry of /tmp/mnb98/ other than venv/ and leakcheck.sh, one name a line.
extra_entries() {
  local entry
  for entry in /tmp/mnb98/* /tmp/mnb98/.[!.]* /tmp/mnb98/..?*; do
    { [ -e "$entry" ] || [ -L "$entry" ]; } || continue
    case "${entry##*/}" in
      venv | leakcheck.sh) ;;
      *) printf '%s\n' "${entry##*/}" ;;
    esac
  done
}

# Stop, with exit 3, while /tmp/mnb98/ holds anything but venv/ and leakcheck.sh. $1 says why, and
# "refusing" is the default.
refuse_extras() {
  local found
  found="$(extra_entries)"
  [ -z "$found" ] && return 0
  echo "${1:-refusing} (exit 3): /tmp/mnb98/ holds more than venv/ and leakcheck.sh. Move each entry out first:"
  printf '%s\n' "$found" | sed 's|^|  /tmp/mnb98/|'
  exit 3
}

# Move each stray entry that a rep wrote into /tmp/mnb98/ to stray/. A rep directory stays, because
# its own rep moves it when the rep ends, and a rep directory that is still there may be running.
sweep_strays() {
  local name dest
  mkdir -p "$PARK/stray" || return 1
  extra_entries | while IFS= read -r name; do
    case "$name" in
      rep-??????) continue ;;
    esac
    dest="$PARK/stray/$(date +%Y%m%d-%H%M%S)-$$-$name"
    mv "/tmp/mnb98/$name" "$dest" && echo "moved stray /tmp/mnb98/$name to ~/${dest#"$HOME"/}"
  done
}

# Move a finished rep directory out of /tmp/mnb98/ into repdirs/, so that no later rep can read it.
park_rep_dir() {
  local dir="$1"
  [ -n "$dir" ] && [ -d "$dir" ] || return 0
  mkdir -p "$PARK/repdirs" || return 1
  [ -e "$PARK/repdirs/${dir##*/}" ] && { echo "cannot move $dir: repdirs/ already holds ${dir##*/}"; return 1; }
  mv "$dir" "$PARK/repdirs/"
}

KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
ARM="$1"
CASE="$2"
case "$ARM" in
  control | block) ;;
  *) echo "refusing: arm must be control or block, not $ARM"; exit 2 ;;
esac
case "$CASE" in
  explore | override) NOTEBOOK="$KIT/fixture/repo/notebooks/explore.py" ;;
  lint | tidy) NOTEBOOK="$KIT/fixture/lint/explore.py" ;;
  verdict) NOTEBOOK="$KIT/fixture/verdict/explore.py" ;;
  *) echo "refusing: case must be explore, override, lint, tidy or verdict, not $CASE"; exit 2 ;;
esac
PROMPT="$KIT/cases/$CASE.txt"
# Resolve <out-dir> once. The check and every write below use this one physical path.
OUT="$(resolve_path "$3")" || { echo "refusing (exit 2): cannot resolve $3"; exit 2; }
refuse_inside "$OUT" "$3"
mkdir -p "$OUT" || exit 2
FIRST="$4"
LAST="$5"
ROOT="$(git -C "$KIT" rev-parse --show-toplevel)" || exit 2
BLOCK="$ROOT/templates/marimo-repo/notebook-block.md"
ANCHOR='marimo-pair drives live notebook sessions in this repo.'
SCRATCH="$HOME/.cache/agent-skills/scratch/plan98/$(basename "$(dirname "$OUT")")/$(basename "$OUT")"
DENY='{"permissions":{"deny":["Read(~/**)","Edit(~/**)","Write(~/**)"]}}'
[ -f "$PROMPT" ] || { echo "refusing: no prompt $PROMPT"; exit 2; }
[ -f "$NOTEBOOK" ] && [ -f "$KIT/fixture/repo/CLAUDE.md" ] || { echo "refusing: the fixture is incomplete"; exit 2; }
[ "$ARM" = control ] || [ -f "$BLOCK" ] || { echo "refusing: no block at $BLOCK"; exit 2; }
[ -x /tmp/mnb98/venv/bin/marimo ] || { echo "refusing: /tmp/mnb98/venv/bin/marimo is missing (Step 1)"; exit 2; }
refuse_extras
mkdir -p "$SCRATCH" || exit 2
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i" ] && { echo "refusing: $OUT/rep$i exists"; exit 2; }
  [ -e "$SCRATCH/rep$i.jsonl" ] && { echo "refusing: $SCRATCH/rep$i.jsonl exists"; exit 2; }
  i=$((i + 1))
done

kit_failed() {
  printf '{"arm": "%s", "case": "%s", "rep": %s, "kit_error": "%s"}\n' "$ARM" "$CASE" "$1" "$2" \
    > "$OUT/rep$1/summary.json.tmp"
  mv "$OUT/rep$1/summary.json.tmp" "$OUT/rep$1/summary.json"
  echo "rep$1 kit error: $2"
}

# run_rep sets the caller's `run`, so that rep can move the rep directory when run_rep ends.
run_rep() {
  local n="$1" repo base start status claude_md_sha block_sha
  mkdir "$OUT/rep$n" || return 2
  run="$(mktemp -d /tmp/mnb98/rep-XXXXXX)" || { kit_failed "$n" 'mktemp failed'; return 2; }
  (cd "$run" && git rev-parse --show-toplevel > /dev/null 2>&1) \
    && { kit_failed "$n" "$run is inside a git repository"; return 2; }
  repo="$run/repo"
  cp -R "$KIT/fixture/repo" "$repo" && cp "$NOTEBOOK" "$repo/notebooks/explore.py" \
    || { kit_failed "$n" 'fixture copy failed'; return 2; }
  block_sha=null
  if [ "$ARM" = block ]; then
    [ "$(grep -c -x -F "$ANCHOR" "$KIT/fixture/repo/CLAUDE.md")" = 1 ] \
      || { kit_failed "$n" 'the anchor sentence does not match exactly once'; return 2; }
    [ "$(grep -c -F 'marimo-repo:start' "$BLOCK")" = 1 ] && [ "$(grep -c -F 'marimo-repo:end' "$BLOCK")" = 1 ] \
      || { kit_failed "$n" 'the block lacks its markers'; return 2; }
    awk -v block="$BLOCK" -v anchor="$ANCHOR" \
      '{ print } $0 == anchor { print ""; while ((getline line < block) > 0) print line }' \
      "$KIT/fixture/repo/CLAUDE.md" > "$repo/CLAUDE.md" \
      || { kit_failed "$n" 'writing the block arm CLAUDE.md failed'; return 2; }
    block_sha="$(shasum -a 256 "$BLOCK" | cut -d ' ' -f 1)"
  fi
  claude_md_sha="$(shasum -a 256 "$repo/CLAUDE.md" | cut -d ' ' -f 1)"
  git -C "$repo" init -q \
    && printf '__pycache__/\n__marimo__/\n.ruff_cache/\n*.html\n' >> "$repo/.git/info/exclude" \
    && git -C "$repo" config user.name 'Developer' \
    && git -C "$repo" config user.email 'developer@example.invalid' \
    && git -C "$repo" config commit.gpgsign false \
    && git -C "$repo" add -A \
    && git -C "$repo" commit -q -m 'Start the project' \
    || { kit_failed "$n" 'repository setup failed'; return 2; }
  base="$(git -C "$repo" rev-parse HEAD)"
  cp "$PROMPT" "$SCRATCH/rep$n.prompt.txt" || { kit_failed "$n" 'prompt copy failed'; return 2; }
  start="$(date +%s)"
  (
    cd "$repo" || exit 2
    env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" SHELL="$SHELL" TMPDIR="$TMPDIR" LANG="${LANG-}" \
      CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      claude -p --model claude-opus-5-5 --tools Bash,Read,Edit,Write --allowedTools Bash,Read,Edit,Write \
      --strict-mcp-config --setting-sources project --disable-slash-commands --no-session-persistence \
      --settings "$DENY" --max-budget-usd 2.00 --output-format stream-json --verbose \
      < "$SCRATCH/rep$n.prompt.txt" > "$SCRATCH/rep$n.jsonl" 2> "$SCRATCH/rep$n.err"
  )
  status=$?
  (cd "$KIT" && uv run --no-project -q python - "$SCRATCH/rep$n.jsonl" "$SCRATCH/rep$n.err" "$OUT/rep$n" \
    "$ARM" "$CASE" "$n" "$run" "$repo" "$base" "$SCRATCH/rep$n.prompt.txt" "$status" "$(($(date +%s) - start))" \
    "$claude_md_sha" "$block_sha" "$KIT/fixture/repo/CLAUDE.md" "$BLOCK" "$ANCHOR" <<'EOF'
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

(stream, err, dest, arm, case, rep, run_dir, repo, base, prompt, status, wall, claude_md_sha, block_sha,
 fixture_claude_md, block_path, anchor) = sys.argv[1:18]
home = os.environ['HOME']
dest, repo = Path(dest), Path(repo)
INIT_KEYS = ('cwd', 'tools', 'mcp_servers', 'model', 'permissionMode', 'slash_commands', 'skills',
             'output_style', 'claude_code_version')
RESULT_KEYS = ('subtype', 'is_error', 'num_turns', 'duration_ms', 'total_cost_usd', 'modelUsage')
RESULT_TAIL = 1500
REP_DIR = '/tmp/mnb98/rep-XXXXXX'
CWD_FILE = re.compile(r'(/private)?/tmp/claude-[0-9a-f]+-cwd')


def scrub(text):
    tmpdir, user = os.environ.get('TMPDIR', '').rstrip('/'), os.environ.get('USER', '')
    text = text.replace('/private' + run_dir, REP_DIR).replace(run_dir, REP_DIR)
    if tmpdir:
        text = text.replace('/private' + tmpdir, '$TMPDIR').replace(tmpdir, '$TMPDIR')
    text = CWD_FILE.sub('/tmp/claude-XXXX-cwd', text.replace(home, '~'))
    return re.sub(rf'\b{re.escape(user)}\b', '$USER', text) if user else text


def tilde(value):
    if isinstance(value, str):
        return scrub(value)
    if isinstance(value, list):
        return [tilde(item) for item in value]
    if isinstance(value, dict):
        return {tilde(key): tilde(item) for key, item in value.items()}
    return value


def git(*args, env=None):
    return subprocess.run(['git', '-C', str(repo), *args], check=False, capture_output=True, text=True, env=env)


def result_text(content):
    if isinstance(content, str):
        return content
    parts = [item.get('text', '') for item in content or [] if isinstance(item, dict)]
    return '\n'.join(parts)


def arm_claude_md():
    text = Path(fixture_claude_md).read_text()
    if arm == 'control':
        return text.encode()
    lines = Path(block_path).read_text().splitlines()
    out = []
    for line in text.splitlines():
        out.append(line)
        if line == anchor:
            out += [''] + lines
    return ('\n'.join(out) + '\n').encode()


init, result, calls, texts, results = None, None, [], [], {}
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
                calls.append({'id': item.get('id'), 'name': item.get('name'), 'input': item.get('input')})
            elif item.get('type') == 'text':
                texts.append(item.get('text', ''))
    elif kind == 'user':
        content = (record.get('message') or {}).get('content')
        for item in content if isinstance(content, list) else []:
            if isinstance(item, dict) and item.get('type') == 'tool_result':
                results[item.get('tool_use_id')] = (bool(item.get('is_error')), result_text(item.get('content')))
    elif kind == 'result':
        result = {key: record.get(key) for key in RESULT_KEYS}
        usage = record.get('usage') or {}
        result['iterations'] = [it.get('type') for it in usage.get('iterations') or []]
        result['permission_denials'] = [{'tool_name': d.get('tool_name'), 'tool_input': d.get('tool_input')}
                                        for d in record.get('permission_denials') or []]
        result['final_message'] = record.get('result')

for call in calls:
    is_error, text = results.get(call.pop('id'), (None, None))
    call['is_error'] = is_error
    call['result_tail'] = None if text is None else text[-RESULT_TAIL:]

index = Path(run_dir) / 'final.index'
shutil.copy(repo / '.git' / 'index', index)
env = dict(os.environ, GIT_INDEX_FILE=str(index))
git('add', '-A', env=env)
(dest / 'final.diff').write_text(scrub(git('diff', '--cached', '--binary', base, env=env).stdout))
index.unlink()

notebook = repo / 'notebooks' / 'explore.py'
if notebook.exists():
    (dest / 'notebook.py').write_text(scrub(notebook.read_text(errors='replace')))

expected = hashlib.sha256(arm_claude_md()).hexdigest()
err_lines = Path(err).read_text(errors='replace').splitlines() if Path(err).exists() else []
summary = {
    'arm': arm,
    'case': case,
    'rep': int(rep),
    'rep_dir': run_dir,
    'base': base,
    'prompt_sha256': hashlib.sha256(Path(prompt).read_bytes()).hexdigest(),
    'claude_md_sha256': claude_md_sha,
    'arm_claude_md_sha256': expected,
    'claude_md_matches_arm': claude_md_sha == expected,
    'block_sha256': None if block_sha == 'null' else block_sha,
    'notebook_present': notebook.exists(),
    'claude_exit': int(status),
    'wall_seconds': int(wall),
    'init': init,
    'result': result,
    'final_message': result['final_message'] if result else (texts[-1] if texts else None),
    'tool_calls': calls,
    'commits': git('log', '--format=%h %s', f'{base}..HEAD').stdout.splitlines(),
    'status_porcelain': git('status', '--porcelain', '--untracked-files=normal').stdout.splitlines(),
    'stderr_tail': err_lines[-20:],
}
if result:
    del result['final_message']
(dest / 'summary.json.tmp').write_text(json.dumps(tilde(summary), indent=2) + '\n')
os.replace(dest / 'summary.json.tmp', dest / 'summary.json')
cost = result['total_cost_usd'] if result else None
print(f'rep{rep} exit={status} subtype={result and result["subtype"]} cost={cost} wall={wall}s')
EOF
  ) || kit_failed "$n" 'summary step failed'
}

rep() {
  local run=''
  run_rep "$1"
  park_rep_dir "$run" || echo "rep$1: its rep directory stays in /tmp/mnb98/, so the next start refuses"
}

rep "$FIRST"
sweep_strays
# Rep 1 runs alone. If its rep directory, or a stray, is still in /tmp/mnb98/ now, stop before the
# other reps start beside it.
refuse_extras 'stopping the batch after rep 1'
i=$((FIRST + 1))
while [ "$i" -le "$LAST" ]; do
  rep "$i" &
  i=$((i + 1))
done
wait
sweep_strays
