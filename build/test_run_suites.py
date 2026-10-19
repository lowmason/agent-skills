'''Tests for run_suites.py, the runner and commit lint for build/suites.toml.

The run tests inject a fake run function, so no test starts uv; the --check tests
build throwaway git repositories.
'''
import subprocess
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


# --- --check: the registry and its coverage ---

COVERED = {
    'build/suites.toml': FIXTURE,
    'skills/alpha/scripts/test_a.py': '',
    'tools/test_t.py': '',
    'tools/inner/test_i.py': '',
}


def git_repo(root, files):
    '''Write files under root and git-init it, so `git ls-files --others` lists them.'''
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    subprocess.run(['git', 'init', '-q'], cwd=root, env=rs.git_env(), check=True)
    return root


def findings(root):
    return rs.check(root, tomllib.loads((root / 'build' / 'suites.toml').read_text()))


def test_check_passes_when_every_test_directory_is_registered(tmp_path):
    assert findings(git_repo(tmp_path, COVERED)) == []


def test_check_flags_a_test_directory_outside_every_suite(tmp_path):
    root = git_repo(tmp_path, {**COVERED, 'skills/beta/scripts/test_b.py': ''})
    assert findings(root) == [
        'skills/beta/scripts: holds pytest files, but no suite in build/suites.toml contains it']


def test_check_knows_both_pytest_file_patterns(tmp_path):
    root = git_repo(tmp_path, {**COVERED, 'misc/smoke_test.py': '', 'misc/helper.py': '',
                               'docs/test_notes.md': ''})
    assert findings(root) == ['misc: holds pytest files, but no suite in build/suites.toml contains it']


def test_check_flags_a_registered_directory_that_is_missing(tmp_path):
    files = {rel: text for rel, text in COVERED.items() if not rel.startswith('skills/alpha/')}
    assert findings(git_repo(tmp_path, files)) == [
        'build/suites.toml: alpha: skills/alpha/scripts is not a directory']


def test_check_flags_a_registered_directory_without_tests(tmp_path):
    files = {rel: text for rel, text in COVERED.items() if not rel.startswith('skills/alpha/')}
    root = git_repo(tmp_path, {**files, 'skills/alpha/scripts/tool.py': ''})
    assert findings(root) == ['build/suites.toml: alpha: skills/alpha/scripts holds no pytest file']


def test_check_ignores_gitignored_trees(tmp_path):
    root = git_repo(tmp_path, {**COVERED, '.gitignore': 'wt/\n', 'wt/skills/beta/test_b.py': ''})
    assert findings(root) == []


def test_check_reports_registry_problems_alone(tmp_path):
    root = git_repo(tmp_path, {**COVERED, 'build/suites.toml': FIXTURE.replace('with', 'wtih', 1),
                               'skills/beta/scripts/test_b.py': ''})
    assert findings(root) == ["build/suites.toml: suite 1 (alpha): unknown key 'wtih'",
                              "build/suites.toml: suite 1 (alpha): missing key 'with'"]


def test_check_flags_suites_out_of_name_order(tmp_path):
    swapped = FIXTURE.replace("name = 'alpha'", "name = 'zulu'")
    root = git_repo(tmp_path, {**COVERED, 'build/suites.toml': swapped})
    assert findings(root) == ["build/suites.toml: suites are not sorted by name: 'outer' comes after 'zulu'"]


def test_check_fails_closed_outside_a_git_repository(tmp_path):
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'suites.toml').write_text(FIXTURE)
    assert findings(tmp_path) == ['build/suites.toml: git ls-files failed, so the test directories are unknown']
