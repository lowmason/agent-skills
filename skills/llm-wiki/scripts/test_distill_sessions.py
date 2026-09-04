'''Tests for distill_sessions.py. Stdlib + pytest only; synthetic fixtures.'''
import json
from pathlib import Path

import pytest
import distill_sessions as ds


def test_main_unknown_source_exits_nonzero(capsys, tmp_path):
  with pytest.raises(SystemExit) as exc:
    ds.main(['--source', 'nope', str(tmp_path), str(tmp_path / 'out')])
  assert exc.value.code != 0  # argparse rejects the choice


def test_main_empty_src_dir_is_ok(tmp_path):
  src = tmp_path / 'projects'
  src.mkdir()
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', str(src), str(out)])
  assert rc == 0
  assert out.exists()  # OUT_DIR is created even with nothing to write


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


def test_claude_ai_undated_turn_keeps_its_place():
  '''An undated message must not be renumbered to the front. Turn numbers are
  spec §16.4's locator currency for future captures, so a mid-conversation
  message with no created_at has to stay between its neighbours.'''
  conv = {'chat_messages': [
    {'sender': 'human', 'text': 'first', 'created_at': '2026-05-14T10:00:00Z'},
    {'sender': 'assistant', 'text': 'undated middle', 'created_at': ''},
    {'sender': 'human', 'text': 'third', 'created_at': '2026-05-14T10:01:00Z'},
  ]}
  turns = ds._claude_ai_turns(conv)
  assert [t['text'] for t in turns] == ['first', 'undated middle', 'third']
  assert [t['n'] for t in turns] == [1, 2, 3]


def test_reconstruct_undated_record_keeps_its_place():
  '''The same defect on the claude-code path: a record with no timestamp must
  not sort ahead of records that genuinely came first.'''
  records = [
    _rec('a', None, 'user', 'first', ts='2026-05-14T10:00:00Z'),
    _rec('b', 'a', 'assistant', [{'type': 'text', 'text': 'undated middle'}],
         ts=''),
    _rec('c', 'b', 'user', 'third', ts='2026-05-14T10:01:00Z'),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert [t['text'] for t in turns] == ['first', 'undated middle', 'third']
  assert [t['n'] for t in turns] == [1, 2, 3]


def test_leading_undated_turn_stays_first():
  '''Guard on the fix, not on the bug: an undated turn that really was first
  has no dated predecessor to inherit from, so it must stay at position 1.
  This one passes before the fix and must still pass after it.'''
  records = [
    _rec('a', None, 'user', 'undated opener', ts=''),
    _rec('b', 'a', 'assistant', [{'type': 'text', 'text': 'later'}],
         ts='2026-05-14T10:00:00Z'),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert [t['text'] for t in turns] == ['undated opener', 'later']


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


def test_write_digest_caps_long_slug_f1(tmp_path):
  '''F1: a single-word opening turn long enough to blow the 255-char filename
  limit must not raise OSError; the slug is capped, not just the word count.'''
  out = tmp_path / 'sessions'
  session = {
    'session_id': 'deadbeef1234', 'source': 'claude-code', 'project': None,
    'turns': [
      {'n': 1, 'role': 'user', 'text': 'a1b2c3d4' * 30,
       'tools': '', 'compaction': False, 'ts': '2026-05-14T10:00:00Z'},
    ],
  }
  p = ds.write_digest(session, out)
  assert p is not None
  # the real bound the slugify(...)[:60] cap guarantees, not just the OS limit:
  # 10 (date) + 1 + <=60 (slug) + 1 + 8 (sess8) + 3 ('.md') = 83.
  assert len(p.name) <= 83


def test_write_digest_ignores_missing_ts_in_date_range_f2(tmp_path):
  '''F2: a sentinel '0000-00-00' from a missing/empty timestamp must not
  poison the filename date or the dates: range when another turn has a real
  date.'''
  out = tmp_path / 'sessions'
  session = {
    'session_id': 'deadbeef5678', 'source': 'claude-code', 'project': None,
    'turns': [
      {'n': 1, 'role': 'user', 'text': 'plan the wiki',
       'tools': '', 'compaction': False, 'ts': ''},
      {'n': 2, 'role': 'assistant', 'text': 'Done',
       'tools': '', 'compaction': False, 'ts': '2026-05-15T09:00:00Z'},
    ],
  }
  p = ds.write_digest(session, out)
  assert p is not None
  assert p.name.startswith('2026-05-15-')
  text = p.read_text()
  assert 'dates: 2026-05-15/2026-05-15' in text


def test_write_digest_zero_turns_keeps_sentinel_range_f2_guard(tmp_path):
  '''F2 guard: a zero-turn session (no timestamps at all) must still write an
  empty-bodied digest with the honest 0000-00-00/0000-00-00 sentinel range —
  this must not regress when the mixed-date case above is fixed.'''
  out = tmp_path / 'sessions'
  session = {
    'session_id': 'c0ffee123456', 'source': 'claude-code', 'project': None,
    'turns': [],
  }
  p = ds.write_digest(session, out)
  assert p is not None
  text = p.read_text()
  assert 'dates: 0000-00-00/0000-00-00' in text
  assert 'turns: 0' in text
  assert 'redactions: 0' in text
  assert '**[' not in text  # empty body: no turn lines rendered


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


def test_claude_code_since_keeps_session_with_undated_first_turn(tmp_path):
  '''F2: reconstruct yields ts: "" for a record with no timestamp key at all.
  The authorized deviation filters that sentinel out of first_date before
  comparing to --since, so a session whose *first* turn is undated but whose
  other turns fall inside the window must still be kept — and the real date
  (not the sentinel) must drive the filename and dates: header.'''
  base = tmp_path / 'projects' / '-p'
  base.mkdir(parents=True)
  sid = 'ffff6666-0000-0000-0000-000000000000'
  _write_jsonl(base / f'{sid}.jsonl', [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None,
     # no 'timestamp' key -> reconstruct's r.get('timestamp', '') yields ''
     'message': {'role': 'user', 'content': 'undated opener'}},
    {'type': 'assistant', 'uuid': 'b', 'parentUuid': 'a',
     'timestamp': '2026-06-10T09:00:00Z',
     'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': 'real turn'}]}},
  ])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', '--since', '2026-06-01',
               str(tmp_path / 'projects'), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1                          # not dropped by --since
  assert digests[0].name.startswith('2026-06-10-')  # real date, not sentinel
  assert 'dates: 2026-06-10/2026-06-10' in digests[0].read_text()


def test_claude_code_since_still_excludes_fully_prior_session(tmp_path):
  '''F2 complement: a session with only real dates before the cutoff is still
  dropped -- proves the sentinel fix didn't disable --since filtering entirely.'''
  base = tmp_path / 'projects' / '-p'
  base.mkdir(parents=True)
  sid = 'aaaa7777-0000-0000-0000-000000000000'
  _write_jsonl(base / f'{sid}.jsonl', [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None,
     'timestamp': '2026-01-01T09:00:00Z',
     'message': {'role': 'user', 'content': 'old session'}},
  ])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', '--since', '2026-06-01',
               str(tmp_path / 'projects'), str(out)])
  assert rc == 0
  assert len(list(out.glob('*.md'))) == 0


def test_claude_code_project_filter(tmp_path):
  base = tmp_path / 'projects'
  # cwd is the real thing a session records — the encoded dir name under a stub
  # prefix would make _project_name's cwd branch return the encoded name itself.
  for name, sid, cwd in [
      ('-Users-lowell-Projects-alt-nfp', 'aaaa1111-0000-0000-0000-000000000000',
       '/Users/lowell/Projects/alt-nfp'),
      ('-Users-lowell-Projects-bls-stats', 'bbbb2222-0000-0000-0000-000000000000',
       '/Users/lowell/Projects/bls-stats')]:
    _write_jsonl(base / name / f'{sid}.jsonl', [
      {'type': 'user', 'uuid': 'a', 'parentUuid': None, 'timestamp': '2026-05-14T10:00:00Z',
       'cwd': cwd, 'message': {'role': 'user', 'content': 'hi'}}])
  out = tmp_path / 'out'
  ds.main(['--source', 'claude-code', '--project', 'alt-nfp', str(base), str(out)])
  digests = list(out.glob('*.md'))
  assert len(digests) == 1                             # only one session survived
  # ... and it is the right one: a count alone passes under an inverted filter.
  assert 'project: alt-nfp' in digests[0].read_text()


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


def test_claude_code_non_utf8_file_is_reported_not_fatal(tmp_path, capsys):
  '''F: a .jsonl with a truncated multibyte sequence raises UnicodeDecodeError
  from path.read_text() (a ValueError subclass, not an OSError) — the handler
  in iter_claude_code must catch it too, or the whole run aborts and even the
  well-formed sibling session is lost.'''
  base = tmp_path / 'projects' / '-p'
  base.mkdir(parents=True)
  bad = 'dddd4444-0000-0000-0000-000000000000'
  # valid JSON structurally, but the trailing byte is a truncated UTF-8
  # multibyte sequence (b'\xc3' alone is invalid without its continuation byte)
  (base / f'{bad}.jsonl').write_bytes(
    b'{"type":"user","uuid":"a","parentUuid":null,'
    b'"timestamp":"2026-05-14T10:00:00Z","message":'
    b'{"role":"user","content":"caf\xc3"}}\n')
  good = 'eeee5555-0000-0000-0000-000000000000'
  _write_jsonl(base / f'{good}.jsonl', [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None, 'timestamp': '2026-05-14T10:00:00Z',
     'message': {'role': 'user', 'content': 'ok'}}])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', str(tmp_path / 'projects'), str(out)])
  assert rc == 1                                   # the bad file failed
  assert len(list(out.glob('*.md'))) == 1          # the good one still written
  assert 'parse-failure' in capsys.readouterr().err


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


def test_claude_ai_real_export_shape_prefers_content_over_flat_text(tmp_path):
  '''Real export (measured 2026-07-23): an assistant message's flat `text`
  field frequently carries the model's internal thinking prose while the
  actual reply lives in `content` text blocks. When `content` is a non-empty
  list, the normalizer must extract from it (dropping thinking/tool blocks)
  and must NOT fall back to the flat `text` field even if extraction yields
  multiple text blocks around a thinking block. A stub message with
  content: [] and text: '' must yield no turn at all.

  Finding 3 (deviation-locking): m4 below has a non-empty `content` list
  containing ONLY a `thinking` block (no `text` block at all), so
  extract_text(content) == ''. The shipped rule branches on "is `content` a
  non-empty list", not on "did extraction yield truthy text", so m4's turn is
  correctly dropped -- `text` stays '' and the flat `text` field's distinctive
  thinking prose (PURPLEOCTOPUS...) is never consulted. A simplified `or`
  variant -- `text = extract_text(content) or (m.get('text') or '').strip()`
  -- would instead fall back to that flat field and leak the prose into the
  digest, since `extract_text(content)` is falsy here. This is the case that
  distinguishes the two implementations; the other messages in this fixture
  do not.'''
  conv = [{
    'uuid': 'aaaa9999-0000-0000-0000-000000000000',
    'name': 'Real shape test',
    'created_at': '2026-07-20T10:00:00Z',
    'updated_at': '2026-07-20T10:05:00Z',
    'account': {'uuid': 'acct-1'},
    'summary': '',
    'chat_messages': [
      {'uuid': 'm1', 'sender': 'human', 'created_at': '2026-07-20T10:00:00Z',
       'text': 'What sampler works best for hierarchical models?',
       'content': [{'type': 'text',
                    'text': 'What sampler works best for hierarchical models?'}],
       'attachments': [], 'files': [], 'parent_message_uuid': None},
      {'uuid': 'm2', 'sender': 'assistant', 'created_at': '2026-07-20T10:00:10Z',
       'text': 'The user is asking about samplers, let me weigh NUTS versus MCLMC '
               'before replying.',
       'content': [
         {'type': 'text', 'text': 'For hierarchical models, NUTS is the standard default.'},
         {'type': 'thinking',
          'thinking': 'Internal note: check whether they mean centered or '
                      'non-centered parameterization.'},
         {'type': 'text', 'text': 'MCLMC can also work well if tuned carefully.'},
       ],
       'attachments': [], 'files': [], 'parent_message_uuid': 'm1'},
      {'uuid': 'm3', 'sender': 'human', 'created_at': '2026-07-20T10:01:00Z',
       'text': '', 'content': [],
       'attachments': [], 'files': [], 'parent_message_uuid': 'm2'},
      {'uuid': 'm4', 'sender': 'assistant', 'created_at': '2026-07-20T10:02:00Z',
       'text': 'PURPLEOCTOPUS the assistant is quietly re-checking priors before answering.',
       'content': [
         {'type': 'thinking',
          'thinking': 'Scratch: reconsider whether the prior should be weakly informative.'},
       ],
       'attachments': [], 'files': [], 'parent_message_uuid': 'm3'},
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
  assert 'For hierarchical models, NUTS is the standard default.' in body
  assert 'MCLMC can also work well if tuned carefully.' in body
  assert 'Internal note: check whether they mean centered' not in body
  assert 'let me weigh NUTS versus MCLMC before replying' not in body
  assert 'PURPLEOCTOPUS' not in body       # m4's thinking-only content -> flat text unused
  assert 'turns: 2' in body                # m3 (stub) and m4 (thinking-only) both dropped


def test_claude_ai_non_utf8_file_is_reported_not_fatal(tmp_path, capsys):
  '''Finding 1: iter_claude_ai's except clause caught (json.JSONDecodeError,
  OSError), but Path.read_text() decodes strict UTF-8 and raises
  UnicodeDecodeError -- a ValueError subclass, not an OSError -- before
  json.loads ever runs. A conversations.json with a truncated multibyte
  sequence used to escape uncaught, aborting the whole run with zero digests
  and no parse-failure line. Mirrors
  test_claude_code_non_utf8_file_is_reported_not_fatal's fixture shape.'''
  src = tmp_path / 'conversations.json'
  # valid JSON structurally, but the trailing byte is a truncated UTF-8
  # multibyte sequence (b'\xc3' alone is invalid without its continuation byte)
  src.write_bytes(
    b'[{"uuid":"a","name":"x","chat_messages":[{"sender":"human",'
    b'"created_at":"2026-05-14T10:00:00Z","text":"caf\xc3"}]}]')
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-ai', str(src), str(out)])
  assert rc == 1                                   # the bad file failed
  assert len(list(out.glob('*.md'))) == 0          # nothing to write, no crash
  assert 'parse-failure' in capsys.readouterr().err


def test_claude_ai_since_keeps_session_with_undated_first_turn(tmp_path):
  '''Finding 2: iter_claude_ai's first_date used to be
  min(t['ts'][:10] for t in turns), so an undated first message (ts: '', from
  a missing created_at key) yielded first_date = '', below every --since
  value, silently dropping an in-range session. Mirrors
  test_claude_code_since_keeps_session_with_undated_first_turn.'''
  conv = [{
    'uuid': 'ffff8888-0000-0000-0000-000000000000',
    'name': 'undated opener',
    'chat_messages': [
      {'sender': 'human', 'text': 'undated opener'},   # no created_at key at all
      {'sender': 'assistant', 'created_at': '2026-07-20T09:00:00Z', 'text': 'real turn'},
    ],
  }]
  src = tmp_path / 'conversations.json'
  src.write_text(json.dumps(conv))
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-ai', '--since', '2026-01-01', str(src), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1                          # not dropped by --since
  assert digests[0].name.startswith('2026-07-20-')  # real date, not the '' sentinel
  assert 'dates: 2026-07-20/2026-07-20' in digests[0].read_text()


def test_claude_ai_since_still_excludes_fully_prior_conversation(tmp_path):
  '''Finding 2 complement: a conversation with only real dates before the
  cutoff is still dropped -- proves the sentinel fix didn't disable --since
  filtering entirely. Mirrors
  test_claude_code_since_still_excludes_fully_prior_session.'''
  conv = [{
    'uuid': 'bbbb3333-0000-0000-0000-000000000000',
    'name': 'old conversation',
    'chat_messages': [
      {'sender': 'human', 'created_at': '2026-01-01T09:00:00Z', 'text': 'old session'},
    ],
  }]
  src = tmp_path / 'conversations.json'
  src.write_text(json.dumps(conv))
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-ai', '--since', '2026-06-01', str(src), str(out)])
  assert rc == 0
  assert len(list(out.glob('*.md'))) == 0


def test_claude_ai_null_created_at_does_not_crash(tmp_path):
  '''Finding 2 (latent crash): m.get('created_at', '') returns None -- not ''
  -- when the key is present with an explicit JSON null, and
  turns.sort(key=lambda t: t['ts']) then raises TypeError comparing None
  with str. _claude_ai_turns must coerce a null created_at to '' (matching
  _turn_date's None-safety) so the sort never sees a None.'''
  conv = [{
    'uuid': 'aaaa2222-0000-0000-0000-000000000000',
    'name': 'null date',
    'chat_messages': [
      {'sender': 'human', 'created_at': None, 'text': 'no date at all'},
      {'sender': 'assistant', 'created_at': '2026-07-20T09:00:00Z', 'text': 'dated reply'},
    ],
  }]
  src = tmp_path / 'conversations.json'
  src.write_text(json.dumps(conv))
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-ai', str(src), str(out)])  # would raise TypeError pre-fix
  assert rc == 0
  assert len(list(out.glob('*.md'))) == 1


# --- Task 8 item 1: sidechains belong to their parent session ---------------

_PARENT_SID = '95178f12-c89a-42ef-9d03-14dc9bc7f78e'


def _sidechain_fixture(tmp_path, agents, proj_name='-Users-lowell-Projects-bls-stats'):
  '''Real layout (verified against ~/.claude/projects): a main session file
  beside a <stem>/subagents/agent-*.jsonl directory of subagent transcripts.'''
  proj = tmp_path / 'projects' / proj_name
  _write_jsonl(proj / f'{_PARENT_SID}.jsonl', [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None,
     'timestamp': '2026-05-14T10:00:00Z',
     'cwd': '/Users/lowell/Projects/bls-stats',
     'message': {'role': 'user', 'content': 'main question'}},
    {'type': 'assistant', 'uuid': 'b', 'parentUuid': 'a',
     'timestamp': '2026-05-14T10:00:05Z',
     'message': {'role': 'assistant',
                 'content': [{'type': 'text', 'text': 'main answer'}]}},
  ])
  for name, text, ts in agents:
    _write_jsonl(proj / _PARENT_SID / 'subagents' / f'{name}.jsonl', [
      {'type': 'assistant', 'uuid': f'{name}-1', 'parentUuid': None,
       'isSidechain': True, 'timestamp': ts,
       'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': text}]}},
    ])
  return tmp_path / 'projects'


def test_sidechain_files_are_not_standalone_sessions(tmp_path):
  '''Without the flag: exactly one digest (the parent session), no orphan
  agent-… digest, and no sidechain prose.'''
  src = _sidechain_fixture(tmp_path, [
    ('agent-ae022938c3ffa8c41', 'subagent findings one', '2026-05-14T10:00:01Z')])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', str(src), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1
  assert digests[0].name.endswith(f'-{_PARENT_SID[:8]}.md')
  body = digests[0].read_text()
  assert 'subagent findings one' not in body
  assert 'main answer' in body


def test_sidechains_merge_into_parent_session_with_flag(tmp_path):
  '''With the flag: still one digest, keyed on the parent session UUID (not
  agent-…), now carrying the sidechain turns interleaved by timestamp.'''
  src = _sidechain_fixture(tmp_path, [
    ('agent-ae022938c3ffa8c41', 'subagent findings one', '2026-05-14T10:00:01Z')])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', '--include-sidechains',
                str(src), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1
  assert digests[0].name.endswith(f'-{_PARENT_SID[:8]}.md')
  body = digests[0].read_text()
  assert f'session: {_PARENT_SID}' in body
  assert 'agent-' not in body
  assert 'subagent findings one' in body
  assert 'main answer' in body
  assert 'turns: 3' in body


def test_two_sidechain_files_under_one_parent_do_not_collide(tmp_path):
  '''sess8 for agent-<hex> files was the literal "agent-XX", so 407 of 423 real
  digests were swallowed by the idempotence guard. Both files' turns must now
  land in the single parent digest.'''
  src = _sidechain_fixture(tmp_path, [
    ('agent-a7022938c3ffa8c41', 'first subagent line', '2026-05-14T10:00:01Z'),
    ('agent-a7999938c3ffa8c41', 'second subagent line', '2026-05-14T10:00:02Z')])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', '--include-sidechains',
                str(src), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1
  body = digests[0].read_text()
  assert 'first subagent line' in body
  assert 'second subagent line' in body


def test_project_filter_still_matches_with_sidechains(tmp_path):
  '''--project matched path.parent.name, which was the literal "subagents" for
  every sidechain file, so the two documented flags cancelled each other.'''
  src = _sidechain_fixture(tmp_path, [
    ('agent-ae022938c3ffa8c41', 'subagent findings one', '2026-05-14T10:00:01Z')])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', '--include-sidechains',
                '--project', 'bls-stats', str(src), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1
  assert 'subagent findings one' in digests[0].read_text()


def test_unparseable_sidechain_is_reported_but_parent_still_written(tmp_path):
  '''A sidechain file that fails to parse follows the normal failure path:
  recorded, reported, run continues.'''
  src = _sidechain_fixture(tmp_path, [
    ('agent-ae022938c3ffa8c41', 'subagent findings one', '2026-05-14T10:00:01Z')])
  bad = src / '-Users-lowell-Projects-bls-stats' / _PARENT_SID / 'subagents' / 'agent-abad.jsonl'
  bad.write_text('{not json\n')
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', '--include-sidechains',
                str(src), str(out)])
  assert rc == 1
  assert len(list(out.glob('*.md'))) == 1


def test_missing_subagents_dir_is_not_a_failure(tmp_path):
  '''subagents/ is optional -- a session without one must not fail.'''
  src = _sidechain_fixture(tmp_path, [])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', '--include-sidechains',
                str(src), str(out)])
  assert rc == 0
  assert len(list(out.glob('*.md'))) == 1


# --- Task 8 item 2: group consecutive same-request records into one turn ----

def _asst(uuid, text=None, tools=(), req=None, ts='2026-05-14T10:00:00Z'):
  '''One Claude Code assistant record. Real transcripts emit one record per
  tool_use block, all sharing a top-level requestId (verified: 18424 of 18429
  assistant records in ~/.claude/projects carry one; no user record does).'''
  content = []
  if text is not None:
    content.append({'type': 'text', 'text': text})
  for i, name in enumerate(tools):
    content.append({'type': 'tool_use', 'name': name, 'id': f'{uuid}-{i}'})
  r = {'type': 'assistant', 'uuid': uuid, 'parentUuid': None, 'timestamp': ts,
       'message': {'role': 'assistant', 'content': content}}
  if req is not None:
    r['requestId'] = req
  return r


def test_reconstruct_merges_same_request_id_into_one_turn():
  '''Every trace in the real corpus was ×1 because tool_trace only aggregated
  within one record. Merging a request's records is what finally produces the
  spec's own example shape, [tools: bash xN, str_replace xM].'''
  records = [
    _asst('r1', text='Running the checks.', req='req_A', ts='2026-05-14T10:00:00Z'),
    _asst('r2', tools=['bash'], req='req_A', ts='2026-05-14T10:00:01Z'),
    _asst('r3', tools=['bash'], req='req_A', ts='2026-05-14T10:00:02Z'),
    _asst('r4', tools=['str_replace'], req='req_A', ts='2026-05-14T10:00:03Z'),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert len(turns) == 1
  assert turns[0]['tools'] == '[tools: bash ×2, str_replace ×1]'
  assert turns[0]['text'] == 'Running the checks.'
  assert turns[0]['n'] == 1
  assert turns[0]['ts'] == '2026-05-14T10:00:00Z'   # group's first timestamp
  assert set(turns[0]) == {'n', 'role', 'text', 'tools', 'compaction', 'ts'}


def test_reconstruct_merge_joins_texts_and_ors_compaction():
  records = [
    _asst('r1', text='First half.', req='req_A', ts='2026-05-14T10:00:00Z'),
    _asst('r2', text='Second half.', req='req_A', ts='2026-05-14T10:00:01Z'),
  ]
  records[1]['isCompactSummary'] = True
  turns = ds.reconstruct(records, include_sidechains=False)
  assert len(turns) == 1
  assert turns[0]['text'] == 'First half.\nSecond half.'
  assert turns[0]['compaction'] is True


def test_reconstruct_user_record_between_blocks_merge():
  '''A user record has no requestId, so it can never join a group -- and its
  presence must stop the two assistant records around it from merging across
  it, or the narrative would be silently reordered.'''
  records = [
    _asst('r1', tools=['bash'], req='req_A', ts='2026-05-14T10:00:00Z'),
    {'type': 'user', 'uuid': 'u1', 'parentUuid': 'r1',
     'timestamp': '2026-05-14T10:00:01Z',
     'message': {'role': 'user', 'content': 'wait, stop'}},
    _asst('r2', tools=['bash'], req='req_A', ts='2026-05-14T10:00:02Z'),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert [t['role'] for t in turns] == ['assistant', 'user', 'assistant']
  assert [t['n'] for t in turns] == [1, 2, 3]
  assert turns[0]['tools'] == '[tools: bash ×1]'
  assert turns[2]['tools'] == '[tools: bash ×1]'


def test_reconstruct_records_without_request_id_stay_separate():
  records = [
    _asst('r1', tools=['bash'], ts='2026-05-14T10:00:00Z'),
    _asst('r2', tools=['bash'], ts='2026-05-14T10:00:01Z'),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert len(turns) == 2
  assert all(t['tools'] == '[tools: bash ×1]' for t in turns)


def test_reconstruct_does_not_merge_across_different_requests():
  records = [
    _asst('r1', tools=['bash'], req='req_A', ts='2026-05-14T10:00:00Z'),
    _asst('r2', tools=['Read'], req='req_B', ts='2026-05-14T10:00:01Z'),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert len(turns) == 2
  assert turns[1]['tools'] == '[tools: Read ×1]'


def test_reconstruct_merge_survives_dropped_tool_result_plumbing():
  '''The tool_result user records between an assistant request's tool_use
  records are dropped before merging, so they must not break the group.'''
  records = [
    _asst('r1', tools=['bash'], req='req_A', ts='2026-05-14T10:00:00Z'),
    {'type': 'user', 'uuid': 'u1', 'parentUuid': 'r1',
     'timestamp': '2026-05-14T10:00:01Z',
     'message': {'role': 'user',
                 'content': [{'type': 'tool_result', 'tool_use_id': 'r1-0',
                              'content': 'ok'}]}},
    _asst('r2', tools=['Read'], req='req_A', ts='2026-05-14T10:00:02Z'),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert len(turns) == 1
  assert turns[0]['tools'] == '[tools: bash ×1, Read ×1]'


# --- Task 8 item 3: file paths are locators, not secrets --------------------

_SCRATCH_PATH = ('/private/tmp/claude-501/-Users-lowell-Projects-agent-skills/'
                 '02f97fc5-5189-47d8-9d6e-921183575d18/scratchpad')
_SK_PROJ = 'sk-proj-' + 'aB3' * 20


def test_redaction_keeps_file_paths_and_still_catches_sk_proj(tmp_path):
  '''All 558 redactions across the real corpus were high-entropy false
  positives on file paths -- "/" was inside the character class, so a long
  scratchpad path cleared the 40-char bar and the digest's redactions: header
  (its trust signal) counted destroyed locators as scrubbed secrets.

  Both halves live in ONE test on purpose: narrowing high-entropy is what
  opens a real leak, because high-entropy is the SOLE redactor for sk-proj-
  (openai-key's hyphen-free sk-[A-Za-z0-9]{20,} cannot match across the
  hyphen). These assertions must never drift apart.'''
  text = f'wrote {_SCRATCH_PATH}/notes.md using {_SK_PROJ} for the call'
  out, counts = ds.redact(text)
  assert _SCRATCH_PATH in out                     # locator preserved
  assert _SK_PROJ not in out                      # secret gone
  assert counts.get('high-entropy') == 1          # ... and it is the one that fired
  assert 'openai-key' not in counts               # sk-proj- is invisible to it

  session = {
    'session_id': 'beef0001beef', 'source': 'claude-code', 'project': None,
    'turns': [{'n': 1, 'role': 'user', 'text': text, 'tools': '',
               'compaction': False, 'ts': '2026-05-14T10:00:00Z'}],
  }
  digest = ds.write_digest(session, tmp_path / 'sessions')
  body = digest.read_text()
  assert _SCRATCH_PATH in body                    # survives intact in the digest
  assert _SK_PROJ not in body
  assert 'redactions: 1' in body


def test_redaction_still_catches_github_pat_and_base64():
  '''The other two shapes high-entropy is solely responsible for.'''
  pat = 'github_pat_11ABCDE0Y' + 'aZ9' * 15
  blob = 'QUJDREVGabcdef0123456789QUJDREVGabcdef0123456789QUJD'
  for secret in (pat, blob):
    out, counts = ds.redact(f'value {secret} end')
    assert secret not in out
    assert counts.get('high-entropy') == 1


def test_redaction_leaves_plain_project_paths_alone():
  text = 'see /Users/lowell/Projects/agent-skills/skills/llm-wiki/SKILL.md'
  out, counts = ds.redact(text)
  assert out == text
  assert counts == {}


# --- Task 8 item 4: non-dict records/conversations must not abort the run ---

def test_non_dict_jsonl_line_is_skipped_not_fatal(tmp_path, capsys):
  '''A JSONL line that is valid JSON but not an object reached reconstruct's
  r.get('type') and raised an uncaught AttributeError, killing the run. It must
  be skipped like any unknown record type.'''
  base = tmp_path / 'projects' / '-p'
  sid = 'a1a1a1a1-0000-0000-0000-000000000000'
  base.mkdir(parents=True)
  (base / f'{sid}.jsonl').write_text(
    '["not", "an", "object"]\n42\n"bare string"\nnull\n' +
    json.dumps({'type': 'user', 'uuid': 'a', 'parentUuid': None,
                'timestamp': '2026-05-14T10:00:00Z',
                'message': {'role': 'user', 'content': 'still here'}}) + '\n')
  good = 'b2b2b2b2-0000-0000-0000-000000000000'
  _write_jsonl(base / f'{good}.jsonl', [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None,
     'timestamp': '2026-05-14T10:00:00Z',
     'message': {'role': 'user', 'content': 'sibling ok'}}])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', str(tmp_path / 'projects'), str(out)])
  assert rc == 0                                    # not a parse failure: skipped
  bodies = sorted(p.read_text() for p in out.glob('*.md'))
  assert len(bodies) == 2                           # sibling still written
  assert any('still here' in b for b in bodies)
  assert 'parse-failure' not in capsys.readouterr().err


def _write_conversations(tmp_path, payload):
  src = tmp_path / 'conversations.json'
  src.write_text(payload if isinstance(payload, str) else json.dumps(payload))
  return src


_GOOD_CONV = {
  'uuid': 'c0c0c0c0-0000-0000-0000-000000000000', 'name': 'good one',
  'chat_messages': [{'sender': 'human', 'created_at': '2026-05-14T10:00:00Z',
                     'text': 'sibling conversation'}],
}


def test_claude_ai_non_list_top_level_is_parse_failure(tmp_path, capsys):
  '''A top-level JSON object (not a list) used to iterate its keys as
  conversations and abort with a traceback, killing all 156 digests.'''
  src = _write_conversations(tmp_path, {'conversations': [_GOOD_CONV]})
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-ai', str(src), str(out)])
  assert rc == 1                                    # §16.4: a file failed
  assert 'parse-failure' in capsys.readouterr().err
  assert len(list(out.glob('*.md'))) == 0


def test_claude_ai_non_dict_conversation_is_skipped(tmp_path):
  src = _write_conversations(tmp_path, ['a bare string', 7, None, _GOOD_CONV])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-ai', str(src), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1                          # the good sibling survives
  assert 'sibling conversation' in digests[0].read_text()


def test_claude_ai_non_list_chat_messages_is_skipped(tmp_path):
  bad = {'uuid': 'd0d0d0d0-0000-0000-0000-000000000000', 'name': 'bad shape',
         'chat_messages': {'sender': 'human', 'text': 'a dict, not a list'}}
  src = _write_conversations(tmp_path, [bad, _GOOD_CONV])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-ai', str(src), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1
  assert 'sibling conversation' in digests[0].read_text()


def test_claude_ai_non_dict_message_is_skipped(tmp_path):
  bad = {'uuid': 'e0e0e0e0-0000-0000-0000-000000000000', 'name': 'bad message',
         'chat_messages': ['a bare string', None,
                           {'sender': 'human', 'created_at': '2026-05-14T10:00:00Z',
                            'text': 'real message'}]}
  src = _write_conversations(tmp_path, [bad, _GOOD_CONV])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-ai', str(src), str(out)])
  assert rc == 0
  bodies = sorted(p.read_text() for p in out.glob('*.md'))
  assert len(bodies) == 2
  assert any('real message' in b for b in bodies)


# --- Task 8 item 5: a typo'd SRC directory must not exit 0 ------------------

def test_nonexistent_src_dir_reports_and_exits_1(tmp_path, capsys):
  '''rglob on a nonexistent dir returns empty, so a typo'd --source path
  printed nothing and exited 0 -- indistinguishable from "nothing new".'''
  missing = tmp_path / 'porjects'
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', str(missing), str(out)])
  assert rc == 1
  err = capsys.readouterr().err
  assert 'parse-failure' in err
  assert str(missing) in err


# --- Task 8 item 6: re-write a digest when the session has grown ------------

def _grown_session(n_turns):
  '''Real narrative sessions span up to 59.7h wall-clock and are appended to
  under one session id across days, so the literal §16.4 skip rule froze a
  digest written at hour 4 of a 60-hour session forever.'''
  return {
    'session_id': 'ab12cd34ef56', 'source': 'claude-code', 'project': None,
    'turns': [{'n': i, 'role': 'user' if i % 2 else 'assistant',
               'text': f'turn {i}', 'tools': '', 'compaction': False,
               'ts': f'2026-05-{14 + i // 12:02d}T10:00:00Z'}
              for i in range(1, n_turns + 1)],
  }


def test_write_digest_rewrites_when_session_grew(tmp_path):
  out = tmp_path / 'sessions'
  first = ds.write_digest(_grown_session(2), out)
  assert 'turns: 2' in first.read_text()
  second = ds.write_digest(_grown_session(5), out)
  assert second is not None                       # replaced, not skipped
  digests = list(out.glob('*.md'))
  assert len(digests) == 1                        # exactly one digest remains
  body = digests[0].read_text()
  assert 'turns: 5' in body
  assert 'turn 5' in body


def test_write_digest_replaces_even_when_filename_changes(tmp_path):
  '''Growth can change the dates:/slug parts of the filename, so a stale
  digest under the old name must be removed, not left as a second digest for
  the same session.'''
  out = tmp_path / 'sessions'
  early = _grown_session(2)
  first = ds.write_digest(early, out)
  later = _grown_session(30)                      # spans into a later date
  later['turns'][0]['text'] = 'a completely different opening line'
  second = ds.write_digest(later, out)
  assert second is not None
  assert second.name != first.name
  assert not first.exists()
  assert [p.name for p in out.glob('*.md')] == [second.name]


def test_write_digest_still_skips_when_not_grown(tmp_path):
  out = tmp_path / 'sessions'
  first = ds.write_digest(_grown_session(5), out)
  before = first.read_text()
  assert ds.write_digest(_grown_session(5), out) is None   # same size: skip
  assert ds.write_digest(_grown_session(3), out) is None    # shrunk: skip
  assert len(list(out.glob('*.md'))) == 1
  assert first.read_text() == before                       # untouched


# --- Fix pass item 2: nested workflow subagents fold in with the flag ------

def test_sidechains_recurse_into_nested_workflow_subagents(tmp_path):
  '''424 of the real corpus's sidechain files sit directly at
  <stem>/subagents/agent-*.jsonl, but 844 more nest one level deeper at
  <stem>/subagents/workflows/wf_*/agent-*.jsonl -- a single-level glob missed
  every one of them even with --include-sidechains. Gathering sidechain
  records must recurse under subagents/ so both depths fold into the parent
  session, without creating any digest of their own.'''
  src = _sidechain_fixture(tmp_path, [
    ('agent-ae022938c3ffa8c41', 'subagent findings one', '2026-05-14T10:00:01Z')])
  nested_dir = (src / '-Users-lowell-Projects-bls-stats' / _PARENT_SID
                / 'subagents' / 'workflows' / 'wf_test')
  _write_jsonl(nested_dir / 'agent-nested1.jsonl', [
    {'type': 'assistant', 'uuid': 'n1', 'parentUuid': None, 'isSidechain': True,
     'timestamp': '2026-05-14T10:00:02Z',
     'message': {'role': 'assistant',
                 'content': [{'type': 'text', 'text': 'nested workflow line'}]}},
  ])

  # without the flag: nested workflow content absent, still one digest
  out_off = tmp_path / 'out_off'
  rc_off = ds.main(['--source', 'claude-code', str(src), str(out_off)])
  assert rc_off == 0
  digests_off = list(out_off.glob('*.md'))
  assert len(digests_off) == 1
  assert 'nested workflow line' not in digests_off[0].read_text()

  # with the flag: nested workflow content present, still one digest -- no
  # orphan agent-... digest for the nested file
  out_on = tmp_path / 'out_on'
  rc_on = ds.main(['--source', 'claude-code', '--include-sidechains',
                   str(src), str(out_on)])
  assert rc_on == 0
  digests_on = list(out_on.glob('*.md'))
  assert len(digests_on) == 1
  assert digests_on[0].name.endswith(f'-{_PARENT_SID[:8]}.md')
  body = digests_on[0].read_text()
  assert 'nested workflow line' in body
  assert 'subagent findings one' in body   # depth-4 sidechain still merges too
  assert 'main answer' in body
  assert 'turns: 4' in body   # main(2) + depth-4 sidechain(1) + nested(1)


# --- Fix pass item 1: SRC as a single project directory -------------------

def test_claude_code_src_as_single_project_dir_finds_main_sessions(tmp_path):
  '''Task 8's enumeration rule (p.parent.parent == src) silently assumed SRC is
  always the projects root. Pointing SRC at one project's own directory --
  natural usage per Task 6's contract ("SRC may be a projects dir or a single
  .jsonl") -- used to yield zero sessions. The depth-independent fix (no
  'subagents' path component) must find both main sessions here, including one
  that has its own nested subagents/ subtree, while still excluding that
  subtree's file as a session of its own.'''
  proj = tmp_path / '-Users-lowell-Projects-agent-skills'
  sid1 = 'aaaa1111-0000-0000-0000-000000000000'
  sid2 = 'bbbb2222-0000-0000-0000-000000000000'
  _write_jsonl(proj / f'{sid1}.jsonl', [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None,
     'timestamp': '2026-05-14T10:00:00Z',
     'message': {'role': 'user', 'content': 'main session one'}}])
  _write_jsonl(proj / f'{sid2}.jsonl', [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None,
     'timestamp': '2026-05-14T10:00:00Z',
     'message': {'role': 'user', 'content': 'main session two'}}])
  # a sidechain subtree nested under one of the session stems -- must not be
  # picked up as a standalone session, at any depth
  _write_jsonl(proj / sid1 / 'subagents' / 'agent-abc123.jsonl', [
    {'type': 'assistant', 'uuid': 'x', 'parentUuid': None, 'isSidechain': True,
     'timestamp': '2026-05-14T10:00:01Z',
     'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': 'side'}]}}])
  _write_jsonl(proj / sid1 / 'subagents' / 'workflows' / 'wf_x' / 'agent-def456.jsonl', [
    {'type': 'assistant', 'uuid': 'y', 'parentUuid': None, 'isSidechain': True,
     'timestamp': '2026-05-14T10:00:02Z',
     'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': 'nested side'}]}}])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', str(proj), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 2   # both main sessions found; no orphan sidechain digest
  bodies = sorted(p.read_text() for p in digests)
  assert any('main session one' in b for b in bodies)
  assert any('main session two' in b for b in bodies)
  assert not any('side' in b for b in bodies)   # sidechains excluded without the flag


def test_claude_code_src_as_projects_root_still_works(tmp_path):
  '''Depth-pinning complement to the test above: SRC as the projects root (two
  levels: <proj>/<uuid>.jsonl) must still find main sessions and still exclude
  a nested subagents/ subtree -- the depth-independent rule must not regress
  the original, already-tested depth.'''
  base = tmp_path / 'projects'
  proj_name = '-Users-lowell-Projects-alt-nfp'
  sid = 'cccc3333-0000-0000-0000-000000000000'
  _write_jsonl(base / proj_name / f'{sid}.jsonl', [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None,
     'timestamp': '2026-05-14T10:00:00Z',
     'message': {'role': 'user', 'content': 'root-style main session'}}])
  _write_jsonl(base / proj_name / sid / 'subagents' / 'agent-zzz999.jsonl', [
    {'type': 'assistant', 'uuid': 'z', 'parentUuid': None, 'isSidechain': True,
     'timestamp': '2026-05-14T10:00:01Z',
     'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': 'root side'}]}}])
  out = tmp_path / 'out'
  rc = ds.main(['--source', 'claude-code', str(base), str(out)])
  assert rc == 0
  digests = list(out.glob('*.md'))
  assert len(digests) == 1
  body = digests[0].read_text()
  assert 'root-style main session' in body
  assert 'root side' not in body


def test_write_digest_skips_digest_with_unparseable_turns_header(tmp_path):
  '''A hand-edited digest whose turns: header is missing must be skipped, not
  crash the run.'''
  out = tmp_path / 'sessions'
  out.mkdir(parents=True)
  stale = out / '2026-05-14-hand-edited-ab12cd34.md'
  stale.write_text('---\nsession: ab12cd34ef56\n---\nnotes\n')
  assert ds.write_digest(_grown_session(9), out) is None
  assert stale.read_text() == '---\nsession: ab12cd34ef56\n---\nnotes\n'
  assert len(list(out.glob('*.md'))) == 1


def test_turn_date_rejects_malformed_timestamp():
  '''A malformed but non-empty timestamp must not become the digest's date
  ("not-a-timestamp" once sliced to "not-a-time" and reached the filename):
  anything not shaped YYYY-MM-DD falls back to the sentinel.'''
  assert ds._turn_date('2026-05-14T10:00:00Z') == '2026-05-14'
  assert ds._turn_date('2026-05-14') == '2026-05-14'
  assert ds._turn_date('not-a-timestamp') == '0000-00-00'
  assert ds._turn_date('') == '0000-00-00'
  assert ds._turn_date(None) == '0000-00-00'


def test_tool_only_turn_renders_single_space(tmp_path):
  '''A turn with no narrative text and only a tool trace renders as
  "**[02] assistant:** [tools: bash ×1]" -- one space, not two.'''
  session = {
    'session_id': 'b4d5e6f7a8b9', 'source': 'claude-code', 'project': None,
    'turns': [
      {'n': 1, 'role': 'user', 'text': 'run it',
       'tools': '', 'compaction': False, 'ts': '2026-05-14T10:00:00Z'},
      {'n': 2, 'role': 'assistant', 'text': '',
       'tools': '[tools: bash ×1]', 'compaction': False,
       'ts': '2026-05-14T10:01:00Z'},
    ],
  }
  text = ds.write_digest(session, tmp_path / 'sessions').read_text()
  assert '**[02] assistant:** [tools: bash ×1]' in text
  assert ':**  [' not in text


def test_digest_has_blank_line_after_frontmatter(tmp_path):
  text = ds.write_digest(_session(), tmp_path / 'sessions').read_text()
  assert '\n---\n\n**[01] user:**' in text


def test_reads_and_writes_are_utf8_regardless_of_locale(tmp_path):
  '''Path.read_text()/write_text() with no encoding follow the process
  locale. Under a C/ASCII locale with UTF-8 mode off, a well-formed UTF-8
  transcript is misreported as a parse failure and a digest carrying any
  non-ASCII text (every tool trace has "×") cannot even be written. Both
  sources run in a subprocess pinned to that locale; stdio is pinned to
  UTF-8 separately so only the file paths are under test.'''
  import os, subprocess, sys
  env = {**os.environ, 'LC_ALL': 'C', 'LANG': 'C', 'PYTHONIOENCODING': 'utf-8'}
  script = Path(ds.__file__)
  # claude-code: _read_jsonl + write_digest
  base = tmp_path / 'projects' / '-p'
  base.mkdir(parents=True)
  sid = 'aaaa1111-0000-0000-0000-000000000000'
  records = [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None,
     'timestamp': '2026-05-14T10:00:00Z',
     'message': {'role': 'user', 'content': 'summarise the cafe notes'}},
    {'type': 'assistant', 'uuid': 'b', 'parentUuid': 'a',
     'timestamp': '2026-05-14T10:00:05Z',
     'message': {'role': 'assistant', 'content': 'café ✓'}},
  ]
  (base / f'{sid}.jsonl').write_text(
    '\n'.join(json.dumps(r, ensure_ascii=False) for r in records) + '\n',
    encoding='utf-8')
  out = tmp_path / 'out-code'
  r = subprocess.run(
    [sys.executable, '-X', 'utf8=0', str(script), '--source', 'claude-code',
     str(tmp_path / 'projects'), str(out)],
    env=env, capture_output=True, text=True)
  assert r.returncode == 0, r.stderr
  digests = list(out.glob('*.md'))
  assert len(digests) == 1
  assert 'café ✓' in digests[0].read_text(encoding='utf-8')
  # claude-ai: iter_claude_ai's read
  conv = [{
    'uuid': 'ffffdddd-0000-0000-0000-000000000000', 'name': 'Cafe',
    'created_at': '2026-04-02T12:00:00Z', 'updated_at': '2026-04-02T12:30:00Z',
    'chat_messages': [
      {'sender': 'human', 'created_at': '2026-04-02T12:00:00Z', 'text': 'cafe?'},
      {'sender': 'assistant', 'created_at': '2026-04-02T12:00:10Z', 'text': 'café'},
    ],
  }]
  src = tmp_path / 'conversations.json'
  src.write_text(json.dumps(conv, ensure_ascii=False), encoding='utf-8')
  out = tmp_path / 'out-ai'
  r = subprocess.run(
    [sys.executable, '-X', 'utf8=0', str(script), '--source', 'claude-ai',
     str(src), str(out)],
    env=env, capture_output=True, text=True)
  assert r.returncode == 0, r.stderr
  assert 'café' in next(out.glob('*.md')).read_text(encoding='utf-8')


def test_two_titleless_sessions_do_not_collide(tmp_path):
  '''Premise check for a recorded backlog item: two sessions with no
  title-bearing text both slugify to the fallback, but the filename also
  carries each session's own sess8, so they land in two distinct digests.'''
  out = tmp_path / 'sessions'
  def sess(sid):
    return {'session_id': sid, 'source': 'claude-code', 'project': None,
            'turns': [{'n': 1, 'role': 'assistant', 'text': 'hello',
                       'tools': '', 'compaction': False,
                       'ts': '2026-05-14T10:00:00Z'}]}
  a = ds.write_digest(sess('aaaaaaaa-1111'), out)
  b = ds.write_digest(sess('bbbbbbbb-2222'), out)
  assert a is not None and b is not None and a != b
  assert a.name.endswith('-aaaaaaaa.md') and b.name.endswith('-bbbbbbbb.md')
  assert len(list(out.glob('*.md'))) == 2


def test_real_dates_drops_sentinels_and_sorts():
  '''The date floor must ignore undated turns: the sentinel sorts below every
  real date, so leaving it in poisons min(). One helper is the single place
  that rule lives -- the identical sentinel-poisons-min() bug had to be found
  and fixed independently at two of three sites before the duplication was
  even noticed.'''
  turns = [{'ts': '2026-05-15T09:00:00Z'}, {'ts': ''},
           {'ts': '2026-05-14T10:00:00Z'}, {'ts': 'not-a-timestamp'}]
  assert ds._real_dates(turns) == ['2026-05-14', '2026-05-15']
  assert ds._real_dates([{'ts': ''}]) == []
  assert ds._real_dates([]) == []
  assert ds._SENTINEL_DATE == '0000-00-00'


def test_project_name_falls_back_to_the_encoded_dir_name():
  '''The no-cwd branch. With no record carrying cwd, the project name comes
  from the encoded directory's last segment. This branch runs on real-corpus
  sessions but had no unit test, and it is lossy by design -- the encoded name
  splits a hyphenated project, so alt-nfp arrives as "nfp". Pinned so the loss
  is a recorded fact rather than a surprise, and so an inverted precedence
  (dir name winning over cwd) cannot land unnoticed.'''
  assert ds._project_name([], '-Users-lowell-Projects-alt-nfp') == 'nfp'
  assert ds._project_name([{'type': 'user'}],
                          '-Users-lowell-Projects-bls-stats') == 'stats'
  assert ds._project_name([], 'trailing-') == 'trailing'
  assert ds._project_name([], '') is None
  assert ds._project_name([], None) is None
  # cwd, when present, still wins over the encoded name
  assert ds._project_name([{'cwd': '/Users/lowell/Projects/alt-nfp'}],
                          '-Users-lowell-Projects-alt-nfp') == 'alt-nfp'


def test_slugify_rules():
  '''slugify is reached only through write_digest here, and distill_specs.py
  imports it, so its contract is cross-module. Pin the four rules directly:
  lowercase alphanumeric runs joined by hyphens, at most max_words words, a
  60-character cap, and the "session" fallback when nothing survives.'''
  assert ds.slugify('Plan the LLM wiki!') == 'plan-the-llm-wiki'
  assert ds.slugify('one two three four five six seven') == \
      'one-two-three-four-five-six'
  assert ds.slugify('one two three', max_words=2) == 'one-two'
  assert ds.slugify('') == 'session'
  assert ds.slugify(None) == 'session'
  assert ds.slugify('!!! ???') == 'session'
  assert len(ds.slugify('a1b2c3d4' * 30)) == 60


def test_reconstruct_drops_meta_records():
  '''isMeta records are Claude Code's own bookkeeping, not conversation. The
  drop branch had no test, so an inverted or deleted guard would have leaked
  bookkeeping into every digest unnoticed.'''
  records = [
    _rec('a', None, 'user', 'real question', ts='2026-05-14T10:00:00Z'),
    _rec('m', 'a', 'user', 'meta bookkeeping', ts='2026-05-14T10:00:01Z',
         isMeta=True),
  ]
  turns = ds.reconstruct(records, include_sidechains=False)
  assert [t['text'] for t in turns] == ['real question']


def test_reconstruct_keeps_a_textless_compaction_record():
  '''The `not compaction` clause in the tool-plumbing filter. A compaction
  record with genuinely empty text and no tool calls must survive, where the
  same record without the flag is dropped as plumbing. Existing coverage only
  has a compaction record that also carries text, which the text check alone
  would already keep -- so the clause itself was never exercised.'''
  kept = ds.reconstruct(
    [_rec('a', None, 'user', '', ts='2026-05-14T10:00:00Z',
          isCompactSummary=True)],
    include_sidechains=False)
  assert len(kept) == 1
  assert kept[0]['compaction'] is True
  assert kept[0]['text'] == ''

  dropped = ds.reconstruct(
    [_rec('a', None, 'user', '', ts='2026-05-14T10:00:00Z')],
    include_sidechains=False)
  assert dropped == []
