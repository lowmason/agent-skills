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

Exit status: 0 on success; 1 when a check, a gate or a sync comparison fails; 2 for a usage error, an
invalid versions file or a network or resolve failure (the message names the cause).
Design: specs/package-versions.md.
'''
import argparse
import datetime
import re
import subprocess
import sys
import tomllib
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


def bump(root: Path, date: datetime.date, only: Iterable[str] = (),
         resolver: Callable[..., dict[str, str]] | None = None) -> list[str]:
    '''Move the freeze date and re-pin [packages] by one joint resolve; the changed lines.'''
    resolver = resolver or resolve
    v = load(root)
    moved = replace(v, freeze=date)
    resolved = resolver(requirements(v, only), v.dev_python, moved.cutoff)
    missing = [name for name in v.packages if normalize(name) not in resolved]
    if missing:
        raise VersionsError(f'resolve step: the joint resolve did not return {", ".join(missing)}')
    new = {name: resolved[normalize(name)] for name in v.packages}
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


SUBCOMMANDS = {
    'sync': (add_sync, cmd_sync),
    'bump': (add_bump, cmd_bump),
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
