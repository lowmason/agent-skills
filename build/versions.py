'''One source for every pinned or cited package version, the dev interpreter and the freeze date.

build/versions.toml is the only file where a person sets one of them. This script reads it:

    uv run python build/versions.py sync [--check]
    uv run python build/versions.py run GATE [--pin PKG==X ...] -- COMMAND ...
    uv run python build/versions.py verify [--pin PKG==X ...]
    uv run python build/versions.py bump [--date YYYY-MM-DD] [--only PKG ...]
    uv run python build/versions.py drift [--pin PKG==X ...]
    uv run python build/versions.py check

sync writes .python-version, uv.toml and skills/uv.toml, and --check fails when one differs.
run installs a gate's pinned stack and runs COMMAND under uv with the freeze date. verify runs the
re-verify set. bump moves the freeze date and re-pins [packages] by one joint resolve. drift does the
same resolve with no freeze date and reports it. check is the offline commit lint.
--python and --no-freeze on run and verify exist for drift's second pass.

Exit status: 0 on success; 1 when a check, a gate or a sync comparison fails, and when `check` cannot
load the versions file (it reports the load error as a finding); 2 for a usage error, an invalid
versions file in any other subcommand, or a network or resolve failure (the message names the cause).
Design: specs/completed/package-versions.md.
'''
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tomllib
import urllib.request
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


VERSIONS_FILE = 'build/versions.toml'


VERSION_RE = re.compile(r'\d+(?:\.\d+)*')


PYTHON_RE = re.compile(r'3\.\d+')


OVERRIDE_KEYS = ('gate', 'package', 'version', 'reason')


SYNC_NOTE = '# Written by build/versions.py sync from build/versions.toml. Do not edit.\n'


class VersionsError(Exception):
    '''An invalid or unreadable versions file; the message names the cause.'''


def normalize(name: str) -> str:
    '''PEP 503 form, which is how uv prints a package name.'''
    return re.sub(r'[-_.]+', '-', name).lower()


def version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split('.'))


def compare(a: str, b: str) -> int:
    '''-1, 0 or 1; the shorter version is padded with zeros.'''
    x, y = version_tuple(a), version_tuple(b)
    width = max(len(x), len(y))
    x, y = x + (0,) * (width - len(x)), y + (0,) * (width - len(y))
    return (x > y) - (x < y)


@dataclass(frozen=True)
class Override:
    gate: str
    package: str
    version: str
    reason: str


@dataclass(frozen=True)
class Versions:
    dev_python: str
    freeze: datetime.date
    packages: dict[str, str]
    cited: dict[str, str]
    gates: dict[str, tuple[str, ...]]
    overrides: tuple[Override, ...] = ()

    @property
    def cutoff(self) -> str:
        '''00:00:00Z on the day after the freeze date, so the freeze day itself is included.'''
        return f'{self.freeze + datetime.timedelta(days=1):%Y-%m-%d}T00:00:00Z'

    def stack(self, gate: str, pins: Mapping[str, str] | None = None) -> list[str]:
        '''The `pkg==version` strings of a gate: [packages], then overrides, then --pin values.'''
        if gate not in self.gates:
            raise VersionsError(f'unknown gate {gate!r}; the gates are {", ".join(self.gates)}')
        pins = {normalize(k): v for k, v in (pins or {}).items()}
        out = []
        for package in self.gates[gate]:
            version = self.packages[package]
            for override in self.overrides:
                if override.gate == gate and override.package == package:
                    version = override.version
            out.append(f'{package}=={pins.get(normalize(package), version)}')
        return out

    def pins(self) -> dict[str, str]:
        '''Every [packages] entry, keyed by normalised name; what a suite run installs.'''
        return {normalize(name): version for name, version in self.packages.items()}


def _table(data: dict, key: str, where: str) -> dict:
    value = data.get(key)
    if not isinstance(value, dict):
        raise VersionsError(f'{where}: missing table [{key}]')
    return value


def parse(text: str, where: str = VERSIONS_FILE) -> Versions:
    '''Validate the file's text; every error names its key, package, date or value.'''
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise VersionsError(f'{where}: invalid TOML: {exc}') from exc
    known = {'python', 'freeze', 'packages', 'cited', 'gates', 'override'}
    for key in data:
        if key not in known:
            raise VersionsError(f'{where}: unknown table {key!r}')
    dev = _table(data, 'python', where).get('dev')
    if not isinstance(dev, str) or not PYTHON_RE.fullmatch(dev):
        raise VersionsError(f"{where}: [python] dev must be a string such as '3.13', got {dev!r}")
    date = _table(data, 'freeze', where).get('date')
    if not isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
        raise VersionsError(f'{where}: [freeze] date must be a TOML date such as 2026-10-19, got {date!r}')
    packages = dict(_table(data, 'packages', where))
    cited = dict(_table(data, 'cited', where)) if 'cited' in data else {}
    for table, entries in (('packages', packages), ('cited', cited)):
        for name, version in entries.items():
            if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
                raise VersionsError(f'{where}: [{table}] {name}: invalid version {version!r}')
    for name in packages:
        if normalize(name) in {normalize(c) for c in cited}:
            raise VersionsError(f'{where}: {name} is in both [packages] and [cited]')
    gates = {}
    for gate, members in _table(data, 'gates', where).items():
        if not isinstance(members, list) or not members or not all(isinstance(m, str) for m in members):
            raise VersionsError(f'{where}: [gates] {gate} must be a non-empty list of package names')
        for member in members:
            if member not in packages:
                raise VersionsError(f'{where}: [gates] {gate} names {member}, which has no [packages] entry')
        gates[gate] = tuple(members)
    tables = data.get('override', [])
    if not isinstance(tables, list) or not all(isinstance(table, dict) for table in tables):
        raise VersionsError(f'{where}: override must be written [[override]]')
    overrides = []
    for i, table in enumerate(tables, start=1):
        for key in OVERRIDE_KEYS:
            if not isinstance(table.get(key), str) or not table[key]:
                raise VersionsError(f'{where}: [[override]] {i}: missing key {key!r}')
        if table['gate'] not in gates:
            raise VersionsError(f"{where}: [[override]] {i}: unknown gate {table['gate']!r}")
        if table['package'] not in gates[table['gate']]:
            raise VersionsError(f"{where}: [[override]] {i}: {table['package']} is not in gate {table['gate']}")
        if not VERSION_RE.fullmatch(table['version']):
            raise VersionsError(f"{where}: [[override]] {i}: invalid version {table['version']!r}")
        overrides.append(Override(*(table[key] for key in OVERRIDE_KEYS)))
    return Versions(dev, date, packages, cited, gates, tuple(overrides))


def load(root: Path = REPO) -> Versions:
    path = root / VERSIONS_FILE
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        raise VersionsError(f'{VERSIONS_FILE}: cannot read: {exc}') from exc
    return parse(text)


def rewrite(text: str, date: datetime.date | None = None, packages: Mapping[str, str] | None = None) -> str:
    '''The file's text with the freeze date and [packages] values replaced; comments and order stay.'''
    out, table = [], ''
    for line in text.splitlines(keepends=True):
        header = re.match(r'\s*\[+([^\]]+)\]+', line)
        if header:
            table = header.group(1)
        elif date and table == 'freeze' and re.match(r'\s*date\s*=', line):
            line = re.sub(r'=\s*\S+', f'= {date.isoformat()}', line, count=1)
        elif packages and table == 'packages':
            match = re.match(r"(\s*)([\w.-]+)(\s*=\s*)'[^']*'(.*)$", line, re.S)
            if match and match.group(2) in packages:
                line = f"{match.group(1)}{match.group(2)}{match.group(3)}'{packages[match.group(2)]}'{match.group(4)}"
        out.append(line)
    return ''.join(out)


def outputs(v: Versions) -> dict[str, str]:
    '''The three files `sync` owns, as repo-relative path -> exact text.'''
    return {
        '.python-version': f'{v.dev_python}\n',
        'uv.toml': (f'{SYNC_NOTE}# Every uv run in this repo resolves packages as of this cutoff: 00:00:00Z on the day after\n'
                    f'# the freeze date, {v.freeze.isoformat()}, so files uploaded on the freeze date itself are included.\n'
                    f'exclude-newer = "{v.cutoff}"\n'),
        'skills/uv.toml': (f'{SYNC_NOTE}# No settings. This file stops uv from reading the repo-root uv.toml for scripts under\n'
                           '# skills/, so a skill script that a user runs floats within its own dependency floors.\n'
                           '# The repo\'s checks pass --exclude-newer themselves (build/versions.py run, build/run_suites.py).\n'),
    }


def sync(root: Path, check: bool = False) -> list[str]:
    '''Write the outputs, or with check list the ones that differ.'''
    v = load(root)
    problems = []
    for rel, text in outputs(v).items():
        path = root / rel
        current = path.read_text(encoding='utf-8') if path.is_file() else None
        if current == text:
            continue
        if check:
            problems.append(f'{rel}: {"missing" if current is None else "differs"}; run build/versions.py sync')
        else:
            path.write_text(text, encoding='utf-8')
    return problems


RESOLVED_LINE = re.compile(r'^([A-Za-z0-9][A-Za-z0-9._-]*)==([0-9][^\s;]*)', re.M)


def resolve(requirements: Sequence[str], python_version: str, cutoff: str | None) -> dict[str, str]:
    '''One joint `uv pip compile` of the requirements; {normalised name: version}, transitive ones too.
    With no cutoff it ignores the repo's uv.toml, so it sees the newest releases.'''
    argv = ['uv'] + ([] if cutoff else ['--no-config']) + [
        'pip', 'compile', '-', '--python-version', python_version, '--no-header', '--no-annotate', '--quiet']
    if cutoff:
        argv += ['--exclude-newer', cutoff]
    try:
        done = subprocess.run(argv, input='\n'.join(requirements) + '\n', capture_output=True, text=True)
    except OSError as exc:
        raise VersionsError(f'resolve step: cannot start uv: {exc}') from exc
    if done.returncode != 0:
        raise VersionsError(f'resolve step: joint resolve of {", ".join(requirements)} on Python '
                            f'{python_version} failed:\n{done.stderr.strip()}')
    return {normalize(name): version for name, version in RESOLVED_LINE.findall(done.stdout)}


def requirements(v: Versions, only: Iterable[str] = (), pins: Mapping[str, str] | None = None) -> list[str]:
    '''The joint resolve's input: a bare name where it may move, `name==pin` where it may not.'''
    only = {normalize(name) for name in only}
    unknown = only - {normalize(name) for name in v.packages}
    if unknown:
        raise VersionsError(f'--only names {", ".join(sorted(unknown))}, which has no [packages] entry')
    pins = pins or {}
    out = []
    for name, pin in v.packages.items():
        key = normalize(name)
        if key in pins:
            out.append(f'{name}=={pins[key]}')
        elif only and key not in only:
            out.append(f'{name}=={pin}')
        else:
            out.append(name)
    return out


def resolved_pins(v: Versions, resolved: Mapping[str, str]) -> dict[str, str]:
    '''The joint resolve's version for each [packages] entry, keyed by the name as the file writes it.'''
    missing = [name for name in v.packages if normalize(name) not in resolved]
    if missing:
        raise VersionsError(f'resolve step: the joint resolve did not return {", ".join(missing)}')
    return {name: resolved[normalize(name)] for name in v.packages}


def bump(root: Path, date: datetime.date, only: Iterable[str] = (),
         resolver: Callable[..., dict[str, str]] | None = None) -> list[str]:
    '''Move the freeze date and re-pin [packages] by one joint resolve; the changed lines.'''
    resolver = resolver or resolve
    v = load(root)
    moved = replace(v, freeze=date)
    resolved = resolver(requirements(v, only), v.dev_python, moved.cutoff)
    new = resolved_pins(v, resolved)
    path = root / VERSIONS_FILE
    text = rewrite(path.read_text(encoding='utf-8'), date, new)
    written = parse(text)
    for name, version in new.items():
        if written.packages.get(name) != version:
            raise VersionsError(f'cannot rewrite [packages] {name}; write its value in single quotes')
    if written.freeze != date:
        raise VersionsError('cannot rewrite [freeze] date; write it as date = YYYY-MM-DD under [freeze]')
    path.write_text(text, encoding='utf-8')
    sync(root)
    changes = [f'{name}: {old} -> {new[name]}' for name, old in v.packages.items() if new[name] != old]
    if date != v.freeze:
        changes.insert(0, f'freeze: {v.freeze.isoformat()} -> {date.isoformat()}')
    return changes


RUNNER = 'uv run python build/versions.py run'


Fetch = Callable[[str], dict]


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={'User-Agent': 'agent-skills-versions'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except (OSError, ValueError) as exc:
        raise VersionsError(f'cannot reach {url}: {exc}') from exc


def parse_time(text: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(text.replace('Z', '+00:00'))


def first_upload(urls: Sequence[Mapping], what: str) -> datetime.datetime:
    times = [parse_time(entry['upload_time_iso_8601']) for entry in urls]
    if not times:
        raise VersionsError(f'{what}: PyPI lists no files')
    return min(times)


def late_pins(v: Versions, specs: Iterable[str], fetch: Fetch | None = None) -> list[str]:
    '''The specs whose release was first uploaded at or after the freeze cutoff.'''
    fetch = fetch or fetch_json
    cutoff = parse_time(v.cutoff)
    problems = []
    for spec in specs:
        package, _, version = spec.partition('==')
        uploaded = first_upload(fetch(f'https://pypi.org/pypi/{package}/{version}/json').get('urls', []),
                                spec)
        if uploaded >= cutoff:
            problems.append(f'{package} {version}: uploaded {uploaded:%Y-%m-%d}, after the freeze date '
                            f'{v.freeze.isoformat()}')
    return problems


def parse_pins(v: Versions, specs: Sequence[str]) -> dict[str, str]:
    '''`--pin pkg==X` values as {name: version}; each must name a [packages] entry.'''
    known = {normalize(name) for name in v.packages}
    pins = {}
    for spec in specs:
        name, eq, version = spec.partition('==')
        if not eq or not VERSION_RE.fullmatch(version):
            raise VersionsError(f'--pin {spec!r}: write it as package==version')
        if normalize(name) not in known:
            raise VersionsError(f'--pin {spec!r}: {name} has no [packages] entry')
        pins[normalize(name)] = version
    return pins


def uv_run_argv(v: Versions, gate: str | None, command: Sequence[str], pins: Mapping[str, str] | None = None,
                python: str | None = None, freeze: bool = True) -> list[str]:
    '''`uv run` with the interpreter, the freeze cutoff and the gate's pinned stack, then the command.'''
    argv = ['uv', 'run', '--python', python or v.dev_python]
    if freeze:
        argv += ['--exclude-newer', v.cutoff]
    if gate is not None:
        for spec in v.stack(gate, pins):
            argv += ['--with', spec]
    return argv + list(command)


def runner_command(gate: str, tail: str) -> str:
    '''The documented form of a pinned-stack command.'''
    return f'{RUNNER} {gate} -- {tail}'


def run_process(argv: Sequence[str], root: Path = REPO, env: Mapping[str, str] | None = None) -> int:
    try:
        return subprocess.run(list(argv), cwd=root, env=None if env is None else dict(env)).returncode
    except OSError as exc:
        print(f'cannot start {argv[0]}: {exc}', file=sys.stderr, flush=True)
        return 2


@dataclass(frozen=True)
class Step:
    label: str
    argv: tuple[str, ...]


def verify_steps(v: Versions, pins: Mapping[str, str] | None = None, python: str | None = None,
                 freeze: bool = True, user_pins: Mapping[str, str] | None = None) -> list[Step]:
    '''The re-verify set. `pins` pins the gates' stacks; `user_pins` are the --pin values that the
    suite runner repeats (it reads the rest of its pins from the file).'''
    def gate_step(label: str, gate: str, tail: list[str]) -> Step:
        return Step(label, tuple(uv_run_argv(v, gate, tail, pins, python, freeze)))
    suites = ['python', 'build/run_suites.py', '--all', '--extras']
    for name, version in (user_pins if user_pins is not None else (pins or {})).items():
        suites += ['--pin', f'{name}=={version}']
    if python:
        suites += ['--python', python]
    if not freeze:
        suites.append('--no-freeze')
    return [
        gate_step('tier 2 (--api)', 'snippets',
                  ['python', 'build/check_snippets.py', '--api', 'skills/bayesian-workflow/']),
        gate_step('tier 3 (--run)', 'snippets',
                  ['python', 'build/check_snippets.py', '--run', 'skills/bayesian-workflow/']),
        gate_step('jax cpu examples', 'jax-cpu',
                  ['python', 'build/check_jax_examples.py', 'skills/deep-learning/',
                   'skills/evaluate-deep-learning/', 'skills/optimize-jax/']),
        Step('suites', tuple(uv_run_argv(v, None, suites, None, python, freeze))),
    ]


def run_steps(steps: Sequence[Step], root: Path = REPO, env: Mapping[str, str] | None = None,
              runner: Callable[..., int] = run_process) -> list[str]:
    '''Run every step, in order, whatever fails; the labels of the failed ones.'''
    failed = []
    for step in steps:
        print(f'== {step.label}', flush=True)
        if runner(step.argv, root, env) != 0:
            failed.append(step.label)
    return failed


def newest_stable_python() -> str:
    '''The newest CPython that uv can download, as `3.<minor>`, prereleases and free-threaded builds left out.'''
    try:
        done = subprocess.run(['uv', 'python', 'list', '--only-downloads', '--output-format', 'json'],
                              capture_output=True, text=True)
    except OSError as exc:
        raise VersionsError(f'python step: cannot list the Python releases: {exc}') from exc
    if done.returncode != 0:
        raise VersionsError(f'python step: uv python list failed:\n{done.stderr.strip()}')
    try:
        items = json.loads(done.stdout)
    except ValueError as exc:
        raise VersionsError(f'python step: cannot read the Python release list: {exc}') from exc
    found = [(item['version_parts']['major'], item['version_parts']['minor']) for item in items
             if item.get('implementation') == 'cpython' and item.get('variant') == 'default'
             and re.fullmatch(r'\d+\.\d+\.\d+', item.get('version', ''))]
    if not found:
        raise VersionsError('python step: uv lists no stable CPython release')
    major, minor = max(found)
    return f'{major}.{minor}'


@dataclass(frozen=True)
class Row:
    package: str
    pinned: str
    resolved: str
    newest: str
    uploaded: str
    flag: str


def drift_rows(v: Versions, resolved: Mapping[str, str], fetch: Fetch | None = None) -> list[Row]:
    fetch = fetch or fetch_json
    rows = []
    for table, entries in (('packages', v.packages), ('cited', v.cited)):
        for name, pinned in entries.items():
            data = fetch(f'https://pypi.org/pypi/{name}/json')
            newest = data['info']['version']
            uploaded = f'{first_upload(data.get("urls", []), name):%Y-%m-%d}'
            got = resolved.get(normalize(name), '-') if table == 'packages' else '-'
            flag = ''
            try:
                if table == 'packages' and got != '-' and compare(got, newest) < 0:
                    flag = 'resolves below its newest release'
                elif table == 'cited' and version_tuple(newest)[:len(version_tuple(pinned))] != version_tuple(pinned):
                    flag = 'a newer release exists'
            except ValueError as exc:
                raise VersionsError(f'{name}: cannot compare version {got!r} / {newest!r} with {pinned!r}; '
                                    'a version must be dotted integers') from exc
            rows.append(Row(name, pinned, got, newest, uploaded, flag))
    return rows


def render_pass(python: str, rows: Sequence[Row], results: Sequence[tuple[str, bool]]) -> str:
    lines = [f'## Python {python}', '', '| package | pinned | resolved | newest | uploaded | flag |',
             '|---|---|---|---|---|---|']
    lines += [f'| {r.package} | {r.pinned} | {r.resolved} | {r.newest} | {r.uploaded} | {r.flag} |' for r in rows]
    lines += ['', '| gate | result |', '|---|---|']
    lines += [f'| {label} | {"pass" if ok else "FAIL"} |' for label, ok in results]
    return '\n'.join(lines) + '\n'


DRIFT_LIMIT = ('Limit: `check` and this report see only the package names that build/versions.toml lists. '
               'A package that a skill cites and the file omits is invisible to both.')


def drift(root: Path, user_pins: Mapping[str, str] | None = None, fetch: Fetch | None = None,
          resolver: Callable[..., dict[str, str]] | None = None,
          newest_python: Callable[[], str] | None = None,
          runner: Callable[..., int] | None = None) -> tuple[int, str]:
    '''The drift run: (exit status, report). Status 0 when every gate passes on the newest versions,
    1 when a gate fails, 2 when it cannot resolve or reach the network.'''
    resolver, newest_python, runner = resolver or resolve, newest_python or newest_stable_python, runner or run_process
    v = load(root)
    report = ['# Package drift', '', f'Freeze date {v.freeze.isoformat()}; dev Python {v.dev_python}.', '']
    try:
        newest = newest_python()
        passes = [v.dev_python] + ([newest] if newest != v.dev_python else [])
        failed_any = False
        for python in passes:
            resolved = resolver(requirements(v, pins=user_pins), python, None)
            found = resolved_pins(v, resolved)
            rows = drift_rows(v, resolved, fetch)
            pins = {normalize(name): version for name, version in found.items()}
            steps = verify_steps(v, pins, python=python, freeze=False, user_pins=pins)
            failed = run_steps(steps, root, {**os.environ, 'UV_NO_CONFIG': '1'}, runner)
            failed_any = failed_any or bool(failed)
            report.append(render_pass(python, rows, [(s.label, s.label not in failed) for s in steps]))
    except VersionsError as exc:
        report += ['', f'drift could not finish: {exc}', '', DRIFT_LIMIT]
        return 2, '\n'.join(report) + '\n'
    report += [DRIFT_LIMIT]
    return (1 if failed_any else 0), '\n'.join(report) + '\n'


# ---- command line -----------------------------------------------------------

def add_sync(sub) -> None:
    sub.add_parser('sync', help='write .python-version, uv.toml and skills/uv.toml').add_argument(
        '--check', action='store_true', help='fail when an output differs')


def cmd_sync(args, root: Path, tail: Sequence[str]) -> int:
    problems = sync(root, check=args.check)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def parse_date(text: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f'invalid date {text!r}; write YYYY-MM-DD') from exc


def add_bump(sub) -> None:
    parser = sub.add_parser('bump', help='move the freeze date and re-pin [packages]')
    parser.add_argument('--date', type=parse_date, help='the new freeze date (default: today, UTC)')
    parser.add_argument('--only', nargs='+', default=[], metavar='PKG', help='move only these packages')


def cmd_bump(args, root: Path, tail: Sequence[str]) -> int:
    date = args.date or datetime.datetime.now(datetime.timezone.utc).date()
    for line in bump(root, date, args.only):
        print(line)
    return 0


def add_pin_options(parser: argparse.ArgumentParser, drift_only: bool = False) -> None:
    parser.add_argument('--pin', action='append', default=[], metavar='PKG==X',
                        help='use this version for one run; the file stays as it is')
    if not drift_only:
        parser.add_argument('--python', help="another interpreter, for drift's second pass")
        parser.add_argument('--no-freeze', action='store_true',
                            help='leave out the --exclude-newer flag; the root uv.toml still applies '
                                 'unless UV_NO_CONFIG=1 is set, as drift sets it')


def add_run(sub) -> None:
    parser = sub.add_parser('run', help="run a command under a gate's pinned stack; the command follows --")
    parser.add_argument('gate')
    add_pin_options(parser)


def cmd_run(args, root: Path, tail: Sequence[str]) -> int:
    v = load(root)
    pins = parse_pins(v, args.pin)
    if not args.no_freeze:
        late = late_pins(v, v.stack(args.gate, pins))
        if late:
            print('\n'.join(late), file=sys.stderr)
            return 2
    return run_process(uv_run_argv(v, args.gate, tail, pins, args.python, not args.no_freeze), root)


def add_verify(sub) -> None:
    add_pin_options(sub.add_parser('verify', help="run the re-verify set on the file's versions"))


def cmd_verify(args, root: Path, tail: Sequence[str]) -> int:
    v = load(root)
    pins = parse_pins(v, args.pin)
    if not args.no_freeze:
        late = late_pins(v, sorted({spec for gate in v.gates for spec in v.stack(gate, pins)}))
        if late:
            print('\n'.join(late), file=sys.stderr)
            return 2
    failed = run_steps(verify_steps(v, pins, args.python, not args.no_freeze), root)
    if failed:
        print(f'verify failed: {", ".join(failed)}', file=sys.stderr)
        return 1
    print('verify passed')
    return 0


def add_drift(sub) -> None:
    add_pin_options(sub.add_parser('drift', help='resolve with no freeze date and run the re-verify set'),
                    drift_only=True)


def cmd_drift(args, root: Path, tail: Sequence[str]) -> int:
    status, report = drift(root, parse_pins(load(root), args.pin))
    print(report)
    return status


def add_check(sub) -> None:
    sub.add_parser('check', help='the offline commit lint')


def cmd_check(args, root: Path, tail: Sequence[str]) -> int:
    import versions_check
    problems = versions_check.check(root)
    for problem in problems:
        print(problem)
    print(f'{len(problems)} problem(s)' if problems else 'versions ok')
    return 1 if problems else 0


SUBCOMMANDS = {
    'sync': (add_sync, cmd_sync),
    'bump': (add_bump, cmd_bump),
    'run': (add_run, cmd_run),
    'verify': (add_verify, cmd_verify),
    'drift': (add_drift, cmd_drift),
    'check': (add_check, cmd_check),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='versions.py', description="Read and move the repo's package versions.")
    sub = parser.add_subparsers(dest='command', required=True)
    for add, _ in SUBCOMMANDS.values():
        add(sub)
    return parser


def main(argv: Sequence[str] | None = None, root: Path = REPO) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    tail: list[str] = []
    if '--' in argv:
        cut = argv.index('--')
        argv, tail = argv[:cut], argv[cut + 1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != 'run' and tail:
        parser.error(f'{args.command} takes no command after --')
    if args.command == 'run' and not tail:
        parser.error('run needs a command after --')
    try:
        return SUBCOMMANDS[args.command][1](args, root, tail)
    except VersionsError as exc:
        print(f'{args.command}: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
