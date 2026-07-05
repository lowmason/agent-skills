from pathlib import Path

from check_provenance import find_binary_assets, main, missing_attributions


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
