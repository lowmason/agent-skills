'''Run one batch of plan 102's reps, one at a time, under Python 3.13:

    run.py <batch>

It reads the rep ids in $K/batches/<batch>.txt and skips each rep that
already has $K/results/<rid>/. For every other rep, in order, it:
  1. refuses (exit 3) while R holds anything (plan 100's C6);
  2. refuses (exit 4) when the held binary's sha256 differs from $K/binary.txt's;
  3. holds the rep, and every later one in the batch (exit 5), when the spend
     so far plus its cap exceeds $K/ceiling.txt. The spend counts each rep that
     has a results folder at its result's total_cost_usd, or at its cap when it
     left no result;
  4. builds R/<rid>/work/ and R/<rid>/tmp/ (the Rep layout): the arm's file as
     .claude/agents/cc-guide-verifier.md, the packet copy as packet/ without
     report.md or settled.json, and for an audit rep the docs copy as docs/,
     with the copy's index.json `docs` and `quotes.docs` naming it. The probe
     rep gets the control arm's file, the kit's vr-probe.md and the docs copy.
     A missing source, or a copy that fails, refuses (exit 2) with a message
     that names no path, and leaves R empty;
  5. runs command(rid) in R/<rid>/work with the prompt on stdin (common.MAIN,
     or probe.txt with {canary} filled in), stopping it at the rep's timeout,
     and writes stream.jsonl and stderr.txt to $K/results/<rid>/;
  6. moves the session's files, found under $HOME/.claude/projects/ by the
     first init record's session_id, to $K/results/<rid>/project/<slug>/;
  7. writes result.json, the stream's last `result` record;
  8. runs postprocess's strip-tree on $K/results/<rid>/, then fails the rep
     (V6) when the string credential_expires_at remains in any file there;
  9. writes status.json (exit, timed_out, interrupted, seconds, strip_ok) and
     moves R/<rid> to $K/homes/<rid>.
Steps 6 to 9 run even when the run fails, so R is empty for the next rep.
When the runner itself stops while a rep runs (Ctrl-C, or SIGTERM, which it
turns into SystemExit so cleanup runs), it first stops the rep's process
group, then runs steps 6 to 9 and records the rep as interrupted. Such a rep
leaves no result, so it counts at its cap.

Each printed line names a rep id, a status or a cost, never an arm (DF15).
Exit 0 when the batch is done, 2 on a usage or setup error.'''
import hashlib
import json
import os
import pwd
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import common
import postprocess

REP_PATH = '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
SKIP = {'report.md', 'settled.json'}  # a packet copy leaves these out (Rep layout)
SESSION_RE = re.compile(r'[0-9A-Za-z][0-9A-Za-z-]*')
KILL_GRACE = 10  # seconds between SIGTERM and SIGKILL for a rep past its timeout
EXIT_SETUP, EXIT_ROOT, EXIT_BINARY, EXIT_HELD = 2, 3, 4, 5


class Stop(Exception):
    '''Ends the batch with an exit code; its message names no arm.'''

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


def plan_reps() -> dict[str, dict]:
    path = common.k_dir() / 'plan.json'
    if not path.exists():
        raise Stop(EXIT_SETUP, 'no plan.json; run build.py first')
    return {rep['rid']: rep for rep in json.loads(path.read_text(encoding='utf-8'))['reps']}


def rep_of(rid: str) -> dict:
    reps = plan_reps()
    if rid not in reps:
        raise Stop(EXIT_SETUP, f'{rid}: not in plan.json')
    return reps[rid]


def limits(rid: str) -> tuple[int, int]:
    '''Rep rid's cap in USD and its timeout in seconds (PC9).'''
    kind = common.kind(rep_of(rid)['packet'])
    return common.CAPS[kind], common.TIMEOUTS[kind]


def held_binary() -> dict[str, str]:
    '''$K/binary.txt's fields: `path`, `version` and `sha256`, one `key: value` a line.'''
    path = common.k_dir() / 'binary.txt'
    if not path.exists():
        raise Stop(EXIT_SETUP, 'no binary.txt; hold the binary first (Task 8 Step 1)')
    fields = dict(line.split(': ', 1) for line in path.read_text(encoding='utf-8').splitlines() if ': ' in line)
    if not {'path', 'sha256'} <= fields.keys():
        raise Stop(EXIT_SETUP, 'binary.txt lacks its path or sha256 line')
    return fields


def command(rid: str) -> tuple[list[str], dict[str, str]]:
    '''Rep rid's argv and its whole environment, built from scratch (env -i,
    PC11), so no variable of the session that launched run.py reaches it.'''
    cap, _ = limits(rid)
    argv = [held_binary()['path'], '-p', '--permission-mode', 'auto', '--settings', common.SETTINGS,
            '--max-budget-usd', str(cap), '--output-format', 'stream-json', '--verbose']
    user = os.environ.get('USER') or pwd.getpwuid(os.getuid()).pw_name
    env = {'HOME': os.environ['HOME'], 'USER': user, 'LOGNAME': os.environ.get('LOGNAME') or user,
           'SHELL': '/bin/zsh', 'LANG': os.environ.get('LANG') or 'en_US.UTF-8', 'PATH': REP_PATH,
           'TMPDIR': str(common.R / rid / 'tmp'), 'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': str(common.BG_CEILING_MS),
           'DISABLE_AUTOUPDATER': '1'}
    return argv, env


def check_root() -> None:
    root = common.R
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise Stop(EXIT_ROOT, f'{root} holds files from an earlier rep; move them out before the next rep')


def check_binary() -> None:
    fields = held_binary()
    try:
        digest = hashlib.sha256(Path(fields['path']).read_bytes()).hexdigest()
    except OSError:
        digest = None
    if digest != fields['sha256'].strip():
        raise Stop(EXIT_BINARY, 'the held binary does not match the sha256 in binary.txt')


def cost_of(rid: str, reps: dict[str, dict]) -> float:
    '''What rep rid has cost: its result's total_cost_usd, else its full cap,
    since a run that left no result may still have spent it.'''
    path = common.k_dir() / 'results' / rid / 'result.json'
    if path.exists():
        cost = json.loads(path.read_text(encoding='utf-8')).get('total_cost_usd')
        if isinstance(cost, int | float) and not isinstance(cost, bool):
            return float(cost)
    return float(common.CAPS[common.kind(reps[rid]['packet'])] if rid in reps else max(common.CAPS.values()))


def spent() -> float:
    results = common.k_dir() / 'results'
    reps = plan_reps()
    return sum(cost_of(p.name, reps) for p in sorted(results.iterdir()) if p.is_dir()) if results.is_dir() else 0.0


def ceiling() -> float:
    path = common.k_dir() / 'ceiling.txt'
    if not path.exists():
        raise Stop(EXIT_SETUP, 'no ceiling.txt; the owner approves the ceiling first (Task 8 Step 4)')
    return float(path.read_text(encoding='utf-8').strip())


def prompt(rid: str, rep: dict) -> str:
    if rep['packet'] == common.PROBE:
        path = common.KIT / 'probe.txt'
        if not path.exists():
            raise Stop(EXIT_SETUP, f'{rid}: the kit has no probe.txt (Task 8 Step 5); nothing ran')
        text = path.read_text(encoding='utf-8')
        return text.replace(common.CANARY_FIELD, str(common.k_dir() / 'canary.txt'))
    packet = common.R / rid / 'work' / 'packet'
    mode = common.PACKETS[rep['packet']]['mode']
    return common.MAIN.format(dispatch=common.DISPATCH.format(mode=mode, packet=packet))


def sources(rep: dict) -> dict[str, Path]:
    '''What rep's work folder copies, by its place there.'''
    agents = Path('.claude') / 'agents'
    found = {str(agents / 'cc-guide-verifier.md'): common.k_dir() / 'arms' / f"{rep['arm']}.md"}
    if rep['packet'] == common.PROBE:
        found[str(agents / 'vr-probe.md')] = common.KIT / 'vr-probe.md'
    else:
        found['packet'] = common.fixture(rep['packet'], rep['arm'])
    if common.kind(rep['packet']) in ('audit', common.PROBE):
        found['docs'] = common.docs_fixture()
    return found


def skip_top(top: Path):
    '''A copytree ignore that leaves SKIP out of the packet's own folder only.'''
    return lambda folder, names: SKIP & set(names) if Path(folder) == top else set()


def build_folder(rid: str, rep: dict) -> Path:
    '''R/<rid>/work and R/<rid>/tmp (Rep layout); returns the work folder.'''
    found = sources(rep)
    if not all(src.exists() for src in found.values()):
        raise Stop(EXIT_SETUP, f'{rid}: its arm file, packet copy or docs copy is missing; nothing ran')
    work = common.R / rid / 'work'
    try:
        (common.R / rid / 'tmp').mkdir(parents=True)
        work.mkdir()
        for place, src in found.items():
            dst = work / place
            if src.is_dir():
                shutil.copytree(src, dst, ignore=skip_top(src))
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        if rep['packet'] == 'audit':
            index_path = work / 'packet' / 'index.json'
            index = json.loads(index_path.read_text(encoding='utf-8'))
            index['docs'] = str(work / 'docs')
            index['quotes']['docs'] = [str(work / 'docs')]
            index_path.write_text(json.dumps(index, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    except BaseException as error:
        shutil.rmtree(common.R / rid, ignore_errors=True)
        if isinstance(error, Exception):  # an OSError names a path, which may name an arm
            raise Stop(EXIT_SETUP, f'{rid}: its rep folder could not be built; nothing ran') from None
        raise
    return work


def launch(argv: list[str], env: dict[str, str], work: Path, text: str, timeout: int,
           results: Path) -> tuple[int | None, bool]:
    '''Run the rep; its exit code (None after a timeout) and whether it timed out.'''
    with (results / 'stream.jsonl').open('wb') as out, (results / 'stderr.txt').open('wb') as err:
        proc = subprocess.Popen(argv, cwd=work, env=env, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                start_new_session=True)
        try:
            proc.communicate(text.encode('utf-8'), timeout=timeout)
            return proc.returncode, False
        except subprocess.TimeoutExpired:
            stop_group(proc)
            return None, True
        except BaseException:  # Ctrl-C, SystemExit from SIGTERM: the paid rep must not run on
            stop_group(proc)
            raise


def stop_group(proc: subprocess.Popen) -> None:
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            break
        try:
            proc.wait(timeout=KILL_GRACE)
            break
        except subprocess.TimeoutExpired:
            continue
    proc.wait()


def records(path: Path) -> list[dict]:
    '''The stream's JSON objects; a line that is no JSON object is skipped.'''
    found = []
    if path.exists():
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
            obj = postprocess.parsed(line)
            if isinstance(obj, dict):
                found.append(obj)
    return found


def move_session(session: str | None, dest: Path) -> int:
    '''Move <slug>/<session>.jsonl and <slug>/<session>/ out of
    $HOME/.claude/projects/ into dest/<slug>/; the count moved.'''
    projects = Path(os.environ['HOME']) / '.claude' / 'projects'
    if not session or not SESSION_RE.fullmatch(session) or not projects.is_dir():
        return 0
    moved = 0
    for slug in sorted(p for p in projects.iterdir() if p.is_dir()):
        for entry in sorted(slug.iterdir()):
            if entry.name == session or entry.name.startswith(session + '.'):
                (dest / slug.name).mkdir(parents=True, exist_ok=True)
                shutil.move(entry, dest / slug.name / entry.name)
                moved += 1
    return moved


def leftovers(root: Path) -> list[Path]:
    '''Files under root that still hold the string postprocess strips.'''
    key = postprocess.KEY.encode()
    return [p for p in sorted(root.rglob('*')) if p.is_file() and key in p.read_bytes()]


def finish(rid: str, results: Path, outcome: dict) -> str:
    '''Steps 6 to 9; the rep's status line.'''
    found = records(results / 'stream.jsonl')
    session = next((r.get('session_id') for r in found if r.get('type') == 'system' and r.get('subtype') == 'init'),
                   None)
    move_session(session, results / 'project')
    result = next((r for r in reversed(found) if r.get('type') == 'result'), None)
    if result is not None:
        (results / 'result.json').write_text(json.dumps(result, indent=1, ensure_ascii=False) + '\n',
                                             encoding='utf-8')
    postprocess.strip_tree(results)
    strip_ok = not leftovers(results)
    (results / 'status.json').write_text(json.dumps(outcome | {'strip_ok': strip_ok}, indent=1) + '\n',
                                         encoding='utf-8')
    homes = common.k_dir() / 'homes'
    homes.mkdir(parents=True, exist_ok=True)
    shutil.move(common.R / rid, homes / rid)
    if outcome['interrupted']:
        state = 'interrupted'
    elif outcome['timed_out']:
        state = 'timeout'
    elif result is None:
        state = f"exit {outcome['exit']}, no result"
    else:
        state = 'ok' if outcome['exit'] == 0 and not result.get('is_error') else f"exit {outcome['exit']}, error"
    cost = result.get('total_cost_usd') if result else None
    money = f'${cost:.2f}' if isinstance(cost, int | float) else 'none'
    return f"{rid}: {state}, cost {money}, {outcome['seconds']:.0f} s" + ('' if strip_ok else ', void (V6)')


def run_rep(rid: str, rep: dict) -> None:
    '''Steps 4 to 9 for one rep, and its status line. Nothing under
    results/<rid>/ exists until the folder is built, so a setup error leaves
    the rep to run again.'''
    _, timeout = limits(rid)
    text = prompt(rid, rep)
    argv, env = command(rid)
    work = build_folder(rid, rep)
    results = common.k_dir() / 'results' / rid
    results.mkdir(parents=True)
    outcome = {'exit': None, 'timed_out': False, 'interrupted': False, 'seconds': 0.0}
    started = time.monotonic()
    try:
        outcome['exit'], outcome['timed_out'] = launch(argv, env, work, text, timeout, results)
    except BaseException:
        outcome['interrupted'] = True
        raise
    finally:
        outcome['seconds'] = round(time.monotonic() - started, 1)
        print(finish(rid, results, outcome), flush=True)


def run_batch(batch: str) -> None:
    path = common.k_dir() / 'batches' / f'{batch}.txt'
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*', batch) or not path.exists():
        raise Stop(EXIT_SETUP, f'no batch {batch}; run build.py first')
    rids = [line.strip() for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    results = common.k_dir() / 'results'
    for i, rid in enumerate(rids):
        if (results / rid).exists():
            print(f'{rid}: skipped, it has results')
            continue
        rep = rep_of(rid)
        check_root()
        check_binary()
        cap, _ = limits(rid)
        so_far, limit = spent(), ceiling()
        if so_far + cap > limit:
            print(f'{rid}: held: spend ${so_far:.2f} plus its cap ${cap} exceeds the ceiling ${limit:.2f}')
            for later in rids[i + 1:]:
                if not (results / later).exists():
                    print(f'{later}: held, after {rid}')
            raise Stop(EXIT_HELD, 'held at the ceiling; raising it is the owner\'s call')
        run_rep(rid, rep)


def exit_on_sigterm(signum, frame) -> None:
    '''SIGTERM's default ends the process at once, so no finally block would
    stop the rep's group or clear R. Raising SystemExit lets them run.'''
    raise SystemExit(128 + signum)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print('usage: run.py <batch>', file=sys.stderr)
        return EXIT_SETUP
    previous = signal.signal(signal.SIGTERM, exit_on_sigterm)
    try:
        run_batch(argv[0])
    except Stop as stop:
        print(f'run.py: {stop}', file=sys.stderr)
        return stop.code
    finally:
        if previous is not None:
            signal.signal(signal.SIGTERM, previous)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
