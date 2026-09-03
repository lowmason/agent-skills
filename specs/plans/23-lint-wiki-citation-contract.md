# lint_wiki Citation-Detection Contract Implementation Plan

**Status: COMPLETE (2026-09-03)** — executed via executing-plans; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `lint_wiki.py` hard-error only on bracketed text that `SCHEMA.md` actually reserves as a citation — closing deferred items D1 (prose false positives), D3 (invisible citations, both directions), and the `_index_targets` fragment item.

**Architecture:** One regex currently both *recognizes* and *resolves* body citations, which is why its two failure directions cannot be fixed independently. Split it: `BODY_CITE_RE` captures the `(token, position)` shape, two small predicates decide whether the pair is a citation, and the existing `check_links` resolution logic is left alone behind that filter. Recognition is `position_ok ∧ (slug_shape_ok ∨ token ∈ known_source_slugs)` — the membership clause can never manufacture an error, so all error risk stays in the structural clause. Separately, `_index_targets` gains the `#fragment` strip that `check_links` already does. Finally the rule is written into the contract it enforces (`schema-template.md`, version 2 → 3) and rolled out to the live wiki, whose `scripts/` are independent **copies**, not symlinks.

**Tech Stack:** Python ≥ 3.12, stdlib only (`re`, `pathlib`). pytest via `uv run --python 3.13 --with pytest`.

## Global Constraints

- `lint_wiki.py` is **stdlib-only**, Python ≥ 3.12 (`llm-wiki-spec.md` §10). Add no imports.
- Style: **single quotes, two-space indentation**. Match the surrounding file exactly.
- The position vocabulary is **exactly** `§`, `p.`, `Table`, `Fig`, `Eq`, or a leading digit. Do **not** add `pp.`, `Ch`, or any other entry — that list is D1's recorded list, and widening it by invention is the exact error this spec exists to fix.
- Resolution stays **case-sensitive**: a miscased slug must be an ERROR, not a silent miss.
- The linter may only hard-error on what `SCHEMA.md` reserves. Any sigil the code accepts must be written into `schema-template.md` in the same change.
- **No new severity level.** The two "Accepted limitations" get no WARN.
- **No existing test may be deleted or weakened.** `test_body_citation_without_source_is_error` must stay green **unchanged**.
- Out of scope — leave for the separate `lint_wiki.py` mechanical-fixes plan: `MD_LINK_RE` nested-bracket handling, CommonMark title attributes in link targets, `DECISION_META_RE` leading whitespace, and `check_links`' self-link / case-insensitive-filesystem holes.
- Tests are **directory-scoped with bare imports**: always `cd skills/llm-wiki/scripts` first. A repo-root pytest run fails outright.

**Baseline (verified 2026-09-03):** `185 passed` in `skills/llm-wiki/scripts/`.

## Spec note — read before Task 3

`specs/lint-wiki-citation-contract.md` is internally inconsistent in one place. Its **Design §C** (narrowed by commit `1cd448f`) fixes the vocabulary at D1's list and explicitly verifies that `pp.` does **not** match and `Ch` is **not accepted**. Its **Contract changes §1** was not updated by that commit and still names `p.`/`pp.`, `Table(s)`, `Fig`/`Figure(s)`, `Eq`, `Ch`.

**§C governs.** Writing `pp.` and `Ch` into `SCHEMA.md` would document a rule the linter does not enforce — the D1 sin mirrored. Task 3 Step 6 corrects the stale sentence in the spec so the contradiction is not enshrined when the spec retires.

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `skills/llm-wiki/scripts/lint_wiki.py` | Modify (`:14-17`, `:90-102`, `:155-165`) | The linter. Gains `POSITION_RE`, `SLUG_SHAPE_RE`, `_looks_like_position`, `_is_citation`; `BODY_CITE_RE` gains a second capture group; `_index_targets` strips fragments. |
| `skills/llm-wiki/scripts/test_lint_wiki.py` | Modify (append) | Table-driven acceptance cases + per-predicate unit tests + two index-fragment tests. |
| `skills/llm-wiki/scripts/schema-template.md` | Modify (`:1`, `:47-54`) | The seeded contract. Version marker 2 → 3; § "Body conventions" gains the normative position vocabulary. |
| `skills/llm-wiki/scripts/test_bootstrap_wiki.py` | Modify (`:212`, append) | Pins the version bump and the seeded vocabulary text. |
| `specs/completed/llm-wiki-spec.md` | Modify (after `:177`) | §10 pointer to the amending spec. Table rows unchanged. |
| `specs/lint-wiki-citation-contract.md` | Modify (Contract changes §1) | Remove the stale wider vocabulary. |
| `~/research-wiki/` | Rollout only, no repo change | The live wiki's `scripts/` are copies; the fix does not reach the user's linter until `bootstrap_wiki.py --force` runs. |

Consumer audit (re-verified): `BODY_CITE_RE` has exactly one consumer (`check_links`, `lint_wiki.py:158`) and `INDEX_LINE_RE` exactly one (`_index_targets`, `:97`, itself read only by `check_index_parity`). The mention of "BODY_CITE_RE discipline" in `distill_specs.py:365` is a message string, not a use — do not touch it.

---

### Task 1: Split citation recognition from slug resolution

Closes D1 and D3.

**Files:**
- Modify: `skills/llm-wiki/scripts/lint_wiki.py:14-17` (regex block) and `:155-165` (`check_links` citation loop); insert two predicates above `check_links`
- Test: `skills/llm-wiki/scripts/test_lint_wiki.py` (append)

**Interfaces:**
- Consumes: existing module globals `MD_LINK_RE`, `_source_slugs(root)`, `_strip_frontmatter(text)`, and `check_links(root, pages) -> list[tuple]`.
- Produces:
  - `BODY_CITE_RE` — now **two** capture groups: `(token, position)`. `findall` yields tuples, not strings.
  - `POSITION_RE`, `SLUG_SHAPE_RE` — module-level compiled patterns.
  - `_looks_like_position(rest: str) -> bool`
  - `_is_citation(token: str, position: str, slugs: set[str]) -> bool`
  - `check_links` finding message format is **unchanged**: `f'citation: [{token} …] has no source page'`.

- [x] **Step 1: Write the failing tests**

> Deviation: `import pytest` went in its own group between the stdlib block and
> `import lint_wiki`, matching `test_distill_specs.py`, rather than literally after
> `import sys` — which would have split `from pathlib import Path` out of the stdlib
> group. Diff is 109 insertions, 0 deletions: no existing test was touched.

Append to `skills/llm-wiki/scripts/test_lint_wiki.py`. Also add `import pytest` to the import block at the top of the file (it currently imports only `subprocess`, `sys`, `pathlib.Path`, `lint_wiki`) — put it after `import sys`, separated from `import lint_wiki` by a blank line, matching the file's existing stdlib/local grouping.

```python
# --- citation recognition (spec: lint_wiki citation-detection contract) ---

# `ghost-2020-none` is deliberately absent: that absence is what makes case 3
# an error and pins test_body_citation_without_source_is_error.
CITE_SLUGS = ('robnik-2022-mclmc', 'hoffman-2014-nuts', 'mclmc')


def cite_fixture(root, body):
  '''Wiki with the three fixture source slugs plus one concept page carrying
  `body`. Returns (citation_errors, referenced) where `referenced` is the set
  of fixture slugs something pointed at -- i.e. those with no orphan WARN. The
  concept page cites nothing, so a slug lands in `referenced` only via a body
  locator, which is what makes the three verdicts distinguishable.'''
  for stem in CITE_SLUGS:
    valid_source(root, f'sources/{stem}.md', stem)
  write_page(root, 'samplers/notes.md',
             {'title': 'Notes', 'type': 'concept', 'status': 'unverified',
              'topics': '[samplers]', 'cites': '[]',
              'updated': '2026-07-22'},
             body=body)
  set_index(root,
            [f'- [{s}](sources/{s}.md) — s · 1 · verified · 2026-07-22'
             for s in CITE_SLUGS]
            + ['- [notes](samplers/notes.md) — s · 1 · unverified · 2026-07-22'])
  findings = lint_wiki.run_checks(root)
  errors = [f[2] for f in findings
            if f[0] == 'ERROR' and f[2].startswith('citation:')]
  orphaned = {f[1] for f in findings if f[0] == 'WARN' and 'orphan' in f[2]}
  referenced = {s for s in CITE_SLUGS
                if f'wiki/sources/{s}.md' not in orphaned}
  return errors, referenced


# The spec's acceptance table, verbatim. 'cite' = recognized and resolves,
# 'error' = recognized and unresolved, 'prose' = not a citation at all.
CITATION_CASES = [
  (1, '[robnik-2022-mclmc §4.2]', 'cite', 'robnik-2022-mclmc'),
  (2, '[hoffman-2014-nuts Table 2]', 'cite', 'hoffman-2014-nuts'),
  (3, '[ghost-2020-none §4.2]', 'error', 'ghost-2020-none'),
  (4, '[mclmc §4.2]', 'cite', 'mclmc'),
  (5, '[see below]', 'prose', None),
  (6, '[per the user]', 'prose', None),
  (7, '[todo fix this]', 'prose', None),
  (8, '[Figure 2]', 'prose', None),
  (9, '[NUTS §3]', 'prose', None),
  (10, '[see Table 2]', 'prose', None),
  (11, '[Hoffman2014 §3]', 'error', 'Hoffman2014'),
  (12, '[robnik_2022 §4]', 'error', 'robnik_2022'),
  (13, '[robnik.2022 §4]', 'error', 'robnik.2022'),
  (14, '[the [above] discussion](x.md)', 'prose', None),
  (15, '[robnik-2022-mclmc §4.2](x.md)', 'prose', None),
  (16, '### [d-01] Flat files primary', 'prose', None),
  (17, '## [2026-07-24] log entry', 'prose', None),
  (18, '[well-known Table 2]', 'error', 'well-known'),
]


@pytest.mark.parametrize('case,body,verdict,token', CITATION_CASES,
                         ids=[f'case{c}' for c, _, _, _ in CITATION_CASES])
def test_citation_recognition_table(tmp_path, case, body, verdict, token):
  errors, referenced = cite_fixture(make_wiki(tmp_path), body)
  if verdict == 'cite':
    assert errors == [], f'case {case}: unexpected citation error'
    assert token in referenced, f'case {case}: did not count as an inbound ref'
  elif verdict == 'error':
    assert any(token in e for e in errors), f'case {case}: no error for {token}'
    assert referenced == set(), f'case {case}: nothing should resolve'
  else:
    assert errors == [], f'case {case}: prose treated as a citation'
    assert referenced == set(), f'case {case}: prose counted as an inbound ref'


@pytest.mark.parametrize('position,expected', [
  ('§4.2', True),
  ('p. 12', True),
  ('Table 2', True),
  ('Tables 3', True),      # prefix match, free
  ('Fig 1', True),
  ('Figure 1', True),      # prefix match, free
  ('Figs 2-3', True),      # prefix match, free
  ('Eq 7', True),
  ('12', True),
  (' §4.2', True),         # leading whitespace is stripped
  ('below', False),
  ('the user', False),
  ('fix this', False),
  ('pp. 12', False),       # accepted narrowness: D1's list has p., not pp.
  ('Ch 4', False),         # accepted narrowness: D1's list has no Ch
  ('see Table 2', False),  # sigil must OPEN the position, not appear in it
])
def test_looks_like_position(position, expected):
  assert lint_wiki._looks_like_position(position) is expected


@pytest.mark.parametrize('token,position,expected', [
  ('robnik-2022-mclmc', '§4.2', True),       # shape: hyphen
  ('Hoffman2014', '§3', True),               # shape: 4-digit year
  ('mclmc', '§4.2', True),                   # membership only
  ('nope', '§4.2', False),                   # neither shape nor membership
  ('see', 'Table 2', False),                 # position ok, token is prose
  ('mclmc', 'see this', False),              # membership, bad position
  ('robnik-2022-mclmc', 'see this', False),  # shape, bad position (limitation 1)
])
def test_is_citation(token, position, expected):
  assert lint_wiki._is_citation(token, position, set(CITE_SLUGS)) is expected
```

- [x] **Step 2: Run the tests to verify they fail**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q test_lint_wiki.py
```

Expected: `31 failed, 48 passed` (verified 2026-09-03 against the unmodified linter).

- All 23 predicate tests error with `AttributeError: module 'lint_wiki' has no attribute '_looks_like_position'` / `'_is_citation'`.
- Table cases **5, 6, 7, 10, 14** fail on `prose treated as a citation` — bracketed prose hard-erroring is D1. Case 14 failing here is D2's citation-fabrication half (`the`, extracted from the link text of `[the [above] discussion](x.md)`); the implementation closes it for free, with no code aimed at it.
- Table cases **11, 12, 13** fail on `no error for …` — the citation is invisible today, in both directions. That is D3.
- Table cases **1, 2, 3, 4, 8, 9, 15, 16, 17, 18** already pass — they are the no-regression rows. Cases 4 and 18 pass by accident of the old rule (`mclmc` and `well-known` both satisfy the old lowercase-hyphen anchor); they must still pass after the change, for the new reasons.

- [x] **Step 3: Replace the regex block**

In `skills/llm-wiki/scripts/lint_wiki.py`, replace the two commented lines and `BODY_CITE_RE` (currently `:14-17`) with:

```python
# Structural shape of a body locator: [token position], and NOT a markdown
# link (no '(' immediately after the ']'). Shape only -- _is_citation decides
# whether a matched pair is actually a citation.
BODY_CITE_RE = re.compile(r'\[([A-Za-z0-9][A-Za-z0-9._-]*)\s+([^\]]+)\](?!\()')
# A position opens with a documented locator sigil, or a digit (SCHEMA.md
# "Body conventions"). These are prefix matches, so 'Table' also covers
# 'Tables' and 'Fig' covers 'Figure'/'Figs'; 'pp.' and 'Ch' are NOT accepted.
# Extend additively, against real content -- never speculatively: an
# unrecognized position silently makes the token prose, while a spurious one
# adds hard-ERROR surface.
POSITION_RE = re.compile(r'^(?:§|p\.|Table|Fig|Eq|\d)')
# A slug is multi-part: it carries a hyphen, or a 4-digit run (a year).
SLUG_SHAPE_RE = re.compile(r'-|\d{4}')
```

Leave `MD_LINK_RE` and its comment above this block untouched.

- [x] **Step 4: Add the two predicates**

Insert immediately after `_strip_frontmatter` and before `def check_links(root, pages):`:

```python
def _looks_like_position(rest):
  '''Is the text after the token a locator position?'''
  return bool(POSITION_RE.match(rest.strip()))


def _is_citation(token, position, slugs):
  '''Recognition, kept separate from resolution: a [token position] pair is a
  citation when the position looks like one AND the token either is shaped like
  a slug or names a known source page. The membership clause lets a single-word
  slug (`mclmc`) stay citable without loosening the structural clause, and it
  can never manufacture an error -- a token in `slugs` resolves by
  construction. All error risk therefore sits in the structural clause.'''
  if not _looks_like_position(position):
    return False
  return bool(SLUG_SHAPE_RE.search(token)) or token in slugs
```

- [x] **Step 5: Rewire the check_links citation loop**

In `check_links`, replace:

```python
    # body citation locators [slug §x] must map to a source page; and count
    # as an inbound reference to it
    for slug in BODY_CITE_RE.findall(body):
      if slug in slugs:
        referenced.add(f'sources/{slug}.md')
      else:
        findings.append(
          ('ERROR', str(rel), f'citation: [{slug} …] has no source page'))
```

with:

```python
    # body citation locators [slug §x] must map to a source page; and count
    # as an inbound reference to it. Bracketed prose is not a citation and is
    # neither validated nor counted.
    for token, position in BODY_CITE_RE.findall(body):
      if not _is_citation(token, position, slugs):
        continue
      if token in slugs:
        referenced.add(f'sources/{token}.md')
      else:
        findings.append(
          ('ERROR', str(rel), f'citation: [{token} …] has no source page'))
```

- [x] **Step 6: Run the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: `226 passed` (185 baseline + 41 new: 18 table + 16 position + 7 citation). A different total means a case was added or dropped — reconcile before continuing.

Confirm specifically that these pre-existing tests are still green and were **not** edited:
- `test_body_citation_without_source_is_error` — `[ghost-2020-none §4.2]`, hyphenated token, passes via the structural clause.
- `test_valid_pages_are_clean` — body `[a §1]`. Note for the reviewer: under the new rule this passes **only via the membership clause** (`a` is a source stem; it has no hyphen and no year). That is case 4's capability already under test — load-bearing, not incidental.

- [x] **Step 7: Commit**

```bash
git add skills/llm-wiki/scripts/lint_wiki.py skills/llm-wiki/scripts/test_lint_wiki.py
git commit -m "$(cat <<'MSG'
fix(llm-wiki): split citation recognition from slug resolution

BODY_CITE_RE both recognized and resolved body citations, so D1 (prose like
[see below] hard-erroring) and D3 ([Hoffman2014 §3] invisible in both
directions) could not be fixed independently — widening the charset for D3
reintroduced D1, because the lowercase anchor was doubling as the prose guard.

Recognition is now position_ok AND (slug_shape_ok OR token in source slugs).
The membership clause cannot manufacture an error (the token resolves by
construction), so all error risk stays in the structural clause. The position
vocabulary is exactly D1's recorded list; widening it by invention would be
the D1 error in a new place.

Closes deferred items D1 and D3 (plan 13). Verified against all 18 acceptance
cases from specs/lint-wiki-citation-contract.md.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 2: Strip `#fragment` from index-line targets

Closes the `_index_targets` fragment item.

**Files:**
- Modify: `skills/llm-wiki/scripts/lint_wiki.py:90-102` (`_index_targets`)
- Test: `skills/llm-wiki/scripts/test_lint_wiki.py` (append)

**Interfaces:**
- Consumes: `INDEX_LINE_RE` (unchanged), and `check_index_parity`, which reads `_index_targets` for all three parity checks.
- Produces: `_index_targets(root) -> list[str]` — same signature, targets now fragment-free. All three parity checks (missing-line, missing-page, duplicate) inherit the fix from this one site.

- [x] **Step 1: Write the failing tests**

Append to `skills/llm-wiki/scripts/test_lint_wiki.py`:

```python
def test_index_line_with_fragment_resolves(tmp_path):
  '''A deep-link index line is legal: SCHEMA.md reserves nothing that
  prohibits it, and check_links already strips fragments from body links.'''
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a')
  set_index(root,
            ['- [a](sources/a.md#background) — s · 1 · verified · 2026-07-22'])
  assert [f for f in lint_wiki.run_checks(root)
          if f[0] == 'ERROR' and 'index' in f[2].lower()] == []


def test_index_lines_differing_only_by_fragment_are_a_duplicate(tmp_path):
  '''Two lines pointing into the same page collapse to one target, so
  duplicate detection is fixed by the same strip.'''
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a')
  set_index(root,
            ['- [a](sources/a.md#background) — s · 1 · verified · 2026-07-22',
             '- [a](sources/a.md#method) — s · 1 · verified · 2026-07-22'])
  assert any(f[0] == 'ERROR' and 'duplicate' in f[2].lower()
             for f in lint_wiki.run_checks(root))
```

- [x] **Step 2: Run the tests to verify they fail**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k fragment
```

Expected: `2 failed`. The first collects two spurious errors — `index: line target missing page: sources/a.md#background` and `index: page has no index line`. The second reports no duplicate, because `sources/a.md#background` and `sources/a.md#method` are distinct strings today.

- [x] **Step 3: Strip the fragment**

In `_index_targets`, replace:

```python
  '''Set of index-line targets (paths relative to wiki/, e.g. sources/a.md).'''
```

with:

```python
  '''Set of index-line targets (paths relative to wiki/, e.g. sources/a.md).
  A #fragment is stripped, matching check_links: SCHEMA.md does not prohibit
  an index deep-link, and the divergence between the two code paths was the
  bug. Duplicate detection inherits this -- two lines into the same page
  collapse to one target.'''
```

and replace:

```python
    if m:
      out.append(m.group(1))
```

with:

```python
    if m:
      out.append(m.group(1).split('#', 1)[0])
```

- [x] **Step 4: Run the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: `228 passed`.

- [x] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/lint_wiki.py skills/llm-wiki/scripts/test_lint_wiki.py
git commit -m "$(cat <<'MSG'
fix(llm-wiki): strip #fragment from index-line targets

check_links strips a fragment from body links; _index_targets did not, so an
index deep-link (sources/a.md#background) produced two spurious errors — line
target missing page, and page has no index line. Erroring on something
SCHEMA.md never reserved is the same mistake as D1, one section later.

All three parity checks read this one site, so duplicate detection is fixed
at the same time: two lines differing only by fragment now correctly collapse
to one target and report as a duplicate.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 3: Write the rule into the contract it enforces

**Files:**
- Modify: `skills/llm-wiki/scripts/schema-template.md:1` (version marker) and `:47-54` (§ "Body conventions")
- Modify: `skills/llm-wiki/scripts/test_bootstrap_wiki.py:212` and append one test
- Modify: `specs/completed/llm-wiki-spec.md` (after the §10 table, `:177`)
- Modify: `specs/lint-wiki-citation-contract.md` (Contract changes §1)

**Interfaces:**
- Consumes: `bootstrap_wiki._schema_version(path) -> int | None`, `bootstrap_wiki.main(argv) -> int`, and the test module's existing `bw` alias and `BUNDLE` constant.
- Produces: bundle schema version `3`. `_install_schema` is seed-once and never overwrites an existing `SCHEMA.md`, so the bump changes no live root's contents — it only makes `--check` report `STALE` for a root still on 2.

- [x] **Step 1: Write the failing tests**

In `skills/llm-wiki/scripts/test_bootstrap_wiki.py`, change the assertion on line 212 inside `test_seeded_schema_contains_specs_harvest_contract`:

```python
  assert 'schema-version: 2' in schema
```

to:

```python
  assert 'schema-version: 3' in schema
```

Then append a new test at the end of the file:

```python
def test_seeded_schema_documents_locator_vocabulary(tmp_path):
  '''The linter may only hard-error on what SCHEMA.md reserves, so the
  citation rule must be stated in the contract a bootstrapped root inherits
  (spec: lint_wiki citation-detection contract).'''
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  schema = (root / 'SCHEMA.md').read_text()
  assert 'A position opens with' in schema
  assert 'is prose, not a citation' in schema
  assert 'four-digit year' in schema
```

- [x] **Step 2: Run the tests to verify they fail**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q test_bootstrap_wiki.py
```

Expected: `2 failed, 17 passed` — `test_seeded_schema_contains_specs_harvest_contract` (the template still says `schema-version: 2`) and `test_seeded_schema_documents_locator_vocabulary` (no vocabulary paragraph yet). Verified 2026-09-03 in this task's actual starting state, i.e. with Tasks 1 and 2 already applied to `lint_wiki.py` — these tests bootstrap a tmp root from the live bundle, so they run the modified linter through `_verify`, and it still exits 0 on an empty scaffold.

- [x] **Step 3: Bump the schema version marker**

In `skills/llm-wiki/scripts/schema-template.md`, line 1, change `schema-version: 2` to `schema-version: 3`. The line becomes:

```
<!-- schema-version: 3 (bump on a breaking contract change; `bootstrap_wiki.py --check` flags a root whose schema is behind the bundle) -->
```

- [x] **Step 4: Add the normative vocabulary to § "Body conventions"**

In `skills/llm-wiki/scripts/schema-template.md`, § "Body conventions" currently reads:

```markdown
### Body conventions

Prose-first; relative links only; no H1 (title lives in frontmatter). Every
quantitative or attributable claim carries an inline locator in square brackets
referencing a source-page slug plus a position: `[robnik-2022-mclmc §4.2]`,
`[hoffman-2014-nuts Table 2]`. Contradictory claims are recorded adjacently with
both locators and a one-line note, then logged to `open-questions.md`. Session
digest source pages structure their body as capture notes (below), not prose.
```

Insert one new paragraph between the `[hoffman-2014-nuts Table 2]` sentence's paragraph and the `## index` heading — i.e. leave the paragraph above untouched and add, after a blank line:

```markdown
A position opens with `§`, `p.`, `Table`, `Fig`, `Eq`, or a digit — `Table`
also covers `Tables`, and `Fig` covers `Figure`/`Figs`, while a page range is
written `p. 3-4` (not `pp.`). A bracketed token whose remainder does not open
that way is prose, not a citation, and is never checked as one: `[see below]`,
`[Figure 2]` and `[NUTS §3]` are ordinary text. A citation is recognized only
when the position matches *and* the token either is multi-part (carries a
hyphen or a four-digit year) or exactly names an existing source-page slug.
Extend the position list additively, against real content.
```

Do not add `pp.` or `Ch` to the accepted list — the linter rejects both (see Global Constraints).

- [x] **Step 5: Add the §10 pointer to the retired spec**

In `specs/completed/llm-wiki-spec.md`, immediately after the §10 severity table's last row (`| Page count > 120 or source count > 100 (soft ceiling — revisit qmd) | info |`) and before the blank line preceding `## 11. Scale policy`, add:

```markdown

> Amended 2026-09-03 by `specs/lint-wiki-citation-contract.md`: the severities
> above are unchanged, but *what counts as a body citation* is now the
> recognition rule in that spec (position vocabulary + slug shape or
> membership), not any bracketed token. Index-line targets may carry a
> `#fragment`.
```

Use the backticked path, **not** a markdown link — a relative link would break when either spec moves directory at retirement.

- [x] **Step 6: Fix the spec's stale vocabulary sentence**

In `specs/lint-wiki-citation-contract.md`, § "Contract changes", item 1 currently reads:

```markdown
1. **`skills/llm-wiki/scripts/schema-template.md`** — § "Body conventions"
   gains the normative locator-position vocabulary (`§`, `p.`/`pp.`,
   `Table(s)`, `Fig`/`Figure(s)`, `Eq`, `Ch`, or a leading digit) and states
   that a bracketed token failing the rule is prose, not a citation. Bump
   `<!-- schema-version: 2 -->` to `3`.
```

Replace it with:

```markdown
1. **`skills/llm-wiki/scripts/schema-template.md`** — § "Body conventions"
   gains the normative locator-position vocabulary (`§`, `p.`, `Table`, `Fig`,
   `Eq`, or a leading digit — D1's recorded list, per Design §C; the prefix
   match makes `Tables`/`Figure`/`Figs` free, while `pp.` and `Ch` are not
   accepted) and states that a bracketed token failing the rule is prose, not
   a citation. Bump `<!-- schema-version: 2 -->` to `3`.
```

This sentence predates commit `1cd448f`, which narrowed Design §C to D1's list; leaving it would enshrine a contradiction when the spec retires.

- [x] **Step 7: Run the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: `229 passed`.

- [x] **Step 8: Run the repo frontmatter and provenance lints**

> Deviation: run this from the repo root explicitly — Step 7 leaves the shell in
> `skills/llm-wiki/scripts`, and the bare `build/…` paths below resolve against that
> cwd. Prefix the command with `cd /Users/lowell/Projects/agent-skills &&`. Both lints
> exit 0.

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py
```

Expected: both exit 0 with no findings. (Run from the repo root, not the scripts dir.)

- [x] **Step 9: Commit**

```bash
git add skills/llm-wiki/scripts/schema-template.md skills/llm-wiki/scripts/test_bootstrap_wiki.py specs/completed/llm-wiki-spec.md specs/lint-wiki-citation-contract.md
git commit -m "$(cat <<'MSG'
docs(llm-wiki): make the locator-position vocabulary normative (schema v3)

The linter must only hard-error on what SCHEMA.md reserves, so the recognition
rule has to be written into the contract rather than living only in the code.
§ "Body conventions" now states the position vocabulary (§, p., Table, Fig,
Eq, leading digit), that a bracketed token failing the rule is prose, and the
shape-or-membership condition on the token.

schema-version 2 -> 3: content that lints clean today can become an ERROR
tomorrow, and the contract text itself changed. _install_schema is seed-once,
so this touches no live root's SCHEMA.md — it makes --check report STALE for
a root still on 2, which is the signal the user migrates by hand.

Also corrects Contract changes §1 of the amending spec, which still carried
the wider vocabulary (pp., Ch, Table(s), Figure(s)) that commit 1cd448f
narrowed out of Design §C.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
MSG
)"
```

---

### Task 4: Roll the fix out to the live wiki

`~/research-wiki/scripts/` holds independent **copies** of the three runtime scripts, not symlinks. A fix landing only in `skills/llm-wiki/scripts/` does not reach the linter the user actually runs — this drift has already happened once (`distill_sessions.py` was stale from 2026-09-02 to 2026-09-03).

**Files:**
- Modify: `~/research-wiki/scripts/lint_wiki.py` (via `bootstrap_wiki.py --force`; outside the repo, nothing to commit)
- Do **not** touch: `~/research-wiki/SCHEMA.md`

**Interfaces:**
- Consumes: `bootstrap_wiki.py --force` (copies `MANAGED_SCRIPTS = ('lint_wiki.py', 'distill_sessions.py', 'distill_specs.py')`, then runs `_verify`, which executes the newly installed linter against the root and fails the run on a nonzero exit) and `--check` (read-only drift report).
- Produces: a live wiki running the new linter, and a `STALE SCHEMA.md` signal for the user to migrate by hand.

- [x] **Step 1: Pre-flight — run the new bundle linter against the live wiki**

This is exactly what `_verify` will execute after the copy, so run it first: a failure here is diagnosable, a failure inside `--force` is not.

```bash
python3 skills/llm-wiki/scripts/lint_wiki.py ~/research-wiki; echo "exit=$?"
```

Expected — unchanged from the pre-change baseline recorded 2026-09-03:

```
WARN  wiki/sources/2026-07-24-bls-stats-specs-harvest.md  orphan: no inbound links
0 errors, 1 warnings, 0 info
exit=0
```

The live wiki has zero content matching the new recognition rule (verified: every bracketed token there is a capture id with no internal space), so the new linter sees exactly what the old one saw. **If this prints any ERROR, stop and report** — do not run `--force`; `_verify` would fail and the cause needs a decision, not a retry. Warnings do not fail `_verify`, which does not pass `--strict`.

- [x] **Step 2: Install the updated scripts**

```bash
python3 skills/llm-wiki/scripts/bootstrap_wiki.py ~/research-wiki --force
```

Expected: an `$LLM_WIKI_ROOT` note and a Python-3.9 WARN from the system `python3` (both advisory and pre-existing — `bootstrap_wiki.py` only copies and compares), then `exists` lines for the scaffold, then these four action lines (verified 2026-09-03 via `--force --dry-run` against the post-Task-3 bundle):

```
  STALE   SCHEMA.md  (contract is behind the bundle; reconcile by hand against the template)
  update  scripts/lint_wiki.py
  same    scripts/distill_sessions.py
  same    scripts/distill_specs.py
```

followed by the `next steps` footer and the `_verify` lint output from Step 1. Exit 0.

`same` for the two distillers is correct — this plan does not touch them.

`SCHEMA.md` is **seed-once and never overwritten, even with `--force`** — that is the intended behavior, not a bug to work around.

- [x] **Step 3: Confirm the drift state**

```bash
python3 skills/llm-wiki/scripts/bootstrap_wiki.py ~/research-wiki --check; echo "exit=$?"
```

Run this un-piped, exactly as written: through a pipe (`| tail`, `| grep`) `$?` reports the *pipe's* status, not the check's, and the exit code is the point of this step.

Expected: `STALE` on `SCHEMA.md` only, all three scripts `current`, and **exit 1**:

```
check: comparing installed tooling against the skill bundle
  STALE     SCHEMA.md  (contract v2 is behind bundle v3; reconcile by hand against the template)
  current   scripts/lint_wiki.py
  current   scripts/distill_sessions.py
  current   scripts/distill_specs.py
check: 1 item(s) missing or stale
exit=1
```

**Exit 1 is the expected, correct outcome** — `_run_check` counts STALE as drift, and the STALE signal *is* this task's deliverable. Do not "fix" it by editing `~/research-wiki/SCHEMA.md`: migrating the root contract is the user's hand edit, and seed-once is the design. If any `scripts/*.py` line reads `DIFFERS`, the copy did not land — investigate before reporting done.

- [x] **Step 4: Report, no commit**

Nothing under the repo changed in this task, so there is no commit. Paste the verbatim output of Steps 1–3 into the task report, and state explicitly that `~/research-wiki/SCHEMA.md` was left on v2 for the user to migrate.

---

## Plan completion notes

For the Plan Completion Protocol (writing-plans § Plan Completion Protocol), when every task is done:

- **Tick in `specs/deferred_items.md`, § `## 13-llm-wiki — 2026-07-22`:** the **D1** item, the **D3** item, and the `_index_targets` fragment item under "Downgraded-to-minor" — each `- [x] … → done in plan 23`.
- **Amend, do not tick, the D2 item.** Its citation-fabrication half is closed for free by this design (acceptance case 14 — `[the [above] discussion](x.md)` is prose). D2 shrinks to its `MD_LINK_RE` nesting half alone, which remains open for the mechanical-fixes plan. Note that reduction on the item rather than ticking it.
- **Deferred by this plan:** the two "Accepted limitations" from the spec — a well-formed slug with a malformed position is silently unrecognized (`[robnik-2022-mclmc see this]`), and hyphenated or year-bearing prose whose remainder opens with a sigil hard-errors (`[well-known Table 2]`). Both are deliberate design consequences, not oversights; record them as such if the gate defers them, and note that the fix in each case is a new WARN severity, which this design explicitly declined as YAGNI.
- **Live-wiki `SCHEMA.md` migration** is the user's hand edit, tracked by the `STALE` signal — not a deferred code item.
- **Retirement:** `specs/lint-wiki-citation-contract.md` has no other live plan implementing it, so it retires to `specs/completed/` in the same commit as this plan's move to `specs/plans/completed/`. The §10 pointer added in Task 3 Step 5 is a backticked path, not a link, so no relative-link re-pointing is needed for it.
