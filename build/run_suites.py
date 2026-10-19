'''Run the repo's directory-scoped pytest suites from their registry, build/suites.toml.

Each suite runs pytest from its own directory through uv, with its own inline deps;
the root CLAUDE.md says why. From any directory in the repo:

    uv run --python 3.13 python build/run_suites.py --list [NAME ...]
    uv run --python 3.13 python build/run_suites.py NAME [NAME ...] [--extras] [-- PYTEST_ARGS]
    uv run --python 3.13 python build/run_suites.py --all [--extras] [-- PYTEST_ARGS]
    uv run --python 3.13 python build/run_suites.py --check

--list prints each suite's exact shell commands, its extras and its notes; --extras and
the arguments after -- apply there too. A run prints its suite's notes after its first
header and keeps going after a failure. --all skips a suite whose directory lies inside
another suite's, since pytest collects it there. --check is a commit lint: it validates
the registry and fails when a directory that holds pytest files lies inside no
registered suite directory.

Exit status: 0 when everything passes; 1 when a run fails or --check finds a problem;
2 for a usage error, an unknown suite name or an invalid registry.
Design: specs/completed/test-suite-registry.md.
'''
import argparse
import os
import shlex
import subprocess
import sys
import tomllib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parent.parent
REGISTRY = 'build/suites.toml'  # relative to the repo root
DEFAULT_PYTHONS = ('3.13',)
TEST_FILE_PATTERNS = ('test_*.py', '*_test.py')  # pytest's default python_files
REQUIRED_KEYS = ('name', 'dir', 'with')
OPTIONAL_KEYS = ('extras', 'pythons', 'notes')
STRING_KEYS = ('name', 'dir')
LIST_KEYS = ('with', 'extras', 'pythons', 'notes')


@dataclass(frozen=True)
class Suite:
    name: str
    dir: str
    deps: tuple[str, ...]  # the registry's `with` list
    extras: tuple[str, ...] = ()
    pythons: tuple[str, ...] = DEFAULT_PYTHONS
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Run:
    '''One interpreter's pytest run of one suite.'''
    suite: Suite
    python: str
    argv: tuple[str, ...]

    @property
    def label(self) -> str:
        return f'{self.suite.name} ({self.python})'

    def shell(self) -> str:
        '''The run as one shell line, in the form the root CLAUDE.md used.'''
        return f'cd {shlex.quote(self.suite.dir)} && {shlex.join(self.argv)}'


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) and v for v in value)


def _dir_problem(value: str) -> str | None:
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value or value == '.':
        return "'dir' must be a normalised path below the repo root"
    return None


def validate(data: dict) -> list[str]:
    '''Every problem that keeps the registry from being used; empty when it is valid.'''
    problems = [f'unknown top-level key {key!r}' for key in data if key != 'suite']
    tables = data.get('suite')
    if not isinstance(tables, list) or not tables:
        return [*problems, 'no [[suite]] tables']
    names: set[str] = set()
    dirs: set[str] = set()
    for i, table in enumerate(tables, start=1):
        if not isinstance(table, dict):
            problems.append(f'suite {i}: not a table')
            continue
        name = table.get('name')
        where = f'suite {i} ({name})' if isinstance(name, str) and name else f'suite {i}'
        problems += [f'{where}: unknown key {key!r}' for key in table
                     if key not in REQUIRED_KEYS + OPTIONAL_KEYS]
        problems += [f'{where}: missing key {key!r}' for key in REQUIRED_KEYS if key not in table]
        problems += [f'{where}: {key!r} must be a non-empty string' for key in STRING_KEYS
                     if key in table and not (isinstance(table[key], str) and table[key])]
        problems += [f'{where}: {key!r} must be a list of non-empty strings' for key in LIST_KEYS
                     if key in table and not _is_string_list(table[key])]
        if _is_string_list(table.get('with')) and 'pytest' not in table['with']:
            problems.append(f"{where}: 'with' must include 'pytest'")
        if table.get('pythons') == []:
            problems.append(f"{where}: 'pythons' must not be empty")
        if isinstance(name, str) and name:
            if name in names:
                problems.append(f'{where}: duplicate name')
            names.add(name)
        dir_ = table.get('dir')
        if isinstance(dir_, str) and dir_:
            if problem := _dir_problem(dir_):
                problems.append(f'{where}: {problem}')
            if dir_ in dirs:
                problems.append(f'{where}: duplicate dir {dir_!r}')
            dirs.add(dir_)
    return problems


def parse(data: dict) -> list[Suite]:
    '''The suites of a registry that validate() passes, in file order.'''
    return [Suite(name=t['name'], dir=t['dir'], deps=tuple(t['with']),
                  extras=tuple(t.get('extras', ())),
                  pythons=tuple(t.get('pythons', DEFAULT_PYTHONS)),
                  notes=tuple(t.get('notes', ())))
            for t in data['suite']]


def runs(suite: Suite, extras: bool = False, pytest_args: Sequence[str] = ()) -> list[Run]:
    '''One run per interpreter, in the suite's order; --extras adds the extras.'''
    deps = suite.deps + (suite.extras if extras else ())
    withs = tuple(word for dep in deps for word in ('--with', dep))
    return [Run(suite, python, ('uv', 'run', '--python', python, *withs,
                                'python', '-m', 'pytest', '-q', *pytest_args))
            for python in suite.pythons]


def container(suite: Suite, suites: Sequence[Suite]) -> Suite | None:
    '''The other suite whose directory holds this suite's directory, if any.'''
    path = PurePosixPath(suite.dir)
    return next((other for other in suites
                 if other.dir != suite.dir and path.is_relative_to(other.dir)), None)


def git_env() -> dict[str, str]:
    '''os.environ without git's repo-local variables, as check_conformance.git_env:
    a hook may export GIT_DIR or GIT_INDEX_FILE for another repository.'''
    local = subprocess.run(['git', 'rev-parse', '--local-env-vars'],
                           capture_output=True, text=True, check=True).stdout.split()
    return {name: value for name, value in os.environ.items() if name not in local}


def pytest_dirs(root: Path) -> set[str] | None:
    '''The directories that hold a pytest file, among the files git keeps under root
    (tracked, or untracked and not ignored); None when git fails.'''
    try:
        listing = subprocess.run(
            ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
            cwd=root, env=git_env(), capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    paths = [os.fsdecode(entry) for entry in listing.split(b'\0') if entry]
    # --cached also lists tracked files deleted from the working tree.
    return {str(PurePosixPath(p).parent) for p in paths
            if any(fnmatchcase(PurePosixPath(p).name, pattern) for pattern in TEST_FILE_PATTERNS)
            and (root / p).is_file()}


def check(root: Path, data: dict) -> list[str]:
    '''The --check findings: the registry's problems, then any test directory that
    no registered suite directory contains.'''
    problems = [f'{REGISTRY}: {p}' for p in validate(data)]
    if problems:
        return problems
    suites = parse(data)
    names = [s.name for s in suites]
    problems += [f'{REGISTRY}: suites are not sorted by name: {b!r} comes after {a!r}'
                 for a, b in zip(names, names[1:]) if a > b][:1]
    found = pytest_dirs(root)
    if found is None:
        return [*problems, f'{REGISTRY}: git ls-files failed, so the test directories are unknown']
    for suite in suites:
        if not (root / suite.dir).is_dir():
            problems.append(f'{REGISTRY}: {suite.name}: {suite.dir} is not a directory')
        elif not any(PurePosixPath(d).is_relative_to(suite.dir) for d in found):
            problems.append(f'{REGISTRY}: {suite.name}: {suite.dir} holds no pytest file')
    problems += [f'{d}: holds pytest files, but no suite in {REGISTRY} contains it'
                 for d in sorted(found)
                 if not any(PurePosixPath(d).is_relative_to(s.dir) for s in suites)]
    return problems


RunOne = Callable[[Path, Run], int]


def run_subprocess(root: Path, run: Run) -> int:
    '''Start one run in its suite's directory, with this process's environment.'''
    try:
        return subprocess.run(run.argv, cwd=root / run.suite.dir).returncode
    except OSError as exc:
        print(f'{run.label}: cannot start: {exc}', file=sys.stderr, flush=True)
        return 1


def execute(root: Path, suites: Sequence[Suite], extras: bool, pytest_args: Sequence[str],
            run_one: RunOne) -> int:
    '''Every run of every suite, in order; a failure does not stop the next run.'''
    failed: list[str] = []
    for suite in suites:
        for i, run in enumerate(runs(suite, extras, pytest_args)):
            print(f'== {run.label}', flush=True)
            if i == 0:
                for note in suite.notes:
                    print(f'note: {note}', flush=True)
            if run_one(root, run) != 0:
                failed.append(run.label)
    if failed:
        print(f'suite runs failed: {", ".join(failed)}', file=sys.stderr)
        return 1
    print('suite runs passed')
    return 0


def list_suites(suites: Sequence[Suite], extras: bool, pytest_args: Sequence[str]) -> None:
    for suite in suites:
        print(f'{suite.name}: {suite.dir}')
        for run in runs(suite, extras, pytest_args):
            print(f'  {run.shell()}')
        if suite.extras:
            print(f'  extras: {" ".join(suite.extras)}')
        for note in suite.notes:
            print(f'  note: {note}')


def parse_args(argv: list[str]) -> tuple[argparse.Namespace, tuple[str, ...]]:
    '''The options, and the pytest arguments that follow a `--`.'''
    pytest_args: tuple[str, ...] = ()
    if '--' in argv:
        cut = argv.index('--')
        argv, pytest_args = argv[:cut], tuple(argv[cut + 1:])
    parser = argparse.ArgumentParser(
        prog='run_suites.py', epilog='Arguments after -- go to pytest in every run.',
        description="Run the repo's pytest suites from build/suites.toml.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--list', action='store_true',
                      help="print each suite's commands, extras and notes; runs nothing")
    mode.add_argument('--all', action='store_true',
                      help="run every suite, except one inside another suite's directory")
    mode.add_argument('--check', action='store_true',
                      help='validate the registry and its coverage (a commit lint)')
    parser.add_argument('--extras', action='store_true',
                        help='add the deps that unlock skips')
    parser.add_argument('names', nargs='*', metavar='NAME', help='a suite to run or list')
    args = parser.parse_args(argv)
    if args.check and (args.names or args.extras or pytest_args):
        parser.error('--check takes no suite names, --extras or pytest arguments')
    if args.all and args.names:
        parser.error('--all takes no suite names')
    if not (args.list or args.all or args.check or args.names):
        parser.error('name a suite, or use --list, --all or --check')
    return args, pytest_args


def main(argv: Sequence[str] | None = None, root: Path = REPO,
         run_one: RunOne = run_subprocess) -> int:
    args, pytest_args = parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        data = tomllib.loads((root / REGISTRY).read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f'{REGISTRY}: cannot read: {exc}', file=sys.stderr)
        return 1 if args.check else 2
    if args.check:
        problems = check(root, data)
        for problem in problems:
            print(problem)
        if problems:
            return 1
        print('suite registry ok')
        return 0
    problems = validate(data)
    if problems:
        for problem in problems:
            print(f'{REGISTRY}: {problem}', file=sys.stderr)
        return 2
    suites = parse(data)
    by_name = {suite.name: suite for suite in suites}
    unknown = [name for name in args.names if name not in by_name]
    if unknown:
        print(f'unknown suite: {", ".join(unknown)} (--list names them all)', file=sys.stderr)
        return 2
    chosen = [by_name[name] for name in args.names] or suites
    if args.list:
        list_suites(chosen, args.extras, pytest_args)
        return 0
    if args.all:
        chosen = []
        for suite in suites:
            if outer := container(suite, suites):
                print(f'skip {suite.name}: the {outer.name} suite collects {suite.dir}')
            else:
                chosen.append(suite)
    return execute(root, chosen, args.extras, pytest_args, run_one)


if __name__ == '__main__':
    sys.exit(main())
