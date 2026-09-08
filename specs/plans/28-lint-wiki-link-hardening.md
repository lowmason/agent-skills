# lint_wiki.py Link-Checking Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Execution mode chosen at the 2026-09-08 handoff: INLINE.** Use the **executing-plans** skill and work the tasks yourself in plan order, in this session. Do **not** dispatch subagents per task — the partner chose inline execution deliberately. executing-plans' stop-and-ask rules and completion chain apply.

**Goal:** Close the three recorded link-checking holes in `skills/llm-wiki/scripts/lint_wiki.py` so that a broken link cannot hide behind nested brackets, a CommonMark link title, a self-reference, or a case-insensitive filesystem.

**Architecture:** All four code tasks touch one file plus its test file. Two tasks widen *recognition* (the link regexes see links they currently skip); two tasks tighten *resolution* (what counts as a real, inbound-referencing link). Each task is a self-contained red→green→commit cycle. No new severity level is introduced — every finding stays in the existing `ERROR` / `WARN` vocabulary.

**Tech Stack:** Python 3.13, standard library only. pytest for tests, run through `uv` with inline deps. No third-party imports may enter `lint_wiki.py` or `test_lint_wiki.py`.

## Global Constraints

There is no spec for this plan; the requirements are three deferred items in `specs/deferred_items.md` under `## 13-llm-wiki — 2026-07-22`, quoted verbatim in the tasks below. These constraints are project-wide and every task's requirements implicitly include them.

- **Indentation in `skills/llm-wiki/scripts/` is TWO spaces, not four.** This differs from the rest of the repo and is deliberate. Match the file you are editing. Do not reformat surrounding code.
- **Single quotes** for Python strings (repo convention, `CLAUDE.md`). Docstrings use `'''`.
- **Standard library only.** `lint_wiki.py` ships to user wikis with no dependency install; `test_lint_wiki.py` is stdlib + pytest, building fixture wikis in `tmp_path`.
- **Test command** — run from inside the scripts directory, never the repo root (a repo-root collection fails outright):
  ```bash
  cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
  ```
  Baseline before this plan: **252 passed** for the directory, **83 passed** for `test_lint_wiki.py` alone. Report test growth as a **+N delta**, never as a new absolute total — a later session will not have this session's tree.
- **`lint_wiki.py` is a managed install.** It is listed in `MANAGED_SCRIPTS` at `skills/llm-wiki/scripts/bootstrap_wiki.py:48`. Edit only the repo copy. **Never hand-edit `~/research-wiki/scripts/lint_wiki.py`** — refreshing a deployed wiki is `bootstrap_wiki.py --force`, and it is the owner's call. This plan will leave the deployed copy stale; that is expected and belongs to the existing owner-only item in `specs/deferred_items.md` § `26-distill-sessions-hardening`.
- **Do not introduce a new severity.** `lint_wiki.py` emits `('ERROR' | 'WARN', path, message)` tuples. The retired spec `specs/completed/lint-wiki-citation-contract.md` explicitly declined a third severity as YAGNI, and two open backlog items depend on that decision still standing. Nothing in this plan needs one.
- **Do not touch `specs/deferred_items.md` during execution.** The Plan Completion Protocol ticks the three source items at the end, not mid-plan.
- **Never regress an existing test.** All 252 must stay green at every commit.

---

## File Structure

| File | Responsibility | Tasks |
|---|---|---|
| `skills/llm-wiki/scripts/lint_wiki.py` | The linter. Modify `MD_LINK_RE`, `INDEX_LINE_RE`, `check_links`, `_index_targets`; add two module-level helpers. | 1–4 |
| `skills/llm-wiki/scripts/test_lint_wiki.py` | Fixture-wiki tests. Append new tests near their subject-matter neighbours. | 1–4 |
| `skills/llm-wiki/scripts/schema-template.md` | The wiki contract shipped to new wikis. Gains two sentences under `### Body conventions`. | 5 |
| `CLAUDE.md` | Repo command reference; carries per-suite test counts. | 5 |

No new files. No file is split — `lint_wiki.py` is 371 lines and stays comfortably focused.

---

### Task 1: `MD_LINK_RE` misses a link whose text contains nested brackets

**Files:**
- Modify: `skills/llm-wiki/scripts/lint_wiki.py:14` (`MD_LINK_RE`)
- Test: `skills/llm-wiki/scripts/test_lint_wiki.py` (append after `test_broken_relative_link_is_error`, currently at line 158)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `MD_LINK_RE` — still a compiled pattern with exactly **one** capturing group, group 1 being everything between `(` and `)`. Tasks 2 and 4 rely on that shape and on `MD_LINK_RE.findall(body)` returning a list of plain strings.

**The requirement (deferred item, verbatim):**

> D2 — nested brackets in link text break both directions: `MD_LINK_RE` misses a genuinely-broken link like `[the [above] discussion](samplers/none.md)` AND `BODY_CITE_RE` fabricates a citation from the link text. Fix `MD_LINK_RE` to allow one level of balanced nested brackets, and exclude link-text spans from citation matching. Edge case; unlikely in early content.
>
> → REDUCED by plan 23 (still open): the citation-fabrication half is closed — the recognition rule rejects the fabricated token (`the`, position `[above`), verified as acceptance case 14 and observable as a red row in that plan's Task 1 Step 2. What remains is the `MD_LINK_RE` nesting half alone: a genuinely-broken link like `[the [above] discussion](samplers/none.md)` is still missed. No longer needs "exclude link-text spans from citation matching" — write the mechanical plan against the nesting fix only.

**Only the nesting half is in scope.** Do not touch `BODY_CITE_RE` or `_is_citation`; that half is already closed and re-opening it risks the D1 false-positive regression that plan 23 fixed.

**Why the current pattern misses it.** `MD_LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')`. Against `[the [above] discussion](samplers/none.md)` the engine matches `[` then `[^\]]*` = `the [above` then `]`, and then requires `(` — but the next character is a space. It backtracks, retries from `[above]`, again requires `(` and finds a space. No match anywhere, so the broken target `samplers/none.md` is never checked.

- [ ] **Step 1: Write the failing test**

Append to `skills/llm-wiki/scripts/test_lint_wiki.py`:

```python
def test_broken_link_with_nested_brackets_in_text_is_error(tmp_path):
  '''A link whose TEXT contains brackets must still have its TARGET checked.

  The pre-fix MD_LINK_RE required no ']' inside the link text, so this whole
  link was invisible and its dangling target went unreported.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [the [above] discussion](none.md).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert any(
    level == 'ERROR' and 'broken relative link: none.md' in msg
    for level, _, msg in findings), findings


def test_link_with_nested_brackets_resolves_and_counts_as_inbound(tmp_path):
  '''The same shape, pointing at a real page: no error, and the target is
  no longer an orphan. Pins that the widened regex still captures the TARGET
  (group 1), not the bracketed text.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [the [above] discussion](../sources/a.md).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings if f[0] == 'ERROR'], findings
  assert not [f for f in findings
              if f[0] == 'WARN' and f[1] == 'wiki/sources/a.md'], findings
```

- [ ] **Step 2: Run the tests and watch them fail**

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k nested_brackets
```

Expected: **2 failed**. The first fails its `assert any(...)` because no ERROR is produced at all (the link is invisible). The second fails on the orphan `WARN` for `wiki/sources/a.md`, because the link that would have referenced it was never seen.

If either fails for any other reason — an import error, a `write_page` signature mismatch, a fixture typo — stop and fix the test before going on. A test that fails for the wrong reason proves nothing.

- [ ] **Step 3: Widen the pattern to one level of balanced nesting**

In `skills/llm-wiki/scripts/lint_wiki.py`, replace line 13–14:

```python
# Markdown relative links: [text](target) where target is not a URL/anchor.
MD_LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
```

with:

```python
# Markdown relative links: [text](target) where target is not a URL/anchor.
# The text alternation allows ONE level of balanced nested brackets, so
# `[the [above] discussion](x.md)` is seen and its target checked; the flat
# `[^\]]*` form matched no part of it and let the target go unvalidated. The
# two alternatives are disjoint on their first character, so the repetition
# cannot backtrack ambiguously.
MD_LINK_RE = re.compile(r'\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(([^)]+)\)')
```

- [ ] **Step 4: Run the new tests, then the whole suite**

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k nested_brackets
```
Expected: **2 passed**.

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```
Expected: all green, **+2** on the directory baseline.

- [ ] **Step 5: Mutation-check the tests**

Temporarily restore the old flat pattern (`r'\[[^\]]*\]\(([^)]+)\)'`), re-run `-k nested_brackets`, and confirm **both** tests fail. Then put the new pattern back and re-run to green. A test that survives this revert is not pinning the fix.

- [ ] **Step 6: Commit**

```bash
git add skills/llm-wiki/scripts/lint_wiki.py skills/llm-wiki/scripts/test_lint_wiki.py
git commit -m "fix(llm-wiki): see links whose text contains nested brackets"
```

---

### Task 2: a CommonMark link title is swallowed into the path

**Files:**
- Modify: `skills/llm-wiki/scripts/lint_wiki.py` — add `LINK_TITLE_RE` and `_link_target()` beside the other module regexes/helpers; call it in `check_links` and `_index_targets`
- Test: `skills/llm-wiki/scripts/test_lint_wiki.py`

**Interfaces:**
- Consumes: `MD_LINK_RE` from Task 1 (one capture group holding the raw parenthesised destination).
- Produces: `_link_target(dest: str) -> str` — strips a trailing CommonMark title from a raw link destination and trims whitespace. Task 4 calls `check_links` after this normalisation is already in place; it does not call `_link_target` itself.

**The requirement (deferred item, verbatim):**

> `MD_LINK_RE` / `INDEX_LINE_RE` capture a CommonMark link *title* attribute (`[a](x.md "Title")`) as part of the path, breaking resolution/parity if titles are used.

**Both regexes capture everything inside the parens**, so `[a](x.md "Title")` yields the destination `x.md "Title"`. In `check_links` that is treated as a path and reported as a broken link; in `_index_targets` it becomes an index target that matches no page, so `check_index_parity` reports both a missing page **and** an unindexed page for the same file. The fix is one shared helper, called at both sites — the same DRY shape as the `_real_dates` extraction in `distill_sessions.py`.

- [ ] **Step 1: Write the failing tests**

Append to `test_lint_wiki.py`:

```python
def test_link_title_is_not_part_of_the_path(tmp_path):
  '''[a](x.md "Title") points at x.md. The title is display metadata.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [A](../sources/a.md "The A page").')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings if f[0] == 'ERROR'], findings
  assert not [f for f in findings
              if f[0] == 'WARN' and f[1] == 'wiki/sources/a.md'], findings


def test_link_title_does_not_hide_a_broken_target(tmp_path):
  '''Stripping the title must not stop the PATH being checked.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [gone](none.md "Not here").')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert any(
    level == 'ERROR' and 'broken relative link: none.md' in msg
    for level, _, msg in findings), findings


def test_index_line_title_is_not_part_of_the_target(tmp_path):
  '''An index line carrying a title must still reach parity with its page.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  (root / 'wiki/index.md').write_text(
    '# Wiki index\n\n## sources\n- [A](sources/a.md "The A page")\n')
  findings = lint_wiki.check_index_parity(root, lint_wiki.discover_pages(root))
  assert findings == [], findings


def test_link_target_helper_handles_both_quote_styles():
  '''Direct unit coverage of the helper: its contract is shared by two
  callers, so it is pinned on its own terms rather than only through them.'''
  assert lint_wiki._link_target('x.md') == 'x.md'
  assert lint_wiki._link_target('x.md "Title"') == 'x.md'
  assert lint_wiki._link_target("x.md 'Title'") == 'x.md'
  assert lint_wiki._link_target('x.md#frag "Title"') == 'x.md#frag'
  # No trailing quoted run: nothing is stripped.
  assert lint_wiki._link_target('a"b".md') == 'a"b".md'
```

- [ ] **Step 2: Run the tests and watch them fail**

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "title"
```

Expected: **4 failed**. The helper test fails with `AttributeError: module 'lint_wiki' has no attribute '_link_target'`; the other three fail on the swallowed title (a broken-link ERROR naming `../sources/a.md "The A page"`, an orphan WARN, and two index-parity ERRORs respectively).

- [ ] **Step 3: Add the helper**

In `lint_wiki.py`, immediately after the `MD_LINK_RE` definition, add:

```python
# A CommonMark link title trailing the destination: [a](x.md "Title"). Both
# link patterns capture everything inside the parens, so the title is stripped
# once, here, rather than complicating two regexes.
LINK_TITLE_RE = re.compile(r'''\s+(?:"[^"]*"|'[^']*')\s*$''')
```

and add this helper next to the other private helpers (immediately above `_index_targets` is a good home):

```python
def _link_target(dest):
  '''The path part of a link destination, without a CommonMark title.

  `[a](x.md "Title")` and the index line `- [A](sources/a.md "Title")` both
  name `x.md` / `sources/a.md`; the title is display metadata. Shared by
  check_links and _index_targets so body links and index lines cannot
  disagree about what a destination points at -- a divergence between those
  two code paths was the earlier #fragment bug.'''
  return LINK_TITLE_RE.sub('', dest).strip()
```

- [ ] **Step 4: Call it at both sites**

In `check_links`, the loop currently reads:

```python
    for target in MD_LINK_RE.findall(body):
      if target.startswith(('http://', 'https://', 'mailto:', '#')):
```

Change the first two lines to:

```python
    for raw_target in MD_LINK_RE.findall(body):
      target = _link_target(raw_target)
      if target.startswith(('http://', 'https://', 'mailto:', '#')):
```

The rest of the loop body is unchanged and keeps using `target`. Order matters: the title is stripped **before** the URL-scheme test and before the existing `target.split('#', 1)[0]` fragment strip, so `(https://x "T")` is still recognised as a URL and `(x.md#frag "T")` still resolves to `x.md`.

In `_index_targets`, change:

```python
      out.append(m.group(1).split('#', 1)[0])
```

to:

```python
      out.append(_link_target(m.group(1)).split('#', 1)[0])
```

- [ ] **Step 5: Run the new tests, then the whole suite**

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "title"
```
Expected: **4 passed**.

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```
Expected: all green, **+4** on the Task 1 total (three fixture tests plus the direct helper test). Confirm the arithmetic against your own run rather than trusting this line.

- [ ] **Step 6: Mutation-check both call sites separately**

Revert **only** the `check_links` call (back to `for target in MD_LINK_RE.findall(body):`), re-run, confirm the two body-link title tests fail while the index test still passes. Restore. Then revert **only** the `_index_targets` call, re-run, confirm the index test fails while the body-link tests pass. Restore and re-run to green.

Two call sites need two independent mutation checks — a single check could pass while one site was silently unwired.

- [ ] **Step 7: Commit**

```bash
git add skills/llm-wiki/scripts/lint_wiki.py skills/llm-wiki/scripts/test_lint_wiki.py
git commit -m "fix(llm-wiki): strip CommonMark link titles from link and index targets"
```

---

### Task 3: a page must not reference itself out of its own orphan warning

**Files:**
- Modify: `skills/llm-wiki/scripts/lint_wiki.py` — `check_links`
- Test: `skills/llm-wiki/scripts/test_lint_wiki.py` (append near `test_orphan_page_is_warning`, currently at line 184)

**Interfaces:**
- Consumes: `_link_target` from Task 2 (already wired into `check_links`).
- Produces: `_page_key(root, p) -> str` — a page's identity in the `referenced` set, i.e. its path relative to `wiki/`. `check_links(root, pages)` keeps its signature and its `(level, path, message)` tuple contract.

**The requirement (deferred item, first half, verbatim):**

> `check_links` counts a page's self-link as an inbound reference (silencing its own orphan warning) […]

**Scope decision, made deliberately — read this before implementing.** The item names the *body link* channel. `check_links` builds its `referenced` set from **three** channels, and all three carry the identical defect:

1. `cites:` frontmatter — `referenced.add(target + '.md')`
2. body markdown links — `referenced.add(str(resolved.relative_to(wiki_abs)))`
3. body citation locators — `referenced.add(f'sources/{token}.md')`

A page whose frontmatter cites itself, or a source page whose body carries its own slug as a locator, silences its orphan warning exactly as a self-link does. Fixing only the named channel would ship a guard with two open doors.

This repo has a recorded precedent for exactly this call: the `_ordered_by_time` fix in plan 26 "Landed at **both** sort sites — `reconstruct` (claude-code) carried the byte-identical defect the item did not name." Follow it. Close all three channels, and record the widening as a `> Deviation:` note under this task at completion, since it goes beyond the item's literal text.

- [ ] **Step 1: Write the failing tests**

```python
def test_self_link_does_not_silence_its_own_orphan_warning(tmp_path):
  '''A page linking to itself has no INBOUND reference -- it is still an
  orphan. Counting the self-link made the orphan check self-defeating.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'As noted [here](p.md), and see [A](../sources/a.md).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings if f[0] == 'ERROR'], findings
  assert any(
    level == 'WARN' and path == 'wiki/samplers/p.md' and 'orphan' in msg
    for level, path, msg in findings), findings


def test_self_cite_does_not_silence_its_own_orphan_warning(tmp_path):
  '''Same hole via the cites: frontmatter channel.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md',
    {'title': 'P', 'type': 'concept', 'cites': ['samplers/p', 'sources/a']})
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert any(
    level == 'WARN' and path == 'wiki/samplers/p.md' and 'orphan' in msg
    for level, path, msg in findings), findings


def test_self_locator_does_not_silence_its_own_orphan_warning(tmp_path):
  '''Same hole via the citation-locator channel: a source page carrying its
  own slug as a locator pointed the reference straight back at itself.'''
  root = make_wiki(tmp_path)
  write_page(
    root, 'sources/robnik-2022-mclmc.md', {'title': 'R', 'type': 'source'},
    'Restating [robnik-2022-mclmc §4] from the same page.')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings if f[0] == 'ERROR'], findings
  assert any(
    level == 'WARN' and path == 'wiki/sources/robnik-2022-mclmc.md'
    and 'orphan' in msg
    for level, path, msg in findings), findings


def test_inbound_reference_from_another_page_still_clears_the_orphan(tmp_path):
  '''The guard must not make every page an orphan: a genuine cross-page
  link still counts. This is the counter-test for the three above.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [A](../sources/a.md).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings
              if f[0] == 'WARN' and f[1] == 'wiki/sources/a.md'], findings
```

- [ ] **Step 2: Run the tests and watch them fail**

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "self_link or self_cite or self_locator or inbound_reference"
```

Expected: **3 failed, 1 passed**. The three self-reference tests fail because no orphan WARN is emitted; `test_inbound_reference_from_another_page_still_clears_the_orphan` passes already and exists to stay passing.

- [ ] **Step 3: Add the self-reference guard**

First give the key one definition. `check_links` already derives a page's `referenced`-set identity in its orphan loop (`relw = str(p.relative_to(root / 'wiki'))`), and the guard needs the same expression — two copies of one key rule is precisely the divergence that caused the earlier `_index_targets` / `check_links` fragment-stripping bug. Add above `check_links`:

```python
def _page_key(root, p):
  '''A page's identity in check_links' `referenced` set: its path relative to
  wiki/. One definition, shared by every producer and by the orphan consumer,
  so the two can never disagree about what names a page.'''
  return str(p.relative_to(root / 'wiki'))
```

Then, in `check_links`, compute the page's own key once at the top of the per-page loop. The loop currently opens:

```python
  for p in pages:
    rel = p.relative_to(root)
    text = p.read_text()
```

Change to:

```python
  for p in pages:
    rel = p.relative_to(root)
    # A page cannot reference itself into non-orphanhood. All three inbound
    # channels below (cites, links, locators) are filtered against this key:
    # the orphan check asks whether ANOTHER page points here.
    own = _page_key(root, p)
    text = p.read_text()
```

And change the orphan loop at the end of the function to use the same helper:

```python
  for p in pages:
    if _page_key(root, p) not in referenced:
      findings.append(('WARN', str(p.relative_to(root)), 'orphan: no inbound links'))
```

Then filter each of the three `referenced.add(...)` sites. The `cites` block becomes:

```python
    cites = fm.get('cites')
    if isinstance(cites, list):
      for target in cites:
        if target + '.md' != own:
          referenced.add(target + '.md')
```

The link block's `else` branch becomes:

```python
      else:
        try:
          key = str(resolved.relative_to(wiki_abs))
        except ValueError:
          continue
        if key != own:
          referenced.add(key)
```

And the locator block becomes:

```python
      if token in slugs:
        if f'sources/{token}.md' != own:
          referenced.add(f'sources/{token}.md')
      else:
```

Note the link block also replaces the old `try/except ValueError: pass` with an early `continue` — a target outside `wiki/` is not a page key and there is nothing further to do with it. Behaviour is unchanged for that case.

- [ ] **Step 4: Run the tests, then the whole suite**

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "self_link or self_cite or self_locator or inbound_reference"
```
Expected: **4 passed**.

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```
Expected: all green, **+4** on the Task 2 total.

Watch for a pre-existing test that asserted a self-referencing fixture was *not* an orphan. If one fails, do not weaken the new guard — read the old test, decide whether it encoded the bug, and if so update it and say so in your report.

- [ ] **Step 5: Mutation-check each channel independently**

Remove the `!= own` guard from one channel at a time, re-run, and confirm that exactly the matching test fails each time (`self_link` → link channel, `self_cite` → cites channel, `self_locator` → locator channel). Restore between checks. Three guards need three checks; one combined check would let a mis-wired channel through.

- [ ] **Step 6: Commit**

```bash
git add skills/llm-wiki/scripts/lint_wiki.py skills/llm-wiki/scripts/test_lint_wiki.py
git commit -m "fix(llm-wiki): a page's self-reference no longer clears its orphan warning"
```

---

### Task 4: link resolution must be case-sensitive on any filesystem

**Files:**
- Modify: `skills/llm-wiki/scripts/lint_wiki.py` — add `_real_paths()`; use it in `check_links` in place of `Path.exists()`
- Test: `skills/llm-wiki/scripts/test_lint_wiki.py`

**Interfaces:**
- Consumes: `check_links` as left by Task 3 (the `own` key and the three filtered channels).
- Produces: `_real_paths(root) -> set[Path]` — every real file under `root`, resolved, excluding anything under a dot-directory. Nothing later in this plan consumes it.

**The requirement (deferred item, second half, verbatim):**

> […] and on a case-insensitive FS (macOS/APFS) a broken relative link with wrong case (`../Sources/A.MD`) resolves via `.exists()` and escapes the broken-link check. Prefer membership in the discovered page set over `resolved.exists()`.

**Design decision, made deliberately.** The item says "the discovered page set", but `discover_pages()` returns only `wiki/*/*.md` content pages — it excludes the structural files (`index.md`, `log.md`, `open-questions.md`) and everything under `raw/`, `reports/` and `scripts/`. Testing membership in *that* set would report every legitimate link to a structural or raw file as broken. So the fix generalises the item's steer correctly: membership in the set of **all real files under the wiki root**. That is case-sensitive on every filesystem, because it compares strings the directory walk produced rather than asking the filesystem to match a name.

**Second, consequential decision:** a link pointing *outside* the wiki root currently passes via `exists()` and will now be reported as broken. That is a deliberate tightening, consistent with `schema-template.md`'s "relative links only" and with a wiki being self-contained. It is called out in Task 5's contract text.

- [ ] **Step 0: Sanity-check path-resolution symmetry before writing anything**

`_real_paths` compares `resolved` link targets against `{p.resolve() for p in root.rglob('*')}`. Both sides call `.resolve()`, so they should agree — but on macOS pytest's `tmp_path` lives under `/var/folders/…`, which is a symlink to `/private/var/folders/…`. If the two sides ever resolved asymmetrically, **every link test in the suite would go red at once** and you would waste a long time chasing a fixture artefact instead of a code bug. Prove the symmetry first, in a scratch dir outside the repo:

```bash
mkdir -p /tmp/lwcheck && cd /tmp/lwcheck && uv run --python 3.13 python -c "
from pathlib import Path
import tempfile
root = Path(tempfile.mkdtemp())   # honours \$TMPDIR, same as pytest's tmp_path
(root / 'wiki/samplers').mkdir(parents=True)
(root / 'wiki/index.md').write_text('x')
(root / 'wiki/samplers/p.md').write_text('x')
real = {p.resolve() for p in root.rglob('*') if p.is_file()}
target = ((root / 'wiki/samplers/p.md').parent / '../index.md').resolve()
print('root:      ', root)
print('resolved:  ', root.resolve())
print('symmetric: ', target in real)
"
```

The plan author ran this on 2026-09-08 and got:

```
root:       /var/folders/3m/…/T/tmpxiqwji64
resolved:   /private/var/folders/3m/…/T/tmpxiqwji64
symmetric:  True
```

Note the first two lines: the symlink is real, so the hazard is real — symmetry holds only because **both** sides call `.resolve()`. Keep it that way. If your run prints `symmetric: False`, stop and report; the membership approach would then need both sides normalised the same way (resolve the root once and build keys relative to it) before Task 4 can proceed.

- [ ] **Step 1: Write the failing tests**

The case test must not silently pass on a case-sensitive filesystem, where the old code was already correct. Gate it so it *proves* something wherever it runs — on a case-sensitive FS the wrong-case link is broken for the ordinary reason and the assertion still holds, so no skip is needed; the added `is_case_insensitive` assertion documents which regime you observed.

```python
def test_wrong_case_link_is_error_even_on_a_case_insensitive_fs(tmp_path):
  '''`.exists()` asks the filesystem, and APFS/macOS answers case-
  insensitively, so `../Sources/A.MD` resolved and escaped the check. Set
  membership compares names the directory walk produced, so the answer is the
  same on every filesystem.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [A](../Sources/A.MD).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert any(
    level == 'ERROR' and 'broken relative link: ../Sources/A.MD' in msg
    for level, _, msg in findings), findings


def test_links_to_structural_and_raw_files_still_resolve(tmp_path):
  '''The membership set is every real file under the root, NOT the page set:
  links to structural files and to raw/ are legal and must not become
  errors. This is the regression this task is most likely to cause.'''
  root = make_wiki(tmp_path)
  (root / 'raw/samplers/note.md').write_text('raw note\n')
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [the index](../index.md), [the log](../log.md) and '
    '[the raw note](../../raw/samplers/note.md).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings if f[0] == 'ERROR'], findings


def test_real_paths_excludes_dot_directories(tmp_path):
  '''A wiki root is a git repo; .git must not be walked into the set, and no
  legitimate link targets a dotfile.'''
  root = make_wiki(tmp_path)
  (root / '.git').mkdir(exist_ok=True)
  (root / '.git/config').write_text('[core]\n')
  paths = lint_wiki._real_paths(root)
  assert (root / 'wiki/index.md').resolve() in paths
  assert (root / '.git/config').resolve() not in paths
```

- [ ] **Step 2: Run the tests and watch them fail**

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "wrong_case or structural_and_raw or real_paths"
```

Expected on macOS/APFS: **2 failed, 1 passed** — `wrong_case` fails (no ERROR: `exists()` accepted `../Sources/A.MD`), `real_paths` fails with `AttributeError: module 'lint_wiki' has no attribute '_real_paths'`, and `structural_and_raw` passes already and exists to stay passing.

Confirm you are on a case-insensitive filesystem before trusting the first failure:

```bash
cd /tmp && rm -rf casetest && mkdir casetest && touch casetest/a.md && ls casetest/A.MD 2>/dev/null && echo CASE-INSENSITIVE || echo CASE-SENSITIVE
```

If that prints `CASE-SENSITIVE`, the `wrong_case` test will already pass — say so in your report, and rely on the mutation check in Step 5 for evidence instead.

- [ ] **Step 3: Add the helper**

Add above `check_links` in `lint_wiki.py`:

```python
def _real_paths(root):
  '''Every real file under root, resolved. Membership in this set replaces
  Path.exists() for link resolution: exists() consults the filesystem, and a
  case-insensitive one (macOS/APFS) accepts `../Sources/A.MD` for
  `sources/a.md`, so a genuinely wrong link passed the check on the author's
  machine and failed on a case-sensitive one. Comparing against names the
  directory walk produced gives the same answer everywhere.

  Dot-directories are skipped -- a wiki root is a git repo, and no legal link
  targets a dotfile. A link resolving outside root is absent from this set and
  is therefore an error, which matches SCHEMA.md's relative-links-only rule.'''
  return {
    p.resolve() for p in root.rglob('*')
    if p.is_file()
    and not any(part.startswith('.') for part in p.relative_to(root).parts)
  }
```

- [ ] **Step 4: Use it in `check_links`**

Build the set once, alongside the other per-run values at the top of `check_links`:

```python
def check_links(root, pages):
  findings = []
  slugs = _source_slugs(root)
  referenced = set()  # page paths (relative to wiki/) that something points at
  wiki_abs = (root / 'wiki').resolve()
  real = _real_paths(root)
```

Then replace the existence test. It currently reads:

```python
      resolved = (p.parent / target.split('#', 1)[0]).resolve()
      if not resolved.exists():
```

Change the condition to:

```python
      resolved = (p.parent / target.split('#', 1)[0]).resolve()
      if resolved not in real:
```

Nothing else in the loop changes.

- [ ] **Step 5: Run the tests, then the whole suite**

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "wrong_case or structural_and_raw or real_paths"
```
Expected: **3 passed**.

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```
Expected: all green, **+3** on the Task 3 total.

- [ ] **Step 6: Mutation-check**

Revert the condition to `if not resolved.exists():` and re-run `-k wrong_case`. On a case-insensitive filesystem it must fail. On a case-sensitive one it will still pass — in that case, prove the tripwire differently: keep the membership form and mutate `_real_paths` to lowercase every path, then confirm a correctly-cased link is newly reported. Restore, re-run to green.

- [ ] **Step 7: Commit**

```bash
git add skills/llm-wiki/scripts/lint_wiki.py skills/llm-wiki/scripts/test_lint_wiki.py
git commit -m "fix(llm-wiki): resolve links case-sensitively on every filesystem"
```

---

### Task 5: contract text and repo bookkeeping

**Files:**
- Modify: `skills/llm-wiki/scripts/schema-template.md` (`### Body conventions`, around line 47)
- Modify: `CLAUDE.md` (the `llm-wiki bundled wiki-script tests` command block)

**Interfaces:**
- Consumes: the finished behaviour of Tasks 1–4.
- Produces: nothing consumed by code.

Two of the four changes are author-visible and belong in the contract shipped to new wikis; the fourth changes a published test count.

- [ ] **Step 1: Add the two contract sentences**

In `skills/llm-wiki/scripts/schema-template.md`, the `### Body conventions` section opens:

> Prose-first; relative links only; no H1 (title lives in frontmatter).

Extend that opening paragraph with:

```markdown
Link paths are matched case-sensitively against real files and must resolve
inside the wiki root, on every filesystem — a link that only works because
macOS matches names case-insensitively is an error. A CommonMark link title
(`[a](x.md "Title")`) is display metadata and is not part of the path. A page
linking or citing itself does not count as an inbound reference, so it still
reports as an orphan.
```

**Do not bump `schema-version`.** The header comment at line 1 says to bump only "on a breaking contract change", and no *rule* changes here: the case rule enforces what "relative links only" always meant, link titles previously did not work at all, and a self-reference was never an inbound reference in intent.

**But be precise about what that means for existing wikis, and say so in your report.** These tasks do not invalidate content that was valid — they surface breakage that was already there and silently passing. Concretely: a wiki authored on macOS can contain a wrong-case link that lints clean today and will report an ERROR after Task 4, and a page that only self-links will start reporting an orphan WARN after Task 3. Expect the pilot wiki to need one cleanup pass on first lint after this lands. That is the fix working, not a regression — but the owner should hear it before running it, not discover it.

If you conclude after implementing that this really is a breaking contract change, raise it rather than bumping silently.

- [ ] **Step 2: Sync the test count in `CLAUDE.md`**

Find the `llm-wiki bundled wiki-script tests` block. It reads `252 tests`. Replace that number with the count your own final full-directory run reported, and leave the surrounding notes (`stdlib only`, the three `@needs_pilot` skips) untouched.

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q | tail -2
```

Use that output. Do not compute the number from this plan's per-task deltas — they are estimates, and your run is the fact.

- [ ] **Step 3: Run the two repo lints**

```bash
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py
```
Expected: both exit 0 with no output. `schema-template.md` is not a skill file, but `check_frontmatter.py` walks referenced paths in skill prose, so run it after any file under `skills/` changes.

- [ ] **Step 4: Full-suite confirmation**

```bash
cd /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```
Expected: all green, no failures, no errors.

- [ ] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/schema-template.md CLAUDE.md
git commit -m "docs(llm-wiki): record the link-resolution contract and sync test counts"
```

---

## Completion notes for the executor

Run the **Plan Completion Protocol** (writing-plans § Plan Completion Protocol) when Task 5 is committed and the final review is resolved. Specific to this plan:

- **Tick three items, not one.** In `specs/deferred_items.md` under `## 13-llm-wiki — 2026-07-22`, all three of these are implemented here and get `- [x] … → done in plan 28`:
  - the `D2 — nested brackets` item (Task 1),
  - the `MD_LINK_RE` / `INDEX_LINE_RE` link-title item (Task 2),
  - the `check_links` self-link / case-insensitive-FS item (Tasks 3 **and** 4 together — do not tick it until both have landed).

  Verify each box actually flipped from `- [ ]` to `- [x]`; a tick note anchored on an item's continuation lines appends the note and leaves the box open, which has happened before in this file. Check the open/closed counts before and after.
- **Expected backlog effect:** open 25 → 22, and the aged tail (>45 days) 6 → 3. Report `deferred_stats.py` in the completion batch either way.
- **Record the Task 3 widening** as a `> Deviation:` note: the item named the self-*link* channel and the implementation closed the `cites` and citation-locator channels too.
- **The deployed wiki copy is now stale.** `lint_wiki.py` is a `MANAGED_SCRIPTS` entry, so `~/research-wiki/scripts/lint_wiki.py` no longer matches the repo. Do **not** refresh it as part of this plan — it is owner-only, and the existing item under `## 26-distill-sessions-hardening` already tracks the refresh. Add `lint_wiki.py` to that item's scope in the completion pass so one `bootstrap_wiki.py --force` discharges both.
