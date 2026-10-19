'''Tests for preflight.py: stdlib and pytest only, no network.

The fetch tests clone a local bare repository through a file:// URL, so that
git applies --depth and --filter as it does against GitHub. PATH holds only a
link to git and a fake quarto, so a test can take Quarto away.
'''
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

import preflight

GIT = shutil.which('git')
QUARTO_VERSION = '1.10.19'
TAG = 'v0.17.0'
STOP_FETCH = 'next: stop: fetching the official skills failed: '


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


def fake_quarto(bin_dir: Path, version: str) -> None:
    quarto = bin_dir / 'quarto'
    quarto.write_text(f'#!/bin/sh\necho {version}\n')
    quarto.chmod(0o755)


@pytest.fixture(autouse=True)
def pkg(tmp_path, monkeypatch):
    '''An empty package root as the working directory, a scratch cache, git
    with no user or system config, and a PATH of git and a fake quarto.'''
    root = tmp_path / 'pkg'
    root.mkdir()
    monkeypatch.chdir(root)
    monkeypatch.setenv('XDG_CACHE_HOME', str(tmp_path / 'cache'))
    (tmp_path / 'gitconfig').write_text('')
    monkeypatch.setenv('GIT_CONFIG_GLOBAL', str(tmp_path / 'gitconfig'))
    monkeypatch.setenv('GIT_CONFIG_NOSYSTEM', '1')
    for role in ('AUTHOR', 'COMMITTER'):
        monkeypatch.setenv(f'GIT_{role}_NAME', 'Test')
        monkeypatch.setenv(f'GIT_{role}_EMAIL', 'test@example.com')
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    (bin_dir / 'git').symlink_to(GIT)
    fake_quarto(bin_dir, QUARTO_VERSION)
    monkeypatch.setenv('PATH', str(bin_dir))
    return root


@pytest.fixture
def bare(tmp_path) -> Path:
    '''A bare repository with an annotated tag v0.17.0 on a tree that holds
    skills/ and one file outside it.'''
    work = tmp_path / 'work'
    (work / 'skills' / 'great-docs').mkdir(parents=True)
    (work / 'skills' / 'great-docs' / 'SKILL.md').write_text('---\nname: great-docs\n---\n')
    (work / 'README.md').write_text('outside skills/\n')
    git('init', '--quiet', '--initial-branch', 'main', cwd=work)
    git('add', '.', cwd=work)
    git('commit', '--quiet', '--message', 'skills', cwd=work)
    git('tag', '--annotate', TAG, '--message', TAG, cwd=work)
    remote = tmp_path / 'remote.git'
    git('clone', '--quiet', '--bare', str(work), str(remote), cwd=tmp_path)
    git('config', 'uploadpack.allowFilter', 'true', cwd=remote)
    return remote


def lock(root: Path, version: str | None) -> None:
    '''Write root/uv.lock; None leaves great-docs out of it.'''
    entries = ['[[package]]\nname = "polars"\nversion = "1.0.0"\n']
    if version is not None:
        entries.append(f'[[package]]\nname = "great-docs"\nversion = "{version}"\n')
    (root / 'uv.lock').write_text('version = 1\n\n' + '\n'.join(entries))


def cache_dir(tmp_path: Path) -> Path:
    return tmp_path / 'cache' / 'agent-skills' / 'great-docs' / '0.17.0'


def report(version: str = 'none', in_range: str = 'none', layout: str = 'none', config: str = 'none',
           quarto: str = QUARTO_VERSION, skills: str = 'none', step: str = 'pin') -> list[str]:
    return [f'great-docs: {version}', 'range: >=0.17.0,<0.18', f'in-range: {in_range}',
            f'layout: {layout}', f'config: {config}', f'quarto: {quarto}', f'skills: {skills}',
            f'next: {step}']


def run(capsys, *argv: str) -> tuple[int, list[str]]:
    code = preflight.main(list(argv))
    return code, capsys.readouterr().out.splitlines()


@pytest.mark.parametrize(('version', 'expected'), [
    ('0.16.9', False), ('0.17.0', True), ('0.17.5', True), ('0.18.0', False),
    ('0.18.0rc1', False), ('0.17.1.dev0', False), ('0.17.1+local', False),
])
def test_only_a_final_release_inside_the_range_passes(version, expected):
    assert preflight.in_range(version) is expected


def test_no_lock_gives_pin(capsys):
    assert run(capsys) == (0, report())


def test_a_lock_without_great_docs_gives_pin(pkg, capsys):
    lock(pkg, None)
    assert run(capsys) == (0, report())


def test_a_version_outside_the_range_stops(pkg, capsys):
    lock(pkg, '0.18.0')
    assert run(capsys) == (1, report(
        version='0.18.0', in_range='no',
        step='stop: great-docs 0.18.0 is outside >=0.17.0,<0.18; pin it back into the range and run uv lock'))


@pytest.mark.parametrize(('files', 'expected'), [
    ([], ('none', [])),
    (['great-docs.yml'], ('root', ['great-docs.yml'])),
    (['docs/great-docs.yml'], ('docs', ['docs/great-docs.yml'])),
    (['great-docs.yml', 'docs/great-docs.yml'], ('both', ['great-docs.yml', 'docs/great-docs.yml'])),
])
def test_the_config_layout(pkg, files, expected):
    for rel in files:
        (pkg / rel).parent.mkdir(parents=True, exist_ok=True)
        (pkg / rel).write_text('parser: numpy\n')
    assert preflight.config_layout(pkg) == expected


@pytest.mark.parametrize(('files', 'layout'), [
    (['docs/great-docs.yml'], 'docs'),
    (['great-docs.yml', 'docs/great-docs.yml'], 'both'),
])
def test_a_docs_or_both_layout_stops_with_the_paths(pkg, capsys, files, layout):
    for rel in files:
        (pkg / rel).parent.mkdir(parents=True, exist_ok=True)
        (pkg / rel).write_text('parser: numpy\n')
    config = ', '.join(files)
    assert run(capsys) == (1, report(
        layout=layout, config=config,
        step=f'stop: config layout {layout} ({config}) is not supported; '
             'great-docs 0.17.x reads great-docs.yml at the project root'))


def test_a_fresh_fetch_writes_source_with_the_tag_commit(pkg, tmp_path, bare, capsys):
    lock(pkg, '0.17.0')
    cache = cache_dir(tmp_path)
    assert run(capsys, '--remote', bare.as_uri()) == (0, report(
        version='0.17.0', in_range='yes', skills=str(cache / 'skills'), step='init'))
    commit = git('rev-parse', f'{TAG}^{{commit}}', cwd=bare)
    assert commit != git('rev-parse', TAG, cwd=bare)  # the tag is annotated
    source = (cache / 'SOURCE').read_text().splitlines()
    assert source[:2] == [f'tag: {TAG}', f'commit: {commit}']
    assert re.fullmatch(r'fetched: \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', source[2])
    assert len(source) == 3
    assert (cache / 'skills' / 'great-docs' / 'SKILL.md').is_file()
    assert sorted(p.name for p in cache.iterdir()) == ['SOURCE', 'skills']


def test_a_complete_cache_is_reused_without_a_clone(pkg, tmp_path, capsys):
    lock(pkg, '0.17.0')
    cache = cache_dir(tmp_path)
    (cache / 'skills').mkdir(parents=True)
    (cache / 'SOURCE').write_text('tag: v0.17.0\ncommit: abc\nfetched: 2026-10-19T00:00:00Z\n')
    unreachable = (tmp_path / 'no-such-remote.git').as_uri()  # a clone would fail
    assert run(capsys, '--remote', unreachable) == (0, report(
        version='0.17.0', in_range='yes', skills=str(cache / 'skills'), step='init'))
    assert (cache / 'SOURCE').read_text().splitlines()[1] == 'commit: abc'


def test_a_failed_clone_leaves_no_cache_folder(pkg, tmp_path, capsys):
    lock(pkg, '0.17.0')
    code, lines = run(capsys, '--remote', (tmp_path / 'no-such-remote.git').as_uri())
    assert code == 1
    assert lines[:-1] == report(version='0.17.0', in_range='yes')[:-1]
    assert lines[-1].startswith(STOP_FETCH)
    assert len(lines[-1]) > len(STOP_FETCH)  # git's error follows
    parent = cache_dir(tmp_path).parent
    assert (list(parent.iterdir()) if parent.exists() else []) == []


def test_a_cache_folder_without_source_is_fetched_again(pkg, tmp_path, bare, capsys):
    lock(pkg, '0.17.0')
    cache = cache_dir(tmp_path)
    cache.mkdir(parents=True)
    (cache / 'partial').write_text('left by an interrupted fetch\n')
    assert run(capsys, '--remote', bare.as_uri())[0] == 0
    assert sorted(p.name for p in cache.iterdir()) == ['SOURCE', 'skills']


def test_a_root_config_with_the_skills_cached_is_ready(pkg, tmp_path, bare, capsys):
    lock(pkg, '0.17.0')
    (pkg / 'great-docs.yml').write_text('parser: numpy\n')
    assert run(capsys, '--remote', bare.as_uri()) == (0, report(
        version='0.17.0', in_range='yes', layout='root', config='great-docs.yml',
        skills=str(cache_dir(tmp_path) / 'skills'), step='ready'))


def test_another_quarto_version_is_reported_and_does_not_stop(tmp_path, capsys):
    fake_quarto(tmp_path / 'bin', '1.9.0')
    assert run(capsys) == (0, report(quarto='1.9.0'))


def test_quarto_missing_stops_with_the_install_page(tmp_path, capsys):
    (tmp_path / 'bin' / 'quarto').unlink()
    assert run(capsys) == (1, report(
        quarto='missing', step='stop: quarto is missing; install it from https://quarto.org/docs/get-started/'))


def test_the_cache_defaults_to_the_home_cache(monkeypatch, tmp_path):
    expected = tmp_path / 'home' / '.cache' / 'agent-skills' / 'great-docs'
    monkeypatch.setenv('HOME', str(tmp_path / 'home'))
    monkeypatch.delenv('XDG_CACHE_HOME')
    assert preflight.cache_root() == expected
    monkeypatch.setenv('XDG_CACHE_HOME', '')
    assert preflight.cache_root() == expected
