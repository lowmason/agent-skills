'''Tests for notice.sh, the drift check's session-start pair (drift spec
R9.2, R9.3, R12.5). Each run is made as Claude Code makes it from an app the
Dock started: no inherited environment, only HOME and launchd's PATH. notice.py
writes the files the script reads, so the shell-and-Python file contract is
tested across the two languages.'''
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import notice

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / 'notice.sh'
REPO = HERE.parents[1]
LAUNCHD_PATH = '/usr/bin:/bin'
SHELLS = [shell for shell in ('/bin/sh', '/bin/dash') if Path(shell).exists()]


def cache_of(home: Path) -> Path:
    return home / '.cache' / 'agent-skills' / 'cc-guide'


def sh(home: Path, *args: str, shell: str = '/bin/sh', env: dict | None = None, timeout: int = 60):
    '''notice.sh under shell with HOME, launchd's PATH and any extra
    variables, from a working directory that is not the script's.'''
    return subprocess.run([shell, str(SCRIPT), *args], env={'HOME': str(home), 'PATH': LAUNCHD_PATH, **(env or {})},
                          cwd=home, capture_output=True, text=True, timeout=timeout)


def shown(proc) -> str:
    '''The systemMessage a show run printed. Its whole stdout must be the
    JSON, and an empty stdout fails (R12.5).'''
    assert (proc.returncode, proc.stderr) == (0, '')
    assert proc.stdout, 'a show that prints nothing cannot pass as a quiet day (R12.5)'
    return json.loads(proc.stdout)['systemMessage']


def quiet(proc) -> None:
    assert (proc.returncode, proc.stdout, proc.stderr) == (0, '', '')


@pytest.mark.parametrize('shell', SHELLS)
def test_show_prints_a_notice_once_a_day_and_a_changed_notice_again(tmp_path, shell):
    notice.write_notice(cache_of(tmp_path), 'cc-guide · first → /cc-guide')
    assert shown(sh(tmp_path, 'show', shell=shell)) == 'cc-guide · first → /cc-guide'
    quiet(sh(tmp_path, 'show', shell=shell))
    notice.write_notice(cache_of(tmp_path), 'cc-guide · second → /cc-guide')
    assert shown(sh(tmp_path, 'show', shell=shell)) == 'cc-guide · second → /cc-guide'
    quiet(sh(tmp_path, 'show', shell=shell))


def test_show_runs_as_the_settings_command_runs_it(tmp_path):
    '''The hook executes the script by path, so its shebang and its execute
    bit run it: env -i, as R12.5 writes it.'''
    notice.write_notice(cache_of(tmp_path), 'cc-guide · direct → /cc-guide')
    proc = subprocess.run(['/usr/bin/env', '-i', f'HOME={tmp_path}', f'PATH={LAUNCHD_PATH}', str(SCRIPT), 'show'],
                          cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert shown(proc) == 'cc-guide · direct → /cc-guide'


def test_a_notice_shown_on_an_earlier_day_shows_again(tmp_path):
    cache = cache_of(tmp_path)
    notice.write_notice(cache, 'cc-guide · again → /cc-guide')
    digest = (cache / notice.DIGEST).read_text().strip()
    (cache / 'notice-shown').write_text(f'2000-01-01 {digest}\n')
    assert shown(sh(tmp_path, 'show')) == 'cc-guide · again → /cc-guide'
    assert (cache / 'notice-shown').read_text() == f"{datetime.now().strftime('%Y-%m-%d')} {digest}\n"


@pytest.mark.parametrize('shell', SHELLS)
def test_show_prints_nothing_before_any_check_or_when_nothing_is_due(tmp_path, shell):
    quiet(sh(tmp_path, 'show', shell=shell))
    notice.write_notice(cache_of(tmp_path), None)
    quiet(sh(tmp_path, 'show', shell=shell))


def test_show_still_prints_when_it_cannot_record_the_day(tmp_path):
    cache = cache_of(tmp_path)
    notice.write_notice(cache, 'cc-guide · stuck → /cc-guide')
    (cache / 'notice-shown').mkdir()
    assert shown(sh(tmp_path, 'show')) == 'cc-guide · stuck → /cc-guide'


@pytest.mark.parametrize('shell', SHELLS)
def test_show_replaces_notice_shown_by_renaming_a_temp_file_in_the_cache(tmp_path, shell):
    '''Each cache file is replaced by mv -f of a hidden temp file in its own directory (the file contract).'''
    cache = cache_of(tmp_path)
    notice.write_notice(cache, 'cc-guide · renamed → /cc-guide')
    stubs = tmp_path / 'stubs'
    stubs.mkdir()
    log = tmp_path / 'mv.log'
    log.touch()
    stub = stubs / 'mv'
    stub.write_text(f'#!/bin/sh\n{{ printf \'%s\\n\' "$@"; echo --; }} >> {log}\nexec /bin/mv "$@"\n')
    stub.chmod(0o755)
    assert shown(sh(tmp_path, 'show', shell=shell, env={'PATH': f'{stubs}:{LAUNCHD_PATH}'})) == 'cc-guide · renamed → /cc-guide'
    calls = log.read_text().split('--\n')[:-1]
    assert len(calls) == 1, 'notice-shown is replaced by exactly one mv'
    args = calls[0].splitlines()
    assert args[-1] == str(cache / 'notice-shown')
    temp = Path(args[-2])
    assert (temp.parent, temp.name[0], temp.suffix) == (cache, '.', '.tmp')
    digest = (cache / notice.DIGEST).read_text().strip()
    assert (cache / 'notice-shown').read_text() == f"{datetime.now().strftime('%Y-%m-%d')} {digest}\n"
    assert not [path for path in cache.iterdir() if path.suffix == '.tmp']


def test_show_without_home_and_an_unknown_subcommand_both_exit_zero(tmp_path):
    quiet(subprocess.run(['/bin/sh', str(SCRIPT), 'show'], env={'PATH': LAUNCHD_PATH}, cwd=tmp_path,
                         capture_output=True, text=True, timeout=60))
    proc = sh(tmp_path, 'bogus')
    assert (proc.returncode, proc.stdout) == (0, '')


NO_UV = 'the drift check cannot run: no uv on PATH, in ~/.local/bin or in /opt/homebrew/bin'
FOUND = 'cc-guide · 1 docs block changed (alpha.overview) → /cc-guide'

# A stand-in for uv. It records how it was called, then finishes as check --hook would
# (through notice.py, so the file contract is the real one), hangs, or fails before Python.
FAKE_UV = '''#!/bin/sh
printf '%s\\n' "$0" > "$HOME/uv-path"
printf '%s\\n' "$@" > "$HOME/uv-args"
env | grep '^GIT_' > "$HOME/uv-git-env"
case "${{FAKE_UV:-finish}}" in
    finish) exec "{python}" "{finish}" "$@" ;;
    hang) exec sleep 30 ;;
    *) exit 2 ;;
esac
'''

FINISH = '''import sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, {here!r})
import notice
run = sys.argv[sys.argv.index('--run') + 1]
cache = Path.home() / '.cache' / 'agent-skills' / 'cc-guide'
notice.write_notice(cache, {found!r})
notice.record_check(cache, 1, datetime.now().astimezone(), run)
'''


@pytest.fixture
def fake_uv(tmp_path):
    '''A HOME, and the variables that put the stand-in uv first on launchd's
    PATH with no fallback directory.'''
    home = tmp_path / 'home'
    home.mkdir()
    finish = tmp_path / 'finish.py'
    finish.write_text(FINISH.format(here=str(HERE), found=FOUND), encoding='utf-8')
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    uv = bin_dir / 'uv'
    uv.write_text(FAKE_UV.format(python=sys.executable, finish=finish))
    uv.chmod(0o755)
    return home, {'PATH': f'{bin_dir}:{LAUNCHD_PATH}', 'CC_GUIDE_UV_FALLBACK': str(tmp_path / 'nowhere')}


@pytest.mark.parametrize('shell', SHELLS)
def test_refresh_runs_check_hook_through_uv_by_absolute_path_and_show_follows(fake_uv, shell):
    home, env = fake_uv
    quiet(sh(home, 'refresh', shell=shell, env=env))
    args = (home / 'uv-args').read_text().splitlines()
    assert args[:-1] == ['run', '--python', '3.13', 'python', str(HERE / 'cli.py'), 'check', '--hook', '--run']
    assert re.fullmatch(r'\d+\.\d+', args[-1])
    cache = cache_of(home)
    assert notice.read_last_check(cache)['run'] == args[-1]
    assert not (cache / 'unfinished').exists()
    assert not (cache / 'lock').exists()
    assert shown(sh(home, 'show', shell=shell)) == FOUND


def test_refresh_waits_a_day_after_a_good_check(fake_uv):
    home, env = fake_uv
    cache = cache_of(home)
    notice.record_check(cache, 0, datetime.now().astimezone() - timedelta(hours=23), 'earlier')
    quiet(sh(home, 'refresh', env=env))
    assert not (home / 'uv-args').exists()
    notice.record_check(cache, 0, datetime.now().astimezone() - timedelta(hours=25), 'earlier')
    quiet(sh(home, 'refresh', env=env))
    assert (home / 'uv-args').exists()


def test_refresh_leaves_a_fresh_lock_alone_and_breaks_one_over_an_hour_old(fake_uv):
    home, env = fake_uv
    lock = cache_of(home) / 'lock'
    lock.mkdir(parents=True)
    quiet(sh(home, 'refresh', env=env))
    assert lock.is_dir()
    assert not (home / 'uv-args').exists()
    old = time.time() - 2 * 3600
    os.utime(lock, (old, old))
    quiet(sh(home, 'refresh', env=env))
    assert (home / 'uv-args').exists()
    assert not lock.exists()


def test_refresh_looks_in_each_fallback_directory_in_order(fake_uv, tmp_path):
    home, env = fake_uv
    stand_in = Path(env['PATH'].split(':')[0]) / 'uv'
    first, second = tmp_path / 'first', tmp_path / 'second'
    second.mkdir()
    (second / 'uv').write_bytes(stand_in.read_bytes())
    (second / 'uv').chmod(0o755)
    quiet(sh(home, 'refresh', env={'CC_GUIDE_UV_FALLBACK': f'{first}:{second}'}))
    assert (home / 'uv-path').read_text().strip() == str(second / 'uv')


def test_refresh_without_uv_leaves_the_fixed_error_notice(fake_uv):
    home, _ = fake_uv
    notice.record_check(cache_of(home), 1, datetime.now().astimezone() - timedelta(days=2, hours=1), 'old')
    quiet(sh(home, 'refresh', env={'CC_GUIDE_UV_FALLBACK': str(home / 'nowhere')}))
    assert shown(sh(home, 'show')) == f'cc-guide · {NO_UV} · last good check 2 d ago → install uv'


def test_refresh_stops_a_check_past_its_budget_and_counts_the_run_unfinished(fake_uv):
    home, env = fake_uv
    started = time.monotonic()
    quiet(sh(home, 'refresh', env={**env, 'FAKE_UV': 'hang', 'CC_GUIDE_BUDGET': '1'}))
    assert time.monotonic() - started < 10
    cache = cache_of(home)
    assert (cache / 'unfinished').read_text() == '1\n'
    assert not (cache / notice.NOTICE).exists()


def test_three_unfinished_runs_in_a_row_leave_the_error_notice_and_a_finished_run_clears_them(fake_uv):
    home, env = fake_uv
    cache = cache_of(home)
    for count in (1, 2):
        quiet(sh(home, 'refresh', env={**env, 'FAKE_UV': 'fail'}))
        assert (cache / 'unfinished').read_text() == f'{count}\n'
        assert not (cache / notice.NOTICE).exists()
    quiet(sh(home, 'refresh', env={**env, 'FAKE_UV': 'fail'}))
    assert shown(sh(home, 'show')) == ('cc-guide · the drift check did not finish 3 times in a row · '
                                       'no good check yet → run build/cc_guide/cli.py check')
    quiet(sh(home, 'refresh', env=env))
    assert not (cache / 'unfinished').exists()
    assert shown(sh(home, 'show')) == FOUND


def test_refresh_runs_the_check_without_the_callers_git_variables(fake_uv):
    '''Deferred item "check's report and inputs", part b: a caller's GIT_DIR
    or GIT_INDEX_FILE would point check's git reads somewhere else.'''
    home, env = fake_uv
    quiet(sh(home, 'refresh', env={**env, 'GIT_DIR': '/nonexistent', 'GIT_INDEX_FILE': '/nonexistent/index'}))
    assert (home / 'uv-git-env').read_text() == ''


def test_refresh_replaces_unfinished_by_renaming_a_temp_file_in_the_cache(fake_uv, tmp_path):
    '''refresh replaces unfinished by mv -f of a hidden temp file in the cache (the file contract).'''
    home, env = fake_uv
    cache = cache_of(home)
    stubs = tmp_path / 'stubs'
    stubs.mkdir()
    log = tmp_path / 'mv.log'
    log.touch()
    stub = stubs / 'mv'
    stub.write_text(f'#!/bin/sh\n{{ printf \'%s\\n\' "$@"; echo --; }} >> {log}\nexec /bin/mv "$@"\n')
    stub.chmod(0o755)
    path = env['PATH']
    quiet(sh(home, 'refresh', env={**env, 'PATH': f'{stubs}:{path}', 'FAKE_UV': 'fail'}))
    calls = [call.splitlines() for call in log.read_text().split('--\n')[:-1]]
    onto = [args for args in calls if args[-1] == str(cache / 'unfinished')]
    assert len(onto) == 1, 'unfinished is replaced by exactly one mv'
    temp = Path(onto[0][-2])
    assert (temp.parent, temp.name[0], temp.suffix) == (cache, '.', '.tmp')
    assert (cache / 'unfinished').read_text() == '1\n'
    assert not [entry for entry in cache.iterdir() if entry.suffix == '.tmp']
