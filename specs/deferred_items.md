# Deferred items

## 11-delegation-frontmatter-rollout — 2026-07-19
- [x] Haiku-pinned `Explore` override agent (fork-isolation upgrade; plan "Out of
      scope"): the direct `model: haiku` pins on `explore-data`/`bls-data-context`
      only cover the *invoking* turn (a skill `model` override is per-turn). A single
      haiku-pinned `agents/Explore.md` would keep a whole multi-turn profiling
      workflow on Haiku via `context: fork` + `agent: Explore`, and double as a global
      Explore→Haiku lever. Add only if the per-turn saving proves insufficient; needs
      a new agent file + a README Agents-table row. → done in plan 17
      (`agents/explore.md`, lowercase filename with load-bearing `name: Explore`;
      shadowing probe-verified on 2.1.219)
- [ ] Interactive verification (plan Task 5 Steps 3–4, deviation): confirm the live
      model/effort indicator shows haiku/xhigh when the pinned skills load, and take a
      `/status` before/after cost reading on one exploration-heavy session. Could not
      run in the non-interactive execution flow; the enforceable lints/tests passed.
      Run in a normal interactive session — no code needed.
- [x] Opt-ins decided against but available (one-line frontmatter adds if revisited):
      `effort: high` on `recommend-probabilistic-model`/`recommend-visualization`
      (no-op at the default `high`); `model: opus` on `bayesian-workflow` (would
      override its fresh-session model choice); `model: haiku` on `validate-data`
      (deliberately excluded — judgment-heavy ship-gate). See
      specs/completed/delegation-frontmatter-rollout.md Req 3/Req 5.
      → retired 2026-09-02: a record of options deliberately not taken, not work; none
      of the three keys was ever added, and the decision already lives in
      specs/completed/delegation-frontmatter-rollout.md Req 3/Req 5.

## 12-audit_7_20_26 — 2026-07-20
- [x] Deep-ensembles notebook mispairing (final-review Minor (h), gate-batch deferred):
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
      → done 2026-09-02 (/deferred quick fix): dropped the link — no pyprobml deep-
      ensembles notebook exists, so the row carries §17.3.9 alone, as other notebook-
      less rows do; Gate A, the rpm tests and the smoke test pass.
- [ ] Snippet-execution gate for `bayesian-workflow` (audit Theme 1; offered at the
      completion gate, not selected): `skills/bayesian-workflow/SKILL.md:59` promises "the
      modern ArviZ >= 1.0 stack" and no gate enforces it. C1, C2 and D2 were all executable
      or API claims that went stale silently — C1's *mandatory* recipe raised on the exact
      declared stack. `build/verify_citations.py` proves this repo will mechanize a
      correctness check when the artifact is a §-ref; nothing equivalent guards inline code.
      Would have caught all three before review. Needs a runner that extracts fenced python
      from the skill and executes it against pinned deps.
- [x] `PML2 §2.2.1.4` chapter-fallback WARN (offered at the completion gate, not selected):
      Gate A exits 0 but emits a standing WARN on this ref every run. Gate B verified it is
      a false alarm — the section exists ("Negative binomial distribution") and substantiates
      both claims attached to it; the WARN is an artifact of `build/.scratch/book2_sections.tsv`
      truncating at three nesting levels, so it holds `2.2.1` but no `2.2.1.x`. Either record
      it as a known-good exception or deepen `build/extract_structure.py`'s nesting. Until
      then it draws review attention on every pass.
      → done 2026-09-02 (/deferred quick fix): recorded in KNOWN_GOOD_FALLBACKS in
      build/verify_citations.py, test-first; Gate A now runs with no stderr.
- [x] QCEW datatype-05 label unverified (final-review Minor (f), partially resolved):
      the hub's claim that datatype 05 is "average annual pay" was dropped to the verified
      "its annual-only datatype carries `A01`" (period structure confirmed live via BLS API
      v1: `ENUUS00050010` returns only `A01`). The *label* remains unconfirmed because
      `download.bls.gov` returns 403 from this environment and `references/qcew.md` documents
      no datatype codes. Restore the specific label once BLS is reachable, or add a datatype
      table to `qcew.md` so the hub has a quotable line to derive from.
      → done 2026-09-03 (/deferred quick fix): verified and restored. The owner authorised
      using their contact email in the User-Agent, which cleared the 403. Two independent
      sources agree that **datatype 5 = Average Annual Pay**: the live CEW classifications
      table (bls.gov/cew/classifications/datatype/datatype-titles.htm, fetched 2026-09-03)
      and `en.type` inside the archived `en_meta.zip`. `references/qcew.md` gained a datatype
      table with both sources, and the hub's reference index advertises it. The hub now names
      average annual pay as the annual-only datatype, code `5`, whose cells carry `A01` — the
      datatype and the period code are deliberately kept distinct, since `A01` is a period code
      and an earlier draft of this fix conflated the two. Two corrections the item did not anticipate:
      the code is `5`, **one character at series-ID position 9, not the zero-padded `05`**;
      and the old routes are gone, not merely blocked — `/pub/time.series/en/` 404s (no `en`
      directory at all, and Wayback has no `en.datatype` capture) and `help/hlpforma.htm` no
      longer documents the ENU format.

## 13-llm-wiki — 2026-07-22
Deferred from the final adversarial linter audit (all in the plan's verbatim regexes;
the spec author chose to fix the two guard/backstop holes — G1 quarantine bypass, G2
secret backstop — and defer these). The linter faithfully implements M0 and passes all
gates; these bite only on real wiki *content*, which does not exist yet (M1+).

Regex-strictness design calls (need a spec decision on how strict the M0 linter should be):
- [x] D1 — `BODY_CITE_RE` fires a hard ERROR on ordinary bracketed prose (`[see below]`,
      `[per the user]`, `[todo …]`): any `[word …]` not immediately followed by `(` is
      treated as a citation locator. Task 7's reviewer read this as intended strictness;
      the whole-branch Opus reviewer and the regex breaker read it as a false positive
      (`SCHEMA.md` does not reserve brackets for locators). Decide the intent; if
      false-positive, tighten to require a locator sigil (`§`/`p.`/`Table`/`Fig`/`Eq`/a
      leading digit) after the slug, or require a multi-part slug (hyphen or 4-digit year).
      `~/research-wiki/scripts/lint_wiki.py` `BODY_CITE_RE`.
      → done in plan 23: adjudicated a false positive. Recognition now requires a
      position sigil AND (multi-part slug OR membership in the source-slug set), so
      `[see below]` is prose. Rule written into SCHEMA.md at schema-version 3.
- [ ] D2 — nested brackets in link text break both directions: `MD_LINK_RE` misses a
      genuinely-broken link like `[the [above] discussion](samplers/none.md)` AND
      `BODY_CITE_RE` fabricates a citation from the link text. Fix `MD_LINK_RE` to allow one
      level of balanced nested brackets, and exclude link-text spans from citation matching.
      Edge case; unlikely in early content.
      → REDUCED by plan 23 (still open): the citation-fabrication half is closed — the
      recognition rule rejects the fabricated token (`the`, position `[above`), verified
      as acceptance case 14 and observable as a red row in that plan's Task 1 Step 2.
      What remains is the `MD_LINK_RE` nesting half alone: a genuinely-broken link like
      `[the [above] discussion](samplers/none.md)` is still missed. No longer needs
      "exclude link-text spans from citation matching" — write the mechanical plan
      against the nesting fix only.
- [x] D3 — citation slugs outside `[a-z0-9-]` are invisible (`[Hoffman2014 §3]`,
      `[robnik_2022 §4]`, `[robnik.2022 §4]` all pass unchecked, both directions). The
      lowercase-start anchor also serves as a deliberate prose guard (`[NUTS §3]`,
      `[Figure 2]` correctly ignored), so widening the charset naively re-introduces prose
      false-positives. Needs a design separating "is a citation" from "slug charset".
      → done in plan 23: BODY_CITE_RE now captures (token, position) and the charset
      widened to `[A-Za-z0-9._-]`; the prose guard moved into `_looks_like_position` +
      `_is_citation`, so widening no longer reintroduces D1. Resolution stays
      case-sensitive, so a miscased slug errors rather than silently missing.

Downgraded-to-minor from the same audit (later hardening pass; none block M0):
- [ ] `MD_LINK_RE` / `INDEX_LINE_RE` capture a CommonMark link *title* attribute
      (`[a](x.md "Title")`) as part of the path, breaking resolution/parity if titles are used.
- [x] `_index_targets` does not strip a `#fragment` from an index-line target (whereas
      `check_links` does for body links) — an index deep-link `sources/a.md#background`
      yields false parity/link errors. Decide whether fragment-bearing index lines are legal.
      → done in plan 23: legal. `_index_targets` strips the fragment, matching
      `check_links`. All three parity checks read that one site, so duplicate detection
      was fixed at the same time.
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
      → decided 2026-09-03 (/deferred): renumber now — the owner released the
      "batch with another numbering-affecting change" condition, and no such
      change exists among the remaining items. The condition is discharged, so
      this joins the `distill_sessions.py` plan as ordinary planned work. Still
      unticked: the decision is made, the work is not.
- [x] `distill_sessions.py::_turn_date` passes a malformed but non-empty timestamp straight
      through unvalidated — e.g. `'not-a-timestamp'` slices to `'not-a-time'`, survives the
      sentinel filter added by the Task 5/6 fixes, and becomes the digest's filename date.
      Fix would validate the sliced prefix looks like `YYYY-MM-DD` (e.g. a small regex check)
      and fall back to the `'0000-00-00'` sentinel otherwise.
      → done 2026-09-02 (/deferred quick fix): date-shaped or sentinel, test-first.
- [x] `distill_sessions.py::_read_jsonl` and `::iter_claude_ai` call `Path.read_text()` with no
      explicit `encoding='utf-8'`. On a non-UTF-8 default locale this could silently
      misclassify good transcripts as parse failures via the (now correctly caught)
      `UnicodeDecodeError` path, rather than reading them correctly. Fix: pass
      `encoding='utf-8'` explicitly at both read sites.
      → done 2026-09-02 (/deferred quick fix): encoding='utf-8' at all three read sites
      (a third, _digest_turns, was unrecorded) and on the digest write, which carried
      the same defect; pinned by a C-locale subprocess test.
- [x] `distill_sessions.py::slugify('')` returns `'session'`; two sessions from the same
      source with no title-bearing text at all (no user-turn text to slugify, no conversation
      `name`) collide on `session-<sess8>` in the output filename, and idempotence silently
      swallows the second. Narrow (requires a genuinely titleless, textless session) but
      unguarded.
      → retired 2026-09-02: the premise does not hold — the filename also carries each
      session's own sess8, so two titleless sessions land in distinct digests; pinned by
      test_two_titleless_sessions_do_not_collide, which passes on unchanged code. The
      neighbouring real hazard (the idempotence glob keys on sess8 alone, so two
      sessions sharing an 8-char id prefix would skip the second) is a separate,
      unrecorded item.
- [x] Adjudicated INTENDED-behavior, no action (recorded so it is not re-litigated): a
      generic hex-only high-entropy secret with no key-shaped prefix (no `sk-`, `ghp_`,
      `AKIA`, etc.) is caught by neither the distiller's `redact()` nor the `lint_wiki.py`
      backstop. Deliberate — widening the `high-entropy` class or the backstop to catch
      bare hex would also flag git SHAs, and `lint_wiki.py`'s `BASIS_OK_RE` requires a
      literal, intact SHA for `basis: git:<sha>` decision captures to pass their own lint.
      → retired 2026-09-02: an adjudicated no-action record, never work; plan 13 keeps
      the same class as plain bullets with no checkbox, and this entry stays readable as
      the not-re-litigated record.
- [x] Adjudicated INTENDED-behavior, no action (reviewer explicitly rejected this as a gap):
      the `claude-ai` adapter emits no tool-use traces even though the real export contains
      1770 `tool_use` content blocks. `claude-ai` conversations don't carry the same tool-call
      shape as Claude Code transcripts and adding trace synthesis for them was ruled
      deliberately out of this plan's scope, not a missed requirement.
      → retired 2026-09-02: an adjudicated no-action record (the reviewer rejected it as
      a gap), never work; kept only as the not-re-litigated record.

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
- [x] Zero-turn digest writing (a session with no narrative turns still gets an empty-bodied
      digest, per §16.5's "zero is a legitimate outcome") is untested beyond the guard the
      Task 5 fix pass added; no test asserts the empty-bodied file's actual header contents
      (e.g. `turns: 0`).
      → retired 2026-09-03: the premise no longer holds —
      `test_write_digest_zero_turns_keeps_sentinel_range_f2_guard`
      (`skills/llm-wiki/scripts/test_distill_sessions.py:196`) asserts exactly those header
      contents on a zero-turn session: `turns: 0`, the sentinel `dates: 0000-00-00/0000-00-00`
      range, `redactions: 0`, and `'**[' not in text` for the empty body. It landed in
      b0ef660 (2026-07-23), the same day this item was written.
- [ ] The Task 5 fix-pass regression test for the unbounded-slug fix (F1) asserts
      `len(name) < 255`; the real bound the `slugify(...)[:60]` fix guarantees is 83
      characters (10-char date + up to 60-char slug + hyphens + 8-char sess8 + `.md`) — a
      much weaker assertion than what the fix actually guarantees.
- [ ] Three Task 5 fix-pass tests construct a session with `project=None` but none asserts
      `'project:'` is actually absent from the written digest body.
- [ ] `slugify` and `_turn_date` have no test that calls them directly; both are exercised
      only indirectly through `write_digest`'s behavior.

Cosmetic:
- [x] A tool-only turn with no narrative text renders with a double space —
      `'**[03] assistant:**  [tools: Bash ×1]'` — because `write_digest`'s body-line f-string
      always inserts a space before the trace even when the redacted text is empty.
      → done 2026-09-02 (/deferred quick fix): non-empty parts joined by one space,
      test-first.
- [x] No blank line separates a digest's closing frontmatter `---` from its first body line.
      Cosmetic only: §16.4 imposes no such requirement, and `lint_wiki.py` never parses
      `raw/sessions/*.md` as frontmatter pages (`check_frontmatter_schema` only runs over
      `wiki/*/*.md`), so this cannot fail lint.
      → done 2026-09-02 (/deferred quick fix): blank line after the closing ---; a zero-
      turn digest is unchanged.
- [x] `test_distill_sessions.py`'s claude-ai tests are interleaved with a claude-code test
      rather than grouped together.
      → done 2026-09-02 (/deferred quick fix): the claude-code test moved up beside its
      siblings; 185 tests pass.
- [x] One Task 5 implementer report described its own self-review as "no issues found"
      immediately before re-review found 2 Important findings in the same task's diff — a
      report-accuracy note; the code was always independently re-verified regardless.
      → retired 2026-09-02: a report-accuracy observation with no action named; the code
      was independently re-verified at the time.

Spec/plan wording:
- [x] Spec's own §16.4 worked example (now `specs/completed/llm-wiki-spec.md`) shows
      `session: a3f2c9d1` (8 characters) in the digest frontmatter, but the shipped code
      always writes the full session UUID (`session: 81bf53fc-2687-4b61-80e6-359c50e3f047`),
      and the plan's own Task 5 test pins the full form. The plan deliberately diverged from
      the spec's illustrative example — the full id is arguably more useful, since the 8-char
      form is already in the filename — but nobody has gone back to correct the spec's now-
      stale example to match. Cosmetic; only the Idempotence bullet was amended at this
      completion (see plan 14 Post-execution), not this example.
      → done 2026-09-02 (/deferred quick fix): the example now shows the full id, with a
      note that the filename carries its first 8 chars.
- [x] Plan 14 Task 4's prose says the noise-removal rule drops "USER records that are pure
      tool-result plumbing"; the shipped `reconstruct` code applies the same
      empty-text/no-tools/no-compaction filter to *both* roles. The wider behavior is correct
      (an assistant turn consisting only of `thinking` blocks should also be dropped), so this
      is a wording defect in the retired plan's text, not a logic defect in the code.
      → done 2026-09-02 (/deferred quick fix): now "records of either role … (no text
      and no tool calls)".

Residual lint false positive (real corpus, precise, deliberately not chased further):
- [x] `lint_wiki.py`'s `assignment` secret pattern still scores 2 false positives on one real
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
      → retired 2026-09-02: recorded as deliberately not fixed; narrowing the pattern
      would reopen the plan-13 adjudicated no-`\b` decision, and a normal ingest already
      lints clean.

## 15-clean-code-family — 2026-07-24

- [ ] Ship `clean-code-python` user-level (`~/.claude/rules` → `~/Projects/agent-skills/rules`):
      deliberately not shipped — gate 2026-07-24 chose project-level only. Task 8's
      informational probe showed the user-level symlink DID load on Claude Code 2.1.218
      (contradicting issue #21858's silent-ignore report; probe transcript in commit
      7aa454f's body). Revisit if the always-on Python guardrails are wanted across work
      repos; mechanism is version-dependent, so re-probe on the then-current binary first
      (one `claude -p` probe against a scratch `probe.py`, per plan 15 Task 8 Step 5).

## 16-llm-wiki-specs-harvest — 2026-07-25
- [ ] Script-family hardening pass: unguarded `read_text()` in the walk loops and the unguarded per-file `sha_table()` `_git` call in `cmd_inventory` (skills/llm-wiki/scripts/distill_specs.py; same unguarded convention exists in distill_sessions.py / lint_wiki.py). Wrap in the house stderr+exit-1 style or settle the convention repo-wide.
- [ ] `_extend_brief` never renders directory-presence `note:` lines — same divergence class as the fixed is_deferred bug; reachable when dir notes change between two same-date runs (distill_specs.py).
- [ ] `files_walked:` header splice in `_extend_brief` assumes exactly one continuation line; a wrapping walk list would corrupt the header (distill_specs.py).
- [ ] Ticked q-entries bypass the square-bracket claim check (the q branch `continue`s before the check in `validate_entries`); hoist the check + red test (distill_specs.py).
- [ ] Brief missing `repo_path:` → `Path('')` → the drift check runs `git -C .` and warns about a foreign HEAD; should report "cannot check drift" instead (distill_specs.py).
- [ ] Hermetic `(also …)` render test: digest-renders-it / source-body-omits-it is currently pinned only by @needs_pilot tests that skip on machines without /Users/lowell/research-wiki (test_distill_specs.py).
- [ ] All-q ticked brief edge: stdout body is a bare newline while the digest preamble still points readers at a capture page that would have no captures (distill_specs.py).
- [ ] Required digest header keys are read with hard `[]` in `cmd_assemble` — a hand-edited brief missing e.g. `date:` raises KeyError instead of a `brief-error:` line (the write-nothing contract still holds) (distill_specs.py).
- [ ] `_repo_name` YAML-hostile residue: a zero-ASCII-word directory name containing `': '` still lands unquoted in the brief header (distill_specs.py).
- [x] Placeholder-less f-string in a test (`f'reports/harvest-wt-2026-07-24.md'`); fold into any future style sweep (test_distill_specs.py).
      → done 2026-09-02 (/deferred quick fix).
- [x] Also-line sha shape gate (`ALSO_RE` swallowed a non-hex `(also … · sha:)` into the location text) → done post-merge in afa9af8.
- [ ] Renamed spec files lose `previously seen` hinting (prior keys grouped by the old at:-path, looked up by the new walk path); agent-side dedup still reads the whole prior brief, so impact is weaker hints only — decide whether rename-following is worth building (distill_specs.py).
      → decided 2026-09-03 (/deferred): yes, build it. The open decision is closed, so
      this is no longer a design item — it joins the `distill_specs.py` hardening pass
      as ordinary planned work. Still unticked: the decision is made, the work is not.

## 17-agents-and-commands-expansion — 2026-07-25
- [x] PreToolUse hooks mechanically enforcing the read-only contracts of
      `security-auditor`, `Explore`, and `test-runner` (spec "Out of scope",
      recorded deliberately): today the contracts are prose, matching the
      code-reviewer/task-reviewer precedent. Would need a hook design with
      per-agent matchers; touches agents/*.md and settings wiring. See
      specs/completed/agents-and-commands-expansion.md.
      → done in plan 24. Two corrections to the item as recorded: the guard covers
      all **five** read-only agents, not three — the code-reviewer/task-reviewer
      precedent carries the same contract and the same tool list, so guarding three
      of five would ship an unmotivated asymmetry. And "per-agent matchers" are not
      available: `PreToolUse` `matcher` keys on tool name, so agent discrimination
      happens inside the script, reading `agent_type` from the payload.
- [x] `disable-model-invocation` lint (final-review Important, gate-deferred):
      `check_command_file` in build/check_frontmatter.py validates only
      `description`, so nothing guards the key the commands' listing-budget
      motivation rests on — and pre-existing commands/deferred.md lacks the
      key entirely. TDD a check (Task-1 precedent) and decide /deferred's
      status as part of the same work: add the key there, or make the check
      per-file.
      → done 2026-09-02 (/deferred quick fix): check_command_file requires the YAML
      boolean true, test-first; commands/deferred.md carries the key.
- [ ] Agent description length cap (final-review Minor): `check_skill`
      enforces the 1024-char cap but `check_agent_file` caps nothing, and
      all agent descriptions load into the Agent-tool listing (current
      roster: 261–445 chars each). Add a cap to build/check_frontmatter.py
      when the roster grows.

## 18-methodology-pipeline-skills (plan #1, describe-critique-methodology) — 2026-07-26
- [ ] **DL/NLP domain extension for the methodology templates (spec Req 15,
      v1 scope boundary — deliberately not built).** v1's templates are
      statistical/Bayesian/nowcast only and carry no DL/NLP slots. The
      sketched extension is *conditional* slots rather than new mandatory
      ones: "if trained → training objective (loss, optimizer, schedule)";
      "if pipeline-assembled → assembly policy (what calls what, with which
      prompts/thresholds)". Known breakage cases the current six slots
      handle badly: a **RAG system** has no estimation procedure at all —
      its methodology lives in retrieval/chunking/reranking assembly
      choices, which the "Estimation / inference procedure" slot cannot
      hold; a **fine-tuned classifier** has no data-generating story in the
      generative sense (the story is dataset construction + label
      provenance); and checkpoint / tokenization / schedule details have no
      slot yet are methodologically load-bearing. Build only when a real
      DL/NLP target needs describing — speculative slots would dilute the
      stats-tuned wording that MT1 showed is doing the work.
- [ ] **In-session SOTA pass as a Chat-Research alternative (spec "Out of
      scope").** Today Describe mode always hands off to an external Claude
      Chat session with Research enabled. An in-session variant — WebSearch
      + paper search + an llm-wiki query — would close the loop without
      leaving Claude Code, at the cost of the interactive push-back /
      adjudication that makes the Chat critique valuable. Revisit after the
      user has run a few real round-trips and can compare critique quality;
      the spec's Req 13 round-trip is the natural evidence source.
- [ ] **Synthesize mode has no scenario verification (spec Req 13,
      gate-deferred).** MT2 proved the mode is *routed to* correctly (5/5
      across three treatment arms) but nothing tests its *behavior* once
      entered — triage-table-before-spec-text, locator discipline, the
      derive-roadmap handoff. It ships consciously untested. The fixture
      that would test it is the real critique from the user's round-trip;
      fold this into plan #2 rather than synthesizing a strawman critique.
      **Partially closed 2026-07-26** (spec Amendment A): the real round-trip
      arrived, and a three-arm subagent check now covers adjudication-status
      detection. Still untested once entered: locator discipline, the
      triage-table-before-spec-text ordering, and the derive-roadmap handoff.
- [ ] **Partial adjudication has no explicit handling.** The skill frames
      adjudication status as binary — "was the critique adjudicated at all?"
      — but a real critique can record push-back on a handful of points and
      none on the rest. Observed in the Amendment A arm-C check: given a
      fixture with 2 adjudicated points out of ~30, both agents diagnosed the
      split unprompted, inherited the two recorded rejections, and adjudicated
      the remainder themselves — the correct behavior, reached without
      guidance. Deliberately NOT added to the skill text on that evidence
      (writing-skills: do not add guidance for a failure mode that did not
      occur). Revisit only if a real critique produces a mishandled split.
      One genuine hazard the same check surfaced, also handled unprompted: a
      withdrawn point can survive elsewhere in the document (the fixture's
      withdrawn X-13 recommendation still stood in the Recommendations block),
      so a withdrawal must be carried to every site, not just the paragraph
      recording it. Worth a clause if it recurs.
- [ ] **`suspicious_notation` false positives on acronym subscripts.** After
      the LaTeX fix, uppercase-acronym math symbols (`NSA_t`, `TOT_c`,
      `NSA_v` — from `G^{\mathrm{NSA}}_t`) are reported as
      identifier-shaped. They are correct-by-the-documented-rule (advisory,
      human-read) and appeared in both the micro-tests and the full run, so
      the noise is predictable rather than alarming. If it becomes
      irritating, exempt all-uppercase segments of ≤4 chars — but only with
      a test proving a genuine uppercase identifier still warns.

## 19-methodology-pipeline-skills — 2026-07-30

- [ ] **The stage-stamp lifecycle carrier is unbacked.**
      `skills/derive-roadmap/references/roadmap-format.md` and
      `skills/describe-critique-methodology/references/spec-synthesis.md` both assert
      that writing-plans copies a spec's Rollout note verbatim into the stage plan's
      header, and that "that copy is the whole carrier." `grep -rn -i "rollout"
      skills/writing-plans/` returns zero matches; what writing-plans actually has is a
      generic rule to copy the spec's project-wide requirements into the plan's Global
      Constraints block. Req 10 deliberately rejected a writing-plans protocol edit for
      v1 for this iteration (provenance-touching, needs its own RED cycle), naming the
      one-line hook as the recorded fallback "if the carrier proves fragile." Owner's
      decision: defer, and let the first real stage cycle settle it.
- [x] **A stranded roadmap artifact.**
      `/Users/lowell/Projects/alt-nfp/specs/usable-series-selection-roadmap.md` was
      named from the spec's H1 title, a convention now superseded by the skill's
      filename-stem `<name>` rule (landed post-review, commit `c818893`). Either rename
      it to the canonical stem-derived name or consciously accept the divergence. Not a
      skill defect — the shipped header-based collision guard (`a2d4f1f`) finds this
      artifact regardless of filename, which a 3-rep behavioral check confirmed 3/3.
      → retired 2026-09-03: the artifact is no longer live — it was retired to
      `alt-nfp/specs/completed/` on 2026-08-02 (f87a134, 89c8b7f), where a stem-named
      `usable_series_methodology_roadmap.md` now sits beside it. Renaming a retired
      artifact settles no convention, and the collision guard finds it either way.
- [x] **No non-interactive fallback for the batched-question checkpoint**
      (`skills/derive-roadmap/SKILL.md` §1, `references/gap-rubric.md`). A sub-agent run
      parked its questions in the artifact instead of asking. Degraded safely, since the
      §4 human checkpoint still gates before Stage 1. Would take one sentence: when the
      session cannot ask, the questions go in a clearly-marked block and the artifact is
      marked provisional.
      → done 2026-09-02 (/deferred quick fix): one sentence at both sites (SKILL.md §1
      and gap-rubric.md). Checked with 2 unattended Sonnet reps on a neutral greenhouse-
      log fixture: 2/2 wrote a top PROVISIONAL banner and a marked Open-questions block
      ahead of any stage text, kept the §4 checkpoint, and read none of this repo's
      specs.
- [ ] **The roadmap format cannot express parallel stages**
      (`skills/derive-roadmap/references/roadmap-format.md`). The gold master's own
      sequencing wants it ("Req 5 Stage-A audit starts in parallel"). Deferred because
      `Consumes:` already carries the dependency information, so parallelism is
      derivable rather than lost.
- [ ] **Two of the skill's own checkpoints have no behavioural evidence.**
      `skills/derive-roadmap/SKILL.md` §1's batched question set and §4's human approval
      before Stage 1 both require an interactive turn; every test in this plan ran
      non-interactively, so neither was exercised.
- [ ] **The RED baseline for this skill is confounded and could be re-run cleanly.**
      Both leak channels are now closed (the fixture is name-neutralisable, and the
      shared task list no longer names the work). A clean round would settle whether
      E1–E5 are genuinely unobserved, which is what the kept-as-is SKILL.md guidance
      rests on. See specs/plans/completed/19-methodology-pipeline-skills.md (Task 1) for
      the full method.
- [x] **Req 12's `/context` residency check** → discharged 2026-07-30, same day. The owner
      ran `/context`: the skill listing reports **12.8K tokens, 1.3%** of the window. That
      implies a ~1M-token window, so `skillListingBudgetFraction: 0.025` allows ~25K and
      the listing uses about half of it — no drop-by-rank pressure, nothing evicted.
      Residency of `derive-roadmap` itself is separately confirmed: it appeared in the
      live available-skills listing immediately after creation, and the mechanical half
      holds (30 skills in the repo == 30 installed, zero dangling symlinks).
      Note for future budget work: a chars/4 estimate of name+description came to ~5.1K
      and badly understated the real 12.8K, so the listing carries substantial per-entry
      overhead beyond the description text — measure with `/context`, don't estimate.
- [x] **The `/deferred` boundary is asserted in only one place.**
      `skills/derive-roadmap/references/gap-rubric.md` states that live roadmap stages
      are out of `/deferred`'s scope; `commands/deferred.md` says nothing either way.
      Spec Req 10 mandates recording the boundary, which is satisfied — but the two
      could drift.
      → retired 2026-09-02: commands/deferred.md now states the roadmap boundary in its
      Scope paragraph (same session as this retire), so the two records can no longer
      silently diverge.
- [x] **Two uncommitted artifacts in `/Users/lowell/Projects/alt-nfp`**, left there
      deliberately because this work has a standing no-git waiver for that repo:
      `specs/usable-series-selection-roadmap.md` (this plan's verification output) and
      `specs/nfp-model-methodology.md` (plan 18's Describe-mode output). Committing them
      is the owner's call in that repo.
      → retired 2026-09-03: the owner made the call — both files are committed in
      alt-nfp as of 2026-08-02 (f87a134, 89c8b7f) and now live under
      `specs/completed/`. `git -C ../alt-nfp status --short -- specs/` is clean.

## 20-bayesian-workflow-book-integration — 2026-09-03
- [ ] Split the durable Δ-ECDF reading rule from the arviz-plots-1.3.1-specific notes
      (final-review Minor, triaged defer): the "What that call actually draws" paragraph in
      `skills/bayesian-workflow/references/model-criticism.md` (SBC section, ~line 189) is one
      ~10-sentence block of version-pinned detail (the `rcParams["stats.envelope_prob"]` fallback,
      the `method="envelope"` deprecation warning, a TypeError seen on this stack). Accurate
      today, and its accuracy is the point; when the pot_c/envelope situation settles upstream,
      keep the one durable instruction (read the p-value and the highlighted points, not a
      picture of a band) and shrink the version notes to a clause.
- [x] `sbc_rank` sketch breaks on scalar parameters (final-review Minor; pre-existing and
      re-shipped verbatim by plan 20's own replacement text): in
      `skills/bayesian-workflow/references/model-criticism.md`, `draws[..., idx]` and
      `theta_true[idx]` assume a vector site — for a scalar site `draws` is 1-D and
      `theta_true[idx]` raises on a 0-d array. Fix by running it (this skill's history,
      c707a48, is a recipe that shipped unrun): e.g. `np.atleast_1d` on both, plus the scalar
      case in the prose.
      → done 2026-09-03 (/deferred quick fix): fixed and, per the item's own instruction,
      actually run. **The recorded remedy above is wrong — do not follow it.** `np.atleast_1d`
      on both is a no-op on a scalar site's `(L,)` draws array, so `draws[..., idx]` still
      indexes the *draw* axis: 200 replications returned only {0, 1} (chi2 = 1901.9, p = 0.000).
      Shipping it verbatim would have traded a loud crash for a silently wrong SBC conclusion.
      The fix needs a second guard, `draws.reshape(draws.shape[0], -1)`, alongside the
      `atleast_1d`. Verified by extracting the sketch text from the edited file and executing
      it: scalar and vector sites both return well-spread ints in [0, L]. The 11 bayesian-
      workflow script tests still pass. Standing gap, not closed: no bundled suite covers this
      reference file, so the recipe can regress silently again.


## 21-audit_9_2_26 — 2026-09-03
- [ ] `skills/bayesian-workflow/scripts/calibration_check.py` still has no test
      (audit H1). Owned by no plan: plan 20's scope fence excluded the file and
      plan 21 left it out because the suite needs the full
      arviz/arviz-plots/arviz-stats chain and the script is mostly ArviZ
      delegation. Would take a fixture InferenceData with a known
      over-/under-confident posterior plus assertions on
      `assess_calibration`'s five returned keys. Confirmed at the 2026-09-03
      gate as a deferral, not an accepted permanent gap.
- [ ] `skills/tech-debt/scripts/scan.sh` has no test (audit H1). Deferred on
      cost: it needs fixture repositories with planted debt signals (a magic
      seed, a hardcoded /Users/ path, an unvalidated join, a committed .env) and
      assertions per section. Highest cost, lowest marginal value of the five
      untested scripts.
- [x] Audit H4 — loose files inside skill directories: `README.md` in three
      skills, `writing-skills/`'s five support docs at top level while it
      prescribes `references/` for everyone else, `systematic-debugging/`'s four
      technique files plus `find-polluter.sh`. No behaviour impact; recorded as
      a finding only, confirmed at the 2026-09-03 gate.
      → retired 2026-09-03: records a no-action finding, not work. `find skills
      -maxdepth 2 -name '*.md' -not -name SKILL.md -not -path '*/references/*'`
      returns 18 files across ~10 skills — broader than the three named here, and
      each is cross-referenced by path from its SKILL.md, so normalizing them is
      churn with no behaviour change. Accepted as the repo's layout.
- [ ] Audit H2 — `skills/geographic-codes/scripts/build.py:210` emits 7 polars
      `FutureWarning`s through the fastexcel engine (`pl.read_excel(...).select(...)`;
      polars 2.0 changes the `from_arrow` return type). Harmless until then; the 7
      `test_parse_each_bundled_delineation_workbook[*]` cases are the canary.
      Re-run the suite when polars 2.0 lands.
- [ ] Audit W1 — the skill-listing budget is near its cap (32 descriptions
      ≈ 4,940 est. tokens against ≈ 5,000 at `skillListingBudgetFraction`
      0.025). All 32 fit today; the next skill likely tips it into
      drop-by-rank. Standing decision unchanged — the lever is the fraction
      (≈ 0.03) or per-project scoping, not trimming descriptions. Check
      `/context` before skill #33.
- [x] Audit scorecard rubric weights were never ratified (audit "Decisions for
      you" item 5): the S dimension's 2,500-word threshold and the V evidence
      ladder are the auditor's calls. The notes column stands regardless.
      → retired 2026-09-03: nothing downstream consumes the weights. The rubric exists
      only inside the retired `specs/completed/audit_9_2_26.md` and
      `specs/plans/completed/21-audit_9_2_26.md`; no skill, script or lint reads it, and
      the item's own text concedes the notes column stands whatever the weights are.
      Ratifying a rubric with no consumer is ceremony, not work.
- [x] `NOTICE`'s superpowers block pins the vendoring date (plan 21 Task 3) but
      its "Changes from upstream" list is incomplete — `sdd-workspace`,
      `task-brief` and `review-package` arrived in `2f283ae` and were changed
      locally afterwards by `c5ff0b5` (`.superpowers/sdd/` → `.sdd/`) and
      `b8faf9c` (trailing-section leak; Global Constraints prepend), neither of
      which is listed. Not an attribution defect — the blanket "modifications
      are by Lowell Mason" clause covers it — but H3's whole purpose was to make
      drift reviewable, and an incomplete change list undercuts the pin.
      → done 2026-09-03 (/deferred quick fix): the change list gained the three scripts,
      `c5ff0b5` and `b8faf9c`, after the history was re-checked against the item's account.
      A second, unrecorded inaccuracy surfaced and was fixed in the same pass: the block
      claimed the vendored files "never matched any upstream commit byte for byte", which is
      false for exactly these three — fetching each from `obra/superpowers` at `896224c` and
      hashing against the as-vendored blobs shows all three identical. Note the gates cannot
      see any of this: `check_provenance.py` never parses the change list.
- [x] `skills/explore-data/scripts/test_profile.py` — the plan's mutation check
      (Task 5 Step 3) proved the suite detects a renamed `"column"` key, but not
      the way it claimed: `quality_flags` reads `r["column"]` at
      `profile.py:261,263` before JSON is written, so the CLI crashes and three
      of four failures are `CalledProcessError`, never the contract assertion at
      `:65-70`. A serialization-boundary-only rename would exercise the
      silent-drift tripwire on its own terms.
      → done 2026-09-03 (/deferred quick fix): the tripwire was tested and it works. A
      serialization-boundary-only rename fails on the contract assertion itself
      (`AssertionError`, extra item 'column'), not on `CalledProcessError`; the naive rename
      at `column_profile` reproduces the item's account exactly (3 × `CalledProcessError`
      plus one `KeyError`). `profile.py` was restored byte-for-byte (`git diff --exit-code`
      clean), so the code change is nil and only the test's docstring gained the finding.
      The mechanism is *ordering*, not copying: every internal reader of the key runs before
      the JSON write. An earlier draft of that docstring asserted a false cause and was
      corrected before ticking.
- [x] `skills/design-architecture/scripts/new_adr.py:6` promises numbering
      "permanent and never reused". `test_new_adr.py` pins the gap case (delete
      `0002-`, next is still 4) but not the full-reset case: delete every file
      and `next_number` returns 1, reusing a number. That is the scenario most
      counter to the docstring's literal claim; closing it means changing
      `new_adr.py` (persist the high-water mark) or narrowing the docstring.
      → done 2026-09-03 (/deferred quick fix): docstring narrowed rather than adding a
      persisted counter — a state file is the wrong price for a scenario (deleting every ADR)
      that contradicts ADR practice. The full-reset case is now pinned by a test named for
      the real contract, that numbering derives from the directory. Two rounds were needed:
      the first replacement still overpromised ("never reused while earlier ADRs remain on
      disk"), which is false when only the *highest* ADR is deleted — 0001–0003 present gives
      4, deleting just 0003 gives 3. `SKILL.md` keeps its permanence sentence, reworded as a
      convention the author upholds rather than a guarantee the scaffolder enforces.
- [x] `skills/subagent-driven-development/scripts/test_sdd_scripts.py` coverage
      gaps: `task-brief`'s level-termination (`hlevel($0) <= tlvl`) is exercised
      only via fenced content, with no deeper-sub-heading case (a `#### Sub`
      inside a task must be *retained* as content); and two exit-2 arms are
      untested — `review-package:21` (`bad HEAD`; only `bad BASE` is covered)
      and `task-brief:13`'s `$# -gt 3` arm (only `$# -lt 2` is covered).
      → done 2026-09-03 (/deferred quick fix): all three arms added, 11 tests → 14, each
      mutation-checked against the bash line it targets and the three scripts confirmed
      byte-identical afterwards. The `bad HEAD` test pins the message, not just the exit code.
      Still untested and worth a future item: the *operator* boundary at `task-brief:48` —
      changing `<= tlvl` to `< tlvl` leaves all 14 green, because `### Task 2` is terminated
      by the Task-heading rule before the level comparison is consulted. `CLAUDE.md`'s test
      counts were synced in the same pass (this suite 11 → 14, design-architecture 8 → 9).

## 22-sdd-hardening — 2026-09-03
- [x] M1 — `skills/subagent-driven-development/scripts/test_sdd_scripts.py:89-144`:
      basename stripping is never exercised. Every workspace test passes a
      root-level plan (`plan.md`), so a bug that resolved a nested plan path
      (e.g. `specs/plans/22-x.md`) into the wrong slug — `.sdd/specs/plans/22-x/`
      instead of `.sdd/22-x/` — would still pass every existing test. Add a case
      that calls `sdd-workspace` with a plan path containing directory
      components and asserts the workspace is named from the basename alone.
      → done 2026-09-03 (/deferred quick fix): added
      `test_workspace_is_named_from_the_plan_basename_alone`, which passes the
      relative form a controller actually types. Verified RED against a
      deliberately broken `slug=${plan%.md}`: it produced exactly the predicted
      `.sdd/specs/plans/22-sdd-hardening`.
- [x] M2 — `skills/subagent-driven-development/scripts/sdd-workspace:31`
      (`slug=$(basename "$plan" .md)`): basename slugs collide across
      directories — two different plans sharing a basename in different
      directories (e.g. `specs/plans/7-x.md` and an archived or worktree copy
      at another path) would resolve to the same `.sdd/<slug>/` and share a
      ledger. The script relies on this repo's convention that plan ids are
      unique across `specs/plans/` and `specs/plans/completed/`; nothing
      enforces that. Worth a one-line comment recording the assumption, not a
      behavior change.
      → done 2026-09-03 (/deferred quick fix): comment added above
      `sdd-workspace:31`, pointing at the ledger's `Plan:` first line as the
      mitigation that makes a collision visible.
- [x] M3 — `skills/subagent-driven-development/scripts/test_sdd_scripts.py`
      mixes quote styles: the lines Task 1 rewrote use single quotes (this
      repo's Python convention, CLAUDE.md), the lines it didn't touch still use
      double. Whole-file normalization pass to single quotes.
      → done 2026-09-03 (/deferred quick fix): 128 literals converted under an
      `ast.dump()` equivalence guard. Docstrings keep `"""` per Python
      convention, and one literal containing an apostrophe stays double-quoted
      rather than growing an escape.
- [x] M5 — several sites describe `scripts/review-package` as printing "the
      path" when it actually prints `wrote <path>: N commit(s), M bytes`. Two
      say so explicitly and are confirmed misstatements:
      `skills/subagent-driven-development/task-reviewer-prompt.md:267`
      ("`scripts/review-package PLAN_FILE BASE HEAD` prints the unique path
      it wrote") and `skills/requesting-code-review/code-reviewer.md:165`
      ("`scripts/review-package PLAN_FILE BASE HEAD` prints it"). Several more
      sites in `skills/subagent-driven-development/SKILL.md` (File Handoffs
      at `:330`, Example Workflow at `:452`/`:469`, Red Flags at `:545`) say
      "pass"/"name the printed path" without stating the format either way —
      same silent bare-path assumption, softer wording; grep `review-package`
      across those files to enumerate the full set the original review's
      "five sites" count referred to before fixing. PRE-EXISTING — plan 22
      Task 1 did not change the print format, and no task in this plan owned
      this text; the controller ruled it out of scope at Task 2's review (not
      in the spec, no task named it). A controller who pastes the raw stdout
      line verbatim into a dispatch hands the reviewer a malformed path (the
      `wrote ` prefix and `: N commit(s), M bytes` suffix are not part of the
      path), so this should not sit indefinitely. Each fix is a one-line
      wording correction.
      → done 2026-09-03, on the same branch: the File Handoffs contract now
      states the format once and authoritatively (`wrote <path>: <N> commit(s),
      <M> bytes`) with the instruction to take the path out of it rather than
      paste the line, and the three placeholder definitions that implied a bare
      path — `task-reviewer-prompt.md`'s `[DIFF_FILE]`, `code-reviewer.md`'s
      `[DIFF_FILE]`, and `re-review-prompt.md`'s `<DIFF_FILE>` — now say the
      script reports it in a summary line and that the path alone is passed.
      `SKILL.md`'s DONE handler, Red Flags bullet, and both Example Workflow
      brackets were reworded to match. A grep for `printed path`, `prints it`,
      `prints the unique path`, and `path printed by` across `skills/` and
      `agents/` now returns nothing.
- [x] M6 — the Short Form of
      `skills/subagent-driven-development/task-reviewer-prompt.md` now ships
      the no-nested-subagent ban ("## You Do Not Dispatch Subagents") twice
      per dispatch: once inline in the form itself, once from
      `agents/task-reviewer.md`, which the Short Form exists to defer to.
      ARGUABLY A FEATURE, not a defect worth fixing: this same plan's Task 5
      fix round found live evidence that a dispatched task-reviewer agent
      falls back to its own definition's report format when a prompt doesn't
      explicitly suspend it — re-reviews earlier in this plan's own execution
      came back in the full report shape until `re-review-prompt.md` was
      fixed to say so explicitly (see plan 22 Task 5's deviation note).
      Redundant ban text is cheap insurance against that same failure mode
      recurring here. Recorded so a future reader does not "fix" the apparent
      duplication by stripping the inline ban text out of the prompt
      templates as dead weight: that same inline text is the ONLY copy on the
      Full Form path, used specifically when `agents/task-reviewer.md` is not
      installed and dispatch falls back to `general-purpose` — removing it
      there would silently leave that path with no ban at all.
      → retired 2026-09-03: the item's own verdict is "not a defect worth
      fixing"; it exists to warn, and the warning survives ticked. THE WARNING:
      the inline ban at task-reviewer-prompt.md:43 (Short Form) and :115 (Full
      Form) is the ONLY copy on the Full Form path, which runs when
      agents/task-reviewer.md is absent and dispatch falls back to
      general-purpose. Do not strip it as duplication.
- [x] M7 — `## You Do Not Dispatch Subagents` is Title Case in
      `agents/task-reviewer.md` and `agents/code-reviewer.md`, both of which
      otherwise use sentence-case section headings (`## Read-only contract`,
      `## Reading the diff`, `## Do not trust the report`, etc. — single-word
      headings like `## Calibration` are case-neutral). `agents/task-reviewer.md`
      already has one other Title Case heading, `## Batched Dispatches`
      (added by this same plan's Task 4), so this is now the second
      exception rather than the only one. The three prompt templates that
      carry the ban heading
      (`skills/subagent-driven-development/implementer-prompt.md`,
      `skills/subagent-driven-development/task-reviewer-prompt.md`,
      `skills/requesting-code-review/code-reviewer.md`) use Title Case for it
      too, so only the two agent files' own local convention is at odds with
      it. One-word-casing fix, or accept Title Case as the convention for
      these two cross-cutting rule headings and move on.
      → done 2026-09-03 (/deferred quick fix): resolved as per-file convention.
      `## Batched Dispatches` → `## Batched dispatches` in agents/task-reviewer.md
      (that file is sentence-case throughout). The ban heading KEEPS Title Case
      in both agent files: it appears verbatim in six files as a fixed rule name.
      Also checked and deliberately left alone — task-reviewer-prompt.md carries
      `## Batched Dispatches` at :59 and :131, and that file is Title Case
      throughout (`## What Was Requested`, `## Output Format`), so it is already
      locally consistent.
- [x] M10 — the batched-dispatch ledger example in
      `skills/subagent-driven-development/SKILL.md`'s Durable Progress section
      shows a contiguous range (`Tasks 4-7: complete (batched; commits
      <base7>..<head7>, review clean)`), but the rule it illustrates
      generalizes to any batch, including a non-contiguous one (e.g. tasks 2,
      5, and 9 batched together). The example doesn't show what notation a
      non-contiguous batch uses. Add a second example or a parenthetical.
      → done 2026-09-03 (/deferred quick fix): SKILL.md's Durable Progress bullet
      now states the range is shorthand for a contiguous batch, not the required
      form, and shows `Tasks 2, 5, 9: complete (batched; …)`.
- [x] M13 — `.sdd/task-6-report.md`'s rationale for the `review-package`
      argument-order clause claimed the spec was silent on matching
      upstream's argument order; `specs/completed/sdd-hardening.md`'s
      Decisions section actually says it matches upstream. Report-accuracy
      only — the shipped `NOTICE` text itself is correct and needed no change.
      → no action needed (2026-09-03): a report-accuracy observation with no
      code or doc defect behind it; recorded so it is not re-litigated.
- [x] Adjudicated INTENDED-behavior, no action (final whole-branch review
      recommendation, verified and corrected against the shipped state
      rather than transcribed as-is): the no-nested-subagent ban
      ("## You Do Not Dispatch Subagents") was byte-identical prose across
      five reviewer-seat locations right after Task 3 landed — both forms of
      `skills/subagent-driven-development/task-reviewer-prompt.md`,
      `skills/requesting-code-review/code-reviewer.md`,
      `agents/task-reviewer.md`, and `agents/code-reviewer.md` — which this
      repo's own pre-flight review rubric would ordinarily flag as verbatim
      duplication to extract into a shared reference.
      `implementer-prompt.md` was never part of that set; its ban is
      implementer-framed prose that always read differently. Checked against
      the actual current files rather than taken on the recommendation's
      word, because it is no longer fully byte-identical: the final-review
      fix round (`e135234`, resolving GATE-Q1) generalized the evidence-rule
      paragraph's "the implementer's report" wording to "any input material
      this dispatch hands you" for the two code-reviewer seats only
      (`agents/code-reviewer.md`, `requesting-code-review/code-reviewer.md`)
      — plain `requesting-code-review` has no report input to point at, so
      the original wording risked a spurious missing-artifact finding there.
      The two task-reviewer seats (`agents/task-reviewer.md`, both forms of
      `task-reviewer-prompt.md`) kept the original wording, where the report
      is an established input. Still deliberately not extracted into one
      shared reference, and the split is itself a reason why: each file is a
      distinct dispatch path (implementer vs. task reviewer vs. code
      reviewer, Short Form vs. Full Form vs. agent definition, per-task vs.
      whole-branch review), these two reviewer-seat wordings have already
      diverged once for a real reason and may again, and the prose is what
      travels when the agent definitions are not installed (see M6 above) —
      a shared reference would go unread on the paths that most need the
      ban, and would force one wording onto two seats that just proved they
      need different ones. Recorded so a future reader does not factor this
      out as cleanup, and does not cite "byte-identical across five files"
      as current fact — it described the state immediately after Task 3,
      before the same review cycle's own fix round split it.

## 23-lint-wiki-citation-contract — 2026-09-03

Both items are deliberate design consequences recorded as "Accepted limitations" in
`specs/completed/lint-wiki-citation-contract.md`, not oversights. The structural clause
is where the design deliberately concentrates error risk, and these are its two
residuals. The fix in each case is a new WARN severity, which the spec explicitly
declined as YAGNI (zero instances in a one-page wiki).

- [ ] A well-formed slug with a malformed position is silently unrecognized —
      `[robnik-2022-mclmc see this]` is read as prose, so a real citation goes
      uncounted and unvalidated. The symmetric residual of requiring both predicates.
      Pinned as a test today (`test_is_citation`, the `shape, bad position` row) so the
      behavior is deliberate rather than accidental. To fix: add a WARN when the token
      passes `SLUG_SHAPE_RE` or membership but the position does not parse. Touches
      `skills/llm-wiki/scripts/lint_wiki.py` `check_links`.
- [ ] Prose whose first token is hyphenated or year-bearing and whose remainder opens
      with a position sigil hard-errors — `[well-known Table 2]` (acceptance case 18,
      pinned as an expected ERROR). Contrived; the escape is to not bracket it. Same
      file; the fix would be a curated stop-word list or a WARN, both rejected as
      inventing contract the wiki has no content for.
