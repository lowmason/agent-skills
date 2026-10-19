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
Design: specs/test-suite-registry.md.
'''
import shlex
from collections.abc import Sequence
from dataclasses import dataclass
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
