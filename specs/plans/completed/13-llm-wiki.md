# llm-wiki M0 Tooling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the buildable M0 core of the personal research wiki (Karpathy LLM-wiki pattern): retention protection, the `research-wiki` repo scaffold, its `SCHEMA.md`, the stdlib mechanical linter `lint_wiki.py`, and the `llm-wiki` skill — so that literature can be ingested afterward.

**Architecture:** Two repositories. A new **`research-wiki`** repo (default `~/research-wiki`, overridable via `$LLM_WIKI_ROOT`) holds immutable `raw/` sources, an agent-written `wiki/`, `reports/`, `scripts/`, and a normative `SCHEMA.md`. A thin **`llm-wiki` skill** lives in the existing **`agent-skills`** repo (`skills/llm-wiki/SKILL.md`, symlinked into `~/.claude/skills/`) and carries only procedure — every wiki-specific format lives in `SCHEMA.md` so the skill stays reusable for a second wiki. The mechanical linter is deterministic, stdlib-only, and is the precondition for every status flip.

**Tech Stack:** Python ≥ 3.12 (tested on Homebrew 3.13 via `uv run`), standard library only — no third-party deps, **no `pyyaml`**. Markdown wiki pages with YAML-ish frontmatter. Git, one repo per layer.

## Repositories referenced by this plan

- **`~/research-wiki`** — the wiki repo this plan creates (`git init` in Task 2). All `raw/…`, `wiki/…`, `reports/…`, `scripts/…`, `SCHEMA.md` paths below are inside it. Equals `$LLM_WIKI_ROOT` (default `~/research-wiki`).
- **`agent-skills`** — the existing repo at `/Users/lowell/Projects/agent-skills` (where this plan file lives). Only Task 11 writes here: `skills/llm-wiki/SKILL.md`, `NOTICE`, `CLAUDE.md`.
- **`~/.claude/`** — user config. Task 1 edits `settings.json`; Task 11 creates a symlink under `skills/`.

## Global Constraints

Copied verbatim from the spec (`specs/completed/llm-wiki-spec.md` §10, §14); every task's requirements implicitly include these.

- **Python:** stdlib only; `pathlib` over `os.path`; single quotes; **two-space indentation**; Python ≥ 3.12. `lint_wiki.py` imports only from `pathlib`, `re`, `argparse`, `sys`, `os` (for `$LLM_WIKI_ROOT`). **No `import yaml`** — the frontmatter parser is hand-rolled (the repo's `build/check_frontmatter.py` uses pyyaml; do **not** copy that here).
- **Dates:** ISO-8601 (`YYYY-MM-DD`) everywhere.
- **Wiki root:** resolved from `$LLM_WIKI_ROOT`, defaulting to `~/research-wiki`.
- **Wiki prose:** declarative, claim-per-sentence where locators attach, no rhetorical hedging (the `status` field is the hedge).
- **Skill file:** frontmatter needs `name` (== directory name) + `description` (≤1024 chars); body ≤150 lines; reference `SCHEMA.md` as **inline code**, never a markdown link (the repo's `check_frontmatter.py` `LINK_RE` would try to resolve a `](SCHEMA.md)` target in the wrong repo and fail); no bundled `references/` or `scripts/`.
- **Provenance gate:** `skills/llm-wiki/` must be attributed in `agent-skills/NOTICE` and cross-listed in `agent-skills/CLAUDE.md`, or `build/check_provenance.py` fails (Task 11).

## Out of scope (do NOT attempt as plan tasks)

- **`scripts/distill_sessions.py`** (spec §16.4) — the session-history distiller is a second, independent subsystem. It ships as **Plan 14**. This plan's linter validates the digest *format* it will produce (Task 9) using hand-written fixtures, so the two meet at `SCHEMA.md`, not in code.
- **Content milestones M1–M3, S1–S3** (spec §13, §16.7) — ingesting papers, verifying pages, semantic-lint passes, file-backs. These are *operations run with the skill*, not code; they have no red→green cycle and belong to normal use after this plan lands.
- **The claude.ai data-export request** (spec §16.1.3) is a manual, user-only action; it appears in Task 1 as a reminder, not an automatable step.

## Test command

The wiki scripts are stdlib-only and directory-scoped (bare imports, tests co-located), matching the `agent-skills` convention:

```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Run a single test:

```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py::test_name -q
```

---

### Task 1: S0 — retention protection (urgent, no TDD)

Spec §16.1 / §16.7 S0. Claude Code hard-deletes session transcripts older than the retention window at startup, with no recovery. `cleanupPeriodDays` is currently **unset** (30-day default is live) and `~/.claude/projects/` holds ~354 MB of transcripts. This task protects the distiller's future input; it is independent of the rest of the plan and should be done **first / immediately**.

**Files:**
- Modify: `~/.claude/settings.json` (add one key)
- Create: `~/archives/claude-projects-<date>.tar.gz` (archive of record, outside any repo)

**Interfaces:**
- Consumes: nothing.
- Produces: nothing other tasks depend on. (Plan 14's distiller will read the tarball and the live `~/.claude/projects/`.)

- [x] **Step 1: Check the current setting (skip the task if already fixed)**

Run:
```bash
python3 -c "import json,os;p=os.path.expanduser('~/.claude/settings.json');d=json.load(open(p));print('cleanupPeriodDays =', d.get('cleanupPeriodDays','<unset>'))"
```
Expected: `cleanupPeriodDays = <unset>` (if it already prints `3650`, Steps 2 is done — go to Step 3).

- [x] **Step 2: Set `cleanupPeriodDays: 3650` (never 0)**

Editing the user's global `~/.claude/settings.json` is a persistent-config change — get an explicit go-ahead first. Add the key (preserving all existing keys):

```bash
python3 - <<'PY'
import json, os
p = os.path.expanduser('~/.claude/settings.json')
d = json.load(open(p))
d['cleanupPeriodDays'] = 3650
json.dump(d, open(p, 'w'), indent=2)
print('set cleanupPeriodDays =', d['cleanupPeriodDays'])
PY
```
Expected: `set cleanupPeriodDays = 3650`. **Never set 0** — a known bug makes 0 disable transcript persistence entirely rather than disable cleanup.

- [x] **Step 3: Snapshot `~/.claude/projects/` outside the wiki repo**

Run:
```bash
mkdir -p ~/archives && tar -czf ~/archives/claude-projects-$(date +%F).tar.gz -C ~ .claude/projects && ls -lh ~/archives/claude-projects-*.tar.gz
```
Expected: a listed `.tar.gz` of non-trivial size (tens of MB). This dated tarball is the archive of record for raw JSONL; only digests (Plan 14) ever enter the repo.

- [x] **Step 4: Request the claude.ai data export (manual, user-only)**

Not automatable — remind the user to do it in the browser: **claude.ai → Settings → Privacy → Export data**. It arrives later as `conversations.json` and feeds Plan 14's S2 track. Note in the handoff that this was requested; there is nothing to commit (all paths are outside both git repos).

---

### Task 2: Scaffold the `research-wiki` repo

Spec §5. Create the repo and its directory tree with seed structural files, so the linter (Tasks 4–10) has an empty-but-valid wiki to run against. No application code here — the deliverable is a committed, well-formed tree.

**Files (all under `~/research-wiki`):**
- Create: `raw/{samplers,nowcasting,benchmarks,sessions,assets}/.gitkeep`
- Create: `wiki/{sources,samplers,nowcasting}/.gitkeep`
- Create: `wiki/index.md`, `wiki/log.md`, `wiki/open-questions.md`
- Create: `reports/.gitkeep`, `scripts/.gitkeep`
- Create: `.gitignore`, `README.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the tree the linter treats as ROOT. Pages live one level under `wiki/` (`wiki/sources/`, `wiki/samplers/`, `wiki/nowcasting/`); the three structural files (`index.md`, `log.md`, `open-questions.md`) live directly under `wiki/` and are **not** pages.

- [x] **Step 1: Create the directory tree and keep-files**

Run:
```bash
mkdir -p ~/research-wiki && cd ~/research-wiki && \
mkdir -p raw/samplers raw/nowcasting raw/benchmarks raw/sessions raw/assets \
         wiki/sources wiki/samplers wiki/nowcasting reports scripts && \
touch raw/samplers/.gitkeep raw/nowcasting/.gitkeep raw/benchmarks/.gitkeep \
      raw/sessions/.gitkeep raw/assets/.gitkeep \
      wiki/sources/.gitkeep wiki/samplers/.gitkeep wiki/nowcasting/.gitkeep \
      reports/.gitkeep scripts/.gitkeep
```
Expected: no output, exit 0.

- [x] **Step 2: Write the seed structural files**

`~/research-wiki/wiki/index.md`:
```markdown
# Wiki index

One line per page, grouped by topic. See SCHEMA.md §index.

## samplers

## nowcasting
```

`~/research-wiki/wiki/log.md`:
```markdown
# Operation log

Append-only. Grammar: `## [YYYY-MM-DD] <op> | <subject> | <note>`. See SCHEMA.md §log.
```

`~/research-wiki/wiki/open-questions.md`:
```markdown
# Open questions

Contradictions and gaps awaiting resolution. See SCHEMA.md §contradictions.
```

`~/research-wiki/.gitignore`:
```gitignore
__pycache__/
*.pyc
.DS_Store
.pytest_cache/
```

`~/research-wiki/README.md`:
```markdown
# research-wiki

Personal research wiki (Karpathy LLM-wiki pattern). `raw/` is immutable source
material (human-curated); `wiki/` is agent-compiled knowledge; `SCHEMA.md` is
the normative contract the `llm-wiki` skill and `scripts/lint_wiki.py` enforce.
Resolve the root via `$LLM_WIKI_ROOT` (default `~/research-wiki`).
```

- [x] **Step 3: Initialize git and commit the scaffold**

Run:
```bash
cd ~/research-wiki && git init -q && git add -A && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'chore: scaffold research-wiki repo layout' && \
git log --oneline -1
```
Expected: one commit line printed. Confirm the tree:
```bash
cd ~/research-wiki && find . -path ./.git -prune -o -type f -print | sort
```
Expected: lists `.gitignore`, `README.md`, the three `wiki/*.md` files, and the `.gitkeep` files.

---

### Task 3: Transcribe `SCHEMA.md`

Spec §6–§9 plus the transcription mandates in §16.3 (epistemic rules) and §16.5 (capture-note format). `SCHEMA.md` is the contract the linter and skill both read; it is transcribed from **this spec's prose (Lowell's), never from Karpathy's gist or `kfchou/wiki-skills`** — so no external prose enters the repo and no license binds.

**Files:**
- Create: `~/research-wiki/SCHEMA.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the normative definitions the linter encodes (Tasks 4–10) and the skill dispatches (Task 11). Section anchors referenced later: page frontmatter keys/enums, quarantine rule, index format, log grammar, capture-note grammar.

- [x] **Step 1: Write `~/research-wiki/SCHEMA.md`**

````markdown
# SCHEMA — research-wiki normative formats

This file is the machine-readable contract. `scripts/lint_wiki.py` enforces the
mechanical parts; the `llm-wiki` skill reads this file before any operation.
Transcribed from the llm-wiki spec §6–§9, §16.3, §16.5.

## Page format

Three page types. Frontmatter is the machine-readable contract.

```yaml
---
title: Microcanonical Langevin Monte Carlo
type: concept            # source | concept | synthesis
status: unverified       # unverified | verified
topics: [samplers]
cites: [sources/robnik-2022-mclmc]   # concept/synthesis only
updated: 2026-07-22
---
```

Frontmatter is flat: scalar values and single-line bracketed lists only. Inline
`#` annotations shown above are illustrative — do **not** write them into real
pages. Required keys on every page: `title`, `type`, `status`, `topics`,
`updated`. Enums: `type ∈ {source, concept, synthesis}`;
`status ∈ {unverified, verified}`.

Per-type keys:

- `type: source` — carries `raw:` (e.g. `raw: raw/samplers/robnik-2022-mclmc.pdf`)
  instead of `cites`. The page filename stem matches the raw file stem. A source
  page is the agent's summary of one raw source; it is not trusted by
  construction and starts `unverified`.
- `type: concept` — an entity page (a sampler, a method, an estimator). Carries
  `cites`, not `raw`.
- `type: synthesis` — a comparison, decision, or filed-back answer spanning
  sources. Carries `cites`, not `raw`.

### Quarantine rule (load-bearing)

`cites` may only list pages of `type: source` with `status: verified`. Anything
else is a lint error. Consequence: an unverified summary — including any freshly
filed-back answer — cannot become grounds for anything else until checked. This
is the circular-self-citation guard.

### Body conventions

Prose-first; relative links only; no H1 (title lives in frontmatter). Every
quantitative or attributable claim carries an inline locator in square brackets
referencing a source-page slug plus a position: `[robnik-2022-mclmc §4.2]`,
`[hoffman-2014-nuts Table 2]`. Contradictory claims are recorded adjacently with
both locators and a one-line note, then logged to `open-questions.md`. Session
digest source pages structure their body as capture notes (below), not prose.

## index

`wiki/index.md`: one line per page, grouped by topic heading:

```
## samplers
- [mclmc](samplers/mclmc.md) — microcanonical dynamics; tuning-free ESS claims · 3 sources · verified · 2026-07-22
```

Parity holds in both directions: every page on disk has exactly one index line;
every index line resolves to a page.

## log

`wiki/log.md`: append-only, one line per operation, grep-parseable:

```
## [2026-07-22] ingest | robnik-2022-mclmc | 1 source page, 2 concept pages touched
## [2026-07-22] lint-mechanical | clean
```

Grammar: `## [YYYY-MM-DD] <op> | <subject> | <note>`, with
`op ∈ {ingest, file-back, verify, lint-mechanical, lint-semantic, schema}`.
Every mutating operation appends a line. Plain queries are logged only when they
file back or expose a coverage gap.

## contradictions

A new claim conflicting with an existing one is never overwritten — both are
kept with locators, and an entry is appended to `open-questions.md`.

## Operations (dispatched by the skill; see the skill for procedure)

- **ingest** — one source, supervised: read source, propose 3–5 takeaways +
  source-page draft + concept touch-list; on approval write source page
  (`unverified`), edit concept pages (each new claim carries a locator), update
  `index.md`, append to `log.md`. New concept page only for an entity linked
  from ≥2 pages; ceiling one new concept page per ingest without approval.
- **query** — index-first: read `index.md`, select ≤5 pages, answer with page
  references and locators; open raw only if pages are insufficient (a coverage
  gap). File-back only when synthesizing ≥2 sources or recording a decision;
  filed pages are `type: synthesis`, `status: unverified`.
- **lint** — mechanical (`scripts/lint_wiki.py`) then semantic (agent pass).
- **verify** — walk every locator-carrying claim, open the cited source page's
  raw file at the locator, confirm or flag; all confirmed → `status: verified`.

## Epistemic rules for session digests (spec §16.3)

1. **Echo rule.** The assistant's proposals are not the user's decisions. A
   capture of `kind: decision` requires `basis: user-turn` (the user states or
   confirms it, with a turn locator) or `basis: git:<sha>` (the decision landed
   in code). An unadopted assistant proposal is captured, if at all, as
   `kind: rejected-approach`. No `decision` captures from compaction-summary
   text — decisions require verbatim turns.
2. **Staleness.** Every capture carries the session date from its digest header;
   claims about code are dated claims, suspect once the referenced files change.
3. **Secrets.** Redaction happens at distillation and is not optional; any
   residual secret-shaped string under `raw/sessions/` is a lint error.

## Capture-note format for session-digest source pages (spec §16.5)

A session-digest source page's body is atomic capture notes, not prose:

```
### [d-03] Blackjax stays the sampler layer; NumPyro the model layer
kind: decision · turns: 18–24 · basis: user-turn
One- to three-sentence self-contained statement of the capture.
```

Kinds and id prefixes: `decision` (d), `rejected-approach` (r), `gotcha` (g),
`resolved-confusion` (c), `validated-pattern` (p). The metadata line is
regex-checkable; lint enforces the echo rule on `decision` captures mechanically.
````

- [x] **Step 2: Sanity-check required sections exist, then commit**

Run:
```bash
cd ~/research-wiki && grep -qE '## Quarantine rule|### Quarantine rule' SCHEMA.md && \
grep -q 'Echo rule' SCHEMA.md && grep -q 'Capture-note format' SCHEMA.md && \
echo 'SCHEMA sections present'
```
Expected: `SCHEMA sections present`.

```bash
cd ~/research-wiki && git add SCHEMA.md && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'docs: transcribe SCHEMA.md from spec §6-§9, §16.3, §16.5' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 4: `lint_wiki.py` — skeleton, frontmatter parser, output & exit contract

Spec §10. Establish the CLI, the hand-rolled stdlib frontmatter parser, page discovery, the finding/output format, and exit codes. Deliverable: runs clean on the empty scaffold and exits 0.

**Files:**
- Create: `~/research-wiki/scripts/lint_wiki.py`
- Create: `~/research-wiki/scripts/test_lint_wiki.py`

**Interfaces:**
- Produces (used by every later lint task):
  - `parse_frontmatter(text: str) -> dict | None` — leading `---…---` block → flat dict; bracketed single-line lists become `list[str]`; `None` if no block.
  - `discover_pages(root: Path) -> list[Path]` — sorted `wiki/*/*.md` (pages only; excludes `wiki/index.md`, `wiki/log.md`, `wiki/open-questions.md`).
  - `default_root() -> Path` — `$LLM_WIKI_ROOT` or `~/research-wiki`.
  - `run_checks(root: Path) -> list[tuple[str, str, str]]` — findings as `(severity, path, message)`, `severity ∈ {'ERROR','WARN','INFO'}`.
  - `main(argv: list[str] | None = None) -> int` — prints one line per finding as `f'{sev}  {path}  {msg}'` (two spaces between fields), then a summary line `f'{e} errors, {w} warnings, {i} info'`; returns 1 if any error, or if `--strict` and any warning; else 0.

- [x] **Step 1: Write the failing tests**

`~/research-wiki/scripts/test_lint_wiki.py`:
```python
'''Tests for lint_wiki.py. Stdlib + pytest only; build fixture wikis in tmp.'''
import subprocess
import sys
from pathlib import Path

import lint_wiki


def make_wiki(tmp_path):
  '''Minimal valid empty scaffold mirroring Task 2.'''
  for d in ['raw/samplers', 'raw/sessions', 'wiki/sources', 'wiki/samplers',
            'wiki/nowcasting', 'reports']:
    (tmp_path / d).mkdir(parents=True, exist_ok=True)
  (tmp_path / 'wiki/index.md').write_text('# Wiki index\n\n## samplers\n')
  (tmp_path / 'wiki/log.md').write_text('# Operation log\n')
  (tmp_path / 'wiki/open-questions.md').write_text('# Open questions\n')
  return tmp_path


def write_page(root, relpath, fm, body=''):
  '''relpath is under wiki/, e.g. "sources/x.md". fm is a dict.'''
  lines = ['---']
  for k, v in fm.items():
    if isinstance(v, list):
      lines.append(f'{k}: [{", ".join(v)}]')
    else:
      lines.append(f'{k}: {v}')
  lines += ['---', '', body, '']
  p = root / 'wiki' / relpath
  p.parent.mkdir(parents=True, exist_ok=True)
  p.write_text('\n'.join(lines))
  return p


def test_parse_frontmatter_scalars_and_lists():
  fm = lint_wiki.parse_frontmatter(
    '---\ntitle: X\ntype: concept\ntopics: [samplers]\n'
    'cites: [sources/a, sources/b]\n---\nbody\n')
  assert fm['title'] == 'X'
  assert fm['type'] == 'concept'
  assert fm['topics'] == ['samplers']
  assert fm['cites'] == ['sources/a', 'sources/b']


def test_parse_frontmatter_none_when_absent():
  assert lint_wiki.parse_frontmatter('no frontmatter here') is None


def test_discover_pages_excludes_structural_files(tmp_path):
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md',
             {'title': 'A', 'type': 'source', 'status': 'unverified',
              'topics': '[samplers]', 'raw': 'raw/samplers/a.pdf',
              'updated': '2026-07-22'})
  pages = lint_wiki.discover_pages(root)
  names = {p.name for p in pages}
  assert 'a.md' in names
  assert 'index.md' not in names and 'log.md' not in names


def test_empty_scaffold_is_clean(tmp_path):
  root = make_wiki(tmp_path)
  assert lint_wiki.run_checks(root) == []


def test_main_exit_zero_on_clean_scaffold(tmp_path):
  root = make_wiki(tmp_path)
  assert lint_wiki.main([str(root)]) == 0
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q
```
Expected: FAIL — `ModuleNotFoundError: No module named 'lint_wiki'` (or `AttributeError` once the file exists but functions don't).

- [x] **Step 3: Write the minimal implementation**

`~/research-wiki/scripts/lint_wiki.py`:
```python
'''Mechanical linter for the research-wiki (spec §10). Stdlib only; no yaml.'''
import argparse
import os
import re
import sys
from pathlib import Path

STRUCTURAL = {'index.md', 'log.md', 'open-questions.md'}


def parse_frontmatter(text):
  '''Parse a leading --- ... --- block into a flat dict. Scalars are strings;
  single-line bracketed lists become list[str]. Returns None if no block.
  Inline # comments are not part of real frontmatter and are kept literal.'''
  m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
  if not m:
    return None
  fm = {}
  for line in m.group(1).split('\n'):
    if not line.strip() or ':' not in line:
      continue
    key, _, val = line.partition(':')
    key, val = key.strip(), val.strip()
    if val.startswith('[') and val.endswith(']'):
      inner = val[1:-1].strip()
      fm[key] = [v.strip() for v in inner.split(',')] if inner else []
    else:
      fm[key] = val
  return fm


def discover_pages(root):
  '''Wiki content pages: one level under wiki/. Structural files live directly
  under wiki/ and are excluded.'''
  return sorted(
    p for p in (root / 'wiki').glob('*/*.md') if p.name not in STRUCTURAL)


def default_root():
  return Path(os.environ.get('LLM_WIKI_ROOT', str(Path.home() / 'research-wiki')))


def run_checks(root):
  '''Return a list of (severity, path, message) findings.'''
  findings = []
  # check functions are wired in by later tasks
  return findings


def main(argv=None):
  ap = argparse.ArgumentParser(description='Mechanical linter for research-wiki.')
  ap.add_argument('--strict', action='store_true',
                  help='warnings also cause a non-zero exit')
  ap.add_argument('root', nargs='?', default=None,
                  help='wiki root (default $LLM_WIKI_ROOT or ~/research-wiki)')
  args = ap.parse_args(argv)
  root = Path(args.root) if args.root else default_root()
  findings = run_checks(root)
  errors = sum(1 for f in findings if f[0] == 'ERROR')
  warnings = sum(1 for f in findings if f[0] == 'WARN')
  infos = sum(1 for f in findings if f[0] == 'INFO')
  for sev, path, msg in findings:
    print(f'{sev}  {path}  {msg}')
  print(f'{errors} errors, {warnings} warnings, {infos} info')
  if errors or (args.strict and warnings):
    return 1
  return 0


if __name__ == '__main__':
  sys.exit(main())
```

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q
```
Expected: PASS (5 passed).

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/lint_wiki.py scripts/test_lint_wiki.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(lint): skeleton, frontmatter parser, output/exit contract' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 5: `lint_wiki.py` — frontmatter schema check (error)

Spec §10 row "Frontmatter schema violation". Required keys, enum values, and the per-type key rule (`source`→`raw` present & `cites` absent; `concept`/`synthesis`→`cites` present & `raw` absent). The three structural files are already excluded by `discover_pages`, so the empty scaffold stays clean.

**Files:**
- Modify: `~/research-wiki/scripts/lint_wiki.py`
- Modify: `~/research-wiki/scripts/test_lint_wiki.py`

**Interfaces:**
- Consumes: `parse_frontmatter`, `discover_pages` (Task 4).
- Produces: `check_frontmatter_schema(root, pages) -> list[tuple]`, wired into `run_checks`.

- [x] **Step 1: Write the failing tests**

Append to `test_lint_wiki.py`:
```python
def test_missing_required_key_is_error(tmp_path):
  root = make_wiki(tmp_path)
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'concept', 'status': 'unverified',
              'cites': '[sources/a]'})  # no topics, no updated
  sevs = [f for f in lint_wiki.run_checks(root) if f[0] == 'ERROR']
  assert any('topics' in f[2] or 'updated' in f[2] for f in sevs)


def test_bad_enum_is_error(tmp_path):
  root = make_wiki(tmp_path)
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'concept', 'status': 'maybe',
              'topics': '[samplers]', 'cites': '[sources/a]',
              'updated': '2026-07-22'})
  assert any(f[0] == 'ERROR' and 'status' in f[2] for f in lint_wiki.run_checks(root))


def test_source_with_cites_is_error(tmp_path):
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md',
             {'title': 'A', 'type': 'source', 'status': 'unverified',
              'topics': '[samplers]', 'cites': '[sources/b]',
              'updated': '2026-07-22'})
  assert any(f[0] == 'ERROR' and 'cites' in f[2] for f in lint_wiki.run_checks(root))


def test_concept_without_cites_is_error(tmp_path):
  root = make_wiki(tmp_path)
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'concept', 'status': 'unverified',
              'topics': '[samplers]', 'updated': '2026-07-22'})  # no cites
  assert any(f[0] == 'ERROR' and 'cites' in f[2] for f in lint_wiki.run_checks(root))


def test_valid_pages_are_clean(tmp_path):
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md',
             {'title': 'A', 'type': 'source', 'status': 'verified',
              'topics': '[samplers]', 'raw': 'raw/samplers/a.pdf',
              'updated': '2026-07-22'})
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'concept', 'status': 'unverified',
              'topics': '[samplers]', 'cites': '[sources/a]',
              'updated': '2026-07-22'},
             body='Claim [a §1].')
  assert [f for f in lint_wiki.run_checks(root)
          if f[0] == 'ERROR' and 'frontmatter' in f[2].lower()] == []
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -k frontmatter_schema_or -q
```
Actually run the four new tests:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "required_key or bad_enum or source_with_cites or concept_without_cites"
```
Expected: FAIL — no errors emitted yet (the checks are unwired).

- [x] **Step 3: Write the implementation**

In `lint_wiki.py`, add the constants and function, and wire it into `run_checks`:
```python
REQUIRED_KEYS = ('title', 'type', 'status', 'topics', 'updated')
TYPES = ('source', 'concept', 'synthesis')
STATUSES = ('unverified', 'verified')


def check_frontmatter_schema(root, pages):
  findings = []
  for p in pages:
    rel = p.relative_to(root)
    fm = parse_frontmatter(p.read_text())
    if fm is None:
      findings.append(('ERROR', str(rel), 'frontmatter: no --- block'))
      continue
    for k in REQUIRED_KEYS:
      if k not in fm:
        findings.append(('ERROR', str(rel), f'frontmatter: missing key {k!r}'))
    ptype = fm.get('type')
    if ptype not in TYPES:
      findings.append(('ERROR', str(rel), f'frontmatter: bad type {ptype!r}'))
    if fm.get('status') not in STATUSES:
      findings.append(
        ('ERROR', str(rel), f'frontmatter: bad status {fm.get("status")!r}'))
    if ptype == 'source':
      if 'raw' not in fm:
        findings.append(('ERROR', str(rel), 'frontmatter: source needs raw:'))
      if 'cites' in fm:
        findings.append(('ERROR', str(rel), 'frontmatter: source must not cites:'))
    elif ptype in ('concept', 'synthesis'):
      if 'cites' not in fm:
        findings.append(
          ('ERROR', str(rel), f'frontmatter: {ptype} needs cites:'))
      if 'raw' in fm:
        findings.append(
          ('ERROR', str(rel), f'frontmatter: {ptype} must not raw:'))
  return findings
```
And in `run_checks`, replace the body with:
```python
def run_checks(root):
  findings = []
  pages = discover_pages(root)
  findings += check_frontmatter_schema(root, pages)
  return findings
```

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q
```
Expected: PASS (all Task 4 + Task 5 tests green).

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/lint_wiki.py scripts/test_lint_wiki.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(lint): frontmatter schema + per-type key checks' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 6: `lint_wiki.py` — index/page parity check (error)

Spec §10 row "Index/page parity violation, either direction". Every page on disk has exactly one index line; every index line resolves to a page. Index lines look like `- [slug](topic/slug.md) — …`; the parenthesized target is a path relative to `wiki/`.

**Files:**
- Modify: `~/research-wiki/scripts/lint_wiki.py`
- Modify: `~/research-wiki/scripts/test_lint_wiki.py`

**Interfaces:**
- Consumes: `discover_pages` (Task 4).
- Produces: `check_index_parity(root, pages) -> list[tuple]`, wired into `run_checks`.

- [x] **Step 1: Write the failing tests**

Append to `test_lint_wiki.py`:
```python
def valid_source(root, relpath, stem, status='verified'):
  write_page(root, relpath,
             {'title': stem, 'type': 'source', 'status': status,
              'topics': '[samplers]', 'raw': f'raw/samplers/{stem}.pdf',
              'updated': '2026-07-22'})


def set_index(root, lines):
  (root / 'wiki/index.md').write_text(
    '# Wiki index\n\n## samplers\n' + '\n'.join(lines) + '\n')


def test_page_missing_from_index_is_error(tmp_path):
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a')
  set_index(root, [])  # page exists, no index line
  assert any(f[0] == 'ERROR' and 'index' in f[2].lower()
             for f in lint_wiki.run_checks(root))


def test_index_line_without_page_is_error(tmp_path):
  root = make_wiki(tmp_path)
  set_index(root, ['- [ghost](sources/ghost.md) — nope · 0 · unverified · 2026-07-22'])
  assert any(f[0] == 'ERROR' and 'ghost' in f[2]
             for f in lint_wiki.run_checks(root))


def test_index_parity_clean(tmp_path):
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a')
  set_index(root, ['- [a](sources/a.md) — summary · 1 · verified · 2026-07-22'])
  assert [f for f in lint_wiki.run_checks(root)
          if f[0] == 'ERROR' and 'index' in f[2].lower()] == []
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "index"
```
Expected: FAIL (parity not implemented).

- [x] **Step 3: Write the implementation**

Add to `lint_wiki.py`:
```python
INDEX_LINE_RE = re.compile(r'^- \[[^\]]+\]\(([^)]+)\)')


def _index_targets(root):
  '''Set of index-line targets (paths relative to wiki/, e.g. sources/a.md).'''
  idx = root / 'wiki/index.md'
  if not idx.exists():
    return []
  out = []
  for line in idx.read_text().split('\n'):
    m = INDEX_LINE_RE.match(line.strip())
    if m:
      out.append(m.group(1))
  return out


def check_index_parity(root, pages):
  findings = []
  page_rels = {str(p.relative_to(root / 'wiki')) for p in pages}
  targets = _index_targets(root)
  target_set = set(targets)
  for rel in sorted(page_rels - target_set):
    findings.append(('ERROR', f'wiki/{rel}', 'index: page has no index line'))
  for t in targets:
    if t not in page_rels:
      findings.append(('ERROR', 'wiki/index.md', f'index: line target missing page: {t}'))
  # duplicate index lines for the same page
  for t in target_set:
    if targets.count(t) > 1:
      findings.append(('ERROR', 'wiki/index.md', f'index: duplicate line for {t}'))
  return findings
```
Wire into `run_checks` after the frontmatter check:
```python
  findings += check_index_parity(root, pages)
```

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q
```
Expected: PASS (all green).

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/lint_wiki.py scripts/test_lint_wiki.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(lint): index/page parity check' && git log --oneline -1
```
Expected: one commit line printed.

---

### Task 7: `lint_wiki.py` — links, body-citation slugs, orphan warning

Spec §10 rows "Broken relative links between wiki pages" (error), "Body citation slug with no matching source page" (error), "Orphan page (no inbound links, index excluded)" (warning). A body locator is `[slug §…]` / `[slug Table …]` — a bracket whose first token is a slug and which is **not** a markdown link (not followed by `(`). A source page's slug is its filename stem under `wiki/sources/`.

**Files:**
- Modify: `~/research-wiki/scripts/lint_wiki.py`
- Modify: `~/research-wiki/scripts/test_lint_wiki.py`

**Interfaces:**
- Consumes: `discover_pages`, `parse_frontmatter` (Task 4).
- Produces: `_source_slugs`, `_strip_frontmatter`, `MD_LINK_RE`, `BODY_CITE_RE`, and `check_links(root, pages) -> list[tuple]`, wired into `run_checks`.

- [x] **Step 1: Write the failing tests**

Append to `test_lint_wiki.py`:
```python
def test_broken_relative_link_is_error(tmp_path):
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a')
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'concept', 'status': 'unverified',
              'topics': '[samplers]', 'cites': '[sources/a]',
              'updated': '2026-07-22'},
             body='See [the missing page](../samplers/nope.md).')
  set_index(root, ['- [a](sources/a.md) — s · 1 · verified · 2026-07-22',
                   '- [x](samplers/x.md) — s · 1 · unverified · 2026-07-22'])
  assert any(f[0] == 'ERROR' and 'link' in f[2].lower()
             for f in lint_wiki.run_checks(root))


def test_body_citation_without_source_is_error(tmp_path):
  root = make_wiki(tmp_path)
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'concept', 'status': 'unverified',
              'topics': '[samplers]', 'cites': '[sources/a]',
              'updated': '2026-07-22'},
             body='Tuning-free claim [ghost-2020-none §4.2].')
  set_index(root, ['- [x](samplers/x.md) — s · 1 · unverified · 2026-07-22'])
  assert any(f[0] == 'ERROR' and 'ghost-2020-none' in f[2]
             for f in lint_wiki.run_checks(root))


def test_orphan_page_is_warning(tmp_path):
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a')  # nothing links to it
  set_index(root, ['- [a](sources/a.md) — s · 1 · verified · 2026-07-22'])
  assert any(f[0] == 'WARN' and 'orphan' in f[2].lower()
             for f in lint_wiki.run_checks(root))


def test_strict_flips_warning_to_exit_one(tmp_path):
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a')
  set_index(root, ['- [a](sources/a.md) — s · 1 · verified · 2026-07-22'])
  assert lint_wiki.main([str(root)]) == 0          # warnings don't fail
  assert lint_wiki.main(['--strict', str(root)]) == 1  # unless --strict
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "link or citation or orphan or strict"
```
Expected: FAIL.

- [x] **Step 3: Write the implementation**

Add to `lint_wiki.py`:
```python
# Markdown relative links: [text](target) where target is not a URL/anchor.
MD_LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
# Body citation locators: [slug §x] / [slug Table 2] — slug token then a space,
# and NOT a markdown link (no '(' immediately after the ']').
BODY_CITE_RE = re.compile(r'\[([a-z0-9][a-z0-9-]*)\s+[^\]]+\](?!\()')


def _source_slugs(root):
  return {p.stem for p in (root / 'wiki/sources').glob('*.md')}


def _strip_frontmatter(text):
  m = re.match(r'^---\n.*?\n---\n', text, re.S)
  return text[m.end():] if m else text


def check_links(root, pages):
  findings = []
  slugs = _source_slugs(root)
  referenced = set()  # page paths (relative to wiki/) that something points at
  wiki_abs = (root / 'wiki').resolve()
  for p in pages:
    rel = p.relative_to(root)
    text = p.read_text()
    fm = parse_frontmatter(text) or {}
    body = _strip_frontmatter(text)
    # cites: frontmatter counts as an inbound reference to the cited source page
    cites = fm.get('cites')
    if isinstance(cites, list):
      for target in cites:
        referenced.add(target + '.md')
    # body markdown links must resolve; a resolved wiki target is inbound
    for target in MD_LINK_RE.findall(body):
      if target.startswith(('http://', 'https://', 'mailto:', '#')):
        continue
      resolved = (p.parent / target.split('#', 1)[0]).resolve()
      if not resolved.exists():
        findings.append(('ERROR', str(rel), f'link: broken relative link: {target}'))
      else:
        try:
          referenced.add(str(resolved.relative_to(wiki_abs)))
        except ValueError:
          pass
    # body citation locators [slug §x] must map to a source page; and count
    # as an inbound reference to it
    for slug in BODY_CITE_RE.findall(body):
      if slug in slugs:
        referenced.add(f'sources/{slug}.md')
      else:
        findings.append(
          ('ERROR', str(rel), f'citation: [{slug} …] has no source page'))
  # orphan warning: a page nothing references (via link, cites, or locator)
  for p in pages:
    relw = str(p.relative_to(root / 'wiki'))
    if relw not in referenced:
      findings.append(('WARN', str(p.relative_to(root)), 'orphan: no inbound links'))
  return findings
```
Wire into `run_checks`:
```python
  findings += check_links(root, pages)
```

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q
```
Expected: PASS.

> Note: the empty-scaffold test (`test_empty_scaffold_is_clean`) still passes because it has zero pages, so no orphan warnings arise. Pages added in other tests carry their own index lines and, where needed, inbound links.

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/lint_wiki.py scripts/test_lint_wiki.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(lint): relative links, body-citation slugs, orphan warning' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 8: `lint_wiki.py` — quarantine check (error)

Spec §10 rows "`cites` target not `type: source`" and "`cites` target not `status: verified`", plus §6 quarantine rule. Each `cites` entry (e.g. `sources/robnik-2022-mclmc`) must resolve to a page under `wiki/` whose `type` is `source` and whose `status` is `verified`.

**Files:**
- Modify: `~/research-wiki/scripts/lint_wiki.py`
- Modify: `~/research-wiki/scripts/test_lint_wiki.py`

**Interfaces:**
- Consumes: `parse_frontmatter`, `discover_pages` (Task 4).
- Produces: `check_quarantine(root, pages) -> list[tuple]`, wired into `run_checks`.

- [x] **Step 1: Write the failing tests**

Append to `test_lint_wiki.py`:
```python
def test_cites_non_source_is_error(tmp_path):
  root = make_wiki(tmp_path)
  # a concept page cited as a source
  write_page(root, 'samplers/other.md',
             {'title': 'Other', 'type': 'concept', 'status': 'verified',
              'topics': '[samplers]', 'cites': '[sources/a]',
              'updated': '2026-07-22'})
  valid_source(root, 'sources/a.md', 'a')
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'synthesis', 'status': 'unverified',
              'topics': '[samplers]', 'cites': '[samplers/other]',
              'updated': '2026-07-22'})
  assert any(f[0] == 'ERROR' and 'type: source' in f[2]
             for f in lint_wiki.run_checks(root))


def test_cites_unverified_source_is_error(tmp_path):
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a', status='unverified')
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'concept', 'status': 'unverified',
              'topics': '[samplers]', 'cites': '[sources/a]',
              'updated': '2026-07-22'})
  assert any(f[0] == 'ERROR' and 'verified' in f[2]
             for f in lint_wiki.run_checks(root))


def test_cites_verified_source_is_clean(tmp_path):
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a', status='verified')
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'concept', 'status': 'unverified',
              'topics': '[samplers]', 'cites': '[sources/a]',
              'updated': '2026-07-22'})
  assert [f for f in lint_wiki.run_checks(root)
          if f[0] == 'ERROR' and 'cites' in f[2].lower()] == []
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "cites"
```
Expected: FAIL.

- [x] **Step 3: Write the implementation**

Add to `lint_wiki.py`:
```python
def check_quarantine(root, pages):
  findings = []
  for p in pages:
    rel = p.relative_to(root)
    fm = parse_frontmatter(p.read_text()) or {}
    cites = fm.get('cites')
    if not isinstance(cites, list):
      continue
    for target in cites:
      cited = root / 'wiki' / (target + '.md')
      if not cited.exists():
        findings.append(
          ('ERROR', str(rel), f'cites: target page missing: {target}'))
        continue
      cfm = parse_frontmatter(cited.read_text()) or {}
      if cfm.get('type') != 'source':
        findings.append(
          ('ERROR', str(rel), f'cites: {target} is not type: source'))
      if cfm.get('status') != 'verified':
        findings.append(
          ('ERROR', str(rel), f'cites: {target} is not status: verified'))
  return findings
```
Wire into `run_checks`:
```python
  findings += check_quarantine(root, pages)
```

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q
```
Expected: PASS.

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/lint_wiki.py scripts/test_lint_wiki.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(lint): quarantine — cites must be verified source pages' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 9: `lint_wiki.py` — session-digest checks (error)

Spec §10 rows "Secret-shaped string anywhere under `raw/sessions/`" and "`kind: decision` capture without `basis: user-turn` or `basis: git:<sha>`" (§16.3, §16.5). These operate on files under `raw/sessions/`, not on wiki pages. The secret pattern set here is the **backstop** for Plan 14's distiller redaction and must stay at least as broad as it.

**Files:**
- Modify: `~/research-wiki/scripts/lint_wiki.py`
- Modify: `~/research-wiki/scripts/test_lint_wiki.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `SECRET_PATTERNS` (module constant), `check_sessions(root) -> list[tuple]`, wired into `run_checks`.

- [x] **Step 1: Write the failing tests**

Append to `test_lint_wiki.py`:
```python
def write_session(root, name, text):
  p = root / 'raw/sessions' / name
  p.parent.mkdir(parents=True, exist_ok=True)
  p.write_text(text)
  return p


def test_secret_shaped_string_is_error(tmp_path):
  root = make_wiki(tmp_path)
  write_session(root, '2026-05-14-x-a3f2c9d1.md',
                '---\nsession: a3f2c9d1\n---\n\ntoken ghp_' + 'A' * 36 + '\n')
  assert any(f[0] == 'ERROR' and 'secret' in f[2].lower()
             for f in lint_wiki.run_checks(root))


def test_decision_without_basis_is_error(tmp_path):
  root = make_wiki(tmp_path)
  write_session(root, '2026-05-14-y-b4a1.md',
                '---\nsession: b4a1\n---\n\n'
                '### [d-01] Something decided\n'
                'kind: decision · turns: 3-5\n'  # no basis:
                'Statement.\n')
  assert any(f[0] == 'ERROR' and 'basis' in f[2].lower()
             for f in lint_wiki.run_checks(root))


def test_decision_with_basis_is_clean(tmp_path):
  root = make_wiki(tmp_path)
  write_session(root, '2026-05-14-z-c9d1.md',
                '---\nsession: c9d1\n---\n\n'
                '### [d-01] Something decided\n'
                'kind: decision · turns: 3-5 · basis: user-turn\n'
                'Statement.\n')
  assert [f for f in lint_wiki.run_checks(root)
          if f[0] == 'ERROR' and 'basis' in f[2].lower()] == []
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "secret or decision"
```
Expected: FAIL.

- [x] **Step 3: Write the implementation**

Add to `lint_wiki.py`:
```python
# Secret-shaped strings. BACKSTOP for distill_sessions.py redaction (Plan 14):
# keep this set at least as broad as the distiller's, so a residual secret in a
# distilled digest is always caught here.
SECRET_PATTERNS = [
  ('openai-key', re.compile(r'sk-[A-Za-z0-9]{20,}')),
  ('github-token', re.compile(r'ghp_[A-Za-z0-9]{30,}')),
  ('aws-key', re.compile(r'AKIA[0-9A-Z]{16}')),
  ('pem-block', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
  ('assignment', re.compile(
    r'(?i)(password|secret|token)\s*[:=]\s*[\'"]?[A-Za-z0-9/+_-]{12,}')),
]
# `kind: decision` capture metadata line must carry an approved basis.
DECISION_META_RE = re.compile(r'^kind:\s*decision\b(.*)$', re.M)
BASIS_OK_RE = re.compile(r'basis:\s*(user-turn|git:[0-9a-f]{7,40})')


def check_sessions(root):
  findings = []
  sess_dir = root / 'raw/sessions'
  if not sess_dir.exists():
    return findings
  for p in sorted(sess_dir.glob('*.md')):
    rel = p.relative_to(root)
    text = p.read_text()
    for cls, pat in SECRET_PATTERNS:
      if pat.search(text):
        findings.append(('ERROR', str(rel), f'secret: {cls}-shaped string present'))
    for m in DECISION_META_RE.finditer(text):
      if not BASIS_OK_RE.search(m.group(1)):
        findings.append(
          ('ERROR', str(rel),
           'basis: kind: decision needs basis: user-turn or git:<sha>'))
  return findings
```
Wire into `run_checks`:
```python
  findings += check_sessions(root)
```

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q
```
Expected: PASS.

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/lint_wiki.py scripts/test_lint_wiki.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(lint): session-digest secret + decision-basis checks' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 10: `lint_wiki.py` — cadence & scale (warn + info), then M0 acceptance

Spec §10 rows "Newest `updated` … newer than last `log.md` entry" (warning), "Raw file with no source page" (info), "Page count > 120 or source count > 100" (info). Final step runs the linter against the **real** scaffold to satisfy M0 acceptance #1.

**Files:**
- Modify: `~/research-wiki/scripts/lint_wiki.py`
- Modify: `~/research-wiki/scripts/test_lint_wiki.py`

**Interfaces:**
- Consumes: `discover_pages`, `parse_frontmatter` (Task 4).
- Produces: `check_cadence_and_scale(root, pages) -> list[tuple]`, wired into `run_checks`.

- [x] **Step 1: Write the failing tests**

Append to `test_lint_wiki.py`:
```python
def test_raw_without_source_page_is_info(tmp_path):
  root = make_wiki(tmp_path)
  (root / 'raw/samplers/newpaper.pdf').write_bytes(b'%PDF-1.4 stub')
  set_index(root, [])
  infos = [f for f in lint_wiki.run_checks(root) if f[0] == 'INFO']
  assert any('newpaper' in f[2] for f in infos)


def test_updated_newer_than_log_is_warning(tmp_path):
  root = make_wiki(tmp_path)
  (root / 'wiki/log.md').write_text('# Operation log\n\n## [2026-01-01] schema | init | x\n')
  valid_source(root, 'sources/a.md', 'a')  # updated 2026-07-22 > log 2026-01-01
  set_index(root, ['- [a](sources/a.md) — s · 1 · verified · 2026-07-22'])
  assert any(f[0] == 'WARN' and 'log' in f[2].lower()
             for f in lint_wiki.run_checks(root))
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q -k "raw_without or updated_newer"
```
Expected: FAIL.

- [x] **Step 3: Write the implementation**

Add to `lint_wiki.py`:
```python
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
LOG_DATE_RE = re.compile(r'^## \[(\d{4}-\d{2}-\d{2})\]', re.M)


def _last_log_date(root):
  log = root / 'wiki/log.md'
  if not log.exists():
    return None
  dates = LOG_DATE_RE.findall(log.read_text())
  return max(dates) if dates else None


def check_cadence_and_scale(root, pages):
  findings = []
  # warning: newest page `updated` newer than last log entry
  updates = []
  for p in pages:
    fm = parse_frontmatter(p.read_text()) or {}
    if isinstance(fm.get('updated'), str) and DATE_RE.fullmatch(fm['updated']):
      updates.append(fm['updated'])
  last_log = _last_log_date(root)
  if updates and last_log and max(updates) > last_log:
    findings.append(
      ('WARN', 'wiki/log.md',
       f'log: newest page updated {max(updates)} > last log {last_log}'))
  # info: raw file (non-.gitkeep) with no source page of the same stem
  source_stems = {p.stem for p in (root / 'wiki/sources').glob('*.md')}
  raw_files = [f for f in (root / 'raw').rglob('*')
               if f.is_file() and f.suffix not in ('', '.gitkeep')
               and f.name != '.gitkeep']
  for f in raw_files:
    if f.parent.name == 'assets':
      continue
    if f.stem not in source_stems:
      findings.append(
        ('INFO', str(f.relative_to(root)), 'backlog: raw file has no source page'))
  # info: soft ceiling
  n_pages = len(pages)
  n_sources = len(source_stems)
  if n_pages > 120 or n_sources > 100:
    findings.append(
      ('INFO', 'wiki/', f'scale: {n_pages} pages, {n_sources} sources — revisit qmd'))
  return findings
```
Wire into `run_checks`:
```python
  findings += check_cadence_and_scale(root, pages)
```

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q
```
Expected: PASS (full suite green).

- [x] **Step 5: M0 acceptance — lint the real empty scaffold**

Run:
```bash
cd ~/research-wiki && uv run --python 3.13 python scripts/lint_wiki.py . ; echo "exit=$?"
```
Expected: prints `0 errors, 0 warnings, 0 info` and `exit=0`. This is **M0 acceptance criterion 1** (`python scripts/lint_wiki.py` exits 0 on the empty scaffold).

- [x] **Step 6: Commit**

```bash
cd ~/research-wiki && git add scripts/lint_wiki.py scripts/test_lint_wiki.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(lint): cadence + scale checks; empty scaffold lints clean' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 11: `llm-wiki` skill + install + provenance sync

Spec §12. Write the procedure-only skill in the `agent-skills` repo, symlink it into `~/.claude/skills/`, and synchronize the provenance gate (`NOTICE`, `CLAUDE.md`) so `check_provenance.py` and `check_frontmatter.py` stay green. The skill is a **Lowell original (MIT)** that *cites* the Karpathy LLM-wiki gist and `kfchou/wiki-skills` by reference (pattern/idea only — no external prose or code enters the repo).

**Files (all in `agent-skills` unless noted):**
- Create: `skills/llm-wiki/SKILL.md`
- Create (symlink): `~/.claude/skills/llm-wiki` → `/Users/lowell/Projects/agent-skills/skills/llm-wiki`
- Modify: `NOTICE` (add `llm-wiki/` to the originals block)
- Modify: `CLAUDE.md` (add `llm-wiki` to the "Lowell's originals" list; `Eleven` → `Twelve`)

**Interfaces:**
- Consumes: `SCHEMA.md` (Task 3) — referenced at runtime, read before any operation.
- Produces: a triggerable skill (M0 acceptance #2).

- [x] **Step 1: Write `skills/llm-wiki/SKILL.md`** (body ≤150 lines; reference `SCHEMA.md` as inline code, never a markdown link)

```markdown
---
name: llm-wiki
description: >
  Maintain the personal research wiki (Karpathy LLM-wiki pattern) at
  $LLM_WIKI_ROOT. Use whenever the user says 'ingest', 'add to the wiki',
  'what does the wiki say', 'wiki lint', 'verify <page>', or 'file this into
  the wiki'; whenever they reference the research wiki, sampler literature
  notes, or nowcasting literature notes; and whenever they drop a paper into
  raw/ and ask to process it.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# llm-wiki

Procedure for maintaining the research wiki. The wiki carries its own schema, so
this skill stays generic — a second wiki can reuse it unchanged.

## Resolve the root, then read the schema

1. Root is `$LLM_WIKI_ROOT`, default `~/research-wiki`. All paths below are
   relative to it.
2. **Before any operation, read `SCHEMA.md` at the root.** It is the normative
   contract (page formats, quarantine rule, index/log grammar, capture-note
   format). Do not act from memory of it.

## Hard rules (never violate)

- **Raw is immutable.** Never modify anything under `raw/`; the human curates it,
  the agent only reads it.
- **Quarantine.** A page's `cites` may list only `type: source` pages with
  `status: verified`. An unverified summary is never grounds for another page.
- **Contradictions are kept, not overwritten.** A new claim conflicting with an
  existing one keeps both (with locators) and appends to `open-questions.md`.
- **Every mutating operation appends one line to `log.md`** using the grammar in
  `SCHEMA.md`: `## [YYYY-MM-DD] <op> | <subject> | <note>`.
- Run `scripts/lint_wiki.py` (mechanical) before any status flip and before a
  semantic pass; it must exit 0.

## Operations

### ingest `<raw/path>`
1. Read the source. Propose 3–5 key takeaways, a source-page draft
   (`type: source`, `status: unverified`, `raw:` = the file), and a touch-list
   of existing concept pages to update.
2. New concept page only for an entity linked from ≥2 pages; ceiling one new
   concept page per ingest without explicit approval.
3. On approval: write the source page; apply concept edits (each new claim
   carries an inline locator `[slug §x]`); update `index.md`; append to `log.md`.
4. Write-time contradiction → keep both claims, append to `open-questions.md`.
5. **Cadence:** grep `log.md`; if ≥5 ingests since the last `lint-semantic`
   entry, or that entry is >30 days old, say so and offer to run one now.
6. A session digest (`raw/sessions/…`) ingests the same way, but its source-page
   body is atomic capture notes (see `SCHEMA.md`), not prose.

### query `<question>`
1. Read `index.md`; select ≤5 pages; read them; answer with page references and
   inline locators.
2. Open raw sources only if the pages are insufficient — say so explicitly; that
   is a coverage gap worth an `open-questions.md` entry.
3. **File-back only** when the answer synthesizes ≥2 sources or records a
   decision; simple lookups are never filed. Filed pages are `type: synthesis`,
   `status: unverified`. If a needed source page is unverified, verification is
   the visible prerequisite.

### lint
1. **Mechanical:** run `scripts/lint_wiki.py` (add `--strict` to fail on
   warnings). Fix errors before proceeding.
2. **Semantic:** an agent pass over the whole wiki — contradictions not yet in
   `open-questions.md`; claims plausibly superseded by newer ingests; concepts
   mentioned ≥3 times without their own page; gaps worth a web search. Write
   `reports/lint-YYYY-MM-DD.md`, add new items to `open-questions.md`, append one
   line to `log.md`.

### verify `<wiki/page.md>`
1. Mechanical lint must be clean first.
2. Walk every locator-carrying claim; open the cited source page's raw file at
   the locator; confirm or flag. For a session-digest source page, confirm each
   capture against its cited turns (and, for `basis: git:<sha>`, the commit).
3. All confirmed → flip to `status: verified`, append to `log.md`. Anything
   flagged → status unchanged; write flags to `reports/`.

## Attribution

Pattern from Andrej Karpathy's LLM-wiki idea file; the per-claim citation-audit
form is simplified from `kfchou/wiki-skills`. This skill is original prose.
```

- [x] **Step 2: Symlink the skill and confirm it resolves**

Run:
```bash
ln -s /Users/lowell/Projects/agent-skills/skills/llm-wiki ~/.claude/skills/llm-wiki && \
ls -l ~/.claude/skills/llm-wiki && readlink ~/.claude/skills/llm-wiki
```
Expected: the symlink prints, pointing at `…/agent-skills/skills/llm-wiki`.

- [x] **Step 3: Add the `llm-wiki/` attribution to `NOTICE`**

In `/Users/lowell/Projects/agent-skills/NOTICE`, inside the block under
`The following skills are original works by Lowell Mason, MIT licensed:`, add
`llm-wiki/` as the last entry before the blank line (after `creative-thinking/`):
```
    creative-thinking/
    llm-wiki/
```
Then, after the `recommend-probabilistic-model/` explanatory paragraph, add a citation note (mirrors the recommend-visualization pattern):
```
llm-wiki/ is an original work by Lowell Mason (MIT). It implements the LLM-wiki
pattern from Andrej Karpathy's public idea file (gist
karpathy/442a6bf555914893e9891c11519de94f) and adopts a simplified per-claim
citation-audit form from kfchou/wiki-skills — both by reference to the idea only;
it reproduces no external prose or code and bundles no copies.
```

- [x] **Step 4: Update `CLAUDE.md`'s originals list**

In `/Users/lowell/Projects/agent-skills/CLAUDE.md`, the "Lowell's originals" bullet: append `llm-wiki` to the backtick-quoted list and change the parenthetical count. Exact edit — from:
```
`track-model-experiments`, `tune-hyperparameters`, `creative-thinking`. (Eleven — keep in sync with `NOTICE`, which is authoritative.)
```
to:
```
`track-model-experiments`, `tune-hyperparameters`, `creative-thinking`, `llm-wiki`. (Twelve — keep in sync with `NOTICE`, which is authoritative.)
```

- [x] **Step 5: Run the frontmatter and provenance lints (must be clean)**

Run:
```bash
cd /Users/lowell/Projects/agent-skills && \
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py ; echo "frontmatter exit=$?" && \
uv run --python 3.13 python build/check_provenance.py ; echo "provenance exit=$?"
```
Expected: both print nothing and `exit=0`. If frontmatter flags a referenced-path error, confirm the SKILL.md mentions `SCHEMA.md` only as inline code (backticks), not as a `](SCHEMA.md)` markdown link.

- [x] **Step 6: Confirm the skill body is within budget (≤150 lines)**

Run:
```bash
wc -l /Users/lowell/Projects/agent-skills/skills/llm-wiki/SKILL.md
```
Expected: ≤ ~165 (frontmatter + ≤150-line body). If over, tighten prose.

- [x] **Step 7: Commit (in the `agent-skills` repo)**

```bash
cd /Users/lowell/Projects/agent-skills && \
git add skills/llm-wiki/SKILL.md NOTICE CLAUDE.md && \
git commit -m 'feat(skill): add llm-wiki skill + provenance sync' \
  -m 'Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>' && \
git log --oneline -1
```
Expected: one commit line printed.

> **M0 acceptance criterion 2** — "Saying 'ingest <path>' triggers the skill, which reads `SCHEMA.md` before acting" — is behavioral and verified by use, not a unit test: the pushy `description` drives auto-loading, and the skill body's first instruction is to read `SCHEMA.md`. Confirm by starting a fresh session and issuing an `ingest` request against a raw file.

---

## Self-Review

**1. Spec coverage (M0 + S0 scope):**
- §5 repository layout → Task 2. §6–§9, §16.3, §16.5 formats → Task 3 (`SCHEMA.md`).
- §10 linter contract, all 12 rows → Tasks 4–10 (schema, parity, links+citation+orphan, quarantine, session secret+decision, cadence+backlog+scale; CLI/exit/output in Task 4).
- §12 skill → Task 11 (+ symlink + provenance). §14 conventions → Global Constraints, enforced per task.
- §16.1 / §16.7 S0 retention → Task 1.
- **Deliberately excluded** (stated in "Out of scope"): §16.4 distiller → Plan 14; §13 M1–M3 and §16.7 S1–S3 content operations → run with the skill, not code; §16.1.3 export request → manual (Task 1 Step 4). §11 scale policy is realized by the info-level ceiling check (Task 10). §15 open questions are non-blocking design notes, not tasks.

**2. Placeholder scan:** No "TBD"/"handle edge cases"/"similar to Task N". Every code step shows complete code; every run step shows the command and expected output.

**3. Type consistency:** `parse_frontmatter`, `discover_pages`, `default_root`, `run_checks`, `main` defined in Task 4 and reused unchanged. Findings are `(severity, path, message)` tuples throughout. `check_*` functions each take `(root, pages)` except `check_sessions(root)` (session files aren't wiki pages) — noted at each call site. `run_checks` accumulates them in one list. `_index_targets`, `_source_slugs`, `_strip_frontmatter`, `_last_log_date` are private helpers introduced before first use.

**4. Known follow-ups for Plan 14 (distiller):** the `SECRET_PATTERNS` backstop in Task 9 must remain ≥ the distiller's redaction set; the digest/capture format the distiller emits is already pinned by `SCHEMA.md` (Task 3) and validated by Task 9's checks.

---

## Post-Execution Status — completed 2026-07-22

Executed via **subagent-driven-development**. All 11 tasks complete; every per-task review returned zero Critical/Important. Final verification ran two Opus whole-branch reviews plus a 23-agent adversarial linter audit (five breakers running real fixtures against the linter + a spec-§10 completeness critic + an Opus adversarial-verify pass on every Critical/Important finding).

**Acceptance.** M0 #1 met — `scripts/lint_wiki.py .` on the empty scaffold prints `0 errors, 0 warnings, 0 info`, exit 0 (controller-verified independently). All 12 spec §10 rows are enforced at the specified severity. Linter suite: 30 tests (25 as planned + 5 for the post-review fix below). agent-skills provenance gate green (`check_frontmatter.py` and `check_provenance.py` exit 0; build suite 33 passed). The skill auto-loads/triggers (M0 #2 confirmed to the extent that it appears in the live skills list; a full behavioral pass in a fresh interactive session remains a normal-use check).

**Deviations from the plan's literal text (shipped code differs — recorded per the completion protocol):**
- **Task 10, Step 3:** the raw-backlog INFO message was changed from the plan's static string to `f'backlog: raw file {f.name} has no source page'`. The plan's own Step-1 test asserts `'newpaper' in f[2]` (the *message* field), which the static string can never satisfy — the plan's snippet and its own test were mutually inconsistent, and the message fix is the only way to green the plan's test.
- **Task 11, Step 1:** two backtick references `` `scripts/lint_wiki.py` `` in `SKILL.md` were reworded to `` `$LLM_WIKI_ROOT/scripts/lint_wiki.py` ``. The plan warned only that a `](SCHEMA.md)` markdown link would trip `check_frontmatter.py`'s `LINK_RE`; it missed that a backtick `scripts/…` path trips the sibling `TICK_PATH_RE` the same cross-repo way. The reword dodges the regex and is semantically truer (the linter lives at `$LLM_WIKI_ROOT`, not in `agent-skills`).
- **Task 11 (scope add):** the build-suite guard `test_real_notice_originals_has_eleven_entries` hardcoded the originals count; adding the 12th original (`llm-wiki`) required updating it to `…_twelve_entries` / `== 12`. The plan's Step 5 ran only the two lints, not the build suite, so this fix was outside the plan's stated scope.
- **Post-review fix (human-approved, `70e690c`):** a follow-up commit closed two robustness holes found in the plan's own verbatim regexes/parser — (G1) a bare/unbracketed `cites:`/`topics:` value bypassing the load-bearing quarantine guard, and (G2) the secret backstop missing current OpenAI (`sk-proj-`) and GitHub (`github_pat_`) key formats. Three further regex-strictness gaps the audit surfaced were deliberately deferred by the spec author — see `specs/deferred_items.md § 13-llm-wiki`.

**Repositories & retirement.** The linter, scaffold, and `SCHEMA.md` live in the **standalone `~/research-wiki` repo** (its own `main`, 11 commits `a81572c`…`70e690c`) — not part of any PR, kept as built. The `llm-wiki` skill + provenance sync + this plan's retirement are on **`agent-skills` branch `feat/llm-wiki`** (`edb149d`, `3b7f61b`, + the completion commit), opened as a PR. This plan (13) is retired to `specs/plans/completed/`; **`specs/llm-wiki-spec.md` stays live** because Plan 14 (the distiller) still implements the same spec (per Plan 14's retirement note).
