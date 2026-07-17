# Plan 10: Model-routing setup (Sonnet default, Opus at structural checkpoints)

**Status: COMPLETE (2026-07-17)** — executed via executing-plans; nothing deferred
**Execution:** directly via `executing-plans` (config chore — too small for subagent dispatch)
**Spec:** none (context inline below; decided interactively 2026-07-17)

## Context (read this, skip the archaeology)

Analysis of 30 days of local transcripts (`~/.claude/projects/**/*.jsonl`) showed:
cache reads are 61% of token spend, output 21%, cache writes 17%, fresh input 1%;
the top 10 sessions (long agentic grinds) account for ~85% of monthly spend.

Decision: invert the default. Sessions run on **Sonnet** by default; **Opus** is used
at structural checkpoints only — planning/design sessions, reviewer agents, and manual
`/model opus` escalation when visibly needed. Explicitly rejected: any automatic
per-prompt router (a model cannot reliably detect tasks above its own ability, and
the failure mode — silent under-escalation — is invisible). Routing must be decided
by structure (plan vs. execute, task vs. review), never by per-prompt classification.

The plan file produced by `writing-plans` is the model boundary: plan on Opus,
execute on Sonnet in a fresh session, no mid-session switch needed.

## Tasks

### Task 1: Default model → sonnet in user settings

Edit `~/.claude/settings.json`: change `"model": "opus"` to `"model": "sonnet"`.
**Merge, don't replace** — preserve `enabledPlugins`, `advisorModel`, `theme`, `tui`,
and everything else. Leave `"advisorModel": "opus"` as is (advisor must be ≥ executor;
Sonnet executor + Opus advisor is a valid and desirable pair).

Verify: `jq . ~/.claude/settings.json` exits 0 and shows the new value alongside all
pre-existing keys.

### Task 2: Pin reviewer agents to Opus

Add `model: opus` to the YAML frontmatter of:
- `agents/code-reviewer.md`
- `agents/task-reviewer.md`

These are live via the `~/.claude/agents/` symlinks — no install step. Reviews are
high-leverage, low-token; they keep Opus judgment while sessions default to Sonnet.

Verify: frontmatter still parses (`uv run --python 3.13 --with pyyaml python
build/check_frontmatter.py` for the repo lints; if it doesn't cover `agents/`,
parse the two files' frontmatter with pyyaml directly).

### Task 3: Add routing policy to global CLAUDE.md

Append to `~/.claude/CLAUDE.md`:

```markdown
## Model routing
- Sessions default to Sonnet. Escalate deliberately; don't default to Opus.
- Opus at structural checkpoints: planning/design sessions (brainstorming → writing-plans)
  run under /model opus; execution sessions run on the Sonnet default with the plan file
  as the handoff. Reviewer agents are pinned to Opus in frontmatter.
- Mid-session escalation: /model opus when a task is visibly beyond Sonnet
  (accept the one-time cache re-write). Haiku for Explore-style search agents.
- Never route per-prompt by model self-assessment — route by task structure.
```

### Task 4: Wrap up

- Offer to commit the `agents/` changes (repo rule: commit only when the user asks).
- Run the plan-completion protocol (writing-plans § Plan Completion Protocol):
  mark up this plan, no deferred items expected, retire to `specs/plans/completed/`.

## Out of scope (work environment — user does this by hand)

Portable to the work machine, no repo needed:
1. `"model": "sonnet"` in work `~/.claude/settings.json` (or `ANTHROPIC_MODEL` env var).
2. If aliases are restricted, use full model IDs (`claude-sonnet-5`) or the gateway's
   IDs; remap via `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` /
   `ANTHROPIC_SMALL_FAST_MODEL` if needed.
3. Same session-boundary habit: plan on Opus, execute on Sonnet; `opusplan` unavailable
   there, so the split is manual.
