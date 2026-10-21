# design-architecture Recast Implementation Plan

**Status: COMPLETE (2026-10-21)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `design-architecture` stop presenting the retired `alt-nfp` trio as the present, move its five decision sketches into a reference with three new ones from other project families, and refresh the stale repo names in `hooks/README.md` and `develop-testing-strategy`.

**Architecture:** Text-only edits to two skills and one README. The "failing test" is a stale-name `git grep` (the item's Done when, made runnable): it lists every line naming a retired repo, and after the change the in-scope files keep such names only in dated history. `design-architecture`'s "Decision examples" section becomes a short pointer to a new `references/decision-examples.md`, which holds the five `alt-nfp` sketches under a dated heading plus three sketches drawn from the owner's public repos.

**Tech Stack:** Markdown. The repo's lints (`build/check_frontmatter.py`, `build/check_provenance.py`, `build/check_conformance.py`, `build/check_snippets.py`, the dependency-drift test) and the `design-architecture` suite.

**Spec:** none. The requirement is the deferred item that the Background quotes. Its Done when is the bar.

## Background

Labels used below, each expanded here once:
- **The item** is "Recast design-architecture's alt-nfp framing and refresh stale repo names" in `specs/deferred_items.md`, section `## audit-3-10-26 routing (...)`. It comes from finding **G13** of the repo audit of 2026-10-03 (`specs/completed/audit-3-10-26.md`): `design-architecture`'s motivation and examples are tied to the pre-split `alt-nfp` trio. Its text, in short: recast "Why this exists" as dated history; move the sketches to `references/decision-examples.md`; add sketches from outside BLS nowcasting (an ML or serving choice, a causal-design choice, a repo-tooling decision); refresh the repo names in `hooks/README.md:14-15` and `skills/develop-testing-strategy/SKILL.md:87` and `:232`. **Done when:** no present-tense claim names a retired repo, and the sketches span more than one project family.
- **The 2026-09 split.** `alt-nfp` became two repos, `alt-nfp-stats` (the data side, a uv workspace that includes the `bls-stats` package) and `alt-nfp-model` (the `nfp-model` inference layer). `alt_nfp` is archived, and so is the `bls-stats` repo, whose code now lives as the `bls-stats` package inside `alt-nfp-stats`.
- **Public and private.** `agent-skills` (this repo) is public. `alt-nfp-stats` and `alt-nfp-model` are private. `earnings-themes` and `ces-revisions` are public. Checked with `gh repo view` on 2026-10-21.

## Global Constraints

- **Where to execute.** Branch `claude/deferred-unblocked-3` in the worktree `/Users/lowell/Projects/agent-skills/.claude/worktrees/laughing-tu-951446`. Before Task 1, `test -f specs/plans/62-design-architecture-recast.md` must exit 0.
- **Run every command from the worktree root**, with the relative paths this plan gives. Never `cd`: a Bash `cd` persists and moves the session's working directory.
- **Keep `skills/design-architecture/SKILL.md`'s frontmatter (lines 1-21) byte-identical.** A description change would need trigger micro-tests (writing-skills). Check: `git show HEAD:skills/design-architecture/SKILL.md | sed -n 1,21p | diff - <(sed -n 1,21p skills/design-architecture/SKILL.md) && echo frontmatter-unchanged` prints `frontmatter-unchanged` (run it before committing, while `HEAD` is still the previous commit).
- **Do not edit the body of `skills/design-architecture/references/example-inference-engine-adr.md`** (everything from its first `---` line on). It is an Accepted ADR dated 2025-11-03, and the skill's own rule makes an Accepted ADR immutable. Only its framing intro above the `---` changes.
- **Privacy.** Repo names may appear (they already do). Take no new detail from the private `alt-nfp-stats` or `alt-nfp-model` beyond what this plan's Replace blocks state. The three new sketches come only from public sources: `earnings-themes` `docs/adr/0004-use-a-local-open-weight-model-for-the-extractors-live-test.md`, `ces-revisions` `specs/ces-revisions.md` (Req 13 and Req 19), and this repo's `specs/completed/agent-skills-portability-spec.md` ("Decisions and alternatives", items 1 and 2).
- **Provenance.** `design-architecture` and `develop-testing-strategy` are Lowell's originals (`NOTICE`, the originals list). The new sketches summarize the owner's own repos. No `NOTICE` or license change.
- **Prose.** `hooks/README.md` edits follow `rules/write-with-asd-ste100.md` (plain technical English). `SKILL.md` and `references/` text is agent-facing and keeps the skill's existing style. Change only the text this plan's Replace blocks name.
- **Out of scope** (each still names an old repo, and each stays): `tech-debt`'s `alt_nfp` examples, its description included; the `llm-wiki` test fixtures and docstring; the dated comment in `skills/tech-debt/scripts/scan.sh`; the illustrative import in `skills/develop-testing-strategy/references/scraper-tests.md`; `classification-codes`' mentions of `bls-stats`, which stay true because the package lives on in `alt-nfp-stats`.
- **Leave `specs/deferred_items.md` alone.** The plan completion protocol ticks the item.
- **Every commit passes the nine commit lints** (`build/githooks/pre-commit` runs `build/run_commit_lints.sh`). A lint failure stops the commit: fix the cause, then commit again.
- **Commit trailer:** `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` as a second `-m`. Subagent-authored commits keep that same line. Check it with `git log -1 --format=%B`.
- **No push and no PR** without the owner's go-ahead.

## Decisions

- **D1** (owner, session, 2026-10-21): run this item now, in this session, on Opus ("Do the unblocked items ...", then "This session then"). Applied in: header.
- **D2** (owner, plan review, 2026-10-21): the seven defaults below, P1 to P7, the option "Approve all": log them as a decision and execute the plan with subagent-driven-development in this session. Applied in: Global Constraints (P1, P2, P5, P6), Task 1 (P1, P3, P7), Tasks 2 and 3 (P2, P4, P5).
- **D3** (owner, plan review, 2026-10-21): the final review's Codex seat runs `codex exec review` read-only with the per-run override `-c 'model="gpt-6-astra"'`, one retry if it fails, then the code-reviewer seat stands alone. The Codex config is not edited. Applied in: the final whole-branch review.

## Defaults for review

This plan settles these defaults. The owner approves or changes each at plan review, and an approved default becomes a Decision. D2 approved all seven as written.

- **P1. Scope.** The item's files, plus `hooks/README.md:42` (its `~/Projects/bls-stats` example path names the archived repo). The Global Constraints' out-of-scope list stays as is.
- **P2. The example ADR's body stays untouched.** Only its intro gains a dated note that names the split and says a real log would record it as a superseding ADR.
- **P3. The hooks README names `alt-nfp-stats`, `alt-nfp-model` and `naics-embedder`.** Each has a `pyproject.toml` with ruff (checked 2026-10-21). `alt-nfp-stats-runner` is left out: it is not on the owner's GitHub account.
- **P4. The three new sketches** are `earnings-themes` ADR 0004 (an ML or serving choice: which local open-weight model a live test runs), `ces-revisions` Req 13 (a causal-design choice: decline the causal claim and report an association) and this repo's portability spec, Decisions 1 and 2 (repo tooling: one canonical `skills/` tree).
- **P5. `alt-nfp-stats` is the live example** for `specs/adr/` (it holds `specs/adr/`) and in the template's blast-radius example, although the repo is private. Its name is already public in the skill.
- **P6. No pressure test or wording micro-test.** The description stays byte-identical, and the edits are facts and example content in a reference skill (`CLAUDE.md`: pure reference skills are not pressure-tested). The stale-name `git grep` is the failing test.
- **P7. `develop-testing-strategy:87` names no function from the private repo.** It says the `bls-stats` package tests "its period parser and reference dates".

---

## Planning record

> Deviation: three lines of this record (the split's description and the first two `alt-nfp-stats` facts) were reworded at the completion gate (owner, 2026-10-21) to say no more about the private repo than the shipped text does. The branch history was rewritten before any push, so no commit carries the earlier wording.

Facts measured on 2026-10-21 at `234d41b`:

- The stale-name check below found 51 matching lines across `skills`, `hooks`, `README.md` and `rules`. In the files this plan edits, it found `hooks/README.md:14`, `:15`, `:42`; `skills/design-architecture/SKILL.md:33`, `:82`, `:87`, `:110`, `:172`; `skills/develop-testing-strategy/SKILL.md:87`, `:232`; and 15 lines in the example ADR (intro line 4 and the dated body).
- `alt-nfp-stats` keeps its ADRs in `specs/adr/`, and its conftest blanks the store credentials for tests not marked `real_store`.
- The `bls-stats` package in `alt-nfp-stats` tests its period parser and reference-date rules.
- `alt-nfp-stats`, `alt-nfp-model` and `naics-embedder` each have a `pyproject.toml` that names ruff.

## The stale-name check

This command is the plan's test. Run it from the worktree root:

```bash
git grep -n -E 'alt_nfp|oi-indices|bls-stats-aggregation|alt-nfp([^-]|$)|~/Projects/bls-stats|_parse_ref_date|_last_business_day' -- hooks/README.md skills/design-architecture/SKILL.md skills/develop-testing-strategy/SKILL.md
```

The pattern `alt-nfp([^-]|$)` matches `alt-nfp` but not `alt-nfp-stats` or `alt-nfp-model`.

## File Structure

| File | Task | Change |
|---|---|---|
| `hooks/README.md` | 1 | Edit: the repo list (lines 14-15) and the example path (line 42) |
| `skills/develop-testing-strategy/SKILL.md` | 1 | Edit: lines 86-88 and 232 |
| `skills/design-architecture/SKILL.md` | 2, 3 | Edit: "Why this exists", "Where ADRs live", the template, "Decision examples", one anti-pattern (2); the pointer's list (3) |
| `skills/design-architecture/references/decision-examples.md` | 2, 3 | Create: the five `alt-nfp` sketches, dated (2); append three sketches (3) |
| `skills/design-architecture/references/example-inference-engine-adr.md` | 2 | Edit: the intro above the first `---` only |

Not touched: `skills/design-architecture/scripts/`, the frontmatter of either skill, `NOTICE`, `install.py`, `specs/deferred_items.md`.

---

### Task 1: Refresh the stale repo names outside design-architecture

**Files:**
- Modify: `hooks/README.md:14-15`, `hooks/README.md:42`
- Modify: `skills/develop-testing-strategy/SKILL.md:86-88`, `skills/develop-testing-strategy/SKILL.md:232`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing that a later task uses.

- [x] **Step 1: Run the stale-name check on this task's two files to see RED**

Run: `git grep -n -E 'alt_nfp|oi-indices|bls-stats-aggregation|alt-nfp([^-]|$)|~/Projects/bls-stats|_parse_ref_date|_last_business_day' -- hooks/README.md skills/develop-testing-strategy/SKILL.md`

Expected: exactly 5 lines: `hooks/README.md:14`, `hooks/README.md:15`, `hooks/README.md:42`, `skills/develop-testing-strategy/SKILL.md:87`, `skills/develop-testing-strategy/SKILL.md:232`.

- [x] **Step 2: Edit `hooks/README.md`**

Replace:

```markdown
Reusable Claude Code hook scripts for **your real Python/uv work repos** — `alt-nfp`,
`bls-stats`, `bls-stats-aggregation`, `naics-embedder` (each has a `pyproject.toml` +
ruff dev-dep). They convert advisory CLAUDE.md prose ("always run ruff", "use uv, not
```

with:

```markdown
Reusable Claude Code hook scripts for **your real Python/uv work repos** — `alt-nfp-stats`,
`alt-nfp-model`, `naics-embedder` (each has a `pyproject.toml` + ruff dev-dep). They
convert advisory CLAUDE.md prose ("always run ruff", "use uv, not
```

Then replace:

```markdown
From the target repo (e.g. `~/Projects/bls-stats`):
```

with:

```markdown
From the target repo (e.g. `~/Projects/alt-nfp-stats`):
```

- [x] **Step 3: Edit `skills/develop-testing-strategy/SKILL.md`**

Replace:

```markdown
- Test the small pure helpers directly — date parsers, period mappers, link extractors —
  exactly as `bls-stats` already does for `_parse_ref_date` and `_last_business_day`. These are
  the highest-value, cheapest tests in a scraper.
```

with:

```markdown
- Test the small pure helpers directly — date parsers, period mappers, link extractors —
  exactly as the `bls-stats` package (now inside `alt-nfp-stats`) does for its period parser
  and reference dates. These are the highest-value, cheapest tests in a scraper.
```

Then replace:

```markdown
  *unmarked* test that reaches the store should be blocked (the `alt-nfp` conftest blanks
```

with:

```markdown
  *unmarked* test that reaches the store should be blocked (the `alt-nfp-stats` conftest blanks
```

- [x] **Step 4: Run the check again to see GREEN**

Run the Step 1 command. Expected: no output (exit 1).

- [x] **Step 5: Run the lints**

Run: `uv run --python 3.13 --with pyyaml python build/check_conformance.py` — expected exit 0.
Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` — expected exit 0.
Run: `uv run --python 3.13 python build/check_snippets.py skills/develop-testing-strategy/` — expected exit 0.

- [x] **Step 6: Commit**

```bash
git add hooks/README.md skills/develop-testing-strategy/SKILL.md
git commit -m "docs: name the current repos in the hooks README and develop-testing-strategy" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Expected: the pre-commit lints pass and the commit lands.

---

### Task 2: Recast design-architecture's alt-nfp framing as dated history

**Files:**
- Modify: `skills/design-architecture/SKILL.md` (lines 32-36, 82, 87-88, 110, 164-211, 253-256)
- Create: `skills/design-architecture/references/decision-examples.md`
- Modify: `skills/design-architecture/references/example-inference-engine-adr.md` (lines 3-7 only)

**Interfaces:**
- Consumes: nothing.
- Produces, for Task 3: `references/decision-examples.md` ending with the `alt-nfp` group's fifth sketch, and a "Decision examples" pointer section in `SKILL.md` whose project list has one bullet, starting `- **NFP nowcasting**`.

- [x] **Step 1: Run the stale-name check on SKILL.md to see RED**

Run: `git grep -n -E 'alt_nfp|oi-indices|bls-stats-aggregation|alt-nfp([^-]|$)|~/Projects/bls-stats|_parse_ref_date|_last_business_day' -- skills/design-architecture/SKILL.md`

Expected: exactly 5 lines: `:33`, `:82`, `:87`, `:110`, `:172`.

- [x] **Step 2: Recast "Why this exists"**

In `skills/design-architecture/SKILL.md`, replace:

```markdown
This is a live cost in practice: the **same NFP-nowcasting problem is currently solved three
ways** — NumPyro/JAX in `alt-nfp`, and PyMC in both `alt_nfp` and `oi-indices` — with no
recorded rationale for the split. An agent reading any one repo cannot tell whether the other
engines are deliberate (parity cross-checks, GPU vs ergonomics) or accidental drift. An ADR
turns that fork from a mystery into a decision you can build on.
```

with:

```markdown
The cost is real, and this skill grew out of it. In late 2025 the **same NFP-nowcasting
problem was solved three ways**: NumPyro/JAX in `alt-nfp`, and PyMC in both `alt_nfp` and
`oi-indices`, with no recorded rationale for the split. An agent reading any one repo could not
tell whether the other engines were deliberate (parity cross-checks, GPU vs ergonomics) or
accidental drift. An ADR turns such a fork from a mystery into a decision you can build on.
(That trio is history: a 2026-09 split turned `alt-nfp` into `alt-nfp-stats` and
`alt-nfp-model` and archived `alt_nfp`. In a real decision log, the split is itself a
superseding ADR.)
```

- [x] **Step 3: Update "Where ADRs live" and the template's example**

Replace:

```markdown
stack the conventions are `specs/` (active design, e.g. `alt-nfp/specs/`) plus MkDocs + per-package
```

with:

```markdown
stack the conventions are `specs/` (active design, e.g. `alt-nfp-stats/specs/`) plus MkDocs + per-package
```

Replace:

```markdown
- **Use `specs/adr/` when the repo's design record already lives in `specs/`** (as `alt-nfp`
  does) — keep ADRs beside the specs and plans they formalize.
```

with:

```markdown
- **Use `specs/adr/` when the repo's design record already lives in `specs/`** (as
  `alt-nfp-stats` does) — keep ADRs beside the specs and plans they formalize.
```

Replace:

```markdown
- **Blast radius:** <packages/repos affected, e.g. nfp-model only | whole uv workspace | alt-nfp + oi-indices>
```

with:

```markdown
- **Blast radius:** <packages/repos affected, e.g. nfp-model only | whole uv workspace | alt-nfp-stats + alt-nfp-model>
```

- [x] **Step 4: Create `references/decision-examples.md` with the five dated sketches**

> Deviation: after the final review, the owner approved one correction to this block (completion gate, 2026-10-21): sketch 1 names `example-inference-engine-adr.md` instead of "the reference file", which pointed nowhere once the sketch moved out of `SKILL.md`.

Create `skills/design-architecture/references/decision-examples.md` with exactly this content. Sketches 1 to 5 are the current `SKILL.md` text (lines 171-211), moved unchanged except that sketch 1's "runs" becomes "ran".

```markdown
# Decision examples

Compact sketches of real decisions: the decision, the trade-off that actually drives it, and the
real alternatives. Each group is dated to the project state it describes. Use them as models for
a Decision or Alternatives section, and tune the pattern to the repo you are in. Do not copy a
decision you have not weighed.

## NFP nowcasting (the `alt-nfp` family, late 2025)

These five come from the `alt-nfp` project as it stood in late 2025, before a 2026-09 split
turned it into `alt-nfp-stats` and `alt-nfp-model`. They describe that state, not the current
repos.

**1. Inference engine: NumPyro/JAX over PyMC (the flagship).** The same nowcast ran three ways
across repos (NumPyro/JAX in `alt-nfp`; PyMC in `alt_nfp` and `oi-indices`). `alt-nfp` chose JAX
for `vmap`-batched fitting over the as-of grid, GPU as the speed lever, and float64 parity gates
against the frozen PyMC reference. Cost: a full rewrite, an ongoing parity-gate maintenance
burden, and a familiarity split across the three repos. Alternatives: stay on PyMC (ergonomics,
`nutpie`, team fluency — rejected for batching/GPU); Stan (fast but a second language and weaker
Python data interop); BlackJAX (same JAX upside, more boilerplate than NumPyro). Worked in full
in the reference file — this is the decision whose absence motivated the whole skill.

**2. Parquet store layout & dedup/vintage policy.** Decision: store **levels only**, partitioned
Hive-style by `(source, seasonally_adj)`, with `vintage_date` / `revision` tags; derive log-growth
at *read* time per cohort. Trade-off: read-time derivation costs CPU on every panel build, but
keeps the store small, append-friendly, and free of precomputed-growth staleness bugs.
Alternatives: store growth precomputed (rejected — every revision invalidates it, and the growth
convention is still an open scoring question); one flat file (rejected — no partition pruning,
forces full scans). Dedup: last-writer-wins on `(series_id, ref_date, vintage_date)`; never
mutate in place — rebuild to a scratch prefix and promote.

**3. Scraper resilience: retry policy + recorded fixtures.** Decision: bounded exponential backoff
with jitter on the BLS/FRED HTTP layer (`httpx`/`curl-cffi`), plus checked-in HTML/JSON **fixtures**
so parsers (`BeautifulSoup`/`lxml`) are tested offline and CI runs without network. Trade-off:
fixtures go stale when BLS changes page structure, so you need a refresh path — but the alternative
(live-network tests) is flaky and unrunnable in CI. Alternatives: retry-only, no fixtures (rejected
— can't test the parser, can't run in CI); full VCR-style cassettes (rejected — heavier than the
handful of pages warrant). Mark live tests `network` and exclude them in CI.

**4. As-of / vintage data model: two-layer censoring.** Decision: every backtest sees only what
was knowable on date D via **combined** filtering — `vintage_date ≤ D` *and* `ref_date < D` — then
rank-based revision selection per series. Trade-off: two filters plus a rank are more complex than
one date cut, but each single-filter shortcut leaks future information in a documented way.
Alternatives: `vintage_date`-only or `ref_date`-only (both rejected — settled empirically to leak).
This is a one-way door: get it wrong and every backtest number is silently optimistic. (The
per-program publication lags this censoring depends on are catalogued in `bls-data-context`.)

**5. Multi-package workspace boundaries.** Decision: a `uv` workspace of 5 packages with a
**one-directional import graph** — the data chain (`lookups → download → ingest → vintages`) and a
model package that imports **no `nfp_*`**, consuming a content-hashed `.npz` snapshot as the only
boundary. Trade-off: the artifact seam adds a serialize/hash step, but it makes "the model never
sees a `vintage_date`" a *structural* guarantee (test-enforced), lets the model develop offline
against fixtures, and runs identically on CPU/GPU. Alternative: one package with module discipline
(rejected — discipline isn't enforceable; imports drift).
```

Then compare the moved block with the original, before Step 5 removes it from `SKILL.md`:
`diff <(awk '/^\*\*1\. Inference engine/,/imports drift\)\.$/' skills/design-architecture/SKILL.md) <(awk '/^\*\*1\. Inference engine/,/imports drift\)\.$/' skills/design-architecture/references/decision-examples.md)`.
Expected: one changed line, sketch 1's first line (`runs` against `ran`).

- [x] **Step 5: Replace the "Decision examples" section with a pointer**

In `skills/design-architecture/SKILL.md`, replace everything from the line `## Decision examples (this stack)` through the last line of sketch 5 (`(rejected — discipline isn't enforceable; imports drift).`), keeping the blank line before `## Evaluating a proposal`, with:

```markdown
## Decision examples

Compact sketches of real decisions are in
[references/decision-examples.md](references/decision-examples.md): the decision, the trade-off
that actually drives it, and the real alternatives. Read them when you need a model for a
Decision or Alternatives section, or a check that your own sketch is honest. They come from
these projects:

- **NFP nowcasting** (the `alt-nfp` family, late 2025): the inference engine, the parquet store
  layout, scraper resilience, as-of censoring, and workspace boundaries.

The flagship inference-engine ADR is worked in full in
[references/example-inference-engine-adr.md](references/example-inference-engine-adr.md) and
doubles as a copy-paste starting point.
```

- [x] **Step 6: Date the "Solving one problem N ways" anti-pattern**

Replace:

```markdown
- **Solving one problem N ways with zero ADRs.** The motivating failure: NumPyro/JAX vs PyMC
  across three repos with no record. Multiple implementations are *fine* — as a deliberate,
  documented choice (e.g. PyMC as a parity reference). Undocumented, they read as drift and get
  "fixed" by someone unifying them and breaking a cross-check.
```

with:

```markdown
- **Solving one problem N ways with zero ADRs.** The failure that motivated this skill: in late
  2025, NumPyro/JAX vs PyMC across three repos with no record. Multiple implementations are
  *fine* — as a deliberate, documented choice (e.g. PyMC as a parity reference). Undocumented,
  they read as drift and get "fixed" by someone unifying them and breaking a cross-check.
```

- [x] **Step 7: Add the dated note to the example ADR's intro**

> Deviation: the expected check output was worded wrong. Default diff context runs past the `---` line, so the hunk does not end before it. The edit was right: `git diff -U0` shows one hunk (`@@ -3,5 +3,10 @@`), and the body from the first `---` line on is byte-identical.

In `skills/design-architecture/references/example-inference-engine-adr.md`, replace:

```markdown
This is a fully-filled ADR for the decision whose *absence* motivated this skill — the same NFP
nowcast solved three ways (NumPyro/JAX in `alt-nfp`, PyMC in `alt_nfp` and `oi-indices`). Read it
as the exemplar of what "good" looks like, and copy it as a starting point for a real ADR. It is
written as a snapshot dated to when the choice was made; the bracketed notes `[like this]` are
authoring guidance, not part of the record — delete them when you adapt it.
```

with:

```markdown
This is a fully-filled ADR for the decision whose *absence* motivated this skill — in late 2025
the same NFP nowcast was solved three ways (NumPyro/JAX in `alt-nfp`, PyMC in `alt_nfp` and
`oi-indices`). Read it as the exemplar of what "good" looks like, and copy it as a starting point
for a real ADR. It is written as a snapshot dated to when the choice was made; the bracketed notes
`[like this]` are authoring guidance, not part of the record — delete them when you adapt it.

The record below is dated 2025-11-03 and stays as written, because an Accepted ADR is immutable.
The repos it names have changed since: a 2026-09 split turned `alt-nfp` into `alt-nfp-stats` and
`alt-nfp-model` and archived `alt_nfp`. In a real decision log that change arrives as a
superseding ADR, not as an edit to this one.
```

Then run `git diff --stat skills/design-architecture/references/example-inference-engine-adr.md` and `git diff skills/design-architecture/references/example-inference-engine-adr.md | grep '^@@'`. Expected: one hunk, which starts at or before line 3 and ends before the first `---` line.

- [x] **Step 8: Run the check again to see GREEN**

Run the Step 1 command. Expected: exactly 5 lines, each in dated history. Four are in the second paragraph of `## Why this exists`: the line with `` `alt-nfp`, and PyMC in both `alt_nfp` and ``, the line starting `` `oi-indices`, with no recorded rationale ``, the line starting `(That trio is history`, and the line starting `` `alt-nfp-model` and archived `alt_nfp` ``. The fifth is the pointer's bullet, `- **NFP nowcasting** (the \`alt-nfp\` family, late 2025)`.

Then check the frontmatter: `git show HEAD:skills/design-architecture/SKILL.md | sed -n 1,21p | diff - <(sed -n 1,21p skills/design-architecture/SKILL.md) && echo frontmatter-unchanged`. Expected: `frontmatter-unchanged`.

- [x] **Step 9: Run the lints and the skill's suite**

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` — expected exit 0.
Run: `uv run --python 3.13 --with pyyaml python build/check_conformance.py` — expected exit 0.
Run: `uv run --python 3.13 python build/check_snippets.py skills/design-architecture/` — expected exit 0.
Run: `uv run --python 3.13 python build/check_provenance.py` — expected exit 0.
Run: `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies` — expected all passed.
Run: `uv run --python 3.13 python build/run_suites.py design-architecture` — expected the suite passes.

- [x] **Step 10: Commit**

```bash
git add skills/design-architecture/SKILL.md skills/design-architecture/references/decision-examples.md skills/design-architecture/references/example-inference-engine-adr.md
git commit -m "docs(design-architecture): date the alt-nfp framing and move the sketches to a reference" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Expected: the pre-commit lints pass and the commit lands.

---

### Task 3: Add three sketches from other project families

Each sketch summarizes one public source. The reviewer checks every factual clause against that source.

**Files:**
- Modify: `skills/design-architecture/references/decision-examples.md` (append)
- Modify: `skills/design-architecture/SKILL.md` (the pointer's project list)

**Interfaces:**
- Consumes from Task 2: `references/decision-examples.md` ending with sketch 5; the pointer section's one-bullet list.
- Produces: nothing that a later task uses.

- [x] **Step 1: See the Done-when gap**

Run: `grep -c '^## ' skills/design-architecture/references/decision-examples.md`
Expected: `1` (one project family). The item's Done when needs more than one.

- [x] **Step 2: Append the three sketches**

> Deviation: after the final review, the owner approved three corrections to this block (completion gate, 2026-10-21). Sketch 7 cites Req 15, the source of "persistent". Sketch 8's Trade-off states the spec's own trade-off (a large blast radius that buys nothing the installer's links do not already give) instead of a cost every option shares, its Alternatives drop that clause so it is said once, and its citation names `agent-skills` and the spec's path.

Append this block to the end of `skills/design-architecture/references/decision-examples.md`, after one blank line:

```markdown
## LLM evidence extraction (`earnings-themes`, 2026-10)

**6. Live-test model: a local open-weight model.** Decision: run the extractor's live test on
Gemma 4 31B-it (QAT Q4_0 weights), served on the developer's machine by llama.cpp's
`llama-server` with JSON-schema output, and pin the model ID, the weights' SHA-256 and the
runtime version. The requirements limit the required path to open-weight, self-hosted models, so
no billable call is made. Trade-off: the stronger dense model beats a mixture of experts that is
about twice as fast, because the test must finish both windows, and the 36 GB machine holds it.
Every cached reply's key names the model, the weights' hash and the runtime, so a change to any
of them misses the cache. Alternatives: Gemma 4 26B-A4B-it (faster, more memory headroom, but
weaker); Qwen3.8-27B (the newest, but its thinking is on by default and its card gives settings
against repetition, and either could leave a reply unfinished within the 2048-token limit);
Gemma 4 12B-it (a fallback for memory and speed that this machine does not need). Reversible:
another model is a new configuration and a new ADR, and no committed file stores a reply.
(`earnings-themes`, ADR 0004.)

## Revision research (`ces-revisions`, 2026-09)

**7. Causal design: decline the causal claim the data cannot identify.** Decision: fold the
Bureau's operational capacity (real enacted budget authority, appropriation-funded FTE and, where
the definitions match, CES workyears) into one persistent annual latent factor, and report its
effect on revision scale as an association with its prior sensitivity, never as a causal effect.
Trade-off: the report cannot say how many jobs of revision one more BLS employee prevents, and it
says so. In exchange it claims nothing the data cannot carry. Alternatives: unrestricted separate
slopes for budget, FTE, headcount, sample size and mode mix (rejected — separate slopes are not
recoverable from about 40 annual points, and reporting them as primary invites misreading); a
horseshoe over the separate slow covariates as the primary model (rejected for the same reason);
pooling government shutdowns with annual funding (rejected — shutdowns are case studies or timing
interventions). When the question is whether the data can identify an effect at all, the
recommend-causal-design skill goes deeper. (`ces-revisions` design spec, Req 13 and Req 19.)

## Repo tooling (`agent-skills`, 2026-10)

**8. One canonical skills tree, linked into each runtime.** Decision: keep every skill in the
repo's `skills/` directory and let the installer link it into each runtime's discovery path
(`~/.claude/skills/` for Claude Code, `~/.agents/skills/` for Codex and Gemini CLI). Trade-off:
one tree and one installer serve three runtimes, and each machine needs an install step.
Alternatives: move the tree to a cross-runtime `.agents/skills/` layout (rejected — a large blast
radius through the installer, the tests, `CLAUDE.md` and the symlinks, and it buys nothing the
installer's links do not already give); add an in-repo `.claude/skills` link as well (rejected —
the skills already load user-level from the same checkout, so each would be listed twice). A
later move means re-pointing the installer, the tests and every machine's links. (This repo's
portability spec, Decisions 1 and 2.)
```

- [x] **Step 3: Extend the pointer's project list**

In `skills/design-architecture/SKILL.md`, replace:

```markdown
- **NFP nowcasting** (the `alt-nfp` family, late 2025): the inference engine, the parquet store
  layout, scraper resilience, as-of censoring, and workspace boundaries.
```

with:

```markdown
- **NFP nowcasting** (the `alt-nfp` family, late 2025): the inference engine, the parquet store
  layout, scraper resilience, as-of censoring, and workspace boundaries.
- **LLM evidence extraction** (`earnings-themes`): which open-weight model a live test runs.
- **Revision research** (`ces-revisions`): declining a causal claim the data cannot identify.
- **Repo tooling** (`agent-skills`): one canonical skills tree, linked into each runtime.
```

- [x] **Step 4: See the gap close**

Run the Step 1 command. Expected: `4`.

Run: `git grep -n -E 'alt_nfp|oi-indices|alt-nfp([^-]|$)' -- skills/design-architecture/references/decision-examples.md`
Expected: exactly 3 lines, all in the `## NFP nowcasting (the \`alt-nfp\` family, late 2025)` group: its heading, its intro's first line, and sketch 1's second line.

- [x] **Step 5: Check the sources**

> Deviation: two clauses rested on text outside the named sources (sketch 7's "persistent" on Req 15, sketch 8's install step on the README and `install.py`). The implementer reported them as concerns and committed instead of stopping. The task review and the completion gate settled both.

For each new sketch, open its source and confirm each clause:
- Sketch 6: `/Users/lowell/Projects/earnings-themes/docs/adr/0004-use-a-local-open-weight-model-for-the-extractors-live-test.md` (Context, Decision, Consequences, Alternatives considered, Trade-offs & reversibility).
- Sketch 7: `/Users/lowell/Projects/ces-revisions/specs/ces-revisions.md`, Req 13 (from `**Req 13 — Operational capacity`) and Req 19 (from `**Req 19 — Outputs and claims.**`).
- Sketch 8: `specs/completed/agent-skills-portability-spec.md`, "Decisions and alternatives", items 1 and 2; `CLAUDE.md` for the two install paths.

If a clause is not in its source, stop and report it (NEEDS_CONTEXT) instead of rewording.

- [x] **Step 6: Run the lints and the skill's suite**

Run the six commands of Task 2 Step 9. Expected: each exits 0 or passes. Then run the frontmatter check from Task 2 Step 8. Expected: `frontmatter-unchanged`.

- [x] **Step 7: Commit**

```bash
git add skills/design-architecture/references/decision-examples.md skills/design-architecture/SKILL.md
git commit -m "docs(design-architecture): add decision sketches from three more projects" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Expected: the pre-commit lints pass and the commit lands.
