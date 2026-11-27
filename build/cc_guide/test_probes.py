'''Tests for probes.py: R10.4's command lines and isolation, the run
directory and the PROBES.md row each probe leaves (R10.6), the version
refusal (R10.3), which probes run, and binaries. Every claude here is a
fake, so no test spends a token or reads the real ~/.claude.'''
import builtins
import contextlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import probe_checks
import probe_process
import probes
import state
import test_probe_checks as tpc
from cc_fixtures import MANIFEST_TOML, isolated_home, write_tree  # noqa: F401
from state import DIVERGES, ERROR, PASS

REPO = Path(__file__).resolve().parents[2]
PROBES_PY = Path(probes.__file__).resolve()
NOW = datetime(2026, 10, 20, 14, 0, tzinfo=timezone.utc)
TODAY = NOW.date()
REGISTRY = '\n'.join(['', '[[probe]]', "id = 'agent-tools'", "sections = ['beta.reference']", '',
                      '[[probe]]', "id = 'stop-continuation'", "sections = ['beta.reference']", ''])


def stream(*events) -> str:
    return ''.join(json.dumps(e) + '\n' for e in events)


def init(tools=('Read', 'Bash'), session='s-1'):
    return {'type': 'system', 'subtype': 'init', 'tools': list(tools), 'session_id': session}


RESULT = {'type': 'result', 'subtype': 'success', 'is_error': False}
TOOLS_PASS = {'probe-with-bash': stream(init(), RESULT),
              'probe-without-bash': stream(init(('Read', 'Grep', 'Glob')), RESULT)}
STOP_PASS = stream(init(), *[{'type': 'system', 'subtype': 'hook_response', 'hook_event': 'Stop', 'exit_code': c}
                             for c in (2, 2, 0)], RESULT)


class FakeRuns:
    '''An Execute that writes each invocation's canned stdout, runs its side
    effect in the scratch directory, and records what it ran.'''

    def __init__(self, streams, side=None, timeout=()):
        self.streams, self.side, self.timeout, self.ran = streams, side or {}, set(timeout), []

    def __call__(self, inv, cwd, out, err):
        self.ran.append((inv, cwd, sorted(p.relative_to(cwd).as_posix() for p in cwd.rglob('*'))))
        out.write_text('' if inv.name in self.timeout else self.streams.get(inv.name, ''), encoding='utf-8')
        err.write_text('', encoding='utf-8')
        if inv.name in self.timeout:
            return None
        if inv.name in self.side:
            self.side[inv.name](cwd)
        return 0


def stop_log(*lines):
    return lambda cwd: (cwd / 'stop.log').write_text(''.join(f'{line}\n' for line in lines), encoding='utf-8')


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / 'repo'
    write_tree(root, {state.MANIFEST: MANIFEST_TOML + REGISTRY})
    return root


@pytest.fixture
def claude(tmp_path):
    path = tmp_path / 'bin' / 'claude'
    path.parent.mkdir()
    path.write_text('#!/bin/sh\nexit 0\n')
    path.chmod(0o755)
    return path


@pytest.fixture(autouse=True)
def no_alias_remaps(monkeypatch):
    '''A remap in the machine running the suite would add its name to every row; each test starts without one.'''
    for name in probe_process.ALIAS_REMAPS:
        monkeypatch.delenv(name, raising=False)


def run(repo, tmp_path, claude, fake, *, only=None, force=False, allow_old=False, version='2.1.902'):
    return probes.run(repo, tmp_path / 'cache', claude, only=only, force=force, allow_old=allow_old,
                      newest='2.1.902', today=TODAY, now=NOW, execute=fake, version_of=lambda path: version)


def test_a_log_with_no_probe_table_refuses_before_any_probe_runs(repo, tmp_path, claude):
    write_tree(repo, {state.PROBES: '# Probes\n\n| Term | Meaning |\n|---|---|\n| PASS | ok |\n'})
    calls = []
    with pytest.raises(state.SetupError, match='no probe log table'):
        run(repo, tmp_path, claude, lambda *a, **k: calls.append(a))
    assert calls == []


def test_the_command_line_follows_r10_4():
    argv = probes.claude_args('/bin/claude', 'Say OK.', turns=2, sources='project', mode='default')
    assert argv[:3] == ['/bin/claude', 'Say OK.', '-p']
    flags = {a: argv[i + 1] for i, a in enumerate(argv[:-1]) if a.startswith('--') and not argv[i + 1].startswith('--')}
    assert flags['--output-format'] == 'stream-json' and flags['--setting-sources'] == 'project'
    assert json.loads(flags['--settings']) == {'permissions': {'defaultMode': 'default'}}
    assert (flags['--model'], flags['--effort'], flags['--max-turns']) == ('sonnet', 'low', '2')
    assert argv[-1] == '--no-session-persistence'
    kept = probes.claude_args('c', 'p', turns=1, sources='user', mode='auto', allow=('Agent',), persist=True,
                              extra=('--x',))
    assert '--no-session-persistence' not in kept and kept[-1] == '--x'
    assert json.loads(kept[kept.index('--settings') + 1]) == {'permissions': {'defaultMode': 'auto',
                                                                              'allow': ['Agent']}}


def test_a_pass_appends_a_row_from_a_fresh_scratch_directory_that_is_then_removed(repo, tmp_path, claude):
    fake = FakeRuns(TOOLS_PASS)
    code, lines = run(repo, tmp_path, claude, fake, only=['agent-tools'])
    assert code == 0
    (first, cwd, files), (second, cwd2, _) = fake.ran
    assert cwd == cwd2 and not cwd.exists() and not cwd.is_relative_to(repo)
    assert cwd.name.startswith('cc-guide-probe-agent-tools-')
    assert files == ['.claude', '.claude/agents', '.claude/agents/probe-with-bash.md',
                     '.claude/agents/probe-without-bash.md']
    assert (first.name, first.argv[-3:]) == ('probe-with-bash', ['--agent', 'probe-with-bash',
                                                                 '--no-session-persistence'])
    rows = state.parse_probes((repo / state.PROBES).read_text())
    assert rows == [state.ProbeRow(TODAY, '2.1.902', 'agent-tools', PASS)]
    run_dir = tmp_path / 'cache' / 'probes' / '20261020T140000-agent-tools'
    assert sorted(p.name for p in run_dir.iterdir()) == [
        'probe-with-bash.argv.json', 'probe-with-bash.err', 'probe-with-bash.jsonl',
        'probe-without-bash.argv.json', 'probe-without-bash.err', 'probe-without-bash.jsonl']
    assert lines == [f'probes: 2.1.902 at {claude}',
                     'agent-tools: PASS: with Bash: Bash, Read; without Bash: Glob, Grep, Read',
                     f'  raw output: {run_dir}', f'appended 1 row(s) to {state.PROBES}; nothing is committed']


def test_two_runs_in_one_second_each_get_a_run_directory_of_their_own(repo, tmp_path, claude):
    '''Two runs that start in the same second, from two worktrees or a
    scripted loop, must not share a run directory: the second would
    truncate the first's streams, and assess could read the other run's.'''
    other = {**TOOLS_PASS, 'probe-with-bash': stream(init(session='s-2'), RESULT)}
    lines = [line for fake in (FakeRuns(TOOLS_PASS), FakeRuns(other))
             for line in run(repo, tmp_path, claude, fake, only=['agent-tools'])[1]]
    dirs = [Path(line.removeprefix('  raw output: ')) for line in lines if line.startswith('  raw output: ')]
    probes_dir = tmp_path / 'cache' / 'probes'
    assert dirs == [probes_dir / '20261020T140000-agent-tools', probes_dir / '20261020T140000-agent-tools-2']
    assert [(d / 'probe-with-bash.jsonl').read_text() for d in dirs] == [TOOLS_PASS['probe-with-bash'],
                                                                         other['probe-with-bash']]


def test_a_divergence_or_an_error_exits_one_and_is_logged(repo, tmp_path, claude):
    fake = FakeRuns({'stop': STOP_PASS, **TOOLS_PASS}, side={'stop': stop_log('false', 'false', 'true')},
                    timeout=['probe-with-bash'])
    code, lines = run(repo, tmp_path, claude, fake, force=True)
    assert code == 1
    rows = state.parse_probes((repo / state.PROBES).read_text())
    assert [(r.probe, r.outcome) for r in rows] == [('agent-tools', ERROR), ('stop-continuation', DIVERGES)]
    assert 'agent-tools: ERROR: probe-with-bash timed out after 600 s' in lines
    assert 'stop-continuation: DIVERGES: stop_hook_active read false, false, true' in lines


def test_an_old_binary_is_refused_unless_allowed_and_the_row_records_the_flag(repo, tmp_path, claude):
    with pytest.raises(state.SetupError) as err:
        run(repo, tmp_path, claude, FakeRuns(TOOLS_PASS), only=['agent-tools'], version='2.1.901')
    assert str(err.value) == (f'--claude {claude} is 2.1.901, older than the newest changelog release 2.1.902: '
                              'pass --allow-old to run it anyway, and each row records the flag (R10.3)')
    assert not (repo / state.PROBES).exists()
    run(repo, tmp_path, claude, FakeRuns(TOOLS_PASS), only=['agent-tools'], version='2.1.901', allow_old=True)
    assert (repo / state.PROBES).read_text().split('\n')[-2].endswith('| agent-tools | PASS |'
                                                                     ' with Bash: Bash, Read; without Bash: Glob, Grep,'
                                                                     ' Read | --allow-old |')


TOOLS_ROW_TAIL = '| agent-tools | PASS | with Bash: Bash, Read; without Bash: Glob, Grep, Read |'


def last_row(repo) -> str:
    return (repo / state.PROBES).read_text().split('\n')[-2]


def test_a_run_with_no_alias_remap_leaves_the_flags_cell_empty(repo, tmp_path, claude):
    run(repo, tmp_path, claude, FakeRuns(TOOLS_PASS), only=['agent-tools'])
    assert last_row(repo).endswith(f'{TOOLS_ROW_TAIL}  |')


def test_an_inherited_alias_remap_is_named_in_the_row_and_its_value_is_not(repo, tmp_path, claude, monkeypatch):
    '''A remap decides which model an alias serves (guide, lean.model-routing), so a DIVERGES from
    agent-model-pins can only be read against it. The log is committed to a public repo: the name goes in
    the row and the value, which can be a provider's model path, never does.'''
    monkeypatch.setenv('ANTHROPIC_DEFAULT_HAIKU_MODEL', 'arn:aws:bedrock:zz:123456789012:profile/not-haiku')
    run(repo, tmp_path, claude, FakeRuns(TOOLS_PASS), only=['agent-tools'])
    assert last_row(repo).endswith(f'{TOOLS_ROW_TAIL} ANTHROPIC_DEFAULT_HAIKU_MODEL |')
    assert 'bedrock' not in (repo / state.PROBES).read_text()
    assert [r.outcome for r in state.parse_probes((repo / state.PROBES).read_text())] == [PASS]


def test_every_inherited_alias_remap_is_named_after_the_allow_old_flag(repo, tmp_path, claude, monkeypatch):
    for name in probe_process.ALIAS_REMAPS:
        monkeypatch.setenv(name, 'a-model')
    monkeypatch.setenv('ANTHROPIC_DEFAULT_MODEL', 'a-model')  # the default model, not an alias remap
    monkeypatch.setenv('CLAUDE_CODE_SUBAGENT_MODEL', 'a-model')  # outranked by an agent's model field
    run(repo, tmp_path, claude, FakeRuns(TOOLS_PASS), only=['agent-tools'], version='2.1.901', allow_old=True)
    assert last_row(repo).endswith(f'{TOOLS_ROW_TAIL} --allow-old ANTHROPIC_DEFAULT_OPUS_MODEL '
                                   'ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL '
                                   'ANTHROPIC_DEFAULT_FABLE_MODEL |')


def test_an_empty_alias_remap_remaps_nothing_and_is_not_named(repo, tmp_path, claude, monkeypatch):
    monkeypatch.setenv('ANTHROPIC_DEFAULT_HAIKU_MODEL', '')
    monkeypatch.setenv('ANTHROPIC_DEFAULT_OPUS_MODEL', 'a-model')
    run(repo, tmp_path, claude, FakeRuns(TOOLS_PASS), only=['agent-tools'])
    assert last_row(repo).endswith(f'{TOOLS_ROW_TAIL} ANTHROPIC_DEFAULT_OPUS_MODEL |')


def test_only_force_and_the_due_rules_choose_the_probes(repo, tmp_path, claude):
    write_tree(repo, {state.PROBES: probes.LOG_TEXT + '| 2026-10-19 | 2.1.902 | ~/c | agent-tools | PASS | ok | |\n'})
    fake = FakeRuns({'stop': STOP_PASS}, side={'stop': stop_log('false', 'true', 'true')})
    assert run(repo, tmp_path, claude, fake)[0] == 0
    assert [inv.name for inv, _, _ in fake.ran] == ['stop']
    fake = FakeRuns(TOOLS_PASS)
    run(repo, tmp_path, claude, fake, only=['agent-tools', 'agent-tools'])
    assert [inv.name for inv, _, _ in fake.ran] == ['probe-with-bash', 'probe-without-bash']
    assert run(repo, tmp_path, claude, FakeRuns({}), only=None) == (0, ['probes: none due'])
    with pytest.raises(state.SetupError) as err:
        run(repo, tmp_path, claude, FakeRuns({}), only=['agent-tool'])
    assert str(err.value) == '--only agent-tool: not a registered probe'


def test_a_registered_probe_with_no_runner_or_an_unusable_binary_is_a_setup_error(repo, tmp_path, claude):
    with pytest.raises(state.SetupError) as err:
        run(repo, tmp_path, tmp_path / 'missing', FakeRuns({}), force=True)
    assert str(err.value) == f"--claude {tmp_path / 'missing'}: not an executable file"
    write_tree(repo, {state.MANIFEST: MANIFEST_TOML + REGISTRY.replace('stop-continuation', 'skill-pins')})
    with pytest.raises(state.SetupError) as err:
        run(repo, tmp_path, claude, FakeRuns({}), force=True)
    assert str(err.value) == f'{state.MANIFEST} registers skill-pins, which probes.py does not run'


def test_append_row_keeps_the_table_whole_and_escapes_pipes(tmp_path):
    path = tmp_path / 'PROBES.md'
    legend = '\n'.join(['', 'Outcomes:', '', '| Outcome | Meaning |', '|---|---|', '| ERROR | never fired |', ''])
    path.write_text(probes.LOG_TEXT + legend)
    verdict = probes.Verdict(DIVERGES, 'a | b\nc')
    probes.append_row(path, probes.log_row(TODAY, '2.1.902', Path('/opt/claude'), 'agent-tools', verdict, False))
    lines = path.read_text().split('\n')
    assert lines[lines.index('|---|---|---|---|---|---|---|') + 1] == (
        '| 2026-10-20 | 2.1.902 | /opt/claude | agent-tools | DIVERGES | a \\| b c |  |')
    assert state.parse_probes(path.read_text()) == [state.ProbeRow(TODAY, '2.1.902', 'agent-tools', DIVERGES)]
    path.write_text('# Probe log\n\nNo table.\n')
    with pytest.raises(state.SetupError):
        probes.append_row(path, '| x |')


def test_append_row_replaces_the_log_whole_so_a_stop_never_cuts_it_short(tmp_path, monkeypatch):
    '''A SIGTERM during probes is a SystemExit (term_as_exit): one that lands
    while the log is written must leave the old log whole, not an empty file.'''
    path = tmp_path / 'log' / 'PROBES.md'
    path.parent.mkdir()
    path.write_text(probes.LOG_TEXT)

    def stopped(source, target):
        raise SystemExit(143)
    monkeypatch.setattr(probes.os, 'replace', stopped)
    with pytest.raises(SystemExit):
        probes.append_row(path, probes.log_row(TODAY, '2.1.902', Path('/c'), 'agent-tools', probes.Verdict(PASS, 'ok'),
                                               False))
    assert path.read_text() == probes.LOG_TEXT
    assert sorted(p.name for p in path.parent.iterdir()) == ['PROBES.md']


def test_a_failed_draft_write_leaves_no_draft(tmp_path, monkeypatch):
    path = tmp_path / 'log' / 'PROBES.md'
    path.parent.mkdir()
    path.write_text(probes.LOG_TEXT)
    real_write = Path.write_text

    def half(self, text, **kwargs):
        real_write(self, text[:len(text) // 2], **kwargs)
        raise OSError(28, 'No space left on device')
    monkeypatch.setattr(Path, 'write_text', half)
    with pytest.raises(OSError):
        probes.append_row(path, '| 2026-10-20 | 2.1.902 | /c | agent-tools | PASS | ok |  |')
    monkeypatch.undo()
    assert path.read_text() == probes.LOG_TEXT
    assert sorted(p.name for p in path.parent.iterdir()) == ['PROBES.md']


def test_two_runs_appending_at_once_both_keep_their_rows(tmp_path, monkeypatch):
    '''Two probes runs in one working tree: the read, insert and replace are
    one locked step, so neither run's row is lost.'''
    path = tmp_path / 'log' / 'PROBES.md'
    path.parent.mkdir()
    path.write_text(probes.LOG_TEXT)
    real_replace = os.replace

    def slow_replace(source, target):
        time.sleep(0.3)
        real_replace(source, target)
    monkeypatch.setattr(probes.os, 'replace', slow_replace)
    rows = [f'| 2026-10-20 | 2.1.902 | /c | {pid} | PASS | ok |  |' for pid in ('agent-tools', 'stop-continuation')]
    threads = [threading.Thread(target=probes.append_row, args=(path, row)) for row in rows]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sorted(r.probe for r in state.parse_probes(path.read_text())) == ['agent-tools', 'stop-continuation']


def test_the_log_shows_the_home_directory_as_a_tilde(isolated_home):
    assert probes.shown_path(isolated_home / '.local' / 'bin' / 'claude') == '~/.local/bin/claude'
    assert probes.shown_path(Path('/opt/claude')) == '/opt/claude'


def test_the_binary_cell_hides_the_resolved_home_and_the_login(tmp_path, monkeypatch):
    '''HOME may be a symlink, and a binary found through PATH is often given by its resolved path.'''
    real = tmp_path / 'real-home'
    (real / 'zzlogin' / 'bin').mkdir(parents=True)
    link = tmp_path / 'home-link'
    link.symlink_to(real)
    monkeypatch.setenv('HOME', str(link))
    monkeypatch.setattr('getpass.getuser', lambda: 'zzlogin')
    binary = real / 'zzlogin' / 'bin' / 'claude'
    row = probes.log_row(TODAY, '2.1.902', binary, 'agent-tools', probes.Verdict(PASS, 'ok'), False)
    shown = row.split(' | ')[2]
    assert shown.startswith('~')
    assert str(real) not in row and 'zzlogin' not in row
    assert shown == '~/<private>/bin/claude'
    assert probes.shown_path(real) == '~'


def test_run_prints_the_scrubbed_finding(repo, tmp_path, claude, isolated_home, monkeypatch):
    '''The terminal gets the finding the log gets: a transcript of a run can be pasted anywhere.'''
    finding = f'OSError: {Path.home()}/x refused mcp__srv__tool'
    monkeypatch.setattr(probes, 'run_probe', lambda *args: probes.Verdict(ERROR, finding))
    code, lines = run(repo, tmp_path, claude, FakeRuns({}), only=['agent-tools'])
    assert code == 1
    (printed,) = [line for line in lines if line.startswith('agent-tools: ')]
    assert printed == 'agent-tools: ERROR: OSError: <private>/x refused <mcp-tool>'
    assert str(Path.home()) not in printed
    assert probes.public_finding(probes.Verdict(ERROR, finding)) == 'OSError: <private>/x refused <mcp-tool>'


@pytest.fixture
def planted_privates(isolated_home, monkeypatch) -> list[str]:
    '''The five strings a committed probe file must not show (owner, plan 58 decision D3), the login name set
    to a value no path or word in a test holds.'''
    monkeypatch.setattr('getpass.getuser', lambda: 'zzlogin')
    return [str(Path.home()), str(Path.home().resolve()), tempfile.gettempdir(),
            os.path.realpath(tempfile.gettempdir()), 'zzlogin']


def test_the_log_row_holds_no_private_text_and_no_mcp_tool_name(isolated_home, planted_privates):
    '''A finding built from an OSError, a scratch path or a tool name reaches a public repo through PROBES.md.'''
    planted = planted_privates
    finding = f"OSError: {' '.join(planted)} refused 'mcp__srv__tool' for mcp__plug__other"
    verdict = probes.Verdict(ERROR, finding)
    row = probes.log_row(TODAY, '2.1.902', isolated_home / 'bin' / 'claude', 'agent-tools', verdict, True)
    for value in planted:
        assert value not in row
    assert 'mcp__' not in row
    assert row == ('| 2026-10-20 | 2.1.902 | ~/bin/claude | agent-tools | ERROR | OSError: '
                   f"{' '.join(['<private>'] * len(planted))} refused '<mcp-tool>' for <mcp-tool> | --allow-old |")
    # A private string inside an MCP name must not cut the MCP pass short at the > of <private>, which would leave
    # the rest of the server or plugin name in the row.
    nested = probes.Verdict(ERROR, 'refused mcp__plugin_zzlogin-tools__t for the call')
    row = probes.log_row(TODAY, '2.1.902', isolated_home / 'bin' / 'claude', 'agent-tools', nested, False)
    assert 'zzlogin' not in row and '-tools__t' not in row
    assert row == '| 2026-10-20 | 2.1.902 | ~/bin/claude | agent-tools | ERROR | refused <mcp-tool> for the call |  |'


@pytest.mark.parametrize('failure', [OSError('no login'), KeyError('getpwuid(): uid not found')])
def test_a_missing_login_name_does_not_lose_the_log_row(isolated_home, monkeypatch, failure):
    '''getpass.getuser raises when a machine has no login name: OSError on Python 3.13, KeyError before. The row is
    written after a probe has spent tokens, so it must survive, with the other private strings still scrubbed.'''
    def no_login():
        raise failure
    monkeypatch.setattr('getpass.getuser', no_login)
    assert probes.private_strings()[-1] == ''
    verdict = probes.Verdict(ERROR, f'OSError: {Path.home()}/x')
    row = probes.log_row(TODAY, '2.1.902', isolated_home / 'bin' / 'claude', 'agent-tools', verdict, False)
    assert row == '| 2026-10-20 | 2.1.902 | ~/bin/claude | agent-tools | ERROR | OSError: <private>/x |  |'


def executable(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(0o755)
    return path


def test_binary_version_reads_the_label_or_refuses(tmp_path):
    good = executable(tmp_path / 'good', "#!/bin/sh\necho '2.1.303 (Claude Code)'\n")
    assert probes.binary_version(good) == '2.1.303'
    bad = executable(tmp_path / 'bad', '#!/bin/sh\necho hello\n')
    with pytest.raises(state.SetupError) as err:
        probes.binary_version(bad)
    assert str(err.value) == f'{bad} --version printed no Claude Code version'


def test_binaries_lists_each_path_claude_then_the_desktop_bundles(tmp_path, isolated_home):
    target = executable(tmp_path / 'versions' / '2.1.303', '#!/bin/sh\n')
    first = tmp_path / 'bin1'
    first.mkdir()
    (first / 'claude').symlink_to(target)
    second = executable(tmp_path / 'bin2' / 'claude', '#!/bin/sh\n')
    bundle = executable(isolated_home / probes.DESKTOP_BUNDLES / '2.1.304' / 'abc' / 'claude.app' / 'Contents'
                        / 'MacOS' / 'claude', '#!/bin/sh\n')
    versions = {first / 'claude': '2.1.303', bundle: '2.1.304'}

    def version_of(path):
        if path not in versions:
            raise state.SetupError('no version')
        return versions[path]
    found = probes.binaries(os.pathsep.join([str(first), '', str(tmp_path / 'none'), str(first), str(second.parent)]),
                            isolated_home, version_of)
    assert [(c.path, c.version, c.where) for c in found] == [
        (first / 'claude', '2.1.303', 'PATH'), (second, None, 'PATH'), (bundle, '2.1.304', probes.DESKTOP_NOTE)]
    assert probes.describe(found[0]) == f"2.1.303  {first / 'claude'} -> {target.resolve()}  (PATH)"
    assert probes.describe(found[1]) == f'version unknown  {second}  (PATH)'


FAKE_GUARD_CLAUDE = r'''#!/usr/bin/env bash
if [ "$1" = --version ]; then echo '2.1.902 (Claude Code)'; exit 0; fi
echo "argv: ${*:2}" >&2
case "$1" in
  *'git status'*) cmd='git status --porcelain'; out='(Bash completed with no output)'; err=false ;;
  *'git fetch'*) cmd='git fetch --dry-run origin'; out='readonly-agent-guard: denied'; err=true ;;
  *) cmd='git config --global --list'; out=@THIRD@; err=true ;;
esac
use='{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"%s"}}'
res='{"type":"tool_result","tool_use_id":"t1","is_error":%s,"content":"%s"}'
echo '{"type":"system","subtype":"init","tools":["Read","Bash"]}'
printf '{"type":"assistant","parent_tool_use_id":null,"message":{"model":"m","content":['"$use"']}}\n' "$cmd"
printf '{"type":"user","parent_tool_use_id":null,"message":{"content":['"$res"']}}\n' "$err" "$out"
echo '{"type":"result","subtype":"success","is_error":false}'
'''


@pytest.mark.parametrize('third, verdict', [
    ("'readonly-agent-guard: denied'", (PASS, 'git status passed; git fetch and git config --global were denied')),
    ("'user.name=x'", (DIVERGES, 'git config --global --list was not denied')),
])
def test_the_guard_probe_runs_the_real_script_and_reads_its_three_kept_streams(tmp_path, third, verdict):
    fake = executable(tmp_path / 'fake-claude', FAKE_GUARD_CLAUDE.replace('@THIRD@', third))
    run_dir = tmp_path / 'run'
    assert probes.run_probe('guard-liveness', str(fake), REPO, run_dir) == verdict
    assert sorted(p.name for p in run_dir.iterdir()) == [
        'guard-1.jsonl', 'guard-2.jsonl', 'guard-3.jsonl', 'guard.argv.json', 'guard.err', 'guard.txt']
    assert 'Claude Code: 2.1.902 (Claude Code)' in (run_dir / 'guard.txt').read_text()
    # The script merges stderr into each kept stream, where the fake printed its flags (R10.4).
    flags = (run_dir / 'guard-1.jsonl').read_text().split('\n')[0]
    for flag in ('--setting-sources user', '--max-turns 4', '--max-budget-usd 0.50', '--no-session-persistence',
                 '--agent Explore'):
        assert flag in flags


@pytest.mark.parametrize('calls, codes, log', [
    (['{"stop_hook_active": false}', '{"stop_hook_active":true}', '{"stop_hook_active": true}'], [2, 2, 0],
     'false\ntrue\ntrue\n'),
    (['{}'], [2], 'missing\n'),
])
def test_the_stop_hook_logs_the_flag_and_blocks_its_first_two_calls(tmp_path, calls, codes, log):
    (inv,) = probes.prepare_stop(tmp_path, 'claude', REPO)
    settings = json.loads((tmp_path / '.claude' / 'settings.json').read_text())
    hook = settings['hooks']['Stop'][0]['hooks'][0]['command']
    assert '--include-hook-events' in inv.argv and inv.argv[inv.argv.index('--setting-sources') + 1] == 'project'
    got = [subprocess.run([hook], input=c, text=True, capture_output=True).returncode for c in calls]
    assert (got, (tmp_path / 'stop.log').read_text()) == (codes, log)


def transcript(home, session, agent_id, agent_type, *lines):
    folder = home / '.claude' / 'projects' / '-private-tmp-x' / session / 'subagents'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f'agent-{agent_id}.meta.json').write_text(json.dumps({'agentType': agent_type}))
    (folder / f'agent-{agent_id}.jsonl').write_text(''.join(
        json.dumps({'type': kind, 'message': {'model': model}, 'effort': effort}) + '\n'
        for kind, model, effort in lines))


def test_read_transcripts_maps_each_agent_type_to_its_assistant_lines(isolated_home):
    transcript(isolated_home, 's-1', 'a1', 'Explore', ('user', None, None), ('assistant', 'claude-haiku-5-5', 'low'))
    transcript(isolated_home, 's-2', 'a2', 'Explore', ('assistant', 'claude-opus-5-5', 'high'))
    projects = isolated_home / '.claude' / 'projects'
    assert probes.read_transcripts(projects, 's-1') == {'Explore': [{'model': 'claude-haiku-5-5', 'effort': 'low'}]}
    assert probes.read_transcripts(projects, None) == {}


def pins_stream() -> str:
    '''A parent that dispatches the three pinned agents, each forwarding one message.'''
    sent = [{'type': 'assistant', 'parent_tool_use_id': None, 'message': {'model': 'claude-sonnet-5-5', 'content': [
        {'type': 'tool_use', 'id': f't{n}', 'name': 'Agent', 'input': {'subagent_type': agent}}]}}
        for n, agent in enumerate(('Explore', 'test-runner', 'code-reviewer'))]
    forwarded = [{'type': 'assistant', 'parent_tool_use_id': f't{n}', 'message': {'model': model, 'content': []}}
                 for n, model in enumerate(('claude-haiku-5-5', 'claude-haiku-5-5', 'claude-opus-5-5'))]
    return stream(init(), *sent, *forwarded, RESULT)


def leave_transcripts(home, reviewer_effort='xhigh'):
    '''A side effect that writes the session's three subagent transcripts.'''
    def side(cwd):
        for agent, model, effort in (('Explore', 'claude-haiku-5-5', 'low'), ('test-runner', 'claude-haiku-5-5', 'low'),
                                     ('code-reviewer', 'claude-opus-5-5', reviewer_effort)):
            transcript(home, 's-1', agent, agent, ('assistant', model, effort))
    return side


def test_the_pins_probe_persists_its_session_and_reads_effort_from_the_transcripts(tmp_path, isolated_home):
    fake = FakeRuns({'pins': pins_stream()}, side={'pins': leave_transcripts(isolated_home)})
    run_dir = tmp_path / 'run'
    verdict = probes.run_probe('agent-model-pins', 'claude', REPO, run_dir, fake)
    assert verdict == (PASS, 'Explore and test-runner served claude-haiku-5-5; code-reviewer effort xhigh')
    ((inv, cwd, files),) = fake.ran
    assert files == ['a.py'] and '--no-session-persistence' not in inv.argv and '--forward-subagent-text' in inv.argv
    assert inv.env == {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': '900000'} and inv.timeout == 1200
    assert inv.argv[inv.argv.index('--setting-sources') + 1] == 'user'
    assert json.loads(inv.argv[inv.argv.index('--settings') + 1]) == {'permissions': {'defaultMode': 'auto',
                                                                                      'allow': ['Agent']}}
    assert str(cwd) in inv.argv[1]
    assert json.loads((run_dir / 'transcripts.json').read_text())['code-reviewer'] == [
        {'model': 'claude-opus-5-5', 'effort': 'xhigh'}]


def test_output_of_another_shape_is_an_error_never_a_crash(tmp_path, isolated_home):
    '''An effort recorded as an object, as hooks receive it, makes the
    assessment raise TypeError: the row is ERROR, and the run goes on. Python
    3.15 words the error as "cannot use 'dict' as a set element (unhashable
    type: 'dict')", so only the part both wordings share is pinned.'''
    fake = FakeRuns({'pins': pins_stream()}, side={'pins': leave_transcripts(isolated_home, {'level': 'xhigh'})})
    outcome, finding = probes.run_probe('agent-model-pins', 'claude', REPO, tmp_path / 'run', fake)
    assert outcome == ERROR
    assert finding.startswith('TypeError: ') and "unhashable type: 'dict'" in finding


def dispatch_payload(agent, model=None):
    '''An agent dispatch's PreToolUse payload, shaped like plan 63's recordings (Claude Code 2.1.304).'''
    tool_input = {'description': 'd', 'prompt': 'Reply with the word OK.', 'subagent_type': agent,
                  **({'model': model} if model else {})}
    return {'session_id': '364e6342-a957-4e26-a308-caa9e4b4bc69', 'cwd': '/private/tmp/cc-guide-probe-x',
            'hook_event_name': 'PreToolUse', 'tool_name': 'Agent', 'tool_input': tool_input,
            'tool_use_id': 'toolu_01AbC'}


# The control, the pinned built-in, a dispatch made inside a subagent, and a call to another tool.
PAYLOADS = [dispatch_payload('general-purpose', 'haiku'), dispatch_payload('claude-code-guide'),
            {**dispatch_payload('general-purpose'), 'agent_id': 'a5287d9d575e'},
            {**dispatch_payload('x'), 'tool_name': 'Read', 'tool_input': {'file_path': '/private/tmp/x/a.py'}}]
TRIMMED = [{'matcher': matcher, 'tool_name': 'Agent', 'subagent_type': agent, 'model': model, 'input_keys': keys}
           for matcher in ('*', 'Agent')
           for agent, model, keys in (('claude-code-guide', None, ['description', 'prompt', 'subagent_type']),
                                      ('general-purpose', 'haiku', ['description', 'model', 'prompt',
                                                                    'subagent_type']))]


def fire_payload_hooks(*payloads):
    '''A side effect that runs each PreToolUse hook in the scratch project
    settings on each payload whose tool its matcher matches, as Claude Code
    would.'''
    def side(cwd):
        settings = json.loads((cwd / '.claude' / 'settings.json').read_text())
        for group in settings['hooks']['PreToolUse']:
            for payload in payloads:
                if group['matcher'] in ('*', payload['tool_name']):
                    subprocess.run(shlex.split(group['hooks'][0]['command']), input=json.dumps(payload), text=True,
                                   check=True)
    return side


def payload_stream(control_model: str | None = 'haiku') -> str:
    '''A parent on Sonnet that dispatches the control, with control_model,
    and claude-code-guide in one message, each forwarding one Haiku
    message.'''
    control = {'model': control_model} if control_model else {}
    sent = [{'type': 'tool_use', 'id': f't{n}', 'name': 'Agent', 'input': {'subagent_type': agent, **given}}
            for n, (agent, given) in enumerate((('general-purpose', control), ('claude-code-guide', {})))]
    parent = {'type': 'assistant', 'parent_tool_use_id': None,
              'message': {'model': 'claude-sonnet-5-5', 'content': sent}}
    forwarded = [{'type': 'assistant', 'parent_tool_use_id': f't{n}',
                  'message': {'model': 'claude-haiku-5-5', 'content': []}} for n in range(len(sent))]
    return stream({**init(), 'model': 'claude-sonnet-5-5'}, parent, *forwarded, RESULT)


def test_the_payload_probe_logs_each_dispatch_through_both_matchers(tmp_path):
    '''Project settings only, two logging hooks, one file a payload, since
    the hooks and the two dispatches can run at once; collect keeps each
    hook's raw log beside payloads.json, which counts each log's payloads
    before trimming, and rebuild_payloads writes it again from the raw logs
    alone.'''
    (inv,) = probes.prepare_payload(tmp_path, 'claude', REPO)
    settings = json.loads((tmp_path / '.claude' / 'settings.json').read_text())
    assert [g['matcher'] for g in settings['hooks']['PreToolUse']] == ['*', 'Agent']
    assert inv.name == 'dispatch' and inv.timeout == probes.PROBE_TIMEOUT
    assert inv.env == {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': '300000'}
    assert probes.PAYLOAD_CEILING_MS < probes.PROBE_TIMEOUT * 1000  # claude ends its own wait first
    assert inv.argv[inv.argv.index('--setting-sources') + 1] == 'project'
    assert json.loads(inv.argv[inv.argv.index('--settings') + 1]) == {'permissions': {'defaultMode': 'default',
                                                                                      'allow': ['Agent']}}
    assert '--forward-subagent-text' in inv.argv and inv.argv[-1] == '--no-session-persistence'
    for agent in ('"general-purpose" with model "haiku"', '"claude-code-guide", passing no model'):
        assert agent in inv.argv[1]
    fire_payload_hooks(*PAYLOADS)(tmp_path)
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    probes.collect_payload(tmp_path, run_dir)
    expected = {'logged': {'any': 4, 'agent': 3}, 'payloads': TRIMMED}
    assert json.loads((run_dir / 'payloads.json').read_text()) == expected
    assert len((run_dir / 'payloads-any.raw.jsonl').read_text().splitlines()) == 4
    assert len((run_dir / 'payloads-agent.raw.jsonl').read_text().splitlines()) == 3
    shutil.rmtree(tmp_path / 'payloads')
    (run_dir / 'payloads.json').unlink()
    probes.rebuild_payloads(run_dir)
    assert json.loads((run_dir / 'payloads.json').read_text()) == expected


def bad_payload(folder):
    def write(cwd):
        (cwd / 'payloads' / folder / 'payload.bad').write_text('not json\n', encoding='utf-8')
    return write


def empty_payload(cwd):
    fire_payload_hooks(*PAYLOADS)(cwd)
    (cwd / 'payloads' / 'agent' / 'payload.empty').write_text('', encoding='utf-8')


@pytest.mark.parametrize('side, outcome, finding', [
    (fire_payload_hooks(*PAYLOADS), PASS, 'dispatches reach PreToolUse as Agent, with no model when unset; '
                                          'claude-code-guide served claude-haiku-5-5, as the haiku control was'),
    (bad_payload('any'), ERROR, 'JSONDecodeError: '),
    (bad_payload('agent'), ERROR, 'JSONDecodeError: '),
    # An empty payload is not JSON either, and hooks that never fired leave empty logs, not a broken file.
    (empty_payload, ERROR, 'JSONDecodeError: '),
    (lambda cwd: None, ERROR, 'the PreToolUse hooks logged no subagent dispatch'),
])
def test_the_payload_probe_reads_its_run_like_a_live_one(tmp_path, side, outcome, finding):
    '''From prepare to the verdict through run_probe, with the hooks fired on
    the scratch settings; a payload that is not JSON is an ERROR row.'''
    fake = FakeRuns({'dispatch': payload_stream()}, side={'dispatch': side})
    verdict = probes.run_probe('agent-payload', 'claude', REPO, tmp_path / 'run', fake)
    assert verdict.outcome == outcome and verdict.finding.startswith(finding)


def test_a_live_run_whose_parent_strays_from_its_prompt_is_error(tmp_path):
    '''Payloads that match the prompt cannot hide a parent that strayed
    from it: the stream's own Agent calls decide.'''
    fake = FakeRuns({'dispatch': payload_stream(control_model=None)}, side={'dispatch': fire_payload_hooks(*PAYLOADS)})
    verdict = probes.run_probe('agent-payload', 'claude', REPO, tmp_path / 'run', fake)
    assert verdict == (ERROR, "the parent session sent general-purpose with no model, but its prompt asks for model "
                              "'haiku'")


EXPLORE_PASS = 'Explore override read CLAUDE.md and got no git-status snapshot in 3 of 3 reps; the control got both'
EXPLORE_REPS = [f'explore-{n}' for n in range(1, 4)]


def frontmatter(path: Path) -> dict[str, str]:
    head = path.read_text(encoding='utf-8').split('---\n')[1]
    return dict(line.split(': ', 1) for line in head.splitlines())


def test_the_explore_probe_prepares_two_project_agents_its_canaries_and_three_reps(tmp_path):
    '''Each run draws its own canaries: the CLAUDE.md word and an untracked file in a fresh git repo. Both agents
    are project agents that may not read, search or run anything, and the parent's prompt names neither canary
    nor mark, so an answer can hold them only from the agent's context.'''
    first, second = tmp_path / 'a', tmp_path / 'b'
    first.mkdir()
    second.mkdir()
    invs = probes.prepare_explore(first, 'claude', REPO)
    probes.prepare_explore(second, 'claude', REPO)
    canaries = [json.loads((d / 'canaries.json').read_text(encoding='utf-8')) for d in (first, second)]
    for key in ('claude_md', 'git_status'):
        assert canaries[0][key] != canaries[1][key]
    for drawn in canaries:
        assert re.fullmatch(r'cm-[0-9a-f]{8}', drawn['claude_md'])
        assert re.fullmatch(r'gs-[0-9a-f]{8}', drawn['git_status'])
    word, untracked = canaries[0]['claude_md'], f"{canaries[0]['git_status']}.txt"
    assert (first / 'CLAUDE.md').read_text(encoding='utf-8') == f'The canary word for this project is {word}.\n'
    status = subprocess.run(['git', 'status', '--porcelain'], cwd=first, capture_output=True, text=True, check=True)
    assert f'?? {untracked}' in status.stdout.splitlines()
    for stem, name, mark in (('explore', 'Explore', 'EXPLORE-OVERRIDE'),
                             ('canary-control', 'canary-control', 'CANARY-CONTROL')):
        path = first / '.claude' / 'agents' / f'{stem}.md'
        assert frontmatter(path) == {'name': name, 'description': 'A drift probe agent.',
                                     'disallowedTools': 'Read, Grep, Glob, Bash, Edit, Write'}
        body = path.read_text(encoding='utf-8').split('---\n', 2)[2]
        assert f'1. {mark}\n' in body and 'CLAUDE.md' in body and 'git status' in body and 'NONE' in body
    assert sorted(p.name for p in (first / '.claude' / 'agents').iterdir()) == ['canary-control.md', 'explore.md']
    assert [inv.name for inv in invs] == EXPLORE_REPS
    inv = invs[0]
    assert all(other.argv == inv.argv and other.env == inv.env for other in invs)
    assert (inv.timeout, inv.env) == (probes.PROBE_TIMEOUT, {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': '300000'})
    flags = {flag: inv.argv[inv.argv.index(flag) + 1] for flag in ('--setting-sources', '--settings', '--max-turns',
                                                                   '--max-budget-usd')}
    assert (flags['--setting-sources'], flags['--max-turns'], flags['--max-budget-usd']) == ('project', '6', '0.50')
    assert json.loads(flags['--settings']) == {'permissions': {'defaultMode': 'default', 'allow': ['Agent']}}
    assert '--forward-subagent-text' in inv.argv and inv.argv[-1] == '--no-session-persistence'
    prompt = inv.argv[1]
    for agent in ('Explore', 'canary-control'):
        assert f'subagent_type "{agent}" with prompt "Follow your instructions."' in prompt
    for secret in (*canaries[0].values(), 'EXPLORE-OVERRIDE', 'CANARY-CONTROL', 'cm-', 'gs-'):
        assert secret not in prompt


def test_the_explore_probe_reads_its_run_like_a_live_one(tmp_path, monkeypatch):
    '''From prepare to the verdict through run_probe: three reps from one scratch git repo, each stream built by
    test_probe_checks' explore_run, with the canaries prepare draws fixed to that file's CANARIES.'''
    drawn = []
    monkeypatch.setattr(probes.secrets, 'token_hex', lambda n: drawn.append(n) or '0a1b2c3d')
    fake = FakeRuns({rep: stream(*tpc.explore_run()) for rep in EXPLORE_REPS})
    run_dir = tmp_path / 'run'
    assert probes.run_probe('explore-override', 'claude', REPO, run_dir, fake) == (PASS, EXPLORE_PASS)
    assert drawn == [4, 4]
    assert [inv.name for inv, _, _ in fake.ran] == EXPLORE_REPS
    assert len({cwd for _, cwd, _ in fake.ran}) == 1
    files = [f for f in fake.ran[0][2] if not f.startswith('.git/')]
    assert files == ['.claude', '.claude/agents', '.claude/agents/canary-control.md', '.claude/agents/explore.md',
                     '.git', 'CLAUDE.md', 'canaries.json', 'gs-0a1b2c3d.txt']
    assert json.loads((run_dir / 'canaries.json').read_text(encoding='utf-8')) == tpc.CANARIES
    assert json.loads((run_dir / 'sightings.json').read_text(encoding='utf-8')) == [tpc.sighting()] * 3
    assert sorted(p.name for p in run_dir.iterdir()) == sorted(
        ['canaries.json', 'sightings.json', *(f'{rep}{suffix}' for rep in EXPLORE_REPS
                                              for suffix in ('.argv.json', '.err', '.jsonl'))])


def test_the_explore_probe_backs_its_sections_and_its_fixture_replays_like_the_run(tmp_path, monkeypatch):
    '''The registry entry the owner chose (plan 109, D10), and the one fixture save_fixtures writes, which the
    replay reads as the run was read. A run with no sightings.json is ERROR, never a pass.'''
    manifest = state.parse_manifest((REPO / state.MANIFEST).read_text(encoding='utf-8'))
    assert manifest.probes['explore-override'] == (['subagents.isolation', 'subagents.models'], ['agents/explore.md'])
    monkeypatch.setattr(probes.secrets, 'token_hex', lambda n: '0a1b2c3d')
    unmarked = tpc.explore_run(control=[tpc.text(tpc.answer('canary-control', mark=False))])
    fake = FakeRuns({'explore-1': stream(*tpc.explore_run()), 'explore-2': stream(*tpc.explore_run()),
                     'explore-3': stream(*unmarked)})
    run_dir, dest = tmp_path / 'run', tmp_path / 'fixtures'
    verdict = probes.run_probe('explore-override', 'claude', REPO, run_dir, fake)
    assert verdict == (ERROR, 'rep 3: canary-control did not give its mark CANARY-CONTROL')
    assert probes.save_fixtures(run_dir, 'explore-override', dest) == [dest / 'explore-override.sightings.json']
    probe = probes.PROBE_RUNS['explore-override']
    assert probe.assess(probes.reader(dest, probe.fixtures)) == verdict
    assert probe.assess(lambda name: None) == (ERROR, 'expected 3 reps, found 0')


def test_the_explore_probe_reads_each_rep_from_its_own_stream(tmp_path, monkeypatch):
    '''A rep whose stream diverges is named by its number, and a missing stream is a broken rep, not a pass.'''
    monkeypatch.setattr(probes.secrets, 'token_hex', lambda n: '0a1b2c3d')
    snapshot = tpc.explore_run(explore=[tpc.text(tpc.answer('Explore'))])
    fake = FakeRuns({'explore-1': stream(*tpc.explore_run()), 'explore-2': stream(*snapshot),
                     'explore-3': stream(*tpc.explore_run())})
    assert probes.run_probe('explore-override', 'claude', REPO, tmp_path / 'run', fake) == (
        DIVERGES, 'rep 2: the Explore override got a git-status snapshot')
    fake = FakeRuns({'explore-1': stream(*tpc.explore_run()), 'explore-2': stream(*tpc.explore_run())})
    assert probes.run_probe('explore-override', 'claude', REPO, tmp_path / 'short', fake) == (
        ERROR, 'rep 3: the run broke: no stream-json events')


AT_ONCE = 0.5  # seconds: a trap that waited for the hook's one-second sleep to end would come later


def gone_pid() -> int:
    '''The pid of a process that has exited and been reaped.'''
    proc = subprocess.Popen(['true'])
    proc.wait()
    return proc.pid


def orphan(command: str) -> int:
    '''The pid of a background shell running `command`, whose parent has exited, so init reaps it when it ends,
    as it reaps a hook whose claude has exited.'''
    started = subprocess.run(['sh', '-c', f'({command}) >/dev/null 2>&1 &\necho $!'], capture_output=True, text=True,
                             check=True)
    return int(started.stdout)


def teardown_log(*lines):
    return lambda cwd: (cwd / 'teardown.log').write_text(''.join(f'{line}\n' for line in lines), encoding='utf-8')


def default_signals():
    '''In the hook's process before exec: a signal the suite's process ignores, as nohup ignores SIGHUP, would stay
    ignored in the hook's shell, which then could not trap it.'''
    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, signal.SIG_DFL)


def start_hook(scratch: Path, script: str | None = None) -> tuple[subprocess.Popen, Path]:
    hook = executable(scratch / 'teardown-hook.sh', script or probes.TEARDOWN_HOOK)
    log = scratch / 'teardown.log'
    return subprocess.Popen([str(hook), str(log)], start_new_session=True, preexec_fn=default_signals), log


def log_reads(log: Path, lines: list[str], wait: float) -> bool:
    '''Whether the log holds exactly these lines within `wait` seconds.'''
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        if log.is_file() and log.read_text(encoding='utf-8').splitlines() == lines:
            return True
        time.sleep(0.01)
    return False


def written(path: Path, wait: float = 5) -> bool:
    '''Whether the file holds text within `wait` seconds.'''
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        if path.is_file() and path.read_text(encoding='utf-8').strip():
            return True
        time.sleep(0.01)
    return False


@contextlib.contextmanager
def reaped(proc: subprocess.Popen):
    try:
        yield proc
    finally:
        with contextlib.suppress(ProcessLookupError):
            proc.kill()
        proc.wait()


def test_the_teardown_probe_registers_an_async_session_start_hook(tmp_path):
    '''Project settings only, one async SessionStart command hook on the startup matcher, as .claude/settings.json
    registers notice.sh's refresh, and hook events in the stream.'''
    (inv,) = probes.prepare_teardown(tmp_path, 'claude', REPO)
    hook, log = tmp_path / 'teardown-hook.sh', tmp_path / 'teardown.log'
    settings = json.loads((tmp_path / '.claude' / 'settings.json').read_text(encoding='utf-8'))
    command = f'{shlex.quote(str(hook))} {shlex.quote(str(log))}'
    assert settings == {'hooks': {'SessionStart': [
        {'matcher': 'startup', 'hooks': [{'type': 'command', 'command': command, 'async': True}]}]}}
    assert hook.read_text(encoding='utf-8') == probes.TEARDOWN_HOOK and os.access(hook, os.X_OK)
    assert (inv.name, inv.env, inv.timeout, inv.suffix) == ('teardown', {}, probes.PROBE_TIMEOUT, '.jsonl')
    assert inv.argv == probes.claude_args('claude', 'Reply with the word OK.', turns=1, sources='project',
                                          mode='default', extra=('--include-hook-events',))
    assert probes.TEARDOWN_WAIT == 5


def test_the_teardown_hook_logs_each_signal_at_once_and_keeps_running(tmp_path):
    proc, log = start_hook(tmp_path)
    with reaped(proc):
        expected = [f'start {proc.pid}']
        assert log_reads(log, expected, 5), 'the hook never logged its start line'
        for name in ('TERM', 'HUP', 'INT'):
            os.kill(proc.pid, getattr(signal, f'SIG{name}'))
            expected.append(name)
            assert log_reads(log, expected, AT_ONCE), f'{name} was not logged at once'
            assert proc.poll() is None, f'the hook ended on {name}'


def test_the_teardown_hook_logs_expired_once_its_lifetime_ends(tmp_path):
    '''Nothing the probe starts runs unbounded: with its 120-second bound cut to 2, the hook ends on its own, and
    its last line says so, so the assessment never reads its natural end as claude's teardown.'''
    bound = f'-lt {probes.TEARDOWN_LIFETIME} ]'
    assert probes.TEARDOWN_LIFETIME == 120 and bound in probes.TEARDOWN_HOOK
    proc, log = start_hook(tmp_path, probes.TEARDOWN_HOOK.replace(bound, '-lt 2 ]'))
    with reaped(proc):
        assert proc.wait(timeout=10) == 0
        assert log.read_text(encoding='utf-8').splitlines()[-1] == 'expired'
        assert log.read_text(encoding='utf-8') == f'start {proc.pid}\nexpired\n'


def test_the_teardown_probe_reads_its_run_like_a_live_one(tmp_path):
    '''From prepare to the verdict through run_probe: the hook logged its start and TERM, and its pid is gone.'''
    pid = gone_pid()
    fake = FakeRuns({'teardown': stream(init(), RESULT)}, side={'teardown': teardown_log(f'start {pid}', 'TERM')})
    run_dir = tmp_path / 'run'
    assert probes.run_probe('async-teardown', 'claude', REPO, run_dir, fake) == (PASS, tpc.TEARDOWN_PASS)
    assert fake.ran[0][2] == ['.claude', '.claude/settings.json', 'teardown-hook.sh']
    assert (run_dir / 'teardown.log').read_text(encoding='utf-8') == f'start {pid}\nTERM\ngone\n'
    assert sorted(p.name for p in run_dir.iterdir()) == ['teardown.argv.json', 'teardown.err', 'teardown.jsonl',
                                                         'teardown.log']


def test_the_teardown_run_is_not_swept_so_collect_sees_what_claude_left(tmp_path):
    '''A sweep after claude -p ends would kill a hook claude left behind, and the log would read gone.'''
    (inv,) = probes.prepare_teardown(tmp_path, 'claude', REPO)
    assert inv.sweep is False
    tools = tmp_path / 'tools'
    tools.mkdir()
    assert all(inv.sweep for inv in probes.prepare_agent_tools(tools, 'claude', REPO))


def test_collect_teardown_never_kills_a_pid_that_is_not_its_hook(tmp_path, monkeypatch):
    '''The OS may reuse a hook's pid once the hook is gone: that process is never signalled and never read as the
    hook (Review Focus 5).'''
    real_kill, sent = os.kill, []

    def spy(pid, signum):
        if signum:
            sent.append((pid, signum))
        return real_kill(pid, signum)
    with reaped(subprocess.Popen(['sleep', '60'])) as other:
        (tmp_path / 'teardown.log').write_text(f'start {other.pid}\nTERM\n', encoding='utf-8')
        run_dir = tmp_path / 'run'
        run_dir.mkdir()
        monkeypatch.setattr(probes.os, 'kill', spy)
        probes.collect_teardown(tmp_path, run_dir)
        monkeypatch.undo()
        assert sent == []
        assert (run_dir / 'teardown.log').read_text(encoding='utf-8').splitlines()[-1] == 'gone'
        assert other.poll() is None


def test_is_hook_reads_the_command_line_of_the_pid(tmp_path, monkeypatch):
    proc, log = start_hook(tmp_path)
    with reaped(proc):
        assert written(log)
        assert probes.is_hook(proc.pid, tmp_path / probes.TEARDOWN_SCRIPT)
        assert not probes.is_hook(proc.pid, tmp_path / 'other-hook.sh')
        # Another probe's hook has the same file name in its own scratch directory.
        assert not probes.is_hook(proc.pid, tmp_path / 'other-scratch' / probes.TEARDOWN_SCRIPT)
    assert not probes.is_hook(gone_pid(), tmp_path / probes.TEARDOWN_SCRIPT)

    def no_ps(*args, **kwargs):
        raise OSError('no ps')
    monkeypatch.setattr(probes.subprocess, 'run', no_ps)
    assert not probes.is_hook(os.getpid(), Path(sys.argv[0]))


def test_collect_teardown_waits_for_a_hook_that_goes_late_and_reads_its_log_after(tmp_path):
    '''A hook that logs TERM and ends a second after collect starts reads gone, with that TERM in the log.'''
    log = tmp_path / 'teardown.log'
    body = f"#!/bin/sh\nsleep 1\nprintf 'TERM\\n' >> {shlex.quote(str(log))}\n"
    hook = executable(tmp_path / probes.TEARDOWN_SCRIPT, body)
    pid = orphan(shlex.quote(str(hook)))
    log.write_text(f'start {pid}\n', encoding='utf-8')
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    probes.collect_teardown(tmp_path, run_dir)
    assert (run_dir / 'teardown.log').read_text(encoding='utf-8') == f'start {pid}\nTERM\ngone\n'


def test_collect_teardown_kills_every_hook_still_there_after_the_wait(tmp_path, monkeypatch):
    '''A hook that outlives the wait reads alive and gets SIGKILL, which its traps cannot catch, so it never
    outlives the probe. Each start line counts, not only the first.'''
    monkeypatch.setattr(probes, 'TEARDOWN_WAIT', 0.3)
    proc, log = start_hook(tmp_path)
    with reaped(proc):
        assert written(log)
        lines = f'start {gone_pid()}\nstart {proc.pid}\n'
        log.write_text(lines, encoding='utf-8')
        run_dir = tmp_path / 'run'
        run_dir.mkdir()
        probes.collect_teardown(tmp_path, run_dir)
        assert proc.wait(timeout=5) == -signal.SIGKILL
        assert (run_dir / 'teardown.log').read_text(encoding='utf-8') == f'{lines}alive\n'


def test_collect_teardown_kills_the_hook_when_its_wait_is_cut_short(tmp_path, monkeypatch):
    '''A stop during the wait, which term_as_exit turns into SystemExit, still ends the hook.'''
    proc, log = start_hook(tmp_path)
    with reaped(proc):
        assert written(log)

        def stop(seconds):
            raise SystemExit(143)

        with monkeypatch.context() as patched:
            patched.setattr(probes.time, 'sleep', stop)
            with pytest.raises(SystemExit):
                probes.collect_teardown(tmp_path, tmp_path)
        assert proc.wait(timeout=5) == -signal.SIGKILL


@pytest.mark.parametrize('line', ['start 0', 'start 1', f'start {os.getpid()}'], ids=['pid 0', 'pid 1', 'own pid'])
def test_collect_teardown_never_signals_a_group_init_or_itself(tmp_path, monkeypatch, line):
    '''os.kill on pid 0 signals the probe's own process group; 1 is init. Such a start line is no start.'''
    sent = []
    monkeypatch.setattr(probes.os, 'kill', lambda pid, signum: sent.append((pid, signum)))
    (tmp_path / 'teardown.log').write_text(f'{line}\nTERM\n', encoding='utf-8')
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    probes.collect_teardown(tmp_path, run_dir)
    assert sent == []
    assert (run_dir / 'teardown.log').read_text(encoding='utf-8') == f'{line}\nTERM\n'


def test_collect_teardown_counts_a_pid_it_may_not_signal_as_alive(tmp_path, monkeypatch):
    '''PermissionError means a process holds the pid, though this user may not signal it: the pid is not gone, so
    the hook reads alive, and a SIGKILL refused the same way does not stop collect.'''
    def refuse(pid, signum):
        raise PermissionError(1, 'Operation not permitted')

    monkeypatch.setattr(probes, 'TEARDOWN_WAIT', 0.2)
    monkeypatch.setattr(probes, 'is_hook', lambda pid, hook: True)
    monkeypatch.setattr(probes.os, 'kill', refuse)
    (tmp_path / 'teardown.log').write_text('start 99999\nTERM\n', encoding='utf-8')
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    probes.collect_teardown(tmp_path, run_dir)
    assert (run_dir / 'teardown.log').read_text(encoding='utf-8') == 'start 99999\nTERM\nalive\n'


def test_collect_teardown_copies_a_log_with_no_start_line_and_adds_nothing(tmp_path):
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    probes.collect_teardown(tmp_path, run_dir)
    assert (run_dir / 'teardown.log').read_text(encoding='utf-8') == ''
    (tmp_path / 'teardown.log').write_text('TERM\n', encoding='utf-8')
    probes.collect_teardown(tmp_path, run_dir)
    assert (run_dir / 'teardown.log').read_text(encoding='utf-8') == 'TERM\n'
    (run_dir / 'teardown.jsonl').write_text(stream(init(), RESULT), encoding='utf-8')
    assert probes.assess_teardown(probes.reader(run_dir)) == (ERROR, 'the async SessionStart hook never started')


def test_the_teardown_probe_backs_its_sections_and_its_fixtures_replay_like_the_run(tmp_path):
    '''The registry entry the owner chose (plan 109, D10), and the two fixtures save_fixtures writes, which the
    replay reads as the run was read. A run with neither file is ERROR, never a pass.'''
    manifest = state.parse_manifest((REPO / state.MANIFEST).read_text(encoding='utf-8'))
    assert manifest.probes['async-teardown'] == (['hooks.pitfalls'], ['build/cc_guide/notice.sh'])
    pid = gone_pid()
    fake = FakeRuns({'teardown': stream(init(), RESULT)}, side={'teardown': teardown_log(f'start {pid}', 'HUP')})
    run_dir, dest = tmp_path / 'run', tmp_path / 'fixtures'
    verdict = probes.run_probe('async-teardown', 'claude', REPO, run_dir, fake)
    assert verdict == (DIVERGES, tpc.TEARDOWN_HUP)
    assert probes.save_fixtures(run_dir, 'async-teardown', dest) == [dest / 'async-teardown.jsonl',
                                                                      dest / 'async-teardown.log']
    probe = probes.PROBE_RUNS['async-teardown']
    assert probe.assess(probes.reader(dest, probe.fixtures)) == verdict
    assert probe.assess(lambda name: None) == (ERROR, 'no stream-json events')


def test_register_window_reads_the_compaction_window_check(tmp_path, monkeypatch):
    '''tokens times chars_per_token, less reserve_chars, which a register may leave out (plan 87).'''
    assert probes.register_window() == 19700
    text = probes.CONFORMANCE.read_text(encoding='utf-8')
    copy = tmp_path / 'conformance.toml'
    monkeypatch.setattr(probes, 'CONFORMANCE', copy)
    for edited, window in (('reserve_chars = 150\n', 19850), ('', 20000)):
        changed = text.replace('reserve_chars = 300\n', edited, 1)
        assert changed != text
        copy.write_text(changed, encoding='utf-8')
        assert probes.register_window() == window


def test_the_cut_probe_prepares_one_invocation_that_drives_the_session(tmp_path):
    '''One claude process takes the three messages on stdin, since a /compact in a resumed process re-attaches
    nothing (plan 87's spike). The session is persisted under an id chosen here, since collect reads its
    transcript.'''
    (inv,) = probes.prepare_cut(tmp_path, '/bin/claude', REPO)
    assert (inv.name, inv.env, inv.timeout) == ('cut', {}, probes.PROBE_TIMEOUT)
    assert inv.argv[:3] == [sys.executable, str(PROBES_PY), 'drive-cut'] and len(inv.argv) == 4
    argv = json.loads(inv.argv[3])
    assert argv[:2] == ['/bin/claude', '-p'] and probes.CUT_PROMPT not in argv
    session = (tmp_path / 'session-id').read_text(encoding='utf-8').strip()
    assert probe_checks.UUID_RE.fullmatch(session)
    after = {flag: argv[argv.index(flag) + 1] for flag in ('--input-format', '--session-id', '--max-budget-usd',
                                                           '--setting-sources', '--settings')}
    assert after['--input-format'] == 'stream-json' and after['--session-id'] == session
    assert after['--max-budget-usd'] == '0.75' and after['--setting-sources'] == 'project'
    assert json.loads(after['--settings']) == {'permissions': {'defaultMode': 'default', 'allow': ['Skill']}}
    assert '--resume' not in argv and '--no-session-persistence' not in argv
    for kind in probe_checks.CUT_KINDS:
        skill = tmp_path / '.claude' / 'skills' / f'cut-probe-{kind}' / 'SKILL.md'
        assert skill.read_text(encoding='utf-8') == probe_checks.cut_frontmatter(kind) + probe_checks.cut_body(kind)


# A stand-in for claude -p --input-format stream-json. It reads stdin a byte at a time, so a line the driver sent
# early stays in the pipe, where select sees it. Its mode: pace prints an init event as soon as it reads a line,
# then waits 0.3 s, reports a line that came early and prints the result, so a driver that sends on any stdout line,
# not only on a result, is caught; error answers every line with an error result; exit leaves with code 3 after its
# first line. At the end of its stdin it reports how many lines it read.
FAKE_STREAM_CLAUDE = r'''import json, os, select, sys, time


def line():
    data = b''
    while not data.endswith(b'\n'):
        byte = os.read(0, 1)
        if not byte:
            return None
        data += byte
    return data


mode, count = sys.argv[1], 0
while (got := line()) is not None:
    count += 1
    if mode == 'exit':
        sys.exit(3)
    if mode == 'pace':
        print(json.dumps({'type': 'system', 'subtype': 'init'}), flush=True)
        time.sleep(0.3)
        if select.select([0], [], [], 0)[0]:
            print(json.dumps({'type': 'early'}), flush=True)
    print(json.dumps({'type': 'result', 'is_error': mode == 'error', 'echo': json.loads(got)}), flush=True)
print(json.dumps({'type': 'closed', 'lines': count}), flush=True)
'''


def fake_stream_claude(tmp_path) -> Path:
    path = tmp_path / 'fake_claude.py'
    path.write_text(FAKE_STREAM_CLAUDE, encoding='utf-8')
    return path


def drive(fake: Path, mode: str) -> subprocess.CompletedProcess:
    '''The drive-cut entry point, run as prepare_cut's invocation runs it, on the fake in the given mode.'''
    return subprocess.run([sys.executable, str(PROBES_PY), 'drive-cut', json.dumps([sys.executable, str(fake), mode])],
                          stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20)


def events_of(text: str) -> list[dict]:
    return [json.loads(line) for line in text.splitlines()]


def user_line(text: str) -> dict:
    return {'type': 'user', 'message': {'role': 'user', 'content': text}}


def test_drive_cut_sends_each_message_after_the_previous_result(tmp_path):
    fake = fake_stream_claude(tmp_path)
    # The control: the fake reports a line that arrives before its result.
    control = subprocess.run([sys.executable, str(fake), 'pace'], input=''.join(
        json.dumps(user_line(m)) + '\n' for m in probes.CUT_MESSAGES), capture_output=True, text=True, timeout=20)
    assert {'type': 'early'} in events_of(control.stdout)
    proc = drive(fake, 'pace')
    assert (proc.returncode, proc.stderr) == (0, '')
    assert events_of(proc.stdout) == [
        *(event for m in probes.CUT_MESSAGES
          for event in ({'type': 'system', 'subtype': 'init'}, {'type': 'result', 'is_error': False,
                                                                 'echo': user_line(m)})),
        {'type': 'closed', 'lines': 3}]


def test_drive_cut_stops_on_an_error_result_and_on_a_closed_stdout(tmp_path):
    fake = fake_stream_claude(tmp_path)
    proc = drive(fake, 'error')
    assert (proc.returncode, proc.stderr) == (0, '')
    assert events_of(proc.stdout) == [{'type': 'result', 'is_error': True, 'echo': user_line(probes.CUT_PROMPT)},
                                      {'type': 'closed', 'lines': 1}]
    proc = drive(fake, 'exit')
    assert (proc.returncode, proc.stdout, proc.stderr) == (3, '', '')


# The real marker after a re-attached copy's kept text (plan 87's spike, S2).
CUT_MARKER = '\n\n\n[... skill content truncated for compaction; use Read on the skill path if you need the full text]'
CUT_KEPT = 19775


def cut_copy(kind: str) -> str:
    header = f'Base directory for this skill: /x/cut-probe-{kind}\n\n'
    return header + probe_checks.cut_body(kind)[:CUT_KEPT] + CUT_MARKER


def cut_stream() -> str:
    '''The three turns of a live compaction-cut run, in the event order Claude Code 2.1.317 wrote (plan 87's spike).'''
    said = {'type': 'assistant', 'parent_tool_use_id': None, 'message': {'model': 'claude-sonnet-5-5', 'content': []}}
    heard = {'type': 'user', 'parent_tool_use_id': None, 'message': {'content': []}}
    summary = {'type': 'system', 'subtype': 'post_turn_summary'}
    status = [{'type': 'system', 'subtype': 'status', 'status': 'compacting'}, {'type': 'system', 'subtype': 'status'}]
    return stream(init(), said, {'type': 'rate_limit_event'}, heard, heard, said, heard, heard, said, summary, RESULT,
                  *status, init(), {'type': 'system', 'subtype': 'compact_boundary'}, heard, heard, RESULT,
                  init(), said, summary, RESULT)


def leave_cut_transcript(home):
    '''A side effect that writes the session's transcript: a boundary, then the invoked_skills attachment with
    both cut copies.'''
    def side(cwd):
        session = (cwd / 'session-id').read_text(encoding='utf-8').strip()
        folder = home / '.claude' / 'projects' / '-x'
        folder.mkdir(parents=True, exist_ok=True)
        attachment = {'type': 'invoked_skills', 'skills': [
            {'name': f'cut-probe-{kind}', 'path': f'projectSettings:cut-probe-{kind}', 'content': cut_copy(kind)}
            for kind in probe_checks.CUT_KINDS]}
        entries = [{'type': 'system', 'subtype': 'compact_boundary'}, {'type': 'attachment', 'attachment': attachment}]
        (folder / f'{session}.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in entries), encoding='utf-8')
    return side


def test_the_cut_probe_reads_its_run_like_a_live_one(tmp_path, isolated_home):
    '''From prepare to the verdict through run_probe. A transcript that is absent leaves cut.json empty: ERROR.'''
    events = probe_checks.parse_stream(cut_stream())
    assert probe_checks.broken(events) is None
    measures = {kind: probe_checks.measure_cut(cut_copy(kind), probe_checks.cut_body(kind))
                for kind in probe_checks.CUT_KINDS}
    run_dir = tmp_path / 'run'
    fake = FakeRuns({'cut': cut_stream()}, side={'cut': leave_cut_transcript(isolated_home)})
    verdict = probes.run_probe('compaction-cut', 'claude', REPO, run_dir, fake)
    assert verdict == probe_checks.assess_compaction_cut(events, measures, probes.register_window())
    assert verdict == (PASS, f'compaction kept {CUT_KEPT} body characters of the prose probe skill (by '
                             'characters; 51 characters before the body), at least the register window '
                             f'{probes.register_window()}')
    assert sorted(p.name for p in run_dir.iterdir()) == ['cut.argv.json', 'cut.err', 'cut.json', 'cut.jsonl',
                                                         'transcript.raw.jsonl']
    assert json.loads((run_dir / 'cut.json').read_text(encoding='utf-8')) == measures
    absent = probes.run_probe('compaction-cut', 'claude', REPO, tmp_path / 'absent', FakeRuns({'cut': cut_stream()}))
    assert absent == (ERROR, 'no re-attached copy of cut-probe-prose after the compact boundary')
    assert json.loads((tmp_path / 'absent' / 'cut.json').read_text(encoding='utf-8')) == {}


def test_a_setup_failure_is_an_error_never_a_pass(tmp_path, monkeypatch):
    def broken(scratch, claude, repo):
        raise OSError('disk full')
    monkeypatch.setitem(probes.PROBE_RUNS, 'agent-tools', probes.PROBE_RUNS['agent-tools']._replace(prepare=broken))
    assert probes.run_probe('agent-tools', 'claude', REPO, tmp_path / 'run', FakeRuns({})) == (
        ERROR, 'OSError: disk full')


def test_a_run_dir_that_cannot_be_made_is_an_error_row(tmp_path):
    '''(i): run_probe returns ERROR, never a traceback, so the row is still written.'''
    parent = tmp_path / 'a-file'
    parent.write_text('', encoding='utf-8')
    verdict = probes.run_probe('agent-tools', 'claude', REPO, parent / 'run', FakeRuns(TOOLS_PASS))
    assert verdict.outcome == ERROR
    name = verdict.finding.partition(':')[0]
    assert issubclass(getattr(builtins, name), OSError), verdict.finding


def test_a_scratch_folder_that_cannot_be_made_is_an_error_row(tmp_path, monkeypatch):
    monkeypatch.setattr(tempfile, 'tempdir', str(tmp_path / 'missing'))
    verdict = probes.run_probe('agent-tools', 'claude', REPO, tmp_path / 'run', FakeRuns(TOOLS_PASS))
    assert verdict.outcome == ERROR and verdict.finding.startswith('FileNotFoundError: ')


def scratch_folders(tmp: Path) -> list[Path]:
    return sorted(tmp.glob('cc-guide-probe-*'))


def test_a_scratch_folder_inside_a_work_tree_is_an_error_and_is_removed(tmp_path, monkeypatch):
    work = (tmp_path / 'work').resolve()
    (work / 'tmp').mkdir(parents=True)
    subprocess.run(['git', 'init', '-q'], cwd=work, check=True, capture_output=True)
    monkeypatch.setattr(tempfile, 'tempdir', str(work / 'tmp'))
    fake = FakeRuns(TOOLS_PASS)
    verdict = probes.run_probe('agent-tools', 'claude', REPO, tmp_path / 'run', fake)
    assert verdict.outcome == ERROR and 'inside a git work tree' in verdict.finding
    assert f'{work}{os.sep}' in verdict.finding
    assert fake.ran == []
    assert scratch_folders(work / 'tmp') == []


def test_scratch_is_removed_after_an_error_and_after_a_timeout(tmp_path, monkeypatch):
    tmp = tmp_path / 'tmp'
    tmp.mkdir()
    monkeypatch.setattr(tempfile, 'tempdir', str(tmp))

    def broken(inv, cwd, out, err):
        raise OSError('no claude')
    timeout = probes.run_probe('agent-tools', 'claude', REPO, tmp_path / 'r1', lambda inv, cwd, out, err: None)
    assert timeout.outcome == ERROR and 'timed out' in timeout.finding
    assert scratch_folders(tmp) == []
    assert probes.run_probe('agent-tools', 'claude', REPO, tmp_path / 'r2', broken) == (ERROR, 'OSError: no claude')
    assert scratch_folders(tmp) == []


def test_save_fixtures_scrubs_a_recorded_run_and_the_replay_reads_it_like_the_run(tmp_path, isolated_home,
                                                                                   planted_privates):
    # The trim drops an init event's cwd and memory_paths, so those prove nothing. The private strings go where the
    # trim keeps them, a Bash command, and each must come out as <private> on its own: a path that another entry
    # covers by its prefix, as the temporary directory covers a home inside it, must not hide an uncovered one.
    planted = planted_privates
    ran = {'type': 'assistant', 'parent_tool_use_id': None, 'message': {'model': 'm', 'content': [
        {'type': 'tool_use', 'id': 't1', 'name': 'Bash', 'input': {'command': 'ls ' + ' '.join(planted)}}]}}
    run_dir, dest = tmp_path / 'run', tmp_path / 'fixtures'
    with_bash = stream({**init(), 'cwd': str(isolated_home / 'work'), 'memory_paths': [str(isolated_home)]}, ran,
                       RESULT)
    write_tree(run_dir, {'probe-with-bash.jsonl': with_bash,
                         'probe-without-bash.jsonl': TOOLS_PASS['probe-without-bash']})
    probe = probes.PROBE_RUNS['agent-tools']
    written = probes.save_fixtures(run_dir, 'agent-tools', dest)
    assert sorted(p.name for p in written) == ['agent-tools.with-bash.jsonl', 'agent-tools.without-bash.jsonl']
    scrubbed = (dest / 'agent-tools.with-bash.jsonl').read_text()
    assert str(isolated_home) not in scrubbed
    for value in planted:
        assert value not in scrubbed
    assert '<private>' in scrubbed
    assert f'"command": "ls {" ".join(["<private>"] * len(planted))}"' in scrubbed
    assert probe.assess(probes.reader(dest, probe.fixtures)) == probe.assess(probes.reader(run_dir))
    write_tree(run_dir, {'probe-with-bash.jsonl': 'not a stream\n{"broken": \n'})
    with pytest.raises(state.SetupError):
        probes.save_fixtures(run_dir, 'agent-tools', dest)


@pytest.mark.parametrize('pid, stream_name, side_name, template, fixture', [
    ('agent-model-pins', 'pins.jsonl', 'transcripts.json', '{"Explore": [{"model": "@P@", "effort": "low"}]}',
     'agent-model-pins.transcripts.json'),
    ('stop-continuation', 'stop.jsonl', 'stop.log', 'false\n@P@\ntrue\n', 'stop-continuation.log'),
])
def test_save_fixtures_scrubs_a_side_file_as_well_as_a_stream(tmp_path, isolated_home, planted_privates, pid,
                                                              stream_name, side_name, template, fixture):
    '''A transcripts.json or a stop.log is copied whole, so it needs the same scrub as a stream.'''
    planted = planted_privates
    run_dir, dest = tmp_path / 'run', tmp_path / 'fixtures'
    write_tree(run_dir, {stream_name: stream(init(), RESULT), side_name: template.replace('@P@', ' '.join(planted))})
    probes.save_fixtures(run_dir, pid, dest)
    saved = (dest / fixture).read_text()
    for value in planted:
        assert value not in saved
    assert saved == template.replace('@P@', ' '.join(['<private>'] * len(planted)))
