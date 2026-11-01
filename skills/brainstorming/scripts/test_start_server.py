"""Tests for the visual companion's start-server.sh — run from this directory.

cd skills/brainstorming/scripts && uv run --with pytest python -m pytest -q

The tests drive the script as a bash subprocess. The option cases never reach
node. The relative project dir case starts a real server and stops it again.
Skips when node is not on PATH.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

START = Path(__file__).resolve().parent / 'start-server.sh'
STOP = Path(__file__).resolve().parent / 'stop-server.sh'
NODE = shutil.which('node')

needs_node = pytest.mark.skipif(NODE is None, reason='node is not on PATH')


@pytest.mark.parametrize('option', ['--project-dir', '--host', '--url-host', '--idle-timeout-minutes'])
def test_value_option_without_a_value_exits_with_an_error(option):
    proc = subprocess.run(['bash', str(START), option], capture_output=True, text=True, timeout=10)
    assert proc.returncode == 1
    assert json.loads(proc.stdout)['error'] == f'{option} needs a value'


@needs_node
def test_relative_project_dir_starts_the_server_under_it(tmp_path):
    proc = subprocess.run(['bash', str(START), '--project-dir', 'proj', '--idle-timeout-minutes', '1'],
                          cwd=tmp_path, capture_output=True, text=True, timeout=30)
    try:
        assert proc.returncode == 0, proc.stdout
        info = json.loads(proc.stdout.strip().splitlines()[-1])
        state = Path(info['state_dir'])
        assert state.is_absolute()
        assert state.resolve().is_relative_to((tmp_path / 'proj' / '.brainstorm').resolve())
        assert (state / 'server.log').is_file()
    finally:
        for state in (tmp_path / 'proj' / '.brainstorm').glob('*/state'):
            subprocess.run(['bash', str(STOP), str(state.parent)], capture_output=True, timeout=10)
