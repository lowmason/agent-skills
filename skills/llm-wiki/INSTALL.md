# Installing the llm-wiki skill on a new machine

This sets up the `llm-wiki` skill and a **fresh, empty wiki** on a machine that
has never had one — for example a work laptop that should keep its own wiki,
entirely separate from a personal one. The skill procedure lives in
[`SKILL.md`](SKILL.md); this file is the one-time machine setup.

## What you get, and what stays separate

- The **skill** (this directory) is shared config — it travels with the
  `agent-skills` repo and carries no wiki content.
- A **wiki** is a root directory (`$LLM_WIKI_ROOT`) holding *your* pages, raw
  sources, and session digests. It never leaves the machine and is not in any
  git remote unless you add one.

Personal and work wikis are **separate roots**. The bootstrap requires you to
name the root explicitly — there is no default — so content from one wiki can
never land in the other by accident.

## Prerequisites

- **Python 3.12 or newer** on `PATH` as `python3`. The wiki scripts are
  standard-library only — nothing to `pip install` to *use* the wiki. (`uv` is
  needed only to run the bundled test suite, below, which you can skip.)
- **git**, to get and update the `agent-skills` repo.
- **Claude Code**, if you want the skill to load automatically.

## Steps

### 1. Get the `agent-skills` repo

Clone it, or pull if it is already present:

```bash
git clone https://github.com/lowmason/agent-skills.git ~/Projects/agent-skills \
  || git -C ~/Projects/agent-skills pull
```

### 2. Make the skill discoverable to Claude Code

Symlink this skill into `~/.claude/skills/` (a symlink means later `git pull`s
update the skill in place — no re-copy):

```bash
mkdir -p ~/.claude/skills
ln -sfn ~/Projects/agent-skills/skills/llm-wiki ~/.claude/skills/llm-wiki
```

### 3. Bootstrap a wiki

Pick a root that signals which wiki it is (use a work-specific path on a work
machine). The root is the only required argument:

```bash
python3 ~/.claude/skills/llm-wiki/scripts/bootstrap_wiki.py ~/work-wiki
```

This scaffolds the skeleton, seeds `SCHEMA.md`, and installs `lint_wiki.py`,
`distill_sessions.py`, and `distill_specs.py` under `~/work-wiki/scripts/`. It
is safe to re-run: it **never overwrites existing wiki content**.

To seed topic folders for this wiki's own subjects (instead of the personal
default, which starts with no topic folders), add `--topic` once per subject:

```bash
python3 ~/.claude/skills/llm-wiki/scripts/bootstrap_wiki.py ~/work-wiki \
  --topic forecasting --topic risk
```

That creates `raw/forecasting/`, `raw/risk/`, `wiki/forecasting/`, and
`wiki/risk/`. Preview any run with `--dry-run` first to see the plan without
writing.

### 4. Point your environment at it, and verify

```bash
export LLM_WIKI_ROOT=~/work-wiki        # add to your shell profile to persist
python3 "$LLM_WIKI_ROOT/scripts/lint_wiki.py" "$LLM_WIKI_ROOT"
```

The lint must print `0 errors, 0 warnings, 0 info` and exit 0 — a freshly
bootstrapped wiki is clean from the first run. The skill is now operational:
`ingest`, `query`, `lint`, and `verify` all work against this root.

> **Export `LLM_WIKI_ROOT` in every session.** Without it the skill falls back
> to `~/research-wiki`; on a machine that has no such directory the skill will
> (correctly) offer to bootstrap one. Putting the `export` in your shell
> profile avoids the fallback.

## Keeping the scripts current

The wiki's installed scripts are copies of the skill's bundled versions, so
after a `git pull` of `agent-skills` they can fall behind. Check and refresh:

```bash
# report whether the installed scripts match the skill bundle (writes nothing)
python3 ~/.claude/skills/llm-wiki/scripts/bootstrap_wiki.py "$LLM_WIKI_ROOT" --check

# refresh only the installed scripts that differ (never touches SCHEMA.md or content)
python3 ~/.claude/skills/llm-wiki/scripts/bootstrap_wiki.py "$LLM_WIKI_ROOT" --force
```

`--check` exits non-zero when an installed script is missing or differs from the
skill bundle, or when the installed `SCHEMA.md` is an *older contract version*
than the bundle (a coupled tooling+schema update you should reconcile by hand).
A `SCHEMA.md` you have merely customized at the current version is reported but
does not fail. `--force` refreshes only the differing scripts and leaves your
`SCHEMA.md` and all wiki content untouched.

## Session digests and privacy

`distill_sessions.py` turns this machine's Claude Code history
(`~/.claude/projects`) into redacted digests under `$LLM_WIKI_ROOT/raw/sessions/`:

```bash
python3 "$LLM_WIKI_ROOT/scripts/distill_sessions.py" --source claude-code \
  ~/.claude/projects "$LLM_WIKI_ROOT/raw/sessions"
```

Redaction is always on and nothing leaves the machine, but on a work machine
this reads **work** session transcripts and writes a second at-rest copy of
that material outside `~/.claude`. Confirm that fits your employer's policy
before running it. `--help` documents the optional `--project` and `--since`
filters for scoping which sessions are distilled.
