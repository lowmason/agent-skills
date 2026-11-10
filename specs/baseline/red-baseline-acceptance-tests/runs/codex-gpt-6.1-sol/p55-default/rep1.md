<tests>
import ast
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

import run_suites as runner


ROOT = Path(runner.__file__).resolve().parent.parent
RUNNER_FILE = ROOT / "build/run_suites.py"
REGISTRY_FILE = ROOT / "build/suites.toml"

# Values below come from R2.3. Each dependency list includes R2.2's pytest.
EXPECTED = {
    "bayesian-workflow": (
        "skills/bayesian-workflow/scripts",
        ("pytest", "arviz", "arviz-stats", "numpy", "xarray"),
        ("matplotlib",),
        ("3.13",),
    ),
    "brainstorming": (
        "skills/brainstorming/scripts", ("pytest",), (), ("3.13",)
    ),
    "build": (
        "build",
        ("pytest", "numpy", "polars", "pyyaml"),
        (
            "arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots",
            "numpyro", "jax", "matplotlib",
        ),
        ("3.13",),
    ),
    "cc-guide": ("build/cc_guide", ("pytest",), (), ("3.13",)),
    "classification-codes": (
        "skills/classification-codes/scripts",
        ("pytest", "polars"), (), ("3.13",),
    ),
    "describe-critique-methodology": (
        "skills/describe-critique-methodology/scripts",
        ("pytest",), (), ("3.13",),
    ),
    "design-architecture": (
        "skills/design-architecture/scripts", ("pytest",), (), ("3.13",)
    ),
    "explore-data": (
        "skills/explore-data/scripts", ("pytest", "polars"), (), ("3.13",)
    ),
    "geographic-codes": (
        "skills/geographic-codes/scripts",
        ("pytest", "polars", "fastexcel"), (), ("3.13",),
    ),
    "hooks": ("hooks", ("pytest",), (), ("3.13", "/usr/bin/python3")),
    "llm-wiki": ("skills/llm-wiki/scripts", ("pytest",), (), ("3.13",)),
    "recommend-probabilistic-model": (
        "skills/recommend-probabilistic-model/scripts",
        ("pytest", "numpy", "polars"), (), ("3.13",),
    ),
    "recommend-visualization": (
        "skills/recommend-visualization/scripts",
        ("pytest", "numpy", "polars"), (), ("3.13",),
    ),
    "subagent-driven-development": (
        "skills/subagent-driven-development/scripts",
        ("pytest",), (), ("3.13",),
    ),
    "systematic-debugging": (
        "skills/systematic-debugging", ("pytest",), (), ("3.13",)
    ),
    "track-model-experiments": (
        "skills/track-model-experiments/scripts",
        ("pytest", "numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"),
        (), ("3.13",),
    ),
    "tune-hyperparameters": (
        "skills/tune-hyperparameters/scripts",
        ("pytest", "numpy", "polars"),
        ("scikit-learn", "optuna"), ("3.13",),
    ),
    "writing-plans": (
        "skills/writing-plans/scripts", ("pytest",), (), ("3.13",)
    ),
}


def entry(name="brainstorming", directory="skills/brainstorming/scripts", **changes):
    result = {"name": name, "dir": directory, "with": ["pytest"]}
    result.update(changes)
    return result


def inventory_entry(name):
    directory, deps, extras, pythons = EXPECTED[name]
    return entry(
        name, directory,
        **{"with": list(deps), "extras": list(extras), "pythons": list(pythons)},
    )


def parse_entries(*entries):
    return runner.parse({"suite": list(entries)})


def write_registry(root, data):
    path = root / "build/suites.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in data.items():
        if key == "suite" and isinstance(value, list) and all(
            isinstance(item, dict) for item in value
        ):
            for item in value:
                lines.append("[[suite]]")
                lines.extend(
                    f"{field} = {json.dumps(content)}"
                    for field, content in item.items()
                )
                lines.append("")
        else:
            lines.append(f"{key} = {json.dumps(value)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_project(root, *entries):
    write_registry(root, {"suite": list(entries)})
    for item in entries:
        directory = root / item["dir"]
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "test_new.py").write_text(
            "def test_new():\n    pass\n", encoding="utf-8"
        )


def invoke(argv, root, run_one):
    try:
        return runner.main(argv, root=root, run_one=run_one)
    except SystemExit as error:
        return 0 if error.code is None else error.code


def no_run(*args, **kwargs):
    pytest.fail("This operation must not start a suite")


def expected_argv(python, deps, pytest_args=()):
    arguments = ["uv", "run", "--python", python]
    for dependency in deps:
        arguments.extend(["--with", dependency])
    arguments.extend(["python", "-m", "pytest", "-q", *pytest_args])
    return tuple(arguments)


def git_environment():
    return {
        key: value for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        env=git_environment(),
        text=True,
        capture_output=True,
        check=True,
    )


def init_git(root):
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init")
    git(root, "config", "user.name", "Acceptance Tests")
    git(root, "config", "user.email", "acceptance@example.invalid")


def registered_git_project(root):
    make_project(root, entry())
    init_git(root)
    git(root, "add", ".")


def install_fake_tool(monkeypatch, root, name, stdout="", stderr="", status=0):
    directory = root / "fake-bin"
    directory.mkdir(parents=True, exist_ok=True)
    report = directory / f"{name}.json"
    executable = directory / name
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "from pathlib import Path\n"
        f"Path({str(report)!r}).write_text(json.dumps({{\n"
        "    'argv': sys.argv[1:],\n"
        "    'cwd': os.getcwd(),\n"
        "    'env': dict(os.environ),\n"
        "}}), encoding='utf-8')\n"
        f"os.write(1, {stdout.encode()!r})\n"
        f"os.write(2, {stderr.encode()!r})\n"
        f"sys.exit({status})\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    monkeypatch.setenv(
        "PATH", str(directory) + os.pathsep + os.environ.get("PATH", "")
    )
    monkeypatch.setenv("PYTHONCOERCECLOCALE", "0")
    return report


def invalid_registries():
    cases = []

    def add(label, data):
        cases.append(pytest.param(data, id=label))

    add("unknown-root-key", {"suite": [entry()], "unexpected": True})
    add("unknown-suite-key", {"suite": [entry(unexpected=True)]})
    add("missing-suite-table", {})
    add("suite-wrong-type", {"suite": "brainstorming"})
    add("suite-member-wrong-type", {"suite": [7]})

    for key in ("name", "dir", "with"):
        item = entry()
        del item[key]
        add(f"missing-{key}", {"suite": [item]})

    for key, wrong_value in (
        ("name", 7),
        ("name", ["brainstorming"]),
        ("dir", 7),
        ("dir", ["skills/brainstorming/scripts"]),
        ("with", "pytest"),
        ("with", [7]),
        ("extras", "matplotlib"),
        ("extras", [7]),
        ("pythons", "3.13"),
        ("pythons", [3.13]),
        ("notes", "node skip"),
        ("notes", [False]),
    ):
        add(f"wrong-{key}-{wrong_value!r}", {"suite": [entry(**{key: wrong_value})]})

    add(
        "duplicate-name",
        {"suite": [entry(), entry(directory="other/scripts")]},
    )
    add(
        "duplicate-directory",
        {"suite": [entry(), entry(name="writing-plans")]},
    )
    add("missing-pytest", {"suite": [entry(**{"with": ["numpy"]})]})
    add("empty-with", {"suite": [entry(**{"with": []})]})
    return cases


INVALID_REGISTRIES = invalid_registries()


@pytest.mark.parametrize("data", INVALID_REGISTRIES)
# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
def test_validation_rejects_each_invalid_registry(data):
    problems = runner.validate(data)
    assert isinstance(problems, list)
    assert problems
    assert all(isinstance(problem, str) and problem for problem in problems)


# spec: "The interpreters, one run each, in order. Default `['3.13']`."
# task: 2
def test_omitted_optional_fields_and_default_python():
    data = {"suite": [entry()]}
    assert runner.validate(data) == []
    suite, = runner.parse(data)
    assert suite.name == "brainstorming"
    assert suite.dir == "skills/brainstorming/scripts"
    assert tuple(suite.deps) == ("pytest",)
    assert tuple(suite.extras) == ()
    assert tuple(suite.notes) == ()
    assert tuple(suite.pythons) == ("3.13",)
    assert tuple(runner.DEFAULT_PYTHONS) == ("3.13",)


# spec: "What the suite covers or needs: opt-in environment variables, expected warnings, run times, why some tests skip or fail."
# task: 2
def test_optional_notes_are_preserved_in_order():
    notes = ["CALIBRATION_SWEEP=1", "expected arviz warnings"]
    data = {"suite": [entry(notes=notes)]}
    assert runner.validate(data) == []
    suite, = runner.parse(data)
    assert tuple(suite.notes) == tuple(notes)


@pytest.mark.parametrize("name", EXPECTED)
# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_argv_and_shell_forms(name):
    directory, deps, _, pythons = EXPECTED[name]
    suite, = parse_entries(inventory_entry(name))
    runs = runner.runs(suite)
    assert len(runs) == len(pythons)
    for run, python in zip(runs, pythons):
        argv = expected_argv(python, deps)
        assert run.suite == suite
        assert run.python == python
        assert tuple(run.argv) == argv
        assert run.label == f"{name} ({python})"
        assert run.shell() == f"cd {directory} && {' '.join(argv)}"


@pytest.mark.parametrize("name", EXPECTED)
# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_are_opt_in_and_append_after_default_dependencies(name):
    _, deps, extras, pythons = EXPECTED[name]
    suite, = parse_entries(inventory_entry(name))
    defaults = runner.runs(suite)
    expanded = runner.runs(suite, extras=True)
    for default, extra, python in zip(defaults, expanded, pythons):
        assert tuple(default.argv) == expected_argv(python, deps)
        assert tuple(extra.argv) == expected_argv(python, deps + extras)


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 2
def test_pytest_arguments_reach_every_interpreter_unchanged():
    suite, = parse_entries(inventory_entry("hooks"))
    arguments = ("test_new.py::test_new", "-k", "not slow", "-s", "-rs")
    runs = runner.runs(suite, pytest_args=arguments)
    assert [run.python for run in runs] == ["3.13", "/usr/bin/python3"]
    for run in runs:
        assert tuple(run.argv) == expected_argv(run.python, ("pytest",), arguments)


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_directory_dependencies_and_pytest_arguments():
    suite, = parse_entries(
        entry(
            directory="skills/a suite/scripts",
            **{"with": ["pytest", "arviz>=1.0"]},
        )
    )
    arguments = ("test_new.py::test_new[space case]", "-k", "not slow", "-s")
    run, = runner.runs(suite, pytest_args=arguments)
    shell = run.shell()
    assert shlex.split(shell) == ["cd", suite.dir, "&&", *run.argv]
    assert shlex.split(shell.split(" && ", 1)[1]) == list(run.argv)


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_uses_directory_boundaries_and_does_not_contain_itself():
    suites = parse_entries(
        inventory_entry("build"),
        inventory_entry("cc-guide"),
        entry(directory="building"),
        inventory_entry("hooks"),
    )
    by_name = {suite.name: suite for suite in suites}
    assert runner.container(by_name["cc-guide"], suites) == by_name["build"]
    for name in ("build", "brainstorming", "hooks"):
        assert runner.container(by_name[name], suites) is None


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 2
def test_repo_constant_does_not_depend_on_current_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert Path(runner.REPO).resolve() == ROOT
    assert runner.REGISTRY == "build/suites.toml"


@pytest.mark.parametrize("data", INVALID_REGISTRIES)
@pytest.mark.parametrize("argv", [("--list",), ("brainstorming",), ("--all",)])
# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_invalid_registry_stops_every_execution_or_listing_mode(tmp_path, data, argv):
    write_registry(tmp_path, data)
    assert invoke(list(argv), tmp_path, no_run) == 2


@pytest.mark.parametrize("argv", [("--list",), ("brainstorming",), ("--all",), ("--check",)])
# spec: "Validation fails closed."
# task: 4
def test_malformed_toml_is_refused(tmp_path, argv):
    path = tmp_path / "build/suites.toml"
    path.parent.mkdir(parents=True)
    path.write_text("[[suite]\n", encoding="utf-8")
    expected_status = 1 if argv == ("--check",) else 2
    assert invoke(list(argv), tmp_path, no_run) == expected_status


@pytest.mark.parametrize(
    "argv",
    [
        ["--unknown-option"],
        ["unknown-suite"],
        ["--list", "unknown-suite"],
        ["brainstorming", "unknown-suite"],
    ],
)
# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_usage_errors_and_unknown_names_return_two_without_running(tmp_path, argv):
    make_project(tmp_path, entry())
    assert invoke(argv, tmp_path, no_run) == 2


@pytest.mark.parametrize("extras", [False, True])
# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_prints_commands_extras_notes_and_selection(tmp_path, capsys, extras):
    build = inventory_entry("build")
    build["notes"] = ["build/.scratch/"]
    hooks = inventory_entry("hooks")
    hooks["notes"] = ["3.9 floor", "launchd-PATH skips", "Gate B probe"]
    make_project(tmp_path, build, inventory_entry("cc-guide"), hooks)
    arguments = ("-k", "not slow", "-s", "-rs")
    argv = ["--list", "hooks", "build"]
    if extras:
        argv.append("--extras")
    argv.extend(["--", *arguments])

    assert invoke(argv, tmp_path, no_run) == 0
    output = capsys.readouterr().out

    assert "cc-guide" not in output
    positions = []
    for name, notes in (("hooks", hooks["notes"]), ("build", build["notes"])):
        directory, deps, extra_deps, pythons = EXPECTED[name]
        commands = []
        for python in pythons:
            argv = expected_argv(
                python, deps + extra_deps if extras else deps, arguments
            )
            command = f"cd {shlex.quote(directory)} && {shlex.join(argv)}"
            assert command in output
            commands.append(command)
        assert name in output
        assert directory in output
        positions.append(output.index(commands[0]))
        for dependency in extra_deps:
            assert dependency in output
        for note in notes:
            assert note in output
    assert positions == sorted(positions)


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_without_names_includes_nested_suites(tmp_path, capsys):
    make_project(
        tmp_path,
        inventory_entry("build"),
        inventory_entry("cc-guide"),
        inventory_entry("hooks"),
    )
    assert invoke(["--list"], tmp_path, no_run) == 0
    output = capsys.readouterr().out
    for name in ("build", "cc-guide", "hooks"):
        directory, deps, _, pythons = EXPECTED[name]
        assert name in output
        assert directory in output
        for python in pythons:
            assert (
                f"cd {directory} && {' '.join(expected_argv(python, deps))}"
                in output
            )


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_runs_preserve_suite_and_interpreter_order(tmp_path):
    make_project(tmp_path, entry(), inventory_entry("hooks"))
    calls = []

    def run_one(root, run):
        calls.append((root, run))
        return 0

    arguments = ("test_new.py::test_new", "-s", "-rs")
    assert invoke(
        ["hooks", "brainstorming", "--", *arguments], tmp_path, run_one
    ) == 0
    assert [(run.suite.name, run.python) for _, run in calls] == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("brainstorming", "3.13"),
    ]
    assert all(root == tmp_path for root, _ in calls)
    assert all(
        tuple(run.argv[-len(arguments):]) == arguments for _, run in calls
    )


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_notes_follow_first_header_and_precede_run_output(tmp_path, capsys):
    hooks = inventory_entry("hooks")
    hooks["notes"] = ["3.9 floor", "launchd-PATH skips", "Gate B probe"]
    make_project(tmp_path, hooks)
    calls = []

    def run_one(root, run):
        calls.append(run)
        print(f"OUTPUT {run.label}")
        return 0

    assert invoke(["hooks"], tmp_path, run_one) == 0
    output = capsys.readouterr().out
    first_header = output.index("== hooks (3.13)")
    first_output = output.index("OUTPUT hooks (3.13)")
    second_header = output.index("== hooks (/usr/bin/python3)")
    second_output = output.index("OUTPUT hooks (/usr/bin/python3)")
    assert first_header < first_output < second_header < second_output
    for note in hooks["notes"]:
        assert output.count(note) == 1
        assert first_header < output.index(note) < first_output
    assert len(calls) == 2


@pytest.mark.parametrize(
    "statuses, expected_status",
    [((0, 0, 0), 0), ((1, 5, 0), 1), ((0, 0, 5), 1)],
)
# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_all_runs_happen_and_final_summary_identifies_failures(
    tmp_path, capsys, statuses, expected_status
):
    make_project(tmp_path, inventory_entry("hooks"), entry())
    calls = []

    def run_one(root, run):
        result = statuses[len(calls)]
        calls.append(run)
        return result

    assert invoke(["hooks", "brainstorming"], tmp_path, run_one) == expected_status
    assert len(calls) == 3
    captured = capsys.readouterr()
    lines = (captured.out + captured.err).strip().splitlines()
    assert lines
    summary = lines[-1]
    if expected_status == 0:
        assert re.search(r"\bpass(?:ed)?\b", summary, re.IGNORECASE)
        assert not re.search(r"\bfail(?:ed|ure)?\b", summary, re.IGNORECASE)
    else:
        for run, status in zip(calls, statuses):
            if status:
                assert run.label in summary
            else:
                assert run.label not in summary


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_skips_nested_suites_but_not_directory_prefix_siblings(tmp_path, capsys):
    make_project(
        tmp_path,
        inventory_entry("build"),
        inventory_entry("cc-guide"),
        entry(directory="building"),
        inventory_entry("hooks"),
    )
    calls = []

    def run_one(root, run):
        calls.append(run)
        return 0

    assert invoke(["--all"], tmp_path, run_one) == 0
    names = [run.suite.name for run in calls]
    assert names.count("build") == 1
    assert names.count("brainstorming") == 1
    assert names.count("hooks") == 2
    assert "cc-guide" not in names
    lines = capsys.readouterr().out.splitlines()
    skip_lines = [
        line for line in lines
        if "cc-guide" in line and "build/cc_guide" in line
    ]
    assert len(skip_lines) == 1
    assert "build" in skip_lines[0]


# spec: "A suite named on the command line always runs."
# task: 4
def test_explicitly_named_nested_suite_runs(tmp_path):
    make_project(
        tmp_path, inventory_entry("build"), inventory_entry("cc-guide")
    )
    calls = []

    def run_one(root, run):
        calls.append(run)
        return 0

    assert invoke(["cc-guide"], tmp_path, run_one) == 0
    assert [run.suite.name for run in calls] == ["cc-guide"]


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_receives_exact_environment_argv_and_working_directory(
    tmp_path, monkeypatch, capfd
):
    make_project(tmp_path, inventory_entry("bayesian-workflow"))
    report = install_fake_tool(
        monkeypatch, tmp_path, "uv",
        stdout="pytest stdout\n", stderr="pytest stderr\n",
    )
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    environment = dict(os.environ)
    suite, = parse_entries(inventory_entry("bayesian-workflow"))
    run, = runner.runs(suite, pytest_args=("-s",))

    assert runner.run_subprocess(tmp_path, run) == 0
    received = json.loads(report.read_text(encoding="utf-8"))
    assert received["argv"] == list(run.argv[1:])
    assert Path(received["cwd"]) == tmp_path / suite.dir
    assert received["env"] == environment
    captured = capfd.readouterr()
    assert "pytest stdout" in captured.out
    assert "pytest stderr" in captured.err


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_header_and_notes_reach_stdout_before_child_output(
    tmp_path, monkeypatch, capfd
):
    record = entry(notes=["node skip"])
    make_project(tmp_path, record)
    install_fake_tool(monkeypatch, tmp_path, "uv", stdout="CHILD OUTPUT\n")
    assert invoke(["brainstorming"], tmp_path, runner.run_subprocess) == 0
    output = capfd.readouterr().out
    assert (
        output.index("== brainstorming (3.13)")
        < output.index("node skip")
        < output.index("CHILD OUTPUT")
    )


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_is_failure_and_does_not_abort_remaining_runs(
    tmp_path, monkeypatch, capsys
):
    make_project(tmp_path, inventory_entry("hooks"))
    empty_path = tmp_path / "empty-path"
    empty_path.mkdir()
    monkeypatch.setenv("PATH", str(empty_path))
    assert invoke(["hooks"], tmp_path, runner.run_subprocess) == 1
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "== hooks (3.13)" in output
    assert "== hooks (/usr/bin/python3)" in output
    summary = output.strip().splitlines()[-1]
    assert "hooks (3.13)" in summary
    assert "hooks (/usr/bin/python3)" in summary


# spec: "Invoked as `uv run --python 3.13 python build/run_suites.py …` from any directory."
# task: 4
def test_script_lists_real_registry_from_an_unrelated_directory(tmp_path):
    result = subprocess.run(
        [sys.executable, str(RUNNER_FILE), "--list", "brainstorming"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    directory, deps, _, _ = EXPECTED["brainstorming"]
    assert (
        f"cd {directory} && {' '.join(expected_argv('3.13', deps))}"
        in result.stdout
    )


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 4
def test_runner_imports_only_standard_library_modules():
    tree = ast.parse(RUNNER_FILE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.level == 0
            imported.add(node.module.split(".", 1)[0])
    assert imported <= sys.stdlib_module_names | {"__future__"}


# spec: "The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root."
# task: 3
def test_pytest_file_inventory_uses_the_required_git_command(
    tmp_path, monkeypatch
):
    report = install_fake_tool(
        monkeypatch, tmp_path, "git",
        stdout="skills/brainstorming/scripts/test_new.py\n",
    )
    assert runner.pytest_dirs(tmp_path) == {"skills/brainstorming/scripts"}
    received = json.loads(report.read_text(encoding="utf-8"))
    assert received["argv"] == [
        "ls-files", "--cached", "--others", "--exclude-standard"
    ]
    assert Path(received["cwd"]) == tmp_path


@pytest.mark.parametrize("tracked", [False, True])
@pytest.mark.parametrize(
    "filename, is_pytest_file",
    [
        ("test_new.py", True),
        ("new_test.py", True),
        ("test_.py", True),
        ("_test.py", True),
        ("test.py", False),
        ("tests.py", False),
        ("test_new.txt", False),
        ("new_test.py.backup", False),
    ],
)
# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_default_pytest_patterns_and_tracked_or_untracked_files(
    tmp_path, tracked, filename, is_pytest_file
):
    registered_git_project(tmp_path)
    directory = tmp_path / "skills/new-suite/scripts"
    directory.mkdir(parents=True)
    path = directory / filename
    path.write_text("", encoding="utf-8")
    if tracked:
        git(tmp_path, "add", "--", str(path.relative_to(tmp_path)))

    directories = runner.pytest_dirs(tmp_path)
    assert directories is not None
    assert ("skills/new-suite/scripts" in directories) is is_pytest_file
    findings = runner.check(tmp_path, {"suite": [entry()]})
    if is_pytest_file:
        assert len(findings) == 1
        assert "skills/new-suite/scripts" in findings[0]
    else:
        assert findings == []


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_ignored_test_trees_produce_no_coverage_findings(tmp_path):
    registered_git_project(tmp_path)
    (tmp_path / ".gitignore").write_text(
        ".claude/worktrees/\nbuild/.scratch/\nignored/\n", encoding="utf-8"
    )
    for relative in (
        ".claude/worktrees/other/test_new.py",
        "build/.scratch/test_new.py",
        "ignored/test_new.py",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    assert runner.pytest_dirs(tmp_path) == {"skills/brainstorming/scripts"}
    assert runner.check(tmp_path, {"suite": [entry()]}) == []


@pytest.mark.parametrize("exists", [False, True])
# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_missing_or_testless_registered_directory_is_a_finding(tmp_path, exists):
    data = {"suite": [entry()]}
    write_registry(tmp_path, data)
    init_git(tmp_path)
    if exists:
        directory = tmp_path / "skills/brainstorming/scripts"
        directory.mkdir(parents=True)
        (directory / "helper.py").write_text("", encoding="utf-8")
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert "skills/brainstorming/scripts" in findings[0]


# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_registered_directory_covers_descendants_but_not_prefix_siblings(tmp_path):
    make_project(tmp_path, inventory_entry("build"))
    init_git(tmp_path)
    nested = tmp_path / "build/cc_guide/test_new.py"
    nested.parent.mkdir(parents=True)
    nested.write_text("", encoding="utf-8")
    sibling = tmp_path / "building/test_new.py"
    sibling.parent.mkdir()
    sibling.write_text("", encoding="utf-8")
    findings = runner.check(tmp_path, {"suite": [inventory_entry("build")]})
    assert len(findings) == 1
    assert "building" in findings[0]
    assert "build/cc_guide" not in findings[0]


# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_root_test_file_is_not_covered_by_a_registered_child_directory(tmp_path):
    registered_git_project(tmp_path)
    (tmp_path / "test_new.py").write_text("", encoding="utf-8")
    directories = runner.pytest_dirs(tmp_path)
    assert directories is not None
    assert "." in directories
    assert len(runner.check(tmp_path, {"suite": [entry()]})) == 1


# spec: "If git fails, `--check` fails."
# task: 3
def test_git_failure_cannot_report_a_clean_registry(tmp_path, monkeypatch, capsys):
    make_project(tmp_path, entry())
    install_fake_tool(monkeypatch, tmp_path, "git", status=1)
    assert runner.pytest_dirs(tmp_path) is None
    assert runner.check(tmp_path, {"suite": [entry()]})
    assert invoke(["--check"], tmp_path, no_run) == 1
    captured = capsys.readouterr()
    assert "suite registry ok" not in captured.out + captured.err


@pytest.mark.parametrize("data", INVALID_REGISTRIES)
# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 4
def test_check_reports_invalid_registry_as_findings_with_exit_one(
    tmp_path, data, capsys
):
    registered_git_project(tmp_path)
    write_registry(tmp_path, data)
    findings = runner.check(tmp_path, data)
    assert findings
    assert invoke(["--check"], tmp_path, no_run) == 1
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "suite registry ok" not in output
    for finding in findings:
        assert finding in output


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_success_and_one_line_per_finding(tmp_path, capsys):
    registered_git_project(tmp_path)
    assert invoke(["--check"], tmp_path, no_run) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "suite registry ok"
    assert captured.err == ""

    for relative in (
        "skills/new-suite/scripts/test_new.py",
        "hooks/new_test.py",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    findings = runner.check(tmp_path, {"suite": [entry()]})
    assert len(findings) == 2
    assert invoke(["--check"], tmp_path, no_run) == 1
    captured = capsys.readouterr()
    lines = (captured.out + captured.err).strip().splitlines()
    assert sorted(lines) == sorted(findings)


# spec: "The entries carry the text of today's commands and comments."
# task: 5
def test_real_registry_matches_the_complete_spec_inventory():
    data = tomllib.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    assert runner.validate(data) == []
    suites = runner.parse(data)
    by_name = {suite.name: suite for suite in suites}
    assert set(EXPECTED) <= set(by_name)
    assert len(by_name) == len(suites)
    assert len({suite.dir for suite in suites}) == len(suites)
    for name, (directory, deps, extras, pythons) in EXPECTED.items():
        suite = by_name[name]
        assert suite.dir == directory
        assert tuple(suite.deps) == deps
        assert tuple(suite.extras) == extras
        assert tuple(suite.pythons) == pythons


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_tables_are_sorted_by_name():
    data = tomllib.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    names = [item["name"] for item in data["suite"]]
    assert names == sorted(names)


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_describes_keys_sort_order_and_ninth_lint():
    text = REGISTRY_FILE.read_text(encoding="utf-8")
    header = text.split("[[suite]]", 1)[0]
    comments = "\n".join(
        line.lstrip("#").strip()
        for line in header.splitlines()
        if line.lstrip().startswith("#")
    )
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert re.search(rf"\b{key}\b", comments)
    assert re.search(r"\bsort(?:ed|ing)?\b", comments, re.IGNORECASE)
    assert re.search(r"\bninth\b", comments, re.IGNORECASE)
    assert re.search(r"\bcommit\b.*\blint\b", comments, re.IGNORECASE)


@pytest.mark.parametrize(
    "name, required_text",
    [
        ("build", "build/.scratch/"),
        ("bayesian-workflow", "CALIBRATION_SWEEP=1"),
        ("bayesian-workflow", "arviz"),
        ("llm-wiki", "@needs_pilot"),
        ("llm-wiki", "$LLM_WIKI_ROOT"),
        ("brainstorming", "node"),
        ("tune-hyperparameters", "--with sklearn"),
        ("hooks", "3.9"),
        ("hooks", "launchd"),
        ("hooks", "Gate B"),
    ],
)
# spec: "The notes carry the rest of each comment."
# task: 5
def test_real_registry_preserves_explicit_note_details(name, required_text):
    data = tomllib.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    suite = next(suite for suite in runner.parse(data) if suite.name == name)
    assert required_text in "\n".join(suite.notes)


# spec: "the real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_passes_coverage_check(capsys):
    data = tomllib.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    assert runner.check(ROOT, data) == []
    assert invoke(["--check"], ROOT, no_run) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"


# spec: "If plan 52 lands first after all, R5.2's deletion still works, and this plan registers that suite itself."
# task: 5
def test_plan_52_suite_is_registered_if_its_directory_has_landed():
    directory = ROOT / "skills/write-with-asd-ste100/scripts"
    if directory.is_dir():
        data = tomllib.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        by_name = {suite.name: suite for suite in runner.parse(data)}
        assert "write-with-asd-ste100" in by_name
        assert by_name["write-with-asd-ste100"].dir == (
            "skills/write-with-asd-ste100/scripts"
        )


# spec: "**The Stage 2 audit** (one time, a scratch script that is never committed, as in plan 38's Task 2)."
# task: 5
def test_audit_scratch_script_is_not_tracked():
    result = git(
        ROOT, "ls-files", "--cached", "--",
        ".sdd/55-test-suite-registry/audit_commands.py",
    )
    assert result.stdout == ""


def lint_invocations(text):
    commands = []
    for line in text.splitlines():
        if re.match(r"^\s*run\s+", line):
            tokens = shlex.split(line, comments=True)
            commands.append((tokens[1], tokens[2:]))
    return commands


# spec: "R4.4 `build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_suite_registry_is_the_literal_ninth_commit_lint():
    text = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    commands = lint_invocations(text)
    assert len(commands) == 9
    assert commands[-1] == (
        "suite_registry",
        ["uv", "run", "--python", "3.13", "python", "build/run_suites.py", "--check"],
    )
    assert sum(name == "suite_registry" for name, _ in commands) == 1
    header = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            header.append(line)
        else:
            break
    assert re.search(r"\bnine\b", "\n".join(header), re.IGNORECASE)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_checks_include_suite_registry():
    module = load_module(
        "_acceptance_commit_lint_tests", ROOT / "build/test_commit_lints.py"
    )
    assert "suite_registry" in module.CHECKS


def clone_repo(destination):
    result = subprocess.run(
        ["git", "clone", "--local", "--no-hardlinks", str(ROOT), str(destination)],
        env=git_environment(),
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    git(destination, "config", "user.name", "Acceptance Tests")
    git(destination, "config", "user.email", "acceptance@example.invalid")
    return destination


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_committed_unregistered_suite_fails_only_registry_lint(tmp_path):
    clone = clone_repo(tmp_path / "clone")
    relative = "skills/unregistered-acceptance-suite/scripts/test_new.py"
    path = clone / relative
    path.parent.mkdir(parents=True)
    path.write_text("def test_new():\n    pass\n", encoding="utf-8")
    git(clone, "add", "--", relative)
    git(
        clone, "-c", "core.hooksPath=/dev/null",
        "commit", "-m", "Add an unregistered directory suite",
    )

    script = (clone / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    results = {}
    for name, command in lint_invocations(script):
        result = subprocess.run(
            command, cwd=clone, env=git_environment(),
            text=True, capture_output=True,
        )
        results[name] = result

    failed = {
        name: result.stdout + result.stderr
        for name, result in results.items()
        if result.returncode != 0
    }
    assert set(failed) == {"suite_registry"}, failed

    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=clone, env=git_environment(), text=True, capture_output=True,
    )
    assert result.returncode != 0
    assert "commit lints passed" not in result.stdout + result.stderr


# spec: "`build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_documentation_describes_nine_lints_and_registry_check():
    text = (ROOT / "build/CLAUDE.md").read_text(encoding="utf-8")
    assert "the eight commit lints" not in text
    assert "the nine commit lints" in text
    paragraphs = text.split("\n\n")
    assert any(
        all(token in paragraph for token in (
            "suites.toml", "run_suites.py", "--check", "commit lint",
        ))
        for paragraph in paragraphs
    )


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_commands_intro_preserves_execution_rules_and_explains_registry():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "There is no root test runner" not in text
    paragraphs = [
        paragraph for paragraph in text.split("\n\n")
        if "test_build.py" in paragraph and "build/run_suites.py" in paragraph
    ]
    assert len(paragraphs) == 1
    paragraph = paragraphs[0]
    assert len(paragraph.splitlines()) == 1
    for token in ("uv", "3.13", "build/suites.toml", "notes"):
        assert token in paragraph
    assert re.search(r"director", paragraph, re.IGNORECASE)
    assert re.search(r"collis", paragraph, re.IGNORECASE)
    assert re.search(r"before", paragraph, re.IGNORECASE)


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_commands_block_has_the_four_runner_examples():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    prefix = "uv run --python 3.13 python build/run_suites.py"
    commands = [
        f"{prefix} --list",
        f"{prefix} <name> [--extras] [-- <pytest args>]",
        f"{prefix} --all",
        f"{prefix} --check",
    ]
    blocks = re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
    matching = [block for block in blocks if all(cmd in block for cmd in commands)]
    assert len(matching) == 1
    block = matching[0]
    positions = [block.index(command) for command in commands]
    assert positions == sorted(positions)
    assert any(
        line.lstrip().startswith("#")
        for line in block[:positions[0]].splitlines()
    )


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_selected_tests_and_tools_remain_in_root_documentation():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    blocks = "\n".join(
        re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
    )
    for token in (
        "test_runtime_support.py",
        "test_commit_lints.py",
        "-k declared_dependencies",
        "-k test_real_skill",
        "test_check_jax_examples.py",
        "verify_citations.py",
        "extract_structure.py",
        "run_commit_lints.sh",
    ):
        assert token in blocks
    assert "Single test" in text
    assert re.search(r"cli\.py[^\n]*\blint\b", blocks)
    assert re.search(r"cli\.py[^\n]*\bcheck\b", blocks)
    rebuild_commands = [
        line for line in blocks.splitlines()
        if "build.py" in line and not line.lstrip().startswith("#")
    ]
    assert len(rebuild_commands) >= 2


def literal_directory_suite_commands(text):
    commands = []
    for block in re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL):
        for line in block.splitlines():
            if not re.match(r"^\s*cd\s+", line):
                continue
            tokens = shlex.split(line, comments=True)
            segments = [[]]
            for token in tokens:
                if token == "&&":
                    segments.append([])
                else:
                    segments[-1].append(token)
            for segment in segments[1:]:
                for index in range(len(segment) - 1):
                    if segment[index:index + 2] == ["-m", "pytest"]:
                        if segment[index + 2:] == ["-q"]:
                            commands.append(line)
    return commands


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_documentation_has_no_literal_directory_suite_and_is_under_limit():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert literal_directory_suite_commands(text) == []
    assert len(text.splitlines()) < 200


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_runner_documentation_does_not_make_suite_or_test_count_claims():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    changed_text = "\n".join(
        paragraph for paragraph in text.split("\n\n")
        if "run_suites.py" in paragraph or "suites.toml" in paragraph
    )
    number = (
        r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen)"
    )
    assert not re.search(
        rf"\b{number}\s+(?:directory\s+)?(?:suites?|tests?)\b",
        changed_text,
        re.IGNORECASE,
    )


# spec: "The commit-lint comment names the suite-registry check and says \"nine\"."
# task: 7
def test_root_lint_comment_names_the_ninth_check():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    comment_lines = [
        line for line in text.splitlines() if line.lstrip().startswith("#")
    ]
    assert any(
        re.search(r"\bnine\b", line, re.IGNORECASE)
        and re.search(r"suite[- _]registry", line, re.IGNORECASE)
        for line in comment_lines
    )


# spec: "The comment names the suite `run_suites.py cc-guide` instead of \"its suite\"."
# task: 7
def test_cc_guide_comment_names_its_runner_command():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert any(
        "run_suites.py cc-guide" in line and line.lstrip().startswith("#")
        for line in text.splitlines()
    )


@pytest.mark.parametrize(
    "variant, should_pass",
    [("original", True), ("changed-version", True), ("missing-stamp", False)],
)
# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_checks_stamp_and_tolerates_version_changes(
    tmp_path, variant, should_pass
):
    clone = clone_repo(tmp_path / "clone")
    path = clone / "CLAUDE.md"
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    match = re.fullmatch(
        r"(<!-- cc-guide: .+ @)([^ ]+)( -->)\n?", lines[0]
    )
    assert match is not None
    if variant == "changed-version":
        lines[0] = (
            match.group(1) + match.group(2) + ".1" + match.group(3) + "\n"
        )
    elif variant == "missing-stamp":
        lines[0] = "\n"
    path.write_text("".join(lines), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", "-q",
            "build/test_check_conformance.py::"
            "test_claude_md_import_resolves_passes_on_the_repo",
        ],
        cwd=clone,
        env=git_environment(),
        text=True,
        capture_output=True,
    )
    if should_pass:
        assert result.returncode == 0, result.stdout + result.stderr
    else:
        assert result.returncode == 1, result.stdout + result.stderr
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`.</plan></flag>
<flag task="2"><spec>Default `['3.13']`.</spec><plan>DEFAULT_PYTHONS = ('3.12',)</plan></flag>
<flag task="5"><spec>| `cc-guide` | `build/cc_guide` | — | — | default |</spec><plan>`cc_guide`</plan></flag>
</flags>
<untestable>
**Status:** Design approved in brainstorming on 2026-10-18.
Next step: an implementation plan from the writing-plans skill (`entry_check.py` reported plan id 54 as next free on 2026-10-18).
`CLAUDE.md` had 199 on `main` at `456e3fb`.
Its Commands block spends lines 66–125, 60 lines, on one `cd <dir> && uv run … python -m pytest -q` command and comment per suite.
Each new suite costs two or three more lines.
Plan 50 (the superpowers upstream fixes, lowmason/agent-skills#56) took the file from 195 to 199.
Plan 52 (the write-with-asd-ste100 skill, not merged) needs two more lines.
Its open question Q4 asked where they come from: (a) fold seven suites under one comment, (b) record a size deviation, or (c) move the per-suite commands out of the root file first.
This spec is option (c).
In plan 38, Task 2 condensed `CLAUDE.md` from 224 lines to 170 and kept every command in place.
The file then grew back to 199 by 2026-10-18.
A registry removes the per-suite growth.
Worktree-isolated sessions and their subagents have refused compound shell such as `cd X && Y` (seen on 2026-10-12).
A runner gives each suite a single simple command.
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
"`run_suites.py --check` joins build/run_commit_lints.sh, so the pre-commit hook and CI run it."
"This work lands whole, registry and CLAUDE.md shrink, ahead of plan 52's Task 6.
Task 6 then adds one build/suites.toml entry instead of editing Commands.
Plan 52's planning session amends its plan to match and records Q4 as (c)."
Matches conformance.toml and manifest.toml.
Rejected: a Python list inside the runner (every suite change becomes a code edit), and one manifest per suite directory (`install.py` copies skill directories, so the manifests would ship with installed skills).
An `@`-imported document was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
**Design section 1** (the registry keys and the runner's behaviour) was approved as presented.
It is R1–R3 below.
**Design section 2** (the guard, the file edits, the tests and the couplings) was approved as presented.
It is R4–R7 below.
On `main` at `456e3fb` there are 18: the 17 in `CLAUDE.md` lines 66–125, and `build/cc_guide`, whose command is line 145.
They are selections or tools, not directory suites, and their comments say when to run them:
`build/run_commit_lints.sh` keeps its literal commands.
Every command, dependency and note survives; the only change is the form.
The notes carry the rest of each comment.
Examples: `build`'s missing `build/.scratch/` in a fresh clone or worktree; `bayesian-workflow`'s `CALIBRATION_SWEEP=1` sweep and its expected arviz warnings; `llm-wiki`'s `@needs_pilot` tests and `$LLM_WIKI_ROOT`; `brainstorming`'s node skip; `tune-hyperparameters`' "`--with sklearn` fails"; `track-model-experiments`' run time; the guard's 3.9 floor, its launchd-PATH skips and its Gate B probe for `hooks`.
With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character.
The file ends at about 145 lines.
Same number of lines.
Line 133 is not touched (plan 53's Task 7 edits it).
The deletion of lines 66–125 is bounded by two lines that no other plan edits: the `# Full build-directory tests` comment and the `cd hooks && …` command.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
The new files are the owner's original tooling.
The register's deviation `claude-md-serves-codex-gemini` still holds as written: a condensed Commands block stays in the root file, and the registry is a plain file that every runtime can read.
Write each test before its code and see it fail first (red, then green).
Under decision 2, plan 52's Task 6 drops its `CLAUDE.md:commands-moved` and `CLAUDE.md:commands` edits and adds one `[[suite]]` entry for `skills/write-with-asd-ste100/scripts` instead.
Its expectations of 199 and 197 lines (Task 1, DF19, Q4, Coupling (e)) change with it.
Its `CLAUDE.md:sources` and `CLAUDE.md:bullet` edits are outside the Commands block and still apply.
A note in the session group's shared notes folder gives the exact entry.
None of the lines that R5.1 deletes carries one of its edit anchors.
Its Task 7 edits line 133, which stays.
Its own suite commands are written out in full in the plan, so they work without `CLAUDE.md`.
It edits one sentence of `build/CLAUDE.md`'s `cc_guide/` paragraph.
R5.3 edits the `run_commit_lints.sh` paragraph and adds a sentence.
If an edit block does not match, merge by hand.
**R6's tests** run red first, then green.
Run it before the `CLAUDE.md` deletion.
It extracts every `cd <dir> && uv run …` command from lines 66–125 and 145, splitting the hooks `&&` chain into one command per run.
It asserts that the set equals the set of default shell forms that `--list` prints: nothing is missing on either side.
It also checks each comment's skip-unlocking deps against that suite's `extras`.
Run `hooks`, `build` and `bayesian-workflow` once directly and once through the runner, in the same checkout.
Their pytest summary lines match.
Then run `--all` once, and record each run's result beside the direct result.
The build suite passes (where the missing `build/.scratch/` lets it).
`bash build/run_commit_lints.sh` prints `commit lints passed`.
`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`.
The Stage 2 audit passes, and the behaviour runs match.
The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
No commit can add a test directory without a registry entry, plan 52's new suite included.
The commit hook runs one more fast, stdlib-only check.
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
It would need node, a 3.9 `/usr/bin/python3` and `build/.scratch/`.
Revisit if: the owner wants suites in CI.
Revisit if: `--all` gets slow or a tool needs to parse its results.
Revisit if: `CLAUDE.md` nears its limit again.
</untestable>