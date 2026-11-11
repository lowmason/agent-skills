# cc_guide Owner Rulings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the owner's 2026-10-31 rulings on three cc_guide backlog items. A Stop-hook loop guard is the flag or a waiver per wiring file. The drift notice reaches Claude as SessionStart context in the CLI and the Desktop app. Each citation records the hash of the section text its file was reviewed against.

**Architecture:** Item 1 is register text plus a waiver hint in `check_conformance.py`'s Stop-hook findings. The existing per-(check, file) waiver match already accepts the form. Item 2 changes the two writers of `notice.json` (`notice.py`, and `notice.sh`'s `fail_notice`) to add `hookSpecificOutput.additionalContext` beside `systemMessage`. `show` prints the file as it stands. Item 3 gives `baseline.json` a `format` marker and a `cited` map. `baseline cite` writes the map, an editorial `accept` carries it forward, and `lint.stale_citations` reads it.

**Tech Stack:** Python 3.13 (stdlib, pytest), POSIX `sh`, TOML, JSON; the repo's lints.

**Spec:** none. This is `/deferred` step 5's **Plan** disposition (2026-11-11): the three deferred items below are the requirements, with their 2026-10-31 owner rulings and D1–D5. Background: `specs/completed/claude-code-drift-automation-spec.md` (R2.3, R2.4, R5, R7, R9, Decision 8, Stage 4), which Tasks 2 to 4 amend.

## Requirements

From `specs/deferred_items.md`, trimmed to what decides the work (`[…]` marks a cut):

- Section `cc-guide-files-backlog (no plan; /cc-guide files, branch worktree-cc-guide-files-backlog) — 2026-10-13`:
  > Stop-hook guard design (`build/cc_guide/conformance.toml:165`, check `stop-hook-guard`; `build/check_conformance.py:534`). The rule and the check flag a Stop hook script that never reads `stop_hook_active`. The guide accepts checking the transcript instead […], and its Pattern 3 recommends capping retries in the hook itself […]; neither needs the flag. The rule text and the check must change together. […] Done when: the owner picks what counts as a loop guard […], the rule and the check agree on it, a test covers each accepted form, and both files' contradictions are cleared.
  > → progress 2026-10-31 (owner ruling): a loop guard is the flag (a read of `stop_hook_active`) or a waiver per hook, recorded in `build/cc_guide/conformance.toml`, that names the guard the hook uses instead.

- Section `49-claude-code-drift-automation — 2026-10-18`:
  > A Desktop-visible channel for the drift notice […]. In the Desktop app […] the SessionStart hook runs and its `systemMessage` is recorded in the transcript […], but the default transcript view displays nothing […]. `notice.sh show` records `notice-shown` right after printing, whether or not the surface displayed the line […]. Work: pick a channel Desktop shows […] and a way for `show` to tell the surfaces apart […]. Files: `build/cc_guide/notice.sh`, `.claude/settings.json`, spec R9 and Decision 8, `build/CLAUDE.md`. […] Done when: the owner decides the channel, and a new Desktop session shows the notice at its start, or terminal-only is recorded as the accepted scope.
  > → progress 2026-10-31 (owner ruling): a Desktop channel via SessionStart's plain stdout, which reaches Claude as context in both the CLI and Desktop, so the first reply can name the notice.

- Section `cc-guide-files-2026-10-21 (no plan; /cc-guide files, lowmason/agent-skills#94 and branch claude/cc-guide-hooks-files-2.1.306) — 2026-10-21`:
  > Two branches can give a section's `changed` and a citing file's stamp the same release, and `cli.py lint` then calls the file fresh though no verifier read the newer text. […] R2.4's rule that `accept` stays above every citer's stamp reads only the stamps on its own branch […]. Files: `build/cc_guide/baseline.py`, `build/cc_guide/lint.py`, drift spec R2.4. […] Done when: the owner picks a remedy and a test shows that two such branches, merged in either order, leave the file STALE, or the owner records the gap as accepted.
  > → progress 2026-10-31 (owner ruling): `text_hash` at cite time. Record each cited section's text hash when the file is cited, in the citation or beside it, and let the lint compare hashes.

- Section `cc-guide-hashed-keys (no plan; branch feat/cc-guide-hashed-keys) — 2026-10-05` (folded in by F3):
  > Mark baseline.json's format so older code refuses it […]. A top-level format key would make any older reader exit 2 ("holds exactly sections, groups and llms"), now and at any later format change. Files: `build/cc_guide/state.py`, `baseline.py`, their tests, R2.3. […] Revisit if: an open branch predates the merge, or baseline.json's format changes again.

## Owner review (defaults this plan settles; change any at plan review)

- **F1. Surface split (item 2).** Default: drop it. Under D2 both surfaces receive the notice, so `show` keeps recording `notice-shown` at print time (`build/cc_guide/notice.sh:33`), with no code change. Effect if wrong: a day's notice is spent on a Desktop session whose first reply does not quote it. Task 6 tests exactly that.
- **F2. The `stop-hook-guard-literal` deviation (item 1).** Default: keep it, and reword its `reason` and `revisit` to name both accepted forms (Task 1 Step 6). The check alone still cannot verify a transcript read or a retry cap. Effect if wrong: the register misdescribes the check, and a `/cc-guide files` review raises the contradiction again.
- **F3. The format-marker watch item.** Default: fold it in and close it at completion. Task 3 adds `"format": 3` (text block keys were layout 1, hashed keys layout 2). The loader refuses any other value, and code older than this plan refuses the file by its key set. New code does not read the old layout either: no compatibility path. Two side effects of that strictness:
  - During execution: after Task 3 commits, the worktree's code refuses `main`'s old file (see Global Constraints, Loader window).
  - After the merge reaches the local `main`: a session started in any checkout whose code predates the merge runs `refresh`, whose `check --hook` exits 2. That writes a "check failed" notice to the shared `~/.cache/agent-skills/cc-guide/notice.json`, which every session then shows until a checkout with this plan's code runs a good check. Bringing such checkouts up to date is the owner's call.
- **F4. The note for Claude (D3).** Default exact copy, phrased as a fact per `hooks.md:1184` ("Text framed as out-of-band system commands can trigger Claude's prompt-injection defenses"):
  `The line above is the Claude Code drift notice for this repository. The repository owner wants the first reply of this session to quote it, because the Desktop app does not display hook messages.`
  ASCII only, with no `"` or `\`, so `notice.sh` can write it with `printf`. It goes in `additionalContext` only: `systemMessage` keeps the line alone, so the terminal line reads as today.
- **F5. A citation with no recorded hash (item 3).** Default: the stamp rule alone judges it, as today. Task 4 records a hash for every citing file `cli.py lint` does not list as STALE, and every later `baseline cite` records one. So the gap left is a citation written or extended by hand without a `cite` run. Alternative: after the migration, a cited section with no record reads as STALE. That closes the gap, but every new citation then needs a `cite` run before it reads fresh, and fixtures in `test_lint.py`, `test_cli.py`, `test_check.py` and `test_packets.py` change. Effect if wrong: a hand-stamped citation can still collide across branches, as #93 and #94 did.
- **F6. An editorial `accept` carries records forward (item 3).** Default: for each accepted section, every `cited` record equal to the old `text_hash` moves to the new one. A substantive accept moves none. Without this, an editorial accept would flag every citer through the hash rule, against R2.4 ("Editorial: a new `text_hash` only"). Residual: an editorial accept on one branch and a new `cite` of the same section on another give a false STALE after the merge. That errs toward one more review.
- **F7. Re-review of `notice.sh` (T7).** Default: Task 5 runs `/cc-guide files build/cc_guide/notice.sh`. The file now relies on a fact the guide covers only in general terms (`specs/guides/claude-code-customization-guide.md:313`): a synchronous SessionStart hook's `additionalContext` reaches Claude in both surfaces. A not-covered row comes to you there (a guide addition through `/cc-guide`, a register entry, or no action). `notice.py` gets no citation of its own: `notice.sh`'s citation covers the pair, as its header says. Alternative: skip Task 5 and log a deferred item. Cost: one packet, about $0.30–1.
- **F8. The check names the waiver route (item 1).** Default: both `stop-hook-guard` findings end with ` (or waive this file under stop-hook-guard, naming the guard the hook uses)`. So the rule and the message agree, and a person who sees the finding learns the second accepted form. Effect if wrong: the waiver form is documented only in the register.
- **F9. The 2026-10-03 measurement lines stay (item 2).** Default: the drift spec's `:87` (measured hook output channels) and `:1450` (sources) are left as they are. They record what the 2.1.288 docs said, and both are still true. The new docs lines go into R9.2's amendment. T2's other lines change in Task 2. A sweep of the drift spec, `.claude/skills/cc-guide/SKILL.md`, `hooks/README.md` and the guide found no other line that items 2 or 3 make false. Decision 8's rejected list (async output reaches only Claude) and R8's `cite` steps (about lines 937 and 964) stay.

## Global Constraints

- **Anchors.** Line numbers are as of `696fa5d`. The old text in each step is the match key, not the line number. In `build/cc_guide/conformance.toml`, find the `stop-hook-guard` `[[check]]` and the `stop-hook-guard-literal` `[[exception]]` by their `id` lines.
- **Order.** This plan executes after plan 88 (branch `claude/agent-skills-handoff-plan-3d2805`) merges into `main`, and one execution at a time. Plan 88 edits another entry in `conformance.toml`. Cut the execution branch from a `main` that holds plan 88.
- **Loader window.** From Task 3's commit until the local `main` ref holds the merge, this branch's code refuses `main`'s `baseline.json`, because `check` reads the local `main` unless given `--worktree`. In that window, run `cli.py check` only with `--worktree`. A session start in the execution worktree runs `refresh`, whose failed check would put an error notice in the shared cache. Subagents start no SessionStart hook. Before a new session starts in the worktree in that window (to resume execution, say), confirm that a good check under a day old is on record, so `refresh` exits at once: `uv run --directory build/cc_guide python -c "import notice, state, time; ok = notice.last_ok(state.default_cache()); print(ok is not None and time.time() - ok < 86400)"` prints `True`. If it prints `False`, start the session from the main checkout instead.
- **Files.** A task edits only its listed files. During execution, `specs/deferred_items.md` changes only in the completion protocol. The planning commit writes its `→ planned` notes.
- **Citations.** No task restamps a citation, except Task 5 through `/cc-guide files`. After each task, `uv run python build/cc_guide/cli.py lint` lists no STALE file other than `skills/writing-skills/SKILL.md`. If it lists a file this plan edited, Task 5 adds that file (T4).
- **Spec amendments.** Edits to `specs/completed/claude-code-drift-automation-spec.md` are the exact blocks below, each tagged `(owner, plan 89, 2026-11-11)`. The spec's status lines stay as they are.
- **Exact copy.** F4's note, F8's suffix, the loader's messages and the spec and doc blocks are exact copy.
- **Suites and gates.** Run tests through `uv run python build/run_suites.py <suite> -- <pytest args>` from the repo root: suite `build` for `build/test_check_conformance.py`, suite `cc_guide` for `build/cc_guide/`. Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English, and end with the executing session's attribution trailer, written below as `<the session's trailer>`.
- **Shell.** The Bash tool runs zsh. Quote any `===` in an echo, and use `/usr/bin/grep` for sweeps. Scratch files go under `~/.cache/agent-skills/scratch/plan89-work/`. Never `cd` in a step: a `cd` moves the session's working directory, and later repo-root commands then read the wrong paths. Run code that needs `build/cc_guide/` as its directory with `uv run --directory build/cc_guide …`.
- **Who runs a task.** Tasks 1 to 4 go to implementer subagents. Tasks 5 and 6 are marked **(controller)**. The controller runs them itself with no implementer dispatch: `/cc-guide files` dispatches its own verifier agent, and Task 6 needs the owner.
- **Public repository.** The plan and commits hold no private detail.
- **Completion.** No spec retires: the drift spec is already in `specs/completed/`. Protocol step 3 ticks the three items and the F3 watch item with `→ done <date>` notes. Item 2's note records Task 6's result. The owner-only item "Observe the once-a-day half of the notice in real sessions" (section `49-claude-code-drift-automation`) closes only if Task 6's sitting also observed it.

## Review Focus

1. An editorial `accept` must leave its citers fresh (R2.4), whatever the hash rule says: `test_an_editorial_accept_leaves_its_citers_fresh` (Task 4).
2. A refused `baseline cite` must write nothing, `baseline.json` included: the existing `test_cite_refuses_with_one_error_line_and_writes_nothing` keeps asserting `dirty(repo) == []` (Task 4 Step 8 runs it).
3. Two branches that cite different files must merge without a conflict in `baseline.json`: `test_two_branches_that_cite_different_files_merge_cleanly` (Task 4).
4. The terminal line must read as today, with no note in it: `test_refresh_error_notice_has_the_python_payload` compares the whole object, and the existing `shown()` helper keeps reading `systemMessage` as the bare line (Task 2).
5. A `baseline.json` from a later layout must be refused with a message that names both formats, never misread: `test_baseline_must_carry_this_codes_format`, its `4` case (Task 3).

## Decisions

- **D1** (owner, brief, 2026-11-11): one plan for the three owner-ruled items, with no spec ("Yes, split it"). Applied in: the header's **Spec:** line.
- **D2** (owner, brief, 2026-11-11): the notice is JSON with both fields: the line in `systemMessage` for the CLI, and in `hookSpecificOutput.additionalContext` for Claude in the CLI and Desktop. This refines the 2026-10-31 ruling's "plain stdout". Docs: `hooks.md:1205` and `:1331-1337` (2.1.322). Reading: `additionalContext` holds the line followed by D3's note, so it is not the same text as `systemMessage` (F4). Applied in: Task 2.
- **D3** (owner, brief, 2026-11-11): the owner check is "a new Desktop session's first reply names the notice", and the notice text gains one line for Claude. This replaces the item's "shows the notice at its start". The wording is confirmed at plan review (F4). Applied in: Task 2, Task 6.
- **D4** (owner, brief, 2026-11-11): a waiver per wiring file is the ruling's "waiver per hook": an `[[exception]]` with `check = 'stop-hook-guard'` and `artifacts` naming the file that wires the Stop command. Its `reason` names the hook script and the guard it uses instead. It waives every Stop command in that file. No schema change. Applied in: Task 1.
- **D5** (owner, brief, 2026-11-11): `baseline cite` records each cited section's `text_hash` beside the citation, in `build/cc_guide/baseline.json`, keyed by citing file and section ID, and `cli.py lint` compares it with the section's current `text_hash`. The citation form (R4.1) and the citing files stay as they are. Applied in: Task 3, Task 4.
- **D6** (owner, plan review, 2026-11-11): "Approve as is", in answer to "Approve plan 89 with F1 to F9 as recommended?" F1 to F9 keep their defaults, F4's note wording included. Applied in: Tasks 1 to 6, Global Constraints.

## Related open items (taken into account, not absorbed)

- Owner-only "Observe the once-a-day half of the notice in real sessions" (section `49-claude-code-drift-automation`): its terminal check still works under D2, and it may share Task 6's sitting.
- The other cc_guide backlog items, plan 88's branch and worktree, and branch `claude/deferred-abc549` stay as they are.
- Evidence for D2's channel: this plan was written in a Desktop app session that received a plugin's SessionStart `additionalContext` at its start.

---

### Task 1: A Stop-hook loop guard is the flag or a waiver (item 1)

**Files:**
- Modify: `build/check_conformance.py:517-538` (`check_stop_hook_guard`) and a new module constant beside it
- Modify: `build/cc_guide/conformance.toml` (the `stop-hook-guard` `[[check]]` and the comment above it; the `stop-hook-guard-literal` `[[exception]]`)
- Test: `build/test_check_conformance.py`

**Interfaces:**
- Produces: `check_conformance.STOP_GUARD_WAIVER: str`, equal to `' (or waive this file under stop-hook-guard, naming the guard the hook uses)'`, appended to both `stop-hook-guard` finding messages.

- [ ] **Step 1: Write the tests**

In `build/test_check_conformance.py`, add a test-side copy of the suffix and two pins beside `test_hook_var_quoted_can_be_waived`:

```python
WAIVER_ROUTE = ' (or waive this file under stop-hook-guard, naming the guard the hook uses)'
GATE = stop_tree('"$CLAUDE_PROJECT_DIR"/.claude/hooks/gate.sh', 'hooks/gate.sh', '#!/usr/bin/env bash\nexit 2\n')
STOP_WAIVER = {'id': 'gate-caps-retries', 'type': 'deviation', 'check': 'stop-hook-guard',
               'sections': ['a.one'], 'artifacts': ['hooks/README.md'],
               'guide': 'A Stop hook guards against a loop.',
               'reason': 'hooks/gate.sh caps its retries with a per-session counter.',
               'evidence': 'Fixture.', 'revisit': 'If the check can verify a retry cap.'}


def test_an_unguarded_stop_hook_names_the_waiver_route(tmp_path):
    root = fixture_repo(tmp_path, GATE)
    assert cc.run(root) == [
        'hooks/README.md: stop-hook-guard (a.one): JSON block at line 1: Stop command runs hooks/gate.sh, '
        'which never reads stop_hook_active' + WAIVER_ROUTE]


def test_a_stop_hook_guard_waiver_covers_a_hook_that_guards_another_way(tmp_path):
    root = fixture_repo(tmp_path, GATE, register=FIXTURE_REGISTER + exception_toml(STOP_WAIVER))
    assert cc.run(root) == []


def test_a_stop_hook_guard_waiver_goes_stale_once_the_hook_reads_the_flag(tmp_path):
    files = {**GATE, 'hooks/gate.sh': '#!/usr/bin/env bash\n# reads stop_hook_active\n'}
    root = fixture_repo(tmp_path, files, register=FIXTURE_REGISTER + exception_toml(STOP_WAIVER))
    assert cc.run(root) == [
        'hooks/README.md: stale-waiver (a.one): exception gate-caps-retries (hooks/gate.sh caps its retries '
        'with a per-session counter.) waives stop-hook-guard here, but the file no longer violates it: '
        'remove the entry, or this file from it']
```

Then append `+ WAIVER_ROUTE` to the expected message of every `stop-hook-guard` finding: lines 791 and 792 (`test_stop_hook_guard_flags_an_unguarded_or_unresolvable_script`), 2432 (`test_stop_hook_guard_survives_a_command_shlex_rejects`), 2723 (`test_stop_hook_guard_flags_an_unguarded_script_behind_a_runner`) and 2731 (`test_stop_hook_guard_still_flags_a_runner_with_no_repo_script`). Leave lines 1809 and 1836 alone: they are `hook-scripts-executable` findings with a similar message.

Place the new tests after `stop_tree` (about line 2705), which `GATE` calls. `fixture_repo` leaves its files untracked, so `hook-scripts-executable` judges `hooks/gate.sh` by its execute bit: after each `fixture_repo` call, run `(root / 'hooks/gate.sh').chmod(0o755)`. If `cc.run` reports another check's finding on the fixture, change the fixture until only the line under test stands. Never loosen the assertion.

- [ ] **Step 2: Run the tests to see the RED**

Run: `uv run python build/run_suites.py build -- test_check_conformance.py -k "stop_hook or waiver_route"`
Expected: the new route test and the four edited tests FAIL, each on a message that lacks the suffix. The two waiver tests PASS at BASE. They pin D4's form, which `apply_waivers` already accepts, so a pass here is not a failed RED.

- [ ] **Step 3: Implement the suffix**

In `build/check_conformance.py`, define `STOP_GUARD_WAIVER` above `check_stop_hook_guard`, and append it to both `Finding` messages in that function. No other check changes.

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run python build/run_suites.py build -- test_check_conformance.py`
Expected: all pass.

- [ ] **Step 5: Reword the rule**

In `build/cc_guide/conformance.toml`, in the `stop-hook-guard` `[[check]]`, replace:

```toml
rule = 'A command wired to Stop runs a repo hook script that reads stop_hook_active, directly or through uv run or python.'
```

with:

```toml
rule = 'A command wired to Stop runs a repo hook script that reads stop_hook_active, directly or through uv run or python, or the file that wires it holds a stop-hook-guard waiver whose reason names the hook script and the guard it uses instead.'
```

Above that `[[check]]`, after the comment line `# them, so every fix attempt that edits a file starts the count over.`, add:

```toml
# A hook that guards another way (a transcript read, a retry cap) is waived per
# wiring file (owner ruling 2026-10-31, plan 89).
```

- [ ] **Step 6: Reword the deviation (F2)**

In the `stop-hook-guard-literal` `[[exception]]`, replace the `reason`, `evidence` and `revisit` lines with:

```toml
reason = "The stop-hook-guard check in build/check_conformance.py verifies only a Stop script that reads stop_hook_active. A hook that guards by a transcript read or a retry cap needs a stop-hook-guard waiver on its wiring file that names that guard, because the check cannot verify one. The repo's one Stop hook reads the flag."
evidence = '/cc-guide files settle, packet 20261020T143604-files (check_conformance.py:532); owner ruling E1, 2026-10-20; owner ruling 2026-10-31 (a loop guard is the flag or a waiver per hook), plan 89.'
revisit = 'If the check gains a way to verify a transcript read or a retry cap.'
```

Change the comment above it, `# The repo's Stop guard reads stop_hook_active, the one guard the lint can verify.`, to:

```toml
# The lint verifies only the stop_hook_active read; other guards need a waiver.
```

- [ ] **Step 7: Verify the register and the lints**

Run: `uv run --with pyyaml python build/check_conformance.py`
Expected: exit 0, no violations.
Run: `uv run python build/cc_guide/cli.py lint`
Expected: exit 0, with the one STALE line for `skills/writing-skills/SKILL.md`.

- [ ] **Step 8: Commit**

```bash
git add build/check_conformance.py build/test_check_conformance.py build/cc_guide/conformance.toml
git commit -m "feat(conformance): accept a stop-hook-guard waiver as a loop guard

A Stop hook may guard by reading stop_hook_active, or by a waiver on its
wiring file that names the guard it uses instead (owner ruling 2026-10-31).
The rule text says so, the findings name the waiver route, and the
stop-hook-guard-literal deviation names both forms.

<the session's trailer>"
```

### Task 2: The drift notice reaches Claude as context (item 2)

**Files:**
- Modify: `build/cc_guide/notice.py` (module docstring lines 5-7; `write_notice`; new `CONTEXT_NOTE`, `EVENT` and `payload`)
- Modify: `build/cc_guide/notice.sh` (`fail_notice`, lines 58-69)
- Test: `build/cc_guide/test_notice.py`, `build/cc_guide/test_notice_sh.py`
- Modify: `build/CLAUDE.md:108-112`, `CLAUDE.md:97`
- Modify: `specs/completed/claude-code-drift-automation-spec.md` (Decision 8, R9.2, Stage 4)

**Interfaces:**
- Produces: `notice.EVENT = 'SessionStart'`; `notice.CONTEXT_NOTE: str` (F4's exact copy); `notice.payload(message: str) -> dict`, which returns `{'systemMessage': message, 'hookSpecificOutput': {'hookEventName': EVENT, 'additionalContext': f'{message}\n{CONTEXT_NOTE}'}}`. `write_notice` writes `json.dumps(payload(message))`.

- [ ] **Step 1: Write the failing tests**

In `build/cc_guide/test_notice.py`, change the assertion in `test_the_notice_is_one_ascii_json_line_written_before_its_digest` to:

```python
    assert json.loads(text) == notice.payload('cc-guide · x → /cc-guide')
```

and add:

```python
NOTE = ('The line above is the Claude Code drift notice for this repository. The repository owner wants the first '
        'reply of this session to quote it, because the Desktop app does not display hook messages.')


def test_the_payload_shows_the_line_and_gives_claude_the_line_and_the_note():
    assert notice.payload('cc-guide · x → /cc-guide') == {
        'systemMessage': 'cc-guide · x → /cc-guide',
        'hookSpecificOutput': {'hookEventName': 'SessionStart',
                               'additionalContext': 'cc-guide · x → /cc-guide\n' + NOTE}}
    assert NOTE.isascii() and '"' not in NOTE and '\\' not in NOTE
```

In `build/cc_guide/test_notice_sh.py`, after `test_refresh_without_uv_leaves_the_fixed_error_notice`, add:

```python
def test_refresh_error_notice_has_the_python_payload(fake_uv):
    '''fail_notice writes the object notice.py writes, field for field.'''
    home, _ = fake_uv
    notice.record_check(cache_of(home), 1, datetime.now().astimezone() - timedelta(days=2, hours=1), 'old')
    quiet(sh(home, 'refresh', env={'CC_GUIDE_UV_FALLBACK': str(home / 'nowhere')}))
    proc = sh(home, 'show')
    assert json.loads(proc.stdout) == notice.payload(f'cc-guide · {NO_UV} · last good check 2 d ago → install uv')
```

- [ ] **Step 2: Run the tests to see the RED**

Run: `uv run python build/run_suites.py cc_guide -- test_notice.py test_notice_sh.py`
Expected: the three tests above FAIL with `AttributeError: module 'notice' has no attribute 'payload'`. The rest pass.

- [ ] **Step 3: Implement the Python writer**

In `build/cc_guide/notice.py`, add `EVENT`, `CONTEXT_NOTE` and `payload` per the Interfaces block, and make `write_notice` use `payload`. In the docstring, replace the whole notice.json bullet (its three lines, through `show prints it as it stands.`) with:

```
- notice.json: empty when nothing is due, else one ASCII JSON line holding
  {"systemMessage": <line>, "hookSpecificOutput": {"hookEventName":
  "SessionStart", "additionalContext": <line, newline, CONTEXT_NOTE>}}.
  Written here, or by refresh for its own two errors; show prints it as it
  stands.
```

and change `write_notice`'s docstring to `notice.json, then its digest: one ASCII JSON line holding payload(message), or an empty file when nothing is due.`

- [ ] **Step 4: Implement the shell writer**

In `build/cc_guide/notice.sh`, give `fail_notice` the same object. Add `NOTE='<F4's exact copy>'` beside the other constants at the top, with the comment `# notice.py's CONTEXT_NOTE, word for word; test_notice_sh.py compares the two`. The `printf` format writes `{"systemMessage": "%s", "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "%s\\n%s"}}` from `"$message" "$message" "$NOTE"`. Inside single quotes, `\\n` makes `printf` print the two characters `\n`, which JSON reads as a newline. Leave `show` as it is.

- [ ] **Step 5: Run the suite to see it pass**

Run: `uv run python build/run_suites.py cc_guide`
Expected: all pass. `test_cli.py`'s and `test_notice_sh.py`'s `shown()` helpers still read `systemMessage` as the bare line.

- [ ] **Step 6: Update the docs**

In `build/CLAUDE.md`, replace:

```
one of `refresh`'s own two error notices, once a day per notice. It prints in
the terminal; the Desktop app runs the hook and records its output but
displays nothing, and since `show` marks a notice shown when it prints, a
Desktop session that starts first on a day uses that day's showing up for the
terminal too. The async `refresh` runs `check --hook` once the last good check
```

with:

```
one of `refresh`'s own two error notices, once a day per notice. The terminal
shows the notice line, its `systemMessage`. The Desktop app displays nothing,
but the same object's `hookSpecificOutput.additionalContext`, the line and a
note asking the first reply to quote it, reaches Claude in both, and `show`
marks a notice shown when it prints. The async `refresh` runs `check --hook` once the last good check
```

In `CLAUDE.md`, replace `its notice shows in terminal sessions only` (line 97) with `the terminal shows its notice, and Claude gets it as context in the CLI and Desktop`.

- [ ] **Step 7: Amend the drift spec**

In `specs/completed/claude-code-drift-automation-spec.md`, Decision 8 (about line 154), replace:

```
8. **Trigger: a SessionStart hook pair in this repo.** A synchronous `show`
   prints a precomputed `systemMessage`, the only hook channel shown to the
   user in the terminal, at most once a day. The Desktop app runs the hook and
   records the message but does not display it, and `show` marks a notice
   shown when it prints, so a Desktop session that starts first on a day also
   uses that day's showing up for the terminal (owner, plan 49, 2026-10-18,
   from Task 10's live run); a Desktop-visible channel is a deferred item. An
   async `refresh` recomputes it without delaying the session. Rejected:
```

with:

```
8. **Trigger: a SessionStart hook pair in this repo.** A synchronous `show`
   prints a precomputed notice object at most once a day. Its `systemMessage`
   is the only hook channel shown to the user in the terminal. The Desktop app
   runs the hook and records the message but does not display it (owner,
   plan 49, 2026-10-18, from Task 10's live run). So the object also carries
   the line, with a note asking that the first reply quote it, as
   `hookSpecificOutput.additionalContext`, which reaches Claude in the CLI and
   the Desktop app. Both surfaces receive the notice, so `show` marks it shown
   when it prints (owner, plan 89, 2026-11-11). An
   async `refresh` recomputes it without delaying the session. Rejected:
```

In R9.2 (about line 1034), replace:

```
prints `~/.cache/agent-skills/cc-guide/notice.json`, a JSON object holding one
`systemMessage` that Python escaped when writing it, unless the same notice
was already shown today.
```

with:

```
prints `~/.cache/agent-skills/cc-guide/notice.json`, a JSON object holding the
notice line as `systemMessage` and, under `hookSpecificOutput` with
`hookEventName` `SessionStart`, the line and a note asking that the first reply
quote it as `additionalContext`, unless the same notice was already shown
today. Python escapes both strings when it writes them; `refresh`'s own error
notices carry no character that needs escaping (owner, plan 89, 2026-11-11;
`hooks.md:1149, 1184, 1205, 1331-1337` at 2.1.322).
```

In the Stage 4 acceptance (about line 1382), replace:

```
   - `show` prints nothing on exit 0 and a single `systemMessage` on exit 1 or
     2, and passes R12.5 in its launchd-like environment.
   - The owner sees the notice at a live session start, at most once a day.
```

with:

```
   - `show` prints nothing on exit 0 and a single notice object on exit 1 or
     2, and passes R12.5 in its launchd-like environment.
   - The owner sees the notice at a live session start, at most once a day.
     In the Desktop app, the first reply of a new session quotes it (owner,
     plan 89, 2026-11-11).
```

- [ ] **Step 8: Verify and commit**

Run: `uv run python build/cc_guide/cli.py lint` (exit 0, the one STALE line) and `bash build/run_commit_lints.sh` (`commit lints passed`).

```bash
git add build/cc_guide/notice.py build/cc_guide/notice.sh build/cc_guide/test_notice.py build/cc_guide/test_notice_sh.py build/CLAUDE.md CLAUDE.md specs/completed/claude-code-drift-automation-spec.md
git commit -m "feat(cc-guide): give the drift notice to Claude as SessionStart context

notice.json now carries the line as systemMessage, which the terminal
shows, and as hookSpecificOutput.additionalContext with a note asking the
first reply to quote it, which reaches Claude in the CLI and the Desktop
app (owner rulings 2026-10-31 and 2026-11-11).

<the session's trailer>"
```

### Task 3: Mark baseline.json's format (F3)

**Files:**
- Modify: `build/cc_guide/state.py` (new `FORMAT`; `parse_baseline`, lines 316-350)
- Modify: `build/cc_guide/baseline.py` (`init`, lines 70-94)
- Modify: `build/cc_guide/baseline.json` (migration)
- Test: `build/cc_guide/test_state.py` (the fixture dicts at lines 22 and 175, and new tests), `build/cc_guide/test_baseline.py`
- Modify: `specs/completed/claude-code-drift-automation-spec.md` (R2.3)

**Interfaces:**
- Produces: `state.FORMAT = 3`. `parse_baseline` returns a dict with exactly `format`, `sections`, `groups`, `llms` and `cited`, where `cited` maps a repo-relative path to a dict of section ID to a `text_hash` string (`TEXT_HASH_RE`). `baseline.init` returns that shape with `cited` empty, keys in the order `format`, `sections`, `groups`, `llms`, `cited`.

- [ ] **Step 1: Write the failing tests**

In `build/cc_guide/test_state.py`, give the two fixture dicts (lines 22 and 175) `'format': 3` first and `'cited': {}` last, and add:

```python
@pytest.mark.parametrize('value', [None, 2, 4, '3'])
def test_baseline_must_carry_this_codes_format(value):
    raw = json.loads(baseline_text())
    if value is None:
        del raw['format']
    else:
        raw['format'] = value
    with pytest.raises(state.SetupError) as err:
        state.parse_baseline(json.dumps(raw))
    assert str(err.value) == f'{state.BASELINE}: format {value!r} is not 3, the format this code reads'


def test_baseline_holds_exactly_its_five_keys():
    raw = {**json.loads(baseline_text()), 'extra': 1}
    with pytest.raises(state.SetupError) as err:
        state.parse_baseline(json.dumps(raw))
    assert str(err.value) == f'{state.BASELINE}: holds exactly format, sections, groups, llms and cited'


@pytest.mark.parametrize('cited', [[], {'a.md': []}, {'a.md': {'x.one': 'abc'}}])
def test_cited_maps_each_file_to_section_hashes(cited):
    raw = {**json.loads(baseline_text()), 'cited': cited}
    with pytest.raises(state.SetupError) as err:
        state.parse_baseline(json.dumps(raw))
    assert str(err.value) == f'{state.BASELINE}: cited must map each file to section ID -> text_hash'
```

Adjust the helper names (`baseline_text`, imports) to what `test_state.py` already uses. In `build/cc_guide/test_baseline.py`, add:

```python
def test_init_writes_the_format_first_and_an_empty_cited_map_last(docs_dir):
    s = fixture_state(docs_dir)
    assert list(s) == ['format', 'sections', 'groups', 'llms', 'cited']
    assert (s['format'], s['cited']) == (3, {})
```

- [ ] **Step 2: Run the tests to see the RED**

Run: `uv run python build/run_suites.py cc_guide -- test_state.py test_baseline.py`
Expected: the new tests FAIL, and so does every test whose fixture dict now holds the two new keys, on `holds exactly sections, groups and llms`.

- [ ] **Step 3: Implement the loader and init**

In `parse_baseline`, check the format first, so a later layout gets the format message rather than the key-set one: when `raw` is a dict whose `format` is not the int `FORMAT` (a `bool` or a `str` fails), raise `SetupError(f'{BASELINE}: format {raw.get("format")!r} is not {FORMAT}, the format this code reads')`. Then the key-set check raises `f'{BASELINE}: holds exactly format, sections, groups, llms and cited'`. A malformed `cited` adds the problem `cited must map each file to section ID -> text_hash` to the existing list. In `baseline.init`, build the dict in the order the Interfaces block gives.

- [ ] **Step 4: Migrate the committed file**

Run from the repo root:

```bash
uv run --directory build/cc_guide python -c "import json, state; from pathlib import Path; p = Path('baseline.json'); d = json.loads(p.read_text()); p.write_text(state.dump_baseline({'format': state.FORMAT, **d, 'cited': {}}), encoding='utf-8')"
```

Expected: `git diff --stat build/cc_guide/baseline.json` shows 3 insertions and 1 deletion: `"format": 3,`, the comma after `llms`'s closing bracket, and `"cited": {}`.

- [ ] **Step 5: Run the suite and the lint**

Run: `uv run python build/run_suites.py cc_guide`
Expected: all pass.
Run: `uv run python build/cc_guide/cli.py lint`
Expected: exit 0, with the one STALE line. From here to the merge the Loader window applies.

- [ ] **Step 6: Amend R2.3**

In the drift spec's R2.3 (about line 385), replace:

```
- the `llms.txt` slug list from the last baseline.
```

with:

```
- the `llms.txt` slug list from the last baseline;
- `format`, the layout's number: 3 since plan 89, after text block keys (1)
  and hashed keys (2). The loader refuses any other value, and code older
  than plan 89 refuses the file by its key set, so no checkout misreads a
  layout it predates (owner, plan 89, 2026-11-11);
- `cited`: per citing file, per section its citation names, the section's
  `text_hash` when `baseline cite` last stamped the file (R7), paths and
  section IDs sorted (owner, plan 89, 2026-11-11).
```

- [ ] **Step 7: Commit**

The loader, the file and the tests go in one commit, since the commit hook runs `cli.py lint` on the working tree (T5).

```bash
git add build/cc_guide/state.py build/cc_guide/baseline.py build/cc_guide/baseline.json build/cc_guide/test_state.py build/cc_guide/test_baseline.py specs/completed/claude-code-drift-automation-spec.md
git commit -m "feat(cc-guide): mark baseline.json's format and add an empty cited map

baseline.json gains format 3 and a cited map, which plan 89's next task
fills. The loader refuses any other format, and older code refuses the
file by its key set, so no checkout misreads a layout it predates.

<the session's trailer>"
```

### Task 4: Record each cited section's text hash (item 3)

**Files:**
- Modify: `build/cc_guide/baseline.py` (new `record_cites`; `accept`, lines 112-128)
- Modify: `build/cc_guide/cli.py` (the `cite` action, lines 311-324)
- Modify: `build/cc_guide/lint.py` (`stale_citations`, lines 160-170)
- Modify: `build/cc_guide/baseline.json` (migration)
- Test: `build/cc_guide/test_baseline.py` (new tests, and the partial state at line 98), `build/cc_guide/test_lint.py`, `build/cc_guide/test_cli.py`
- Modify: `build/CLAUDE.md:98-101`; `specs/completed/claude-code-drift-automation-spec.md` (R2.4, R5, R7)

**Interfaces:**
- Consumes: Task 3's `cited` map and key order.
- Produces:
  - `baseline.record_cites(state: dict, ids_by_path: dict[str, tuple[str, ...]], present: set[str]) -> dict`: a new state in which each path in `ids_by_path` maps to `{sid: state['sections'][sid]['text_hash']}` for its IDs, sorted. It drops every `cited` path not in `present`, and `cited` is sorted by path.
  - `baseline.accept`: same signature. An editorial accept also moves each `cited` record equal to the old `text_hash` to the new one (F6).
  - `lint.stale_citations`: same signature. A cited section is behind when the stamp is below its `changed`, or when `state['cited']` holds a hash for that file and section that differs from the section's `text_hash`. With no record, only the stamp rule applies (F5).

- [ ] **Step 1: Write the failing unit tests**

In `build/cc_guide/test_baseline.py`:

```python
def test_record_cites_keeps_each_cited_sections_hash_sorted_and_drops_absent_files(docs_dir):
    s = fixture_state(docs_dir)
    s['cited'] = {'gone.sh': {'alpha.overview': 'sha256:' + '0' * 64}}
    new = baseline.record_cites(s, {'z.sh': ('beta.overview', 'alpha.overview'), 'a.sh': ('alpha.overview',)},
                                {'a.sh', 'z.sh'})
    h = {sid: s['sections'][sid]['text_hash'] for sid in s['sections']}
    assert new['cited'] == {'a.sh': {'alpha.overview': h['alpha.overview']},
                            'z.sh': {'alpha.overview': h['alpha.overview'], 'beta.overview': h['beta.overview']}}
    assert list(new['cited']) == ['a.sh', 'z.sh'] and list(new['cited']['z.sh']) == ['alpha.overview', 'beta.overview']
    assert s['cited'] == {'gone.sh': {'alpha.overview': 'sha256:' + '0' * 64}}


def test_an_editorial_accept_carries_matching_records_and_a_substantive_one_does_not(docs_dir):
    s = fixture_state(docs_dir)
    old = s['sections']['alpha.overview']['text_hash']
    s['cited'] = {'a.sh': {'alpha.overview': old}, 'b.sh': {'alpha.overview': 'sha256:' + '0' * 64}}
    text = guide_text().replace('Alpha uses', 'Alpha now uses')
    editorial = baseline.accept(s, text, ['alpha.overview'], False, None)
    new = editorial['sections']['alpha.overview']['text_hash']
    assert new != old
    assert editorial['cited'] == {'a.sh': {'alpha.overview': new}, 'b.sh': {'alpha.overview': 'sha256:' + '0' * 64}}
    substantive = baseline.accept(s, text, ['alpha.overview'], True, '2.1.902', {})
    assert substantive['cited'] == s['cited']
```

In `build/cc_guide/test_lint.py`, beside `test_a_citation_of_a_section_the_baseline_lacks_is_never_stale`:

```python
def test_a_recorded_hash_that_differs_is_stale_even_at_an_equal_stamp(docs_dir):
    s = fixture_state(docs_dir)
    current = s['sections']['alpha.overview']['text_hash']
    cite = Citation('hooks/gate.sh', 2, ('alpha.overview',), s['sections']['alpha.overview']['changed'])
    s['cited'] = {'hooks/gate.sh': {'alpha.overview': 'sha256:' + '0' * 64}}
    assert stale_citations([cite], s) == [('hooks/gate.sh', ['alpha.overview'])]
    s['cited'] = {'hooks/gate.sh': {'alpha.overview': current}}
    assert stale_citations([cite], s) == []
    s['cited'] = {}
    assert stale_citations([cite], s) == []
```

Use the import names `test_lint.py` already has for `Citation` and `stale_citations`. `test_the_replay_flags_the_citers_of_drifted_sections_and_not_the_control` (`test_baseline.py:98`) hands `stale_citations` a partial state: give it `'cited': {}` beside `'sections'`. `stale_citations` reads `state['cited']`, which the loader guarantees.

- [ ] **Step 2: Write the failing CLI tests**

In `build/cc_guide/test_cli.py`, in `test_cite_stamps_each_file_at_its_sections_highest_changed_and_writes_only_those_files`, change the `dirty` assertion to `[state.BASELINE, 'hooks/gate.sh', 'rules/style.md']`, and add:

```python
    h = {sid: v['text_hash'] for sid, v in load(repo)['sections'].items()}
    assert load(repo)['cited'] == {'hooks/gate.sh': {'alpha.overview': h['alpha.overview'],
                                                     'alpha.reference': h['alpha.reference']},
                                   'rules/style.md': {'alpha.reference': h['alpha.reference']}}
```

Then add three tests. They use `world`, `main`, `cited`, `git`, `load` and `GUIDE_PATH`, which the file already has.

1. `test_an_editorial_accept_leaves_its_citers_fresh(world, capsys)`: cite `hooks/gate.sh` (citing `alpha.overview`), replace `Alpha uses` with `Alpha now uses` in the guide, run `baseline accept alpha.overview --editorial`, and assert `main(cache, 'lint') == 0` with `capsys.readouterr().err == ''`.

2. `test_two_branches_that_collide_on_a_stamp_leave_the_file_stale_in_either_merge_order(world, capsys, order)`, parametrized `order` in `['accept-first', 'cite-first']`. This rebuilds #93 and #94 on the fixture, whose newest release is 2.1.902:
   - On `main`: replace ``| `BETA_ENV` | on |`` with ``| `BETA_ENV` | off |`` in the guide (beta.overview's table), run `baseline accept beta.overview --substantive` (so `changed` becomes 2.1.902), then `baseline stamp`. Add `hooks/gate.sh` citing `alpha.overview beta.overview @2.1.900`, and commit everything.
   - Branch `cite`: `baseline cite hooks/gate.sh`, which stamps @2.1.902 and records both hashes. Commit.
   - Branch `accept` (from `main`): replace `Alpha uses` with `Alpha now uses`, run `baseline accept alpha.overview --substantive` (its only citer stamp is 2.1.900, so `changed` becomes 2.1.902), then `baseline stamp`. Commit.
   - Check out `main`, then merge the two branches in the given order. Assert that each `git merge --no-edit` returns and `git status --porcelain` is empty, so a conflict fails the test rather than hiding it.
   - Assert the collision holds: `hooks/gate.sh`'s stamp reads `@2.1.902`, and `load(repo)['sections']['alpha.overview']['changed'] == '2.1.902'`.
   - Assert `main(cache, 'lint') == 0`, and that `STALE hooks/gate.sh alpha.overview` is a line of stderr.

3. `test_two_branches_that_cite_different_files_merge_cleanly(world, capsys)`: on `main`, cite and commit `hooks/gate.sh`. Branch one adds and cites `hooks/a.sh`. Branch two adds and cites `rules/z.md` (frontmatter citation, as in the existing cite test). Merge both into `main`. Assert both merges leave `git status --porcelain` empty, `list(load(repo)['cited']) == ['hooks/a.sh', 'hooks/gate.sh', 'rules/z.md']`, and `main(cache, 'lint') == 0` with empty stderr.

- [ ] **Step 3: Run the tests to see the RED**

Run: `uv run python build/run_suites.py cc_guide -- test_baseline.py test_lint.py test_cli.py`
Expected FAIL: `record_cites` (no attribute), the editorial carry-forward, the lint hash rule, the edited cite test (`baseline.json` not dirty), the collision test in both orders (no `STALE` line), and the different-files test (an empty `cited`). Expected PASS at BASE: `test_an_editorial_accept_leaves_its_citers_fresh`. It pins F6: it must still pass after Step 4, and fails if the hash rule lands without the carry-forward.

- [ ] **Step 4: Implement**

- `baseline.record_cites` and the editorial carry-forward in `baseline.accept`, per Interfaces.
- `cli.py`'s `cite` action: after it stamps the files, write `dump_baseline(baseline.record_cites(state, ids_by_path, set(readable)))` to `baseline.json`, where `ids_by_path` maps each stamped path to its citation's IDs. Take the IDs from `guide.file_citation(path, text)[0].ids` on the text before stamping. All checks still run before any write.
- `lint.stale_citations`: add the hash half of the rule, per Interfaces, and update its docstring to `R5: each citing file with a cited section whose changed is above the file's stamp, or whose text_hash differs from the one baseline cite recorded for the file (R7), with those sections. A section baseline.json lacks is a lint violation, never stale.`

- [ ] **Step 5: Run the tests to see them pass**

Run: `uv run python build/run_suites.py cc_guide`
Expected: all pass, the existing `test_cite_refuses_with_one_error_line_and_writes_nothing` included (Review Focus 2).

- [ ] **Step 6: Migrate the committed file**

Record hashes for every citing file that `cli.py lint` does not list as STALE (T5). Run from the repo root:

```bash
uv run python build/cc_guide/cli.py lint
uv run --directory build/cc_guide python - <<'EOF'
from pathlib import Path
import baseline
import state
from guide import read_citations
from lint import stale_citations
repo = Path('../..').resolve()
tree = state.Source(repo)
manifest = state.parse_manifest(tree.require(state.MANIFEST))
current = state.parse_baseline(tree.require(state.BASELINE))
citations = read_citations(state.citing_files(tree, manifest.guide))[0]
stale = {path for path, _ in stale_citations(citations, current)}
new = baseline.record_cites(current, {c.path: c.ids for c in citations if c.path not in stale},
                            {c.path for c in citations})
(repo / state.BASELINE).write_text(state.dump_baseline(new), encoding='utf-8')
print(f'recorded {len(new["cited"])} files; unrecorded: {sorted(stale)}')
EOF
```

Expected: the unrecorded list equals the STALE files the first command printed (on 2026-11-11, `skills/writing-skills/SKILL.md` alone). With `cited` still empty, `stale_citations` applies the stamp rule only. Then `uv run python build/cc_guide/cli.py lint` prints the same STALE line and exits 0.

- [ ] **Step 7: Update the docs**

In `build/CLAUDE.md`, replace:

```
each one and prints `STALE` for a file reviewed before a cited section last
changed. After reviewing such a file, `cli.py baseline cite <file>` restamps
it. The `/cc-guide` skill in `../.claude/skills/` acts on what `check`
```

with:

```
each one and prints `STALE` for a file reviewed before a cited section last
changed, or reviewed against text whose hash differs from the section's now.
After reviewing such a file, `cli.py baseline cite <file>` restamps it and
records each cited section's `text_hash` in `baseline.json`. The `/cc-guide` skill in `../.claude/skills/` acts on what `check`
```

In the drift spec's R2.4 (about line 397), replace:

```
  and `text_hash`, which flags every citer. **Editorial:** a new `text_hash`
  only.
```

with:

```
  and `text_hash`, which flags every citer. **Editorial:** a new `text_hash`
  only. Each citer's `cited` hash that matched the old `text_hash` moves to
  the new one, so an editorial accept flags no citer (owner, plan 89,
  2026-11-11).
```

In R5 (about line 600), replace:

```
Stale citations, whose stamp is below a cited section's `changed`, print as
`STALE <file> <ids>` on stderr and do not change the exit code.
```

with:

```
Stale citations, whose stamp is below a cited section's `changed`, or whose
`cited` hash for a section differs from that section's `text_hash` (R2.3),
print as `STALE <file> <ids>` on stderr and do not change the exit code. The
hash half catches two branches that give a section's `changed` and a file's
stamp the same release; a citation with no `cited` hash has the stamp half
only (owner, plan 89, 2026-11-11).
```

In R7 (about line 763), replace:

```
- `cite <file>`: after a review, set the file's citation stamp to the highest
  `changed` among its cited sections.
```

with:

```
- `cite <file>`: after a review, set the file's citation stamp to the highest
  `changed` among its cited sections, and record each cited section's
  `text_hash` under the file in `cited`, dropping the entries of files the
  citation scan no longer finds (owner, plan 89, 2026-11-11).
```

- [ ] **Step 8: Verify and commit**

Run: `uv run python build/run_suites.py cc_guide` (all pass), `uv run python build/cc_guide/cli.py lint` (exit 0, the one STALE line) and `bash build/run_commit_lints.sh` (`commit lints passed`).

```bash
git add build/cc_guide/baseline.py build/cc_guide/cli.py build/cc_guide/lint.py build/cc_guide/baseline.json build/cc_guide/test_baseline.py build/cc_guide/test_lint.py build/cc_guide/test_cli.py build/CLAUDE.md specs/completed/claude-code-drift-automation-spec.md
git commit -m "feat(cc-guide): record each cited section's text hash at cite time

baseline cite records each cited section's text_hash in baseline.json,
and lint calls a file stale when that hash differs from the section's
now. Two branches that give a section's changed and a file's stamp the
same release no longer leave the file fresh. An editorial accept carries
matching hashes forward, so it still flags no citer. The committed file
records hashes for every citing file the lint did not list as stale
(owner ruling 2026-10-31).

<the session's trailer>"
```

### Task 5 (controller): Re-review `notice.sh` (F7, T4)

**Files:**
- Modify: only what `/cc-guide files` settles for the files below, and `build/cc_guide/baseline.json` through its `baseline cite`.

- [ ] **Step 1: List the files**

Run: `uv run python build/cc_guide/cli.py lint`
The paths are `build/cc_guide/notice.sh`, plus any file this plan edited that the output lists as STALE.

- [ ] **Step 2: Run the files mode**

Invoke `/cc-guide files <paths>` and follow the skill. The Loader window applies: its `check` runs with `--worktree`. A contradiction it lists is fixed in that file only. A not-covered row about SessionStart `additionalContext` (T7) goes to the owner, and the file is held until the owner rules on it.

- [ ] **Step 3: Verify and commit**

Run: `uv run python build/cc_guide/cli.py lint`, `uv run --with pyyaml python build/check_conformance.py` and `bash build/run_commit_lints.sh`. Commit as the skill directs. If the owner holds the file, record the open row for the completion gate.

### Task 6 (controller): The owner checks both surfaces (D3)

The owner runs the two sessions. The executor prepares the cache and restores it afterwards.

- [ ] **Step 1: Back up the cache and write a stand-in notice**

```bash
mkdir -p ~/.cache/agent-skills/scratch/plan89-work && cp -p ~/.cache/agent-skills/cc-guide/notice.json ~/.cache/agent-skills/cc-guide/notice.digest ~/.cache/agent-skills/cc-guide/notice-shown ~/.cache/agent-skills/scratch/plan89-work/ 2>/dev/null; ls ~/.cache/agent-skills/scratch/plan89-work/
uv run --directory build/cc_guide python -c "import notice, state; notice.write_notice(state.default_cache(), 'cc-guide · stand-in notice for the plan 89 check → /cc-guide')" && rm -f ~/.cache/agent-skills/cc-guide/notice-shown
```

The `ls` shows which files existed. A missing file is removed again at restore time.

- [ ] **Step 2: Desktop check (owner)**

The owner opens a new Code session in the Desktop app on the main checkout (`/Users/lowell/Projects/agent-skills`), not the execution worktree. Its `show` is the same script, and its `refresh` runs code that reads `main`'s file (Loader window). Pass: the first reply quotes the stand-in line. Record pass or fail.

- [ ] **Step 3: Terminal check (owner)**

Run `rm -f ~/.cache/agent-skills/cc-guide/notice-shown`, because the Desktop session's `show` recorded the day. The owner runs `claude` in a terminal in the main checkout. Pass: the terminal shows `SessionStart:startup says: cc-guide · stand-in notice …`, which proves the CLI line survives D2. Record what the first reply does too.

- [ ] **Step 4: Restore the cache**

Copy each backed-up file back to `~/.cache/agent-skills/cc-guide/`. Remove any of the three that had no backup.

- [ ] **Step 5: Act on the result**

- Both pass: item 2's `→ done` note at completion records the result, the date and `claude --version`.
- The Desktop reply does not quote the line: one wording round on `CONTEXT_NOTE` and `notice.sh`'s `NOTE` (Task 2's tests, then a `fix(cc-guide)` commit), then Steps 1 to 4 again. A second miss goes to the owner.
- The terminal shows no line: stop and ask the owner. D2's premise has failed.
