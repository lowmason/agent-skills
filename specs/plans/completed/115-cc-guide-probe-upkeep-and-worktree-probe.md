# cc-guide probe upkeep and the worktree-isolation probe Implementation Plan

**Status: COMPLETE (2026-11-27)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md, or specs/completed/deferred_items.md once archived

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clear plan 58's review Minors (a)–(aa), move process control out of `build/cc_guide/probes.py`, fix plan 109's four watch items, and register a live probe for the worktree-isolation facts of the guide.

**Architecture:** Process control (environment, `execute`, process groups, signals, the `claude -p` command line) moves from `probes.py` into a new `probe_process.py`. The new probe's runner goes in its own `probe_worktrees.py`, and its assertions go in `probe_checks.py`, as the other probes' assertions do. Its `collect` step reduces the raw streams to a small sightings file. That file is the committed fixture, as with `explore-override`, because the scrubbed stream drops all tool output.

**Tech Stack:** Python (the dev Python in `build/versions.toml`), stdlib only, pytest; `git` and `ps` on macOS and Linux.

**Spec:** none. The requirements are six `specs/deferred_items.md` items, chosen for a plan by the owner in the 2026-11-27 `/deferred` pass (stream C):

- R52: "Review Minors from the per-task and final reviews of plan 58" (section `58-claude-code-drift-automation — 2026-10-20`), points (a)–(aa). Triggered 2026-11-14, so (l) applies.
- R122: "Watch the probe-backed facts of the guide's worktree-isolation section with a registered probe" (section `cc-guide-2.1.326-worktree-isolation …— 2026-11-17`).
- R147–R150: the four items of section `109-cc-guide-fetch-notice-and-probes — 2026-11-26`. They are watch items whose revisit signals have not fired. **They are taken early by the owner's choice**, because they share these files.

The drift spec that the probe code argues from is `specs/completed/claude-code-drift-automation-spec.md` (R10, R12.6).

## Global Constraints

- Edit only these files: `build/cc_guide/` (`probes.py`, the new `probe_process.py` and `probe_worktrees.py`, `probe_checks.py`, `state.py`, `check.py`, `cli.py`, `manifest.toml`, `PROBES.md`, `baseline.json` through `cli.py baseline cite` only, `probe_streams/`, and their tests), `.claude/skills/cc-guide/SKILL.md`, `build/CLAUDE.md`, and append-only lines in `specs/deferred_items.md` and `specs/history.md`. Do not touch `skills/derive-roadmap/`, `skills/write-with-asd-ste100/`, the guide, or the execution machinery (writing-plans, subagent-driven-development, executing-plans, reviewer agents and the shared reviewer block, finishing-a-development-branch).
- The `[[probe]]` entry may name `skills/using-git-worktrees/SKILL.md` and `skills/finishing-a-development-branch/SKILL.md` in `files`. Never edit either skill.
- Run the `cc_guide` suite as `uv run python build/run_suites.py cc_guide` from the repo root. Every task ends with it green.
- After any change under `build/cc_guide/`, run `uv run python build/cc_guide/cli.py lint` (exit 0) and `uv run --with pyyaml python build/check_conformance.py`. On 2026-11-27 lint already lists about 40 files STALE, `probes.py` and `probe_checks.py` among them. Those are a `/cc-guide files` review's to clear, not this plan's. Run `baseline cite` only on `probe_worktrees.py`, the one file this plan writes against the guide's current `subagents.worktrees` text, and never on a file the plan has not reviewed against every section it cites.
- Module and test basenames stay unique across `build/`, since `cd build && pytest` collects this suite too. `probe_process.py`, `test_probe_process.py`, `probe_worktrees.py` and `test_probe_worktrees.py` are free names today.
- Single quotes, named constants (G25), stdlib only. No `/proc` and no macOS-only tool: the repo stays portable (`ps -o args= -p <pid>` works on both macOS and Linux).
- A committed probe file holds no home path, temp path, login name, session id or tool-use id (plan 58 decision D3). `test_probe_replay.py`'s `PRIVATE_RE` checks this.
- A live probe run spends money. It runs only in Task 8, after the owner's go-ahead in chat.

## Review Focus

1. The model changes a step's command text, such as extra quoting. Expected: that step reads as never run, so the verdict is ERROR, not DIVERGES (Task 6, `test_a_rewritten_command_is_an_error_not_a_divergence`).
2. The owner's global git config has signing, hooks or another `init.defaultBranch`. Expected: the scratch repos still build the same way (Task 7, `test_the_setup_git_ignores_the_callers_global_config`).
3. The owner's user settings set `worktree.baseRef`. Expected: fact 4 is not decided by them, because each run loads only project settings and the scratch repos have none (Task 7, `test_each_run_loads_project_settings_only`).
4. `pwd` prints `/tmp/...` where the scratch path resolves to `/private/tmp/...`. Expected: the place still matches (Task 6, `test_a_pwd_through_a_symlink_names_the_same_place`).
5. The OS reuses a teardown hook's pid for another process. Expected: that process is never killed and is not read as the hook (Task 2, `test_collect_teardown_never_kills_a_pid_that_is_not_its_hook`).

## Decisions

- **D1** (owner, plan review, 2026-11-27): approved the plan with the planner's defaults P1–P5 below, and chose subagent-driven execution in this session. Applied in: Tasks 1–8.
- **D2** (owner, Task 8 gate, 2026-11-27): go ahead with the live run on the 2.1.330 Desktop app binary with `--allow-old`. Applied in: Task 8.

Planner's defaults, approved by D1:

- **P1** The worktree runner goes in its own module, `probe_worktrees.py`, not in `probes.py`. Its git setup alone is about 80 lines, and `probes.py` already holds five jobs (R52 (l)). The older probes stay in `probes.py`.
- **P2** R52 (x): the `probes` mode learns the count from the `probes:` line of `cli.py check --worktree`, which that mode runs anyway. No `--dry-run` flag is added.
- **P3** R52 (j): `execute` sweeps a run's process group with SIGKILL after a normal exit. `async-teardown` turns the sweep off (`Invocation.sweep = False`), because its `collect` step must see whether claude itself ended the hook.
- **P4** R148: a hook that outlives its 120 s loop logs `expired`, and the assessment reads such a log as ERROR (inconclusive). The lifetime stays at 120 s, so a hook orphaned on the timeout path still ends soon.
- **P5** R122 covers the first four facts. The desktop-app fact stays a hand check, as the item says.

## Point map for R52

| Point | Task | Remedy |
|---|---|---|
| (a) | 3 | `parse_probes` calls `is_probe_header` instead of its own `PROBE_COLUMNS <= set(header)` test |
| (b) | 3 | A test for a row with an empty Probe cell (SetupError) |
| (c) | 3 | `scrub_events` also redacts each private string in its JSON-escaped form |
| (d) | 3 | Remove `parse_stream`'s dict check, which cannot fire |
| (e) | 3 | Tests: the `None in results` branch of `assess_guard_liveness`, a `Task` dispatch, a JSON-escaped private value |
| (f) | 3 | `broken()` also reads a result whose `subtype` starts with `error` as broken |
| (g) | 3 | `MCP_TOKEN_RE` stops before a trailing `,`, `;` or `:` |
| (h) | 2 | `shown_path` also maps the resolved home to `~`, and `log_row` redacts the Binary cell |
| (i) | 2 | `run_probe` makes `run_dir` and the scratch folder inside its `try` |
| (j) | 2 | Correct the `stop_group` docstring, and sweep the group after a normal exit (P3) |
| (k) | 2 | Tests: the scratch-inside-a-work-tree ERROR, scratch removal on ERROR and on timeout |
| (l) | 1 | Process control moves to `probe_process.py` |
| (m) | 2 | `probes.run` prints the scrubbed finding that the row holds |
| (n) | 2 | One `planted_privates` fixture in `test_probes.py` |
| (o) | 5 | Drop the unused `capsys`; both cases assert the subcommand's own error text |
| (p) | 5 | Tests: `~` expansion of `--claude`, the success path of `run_binaries` |
| (q) | 5 | `main` computes the cache only for subcommands that use it |
| (r) | 4 | Each DIVERGES replay case pins its finding |
| (s) | 4 | Replay cases for the five named variants |
| (t) | 4 | `PRIVATE_RE` gains `msg_` and `req_` |
| (u) | 4 | Import `probe_checks.dispatches` directly |
| (v) | 4 | `save_fixtures` keeps Bash command text only for a probe that reads it, and replaces the scratch-folder name; re-scrub the committed fixtures |
| (w) | 4 | The isolated home in the replay test is reached through a symlink, so `home` and `home.resolve()` differ |
| (x) | 5 | SKILL.md: the count comes from `check --worktree`'s `probes:` line (P2) |
| (y) | 5 | SKILL.md: the Ground rules and After any mode lines on guide edits and settle exclude `probes` |
| (z) | 5 | SKILL.md: exit 1 means a probe DIVERGED or ERRORed |
| (aa) | 5 | `build/CLAUDE.md`: the probes text becomes its own paragraph, which ends with "Nothing is committed for you." |

---

### Task 1: Move process control into `probe_process.py` (R52 (l))

A pure move. Behaviour and every test stay the same.

**Files:**
- Create: `build/cc_guide/probe_process.py`
- Modify: `build/cc_guide/probes.py` (lines 36–197 today)
- Create: `build/cc_guide/test_probe_process.py`
- Modify: `build/cc_guide/test_probes.py` (the process tests at lines 1114–1305 today, and `monkeypatch.setattr(probes, 'KILL_GRACE', …)`)

**Interfaces:**
- Produces, in `probe_process.py`: `SCRUBBED_ENV`, `ALIAS_REMAPS`, `KILL_GRACE`, `EXIT_SIGNALS`, `HELD_SIGNALS`, `BUDGET_USD`, `Invocation`, `Execute`, `inherited_env() -> dict[str, str]`, `inherited_remaps() -> list[str]`, `execute(inv, cwd, out, err) -> int | None`, `stop_group(proc) -> None`, `held_signals()`, `term_as_exit()`, and `claude_args(claude, prompt, *, turns, sources, mode, allow=(), budget=BUDGET_USD, persist=False, extra=()) -> list[str]`. Signatures are unchanged.
- `probes.py` imports these names back (`from probe_process import …`), so `probes.execute`, `probes.Invocation` and `probes.claude_args` still resolve for `cli.py` and the tests.

- [x] **Step 1:** Move the names above into `probe_process.py` with their comments and docstrings. Give it a module docstring: process control for a probe run (R10.4). It cites no guide section: the stdin and process-group facts come from the drift spec, not the guide.
  > Deviation: probe_process.py carries `# cc-guide: subagents.frontmatter lean.model-routing @2.1.326` (final fix F5), since the SCRUBBED_ENV and ALIAS_REMAPS comments rest on those sections; lint lists it STALE, as it lists probes.py. It later also took Probe, Read, PROBE_TIMEOUT, GIT_ROUTING and environ_without (Task 7, F10).
- [x] **Step 2:** Move the tests of the moved functions (`test_a_run_never_inherits_the_effort_override` through `test_an_ignored_signal_is_not_held_so_a_stop_after_it_is_acted_on_once`, with the fixtures they alone use) into `test_probe_process.py`. Point their patches at `probe_process` (for example `monkeypatch.setattr(probe_process, 'KILL_GRACE', 1)`). A patch of `probes.os.<name>` patches the shared `os` module and needs no change.
- [x] **Step 3:** Run `uv run python build/run_suites.py cc_guide`. Expected: the same pass count as before the move (note it before Step 1), 0 failed.
- [x] **Step 4:** Run `wc -l build/cc_guide/probes.py build/cc_guide/probe_process.py`, `uv run python build/cc_guide/cli.py lint` and `uv run python build/cc_guide/probes.py drive-cut` (expected: the usage message, exit 1). Commit: `refactor(cc_guide): move probe process control into probe_process.py`.

### Task 2: Run, log and teardown fixes in `probes.py` (R52 (h) (i) (j) (k) (m) (n), R147, R148)

**Files:**
- Modify: `build/cc_guide/probe_process.py`, `build/cc_guide/probes.py`, `build/cc_guide/probe_checks.py` (`assess_async_teardown`)
- Test: `build/cc_guide/test_probe_process.py`, `build/cc_guide/test_probes.py`, `build/cc_guide/test_probe_checks.py`

**Interfaces:**
- Consumes: Task 1's `probe_process`.
- Produces: `Invocation.sweep: bool = True`, a new last field. `probes.is_hook(pid: int, hook: Path) -> bool`. `probe_checks.TEARDOWN_EXPIRED = 'expired'`. `probes.public_finding(verdict: Verdict) -> str`.

- [x] **Step 1: Write the failing tests.**
  - `test_probe_process.py::test_a_normal_exit_sweeps_what_the_run_left_in_its_group`: a script starts `sleep 60 &` and exits 0. After `execute` returns 0, the background pid is gone.
  - `test_probe_process.py::test_an_invocation_with_sweep_off_leaves_its_group_alone`: the same with `sweep=False`. The pid is still running; the test then kills it.
  - `test_probes.py::test_collect_teardown_never_kills_a_pid_that_is_not_its_hook` (Review Focus 5): the log names the pid of a `sleep 60` child that the test started, whose command line lacks the hook path. `collect_teardown` sends it no signal, the log ends with `gone`, and the `sleep` still runs.
  - `test_probes.py::test_the_teardown_hook_logs_expired_once_its_lifetime_ends`: with the lifetime patched short, the log's last line is `expired`.
  - `test_probe_checks.py::test_a_teardown_hook_that_expired_is_an_error`: `assess_async_teardown(events, ['start 4242', 'expired', 'gone'])` is `ERROR`, and the finding names the hook's lifetime.
  - `test_probes.py::test_a_run_dir_that_cannot_be_made_is_an_error_row` (i): `run_dir`'s parent is a file. `run_probe` returns ERROR with `OSError` in the finding, with no traceback.
  - `test_probes.py::test_a_scratch_folder_inside_a_work_tree_is_an_error_and_is_removed` (k): patch `tempfile.tempdir` to a folder inside a `git init` repo. The verdict is ERROR naming the work tree, and the scratch folder is gone afterwards.
  - `test_probes.py::test_scratch_is_removed_after_an_error_and_after_a_timeout` (k): a fake `execute` that returns `None`, and one that raises `OSError`. Both leave no `cc-guide-probe-*` folder under the patched temp dir.
  - `test_probes.py::test_the_binary_cell_hides_the_resolved_home_and_the_login` (h): HOME is a symlink to the real folder, and the binary lies under the resolved path in a folder named after the login. The cell starts with `~` and holds neither the resolved home nor the login.
  - `test_probes.py::test_run_prints_the_scrubbed_finding` (m): a verdict whose finding holds the home path. The printed line holds `<private>` and not the path.
- [x] **Step 2:** Run the new tests. Expected: each FAILS (a missing name, or an assertion).
- [x] **Step 3: Implement.**
  - `execute`: after a normal `proc.wait`, when `inv.sweep`, send SIGKILL to the group with the same `ProcessLookupError`/`PermissionError` suppression as `stop_group`. `prepare_teardown`'s invocation passes `sweep=False`.
  - `stop_group` docstring (j): it waits up to `KILL_GRACE` seconds for the group's leader, not for every member, and a normal exit is swept by `execute`.
  - `is_hook(pid, hook)`: `ps -o args= -p <pid>` holds `str(hook)`. A failed `ps` is False. `collect_teardown` takes the hook path as `scratch / TEARDOWN_SCRIPT` (name the file `teardown-hook.sh` through that constant), uses `is_hook` and `running` together for both the gone/alive reading and the SIGKILL, and so never signals a pid that is not its hook.
  - `TEARDOWN_HOOK` ends with `echo expired >> "$log"` after its loop. `assess_async_teardown` returns ERROR when `TEARDOWN_EXPIRED` is in the log, before any other reading: the hook ended by itself, so the log shows nothing about claude's teardown.
  - `run_probe` (i): `run_dir.mkdir` and `tempfile.mkdtemp` move inside the `try`. `scratch` starts as `None`, and the `finally` removes it only when set.
  - `shown_path` (h) also maps `Path.home().resolve()` to `~`. `log_row` passes the Binary cell through `probe_checks.redact(…, private_strings())` after `shown_path`.
  - `public_finding(verdict)` holds `log_row`'s MCP-then-redact pass. `log_row` and `run`'s printed line both use it (m).
  - (n): one `planted_privates` fixture in `test_probes.py` replaces the setup that `planted_privates` and the `save_fixtures` test repeat.
  > Deviation: final fixes F8 and F10: inside_a_repo drops inherited GIT_* names, and probes.run removes every inherited GIT_* name from os.environ around the probe loop (probe_process.environ_without) and restores it after, also on a stop.
- [x] **Step 4:** Run `uv run python build/run_suites.py cc_guide`. Expected: all pass, the recorded `async-teardown` replay included.
- [x] **Step 5:** Run `cli.py lint`. Commit: `fix(cc_guide): sweep run groups, guard teardown kills, and scrub every printed finding`.

### Task 3: Assertion and log-parse fixes (R52 (a)–(g), R150)

**Files:**
- Modify: `build/cc_guide/state.py` (`parse_probes`), `build/cc_guide/probe_checks.py`
- Test: `build/cc_guide/test_state.py`, `build/cc_guide/test_probe_checks.py`

**Interfaces:**
- Produces: `probe_checks.HANDBACK_TOOLS = frozenset({'SubagentHandback'})` and `HANDBACK_FIELD = 'message'`.

- [x] **Step 1: Write the failing tests.**
  - `test_state.py::test_a_row_with_an_empty_probe_cell_is_a_setup_error` (b).
  - `test_probe_checks.py::test_scrub_events_redacts_a_private_value_with_a_quote_or_backslash` (c, e): private `C:\\Users\\o"q` inside a Bash command. The scrubbed text holds `<private>` and neither the raw nor the escaped value.
  - `test_probe_checks.py::test_a_guard_check_whose_result_is_missing_is_an_error` (e): a Bash call with no `tool_result` gives ERROR, "its result is missing".
  - `test_probe_checks.py::test_a_task_dispatch_counts_as_an_agent_dispatch` (e): `dispatches` maps a `Task` tool_use like an `Agent` one.
  - `test_probe_checks.py::test_an_error_subtype_result_is_broken` (f): a result with `subtype: 'error_max_turns'` and `is_error: False` gives a reason from `broken`.
  - `test_probe_checks.py::test_the_mcp_token_stops_before_trailing_punctuation` (g): `MCP_TOKEN_RE.sub(MCP_MARK, 'mcp__s__t, mcp__u__v; mcp__w__x:')` is `'<mcp-tool>, <mcp-tool>; <mcp-tool>:'`.
  - `test_probe_checks.py::test_a_hand_back_is_not_a_read_and_its_message_is_the_answer` (R150): an Explore agent whose only tool call is `SubagentHandback` with `{'message': '<mark> <claude_md canary>'}`. `explore_void` gives None. The sighting's tool-call count is 0, and its mark and CLAUDE.md canary are seen.
- [x] **Step 2:** Run them. Expected: FAIL. The (b) test may already pass. Then it stays as the missing coverage, and the step notes that.
- [x] **Step 3: Implement.**
  - (a) `parse_probes` takes a header as the log table's when `is_probe_header(line)` is true, and drops its own `PROBE_COLUMNS <= set(header)` test.
  - (c) `scrub_events` redacts each private string and its `json.dumps(value, ensure_ascii=False)[1:-1]` form.
  - (d) Remove the `isinstance(event, dict)` branch of `parse_stream`. A line that opens with `{` and parses is a dict.
  - (f) `broken` also returns a reason for a result whose `subtype` starts with `error`, worded as the `is_error` reason is.
  - (g) Add `,;:` to `MCP_TOKEN_RE`'s excluded characters.
  - R150: `explore_sightings` leaves `HANDBACK_TOOLS` calls out of the tool-call count, and adds each one's `input[HANDBACK_FIELD]` text to what the agent said.
  > Deviation: the review of the save_fixtures side-file redaction was folded into Task 4: side files get the same escaped-form redaction.
- [x] **Step 4:** Run `uv run python build/run_suites.py cc_guide`. Expected: all pass, the eight recorded replays included.
- [x] **Step 5:** Run `cli.py lint`. Commit: `fix(cc_guide): tighten probe assertions and read a subagent hand-back as an answer`.

### Task 4: Fixtures and replay coverage (R52 (r)–(w))

**Files:**
- Modify: `build/cc_guide/probes.py` (`Probe`, `save_fixtures`), `build/cc_guide/probe_checks.py` (`scrub_events`, `_trim_block`)
- Modify: `build/cc_guide/probe_streams/*.jsonl` (re-scrubbed)
- Test: `build/cc_guide/test_probe_replay.py`, `build/cc_guide/test_probes.py`

**Interfaces:**
- Produces: `Probe.reads_commands: bool = False`, a new last field, set True for `guard-liveness` only. `probe_checks.scrub_events(events, private, *, keep_commands: bool = True) -> str`. `probe_checks.SCRATCH_MARK = '<scratch>'` and `SCRATCH_RE`, which matches `cc-guide-probe-<id>-<random suffix>`.

- [x] **Step 1: Write the failing tests.**
  - `test_probes.py::test_save_fixtures_drops_command_text_unless_the_probe_reads_it` (v): a recorded `agent-tools` stream with a Bash command keeps no `command`. A `guard-liveness` one keeps it.
  - `test_probes.py::test_save_fixtures_replaces_the_scratch_folder_name` (v): a stream holding `cc-guide-probe-agent-model-pins-7665i08q` becomes `<scratch>`.
  - (w): the `isolated_home` that the save_fixtures tests use is a symlink to a real folder, and a test asserts `str(home) != str(home.resolve())` before it plants both.
  - (t): `PRIVATE_RE` gains `msg_` and `req_`. `test_no_fixture_holds_a_path_or_an_id_from_the_recording_machine` stays green.
  - (u): `test_probe_replay.py` imports `probe_checks` and calls `probe_checks.dispatches`, not `probes.probe_checks.dispatches`.
  - (r): each DIVERGES case in `test_a_changed_behaviour_diverges_and_a_broken_run_is_an_error` asserts its finding as an exact substring that names the changed behaviour.
  - (s): five new cases in that table, each made by editing the recorded fixture: code-reviewer's effort changed from `xhigh` (DIVERGES); test-runner served on a non-Haiku model (DIVERGES); the without-Bash control gains Bash (`agent-tools`, DIVERGES); a `stop-continuation` log with the wrong exit codes (ERROR); guard check 1's `git status` result carrying the guard marker (DIVERGES, "was denied").
  > Deviation: (s) "the without-Bash control gains Bash" reads ERROR, not DIVERGES: assess_agent_tools rejects a control with the wrong tool list before its DIVERGES check, so the case is pinned as ERROR. Scratch names inside side files stay unreplaced, deferred (no committed side file holds one).
- [x] **Step 2:** Run them. Expected: the (v) and (s) tests FAIL. Any (s) case that already passes is kept as coverage, and the step notes it.
- [x] **Step 3:** Implement `keep_commands` (`_trim_block` drops `command` when it is false) and the `SCRATCH_RE` pass in `scrub_events`. `save_fixtures` passes `keep_commands=probe.reads_commands`.
- [x] **Step 4:** Re-scrub the committed stream fixtures through the new code, since the raw runs behind some of them are gone. For each `.jsonl` fixture of each probe: `probe_checks.scrub_events(probe_checks.parse_stream(text), probes.private_strings(), keep_commands=probe.reads_commands)`, written back in place. Then `git diff --stat build/cc_guide/probe_streams/`. Expected: only `command` keys and the one scratch name change.
- [x] **Step 5:** Run `uv run python build/run_suites.py cc_guide`. Expected: all pass. Commit: `test(cc_guide): pin replay findings, cover five variants, and scrub fixture commands`.

### Task 5: CLI, prune and docs fixes (R52 (o)–(q), (x)–(aa), R149)

**Files:**
- Modify: `build/cc_guide/cli.py` (`main`), `build/cc_guide/check.py` (`swap_latest`)
- Modify: `.claude/skills/cc-guide/SKILL.md`, `build/CLAUDE.md`
- Test: `build/cc_guide/test_cli.py`, `build/cc_guide/test_check.py`

- [x] **Step 1: Write the failing tests.**
  - (o) `test_probes_needs_claude_and_takes_only_or_force_not_both`: drop `capsys`. Each case asserts the argparse error text that names `--claude`, or `--only` with `--force`. Check that it fails on a parser without the subcommand: temporarily rename the subparser in a scratch copy, or reason it out from argparse's "invalid choice" text, and note which in the step.
  - (p) `test_probes_expands_a_tilde_in_claude`: `--claude ~/bin/claude` under `isolated_home` reaches `probes.run` as the expanded path. `test_binaries_prints_each_candidate_and_exits_zero`: a fake candidate on a patched PATH is printed with its version, exit 0.
  - (q) `test_binaries_never_computes_the_cache`: patch `cli.default_cache` to raise. `main(['binaries'])` still exits 0.
  - R149 `test_check.py::test_a_replaced_generation_survives_the_next_swap_within_the_grace`: make generation A with an mtime two hours old as `latest`. Swap to B, then at once to C. A still exists, because the first swap touched it.
- [x] **Step 2:** Run them. Expected: (q) and R149 FAIL. Note any that already pass.
- [x] **Step 3: Implement.** In `main`, dispatch `binaries`, `quotes` and `settle` before `cache = args.cache or default_cache()`. In `swap_latest`, `os.utime` the replaced generation (when there is one) before `prune_generations`, with the docstring saying why.
- [x] **Step 4: Docs.**
  - SKILL.md `## probes` step 3 (x, z): take the count from the `probes:` line of `cli.py check --worktree` (with `--only`, the ids named; with `--force`, every `[[probe]]`). State it and its cost before the run. Exit 1 means at least one probe DIVERGED or ERRORed; read the rows.
  - SKILL.md (y): the Ground rules lines on applying settle's corrections and on holds, and the After any mode lines on `[[exception]]` and on lint's STALE lines, say they do not apply to `probes`.
  - `build/CLAUDE.md` (aa): the text from "`cli.py probes --claude <path>` runs the live probes" to "Nothing is committed for you." becomes its own paragraph, wrapped like the rest of the file, with that sentence folded into its first sentences.
- [x] **Step 5:** Run the suite, `cli.py lint` and `uv run --with pyyaml python build/check_conformance.py`. Expected: all clean. Commit: `fix(cc_guide): keep replaced generations through a quick second swap; probes-mode and CLI fixes`.

### Task 6: The worktree-isolation assertions (R122, part 1)

**Files:**
- Modify: `build/cc_guide/probe_checks.py`
- Test: `build/cc_guide/test_probe_checks.py`

**Interfaces:**
- Produces, in `probe_checks.py`:
  - Command constants that the prompt and the assertion share: `WT_CONTROL = 'git rev-parse --show-toplevel'`, `WT_GIT_SUBSHELL = 'TOP=$(git rev-parse --show-toplevel); echo "$TOP"'`, `WT_PLAIN_SUBSHELL = 'HERE=$(pwd); echo "$HERE"'`, `WT_LIST = 'git worktree list --porcelain'`, `WT_PWD = 'pwd'`, `WT_MAIN_GIT = 'git -C {main} rev-parse --show-toplevel'`, `WT_LOG = 'git log --format=%s'`.
  - `WT_PUSHED = 'probe: pushed'`, `WT_UNPUSHED = 'probe: unpushed'` (commit subjects), `WT_ISOLATION_MARK = 'isolated in the worktree'` (in the harness's refusal text), `WT_LOCKED = 'locked'` (a porcelain line).
  - `worktree_sightings(streams: dict[str, list[dict] | None], places: dict[str, str]) -> dict`. `streams` keys: `isolation`, `noop`, `base-no-remote`, `base-failed-fetch`. `places` maps `main`, `worktree` and `plain-worktree` to absolute paths. It returns only booleans, place names and None, never a path or tool output:
    `{'isolation': {'broken', 'exited', 'pwd_after', 'locked_before', 'locked_after', 'steps': {<key>: {'ran', 'refused', 'marked'}}}, 'noop': {'broken', 'exit_refused', 'pwd_after'}, 'base-no-remote': {'broken', 'entered', 'has_pushed', 'has_unpushed'}, 'base-failed-fetch': {…same}}`.
    Step keys: `control`, `main_git_before`, `git_subshell`, `plain_subshell`, `main_git_after`. `before` and `after` are relative to the stream's ExitWorktree call. A step is found by its exact command after `strip()`. `pwd_after` is the place whose `os.path.realpath` equals the realpath of the first `WT_PWD` result after ExitWorktree, else `'other'`, or None when there is none.
  - `assess_worktree_isolation(sightings: dict) -> Verdict`.

The verdict rules:

| Reading | Outcome |
|---|---|
| Any part broken, a step never ran, a base run never entered a worktree, or a base log without `WT_PUSHED` | ERROR, naming it |
| A refused step without `WT_ISOLATION_MARK` | ERROR (refused for another reason) |
| `control`, `plain_subshell` or `main_git_after` refused with the mark; `git_subshell` or `main_git_before` not refused | DIVERGES (fact 1 or 2) |
| ExitWorktree in `isolation` refused, `pwd_after` not `main`, `locked_before` false or `locked_after` true | DIVERGES (fact 2) |
| `noop`'s ExitWorktree not refused, or its `pwd_after` not `plain-worktree` | DIVERGES (fact 3) |
| `base-failed-fetch` has `WT_UNPUSHED`, or `base-no-remote` lacks it | DIVERGES (fact 4) |
| Otherwise | PASS: `a $(...) naming git was refused and HERE=$(pwd) ran; ExitWorktree keep left a --worktree launch and its lock; it was a no-op in a plain-git worktree; a failed fetch left the unpushed commit out, and no remote kept it` |

All DIVERGES readings are listed in one finding, joined by `; `, as `assess_guard_liveness` does. ERROR outranks DIVERGES.

- [x] **Step 1: Write the failing tests** over synthetic events built by a local helper (a Bash `tool_use` and its `tool_result`, an ExitWorktree call, an init and a result event):
  - `test_the_recorded_shape_passes`: the 2026-11-17 behaviour gives PASS with the finding above.
  - One parametrized `test_each_changed_fact_diverges` with a case for each DIVERGES row of the table, each asserting a finding substring.
  - `test_a_rewritten_command_is_an_error_not_a_divergence` (Review Focus 1): `git_subshell` run as `TOP="$(git rev-parse --show-toplevel)"; echo "$TOP"` gives ERROR, "never ran".
  - `test_a_refusal_without_the_isolation_mark_is_an_error`.
  - `test_a_pwd_through_a_symlink_names_the_same_place` (Review Focus 4): the `pwd` result is `<tmp>/link/main`, where `link` is a symlink to the folder that holds `main`, and `pwd_after` is `main`.
  - `test_sightings_hold_no_path`: `json.dumps(worktree_sightings(...))` contains no value of `places`.
- [x] **Step 2:** Run them. Expected: FAIL (names not defined).
- [x] **Step 3:** Implement the constants, `worktree_sightings` and `assess_worktree_isolation`. Reuse `broken`, `tool_result_text` and the result-error reading of `tool_result_errors`. Add `subagents.worktrees` to the file's `# cc-guide:` citation line.
  > Deviation: the final review (F2, F4, F7, F9, F11) widened the sightings and the verdict table. The keep step is the first ExitWorktree keep call that succeeded or whose refusal carries WT_NOOP_MARK = 'No-op'; an isolation refusal is DIVERGES only with that mark, else ERROR; a successful ExitWorktree with another action, or an EnterWorktree the model made and the CLI did not refuse, is ERROR; the post-exit list must hold the worktree's own block (else DIVERGES "removed the worktree"), and a failed list is ERROR. Isolation gains kept_before, kept_after, exit_marked, other_exit and entered_by_model; noop gains other_exit and entered_by_model, and its exit_refused reads the No-op mark (Task 6 finding 4).
- [x] **Step 4:** Run the suite. Expected: all pass. Commit: `feat(cc_guide): worktree-isolation probe assertions`.

### Task 7: The worktree-isolation runner, not yet registered (R122, part 2)

**Files:**
- Create: `build/cc_guide/probe_worktrees.py`
- Modify: `build/cc_guide/probe_process.py` (`Invocation.cwd`, `execute`)
- Create: `build/cc_guide/test_probe_worktrees.py`

**Interfaces:**
- Consumes: Task 1's `Invocation`, `claude_args`, `PROBE_TIMEOUT` (move it to `probe_process` if `probes` would otherwise be imported) and Task 6's constants, `worktree_sightings` and `assess_worktree_isolation`.
- Produces: `Invocation.cwd: str = '.'`, a field placed before `sweep`, relative to the scratch folder that `execute` runs in. In `probe_worktrees.py`: `prepare_worktrees(scratch: Path, claude: str, repo: Path) -> list[Invocation]`, `collect_worktrees(scratch: Path, run_dir: Path) -> None` (writes `run_dir / 'worktrees.json'`), `assess_worktrees(read: Read) -> Verdict`, and `WORKTREE_PROBE = Probe(prepare_worktrees, collect_worktrees, assess_worktrees, {'worktrees.json': 'worktree-isolation.sightings.json'})`. `Probe` and `Read` stay in `probes.py`, so `probe_worktrees` builds a plain tuple that `probes.py` wraps, or `Probe` moves to `probe_process`. Pick whichever keeps `probe_worktrees` from importing `probes`.

The layout that `prepare_worktrees` builds under `scratch`, with git run with `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1` and `-c user.name=probe -c user.email=probe@example.invalid`:

| Folder | Build | Invocation (cwd) | Prompt |
|---|---|---|---|
| `iso/` + `iso-origin.git` | one commit, pushed, `origin/HEAD` set | `isolation` (`iso`), with `--worktree probe` | steps in order: `WT_CONTROL`, `WT_MAIN_GIT` (main = `scratch/iso`), `WT_GIT_SUBSHELL`, `WT_PLAIN_SUBSHELL`, `WT_LIST`, ExitWorktree action keep, `WT_PWD`, `WT_MAIN_GIT`, `WT_LIST` |
| `plain/` + `plain-wt/` | one commit; `git worktree add ../plain-wt` | `noop` (`plain-wt`) | ExitWorktree action keep, then `WT_PWD` |
| `norem/` | `WT_PUSHED`, then `WT_UNPUSHED`, no remote | `base-no-remote` (`norem`) | EnterWorktree name probe, then `WT_LOG` |
| `gone/` | `WT_PUSHED` pushed to `gone-origin.git`, `WT_UNPUSHED`, then the bare repo removed | `base-failed-fetch` (`gone`) | the same as `base-no-remote` |

- Before it returns, `prepare_worktrees` checks that `gone` has no `refs/remotes/origin/HEAD`, does have `refs/remotes/origin/main`, and fails `git fetch`. It raises `SetupError` otherwise, which `run_probe` turns into an ERROR row.
- Each prompt says: use the Bash tool for each command, one call each, exactly as written, with no retry in another form, and load ExitWorktree or EnterWorktree with ToolSearch if needed (2.1.325 deferred them).
- Each invocation uses `claude_args(…, turns=WORKTREE_TURNS, sources='project', mode='default', allow=('Bash', 'ExitWorktree', 'EnterWorktree', 'ToolSearch'), extra=('--strict-mcp-config', …))` with `WORKTREE_TURNS = 20`, `PROBE_TIMEOUT`, and env `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, `GIT_CONFIG_GLOBAL=os.devnull` and `GIT_CONFIG_NOSYSTEM=1`.
- `collect_worktrees` reads the four `.jsonl` streams from `run_dir`, builds `places` from `scratch` (`worktree` is `scratch/iso/.claude/worktrees/probe`), and writes `worktree_sightings(...)` as JSON. `assess_worktrees` reads `worktrees.json`. A missing file is ERROR.

- [x] **Step 1: Write the failing tests** in `test_probe_worktrees.py`:
  - `test_execute_runs_an_invocation_from_its_cwd` (in `test_probe_process.py`): `cwd='sub'` runs `pwd` in `scratch/sub`.
  - `test_prepare_builds_the_four_repos_and_their_invocations`: names, cwds, `--worktree probe` only on `isolation`, each prompt holding its commands in order, and `git -C <scratch>/iso` in the isolation prompt.
  - `test_the_failed_fetch_repo_meets_its_preconditions`: run the same git checks as `prepare_worktrees` and assert each.
  - `test_the_setup_git_ignores_the_callers_global_config` (Review Focus 2): HOME holds a `.gitconfig` with `commit.gpgsign = true` and `init.defaultBranch = trunk`. `prepare_worktrees` still succeeds, and `norem`'s branch is `main`.
  - `test_each_run_loads_project_settings_only` (Review Focus 3): each argv holds `--setting-sources project`, and no folder under `scratch` holds `.claude/settings.json`.
  - `test_collect_and_assess_read_a_run_like_a_live_one`: write synthetic streams (Task 6's shape) into a run folder, run `collect_worktrees` and `assess_worktrees`. Expected: PASS, and `worktrees.json` holds no scratch path.
  - `test_a_missing_sightings_file_is_an_error`.
- [x] **Step 2:** Run them. Expected: FAIL.
- [x] **Step 3:** Implement `Invocation.cwd` (`execute` runs from `cwd / inv.cwd`) and `probe_worktrees.py`. Give the module a `# cc-guide: subagents.worktrees @<release>` citation line, the release that `cli.py lint` asks for, and a docstring naming the four facts and the hand-checked desktop fact. Do not add it to `PROBE_RUNS` or `manifest.toml` yet.
  > Deviation: Probe and Read moved to probe_process.py. Final fixes F1 (Invocation.drop_prefixes; the four runs drop inherited GIT_* names) and F3 (main_git_command shell-quotes the scratch path, shared by the prompt and the matcher).
- [x] **Step 4:** Run the suite, then `uv run python build/cc_guide/cli.py baseline cite build/cc_guide/probe_worktrees.py`, then `cli.py lint`. Expected: all pass, and lint has no STALE line for `probe_worktrees.py`. `probe_checks.py` stays STALE, as it was before this plan. Commit: `feat(cc_guide): worktree-isolation probe runner (unregistered)`.

### Task 8: Register the probe and run it live (R122, part 3) — OWNER GATE

Registration, the live run, the fixture and the PROBES.md row land in one commit, because `run()` refuses a registered probe with no runner, and `test_the_recorded_run_passes` needs the fixture.

**Cost:** one run is four `claude -p` calls. The 2026-11-17 kit spent about $0.62 on the same four (isolation $0.27, no-op $0.11, each base run $0.12). This is above the usual $0.05–0.30 for one probe, because this probe makes four calls. The hard cap is $2.00 (four calls at `BUDGET_USD` $0.50). The plan allows at most two runs: the second only if the first is ERROR because the model strayed from a prompt, after a prompt fix. Expected spend is about $0.62–1.25, at most $4.00.

**Files:**
- Modify: `build/cc_guide/manifest.toml`, `build/cc_guide/probes.py` (`PROBE_RUNS`), `build/cc_guide/PROBES.md`, `build/cc_guide/test_probe_replay.py`, `build/CLAUDE.md`
- Create: `build/cc_guide/probe_streams/worktree-isolation.sightings.json`

- [x] **Step 1: Ask the owner** for the go-ahead, with the cost above, and for the binary. `cli.py binaries` lists them. On 2026-11-27 the PATH binary is 2.1.323 and the newest rows ran 2.1.330 from the desktop bundle with `--allow-old`. Ask whether an `--allow-old` row on the newest installed binary counts as "a current binary", or whether to update `claude` first. Do not go on without a yes in chat.
- [x] **Step 2:** Add the `[[probe]]` entry: `id = 'worktree-isolation'`, `sections = ['subagents.worktrees']`, `files = ['skills/using-git-worktrees/SKILL.md', 'skills/finishing-a-development-branch/SKILL.md']`, with a comment naming R122's four facts and the desktop hand check. Add `'worktree-isolation': probe_worktrees.WORKTREE_PROBE` to `PROBE_RUNS`.
- [x] **Step 3:** Run `uv run python build/cc_guide/cli.py probes --claude <path> --only worktree-isolation`, adding `--allow-old` only on the owner's word. Expected: exit 0 and one PASS row in `PROBES.md`. On DIVERGES, stop and report to the owner: it is drift for `/cc-guide verify subagents.worktrees`, not a bug to fix here. On ERROR, read the raw output that the command prints, then apply the Cost paragraph's two-run rule.
  > Deviation: one run, on the 2.1.330 Desktop app binary with --allow-old (D2): PASS, 2026-11-27.
- [x] **Step 4:** `probes.save_fixtures(<run dir>, 'worktree-isolation', FIXTURES)`. Add replay cases to `test_a_changed_behaviour_diverges_and_a_broken_run_is_an_error`, each an edit of the sightings JSON: `git_subshell` not refused (DIVERGES, fact 1), `locked_after` true (DIVERGES, fact 2), `noop` ExitWorktree not refused (DIVERGES, fact 3), `base-failed-fetch` with `has_unpushed` true (DIVERGES, fact 4), and `isolation.broken` set (ERROR).
  > Deviation: after F2 and F4 added sightings fields, the fixture was regenerated from the cached raw run through collect_worktrees and save_fixtures, with no second live run.
- [x] **Step 5:** In `build/CLAUDE.md`'s probes paragraph, name `probe_worktrees.py` as the worktree-isolation runner, and `probe_process.py` as the home of process control (from Task 1).
- [x] **Step 6:** Run the suite, `cli.py lint`, `check_conformance.py` and `bash build/run_commit_lints.sh`. Expected: all clean. Commit, with the row: `feat(cc_guide): register the worktree-isolation probe; PASS on <version>`.

---

## Completion

Run writing-plans' Plan Completion Protocol. Its ticking pass marks R52, R122 and R147–R150 `→ done <date> (plan 115): …`, or re-notes each one the gate leaves open. R122's tick needs Task 8's PASS row.
