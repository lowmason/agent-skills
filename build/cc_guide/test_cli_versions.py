'''Tests for cli_versions.py: each stamped guide's cli-stamp line against the
--version of the CLI installed here (owner design, 2026-11-12).'''
import os
import stat
from pathlib import Path

import pytest

import cli_versions
from cc_fixtures import fixture_repo, git, write_tree
from state import Source

REPO = Path(__file__).resolve().parents[2]
(CODEX, CODEX_GUIDE), (AGY, AGY_GUIDE) = cli_versions.GUIDES


def guide(cli: str, version: str) -> str:
    return f'# A guide\n\n<!-- cli-stamp: {cli} {version} -->\n> Checked with {cli} {version}.\n'


def fake(outputs: dict):
    '''A version_text seam: the output for each CLI, None for one not on
    PATH, or a CliError to raise. Any other CLI fails the test.'''
    def version_text(cli: str) -> str | None:
        out = outputs[cli]
        if isinstance(out, cli_versions.CliError):
            raise out
        return out
    return version_text


@pytest.mark.parametrize('text, found', [
    ('<!-- cli-stamp: agy 1.5.7 -->\n', '1.5.7'),
    ('# Title\n\n<!-- cli-stamp: agy 1.5.7 -->\n> prose\n', '1.5.7'),
    ('<!-- cli-stamp: codex 0.167.2 -->\n', None),     # another CLI's stamp
    ('<!-- cli-stamp: agy 1.5 -->\n', None),           # not three parts
    ('Checked with agy 1.5.7.\n', None),               # prose is not a stamp
    ('`<!-- cli-stamp: agy 1.5.7 -->`\n', None),       # quoted, not on a line of its own
])
def test_the_stamp_is_a_line_of_its_own_naming_the_cli_and_a_three_part_version(text, found):
    assert cli_versions.read_stamp(text, 'agy') == found


@pytest.mark.parametrize('output, version', [
    ('codex-cli 0.163.0\n', '0.163.0'),
    ('1.5.7\n', '1.5.7'),
    ('agy version 1.10.2 (build abc)\n', '1.10.2'),
    ('unknown\n', None),
])
def test_the_installed_version_is_the_first_three_part_version_in_the_output(output, version):
    assert cli_versions.parse_version(output) == version


@pytest.mark.parametrize('stamped, installed, behind', [
    ('1.5.7', '1.5.7', False),
    ('1.5.7', '1.5.8', False),       # a patch release does not count
    ('1.5.7', '1.6.0', True),
    ('1.5.7', '2.0.0', True),
    ('0.167.2', '0.163.0', False),   # installed older than the guide
    ('0.167.2', '0.168.0', True),
    ('0.99.0', '0.100.0', True),     # compared as numbers, not as text
])
def test_a_guide_is_behind_when_the_installed_major_minor_is_newer(stamped, installed, behind):
    assert cli_versions.is_behind(stamped, installed) is behind


def stamped_repo(tmp_path, files: dict):
    return Source(fixture_repo(tmp_path / 'repo', files), 'main')


def test_statuses_compare_each_guide_with_its_cli(tmp_path):
    source = stamped_repo(tmp_path, {CODEX_GUIDE: guide(CODEX, '0.167.2'), AGY_GUIDE: guide(AGY, '1.5.7')})
    got = cli_versions.statuses(source, fake({CODEX: 'codex-cli 0.163.0\n', AGY: '1.6.0\n'}))
    assert got == [cli_versions.Status(CODEX, '0.167.2', '0.163.0', None),
                   cli_versions.Status(AGY, '1.5.7', '1.6.0', None)]
    assert [s.behind for s in got] == [False, True]


def test_stamps_are_read_where_the_source_reads_not_from_the_working_tree(tmp_path):
    source = stamped_repo(tmp_path, {CODEX_GUIDE: guide(CODEX, '0.167.2'), AGY_GUIDE: guide(AGY, '1.5.7')})
    write_tree(source.repo, {AGY_GUIDE: guide(AGY, '1.6.0')})  # restamped, not committed
    got = cli_versions.statuses(source, fake({CODEX: '0.167.2', AGY: '1.6.0'}))
    assert got[1].stamped == '1.5.7' and got[1].behind
    git(source.repo, 'commit', '-qam', 'restamp')
    assert not cli_versions.statuses(source, fake({CODEX: '0.167.2', AGY: '1.6.0'}))[1].behind


def test_a_cli_that_cannot_be_compared_is_skipped_with_the_reason(tmp_path):
    source = stamped_repo(tmp_path, {CODEX_GUIDE: guide(CODEX, '0.167.2'), AGY_GUIDE: guide(AGY, '1.5.7')})
    got = cli_versions.statuses(source, fake({CODEX: None, AGY: cli_versions.CliError('agy --version exited 3')}))
    assert got == [cli_versions.Status(CODEX, '0.167.2', None, 'codex not found on PATH'),
                   cli_versions.Status(AGY, '1.5.7', None, 'agy --version exited 3')]
    got = cli_versions.statuses(source, fake({CODEX: 'unknown', AGY: '1.5.7'}))
    assert got[0] == cli_versions.Status(CODEX, '0.167.2', None, 'no version in the output of codex --version')
    assert not any(s.behind for s in got)


def test_a_guide_without_a_stamp_is_skipped_and_its_cli_never_runs(tmp_path):
    source = stamped_repo(tmp_path, {AGY_GUIDE: '# A guide with no stamp\n'})
    got = cli_versions.statuses(source, fake({}))  # any call raises KeyError
    assert got == [cli_versions.Status(CODEX, None, None, f'no cli-stamp line for codex in {CODEX_GUIDE}'),
                   cli_versions.Status(AGY, None, None, f'no cli-stamp line for agy in {AGY_GUIDE}')]


def test_the_summary_line_and_the_notice_part():
    behind = cli_versions.Status(AGY, '1.5.7', '1.6.0', None)
    assert behind.line() == 'agy guide: stamped 1.5.7, installed 1.6.0, behind'
    assert behind.part() == 'agy guide 1.5.7, installed 1.6.0'
    current = cli_versions.Status(CODEX, '0.167.2', '0.163.0', None)
    assert current.line() == 'codex guide: stamped 0.167.2, installed 0.163.0, current'
    assert cli_versions.Status(CODEX, '0.167.2', None, 'codex not found on PATH').line() == (
        'codex guide: stamped 0.167.2; skipped: codex not found on PATH')
    assert cli_versions.Status(CODEX, None, None, 'no stamp').line() == 'codex guide: skipped: no stamp'


def script(folder: Path, name: str, body: str) -> None:
    path = folder / name
    path.write_text(f'#!/bin/sh\n{body}\n', encoding='utf-8')
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_run_version_runs_the_cli_on_path_and_reports_how_it_failed(tmp_path, monkeypatch):
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    script(bin_dir, 'goodcli', 'read -r line; echo "goodcli $1 1.2.3 ${line:-no-stdin}"')
    script(bin_dir, 'badcli', 'echo oops >&2; exit 3')
    script(bin_dir, 'slowcli', 'sleep 5')
    monkeypatch.setenv('PATH', os.pathsep.join([str(bin_dir), '/usr/bin', '/bin']))  # sleep for slowcli
    monkeypatch.setattr(cli_versions, 'TIMEOUT', 0.5)
    assert cli_versions.run_version('goodcli') == 'goodcli --version 1.2.3 no-stdin\n'  # stdin is empty
    assert cli_versions.run_version('missingcli') is None
    with pytest.raises(cli_versions.CliError, match=r'^badcli --version exited 3: oops$'):
        cli_versions.run_version('badcli')
    with pytest.raises(cli_versions.CliError, match=r'^slowcli --version timed out after 0.5 s$'):
        cli_versions.run_version('slowcli')


@pytest.mark.parametrize('cli, path', cli_versions.GUIDES)
def test_each_guide_carries_its_stamp_and_its_header_names_the_same_version(cli, path):
    '''A refresh that restamps the header prose must restamp the line too.'''
    text = (REPO / path).read_text(encoding='utf-8')
    version = cli_versions.read_stamp(text, cli)
    assert version is not None, f'{path}: no cli-stamp line for {cli}'
    lines = text.splitlines()
    after = lines[lines.index(f'<!-- cli-stamp: {cli} {version} -->') + 1:]
    header = next(line for line in after if line.startswith('> '))
    assert version in header, f'{path}: the header after the stamp does not name {version}'
