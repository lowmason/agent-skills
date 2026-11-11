# Compaction-Cut Probe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a live drift probe, `compaction-cut`, that records where Claude Code cuts a skill it re-attaches after compaction, and fails when a body that passes the `compaction-window` check would lose text.

**Architecture:** The probe follows the five probes in `build/cc_guide/`. `probes.py` writes two synthetic project skills of the same size into a scratch directory, one of prose and one of digits, so a cut by characters and a cut by tokens fall at different places. It runs three `claude -p` invocations on one session id: invoke both skills, `/compact`, and a one-line nudge. `collect` reads the persisted transcript after the compact boundary and measures each re-attached copy into `cut.json`. A pure assertion in `probe_checks.py` compares the prose skill's kept body with the register's window. Task 2 is a gated spike that settles what the transcript holds before the runner is written. Task 4 registers the probe, records one live run, and settles the register if the run diverges.

**Tech Stack:** Python 3.13 (dev Python in `build/versions.toml`), stdlib only (`tomllib` for the register), pytest; Claude Code `claude -p` with stream-json, `--session-id` and `--resume`.

**Spec:** none. This is `/deferred` step 5's **Plan** disposition (2026-11-10): the deferred item below is the requirements. Background: `specs/findings/superpowers-drift-v7-0-2.md` finding 17, `specs/completed/claude-code-drift-automation-spec.md` R10 and R12.6 (probes and fixtures), and `specs/plans/completed/69-agent-payload-probe.md` (the latest probe, whose shape this plan copies).

## Requirements

The deferred item, from `specs/deferred_items.md` section `superpowers-drift-v7.0.1 (no plan; drift review of upstream v7.0.1, branch claude/practical-hugle-86bb56) — 2026-10-28`, verbatim with its notes:

> Probe how Claude Code cuts a re-attached skill after compaction (superpowers drift finding
> 17, `specs/findings/superpowers-drift-v7-0-2.md`). The guide says each invoked skill keeps its first
> 5,000 tokens (`specs/guides/claude-code-customization-guide.md:128`). Upstream's #2481
> transcript shows a cut at exactly 20,000 characters, with a marker that points at the
> file. The `compaction-window` check in `build/cc_guide/conformance.toml` measures the
> body after the frontmatter, at 5,000 × 4 characters. Nobody has checked whether the cut
> counts frontmatter or a header Claude Code adds. [...] Size: plan. Done when: the probe runs and records where the cut
> falls, and the register's window (and the guide, through `/cc-guide`) matches what it
> shows.
> → progress 2026-10-28 (owner decision, "I approve your recommendations"): upstream's
> whole-file byte bar is not adopted. This probe decides the measure: if the cut counts
> the frontmatter, correct the register's window.

Two facts were measured on 2026-11-10 while this plan was written:

- In a Claude Code session, an invoked skill reaches the model as `Base directory for this skill: <skill dir>`, a blank line, then the body. The frontmatter is not in it. So the "header" in the item is that line, about 31 characters plus the skill's path.
- The three tightest bodies: finishing-a-development-branch has 26 characters of room under the 20,000-character window, subagent-driven-development 75, writing-plans 312. A header of about 90 characters that counts toward the cut would put the first two past it.

## Owner review (defaults this plan settles; change any at plan review)

- **O1. The probe's guide section and files.** Default: `sections = ['skills.progressive-disclosure']`, the section the `compaction-window` check cites, and no `files` list. A DIVERGES row sends the section to `/cc-guide verify`.
- **O2. What the probe asserts.** Default: PASS when the prose skill keeps at least the register's window of body characters, the window the check uses. The check is then safe: every body it passes survives compaction whole. The digits skill only tells a cut by characters from a cut by tokens, and the finding reports which. Real skill bodies are prose, so the digits skill never decides the verdict.
- **O3. The scratch path stands in for a real install path.** The probe's skills live under a temporary directory, so its header is longer than `/Users/<name>/.claude/skills/<skill>` for most skills. A PASS therefore covers any install path no longer than the probe's. The finding prints the header length so the margin is visible.
- **O4. How the register is corrected if the live run diverges (Task 4).** Default: a new `reserve_chars` parameter on the `compaction-window` check. The check's window becomes `tokens × chars_per_token − reserve_chars`. Its value is the smallest multiple of 50 that is at least the measured header's fixed part (the header less its path) plus 120 characters of path. If the run shows the frontmatter is re-attached, a second parameter, `counts_frontmatter = true`, also subtracts each file's own frontmatter length.
- **O5. Files the corrected window fails (Task 4).** Default: one `[[exception]]` of type `gap` per file, in the form of the retired `writing-skills-late-critical-headings` exception, and one backlog item per file at completion. Plan 88 frees room in finishing-a-development-branch and removes that file's exception. Alternative: split each failing file in this plan.
- **O6. The probe's running cost.** Registering the probe puts it in the weekly probe set (`probe_days = 7` in `manifest.toml`). Each weekly run is three invocations with a 32,000-character skill and a compaction, about $0.20–0.60. Default: register it, as the item asks ("a live probe beside the others"). Alternative: keep it out of the registry and run it by hand after a Claude Code release that mentions compaction.

## Global Constraints

- Python style: single quotes, f-strings, 4-space indentation, stdlib only in `probes.py` and `probe_checks.py`, the dev Python in `build/versions.toml` (3.13).
- Tests are directory-scoped. Run them through `uv run python build/run_suites.py <suite> [-- <pytest args>]` from the repo root, never through a repo-root pytest.
- Every commit passes `build/run_commit_lints.sh`.
- Do not edit `specs/deferred_items.md` before the Plan Completion Protocol. Re-read it just before the ticking pass, since another session may edit it.
- Leave these alone: `SCRUBBED_ENV`, `execute`, `claude_args`, `scrub_events`, `_trim_event`, `_trim_block`, `save_fixtures`, `run_probe`, the five existing probes with their tests and fixtures, `.claude/skills/cc-guide/SKILL.md` and the guide. The guide changes only through `/cc-guide` (Task 5).
- Never commit raw probe output or a raw transcript. Only files that `probes.save_fixtures` wrote go into `build/cc_guide/probe_streams/`, and `test_probe_replay.py` fails on a path or an id in them. The repo is public.
- Every live run (Task 2 and Task 4) waits for the owner to name the binary and approve the spend. One probe run is three invocations, each capped by `--max-budget-usd 0.50`; expect about $0.20–0.60 a run. A rerun needs the owner's word.
- The spike's scratch files live outside every repository, under `~/.cache/agent-skills/scratch/plan87-spike/`. Never under `/tmp` directly: a stray `/tmp/struct.py` breaks `import numpy` there.
- This plan does not execute while plan 85 executes: one execution at a time.
- Prose in commit messages and in the plan's notes follows `rules/write-with-asd-ste100.md`.
- Each commit message ends with the execution session's `Co-Authored-By` line. The commit blocks below write it as `<the session's trailer>`.
- Test deltas are +N per suite, never absolute totals. The `build` suite collects `build/cc_guide/`, so each `cc_guide` delta also applies to `build`.

## Review Focus

1. A transcript with two compact boundaries, or a re-attached copy from before the boundary: the probe must measure only copies after the last boundary, or a stale whole copy reads as "not cut".
2. A body found nowhere in the re-attached text (the model invoked one skill, not both): an ERROR that names the missing skill, never a PASS on the other.
3. A cut that falls inside the body's first line: `measure_cut` must still find the body's start, or report the copy as not found, not crash.
4. Path text in `cut.json`'s tail: the fixture must hold no path once `save_fixtures` redacts it.
5. A register with no `reserve_chars`: the window is `tokens × chars_per_token`, today's value, so nothing changes until Task 4 adds it.

Each line has its test: 3 in Task 1 (a `measure_cut` case), 2 in Task 1's assertion cases, 1 in Task 3 (the `reattached_after_boundary` case), 5 in Task 3's `register_window` test, 4 in Task 4's fixture check.

## Decisions

- **D1** (owner, /deferred selection, 2026-11-10): write this plan and plan 88. This plan executes first, after plan 85. Plan 88 frees about 1,000 characters in finishing-a-development-branch, enough to survive any correction this probe makes. Applied in: Global Constraints, O5.
- **D2** (owner, plan review, 2026-11-10): O1, default kept. The probe backs `skills.progressive-disclosure` and lists no `files`. Applied in: Task 4.
- **D3** (owner, plan review, 2026-11-10): O2, default kept. PASS means the prose skill keeps at least the register's window of body characters; the digits skill only tells characters from tokens. Applied in: Task 1.
- **D4** (owner, plan review, 2026-11-10): O3, default kept. The scratch path stands in for a real install path, and the finding prints the header length. Applied in: Task 1.
- **D5** (owner, plan review, 2026-11-10): O4, default kept. A DIVERGES run corrects the register with `reserve_chars` (and `counts_frontmatter` if the frontmatter is re-attached), at the value O4 states. Applied in: Task 4.
- **D6** (owner, plan review, 2026-11-10): O5, default kept. Each file the corrected window fails gets a `gap` exception and a backlog item; plan 88 removes finishing-a-development-branch's. Applied in: Task 4, Task 5.
- **D7** (owner, plan review, 2026-11-10): O6, default kept. The probe is registered and joins the weekly probe set, at about $0.20–0.60 a run. Applied in: Task 4.

## Related open items (taken into account, not absorbed)

- **Plan 58 review Minors batch** (section `58-claude-code-drift-automation — 2026-10-20`), item (l): `probes.py` grows by about 90 lines. Report the item's trigger at completion, and do not split the file.
- **Split and rewrite writing-skills against the guide** (section `53-agent-skills-portability — 2026-10-20`): unaffected. writing-skills' body is about 18,100 characters.

## File map

- Modify `build/cc_guide/probe_checks.py`: `CUT_KINDS`, `cut_frontmatter`, `cut_body`, `measure_cut`, `reattached_after_boundary`, `assess_compaction_cut` (Task 1; `reattached_after_boundary` is finished in Task 3).
- Modify `build/cc_guide/test_probe_checks.py`: their cases (Tasks 1 and 3).
- Modify `build/cc_guide/probes.py`: `register_window`, `prepare_cut`, `collect_cut`, `assess_cut`, `CUT_PROBE` (Task 3), then its `PROBE_RUNS` entry (Task 4).
- Modify `build/cc_guide/test_probes.py`: the runner's tests (Task 3).
- Modify `build/cc_guide/manifest.toml`: the `[[probe]]` entry (Task 4).
- Create `build/cc_guide/probe_streams/compaction-cut.compact.jsonl` and `build/cc_guide/probe_streams/compaction-cut.cut.json`, written only by `save_fixtures` (Task 4).
- Modify `build/cc_guide/test_probe_replay.py`: the replay cases (Task 4).
- Modify `build/cc_guide/PROBES.md`: the live run's row, appended by `cli.py probes` (Task 4).
- Only if the live run diverges (Task 4, Step 5): `build/check_conformance.py`, `build/test_check_conformance.py`, `build/cc_guide/conformance.toml`.
- This plan file: the `## Spike findings` section (Task 2).

---

### Task 1: The cut measurement and its assertion

**Files:**
- Modify: `build/cc_guide/probe_checks.py`
- Test: `build/cc_guide/test_probe_checks.py`

**Interfaces:**
- Produces:
  - `CUT_KINDS: dict[str, str]`: `{'prose': 'the cat sat on the mat while the dog ran past the gate ', 'digit': '0123456789'}`. The two names have the same length, so the two headers have the same length.
  - `CUT_LINE_CHARS = 64`, `CUT_BODY_LINES = 500` (a 32,000-character body), `CUT_SENTINEL = 'FRONTMATTER-SENTINEL'`, `CUT_TAIL_CHARS = 200`.
  - `cut_frontmatter(kind: str) -> str`: `---\nname: cut-probe-<kind>\ndescription: Use when the compaction-cut probe asks for cut-probe-<kind>. FRONTMATTER-SENTINEL\n---\n`.
  - `cut_body(kind: str) -> str`: `CUT_BODY_LINES` lines, each exactly `CUT_LINE_CHARS` characters with its newline: `@` plus the line's body offset as seven digits plus a space, then the kind's filler repeated and cut to fill the line.
  - `measure_cut(text: str, body: str) -> dict | None`: finds `body`'s first line in `text`. None when absent. Otherwise `{'header_chars': <chars of text before the body>, 'body_chars_kept': <length of the longest common prefix of text from there and body>, 'total_chars': <the sum>, 'cut': <kept < len(body)>, 'frontmatter_seen': <CUT_SENTINEL in text>, 'tail': <up to CUT_TAIL_CHARS characters of text after the kept body>}`.
  - `reattached_after_boundary(entries: list[dict], kinds) -> dict[str, str]`: a stub that returns `{}` until Task 3.
  - `assess_compaction_cut(compact: list[dict] | None, cut: dict[str, dict] | None, window: int) -> Verdict`.

- [ ] **Step 1: Write the failing tests**

In `test_probe_checks.py`, add:
- `test_cut_body_lines_carry_their_offsets`: for each kind, `len(cut_body(kind)) == 32000`, every line is 64 characters with its newline, and the line at index 300 (counting from 0) starts with `@0019200 `.
- `test_measure_cut_reads_header_kept_body_and_tail`: with `body = cut_body('prose')` and `text = 'Base directory for this skill: /x/cut-probe-prose\n\n' + body[:19950] + '\n[truncated: see /x/SKILL.md]'`, the result has `header_chars == 51`, `body_chars_kept == 19950`, `total_chars == 20001`, `cut is True`, `frontmatter_seen is False`, and `tail` starting with `'\n[truncated'`.
- `test_measure_cut_sees_frontmatter_and_whole_bodies`: text = `cut_frontmatter('digit') + cut_body('digit')` gives `frontmatter_seen is True`, `cut is False`.
- `test_measure_cut_returns_none_when_the_body_is_absent`: a text holding only `body[:30]` (part of the first line) returns None. (Review Focus 3.)
- `test_assess_compaction_cut` parametrized, with `ok = <a compact stream of an init, a {'type': 'system', 'subtype': 'compact_boundary'} event and a non-error result>` and `m(kept, cut=True)` building a measure with `header_chars=60`:
  - prose kept 20,000, digit kept 20,000, window 20,000 → PASS, finding `compaction kept 20000 body characters of the prose probe skill (by characters; 60 characters before the body), at least the register window 20000`.
  - prose kept 19,940, digit kept 19,940, window 20,000 → DIVERGES, finding `compaction keeps 19940 body characters of the prose probe skill (by characters; 60 characters before the body), fewer than the register window 20000, so a body that passes compaction-window can lose its last 60`.
  - prose kept 21,000, digit kept 14,000, window 20,000 → PASS whose finding says `by tokens`. Kept totals more than 5 characters apart mean tokens.
  - prose not cut (kept 32,000) → PASS, finding `compaction kept the whole 32000-character prose body; the register window 20000 is safe`.
  - prose `frontmatter_seen` → the finding's parenthesis ends `, frontmatter included`.
  - `cut` missing `'digit'` → ERROR `no re-attached copy of cut-probe-digit after the compact boundary`. (Review Focus 2.)
  - the compact stream without the boundary event → ERROR `the /compact run emitted no compact_boundary event`.
  - `compact=None` → ERROR `the /compact run broke: no stream-json events`.

- [ ] **Step 2: Run them to see them fail**

Run: `uv run python build/run_suites.py cc_guide -- test_probe_checks.py`
Expected: the new tests fail with `AttributeError` on the missing names. Every other test passes.

- [ ] **Step 3: Implement the names in `probe_checks.py`**

Check order in `assess_compaction_cut`: `broken(compact)`, then the boundary event, then each kind in `CUT_KINDS` order, then the prose verdict. The unit is `by characters` when the two `total_chars` are at most 5 apart, else `by tokens`.

- [ ] **Step 4: Run them to see them pass**

Run: `uv run python build/run_suites.py cc_guide -- test_probe_checks.py`
Expected: PASS, +12.

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/probe_checks.py build/cc_guide/test_probe_checks.py
git commit -m "$(cat <<'EOF'
feat(cc-guide): measure a compaction cut and assess it against the register

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 2: Spike: what a forced compaction leaves in the transcript (owner gate)

The controller runs this task itself, not a subagent: it needs the owner's answer and spends tokens. It commits only this plan file.

- [ ] **Step 1: Owner gate**

Run `uv run python build/cc_guide/cli.py binaries`. Ask the owner, as one question: which binary, and whether to spend up to three spike runs of about $0.20–0.60 each. Log the answer as the next `D<n>` in `## Decisions`.

- [ ] **Step 2: Run the three invocations by hand**

In a new folder under `~/.cache/agent-skills/scratch/plan87-spike/`, write `.claude/skills/cut-probe-<kind>/SKILL.md` for each kind as `cut_frontmatter(kind) + cut_body(kind)`, with the Task 1 functions. Pick one UUID. From that folder, run the binary three times with `claude_args`' flags (`--setting-sources project`, Sonnet at low effort, `--max-budget-usd 0.50`, persisted):
1. `--session-id <uuid>`, prompt: `Invoke the skill cut-probe-prose with the Skill tool, then the skill cut-probe-digit. Then reply DONE.`, Skill pre-allowed, 4 turns.
2. `--resume <uuid>`, prompt `/compact`, 1 turn.
3. `--resume <uuid>`, prompt `Reply OK.`, 1 turn.

- [ ] **Step 3: Read what happened**

From the stream of invocation 2 and the transcript `~/.claude/projects/*/<uuid>.jsonl`, record:
- S1: whether invocation 2's stream has a `compact_boundary` event, and how the transcript marks the boundary (entry type and fields);
- S2: which transcript entries after the boundary hold a copy of each probe skill's text, and in which invocation they were written. Give each entry's `type` and the JSON path to the string;
- S3: `measure_cut` on each copy: the header text (path replaced by `<path>`), and `header_chars`, `body_chars_kept`, `total_chars`, `frontmatter_seen`, and `tail` with paths replaced.

**Stop rules.** If S1 shows no boundary, or S2 finds no copy of either skill after the boundary, stop and report to the owner. Do not try another way to force compaction or to read the copy without the owner's word.

- [ ] **Step 4: Record the findings and commit**

Write S1–S3 into a new `## Spike findings` section of this plan, after `## Decisions`, with the Claude Code version. Write no path, session id or login name. Copy no raw transcript into the repo.

```bash
git add specs/plans/87-compaction-cut-probe.md
git commit -m "$(cat <<'EOF'
docs(specs): record the compaction-cut spike in plan 87

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 3: The compaction-cut runner, not yet registered

**Files:**
- Modify: `build/cc_guide/probe_checks.py` (`reattached_after_boundary`)
- Modify: `build/cc_guide/probes.py`
- Test: `build/cc_guide/test_probe_checks.py`, `build/cc_guide/test_probes.py`

**Interfaces:**
- Consumes: Task 1's names; the spike findings S1 and S2.
- Produces:
  - `reattached_after_boundary(entries, kinds) -> dict[str, str]`: for each kind, the text of the copy of `cut-probe-<kind>` in the entries after the last boundary entry (S1), read at the JSON path S2 names. A kind with no copy there is absent from the result.
  - `CUT_TURNS = 4`, `CUT_PROMPT` (the Step 2 prompt of Task 2), and `CONFORMANCE = Path(__file__).resolve().with_name('conformance.toml')` in `probes.py`.
  - `register_window() -> int`: from the `[[check]]` whose `id` is `compaction-window`, `tokens * chars_per_token - reserve_chars`, with `reserve_chars` 0 when absent.
  - `prepare_cut(scratch, claude, repo) -> list[Invocation]`: writes both skills and a `session-id` file holding a new UUID, and returns the three invocations of Task 2 as `invoke`, `compact` and `nudge`, each from `claude_args(..., sources='project', mode='default', persist=True, extra=...)`, with `allow=('Skill',)` on `invoke` only.
  - `collect_cut(scratch, run_dir) -> None`: reads the session's transcript under `Path.home() / '.claude' / 'projects'`, copies it to `transcript.raw.jsonl` for reading by hand, and writes `cut.json` as `{kind: measure_cut(text, cut_body(kind))}` for each kind that `reattached_after_boundary` found.
  - `assess_cut(read) -> Verdict`: `assess_compaction_cut(stream_of(read('compact.jsonl')), json.loads(read('cut.json') or '{}'), register_window())`.
  - `CUT_PROBE = Probe(prepare_cut, collect_cut, assess_cut, {'compact.jsonl': 'compaction-cut.compact.jsonl', 'cut.json': 'compaction-cut.cut.json'})`.

- [ ] **Step 1: Write the failing tests**

- `test_reattached_after_boundary_reads_only_the_last_boundary`, in `test_probe_checks.py`: a synthetic transcript in S1/S2's shape, with a whole prose copy before a first boundary, a second boundary, and a cut prose copy and a cut digit copy after it, returns the two cut copies. (Review Focus 1.)
- In `test_probes.py`, following plan 69's runner tests (`monkeypatch.setitem(probes.PROBE_RUNS, 'compaction-cut', probes.CUT_PROBE)` until Task 4):
  - `test_register_window_reads_the_compaction_window_check`: `register_window() == 20000` on today's register. On a copy with `reserve_chars = 150` added, at a monkeypatched `CONFORMANCE`, it is 19850. (Review Focus 5.)
  - `test_the_cut_probe_prepares_three_invocations_on_one_session`: the three argv lists name the same UUID, `--session-id` in the first and `--resume` in the other two; both SKILL.md files exist with the Task 1 text.
  - `test_the_cut_probe_reads_its_run_like_a_live_one`: with a fake `execute` that writes S1-shaped streams and a fake transcript in a monkeypatched home, `run_probe` returns the verdict that `assess_compaction_cut` gives for those measures.

- [ ] **Step 2: Run them to see them fail**

Run: `uv run python build/run_suites.py cc_guide -- test_probe_checks.py test_probes.py`
Expected: the new tests fail on the missing names. Every other test passes.

- [ ] **Step 3: Implement the names**

`collect_cut` finds the transcript by the UUID in `scratch / 'session-id'`. A transcript that is absent leaves `cut.json` as `{}`, which the assertion reports as ERROR.

- [ ] **Step 4: Run them to see them pass**

Run: `uv run python build/run_suites.py cc_guide -- test_probe_checks.py test_probes.py`
Expected: PASS, +4.

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/probe_checks.py build/cc_guide/test_probe_checks.py build/cc_guide/probes.py build/cc_guide/test_probes.py
git commit -m "$(cat <<'EOF'
feat(cc-guide): add the compaction-cut runner, not yet registered

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 4: Register the probe, record its first run, settle the register (owner gates)

The controller runs this task itself: it needs the owner's answers and spends tokens.

**Files:**
- Modify: `build/cc_guide/probes.py` (`PROBE_RUNS`), `build/cc_guide/manifest.toml`, `build/cc_guide/test_probes.py` (drop the `monkeypatch.setitem` lines), `build/cc_guide/test_probe_replay.py`, `build/cc_guide/PROBES.md`
- Create: the two fixtures, written only by `save_fixtures`
- Only on DIVERGES: `build/check_conformance.py`, `build/test_check_conformance.py`, `build/cc_guide/conformance.toml`; with `counts_frontmatter`, also `build/cc_guide/probes.py` (`register_window`) and `build/cc_guide/test_probes.py`

**Interfaces:**
- Consumes: `CUT_PROBE` (Task 3).
- Produces: the registered probe `compaction-cut`; on DIVERGES, the `reserve_chars` parameter.

- [ ] **Step 1: Owner gate**

As in Task 2, Step 1: the binary, one run's spend, and `--allow-old` if the binary is older than the newest cached changelog release. Log the answer as the next `D<n>`.

- [ ] **Step 2: Register the probe**

Add `'compaction-cut': CUT_PROBE,` as the last `PROBE_RUNS` entry, and append to `manifest.toml`:

```toml

[[probe]]
id = 'compaction-cut'
# Where Claude Code cuts a skill it re-attaches after compaction: the window the compaction-window check
# assumes (plan 87, drift finding 17).
sections = ['skills.progressive-disclosure']
```

Drop Task 3's `monkeypatch.setitem` lines.

Run: `uv run python build/run_suites.py cc_guide -- test_cli.py test_probes.py test_probe_replay.py`
Expected: exactly two failures, both in `test_probe_replay.py`: `test_every_registered_probe_has_its_fixtures` and `test_the_recorded_run_passes[compaction-cut]`. Any other failure is a stop.

- [ ] **Step 3: Run the live probe**

Run: `uv run python build/cc_guide/cli.py probes --claude '<path>' --only compaction-cut`
Expected: a `compaction-cut: PASS: …` or `compaction-cut: DIVERGES: …` line, the raw output folder, and one appended row. On PASS, go to Step 6. On DIVERGES, go to Step 4. On ERROR, stop: list the raw folder's files and report to the owner. Do not rerun without the owner's word.

- [ ] **Step 4: On DIVERGES, report and ask**

Show the owner the finding and `cut.json`'s numbers, and propose the O4 value of `reserve_chars` (and `counts_frontmatter` if `frontmatter_seen`). Run the check with that value in a scratch copy of the register and list the skill files it would fail. Ask, as one question: the value, and O5 (exceptions or splits) for those files. Log the answer as the next `D<n>`.

- [ ] **Step 5: On DIVERGES, correct the register**

Write `test_compaction_window_subtracts_reserve_chars` in `build/test_check_conformance.py`, after `test_compaction_window_flags_a_critical_heading_past_the_window`: with `WINDOW_PARAMS` plus `'reserve_chars': 5`, a body of 18 tokens' characters that passes today is flagged as `body is about 18 tokens; compaction re-attaches only the first 20`. If the owner took `counts_frontmatter`, add a second test in which a body that fits passes without its frontmatter and fails with it. Run `uv run python build/run_suites.py build -- test_check_conformance.py` and see them fail.

Make `check_compaction_window` subtract `params.get('reserve_chars', 0)` from the window, and each file's frontmatter length when `params.get('counts_frontmatter')` is true. Use the same window for the late-heading scan. If the owner took `counts_frontmatter`, the probe's window must follow the same rule, or the reassessment below fails on the probe's own frontmatter: first write `test_register_window_subtracts_the_probe_frontmatter_when_counted` in `test_probes.py` (on a register copy with `counts_frontmatter = true`, `register_window() == 20000 - reserve_chars - len(cut_frontmatter('prose'))`), see it fail, then make `register_window()` subtract `len(cut_frontmatter('prose'))` when the check has `counts_frontmatter = true`. Add the owner's values to the `compaction-window` check in `conformance.toml`, with a comment naming plan 87. Add the exceptions that the owner chose in Step 4. Run the test again (expected: PASS, +1 or +2), then `uv run --with pyyaml python build/check_conformance.py` (expected: exit 0).

Then reassess the recorded run against the corrected register:

Run: `uv run --directory build/cc_guide --python 3.13 python -c "import probes; from pathlib import Path; print(probes.CUT_PROBE.assess(probes.reader(Path('<raw output folder>'))))"`
Expected: a PASS verdict. If it is not PASS, stop and report.

- [ ] **Step 6: Save the fixtures and write the replay cases**

Run: `uv run --directory build/cc_guide --python 3.13 python -c "import probes; from pathlib import Path; print(probes.save_fixtures(Path('<raw output folder>'), 'compaction-cut', Path('probe_streams')))"`
Expected: two paths. Run `grep -c '<private>' build/cc_guide/probe_streams/compaction-cut.cut.json` and read the file: numbers and redacted tails only. (Review Focus 4.)

Append to the parametrize list of `test_a_changed_behaviour_diverges_and_a_broken_run_is_an_error`:
- the recorded `cut.json` with the prose `body_chars_kept` set to `register_window() - 1` → DIVERGES, its finding ending `can lose its last 1`;
- `cut.json` without `'digit'` → ERROR `no re-attached copy of cut-probe-digit after the compact boundary`;
- the compact stream without its boundary event → ERROR `the /compact run emitted no compact_boundary event`.

Check that each case can fail: change one expected finding, see it fail, revert.

Run: `uv run python build/run_suites.py cc_guide -- test_probe_replay.py`
Expected: PASS, +4 (the recorded run and three cases).

- [ ] **Step 7: Run the suites and commit**

Run: `uv run python build/run_suites.py cc_guide build`
Expected: PASS. Read the row: `tail -n 1 build/cc_guide/PROBES.md`. Its outcome is the live run's, DIVERGES included. Run `uv run python build/cc_guide/cli.py lint` and `build/run_commit_lints.sh` (both exit 0).

```bash
git add build/cc_guide/probes.py build/cc_guide/manifest.toml build/cc_guide/test_probes.py \
        build/cc_guide/test_probe_replay.py build/cc_guide/probe_streams/compaction-cut.compact.jsonl \
        build/cc_guide/probe_streams/compaction-cut.cut.json build/cc_guide/PROBES.md
# on DIVERGES, also: build/check_conformance.py build/test_check_conformance.py build/cc_guide/conformance.toml
# (probes.py and test_probes.py are already listed; they carry the counts_frontmatter change if any)
git commit -m "$(cat <<'EOF'
feat(cc-guide): register the compaction-cut probe with its first run

Co-Authored-By: <the session's trailer>
EOF
)"
```

The commit message body says where the cut fell, and, on DIVERGES, the register's new window and each exception.

---

### Task 5: Whole-plan checks

- [ ] **Step 1: Run the suites and the lints**

Run: `uv run python build/run_suites.py cc_guide build`, `build/run_commit_lints.sh`, `uv run python build/cc_guide/cli.py lint`, `uv run --with pyyaml python build/check_conformance.py` and `uv run python build/run_suites.py --check`.
Expected: all pass. Against the plan's base: `cc_guide` +20 (12 + 4 + 4), or +21 with `counts_frontmatter`; `build` the same plus Task 4's one or two.

- [ ] **Step 2: Check the scope fence**

Run: `git diff --stat "$(git merge-base main HEAD)"..HEAD`
Expected: only the File map's files and this plan. No guide, no `specs/deferred_items.md` (until the completion protocol), no skill file.

- [ ] **Step 3: Completion**

Run the Plan Completion Protocol (writing-plans). Name these in the completion report:
- where the cut fell, by characters or tokens, and whether the header or the frontmatter counts;
- whether the guide's sentence ("keeps the first 5,000 tokens of each") still matches. If it does not, the owner runs `/cc-guide verify skills.progressive-disclosure`. The deferred item's Done when needs the guide to match, so tick it only once the guide matches or that verify has run. Otherwise write a `→ progress` note naming the step left;
- each exception that Task 4 added, each with a backlog item (O5);
- plan 58 Minor (l)'s trigger (`probes.py` grew).
