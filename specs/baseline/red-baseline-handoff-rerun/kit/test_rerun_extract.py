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
        self.extra_env: dict[str, str] = {}

    def env(self) -> dict[str, str]:
        return {'HOME': str(self.real), 'PATH': '/usr/bin:/bin:/opt/homebrew/bin', 'PHR_CTL': str(self.ctl),
                'PHR_ROOT': ROOT, **self.extra_env}

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
        repo = f'/private/tmp/phr100/{rep}/work/{rep}'
        self.transcript(project / 'sid-1.jsonl', main or [('Bash', {'command': 'git status'})], repo)
        self.transcript(project / 'sid-1' / 'subagents' / 'agent-a1.jsonl',
                        sub or [('Read', {'file_path': f'{repo}/README.md'})], repo)
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


# --- strengthening tests (mutant step) ----------------------------------------


@pytest.mark.parametrize('command', [
    'ls $HOME/.claude/skills', 'ls ${HOME}/.claude/skills', 'cat ~/.claude/agents/code-reviewer.md',
    f'ls /System/Volumes/Data/private/tmp/phr100/{REP}/.claude/skills',
    'ls /tmp/scratch-1 /private/tmp/other', f'ls {HOME_RUN}/tmp/x',
    'cat <<EOF > notes.md\n/Users/someone/Projects/agent-skills is named here\nEOF',
])
def test_rep_home_and_scratch_spellings_are_valid(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    audit = ctl.audit()
    assert audit['valid'] is True, audit


@pytest.mark.parametrize('form', ['plain', 'data', 'upper', 'tilde-user', 'user-var'])
def test_real_home_spellings_void(ctl: Ctl, form: str) -> None:
    real = str(ctl.real)
    path = {
        'plain': f'ls {real}/.ssh',
        'data': f'ls /System/Volumes/Data{real}/.ssh',
        'upper': f'ls {real.upper()}/.ssh',
        'tilde-user': f'ls ~{ctl.real.name}/.ssh',
        'user-var': f'ls {ctl.real.parent}/$USER/.ssh',
    }[form]
    ctl.rep(main=[('Bash', {'command': path})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('real home' in flag for flag in audit['flags']), audit['flags']


@pytest.mark.parametrize('command', [
    'ls ~/Library/Keychains/../../Projects/x', 'ls ~/Library/Preferences', 'cd ~ && ls Library/Keychains',
    'ls ~/Library/Key""chains', 'cd ~ && ls Library/Key""chains',
])
def test_library_and_keychains_void(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('Library' in flag or 'Keychains' in flag for flag in audit['flags']), audit['flags']


def test_library_escape_through_link_is_flagged_as_library(ctl: Ctl) -> None:
    ctl.rep(main=[('Read', {'file_path': '~/Library/Keychains/../../Projects/x'})])
    audit = ctl.audit()
    assert any('through the Library folder' in flag for flag in audit['flags']), audit['flags']


@pytest.mark.parametrize('command', ['ls /tmp/phr100/r282', 'ls ../../..', 'ls /tmp/phr100/'])
def test_reps_dir_shapes_void(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('reps directory' in flag for flag in audit['flags']), audit['flags']


def test_record_cwd_decides_a_relative_path(ctl: Ctl) -> None:
    out = ctl.rep()
    Ctl.transcript(out / 'project' / 'sid-1.jsonl', [('Bash', {'command': 'ls ..'})], HOME_RUN)
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('/private/tmp/phr100 (the reps directory)' in flag for flag in audit['flags']), audit['flags']


def test_record_without_cwd_uses_the_repo(ctl: Ctl) -> None:
    out = ctl.rep()
    Ctl.transcript(out / 'project' / 'sid-1.jsonl', [('Bash', {'command': 'ls ../..'})], None)
    audit = ctl.audit()
    assert audit['valid'] is True, audit


def test_glob_pattern_is_relative_to_its_path(ctl: Ctl) -> None:
    ctl.rep(main=[('Glob', {'pattern': '../../*', 'path': f'{HOME_RUN}/work'})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('reps directory' in flag for flag in audit['flags']), audit['flags']


def test_relative_file_field_is_one_token(ctl: Ctl) -> None:
    ctl.rep(main=[('Read', {'file_path': '../../../r282/x'})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit


def test_subagent_fragment_voids(ctl: Ctl) -> None:
    ctl.rep(sub=[('Grep', {'pattern': 'x', 'path': 'specs/handoff-briefs.md'})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any(f.startswith('agent-a1.jsonl: Grep: fragment') for f in audit['flags']), audit['flags']


def test_missing_and_failed_turns_void(ctl: Ctl) -> None:
    out = ctl.rep(arm='b2')
    (out / 'turn3.json').unlink()
    ctl.result(REP, 2, {'subtype': 'error_during_execution', 'is_error': False})
    audit = ctl.audit()
    assert 'turn 3: no output' in audit['problems'], audit['problems']
    assert 'turn 2: error_during_execution' in audit['problems'], audit['problems']


@pytest.mark.parametrize('edit', ['no-after', 'empty-before', 'kit-error', 'exited'])
def test_meta_harness_problems_void(ctl: Ctl, edit: str) -> None:
    out = ctl.rep()
    text = (out / 'meta.txt').read_text()
    text = {
        'no-after': text.replace(f'kit_sha_after={"a" * 64}\n', ''),
        'empty-before': text.replace(f'kit_sha_before={"a" * 64}', 'kit_sha_before='),
        'kit-error': text + 'kit_error=the strip check found the field in: x\n',
        'exited': text + 'turn 1 exited 1; later turns not run\n',
    }[edit]
    (out / 'meta.txt').write_text(text)
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    want = {'no-after': 'kit hash missing', 'empty-before': 'kit hash missing', 'kit-error': 'kit error:',
            'exited': 'turn 1: exited 1'}[edit]
    assert any(want in p for p in audit['problems']), audit['problems']


def test_init_agent_missing_voids(ctl: Ctl) -> None:
    ctl.rep()
    ctl.init(REP, 2, agents=['code-reviewer', 'general-purpose'])
    audit = ctl.audit()
    assert audit['valid'] is False
    assert 'turn 2: init agents lack task-reviewer' in audit['problems'], audit['problems']


def test_missing_first_init_voids(ctl: Ctl) -> None:
    out = ctl.rep()
    (out / 'turn1.init.json').unlink()
    audit = ctl.audit()
    assert 'turn 1: no init record' in audit['problems'], audit['problems']


def test_missing_later_init_is_valid(ctl: Ctl) -> None:
    out = ctl.rep()
    (out / 'turn2.init.json').unlink()
    assert ctl.audit()['valid'] is True


def test_init_names_as_objects_and_twice_are_valid(ctl: Ctl) -> None:
    out = ctl.rep()
    record = {'type': 'system', 'subtype': 'init',
              'skills': [{'name': s} for s in KIT_SKILLS] + KIT_SKILLS + ['init'],
              'agents': [{'name': a} for a in KIT_AGENTS]}
    (out / 'turn1.init.json').write_text(json.dumps(record))
    assert ctl.audit()['valid'] is True


def test_no_transcript_voids(ctl: Ctl) -> None:
    out = ctl.rep()
    for f in (out / 'project').rglob('*.jsonl'):
        f.unlink()
    assert 'no transcript copied' in ctl.audit()['problems']


def test_audit_record_and_extract_sections(ctl: Ctl) -> None:
    out = ctl.rep(main=[('Skill', {'skill': 'prepare-handoff'}), ('Bash', {'command': 'git status'})])
    ctl.result(REP, 1, {'subtype': 'success', 'is_error': False, 'result': 'final one', 'total_cost_usd': 1.25,
                        'permission_denials': [{'tool_name': 'Bash'}]})
    (out / 'handoffs' / REP).mkdir(parents=True)
    (out / 'handoffs' / REP / 'brief.md').write_text('# the brief\n')
    (out / 'project' / 'memory').mkdir()
    (out / 'project' / 'memory' / 'MEMORY.md').write_text('# memory line\n')
    repo = ctl.ctl / 'homes' / REP / 'work' / REP
    repo.mkdir(parents=True)
    git = ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-c', 'commit.gpgsign=false', '-C',
           str(repo)]
    subprocess.run([*git, 'init', '-q', '-b', 'main'], check=True)
    (repo / 'a.txt').write_text('a\n')
    subprocess.run([*git, 'add', '-A'], check=True)
    subprocess.run([*git, 'commit', '-q', '-m', 'parked repo commit'], check=True)
    (repo / 'untracked.md').write_text('untracked note\n')
    head = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], capture_output=True, text=True,
                          check=True).stdout.strip()
    subprocess.run([*git, 'commit', '-q', '--allow-empty', '-m', 'rep made this commit'], check=True)
    heads = ctl.tmp / 'heads.tsv'
    heads.write_text(f'template\thead\nt3\t{head}\n')
    ctl.extra_env = {'PHR_TEMPLATE_HEADS': str(heads)}
    audit = ctl.audit()
    assert sorted(audit) == sorted(['rep', 'arm', 'phase', 'valid', 'problems', 'flags', 'denials', 'cost_usd'])
    assert (audit['rep'], audit['arm'], audit['phase']) == (REP, 'c4a-neg', 'rerun100')
    assert audit['cost_usd'] == 1.75 and audit['denials'] == [{'tool_name': 'Bash'}]
    text = (out / 'extract.md').read_text()
    for part in (f'# {REP} — c4a-neg (rerun100; template t3, kit {KIT_COMMIT})', '## Audit', '- verdict: valid',
                 '## Turn 1', '### Final message\n\nfinal one', '## Tool calls, in order', '- Skill: prepare-handoff',
                 '--- turn 1 prompt ---', '## Repo at the end', '### New commits\n', 'rep made this commit',
                 f'### main: changes since {head}', '### Untracked: untracked.md',
                 f'## Brief directory: {REP}/brief.md', '# the brief', '## Memory: MEMORY.md', 'kit_sha_after='):
        assert part in text, part


def test_batch_mode_audits_each_rep(ctl: Ctl) -> None:
    ctl.rep()
    ctl.rep('r282', main=[('Bash', {'command': 'ls /tmp/phr100'})])
    (ctl.ctl / 'batches').mkdir()
    (ctl.ctl / 'batches' / 'b.txt').write_text(f'{REP}\nr282\nr283\n')
    done = ctl.extract('b')
    assert done.returncode == 0, done.stderr
    assert f'{REP} c4a-neg: valid' in done.stdout
    assert 'r282 c4a-neg: VOID' in done.stdout
    assert 'r283: no results yet' in done.stdout


def test_audit_writes_nothing_under_the_reps_root(ctl: Ctl) -> None:
    before = sorted(os.listdir('/private/tmp/phr100')) if os.path.isdir('/private/tmp/phr100') else None
    ctl.rep(main=[('Bash', {'command': 'ls /tmp/phr100'})])
    ctl.audit()
    after = sorted(os.listdir('/private/tmp/phr100')) if os.path.isdir('/private/tmp/phr100') else None
    assert before == after


# --- tally ----------------------------------------------------------------------


def score(ctl: Ctl, phase: str, arm: str, rows: list[tuple[str, str, str]]) -> None:
    folder = ctl.ctl / 'scores' / phase
    folder.mkdir(parents=True, exist_ok=True)
    lines = ['rep\tcriterion\tverdict\tquote'] + [f'{r}\t{c}\t{v}\t{"" if v == "NA" else "## Audit"}'
                                                  for r, c, v in rows]
    (folder / f'{arm}.tsv').write_text('\n'.join(lines) + '\n')


def tally(ctl: Ctl, phase: str) -> subprocess.CompletedProcess:
    return subprocess.run([PY, str(TALLY), phase], env=ctl.env(), capture_output=True, text=True, check=False)


def reps(ctl: Ctl, arm: str, ids: range, phase: str = 'rerun100') -> list[str]:
    names = [f'r{n}' for n in ids]
    for rep in names:
        ctl.rep(rep, arm=arm, phase=phase)
        assert ctl.audit(rep)['valid'] is True
    return names


@pytest.mark.parametrize('failing, verdict', [(1, 'PASS (1 of 5 failing)'), (2, 'FAIL (2 of 5 failing)')])
def test_tally_positive_arm(ctl: Ctl, failing: int, verdict: str) -> None:
    names = reps(ctl, 'v1', range(281, 287))
    rows = [(r, 'F-restate', 'FAIL' if i < failing else 'PASS') for i, r in enumerate(names[:5])]
    rows += [(names[5], 'F-restate', 'FAIL')]  # the sixth valid rep never counts
    score(ctl, 'rerun100', 'v1', rows)
    done = tally(ctl, 'rerun100')
    assert done.returncode == 0, done.stdout + done.stderr
    assert verdict in done.stdout, done.stdout
    assert 'r281,r282,r283,r284,r285 ' in done.stdout


@pytest.mark.parametrize('failing, verdict', [(1, 'PASS (1 of 5 failing)'), (2, 'FAIL (2 of 5 failing)')])
def test_tally_negative_arm(ctl: Ctl, failing: int, verdict: str) -> None:
    names = reps(ctl, 'c4a-neg', range(281, 286))
    score(ctl, 'rerun100', 'c4a-neg', [(r, 'F-brief', 'FAIL' if i < failing else 'PASS') for i, r in enumerate(names)])
    done = tally(ctl, 'rerun100')
    assert verdict in done.stdout, done.stdout


def test_tally_skips_void_and_pilot_reps(ctl: Ctl) -> None:
    names = reps(ctl, 'b2', range(281, 286))
    pilot = reps(ctl, 'b2', range(286, 287), phase='pilot')
    ctl.rep('r287', arm='b2', main=[('Bash', {'command': 'ls /tmp/phr100'})])
    ctl.audit('r287')
    rows = [(r, 'B2-out', 'PASS') for r in names[:4]] + [(names[4], 'VOID', 'VOID')]
    rows += [(pilot[0], 'B2-out', 'PASS'), ('r287', 'B2-out', 'PASS')]
    score(ctl, 'rerun100', 'b2', rows)
    done = tally(ctl, 'rerun100')
    assert 'UNSETTLED (4 of 5 valid)' in done.stdout, done.stdout
    assert 'counted r281,r282,r283,r284 ' in done.stdout, done.stdout


def test_tally_rejects_a_missing_quote(ctl: Ctl) -> None:
    names = reps(ctl, 'c4a-neg', range(281, 282))
    folder = ctl.ctl / 'scores' / 'rerun100'
    folder.mkdir(parents=True)
    (folder / 'c4a-neg.tsv').write_text(f'rep\tcriterion\tverdict\tquote\n{names[0]}\tF-brief\tPASS\tnot in it\n')
    done = tally(ctl, 'rerun100')
    assert done.returncode == 1
    assert f'{names[0]} F-brief PASS: quote not found' in done.stdout


def test_tally_pilot_phase_is_not_counted(ctl: Ctl) -> None:
    names = reps(ctl, 'v1', range(281, 282), phase='pilot')
    score(ctl, 'pilot', 'v1', [(names[0], 'F-restate', 'PASS')])
    done = tally(ctl, 'pilot')
    assert 'pilot (not counted)' in done.stdout, done.stdout


def test_relative_file_field_without_dots_is_one_token(ctl: Ctl) -> None:
    out = ctl.rep()
    Ctl.transcript(out / 'project' / 'sid-1.jsonl', [('Read', {'file_path': 'Library/Preferences/x.plist'})], HOME_RUN)
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('Library' in flag for flag in audit['flags']), audit['flags']


@pytest.mark.parametrize('form', ['star-user', 'star-prefix', 'question'])
def test_glob_into_the_real_home_voids(ctl: Ctl, form: str) -> None:
    real = ctl.real
    command = {
        'star-user': f'ls {real.parent}/*/.ssh',
        'star-prefix': f'ls {real.parent}/{real.name[:2]}*',
        'question': f'cat {real.parent}/{real.name[:-1]}?/.ssh/x',
    }[form]
    ctl.rep(main=[('Bash', {'command': command})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('real home' in flag for flag in audit['flags']), audit['flags']


@pytest.mark.parametrize('command', ['ls /*', 'ls /private/tmp/*', 'ls ~/.claude/skills/*', 'ls /opt/*/bin'])
def test_glob_outside_the_real_home_is_valid(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    assert ctl.audit()['valid'] is True


# --- review round 1 -------------------------------------------------------------


def test_glob_relative_path_from_a_subfolder_is_valid(ctl: Ctl) -> None:
    out = ctl.rep()
    Ctl.transcript(out / 'project' / 'sid-1.jsonl', [('Glob', {'pattern': '*.md', 'path': '../..'})],
                   f'{REPO_RUN}/specs')
    audit = ctl.audit()
    assert audit['valid'] is True, audit


@pytest.mark.parametrize('command', ['grep -rn keychains .', 'grep -rn "Keychains" docs/', 'ls keychains/'])
def test_keychains_word_without_library_is_valid(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    assert ctl.audit()['valid'] is True


def test_record_without_cwd_resolves_from_the_repo(ctl: Ctl) -> None:
    out = ctl.rep()
    Ctl.transcript(out / 'project' / 'sid-1.jsonl', [('Bash', {'command': 'ls ../../..'})], None)
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('/private/tmp/phr100 (the reps directory)' in flag for flag in audit['flags']), audit['flags']


def test_glob_at_real_home_depth_with_another_top_is_valid(ctl: Ctl) -> None:
    parts = ctl.real.parts[2:]  # the real home's components after the first
    command = 'ls /opt/' + '/'.join(parts[:-1]) + '/*/x'
    ctl.rep(main=[('Bash', {'command': command})])
    assert ctl.audit()['valid'] is True


# --- review round 2 -------------------------------------------------------------


def test_sibling_rep_through_the_data_spelling_voids(ctl: Ctl) -> None:
    ctl.rep(main=[('Bash', {'command': 'ls /System/Volumes/Data/private/tmp/phr100/r282'})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('/private/tmp/phr100/r282 (the reps directory)' in flag for flag in audit['flags']), audit['flags']


@pytest.mark.parametrize('command', ['cd ~ && cd Library && ls Keychains', 'cd ~ && ls Library//Keychains'])
def test_split_library_keychains_spellings_void(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('Library/Keychains' in flag for flag in audit['flags']), audit['flags']
