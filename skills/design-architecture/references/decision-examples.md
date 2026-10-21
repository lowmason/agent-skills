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
in `example-inference-engine-adr.md` — this is the decision whose absence motivated the whole
skill.

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
recommend-causal-design skill goes deeper. (`ces-revisions` design spec, Req 13, Req 15 and
Req 19.)

## Repo tooling (`agent-skills`, 2026-10)

**8. One canonical skills tree, linked into each runtime.** Decision: keep every skill in the
repo's `skills/` directory and let the installer link it into each runtime's discovery path
(`~/.claude/skills/` for Claude Code, `~/.agents/skills/` for Codex and Gemini CLI). Trade-off:
the repo departs from the cross-runtime `.agents/skills/` convention and relies on the
installer's links, and in return it avoids a move whose large blast radius would buy nothing
those links do not already give. Alternatives: move the tree to a cross-runtime
`.agents/skills/` layout (rejected — a large blast radius through the installer, the tests,
`CLAUDE.md` and the symlinks); add an in-repo `.claude/skills` link as well (rejected — the
skills already load user-level from the same checkout, so each would be listed twice). A later
move means re-pointing the installer, the tests and every machine's links. (`agent-skills`
portability spec, `specs/completed/agent-skills-portability-spec.md`, Decisions 1 and 2.)
