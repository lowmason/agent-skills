# Read-only agent guard (PreToolUse contract enforcement)

A `PreToolUse` hook that mechanically enforces the Bash half of the read-only
contract carried by five agents, replacing prose that nothing checks. Traces to
the deferred item recorded at plan 17's completion (2026-07-25) and selected for
design on 2026-09-03 via `/deferred`; the original out-of-scope note is in
[agents-and-commands-expansion.md](completed/agents-and-commands-expansion.md).

## Problem

Five agent definitions declare a read-only contract. Four state it in these words
(`code-reviewer`, `task-reviewer`, `security-auditor`, `Explore`):

> Your review is read-only on this checkout: you have no edit tools, and you must
> not mutate the working tree, the index, HEAD, branch state, or the worktree
> list via Bash.

Half of that is already mechanical. `tools: Read, Grep, Glob, Bash` in the
frontmatter means these agents have no `Write` or `Edit` tool at all — the
"no edit tools" clause enforces itself.

The other half is enforced by nothing. `git checkout`, `git stash`, `git reset`,
and `sed -i` are all reachable through the `Bash` tool the agents legitimately
need, and every one of them silently violates the contract. The damage lands on
the *caller's* uncommitted work: a `task-reviewer` that runs `git checkout <base>`
to compare, or a `test-runner` that runs `git stash` to get a clean tree, destroys
state the controller was mid-way through building.

The gap is not hypothetical in kind — it is the same class of gap that
`hooks/uv-guard.sh` already closes for tooling discipline in the work repos. What
is missing is the agent-scoped equivalent.

The item as recorded named three agents (`security-auditor`, `Explore`,
`test-runner`) and deferred to "the code-reviewer/task-reviewer precedent". That
framing was wrong on inspection. All five have identical tool lists (`Read, Grep,
Glob, Bash`, order varying), and four of the five carry the enumerated clause quoted
above verbatim; `test-runner` carries a compressed equivalent ("Never edit source
files; never mutate git state") covering the same two halves. Enforcing only the
three would leave the two agents cited as precedent unguarded. This spec covers all
five.

The item also anticipated "a hook design with per-agent matchers". That is not
available: the `PreToolUse` `matcher` field keys on *tool name*, not agent type.
Agent discrimination happens inside the script, reading `agent_type` from the hook
payload.

## Scope

- **Guarded agents (5):** `security-auditor`, `Explore`, `test-runner`,
  `code-reviewer`, `task-reviewer`.
- **Not guarded:** `debugger` and `docs-writer` (both legitimately edit files;
  their narrower "never commit or push" contract stays prose), and every built-in
  agent.
- **Enforcement surface:** the `Bash` tool only. The `Write`/`Edit` half needs no
  hook.
- **Install:** one global hook in `~/.claude/settings.json`, matching the scope of
  the agents themselves (user-level, dispatched in every repo).

## Design

### 1. The guard script — `hooks/readonly-agent-guard.py`

Python 3, stdlib only. This is a deliberate departure from the bash convention of
the existing `hooks/` templates, for three reasons:

- `shlex` tokenizes quoted commands correctly, narrowing the "heuristic, not a
  shell parser" gap that `uv-guard.sh`'s `sed`-based splitting leaves open.
- It drops the `jq` dependency, which matters more for a hook that now runs in
  every project than for a per-repo template.
- The test suite can import the classifier directly rather than only
  round-tripping subprocesses.

Cost: roughly 40 ms of interpreter start per `Bash` tool call, session-wide.

Module-level constant `READONLY_AGENTS: frozenset[str]` holds the roster; the
sync lint (§4) imports it.

Data flow:

```
stdin JSON → agent_type absent?         → exit 0   (main session; never blocked)
           → agent_type not in roster?  → exit 0   (debugger, docs-writer, built-ins)
           → classify tool_input.command → allow: exit 0, no output
                                         → deny:  exit 0 + permissionDecision JSON
```

The deny payload is:

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "..."}}
```

with exit 0. The reason names the agent, the offending command, the contract
clause, and the read-only alternative where one exists, so the agent reports
accurately to its controller instead of retrying blind.

**No escape hatch.** `uv-guard.sh` honours a `no-uv-guard` string because the
party it constrains is the main session. Here the constrained party is the agent
being denied, and a documented bypass string in the denial message would teach it
the way through — making the guard advisory, which is the state this spec exists
to leave.

### 2. Classification rules

The rules are asymmetric, and the asymmetry follows from the shape of each space
rather than from inconsistency. **This must not be "fixed" into one uniform rule.**

**git → allowlist, failing closed.** Git has a small, enumerable read-only
vocabulary, so unknown verbs can be denied by default and still leave a usable
agent.

Always allowed:

```
log show diff diff-tree status grep blame ls-files ls-tree ls-remote cat-file
rev-parse rev-list describe shortlog whatchanged name-rev merge-base
for-each-ref count-objects verify-commit check-ignore check-attr var help version
```

Allowed only in read-only form (any other form is denied):

| verb | allowed forms |
|---|---|
| `stash` | `list`, `show` (bare `git stash` is denied — it mutates) |
| `worktree` | `list` |
| `branch` | bare, or only `-l --list -a -r -v -vv --contains --merged --no-merged --show-current --format --sort` |
| `tag` | bare, or only `-l --list --contains --points-at --sort --format` |
| `config` | `--get --get-all --get-regexp --list -l` |
| `remote` | bare, `-v`, `show`, `get-url` |
| `reflog` | bare, `show` |
| `submodule` | `status`, `summary` |
| `notes` | `list`, `show` |
| `bisect` | `log`, `view` |
| `sparse-checkout` | `list` |

Everything else after `git` is denied. That covers the obvious writes (`commit`
`add` `checkout` `switch` `restore` `reset` `revert` `merge` `rebase`
`cherry-pick` `am` `apply` `push` `pull` `fetch` `clone` `init` `clean` `gc`
`prune` `mv` `rm`), the plumbing that mutates without a recognizable write verb in
its name (`update-ref` `update-index` `write-tree` `commit-tree` `hash-object`
`fast-import` `filter-branch` `replace` `symbolic-ref`), and any verb added to git
in the future.

Global options are skipped when locating the verb: `-C <path>`, `-c <k=v>`,
`--git-dir=`, `--work-tree=`, `--namespace=`, `-p`/`--paginate`/`--no-pager`,
`--exec-path`, `--bare`, `--literal-pathspecs`, `--no-replace-objects`.
Consequently **`git -C /other/repo commit` is denied**. This case is load-bearing,
not incidental: `-C` is exactly how an agent would step outside a guard that only
considered the working directory.

**non-git → denylist; unlisted commands pass.** (A different sense of "open" from
§3, which governs error handling.) An allowlist is impossible here, because
read-only shell is unbounded (`cat`, `grep`, `awk`, `find`, `uv run pytest`, `jq`,
`python -c`, …). A small denylist of unambiguous mutators is the only workable
form:

```
rm  mv  truncate  shred  sudo    and    sed with -i / --in-place / -i<suffix>
```

Consciously excluded, per the strictness decision (§Decisions D2): `>` and `>>`
redirection, `tee`, `mkdir`, `touch`, `chmod`, `cp`, `dd`, `ln`. Each has ordinary
read-only-workflow uses (paginating output to a temp file, creating a scratch
directory) that the heuristic cannot distinguish from a repo mutation without real
path analysis.

**Compound commands** are split on `&& || ; | &` and newlines; each subcommand's
first token is classified independently.

### 3. Failure posture — fail open before identification, fail closed after

| Condition | Outcome |
|---|---|
| stdin JSON malformed or unreadable | **allow** |
| `agent_type` absent | **allow** |
| `agent_type` not in `READONLY_AGENTS` | **allow** |
| in roster, but classification raises | **deny**, with the exception text in the reason |

The switch is keyed on "have we identified a guarded agent yet", which puts the
strict half only where the blast radius is a single subagent. A uniform posture is
wrong in both directions: fail-closed everywhere means one malformed payload
blocks `Bash` in every project on the machine; fail-open everywhere means the
guard stops guarding exactly when its input gets unusual.

The **`agent_type` absent → allow** row is the property everything else rests on.
The main session must never be blocked by this hook.

### 4. Roster sync lint

**Prerequisite — normalize one heading.** The lint keys on a `## Read-only contract`
heading, which four of the five guarded agents already use. `agents/test-runner.md`
calls its equivalent section `## Contract`, so this work renames that heading to
`## Read-only contract`. The rename is accurate on its own terms (the section's two
clauses are "Never edit source files; never mutate git state") and it promotes the
heading from a label into a load-bearing marker: after it, `## Read-only contract`
means exactly "guarded by the hook". `agents/debugger.md` and `agents/docs-writer.md`
keep their plain `## Contract` heading, correctly — theirs are not read-only
contracts, and that distinction is now what the lint reads.

`build/check_frontmatter.py` — which already walks `agents/*.md` through
`check_agent_file` — imports `READONLY_AGENTS` from the guard and asserts
**bidirectionally**:

- every `agents/*.md` containing a `## Read-only contract` heading appears in the
  roster;
- every roster entry names an agent file that carries that heading.

Both directions matter: the forward check catches a sixth read-only agent shipping
unguarded, and the reverse catches a roster entry left behind by a renamed or
deleted agent. This is what makes the hardcoded roster safe — drift becomes a lint
failure at the commit that introduces it, not a silent gap found later.

### 5. Install and wiring

Symlink, matching the `~/.claude/agents/` convention already used by this repo:

```bash
mkdir -p ~/.claude/hooks
ln -s ~/Projects/agent-skills/hooks/readonly-agent-guard.py \
      ~/.claude/hooks/readonly-agent-guard.py
```

`~/.claude/settings.json` gains its first `hooks` key (confirmed absent as of
2026-09-03):

```json
{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [
  {"type": "command", "command": "$HOME/.claude/hooks/readonly-agent-guard.py"}]}]}}
```

`$CLAUDE_PROJECT_DIR` is unusable here — it resolves per-project, and this hook has
one global install.

Symlinking is a **deliberate departure** from `hooks/README.md`'s "prefer `cp` over
symlinking so a hook change can't silently alter every repo at once". That rule
protects against one template edit changing every *work repo*. Here there is
exactly one install, and the hazard runs the other way: the guard must not drift
from the agent files it enforces, which are themselves symlinked from this repo.

### 6. Documentation changes

- **`hooks/README.md`** is restructured into two categories:
  - *Project tooling hooks* (`ruff-fix.sh`, `ruff-check.sh`, `uv-guard.sh`) —
    per-repo `cp`, never global. The existing "do not install as a global hook"
    warning stays, now explicitly scoped to this category.
  - *Agent contract hooks* (`readonly-agent-guard.py`) — one global install. The
    warning does not apply, because the guard no-ops unless `agent_type` matches a
    guarded agent, so it never fires in the main session or in a non-Python repo.
  - The known limitations (§Out of scope) are documented here in the same candid
    register the README already uses for `uv-guard.sh`.
  - The Gate B probe result records the verified Claude Code version, as
    `agents/explore.md` does for its capitalization probe.
- **`agents/test-runner.md`** — `## Contract` renamed to `## Read-only contract`
  (see §4). No other change to the file.
- **`CLAUDE.md`** — the `hooks/` line currently reads "reusable hook templates for
  the user's *work* repos — ruff/uv gates; not wired into this repo". Both clauses
  become wrong; amend. Add the Gate A command to the Commands section:

  ```bash
  cd hooks && uv run --python 3.13 --with pytest python -m pytest -q
  ```

## Decisions

- **D1 — All five read-only agents, not the item's three.** The recorded item
  scoped to plan 17's additions and deferred to the `code-reviewer`/`task-reviewer`
  precedent. But the precedent agents carry the same contract and the same tool
  list, so enforcing three of five would ship an asymmetry with no rationale behind
  it.
- **D2 — Git state plus unambiguous file mutators.** The contract prose names "the
  working tree" as the first thing not to mutate, so blocking `sed -i` and `rm` is
  enforcing written contract, not inventing new contract. Redirection, `mkdir`,
  `touch`, `chmod`, and `cp` are excluded because the heuristic cannot separate a
  repo write from a `/tmp` write without real path analysis — the exact
  false-positive failure `hooks/README.md` already flags for `uv-guard.sh`.
- **D3 — Global install.** The agents are user-level and get dispatched in every
  work repo, which is where clobbered state actually costs something. A
  project-level hook in this repo would guard the one place with the least to lose.
  Safe globally in a way the ruff/uv hooks are not, because it no-ops unless
  `agent_type` matches.
- **D4 — Hardcoded roster plus a commit-time sync lint**, rather than deriving the
  roster from `agents/*.md` at runtime. Runtime derivation cannot drift, but it
  makes every `Bash` call in every project parse markdown, and it couples a global
  hook to this repo's presence on disk — if `~/Projects/agent-skills` moves, the
  guard fails open silently. Failing open silently is the one outcome a contract
  guard must not have. The lint recovers the anti-drift property at commit time
  instead.
- **D7 — `fetch` and `pull` are denied deliberately, not by fall-through.**
  `git fetch` is the one verb the fail-closed default sweeps in that arguably
  violates no clause of the quoted contract: it writes `refs/remotes/*` and
  `FETCH_HEAD`, touching neither the working tree, the index, HEAD, local branch
  state, nor the worktree list. It is denied anyway, for two reasons. First,
  reproducibility: a fetch part-way through a review silently changes what a
  subsequent `git diff origin/main...` shows, so the artifact under review moves
  while it is being reviewed. Second, architecture: in both review paths the
  *controller* prepares the diff (`scripts/review-package`) before dispatching, and
  `agents/task-reviewer.md` already instructs the reviewer not to re-run git
  commands when a diff file is present — so the reviewer seat has no occasion to
  fetch. Confirmed against the roster: no guarded agent's definition invokes
  `git fetch` (`task-reviewer.md:32`'s "fetch the diff yourself" is English, and
  resolves to `git diff BASE..HEAD`, which is allowed). If a real dispatch ever
  needs a base ref that is not local, the fix is for the controller to fetch before
  dispatching, not to widen the guard. `pull` is denied on the stronger ground that
  it merges into HEAD. **Recorded as a decision so a future reader does not "fix"
  it as an oversight** — and so that flipping it, if a real case appears, is a
  one-line change with a known rationale to argue against.
- **D5 — No escape hatch.** See §1.
- **D6 — Python rather than bash**, against the local convention of `hooks/`. See
  §1.

## Verification

**Gate A — `hooks/test_readonly_agent_guard.py`** (pytest, stdlib only, run from
`hooks/`). Two layers, following the `test_sdd_scripts.py` precedent of keeping the
repo on one test runner:

1. *Unit*, importing the classifier — table-driven over: every always-allowed git
   verb; both sides of each mode-dependent pair (`stash list` vs bare `stash`,
   `worktree list` vs `worktree add`, `branch -v` vs `branch -d x`, `config --get`
   vs `config a b`, `tag -l` vs `tag -a v1`); the fail-closed default, asserted on
   both a real plumbing write (`git update-index`) and an invented verb
   (`git frobnicate`); the D7 network verbs (`git fetch` and `git pull` both deny,
   asserted as intentional rather than incidental); global-option skipping
   (`git -C /x commit` denies,
   `git -C /x log` allows); each non-git denylist entry; and compound commands
   where the mutator is not the first subcommand.
2. *Contract*, driving the script as a subprocess with real payloads on stdin — all
   four rows of the §3 table, plus the exact shape of the deny JSON.

**Gate B — `hooks/probe-readonly-guard.sh`.** A live check that Claude Code
actually delivers `agent_type` and honours the denial on the installed binary:
`claude -p --agent Explore` twice, asserting `git status` passes and `git stash` is
denied. Gate A can pass perfectly against a hook Claude Code never invokes; Gate B
is the only test of the real claim.

> **Assumption flagged for the plan.** The probe route depends on `--agent`
> populating `agent_type` at session level, which is documentation-derived and not
> yet observed on this machine. **Confirming the probe route must be the first
> task's finding, not an assumption later tasks build on.** If `--agent` does not
> populate the field, the fallback is a real subagent dispatch inside a `claude -p`
> run. The mechanism is version-sensitive, so the README records the verified
> version and the probe is re-run after binary updates.

Both gates plus `build/check_frontmatter.py` and `build/check_provenance.py` must
pass before the branch is considered complete.

## Out of scope

- **Adversarial containment.** This is a guardrail against an agent drifting off
  contract, not a sandbox. Not caught, and documented as such in
  `hooks/README.md`: `xargs rm`, `find -delete`, `find -exec rm`, command
  substitution (`$(git commit …)`), and mutators inside `python -c` or `sh -c`
  strings. The real containment remains the `tools:` frontmatter denying
  `Write`/`Edit` outright, plus the permission system.
- **Guarding `debugger` and `docs-writer`.** Both legitimately write files. Their
  narrower "never commit, push, or otherwise mutate git history" clause could be a
  second tier keyed on the same `agent_type` mechanism, but it is not built here —
  no observed violation motivates it, and a second ruleset doubles the surface the
  sync lint must reason about.
- **Guarding tools other than `Bash`.** No other tool available to these five can
  mutate state.
- **Retrofitting the existing ruff/uv templates** to Python or to the JSON decision
  protocol. They work, they are per-repo, and they are out of this spec's path.

## Provenance

Original work by Lowell Mason; covered by this repo's MIT `LICENSE`. No `NOTICE`
entry is required: `build/check_provenance.py` scans `skills/` only, and `NOTICE`
enumerates non-skill paths solely where third-party provenance exists (as with
`rules/clean-code-python.md`, which adapts Robert C. Martin's rule catalog).
Nothing in this design derives from the superpowers plugin or any external source.
The hook payload field names (`agent_type`, `permissionDecision`) are Claude Code
API surface, cited from the official hooks documentation.
