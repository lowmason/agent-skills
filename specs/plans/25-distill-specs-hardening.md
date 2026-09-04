# distill_specs.py Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the nine remaining deferred hardening items against `skills/llm-wiki/scripts/distill_specs.py` — hand-edited-brief robustness, same-date accretion correctness, unguarded I/O, and rename-following for previously-seen hints.

**Architecture:** Nine independent, test-first tasks against one script and its test file. No new modules and no new dependencies. Two internal signatures change (`_extend_brief` gains a `notes` parameter; `_render_new_sections` gains a raising contract), both consumed only inside this module. Every task is one defect, one RED test, one minimal fix, one commit.

**Tech Stack:** Python 3.13, stdlib only (`argparse`, `re`, `subprocess`, `pathlib`, `hashlib`, `fnmatch`), pytest via `uv run`. The script imports `redact` and `slugify` from its sibling `distill_sessions.py`; that is the only cross-module dependency and it stays that way.

## Global Constraints

Copied from the source items and the repo's standing conventions. Every task's requirements implicitly include this section.

- **Stdlib only.** `distill_specs.py`'s module docstring opens with "Stdlib only." No import may be added beyond the stdlib and the existing `from distill_sessions import redact, slugify`.
- **Style:** 2-space indent, single quotes, matching the surrounding file. Tests use bare imports (`import distill_specs as dsp`), 2-space indent, and stdlib+pytest only — git fixture repos are built in `tmp_path` via the existing `make_repo` / `make_root` helpers.
- **Test command (directory-scoped — a repo-root pytest run fails outright, and `test_build.py` basenames collide across sibling skills):**
  ```bash
  cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
  ```
  **Record the count `pytest -q` reports before Task 1 and treat it as the baseline** — do not hard-code 231. This plan's baseline assumes the /deferred quick-fix commits from 2026-09-04 are present (they add 2 tests to `test_lint_wiki.py`; the two `test_distill_sessions.py` fixes strengthened existing assertions and added no tests); on a checkout without them the absolute numbers shift. Every task states how many tests it *adds*; the count must only ever grow by exactly that many.
- **House error style:** a hard failure prints `error: <what> (<why>)` to stderr and returns 1 from the `cmd_*` function; a non-fatal condition prints `warning: …` to stderr and continues; a brief-content defect prints `brief-error: <what>` to stderr and returns 1. Follow the style already in `cmd_inventory` / `cmd_assemble`; do not invent a new one.
- **Write-nothing contract (framework spec §7):** `assemble` validates everything before writing anything, and `inventory` writes the brief atomically via `_atomic_write` as an all-or-nothing artifact. No task may move a write earlier than its validation gate, or leave a partial brief on disk after an error.
- **Scope fence — one script.** The Task 8 source item offers "…or settle the convention repo-wide." This plan deliberately takes the narrower reading and guards `distill_specs.py` only. Do **not** touch `distill_sessions.py` or `lint_wiki.py`: their identical unguarded convention is out of scope and stays deferred. If you believe the repo-wide settle is required, stop and ask rather than widening.
- **Determinism:** the script is "deterministic given its inputs; the only clock read is the `--date` default." No task may add a clock read, a network call, or an environment read.
- **Commits:** one per task, conventional-commit subject, ending with the trailer:
  ```
  Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
  ```

## File Structure

Only two files change. Both already exist; neither is split.

| File | Responsibility | Change |
|---|---|---|
| `skills/llm-wiki/scripts/distill_specs.py` | The whole distiller: walk, seed-grep, SHA tables, brief render/accrete, brief parse/validate, digest render, CLI | Modified in 8 of 9 tasks |
| `skills/llm-wiki/scripts/test_distill_specs.py` | Its tests (stdlib + pytest, hermetic git fixture repos) | Modified in all 9 tasks |

Functions touched, in plan order: `validate_entries` (T1), `_repo_name` (T2), — (T3, test-only), `render_digest` + `render_source_body` + `cmd_assemble` (T4), `cmd_assemble` (T5), `_extend_brief` (T6, T7), `_render_new_sections` + `cmd_inventory` + `_extend_brief` (T8), `_render_new_sections` + new `renamed_from` (T9).

---

### Task 1: Ticked `q` entries must not bypass the square-bracket claim check

Source item: plan 16 — "Ticked q-entries bypass the square-bracket claim check (the q branch `continue`s before the check in `validate_entries`); hoist the check + red test."

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py:315-368` (`validate_entries`)
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: nothing later tasks rely on. `validate_entries(entries, errors) -> None` (mutates `errors`) is unchanged.

**Why this is a real defect:** `q` claims are rendered into the digest by `render_digest_entry` exactly like capture claims. `lint_wiki.py`'s `BODY_CITE_RE` reads `[word …]` in a digest body as a citation locator, so a bracketed `q` claim fabricates a citation the wiki cannot resolve. The `also`-sha gate directly above the `q` branch already carries this exact reasoning in its comment — the bracket check was simply left below the `continue`.

- [ ] **Step 1: Write the failing test**

Append after `test_also_without_sha_stays_valid` (ends near line 682):

```python
def test_ticked_q_entry_claim_brackets_are_reported():
  '''The square-bracket claim check applies to every ticked entry: q claims
  are rendered into the digest by render_digest_entry too, so brackets there
  fabricate a lint_wiki BODY_CITE_RE citation exactly like a capture claim
  would. The q branch continue'd before the check.'''
  text = ('- [x] [q-01] Open thing\n'
          '  at: specs/x.md L1\n'
          '  claim: Whether [the thing] matters is unresolved.\n')
  _, entries, errors = dsp.parse_brief(text)
  dsp.validate_entries(entries, errors)
  assert any('square brackets in claim' in err for err in errors)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py::test_ticked_q_entry_claim_brackets_are_reported -v
```

Expected: FAIL — `assert any(...)` is False because `errors` is empty (the `q` branch returned before the check). If it fails any other way, fix the test before continuing.

- [ ] **Step 3: Hoist the check above the `q` branch**

In `validate_entries`, immediately after the `for loc, sha in e['also']:` loop and **before** `if e['prefix'] == 'q':`, insert:

```python
    # Hoisted above the q branch for the same reason the also-sha gate is:
    # q claims are rendered into the digest by render_digest_entry too, so a
    # bracketed q claim fabricates a BODY_CITE_RE citation just like a
    # bracketed capture claim.
    if re.search(r'[\[\]]', f.get('claim', '')):
      errors.append(f'{e["id"]}: square brackets in claim '
                    '(BODY_CITE_RE discipline)')
```

Then delete the now-duplicated check at the end of the function — these three lines:

```python
    if re.search(r'[\[\]]', f.get('claim', '')):
      errors.append(f'{e["id"]}: square brackets in claim '
                    '(BODY_CITE_RE discipline)')
```

- [ ] **Step 4: Run the test and the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: PASS, baseline +1, no warnings. The existing capture-claim bracket test must still pass — it proves the hoist did not lose the original behavior.

- [ ] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "$(cat <<'MSG'
fix(llm-wiki): apply the claim bracket check to ticked q entries

The q branch continued before the check, so a bracketed q claim shipped
into the digest and fabricated a BODY_CITE_RE citation.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 2: `_repo_name` must not emit a YAML-hostile `repo:` value

Source item: plan 16 — "`_repo_name` YAML-hostile residue: a zero-ASCII-word directory name containing `': '` still lands unquoted in the brief header."

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py:55-72` (`_repo_name`)
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: nothing. `_repo_name(repo: Path) -> str` is unchanged.

**Why this is a real defect:** `render_brief_header` embeds the result unquoted as `repo: {repo_name}` in the brief's YAML frontmatter. `_repo_name` already strips a leading `#` or `-` for exactly this reason. A `': '` anywhere in the name re-parses as a nested key and cannot be fixed by stripping, so it takes the same fallback the empty-after-sanitizing case takes.

- [ ] **Step 1: Write the failing test**

Append next to the other `_repo_name` tests (search for `_repo_name` in the test file and place it after the last one):

```python
def test_repo_name_falls_back_when_the_raw_name_carries_a_yaml_key_sep(
    tmp_path):
  '''repo_name is embedded unquoted as `repo: {repo_name}` in the brief's
  YAML frontmatter. A zero-ASCII-word directory name (slugify collapses to
  the 'session' sentinel) containing ': ' would land there raw and re-parse
  as a nested key — the same unquoted-scalar hazard the leading '#'/'-'
  strip already guards, but not fixable by stripping.'''
  repo = tmp_path / 'δ: δ'
  repo.mkdir()
  assert dsp._repo_name(repo) == 'session'
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py::test_repo_name_falls_back_when_the_raw_name_carries_a_yaml_key_sep -v
```

Expected: FAIL with `AssertionError: assert 'δ: δ' == 'session'` — the raw-name branch returns the hostile name as-is.

- [ ] **Step 3: Extend the fallback**

Replace the last two lines of `_repo_name`:

```python
  name = repo.name.lstrip('#-').strip()
  return name or 'session'
```

with:

```python
  name = repo.name.lstrip('#-').strip()
  # ': ' re-parses as a nested key in `repo: {repo_name}` — the same
  # unquoted-scalar hazard as the lead characters stripped above, but it can
  # sit anywhere in the name, so the only safe move is the sentinel.
  if not name or ': ' in name:
    return 'session'
  return name
```

Also extend the docstring's last sentence from "A name that sanitizes to nothing falls back to 'session'." to "A name that sanitizes to nothing — or that still carries a YAML key separator — falls back to 'session'."

- [ ] **Step 4: Run the test and the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: PASS, +1 over Task 1.

- [ ] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "$(cat <<'MSG'
fix(llm-wiki): reject a YAML key separator in the derived repo name

repo_name lands unquoted in the brief frontmatter; ': ' re-parsed it as a
nested key. Same fallback the leading-'#'/'-' guard already takes.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 3: Hermetic cover for `(also …)` render asymmetry

Source item: plan 16 — "Hermetic `(also …)` render test: digest-renders-it / source-body-omits-it is currently pinned only by @needs_pilot tests that skip on machines without /Users/lowell/research-wiki."

**Files:**
- Test only: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: existing helpers `make_repo`, `make_root`, `_sha`, `_write_brief`, `assemble`, `_digests`.
- Produces: nothing.

**This task is a characterization test, not a red-green cycle.** The behavior is already correct; what is missing is a cover that runs everywhere. So the failure you must witness is a *mutation* failure, not an initial failure. Do not "make it fail" by breaking the test.

- [ ] **Step 1: Write the test**

Append after `test_also_sha_placeholder_end_to_end_reports_and_writes_nothing` (ends near line 934):

```python
def test_also_location_is_digest_only(tmp_path, capsys):
  '''Framework spec §5.3: (also …) locations ride in the digest and are
  dropped from the wiki/sources capture-note body. Until now that asymmetry
  was pinned only by the @needs_pilot round-trip tests, which skip on every
  machine without the pilot reference wiki — i.e. in CI and on a fresh
  clone. Not redundant with
  test_planted_secret_in_title_at_and_also_never_reaches_sinks: that one
  carries an (also …) line but asserts only that its secret is REDACTED,
  never that the location rides in the digest and is dropped from stdout.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  sha = _sha(repo)
  entry = (f'- [x] [d-01] Use X over Y\n'
           f'  kind: decision · boundary: transferable\n'
           f'  at: specs/completed/a-spec.md §1 · sha: {sha}\n'
           f'  (also specs/plans/completed/1-a-spec.md L4)\n'
           f'  excerpt: "**Decision:** use X over Y."\n'
           f'  claim: X was chosen over Y.\n')
  brief = _write_brief(root, repo, entry)
  assert assemble(brief, root) == 0
  digest = _digests(root)[0].read_text()
  out = capsys.readouterr().out
  assert '  (also specs/plans/completed/1-a-spec.md L4)' in digest
  # assert the body was produced at all, so an unrelated change that empties
  # stdout cannot satisfy the omission assertion below by accident
  assert '### [d-01]' in out
  assert 'specs/plans/completed/1-a-spec.md' not in out
```

- [ ] **Step 2: Run it and confirm it passes**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py::test_also_location_is_digest_only -v
```

Expected: PASS. It characterizes behavior that already holds.

- [ ] **Step 3: Mutation-verify the digest half**

In `render_digest_entry`, comment out the loop that renders also-lines:

```python
    # for loc, sha in e['also']:
    #   loc = redact(loc)[0]
    #   lines.append(f'  (also {loc}{SEP}sha: {sha})' if sha
    #                else f'  (also {loc})')
```

Re-run the test. Expected: FAIL on the digest assertion. Then **restore the loop** with `git checkout -- skills/llm-wiki/scripts/distill_specs.py` and re-run to confirm PASS.

- [ ] **Step 4: Mutation-verify the source-body half**

In `render_source_body`, append the also-locations to each block by replacing:

```python
    blocks.append(f'### [{e["id"]}] {title}\n'
                  f'kind: {f["kind"]}{SEP}at: {repo_name} {pos}{SEP}'
                  f'basis: git:{f["sha"]}\n'
                  + redact(f['claim'])[0])
```

with the same call plus a leaked also-line:

```python
    blocks.append(f'### [{e["id"]}] {title}\n'
                  f'kind: {f["kind"]}{SEP}at: {repo_name} {pos}{SEP}'
                  f'basis: git:{f["sha"]}\n'
                  + ''.join(f'(also {loc})\n' for loc, _ in e['also'])
                  + redact(f['claim'])[0])
```

Re-run the test. Expected: FAIL on the stdout assertion. Then **restore** with `git checkout -- skills/llm-wiki/scripts/distill_specs.py` and re-run to confirm PASS.

- [ ] **Step 5: Run the full suite and commit**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
git status --porcelain skills/llm-wiki/scripts/distill_specs.py   # MUST be empty
```

Expected: +1 over Task 2, and `distill_specs.py` unmodified (this is a test-only task — if git reports it dirty, a mutation was not restored).

```bash
git add skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "$(cat <<'MSG'
test(llm-wiki): cover the (also ...) digest-only rule hermetically

The asymmetry was pinned only by @needs_pilot tests that skip without the
pilot reference wiki. Mutation-verified on both halves.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 4: An all-`q` brief must not advertise a capture page that will not exist

Source item: plan 16 — "All-q ticked brief edge: stdout body is a bare newline while the digest preamble still points readers at a capture page that would have no captures."

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py:442-482` (`render_digest`), `:484-506` (`render_source_body`), `:557-593` (`cmd_assemble`)
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `render_source_body(entries, repo_name) -> str` now returns `''` (not `'\n'`) when no ticked non-`q` entries exist. Task 5's tests assert on `cmd_assemble` stderr and must tolerate the extra `note:` line added here.

**Why this is a real defect:** a harvest yielding only open questions is legitimate grammar (pilot `q-02`). But `render_digest`'s preamble unconditionally says "Ground-truth entries for the capture notes in `wiki/sources/{stem}.md`", and `render_source_body` returns a bare `'\n'` — so the agent is told to create a capture page and handed a blank body for it.

- [ ] **Step 1: Write the failing test**

Append after `test_no_ticked_entries_is_error`:

```python
def test_all_q_brief_advertises_no_capture_page(tmp_path, capsys):
  '''A harvest whose only ticked entries are open questions is legitimate
  (pilot q-02), but the digest preamble pointed at a wiki/sources page that
  would hold no captures, and the stdout body was a bare newline the agent
  would paste as that empty page.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  entry = ('- [x] [q-01] Open thing\n'
           '  at: specs/deferred_items.md L3\n'
           '  claim: Whether the later thing matters is unresolved.\n')
  brief = _write_brief(root, repo, entry)
  assert assemble(brief, root) == 0
  digest = _digests(root)[0].read_text()
  assert 'wiki/sources/' not in digest
  assert 'Open questions only' in digest
  cap = capsys.readouterr()
  assert cap.out == ''
  assert 'no ticked captures' in cap.err
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py::test_all_q_brief_advertises_no_capture_page -v
```

Expected: FAIL on `assert 'wiki/sources/' not in digest` — the preamble names the page unconditionally.

- [ ] **Step 3: Make the preamble conditional**

In `render_digest`, delete these four entries from the end of the `fm` list literal (they sit after `'---', ''`):

```python
    f'Ground-truth entries for the capture notes in wiki/sources/{stem}.md.',
    f'Each entry: verbatim excerpt from the {header["repo"]} file at the',
    'stated location, introducing commit sha.',
    '',
```

so `fm` now ends with `'---',` then `'',` then `]`. Immediately after the `fm = [...]` literal, insert:

```python
  if caps:
    fm += [
      f'Ground-truth entries for the capture notes in wiki/sources/{stem}.md.',
      f'Each entry: verbatim excerpt from the {header["repo"]} file at the',
      'stated location, introducing commit sha.',
      '',
    ]
  else:
    # No ticked captures: assemble creates no wiki/sources page for this
    # harvest, so the preamble must not send a reader to one.
    fm += [
      'Open questions only — this harvest produced no capture notes, and no',
      'wiki/sources page is created for it. Each entry: a question raised by',
      f'the {header["repo"]} specs at the stated location.',
      '',
    ]
```

- [ ] **Step 4: Make the empty source body empty**

In `render_source_body`, replace the final line:

```python
  return '\n\n'.join(blocks) + '\n'
```

with:

```python
  # No blocks means no capture page: return nothing rather than a bare
  # newline the caller would print as an empty page body.
  return '\n\n'.join(blocks) + '\n' if blocks else ''
```

- [ ] **Step 5: Say so on stderr**

In `cmd_assemble`, between the source-body print and the `wrote` line, insert the note. The region becomes:

```python
  print(render_source_body(entries, header['repo']), end='')
  if not any(e['ticked'] and e['prefix'] != 'q' for e in entries):
    print('note: no ticked captures — open questions only; the digest is the '
          'whole yield and there is no wiki/sources page to create',
          file=sys.stderr)
  print(f'wrote {out.relative_to(root)}', file=sys.stderr)
```

- [ ] **Step 6: Run the test and the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: PASS, +1 over Task 3. `test_assemble_golden_digest` must still pass — it has captures, so it takes the `if caps:` branch and its expected text is unchanged.

- [ ] **Step 7: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "$(cat <<'MSG'
fix(llm-wiki): stop advertising a capture page for an all-q harvest

The digest preamble named a wiki/sources page that assemble creates no
body for, and the stdout body was a bare newline.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 5: `cmd_assemble` must report a malformed header, not raise

Source items: plan 16 — "Required digest header keys are read with hard `[]` in `cmd_assemble` — a hand-edited brief missing e.g. `date:` raises KeyError instead of a `brief-error:` line" **and** "Brief missing `repo_path:` → `Path('')` → the drift check runs `git -C .` and warns about a foreign HEAD; should report 'cannot check drift' instead."

Both are the same failure mode — `cmd_assemble` trusting a hand-edited header — so they share one reviewer gate.

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py:557-593` (`cmd_assemble`), plus one module constant near `WALK_DIRS`
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: Task 4's `cmd_assemble` edits (the `note:` stderr line). Do not revert them.
- Produces: module constant `REQUIRED_HEADER_KEYS: tuple[str, ...] = ('repo', 'repo_head', 'date')`.

**Why these are real defects:** `render_digest` reads `header["date"]`, `header["repo"]` and `header["repo_head"]` with a hard `[]`. The write-nothing contract still holds when one is missing (the KeyError is raised before `_atomic_write`), but the operator gets a traceback where the CLI promises a `brief-error:` line. Separately, `Path('')` is `Path('.')`, so the drift check runs `git -C .` and reports the *current working directory's* HEAD as a mismatch — a foreign-HEAD warning about a repo the brief never named.

- [ ] **Step 1: Write the two failing tests**

Append after the test added in Task 4:

```python
def test_brief_missing_a_required_header_key_is_a_brief_error(
    tmp_path, capsys):
  '''render_digest reads header['date'] with a hard []; a hand-edited brief
  missing it raised KeyError. The write-nothing contract held, but the
  operator got a traceback where the CLI promises a brief-error line.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  brief.write_text(brief.read_text().replace('date: 2026-07-24\n', ''))
  assert assemble(brief, root) == 1
  assert 'brief-error: brief: missing header key date' in \
    capsys.readouterr().err
  assert _digests(root) == []


def test_brief_missing_repo_path_reports_cannot_check_drift(
    tmp_path, capsys):
  '''Path('') is Path('.'), so the drift check ran `git -C .` and reported
  the CURRENT directory's HEAD as a mismatch — a foreign-HEAD warning about
  a repo the brief never named.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  brief.write_text(brief.read_text().replace(f'repo_path: {repo}\n', ''))
  assert assemble(brief, root) == 0
  err = capsys.readouterr().err
  assert 'warning: cannot check drift (no repo_path in brief)' in err
  assert 'post-inventory edits' not in err   # the foreign-HEAD warning
```

- [ ] **Step 2: Run them to verify they fail**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py -k "required_header_key or cannot_check_drift" -v
```

Expected: the first ERRORs with `KeyError: 'date'` raised from `render_digest`; the second FAILs because stderr carries the foreign-HEAD `post-inventory edits` warning instead. Both failures are the defects themselves.

- [ ] **Step 3: Add the required-key constant**

Immediately after the `DEFERRED_FILE = 'specs/deferred_items.md'` line, add:

```python
# render_digest and the drift check read these with a hard []; a hand-edited
# brief missing one must fail the gate with a brief-error line, not a
# KeyError traceback.
REQUIRED_HEADER_KEYS = ('repo', 'repo_head', 'date')
```

- [ ] **Step 4: Check them at the gate**

In `cmd_assemble`, immediately after `validate_entries(entries, errors)` and before the `if not any(e['ticked'] ...)` line, insert:

```python
  for key in REQUIRED_HEADER_KEYS:
    if not header.get(key):
      errors.append(f'brief: missing header key {key}')
```

- [ ] **Step 5: Guard the drift check**

Replace this block:

```python
  repo_path = Path(header.get('repo_path', ''))
  try:
    head = _git(repo_path, 'rev-parse', '--short', 'HEAD').strip()
    if head != header.get('repo_head'):
      print(f'warning: {header["repo"]} HEAD {head} != brief repo_head '
            f'{header["repo_head"]} — post-inventory edits are the wiki\'s '
            'dated-claims staleness, not re-harvested here', file=sys.stderr)
  except (RuntimeError, OSError):
    print(f'warning: cannot check drift ({repo_path} unavailable)',
          file=sys.stderr)
```

with:

```python
  repo_path = header.get('repo_path', '')
  if not repo_path:
    # Path('') is Path('.'): the check would run `git -C .` and report the
    # cwd's HEAD as a mismatch for a repo the brief never named.
    print('warning: cannot check drift (no repo_path in brief)',
          file=sys.stderr)
  else:
    try:
      head = _git(Path(repo_path), 'rev-parse', '--short', 'HEAD').strip()
      if head != header.get('repo_head'):
        print(f'warning: {header["repo"]} HEAD {head} != brief repo_head '
              f'{header["repo_head"]} — post-inventory edits are the wiki\'s '
              'dated-claims staleness, not re-harvested here',
              file=sys.stderr)
    except (RuntimeError, OSError):
      print(f'warning: cannot check drift ({repo_path} unavailable)',
            file=sys.stderr)
```

- [ ] **Step 6: Run the tests and the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: PASS, +2 over Task 4.

- [ ] **Step 7: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "$(cat <<'MSG'
fix(llm-wiki): gate a hand-edited brief header instead of trusting it

Missing required keys now fail as brief-error lines rather than KeyError,
and a missing repo_path reports "cannot check drift" instead of warning
about the cwd's foreign HEAD.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 6: The `files_walked:` splice must rewrite the whole continuation block

Source item: plan 16 — "`files_walked:` header splice in `_extend_brief` assumes exactly one continuation line; a wrapping walk list would corrupt the header."

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py:384-412` (`_extend_brief`)
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: nothing. Task 7 restructures the same function and must keep this splice loop intact.

**Why this is a real defect:** `parse_brief` folds *every* two-space continuation line into one header value, so a wrapped `files_walked:` block is valid input. The splice replaces exactly `lines[i + 1]`, leaving the remaining continuation lines behind — on re-parse the brief lists those files twice, and `walked += [f for f in new if f not in walked]` then dedups against a list that already contains duplicates.

- [ ] **Step 1: Write the failing test**

Append near the other extend tests (search for `no new files` to find them):

```python
def test_extend_rewrites_a_wrapped_files_walked_block(tmp_path, capsys):
  '''parse_brief folds any number of two-space continuation lines into
  files_walked, so a wrapped walk list is valid input — but the splice
  replaced exactly lines[i + 1], leaving the stale tail behind and listing
  files twice on re-parse.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='specs/completed/*.md') == 0
  brief = root / 'reports/harvest-repo-2026-07-24.md'
  # hand-wrap the walk list across two continuation lines, as a human editor
  # or a future wrapping writer would
  brief.write_text(brief.read_text().replace(
    '  specs/completed/a-spec.md\n',
    '  specs/completed/a-spec.md;\n  specs/deferred_items.md\n'))
  assert inventory(repo, root) == 0
  lines = brief.read_text().split('\n')
  i = lines.index('files_walked: >')
  assert not lines[i + 2].startswith('  ')     # exactly one continuation line
  header, _, _ = dsp.parse_brief(brief.read_text())
  walked = [f.strip() for f in header['files_walked'].split(';') if f.strip()]
  assert len(walked) == len(set(walked))       # no duplicates
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py::test_extend_rewrites_a_wrapped_files_walked_block -v
```

Expected: FAIL on `assert not lines[i + 2].startswith('  ')` — the stale `  specs/deferred_items.md` line survives as a second continuation line.

- [ ] **Step 3: Replace the splice loop**

In `_extend_brief`, replace:

```python
  for i, line in enumerate(lines):
    if line == 'files_walked: >':
      lines[i + 1] = '  ' + '; '.join(walked)
      break
```

with:

```python
  for i, line in enumerate(lines):
    if line == 'files_walked: >':
      # the block is EVERY two-space continuation line, not just the first:
      # parse_brief folds all of them into one value, so replacing one leaves
      # a stale tail that re-parses as duplicate walked files.
      j = i + 1
      while j < len(lines) and lines[j].startswith('  ') and lines[j].strip():
        j += 1
      lines[i + 1:j] = ['  ' + '; '.join(walked)]
      break
```

- [ ] **Step 4: Run the test and the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: PASS, +1 over Task 5. The existing single-line extend tests must still pass — the `while` loop consumes exactly one line in that case.

- [ ] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "$(cat <<'MSG'
fix(llm-wiki): rewrite the whole files_walked continuation block on extend

Replacing only the first continuation line left a stale tail that
re-parsed as duplicate walked files.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 7: Same-date re-runs must refresh the directory-presence notes

Source item: plan 16 — "`_extend_brief` never renders directory-presence `note:` lines — same divergence class as the fixed is_deferred bug; reachable when dir notes change between two same-date runs."

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py:384-412` (`_extend_brief`, plus a new `_splice_notes` helper above it), `:515-556` (`cmd_inventory` call site)
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: Task 6's splice loop — keep it verbatim inside the restructured function.
- Produces: `_extend_brief(path, repo, head, files, notes, seen) -> int` (new fifth parameter `notes`, the list `walk_specs` returns as its second element). `_splice_notes(lines, notes) -> bool`. Task 8 wraps `_render_new_sections` inside this same function.

**Why this is a real defect:** `cmd_inventory` renders `note: <dir>/: absent` and `note: <dir>/: no .md files` lines only on the fresh-brief path. `_extend_brief` is not even passed `notes`, so on a same-date re-run the brief keeps asserting a directory state that no longer holds. This is the same divergence class `_render_new_sections` was extracted to prevent (the `is_deferred` flag drifting between the two paths).

**Design note — regeneration, not accretion.** The block is rewritten from the current `notes` list, so a note that stopped being true leaves as well as a newly-true one arriving. The note block is script-generated; nothing else writes `note: ` lines at that position.

- [ ] **Step 1: Write the two failing tests**

Append after the Task 6 test:

```python
def test_extend_adds_a_note_for_a_directory_that_vanished(tmp_path, capsys):
  '''Directory-presence notes were rendered only on the fresh-brief path, so
  a same-date re-run left the brief asserting a directory state that no
  longer held.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='specs/completed/*.md') == 0
  brief = root / 'reports/harvest-repo-2026-07-24.md'
  assert 'note: specs/plans/completed/: absent' not in brief.read_text()
  (repo / 'specs/plans/completed/1-a-spec.md').unlink()
  (repo / 'specs/plans/completed').rmdir()
  assert inventory(repo, root) == 0
  assert 'note: specs/plans/completed/: absent' in brief.read_text()


def test_extend_drops_a_note_that_stopped_being_true(tmp_path, capsys):
  '''The other direction: a WALK_DIRS dir that gained a .md file between two
  same-date runs must lose its "no .md files" note. The block is regenerated
  from the current walk, not accreted.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='specs/completed/*.md') == 0
  brief = root / 'reports/harvest-repo-2026-07-24.md'
  assert 'note: specs/plans/: no .md files' in brief.read_text()
  (repo / 'specs/plans/live-plan.md').write_text('# Live plan\n')
  assert inventory(repo, root) == 0
  assert 'note: specs/plans/: no .md files' not in brief.read_text()
```

- [ ] **Step 2: Run them to verify they fail**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py -k "a_directory_that_vanished or stopped_being_true" -v
```

Expected: both FAIL on their final assertion — the note block is untouched by the extend path.

- [ ] **Step 3: Add the `_splice_notes` helper**

Insert immediately above `def _extend_brief(...)`:

```python
def _splice_notes(lines, notes):
  '''Regenerate the header's directory-presence note block in place.
  Regeneration, not accretion: a note that stopped being true (a WALK_DIRS
  dir that gained .md files) must leave, exactly as a newly-true one must
  arrive. -> True if the block changed.

  A brief with no closing '---' is malformed beyond this function's remit:
  leave it alone rather than raising ValueError out of cmd_inventory. The
  repo_head check above already rejects every brief this script did not
  write, so this is a belt-and-braces guard, not a supported input.'''
  if '---' not in lines[1:]:
    return False
  close = lines.index('---', 1)
  at = close + 1
  if at < len(lines) and lines[at] == '':
    at += 1
  start = at
  while at < len(lines) and lines[at].startswith('note: '):
    at += 1
  end = at
  if end > start and end < len(lines) and lines[end] == '':
    end += 1                       # the blank line closing an existing block
  block = [f'note: {n}' for n in notes]
  if block:
    block.append('')
  if lines[start:end] == block:
    return False
  lines[start:end] = block
  return True
```

- [ ] **Step 4: Restructure `_extend_brief`**

Replace the whole function with:

```python
def _extend_brief(path, repo, head, files, notes, seen):
  '''Same-date re-run (spec §7): append sections for files not yet present
  and refresh the directory-presence notes; never overwrite or duplicate.
  One brief = one repo_head.'''
  text = path.read_text()
  header, _, _ = parse_brief(text)
  if header.get('repo_head') != head:
    print(f'error: {path.name} pins repo_head {header.get("repo_head")} but '
          f'HEAD is {head}; use a fresh --date (or re-run at the pinned head)',
          file=sys.stderr)
    return 1
  have = set(re.findall(r'^## (.+)$', text, re.M))
  new = [f for f in files if f not in have]
  lines = text.rstrip('\n').split('\n')
  notes_changed = _splice_notes(lines, notes)
  if not new:
    if notes_changed:
      _atomic_write(path, '\n'.join(lines) + '\n')
      print(f'{path.name}: no new files; notes refreshed')
      return 0
    print(f'{path.name}: no new files; brief unchanged')
    return 0
  body = _render_new_sections(repo, new, seen)
  walked = [f.strip() for f in header.get('files_walked', '').split(';')
            if f.strip()]
  walked += [f for f in new if f not in walked]
  for i, line in enumerate(lines):
    if line == 'files_walked: >':
      # the block is EVERY two-space continuation line, not just the first:
      # parse_brief folds all of them into one value, so replacing one leaves
      # a stale tail that re-parses as duplicate walked files.
      j = i + 1
      while j < len(lines) and lines[j].startswith('  ') and lines[j].strip():
        j += 1
      lines[i + 1:j] = ['  ' + '; '.join(walked)]
      break
  _atomic_write(path, '\n'.join(lines) + '\n\n'
                + '\n'.join(body).rstrip('\n') + '\n')
  print(f'extended {path} (+{len(new)} files)')
  return 0
```

The `files_walked` splice is Task 6's loop verbatim — do not re-derive it. Note that `_splice_notes` inserts only *after* the closing `---`, so the `files_walked` indices found afterwards are unaffected.

- [ ] **Step 5: Pass `notes` at the call site**

In `cmd_inventory`, change:

```python
  if path.exists():
    return _extend_brief(path, repo, head, files, seen)
```

to:

```python
  if path.exists():
    return _extend_brief(path, repo, head, files, notes, seen)
```

- [ ] **Step 6: Run the tests and the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: PASS, +2 over Task 6. Any existing test asserting the exact `no new files; brief unchanged` string must still pass — that branch is reached whenever the notes are unchanged, which is every prior fixture.

- [ ] **Step 7: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "$(cat <<'MSG'
fix(llm-wiki): refresh directory-presence notes on a same-date extend

Notes were rendered only on the fresh-brief path, so a re-run left the
brief asserting a directory state that no longer held.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 8: Guard the unguarded reads in the walk loop

Source item: plan 16 — "Script-family hardening pass: unguarded `read_text()` in the walk loops and the unguarded per-file `sha_table()` `_git` call in `cmd_inventory`."

**Scope reminder (Global Constraints):** this task takes the item's first branch — wrap in the house stderr+exit-1 style, in `distill_specs.py` only. The item's alternative ("or settle the convention repo-wide") is explicitly out of scope; `distill_sessions.py` and `lint_wiki.py` keep their convention and stay deferred.

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py:368-382` (`_render_new_sections`), and its two call sites in `_extend_brief` and `cmd_inventory`
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: Task 7's restructured `_extend_brief`.
- Produces: `_render_new_sections(repo, rels, seen) -> list[str]` now raises `RuntimeError` naming the offending file. Both call sites catch it. Task 9 adds a second git call inside the same `try`.

**Why this is a real defect:** a brief lists every walked file or none at all (spec §7). An unreadable spec file or a git failure mid-walk currently aborts with a traceback, and the operator cannot tell from it which file failed or whether anything was written.

- [ ] **Step 1: Write the two failing tests**

Append after the Task 7 tests:

```python
@pytest.mark.skipif(os.geteuid() == 0, reason='root bypasses chmod')
def test_unreadable_spec_file_is_a_hard_error_not_a_traceback(
    tmp_path, capsys):
  '''The walk loop read each file unguarded: one unreadable file aborted the
  inventory with a traceback instead of the house error line, and the brief
  is all-or-nothing (spec §7) so no partial one may survive.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  target = repo / 'specs/completed/a-spec.md'
  target.chmod(0o000)
  try:
    assert inventory(repo, root) == 1
  finally:
    target.chmod(0o644)
  assert 'error: cannot read specs/completed/a-spec.md' in \
    capsys.readouterr().err
  assert not (root / 'reports/harvest-repo-2026-07-24.md').exists()


def test_unreadable_git_history_is_a_hard_error(tmp_path, capsys,
                                                monkeypatch):
  '''sha_table's _git call was unguarded too. Monkeypatched at the seam
  rather than faked with a corrupt repo: making git fail for ONE file
  mid-walk while the repo-level HEAD check still passes is not arrangeable
  hermetically, and the seam is the thing under test.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)

  def boom(repo_, rel):
    raise RuntimeError('fatal: bad object')

  monkeypatch.setattr(dsp, 'sha_table', boom)
  assert inventory(repo, root) == 1
  assert 'error: cannot read git history for' in capsys.readouterr().err
  assert not (root / 'reports/harvest-repo-2026-07-24.md').exists()
```

- [ ] **Step 2: Run them to verify they fail**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py -k "unreadable_spec_file or unreadable_git_history" -v
```

Expected: the first ERRORs with `PermissionError`, the second with `RuntimeError: fatal: bad object` — both propagating out of `dsp.main` as tracebacks rather than returning 1.

- [ ] **Step 3: Raise a named error from the walk loop**

Replace the body of `_render_new_sections` (keep its existing docstring and append the new paragraph shown):

```python
def _render_new_sections(repo, rels, seen):
  '''Shared per-file section-render loop (cmd_inventory's first pass and
  _extend_brief's accretion pass): read each file at repo_head, build its
  SHA table and seed hits, and render its `## ` section. One place for both
  callers so the is_deferred flag can't drift between them (review finding:
  the extend path once called seed_hits without it, so deferred_items.md
  rendered "- none" when it first entered the brief via that path).

  Raises RuntimeError naming the offending file when a spec file or its git
  history cannot be read: the brief lists every walked file or none at all
  (spec §7), so a mid-walk failure must reach the cmd_* caller as the house
  error line, not a traceback.'''
  body = []
  for rel in rels:
    try:
      text = (repo / rel).read_text()
    except (OSError, UnicodeDecodeError) as exc:
      raise RuntimeError(f'cannot read {rel}: {exc}') from exc
    try:
      shas = sha_table(repo, rel)
    except (RuntimeError, OSError) as exc:
      raise RuntimeError(f'cannot read git history for {rel}: {exc}') from exc
    body += render_file_section(rel, shas,
                                seed_hits(text, rel == DEFERRED_FILE),
                                seen.get(rel, []))
  return body
```

- [ ] **Step 4: Catch it at both call sites**

In `_extend_brief`, replace `body = _render_new_sections(repo, new, seen)` with:

```python
  try:
    body = _render_new_sections(repo, new, seen)
  except RuntimeError as exc:
    print(f'error: {exc}; the brief lists every walked file or none',
          file=sys.stderr)
    return 1
```

In `cmd_inventory`, replace `body += _render_new_sections(repo, files, seen)` with:

```python
  try:
    body += _render_new_sections(repo, files, seen)
  except RuntimeError as exc:
    print(f'error: {exc}; the brief lists every walked file or none',
          file=sys.stderr)
    return 1
```

- [ ] **Step 5: Run the tests and the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: PASS, +2 over Task 7. Confirm `os` and `pytest` are already imported at the top of the test file (they are) — do not add imports.

- [ ] **Step 6: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "$(cat <<'MSG'
fix(llm-wiki): report a failed walk read as an error, not a traceback

The brief is all-or-nothing, so an unreadable spec file or git history now
names the file and exits 1 without writing a partial brief.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 9: Follow renames when looking up `previously seen` keys

Source item: plan 16 — "Renamed spec files lose `previously seen` hinting (prior keys grouped by the old at:-path, looked up by the new walk path)… decide whether rename-following is worth building." The decision was closed on 2026-09-03: **yes, build it.**

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py` — new `renamed_from` after `sha_table` (ends line 156), and `_render_new_sections`
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: Task 8's `try`/`except` around the git call — the new call goes inside it.
- Produces: `renamed_from(repo: Path, rel: str) -> list[str]`, historical repo-relative paths for `rel`, newest first, excluding `rel` itself.

**Why this is a real defect:** `seen_keys_by_file` groups prior-brief keys by the `at:` path recorded in those briefs, and `render_file_section` looks them up by the *current* walk path. `make_repo`'s own fixture history is the case: `specs/a-spec.md` retired to `specs/completed/a-spec.md` by a pure `git mv`. A brief harvested before the retirement records `at: specs/a-spec.md …`, so the next harvest renders `previously seen: - none` and the agent re-proposes a capture already declined.

- [ ] **Step 1: Write the failing test**

Append after the Task 8 tests:

```python
def test_previously_seen_follows_a_rename(tmp_path, capsys):
  '''make_repo retires specs/a-spec.md to specs/completed/a-spec.md with a
  pure git mv. A prior brief recorded its capture under the OLD path, so the
  new walk path found nothing and the agent lost the dedup hint entirely.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  sha = _sha(repo)
  prior = root / 'reports/harvest-repo-2026-07-23.md'
  prior.write_text(
    f'---\nharvest: specs\nrepo: repo\nrepo_path: {repo}\n'
    f'repo_head: {sha}\nroot: {root.resolve()}\ndate: 2026-07-23\n'
    f'prior_brief: none\nfiles_walked: >\n  specs/a-spec.md\n---\n\n'
    f'## specs/a-spec.md\n\ncaptures:\n\n'
    f'- [x] [d-01] Use X over Y\n'
    f'  kind: decision · boundary: transferable\n'
    f'  at: specs/a-spec.md §1 · sha: {sha}\n'
    f'  excerpt: "**Decision:** use X over Y."\n'
    f'  claim: X was chosen over Y.\n')
  assert inventory(repo, root, date='2026-07-24') == 0
  brief = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  section = brief.split('## specs/completed/a-spec.md', 1)[1]
  seen = section.split('previously seen:', 1)[1].split('captures:', 1)[0]
  assert 'd-01' in seen
  assert '- none' not in seen
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py::test_previously_seen_follows_a_rename -v
```

Expected: FAIL on `assert 'd-01' in seen` — the section renders `previously seen:\n- none`.

- [ ] **Step 3: Add `renamed_from`**

Insert immediately after `sha_table` (before `def _classify(status):`):

```python
def renamed_from(repo, rel):
  '''Historical repo-relative paths for rel, newest first, read from the same
  --follow history sha_table walks. `previously seen` keys are grouped by the
  at:-path recorded in prior briefs, so a spec retired between two harvests
  (specs/x.md -> specs/completed/x.md) loses every prior hint unless its old
  names are looked up too.'''
  out = _git(repo, 'log', '--follow', '-M', '--name-status',
             '--diff-filter=R', '--format=', '--', rel)
  olds = []
  for line in out.splitlines():
    parts = line.split('\t')
    if len(parts) == 3 and parts[0].startswith('R') and parts[1] not in olds:
      olds.append(parts[1])
  return olds
```

- [ ] **Step 4: Union the old paths' keys in the walk loop**

In `_render_new_sections`, replace the git block and the render call:

```python
    try:
      shas = sha_table(repo, rel)
    except (RuntimeError, OSError) as exc:
      raise RuntimeError(f'cannot read git history for {rel}: {exc}') from exc
    body += render_file_section(rel, shas,
                                seed_hits(text, rel == DEFERRED_FILE),
                                seen.get(rel, []))
```

with:

```python
    try:
      shas = sha_table(repo, rel)
      olds = renamed_from(repo, rel)
    except (RuntimeError, OSError) as exc:
      raise RuntimeError(f'cannot read git history for {rel}: {exc}') from exc
    # prior briefs key their entries by the at:-path of the day, which is the
    # pre-rename name for anything retired since — order-preserving union so
    # the current path's hints stay first.
    prior_keys = list(seen.get(rel, []))
    for old in olds:
      prior_keys += [k for k in seen.get(old, []) if k not in prior_keys]
    body += render_file_section(rel, shas,
                                seed_hits(text, rel == DEFERRED_FILE),
                                prior_keys)
```

- [ ] **Step 5: Run the test and the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: PASS, +1 over Task 8.

- [ ] **Step 6: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "$(cat <<'MSG'
feat(llm-wiki): follow renames when listing previously-seen captures

Prior briefs key entries by the at:-path of the day, so a spec retired
between harvests lost every dedup hint at its new path.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

## Coverage map

For the Plan Completion Protocol — every unticked plan-16 item in `specs/deferred_items.md` and the task that closes it.

| Source item (plan 16 — 2026-07-25) | Task |
|---|---|
| Script-family hardening pass: unguarded `read_text()` + `sha_table()` `_git` | 8 |
| `_extend_brief` never renders directory-presence `note:` lines | 7 |
| `files_walked:` header splice assumes exactly one continuation line | 6 |
| Ticked q-entries bypass the square-bracket claim check | 1 |
| Brief missing `repo_path:` → `git -C .` foreign-HEAD warning | 5 |
| Hermetic `(also …)` render test | 3 |
| All-q ticked brief edge | 4 |
| Required digest header keys read with hard `[]` in `cmd_assemble` | 5 |
| `_repo_name` YAML-hostile residue | 2 |
| Renamed spec files lose `previously seen` hinting | 9 |

Ten items, nine tasks (Task 5 closes two). Expected on completion: **+12 tests over the pre-Task-1 baseline** (1+1+1+1+2+1+2+2+1).

## Final verification

After Task 9, before the Plan Completion Protocol:

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py
```

Both lints must exit 0. No skill frontmatter changes in this plan, but they are the repo's pre-commit gate for anything under `skills/`.
