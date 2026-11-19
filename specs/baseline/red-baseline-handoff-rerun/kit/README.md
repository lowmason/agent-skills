# Plan 100 handoff rerun kit

This kit reruns three arms of plan 40's prepare-handoff baseline: `v1`, `b2` and `c4a-neg`. Plan 100 (`specs/plans/100-prepare-handoff-rerun.md`, retired later to `specs/plans/completed/`) builds it. Each rep runs `claude -p` in its own `HOME`. That `HOME` holds the shipped skills from one commit, `KIT_COMMIT`.

## Files

- `run_rep.sh REP` runs one registered rep.
- `run_batch.sh BATCH` runs the reps of one batch, one at a time.
- `make_reps.py ARM PHASE COUNT BATCH` registers new reps.
- `postprocess.py` splits each turn's stream and removes `credential_expires_at`.
- `guard.py` is the PreToolUse hook that denies any tool input that reaches the real home. It also denies a recursive or whole-disk search rooted at a folder that holds the real home.
- `arms.tsv` gives each arm's template and prompt files, in turn order.
- `templates.tsv` gives the expected `HEAD` of each fixture template.
- `prompts/` holds byte-identical copies of plan 40's prompt files.
- `shim/gh` is the stand-in GitHub CLI that each rep gets.
- `extract.py` audits each rep and writes its extract. `tally.py` checks the scores and prints the verdicts.
- `test_rerun_guard.py`, `test_rerun_runner.py` and `test_rerun_extract.py` are the tests. They run as suite `handoff-rerun-kit`.

## How to run it

1. Register the reps: `KIT_COMMIT=<sha> /usr/bin/python3 make_reps.py c4a-neg rerun100 5 rerun100-c4a-neg`.
2. Run the batch: `run_batch.sh rerun100-c4a-neg`.

The controller launches the runner through `env -i` (plan 100, C13). The runner refuses to start a rep while `PHR_ROOT` holds anything (exit 3). A rep id never runs twice.

These environment variables control the kit:

| Variable | Default | Use |
|---|---|---|
| `PHR_ROOT` | `/private/tmp/phr100` | The folder that holds the running rep's `HOME`. |
| `PHR_CTL` | `~/.cache/agent-skills/handoffs/rerun100` | The control folder: registry, batches, results and parked homes. |
| `PHR_TEMPLATES` | `~/.cache/pondworks/templates` | Plan 40's fixture templates, used read-only. |
| `PHR_TEMPLATE_HEADS` | `templates.tsv` in the kit | A file of `template<TAB>head` rows. The tests point it at their own template. |
| `PHR_PROMPTS` | `prompts/` in the kit | The folder of prompt files. The tests point it at their own prompts. |
| `PHR_KIT_REPO` | the git checkout that holds the kit | The repo that `git archive KIT_COMMIT` reads. |
| `CLAUDE_BIN` | `command -v claude` | The claude binary. The tests set a stub. |
| `KIT_COMMIT` | none, required by `make_reps.py` | The commit whose skills fill each rep's `HOME`. `run_rep.sh` reads it from the registry. |

The kit must sit in an agent-skills checkout that holds `KIT_COMMIT`, or `PHR_KIT_REPO` must name one.

## What a rep gets

The rep's `HOME` is `PHR_ROOT/<rep>`. It holds:

- `.claude/skills/` with the 12 kit skills, `.claude/agents/` with `code-reviewer.md` and `task-reviewer.md`, and `.claude/commands/deferred.md`. All come from `git archive KIT_COMMIT`.
- `work/<rep>/`, a copy of the arm's template. Its origin is the bare repo `git/<rep>.git`, with `main` pushed and `origin/HEAD` set.
- `.local/bin/` with the `gh` stub and links to `/opt/homebrew/bin` for `git`, `python3`, `python3.13` and `uv`. The stub logs each call to `~/.cache/gh-calls.log` in the rep's `HOME`.
- `tmp/`, the rep's `TMPDIR`. It does not keep all scratch files apart, because macOS `mktemp` ignores `TMPDIR` (see the guard's known limits).
- `Library/Keychains`, a link to the real `~/Library/Keychains`. Claude Code needs it to keep the login.

The rep's `HOME` has no `CLAUDE.md`, no `settings.json`, no rules and no `.zshenv`.

It has a minimal `.gitconfig` that sets only `user.name` (`Pondworks Rep`) and `user.email` (`rep@pondworks.invalid`). Nothing else comes from any real git config. Plan 40's reps committed with the owner's global identity. A rep with no identity gets git's guessed identity and its warnings, and that could change what the rep does. The controller ruled for this file.

Before the first turn, the runner checks the template's `HEAD`, its refs and its status. It also checks that the hash of the rep's kit folders equals the hash of `KIT_COMMIT`'s copy. The hash is `shasum -a 256` over the sorted file list and the contents of `.claude/skills`, `.claude/agents` and `.claude/commands`.

## Results layout

The runner writes `PHR_CTL/results/<rep>/`:

- `meta.txt` has one `key=value` line for each of `rep`, `arm`, `phase`, `template`, `kit_commit`, `model`, `effort`, `claude`, `kit_sha_before` and `kit_sha_after`. A turn that exits non-zero adds the line `turn <n> exited <status>; later turns not run`. A failed strip check adds a `kit_error=` line.
- `session-id` holds the session's id.
- `turn<n>.prompt.txt` is the prompt, with `@REP@` and `@REAL@` filled in.
- `turn<n>.jsonl` is the turn's stream. `turn<n>.json` is its `result` record. `turn<n>.init.json` is its `system`/`init` record.
- `turn<n>.stderr` is the turn's standard error.
- `turn<n>.git.txt` gives the repo's branch, status and log after the turn, as plan 40's runner wrote it.
- `project/` is a copy of the session's project folder, with its `memory/`.
- `handoffs/` is a copy of the whole `~/.cache/agent-skills/handoffs/` tree of the rep's `HOME`. The rep's own brief folder is `handoffs/<rep>/`.

No JSON or JSONL file in the results folder holds `credential_expires_at`. A final check fails the rep (exit 4) if the string is anywhere in that folder.

When the rep ends, the runner moves its `HOME` to `PHR_CTL/homes/<rep>/`. The audit reads the repo from `PHR_CTL/homes/<rep>/work/<rep>`.

## The audit and the tally

`extract.py BATCH` or `extract.py --rep REP` audits each rep and writes `PHR_CTL/results/<rep>/extract.md` and `audit.json`. The extract has the same sections as plan 40's. `tally.py PHASE` checks each score's quote against its extract and prints the counts and verdicts. Both are forks of plan 40's `tools/` files.

The audit reads the frozen VOID rules by table B of plan 100's C10:

- `~` is the `HOME` the rep ran with, `PHR_ROOT/<rep>`. The whole rep `HOME` is allowed, except its `Library` folder.
- A path into the real home voids, and so does a glob whose leading parts can match it, such as `/Users/*/.ssh`. So does a path into, or through, the rep's `Library` folder, because `Library/Keychains` links into the real home. An input that names a `Library` path part and, later, a `Keychains` part also voids, even with no `~` before it. Examples are `Library//Keychains` and `cd Library && ls Keychains`. The bare word `keychains`, in a grep say, names no path and does not void.
- The reps directory voids, and so does anything in it outside the rep's `HOME`.
- `/tmp`, `/private/tmp` and `/System/Volumes/Data/private/tmp` are one folder. The real home's `/System/Volumes/Data` form is the real home. The audit compares paths without case.
- A recursive or whole-disk search rooted at a folder that holds the real home voids, by the guard's rule (see below). An example is `find / -name SKILL.md`.
- The fragments, a failed turn and the denial rule are unchanged.
- `audit.json`'s `denials` list every denied tool call of the rep. The audit reads every transcript: the session's, each subagent's and each turn's stream. A denial is a tool result that starts with `Permission for this action was denied` (the auto-mode classifier) or holds `blocked by the workspace path guard:`. The audit pairs it with its tool call and keeps one entry for each `tool_use_id`. Each entry names its transcript and says whether a subagent made the call. The scorer voids a rep whose failure traces to a denial.

The audit resolves `..` in the text of each path. It never reads the paths, because the rep's `HOME` is parked by then. The real home is the audit's own `HOME`.

These harness checks also void a rep (C11 and the wait ceiling below):

- `kit_sha_before` and `kit_sha_after` in `meta.txt` are missing or differ.
- `meta.txt` has a `kit_error=` line or a `turn <n> exited <status>` line.
- `turn1.init.json` is missing. Or an init record's `skills` lack one of the 12 kit skills, or its `agents` lack `code-reviewer` or `task-reviewer`. The check compares sets. Extra names, such as Claude Code's built-in skills and agents, do not void, and a name listed twice counts once. A later turn's init record is checked when it exists. Task 4's pilot shows the real init record. If it lists extra names that look user-level, the controller decides then.
- A `turn<n>.stderr` holds `Background tasks still running`.

`tally.py` reads `PHR_CTL/scores/PHASE/<arm>.tsv`. `v1` and `b2` pass when at least 4 of their first 5 valid reps pass every criterion. `c4a-neg` passes when at most 1 of its first 5 valid reps fails. The tally takes an arm's reps from the audits, not the score file: the first 5 by id whose `audit.json` is valid, names that arm and has `PHASE` as its phase, less any rep the score file marks VOID. So a probe or pilot rep never counts in another phase. The tally exits 1 and names the gap when a counted rep has no rows, or has no row for a criterion that the arm's other rows use.

## Deviations

**KIT_COMMIT.** `KIT_COMMIT` is `92f6a379d4bb77ba53adb360f8171ebd9c295ce8`, the base of the execution branch. The plan asked for the branch's `HEAD` before its first commit. The value was recorded right after the branch was cut, before Task 1. Task 1 committed first, so that step could not come first. The base is the commit that the plan's Kit commit constraint names. `git diff --stat 275edc1 92f6a37 -- skills/ agents/ commands/` is empty, so the kit text equals the text at plan 100's merge.

**The wait ceiling.** The `env -i` list of each rep turn also sets `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=2400000` (40 minutes). In print mode, Claude Code stops background subagents 10 minutes after the main turn ends. That voided plan 45's gate reps. Without the variable, a stopped fact-checker or cold reader could score as a FAIL, not a VOID. The runner admits only two `CLAUDE*` names: `CLAUDE_CODE_DISABLE_ADVISOR_TOOL` and `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`. It refuses any other. Task 3's audit voids a rep whose `turn<n>.stderr` holds `Background tasks still running`. That void is a harness check, not a change to the frozen VOID rules.

**Claude.ai skill sync off.** The `--settings` JSON of each rep turn also sets `"syncClaudeAiSkills": false` (plan 100, owner decision D4). Without it, Claude Code downloads the skills enabled on the claude.ai account into the rep's `~/.claude/skills/synced/` during a turn. That changed the kit hash of probe rep r282, so the audit voided it. The download also lands at an unpredictable time, so a rep could see other skills in a later turn. With the setting, each rep sees only the 12 kit skills and Claude Code's built-in skills.

**Fixes after the batches.** The batches ran with the kit at commit 1563e98. The final-review fixes landed afterward: f7f8ab6 matches the `/System/Volumes/Data` prefix in any case, and 10c0e31 makes the tally take each arm's reps from the audits and refuse a gap in the rows. They change no recorded verdict. No rep used any Data-volume spelling, every counted rep has a full row set, and no probe rep sits in a score file. The fixed tally prints the same counted reps and verdicts.

The completion-gate fixes came next. 48c6eeb makes the runner find the session transcript without a pipe to `head`, which could kill it with SIGPIPE (exit 141). f5173d4 makes the guard deny a search rooted at a folder that holds the real home. db54f5d makes the audit void that search and list the denials from every transcript. 8341ec1 closes four gaps in the search parser that a scoped review found: a `#` read as a comment, a search after a reserved word such as `do`, a substitution inside double quotes, and the `2` of `2>/dev/null` read as the root. These fixes also change no recorded verdict. A read-only rerun of the new audit rules over reps r281 to r302, before and after 8341ec1, gave these results:

- Only r289 gains the new flag, for its subagent's `find /`. r289 is already void by owner decision D5. No counted rep gains a flag, and probes r282 and r283 gain none.
- The denials are the seven that the record's Denials paragraph names: r289 1, r292 1, r293 2, r294 2 and r300 1. Probes r282 and r283 keep their 2 and 3 guard denials. No other rep has a denial.

**Template heads as data.** The expected template `HEAD`s live in `templates.tsv`, not in the runner's code. The tests set `PHR_TEMPLATE_HEADS` to their own file.

## The guard's known limits

The guard (`guard.py`) checks each path token of a tool input. It cannot see everything:

- It cannot see a path that a command builds at run time, for example from pieces joined in a variable.
- It can miss an obscured route to the keychain link, for example a `Keychain?` glob after a `cd`.
- It denies a glob with more than 1000 matches, and a glob walk that takes more than 2 seconds.
- A single guard call takes about 3 seconds in the worst case.
- It checks only the first line of a Bash command that holds `<<` anywhere, because a heredoc's body is content. So a search or a real-home path on a later line of such a command passes. The audit applies the same rule.
- It finds a search by its command words: `find`, `ls -R`, `grep -r`, `rg`, `fd`, `du`, `tree`, `mdfind` and `locate`, also after `cd`, `sudo`, `env`, `xargs` or `sh -c`. It misses a walk that another program makes, such as `python3 -c` with `os.walk('/')`.
- It cannot see a relative name after a `cd` above the real home. An example is `cd /Users && cat <name>/...`: the second token has no leading `/` or `~` and no `..`.
- Reps stay apart only because they run one at a time. macOS `mktemp` ignores `TMPDIR` and writes under `/var/folders`. Reps also write literal `/tmp` paths. Both are shared between reps and with the owner's sessions.

The audit (`extract.py`, Task 3) is the backstop, but it shares the guard's limits on paths built at run time, on relative names after a `cd` and on walks by other programs. It reads the tool inputs of every tool call of the rep, never the tool results. It voids a rep whose input names a path in the real home. It does not scan results, because fixture `t9` names the real home path in five files, so a result scan would void reps that only read the fixture.
