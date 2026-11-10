<tests>
import ast
import copy
import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

import build.run_suites as runner
import build.test_commit_lints as commit_lint_tests


ROOT = runner.REPO

FIXTURE = """
[[suite]]
name = "build"
dir = "build"
with = ["pytest", "numpy"]
extras = ["arviz>=1.0"]
notes = ["fixture note"]

[[suite]]
name = "cc-guide"
dir = "build/cc_guide"
with = ["pytest"]

[[suite]]
name = "hooks"
dir = "hooks"
with = ["pytest"]
pythons = ["3.13", "/usr/bin/python3"]
notes = ["hook note"]
"""

EXPECTED = {
    "bayesian-workflow": ("skills/bayesian-workflow/scripts", ["pytest", "arviz", "arviz-stats", "numpy", "xarray"], ["matplotlib"], ["3.13"]),
    "brainstorming": ("skills/brainstorming/scripts", ["pytest"], [], ["3.13"]),
    "build": ("build", ["pytest", "numpy", "polars", "pyyaml"], ["arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots", "numpyro", "jax", "matplotlib"], ["3.13"]),
    "cc-guide": ("build/cc_guide", ["pytest"], [], ["3.13"]),
    "classification-codes": ("skills/classification-codes/scripts", ["pytest", "polars"], [], ["3.13"]),
    "describe-critique-methodology": ("skills/describe-critique-methodology/scripts", ["pytest"], [], ["3.13"]),
    "design-architecture": ("skills/design-architecture/scripts", ["pytest"], [], ["3.13"]),
    "explore-data": ("skills/explore-data/scripts", ["pytest", "polars"], [], ["3.13"]),
    "geographic-codes": ("skills/geographic-codes/scripts", ["pytest", "polars", "fastexcel"], [], ["3.13"]),
    "hooks": ("hooks", ["pytest"], [], ["3.13", "/usr/bin/python3"]),
    "llm-wiki": ("skills/llm-wiki/scripts", ["pytest"], [], ["3.13"]),
    "recommend-probabilistic-model": ("skills/recommend-probabilistic-model/scripts", ["pytest", "numpy", "polars"], [], ["3.13"]),
    "recommend-visualization": ("skills/recommend-visualization/scripts", ["pytest", "numpy", "polars"], [], ["3.13"]),
    "subagent-driven-development": ("skills/subagent-driven-development/scripts", ["pytest"], [], ["3.13"]),
    "systematic-debugging": ("skills/systematic-debugging", ["pytest"], [], ["3.13"]),
    "track-model-experiments": ("skills/track-model-experiments/scripts", ["pytest", "numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"], [], ["3.13"]),
    "tune-hyperparameters": ("skills/tune-hyperparameters/scripts", ["pytest", "numpy", "polars"], ["scikit-learn", "optuna"], ["3.13"]),
    "writing-plans": ("skills/writing-plans/scripts", ["pytest"], [], ["3.13"]),
}


def entry(name="build", directory="build", deps=("pytest",), **optional):
    return {"name": name, "dir": directory, "with": list(deps), **optional}


def fixture_root(root, text=FIXTURE):
    registry = root / "build" / "suites.toml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(text)
    if text == FIXTURE:
        for suite in runner.parse(tomllib.loads(FIXTURE)):
            (root / suite.dir).mkdir(parents=True, exist_ok=True)
    return root


def git_root(root):
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / "build").mkdir()
    (root / "build" / "test_build.py").write_text("def test_build(): pass\n")
    return root


def notes_for(records, name):
    return "\n".join(next(record for record in records if record["name"] == name).get("notes", []))


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_imports_only_stdlib():
    tree = ast.parse((ROOT / "build" / "run_suites.py").read_text())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= sys.stdlib_module_names | {"__future__"}


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
def test_validation_rejects_every_named_defect():
    base = entry()
    invalid = [
        {"suite": [{**base, "wit": ["pytest"]}]},
        {"suite": [{key: value for key, value in base.items() if key != "name"}]},
        {"suite": [{key: value for key, value in base.items() if key != "dir"}]},
        {"suite": [{key: value for key, value in base.items() if key != "with"}]},
        {"suite": [{**base, "name": 3}]},
        {"suite": [{**base, "dir": 3}]},
        {"suite": [{**base, "with": "pytest"}]},
        {"suite": [{**base, "with": ["pytest", 3]}]},
        {"suite": [{**base, "extras": "numpy"}]},
        {"suite": [{**base, "pythons": [3]}]},
        {"suite": [{**base, "notes": [3]}]},
        {"suite": [base, entry(name="build", directory="hooks")]},
        {"suite": [base, entry(name="hooks", directory="build")]},
        {"suite": [{**base, "with": ["numpy"]}]},
    ]
    for data in invalid:
        assert runner.validate(copy.deepcopy(data)), data


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_run_argv():
    suite = runner.Suite("build", "build", ("pytest", "numpy"))
    run, = runner.runs(suite)
    assert run.argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy",
        "python", "-m", "pytest", "-q",
    )


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_and_quoting():
    suite = runner.Suite("spaced", "suite dir", ("pytest",))
    run, = runner.runs(suite, pytest_args=("test case.py", "-k", "a or b"))
    assert run.shell() == (
        "cd 'suite dir' && uv run --python 3.13 --with pytest "
        "python -m pytest -q 'test case.py' -k 'a or b'"
    )


# spec: "`--extras` adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_follow_default_deps():
    suite = runner.Suite("build", "build", ("pytest", "numpy"), extras=("arviz>=1.0",))
    run, = runner.runs(suite, extras=True)
    assert run.argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy", "--with", "arviz>=1.0",
        "python", "-m", "pytest", "-q",
    )
    assert shlex.quote("arviz>=1.0") in run.shell()


# spec: "Arguments after `--` go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 2
def test_pytest_arguments_reach_every_interpreter():
    suite = runner.Suite(
        "hooks", "hooks", ("pytest",),
        pythons=("3.13", "/usr/bin/python3"),
    )
    actual = runner.runs(suite, pytest_args=("test_hook.py::test_one", "-k", "focus", "-s", "-rs"))
    assert len(actual) == 2
    for run in actual:
        assert run.argv[-5:] == ("test_hook.py::test_one", "-k", "focus", "-s", "-rs")


# spec: "`--all` runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_uses_directory_boundaries():
    outer = runner.Suite("build", "build", ("pytest",))
    nested = runner.Suite("cc-guide", "build/cc_guide", ("pytest",))
    sibling = runner.Suite("builder", "builder", ("pytest",))
    assert runner.container(nested, [outer, nested, sibling]) == outer
    assert runner.container(sibling, [outer, nested, sibling]) is None


# spec: "The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root."
# task: 3
def test_git_file_listing_includes_untracked_pytest_directories(tmp_path):
    root = git_root(tmp_path / "repo")
    test_file = root / "skills" / "new" / "scripts" / "test_new.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_new(): pass\n")
    assert "skills/new/scripts" in runner.pytest_dirs(root)


# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_check_covers_both_pytest_filename_patterns(tmp_path):
    root = git_root(tmp_path / "repo")
    for directory, filename in (("first", "test_new.py"), ("second", "new_test.py")):
        folder = root / directory
        folder.mkdir()
        (folder / filename).write_text("def test_new(): pass\n")
    findings = runner.check(root, {"suite": [entry()]})
    assert "first: holds pytest files, but no suite in build/suites.toml contains it" in findings
    assert "second: holds pytest files, but no suite in build/suites.toml contains it" in findings


# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_registered_parent_covers_nested_pytest_files(tmp_path):
    root = git_root(tmp_path / "repo")
    nested = root / "build" / "cc_guide"
    nested.mkdir()
    (nested / "test_guide.py").write_text("def test_guide(): pass\n")
    assert runner.check(root, {"suite": [entry()]}) == []


# spec: "registry: R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_reports_missing_registered_directory(tmp_path):
    root = git_root(tmp_path / "repo")
    data = {"suite": [entry(), entry("missing", "skills/missing/scripts")]}
    assert any("skills/missing/scripts" in finding for finding in runner.check(root, data))


# spec: "registry: R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_reports_registered_directory_without_tests(tmp_path):
    root = git_root(tmp_path / "repo")
    empty = root / "hooks"
    empty.mkdir()
    (empty / "notes.txt").write_text("no tests here\n")
    data = {"suite": [entry(), entry("hooks", "hooks")]}
    assert any("hooks" in finding for finding in runner.check(root, data))


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_check_ignores_git_ignored_trees(tmp_path):
    root = git_root(tmp_path / "repo")
    (root / ".gitignore").write_text(".claude/worktrees/\nbuild/.scratch/\n")
    for relative in (
        ".claude/worktrees/one/test_hidden.py",
        "build/.scratch/test_hidden.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_hidden(): pass\n")
    assert runner.check(root, {"suite": [entry()]}) == []


# spec: "If git fails, `--check` fails."
# task: 3
def test_check_fails_outside_a_git_repo(tmp_path):
    root = tmp_path / "not-a-repo"
    root.mkdir()
    fixture_root(root, FIXTURE)
    assert runner.main(["--check"], root=root) == 1


# spec: "Each registry problem starts `build/suites.toml: `; an uncovered directory reads `<dir>: holds pytest files, but no suite in build/suites.toml contains it`."
# task: 3
def test_registry_validation_findings_have_registry_prefix(tmp_path):
    root = git_root(tmp_path / "repo")
    bad = {"suite": [{**entry(), "unknown": True}]}
    assert all(
        finding.startswith("build/suites.toml: ")
        for finding in runner.check(root, bad)
    )


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_prints_one_line_for_one_finding(tmp_path, capsys):
    root = git_root(tmp_path / "repo")
    fixture_root(root, '[[suite]]\nname = "build"\ndir = "build"\nwith = ["pytest"]\n')
    new = root / "skills" / "new" / "scripts" / "test_new.py"
    new.parent.mkdir(parents=True)
    new.write_text("def test_new(): pass\n")
    assert runner.main(["--check"], root=root) == 1
    output = capsys.readouterr()
    assert (output.out + output.err).strip().splitlines() == [
        "skills/new/scripts: holds pytest files, but no suite in build/suites.toml contains it"
    ]


# spec: "`--list [NAME …]` prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_prints_all_fixture_details(tmp_path, capsys):
    root = fixture_root(tmp_path)
    assert runner.main(["--list"], root=root) == 0
    output = capsys.readouterr().out
    for name, directory in (
        ("build", "build"),
        ("cc-guide", "build/cc_guide"),
        ("hooks", "hooks"),
    ):
        assert name in output
        assert directory in output
    assert "cd build && uv run --python 3.13 --with pytest --with numpy python -m pytest -q" in output
    assert "arviz>=1.0" in output
    assert "fixture note" in output
    assert "cd hooks && uv run --python /usr/bin/python3 --with pytest python -m pytest -q" in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_applies_extras_and_pytest_arguments(tmp_path, capsys):
    root = fixture_root(tmp_path)
    assert runner.main(["--list", "build", "--extras", "--", "-k", "focus"], root=root) == 0
    output = capsys.readouterr().out
    assert "cd build && uv run --python 3.13 --with pytest --with numpy --with 'arviz>=1.0' python -m pytest -q -k focus" in output
    assert "cd hooks &&" not in output


# spec: "`NAME [NAME …]` runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_suites_run_in_requested_interpreter_order(tmp_path):
    root = fixture_root(tmp_path)
    called = []

    def fake_run(root_path, run):
        called.append(run.label)
        return 0

    assert runner.main(["hooks", "build"], root=root, run_one=fake_run) == 0
    assert called == ["hooks (3.13)", "hooks (/usr/bin/python3)", "build (3.13)"]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_notes_print_once_after_first_header_and_before_output(tmp_path, capsys):
    root = fixture_root(tmp_path)

    def fake_run(root_path, run):
        print("pytest output")
        return 0

    assert runner.main(["hooks"], root=root, run_one=fake_run) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines.index("== hooks (3.13)") < lines.index("note: hook note") < lines.index("pytest output")
    assert lines.count("note: hook note") == 1
    assert "== hooks (/usr/bin/python3)" in lines


# spec: "A failed run does not stop the next one."
# task: 4
def test_failure_does_not_stop_later_runs(tmp_path, capsys):
    root = fixture_root(tmp_path)
    called = []

    def fake_run(root_path, run):
        called.append(run.label)
        return 5 if len(called) == 1 else 0

    assert runner.main(["hooks", "build"], root=root, run_one=fake_run) == 1
    assert called == ["hooks (3.13)", "hooks (/usr/bin/python3)", "build (3.13)"]
    assert "hooks (3.13)" in capsys.readouterr().err.splitlines()[-1]


# spec: "Exit status: 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_exit_codes_for_success_unknown_name_and_exit_five(tmp_path):
    root = fixture_root(tmp_path)
    assert runner.main(["build"], root=root, run_one=lambda *_: 0) == 0
    assert runner.main(["build"], root=root, run_one=lambda *_: 5) == 1
    assert runner.main(["unknown"], root=root, run_one=lambda *_: 0) == 2


# spec: "Exit status: 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_invalid_cli_usage_exits_two():
    with pytest.raises(SystemExit) as error:
        runner.parse_args(["--not-an-option"])
    assert error.value.code == 2


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_invalid_registry_stops_all_running_modes(tmp_path):
    bad = FIXTURE.replace('name = "build"', 'name = "build"\nunknown = true', 1)
    root = fixture_root(tmp_path, bad)
    called = []

    def fake_run(root_path, run):
        called.append(run)
        return 0

    for args in (["--list"], ["build"], ["--all"]):
        assert runner.main(args, root=root, run_one=fake_run) == 2
    assert called == []


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 4
def test_check_reports_invalid_registry_as_exit_one(tmp_path, capsys):
    root = git_root(tmp_path / "repo")
    bad = '[[suite]]\nname = "build"\ndir = "build"\nwith = ["pytest"]\nunknown = true\n'
    fixture_root(root, bad)
    assert runner.main(["--check"], root=root) == 1
    assert "build/suites.toml: " in (capsys.readouterr().out + capsys.readouterr().err)


# spec: "`--all` prints one line for each suite that it skips."
# task: 4
def test_all_skips_nested_suite_and_prints_its_skip(tmp_path, capsys):
    root = fixture_root(tmp_path)
    called = []

    def fake_run(root_path, run):
        called.append(run.label)
        return 0

    assert runner.main(["--all"], root=root, run_one=fake_run) == 0
    assert called == ["build (3.13)", "hooks (3.13)", "hooks (/usr/bin/python3)"]
    assert sum("skip cc-guide:" in line for line in capsys.readouterr().out.splitlines()) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_named_nested_suite_runs(tmp_path):
    root = fixture_root(tmp_path)
    called = []

    def fake_run(root_path, run):
        called.append(run.label)
        return 0

    assert runner.main(["cc-guide"], root=root, run_one=fake_run) == 0
    assert called == ["cc-guide (3.13)"]


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_counts_as_failed_run(tmp_path, monkeypatch):
    root = fixture_root(tmp_path / "repo")
    empty_path = tmp_path / "empty-bin"
    empty_path.mkdir()
    monkeypatch.setenv("PATH", str(empty_path))
    assert runner.main(["build"], root=root, run_one=runner.run_subprocess) == 1


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_inherits_environment_and_uses_suite_directory(tmp_path, monkeypatch):
    root = fixture_root(tmp_path / "repo")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    capture = tmp_path / "capture.txt"
    fake_uv = bin_dir / "uv"
    fake_uv.write_text(
        f"#!{sys.executable}\n"
        "import os\n"
        "from pathlib import Path\n"
        "Path(os.environ['RUN_CAPTURE']).write_text(os.getcwd() + '\\n' + os.environ['RUN_MARKER'])\n"
    )
    fake_uv.chmod(0o755)
    monkeypatch.setenv("RUN_CAPTURE", str(capture))
    monkeypatch.setenv("RUN_MARKER", "kept")
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ.get("PATH", ""))
    suite = runner.Suite("build", "build", ("pytest",))
    run, = runner.runs(suite)
    assert runner.run_subprocess(root, run) == 0
    assert capture.read_text().splitlines() == [str(root / "build"), "kept"]


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 5
def test_script_finds_repo_when_started_elsewhere(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(ROOT / "build" / "run_suites.py"), "--list", "build"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert "build" in completed.stdout


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_has_exact_inventory_in_name_order():
    records = tomllib.loads((ROOT / "build" / "suites.toml").read_text())["suite"]
    names = [record["name"] for record in records]
    assert names == sorted(EXPECTED)
    assert len(names) == len(set(names))
    for record in records:
        directory, deps, extras, pythons = EXPECTED[record["name"]]
        assert record["dir"] == directory
        assert record["with"] == deps
        assert record.get("extras", []) == extras
        assert record.get("pythons", ["3.13"]) == pythons


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_describes_keys_order_and_lint():
    text = (ROOT / "build" / "suites.toml").read_text()
    header = text.split("[[suite]]", 1)[0].lower()
    assert header.strip().startswith("#")
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert key in header
    assert "sort" in header
    assert "lint" in header
    assert "ninth" in header or "9th" in header


# spec: "The notes carry the rest of each comment."
# task: 5
def test_registry_notes_retain_named_operational_details():
    records = tomllib.loads((ROOT / "build" / "suites.toml").read_text())["suite"]
    assert "build/.scratch/" in notes_for(records, "build")
    bayesian = notes_for(records, "bayesian-workflow")
    assert "CALIBRATION_SWEEP=1" in bayesian
    assert "arviz" in bayesian.lower()
    assert "node" in notes_for(records, "brainstorming").lower()
    wiki = notes_for(records, "llm-wiki")
    assert "@needs_pilot" in wiki
    assert "LLM_WIKI_ROOT" in wiki
    assert "--with sklearn" in notes_for(records, "tune-hyperparameters")
    assert re.search(r"\d|time|slow", notes_for(records, "track-model-experiments"), re.I)
    hooks = notes_for(records, "hooks").lower()
    assert "3.9" in hooks
    assert "launchd" in hooks
    assert "gate b" in hooks


# spec: "`build/test_run_suites.py`, stdlib and pytest only, which the build suite collects."
# task: 5
def test_runner_test_module_uses_only_stdlib_pytest_and_runner():
    path = ROOT / "build" / "test_run_suites.py"
    tree = ast.parse(path.read_text())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= sys.stdlib_module_names | {"__future__", "pytest", "run_suites", "build"}


# spec: "the real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_passes_check(capsys):
    assert runner.main(["--check"], root=ROOT) == 0
    assert "suite registry ok" in capsys.readouterr().out


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_commit_lint_script_has_ninth_registry_check():
    text = (ROOT / "build" / "run_commit_lints.sh").read_text()
    lines = text.splitlines()
    run_lines = [line.strip() for line in lines if line.strip().startswith("run ")]
    assert len(run_lines) == 9
    assert run_lines[-1] == "run suite_registry uv run --python 3.13 python build/run_suites.py --check"
    assert "nine" in text.lower()


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_test_registers_the_new_case():
    assert "suite_registry" in str(commit_lint_tests.CHECKS)
    assert hasattr(commit_lint_tests, "test_unregistered_suite_is_refused")


# spec: "`build/CLAUDE.md`: "the eight commit lints" becomes "the nine commit lints", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_guide_names_ninth_lint_and_runner():
    text = (ROOT / "build" / "CLAUDE.md").read_text()
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    assert any(
        "suites.toml" in line
        and "run_suites.py" in line
        and "--check" in line
        and "commit lint" in line
        for line in text.splitlines()
    )


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_guide_intro_keeps_runner_context():
    lines = (ROOT / "CLAUDE.md").read_text().splitlines()
    intro = [line for line in lines if "build/suites.toml" in line and "build/run_suites.py" in line]
    assert len(intro) == 1
    line = intro[0]
    for token in ("uv", "3.13", "director", "test_build.py", "note"):
        assert token in line.lower()


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_guide_has_all_four_runner_commands():
    text = (ROOT / "CLAUDE.md").read_text()
    command_lines = [
        line.strip()
        for line in text.splitlines()
        if "uv run --python 3.13 python build/run_suites.py " in line
    ]
    assert any("--list" in line for line in command_lines)
    assert any("<name>" in line and "--extras" in line and "<pytest args>" in line for line in command_lines)
    assert any(line.endswith("--all") for line in command_lines)
    assert any(line.endswith("--check") for line in command_lines)


# spec: "These commands stay literal in `CLAUDE.md`."
# task: 7
def test_root_guide_retains_selected_commands_and_tools():
    text = (ROOT / "CLAUDE.md").read_text()
    for marker in (
        "test_runtime_support.py",
        "test_commit_lints.py",
        "-k declared_dependencies",
        "-k test_real_skill",
        "test_check_jax_examples.py",
        "Single test",
        "verify_citations.py",
        "extract_structure.py",
        "cli.py lint",
        "cli.py check",
    ):
        assert marker in text


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_guide_removes_directory_suite_commands_and_stays_short():
    lines = (ROOT / "CLAUDE.md").read_text().splitlines()
    assert len(lines) < 200
    suites = runner.parse(tomllib.loads((ROOT / "build" / "suites.toml").read_text()))
    for suite in suites:
        for run in runner.runs(suite):
            assert not any(
                line.strip() == run.shell() or line.strip().startswith(run.shell() + " &&")
                for line in lines
            )


# spec: "The comment names the suite `run_suites.py cc-guide` instead of "its suite"."
# task: 7
def test_cc_guide_comment_names_runner_suite():
    text = (ROOT / "CLAUDE.md").read_text()
    assert any("run_suites.py cc-guide" in line for line in text.splitlines())


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_checks_first_line_stamp():
    first_line = (ROOT / "CLAUDE.md").read_text().splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .*@[^\s]+ -->", first_line)
    source = (ROOT / "build" / "test_check_conformance.py").read_text()
    tree = ast.parse(source)
    function = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    function_source = ast.get_source_segment(source, function)
    assert "cc-guide:" in function_source
    assert "@needs_pilot" not in function_source


# spec: "`bash build/run_commit_lints.sh` prints `commit lints passed`."
# task: 6
def test_commit_lint_gate_passes():
    completed = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "commit lints passed" in completed.stdout + completed.stderr
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`.</plan></flag>
<flag task="5"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>`cc_guide`</plan></flag>
</flags>
<untestable>
On `main` at `456e3fb` there are 18: the 17 in `CLAUDE.md` lines 66–125, and `build/cc_guide`, whose command is line 145.
The entries carry the text of today's commands and comments.
Every command, dependency and note survives; the only change is the form.
With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character.
`build/run_commit_lints.sh` keeps its literal commands.
Line 133 is not touched (plan 53's Task 7 edits it).
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
Write each test before its code and see it fail first (red, then green).
Under decision 2, plan 52's Task 6 drops its `CLAUDE.md:commands-moved` and `CLAUDE.md:commands` edits and adds one `[[suite]]` entry for `skills/write-with-asd-ste100/scripts` instead.
Its expectations of 199 and 197 lines (Task 1, DF19, Q4, Coupling (e)) change with it.
Its `CLAUDE.md:sources` and `CLAUDE.md:bullet` edits are outside the Commands block and still apply.
A note in the session group's shared notes folder gives the exact entry.
If plan 52 lands first after all, R5.2's deletion still works, and this plan registers that suite itself.
None of the lines that R5.1 deletes carries one of its edit anchors.
Its Task 7 edits line 133, which stays.
Its own suite commands are written out in full in the plan, so they work without `CLAUDE.md`.
It edits one sentence of `build/CLAUDE.md`'s `cc_guide/` paragraph.
If an edit block does not match, merge by hand.
Run it before the `CLAUDE.md` deletion.
It extracts every `cd <dir> && uv run …` command from lines 66–125 and 145, splitting the hooks `&&` chain into one command per run.
It asserts that the set equals the set of default shell forms that `--list` prints: nothing is missing on either side.
It also checks each comment's skip-unlocking deps against that suite's `extras`.
Run `hooks`, `build` and `bayesian-workflow` once directly and once through the runner, in the same checkout.
Their pytest summary lines match.
Then run `--all` once, and record each run's result beside the direct result.
R6's tests run red first, then green.
The build suite passes (where the missing `build/.scratch/` lets it).
`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`.
The Stage 2 audit passes, and the behaviour runs match.
The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
</untestable>