# Claude Code Drift Automation, Stage 4 (the Notice) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show the owner what the drift check finds due, once a day, at the start of a Claude Code session in this repo, without delaying the session and without ever failing silently.

**Architecture:** `.claude/settings.json` wires a `SessionStart` pair on the `startup` matcher. `build/cc_guide/notice.sh show` runs synchronously in POSIX `sh` and prints a precomputed `{"systemMessage": …}`, at most once a day per notice. `notice.sh refresh` runs async: once the last good check is a day old, it runs `cli.py check --hook` under a time budget. A new module, `build/cc_guide/notice.py`, turns `check`'s report into the one-line notice and writes it with `last-check.json` on every exit path. Python writes everything the notice says. The shell writes only its two fixed error notices: no `uv`, and three unfinished runs in a row.

**Tech Stack:** POSIX `sh` (`build/cc_guide/notice.sh`, run by `/bin/sh` and tested under `/bin/dash` too); Python 3.13, stdlib only (`build/cc_guide/notice.py`, `cli.py`, `check.py`); pytest through `uv run`; Claude Code project settings (`.claude/settings.json`); TOML (`build/cc_guide/conformance.toml`).

**Spec:** `specs/claude-code-drift-automation-spec.md`, Stage 4 (Sequencing item 4): R9, R6.10's `check --hook`, R12.5, R12.2's R9 bullet, R12.7, and Validation items 4 and 6. Task 2 amends the spec where this plan goes beyond its wording; your human partner approves that wording at plan review.

## Global Constraints

- **The tool's writes stay in the cache.** "`check` never writes inside the repo. Its writes go under `~/.cache/agent-skills/cc-guide/` only; `--hook` also writes the notice (R9)." (R6.10)
- **`show`'s environment.** "synchronous, in POSIX `sh` with no Python, network or git. … It always exits 0 and needs only `HOME` and a minimal `PATH`: a session started from the Dock keeps `HOME` but gets launchd's `PATH`." (R9.2)
- **`refresh` is silent.** "It exits 0." "`check --hook` writes `notice.json` and `last-check.json` and prints nothing: an async hook's output would reach only Claude." (R9.3)
- **The notice.** "Exit 1: one line under 300 characters naming every due item". "A failure is never silent." "The stale backlog is not part of the notice". (R9.4)
- **Where it fires.** "It fires only in this repo (the main checkout and its worktrees) and only in Claude Code. The settings change is persistent configuration: the owner confirms it before it is committed." (R9.5) Task 8 stops for that confirmation in the execution session's conversation; a note in a ledger or a plan is not that confirmation.
- **Tests.** "Tests are offline. Fixtures … are hand-written, never copied docs text". "Module and test basenames therefore stay unique across `build/` (bare imports, no `__init__.py`), and the modules import nothing from `build/`". (R12.1) No fixture is built from a real report: its finding keys are docs headings.
- **R12.5, verbatim.** "`notice.sh show` is tested under `env -i HOME=<tmpdir> PATH=/usr/bin:/bin`, with a fixture notice under that `HOME`. It must print the notice, print nothing on a second run the same day, print a changed notice again, print only JSON, and always exit 0. A run that prints nothing at all fails, so a missing notice cannot pass as a quiet day."
- **Never commit docs text** (Sequencing constraints). Quotes from the docs appear only in session reports.
- **Every existing gate passes** (Validation 6): `check_frontmatter.py`, `check_provenance.py`, `check_snippets.py skills/` (Tier 1), the dependency-drift test, the `build/` suite, `sync_runtime_assets.py --check` with no adapter change, and `check_conformance.py`. `bash build/run_commit_lints.sh` runs all eight commit lints; run it before every commit.
- **`CLAUDE.md` stays under 200 lines** (R12.7, check `claude-md-size`). It has 194 lines at `b7beaa1`; Task 8 adds 1.
- **Test counts are deltas** (+N), never absolute pytest totals.
- **Execute in this plan's worktree**, `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice`, on branch `feat/plan-49-drift-notice`, never in the shared checkout. Start the execution session with that folder as its working directory, and not in a new app worktree: the plan commit lives only on this branch, and an app-worktree session cannot edit a second `git worktree add` worktree. Write every path out absolutely and use `git -C <worktree>` and `uv run --directory <dir>`. A Bash `cd` persists and moves the session's working directory, and guarded worktree sessions refuse compound shell, runtime-computed `$VAR` paths and pipes.
- **No live refresh while a `/cc-guide` run is in flight.** Task 9 Step 2 and Task 10 run a live `check --hook`, which can rewrite the shared `~/.cache/agent-skills/cc-guide/latest/` when the changelog head has moved (Q1 below). Before each, run `git -C /Users/lowell/Projects/agent-skills worktree list`. If a `cc-drift` or `/cc-guide` worktree there has uncommitted work, or the owner says a run is open, wait and ask.
- **Rebase before Task 2.** A drift-triage session started on 2026-10-17 (`/cc-guide` on 172 changed docs blocks) edits the guide, `build/cc_guide/baseline.json` and citation stamps, and may move the `changed` release of the `hooks.*` sections. Run `git -C /Users/lowell/Projects/agent-skills fetch origin`. If its PR has merged, rebase this branch onto `origin/main`; if it is still open, ask the owner whether to wait. Never hard-code a citation stamp: `cli.py baseline cite` sets it.
- **Python style:** single quotes, f-strings, named constants (G25), stdlib only in `build/cc_guide/`, Python 3.13.
- **Commit trailer:** the executing session's own `Co-Authored-By:` line; subagent-authored commits keep that same line. Check it with `git log -1 --format=%B`.

## Decisions

- **D1** (owner, plan review, 2026-10-17): the plan is approved as written, settled defaults DF1–DF9 included, with Task 2's spec amendments A1–A6 worded as shown. Applied in: Tasks 1–10, Task 2 (spec amendment).
- **D2** (owner, plan review, 2026-10-17): Q1 takes option (b). `rebaseline` is to refuse when `fetch.json`'s head differs from the head of the packet it settles, as `audited --to` already does for audits. That change belongs to Stage 3's tools, not this stage, so this plan logs it as a deferred item at completion. Until it lands, the Global Constraint against a live refresh during a `/cc-guide` run stays. Applied in: Planning record (Q1), Plan completion notes.

---

## Planning record

### Facts measured while planning (2026-10-17)

- **`uv run` passes SIGTERM on to its child.** Under uv 0.13.1 (Homebrew, `/opt/homebrew/bin/uv`), `kill -TERM <uv pid>` reached the Python child's handler, and uv exited with the child's status. So `refresh` stops a check past its budget by killing the `uv run` process.
- **`kill -0` polling is safe here.** `/bin/sh` (bash 3.2 in POSIX mode), `/bin/dash` and `/bin/bash` all reap a finished background job, so a `while kill -0 "$pid"` loop ends when the job ends.
- **Every tool `notice.sh` calls is on launchd's PATH.** Under `env -i PATH=/usr/bin:/bin /bin/sh`: `cat`, `date`, `mkdir`, `mv`, `rm` and `sleep` resolve in `/bin`; `sed`, `grep`, `find`, `cksum`, `dirname` and `env` in `/usr/bin`.
- **This Mac has `uv` only in `/opt/homebrew/bin`**, one of R9.3's two fallback directories, and none in `~/.local/bin`. So a "no uv" test cannot make `uv` absent without a seam (DF3).
- **The docs.** `hooks.md`, as fetched on 2026-10-17 (head 2.1.302), says a hook's `systemMessage` reaches the user on every platform, with per-event exceptions; SessionStart is not among them. It lists `startup` as the matcher value for a new session, and says `timeout` is not enforced on an `async: true` command hook. Nothing in the docs says how the Desktop app renders a SessionStart `systemMessage`, so Task 1 checks it live before anything is built.
- **The conformance register blocks the wiring as it stands.** Check `hook-scripts-executable` fails a settings command whose `.sh` script is not one of the register's hook scripts, and `[kinds.hook]` globs only `hooks/`. Task 6 adds `build/cc_guide/notice.sh` to that kind.
- **`.claude/settings.json` has no citation carrier yet.** Plan 43 left it uncited until Stage 4: "JSON holds no comments, so `build/cc_guide/notice.sh` carries the citation for the settings wiring" (R4.2).
- **Record only, not settled:** Task 1 Step 5 checks whether the `startup` matcher also fires for `claude -p` runs started in the repo, such as gate reps and Stage 5's probes. If it does, each such run would start an async check and read the notice. The check is harmless, but its result is noted for Stage 5.

### Prototype and replay

Every code block in Tasks 2–8 was replayed, in task order, onto a throwaway clone of `b7beaa1` (`~/.cache/agent-skills/scratch/plan49-proto`). A script lifted the blocks out of this file, so the replay ran this plan's text and not a copy of it. What it saw is a record, not a target:
- **Each RED came out as its step predicts.** Task 3: `KeyError: 'audit'`. Task 4: a collection error. Task 5: 5 failed on `unrecognized arguments`. Task 6: 8 failed. Task 7: 9 failed and Task 6's 8 passed. Task 8: `KeyError` on `hooks`.
- **The replay caught one regression, and the plan now carries the fix.** The first draft of Task 5 moved `default_cache()` out of `main`'s `try`, which broke the existing `test_a_crash_exits_two_never_one` (R6.9). Task 5 now keeps the cache and the clock inside the `try`, and `hook_failure` accepts a missing cache.
- **The suites.** The cc_guide suite went from 448 to 486 passed (+38, with `/bin/dash` present). The build directory's suite had 1069 passed and 13 skipped, and its only failures were the 4 `test_verify_citations.py` tests that need the gitignored `build/.scratch/`. That means no basename collides. All eight commit lints passed, and `check_conformance.py` exited 0.
- **The register glob is needed.** With Task 8's settings in place and `conformance.toml` at `b7beaa1`, `check_conformance.py` reports `hook-scripts-executable`: the SessionStart command "names no hook script in the repo". With Task 6's glob, it is clean.
- **The tests bite.** Three mutations of `notice.sh` were each caught: keeping the caller's `GIT_*` variables, dropping the budget's `kill` (the test then waited out the stand-in's 30-second sleep), and freezing `show`'s digest.
- **`baseline cite` stamped `notice.sh` `@2.1.296`**, and `cli.py lint` exited 0 with no `STALE` line for it. The full rewrite in Task 7 kept the file's execute bit and its citation line.

### Settled defaults (your human partner reviews each)

- **DF1. A display probe comes first, as a gate** (Task 1). The whole stage rests on a synchronous SessionStart hook's `systemMessage` being shown in the Desktop app, which the docs do not cover for that app. A scratch repo outside this one, with its own two-hook `startup` group, shows it or not in a new Desktop session and in an app worktree session. If it is not shown, the plan stops before Task 2. If wrong: plan review drops Task 1, and Task 10 becomes the first live check.
- **DF2. The shell counts the runs Python never finished** (Task 2: A3–A5). R9.4's "three failed checks in a row" needs state for a run that wrote nothing: one the budget killed, one `uv` could not start, or one where Python failed on import. `check --hook --run <id>` writes the run's ID into `last-check.json` last of all, and `refresh` checks for it afterwards. A run missing from it is counted in a new cache file, `unfinished`; three in a row write the shell's error notice, and a finished run clears the count. An exit 2, a setup error or a crash inside `cli.py` is not unfinished: `check --hook` writes its own error notice for those, at once, as R9.4 asks. The alternative, Python counting the failures it can see, misses the runs that never reach Python. Spec-level, so Task 2 amends the Layout, R6.10, R9.3 and R9.4.
- **DF3. Two test seams, and the budget's value** (Task 2: A4). `CC_GUIDE_UV_FALLBACK`, colon-separated like `PATH`, replaces the two fallback directories, so a test can make `uv` absent on a machine that has `/opt/homebrew/bin/uv`. `CC_GUIDE_BUDGET` replaces the budget, 300 seconds by default, so a test can stop a check in one second. A non-numeric value falls back to 300.
- **DF4. The notice's wording.** Items in this order, each only when due, joined by ` · `, after `cc-guide` and before ` → /cc-guide`:
  - `N lint violation(s)`;
  - `N docs block(s) changed (<sections>)`, where the sections are the findings' candidates, the most named first and ties by ID, cut with `+N more` to keep the line under 300 characters;
  - `N release(s) untriaged (oldest D d)`;
  - `probes due N`;
  - `audit due: <group>`.

  R9.4's own example comes out character for character (Task 4's first test). The error lines are:
  - `cc-guide · check failed: <reason> · <age> → run build/cc_guide/cli.py check` (Python);
  - `cc-guide · the drift check cannot run: no uv on PATH, in ~/.local/bin or in /opt/homebrew/bin · <age> → install uv` (shell);
  - `cc-guide · the drift check did not finish N times in a row · <age> → run build/cc_guide/cli.py check` (shell).

  `<age>` is `last good check D d ago`, or `no good check yet`.
- **DF5. `notice.sh` carries the citation for all of `.claude/settings.json`**, its model keys included: `hooks.events hooks.exit-codes hooks.configuration hooks.patterns hooks.pitfalls lean.model-routing rules.settings`. R4.2's "the settings wiring" could be read as the hooks alone, but then the file's `model`, `availableModels` and `enforceAvailableModels` keys would rest on `lean.model-routing` with no citation to flag them. A comment in `notice.sh` asks a reviewer to read the settings file before restamping. Note that a `/cc-guide files` packet holds only `notice.sh`, so the reviewer opens the settings file by hand. Spec-level, so Task 2 amends R4.2 (A6).
- **DF6. Deferred item "check's report and inputs, for Stage 4's hook and notice" (section `38-claude-code-drift-automation`), part by part.**
  - (a) needs no fix for the hook. `check --hook` writes the notice and `last-check.json` on every exit path, a setup error or a crash before `check()` returns included, and nothing in the hook reads the report file (Task 5's setup-error and crash tests). `/cc-guide` runs its own `check`.
  - (b) is fixed in `notice.sh` alone: `refresh` unsets every `GIT_*` variable before it runs the check (Task 7). `state.Source` keeps inheriting them, because the pre-commit hook runs `cli.py lint` with git's own `GIT_INDEX_FILE` set, and stripping it there would change what the lint reads.
  - (c) is fixed in `check.py`: the audit due rule runs when the fetch fails (Task 3), as R6.3 requires.
- **DF7. Two tools outside POSIX.** `date +%s` and `find -mmin` are not POSIX, but BSD (macOS) and GNU (Linux) both have them. The lock's age is the directory's own mtime, so no other process ever reads a half-written lock file.
- **DF8. The docs.** `build/CLAUDE.md` gains a paragraph on `notice.sh` and `notice.py`. The root `CLAUDE.md`'s drift-detector comment gains one line (194 → 195). The `/cc-guide` skill is not edited: the notice is not one of its modes (R12.7).
- **DF9. The live acceptance runs from this plan's worktree before the merge** (Task 10). A session started in the worktree loads the worktree's `.claude/settings.json` and `notice.sh`, while `check --hook` reads `main`'s guide and baseline. The owner starts the sessions; the executing session prepares the cache and reads the results.

### Open question for plan review

- **Q1. A session start can refetch the docs under a `/cc-guide` run.** `baseline rebaseline` re-hashes from `latest/` at whatever head `fetch.json` holds when it runs; only `baseline audited` is pinned to the packet's head (`--to`, plan 44). Today only a manual `check` refetches. With Stage 4, any new session in the repo can, through `refresh`. That happens when the hook's last good check is a day old and the changelog head has moved. If it happens between a `/cc-guide` verify and the rebaseline settle prints, the baseline records hashes for docs text the verifier never read. The window is narrow (a release mid-run, plus a session start), but nothing guards it. Options for the owner:
  - (a) Guard it in Stage 4: `check --hook` fetches into its own cache directory, so it never touches the `latest/` that packets and `rebaseline` read. This is spec-level (Layout, R6.3, R6.10), and adds a task.
  - (b) Guard it in Stage 3's tools: `settle` prints `rebaseline --head <packet head>`, and `rebaseline` refuses when `fetch.json`'s head differs, as `audited --to` already does for audits. This is a follow-up plan, logged as a deferred item.
  - (c) Accept it and document an operating rule in `build/CLAUDE.md`: finish a `/cc-guide` run's rebaseline before starting another session in the repo.

  The plan applies (c)'s rule only as the Global Constraint above, which covers this plan's own live steps. **Decided: (b) (D2).** The guard is logged as a deferred item at completion (Plan completion notes), and no task is added here.

### Coverage gaps (R4.3; listed in the completion report for the owner)

These are facts `notice.sh` and its wiring rely on that no guide section covers. The owner may extend the guide or leave each one uncovered.
- **G1.** The `startup` value of SessionStart's matcher. `hooks.configuration` says the matcher runs over the session source, but names no values.
- **G2.** A synchronous hook's `systemMessage` is shown to the user, while SessionStart's plain stdout goes only to Claude as context. `hooks.exit-codes` lists `systemMessage` as a universal field, but does not say where it is shown.
- **G3.** An `async: true` hook's output reaches only Claude, on the next turn.
- **G4.** `timeout` is not enforced on an async command hook. `hooks.handlers` gives the default timeouts only.
- **G5.** A session started from the Dock gives its hooks launchd's `PATH`. R4.3 already expected this gap.

### Plan ID

`entry_check.py` (2026-10-17) reports `next free: 49` and no collisions. `main` and `origin/main` are both `b7beaa1`. The drift spec's earlier stages are plans 38, 43 and 44; plan 45 (verifier recall) was reverted.

### CLAUDE.md line budget

194 lines at `b7beaa1`, and 195 after Task 8, under the 200-line check.

### File contract (shell and Python)

Every implementer reads this table. Its home in code is `notice.py`'s module docstring (Task 4). The directory is `~/.cache/agent-skills/cc-guide/`: `state.default_cache()` in Python, and `"${HOME:-}/.cache/agent-skills/cc-guide"` in `notice.sh`.

| File | Written by | Read by | Content |
|---|---|---|---|
| `notice.json` | `notice.write_notice` (`check --hook`); `fail_notice` in `refresh`, for its two errors only | `show` | Empty when nothing is due; otherwise one ASCII line, `{"systemMessage": "…"}`, with `·` and `→` as `·` and `→` escapes |
| `notice.digest` | the same two writers, always **after** `notice.json` | `show`, **before** it reads `notice.json` | One line: the sha256 hex of `notice.json`'s bytes from Python, `cksum`'s checksum from the shell. It changes whenever the notice does |
| `notice-shown` | `show` alone | `show` | One line, `YYYY-MM-DD <digest>`: the day and the notice last printed |
| `last-check.json` | `notice.record_check` alone, last of all | `refresh`, through `sed` and `grep`, not a JSON parser | `json.dumps(…, indent=1)` of `run`, `finished_at`, `exit`, `ok_at`, `ok_epoch`. `refresh` reads the line ` "run": "<id>",` and the line ` "ok_epoch": <seconds>` (the last key, or `null`) |
| `unfinished` | `refresh` alone | `refresh` | One decimal count of unfinished runs in a row |
| `lock/` | `refresh` (`mkdir`) | `refresh` | An empty directory. Its mtime is its age |

Every file is replaced by renaming a temporary file over it: `os.replace` in Python, `mv -f` in the shell. Because the write order and the read order are reversed, a `show` that races a writer prints the new notice with the old digest, at worst. The next session then shows that notice once more; no notice is ever skipped.

---

### Task 1: The display probe (DF1; owner gate)

**Files:** none in the repo. A scratch repo at `/tmp/cc-notice-probe/` and a log at `/tmp/cc-notice-probe-async.log`.

**Interfaces:**
- Consumes: nothing.
- Produces: the gate's result, recorded under this task as a `> Result:` line. Every later task depends on a pass.

- [ ] **Step 1: Build the probe repo.** Create `/tmp/cc-notice-probe/probe-show.sh`:

```sh
#!/bin/sh
printf '%s\n' '{"systemMessage": "cc-notice-probe: a synchronous SessionStart hook on startup reached you"}'
```

Create `/tmp/cc-notice-probe/probe-async.sh`:

```sh
#!/bin/sh
date '+%Y-%m-%dT%H:%M:%S' >> /tmp/cc-notice-probe-async.log
printf '%s\n' '{"systemMessage": "cc-notice-probe: async output, which should NOT be shown to you"}'
```

Create `/tmp/cc-notice-probe/.claude/settings.json`:

```json
{
    "hooks": {
        "SessionStart": [
            {
                "matcher": "startup",
                "hooks": [
                    { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/probe-show.sh" },
                    { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/probe-async.sh", "async": true }
                ]
            }
        ]
    }
}
```

Then run each:

```bash
chmod +x /tmp/cc-notice-probe/probe-show.sh /tmp/cc-notice-probe/probe-async.sh
git -C /tmp/cc-notice-probe init -q
git -C /tmp/cc-notice-probe add -A
git -C /tmp/cc-notice-probe -c user.name=Probe -c user.email=probe@example.invalid -c commit.gpgsign=false commit -qm probe
```

- [ ] **Step 2: The owner starts a new Desktop Code session in `/tmp/cc-notice-probe`, without a worktree.** Ask in the conversation, and wait for the answer. The owner reports:
  - whether `cc-notice-probe: a synchronous SessionStart hook on startup reached you` appeared, and where;
  - whether the async line appeared. It should not.

  The app may ask the owner to trust the folder first.
- [ ] **Step 3: The owner starts a second new Desktop session on the same repo, in an app worktree.** Ask, wait, and record the same two observations.
- [ ] **Step 4: Confirm the async hook ran.** Run `cat /tmp/cc-notice-probe-async.log`: it holds one line per session started in Steps 2 and 3.
- [ ] **Step 5 (record only): does `startup` fire under `claude -p`?** Running it needs `/tmp/cc-notice-probe` as the working directory, and a Bash `cd` there would move this session. So ask the owner to run these from a terminal, or to skip the step:

```bash
cd /tmp/cc-notice-probe
```

```bash
claude -p --tools "" "Reply with the word OK."
```

Then run `cat /tmp/cc-notice-probe-async.log`. A new line means `startup` fires under `-p`. Record the answer and `claude --version` either way; nothing in this plan depends on it.
- [ ] **Step 6: The gate.** If the synchronous line appeared in both Step 2 and Step 3, record `> Result: PASS (<date>, Claude Code <version>)`, and go on. Otherwise, stop and tell the owner that spec Decision 8's premise fails in the Desktop app, quoting what each session showed. Do not start Task 2: the trigger needs a redesign, which is the owner's call.
- [ ] **Step 7: Clean up**, once the owner has closed or archived the probe sessions:

```bash
rm -rf /tmp/cc-notice-probe /tmp/cc-notice-probe-async.log
```

If an app worktree of the probe repo remains, `git worktree list` from a terminal shows it; remove it through the app.

---

### Task 2: Spec amendments (DF2, DF3, DF5)

**Files:**
- Modify: `specs/claude-code-drift-automation-spec.md` (Layout, R4.2, R6.10, R9.3, R9.4)

Each edit is tagged `(owner, plan 49, 2026-10-17)`; the status line stays untouched. Your human partner approves this wording at plan review. Make each edit with an exact replace of the block shown.

- [ ] **Step 1 (A1): the Layout names `notice.py`.** Replace:

```text
  - `manifest.toml` and `baseline.json` (R2), `PROBES.md` (R10) and
    `notice.sh` (R9);
```

with:

```text
  - `manifest.toml` and `baseline.json` (R2), `PROBES.md` (R10),
    `notice.sh` (R9), and `notice.py`, which writes the notice for
    `check --hook` (owner, plan 49, 2026-10-17);
```

- [ ] **Step 2 (A2): the Layout's cache files.** Replace:

```text
  - `notice.json` and its digest, `notice-shown`, `last-check.json` and the
    `lock/` directory (R9);
```

with:

```text
  - `notice.json` and its digest `notice.digest`, `notice-shown`,
    `last-check.json`, `unfinished` and the `lock/` directory (R9);
    `notice.py`'s docstring says which side writes each, and in what order
    (owner, plan 49, 2026-10-17);
```

- [ ] **Step 3 (A3): R6.10's `--hook` and `--run`.** Replace:

```text
R6.10 `check` never writes inside the repo. Its writes go under
`~/.cache/agent-skills/cc-guide/` only; `--hook` also writes the notice (R9).
```

with:

```text
R6.10 `check` never writes inside the repo. Its writes go under
`~/.cache/agent-skills/cc-guide/` only; `--hook` also writes the notice (R9).
`--hook` writes the notice and `last-check.json` on every exit, a setup error
or a crash included, and `--run <id>`, accepted only with `--hook`, records
the run's ID in `last-check.json` (owner, plan 49, 2026-10-17).
```

- [ ] **Step 4 (A4): R9.3's run ID, budget, `GIT_*` rule, unfinished runs and test seams.** Replace:

```text
- Otherwise it looks for `uv` on PATH, then in `~/.local/bin` and
  `/opt/homebrew/bin`, and runs `cli.py check --hook` through
  `uv run --python 3.13` under an overall time budget, since `timeout` is not
  enforced on async hooks. It locates `cli.py` from its own directory, never
  from the hook's working directory: a relative path would repeat drift #3's
  class of bug. When `uv` is missing, it writes a fixed error notice itself.
  It exits 0.
```

with:

```text
- Otherwise it looks for `uv` on PATH, then in `~/.local/bin` and
  `/opt/homebrew/bin`, and runs `cli.py check --hook --run <id>` through
  `uv run --python 3.13` under an overall time budget of 300 seconds, since
  `timeout` is not enforced on async hooks. It locates `cli.py` from its own
  directory, never from the hook's working directory: a relative path would
  repeat drift #3's class of bug. It runs the check with none of its caller's
  `GIT_*` variables. When `uv` is missing, it writes a fixed error notice
  itself. It exits 0 (owner, plan 49, 2026-10-17: the run ID, the budget's
  value and the `GIT_*` rule).
- A run that leaves no `last-check.json` naming its ID is unfinished: the
  budget stopped it, `uv` failed, or Python failed before `check --hook`
  could write. `refresh` counts unfinished runs in `unfinished`, and a
  finished run clears the count. Two variables exist for the tests:
  `CC_GUIDE_UV_FALLBACK`, a colon-separated list that replaces the two
  fallback directories, and `CC_GUIDE_BUDGET`, the budget in seconds
  (owner, plan 49, 2026-10-17).
```

- [ ] **Step 5 (A5): R9.4's error line.** Replace:

```text
- Exit 2, no `uv`, or three failed checks in a row: an error line with the age
  of the last good check. A failure is never silent.
```

with:

```text
- Exit 2, no `uv`, or three unfinished runs in a row (R9.3): an error line
  with the age of the last good check. `check --hook` writes it for an exit 2,
  a setup error or a crash; `refresh` writes it for the other two. A failure
  is never silent (owner, plan 49, 2026-10-17).
```

- [ ] **Step 6 (A6): R4.2's carrier for the settings file.** Replace:

```text
  JSON holds no comments, so `build/cc_guide/notice.sh` carries the citation
  for the settings wiring.
```

with:

```text
  JSON holds no comments, so `build/cc_guide/notice.sh` carries the citation
  for `.claude/settings.json`, its model keys included; a review of that
  citation reads the settings file too (owner, plan 49, 2026-10-17).
```

- [ ] **Step 7: Check and commit.** Run `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice --python 3.13 python build/cc_guide/cli.py lint`: exit 0, since the spec is outside the citation scan. Run `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice diff --stat`: only the spec changed, with six hunks. Run `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/run_commit_lints.sh`, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice add specs/claude-code-drift-automation-spec.md
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice commit -m "docs(specs): amend drift Stage 4 for the run handshake, unfinished runs and the settings carrier"
```

---

### Task 3: The audit due rule runs when the fetch fails (DF6 part c)

**Files:**
- Modify: `build/cc_guide/check.py` (`check()`'s `due` block, near line 342; `summary()`'s audit line, near line 391)
- Test: `build/cc_guide/test_check.py` (a new test after `test_a_network_failure_exits_two_and_is_reported`, near line 430)

**Interfaces:**
- Consumes: `check.check(...)`, `check.summary(report, path)`, and `test_check.py`'s `run_check`, `serving`, `drift_repo` and `MANIFEST`.
- Produces: `report['due']['audit']` on every `check` that reaches the due rules, a failed fetch included. Task 4's `due_message` reads it.

- [ ] **Step 1: Record the baselines.** Run each and write the counts down:

```bash
uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 --with pytest python -m pytest -q
uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q
```

The second is the build directory's suite. A fresh worktree lacks the gitignored `build/.scratch/`, so `test_verify_citations.py`'s ground-truth tests fail or skip there; note which, and compare against them later.

- [ ] **Step 2: Write the failing test.** In `build/cc_guide/test_check.py`, after `test_a_network_failure_exits_two_and_is_reported`, insert:

```python
def test_a_failed_fetch_still_runs_the_audit_due_rule(tmp_path, docs_dir):
    '''R6.3: the due rules always run. The audit clock needs only the
    baseline, so a failed changelog fetch still reports the audit beside its
    exit 2, and the summary prints it.'''
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    code, report, path = run_check(repo, tmp_path / 'cache', today=date(2026, 10, 4),
                                   fetch=serving(docs_dir, fail={MANIFEST.sources['changelog']}))
    assert (code, report['due']['audit']['due'], report['due']['audit']['group']) == (2, True, 'alpha')
    assert 'audit: alpha due from 2026-10-02, due' in check.summary(report, path)
```

- [ ] **Step 3: Run it and watch it fail.**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_check.py -k audit_due_rule`
Expected: FAIL with `KeyError: 'audit'`, since `report['due']` holds only `lint` when the fetch fails.

- [ ] **Step 4: Run the audit rule outside the docs branch.** In `build/cc_guide/check.py`, replace:

```python
        due.update({'blocks': len(findings),
                    'changelog': due_changelog(state, releases, manifest.cadence['changelog_days'], today),
                    'probes': due_probes(manifest, rows, releases[0].label, manifest.cadence['probe_days'], today),
                    'audit': due_audit(manifest, state, manifest.cadence['audit_days'], today)})
    report['due'] = due
```

with:

```python
        due.update({'blocks': len(findings),
                    'changelog': due_changelog(state, releases, manifest.cadence['changelog_days'], today),
                    'probes': due_probes(manifest, rows, releases[0].label, manifest.cadence['probe_days'], today)})
    # R6.3: the due rules always run. The audit clock needs only the baseline, so a failed fetch keeps it.
    due['audit'] = due_audit(manifest, state, manifest.cadence['audit_days'], today)
    report['due'] = due
```

Then, in `summary()`, replace:

```python
        lines.append('probes: none due' if not due['probes'] else
                     'probes: ' + '; '.join(f"{p['probe']} ({p['why']})" for p in due['probes']))
        audit = due['audit']
        lines.append(f"audit: {audit['group']} due from {audit['due_from']}" + (', due' if audit['due'] else ''))
    lines += [f'error: {e}' for e in report['errors']]
```

with:

```python
        lines.append('probes: none due' if not due['probes'] else
                     'probes: ' + '; '.join(f"{p['probe']} ({p['why']})" for p in due['probes']))
    audit = due['audit']
    lines.append(f"audit: {audit['group']} due from {audit['due_from']}" + (', due' if audit['due'] else ''))
    lines += [f'error: {e}' for e in report['errors']]
```

The `due` keys keep their order (`lint`, `blocks`, `changelog`, `probes`, `audit`), and the summary prints the audit line in the same place as before.

- [ ] **Step 4b: Correct the module docstring.** In `build/cc_guide/check.py`, replace:

```python
and the files citing it, and report what is due (drift spec R6). `--hook`
(R6.10) is Stage 4's; packets.py builds R6.11's packets from these parts.'''
```

with:

```python
and the files citing it, and report what is due (drift spec R6). For
`--hook` (R6.10), notice.py turns the report into the session-start notice;
packets.py builds R6.11's packets from these parts.'''
```

- [ ] **Step 5: Run the suite.**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: the baseline +1, all passing.

- [ ] **Step 6: Commit.** Run `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/run_commit_lints.sh`, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice add build/cc_guide/check.py build/cc_guide/test_check.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice commit -m "fix(cc_guide): run the audit due rule when the fetch fails"
```

---

### Task 4: `notice.py`, the notice's text and the files it leaves

**Files:**
- Create: `build/cc_guide/notice.py`
- Test: `build/cc_guide/test_notice.py` (new)

**Interfaces:**
- Consumes: a `check` report's `due` (`lint`, `blocks`, `changelog`, `probes`, `audit`), its `findings` (each with `candidates`) and its `errors`.
- Produces, for Tasks 5 and 7:
  - constants `NOTICE = 'notice.json'`, `DIGEST = 'notice.digest'`, `LAST_CHECK = 'last-check.json'`, `LIMIT = 300` and `DAY = 86400`;
  - `due_message(report: dict, today: date) -> str | None`;
  - `error_message(reason: str, ok_epoch: int | None, now_epoch: int) -> str`;
  - `write_notice(cache: Path, message: str | None) -> None`;
  - `read_last_check(cache: Path) -> dict | None`;
  - `last_ok(cache: Path) -> int | None`;
  - `record_check(cache: Path, code: int, now: datetime, run: str | None) -> dict`;
  - `after_check(cache: Path, code: int, report: dict, now: datetime, today: date, run: str | None) -> None`;
  - `after_failure(cache: Path, reason: str, now: datetime, run: str | None) -> None`.

- [ ] **Step 1: Write the failing tests.** Create `build/cc_guide/test_notice.py`:

```python
'''Tests for notice.py: the notice's line for each outcome (drift spec R9.4,
R12.2's R9 bullet) and the files check --hook leaves for notice.sh.'''
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone

import notice

NOW = datetime(2026, 10, 17, 9, 0, tzinfo=timezone.utc)
EPOCH = int(NOW.timestamp())
TODAY = date(2026, 10, 17)


def report(findings=(), lint=0, changelog=None, probes=(), audit=None):
    '''A report holding what due_message reads: `due`, and one block finding
    per tuple of candidate sections.'''
    due = {'lint': lint, 'blocks': len(findings), 'changelog': changelog, 'probes': list(probes),
           'audit': audit or {'group': 'alpha', 'due': False}}
    return {'due': due, 'findings': {'alpha': [{'kind': 'changed', 'candidates': list(c)} for c in findings]},
            'errors': []}


def test_the_spec_example_line():
    '''R9.4's own example, item for item.'''
    got = notice.due_message(report(
        findings=[('hooks.events',), ('rules.settings',)],
        changelog={'releases': 9, 'oldest': '2.1.300', 'oldest_date': '2026-10-09', 'due': True},
        probes=[{'probe': 'p1'}, {'probe': 'p2'}],
        audit={'group': 'hooks', 'due': True}), TODAY)
    assert got == ('cc-guide · 2 docs blocks changed (hooks.events, rules.settings) · '
                   '9 releases untriaged (oldest 8 d) · probes due 2 · audit due: hooks → /cc-guide')


def test_only_due_items_are_named_and_lint_comes_first():
    got = notice.due_message(report(
        lint=1, changelog={'releases': 3, 'oldest': '2.1.300', 'oldest_date': '2026-10-15', 'due': False}), TODAY)
    assert got == 'cc-guide · 1 lint violation → /cc-guide'


def test_nothing_due_is_no_message():
    assert notice.due_message(report(), TODAY) is None


def test_sections_are_named_most_often_first_then_by_id():
    got = notice.due_message(report(findings=[('b.two', 'a.one'), ('b.two',), ('c.three',)]), TODAY)
    assert got == 'cc-guide · 3 docs blocks changed (b.two, a.one, c.three) → /cc-guide'


def test_a_report_at_todays_scale_stays_under_the_limit_and_counts_what_it_left_out():
    '''About 170 findings over 38 sections, as check reported on 2026-10-17.'''
    sections = [f'group{g}.section-{s:02d}' for g in range(6) for s in range(7)][:38]
    findings = [tuple(sections[(i + k) % 38] for k in range(3)) for i in range(172)]
    got = notice.due_message(report(
        findings=findings, lint=2,
        changelog={'releases': 4, 'oldest': '2.1.299', 'oldest_date': '2026-10-14', 'due': True},
        audit={'group': 'overview', 'due': True}), date(2026, 10, 21))
    assert len(got) < notice.LIMIT
    assert got.startswith('cc-guide · 2 lint violations · 172 docs blocks changed (')
    assert got.endswith(' more) · 4 releases untriaged (oldest 7 d) · audit due: overview → /cc-guide')
    named = re.search(r'changed \((.*), \+(\d+) more\)', got)
    assert len(named.group(1).split(', ')) + int(named.group(2)) == 38


def test_the_error_line_names_the_reason_and_the_age_of_the_last_good_check():
    assert notice.error_message('https://example.invalid/changelog.md: timed out',
                                EPOCH - 3 * notice.DAY - 5, EPOCH) == (
        'cc-guide · check failed: https://example.invalid/changelog.md: timed out · '
        'last good check 3 d ago → run build/cc_guide/cli.py check')
    assert notice.error_message('boom', None, EPOCH) == (
        'cc-guide · check failed: boom · no good check yet → run build/cc_guide/cli.py check')


def test_a_long_reason_is_cut_to_keep_the_line_under_the_limit():
    got = notice.error_message('x' * 1000 + '\nsecond line', None, EPOCH)
    assert len(got) == notice.LIMIT - 1
    assert '\n' not in got
    assert '… · no good check yet' in got


def test_the_notice_is_one_ascii_json_line_written_before_its_digest(tmp_path, monkeypatch):
    order = []
    real = notice.os.replace

    def replace(src, dst):
        order.append(dst.name)
        real(src, dst)
    monkeypatch.setattr(notice.os, 'replace', replace)
    notice.write_notice(tmp_path, 'cc-guide · x → /cc-guide')
    text = (tmp_path / notice.NOTICE).read_text(encoding='utf-8')
    assert text.isascii() and text.count('\n') == 1
    assert json.loads(text) == {'systemMessage': 'cc-guide · x → /cc-guide'}
    assert (tmp_path / notice.DIGEST).read_text() == hashlib.sha256(text.encode()).hexdigest() + '\n'
    assert order == [notice.NOTICE, notice.DIGEST]
    assert sorted(p.name for p in tmp_path.iterdir()) == [notice.DIGEST, notice.NOTICE]


def test_nothing_due_writes_an_empty_notice(tmp_path):
    notice.write_notice(tmp_path, None)
    assert (tmp_path / notice.NOTICE).read_text() == ''
    assert (tmp_path / notice.DIGEST).read_text() == hashlib.sha256(b'').hexdigest() + '\n'


def test_a_good_check_records_itself_and_a_failed_one_keeps_the_last_good_check(tmp_path):
    first = notice.record_check(tmp_path, 1, NOW, 'r1')
    assert (first['run'], first['exit'], first['ok_epoch']) == ('r1', 1, EPOCH)
    failed = notice.record_check(tmp_path, 2, NOW + timedelta(hours=30), 'r2')
    assert (failed['run'], failed['exit'], failed['ok_at'], failed['ok_epoch']) == ('r2', 2, first['ok_at'], EPOCH)
    assert json.loads((tmp_path / notice.LAST_CHECK).read_text()) == failed
    assert notice.last_ok(tmp_path) == EPOCH


def test_a_first_failure_records_no_good_check(tmp_path):
    record = notice.record_check(tmp_path, 2, NOW, None)
    assert (record['ok_at'], record['ok_epoch'], notice.last_ok(tmp_path)) == (None, None, None)


def test_the_record_keeps_the_two_lines_notice_sh_reads(tmp_path):
    '''notice.sh reads last-check.json with sed and grep, not a JSON parser:
    ok_epoch alone on its line, and the run ID as "run": "<id>".'''
    notice.record_check(tmp_path, 0, NOW, '123.456')
    text = (tmp_path / notice.LAST_CHECK).read_text()
    assert re.search(rf'^ *"ok_epoch": {EPOCH},?$', text, re.M)
    assert '"run": "123.456"' in text


def test_after_check_writes_the_notice_for_each_exit_then_the_record(tmp_path):
    due = report(changelog={'releases': 2, 'oldest': '2.1.901', 'oldest_date': '2026-10-10', 'due': True})
    notice.after_check(tmp_path, 1, due, NOW, TODAY, 'r1')
    assert json.loads((tmp_path / notice.NOTICE).read_text())['systemMessage'] == (
        'cc-guide · 2 releases untriaged (oldest 7 d) → /cc-guide')
    notice.after_check(tmp_path, 0, report(), NOW, TODAY, 'r2')
    assert (tmp_path / notice.NOTICE).read_text() == ''
    failing = dict(report(), errors=['https://example.invalid/llms.txt: HTTP 503'])
    notice.after_check(tmp_path, 2, failing, NOW + timedelta(days=2), date(2026, 10, 19), 'r3')
    assert json.loads((tmp_path / notice.NOTICE).read_text())['systemMessage'] == (
        'cc-guide · check failed: https://example.invalid/llms.txt: HTTP 503 · '
        'last good check 2 d ago → run build/cc_guide/cli.py check')
    assert notice.read_last_check(tmp_path)['run'] == 'r3'


def test_after_failure_writes_the_error_line_and_records_an_exit_two(tmp_path):
    notice.after_failure(tmp_path, 'RuntimeError: boom', NOW, 'r9')
    assert json.loads((tmp_path / notice.NOTICE).read_text())['systemMessage'] == (
        'cc-guide · check failed: RuntimeError: boom · no good check yet'
        ' → run build/cc_guide/cli.py check')
    record = notice.read_last_check(tmp_path)
    assert (record['run'], record['exit']) == ('r9', 2)
```

- [ ] **Step 2: Run them and watch them fail.**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_notice.py`
Expected: a collection error, `ModuleNotFoundError: No module named 'notice'`.

- [ ] **Step 3: Write the module.** Create `build/cc_guide/notice.py`:

```python
'''The session-start notice (drift spec R9): the line `check --hook` leaves
for notice.sh to show, and the record it leaves for notice.sh refresh.

The cache files the two languages share, under ~/.cache/agent-skills/cc-guide/:
- notice.json: empty when nothing is due, else one ASCII JSON line holding
  {"systemMessage": ...}. Written here, or by refresh for its own two errors;
  show prints it as it stands.
- notice.digest: one line that changes whenever notice.json does: a sha256
  here, cksum's checksum from refresh. Always written after notice.json, and
  show reads it before notice.json, so a notice replaced between the two
  reads is shown once more, never skipped.
- notice-shown: "<YYYY-MM-DD> <digest>", written by show alone.
- last-check.json: written here alone, last of all, so a run ID in it means
  the notice is in place. refresh reads two of its lines without a JSON
  parser: ` "run": "<id>",` and ` "ok_epoch": <seconds>`, the last good check.
- unfinished: refresh's count of runs in a row that never wrote last-check.json.
- lock/: refresh's lock directory.
Each file is replaced by renaming a temporary file over it, in both
languages, so no reader sees a partial file.'''
import hashlib
import json
import os
from datetime import date, datetime
from pathlib import Path

NOTICE = 'notice.json'
DIGEST = 'notice.digest'
LAST_CHECK = 'last-check.json'
LIMIT = 300                 # R9.4: a notice line stays under 300 characters
DAY = 86400                 # seconds; notice.sh measures a day the same way
HEAD = 'cc-guide'
SEP = ' · '
TO_SKILL = ' → /cc-guide'
TO_CHECK = ' → run build/cc_guide/cli.py check'


def plural(count: int, noun: str) -> str:
    return f'{count} {noun}' + ('' if count == 1 else 's')


def named_sections(report: dict) -> list[str]:
    '''The candidate sections of the report's block findings, the most named
    first, ties by ID.'''
    counts: dict[str, int] = {}
    for findings in report.get('findings', {}).values():
        for finding in findings:
            for sid in finding['candidates']:
                counts[sid] = counts.get(sid, 0) + 1
    return sorted(counts, key=lambda sid: (-counts[sid], sid))


def fitted(names: list[str], room: int) -> str:
    '''As many of names as fit in room characters, comma-separated, with
    "+N more" for the rest.'''
    for shown in range(len(names), 0, -1):
        rest = len(names) - shown
        text = ', '.join(names[:shown]) + (f', +{rest} more' if rest else '')
        if len(text) <= room:
            return text
    return f'+{len(names)} more'


def due_message(report: dict, today: date) -> str | None:
    '''R9.4: one line under LIMIT characters naming every due item, or None
    when nothing is due. The block item names its candidate sections as far
    as the line has room.'''
    due = report['due']
    before, after = [], []
    if due.get('lint'):
        before.append(plural(due['lint'], 'lint violation'))
    batch = due.get('changelog') or {}
    if batch.get('due'):
        days = (today - date.fromisoformat(batch['oldest_date'])).days
        after.append(f"{plural(batch['releases'], 'release')} untriaged (oldest {days} d)")
    if due.get('probes'):
        after.append(f"probes due {len(due['probes'])}")
    audit = due.get('audit') or {}
    if audit.get('due'):
        after.append(f"audit due: {audit['group']}")
    blocks = due.get('blocks') or 0
    if not (before or blocks or after):
        return None
    if blocks:
        words = f"{plural(blocks, 'docs block')} changed"
        frame = SEP.join([HEAD, *before, f'{words} ()', *after]) + TO_SKILL
        before.append(f'{words} ({fitted(named_sections(report), LIMIT - 1 - len(frame))})')
    return SEP.join([HEAD, *before, *after]) + TO_SKILL


def age_words(ok_epoch: int | None, now_epoch: int) -> str:
    '''The age of the last good check, in whole days, as notice.sh words it.'''
    if ok_epoch is None:
        return 'no good check yet'
    return f'last good check {(now_epoch - ok_epoch) // DAY} d ago'


def error_message(reason: str, ok_epoch: int | None, now_epoch: int) -> str:
    '''R9.4: an error line with the age of the last good check, the reason
    flattened to one line and cut to keep the line under LIMIT characters.'''
    reason = ' '.join(reason.split())
    age = age_words(ok_epoch, now_epoch)
    room = LIMIT - 1 - len(f'{HEAD}{SEP}check failed: {SEP}{age}{TO_CHECK}')
    if len(reason) > room:
        reason = reason[:room - 1] + '…'
    return f'{HEAD}{SEP}check failed: {reason}{SEP}{age}{TO_CHECK}'


def replace(path: Path, text: str) -> None:
    '''Write text to path by renaming a temporary file over it.'''
    tmp = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    tmp.write_text(text, encoding='utf-8')
    os.replace(tmp, path)


def write_notice(cache: Path, message: str | None) -> None:
    '''notice.json, then its digest: one ASCII JSON line holding the message
    as systemMessage, or an empty file when nothing is due.'''
    cache.mkdir(parents=True, exist_ok=True)
    text = '' if message is None else json.dumps({'systemMessage': message}) + '\n'
    replace(cache / NOTICE, text)
    replace(cache / DIGEST, hashlib.sha256(text.encode('utf-8')).hexdigest() + '\n')


def read_last_check(cache: Path) -> dict | None:
    '''The record check --hook last wrote, or None when there is none or it
    does not parse.'''
    try:
        data = json.loads((cache / LAST_CHECK).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def last_ok(cache: Path) -> int | None:
    '''The epoch second of the last good check, or None.'''
    value = (read_last_check(cache) or {}).get('ok_epoch')
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def record_check(cache: Path, code: int, now: datetime, run: str | None) -> dict:
    '''last-check.json: this run's ID and exit, and the last good check. An
    exit 0 or 1 is a good check; an exit 2 carries the previous one over.'''
    previous = read_last_check(cache) or {}
    good = code in (0, 1)
    stamp = now.isoformat(timespec='seconds')
    record = {'run': run, 'finished_at': stamp, 'exit': code,
              'ok_at': stamp if good else previous.get('ok_at'),
              'ok_epoch': int(now.timestamp()) if good else last_ok(cache)}
    cache.mkdir(parents=True, exist_ok=True)
    replace(cache / LAST_CHECK, json.dumps(record, indent=1) + '\n')
    return record


def after_check(cache: Path, code: int, report: dict, now: datetime, today: date, run: str | None) -> None:
    '''check --hook once check() returned: the notice for its exit, then the
    record (R9.3, R9.4).'''
    if code == 2:
        reason = report['errors'][0] if report.get('errors') else 'check exited 2'
        message = error_message(reason, last_ok(cache), int(now.timestamp()))
    else:
        message = due_message(report, today) if code == 1 else None
    write_notice(cache, message)
    record_check(cache, code, now, run)


def after_failure(cache: Path, reason: str, now: datetime, run: str | None) -> None:
    '''check --hook on a setup error or a crash: the error line, then the
    record, as for an exit 2.'''
    write_notice(cache, error_message(reason, last_ok(cache), int(now.timestamp())))
    record_check(cache, 2, now, run)
```

- [ ] **Step 4: Run the tests.**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_notice.py`
Expected: 14 passed. Then the whole cc_guide suite: the baseline +15.

- [ ] **Step 5: Commit.** Run `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/run_commit_lints.sh`, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice add build/cc_guide/notice.py build/cc_guide/test_notice.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice commit -m "feat(cc_guide): write the session-start notice and its record"
```

---

### Task 5: `check --hook` (R6.10)

**Files:**
- Modify: `build/cc_guide/cli.py` (the docstring, lines 2–4 and 17–21; the imports; `parser()`'s `check` block, lines 114–118; `run_check`, lines 208–212; `main`, lines 343–365)
- Test: `build/cc_guide/test_cli.py` (imports; new tests after `test_check_reads_main_unless_told_otherwise`, near line 108)

**Interfaces:**
- Consumes: from Task 4, `notice.after_check(cache, code, report, now, today, run)`, `notice.after_failure(cache, reason, now, run)`, `notice.read_last_check`, `notice.record_check`, `notice.NOTICE` and `notice.LAST_CHECK`.
- Produces: `cli.py check --hook [--run ID]`, which prints nothing on any exit and leaves `notice.json`, `notice.digest` and `last-check.json` in the cache. `--run` without `--hook` is a setup error, exit 2. Task 7's `refresh` runs `check --hook --run <id>`.

- [ ] **Step 1: Write the failing tests.** In `build/cc_guide/test_cli.py`, change the imports from:

```python
import json
from datetime import date, datetime

import pytest

import baseline
import cli
import state
```

to:

```python
import json
from datetime import date, datetime, timedelta, timezone

import pytest

import baseline
import cli
import notice
import state
```

After `test_check_reads_main_unless_told_otherwise`, insert:

```python
HOOK_NOW = datetime(2026, 9, 27, 9, 0, tzinfo=timezone.utc)


def hook(cache, *argv, today=date(2026, 9, 27)):
    '''check --hook as notice.sh refresh runs it, at HOOK_NOW.'''
    return cli.main(['--cache', str(cache), 'check', '--hook', *argv], today=today, now=HOOK_NOW)


def shown(cache):
    return json.loads((cache / notice.NOTICE).read_text())['systemMessage']


def test_check_hook_prints_nothing_and_leaves_the_notice_then_the_record(world, capsys):
    repo, cache, docs = world
    assert hook(cache, '--run', 'r1', '--docs', str(docs)) == 1
    assert capsys.readouterr() == ('', '')
    assert shown(cache) == 'cc-guide · 2 releases untriaged (oldest 7 d) → /cc-guide'
    record = notice.read_last_check(cache)
    assert (record['run'], record['exit'], record['ok_epoch']) == ('r1', 1, int(HOOK_NOW.timestamp()))
    assert hook(cache, '--run', 'r2', '--docs', str(docs), today=date(2026, 9, 10)) == 0
    assert capsys.readouterr() == ('', '')
    assert (cache / notice.NOTICE).read_text() == ''
    assert git(repo, 'status', '--porcelain') == ''


def test_check_hook_turns_a_setup_error_into_the_error_line(tmp_path, docs_dir, monkeypatch, capsys):
    '''A setup error raised before check() returns still leaves the notice
    and the record, so the hook never shows a stale report's outcome
    (deferred item "check's report and inputs", part a).'''
    repo = fixture_repo(tmp_path / 'repo', {GUIDE_PATH: guide_text()})
    monkeypatch.setattr(cli, 'REPO', repo)
    cache = tmp_path / 'cache'
    earlier = HOOK_NOW - timedelta(days=3)
    notice.record_check(cache, 0, earlier, 'r0')
    assert hook(cache, '--run', 'r1', '--docs', str(docs_dir)) == 2
    assert capsys.readouterr() == ('', '')
    assert shown(cache) == (f'cc-guide · check failed: {state.MANIFEST}: not found in main · '
                            'last good check 3 d ago → run build/cc_guide/cli.py check')
    record = notice.read_last_check(cache)
    assert (record['run'], record['exit'], record['ok_epoch']) == ('r1', 2, int(earlier.timestamp()))


def test_check_hook_turns_a_crash_into_the_error_line(world, monkeypatch, capsys):
    _, cache, docs = world

    def boom(*args, **kwargs):
        raise RuntimeError('boom')
    monkeypatch.setattr(cli, 'check', boom)
    assert hook(cache, '--run', 'r1', '--docs', str(docs)) == 2
    assert capsys.readouterr() == ('', '')
    assert shown(cache) == ('cc-guide · check failed: RuntimeError: boom · no good check yet'
                            ' → run build/cc_guide/cli.py check')
    assert notice.read_last_check(cache)['run'] == 'r1'


def test_run_goes_with_hook(world, capsys):
    _, cache, docs = world
    assert main(cache, 'check', '--run', 'r1', '--docs', str(docs)) == 2
    assert capsys.readouterr() == ('', 'cc-guide: --run goes with --hook\n')


def test_check_hook_writes_only_its_cache_files(world):
    '''R6.10: the report, the notice, its digest and the record, all in the
    cache, and nothing in the repo.'''
    repo, cache, docs = world

    def files():
        return {p.relative_to(cache).as_posix() for p in cache.rglob('*') if p.is_file()}
    before = files()
    hook(cache, '--run', 'r1', '--docs', str(docs))
    added = files() - before
    reports = {name for name in added if name.startswith('reports/')}
    assert len(reports) == 1
    assert sorted(added - reports) == [notice.LAST_CHECK, notice.DIGEST, notice.NOTICE]
    assert git(repo, 'status', '--porcelain') == ''
```

- [ ] **Step 2: Run them and watch them fail.**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_cli.py -k "hook or run_goes"`
Expected: 5 failed, each with argparse's `unrecognized arguments: --hook` (or `--run`) and `SystemExit: 2`.

- [ ] **Step 3: Implement.** In `build/cc_guide/cli.py`:

Replace the docstring's third line:

```python
(Stages 1 to 3 of specs/claude-code-drift-automation-spec.md).
```

with:

```python
(Stages 1 to 4 of specs/claude-code-drift-automation-spec.md).
```

Replace:

```python
  check [--ref REF | --worktree] [--docs DIR]
      Fetch the docs when the changelog head moved, compare, and report what
      is due (R6). Reads main's commit unless --ref or --worktree says
      otherwise; --docs DIR runs offline against a local copy. Writes only
      under the cache. Exit 0 nothing due, 1 something due, 2 an error.
```

with:

```python
  check [--ref REF | --worktree] [--docs DIR] [--hook [--run ID]]
      Fetch the docs when the changelog head moved, compare, and report what
      is due (R6). Reads main's commit unless --ref or --worktree says
      otherwise; --docs DIR runs offline against a local copy. Writes only
      under the cache. Exit 0 nothing due, 1 something due, 2 an error.
      --hook prints nothing, even on an error, and leaves the session-start
      notice and last-check.json in the cache instead (R9). notice.sh
      refresh passes --run, the ID it then looks for in last-check.json.
```

Replace:

```python
import baseline
import packets
```

with:

```python
import baseline
import notice
import packets
```

Replace:

```python
    c.add_argument('--docs', type=Path)
```

with:

```python
    c.add_argument('--docs', type=Path)
    c.add_argument('--hook', action='store_true')
    c.add_argument('--run', metavar='ID')
```

Replace:

```python
def run_check(args, cache: Path, today: date, now: datetime, fetch) -> int:
    source = Source(REPO, None if args.worktree else args.ref)
    code, report, path = check(source, cache, docs_dir=args.docs, today=today, now=now, fetch=fetch)
    print('\n'.join(summary(report, path)))
    return code
```

with:

```python
def run_check(args, cache: Path, today: date, now: datetime, fetch) -> int:
    if args.run is not None and not args.hook:
        raise SetupError('--run goes with --hook')
    source = Source(REPO, None if args.worktree else args.ref)
    code, report, path = check(source, cache, docs_dir=args.docs, today=today, now=now, fetch=fetch)
    if args.hook:
        notice.after_check(cache, code, report, now, today, args.run)
    else:
        print('\n'.join(summary(report, path)))
    return code


def hook_failure(cache: Path | None, reason: str, now: datetime | None, run: str | None) -> int:
    '''check --hook on a setup error or a crash: the error notice and the
    record, printing nothing (R9.3, R9.4). With no cache to write to, or a
    write that fails, this run stays out of last-check.json, which notice.sh
    refresh counts as unfinished.'''
    if cache is not None:
        try:
            notice.after_failure(cache, reason, now or datetime.now().astimezone(), run)
        except OSError:
            pass
    return 2
```

Replace `main`:

```python
def main(argv=None, *, today: date | None = None, now: datetime | None = None, fetch=None) -> int:
    args = parser().parse_args(argv)
    try:
        cache = args.cache or default_cache()
        now = now or datetime.now().astimezone()
        today = today or now.date()
        if args.command == 'lint':
```

with:

```python
def main(argv=None, *, today: date | None = None, now: datetime | None = None, fetch=None) -> int:
    args = parser().parse_args(argv)
    hook = args.command == 'check' and args.hook
    cache = None
    try:
        cache = args.cache or default_cache()
        now = now or datetime.now().astimezone()
        today = today or now.date()
        if args.command == 'lint':
```

The cache and the clock stay inside the `try`: `test_a_crash_exits_two_never_one` pins that a crash in `default_cache()` still exits 2 (R6.9).

and the two handlers at its end:

```python
    except SetupError as exc:
        print(f'cc-guide: {exc}', file=sys.stderr)
        return 2
    except Exception:  # R6.9: a crash must never read as 0, clean, or 1, due
        traceback.print_exc()
        return 2
```

with:

```python
    except SetupError as exc:
        if hook:
            return hook_failure(cache, str(exc), now, args.run)
        print(f'cc-guide: {exc}', file=sys.stderr)
        return 2
    except Exception as exc:  # R6.9: a crash must never read as 0, clean, or 1, due
        if hook:
            return hook_failure(cache, f'{type(exc).__name__}: {exc}', now, args.run)
        traceback.print_exc()
        return 2
```

- [ ] **Step 4: Run the tests.**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: the baseline +20 (Task 3's 1, Task 4's 14, these 5), all passing. Then run `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice --python 3.13 python build/cc_guide/cli.py check --help`: the `check` usage line ends `[--hook] [--run ID]`.

- [ ] **Step 5: Commit.** Run `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/run_commit_lints.sh`, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice add build/cc_guide/cli.py build/cc_guide/test_cli.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice commit -m "feat(cc_guide): add check --hook, which leaves the notice on every exit"
```

---

### Task 6: `notice.sh show` (R9.2, R12.5), its citation, and the register

**Files:**
- Create: `build/cc_guide/notice.sh` (git mode 100755)
- Test: `build/cc_guide/test_notice_sh.py` (new)
- Modify: `build/cc_guide/conformance.toml` (`[kinds.hook]`, lines 56–64)

**Interfaces:**
- Consumes: from Task 4, `notice.write_notice` and `notice.DIGEST`, which write the fixtures `show` reads.
- Produces: `notice.sh show`, and the test helpers `cache_of(home)`, `sh(home, *args, shell, env, timeout)`, `shown(proc) -> str` and `quiet(proc)`, plus the constants `HERE`, `SCRIPT`, `REPO`, `LAUNCHD_PATH` and `SHELLS`. Task 7 extends this file and these helpers.

- [ ] **Step 1: Write the failing tests.** Create `build/cc_guide/test_notice_sh.py`:

```python
'''Tests for notice.sh, the drift check's session-start pair (drift spec
R9.2, R9.3, R12.5). Each run is made as Claude Code makes it from an app the
Dock started: no inherited environment, only HOME and launchd's PATH. notice.py
writes the files the script reads, so the shell-and-Python file contract is
tested across the two languages.'''
import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

import notice

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / 'notice.sh'
REPO = HERE.parents[1]
LAUNCHD_PATH = '/usr/bin:/bin'
SHELLS = [shell for shell in ('/bin/sh', '/bin/dash') if Path(shell).exists()]


def cache_of(home: Path) -> Path:
    return home / '.cache' / 'agent-skills' / 'cc-guide'


def sh(home: Path, *args: str, shell: str = '/bin/sh', env: dict | None = None, timeout: int = 60):
    '''notice.sh under shell with HOME, launchd's PATH and any extra
    variables, from a working directory that is not the script's.'''
    return subprocess.run([shell, str(SCRIPT), *args], env={'HOME': str(home), 'PATH': LAUNCHD_PATH, **(env or {})},
                          cwd=home, capture_output=True, text=True, timeout=timeout)


def shown(proc) -> str:
    '''The systemMessage a show run printed. Its whole stdout must be the
    JSON, and an empty stdout fails (R12.5).'''
    assert (proc.returncode, proc.stderr) == (0, '')
    assert proc.stdout, 'a show that prints nothing cannot pass as a quiet day (R12.5)'
    return json.loads(proc.stdout)['systemMessage']


def quiet(proc) -> None:
    assert (proc.returncode, proc.stdout, proc.stderr) == (0, '', '')


@pytest.mark.parametrize('shell', SHELLS)
def test_show_prints_a_notice_once_a_day_and_a_changed_notice_again(tmp_path, shell):
    notice.write_notice(cache_of(tmp_path), 'cc-guide · first → /cc-guide')
    assert shown(sh(tmp_path, 'show', shell=shell)) == 'cc-guide · first → /cc-guide'
    quiet(sh(tmp_path, 'show', shell=shell))
    notice.write_notice(cache_of(tmp_path), 'cc-guide · second → /cc-guide')
    assert shown(sh(tmp_path, 'show', shell=shell)) == 'cc-guide · second → /cc-guide'
    quiet(sh(tmp_path, 'show', shell=shell))


def test_show_runs_as_the_settings_command_runs_it(tmp_path):
    '''The hook executes the script by path, so its shebang and its execute
    bit run it: env -i, as R12.5 writes it.'''
    notice.write_notice(cache_of(tmp_path), 'cc-guide · direct → /cc-guide')
    proc = subprocess.run(['/usr/bin/env', '-i', f'HOME={tmp_path}', f'PATH={LAUNCHD_PATH}', str(SCRIPT), 'show'],
                          cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert shown(proc) == 'cc-guide · direct → /cc-guide'


def test_a_notice_shown_on_an_earlier_day_shows_again(tmp_path):
    cache = cache_of(tmp_path)
    notice.write_notice(cache, 'cc-guide · again → /cc-guide')
    digest = (cache / notice.DIGEST).read_text().strip()
    (cache / 'notice-shown').write_text(f'2000-01-01 {digest}\n')
    assert shown(sh(tmp_path, 'show')) == 'cc-guide · again → /cc-guide'
    assert (cache / 'notice-shown').read_text() == f"{datetime.now().strftime('%Y-%m-%d')} {digest}\n"


@pytest.mark.parametrize('shell', SHELLS)
def test_show_prints_nothing_before_any_check_or_when_nothing_is_due(tmp_path, shell):
    quiet(sh(tmp_path, 'show', shell=shell))
    notice.write_notice(cache_of(tmp_path), None)
    quiet(sh(tmp_path, 'show', shell=shell))


def test_show_still_prints_when_it_cannot_record_the_day(tmp_path):
    cache = cache_of(tmp_path)
    notice.write_notice(cache, 'cc-guide · stuck → /cc-guide')
    (cache / 'notice-shown').mkdir()
    assert shown(sh(tmp_path, 'show')) == 'cc-guide · stuck → /cc-guide'


def test_show_without_home_and_an_unknown_subcommand_both_exit_zero(tmp_path):
    quiet(subprocess.run(['/bin/sh', str(SCRIPT), 'show'], env={'PATH': LAUNCHD_PATH}, cwd=tmp_path,
                         capture_output=True, text=True, timeout=60))
    proc = sh(tmp_path, 'bogus')
    assert (proc.returncode, proc.stdout) == (0, '')
```

- [ ] **Step 2: Run them and watch them fail.**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_notice_sh.py`
Expected: every test fails. `sh` exits 127 (`notice.sh: No such file or directory`), and `env -i` cannot find the script.

- [ ] **Step 3: Write the script.** Create `build/cc_guide/notice.sh`:

```sh
#!/bin/sh
# notice.sh: the drift check's session-start pair (specs/claude-code-drift-automation-spec.md, R9).
#   notice.sh show     synchronous: print the notice check --hook left, once a day per notice (R9.2)
#   notice.sh refresh  async: run cli.py check --hook once the last good check is a day old (R9.3)
# Both exit 0 and print nothing but show's notice. .claude/settings.json wires the pair on
# SessionStart's startup matcher. JSON takes no comments, so this file carries the citation
# for the whole settings file, its model keys included: read .claude/settings.json with this
# file before restamping it (R4.2). notice.py's docstring lists the cache files the two
# languages share, and the order they are written and read in.
# Test seams: CC_GUIDE_UV_FALLBACK, colon-separated directories searched for uv after PATH,
# and CC_GUIDE_BUDGET, the seconds the check may run.
# cc-guide: hooks.events hooks.exit-codes hooks.configuration hooks.patterns hooks.pitfalls lean.model-routing rules.settings @2.1.219

cache="${HOME:-}/.cache/agent-skills/cc-guide"

# Print the notice unless this notice was already shown today. The digest is read before the
# notice, the reverse of the order they are written in, so a notice replaced between the two
# reads is shown once more and never skipped.
show() {
    digest=$(cat "$cache/notice.digest" 2>/dev/null)
    text=$(cat "$cache/notice.json" 2>/dev/null)
    [ -n "$text" ] || return 0
    today=$(date +%Y-%m-%d)
    [ "$(cat "$cache/notice-shown" 2>/dev/null)" = "$today $digest" ] && return 0
    printf '%s\n' "$text"
    { printf '%s %s\n' "$today" "$digest" > "$cache/notice-shown"; } 2>/dev/null
    return 0
}

case "${1:-}" in
    show) show ;;
    *) echo 'usage: notice.sh show | refresh' >&2 ;;
esac
exit 0
```

- [ ] **Step 4: Make it executable, track it, and run the tests.** The hook runs the script by path, so its execute bit matters in the working tree and in git's index:

```bash
chmod +x /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide/notice.sh
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice add --chmod=+x build/cc_guide/notice.sh
```

Run `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice ls-files -s build/cc_guide/notice.sh`: its mode is `100755`. Run the Step 2 command. Expected: 8 passed on a machine with `/bin/dash` (6 without it, since two tests run once per shell).

- [ ] **Step 5: Cite it.** The file is tracked now, so `baseline cite` accepts it:

```bash
uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice --python 3.13 python build/cc_guide/cli.py baseline cite build/cc_guide/notice.sh
```

It prints `stamped build/cc_guide/notice.sh @<release>`, where `<release>` is the highest `changed` among the seven cited sections on this branch's baseline (2.1.296 at `b7beaa1`). Run `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice --python 3.13 python build/cc_guide/cli.py lint`: exit 0, with no `STALE` line naming `notice.sh`. Re-run the Step 2 command: all pass.

- [ ] **Step 6: Admit the script to the register's hook kind.** In `build/cc_guide/conformance.toml`, replace:

```toml
[kinds.hook]
description = 'Hook scripts and the README that documents their wiring.'
globs = ['hooks/*.sh', 'hooks/*.py', 'hooks/README.md']
```

with:

```toml
[kinds.hook]
description = 'Hook scripts, the README that documents their wiring, and the drift notice script.'
globs = ['hooks/*.sh', 'hooks/*.py', 'hooks/README.md', 'build/cc_guide/notice.sh']
```

Run each:

```bash
uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice --python 3.13 --with pyyaml python build/check_conformance.py
uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py
```

Expected: `check_conformance.py` exits 0, and the suite passes at its baseline count. If any check now reports `build/cc_guide/notice.sh`, stop and bring the finding to the owner; do not add a register exception.

- [ ] **Step 7: Commit.** Run `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/run_commit_lints.sh`, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice add build/cc_guide/notice.sh build/cc_guide/test_notice_sh.py build/cc_guide/conformance.toml
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice commit -m "feat(cc_guide): add notice.sh show, the synchronous half of the session-start pair"
```

Check `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice ls-files -s build/cc_guide/notice.sh` once more: still `100755`.

---

### Task 7: `notice.sh refresh` (R9.3, R9.4; DF2, DF3, DF6 part b)

**Files:**
- Modify: `build/cc_guide/notice.sh` (replaced whole; the citation line keeps the stamp Task 6 set)
- Test: `build/cc_guide/test_notice_sh.py` (new imports, a fixture, and tests appended at the end)

**Interfaces:**
- Consumes: from Task 5, `cli.py check --hook --run <id>`. From Task 4, `notice.write_notice`, `notice.record_check`, `notice.read_last_check` and `notice.NOTICE`. From Task 6, the helpers in `test_notice_sh.py`.
- Produces: `notice.sh refresh`. Task 8 wires it into the settings as an async hook.

- [ ] **Step 1: Write the failing tests.** In `build/cc_guide/test_notice_sh.py`, replace the imports:

```python
import json
import subprocess
from datetime import datetime
from pathlib import Path
```

with:

```python
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
```

Append at the end of the file:

```python
NO_UV = 'the drift check cannot run: no uv on PATH, in ~/.local/bin or in /opt/homebrew/bin'
FOUND = 'cc-guide · 1 docs block changed (alpha.overview) → /cc-guide'

# A stand-in for uv. It records how it was called, then finishes as check --hook would
# (through notice.py, so the file contract is the real one), hangs, or fails before Python.
FAKE_UV = '''#!/bin/sh
printf '%s\\n' "$0" > "$HOME/uv-path"
printf '%s\\n' "$@" > "$HOME/uv-args"
env | grep '^GIT_' > "$HOME/uv-git-env"
case "${{FAKE_UV:-finish}}" in
    finish) exec "{python}" "{finish}" "$@" ;;
    hang) exec sleep 30 ;;
    *) exit 2 ;;
esac
'''

FINISH = '''import sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, {here!r})
import notice
run = sys.argv[sys.argv.index('--run') + 1]
cache = Path.home() / '.cache' / 'agent-skills' / 'cc-guide'
notice.write_notice(cache, {found!r})
notice.record_check(cache, 1, datetime.now().astimezone(), run)
'''


@pytest.fixture
def fake_uv(tmp_path):
    '''A HOME, and the variables that put the stand-in uv first on launchd's
    PATH with no fallback directory.'''
    home = tmp_path / 'home'
    home.mkdir()
    finish = tmp_path / 'finish.py'
    finish.write_text(FINISH.format(here=str(HERE), found=FOUND), encoding='utf-8')
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    uv = bin_dir / 'uv'
    uv.write_text(FAKE_UV.format(python=sys.executable, finish=finish))
    uv.chmod(0o755)
    return home, {'PATH': f'{bin_dir}:{LAUNCHD_PATH}', 'CC_GUIDE_UV_FALLBACK': str(tmp_path / 'nowhere')}


@pytest.mark.parametrize('shell', SHELLS)
def test_refresh_runs_check_hook_through_uv_by_absolute_path_and_show_follows(fake_uv, shell):
    home, env = fake_uv
    quiet(sh(home, 'refresh', shell=shell, env=env))
    args = (home / 'uv-args').read_text().splitlines()
    assert args[:-1] == ['run', '--python', '3.13', 'python', str(HERE / 'cli.py'), 'check', '--hook', '--run']
    assert re.fullmatch(r'\d+\.\d+', args[-1])
    cache = cache_of(home)
    assert notice.read_last_check(cache)['run'] == args[-1]
    assert not (cache / 'unfinished').exists()
    assert not (cache / 'lock').exists()
    assert shown(sh(home, 'show', shell=shell)) == FOUND


def test_refresh_waits_a_day_after_a_good_check(fake_uv):
    home, env = fake_uv
    cache = cache_of(home)
    notice.record_check(cache, 0, datetime.now().astimezone() - timedelta(hours=23), 'earlier')
    quiet(sh(home, 'refresh', env=env))
    assert not (home / 'uv-args').exists()
    notice.record_check(cache, 0, datetime.now().astimezone() - timedelta(hours=25), 'earlier')
    quiet(sh(home, 'refresh', env=env))
    assert (home / 'uv-args').exists()


def test_refresh_leaves_a_fresh_lock_alone_and_breaks_one_over_an_hour_old(fake_uv):
    home, env = fake_uv
    lock = cache_of(home) / 'lock'
    lock.mkdir(parents=True)
    quiet(sh(home, 'refresh', env=env))
    assert lock.is_dir()
    assert not (home / 'uv-args').exists()
    old = time.time() - 2 * 3600
    os.utime(lock, (old, old))
    quiet(sh(home, 'refresh', env=env))
    assert (home / 'uv-args').exists()
    assert not lock.exists()


def test_refresh_looks_in_each_fallback_directory_in_order(fake_uv, tmp_path):
    home, env = fake_uv
    stand_in = Path(env['PATH'].split(':')[0]) / 'uv'
    first, second = tmp_path / 'first', tmp_path / 'second'
    second.mkdir()
    (second / 'uv').write_bytes(stand_in.read_bytes())
    (second / 'uv').chmod(0o755)
    quiet(sh(home, 'refresh', env={'CC_GUIDE_UV_FALLBACK': f'{first}:{second}'}))
    assert (home / 'uv-path').read_text().strip() == str(second / 'uv')


def test_refresh_without_uv_leaves_the_fixed_error_notice(fake_uv):
    home, _ = fake_uv
    notice.record_check(cache_of(home), 1, datetime.now().astimezone() - timedelta(days=2, hours=1), 'old')
    quiet(sh(home, 'refresh', env={'CC_GUIDE_UV_FALLBACK': str(home / 'nowhere')}))
    assert shown(sh(home, 'show')) == f'cc-guide · {NO_UV} · last good check 2 d ago → install uv'


def test_refresh_stops_a_check_past_its_budget_and_counts_the_run_unfinished(fake_uv):
    home, env = fake_uv
    started = time.monotonic()
    quiet(sh(home, 'refresh', env={**env, 'FAKE_UV': 'hang', 'CC_GUIDE_BUDGET': '1'}))
    assert time.monotonic() - started < 10
    cache = cache_of(home)
    assert (cache / 'unfinished').read_text() == '1\n'
    assert not (cache / notice.NOTICE).exists()


def test_three_unfinished_runs_in_a_row_leave_the_error_notice_and_a_finished_run_clears_them(fake_uv):
    home, env = fake_uv
    cache = cache_of(home)
    for count in (1, 2):
        quiet(sh(home, 'refresh', env={**env, 'FAKE_UV': 'fail'}))
        assert (cache / 'unfinished').read_text() == f'{count}\n'
        assert not (cache / notice.NOTICE).exists()
    quiet(sh(home, 'refresh', env={**env, 'FAKE_UV': 'fail'}))
    assert shown(sh(home, 'show')) == ('cc-guide · the drift check did not finish 3 times in a row · '
                                       'no good check yet → run build/cc_guide/cli.py check')
    quiet(sh(home, 'refresh', env=env))
    assert not (cache / 'unfinished').exists()
    assert shown(sh(home, 'show')) == FOUND


def test_refresh_runs_the_check_without_the_callers_git_variables(fake_uv):
    '''Deferred item "check's report and inputs", part b: a caller's GIT_DIR
    or GIT_INDEX_FILE would point check's git reads somewhere else.'''
    home, env = fake_uv
    quiet(sh(home, 'refresh', env={**env, 'GIT_DIR': '/nonexistent', 'GIT_INDEX_FILE': '/nonexistent/index'}))
    assert (home / 'uv-git-env').read_text() == ''
```

- [ ] **Step 2: Run them and watch them fail.**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_notice_sh.py`
Expected: Task 6's 8 still pass, and the 9 new tests fail. `refresh` is still an unknown subcommand, so `quiet` fails on the usage line in stderr, and the assertions on `uv-args` fail.

- [ ] **Step 3: Replace the script.** Replace `build/cc_guide/notice.sh` with the text below. Keep the citation line's stamp as Task 6 set it: the `@2.1.296` below is `b7beaa1`'s value, so if your line reads otherwise, keep yours.

```sh
#!/bin/sh
# notice.sh: the drift check's session-start pair (specs/claude-code-drift-automation-spec.md, R9).
#   notice.sh show     synchronous: print the notice check --hook left, once a day per notice (R9.2)
#   notice.sh refresh  async: run cli.py check --hook once the last good check is a day old (R9.3)
# Both exit 0 and print nothing but show's notice. .claude/settings.json wires the pair on
# SessionStart's startup matcher. JSON takes no comments, so this file carries the citation
# for the whole settings file, its model keys included: read .claude/settings.json with this
# file before restamping it (R4.2). notice.py's docstring lists the cache files the two
# languages share, and the order they are written and read in.
# Test seams: CC_GUIDE_UV_FALLBACK, colon-separated directories searched for uv after PATH,
# and CC_GUIDE_BUDGET, the seconds the check may run.
# cc-guide: hooks.events hooks.exit-codes hooks.configuration hooks.patterns hooks.pitfalls lean.model-routing rules.settings @2.1.296

DAY=86400             # seconds; notice.py measures a day the same way
LOCK_MINUTES=60       # R9.3: a lock older than an hour is broken
BUDGET=300            # seconds check --hook may run, since async hooks have no timeout
UNFINISHED_LIMIT=3    # R9.4: three unfinished runs in a row are an error

unset CDPATH
here=$(cd "$(dirname "$0")" && pwd -P)
cache="${HOME:-}/.cache/agent-skills/cc-guide"

# Print the notice unless this notice was already shown today. The digest is read before the
# notice, the reverse of the order they are written in, so a notice replaced between the two
# reads is shown once more and never skipped.
show() {
    digest=$(cat "$cache/notice.digest" 2>/dev/null)
    text=$(cat "$cache/notice.json" 2>/dev/null)
    [ -n "$text" ] || return 0
    today=$(date +%Y-%m-%d)
    [ "$(cat "$cache/notice-shown" 2>/dev/null)" = "$today $digest" ] && return 0
    printf '%s\n' "$text"
    { printf '%s %s\n' "$today" "$digest" > "$cache/notice-shown"; } 2>/dev/null
    return 0
}

# The last good check's epoch second, read from the line notice.py writes; empty when none.
ok_epoch() {
    sed -n 's/^ *"ok_epoch": \([0-9][0-9]*\),\{0,1\}$/\1/p' "$cache/last-check.json" 2>/dev/null
}

# The age of the last good check, as notice.py words it.
age_words() {
    ok=$(ok_epoch)
    if [ -n "$ok" ]; then
        printf 'last good check %s d ago' $(( ($(date +%s) - ok) / DAY ))
    else
        printf 'no good check yet'
    fi
}

# True while the last good check is under a day old.
fresh() {
    ok=$(ok_epoch)
    [ -n "$ok" ] && [ $(( $(date +%s) - ok )) -lt "$DAY" ]
}

# Write one of refresh's two error notices: notice.json, then its digest, each renamed into
# place. $1 says what failed and $2 what to do. Neither holds a quote or a backslash, so the
# JSON needs no escaping beyond the two \u escapes written here.
fail_notice() {
    message="cc-guide \\u00b7 $1 \\u00b7 $(age_words) \\u2192 $2"
    tmp="$cache/.notice.$$.tmp"
    { printf '{"systemMessage": "%s"}\n' "$message" > "$tmp" && mv -f "$tmp" "$cache/notice.json"; } 2>/dev/null \
        || return 0
    sum=$(cksum < "$cache/notice.json")
    { printf '%s\n' "${sum%% *}" > "$tmp" && mv -f "$tmp" "$cache/notice.digest"; } 2>/dev/null
    return 0
}

# Take the lock, breaking one older than LOCK_MINUTES. find -mmin is BSD and GNU, not POSIX.
take_lock() {
    mkdir "$lock" 2>/dev/null && return 0
    [ -n "$(find "$lock" -prune -mmin +"$LOCK_MINUTES" 2>/dev/null)" ] || return 1
    rm -rf "$lock" && mkdir "$lock" 2>/dev/null
}

# Print the uv to run: the one on PATH, else the first in the fallback directories.
find_uv() {
    command -v uv 2>/dev/null && return 0
    set -f
    old_ifs=$IFS
    IFS=:
    for dir in ${CC_GUIDE_UV_FALLBACK-$HOME/.local/bin:/opt/homebrew/bin}; do
        if [ -x "$dir/uv" ]; then
            IFS=$old_ifs
            set +f
            printf '%s\n' "$dir/uv"
            return 0
        fi
    done
    IFS=$old_ifs
    set +f
    return 1
}

# Run check --hook through uv under the budget, then see whether it finished: a finished run
# leaves its ID in last-check.json, which notice.py writes last of all.
check_now() {
    for name in $(env | sed -n 's/^\(GIT_[A-Za-z0-9_]*\)=.*/\1/p'); do
        unset "$name"   # a caller's GIT_DIR or GIT_INDEX_FILE would redirect check's git reads
    done
    budget=${CC_GUIDE_BUDGET:-$BUDGET}
    case $budget in ''|*[!0-9]*) budget=$BUDGET ;; esac
    id="$$.$(date +%s)"
    "$1" run --python 3.13 python "$here/cli.py" check --hook --run "$id" </dev/null >/dev/null 2>&1 &
    pid=$!
    waited=0
    while kill -0 "$pid" 2>/dev/null; do
        if [ "$waited" -ge "$budget" ]; then
            kill "$pid" 2>/dev/null   # uv passes SIGTERM on to the check
            break
        fi
        sleep 1
        waited=$((waited + 1))
    done
    wait "$pid" 2>/dev/null
    if grep -qF "\"run\": \"$id\"" "$cache/last-check.json" 2>/dev/null; then
        rm -f "$cache/unfinished"
        return 0
    fi
    count=$(cat "$cache/unfinished" 2>/dev/null)
    case $count in ''|*[!0-9]*) count=0 ;; esac
    count=$((count + 1))
    { printf '%s\n' "$count" > "$cache/unfinished"; } 2>/dev/null
    if [ "$count" -ge "$UNFINISHED_LIMIT" ]; then
        fail_notice "the drift check did not finish $count times in a row" 'run build/cc_guide/cli.py check'
    fi
    return 0
}

refresh() {
    mkdir -p "$cache" 2>/dev/null || return 0
    fresh && return 0
    lock="$cache/lock"
    take_lock || return 0
    trap 'rm -rf "$lock"' EXIT
    trap 'exit 0' HUP INT TERM
    fresh && return 0   # another session may have finished a check while this one waited
    if ! uv=$(find_uv); then
        fail_notice 'the drift check cannot run: no uv on PATH, in ~/.local/bin or in /opt/homebrew/bin' 'install uv'
        return 0
    fi
    check_now "$uv"
}

case "${1:-}" in
    show) show ;;
    refresh) refresh ;;
    *) echo 'usage: notice.sh show | refresh' >&2 ;;
esac
exit 0
```

- [ ] **Step 4: Run the tests.**

Run the Step 2 command. Expected: 17 passed on a machine with `/bin/dash` (14 without it). Most refresh tests take about a second each, since the budget loop polls once a second. Then run `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice ls-files -s build/cc_guide/notice.sh`: still `100755`. The verbatim block above carries `b7beaa1`'s stamp, so restamp it against this branch's baseline. When the stamp is already current, this changes nothing:

```bash
uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice --python 3.13 python build/cc_guide/cli.py baseline cite build/cc_guide/notice.sh
```

Run `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice --python 3.13 python build/cc_guide/cli.py lint`: exit 0, with no `STALE` line for `notice.sh`.

- [ ] **Step 5: Commit.** Run `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/run_commit_lints.sh`, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice add build/cc_guide/notice.sh build/cc_guide/test_notice_sh.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice commit -m "feat(cc_guide): add notice.sh refresh, the async half of the session-start pair"
```

---

### Task 8: Wire the pair, and the docs (R9.1, R9.5, R12.7; owner gate)

**Files:**
- Modify: `.claude/settings.json` (add the `hooks` key)
- Test: `build/cc_guide/test_notice_sh.py` (one test appended)
- Modify: `build/CLAUDE.md` (a paragraph after the one on `cc_guide/`)
- Modify: `CLAUDE.md` (the drift detector's comment, lines 136–138)

**Interfaces:**
- Consumes: `notice.sh show` and `notice.sh refresh` (Tasks 6 and 7), and `REPO` in `test_notice_sh.py`.
- Produces: the committed SessionStart wiring that Task 10 exercises live.

- [ ] **Step 1: Write the failing test.** Append to `build/cc_guide/test_notice_sh.py`:

```python
def test_the_project_settings_wire_the_pair_on_startup():
    '''R9.1: one SessionStart group on the startup matcher, show and then an
    async refresh, each naming this script through the quoted project dir.'''
    settings = json.loads((REPO / '.claude' / 'settings.json').read_text())
    assert settings['hooks']['SessionStart'] == [{'matcher': 'startup', 'hooks': [
        {'type': 'command', 'command': '"$CLAUDE_PROJECT_DIR"/build/cc_guide/notice.sh show'},
        {'type': 'command', 'command': '"$CLAUDE_PROJECT_DIR"/build/cc_guide/notice.sh refresh', 'async': True},
    ]}]
```

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_notice_sh.py -k wire_the_pair`
Expected: FAIL with `KeyError: 'hooks'`.

- [ ] **Step 2: Wire the settings.** Add a `hooks` key to `.claude/settings.json`, and leave its other keys as they are. At `b7beaa1` the file becomes:

```json
{
    "model": "opus",
    "availableModels": ["sonnet", "opus", "haiku", "fable"],
    "enforceAvailableModels": true,
    "hooks": {
        "SessionStart": [
            {
                "matcher": "startup",
                "hooks": [
                    { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/build/cc_guide/notice.sh show" },
                    { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/build/cc_guide/notice.sh refresh", "async": true }
                ]
            }
        ]
    }
}
```

Re-run the Step 1 command: PASS. Run `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice --python 3.13 --with pyyaml python build/check_conformance.py`: exit 0. That covers `hook-dir-quoted`, `hook-var-quoted`, and `hook-scripts-executable`, which needs Task 6's register glob.

- [ ] **Step 3: The docs.** In `build/CLAUDE.md`, replace:

```markdown
prints the corrections and the `baseline` commands that follow.
Nothing is committed for you.
```

with:

```markdown
prints the corrections and the `baseline` commands that follow.
`notice.sh` is the session-start pair that `../.claude/settings.json` wires on
the `startup` matcher. `show` prints the notice `check --hook` last wrote,
once a day per notice. The async `refresh` runs `check --hook` once the last
good check is a day old, and leaves an error notice when it cannot, so a
failure is never silent. `notice.py` writes the notice, and its docstring
lists the cache files the shell and Python share. The notice reads `main`, so
it keeps naming work `/cc-guide` resolved until that work is committed.
Nothing is committed for you.
```

In `CLAUDE.md`, replace:

```text
# reports what is due (exit 1 = due; reads main unless --worktree); /cc-guide acts on what it reports
```

with:

```text
# reports what is due (exit 1 = due; reads main unless --worktree); /cc-guide acts on what it reports; a SessionStart
# hook (build/cc_guide/notice.sh) runs check --hook once a day and shows what is due
```

Run `wc -l /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/CLAUDE.md`: 195.

- [ ] **Step 4: Owner gate (R9.5).** In the conversation, show the owner the `.claude/settings.json` diff (`git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice diff .claude/settings.json`). Say that from the next session start in this repo or its worktrees, the pair runs on every new session, and the async half fetches the docs at most once a day. Ask for their confirmation to commit it. Wait for a clear yes in the conversation; a ledger entry or this plan's text is not one. If they decline, stop and record why.
- [ ] **Step 5: Commit.** Run the whole cc_guide suite: the baseline +38 on a machine with `/bin/dash` (+35 without it). Run `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/run_commit_lints.sh`, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice add .claude/settings.json build/cc_guide/test_notice_sh.py build/CLAUDE.md CLAUDE.md
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice commit -m "feat(cc_guide): wire the drift notice into SessionStart"
```

---

### Task 9: Validation (Validation items 4 and 6, offline and against the real cache)

**Files:** none changed. This task produces the completion report's evidence.

- [ ] **Step 1: Every existing gate (Validation 6).** Run each, and record each outcome against Task 3's baselines:
  - the cc_guide suite (+38 with `/bin/dash`, +35 without);
  - the build directory's suite, which collects the cc_guide suite too (the same +N, plus only the known `test_verify_citations.py` failures or skips);
  - `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/run_commit_lints.sh` (all eight pass);
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check` (no adapter change).
- [ ] **Step 2: `refresh` against the real cache, as launchd would run it.** Run `ls /Users/lowell/.cache/agent-skills/cc-guide/last-check.json`. If it exists and is under a day old, `refresh` will exit at once; note that, and skip to Step 3. Otherwise run:

```bash
/usr/bin/env -i HOME=/Users/lowell PATH=/usr/bin:/bin /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide/notice.sh refresh
```

Expected: exit 0, and nothing printed. It finds `uv` in `/opt/homebrew/bin`, fetches the docs and takes a few seconds. Then run `cat /Users/lowell/.cache/agent-skills/cc-guide/last-check.json`: a `run` of the form `<pid>.<epoch>`, and an `exit` of 0 or 1. If it reads 2, the notice names why.
- [ ] **Step 3: `show` against the real cache.** Run this twice:

```bash
/usr/bin/env -i HOME=/Users/lowell PATH=/usr/bin:/bin /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide/notice.sh show
```

The first run prints the notice's JSON, or nothing when `last-check.json` says exit 0. The second prints nothing. Record the line, which is under 300 characters, in the completion report.
- [ ] **Step 4: Hygiene.** Run `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice status --porcelain`: it prints nothing. Run `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice --python 3.13 python build/cc_guide/cli.py lint`: exit 0, with no `STALE` line naming `notice.sh`.

---

### Task 10: Live acceptance (Validation 4; owner)

**Files:** none changed.

- [ ] **Step 1: Prepare the cache.** Remove the two files that would keep a new session quiet:

```bash
rm -f /Users/lowell/.cache/agent-skills/cc-guide/notice-shown /Users/lowell/.cache/agent-skills/cc-guide/last-check.json
```

If `/Users/lowell/.cache/agent-skills/cc-guide/notice.json` is empty, because nothing is due on `main`, write a stand-in so there is something to see:

```bash
uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice/build/cc_guide --python 3.13 python -c "import notice, state; notice.write_notice(state.default_cache(), 'cc-guide · live acceptance stand-in → /cc-guide')"
```

The session's own `refresh` replaces it with the real notice.
- [ ] **Step 2: The owner starts a new Desktop session in `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-49-drift-notice`.** Ask in the conversation, and wait. The owner reports the line shown at the session's start, if any.
- [ ] **Step 3: Confirm `refresh` ran.** Within a minute or two, run `cat /Users/lowell/.cache/agent-skills/cc-guide/last-check.json`: a `run` of the form `<pid>.<epoch>`. Run `ls /Users/lowell/.cache/agent-skills/cc-guide/`: no `lock` directory remains.
- [ ] **Step 4: Once a day.** The owner starts further new sessions in the same worktree until two in a row have started with the same notice; the second shows nothing. If Step 3's `refresh` replaced the stand-in, the next session shows the real notice once, because a changed notice shows again; the one after shows nothing. Record each session's observation.
- [ ] **Step 5: Record the result** under this task: `> Result: <date>, Claude Code <version>: <what each session showed>`. If the notice never appeared, or appeared twice for the same notice on the same day, stop and bring it to the owner before the Plan Completion Protocol.

---

## Plan completion notes

- **Step 1, gate.** Leftovers that need the owner go to them in one batch. That includes Task 1's `claude -p` observation for Stage 5, and the coverage gaps G1–G5, with any gap execution found.
- **Step 3, deferred items.** Tick "check's report and inputs, for Stage 4's hook and notice" (section `38-claude-code-drift-automation`) with: `→ done in plan 49: (a) needs no fix for the hook, since check --hook writes the notice and its record on every exit path and nothing in the hook reads the report; (b) refresh runs the check without its caller's GIT_* variables, and Source is unchanged because the pre-commit lint relies on git's environment; (c) check runs the audit due rule when the fetch fails.` Then append this plan's section, which holds at least D2's item:

  ```markdown
  - [ ] Pin `baseline rebaseline` to its packet's head (plan 49, Q1, owner decision D2). A
        session start can now refetch the docs: `notice.sh refresh` runs `check --hook`
        once the hook's last good check is a day old, and when the changelog head has
        moved, that rewrites the shared `~/.cache/agent-skills/cc-guide/latest/`. A manual
        `check` can do the same. `baseline rebaseline` (`build/cc_guide/baseline.py`,
        `cli.py`'s `run_baseline`) re-hashes from `latest/` at whatever head
        `fetch.json` holds, so a refetch between a `/cc-guide` verify and the rebaseline
        `settle` prints records hashes for docs text the verifier never read. Only
        `baseline audited` is pinned, through `--to` (plan 44). Fix: `settle`
        (`build/cc_guide/settle.py`) prints `rebaseline --head <the packet's index.json
        head>`, and `rebaseline` refuses when `fetch.json`'s `changelog_head` differs,
        naming both heads. This amends drift spec R7 and R8.8. Until it lands, finish a
        `/cc-guide` run's rebaseline before starting another session in the repo. Size:
        plan. Done when: `rebaseline --head` refuses a moved head with a test in
        `build/cc_guide/test_cli.py`, `settle` prints the flag with a test in
        `build/cc_guide/test_settle.py`, and the spec states the rule.
  ```

  Append further items only for what execution deferred.
- **Step 4, triage.** The backlog holds 62 open items at `b7beaa1`, over the 20-item threshold, so the triage proposal runs.
- **Step 5, retire.** `git mv` this plan to `specs/plans/completed/`. The spec stays in `specs/`, since Stage 5 (probes) remains. Re-point this plan's relative links, if any, for the new depth.
