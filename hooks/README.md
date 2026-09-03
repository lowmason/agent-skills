# Hook templates

Reusable Claude Code hook scripts for **your real Python/uv work repos** — `alt-nfp`,
`bls-stats`, `bls-stats-aggregation`, `naics-embedder` (each has a `pyproject.toml` +
ruff dev-dep). They convert advisory CLAUDE.md prose ("always run ruff", "use uv, not
pip") into deterministic gates that fire every time for ~0 tokens.

> **These are templates, not wired into this repo.** This repo (`agent-skills`) is a
> skills library: no root `pyproject.toml`, and its bundled scripts run via
> `uv run --with` inline deps. A `uv run ruff check` hook here would have no config to
> run against, and the uv-guard would fight the intended inline-deps invocation. So do
> **not** add these to this repo's settings, and do **not** install them as a global
> `~/.claude` hook (a global hook fires in *every* project — including this one and any
> non-Python repo). Install them per work-repo instead.

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
