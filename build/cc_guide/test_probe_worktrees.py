'''Tests for probe_worktrees.py: the scratch repos worktree-isolation builds, the four claude -p command lines it
runs in them, and the sightings its collect step writes (deferred item R122). The repos are real git repos under
tmp_path, built with no global or system git config; no test runs claude or spends a token.'''
import json
import os
import subprocess
from pathlib import Path

import pytest

import probe_checks as pc
import probe_process
import probe_worktrees as pw
import test_probe_checks as tpc
from cc_fixtures import isolated_home  # noqa: F401
from state import ERROR, PASS, SetupError

CLAUDE = '/bin/claude-stub'
REPO = Path(__file__).resolve().parents[2]
NAMES = ('isolation', 'noop', 'base-no-remote', 'base-failed-fetch')
CWDS = {'isolation': 'iso', 'noop': 'plain-wt', 'base-no-remote': 'norem', 'base-failed-fetch': 'gone'}
ENV = {'CLAUDE_CODE_DISABLE_ADVISOR_TOOL': '1', 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}
ALLOW = ['Bash', 'ExitWorktree', 'EnterWorktree', 'ToolSearch']


def git_out(repo: Path, *args: str) -> subprocess.CompletedProcess:
    '''git in a built repo with no global or system config and none of the caller's GIT_ variables.'''
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env |= {'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}
    return subprocess.run(['git', *args], cwd=repo, env=env, capture_output=True, text=True)


@pytest.fixture
def built(tmp_path):
    scratch = tmp_path / 'scratch'
    scratch.mkdir()
    return scratch, pw.prepare_worktrees(scratch, CLAUDE, REPO)


def by_name(invocations):
    return {inv.name: inv for inv in invocations}


def prompt_of(inv) -> str:
    return inv.argv[1]


def in_order(text: str, parts) -> bool:
    '''Whether each part appears in text after the one before it.'''
    at = 0
    for part in parts:
        found = text.find(part, at)
        if found < 0:
            return False
        at = found + len(part)
    return True


def test_prepare_builds_the_four_repos_and_their_invocations(built):
    scratch, invocations = built
    runs = by_name(invocations)
    assert [inv.name for inv in invocations] == list(NAMES)
    assert {name: inv.cwd for name, inv in runs.items()} == CWDS
    for name, inv in runs.items():
        assert (scratch / inv.cwd).is_dir()
        assert inv.argv[0] == CLAUDE
        assert (inv.env, inv.timeout, inv.suffix) == (ENV, probe_process.PROBE_TIMEOUT, '.jsonl')
        argv = inv.argv
        assert argv[argv.index('--max-turns') + 1] == '20'
        assert argv[argv.index('--setting-sources') + 1] == 'project'
        assert argv[argv.index('--max-budget-usd') + 1] == probe_process.BUDGET_USD
        assert json.loads(argv[argv.index('--settings') + 1]) == {
            'permissions': {'defaultMode': 'default', 'allow': ALLOW}}
        assert '--strict-mcp-config' in argv
        assert ('--worktree' in argv) == (name == 'isolation')
    isolation = runs['isolation'].argv
    assert isolation[isolation.index('--worktree') + 1] == 'probe'
    main_git = pc.WT_MAIN_GIT.format(main=pw.worktree_places(scratch)[pc.WT_MAIN])
    assert main_git == f'git -C {scratch / "iso"} rev-parse --show-toplevel'
    assert in_order(prompt_of(runs['isolation']), [
        pc.WT_CONTROL, main_git, pc.WT_GIT_SUBSHELL, pc.WT_PLAIN_SUBSHELL, pc.WT_LIST, 'ExitWorktree',
        'action keep', pc.WT_PWD, main_git, pc.WT_LIST, 'DONE'])
    assert in_order(prompt_of(runs['noop']), ['ExitWorktree', 'action keep', pc.WT_PWD, 'DONE'])
    for name in ('base-no-remote', 'base-failed-fetch'):
        assert in_order(prompt_of(runs[name]), ['EnterWorktree', 'name probe', pc.WT_LOG, 'DONE'])
        assert 'ExitWorktree' not in prompt_of(runs[name])
    assert prompt_of(runs['base-no-remote']) == prompt_of(runs['base-failed-fetch'])
    for inv in invocations:
        text = prompt_of(inv)
        assert 'exactly as written' in text and 'ToolSearch' in text and 'one call' in text
        assert 'with the Bash tool' in text and 'do not retry a command in another form' in text


def test_the_repos_hold_what_each_run_reads(built):
    scratch, _ = built
    iso, plain_wt, norem, gone = (scratch / name for name in ('iso', 'plain-wt', 'norem', 'gone'))
    assert git_out(iso, 'symbolic-ref', 'refs/remotes/origin/HEAD').stdout.strip() == 'refs/remotes/origin/main'
    assert git_out(iso, 'rev-parse', 'HEAD').stdout == git_out(iso, 'rev-parse', 'origin/main').stdout
    listed = git_out(scratch / 'plain', 'worktree', 'list', '--porcelain').stdout
    worktrees = {os.path.realpath(line.removeprefix('worktree ')) for line in listed.splitlines()
                 if line.startswith('worktree ')}
    assert os.path.realpath(plain_wt) in worktrees
    assert git_out(norem, 'remote').stdout == ''
    assert git_out(norem, 'log', '--format=%s').stdout.splitlines() == [pc.WT_UNPUSHED, pc.WT_PUSHED]
    assert git_out(gone, 'log', '--format=%s').stdout.splitlines() == [pc.WT_UNPUSHED, pc.WT_PUSHED]
    assert git_out(gone, 'log', '--format=%s', 'refs/remotes/origin/main').stdout.splitlines() == [pc.WT_PUSHED]


def test_the_failed_fetch_repo_meets_its_preconditions(built):
    scratch, _ = built
    gone = scratch / 'gone'
    assert git_out(gone, 'symbolic-ref', '-q', 'refs/remotes/origin/HEAD').returncode != 0
    assert git_out(gone, 'rev-parse', '--verify', 'refs/remotes/origin/main').returncode == 0
    assert git_out(gone, 'fetch', 'origin').returncode != 0
    assert not (scratch / 'gone-origin.git').exists()


def test_a_failed_fetch_repo_that_still_fetches_is_a_setup_error(tmp_path, monkeypatch):
    monkeypatch.setattr(pw.shutil, 'rmtree', lambda path, **kw: None)
    with pytest.raises(SetupError, match='fetch'):
        pw.prepare_worktrees(tmp_path, CLAUDE, REPO)


def test_a_failed_fetch_repo_with_an_origin_head_is_a_setup_error(tmp_path, monkeypatch):
    real = pw.git

    def also_set_head(args, cwd):
        real(args, cwd)
        if Path(cwd).name == 'gone' and args[:1] == ['push']:
            real(['remote', 'set-head', 'origin', 'main'], cwd)
    monkeypatch.setattr(pw, 'git', also_set_head)
    with pytest.raises(SetupError, match='origin/HEAD'):
        pw.prepare_worktrees(tmp_path, CLAUDE, REPO)


def test_a_failed_fetch_repo_without_its_remote_branch_is_a_setup_error(tmp_path, monkeypatch):
    real = pw.git

    def drop_branch(args, cwd):
        real(args, cwd)
        if Path(cwd).name == 'gone' and args[:1] == ['push']:
            real(['update-ref', '-d', 'refs/remotes/origin/main'], cwd)
    monkeypatch.setattr(pw, 'git', drop_branch)
    with pytest.raises(SetupError, match='origin/main'):
        pw.prepare_worktrees(tmp_path, CLAUDE, REPO)


def test_a_failed_git_command_is_a_setup_error_naming_it(tmp_path):
    with pytest.raises(SetupError, match='git rev-parse --verify no-such-ref'):
        pw.git(['rev-parse', '--verify', 'no-such-ref'], tmp_path)


def test_the_setup_git_ignores_the_callers_global_config(tmp_path, isolated_home):
    '''Review Focus 2: signing, another default branch and failing hooks in the caller's global config change
    nothing, since setup git reads no global or system config.'''
    hooks = isolated_home / 'hooks'
    hooks.mkdir()
    for hook in ('pre-commit', 'pre-push', 'post-checkout'):
        (hooks / hook).write_text('#!/bin/sh\nexit 1\n', encoding='utf-8')
        (hooks / hook).chmod(0o755)
    (isolated_home / '.gitconfig').write_text(
        f'[commit]\n\tgpgsign = true\n[init]\n\tdefaultBranch = trunk\n[core]\n\thooksPath = {hooks}\n',
        encoding='utf-8')
    pw.prepare_worktrees(tmp_path, CLAUDE, REPO)
    assert git_out(tmp_path / 'norem', 'branch', '--show-current').stdout.strip() == 'main'


def test_the_setup_git_ignores_an_inherited_git_dir(tmp_path, monkeypatch):
    '''A commit hook exports GIT_DIR and GIT_INDEX_FILE for the repo being committed; setup must not write there.'''
    monkeypatch.setenv('GIT_DIR', str(tmp_path / 'elsewhere.git'))
    monkeypatch.setenv('GIT_INDEX_FILE', str(tmp_path / 'elsewhere.index'))
    pw.prepare_worktrees(tmp_path, CLAUDE, REPO)
    assert not (tmp_path / 'elsewhere.git').exists() and not (tmp_path / 'elsewhere.index').exists()


def test_each_run_loads_project_settings_only(built):
    '''Review Focus 3: a worktree.baseRef in the owner's user settings cannot decide fact 4, since each run loads
    project settings only and no scratch repo has any.'''
    scratch, invocations = built
    for inv in invocations:
        assert inv.argv[inv.argv.index('--setting-sources') + 1] == 'project'
    assert not list(scratch.rglob('settings.json')) and not list(scratch.rglob('settings.local.json'))


def write_streams(run_dir: Path, streams: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    for part, events in streams.items():
        (run_dir / f'{part}.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events), encoding='utf-8')


def test_collect_and_assess_read_a_run_like_a_live_one(tmp_path):
    scratch, run_dir = tmp_path / 'scratch', tmp_path / 'run'
    places = pw.worktree_places(scratch)
    assert places == {pc.WT_MAIN: str(scratch / 'iso'), 'worktree': str(scratch / 'iso' / '.claude' / 'worktrees'
                                                                          / 'probe'),
                      pc.WT_PLAIN: str(scratch / 'plain-wt')}
    write_streams(run_dir, tpc.wt_streams(places))
    pw.collect_worktrees(scratch, run_dir)
    text = (run_dir / 'worktrees.json').read_text(encoding='utf-8')
    assert str(scratch) not in text and str(tmp_path) not in text
    assert json.loads(text) == pc.worktree_sightings(tpc.wt_streams(places), places)
    assert pw.assess_worktrees(lambda name: text if name == 'worktrees.json' else None) == (PASS, pc.WT_FINDING)


def test_collect_reads_a_missing_stream_as_a_broken_run(tmp_path):
    scratch, run_dir = tmp_path / 'scratch', tmp_path / 'run'
    streams = tpc.wt_streams(pw.worktree_places(scratch))
    del streams['noop']
    write_streams(run_dir, streams)
    pw.collect_worktrees(scratch, run_dir)
    verdict = pw.assess_worktrees(lambda name: (run_dir / name).read_text(encoding='utf-8'))
    assert verdict.outcome == ERROR and verdict.finding.startswith('noop: the run broke')


def test_a_missing_sightings_file_is_an_error():
    verdict = pw.assess_worktrees(lambda name: None)
    assert verdict.outcome == ERROR and 'worktrees.json' in verdict.finding


def test_the_probe_saves_its_sightings_as_one_fixture():
    probe = pw.WORKTREE_PROBE
    assert isinstance(probe, probe_process.Probe)
    assert (probe.prepare, probe.collect, probe.assess) == (pw.prepare_worktrees, pw.collect_worktrees,
                                                            pw.assess_worktrees)
    assert probe.fixtures == {'worktrees.json': 'worktree-isolation.sightings.json'}
    assert not probe.reads_commands
