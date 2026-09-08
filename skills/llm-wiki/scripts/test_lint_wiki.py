'''Tests for lint_wiki.py. Stdlib + pytest only; build fixture wikis in tmp.'''
import subprocess
import sys
from pathlib import Path

import pytest

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


def test_broken_link_with_nested_brackets_in_text_is_error(tmp_path):
  '''A link whose TEXT contains brackets must still have its TARGET checked.

  The pre-fix MD_LINK_RE required no ']' inside the link text, so this whole
  link was invisible and its dangling target went unreported.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [the [above] discussion](none.md).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert any(
    level == 'ERROR' and 'broken relative link: none.md' in msg
    for level, _, msg in findings), findings


def test_link_with_nested_brackets_resolves_and_counts_as_inbound(tmp_path):
  '''The same shape, pointing at a real page: no error, and the target is
  no longer an orphan. Pins that the widened regex still captures the TARGET
  (group 1), not the bracketed text.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [the [above] discussion](../sources/a.md).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings if f[0] == 'ERROR'], findings
  assert not [f for f in findings
              if f[0] == 'WARN' and f[1] == 'wiki/sources/a.md'], findings


def test_link_title_is_not_part_of_the_path(tmp_path):
  '''[a](x.md "Title") points at x.md. The title is display metadata.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [A](../sources/a.md "The A page").')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings if f[0] == 'ERROR'], findings
  assert not [f for f in findings
              if f[0] == 'WARN' and f[1] == 'wiki/sources/a.md'], findings


def test_link_title_does_not_hide_a_broken_target(tmp_path):
  '''Stripping the title must not stop the PATH being checked.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [gone](none.md "Not here").')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  # Exact match, not a substring: the pre-fix message read
  # `... none.md "Not here"`, which CONTAINS the substring, so a containment
  # assertion here passes against the bug and pins nothing.
  assert any(
    level == 'ERROR' and msg == 'link: broken relative link: none.md'
    for level, _, msg in findings), findings


def test_index_line_title_is_not_part_of_the_target(tmp_path):
  '''An index line carrying a title must still reach parity with its page.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  (root / 'wiki/index.md').write_text(
    '# Wiki index\n\n## sources\n- [A](sources/a.md "The A page")\n')
  findings = lint_wiki.check_index_parity(root, lint_wiki.discover_pages(root))
  assert findings == [], findings


def test_index_line_with_nested_brackets_reaches_parity(tmp_path):
  '''Plan 28 widened MD_LINK_RE to see one level of nested brackets but left
  INDEX_LINE_RE flat, so `- [the [above] page](sources/a.md)` matched no index
  line at all and the page was reported as having none -- while the body-link
  path resolved the same text fine. The two patterns must agree about what an
  index line points at.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  (root / 'wiki/index.md').write_text(
    '# Wiki index\n\n## sources\n- [the [above] page](sources/a.md)\n')
  findings = lint_wiki.check_index_parity(root, lint_wiki.discover_pages(root))
  assert findings == [], findings


def test_index_line_with_unbalanced_bracket_has_no_target(tmp_path):
  '''The balanced alternation admits no stray `[`, where the old flat class
  did. INDEX_LINE_RE is anchored, so unlike its unanchored sibling it cannot
  re-anchor on the inner link and simply yields no target. Deliberate: the
  line is malformed markdown, and a loud "no index line" beats the old
  accidentally-right read of a typo. Pinned so it is not refiled as a bug.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  (root / 'wiki/index.md').write_text(
    '# Wiki index\n\n## sources\n- [a [b](sources/a.md)\n')
  findings = lint_wiki.check_index_parity(root, lint_wiki.discover_pages(root))
  assert findings == [
    ('ERROR', 'wiki/sources/a.md', 'index: page has no index line')], findings


def test_link_target_helper_handles_both_quote_styles():
  '''Direct unit coverage of the helper: its contract is shared by two
  callers, so it is pinned on its own terms rather than only through them.'''
  assert lint_wiki._link_target('x.md') == 'x.md'
  assert lint_wiki._link_target('x.md "Title"') == 'x.md'
  assert lint_wiki._link_target("x.md 'Title'") == 'x.md'
  assert lint_wiki._link_target('x.md#frag "Title"') == 'x.md#frag'
  # No trailing quoted run: nothing is stripped.
  assert lint_wiki._link_target('a"b".md') == 'a"b".md'


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


def test_self_link_does_not_silence_its_own_orphan_warning(tmp_path):
  '''A page linking to itself has no INBOUND reference -- it is still an
  orphan. Counting the self-link made the orphan check self-defeating.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'As noted [here](p.md), and see [A](../sources/a.md).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings if f[0] == 'ERROR'], findings
  assert any(
    level == 'WARN' and path == 'wiki/samplers/p.md' and 'orphan' in msg
    for level, path, msg in findings), findings


def test_self_cite_does_not_silence_its_own_orphan_warning(tmp_path):
  '''Same hole via the cites: frontmatter channel.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md',
    {'title': 'P', 'type': 'concept', 'cites': ['samplers/p', 'sources/a']})
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert any(
    level == 'WARN' and path == 'wiki/samplers/p.md' and 'orphan' in msg
    for level, path, msg in findings), findings


def test_self_locator_does_not_silence_its_own_orphan_warning(tmp_path):
  '''Same hole via the citation-locator channel: a source page carrying its
  own slug as a locator pointed the reference straight back at itself.'''
  root = make_wiki(tmp_path)
  write_page(
    root, 'sources/robnik-2022-mclmc.md', {'title': 'R', 'type': 'source'},
    'Restating [robnik-2022-mclmc §4] from the same page.')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings if f[0] == 'ERROR'], findings
  assert any(
    level == 'WARN' and path == 'wiki/sources/robnik-2022-mclmc.md'
    and 'orphan' in msg
    for level, path, msg in findings), findings


def test_inbound_reference_from_another_page_still_clears_the_orphan(tmp_path):
  '''The guard must not make every page an orphan: a genuine cross-page
  link still counts. This is the counter-test for the three above.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [A](../sources/a.md).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings
              if f[0] == 'WARN' and f[1] == 'wiki/sources/a.md'], findings


def test_wrong_case_link_is_error_even_on_a_case_insensitive_fs(tmp_path):
  '''`.exists()` asks the filesystem, and APFS/macOS answers case-
  insensitively, so `../Sources/A.MD` resolved and escaped the check. Set
  membership compares names the directory walk produced, so the answer is the
  same on every filesystem.'''
  root = make_wiki(tmp_path)
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [A](../Sources/A.MD).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert any(
    level == 'ERROR' and 'broken relative link: ../Sources/A.MD' in msg
    for level, _, msg in findings), findings


def test_links_to_structural_and_raw_files_still_resolve(tmp_path):
  '''The membership set is every real file under the root, NOT the page set:
  links to structural files and to raw/ are legal and must not become
  errors. This is the regression this task is most likely to cause.'''
  root = make_wiki(tmp_path)
  (root / 'raw/samplers/note.md').write_text('raw note\n')
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [the index](../index.md), [the log](../log.md) and '
    '[the raw note](../../raw/samplers/note.md).')
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert not [f for f in findings if f[0] == 'ERROR'], findings


def test_real_paths_excludes_dot_directories(tmp_path):
  '''A wiki root is a git repo; .git must not be walked into the set, and no
  legitimate link targets a dotfile.'''
  root = make_wiki(tmp_path)
  (root / '.git').mkdir(exist_ok=True)
  (root / '.git/config').write_text('[core]\n')
  paths = lint_wiki._real_paths(root)
  assert (root / 'wiki/index.md').resolve() in paths
  assert (root / '.git/config').resolve() not in paths


def test_link_resolving_outside_the_wiki_root_is_error(tmp_path):
  '''A link escaping the wiki root is absent from the real-file set and is
  therefore broken. `exists()` accepted it, so this is a real tightening --
  and it now ships as a contract rule in SCHEMA.md's "must resolve inside the
  wiki root", so it is pinned rather than left to the helper's docstring.'''
  outside = tmp_path / 'outside-note.md'
  outside.write_text('not part of the wiki\n')
  root = make_wiki(tmp_path / 'wikiroot')
  write_page(root, 'sources/a.md', {'title': 'A', 'type': 'source'})
  write_page(
    root, 'samplers/p.md', {'title': 'P', 'type': 'concept'},
    'See [outside](../../../outside-note.md).')
  assert outside.exists()  # the target is real; only its LOCATION is wrong
  findings = lint_wiki.check_links(root, lint_wiki.discover_pages(root))
  assert any(
    level == 'ERROR'
    and msg == 'link: broken relative link: ../../../outside-note.md'
    for level, _, msg in findings), findings


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


def test_indented_decision_without_basis_is_error(tmp_path):
  '''The basis check must not be disabled by leading whitespace: an indented
  capture is still a `kind: decision` line and still needs a basis.'''
  root = make_wiki(tmp_path)
  write_session(root, '2026-05-14-w-d5e2.md',
                '---\nsession: d5e2\n---\n\n'
                '### [d-01] Something decided\n'
                '  kind: decision · turns: 3-5\n'   # indented, no basis:
                'Statement.\n')
  assert any(f[0] == 'ERROR' and 'basis' in f[2].lower()
             for f in lint_wiki.run_checks(root))


def test_list_prefixed_decision_without_basis_is_error(tmp_path):
  '''Same for a markdown list prefix — `- kind: decision` must not slip past.'''
  root = make_wiki(tmp_path)
  write_session(root, '2026-05-14-v-e6f3.md',
                '---\nsession: e6f3\n---\n\n'
                '### [d-01] Something decided\n'
                '- kind: decision · turns: 3-5\n'   # list prefix, no basis:
                'Statement.\n')
  assert any(f[0] == 'ERROR' and 'basis' in f[2].lower()
             for f in lint_wiki.run_checks(root))


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


def test_neighbor_entry_sha_does_not_satisfy_missing_entry(tmp_path):
  '''Multi-capture digest: [d-01] carries a valid at:/sha: line, [d-02] does
  not. The basis check must be scoped per-[d-NN]-block -- a neighboring
  entry's sha must not bleed across and silently satisfy a different entry's
  requirement.'''
  root = make_wiki(tmp_path)
  write_spec_digest(root, 'multi.md',
                    '[d-01] Has basis\n'
                    'at: specs/a.md §1 · sha: 1234567\n'
                    'excerpt: "x"\n'
                    '\n'
                    '[d-02] Missing basis\n'
                    'at: specs/b.md §2\n'
                    'excerpt: "y"\n')
  basis_findings = [f for f in lint_wiki.run_checks(root)
                     if f[0] == 'ERROR' and 'basis' in f[2]]
  assert len(basis_findings) == 1
  assert any('[d-02]' in f[2] for f in basis_findings)
  assert not any('[d-01]' in f[2] for f in basis_findings)


# --- citation recognition (spec: lint_wiki citation-detection contract) ---

# `ghost-2020-none` is deliberately absent: that absence is what makes case 3
# an error and pins test_body_citation_without_source_is_error.
CITE_SLUGS = ('robnik-2022-mclmc', 'hoffman-2014-nuts', 'mclmc')


def cite_fixture(root, body):
  '''Wiki with the three fixture source slugs plus one concept page carrying
  `body`. Returns (citation_errors, referenced) where `referenced` is the set
  of fixture slugs something pointed at -- i.e. those with no orphan WARN. The
  concept page cites nothing, so a slug lands in `referenced` only via a body
  locator, which is what makes the three verdicts distinguishable.'''
  for stem in CITE_SLUGS:
    valid_source(root, f'sources/{stem}.md', stem)
  write_page(root, 'samplers/notes.md',
             {'title': 'Notes', 'type': 'concept', 'status': 'unverified',
              'topics': '[samplers]', 'cites': '[]',
              'updated': '2026-07-22'},
             body=body)
  set_index(root,
            [f'- [{s}](sources/{s}.md) — s · 1 · verified · 2026-07-22'
             for s in CITE_SLUGS]
            + ['- [notes](samplers/notes.md) — s · 1 · unverified · 2026-07-22'])
  findings = lint_wiki.run_checks(root)
  errors = [f[2] for f in findings
            if f[0] == 'ERROR' and f[2].startswith('citation:')]
  orphaned = {f[1] for f in findings if f[0] == 'WARN' and 'orphan' in f[2]}
  referenced = {s for s in CITE_SLUGS
                if f'wiki/sources/{s}.md' not in orphaned}
  return errors, referenced


# The spec's acceptance table, verbatim. 'cite' = recognized and resolves,
# 'error' = recognized and unresolved, 'prose' = not a citation at all.
CITATION_CASES = [
  (1, '[robnik-2022-mclmc §4.2]', 'cite', 'robnik-2022-mclmc'),
  (2, '[hoffman-2014-nuts Table 2]', 'cite', 'hoffman-2014-nuts'),
  (3, '[ghost-2020-none §4.2]', 'error', 'ghost-2020-none'),
  (4, '[mclmc §4.2]', 'cite', 'mclmc'),
  (5, '[see below]', 'prose', None),
  (6, '[per the user]', 'prose', None),
  (7, '[todo fix this]', 'prose', None),
  (8, '[Figure 2]', 'prose', None),
  (9, '[NUTS §3]', 'prose', None),
  (10, '[see Table 2]', 'prose', None),
  (11, '[Hoffman2014 §3]', 'error', 'Hoffman2014'),
  (12, '[robnik_2022 §4]', 'error', 'robnik_2022'),
  (13, '[robnik.2022 §4]', 'error', 'robnik.2022'),
  (14, '[the [above] discussion](x.md)', 'prose', None),
  (15, '[robnik-2022-mclmc §4.2](x.md)', 'prose', None),
  (16, '### [d-01] Flat files primary', 'prose', None),
  (17, '## [2026-07-24] log entry', 'prose', None),
  (18, '[well-known Table 2]', 'error', 'well-known'),
]


@pytest.mark.parametrize('case,body,verdict,token', CITATION_CASES,
                         ids=[f'case{c}' for c, _, _, _ in CITATION_CASES])
def test_citation_recognition_table(tmp_path, case, body, verdict, token):
  errors, referenced = cite_fixture(make_wiki(tmp_path), body)
  if verdict == 'cite':
    assert errors == [], f'case {case}: unexpected citation error'
    assert token in referenced, f'case {case}: did not count as an inbound ref'
  elif verdict == 'error':
    assert any(token in e for e in errors), f'case {case}: no error for {token}'
    assert referenced == set(), f'case {case}: nothing should resolve'
  else:
    assert errors == [], f'case {case}: prose treated as a citation'
    assert referenced == set(), f'case {case}: prose counted as an inbound ref'


@pytest.mark.parametrize('position,expected', [
  ('§4.2', True),
  ('p. 12', True),
  ('Table 2', True),
  ('Tables 3', True),      # prefix match, free
  ('Fig 1', True),
  ('Figure 1', True),      # prefix match, free
  ('Figs 2-3', True),      # prefix match, free
  ('Eq 7', True),
  ('12', True),
  (' §4.2', True),         # leading whitespace is stripped
  ('below', False),
  ('the user', False),
  ('fix this', False),
  ('pp. 12', False),       # accepted narrowness: D1's list has p., not pp.
  ('Ch 4', False),         # accepted narrowness: D1's list has no Ch
  ('see Table 2', False),  # sigil must OPEN the position, not appear in it
])
def test_looks_like_position(position, expected):
  assert lint_wiki._looks_like_position(position) is expected


@pytest.mark.parametrize('token,position,expected', [
  ('robnik-2022-mclmc', '§4.2', True),       # shape: hyphen
  ('Hoffman2014', '§3', True),               # shape: 4-digit year
  ('mclmc', '§4.2', True),                   # membership only
  ('nope', '§4.2', False),                   # neither shape nor membership
  ('see', 'Table 2', False),                 # position ok, token is prose
  ('mclmc', 'see this', False),              # membership, bad position
  ('robnik-2022-mclmc', 'see this', False),  # shape, bad position (limitation 1)
])
def test_is_citation(token, position, expected):
  assert lint_wiki._is_citation(token, position, set(CITE_SLUGS)) is expected


def test_index_line_with_fragment_resolves(tmp_path):
  '''A deep-link index line is legal: SCHEMA.md reserves nothing that
  prohibits it, and check_links already strips fragments from body links.'''
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a')
  set_index(root,
            ['- [a](sources/a.md#background) — s · 1 · verified · 2026-07-22'])
  assert [f for f in lint_wiki.run_checks(root)
          if f[0] == 'ERROR' and 'index' in f[2].lower()] == []


def test_index_lines_differing_only_by_fragment_are_a_duplicate(tmp_path):
  '''Two lines pointing into the same page collapse to one target, so
  duplicate detection is fixed by the same strip.'''
  root = make_wiki(tmp_path)
  valid_source(root, 'sources/a.md', 'a')
  set_index(root,
            ['- [a](sources/a.md#background) — s · 1 · verified · 2026-07-22',
             '- [a](sources/a.md#method) — s · 1 · verified · 2026-07-22'])
  assert any(f[0] == 'ERROR' and 'duplicate' in f[2].lower()
             for f in lint_wiki.run_checks(root))
