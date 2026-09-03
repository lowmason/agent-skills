# Hooks

Two categories live here, and they install differently. Read the category before
copying anything.

| category | scripts | install |
|---|---|---|
| **Project tooling hooks** | `ruff-fix.sh`, `ruff-check.sh`, `uv-guard.sh` | per work-repo `cp`, **never** global |
| **Agent contract hooks** | `readonly-agent-guard.py` | one global install in `~/.claude` |

# Project tooling hooks

Reusable Claude Code hook scripts for **your real Python/uv work repos** — `alt-nfp`,
`bls-stats`, `bls-stats-aggregation`, `naics-embedder` (each has a `pyproject.toml` +
ruff dev-dep). They convert advisory CLAUDE.md prose ("always run ruff", "use uv, not
pip") into deterministic gates that fire every time for ~0 tokens.

> **These three are templates, not wired into this repo.** This repo (`agent-skills`)
> is a skills library: no root `pyproject.toml`, and its bundled scripts run via
> `uv run --with` inline deps. A `uv run ruff check` hook here would have no config to
> run against, and the uv-guard would fight the intended inline-deps invocation. So do
> **not** add these to this repo's settings, and do **not** install them as a global
> `~/.claude` hook (a global hook fires in *every* project — including this one and any
> non-Python repo). Install them per work-repo instead.
>
> This warning is scoped to this category. The agent contract hook below is
> deliberately global, and safe globally for a reason spelled out there.

## The scripts

| script | event | what it does |
|---|---|---|
| `ruff-fix.sh` | `PostToolUse` (`Write`/`Edit`) | `uv run ruff check --fix` + `ruff format` on the edited `*.py`. Best-effort (PostToolUse can't undo the edit). |
| `ruff-check.sh` | `Stop` | `uv run ruff check .`; exit 2 feeds unfixable lint back to Claude. Guarded by `stop_hook_active` against loops. |
| `uv-guard.sh` | `PreToolUse` (`Bash`) | Blocks `pip install`, bare `python`/`pytest`; injects the `uv …` form. Escape hatch: `no-uv-guard` in the command. |

All three parse the hook JSON payload from stdin with `jq` (already on your machine).

## Install into a work repo

From the target repo (e.g. `~/Projects/bls-stats`):

```bash
mkdir -p .claude/hooks
cp ~/Projects/agent-skills/hooks/{ruff-fix,ruff-check,uv-guard}.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
```

Then add to that repo's `.claude/settings.json` (merge if it exists):

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [
        { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/uv-guard.sh" } ] }
    ],
    "PostToolUse": [
      { "matcher": "Write|Edit", "hooks": [
        { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/ruff-fix.sh" } ] }
    ],
    "Stop": [
      { "hooks": [
        { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/ruff-check.sh" } ] }
    ]
  }
}
```

Optionally pair with a permission allowlist in the same file so the `uv` forms don't
prompt:

```json
{ "permissions": { "allow": ["Bash(uv run:*)", "Bash(uv add:*)", "Bash(uv sync:*)"] } }
```

Prefer `cp` over symlinking so a hook change can't silently alter every repo at once;
re-copy when you update a template here.

## Limitations (by design — tune per repo)

- **`uv-guard.sh` is a heuristic, not a shell parser.** It splits on `&& || ; | &` and
  checks each subcommand's *first* token, so `uv run python x.py`, `echo python`, and
  `which python` pass, while `python x.py` and `cat x | python -` are blocked. A
  `python` invoked deeper inside a quoted string could slip through — acceptable for a
  guardrail. Drop the `pytest)` case if you run pytest outside uv anywhere.
- **`ruff-fix.sh` is best-effort.** PostToolUse runs *after* the write and cannot undo
  it; if `uv run ruff` errors (e.g. the file isn't in a uv project) it silently no-ops.
  `ruff-check.sh` (Stop) is the backstop for anything `--fix` can't resolve.
- **Exit codes matter:** only exit 2 blocks and feeds stderr to Claude; exit 1 just
  logs. All three follow that convention.

# Agent contract hooks

## `readonly-agent-guard.py`

`PreToolUse` (`Bash`). Five agents declare a read-only contract — `code-reviewer`,
`task-reviewer`, `security-auditor`, `Explore`, `test-runner`. Half of it is already
mechanical: their `tools:` frontmatter has no `Write` or `Edit`. The other half was
enforced by nothing, and `git checkout`, `git stash`, `git reset`, and `sed -i` are
all reachable through the `Bash` tool they legitimately need. The damage lands on the
*caller's* uncommitted work — a reviewer that runs `git checkout <base>` to compare
destroys state the controller was mid-way through building. This hook closes that
half.

Design and rationale: `specs/completed/readonly-agent-guard.md`.

**Install — globally, and by symlink.** Both are deliberate departures from the rules
in the category above:

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
check the payload's `agent_type`, and it exits 0 immediately unless that names one of
the five. It never fires in the main session, in a non-Python repo, or for `debugger`,
`docs-writer`, or any built-in agent. `$CLAUDE_PROJECT_DIR` is unusable — it resolves
per-project, and this hook has one install. Symlinked rather than copied because the
guard must not drift from the agent files it enforces, which are themselves symlinked
from this repo.

Python rather than bash, against this directory's convention: `shlex` tokenizes quoted
commands properly (narrowing the "heuristic, not a shell parser" gap below), it drops
the `jq` dependency for a hook that now runs in every project, and the tests can import
the classifier directly. It runs under whatever `python3` is first on `PATH` — 3.9 on
macOS system Python — so the source stays 3.9-compatible, which the contract tests
enforce by invoking the script through its own shebang.

**Tests.** Gate A is `test_readonly_agent_guard.py`:

```bash
cd hooks && uv run --python 3.13 --with pytest python -m pytest -q
```

Gate B is `probe-readonly-guard.sh`, a live check against the installed binary — Gate A
can pass perfectly against a hook Claude Code never invokes. Two things that probe
learned the hard way, both now baked into the script: assert on the raw
`--output-format stream-json` events rather than the agent's final message (a denied
agent reports the constraint to its controller **in its own words**, paraphrasing the
marker away), and probe the deny path with `git config --global --list` rather than a
real mutator (a guarded agent refuses `git stash` on its own prose contract before Bash
is ever invoked, so the hook never fires and the probe measures nothing).

## Limitations (by design)

**This is a guardrail against an agent drifting off contract, not a sandbox.** The real
containment is the `tools:` frontmatter denying `Write`/`Edit` outright, plus the
permission system. Not caught:

- `xargs rm` — the mutator is not any subcommand's first token.
- `find . -delete` and `find . -exec rm {} \;` — same reason.
- Command substitution: `$(git commit -m x)`.
- Mutators inside a quoted script: `python -c "..."`, `sh -c "..."`, `perl -e`.
- Anything reached through an alias or a wrapper script.

Known false positives, accepted rather than widened:

- **`git config --global --list` is denied.** The allowlist carries exactly the five
  read-mode flags from the spec (`--get --get-all --get-regexp --list -l`); a scope
  flag is not one of them. Widening is a one-line change if it ever bites. Gate B
  currently relies on this case, so change both together.
- **`git fetch` and `git pull` are denied *deliberately*, not by fall-through.**
  `fetch` mutates no clause of the quoted contract, but a fetch part-way through a
  review silently changes what a later `git diff origin/main...` shows — the artifact
  moves while it is being reviewed. In both review paths the controller prepares the
  diff before dispatching, so the reviewer seat has no occasion to fetch. Do not "fix"
  this as an oversight; if a real case appears, flipping it is one line.

Consciously **not** blocked, because the heuristic cannot separate a `/tmp` write from
a repo write without real path analysis: `>` and `>>` redirection, `tee`, `mkdir`,
`touch`, `chmod`, `cp`, `dd`, `ln`. Each has ordinary read-only-workflow uses
(paginating output to a temp file, creating a scratch directory).

**No escape hatch.** `uv-guard.sh` honours a `no-uv-guard` string because the party it
constrains is you. Here the constrained party is the agent being denied, and a
documented bypass string in the denial message would teach it the way through — making
the guard advisory, which is the state it exists to leave.

**Roster drift is a lint failure, not a silent gap.** `build/check_frontmatter.py`
imports `READONLY_AGENTS` from the guard and asserts it bidirectionally against the
`## Read-only contract` heading in `agents/*.md` — a sixth read-only agent cannot ship
unguarded, and a roster entry cannot outlive the agent it names. That heading is a
load-bearing marker, not a label; `debugger.md` and `docs-writer.md` keep a plain
`## Contract` because theirs are not read-only contracts.

## Probe log

`readonly-agent-guard.py` depends on Claude Code putting the dispatched agent's
name in the `PreToolUse` payload. That is version-sensitive API surface, so it is
probed rather than assumed — re-run the probe after a binary update.

| date | Claude Code | finding |
|---|---|---|
| 2026-09-03 | 2.1.259 | `agent_type` arrives **top-level** on `PreToolUse(Bash)` payloads and is **absent** for main-session calls. Confirmed on the production path (an Agent-tool dispatch of `Explore`), which additionally carries a per-dispatch `agent_id`. The `claude -p --agent <name>` route populates `agent_type` too, without `agent_id` — so Gate B can use it. |

Two mechanics worth keeping with the row:

- `--allowedTools <tools...>` is **variadic**, so it swallows the positional
  prompt. Put the prompt first: `claude '<prompt>' -p --allowedTools "Bash"`.
- `claude -p` waits on stdin when it is a pipe; redirect `< /dev/null` in scripts.

The recorded payloads are frozen as `RECORDED_PAYLOAD` and
`RECORDED_MAIN_SESSION_PAYLOAD` in `test_readonly_agent_guard.py`;
`probe-readonly-guard.sh` re-checks the live behaviour end to end.
