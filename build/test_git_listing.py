'''Tests for build/git_listing.py, the git helpers that run_suites.py, check_conformance.py and
versions_check.py share.'''
import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

import git_listing
from git_listing import GitError, git_env, git_reason, kept_paths


@pytest.fixture(autouse=True)
def isolated_git_config(monkeypatch):
    monkeypatch.setenv('GIT_CONFIG_GLOBAL', os.devnull)
    monkeypatch.setenv('GIT_CONFIG_NOSYSTEM', '1')


def run_git(root, *args):
    subprocess.run(['git', *args], cwd=root, env=git_env(), check=True, capture_output=True)


def make_repo(root, files):
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        (root / rel).write_text(text)
    run_git(root, 'init', '-q')
    return root


def test_git_env_drops_repo_local_variables(monkeypatch):
    monkeypatch.setenv('GIT_DIR', '/nowhere')
    monkeypatch.setenv('GIT_INDEX_FILE', '/nowhere/index')
    monkeypatch.setenv('LANE3_KEEP', 'yes')
    env = git_env()
    assert env['LANE3_KEEP'] == 'yes'
    assert 'GIT_DIR' not in env
    assert 'GIT_INDEX_FILE' not in env


def test_git_reason_prefers_gits_stderr():
    assert git_reason(subprocess.CalledProcessError(128, ['git'], stderr=b'fatal: x\n')) == 'fatal: x'
    assert git_reason(OSError('no git')) == 'no git'


def test_kept_paths_lists_tracked_untracked_and_deleted_but_not_ignored(tmp_path):
    root = make_repo(tmp_path / 'repo', {'a.md': 'a', 'gone.md': 'g', '.gitignore': '*.log\n'})
    run_git(root, 'add', 'a.md', 'gone.md', '.gitignore')
    run_git(root, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '-m', 'init')
    (root / 'gone.md').unlink()
    (root / 'b.md').write_text('b')
    (root / 'c.log').write_text('c')
    assert sorted(kept_paths(root)) == ['.gitignore', 'a.md', 'b.md', 'gone.md']


def test_kept_paths_ignores_a_foreign_git_dir(tmp_path, monkeypatch):
    root = make_repo(tmp_path / 'repo', {'a.md': 'a'})
    other = make_repo(tmp_path / 'other', {'z.md': 'z'})
    monkeypatch.setenv('GIT_DIR', str(other / '.git'))
    monkeypatch.setenv('GIT_INDEX_FILE', str(other / '.git' / 'index'))
    assert kept_paths(root) == ['a.md']


def test_kept_paths_outside_a_repo_raises_with_gits_reason(tmp_path, monkeypatch):
    monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path.parent))
    monkeypatch.setenv('LC_ALL', 'C')
    with pytest.raises(GitError, match='not a git repository'):
        kept_paths(tmp_path)


def test_kept_paths_without_git_raises(tmp_path, monkeypatch):
    root = make_repo(tmp_path / 'repo', {'a.md': 'a'})
    empty = tmp_path / 'empty'
    empty.mkdir()
    monkeypatch.setenv('PATH', str(empty))
    with pytest.raises(GitError):
        kept_paths(root)


def test_the_module_imports_only_the_standard_library():
    tree = ast.parse(Path(git_listing.__file__).read_text(encoding='utf-8'))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {alias.name.split('.')[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names.add(node.module.split('.')[0])
    assert names
    assert names <= sys.stdlib_module_names


def test_kept_paths_decodes_with_fsdecode(tmp_path, monkeypatch):
    listing = b'a.md\0caf\xe9.md\0'
    monkeypatch.setattr(git_listing, 'git_env', dict)
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=listing))
    assert kept_paths(tmp_path) == ['a.md', os.fsdecode(b'caf\xe9.md')]


def test_kept_paths_ignores_a_foreign_index_that_tracks_other_files(tmp_path, monkeypatch):
    root = make_repo(tmp_path / 'repo', {'a.md': 'a'})
    other = make_repo(tmp_path / 'other', {'z.md': 'z'})
    run_git(other, 'add', 'z.md')
    monkeypatch.setenv('GIT_DIR', str(other / '.git'))
    monkeypatch.setenv('GIT_INDEX_FILE', str(other / '.git' / 'index'))
    assert kept_paths(root) == ['a.md']
