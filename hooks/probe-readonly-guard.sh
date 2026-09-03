#!/usr/bin/env bash
# Gate B — a live check that Claude Code actually delivers the agent identity in
# the PreToolUse payload and honours the guard's denial on the installed binary.
# Gate A (test_readonly_agent_guard.py) can pass perfectly against a hook Claude
# Code never invokes; this is the only test of the real claim.
#
# Three mechanics, all probed on 2.1.259 (see the README "Probe log"):
#
#  1. --allowedTools is variadic and swallows a trailing positional, so the
#     prompt goes FIRST. `claude -p` also blocks on a piped stdin: < /dev/null.
#
#  2. Assert on the RAW EVENT STREAM, not the agent's final message. When the
#     guard denies, the agent reports the constraint to its controller in its
#     own words — correct behaviour, but it paraphrases the marker away. The
#     denial text is reliably present in --output-format stream-json.
#
#  3. The deny probe is `git config --global --list`, NOT `git stash`. A guarded
#     agent refuses `git stash` on its own, citing the prose contract, so Bash is
#     never invoked and the hook never fires — the probe would then report a
#     failure that says nothing about the guard. `git config --global --list` is
#     genuinely read-only, so the agent has no reason to refuse it, while the
#     guard denies it as the documented false positive (only the five read-mode
#     flags are allowlisted). That makes it the one command guaranteed to
#     exercise the deny path end to end.
#
# Run from inside any git repo, after installing the hook:
#   hooks/probe-readonly-guard.sh
set -uo pipefail

MARKER='readonly-agent-guard:'
STREAM=$(mktemp -t readonly-guard-probe)
trap 'rm -f "$STREAM"' EXIT
fail=0

probe() {  # probe <prompt> -> writes the raw event stream to $STREAM
  claude "$1" -p --agent Explore --allowedTools "Bash" \
    --output-format stream-json --verbose < /dev/null > "$STREAM" 2>&1
}

echo "Claude Code: $(claude --version)"

echo "== 1/2: a read-only command must pass =="
probe 'Run exactly this command and report its output: git status --porcelain'
if grep -q "$MARKER" "$STREAM"; then
  echo "FAIL: the guard denied a read-only command"
  grep -o "$MARKER[^\"]*" "$STREAM" | head -2
  fail=1
else
  echo "ok: git status was not denied"
fi

echo "== 2/2: a mutator must be denied by THIS hook =="
probe 'Run exactly this command and report its output: git config --global --list'
if grep -q "$MARKER" "$STREAM"; then
  echo "ok: the guard denied it, and Claude Code honoured the decision"
else
  echo "FAIL: the command was not denied by the guard"
  tail -3 "$STREAM"
  fail=1
fi

exit "$fail"
