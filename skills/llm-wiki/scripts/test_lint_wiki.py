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


def test_bare_scalar_cites_is_error(tmp_path):
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a')
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'concept', 'status': 'unverified',
              'topics': '[samplers]', 'cites': 'sources/a',
              'updated': '2026-07-22'})
  assert any(f[0] == 'ERROR' and
             ('bracketed list' in f[2] or 'cites must be' in f[2])
             for f in lint_wiki.run_checks(root))


def test_bare_scalar_topics_is_error(tmp_path):
  root = make_wiki(tmp_path)
  write_page(root, 'samplers/x.md',
             {'title': 'X', 'type': 'concept', 'status': 'unverified',
              'topics': 'samplers', 'cites': '[sources/a]',
              'updated': '2026-07-22'})
  assert any(f[0] == 'ERROR' and 'bracketed list' in f[2]
             for f in lint_wiki.run_checks(root))


def test_trailing_comma_no_phantom_element():
  fm = lint_wiki.parse_frontmatter(
    '---\ntitle: X\ntype: concept\nstatus: unverified\ntopics: [samplers]\n'
    'cites: [sources/a,]\nupdated: 2026-07-22\n---\n')
  assert fm['cites'] == ['sources/a']


def test_secret_sk_proj_key_caught(tmp_path):
  root = make_wiki(tmp_path)
  write_session(root, '2026-05-14-p-a1b2c3d4.md',
                '---\nsession: a1b2c3d4\n---\n\nkey sk-proj-' + 'A1b2C3d4' * 4 + '\n')
  assert any(f[0] == 'ERROR' and 'secret' in f[2].lower()
             for f in lint_wiki.run_checks(root))


def test_secret_github_pat_caught(tmp_path):
  root = make_wiki(tmp_path)
  write_session(root, '2026-05-14-q-e5f6a7b8.md',
                '---\nsession: e5f6a7b8\n---\n\ntoken github_pat_' + 'A1b2C3d4' * 7 + '\n')
  assert any(f[0] == 'ERROR' and 'secret' in f[2].lower()
             for f in lint_wiki.run_checks(root))


def test_openai_key_anchor_ignores_hyphenated_prose_but_still_catches_keys(tmp_path):
  '''The unanchored openai-key pattern matched "sk-" mid-word with no left
  anchor -- measured across 137 real digests: 90 hits, all false positives on
  ordinary hyphenated prose ("task-reviewer-agent-and-deferred-command",
  "risk-adjusted-return-modelling-approach"), because both contain "sk-" as a
  substring of an ordinary word. The (?<![A-Za-z0-9]) lookbehind restricts
  "sk-" to a token start without weakening real-key detection: a proj- style
  key and a legacy sk- key must both still be caught.'''
  root = make_wiki(tmp_path)
  prose_path = write_session(
    root, '2026-05-14-r-a1a1a1a1.md',
    '---\nsession: a1a1a1a1\n---\n\n'
    'The "mapping" is **task-difficulty-dependent** and refers to '
    'specs/task-reviewer-agent-and-deferred-command and a '
    'risk-adjusted-return-modelling-approach.\n')
  keys_path = write_session(
    root, '2026-05-14-s-b2b2b2b2.md',
    '---\nsession: b2b2b2b2\n---\n\n'
    'key sk-proj-' + 'aB3' * 20 + ' and legacy key sk-' + 'A' * 24 + '\n')
  findings = lint_wiki.run_checks(root)
  prose_rel = str(prose_path.relative_to(root))
  keys_rel = str(keys_path.relative_to(root))
  assert not any(f[0] == 'ERROR' and f[1] == prose_rel and 'secret' in f[2].lower()
                 for f in findings)
  assert any(f[0] == 'ERROR' and f[1] == keys_rel and 'secret' in f[2].lower()
             for f in findings)
