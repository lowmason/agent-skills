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

Python rather than bash, against this directory's convention: it tokenizes quoted
commands properly, reading words exactly as `shlex`'s posix mode does while keeping the
quoting `shlex` drops (narrowing the "heuristic, not a shell parser" gap below), it
drops the `jq` dependency for a hook that now runs in every project, and the tests can
import the classifier directly. It runs under whatever `python3` is first on the `PATH`
Claude Code hands its hooks, which need not be your shell's: an app launched from the
Dock can inherit launchd's `/usr/bin:/bin:/usr/sbin:/sbin`, where `python3` is macOS's
system Python 3.9. So the source stays 3.9-compatible.

**Tests.** Gate A is `test_readonly_agent_guard.py`, run both ways:

```bash
cd hooks && uv run --python 3.13 --with pytest python -m pytest -q \
  && uv run --python /usr/bin/python3 --with pytest python -m pytest -q
```

The 3.9 floor is checked on purpose, not by `PATH` order. Under `uv run` the shebang
resolves to uv's pinned interpreter, so a plain shebang run never reliably reached 3.9.
Instead each contract test runs twice through the script's own shebang: once on the
test's `PATH`, once on launchd's. The launchd run skips where that `python3` is missing
or is not 3.9 (`pytest -rs` prints the reason). It catches 3.10-only *syntax* anywhere
in the guard, but a 3.10-only *runtime* API (`zip(strict=)`, `isinstance(x, A | B)`)
only on a classifier branch some contract payload reaches. The second command runs the
whole suite, unit tests included, under `/usr/bin/python3`, so that API fails there on
any branch.

Gate B is `probe-readonly-guard.sh`, a live check against the installed binary — Gate A
can pass perfectly against a hook Claude Code never invokes. Three things that probe
learned the hard way, all now baked into the script:

- **Assert on the raw `--output-format stream-json` events, not the agent's final
  message.** A denied agent relays the constraint to its controller **in its own
  words**, paraphrasing the marker away.
- **Do not probe with a real mutator.** A guarded agent refuses `git stash` on its own
  prose contract before Bash is ever invoked, so the hook never fires and the probe
  measures nothing. (That the prose already stops the blatant cases is the point: the
  hook's value is the *non-obvious* ones, like a reviewer running `git checkout <base>`
  to compare.) Both deny probes use commands an agent has no contract reason to refuse.
- **"Read-only command passed" is not a liveness check.** Marker-absent also holds when
  the hook never ran at all. Check 2 (`git fetch`, denied by design under D7 and
  violating no clause of the prose contract) is the assertion that proves the hook is
  live.

## Limitations (by design)

**This is a guardrail against an agent drifting off contract, not a sandbox.** The real
containment is the `tools:` frontmatter denying `Write`/`Edit` outright, plus the
permission system. Each subcommand is classified by its command word, taken by its
basename (`/bin/rm` is `rm`) and found past redirections, assignments (`X=1`), leading
keywords (`!`, `if`, `then`, `do`, `coproc`, `noglob`, zsh's `-` modifier, …) and the
prefix utilities `env`, `command`, `exec`, `time`, `nohup` and `nice` with their
options, read as getopt reads them: short options clustered or apart, a value attached
or in the next word, and GNU long options by any unambiguous prefix (`--ch /tmp` is
`--chdir /tmp`). Subshells, brace groups, `$(…)` and `<(…)` are classified as commands
of their own. A quoted or escaped word is a word, never syntax: `git branch ')' -D feature`
deletes a branch. A redirection leaves with its target and with the file descriptor zsh
reads for it: one unquoted digit touching the operator (`2>&1`), or a `{name}` before
it (`exec {fd}>f`). Any other word before a redirection is an argument: `git branch 5
>f` creates branch `5`. A `{name}` descriptor is an ASCII identifier only, as zsh reads
it in the C locale the Bash tool runs under. A process substitution `<(…)` / `>(…)` is
one word, a path, never a redirection, so a digit or `{name}` touching it is part of
that word (`2<(true)` is one argument). A numeric glob `<1-5>` is one word too, and an
operator glued to one ends before it, since zsh has no `><` or `<<<<`: in `git ><1-1>
stash` the glob is the target of `>`, and `stash` is the verb. zsh takes `<<<` and `<<`
from a run of `<` first, so only a `<` left alone opens a glob (`<<<1-1>` is a
herestring of `1-1`), and a glob ends at its first `>`, so `<1->>><1->` is two globs
around a `>>`. An unquoted `$(…)`, a glob group `(…)` or a numeric glob where git or
`sed` takes a value or a verb, which zsh can split or expand into any number of words,
fails closed; quoting keeps a substitution one word (`git -C "$(pwd)" log`). Other globs
(`*`, `?`, `[…]`) are read as the literal word. Not caught:

- A command run by any other utility: `xargs rm`, `find . -exec rm {} \;`, and
  `find . -delete`, or read from what a command prints: `source <(echo rm x)`, and
  zsh's `source =(echo rm x)`.
- Mutators inside a quoted string, which is one word: `"$(git commit)"`, `eval '…'`,
  `env -S '…'`, `sh -c "..."`, `python -c "..."`, `perl -e`. (A quoted word made only
  of punctuation is also read as the syntax it spells, the way `eval` hands it back to
  the shell, so `eval echo \; rm x` is denied.)
- Command substitution in backticks. The tokenizer, like `shlex`, takes a backtick for
  an ordinary character, so `` echo `rm x` `` reads as the words `echo`, `` `rm `` and
  `` x` ``, and none of them is a denied command. `$(…)` is read as a command.
- A command word the shell produces by expansion (`c=rm; $c x`, `$(which rm) x`), by
  zsh's `=cmd` path expansion (`=rm x`), or by gluing to a brace (zsh runs `{rm x;}`).
- A word the guard does not recognise as an assignment, so the word becomes the command
  and the real command after it is never read: `arr[1]=x rm t`, `ä=x rm t`. `env` takes
  any `name=value` operand the same way, including after `--`: `env a-b=x rm t`,
  `env -- a-b=x rm t`.
- A line that needs the flat reading for one construct and the nested reading for
  another. Each of the eight readings below applies to the whole line, so no single
  reading catches both, and a reserved word or brace group before a git verb hides it:
  `{ git branch ]] HEAD; }`, `true && { git branch ]] HEAD; }`,
  `if [[ -n a ]] git branch ]] HEAD`.
- A glob qualifier glued to the command word, `git(.) stash`, which zsh expands to `git`
  only with `BARE_GLOB_QUAL` on and a file named `git` present. The Bash tool turns the
  option off, and there the word is an unmatched glob.
- A program run by an allowlisted git verb through configuration or the environment:
  `git -c core.fsmonitor=… status`, `git -c diff.external=… diff`,
  `GIT_EXTERNAL_DIFF=… git diff`.
- Anything reached through an alias, a function defined elsewhere, or a wrapper script.

Known false positives, accepted rather than widened:

- **Multi-line commands are read across lines only where the quoting is certain.**
  A quoted string may span lines, so a multi-line `python -c "..."` is classified
  by its leading token. A misread quote would join a later command into a word and
  hide it, so three rules deny instead of guessing:
  - A command containing `$(`, a backtick, `$'`, `${`, `$[`, `((`, `<<`, or a
    backslash-newline is split at every newline, as before multi-line support. The
    first seven carry nested quoting that the tokenizer, like `shlex`, cannot follow,
    and the shell joins continued lines in and out of quotes. So a quote spanning
    lines there fails closed, and so does every backslash-continued command (the line
    ending in `\` does not tokenize), and heredoc bodies are read as shell, line by
    line.
  - Comments are tokenized, never stripped. Where a `#` starts one depends on the
    shell and the context (zsh glob qualifiers, arithmetic, `${…}`), and a wrong
    guess either hides live code or lets a comment's apostrophe open a quote. So a
    quote spanning lines after an unquoted `#` on the same line fails closed, and a
    `# what's changed` line above a multi-line command is denied.
  - Every physical line is also classified alone, the pre-multi-line way. That is
    the backstop against a misread the first two rules miss, and its cost is a
    line inside a quoted script that begins with a denied word (`rm = 5`).

- **Every command is read eight ways, each reading applied to the whole line, and a
  denial in any of them stands.** Three things take a parser to tell apart, so each is
  read both ways. (Because a reading spans the whole line, a line that mixes a construct
  needing one reading with a construct needing another is caught by none — see the
  mixed-reading gap under "Not caught".)
  - Parentheses nest, or end the command. Nested, a group is a command of its own and
    the command around it continues after it (`$(…)`, `<(…)`, zsh's `*(.)`); flat, a
    parenthesis ends the command, as a case pattern or `f()` does before the command
    that follows it. So a parenthesized word that is not a command is classified as
    one: a case pattern `(rm)`, an array `(rm mv)`, or a comment's `# (rm x)`. A word
    glued to a group is part of one word, as zsh reads it, so a `<(…)` process
    substitution is a single path and a heredoc line such as `print(git(x))` is not
    split into a `git` command. A group where git expects its verb fails closed, since
    zsh globs `git (stash)` into `git stash` when a file named `stash` exists.
  - `{` and `]]` end the command, as where a command could start (`{ rm x; }`,
    `if [[ -n a ]] rm x`), or are words, as among arguments (`git branch {`). So the
    word after one is classified as a command: `echo { rm x` is denied.
  - Quoting is kept, or ignored. Kept, a quoted word is only a word, as zsh reads it,
    and a `!` glued after `>` or `&` joins the operator as zsh lexes it: `>!` and `>>!`
    clobber, `&!` disowns. The `!` joins from a partly quoted word too (`&!"rm" x` runs
    `rm`), and so from a wholly quoted one, which zsh leaves a word: `&"!rm" x` is
    denied. A quoted `!` alone stays a word, since zsh takes it as the target (`>"!" rm
    x` runs `rm`). Ignored, a quoted word made only of punctuation is the syntax it
    spells, as `eval` reads it and as every command was read before quoting was kept,
    and that `!` stays a word, as bash reads it. So `echo ';' rm x` is denied, and so is
    `git --namespace '>' log`, where `'>'` reads as a redirection that takes `log` with
    it, and so is `>! rm x`, which zsh runs as `x` with its output in a file `rm`.

- **`time -p rm x` is denied**, though zsh's `time` is a reserved word that takes no
  options: it runs a command named `-p` and never reaches `rm`. Options after `time` are
  skipped as they are after `env` and `nice`, since `/usr/bin/time -p` and bash's
  `time -p` do run the command.
- **An unquoted `$(…)`, glob group or numeric glob is denied where git takes a
  global-option value or a flag verb's argument, or anywhere in a `sed` command, even
  when it is read-only** (`git -C $(pwd) log`, `git branch --format $(cmd) x`, `sed -n
  $(cmd) f`), because zsh can split or expand it into several words and the guard
  cannot see which lands in the verb or value slot. Quoting keeps a substitution one
  word and is allowed: `git -C "$(pwd)" log`; and an unquoted substitution that only
  supplies a positional to a read-only verb still passes (`git log $(git merge-base a
  b)..b`).
- **Read-only git verbs missing from the allowlist are denied wherever they appear**, and
  with subshells, `$(…)`, `if` and assignments no longer hiding a command, that now
  includes the likes of `B=$(git symbolic-ref --short HEAD)`. Among them:
  `symbolic-ref`, `merge-tree`, `hash-object`, `diff-index`, `diff-files`, `show-ref`,
  `cherry`, `range-diff`, `show-branch`, `patch-id`, `check-ref-format`, and
  `filter-repo --version`. The allowlist fails closed on whatever it does not list.
  Widening it is a line per verb, but several of these also have forms that write
  (`symbolic-ref` with two arguments, `hash-object -w`).

- **`git config --global --list` is denied.** The allowlist carries exactly the five
  read-mode flags from the spec (`--get --get-all --get-regexp --list -l`); a scope
  flag is not one of them. Widening is a one-line change if it ever bites — in which
  case replace Gate B's check 3, which rides on this case. Gate B's *liveness* proof
  is check 2 (`git fetch`), which is independent of it.
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
