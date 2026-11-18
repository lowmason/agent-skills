# prepare-handoff Re-run (`v1`, `b2`, `c4a-neg`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give each of the arms `v1`, `b2` and `c4a-neg` five valid reps on the shipped prepare-handoff text and a recorded verdict. The reps run in a new committed micro-test kit, where each rep's `HOME` is its own folder that holds the shipped skills.

**Architecture:** A new kit under `specs/baseline/red-baseline-handoff-rerun/kit/` reuses plan 40's frozen arms, prompts, fixtures and rubric. It replaces plan 40's runner and audit. Each rep gets a fresh `HOME` at `/tmp/phr100/<rep>/`. That folder holds copies of the shipped skills, agents and command, the fixture repo, its origin, a shim and a `TMPDIR`. So a reviewer subagent that looks under `~/.claude/skills` reads the text under test. A PreToolUse guard denies tool inputs that reach the real home. Reps run one at a time, and each rep's `HOME` moves out of `/tmp/phr100/` when the rep ends. The runner strips `credential_expires_at` from every JSON file it writes. The audit applies plan 40's VOID rules through a translation table for the new layout.

**Tech Stack:** bash (3.2 compatible), Python 3 through `uv run` (the guard runs on `/usr/bin/python3`, stdlib only, 3.9 compatible), `claude -p` with tools (Claude Code 2.1.323 at planning), git, pytest.

**Spec:** none. The plan argues from four items of `specs/deferred_items.md` and from plan 40's record:
- the item "Re-run `v1`, `b2` and `c4a-neg` on the shipped prepare-handoff text" (section `40-handoff-briefs`) and its `→ progress 2026-11-17 (owner ruling)` note;
- the item "The deny rule `Read(~/**)` does not stop every Bash read of the home folder" (section `98-marimo-notebook-seam`);
- the item "Parallel micro-test reps share the scratch folder" (section `98-marimo-notebook-seam Step 4b review`);
- the item "The next micro-test kit still copies `credential_expires_at` into its rep JSON files" (section `deferred-2026-11-14`);
- `specs/completed/red-baseline-handoff-briefs-2026-10-10.md`, Phase 3, Acceptance and the Addendum;
- plan 40's frozen protocol in `~/.cache/agent-skills/handoffs/red/` (`PROTOCOL.md`, `rubric.md`, `prompts/`, `tools/`), called `$RED` below. It is outside the repo.

## Global Constraints

- **Scope.** The four items above. Do not edit any file under `skills/`, `agents/`, `commands/`, `hooks/` or `runtimes/`. Do not edit any file in `$RED` except `changes.log`, which gets one line (Task 4).
- **Branch.** This plan reaches `main` first, in a PR of its own, so that the `→ planned` notes stop the aging clock on `main` before 2026-11-26. Execution starts after that PR merges, in a fresh session, on a new branch cut from that `main`, in its own worktree. Do not push during execution. finishing-a-development-branch decides how the branch is integrated.
- **Concurrency** (owner rule, 2026-11-17). This plan is a domain stream: its files are `specs/baseline/red-baseline-handoff-rerun*`, `build/suites.toml` (one table), this plan, the plan 40 record (one section) and the closing edits to `specs/deferred_items.md` and `specs/history.md`. Before execution starts, `list_sessions` must show at most two other plan executions running in agent-skills, and none of them a machinery stream.
- **Paid runs.** No `claude -p` runs before the owner approves the budget at Task 4's gate. The estimate is in Builder's call C14.
- **Kit commit.** The skills, agents and command in each rep's `HOME` come from one commit: the execution branch's base, recorded as `KIT_COMMIT` in Task 2. They come from `git archive KIT_COMMIT`, never from the working tree.
- **Fixtures.** Plan 40's templates `~/.cache/pondworks/templates/t2`, `t3` and `t9`, used read-only. Each must have only `refs/heads/main`, a clean status, and this HEAD: `t2` `a3df8a06785691b7528332b855d38e46e387acef`, `t3` `6b17dd86fafdb3dade26ce2a07af86a0da7cba9a`, `t9` `7137e5ecd591f7195b196e67a0df79a385a402c2`.
- **Rep command.** Every rep turn runs this command, from the rep's repo, with stdin from the turn's prompt file:

  ```bash
  env -i HOME="$H" USER="$USER" LOGNAME="$LOGNAME" SHELL=/bin/zsh LANG="${LANG-}" \
    TMPDIR="$H/tmp" PATH="$H/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin" \
    CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 \
    "$CLAUDE_BIN" -p <--session-id SID | --resume SID> \
    --setting-sources user,project,local --strict-mcp-config \
    --model claude-opus-5-5 --effort xhigh --permission-mode auto \
    --settings "$SETTINGS_JSON" --max-budget-usd 30 \
    --output-format stream-json --verbose
  ```

  `$H` is `/private/tmp/phr100/<rep>`, the physical form of `/tmp/phr100/<rep>`. macOS reports a working folder under `/tmp` as `/private/tmp`, so `HOME` uses that form too, and the two agree. `$SETTINGS_JSON` is the inline JSON of Task 1's Interfaces block. No other flag, variable or setting source is added.

  > Deviation (execution, 2026-11-18, execution brief default 2): the `env -i` list also sets `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=2400000` (40 minutes). In print mode, Claude Code stops background subagents 10 minutes after the main turn ends, and that voided plan 45's gate reps. Without the variable, a stopped fact-checker or cold reader could score as a FAIL, not a VOID (Review Focus 3). The runner's allow-list of `CLAUDE*` names (C13) and `test_env_holds_no_session_variables` (Task 2) admit this one name too. Task 3's audit voids a rep whose `turn<n>.stderr` holds `Background tasks still running`. That void is a harness check in C11's family, not a change to the frozen VOID rules (D1). The kit's `README.md` repeats this note.
- **Thresholds** (`$RED/PROTOCOL.md`, Thresholds). `v1` and `b2` pass when at least 4 of their first 5 valid reps pass every criterion. `c4a-neg` passes when at most 1 of its first 5 valid reps fails F-brief. A void rep is replaced, up to 10 dispatched per arm. An arm with fewer than 5 valid reps at 10 dispatched stops for the owner. Only the first 5 valid reps by id count. Pilot reps never count.
- **Rubric.** `$RED/rubric.md`, sections `b2`, `c4a-neg` and `c4b, v1`, unchanged. The rubric's `~/.cache/pondworks/reps/<rep>/` means the rep's repo, now `~/work/<rep>` inside the parked `HOME`.
- **Raw outputs stay out of the repo.** The control folder is `~/.cache/agent-skills/handoffs/rerun100/` (`$CTL`). Results, parked homes, the registry and scores live there. The repo gets the kit, the scores TSVs and the record. A committed file writes the real home as `~real`.
- **Style.** The record, the kit README text and commit messages follow the plain-English rule. Python uses single quotes. Bash stays bash 3.2 compatible.
- **Lints.** Run `build/run_commit_lints.sh` before each commit, through the pre-commit hook. Never use `--no-verify`. The kit's tests are registered in `build/suites.toml` (Task 1), because `run_suites.py --check` fails on an unregistered test directory.
- **Commits.** Each commit message ends with the session's `Co-Authored-By` trailer.
- **Completion.** The Plan Completion Protocol ticks all four items with `→ done` notes. No spec retires.

## Review Focus

1. **A rep's `~` read lands in the kit, not in the real home.** A subagent's `ls ~/.claude/skills` or `Read ~/.claude/skills/writing-plans/SKILL.md` must read the copy from `KIT_COMMIT`. The audit must count it as valid. Pinned in Task 2 (the rep `HOME` holds the kit and passes its hash check) and Task 3 (`test_tilde_kit_read_is_valid`).
2. **The keychain link is a door to the real home.** `~/Library/Keychains` points into the real `~/Library`. A tool input that reaches it, or goes through it with `..`, must be denied and must void the rep. Pinned in Task 1 (`test_denies_through_keychain_link`) and Task 3 (`test_library_link_voids`).
3. **A login or budget failure reads as behavior.** If the redirected `HOME` loses the login, or a turn hits the budget cap, the turn ends in an error. It must void the rep, never score as a FAIL. Pinned in Task 3 (`test_error_turn_voids`) and Task 4's pilot (auth check).
4. **Two reps see each other's files.** A rep must not see a brief, memory or export that another rep wrote. Pinned in Task 2 (`test_second_rep_sees_nothing_of_first`).
5. **`credential_expires_at` survives in a copied file.** The field sits in the stream's `result` record. Every JSON or JSONL file that the runner writes must lack it. Pinned in Task 2 (`test_strip_removes_field_everywhere`).

## Decisions

- **D1** (owner, brief, 2026-11-17): use a kit-owned skills folder. The kit points the skill path (or `HOME`) at a folder that holds the shipped skills, so the reviewer subagents that the skill dispatches read the text under test. The VOID rules stay as they are. Applied in: Builder's calls C1 and C10, Tasks 2 and 3.
- **D2** (owner, plan review, 2026-11-17): "Approve with table B". The plan stands as written, Builder's calls C1–C14 included, and the audit uses table B, not table A. Applied in: Builder's call C10, Task 3.

## Builder's calls

These settle what the items and the owner ruling leave open. The owner reviews them at plan review.

- **C1. Layout.** One folder per rep, `/private/tmp/phr100/<rep>/`, which is the rep's `HOME`. It holds:
  - `.claude/skills/<12 skills>`, `.claude/agents/code-reviewer.md` and `task-reviewer.md`, and `.claude/commands/deferred.md`, all from `KIT_COMMIT`. The 12 skills are plan 40's kit list: brainstorming, writing-plans, executing-plans, subagent-driven-development, finishing-a-development-branch, requesting-code-review, receiving-code-review, using-git-worktrees, verification-before-completion, test-driven-development, derive-roadmap and prepare-handoff;
  - `work/<rep>/`, the fixture repo, and `git/<rep>.git`, its bare origin with `main` pushed and `origin/HEAD` set;
  - `.local/bin/`, the shim (C8), and `tmp/`, the rep's `TMPDIR`;
  - `Library/Keychains`, a symlink to the real `~/Library/Keychains` (C2).

  The repo folder is named by the rep id, as in plan 40, so the brief folder is `~/.cache/agent-skills/handoffs/<rep>/`. Rep ids continue plan 40's numbering, from `r281`.
- **C2. Login.** A planning probe (2026-11-17, Claude Code 2.1.323) ran `claude auth status` under `env -i`. With `HOME` at a new folder it reported `"loggedIn": false`. With `CLAUDE_CONFIG_DIR` set to the real `~/.claude` it was also false. With one symlink, `HOME/Library/Keychains` to the real `~/Library/Keychains`, it was true. So the rep `HOME` carries only that link. The guard (C5) and the audit (C10) treat it as the real home.
- **C3. Setting sources.** `--setting-sources user,project,local`, with no `--add-dir`. The user source is the rep's own `HOME`, so the kit's skills load as personal skills with bare names, as in the owner's sessions. Plan 40 used `project,local` with `--add-dir <kit>`. Task 4's pilot checks the init record: the set of its `skills` holds the 12 kit skills, and the set of its `agents` holds the two kit agents. The checks compare sets, because the rep `HOME` is also an ancestor of the working folder, so a skill may be listed twice, as in the owner's sessions. The pilot shows what the init record lists before C11's check is fixed.
- **C4. User-level context.** The rep `HOME` has no `CLAUDE.md`, no rules, no output style, no plugins and no `.zshenv`. Phase 3 loaded the owner's user-level instructions, an isolation gap that the plan 40 record names. This run closes that gap. So a verdict that differs from Phase 3 may owe part of the difference to it, and the record says so. Auto-memory stays on, because prepare-handoff's step 5 writes to memory. The memory folder is the rep's own.
- **C5. The `for`-loop gap.** With the redirected `HOME`, every `~/…` read, in any shell form, reads the rep's own folder. Only an absolute path into the real home, or the keychain link, can still reach it. A PreToolUse hook, `kit/guard.py`, closes that path for every tool, including a Bash command that runs inside a `for` loop. It takes each path token of the input, puts the rep's `HOME` in place of `~`, `$HOME` and `${HOME}`, and resolves `..` and symlinks with `os.path.realpath`. It denies the call when a resolved token lies inside the real home or its `/System/Volumes/Data` form, or when the input names `Library/Keychains`. Its reason always starts `blocked by the workspace path guard:`, so a probe can tell the guard's denial from one by the auto-mode classifier. The `--settings` deny rules repeat this for the file tools. The Bash sandbox would also close the gap. It was not chosen, because it limits writes and network, which the arms use (the brief folder, `uv`), and that would change rep behavior. The item's done-when ("a probe rep shows a `for`-loop `ls ~/…` denied") maps to Task 4's guard probe: a `for`-loop `ls` of the real home by its absolute path, and one through `~/Library/Keychains`, are both denied with the guard's reason, in the rep and in a subagent it dispatches, and a `for`-loop `ls ~/.claude/skills` lists the kit. Known limit: `t9` names the real home path in five files. A rep that greps for it, or opens a path that one of them cites, gets a guard denial, and the denial rule can then void that rep.
- **C6. Scratch folders.** The reps run one after the other. Each rep has its own `HOME` and `TMPDIR`. The runner refuses to start while `/private/tmp/phr100/` holds anything, and it moves the rep's `HOME` to `$CTL/homes/<rep>/` when the rep ends. So no rep can see another rep's files. The item allows either fix. Running one at a time also keeps the reps directory free of siblings.
- **C7. `credential_expires_at`.** The runner saves each turn's stream as `turn<n>.jsonl`, writes the `result` record as `turn<n>.json` and the `system`/`init` record as `turn<n>.init.json`, and copies the session's transcripts into `project/`. Before it writes, `kit/postprocess.py` removes the key `credential_expires_at` at any depth from every JSON object. A final check fails the rep (`kit_error`) if the string is anywhere under the rep's results folder.
- **C8. Shim.** As plan 40's: `git`, `python3`, `python3.13` and `uv` link to `/opt/homebrew/bin/`. `gh` is plan 40's stub, except that it logs to `$HOME/.cache/gh-calls.log`.
- **C9. Model and flags.** `claude-opus-5-5` at `xhigh` effort for all three arms. Plan 40's `config.env` set `MODEL_PLAN=opus` and `EFFORT_PLAN=xhigh`, and the `opus` alias now resolves to `claude-opus-5-5`. The reviewer subagents run at the model the skill names (`sonnet`). `--permission-mode auto` and `--strict-mcp-config` are plan 40's. `--max-budget-usd 30` for each turn is new: it only stops a runaway turn, and a stopped turn voids.
- **C10. Audit translation.** The frozen Audit section of `$RED/PROTOCOL.md`, with the Addendum's skill-path exception, protected paths under the real home. Each rep now has its own `HOME`. The audit (`kit/extract.py`) reads it this way (table B, which the owner chose at plan review, D2):

  | Frozen rule | Table B (default) | Table A (literal) |
  |---|---|---|
  | Protected roots under `~` | the real home, by absolute path or by its `/System/Volumes/Data` form, and anything that resolves into it | as B, plus the frozen roots inside the rep's `HOME` (`~/.claude`, `~/.cache/agent-skills`, `~/.cache/pondworks`, `~/Projects`, `~/.agents`, `~/.codex`, `~/.gemini`) |
  | Allowed paths | the whole rep `HOME`, except `~/Library` | the rep's repo, origin, shim, `TMPDIR`, kit folders, own project folder and own brief folder |
  | Listing the handoffs folder | allowed: it holds only this rep's folder | voids |
  | The reps directory | `/tmp/phr100/` itself, and anything in it outside the rep's `HOME`, voids | same |
  | Spelling | `/tmp`, `/private/tmp` and `/System/Volumes/Data/private/tmp` are one folder: the audit maps all three to `/private/tmp` before it compares | same |
  | Fragments | unchanged: `handoffs/red`, `agent-skills/handoff-brief`, `plan40-draft`, `Projects/agent-skills`, `specs/handoff-briefs`, `red-baseline-handoff` | same |
  | Failed turn, denial | unchanged | same |

  Read by flag, the 25 void reps of these three arms in Phase 3 would mostly clear under table B (20 of 25) and mostly stay void under table A (3 of 25). The 5 that stay void under B named the fragment `Projects/agent-skills`. With no user-level instructions to name that path (C4), it may come up less often. These counts assume the reps behave as in Phase 3, which C4 changes.
- **C11. Harness checks that void.** The Addendum checked the main checkout's `skills/` tree before and after each batch. The kit replaces that with a per-rep check: the hash of the rep `HOME`'s kit folders must equal the hash of `KIT_COMMIT`'s copy before turn 1 and after the last turn. A mismatch voids the rep. So does an init record whose `skills` or `agents` differ from the kit's (C3).
- **C12. Prompts.** As the counted Phase 3 reps used them: `v1` takes `c4b.t1.loc.txt` then `c4b.t2.txt`. `b2` takes `c2.t1.loc.txt`, `b2.t2.txt` and `c2.t3.txt`. `c4a-neg` takes `c4a-neg.t1.txt` then `c4a.t2.txt`, with no location line. The kit holds byte-identical copies. `@REP@` becomes the rep's repo path.
- **C13. Launch.** The controller launches the runner from its session through `env -i`, as plan 98's kit did. `$RED/PROTOCOL.md` has the owner launch from a plain terminal, and `run_rep.sh` there refuses when `CLAUDECODE` is set (Channel 5). `env -i` drops `CLAUDECODE` and the session's variables, and the rep `HOME` drops the user-level files. The runner refuses if any variable named `CLAUDE*` other than `CLAUDE_CODE_DISABLE_ADVISOR_TOOL` reaches the rep. `$RED/changes.log` records this change.
- **C14. Cost.** Phase 3 reps cost $8 to $14 (`v1`), $4 to $8 (`b2`) and about $0.85 (`c4a-neg`). Pilots: about $15. Expected, with 6 reps per arm: about $120 plus pilots. Worst case, 10 dispatched per arm: about $230 plus pilots. Task 4 measures the real cost of each arm's pilot or first rep and restates the estimate before the batches.

## File map

| File | Change | Task |
|---|---|---|
| `specs/baseline/red-baseline-handoff-rerun/kit/guard.py`, `test_rerun_guard.py` | new: the PreToolUse guard and its tests | 1 |
| `build/suites.toml` | one `[[suite]]` table, `handoff-rerun-kit` | 1 |
| `specs/baseline/red-baseline-handoff-rerun/kit/run_rep.sh`, `run_batch.sh`, `make_reps.py`, `postprocess.py`, `arms.tsv`, `prompts/`, `test_rerun_runner.py` | new: the runner, the registry tool, the strip step and their tests | 2 |
| `specs/baseline/red-baseline-handoff-rerun/kit/README.md` | new (deviation, execution 2026-11-18): how to run the kit, `KIT_COMMIT`, and every execution deviation, so that a reader of the kit alone finds them | 2 |
| `specs/baseline/red-baseline-handoff-rerun/kit/extract.py`, `tally.py`, `test_rerun_extract.py` | new: plan 40's audit and tally, forked for the new layout | 3 |
| `specs/baseline/red-baseline-handoff-rerun/kit/prompts/isolation_probe.txt`, `guard_probe.txt` | new: probe prompts | 4 |
| `specs/baseline/red-baseline-handoff-rerun/scores/` | new: the scores TSVs | 5 |
| `specs/baseline/red-baseline-handoff-rerun.md` | new: the record | 4 to 6 |
| `specs/completed/red-baseline-handoff-briefs-2026-10-10.md` | one pointer section at the end | 6 |

---

### Task 1: The guard

**Files:**
- Create: `specs/baseline/red-baseline-handoff-rerun/kit/guard.py`
- Create: `specs/baseline/red-baseline-handoff-rerun/kit/test_rerun_guard.py`
- Modify: `build/suites.toml` (a new `[[suite]]` table, in name order)

**Interfaces:**
- Produces: `guard.py`, run as `/usr/bin/python3 <kit>/guard.py --real-home <path>`. It reads the PreToolUse payload on stdin. It uses `HOME` from its environment as the rep's `HOME` and the payload's `cwd` for relative paths. To deny, it prints `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "<reason>"}}` and exits 0. To allow, it prints nothing and exits 0. On any internal error it denies, because a crashed hook fails open.
- Produces: `denied(tool_name: str, tool_input: dict, home: str, cwd: str, real_home: str) -> str | None`, which returns the reason or None. It scans the Bash `command` (first line only when the command holds a heredoc, as `$RED/tools/extract.py`'s `scanned` does), the fields `file_path`, `path`, `notebook_path`, and a Glob `pattern`.
- Produces: `SETTINGS_JSON`, the value of `--settings`, built by the runner (Task 2) from this template:

  ```json
  {"permissions": {"deny": ["Read(//Users/**)", "Edit(//Users/**)", "Write(//Users/**)",
     "Read(~/Library/**)", "Edit(~/Library/**)", "Write(~/Library/**)"]},
   "hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command",
     "command": "/usr/bin/python3 <kit>/guard.py --real-home <real home>"}]}]}}
  ```

- [ ] **Step 1: Write the failing tests** in `test_rerun_guard.py`. Each builds a payload and runs `guard.py` as a subprocess with `HOME` set to a temporary rep home that holds a `Library/Keychains` symlink to a temporary "real home". Assert the decision and `returncode == 0` in every test. Every deny asserts a reason that starts `blocked by the workspace path guard:`.
  - `test_denies_for_loop_absolute_real_home`: Bash `for d in a b; do ls <real>/.claude/skills 2>/dev/null; done` → deny.
  - `test_denies_system_volumes_form`: Bash `cat /System/Volumes/Data<real>/x` → deny.
  - `test_denies_through_keychain_link`: Bash `ls ~/Library/Keychains/../..` → deny. Read `file_path` `<home>/Library/Keychains/x` → deny.
  - `test_denies_keychains_name`: Bash `for d in Library/Keychains; do ls ~/$d; done` → deny.
  - `test_allows_tilde_kit_read`: Bash `for d in .claude/skills; do ls ~/$d; done` → allow. Read `~/.claude/skills/prepare-handoff/SKILL.md` → allow.
  - `test_allows_repo_relative`: Bash `git status && ls ../` from cwd `<home>/work/r281` → allow.
  - `test_malformed_payload_denies`: stdin `not json` → deny, exit 0.

- [ ] **Step 2: Run the tests and see them fail**

  Run: `cd specs/baseline/red-baseline-handoff-rerun/kit && uv run --with pytest python -m pytest -q test_rerun_guard.py`
  Expected: errors, `guard.py` not found.

- [ ] **Step 3: Write `guard.py`**, with `denied` as in Interfaces. Take the path-token and `..` regexes from `$RED/tools/extract.py` (`PATH_TOKEN`, `DOTDOT_TOKEN`).

- [ ] **Step 4: Run the tests and see them pass**

  Run: the Step 2 command. Expected: `7 passed`.

- [ ] **Step 5: Register the suite.** Add to `build/suites.toml`, in name order:

  ```toml
  [[suite]]
  name = 'handoff-rerun-kit'
  dir = 'specs/baseline/red-baseline-handoff-rerun/kit'
  with = ['pytest']
  notes = ['Plan 100 kit: guard, runner (stub claude, no model) and audit tests. bash and git required.']
  ```

  Run: `uv run python build/run_suites.py --check && uv run python build/run_suites.py handoff-rerun-kit`
  Expected: the check exits 0, and the suite reports `7 passed`.

- [ ] **Step 6: Commit** `guard.py`, the test and `build/suites.toml`: `feat(handoff-rerun): add the kit's real-home guard (plan 100)`.

### Task 2: The runner

**Files:**
- Create: `specs/baseline/red-baseline-handoff-rerun/kit/run_rep.sh`, `run_batch.sh`, `make_reps.py`, `postprocess.py`, `arms.tsv`
- Create: `specs/baseline/red-baseline-handoff-rerun/kit/prompts/` (7 files, C12)
- Create: `specs/baseline/red-baseline-handoff-rerun/kit/test_rerun_runner.py`

**Interfaces:**
- Consumes: `guard.py` and `SETTINGS_JSON` (Task 1).
- Produces: `arms.tsv`, tab-separated, header `arm template prompts`: `v1 t9 c4b.t1.loc.txt,c4b.t2.txt`, `b2 t2 c2.t1.loc.txt,b2.t2.txt,c2.t3.txt`, `c4a-neg t3 c4a-neg.t1.txt,c4a.t2.txt`, and two probe arms that Task 4 fills: `probe-iso t3 isolation_probe.txt` and `probe-guard t3 guard_probe.txt`. Prompt files live in `kit/prompts/`. `run_rep.sh` fills `@REP@` with the rep's repo path and `@REAL@` with the real home.
- Produces: `make_reps.py ARM PHASE COUNT BATCH`. It appends rows to `$CTL/registry.tsv` (header `rep arm phase template kit_commit prompts`) and rep ids to `$CTL/batches/BATCH.txt`. Ids continue from `r281` and are never reused. It refuses an id whose `$CTL/results/<id>` or `$CTL/homes/<id>` exists.
- Produces: `run_rep.sh REP`. It builds the rep `HOME` (C1, C2, C8), checks the kit hash (C11), runs every turn with the Global Constraints command, post-processes (C7), checks for the strip, and moves the `HOME` to `$CTL/homes/<rep>/`. Into `$CTL/results/<rep>/` it writes: `meta.txt` (rep, arm, phase, template, `KIT_COMMIT`, model, effort, `claude --version`, `kit_sha_before`, `kit_sha_after`), `session-id`, `turn<n>.prompt.txt`, `turn<n>.jsonl`, `turn<n>.json`, `turn<n>.init.json`, `turn<n>.stderr`, `turn<n>.git.txt` (as plan 40's run_rep.sh writes it), `project/` (with the session's `memory/`), and `handoffs/`, a copy of the rep `HOME`'s whole `.cache/agent-skills/handoffs/` tree. Plan 40's extract reads its Brief directory and Memory sections from those two folders.
- Produces: `run_batch.sh BATCH`, which runs the batch's reps one at a time and skips a rep that has results.
- Produces: `postprocess.strip(obj) -> obj` and `postprocess.py split <stream.jsonl> <out-dir> <n>`, which writes the stripped `turn<n>.jsonl`, `turn<n>.json` and `turn<n>.init.json`. `postprocess.py strip-tree <dir>` strips every `.json` and `.jsonl` file under a folder in place.
- Environment: `PHR_ROOT` (default `/private/tmp/phr100`), `PHR_CTL` (default `~/.cache/agent-skills/handoffs/rerun100`), `PHR_TEMPLATES` (default `~/.cache/pondworks/templates`), `CLAUDE_BIN` (default `command -v claude`), `KIT_COMMIT` (required; `make_reps.py` records it and `run_rep.sh` reads it from the registry).

- [ ] **Step 1: Record `KIT_COMMIT`.** Run `git rev-parse HEAD` on the execution branch before its first commit. Write the value into the record's Method section (Task 4 creates it) and into each registry row.

  > Deviation (execution, 2026-11-18, execution brief default 1): `KIT_COMMIT` is `92f6a379d4bb77ba53adb360f8171ebd9c295ce8`, the branch base, recorded right after the branch was cut and before Task 1. Task 1 commits first, so "before its first commit" could not be met at this step. The base is the commit that the Kit commit constraint names. `git diff --stat 275edc1 92f6a37 -- skills/ agents/ commands/` is empty, so the kit text equals the text at plan 100's merge. The kit's `README.md` repeats this note.

- [ ] **Step 2: Copy the prompts.** Copy the seven files of C12 from `$RED/prompts/` into `kit/prompts/`. Then:

  Run: `cd specs/baseline/red-baseline-handoff-rerun/kit/prompts && for f in *; do cmp "$f" ~/.cache/agent-skills/handoffs/red/prompts/"$f" || echo DIFF "$f"; done`
  Expected: no output.

- [ ] **Step 3: Write the failing tests** in `test_rerun_runner.py`. They use a stub `claude` (a shell script set as `CLAUDE_BIN`), a temporary `PHR_ROOT`, `PHR_CTL` and `PHR_TEMPLATES`, and a one-commit template repo. The stub reads stdin, writes a stream with an `init`, an `assistant` and a `result` record whose `result` and `modelUsage` hold `credential_expires_at`, and runs the probe actions that the test names.
  - `test_strip_removes_field_everywhere`: after one rep, no file under `$PHR_CTL/results/<rep>/` holds the string `credential_expires_at`, and `turn1.json` keeps `total_cost_usd`.
  - `test_brief_tree_is_copied`: the stub writes `$HOME/.cache/agent-skills/handoffs/other-name/brief.md`. After the rep, `$PHR_CTL/results/<rep>/handoffs/other-name/brief.md` exists.
  - `test_second_rep_sees_nothing_of_first`: rep 1's stub writes a marker into `$HOME`, `$TMPDIR`, the repo and `$HOME/.cache/agent-skills/handoffs/<rep>/`. Rep 2's stub lists `$PHR_ROOT`, `$HOME`, `$TMPDIR` and `$HOME/.cache/agent-skills/handoffs` recursively into its output. Rep 2's output names no rep-1 marker and no rep-1 id. Rep 1's `HOME` is in `$PHR_CTL/homes/`.
  - `test_refuses_nonempty_root`: with a stray file in `$PHR_ROOT`, `run_rep.sh` exits 3 and runs no turn.
  - `test_home_holds_kit_and_no_user_files`: the stub checks that `$HOME/.claude/skills` holds exactly the 12 kit skills, that `~/.claude/CLAUDE.md`, `~/.claude/settings.json` and `~/.zshenv` are absent, and that `$HOME/Library/Keychains` is a link. `meta.txt` has equal `kit_sha_before` and `kit_sha_after`.
  - `test_env_holds_no_session_variables`: the stub writes its environment. It holds no name starting `CLAUDE` other than `CLAUDE_CODE_DISABLE_ADVISOR_TOOL`, and `HOME` and `TMPDIR` are the rep's.
  - `test_resume_on_later_turns`: a two-prompt arm calls the stub with `--session-id` then `--resume` and the same id.

- [ ] **Step 4: Run the tests and see them fail**

  Run: `uv run python build/run_suites.py handoff-rerun-kit`
  Expected: the 7 new tests fail or error, and Task 1's 7 pass.

- [ ] **Step 5: Write `postprocess.py`, `make_reps.py`, `run_rep.sh` and `run_batch.sh`** to the Interfaces block. `run_rep.sh` copies the template with `cp -R` and checks the Global Constraints' HEAD, refs and clean status. It builds the kit folders with `git -C <repo> archive "$KIT_COMMIT" <paths> | tar -x`. It fills `@REP@` in each prompt. After each turn it runs `postprocess.py split`. After the last turn it copies the session's project folder from `$H/.claude/projects/` into `project/` and the handoffs tree into `handoffs/`, runs `strip-tree` on the results folder, then greps for the field. The kit hash is `shasum -a 256` over the sorted file list and contents of `.claude/skills`, `.claude/agents` and `.claude/commands`.

- [ ] **Step 6: Run the tests and see them pass**

  Run: `uv run python build/run_suites.py handoff-rerun-kit`
  Expected: `14 passed`.

- [ ] **Step 7: Commit** the runner files, the prompts and the test: `feat(handoff-rerun): add the kit runner with per-rep homes (plan 100)`.

### Task 3: The audit and the tally

**Files:**
- Create: `specs/baseline/red-baseline-handoff-rerun/kit/extract.py`, `tally.py`
- Create: `specs/baseline/red-baseline-handoff-rerun/kit/test_rerun_extract.py`

**Interfaces:**
- Consumes: Task 2's results layout, registry and parked homes.
- Produces: `extract.py BATCH` and `extract.py --rep REP`, a fork of `$RED/tools/extract.py`. It writes `$CTL/results/<rep>/extract.md`, in the same sections as plan 40's, and `audit.json` (`rep`, `arm`, `phase`, `valid`, `problems`, `flags`, `denials`, `cost_usd`). The extract reads the repo from `$CTL/homes/<rep>/work/<rep>`.
- Produces: `classify(token: str, cwd: str, home: str, real_home: str, root: str) -> str | None`, which returns a flag or None by the table that the owner picked for C10. It maps each `/tmp` spelling to `/private/tmp` (C10, Spelling) before it compares.
- Produces: `tally.py PHASE`, a fork of `$RED/tools/tally.py` that reads `$CTL`. It checks each quote against its extract and prints counts and verdicts by the Global Constraints' thresholds.

- [ ] **Step 1: Write the failing tests** in `test_rerun_extract.py`. They write small transcripts and results under a temporary `$PHR_CTL`, then run the audit.
  - `test_tilde_kit_read_is_valid`: a subagent's Bash `ls ~/.claude/skills/writing-plans` → valid. So is a Read of the same file spelled `/tmp/phr100/<rep>/.claude/…` and `/private/tmp/phr100/<rep>/.claude/…`.
  - `test_real_home_voids`: Read `<real>/.claude/skills/x` → void, flag names the path.
  - `test_library_link_voids`: Bash `ls ~/Library/Keychains/..` → void.
  - `test_reps_dir_voids`: Bash `ls /tmp/phr100` and `ls /private/tmp/phr100` from the repo → void.
  - `test_fragment_voids`: Bash `ls ~/Projects/agent-skills` → void on the fragment.
  - `test_handoffs_listing`: Bash `ls ~/.cache/agent-skills/handoffs` → valid under table B (void under table A).
  - `test_error_turn_voids`: a `turn2.json` with `is_error: true` → void, problem `turn 2: <subtype>`.
  - `test_kit_hash_mismatch_voids`: unequal `kit_sha_before` and `kit_sha_after` → void.
  - `test_init_skill_mismatch_voids`: a `turn1.init.json` whose `skills` lack `prepare-handoff` → void.

- [ ] **Step 2: Run the tests and see them fail**

  Run: `uv run python build/run_suites.py handoff-rerun-kit`
  Expected: the 9 new tests fail or error.

- [ ] **Step 3: Write `extract.py` and `tally.py`.** Start from the `$RED/tools/` files. Change only the paths, `normalize` (`~` becomes the rep's `HOME`), the protected and allowed sets (C10), the harness checks (C11), and the read of `turn<n>.json`.

- [ ] **Step 4: Run the tests and see them pass**

  Run: `uv run python build/run_suites.py handoff-rerun-kit`
  Expected: `23 passed`.

- [ ] **Step 5: Commit** `extract.py`, `tally.py` and the test: `feat(handoff-rerun): fork plan 40's audit and tally for per-rep homes (plan 100)`.

### Task 4: Probes and pilot (paid)

**Files:**
- Create: `specs/baseline/red-baseline-handoff-rerun/kit/prompts/isolation_probe.txt`, `guard_probe.txt`
- Create: `specs/baseline/red-baseline-handoff-rerun.md` (Method, Probes, Pilot)

- [ ] **Step 1: Owner gate.** Tell the owner C14's estimate and the cost of this task's runs (about $15). Wait for the owner's yes before Step 3. Log the answer in `## Decisions`.

- [ ] **Step 2: Log the change in `$RED/changes.log`.** Append one line: the date, plan 100's kit path and `KIT_COMMIT`, the arms, C10's table as chosen, C11, C13, and "no frozen file edited; freeze id unchanged".

- [ ] **Step 3: Isolation probe.** Write `isolation_probe.txt`. It asks for one line each, YES or NO with a quote: text loaded from a `CLAUDE.md`, an output style, rules, a SessionStart hook's text, a memory index, the names of the skills and agents available. Run one rep of arm `probe-iso` with phase `probe`.
  Expected: the CLAUDE.md, output-style, rules, hook and memory lines read NO. The skill and agent lines name the 12 kit skills and 2 kit agents. `turn1.init.json` agrees. `turn1.json` has `subtype` `success`.

- [ ] **Step 4: Guard probe.** Write `guard_probe.txt`. It asks the rep to run three commands as written and to report each output: `for d in .claude/skills; do ls ~/$d; done`, `for d in a; do ls @REAL@/.claude; done` and `for d in a; do ls ~/Library/Keychains/..; done`. Run one rep of arm `probe-guard` with phase `probe`.
  The prompt then asks the rep to dispatch one `general-purpose` subagent, at `model: sonnet`, that runs the second command and reports its output.
  Expected: the first lists the 12 kit skills. The second and third, and the subagent's command, each end with a tool result that starts `blocked by the workspace path guard:`. A denial with any other reason does not count. If the rep declines to run a command, so that no tool call exists, reword the prompt more plainly and rerun. Record the results as the item's probe (C5).

- [ ] **Step 5: Pilot reps.** Run one `c4a-neg` rep, then one `v1` rep, with phase `pilot`. Run `extract.py --rep` on each.
  Expected: both valid. In the `v1` rep, the subagent transcripts show the fact-checker and cold-reader dispatches, and any skill-text read resolves under the rep `HOME`. No flag names the real home.

- [ ] **Step 6: Restate the cost.** Take each pilot's `total_cost_usd`. If the expected total for 6 reps per arm differs from C14 by more than 25%, tell the owner before Task 5.

- [ ] **Step 7: Write the record's Method, Probes and Pilot sections.** Method gives `KIT_COMMIT`, the Claude Code version, the command, C1 to C13 by reference, and the differences from Phase 3: user-level context (C4), the model and CLI version (C9), the setting sources (C3), the kit holding `KIT_COMMIT`'s text for all 12 skills, and the empty `~/.cache/agent-skills/cc-guide`, which `t9`'s drift spec cites.

- [ ] **Step 8: Commit** the probe prompts and the record: `test(handoff-rerun): record the isolation and guard probes and the pilot (plan 100)`.

### Task 5: The batches (paid)

**Files:**
- Create: `specs/baseline/red-baseline-handoff-rerun/scores/<arm>.tsv` (3 files)

- [ ] **Step 1: Run 5 reps of each arm**, in this order: `c4a-neg`, `b2`, `v1`, each as its own batch (`make_reps.py <arm> rerun100 5 rerun100-<arm>`, then `run_batch.sh rerun100-<arm>` in the background). After each batch, run `extract.py rerun100-<arm>`.

- [ ] **Step 2: Replace voids.** For each void rep, make one more rep of its arm, up to 10 dispatched per arm. If an arm reaches 10 with fewer than 5 valid reps, stop and bring the void list to the owner.

- [ ] **Step 3: Score.** Follow `$RED/PROTOCOL.md` Scoring step 2. Dispatch one scorer subagent for each arm, with `$RED/rubric.md` and the arm's first 5 valid extracts. The `v1` scorer runs on `opus`, the others on `sonnet`. Each scorer writes `$CTL/scores/rerun100/<arm>.tsv`. For `v1` and `b2`, the scorer reads each rep's repo under `$CTL/homes/<rep>/work/<rep>`.

- [ ] **Step 4: Tally.**

  Run: `uv run python specs/baseline/red-baseline-handoff-rerun/kit/tally.py rerun100`
  Expected: every quote found, and a verdict for each arm. Rescore any line whose quote is not found.

- [ ] **Step 5: Copy the scores into the repo** with the real home written as `~real`. Then:

  Run: `git grep -n -e "$HOME" -e credential_expires_at -- specs/baseline/red-baseline-handoff-rerun/`
  Expected: no output.

- [ ] **Step 6: Commit** the scores: `test(handoff-rerun): score v1, b2 and c4a-neg on the shipped skills (plan 100)`.

### Task 6: The record

**Files:**
- Modify: `specs/baseline/red-baseline-handoff-rerun.md`
- Modify: `specs/completed/red-baseline-handoff-briefs-2026-10-10.md` (one section at the end)

- [ ] **Step 1: Write the Results section.** One table, as Phase 3's: arm, valid, failing reps, per criterion, verdict. Then one evidence line per failing rep and criterion (rep: criterion: paraphrase), the voids with their flags, the cost per arm and in total, and the comparison with Phase 3 (`v1` 3 valid, 1 failing; `b2` 3 valid, 1 failing; `c4a-neg` 0 of 5), read against C4's difference.

- [ ] **Step 2: Answer the open Phase 3 points.** Say what this run shows for each: Validation 1 on the shipped cold reader (its false-positive rate on a brief with no planted defect), Validation 2 on the widened and anchored description, and the `b2` route on the shipped private-decision trigger.

- [ ] **Step 3: Add the pointer** to the plan 40 record: a section `## Re-run on the shipped text (plan 100, <date>)` with one line per arm (valid count, verdict) and the record's path.

- [ ] **Step 4: Check the record**

  Run: `uv run python build/check_links.py && git grep -n -e "$HOME" -- specs/baseline/red-baseline-handoff-rerun.md`
  Expected: `0 broken`, and no grep output.

- [ ] **Step 5: Commit**: `docs(handoff-rerun): record the re-run of v1, b2 and c4a-neg (plan 100)`.

Then run the Plan Completion Protocol. Its step 3 ticks the four items. Other lanes build kits too, so first check on `origin/main` whether another kit has already ticked a kit item. If one has, add a `→ progress` note that names this kit, and do not tick it twice. The main item's `→ done` note gives each arm's verdict and the record's path. The three kit items' notes name the kit and the test or probe that meets each done-when (Task 1's guard tests and Task 4's guard probe; `test_second_rep_sees_nothing_of_first`; `test_strip_removes_field_everywhere`).
