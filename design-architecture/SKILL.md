---
name: design-architecture
description: >
  Use when authoring or evaluating Architecture Decision Records (ADRs) for data and modeling
  systems — choosing between technologies or approaches (NumPyro/JAX vs PyMC inference, Polars
  vs pandas, Trino vs DuckDB, one parquet layout vs another), when a design decision spans
  multiple packages or repos, when reviewing a design proposal or spec for whether its
  trade-offs are honest, or when you catch yourself re-explaining a past decision. An ADR is the
  durable, numbered, immutable record of WHY a cross-cutting choice was made, so it isn't
  silently re-litigated every session. Trigger on: ADR, architecture decision, design record, design
  doc/spec review, "should we use X or Y", "document this decision", "why did we pick", trade-off
  analysis, alternatives considered, reversibility / blast radius, superseding a prior decision,
  parquet store layout & dedup/vintage policy, scraper resilience (retry/backoff/fixtures),
  as-of / vintage / point-in-time data modeling, multi-package workspace boundaries, inference
  engine choice, or determinism/seed/parity decisions. Especially when the same problem is being
  solved more than one way across repos with no recorded rationale.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# Design Architecture (ADRs)

## Why this exists

An Architecture Decision Record captures **one significant, hard-to-reverse decision and the
reasoning behind it** at the moment it is made. The value is not the document — it is the
*audit trail*. Without it, a choice like "nowcast in NumPyro/JAX, not PyMC" survives only as
tribal memory, and every new session re-derives, re-argues, or quietly contradicts it.

This is a live cost in practice: the **same NFP-nowcasting problem is currently solved three
ways** — NumPyro/JAX in `alt-nfp`, and PyMC in both `alt_nfp` and `oi-indices` — with no
recorded rationale for the split. An agent reading any one repo cannot tell whether the other
engines are deliberate (parity cross-checks, GPU vs ergonomics) or accidental drift. An ADR
turns that fork from a mystery into a decision you can build on.

Two modes, both first-class:

- **Authoring** — write a new ADR for a decision being made now (most of this skill).
- **Evaluating** — judge an existing ADR, spec, or design proposal: are the trade-offs honest,
  the alternatives real, the blast radius understood? See **Evaluating a proposal** below.

Reach for an ADR when a decision is **costly to reverse, affects more than one package/repo, or
constrains future choices**. Skip it for reversible, local calls (a function signature, a plot
style) — over-documenting trivia trains readers to ignore the record.

## The mechanism that actually solves re-litigation

A template alone does not stop a decision from being re-argued. Two properties do:

1. **An accepted ADR is immutable.** Once its Status is `Accepted`, you do not edit the Context
   or Decision to reflect new thinking. The record is what was decided *then*, with the
   information available *then*. Editing it destroys the audit trail — the next reader can no
   longer see that the world changed.
2. **Decisions change by supersession, not edit.** When a decision is revisited, write a *new*
   ADR that supersedes the old one, and flip the old one's status to `Superseded by NNNN`. The
   chain of superseding ADRs *is* the institutional memory: it shows not just the current answer
   but every answer you've held and why each was abandoned.

This is the whole point. A skim of the new ADR shows the rejected alternative was already
considered and ruled out — so it doesn't get proposed again from scratch.

### Status lifecycle

```
Proposed ──► Accepted ──► Deprecated          (no longer relevant; nothing replaces it)
                   │
                   └────► Superseded by 0014   (replaced; 0014 supersedes 0009)
```

- **Proposed** — drafted, under discussion. Editable.
- **Accepted** — agreed and in force. Immutable except the Status line itself.
- **Deprecated** — the decision no longer applies and nothing replaces it (e.g. the component
  was deleted). The ADR stays in the tree as history.
- **Superseded by NNNN** — a later ADR replaces it. The new ADR names the old one in its own
  Context ("supersedes 0009").

## Where ADRs live

Follow the repo's existing design-record culture rather than inventing a new home. In this
stack the conventions are `specs/` (active design, e.g. `alt-nfp/specs/`) plus MkDocs + per-package
`CLAUDE.md`. So:

- **Default to `docs/adr/` when the repo publishes a MkDocs site** — ADRs render as a browsable
  decision log and link from the nav. Add an `index.md` listing them.
- **Use `specs/adr/` when the repo's design record already lives in `specs/`** (as `alt-nfp`
  does) — keep ADRs beside the specs and plans they formalize.

Name files `NNNN-kebab-slug.md` with a zero-padded sequence: `0001-record-architecture-decisions.md`,
`0009-numpyro-jax-over-pymc-for-nowcasting.md`. The number is permanent and never reused, even
after supersession. The optional `scripts/new_adr.py` scaffolder picks the next number and writes
the template for you (see **Scaffolder**).

## ADR template

Keep ADRs short — one decision, one page. Prose over bullet soup; a reader should grasp the
*why* in a minute.

```markdown
# NNNN. <short imperative title: the decision, not the problem>

- **Status:** Proposed | Accepted | Deprecated | Superseded by NNNN
- **Date:** YYYY-MM-DD
- **Deciders:** <who agreed>
- **Blast radius:** <packages/repos affected, e.g. nfp-model only | whole uv workspace | alt-nfp + oi-indices>

## Context

The forces at play: the problem, the constraints, what is and isn't known *as of this date*.
State the constraints that actually drive the choice (determinism requirement, GPU target,
as-of correctness, team familiarity). This section is frozen once Accepted — write it as a
snapshot, not a living doc.

## Decision

The choice, in active voice: "We will <do X>." One decision per ADR. If you're tempted to write
"and also," that's a second ADR.

## Consequences

What becomes easier and what becomes harder *because* of this decision — both honestly.

- **Positive:** <what this unlocks>
- **Negative:** <the price paid, ongoing>
- **Neutral / follow-on:** <new work or ADRs this creates>

## Alternatives considered

At least the genuinely-viable options, each with the specific reason it lost — not a strawman.
"We considered pandas but chose Polars" is not an alternative; "pandas — rejected because the
as-of joins are 8x slower on the vintage panel and lack lazy streaming" is.

- **<Option A>** — rejected because <concrete trade-off>.
- **<Option B>** — rejected because <concrete trade-off>.

## Trade-offs & reversibility

The crux: what you're trading, and how expensive a reversal would be (one-way vs two-way door).
Note what would *trigger* a revisit (a superseding ADR) — e.g. "if GPU batching stops being the
bottleneck, the JAX cost may no longer pay for itself."
```

## Authoring workflow

1. **Confirm it deserves an ADR.** Costly to reverse, or crosses package/repo boundaries? If
   not, decide in a code comment or `CLAUDE.md` note instead.
2. **Pick the number and file** (or run `scripts/new_adr.py "<title>"`).
3. **Write Context first, as a frozen snapshot.** Resist editing it later — that's what
   supersession is for.
4. **State exactly one Decision.** Split anything compound.
5. **Fill Consequences honestly**, including the negatives you'd rather not advertise. An ADR
   with no negative consequences is a sales pitch, not a record.
6. **List real alternatives** with concrete losing reasons (see the rubric below).
7. **Set Status.** `Proposed` while under discussion; `Accepted` once agreed — and from then on,
   immutable.
8. **Link it.** Reference the ADR from the relevant `CLAUDE.md` / `ARCHITECTURE.md` / spec so
   future readers find it. If it supersedes another, flip the old one's status and name it here.

## Decision examples (this stack)

Compact sketches — decision + the trade-off that actually drives it + the real alternatives.
Tune to the repo you're in. The flagship inference-engine ADR is worked in full in
[references/example-inference-engine-adr.md](references/example-inference-engine-adr.md) and
doubles as a copy-paste starting point.

**1. Inference engine: NumPyro/JAX over PyMC (the flagship).** The same nowcast runs three ways
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

## Evaluating a proposal

When reviewing an ADR, spec, or design doc, you are checking whether the *reasoning* is sound,
not whether you'd have made the same call. Apply this rubric.

| Check | What "good" looks like | Red flag |
|---|---|---|
| **Trade-offs explicit** | Both positive *and* negative consequences stated; the price is named | All upside, no cost — a pitch, not a record |
| **Alternatives genuine** | ≥2 viable options, each with a *concrete* losing reason | One option, or strawmen ("we could do nothing") |
| **One decision** | A single choice; compounds are split | "X and also Y and while we're at it Z" |
| **Reversibility named** | States one-way vs two-way door; what would trigger a revisit | Silent on cost of being wrong |
| **Blast radius scoped** | Names the packages/repos affected (e.g. `nfp-model` only vs whole workspace) | "It's fine" with no scope |
| **Testability / parity** | Says how the decision is verified — parity gate, fixtures, determinism/seed, golden masters | No way to tell if it's working |
| **Context is frozen-able** | Reads as a dated snapshot, not a living wishlist | Aspirations mixed into recorded fact |
| **Determinism** | For modeling/data decisions: seeds, float precision, ordering pinned | Reproducibility left implicit |

For a modeling/inference decision specifically, push on **parity and determinism**: does the
proposal say how results are reproduced (descriptive seeds, not `42`), at what float precision
(parity is often defined in float64), and against what reference (a frozen golden master, not "it
looked right")? In this stack, "parity is a fidelity floor, not a correctness certificate" — a
good ADR says so, and points correctness validation at external ground truth (published BLS /
ALFRED vintages), not at the reference implementation.

If a proposal fails the rubric, the fix is usually not "reject" but "send back for the missing
half": demand the second alternative, the negative consequence, or the reversibility note.

## Common mistakes & anti-patterns

- **Editing an Accepted ADR instead of superseding it.** This is the cardinal sin — it erases the
  audit trail. The record should show the world changed, not pretend it always read this way.
  Write a new ADR; flip the old status to `Superseded by NNNN`.
- **Strawman alternatives.** Listing only the chosen option, or "do nothing," so the Alternatives
  section is theater. If you can't name two options you genuinely weighed, you haven't finished
  thinking — or it didn't need an ADR.
- **Consequences with no negatives.** Every real decision costs something. An all-positive
  Consequences section means the cost was hidden, not absent — and it'll surface later as a
  surprise the ADR should have flagged.
- **Documenting the obvious / over-ADR-ing.** An ADR per function or plot style buries the
  load-bearing decisions in noise and teaches readers to skip the folder. Reserve ADRs for the
  costly, cross-cutting calls.
- **Solving one problem N ways with zero ADRs.** The motivating failure: NumPyro/JAX vs PyMC
  across three repos with no record. Multiple implementations are *fine* — as a deliberate,
  documented choice (e.g. PyMC as a parity reference). Undocumented, they read as drift and get
  "fixed" by someone unifying them and breaking a cross-check.
- **The compound decision.** Bundling several choices into one ADR so none can be superseded
  independently. Split them; each gets its own number and lifecycle.
- **Context that keeps growing.** If you find yourself appending to an Accepted ADR's Context,
  that's a superseding ADR trying to be born.
- **Title states the problem, not the decision.** "0009. Inference engine" is a topic;
  "0009. Use NumPyro/JAX over PyMC for nowcasting" is a decision a reader can act on.
- **No back-link.** An ADR no one can find is no better than tribal memory. Link it from
  `ARCHITECTURE.md` / `CLAUDE.md` / the relevant spec.

## Scaffolder

`scripts/new_adr.py` automates the next-number-plus-slug step so numbering stays consistent:

```bash
# Writes specs/adr/0009-use-numpyro-jax-over-pymc-for-nowcasting.md (or docs/adr/ — pass --dir)
# (stdlib-only, so plain python3 suffices; absolute path works from any repo cwd)
python3 ~/.claude/skills/design-architecture/scripts/new_adr.py "Use NumPyro/JAX over PyMC for nowcasting"
python3 ~/.claude/skills/design-architecture/scripts/new_adr.py "Store parquet levels only" --dir docs/adr --status Proposed
```

It scans the target directory for the highest `NNNN-` prefix, increments it, slugifies the title,
and writes the template above with the date filled in. It never overwrites an existing file. The
scaffolder is a convenience — writing the file by hand with the next number is equally fine.
