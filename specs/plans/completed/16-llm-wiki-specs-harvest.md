# llm-wiki specs-harvest framework Implementation Plan

**Status: COMPLETE (2026-07-25)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the specs-harvest avenue — a `distill_specs.py` script (subcommands `inventory` and `assemble`), a `harvest` operation in the llm-wiki SKILL.md, and the contract extension (schema template + lint + bootstrap) that codifies the `raw/specs/` class, the `at:` capture locator, and the brief format — per `specs/llm-wiki-specs-harvest.md`.

**Architecture:** One new stdlib-only script beside the session distiller, importing `redact`/`slugify` from it (the first script→script import in the dir — proven safe because both runtime execution and directory-scoped pytest put the scripts dir on `sys.path`). The mechanical stages (walk, seed grep, SHA archaeology, validation, redaction, digest write) are scripted; extraction/verification/dedup stay agent+human procedure in the SKILL.md `harvest` op; the human tick in the brief remains the gate in front of `raw/`.

**Tech Stack:** Python 3.13 (stdlib only — `argparse`, `re`, `subprocess`, `hashlib`, `pathlib`), pytest via `uv run`, git CLI for SHA archaeology.

## Global Constraints

Copied from the spec and the repo's house rules — every task's requirements implicitly include these:

- **Spec:** `specs/llm-wiki-specs-harvest.md` (committed on this branch). Requirements R1–R6; formats §5; tests §9.
- **Stdlib only** in `skills/llm-wiki/scripts/*.py` — no third-party imports; these scripts are installed into wiki roots and must run on bare `python3` (3.12+).
- **Deterministic:** no `uuid`, no randomness, no clock reads — **sole exception**: `inventory --date` defaults to `datetime.date.today().isoformat()`; tests always pass `--date`.
- **House style** (match `distill_sessions.py` exactly): single quotes (including `'''` docstrings), **2-space indent**, no type hints, `pathlib` for paths, `main(argv=None)` returning an int, `sys.exit(main())` guard, constants adjacent to their consumers, rationale-bearing comments citing spec §s.
- **Separator glyph:** capture-metadata fields join with ` · ` — space, U+00B7 MIDDLE DOT, space. Never a hyphen or ASCII period. (The session `turns:` format uses an en dash U+2013 in ranges; specs-harvest `at:` positions copy source text verbatim and add no dashes of their own.)
- **Failure contract** (spec §7, mirrors the session distiller): collect ALL failures, print one line each to stderr, exit 1, **write nothing on failure**; the digest write is atomic (temp file + `os.replace`) and happens last.
- **Explicit paths, no defaults:** both subcommands require `--root`; `inventory` requires the repo path; `assemble` refuses a brief whose recorded root mismatches `--root`. (Deliberately unlike `lint_wiki.py`'s `$LLM_WIKI_ROOT` fallback — spec §4.1/§7 wrong-wiki protection.)
- **Existing tests unchanged:** the current 101 tests (55 distill + 31 lint + 15 bootstrap) must keep passing untouched after every task. Test runner, run from inside the scripts dir:

  ```bash
  cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
  ```

- **Repo gates** before the final commit:

  ```bash
  uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
  uv run --python 3.13 python build/check_provenance.py
  ```

- **Kinds and prefixes** (from the wiki SCHEMA): `decision` (d), `rejected-approach` (r), `gotcha` (g), `resolved-confusion` (c), `validated-pattern` (p); open questions are `q` (digest-only, no kind). Boundary verdicts: `transferable | mixed | code-coupled`.
- **Provenance:** `llm-wiki` is one of Lowell's originals (MIT) per `NOTICE`; new files inside the skill need no `NOTICE` change. Do not touch other skills.
- **Commits:** one per task, `feat(llm-wiki): …` / `test(llm-wiki): …` style, from the repo root of this worktree.

### Reference instances (read-only ground truth on this machine)

- Pilot digest: `/Users/lowell/research-wiki/raw/specs/2026-07-24-bls-stats-specs-harvest.md` (172 lines, hand-authored, grandfathered filename).
- Pilot source page: `/Users/lowell/research-wiki/wiki/sources/2026-07-24-bls-stats-specs-harvest.md` (170 lines).
- Live root schema: `/Users/lowell/research-wiki/SCHEMA.md` (differs from `scripts/schema-template.md` by exactly one line: the root copy lacks the template's line-1 `schema-version` comment).
- **No pilot brief exists** (`/Users/lowell/research-wiki/reports/` is empty). Task 7 reconstructs one as a test fixture by transcribing the pilot digest + source page.

### File structure (what this plan creates/modifies)

| File | Action | Responsibility |
|---|---|---|
| `skills/llm-wiki/scripts/distill_specs.py` | Create (Tasks 1–6) | inventory + assemble, all mechanical stages |
| `skills/llm-wiki/scripts/test_distill_specs.py` | Create (Tasks 1–7) | new suite incl. git fixtures + golden pairs |
| `skills/llm-wiki/scripts/lint_wiki.py` | Modify (Task 8) | extend secret + decision-basis checks to `raw/specs/` |
| `skills/llm-wiki/scripts/test_lint_wiki.py` | Modify (Task 8) | new tests appended; existing 31 untouched |
| `skills/llm-wiki/scripts/schema-template.md` | Modify (Task 9) | new specs-harvest section; secrets rule widened; version→2 |
| `skills/llm-wiki/scripts/bootstrap_wiki.py` | Modify (Task 9) | install `distill_specs.py`, create `raw/specs/` |
| `skills/llm-wiki/scripts/test_bootstrap_wiki.py` | Modify (Task 9) | template-parity + new-script tests |
| `skills/llm-wiki/INSTALL.md` | Modify (Task 9) | script list + ops list mentions |
| `skills/llm-wiki/SKILL.md` | Modify (Task 10) | `harvest` operation + description trigger |
| `/Users/lowell/research-wiki/SCHEMA.md` + `wiki/log.md` | Modify (Task 11, **human-gated**) | root contract amendment + `schema` log line |

### The brief format (normative for Tasks 1–7; also lands in SCHEMA in Task 9)

`<root>/reports/harvest-<repo>-<YYYY-MM-DD>.md`. Complete small example — the grammar every parser/renderer in this plan implements:

```markdown
---
harvest: specs
repo: bls-stats
repo_path: /Users/lowell/Projects/bls-stats
repo_head: ad8abe0
root: /Users/lowell/research-wiki
date: 2026-07-24
prior_brief: none
files_walked: >
  specs/completed/arch.md; specs/plans/completed/1-arch.md; specs/deferred_items.md
assembled: 2026-07-24-bls-stats-specs-1a2b3c4d
---

note: specs/plans/: no .md files

## specs/completed/arch.md

shas:
- 1d26d71 · spec: architecture v1 · substantive
- 9f00aa2 · chore: retire spec to completed/ · mechanical

seeds:
- L12 decision: **Decision:** Delta Lake over plain Parquet
- L88 rejected: merge/upsert rejected for idempotent re-runs

previously seen:
- d-01 · specs/completed/arch.md §6.1 · 3f9c2e01

captures:

(extraction: read the whole file at repo_head; append entries per the brief grammar in SCHEMA.md)

- [x] [d-01] Flat files primary; BLS API v2 demoted to utility
  kind: decision · boundary: transferable
  at: specs/completed/arch.md §6.1 · sha: 1d26d71
  (also specs/plans/completed/1-arch.md L3204 · sha: 168da46)
  excerpt: "The BLS API v2 **cannot** carry full-universe daily increments
    on one registered key"
  claim: BLS API v2 quotas cannot carry full-universe daily ingest; LABSTAT
    flat files deliver the same-morning vintage in one GET.
- [ ] [g-01] A declined gotcha stays here as the durable declined record
  kind: gotcha · boundary: transferable
  at: specs/completed/arch.md §7.2 · sha: 1d26d71
  excerpt: "Nullable key columns silently defeat idempotency checks"
  claim: Nullable key columns silently defeat idempotency checks.
- [x] [q-01] QCEW routine print count and touched-set
  at: specs/completed/arch.md §12.3
  claim: The actual QCEW revision lifecycle is an unverified data-source fact
    any implementation would face again.
```

Grammar rules (the parser in Task 5 implements exactly these):

- Header: `---`-fenced, `key: value` lines; `key: >` starts a folded value whose 2-space-indented following lines join with spaces. `assembled:` is absent until `assemble` stamps it.
- `note:` lines (absent-input notes) sit between the header and the first `## ` section.
- One `## <repo-relative path>` section per walked file, containing `shas:` / `seeds:` / `previously seen:` lists (each `- `-bulleted, `- none` when empty) and a `captures:` area.
- Capture entry: checkbox line `- [ ] [<prefix>-NN] <title>` (or `- [x]`), then 2-space-indented field lines `kind:`, `at:`, `excerpt:`, `claim:`, optional `note:`; 4-space-indented lines continue the previous field (joined with a single space). `kind:` carries ` · boundary: <verdict>`; `at:` carries ` · sha: <hex>` (7–40 chars). Additional locations: 2-space-indented `(also <path> <pos> · sha: <hex>)` lines directly usable after `at:` (the ` · sha:` part optional on q entries).
- Open-question entries (`[q-NN]`) have only `at:` (no sha required) and `claim:`.
- Tick semantics: `[x]` = approved for assembly; unticked entries persist as the durable declined record; later inventories dedup against ALL prior entries — approved and declined — keyed on locator + claim hash.

### The digest format (normative for Task 6; §5.2)

`<root>/raw/specs/<date>-<repo>-specs-<id8>.md`, where `id8` = first 8 hex chars of SHA-256 over the ordered ticked entry blocks (body only — not header, not preamble), so an unchanged brief re-assembles to the identical file. Exact rendered output for a brief with one ticked capture and one ticked q (`{…}` filled at run time):

```markdown
---
source: specs-harvest
repo: {repo}
repo_head: {head}
date: {date}
files: {n_files}
captures: {n_caps}
open_questions: {n_qs}
note: >
  Assembled by distill_specs.py from {brief_name}: {n_caps} ticked of
  {n_total} proposed captures; unticked entries remain in the brief as
  the declined record.
brief: reports/{brief_name}
files_read: >
  {files_walked joined with '; '}
---

Ground-truth entries for the capture notes in wiki/sources/{stem}.md.
Each entry: verbatim excerpt from the {repo} file at the stated location,
introducing commit sha.

[d-01] {title}
at: {path} {pos} · sha: {sha}
  (also {path2} {pos2} · sha: {sha2})
excerpt: "{excerpt}"
note: {note}

[q-01] {title}
at: {path} {pos}
{claim prose}
```

Capture entries render in brief order with q entries last; `excerpt:`/`note:`/q-prose are redacted; excerpts render on one (long) line — the hand-wrapped pilot digest is the reference for *content*, compared whitespace-normalized (Task 7). The surrounding `"…"` on a brief `excerpt:` is brief syntax, stripped at parse and re-added by the renderer — never doubled. `files:` counts the brief's `files_walked` entries. Superseded digests from earlier tick-sets are the human's to curate (raw/ is human-curated); the script never deletes under `raw/`.

### The source-page body (normative for Task 6; §5.3)

`assemble` prints this to **stdout** (the agent wraps frontmatter and runs the normal ingest op; the script itself never writes under `wiki/`). Per ticked capture, in digest order, q entries excluded:

```markdown
### [d-01] {title}
kind: decision · at: {repo} {path} {pos} · basis: git:{sha}
{claim}
```

The position drops a trailing ` (L…)` parenthetical (pilot: digest `Task 2 (L176)` → source page `Task 2`); `(also …)` locations are digest-only.

---

### Task 1: `distill_specs.py` skeleton — CLI, walk, hard errors, brief creation

> Deviation: plan's dead 'slugify(...) or repo.name' fallback replaced by a local _repo_name() sanitizer; git guard extended to require the repo be its own 'rev-parse --show-toplevel' (parent-repo bypass closed; linked worktrees pinned by test).

**Files:**
- Create: `skills/llm-wiki/scripts/distill_specs.py`
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: `from distill_sessions import redact, slugify` — `redact(text) -> (text, counts)` (note the 2-tuple), `slugify(text, max_words=6) -> str`.
- Produces (later tasks rely on these exact names): `main(argv=None) -> int`, `cmd_inventory(args) -> int`, `_git(repo, *args) -> str` (raises `RuntimeError` on nonzero), `walk_specs(repo, only=None) -> (files, notes)`, `brief_path(root, repo_name, date) -> Path`, `render_brief_header(...) -> list[str]`, `render_file_section(rel, shas, seeds, prior_keys) -> list[str]`, `_atomic_write(path, text)`, module constants `KINDS`, `BOUNDARIES`, `SEP`, `WALK_DIRS`, `DEFERRED_FILE`. In this task `render_file_section` is called with `shas=[]`, `seeds=[]`, `prior_keys=[]` (Tasks 2–4 fill them in).

- [x] **Step 1: Write the failing tests**

Create `skills/llm-wiki/scripts/test_distill_specs.py`:

```python
'''Tests for distill_specs.py. Stdlib + pytest only; git fixture repos in tmp.'''
import os
import subprocess

import pytest

import distill_specs as dsp

# Hermetic git: ignore the host's config so commits work on any machine.
GIT_ENV = dict(
  os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
  GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t.invalid',
  GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t.invalid')


def _git(repo, *args):
  proc = subprocess.run(['git', '-C', str(repo), *args],
                        capture_output=True, text=True, env=GIT_ENV)
  assert proc.returncode == 0, proc.stderr
  return proc.stdout


def _sha(repo, ref='HEAD'):
  return _git(repo, 'rev-parse', '--short', ref).strip()


def make_repo(tmp_path):
  '''specs/ corpus with history: a spec committed live, edited, then retired
  via a pure `git mv` (the mechanical-commit fixture spec §9 requires), plus
  a completed plan and deferred_items.md.'''
  repo = tmp_path / 'repo'
  (repo / 'specs/plans/completed').mkdir(parents=True)
  (repo / 'specs/completed').mkdir(parents=True)
  _git(repo, 'init', '-q', '-b', 'main')
  spec = repo / 'specs/a-spec.md'
  spec.write_text('# A spec\n\n**Decision:** use X over Y.\n')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'spec: a v1')
  spec.write_text('# A spec\n\n**Decision:** use X over Y.\n\nMore prose.\n')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'spec: a v2')
  _git(repo, 'mv', 'specs/a-spec.md', 'specs/completed/a-spec.md')
  _git(repo, 'commit', '-qm', 'chore: retire spec')
  plan = repo / 'specs/plans/completed/1-a-spec.md'
  plan.write_text('# Plan\n\n**Status: COMPLETE (2026-01-01)** — done\n\n'
                  '> Deviation: step 3 skipped\n')
  (repo / 'specs/deferred_items.md').write_text(
    '# Deferred items\n\n- [ ] later thing\n')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'plan: complete')
  return repo


def make_root(tmp_path):
  '''Minimal wiki root: SCHEMA.md marks it as a real root (wrong-wiki guard).'''
  root = tmp_path / 'wiki'
  for d in ('reports', 'raw/specs', 'wiki/sources'):
    (root / d).mkdir(parents=True)
  (root / 'SCHEMA.md').write_text('# SCHEMA\n')
  return root


def inventory(repo, root, date='2026-07-24', only=None):
  argv = ['inventory', str(repo), '--root', str(root), '--date', date]
  if only:
    argv += ['--only', only]
  return dsp.main(argv)


# --- Task 1: CLI, walk, hard errors, brief creation --------------------------

def test_no_subcommand_exits_nonzero(tmp_path):
  with pytest.raises(SystemExit) as exc:
    dsp.main([])
  assert exc.value.code != 0


def test_root_is_required(tmp_path):
  with pytest.raises(SystemExit) as exc:
    dsp.main(['inventory', str(tmp_path)])
  assert exc.value.code != 0


def test_non_wiki_root_is_hard_error(tmp_path, capsys):
  repo = make_repo(tmp_path)
  bare = tmp_path / 'not-a-wiki'
  bare.mkdir()
  assert inventory(repo, bare) == 1
  assert 'SCHEMA.md' in capsys.readouterr().err


def test_no_specs_dir_is_hard_error(tmp_path, capsys):
  root = make_root(tmp_path)
  repo = tmp_path / 'empty-repo'
  repo.mkdir()
  _git(repo, 'init', '-q', '-b', 'main')
  assert inventory(repo, root) == 1
  assert 'no specs/' in capsys.readouterr().err


def test_no_git_history_is_hard_error(tmp_path, capsys):
  root = make_root(tmp_path)
  repo = tmp_path / 'gitless'
  (repo / 'specs').mkdir(parents=True)
  assert inventory(repo, root) == 1
  err = capsys.readouterr().err
  assert 'git history' in err and 'load-bearing' in err


def test_inventory_writes_brief_with_header_and_sections(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root) == 0
  brief = root / 'reports/harvest-repo-2026-07-24.md'
  text = brief.read_text()
  assert text.startswith('---\nharvest: specs\nrepo: repo\n')
  assert f'repo_head: {_sha(repo)}' in text
  assert f'root: {root.resolve()}' in text
  assert 'date: 2026-07-24' in text
  assert 'prior_brief: none' in text
  # settled strata first, deferred last (spec §7)
  a = text.index('## specs/completed/a-spec.md')
  b = text.index('## specs/plans/completed/1-a-spec.md')
  c = text.index('## specs/deferred_items.md')
  assert a < b < c
  assert 'captures:' in text


def test_missing_dirs_get_notes_not_errors(tmp_path):
  root = make_root(tmp_path)
  repo = tmp_path / 'partial'
  (repo / 'specs').mkdir(parents=True)
  (repo / 'specs/only.md').write_text('# Only\n')
  _git(repo, 'init', '-q', '-b', 'main')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'one file')
  assert inventory(repo, root, date='2026-07-25') == 0
  text = (root / 'reports/harvest-partial-2026-07-25.md').read_text()
  assert 'note: specs/completed/: absent' in text
  assert 'note: specs/plans/: absent' in text
  assert 'note: specs/plans/completed/: absent' in text
  assert 'note: specs/deferred_items.md: absent' in text
  assert '## specs/only.md' in text


def test_empty_walk_is_hard_error(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='nomatch/*') == 1
  assert 'nothing to walk' in capsys.readouterr().err
```

- [x] **Step 2: Run tests to verify they fail**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py -q
```

Expected: collection error — `ModuleNotFoundError: No module named 'distill_specs'`.

- [x] **Step 3: Write the skeleton implementation**

Create `skills/llm-wiki/scripts/distill_specs.py`:

```python
'''Specs-harvest distiller (specs-harvest framework spec §4.1). Stdlib only.

inventory <repo> --root <wiki>: walk the repo's specs/ corpus, seed-grep,
build per-file introducing-SHA tables, pre-list previously-seen captures
from prior briefs, and write (or same-date-extend) the skeleton brief under
<root>/reports/. assemble <brief> --root <wiki>: validate ticked entries,
redact, write the raw/specs/ digest atomically, stamp the brief, and print
the source-page capture-note body for the ingest step.

Deterministic given its inputs; the only clock read is the --date default.
'''
import argparse
import datetime
import fnmatch
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

from distill_sessions import redact, slugify

KINDS = {'d': 'decision', 'r': 'rejected-approach', 'g': 'gotcha',
         'c': 'resolved-confusion', 'p': 'validated-pattern'}
BOUNDARIES = ('transferable', 'mixed', 'code-coupled')
SEP = ' · '  # U+00B7 middle dot: the capture-metadata field separator


def _atomic_write(path, text):
  '''Spec §7: validate everything first, then write last — and atomically.'''
  tmp = path.with_name('.tmp-' + path.name)
  tmp.write_text(text)
  os.replace(tmp, path)


def _git(repo, *args):
  proc = subprocess.run(['git', '-C', str(repo), *args],
                        capture_output=True, text=True)
  if proc.returncode != 0:
    raise RuntimeError(proc.stderr.strip() or f'git {args[0]} failed')
  return proc.stdout


# Settled strata first (spec §7): completed material is stable ground truth;
# live drafts are harvested last if at all; deferred_items.md is demoted to
# the tail (pilot: near-noise, open questions at most).
WALK_DIRS = ('specs/completed', 'specs/plans/completed', 'specs', 'specs/plans')
DEFERRED_FILE = 'specs/deferred_items.md'


def walk_specs(repo, only=None):
  '''Return (repo-relative .md paths in harvest order, absent-input notes).'''
  files, notes = [], []
  for d in WALK_DIRS:
    p = repo / d
    if not p.is_dir():
      notes.append(f'{d}/: absent')
      continue
    section = sorted(f for f in p.glob('*.md') if f.name != 'deferred_items.md')
    if not section:
      notes.append(f'{d}/: no .md files')
    files += [str(f.relative_to(repo)) for f in section]
  if (repo / DEFERRED_FILE).is_file():
    files.append(DEFERRED_FILE)
  else:
    notes.append(f'{DEFERRED_FILE}: absent')
  if only:
    files = [f for f in files if fnmatch.fnmatch(f, only)]
  return files, notes


def brief_path(root, repo_name, date):
  return root / 'reports' / f'harvest-{repo_name}-{date}.md'


def render_brief_header(repo_name, repo_path, head, root, date, files, prior):
  return [
    '---',
    'harvest: specs',
    f'repo: {repo_name}',
    f'repo_path: {repo_path}',
    f'repo_head: {head}',
    f'root: {root}',
    f'date: {date}',
    f'prior_brief: {prior}',
    'files_walked: >',
    '  ' + '; '.join(files),
    '---',
    '',
  ]


def render_file_section(rel, shas, seeds, prior_keys):
  lines = [f'## {rel}', '', 'shas:']
  lines += ([f'- {sha}{SEP}{subj}{SEP}{cls}' for sha, subj, cls in shas]
            or ['- none'])
  lines += ['', 'seeds:']
  lines += ([f'- L{n} {label}: {text}' for n, label, text in seeds]
            or ['- none'])
  lines += ['', 'previously seen:']
  lines += ([f'- {key}' for key in prior_keys] or ['- none'])
  lines += ['', 'captures:', '',
            '(extraction: read the whole file at repo_head; append entries '
            'per the brief grammar in SCHEMA.md)', '']
  return lines


def cmd_inventory(args):
  repo = Path(args.repo).resolve()
  root = Path(args.root).resolve()
  date = args.date or datetime.date.today().isoformat()
  if not (root / 'SCHEMA.md').is_file():
    print(f'error: {root} is not a wiki root (no SCHEMA.md)', file=sys.stderr)
    return 1
  if not (repo / 'specs').is_dir():
    print(f'error: no specs/ directory in {repo} (nothing to harvest)',
          file=sys.stderr)
    return 1
  try:
    head = _git(repo, 'rev-parse', '--short', 'HEAD').strip()
  except (RuntimeError, OSError) as exc:
    print(f'error: {repo} has no usable git history ({exc}); '
          'landing SHAs are load-bearing', file=sys.stderr)
    return 1
  repo_name = slugify(repo.name) or repo.name
  files, notes = walk_specs(repo, args.only)
  if not files:
    print('error: nothing to walk (check --only)', file=sys.stderr)
    return 1
  path = brief_path(root, repo_name, date)
  path.parent.mkdir(parents=True, exist_ok=True)
  body = render_brief_header(repo_name, repo, head, root, date, files, 'none')
  body += [f'note: {n}' for n in notes]
  if notes:
    body.append('')
  for rel in files:
    body += render_file_section(rel, [], [], [])
  _atomic_write(path, '\n'.join(body).rstrip('\n') + '\n')
  print(f'wrote {path}')
  return 0


def cmd_assemble(args):
  raise NotImplementedError  # Task 6


def main(argv=None):
  ap = argparse.ArgumentParser(
    description='Specs-harvest distiller: inventory and assemble.')
  sub = ap.add_subparsers(dest='cmd', required=True)
  inv = sub.add_parser('inventory',
                       help='walk a repo, write the skeleton brief')
  inv.add_argument('repo', help='repo checkout to harvest (explicit path)')
  inv.add_argument('--root', required=True,
                   help='wiki root (explicit, no default: wrong-wiki protection)')
  inv.add_argument('--date', default=None,
                   help='brief date YYYY-MM-DD (default: today)')
  inv.add_argument('--only', default=None,
                   help='glob over repo-relative paths, to batch large corpora')
  asm = sub.add_parser('assemble', help='ticked brief -> raw/specs digest')
  asm.add_argument('brief', help='the harvest brief (explicit path)')
  asm.add_argument('--root', required=True,
                   help='wiki root (must match the root recorded in the brief)')
  args = ap.parse_args(argv)
  return cmd_inventory(args) if args.cmd == 'inventory' else cmd_assemble(args)


if __name__ == '__main__':
  sys.exit(main())
```

- [x] **Step 4: Run the new tests — all pass; run the full suite — 101 + new all green**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: `109 passed` (101 existing + 8 new).

- [x] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "feat(llm-wiki): distill_specs skeleton - CLI, specs walk, hard errors, brief creation"
```

---

### Task 2: Seed grep

> Deviation: deferred-item seed pattern split into standalone DEFERRED_ITEM_PATTERN applied only to deferred_items.md (spec §5.1); signature is seed_hits(text, is_deferred=False).

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py` (add `SEED_PATTERNS`, `seed_hits`; wire into `cmd_inventory`)
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Produces: `SEED_PATTERNS` (tuple of `(label, compiled_regex)`), `seed_hits(text) -> [(line_no, label, line), …]` sorted by line number. `cmd_inventory` now calls `render_file_section(rel, [], seed_hits(text), [])`.
- Note: seed-hit lines pass through `redact()` before landing in the brief — a hardening beyond the spec's assemble-time redaction (briefs live on disk in `reports/`); deterministic, consistent with the distiller⊆lint containment contract.

- [x] **Step 1: Write the failing tests** (append to `test_distill_specs.py`)

```python
# --- Task 2: seed grep -------------------------------------------------------

SEED_DOC = '''# Doc

**Decision:** Delta Lake over plain Parquet.

Delta merge/upsert was rejected for idempotent re-runs.

## 10. Alternatives considered (recorded)

## 1. TL;DR

## Global Constraints

**Status: COMPLETE (2026-07-04)** — executed

> Deviation: retry moved to Task 9

- [ ] Redis-backed counter store (deferred)
'''


def test_seed_hits_every_pattern_class():
  labels = {label for _, label, _ in dsp.seed_hits(SEED_DOC)}
  assert labels == {'decision', 'rejected', 'recorded', 'tldr', 'policy',
                    'completion', 'deviation', 'deferred-item'}


def test_seed_hits_carry_line_numbers_and_text():
  hits = dsp.seed_hits(SEED_DOC)
  assert (3, 'decision', '**Decision:** Delta Lake over plain Parquet.') in hits


def test_seed_lines_are_redacted():
  doc = '**Decision:** use key sk-' + 'A' * 24 + ' for auth.\n'
  hits = dsp.seed_hits(doc)
  assert hits and 'sk-' + 'A' * 24 not in hits[0][2]
  assert '[REDACTED:openai-key]' in hits[0][2]


def test_brief_contains_seed_hits_or_none_marker(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root) == 0
  text = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  assert 'decision: **Decision:** use X over Y.' in text
  assert 'completion: **Status: COMPLETE (2026-01-01)**' in text
```

- [x] **Step 2: Run to verify failure**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py -q
```

Expected: 4 FAIL — 3 with `AttributeError: … has no attribute 'seed_hits'`, 1 (`test_brief_contains_seed_hits_or_none_marker`) with an assertion on the brief content.

- [x] **Step 3: Implement**

Add to `distill_specs.py` directly above `walk_specs` (constants adjacent to consumers):

```python
# Seed grep (spec §5.1). Hits are prompts for whole-file agent reading, not
# recall bounds (pilot: much of the yield was interleaved prose no seed regex
# can see) — precision here only orders attention.
SEED_PATTERNS = (
  ('decision', re.compile(r'^.*\*\*[^*\n]*\bdecision\b[^*\n]*\*\*.*$',
                          re.I | re.M)),
  ('rejected', re.compile(r'^.*\b(?:rejected|not taken|set aside)\b.*$',
                          re.I | re.M)),
  ('recorded', re.compile(r'^#{1,6} .*\(recorded\).*$', re.I | re.M)),
  ('tldr', re.compile(r'^#{1,6} .*\btl;?dr\b.*$', re.I | re.M)),
  ('policy', re.compile(r'^#{1,6} .*\b(?:policy|global constraints)\b.*$',
                        re.I | re.M)),
  ('completion', re.compile(r'^\*\*Status: COMPLETE.*$', re.M)),
  ('deviation', re.compile(r'^\s*> Deviation:.*$', re.M)),
  ('deferred-item', re.compile(r'^- \[[ x]\] .*$', re.M)),
)


def seed_hits(text):
  '''(line_no, label, redacted line ≤120 chars) per seed match, line order.
  Redacting here is belt-and-braces: briefs live in reports/ on disk.'''
  hits = []
  for label, pat in SEED_PATTERNS:
    for m in pat.finditer(text):
      line_no = text.count('\n', 0, m.start()) + 1
      hits.append((line_no, label, redact(m.group(0).strip())[0][:120]))
  return sorted(hits)
```

In `cmd_inventory`, change the section loop to:

```python
  for rel in files:
    text = (repo / rel).read_text()
    body += render_file_section(rel, [], seed_hits(text), [])
```

- [x] **Step 4: Run the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: `113 passed`.

- [x] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "feat(llm-wiki): specs-harvest seed grep with redacted hit lines"
```

---

### Task 3: Per-file SHA tables with substantive/mechanical classification

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py` (add `sha_table`, `_classify`; wire into `cmd_inventory`)
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Produces: `sha_table(repo, rel) -> [(sha, subject, 'substantive'|'mechanical'), …]` newest first, following renames; `_classify(status) -> str`.
- Definition (spec §4.1): mechanical ⇔ the commit's only change to this file is a pure rename/move with no content change — i.e. `git log --follow -M --name-status` reports status `R100` for it. Everything else (`A`, `M`, `R0xx`, missing status) is substantive.

- [x] **Step 1: Write the failing tests** (append)

```python
# --- Task 3: SHA tables ------------------------------------------------------

def test_sha_table_follows_rename_and_classifies(tmp_path):
  repo = make_repo(tmp_path)
  rows = dsp.sha_table(repo, 'specs/completed/a-spec.md')
  # newest first: retirement (pure git mv), v2 edit, v1 creation
  assert [cls for _, _, cls in rows] == \
    ['mechanical', 'substantive', 'substantive']
  assert rows[0][1] == 'chore: retire spec'
  assert rows[2][1] == 'spec: a v1'


def test_rename_with_edit_is_substantive(tmp_path):
  repo = make_repo(tmp_path)
  moved = repo / 'specs/plans/completed/1-a-spec.md'
  target = repo / 'specs/plans/completed/01-a-spec.md'
  target.write_text(moved.read_text() + '\nEdited during move.\n')
  moved.unlink()
  _git(repo, 'add', '-A')
  _git(repo, 'commit', '-qm', 'chore: renumber plan with edits')
  rows = dsp.sha_table(repo, 'specs/plans/completed/01-a-spec.md')
  assert rows[0][2] == 'substantive'


def test_brief_contains_sha_table(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root) == 0
  text = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  assert ' · chore: retire spec · mechanical' in text
  assert ' · spec: a v2 · substantive' in text
```

- [x] **Step 2: Run to verify failure**

Expected: 3 FAIL — 2 with `AttributeError: … no attribute 'sha_table'`, 1 (`test_brief_contains_sha_table`) with an assertion on the brief content.

- [x] **Step 3: Implement**

Add to `distill_specs.py` below `walk_specs`:

```python
def sha_table(repo, rel):
  '''Per-commit rows (sha, subject, class) newest first, following renames
  past retirement/reorg commits. Mechanical = the commit touches this file
  only as a pure rename/move with no content change (name-status R100);
  anything else — including a rename with edits (R0xx) — is substantive.'''
  out = _git(repo, 'log', '--follow', '-M', '--name-status',
             '--format=%x01%h%x02%s', '--', rel)
  rows, sha, subject, status = [], None, None, None
  for line in out.splitlines():
    if line.startswith('\x01'):
      if sha is not None:
        rows.append((sha, subject, _classify(status)))
      sha, subject = line[1:].split('\x02', 1)
      status = None
    elif line.strip():
      status = line.split('\t', 1)[0]
  if sha is not None:
    rows.append((sha, subject, _classify(status)))
  return rows


def _classify(status):
  return 'mechanical' if status and status.startswith('R100') else 'substantive'
```

In `cmd_inventory`'s loop: `body += render_file_section(rel, sha_table(repo, rel), seed_hits(text), [])`.

- [x] **Step 4: Run the full suite**

Expected: `116 passed`.

- [x] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "feat(llm-wiki): per-file SHA tables with substantive/mechanical classification"
```

---

### Task 4: Prior-brief dedup keys, same-date accretion, `--only` batching

> Deviation: per-file section rendering extracted to shared _render_new_sections() used by both cmd_inventory and _extend_brief; prior_briefs matches are anchored with re.fullmatch('harvest-<repo>-YYYY-MM-DD.md').

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py`
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: `parse_brief(text)` does **not** exist yet — this task adds a *minimal forward declaration* used only for prior-brief scanning; Task 5 replaces it with the full parser (same signature, superset behavior — the Task 4 tests must still pass after Task 5).
- Produces: `claim_hash(claim) -> str` (8 hex), `prior_briefs(root, repo_name, date) -> [Path]` (prior dates only, sorted), `seen_keys_by_file(briefs) -> {at_path: [key, …]}` with `key = '<id> · <at> · <hash8>'`, `_extend_brief(path, repo, head, files, seen) -> int`, `parse_brief(text) -> (header, entries, errors)`.
- Dedup rule (spec §5.1): keys come from ALL prior entries, ticked and unticked alike.

- [x] **Step 1: Write the failing tests** (append)

```python
# --- Task 4: prior briefs, accretion, --only ---------------------------------

PRIOR_BRIEF = '''---
harvest: specs
repo: repo
repo_path: /old/path
repo_head: 0000000
root: /old/root
date: 2026-07-01
prior_brief: none
files_walked: >
  specs/completed/a-spec.md
---

## specs/completed/a-spec.md

captures:

- [x] [d-01] Kept decision
  kind: decision · boundary: transferable
  at: specs/completed/a-spec.md §1 · sha: 1111111
  excerpt: "kept"
  claim: This one was approved.
- [ ] [g-01] Declined gotcha
  kind: gotcha · boundary: transferable
  at: specs/completed/a-spec.md §2 · sha: 1111111
  excerpt: "declined"
  claim: This one was declined.
'''


def test_seen_keys_include_ticked_and_unticked(tmp_path):
  b = tmp_path / 'harvest-repo-2026-07-01.md'
  b.write_text(PRIOR_BRIEF)
  seen = dsp.seen_keys_by_file([b])
  keys = seen['specs/completed/a-spec.md']
  assert len(keys) == 2  # declined entries dedup too (spec §5.1)
  assert any(k.startswith('d-01 · specs/completed/a-spec.md §1 · ') for k in keys)
  assert any(k.startswith('g-01 · specs/completed/a-spec.md §2 · ') for k in keys)


def test_claim_hash_is_whitespace_normalized():
  assert dsp.claim_hash('a  b\n c') == dsp.claim_hash('a b c')
  assert len(dsp.claim_hash('x')) == 8


def test_inventory_lists_previously_seen_and_prior_pointer(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  (root / 'reports/harvest-repo-2026-07-01.md').write_text(PRIOR_BRIEF)
  assert inventory(repo, root) == 0
  text = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  assert 'prior_brief: reports/harvest-repo-2026-07-01.md' in text
  assert '- d-01 · specs/completed/a-spec.md §1 · ' in text
  assert '- g-01 · specs/completed/a-spec.md §2 · ' in text


def test_same_date_rerun_appends_only_new_sections(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='specs/completed/*') == 0
  brief = root / 'reports/harvest-repo-2026-07-24.md'
  first = brief.read_text()
  assert '## specs/completed/a-spec.md' in first
  assert '## specs/plans/completed/1-a-spec.md' not in first
  # sentinel: hand-added capture entry must survive the re-run untouched
  brief.write_text(first + '- [x] [d-01] Hand-added\n')
  assert inventory(repo, root) == 0
  text = brief.read_text()
  assert text.count('## specs/completed/a-spec.md') == 1  # never duplicated
  assert '## specs/plans/completed/1-a-spec.md' in text   # appended
  assert '- [x] [d-01] Hand-added' in text                # never overwritten
  assert 'specs/deferred_items.md' in text.split('---')[1]  # files_walked union


def test_same_date_rerun_with_moved_head_is_error(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='specs/completed/*') == 0
  (repo / 'specs/new.md').write_text('# New\n')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'spec: new')
  assert inventory(repo, root) == 1
  assert 'repo_head' in capsys.readouterr().err


def test_same_date_rerun_with_no_new_files_is_noop(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root) == 0
  before = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  assert inventory(repo, root) == 0
  assert (root / 'reports/harvest-repo-2026-07-24.md').read_text() == before
  assert 'no new files' in capsys.readouterr().out


def test_only_glob_filters_walk(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='specs/plans/completed/*') == 0
  text = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  assert '## specs/plans/completed/1-a-spec.md' in text
  assert '## specs/completed/a-spec.md' not in text
```

- [x] **Step 2: Run to verify failure**

Expected: 7 FAIL (`AttributeError: … no attribute 'seen_keys_by_file'` etc.).

- [x] **Step 3: Implement**

Add to `distill_specs.py` (above `cmd_inventory`):

```python
def claim_hash(claim):
  '''Dedup-key half (spec §5.1): whitespace-normalized claim, 8 hex chars.'''
  norm = ' '.join((claim or '').split())
  return hashlib.sha256(norm.encode()).hexdigest()[:8]


def prior_briefs(root, repo_name, date):
  '''Prior briefs for this repo, sorted (ISO dates sort); the same-date
  brief is the accretion target, not a prior.'''
  return [p for p in
          sorted((root / 'reports').glob(f'harvest-{repo_name}-*.md'))
          if p.name != f'harvest-{repo_name}-{date}.md']


def seen_keys_by_file(briefs):
  '''{at-path: [id · at · claim-hash8, …]} across ALL prior entries —
  approved and declined alike, never only what was kept (spec §5.1).'''
  seen = {}
  for b in briefs:
    _, entries, _ = parse_brief(b.read_text())
    for e in entries:
      at = e['fields'].get('at')
      if not at:
        continue
      path = at.split(' ', 1)[0]
      key = (f'{e["id"]}{SEP}{at}{SEP}'
             f'{claim_hash(e["fields"].get("claim", ""))}')
      seen.setdefault(path, []).append(key)
  return seen


# Minimal brief reader for prior-brief scanning; Task 5 replaces it with
# the full validating parser (same signature, superset behavior).
ENTRY_RE = re.compile(r'^- \[([ x])\] \[([a-z])-(\d{2,})\] (.+)$')
FIELD_RE = re.compile(r'^  (kind|at|excerpt|claim|note): ?(.*)$')


def parse_brief(text):
  '''-> (header dict, entry list, error list).'''
  lines = text.split('\n')
  header, errors, i = {}, [], 0
  if lines and lines[0] == '---':
    i, key = 1, None
    while i < len(lines) and lines[i] != '---':
      line = lines[i]
      if line.startswith('  ') and key:
        header[key] = (header[key] + ' ' + line.strip()).strip()
      else:
        m = re.match(r'^([a-z_]+): ?(.*)$', line)
        if m:
          key = m.group(1)
          header[key] = '' if m.group(2) == '>' else m.group(2)
      i += 1
    i += 1
  entries, entry, field = [], None, None
  for line in lines[i:]:
    m = ENTRY_RE.match(line)
    if m:
      entry = {'ticked': m.group(1) == 'x',
               'id': f'{m.group(2)}-{m.group(3)}', 'prefix': m.group(2),
               'title': m.group(4).strip(), 'fields': {}, 'also': []}
      entries.append(entry)
      field = None
      continue
    if entry is None:
      continue
    fm = FIELD_RE.match(line)
    if fm:
      field = fm.group(1)
      entry['fields'][field] = fm.group(2).strip()
      continue
    if line.startswith('    ') and line.strip() and field:
      entry['fields'][field] += ' ' + line.strip()
      continue
    if line.strip():
      entry, field = None, None  # any other content ends the entry
  for e in entries:
    at = e['fields'].get('at', '')
    if SEP + 'sha: ' in at:
      e['fields']['at'], e['fields']['sha'] = at.rsplit(SEP + 'sha: ', 1)
  return header, entries, errors


def _extend_brief(path, repo, head, files, seen):
  '''Same-date re-run (spec §7): append sections for files not yet present;
  never overwrite or duplicate. One brief = one repo_head.'''
  text = path.read_text()
  header, _, _ = parse_brief(text)
  if header.get('repo_head') != head:
    print(f'error: {path.name} pins repo_head {header.get("repo_head")} but '
          f'HEAD is {head}; use a fresh --date (or re-run at the pinned head)',
          file=sys.stderr)
    return 1
  have = set(re.findall(r'^## (.+)$', text, re.M))
  new = [f for f in files if f not in have]
  if not new:
    print(f'{path.name}: no new files; brief unchanged')
    return 0
  body = []
  for rel in new:
    file_text = (repo / rel).read_text()
    body += render_file_section(rel, sha_table(repo, rel),
                                seed_hits(file_text), seen.get(rel, []))
  walked = [f.strip() for f in header.get('files_walked', '').split(';')
            if f.strip()]
  walked += [f for f in new if f not in walked]
  lines = text.rstrip('\n').split('\n')
  for i, line in enumerate(lines):
    if line == 'files_walked: >':
      lines[i + 1] = '  ' + '; '.join(walked)
      break
  _atomic_write(path, '\n'.join(lines) + '\n\n'
                + '\n'.join(body).rstrip('\n') + '\n')
  print(f'extended {path} (+{len(new)} files)')
  return 0
```

Rewrite the tail of `cmd_inventory` (everything after the `if not files:` block) to:

```python
  priors = prior_briefs(root, repo_name, date)
  seen = seen_keys_by_file(priors)
  prior = f'reports/{priors[-1].name}' if priors else 'none'
  path = brief_path(root, repo_name, date)
  path.parent.mkdir(parents=True, exist_ok=True)
  if path.exists():
    return _extend_brief(path, repo, head, files, seen)
  body = render_brief_header(repo_name, repo, head, root, date, files, prior)
  body += [f'note: {n}' for n in notes]
  if notes:
    body.append('')
  for rel in files:
    text = (repo / rel).read_text()
    body += render_file_section(rel, sha_table(repo, rel), seed_hits(text),
                                seen.get(rel, []))
  _atomic_write(path, '\n'.join(body).rstrip('\n') + '\n')
  print(f'wrote {path}')
  return 0
```

- [x] **Step 4: Run the full suite**

Expected: `123 passed`.

- [x] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "feat(llm-wiki): prior-brief dedup keys, same-date brief accretion, --only batching"
```

---

### Task 5: Full brief parser and entry validation

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py` (replace the minimal `parse_brief`; add `ALSO_RE`, `_split_kind`, `validate_entries`)
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Produces: `parse_brief(text)` (same signature; now also splits `kind:`→`kind`+`boundary`, collects `also` locations and duplicate-field errors), `validate_entries(entries, errors) -> None` (appends one `'<id>: reason'` string per defect in **ticked** entries).
- Validation classes (spec §9 "each validation failure class red-tested"): missing field (`kind`/`boundary`/`at`/`sha`/`excerpt`/`claim`; q: `at`/`claim`), kind↔prefix mismatch, unknown boundary, ticked `code-coupled`, square brackets in claim (BODY_CITE_RE discipline), duplicate id, duplicate field, unknown prefix. The `sha` requirement IS the echo rule here: every capture's basis is its introducing commit.

- [x] **Step 1: Write the failing tests** (append)

```python
# --- Task 5: parser + validation ---------------------------------------------

def _entry(ticked='x', eid='d-01', title='T', kind='decision',
           boundary='transferable', at='specs/a.md §1', sha='1234567',
           excerpt='"quoted"', claim='A claim.'):
  sha_part = f' · sha: {sha}' if sha else ''
  return (f'- [{ticked}] [{eid}] {title}\n'
          f'  kind: {kind} · boundary: {boundary}\n'
          f'  at: {at}{sha_part}\n'
          f'  excerpt: {excerpt}\n'
          f'  claim: {claim}\n')


def _brief_with(entries_text, root='/w'):
  return (f'---\nharvest: specs\nrepo: repo\nrepo_path: /r\n'
          f'repo_head: abc1234\nroot: {root}\ndate: 2026-07-24\n'
          f'prior_brief: none\nfiles_walked: >\n  specs/a.md\n---\n\n'
          f'## specs/a.md\n\ncaptures:\n\n{entries_text}')


def _validated(entries_text):
  header, entries, errors = dsp.parse_brief(_brief_with(entries_text))
  dsp.validate_entries(entries, errors)
  return errors


def test_parse_splits_kind_boundary_and_at_sha():
  _, entries, errors = dsp.parse_brief(_brief_with(_entry()))
  assert errors == []
  e = entries[0]
  assert e['fields']['kind'] == 'decision'
  assert e['fields']['boundary'] == 'transferable'
  assert e['fields']['at'] == 'specs/a.md §1'
  assert e['fields']['sha'] == '1234567'


def test_parse_collects_also_locations_and_continuations():
  text = ('- [x] [g-02] Title\n'
          '  kind: gotcha · boundary: mixed\n'
          '  at: specs/a.md §1 · sha: 1234567\n'
          '  (also specs/plans/completed/1-a.md L320 · sha: abcdef0)\n'
          '  excerpt: "first line\n'
          '    second line"\n'
          '  claim: Wrapped\n'
          '    claim text.\n')
  _, entries, _ = dsp.parse_brief(_brief_with(text))
  e = entries[0]
  assert e['also'] == [('specs/plans/completed/1-a.md L320', 'abcdef0')]
  # surrounding quotes are brief syntax, stripped at parse (the renderer
  # re-adds exactly one pair)
  assert e['fields']['excerpt'] == 'first line second line'
  assert e['fields']['claim'] == 'Wrapped claim text.'


def test_valid_entry_has_no_errors():
  assert _validated(_entry()) == []


def test_unticked_entries_skip_field_validation():
  assert _validated(_entry(ticked=' ', excerpt='', claim='')) == []


def test_missing_fields_each_reported():
  errors = _validated('- [x] [d-01] Bare\n')
  for req in ('kind', 'boundary', 'at', 'sha', 'excerpt', 'claim'):
    assert any(f'missing {req}' in err for err in errors), req


def test_missing_sha_is_reported():
  errors = _validated(_entry(sha=''))
  assert any('missing sha' in err for err in errors)


def test_kind_prefix_mismatch_is_reported():
  errors = _validated(_entry(eid='d-01', kind='gotcha'))
  assert any('does not match prefix' in err for err in errors)


def test_unknown_boundary_is_reported():
  errors = _validated(_entry(boundary='global'))
  assert any('unknown boundary' in err for err in errors)


def test_ticked_code_coupled_is_reported():
  errors = _validated(_entry(boundary='code-coupled'))
  assert any('code-coupled' in err for err in errors)


def test_square_brackets_in_claim_are_reported():
  errors = _validated(_entry(claim='See [pml1 §3.2] for details.'))
  assert any('square brackets' in err for err in errors)


def test_duplicate_id_is_reported():
  errors = _validated(_entry() + _entry())
  assert any('duplicate id' in err for err in errors)


def test_duplicate_field_is_reported():
  text = _entry() + '  claim: Second claim line.\n'
  errors = _validated(text)
  assert any('duplicate field claim' in err for err in errors)


def test_q_entry_needs_only_at_and_claim():
  text = ('- [x] [q-01] Open thing\n'
          '  at: specs/a.md §12.3\n'
          '  claim: Unresolved question prose.\n')
  assert _validated(text) == []


def test_q_entry_missing_claim_is_reported():
  errors = _validated('- [x] [q-01] Open thing\n  at: specs/a.md §12.3\n')
  assert any('q-01: missing claim' in err for err in errors)
```

- [x] **Step 2: Run to verify failure**

Expected: FAILs — `also`/duplicate-field/validation asserts fail against the minimal parser (`AttributeError: … no attribute 'validate_entries'` and assertion failures).

- [x] **Step 3: Implement**

In `distill_specs.py`, add `ALSO_RE` beside the other regexes and replace `parse_brief`'s entry loop + post-processing:

```python
ALSO_RE = re.compile(r'^  \(also (.+?)(?:' + SEP
                     + r'sha: ([0-9a-f]{7,40}))?\)$')
```

```python
  entries, entry, field = [], None, None
  for line in lines[i:]:
    m = ENTRY_RE.match(line)
    if m:
      entry = {'ticked': m.group(1) == 'x',
               'id': f'{m.group(2)}-{m.group(3)}', 'prefix': m.group(2),
               'title': m.group(4).strip(), 'fields': {}, 'also': []}
      entries.append(entry)
      field = None
      continue
    if entry is None:
      continue
    am = ALSO_RE.match(line)
    if am:
      entry['also'].append((am.group(1), am.group(2)))
      continue
    fm = FIELD_RE.match(line)
    if fm:
      field = fm.group(1)
      if field in entry['fields']:
        errors.append(f'{entry["id"]}: duplicate field {field}')
      entry['fields'][field] = fm.group(2).strip()
      continue
    if line.startswith('    ') and line.strip() and field:
      entry['fields'][field] += ' ' + line.strip()
      continue
    if line.strip():
      entry, field = None, None  # any other content ends the entry
  for e in entries:
    kind = e['fields'].get('kind', '')
    if SEP + 'boundary: ' in kind:
      e['fields']['kind'], e['fields']['boundary'] = \
        kind.split(SEP + 'boundary: ', 1)
    at = e['fields'].get('at', '')
    if SEP + 'sha: ' in at:
      e['fields']['at'], e['fields']['sha'] = at.rsplit(SEP + 'sha: ', 1)
    exc = e['fields'].get('excerpt', '')
    if len(exc) >= 2 and exc[0] == '"' and exc[-1] == '"':
      # the surrounding quotes are brief syntax, not excerpt content — the
      # digest renderer re-adds exactly one pair
      e['fields']['excerpt'] = exc[1:-1]
  return header, entries, errors
```

Add below `parse_brief`:

```python
def validate_entries(entries, errors):
  '''One error line per defect in TICKED entries (spec §9 failure classes).
  Unticked entries are the declined record: parsed, never field-validated.
  Requiring sha on every capture IS the echo rule here — a specs-harvest
  capture's basis is always its introducing commit (spec §4.2).'''
  seen_ids = set()
  for e in entries:
    if e['id'] in seen_ids:
      errors.append(f'{e["id"]}: duplicate id')
    seen_ids.add(e['id'])
  for e in entries:
    if not e['ticked']:
      continue
    f = e['fields']
    if e['prefix'] == 'q':
      for req in ('at', 'claim'):
        if not f.get(req):
          errors.append(f'{e["id"]}: missing {req}')
      continue
    if e['prefix'] not in KINDS:
      errors.append(f'{e["id"]}: unknown id prefix')
      continue
    for req in ('kind', 'boundary', 'at', 'sha', 'excerpt', 'claim'):
      if not f.get(req):
        errors.append(f'{e["id"]}: missing {req}')
    if f.get('kind') and f['kind'] != KINDS[e['prefix']]:
      errors.append(f'{e["id"]}: kind {f["kind"]} does not match prefix '
                    f'{e["prefix"]}')
    if f.get('boundary') and f['boundary'] not in BOUNDARIES:
      errors.append(f'{e["id"]}: unknown boundary {f["boundary"]}')
    if f.get('boundary') == 'code-coupled':
      errors.append(f'{e["id"]}: code-coupled entries must not be ticked '
                    '(engineering stratum waits for the code-wiki root)')
    if re.search(r'[\[\]]', f.get('claim', '')):
      errors.append(f'{e["id"]}: square brackets in claim '
                    '(BODY_CITE_RE discipline)')
```

- [x] **Step 4: Run the full suite** — Task 4's tests must still pass against the replaced parser.

Expected: `137 passed`.

- [x] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "feat(llm-wiki): full brief parser and ticked-entry validation"
```

---

### Task 6: `assemble` — redaction, id8, atomic digest write, brief stamp, source-page body

> Deviation: post-final-review hardening in 3d2c62f — title/at/(also …) values redacted at both output sinks; sha shape validated with [0-9a-f]{7,40}. Post-merge, afa9af8 also routes (also …) sha parsing through rsplit so malformed shas hit the validation gate.

**Files:**
- Modify: `skills/llm-wiki/scripts/distill_specs.py` (replace the `cmd_assemble` stub; add renderers and `_stamp_brief`)
- Test: `skills/llm-wiki/scripts/test_distill_specs.py`

**Interfaces:**
- Consumes: `parse_brief`, `validate_entries`, `_atomic_write`, `_git`, `redact`, `SEP`.
- Produces: `render_digest_entry(e) -> str`, `render_digest(header, entries, brief_name) -> (stem, text)`, `render_source_body(entries, repo_name) -> str`, `_stamp_brief(brief, stem)`, working `cmd_assemble(args) -> int`.
- Contract: all failures listed as `brief-error: …` on stderr, exit 1, nothing written; digest written atomically to `<root>/raw/specs/<date>-<repo>-specs-<id8>.md`; brief frontmatter gains `assembled: <stem>`; source-page body on stdout; drift (repo HEAD ≠ `repo_head`) and an unreachable `repo_path` are stderr **warnings**, never fatal (post-`repo_head` edits are the wiki's dated-claims staleness, spec §7).

- [x] **Step 1: Write the failing tests** (append; also add `import hashlib` to the test file's top import block, under `import os`)

```python
# --- Task 6: assemble --------------------------------------------------------

def _write_brief(root, repo, entries_text, date='2026-07-24'):
  head = _sha(repo)
  text = (f'---\nharvest: specs\nrepo: repo\nrepo_path: {repo}\n'
          f'repo_head: {head}\nroot: {root.resolve()}\ndate: {date}\n'
          f'prior_brief: none\nfiles_walked: >\n'
          f'  specs/completed/a-spec.md; specs/deferred_items.md\n---\n\n'
          f'## specs/completed/a-spec.md\n\ncaptures:\n\n{entries_text}')
  path = root / 'reports' / f'harvest-repo-{date}.md'
  path.write_text(text)
  return path


def _ticked_pair(repo):
  sha = _sha(repo)
  return (f'- [x] [d-01] Use X over Y\n'
          f'  kind: decision · boundary: transferable\n'
          f'  at: specs/completed/a-spec.md §1 · sha: {sha}\n'
          f'  excerpt: "**Decision:** use X over Y."\n'
          f'  claim: X was chosen over Y.\n'
          f'- [ ] [g-01] Declined\n'
          f'  kind: gotcha · boundary: transferable\n'
          f'  at: specs/completed/a-spec.md §2 · sha: {sha}\n'
          f'  excerpt: "More prose."\n'
          f'  claim: Declined claim.\n'
          f'- [x] [q-01] Open thing\n'
          f'  at: specs/deferred_items.md L3\n'
          f'  claim: Whether the later thing matters is unresolved.\n')


def assemble(brief, root):
  return dsp.main(['assemble', str(brief), '--root', str(root)])


def _digests(root):
  return sorted((root / 'raw/specs').glob('*.md'))


def test_assemble_golden_digest(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  sha = _sha(repo)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  assert assemble(brief, root) == 0
  blocks = [(f'[d-01] Use X over Y\n'
             f'at: specs/completed/a-spec.md §1 · sha: {sha}\n'
             f'excerpt: "**Decision:** use X over Y."'),
            (f'[q-01] Open thing\n'
             f'at: specs/deferred_items.md L3\n'
             f'Whether the later thing matters is unresolved.')]
  id8 = hashlib.sha256('\n\n'.join(blocks).encode()).hexdigest()[:8]
  stem = f'2026-07-24-repo-specs-{id8}'
  files = _digests(root)
  assert [p.name for p in files] == [f'{stem}.md']
  expected = (f'---\n'
              f'source: specs-harvest\n'
              f'repo: repo\n'
              f'repo_head: {sha}\n'
              f'date: 2026-07-24\n'
              f'files: 2\n'
              f'captures: 1\n'
              f'open_questions: 1\n'
              f'note: >\n'
              f'  Assembled by distill_specs.py from '
              f'harvest-repo-2026-07-24.md: 1 ticked of\n'
              f'  2 proposed captures; unticked entries remain in the brief '
              f'as\n'
              f'  the declined record.\n'
              f'brief: reports/harvest-repo-2026-07-24.md\n'
              f'files_read: >\n'
              f'  specs/completed/a-spec.md; specs/deferred_items.md\n'
              f'---\n\n'
              f'Ground-truth entries for the capture notes in '
              f'wiki/sources/{stem}.md.\n'
              f'Each entry: verbatim excerpt from the repo file at the\n'
              f'stated location, introducing commit sha.\n\n'
              + '\n\n'.join(blocks) + '\n')
  assert files[0].read_text() == expected


def test_assemble_emits_source_page_body_and_stamps_brief(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  sha = _sha(repo)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  assert assemble(brief, root) == 0
  out = capsys.readouterr().out
  assert (f'### [d-01] Use X over Y\n'
          f'kind: decision · at: repo specs/completed/a-spec.md §1 · '
          f'basis: git:{sha}\n'
          f'X was chosen over Y.') in out
  assert '[q-01]' not in out           # q entries ride in the digest only
  assert '[g-01]' not in out           # unticked stays out
  stem = _digests(root)[0].stem
  brief_text = brief.read_text()
  fm = brief_text.split('---')[1]
  assert f'assembled: {stem}' in fm


def test_source_page_position_drops_line_detail(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  sha = _sha(repo)
  entry = (f'- [x] [g-05] Padded headers\n'
           f'  kind: gotcha · boundary: transferable\n'
           f'  at: specs/completed/a-spec.md Task 2 (L176) · sha: {sha}\n'
           f'  excerpt: "x"\n'
           f'  claim: Headers are padded.\n')
  brief = _write_brief(root, repo, entry)
  assert assemble(brief, root) == 0
  out = capsys.readouterr().out
  assert 'at: repo specs/completed/a-spec.md Task 2 · basis:' in out
  # the digest keeps the full position
  assert 'Task 2 (L176) · sha:' in _digests(root)[0].read_text()


def test_reassembly_is_byte_identical(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  assert assemble(brief, root) == 0
  first = _digests(root)[0]
  before = first.read_bytes()
  assert assemble(brief, root) == 0
  assert [p.name for p in _digests(root)] == [first.name]  # no duplicates
  assert first.read_bytes() == before
  # stamp is idempotent too
  assert brief.read_text().count('assembled:') == 1


def test_validation_failure_reports_all_writes_nothing(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  bad = ('- [x] [d-01] No fields at all\n'
         '- [x] [g-01] Bracketed claim\n'
         '  kind: gotcha · boundary: transferable\n'
         f'  at: specs/completed/a-spec.md §1 · sha: {_sha(repo)}\n'
         '  excerpt: "x"\n'
         '  claim: Bad [locator] here.\n')
  brief = _write_brief(root, repo, bad)
  assert assemble(brief, root) == 1
  err = capsys.readouterr().err
  assert 'brief-error: d-01: missing excerpt' in err
  assert 'brief-error: g-01: square brackets in claim' in err
  assert _digests(root) == []                       # nothing written
  assert 'assembled:' not in brief.read_text()      # no stamp either


def test_each_validation_class_exits_1_and_writes_nothing(tmp_path, capsys):
  '''Spec §9: every failure class through the CLI gate — exit 1, no file.
  (Duplicate-id and duplicate-field are grammar-level classes covered by the
  Task 5 unit tests; the gate path is identical.)'''
  repo = make_repo(tmp_path)
  sha = _sha(repo)
  ok = dict(ticked='x', eid='d-01', title='T', kind='decision',
            boundary='transferable', at='specs/a.md §1', sha=sha,
            excerpt='"x"', claim='A claim.')
  bad_cases = [
    dict(ok, excerpt=''),                  # missing field
    dict(ok, sha=''),                      # missing sha (echo rule)
    dict(ok, kind='gotcha'),               # kind does not match prefix
    dict(ok, boundary='global'),           # unknown boundary
    dict(ok, boundary='code-coupled'),     # ticked code-coupled
    dict(ok, claim='Bad [locator] ref.'),  # square brackets in claim
  ]
  for i, case in enumerate(bad_cases):
    case_root = make_root(tmp_path / f'case{i}')
    brief = _write_brief(case_root, repo, _entry(**case))
    assert assemble(brief, case_root) == 1, case
    assert _digests(case_root) == [], case
    assert 'assembled:' not in brief.read_text(), case
  capsys.readouterr()


def test_no_ticked_entries_is_error(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  unticked = _ticked_pair(repo).replace('- [x]', '- [ ]')
  brief = _write_brief(root, repo, unticked)
  assert assemble(brief, root) == 1
  assert 'no ticked entries' in capsys.readouterr().err
  assert _digests(root) == []


def test_root_mismatch_refused(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  other = tmp_path / 'other-wiki'
  (other / 'raw/specs').mkdir(parents=True)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  assert assemble(brief, other) == 1
  assert 'root mismatch' in capsys.readouterr().err
  assert _digests(other) == [] and _digests(root) == []


def test_planted_secret_never_reaches_digest_or_stdout(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  secret = 'sk-' + 'A' * 24
  sha = _sha(repo)
  entry = (f'- [x] [g-01] Leaky\n'
           f'  kind: gotcha · boundary: transferable\n'
           f'  at: specs/completed/a-spec.md §1 · sha: {sha}\n'
           f'  excerpt: "uses {secret} inline"\n'
           f'  claim: The example key {secret} leaked into the spec.\n'
           f'  note: also here {secret}\n')
  brief = _write_brief(root, repo, entry)
  assert assemble(brief, root) == 0
  digest = _digests(root)[0].read_text()
  out = capsys.readouterr().out
  assert secret not in digest and secret not in out
  assert '[REDACTED:openai-key]' in digest


def test_drift_warns_but_assembles(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  (repo / 'specs/drift.md').write_text('# Drift\n')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'spec: drift')
  assert assemble(brief, root) == 0
  assert 'warning:' in capsys.readouterr().err
  assert len(_digests(root)) == 1


def test_missing_repo_path_warns_but_assembles(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  brief.write_text(brief.read_text().replace(
    f'repo_path: {repo}', 'repo_path: /nonexistent/repo'))
  assert assemble(brief, root) == 0
  assert 'cannot check drift' in capsys.readouterr().err
```

- [x] **Step 2: Run to verify failure**

Expected: the assemble tests FAIL with `NotImplementedError`.

- [x] **Step 3: Implement**

Replace the `cmd_assemble` stub in `distill_specs.py`:

```python
def render_digest_entry(e):
  '''One ground-truth digest block (pilot format). Redaction on everything
  that carries source text — the lint extension is only the backstop.'''
  f = e['fields']
  lines = [f'[{e["id"]}] {e["title"]}']
  if e['prefix'] == 'q':
    lines.append(f'at: {f["at"]}')
  else:
    lines.append(f'at: {f["at"]}{SEP}sha: {f["sha"]}')
  for loc, sha in e['also']:
    lines.append(f'  (also {loc}{SEP}sha: {sha})' if sha
                 else f'  (also {loc})')
  if e['prefix'] == 'q':
    lines.append(redact(f['claim'])[0])
  else:
    lines.append(f'excerpt: "{redact(f["excerpt"])[0]}"')
    if f.get('note'):
      lines.append(f'note: {redact(f["note"])[0]}')
  return '\n'.join(lines)


def render_digest(header, entries, brief_name):
  '''-> (stem, digest text). id8 hashes ONLY the ordered ticked entry
  blocks — not the header or preamble — so an unchanged brief re-assembles
  to the identical filename and bytes (spec §5.2).'''
  ticked = [e for e in entries if e['ticked']]
  caps = [e for e in ticked if e['prefix'] != 'q']
  qs = [e for e in ticked if e['prefix'] == 'q']
  blocks = [render_digest_entry(e) for e in caps + qs]
  id8 = hashlib.sha256('\n\n'.join(blocks).encode()).hexdigest()[:8]
  stem = f'{header["date"]}-{header["repo"]}-specs-{id8}'
  files = [f.strip() for f in header.get('files_walked', '').split(';')
           if f.strip()]
  n_total = sum(1 for e in entries if e['prefix'] != 'q')
  fm = [
    '---',
    'source: specs-harvest',
    f'repo: {header["repo"]}',
    f'repo_head: {header["repo_head"]}',
    f'date: {header["date"]}',
    f'files: {len(files)}',
    f'captures: {len(caps)}',
    f'open_questions: {len(qs)}',
    'note: >',
    f'  Assembled by distill_specs.py from {brief_name}: {len(caps)} '
    'ticked of',
    f'  {n_total} proposed captures; unticked entries remain in the brief as',
    '  the declined record.',
    f'brief: reports/{brief_name}',
    'files_read: >',
    '  ' + '; '.join(files),
    '---',
    '',
    f'Ground-truth entries for the capture notes in wiki/sources/{stem}.md.',
    f'Each entry: verbatim excerpt from the {header["repo"]} file at the',
    'stated location, introducing commit sha.',
    '',
  ]
  # '\n'.join leaves fm's trailing '' as a single newline; add one more so a
  # blank line separates the preamble from the first entry block.
  return stem, '\n'.join(fm) + '\n' + '\n\n'.join(blocks) + '\n'


def render_source_body(entries, repo_name):
  '''Capture-note body for the wiki/sources page (stdout; the agent wraps
  frontmatter and runs the normal ingest op — this script never writes under
  wiki/). q entries ride in the digest only; positions drop a trailing (L…)
  detail; (also …) locations are digest-only (spec §5.3, pilot).'''
  blocks = []
  for e in entries:
    if not e['ticked'] or e['prefix'] == 'q':
      continue
    f = e['fields']
    pos = re.sub(r'\s*\(L[0-9–-]+\)$', '', f['at'])
    blocks.append(f'### [{e["id"]}] {e["title"]}\n'
                  f'kind: {f["kind"]}{SEP}at: {repo_name} {pos}{SEP}'
                  f'basis: git:{f["sha"]}\n'
                  + redact(f['claim'])[0])
  return '\n\n'.join(blocks) + '\n'


def _stamp_brief(brief, stem):
  lines = brief.read_text().split('\n')
  lines = [l for l in lines if not l.startswith('assembled: ')]
  close = lines.index('---', 1)
  lines.insert(close, f'assembled: {stem}')
  _atomic_write(brief, '\n'.join(lines))


def cmd_assemble(args):
  brief = Path(args.brief).resolve()
  root = Path(args.root).resolve()
  if not brief.is_file():
    print(f'error: brief not found: {brief}', file=sys.stderr)
    return 1
  header, entries, errors = parse_brief(brief.read_text())
  if header.get('root') != str(root):
    print(f'brief-error: root mismatch: brief says {header.get("root")}, '
          f'--root is {root} (wrong-wiki protection)', file=sys.stderr)
    return 1
  validate_entries(entries, errors)
  if not any(e['ticked'] for e in entries):
    errors.append('brief: no ticked entries')
  if errors:
    for err in errors:
      print(f'brief-error: {err}', file=sys.stderr)
    return 1
  repo_path = Path(header.get('repo_path', ''))
  try:
    head = _git(repo_path, 'rev-parse', '--short', 'HEAD').strip()
    if head != header.get('repo_head'):
      print(f'warning: {header["repo"]} HEAD {head} != brief repo_head '
            f'{header["repo_head"]} — post-inventory edits are the wiki\'s '
            'dated-claims staleness, not re-harvested here', file=sys.stderr)
  except (RuntimeError, OSError):
    print(f'warning: cannot check drift ({repo_path} unavailable)',
          file=sys.stderr)
  stem, digest = render_digest(header, entries, brief.name)
  out = root / 'raw/specs' / f'{stem}.md'
  out.parent.mkdir(parents=True, exist_ok=True)
  _atomic_write(out, digest)
  _stamp_brief(brief, stem)
  print(render_source_body(entries, header['repo']), end='')
  print(f'wrote {out.relative_to(root)}', file=sys.stderr)
  return 0
```

(The module already imports `hashlib` at top from Task 1 — no new imports needed in `distill_specs.py`.)

- [x] **Step 4: Run the full suite**

Expected: `148 passed`.

- [x] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/distill_specs.py skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "feat(llm-wiki): assemble - validation gate, redaction, id8 atomic digest, brief stamp, source-page body"
```

---

### Task 7: Pilot golden pair (bls-stats)

> Deviation: 'import re' added to the test file (the brief's own Step-2 code requires it).

**Files:**
- Modify: `skills/llm-wiki/scripts/test_distill_specs.py` (fixture module-level constants + 3 tests)

**Interfaces:**
- Consumes: `dsp.main(['assemble', …])`, `dsp.parse_brief`, the reference pilot files listed in Global Constraints.
- Produces: `PILOT_BRIEF` (str constant), a `pilot_case(tmp_path)` builder, tests comparing assemble output to the pilot digest **content**.

**Background (deviation note, record in the PR):** the pilot brief was never materialized — `/Users/lowell/research-wiki/reports/` is empty; the pilot digest is hand-authored and hand-wrapped, and its header `note:`/`source:` free text predates `assemble`. So this golden pair is: (a) a `PILOT_BRIEF` fixture **transcribed** from the two real pilot files, (b) assembled, (c) compared to the real pilot digest **entry-by-entry, whitespace-normalized** (content golden), plus header-count asserts — never byte-golden against the hand-authored file. The byte-golden case is Task 6's.

- [x] **Step 1: Build the `PILOT_BRIEF` fixture constant**

Transcribe from the two read-only reference files into a module-level string constant near the top of `test_distill_specs.py`. Mapping rule, per capture id (`d-01`…`d-06`, `g-01`…`g-08`, `c-01`, `c-02`, `p-01`…`p-04`, `q-01`, `q-02`):

- checkbox line `- [x] [<id>] <title>` — title from the digest entry line `[<id>] <title>` (identical on the source page).
- `  kind: <kind> · boundary: transferable` — kind from the source page's `kind:` field (prefix map: d→decision, g→gotcha, c→resolved-confusion, p→validated-pattern). All 20 ticked pilot captures were transferable-or-mixed; use `transferable` throughout (boundary is a brief-only field; it does not surface in digest or source page, so this cannot diverge from the reference output).
- `  at: <path> <pos> · sha: <sha>` — from the digest entry's `at:` line (which reads `at: <path> <pos> · sha: <sha>`); keep the position VERBATIM including any `(L…)` detail. A digest continuation line `  (also <path> <pos> · sha: <sha>)` becomes the identical `(also …)` line in the brief.
- `  excerpt: "<text>"` — the digest entry's excerpt with its hand-wrapping joined to one line by single spaces. Keep the embedded `\"` escapes exactly as they appear in the file — which means the Python fixture constants MUST be raw strings (`r'''…'''`), or every backslash doubled; in a plain triple-quoted literal `\"` collapses to `"` and the content comparison fails (d-06, g-01, g-02, g-06, p-02 all carry them).
- `  claim: <text>` — the source page's claim paragraph (the prose under the metadata line), wrapping joined to one line.
- `  note: <text>` — only for `g-05` and `p-03` (the two digest entries with `note:` trailers).
- q entries: `- [x] [q-01] <title>` / `  at: <path> <pos>` (no sha — q-01 and q-02 have none) / `  claim: <prose>`; q-02's `(also …)` continuation carries no sha, exercising the sha-less `ALSO_RE` branch.

Brief header for the fixture (`repo_head: ad8abe0`, `date: 2026-07-24`, `repo: bls-stats`; `repo_path` and `root` are placeholders filled per-test):

```python
PILOT_HEADER = '''---
harvest: specs
repo: bls-stats
repo_path: {repo_path}
repo_head: ad8abe0
root: {root}
date: 2026-07-24
prior_brief: none
files_walked: >
  specs/completed/bls-stats-architecture.md; specs/completed/audit_5-7-26.md; specs/plans/completed/1-bls-stats-architecture.md; specs/plans/completed/2-audit_5-7-26.md; specs/deferred_items.md
---

## specs/completed/bls-stats-architecture.md

captures:

'''
# PILOT_ENTRIES: the 22 transcribed entries, in pilot digest order
# (d-01..d-06, g-01..g-08, c-01, c-02, p-01..p-04, q-01, q-02), all ticked.
# MUST be a raw string (r'''…''') so the pilot's literal \" sequences survive.
PILOT_BRIEF = PILOT_HEADER + PILOT_ENTRIES
```

The `{repo_path}`/`{root}` placeholders are filled with `str.replace`, **never `str.format`** — pilot excerpts contain literal braces (g-02: `{feed}_{MMDDYYYY}.htm`) that make `.format()` raise `KeyError`.

(The transcription is mechanical but long — 22 entries. Do it by reading the two reference files side by side; do not paraphrase, trim, or "fix" anything in excerpts, claims, titles, positions, or SHAs. Where the digest wraps a line, join with exactly one space.)

- [x] **Step 2: Write the tests** (append; also add `from pathlib import Path` to the test file's top import block)

```python
# --- Task 7: pilot golden pair -----------------------------------------------

PILOT_DIGEST = Path('/Users/lowell/research-wiki/raw/specs/'
                    '2026-07-24-bls-stats-specs-harvest.md')
PILOT_SOURCE = Path('/Users/lowell/research-wiki/wiki/sources/'
                    '2026-07-24-bls-stats-specs-harvest.md')

needs_pilot = pytest.mark.skipif(
  not PILOT_DIGEST.exists(), reason='pilot reference wiki not on this machine')


def _norm_blocks(text):
  '''Entry blocks ([id]-keyed), each whitespace-normalized to one string —
  the hand-authored pilot digest is reference for CONTENT, not wrapping.'''
  body = text.split('---', 2)[2]
  body = body.split('\n[', 1)
  body = '[' + body[1] if len(body) == 2 else ''
  blocks = re.split(r'\n\n(?=\[)', body.strip())
  return [' '.join(b.split()) for b in blocks]


def pilot_case(tmp_path):
  root = make_root(tmp_path)
  brief = root / 'reports/harvest-bls-stats-2026-07-24.md'
  # str.replace, not str.format: pilot excerpts contain literal {braces}
  brief.write_text(PILOT_BRIEF
                   .replace('{repo_path}', '/nonexistent/bls-stats')
                   .replace('{root}', str(root.resolve())))
  return root, brief


@needs_pilot
def test_pilot_brief_round_trips_to_pilot_digest_content(tmp_path, capsys):
  root, brief = pilot_case(tmp_path)
  assert assemble(brief, root) == 0
  got = _digests(root)[0].read_text()
  assert _norm_blocks(got) == _norm_blocks(PILOT_DIGEST.read_text())
  # header counts match the pilot's
  assert 'files: 5' in got
  assert 'captures: 20' in got
  assert 'open_questions: 2' in got
  assert 'repo_head: ad8abe0' in got


@needs_pilot
def test_pilot_source_body_matches_pilot_page(tmp_path, capsys):
  root, brief = pilot_case(tmp_path)
  assert assemble(brief, root) == 0
  out = capsys.readouterr().out
  want = PILOT_SOURCE.read_text().split('---', 2)[2]
  norm = lambda t: [' '.join(b.split())
                    for b in re.split(r'\n(?=### \[)', t.strip())]
  assert norm(out) == norm(want)


@needs_pilot
def test_pilot_digest_filename_follows_id8_rule(tmp_path, capsys):
  root, brief = pilot_case(tmp_path)
  assert assemble(brief, root) == 0
  name = _digests(root)[0].name
  assert re.fullmatch(r'2026-07-24-bls-stats-specs-[0-9a-f]{8}\.md', name)
```

Notes for the implementer:
- The pilot digest's hand-authored preamble (lines 27–29) and `note:`/`source:` header free text differ from `assemble`'s deterministic output by design — `_norm_blocks` starts at the first `[`-keyed entry, so only entry content is compared. The grandfathered pilot filename is asserted nowhere (spec §5.2: reference for content, not filename).
- If an entry-block mismatch appears, diff the normalized block lists element-wise — the failure is almost always a transcription slip in `PILOT_BRIEF`, not a renderer bug; fix the transcription to match the reference files, never the reference files.
- `repo_path` is deliberately nonexistent → exercises the drift-check warning path on a realistic corpus; stderr is ignored here.

- [x] **Step 3: Run the new tests**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_specs.py -q
```

Expected: all pass (the 3 new ones live-compare against `/Users/lowell/research-wiki`; on machines without it they skip).

- [x] **Step 4: Run the full suite**

Expected: `151 passed` (148 + 3; 3 skipped instead on machines without the reference wiki).

- [x] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/test_distill_specs.py
git commit -m "test(llm-wiki): pilot golden pair - bls-stats brief fixture round-trips to pilot digest content"
```

---

### Task 8: Lint extension — secret + decision-basis checks over `raw/specs/`

**Files:**
- Modify: `skills/llm-wiki/scripts/lint_wiki.py:215-231` (the `check_sessions` function)
- Test: `skills/llm-wiki/scripts/test_lint_wiki.py` (append only — the existing 31 tests must not change)

**Interfaces:**
- Consumes: existing `SECRET_PATTERNS` (lint_wiki.py:196-209), `DECISION_META_RE`/`BASIS_OK_RE` (lint_wiki.py:211-212), `run_checks` dispatch (lint_wiki.py:283 — unchanged; `check_sessions` keeps its name).
- Produces: `check_sessions(root)` now scans both `raw/sessions/*.md` and `raw/specs/*.md`; new helper `_check_spec_decisions(text, rel)` enforcing the specs-harvest echo rule: a `[d-NN]` digest entry needs `· sha: <hex>` on an `at:` line. New finding message: `basis: [d-NN] needs an at: line with sha: <sha>`.
- Free coverage to assert, not build: the backlog INFO check (lint_wiki.py:255-265) already `rglob`s all of `raw/`, so an uningested `raw/specs/` digest queues as `INFO … backlog: …` with no code change — this is spec §6 step 7.

- [x] **Step 1: Write the failing tests** (append to `test_lint_wiki.py`; touch nothing above)

```python
# --- specs-harvest extension (specs-harvest framework spec R4) ---------------

def write_spec_digest(root, name, text):
  d = root / 'raw/specs'
  d.mkdir(parents=True, exist_ok=True)
  (d / name).write_text(text)


PILOTED_DIGEST = '''---
source: specs-harvest
repo: bls-stats
repo_head: ad8abe0
date: 2026-07-24
files: 5
captures: 2
open_questions: 1
brief: reports/harvest-bls-stats-2026-07-24.md
---

Ground-truth entries for the capture notes in wiki/sources/x.md.

[d-01] Flat files primary; BLS API v2 demoted to utility
at: specs/completed/bls-stats-architecture.md §6.1 · sha: 1d26d71
excerpt: "The BLS API v2 cannot carry full-universe daily increments"

[g-05] LABSTAT files: space-padded headers and M13 annual rows
at: specs/plans/completed/1-bls-stats-architecture.md L2611 · sha: 50e0f52
  (also specs/completed/audit_5-7-26.md C-2 · sha: 168da46)
excerpt: "rename(lambda c: c.strip())"
note: dedicated fix commit

[q-01] QCEW routine print count
at: specs/completed/bls-stats-architecture.md §12.3
The revision lifecycle is an unverified data-source fact.
'''


def test_piloted_specs_digest_at_lines_pass_clean(tmp_path):
  root = make_wiki(tmp_path)
  write_spec_digest(root, '2026-07-24-bls-stats-specs-abcd1234.md',
                    PILOTED_DIGEST)
  assert [f for f in lint_wiki.run_checks(root) if f[0] == 'ERROR'] == []


def test_secret_in_raw_specs_is_error(tmp_path):
  root = make_wiki(tmp_path)
  write_spec_digest(root, 'leak.md', 'tok ghp_' + 'A' * 36 + '\n')
  assert any(f[0] == 'ERROR' and 'secret' in f[2]
             and f[1] == 'raw/specs/leak.md'
             for f in lint_wiki.run_checks(root))


def test_decision_entry_without_sha_is_error(tmp_path):
  root = make_wiki(tmp_path)
  write_spec_digest(root, 'bad.md',
                    '[d-01] Missing basis\nat: specs/a.md §1\nexcerpt: "x"\n')
  assert any(f[0] == 'ERROR' and '[d-01]' in f[2] and 'basis' in f[2]
             for f in lint_wiki.run_checks(root))


def test_non_decision_entry_without_sha_is_not_basis_error(tmp_path):
  root = make_wiki(tmp_path)
  write_spec_digest(root, 'q.md',
                    '[q-01] Open question\nat: specs/a.md §12.3\nProse.\n')
  assert not any('basis' in f[2] for f in lint_wiki.run_checks(root))


def test_kind_decision_line_in_raw_specs_needs_basis(tmp_path):
  root = make_wiki(tmp_path)
  write_spec_digest(root, 'k.md', 'kind: decision · turns: 3\n')
  assert any(f[0] == 'ERROR' and 'basis' in f[2]
             for f in lint_wiki.run_checks(root))


def test_raw_specs_digest_without_source_page_is_backlog_info(tmp_path):
  root = make_wiki(tmp_path)
  write_spec_digest(root, '2026-07-24-r-specs-abcd1234.md',
                    '[g-01] x\nat: specs/a.md §1 · sha: 1234567\n'
                    'excerpt: "y"\n')
  assert any(f[0] == 'INFO' and 'backlog' in f[2]
             for f in lint_wiki.run_checks(root))
```

- [x] **Step 2: Run to verify failure**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_lint_wiki.py -q
```

Expected: `test_secret_in_raw_specs_is_error`, `test_decision_entry_without_sha_is_error`, `test_kind_decision_line_in_raw_specs_needs_basis` FAIL (checks don't cover `raw/specs` yet); the other three already pass (backlog is generic; clean stays clean) — that is expected, keep them as regression guards.

- [x] **Step 3: Implement**

Replace `check_sessions` (lint_wiki.py:215-231) with:

```python
def check_sessions(root):
  '''Secret + decision-basis backstop over the distilled raw classes:
  raw/sessions/ (session digests, spec §16.3) and raw/specs/ (specs-harvest
  digests, specs-harvest framework §4.3).'''
  findings = []
  for sub in ('raw/sessions', 'raw/specs'):
    class_dir = root / sub
    if not class_dir.exists():
      continue
    for p in sorted(class_dir.glob('*.md')):
      rel = p.relative_to(root)
      text = p.read_text()
      for cls, pat in SECRET_PATTERNS:
        if pat.search(text):
          findings.append(
            ('ERROR', str(rel), f'secret: {cls}-shaped string present'))
      for m in DECISION_META_RE.finditer(text):
        if not BASIS_OK_RE.search(m.group(1)):
          findings.append(
            ('ERROR', str(rel),
             'basis: kind: decision needs basis: user-turn or git:<sha>'))
      if sub == 'raw/specs':
        findings += _check_spec_decisions(text, rel)
  return findings


# Specs-harvest echo rule: a [d-NN] ground-truth entry's basis is its
# introducing commit — its block must carry `· sha: <hex>` on an at: line.
SPEC_ENTRY_SPLIT_RE = re.compile(r'\n(?=\[[a-z]-\d)')
SPEC_AT_SHA_RE = re.compile(r'^at: .+ · sha: [0-9a-f]{7,40}(?:\s|$)', re.M)


def _check_spec_decisions(text, rel):
  findings = []
  for block in SPEC_ENTRY_SPLIT_RE.split(text):
    m = re.match(r'\[(d-\d+)\]', block)
    if m and not SPEC_AT_SHA_RE.search(block):
      findings.append(
        ('ERROR', str(rel),
         f'basis: [{m.group(1)}] needs an at: line with sha: <sha>'))
  return findings
```

The `raw/sessions` behavior is byte-for-byte the old logic (same messages, same scoping) — only the loop wrapper and the `raw/specs` branch are new.

- [x] **Step 4: Run the full suite**

```bash
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: all pass — 31 original lint tests untouched and green, 6 new lint tests green, distill/bootstrap suites unaffected.

- [x] **Step 5: Commit**

```bash
git add skills/llm-wiki/scripts/lint_wiki.py skills/llm-wiki/scripts/test_lint_wiki.py
git commit -m "feat(llm-wiki): lint secret + decision-basis checks extended to raw/specs"
```

---

### Task 9: Contract extension — schema template, bootstrap, INSTALL script list

> Deviation: shipped as two commits (feat + a small style follow-up for GITKEEP_DIRS indent idiom); one-line docstring accuracy edit in test_bootstrap_wiki.py ("two managed scripts" → "managed scripts").

**Files:**
- Modify: `skills/llm-wiki/scripts/schema-template.md` (version→2, secrets rule, new section)
- Modify: `skills/llm-wiki/scripts/bootstrap_wiki.py` (6 touchpoints, listed below)
- Modify: `skills/llm-wiki/INSTALL.md` (installed-script mentions)
- Test: `skills/llm-wiki/scripts/test_bootstrap_wiki.py` (append)

**Interfaces:**
- Consumes: `MANAGED_SCRIPTS` (bootstrap_wiki.py:48), `REQUIRED_FILES` (:66-69), `WIKI_DIRS` (:53-56), `GITKEEP_DIRS` (:59), `REQUIRED_DIRS` (:62-65), `_SCHEMA_VERSION_RE` (:43).
- Produces: a bundle whose bootstrap installs `distill_specs.py` beside its import target `distill_sessions.py` (side-by-side install is what makes the sibling import work at a wiki root: `python3 <root>/scripts/distill_specs.py` puts `scripts/` on `sys.path[0]`), creates `raw/specs/`, and seeds a SCHEMA.md carrying the specs-harvest contract at `schema-version: 2`.

- [x] **Step 1: Write the failing tests** (append to `test_bootstrap_wiki.py`; add `import subprocess` and `import sys` to its import block — currently absent)

```python
# --- specs-harvest extension (specs-harvest framework spec R5/R6) ------------

def test_bootstrap_installs_distill_specs_and_raw_specs_dir(tmp_path):
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  assert (root / 'scripts/distill_specs.py').is_file()
  assert (root / 'raw/specs/.gitkeep').is_file()


def test_seeded_schema_contains_specs_harvest_contract(tmp_path):
  '''Template parity (spec §9): a bootstrapped root inherits the new
  sections without hand edits.'''
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  schema = (root / 'SCHEMA.md').read_text()
  assert 'schema-version: 2' in schema
  assert '## Specs-harvest briefs and digests' in schema
  assert 'raw/specs/' in schema
  assert '`raw/sessions/` or `raw/specs/`' in schema
  assert '- [x] [d-01]' in schema  # the brief entry grammar is codified


def test_installed_distill_specs_runs_beside_its_sibling(tmp_path):
  '''The sibling import (distill_specs -> distill_sessions) must work from
  an installed wiki root, not just the bundle dir.'''
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  proc = subprocess.run(
    [sys.executable, str(root / 'scripts/distill_specs.py'), '--help'],
    capture_output=True, text=True)
  assert proc.returncode == 0
  assert 'inventory' in proc.stdout and 'assemble' in proc.stdout
```

- [x] **Step 2: Run to verify failure**

Expected: 3 FAIL (`distill_specs.py` not installed; schema lacks the section).

- [x] **Step 3: Edit `bootstrap_wiki.py`** — all six touchpoints:

1. `:48` → `MANAGED_SCRIPTS = ('lint_wiki.py', 'distill_sessions.py', 'distill_specs.py')`
2. `:53-56` `WIKI_DIRS` → add `'raw/specs',` (keep tuple order alphabetical-ish: after `'raw/sessions'`); update the comment above it (`:51-52`) to include `raw/specs/`.
3. `:59` `GITKEEP_DIRS` → add `'raw/specs'` after `'raw/sessions'`.
4. `:62-65` `REQUIRED_DIRS` → the same addition (it mirrors `WIKI_DIRS`).
5. `:66-69` `REQUIRED_FILES` → add `'scripts/distill_specs.py',`.
6. Prose: module docstring `:4-5` "the two runtime scripts (lint_wiki.py, distill_sessions.py)" → "the three runtime scripts (lint_wiki.py, distill_sessions.py, distill_specs.py)"; comment `:57-58` "scripts/ by the two installed scripts" → "…the three installed scripts"; warning `:320-321` "run lint_wiki.py / distill_sessions.py with" → "run lint_wiki.py / distill_sessions.py / distill_specs.py with".

- [x] **Step 4: Edit `schema-template.md`:**

1. Line 1: bump the marker to `schema-version: 2` (same comment text otherwise) — the contract gained a raw class and a metadata variant; `bootstrap_wiki.py --check` will now flag roots still on v1 as STALE, which is the desired reconcile nudge. (Safe for the existing suite: the version tests in `test_bootstrap_wiki.py:118-135` compare relationally — `0 <` bundle, seeded root `==` bundle — and never pin the literal `1`.)
2. Secrets rule (line 113): change `any residual secret-shaped string under `raw/sessions/` is a lint error.` to `any residual secret-shaped string under `raw/sessions/` or `raw/specs/` is a lint error.`
3. Append after the capture-note section (after line 127), using a fenced code block for the example exactly like the existing capture-note section does:

```markdown
## Specs-harvest briefs and digests (specs-harvest framework)

`raw/specs/` holds specs-harvest digests: ground truth distilled from a
repo's `specs/` corpus (specs, completed specs, completed plans, deferred
items). Digest filename: `<date>-<repo>-specs-<id8>.md`, where `id8` is the
first 8 hex chars of SHA-256 over the ordered ticked-capture content — an
unchanged brief re-assembles to the identical file. Digest entries are
`[<id>]`-keyed ground truth: `at: <path> <position> · sha: <introducing
commit>` plus a verbatim excerpt; `[q-NN]` open questions carry `at:` and
prose only and are appended to `open-questions.md` at ingest.

Specs-harvest source pages use the `at:` capture-metadata variant — the
session-digest `turns:` locator is replaced by a repo locator and the basis
is always a commit:

    ### [d-01] Flat files primary; BLS API v2 demoted to utility
    kind: decision · at: bls-stats specs/completed/bls-stats-architecture.md §6.1 · basis: git:1d26d71
    One- to three-sentence self-contained claim (no square brackets).

Briefs (`reports/harvest-<repo>-<date>.md`) are working files, not wiki
content: `distill_specs.py inventory` writes the skeleton, agents extract
and adversarially verify capture entries, the human ticks. A capture entry
is a checkbox line plus 2-space-indented fields; 4-space-indented lines
continue the previous field, and `(also <path> <pos> · sha: <sha>)` lines
add secondary locations:

    - [x] [d-01] Flat files primary; BLS API v2 demoted to utility
      kind: decision · boundary: transferable
      at: specs/completed/bls-stats-architecture.md §6.1 · sha: 1d26d71
      excerpt: "The BLS API v2 cannot carry full-universe daily increments"
      claim: One- to three-sentence self-contained claim (no square brackets).

`[q-NN]` open-question entries carry only `at:` and `claim:`. Boundary
verdicts: `transferable | mixed | code-coupled`; a code-coupled entry is
never ticked. `[x]` = approved for assembly; unticked entries persist as
the durable declined record — later inventories dedup against all prior
entries, approved and declined, keyed on locator + claim hash. The echo
rule holds: every capture's basis is its introducing commit (`sha:` on the
`at:` line); a `[d-NN]` digest entry without one is a lint error, as is any
secret-shaped string under `raw/specs/`.
```

(The indented examples above stand in for ``` fences — in the template use real fenced blocks, matching the capture-note section's style.)

- [x] **Step 5: Edit `INSTALL.md`** — `:58-59`: "installs `lint_wiki.py` and `distill_sessions.py`" → "installs `lint_wiki.py`, `distill_sessions.py`, and `distill_specs.py`". Leave the ops list for Task 10.

- [x] **Step 6: Run the full suite**

Expected: all pass, including the 15 original bootstrap tests (they iterate `bw.MANAGED_SCRIPTS` / `bw.REQUIRED_DIRS` dynamically, so they absorb the additions).

- [x] **Step 7: Commit**

```bash
git add skills/llm-wiki/scripts/bootstrap_wiki.py skills/llm-wiki/scripts/schema-template.md skills/llm-wiki/scripts/test_bootstrap_wiki.py skills/llm-wiki/INSTALL.md
git commit -m "feat(llm-wiki): contract extension - schema template v2, bootstrap installs distill_specs, raw/specs scaffold"
```

---

### Task 10: SKILL.md `harvest` operation + repo gates

**Files:**
- Modify: `skills/llm-wiki/SKILL.md` (new op before `## Attribution` at :103; description + version in frontmatter)
- Modify: `skills/llm-wiki/INSTALL.md` (ops list `:82-83`)

**Interfaces:**
- Consumes: the installed-script invocation voice (`python3 $LLM_WIKI_ROOT/scripts/<name>.py` with args spelled inline — see the ingest op :57-74); the brief/digest contracts from Tasks 1–6 and the SCHEMA section from Task 9.
- Budget check: SKILL.md body is currently 731 words; this op adds ~210 — well under the writing-skills ~1,500-word median. Description is 466 of 1,024 chars; the addition below keeps it ≤ 650.

- [x] **Step 1: Add the operation** — insert after the `### verify` section (ends :101), before `## Attribution`:

```markdown
### harvest `<repo-path>` (specs → wiki)

Turn a repo's `specs/` corpus (specs, completed specs, completed plans,
deferred items) into a `raw/specs/` digest. Supervised; one repo at a time.

1. Inventory (mechanical): `python3 $LLM_WIKI_ROOT/scripts/distill_specs.py
   inventory <repo-path> --root $LLM_WIKI_ROOT` — walks `specs/`, seed-greps,
   builds per-file SHA tables, lists previously-seen captures, and writes the
   skeleton brief to `reports/harvest-<repo>-<date>.md` (`--help` for
   `--only`, which batches large corpora into one accreting same-date brief).
2. Extract: read each walked file WHOLE at the brief's pinned `repo_head` —
   seed hits are prompts, not bounds. Append capture entries per the brief
   grammar in `SCHEMA.md`. Hard rules: transferable or
   mixed-with-standalone-claim content only; the proprietary stratum never
   enters a brief; `deferred_items.md` yields open questions at most.
3. Verify (independent adversarial pass, per file): excerpt verbatim by grep
   at `repo_head`; basis sha confirmed as the *introducing* commit (follow
   past mechanical renames; pickaxe when unsure); kind honest under the echo
   rule (downgrade where unmet); challenge each boundary verdict. Amend
   entries in place.
4. Dedup: merge spec↔plan duplicates into one entry with multi-source `at:`
   lines; drop items already in prior briefs or existing digests.
5. Human ticks `[x]` — the `raw/` gate. Unticked entries stay in the brief
   as the durable declined record.
6. Assemble: `python3 $LLM_WIKI_ROOT/scripts/distill_specs.py assemble
   <brief> --root $LLM_WIKI_ROOT` — validates, redacts, writes the digest,
   stamps the brief, prints the source-page body. Then ingest the digest via
   the normal flow (capture-note body; `q-NN` entries append to
   `open-questions.md`).
```

- [x] **Step 2: Frontmatter** — in the `description`, after "…'install the research wiki' on a new machine or for a second wiki root", append: `; and 'harvest', 'harvest the specs', or turning a repo's specs/ corpus (specs, plans, deferred items) into wiki captures.` Bump `version: "1.1"` → `"1.2"`.

- [x] **Step 3: INSTALL.md ops list** (`:82-83`): "`ingest`, `query`, `lint`, and `verify` all work against this root" → "`ingest`, `query`, `lint`, `verify`, and `harvest` all work against this root".

- [x] **Step 4: Run the repo gates and the full suite**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: both gates exit 0 (description ≤1024 chars); full suite green.

- [x] **Step 5: Commit**

```bash
git add skills/llm-wiki/SKILL.md skills/llm-wiki/INSTALL.md
git commit -m "feat(llm-wiki): harvest operation - specs corpus to raw/specs digest via distill_specs"
```

---

### Task 11: Root SCHEMA.md amendment — **HUMAN-GATED** — and live-root deployment

> Deviation (human-approved at the completion gate): also added the schema-version 2 marker line so the live root SCHEMA.md is byte-identical to the template and the staleness check works.

**Files (all OUTSIDE this repo — no repo commit in this task):**
- Modify: `/Users/lowell/research-wiki/SCHEMA.md` (only with explicit approval)
- Modify: `/Users/lowell/research-wiki/wiki/log.md` (append one line)
- Refresh: `/Users/lowell/research-wiki/scripts/` via bootstrap `--force`

The spec (R5) makes the root copy the governing, human-gated contract: the template change (Task 9) reaches only *future* roots; the live research wiki must be amended by hand, past the human.

- [x] **Step 1: Prepare the amendment.** Build the exact edit for `/Users/lowell/research-wiki/SCHEMA.md`:
  1. The same two content changes as Task 9's template edit: the secrets-rule line gains `or `raw/specs/``, and the `## Specs-harvest briefs and digests (specs-harvest framework)` section is appended (identical text).
  2. Additionally insert the version marker as line 1: `<!-- schema-version: 2 (bump on a breaking contract change; `bootstrap_wiki.py --check` flags a root whose schema is behind the bundle) -->` — the live root currently has **no** marker at all (it is the single line by which it diverges from the template today); adding it heals that drift and lets `--check` version-compare in the future.

- [x] **Step 2: STOP — present the diff to your human partner and ask for approval.** Do not touch the live root without an explicit yes in this session. If the human is unavailable, mark this task deferred at the plan-completion gate and finish the rest of the protocol; the framework is fully testable without the live amendment.

- [x] **Step 3 (on approval): apply the edit**, then append the log line to `/Users/lowell/research-wiki/wiki/log.md` (grammar `## [YYYY-MM-DD] <op> | <subject> | <note>`, `schema` is an allowed op; use today's date):

```
## [2026-07-24] schema | specs-harvest | raw/specs class, at: capture variant, brief format codified
```

- [x] **Step 4 (on approval): deploy the scripts the harvest op invokes** — the live root still carries the pre-plan `lint_wiki.py` and no `distill_specs.py`:

```bash
python3 ~/.claude/skills/llm-wiki/scripts/bootstrap_wiki.py /Users/lowell/research-wiki --force
```

(`--force` refreshes only managed scripts and creates any missing dirs; it never touches `SCHEMA.md` or wiki content. `raw/specs/` already exists at this root from the pilot.)

- [x] **Step 5: Verify the live root:**

```bash
python3 /Users/lowell/research-wiki/scripts/lint_wiki.py /Users/lowell/research-wiki
```

Expected: exit 0; the pilot digest under `raw/specs/` produces no ERROR (its `at:` lines pass clean — R4's acceptance on real data). A `backlog:` INFO line for any uningested raw file is normal.

```bash
python3 ~/.claude/skills/llm-wiki/scripts/bootstrap_wiki.py --check /Users/lowell/research-wiki
```

Expected: exit 0, `check: tooling is current` (schema at v2 matches the bundle, scripts byte-identical).

---

## Execution order and dependencies

Tasks 1→7 are strictly sequential (each extends `distill_specs.py`/its tests). Task 8 depends on nothing after Task 1 conceptually but runs after 7 to keep one file in flight at a time. Task 9 needs Task 1 (the script must exist in the bundle for bootstrap to install). Task 10 needs Tasks 6 and 9 (it documents both commands and the SCHEMA section). Task 11 is last and human-gated.

Spec-requirement coverage: R1 → Tasks 1–4; R2 → Tasks 5–7; R3 → Task 10; R4 → Task 8; R5 → Tasks 9 + 11; R6 → every task's suite run + Task 10's gates.
