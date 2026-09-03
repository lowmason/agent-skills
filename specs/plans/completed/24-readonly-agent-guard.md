# Read-only Agent Guard Implementation Plan

**Status: COMPLETE (2026-09-03)** — executed via executing-plans (inline); nothing deferred.

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a `PreToolUse(Bash)` hook that mechanically enforces the Bash half of the read-only contract carried by five agents (`code-reviewer`, `task-reviewer`, `security-auditor`, `Explore`, `test-runner`), plus the commit-time lint that keeps its roster from drifting.

**Architecture:** A single stdlib-only Python script, `hooks/readonly-agent-guard.py`, reads the hook payload from stdin. It exits 0 immediately unless the payload names one of five guarded agents, then classifies the `Bash` command: git is an **allowlist** that fails closed on unknown verbs, non-git is a small **denylist** of unambiguous mutators. A denial is emitted as `permissionDecision: deny` JSON on stdout with exit 0. `build/check_frontmatter.py` imports the roster constant and asserts bidirectionally against the `## Read-only contract` heading in `agents/*.md`, so a sixth read-only agent or a stale roster entry fails the lint at the commit that introduces it.

**Tech Stack:** Python (stdlib only: `json`, `shlex`, `sys`, `importlib.util`), pytest via `uv run --python 3.13`, bash for the live probe, Claude Code hooks JSON in `~/.claude/settings.json`.

**Spec:** [specs/completed/readonly-agent-guard.md](../../completed/readonly-agent-guard.md) — section references below (§1–§6, D1–D7) point into it.

## Global Constraints

- **The guard source must be Python 3.9-compatible.** `#!/usr/bin/env python3` resolves to `/usr/bin/python3` = **Python 3.9.6** on this machine (verified 2026-09-03). Use `from __future__ import annotations` so `str | None` and `frozenset[str]` annotations are never evaluated at runtime. No `match` statements, no PEP-604 unions outside annotations.
- **Stdlib only in `hooks/`.** The guard and its tests import nothing outside the standard library. The hook runs on every `Bash` call in every project; a third-party import would break it wherever that package is absent.
- **Contract tests invoke the script through its shebang** — `subprocess.run([str(GUARD)], ...)`, never `[sys.executable, str(GUARD)]`. This is what makes the 3.9-compatibility constraint above self-testing: the tests exercise the same interpreter production does.
- **The guard filename is hyphenated** (`hooks/readonly-agent-guard.py`, per spec §1/§5), so it is not importable by a plain `import` statement. Every consumer — the Gate A tests and `build/check_frontmatter.py` — loads it with `importlib.util.spec_from_file_location`. This is safe only because `main()` sits behind `if __name__ == '__main__':`; keep it there.
- **The roster keys on the frontmatter `name`, not the filename.** `agents/explore.md` carries `name: Explore`, and `agent_type` at runtime is the frontmatter name. A roster entry of `explore` would silently never match.
- **Task 1's probe finding governs** `AGENT_TYPE_KEY` and the recorded payload shape. Later tasks are written against `agent_type`; if Task 1 observes a different key or nesting, update Task 2's constant and every payload fixture, and note the deviation. Do not proceed on a guessed name.
- **No escape hatch** (spec D5). No opt-out string, no environment-variable bypass, nothing in the denial message that teaches a way through.
- **Python style:** single quotes over double, matching `build/check_frontmatter.py`.
- **Tests are directory-scoped.** The Gate A suite runs from `hooks/`: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q`. The lint suite runs from `build/`.
- Commit at the end of every task.

---

### Task 1: Probe the PreToolUse payload contract

Spec §Verification flags this as an assumption that must be a **finding, not a premise**: every later task hardcodes the field that carries the agent identity. This task observes it on the real binary and freezes what it saw as a test fixture.

**Acceptance criterion:** a real **Agent-tool dispatch** of `Explore` produces a `PreToolUse(Bash)` payload carrying the agent name. That is the production path. The `claude -p --agent` route is recorded *separately* — it is only the scriptable route for Gate B (Task 7), and it is possible for `--agent` to set a session-level field without populating the per-call payload.

**Files:**
- Create: `hooks/test_readonly_agent_guard.py` (fixture + one assertion only; Tasks 2–5 extend it)
- Modify: `hooks/README.md` (append a `## Probe log` section at the end)
- Scratch, never committed: `/tmp/rag-probe/`

**Interfaces:**
- Produces: `RECORDED_PAYLOAD` — a module-level `dict` in `hooks/test_readonly_agent_guard.py` holding one verbatim recorded payload from a guarded-agent `Bash` call, and `RECORDED_MAIN_SESSION_PAYLOAD` holding one from a main-session `Bash` call. Tasks 2–5 build every stdin fixture from these.
- Produces: the confirmed key name for Task 2's `AGENT_TYPE_KEY`, and the confirmed Gate B invocation route for Task 7.

- [x] **Step 1: Build the recorder outside the repo**

Nothing untracked may land in the working tree, so the recorder lives in `/tmp`.

```bash
mkdir -p /tmp/rag-probe
cat > /tmp/rag-probe/recorder.py <<'PY'
#!/usr/bin/env python3
"""Throwaway PreToolUse recorder: append the raw stdin payload, allow everything."""
import pathlib
import sys

raw = sys.stdin.read().replace('\n', ' ')
with pathlib.Path('/tmp/rag-probe/payloads.jsonl').open('a') as fh:
    fh.write(raw + '\n')
PY
chmod +x /tmp/rag-probe/recorder.py
: > /tmp/rag-probe/payloads.jsonl
```

- [x] **Step 2: Back up this repo's local settings, then install the recorder into them**

`.claude/settings.local.json` is gitignored and per-machine, and this repo is already a trusted directory — so the probe needs no global mutation. Back it up first; Step 6 restores it.

```bash
cp .claude/settings.local.json /tmp/rag-probe/settings.local.json.bak
python3 - <<'PY'
import json
import pathlib

p = pathlib.Path('.claude/settings.local.json')
cfg = json.loads(p.read_text())
cfg.setdefault('hooks', {}).setdefault('PreToolUse', []).append(
    {'matcher': 'Bash',
     'hooks': [{'type': 'command', 'command': '/tmp/rag-probe/recorder.py'}]})
p.write_text(json.dumps(cfg, indent=2) + '\n')
print('recorder installed')
PY
```

- [x] **Step 3: Probe the production route — a real Agent-tool dispatch**

```bash
claude -p --allowedTools "Bash,Task,Agent" 'Use the Agent tool with subagent_type "Explore" to run exactly this command and report its first line: git status --porcelain'
```

Expected: the nested session completes and `/tmp/rag-probe/payloads.jsonl` is non-empty. If the run errors before dispatching, retry once with a simpler prompt; if it still fails, record that and move to Step 4 — the `--agent` route may be the only observable one.

- [x] **Step 4: Probe the Gate B route — the `--agent` flag**

```bash
claude -p --agent Explore --allowedTools "Bash" 'Run exactly: git status --porcelain'
```

- [x] **Step 5: Read the recorded payloads**

```bash
python3 - <<'PY'
import json
import pathlib

for i, line in enumerate(pathlib.Path('/tmp/rag-probe/payloads.jsonl').read_text().splitlines()):
    d = json.loads(line)
    agentish = {k: v for k, v in d.items() if 'agent' in k.lower() or 'subagent' in k.lower()}
    print(i, 'keys=', sorted(d))
    print('   agent-ish=', agentish)
    print('   command=', (d.get('tool_input') or {}).get('command'))
PY
```

Expected: at least one record whose agent-ish field equals `Explore`, and at least one main-session record where that field is absent. Write down (a) the exact key name, (b) whether it is top-level or nested, (c) which of Steps 3/4 produced it.

**Disambiguate a null result before concluding anything.** "No record carries an agent-ish field" has two causes with opposite consequences: the field does not exist, or the dispatch never happened (in `-p` mode the model *chooses* whether to use the Agent tool — a prompt can simply be ignored). Tell them apart:

- **Zero records at all** -> the hook never fired. The settings merge in Step 2 did not take effect; fix that and re-run. Conclude nothing about the field.
- **Records exist, all of them main-session-shaped** -> check whether the Step 3 transcript actually shows a subagent dispatch. If it does not, re-run Step 3 with a more forcing prompt (`'Do not run any command yourself. Your only action is to dispatch the Explore subagent via the Agent tool and have it run: git status --porcelain'`) before concluding the field is absent.
- **Only the `--agent` route produced the field** -> record that in the probe log. Task 7 builds Gate B on it, but flag it: `--agent` is not the production path, so the guard's real-world coverage stays unproven and the next binary update must re-probe the dispatch route.

Only after one of these resolves is the field name a finding rather than a guess.

- [x] **Step 6: Restore the settings file and verify the restore**

Do this before anything else, so a failure later in the task cannot leave the recorder installed.

```bash
cp /tmp/rag-probe/settings.local.json.bak .claude/settings.local.json
diff /tmp/rag-probe/settings.local.json.bak .claude/settings.local.json && echo RESTORED
grep -c 'rag-probe' .claude/settings.local.json || echo "recorder gone (grep found 0)"
```

Expected: `RESTORED`, and the grep reports 0 matches.

- [x] **Step 7: Freeze the observed payloads as the test fixture**

Create `hooks/test_readonly_agent_guard.py`. Replace the two dict literals below with the **verbatim** payloads printed in Step 5 — same keys, same nesting, same types. Trim only fields that are obviously volatile (`session_id`, absolute transcript paths) and leave a comment saying you did.

```python
"""Gate A for hooks/readonly-agent-guard.py — run from this directory.

cd hooks && uv run --python 3.13 --with pytest python -m pytest -q

Two layers, per spec Verification: unit tests import the classifier directly,
contract tests drive the script as a subprocess with real payloads on stdin.
Stdlib only, matching the guard itself.
"""

import importlib.util
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
GUARD = HOOKS / 'readonly-agent-guard.py'

# Recorded from Claude Code 2.1.259 on 2026-09-03 by the Task 1 probe
# (specs/plans/completed/24-readonly-agent-guard.md). This is the observed
# payload shape, not an invented one — every stdin fixture below derives from
# it, so Gate A cannot pass against a shape Claude Code never sends.
RECORDED_PAYLOAD = {
    'hook_event_name': 'PreToolUse',
    'tool_name': 'Bash',
    'tool_input': {'command': 'git status --porcelain'},
    'agent_type': 'Explore',
}

# The same event from the main session: the agent-identity field is absent.
RECORDED_MAIN_SESSION_PAYLOAD = {
    'hook_event_name': 'PreToolUse',
    'tool_name': 'Bash',
    'tool_input': {'command': 'git status --porcelain'},
}


def test_recorded_payload_carries_the_agent_identity():
    assert RECORDED_PAYLOAD['agent_type'] == 'Explore'
    assert 'agent_type' not in RECORDED_MAIN_SESSION_PAYLOAD
    assert RECORDED_PAYLOAD['tool_name'] == 'Bash'
    assert isinstance(RECORDED_PAYLOAD['tool_input']['command'], str)
```

- [x] **Step 8: Run the fixture test**

Run: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `1 passed`.

- [x] **Step 9: Record the finding in the README probe log**

Append to the end of `hooks/README.md` (Task 8 restructures the rest of this file and **preserves this section verbatim**):

```markdown
## Probe log

`readonly-agent-guard.py` depends on Claude Code putting the dispatched agent's
name in the `PreToolUse` payload. That is version-sensitive API surface, so it is
probed rather than assumed — re-run the probe after a binary update.

| date | Claude Code | finding |
|---|---|---|
| 2026-09-03 | 2.1.259 | `agent_type` is delivered top-level on `PreToolUse(Bash)` payloads for Agent-tool dispatches, and is absent for main-session calls. Gate B route: `claude -p --agent <name>`. |

The recorded payloads are frozen as `RECORDED_PAYLOAD` in
`test_readonly_agent_guard.py`; `probe-readonly-guard.sh` re-checks the live
behaviour end to end.
```

Correct the table row to what you actually observed. If the `--agent` route did **not** populate the field, say so in the row and record the working route instead — Task 7 builds Gate B on whatever this row names.

- [x] **Step 10: Commit**

```bash
git add hooks/test_readonly_agent_guard.py hooks/README.md
git commit -m "test(hooks): freeze the probed PreToolUse agent-identity payload

Records the observed payload shape for the read-only agent guard rather than
assuming it, per the spec's flagged assumption. Probed on Claude Code 2.1.259.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Guard module skeleton — tokenizer and the non-git denylist

Spec §2's non-git half: a denylist of unambiguous mutators, with unlisted commands passing. Redirection, `tee`, `mkdir`, `touch`, `chmod`, `cp`, `dd`, and `ln` are **deliberately excluded** (spec D2) — do not add them.

**Files:**
- Create: `hooks/readonly-agent-guard.py`
- Modify: `hooks/test_readonly_agent_guard.py`

**Interfaces:**
- Produces: `READONLY_AGENTS: frozenset[str]` — the five guarded agent names, keyed on frontmatter `name`. Task 6's lint imports this.
- Produces: `AGENT_TYPE_KEY: str` — the payload key confirmed in Task 1. Task 5 uses it.
- Produces: `CONTRACT_CLAUSE: str` — the quoted contract sentence, used in Task 5's denial message.
- Produces: `split_subcommands(command: str) -> list[list[str]]` — tokenized subcommands.
- Produces: `classify(command: str) -> str | None` — `None` allows; a `str` is a one-or-two-sentence reason fragment naming the problem and the read-only alternative. Tasks 3 and 4 extend its git half; Task 5 consumes it.
- Produces: `_classify_subcommand(tokens: list[str]) -> str | None` — dispatches one subcommand.

- [x] **Step 1: Write the failing tests — tokenizer facts and the denylist**

The tokenizer assertions pin exact token lists rather than trusting a reading of the `shlex` docs. Append to `hooks/test_readonly_agent_guard.py`:

```python
def _load_guard():
    spec = importlib.util.spec_from_file_location('readonly_agent_guard', GUARD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = _load_guard()


def test_roster_is_the_five_readonly_agents():
    assert guard.READONLY_AGENTS == frozenset(
        {'code-reviewer', 'task-reviewer', 'security-auditor', 'Explore', 'test-runner'}
    )


def test_tokenizer_splits_on_shell_operators():
    assert guard.split_subcommands('git log && rm -rf x') == [
        ['git', 'log'], ['rm', '-rf', 'x']]
    assert guard.split_subcommands('cat a|grep b') == [['cat', 'a'], ['grep', 'b']]
    assert guard.split_subcommands('a; b & c || d') == [['a'], ['b'], ['c'], ['d']]


def test_tokenizer_splits_on_newlines():
    # shlex treats a newline as plain whitespace, so 'a\nb' would collapse into
    # one subcommand and hide b's leading token. The pre-split is load-bearing.
    assert guard.split_subcommands('git log\nrm x') == [['git', 'log'], ['rm', 'x']]


def test_tokenizer_leaves_redirection_intact():
    # '2>&1' lexes as ['2', '>&', '1'] and '>' is not an operator we split on —
    # redirection stays inside its subcommand, per spec D2.
    assert guard.split_subcommands('cat x 2>&1') == [['cat', 'x', '2', '>&', '1']]
    assert guard.split_subcommands('git log > /tmp/f') == [
        ['git', 'log', '>', '/tmp/f']]


def test_tokenizer_does_not_treat_hash_as_a_comment():
    # A real shell only starts a comment at a word boundary; shlex's default
    # commenters would swallow the rest of the line mid-word and hide a mutator.
    assert guard.split_subcommands('foo#;rm -rf x') == [['foo#'], ['rm', '-rf', 'x']]


def test_quoted_arguments_survive_tokenization():
    assert guard.split_subcommands("git log --grep='a && b'") == [
        ['git', 'log', '--grep=a && b']]


def test_non_git_denylist_entries_are_denied():
    for command in ('rm -rf build', 'mv a b', 'truncate -s 0 f', 'shred f', 'sudo ls'):
        assert guard.classify(command) is not None, command


def test_sed_in_place_is_denied_in_every_spelling():
    for command in ("sed -i 's/a/b/' f", "sed --in-place 's/a/b/' f",
                    "sed -i.bak 's/a/b/' f", "sed -ne 'p' f && sed -i 's/a/b/' f"):
        assert guard.classify(command) is not None, command


def test_read_only_shell_passes():
    for command in ('cat f', 'grep -r x .', 'jq . f.json', 'find . -name "*.py"',
                    "sed -n '1,10p' f", 'uv run pytest -q', 'echo rm', 'ls -la'):
        assert guard.classify(command) is None, command


def test_excluded_mutators_still_pass_per_spec_D2():
    # Consciously excluded: the heuristic cannot separate a /tmp write from a
    # repo write without real path analysis. Documented, not an oversight.
    for command in ('echo x > /tmp/f', 'mkdir -p /tmp/d', 'touch /tmp/f',
                    'cp a b', 'chmod +x s.sh', 'tee /tmp/f'):
        assert guard.classify(command) is None, command


def test_mutator_is_caught_when_it_is_not_the_first_subcommand():
    assert guard.classify('git log --oneline && rm -rf .git') is not None
    assert guard.classify('cat f | grep x ; sudo reboot') is not None
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: collection error — `FileNotFoundError` / `No such file or directory: '.../readonly-agent-guard.py'` from `_load_guard()`.

- [x] **Step 3: Write the guard skeleton**

Create `hooks/readonly-agent-guard.py`:

```python
#!/usr/bin/env python3
"""PreToolUse(Bash) guard enforcing the read-only agents' Bash contract.

Five agents (see READONLY_AGENTS) declare that they will not mutate the working
tree, the index, HEAD, branch state, or the worktree list. Their `tools:`
frontmatter already denies Write/Edit; nothing enforced the Bash half. This hook
does, by classifying the command and returning a `deny` decision for mutators.

Payloads without a guarded agent — the main session, `debugger`, `docs-writer`,
every built-in agent — are allowed untouched and as early as possible.

Design and rationale: specs/completed/readonly-agent-guard.md.

Runs under whatever `python3` is first on PATH (Python 3.9 on macOS system
Python), so keep this file 3.9-compatible: stdlib only, no `match`, and
annotations deferred via __future__.
"""
from __future__ import annotations

import json
import shlex
import sys

# Keyed on each agent's frontmatter `name`, which is what Claude Code reports as
# the agent type — note the capital E in Explore. build/check_frontmatter.py
# imports this and asserts it against the `## Read-only contract` heading in
# agents/*.md in both directions, so drift fails the lint at commit time.
READONLY_AGENTS = frozenset({
    'code-reviewer',
    'task-reviewer',
    'security-auditor',
    'Explore',
    'test-runner',
})

# Confirmed against Claude Code 2.1.259 by the probe in hooks/README.md.
AGENT_TYPE_KEY = 'agent_type'

CONTRACT_CLAUSE = (
    'you must not mutate the working tree, the index, HEAD, branch state, '
    'or the worktree list via Bash'
)

# Subcommand separators. '>' and '<' are deliberately absent: redirection stays
# inside its subcommand so `git log > /tmp/f` classifies as a `git log`.
OPERATORS = frozenset({'&&', '||', ';', '|', '&'})

DENIED_COMMANDS = {
    'rm': '`rm` deletes files.',
    'mv': '`mv` moves or renames files.',
    'truncate': '`truncate` rewrites file contents in place.',
    'shred': '`shred` destroys file contents.',
    'sudo': '`sudo` escalates privileges and can mutate anything.',
}


def split_subcommands(command):
    """Tokenize `command` and split it into subcommands on shell operators.

    Newlines are pre-split because shlex treats them as ordinary whitespace,
    which would otherwise fold a second line into the first subcommand and hide
    its leading token from classification.
    """
    subcommands = []
    for line in command.split('\n'):
        lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ''  # a shell comment only starts at a word boundary
        current = []
        for token in lexer:
            if token in OPERATORS:
                if current:
                    subcommands.append(current)
                current = []
            else:
                current.append(token)
        if current:
            subcommands.append(current)
    return subcommands


def _sed_edits_in_place(args):
    for token in args:
        if token == '--in-place' or token.startswith('--in-place='):
            return True
        if token.startswith('-') and not token.startswith('--') and 'i' in token[1:]:
            return True
    return False


def _classify_non_git(tokens):
    head = tokens[0]
    if head in DENIED_COMMANDS:
        return DENIED_COMMANDS[head] + ' This agent inspects; it does not modify.'
    if head == 'sed' and _sed_edits_in_place(tokens[1:]):
        return ('`sed -i` edits files in place; drop `-i` to write the result to '
                'stdout instead.')
    return None


def _classify_subcommand(tokens):
    if not tokens:
        return None
    if tokens[0] == 'git':
        return _classify_git(tokens[1:])
    return _classify_non_git(tokens)


def classify(command):
    """Return None if `command` is read-only, else a reason fragment for denial.

    git is an allowlist that fails closed on unknown verbs; non-git is a
    denylist of unambiguous mutators, so unlisted commands pass. The asymmetry
    is deliberate — read-only shell is unbounded, read-only git is not.
    """
    for tokens in split_subcommands(command):
        detail = _classify_subcommand(tokens)
        if detail is not None:
            return detail
    return None


def _classify_git(args):
    return None  # Tasks 3 and 4 replace this


if __name__ == '__main__':
    sys.exit(0)  # Task 5 replaces this with main()
```

The docstring points at `specs/completed/readonly-agent-guard.md` — the spec's
**post-retirement** location. It is still at `specs/readonly-agent-guard.md` while
this plan runs; the Plan Completion Protocol moves it, which makes the reference
correct at the end state. Nothing lints it either way (`check_frontmatter.py`
validates links inside `skills/` only).

Then make it executable:

```bash
chmod +x hooks/readonly-agent-guard.py
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: PASS (all tests in the file).

- [x] **Step 5: Confirm the file is 3.9-clean under the real hook interpreter**

Run: `/usr/bin/env python3 -m py_compile hooks/readonly-agent-guard.py && echo "3.9 OK"`
Expected: `3.9 OK` with no `SyntaxError`.

- [x] **Step 6: Commit**

```bash
git add hooks/readonly-agent-guard.py hooks/test_readonly_agent_guard.py
git commit -m "feat(hooks): add read-only agent guard skeleton and non-git denylist

Tokenizer splits on shell operators and newlines; unambiguous file mutators
(rm, mv, truncate, shred, sudo, sed -i) deny. Redirection, mkdir, touch, cp,
and chmod are deliberately excluded per spec D2.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Git allowlist — read-only verbs, global options, fail-closed default

Spec §2's git half, first layer. The allowlist fails closed: any verb not explicitly listed is denied, which covers today's write verbs, the plumbing that mutates without a recognizable write verb in its name, and any verb git adds in the future.

**Files:**
- Modify: `hooks/readonly-agent-guard.py` (replace the `_classify_git` stub)
- Modify: `hooks/test_readonly_agent_guard.py`

**Interfaces:**
- Consumes: `_classify_git(args: list[str]) -> str | None` from Task 2 (currently a stub returning `None`); `args` is the token list **after** the leading `git`.
- Produces: `GIT_READONLY_VERBS: frozenset[str]`, `GIT_INFO_FLAGS`, `GIT_GLOBAL_FLAGS`, `GIT_GLOBAL_WITH_VALUE`, `GIT_ALTERNATIVES: dict[str, str]` — Task 4 adds two more tables consulted by the same dispatcher.

- [x] **Step 1: Write the failing tests**

Append to `hooks/test_readonly_agent_guard.py`:

```python
ALWAYS_ALLOWED_GIT_VERBS = [
    'log', 'show', 'diff', 'diff-tree', 'status', 'grep', 'blame', 'ls-files',
    'ls-tree', 'ls-remote', 'cat-file', 'rev-parse', 'rev-list', 'describe',
    'shortlog', 'whatchanged', 'name-rev', 'merge-base', 'for-each-ref',
    'count-objects', 'verify-commit', 'check-ignore', 'check-attr', 'var',
    'help', 'version',
]


def test_every_readonly_git_verb_is_allowed():
    for verb in ALWAYS_ALLOWED_GIT_VERBS:
        assert guard.classify('git ' + verb) is None, verb
    assert guard.classify('git show abc123:src/x.py') is None
    assert guard.classify('git diff --stat main..HEAD') is None


def test_write_verbs_are_denied():
    for verb in ('commit', 'add', 'checkout', 'switch', 'restore', 'reset',
                 'revert', 'merge', 'rebase', 'cherry-pick', 'am', 'apply',
                 'push', 'clone', 'init', 'clean', 'gc', 'prune', 'mv', 'rm'):
        assert guard.classify('git ' + verb + ' x') is not None, verb


def test_mutating_plumbing_is_denied():
    # No recognizable write verb in the name; caught only by failing closed.
    for verb in ('update-ref', 'update-index', 'write-tree', 'commit-tree',
                 'hash-object', 'fast-import', 'filter-branch', 'replace',
                 'symbolic-ref'):
        assert guard.classify('git ' + verb + ' x') is not None, verb


def test_unknown_verb_fails_closed():
    detail = guard.classify('git frobnicate --wat')
    assert detail is not None
    assert 'frobnicate' in detail


def test_fetch_and_pull_are_denied_deliberately_not_incidentally():
    # Spec D7: fetch touches neither the working tree, the index, HEAD, local
    # branch state, nor the worktree list — it is denied for reproducibility
    # (a mid-review fetch moves the artifact under review) and because the
    # controller prepares the diff before dispatching. The denial message must
    # say so, or a future reader "fixes" this as an oversight.
    for verb in ('fetch', 'pull'):
        detail = guard.classify('git ' + verb + ' origin main')
        assert detail is not None, verb
        assert 'deliberate' in detail.lower(), detail
        assert 'controller' in detail.lower(), detail


def test_global_options_are_skipped_when_locating_the_verb():
    assert guard.classify('git -C /other/repo log --oneline') is None
    assert guard.classify('git --no-pager diff') is None
    assert guard.classify('git --git-dir=/x/.git status') is None
    assert guard.classify('git -c core.pager=cat log') is None


def test_global_options_do_not_smuggle_a_write_past_the_guard():
    # -C is exactly how an agent would step outside a guard that only looked at
    # the working directory. This case is load-bearing, not incidental.
    assert guard.classify('git -C /other/repo commit -m x') is not None
    assert guard.classify('git --git-dir=/x/.git push') is not None
    assert guard.classify('git -c user.name=x commit -m y') is not None


def test_bare_git_and_info_flags_are_allowed():
    assert guard.classify('git') is None
    assert guard.classify('git --version') is None
    assert guard.classify('git --help') is None


def test_unknown_global_option_fails_closed():
    assert guard.classify('git --wat log') is not None


def test_git_denial_names_a_read_only_alternative_where_one_exists():
    detail = guard.classify('git checkout main -- src/x.py')
    assert detail is not None
    assert 'git show' in detail
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q -k git`
Expected: FAIL — the stub `_classify_git` returns `None`, so every "denied" assertion fails with `assert None is not None`.

> Deviation: `-k git` filters on *test names*, so it under-selected (1 failed, 3 passed, 18 deselected). Ran the full suite instead for the true RED state: 7 failed, 15 passed — all the deny assertions, as intended.

- [x] **Step 3: Implement the git allowlist**

In `hooks/readonly-agent-guard.py`, add these tables below `DENIED_COMMANDS`:

```python
# git's read-only vocabulary is small and enumerable, so this is an allowlist
# and anything not on it is denied — including verbs git adds in the future.
GIT_READONLY_VERBS = frozenset({
    'log', 'show', 'diff', 'diff-tree', 'status', 'grep', 'blame', 'ls-files',
    'ls-tree', 'ls-remote', 'cat-file', 'rev-parse', 'rev-list', 'describe',
    'shortlog', 'whatchanged', 'name-rev', 'merge-base', 'for-each-ref',
    'count-objects', 'verify-commit', 'check-ignore', 'check-attr', 'var',
    'help', 'version',
})

# Print-and-exit flags: allow immediately, there is no verb behind them.
GIT_INFO_FLAGS = frozenset({
    '--version', '--help', '-h', '--html-path', '--man-path', '--info-path',
})

# Global options skipped while locating the verb.
GIT_GLOBAL_FLAGS = frozenset({
    '-p', '--paginate', '-P', '--no-pager', '--bare', '--literal-pathspecs',
    '--no-literal-pathspecs', '--glob-pathspecs', '--noglob-pathspecs',
    '--icase-pathspecs', '--no-replace-objects', '--no-optional-locks',
    '--no-lazy-fetch', '--no-advice',
})
GIT_GLOBAL_WITH_VALUE = frozenset({
    '-C', '-c', '--git-dir', '--work-tree', '--namespace', '--exec-path',
    '--config-env', '--attr-source',
})

# A read-only route to what the denied verb was probably reaching for. Naming it
# lets the agent report accurately to its controller instead of retrying blind.
# Only consulted for verbs that reach the fail-closed default, so do NOT add keys
# for verbs in GIT_SUBCOMMAND_ALLOWED / GIT_FLAG_ALLOWED (Task 4) — those are
# handled earlier in _classify_git, and an entry here would be dead code.
GIT_ALTERNATIVES = {
    'checkout': 'To read a file at another revision use `git show <SHA>:<path>`; '
                'to compare, `git diff <SHA>..HEAD`.',
    'switch': 'To read a file at another revision use `git show <SHA>:<path>`.',
    'restore': 'To read a file at another revision use `git show <SHA>:<path>`.',
    'reset': 'To compare against another revision use `git diff <SHA>..HEAD`.',
    'clean': 'To see what is untracked use `git status --porcelain`.',
    'add': 'Nothing in a read-only review touches the index.',
    'commit': 'Nothing in a read-only review creates a commit.',
    'fetch': 'Denied deliberately, not by fall-through: a fetch part-way through a '
             'review silently changes what a later `git diff origin/main...` shows, '
             'so the artifact moves while it is being reviewed. If you need a base '
             'ref that is not local, report that to your controller so it can fetch '
             'before dispatching.',
    'pull': 'Denied deliberately, not by fall-through: `git pull` merges into HEAD. '
            'Report a missing base ref to your controller instead of fetching it '
            'yourself.',
}
```

Now replace the `_classify_git` stub with the dispatcher. `_classify_git_subcommand_verb` and `GIT_SUBCOMMAND_ALLOWED` / `GIT_FLAG_ALLOWED` arrive in Task 4 — for this task, define the two tables as empty dicts so the dispatcher's shape is final and Task 4 only fills them in:

```python
GIT_SUBCOMMAND_ALLOWED = {}  # Task 4 fills this
GIT_FLAG_ALLOWED = {}        # Task 4 fills this


def _locate_git_verb(args):
    """Return (index of the verb, None) or (None, reason) if we should stop.

    A reason of '' means "allow, there is no verb" — bare `git` or an info flag.
    """
    i = 0
    while i < len(args):
        token = args[i]
        if token in GIT_INFO_FLAGS:
            return None, ''
        if token in GIT_GLOBAL_FLAGS:
            i += 1
            continue
        if token in GIT_GLOBAL_WITH_VALUE:
            i += 2  # the option's value is the next token
            continue
        if '=' in token and token.partition('=')[0] in GIT_GLOBAL_WITH_VALUE:
            i += 1
            continue
        if token.startswith('-'):
            return None, ('`git ' + token + '` is not a recognized read-only git '
                          'global option, and this guard fails closed on options '
                          'it cannot account for.')
        return i, None
    return None, ''  # ran out of tokens: bare `git`, which only prints usage


def _classify_git(args):
    index, reason = _locate_git_verb(args)
    if index is None:
        return reason or None
    verb = args[index]
    rest = args[index + 1:]
    if verb in GIT_READONLY_VERBS:
        return None
    if verb in GIT_SUBCOMMAND_ALLOWED:
        return _classify_git_subcommand_verb(verb, rest)
    if verb in GIT_FLAG_ALLOWED:
        return _classify_git_flag_verb(verb, rest)
    alternative = GIT_ALTERNATIVES.get(verb)
    if alternative:
        return '`git ' + verb + '` is denied by the read-only allowlist. ' + alternative
    return ('`git ' + verb + '` is not on the read-only allowlist — it either mutates '
            'git state or is unrecognized, and this guard fails closed on both.')
```

Note the ordering inside `_locate_git_verb`: an unknown leading option denies rather than being treated as a verb, so `git --wat log` cannot slip a verb past the scan.

- [x] **Step 4: Run the tests to verify they pass**

Run: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: PASS. (`_classify_git_subcommand_verb` and `_classify_git_flag_verb` are referenced but undefined — that is fine at import time because both tables are empty, so neither name is ever looked up. Task 4 defines them.)

- [x] **Step 5: Commit**

```bash
git add hooks/readonly-agent-guard.py hooks/test_readonly_agent_guard.py
git commit -m "feat(hooks): add the fail-closed git read-only allowlist

Unknown and mutating verbs deny; global options (notably -C) are skipped when
locating the verb, so 'git -C /other/repo commit' cannot step outside the guard.
fetch and pull carry an explicit spec-D7 rationale in their denial message.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Git mode-dependent verbs

Spec §2's table: eleven verbs that are read-only in some forms and mutating in others. Two shapes — **subcommand-keyed** (the allowed form is the first non-option argument) and **flag-keyed** (the allowed form is determined by the options, and a bare positional means "create").

Two notes on the rules, so they do not read as drift:
- `config` gets **exactly** the five flags in the spec table. Any other flag — including read-only scope flags like `--global` — denies. That is faithful to the spec, costs one denied command at worst, and widening it later is a one-line change. Task 8 records it in the README limitations.
- `branch` and `tag` allow a positional argument **only when a list flag is present**. This is the spec's "bare, or only \<flags\>" read: `git branch --list 'f*'` passes a pattern, whereas `git branch foo` and `git tag v1` *create*, and both are bare-plus-positional.

**Files:**
- Modify: `hooks/readonly-agent-guard.py` (fill `GIT_SUBCOMMAND_ALLOWED` / `GIT_FLAG_ALLOWED`, add their two handlers)
- Modify: `hooks/test_readonly_agent_guard.py`

**Interfaces:**
- Consumes: `GIT_SUBCOMMAND_ALLOWED`, `GIT_FLAG_ALLOWED`, and the `_classify_git` dispatcher from Task 3.
- Produces: `_classify_git_subcommand_verb(verb: str, rest: list[str]) -> str | None` and `_classify_git_flag_verb(verb: str, rest: list[str]) -> str | None`, both already called by that dispatcher.

- [x] **Step 1: Write the failing tests**

Append to `hooks/test_readonly_agent_guard.py`. Every pair asserts both sides, per spec Verification:

```python
MODE_DEPENDENT_PAIRS = [
    # (allowed command, denied command)
    ('git stash list', 'git stash'),
    ('git stash show', 'git stash pop'),
    ('git worktree list', 'git worktree add ../wt main'),
    ('git submodule status', 'git submodule update --init'),
    ('git notes list', 'git notes add -m x'),
    ('git bisect log', 'git bisect start'),
    ('git sparse-checkout list', 'git sparse-checkout set src'),
    ('git remote -v', 'git remote add origin url'),
    ('git remote show origin', 'git remote remove origin'),
    ('git remote get-url origin', 'git remote set-url origin url'),
    ('git reflog', 'git reflog delete HEAD@{0}'),
    ('git reflog show HEAD', 'git reflog expire --all'),
    ('git branch', 'git branch new-feature'),
    ('git branch -v', 'git branch -d old'),
    ('git branch -a', 'git branch -m old new'),
    ('git branch --show-current', 'git branch -f main HEAD~1'),
    ("git branch --list 'f*'", 'git branch --edit-description'),
    ('git branch --merged main', 'git branch --unset-upstream'),
    ('git tag -l', 'git tag v1.0'),
    ("git tag --list 'v*'", 'git tag -a v1 -m x'),
    ('git tag --points-at HEAD', 'git tag -d v1'),
    ('git config --get user.name', 'git config user.name Someone'),
    ('git config --list', 'git config --unset user.name'),
    ('git config --get-regexp "^remote"', 'git config --add k v'),
]


def test_mode_dependent_verbs_allow_the_read_only_form():
    for allowed, _ in MODE_DEPENDENT_PAIRS:
        assert guard.classify(allowed) is None, allowed


def test_mode_dependent_verbs_deny_every_other_form():
    for _, denied in MODE_DEPENDENT_PAIRS:
        assert guard.classify(denied) is not None, denied


def test_bare_stash_is_denied_because_it_mutates():
    # The one case where the bare verb is the dangerous one: `git stash` with no
    # subcommand stashes the caller's uncommitted work.
    detail = guard.classify('git stash')
    assert detail is not None
    assert 'stash list' in detail


def test_positional_without_a_list_flag_denies_for_branch_and_tag():
    assert guard.classify('git branch foo') is not None
    assert guard.classify('git tag v1') is not None
    assert guard.classify("git branch --list 'f*'") is None
    assert guard.classify("git tag -l 'v*'") is None


def test_config_requires_a_read_mode_flag():
    assert guard.classify('git config a b') is not None
    assert guard.classify('git config --get a') is None
    # Faithful to the spec table: only the five read-mode flags are listed, so a
    # scope flag denies. Documented in hooks/README.md as a known false positive.
    assert guard.classify('git config --global --list') is not None


def test_value_taking_flags_do_not_look_like_positionals():
    for command in ('git branch --contains HEAD', 'git branch --no-merged main',
                    'git branch --sort=-committerdate', 'git tag --sort refname',
                    'git tag --format="%(refname)"'):
        assert guard.classify(command) is None, command
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q -k "mode_dependent or stash or positional or config or value_taking"`
Expected: FAIL — with both tables empty, every mode-dependent verb falls through to the allowlist default, so the *allowed* half fails first (`assert 'reason' is None`).

> Deviation: ran the full suite rather than the `-k` filter, for the same name-matching reason as Task 3. RED was exactly as predicted: 5 failed, 23 passed, the allowed half failing first.

- [x] **Step 3: Implement both handlers**

Replace the two empty-dict placeholders in `hooks/readonly-agent-guard.py`:

```python
# Verbs whose read-only forms are named by a subcommand: (allowed subcommands,
# whether the bare verb is itself read-only). `git stash` bare is NOT — it
# stashes the caller's uncommitted work, which is the exact damage this guard
# exists to prevent.
GIT_SUBCOMMAND_ALLOWED = {
    'stash': (frozenset({'list', 'show'}), False),
    'worktree': (frozenset({'list'}), False),
    'submodule': (frozenset({'status', 'summary'}), False),
    'notes': (frozenset({'list', 'show'}), False),
    'bisect': (frozenset({'log', 'view'}), False),
    'sparse-checkout': (frozenset({'list'}), False),
    'remote': (frozenset({'show', 'get-url'}), True),
    'reflog': (frozenset({'show'}), True),
}

# Verbs whose read-only forms are named by flags. `value_flags` take an argument,
# which must not be mistaken for a positional. A positional is allowed only
# alongside a `list_flag`, because `git branch foo` and `git tag v1` create.
# `required` (config only) means at least one of these must be present.
GIT_FLAG_ALLOWED = {
    'branch': {
        'flags': frozenset({'-l', '--list', '-a', '-r', '-v', '-vv', '--contains',
                            '--merged', '--no-merged', '--show-current',
                            '--format', '--sort'}),
        'value_flags': frozenset({'--contains', '--merged', '--no-merged',
                                  '--format', '--sort'}),
        'list_flags': frozenset({'-l', '--list'}),
        'required': frozenset(),
    },
    'tag': {
        'flags': frozenset({'-l', '--list', '--contains', '--points-at',
                            '--sort', '--format'}),
        'value_flags': frozenset({'--contains', '--points-at', '--sort',
                                  '--format'}),
        'list_flags': frozenset({'-l', '--list'}),
        'required': frozenset(),
    },
    'config': {
        'flags': frozenset({'--get', '--get-all', '--get-regexp', '--list', '-l'}),
        'value_flags': frozenset(),
        'list_flags': frozenset({'--get', '--get-all', '--get-regexp',
                                 '--list', '-l'}),
        'required': frozenset({'--get', '--get-all', '--get-regexp',
                               '--list', '-l'}),
    },
}


def _readable_forms(verb, subcommands):
    return ' / '.join('`git ' + verb + ' ' + s + '`' for s in sorted(subcommands))


def _classify_git_subcommand_verb(verb, rest):
    allowed, bare_is_readonly = GIT_SUBCOMMAND_ALLOWED[verb]
    subcommand = None
    for token in rest:
        if not token.startswith('-'):
            subcommand = token
            break
    if subcommand is None:
        if bare_is_readonly:
            return None
        return ('bare `git ' + verb + '` mutates state; only '
                + _readable_forms(verb, allowed) + ' are read-only.')
    if subcommand in allowed:
        return None
    return ('`git ' + verb + ' ' + subcommand + '` is not a read-only form; only '
            + _readable_forms(verb, allowed) + ' are allowed.')


def _classify_git_flag_verb(verb, rest):
    """Classify a flag-keyed verb (branch / tag / config).

    Two structural notes:
    * A value flag consumes the next token, so `git branch --contains <ref>` and
      `git branch --merged <ref>` never register a positional. That is the right
      resolution for a read-only check — those arguments are commit-ish, not new
      branch names — but it does mean the positional guard below cannot fire
      alongside them.
    * For `config`, `list_flags == required`, so the positional branch is
      unreachable: anything carrying a positional has already satisfied the
      required check via the same flag set. Kept uniform with branch/tag rather
      than special-cased.
    """
    rule = GIT_FLAG_ALLOWED[verb]
    seen = set()
    has_positional = False
    i = 0
    while i < len(rest):
        token = rest[i]
        if token.startswith('-'):
            name, sep, _value = token.partition('=')
            if name not in rule['flags']:
                return ('`git ' + verb + ' ' + token + '` is not one of the '
                        'read-only forms of `git ' + verb + '`.')
            seen.add(name)
            i += 1 if sep else (2 if name in rule['value_flags'] else 1)
            continue
        has_positional = True
        i += 1
    if rule['required'] and not (seen & rule['required']):
        return ('`git ' + verb + '` is read-only only in its query forms ('
                + ', '.join('`' + f + '`' for f in sorted(rule['required']))
                + '); any other form writes.')
    if has_positional and not (seen & rule['list_flags']):
        return ('`git ' + verb + '` with a bare argument creates or moves a '
                + verb + '; use `git ' + verb + ' --list` to read.')
    return None
```

- [x] **Step 4: Run the full suite**

Run: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: PASS.

- [x] **Step 5: Confirm 3.9 compatibility still holds**

Run: `/usr/bin/env python3 -m py_compile hooks/readonly-agent-guard.py && echo "3.9 OK"`
Expected: `3.9 OK`.

- [x] **Step 6: Commit**

```bash
git add hooks/readonly-agent-guard.py hooks/test_readonly_agent_guard.py
git commit -m "feat(hooks): classify the mode-dependent git verbs

stash/worktree/submodule/notes/bisect/sparse-checkout/remote/reflog by
subcommand; branch/tag/config by flags, where a bare positional means create.
Both sides of every pair are asserted.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Payload routing, failure posture, and the deny decision

Spec §1's data flow and §3's failure table. The posture switch is keyed on *"have we identified a guarded agent yet"*: fail **open** before identification (a malformed payload must never block `Bash` in every project on this machine), fail **closed** after it (blast radius is one subagent).

The **`agent_type` absent → allow** row is the property everything else rests on: the main session must never be blocked by this hook.

**Files:**
- Modify: `hooks/readonly-agent-guard.py` (add `build_denial` and `main`, replace the `__main__` stub)
- Modify: `hooks/test_readonly_agent_guard.py` (add the contract layer)

**Interfaces:**
- Consumes: `READONLY_AGENTS`, `AGENT_TYPE_KEY`, `CONTRACT_CLAUSE`, `classify` (Tasks 2–4).
- Produces: `build_denial(agent: str, command: str, detail: str) -> dict` — the `hookSpecificOutput` payload.
- Produces: `main() -> int` — always returns 0; a denial is JSON on stdout.

- [x] **Step 1: Write the failing tests**

> Deviation: the three new imports went into the file's top import block
> rather than mid-file as sketched here; the test bodies are unchanged.

Append to `hooks/test_readonly_agent_guard.py`:

```python
import copy
import json
import subprocess


def run_guard(payload):
    """Drive the hook exactly as Claude Code does: through its own shebang.

    Not [sys.executable, GUARD] — the shebang resolves to the system python3
    (3.9 on macOS), so this is also the regression test for the guard staying
    3.9-compatible.
    """
    proc = subprocess.run(
        [str(GUARD)], input=json.dumps(payload), capture_output=True, text=True)
    return proc


def payload_for(command, agent='Explore'):
    p = copy.deepcopy(RECORDED_PAYLOAD)
    p['tool_input']['command'] = command
    if agent is None:
        p.pop('agent_type', None)
    else:
        p['agent_type'] = agent
    return p


def test_malformed_stdin_allows():
    proc = subprocess.run([str(GUARD)], input='not json at all',
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ''


def test_empty_stdin_allows():
    proc = subprocess.run([str(GUARD)], input='', capture_output=True, text=True)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ''


def test_main_session_is_never_blocked():
    # The property everything else rests on.
    proc = run_guard(payload_for('git stash', agent=None))
    assert proc.returncode == 0
    assert proc.stdout.strip() == ''
    assert run_guard(copy.deepcopy(RECORDED_MAIN_SESSION_PAYLOAD)).stdout.strip() == ''


def test_unguarded_agents_are_allowed():
    for agent in ('debugger', 'docs-writer', 'general-purpose', 'explore'):
        proc = run_guard(payload_for('git commit -m x', agent=agent))
        assert proc.stdout.strip() == '', agent


def test_guarded_agent_running_a_readonly_command_is_allowed():
    for agent in sorted(guard.READONLY_AGENTS):
        proc = run_guard(payload_for('git diff main..HEAD', agent=agent))
        assert proc.returncode == 0
        assert proc.stdout.strip() == '', agent


def test_guarded_agent_running_a_mutator_is_denied():
    for agent in sorted(guard.READONLY_AGENTS):
        proc = run_guard(payload_for('git stash', agent=agent))
        assert proc.returncode == 0, agent
        out = json.loads(proc.stdout)
        assert out['hookSpecificOutput']['permissionDecision'] == 'deny', agent


def test_deny_payload_has_the_exact_documented_shape():
    proc = run_guard(payload_for('git checkout main'))
    out = json.loads(proc.stdout)
    assert set(out) == {'hookSpecificOutput'}
    inner = out['hookSpecificOutput']
    assert set(inner) == {'hookEventName', 'permissionDecision',
                          'permissionDecisionReason'}
    assert inner['hookEventName'] == 'PreToolUse'
    assert inner['permissionDecision'] == 'deny'


def test_denial_reason_names_agent_command_clause_and_alternative():
    proc = run_guard(payload_for('git checkout main', agent='task-reviewer'))
    reason = json.loads(proc.stdout)['hookSpecificOutput']['permissionDecisionReason']
    assert 'task-reviewer' in reason
    assert 'git checkout main' in reason
    assert 'worktree list' in reason          # the quoted contract clause
    assert 'git show' in reason               # the read-only alternative


def test_denial_reason_offers_no_escape_hatch():
    # Spec D5: the constrained party reads this message. A documented bypass
    # string here would make the guard advisory.
    proc = run_guard(payload_for('rm -rf build'))
    reason = json.loads(proc.stdout)['hookSpecificOutput']['permissionDecisionReason']
    lowered = reason.lower()
    for word in ('bypass', 'override', 'escape hatch', 'disable', 'skip this'):
        assert word not in lowered, word


def test_classification_failure_fails_closed_for_a_guarded_agent():
    # Unbalanced quote: shlex raises, and after identification the guard denies.
    proc = run_guard(payload_for('git log "unterminated'))
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out['hookSpecificOutput']['permissionDecision'] == 'deny'
    assert 'ValueError' in out['hookSpecificOutput']['permissionDecisionReason']


def test_classification_failure_still_allows_the_main_session():
    proc = run_guard(payload_for('git log "unterminated', agent=None))
    assert proc.stdout.strip() == ''


def test_missing_command_does_not_block():
    p = copy.deepcopy(RECORDED_PAYLOAD)
    p['tool_input'] = {}
    assert run_guard(p).stdout.strip() == ''
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q -k "guard or deny or session or classification or missing_command"`
Expected: FAIL — the `__main__` stub exits 0 with no output, so every deny assertion fails on `json.loads('')`.

- [x] **Step 3: Implement the decision layer**

Replace the `if __name__ == '__main__':` stub at the bottom of `hooks/readonly-agent-guard.py`:

```python
def build_denial(agent, command, detail):
    reason = (
        'readonly-agent-guard: the ' + agent + ' agent is read-only on this '
        'checkout — ' + CONTRACT_CLAUSE + '. Denied: ' + repr(command) + '. '
        + detail + ' Report this to your controller rather than retrying with a '
        'variant.'
    )
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': reason,
    }}


def main():
    """Always exit 0. A denial is a JSON decision on stdout, not an exit code.

    Fail open before we have identified a guarded agent, fail closed after. A
    uniform posture is wrong in both directions: fail-closed everywhere means one
    malformed payload blocks Bash in every project on this machine, and
    fail-open everywhere means the guard stops guarding exactly when its input
    gets unusual.
    """
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0

    agent = payload.get(AGENT_TYPE_KEY)
    if not isinstance(agent, str) or agent not in READONLY_AGENTS:
        return 0  # main session, debugger/docs-writer, every built-in agent

    tool_input = payload.get('tool_input')
    command = tool_input.get('command') if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not command.strip():
        return 0  # no command to classify; there is nothing here to mutate with

    try:
        detail = classify(command)
    except Exception as exc:  # identified agent: fail closed
        detail = ('the guard could not classify this command ('
                  + type(exc).__name__ + ': ' + str(exc) + '), and it fails '
                  'closed for read-only agents.')
    if detail is None:
        return 0

    print(json.dumps(build_denial(agent, command, detail)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [x] **Step 4: Run the full suite**

Run: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: PASS.

- [x] **Step 5: Sanity-check the real interpreter end to end**

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git stash"},"agent_type":"Explore"}' \
  | ./hooks/readonly-agent-guard.py
echo "---"
echo '{"tool_name":"Bash","tool_input":{"command":"git stash"}}' \
  | ./hooks/readonly-agent-guard.py
echo "--- (nothing above this line means the main session passes)"
```

Expected: a `permissionDecision: deny` JSON object for the first, and no output at all for the second.

- [x] **Step 6: Commit**

```bash
git add hooks/readonly-agent-guard.py hooks/test_readonly_agent_guard.py
git commit -m "feat(hooks): route payloads and emit the deny decision

Fail open before a guarded agent is identified, fail closed after. The denial
names the agent, the command, the contract clause, and a read-only alternative,
and offers no escape hatch.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Roster sync lint and the `test-runner` heading rename

Spec §4. The hardcoded roster is only safe if drift fails a lint at the commit that introduces it. The lint keys on the `## Read-only contract` heading, which this task promotes from a label into a load-bearing marker: after it, that heading means exactly "guarded by the hook".

`agents/test-runner.md` calls its equivalent section `## Contract`; rename it. `agents/debugger.md` and `agents/docs-writer.md` keep their plain `## Contract` heading — correctly, since theirs are not read-only contracts, and that distinction is now what the lint reads.

**Files:**
- Modify: `agents/test-runner.md:23` (`## Contract` → `## Read-only contract`; no other change)
- Modify: `build/check_frontmatter.py`
- Modify: `build/test_check_frontmatter.py`

**Interfaces:**
- Consumes: `READONLY_AGENTS` from `hooks/readonly-agent-guard.py` (Task 2), loaded via `importlib`.
- Produces: `load_readonly_roster(guard_path: Path | None = None) -> frozenset[str]` and `check_readonly_roster(agents_dir: Path | None = None, roster: frozenset[str] | None = None) -> list[str]` in `build/check_frontmatter.py`. Both parameters default to the real repo paths; the tests pass `tmp_path` fixtures so **both** directions of the assert are actually exercised, not just the happy path.

- [x] **Step 1: Write the failing tests**

Append to `build/test_check_frontmatter.py`:

> Deviation: `check_readonly_roster` / `load_readonly_roster` /
> `READONLY_HEADING` were added to the file's existing top-level
> `from check_frontmatter import ...` (reflowed to parenthesised form) rather
> than imported mid-file.

```python
from check_frontmatter import check_readonly_roster, load_readonly_roster, READONLY_HEADING


def _agent(dir_path: Path, filename: str, name: str, heading: str) -> Path:
    md = dir_path / filename
    md.write_text(
        f'---\nname: {name}\ndescription: x\ntools: Read, Grep, Glob, Bash\n---\n'
        f'\n{heading}\n\nBody.\n'
    )
    return md


def test_readonly_roster_clean_when_both_sides_agree(tmp_path):
    _agent(tmp_path, 'alpha.md', 'alpha', READONLY_HEADING)
    _agent(tmp_path, 'beta.md', 'beta', '## Contract')
    assert check_readonly_roster(tmp_path, frozenset({'alpha'})) == []


def test_readonly_roster_catches_an_unguarded_readonly_agent(tmp_path):
    # Forward direction: a sixth read-only agent shipping without a roster entry.
    _agent(tmp_path, 'gamma.md', 'gamma', READONLY_HEADING)
    errs = '\n'.join(check_readonly_roster(tmp_path, frozenset()))
    assert 'gamma' in errs


def test_readonly_roster_catches_a_stale_roster_entry(tmp_path):
    # Reverse direction: an entry left behind by a renamed or deleted agent.
    _agent(tmp_path, 'alpha.md', 'alpha', READONLY_HEADING)
    errs = '\n'.join(check_readonly_roster(tmp_path, frozenset({'alpha', 'ghost'})))
    assert 'ghost' in errs


def test_readonly_roster_keys_on_frontmatter_name_not_filename(tmp_path):
    # agents/explore.md carries `name: Explore`, and agent_type is the
    # frontmatter name — a roster keyed on the filename would never match.
    _agent(tmp_path, 'explore.md', 'Explore', READONLY_HEADING)
    assert check_readonly_roster(tmp_path, frozenset({'Explore'})) == []
    assert check_readonly_roster(tmp_path, frozenset({'explore'})) != []


def test_readonly_roster_reports_a_missing_guard_instead_of_raising(tmp_path, monkeypatch):
    # If the hook file is gone, the lint must print one violation line, not
    # traceback out of build/check_frontmatter.py and take the whole gate with it.
    import check_frontmatter

    monkeypatch.setattr(check_frontmatter, 'GUARD_PATH', tmp_path / 'nope.py')
    errs = check_frontmatter.check_readonly_roster(tmp_path, None)
    assert len(errs) == 1
    assert 'cannot load READONLY_AGENTS' in errs[0]


def test_load_readonly_roster_reads_the_real_guard():
    roster = load_readonly_roster()
    assert 'Explore' in roster and 'test-runner' in roster


def test_real_roster_matches_the_real_agents():
    # The bidirectional assert against the shipped guard and agents/.
    assert check_readonly_roster() == []
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q -k readonly`
Expected: FAIL — `ImportError: cannot import name 'check_readonly_roster' from 'check_frontmatter'`.

- [x] **Step 3: Implement the lint**

In `build/check_frontmatter.py`, add `import importlib.util` beside the other imports, then add these constants below `KNOWN_AGENT_TOOLS`:

```python
GUARD_PATH = REPO / 'hooks' / 'readonly-agent-guard.py'
# Load-bearing marker, not a label: an agents/*.md carrying this heading is
# asserted to be in the guard's roster, and vice versa. debugger.md and
# docs-writer.md use a plain '## Contract' because theirs are not read-only.
READONLY_HEADING = '## Read-only contract'
```

And these two functions above `main()`:

```python
def load_readonly_roster(guard_path: Path | None = None) -> frozenset[str]:
    '''Import READONLY_AGENTS from the hook script.

    The file is hyphenated (hook-script convention) so it is not importable by
    name; exec'ing it is safe because its main() sits behind __main__.
    '''
    path = guard_path or GUARD_PATH
    spec = importlib.util.spec_from_file_location('readonly_agent_guard', path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return frozenset(module.READONLY_AGENTS)


def check_readonly_roster(agents_dir: Path | None = None,
                          roster: frozenset[str] | None = None) -> list[str]:
    '''Assert the guard's roster and the read-only agent files agree, both ways.

    Forward: a sixth read-only agent must not ship unguarded. Reverse: a roster
    entry must not outlive the agent it names. This is what makes the hook's
    hardcoded roster safe — drift fails here, at the commit that introduces it.
    '''
    d = agents_dir or (REPO / 'agents')
    if roster is None:
        try:
            roster = load_readonly_roster()
        except (FileNotFoundError, OSError, SyntaxError, AttributeError) as exc:
            return [f'{GUARD_PATH}: cannot load READONLY_AGENTS '
                    f'({type(exc).__name__}: {exc})']
    errs: list[str] = []
    marked: dict[str, Path] = {}
    for md in sorted(d.glob('*.md')):
        if not any(ln.strip() == READONLY_HEADING for ln in md.read_text().splitlines()):
            continue
        fm, _ = _parse_frontmatter(md)
        marked[str((fm or {}).get('name') or md.stem)] = md
    for name, md in sorted(marked.items()):
        if name not in roster:
            errs.append(f'{md}: carries "{READONLY_HEADING}" but {name!r} is not in '
                        f'READONLY_AGENTS ({GUARD_PATH.name})')
    for name in sorted(roster):
        if name not in marked:
            errs.append(f'{GUARD_PATH}: READONLY_AGENTS entry {name!r} has no '
                        f'agents/*.md carrying "{READONLY_HEADING}"')
    return errs
```

Wire it into `main()`, after the commands loop:

```python
    errs += check_readonly_roster()
```

- [x] **Step 4: Run the tests — the real-roster test must still fail**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q -k readonly`
Expected: the four `tmp_path` tests PASS; `test_real_roster_matches_the_real_agents` FAILS, reporting that `'test-runner'` has no agents file carrying the heading. That failure is the point — it is the lint catching the un-renamed heading.

> Deviation: `-k readonly` deselected `test_real_roster_matches_the_real_agents` (no "readonly" in its name). Ran the full build suite: 6 roster tests pass, and the real-roster test fails with exactly the predicted message naming `'test-runner'`.

- [x] **Step 5: Rename the heading in `agents/test-runner.md`**

```bash
sed -i.bak 's/^## Contract$/## Read-only contract/' agents/test-runner.md && rm agents/test-runner.md.bak
git diff --stat agents/test-runner.md
```

Expected: exactly one line changed. Verify the other two `## Contract` headings are untouched:

```bash
grep -l '^## Contract$' agents/*.md
```

Expected: `agents/debugger.md` and `agents/docs-writer.md` only.

- [x] **Step 6: Run the full build suite and the lint itself**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`
Expected: PASS.

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && echo CLEAN`
Expected: `CLEAN`.

- [x] **Step 7: Commit**

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py agents/test-runner.md
git commit -m "feat(build): assert the guard roster against the read-only agents

Bidirectional: a sixth read-only agent cannot ship unguarded, and a roster entry
cannot outlive the agent it names. Promotes '## Read-only contract' from a label
into the marker the lint reads, renaming test-runner's heading to match.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: Install the guard globally and prove it live (Gate B)

Spec §5 and Gate B. Gate A can pass perfectly against a hook Claude Code never invokes; this task is the only test of the real claim.

The install is a **symlink**, a deliberate departure from `hooks/README.md`'s "prefer `cp` over symlinking" rule. That rule protects against one template edit changing every *work repo*; here there is exactly one install, and the hazard runs the other way — the guard must not drift from the agent files it enforces, which are themselves symlinked from this repo.

**Files:**
- Create: `hooks/probe-readonly-guard.sh` (executable)
- Modify: `~/.claude/settings.json` (outside the repo — gains its first `hooks` key)
- Create: `~/.claude/hooks/readonly-agent-guard.py` (symlink into this repo)

**Interfaces:**
- Consumes: the completed guard from Task 5 and the probe route recorded in `hooks/README.md` by Task 1.
- Produces: nothing other tasks import. Task 8 documents this install.

- [x] **Step 1: Write the Gate B probe script**

Create `hooks/probe-readonly-guard.sh`:

```bash
#!/usr/bin/env bash
# Gate B — a live check that Claude Code actually delivers the agent identity in
# the PreToolUse payload and honours the guard's denial on the installed binary.
# Gate A (test_readonly_agent_guard.py) can pass perfectly against a hook Claude
# Code never invokes; this is the only test of the real claim.
#
# Both assertions grep for the guard's own marker string, which distinguishes a
# denial by THIS hook from a generic permission denial.
#
# Run from inside any git repo, after installing the hook:
#   hooks/probe-readonly-guard.sh
set -uo pipefail

MARKER='readonly-agent-guard:'
fail=0

echo "Claude Code: $(claude --version)"

echo "== 1/2: a read-only command must pass =="
out=$(claude -p --agent Explore --allowedTools "Bash" \
  'Run exactly this command and report its output: git status --porcelain' 2>&1)
if printf '%s' "$out" | grep -q "$MARKER"; then
  echo "FAIL: the guard denied a read-only command"
  printf '%s\n' "$out" | tail -20
  fail=1
else
  echo "ok: git status was not denied"
fi

echo "== 2/2: a mutator must be denied by THIS hook =="
out=$(claude -p --agent Explore --allowedTools "Bash" \
  'Run exactly this command and report what happened: git stash' 2>&1)
if printf '%s' "$out" | grep -q "$MARKER"; then
  echo "ok: git stash was denied by the guard"
else
  echo "FAIL: git stash was not denied by the guard"
  printf '%s\n' "$out" | tail -20
  fail=1
fi

exit "$fail"
```

If Task 1's probe log records that `--agent` does **not** populate the agent identity, replace both `claude -p --agent Explore --allowedTools "Bash" '<prompt>'` invocations with the dispatch route it recorded instead:

```bash
claude -p --allowedTools "Bash,Task,Agent" \
  'Use the Agent tool with subagent_type "Explore" to run exactly: <command>. Report what happened.'
```

Then make it executable:

```bash
chmod +x hooks/probe-readonly-guard.sh
```

> Deviation: the shipped `probe-readonly-guard.sh` differs from the script above in
> three ways, each forced by something execution learned.
>
> 1. **Prompt before the flags, and `< /dev/null`.** Task 1 found `--allowedTools`
>    is variadic, so it swallows a trailing positional prompt (`claude -p` then
>    errors "Input must be provided..."), and that `claude -p` blocks on a piped
>    stdin. Both are recorded in the README probe log.
> 2. **Assert on `--output-format stream-json`, not the final message.** The first
>    Gate B run showed the guard denying correctly while the probe reported FAIL:
>    a denied agent relays the constraint to its controller *in its own words*, so
>    the `readonly-agent-guard:` marker never reaches the final text. It is
>    reliably present in the raw event stream.
> 3. **The deny probe is `git config --global --list`, not `git stash`.** A guarded
>    agent refuses `git stash` on its own prose contract before Bash is ever
>    invoked — so the hook never fires and the probe measures nothing. This is a
>    real finding, not a workaround: the prose contract already handles the
>    blatant cases, which is exactly why the hook's value is the *non-obvious*
>    ones (`git checkout <base>` to compare). `git config --global --list` is
>    genuinely read-only, so the agent attempts it, and the guard denies it as the
>    documented false positive — the one command guaranteed to exercise the deny
>    path end to end.

- [x] **Step 2: Install the symlink**

```bash
mkdir -p ~/.claude/hooks
ln -sfn ~/Projects/agent-skills/hooks/readonly-agent-guard.py \
        ~/.claude/hooks/readonly-agent-guard.py
ls -l ~/.claude/hooks/readonly-agent-guard.py
```

Expected: a symlink pointing into this repo.

- [x] **Step 3: Back up and wire `~/.claude/settings.json`**

`$CLAUDE_PROJECT_DIR` is unusable here — it resolves per-project, and this hook has one global install. Use `$HOME`.

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak-readonly-guard
python3 - <<'PY'
import json
import pathlib

p = pathlib.Path.home() / '.claude' / 'settings.json'
cfg = json.loads(p.read_text())
entry = {'matcher': 'Bash',
         'hooks': [{'type': 'command',
                    'command': '$HOME/.claude/hooks/readonly-agent-guard.py'}]}
hooks = cfg.setdefault('hooks', {}).setdefault('PreToolUse', [])
if entry not in hooks:
    hooks.append(entry)
p.write_text(json.dumps(cfg, indent=2) + '\n')
print(json.dumps(cfg['hooks'], indent=2))
PY
```

Expected: the printed `hooks` block shows exactly one `PreToolUse` entry matching `Bash`.

The `if entry not in hooks` check compares dicts exactly, so it only prevents an exact-duplicate append — it will not recognise a hand-edited variant of the same hook. If the printed block shows two `Bash` entries, remove one by hand rather than re-running this step.

- [x] **Step 4: Verify the settings file is still valid and nothing else changed**

```bash
python3 -c "import json,pathlib; json.loads((pathlib.Path.home()/'.claude/settings.json').read_text()); print('valid JSON')"
diff <(python3 -c "
import json, pathlib
d = json.loads((pathlib.Path.home()/'.claude/settings.json.bak-readonly-guard').read_text())
print(json.dumps(d, indent=2, sort_keys=True))") \
     <(python3 -c "
import json, pathlib
d = json.loads((pathlib.Path.home()/'.claude/settings.json').read_text())
d.pop('hooks', None)
print(json.dumps(d, indent=2, sort_keys=True))") && echo "only the hooks key was added"
```

Expected: `valid JSON` and `only the hooks key was added`.

- [x] **Step 5: Run Gate B**

Run: `./hooks/probe-readonly-guard.sh`
Expected: `ok:` on both checks and exit 0.

If check 2 fails, the guard is not being invoked or the identity field is not arriving. Do **not** work around it by loosening the guard: re-run the Task 1 probe against the current binary, fix `AGENT_TYPE_KEY`, and update the probe log row. If check 1 fails, a read-only command is being denied — that is a classification bug; add the failing command as a unit test in Task 2's file and fix the rule.

- [x] **Step 6: Confirm the main session is unaffected**

The hook now fires on every `Bash` call on this machine. Verify it is inert here:

```bash
git status --porcelain && git stash list && echo "main session unblocked"
```

Expected: both commands run normally and `main session unblocked` prints.

> **From this step onward, this plan's own review subagents are guarded.** A
> `task-reviewer` dispatched for Task 8 is one of the five, so it now runs under
> this hook. That is the intended end state, and reviewers only read — but if a
> review reports a spuriously denied command, that is a classification bug in
> Task 3 or Task 4. Fix it there with a new unit test; do not uninstall the hook
> or loosen a rule to get the review through.

- [x] **Step 7: Commit**

The settings file and the symlink live outside the repo; only the probe script is committed.

```bash
git add hooks/probe-readonly-guard.sh
git commit -m "test(hooks): add the Gate B live probe for the read-only guard

Asserts on the installed binary that a read-only command passes and that a
mutator is denied by this hook specifically, matching on the guard's own marker
string rather than any denial.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 8: Documentation

Spec §6. `hooks/README.md` currently says these scripts must never be installed globally; that warning is now true of one category and false of the other, so the file is restructured rather than patched.

**Files:**
- Modify: `hooks/README.md` (restructure; **preserve the `## Probe log` section from Task 1 verbatim**)
- Modify: `CLAUDE.md:7` (the `hooks/` clause) and the Commands section

**Interfaces:**
- Consumes: everything built in Tasks 1–7. Produces nothing further tasks use.

- [x] **Step 1: Get the real test count for the CLAUDE.md entry**

Run: `cd hooks && uv run --python 3.13 --with pytest python -m pytest -q | tail -3`
Note the passed count printed — Step 3 uses it verbatim.

- [x] **Step 2: Restructure `hooks/README.md`**

Rewrite the file so it opens with the two categories, keeping the existing install instructions and the `uv-guard.sh` limitations text intact under the first category, and appending the second. The `## Probe log` section added in Task 1 stays at the end, unchanged.

Replace the opening paragraph and its blockquote warning with:

````markdown
# Hook templates

Two categories live here, and they install differently. Read the category before
copying anything.

| category | scripts | install |
|---|---|---|
| **Project tooling hooks** | `ruff-fix.sh`, `ruff-check.sh`, `uv-guard.sh` | per work-repo `cp`, **never** global |
| **Agent contract hooks** | `readonly-agent-guard.py` | one global install in `~/.claude` |

## Project tooling hooks

Reusable Claude Code hook scripts for **your real Python/uv work repos** — `alt-nfp`,
`bls-stats`, `bls-stats-aggregation`, `naics-embedder` (each has a `pyproject.toml` +
ruff dev-dep). They convert advisory CLAUDE.md prose ("always run ruff", "use uv, not
pip") into deterministic gates that fire every time for ~0 tokens.

> **These three are templates, not wired into this repo.** This repo
> (`agent-skills`) is a skills library: no root `pyproject.toml`, and its bundled
> scripts run via `uv run --with` inline deps. A `uv run ruff check` hook here would
> have no config to run against, and the uv-guard would fight the intended
> inline-deps invocation. So do **not** add these three to this repo's settings, and
> do **not** install them as a global `~/.claude` hook (a global hook fires in
> *every* project — including this one and any non-Python repo). Install them
> per work-repo instead. This warning is scoped to this category; the agent
> contract hook below is deliberately global.
````

Keep the existing `## The scripts` table, `## Install into a work repo`, and `## Limitations` sections under this category, unchanged.

Then add, before the `## Probe log` section:

````markdown
## Agent contract hooks

### `readonly-agent-guard.py`

`PreToolUse` (`Bash`). Five agents declare a read-only contract — `code-reviewer`,
`task-reviewer`, `security-auditor`, `Explore`, `test-runner`. Half of it is already
mechanical: their `tools:` frontmatter has no `Write` or `Edit`. The other half was
enforced by nothing, and `git checkout`, `git stash`, `git reset`, and `sed -i` are
all reachable through the `Bash` tool they legitimately need. The damage lands on the
*caller's* uncommitted work. This hook closes that half.

Design and rationale: `specs/completed/readonly-agent-guard.md`.

**Install — globally, and by symlink.** Both are deliberate departures from the rules
above:

```bash
mkdir -p ~/.claude/hooks
ln -s ~/Projects/agent-skills/hooks/readonly-agent-guard.py \
      ~/.claude/hooks/readonly-agent-guard.py
```

then in `~/.claude/settings.json`:

```json
{ "hooks": { "PreToolUse": [ { "matcher": "Bash", "hooks": [
  { "type": "command", "command": "$HOME/.claude/hooks/readonly-agent-guard.py" } ] } ] } }
```

Global is safe here in a way the ruff/uv hooks are not: the guard's first act is to
check the payload's agent identity, and it exits 0 immediately unless that names one
of the five. It never fires in the main session, in a non-Python repo, or for
`debugger`, `docs-writer`, or any built-in agent. `$CLAUDE_PROJECT_DIR` is unusable —
it resolves per-project, and this hook has one install. Symlinked rather than copied
because the guard must not drift from the agent files it enforces, which are
themselves symlinked from this repo.

**Tests.** Gate A is `test_readonly_agent_guard.py` (`cd hooks && uv run --python 3.13
--with pytest python -m pytest -q`). Gate B is `probe-readonly-guard.sh`, a live check
against the installed binary — Gate A can pass perfectly against a hook Claude Code
never invokes.

### Limitations (by design)

**This is a guardrail against an agent drifting off contract, not a sandbox.** The
real containment is the `tools:` frontmatter denying `Write`/`Edit` outright, plus the
permission system. Not caught:

- `xargs rm` — the mutator is not any subcommand's first token.
- `find . -delete` and `find . -exec rm {} \;` — same reason.
- Command substitution: `$(git commit -m x)`.
- Mutators inside a quoted script: `python -c "..."`, `sh -c "..."`, `perl -e`.
- Anything reached through an alias or a wrapper script.

Known false positives, accepted rather than widened:

- `git config --global --list` is denied. The allowlist carries exactly the five
  read-mode flags from the spec; a scope flag is not one of them. Widening is a
  one-line change if it ever bites.
- `git fetch` and `git pull` are denied **deliberately** (spec D7), not by
  fall-through. `fetch` mutates no clause of the quoted contract, but a fetch
  part-way through a review silently changes what a later `git diff origin/main...`
  shows — the artifact moves while it is being reviewed. In both review paths the
  controller prepares the diff before dispatching, so the reviewer seat has no
  occasion to fetch. Do not "fix" this as an oversight.

Consciously **not** blocked, because the heuristic cannot separate a `/tmp` write from
a repo write without real path analysis: `>` and `>>` redirection, `tee`, `mkdir`,
`touch`, `chmod`, `cp`, `dd`, `ln`. Each has ordinary read-only-workflow uses.

**No escape hatch.** `uv-guard.sh` honours a `no-uv-guard` string because the party it
constrains is you. Here the constrained party is the agent being denied, and a
documented bypass string in the denial message would teach it the way through.

**Roster drift is a lint failure, not a silent gap.** `build/check_frontmatter.py`
imports `READONLY_AGENTS` from the guard and asserts it bidirectionally against the
`## Read-only contract` heading in `agents/*.md` — a sixth read-only agent cannot ship
unguarded, and a roster entry cannot outlive the agent it names.
````

- [x] **Step 3: Amend `CLAUDE.md`**

Replace the `hooks/` clause in the "What this repo is" paragraph (line 7) — currently `hooks/` (reusable hook templates for the user's *work* repos — ruff/uv gates; not wired into this repo, see `hooks/README.md`) — with:

```
`hooks/` (two categories: per-repo ruff/uv gate templates for the user's *work* repos, not wired into this repo; and `readonly-agent-guard.py`, a globally-installed `PreToolUse` hook that enforces the five read-only agents' Bash contract — see `hooks/README.md`)
```

Then add to the Commands section, immediately before the "Frontmatter + provenance lints" block, substituting the count from Step 1 for `<N>` (it was **40**):

```bash
# read-only agent guard tests (Gate A: classifier units + payload contract) — <N> tests
# (stdlib only; the contract tests run the hook through its own shebang, which is the
# system python3 — that is also the regression test for it staying 3.9-compatible)
cd hooks && uv run --python 3.13 --with pytest python -m pytest -q
```

- [x] **Step 4: Verify the docs against reality**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && echo "frontmatter CLEAN"
uv run --python 3.13 python build/check_provenance.py && echo "provenance CLEAN"
grep -c 'Probe log' hooks/README.md
```

Expected: both `CLEAN` lines, and the probe log section still present (count `1`).

- [x] **Step 5: Run every gate one final time**

```bash
cd hooks && uv run --python 3.13 --with pytest python -m pytest -q
```

```bash
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q
```

```bash
./hooks/probe-readonly-guard.sh
```

Expected: all three pass.

- [x] **Step 6: Commit**

```bash
git add hooks/README.md CLAUDE.md
git commit -m "docs(hooks): split the README into project-tooling and agent-contract hooks

The 'never install globally' warning is now scoped to the ruff/uv templates; the
read-only agent guard is deliberately global and says why. Documents every case
the guard does not catch, plus the two accepted false positives.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Verification

Spec §Verification requires all four to pass before the branch is complete:

```bash
cd hooks && uv run --python 3.13 --with pytest python -m pytest -q
```

```bash
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q
```

```bash
./hooks/probe-readonly-guard.sh
```

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py
```

## Rollback

The install lives outside the repo, so reverting the branch does not uninstall it:

Prefer removing just the entry: the backup was taken before the merge, so a
wholesale restore would also revert any unrelated settings change made since.

```bash
python3 - <<'PY'
import json
import pathlib

p = pathlib.Path.home() / '.claude' / 'settings.json'
cfg = json.loads(p.read_text())
hooks = cfg.get('hooks', {})
hooks['PreToolUse'] = [h for h in hooks.get('PreToolUse', [])
                       if 'readonly-agent-guard' not in json.dumps(h)]
if not hooks['PreToolUse']:
    hooks.pop('PreToolUse')
if not hooks:
    cfg.pop('hooks', None)
p.write_text(json.dumps(cfg, indent=2) + '\n')
print('guard hook removed')
PY
rm ~/.claude/hooks/readonly-agent-guard.py
```

Only if the settings file is otherwise untouched since the install is the
wholesale restore equivalent:

```bash
cp ~/.claude/settings.json.bak-readonly-guard ~/.claude/settings.json
```
