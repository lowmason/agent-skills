import re
from pathlib import Path

import pytest

import check_provenance

from check_provenance import (
    AGENT_LICENSES,
    BUNDLED_LICENSES,
    REPO,
    agent_license_violations,
    bundled_license_violations,
    claude_md_originals,
    find_binary_assets,
    main,
    missing_attributions,
    notice_originals,
    originals_mismatch,
)


ROOT_TEXT = {'LICENSE': 'MIT, Lowell Mason\n', 'LICENSE-x': 'MIT, Upstream\n'}


def _license_tree(tmp_path, copies):
    '''A repo with two root license files and one skill directory per key of
    copies, each holding the named license files copied from the root.'''
    for name, text in ROOT_TEXT.items():
        (tmp_path / name).write_text(text)
    for skill, files in copies.items():
        d = tmp_path / 'skills' / skill
        d.mkdir(parents=True)
        (d / 'SKILL.md').write_text('---\nname: x\n---\n')
        for name in files:
            (d / name).write_text(ROOT_TEXT[name])
    return tmp_path


TABLE = {'LICENSE-x': ('adapted',)}


def test_bundled_licenses_clean_when_every_copy_matches(tmp_path):
    repo = _license_tree(tmp_path, {'own': ['LICENSE'], 'adapted': ['LICENSE', 'LICENSE-x']})
    assert bundled_license_violations(repo, ['adapted', 'own'], TABLE) == []


def test_bundled_licenses_report_a_missing_copy(tmp_path):
    repo = _license_tree(tmp_path, {'own': [], 'adapted': ['LICENSE', 'LICENSE-x']})
    assert bundled_license_violations(repo, ['adapted', 'own'], TABLE) == [
        'skills/own/LICENSE: missing; copy the root LICENSE here as a regular file']


def test_bundled_licenses_report_a_symlinked_copy(tmp_path):
    # install.py --copy refuses symlinks, so a linked copy would not travel.
    repo = _license_tree(tmp_path, {'own': [], 'adapted': ['LICENSE', 'LICENSE-x']})
    (repo / 'skills' / 'own' / 'LICENSE').symlink_to(repo / 'LICENSE')
    assert bundled_license_violations(repo, ['adapted', 'own'], TABLE) == [
        'skills/own/LICENSE: a symlink, which install.py --copy refuses; copy the root LICENSE as a regular file']


def test_bundled_licenses_report_a_copy_that_differs(tmp_path):
    repo = _license_tree(tmp_path, {'own': ['LICENSE'], 'adapted': ['LICENSE', 'LICENSE-x']})
    (repo / 'skills' / 'adapted' / 'LICENSE-x').write_text('edited\n')
    assert bundled_license_violations(repo, ['adapted', 'own'], TABLE) == [
        'skills/adapted/LICENSE-x: differs from the root LICENSE-x; copy it again']


def test_bundled_licenses_report_a_license_outside_the_mapping(tmp_path):
    repo = _license_tree(tmp_path, {'own': ['LICENSE', 'LICENSE-x'], 'adapted': ['LICENSE', 'LICENSE-x']})
    assert bundled_license_violations(repo, ['adapted', 'own'], TABLE) == [
        'skills/own/LICENSE-x: not mapped to own in BUNDLED_LICENSES']


def test_bundled_licenses_report_an_unmapped_root_file_and_a_bad_table(tmp_path):
    repo = _license_tree(tmp_path, {'own': ['LICENSE']})
    table = {'LICENSE-gone': ('own',), 'LICENSE-x': ('ghost',)}
    assert bundled_license_violations(repo, ['own'], {}) == [
        'LICENSE-x: root license file is mapped to no skill in BUNDLED_LICENSES']
    assert bundled_license_violations(repo, ['own'], table) == [
        'BUNDLED_LICENSES: LICENSE-gone is not a root license file',
        'BUNDLED_LICENSES: LICENSE-x names ghost, which is not a skill directory',
    ]


def test_bundled_licenses_table_names_no_plain_license():
    # LICENSE goes to every skill implicitly; listing it would hide a gap.
    assert 'LICENSE' not in BUNDLED_LICENSES


def test_find_binary_assets_flags_documents():
    tracked = ['a/SKILL.md', 'b/paper.PDF', 'c/notes.docx', 'd/script.py']
    assert find_binary_assets(tracked) == ['b/paper.PDF', 'c/notes.docx']


def test_real_repo_is_clean():
    assert main() == 0


def test_anchored_entry_matches():
    notice = 'stuff\n    validate-data/\nmore\n'
    assert missing_attributions(['validate-data'], notice) == []


def test_prose_substring_does_not_match():
    notice = 'conventions plus specs/plans/ retirement prose\n'
    assert missing_attributions(['plans'], notice) == ['plans']


def test_substring_of_other_entry_does_not_match():
    notice = '    receiving-code-review/\n    validate-data/\n'
    assert missing_attributions(['code-review', 'data'], notice) == ['code-review', 'data']


def test_notice_originals_extracts_indented_block():
    notice = (
        'preamble\n\n'
        'The following skills are original works by Lowell Mason, MIT licensed:\n'
        '\n'
        '    alpha/\n'
        '    beta/   (including a trailing note)\n'
        '    gamma/\n'
        '\n'
        'gamma/ is an original work by Lowell Mason (MIT). It CITES other stuff.\n'
    )
    assert notice_originals(notice) == ['alpha', 'beta', 'gamma']


def test_notice_originals_missing_heading_returns_empty():
    assert notice_originals('no such heading here\n') == []


def test_claude_md_originals_parses_bullet_with_trailing_prose():
    # Mirrors the real bullet: a parenthetical before the colon, backtick-quoted
    # names after it, and trailing prose (a count note) after the list's period.
    line = (
        "- **Lowell's originals** (MIT, `LICENSE`): `alpha`, `beta`, `gamma`. "
        "(Three — keep in sync with `NOTICE`, which is authoritative.)\n"
    )
    assert claude_md_originals(line) == ['alpha', 'beta', 'gamma']


def test_claude_md_originals_missing_bullet_returns_empty():
    assert claude_md_originals('no such bullet here\n') == []


def test_originals_mismatch_flags_skill_missing_from_claude_md():
    # This is the drift the 2026-07-20 audit found: NOTICE lists a skill that
    # CLAUDE.md's restatement omits.
    missing, extra = originals_mismatch(['alpha', 'beta'], ['alpha', 'beta', 'gamma'])
    assert missing == ['gamma']
    assert extra == []


def test_originals_mismatch_flags_skill_extra_in_claude_md():
    missing, extra = originals_mismatch(['alpha', 'beta', 'delta'], ['alpha', 'beta'])
    assert missing == []
    assert extra == ['delta']


def test_originals_mismatch_clean_when_sets_match_out_of_order():
    missing, extra = originals_mismatch(['beta', 'alpha'], ['alpha', 'beta'])
    assert missing == []
    assert extra == []


def test_real_notice_originals_match_claude_md_stated_count():
    # Guards against a silent vacuous pass: if a future heading rewording ever
    # breaks notice_originals's regex, it would return [] and the drift check
    # would compare empty-to-empty and pass without checking anything. The
    # expected count is the "(N originals" note on CLAUDE.md's originals
    # bullet rather than a literal, so adding an original means updating that
    # note, not this test, and the note itself can no longer drift.
    repo = Path(__file__).resolve().parent.parent
    notice = (repo / 'NOTICE').read_text()
    claude_md = (repo / 'CLAUDE.md').read_text()
    bullet = re.search(r"^- \*\*Lowell's originals\*\*.*$", claude_md, re.M)
    assert bullet, "CLAUDE.md has no \"- **Lowell's originals**\" bullet"
    stated = re.search(r'\((\d+) originals', bullet.group(0))
    assert stated, "CLAUDE.md's originals bullet has no '(N originals' count note"
    assert len(notice_originals(notice)) == int(stated.group(1))


def test_real_repo_originals_are_in_sync():
    repo = Path(__file__).resolve().parent.parent
    claude_md = (repo / 'CLAUDE.md').read_text()
    notice = (repo / 'NOTICE').read_text()
    missing, extra = originals_mismatch(claude_md_originals(claude_md), notice_originals(notice))
    assert missing == []
    assert extra == []


POINTER = '# license: MIT. Full text: LICENSE-x.'
AGENT_TABLE = {'LICENSE-x': ('adapted',)}
ADAPTED_SURFACES = (
    'agents/adapted.md',
    'runtimes/codex/agents/adapted.toml',
    'runtimes/gemini/agents/adapted.md',
)
OWN_SURFACES = tuple(s.replace('adapted', 'own') for s in ADAPTED_SURFACES)


def _agent_text(surface, pointed):
    pointer = f'{POINTER}\n' if pointed else ''
    if surface.endswith('.toml'):
        return f'# generated\n{pointer}name = "a"\n'
    return f'---\nname: a\n{pointer}# cc-guide: x @1\n---\n\nBody.\n'


def _agent_tree(tmp_path, pointed):
    '''A repo with root LICENSE-x and agents `adapted` and `own`, each with
    all three surfaces; the surfaces named in pointed carry POINTER.'''
    (tmp_path / 'LICENSE-x').write_text(ROOT_TEXT['LICENSE-x'])
    for surface in ADAPTED_SURFACES + OWN_SURFACES:
        path = tmp_path / surface
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_agent_text(surface, surface in pointed))
    return tmp_path


def test_agent_licenses_clean_when_every_surface_points(tmp_path):
    repo = _agent_tree(tmp_path, pointed=ADAPTED_SURFACES)
    assert agent_license_violations(repo, AGENT_TABLE) == []


def test_agent_licenses_report_a_missing_pointer(tmp_path):
    pointed = tuple(s for s in ADAPTED_SURFACES if s != 'runtimes/codex/agents/adapted.toml')
    repo = _agent_tree(tmp_path, pointed=pointed)
    assert agent_license_violations(repo, AGENT_TABLE) == [
        'runtimes/codex/agents/adapted.toml: no license pointer naming LICENSE-x, '
        'which AGENT_LICENSES maps to adapted']


def test_agent_licenses_report_an_unmapped_pointer(tmp_path):
    repo = _agent_tree(tmp_path, pointed=ADAPTED_SURFACES + ('agents/own.md',))
    assert agent_license_violations(repo, AGENT_TABLE) == [
        'agents/own.md: license pointer names LICENSE-x, which AGENT_LICENSES does not map to own']


def test_agent_licenses_report_a_pointer_in_the_body(tmp_path):
    pointed = tuple(s for s in ADAPTED_SURFACES if s != 'agents/adapted.md')
    repo = _agent_tree(tmp_path, pointed=pointed)
    with (repo / 'agents' / 'adapted.md').open('a') as f:
        f.write(f'{POINTER}\n')
    assert agent_license_violations(repo, AGENT_TABLE) == [
        'agents/adapted.md: license pointer outside the frontmatter, where the model reads it',
        'agents/adapted.md: no license pointer naming LICENSE-x, which AGENT_LICENSES maps to adapted']


def test_agent_licenses_report_a_bad_table(tmp_path):
    repo = _agent_tree(tmp_path, pointed=())
    assert agent_license_violations(repo, {'LICENSE-y': ('ghost',)}) == [
        'AGENT_LICENSES: LICENSE-y is not a root license file',
        'AGENT_LICENSES: LICENSE-y names ghost, which is not an agent in agents/']


def test_agent_licenses_table_matches_notice():
    notice = (REPO / 'NOTICE').read_text()
    distilled = re.findall(r'agents/([a-z-]+)\.md is a read-only agent definition distilled', notice)
    assert sorted(distilled) == sorted(AGENT_LICENSES['LICENSE-superpowers'])


@pytest.mark.parametrize('surface', ADAPTED_SURFACES)
def test_agent_licenses_report_a_missing_pointer_on_each_surface(tmp_path, surface):
    repo = _agent_tree(tmp_path, pointed=tuple(s for s in ADAPTED_SURFACES if s != surface))
    assert agent_license_violations(repo, AGENT_TABLE) == [
        f'{surface}: no license pointer naming LICENSE-x, which AGENT_LICENSES maps to adapted']


def test_agent_licenses_read_a_hyphenated_name_in_a_pointer(tmp_path):
    repo = _agent_tree(tmp_path, pointed=ADAPTED_SURFACES)
    path = repo / 'agents' / 'adapted.md'
    path.write_text(path.read_text().replace(
        POINTER, '# license: MIT. Full text: LICENSE-x and LICENSE-y-sources.'))
    assert agent_license_violations(repo, AGENT_TABLE) == [
        'agents/adapted.md: license pointer names LICENSE-y-sources, '
        'which AGENT_LICENSES does not map to adapted']


def test_main_runs_the_agent_license_check(monkeypatch):
    monkeypatch.setattr(check_provenance, 'AGENT_LICENSES', {'LICENSE-superpowers': ('debugger',)})
    assert main() == 1
