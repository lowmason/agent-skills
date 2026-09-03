# lint_wiki citation-detection contract

**Status: APPROVED (2026-09-03), not yet implemented.** Next skill: `writing-plans`.

Amends `specs/completed/llm-wiki-spec.md` §10 (the `scripts/lint_wiki.py`
contract) and § "Body conventions" of the wiki `SCHEMA.md`. Source: the three
regex-strictness design calls deferred from plan 13
(`specs/deferred_items.md`, `## 13-llm-wiki — 2026-07-22`): **D1**, **D3**, and
the `_index_targets` fragment item.

## Problem

`BODY_CITE_RE` does two jobs at once and gets both wrong at the edges:

```python
BODY_CITE_RE = re.compile(r'\[([a-z0-9][a-z0-9-]*)\s+[^\]]+\](?!\()')
```

In `check_links` each match is (a) **validated** — an unknown slug is a hard
ERROR — and (b) **counted** as an inbound reference for orphan detection.

- **D1 — false positives.** The position is `[^\]]+`, which matches anything.
  Ordinary prose (`[see below]`, `[per the user]`, `[todo …]`) is read as a
  citation and hard-errors. The linter errors on something `SCHEMA.md` never
  reserved.
- **D3 — false negatives, in both directions.** The `[a-z0-9]` anchor makes
  `[Hoffman2014 §3]`, `[robnik_2022 §4]` and `[robnik.2022 §4]` invisible: the
  broken citation is not flagged, *and* the source page it points at can be
  falsely reported an orphan. Widening the charset naively re-introduces D1,
  because the same anchor is doubling as the prose guard.
- **Fragment item.** `check_links` strips `#fragment` from body links
  (`target.split('#', 1)[0]`); `_index_targets` does not. An index deep-link
  `sources/a.md#background` therefore yields two spurious errors — *line target
  missing page* and *page has no index line*.

The premise recorded in D1 — "`SCHEMA.md` does not reserve brackets for
locators" — is right about brackets but understates the contract. `SCHEMA.md`
§ "Body conventions" documents the locator as **slug plus a position**
(`[robnik-2022-mclmc §4.2]`, `[hoffman-2014-nuts Table 2]`). The discriminator
already exists in the contract; the regex simply does not use it.

## Scope

**In:** D1, D3, the index-fragment decision, and the `SCHEMA.md` wording that
makes the position vocabulary normative.

**Out — stays in the `lint_wiki.py` mechanical-fixes plan:** `MD_LINK_RE`
nested-bracket handling, the CommonMark title attribute captured as part of a
path, `DECISION_META_RE` leading-whitespace tolerance, and `check_links`'
self-link and case-insensitive-filesystem holes.

**Falls out for free.** D2 has two halves. Its *citation-fabrication* half —
`[the [above] discussion](x.md)` yielding a bogus `the` citation — is closed by
this design with no code aimed at it (verified: case 14 below). D2 therefore
shrinks to its `MD_LINK_RE` nesting half alone, and the mechanical plan should
be written against that reduced item.

## Governing principle

**The linter may only hard-error on what `SCHEMA.md` actually reserves.** D1 is
a violation of this rule; it also decides the fragment question, since
`SCHEMA.md` says nothing prohibiting a fragment in an index line.

## Design

### A. Split recognition from resolution

One regex doing both jobs is why D3's two failure directions are inseparable.
Replace it with three named units plus unchanged resolution:

| unit | question | output |
|---|---|---|
| `BODY_CITE_RE` | is this pair *shaped* like a locator? | `(token, position)` |
| `_looks_like_position(rest)` | is the position a position? | bool |
| `_is_citation(token, position, slugs)` | is this a citation? | bool |
| `check_links` (unchanged) | does the slug name a page? | ERROR / inbound ref |

Resolution stays **case-sensitive**, so a miscased slug is an error rather than
a silent miss — that is the point of D3.

### B. Recognition is a union of two recognizers

```
citation ⟺ position_ok ∧ ( slug_shape_ok ∨ token ∈ known_source_slugs )
```

Each clause serves one of the two jobs `BODY_CITE_RE` was already doing:

| recognizer | job it serves | failure mode if it over-matches |
|---|---|---|
| **structural** (shape ∧ position) | makes **broken** citations visible | hard **ERROR** |
| **membership** (known slug ∧ position) | makes **valid** citations countable for orphan detection | **benign** — the token names a real page by construction, so it resolves; at worst it suppresses an orphan WARN |

That asymmetry is a deliberate safety property: the membership clause can never
manufacture an error, so all error risk stays concentrated in the structural
clause.

Recognition takes the source-slug set as a parameter. This couples recognition
to wiki contents on purpose — it lets the wiki define what counts as a citable
name, which is more precise than any charset heuristic, and it removes what
would otherwise be a naming constraint on source pages (a single-word slug such
as `mclmc` stays citable).

### C. The predicates

```python
# Structural shape of a locator: [token position], not a markdown link.
BODY_CITE_RE = re.compile(r'\[([A-Za-z0-9][A-Za-z0-9._-]*)\s+([^\]]+)\](?!\()')
# A position opens with a documented locator sigil, or a digit.
POSITION_RE = re.compile(r'^(?:§|pp?\.|Tables?|Fig(?:ure)?s?|Eq|Ch|\d)')
# A slug is multi-part: a hyphen, or a 4-digit run (a year).
SLUG_SHAPE_RE = re.compile(r'-|\d{4}')
```

```python
def _looks_like_position(rest):
  return bool(POSITION_RE.match(rest.strip()))


def _is_citation(token, position, slugs):
  if not _looks_like_position(position):
    return False
  return bool(SLUG_SHAPE_RE.search(token)) or token in slugs
```

The slug charset widens to `[A-Za-z0-9._-]`. That is safe only because the
conjunction, not the charset, now does the discriminating.

`BODY_CITE_RE` now carries **two** capture groups, so `check_links`' loop
changes shape from `for slug in BODY_CITE_RE.findall(body)` to iterating
`(token, position)` pairs and filtering through `_is_citation`. Only tokens
that pass are validated or counted as inbound references.

`lint_wiki.py` is stdlib-only, Python ≥ 3.12, **single quotes, two-space
indentation** (`llm-wiki-spec.md` §10). Match it.

### D. Index-line fragments are legal and stripped

Strip the fragment in `_index_targets`, matching `check_links`. One site: all
three parity checks (missing-line, missing-page, duplicate) read from it, so
duplicate detection is fixed at the same time — two lines pointing at
`a.md#x` and `a.md#y` collapse to the same target and correctly report as a
duplicate.

No WARN. A third severity state for a case with zero instances in a one-page
wiki is unwarranted; add it later if real content produces the slip.

## Acceptance criteria

Every case below is verified against the proposed rule. Cases 1–3 are current
behavior that must not regress; 4 is new capability; 5–10 and 14–17 must be
silent; 11–13 are D3's invisible citations becoming errors; 18 is a known,
accepted false positive.

Fixture slug set: `{robnik-2022-mclmc, hoffman-2014-nuts, mclmc}` — note
`ghost-2020-none` is deliberately **absent**, which is what makes case 3 an
error and pins the existing test.

| # | body text | verdict |
|---|---|---|
| 1 | `[robnik-2022-mclmc §4.2]` | citation → resolves |
| 2 | `[hoffman-2014-nuts Table 2]` | citation → resolves |
| 3 | `[ghost-2020-none §4.2]` | citation → **ERROR**, via the structural clause (pins the existing test) |
| 4 | `[mclmc §4.2]` | citation → resolves (single-word slug, via membership) |
| 5 | `[see below]` | prose |
| 6 | `[per the user]` | prose |
| 7 | `[todo fix this]` | prose |
| 8 | `[Figure 2]` | prose (D3 guard) |
| 9 | `[NUTS §3]` | prose (D3 guard) |
| 10 | `[see Table 2]` | prose |
| 11 | `[Hoffman2014 §3]` | citation → **ERROR** |
| 12 | `[robnik_2022 §4]` | citation → **ERROR** |
| 13 | `[robnik.2022 §4]` | citation → **ERROR** |
| 14 | `[the [above] discussion](x.md)` | prose (D2 fabrication closed) |
| 15 | `[robnik-2022-mclmc §4.2](x.md)` | prose (markdown link) |
| 16 | `### [d-01] Flat files primary` | prose (capture id) |
| 17 | `## [2026-07-24] log entry` | prose (log heading) |
| 18 | `[well-known Table 2]` | citation → ERROR (accepted false positive) |

Index-line parity: `- [a](sources/a.md#background)` resolves and produces no
finding; two index lines differing only by fragment report one duplicate error.

## Testing

Table-driven over the 18 cases, plus direct unit tests for
`_looks_like_position` and `_is_citation` (the separation D3 asked for is only
real if each predicate is testable alone). `test_body_citation_without_source_is_error`
must stay green unchanged.

Run from the script directory, per the repo convention:

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

The bundled wiki-script suite is 185 tests today; the count rises with the new
cases and no existing test may be deleted to make room.

## Contract changes

1. **`skills/llm-wiki/scripts/schema-template.md`** — § "Body conventions"
   gains the normative locator-position vocabulary (`§`, `p.`/`pp.`,
   `Table(s)`, `Fig`/`Figure(s)`, `Eq`, `Ch`, or a leading digit) and states
   that a bracketed token failing the rule is prose, not a citation. Bump
   `<!-- schema-version: 2 -->` to `3`.
2. **`specs/completed/llm-wiki-spec.md` §10** — the row *"Body citation slug
   with no matching source page | error"* keeps its severity; what changes is
   what counts as a body citation. Add a pointer to this spec rather than
   rewriting the retired spec's table.

## Rollout

`_install_schema` is **seed-once and never overwrites `SCHEMA.md`, even with
`--force`**, so the version bump does not touch the live wiki. It makes
`bootstrap_wiki.py --check` report **STALE** for a root behind the bundle; the
user migrates `SCHEMA.md` by hand.

**The scripts are copies, not symlinks.** `~/research-wiki/scripts/` holds
independent copies of the three runtime scripts. A fix landing only in
`skills/llm-wiki/scripts/` does not reach the wiki the user actually runs —
this exact drift occurred once already (the 2026-09-02 `/deferred` quick-fix
pass left `distill_sessions.py` stale until 2026-09-03). The plan must end with:

```bash
python3 skills/llm-wiki/scripts/bootstrap_wiki.py ~/research-wiki --force
python3 skills/llm-wiki/scripts/bootstrap_wiki.py ~/research-wiki --check   # expect: STALE on SCHEMA.md only
```

## Accepted limitations

1. **A well-formed slug with a malformed position is silently unrecognized** —
   `[robnik-2022-mclmc see this]`. The symmetric residual of requiring both
   predicates. Not built for; add a WARN if real content produces it.
2. **Prose whose first token is hyphenated or year-bearing and whose remainder
   opens with a position sigil hard-errors** — `[well-known Table 2]`.
   Contrived; the escape is to not bracket it.

Both are consequences of the structural clause, which is where the design
deliberately concentrates error risk.

## Decisions

| Decision | Rationale |
|---|---|
| Conjunction (shape ∧ position), not either alone | Each predicate alone leaks. Sigil-only errors on `[Figure 2]`, `[see Table 2]`, `[NUTS §3]`; shape-only leaves `[Hoffman2014 §3]` invisible, which is all of D3. |
| Union with a membership clause | Removes the naming constraint on single-word source slugs, and cannot manufacture an error. |
| Index fragments legal, not illegal | The divergence between the two code paths *is* the bug; and erroring on something `SCHEMA.md` never reserved would repeat D1 one section later in the same spec. |
| Resolution stays case-sensitive | A miscased slug must be an error, not a silent miss. |
| No WARN severity added | YAGNI: zero instances in a one-page wiki. |
