# describe-critique-methodology Implementation Plan (plan #1 of 2 for methodology-pipeline-skills)

> **STATUS: COMPLETE (2026-07-26)** — executed inline via executing-plans on
> branch `feat/describe-critique-methodology` in the primary checkout.
> Five commits: `197ce1e` (apparatus), `e64cb11` (GREEN skill + provenance),
> `05d1631` (LaTeX-aware validator fix), `d44fb78` (neighbor tweaks), plus
> this markup. All deviations are noted inline below.
>
> **Two user gates remain open** — they need a human and could not be
> answered in-session: Task 7 Step 4 (review/commit the alt-nfp description,
> leg 1 of the round-trip gating plan #2) and Task 9 Step 3 (`/context`
> residency check in a fresh session). Both are recorded as *pending user
> action*, not as satisfied.

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Execution note for this plan:** Tasks 2, 4, 5, 6, and 7 dispatch fresh subagents *as test apparatus*. Implementer subagents cannot spawn subagents, so under subagent-driven-development the **orchestrator executes those five tasks itself** (delegate Tasks 1, 3, and 8 normally; in Task 9 delegate only Steps 1–2 — Steps 3–4 are orchestrator/user dialogue). Where an orchestrator-executed task commits (Task 7), still produce the diff file and dispatch the task-reviewer subagent afterward, as for any SDD task. Inline execution via executing-plans avoids the split and is the recommended mode for this plan.

**Goal:** Ship the `describe-critique-methodology` skill — Describe mode (code-decoupled methodological description + Chat Research handoff) and Synthesize mode (critique triage → house-format spec) — fully RED→GREEN→REFACTOR tested, provenance-tracked, and deployed.

**Architecture:** One new skill directory `skills/describe-critique-methodology/` (SKILL.md + 4 references + 1 tested script), plus provenance edits (NOTICE, CLAUDE.md, README), one neighbor tweak (`agents/docs-writer.md`), and a user-level deployment step (listing-budget fraction + symlink). The skill's routing relies on in-artifact headers paired with description triggers; three micro-tests verify the wording before the full-run gate.

**Tech Stack:** Markdown skills per the writing-skills meta-skill; Python 3.13 stdlib script via `uv run`; pytest; repo lints `build/check_frontmatter.py` + `build/check_provenance.py`.

**Spec:** [`specs/methodology-pipeline-skills.md`](../methodology-pipeline-skills.md). This plan implements Reqs 1–6 and the plan-#1 slices of Reqs 12–15. **Skill B (`derive-roadmap`, Reqs 7–11) is OUT of this plan** — plan #2 is gated on the user running one real describe→Chat→critique round-trip on alt-nfp (Req 13); do not start it (writing-skills STOP gate).

## Global Constraints

- Repo: `/Users/lowell/Projects/agent-skills`. Execute on branch `feat/describe-critique-methodology` cut from `main`, **in the primary checkout, not a worktree** (Task 9's symlink and the subagent dispatches use absolute paths into this checkout). Before every commit: `git branch --show-current` AND `git status` (the user commits from parallel terminals; a commit once landed on the wrong branch).
- **No pushes, no merges** — the user approves push/merge explicitly at finishing-a-development-branch time.
- **Both lints green before EVERY commit** (run verbatim):
  `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
  `uv run --python 3.13 python build/check_provenance.py`
- The NOTICE entry, the CLAUDE.md "Lowell's originals" bullet, and the README row/credits MUST land **in the same commit** that creates `SKILL.md` (Task 3) — `check_provenance.py` cross-checks skill dirs ↔ NOTICE ↔ CLAUDE.md the moment a SKILL.md exists, and spec Verification bullet 8 requires the README update in the same commit as the skill it describes.
- Python: single quotes, 4-space indent, Python 3.13, stdlib-only for the bundled script. Tests use bare imports and are directory-scoped: `cd skills/describe-critique-methodology/scripts && uv run --python 3.13 --with pytest python -m pytest -q`.
- Cross-skill references use **bare skill names** (`derive-roadmap`, `brainstorming`) — never a `superpowers:` or plugin namespace. This is load-bearing (spec Req 12: plugin-namespace poaching mitigation).
- Frontmatter: `name` == directory name; `description` ≤1024 chars; only keys `name`/`description`/`license`/`metadata` (lint-enforced).
- **Scratch artifacts are never committed** (plan-15 precedent): RED transcripts, micro-test outputs, and fixtures live in one scratch dir for the whole plan — `SCRATCH` below means e.g. `/private/tmp/claude-501/-Users-lowell-Projects-agent-skills/<session>/scratchpad/dcm-plan18/`. Distilled results go in commit messages and this plan's deviation notes.
- v1 domain scope is statistical/Bayesian/nowcast only (Req 15) — the templates carry NO DL/NLP slots; the DL/NLP extension is recorded in `specs/deferred_items.md` at plan completion, not built.
- **Ordering is the Iron Law** (writing-skills): Task 1 (apparatus) → Task 2 (RED) → Task 3 (GREEN) → Tasks 4–6 (micro-tests) → Task 7 (REFACTOR + full run) → Tasks 8–9. Do not reorder. In Task 3's verbatim text, the **decoupling recipe and template form** are the spec-sanctioned default hypothesis (Req 2), to be confirmed or revised against RED; the workflow scaffolding (mode steps, handoff scripts, routing headers) is spec-FIXED content (Reqs 1, 3, 4); and the Synthesize-mode text ships **consciously untested** pending plan #2's real-round-trip fixture (Req 13) — record that as a deviation note, not a checklist tick. The RED cut rule is scoped: cut only Describe-mode failure-countering guidance (a Common-mistakes bullet, recipe emphasis) whose failure RED did not exhibit — NEVER a spec-mandated template slot or workflow step, never Synthesize-mode text, and never system-template-specific guidance (its n=2 RED arm is exploratory; record, don't cut). Every reconciliation change gets a `> Deviation:` note.
- Out of scope (spec): any edit to brainstorming / writing-plans / executing-plans / subagent-driven-development; hooks; DL/NLP slots; the in-session SOTA pass.

---

### Task 1: Branch + decoupling-check harvest core (pre-RED apparatus)

Implements: Req 5 (validator core built BEFORE RED — micro-test scoring needs it as apparatus).

**Files:**
- Create: `skills/describe-critique-methodology/scripts/check_decoupling.py`
- Test: `skills/describe-critique-methodology/scripts/test_check_decoupling.py`

**Interfaces:**
- Consumes: nothing (first task).
- Produces: `harvest(text: str, whitelist: set[str] | frozenset = frozenset()) -> list[Finding]` where `Finding` is a frozen dataclass `(line: int, token: str, category: str)`; `notation_whitelist(text: str) -> set[str]`; `suspicious_notation(whitelist) -> list[str]` (identifier-shaped table entries — the anti-laundering counter-check); CLI `python3 check_decoupling.py <file.md>` printing `path:line: [category] token` lines, `[notation-table]` warnings, and an `ADVISORY: …` summary, **always exit 0**. Tasks 2, 4, and 7 score documents with this CLI.

- [x] **Step 1: Cut the branch**

```bash
git branch --show-current   # expect: main
git status                  # expect: clean (stop and report if not)
git checkout -b feat/describe-critique-methodology
mkdir -p skills/describe-critique-methodology/scripts
```

(Neither lint looks at a skill directory until `SKILL.md` exists, so the bare `scripts/` dir is lint-safe.)

- [x] **Step 2: Write the failing tests**

Create `skills/describe-critique-methodology/scripts/test_check_decoupling.py`:

```python
'''Tests for the advisory decoupling checker.

Bare imports, directory-scoped — run from this directory:
uv run --python 3.13 --with pytest python -m pytest -q
'''
import subprocess
import sys
from pathlib import Path

from check_decoupling import harvest, notation_whitelist, suspicious_notation


def toks(findings):
    return {f.token for f in findings}


def cats(findings):
    return {f.category for f in findings}


def test_flags_snake_case_multitoken():
    fs = harvest('the kalman_ll factor carries the likelihood')
    assert 'kalman_ll' in toks(fs)
    assert 'snake_case' in cats(fs)


def test_flags_camel_case():
    fs = harvest('assembled by assembleTotal downstream')
    assert 'assembleTotal' in toks(fs)
    assert 'camelCase' in cats(fs)


def test_ignores_single_words_and_greek():
    assert harvest('the state evolves with growth and sigma controls scale') == []


def test_flags_backticked_dotted_token():
    fs = harvest('see `model.py` for details')
    assert 'model.py' in toks(fs)


def test_ignores_backticked_single_word_and_greek():
    assert harvest('the site `sigma` and the `trend` term') == []


def test_flags_identifier_path():
    fs = harvest('lives in packages/nfp-model')
    assert 'packages/nfp-model' in toks(fs)
    assert 'path' in cats(fs)


def test_ignores_natural_slash_pairs():
    assert harvest('estimation and/or inference') == []


def test_flags_dotted_call_syntax():
    fs = harvest("a single numpyro.factor('ll', x) call")
    assert 'numpyro.factor' in toks(fs)
    assert 'call' in cats(fs)


def test_ignores_distribution_call_notation():
    assert harvest('with priors N(0, 1) and LogNormal(0, 1)') == []


def test_notation_table_whitelist():
    doc = '\n'.join([
        '## Notation',
        '| Symbol | Meaning |',
        '| --- | --- |',
        '| `y_t` | observed employment at month t |',
        '',
        '## Procedure',
        'the series y_t is observed monthly',
    ])
    wl = notation_whitelist(doc)
    assert 'y_t' in wl
    assert harvest(doc, wl) == []


def test_whitelist_is_scoped_to_notation_sections():
    doc = '## Setup\n| `foo_bar` | not a notation table |\n'
    assert notation_whitelist(doc) == set()


def test_suspicious_notation_flags_identifier_shaped_symbols():
    assert suspicious_notation({'kalman_ll', 'assembleTotal', 'model.py'}) == [
        'assembleTotal', 'kalman_ll', 'model.py',
    ]


def test_suspicious_notation_exempts_math_shaped_symbols():
    assert suspicious_notation({'y_t', 'g_cont', 'sigma_obs', 'beta', 'T'}) == []


def test_cli_always_exits_zero(tmp_path):
    doc = tmp_path / 'm.md'
    doc.write_text('uses kalman_ll everywhere\n')
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).parent / 'check_decoupling.py'), str(doc)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0
    assert 'kalman_ll' in proc.stdout
    assert 'ADVISORY' in proc.stdout
```

- [x] **Step 3: Run tests to verify they fail**

```bash
cd skills/describe-critique-methodology/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: collection error — `ModuleNotFoundError: No module named 'check_decoupling'`.

- [x] **Step 4: Write the implementation**

Create `skills/describe-critique-methodology/scripts/check_decoupling.py`:

```python
#!/usr/bin/env python3
'''Advisory decoupling check for methodology descriptions.

Flags code-coupled tokens in a methodology markdown file:
  - multi-token identifiers: snake_case with >=2 tokens, camelCase
  - backticked code-font tokens (unless a single plain word or Greek name)
  - file paths (a slash-joined token with an identifier-flavored segment)
  - dotted call syntax (numpyro.factor(...), az.compare(...))

Never flags single dictionary words or Greek-letter names — house Bayesian
style names sample sites sigma/mu/beta, and the notation table's own content
must survive. Symbols defined in the description's notation table (first
column of any table under a heading containing 'Notation') are whitelisted.

Known misses, accepted: single-word call syntax ('estimate(x)') is not
flagged (prose parentheticals like 'weight(s)' would false-positive);
capitalized distribution notation (N(0,1), LogNormal(0,1)) is exempt by
design; URLs in citations may flag as paths — they are review input too.

ADVISORY ONLY: output is review input, never a fix-until-clean gate.
The CLI always exits 0.

Run: python3 check_decoupling.py <methodology.md>
'''
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

GREEK = {
    'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
    'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho',
    'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
}
SNAKE_RE = re.compile(r'\b[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+\b')
CAMEL_RE = re.compile(r'\b[a-z][a-z0-9]*[A-Z][A-Za-z0-9]*\b')
BACKTICK_RE = re.compile(r'`([^`\n]+)`')
PATH_RE = re.compile(r'(?<![\w/])[\w.-]+(?:/[\w.-]+)+')
DOTTED_CALL_RE = re.compile(r'\b[a-z_][\w]*(?:\.[\w]+)+\s*\(')
WORD_RE = re.compile(r'[A-Za-z]+')
HEADING_RE = re.compile(r'^#+\s+(.*)$')
TABLE_SEP_CHARS = {'-', ':', ' ', '|'}


@dataclass(frozen=True)
class Finding:
    line: int
    token: str
    category: str


def notation_whitelist(text: str) -> set[str]:
    '''Symbols from the first column of tables under a Notation heading.'''
    symbols: set[str] = set()
    in_notation = False
    for raw in text.split('\n'):
        heading = HEADING_RE.match(raw)
        if heading:
            in_notation = 'notation' in heading.group(1).lower()
            continue
        line = raw.strip()
        if in_notation and line.startswith('|'):
            first = line.strip('|').split('|', 1)[0].strip().strip('`$ ')
            if first and not set(first) <= TABLE_SEP_CHARS:
                symbols.add(first)
    return symbols


def _pathlike(token: str) -> bool:
    '''Identifier-flavored paths only — "and/or" stays clean.'''
    return any(c in seg for seg in token.split('/') for c in '._-')


SUBSCRIPT_BASE_MAX = 2  # y_t, g_cont: a 1-2 char base reads as a math subscript


def suspicious_notation(whitelist: set[str] | frozenset[str]) -> list[str]:
    '''Whitelist entries shaped like code identifiers, not notation.

    A notation-table symbol is exempt when it reads as math: single plain
    words, Greek-based names (sigma_obs), short-base subscripts (y_t,
    g_cont). Everything identifier-shaped — camelCase, dotted, path-like,
    or snake_case with a >=3-char non-Greek base — is reported, so a
    smuggled identifier cannot hide by being "defined" in the table.
    '''
    out: list[str] = []
    for sym in sorted(whitelist):
        if CAMEL_RE.fullmatch(sym) or '.' in sym or '/' in sym:
            out.append(sym)
            continue
        if SNAKE_RE.fullmatch(sym):
            base = sym.split('_', 1)[0]
            if len(base) > SUBSCRIPT_BASE_MAX and base.lower() not in GREEK:
                out.append(sym)
    return out


def harvest(
    text: str, whitelist: set[str] | frozenset[str] = frozenset(),
) -> list[Finding]:
    findings: list[Finding] = []
    for lineno, line in enumerate(text.split('\n'), 1):
        flagged: set[str] = set()

        def add(token: str, category: str) -> None:
            if token in whitelist or token in flagged:
                return
            flagged.add(token)
            findings.append(Finding(lineno, token, category))

        for m in SNAKE_RE.finditer(line):
            add(m.group(0), 'snake_case')
        for m in CAMEL_RE.finditer(line):
            add(m.group(0), 'camelCase')
        for m in PATH_RE.finditer(line):
            if _pathlike(m.group(0)):
                add(m.group(0), 'path')
        for m in DOTTED_CALL_RE.finditer(line):
            add(m.group(0).rstrip('( \t'), 'call')
        for m in BACKTICK_RE.finditer(line):
            token = m.group(1).strip()
            if token.lower() in GREEK or WORD_RE.fullmatch(token):
                continue
            add(token, 'backtick')
    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: check_decoupling.py <methodology.md>')
        return 0
    text = Path(argv[1]).read_text()
    whitelist = notation_whitelist(text)
    findings = harvest(text, whitelist)
    for f in findings:
        print(f'{argv[1]}:{f.line}: [{f.category}] {f.token}')
    suspicious = suspicious_notation(whitelist)
    for sym in suspicious:
        print(
            f'{argv[1]}: [notation-table] {sym} — defined as a symbol '
            'but shaped like a code identifier'
        )
    print(
        f'ADVISORY: {len(findings)} code-coupling candidate(s), '
        f'{len(suspicious)} identifier-shaped notation symbol(s) — '
        'review input, not a gate.'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
```

- [x] **Step 5: Run tests to verify they pass**

```bash
cd skills/describe-critique-methodology/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: `14 passed`.

- [x] **Step 6: Lints + commit**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
git branch --show-current && git status
git add skills/describe-critique-methodology/scripts/
git commit -m "feat(describe-critique-methodology): advisory decoupling-check core (pre-RED apparatus)"
```

Expected: both lints exit 0 (the dir has no SKILL.md yet, so neither lint inspects it).

---

### Task 2: RED — no-skill baselines on alt-nfp

Implements: Req 13 (RED baselines; expected failures documented in advance). No repo changes — all artifacts in SCRATCH.

**Files:**
- Create (SCRATCH only, never committed): `SCRATCH/red/RED-observations.md`, `SCRATCH/red/s1-rep{1..5}.md`, `SCRATCH/red/s2-rep{1..2}.md`

**Interfaces:**
- Consumes: Task 1's CLI (`python3 skills/describe-critique-methodology/scripts/check_decoupling.py <file>`).
- Produces: `SCRATCH/red/RED-observations.md` — pre-registered expectations + verbatim observed failures + per-transcript flag counts. Task 3 reconciles its draft against this file; Task 4 reuses the five S1 transcripts as its no-guidance control arm.

- [x] **Step 1: Pre-register expected failures**

Write `SCRATCH/red/RED-observations.md` opening section BEFORE any dispatch, listing the spec's predicted failure modes verbatim:

```markdown
# RED baseline — describe-critique-methodology (plan 18, Task 2)

## Pre-registered expected failures (written before dispatch)
E1. Identifier smuggling: variable/function/file names appear in the math
    ("the kalman_ll factor", "assemble_total sums the legs").
E2. Sections mirror the file/package layout instead of methodological slots.
E3. Code-walkthrough framing: the procedure narrated as library calls, not
    as an estimation algorithm.
E4. Cribbing: content lifted from the stale root notes
    (alt-nfp-methodology*.md) despite the instruction to work from code.
E5. Missing slots: no assumptions/limitations section, no evaluation
    criteria, no questions addressed to the reviewer.

## Observed (verbatim excerpts + counts, filled per rep below)
```

- [x] **Step 2: Dispatch the module-scenario baselines (5 reps)**

Dispatch five FRESH `general-purpose` subagents, one per rep, each with exactly this prompt (substitute `<SCRATCH>` and `<N>` = 1–5; no skill content anywhere in the dispatch):

```
You are working in /Users/lowell/Projects/alt-nfp. Write a methodological
description of the nfp-model package (packages/nfp-model/) — the
mathematical model and the estimation/inference procedure — as a standalone
markdown document for an external statistician who cannot see the code.
The earlier hand-written methodology documents in the repo — at the root
(alt-nfp-methodology*.md) and under specs/ (alt-nfp-model-methodology.md
and the calibration methodology files) — are stale; work from the code,
not from them. Save the document to <SCRATCH>/red/s1-rep<N>.md and reply
with only the file path.
```

- [x] **Step 3: Dispatch the system-scenario baselines (2 reps)**

Same dispatch, replacing the second sentence's target with "the whole alt-nfp forecasting system (all packages and how their outputs combine)" and the output path with `<SCRATCH>/red/s2-rep<N>.md` (N = 1–2).

- [x] **Step 4: Score and record verbatim**

For each of the 7 transcripts:

```bash
python3 skills/describe-critique-methodology/scripts/check_decoupling.py SCRATCH/red/s1-rep1.md
```

Record in `RED-observations.md`, per rep: total flag count, count per category, whether E1–E5 each occurred (with one verbatim quoted excerpt per occurrence), and whether the transcript shows signs of cribbing any of the pre-existing methodology documents (the root notes or the specs/ methodology files named in the dispatch). **Read every flagged match manually** — template echoes and quoted examples are not hits. Close with a summary table: per-rep flag counts (this is Task 4's control distribution) and which expected failures were confirmed / not observed.

- [x] **Step 5: No commit**

> **Deviation (Task 2, observed failures):** E1/E3/E5 CONFIRMED 7/7. **E2
> NOT OBSERVED** in its literal form (no rep mirrored the file/package
> layout); the adjacent observed failure was implementation-apparatus
> sections (parity gates, batched-fit machinery, software notes) and a
> site-name appendix. Nothing was cut — the "code walkthrough" bullet was
> EXTENDED to the observed form instead, and a new "site-inventory
> appendix" bullet added. **E4 NOT OBSERVED 0/7** (no stale-doc cribbing);
> no cribbing-countering guidance existed to cut, so no change. Notation
> tables: 0/7 reps built one — the single strongest signal for the
> notation-table-first recipe.

Nothing lands in the repo. The distilled failure list is pasted into Task 3's commit message. If an expected failure did NOT occur in any rep, mark it `NOT OBSERVED` — Task 3 then omits the failure-countering guidance for it under the **scoped cut rule in Global Constraints** (spec-mandated template slots and workflow steps always stay — E5's slots are fixed by spec Req 2 regardless of observation), with a deviation note.

---

### Task 3: GREEN — SKILL.md + references + provenance (one commit)

Implements: Reqs 1, 2, 3, 4, 6; Req 14's NOTICE/CLAUDE.md slice. **Reconcile every file below against `SCRATCH/red/RED-observations.md` before writing** (Global Constraints: default-hypothesis rule).

**Files:**
- Create: `skills/describe-critique-methodology/SKILL.md`
- Create: `skills/describe-critique-methodology/references/methodology-template.md`
- Create: `skills/describe-critique-methodology/references/critique-prompt.md`
- Create: `skills/describe-critique-methodology/references/spec-synthesis.md`
- Create: `skills/describe-critique-methodology/references/wiki-touchpoints.md`
- Modify: `NOTICE` (originals block, before its terminating blank line)
- Modify: `CLAUDE.md` (Lowell's originals bullet: add name, Twelve→Thirteen; Commands section: new test entry)
- Modify: `README.md` (Mine-table row + Credits bullet — Verification bullet 8 wants these in the skill's own commit)

**Interfaces:**
- Consumes: `SCRATCH/red/RED-observations.md` (Task 2).
- Produces: the skill's frontmatter description text (Tasks 5–6 embed it verbatim in their harness prompts); the three routing headers (methodology / critique / synthesized-spec) exactly as written below; the scripted re-entry utterance `The critique is back — use describe-critique-methodology (synthesize mode) on specs/<name>-critique.md`; the template + recipe text Task 4 tests.

- [x] **Step 1: Write SKILL.md**

Create `skills/describe-critique-methodology/SKILL.md` with exactly this content (then apply RED reconciliation with deviation notes):

````markdown
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

- **Code walkthrough in disguise** — sections mirroring the package layout.
  Organize by the template's slots; name components by methodological role.
- **Smuggled identifiers** — a variable name in an equation. Define a symbol
  in the notation table and use it.
- **Delegating to docs-writer** — its grounding rule is anti-decoupling;
  forbidden above.
- **Treating the critique as a to-do list** — it synthesizes into a spec;
  staging and implementation belong to derive-roadmap and the chain after
  it. Never implement critique points directly.
- **Drafting spec text before the triage table** — triage first, one
  batched set.
- **Chasing validator zero** — the checker is advisory; legitimate notation
  may flag.
````

- [x] **Step 2: Write the methodology templates**

Create `skills/describe-critique-methodology/references/methodology-template.md`:

````markdown
# Methodology description templates

Two shapes. Choose in Describe mode step 1: **module** for one estimand and
one procedure; **system** when components compose. Every slot is REQUIRED —
write "None known." rather than omitting a slot. The output is math and
prose: symbols come from the notation table, never from the code. If you
catch yourself typing a function, file, class, or variable name from the
codebase, define a symbol for the concept in the notation table and use the
symbol. Symbols are mathematical notation or role-names — a snake_case,
camelCase, or dotted name lifted from the code does not become notation by
being defined in the table; rename the concept (subscripted single letters
and Greek bases are fine).

## Module template

```markdown
# <System> — <Module role> methodology

> For agentic workers: when specs/<name>-critique.md exists beside this
> file, REQUIRED SKILL: describe-critique-methodology (synthesize mode) —
> do not draft a spec directly.

## Notation
| Symbol | Meaning | Domain / units |
|---|---|---|
Every symbol used anywhere below is defined here, in-document.

## Problem formulation and data-generating story
What is observed, what is latent, and what generates the data — as random
variables and distributions. State the estimand explicitly.

## Estimation / inference procedure
The procedure in math: model equations, likelihood, priors (if Bayesian),
and the inference algorithm described AS an algorithm — never as a library
call.

## Assumptions and limitations
Numbered. Each assumption states what breaks if it fails.

## Evaluation criteria
How the method's output is judged: metrics, benchmarks, calibration checks,
holdout design — as criteria, not as a test-file inventory.

## Open questions for the reviewer
Numbered questions addressed to the external reviewer — the places you want
the critique to push.
```

## System template

```markdown
# <System> methodology

> For agentic workers: when specs/<name>-critique.md exists beside this
> file, REQUIRED SKILL: describe-critique-methodology (synthesize mode) —
> do not draft a spec directly.

## Component inventory
| Component (by methodological role) | Estimand / output | Consumes |
|---|---|---|
Roles, never package or module names: "private-sector state-space nowcast
leg", not a directory name.

## Composition
How component outputs combine, as math on random variables and estimates
(additive decomposition, convolution of predictive densities,
reconciliation, ...).

## Cross-component assumptions
The assumptions that live BETWEEN components — independence, shared units,
vintage/timing alignment — the ones no single component states.

## Notation
Shared table for the composition math (per-component sections may extend
it).

## Per-component descriptions
One section per component, each following the module template's slots.

## Open questions for the reviewer
```
````

- [x] **Step 3: Write the critique prompt**

Create `skills/describe-critique-methodology/references/critique-prompt.md`:

````markdown
# Critique prompt for the Chat Research round-trip

Paste the block below into a Claude Chat session with **Research** enabled,
attaching the committed methodology description. Run the session
interactively — push back, steer, adjudicate — for as long as it earns its
keep. The closing instruction makes Chat write the critique file; save its
output as `specs/<name>-critique.md` beside the description and commit it.

---

You are conducting a state-of-the-art methodological review. Attached is a
methodological description of a system I built: math and prose, deliberately
decoupled from the implementation. Critique the METHODOLOGY — the code is
invisible and off the table.

Research what others have done for this class of problem, then tell me:

1. Where does this methodology sit relative to the published state of the
   art? What have others done that it ignores?
2. What is methodologically wrong, stale, or unsupported? Cite sources.
3. Where can it improve, ranked by expected value? Distinguish "fix an
   error" from "adopt a better method" from "extend scope".
4. Answer the description's "Open questions for the reviewer" directly.

We will discuss your findings interactively; I will push back, and we will
adjudicate each point together.

When I say the review is done, write the final critique as one markdown
document for me to save as a file, following these rules exactly:

- Open with this block, verbatim:

  > For agentic workers: REQUIRED SKILL: describe-critique-methodology
  > (synthesize mode) — synthesize this critique with its methodology
  > description into a specification; do not treat it as a code review and
  > do not implement fixes directly.

- Record the ADJUDICATED positions we reached, not your first-pass
  findings. Where I rejected a point, keep it, marked rejected, with the
  reason.
- Number every critique point (C1, C2, ...) so a downstream triage table
  can cite them.
- Cite sources for state-of-the-art claims (author-year plus a link).
````

- [x] **Step 4: Write the synthesis reference**

Create `skills/describe-critique-methodology/references/spec-synthesis.md`:

````markdown
# Synthesize mode — triage and spec format

## Critique triage table

Before any spec text, present ONE batched table covering every numbered
critique point:

| # | Critique point (one line) | Verdict | Rationale (one line) |
|---|---|---|---|

Verdicts: **accept** / **reject** / **needs-user-adjudication**. Ask every
needs-user-adjudication question in the same message as the table — one
batched set, never a drip. Rejected-by-Chat points (recorded as rejected in
the critique) default to reject here; overturn only with a rationale.

## Spec format

The synthesized spec uses the house skeleton: summary paragraph, Motivation,
Core principle (when one exists), numbered Requirements with
(chosen)/(rejected) alternatives inline, Verification (observable outcomes),
Out of scope, Rollout note. Do not reinvent the skeleton — before writing
your first synthesized spec, read two retired exemplars in the agent-skills
repo's `specs/completed/` directory (that repo owns the house format; this
file cites it rather than restating it).

## Locators

Every requirement cites its origin inline: `(methodology §N)` and/or
`(critique C7)`, plus the triage verdict where it was not a plain accept.
A requirement with no locator is a new idea — route it to brainstorming
instead of smuggling it into the synthesis.

## Routing header

The spec's first line after the title, verbatim:

> For agentic workers: REQUIRED NEXT SKILL: derive-roadmap — do not plan
> this spec directly and do not split it into per-subsystem plans.

## Self-review, gate, handoff

Run the four checks (placeholders, internal consistency, scope, ambiguity);
fix inline. Then the scripted user gate, then hand off to derive-roadmap by
bare name in a fresh session — and stop.
````

- [x] **Step 5: Write the wiki touchpoints**

Create `skills/describe-critique-methodology/references/wiki-touchpoints.md`:

````markdown
# Wiki touchpoints (only when $LLM_WIKI_ROOT is set)

Both touchpoints are optional conveniences. When `$LLM_WIKI_ROOT` is unset,
skip both silently — no mention in output.

## Describe mode pre-flight (read-only)

Before writing the description, query the wiki for already-filed literature
on the system's method family, using the llm-wiki skill's query procedure.
Filed sampler/nowcasting notes often supply the evaluation-criteria slot or
sharpen the open questions. Read-only: no wiki mutation.

## Synthesize mode suggestion (one line, once)

After the critique file is committed, suggest that the human drop a copy
into `$LLM_WIKI_ROOT/raw/` for llm-wiki ingest — a Research-mode critique is
a citation-rich source document. The agent never writes `raw/` itself.
````

- [x] **Step 6: NOTICE + CLAUDE.md + README in the same commit**

Edit `NOTICE` — in the originals block, insert before its terminating blank line (directly under `    llm-wiki/`):

```
    describe-critique-methodology/
```

Edit `CLAUDE.md` — the "Lowell's originals" bullet. Read the current line first (the user edits from parallel terminals), then: append `` `describe-critique-methodology` `` to the backticked list (before the period) and change `(Twelve — keep in sync with` to `(Thirteen — keep in sync with`. (Plan #2 takes it to Fourteen — the spec's endpoint covers both skills.)

Edit `CLAUDE.md` — Commands section, add after the llm-wiki test entry:

```bash
# describe-critique-methodology decoupling-check tests — 14 tests
cd skills/describe-critique-methodology/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Edit `README.md` — in the "Mine" table, add directly below the `llm-wiki` row:

```markdown
| [`describe-critique-methodology`](skills/describe-critique-methodology/) | Leg 1 of the methodology-critique loop: write a system- or module-level **methodological description** of a codebase — math and prose deliberately decoupled from the code (notation table, data-generating story, estimation procedure, assumptions, evaluation criteria, open questions) — carry it to a Claude Chat **Research** critique, then **synthesize** description + adjudicated critique into a house-format spec routed onward to `derive-roadmap`. Two modes (Describe / Synthesize) joined by routing headers in the artifacts themselves; bundles an advisory `check_decoupling.py`. Stats/Bayesian/nowcast scope in v1. |
```

Edit `README.md` — Credits, "**My original skills**" bullet (read the current line first): change ``...`creative-thinking`, and `llm-wiki` are my own work`` to ``...`creative-thinking`, `llm-wiki`, and `describe-critique-methodology` are my own work``.

- [x] **Step 7: Reconcile with RED, verify, commit**

Re-read `SCRATCH/red/RED-observations.md`. Walk the skill files section by section and record an explicit verdict for each: **CONFIRMED** (RED evidence supports it as written), **EXTENDED** (RED observed a failure it does not address — extend it), **CUT** (failure-countering guidance whose failure was NOT OBSERVED, within the scoped cut rule in Global Constraints), or **SPEC-FIXED / UNTESTED** (workflow scaffolding and all Synthesize-mode text — Reqs 1/3/4, untested pending plan #2). Every EXTENDED/CUT change gets a `> Deviation:` note; the verdict list goes into the commit message. Then:

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
git branch --show-current && git status
git add skills/describe-critique-methodology/ NOTICE CLAUDE.md README.md
git commit -m "feat(describe-critique-methodology): GREEN — SKILL.md, references, provenance

RED baseline (7 no-skill runs on alt-nfp): <paste the distilled failure
summary from SCRATCH/red/RED-observations.md — per-scenario flag counts and
which of E1-E5 were confirmed>"
```

Expected: both lints exit 0 (description ≤1024 chars; name matches dir; all referenced `references/`/`scripts/` paths exist; NOTICE/CLAUDE.md originals in sync at Thirteen).

---

### Task 4: Micro-test 1 — decoupling recipe wording

Implements: Req 13 micro-test (a). Control arm = Task 2's five S1 transcripts (RED **is** the no-guidance control). No repo changes unless the wording fails.

**Files:**
- Create (SCRATCH only): `SCRATCH/mt1/rep{1..5}.md`, `SCRATCH/mt1/MT1-results.md`
- Possibly modify: `skills/describe-critique-methodology/references/methodology-template.md`, `SKILL.md` step 2 (only on a failing result, via Task 7's REFACTOR commit)

**Interfaces:**
- Consumes: Task 2's S1 transcripts + flag counts; Task 3's template + recipe text; Task 1's CLI.
- Produces: `SCRATCH/mt1/MT1-results.md` — per-arm flag counts, slot compliance, variance verdict, and a KEEP / REVISE decision Task 7 acts on.

- [x] **Step 1: Dispatch 5 recipe-arm reps**

Five FRESH `general-purpose` subagents. Prompt = Task 2 Step 2's S1 prompt verbatim (output path `<SCRATCH>/mt1/rep<N>.md`), plus this suffix:

```
Follow the attached template and writing rules exactly.
--- ATTACHED: methodology-template.md ---
<full current content of references/methodology-template.md>
--- ATTACHED: writing rules (from the skill) ---
<the "Write from the notation table outward ..." paragraph from SKILL.md
Describe mode step 2, verbatim>
```

- [x] **Step 2: Score both arms identically**

Run the CLI on each `mt1/rep*.md`; record per-rep: flag count (after notation-table whitelisting), whether all 6 module-template slots are present, and read every flagged match manually (a defined-then-used symbol like `y_t` is a whitelist hit, not smuggling). Also read each rep's notation TABLE itself along with the CLI's `[notation-table]` warnings — an identifier "defined" as a symbol is smuggling the whitelist would otherwise hide; count it as a flag.

- [x] **Step 3: Judge**

> **Deviation (Task 4, PASS bar input was invalid → checker fixed):** on the
> as-committed checker the raw-count bar could not be evaluated honestly —
> `notation_whitelist()` read table entries literally, so a LaTeX table
> (`| $\sigma_p$ |`) whitelisted `\sigma_p` while prose flagged `sigma_p`.
> All 5 reps wrote LaTeX, so **the whitelist was silently inert on every
> recipe document** and the arm was charged for notation it had correctly
> defined. The same leading backslash made `suspicious_notation()` vacuous
> (every branch fails on `\`), so the anti-laundering counter-check
> returned `[]` without inspecting anything.
>
> Fixed in the REFACTOR phase (commit `05d1631`, **a code change not in this
> task's Files list** — recorded as a deviation): normalization applied ONCE
> in `notation_whitelist()`, feeding both the harvest whitelist and the
> counter-check, so a LaTeX-dressed identifier cannot be whitelisted while
> staying invisible to the check —
> `test_latex_wrapped_identifier_still_flagged_by_counter_check` pins that.
> LaTeX Greek variants (`varepsilon`, `varrho`, …, `ell`) added to `GREEK`.
> `harvest()` regexes untouched. 14 → 18 tests; CLAUDE.md count updated in
> the same commit.
>
> **Result after the fix:** control {50, 108, 111, 123, 111} vs recipe
> {30, 12, 32, 15, 13} — separated, non-overlapping, bar MET. It agrees with
> the plan's manual-read metric: verified code-identifier smuggling
> {7, 1, 3, 1, 19} control vs {0, 0, 0, 0, 0} recipe. Notation tables 0/5 vs
> 5/5; slots 5/5; all five reps converged on one shape. **KEEP, zero
> skill-text edits.**

Write `SCRATCH/mt1/MT1-results.md`: control (RED S1) counts vs recipe-arm counts; slot compliance ×5; variance check (five reps converging on the template shape = wording binds; five different shapes = tighten the form before adding words). PASS = every recipe rep has all slots AND the recipe-arm flag distribution sits clearly below the control's (separated, not overlapping medians). On FAIL: revise the recipe wording (form-level change first — e.g. move the rule into a REQUIRED slot — per writing-skills "Match the Form to the Failure"), re-run 5 reps, max two revision cycles. If identifier smuggling survives recipe + validator after those cycles, apply the spec's designated escalation (Req 2): add a rationalization table to the template/skill at REFACTOR — then surface to the user. Record the final wording; Task 7 commits it.

---

### Task 5: Micro-test 2 — Synthesize re-entry vs brainstorming

Implements: Req 13 micro-test (b): the re-entry utterance and the critique-file routing header hold against brainstorming's greedy trigger.

**Files:**
- Create (SCRATCH only): `SCRATCH/mt2/critique-with-header.md`, `SCRATCH/mt2/critique-no-header.md`, `SCRATCH/mt2/MT2-results.md`

**Interfaces:**
- Consumes: Task 3's frontmatter description (verbatim), critique routing header (verbatim from `references/critique-prompt.md`).
- Produces: `SCRATCH/mt2/MT2-results.md` with per-arm tallies and a KEEP / REVISE decision for Task 7.

- [x] **Step 1: Build fixtures**

`SCRATCH/mt2/critique-with-header.md`: the critique routing header block (verbatim from `references/critique-prompt.md`), then the first ~60 lines of `/Users/lowell/Projects/alt-nfp/alt-nfp-methodology-review.md` (a real Research-mode critique — no synthetic strawman). `critique-no-header.md`: same without the header.

- [x] **Step 2: Dispatch arms (5 reps each)**

Each rep = one FRESH `general-purpose` subagent with this prompt (fill the bracketed slots per arm):

```
You are a coding agent starting a fresh session in a work repo. Your
runtime lists these installed skills (name: description):

- brainstorming: Use when the user proposes new functionality — a feature,
  component, script, scraper, pipeline, analysis, or behavior change — and
  no approved design or spec exists yet; before writing any code,
  scaffolding a project, or invoking an implementation skill. Trigger on
  "let's build", "add a feature", "create a tool", "I have an idea", or any
  request that would otherwise jump straight to implementation, however
  simple it looks.
- writing-plans: Use when you have a spec, design doc, or requirements for
  a multi-step task and need an implementation plan before touching code —
  "write a plan", "plan this feature", "break this into tasks", a finished
  spec in specs/ awaiting its plan, or before handing work to subagents or
  a separate execution session.
[TREATMENT ARMS ONLY: - describe-critique-methodology: <frontmatter
description from Task 3, verbatim>]

The file specs/alt-nfp-critique.md exists in the repo. Its opening lines:

<content of the arm's fixture file>

The user's first message is:
"<UTTERANCE>"

Which ONE skill do you invoke first? Reply with exactly two lines:
skill: <name, or "none — <reason>">
why: <one line>
```

(The "none" option keeps the control arm informative — a forced choice would
manufacture the failure by construction.)

Arms × utterances (5 reps each):
- **Control** (no new skill listed, no-header fixture) × U2 `Here's the critique back from the Chat research session — let's turn it into a spec.` Expected: brainstorming (or writing-plans) — the documented failure.
- **T1** (full listing, with-header fixture) × U2. PASS bar: 5/5 choose describe-critique-methodology.
- **T2** (full listing, no-header fixture) × U2. No pass bar — measures how much the description alone carries (the header is the load-bearing mechanism; record the number).
- **T3** (full listing, with-header fixture) × U1 `The critique is back — use describe-critique-methodology (synthesize mode) on specs/alt-nfp-critique.md` (the scripted utterance). PASS bar: 5/5.

- [x] **Step 3: Judge**

Tally into `SCRATCH/mt2/MT2-results.md`, reading every `why:` line (an agent choosing correctly for the wrong reason is a fragility note). If the control does NOT fail (control reps already pick the right behavior), record it — per writing-skills there is then nothing to fix, but keep the header anyway (spec-mandated mechanism) and note the control result. On T1/T3 misses: strengthen the header/description trigger wording, re-run the failing arm, max two cycles, then surface. Task 7 commits any revisions.

---

### Task 6: Micro-test 3 — cold spec encounter vs writing-plans

Implements: Req 13 micro-test (c): the Req 4 spec header holds when someone says "here's a spec, plan it".

**Files:**
- Create (SCRATCH only): `SCRATCH/mt3/spec-with-header.md`, `SCRATCH/mt3/spec-no-header.md`, `SCRATCH/mt3/MT3-results.md`

**Interfaces:**
- Consumes: Task 3's synthesized-spec routing header (verbatim from `references/spec-synthesis.md`); the MT2 harness prompt shape.
- Produces: `SCRATCH/mt3/MT3-results.md` with tallies and a KEEP / REVISE decision for Task 7.

- [x] **Step 1: Build fixtures**

`SCRATCH/mt3/spec-with-header.md`, exactly:

```markdown
# alt-nfp — synthesized methodology spec

> For agentic workers: REQUIRED NEXT SKILL: derive-roadmap — do not plan
> this spec directly and do not split it into per-subsystem plans.

Synthesized from specs/alt-nfp-methodology.md and specs/alt-nfp-critique.md.

## Requirements
1. Turn on density coupling for the Total forecast (critique C5, accepted):
   the two legs' predictive densities are combined with the measured
   cross-leg correlation, not convolved as independent (chosen; independent
   convolution rejected — understates Total variance).
2. Extend the seasonal component to all admissible harmonics (critique C2,
   accepted), with per-harmonic shrinkage (chosen; fixed truncation
   rejected).
3. Anchor the level to the near-census quarterly source at its publication
   lag (critique C8, accepted).

## Verification
- [ ] Interval coverage on the Total reaches nominal on the backtest window.

## Out of scope
- Weekly updating (deferred; critique C11 recorded, not staged).
```

`spec-no-header.md`: identical minus the blockquote.

- [x] **Step 2: Dispatch arms (5 reps each)**

MT2's harness prompt, with: listing = brainstorming + writing-plans + describe-critique-methodology (all three, both arms); fixture line "The file specs/alt-nfp.md exists in the repo. Its content:"; utterance `Here's a spec — write the implementation plan for specs/alt-nfp.md.`
- **Control** (no-header fixture). Expected: writing-plans — correct for a normal spec; this arm just establishes the default.
- **T1** (with-header fixture). PASS bar: 5/5 do NOT proceed to plan — they name derive-roadmap (and, since it is not installed, saying so / stopping counts as a pass — the harness reply format already permits `skill: none — spec requires derive-roadmap, not installed`).

- [x] **Step 3: Judge**

Tally into `SCRATCH/mt3/MT3-results.md`, reading every `why:`. On misses: tighten the header wording (it already pre-empts writing-plans' Scope Check escape hatch with "do not split it into per-subsystem plans" — extend along the observed rationalization), re-run, max two cycles, surface if still failing. Task 7 commits revisions.

---

### Task 7: REFACTOR + full Describe-mode run on alt-nfp (GREEN verification)

Implements: Req 13 (GREEN verification run), spec Verification bullet 5; closes the RED→GREEN→REFACTOR loop.

**Files:**
- Modify: `skills/describe-critique-methodology/SKILL.md` and/or `references/*.md` (micro-test revisions)
- Create (in alt-nfp, committed by the USER, not by this plan): `/Users/lowell/Projects/alt-nfp/specs/nfp-model-methodology.md`

**Interfaces:**
- Consumes: MT1–MT3 results files; the full skill from Task 3.
- Produces: final skill wording (Tasks 8–9 build on it); the alt-nfp description that becomes leg 1 of the user's real round-trip (plan #2's gate).

- [x] **Step 1: Apply micro-test revisions**

Fold MT1/MT2/MT3 REVISE outcomes into the skill files. Every change gets a deviation note under the corresponding Task 3 step at completion time. Then lints + commit:

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
git branch --show-current && git status
git add skills/describe-critique-methodology/
git commit -m "refactor(describe-critique-methodology): micro-tested wording

MT1 (recipe vs RED control): <counts>. MT2 (re-entry routing): <tallies>.
MT3 (cold-spec header): <tallies>. Records in session scratch."
```

(Skip the commit only if all three micro-tests returned KEEP with zero edits.)

> **Deviation (Task 7 Step 1):** all three micro-tests returned KEEP with
> zero skill-text edits (MT1 5/5 slots + zero smuggling; MT2 control failed
> 5/5 to brainstorming while T1/T2/T3 all routed 5/5 correctly; MT3 T1 5/5
> refused to plan and named derive-roadmap). This commit was therefore
> **empty and skipped**, per the instruction above. The only REFACTOR-phase
> change was the validator fix, landed as its own commit (`05d1631`) BEFORE
> the Step 2 dispatch — a checker drowning in ~100 spurious findings would
> have made Step 3's manual read unreliable.

- [x] **Step 2: Dispatch the full run**

One FRESH `general-purpose` subagent:

```
You are working in /Users/lowell/Projects/alt-nfp. You have the personal
skill describe-critique-methodology installed at
/Users/lowell/Projects/agent-skills/skills/describe-critique-methodology/ —
read its SKILL.md and follow it exactly, with ONE waiver for this
verification run: treat the skill's commit step as already done — do NOT
run git commands or commit anything. Task: describe the methodology of the
nfp-model package for external critique. Write the output file where the
skill says to; reply with the output file path followed by the full
handoff message the skill tells you to deliver.
```

- [x] **Step 3: Verify the artifact**

Against `/Users/lowell/Projects/alt-nfp/specs/nfp-model-methodology.md`:
- All six module-template slots present; notation closed (spot-check: every symbol in the equations appears in the table).
- The methodology routing header present verbatim (the `> For agentic workers: when specs/<name>-critique.md exists beside this file ...` block, with `<name>` = `nfp-model`).
- `python3 skills/describe-critique-methodology/scripts/check_decoupling.py /Users/lowell/Projects/alt-nfp/specs/nfp-model-methodology.md` — read every finding AND every `[notation-table]` warning manually, plus the notation table itself; real smuggling (including identifiers "defined" as symbols) fails this step.
- The subagent's reply ends with the handoff message containing the scripted re-entry utterance.

On failure: fix the skill text (not the artifact), delete the artifact, re-dispatch. Max two iterations, then surface to the user with the observed failure.

> **Deviation (Task 7 Step 3, granularity):** the step anticipated the
> **module** template, but the run chose **system** — as did 5/5 MT1 reps on
> this same target, because the package holds three composing components
> (private-payroll leg, government-wedge leg, nowcast readout). That is the
> skill's step-1 granularity choice working as designed, not a failure, so
> it was verified against the system slots. All six present (Component
> inventory / Composition / Cross-component assumptions / Notation /
> Per-component descriptions A–C, each carrying the module slots / Open
> questions ×12). `<name>` was pinned to `nfp-model` in the dispatch so this
> step's literal path check stayed deterministic (MT1 reps had produced both
> `nfp-model-…` and `nfp-nowcast-…` names).
>
> **PASSED first iteration, no re-dispatch.** Routing header verbatim.
> Validator: 12 advisory findings + 2 `[notation-table]` warnings, every one
> read in place — all legitimate LaTeX (`\beta_1`, `\varepsilon_1`,
> `\sum_n`, `c_u`), the required routing-header path, one prose false
> positive ("entry/exit."), and the two warnings are `G^{\mathrm{NSA}}_t` /
> `\sigma^{\mathrm{NSA}}_v` superscript artifacts confirmed absent from
> `packages/nfp-model/src`. **Zero smuggled identifiers.** The reply ended
> with the handoff message carrying the scripted re-entry utterance.
>
> One honest caveat: under the no-git waiver the handoff message's first
> line still reads "committed" while the file is uncommitted — an artifact
> of the waiver, not a skill defect.
>
> The run also surfaced a **repo-state finding for the user** (not a skill
> issue): `alt-nfp/specs/alt-nfp-model-methodology.md` (commit e0f08ef)
> describes a method that does not match the checkout and cites a
> `kalman.py` that has never existed in that repo, and the four root
> `alt-nfp-methodology*.md` files are untracked and dated after the last
> commit. Worth adjudicating before spending an interactive critique
> session.

- [x] **Step 4: User gate — the artifact and the round-trip**

> **PENDING USER ACTION (Task 7 Step 4).** The gate text below was delivered
> verbatim in the execution session's final message. No answer was received
> in-session (non-interactive), so this is **not** ticked as satisfied: the
> alt-nfp artifact remains uncommitted and unreviewed, spec Verification
> bullet 5 stays open, and plan #2 stays gated. Record the alt-nfp commit
> sha here when the user confirms.

Tell the user, verbatim except the path: "Full Describe-mode run passed on alt-nfp. Please review `/Users/lowell/Projects/alt-nfp/specs/nfp-model-methodology.md` and commit it in alt-nfp if it earns its keep — that commit is leg 1 of the real describe→Chat→critique round-trip that gates plan #2 (spec Req 13). The critique-prompt to paste into Chat Research is in the skill's references/." Do not commit in alt-nfp yourself. When the user confirms, record the alt-nfp commit sha in this plan's markup — it closes spec Verification bullet 5 ("a committed specs/<name>-methodology.md") and is leg 1 of plan #2's gate.

- [x] **Step 5: Commit any final skill fixes**

If Step 3 iterations touched skill files: lints, then commit as `refactor(describe-critique-methodology): full-run fixes — <one line>`.

---

### Task 8: Neighbor tweaks (Req 14 remainder)

Implements: Req 14's neighbor tweaks (docs-writer exclusion; design-architecture headroom check). The README and CLAUDE.md documentation edits ride Task 3's skill commit (spec Verification bullet 8: same commit as the skill they describe).

**Files:**
- Modify: `agents/docs-writer.md` (out-of-lane note)
- Verify only: `skills/design-architecture/SKILL.md` (headroom check — expected outcome: skip)

**Interfaces:**
- Consumes: final skill wording (Task 7).
- Produces: nothing downstream in this plan; plan #2 repeats this shape for derive-roadmap.

- [x] **Step 1: docs-writer out-of-lane note**

In `agents/docs-writer.md`, append to the Lanes list:

```markdown
- **Not this agent's lane:** system/module methodology descriptions
  deliberately decoupled from code (the describe-critique-methodology
  skill's Describe-mode output). The grounding rule above — read the code,
  verify every claim against source — is anti-decoupling by design there;
  decline the dispatch and point the caller at that skill.
```

- [x] **Step 2: design-architecture headroom check (expected: skip)**

```bash
uv run --python 3.13 --with pyyaml python -c "
import pathlib, re, yaml
t = pathlib.Path('skills/design-architecture/SKILL.md').read_text()
fm = yaml.safe_load(re.match(r'^---\n(.*?)\n---\n', t, re.S).group(1))
print(1024 - len(fm['description'].strip()))
"
```

> **Deviation (Task 8 Step 2) — conscious skip, as predicted.** Measured
> **5** characters of headroom, exactly the plan's expectation. No
> meaningful reciprocal fence fits in 5 chars, so spec Req 14's fence is
> **deliberately not shipped** and `skills/design-architecture/SKILL.md` is
> unchanged. Recorded in the Task 8 commit message.

Expected: `5` (verified at plan-writing time; an earlier 2026-07-25 measurement of 4 was off by one). Spec Req 14 ships the reciprocal fence **only if** wording fits the headroom; no meaningful fence fits in 5 characters, so record the conscious skip as a deviation note under this step and change nothing. (If the number is unexpectedly large — the description was trimmed since — add a fence only if it fits without displacing existing triggers, e.g. `; methodology write-ups for external critique go to describe-critique-methodology`, and re-run the frontmatter lint.)

- [x] **Step 3: Lints + commit**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
cd skills/describe-critique-methodology/scripts && uv run --python 3.13 --with pytest python -m pytest -q && cd ../../..
git branch --show-current && git status
git add agents/docs-writer.md
git commit -m "docs(agents): docs-writer out-of-lane note for methodology descriptions; design-architecture fence skip recorded"
```

Expected: lints 0, ~~`14 passed`~~ **`18 passed`** (the Task 4 validator fix
added 4 tests; CLAUDE.md's documented count was updated in the same commit).
Actual: both lints exit 0, 18 passed.

---

### Task 9: Deployment (Req 12 precondition + install)

Implements: Req 12 (listing-budget precondition, residency check), writing-skills deployment checklist. Mostly outside git — expect no repo commit.

**Files:**
- Modify: `/Users/lowell/.claude/settings.json` (add `skillListingBudgetFraction`)
- Create: symlink `/Users/lowell/.claude/skills/describe-critique-methodology`

**Interfaces:**
- Consumes: the completed, committed skill (Tasks 1–8).
- Produces: a deployed skill; the user's `/context` confirmation is the final verification artifact (record the result in this plan's markup).

- [x] **Step 1: Raise the listing budget**

Edit `/Users/lowell/.claude/settings.json`: after the `"cleanupPeriodDays": 3650,` line, insert:

```json
  "skillListingBudgetFraction": 0.025,
```

(Read the file first; the user edits it too. Preserve all existing keys. The listing is measured at ~2.11× the default ~2K budget with whole-description drop-by-rank eviction, and a NEW skill is unranked — first to evict. Residency is a correctness precondition, not a cost line.)

- [x] **Step 2: Install the symlink**

```bash
ln -s /Users/lowell/Projects/agent-skills/skills/describe-critique-methodology /Users/lowell/.claude/skills/describe-critique-methodology
ls -la /Users/lowell/.claude/skills/describe-critique-methodology
```

The symlink resolves through the primary checkout's working tree, so it works only while `feat/describe-critique-methodology` (or, post-merge, `main`) is checked out there — if the user switches this repo back to `main` before merging, the link dangles and the skill silently vanishes from listings. If (against the plan's recommendation) execution ran in a worktree, defer this step and Step 3 to after branch integration and say so.

- [x] **Step 3: User verification gate (fresh session, user-run)**

> **Steps 1–2 DONE.** `skillListingBudgetFraction: 0.025` inserted into
> `/Users/lowell/.claude/settings.json` after `cleanupPeriodDays` (file
> re-read first; all existing keys preserved; JSON re-parsed to verify).
> Symlink created and resolving:
> `~/.claude/skills/describe-critique-methodology -> …/agent-skills/skills/describe-critique-methodology`
> (SKILL.md + references + scripts all visible through it). Partial
> in-session evidence that install worked: the skill appeared in this
> session's own skill listing after the full-run dispatch.
>
> **PENDING USER ACTION (Step 3).** The `/context` residency check needs a
> NEW session and a human; the gate text below was delivered verbatim in the
> final message. Not ticked as satisfied — record the answer here. If a
> pre-existing skill dropped out of the listing, stop and raise the fraction
> rather than accepting the eviction.

Ask the user, verbatim: "Deployment needs one check I can't run from inside this session: open a NEW Claude Code session and run `/context` — confirm (a) `describe-critique-methodology` appears among the listed skill descriptions and (b) no existing personal skill dropped out of the listing. Settings now carry `skillListingBudgetFraction: 0.025`, which takes effect in that new session. One caveat until the branch merges: keep `feat/describe-critique-methodology` checked out in agent-skills, or the new skill's symlink dangles — and re-run the `/context` check once after integration." Record the user's answer in the plan markup. If a skill did drop out, stop and surface — the fraction may need a further raise; do not silently accept eviction.

- [x] **Step 4: Close the writing-skills checklist**

Confirm each item and record: RED baselines run before GREEN (Task 2); description "Use when…", third person, ≤1024, trigger-only (Task 3, micro-tested Tasks 4–6); Describe mode re-run WITH the skill (Task 7) — Synthesize-mode scenario verification consciously deferred to the real round-trip / plan #2 (spec Req 13; carry as a deviation note, not a tick); loopholes closed (Tasks 4–7 revision cycles); committed to git (Tasks 1–8). No push — the user pushes/merges explicitly. **STOP here: do not begin derive-roadmap (plan #2) — it is gated on the user's real round-trip (spec Req 13).**

> **writing-skills checklist — recorded:**
> - RED baselines before GREEN — **yes**, 7 no-skill runs (Task 2) preceded
>   any skill text; the Iron Law ordering held throughout.
> - Description "Use when…", third person, ≤1024 chars, triggers only —
>   **yes**, lint-enforced (`check_frontmatter.py` green on every commit).
> - Micro-tested wording — **yes**, MT1/MT2/MT3, each with a real
>   no-guidance control arm; all three KEEP.
> - Describe mode re-run WITH the skill — **yes**, Task 7, passed first
>   iteration.
> - **Synthesize mode: consciously UNTESTED — deviation, not a tick.** No
>   scenario verification exists for it; it ships on spec-fixed workflow
>   text pending the real round-trip (spec Req 13) and plan #2. MT2 verified
>   only that the mode is *routed to* correctly, not that it *behaves*
>   correctly once entered.
> - Loopholes closed — **n/a**, no revision cycles were needed (zero
>   micro-test failures); the one defect found was in the validator, fixed
>   and pinned by a test.
> - Committed to git — **yes**, 4 commits + this markup on
>   `feat/describe-critique-methodology`. **Not pushed, not merged** — the
>   user decides integration.
> - **STOP observed: derive-roadmap (plan #2) NOT started.**

---

## After the last task

Run the Plan Completion Protocol (writing-plans § Plan Completion Protocol): resolve-before-defer gate, plan markup with deviation notes, `specs/deferred_items.md` — **including the Req 15 DL/NLP extension entry with its conditional-slot sketches** ("if trained → training objective; if pipeline-assembled → assembly policy") and known breakage cases (RAG: no estimation procedure, methodology lives in assembly choices; fine-tuned classifier: no data-generating story; checkpoint/tokenization/schedule slots) **and the Out-of-scope in-session SOTA pass** (WebSearch + paper-search + llm-wiki query as a Chat alternative) — then retire this plan to `specs/plans/completed/`. **Do NOT retire the spec**: plan #2 (`<id>-methodology-pipeline-skills.md`) is still unwritten, and the spec stays live until both plans complete (Req 13's same-suffix rule). Integration decision (merge/PR, worktree cleanup) via finishing-a-development-branch, user-approved.
