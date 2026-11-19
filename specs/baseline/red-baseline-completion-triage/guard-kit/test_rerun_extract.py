'''Tests for the kit audit and tally: extract.py and tally.py (plan 100, Task 3; adapted for plan 101, Task 9).

Each test writes a small results folder under a temporary PHR_CTL: a registry
row, meta.txt, turn records, init records and transcripts. It then runs
extract.py (or tally.py) on the system Python, with HOME set to a temporary
"real home". PHR_ROOT is /tmp/phr101, as in a real run: the audit only reads it
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
ROOT = '/tmp/phr101'
REP = 'r501'
HOME_RUN = f'/private/tmp/phr101/{REP}'
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
    'c5a-neg': ('t5', 'c5a-neg.t1.txt,c5a.t2-merge.txt'),
    'p5a': ('t4', 'p5a.t1.txt,c5a.t2-merge.txt'),
    'c5a-ep': ('t4', 'c5a-ep.t1.txt,c5a.t2-merge.txt'),
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

    def rep(self, rep: str = REP, arm: str = 'c5a-neg', phase: str = 'guard101',
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
            f'model=claude-sonnet-5-5\neffort=medium\nclaude=9.9.9 (stub)\nkit_sha_before={"a" * 64}\n'
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
        repo = f'/private/tmp/phr101/{rep}/work/{rep}'
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
    ctl.rep(main=[('Read', {'file_path': f'/tmp/phr101/{REP}/.claude/skills/writing-plans/SKILL.md'}),
                  ('Read', {'file_path': f'/private/tmp/phr101/{REP}/.claude/skills/writing-plans/SKILL.md'})],
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
    ctl.rep(main=[('Bash', {'command': 'ls /tmp/phr101'})])
    ctl.rep('r502', main=[('Bash', {'command': 'ls /private/tmp/phr101'})])
    for rep in (REP, 'r502'):
        audit = ctl.audit(rep)
        assert audit['valid'] is False, rep
        assert any('/private/tmp/phr101' in flag for flag in audit['flags']), audit['flags']


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
    f'ls /System/Volumes/Data/private/tmp/phr101/{REP}/.claude/skills',
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


@pytest.mark.parametrize('prefix', ['/system/volumes/data', '/SYSTEM/Volumes/dAtA'])
def test_real_home_through_data_volume_in_any_case_voids(ctl: Ctl, prefix: str) -> None:
    ctl.rep(main=[('Bash', {'command': f'ls {prefix}{ctl.real}/.ssh'})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('real home' in flag for flag in audit['flags']), audit['flags']


def test_own_home_through_lowercase_data_volume_is_valid(ctl: Ctl) -> None:
    ctl.rep(main=[('Bash', {'command': f'ls /system/volumes/data{HOME_RUN}/.claude/skills'}),
                  ('Read', {'file_path': f'/system/volumes/data{REPO_RUN}/README.md'})])
    audit = ctl.audit()
    assert audit['valid'] is True, audit


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


@pytest.mark.parametrize('command', ['ls /tmp/phr101/r502', 'ls ../../..', 'ls /tmp/phr101/'])
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
    assert any('/private/tmp/phr101 (the reps directory)' in flag for flag in audit['flags']), audit['flags']


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
    ctl.rep(main=[('Read', {'file_path': '../../../r502/x'})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit


def test_subagent_fragment_voids(ctl: Ctl) -> None:
    ctl.rep(sub=[('Grep', {'pattern': 'x', 'path': 'specs/handoff-briefs.md'})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any(f.startswith('agent-a1.jsonl: Grep: fragment') for f in audit['flags']), audit['flags']


def test_missing_and_failed_turns_void(ctl: Ctl) -> None:
    out = ctl.rep(arm='c5a-ep')
    (out / 'turn2.json').unlink()
    ctl.result(REP, 1, {'subtype': 'error_during_execution', 'is_error': False})
    audit = ctl.audit()
    assert 'turn 2: no output' in audit['problems'], audit['problems']
    assert 'turn 1: error_during_execution' in audit['problems'], audit['problems']


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
    heads.write_text(f'template\thead\nt5\t{head}\n')
    ctl.extra_env = {'PHR_TEMPLATE_HEADS': str(heads)}
    audit = ctl.audit()
    assert sorted(audit) == sorted(['rep', 'arm', 'phase', 'valid', 'problems', 'flags', 'denials', 'cost_usd'])
    assert (audit['rep'], audit['arm'], audit['phase']) == (REP, 'c5a-neg', 'guard101')
    assert audit['cost_usd'] == 1.75
    assert audit['denials'] == [{'tool_name': 'Bash', 'transcript': 'turn1.json', 'subagent': False}]
    text = (out / 'extract.md').read_text()
    for part in (f'# {REP} — c5a-neg (guard101; template t5, kit {KIT_COMMIT})', '## Audit', '- verdict: valid',
                 '## Turn 1', '### Final message\n\nfinal one', '## Tool calls, in order', '- Skill: prepare-handoff',
                 '--- turn 1 prompt ---', '## Repo at the end', '### New commits\n', 'rep made this commit',
                 f'### main: changes since {head}', '### Untracked: untracked.md',
                 f'## Brief directory: {REP}/brief.md', '# the brief', '## Memory: MEMORY.md', 'kit_sha_after='):
        assert part in text, part


def test_registry_row_may_carry_the_extra_column(ctl: Ctl) -> None:
    # Plan 101: make_reps.py writes a seventh column, extra. The audit must read it and a six-column row alike.
    ctl.rep()
    ctl.rep('r502')
    ctl.rep('r503')
    registry = ctl.ctl / 'registry.tsv'
    lines = registry.read_text().splitlines()
    lines[0] += '\textra'
    lines[2] += '\t-'
    lines[3] += '\tmerged'
    registry.write_text('\n'.join(lines) + '\n')
    for rep in (REP, 'r502', 'r503'):
        audit = ctl.audit(rep)
        assert (audit['rep'], audit['arm'], audit['phase'], audit['valid']) == (rep, 'c5a-neg', 'guard101', True)
    assert '# r503 — c5a-neg (guard101; template t5, kit' in (ctl.ctl / 'results' / 'r503' / 'extract.md').read_text()


def git_in(repo: Path, *args: str) -> str:
    git = ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-c', 'commit.gpgsign=false', '-C', str(repo)]
    return subprocess.run([*git, *args], capture_output=True, text=True, check=True).stdout.strip()


def t4_like_repo(ctl: Ctl, rep: str, merged: bool) -> dict[str, str]:
    '''A parked repo like a t4 rep's: main, and a feature branch one commit ahead. When merged, the harness merges it
    into main before turn 1 and deletes it. The rep then makes one commit. Returns the shas at the start.'''
    repo = ctl.ctl / 'homes' / rep / 'work' / rep
    repo.mkdir(parents=True)
    git_in(repo, 'init', '-q', '-b', 'main')
    (repo / 'a.txt').write_text('a\n')
    git_in(repo, 'add', '-A')
    git_in(repo, 'commit', '-q', '-m', 'init')
    shas = {'init': git_in(repo, 'rev-parse', 'HEAD')}
    git_in(repo, 'checkout', '-q', '-b', 'feat/s2a-csv-export')
    (repo / 'export.py').write_text('x = 1\n')
    git_in(repo, 'add', '-A')
    git_in(repo, 'commit', '-q', '-m', 'feat: csv export')
    shas['feature'] = git_in(repo, 'rev-parse', 'HEAD')
    if merged:
        git_in(repo, 'checkout', '-q', 'main')
        git_in(repo, 'merge', '-q', '--no-ff', 'feat/s2a-csv-export', '-m', "Merge branch 'feat/s2a-csv-export'")
        git_in(repo, 'branch', '-q', '-d', 'feat/s2a-csv-export')
        shas['merge'] = git_in(repo, 'rev-parse', 'HEAD')
    git_in(repo, 'commit', '-q', '--allow-empty', '-m', 'rep made this commit')
    return shas


def section(text: str, title: str) -> str:
    '''The text under a `### title` heading, up to the next heading.'''
    body = text.split(f'### {title}\n', 1)[1]
    return body.split('\n### ', 1)[0].split('\n## ', 1)[0]


def test_start_refs_in_meta_keep_the_harness_merge_out_of_new_commits(ctl: Ctl) -> None:
    out = ctl.rep(arm='p5a')
    shas = t4_like_repo(ctl, REP, merged=True)
    heads = ctl.tmp / 'heads.tsv'
    heads.write_text(f'template\thead\trefs\nt4\t{shas["feature"]}\t'
                     f'refs/heads/feat/s2a-csv-export={shas["feature"]},refs/heads/main={shas["init"]}\n')
    ctl.extra_env = {'PHR_TEMPLATE_HEADS': str(heads)}
    with (out / 'meta.txt').open('a') as f:
        f.write(f'start_refs=main={shas["merge"]}\n')
    ctl.audit()
    text = (out / 'extract.md').read_text()
    new = section(text, 'New commits')
    assert 'rep made this commit' in new
    assert "Merge branch 'feat/s2a-csv-export'" not in new
    assert 'feat: csv export' not in new
    assert f'### main: changes since {shas["merge"]}\n' in text


def test_missing_start_refs_fall_back_to_the_templates_refs_pin(ctl: Ctl) -> None:
    out = ctl.rep(arm='p5a')
    shas = t4_like_repo(ctl, REP, merged=False)
    heads = ctl.tmp / 'heads.tsv'
    heads.write_text(f'template\thead\trefs\nt4\t{shas["feature"]}\t'
                     f'refs/heads/feat/s2a-csv-export={shas["feature"]},refs/heads/main={shas["init"]}\n')
    ctl.extra_env = {'PHR_TEMPLATE_HEADS': str(heads)}
    assert 'start_refs' not in (out / 'meta.txt').read_text()
    ctl.audit()
    text = (out / 'extract.md').read_text()
    new = section(text, 'New commits')
    assert 'rep made this commit' in new
    assert 'feat: csv export' not in new and 'init' not in new
    assert f'### main: changes since {shas["init"]}\n' in text
    assert f'### feat/s2a-csv-export: changes since {shas["feature"]}\n' in text


def test_batch_mode_audits_each_rep(ctl: Ctl) -> None:
    ctl.rep()
    ctl.rep('r502', main=[('Bash', {'command': 'ls /tmp/phr101'})])
    (ctl.ctl / 'batches').mkdir()
    (ctl.ctl / 'batches' / 'b.txt').write_text(f'{REP}\nr502\nr503\n')
    done = ctl.extract('b')
    assert done.returncode == 0, done.stderr
    assert f'{REP} c5a-neg: valid' in done.stdout
    assert 'r502 c5a-neg: VOID' in done.stdout
    assert 'r503: no results yet' in done.stdout


def test_audit_writes_nothing_under_the_reps_root(ctl: Ctl) -> None:
    before = sorted(os.listdir('/private/tmp/phr101')) if os.path.isdir('/private/tmp/phr101') else None
    ctl.rep(main=[('Bash', {'command': 'ls /tmp/phr101'})])
    ctl.audit()
    after = sorted(os.listdir('/private/tmp/phr101')) if os.path.isdir('/private/tmp/phr101') else None
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


def reps(ctl: Ctl, arm: str, ids: range, phase: str = 'guard101') -> list[str]:
    names = [f'r{n}' for n in ids]
    for rep in names:
        ctl.rep(rep, arm=arm, phase=phase)
        assert ctl.audit(rep)['valid'] is True
    return names


@pytest.mark.parametrize('failing, verdict', [(1, 'PASS (1 of 5 failing)'), (2, 'FAIL (2 of 5 failing)')])
def test_tally_positive_arm(ctl: Ctl, failing: int, verdict: str) -> None:
    names = reps(ctl, 'p5a', range(501, 507))
    rows = [(r, 'F-restate', 'FAIL' if i < failing else 'PASS') for i, r in enumerate(names[:5])]
    rows += [(names[5], 'F-restate', 'FAIL')]  # the sixth valid rep never counts
    score(ctl, 'guard101', 'p5a', rows)
    done = tally(ctl, 'guard101')
    assert done.returncode == 0, done.stdout + done.stderr
    assert verdict in done.stdout, done.stdout
    assert 'r501,r502,r503,r504,r505 ' in done.stdout


@pytest.mark.parametrize('failing, verdict', [(0, 'PASS (0 of 5 failing)'), (1, 'FAIL (1 of 5 failing)')])
def test_tally_negative_arm(ctl: Ctl, failing: int, verdict: str) -> None:
    names = reps(ctl, 'c5a-neg', range(501, 506))
    score(ctl, 'guard101', 'c5a-neg', [(r, 'F-brief', 'FAIL' if i < failing else 'PASS') for i, r in enumerate(names)])
    done = tally(ctl, 'guard101')
    assert verdict in done.stdout, done.stdout


def test_tally_skips_void_and_pilot_reps(ctl: Ctl) -> None:
    names = reps(ctl, 'c5a-ep', range(501, 506))
    pilot = reps(ctl, 'c5a-ep', range(506, 507), phase='pilot')
    ctl.rep('r507', arm='c5a-ep', main=[('Bash', {'command': 'ls /tmp/phr101'})])
    ctl.audit('r507')
    rows = [(r, 'B2-out', 'PASS') for r in names[:4]] + [(names[4], 'VOID', 'VOID')]
    rows += [(pilot[0], 'B2-out', 'PASS'), ('r507', 'B2-out', 'PASS')]
    score(ctl, 'guard101', 'c5a-ep', rows)
    done = tally(ctl, 'guard101')
    assert 'UNSETTLED (4 of 5 valid)' in done.stdout, done.stdout
    assert 'counted r501,r502,r503,r504 ' in done.stdout, done.stdout


def test_tally_rejects_a_missing_quote(ctl: Ctl) -> None:
    names = reps(ctl, 'c5a-neg', range(501, 502))
    folder = ctl.ctl / 'scores' / 'guard101'
    folder.mkdir(parents=True)
    (folder / 'c5a-neg.tsv').write_text(f'rep\tcriterion\tverdict\tquote\n{names[0]}\tF-brief\tPASS\tnot in it\n')
    done = tally(ctl, 'guard101')
    assert done.returncode == 1
    assert f'{names[0]} F-brief PASS: quote not found' in done.stdout


def test_tally_pilot_phase_is_not_counted(ctl: Ctl) -> None:
    names = reps(ctl, 'p5a', range(501, 502), phase='pilot')
    score(ctl, 'pilot', 'p5a', [(names[0], 'F-restate', 'PASS')])
    done = tally(ctl, 'pilot')
    assert 'pilot (not counted)' in done.stdout, done.stdout


def test_tally_counts_the_first_five_valid_reps_from_the_audits(ctl: Ctl) -> None:
    names = reps(ctl, 'p5a', range(501, 507))
    score(ctl, 'guard101', 'p5a', [(r, 'F-restate', 'PASS') for r in names[1:]])  # r501 has no rows
    done = tally(ctl, 'guard101')
    assert done.returncode == 1, done.stdout
    assert 'p5a r501: no rows' in done.stdout, done.stdout
    assert 'PASS' not in done.stdout and 'FAIL' not in done.stdout, done.stdout


def test_tally_refuses_a_counted_rep_missing_a_criterion(ctl: Ctl) -> None:
    names = reps(ctl, 'p5a', range(501, 506))
    rows = [(r, c, 'PASS') for r in names for c in ('F-restate', 'V1-ids')]
    rows = [row for row in rows if row[:2] != ('r503', 'V1-ids')]
    score(ctl, 'guard101', 'p5a', rows)
    done = tally(ctl, 'guard101')
    assert done.returncode == 1, done.stdout
    assert 'p5a r503: no row for V1-ids' in done.stdout, done.stdout
    assert 'PASS (' not in done.stdout, done.stdout


def test_tally_counts_each_arm_from_its_own_audits(ctl: Ctl) -> None:
    first = reps(ctl, 'p5a', range(501, 506))
    second = reps(ctl, 'c5a-ep', range(506, 511))
    score(ctl, 'guard101', 'p5a', [(r, 'F-restate', 'PASS') for r in first])
    score(ctl, 'guard101', 'c5a-ep', [(r, 'B2-out', 'FAIL') for r in second])
    done = tally(ctl, 'guard101')
    assert done.returncode == 0, done.stdout + done.stderr
    assert 'counted r506,r507,r508,r509,r510 ' in done.stdout and 'FAIL (5 of 5 failing)' in done.stdout, done.stdout
    assert 'counted r501,r502,r503,r504,r505 ' in done.stdout and 'PASS (0 of 5 failing)' in done.stdout, done.stdout


def test_tally_counts_no_probe_rep(ctl: Ctl) -> None:
    names = reps(ctl, 'p5a', range(501, 506))
    probe = reps(ctl, 'p5a', range(496, 497), phase='probe')
    rows = [(r, 'F-restate', 'PASS') for r in names] + [(probe[0], 'F-restate', 'FAIL')]
    score(ctl, 'guard101', 'p5a', rows)
    done = tally(ctl, 'guard101')
    assert done.returncode == 0, done.stdout + done.stderr
    assert 'counted r501,r502,r503,r504,r505 ' in done.stdout, done.stdout
    assert 'PASS (0 of 5 failing)' in done.stdout, done.stdout


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
    assert any('/private/tmp/phr101 (the reps directory)' in flag for flag in audit['flags']), audit['flags']


def test_glob_at_real_home_depth_with_another_top_is_valid(ctl: Ctl) -> None:
    parts = ctl.real.parts[2:]  # the real home's components after the first
    command = 'ls /opt/' + '/'.join(parts[:-1]) + '/*/x'
    ctl.rep(main=[('Bash', {'command': command})])
    assert ctl.audit()['valid'] is True


# --- review round 2 -------------------------------------------------------------


def test_sibling_rep_through_the_data_spelling_voids(ctl: Ctl) -> None:
    ctl.rep(main=[('Bash', {'command': 'ls /System/Volumes/Data/private/tmp/phr101/r502'})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('/private/tmp/phr101/r502 (the reps directory)' in flag for flag in audit['flags']), audit['flags']


@pytest.mark.parametrize('command', ['cd ~ && cd Library && ls Keychains', 'cd ~ && ls Library//Keychains'])
def test_split_library_keychains_spellings_void(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('Library/Keychains' in flag for flag in audit['flags']), audit['flags']


# --- completion gate: ancestor-rooted searches and every denial ------------------

R289 = ("cd /private/tmp/phr100/r289/work/r289; uv run --no-project --python 3.13 --with pytest python -m pytest -q "
        "2>&1 | tail -3; find / -path '*writing-plans*' -name 'SKILL.md' 2>/dev/null | head")


@pytest.mark.parametrize('command', [
    R289, 'ls -R /', 'grep -rn x @PARENT@', 'rg --files /', 'du -sh /System/Volumes/Data/*', 'tree /',
    'cd / && find . -name x', 'mdfind writing-plans', 'locate SKILL.md', "sh -c 'find @PARENT@ -name x'",
])
def test_search_rooted_at_an_ancestor_voids(ctl: Ctl, command: str) -> None:
    ctl.rep(sub=[('Bash', {'command': command.replace('@PARENT@', str(ctl.real.parent))})])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('holds the real home' in flag for flag in audit['flags']), audit['flags']


@pytest.mark.parametrize('command', ['mdfind writing-plans', 'locate SKILL.md'])
def test_indexed_search_flag_names_the_index(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    flags = ctl.audit()['flags']
    assert any('its index covers the whole disk' in flag for flag in flags), flags


@pytest.mark.parametrize('command', [
    'ls /', 'ls @PARENT@', 'cd /; rm -rf "$T"', 'find . -name x', f'find {REPO_RUN}/specs -name x',
    'grep -rn "/" src', 'cd /private/tmp/phr101/r501/.claude/skills; grep -rniE x .',
])
def test_harmless_listing_and_search_is_valid(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command.replace('@PARENT@', str(ctl.real.parent))})])
    audit = ctl.audit()
    assert audit['valid'] is True, audit


@pytest.mark.parametrize('name, data', [
    ('Glob', {'pattern': '**/SKILL.md', 'path': '/'}),
    ('Glob', {'pattern': '/**/SKILL.md'}),
    ('Grep', {'pattern': 'x', 'path': '/'}),
    ('Grep', {'pattern': 'x', 'path': '@PARENT@'}),
])
def test_tool_search_rooted_at_an_ancestor_voids(ctl: Ctl, name: str, data: dict) -> None:
    data = {k: v.replace('@PARENT@', str(ctl.real.parent)) for k, v in data.items()}
    ctl.rep(main=[(name, data)])
    audit = ctl.audit()
    assert audit['valid'] is False, audit
    assert any('holds the real home' in flag for flag in audit['flags']), audit['flags']


@pytest.mark.parametrize('name, data', [
    ('Glob', {'pattern': '*', 'path': '/'}), ('Glob', {'pattern': '**/*.py'}), ('Grep', {'pattern': 'x'}),
    ('Grep', {'pattern': 'x', 'path': f'{REPO_RUN}/specs'}),
])
def test_tool_search_inside_the_rep_is_valid(ctl: Ctl, name: str, data: dict) -> None:
    ctl.rep(main=[(name, data)])
    assert ctl.audit()['valid'] is True


CLASSIFIER = ('Permission for this action was denied by the Claude Code auto mode classifier. '
              'Reason: [Unauthorized Access]. If you have other tasks ...')
GUARDED = "PreToolUse:Bash hook error: blocked by the workspace path guard: '/x' reaches the real home"


def denial_records(use_id: str, command: str, text: str, sidechain: bool, as_list: bool) -> list[str]:
    '''A tool_use and its denied tool_result, as transcript lines.'''
    content = [{'type': 'text', 'text': text}] if as_list else text
    use = {'type': 'assistant', 'isSidechain': sidechain, 'message': {'content': [
        {'type': 'tool_use', 'id': use_id, 'name': 'Bash', 'input': {'command': command}}]}}
    result = {'type': 'user', 'isSidechain': sidechain, 'message': {'content': [
        {'type': 'tool_result', 'tool_use_id': use_id, 'content': content, 'is_error': True}]}}
    return [json.dumps(use), json.dumps(result)]


def test_denials_come_from_every_transcript_once(ctl: Ctl) -> None:
    out = ctl.rep()
    main = denial_records('tu-main', 'cat secret', CLASSIFIER, False, False)
    sub = denial_records('tu-sub', 'ls /x', GUARDED, True, True)
    allowed = denial_records('tu-ok', 'git status', 'On branch main', False, False)
    with (out / 'project' / 'sid-1.jsonl').open('a') as f:
        f.write('\n'.join(main + allowed) + '\n')
    with (out / 'project' / 'sid-1' / 'subagents' / 'agent-a1.jsonl').open('a') as f:
        f.write('\n'.join(sub) + '\n')
    # The turn's stream-json repeats both, as the real runs do.
    (out / 'turn1.jsonl').write_text('\n'.join(main + sub) + '\n')
    audit = ctl.audit()
    by_id = {d['tool_use_id']: d for d in audit['denials']}
    assert sorted(by_id) == ['tu-main', 'tu-sub'], audit['denials']
    assert len(audit['denials']) == 2, audit['denials']
    assert by_id['tu-main'] == {'tool_name': 'Bash', 'tool_use_id': 'tu-main', 'tool_input': {'command': 'cat secret'},
                                'transcript': 'project/sid-1.jsonl', 'subagent': False}
    assert by_id['tu-sub']['transcript'] == 'project/sid-1/subagents/agent-a1.jsonl'
    assert by_id['tu-sub']['subagent'] is True
    assert by_id['tu-sub']['tool_input'] == {'command': 'ls /x'}
    text = (out / 'extract.md').read_text()
    assert 'tu-main' in text and 'tu-sub' in text


def test_result_record_denial_merges_with_its_transcript_copy(ctl: Ctl) -> None:
    out = ctl.rep()
    with (out / 'project' / 'sid-1.jsonl').open('a') as f:
        f.write('\n'.join(denial_records('tu-1', 'cat secret', CLASSIFIER, False, False)) + '\n')
    ctl.result(REP, 1, {'subtype': 'success', 'is_error': False, 'result': 'r', 'total_cost_usd': 0.5,
                        'permission_denials': [{'tool_name': 'Bash', 'tool_use_id': 'tu-1',
                                                'tool_input': {'command': 'cat secret'}}]})
    audit = ctl.audit()
    assert [d['tool_use_id'] for d in audit['denials']] == ['tu-1'], audit['denials']


def test_denial_scan_skips_a_record_whose_message_is_text(ctl: Ctl) -> None:
    out = ctl.rep()
    (out / 'turn1.jsonl').write_text(json.dumps({'type': 'system', 'subtype': 'notice', 'message': 'plain text'}) + '\n'
                                     + '\n'.join(denial_records('tu-1', 'cat secret', CLASSIFIER, False, False)) + '\n')
    audit = ctl.audit()
    assert [d['tool_use_id'] for d in audit['denials']] == ['tu-1'], audit['denials']


# --- gate fix round 2: comments, reserved words, quoted substitutions, fd numbers ---


@pytest.mark.parametrize('command', [
    '# look\nfind / -name SKILL.md', 'echo a#b; find / -name x', 'for n in a b; do find / -name SKILL.md; done',
    'if true; then grep -r x @PARENT@; fi', '{ find / -name x; }', '! find / -name x',
    'cat "$(find / -name SKILL.md | head -1)"', 'cat "`find / -name SKILL.md`"', 'cd / && ls -R 2>/dev/null',
    'cd / && rg --files 2>/dev/null | grep SKILL',
])
def test_round2_search_forms_void(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command.replace('@PARENT@', str(ctl.real.parent))})])
    audit = ctl.audit()
    assert any('holds the real home' in flag for flag in audit['flags']), audit['flags']


@pytest.mark.parametrize('command', [
    '# find / is slow\nls -la', 'git log --format=%H#%s -3', 'for f in *.md; do grep -n TODO "$f"; done',
    'if [ -d src ]; then rg foo src; fi', 'grep -rn foo src 2>/dev/null', 'du -sh * 2>/dev/null',
    "echo '$(find / -name x)'",
])
def test_round2_harmless_forms_are_valid(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    assert ctl.audit()['valid'] is True


# --- fix round 3: wrapper values, the denial shape, the tally's criteria -------------


@pytest.mark.parametrize('command', [
    'env -u UNUSED find / -name x', 'sudo -u root find / -name x', 'timeout -s KILL 5 find / -name x',
    'echo x | xargs -n 1 find / -name',
])
def test_wrapper_option_values_void(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    flags = ctl.audit()['flags']
    assert any('holds the real home' in flag for flag in flags), flags


@pytest.mark.parametrize('command', ['env FOO=1 ls', 'timeout 5 pytest -q', 'sudo -n true'])
def test_wrapped_harmless_commands_are_valid(ctl: Ctl, command: str) -> None:
    ctl.rep(main=[('Bash', {'command': command})])
    assert ctl.audit()['valid'] is True


def result_line(use_id: str, text: str, is_error: bool) -> str:
    return json.dumps({'type': 'user', 'message': {'content': [
        {'type': 'tool_result', 'tool_use_id': use_id, 'content': text, 'is_error': is_error}]}})


def test_a_result_quoting_the_guard_phrase_is_no_denial(ctl: Ctl) -> None:
    out = ctl.rep()
    quoted = "guard.py:30:PREFIX = 'blocked by the workspace path guard:'"
    lines = denial_records('tu-real', 'ls /x', GUARDED, False, False) + [
        result_line('tu-grep', quoted, False),
        result_line('tu-err', 'grep: x: No such file. ' + quoted, True),
        result_line('tu-cls', 'Note: Permission for this action was denied earlier', False),
    ]
    with (out / 'project' / 'sid-1.jsonl').open('a') as f:
        f.write('\n'.join(lines) + '\n')
    ids = [d['tool_use_id'] for d in ctl.audit()['denials']]
    assert ids == ['tu-real'], ids


def test_a_classifier_denial_needs_the_error_flag(ctl: Ctl) -> None:
    out = ctl.rep()
    lines = [result_line('tu-ok', CLASSIFIER, False), result_line('tu-den', CLASSIFIER, True)]
    with (out / 'project' / 'sid-1.jsonl').open('a') as f:
        f.write('\n'.join(lines) + '\n')
    ids = [d['tool_use_id'] for d in ctl.audit()['denials']]
    assert ids == ['tu-den'], ids


def test_tally_criteria_come_from_the_counted_reps(ctl: Ctl) -> None:
    names = reps(ctl, 'p5a', range(501, 506))
    probe = reps(ctl, 'p5a', range(496, 497), phase='probe')
    rows = [(r, 'F-restate', 'PASS') for r in names] + [(probe[0], 'F-restate', 'PASS'),
                                                          (probe[0], 'X-probe-only', 'FAIL')]
    score(ctl, 'guard101', 'p5a', rows)
    done = tally(ctl, 'guard101')
    assert done.returncode == 0, done.stdout + done.stderr
    assert 'no row for X-probe-only' not in done.stdout, done.stdout
    assert 'PASS (0 of 5 failing)' in done.stdout, done.stdout
