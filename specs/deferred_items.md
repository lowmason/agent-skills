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

(Ticking pass for this section, run again at plan 14's completion: none of the above were
implemented by plan 14 — it touches `~/research-wiki/scripts/distill_sessions.py` and one
anchor fix in `lint_wiki.py`'s `openai-key` pattern, none of which overlap D1–D3, the
downgraded-to-minor lint items, or the per-task report/test-hygiene notes above.)

## 14-llm-wiki-distiller — 2026-07-23

Deferred from plan 14 (the session distiller) — the consolidated Minor list compiled before
the final whole-branch review, the later review rounds' Minors, and the residual the Task 8
fix pass disclosed but did not chase further. Excluded from this list because they were
actually fixed: the sidechain-collision/tool-trace-aggregation/redaction-false-positive/
defensive-guard/idempotence-freeze set (Task 8's five items), the `UnicodeDecodeError` catch
fixes (Tasks 6/7), and the `lint_wiki.py` `openai-key` anchor fix (see plan 14 Post-execution
item (b)). All file paths are under `~/research-wiki/scripts/` unless noted; function names
are used instead of line numbers because Task 8 rewrote large parts of both files, moving
every pre-Task-8 line reference.

Robustness / edge cases:
- [ ] `distill_sessions.py::_claude_ai_turns` sorts turns by `t['ts']` with no tiebreaker, so
      an undated message (`ts == ''`) sorts to position 1 and gets renumbered ahead of turns
      that actually came first in the conversation. A `(ts, original_index)` compound sort key
      would preserve original order among same-timestamp or undated turns. Deferred because no
      real conversation in the 156-conversation export reproduces it, and turn numbers are
      spec §16.4's locator currency for future captures — renumbering should be batched with
      any other numbering-affecting change, not done piecemeal outside a sequencing window.
- [ ] `distill_sessions.py::_turn_date` passes a malformed but non-empty timestamp straight
      through unvalidated — e.g. `'not-a-timestamp'` slices to `'not-a-time'`, survives the
      sentinel filter added by the Task 5/6 fixes, and becomes the digest's filename date.
      Fix would validate the sliced prefix looks like `YYYY-MM-DD` (e.g. a small regex check)
      and fall back to the `'0000-00-00'` sentinel otherwise.
- [ ] `distill_sessions.py::_read_jsonl` and `::iter_claude_ai` call `Path.read_text()` with no
      explicit `encoding='utf-8'`. On a non-UTF-8 default locale this could silently
      misclassify good transcripts as parse failures via the (now correctly caught)
      `UnicodeDecodeError` path, rather than reading them correctly. Fix: pass
      `encoding='utf-8'` explicitly at both read sites.
- [ ] `distill_sessions.py::slugify('')` returns `'session'`; two sessions from the same
      source with no title-bearing text at all (no user-turn text to slugify, no conversation
      `name`) collide on `session-<sess8>` in the output filename, and idempotence silently
      swallows the second. Narrow (requires a genuinely titleless, textless session) but
      unguarded.
- [ ] Adjudicated INTENDED-behavior, no action (recorded so it is not re-litigated): a
      generic hex-only high-entropy secret with no key-shaped prefix (no `sk-`, `ghp_`,
      `AKIA`, etc.) is caught by neither the distiller's `redact()` nor the `lint_wiki.py`
      backstop. Deliberate — widening the `high-entropy` class or the backstop to catch
      bare hex would also flag git SHAs, and `lint_wiki.py`'s `BASIS_OK_RE` requires a
      literal, intact SHA for `basis: git:<sha>` decision captures to pass their own lint.
- [ ] Adjudicated INTENDED-behavior, no action (reviewer explicitly rejected this as a gap):
      the `claude-ai` adapter emits no tool-use traces even though the real export contains
      1770 `tool_use` content blocks. `claude-ai` conversations don't carry the same tool-call
      shape as Claude Code transcripts and adding trace synthesis for them was ruled
      deliberately out of this plan's scope, not a missed requirement.

DRY / structure:
- [ ] The sentinel-date-filtering logic (exclude `'0000-00-00'` before taking a date floor,
      falling back to the sentinel only when every date is missing) is now duplicated
      verbatim across three sites — `iter_claude_ai`, `iter_claude_code`, and `write_digest` —
      with the `'0000-00-00'` string literal in all three. Evidence it should be a shared
      helper (e.g. `_real_dates(turns) -> list[str]`): the identical sentinel-poisons-`min()`
      bug had to be found and fixed independently at two of the three sites (the Task 5 and
      Task 6 fixes) before the duplication was even noticed. Extracting the helper touches all
      three call sites — treat as one whole-file refactor, not a per-function patch.

Test-coverage gaps:
- [ ] `test_claude_code_project_filter` asserts the resulting digest *count* (`== 1`), not
      which session survived — an inverted filter (keeping the wrong project) would still
      pass. Strengthen to assert the surviving digest's `project:` header value.
- [ ] `_project_name`'s no-`cwd`-fallback branch (deriving the project name from the encoded
      directory name when no record in the session carries `cwd`) executes during real-corpus
      smoke runs but has no dedicated unit test asserting its output.
- [ ] `reconstruct`'s `isMeta` drop branch (records with `isMeta: true` are skipped) has no
      dedicated test; separately, no test exercises a compaction-flagged record with
      genuinely empty text surviving the tool-plumbing filter via the `not compaction` guard
      clause (as opposed to a compaction record that also carries text).
- [ ] `write_digest`'s `' [compaction summary]'` marker rendering is untested — Task 4 tests
      only that the `compaction` flag reaches `reconstruct`'s output, not that `write_digest`
      actually renders the marker string into a written digest body.
- [ ] Zero-turn digest writing (a session with no narrative turns still gets an empty-bodied
      digest, per §16.5's "zero is a legitimate outcome") is untested beyond the guard the
      Task 5 fix pass added; no test asserts the empty-bodied file's actual header contents
      (e.g. `turns: 0`).
- [ ] The Task 5 fix-pass regression test for the unbounded-slug fix (F1) asserts
      `len(name) < 255`; the real bound the `slugify(...)[:60]` fix guarantees is 83
      characters (10-char date + up to 60-char slug + hyphens + 8-char sess8 + `.md`) — a
      much weaker assertion than what the fix actually guarantees.
- [ ] Three Task 5 fix-pass tests construct a session with `project=None` but none asserts
      `'project:'` is actually absent from the written digest body.
- [ ] `slugify` and `_turn_date` have no test that calls them directly; both are exercised
      only indirectly through `write_digest`'s behavior.

Cosmetic:
- [ ] A tool-only turn with no narrative text renders with a double space —
      `'**[03] assistant:**  [tools: Bash ×1]'` — because `write_digest`'s body-line f-string
      always inserts a space before the trace even when the redacted text is empty.
- [ ] No blank line separates a digest's closing frontmatter `---` from its first body line.
      Cosmetic only: §16.4 imposes no such requirement, and `lint_wiki.py` never parses
      `raw/sessions/*.md` as frontmatter pages (`check_frontmatter_schema` only runs over
      `wiki/*/*.md`), so this cannot fail lint.
- [ ] `test_distill_sessions.py`'s claude-ai tests are interleaved with a claude-code test
      rather than grouped together.
- [ ] One Task 5 implementer report described its own self-review as "no issues found"
      immediately before re-review found 2 Important findings in the same task's diff — a
      report-accuracy note; the code was always independently re-verified regardless.

Spec/plan wording:
- [ ] Spec's own §16.4 worked example (now `specs/completed/llm-wiki-spec.md`) shows
      `session: a3f2c9d1` (8 characters) in the digest frontmatter, but the shipped code
      always writes the full session UUID (`session: 81bf53fc-2687-4b61-80e6-359c50e3f047`),
      and the plan's own Task 5 test pins the full form. The plan deliberately diverged from
      the spec's illustrative example — the full id is arguably more useful, since the 8-char
      form is already in the filename — but nobody has gone back to correct the spec's now-
      stale example to match. Cosmetic; only the Idempotence bullet was amended at this
      completion (see plan 14 Post-execution), not this example.
- [ ] Plan 14 Task 4's prose says the noise-removal rule drops "USER records that are pure
      tool-result plumbing"; the shipped `reconstruct` code applies the same
      empty-text/no-tools/no-compaction filter to *both* roles. The wider behavior is correct
      (an assistant turn consisting only of `thinking` blocks should also be dropped), so this
      is a wording defect in the retired plan's text, not a logic defect in the code.

Residual lint false positive (real corpus, precise, deliberately not chased further):
- [ ] `lint_wiki.py`'s `assignment` secret pattern still scores 2 false positives on one real
      digest, and only when `distill_sessions.py` is run with `--include-sidechains`: the
      matched text is pre-existing session prose from a past conversation that literally
      discusses this exact pattern's missing `\b` word-boundary (meta-recursion — the session
      being distilled was, in part, about this bug). Confirmed absent from plain root-level
      and single-project runs, so a normal ingest of this corpus lints fully clean today.
      Deliberately not fixed: narrowing `assignment` risks reopening the real gap the
      `13-llm-wiki` section above already adjudicated as intended behavior (no `\b`, because
      compound identifiers like `client_secret`/`refresh_token` must keep matching). The
      false positive here is content-specific (a session about the pattern itself), not
      structural.

## 15-clean-code-family — 2026-07-24

- [ ] Ship `clean-code-python` user-level (`~/.claude/rules` → `~/Projects/agent-skills/rules`):
      deliberately not shipped — gate 2026-07-24 chose project-level only. Task 8's
      informational probe showed the user-level symlink DID load on Claude Code 2.1.218
      (contradicting issue #21858's silent-ignore report; probe transcript in commit
      7aa454f's body). Revisit if the always-on Python guardrails are wanted across work
      repos; mechanism is version-dependent, so re-probe on the then-current binary first
      (one `claude -p` probe against a scratch `probe.py`, per plan 15 Task 8 Step 5).
