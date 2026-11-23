'''Self-test for plan 106's micro-test kit: the runner, the reader and the panel on a stub claude.

A stub `claude` (a script first on PATH) prints one JSON object, and the kit's real files run on it.
No model runs. The tests pin the next-kit fixes: every rep and vote JSON passes through
postprocess(), so a kept file holds no `origin` and no `credential_expires_at`, and a rep or vote
that a peer message reached is void, with none of its text kept.
'''
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import panel

KIT = Path(__file__).resolve().parent
CLEAN = {'type': 'result', 'is_error': False, 'num_turns': 1, 'result': 'ok', 'result_index': 0,
         'origin': None, 'credential_expires_at': 1790000000, 'total_cost_usd': 0.01,
         'usage': {'credential_expires_at': 1790000000, 'iterations': []},
         'modelUsage': {'claude-opus-5-5': {}}}
PEER = {**CLEAN, 'result': 'a reply to peer-title-x', 'result_index': 1,
        'origin': {'kind': 'peer', 'title': 'peer-title-x'}}


def stub_dir(tmp_path: Path, stdout: str) -> Path:
    '''Write a `claude` stub that ignores its arguments and stdin and prints stdout.'''
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    stub = bin_dir / 'claude'
    stub.write_text(f"#!/bin/bash\ncat > /dev/null\ncat <<'STUB_EOF'\n{stdout}\nSTUB_EOF\n")
    stub.chmod(0o755)
    return bin_dir


def run_reps(tmp_path: Path, stdout: str) -> Path:
    '''Run run_reps.sh reps 1 to 1 on the stub and return the output folder.'''
    prompt = tmp_path / 'prompt.txt'
    prompt.write_text('a prompt\n')
    out = tmp_path / 'round' / 'case'
    env = {**os.environ, 'PATH': f'{stub_dir(tmp_path, stdout)}:{os.environ["PATH"]}',
           'KIT_SCRATCH_ROOT': str(tmp_path / 'scratch')}
    done = subprocess.run(['bash', str(KIT / 'run_reps.sh'), str(prompt), str(out), '1', '1', 'claude-opus-5-5'],
                          capture_output=True, text=True, env=env, check=False, timeout=120)
    assert done.returncode == 0, done.stdout + done.stderr
    return out


def every_text(folder: Path) -> str:
    return ''.join(path.read_text() for path in sorted(folder.rglob('*')) if path.is_file())


def test_run_reps_drops_secrets_and_keeps_the_answer(tmp_path):
    out = run_reps(tmp_path, json.dumps(CLEAN))
    text = (out / 'rep1.json').read_text()
    rep = json.loads(text)
    assert rep['void'] is False
    assert rep['result'] == 'ok'
    assert 'credential_expires_at' not in text
    assert 'origin' not in text


def test_run_reps_voids_a_peer_turn(tmp_path):
    out = run_reps(tmp_path, json.dumps(PEER))
    assert json.loads((out / 'rep1.json').read_text()) == {'void': True, 'reason': 'result_index'}
    assert 'peer-title-x' not in every_text(out)


def test_run_reps_voids_unreadable_output(tmp_path):
    out = run_reps(tmp_path, 'not json at all')
    assert json.loads((out / 'rep1.json').read_text()) == {'void': True, 'reason': 'unreadable'}
    assert 'not json at all' not in every_text(out)


def test_show_reps_prints_void(tmp_path):
    out = run_reps(tmp_path, json.dumps(PEER))
    done = subprocess.run([sys.executable, str(KIT / 'show_reps.py'), str(out)], capture_output=True, text=True,
                          check=True)
    assert 'rep1 VOID (result_index)' in done.stdout


def test_gather_skips_a_void_rep(tmp_path):
    (tmp_path / 'rep1.json').write_text(json.dumps({'result': 'a', 'void': False}))
    (tmp_path / 'rep2.json').write_text(json.dumps({'void': True, 'reason': 'result_index'}))
    assert panel.gather([('x', tmp_path)]) == {'x-rep1': 'a'}


def test_vote_output_is_postprocessed(monkeypatch):
    def stub_run(stdout):
        return lambda *args, **kwargs: SimpleNamespace(stdout=stdout, stderr='', returncode=0)

    monkeypatch.setattr(panel.subprocess, 'run', stub_run(json.dumps(PEER)))
    assert panel.call_voter('text') == {'void': True, 'reason': 'result_index'}
    monkeypatch.setattr(panel.subprocess, 'run', stub_run(json.dumps(CLEAN)))
    vote = panel.call_voter('text')
    assert 'credential_expires_at' not in json.dumps(vote)
    assert 'origin' not in vote


def test_run_stops_on_a_void_vote(tmp_path, monkeypatch):
    reps = tmp_path / 'reps'
    reps.mkdir()
    (reps / 'rep1.json').write_text(json.dumps({'result': 'a', 'void': False}))
    (tmp_path / 'rule.txt').write_text('a rule\n')
    (tmp_path / 'request.txt').write_text('a request\n')
    monkeypatch.setattr(panel, 'call_voter', lambda text: {'void': True, 'reason': 'origin'})
    out = tmp_path / 'panel'
    args = argparse.Namespace(out=str(out), arms=[f'x={reps}'], rule=str(tmp_path / 'rule.txt'),
                           request=str(tmp_path / 'request.txt'), votes=1, seed=1)
    with pytest.raises(SystemExit, match=r'vote 1 .*void'):
        panel.run(args)
    assert not (out / 'panel-verdicts.json').exists()
