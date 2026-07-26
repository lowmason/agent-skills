---
name: describe-critique-methodology
description: >
  Use when writing a system- or module-level methodological description of a
  codebase for external critique, or when a critique returns from that
  round-trip. Describe mode: "describe the methodology", "write up the model
  or math independent of the code", "methodological description", "prepare a
  document for external or SOTA critique" — statistical, Bayesian, nowcast,
  NumPyro, state-space, estimation or inference procedures. Synthesize mode:
  a saved specs/*-critique.md returning from a Claude Chat Research
  round-trip, "the critique is back", "synthesize the critique into a spec".
  Not for new-functionality ideas — that is brainstorming. The critique
  itself happens externally in Chat Research — this skill is not for
  reviewing code or specs. The description is math and prose decoupled from
  code — not a code walkthrough, README, or analysis writeup.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# describe-critique-methodology

## Overview

Two modes, one round-trip. **Describe mode** writes a methodological
description of an existing system — math and prose deliberately decoupled
from the code — and hands it to an external Claude Chat Research critique.
**Synthesize mode** receives the returned critique and folds description +
critique into a house-format specification, which the derive-roadmap skill
turns into staged work.

**Core principle:** the description names concepts, never code. The external
reviewer must critique the METHOD; every smuggled identifier pulls the
critique toward the implementation instead.

**Mode selection:** if `specs/<name>-critique.md` exists beside
`specs/<name>-methodology.md` in the target repo, you are in Synthesize
mode. Otherwise, Describe mode.

## Describe mode

1. **Choose granularity up front** — module (one estimand, one procedure) or
   system (composed components) — and announce the choice and the target.
   If `$LLM_WIKI_ROOT` is set, run the pre-flight in
   `references/wiki-touchpoints.md` first.
2. **Write `specs/<name>-methodology.md` in the target repo** using the
   matching template shape in `references/methodology-template.md`. Every
   slot is REQUIRED. Write from the notation table outward: define every
   symbol first, then write every equation and sentence in those symbols.
   The moment a code identifier — a function, file, variable, class, or
   package name — appears in your draft, define a symbol or role-name for
   the concept in the notation table and use that instead. Components are
   named by methodological role ("the private-sector state-space leg"),
   sections by the template's slots — never by the package or file layout.

   **Hard rule: never delegate the description to the docs-writer agent.**
   Its grounding rule — read the code, verify every claim against source —
   is anti-decoupling by design. Write the description yourself, in-session.
3. **Self-check, then advisory validator.** Walk the template slots (all
   present; notation closed — every symbol used is defined). Then run:

   ```bash
   python3 <this-skill-dir>/scripts/check_decoupling.py specs/<name>-methodology.md
   ```

   Its output is review input: fix real smuggling, keep legitimate notation.
   Read its `[notation-table]` warnings too — a smuggled identifier does not
   become notation by being defined in the table. Never iterate to zero
   findings for its own sake — it is not a gate.
4. **Commit, then hand off.** Commit the description in the target repo,
   then deliver this message verbatim (filling `<name>` and paths):

   ```
   Methodology description committed at specs/<name>-methodology.md.
   Next: the external critique round-trip —
   1. Open a Claude Chat session with Research enabled; use the prompt in
      references/critique-prompt.md (in this skill's directory), attaching
      the committed description.
   2. Run the review interactively — push back, steer, adjudicate.
   3. Have Chat write the final critique per that prompt's rules; save it
      as specs/<name>-critique.md beside the description, and commit it.
   When the critique is saved, start a fresh session and say:
     "The critique is back — use describe-critique-methodology
      (synthesize mode) on specs/<name>-critique.md"
   ```

   Then stop. The critique session is the human's, in Chat — not yours.

## Synthesize mode

1. **Staleness check** (scripted): say "Description committed <date/sha> —
   has the methodology moved since? Checking git log touching the described
   system since that commit." If it has moved materially, refresh via
   Describe mode before synthesizing — the critique may target a stale
   method.
2. **Critique triage.** Build the per-point table per
   `references/spec-synthesis.md` — accept / reject / needs-user-adjudication
   with a one-line rationale each — and present it as ONE batched question
   set before writing any spec text.
3. **Synthesize the spec** at `specs/<name>.md` in the target repo, per
   `references/spec-synthesis.md`: house skeleton, per-claim locators back
   to the description (§) and critique (C#).
4. **Open the spec with the routing header** (verbatim in
   `references/spec-synthesis.md`) naming derive-roadmap as the required
   next skill.
5. **Self-review**: placeholders, internal consistency, scope, ambiguity —
   fix inline.
6. **User gate** (scripted): "Spec synthesized and committed at
   specs/<name>.md — please review it before it moves to roadmap
   derivation."
7. **On approval, hand off**: recommend a fresh session invoking
   derive-roadmap on `specs/<name>.md`, then stop. If derive-roadmap is not
   installed yet, say so and stop — do not improvise a roadmap or plan the
   spec directly.
   If `$LLM_WIKI_ROOT` is set, also make the one-line suggestion in
   `references/wiki-touchpoints.md`.

## Quick reference

| You have | Mode | Output |
|---|---|---|
| A system/module to describe for external critique | Describe | `specs/<name>-methodology.md` + handoff message |
| A saved `specs/<name>-critique.md` back from Chat Research | Synthesize | Triage table → `specs/<name>.md` with derive-roadmap header |
| A new-functionality idea | — | brainstorming, not this skill |
| Code or a spec to review | — | code-review skills, not this skill |

## Common mistakes

- **Code walkthrough in disguise** — sections mirroring the package layout,
  or "verification apparatus" sections narrating parity gates, batched-fit
  machinery, and sampler configuration as library calls. Organize by the
  template's slots; name components by methodological role; describe
  inference as an algorithm, with library-free evaluation criteria.
- **Smuggled identifiers** — a variable name in an equation. Define a symbol
  in the notation table and use it.
- **Site-inventory appendix** — closing with a "symbol ↔ sampler site"
  correspondence table re-couples the entire document to the code. The
  notation table is the only symbol inventory; code names stay out of it.
- **Delegating to docs-writer** — its grounding rule is anti-decoupling;
  forbidden above.
- **Treating the critique as a to-do list** — it synthesizes into a spec;
  staging and implementation belong to derive-roadmap and the chain after
  it. Never implement critique points directly.
- **Drafting spec text before the triage table** — triage first, one
  batched set.
- **Chasing validator zero** — the checker is advisory; legitimate notation
  may flag.
