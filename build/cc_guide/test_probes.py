'''Tests for probes.py: R10.4's command lines and isolation, the run
directory and the PROBES.md row each probe leaves (R10.6), the version
refusal (R10.3), which probes run, and binaries. Every claude here is a
fake, so no test spends a token or reads the real ~/.claude.'''
import contextlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import probes
import state
from cc_fixtures import MANIFEST_TOML, isolated_home, write_tree  # noqa: F401
from state import DIVERGES, ERROR, PASS

REPO = Path(__file__).resolve().parents[2]
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


def run(repo, tmp_path, claude, fake, *, only=None, force=False, allow_old=False, version='2.1.902'):
    return probes.run(repo, tmp_path / 'cache', claude, only=only, force=force, allow_old=allow_old,
                      newest='2.1.902', today=TODAY, now=NOW, execute=fake, version_of=lambda path: version)


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


def planted_privates(monkeypatch) -> list[str]:
    '''The five strings a committed probe file must not show (owner, plan 58 decision D3), the login name set
    to a value no path or word in a test holds.'''
    monkeypatch.setattr('getpass.getuser', lambda: 'zzlogin')
    return [str(Path.home()), str(Path.home().resolve()), tempfile.gettempdir(),
            os.path.realpath(tempfile.gettempdir()), 'zzlogin']


def test_the_log_row_holds_no_private_text_and_no_mcp_tool_name(isolated_home, monkeypatch):
    '''A finding built from an OSError, a scratch path or a tool name reaches a public repo through PROBES.md.'''
    planted = planted_privates(monkeypatch)
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
    assessment raise TypeError: the row is ERROR, and the run goes on.'''
    fake = FakeRuns({'pins': pins_stream()}, side={'pins': leave_transcripts(isolated_home, {'level': 'xhigh'})})
    assert probes.run_probe('agent-model-pins', 'claude', REPO, tmp_path / 'run', fake) == (
        ERROR, "TypeError: unhashable type: 'dict'")


# A run whose leader starts a child, as Gate B's bash starts claude. It writes "<leader> <child>" to $1.
SLOW = '#!/bin/sh\nsleep 300 &\necho "$$ $!" > "$1"\nsleep 300\n'
# The same, but the leader and its child ignore SIGTERM, as a stuck claude might, so only SIGKILL ends them.
STUBBORN = "#!/bin/sh\ntrap '' TERM\nsleep 300 &\necho \"$$ $!\" > \"$1\"\nwait\n"


def written(path: Path, wait: float = 5) -> bool:
    '''Whether the file holds text within `wait` seconds.'''
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        if path.is_file() and path.read_text(encoding='utf-8').strip():
            return True
        time.sleep(0.01)
    return False


def gone(pid: int, wait: float = 5) -> bool:
    '''Whether the process ends within `wait` seconds.'''
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.05)
    return False


@pytest.fixture
def pids(tmp_path):
    '''The pid file a SLOW or STUBBORN run writes. Teardown kills what is
    left of its process group, so a failing test leaks no sleep.'''
    path = tmp_path / 'pids'
    yield path
    if path.is_file() and path.read_text(encoding='utf-8').split():
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(int(path.read_text(encoding='utf-8').split()[0]), signal.SIGKILL)


def child_of(path: Path) -> int:
    return int(path.read_text(encoding='utf-8').split()[1])


def test_a_timeout_stops_everything_the_run_started(tmp_path, pids):
    '''Gate B runs claude under bash: a timeout must stop the grandchild too,
    not only the bash that started it.'''
    inv = probes.Invocation('slow', [str(executable(tmp_path / 'slow', SLOW)), str(pids)], {}, 3)
    assert probes.execute(inv, tmp_path, tmp_path / 'slow.out', tmp_path / 'slow.err') is None
    assert written(pids), 'the run was stopped before it started its child'
    assert gone(child_of(pids))


def test_an_interrupt_stops_everything_the_run_started_and_still_propagates(tmp_path, pids, monkeypatch):
    '''Ctrl-C while a probe runs: its own process group gets no SIGINT from
    the terminal, so execute stops the group itself before re-raising.'''
    real_wait = subprocess.Popen.wait

    def interrupted(proc, timeout=None):
        if timeout == 30:  # the probe's own wait, once its child is running
            assert written(pids), 'the run never started its child'
            raise KeyboardInterrupt
        return real_wait(proc, timeout)
    monkeypatch.setattr(subprocess.Popen, 'wait', interrupted)
    inv = probes.Invocation('slow', [str(executable(tmp_path / 'slow', SLOW)), str(pids)], {}, 30)
    with pytest.raises(KeyboardInterrupt):
        probes.execute(inv, tmp_path, tmp_path / 'slow.out', tmp_path / 'slow.err')
    assert gone(child_of(pids))


def test_a_stop_while_the_run_starts_still_stops_it(tmp_path, pids, monkeypatch):
    '''A SIGTERM that lands while Popen starts the run is held until proc
    is bound, so the run is stopped, not orphaned.'''
    real_popen, leaders = subprocess.Popen, []

    def starting(*args, **kwargs):
        proc = real_popen(*args, **kwargs)
        leaders.append(proc.pid)
        os.kill(os.getpid(), signal.SIGTERM)
        return proc
    monkeypatch.setattr(subprocess, 'Popen', starting)
    inv = probes.Invocation('slow', [str(executable(tmp_path / 'slow', SLOW)), str(pids)], {}, 30)
    with pytest.raises(SystemExit):
        with probes.term_as_exit():
            probes.execute(inv, tmp_path, tmp_path / 'slow.out', tmp_path / 'slow.err')
    assert gone(leaders[0])


def test_a_second_signal_during_the_grace_still_ends_with_sigkill(tmp_path, pids, monkeypatch):
    '''Ctrl-C while stop_group waits out SIGTERM's grace is held, so the
    SIGKILL still goes out, and the interrupt is raised after it.'''
    monkeypatch.setattr(probes, 'KILL_GRACE', 1)
    proc = subprocess.Popen([str(executable(tmp_path / 'stubborn', STUBBORN)), str(pids)], start_new_session=True)
    assert written(pids)
    threading.Timer(0.3, os.kill, (os.getpid(), signal.SIGINT)).start()
    with pytest.raises(KeyboardInterrupt):
        probes.stop_group(proc)
    assert gone(child_of(pids))


# Run in a child Python, so a signal left at its default ends the child, not pytest.
STOP_CHECK = """
import os, signal, sys, time
import probes
signum = int(sys.argv[1])
before = signal.getsignal(signum)
try:
    with probes.term_as_exit():
        os.kill(os.getpid(), signum)
        time.sleep(5)
except SystemExit:
    assert signal.getsignal(signum) is before
    raise
"""


@pytest.mark.parametrize('signum', [signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT])
def test_a_stop_signal_while_probes_run_exits_through_the_cleanup_path(signum):
    '''SIGTERM (a stopped tool), SIGHUP (a closed terminal) and SIGQUIT end
    Python with no except or finally by default; while probes run each one
    raises SystemExit instead, and the old handler comes back after. A
    negative exit code means the signal ended the child unhandled.'''
    proc = subprocess.run([sys.executable, '-c', STOP_CHECK, str(int(signum))], cwd=Path(__file__).parent,
                          capture_output=True, text=True, timeout=30)
    assert (proc.returncode, proc.stderr) == (128 + signum, '')


def test_a_hangup_ignored_by_nohup_stays_ignored():
    before = signal.signal(signal.SIGHUP, signal.SIG_IGN)
    try:
        with probes.term_as_exit():
            assert signal.getsignal(signal.SIGHUP) is signal.SIG_IGN
    finally:
        signal.signal(signal.SIGHUP, before)


def test_held_signals_act_once_the_block_is_done():
    reached = []
    with pytest.raises(SystemExit):
        with probes.term_as_exit():
            with probes.held_signals():
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(0.2)
                reached.append('end of block')
    assert reached == ['end of block']


def test_a_setup_failure_is_an_error_never_a_pass(tmp_path, monkeypatch):
    def broken(scratch, claude, repo):
        raise OSError('disk full')
    monkeypatch.setitem(probes.PROBE_RUNS, 'agent-tools', probes.PROBE_RUNS['agent-tools']._replace(prepare=broken))
    assert probes.run_probe('agent-tools', 'claude', REPO, tmp_path / 'run', FakeRuns({})) == (
        ERROR, 'OSError: disk full')


def test_save_fixtures_scrubs_a_recorded_run_and_the_replay_reads_it_like_the_run(tmp_path, isolated_home,
                                                                                   monkeypatch):
    # The trim drops an init event's cwd and memory_paths, so those prove nothing. The private strings go where the
    # trim keeps them, a Bash command, and each must come out as <private> on its own: a path that another entry
    # covers by its prefix, as the temporary directory covers a home inside it, must not hide an uncovered one.
    monkeypatch.setattr('getpass.getuser', lambda: 'zzlogin')
    planted = [str(Path.home()), str(Path.home().resolve()), tempfile.gettempdir(),
               os.path.realpath(tempfile.gettempdir()), 'zzlogin']
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
def test_save_fixtures_scrubs_a_side_file_as_well_as_a_stream(tmp_path, isolated_home, monkeypatch, pid, stream_name,
                                                              side_name, template, fixture):
    '''A transcripts.json or a stop.log is copied whole, so it needs the same scrub as a stream.'''
    planted = planted_privates(monkeypatch)
    run_dir, dest = tmp_path / 'run', tmp_path / 'fixtures'
    write_tree(run_dir, {stream_name: stream(init(), RESULT), side_name: template.replace('@P@', ' '.join(planted))})
    probes.save_fixtures(run_dir, pid, dest)
    saved = (dest / fixture).read_text()
    for value in planted:
        assert value not in saved
    assert saved == template.replace('@P@', ' '.join(['<private>'] * len(planted)))
