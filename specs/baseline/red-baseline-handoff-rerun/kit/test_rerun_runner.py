'''Tests for the kit runner: make_reps.py, run_rep.sh and postprocess.py (plan 100, Task 2).

No test runs the real claude. Each test builds a stub claude (a bash script
set as CLAUDE_BIN), a temporary PHR_ROOT, PHR_CTL and PHR_TEMPLATES, a
one-commit template repo and a temporary "real home" (the runner's HOME).
run_rep.sh starts the stub under `env -i`, so the stub sees none of the
test's variables: every path it needs is written into its text.
'''

from __future__ import annotations

import json
import os
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
printf '"modelUsage":{"claude-opus-5-5":{"costUSD":0.25,"credential_expires_at":1790000000}}}\n'
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
        template = self.templates / 't3'
        template.mkdir(parents=True)
        subprocess.run([*GIT, 'init', '-q', '-b', 'main', str(template)], check=True)
        (template / 'README.md').write_text('fixture\n')
        subprocess.run([*GIT, '-C', str(template), 'add', '-A'], check=True)
        subprocess.run([*GIT, '-C', str(template), 'commit', '-q', '-m', 'init'], check=True)
        head = subprocess.run(['git', '-C', str(template), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True, check=True).stdout.strip()
        self.heads = tmp / 'heads.tsv'
        self.heads.write_text(f'template\thead\nt3\t{head}\n')

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

    def make_reps(self, arm: str = 'c4a-neg', count: int = 1, batch: str = 'b1') -> list[str]:
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
