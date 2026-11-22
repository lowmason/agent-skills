'''Wiring tests for run_reps.sh: a void rep and a kept rep, with a stub `claude` and no model.

The stub is a bash script that run_reps.sh finds on PATH. It prints the JSON in reply.json. run_reps.sh
starts it under `env -i`, so every path it needs is written into its text. KIT_SCRATCH_ROOT sends the
raw JSON to a temporary folder, so nothing reaches ~/.cache.
'''
import json
import os
import subprocess
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parent
RUN_REPS = KIT / 'run_reps.sh'
STUB = '''#!/bin/bash
cat > /dev/null
cat '@DIR@/reply.json'
'''
PRIVATE_KEYS = ('origin', 'credential_expires_at', 'session_id', 'uuid')


class World:
    def __init__(self, tmp: Path) -> None:
        self.stub_dir = tmp / 'stub'
        self.stub_dir.mkdir()
        stub = self.stub_dir / 'claude'
        stub.write_text(STUB.replace('@DIR@', str(self.stub_dir)))
        stub.chmod(0o755)
        self.prompt = tmp / 'prompt.txt'
        self.prompt.write_text('a prompt\n')
        self.out = tmp / 'runs' / 'case-control'
        self.scratch_root = tmp / 'scratch'
        self.raw = self.scratch_root / 'worktree-skills-fix' / 'runs' / 'case-control'

    def reply(self, data: dict) -> None:
        (self.stub_dir / 'reply.json').write_text(json.dumps(data))

    def run(self, first: int, last: int | None = None) -> subprocess.CompletedProcess:
        env = {**os.environ, 'PATH': f'{self.stub_dir}:{os.environ["PATH"]}', 'KIT_SCRATCH_ROOT': str(self.scratch_root)}
        return subprocess.run(['bash', str(RUN_REPS), str(self.prompt), str(self.out), str(first),
                               str(last or first), 'claude-sonnet-5-5'],
                              capture_output=True, text=True, env=env, cwd=KIT)


@pytest.fixture
def world(tmp_path: Path) -> World:
    return World(tmp_path)


@pytest.mark.parametrize('extra, reason', [({'result_index': 1}, 'result_index'),
                                           ({'origin': {'kind': 'peer', 'socket': '/tmp/s'}}, 'origin')])
def test_a_void_rep_gets_a_note_and_no_json_and_the_batch_exits_3(world, extra, reason):
    world.reply({'result': 'a reply to a peer', 'result_index': 0, 'origin': None, **extra})
    run = world.run(1)
    assert run.returncode == 3, run.stdout + run.stderr
    assert f'rep1 VOID (void {reason})' in run.stdout
    assert 'run a replacement under a new rep number' in run.stdout.lower()
    assert (world.out / 'rep1.VOID').read_text().startswith(f'VOID: {reason}')
    assert not (world.out / 'rep1.json').exists()
    assert 'a reply to a peer' not in (world.out / 'rep1.VOID').read_text()
    # The raw JSON stays outside the repository, so its cost still counts.
    assert json.loads((world.raw / 'rep1.json').read_text())['result'] == 'a reply to a peer'


def test_a_clean_rep_is_kept_without_the_private_keys_and_the_batch_exits_0(world):
    world.reply({'result': 'ok', 'result_index': 0, 'origin': None, 'credential_expires_at': 1,
                 'session_id': 's', 'uuid': 'u', 'total_cost_usd': 0.01,
                 'modelUsage': {'claude-sonnet-5-5': {'credential_expires_at': 2}}})
    run = world.run(1)
    assert run.returncode == 0, run.stdout + run.stderr
    kept = json.loads((world.out / 'rep1.json').read_text())
    assert kept['result'] == 'ok'
    assert not any(key in json.dumps(kept) for key in PRIVATE_KEYS)
    assert not (world.out / 'rep1.VOID').exists()
    # The raw copy is untouched.
    assert 'credential_expires_at' in (world.raw / 'rep1.json').read_text()


def test_one_void_rep_in_a_batch_leaves_the_others_scored_and_exits_3(world):
    world.reply({'result': 'ok', 'result_index': 0, 'origin': None})
    assert world.run(1).returncode == 0
    world.reply({'result': 'peer', 'result_index': 1, 'origin': None})
    run = world.run(2, 3)
    assert run.returncode == 3
    assert (world.out / 'rep1.json').exists()
    assert (world.out / 'rep2.VOID').exists() and (world.out / 'rep3.VOID').exists()
    assert '2 rep(s) void: rep2 rep3.' in run.stdout


def test_a_rep_number_that_was_void_is_refused_so_the_replacement_takes_a_new_number(world):
    world.reply({'result': 'peer', 'result_index': 1, 'origin': None})
    assert world.run(1).returncode == 3
    world.reply({'result': 'ok', 'result_index': 0, 'origin': None})
    again = world.run(1)
    assert again.returncode == 2
    assert 'rep 1 was void' in again.stdout
    replacement = world.run(2)
    assert replacement.returncode == 0
    assert (world.out / 'rep2.json').exists()


def test_an_unreadable_claude_reply_is_void_and_not_a_scored_rep(world):
    (world.stub_dir / 'reply.json').write_text('')
    run = world.run(1)
    assert run.returncode == 3
    assert 'rep1 VOID (unreadable)' in run.stdout
    assert not (world.out / 'rep1.json').exists()


def test_every_rep_of_a_clean_batch_goes_through_postprocess(world):
    # The brief (Interfaces): "run_reps.sh calls it on each raw JSON". The first rep runs alone and the
    # others run together, so a call on only one of them would leave private keys in the rest.
    world.reply({'result': 'ok', 'result_index': 0, 'origin': None, 'credential_expires_at': 1, 'session_id': 's'})
    run = world.run(1, 3)
    assert run.returncode == 0, run.stdout + run.stderr
    for number in (1, 2, 3):
        kept = (world.out / f'rep{number}.json').read_text()
        assert json.loads(kept)['result'] == 'ok'
        assert not any(key in kept for key in PRIVATE_KEYS)
        assert 'credential_expires_at' in (world.raw / f'rep{number}.json').read_text()
