<tests>
import ast
import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

import build.run_suites as runner


def _table(
    name="alpha",
    directory="skills/alpha/scripts",
    deps=("pytest",),
    extras=None,
    pythons=None,
    notes=None,
):
    table = {"name": name, "dir": directory, "with": list(deps)}
    if extras is not None:
        table["extras"] = list(extras)
    if pythons is not None:
        table["pythons"] = list(pythons)
    if notes is not None:
        table["notes"] = list(notes)
    return table


def _data(*tables):
    return {"suite": list(tables)}


def _write(root, relative, content=""):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def _registry_root(root, *tables):
    lines = []
    for table in tables:
        lines.append("[[suite]]")
        lines.extend(f"{key} = {json.dumps(value)}" for key, value in table.items())
        lines.append("")
    _write(root, "build/suites.toml", "\n".join(lines))
    return root


def _git_init(root):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)


def _covered_repo(root):
    _git_init(root)
    table = _table(name="known", directory="known")
    _registry_root(root, table)
    _write(root, "known/test_known.py")
    return _data(table)


def _suite(**kwargs):
    return runner.parse(_data(_table(**kwargs)))[0]


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_describes_its_contract():
    text = (runner.REPO / "build/suites.toml").read_text()
    header = text.split("[[suite]]", 1)[0].lower()
    assert all(key in header for key in ("name", "dir", "with", "extras", "pythons", "notes"))
    assert "sort" in header
    assert "ninth" in header or "nine" in header


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_has_distinct_sorted_entries():
    data = tomllib.loads((runner.REPO / "build/suites.toml").read_text())
    tables = data["suite"]
    names = [table["name"] for table in tables]
    directories = [table["dir"] for table in tables]
    assert names == sorted(names)
    assert len(names) == len(set(names))
    assert len(directories) == len(set(directories))


# spec: "The entries carry the text of today's commands and comments."
# task: 5
def test_real_registry_preserves_the_specified_inventory():
    data = tomllib.loads((runner.REPO / "build/suites.toml").read_text())
    suites = {suite.name: suite for suite in runner.parse(data)}
    expected = {
        "bayesian-workflow": ("skills/bayesian-workflow/scripts", ("arviz", "arviz-stats", "numpy", "xarray"), ("matplotlib",)),
        "brainstorming": ("skills/brainstorming/scripts", (), ()),
        "build": ("build", ("numpy", "polars", "pyyaml"), ("arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots", "numpyro", "jax", "matplotlib")),
        "cc-guide": ("build/cc_guide", (), ()),
        "classification-codes": ("skills/classification-codes/scripts", ("polars",), ()),
        "describe-critique-methodology": ("skills/describe-critique-methodology/scripts", (), ()),
        "design-architecture": ("skills/design-architecture/scripts", (), ()),
        "explore-data": ("skills/explore-data/scripts", ("polars",), ()),
        "geographic-codes": ("skills/geographic-codes/scripts", ("polars", "fastexcel"), ()),
        "hooks": ("hooks", (), ()),
        "llm-wiki": ("skills/llm-wiki/scripts", (), ()),
        "recommend-probabilistic-model": ("skills/recommend-probabilistic-model/scripts", ("numpy", "polars"), ()),
        "recommend-visualization": ("skills/recommend-visualization/scripts", ("numpy", "polars"), ()),
        "subagent-driven-development": ("skills/subagent-driven-development/scripts", (), ()),
        "systematic-debugging": ("skills/systematic-debugging", (), ()),
        "track-model-experiments": ("skills/track-model-experiments/scripts", ("numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"), ()),
        "tune-hyperparameters": ("skills/tune-hyperparameters/scripts", ("numpy", "polars"), ("scikit-learn", "optuna")),
        "writing-plans": ("skills/writing-plans/scripts", (), ()),
    }
    assert expected.keys() <= suites.keys()
    for name, (directory, dependencies, extras) in expected.items():
        suite = suites[name]
        assert suite.dir == directory
        assert suite.deps == ("pytest", *dependencies)
        assert suite.extras == extras
        assert suite.pythons == (("3.13", "/usr/bin/python3") if name == "hooks" else ("3.13",))


# spec: "The notes carry the rest of each comment."
# task: 5
def test_real_registry_keeps_the_named_operational_notes():
    data = tomllib.loads((runner.REPO / "build/suites.toml").read_text())
    suites = {suite.name: suite for suite in runner.parse(data)}
    required = {
        "bayesian-workflow": ("CALIBRATION_SWEEP=1", "arviz", "warning"),
        "brainstorming": ("node", "skip"),
        "build": ("build/.scratch/",),
        "hooks": ("3.9", "launchd", "Gate B"),
        "llm-wiki": ("@needs_pilot", "LLM_WIKI_ROOT"),
        "tune-hyperparameters": ("sklearn", "fails"),
    }
    for name, phrases in required.items():
        notes = " ".join(suites[name].notes).lower()
        assert all(phrase.lower() in notes for phrase in phrases), name
    assert suites["track-model-experiments"].notes


# spec: "Default `['3.13']`."
# task: 2
def test_parse_uses_python_313_when_pythons_is_absent():
    suite = _suite(deps=("pytest", "numpy"))
    assert suite.pythons == ("3.13",)
    assert suite.deps == ("pytest", "numpy")
    assert suite.extras == ()
    assert suite.notes == ()


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
def test_validate_rejects_every_specified_registry_error():
    cases = []
    cases.append(_data({**_table(), "unexpected": "value"}))
    for key in ("name", "dir", "with"):
        table = _table()
        del table[key]
        cases.append(_data(table))
    for key, value in (
        ("name", 7),
        ("dir", 7),
        ("with", "pytest"),
        ("with", [7]),
        ("extras", "numpy"),
        ("extras", [7]),
        ("pythons", "3.13"),
        ("pythons", [7]),
        ("notes", "note"),
        ("notes", [7]),
    ):
        cases.append(_data({**_table(), key: value}))
    cases.append(_data(_table(deps=("numpy",))))
    cases.append(_data(_table(), _table(directory="other")))
    cases.append(_data(_table(), _table(name="other")))
    for case in cases:
        assert runner.validate(case), case


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_invalid_registry_stops_every_execution_mode(tmp_path):
    _registry_root(tmp_path, {**_table(), "misspelled": "value"})
    for arguments in (["--list"], ["alpha"], ["--all"]):
        assert runner.main(arguments, root=tmp_path, run_one=lambda root, run: 0) == 2


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
def test_check_reports_registry_validation_as_findings(tmp_path):
    _git_init(tmp_path)
    table = {**_table(name="known", directory="known"), "misspelled": "value"}
    _registry_root(tmp_path, table)
    _write(tmp_path, "known/test_known.py")
    findings = runner.check(tmp_path, _data(table))
    assert any(line.startswith("build/suites.toml: ") for line in findings)


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_run_argv_has_the_required_order():
    run = runner.runs(_suite(deps=("pytest", "numpy", "polars")))[0]
    assert run.argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy", "--with", "polars",
        "python", "-m", "pytest", "-q",
    )


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_directory_dependencies_and_arguments():
    suite = _suite(directory="skills/a b/scripts", deps=("pytest", "pkg>=1"))
    run = runner.runs(suite, pytest_args=("case name",))[0]
    assert run.shell() == (
        "cd 'skills/a b/scripts' && uv run --python 3.13 "
        "--with pytest --with 'pkg>=1' python -m pytest -q 'case name'"
    )
    assert run.shell() == f"cd {shlex.quote(suite.dir)} && {shlex.join(run.argv)}"


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 2
def test_hooks_has_two_separate_shell_forms():
    suite = _suite(name="hooks", directory="hooks", pythons=("3.13", "/usr/bin/python3"))
    forms = [run.shell() for run in runner.runs(suite)]
    assert forms == [
        "cd hooks && uv run --python 3.13 --with pytest python -m pytest -q",
        "cd hooks && uv run --python /usr/bin/python3 --with pytest python -m pytest -q",
    ]


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_imports_only_standard_library_modules():
    source = (runner.REPO / "build/run_suites.py").read_text()
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.append(node.module.split(".", 1)[0])
    assert set(imported) <= sys.stdlib_module_names


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 5
def test_cli_finds_the_real_registry_from_another_directory(tmp_path):
    result = subprocess.run(
        [sys.executable, str(runner.REPO / "build/run_suites.py"), "--list", "cc-guide"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert "cc-guide" in result.stdout
    assert "build/cc_guide" in result.stdout


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_prints_every_field_and_defaults_to_all(tmp_path, capsys):
    _registry_root(
        tmp_path,
        _table(name="alpha", directory="skills/alpha/scripts", extras=("numpy",), notes=("needs a fixture",)),
        _table(name="beta", directory="skills/beta/scripts"),
    )
    assert runner.main(["--list"], root=tmp_path) == 0
    output = capsys.readouterr().out
    assert "alpha" in output and "beta" in output
    assert "skills/alpha/scripts" in output
    assert "cd skills/alpha/scripts && uv run --python 3.13 --with pytest python -m pytest -q" in output
    assert "numpy" in output
    assert "needs a fixture" in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_shows_the_command_with_extras_and_pytest_arguments(tmp_path, capsys):
    _registry_root(tmp_path, _table(extras=("numpy",)))
    assert runner.main(["--list", "alpha", "--extras", "--", "-k", "needle"], root=tmp_path) == 0
    output = capsys.readouterr().out
    assert (
        "cd skills/alpha/scripts && uv run --python 3.13 --with pytest "
        "--with numpy python -m pytest -q -k needle"
    ) in output


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_suites_run_in_requested_and_interpreter_order(tmp_path):
    _registry_root(
        tmp_path,
        _table(name="alpha"),
        _table(name="beta", directory="skills/beta/scripts", pythons=("3.13", "/usr/bin/python3")),
    )
    calls = []

    def run_one(root, run):
        calls.append(run.label)
        return 0

    assert runner.main(["beta", "alpha"], root=tmp_path, run_one=run_one) == 0
    assert calls == ["beta (3.13)", "beta (/usr/bin/python3)", "alpha (3.13)"]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_notes_print_once_after_the_first_header(tmp_path, capsys):
    _registry_root(
        tmp_path,
        _table(pythons=("3.13", "/usr/bin/python3"), notes=("first note", "second note")),
    )
    assert runner.main(["alpha"], root=tmp_path, run_one=lambda root, run: 0) == 0
    output = capsys.readouterr().out
    first = output.index("== alpha (3.13)")
    note = output.index("note: first note")
    second = output.index("== alpha (/usr/bin/python3)")
    assert first < note < second
    assert output.count("note: first note") == 1
    assert output.count("note: second note") == 1


# spec: "A failed run does not stop the next one."
# task: 4
def test_failure_does_not_stop_later_runs(tmp_path):
    _registry_root(tmp_path, _table(pythons=("3.13", "/usr/bin/python3")))
    calls = []

    def run_one(root, run):
        calls.append(run.label)
        return 5 if len(calls) == 1 else 0

    assert runner.main(["alpha"], root=tmp_path, run_one=run_one) == 1
    assert calls == ["alpha (3.13)", "alpha (/usr/bin/python3)"]


# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_follow_default_dependencies():
    suite = _suite(deps=("pytest", "numpy"), extras=("matplotlib", "arviz"))
    assert runner.runs(suite)[0].argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy",
        "python", "-m", "pytest", "-q",
    )
    assert runner.runs(suite, extras=True)[0].argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy",
        "--with", "matplotlib", "--with", "arviz",
        "python", "-m", "pytest", "-q",
    )


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_cli_forwards_pytest_arguments_to_every_run(tmp_path):
    _registry_root(tmp_path, _table(pythons=("3.13", "/usr/bin/python3")))
    commands = []

    def run_one(root, run):
        commands.append(run.argv)
        return 0

    assert runner.main(
        ["alpha", "--", "test_one.py::test_case", "-k", "needle", "-s", "-rs"],
        root=tmp_path,
        run_one=run_one,
    ) == 0
    assert len(commands) == 2
    assert all(
        argv[-5:] == ("test_one.py::test_case", "-k", "needle", "-s", "-rs")
        for argv in commands
    )


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_skips_nested_suites_once_but_keeps_path_peers(tmp_path, capsys):
    _registry_root(
        tmp_path,
        _table(name="outer", directory="build"),
        _table(name="inner", directory="build/cc_guide"),
        _table(name="peer", directory="builder"),
    )
    calls = []

    def run_one(root, run):
        calls.append(run.suite.name)
        return 0

    assert runner.main(["--all"], root=tmp_path, run_one=run_one) == 0
    assert set(calls) == {"outer", "peer"}
    output = capsys.readouterr().out
    assert output.count("skip inner: the outer suite collects build/cc_guide") == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_named_nested_suite_runs_even_with_all(tmp_path):
    _registry_root(
        tmp_path,
        _table(name="outer", directory="build"),
        _table(name="inner", directory="build/cc_guide"),
    )
    calls = []

    def run_one(root, run):
        calls.append(run.suite.name)
        return 0

    assert runner.main(["--all", "inner"], root=tmp_path, run_one=run_one) == 0
    assert "inner" in calls


# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_cli_exit_statuses(tmp_path):
    _registry_root(tmp_path, _table())
    assert runner.main(["alpha"], root=tmp_path, run_one=lambda root, run: 0) == 0
    assert runner.main(["alpha"], root=tmp_path, run_one=lambda root, run: 5) == 1
    assert runner.main(["missing"], root=tmp_path, run_one=lambda root, run: 0) == 2
    assert runner.main(["--unknown-option"], root=tmp_path, run_one=lambda root, run: 0) == 2


# spec: "The last line names the failed runs, or says that every run passed."
# task: 4
def test_run_summary_is_the_last_line(tmp_path, capsys):
    _registry_root(tmp_path, _table())
    assert runner.main(["alpha"], root=tmp_path, run_one=lambda root, run: 0) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "suite runs passed"
    assert runner.main(["alpha"], root=tmp_path, run_one=lambda root, run: 5) == 1
    assert capsys.readouterr().err.splitlines()[-1] == "suite runs failed: alpha (3.13)"


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_inherits_environment_and_uses_suite_directory(tmp_path, monkeypatch, capfd):
    suite = _suite()
    suite_dir = tmp_path / suite.dir
    suite_dir.mkdir(parents=True)
    bin_dir = tmp_path / "bin"
    probe = tmp_path / "probe.json"
    script = _write(
        tmp_path,
        "bin/uv",
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        "with open(os.environ['RUNNER_PROBE'], 'w') as output:\n"
        "    json.dump({'cwd': os.getcwd(), 'argv': sys.argv[1:], "
        "'sweep': os.getenv('CALIBRATION_SWEEP'), "
        "'sentinel': os.getenv('RUNNER_SENTINEL')}, output)\n"
        "print('pytest stream marker')\n",
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("RUNNER_PROBE", str(probe))
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("RUNNER_SENTINEL", "retained")
    run = runner.runs(suite)[0]
    assert runner.run_subprocess(tmp_path, run) == 0
    observed = json.loads(probe.read_text())
    assert observed["cwd"] == str(suite_dir)
    assert observed["argv"] == list(run.argv[1:])
    assert observed["sweep"] == "1"
    assert observed["sentinel"] == "retained"
    assert "pytest stream marker" in capfd.readouterr().out


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_is_a_failed_run(tmp_path, monkeypatch):
    _registry_root(tmp_path, _table())
    (tmp_path / "skills/alpha/scripts").mkdir(parents=True)
    monkeypatch.setenv("PATH", str(tmp_path / "empty-bin"))
    assert runner.main(["alpha"], root=tmp_path, run_one=runner.run_subprocess) == 1


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_pytest_file_patterns_are_both_discovered(tmp_path):
    _git_init(tmp_path)
    _write(tmp_path, "first/test_one.py")
    _write(tmp_path, "second/one_test.py")
    _write(tmp_path, "third/tests.py")
    assert runner.pytest_dirs(tmp_path) == {"first", "second"}


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_staged_unregistered_directory_is_reported(tmp_path):
    data = _covered_repo(tmp_path)
    _write(tmp_path, "new/test_new.py")
    subprocess.run(["git", "add", "new/test_new.py"], cwd=tmp_path, check=True)
    assert (
        "new: holds pytest files, but no suite in build/suites.toml contains it"
        in runner.check(tmp_path, data)
    )


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_missing_and_empty_registered_directories_are_reported(tmp_path):
    _git_init(tmp_path)
    tables = (
        _table(name="known", directory="known"),
        _table(name="missing", directory="missing"),
        _table(name="empty", directory="empty"),
    )
    _registry_root(tmp_path, *tables)
    _write(tmp_path, "known/test_known.py")
    _write(tmp_path, "empty/keep.txt")
    findings = runner.check(tmp_path, _data(*tables))
    assert any("missing" in line for line in findings)
    assert any("empty" in line for line in findings)


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_ignored_test_directory_does_not_create_a_finding(tmp_path):
    data = _covered_repo(tmp_path)
    _write(tmp_path, ".gitignore", "ignored/\n")
    _write(tmp_path, "ignored/test_later.py")
    assert runner.check(tmp_path, data) == []


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_untracked_test_directory_creates_a_finding(tmp_path):
    data = _covered_repo(tmp_path)
    _write(tmp_path, "draft/test_new.py")
    assert (
        "draft: holds pytest files, but no suite in build/suites.toml contains it"
        in runner.check(tmp_path, data)
    )


# spec: "If git fails, `--check` fails."
# task: 4
def test_check_fails_when_git_cannot_list_files(tmp_path):
    table = _table(name="known", directory="known")
    _registry_root(tmp_path, table)
    _write(tmp_path, "known/test_known.py")
    assert runner.check(tmp_path, _data(table))
    assert runner.main(["--check"], root=tmp_path) == 1


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_success_and_finding_output(tmp_path, capsys):
    _covered_repo(tmp_path)
    assert runner.main(["--check"], root=tmp_path) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"
    _write(tmp_path, "draft/test_new.py")
    assert runner.main(["--check"], root=tmp_path) == 1
    output = capsys.readouterr()
    lines = (output.out + output.err).splitlines()
    assert lines == [
        "draft: holds pytest files, but no suite in build/suites.toml contains it"
    ]


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_ninth_lint_invokes_only_the_check_mode():
    text = (runner.REPO / "build/run_commit_lints.sh").read_text()
    commands = [line.strip() for line in text.splitlines() if line.strip().startswith("run ")]
    assert len(commands) == 9
    assert (
        "run suite_registry uv run --python 3.13 python build/run_suites.py --check"
        in commands
    )
    assert sum("run_suites.py" in line for line in commands) == 1


# spec: "Its header says \"nine\"."
# task: 6
def test_commit_lint_header_says_nine():
    text = (runner.REPO / "build/run_commit_lints.sh").read_text()
    header = text.split("\nrun ", 1)[0].lower()
    assert "nine" in header


# spec: "`suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_tests_include_the_new_clone_case():
    source = (runner.REPO / "build/test_commit_lints.py").read_text()
    tree = ast.parse(source)
    checks_assignments = [
        node for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and "CHECKS" in ast.get_source_segment(source, node)
    ]
    assert any("suite_registry" in ast.get_source_segment(source, node) for node in checks_assignments)
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_unregistered_suite_is_refused"
    )
    body = ast.get_source_segment(source, function)
    assert "test_new.py" in body
    assert "suite_registry" in body


# spec: "The root `CLAUDE.md` then replaces its per-suite commands with a short block that points at the runner."
# task: 7
def test_root_commands_block_points_at_all_runner_modes():
    lines = (runner.REPO / "CLAUDE.md").read_text().splitlines()
    commands = [
        line for line in lines
        if "uv run --python 3.13 python build/run_suites.py" in line
    ]
    assert any("--list" in line for line in commands)
    assert any("<name>" in line and "--extras" in line and "<pytest args>" in line for line in commands)
    assert any("--all" in line for line in commands)
    assert any("--check" in line for line in commands)


# spec: "Rewrite the intro paragraph."
# task: 7
def test_root_intro_names_the_registry_runner_and_directory_scope():
    text = (runner.REPO / "CLAUDE.md").read_text()
    intro = "\n".join(text.splitlines()[:65])
    assert "There is no root test runner" not in text
    assert "build/suites.toml" in intro
    assert "build/run_suites.py" in intro
    assert "uv" in intro
    assert "3.13" in intro
    assert "directory" in intro
    assert "test_build.py" in intro


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_selected_tests_and_tools_remain_literal_commands():
    text = (runner.REPO / "CLAUDE.md").read_text()
    command_lines = [
        line for line in text.splitlines()
        if line.lstrip().startswith(("cd ", "uv run ", "python ", "bash "))
    ]
    for token in (
        "test_runtime_support.py",
        "test_commit_lints.py",
        "declared_dependencies",
        "test_real_skill",
        "test_check_jax_examples.py",
        "verify_citations.py",
        "extract_structure.py",
        "cli.py lint",
        "cli.py check",
    ):
        assert any(token in line for line in command_lines), token
    assert "Single test" in text
    assert any("::" in line for line in command_lines)
    assert sum("build.py" in line for line in command_lines) >= 2


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_file_has_no_bare_directory_suite_command_and_is_under_limit():
    text = (runner.REPO / "CLAUDE.md").read_text()
    assert len(text.splitlines()) < 200
    assert not re.search(
        r"(?m)^cd (?:skills/\S+|build(?:/cc_guide)?|hooks) && "
        r"uv run[^\n]*python -m pytest -q\s*$",
        text,
    )


# spec: "`build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_guide_describes_the_ninth_lint():
    text = (runner.REPO / "build/CLAUDE.md").read_text()
    assert "the nine commit lints" in text
    assert "suites.toml" in text
    assert "run_suites.py" in text
    assert "--check" in text
    assert "the eight commit lints" not in text


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_uses_the_first_line_stamp():
    source = (runner.REPO / "build/test_check_conformance.py").read_text()
    tree = ast.parse(source)
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    body = ast.get_source_segment(source, function)
    assert "@needs_pilot" not in body
    assert "cc-guide:" in body
    first_line = (runner.REPO / "CLAUDE.md").read_text().splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .* @\S+ -->", first_line)


# spec: "`build/test_run_suites.py`, stdlib and pytest only, which the build suite collects."
# task: 5
def test_build_suite_contains_the_runner_test_module_without_external_dependencies():
    path = runner.REPO / "build/test_run_suites.py"
    source = path.read_text()
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.append(node.module.split(".", 1)[0])
    assert set(imported) <= (sys.stdlib_module_names | {"pytest", "build", "run_suites"})
    assert any(
        isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        for node in tree.body
    )


# spec: "`build/suites.toml` registers every directory suite (R2.3) and `--check` passes."
# task: 5
def test_real_registry_passes_the_coverage_guard(capsys):
    assert runner.main(["--check"], root=runner.REPO) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"


# spec: "`bash build/run_commit_lints.sh` prints `commit lints passed`."
# task: 6
def test_commit_lint_gate_passes():
    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=runner.REPO,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "commit lints passed" in result.stdout + result.stderr
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`.</plan></flag>
<flag task="2"><spec>Default `['3.13']`.</spec><plan>`DEFAULT_PYTHONS = ('3.12',)`</plan></flag>
<flag task="5"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>`cc_guide`</plan></flag>
</flags>
<untestable>
Next step: an implementation plan from the writing-plans skill (`entry_check.py` reported plan id 54 as next free on 2026-10-18).
`CLAUDE.md` had 199 on `main` at `456e3fb`.
Its Commands block spends lines 66–125, 60 lines, on one `cd <dir> && uv run … python -m pytest -q` command and comment per suite.
Each new suite costs two or three more lines.
Plan 50 (the superpowers upstream fixes, lowmason/agent-skills#56) took the file from 195 to 199.
Plan 52 (the write-with-asd-ste100 skill, not merged) needs two more lines.
Its open question Q4 asked where they come from: (a) fold seven suites under one comment, (b) record a size deviation, or (c) move the per-suite commands out of the root file first.
In plan 38, Task 2 condensed `CLAUDE.md` from 224 lines to 170 and kept every command in place.
The file then grew back to 199 by 2026-10-18.
Worktree-isolated sessions and their subagents have refused compound shell such as `cd X && Y` (seen on 2026-10-12).
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
"This work lands whole, registry and CLAUDE.md shrink, ahead of plan 52's Task 6.
Task 6 then adds one build/suites.toml entry instead of editing Commands.
Plan 52's planning session amends its plan to match and records Q4 as (c)."
Rejected: a Python list inside the runner (every suite change becomes a code edit), and one manifest per suite directory (`install.py` copies skill directories, so the manifests would ship with installed skills).
An `@`-imported document was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
Every command, dependency and note survives; the only change is the form.
With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character.
`build/run_commit_lints.sh` keeps its literal commands.
The deletion of lines 66–125 is bounded by two lines that no other plan edits: the `# Full build-directory tests` comment and the `cd hooks && …` command.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
Same number of lines.
Line 133 is not touched (plan 53's Task 7 edits it).
The file ends at about 145 lines.
No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
The new files are the owner's original tooling.
The register's deviation `claude-md-serves-codex-gemini` still holds as written: a condensed Commands block stays in the root file, and the registry is a plain file that every runtime can read.
Write each test before its code and see it fail first (red, then green).
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
The build suite passes (where the missing `build/.scratch/` lets it).
`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`.
The Stage 2 audit passes, and the behaviour runs match.
The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
The commit hook runs one more fast, stdlib-only check.
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
Size: design.
Revisit if: the owner wants suites in CI.
Size: plan.
Revisit if: `--all` gets slow or a tool needs to parse its results.
Revisit if: `CLAUDE.md` nears its limit again.
</untestable>