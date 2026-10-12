'''Tests for the commit-lint runner, its pre-commit hook and its CI workflow.

Each hook test clones this repository's HEAD into a temporary directory,
copies in the working-tree runner and hook (so the tests exercise the files
under edit), points core.hooksPath at the hook, and commits. Each clone runs
the full lint set, so this file takes about a minute.
'''
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RUNNER = Path('build/run_commit_lints.sh')
HOOK = Path('build/githooks/pre-commit')
GENERATED = Path('runtimes/gemini/agents/code-reviewer.md')
CHECKS = {'check_frontmatter', 'check_provenance', 'check_snippets',
          'check_conformance', 'declared_dependencies', 'sync_runtime_assets'}


def clean_env(**extra):
    '''os.environ without git's GIT_* variables, plus extra.'''
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(extra)
    return env


def git(repo, *args, env=None, check=True):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                          text=True, env=env or clean_env(), check=check)


def head(repo):
    return git(repo, 'rev-parse', 'HEAD').stdout.strip()


def commit(repo, *args, env=None):
    return git(repo, 'commit', '--quiet', *args, env=env, check=False)


def failed_names(result):
    '''The check names on the runner's `commit lints failed:` line; empty if none.

    The runner echoes `== <name>` for every check it runs, so matching a name
    anywhere in the output cannot tell a failed check from one that passed.
    '''
    match = re.search(r'^commit lints failed: (.*)$', result.stderr, re.MULTILINE)
    return set(match.group(1).split()) if match else set()


def no_uv_path(tmp_path):
    '''A PATH directory holding git and bash but not uv.'''
    bindir = tmp_path / 'bin'
    bindir.mkdir()
    for tool in ('git', 'bash'):
        (bindir / tool).symlink_to(shutil.which(tool))
    return str(bindir)


@pytest.fixture
def clone(tmp_path):
    dst = tmp_path / 'repo'
    subprocess.run(['git', 'clone', '--quiet', '--no-checkout', str(REPO), str(dst)],
                   check=True, env=clean_env())
    git(dst, 'checkout', '--quiet', head(REPO))
    for rel in (RUNNER, HOOK):
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, dst / rel)
    git(dst, 'config', 'user.name', 'lint-test')
    git(dst, 'config', 'user.email', 'lint-test@example.invalid')
    git(dst, 'config', 'core.hooksPath', 'build/githooks')
    return dst


def test_runner_and_hook_are_executable():
    assert os.access(REPO / RUNNER, os.X_OK)
    assert os.access(REPO / HOOK, os.X_OK)


def test_clean_commit_passes(clone):
    before = head(clone)
    result = commit(clone, '--allow-empty', '-m', 'clean')
    assert result.returncode == 0, result.stdout + result.stderr
    assert head(clone) != before


def test_frontmatter_violation_is_refused(clone):
    skill = clone / 'skills' / 'explore-data' / 'SKILL.md'
    text = skill.read_text()
    skill.write_text(re.sub(r'^description:.*$', 'description: ""', text,
                            count=1, flags=re.MULTILINE))
    before = head(clone)
    result = commit(clone, '-am', 'bad frontmatter')
    assert result.returncode != 0
    assert head(clone) == before
    assert 'check_frontmatter' in failed_names(result), result.stderr


def test_runtimes_hand_edit_is_refused(clone):
    target = clone / GENERATED
    target.write_text(target.read_text() + '\nhand edit\n')
    before = head(clone)
    result = commit(clone, '-am', 'hand edit')
    assert result.returncode != 0
    assert head(clone) == before
    assert 'sync_runtime_assets' in failed_names(result), result.stderr


def test_hook_fails_open_without_uv(clone, tmp_path):
    env = clean_env(PATH=no_uv_path(tmp_path))
    before = head(clone)
    result = commit(clone, '--allow-empty', '-m', 'no uv', env=env)
    assert result.returncode == 0, result.stderr
    assert head(clone) != before
    assert 'commit lints skipped' in result.stderr


def test_runner_fails_closed_without_uv(clone, tmp_path):
    env = clean_env(PATH=no_uv_path(tmp_path))
    result = subprocess.run(['bash', str(clone / RUNNER)], cwd=clone,
                            capture_output=True, text=True, env=env)
    assert result.returncode != 0
    assert failed_names(result) == CHECKS, result.stderr
