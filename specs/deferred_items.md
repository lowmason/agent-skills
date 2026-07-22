# Deferred items

## 11-delegation-frontmatter-rollout — 2026-07-19
- [ ] Haiku-pinned `Explore` override agent (fork-isolation upgrade; plan "Out of
      scope"): the direct `model: haiku` pins on `explore-data`/`bls-data-context`
      only cover the *invoking* turn (a skill `model` override is per-turn). A single
      haiku-pinned `agents/Explore.md` would keep a whole multi-turn profiling
      workflow on Haiku via `context: fork` + `agent: Explore`, and double as a global
      Explore→Haiku lever. Add only if the per-turn saving proves insufficient; needs
      a new agent file + a README Agents-table row.
- [ ] Interactive verification (plan Task 5 Steps 3–4, deviation): confirm the live
      model/effort indicator shows haiku/xhigh when the pinned skills load, and take a
      `/status` before/after cost reading on one exploration-heavy session. Could not
      run in the non-interactive execution flow; the enforceable lints/tests passed.
      Run in a normal interactive session — no code needed.
- [ ] Opt-ins decided against but available (one-line frontmatter adds if revisited):
      `effort: high` on `recommend-probabilistic-model`/`recommend-visualization`
      (no-op at the default `high`); `model: opus` on `bayesian-workflow` (would
      override its fresh-session model choice); `model: haiku` on `validate-data`
      (deliberately excluded — judgment-heavy ship-gate). See
      specs/completed/delegation-frontmatter-rollout.md Req 3/Req 5.

## 12-audit_7_20_26 — 2026-07-20
- [ ] Deep-ensembles notebook mispairing (final-review Minor (h), gate-batch deferred):
      `skills/recommend-probabilistic-model/references/families/classification.md`'s
      "Deep ensembles" row cites `PML2 §17.3.9` (a Bayesian-NN posterior-approximation
      topic) but links `notebooks/book1/18/bagging_trees.ipynb`, a decision-tree bagging
      notebook reused verbatim from the "Random forest / bagging" row above. Same defect
      class as C7; Gate A cannot catch it because the path resolves. A pyprobml sweep
      (`bnn|dropout|deep_ens`) found no dedicated deep-ensembles notebook — nearest are
      `book2/17/mnist_classification_mc_dropout.ipynb` (§17.3.1) and
      `book2/19/bnn_mnist_sgld_*.ipynb`. Needs the same deliberate judgment call C7 got:
      substitute a near-neighbour and label it a stand-in, or drop the link and let the
      §-ref carry the row. Pre-existing, not introduced by this plan.
- [ ] Snippet-execution gate for `bayesian-workflow` (audit Theme 1; offered at the
      completion gate, not selected): `skills/bayesian-workflow/SKILL.md:59` promises "the
      modern ArviZ >= 1.0 stack" and no gate enforces it. C1, C2 and D2 were all executable
      or API claims that went stale silently — C1's *mandatory* recipe raised on the exact
      declared stack. `build/verify_citations.py` proves this repo will mechanize a
      correctness check when the artifact is a §-ref; nothing equivalent guards inline code.
      Would have caught all three before review. Needs a runner that extracts fenced python
      from the skill and executes it against pinned deps.
- [ ] `PML2 §2.2.1.4` chapter-fallback WARN (offered at the completion gate, not selected):
      Gate A exits 0 but emits a standing WARN on this ref every run. Gate B verified it is
      a false alarm — the section exists ("Negative binomial distribution") and substantiates
      both claims attached to it; the WARN is an artifact of `build/.scratch/book2_sections.tsv`
      truncating at three nesting levels, so it holds `2.2.1` but no `2.2.1.x`. Either record
      it as a known-good exception or deepen `build/extract_structure.py`'s nesting. Until
      then it draws review attention on every pass.
- [ ] QCEW datatype-05 label unverified (final-review Minor (f), partially resolved):
      the hub's claim that datatype 05 is "average annual pay" was dropped to the verified
      "its annual-only datatype carries `A01`" (period structure confirmed live via BLS API
      v1: `ENUUS00050010` returns only `A01`). The *label* remains unconfirmed because
      `download.bls.gov` returns 403 from this environment and `references/qcew.md` documents
      no datatype codes. Restore the specific label once BLS is reachable, or add a datatype
      table to `qcew.md` so the hub has a quotable line to derive from.

## 13-llm-wiki — 2026-07-22
Deferred from the final adversarial linter audit (all in the plan's verbatim regexes;
the spec author chose to fix the two guard/backstop holes — G1 quarantine bypass, G2
secret backstop — and defer these). The linter faithfully implements M0 and passes all
gates; these bite only on real wiki *content*, which does not exist yet (M1+).

Regex-strictness design calls (need a spec decision on how strict the M0 linter should be):
- [ ] D1 — `BODY_CITE_RE` fires a hard ERROR on ordinary bracketed prose (`[see below]`,
      `[per the user]`, `[todo …]`): any `[word …]` not immediately followed by `(` is
      treated as a citation locator. Task 7's reviewer read this as intended strictness;
      the whole-branch Opus reviewer and the regex breaker read it as a false positive
      (`SCHEMA.md` does not reserve brackets for locators). Decide the intent; if
      false-positive, tighten to require a locator sigil (`§`/`p.`/`Table`/`Fig`/`Eq`/a
      leading digit) after the slug, or require a multi-part slug (hyphen or 4-digit year).
      `~/research-wiki/scripts/lint_wiki.py` `BODY_CITE_RE`.
- [ ] D2 — nested brackets in link text break both directions: `MD_LINK_RE` misses a
      genuinely-broken link like `[the [above] discussion](samplers/none.md)` AND
      `BODY_CITE_RE` fabricates a citation from the link text. Fix `MD_LINK_RE` to allow one
      level of balanced nested brackets, and exclude link-text spans from citation matching.
      Edge case; unlikely in early content.
- [ ] D3 — citation slugs outside `[a-z0-9-]` are invisible (`[Hoffman2014 §3]`,
      `[robnik_2022 §4]`, `[robnik.2022 §4]` all pass unchecked, both directions). The
      lowercase-start anchor also serves as a deliberate prose guard (`[NUTS §3]`,
      `[Figure 2]` correctly ignored), so widening the charset naively re-introduces prose
      false-positives. Needs a design separating "is a citation" from "slug charset".

Downgraded-to-minor from the same audit (later hardening pass; none block M0):
- [ ] `MD_LINK_RE` / `INDEX_LINE_RE` capture a CommonMark link *title* attribute
      (`[a](x.md "Title")`) as part of the path, breaking resolution/parity if titles are used.
- [ ] `_index_targets` does not strip a `#fragment` from an index-line target (whereas
      `check_links` does for body links) — an index deep-link `sources/a.md#background`
      yields false parity/link errors. Decide whether fragment-bearing index lines are legal.
- [ ] `DECISION_META_RE` anchors `^kind: decision` with no tolerance for leading whitespace
      or a markdown list prefix (`  kind: decision`, `- kind: decision`), silently disabling
      the echo-rule check for indented captures.
- [ ] `check_links` counts a page's self-link as an inbound reference (silencing its own
      orphan warning); and on a case-insensitive FS (macOS/APFS) a broken relative link with
      wrong case (`../Sources/A.MD`) resolves via `.exists()` and escapes the broken-link
      check. Prefer membership in the discovered page set over `resolved.exists()`.

Adjudicated INTENDED-behavior (recorded so they are not re-litigated — no action):
- The `assignment` secret pattern fires on compound identifiers like `client_secret` /
  `csrf_token` (no `\b`). Deliberate: adding `\b` would stop catching real
  `client_secret = "…"` / `refresh_token = "…"` — a net regression for a backstop.
- Structural files (`index.md` / `log.md` / `open-questions.md`) are excluded from
  link/citation scanning. Matches the §10 contract (they are not "pages"); making
  `open-questions.md` locators machine-checkable would be a spec change.

Per-task report/test-hygiene minors (cosmetic; code always independently verified — noted,
not tracked as work): several haiku implementer reports miscounted test tallies; and three
plan-mandated test-coverage gaps exist because the briefs specified exactly the shipped test
sets — `test_discover_pages_excludes_structural_files`'s exclusion half is vacuous (the
`wiki/*/*.md` depth-2 glob can't match depth-1 structural files), and neither
`check_quarantine`'s "target page missing" branch nor `check_index_parity`'s duplicate-line
branch has a dedicated test.
