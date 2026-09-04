# distill_sessions.py Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the seven remaining deferred items against `skills/llm-wiki/scripts/distill_sessions.py` — one ordering defect that silently renumbers turns, one three-site duplication, and five test-coverage gaps.

**Architecture:** Two behavior/structure changes to the script (a shared time-ordering helper, and a shared `_real_dates` helper that retires a literal duplicated across three call sites), then four test-only tasks that pin branches and helpers currently exercised only indirectly. No new module, no new dependency, no CLI change. The digest format on disk is unchanged except for turn *numbering* in the presence of an undated turn — which is the point of Task 1.

**Tech Stack:** Python (stdlib only: `argparse`, `json`, `re`, `sys`, `pathlib`), pytest via `uv run`. There is no root test runner; this suite is directory-scoped.

**Source:** No spec. The requirements are the seven items selected from `specs/deferred_items.md` § `14-llm-wiki-distiller — 2026-07-23` during a `/deferred` triage on 2026-09-04. The Coverage map at the end maps each item to its task for the Plan Completion Protocol.

## Global Constraints

Copied from the source items, the target file, and the repo's standing conventions. Every task's requirements implicitly include this section.

- **Stdlib only.** `distill_sessions.py`'s module docstring opens with "Stdlib only; deterministic." No import may be added beyond the stdlib. The test file is stdlib + pytest, synthetic fixtures only — no network, no real corpus.
- **Python floor is 3.12, not 3.13.** `bootstrap_wiki.py:319-324` warns that the installed wiki scripts "target Python >= 3.12". Tests run under 3.13, but no 3.13-only syntax may enter `distill_sessions.py`.
- **Style:** 2-space indent, single quotes, matching the surrounding file. Tests use the bare import `import distill_sessions as ds` already at the top of the test file, and the existing `_rec` / `_write_jsonl` helpers.
- **Test command (directory-scoped — a repo-root pytest run fails outright, because `geographic-codes` and `classification-codes` both ship a `test_build.py` whose basenames collide under pytest's prepend import mode):**
  ```bash
  cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
  ```
  **Record the count `pytest -q` reports before Task 1 and treat it as the baseline — do not hard-code a number.** (This checkout reports 243 at the time of writing, matching `CLAUDE.md:73`, but a fresh execution session may differ.) Every task below states how many tests it *adds*; the count must only ever grow by exactly that many.
- **Cross-module contract.** `distill_specs.py` does `from distill_sessions import redact, slugify`. Neither function's signature or behavior may change in this plan — Task 3 only *tests* `slugify`. If a task tempts you to adjust either, stop and ask.
- **Do not edit the deployed copy.** `~/research-wiki/scripts/distill_sessions.py` is a managed install (`bootstrap_wiki.py` `MANAGED_SCRIPTS`), refreshed with `bootstrap_wiki.py --force`. It is byte-identical to the repo copy today. The repo copy is the only source of truth; no task in this plan touches the wiki root.
- **Scope fence — one script and its suite.** Only `skills/llm-wiki/scripts/distill_sessions.py` and `skills/llm-wiki/scripts/test_distill_sessions.py` change (plus one `CLAUDE.md` line in Task 5). Do **not** touch `lint_wiki.py`, `distill_specs.py`, or `bootstrap_wiki.py`: their own deferred items are separate and stay deferred. If you believe a change must widen, stop and ask rather than widening.
- **Determinism:** the script is deterministic given its inputs and reads no clock, network, or environment. No task may add one.
- **Commits:** one per task, conventional-commit subject, ending with the trailer:
  ```
  Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
  ```

## Planner's note on scope, read before Task 1

Two places where this plan deliberately departs from the deferred items as written. Both are recorded here so a reviewer sees them as decisions, not drift.

1. **The recorded remedy for the ordering item is wrong and must not be implemented.** The item proposes "a `(ts, original_index)` compound sort key". That does not fix the symptom the same item describes. `list.sort` is already stable, so same-timestamp turns already keep their order — the index adds nothing there; and an undated turn's key is still `''`, which still sorts below every real timestamp, so it still jumps to the front. Task 1 Step 3 makes you *prove* this before implementing the real fix. This is the same failure mode the backlog records for `sbc_rank` in § `20-bayesian-workflow-book-integration`, where a recorded remedy shipped verbatim would have traded a loud crash for a silently wrong result.

2. **The ordering fix lands at both sort sites, not just the one the item names.** The item names `_claude_ai_turns`. `reconstruct` (the claude-code path) has the byte-identical defect one screen away. The item's own justification — turn numbers are spec §16.4's locator currency for future captures — applies to both paths equally, and Task 2 exists precisely because this file has already had the same bug fixed independently at two of three sites before anyone noticed the duplication. Fixing one and leaving the other would repeat that. Both sites get the same shared helper.

## File Structure

Only two files change, plus one line of `CLAUDE.md`. Neither script is split; both are well under any size that would warrant it.

| File | Responsibility | Change |
|---|---|---|
| `skills/llm-wiki/scripts/distill_sessions.py` | The whole session distiller: adapters for both sources, narrative reconstruction, redaction, digest render | Modified in Tasks 1–2 |
| `skills/llm-wiki/scripts/test_distill_sessions.py` | Its tests (stdlib + pytest, synthetic fixtures) | Modified in all 5 tasks |
| `CLAUDE.md` | Repo command reference; line 73 records this suite's test count | One line, Task 5 |

Functions touched, in plan order: new `_ordered_by_time` + `reconstruct` + `_claude_ai_turns` (T1); new `_real_dates` + new `_SENTINEL_DATE` + `_turn_date` + `iter_claude_code` + `iter_claude_ai` + `write_digest` (T2); test-only (T3, T4, T5).

---

### Task 1: An undated turn keeps its place instead of jumping to the front

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_sessions.py:71` (`reconstruct`), `:227` (`_claude_ai_turns`), and a new helper above `reconstruct`
- Test: `skills/llm-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Produces: `_ordered_by_time(turns) -> list[dict]` — pure, reads only `t['ts']` on each dict, returns a new list. Both `reconstruct` and `_claude_ai_turns` call it. No other task consumes it.

**Adds 3 tests.**

- [ ] **Step 1: Write the failing tests**

Append these three to `skills/llm-wiki/scripts/test_distill_sessions.py`, next to the other `reconstruct` tests:

```python
def test_claude_ai_undated_turn_keeps_its_place():
  '''An undated message must not be renumbered to the front. Turn numbers are
  spec §16.4's locator currency for future captures, so a mid-conversation
  message with no created_at has to stay between its neighbours.'''
  conv = {'chat_messages': [
    {'sender': 'human', 'text': 'first', 'created_at': '2026-05-14T10:00:00Z'},
    {'sender': 'assistant', 'text': 'undated middle', 'created_at': ''},
    {'sender': 'human', 'text': 'third', 'created_at': '2026-05-14T10:01:00Z'},
  ]}
  turns = ds._claude_ai_turns(conv)
  assert [t['text'] for t in turns] == ['first', 'undated middle', 'third']
  assert [t['n'] for t in turns] == [1, 2, 3]


def test_reconstruct_undated_record_keeps_its_place():
  '''The same defect on the claude-code path: a record with no timestamp must
  not sort ahead of records that genuinely came first.'''
  records = [
    _rec('a', None, 'user', 'first', ts='2026-05-14T10:00:00Z'),
    _rec('b', 'a', 'assistant', [{'type': 'text', 'text': 'undated middle'}],
         ts=''),
    _rec('c', 'b', 'user', 'third', ts='2026-05-14T10:01:00Z'),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert [t['text'] for t in turns] == ['first', 'undated middle', 'third']
  assert [t['n'] for t in turns] == [1, 2, 3]


def test_leading_undated_turn_stays_first():
  '''Guard on the fix, not on the bug: an undated turn that really was first
  has no dated predecessor to inherit from, so it must stay at position 1.
  This one passes before the fix and must still pass after it.'''
  records = [
    _rec('a', None, 'user', 'undated opener', ts=''),
    _rec('b', 'a', 'assistant', [{'type': 'text', 'text': 'later'}],
         ts='2026-05-14T10:00:00Z'),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert [t['text'] for t in turns] == ['undated opener', 'later']
```

- [ ] **Step 2: Run the tests to verify the first two fail**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k "keeps_its_place or leading_undated"
```

Expected: `2 failed, 1 passed`. Both failures are the order assertion, with the undated turn at index 0 — e.g.
`assert ['undated middle', 'first', 'third'] == ['first', 'undated middle', 'third']`.
`test_leading_undated_turn_stays_first` passes already; that is correct and expected.

Do **not** filter on `-k "undated"`: two pre-existing tests
(`test_claude_code_since_keeps_session_with_undated_first_turn` and its
`claude_ai` twin) match that substring and would muddy the count. Both were
confirmed unaffected by this task's change.

- [ ] **Step 3: Prove the remedy recorded in the backlog is a no-op**

Do not skip this. The deferred item proposes a `(ts, original_index)` compound key. Apply it temporarily at `distill_sessions.py:227`, replacing `turns.sort(key=lambda t: t['ts'])` with:

```python
  turns = [t for _, t in sorted(enumerate(turns), key=lambda p: (p[1]['ts'], p[0]))]
```

Run:

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k "claude_ai_undated"
```

Expected: still `1 failed`, with the same assertion and the same wrong order. `''` still sorts below every real timestamp, and `list.sort` was already stable, so the index changes nothing. **Revert this edit** (`git checkout -- distill_sessions.py`) before Step 4 and implement the real fix instead.

- [ ] **Step 4: Write the helper**

Insert immediately above `def reconstruct(...)` in `skills/llm-wiki/scripts/distill_sessions.py`:

```python
def _ordered_by_time(turns):
  '''Sort by timestamp while leaving undated turns where they were.

  A turn with no timestamp inherits the last dated turn before it, so it
  sorts beside its neighbour instead of jumping to the front on ''. The
  original index breaks the resulting ties, which also pins the ordering
  rather than leaning on list.sort's stability. A leading undated turn has
  nothing to inherit, keeps '', and stays first -- which is where it was.

  NOT a (ts, index) compound key: that was the remedy first recorded for this
  bug and it is a no-op. Stability already handled equal timestamps, and ''
  still sorts below every real one.
  '''
  keyed = []
  carried = ''
  for i, t in enumerate(turns):
    if t['ts']:
      carried = t['ts']
    keyed.append(((carried, i), t))
  keyed.sort(key=lambda pair: pair[0])
  return [t for _, t in keyed]
```

- [ ] **Step 5: Wire both call sites**

In `reconstruct`, replace:

```python
  narrative.sort(key=lambda t: t['ts'])
  return _number(_merge_requests(narrative))
```

with:

```python
  return _number(_merge_requests(_ordered_by_time(narrative)))
```

In `_claude_ai_turns`, replace:

```python
  turns.sort(key=lambda t: t['ts'])
  for i, t in enumerate(turns, start=1):
```

with:

```python
  turns = _ordered_by_time(turns)
  for i, t in enumerate(turns, start=1):
```

- [ ] **Step 6: Run the whole suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: baseline + 3, all passing. `_merge_requests`'s "only adjacent records (post-sort) merge" contract still holds — the helper returns a list in the same shape, just ordered differently.

- [ ] **Step 7: Commit**

```bash
git add skills/llm-wiki/scripts/distill_sessions.py skills/llm-wiki/scripts/test_distill_sessions.py
git commit -m "fix(llm-wiki): keep undated turns in place when ordering a session

An undated turn's '' timestamp sorted below every real one, renumbering it
to position 1 ahead of turns that actually came first. Turn numbers are the
spec's locator currency, so this silently invalidated future citations.

Both sort sites share one _ordered_by_time helper: a turn with no timestamp
inherits its last dated predecessor. The (ts, index) key first recorded as
the remedy is a no-op -- list.sort was already stable and '' still sorts
first -- and the docstring says so.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: One `_real_dates` helper replaces the sentinel filter duplicated at three sites

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_sessions.py` — new `_SENTINEL_DATE` and `_real_dates` beside `_turn_date`; call sites in `iter_claude_code`, `iter_claude_ai`, `write_digest`
- Test: `skills/llm-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `_SENTINEL_DATE` (str, `'0000-00-00'`) and `_real_dates(turns) -> list[str]` — sorted `YYYY-MM-DD` strings, sentinels dropped, possibly empty. Callers supply their own sentinel when it is empty, because the meaning differs per site (a date floor vs. both ends of a range).

**Adds 1 test.** This is a behavior-preserving refactor; the existing suite is the real regression net and must stay green with no assertion changes.

- [ ] **Step 1: Write the failing test**

Append to `test_distill_sessions.py`:

```python
def test_real_dates_drops_sentinels_and_sorts():
  '''The date floor must ignore undated turns: the sentinel sorts below every
  real date, so leaving it in poisons min(). One helper is the single place
  that rule lives -- the identical sentinel-poisons-min() bug had to be found
  and fixed independently at two of three sites before the duplication was
  even noticed.'''
  turns = [{'ts': '2026-05-15T09:00:00Z'}, {'ts': ''},
           {'ts': '2026-05-14T10:00:00Z'}, {'ts': 'not-a-timestamp'}]
  assert ds._real_dates(turns) == ['2026-05-14', '2026-05-15']
  assert ds._real_dates([{'ts': ''}]) == []
  assert ds._real_dates([]) == []
  assert ds._SENTINEL_DATE == '0000-00-00'
```

- [ ] **Step 2: Run it to verify it fails**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k "real_dates"
```

Expected: FAIL with `AttributeError: module 'distill_sessions' has no attribute '_real_dates'`.

- [ ] **Step 3: Add the constant and the helper**

In `skills/llm-wiki/scripts/distill_sessions.py`, replace this block:

```python
_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def _turn_date(ts):
  '''YYYY-MM-DD from an ISO timestamp, or the sentinel for anything that is
  not date-shaped -- a malformed value must never become a digest's date.'''
  head = ts[:10] if ts else ''
  return head if _DATE_RE.match(head) else '0000-00-00'
```

with:

```python
_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
_SENTINEL_DATE = '0000-00-00'


def _turn_date(ts):
  '''YYYY-MM-DD from an ISO timestamp, or the sentinel for anything that is
  not date-shaped -- a malformed value must never become a digest's date.'''
  head = ts[:10] if ts else ''
  return head if _DATE_RE.match(head) else _SENTINEL_DATE


def _real_dates(turns):
  '''Sorted YYYY-MM-DD dates of the turns that carry a real one, sentinels
  dropped. Empty when every turn is undated -- the caller supplies the
  sentinel then, because what it stands for differs by site (a date floor at
  one end vs. both ends of a range).

  Single source for this rule on purpose: it was open-coded at three sites,
  and the same sentinel-poisons-min() bug had to be found and fixed twice
  before the duplication was noticed.
  '''
  return sorted(d for d in (_turn_date(t['ts']) for t in turns)
                if d != _SENTINEL_DATE)
```

- [ ] **Step 4: Run the new test to verify it passes**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k "real_dates"
```

Expected: `1 passed`.

- [ ] **Step 5: Replace the first call site (`iter_claude_code`)**

Replace:

```python
    real = sorted(d for d in (_turn_date(t['ts']) for t in turns)
                  if d != '0000-00-00')
    first_date = real[0] if real else '0000-00-00'
```

with:

```python
    real = _real_dates(turns)
    first_date = real[0] if real else _SENTINEL_DATE
```

- [ ] **Step 6: Replace the second call site (`iter_claude_ai`)**

The block there is byte-identical to Step 5's. Replace it with the same two lines:

```python
    real = _real_dates(turns)
    first_date = real[0] if real else _SENTINEL_DATE
```

- [ ] **Step 7: Replace the third call site (`write_digest`)**

Replace:

```python
  real = sorted(d for d in (_turn_date(t['ts']) for t in turns)
                if d != '0000-00-00')
  if real:
    first_date, last_date = real[0], real[-1]
  else:
    first_date, last_date = '0000-00-00', '0000-00-00'
```

with:

```python
  real = _real_dates(turns)
  if real:
    first_date, last_date = real[0], real[-1]
  else:
    first_date, last_date = _SENTINEL_DATE, _SENTINEL_DATE
```

- [ ] **Step 8: Confirm the literal is gone from the logic and the suite is green**

```bash
cd skills/llm-wiki/scripts && grep -n "0000-00-00" distill_sessions.py
```

Expected: exactly one line — the `_SENTINEL_DATE = '0000-00-00'` definition. Any other hit means a call site was missed.

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: baseline + 4 (Task 1's 3 plus this one), all passing, **with no existing assertion edited**. `test_write_digest_zero_turns_keeps_sentinel_range_f2_guard` still asserts the literal `dates: 0000-00-00/0000-00-00` in the written digest — that is the rendered output, not the logic, and must not be changed to reference the constant.

- [ ] **Step 9: Commit**

```bash
git add skills/llm-wiki/scripts/distill_sessions.py skills/llm-wiki/scripts/test_distill_sessions.py
git commit -m "refactor(llm-wiki): one _real_dates helper for the sentinel filter

The exclude-sentinel-then-floor rule was open-coded at three sites with the
'0000-00-00' literal in each. The same sentinel-poisons-min() bug had to be
found and fixed independently at two of them before the duplication was
noticed, which is the argument for extracting it.

Behavior-preserving: the existing suite passes with no assertion changed.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Direct tests for the two pure helpers

**Files:**
- Test: `skills/llm-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Consumes: `ds._project_name(records, proj_dir)` and `ds.slugify(text, max_words=6)` as they already exist. **Test-only task — `distill_sessions.py` must not change.**

**Adds 2 tests.** Both helpers are today exercised only indirectly (`_project_name`'s no-`cwd` branch runs on real-corpus smoke runs but has no unit test; `slugify` only through `write_digest`). `_turn_date` needs nothing — it already gained a direct test on 2026-09-02, which is why the source item is only half open.

- [ ] **Step 1: Write the failing tests**

Append to `test_distill_sessions.py`:

```python
def test_project_name_falls_back_to_the_encoded_dir_name():
  '''The no-cwd branch. With no record carrying cwd, the project name comes
  from the encoded directory's last segment. This branch runs on real-corpus
  sessions but had no unit test, and it is lossy by design -- the encoded name
  splits a hyphenated project, so alt-nfp arrives as "nfp". Pinned so the loss
  is a recorded fact rather than a surprise, and so an inverted precedence
  (dir name winning over cwd) cannot land unnoticed.'''
  assert ds._project_name([], '-Users-lowell-Projects-alt-nfp') == 'nfp'
  assert ds._project_name([{'type': 'user'}],
                          '-Users-lowell-Projects-bls-stats') == 'stats'
  assert ds._project_name([], 'trailing-') == 'trailing'
  assert ds._project_name([], '') is None
  assert ds._project_name([], None) is None
  # cwd, when present, still wins over the encoded name
  assert ds._project_name([{'cwd': '/Users/lowell/Projects/alt-nfp'}],
                          '-Users-lowell-Projects-alt-nfp') == 'alt-nfp'


def test_slugify_rules():
  '''slugify is reached only through write_digest here, and distill_specs.py
  imports it, so its contract is cross-module. Pin the four rules directly:
  lowercase alphanumeric runs joined by hyphens, at most max_words words, a
  60-character cap, and the "session" fallback when nothing survives.'''
  assert ds.slugify('Plan the LLM wiki!') == 'plan-the-llm-wiki'
  assert ds.slugify('one two three four five six seven') == \
      'one-two-three-four-five-six'
  assert ds.slugify('one two three', max_words=2) == 'one-two'
  assert ds.slugify('') == 'session'
  assert ds.slugify(None) == 'session'
  assert ds.slugify('!!! ???') == 'session'
  assert len(ds.slugify('a1b2c3d4' * 30)) == 60
```

- [ ] **Step 2: Run them**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k "project_name_falls_back or slugify_rules"
```

Expected: `2 passed`. These are characterization tests for correct existing code, so they are green on arrival — there is no RED phase to stage. Confirm they are *meaningful* with the mutation check in Step 3 instead.

- [ ] **Step 3: Mutation-check both tests**

Temporarily make each change, run the two tests, confirm the failure, then revert with `git checkout -- distill_sessions.py`.

1. In `_project_name`, change `return Path(cwd).name` to `return None`.
   Expected: `test_project_name_falls_back_to_the_encoded_dir_name` FAILS on the last assertion (`None == 'alt-nfp'`).
2. In `slugify`, change `[:60]` to `[:200]`.
   Expected: `test_slugify_rules` FAILS on `assert len(...) == 60` with `240 == 60`.

If either mutation leaves both tests green, the test is not pinning what it claims — fix the test before continuing.

- [ ] **Step 4: Confirm the script is untouched and the suite is green**

```bash
cd skills/llm-wiki/scripts && git diff --exit-code distill_sessions.py && echo "script unchanged"
```

Expected: prints `script unchanged` and exits 0. This task is test-only; a non-empty diff means a mutation was not reverted.

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: baseline + 6.

- [ ] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/test_distill_sessions.py
git commit -m "test(llm-wiki): pin _project_name's no-cwd branch and slugify directly

Both were exercised only indirectly -- _project_name's fallback ran on real
corpus smoke runs with no unit test, and slugify only through write_digest
despite distill_specs.py importing it. Each assertion is mutation-checked.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Cover `reconstruct`'s two untested filter branches

**Files:**
- Test: `skills/llm-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Consumes: `ds.reconstruct(records, include_sidechains)` and the existing `_rec(uuid, parent, role, content, **extra)` helper — extra kwargs land on the record via `r.update(extra)`, so `isMeta=True` and `isCompactSummary=True` both work. **Test-only task.**

**Adds 2 tests.** The `isMeta` drop branch has no test at all. The `not compaction` clause in the plumbing filter is only reached today by a compaction record that *also* carries text — which the text check alone would keep, so the clause itself is unexercised.

- [ ] **Step 1: Write the failing tests**

Append to `test_distill_sessions.py`, beside the other `reconstruct` tests:

```python
def test_reconstruct_drops_meta_records():
  '''isMeta records are Claude Code's own bookkeeping, not conversation. The
  drop branch had no test, so an inverted or deleted guard would have leaked
  bookkeeping into every digest unnoticed.'''
  records = [
    _rec('a', None, 'user', 'real question', ts='2026-05-14T10:00:00Z'),
    _rec('m', 'a', 'user', 'meta bookkeeping', ts='2026-05-14T10:00:01Z',
         isMeta=True),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert [t['text'] for t in turns] == ['real question']


def test_reconstruct_keeps_a_textless_compaction_record():
  '''The `not compaction` clause in the tool-plumbing filter. A compaction
  record with genuinely empty text and no tool calls must survive, where the
  same record without the flag is dropped as plumbing. Existing coverage only
  has a compaction record that also carries text, which the text check alone
  would already keep -- so the clause itself was never exercised.'''
  kept = ds.reconstruct(
    [_rec('a', None, 'user', '', ts='2026-05-14T10:00:00Z',
          isCompactSummary=True)],
    include_sidechains=False)
  assert len(kept) == 1
  assert kept[0]['compaction'] is True
  assert kept[0]['text'] == ''

  dropped = ds.reconstruct(
    [_rec('a', None, 'user', '', ts='2026-05-14T10:00:00Z')],
    include_sidechains=False)
  assert dropped == []
```

- [ ] **Step 2: Run them**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k "drops_meta or textless_compaction"
```

Expected: `2 passed` — characterization tests for correct code, green on arrival. Step 3 proves they bite.

- [ ] **Step 3: Mutation-check both tests**

Temporarily make each change, run the two tests, confirm the failure, then revert with `git checkout -- distill_sessions.py`.

1. In `reconstruct`, delete the two lines:
   ```python
    if r.get('isMeta'):
      continue
   ```
   Expected: `test_reconstruct_drops_meta_records` FAILS — the list becomes `['real question', 'meta bookkeeping']`.
2. In `reconstruct`, change `if not text and not names and not compaction:` to `if not text and not names:`.
   Expected: `test_reconstruct_keeps_a_textless_compaction_record` FAILS on `assert len(kept) == 1` with `0 == 1`.

- [ ] **Step 4: Confirm the script is untouched and the suite is green**

```bash
cd skills/llm-wiki/scripts && git diff --exit-code distill_sessions.py && echo "script unchanged"
```

Expected: prints `script unchanged` and exits 0.

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: baseline + 8.

- [ ] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/test_distill_sessions.py
git commit -m "test(llm-wiki): cover reconstruct's isMeta drop and textless compaction

Neither branch was exercised: isMeta had no test, and the `not compaction`
clause was only ever reached by a compaction record that also carried text,
which the text check alone would have kept. Both mutation-checked.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Cover what `write_digest` actually renders

**Files:**
- Modify: `skills/llm-wiki/scripts/test_distill_sessions.py:159-213` (three existing tests gain one assertion each)
- Modify: `CLAUDE.md:73` (test count)
- Test: `skills/llm-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Consumes: `ds.write_digest(session, out) -> Path | None`, unchanged. **Test-only task apart from the `CLAUDE.md` line.**

**Adds 1 test** and strengthens 3 existing ones (no count change from those). Two source items are closed here: the `' [compaction summary]'` marker was never asserted in a written digest — Task 4 of the original plan only checked the flag reaching `reconstruct`'s output — and the three `project=None` fixtures never asserted `project:` is actually absent from the frontmatter.

- [ ] **Step 1: Write the failing test for the marker**

Append to `test_distill_sessions.py`:

```python
def test_write_digest_renders_the_compaction_marker(tmp_path):
  '''Coverage elsewhere stops at the compaction flag reaching reconstruct's
  output. This pins the string write_digest actually renders into the body,
  and that an unflagged turn does not get it.'''
  out = tmp_path / 'sessions'
  session = {
    'session_id': 'facefeed0001', 'source': 'claude-code', 'project': None,
    'turns': [
      {'n': 1, 'role': 'user', 'text': 'compacted context', 'tools': '',
       'compaction': True, 'ts': '2026-05-14T10:00:00Z'},
      {'n': 2, 'role': 'user', 'text': 'ordinary turn', 'tools': '',
       'compaction': False, 'ts': '2026-05-14T10:01:00Z'},
    ],
  }
  p = ds.write_digest(session, out)
  assert p is not None
  text = p.read_text(encoding='utf-8')
  assert '**[01] user:** [compaction summary] compacted context' in text
  assert '**[02] user:** ordinary turn' in text
  assert text.count('[compaction summary]') == 1
  assert 'project:' not in text
```

- [ ] **Step 2: Run it**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k "renders_the_compaction_marker"
```

Expected: `1 passed` — characterization of correct code. Step 4 proves it bites.

- [ ] **Step 3: Strengthen the three `project=None` tests**

Each of these builds a session with `'project': None` but never checks the frontmatter omits the key. Add one assertion to each.

In `test_write_digest_caps_long_slug_f1`, replace:

```python
  assert len(p.name) <= 83
```

with:

```python
  assert len(p.name) <= 83
  assert 'project:' not in p.read_text(encoding='utf-8')
```

In `test_write_digest_ignores_missing_ts_in_date_range_f2`, replace:

```python
  assert 'dates: 2026-05-15/2026-05-15' in text
```

with:

```python
  assert 'dates: 2026-05-15/2026-05-15' in text
  assert 'project:' not in text
```

In `test_write_digest_zero_turns_keeps_sentinel_range_f2_guard`, replace:

```python
  assert '**[' not in text  # empty body: no turn lines rendered
```

with:

```python
  assert '**[' not in text  # empty body: no turn lines rendered
  assert 'project:' not in text
```

- [ ] **Step 4: Mutation-check both changes**

Temporarily make each change, run the suite, confirm the failure, then revert with `git checkout -- distill_sessions.py`.

1. In `write_digest`, change `if session.get('project'):` to `if True:`.
   Expected: all four tests carrying an `assert 'project:' not in text` FAIL — the frontmatter renders the literal line `project: None`.
2. In `write_digest`, change `marker = ' [compaction summary]' if t['compaction'] else ''` to `marker = ''`.
   Expected: `test_write_digest_renders_the_compaction_marker` FAILS on the first `in text` assertion.

- [ ] **Step 5: Confirm the script is untouched, the test file still holds its changes, and the suite is green**

```bash
cd skills/llm-wiki/scripts && git diff --exit-code distill_sessions.py && echo "script unchanged"
```

Expected: prints `script unchanged` and exits 0.

```bash
cd skills/llm-wiki/scripts && git diff --stat test_distill_sessions.py
```

Expected: a **non-empty** diff — roughly 20 insertions across the one new test and the three added assertions. Unlike Tasks 3 and 4, three of this task's four changes strengthen *existing* tests, so they do not move the test count and the suite total cannot detect their loss. If you reverted the Step 4 mutations with a bare `git checkout .` or `git checkout --` rather than the script path, this diff will be empty and Step 3's work is gone — redo Steps 1 and 3 before continuing.

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: baseline + 9, all passing.

- [ ] **Step 6: Sync the test count in `CLAUDE.md`**

`CLAUDE.md:73` reads `# 243 tests (stdlib only; these are the scripts the bootstrap installs to a wiki)`. Replace `243` with the number `pytest -q` just reported — do not compute it, copy it from the run in Step 5. Leave the rest of the line alone.

- [ ] **Step 7: Commit**

```bash
git add skills/llm-wiki/scripts/test_distill_sessions.py CLAUDE.md
git commit -m "test(llm-wiki): pin write_digest's compaction marker and absent project key

The marker string was never asserted in a written digest -- existing coverage
stopped at the flag reaching reconstruct's output -- and the three project=None
fixtures never checked the frontmatter actually omits the key. Both
mutation-checked; CLAUDE.md's count for this suite synced.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Coverage map

For the Plan Completion Protocol — every selected item in `specs/deferred_items.md` § `14-llm-wiki-distiller — 2026-07-23` and the task that closes it.

| Source item (plan 14 — 2026-07-23) | Task |
|---|---|
| `_claude_ai_turns` sorts by `ts` with no tiebreaker (undated turn renumbered to the front) | 1 |
| Sentinel-date-filtering duplicated verbatim across three sites | 2 |
| `_project_name`'s no-`cwd` fallback branch has no dedicated unit test | 3 |
| `slugify` and `_turn_date` have no test calling them directly | 3 (see note) |
| `reconstruct`'s `isMeta` drop branch + the `not compaction` guard clause | 4 |
| `write_digest`'s `' [compaction summary]'` marker rendering is untested | 5 |
| Three `project=None` tests never assert `'project:'` is absent | 5 |

Seven items, five tasks. Expected on completion: **+9 tests over the pre-Task-1 baseline** (3+1+2+2+1).

**Note for the ticking pass:** the `slugify` / `_turn_date` item is only half open. `_turn_date` gained a direct test on 2026-09-02 (`test_turn_date_rejects_malformed_timestamp`, added by a `/deferred` quick fix); this plan closes the `slugify` half. Tick it with that qualification rather than as if both halves were outstanding.

**Item recorded during triage, deliberately not in scope:** the ordering item's decision note ("renumber now — the owner released the batch-with-another-numbering-affecting-change condition") is discharged by Task 1. No other numbering-affecting change exists in this plan, so no sequencing window is needed.

## Final verification

After Task 5, before the Plan Completion Protocol:

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Baseline + 9, zero failures.

```bash
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py
```

Both lints must exit 0. No skill frontmatter changes in this plan, but they are the repo's pre-commit gate for anything under `skills/`.

```bash
cd /Users/lowell/Projects/agent-skills && git diff --stat main...HEAD
```

Expected: exactly three files — `skills/llm-wiki/scripts/distill_sessions.py`, `skills/llm-wiki/scripts/test_distill_sessions.py`, `CLAUDE.md`. Anything else means the scope fence was crossed.

**Deployed copy:** `~/research-wiki/scripts/distill_sessions.py` was byte-identical to the repo copy before this plan and is now stale by Tasks 1–2. Refreshing it is `bootstrap_wiki.py --force` at the owner's discretion, on the owner's machine — it is **not** a task in this plan and must not be done as part of execution.
