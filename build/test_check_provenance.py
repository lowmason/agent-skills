from pathlib import Path

from check_provenance import (
    claude_md_originals,
    find_binary_assets,
    main,
    missing_attributions,
    notice_originals,
    originals_mismatch,
)


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


def test_real_notice_originals_has_sixteen_entries():
    # Guards against a silent vacuous pass: if a future heading rewording ever
    # breaks notice_originals's regex, it would return [] and the drift check
    # would compare empty-to-empty and pass without checking anything.
    notice = (Path(__file__).resolve().parent.parent / 'NOTICE').read_text()
    assert len(notice_originals(notice)) == 16


def test_real_repo_originals_are_in_sync():
    repo = Path(__file__).resolve().parent.parent
    claude_md = (repo / 'CLAUDE.md').read_text()
    notice = (repo / 'NOTICE').read_text()
    missing, extra = originals_mismatch(claude_md_originals(claude_md), notice_originals(notice))
    assert missing == []
    assert extra == []
