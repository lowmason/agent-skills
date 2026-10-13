'''Tests for quotes.py and `cli.py quotes`: a quote counts only whole within
one line of a file under the named root (drift spec R8.3).'''
import io

import pytest

import cli
import quotes
from cc_fixtures import isolated_home, write_tree  # noqa: F401


@pytest.fixture
def root(tmp_path):
    folder = tmp_path / 'docs'
    write_tree(folder, {'hooks.md': 'Exit 2 blocks the call.\nA JSON | deny "blocks" too.\n',
                        'sub/page.md': 'One line.\nTwo line.\n'})
    (tmp_path / 'outside.md').write_text('Exit 2 blocks the call.\n')
    return folder


def test_a_quote_is_found_whole_within_one_line(root):
    files = quotes.QuoteFiles(root)
    assert files.find('hooks.md', 'Exit 2 blocks') == 1
    assert files.find('hooks.md', 'A JSON | deny "blocks" too.') == 2
    assert files.find('sub/page.md', 'Two line.') == 2
    assert files.find('sub/page.md', 'One line. Two line.') is None  # never across lines
    assert files.find('hooks.md', 'exit 2 blocks') is None           # case-sensitive


def test_an_empty_quote_a_missing_file_and_a_path_outside_the_root_are_never_found(root):
    files = quotes.QuoteFiles(root)
    assert files.find('hooks.md', '') is None
    assert files.find('nope.md', 'Exit') is None
    assert files.find('../outside.md', 'Exit 2 blocks') is None
    assert files.find(str(root.parent / 'outside.md'), 'Exit 2 blocks') is None
    assert files.find('sub', 'One') is None


def test_find_any_takes_the_first_file_in_order_that_holds_the_quote(root):
    files = quotes.QuoteFiles(root)
    assert files.find_any(['nope.md', 'sub/page.md', 'hooks.md'], 'line.') == ('sub/page.md', 1)
    assert files.find_any(['hooks.md'], 'line.') is None


def test_rows_print_found_or_missing_and_skip_blanks_and_comments(root):
    rows = ['hooks.md\tExit 2 blocks\n', '\n', '# a comment\n', 'sub/page.md\tTwo line.\n',
            'hooks.md\tnot there\n', 'no-tab-here\n']
    assert quotes.check_rows(root, rows) == (
        ['FOUND hooks.md:1', 'FOUND sub/page.md:2', 'MISSING hooks.md', 'MISSING no-tab-here'], False)
    assert quotes.check_rows(root, ['hooks.md\tExit 2 blocks\n']) == (['FOUND hooks.md:1'], True)


def test_a_quote_keeps_any_tab_after_the_first(root):
    write_tree(root, {'tabs.md': 'a\tb\n'})
    assert quotes.check_rows(root, ['tabs.md\ta\tb']) == (['FOUND tabs.md:1'], True)


def test_the_cli_exits_one_on_any_miss_and_two_without_a_directory(root, monkeypatch, capsys):
    monkeypatch.setattr('sys.stdin', io.StringIO('hooks.md\tExit 2 blocks\n'))
    assert cli.main(['quotes', '--in', str(root)]) == 0
    assert capsys.readouterr() == ('FOUND hooks.md:1\n', '')
    monkeypatch.setattr('sys.stdin', io.StringIO('hooks.md\tExit 2 blocks\nhooks.md\tExit 3\n'))
    assert cli.main(['quotes', '--in', str(root)]) == 1
    assert capsys.readouterr() == ('FOUND hooks.md:1\nMISSING hooks.md\n', '')
    assert cli.main(['quotes', '--in', str(root / 'nope')]) == 2
    assert capsys.readouterr() == ('', f"cc-guide: {root / 'nope'}: not a directory\n")
