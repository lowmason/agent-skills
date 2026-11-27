'''Tests for run_suites.py, the runner and commit lint for build/suites.toml.

The run tests inject a fake run function, so no test starts uv; the --check tests
build throwaway git repositories.
'''
import os
import subprocess
import sys
import tomllib

import pytest

import run_suites as rs
import versions
from git_listing import git_env, kept_paths

V = versions.load()   # the dev interpreter and the cutoff come from the file, never from a literal here
DEV = V.dev_python
PINS = rs.Pins(python=DEV, cutoff=V.cutoff, packages={'polars': '9.9.9'})
VERSIONS_TOML = '''\
[python]
dev = '3.13'
[freeze]
date = 2026-10-19
[packages]
polars = '9.9.9'
[gates]
snippets = ['polars']
'''

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
pythons = ['dev', '/usr/bin/python3']
'''


@pytest.fixture(autouse=True)
def isolated_git(tmp_path, monkeypatch):
    '''Keep every git call below tmp_path, and read no user or system git config or default
    excludes file ($XDG_CONFIG_HOME/git/ignore, else $HOME/.config/git/ignore).'''
    monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path.parent))
    monkeypatch.setenv('GIT_CONFIG_GLOBAL', os.devnull)
    monkeypatch.setenv('GIT_CONFIG_NOSYSTEM', '1')
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'no-xdg'))


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
    (ONE + "with = ['pytest', '--index-url=x']\n", "suite 1 (a): 'with' entries must not start with '-'"),
    (ONE + "with = ['pytest']\nextras = ['-e.']\n", "suite 1 (a): 'extras' entries must not start with '-'"),
    (ONE + "with = ['pytest']\npythons = ['-p']\n", "suite 1 (a): 'pythons' entries must not start with '-'"),
    ("suite = 'x'\n", 'no [[suite]] tables'),
    ('suite = [1]\n', 'suite 1: not a table'),
    ("[[suite]]\nname = 'a'\ndir = '/abs'\nwith = ['pytest']\n",
     "suite 1 (a): 'dir' must be a normalised path below the repo root"),
    ("[[suite]]\nname = 1\ndir = 'x'\nwith = ['pytest']\n", "suite 1: 'name' must be a non-empty string"),
    ("[[suite]]\nname = 'a'\ndir = 1\nwith = ['pytest']\n", "suite 1 (a): 'dir' must be a non-empty string"),
    (ONE + "with = ['pytest']\nextras = [1]\n", "suite 1 (a): 'extras' must be a list of non-empty strings"),
    (ONE + "with = ['pytest']\npythons = [1]\n", "suite 1 (a): 'pythons' must be a list of non-empty strings"),
])
def test_validate_refuses(text, problem):
    assert problem in problems(text)


def test_a_default_run_has_the_form_claude_md_used():
    [run] = rs.runs(fixture_suites()[0], PINS)
    assert run.label == f'alpha ({DEV})'
    assert run.argv == ('uv', 'run', '--python', DEV, '--exclude-newer', V.cutoff, '--with', 'pytest',
                        '--with', 'polars==9.9.9', 'python', '-m', 'pytest', '-q')
    assert run.shell() == (f'cd skills/alpha/scripts && uv run --python {DEV} --exclude-newer {V.cutoff} '
                           '--with pytest --with polars==9.9.9 python -m pytest -q')


def test_extras_and_pytest_args_follow_the_deps_and_are_quoted():
    [run] = rs.runs(fixture_suites()[0], PINS, extras=True, pytest_args=('-k', 'a and b'))
    assert run.shell() == (f"cd skills/alpha/scripts && uv run --python {DEV} --exclude-newer {V.cutoff} "
                           "--with pytest --with polars==9.9.9 --with 'arviz>=1.0' python -m pytest -q -k 'a and b'")


def test_each_python_gets_its_own_run_in_order():
    first, second = rs.runs(fixture_suites()[2], PINS)
    assert (first.python, second.python) == (DEV, '/usr/bin/python3')
    assert second.shell() == (f'cd tools/inner && uv run --python /usr/bin/python3 --exclude-newer {V.cutoff} '
                              '--with pytest python -m pytest -q')


def test_the_dev_entry_follows_the_python_override_and_no_other_entry_does():
    first, second = rs.runs(fixture_suites()[2], rs.Pins(python='3.99', cutoff=None))
    assert (first.python, second.python) == ('3.99', '/usr/bin/python3')


def test_a_pins_object_without_a_cutoff_leaves_out_exclude_newer():
    [run] = rs.runs(fixture_suites()[0], rs.Pins(python=DEV, cutoff=None, packages={}))
    assert '--exclude-newer' not in run.argv
    assert run.argv == ('uv', 'run', '--python', DEV, '--with', 'pytest', '--with', 'polars',
                        'python', '-m', 'pytest', '-q')


def test_pins_pin_only_the_packages_the_file_names():
    assert PINS.spec('polars') == 'polars==9.9.9'
    assert PINS.spec('Polars>=1.0') == 'Polars==9.9.9'
    assert PINS.spec('pytest') == 'pytest'
    assert PINS.spec('arviz>=1.0') == 'arviz>=1.0'


def test_pins_from_versions_read_the_file_and_take_the_options():
    assert rs.Pins.from_versions(V) == rs.Pins(DEV, V.cutoff, V.pins())
    custom = rs.Pins.from_versions(V, python='3.99', freeze=False, user_pins={'numpy': '0.1'})
    assert (custom.python, custom.cutoff) == ('3.99', None) and custom.packages['numpy'] == '0.1'


def test_container_is_the_suite_whose_directory_holds_this_one():
    alpha, outer, inner = suites = fixture_suites()
    assert rs.container(inner, suites) == outer
    assert rs.container(outer, suites) is None
    assert rs.container(alpha, suites) is None


def test_container_compares_path_parts_not_string_prefixes():
    build = rs.Suite('build', 'build', ('pytest',))
    other = rs.Suite('other', 'build_extra', ('pytest',))
    assert rs.container(other, [build, other]) is None


def test_all_runs_an_inner_suite_the_outer_one_skips():
    outer = rs.Suite('outer', 'tools', ('pytest',))
    inner = rs.Suite('tools-build', 'tools/build', ('pytest',))
    assert rs.container(inner, [outer, inner]) is None


def test_norecurse_is_pytests_default(request):
    assert set(rs.NORECURSE) == set(request.config.getini('norecursedirs'))


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
    subprocess.run(['git', 'init', '-q'], cwd=root, env=git_env(), check=True)
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


def test_check_ignores_a_tracked_test_file_deleted_from_the_working_tree(tmp_path):
    root = git_repo(tmp_path, {**COVERED, 'skills/beta/scripts/test_b.py': ''})
    subprocess.run(['git', 'add', '.'], cwd=root, env=git_env(), check=True)
    (root / 'skills' / 'beta' / 'scripts' / 'test_b.py').unlink()
    assert findings(root) == []


def test_the_git_isolation_hides_the_users_default_excludes(tmp_path, monkeypatch):
    home = tmp_path / 'home'
    (home / '.config' / 'git').mkdir(parents=True)
    (home / '.config' / 'git' / 'ignore').write_text('build/\n')
    monkeypatch.setenv('HOME', str(home))   # git reads $HOME/.config/git/ignore only while XDG_CONFIG_HOME is unset or empty
    root = git_repo(tmp_path / 'repo', {'build/test_b.py': ''})
    assert kept_paths(root) == ['build/test_b.py']


def test_check_skips_a_tracked_file_deleted_from_the_work_tree(tmp_path):
    files = {rel: text for rel, text in COVERED.items() if not rel.startswith('skills/alpha/')}
    root = git_repo(tmp_path, {**files, 'skills/alpha/scripts/test_a.py': ''})
    git = ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.com']
    subprocess.run([*git, 'add', '.'], cwd=root, env=git_env(), check=True)
    subprocess.run([*git, 'commit', '-q', '-m', 'seed'], cwd=root, env=git_env(), check=True)
    (root / 'skills' / 'alpha' / 'scripts' / 'test_a.py').unlink()
    (root / 'skills' / 'alpha' / 'scripts' / 'tool.py').write_text('')
    assert findings(root) == ['build/suites.toml: alpha: skills/alpha/scripts holds no pytest file']


def test_check_ignores_archived_skills(tmp_path):
    root = git_repo(tmp_path, {**COVERED, 'archive/skills/beta/scripts/test_b.py': ''})
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


def test_check_flags_a_test_directory_that_pytest_skips(tmp_path):
    root = git_repo(tmp_path, {**COVERED, 'skills/alpha/scripts/build/test_y.py': ''})
    assert findings(root) == ["skills/alpha/scripts/build: holds pytest files, but pytest skips 'build' "
                              'below skills/alpha/scripts, so no suite collects it']


def one_suite_registry(*dirs):
    return ''.join(f"[[suite]]\nname = 's{i}'\ndir = '{d}'\nwith = ['pytest']\n\n" for i, d in enumerate(dirs))


@pytest.mark.parametrize('rel, part, below', [
    ('skills/alpha/scripts/build/deep/test_y.py', 'build', 'skills/alpha/scripts'),
    ('skills/alpha/scripts/.hidden/test_y.py', '.hidden', 'skills/alpha/scripts'),
    ('skills/alpha/scripts/pkg.egg/test_y.py', 'pkg.egg', 'skills/alpha/scripts'),
])
def test_check_flags_a_skipped_part_that_is_not_last_or_matches_a_pattern(tmp_path, rel, part, below):
    root = git_repo(tmp_path, {**COVERED, rel: ''})
    assert findings(root) == [f'{rel.rsplit("/", 1)[0]}: holds pytest files, but pytest skips {part!r} '
                              f'below {below}, so no suite collects it']


def test_a_directory_is_covered_when_one_of_its_suites_does_not_skip_it(tmp_path):
    registry = one_suite_registry('tools', 'tools/build')
    root = git_repo(tmp_path, {'build/suites.toml': registry, 'tools/build/x/test_y.py': ''})
    assert findings(root) == []


def test_a_skipped_directory_is_reported_with_its_deepest_suite(tmp_path):
    registry = one_suite_registry('tools', 'tools/.hid/inner')
    root = git_repo(tmp_path, {'build/suites.toml': registry, 'tools/test_t.py': '',
                               'tools/.hid/inner/test_i.py': '', 'tools/.hid/inner/build/test_y.py': ''})
    assert findings(root) == ["tools/.hid/inner/build: holds pytest files, but pytest skips 'build' "
                              'below tools/.hid/inner, so no suite collects it']


def test_a_suite_dir_named_like_a_skipped_folder_is_collected(tmp_path):
    registry = "[[suite]]\nname = 'build'\ndir = 'build'\nwith = ['pytest']\n"
    root = git_repo(tmp_path, {'build/suites.toml': registry, 'build/test_b.py': ''})
    assert findings(root) == []


def test_check_fails_closed_outside_a_git_repository(tmp_path, monkeypatch):
    monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path.parent))
    monkeypatch.setenv('LC_ALL', 'C')
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'suites.toml').write_text(FIXTURE)
    [finding] = findings(tmp_path)
    assert finding.startswith('build/suites.toml: git ls-files failed (')
    assert 'not a git repository' in finding
    assert finding.endswith('), so the test directories are unknown')


# --- the command line ---

class FakeRuns:
    '''Records each run's label and returns its exit code (0 unless given).'''

    def __init__(self, codes=None):
        self.codes = codes or {}
        self.labels = []
        self.argvs = []

    def __call__(self, root, run):
        self.labels.append(run.label)
        self.argvs.append(run.argv)
        return self.codes.get(run.label, 0)


@pytest.fixture
def repo(tmp_path):
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'suites.toml').write_text(FIXTURE)
    (tmp_path / 'build' / 'versions.toml').write_text(VERSIONS_TOML)
    return tmp_path


def test_a_named_suite_runs_once_per_python(repo, capsys):
    fake = FakeRuns()
    assert rs.main(['tools-inner'], root=repo, run_one=fake, pins=PINS) == 0
    assert fake.labels == [f'tools-inner ({DEV})', 'tools-inner (/usr/bin/python3)']
    assert capsys.readouterr().out.splitlines()[-1] == 'suite runs passed'


def test_a_failed_run_does_not_stop_the_next(repo, capsys):
    fake = FakeRuns({f'tools-inner ({DEV})': 1})
    assert rs.main(['tools-inner', 'alpha'], root=repo, run_one=fake, pins=PINS) == 1
    assert fake.labels == [f'tools-inner ({DEV})', 'tools-inner (/usr/bin/python3)', f'alpha ({DEV})']
    assert capsys.readouterr().err.splitlines()[-1] == f'suite runs failed: tools-inner ({DEV})'


def test_no_tests_collected_counts_as_a_failure(repo):
    assert rs.main(['alpha'], root=repo, run_one=FakeRuns({f'alpha ({DEV})': 5}), pins=PINS) == 1


def test_the_notes_follow_the_first_header(repo, capsys):
    rs.main(['alpha'], root=repo, run_one=FakeRuns(), pins=PINS)
    assert capsys.readouterr().out.splitlines()[:2] == [f'== alpha ({DEV})', 'note: Reads a pilot wiki, else skips.']


class PrintingRuns(FakeRuns):
    def __call__(self, root, run):
        print(f'run {run.label}')
        return super().__call__(root, run)


def test_notes_print_once_after_the_first_header_and_before_the_run(repo, capsys):
    (repo / 'build' / 'suites.toml').write_text(
        "[[suite]]\nname = 'alpha'\ndir = 'x'\nwith = ['pytest']\n"
        "pythons = ['dev', '/usr/bin/python3']\nnotes = ['n1']\n")
    rs.main(['alpha'], root=repo, run_one=PrintingRuns(), pins=PINS)
    assert capsys.readouterr().out.splitlines() == [
        f'== alpha ({DEV})', 'note: n1', f'run alpha ({DEV})',
        '== alpha (/usr/bin/python3)', 'run alpha (/usr/bin/python3)', 'suite runs passed']


def test_extras_and_pytest_args_reach_the_run(repo):
    fake = FakeRuns()
    rs.main(['alpha', '--extras', '--', '-k', 'x'], root=repo, run_one=fake, pins=PINS)
    assert fake.argvs == [('uv', 'run', '--python', DEV, '--exclude-newer', V.cutoff, '--with', 'pytest',
                           '--with', 'polars==9.9.9', '--with', 'arviz>=1.0', 'python', '-m', 'pytest', '-q',
                           '-k', 'x')]


def test_an_option_between_suite_names_applies_to_all(repo):
    fake = FakeRuns()
    assert rs.main(['alpha', '--extras', 'outer'], root=repo, run_one=fake, pins=PINS) == 0
    assert fake.labels == [f'alpha ({DEV})', f'outer ({DEV})']
    assert '--with' in fake.argvs[0] and 'arviz>=1.0' in fake.argvs[0]


def test_the_options_build_the_pins_from_the_repos_file(repo):
    fake = FakeRuns()
    args = ['alpha', '--pin', 'polars==8.8.8', '--python', '3.99', '--no-freeze']
    assert rs.main(args, root=repo, run_one=fake) == 0
    assert fake.argvs == [('uv', 'run', '--python', '3.99', '--with', 'pytest', '--with', 'polars==8.8.8',
                           'python', '-m', 'pytest', '-q')]


def test_a_pin_the_file_does_not_name_exits_2(repo, capsys):
    assert rs.main(['alpha', '--pin', 'zeta==1.0'], root=repo, run_one=FakeRuns()) == 2
    assert 'zeta has no [packages] entry' in capsys.readouterr().err


def test_a_missing_versions_file_exits_2(repo, capsys):
    (repo / 'build' / 'versions.toml').unlink()
    assert rs.main(['alpha'], root=repo, run_one=FakeRuns()) == 2
    assert 'build/versions.toml: cannot read' in capsys.readouterr().err


def test_check_takes_no_pin_options(repo, capsys):
    for option in (['--pin', 'polars==1.0'], ['--python', DEV], ['--no-freeze']):
        with pytest.raises(SystemExit) as err:
            rs.main(['--check', *option], root=repo)
        assert err.value.code == 2
        assert '--check takes no' in capsys.readouterr().err   # not argparse's "unrecognized arguments"


def test_all_skips_a_suite_inside_another(repo, capsys):
    fake = FakeRuns()
    assert rs.main(['--all'], root=repo, run_one=fake, pins=PINS) == 0
    assert fake.labels == [f'alpha ({DEV})', f'outer ({DEV})']
    assert 'skip tools-inner: the outer suite collects tools/inner' in capsys.readouterr().out


def test_list_prints_commands_extras_and_notes_and_runs_nothing(repo, capsys):
    fake = FakeRuns()
    assert rs.main(['--list', 'alpha'], root=repo, run_one=fake, pins=PINS) == 0
    assert fake.labels == []
    assert capsys.readouterr().out.splitlines() == [
        'alpha: skills/alpha/scripts',
        f'  cd skills/alpha/scripts && uv run --python {DEV} --exclude-newer {V.cutoff} --with pytest '
        '--with polars==9.9.9 python -m pytest -q',
        '  extras: arviz>=1.0',
        '  note: Reads a pilot wiki, else skips.',
    ]


def test_list_with_extras_shows_the_extras_deps(repo, capsys):
    rs.main(['--list', 'alpha', '--extras'], root=repo, run_one=FakeRuns(), pins=PINS)
    assert ('  cd skills/alpha/scripts && uv run --python ' + DEV + f' --exclude-newer {V.cutoff} --with pytest '
            "--with polars==9.9.9 --with 'arviz>=1.0' python -m pytest -q") in capsys.readouterr().out.splitlines()


def test_list_with_pytest_args_appends_them(repo, capsys):
    rs.main(['--list', 'outer', '--', '-k', 'a and b'], root=repo, run_one=FakeRuns(), pins=PINS)
    assert capsys.readouterr().out.splitlines() == [
        'outer: tools',
        f"  cd tools && uv run --python {DEV} --exclude-newer {V.cutoff} --with pytest python -m pytest -q "
        "-k 'a and b'"]


def test_list_with_no_names_lists_every_suite_in_file_order(repo, capsys):
    rs.main(['--list'], root=repo, run_one=FakeRuns(), pins=PINS)
    heads = [line for line in capsys.readouterr().out.splitlines() if not line.startswith('  ')]
    assert heads == ['alpha: skills/alpha/scripts', 'outer: tools', 'tools-inner: tools/inner']


def test_an_unknown_suite_exits_2(repo, capsys):
    assert rs.main(['nope'], root=repo, run_one=FakeRuns()) == 2
    assert 'unknown suite: nope' in capsys.readouterr().err


def test_an_invalid_registry_stops_a_run_with_exit_2(repo, capsys):
    (repo / 'build' / 'suites.toml').write_text(FIXTURE.replace('with', 'wtih', 1))
    fake = FakeRuns()
    assert rs.main(['outer'], root=repo, run_one=fake) == 2
    assert fake.labels == []
    assert "build/suites.toml: suite 1 (alpha): unknown key 'wtih'" in capsys.readouterr().err


def test_a_missing_registry_exits_2_for_a_run_and_1_for_check(tmp_path):
    assert rs.main(['alpha'], root=tmp_path, run_one=FakeRuns()) == 2
    assert rs.main(['--check'], root=tmp_path) == 1


@pytest.mark.parametrize('argv', [
    [], ['--', '-x'], ['--check', 'alpha'], ['--check', '--extras'], ['--check', '--', '-x'],
    ['--all', 'alpha'], ['--list', '--all'],
])
def test_usage_errors_exit_2(repo, argv):
    with pytest.raises(SystemExit) as stop:
        rs.main(argv, root=repo, run_one=FakeRuns())
    assert stop.value.code == 2


def test_check_mode_prints_ok_and_exits_0(tmp_path, capsys):
    assert rs.main(['--check'], root=git_repo(tmp_path, COVERED)) == 0
    assert capsys.readouterr().out == 'suite registry ok\n'


def test_check_mode_prints_each_finding_and_exits_1(tmp_path, capsys):
    root = git_repo(tmp_path, {**COVERED, 'skills/beta/scripts/test_b.py': ''})
    assert rs.main(['--check'], root=root) == 1
    assert capsys.readouterr().out == (
        'skills/beta/scripts: holds pytest files, but no suite in build/suites.toml contains it\n')


def test_a_run_that_cannot_start_fails(tmp_path, capsys):
    [run] = rs.runs(rs.Suite('ghost', 'missing', ('pytest',)), PINS)
    assert rs.run_subprocess(tmp_path, run) == 1
    assert f'ghost ({DEV}): cannot start' in capsys.readouterr().err


def test_run_subprocess_runs_in_the_suite_dir_with_this_environment(tmp_path, monkeypatch, capfd):
    (tmp_path / 'sub').mkdir()
    monkeypatch.setenv('LANE3_PROBE', 'seen')
    code = "import os, sys; print(os.getcwd()); print(os.environ['LANE3_PROBE']); sys.exit(3)"
    run = rs.Run(rs.Suite('probe', 'sub', ('pytest',)), DEV, (sys.executable, '-c', code))
    assert rs.run_subprocess(tmp_path, run) == 3
    assert capfd.readouterr().out.splitlines() == [str((tmp_path / 'sub').resolve()), 'seen']


def test_a_malformed_registry_exits_2_for_a_run_and_1_for_check(repo, capsys):
    (repo / 'build' / 'suites.toml').write_text('name = [')
    assert rs.main(['alpha'], root=repo, run_one=FakeRuns()) == 2
    assert 'build/suites.toml: cannot read' in capsys.readouterr().err
    assert rs.main(['--check'], root=repo) == 1
    assert 'build/suites.toml: cannot read' in capsys.readouterr().err


# --- the real registry ---

def test_the_real_registry_passes_check():
    data = tomllib.loads((rs.REPO / rs.REGISTRY).read_text(encoding='utf-8'))
    assert rs.check(rs.REPO, data) == []
