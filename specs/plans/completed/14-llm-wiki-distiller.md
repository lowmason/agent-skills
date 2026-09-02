# llm-wiki Session Distiller Implementation Plan

**Status: COMPLETE (2026-07-23)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `scripts/distill_sessions.py` (spec §16.4): a deterministic, stdlib-only stage-1 distiller that turns Claude Code / claude.ai conversation history into redacted, one-file-per-session markdown digests under `raw/sessions/`, ready to ingest as wiki source pages.

**Architecture:** A shared core (redaction, block rendering, thread reconstruction, digest writing, idempotence) plus two thin source adapters — `claude-code` (per-session JSONL under `~/.claude/projects/`) and `claude-ai` (a single `conversations.json` from the data export). The core is fully testable with synthetic fixtures; the `claude-code` adapter is pinned to the real JSONL schema introspected 2026-07-22 (Appendix A); the `claude-ai` adapter is built against the export's documented shape and flagged provisional until an export lands.

**Tech Stack:** Python ≥ 3.12 (tested on Homebrew 3.13 via `uv run`), standard library only — `json`, `pathlib`, `re`, `argparse`, `sys` (spec §16.4). No third-party deps.

**Shared spec / relationship to Plan 13:** This plan and [`13-llm-wiki.md`](13-llm-wiki.md) both implement `specs/completed/llm-wiki-spec.md`. Plan 13 built the wiki scaffold, `SCHEMA.md`, `lint_wiki.py`, and the skill; this plan adds the second script into the same `~/research-wiki/scripts/` directory. **Retirement note:** the spec stays live until *both* plans complete — when retiring one, the other is still a live plan implementing the same spec, so leave `specs/llm-wiki-spec.md` in place. (Both plans are now complete; see Post-execution below for the spec's actual retirement.)

## Repositories referenced by this plan

- **`~/research-wiki`** — the wiki repo (created in Plan 13, Task 2). All `scripts/…`, `raw/sessions/…` paths are inside it. Equals `$LLM_WIKI_ROOT` (default `~/research-wiki`). If Plan 13 has not run, `git init` it and create `scripts/` and `raw/sessions/` first (Task 1 Step 0 covers this defensively).
- **`~/.claude/projects/`** — read-only input for the `claude-code` source (one `.jsonl` per session, grouped by encoded-cwd project directory). The distiller never writes here.
- **`~/archives/claude-projects-*.tar.gz`** — the archive of record (Plan 13, S0). The live `~/.claude/projects/` is the working input; the tarball is the durable backup.

## Global Constraints

Copied verbatim from the spec (§16.4, §14); every task's requirements implicitly include these.

- **Python:** stdlib only (`json`, `pathlib`, `re`, `argparse`, `sys`); `pathlib` over `os.path`; single quotes; **two-space indentation**; Python ≥ 3.12.
- **Dates:** ISO-8601 (`YYYY-MM-DD`) everywhere. Session dates come from record timestamps.
- **Redaction is always on** — never gated behind a flag. Key-shaped tokens (`sk-…`, `ghp_…`, `AKIA…`), PEM blocks, `password|token|secret` assignments, and long high-entropy strings become `[REDACTED:<class>]`; per-file counts land in the digest header.
- **Idempotence:** the output filename embeds the session id; an existing digest for that session is skipped, so the distiller is safe to re-run.
- **Backstop coupling:** the redaction pattern set here must stay **at or below** the lint backstop in `lint_wiki.py` (`SECRET_PATTERNS`, Plan 13 Task 9). Anything this distiller fails to redact must still be caught by the lint check under `raw/sessions/`. Keep the two in sync; when adding a pattern here, confirm the lint set already covers it.
- **Format is not a stable API:** the Claude Code JSONL shape (Appendix A) is an implementation detail. Adapters read defensively — unknown record `type`s are skipped, missing keys default, and a file that fails to parse is reported on stderr without aborting the run.

## Out of scope

- **Stage-2 ingest of digests into wiki source pages** — that is the `llm-wiki` skill's ingest operation with the capture-note variant (spec §16.5), run by hand, not code.
- **The S1 artifact-trail corpus** (spec §16.2.1) — those are ordinary documents ingested directly; they don't go through this distiller.
- **Deciding which digests to keep** — the distiller emits a digest per session (zero captures is a legitimate outcome, §16.5); triage happens at ingest.

## Test command

Stdlib-only, directory-scoped, tests co-located (matches Plan 13):

```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

---

### Task 1: Skeleton — CLI, source dispatch, per-file error handling, exit contract

Spec §16.4 usage line. Establish the argument parser, the dispatch to a source adapter, the OUT_DIR handling, and the exit contract (0 ok; 1 if any input file failed to parse, with failures on stderr and good files still written).

**Files:**
- Create: `~/research-wiki/scripts/distill_sessions.py`
- Create: `~/research-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Produces (used by every later task):
  - `main(argv: list[str] | None = None) -> int` — parses `--source {claude-code,claude-ai}`, `--project SUBSTR`, `--since YYYY-MM-DD`, `--include-sidechains`, positional `SRC`, `OUT_DIR`; dispatches; returns 1 if any file failed to parse else 0.
  - `Options` — a plain object/namespace carrying the parsed flags to adapters (use `argparse.Namespace` directly; no custom class).

- [x] **Step 0: Ensure the wiki repo and script dirs exist (defensive; no-op if Plan 13 ran)**

Run:
```bash
mkdir -p ~/research-wiki/scripts ~/research-wiki/raw/sessions && \
[ -d ~/research-wiki/.git ] || (cd ~/research-wiki && git init -q) && echo ok
```
Expected: `ok`.

- [x] **Step 1: Write the failing test**

`~/research-wiki/scripts/test_distill_sessions.py`:
```python
'''Tests for distill_sessions.py. Stdlib + pytest only; synthetic fixtures.'''
import json
from pathlib import Path

import distill_sessions as ds


def test_main_unknown_source_exits_nonzero(capsys, tmp_path):
  rc = ds.main(['--source', 'nope', str(tmp_path), str(tmp_path / 'out')])
  assert rc != 0  # argparse rejects the choice


def test_main_empty_src_dir_is_ok(tmp_path):
  src = tmp_path / 'projects'
  src.mkdir()
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', str(src), str(out)])
  assert rc == 0
  assert out.exists()  # OUT_DIR is created even with nothing to write
```

> Deviation: `test_main_unknown_source_exits_nonzero` was rewritten to
> `with pytest.raises(SystemExit) as exc: ds.main(...); assert exc.value.code != 0`
> (test file gained `import pytest`). The plan's literal version cannot pass: argparse's
> invalid-choice path calls `parser.error()`, which raises `SystemExit(2)` rather than
> returning, so `rc = ds.main(...)` never executes. Gate-resolved pre-flight (human).

- [x] **Step 2: Run the test to verify it fails**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q
```
Expected: FAIL — `ModuleNotFoundError: No module named 'distill_sessions'`.

- [x] **Step 3: Write the minimal implementation**

`~/research-wiki/scripts/distill_sessions.py`:
```python
'''Stage-1 session distiller (spec §16.4). Stdlib only; deterministic.

Reads Claude Code / claude.ai conversation history and writes one redacted
markdown digest per session into OUT_DIR. See Appendix A of the plan for the
claude-code JSONL schema this pins to.
'''
import argparse
import json
import re
import sys
from pathlib import Path


def main(argv=None):
  ap = argparse.ArgumentParser(description='Distill session history into digests.')
  ap.add_argument('--source', required=True, choices=['claude-code', 'claude-ai'])
  ap.add_argument('--project', default=None,
                  help='claude-code: keep only sessions whose project dir contains this substring')
  ap.add_argument('--since', default=None, help='keep only sessions dated >= YYYY-MM-DD')
  ap.add_argument('--include-sidechains', action='store_true',
                  help='keep subagent sidechain turns (dropped by default)')
  ap.add_argument('src', help='SRC: a projects dir / .jsonl (claude-code) or conversations.json (claude-ai)')
  ap.add_argument('out_dir', help='OUT_DIR for digests')
  args = ap.parse_args(argv)

  src = Path(args.src)
  out = Path(args.out_dir)
  out.mkdir(parents=True, exist_ok=True)

  failures = []
  if args.source == 'claude-code':
    sessions = iter_claude_code(src, args, failures)
  else:
    sessions = iter_claude_ai(src, args, failures)

  for session in sessions:
    write_digest(session, out)

  for f in failures:
    print(f'parse-failure: {f}', file=sys.stderr)
  return 1 if failures else 0


def iter_claude_code(src, args, failures):
  return []  # implemented in Task 6


def iter_claude_ai(src, args, failures):
  return []  # implemented in Task 7


def write_digest(session, out):
  pass  # implemented in Task 5


if __name__ == '__main__':
  sys.exit(main())
```

- [x] **Step 4: Run the test to verify it passes**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q
```
Expected: PASS (2 passed).

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/distill_sessions.py scripts/test_distill_sessions.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(distill): CLI skeleton, source dispatch, exit contract' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 2: Redaction (always-on)

Spec §16.4 "Redaction — always on" and §16.3.3. A pure function that replaces secret-shaped substrings with `[REDACTED:<class>]` and returns per-class counts. This set must stay ≤ the lint backstop (Plan 13 Task 9 `SECRET_PATTERNS`).

**Files:**
- Modify: `~/research-wiki/scripts/distill_sessions.py`
- Modify: `~/research-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Produces: `redact(text: str) -> tuple[str, dict[str, int]]` — redacted text plus `{class: count}` for classes that fired.

- [x] **Step 1: Write the failing tests**

Append to `test_distill_sessions.py`:
```python
def test_redact_openai_and_github_and_aws():
  text = ('key sk-' + 'A' * 24 + ' tok ghp_' + 'B' * 36 +
          ' aws AKIA' + 'C' * 16)
  out, counts = ds.redact(text)
  assert 'sk-' + 'A' * 24 not in out
  assert 'ghp_' not in out
  assert 'AKIA' + 'C' * 16 not in out
  assert counts.get('openai-key') == 1
  assert counts.get('github-token') == 1
  assert counts.get('aws-key') == 1
  assert '[REDACTED:openai-key]' in out


def test_redact_pem_and_assignment():
  text = ('-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----\n'
          'password = "hunter2hunter2hunter2"')
  out, counts = ds.redact(text)
  assert 'BEGIN RSA PRIVATE KEY' not in out
  assert counts.get('pem-block') == 1
  assert counts.get('assignment') == 1


def test_redact_leaves_normal_prose_and_uuids_alone():
  text = 'The sampler ran in 3.2s; session 3747ad0a-e925-4819-8610-7b29bc40e5be.'
  out, counts = ds.redact(text)
  assert out == text
  assert counts == {}
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q -k redact
```
Expected: FAIL — `AttributeError: module has no attribute 'redact'`.

- [x] **Step 3: Write the implementation**

Add to `distill_sessions.py`:
```python
# Secret-shaped patterns. MUST stay <= lint_wiki.py SECRET_PATTERNS (the
# backstop): anything not redacted here must still be caught by the linter under
# raw/sessions/. Order matters — PEM before assignment before high-entropy.
_REDACTORS = [
  ('pem-block', re.compile(
    r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----',
    re.S)),
  ('openai-key', re.compile(r'sk-[A-Za-z0-9]{20,}')),
  ('github-token', re.compile(r'ghp_[A-Za-z0-9]{30,}')),
  ('aws-key', re.compile(r'AKIA[0-9A-Z]{16}')),
  ('assignment', re.compile(
    r'(?i)\b(?:password|secret|token)\b\s*[:=]\s*[\'"]?[A-Za-z0-9/+_-]{12,}[\'"]?')),
  ('high-entropy', re.compile(r'[A-Za-z0-9+/=_-]{40,}')),
]


def _is_high_entropy(token):
  '''A long token is high-entropy only if it mixes >=3 of lower/upper/digit —
  keeps UUIDs (hex+hyphen, 2 classes) and long words out of the net.'''
  classes = sum(bool(re.search(p, token))
                for p in (r'[a-z]', r'[A-Z]', r'[0-9]'))
  return classes >= 3


def redact(text):
  counts = {}

  def _sub(cls):
    def repl(m):
      if cls == 'high-entropy' and not _is_high_entropy(m.group(0)):
        return m.group(0)
      counts[cls] = counts.get(cls, 0) + 1
      return f'[REDACTED:{cls}]'
    return repl

  for cls, pat in _REDACTORS:
    text = pat.sub(_sub(cls), text)
  return text, counts
```

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q
```
Expected: PASS.

> Note on ordering: `sk-…`/`ghp_…`/`AKIA…` run before `high-entropy`, so a key is labeled by its specific class, not the generic one. The `assignment` class catches `token = "…"` forms the specific key patterns miss.

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/distill_sessions.py scripts/test_distill_sessions.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(distill): always-on redaction with per-class counts' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 3: Block rendering — narrative text and tool-trace elision

Spec §16.4 "Noise removal". Render a message's `content` (str or list of blocks; Appendix A) into narrative text: keep `text` blocks, drop `thinking`, and collapse `tool_use` blocks into a one-line trace `[tools: bash ×14, str_replace ×3]`. `tool_result` blocks carry no narrative (they are the elided plumbing).

**Files:**
- Modify: `~/research-wiki/scripts/distill_sessions.py`
- Modify: `~/research-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Produces:
  - `extract_text(content) -> str` — concatenated `text` block text (or the str content); ignores thinking/tool blocks.
  - `tool_names(content) -> list[str]` — `name` of each `tool_use` block, in order.
  - `tool_trace(names: list[str]) -> str` — `'[tools: bash ×14, str_replace ×3]'` (counts, first-seen order); `''` if none.

- [x] **Step 1: Write the failing tests**

Append to `test_distill_sessions.py`:
```python
def test_extract_text_from_blocks_and_str():
  blocks = [{'type': 'thinking', 'thinking': 'hmm'},
            {'type': 'text', 'text': 'Hello.'},
            {'type': 'tool_use', 'name': 'bash', 'input': {}, 'id': 'x'}]
  assert ds.extract_text(blocks) == 'Hello.'
  assert ds.extract_text('plain string') == 'plain string'


def test_tool_names_and_trace():
  blocks = [{'type': 'tool_use', 'name': 'bash', 'id': '1'},
            {'type': 'tool_use', 'name': 'bash', 'id': '2'},
            {'type': 'tool_use', 'name': 'str_replace', 'id': '3'},
            {'type': 'text', 'text': 'done'}]
  assert ds.tool_names(blocks) == ['bash', 'bash', 'str_replace']
  assert ds.tool_trace(ds.tool_names(blocks)) == '[tools: bash ×2, str_replace ×1]'
  assert ds.tool_trace([]) == ''
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q -k "extract_text or tool_"
```
Expected: FAIL.

- [x] **Step 3: Write the implementation**

Add to `distill_sessions.py`:
```python
def extract_text(content):
  if isinstance(content, str):
    return content.strip()
  parts = []
  for b in content or []:
    if isinstance(b, dict) and b.get('type') == 'text':
      parts.append(b.get('text', ''))
  return '\n'.join(p for p in parts if p).strip()


def tool_names(content):
  if not isinstance(content, list):
    return []
  return [b.get('name', '?') for b in content
          if isinstance(b, dict) and b.get('type') == 'tool_use']


def tool_trace(names):
  if not names:
    return ''
  order = []
  counts = {}
  for n in names:
    if n not in counts:
      order.append(n)
    counts[n] = counts.get(n, 0) + 1
  inner = ', '.join(f'{n} ×{counts[n]}' for n in order)
  return f'[tools: {inner}]'
```

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q
```
Expected: PASS.

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/distill_sessions.py scripts/test_distill_sessions.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(distill): block rendering + tool-trace elision' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 4: Thread reconstruction — main chain, sidechains, compaction summaries

Spec §16.4 "Thread reconstruction" + "Compaction summaries". From a session's records, select the narrative turns in order: drop non-narrative record types and `isMeta` records, drop `isSidechain` records unless `--include-sidechains`, keep `isCompactSummary` records (marked), and drop records of either role that are pure tool-result plumbing (no text and no tool calls). Order by timestamp (the linear main chain; Appendix A notes parent-pointer refinement).

**Files:**
- Modify: `~/research-wiki/scripts/distill_sessions.py`
- Modify: `~/research-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Consumes: `extract_text`, `tool_names` (Task 3).
- Produces: `Turn` = dict `{n, role, text, tools, compaction}`; `reconstruct(records, include_sidechains) -> list[Turn]` (turns numbered from 1, in order).

- [x] **Step 1: Write the failing tests**

Append to `test_distill_sessions.py`:
```python
def _rec(uuid, parent, role, content, **extra):
  r = {'type': role, 'uuid': uuid, 'parentUuid': parent,
       'timestamp': extra.pop('ts', '2026-05-14T10:00:00.000Z'),
       'isSidechain': extra.pop('sidechain', False),
       'message': {'role': role, 'content': content}}
  r.update(extra)
  return r


def test_reconstruct_drops_sidechains_and_tool_plumbing():
  records = [
    _rec('a', None, 'user', 'Question one', ts='2026-05-14T10:00:00Z'),
    _rec('b', 'a', 'assistant',
         [{'type': 'text', 'text': 'Answer'},
          {'type': 'tool_use', 'name': 'bash', 'id': 't1'}],
         ts='2026-05-14T10:00:01Z'),
    _rec('c', 'b', 'user',
         [{'type': 'tool_result', 'tool_use_id': 't1', 'content': 'out'}],
         ts='2026-05-14T10:00:02Z'),  # tool plumbing -> dropped
    _rec('s', 'b', 'assistant', [{'type': 'text', 'text': 'side'}],
         ts='2026-05-14T10:00:03Z', sidechain=True),  # dropped
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert [t['role'] for t in turns] == ['user', 'assistant']
  assert turns[0]['n'] == 1 and turns[1]['n'] == 2
  assert turns[1]['tools'] == '[tools: bash ×1]'


def test_reconstruct_keeps_compaction_summary():
  records = [
    _rec('a', None, 'user', 'compacted context', isCompactSummary=True),
    _rec('b', 'a', 'user', 'real question', ts='2026-05-14T10:01:00Z'),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert turns[0]['compaction'] is True
  assert turns[1]['compaction'] is False


def test_reconstruct_include_sidechains_flag():
  records = [
    _rec('a', None, 'user', 'q'),
    _rec('s', 'a', 'assistant', [{'type': 'text', 'text': 'side'}],
         sidechain=True),
  ]
  assert len(ds.reconstruct(records, include_sidechains=False)) == 1
  assert len(ds.reconstruct(records, include_sidechains=True)) == 2
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q -k reconstruct
```
Expected: FAIL.

- [x] **Step 3: Write the implementation**

Add to `distill_sessions.py`:
```python
def reconstruct(records, include_sidechains):
  '''Ordered narrative turns. See Appendix A for the record schema.'''
  narrative = []
  for r in records:
    if r.get('type') not in ('user', 'assistant'):
      continue
    if r.get('isMeta'):
      continue
    if r.get('isSidechain') and not include_sidechains:
      continue
    content = (r.get('message') or {}).get('content')
    text = extract_text(content)
    names = tool_names(content)
    compaction = bool(r.get('isCompactSummary'))
    # drop pure tool-result plumbing: a turn with no text and no tool calls
    if not text and not names and not compaction:
      continue
    narrative.append({
      'role': r.get('type'),
      'text': text,
      'tools': tool_trace(names),
      'compaction': compaction,
      'ts': r.get('timestamp', ''),
    })
  narrative.sort(key=lambda t: t['ts'])
  for i, t in enumerate(narrative, start=1):
    t['n'] = i
  return narrative
```

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q
```
Expected: PASS.

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/distill_sessions.py scripts/test_distill_sessions.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(distill): thread reconstruction (sidechains, compaction)' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 5: Digest writer — frontmatter, numbered turns, slug, idempotence

Spec §16.4 digest format. Given a reconstructed session, write `raw/sessions/YYYY-MM-DD-<slug>-<sess8>.md` with the frontmatter header and numbered-turn body; redact turn text and total the counts into the header. Idempotent: skip if a digest for that `sess8` already exists.

**Files:**
- Modify: `~/research-wiki/scripts/distill_sessions.py`
- Modify: `~/research-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Consumes: `redact` (Task 2), `reconstruct` output (Task 4).
- Produces:
  - `slugify(text: str) -> str` — lowercase, alnum→hyphen, collapse/trim, max 6 words.
  - `Session` = dict `{session_id, source, project, turns}` (turns from `reconstruct`).
  - `write_digest(session: dict, out: Path) -> Path | None` — writes the digest, returns its path, or `None` if skipped (idempotence) or the session has zero turns... (still writes: zero captures is legitimate — write the empty-bodied digest so it is searchable, §16.5).

- [x] **Step 1: Write the failing tests**

Append to `test_distill_sessions.py`:
```python
def _session():
  return {
    'session_id': 'a3f2c9d1e5b6', 'source': 'claude-code', 'project': 'alt-nfp',
    'turns': [
      {'n': 1, 'role': 'user', 'text': 'Use key sk-' + 'A' * 24,
       'tools': '', 'compaction': False, 'ts': '2026-05-14T10:00:00Z'},
      {'n': 2, 'role': 'assistant', 'text': 'Done',
       'tools': '[tools: bash ×2]', 'compaction': False,
       'ts': '2026-05-15T09:00:00Z'},
    ],
  }


def test_write_digest_filename_and_header(tmp_path):
  out = tmp_path / 'sessions'
  p = ds.write_digest(_session(), out)
  assert p is not None
  assert p.name.endswith('-a3f2c9d1.md')          # sess8 suffix
  assert p.name.startswith('2026-05-14-')          # first turn date
  text = p.read_text()
  assert 'session: a3f2c9d1e5b6' in text
  assert 'source: claude-code' in text
  assert 'project: alt-nfp' in text
  assert 'dates: 2026-05-14/2026-05-15' in text
  assert 'turns: 2' in text
  assert 'redactions: 1' in text                   # the sk- key was redacted
  assert 'sk-' + 'A' * 24 not in text              # ... and does not survive
  assert '**[01] user:**' in text
  assert '**[02] assistant:**' in text
  assert '[tools: bash ×2]' in text


def test_write_digest_idempotent(tmp_path):
  out = tmp_path / 'sessions'
  first = ds.write_digest(_session(), out)
  second = ds.write_digest(_session(), out)   # same session id
  assert first is not None and second is None  # skipped on re-run
  assert len(list(out.glob('*.md'))) == 1
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q -k write_digest
```
Expected: FAIL.

- [x] **Step 3: Write the implementation**

Replace the placeholder `write_digest` in `distill_sessions.py` and add helpers:
```python
def slugify(text, max_words=6):
  words = re.findall(r'[a-z0-9]+', (text or '').lower())
  slug = '-'.join(words[:max_words])
  return slug or 'session'


def _turn_date(ts):
  return ts[:10] if ts and len(ts) >= 10 else '0000-00-00'


def write_digest(session, out):
  out.mkdir(parents=True, exist_ok=True)
  sess = session['session_id']
  sess8 = sess[:8]
  # idempotence: any existing digest for this session id
  if any(p.name.endswith(f'-{sess8}.md') for p in out.glob('*.md')):
    return None

  turns = session['turns']
  dates = sorted(_turn_date(t['ts']) for t in turns) or ['0000-00-00']
  first_date, last_date = dates[0], dates[-1]
  slug_src = next((t['text'] for t in turns if t['role'] == 'user' and t['text']), '')
  # redact BEFORE slugifying so a secret in the opening turn never reaches the
  # filename (the body is redacted too, below).
  slug = slugify(redact(slug_src)[0])

  total_redactions = 0
  body_lines = []
  for t in turns:
    red_text, counts = redact(t['text'])
    total_redactions += sum(counts.values())
    marker = ' [compaction summary]' if t['compaction'] else ''
    trace = f' {t["tools"]}' if t['tools'] else ''
    body_lines.append(f'**[{t["n"]:02d}] {t["role"]}:**{marker} {red_text}{trace}'.rstrip())

  fm = [
    '---',
    f'session: {sess}',
    f'source: {session["source"]}',
  ]
  if session.get('project'):
    fm.append(f'project: {session["project"]}')
  fm += [
    f'dates: {first_date}/{last_date}',
    f'turns: {len(turns)}',
    f'redactions: {total_redactions}',
    '---',
    '',
  ]
  path = out / f'{first_date}-{slug}-{sess8}.md'
  path.write_text('\n'.join(fm) + '\n'.join(body_lines) + '\n')
  return path
```

> Deviation: `slugify` returns `(slug or 'session')[:60]` — the plan's version caps word
> count but not character length. An uncapped slug (e.g. a 240-char redaction-surviving
> token, or six ordinary long words) produced filenames over the OS limit, raising an
> uncaught `OSError` that aborted the whole batch — directly reachable when the distiller
> is run over real transcript history. Gate-resolved (human), authorized fix F1.

> Deviation: `write_digest` computes `first_date`/`last_date` from **sentinel-filtered**
> dates (`'0000-00-00'` excluded before sorting, falling back to the sentinel only when
> every date is missing) rather than the plan's plain `sorted(...) or ['0000-00-00']`.
> The plan's version lets the `'0000-00-00'` sentinel from a turn with no timestamp sort
> first and misdate the filename and header even when other turns have real dates.
> Gate-resolved (human), authorized fix F2.

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q
```
Expected: PASS.

- [x] **Step 5: Commit**

```bash
cd ~/research-wiki && git add scripts/distill_sessions.py scripts/test_distill_sessions.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(distill): digest writer with frontmatter + idempotence' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 6: `claude-code` adapter — read JSONL, filter, produce sessions

Spec §16.2.3, §16.4. Wire the core into the `claude-code` source: SRC is a projects directory (or a single `.jsonl`); each `.jsonl` is one session (Appendix A). Apply `--project` (project-dir substring) and `--since` (session date) filters; report unparseable files on stderr without aborting.

**Files:**
- Modify: `~/research-wiki/scripts/distill_sessions.py`
- Modify: `~/research-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Consumes: `reconstruct` (Task 4), `write_digest` (Task 5).
- Produces: `iter_claude_code(src, args, failures) -> list[dict]` (Session dicts). Replaces the Task 1 placeholder. `_read_jsonl(path) -> list[dict]` raising on malformed lines (caller records the failure).

- [x] **Step 1: Write the failing tests**

Append to `test_distill_sessions.py`:
```python
def _write_jsonl(path, records):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text('\n'.join(json.dumps(r) for r in records) + '\n')


def test_claude_code_end_to_end(tmp_path):
  proj = tmp_path / 'projects' / '-Users-lowell-Projects-alt-nfp'
  _write_jsonl(proj / '11111111-2222-3333-4444-555555555555.jsonl', [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None, 'sessionId': 'S',
     'timestamp': '2026-05-14T10:00:00Z', 'cwd': '/Users/lowell/Projects/alt-nfp',
     'message': {'role': 'user', 'content': 'What sampler?'}},
    {'type': 'assistant', 'uuid': 'b', 'parentUuid': 'a', 'sessionId': 'S',
     'timestamp': '2026-05-14T10:00:01Z',
     'message': {'role': 'assistant',
                 'content': [{'type': 'text', 'text': 'MCLMC.'}]}},
  ])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', str(tmp_path / 'projects'), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1
  body = digests[0].read_text()
  assert '**[01] user:** What sampler?' in body
  assert 'project: alt-nfp' in body


def test_claude_code_project_filter(tmp_path):
  base = tmp_path / 'projects'
  for name, sid in [('-Users-lowell-Projects-alt-nfp', 'aaaa1111-0000-0000-0000-000000000000'),
                    ('-Users-lowell-Projects-bls-stats', 'bbbb2222-0000-0000-0000-000000000000')]:
    _write_jsonl(base / name / f'{sid}.jsonl', [
      {'type': 'user', 'uuid': 'a', 'parentUuid': None, 'timestamp': '2026-05-14T10:00:00Z',
       'cwd': f'/x/{name}', 'message': {'role': 'user', 'content': 'hi'}}])
  out = tmp_path / 'out'
  ds.main(['--source', 'claude-code', '--project', 'alt-nfp', str(base), str(out)])
  assert len(list(out.glob('*.md'))) == 1  # only the alt-nfp session


def test_claude_code_bad_file_is_reported_not_fatal(tmp_path, capsys):
  base = tmp_path / 'projects' / '-p'
  (base).mkdir(parents=True)
  (base / 'aaaa1111-0000-0000-0000-000000000000.jsonl').write_text('{not json\n')
  good = 'cccc3333-0000-0000-0000-000000000000'
  _write_jsonl(base / f'{good}.jsonl', [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None, 'timestamp': '2026-05-14T10:00:00Z',
     'message': {'role': 'user', 'content': 'ok'}}])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', str(tmp_path / 'projects'), str(out)])
  assert rc == 1                                   # a file failed
  assert len(list(out.glob('*.md'))) == 1          # the good one still written
  assert 'parse-failure' in capsys.readouterr().err
```

- [x] **Step 2: Run the tests to verify they fail**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q -k claude_code
```
Expected: FAIL (adapter is a placeholder returning `[]`).

- [x] **Step 3: Write the implementation**

Replace `iter_claude_code` in `distill_sessions.py`:
```python
def _read_jsonl(path):
  records = []
  for line in path.read_text().split('\n'):
    line = line.strip()
    if not line:
      continue
    records.append(json.loads(line))  # JSONDecodeError bubbles to caller
  return records


def _project_name(records, proj_dir):
  '''Prefer the authoritative cwd basename — the encoded dir name mangles
  hyphenated projects (-Users-lowell-Projects-alt-nfp splits to "nfp", not
  "alt-nfp"). Fall back to the dir's last segment only if no record has cwd.'''
  cwd = next((r.get('cwd') for r in records if r.get('cwd')), None)
  if cwd:
    return Path(cwd).name
  return proj_dir.rstrip('-').split('-')[-1] if proj_dir else None


def iter_claude_code(src, args, failures):
  sessions = []
  files = [src] if src.suffix == '.jsonl' else sorted(src.rglob('*.jsonl'))
  for path in files:
    proj_dir = path.parent.name
    if args.project and args.project not in proj_dir:
      continue
    try:
      records = _read_jsonl(path)
    except (json.JSONDecodeError, OSError):
      failures.append(str(path))
      continue
    turns = reconstruct(records, args.include_sidechains)
    if not turns:
      continue
    first_date = min((t['ts'][:10] for t in turns), default='0000-00-00')
    if args.since and first_date < args.since:
      continue
    sessions.append({
      'session_id': path.stem,
      'source': 'claude-code',
      'project': _project_name(records, proj_dir),
      'turns': turns,
    })
  return sessions
```

> Deviation: `iter_claude_code`'s `--since` filter uses a sentinel-filtered date floor
> (`'0000-00-00'` entries excluded before taking `min()`, falling back to the sentinel only
> when every turn is undated) instead of the plan's plain
> `min((t['ts'][:10] for t in turns), default=...)`. The plan's version lets one undated
> turn produce `first_date == '0000-00-00'`, which sorts before any real `--since` cutoff
> and silently drops an in-window session from the run. Controller-authorized (implements
> the plan's own defensive-reading constraint; not a new design decision).

> Deviation: the caller now catches `except (ValueError, OSError)` around `_read_jsonl`
> instead of the plan's `except (json.JSONDecodeError, OSError)`. `UnicodeDecodeError` is a
> `ValueError` (not an `OSError`), so a non-UTF-8 `.jsonl` escaped the plan's narrower catch,
> aborted the whole run with an uncaught traceback, and lost every other session in the
> batch — directly violating this plan's own Global Constraint that "a file that fails to
> parse is reported on stderr without aborting the run." Controller-fixed without
> escalating (implements the plan's stated contract; `ValueError` subsumes
> `json.JSONDecodeError`).

- [x] **Step 4: Run the tests to verify they pass**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q
```
Expected: PASS.

- [x] **Step 5: Smoke-test against real transcripts (read-only; scoped, non-destructive)**

Run (writes only to a throwaway temp dir, never `raw/sessions/`):
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 python distill_sessions.py \
  --source claude-code --project agent-skills --since 2026-07-01 \
  ~/.claude/projects /tmp/distill-smoke ; echo "exit=$?" && \
ls /tmp/distill-smoke | head && \
echo "--- redaction check: no raw secrets leaked ---" && \
! grep -rIlE 'sk-[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{30}|AKIA[0-9A-Z]{16}' /tmp/distill-smoke && \
echo 'clean: no secret-shaped strings in digests'
```
Expected: `exit=0` (or `exit=1` if some old file is unparseable — acceptable, good files still written), at least one digest listed, and `clean: no secret-shaped strings in digests`. Then clear the smoke dir: `rm -rf /tmp/distill-smoke`.

> Deviation: run from the session scratchpad
> (`/private/tmp/claude-501/.../scratchpad`) rather than `/tmp/distill-smoke`, and via
> `uv run --python 3.13 python distill_sessions.py` rather than a bare `python3` invocation
> — matching this repo's environment conventions (no bare `/tmp`, no unpinned interpreter).
> Same command shape and expected output; only the working directory and interpreter
> invocation differ.

- [x] **Step 6: Commit**

```bash
cd ~/research-wiki && git add scripts/distill_sessions.py scripts/test_distill_sessions.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(distill): claude-code adapter (filters, robust parse)' && \
git log --oneline -1
```
Expected: one commit line printed.

---

### Task 7: `claude-ai` adapter — parse `conversations.json` (provisional)

Spec §16.2.2, §16.4. The claude.ai export is a single `conversations.json` (a list of conversations, each with an ordered message list). The exact shape is not available at build time, so this adapter is written against the documented shape and **flagged provisional**: it normalizes each conversation into the same `Session` dict the core consumes, and it is verified against a synthetic fixture. When a real export lands, confirm the field names in one conversation and adjust the normalizer only.

**Files:**
- Modify: `~/research-wiki/scripts/distill_sessions.py`
- Modify: `~/research-wiki/scripts/test_distill_sessions.py`

**Interfaces:**
- Consumes: `redact`/`reconstruct` indirectly via a normalizer that emits the same `turns` shape.
- Produces: `iter_claude_ai(src, args, failures) -> list[dict]`; `_claude_ai_turns(conversation) -> list[Turn]`. Replaces the Task 1 placeholder.

- [x] **Step 1: Write the failing test (synthetic fixture matching the documented shape)**

Append to `test_distill_sessions.py`:
```python
def test_claude_ai_adapter(tmp_path):
  conv = [{
    'uuid': 'ffffdddd-0000-0000-0000-000000000000',
    'name': 'Sampler question',
    'created_at': '2026-04-02T12:00:00Z',
    'updated_at': '2026-04-02T12:30:00Z',
    'chat_messages': [
      {'sender': 'human', 'created_at': '2026-04-02T12:00:00Z',
       'text': 'Which sampler for hierarchical models?'},
      {'sender': 'assistant', 'created_at': '2026-04-02T12:00:10Z',
       'text': 'NUTS or MCLMC.'},
    ],
  }]
  src = tmp_path / 'conversations.json'
  src.write_text(json.dumps(conv))
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-ai', str(src), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1
  body = digests[0].read_text()
  assert 'source: claude-ai' in body
  assert 'project:' not in body            # claude-ai has no project
  assert '**[01] user:** Which sampler for hierarchical models?' in body
```

- [x] **Step 2: Run the test to verify it fails**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q -k claude_ai
```
Expected: FAIL (placeholder returns `[]`).

- [x] **Step 3: Write the implementation**

Replace `iter_claude_ai` in `distill_sessions.py`:
```python
def _claude_ai_turns(conversation):
  '''Normalize a claude.ai conversation into core Turn dicts. PROVISIONAL: keyed
  to the documented export shape (chat_messages[].sender/text/created_at); verify
  against a real conversations.json when one is available and adjust here only.'''
  msgs = conversation.get('chat_messages') or conversation.get('messages') or []
  turns = []
  for m in msgs:
    sender = m.get('sender') or m.get('role')
    role = 'user' if sender in ('human', 'user') else 'assistant'
    text = (m.get('text') or '').strip()
    if not text:
      continue
    turns.append({'role': role, 'text': text, 'tools': '',
                  'compaction': False, 'ts': m.get('created_at', '')})
  turns.sort(key=lambda t: t['ts'])
  for i, t in enumerate(turns, start=1):
    t['n'] = i
  return turns


def iter_claude_ai(src, args, failures):
  try:
    data = json.loads(src.read_text())
  except (json.JSONDecodeError, OSError):
    failures.append(str(src))
    return []
  sessions = []
  for conv in data:
    turns = _claude_ai_turns(conv)
    if not turns:
      continue
    first_date = min((t['ts'][:10] for t in turns), default='0000-00-00')
    if args.since and first_date < args.since:
      continue
    sessions.append({
      'session_id': conv.get('uuid', '') or slugify(conv.get('name', '')),
      'source': 'claude-ai',
      'project': None,
      'turns': turns,
    })
  return sessions
```

> Deviation: `_claude_ai_turns` was de-provisionalized against the real 2026-07-23 export
> instead of shipping on the documented-but-unverified shape. It keys text extraction on
> `isinstance(content, list) and content -> extract_text(content)`, falling back to the flat
> `text` field only when `content` is absent — never `extract_text(content) or flat_text`.
> Measured on the real export: 1070/2236 messages carry both a flat `text` and a
> content-block text, and in 521 of those the flat field is the assistant's **thinking**
> prose, not the reply (e.g. flat "The user is asking about..." vs. block "This is a great
> analytical framework..."). An `or`-fallback would leak thinking into digests for the 16
> messages whose content-block text is present but empty. Gate-resolved pre-flight (human):
> pin to the real shape, keep the plan's fixture green, add one new real-shape test.

> Deviation: `iter_claude_ai` received the same three robustness fixes as its
> `iter_claude_code` sibling (Task 6 deviations): `except (ValueError, OSError)` around the
> JSON load (not `json.JSONDecodeError, OSError` — `UnicodeDecodeError` is a `ValueError`);
> the sentinel-filtered `--since` date floor (not a plain `min()` over possibly-empty
> timestamps); and `m.get('created_at') or ''` in `_claude_ai_turns` (None-safe for the
> `turns.sort()`, since `created_at` can be present-but-null). Controller-fixed without
> escalating — character-identical mirrors of the already-adjudicated Task 6 fixes, applying
> an approved fix to a second instance of the same defect class, not a new design call.

- [x] **Step 4: Run the test to verify it passes**

Run:
```bash
cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest test_distill_sessions.py -q
```
Expected: PASS (full suite green).

- [x] **Step 5: Cross-check the redaction/lint backstop coupling**

Confirm every class this distiller redacts is covered by the linter's backstop (Plan 13 Task 9). Run:
```bash
cd ~/research-wiki/scripts && python3 -c "
import re
import distill_sessions as ds, lint_wiki
dist = {c for c, _ in ds._REDACTORS}
lint = {c for c, _ in lint_wiki.SECRET_PATTERNS}
missing = dist - lint - {'high-entropy'}  # high-entropy is a distiller-only heuristic
print('distiller classes:', sorted(dist))
print('lint backstop classes:', sorted(lint))
print('uncovered (excl. high-entropy):', sorted(missing))
assert not missing, 'lint backstop must cover every specific distiller class'
print('OK: backstop covers the distiller')
"
```
Expected: `OK: backstop covers the distiller`. (If it fails, widen `SECRET_PATTERNS` in `lint_wiki.py` — the lint backstop must be ≥ the redactor for the specific key classes.)

> Deviation: run via `uv run --python 3.13 python -c "..."` from the session scratchpad
> rather than a bare `python3 -c "..."` invocation, matching this repo's environment
> conventions. Same script and expected output.

- [x] **Step 6: Commit**

```bash
cd ~/research-wiki && git add scripts/distill_sessions.py scripts/test_distill_sessions.py && \
git -c user.name='Lowell Mason' -c user.email='mason.lowell@mac.com' \
  commit -q -m 'feat(distill): claude-ai adapter (provisional shape)' && \
git log --oneline -1
```
Expected: one commit line printed.

---

## Appendix A — Claude Code JSONL schema (introspected 2026-07-22)

Ground truth from `~/.claude/projects/*/​*.jsonl`; the format is an implementation detail, so adapters read defensively. **One session per file; the filename stem is the session UUID** (`sess8` = its first 8 chars).

- **Record `type` values:** `user`, `assistant` (narrative); `attachment`, `queue-operation`, `last-prompt`, `pr-link`, `system`, `mode` (non-narrative — skip).
- **Narrative record keys:** `uuid`, `parentUuid` (thread pointer; root = `null`), `sessionId`, `timestamp` (ISO-8601), `cwd`, `gitBranch`, `version`, `userType`, `isSidechain` (bool), `message`.
- **User-only extras:** `isMeta` (bool — skip meta records), `toolUseResult`, `isCompactSummary` (bool — **retain, mark `[compaction summary]`**), `slug`, `sourceToolAssistantUUID`.
- **`message`:** `{role, content}`; `content` is a **str** or a **list of blocks**.
- **Block `type` values:** `text` (`.text`), `thinking` (`.thinking` — dropped from digests), `tool_use` (`.name`, `.input`, `.id` — elided to a tool trace), `tool_result` (`.tool_use_id`, `.content` — plumbing; a user record with only these is dropped).
- **Sidechains:** subagent turns carry `isSidechain: true` — dropped unless `--include-sidechains`.
- **Threading:** this plan orders turns by `timestamp` (correct for linear sessions). A parent-pointer walk (`uuid`→`parentUuid`) is the refinement for sessions with edited/retried branches; add it only if a real session shows out-of-order timestamps.
- **Project:** the encoded-cwd directory name (e.g. `-Users-lowell-Projects-alt-nfp`); `--project` matches a substring of it.

## Self-Review

**1. Spec coverage (§16.4):** usage/flags → Task 1; thread reconstruction (parent/sidechain) → Task 4; noise removal (tool elision, file dumps never pass) → Task 3; compaction summaries retained+marked → Task 4; redaction always-on with header counts → Tasks 2 & 5; idempotence via sess8 in filename → Task 5; digest format (frontmatter + numbered turns) → Task 5; two adapters → Tasks 6 (claude-code, real schema) & 7 (claude-ai, provisional). §16.2 corpora → adapters. §16.3 epistemic rules are enforced at *ingest/lint* (Plan 13), not here; this plan only guarantees redaction (§16.3.3) and the session-dated header (§16.3.2).

**2. Placeholder scan:** no "TBD"/"handle edge cases"/"similar to Task N"; every code step is complete; the one deliberately provisional piece (claude-ai field names) is explicitly labeled with the verify-on-real-export instruction, not left blank.

**3. Type consistency:** `redact` returns `(text, counts)` everywhere; a `Turn` is `{n, role, text, tools, compaction, ts}` produced by `reconstruct` (Task 4) and both `_claude_ai_turns` (Task 7); a `Session` is `{session_id, source, project, turns}` consumed by `write_digest` (Task 5); `iter_claude_code`/`iter_claude_ai` both return `list[Session]` and append to `failures`. `main` (Task 1) wires them unchanged.

**4. Cross-plan coupling:** Task 7 Step 5 asserts the lint backstop (Plan 13 `SECRET_PATTERNS`) covers every specific redactor class — the one hard dependency between the two plans, checked mechanically.

---

## Post-execution

Executed via **subagent-driven-development**. All 7 planned tasks completed with zero
Critical/Important findings surviving per-task review (one fix loop each on Tasks 5, 6, 7 —
all controller-adjudicated and folded into the deviation notes above). Corpus figures below
were measured against the real `~/.claude/projects` transcript history and a 40 MB
`conversations.json` claude.ai export.

**Task 8 (post-final-review fix set, not in the original plan).** The final whole-branch
review (opus) found the 7-task output was not yet fit for purpose: 1 Critical + 6 Important,
covering `--include-sidechains` silently discarding the large majority of its output, tool
traces that could never aggregate past ×1, a redaction header whose counts were dominated by
false positives, and three defensive-reading gaps. The human partner authorized a full fix
pass; its brief is `.sdd/task-8-brief.md` and its five items are:

1. Sidechain transcripts are folded into their **parent session** (not enumerated as
   standalone sessions keyed on `agent-<hex>`), fixing both the idempotence collision and the
   `--project` mismatch.
2. `reconstruct` merges consecutive same-role records sharing a `requestId` into one turn
   before numbering, so `tool_trace` can finally aggregate across a whole tool-call group
   (`[tools: bash ×N, str_replace ×M]`) instead of being permanently stuck at ×1.
3. `high-entropy`'s character class dropped `/`, eliminating file-path false positives while
   the sole-redactor coupling to `sk-proj-`/`github_pat_`/base64 blobs is preserved and
   commented in place.
4. Non-dict JSONL records/conversations and non-list `chat_messages` are now guarded with
   `isinstance` checks instead of aborting the run with an uncaught `AttributeError`.
5. A nonexistent `SRC` path is now recorded as a parse failure (exit 1) instead of silently
   exiting 0 having written nothing; and idempotence rewrites a digest when the session has
   grown (turn count increased) rather than freezing it forever — this is the behavior change
   the spec §16.4 Idempotence bullet was amended to describe (see Work item A of this
   completion).

   **Measured improvement (real corpus, same-hour before/after):** content-free tool-only
   stub turns fell from 58.7% to 27.2% of all turns (8073/13753 → 1394/5124); the redaction
   count fell from 558 (100% file-path false positives) to 16 (all genuine); multi-tool traces
   went from 0 to 147 instances (multiplicity now up to ×33); `--include-sidechains` went from
   46 digests with 16 orphan `agent-…` digests to 30 digests with 0 orphans.

   A fix pass then closed a regression Task 8 itself introduced (SRC pointed at a single
   project directory yielded 0 digests because the new enumeration rule assumed SRC was
   always the projects root — fixed to a depth-independent "no `subagents` path component"
   rule) plus one pre-existing ingest blocker unrelated to this plan's own code — see item (b)
   below.

**Corpus structure (correction).** The distiller's own pre-flight brief, and an earlier
progress-ledger note, stated the `claude-code` corpus as "874 main session files." That figure
was wrong: it counted nested workflow-subagent transcripts as main sessions because the
original filter excluded only files whose immediate parent directory was literally
`subagents`. The corpus actually decomposes as:

- **30** true main sessions (`<project-dir>/<uuid>.jsonl`, depth 2)
- **424** direct sidechain transcripts (`<project-dir>/<uuid>/subagents/agent-*.jsonl`, depth 4)
- **844** nested workflow-subagent transcripts
  (`<project-dir>/<uuid>/subagents/workflows/wf_*/agent-*.jsonl`, depth 6)

Task 8's depth-independent enumeration rule ("no `subagents` path component") correctly
excludes all 1268 sidechain/workflow files regardless of nesting depth from the main-session
sweep, and folds both the direct and nested groups into their parent session's digest under
`--include-sidechains`.

**(b) Authorized change to a retired plan's deliverable.** Task 8's real-corpus run surfaced a
pre-existing defect in `~/research-wiki/scripts/lint_wiki.py` (Plan 13's deliverable, already
retired): the `openai-key` backstop pattern (widened by Plan 13's own post-review G2 fix to
include `_`/`-`) matched `sk-` **mid-word** in ordinary prose — e.g.
`ta[sk-reviewer-agent-and-deferred-command]`, `ri[sk-adjusted-return-modelling]` — scoring 90
false positives across the first real batch of produced digests and would have blocked the
very first ingest into `raw/sessions/` on a corpus containing zero actual secrets. The human
partner authorized anchoring the pattern with a `(?<![A-Za-z0-9])` lookbehind; verified this
kills every sampled false positive while still catching `sk-proj-<60 chars>` and legacy
`sk-AAAA...` keys. `scripts/test_lint_wiki.py` gained a regression test for the fix
(`test_lint_wiki.py` 30 → 31); this lands in the same fix-pass commit as the Task 8 regression
close, so it is included in the final counts below.

**(c) Final state.** `~/research-wiki` HEAD = `22fbe6e` (Tasks 1–7 at `70e690c..68dc323`, Task
8 + its fix pass at `68dc323..649cd87..22fbe6e`). Full suite: **86 tests passing** — 31
`test_lint_wiki.py` (30 + the openai-key anchor regression test) + 55 `test_distill_sessions.py`
(`cd ~/research-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q`).
Backstop cross-check still passes (`lint_wiki.SECRET_PATTERNS` covers every distiller class
except the deliberately distiller-only `high-entropy` heuristic). One residual, deliberately
deferred rather than fixed: 2 `assignment`-class lint false positives in a single digest,
**only** under `--include-sidechains`, on pre-existing session text that literally discusses
that pattern's missing `\b` word boundary (meta-recursion) — confirmed absent from plain
root/single-project runs, so a normal ingest of this corpus lints fully clean. See
`specs/deferred_items.md` § `14-llm-wiki-distiller` for this and the rest of the deferred
list.

**Spec retirement.** `specs/llm-wiki-spec.md` was kept live through Plan 13's retirement
because this plan (14) still implemented it. With Task 8 and its fix pass complete, both
plans implementing the spec are now done, so this completion retires the spec alongside this
plan — `specs/llm-wiki-spec.md` → `specs/completed/llm-wiki-spec.md` (marked complete at top),
amending §16.4's Idempotence bullet first (Task 8 item 5) to describe the shipped
grows-then-rewrites behavior rather than the plan's original always-skip rule.
