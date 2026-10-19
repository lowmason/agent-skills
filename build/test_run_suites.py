'''Tests for run_suites.py, the runner and commit lint for build/suites.toml.

The run tests inject a fake run function, so no test starts uv; the --check tests
build throwaway git repositories.
'''
import tomllib

import pytest

import run_suites as rs

FIXTURE = '''\
[[suite]]
name = 'alpha'
dir = 'skills/alpha/scripts'
with = ['pytest', 'polars']
extras = ['arviz>=1.0']
notes = ['Reads a pilot wiki, else skips.']

[[suite]]
name = 'outer'
dir = 'tools'
with = ['pytest']

[[suite]]
name = 'tools-inner'
dir = 'tools/inner'
with = ['pytest']
pythons = ['3.13', '/usr/bin/python3']
'''
ONE = "[[suite]]\nname = 'a'\ndir = 'x'\n"  # a suite table without its `with` line


def problems(text):
    return rs.validate(tomllib.loads(text))


def fixture_suites():
    return rs.parse(tomllib.loads(FIXTURE))


# --- the registry: validation, runs, nesting ---

def test_the_fixture_registry_is_valid():
    assert problems(FIXTURE) == []


@pytest.mark.parametrize('text, problem', [
    (ONE + "with = ['pytest']\nwtih = ['polars']\n", "suite 1 (a): unknown key 'wtih'"),
    ("[[suite]]\nname = 'a'\nwith = ['pytest']\n", "suite 1 (a): missing key 'dir'"),
    (ONE + "with = 'pytest'\n", "suite 1 (a): 'with' must be a list of non-empty strings"),
    (ONE + "with = ['pytest', '']\n", "suite 1 (a): 'with' must be a list of non-empty strings"),
    (ONE + "with = ['polars']\n", "suite 1 (a): 'with' must include 'pytest'"),
    (ONE + "with = ['pytest']\npythons = []\n", "suite 1 (a): 'pythons' must not be empty"),
    (ONE + "with = ['pytest']\nnotes = 'one note'\n", "suite 1 (a): 'notes' must be a list of non-empty strings"),
    ("[[suite]]\nname = ''\ndir = 'x'\nwith = ['pytest']\n", "suite 1: 'name' must be a non-empty string"),
    ("[[suite]]\nname = 'a'\ndir = '../x'\nwith = ['pytest']\n",
     "suite 1 (a): 'dir' must be a normalised path below the repo root"),
    ("[[suite]]\nname = 'a'\ndir = 'x/'\nwith = ['pytest']\n",
     "suite 1 (a): 'dir' must be a normalised path below the repo root"),
    ("[[suite]]\nname = 'a'\ndir = '.'\nwith = ['pytest']\n",
     "suite 1 (a): 'dir' must be a normalised path below the repo root"),
    (ONE + "with = ['pytest']\n" + ONE.replace('x', 'y') + "with = ['pytest']\n", 'suite 2 (a): duplicate name'),
    (ONE + "with = ['pytest']\n" + ONE.replace("'a'", "'b'") + "with = ['pytest']\n",
     "suite 2 (b): duplicate dir 'x'"),
    ("title = 'suites'\n" + ONE + "with = ['pytest']\n", "unknown top-level key 'title'"),
    ('', 'no [[suite]] tables'),
])
def test_validate_refuses(text, problem):
    assert problem in problems(text)


def test_a_default_run_has_the_form_claude_md_used():
    [run] = rs.runs(fixture_suites()[0])
    assert run.label == 'alpha (3.13)'
    assert run.argv == ('uv', 'run', '--python', '3.13', '--with', 'pytest', '--with', 'polars',
                        'python', '-m', 'pytest', '-q')
    assert run.shell() == ('cd skills/alpha/scripts && uv run --python 3.13 --with pytest '
                           '--with polars python -m pytest -q')


def test_extras_and_pytest_args_follow_the_deps_and_are_quoted():
    [run] = rs.runs(fixture_suites()[0], extras=True, pytest_args=('-k', 'a and b'))
    assert run.shell() == ("cd skills/alpha/scripts && uv run --python 3.13 --with pytest "
                           "--with polars --with 'arviz>=1.0' python -m pytest -q -k 'a and b'")


def test_each_python_gets_its_own_run_in_order():
    first, second = rs.runs(fixture_suites()[2])
    assert (first.python, second.python) == ('3.13', '/usr/bin/python3')
    assert second.shell() == 'cd tools/inner && uv run --python /usr/bin/python3 --with pytest python -m pytest -q'


def test_container_is_the_suite_whose_directory_holds_this_one():
    alpha, outer, inner = suites = fixture_suites()
    assert rs.container(inner, suites) == outer
    assert rs.container(outer, suites) is None
    assert rs.container(alpha, suites) is None


def test_container_compares_path_parts_not_string_prefixes():
    build = rs.Suite('build', 'build', ('pytest',))
    other = rs.Suite('other', 'build_extra', ('pytest',))
    assert rs.container(other, [build, other]) is None
