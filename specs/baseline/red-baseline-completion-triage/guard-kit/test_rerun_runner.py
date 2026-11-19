'''Tests for the kit runner: make_reps.py, run_rep.sh and postprocess.py (plan 100, Task 2;
adapted for plan 101, Task 9).

No test runs the real claude. Each test builds a stub claude (a bash script
set as CLAUDE_BIN), a temporary PHR_ROOT, PHR_CTL and PHR_TEMPLATES, a
one-commit template repo and a temporary "real home" (the runner's HOME).
run_rep.sh starts the stub under `env -i`, so the stub sees none of the
test's variables: every path it needs is written into its text.
'''

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parent
RUN_REP = KIT / 'run_rep.sh'
MAKE_REPS = KIT / 'make_reps.py'
KIT_COMMIT = '92f6a379d4bb77ba53adb360f8171ebd9c295ce8'
KIT_SKILLS = sorted([
    'brainstorming', 'writing-plans', 'executing-plans', 'subagent-driven-development',
    'finishing-a-development-branch', 'requesting-code-review', 'receiving-code-review',
    'using-git-worktrees', 'verification-before-completion', 'test-driven-development',
    'derive-roadmap', 'prepare-handoff',
])
FIELD = 'credential_expires_at'
GIT = ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-c', 'commit.gpgsign=false']

STUB = r'''#!/bin/bash
if [ "${1-}" = --version ]; then echo '9.9.9 (stub)'; exit 0; fi
log='@LOG@'
printf '%s\n' "$*" >> "$log"
n=$(wc -l < "$log" | tr -d ' ')
cat > '@DIR@'/stdin.$n
printf '%s\n' "$@" > '@DIR@'/args.$n
sid=''
while [ $# -gt 0 ]; do
  case $1 in --session-id|--resume) sid=$2; shift ;; esac
  shift
done
if [ -f '@DIR@'/actions.sh ]; then . '@DIR@'/actions.sh; fi
proj="$HOME/.claude/projects/$(printf '%s' "$PWD" | tr -c 'A-Za-z0-9' '-')"
mkdir -p "$proj/memory"
printf '{"type":"user","sessionId":"%s"}\n' "$sid" >> "$proj/$sid.jsonl"
printf '# memory\n' > "$proj/memory/MEMORY.md"
printf '{"type":"system","subtype":"init","session_id":"%s","skills":["prepare-handoff"]}\n' "$sid"
printf '{"type":"assistant","message":{"content":[{"type":"text","text":"ok"}]}}\n'
printf '{"type":"result","subtype":"success","is_error":false,"result":"done","session_id":"%s",' "$sid"
printf '"total_cost_usd":0.25,"credential_expires_at":1790000000,'
printf '"modelUsage":{"claude-sonnet-5-5":{"costUSD":0.25,"credential_expires_at":1790000000}}}\n'
'''


class Kit:
    '''One test's temporary world: real home, root, control folder, templates and stub.'''

    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.real = tmp / 'real'
        (self.real / 'Library' / 'Keychains').mkdir(parents=True)
        self.root = tmp / 'root'
        self.ctl = tmp / 'ctl'
        self.templates = tmp / 'templates'
        self.stub_dir = tmp / 'stub'
        self.stub_dir.mkdir()
        self.log = self.stub_dir / 'calls.log'
        self.stub = self.stub_dir / 'claude'
        self.stub.write_text(STUB.replace('@LOG@', str(self.log)).replace('@DIR@', str(self.stub_dir)))
        self.stub.chmod(0o755)
        template = self.templates / 't5'
        template.mkdir(parents=True)
        subprocess.run([*GIT, 'init', '-q', '-b', 'main', str(template)], check=True)
        (template / 'README.md').write_text('fixture\n')
        subprocess.run([*GIT, '-C', str(template), 'add', '-A'], check=True)
        subprocess.run([*GIT, '-C', str(template), 'commit', '-q', '-m', 'init'], check=True)
        head = subprocess.run(['git', '-C', str(template), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True, check=True).stdout.strip()
        self.heads = tmp / 'heads.tsv'
        self.heads.write_text(f'template\thead\nt5\t{head}\n')

    def env(self) -> dict:
        user = os.environ.get('USER') or 'tester'
        return {
            'HOME': str(self.real), 'USER': user, 'LOGNAME': user,
            'PATH': '/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin',
            'PHR_ROOT': str(self.root), 'PHR_CTL': str(self.ctl), 'PHR_TEMPLATES': str(self.templates),
            'PHR_TEMPLATE_HEADS': str(self.heads), 'CLAUDE_BIN': str(self.stub), 'KIT_COMMIT': KIT_COMMIT,
        }

    def actions(self, text: str) -> None:
        (self.stub_dir / 'actions.sh').write_text(text)

    def make_reps(self, arm: str = 'c5a-neg', count: int = 1, batch: str = 'b1') -> list[str]:
        done = subprocess.run(['/usr/bin/python3', str(MAKE_REPS), arm, 'test', str(count), batch],
                              env=self.env(), capture_output=True, text=True, check=False)
        assert done.returncode == 0, done.stderr
        return (self.ctl / 'batches' / f'{batch}.txt').read_text().split()[-count:]

    def run_rep(self, rep: str) -> subprocess.CompletedProcess:
        return subprocess.run(['/bin/bash', str(RUN_REP), rep], env=self.env(), cwd=self.tmp,
                              capture_output=True, text=True, check=False, timeout=300)

    def turns(self) -> list[str]:
        return self.log.read_text().splitlines() if self.log.exists() else []


@pytest.fixture
def kit(tmp_path: Path) -> Kit:
    return Kit(tmp_path)


def run_ok(kit: Kit, rep: str) -> Path:
    done = kit.run_rep(rep)
    assert done.returncode == 0, done.stdout + done.stderr
    return kit.ctl / 'results' / rep


def test_strip_removes_field_everywhere(kit):
    rep, = kit.make_reps()
    out = run_ok(kit, rep)
    files = [p for p in out.rglob('*') if p.is_file()]
    assert files
    holding = [str(p) for p in files if FIELD in p.read_text(errors='replace')]
    assert holding == []
    assert 'total_cost_usd' in json.loads((out / 'turn1.json').read_text())


def test_brief_tree_is_copied(kit):
    kit.actions('mkdir -p "$HOME/.cache/agent-skills/handoffs/other-name"\n'
                'echo brief > "$HOME/.cache/agent-skills/handoffs/other-name/brief.md"\n')
    rep, = kit.make_reps()
    out = run_ok(kit, rep)
    assert (out / 'handoffs' / 'other-name' / 'brief.md').is_file()


def test_second_rep_sees_nothing_of_first(kit):
    first, second = kit.make_reps(count=2)
    listing = kit.tmp / 'listing.txt'
    kit.actions(
        f'rep=$(basename "$HOME")\n'
        f'if [ "$rep" = {first} ]; then\n'
        f'  mkdir -p "$HOME/.cache/agent-skills/handoffs/$rep"\n'
        f'  for d in "$HOME" "$TMPDIR" "$PWD" "$HOME/.cache/agent-skills/handoffs/$rep"; do\n'
        f'    echo x > "$d/MARKER-ONE"\n'
        f'  done\n'
        f'else\n'
        f'  ls -laR \'{kit.root}\' "$HOME" "$TMPDIR" "$HOME/.cache/agent-skills/handoffs" >> \'{listing}\' 2>&1\n'
        f'fi\n')
    run_ok(kit, first)
    run_ok(kit, second)
    text = listing.read_text()
    assert second in text
    assert 'MARKER-ONE' not in text
    assert first not in text
    assert (kit.ctl / 'homes' / first / 'MARKER-ONE').is_file()


def test_refuses_nonempty_root(kit):
    rep, = kit.make_reps()
    kit.root.mkdir(parents=True)
    (kit.root / 'stray').write_text('x\n')
    done = kit.run_rep(rep)
    assert done.returncode == 3, done.stdout + done.stderr
    assert kit.turns() == []


def test_home_holds_kit_and_no_user_files(kit):
    report = kit.tmp / 'home.txt'
    kit.actions(
        f'ls "$HOME/.claude/skills" > \'{report}\'\n'
        f'for f in .claude/CLAUDE.md .claude/settings.json .zshenv; do\n'
        f'  if [ -e "$HOME/$f" ]; then echo "present $f" >> \'{report}\'; fi\n'
        f'done\n'
        f'if [ -L "$HOME/Library/Keychains" ]; then echo link >> \'{report}\'; fi\n')
    rep, = kit.make_reps()
    out = run_ok(kit, rep)
    lines = report.read_text().splitlines()
    first_turn = lines[:lines.index('link') + 1]
    assert first_turn == [*KIT_SKILLS, 'link']
    meta = dict(line.split('=', 1) for line in (out / 'meta.txt').read_text().splitlines() if '=' in line)
    assert meta['kit_sha_before']
    assert meta['kit_sha_before'] == meta['kit_sha_after']


def test_env_holds_no_session_variables(kit):
    envfile = kit.tmp / 'env.txt'
    kit.actions(f'env > \'{envfile}\'\n')
    rep, = kit.make_reps()
    run_ok(kit, rep)
    env = dict(line.split('=', 1) for line in envfile.read_text().splitlines() if '=' in line)
    allowed = {'CLAUDE_CODE_DISABLE_ADVISOR_TOOL', 'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS'}
    assert {name for name in env if name.startswith('CLAUDE')} <= allowed
    assert env['CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS'] == '3600000'  # 60 minutes
    assert [name for name in env if name.startswith('GIT_')] == []  # the runner's own GIT_* identity stays out
    home = os.path.realpath(kit.root / rep)
    assert env['HOME'] == home
    assert env['TMPDIR'] == home + '/tmp'


def test_resume_on_later_turns(kit):
    rep, = kit.make_reps()
    out = run_ok(kit, rep)
    sid = (out / 'session-id').read_text().strip()
    turns = kit.turns()
    assert len(turns) == 2
    assert f'--session-id {sid}' in turns[0]
    assert f'--resume {sid}' in turns[1]
    assert '--session-id' not in turns[1]


# Tests added by the mutant step (plan 100, Task 2): shapes the plan tests leave open.

POSTPROCESS = KIT / 'postprocess.py'
RUN_BATCH = KIT / 'run_batch.sh'


def meta_of(out: Path) -> dict:
    return dict(line.split('=', 1) for line in (out / 'meta.txt').read_text().splitlines() if '=' in line)


def test_make_reps_ids_start_at_r501_and_continue(kit):
    assert kit.make_reps(count=2, batch='a') == ['r501', 'r502']
    assert kit.make_reps(arm='c5a-merged', count=1, batch='b') == ['r503']
    rows = (kit.ctl / 'registry.tsv').read_text().splitlines()
    assert rows[0] == 'rep\tarm\tphase\ttemplate\tkit_commit\tprompts\textra'
    assert rows[1] == f'r501\tc5a-neg\ttest\tt5\t{KIT_COMMIT}\tc5a-neg.t1.txt,c5a.t2-merge.txt\t-'
    assert rows[3] == f'r503\tc5a-merged\ttest\tt4\t{KIT_COMMIT}\tc5a-merged.t1.txt,c5a-merged.t2.txt\tmerged'
    assert (kit.ctl / 'batches' / 'a.txt').read_text() == 'r501\nr502\n'


@pytest.mark.parametrize('folder', ['results', 'homes'])
def test_make_reps_refuses_taken_id(kit, folder):
    (kit.ctl / folder / 'r501').mkdir(parents=True)
    done = subprocess.run(['/usr/bin/python3', str(MAKE_REPS), 'c5a-neg', 'test', '1', 'b1'],
                          env=kit.env(), capture_output=True, text=True, check=False)
    assert done.returncode != 0
    assert 'r501' in done.stderr
    assert not (kit.ctl / 'batches' / 'b1.txt').exists()
    assert (kit.ctl / 'registry.tsv').read_text().splitlines()[1:] == []


def test_make_reps_requires_kit_commit(kit):
    env = kit.env()
    del env['KIT_COMMIT']
    done = subprocess.run(['/usr/bin/python3', str(MAKE_REPS), 'c5a-neg', 'test', '1', 'b1'],
                          env=env, capture_output=True, text=True, check=False)
    assert done.returncode != 0
    assert 'KIT_COMMIT is required' in done.stderr
    assert not (kit.ctl / 'registry.tsv').exists()


def test_rep_command_flags_and_prompt(kit):
    rep, = kit.make_reps()
    out = run_ok(kit, rep)
    sid = (out / 'session-id').read_text().strip()
    args = (kit.stub_dir / 'args.1').read_text().splitlines()
    settings = json.loads(args[args.index('--settings') + 1])
    real = os.path.realpath(kit.real)
    hook = settings['hooks']['PreToolUse'][0]['hooks'][0]['command']
    assert hook == f'/usr/bin/python3 {KIT}/guard.py --real-home {real}'
    assert 'Read(~/Library/**)' in settings['permissions']['deny']
    del args[args.index('--settings'):args.index('--settings') + 2]
    assert args == ['-p', '--session-id', sid, '--setting-sources', 'user,project,local', '--strict-mcp-config',
                    '--model', 'claude-sonnet-5-5', '--effort', 'medium', '--permission-mode', 'auto',
                    '--max-budget-usd', '30', '--output-format', 'stream-json', '--verbose']
    prompt = (out / 'turn1.prompt.txt').read_text()
    assert (kit.stub_dir / 'stdin.1').read_text() == prompt
    assert (kit.stub_dir / 'stdin.2').read_text() == (out / 'turn2.prompt.txt').read_text()
    assert prompt == (KIT / 'prompts' / 'c5a-neg.t1.txt').read_text()


def test_prompt_fills_rep_path(kit):
    # No prompt file of this kit holds @REP@, so the test brings its own prompts folder.
    prompts = kit.tmp / 'prompts'
    prompts.mkdir()
    (prompts / 'c5a-neg.t1.txt').write_text('the plan is at @REP@/specs/plans/4-log-rotation.md\n')
    (prompts / 'c5a.t2-merge.txt').write_text('Merge it locally (option 1).\n')
    env = kit.env()
    env['PHR_PROMPTS'] = str(prompts)
    rep, = kit.make_reps()
    done = subprocess.run(['/bin/bash', str(RUN_REP), rep], env=env, cwd=kit.tmp,
                          capture_output=True, text=True, check=False, timeout=300)
    assert done.returncode == 0, done.stdout + done.stderr
    out = kit.ctl / 'results' / rep
    source = (prompts / 'c5a-neg.t1.txt').read_text()
    repdir = os.path.realpath(kit.root / rep) + f'/work/{rep}'
    assert '@REP@' in source
    assert (out / 'turn1.prompt.txt').read_text() == source.replace('@REP@', repdir)
    assert (kit.stub_dir / 'stdin.1').read_text() == source.replace('@REP@', repdir)


def test_results_layout(kit):
    rep, = kit.make_reps()
    out = run_ok(kit, rep)
    meta = meta_of(out)
    assert meta['rep'] == rep
    assert meta['arm'] == 'c5a-neg'
    assert meta['phase'] == 'test'
    assert meta['template'] == 't5'
    assert meta['kit_commit'] == KIT_COMMIT
    assert meta['model'] == 'claude-sonnet-5-5'
    assert meta['effort'] == 'medium'
    assert meta['claude'] == '9.9.9 (stub)'
    for n in (1, 2):
        assert json.loads((out / f'turn{n}.init.json').read_text())['subtype'] == 'init'
        assert json.loads((out / f'turn{n}.json').read_text())['type'] == 'result'
        assert len((out / f'turn{n}.jsonl').read_text().splitlines()) == 3
        assert (out / f'turn{n}.stderr').is_file()
        git = (out / f'turn{n}.git.txt').read_text()
        assert git.startswith('## branch\nmain\n## status\n## log\n')
    assert (out / 'project' / 'memory' / 'MEMORY.md').is_file()
    sid = (out / 'session-id').read_text().strip()
    assert (out / 'project' / f'{sid}.jsonl').is_file()
    assert (out / 'project').name == 'project'
    assert list(kit.root.iterdir()) == []
    assert (kit.ctl / 'homes' / rep / 'work' / rep / '.git').is_dir()


def test_home_build_details(kit):
    report = kit.tmp / 'build.txt'
    kit.actions(
        f'{{ readlink "$HOME/Library/Keychains"\n'
        f'  ls "$HOME/.claude/agents" "$HOME/.claude/commands"\n'
        f'  ls "$HOME/.local/bin"\n'
        f'  readlink "$HOME/.local/bin/uv"\n'
        f'  git -C "$PWD" rev-parse --abbrev-ref origin/HEAD\n'
        f'  git --git-dir="$HOME/git/$(basename "$HOME").git" rev-parse main\n'
        f'  git -C "$PWD" rev-parse HEAD\n'
        f'  gh pr create --fill\n'
        f'  cat "$HOME/.cache/gh-calls.log" | cut -f3\n'
        f'  echo "pwd=$PWD"\n'
        f'}} > \'{report}\' 2>&1\n')
    rep, = kit.make_reps()
    run_ok(kit, rep)
    lines = report.read_text().splitlines()
    home = os.path.realpath(kit.root / rep)
    assert lines[0] == f'{os.path.realpath(kit.real)}/Library/Keychains'
    assert '\n'.join(lines).count('code-reviewer.md') == 1
    for name in ('task-reviewer.md', 'deferred.md', 'gh', 'git', 'python3', 'python3.13', 'uv'):
        assert name in lines, name
    assert '/opt/homebrew/bin/uv' in lines
    assert 'origin/main' in lines
    heads = [line for line in lines if len(line) == 40]
    assert len(heads) == 2 and heads[0] == heads[1]
    assert 'https://example.invalid/pondworks/pull/17' in lines
    assert 'pr create --fill' in lines
    assert f'pwd={home}/work/{rep}' in lines


def test_failed_turn_stops_later_turns(kit):
    kit.actions('exit 1\n')
    rep, = kit.make_reps()
    out = run_ok(kit, rep)
    assert len(kit.turns()) == 1
    assert 'turn 1 exited 1; later turns not run' in (out / 'meta.txt').read_text()
    assert not (out / 'turn2.prompt.txt').exists()
    assert (out / 'turn1.git.txt').is_file()
    assert 'kit_sha_after' in meta_of(out)


def test_kit_change_shows_in_after_hash(kit):
    kit.actions('echo changed >> "$HOME/.claude/skills/prepare-handoff/SKILL.md"\n')
    rep, = kit.make_reps()
    meta = meta_of(run_ok(kit, rep))
    assert len(meta['kit_sha_before']) == 64
    assert len(meta['kit_sha_after']) == 64
    assert meta['kit_sha_before'] != meta['kit_sha_after']


def test_kit_file_list_shows_in_after_hash(kit):
    kit.actions('mv "$HOME/.claude/commands/deferred.md" "$HOME/.claude/commands/other.md"\n')
    rep, = kit.make_reps()
    meta = meta_of(run_ok(kit, rep))
    assert meta['kit_sha_before'] != meta['kit_sha_after']


def test_unstripped_field_fails_the_rep(kit):
    kit.actions(f"echo 'not json {FIELD}'\n")
    rep, = kit.make_reps()
    done = kit.run_rep(rep)
    assert done.returncode == 4
    assert 'kit_error=' in (kit.ctl / 'results' / rep / 'meta.txt').read_text()
    assert list(kit.root.iterdir()) == []


@pytest.mark.parametrize('spoil', ['head', 'ref', 'dirty', 'untracked'])
def test_refuses_bad_template(kit, spoil):
    template = kit.templates / 't5'
    if spoil == 'head':
        kit.heads.write_text('template\thead\nt5\t' + '0' * 40 + '\n')
    elif spoil == 'ref':
        subprocess.run(['git', '-C', str(template), 'branch', 'extra'], check=True)
    elif spoil == 'dirty':
        (template / 'README.md').write_text('changed\n')
    else:
        (template / 'new.txt').write_text('new\n')
    rep, = kit.make_reps()
    done = kit.run_rep(rep)
    assert done.returncode == 2, done.stdout + done.stderr
    assert kit.turns() == []
    assert not (kit.ctl / 'results' / rep).exists()


def test_refuses_a_rep_that_ran(kit):
    rep, = kit.make_reps()
    run_ok(kit, rep)
    done = kit.run_rep(rep)
    assert done.returncode == 2
    assert len(kit.turns()) == 2


def test_refuses_unregistered_rep(kit):
    kit.make_reps()
    done = kit.run_rep('r999')
    assert done.returncode == 2
    assert kit.turns() == []


def test_run_batch_runs_in_order_and_skips_done(kit):
    reps = kit.make_reps(count=3)
    (kit.ctl / 'results' / reps[1]).mkdir(parents=True)
    done = subprocess.run(['/bin/bash', str(RUN_BATCH), 'b1'], env=kit.env(), cwd=kit.tmp,
                          capture_output=True, text=True, check=False, timeout=300)
    assert done.returncode == 0, done.stdout + done.stderr
    ran = [line.split()[2] for line in kit.turns() if '--session-id' in line]
    sids = [(kit.ctl / 'results' / r / 'session-id').read_text().strip() for r in (reps[0], reps[2])]
    assert ran == sids
    assert f'skip {reps[1]}' in done.stderr


def test_run_batch_stops_at_a_refusal(kit):
    reps = kit.make_reps(count=2)
    kit.root.mkdir(parents=True)
    (kit.root / 'stray').write_text('x\n')
    done = subprocess.run(['/bin/bash', str(RUN_BATCH), 'b1'], env=kit.env(), cwd=kit.tmp,
                          capture_output=True, text=True, check=False, timeout=300)
    assert done.returncode == 3
    assert kit.turns() == []
    assert done.stderr.count('is not empty') == 1


def test_strip_tree_nested(tmp_path):
    (tmp_path / 'a').mkdir()
    (tmp_path / 'a' / 'x.json').write_text(json.dumps({'k': [{FIELD: 1, 'keep': 2}], FIELD: 3}))
    (tmp_path / 'a' / 'y.jsonl').write_text(
        json.dumps({'m': {'n': {FIELD: 1}}}) + '\n' + '{"plain": 1}\n')
    (tmp_path / 'z.txt').write_text(FIELD)
    done = subprocess.run(['/usr/bin/python3', str(POSTPROCESS), 'strip-tree', str(tmp_path)],
                          capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stderr
    assert json.loads((tmp_path / 'a' / 'x.json').read_text()) == {'k': [{'keep': 2}]}
    lines = (tmp_path / 'a' / 'y.jsonl').read_text().splitlines()
    assert [json.loads(line) for line in lines] == [{'m': {'n': {}}}, {'plain': 1}]
    assert lines[1] == '{"plain": 1}'
    assert (tmp_path / 'z.txt').read_text() == FIELD


def test_split_picks_records(tmp_path):
    stream = tmp_path / 's.jsonl'
    stream.write_text('\n'.join([
        json.dumps({'type': 'system', 'subtype': 'hook', 'n': 0}),
        json.dumps({'type': 'system', 'subtype': 'init', 'n': 1, FIELD: 1}),
        'not json',
        json.dumps({'type': 'result', 'n': 2}),
        json.dumps({'type': 'result', 'n': 3, 'u': {FIELD: 1}}),
    ]) + '\n')
    done = subprocess.run(['/usr/bin/python3', str(POSTPROCESS), 'split', str(stream), str(tmp_path / 'o'), '4'],
                          capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stderr
    assert json.loads((tmp_path / 'o' / 'turn4.json').read_text()) == {'type': 'result', 'n': 3, 'u': {}}
    assert json.loads((tmp_path / 'o' / 'turn4.init.json').read_text()) == {
        'type': 'system', 'subtype': 'init', 'n': 1}
    lines = (tmp_path / 'o' / 'turn4.jsonl').read_text().splitlines()
    assert len(lines) == 5
    assert lines[2] == 'not json'
    assert FIELD not in '\n'.join(lines)


# Tests added in review fix round 1 (plan 100, Task 2).

OLD_KIT_COMMIT = 'd778c3e58a5684abf0c6048a12b45718756f4c9e'
DENY = ['Read(//Users/**)', 'Edit(//Users/**)', 'Write(//Users/**)',
        'Read(~/Library/**)', 'Edit(~/Library/**)', 'Write(~/Library/**)']


def test_settings_deny_rules_are_the_plans_six(kit):
    rep, = kit.make_reps()
    run_ok(kit, rep)
    args = (kit.stub_dir / 'args.1').read_text().splitlines()
    settings = json.loads(args[args.index('--settings') + 1])
    assert settings['permissions']['deny'] == DENY


def test_settings_turn_off_claude_ai_skill_sync(kit):
    # Plan 100 D4: the account's claude.ai skills must not reach a rep.
    rep, = kit.make_reps()
    run_ok(kit, rep)
    args = (kit.stub_dir / 'args.1').read_text().splitlines()
    settings = json.loads(args[args.index('--settings') + 1])
    assert settings['syncClaudeAiSkills'] is False
    assert sorted(settings) == ['hooks', 'permissions', 'syncClaudeAiSkills']


def test_prompt_fills_real_home(kit):
    prompts = kit.tmp / 'prompts'
    prompts.mkdir()
    (prompts / 'c5a-neg.t1.txt').write_text('real @REAL@/.claude rep @REP@\n')
    (prompts / 'c5a.t2-merge.txt').write_text('second @REAL@\n')
    env = kit.env()
    env['PHR_PROMPTS'] = str(prompts)
    rep, = kit.make_reps()
    done = subprocess.run(['/bin/bash', str(RUN_REP), rep], env=env, cwd=kit.tmp,
                          capture_output=True, text=True, check=False, timeout=300)
    assert done.returncode == 0, done.stdout + done.stderr
    out = kit.ctl / 'results' / rep
    real = os.path.realpath(kit.real)
    repdir = os.path.realpath(kit.root / rep) + f'/work/{rep}'
    assert (out / 'turn1.prompt.txt').read_text() == f'real {real}/.claude rep {repdir}\n'
    assert (out / 'turn2.prompt.txt').read_text() == f'second {real}\n'


def test_kit_comes_from_the_registry_commit(kit):
    env = kit.env()
    env['KIT_COMMIT'] = OLD_KIT_COMMIT
    done = subprocess.run(['/usr/bin/python3', str(MAKE_REPS), 'c5a-neg', 'test', '1', 'b1'],
                          env=env, capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stderr
    rep = (kit.ctl / 'batches' / 'b1.txt').read_text().split()[0]
    out = run_ok(kit, rep)  # kit.env() keeps KIT_COMMIT at the newer commit
    want = subprocess.run(['git', '-C', str(KIT), 'show', f'{OLD_KIT_COMMIT}:skills/prepare-handoff/SKILL.md'],
                          capture_output=True, text=True, check=True).stdout
    home = kit.ctl / 'homes' / rep
    assert (home / '.claude' / 'skills' / 'prepare-handoff' / 'SKILL.md').read_text() == want
    meta = meta_of(out)
    assert meta['kit_commit'] == OLD_KIT_COMMIT
    assert meta['kit_sha_before'] == meta['kit_sha_after']


def test_rep_git_identity_is_the_placeholder(kit):
    report = kit.tmp / 'git-id.txt'
    kit.actions(f'{{ git config user.name; git config user.email; git config --global --list; }} > \'{report}\' 2>&1\n')
    rep, = kit.make_reps()
    run_ok(kit, rep)
    lines = report.read_text().splitlines()
    assert lines[:2] == ['Pondworks Rep', 'rep@pondworks.invalid']
    assert sorted(lines[2:]) == ['user.email=rep@pondworks.invalid', 'user.name=Pondworks Rep']
    assert (kit.ctl / 'homes' / rep / '.gitconfig').read_text() == \
        '[user]\n\tname = Pondworks Rep\n\temail = rep@pondworks.invalid\n'


def test_many_transcript_matches_do_not_kill_the_runner(kit):
    '''Before the fix, `find | head -n 1` under pipefail died with SIGPIPE (141)
    when find wrote more than a pipe buffer after head had exited. Enough
    matching transcripts make that certain.'''
    kit.actions(
        'if [ ! -d "$HOME/.claude/projects/z0000" ]; then\n'
        '  i=0; while [ $i -lt 1500 ]; do\n'
        '    d="$HOME/.claude/projects/z$(printf %04d $i)-$(printf %060d 0)"; mkdir -p "$d"\n'
        '    printf \'{"type":"user"}\\n\' > "$d/$sid.jsonl"; i=$((i + 1)); done\n'
        '  mkdir -p "$HOME/.claude/projects/z0000"\n'
        'fi\n')
    rep, = kit.make_reps()
    out = run_ok(kit, rep)
    sid = (out / 'session-id').read_text().strip()
    assert (out / 'project' / f'{sid}.jsonl').is_file()


# Plan 101 tests (Task 9): the merged extra, the registry's extra column, the first id and the template pins.

FEATURE = 'feat/s2a-csv-export'


def make_t4(kit: Kit) -> tuple[str, str]:
    '''A template named t4: main and FEATURE one commit ahead, HEAD on FEATURE. Pins it in the heads file.'''
    template = kit.templates / 't4'
    template.mkdir(parents=True)
    subprocess.run([*GIT, 'init', '-q', '-b', 'main', str(template)], check=True)
    (template / 'README.md').write_text('fixture\n')
    subprocess.run([*GIT, '-C', str(template), 'add', '-A'], check=True)
    subprocess.run([*GIT, '-C', str(template), 'commit', '-q', '-m', 'init'], check=True)
    subprocess.run([*GIT, '-C', str(template), 'checkout', '-q', '-b', FEATURE], check=True)
    (template / 'export.py').write_text('def write_table(rows, path, columns=None): ...\n')
    subprocess.run([*GIT, '-C', str(template), 'add', '-A'], check=True)
    subprocess.run([*GIT, '-C', str(template), 'commit', '-q', '-m', 'feat: csv export'], check=True)
    head = subprocess.run(['git', '-C', str(template), 'rev-parse', 'HEAD'],
                          capture_output=True, text=True, check=True).stdout.strip()
    refs = subprocess.run(['git', '-C', str(template), 'for-each-ref', '--format=%(refname)=%(objectname)'],
                          capture_output=True, text=True, check=True).stdout.split()
    pin = ','.join(refs)
    kit.heads.write_text(kit.heads.read_text() + f't4\t{head}\t{pin}\n')
    return head, pin


def test_merged_extra_starts_on_merged_main(kit):
    make_t4(kit)
    report = kit.tmp / 'merged.txt'
    kit.actions(
        'if [ "$n" = 1 ]; then\n'
        '  { git log --format=%s -1\n'
        "    git branch --format='%(refname:short)'\n"
        '    git rev-parse main origin/main\n'
        '    git --git-dir="$HOME/git/$(basename "$HOME").git" rev-parse main\n'
        "    git log -1 --format='%an|%ae|%cn|%ce'\n"
        f"  }} > '{report}' 2>&1\n"
        'fi\n')
    rep, = kit.make_reps(arm='c5a-merged')
    run_ok(kit, rep)
    lines = report.read_text().splitlines()
    assert lines[0] == f"Merge branch '{FEATURE}'"
    assert lines[1] == 'main'
    assert len(lines[2]) == 40 and lines[2] == lines[3] == lines[4]  # main, origin/main, the bare repo's main
    assert lines[5] == 'Pondworks Rep|rep@pondworks.invalid|Pondworks Rep|rep@pondworks.invalid'
    assert len(lines) == 6, lines


def test_unknown_extra_refuses(kit):
    kit.ctl.mkdir(parents=True)
    (kit.ctl / 'registry.tsv').write_text(
        'rep\tarm\tphase\ttemplate\tkit_commit\tprompts\textra\n'
        f'r501\tc5a-neg\ttest\tt5\t{KIT_COMMIT}\tc5a-neg.t1.txt,c5a.t2-merge.txt\tother\n')
    done = kit.run_rep('r501')
    assert done.returncode == 3, done.stdout + done.stderr
    assert 'other' in done.stderr
    assert kit.turns() == []
    # The refusal comes before any HOME is built. A HOME built first would be parked in homes/r501
    # by the cleanup trap, and that burned id would block a rerun.
    assert not (kit.ctl / 'homes' / 'r501').exists()
    assert not (kit.ctl / 'results' / 'r501').exists()
    assert not kit.root.exists() or list(kit.root.iterdir()) == []


def test_ids_start_at_r501(kit):
    assert kit.ctl.exists() is False
    rep, = kit.make_reps()
    assert rep == 'r501'
    assert (kit.ctl / 'registry.tsv').read_text().splitlines()[1].split('\t')[0] == 'r501'


def test_template_refs_pin_refuses_an_unpinned_ref(kit):
    template = kit.templates / 't5'
    subprocess.run(['git', '-C', str(template), 'branch', 'extra'], check=True)
    head, = [row.split('\t')[1] for row in kit.heads.read_text().splitlines()[1:]]
    main_only = f'refs/heads/main={head}'
    kit.heads.write_text(f'template\thead\trefs\nt5\t{head}\t{main_only}\n')
    rep, = kit.make_reps()
    done = kit.run_rep(rep)
    assert done.returncode == 2, done.stdout + done.stderr
    assert kit.turns() == []
    assert not (kit.ctl / 'results' / rep).exists()
    # The same template runs once its pin lists the extra ref.
    kit.heads.write_text(f'template\thead\trefs\nt5\t{head}\trefs/heads/extra={head},{main_only}\n')
    run_ok(kit, rep)
    assert len(kit.turns()) == 2


def test_template_refs_pin_refuses_a_moved_main(kit):
    head, = [row.split('\t')[1] for row in kit.heads.read_text().splitlines()[1:]]
    kit.heads.write_text(f'template\thead\trefs\nt5\t{head}\trefs/heads/main={"0" * 40}\n')
    rep, = kit.make_reps()
    done = kit.run_rep(rep)
    assert done.returncode == 2, done.stdout + done.stderr
    assert kit.turns() == []
    assert not (kit.ctl / 'results' / rep).exists()


# Follow-up tests (Task 9): the start refs that meta.txt records for the audit.


def template_start_refs(template: Path) -> str:
    refs = subprocess.run(['git', '-C', str(template), 'for-each-ref', '--format=%(refname:short)=%(objectname)',
                           'refs/heads'], capture_output=True, text=True, check=True).stdout.split()
    return ','.join(refs)


def test_meta_records_both_t4_refs_as_the_start_refs(kit):
    make_t4(kit)
    rep, = kit.make_reps(arm='p5a')
    meta = meta_of(run_ok(kit, rep))
    want = template_start_refs(kit.templates / 't4')
    assert want.count(',') == 1 and want.startswith(f'{FEATURE}=') and ',main=' in want
    assert meta['start_refs'] == want


def test_meta_records_the_merged_main_as_the_only_start_ref(kit):
    make_t4(kit)
    rep, = kit.make_reps(arm='c5a-merged')
    meta = meta_of(run_ok(kit, rep))
    repo = kit.ctl / 'homes' / rep / 'work' / rep
    merge = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'main'], capture_output=True, text=True,
                           check=True).stdout.strip()
    subject = subprocess.run(['git', '-C', str(repo), 'log', '-1', '--format=%s', merge], capture_output=True,
                             text=True, check=True).stdout.strip()
    assert subject == f"Merge branch '{FEATURE}'"
    assert meta['start_refs'] == f'main={merge}'


SENTINEL_NAME = 'Sentinel Owner Zq'
SENTINEL_EMAIL = 'sentinel.owner.zq@example.invalid'
# A reflog line: <old sha> <new sha> <Name> <<email>> <timestamp> <tz><TAB><message>
REFLOG_LINE = re.compile(r'^[0-9a-f]{40} [0-9a-f]{40} (?P<who>.+? <[^<>]*>) \d+ [+-]\d{4}\t(?P<what>.*)$')
# The placeholder, and the identity that this test's fixture templates are built with.
ALLOWED_IDENTITIES = {'Pondworks Rep <rep@pondworks.invalid>', 't <t@example.invalid>'}


def reflog_entries(home: Path, rep: str) -> list[tuple[str, str, str]]:
    '''(file relative to the parked home, identity, message) for every entry of every reflog file of the
    parked rep repo and of its bare origin.'''
    entries = []
    for folder in (home / 'work' / rep / '.git' / 'logs', home / 'git' / f'{rep}.git' / 'logs'):
        for path in sorted(folder.rglob('*')) if folder.is_dir() else []:
            if not path.is_file():
                continue
            for line in path.read_text().splitlines():
                hit = REFLOG_LINE.match(line)
                assert hit, f'{path.relative_to(home)} has a reflog line that does not parse'
                entries.append((str(path.relative_to(home)), hit['who'], hit['what']))
    return entries


def test_no_real_git_identity_reaches_a_rep_repo(kit):
    # The runner runs with the real HOME, so a git call that writes a reflog entry would stamp the owner's identity.
    # The runner sets the placeholder through GIT_AUTHOR_* and GIT_COMMITTER_*. `-c user.*` is not enough:
    # `git remote set-head` ignores user.* config and writes the account's passwd name and a host-derived email.
    (kit.real / '.gitconfig').write_text(f'[user]\n\tname = {SENTINEL_NAME}\n\temail = {SENTINEL_EMAIL}\n')
    make_t4(kit)
    plain, = kit.make_reps(arm='c5a-neg', batch='plain')
    merged, = kit.make_reps(arm='c5a-merged', batch='merged')
    run_ok(kit, plain)
    run_ok(kit, merged)
    holding, outside = [], []
    for rep in (plain, merged):
        home = kit.ctl / 'homes' / rep
        files = [p for folder in (home / 'work' / rep / '.git', home / 'git' / f'{rep}.git')
                 for p in folder.rglob('*') if p.is_file()]
        assert any(p.name == 'HEAD' for p in files)
        holding += [str(p.relative_to(kit.ctl / 'homes')) for p in files
                    if SENTINEL_NAME.encode() in p.read_bytes() or SENTINEL_EMAIL.encode() in p.read_bytes()]
        entries = reflog_entries(home, rep)
        parsed = {path for path, _, _ in entries}
        assert f'work/{rep}/.git/logs/refs/remotes/origin/HEAD' in parsed  # the file that remote set-head writes
        outside += [(path, what) for path, who, what in entries if who not in ALLOWED_IDENTITIES]
    assert holding == []
    assert outside == [], 'reflog entries by an identity outside the allow list'
