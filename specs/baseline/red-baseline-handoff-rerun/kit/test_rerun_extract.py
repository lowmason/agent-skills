'''Tests for the kit audit and tally: extract.py and tally.py (plan 100, Task 3).

Each test writes a small results folder under a temporary PHR_CTL: a registry
row, meta.txt, turn records, init records and transcripts. It then runs
extract.py (or tally.py) on the system Python, with HOME set to a temporary
"real home". PHR_ROOT is /tmp/phr100, as in a real run: the audit only reads it
as a string, and a test checks that it writes nothing there.
'''

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parent
EXTRACT = KIT / 'extract.py'
TALLY = KIT / 'tally.py'
PY = '/usr/bin/python3'
ROOT = '/tmp/phr100'
REP = 'r281'
HOME_RUN = f'/private/tmp/phr100/{REP}'
REPO_RUN = f'{HOME_RUN}/work/{REP}'
KIT_COMMIT = '92f6a379d4bb77ba53adb360f8171ebd9c295ce8'
KIT_SKILLS = [
    'brainstorming', 'writing-plans', 'executing-plans', 'subagent-driven-development',
    'finishing-a-development-branch', 'requesting-code-review', 'receiving-code-review',
    'using-git-worktrees', 'verification-before-completion', 'test-driven-development',
    'derive-roadmap', 'prepare-handoff',
]
KIT_AGENTS = ['code-reviewer', 'task-reviewer']
ARMS = {
    'c4a-neg': ('t3', 'c4a-neg.t1.txt,c4a.t2.txt'),
    'v1': ('t9', 'c4b.t1.loc.txt,c4b.t2.txt'),
    'b2': ('t2', 'c2.t1.loc.txt,b2.t2.txt,c2.t3.txt'),
}


class Ctl:
    '''One test's control folder, real home and registered reps.'''

    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.real = tmp / 'real'
        self.real.mkdir()
        self.ctl = tmp / 'ctl'
        (self.ctl / 'results').mkdir(parents=True)
        (self.ctl / 'registry.tsv').write_text('rep\tarm\tphase\ttemplate\tkit_commit\tprompts\n')

    def env(self) -> dict[str, str]:
        return {'HOME': str(self.real), 'PATH': '/usr/bin:/bin:/opt/homebrew/bin', 'PHR_CTL': str(self.ctl),
                'PHR_ROOT': ROOT}

    def rep(self, rep: str = REP, arm: str = 'c4a-neg', phase: str = 'rerun100',
            main: list[tuple[str, dict]] | None = None, sub: list[tuple[str, dict]] | None = None) -> Path:
        '''Register one rep and write a clean, valid results folder for it.'''
        template, prompts = ARMS[arm]
        with (self.ctl / 'registry.tsv').open('a') as f:
            f.write('\t'.join((rep, arm, phase, template, KIT_COMMIT, prompts)) + '\n')
        out = self.ctl / 'results' / rep
        out.mkdir()
        turns = len(prompts.split(','))
        (out / 'meta.txt').write_text(
            f'rep={rep}\narm={arm}\nphase={phase}\ntemplate={template}\nkit_commit={KIT_COMMIT}\n'
            f'model=claude-opus-5-5\neffort=xhigh\nclaude=9.9.9 (stub)\nkit_sha_before={"a" * 64}\n'
            f'kit_sha_after={"a" * 64}\n')
        (out / 'session-id').write_text('sid-1\n')
        for n in range(1, turns + 1):
            (out / f'turn{n}.prompt.txt').write_text(f'prompt of turn {n}\n')
            self.result(rep, n, {'subtype': 'success', 'is_error': False, 'result': f'final {n}',
                                 'total_cost_usd': 0.5, 'permission_denials': []})
            self.init(rep, n)
            (out / f'turn{n}.stderr').write_text('')
            (out / f'turn{n}.git.txt').write_text('## branch\nmain\n')
        project = out / 'project'
        (project / 'sid-1' / 'subagents').mkdir(parents=True)
        self.transcript(project / 'sid-1.jsonl', main or [('Bash', {'command': 'git status'})], REPO_RUN)
        self.transcript(project / 'sid-1' / 'subagents' / 'agent-a1.jsonl',
                        sub or [('Read', {'file_path': f'{REPO_RUN}/README.md'})], REPO_RUN)
        return out

    def result(self, rep: str, n: int, data: dict) -> None:
        (self.ctl / 'results' / rep / f'turn{n}.json').write_text(json.dumps({'type': 'result', **data}))

    def init(self, rep: str, n: int, skills: list[str] | None = None, agents: list[str] | None = None) -> None:
        skills = KIT_SKILLS + ['init', 'review'] if skills is None else skills
        agents = KIT_AGENTS + ['general-purpose', 'Explore'] if agents is None else agents
        record = {'type': 'system', 'subtype': 'init', 'skills': skills, 'agents': agents}
        (self.ctl / 'results' / rep / f'turn{n}.init.json').write_text(json.dumps(record))

    @staticmethod
    def transcript(path: Path, uses: list[tuple[str, dict]], cwd: str | None) -> None:
        lines = [json.dumps({'type': 'user', 'message': {'content': 'prompt of turn 1'}})]
        for i, (name, data) in enumerate(uses):
            record = {'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'id': f't{i}', 'name': name, 'input': data}]}}
            if cwd is not None:
                record['cwd'] = cwd
            lines.append(json.dumps(record))
        path.write_text(''.join(line + '\n' for line in lines))

    def extract(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([PY, str(EXTRACT), *args], env=self.env(), capture_output=True, text=True,
                              check=False)

    def audit(self, rep: str = REP) -> dict:
        done = self.extract('--rep', rep)
        assert done.returncode == 0, done.stderr
        return json.loads((self.ctl / 'results' / rep / 'audit.json').read_text())


@pytest.fixture
def ctl(tmp_path: Path) -> Ctl:
    return Ctl(tmp_path)


# --- the plan's tests ---------------------------------------------------------


def test_tilde_kit_read_is_valid(ctl: Ctl) -> None:
    ctl.rep(main=[('Read', {'file_path': f'/tmp/phr100/{REP}/.claude/skills/writing-plans/SKILL.md'}),
                  ('Read', {'file_path': f'/private/tmp/phr100/{REP}/.claude/skills/writing-plans/SKILL.md'})],
            sub=[('Bash', {'command': 'ls ~/.claude/skills/writing-plans'})])
    audit = ctl.audit()
    assert audit['valid'] is True, audit
    assert audit['flags'] == [] and audit['problems'] == []


def test_real_home_voids(ctl: Ctl) -> None:
    target = f'{ctl.real}/.claude/skills/x'
    ctl.rep(main=[('Read', {'file_path': target})])
    audit = ctl.audit()
    assert audit['valid'] is False
    assert any(target in flag for flag in audit['flags']), audit['flags']


def test_library_link_voids(ctl: Ctl) -> None:
    ctl.rep(main=[('Bash', {'command': 'ls ~/Library/Keychains/..'})])
    audit = ctl.audit()
    assert audit['valid'] is False
    assert audit['flags'], audit


def test_reps_dir_voids(ctl: Ctl) -> None:
    ctl.rep(main=[('Bash', {'command': 'ls /tmp/phr100'})])
    ctl.rep('r282', main=[('Bash', {'command': 'ls /private/tmp/phr100'})])
    for rep in (REP, 'r282'):
        audit = ctl.audit(rep)
        assert audit['valid'] is False, rep
        assert any('/private/tmp/phr100' in flag for flag in audit['flags']), audit['flags']


def test_fragment_voids(ctl: Ctl) -> None:
    ctl.rep(main=[('Bash', {'command': 'ls ~/Projects/agent-skills'})])
    audit = ctl.audit()
    assert audit['valid'] is False
    assert any("fragment 'Projects/agent-skills'" in flag for flag in audit['flags']), audit['flags']
    assert not any(': path ' in flag for flag in audit['flags']), audit['flags']


def test_handoffs_listing(ctl: Ctl) -> None:
    ctl.rep(main=[('Bash', {'command': 'ls ~/.cache/agent-skills/handoffs'})])
    audit = ctl.audit()
    assert audit['valid'] is True, audit


def test_error_turn_voids(ctl: Ctl) -> None:
    ctl.rep()
    ctl.result(REP, 2, {'subtype': 'error_max_budget_usd', 'is_error': True, 'total_cost_usd': 30.0})
    audit = ctl.audit()
    assert audit['valid'] is False
    assert 'turn 2: error_max_budget_usd' in audit['problems'], audit['problems']


def test_kit_hash_mismatch_voids(ctl: Ctl) -> None:
    out = ctl.rep()
    meta = (out / 'meta.txt').read_text().replace(f'kit_sha_after={"a" * 64}', f'kit_sha_after={"b" * 64}')
    (out / 'meta.txt').write_text(meta)
    audit = ctl.audit()
    assert audit['valid'] is False
    assert any('kit hash' in p for p in audit['problems']), audit['problems']


def test_init_skill_mismatch_voids(ctl: Ctl) -> None:
    ctl.rep()
    ctl.init(REP, 1, skills=[s for s in KIT_SKILLS if s != 'prepare-handoff'])
    audit = ctl.audit()
    assert audit['valid'] is False
    assert any('prepare-handoff' in p for p in audit['problems']), audit['problems']


# --- the deviation's test (plan note under the Rep command) -------------------


def test_background_tasks_stopped_voids(ctl: Ctl) -> None:
    out = ctl.rep()
    (out / 'turn2.stderr').write_text('Background tasks still running: 1 agent stopped\n')
    audit = ctl.audit()
    assert audit['valid'] is False
    assert any(p.startswith('turn 2:') and 'background' in p.lower() for p in audit['problems']), audit['problems']
