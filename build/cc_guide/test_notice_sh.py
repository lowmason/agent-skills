'''Tests for notice.sh, the drift check's session-start pair (drift spec
R9.2, R9.3, R12.5). Each run is made as Claude Code makes it from an app the
Dock started: no inherited environment, only HOME and launchd's PATH. notice.py
writes the files the script reads, so the shell-and-Python file contract is
tested across the two languages.'''
import json
import subprocess
from datetime import datetime
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
