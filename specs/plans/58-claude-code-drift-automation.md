# Claude Code Drift Automation Stage 5: Live Probes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `cli.py probes` and `cli.py binaries` (drift spec R10) with four registered probes. Each probe checks, on a `claude` binary the owner names, a behaviour the guide states, so a change shows before the docs say so. Their assertions are replayed in tests against recorded, scrubbed streams (R12.6), and the `/cc-guide` skill gains its `probes` mode (R8.9).

**Architecture:** `probe_checks.py` holds the pure assertions, one per probe, over raw `--output-format stream-json` events, and the scrubber that turns a recorded stream into a committable fixture. `probes.py` runs each probe from a fresh temporary directory outside every repo, keeps the raw output under the cache's `probes/`, and appends one row per probe to `build/cc_guide/PROBES.md`. `cli.py` wires the two subcommands, and `manifest.toml` registers the four probes. `state.py` and `check.py` harden the probe log first: only R10.5's three outcomes parse, a legend table is skipped, and ERROR stays due until a later PASS. Task 1 amends the spec where the planning spike settled what R10 left open.

**Tech Stack:** Python 3.13 stdlib (`build/cc_guide/`); pytest through `uv run`; bash (`hooks/probe-readonly-guard.sh`); the Claude Code CLI for the live runs (2.1.303 while planning); Markdown (the spec, the `/cc-guide` skill, `CLAUDE.md`, `build/CLAUDE.md`, `hooks/README.md`).

**Spec:** `specs/claude-code-drift-automation-spec.md`: R10 (`probes` and `PROBES.md`), R12.6 (replay), R8.9 (`/cc-guide probes`), R6.7 (due rules), R12.7 (documentation), Validation 5 and 6, and Decisions 14 (the four v1 probes) and 15 (`--claude` is required). Task 1 amends R6.7, R10.2, R10.4, R10.5, R10.6 and R12.6.

## Background

Labels used below, each expanded here once:
- **Stage 5** is the last of the drift spec's five stages. Plans 38, 43, 44 and 49 built Stages 1 to 4 (the detector, the citation wiring, the `/cc-guide` skill, and the session-start notice), with plans 45 and 51 as follow-ups. Stage 5 adds the live probes.
- **The registry gaps item** is the deferred item "The probe registry's gaps, for Stage 5" in `specs/deferred_items.md`, section `38-claude-code-drift-automation — 2026-10-05`. Its part (a): `state.parse_probes` accepts any outcome word, `check.due_probes` treats ERROR like PASS, and a second table in `PROBES.md` (a legend) makes every check exit 2. Its part (b): the manifest validator requires a non-empty `sections` (R10.1), but R10.2's `guard-liveness` row backs files only. Task 2 closes (a). Decision D1 and Task 1 close (b).
- **The startup item** is the deferred item "Does `startup` fire under `claude -p`?" in section `49-claude-code-drift-automation — 2026-10-18`. If it does, every `claude -p` run in this repo runs the notice's `show` and `refresh`. Decision D5 and Task 8 close it.
- **The planning spike** is a capped recording run the owner approved on 2026-10-20, before this plan was written. It ran each probe's mechanism once on Claude Code 2.1.303 from fresh temporary directories, for about $0.35 in all. Its raw streams stay under `~/.cache/agent-skills/scratch/plan58-spike/`, outside the repo. The Planning record lists what it showed.
- **Fork mode**: since 2.1.302, a `claude -p` session starts named-agent spawns in the background. `claude -p` stops background agents 10 minutes after its main turn unless `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` raises that ceiling.
- **Gate B** is `hooks/probe-readonly-guard.sh`, the hand-run live check of the read-only agent guard (`hooks/readonly-agent-guard.py`). The `guard-liveness` probe wraps it.

Why now: Stage 5 is the spec's last unbuilt stage. Until it lands, the spec stays live, and the four behaviours the repo depends on (the guard firing, an agent's tool list, Stop-hook continuation, and agent model pins) are checked only by hand.

## Global Constraints

- **Work in a worktree** (spec, Sequencing constraints): "Check `git rev-parse main origin/main` first: `EnterWorktree` branches from `origin/main` and omits unpushed commits, and concurrent sessions switch and rebase the shared checkout." Execute on a branch that holds this plan's commit, in its own worktree. Never execute in the shared checkout.
- **The base must contain `73106b8`.** That is `main` after lowmason/agent-skills#82 (`cli.py` reads the changelog's new bold release labels) and #83 (the docs rewritten as Markdown, with the baseline rehashed). A branch based before #82 fails `cli.py lint`, and so every commit gate, once the shared cache holds the new changelog format. Run `git merge-base --is-ancestor 73106b8 HEAD` before Task 1: exit 0 means the base is right. This plan was written on `claude/what-is-next-2636bf` at `5dae679`, so merge the plan to `main` first and cut the execution worktree from current `main`.
- **Run every command from the worktree root**, with the relative paths this plan gives. Never `cd`: a Bash `cd` persists and moves the session's working directory. A guarded worktree session refuses compound shell (`&&`, pipes, `$(...)`), so each command stands alone, and the suites run through `uv run --directory build/cc_guide`.
- **The tests spend nothing; the live runs do.** Every test module this plan adds imports the autouse `isolated_home` fixture from `cc_fixtures.py`, so no test reaches the real `~/.cache` or `~/.claude`, and every `claude` in a test is a fake. The runs that spend tokens are Task 6 Step 6 and Task 8 Step 2, about $0.40 in all. Task 1 Step 2, Task 5 Step 5 and Task 6 Steps 4 and 7 run only `--version`. Run no other live `claude` command.
- **The shared cache.** `~/.cache/agent-skills/cc-guide/` is one directory for `main` and every worktree. `cli.py probes` only reads the cached changelog and writes new folders under `probes/`. `cli.py lint`, which the commit lints run, also reads the cached changelog's release labels; `baseline cite` reads only the baseline and the guide. Never run a live `check`, `packets`, `settle` or `baseline rebaseline` from the worktree against it.
- **The worktree's own notice runs at its session starts.** A session started in the worktree runs `"$CLAUDE_PROJECT_DIR"/build/cc_guide/notice.sh`, which can launch the worktree's `cli.py check --hook`. So `cli.py` stays importable at every commit, and no new session starts in the worktree while it is broken mid-edit.
- **The binary** (D2): every live run uses the held copy `~/.cache/agent-skills/scratch/plan58-bin/claude` that Task 1 makes, never the PATH `claude` directly. `probes` compares it with the newest cached changelog release on every run, and any `check` in the meantime may cache a newer one. So pass `--allow-old` whenever `probes` refuses the held copy as older (exit 2, "older than the newest changelog release"), then run the same command again with the flag. The log row records it (R10.3).
- **What the live runs test.** `guard-liveness` and `agent-model-pins` load user settings, so they run the agents in `~/.claude/agents/` and the guard hook in `~/.claude/hooks/`. Those are symlinks into the shared checkout `~/Projects/agent-skills`, not into the worktree. Task 6 Step 5 checks that the shared checkout is on `main` with no changes under `agents/` or `hooks/`, and that the guide sections the probes back still state what the assertions check. A guide-upkeep session was editing the guide while this plan was written: that check replaces waiting for it. Task 8 runs from a fresh temporary directory with a stand-in hook, so it needs no fresh `last-check.json` and is safe while a `/cc-guide` run is in flight.
- **Never commit a raw stream** (Sequencing constraints: "probe streams live under `~/.cache/agent-skills/cc-guide/`"). Only files that `probes.save_fixtures` wrote go into `build/cc_guide/probe_streams/`, and `test_probe_replay.py` fails on a path or an id in them (D3). The repo is public.
- **Never commit docs text** (Sequencing constraints): quotes from the docs appear only in session reports.
- **Tests** (R12.1): "Tests are offline." Module and test basenames stay unique across `build/`: this plan adds `probes.py`, `probe_checks.py`, `test_probes.py`, `test_probe_checks.py` and `test_probe_replay.py`, and no other `build/` file has those names.
- **Citations** (R4.1): a new `.py` file that rests on a Claude Code fact carries a `# cc-guide: <section ids> @<release>` line before its docstring. After `git add`, run `cli.py baseline cite <file>`, which sets the release from the baseline. The release in this plan's code (`@2.1.304`) is what it set while planning.
- **Every existing gate passes** (Validation 6): `check_frontmatter.py`, `check_provenance.py`, `check_snippets.py skills/` (Tier 1), the dependency-drift test, the `build/` suite, `sync_runtime_assets.py --check` with no adapter change, and `check_conformance.py`. `bash build/run_commit_lints.sh` runs the nine commit lints; run it before every commit.
- **Test counts are deltas** (+N), never absolute pytest totals.
- **The root `CLAUDE.md` stays under 200 lines** (R12.7). It has 148 at `5dae679`, and Task 7 adds 5.
- **Python style:** single quotes, f-strings, named constants (G25), stdlib only in `build/cc_guide/`, Python 3.13, lines of 120 characters or fewer in new code.
- **Expand every bare label at first use** (owner preference) in docs and reports for the owner: give a decision, item or plan number its plain meaning beside it.
- **Commit trailer:** the executing session's own `Co-Authored-By:` line, as a second `-m`. Subagent-authored commits keep that same line. Check it with `git log -1 --format=%B`.

## Decisions

- **D1** (owner, planning, 2026-10-20): the registry gaps item's part (b), the option "Back hooks sections": "guard-liveness backs hooks.events, hooks.exit-codes and hooks.patterns, the sections hooks/readonly-agent-guard.py already cites. The validator stays strict. A spec amendment task replaces R10.2's 'no section yet (R4.3)' cell." Applied in: Task 1 (spec amendment), Task 5 (registry).
- **D2** (owner, planning, 2026-10-20): the binary, the option "PATH CLI, held copy": "At the start of execution, copy the PATH claude into ~/.cache/agent-skills/scratch/plan58-bin/ so the updater cannot prune it mid-plan. Runs pass --allow-old when it is older than the changelog head, and the log row records that." Applied in: Global Constraints, Task 1, Tasks 6 and 8.
- **D3** (owner, planning, 2026-10-20): the fixtures, the option "Trimmed, scrubbed streams": "Commit each real stream cut down to the events its assertion reads, with home paths, session ids and MCP/plugin names replaced by placeholders. A test fails if a fixture holds /Users/ or a session-id pattern. This keeps R12.6 as written." Applied in: Task 1 (spec amendment A5), Task 3 (`scrub_events`), Task 4 (`save_fixtures`), Task 6.
- **D4** (owner, planning, 2026-10-20): `agent-model-pins`, the option "Production path, ceiling set": "Keep fork mode on, as in the owner's Desktop sessions. Set CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS to a bounded value above the probe's timeout. Give code-reviewer a trivial one-line target to keep its Opus xhigh run cheap." Applied in: Task 4 (`prepare_pins`), as 15 minutes: above the generic `PROBE_TIMEOUT` (600 s) and below the pins run's own `PINS_TIMEOUT` (1200 s), so `claude -p` ends its wait for the background agents before the harness stops it. D7 confirms that reading.
- **D5** (owner, planning, 2026-10-20): the startup item, the option "Record once": "One live run during execution. Record the answer and claude --version in the notice.sh paragraph of build/CLAUDE.md, which closes L3817. Decision 14's four probes stay as they are, so no spec amendment is needed." (L3817 is the startup item.) Applied in: Task 8.
- **D6** (owner, plan review, 2026-10-20): spec amendments A1 to A5 as worded in Task 1, Steps 3 to 6, the option "Approve as written": "A1 guard backs the hooks sections; A2 Stop-hook route and ERROR rule; A3 budget flag, pins session exemption, guard keeps Explore's model; A4 ERROR stays due, unknown outcome is a setup error; A5 scrubbed fixtures with a test." Applied in: Task 1 (spec amendment).
- **D7** (owner, plan review, 2026-10-20): the settled defaults DF1 to DF7 and D4's 15-minute reading, the option "All stand": "Includes DF3 (Gate B gains R10.4's flags, so it changes when you run it by hand too) and DF7 (the new /cc-guide probes mode is not micro-tested, like plan 51's edit)." Applied in: Tasks 4, 6, 7 and 8.

---

## Planning record

### Facts measured while planning (2026-10-20, at `5dae679`; rechecked at `73106b8`)

- The plan was written at `5dae679`. While it was reviewed, `main` moved to `73106b8` (lowmason/agent-skills#82 and #83). Main's changes touch five files this plan edits, and every Replace block still matches exactly once at `73106b8`. Base counts at `73106b8`: the cc_guide suite 526 passed; the `build/` suite 1222 passed, 16 skipped.
- The PATH CLI is 2.1.303. The newest Desktop app bundle and the cached changelog's newest release are 2.1.304, so the held copy needs `--allow-old` unless the updater has moved it on.
- `state.parse_probes` (`state.py:361-387`) splits every table line into cells and takes any outcome word. `check.due_probes` (`check.py:261-279` at `73106b8`) tracks only DIVERGES. The manifest's `[[probe]]` validator (`state.py:253-265`) requires a non-empty `sections`. `PROBES` is `build/cc_guide/PROBES.md` (`state.py:19`), and no such file exists yet.
- `hooks/readonly-agent-guard.py:2` cites `hooks.events hooks.exit-codes hooks.patterns`, the sections D1 names.
- The repo's `.claude/settings.json` wires `notice.sh show` and `notice.sh refresh` on the SessionStart `startup` matcher.
- The root `CLAUDE.md` has 148 lines. The cc-guide skill's description is 361 characters after Task 7.

### What the planning spike recorded (Claude Code 2.1.303)

- **The init event** carries `tools`, `model`, `session_id` and `claude_code_version`. It also carries private fields: `cwd`, `memory_paths`, `mcp_servers`, `plugins`, `skills` and `scratchpad_path`, and MCP tool names in `tools`. A run that waits on background agents writes several init and result events.
- **agent-tools.** Through `--agent`, the scratch agent with `tools: Read, Grep, Glob, Bash` got `Bash, Read`, and the control agent without Bash got `Glob, Grep, Read`. Each run cost about $0.013.
- **stop-continuation.** With `--include-hook-events`, each Stop hook's `hook_response` event carries `exit_code` as an integer. The scratch project's `.claude/settings.json` and `--settings` both loaded the hook. The log read `false, true, true`, and the exits were 2, 2, 0. About $0.054.
- **agent-model-pins.** With `--forward-subagent-text`, each subagent's assistant events carry `parent_tool_use_id` and `message.model`, and the Agent `tool_use` input has `subagent_type`. Explore and test-runner were served `claude-haiku-5-5` and code-reviewer `claude-opus-5-5`. Effort is not in the stream. It is in the subagent transcripts, `~/.claude/projects/<project>/<session>/subagents/agent-*.jsonl`, beside an `agent-*.meta.json` that names the `agentType`, so this probe persists its session (A3). code-reviewer's lines read `effort: xhigh`. About $0.24, most of it code-reviewer.
- **guard-liveness.** The guard's marker `readonly-agent-guard:` appears in the denied Bash call's `tool_result`. Each of the three checks took 2 turns and about $0.002.
- **SessionStart.** The guard runs, which load user settings, show `hook_started` and `hook_response` events named `SessionStart:startup` under `claude -p`. This is the startup item's likely answer. Task 8 confirms it with its own run, as D5 asks.

### Prototype

Two parts were added after the spike and have not yet run live: Gate B's new flags (DF3) and the `Agent` pre-allow (DF4). Task 6 Step 6 is their first live run. If either breaks a probe, that probe comes back ERROR, never PASS, and Task 6 says how to debug it.

All code in this plan was built and run in a throwaway clone of `5dae679`, with fixtures saved from the spike's streams. A script applied this plan's Replace and Create blocks, in order, to `5dae679` and compared the result with the clone: they match byte for byte. The same blocks were then applied to `73106b8`. In both clones the cc_guide suite gained 94 tests. At `73106b8` the `build/` suite gained 94 too, and the nine commit lints, `cli.py lint` and `check_conformance.py` all passed. Each task's RED step was checked at `73106b8` by running its new tests against the code before that task.

After plan review, `main` moved to `82818ca` (lowmason/agent-skills#84), which changes `cli.py`, `state.py`, their tests and the spec. The blocks still apply there without change. Both suites again gain 94 tests, the same gates pass, and each RED step fails as before.

### Settled defaults (approved at plan review, D7)

- **DF1.** The rows that Task 6's runs append to `PROBES.md` are committed with the branch. Without them, `main`'s notice would report four probes never run as soon as the registry merges.
- **DF2.** The deliberately broken setup (Validation 5) is a wrapper binary that answers `--version` and fails every probe run, as a crashed or unauthenticated binary would. It is deterministic and costs nothing. Its ERROR row stays in the log, followed by the full run's PASS rows.
- **DF3.** R10.4 applies to every probe, so Gate B's `claude` calls gain `--setting-sources user`, a pinned permission mode, `--max-turns 4`, `--max-budget-usd 0.50` and `--no-session-persistence`. That also changes Gate B when it is run by hand: it no longer loads a repo's project settings, so a run from inside this repo no longer fires the repo's session-start hook.
- **DF4.** `agent-model-pins` pre-allows the `Agent` tool through `--settings` (R10.4: "with the probe's tools pre-allowed"). Its subagents' own calls stay with auto mode, as in the owner's sessions.
- **DF5.** Task 8 answers the startup item with a stand-in SessionStart hook passed through `--settings`, run from a fresh temporary directory, never with this repo's `notice.sh`. So the check fetches nothing and marks no notice shown.
- **DF6.** The fixtures are re-recorded in Task 6 on the held binary through `save_fixtures`. The spike's streams are never committed.
- **DF7.** The skill's new `probes` mode is a procedure whose rules restate the spec's (the owner picks the binary, `--allow-old` only on the owner's word, nothing copied from raw output). It is not micro-tested, as plan 51's edit to this skill was not. Plan 44 micro-tested the skill's settle rules, which are discipline under pressure. A micro-test of the new mode would add a task and about $1.

### Spec amendments (approved at plan review)

Task 1 makes five amendments, each tagged `(owner, plan 58, 2026-10-20)`:
- **A1** (D1): R10.2's `guard-liveness` row backs `hooks.events`, `hooks.exit-codes` and `hooks.patterns`, and its mechanism names `PROBE_STREAM_DIR`.
- **A2**: R10.2's `stop-continuation` row records the registration route the spike proved. A log that reads right with Stop exits other than 2, 2, 0 is ERROR; a log that reads wrong is DIVERGES.
- **A3**: R10.4 adds `--max-budget-usd`, exempts `agent-model-pins` from `--no-session-persistence` (effort is only in its transcripts), and lets `guard-liveness` keep `Explore`'s own model pin.
- **A4**: R6.7 gains an ERROR row (due until a later PASS), R10.5 says so too, and R10.6 defines the log table and rejects an unknown outcome.
- **A5** (D3): R12.6 says the committed streams are cut down and scrubbed, and a test fails on a path, an id or an MCP tool name in them. `save_fixtures` always scrubs the login name; no fixture test checks it, since a short login such as `runner` would match the kept agent name `test-runner`.

### Plan ID

58, from `writing-plans/scripts/entry_check.py` on 2026-10-20. The stub that claimed it is replaced by this file.

---

### Task 1: Hold the binary and amend the spec (D1, D2; wording approved at plan review)

**Files:**
- Modify: `specs/claude-code-drift-automation-spec.md`: R6.7's table, R10.2's table, R10.4, R10.5, R10.6 and R12.6.
- Create (outside the repo): `~/.cache/agent-skills/scratch/plan58-bin/claude`.

The spec's status line stays untouched.

- [ ] **Step 1: Record the starting counts.** Task 9 compares against these. The `build/` suite takes about a minute.

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`

Run: `uv run --directory build --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`

Expected: note each summary line. In a worktree without the gitignored `build/.scratch/`, the `build/` suite may show `test_verify_citations.py` failures; they are not this plan's.

- [ ] **Step 2: Hold the binary (D2).** Find the PATH `claude` and the file it links to, copy that file, and read the copy's version.

Run: `which claude`

Run: `readlink -f <the path which printed>`

Run: `mkdir -p ~/.cache/agent-skills/scratch/plan58-bin`

Run: `cp <the path readlink printed> ~/.cache/agent-skills/scratch/plan58-bin/claude`

Run: `~/.cache/agent-skills/scratch/plan58-bin/claude --version`

Expected: a line such as `2.1.303 (Claude Code)`. Note the version for Tasks 6 and 8. Then read `~/.cache/agent-skills/cc-guide/latest/fetch.json` with the Read tool: its `changelog_head` is the newest cached release (2.1.304 while planning). If the held version is older, expect `probes` to need `--allow-old` (Global Constraints, "The binary").

- [ ] **Step 3: A1 and A2, R10.2's table.**

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
| `guard-liveness` | Wraps `hooks/probe-readonly-guard.sh`, which gains a `CLAUDE_BIN` override, run from a scratch git repo. Needs user settings, since the guard is installed globally | its three checks pass | files `hooks/readonly-agent-guard.py` and `hooks/README.md`; no section yet (R4.3) |
```

**with:**

```markdown
| `guard-liveness` | Wraps `hooks/probe-readonly-guard.sh`, which gains a `CLAUDE_BIN` override, run from a scratch git repo. Needs user settings, since the guard is installed globally. The script keeps each check's raw stream in `PROBE_STREAM_DIR` when that is set (owner, plan 58, 2026-10-20) | its three checks pass | `hooks.events`, `hooks.exit-codes`, `hooks.patterns`, the nearest sections, since `agent_type` in PreToolUse payloads stays a coverage gap (R4.3); files `hooks/readonly-agent-guard.py` and `hooks/README.md` (owner, plan 58, 2026-10-20) |
```

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
| `stop-continuation` | A scratch Stop hook, registered through the scratch project's settings or `--settings` (whichever the first recorded run proves loads), logs `stop_hook_active` and blocks on its first two calls | the log reads `false, true, true`; an empty log is ERROR | `hooks.exit-codes`, `hooks.patterns` |
```

**with:**

```markdown
| `stop-continuation` | A scratch Stop hook, registered through the scratch project's `.claude/settings.json` and loaded with `--setting-sources project`, logs `stop_hook_active` and blocks on its first two calls. Both routes loaded on 2.1.303; `--include-hook-events` puts each Stop hook's exit code in the stream (owner, plan 58, 2026-10-20) | the log reads `false, true, true`; an empty log is ERROR, and so is that log with a stream whose Stop hooks did not exit 2, 2, 0 | `hooks.exit-codes`, `hooks.patterns` |
```

- [ ] **Step 4: A3, R10.4.**

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
- `--model sonnet` at low effort, except where that would mask what the probe
  observes; `agent-model-pins` leaves the agents' own pins in force.
- A bounded `--max-turns`; `--no-session-persistence`; the prompt first, with
  stdin from `/dev/null`.
```

**with:**

```markdown
- `--model sonnet` at low effort, except where that would mask what the probe
  observes; `agent-model-pins` leaves the agents' own pins in force, and so
  does `guard-liveness`, which runs `Explore` (owner, plan 58, 2026-10-20).
- A bounded `--max-turns` and `--max-budget-usd`; `--no-session-persistence`,
  except for `agent-model-pins`, which reads effort from its subagents'
  transcripts because the stream lacks it (R10.5) (owner, plan 58,
  2026-10-20); the prompt first, with stdin from `/dev/null`.
```

- [ ] **Step 5: A4, R6.7, R10.5 and R10.6.**

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
| A DIVERGES probe outcome | Immediately, until a later PASS row for that probe |
```

**with:**

```markdown
| A DIVERGES probe outcome | Immediately, until a later PASS row for that probe |
| An ERROR probe outcome | Immediately, until a later PASS row for that probe (owner, plan 58, 2026-10-20) |
```

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
  differs; it is due (R6.7) and handled like a TOUCHES row for the probe's
  sections and files. **ERROR** means the mechanism never fired or the run
  broke; it is never a pass.
```

**with:**

```markdown
  differs; it is due (R6.7) and handled like a TOUCHES row for the probe's
  sections and files. **ERROR** means the mechanism never fired or the run
  broke; it is never a pass, and like DIVERGES it stays due until a later
  PASS (owner, plan 58, 2026-10-20).
```

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
left uncommitted. Raw streams stay under
`~/.cache/agent-skills/cc-guide/probes/`.
```

**with:**

```markdown
left uncommitted. `PROBES.md`'s log table is the one whose header names the
date, version, probe and outcome columns; other tables, such as a legend,
are skipped, and a log row whose outcome is not one of R10.5's three is a
setup error (owner, plan 58, 2026-10-20). Raw streams stay under
`~/.cache/agent-skills/cc-guide/probes/`.
```

- [ ] **Step 6: A5, R12.6.**

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
R12.6 **Probe assertions** are replayed against streams recorded from our own
probe runs.
```

**with:**

```markdown
R12.6 **Probe assertions** are replayed against streams recorded from our own
probe runs. Before they are committed, the streams are cut down to the events
the assertions read and scrubbed of paths, the login name, session and
tool-use ids, and MCP tool names; a test fails on a path, an id or an MCP
tool name that remains (owner, plan 58, 2026-10-20).
```

- [ ] **Step 7: Run the gates.**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`. The spec is under `specs/`, which the citation lint does not read.

- [ ] **Step 8: Commit.**

```bash
git add specs/claude-code-drift-automation-spec.md
git commit -m "docs(specs): settle Stage 5's open probe details (drift R6.7, R10, R12.6)"
```

---

### Task 2: The probe log reads only R10.5's outcomes, skips a legend, and keeps ERROR due

**Files:**
- Modify: `build/cc_guide/state.py` (constants; `parse_probes`, with two helpers before it)
- Modify: `build/cc_guide/check.py` (the `state` import; `due_probes`)
- Test: `build/cc_guide/test_state.py`, `build/cc_guide/test_check.py`

**Interfaces:**
- Produces: in `state.py`, `PASS, DIVERGES, ERROR = 'PASS', 'DIVERGES', 'ERROR'`, `OUTCOMES`, `PROBE_COLUMNS: frozenset[str]`, `table_cells(line: str) -> list[str]` and `is_probe_header(line: str) -> bool`. `parse_probes` raises `SetupError(f'{PROBES}: unreadable row {s!r}')` on an unknown or empty outcome. `check.due_probes` reports `'ERROR with no later PASS'`.

- [ ] **Step 1: Write the failing tests.**

**Replace** in `build/cc_guide/test_state.py`:

```python
    assert str(err.value) == f"{state.PROBES}: unreadable row '| soon | 2.1.290 | x | PASS |'"


def test_a_source_reads_the_working_tree_or_a_commit(tmp_path):
```

**with:**

```python
    assert str(err.value) == f"{state.PROBES}: unreadable row '| soon | 2.1.290 | x | PASS |'"


def test_probe_rows_skip_a_legend_table_and_reject_an_unknown_outcome():
    '''The probe registry's gaps, part (a): a second table, such as a legend, is
    skipped rather than read as rows, and an outcome outside R10.5's words,
    or an empty one, is a SetupError, never a row read as passed.'''
    log = ['| Date | Version | Binary | Probe | Outcome | Finding | Flags |', '|---|---|---|---|---|---|---|',
           '| 2026-10-10 | 2.1.290 | ~/bin/claude | agent-tools | ERROR | no init event | |']
    legend = ['| Outcome | Meaning |', '|---|---|', '| ERROR | the mechanism never fired |']
    text = '\n'.join(['# Probe log', '', *log, '', *legend, ''])
    assert state.parse_probes(text) == [state.ProbeRow(date(2026, 10, 10), '2.1.290', 'agent-tools', 'ERROR')]
    for outcome in ('DIVERGED', ''):
        bad = log[2].replace('| ERROR |', f'| {outcome} |')
        with pytest.raises(state.SetupError) as err:
            state.parse_probes('\n'.join([*log[:2], bad, '']))
        assert str(err.value) == f'{state.PROBES}: unreadable row {bad!r}'


def test_the_probe_log_header_names_the_four_log_columns():
    assert state.is_probe_header('| Date | Version | Binary | Probe | Outcome | Finding | Flags |')
    assert not state.is_probe_header('| Outcome | Meaning |')
    assert not state.is_probe_header('Date Version Probe Outcome')


def test_a_source_reads_the_working_tree_or_a_commit(tmp_path):
```

**Replace** in `build/cc_guide/test_check.py`:

```python
    ([('2026-10-01', '2.1.902', 'DIVERGES'), ('2026-10-02', '2.1.902', 'PASS')], date(2026, 10, 2), None),
])
def test_probe_due_rules(history, today, why):
```

**with:**

```python
    ([('2026-10-01', '2.1.902', 'DIVERGES'), ('2026-10-02', '2.1.902', 'PASS')], date(2026, 10, 2), None),
    # R10.5: ERROR is never a pass, so it stays due until a later PASS (the probe registry's gaps, part a).
    ([('2026-10-01', '2.1.902', 'ERROR')], date(2026, 10, 1), 'ERROR with no later PASS'),
    ([('2026-10-01', '2.1.902', 'PASS'), ('2026-10-02', '2.1.902', 'ERROR')], date(2026, 10, 2),
     'ERROR with no later PASS'),
    ([('2026-10-01', '2.1.902', 'ERROR'), ('2026-10-02', '2.1.902', 'PASS')], date(2026, 10, 2), None),
])
def test_probe_due_rules(history, today, why):
```

<!-- red:task2 test_state.py test_check.py -->

- [ ] **Step 2: Run the tests to verify they fail.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_state.py test_check.py`
Expected: 4 failed. The legend test fails because the legend's rows raise `SetupError`, the header test with `AttributeError: module 'state' has no attribute 'is_probe_header'`, and the two due cases that end on ERROR with `None` in place of `'ERROR with no later PASS'`. The `[ERROR, PASS]` case passes before and after: it guards that a later PASS settles an ERROR.

- [ ] **Step 3: Write the implementation in `state.py`.**

**Replace** in `build/cc_guide/state.py`:

```python
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
```

**with:**

```python
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
# R10.5's outcomes, and the columns that mark PROBES.md's log table (R10.6).
PASS, DIVERGES, ERROR = 'PASS', 'DIVERGES', 'ERROR'
OUTCOMES = (PASS, DIVERGES, ERROR)
PROBE_COLUMNS = frozenset({'date', 'version', 'probe', 'outcome'})
```

**Replace** in `build/cc_guide/state.py`:

```python
def parse_probes(text: str | None) -> list[ProbeRow]:
    '''PROBES.md's rows (R10.6), in file order. The table's header names the
    columns; date, version, probe and outcome are read. An absent file has no
    rows: Stage 5 creates it, and until then no probe is registered.'''
    if text is None:
        return []
    rows: list[ProbeRow] = []
    header: list[str] | None = None
    for line in text.split('\n'):
        s = line.strip()
        if not s.startswith('|'):
            header = None
            continue
        cells = [c.strip() for c in CELL_SPLIT_RE.split(s.strip('|'))]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set(s) <= set('|-: '):
            continue
        row = dict(zip(header, cells))
        try:
            version_key(row['version'])
            rows.append(ProbeRow(date.fromisoformat(row['date']), row['version'],
                                 row['probe'], row['outcome'].upper()))
        except (KeyError, ValueError):
            raise SetupError(f'{PROBES}: unreadable row {s!r}') from None
    return rows
```

**with:**

```python
def table_cells(line: str) -> list[str]:
    '''A Markdown table line's cells, stripped; an escaped pipe stays in its cell.'''
    return [c.strip() for c in CELL_SPLIT_RE.split(line.strip().strip('|'))]


def is_probe_header(line: str) -> bool:
    '''Whether the line heads PROBES.md's log table: a table line naming the
    date, version, probe and outcome columns.'''
    return line.strip().startswith('|') and PROBE_COLUMNS <= {c.lower() for c in table_cells(line)}


def parse_probes(text: str | None) -> list[ProbeRow]:
    '''PROBES.md's rows (R10.6), in file order. The log table is any table
    whose header names the date, version, probe and outcome columns; another
    table, such as a legend, is skipped. A row needs a release label, a
    date, a probe and one of R10.5's outcomes, so a typo such as `DIVERGED`
    is a SetupError, never a row read as passed. An absent file has no rows:
    the first `probes` run creates it.'''
    if text is None:
        return []
    rows: list[ProbeRow] = []
    header: list[str] | None = None
    for line in text.split('\n'):
        s = line.strip()
        if not s.startswith('|'):
            header = None
            continue
        if header is None:
            header = [c.lower() for c in table_cells(s)]
            continue
        if set(s) <= set('|-: ') or not PROBE_COLUMNS <= set(header):
            continue
        row = dict(zip(header, table_cells(s)))
        try:
            version_key(row['version'])
            outcome = row['outcome'].upper()
            if outcome not in OUTCOMES or not row['probe']:
                raise ValueError(outcome)
            rows.append(ProbeRow(date.fromisoformat(row['date']), row['version'], row['probe'], outcome))
        except (KeyError, ValueError):
            raise SetupError(f'{PROBES}: unreadable row {s!r}') from None
    return rows
```

- [ ] **Step 4: Write the implementation in `check.py`.**

**Replace** in `build/cc_guide/check.py`:

```python
from state import (BASELINE, MANIFEST, PROBES, Manifest, ProbeRow, SetupError, Snapshot, Source, block_namer,
                   citing_files, fetch_record, group_terms, latest_docs, no_snapshot, parse_baseline,
                   parse_manifest, parse_probes, read_fetch, read_utf8, snapshot_text)
```

**with:**

```python
from state import (BASELINE, DIVERGES, ERROR, MANIFEST, PASS, PROBES, Manifest, ProbeRow, SetupError, Snapshot,
                   Source, block_namer, citing_files, fetch_record, group_terms, latest_docs, no_snapshot,
                   parse_baseline, parse_manifest, parse_probes, read_fetch, read_utf8, snapshot_text)
```

**Replace** in `build/cc_guide/check.py`:

```python
    '''R6.7: a registered probe is due with no row; with a DIVERGES row and no
    later PASS; or `days` after its last row once a release has shipped past
    that row's version.'''
    out = []
    for pid in manifest.probes:
        mine = [r for r in rows if r.probe == pid]
        if not mine:
            out.append({'probe': pid, 'why': 'never run'})
            continue
        diverged = False
        for r in mine:
            diverged = True if r.outcome == 'DIVERGES' else False if r.outcome == 'PASS' else diverged
        last = mine[-1]
        if diverged:
            out.append({'probe': pid, 'why': 'DIVERGES with no later PASS'})
```

**with:**

```python
    '''R6.7: a registered probe is due with no row; with a DIVERGES or ERROR
    row and no later PASS, since ERROR is never a pass (R10.5); or `days`
    after its last row once a release has shipped past that row's version.'''
    out = []
    for pid in manifest.probes:
        mine = [r for r in rows if r.probe == pid]
        if not mine:
            out.append({'probe': pid, 'why': 'never run'})
            continue
        unsettled: list[str] = []
        for r in mine:
            unsettled = [] if r.outcome == PASS else unsettled + [r.outcome]
        last = mine[-1]
        if unsettled:
            word = DIVERGES if DIVERGES in unsettled else ERROR
            out.append({'probe': pid, 'why': f'{word} with no later PASS'})
```

- [ ] **Step 5: Run the tests to verify they pass.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +5 against Task 1 Step 1.

- [ ] **Step 6: Run the gates and commit.**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`.

```bash
git add build/cc_guide/state.py build/cc_guide/check.py build/cc_guide/test_state.py build/cc_guide/test_check.py
git commit -m "fix(cc_guide): read only R10.5's probe outcomes and keep ERROR due"
```

---

### Task 3: The probe assertions and the fixture scrubber (`probe_checks.py`)

**Files:**
- Create: `build/cc_guide/probe_checks.py`
- Test: `build/cc_guide/test_probe_checks.py`

**Interfaces:**
- Consumes: `state.PASS`, `state.DIVERGES`, `state.ERROR` (Task 2).
- Produces, for Tasks 4 and 6: `Verdict(outcome: str, finding: str)` (a NamedTuple); `parse_stream(text: str) -> list[dict] | None`; `is_init(event: dict) -> bool`; `broken(events: list[dict] | None) -> str | None`; `assess_agent_tools(with_bash, without_bash, platform: str) -> Verdict`; `assess_stop_continuation(events, log: list[str]) -> Verdict`; `assess_agent_model_pins(events, transcripts: dict[str, list[dict]]) -> Verdict`; `assess_guard_liveness(streams: list[list[dict] | None]) -> Verdict`; `dispatches(events) -> dict[str, str]`; `forwarded_models(events, ids: set[str]) -> set[str]`; `tool_result_text(events, tool_use_id: str) -> str | None`; `scrub_events(events: list[dict], private: list[str]) -> str`; the constants `PIN_AGENTS`, `GUARD_CHECKS` and `GUARD_MARKER`.

The assertions read only raw stream-json fields, never the model's prose (R10.5). Each one returns ERROR, not PASS, when its mechanism never fired: no init event, no result event, an error result, no logged hook call, an agent never dispatched, or a command never run.

- [ ] **Step 1: Write the failing tests.**

**Create** `build/cc_guide/test_probe_checks.py`:

```python
'''Tests for probe_checks.py: each probe's PASS, DIVERGES and ERROR cases on
hand-built events shaped like the streams recorded while planning (Claude
Code 2.1.303, 2026-10-20), and the fixture scrubber (drift spec R10.2,
R10.5, R12.6).'''
import json

import pytest

import probe_checks as pc
from cc_fixtures import isolated_home  # noqa: F401
from state import DIVERGES, ERROR, PASS


def init(tools=('Read', 'Bash'), model='claude-sonnet-5-5'):
    return {'type': 'system', 'subtype': 'init', 'tools': list(tools), 'model': model, 'session_id': 's-1'}


def result(is_error=False):
    return {'type': 'result', 'subtype': 'error_during_execution' if is_error else 'success', 'is_error': is_error}


def assistant(*blocks, parent=None, model='claude-sonnet-5-5'):
    return {'type': 'assistant', 'parent_tool_use_id': parent, 'message': {'model': model, 'content': list(blocks)}}


def tool_use(tid, name, **given):
    return {'type': 'tool_use', 'id': tid, 'name': name, 'input': given}


def tool_result(tid, text, is_error=False, parent=None):
    return {'type': 'user', 'parent_tool_use_id': parent,
            'message': {'content': [{'type': 'tool_result', 'tool_use_id': tid, 'is_error': is_error,
                                     'content': [{'type': 'text', 'text': text}]}]}}


def stop_response(code):
    return {'type': 'system', 'subtype': 'hook_response', 'hook_event': 'Stop', 'hook_name': 'Stop',
            'exit_code': code, 'outcome': 'error' if code else 'success'}


def test_a_stream_skips_merged_stderr_text_and_a_bad_json_line_breaks_it():
    text = 'a warning on stderr\n' + json.dumps(init()) + '\n\n' + json.dumps(result()) + '\n'
    assert [e['type'] for e in pc.parse_stream(text)] == ['system', 'result']
    assert pc.parse_stream(json.dumps(init()) + '\n{"type": \n') is None
    assert pc.parse_stream('[1, 2]\n') == []


@pytest.mark.parametrize('events, why', [
    (None, 'no stream-json events'),
    ([], 'no stream-json events'),
    ([result()], 'no init event'),
    ([init()], 'no result event'),
    # A run that waits on background agents writes a result per turn; an error in any of them counts.
    ([init(), result(), init(), result(is_error=True)], 'a result event is an error (error_during_execution)'),
    ([init(), result(), init(), result()], None),
])
def test_a_run_is_broken_without_init_or_result_or_with_an_error_result(events, why):
    assert pc.broken(events) == why


def tools_run(*tools):
    return [init(tools), assistant({'type': 'text', 'text': 'OK'}), result()]


@pytest.mark.parametrize('with_bash, without_bash, platform, verdict', [
    (('Read', 'Bash'), ('Read', 'Grep', 'Glob'), 'darwin',
     (PASS, 'with Bash: Bash, Read; without Bash: Glob, Grep, Read')),
    (('Read', 'Grep', 'Glob', 'Bash'), ('Read', 'Grep', 'Glob'), 'linux',
     (DIVERGES, 'with Bash: Bash, Glob, Grep, Read; without Bash: Glob, Grep, Read')),
    (('Read', 'Bash'), ('Read', 'Grep'), 'darwin', (DIVERGES, 'with Bash: Bash, Read; without Bash: Grep, Read')),
    (('Read', 'Bash'), ('Read',), 'darwin', (ERROR, 'the control agent lists neither Grep nor Glob')),
    (('Read', 'Bash', 'Agent'), ('Read', 'Grep', 'Glob'), 'darwin',
     (ERROR, 'the agent with Bash did not get its own tool list: Agent, Bash, Read')),
    (('Read', 'Bash'), ('Read', 'Bash', 'Grep'), 'darwin',
     (ERROR, 'the control agent did not get its own tool list: Bash, Grep, Read')),
    (('Read', 'Bash'), ('Read', 'Grep', 'Glob'), 'win32',
     (ERROR, 'the guide states this rule for macOS, Linux and WSL; this run is on win32')),
])
def test_agent_tools(with_bash, without_bash, platform, verdict):
    assert pc.assess_agent_tools(tools_run(*with_bash), tools_run(*without_bash), platform) == verdict


def test_agent_tools_names_the_broken_run():
    assert pc.assess_agent_tools(tools_run('Read', 'Bash'), [init()], 'darwin') == (
        ERROR, 'the agent without Bash: no result event')


def stop_run(*codes):
    return [init(), *[stop_response(c) for c in codes], result()]


@pytest.mark.parametrize('events, log, verdict', [
    (stop_run(2, 2, 0), ['false', 'true', 'true'], (PASS, 'stop_hook_active read false, true, true')),
    (stop_run(2, 2, 0), ['false', 'false', 'true'], (DIVERGES, 'stop_hook_active read false, false, true')),
    (stop_run(2), ['false'], (DIVERGES, 'stop_hook_active read false')),
    (stop_run(2, 2, 0), ['missing', 'missing', 'missing'],
     (DIVERGES, 'stop_hook_active read missing, missing, missing')),
    (stop_run(), [], (ERROR, 'the Stop hook never logged a call')),
    (stop_run(), ['false', 'true', 'true'],
     (ERROR, 'stop_hook_active read false, true, true, but the stream shows Stop hook exits []')),
    ([init()], ['false', 'true', 'true'], (ERROR, 'no result event')),
])
def test_stop_continuation(events, log, verdict):
    assert pc.assess_stop_continuation(events, log) == verdict


def pins_run(models=None, drop=()):
    '''A parent that dispatches the three pinned agents, each forwarding one
    message from the model given for it.'''
    models = {'Explore': 'claude-haiku-5-5', 'test-runner': 'claude-haiku-5-5', 'code-reviewer': 'claude-opus-5-5',
              **(models or {})}
    sent = [tool_use(f'toolu_{n}', 'Agent', subagent_type=agent, prompt='p')
            for n, agent in enumerate(pc.PIN_AGENTS) if agent not in drop]
    forwarded = [assistant({'type': 'text', 'text': 'done'}, parent=f'toolu_{n}', model=models[agent])
                 for n, agent in enumerate(pc.PIN_AGENTS) if agent not in drop]
    return [init(), *[assistant(block) for block in sent], *forwarded, result(), init(), result()]


TRANSCRIPTS = {'Explore': [{'model': 'claude-haiku-5-5', 'effort': 'low'}],
               'test-runner': [{'model': 'claude-haiku-5-5', 'effort': 'low'}],
               'code-reviewer': [{'model': 'claude-opus-5-5', 'effort': 'xhigh'}] * 2}


@pytest.mark.parametrize('events, transcripts, verdict', [
    (pins_run(), TRANSCRIPTS,
     (PASS, 'Explore and test-runner served claude-haiku-5-5; code-reviewer effort xhigh')),
    (pins_run({'Explore': 'claude-sonnet-5-5'}), TRANSCRIPTS, (DIVERGES, 'Explore served claude-sonnet-5-5')),
    (pins_run(), {**TRANSCRIPTS, 'code-reviewer': [{'model': 'claude-opus-5-5', 'effort': 'low'}]},
     (DIVERGES, 'code-reviewer effort low')),
    (pins_run(drop=('test-runner',)), TRANSCRIPTS, (ERROR, 'test-runner was never dispatched')),
    (pins_run(), {k: v for k, v in TRANSCRIPTS.items() if k != 'Explore'}, (ERROR, 'no transcript lines for Explore')),
    (pins_run()[:-2] + [result(is_error=True)], TRANSCRIPTS,
     (ERROR, 'a result event is an error (error_during_execution)')),
    # Claude Code records a message it made itself, such as an API error, as model <synthetic>: the run broke.
    (pins_run(), {**TRANSCRIPTS, 'code-reviewer': [*TRANSCRIPTS['code-reviewer'], {'model': '<synthetic>'}]},
     (ERROR, 'code-reviewer hit an API error: a message from model <synthetic>')),
    (pins_run({'Explore': '<synthetic>'}), TRANSCRIPTS,
     (ERROR, 'Explore hit an API error: a message from model <synthetic>')),
])
def test_agent_model_pins(events, transcripts, verdict):
    assert pc.assess_agent_model_pins(events, transcripts) == verdict


def test_agent_model_pins_needs_a_forwarded_message_for_each_agent():
    events = [e for e in pins_run() if e.get('parent_tool_use_id') != 'toolu_2']
    assert pc.assess_agent_model_pins(events, TRANSCRIPTS) == (ERROR, 'code-reviewer forwarded no message')


DENIAL = 'PreToolUse:Bash hook error: readonly-agent-guard: the Explore agent is read-only on this checkout'


def guard_run(command, output, model='claude-haiku-5-5'):
    return [init(('Read', 'Bash'), model), assistant(tool_use('toolu_g', 'Bash', command=command)),
            tool_result('toolu_g', output, is_error=pc.GUARD_MARKER in output), result()]


def guard_streams(first='(Bash completed with no output)', second=DENIAL, third=DENIAL):
    return [guard_run(cmd, out) for (cmd, _), out in zip(pc.GUARD_CHECKS, (first, second, third))]


@pytest.mark.parametrize('streams, verdict', [
    (guard_streams(), (PASS, 'git status passed; git fetch and git config --global were denied')),
    (guard_streams(second='Would fetch from origin'), (DIVERGES, 'git fetch --dry-run origin was not denied')),
    (guard_streams(first=DENIAL, third='user.name=x'),
     (DIVERGES, 'git status --porcelain was denied; git config --global --list was not denied')),
    (guard_streams()[:2], (ERROR, 'expected 3 streams, found 2')),
    ([*guard_streams()[:2], None], (ERROR, 'check 3: no stream-json events')),
    ([*guard_streams()[:2], [init(), assistant({'type': 'text', 'text': 'I will not run that.'}), result()]],
     (ERROR, 'check 3: the agent never ran git config --global --list, or its result is missing')),
])
def test_guard_liveness(streams, verdict):
    assert pc.assess_guard_liveness(streams) == verdict


def test_scrub_keeps_what_the_assertions_read_and_drops_private_text():
    home, scratch = '/Users/someone', '/private/var/folders/xy/T/cc-guide-probe-pins-abc'
    events = [
        {**init(('Read', 'Bash', 'mcp__mine__search')), 'cwd': scratch, 'memory_paths': [f'{home}/.claude'],
         'mcp_servers': [{'name': 'mine'}], 'session_id': '364e6342-a957-4e26-a308-caa9e4b4bc69', 'plugins': ['x']},
        {'type': 'system', 'subtype': 'task_started', 'prompt': f'List {scratch}'},
        assistant(tool_use('toolu_01AbC', 'Agent', subagent_type='Explore', prompt=f'List {scratch}')),
        assistant({'type': 'text', 'text': f'{home} holds secrets'}, parent='toolu_01AbC', model='claude-haiku-5-5'),
        tool_result('toolu_01AbC', f'drwx someone staff {scratch}/a.py'),
        tool_result('toolu_02', DENIAL + f'\nsee {home}/x', is_error=True),
        stop_response(2),
        {**result(), 'total_cost_usd': 0.2, 'modelUsage': {}, 'session_id': '364e6342-a957-4e26-a308-caa9e4b4bc69'},
    ]
    text = pc.scrub_events(events, [home, scratch, 'someone'])
    for leak in (home, scratch, 'someone', '364e6342', 'toolu_01AbC', 'mine', 'mcp__', 'secrets', 'List'):
        assert leak not in text
    kept = pc.parse_stream(text)
    assert [e.get('subtype', e['type']) for e in kept] == [
        'init', 'assistant', 'assistant', 'user', 'user', 'hook_response', 'success']
    assert kept[0] == {'type': 'system', 'subtype': 'init', 'tools': ['Read', 'Bash'], 'model': 'claude-sonnet-5-5',
                       'claude_code_version': None}
    assert pc.dispatches(kept) == {'toolu_fixture1': 'Explore'}
    assert pc.forwarded_models(kept, {'toolu_fixture1'}) == {'claude-haiku-5-5'}
    assert pc.tool_result_text(kept, 'toolu_fixture2') == DENIAL
    assert pc.tool_result_text(kept, 'toolu_fixture1') == '<output>'
```

<!-- red:task3 test_probe_checks.py -->

- [ ] **Step 2: Run the tests to verify they fail.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_probe_checks.py`
Expected: a collection error, `ModuleNotFoundError: No module named 'probe_checks'`.

- [ ] **Step 3: Write the implementation.**

**Create** `build/cc_guide/probe_checks.py`:

```python
# cc-guide: subagents.frontmatter subagents.tools subagents.models hooks.events hooks.exit-codes hooks.patterns @2.1.304
'''The probe assertions (drift spec R10.2, R10.5): pure functions over a probe
run's raw stream-json events and the side files the run leaves, each giving
an outcome and a one-line finding. They read event fields, never the model's
prose. Tests replay them against streams recorded from our own probe runs
(R12.6), cut down and scrubbed by scrub_events before they are committed.

PASS means the behaviour matches the guide. DIVERGES means it does not.
ERROR means the probe's mechanism never fired or the run broke, and it is
never a pass.'''
import json
import re
from typing import NamedTuple

from state import DIVERGES, ERROR, PASS

GREP_GLOB = frozenset({'Grep', 'Glob'})
WITH_BASH_TOOLS = frozenset({'Read', 'Bash'}) | GREP_GLOB
WITHOUT_BASH_TOOLS = frozenset({'Read'}) | GREP_GLOB
# The guide states the Grep and Glob rule for macOS, Linux and WSL (subagents.tools).
SUPPORTED_PLATFORMS = ('darwin', 'linux')
STOP_LOG = ['false', 'true', 'true']
STOP_EXITS = [2, 2, 0]
DISPATCH_TOOLS = ('Agent', 'Task')  # the subagent tool's name, and its older one
HAIKU_AGENTS = ('Explore', 'test-runner')
REVIEWER, REVIEWER_EFFORT = 'code-reviewer', 'xhigh'
PIN_AGENTS = (*HAIKU_AGENTS, REVIEWER)
SYNTHETIC = '<synthetic>'  # the model Claude Code records on a message it made itself, such as an API error
GUARD_MARKER = 'readonly-agent-guard:'
# hooks/probe-readonly-guard.sh's three checks: the command each asks for, and
# whether the guard must deny it.
GUARD_CHECKS = (('git status --porcelain', False), ('git fetch --dry-run origin', True),
                ('git config --global --list', True))
UUID_RE = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
TOOL_ID_RE = re.compile(r'toolu_[A-Za-z0-9]+')
MCP_PREFIX = 'mcp__'


class Verdict(NamedTuple):
    outcome: str
    finding: str


def parse_stream(text: str) -> list[dict] | None:
    '''A stream-json file's events, one JSON object a line. A line that does
    not open with `{` is stderr text the guard probe merges into its stream,
    and is skipped; one that opens with `{` but does not parse makes the
    whole stream None, so the run reads as broken.'''
    events = []
    for line in text.split('\n'):
        if not line.startswith('{'):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return None
        if not isinstance(event, dict):
            return None
        events.append(event)
    return events


def is_init(event: dict) -> bool:
    return event.get('type') == 'system' and event.get('subtype') == 'init'


def broken(events: list[dict] | None) -> str | None:
    '''Why a run broke, or None. A print-mode run that waits on background
    agents writes an init and a result event for each turn, so every result
    is read, not only the last line.'''
    if not events:
        return 'no stream-json events'
    if not any(map(is_init, events)):
        return 'no init event'
    results = [e for e in events if e.get('type') == 'result']
    if not results:
        return 'no result event'
    failed = next((r for r in results if r.get('is_error')), None)
    if failed is not None:
        return f"a result event is an error ({failed.get('subtype')})"
    return None


def init_tools(events: list[dict]) -> frozenset[str]:
    return frozenset(next(e for e in events if is_init(e)).get('tools') or [])


def assess_agent_tools(with_bash: list[dict] | None, without_bash: list[dict] | None, platform: str) -> Verdict:
    '''agent-tools: an agent that lists Bash gets neither Grep nor Glob, and
    one that lists them without Bash gets both, read from each run's init
    event. A run whose tool list is not its agent's, or a control that lists
    neither Grep nor Glob, is ERROR.'''
    if platform not in SUPPORTED_PLATFORMS:
        return Verdict(ERROR, f'the guide states this rule for macOS, Linux and WSL; this run is on {platform}')
    for name, events in (('with Bash', with_bash), ('without Bash', without_bash)):
        why = broken(events)
        if why:
            return Verdict(ERROR, f'the agent {name}: {why}')
    tools, control = init_tools(with_bash), init_tools(without_bash)
    if 'Bash' not in tools or not tools <= WITH_BASH_TOOLS:
        return Verdict(ERROR, f"the agent with Bash did not get its own tool list: {', '.join(sorted(tools))}")
    if 'Read' not in control or not control <= WITHOUT_BASH_TOOLS:
        return Verdict(ERROR, f"the control agent did not get its own tool list: {', '.join(sorted(control))}")
    if not control & GREP_GLOB:
        return Verdict(ERROR, 'the control agent lists neither Grep nor Glob')
    shown = f"with Bash: {', '.join(sorted(tools))}; without Bash: {', '.join(sorted(control))}"
    if tools & GREP_GLOB or not GREP_GLOB <= control:
        return Verdict(DIVERGES, shown)
    return Verdict(PASS, shown)


def assess_stop_continuation(events: list[dict] | None, log: list[str]) -> Verdict:
    '''stop-continuation: a Stop hook that blocks on its first two calls logs
    stop_hook_active as false, true, true, and the stream's Stop hook
    responses exit 2, 2 and 0. An empty log means the hook never ran.'''
    why = broken(events)
    if why:
        return Verdict(ERROR, why)
    if not log:
        return Verdict(ERROR, 'the Stop hook never logged a call')
    shown = f"stop_hook_active read {', '.join(log)}"
    if log != STOP_LOG:
        return Verdict(DIVERGES, shown)
    exits = [e.get('exit_code') for e in events if e.get('type') == 'system'
             and e.get('subtype') == 'hook_response' and e.get('hook_event') == 'Stop']
    if exits != STOP_EXITS:
        return Verdict(ERROR, f'{shown}, but the stream shows Stop hook exits {exits}')
    return Verdict(PASS, shown)


def dispatches(events: list[dict]) -> dict[str, str]:
    '''The main session's subagent calls: tool-use id -> subagent type.'''
    out = {}
    for e in events:
        if e.get('type') != 'assistant' or e.get('parent_tool_use_id'):
            continue
        for block in (e.get('message') or {}).get('content') or []:
            if block.get('type') == 'tool_use' and block.get('name') in DISPATCH_TOOLS:
                out[block.get('id')] = (block.get('input') or {}).get('subagent_type')
    return out


def forwarded_models(events: list[dict], ids: set[str]) -> set[str]:
    '''The models that served the forwarded messages of the given dispatches.'''
    return {(e.get('message') or {}).get('model') for e in events
            if e.get('type') == 'assistant' and e.get('parent_tool_use_id') in ids}


def assess_agent_model_pins(events: list[dict] | None, transcripts: dict[str, list[dict]]) -> Verdict:
    '''agent-model-pins: dispatched from an auto-mode parent, Explore and
    test-runner are served Haiku, and code-reviewer keeps `effort: xhigh`.
    Each subagent's model is read from its forwarded messages; its effort,
    which the stream lacks, from its transcript lines (R10.5). A message of
    model <synthetic>, in either, means an API error broke the run: ERROR.
    `transcripts` maps an agent type to its lines, each {'model': ...,
    'effort': ...}.'''
    why = broken(events)
    if why:
        return Verdict(ERROR, why)
    sent = dispatches(events)
    models: dict[str, set[str]] = {}
    for agent in PIN_AGENTS:
        ids = {tid for tid, kind in sent.items() if kind == agent}
        if not ids:
            return Verdict(ERROR, f'{agent} was never dispatched')
        forwarded = forwarded_models(events, ids)
        if not forwarded:
            return Verdict(ERROR, f'{agent} forwarded no message')
        if not transcripts.get(agent):
            return Verdict(ERROR, f'no transcript lines for {agent}')
        if SYNTHETIC in forwarded | {line.get('model') for line in transcripts[agent]}:
            return Verdict(ERROR, f'{agent} hit an API error: a message from model {SYNTHETIC}')
        models[agent] = forwarded
    wrong = [f"{agent} served {', '.join(sorted(map(str, models[agent])))}" for agent in HAIKU_AGENTS
             if not all('haiku' in str(m) for m in models[agent])]
    efforts = {line.get('effort') for line in transcripts[REVIEWER]}
    if efforts != {REVIEWER_EFFORT}:
        wrong.append(f"{REVIEWER} effort {', '.join(sorted(map(str, efforts)))}")
    if wrong:
        return Verdict(DIVERGES, '; '.join(wrong))
    served = ', '.join(sorted(models['Explore'] | models['test-runner']))
    return Verdict(PASS, f'Explore and test-runner served {served}; {REVIEWER} effort {REVIEWER_EFFORT}')


def bash_calls(events: list[dict]) -> list[tuple[str, str]]:
    '''(tool-use id, command) for each Bash call in the stream.'''
    return [(block.get('id'), (block.get('input') or {}).get('command') or '')
            for e in events if e.get('type') == 'assistant'
            for block in (e.get('message') or {}).get('content') or []
            if block.get('type') == 'tool_use' and block.get('name') == 'Bash']


def result_body(block: dict) -> str:
    '''A tool_result block's text, whether its content is a string or a list of text blocks.'''
    body = block.get('content')
    if isinstance(body, list):
        return '\n'.join(b.get('text', '') for b in body if isinstance(b, dict))
    return str(body or '')


def tool_result_text(events: list[dict], tool_use_id: str) -> str | None:
    '''The text of a tool call's result, or None when the stream has none.'''
    for e in events:
        content = (e.get('message') or {}).get('content') if e.get('type') == 'user' else None
        for block in content if isinstance(content, list) else []:
            if (isinstance(block, dict) and block.get('type') == 'tool_result'
                    and block.get('tool_use_id') == tool_use_id):
                return result_body(block)
    return None


def assess_guard_liveness(streams: list[list[dict] | None]) -> Verdict:
    '''guard-liveness: hooks/probe-readonly-guard.sh's three checks, read from
    the three streams it keeps. The read-only command must pass, and git
    fetch and git config --global must come back denied with the guard's
    marker. A check whose agent never ran its command is ERROR: the hook had
    nothing to judge.'''
    if len(streams) != len(GUARD_CHECKS):
        return Verdict(ERROR, f'expected {len(GUARD_CHECKS)} streams, found {len(streams)}')
    failed = []
    for n, (events, (command, denied)) in enumerate(zip(streams, GUARD_CHECKS), start=1):
        why = broken(events)
        if why:
            return Verdict(ERROR, f'check {n}: {why}')
        results = [tool_result_text(events, tid) for tid, cmd in bash_calls(events) if command in cmd]
        if not results or None in results:
            return Verdict(ERROR, f'check {n}: the agent never ran {command}, or its result is missing')
        if any(GUARD_MARKER in r for r in results) != denied:
            failed.append(f"{command} {'was not denied' if denied else 'was denied'}")
    if failed:
        return Verdict(DIVERGES, '; '.join(failed))
    return Verdict(PASS, 'git status passed; git fetch and git config --global were denied')


def _trim_block(block: dict) -> dict | None:
    kind = block.get('type')
    if kind == 'tool_use':
        kept = {k: v for k, v in (block.get('input') or {}).items() if k in ('subagent_type', 'command')}
        return {'type': kind, 'id': block.get('id'), 'name': block.get('name'), 'input': kept}
    if kind == 'tool_result':
        marked = [line for line in result_body(block).split('\n') if GUARD_MARKER in line]
        return {'type': kind, 'tool_use_id': block.get('tool_use_id'), 'is_error': block.get('is_error'),
                'content': '\n'.join(marked) if marked else '<output>'}
    if kind == 'text':
        return {'type': kind, 'text': '<text>'}
    return None


def _trim_event(event: dict) -> dict | None:
    kind, sub = event.get('type'), event.get('subtype')
    if is_init(event):
        # An MCP tool's name names a server the recording machine has installed.
        tools = [t for t in event.get('tools') or [] if not t.startswith(MCP_PREFIX)]
        return {'type': kind, 'subtype': sub, 'tools': tools, 'model': event.get('model'),
                'claude_code_version': event.get('claude_code_version')}
    if kind == 'system' and sub == 'hook_response':
        return {k: event.get(k) for k in ('type', 'subtype', 'hook_event', 'hook_name', 'exit_code', 'outcome')}
    if kind == 'result':
        return {k: event.get(k) for k in ('type', 'subtype', 'is_error', 'num_turns')}
    if kind in ('assistant', 'user'):
        message = event.get('message') or {}
        content = message.get('content')
        blocks = [_trim_block(b) for b in content if isinstance(b, dict)] if isinstance(content, list) else []
        trimmed = {'content': [b for b in blocks if b]}
        if kind == 'assistant':
            trimmed['model'] = message.get('model')
        return {'type': kind, 'parent_tool_use_id': event.get('parent_tool_use_id'), 'message': trimmed}
    return None


def scrub_events(events: list[dict], private: list[str]) -> str:
    '''A recorded stream as a committable fixture (R12.6; owner, plan 58
    decision D3): cut to the fields the assertions read, so text blocks and
    tool output lose their text, and stripped of what must stay out of a
    public repo: MCP tool names leave the init tool list, each string in
    `private` (home and scratch paths, the login name), longest first,
    becomes <private>, and uuids and tool-use ids become stable
    placeholders.'''
    kept = [t for t in map(_trim_event, events) if t is not None]
    text = '\n'.join(json.dumps(e, ensure_ascii=False) for e in kept) + '\n'
    for value in sorted(filter(None, private), key=len, reverse=True):
        text = text.replace(value, '<private>')
    ids: dict[str, str] = {}
    text = TOOL_ID_RE.sub(lambda m: ids.setdefault(m.group(0), f'toolu_fixture{len(ids) + 1}'), text)
    uuids: dict[str, str] = {}
    return UUID_RE.sub(lambda m: uuids.setdefault(m.group(0), f'uuid-{len(uuids) + 1}'), text)
```

- [ ] **Step 4: Stamp the citation.** The lint reads only tracked files, so stage the file first.

Run: `git add build/cc_guide/probe_checks.py build/cc_guide/test_probe_checks.py`

Run: `uv run --python 3.13 python build/cc_guide/cli.py baseline cite build/cc_guide/probe_checks.py`
Expected: `stamped build/cc_guide/probe_checks.py @<release>`, where the release is the newest `changed` among the cited sections.

- [ ] **Step 5: Run the tests to verify they pass.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +38 against Task 2.

- [ ] **Step 6: Run the gates and commit.**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`.

```bash
git add build/cc_guide/probe_checks.py build/cc_guide/test_probe_checks.py
git commit -m "feat(cc_guide): add the probe assertions and the fixture scrubber (drift R10.5, R12.6)"
```

---

### Task 4: The probe runner (`probes.py`) and Gate B's stream directory

**Files:**
- Create: `build/cc_guide/probes.py`
- Modify: `hooks/probe-readonly-guard.sh` (its header comment and its `probe` function)
- Test: `build/cc_guide/test_probes.py`

**Interfaces:**
- Consumes: Task 3's `probe_checks` names; `check.due_probes`; `docs.version_key`; `state.ERROR`, `state.PASS`, `state.MANIFEST`, `state.PROBES`, `state.SetupError`, `state.Source`, `state.is_probe_header`, `state.parse_manifest`, `state.parse_probes`.
- Produces, for Tasks 5 and 6: `execute(inv: Invocation, cwd: Path, out: Path, err: Path) -> int | None`, which runs one invocation in its own process group, returns None on a timeout, and stops the whole group on a timeout, Ctrl-C or SystemExit; `stop_group(proc)`, SIGTERM then SIGKILL to the group with stop signals held; `held_signals()`, which records SIGINT, SIGTERM, SIGHUP and SIGQUIT and acts on the first once its block ends; `term_as_exit()`, under which SIGTERM, SIGHUP and SIGQUIT raise SystemExit (an ignored one stays ignored); `run(repo: Path, cache: Path, claude: Path, *, only: list[str] | None, force: bool, allow_old: bool, newest: str, today: date, now: datetime, execute=execute, version_of=binary_version) -> tuple[int, list[str]]`; `binaries(path_env: str, home: Path, version_of=binary_version) -> list[Candidate]`; `describe(c: Candidate) -> str`; `PROBE_RUNS: dict[str, Probe]`, where each `Probe` has `prepare`, `collect`, `assess` and `fixtures` (run-directory file name to fixture file name); `reader(folder: Path, names: dict[str, str] | None = None)`; `save_fixtures(run_dir: Path, pid: str, dest: Path) -> list[Path]`; `stream_of(text: str | None)`; `LOG_TEXT`.
- `hooks/probe-readonly-guard.sh` reads `CLAUDE_BIN` (default `claude`) and, when `PROBE_STREAM_DIR` is set, copies each check's stream to `$PROBE_STREAM_DIR/<n>.jsonl`.

`run` raises `SetupError` (exit 2) for a registered probe that `PROBE_RUNS` lacks, an unknown `--only` id, a binary that is not an executable file, or a binary older than `newest` without `allow_old`. A timeout, a setup failure inside a probe, or unreadable output is an ERROR row, never a pass.

- [ ] **Step 1: Write the failing tests.**

**Create** `build/cc_guide/test_probes.py`:

```python
'''Tests for probes.py: R10.4's command lines and isolation, the run
directory and the PROBES.md row each probe leaves (R10.6), the version
refusal (R10.3), which probes run, and binaries. Every claude here is a
fake, so no test spends a token or reads the real ~/.claude.'''
import contextlib
import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import probes
import state
from cc_fixtures import MANIFEST_TOML, isolated_home, write_tree  # noqa: F401
from state import DIVERGES, ERROR, PASS

REPO = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 10, 20, 14, 0, tzinfo=timezone.utc)
TODAY = NOW.date()
REGISTRY = '\n'.join(['', '[[probe]]', "id = 'agent-tools'", "sections = ['beta.reference']", '',
                      '[[probe]]', "id = 'stop-continuation'", "sections = ['beta.reference']", ''])


def stream(*events) -> str:
    return ''.join(json.dumps(e) + '\n' for e in events)


def init(tools=('Read', 'Bash'), session='s-1'):
    return {'type': 'system', 'subtype': 'init', 'tools': list(tools), 'session_id': session}


RESULT = {'type': 'result', 'subtype': 'success', 'is_error': False}
TOOLS_PASS = {'probe-with-bash': stream(init(), RESULT),
              'probe-without-bash': stream(init(('Read', 'Grep', 'Glob')), RESULT)}
STOP_PASS = stream(init(), *[{'type': 'system', 'subtype': 'hook_response', 'hook_event': 'Stop', 'exit_code': c}
                             for c in (2, 2, 0)], RESULT)


class FakeRuns:
    '''An Execute that writes each invocation's canned stdout, runs its side
    effect in the scratch directory, and records what it ran.'''

    def __init__(self, streams, side=None, timeout=()):
        self.streams, self.side, self.timeout, self.ran = streams, side or {}, set(timeout), []

    def __call__(self, inv, cwd, out, err):
        self.ran.append((inv, cwd, sorted(p.relative_to(cwd).as_posix() for p in cwd.rglob('*'))))
        out.write_text('' if inv.name in self.timeout else self.streams.get(inv.name, ''), encoding='utf-8')
        err.write_text('', encoding='utf-8')
        if inv.name in self.timeout:
            return None
        if inv.name in self.side:
            self.side[inv.name](cwd)
        return 0


def stop_log(*lines):
    return lambda cwd: (cwd / 'stop.log').write_text(''.join(f'{line}\n' for line in lines), encoding='utf-8')


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / 'repo'
    write_tree(root, {state.MANIFEST: MANIFEST_TOML + REGISTRY})
    return root


@pytest.fixture
def claude(tmp_path):
    path = tmp_path / 'bin' / 'claude'
    path.parent.mkdir()
    path.write_text('#!/bin/sh\nexit 0\n')
    path.chmod(0o755)
    return path


def run(repo, tmp_path, claude, fake, *, only=None, force=False, allow_old=False, version='2.1.902'):
    return probes.run(repo, tmp_path / 'cache', claude, only=only, force=force, allow_old=allow_old,
                      newest='2.1.902', today=TODAY, now=NOW, execute=fake, version_of=lambda path: version)


def test_the_command_line_follows_r10_4():
    argv = probes.claude_args('/bin/claude', 'Say OK.', turns=2, sources='project', mode='default')
    assert argv[:3] == ['/bin/claude', 'Say OK.', '-p']
    flags = {a: argv[i + 1] for i, a in enumerate(argv[:-1]) if a.startswith('--') and not argv[i + 1].startswith('--')}
    assert flags['--output-format'] == 'stream-json' and flags['--setting-sources'] == 'project'
    assert json.loads(flags['--settings']) == {'permissions': {'defaultMode': 'default'}}
    assert (flags['--model'], flags['--effort'], flags['--max-turns']) == ('sonnet', 'low', '2')
    assert argv[-1] == '--no-session-persistence'
    kept = probes.claude_args('c', 'p', turns=1, sources='user', mode='auto', allow=('Agent',), persist=True,
                              extra=('--x',))
    assert '--no-session-persistence' not in kept and kept[-1] == '--x'
    assert json.loads(kept[kept.index('--settings') + 1]) == {'permissions': {'defaultMode': 'auto',
                                                                              'allow': ['Agent']}}


def test_a_pass_appends_a_row_from_a_fresh_scratch_directory_that_is_then_removed(repo, tmp_path, claude):
    fake = FakeRuns(TOOLS_PASS)
    code, lines = run(repo, tmp_path, claude, fake, only=['agent-tools'])
    assert code == 0
    (first, cwd, files), (second, cwd2, _) = fake.ran
    assert cwd == cwd2 and not cwd.exists() and not cwd.is_relative_to(repo)
    assert cwd.name.startswith('cc-guide-probe-agent-tools-')
    assert files == ['.claude', '.claude/agents', '.claude/agents/probe-with-bash.md',
                     '.claude/agents/probe-without-bash.md']
    assert (first.name, first.argv[-3:]) == ('probe-with-bash', ['--agent', 'probe-with-bash',
                                                                 '--no-session-persistence'])
    rows = state.parse_probes((repo / state.PROBES).read_text())
    assert rows == [state.ProbeRow(TODAY, '2.1.902', 'agent-tools', PASS)]
    run_dir = tmp_path / 'cache' / 'probes' / '20261020T140000-agent-tools'
    assert sorted(p.name for p in run_dir.iterdir()) == [
        'probe-with-bash.argv.json', 'probe-with-bash.err', 'probe-with-bash.jsonl',
        'probe-without-bash.argv.json', 'probe-without-bash.err', 'probe-without-bash.jsonl']
    assert lines == [f'probes: 2.1.902 at {claude}',
                     'agent-tools: PASS: with Bash: Bash, Read; without Bash: Glob, Grep, Read',
                     f'  raw output: {run_dir}', f'appended 1 row(s) to {state.PROBES}; nothing is committed']


def test_a_divergence_or_an_error_exits_one_and_is_logged(repo, tmp_path, claude):
    fake = FakeRuns({'stop': STOP_PASS, **TOOLS_PASS}, side={'stop': stop_log('false', 'false', 'true')},
                    timeout=['probe-with-bash'])
    code, lines = run(repo, tmp_path, claude, fake, force=True)
    assert code == 1
    rows = state.parse_probes((repo / state.PROBES).read_text())
    assert [(r.probe, r.outcome) for r in rows] == [('agent-tools', ERROR), ('stop-continuation', DIVERGES)]
    assert 'agent-tools: ERROR: probe-with-bash timed out after 600 s' in lines
    assert 'stop-continuation: DIVERGES: stop_hook_active read false, false, true' in lines


def test_an_old_binary_is_refused_unless_allowed_and_the_row_records_the_flag(repo, tmp_path, claude):
    with pytest.raises(state.SetupError) as err:
        run(repo, tmp_path, claude, FakeRuns(TOOLS_PASS), only=['agent-tools'], version='2.1.901')
    assert str(err.value) == (f'--claude {claude} is 2.1.901, older than the newest changelog release 2.1.902: '
                              'pass --allow-old to run it anyway, and each row records the flag (R10.3)')
    assert not (repo / state.PROBES).exists()
    run(repo, tmp_path, claude, FakeRuns(TOOLS_PASS), only=['agent-tools'], version='2.1.901', allow_old=True)
    assert (repo / state.PROBES).read_text().split('\n')[-2].endswith('| agent-tools | PASS |'
                                                                     ' with Bash: Bash, Read; without Bash: Glob, Grep,'
                                                                     ' Read | --allow-old |')


def test_only_force_and_the_due_rules_choose_the_probes(repo, tmp_path, claude):
    write_tree(repo, {state.PROBES: probes.LOG_TEXT + '| 2026-10-19 | 2.1.902 | ~/c | agent-tools | PASS | ok | |\n'})
    fake = FakeRuns({'stop': STOP_PASS}, side={'stop': stop_log('false', 'true', 'true')})
    assert run(repo, tmp_path, claude, fake)[0] == 0
    assert [inv.name for inv, _, _ in fake.ran] == ['stop']
    fake = FakeRuns(TOOLS_PASS)
    run(repo, tmp_path, claude, fake, only=['agent-tools', 'agent-tools'])
    assert [inv.name for inv, _, _ in fake.ran] == ['probe-with-bash', 'probe-without-bash']
    assert run(repo, tmp_path, claude, FakeRuns({}), only=None) == (0, ['probes: none due'])
    with pytest.raises(state.SetupError) as err:
        run(repo, tmp_path, claude, FakeRuns({}), only=['agent-tool'])
    assert str(err.value) == '--only agent-tool: not a registered probe'


def test_a_registered_probe_with_no_runner_or_an_unusable_binary_is_a_setup_error(repo, tmp_path, claude):
    with pytest.raises(state.SetupError) as err:
        run(repo, tmp_path, tmp_path / 'missing', FakeRuns({}), force=True)
    assert str(err.value) == f"--claude {tmp_path / 'missing'}: not an executable file"
    write_tree(repo, {state.MANIFEST: MANIFEST_TOML + REGISTRY.replace('stop-continuation', 'skill-pins')})
    with pytest.raises(state.SetupError) as err:
        run(repo, tmp_path, claude, FakeRuns({}), force=True)
    assert str(err.value) == f'{state.MANIFEST} registers skill-pins, which probes.py does not run'


def test_append_row_keeps_the_table_whole_and_escapes_pipes(tmp_path):
    path = tmp_path / 'PROBES.md'
    legend = '\n'.join(['', 'Outcomes:', '', '| Outcome | Meaning |', '|---|---|', '| ERROR | never fired |', ''])
    path.write_text(probes.LOG_TEXT + legend)
    verdict = probes.Verdict(DIVERGES, 'a | b\nc')
    probes.append_row(path, probes.log_row(TODAY, '2.1.902', Path('/opt/claude'), 'agent-tools', verdict, False))
    lines = path.read_text().split('\n')
    assert lines[lines.index('|---|---|---|---|---|---|---|') + 1] == (
        '| 2026-10-20 | 2.1.902 | /opt/claude | agent-tools | DIVERGES | a \\| b c |  |')
    assert state.parse_probes(path.read_text()) == [state.ProbeRow(TODAY, '2.1.902', 'agent-tools', DIVERGES)]
    path.write_text('# Probe log\n\nNo table.\n')
    with pytest.raises(state.SetupError):
        probes.append_row(path, '| x |')


def test_append_row_replaces_the_log_whole_so_a_stop_never_cuts_it_short(tmp_path, monkeypatch):
    '''A SIGTERM during probes is a SystemExit (term_as_exit): one that lands
    while the log is written must leave the old log whole, not an empty file.'''
    path = tmp_path / 'log' / 'PROBES.md'
    path.parent.mkdir()
    path.write_text(probes.LOG_TEXT)

    def stopped(source, target):
        raise SystemExit(143)
    monkeypatch.setattr(probes.os, 'replace', stopped)
    with pytest.raises(SystemExit):
        probes.append_row(path, probes.log_row(TODAY, '2.1.902', Path('/c'), 'agent-tools', probes.Verdict(PASS, 'ok'),
                                               False))
    assert path.read_text() == probes.LOG_TEXT
    assert sorted(p.name for p in path.parent.iterdir()) == ['PROBES.md']


def test_a_failed_draft_write_leaves_no_draft(tmp_path, monkeypatch):
    path = tmp_path / 'log' / 'PROBES.md'
    path.parent.mkdir()
    path.write_text(probes.LOG_TEXT)
    real_write = Path.write_text

    def half(self, text, **kwargs):
        real_write(self, text[:len(text) // 2], **kwargs)
        raise OSError(28, 'No space left on device')
    monkeypatch.setattr(Path, 'write_text', half)
    with pytest.raises(OSError):
        probes.append_row(path, '| 2026-10-20 | 2.1.902 | /c | agent-tools | PASS | ok |  |')
    monkeypatch.undo()
    assert path.read_text() == probes.LOG_TEXT
    assert sorted(p.name for p in path.parent.iterdir()) == ['PROBES.md']


def test_two_runs_appending_at_once_both_keep_their_rows(tmp_path, monkeypatch):
    '''Two probes runs in one working tree: the read, insert and replace are
    one locked step, so neither run's row is lost.'''
    path = tmp_path / 'log' / 'PROBES.md'
    path.parent.mkdir()
    path.write_text(probes.LOG_TEXT)
    real_replace = os.replace

    def slow_replace(source, target):
        time.sleep(0.3)
        real_replace(source, target)
    monkeypatch.setattr(probes.os, 'replace', slow_replace)
    rows = [f'| 2026-10-20 | 2.1.902 | /c | {pid} | PASS | ok |  |' for pid in ('agent-tools', 'stop-continuation')]
    threads = [threading.Thread(target=probes.append_row, args=(path, row)) for row in rows]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sorted(r.probe for r in state.parse_probes(path.read_text())) == ['agent-tools', 'stop-continuation']


def test_the_log_shows_the_home_directory_as_a_tilde(isolated_home):
    assert probes.shown_path(isolated_home / '.local' / 'bin' / 'claude') == '~/.local/bin/claude'
    assert probes.shown_path(Path('/opt/claude')) == '/opt/claude'


def executable(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(0o755)
    return path


def test_binary_version_reads_the_label_or_refuses(tmp_path):
    good = executable(tmp_path / 'good', "#!/bin/sh\necho '2.1.303 (Claude Code)'\n")
    assert probes.binary_version(good) == '2.1.303'
    bad = executable(tmp_path / 'bad', '#!/bin/sh\necho hello\n')
    with pytest.raises(state.SetupError) as err:
        probes.binary_version(bad)
    assert str(err.value) == f'{bad} --version printed no Claude Code version'


def test_binaries_lists_each_path_claude_then_the_desktop_bundles(tmp_path, isolated_home):
    target = executable(tmp_path / 'versions' / '2.1.303', '#!/bin/sh\n')
    first = tmp_path / 'bin1'
    first.mkdir()
    (first / 'claude').symlink_to(target)
    second = executable(tmp_path / 'bin2' / 'claude', '#!/bin/sh\n')
    bundle = executable(isolated_home / probes.DESKTOP_BUNDLES / '2.1.304' / 'abc' / 'claude.app' / 'Contents'
                        / 'MacOS' / 'claude', '#!/bin/sh\n')
    versions = {first / 'claude': '2.1.303', bundle: '2.1.304'}

    def version_of(path):
        if path not in versions:
            raise state.SetupError('no version')
        return versions[path]
    found = probes.binaries(os.pathsep.join([str(first), '', str(tmp_path / 'none'), str(first), str(second.parent)]),
                            isolated_home, version_of)
    assert [(c.path, c.version, c.where) for c in found] == [
        (first / 'claude', '2.1.303', 'PATH'), (second, None, 'PATH'), (bundle, '2.1.304', probes.DESKTOP_NOTE)]
    assert probes.describe(found[0]) == f"2.1.303  {first / 'claude'} -> {target.resolve()}  (PATH)"
    assert probes.describe(found[1]) == f'version unknown  {second}  (PATH)'


FAKE_GUARD_CLAUDE = r'''#!/usr/bin/env bash
if [ "$1" = --version ]; then echo '2.1.902 (Claude Code)'; exit 0; fi
echo "argv: ${*:2}" >&2
case "$1" in
  *'git status'*) cmd='git status --porcelain'; out='(Bash completed with no output)'; err=false ;;
  *'git fetch'*) cmd='git fetch --dry-run origin'; out='readonly-agent-guard: denied'; err=true ;;
  *) cmd='git config --global --list'; out=@THIRD@; err=true ;;
esac
use='{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"%s"}}'
res='{"type":"tool_result","tool_use_id":"t1","is_error":%s,"content":"%s"}'
echo '{"type":"system","subtype":"init","tools":["Read","Bash"]}'
printf '{"type":"assistant","parent_tool_use_id":null,"message":{"model":"m","content":['"$use"']}}\n' "$cmd"
printf '{"type":"user","parent_tool_use_id":null,"message":{"content":['"$res"']}}\n' "$err" "$out"
echo '{"type":"result","subtype":"success","is_error":false}'
'''


@pytest.mark.parametrize('third, verdict', [
    ("'readonly-agent-guard: denied'", (PASS, 'git status passed; git fetch and git config --global were denied')),
    ("'user.name=x'", (DIVERGES, 'git config --global --list was not denied')),
])
def test_the_guard_probe_runs_the_real_script_and_reads_its_three_kept_streams(tmp_path, third, verdict):
    fake = executable(tmp_path / 'fake-claude', FAKE_GUARD_CLAUDE.replace('@THIRD@', third))
    run_dir = tmp_path / 'run'
    assert probes.run_probe('guard-liveness', str(fake), REPO, run_dir) == verdict
    assert sorted(p.name for p in run_dir.iterdir()) == [
        'guard-1.jsonl', 'guard-2.jsonl', 'guard-3.jsonl', 'guard.argv.json', 'guard.err', 'guard.txt']
    assert 'Claude Code: 2.1.902 (Claude Code)' in (run_dir / 'guard.txt').read_text()
    # The script merges stderr into each kept stream, where the fake printed its flags (R10.4).
    flags = (run_dir / 'guard-1.jsonl').read_text().split('\n')[0]
    for flag in ('--setting-sources user', '--max-turns 4', '--max-budget-usd 0.50', '--no-session-persistence',
                 '--agent Explore'):
        assert flag in flags


@pytest.mark.parametrize('calls, codes, log', [
    (['{"stop_hook_active": false}', '{"stop_hook_active":true}', '{"stop_hook_active": true}'], [2, 2, 0],
     'false\ntrue\ntrue\n'),
    (['{}'], [2], 'missing\n'),
])
def test_the_stop_hook_logs_the_flag_and_blocks_its_first_two_calls(tmp_path, calls, codes, log):
    (inv,) = probes.prepare_stop(tmp_path, 'claude', REPO)
    settings = json.loads((tmp_path / '.claude' / 'settings.json').read_text())
    hook = settings['hooks']['Stop'][0]['hooks'][0]['command']
    assert '--include-hook-events' in inv.argv and inv.argv[inv.argv.index('--setting-sources') + 1] == 'project'
    got = [subprocess.run([hook], input=c, text=True, capture_output=True).returncode for c in calls]
    assert (got, (tmp_path / 'stop.log').read_text()) == (codes, log)


def transcript(home, session, agent_id, agent_type, *lines):
    folder = home / '.claude' / 'projects' / '-private-tmp-x' / session / 'subagents'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f'agent-{agent_id}.meta.json').write_text(json.dumps({'agentType': agent_type}))
    (folder / f'agent-{agent_id}.jsonl').write_text(''.join(
        json.dumps({'type': kind, 'message': {'model': model}, 'effort': effort}) + '\n'
        for kind, model, effort in lines))


def test_read_transcripts_maps_each_agent_type_to_its_assistant_lines(isolated_home):
    transcript(isolated_home, 's-1', 'a1', 'Explore', ('user', None, None), ('assistant', 'claude-haiku-5-5', 'low'))
    transcript(isolated_home, 's-2', 'a2', 'Explore', ('assistant', 'claude-opus-5-5', 'high'))
    projects = isolated_home / '.claude' / 'projects'
    assert probes.read_transcripts(projects, 's-1') == {'Explore': [{'model': 'claude-haiku-5-5', 'effort': 'low'}]}
    assert probes.read_transcripts(projects, None) == {}


def pins_stream() -> str:
    '''A parent that dispatches the three pinned agents, each forwarding one message.'''
    sent = [{'type': 'assistant', 'parent_tool_use_id': None, 'message': {'model': 'claude-sonnet-5-5', 'content': [
        {'type': 'tool_use', 'id': f't{n}', 'name': 'Agent', 'input': {'subagent_type': agent}}]}}
        for n, agent in enumerate(('Explore', 'test-runner', 'code-reviewer'))]
    forwarded = [{'type': 'assistant', 'parent_tool_use_id': f't{n}', 'message': {'model': model, 'content': []}}
                 for n, model in enumerate(('claude-haiku-5-5', 'claude-haiku-5-5', 'claude-opus-5-5'))]
    return stream(init(), *sent, *forwarded, RESULT)


def leave_transcripts(home, reviewer_effort='xhigh'):
    '''A side effect that writes the session's three subagent transcripts.'''
    def side(cwd):
        for agent, model, effort in (('Explore', 'claude-haiku-5-5', 'low'), ('test-runner', 'claude-haiku-5-5', 'low'),
                                     ('code-reviewer', 'claude-opus-5-5', reviewer_effort)):
            transcript(home, 's-1', agent, agent, ('assistant', model, effort))
    return side


def test_the_pins_probe_persists_its_session_and_reads_effort_from_the_transcripts(tmp_path, isolated_home):
    fake = FakeRuns({'pins': pins_stream()}, side={'pins': leave_transcripts(isolated_home)})
    run_dir = tmp_path / 'run'
    verdict = probes.run_probe('agent-model-pins', 'claude', REPO, run_dir, fake)
    assert verdict == (PASS, 'Explore and test-runner served claude-haiku-5-5; code-reviewer effort xhigh')
    ((inv, cwd, files),) = fake.ran
    assert files == ['a.py'] and '--no-session-persistence' not in inv.argv and '--forward-subagent-text' in inv.argv
    assert inv.env == {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': '900000'} and inv.timeout == 1200
    assert inv.argv[inv.argv.index('--setting-sources') + 1] == 'user'
    assert json.loads(inv.argv[inv.argv.index('--settings') + 1]) == {'permissions': {'defaultMode': 'auto',
                                                                                      'allow': ['Agent']}}
    assert str(cwd) in inv.argv[1]
    assert json.loads((run_dir / 'transcripts.json').read_text())['code-reviewer'] == [
        {'model': 'claude-opus-5-5', 'effort': 'xhigh'}]


def test_output_of_another_shape_is_an_error_never_a_crash(tmp_path, isolated_home):
    '''An effort recorded as an object, as hooks receive it, makes the
    assessment raise TypeError: the row is ERROR, and the run goes on.'''
    fake = FakeRuns({'pins': pins_stream()}, side={'pins': leave_transcripts(isolated_home, {'level': 'xhigh'})})
    assert probes.run_probe('agent-model-pins', 'claude', REPO, tmp_path / 'run', fake) == (
        ERROR, "TypeError: unhashable type: 'dict'")


# A run whose leader starts a child, as Gate B's bash starts claude. It writes "<leader> <child>" to $1.
SLOW = '#!/bin/sh\nsleep 300 &\necho "$$ $!" > "$1"\nsleep 300\n'
# The same, but the leader and its child ignore SIGTERM, as a stuck claude might, so only SIGKILL ends them.
STUBBORN = "#!/bin/sh\ntrap '' TERM\nsleep 300 &\necho \"$$ $!\" > \"$1\"\nwait\n"


def written(path: Path, wait: float = 5) -> bool:
    '''Whether the file holds text within `wait` seconds.'''
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        if path.is_file() and path.read_text(encoding='utf-8').strip():
            return True
        time.sleep(0.01)
    return False


def gone(pid: int, wait: float = 5) -> bool:
    '''Whether the process ends within `wait` seconds.'''
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.05)
    return False


@pytest.fixture
def pids(tmp_path):
    '''The pid file a SLOW or STUBBORN run writes. Teardown kills what is
    left of its process group, so a failing test leaks no sleep.'''
    path = tmp_path / 'pids'
    yield path
    if path.is_file() and path.read_text(encoding='utf-8').split():
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(int(path.read_text(encoding='utf-8').split()[0]), signal.SIGKILL)


def child_of(path: Path) -> int:
    return int(path.read_text(encoding='utf-8').split()[1])


def test_a_timeout_stops_everything_the_run_started(tmp_path, pids):
    '''Gate B runs claude under bash: a timeout must stop the grandchild too,
    not only the bash that started it.'''
    inv = probes.Invocation('slow', [str(executable(tmp_path / 'slow', SLOW)), str(pids)], {}, 3)
    assert probes.execute(inv, tmp_path, tmp_path / 'slow.out', tmp_path / 'slow.err') is None
    assert written(pids), 'the run was stopped before it started its child'
    assert gone(child_of(pids))


def test_an_interrupt_stops_everything_the_run_started_and_still_propagates(tmp_path, pids, monkeypatch):
    '''Ctrl-C while a probe runs: its own process group gets no SIGINT from
    the terminal, so execute stops the group itself before re-raising.'''
    real_wait = subprocess.Popen.wait

    def interrupted(proc, timeout=None):
        if timeout == 30:  # the probe's own wait, once its child is running
            assert written(pids), 'the run never started its child'
            raise KeyboardInterrupt
        return real_wait(proc, timeout)
    monkeypatch.setattr(subprocess.Popen, 'wait', interrupted)
    inv = probes.Invocation('slow', [str(executable(tmp_path / 'slow', SLOW)), str(pids)], {}, 30)
    with pytest.raises(KeyboardInterrupt):
        probes.execute(inv, tmp_path, tmp_path / 'slow.out', tmp_path / 'slow.err')
    assert gone(child_of(pids))


def test_a_stop_while_the_run_starts_still_stops_it(tmp_path, pids, monkeypatch):
    '''A SIGTERM that lands while Popen starts the run is held until proc
    is bound, so the run is stopped, not orphaned.'''
    real_popen, leaders = subprocess.Popen, []

    def starting(*args, **kwargs):
        proc = real_popen(*args, **kwargs)
        leaders.append(proc.pid)
        os.kill(os.getpid(), signal.SIGTERM)
        return proc
    monkeypatch.setattr(subprocess, 'Popen', starting)
    inv = probes.Invocation('slow', [str(executable(tmp_path / 'slow', SLOW)), str(pids)], {}, 30)
    with pytest.raises(SystemExit):
        with probes.term_as_exit():
            probes.execute(inv, tmp_path, tmp_path / 'slow.out', tmp_path / 'slow.err')
    assert gone(leaders[0])


def test_a_second_signal_during_the_grace_still_ends_with_sigkill(tmp_path, pids, monkeypatch):
    '''Ctrl-C while stop_group waits out SIGTERM's grace is held, so the
    SIGKILL still goes out, and the interrupt is raised after it.'''
    monkeypatch.setattr(probes, 'KILL_GRACE', 1)
    proc = subprocess.Popen([str(executable(tmp_path / 'stubborn', STUBBORN)), str(pids)], start_new_session=True)
    assert written(pids)
    threading.Timer(0.3, os.kill, (os.getpid(), signal.SIGINT)).start()
    with pytest.raises(KeyboardInterrupt):
        probes.stop_group(proc)
    assert gone(child_of(pids))


# Run in a child Python, so a signal left at its default ends the child, not pytest.
STOP_CHECK = """
import os, signal, sys, time
import probes
signum = int(sys.argv[1])
before = signal.getsignal(signum)
try:
    with probes.term_as_exit():
        os.kill(os.getpid(), signum)
        time.sleep(5)
except SystemExit:
    assert signal.getsignal(signum) is before
    raise
"""


@pytest.mark.parametrize('signum', [signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT])
def test_a_stop_signal_while_probes_run_exits_through_the_cleanup_path(signum):
    '''SIGTERM (a stopped tool), SIGHUP (a closed terminal) and SIGQUIT end
    Python with no except or finally by default; while probes run each one
    raises SystemExit instead, and the old handler comes back after. A
    negative exit code means the signal ended the child unhandled.'''
    proc = subprocess.run([sys.executable, '-c', STOP_CHECK, str(int(signum))], cwd=Path(__file__).parent,
                          capture_output=True, text=True, timeout=30)
    assert (proc.returncode, proc.stderr) == (128 + signum, '')


def test_a_hangup_ignored_by_nohup_stays_ignored():
    before = signal.signal(signal.SIGHUP, signal.SIG_IGN)
    try:
        with probes.term_as_exit():
            assert signal.getsignal(signal.SIGHUP) is signal.SIG_IGN
    finally:
        signal.signal(signal.SIGHUP, before)


def test_held_signals_act_once_the_block_is_done():
    reached = []
    with pytest.raises(SystemExit):
        with probes.term_as_exit():
            with probes.held_signals():
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(0.2)
                reached.append('end of block')
    assert reached == ['end of block']


def test_a_setup_failure_is_an_error_never_a_pass(tmp_path, monkeypatch):
    def broken(scratch, claude, repo):
        raise OSError('disk full')
    monkeypatch.setitem(probes.PROBE_RUNS, 'agent-tools', probes.PROBE_RUNS['agent-tools']._replace(prepare=broken))
    assert probes.run_probe('agent-tools', 'claude', REPO, tmp_path / 'run', FakeRuns({})) == (
        ERROR, 'OSError: disk full')


def test_save_fixtures_scrubs_a_recorded_run_and_the_replay_reads_it_like_the_run(tmp_path, isolated_home):
    run_dir, dest = tmp_path / 'run', tmp_path / 'fixtures'
    with_bash = stream({**init(), 'cwd': str(isolated_home / 'work'), 'memory_paths': [str(isolated_home)]}, RESULT)
    write_tree(run_dir, {'probe-with-bash.jsonl': with_bash,
                         'probe-without-bash.jsonl': TOOLS_PASS['probe-without-bash']})
    probe = probes.PROBE_RUNS['agent-tools']
    written = probes.save_fixtures(run_dir, 'agent-tools', dest)
    assert sorted(p.name for p in written) == ['agent-tools.with-bash.jsonl', 'agent-tools.without-bash.jsonl']
    assert str(isolated_home) not in (dest / 'agent-tools.with-bash.jsonl').read_text()
    assert probe.assess(probes.reader(dest, probe.fixtures)) == probe.assess(probes.reader(run_dir))
    write_tree(run_dir, {'probe-with-bash.jsonl': 'not a stream\n{"broken": \n'})
    with pytest.raises(state.SetupError):
        probes.save_fixtures(run_dir, 'agent-tools', dest)
```

<!-- red:task4 test_probes.py -->

- [ ] **Step 2: Run the tests to verify they fail.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_probes.py`
Expected: a collection error, `ModuleNotFoundError: No module named 'probes'`.

- [ ] **Step 3: Give Gate B a binary override and a stream directory (R10.2), and R10.4's flags.**

**Replace** in `hooks/probe-readonly-guard.sh`:

```bash
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
```

**with:**

```bash
#  4. Each check loads user settings only, where the guard is installed, with
#     the permission mode pinned, a bounded turn count and spend, and no saved
#     session, so a run from inside this repo never fires its session-start
#     hook (drift spec R10.4).
#
# Run from inside any git repo, after installing the hook:
#   hooks/probe-readonly-guard.sh
# CLAUDE_BIN names the binary to probe (default: claude on PATH). When
# PROBE_STREAM_DIR is set, each check's raw stream is kept there as <n>.jsonl,
# which build/cc_guide/cli.py probes reads (drift spec R10.2).
set -uo pipefail

CLAUDE_BIN=${CLAUDE_BIN:-claude}

MARKER='readonly-agent-guard:'
STREAM=$(mktemp -t readonly-guard-probe.XXXXXX)
trap 'rm -f "$STREAM"' EXIT
fail=0

probe() {  # probe <n> <prompt> -> writes the raw event stream to $STREAM, kept as <n>.jsonl
  "$CLAUDE_BIN" "$2" -p --agent Explore --allowedTools "Bash" \
    --setting-sources user --settings '{"permissions":{"defaultMode":"default"}}' \
    --max-turns 4 --max-budget-usd 0.50 --no-session-persistence \
    --output-format stream-json --verbose < /dev/null > "$STREAM" 2>&1
  if [ -n "${PROBE_STREAM_DIR:-}" ]; then
    mkdir -p "$PROBE_STREAM_DIR" && cp "$STREAM" "$PROBE_STREAM_DIR/$1.jsonl"
  fi
}

echo "Claude Code: $("$CLAUDE_BIN" --version)"
```

**Replace** in `hooks/probe-readonly-guard.sh`:

```bash
probe 'Run exactly this command and report its output: git status --porcelain'
```

**with:**

```bash
probe 1 'Run exactly this command and report its output: git status --porcelain'
```

**Replace** in `hooks/probe-readonly-guard.sh`:

```bash
probe 'Run exactly this command and report its output: git fetch --dry-run origin'
```

**with:**

```bash
probe 2 'Run exactly this command and report its output: git fetch --dry-run origin'
```

**Replace** in `hooks/probe-readonly-guard.sh`:

```bash
probe 'Run exactly this command and report its output: git config --global --list'
```

**with:**

```bash
probe 3 'Run exactly this command and report its output: git config --global --list'
```

The `mktemp` template gains `.XXXXXX` because GNU `mktemp` refuses a template without X's, and Step 6's test runs the real script; macOS `mktemp -t` accepts both forms.

Run: `bash -n hooks/probe-readonly-guard.sh`
Expected: no output.

- [ ] **Step 4: Write the implementation.**

**Create** `build/cc_guide/probes.py`:

```python
# cc-guide: subagents.frontmatter subagents.isolation hooks.configuration @2.1.304
'''`probes` and `binaries` (drift spec R10.3-R10.7). `probes` runs the
registered probes that are due, the ones --only names, or every one with
--force, against the binary --claude names. Each run starts in a fresh
temporary directory outside every repo, loads only the setting sources the
probe needs, and keeps its raw output under the cache's probes/. Its
outcome comes from probe_checks.py and goes into one row of PROBES.md in the
working tree, which nothing commits. `binaries` lists the candidate
binaries with their versions.'''
import contextlib
import getpass
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Callable, NamedTuple

import probe_checks
from check import due_probes
from docs import version_key
from probe_checks import Verdict
from state import ERROR, MANIFEST, PASS, PROBES, SetupError, Source, is_probe_header, parse_manifest, parse_probes

VERSION_RE = re.compile(r'(\d+(?:\.\d+)+) \(Claude Code\)')
VERSION_TIMEOUT = 30  # seconds for `claude --version`
PROBE_TIMEOUT = 600  # seconds for one probe invocation
PINS_TIMEOUT = 1200  # agent-model-pins waits on three background agents
# claude -p stops background agents 10 minutes after the main turn unless this
# says otherwise. 15 minutes is above PROBE_TIMEOUT and below PINS_TIMEOUT, so
# claude ends its own wait before the harness stops it (plan 58, decision D4).
PINS_CEILING_MS = 900_000
KILL_GRACE = 5  # seconds between SIGTERM and SIGKILL when a run is stopped, and for each reap after
# SystemExit while probes run (term_as_exit). SIGHUP and SIGQUIT are POSIX-only, and cli.py imports this
# module for every subcommand, so a platform without them still imports it.
EXIT_SIGNALS = tuple(getattr(signal, name) for name in ('SIGTERM', 'SIGHUP', 'SIGQUIT') if hasattr(signal, name))
HELD_SIGNALS = (signal.SIGINT, *EXIT_SIGNALS)  # held while a run starts or is stopped (held_signals)
# A setup or output problem inside a probe: an ERROR row, never a crash (R10.5).
PROBE_FAILURES = (OSError, subprocess.SubprocessError, ValueError, TypeError, KeyError, AttributeError)
BUDGET_USD = '0.50'  # --max-budget-usd for one probe invocation
PINS_BUDGET_USD = '0.75'  # three agents, one of them Opus at xhigh
TOOLS_TURNS, STOP_TURNS, PINS_TURNS = 1, 6, 8
GUARD_SCRIPT = 'hooks/probe-readonly-guard.sh'
GUARD_STREAMS = 3
DESKTOP_BUNDLES = Path('Library/Application Support/Claude/claude-code')
DESKTOP_GLOB = '*/*/claude.app/Contents/MacOS/claude'
DESKTOP_NOTE = 'Desktop app bundle (observed layout, not documented)'
LOG_TEXT = '\n'.join([
    '# Probe log', '',
    'One row per probe run, appended by `cli.py probes` (drift spec R10.6), newest last.',
    'Nothing commits it for you: review the rows, then commit them. Each run keeps its raw',
    'output under `~/.cache/agent-skills/cc-guide/probes/`.', '',
    '| Date | Version | Binary | Probe | Outcome | Finding | Flags |',
    '|---|---|---|---|---|---|---|', ''])


class Invocation(NamedTuple):
    name: str             # its stdout goes to <name><suffix>, its stderr to <name>.err
    argv: list[str]
    env: dict[str, str]   # added to the caller's environment
    timeout: int          # seconds
    suffix: str = '.jsonl'


# Runs one invocation from a directory, writing its stdout and stderr to the
# two paths; returns its exit code, or None when it timed out.
Execute = Callable[[Invocation, Path, Path, Path], int | None]
# Reads a run directory's file by name: its text, or None when absent.
Read = Callable[[str], str | None]


def execute(inv: Invocation, cwd: Path, out: Path, err: Path) -> int | None:
    '''R10.4: the prompt goes first and stdin is /dev/null, since claude -p
    waits on a piped stdin. The run gets its own process group, so a timeout
    or a stop ends everything it started, such as the claude under Gate B's
    bash: the group gets no terminal signal of its own. A stop signal while
    the run starts is held until `proc` is bound, so it cannot orphan it.'''
    with out.open('wb') as stdout, err.open('wb') as stderr:
        proc = None
        try:
            with held_signals():
                proc = subprocess.Popen(inv.argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                        env={**os.environ, **inv.env}, start_new_session=True)
            return proc.wait(timeout=inv.timeout)
        except subprocess.TimeoutExpired:
            stop_group(proc)
            return None
        except BaseException:  # Ctrl-C, or term_as_exit's SystemExit
            if proc is not None:
                stop_group(proc)
            raise


def stop_group(proc: subprocess.Popen) -> None:
    '''SIGTERM to a run's process group, which lets a script's EXIT trap
    run, then SIGKILL to whatever is left after KILL_GRACE. Stop signals are
    held meanwhile, so a second Ctrl-C cannot skip the SIGKILL. macOS answers
    EPERM for a group whose members have all exited but are not reaped. The
    reaps are bounded, since an interrupted wait can leave Popen's lock held.'''
    with held_signals():
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGTERM)
        with contextlib.suppress(subprocess.TimeoutExpired):
            proc.wait(timeout=KILL_GRACE)
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)
        with contextlib.suppress(subprocess.TimeoutExpired):
            proc.wait(timeout=KILL_GRACE)


@contextlib.contextmanager
def held_signals():
    '''Record the stop signals instead of acting on them, then act on the
    first once the block is done, through the handler in force before it.
    Starting a run and stopping one must not be cut short. Main thread only,
    as signal.signal requires.'''
    got: list[int] = []
    previous = {s: signal.signal(s, lambda signum, frame: got.append(signum)) for s in HELD_SIGNALS}
    try:
        yield
    finally:
        for s, handler in previous.items():
            signal.signal(s, handler)
        if got:
            signal.raise_signal(got[0])


@contextlib.contextmanager
def term_as_exit():
    '''While probes run, SIGTERM (a stopped tool), SIGHUP (a closed
    terminal) and SIGQUIT raise SystemExit, so a stopped run still ends its
    probe's process group and removes its scratch directory: by default each
    ends Python with no except or finally. A signal already ignored, as
    nohup ignores SIGHUP, stays ignored.'''
    exits = [s for s in EXIT_SIGNALS if signal.getsignal(s) is not signal.SIG_IGN]
    previous = {s: signal.signal(s, lambda signum, frame: sys.exit(128 + signum)) for s in exits}
    try:
        yield
    finally:
        for s, handler in previous.items():
            signal.signal(s, handler)


def claude_args(claude: str, prompt: str, *, turns: int, sources: str, mode: str, allow: tuple[str, ...] = (),
                budget: str = BUDGET_USD, persist: bool = False, extra: tuple[str, ...] = ()) -> list[str]:
    '''R10.4's command line: the prompt first, raw stream-json events, only
    the setting sources the probe needs, its permission mode pinned and its
    tools pre-allowed through --settings, Sonnet at low effort, and a bounded
    turn count and spend. Sessions are not persisted unless the probe reads
    its transcript.'''
    permissions = {'defaultMode': mode, **({'allow': list(allow)} if allow else {})}
    argv = [claude, prompt, '-p', '--output-format', 'stream-json', '--verbose',
            '--setting-sources', sources, '--settings', json.dumps({'permissions': permissions}),
            '--model', 'sonnet', '--effort', 'low', '--max-turns', str(turns), '--max-budget-usd', budget, *extra]
    return argv if persist else [*argv, '--no-session-persistence']


def stream_of(text: str | None) -> list[dict] | None:
    return None if text is None else probe_checks.parse_stream(text)


def copy_if_there(source: Path, target: Path) -> None:
    if source.is_file():
        shutil.copy(source, target)


class Probe(NamedTuple):
    # (scratch directory, claude, repo) -> the invocations to run there
    prepare: Callable[[Path, str, Path], list[Invocation]]
    # (scratch directory, run directory): copy what the run left beside its streams
    collect: Callable[[Path, Path], None]
    # the verdict from the run directory's files, the same path R12.6's replay takes
    assess: Callable[[Read], Verdict]
    # run-directory file -> the fixture file it is scrubbed into (R12.6)
    fixtures: dict[str, str]


def prepare_guard(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''guard-liveness wraps hooks/probe-readonly-guard.sh in a scratch git
    repo, with user settings, since the guard is installed globally.'''
    subprocess.run(['git', 'init', '-q'], cwd=scratch, check=True, capture_output=True)
    env = {'CLAUDE_BIN': claude, 'PROBE_STREAM_DIR': str(scratch / 'streams')}
    return [Invocation('guard', ['bash', str(repo / GUARD_SCRIPT)], env, PROBE_TIMEOUT, '.txt')]


def collect_guard(scratch: Path, run_dir: Path) -> None:
    for n in range(1, GUARD_STREAMS + 1):
        copy_if_there(scratch / 'streams' / f'{n}.jsonl', run_dir / f'guard-{n}.jsonl')


def assess_guard(read: Read) -> Verdict:
    return probe_checks.assess_guard_liveness([stream_of(read(f'guard-{n}.jsonl'))
                                               for n in range(1, GUARD_STREAMS + 1)])


TOOLS_AGENTS = {'probe-with-bash': 'Read, Grep, Glob, Bash', 'probe-without-bash': 'Read, Grep, Glob'}
TOOLS_AGENT_FILE = ('---\nname: {name}\ndescription: A drift probe agent.\ntools: {tools}\nomitClaudeMd: true\n'
                    '---\n\nReply with the word OK and nothing else.\n')


def prepare_agent_tools(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''agent-tools runs a scratch agent that lists Bash and a control that
    does not, each through --agent, from the scratch directory's project
    agents.'''
    agents = scratch / '.claude' / 'agents'
    agents.mkdir(parents=True)
    for name, tools in TOOLS_AGENTS.items():
        (agents / f'{name}.md').write_text(TOOLS_AGENT_FILE.format(name=name, tools=tools), encoding='utf-8')
    return [Invocation(name, claude_args(claude, 'Reply with the word OK.', turns=TOOLS_TURNS, sources='project',
                                         mode='default', extra=('--agent', name)), {}, PROBE_TIMEOUT)
            for name in TOOLS_AGENTS]


def collect_nothing(scratch: Path, run_dir: Path) -> None:
    '''agent-tools leaves nothing but its streams.'''


def assess_agent_tools(read: Read) -> Verdict:
    return probe_checks.assess_agent_tools(stream_of(read('probe-with-bash.jsonl')),
                                           stream_of(read('probe-without-bash.jsonl')), sys.platform)


# The Stop hook logs stop_hook_active and blocks on its first two calls. @LOG@
# is replaced by the quoted path of its log.
STOP_HOOK = r'''#!/usr/bin/env bash
input=$(cat)
v=$(printf '%s' "$input" | grep -o '"stop_hook_active"[[:space:]]*:[[:space:]]*\(true\|false\)' | grep -o 'true\|false')
echo "${v:-missing}" >> @LOG@
n=$(wc -l < @LOG@)
if [ "$n" -le 2 ]; then echo 'Reply with the word OK once more.' >&2; exit 2; fi
exit 0
'''


def prepare_stop(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''stop-continuation registers its Stop hook in the scratch directory's
    project settings, which plan 58's planning spike proved load (R10.2),
    and asks for hook events in the stream.'''
    hook = scratch / 'stop-hook.sh'
    hook.write_text(STOP_HOOK.replace('@LOG@', shlex.quote(str(scratch / 'stop.log'))), encoding='utf-8')
    hook.chmod(0o755)
    settings = {'hooks': {'Stop': [{'hooks': [{'type': 'command', 'command': shlex.quote(str(hook))}]}]}}
    (scratch / '.claude').mkdir()
    (scratch / '.claude' / 'settings.json').write_text(json.dumps(settings, indent=1) + '\n', encoding='utf-8')
    return [Invocation('stop', claude_args(claude, 'Reply with the word OK.', turns=STOP_TURNS, sources='project',
                                           mode='default', extra=('--include-hook-events',)), {}, PROBE_TIMEOUT)]


def collect_stop(scratch: Path, run_dir: Path) -> None:
    copy_if_there(scratch / 'stop.log', run_dir / 'stop.log')


def assess_stop(read: Read) -> Verdict:
    return probe_checks.assess_stop_continuation(stream_of(read('stop.jsonl')), (read('stop.log') or '').split())


PINS_PROMPT = ('In one message, call the Agent tool three times: (1) subagent_type "Explore" with prompt '
               '"List the file names in {dir}. Reply with the names only."; (2) subagent_type "test-runner" with '
               'prompt "Working directory: {dir}. Run exactly this command: true. Report its exit code in one '
               'line."; (3) subagent_type "code-reviewer" with prompt "Review {dir}/a.py against this one '
               'requirement: it prints hello. Reply in one sentence.". Wait for all three results, then reply '
               'with the word DONE.')


def prepare_pins(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''agent-model-pins takes the production path: an auto-mode parent with
    user settings dispatches the three pinned agents with the Agent tool, in
    fork mode's background, with the background ceiling raised (owner, plan
    58 decision D4). The session is persisted, since effort is read from the
    subagents' transcripts (R10.4, as plan 58 amends it).'''
    (scratch / 'a.py').write_text("print('hello')\n", encoding='utf-8')
    argv = claude_args(claude, PINS_PROMPT.format(dir=scratch), turns=PINS_TURNS, sources='user', mode='auto',
                       allow=('Agent',), budget=PINS_BUDGET_USD, persist=True, extra=('--forward-subagent-text',))
    return [Invocation('pins', argv, {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': str(PINS_CEILING_MS)}, PINS_TIMEOUT)]


def read_transcripts(projects: Path, session: str | None) -> dict[str, list[dict]]:
    '''Each subagent's transcript lines, agent type -> [{'model', 'effort'}],
    from <projects>/<project>/<session>/subagents/: each agent-*.meta.json
    names its agent type, and the agent-*.jsonl beside it holds its lines.'''
    found: dict[str, list[dict]] = {}
    if not session:
        return found
    for meta in sorted(projects.glob(f'*/{session}/subagents/agent-*.meta.json')):
        kind = json.loads(meta.read_text(encoding='utf-8')).get('agentType')
        lines = meta.with_name(meta.name.removesuffix('.meta.json') + '.jsonl')
        if not lines.is_file():
            continue
        for line in filter(str.strip, lines.read_text(encoding='utf-8').split('\n')):
            entry = json.loads(line)
            if entry.get('type') == 'assistant':
                found.setdefault(kind, []).append({'model': (entry.get('message') or {}).get('model'),
                                                   'effort': entry.get('effort')})
    return found


def collect_pins(scratch: Path, run_dir: Path) -> None:
    '''The persisted transcripts of the stream's session, kept as transcripts.json.'''
    path = run_dir / 'pins.jsonl'
    events = stream_of(path.read_text(encoding='utf-8')) if path.is_file() else None
    session = next((e.get('session_id') for e in events or [] if probe_checks.is_init(e)), None)
    transcripts = read_transcripts(Path.home() / '.claude' / 'projects', session)
    (run_dir / 'transcripts.json').write_text(json.dumps(transcripts, indent=1) + '\n', encoding='utf-8')


def assess_pins(read: Read) -> Verdict:
    return probe_checks.assess_agent_model_pins(stream_of(read('pins.jsonl')),
                                                json.loads(read('transcripts.json') or '{}'))


PROBE_RUNS = {
    'guard-liveness': Probe(prepare_guard, collect_guard, assess_guard,
                            {f'guard-{n}.jsonl': f'guard-liveness.{n}.jsonl' for n in range(1, GUARD_STREAMS + 1)}),
    'agent-tools': Probe(prepare_agent_tools, collect_nothing, assess_agent_tools,
                         {'probe-with-bash.jsonl': 'agent-tools.with-bash.jsonl',
                          'probe-without-bash.jsonl': 'agent-tools.without-bash.jsonl'}),
    'stop-continuation': Probe(prepare_stop, collect_stop, assess_stop,
                               {'stop.jsonl': 'stop-continuation.jsonl', 'stop.log': 'stop-continuation.log'}),
    'agent-model-pins': Probe(prepare_pins, collect_pins, assess_pins,
                              {'pins.jsonl': 'agent-model-pins.jsonl',
                               'transcripts.json': 'agent-model-pins.transcripts.json'}),
}


def reader(folder: Path, names: dict[str, str] | None = None) -> Read:
    '''Reads a run directory, or with `names` a fixture directory under
    each run-directory name's fixture name.'''
    def read(name: str) -> str | None:
        path = folder / (names[name] if names else name)
        return path.read_text(encoding='utf-8') if path.is_file() else None
    return read


def save_fixtures(run_dir: Path, pid: str, dest: Path) -> list[Path]:
    '''R12.6: turn one recorded run into the fixtures its replay test reads,
    each stream cut down and scrubbed of the home directory, the temporary
    directory and the login name (owner, plan 58 decision D3).'''
    private = [str(Path.home()), str(Path.home().resolve()), tempfile.gettempdir(),
               os.path.realpath(tempfile.gettempdir()), getpass.getuser()]
    written = []
    for name, fixture in PROBE_RUNS[pid].fixtures.items():
        text = (run_dir / name).read_text(encoding='utf-8')
        if name.endswith('.jsonl'):
            events = probe_checks.parse_stream(text)
            if events is None:
                raise SetupError(f'{run_dir / name}: not a stream-json file')
            text = probe_checks.scrub_events(events, private)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / fixture).write_text(text, encoding='utf-8')
        written.append(dest / fixture)
    return written


def inside_a_repo(path: Path) -> bool:
    proc = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], cwd=path, capture_output=True, text=True)
    return proc.returncode == 0 and proc.stdout.strip() == 'true'


def run_probe(pid: str, claude: str, repo: Path, run_dir: Path, execute: Execute = execute) -> Verdict:
    '''One probe, from a fresh temporary directory that is removed after the
    verdict; its raw output stays in run_dir. A setup failure, a timeout or
    unreadable output is ERROR, never a pass.'''
    probe = PROBE_RUNS[pid]
    run_dir.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=f'cc-guide-probe-{pid}-')).resolve()
    try:
        if inside_a_repo(scratch):
            return Verdict(ERROR, f'the temporary directory {scratch} is inside a git work tree')
        for inv in probe.prepare(scratch, claude, repo):
            (run_dir / f'{inv.name}.argv.json').write_text(json.dumps(inv.argv, indent=1) + '\n', encoding='utf-8')
            if execute(inv, scratch, run_dir / f'{inv.name}{inv.suffix}', run_dir / f'{inv.name}.err') is None:
                return Verdict(ERROR, f'{inv.name} timed out after {inv.timeout} s')
        probe.collect(scratch, run_dir)
        return probe.assess(reader(run_dir))
    except PROBE_FAILURES as exc:
        return Verdict(ERROR, f'{type(exc).__name__}: {exc}')
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def binary_version(claude: Path) -> str:
    '''The release label `claude --version` prints, or a SetupError.'''
    try:
        proc = subprocess.run([str(claude), '--version'], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                              timeout=VERSION_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as exc:
        raise SetupError(f'{claude} --version: {exc}') from None
    found = VERSION_RE.search(proc.stdout)
    if proc.returncode != 0 or found is None:
        raise SetupError(f'{claude} --version printed no Claude Code version')
    return found.group(1)


def shown_path(path: Path) -> str:
    '''A path as the log shows it, with ~ for the home directory (R10.6).'''
    home, text = str(Path.home()), str(path)
    return '~' + text[len(home):] if text == home or text.startswith(home + os.sep) else text


def cell(text: str) -> str:
    '''Text as one table cell: whitespace collapsed, pipes escaped.'''
    return ' '.join(text.split()).replace('|', '\\|')


def log_row(day: date, version: str, claude: Path, pid: str, verdict: Verdict, allow_old: bool) -> str:
    cells = [day.isoformat(), version, shown_path(claude), pid, verdict.outcome, verdict.finding,
             '--allow-old' if allow_old else '']
    return '| ' + ' | '.join(map(cell, cells)) + ' |'


def append_row(path: Path, row: str) -> None:
    '''Append a row to PROBES.md's log table, creating the file when absent.
    The row goes right after the table's last row, so text below the table
    never splits it from its header. The new log replaces the old one whole,
    so a stop mid-write never leaves the log cut short, and the folder lock
    keeps a second run's row from being lost.'''
    with locked(path.parent):
        lines = (path.read_text(encoding='utf-8') if path.is_file() else LOG_TEXT).split('\n')
        start = next((i for i, line in enumerate(lines) if is_probe_header(line)), None)
        if start is None:
            raise SetupError(f'{PROBES}: no log table naming the date, version, probe and outcome columns')
        end = start
        while end + 1 < len(lines) and lines[end + 1].strip().startswith('|'):
            end += 1
        lines.insert(end + 1, row)
        draft = path.with_name(f'.{path.name}.new')
        try:
            draft.write_text('\n'.join(lines), encoding='utf-8')
            os.replace(draft, path)
        finally:
            draft.unlink(missing_ok=True)


@contextlib.contextmanager
def locked(folder: Path):
    '''An exclusive lock on a folder, so two probes runs in one working tree
    append to its log one at a time; flock takes a folder's descriptor on
    macOS and Linux, and leaves no lock file behind. fcntl is POSIX-only,
    so it is imported here, where only a probes run reaches it.'''
    import fcntl
    fd = os.open(folder, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def run(repo: Path, cache: Path, claude: Path, *, only: list[str] | None, force: bool, allow_old: bool,
        newest: str, today: date, now: datetime, execute: Execute = execute,
        version_of: Callable[[Path], str] = binary_version) -> tuple[int, list[str]]:
    '''R10.6: run the chosen probes and append a row for each; (exit code,
    lines to print). Exit 0 when every probe passed or none was due, 1 when
    any DIVERGES or is ERROR. A setup problem raises SetupError (exit 2):
    an unknown probe, an unusable binary, or one older than `newest`, the
    newest cached changelog release, without --allow-old (R10.3).'''
    tree = Source(repo)
    manifest = parse_manifest(tree.require(MANIFEST))
    rows = parse_probes(tree.read(PROBES))
    unbuilt = sorted(set(manifest.probes) - set(PROBE_RUNS))
    if unbuilt:
        raise SetupError(f"{MANIFEST} registers {', '.join(unbuilt)}, which probes.py does not run")
    unknown = sorted(set(only or []) - set(manifest.probes))
    if unknown:
        raise SetupError(f"--only {', '.join(unknown)}: not a registered probe")
    if not (claude.is_file() and os.access(claude, os.X_OK)):
        raise SetupError(f'--claude {claude}: not an executable file')
    version = version_of(claude)
    if version_key(version) < version_key(newest) and not allow_old:
        raise SetupError(f'--claude {claude} is {version}, older than the newest changelog release {newest}: '
                         'pass --allow-old to run it anyway, and each row records the flag (R10.3)')
    chosen = only or (list(manifest.probes) if force else
                      [d['probe'] for d in due_probes(manifest, rows, newest, manifest.cadence['probe_days'], today)])
    if not chosen:
        return 0, ['probes: none due']
    lines, outcomes = [f'probes: {version} at {shown_path(claude)}'], []
    with term_as_exit():
        for pid in dict.fromkeys(chosen):
            run_dir = cache / 'probes' / f"{now.strftime('%Y%m%dT%H%M%S')}-{pid}"
            verdict = run_probe(pid, str(claude), repo, run_dir, execute)
            append_row(repo / PROBES, log_row(today, version, claude, pid, verdict, allow_old))
            outcomes.append(verdict.outcome)
            lines += [f'{pid}: {verdict.outcome}: {verdict.finding}', f'  raw output: {run_dir}']
    lines.append(f'appended {len(outcomes)} row(s) to {PROBES}; nothing is committed')
    return (0 if all(o == PASS for o in outcomes) else 1), lines


class Candidate(NamedTuple):
    path: Path
    target: Path
    version: str | None
    where: str


def binaries(path_env: str, home: Path, version_of: Callable[[Path], str] = binary_version) -> list[Candidate]:
    '''R10.3: each claude on PATH with its symlink target, then the Desktop
    app's bundled binaries, labelled as an observed layout.'''
    def version(path: Path) -> str | None:
        try:
            return version_of(path)
        except SetupError:
            return None
    found: list[Candidate] = []
    for folder in dict.fromkeys(filter(None, path_env.split(os.pathsep))):
        exe = Path(folder) / 'claude'
        if exe.is_file() and os.access(exe, os.X_OK):
            found.append(Candidate(exe, exe.resolve(), version(exe), 'PATH'))
    for exe in sorted((home / DESKTOP_BUNDLES).glob(DESKTOP_GLOB)):
        found.append(Candidate(exe, exe.resolve(), version(exe), DESKTOP_NOTE))
    return found


def describe(c: Candidate) -> str:
    target = '' if c.target == c.path else f' -> {shown_path(c.target)}'
    return f"{c.version or 'version unknown'}  {shown_path(c.path)}{target}  ({c.where})"
```

- [ ] **Step 5: Stamp the citation.**

Run: `git add build/cc_guide/probes.py build/cc_guide/test_probes.py hooks/probe-readonly-guard.sh`

Run: `uv run --python 3.13 python build/cc_guide/cli.py baseline cite build/cc_guide/probes.py`
Expected: `stamped build/cc_guide/probes.py @<release>`.

- [ ] **Step 6: Run the tests to verify they pass.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +31 against Task 3. `test_the_guard_probe_runs_the_real_script_and_reads_its_three_kept_streams` runs the real `hooks/probe-readonly-guard.sh` against a fake `claude`, so it checks Step 3's flags and stream copies. The process tests take a few seconds, and their `pids` fixture kills any `sleep` a failing one leaves.

- [ ] **Step 7: Run the gates and commit.**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`.

```bash
git add build/cc_guide/probes.py build/cc_guide/test_probes.py hooks/probe-readonly-guard.sh
git commit -m "feat(cc_guide): add the probe runner and Gate B's stream directory (drift R10.2-R10.6)"
```

---

### Task 5: `cli.py probes` and `cli.py binaries`, and the registry (R10.1, R10.3)

**Files:**
- Modify: `build/cc_guide/cli.py` (docstring, imports, `parser`, two run functions, `main`)
- Modify: `build/cc_guide/manifest.toml` (the `[[probe]]` registry)
- Test: `build/cc_guide/test_cli.py`

**Interfaces:**
- Consumes: Task 4's `probes.run`, `probes.binaries`, `probes.describe` and `probes.PROBE_RUNS`; `cli.newest_releases(cache)`, which raises `SetupError('no cached changelog: run check, or restore the 2.1.288 snapshot')`.
- Produces: `cli.py probes --claude PATH [--only ID [ID ...] | --force] [--allow-old]` and `cli.py binaries`.

- [ ] **Step 1: Write the failing tests.**

**Replace** in `build/cc_guide/test_cli.py`:

```python
import notice
import state
```

**with:**

```python
import notice
import probes
import state
```

**Replace** in `build/cc_guide/test_cli.py`:

```python
    assert capsys.readouterr() == ('', 'cc-guide: a substantive accept needs every citation to parse (R2.4);'
                                       f' fix these first:\n{malformed}')
    assert dirty(repo) == [GUIDE_PATH]
```

**with:**

```python
    assert capsys.readouterr() == ('', 'cc-guide: a substantive accept needs every citation to parse (R2.4);'
                                       f' fix these first:\n{malformed}')
    assert dirty(repo) == [GUIDE_PATH]


def test_probes_passes_the_newest_cached_release_and_its_flags(world, monkeypatch, capsys):
    repo, cache, _ = world
    seen = {}

    def fake_run(root, cache_dir, claude, **given):
        seen.update(root=root, cache=cache_dir, claude=claude, **given)
        return 1, ['agent-tools: ERROR: no init event']
    monkeypatch.setattr(probes, 'run', fake_run)
    assert main(cache, 'probes', '--claude', 'bin/claude', '--only', 'agent-tools', '--allow-old') == 1
    assert (seen['root'], seen['cache'], seen['claude'], seen['newest']) == (
        repo, cache, Path.cwd() / 'bin' / 'claude', '2.1.902')
    assert (seen['only'], seen['force'], seen['allow_old']) == (['agent-tools'], False, True)
    assert capsys.readouterr().out == 'agent-tools: ERROR: no init event\n'


@pytest.mark.parametrize('argv', [['probes'], ['probes', '--claude', 'c', '--only', 'a', '--force']])
def test_probes_needs_claude_and_takes_only_or_force_not_both(world, argv, capsys):
    with pytest.raises(SystemExit) as exit_:
        main(world[1], *argv)
    assert exit_.value.code == 2


def test_probes_without_a_cached_changelog_is_a_setup_error(tmp_path, capsys):
    assert main(tmp_path / 'empty-cache', 'probes', '--claude', 'c') == 2
    assert capsys.readouterr().err == 'cc-guide: no cached changelog: run check, or restore the 2.1.288 snapshot\n'


def test_binaries_exits_two_when_no_claude_is_found(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv('PATH', str(tmp_path))
    assert main(tmp_path / 'cache', 'binaries') == 2
    assert capsys.readouterr().err == 'cc-guide: no claude binary on PATH or in the Desktop app bundle\n'


def test_the_registry_names_exactly_the_probes_that_probes_py_runs():
    '''R10.1: manifest.toml registers each probe, and probes.py runs it. One
    registered on either side alone fails here, before a live run finds it.'''
    manifest = state.parse_manifest((cli.REPO / state.MANIFEST).read_text(encoding='utf-8'))
    assert sorted(manifest.probes) == sorted(probes.PROBE_RUNS)
```

<!-- red:task5 test_cli.py -->

- [ ] **Step 2: Run the tests to verify they fail.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_cli.py`
Expected: 4 failed. `probes` and `binaries` are unknown subcommands, so argparse exits 2 where three tests expect a return value, and the registry test finds no `[[probe]]` in `manifest.toml`. The two `test_probes_needs_claude_and_takes_only_or_force_not_both` cases pass before and after, since argparse also exits 2 on an unknown subcommand: they guard the flag rules once the subcommand exists.

- [ ] **Step 3: Write the implementation in `cli.py`.**

**Replace** in `build/cc_guide/cli.py`:

```python
the citations that point at it, and the deterministic half of /cc-guide
(Stages 1 to 4 of specs/claude-code-drift-automation-spec.md).
```

**with:**

```python
the citations that point at it, the deterministic half of /cc-guide, and
the live probes (Stages 1 to 5 of specs/claude-code-drift-automation-spec.md).
```

**Replace** in `build/cc_guide/cli.py`:

```python
      was found, with nothing discarded or left out; 1 otherwise; 2 on an
      error.

After reviewing what check reported, record it in R8.8's order: accept,
```

**with:**

```python
      was found, with nothing discarded or left out; 1 otherwise; 2 on an
      error.
  probes --claude PATH [--only ID [ID ...] | --force] [--allow-old]
      Run the registered probes that are due (R6.7), or those --only names, or
      every one with --force, against the binary PATH names, and append one
      row each to build/cc_guide/PROBES.md, uncommitted (R10). Each probe runs
      from a fresh temporary directory outside every repo and keeps its raw
      output under the cache's probes/. A binary older than the newest cached
      changelog release is refused unless --allow-old is given, which each row
      records. Live runs spend about $0.05-0.30 a probe. Exit 0 when every
      probe passed or none was due, 1 when any DIVERGES or is ERROR, 2 on a
      setup error.
  binaries
      List each claude on PATH with its symlink target and version, then the
      Desktop app's bundled binaries, an observed layout the docs do not
      document (R10.3). Exit 0, or 2 when none is found.

After reviewing what check reported, record it in R8.8's order: accept,
```

**Replace** in `build/cc_guide/cli.py`:

```python
import argparse
import subprocess
```

**with:**

```python
import argparse
import os
import subprocess
```

**Replace** in `build/cc_guide/cli.py`:

```python
import packets
from check import
```

**with:**

```python
import packets
import probes
from check import
```

**Replace** in `build/cc_guide/cli.py`:

```python
    s.add_argument('--hold', nargs='+', default=[], metavar='ID')
    return p
```

**with:**

```python
    s.add_argument('--hold', nargs='+', default=[], metavar='ID')
    pr = sub.add_parser('probes')
    pr.add_argument('--claude', type=Path, required=True, metavar='PATH')
    which = pr.add_mutually_exclusive_group()
    which.add_argument('--only', nargs='+', metavar='ID')
    which.add_argument('--force', action='store_true')
    pr.add_argument('--allow-old', action='store_true')
    sub.add_parser('binaries')
    return p
```

**Replace** in `build/cc_guide/cli.py`:

```python
    return 0 if result.clean else 1


def main(
```

**with:**

```python
    return 0 if result.clean else 1


def run_probes(args, cache: Path, today: date, now: datetime) -> int:
    code, lines = probes.run(REPO, cache, args.claude.expanduser().absolute(), only=args.only, force=args.force,
                             allow_old=args.allow_old, newest=newest_releases(cache)[0].label, today=today, now=now)
    print('\n'.join(lines))
    return code


def run_binaries() -> int:
    found = probes.binaries(os.environ.get('PATH', ''), Path.home())
    if not found:
        raise SetupError('no claude binary on PATH or in the Desktop app bundle')
    print('\n'.join(map(probes.describe, found)))
    return 0


def main(
```

**Replace** in `build/cc_guide/cli.py`:

```python
        if args.command == 'settle':
            return run_settle(args)
        return run_baseline(args, cache, today)
```

**with:**

```python
        if args.command == 'settle':
            return run_settle(args)
        if args.command == 'probes':
            return run_probes(args, cache, today, now)
        if args.command == 'binaries':
            return run_binaries()
        return run_baseline(args, cache, today)
```

- [ ] **Step 4: Register the four probes (R10.1, D1).**

**Replace** in `build/cc_guide/manifest.toml`:

```toml
# The probe registry (R10.1) stays empty until Stage 5 registers its probes
# as [[probe]] entries with an id, the sections they back, and optional files.
```

**with:**

```toml
# The probe registry (R10.1): each probe's id, the guide sections it backs, and
# the files that rest on what it observes. A DIVERGES row sends both to
# /cc-guide verify and files (R10.5). build/cc_guide/probes.py runs each one.

[[probe]]
id = 'guard-liveness'
# The sections hooks/readonly-agent-guard.py cites (owner, plan 58 decision D1, 2026-10-20).
sections = ['hooks.events', 'hooks.exit-codes', 'hooks.patterns']
files = ['hooks/readonly-agent-guard.py', 'hooks/README.md']

[[probe]]
id = 'agent-tools'
sections = ['subagents.tools']

[[probe]]
id = 'stop-continuation'
sections = ['hooks.exit-codes', 'hooks.patterns']

[[probe]]
id = 'agent-model-pins'
sections = ['subagents.frontmatter', 'subagents.models']
files = ['agents/explore.md', 'agents/test-runner.md', 'agents/code-reviewer.md']
```

- [ ] **Step 5: Run the tests to verify they pass.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +6 against Task 4.

Run: `uv run --python 3.13 python build/cc_guide/cli.py binaries`
Expected: exit 0, one line per binary, the PATH `claude` first with `-> <its target>` and `(PATH)`. This reads only `--version` from each binary.

- [ ] **Step 6: Run the gates and commit.**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`.

```bash
git add build/cc_guide/cli.py build/cc_guide/test_cli.py build/cc_guide/manifest.toml
git commit -m "feat(cc_guide): add the probes and binaries subcommands and register four probes (drift R10.1, R10.3)"
```

---

### Task 6: Record the probes and replay them (R12.6, Validation 5)

**Files:**
- Test: `build/cc_guide/test_probe_replay.py`
- Create (from the runs): `build/cc_guide/probe_streams/` (nine files, written only by `save_fixtures`), `build/cc_guide/PROBES.md` (written only by `cli.py probes`).
- Create (outside the repo): `~/.cache/agent-skills/scratch/plan58-bin/broken-claude`.

**Interfaces:**
- Consumes: Task 4's `PROBE_RUNS`, `reader`, `stream_of` and `save_fixtures`, and `probe_checks.dispatches`; Task 5's `cli.py probes`.

This task spends about $0.35 and makes the plan's only commits of recorded data. Run the live commands exactly as written: each one is the whole budget for its step. If a probe's live run comes back DIVERGES, stop and report it to your human partner with the row and the raw output folder: the behaviour the guide states has changed, which is a `/cc-guide` finding, not a fixture to save. If one comes back ERROR, read its raw output (`*.err` and the streams) and use the systematic-debugging skill before running it again with `--only <id>`.

- [ ] **Step 1: Write the failing test.**

**Create** `build/cc_guide/test_probe_replay.py`:

```python
'''R12.6: each probe's assertion replayed against the streams recorded from
our own probe runs, kept under probe_streams/ after save_fixtures cut them
down and scrubbed them. The recorded run passes; the same run with the
observed behaviour changed diverges; and a run whose mechanism never fired
is ERROR. No fixture may hold a path or an id from the machine it was
recorded on (owner, plan 58 decision D3).'''
import json
import re
from pathlib import Path

import pytest

import probes
from cc_fixtures import isolated_home  # noqa: F401
from state import DIVERGES, ERROR, PASS

FIXTURES = Path(__file__).resolve().parent / 'probe_streams'
PRIVATE_RE = re.compile(r'/Users/|/home/|/private/|/var/folders/|/tmp/|toolu_0|mcp__|'
                        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def replay(pid: str, changes: dict[str, str] | None = None):
    '''The probe's verdict on its fixtures, with some fixture texts replaced.'''
    probe = probes.PROBE_RUNS[pid]
    read = probes.reader(FIXTURES, probe.fixtures)
    return probe.assess(lambda name: (changes or {}).get(name, read(name)))


def edited(pid: str, name: str, edit) -> dict[str, str]:
    '''A fixture stream with `edit` applied to each event.'''
    text = (FIXTURES / probes.PROBE_RUNS[pid].fixtures[name]).read_text(encoding='utf-8')
    return {name: ''.join(json.dumps(edit(json.loads(line))) + '\n' for line in text.split('\n') if line)}


def test_every_registered_probe_has_its_fixtures():
    for pid, probe in probes.PROBE_RUNS.items():
        for fixture in probe.fixtures.values():
            assert (FIXTURES / fixture).is_file(), f'{pid}: {fixture} is missing; record it with save_fixtures'


@pytest.mark.parametrize('pid', list(probes.PROBE_RUNS))
def test_the_recorded_run_passes(pid):
    assert replay(pid).outcome == PASS


def with_tools(*added):
    def edit(event):
        if event.get('subtype') == 'init':
            event['tools'] = sorted({*event['tools'], *added})
        return event
    return edit


def model_of(parent_model: dict[str, str]):
    def edit(event):
        if event.get('type') == 'assistant' and event.get('parent_tool_use_id') in parent_model:
            event['message']['model'] = parent_model[event['parent_tool_use_id']]
        return event
    return edit


def drop(kind: str):
    return lambda event: {} if event.get('subtype') == kind else event


def explore_ids() -> dict[str, str]:
    probe = probes.PROBE_RUNS['agent-model-pins']
    events = probes.stream_of(probes.reader(FIXTURES, probe.fixtures)('pins.jsonl'))
    return {tid: 'claude-sonnet-5-5' for tid, kind in probes.probe_checks.dispatches(events).items()
            if kind == 'Explore'}


def unmarked(event):
    for block in (event.get('message') or {}).get('content') or []:
        if block.get('type') == 'tool_result':
            block['content'] = '<output>'
    return event


# Each ERROR case names its finding, so a missing fixture, which is ERROR for
# another reason, cannot pass it.
@pytest.mark.parametrize('pid, changes, outcome, finding', [
    ('agent-tools', lambda: edited('agent-tools', 'probe-with-bash.jsonl', with_tools('Grep', 'Glob')), DIVERGES,
     None),
    ('agent-tools', lambda: edited('agent-tools', 'probe-without-bash.jsonl', drop('init')), ERROR,
     'the agent without Bash: no init event'),
    ('stop-continuation', lambda: {'stop.log': 'false\nfalse\ntrue\n'}, DIVERGES, None),
    ('stop-continuation', lambda: {'stop.log': ''}, ERROR, 'the Stop hook never logged a call'),
    ('agent-model-pins', lambda: edited('agent-model-pins', 'pins.jsonl', model_of(explore_ids())), DIVERGES, None),
    ('agent-model-pins', lambda: {'transcripts.json': '{}'}, ERROR, 'no transcript lines for Explore'),
    ('guard-liveness', lambda: edited('guard-liveness', 'guard-2.jsonl', unmarked), DIVERGES, None),
    ('guard-liveness', lambda: edited('guard-liveness', 'guard-3.jsonl', drop('init')), ERROR,
     'check 3: no init event'),
])
def test_a_changed_behaviour_diverges_and_a_broken_run_is_an_error(pid, changes, outcome, finding):
    verdict = replay(pid, changes())
    assert verdict.outcome == outcome
    assert finding is None or verdict.finding == finding


def test_no_fixture_holds_a_path_or_an_id_from_the_recording_machine():
    for path in sorted(FIXTURES.iterdir()):
        found = PRIVATE_RE.search(path.read_text(encoding='utf-8'))
        assert found is None, f'{path.name} holds {found.group(0)!r}: re-record it through save_fixtures'
```

<!-- red:task6 test_probe_replay.py -->

- [ ] **Step 2: Run the test to verify it fails.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_probe_replay.py`
Expected: 14 failed, since no fixture folder exists yet. `test_every_registered_probe_has_its_fixtures` fails with "is missing; record it with save_fixtures", and each `test_the_recorded_run_passes` case gets ERROR in place of PASS. The four cases that edit a stream through `edited()` alone (both `agent-tools` cases and both `guard-liveness` cases), and the privacy test, raise `FileNotFoundError`. The `agent-model-pins` DIVERGES case raises `TypeError: 'NoneType' object is not iterable` first, from `dispatches(None)` in `explore_ids()`. The `stop-continuation` DIVERGES case and the two ERROR cases that change no stream fail their assertions: a missing stream is ERROR with the finding `no stream-json events`.

- [ ] **Step 3: Make the broken binary (DF2).**

**Create** `~/.cache/agent-skills/scratch/plan58-bin/broken-claude` with the Write tool:

```bash
#!/bin/sh
# A deliberately broken setup for drift spec Validation 5: it answers
# --version like the held binary and fails every probe run, as a crashed or
# unauthenticated binary would.
if [ "$1" = --version ]; then exec "$HOME/.cache/agent-skills/scratch/plan58-bin/claude" --version; fi
exit 3
```

Run: `chmod +x ~/.cache/agent-skills/scratch/plan58-bin/broken-claude`

- [ ] **Step 4: A broken setup yields ERROR (Validation 5).** Add `--allow-old` if `probes` refuses the binary as older.

Run: `uv run --python 3.13 python build/cc_guide/cli.py probes --claude ~/.cache/agent-skills/scratch/plan58-bin/broken-claude --only agent-tools`
Expected: exit 1, and these lines:

```text
probes: <version> at ~/.cache/agent-skills/scratch/plan58-bin/broken-claude
agent-tools: ERROR: the agent with Bash: no stream-json events
  raw output: <cache>/probes/<timestamp>-agent-tools
appended 1 row(s) to build/cc_guide/PROBES.md; nothing is committed
```

`build/cc_guide/PROBES.md` now exists, with one ERROR row.

- [ ] **Step 5: Check what the live runs will load.** These are read-only.

Run: `git -C ~/Projects/agent-skills branch --show-current`
Expected: `main`.

Run: `git -C ~/Projects/agent-skills status --short -- agents hooks`
Expected: no output.

Run: `readlink ~/.claude/agents/explore.md`, then the same for `~/.claude/agents/test-runner.md`, `~/.claude/agents/code-reviewer.md` and `~/.claude/hooks/readonly-agent-guard.py`.
Expected: each prints its file's full path under `~/Projects/agent-skills/` (`agents/` or `hooks/`).

Run: `git -C ~/Projects/agent-skills rev-parse --short HEAD`
Expected: a commit; note it for the completion report, since the rows describe the agents and the guard at that commit.

Run: `git diff 5dae679 HEAD -- specs/guides/claude-code-customization-guide.md`
Expected: no output, or changes outside the sections the probes back (`hooks.events`, `hooks.exit-codes`, `hooks.patterns`, `subagents.frontmatter`, `subagents.tools`, `subagents.models`).

If the shared checkout is on another branch or has changes there, stop and tell your human partner: another session may be using it, so do not switch it yourself. If a backed section now states a behaviour differently from what its probe asserts, stop and ask whether the assertion changes first.

- [ ] **Step 6: The full run on the held binary (Validation 5).** `agent-model-pins` waits on three background agents, so this can take several minutes: run it with the Bash tool's `run_in_background`, and wait for its notification. Add `--allow-old` if `probes` refuses the binary as older.

Run: `uv run --python 3.13 python build/cc_guide/cli.py probes --claude ~/.cache/agent-skills/scratch/plan58-bin/claude --force`
Expected: exit 0, and four PASS lines, each followed by its `raw output:` folder:

```text
guard-liveness: PASS: git status passed; git fetch and git config --global were denied
agent-tools: PASS: with Bash: Bash, Read; without Bash: Glob, Grep, Read
stop-continuation: PASS: stop_hook_active read false, true, true
agent-model-pins: PASS: Explore and test-runner served claude-haiku-5-5; code-reviewer effort xhigh
```

A finding's tool or model names may differ on a newer binary while the outcome is still PASS: record the finding as printed. Note the four `raw output:` folders for Step 8.

- [ ] **Step 7: The ERROR row is settled by the later PASS.** Add `--allow-old` if `probes` refuses the binary as older.

Run: `uv run --python 3.13 python build/cc_guide/cli.py probes --claude ~/.cache/agent-skills/scratch/plan58-bin/claude`
Expected: exit 0 and `probes: none due`. It runs only `--version`.

- [ ] **Step 8: Save the fixtures (D3).** One command per probe, each with its folder from Step 6. `save_fixtures` cuts each stream to the fields the assertions read and scrubs the home folder, the temporary folder and the login name.

Run: `uv run --directory build/cc_guide --python 3.13 python -c "import probes; from pathlib import Path; print(probes.save_fixtures(Path('<guard-liveness folder>'), 'guard-liveness', Path('probe_streams')))"`

Run: `uv run --directory build/cc_guide --python 3.13 python -c "import probes; from pathlib import Path; print(probes.save_fixtures(Path('<agent-tools folder>'), 'agent-tools', Path('probe_streams')))"`

Run: `uv run --directory build/cc_guide --python 3.13 python -c "import probes; from pathlib import Path; print(probes.save_fixtures(Path('<stop-continuation folder>'), 'stop-continuation', Path('probe_streams')))"`

Run: `uv run --directory build/cc_guide --python 3.13 python -c "import probes; from pathlib import Path; print(probes.save_fixtures(Path('<agent-model-pins folder>'), 'agent-model-pins', Path('probe_streams')))"`

Expected: nine paths in all under `build/cc_guide/probe_streams/`, about 50 KB together.

Run: `grep -rn "$USER" build/cc_guide/probe_streams`
Expected: no output (exit 1). Read one fixture of each probe with the Read tool and confirm it holds no path, email address or session id.

- [ ] **Step 9: Run the tests to verify they pass.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +14 against Task 5.

- [ ] **Step 10: Run the gates and commit (DF1).**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`.

```bash
git add build/cc_guide/test_probe_replay.py build/cc_guide/probe_streams build/cc_guide/PROBES.md
git commit -m "test(cc_guide): record the four probes and replay their assertions (drift R12.6)"
```

---

### Task 7: The `/cc-guide probes` mode and the docs (R8.9, R12.7)

**Files:**
- Modify: `.claude/skills/cc-guide/SKILL.md` (description, argument hint, "Pick the mode", a new `## probes` section)
- Modify: `build/CLAUDE.md` (a paragraph on the probes)
- Modify: `CLAUDE.md` (the Commands lines)
- Modify: `hooks/README.md` (the Probe log's pointer to `PROBES.md`, R10.6)

The skill is project-local and Claude-only, so `check_frontmatter.py` does not read it (spec, Out of scope). Its description still starts with "Use when" and names the new trigger.

- [ ] **Step 1: The skill.**

**Replace** in `.claude/skills/cc-guide/SKILL.md`:

```markdown
  or a check summary that names releases untriaged, changed docs blocks, an
  audit due or stale citing files.
argument-hint: 'triage | verify <ids> | audit [<group>] | files [<paths>]'
```

**with:**

```markdown
  "run the probes", or a check summary that names releases untriaged, changed
  docs blocks, an audit due, probes due or stale citing files.
argument-hint: 'triage | verify <ids> | audit [<group>] | files [<paths>] | probes'
```

**Replace** in `.claude/skills/cc-guide/SKILL.md`:

```markdown
Each mode builds packets, dispatches the `cc-guide-verifier` agent on them, and settles every report with a script before anything is applied. The design is `specs/claude-code-drift-automation-spec.md`, R8; `references/formats.md` holds the packet layout and the report formats.
```

**with:**

```markdown
Each mode but `probes` builds packets, dispatches the `cc-guide-verifier` agent on them, and settles every report with a script before anything is applied. The design is `specs/claude-code-drift-automation-spec.md`, R8, and R10 for `probes`; `references/formats.md` holds the packet layout and the report formats.
```

**Replace** in `.claude/skills/cc-guide/SKILL.md`:

```markdown
The typed words arrive on the ARGUMENTS line: `triage`, `verify <ids>`, `audit [<group>]` or `files [<paths>]`. With none, run `cli.py check --worktree` and offer the mode its due items call for. Probes arrive with Stage 5.
```

**with:**

```markdown
The typed words arrive on the ARGUMENTS line: `triage`, `verify <ids>`, `audit [<group>]`, `files [<paths>]` or `probes`. With none, run `cli.py check --worktree` and offer the mode its due items call for.
```

**Replace** in `.claude/skills/cc-guide/SKILL.md`:

```markdown
## After any mode
```

**with:**

```markdown
## probes

Live probes check behaviour the guide states before the docs change (spec R10). Each one is a short `claude -p` run that spends tokens, so they run only in this mode or by the owner's hand, never from the session-start hook.

1. Run `cli.py binaries` and ask the owner which binary to probe. `probes` takes no default, since with several versions installed a default would probe the wrong one (spec Decision 15).
2. Run `cli.py probes --claude <path>`, which runs the due probes. `--only <ids>` names others, and `--force` runs every one. State the count first: a live probe costs about \$0.05–0.30. A binary older than the newest cached changelog release is refused; pass `--allow-old` only on the owner's word, and each row records it. Exit 2 is a setup error to fix first.
3. Each probe appends one row to `build/cc_guide/PROBES.md`, uncommitted, and keeps its raw output under `~/.cache/agent-skills/cc-guide/probes/`. `agent-model-pins` also leaves its session under `~/.claude/projects/`, since it reads effort from the transcripts. That output holds home paths and session ids: copy nothing from it into the repo.
4. A DIVERGES row is handled like a TOUCHES row: the probe's `[[probe]]` entry in `build/cc_guide/manifest.toml` names its sections and files. Run the `verify <ids>` mode on those sections and the `files [<paths>]` mode on those files. An ERROR row says nothing about the behaviour: read its raw output, then report it to the owner. DIVERGES and ERROR stay due until a later PASS.

## After any mode
```

- [ ] **Step 2: `build/CLAUDE.md`.**

**Replace** in `build/CLAUDE.md`:

```markdown
committed on `main` and the next daily check runs.
Nothing is committed for you.
```

**with:**

```markdown
committed on `main` and the next daily check runs.
`cli.py probes --claude <path>` runs the live probes that `manifest.toml`
registers (spec R10): short `claude -p` runs that check behaviour the guide
states, each from its own scratch directory under the system temp directory.
`cli.py binaries` lists the binaries to choose from. A probe keeps its raw
output under `~/.cache/agent-skills/cc-guide/probes/` and appends one row to
`cc_guide/PROBES.md`; a DIVERGES or ERROR row stays due until a later PASS.
`agent-model-pins` also leaves its session under `~/.claude/projects/`, since
it reads effort from the subagents' transcripts.
`probe_checks.py` holds the assertions, which read the raw stream-json.
`probe_streams/` holds recorded runs, cut down and scrubbed by
`probes.save_fixtures`, which `test_probe_replay.py` replays (R12.6); re-record
them only through `save_fixtures`, since a raw stream holds home paths and
session ids.
Nothing is committed for you.
```

- [ ] **Step 3: The root `CLAUDE.md`'s Commands section (R12.7).**

**Replace** in `CLAUDE.md`:

```bash
uv run --python 3.13 python build/cc_guide/cli.py lint
uv run --python 3.13 python build/cc_guide/cli.py check
```

**with:**

```bash
uv run --python 3.13 python build/cc_guide/cli.py lint
uv run --python 3.13 python build/cc_guide/cli.py check

# Live probes (spec R10): binaries lists the claude binaries installed; probes runs the due probes against the one named
# (about $0.05-0.30 each), appends rows to build/cc_guide/PROBES.md and commits nothing; /cc-guide probes drives both
uv run --python 3.13 python build/cc_guide/cli.py binaries
uv run --python 3.13 python build/cc_guide/cli.py probes --claude <path>
```

Run: `wc -l CLAUDE.md`
Expected: 153, under the `claude-md-size` check's 200.

- [ ] **Step 4: `hooks/README.md`'s Probe log (R10.6).**

**Replace** in `hooks/README.md`:

```markdown
`RECORDED_MAIN_SESSION_PAYLOAD` in `test_readonly_agent_guard.py`;
`probe-readonly-guard.sh` re-checks the live behaviour end to end.
```

**with:**

```markdown
`RECORDED_MAIN_SESSION_PAYLOAD` in `test_readonly_agent_guard.py`;
`probe-readonly-guard.sh` re-checks the live behaviour end to end. The drift
tool's `guard-liveness` probe runs that script (`build/cc_guide/cli.py probes`)
and logs each run in `build/cc_guide/PROBES.md`; this table keeps the payload
findings.
```

- [ ] **Step 5: Run the gates and commit.**

Run: `uv run --python 3.13 python build/cc_guide/cli.py lint`
Expected: exit 0. Any `STALE` lines name files this plan did not touch.

Run: `uv run --python 3.13 --with pyyaml python build/check_conformance.py`
Expected: exit 0, no output.

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`.

```bash
git add .claude/skills/cc-guide/SKILL.md build/CLAUDE.md CLAUDE.md hooks/README.md
git commit -m "docs(cc_guide): add the /cc-guide probes mode and document the probes (drift R8.9, R12.7)"
```

---

### Task 8: Record whether `startup` fires under `claude -p` (D5)

**Files:**
- Modify: `build/CLAUDE.md` (one sentence in the `notice.sh` paragraph)

The check runs the held binary once from a fresh temporary directory, with a stand-in SessionStart hook on this repo's matcher, `startup`, passed through `--settings` (DF5). No project settings exist there, so this repo's `notice.sh` cannot load: nothing is fetched and no notice is marked shown. The spike loaded a `--settings` hook the same way. The run costs a few cents.

- [ ] **Step 1: Write the check script.**

**Create** `~/.cache/agent-skills/scratch/plan58-bin/startup_check.py` with the Write tool:

```python
'''Plan 58 Task 8: does a SessionStart hook on the startup matcher fire under
claude -p? One run of the held binary from a fresh temporary directory, with
a stand-in hook, so no repo's settings or notice.sh load.'''
import json
import subprocess
import tempfile
from pathlib import Path

BIN = Path.home() / '.cache/agent-skills/scratch/plan58-bin'
LOG = BIN / 'startup.log'
LOG.unlink(missing_ok=True)
hook = {'hooks': {'SessionStart': [{'matcher': 'startup', 'hooks': [
    {'type': 'command', 'command': f"echo startup >> '{LOG}'"}]}]}}
argv = [str(BIN / 'claude'), 'Reply with the word OK.', '-p', '--setting-sources', 'user',
        '--settings', json.dumps(hook), '--model', 'sonnet', '--effort', 'low', '--max-turns', '1',
        '--no-session-persistence', '--output-format', 'stream-json', '--verbose', '--include-hook-events']
with tempfile.TemporaryDirectory(prefix='cc-guide-startup-') as cwd:
    run = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=300)
events = [json.loads(line) for line in run.stdout.split('\n') if line.startswith('{')]
names = sorted({e.get('hook_name') or '' for e in events if e.get('subtype') == 'hook_response'})
print('exit', run.returncode)
print('hook responses:', ', '.join(filter(None, names)) or 'none')
print('stand-in log:', LOG.read_text(encoding='utf-8').strip() if LOG.exists() else 'absent')
```

- [ ] **Step 2: Run the check once.**

Run: `uv run --python 3.13 python ~/.cache/agent-skills/scratch/plan58-bin/startup_check.py`
Expected: `exit 0`, `hook responses:` naming `SessionStart:startup`, and `stand-in log: startup`. That means the hook fired under `claude -p`. `stand-in log: absent` means it did not.

- [ ] **Step 3: Record the answer.** Put the held binary's version from Task 1 Step 2 and today's date in place of `2.1.303, 2026-10-20` where they differ.

If the hook fired:

**Replace** in `build/CLAUDE.md`:

```markdown
committed on `main` and the next daily check runs.
`cli.py probes --claude <path>` runs the live probes that `manifest.toml`
```

**with:**

```markdown
committed on `main` and the next daily check runs. The `startup` matcher also
fires under `claude -p` (checked on 2.1.303, 2026-10-20), so a `claude -p` run
whose working directory is this repo or one of its worktrees runs `show` and
`refresh` too.
`cli.py probes --claude <path>` runs the live probes that `manifest.toml`
```

If it did not fire, put this sentence in the same place instead: "The `startup` matcher does not fire under `claude -p` (checked on 2.1.303, 2026-10-20), so a `claude -p` run in this repo runs neither `show` nor `refresh`."

- [ ] **Step 4: Run the gates and commit.**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`.

```bash
git add build/CLAUDE.md
git commit -m "docs(build): record that startup fires under claude -p (the startup item)"
```

If the hook did not fire, the commit message says "does not fire".

---

### Task 9: Validation (Validation 5 and 6)

- [ ] **Step 1: The suites.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +94 against Task 1 Step 1.

Run: `uv run --directory build --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`
Expected: +94 passed against Task 1 Step 1, with the same skips and the same pre-existing failures, if any.

- [ ] **Step 2: Every existing gate (Validation 6).**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`. It runs the frontmatter, provenance and conformance lints, Tier 1 snippets, the dependency-drift test, `sync_runtime_assets.py --check`, `cli.py lint`, the placement tests and the suite-registry check.

Run: `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check`
Expected: exit 0: no adapter changed.

- [ ] **Step 3: The acceptance evidence (Validation 5).** Read `build/cc_guide/PROBES.md` with the Read tool.
Expected: one ERROR row for `agent-tools` from `broken-claude`, then four PASS rows from the held binary, each with the version and, where used, `--allow-old`.

Run: `git ls-files build/cc_guide/probe_streams`
Expected: nine files, and no other new file under `build/cc_guide/` but the five modules and tests and `PROBES.md`.

Run: `git status --short`
Expected: clean.

---

## Plan completion notes

Run the Plan Completion Protocol (writing-plans) after Task 9 and the final review.
- **Deferred items to tick** (step 3): the registry gaps item (section `38-claude-code-drift-automation — 2026-10-05`), done by Task 2 for part (a) and by D1, Task 1 and Task 5 for part (b); and the startup item (section `49-claude-code-drift-automation — 2026-10-18`), done by Task 8. Tick each as `- [x] … → done in plan 58`.
- **Coverage gaps for the owner** (R4.3): the probes rest on facts no guide section covers. List them in the completion report, for the owner to extend the guide or leave them uncovered: `agent_type` in PreToolUse payloads (the guard); the `claude -p` flags the probes use (`--setting-sources`, `--include-hook-events`, `--forward-subagent-text`, `--max-budget-usd`); the subagent transcripts' `effort` field and their `subagents/` layout; fork mode and `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`; and whether `startup` fires under `claude -p` (Task 8's answer).
- **The spec retires.** Stage 5 is the drift spec's last stage, and no other live plan implements it, so step 5 moves `specs/claude-code-drift-automation-spec.md` to `specs/completed/`, marked complete at the top. The spec has no relative links of its own. Other files name its path, so the retire commit re-points them to `specs/completed/claude-code-drift-automation-spec.md`, as plan 53's retire commit did for its spec. Find them with `git grep -n "specs/claude-code-drift-automation-spec.md"`: at `5dae679` they are `NOTICE`, `.claude/skills/cc-guide/SKILL.md`, `build/CLAUDE.md`, `build/cc_guide/cli.py` (its docstring, which Task 5 rewrites), `build/cc_guide/manifest.toml`, `build/cc_guide/notice.sh` and `build/test_check_conformance.py`. Leave the paths inside completed plans as they are. Run the cc_guide suite and the commit lints after the re-point.
- **The spec's Out of scope list goes to the backlog** (step 3). Its heading says those items are "logged to `specs/deferred_items.md` at plan completion", and the spec retires with this plan. Append these to this plan's section, each in the deferred-item schema:
  - The Stop-hook block cap probe. Size: plan. Revisit if: drift #2 (the Stop-hook continuation reading) is resolved toward re-checking.
  - Probes for behavioural ⚠ claims the repo does not depend on, such as the fork-mode and `background` defaults. Size: plan. Revisit if: a skill, agent or hook comes to depend on one of them.
  - Line-level citations, and anchors for single rows of the guide's tables. Size: design. Revisit if: a section-level citation proves too coarse to tell a stale file from a current one.
  - Widening `check_frontmatter.py` to `.claude/skills` and `.claude/agents`. Size: design. Revisit if: a project-local skill or agent ships a frontmatter defect the lint would have caught.
  Skill frontmatter pins stay with deferred item 31, and the Codex and Gemini guides with their existing item from the conformance spec. The best-practices spec and the §8 TODO are settled, and outward-facing automation is a standing non-goal: log none of these.
- **The scratch files** under `~/.cache/agent-skills/scratch/plan58-bin/` and `plan58-spike/` are outside the repo. Remove them once the branch has merged, or keep the held binary for a later re-recording. The spike's persisted sessions are under `~/.claude/projects/`, in the folders whose names start `-private-tmp-plan58-spike-`, and Task 6's `agent-model-pins` run leaves one in a folder named after its `cc-guide-probe-agent-model-pins-` temporary directory. Removing them is the owner's call. The planning proof is outside the repo too: the template and scripts in `plan58-gen/`, and the clones `plan58-full/`, `plan58-main/`, `plan58-head/` and `plan58-proto/`. They can go with the rest once the plan is retired.
