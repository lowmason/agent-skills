from pathlib import Path

from check_provenance import find_binary_assets, main


def test_find_binary_assets_flags_documents():
    tracked = ['a/SKILL.md', 'b/paper.PDF', 'c/notes.docx', 'd/script.py']
    assert find_binary_assets(tracked) == ['b/paper.PDF', 'c/notes.docx']


def test_real_repo_is_clean():
    assert main() == 0
