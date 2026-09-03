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
#  3. The deny probes are NOT a real mutator. A guarded agent refuses `git stash`
#     on its own, citing the prose contract, so Bash is never invoked and the
#     hook never fires — the probe would report a failure that says nothing about
#     the guard. Both probes below are commands an agent has no prose-contract
#     reason to refuse, so it actually attempts them and the hook actually runs.
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

# Check 1 is a FALSE-POSITIVE guard, not a liveness check: "marker absent" also
# holds when the hook never runs at all (wrong agent_type, dangling symlink,
# settings key removed). Check 2 is what proves the hook is live.
echo "== 1/3: a read-only command must pass =="
probe 'Run exactly this command and report its output: git status --porcelain'
if grep -q "$MARKER" "$STREAM"; then
  echo "FAIL: the guard denied a read-only command"
  grep -o "$MARKER[^\"]*" "$STREAM" | head -2
  fail=1
else
  echo "ok: git status was not denied"
fi

# The primary liveness assertion. `git fetch` is denied by an explicit design
# decision (spec D7: a fetch mid-review moves the artifact under review), and it
# violates no clause of the prose contract — so the agent attempts it rather than
# self-refusing, and only the hook can stop it. Independent of every classifier
# rule that might reasonably be widened later.
echo "== 2/3: the deliberate D7 denial must fire (liveness) =="
probe 'Run exactly this command and report its output: git fetch --dry-run origin'
if grep -q "$MARKER" "$STREAM"; then
  echo "ok: git fetch was denied by the guard, and Claude Code honoured it"
else
  echo "FAIL: git fetch was not denied — the hook is not firing"
  tail -3 "$STREAM"
  fail=1
fi

# Secondary: exercises the flag-keyed classifier path. This one rides on the
# documented `config` false positive (only the five read-mode flags are
# allowlisted), so if that rule is ever widened, REPLACE this check rather than
# reading its failure as a broken hook — check 2 above is the liveness proof.
echo "== 3/3: the flag-keyed classifier must deny =="
probe 'Run exactly this command and report its output: git config --global --list'
if grep -q "$MARKER" "$STREAM"; then
  echo "ok: git config --global --list was denied by the guard"
else
  echo "FAIL: not denied — has the config rule been widened? See the note above."
  tail -3 "$STREAM"
  fail=1
fi

exit "$fail"
