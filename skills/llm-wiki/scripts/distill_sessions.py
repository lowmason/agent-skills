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


def reconstruct(records, include_sidechains):
  '''Ordered narrative turns. See Appendix A for the record schema.'''
  narrative = []
  for r in records:
    if not isinstance(r, dict):  # valid JSON, not an object: skip like any
      continue                   # unknown record type -- the format is not an API
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
      'names': names,
      'compaction': compaction,
      'ts': r.get('timestamp', ''),
      'req': r.get('requestId') or None,
    })
  narrative.sort(key=lambda t: t['ts'])
  return _number(_merge_requests(narrative))


def _merge_requests(narrative):
  '''Claude Code emits one assistant record per tool_use block, so a single
  request arrives as several records sharing one top-level requestId. Merge
  consecutive same-role records of the same request into one turn: without
  this, every trace renders as [tools: X ×1] and 60% of a digest is
  content-free stubs. Only adjacent records (post-sort) merge, so an
  interleaved turn is never reordered; a record with no requestId (every user
  record, and any assistant record lacking one) never joins a group.'''
  merged = []
  for t in narrative:
    prev = merged[-1] if merged else None
    if (prev is not None and t['req'] is not None
        and prev['req'] == t['req'] and prev['role'] == t['role']):
      if t['text']:
        prev['text'] = f'{prev["text"]}\n{t["text"]}' if prev['text'] else t['text']
      prev['names'].extend(t['names'])
      prev['compaction'] = prev['compaction'] or t['compaction']
      continue  # keeps the group's first ts
    merged.append({**t, 'names': list(t['names'])})
  return merged


def _number(merged):
  '''Render the fixed Turn shape: {n, role, text, tools, compaction, ts}.
  Numbering runs after merging, so turn numbers count merged turns.'''
  return [{'n': i, 'role': t['role'], 'text': t['text'],
           'tools': tool_trace(t['names']), 'compaction': t['compaction'],
           'ts': t['ts']}
          for i, t in enumerate(merged, start=1)]


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
  cwd = next((r.get('cwd') for r in records
              if isinstance(r, dict) and r.get('cwd')), None)
  if cwd:
    return Path(cwd).name
  return proj_dir.rstrip('-').split('-')[-1] if proj_dir else None


def _sidechain_records(path, failures):
  '''Subagent transcripts for a main session live at
  <project-dir>/<session-stem>/subagents/agent-*.jsonl, and some nest one
  level deeper still, at .../subagents/workflows/wf_*/agent-*.jsonl (measured:
  424 direct, 844 nested in the real corpus). All of them are part of that
  session, not sessions of their own: read as standalone files their stem
  (agent-<hex>) collapses to ~16 distinct sess8 values, so the idempotence
  guard silently swallowed 407 of 423 of them, and --project (which matches the
  parent dir name, literally "subagents") excluded every one. A single-level
  glob also missed every nested workflow transcript even with
  --include-sidechains, so this recurses (rglob) under subagents/ rather than
  globbing one level. A missing or unreadable subagents/ dir is normal and
  must never fail the session.'''
  extra = []
  sub = path.parent / path.stem / 'subagents'
  try:
    side_files = sorted(sub.rglob('*.jsonl'))
  except OSError:
    return extra
  for side in side_files:
    try:
      extra.extend(_read_jsonl(side))
    except (ValueError, OSError):
      failures.append(str(side))
  return extra


def iter_claude_code(src, args, failures):
  sessions = []
  if not src.exists():
    failures.append(str(src))  # a typo'd SRC must not exit 0 having done nothing
    return sessions
  if src.suffix == '.jsonl':
    files = [src]
  else:
    # main session files only. Depth-independent: a main session is any
    # .jsonl with no 'subagents' path component, checked against the full
    # relative path (not just the immediate parent) -- 'parent.parent == src'
    # silently assumed SRC was always the projects root, so pointing SRC at a
    # single project directory (SRC = <proj-dir>, one level shallower) matched
    # nothing. This rule is correct whether SRC is the projects root
    # (<proj>/<uuid>.jsonl) or a single project dir (<uuid>.jsonl directly),
    # and excludes sidechains at any nesting depth, including the nested
    # <uuid>/subagents/workflows/wf_*/agent-*.jsonl transcripts.
    files = sorted(p for p in src.rglob('*.jsonl')
                    if 'subagents' not in p.relative_to(src).parts)
  for path in files:
    proj_dir = path.parent.name
    if args.project and args.project not in proj_dir:
      continue
    try:
      records = _read_jsonl(path)
    except (ValueError, OSError):
      failures.append(str(path))
      continue
    if args.include_sidechains:
      records.extend(_sidechain_records(path, failures))
    turns = reconstruct(records, args.include_sidechains)
    if not turns:
      continue
    real = sorted(d for d in (_turn_date(t['ts']) for t in turns)
                  if d != '0000-00-00')
    first_date = real[0] if real else '0000-00-00'
    if args.since and first_date < args.since:
      continue
    sessions.append({
      'session_id': path.stem,
      'source': 'claude-code',
      'project': _project_name(records, proj_dir),
      'turns': turns,
    })
  return sessions


def _claude_ai_turns(conversation):
  '''Normalize a claude.ai conversation into core Turn dicts. Shape verified
  against a real conversations.json export on 2026-07-23 (347 conversations,
  2236 messages; chat_messages[].sender/text/content/created_at). Load-bearing
  fact from that export: an assistant message's flat `text` field frequently
  carries the model's internal thinking prose, not its reply, so when `content`
  is a non-empty list we must extract from it (extract_text drops thinking/
  tool_use/tool_result) rather than ever falling back to the flat text field.'''
  msgs = conversation.get('chat_messages') or conversation.get('messages') or []
  if not isinstance(msgs, list):  # defensive: shape drift must not abort the run
    msgs = []
  turns = []
  for m in msgs:
    if not isinstance(m, dict):
      continue
    sender = m.get('sender') or m.get('role')
    role = 'user' if sender in ('human', 'user') else 'assistant'
    content = m.get('content')
    if isinstance(content, list) and content:
      text = extract_text(content)          # drops thinking (Task 3)
    else:
      text = (m.get('text') or '').strip()  # no content key: documented/fixture shape
    if not text:
      continue
    turns.append({'role': role, 'text': text, 'tools': '',
                  'compaction': False, 'ts': m.get('created_at') or ''})
  turns.sort(key=lambda t: t['ts'])
  for i, t in enumerate(turns, start=1):
    t['n'] = i
  return turns


def iter_claude_ai(src, args, failures):
  try:
    data = json.loads(src.read_text())
  except (ValueError, OSError):
    failures.append(str(src))
    return []
  if not isinstance(data, list):
    failures.append(str(src))  # malformed top-level structure: report, don't abort
    return []
  sessions = []
  for conv in data:
    if not isinstance(conv, dict):
      continue
    turns = _claude_ai_turns(conv)
    if not turns:
      continue
    real = sorted(d for d in (_turn_date(t['ts']) for t in turns)
                  if d != '0000-00-00')
    first_date = real[0] if real else '0000-00-00'
    if args.since and first_date < args.since:
      continue
    sessions.append({
      'session_id': conv.get('uuid', '') or slugify(conv.get('name', '')),
      'source': 'claude-ai',
      'project': None,
      'turns': turns,
    })
  return sessions


def slugify(text, max_words=6):
  words = re.findall(r'[a-z0-9]+', (text or '').lower())
  slug = '-'.join(words[:max_words])
  return (slug or 'session')[:60]


def _turn_date(ts):
  return ts[:10] if ts and len(ts) >= 10 else '0000-00-00'


_TURNS_HEADER_RE = re.compile(r'^turns:\s*(\d+)\s*$', re.M)


def _digest_turns(path):
  '''The turn count recorded in an existing digest's header, or None if it is
  missing/unparseable/unreadable (a hand-edited digest must never crash a run).'''
  try:
    m = _TURNS_HEADER_RE.search(path.read_text())
  except (ValueError, OSError):
    return None
  return int(m.group(1)) if m else None


def write_digest(session, out):
  out.mkdir(parents=True, exist_ok=True)
  sess = session['session_id']
  sess8 = sess[:8]
  turns = session['turns']
  # Idempotence (§16.4, as amended): an existing digest for this session id is
  # skipped -- UNLESS the session has grown. Real sessions are appended to under
  # one id for up to 60 hours, and the literal skip rule would freeze a digest
  # written at hour 4 forever, permanently recording a truncated session.
  existing = [p for p in sorted(out.glob('*.md'))
              if p.name.endswith(f'-{sess8}.md')]
  if existing:
    previous = _digest_turns(existing[0])
    if previous is None or len(turns) <= previous:
      return None

  real = sorted(d for d in (_turn_date(t['ts']) for t in turns)
                if d != '0000-00-00')
  if real:
    first_date, last_date = real[0], real[-1]
  else:
    first_date, last_date = '0000-00-00', '0000-00-00'
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
  # growth can change the date/slug parts of the name, so drop any stale digest
  # for this session: one session must never leave two digests behind.
  for stale in existing:
    if stale != path:
      stale.unlink(missing_ok=True)
  return path


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
  # `/` is deliberately OUT of this class: with it, long file paths cleared the
  # 40-char bar and every one of the 558 redactions in the real corpus was a
  # destroyed locator, not a secret.
  # DO NOT narrow this further. high-entropy is the SOLE redactor for
  # `sk-proj-…`, `github_pat_…` and generic base64 here: openai-key's
  # hyphen-free `sk-[A-Za-z0-9]{20,}` cannot match across the hyphen in
  # `sk-proj-`, and this module has no github-pat class (lint_wiki.py's
  # backstop has both). Removing or tightening it opens a real leak.
  ('high-entropy', re.compile(r'[A-Za-z0-9+=_-]{40,}')),
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


if __name__ == '__main__':
  sys.exit(main())
