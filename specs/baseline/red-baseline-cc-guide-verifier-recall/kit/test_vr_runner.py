'''No-model tests of plan 102's kit runner (Task 6).

Every test runs with HOME and common.R under pytest's temporary folder, and
with common.KIT pointed at fakes there too (the autouse fixture checks all
three before the test body runs). The held binary is a stub claude: a Python
script that records its argv, environment, working folder and stdin, writes a
marker into its working folder and TMPDIR, lists R into its stream, and writes
a fake session under $HOME/.claude/projects/. No test reaches the real $K,
/private/tmp/vr102 or ~/.claude/projects/, and no test spends money.'''
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

import build
import common
import postprocess
import run

KEY = 'credential_expires_at'
ARM_WORDS = ('control', 'changed')
ENV_KEYS = {'HOME', 'USER', 'LOGNAME', 'SHELL', 'LANG', 'PATH', 'TMPDIR', 'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS',
            'DISABLE_AUTOUPDATER'}
REP_PATH = '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
DEFAULT_R, DEFAULT_KIT = common.R, common.KIT  # read at import, before the fixture replaces them

# The stub claude. run.py gives it an environment built from scratch, so it
# reads its behavior from a config file whose path is baked in (__CONFIG__).
# It records the environment it got at exec (/proc/self/environ, or macOS's
# KERN_PROCARGS2), since a macOS Python's own startup adds
# __CF_USER_TEXT_ENCODING (and LC_CTYPE under a C locale) to os.environ.
STUB = r'''#!__PYTHON__
import ctypes, ctypes.util, json, os, pathlib, secrets, struct, sys, time


def exec_env():
    if os.path.exists('/proc/self/environ'):
        raw = pathlib.Path('/proc/self/environ').read_bytes()
        return dict(e.decode().split('=', 1) for e in raw.split(b'\0') if e)
    libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
    mib = (ctypes.c_int * 3)(1, 49, os.getpid())  # CTL_KERN, KERN_PROCARGS2
    size = ctypes.c_size_t(0)
    assert libc.sysctl(mib, 3, None, ctypes.byref(size), None, 0) == 0
    buf = ctypes.create_string_buffer(size.value)
    assert libc.sysctl(mib, 3, buf, ctypes.byref(size), None, 0) == 0
    raw = buf.raw[:size.value]
    parts = raw[4:].split(b'\0')
    i = 1
    while parts[i] == b'':
        i += 1
    i += struct.unpack('i', raw[:4])[0]
    env = {}
    while i < len(parts) and parts[i]:
        key, _, value = parts[i].decode().partition('=')
        env[key] = value
        i += 1
    return env


config = json.loads(pathlib.Path('__CONFIG__').read_text())
if not os.environ.get('HOME', '').startswith(config['base']):
    sys.exit(97)
cwd = pathlib.Path.cwd()
rid = cwd.parent.name
mine = config['reps'].get(rid, {})
stdin = sys.stdin.read()
child = None
if mine.get('sleep'):
    import subprocess
    child = subprocess.Popen(['/bin/sleep', str(mine['sleep'])]).pid
calls = pathlib.Path(config['calls'])
calls.mkdir(parents=True, exist_ok=True)
(calls / (rid + '.json')).write_text(json.dumps(
    {'argv': sys.argv, 'env': exec_env(), 'runtime_keys': sorted(os.environ), 'cwd': os.getcwd(), 'stdin': stdin,
     'pid': os.getpid(), 'child': child}))
if mine.get('silent'):
    sys.exit(mine.get('exit', 1))
token = secrets.token_hex(8)
for folder in (cwd, pathlib.Path(os.environ['TMPDIR'])):
    (folder / ('marker-' + token + '.txt')).write_text(token)
listing = sorted(str(p) for p in pathlib.Path(config['root']).rglob('*'))
sid = mine.get('session', 'sess-' + token)


def emit(record):
    print(json.dumps(record), flush=True)


emit({'type': 'system', 'subtype': 'init', 'session_id': sid, 'cwd': os.getcwd()})
emit({'type': 'stub', 'listing': listing})
emit({'type': 'system', 'subtype': 'status', 'credential_expires_at': 1})
print('stub stderr ' + mine.get('stderr', ''), file=sys.stderr, flush=True)
time.sleep(mine.get('sleep', 0))
if not mine.get('no_session_files'):
    project = pathlib.Path(os.environ['HOME']) / '.claude' / 'projects' / os.getcwd().replace('/', '-')
    (project / sid / 'subagents').mkdir(parents=True, exist_ok=True)
    (project / (sid + '.jsonl')).write_text(json.dumps({'type': 'user', 'meta': {'credential_expires_at': 2}}) + '\n')
    (project / sid / 'subagents' / 'agent-a1.meta.json').write_text(
        json.dumps({'agentType': 'cc-guide-verifier', 'credential_expires_at': 3}))
    (project / sid / 'subagents' / 'agent-a1.jsonl').write_text(
        json.dumps({'type': 'assistant', 'message': {'model': 'm', 'credential_expires_at': 4}}) + '\n')
if 'early_cost' in mine:
    emit({'type': 'result', 'subtype': 'success', 'is_error': False, 'total_cost_usd': mine['early_cost']})
if not mine.get('no_result'):
    emit({'type': 'result', 'subtype': 'success', 'is_error': False, 'total_cost_usd': mine.get('cost', 0.5),
          'result': 'the report', 'usage': {'server': {'credential_expires_at': 5}},
          'notes': [{'kept': 1}, {'credential_expires_at': 6}]})
sys.exit(mine.get('exit', 0))
'''

AUDIT_INDEX = {'mode': 'audit', 'group': 'models', 'sections': ['models.one'], 'lines': {'models.one': [1, 9]},
               'docs': '/master/docs', 'releases': [], 'held': [],
               'quotes': {'guide': ['guide.md'], 'changelog': ['changelog.md'], 'docs': ['/master/docs']},
               'blocks': []}


@pytest.fixture(autouse=True)
def sandbox(tmp_path, tmp_path_factory, monkeypatch):
    '''HOME, R and KIT under pytest's temporary folder, checked before any test
    body runs: run.py moves files out of $HOME/.claude/projects/ and out of R.'''
    base = tmp_path_factory.getbasetemp().resolve()
    home = tmp_path / 'home'
    home.mkdir()
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setattr(common, 'R', tmp_path / 'R')
    monkeypatch.setattr(common, 'KIT', tmp_path / 'kitfiles')
    assert_sandboxed(base)
    return base


def assert_sandboxed(base: Path) -> None:
    for path in (Path(os.environ['HOME']), common.R, common.k_dir(), common.KIT):
        assert path.resolve().is_relative_to(base), path


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


def write_json(path: Path, obj) -> Path:
    return write(path, json.dumps(obj, indent=1) + '\n')


@pytest.fixture
def kit(tmp_path, sandbox):
    '''$K with fake arms, packet copies, docs, a stub binary and a ceiling.'''
    k = common.k_dir()
    write(k / 'arms' / 'control.md', '---\nname: cc-guide-verifier\n---\n\nArm one body.\n')
    write(k / 'arms' / 'changed.md', '---\nname: cc-guide-verifier\n---\n\nArm two body, with listed items.\n')
    fx = k / 'fixtures'
    for name, index in (('audit-control', AUDIT_INDEX),
                        ('audit-changed', AUDIT_INDEX | {'listed': [{'item': 'L1', 'line': 1288}]})):
        write_json(fx / name / 'index.json', index)
        for leaf in ('guide.md', 'sections.md', 'changelog.md', 'releases.md', 'report.md', 'settled.json'):
            write(fx / name / leaf, f'{leaf}\n')
    write(fx / 'audit-changed' / 'listed.md', 'L1 | changelog.md:1288\n')
    write_json(fx / 'readme' / 'index.json', {'mode': 'files', 'file': 'hooks/README.md', 'copy': 'cited_README.md',
                                              'quotes': {'guide': ['guide.md']}, 'covered': {}})
    for leaf in ('cited_README.md', 'guide.md', 'sections.md', 'report.md', 'settled.json'):
        write(fx / 'readme' / leaf, f'{leaf}\n')
    write_json(fx / 'precision' / 'index.json',
               {'mode': 'files', 'file': 'skills/x/SKILL.md', 'copy': 'cited_SKILL.md',
                'quotes': {'guide': ['guide.md']}, 'covered': {'skills/x/references/a.md': 'covered/references/a.md'}})
    for leaf in ('cited_SKILL.md', 'guide.md', 'sections.md', 'covered/references/a.md',
                 'covered/references/report.md'):
        write(fx / 'precision' / leaf, f'{leaf}\n')
    write(fx / 'docs' / 'changelog.md', 'docs changelog\n')
    write(fx / 'docs' / 'settings.md', 'docs settings\n')
    write(common.KIT / 'probe.txt', 'Probe. Read {canary} and report.\n')
    write(common.KIT / 'vr-probe.md', '---\nname: vr-probe\n---\n\nProbe agent.\n')
    config = tmp_path / 'stub' / 'config.json'
    write_json(config, {'base': str(sandbox), 'calls': str(tmp_path / 'calls'), 'root': str(common.R), 'reps': {}})
    stub = write(tmp_path / 'stub' / 'claude',
                 STUB.replace('__PYTHON__', sys.executable).replace('__CONFIG__', str(config)))
    stub.chmod(0o755)
    hold_binary(stub)
    write(k / 'ceiling.txt', '130\n')
    return k


def hold_binary(stub: Path) -> None:
    digest = hashlib.sha256(stub.read_bytes()).hexdigest()
    write(common.k_dir() / 'binary.txt', f'path: {stub}\nversion: 0.0.0 (stub)\nsha256: {digest}\n')


def configure(tmp_path: Path, rid: str, **behavior) -> None:
    path = tmp_path / 'stub' / 'config.json'
    config = json.loads(path.read_text())
    config['reps'][rid] = behavior
    write_json(path, config)


def plan(*reps: tuple[str, str, str], batch: str = 'b', role: str = 'counted') -> None:
    '''Add reps, each (rid, packet, arm), to plan.json and to the batch file,
    in build.py's formats.'''
    k = common.k_dir()
    path = k / 'plan.json'
    data = json.loads(path.read_text()) if path.exists() else {'reps': []}
    data['reps'] += [{'rid': rid, 'batch': batch, 'packet': packet, 'arm': arm, 'role': role}
                     for rid, packet, arm in reps]
    write_json(path, data)
    (k / 'batches').mkdir(parents=True, exist_ok=True)
    with (k / 'batches' / f'{batch}.txt').open('a') as f:
        f.writelines(rid + '\n' for rid, _, _ in reps)


def run_batch(sandbox: Path, name: str = 'b') -> int:
    '''run.main, after checking again that HOME and R are temporary.'''
    assert_sandboxed(sandbox)
    return run.main([name])


def calls(tmp_path: Path) -> dict[str, dict]:
    folder = tmp_path / 'calls'
    return {p.stem: json.loads(p.read_text()) for p in sorted(folder.glob('*.json'))} if folder.is_dir() else {}


def stream(rid: str) -> list[dict]:
    text = (common.k_dir() / 'results' / rid / 'stream.jsonl').read_text()
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def listing(rid: str) -> list[str]:
    return next(r['listing'] for r in stream(rid) if r.get('type') == 'stub')


def status(rid: str) -> dict:
    return json.loads((common.k_dir() / 'results' / rid / 'status.json').read_text())


def gone(pid: int, wait: float = 5.0) -> bool:
    '''Whether process pid has ended (and been reaped) within wait seconds.'''
    end = time.monotonic() + wait
    while time.monotonic() < end:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.05)
    return False


def wait_for(path: Path, limit: float = 15.0) -> bool:
    '''Whether path exists within limit seconds.'''
    end = time.monotonic() + limit
    while time.monotonic() < end:
        if path.exists():
            return True
        time.sleep(0.05)
    return False


# Runs run.main in a child process, with common.R and common.KIT set as in the
# fixture. It refuses (exit 97) unless HOME and R lie under pytest's folder.
DRIVER = '''import os, sys
from pathlib import Path
base, kit, root, kitfiles, batch = sys.argv[1:6]
if not os.environ['HOME'].startswith(base) or not root.startswith(base):
    sys.exit(97)
sys.path.insert(0, kit)
import common, run
common.R = Path(root)
common.KIT = Path(kitfiles)
sys.exit(run.main([batch]))
'''


def start_runner(tmp_path: Path, sandbox: Path, batch: str = 'b') -> subprocess.Popen:
    '''run.py's entry point in a child process, with this test's HOME, R and KIT.'''
    assert_sandboxed(sandbox)
    driver = write(tmp_path / 'driver.py', DRIVER)
    argv = [sys.executable, str(driver), str(sandbox), str(Path(__file__).resolve().parent), str(common.R),
            str(common.KIT), batch]
    return subprocess.Popen(argv, env=dict(os.environ), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def no_arm_named(text: str) -> bool:
    lowered = text.lower()
    return not any(w in lowered for w in ARM_WORDS) and 'arms/' not in lowered


def scripted(monkeypatch, values: list[int]) -> list[int]:
    '''Replace secrets.randbelow with a script; returns the list of its arguments.'''
    seen = []

    def fake(n):
        seen.append(n)
        return values.pop(0)

    monkeypatch.setattr(build.secrets, 'randbelow', fake)
    return seen


# --- the plan's tests ---------------------------------------------------------------------------------------


def test_two_reps_see_nothing_of_each_other(kit, tmp_path, sandbox):
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))
    assert run_batch(sandbox) == 0
    homes = kit / 'homes'
    token = next((homes / 'r001' / 'work').glob('marker-*.txt')).read_text()
    assert (homes / 'r001' / 'tmp' / f'marker-{token}.txt').is_file()
    seen = listing('r002')
    assert any('r002' in entry for entry in seen)
    assert not [entry for entry in seen if token in entry or 'r001' in entry]
    assert (homes / 'r001').is_dir() and (homes / 'r002').is_dir()
    assert not any(common.R.iterdir())
    recorded = calls(tmp_path)
    assert [recorded[rid]['env']['TMPDIR'] for rid in ('r001', 'r002')] == [str(common.R / 'r001' / 'tmp'),
                                                                              str(common.R / 'r002' / 'tmp')]


def test_the_runner_refuses_a_nonempty_rep_root(kit, tmp_path, sandbox):
    plan(('r001', 'readme', 'control'))
    write(common.R / 'stray.txt', 'left over\n')
    assert run_batch(sandbox) == 3
    assert calls(tmp_path) == {}
    assert not (kit / 'results' / 'r001').exists()


def test_rep_files_hold_no_credential_expires_at(kit, sandbox):
    plan(('r001', 'readme', 'control'))
    assert run_batch(sandbox) == 0
    results = kit / 'results' / 'r001'
    files = [p for p in results.rglob('*') if p.is_file()]
    assert {p.name for p in files} >= {'stream.jsonl', 'stderr.txt', 'result.json', 'agent-a1.meta.json'}
    assert [p for p in files if KEY.encode() in p.read_bytes()] == []
    assert json.loads((results / 'result.json').read_text())['total_cost_usd'] == 0.5


def test_the_rep_command_denies_bash_and_fences_reads(kit):
    plan(('r001', 'audit', 'control'))
    argv, env = run.command('r001')
    settings = json.loads(argv[argv.index('--settings') + 1])
    assert 'Bash' in settings['permissions']['deny']
    assert 'Read(~/**)' in settings['permissions']['deny']
    assert settings['permissions']['blockReadsOutsideWorkingDirectories'] is True
    assert set(env) == ENV_KEYS
    assert int(env['CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS']) > common.TIMEOUTS['audit'] * 1000


@pytest.mark.parametrize('tool', ['ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger'])
def test_the_rep_command_denies_each_cross_session_tool(kit, tool):
    '''D5: the probe's init record listed these four, and a name-only deny
    rule removes a tool from a session's list. Every CROSS_SESSION_TOOLS name
    is in the deny list of the argv a rep runs with.'''
    plan(('r001', 'audit', 'control'))
    argv, _ = run.command('r001')
    deny = json.loads(argv[argv.index('--settings') + 1])['permissions']['deny']
    assert tool in common.CROSS_SESSION_TOOLS and tool in deny
    assert set(common.CROSS_SESSION_TOOLS) <= set(deny)


def test_no_controller_variable_reaches_a_rep(kit, tmp_path, sandbox, monkeypatch):
    monkeypatch.setenv('CLAUDECODE', '1')
    monkeypatch.setenv('CLAUDE_CODE_ENTRYPOINT', 'cli')
    plan(('r001', 'readme', 'control'))
    assert run_batch(sandbox) == 0
    env = calls(tmp_path)['r001']['env']
    assert set(env) == ENV_KEYS
    assert env['HOME'] == os.environ['HOME']


def test_the_ceiling_holds_a_rep_whose_cap_does_not_fit(kit, tmp_path, sandbox, capsys):
    write(kit / 'ceiling.txt', '13\n')
    configure(tmp_path, 'r001', cost=8.5)  # r002: 8.5 + 10 exceeds 13; r003 alone would fit (8.5 + 4)
    plan(('r001', 'audit', 'control'), ('r002', 'audit', 'changed'), ('r003', 'readme', 'control'))
    assert run_batch(sandbox) == 5
    assert set(calls(tmp_path)) == {'r001'}
    assert not (kit / 'results' / 'r002').exists()
    held = [line for line in capsys.readouterr().out.splitlines() if 'held' in line]
    assert [line.split(':')[0] for line in held] == ['r002', 'r003']


def test_an_audit_reps_index_names_its_own_docs_copy_in_both_arms(kit, sandbox):
    plan(('r001', 'audit', 'control'), ('r002', 'audit', 'changed'))
    assert run_batch(sandbox) == 0
    indexes = {}
    for rid in ('r001', 'r002'):
        index = json.loads((kit / 'homes' / rid / 'work' / 'packet' / 'index.json').read_text())
        docs = str(common.R / rid / 'work' / 'docs')
        assert index['docs'] == docs
        assert index['quotes']['docs'] == [docs]
        assert (kit / 'homes' / rid / 'work' / 'docs' / 'changelog.md').is_file()
        indexes[rid] = index
    assert 'listed' not in indexes['r001']
    assert indexes['r002']['listed'] == [{'item': 'L1', 'line': 1288}]

    def normalized(index):
        rest = {k: v for k, v in index.items() if k != 'listed'}
        return rest | {'docs': 'D', 'quotes': rest['quotes'] | {'docs': ['D']}}

    assert normalized(indexes['r001']) == normalized(indexes['r002'])


def test_build_orders_each_pair_at_random_and_batches_name_no_arm(kit, monkeypatch):
    script = [0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1]
    seen = scripted(monkeypatch, list(script))
    assert build.main(['batch', 'g1', 'audit', '12']) == 0
    assert seen == [2] * 12
    reps = json.loads((kit / 'plan.json').read_text())['reps']
    assert [r['rid'] for r in reps] == [f'r{i:03d}' for i in range(1, 25)]
    arms = [r['arm'] for r in reps]
    assert [tuple(arms[i:i + 2]) for i in range(0, 24, 2)] == [
        ('control', 'changed') if first == 0 else ('changed', 'control') for first in script]
    assert {(r['batch'], r['packet']) for r in reps} == {('g1', 'audit')}
    lines = (kit / 'batches' / 'g1.txt').read_text().splitlines()
    assert lines == [r['rid'] for r in reps]
    assert all(re.fullmatch(r'r\d{3}', line) for line in lines)


def test_build_refuses_a_third_spare(kit, monkeypatch, capfd):
    scripted(monkeypatch, [0, 0, 0])
    assert build.main(['batch', 'f1', 'readme', '3']) == 0  # r001 control, r002 changed, ...
    assert build.main(['spare', 'r001']) == 0  # r007
    assert build.main(['spare', 'r007']) == 0  # r008: a spare's spare counts too
    before = (kit / 'plan.json').read_bytes(), (kit / 'batches' / 'f1.txt').read_bytes()
    capfd.readouterr()
    assert build.main(['spare', 'r001']) == 1
    out, err = capfd.readouterr()
    assert 'spare' in out + err
    assert not [w for w in ARM_WORDS if w in (out + err).lower()]
    assert ((kit / 'plan.json').read_bytes(), (kit / 'batches' / 'f1.txt').read_bytes()) == before
    assert build.main(['spare', 'r002']) == 0  # the other arm has its own two


# --- the extra blind-reading test ---------------------------------------------------------------------------


def test_no_output_line_names_an_arm(kit, tmp_path, sandbox, monkeypatch, capfd):
    scripted(monkeypatch, [1, 0, 1, 0])
    assert build.main(['batch', 'f1', 'readme', '2']) == 0  # r001-r004
    assert build.main(['batch', 'a1', 'audit', '1']) == 0  # r005-r006
    assert build.main(['spare', 'r001']) == 0  # r007
    assert build.main(['spare', 'r001']) == 0  # r008
    assert build.main(['spare', 'r001']) == 1
    assert build.main(['probe']) == 0  # r009
    assert build.main(['pilot']) == 0  # r010
    configure(tmp_path, 'r002', stderr=KEY)  # void under V6
    for batch in ('f1', 'a1', 'probe', 'pilot', 'f1'):
        assert run_batch(sandbox, batch) == 0
    assert postprocess.main(['strip-tree', str(kit / 'results')]) == 0
    assert build.main(['batch', 'a2', 'audit', '1']) == 0  # r011-r012
    write(common.R / 'stray', '')
    assert run_batch(sandbox, 'a2') == 3
    (common.R / 'stray').unlink()
    good = (kit / 'binary.txt').read_text()
    write(kit / 'binary.txt', re.sub(r'sha256: \w+', 'sha256: ' + '0' * 64, good))
    assert run_batch(sandbox, 'a2') == 4
    write(kit / 'binary.txt', good)
    for name in ('audit-control', 'audit-changed'):
        (kit / 'fixtures' / name).rename(tmp_path / name)
    assert run_batch(sandbox, 'a2') == 2
    assert not any(common.R.iterdir())
    write(kit / 'ceiling.txt', '1\n')
    assert run_batch(sandbox, 'a2') == 5
    out, err = capfd.readouterr()
    lines = (out + err).splitlines()
    assert any('r011' in line for line in lines) and any('held' in line for line in lines)
    assert any('r011' in line and 'missing' in line for line in lines)  # the cause is named, not the path
    assert not [line for line in lines if any(w in line.lower() for w in ARM_WORDS)]
    exempt = {kit / 'arms', kit / 'homes', kit / 'plan.json', kit / 'fixtures'}
    written = [p for p in kit.rglob('*') if not any(p == e or p.is_relative_to(e) for e in exempt)]
    assert not [p for p in written if any(w in str(p.relative_to(kit)).lower() for w in ARM_WORDS)]
    mine = [p for p in written if p.parent == kit / 'batches' or p.name == 'status.json']
    assert mine and not [p for p in mine if any(w in p.read_text().lower() for w in ARM_WORDS)]


# --- the input shapes of the stated rules -------------------------------------------------------------------


def test_the_constants_hold_the_plans_values():
    assert common.CAPS == {'audit': 10, 'files': 4, 'probe': 1}
    assert common.TIMEOUTS == {'audit': 3600, 'files': 1200, 'probe': 600}
    assert common.BG_CEILING_MS == 4_200_000
    assert common.MAX_SPARES == 2
    assert common.MARKERS == ('deniedModels', 'availableModels', 'effortLevel', 'README.md:89')
    assert json.loads(common.SETTINGS) == {  # PC2, as D5 amends it
        'permissions': {'deny': ['Bash', 'Read(~/**)', 'ListAgents', 'SendMessage', 'PushNotification',
                                 'RemoteTrigger'], 'blockReadsOutsideWorkingDirectories': True}}
    assert common.CROSS_SESSION_TOOLS == ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')
    assert {p: (v['mode'], v['reps']) for p, v in common.PACKETS.items()} == {
        'audit': ('audit', 5), 'readme': ('files', 3), 'precision': ('files', 3)}
    assert common.PACKETS['audit']['master'] == 'cc-guide/packets/20261013T113847-audit'
    assert common.PACKETS['readme']['master'] == 'cc-guide/packets/20261013T121854-files/hooks__README.md'
    assert [common.kind(p) for p in ('audit', 'readme', 'precision', 'probe')] == ['audit', 'files', 'files', 'probe']
    assert common.REPO == Path(__file__).resolve().parents[4]
    assert str(common.REPO / 'build' / 'cc_guide') in sys.path
    assert common.k_dir() == Path(os.environ['HOME']) / '.cache' / 'agent-skills' / 'scratch' / 'vr102'


def test_the_rep_root_and_kit_defaults():
    assert DEFAULT_R == Path('/private/tmp/vr102')
    assert DEFAULT_KIT == Path(common.__file__).resolve().parent


@pytest.mark.parametrize('packet, cap, timeout', [('audit', '10', 3600), ('readme', '4', 1200),
                                                  ('precision', '4', 1200), ('probe', '1', 600)])
def test_command_gives_the_exact_argv_and_env_for_each_packet_kind(kit, monkeypatch, packet, cap, timeout):
    monkeypatch.setenv('USER', 'tester')
    monkeypatch.setenv('LOGNAME', 'tester-login')
    monkeypatch.setenv('LANG', 'C.UTF-8')
    plan(('r001', 'readme', 'control'), ('r002', packet, 'control' if packet == 'probe' else 'changed'))
    argv, env = run.command('r002')
    stub = re.search(r'path: (.+)', (kit / 'binary.txt').read_text()).group(1)
    assert argv == [stub, '-p', '--permission-mode', 'auto', '--settings', common.SETTINGS,
                    '--max-budget-usd', cap, '--output-format', 'stream-json', '--verbose']
    assert run.limits('r002') == (common.CAPS[common.kind(packet)], timeout)
    assert env == {'HOME': os.environ['HOME'], 'USER': 'tester', 'LOGNAME': 'tester-login', 'SHELL': '/bin/zsh',
                   'LANG': 'C.UTF-8', 'PATH': REP_PATH, 'TMPDIR': str(common.R / 'r002' / 'tmp'),
                   'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': '4200000', 'DISABLE_AUTOUPDATER': '1'}


def test_a_rep_past_its_timeout_is_stopped_and_recorded(kit, tmp_path, sandbox, monkeypatch):
    monkeypatch.setattr(common, 'TIMEOUTS', {'audit': 60, 'files': 1, 'probe': 60})
    configure(tmp_path, 'r001', sleep=30)
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))
    started = time.monotonic()
    assert run_batch(sandbox) == 0
    assert time.monotonic() - started < 20
    assert status('r001')['timed_out'] is True and status('r002')['timed_out'] is False
    stopped = calls(tmp_path)['r001']
    assert gone(stopped['pid']) and gone(stopped['child'])  # the stub and its child, the whole group
    assert not (kit / 'results' / 'r001' / 'result.json').exists()
    assert (kit / 'homes' / 'r001').is_dir() and not any(common.R.iterdir())


@pytest.mark.parametrize('stray', ['folder', '.hidden'])
def test_the_runner_refuses_a_stray_folder_or_a_hidden_file(kit, tmp_path, sandbox, stray):
    plan(('r001', 'readme', 'control'))
    if stray == 'folder':
        (common.R / 'old').mkdir(parents=True)
    else:
        write(common.R / '.DS_Store', '')
    assert run_batch(sandbox) == 3
    assert calls(tmp_path) == {}


def test_the_runner_refuses_a_binary_whose_hash_differs(kit, tmp_path, sandbox):
    plan(('r001', 'readme', 'control'))
    stub = tmp_path / 'stub' / 'claude'
    stub.write_text(stub.read_text() + '# edited after the hash was held\n')
    assert run_batch(sandbox) == 4
    assert calls(tmp_path) == {}
    assert not (kit / 'results' / 'r001').exists()


def test_the_ceiling_counts_an_earlier_rep_at_its_cost_or_at_its_cap(kit, tmp_path, sandbox, capsys):
    write(kit / 'ceiling.txt', '14.5\n')
    configure(tmp_path, 'r001', no_result=True)  # counts at its cap, 10
    plan(('r001', 'audit', 'control'), batch='a')
    plan(('r002', 'readme', 'changed'), ('r003', 'readme', 'control'), ('r004', 'readme', 'changed'), batch='b')
    assert run_batch(sandbox, 'a') == 0
    assert run_batch(sandbox, 'b') == 5  # r002: 10 + 4; r003: 10.5 + 4, equal fits; r004: 11 + 4 exceeds
    assert set(calls(tmp_path)) == {'r001', 'r002', 'r003'}
    assert [line.split(':')[0] for line in capsys.readouterr().out.splitlines() if 'held' in line] == ['r004']


def test_the_runner_skips_a_rep_that_has_results(kit, tmp_path, sandbox, capsys):
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))
    (kit / 'results' / 'r001').mkdir(parents=True)
    assert run_batch(sandbox) == 0
    assert set(calls(tmp_path)) == {'r002'}
    assert any(line.startswith('r001') and 'skipped' in line for line in capsys.readouterr().out.splitlines())
    assert run_batch(sandbox) == 0
    assert set(calls(tmp_path)) == {'r002'}


def test_strip_removes_the_key_at_any_depth():
    deep = {KEY: 1, 'a': {'b': {KEY: 2, 'c': 3}}, 'list': [{KEY: 4, 'd': 5}, [{KEY: 6}], 7], 'e': None}
    assert postprocess.strip(deep) == {'a': {'b': {'c': 3}}, 'list': [{'d': 5}, [{}], 7], 'e': None}
    assert deep['a']['b'][KEY] == 2 and deep['list'][0][KEY] == 4  # the input is not changed
    absent = {'a': [1, {'b': 'credential'}], 'c': 'x'}
    assert postprocess.strip(absent) == absent
    assert postprocess.strip([{KEY: 1}, 2]) == [{}, 2]
    assert postprocess.strip('text') == 'text'


def test_strip_tree_rewrites_json_and_jsonl_in_place(tmp_path):
    root = tmp_path / 'tree'
    write_json(root / 'a.json', {'x': {'y': [{KEY: 1, 'z': 2}]}})
    keep_line = '{"type": "kept", "spacing": "as written"}'
    bad_line = 'not json but ' + KEY
    write(root / 'b.jsonl', '\n'.join(['{"' + KEY + '": 1, "k": 2}', keep_line, bad_line,
                                       '{"l": [{"' + KEY + '": 3}]}']) + '\n')
    other = write(root / 'c.txt', json.dumps({KEY: 1}) + '\n')
    plain = write(root / 'd.json', '{"spacing":   "kept"}\n')
    write(root / 'deep' / 'e.jsonl', json.dumps({'m': {KEY: 4}}) + '\n')
    before = other.read_bytes(), plain.read_bytes()
    assert postprocess.main(['strip-tree', str(root)]) == 0
    assert json.loads((root / 'a.json').read_text()) == {'x': {'y': [{'z': 2}]}}
    lines = (root / 'b.jsonl').read_text().splitlines()
    assert [json.loads(lines[0]), lines[1], lines[2], json.loads(lines[3])] == [{'k': 2}, keep_line, bad_line,
                                                                                 {'l': [{}]}]
    assert (other.read_bytes(), plain.read_bytes()) == before
    assert json.loads((root / 'deep' / 'e.jsonl').read_text()) == {'m': {}}


def test_a_rep_whose_results_keep_the_string_is_void(kit, tmp_path, sandbox, capsys):
    configure(tmp_path, 'r001', stderr=KEY)  # stderr.txt is no JSON file, so the strip leaves it
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))
    assert run_batch(sandbox) == 0
    assert status('r001')['strip_ok'] is False and status('r002')['strip_ok'] is True
    assert KEY.encode() not in (kit / 'results' / 'r001' / 'stream.jsonl').read_bytes()
    lines = capsys.readouterr().out.splitlines()
    assert [line.split(':')[0] for line in lines if 'V6' in line] == ['r001']


def test_session_files_move_by_the_init_session_id(kit, tmp_path, sandbox):
    projects = Path(os.environ['HOME']) / '.claude' / 'projects'
    others = [write(projects / '-elsewhere' / 'abc-1234.jsonl', '{}\n'),
              write(projects / '-elsewhere' / 'other.jsonl', '{}\n'),
              write(projects / '-elsewhere' / 'abc-1234' / 'subagents' / 'agent-b.jsonl', '{}\n')]
    configure(tmp_path, 'r001', session='abc-123')
    configure(tmp_path, 'r002', session='abc-999', no_session_files=True)
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))
    assert run_batch(sandbox) == 0
    slug = str(common.R / 'r001' / 'work').replace('/', '-')
    moved = kit / 'results' / 'r001' / 'project' / slug
    assert (moved / 'abc-123.jsonl').is_file()
    assert (moved / 'abc-123' / 'subagents' / 'agent-a1.meta.json').is_file()
    assert not [p for p in projects.rglob('*') if p.name.startswith('abc-123') and 'abc-1234' not in p.name]
    assert all(p.is_file() for p in others)
    assert not [p for p in (kit / 'results' / 'r002').rglob('*') if 'abc-' in p.name]


def test_the_result_json_is_the_streams_last_result_record(kit, tmp_path, sandbox):
    configure(tmp_path, 'r001', early_cost=0.1, cost=0.7)
    plan(('r001', 'readme', 'control'))
    assert run_batch(sandbox) == 0
    result = json.loads((kit / 'results' / 'r001' / 'result.json').read_text())
    assert result['total_cost_usd'] == 0.7 and result['result'] == 'the report'
    assert result['notes'] == [{'kept': 1}, {}]


def test_a_rep_folder_holds_the_arm_the_packet_copy_and_the_docs(kit, sandbox):
    plan(('r001', 'readme', 'control'), ('r002', 'precision', 'changed'), ('r003', 'audit', 'changed'))
    plan(('r004', 'probe', 'control'), batch='probe', role='probe')
    assert run_batch(sandbox) == 0 and run_batch(sandbox, 'probe') == 0
    homes = kit / 'homes'

    def files(rid, sub):
        folder = homes / rid / 'work' / sub
        return sorted(str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file())

    def verifier(rid):
        return (homes / rid / 'work' / '.claude' / 'agents' / 'cc-guide-verifier.md').read_text()

    assert verifier('r001') == (kit / 'arms' / 'control.md').read_text() == verifier('r004')
    assert verifier('r002') == (kit / 'arms' / 'changed.md').read_text() == verifier('r003')
    assert files('r001', 'packet') == ['cited_README.md', 'guide.md', 'index.json', 'sections.md']
    assert files('r002', 'packet') == ['cited_SKILL.md', 'covered/references/a.md', 'covered/references/report.md',
                                       'guide.md', 'index.json', 'sections.md']
    assert files('r003', 'packet') == ['changelog.md', 'guide.md', 'index.json', 'listed.md', 'releases.md',
                                       'sections.md']
    assert files('r003', 'docs') == files('r004', 'docs') == ['changelog.md', 'settings.md']
    assert not (homes / 'r001' / 'work' / 'docs').exists() and not (homes / 'r002' / 'work' / 'docs').exists()
    assert not (homes / 'r004' / 'work' / 'packet').exists()
    assert (homes / 'r004' / 'work' / '.claude' / 'agents' / 'vr-probe.md').read_text() == \
        (common.KIT / 'vr-probe.md').read_text()
    assert (kit / 'fixtures' / 'readme' / 'report.md').is_file()  # copied, not moved


def test_a_rep_gets_the_main_prompt_on_stdin_in_its_work_folder(kit, tmp_path, sandbox):
    assert build.main(['probe']) == 0  # r001, with a canary
    plan(('r002', 'audit', 'control'), ('r003', 'readme', 'changed'))
    assert run_batch(sandbox, 'probe') == 0 and run_batch(sandbox) == 0
    recorded = calls(tmp_path)
    for rid, mode in (('r002', 'audit'), ('r003', 'files')):
        packet = str(common.R / rid / 'work' / 'packet')
        assert recorded[rid]['stdin'] == common.MAIN.format(dispatch=common.DISPATCH.format(mode=mode, packet=packet))
        assert recorded[rid]['cwd'] == str(common.R / rid / 'work')
    canary = kit / 'canary.txt'
    assert re.fullmatch(r'[0-9a-f]{32}\n?', canary.read_text())
    assert recorded['r001']['stdin'] == f'Probe. Read {canary} and report.\n'
    skill = (common.REPO / '.claude' / 'skills' / 'cc-guide' / 'SKILL.md').read_text()
    assert '`' + common.DISPATCH.format(mode='<mode>', packet='<absolute packet directory>') + '`' in skill
    assert 'subagent_type cc-guide-verifier' in common.MAIN and 'model sonnet' in common.MAIN
    assert 'report' in common.MAIN.split('{dispatch}')[1]


def test_build_rep_ids_run_from_r001_and_are_never_reused(kit, monkeypatch, capsys):
    scripted(monkeypatch, [0, 0, 0])
    assert build.main(['batch', 'a', 'readme', '1']) == 0  # r001, r002
    assert build.main(['spare', 'r001']) == 0  # r003
    assert build.main(['pilot']) == 0  # r004
    assert build.main(['probe']) == 0  # r005
    assert build.main(['batch', 'b', 'audit', '1']) == 0  # r006, r007
    assert build.main(['batch', 'a', 'audit', '1']) == 0  # r008, r009: the name's batch grows
    reps = json.loads((kit / 'plan.json').read_text())['reps']
    assert [r['rid'] for r in reps] == ['r001', 'r002', 'r003', 'r004', 'r005', 'r006', 'r007', 'r008', 'r009']
    assert reps[3] == {'rid': 'r004', 'batch': 'pilot', 'packet': 'audit', 'arm': 'changed', 'role': 'pilot'}
    assert reps[4] == {'rid': 'r005', 'batch': 'probe', 'packet': 'probe', 'arm': 'control', 'role': 'probe'}
    batches = {p.stem: p.read_text().splitlines() for p in (kit / 'batches').glob('*.txt')}
    assert batches == {'a': ['r001', 'r002', 'r003', 'r008', 'r009'], 'pilot': ['r004'], 'probe': ['r005'],
                       'b': ['r006', 'r007']}
    out = capsys.readouterr().out
    assert all(f'r00{i}' in out for i in range(1, 10))


def test_a_spare_takes_the_void_reps_packet_and_arm(kit, monkeypatch):
    scripted(monkeypatch, [1, 0])
    assert build.main(['batch', 'p1', 'precision', '2']) == 0  # r001 changed, r002 control, r003 control, ...
    assert build.main(['spare', 'r001']) == 0
    assert build.main(['spare', 'r002']) == 0
    assert build.main(['spare', 'r099']) == 1  # no such rep
    reps = {r['rid']: r for r in json.loads((kit / 'plan.json').read_text())['reps']}
    assert reps['r005'] == {'rid': 'r005', 'batch': 'p1', 'packet': 'precision', 'arm': 'changed', 'role': 'spare',
                            'replaces': 'r001'}
    assert reps['r006'] == {'rid': 'r006', 'batch': 'p1', 'packet': 'precision', 'arm': 'control',
                                 'role': 'spare', 'replaces': 'r002'}
    assert build.main(['pilot']) == 0  # r007
    assert build.main(['spare', 'r007']) == 1  # an uncounted rep has no spare


# --- fix round 1 -------------------------------------------------------------------------------------------


def test_two_batch_calls_with_one_name_append_to_one_batch(kit, monkeypatch):
    scripted(monkeypatch, [0, 1, 1])
    assert build.main(['batch', 'gateF', 'readme', '1']) == 0  # r001, r002
    assert build.main(['spare', 'r002']) == 0  # r003 joins gateF
    assert build.main(['batch', 'gateF', 'precision', '2']) == 0  # r004 to r007
    reps = json.loads((kit / 'plan.json').read_text())['reps']
    assert [r['rid'] for r in reps] == [f'r{i:03d}' for i in range(1, 8)]
    assert [(r['packet'], r['arm']) for r in reps] == [
        ('readme', 'control'), ('readme', 'changed'), ('readme', 'changed'), ('precision', 'changed'),
        ('precision', 'control'), ('precision', 'changed'), ('precision', 'control')]
    assert {r['batch'] for r in reps} == {'gateF'}
    assert [p.name for p in (kit / 'batches').iterdir()] == ['gateF.txt']
    assert (kit / 'batches' / 'gateF.txt').read_text().splitlines() == [r['rid'] for r in reps]


def test_batch_names_take_mixed_case_but_not_a_case_only_variant(kit, monkeypatch, capfd):
    scripted(monkeypatch, [0, 0])
    assert build.main(['batch', 'gateA1', 'audit', '1']) == 0
    before = (kit / 'plan.json').read_bytes()
    capfd.readouterr()
    for name in ('gatea1', 'GATEA1', 'Probe', 'PILOT', 'probe', 'pilot', 'gate_A1'):
        assert build.main(['batch', name, 'audit', '1']) == 1, name
    out, err = capfd.readouterr()
    assert no_arm_named(out + err)
    assert (kit / 'plan.json').read_bytes() == before
    assert [p.name for p in (kit / 'batches').iterdir()] == ['gateA1.txt']
    assert build.main(['batch', 'gateA2', 'audit', '1']) == 0


def test_a_mixed_case_batch_runs_its_combined_reps_in_order(kit, tmp_path, sandbox, monkeypatch, capsys):
    scripted(monkeypatch, [1, 0])
    assert build.main(['batch', 'gateF', 'readme', '1']) == 0
    assert build.main(['batch', 'gateF', 'precision', '1']) == 0
    capsys.readouterr()
    assert run_batch(sandbox, 'gateF') == 0
    lines = capsys.readouterr().out.splitlines()
    assert [line.split(':')[0] for line in lines] == ['r001', 'r002', 'r003', 'r004']
    assert set(calls(tmp_path)) == {'r001', 'r002', 'r003', 'r004'}


def test_an_interrupted_runner_stops_the_rep_and_its_group(kit, tmp_path, sandbox, monkeypatch):
    '''Ctrl-C while a rep runs: the rep's whole process group is stopped before
    the runner moves R/<rid> to homes/, so R is empty and no rep runs on. The
    rep is recorded as interrupted (status.json exit null, timed_out false,
    interrupted true), leaves no result, and so counts at its cap.'''
    configure(tmp_path, 'r001', sleep=30)
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))

    def interrupted(self, input=None, timeout=None):
        self.stdin.write(input)
        self.stdin.close()
        assert wait_for(tmp_path / 'calls' / 'r001.json')
        raise KeyboardInterrupt

    monkeypatch.setattr(run.subprocess.Popen, 'communicate', interrupted)
    with pytest.raises(KeyboardInterrupt):
        run_batch(sandbox)
    stopped = calls(tmp_path)['r001']
    assert gone(stopped['pid']) and gone(stopped['child'])
    assert not any(common.R.iterdir())
    assert set(calls(tmp_path)) == {'r001'}
    assert status('r001') | {'seconds': 0} == {'exit': None, 'timed_out': False, 'interrupted': True,
                                               'seconds': 0, 'strip_ok': True}
    assert not (kit / 'results' / 'r001' / 'result.json').exists()
    assert run.spent() == common.CAPS['files']


def test_a_sigterm_to_the_runner_stops_the_rep(kit, tmp_path, sandbox):
    configure(tmp_path, 'r001', sleep=30)
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))
    runner = start_runner(tmp_path, sandbox)
    try:
        assert wait_for(tmp_path / 'calls' / 'r001.json')
        runner.send_signal(signal.SIGTERM)
        out, err = runner.communicate(timeout=30)
    finally:
        if runner.poll() is None:
            runner.kill()
    assert runner.returncode == 128 + signal.SIGTERM
    stopped = calls(tmp_path)['r001']
    assert gone(stopped['pid']) and gone(stopped['child'])
    assert not any(common.R.iterdir())
    assert set(calls(tmp_path)) == {'r001'}
    assert status('r001')['interrupted'] is True
    assert no_arm_named(out + err)


def test_a_rep_that_ends_before_its_init_record(kit, tmp_path, sandbox):
    projects = Path(os.environ['HOME']) / '.claude' / 'projects'
    kept = write(projects / '-elsewhere' / 'other.jsonl', '{}\n')
    configure(tmp_path, 'r001', silent=True, exit=1)
    plan(('r001', 'readme', 'control'), ('r002', 'readme', 'changed'))
    assert run_batch(sandbox) == 0
    assert status('r001')['exit'] == 1 and status('r002')['exit'] == 0
    assert set(calls(tmp_path)) == {'r001', 'r002'}
    assert not any(common.R.iterdir()) and (kit / 'homes' / 'r001').is_dir()
    assert kept.is_file() and not (kit / 'results' / 'r001' / 'project').exists()


def test_a_rep_that_exits_with_an_init_record_but_no_result(kit, tmp_path, sandbox, capsys):
    configure(tmp_path, 'r001', no_result=True, exit=2, session='abc-5')
    plan(('r001', 'readme', 'control'))
    assert run_batch(sandbox) == 0
    assert status('r001')['exit'] == 2
    assert not (kit / 'results' / 'r001' / 'result.json').exists()
    assert list((kit / 'results' / 'r001' / 'project').glob('*/abc-5.jsonl'))
    assert capsys.readouterr().out.startswith('r001: exit 2, no result')


def test_a_session_id_outside_the_pattern_moves_nothing(kit, tmp_path, sandbox):
    configure(tmp_path, 'r001', session='bad id')
    plan(('r001', 'readme', 'control'))
    assert run_batch(sandbox) == 0
    projects = Path(os.environ['HOME']) / '.claude' / 'projects'
    assert list(projects.glob('*/bad id.jsonl')) and list(projects.glob('*/bad id/subagents/*'))
    assert not (kit / 'results' / 'r001' / 'project').exists()
    assert status('r001')['exit'] == 0 and (kit / 'results' / 'r001' / 'result.json').is_file()


def test_a_copy_error_refuses_without_naming_an_arm(kit, tmp_path, sandbox, monkeypatch, capfd):
    def failing(src, dst, *args, **kwargs):
        raise OSError(f'cannot copy {src}')

    monkeypatch.setattr(run.shutil, 'copy2', failing)  # the arm file is the first thing copied
    plan(('r001', 'readme', 'control'))
    assert run_batch(sandbox) == 2
    out, err = capfd.readouterr()
    assert 'r001' in err and no_arm_named(out + err)
    assert not common.R.exists() or not any(common.R.iterdir())
    assert not (kit / 'results' / 'r001').exists() and not (kit / 'homes' / 'r001').exists()
    assert calls(tmp_path) == {}


def test_a_copy_error_in_the_entry_point_prints_no_arm(kit, tmp_path, sandbox):
    (kit / 'fixtures' / 'audit-changed' / 'gone.md').symlink_to(tmp_path / 'nowhere.md')  # a dangling link
    plan(('r001', 'audit', 'changed'))
    runner = start_runner(tmp_path, sandbox)
    out, err = runner.communicate(timeout=60)
    assert runner.returncode == 2
    assert 'r001' in err and 'Traceback' not in err and no_arm_named(out + err)
    assert not common.R.exists() or not any(common.R.iterdir())
    assert not (kit / 'results' / 'r001').exists() and calls(tmp_path) == {}
