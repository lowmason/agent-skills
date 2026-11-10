<tests>
import ast
import copy
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


ROOT = Path(runner.__file__).resolve().parents[1]

EXPECTED = {
    "bayesian-workflow": (
        "skills/bayesian-workflow/scripts",
        ("pytest", "arviz", "arviz-stats", "numpy", "xarray"),
        ("matplotlib",),
        ("3.13",),
    ),
    "brainstorming": (
        "skills/brainstorming/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "build": (
        "build",
        ("pytest", "numpy", "polars", "pyyaml"),
        (
            "arviz>=1.0",
            "arviz-base",
            "arviz-stats",
            "arviz-plots",
            "numpyro",
            "jax",
            "matplotlib",
        ),
        ("3.13",),
    ),
    "cc-guide": ("build/cc_guide", ("pytest",), (), ("3.13",)),
    "classification-codes": (
        "skills/classification-codes/scripts",
        ("pytest", "polars"),
        (),
        ("3.13",),
    ),
    "describe-critique-methodology": (
        "skills/describe-critique-methodology/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "design-architecture": (
        "skills/design-architecture/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "explore-data": (
        "skills/explore-data/scripts",
        ("pytest", "polars"),
        (),
        ("3.13",),
    ),
    "geographic-codes": (
        "skills/geographic-codes/scripts",
        ("pytest", "polars", "fastexcel"),
        (),
        ("3.13",),
    ),
    "hooks": (
        "hooks",
        ("pytest",),
        (),
        ("3.13", "/usr/bin/python3"),
    ),
    "llm-wiki": ("skills/llm-wiki/scripts", ("pytest",), (), ("3.13",)),
    "recommend-probabilistic-model": (
        "skills/recommend-probabilistic-model/scripts",
        ("pytest", "numpy", "polars"),
        (),
        ("3.13",),
    ),
    "recommend-visualization": (
        "skills/recommend-visualization/scripts",
        ("pytest", "numpy", "polars"),
        (),
        ("3.13",),
    ),
    "subagent-driven-development": (
        "skills/subagent-driven-development/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "systematic-debugging": (
        "skills/systematic-debugging",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "track-model-experiments": (
        "skills/track-model-experiments/scripts",
        ("pytest", "numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"),
        (),
        ("3.13",),
    ),
    "tune-hyperparameters": (
        "skills/tune-hyperparameters/scripts",
        ("pytest", "numpy", "polars"),
        ("scikit-learn", "optuna"),
        ("3.13",),
    ),
    "writing-plans": (
        "skills/writing-plans/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
}


def minimal_data():
    return {
        "suite": [
            {
                "name": "brainstorming",
                "dir": "skills/brainstorming/scripts",
                "with": ["pytest"],
            }
        ]
    }


def fixture_data():
    entries = []
    for name in ("build", "cc-guide", "hooks"):
        directory, deps, extras, pythons = EXPECTED[name]
        entry = {"name": name, "dir": directory, "with": list(deps)}
        if extras:
            entry["extras"] = list(extras)
        if name == "hooks":
            entry["pythons"] = list(pythons)
        entries.append(entry)
    entries[0]["notes"] = [
        "build/.scratch/ is missing in a fresh clone or worktree."
    ]
    entries[2]["notes"] = [
        "The guard has a 3.9 floor.",
        "launchd-PATH skips and the Gate B probe apply."
    ]
    return {"suite": entries}


def toml_value(value):
    if isinstance(value, dict):
        return "{ " + ", ".join(
            f"{json.dumps(key)} = {toml_value(item)}"
            for key, item in value.items()
        ) + " }"
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    return json.dumps(value)


def registry_text(data):
    lines = [
        f"{json.dumps(key)} = {toml_value(value)}"
        for key, value in data.items()
        if key != "suite"
    ]
    if "suite" in data:
        entries = data["suite"]
        if (
            isinstance(entries, list)
            and entries
            and all(isinstance(entry, dict) for entry in entries)
        ):
            for entry in entries:
                lines.append("[[suite]]")
                lines.extend(
                    f"{json.dumps(key)} = {toml_value(value)}"
                    for key, value in entry.items()
                )
        else:
            lines.append(f"suite = {toml_value(entries)}")
    return "\n".join(lines) + "\n"


def write_registry(root, data):
    path = root / "build/suites.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(registry_text(data), encoding="utf-8")


def write_file(root, relative, text="def test_example():\n    assert True\n"):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def materialize(root, data):
    root.mkdir(parents=True, exist_ok=True)
    write_registry(root, data)
    for entry in data["suite"]:
        write_file(root, str(Path(entry["dir"]) / "test_example.py"))
    return root


def unexpected_run(root, run):
    pytest.fail(f"Unexpected suite execution: {run.suite.name}, {run.python}")


def invoke(argv, root, run_one=unexpected_run):
    try:
        return runner.main(argv=argv, root=root, run_one=run_one)
    except SystemExit as exc:
        return 0 if exc.code is None else exc.code


def git_environment():
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    return env


def git(root, *args):
    return subprocess.run(
        ["git", *args],
        cwd=root,
        env=git_environment(),
        text=True,
        capture_output=True,
        check=True,
    )


def git_root(root):
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q")
    git(root, "config", "core.excludesFile", os.devnull)
    return root


def clone_repo(tmp_path):
    clone = tmp_path / "clone"
    git(tmp_path, "clone", "--quiet", "--no-hardlinks", str(ROOT), str(clone))
    return clone


def expected_argv(entry, python, extras=False, pytest_args=()):
    deps = list(entry["with"])
    if extras:
        deps.extend(entry.get("extras", []))
    argv = ["uv", "run", "--python", python]
    for dep in deps:
        argv.extend(["--with", dep])
    argv.extend(["python", "-m", "pytest", "-q", *pytest_args])
    return tuple(argv)


def invalid_registries():
    cases = []

    for key in ("name", "dir", "with"):
        data = minimal_data()
        del data["suite"][0][key]
        cases.append(pytest.param(data, id=f"missing-{key}"))

    wrong_values = [
        ("name", 13),
        ("name", ["brainstorming"]),
        ("dir", False),
        ("dir", ["skills/brainstorming/scripts"]),
        ("with", "pytest"),
        ("with", {"pytest": True}),
        ("with", ["pytest", 13]),
        ("with", ["pytest", False]),
        ("extras", "matplotlib"),
        ("extras", ["matplotlib", 13]),
        ("pythons", "3.13"),
        ("pythons", ["3.13", 13]),
        ("notes", "A note"),
        ("notes", ["A note", False]),
    ]
    for index, (key, value) in enumerate(wrong_values):
        data = minimal_data()
        data["suite"][0][key] = value
        cases.append(pytest.param(data, id=f"wrong-type-{key}-{index}"))

    data = minimal_data()
    data["suite"][0]["extra"] = ["matplotlib"]
    cases.append(pytest.param(data, id="unknown-suite-key"))

    data = minimal_data()
    data["suiet"] = []
    cases.append(pytest.param(data, id="unknown-root-key"))

    data = minimal_data()
    data["suite"][0]["with"] = ["numpy"]
    cases.append(pytest.param(data, id="missing-pytest"))

    data = minimal_data()
    duplicate = copy.deepcopy(data["suite"][0])
    duplicate["dir"] = "skills/writing-plans/scripts"
    data["suite"].append(duplicate)
    cases.append(pytest.param(data, id="duplicate-name"))

    data = minimal_data()
    duplicate = copy.deepcopy(data["suite"][0])
    duplicate["name"] = "writing-plans"
    data["suite"].append(duplicate)
    cases.append(pytest.param(data, id="duplicate-directory"))

    cases.extend([
        pytest.param({}, id="missing-suite-tables"),
        pytest.param({"suite": "brainstorming"}, id="suite-not-list"),
        pytest.param({"suite": ["brainstorming"]}, id="entry-not-table"),
    ])
    return cases


INVALID_REGISTRIES = invalid_registries()


def lint_commands(text):
    commands = []
    for line in text.replace("\\\n", " ").splitlines():
        match = re.match(r"^\s*run\s+([A-Za-z_][A-Za-z_0-9]*)\s+(.+)$", line)
        if match:
            commands.append(match.groups())
    return commands


# spec: "R3.1 Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_imports_only_standard_library_modules():
    tree = ast.parse(Path(runner.__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            imported.add(node.module.split(".")[0])
    assert imported <= sys.stdlib_module_names
    assert "tomllib" in imported


# spec: "Default `['3.13']`."
# task: 2
def test_omitted_pythons_default_to_python_313():
    suite = runner.parse(minimal_data())[0]
    assert runner.DEFAULT_PYTHONS == ("3.13",)
    assert suite.pythons == ("3.13",)
    assert [run.python for run in runner.runs(suite)] == ["3.13"]


# spec: "R2.2 Keys:"
# task: 2
def test_optional_registry_keys_have_empty_defaults():
    suite = runner.parse(minimal_data())[0]
    assert suite.name == "brainstorming"
    assert suite.dir == "skills/brainstorming/scripts"
    assert suite.deps == ("pytest",)
    assert suite.extras == ()
    assert suite.notes == ()


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
@pytest.mark.parametrize("data", INVALID_REGISTRIES)
def test_each_invalid_registry_is_rejected_by_validation(data):
    findings = runner.validate(data)
    assert findings
    assert all(isinstance(finding, str) and finding.strip() for finding in findings)


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
@pytest.mark.parametrize("data", INVALID_REGISTRIES)
@pytest.mark.parametrize("argv", [["--list"], ["brainstorming"], ["--all"]])
def test_invalid_registry_stops_every_execution_or_listing_mode(
    tmp_path, capsys, data, argv
):
    materialize(tmp_path, minimal_data())
    write_registry(tmp_path, data)
    assert invoke(argv, tmp_path) == 2
    output = capsys.readouterr()
    assert (output.out + output.err).strip()


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
@pytest.mark.parametrize("data", INVALID_REGISTRIES)
def test_check_reports_registry_validation_failures(tmp_path, data):
    git_root(tmp_path)
    materialize(tmp_path, minimal_data())
    write_registry(tmp_path, data)
    problems = runner.validate(data)
    findings = runner.check(tmp_path, data)
    assert findings
    for problem in problems:
        assert any(problem in finding for finding in findings)


# spec: "R4.3 Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
@pytest.mark.parametrize("data", INVALID_REGISTRIES)
def test_check_uses_exit_one_for_invalid_registry(tmp_path, capsys, data):
    git_root(tmp_path)
    materialize(tmp_path, minimal_data())
    write_registry(tmp_path, data)
    assert invoke(["--check"], tmp_path) == 1
    output = capsys.readouterr()
    assert (output.out + output.err).strip()
    assert "suite registry ok" not in output.out + output.err


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_argv_preserves_dependency_order():
    entry = fixture_data()["suite"][0]
    suite = runner.parse({"suite": [entry]})[0]
    runs = runner.runs(suite)
    assert len(runs) == 1
    assert runs[0].argv == expected_argv(entry, "3.13")
    assert runs[0].suite == suite


# spec: "R3.5 **`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
@pytest.mark.parametrize("extras", [False, True])
def test_extras_are_opt_in_and_follow_default_dependencies(extras):
    entry = fixture_data()["suite"][0]
    suite = runner.parse({"suite": [entry]})[0]
    run = runner.runs(suite, extras=extras)[0]
    assert run.argv == expected_argv(entry, "3.13", extras=extras)


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 2
def test_pytest_arguments_reach_every_interpreter_unchanged():
    entry = fixture_data()["suite"][2]
    args = ("test_example.py::test_example", "-k", "one or two", "-s", "-rs")
    suite = runner.parse({"suite": [entry]})[0]
    runs = runner.runs(suite, pytest_args=args)
    assert [run.python for run in runs] == ["3.13", "/usr/bin/python3"]
    assert [run.argv for run in runs] == [
        expected_argv(entry, python, pytest_args=args)
        for python in ("3.13", "/usr/bin/python3")
    ]


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_directory_dependencies_and_pytest_arguments():
    entry = {
        "name": "build",
        "dir": "suite directory/owner's tests",
        "with": ["pytest", "arviz>=1.0"],
        "extras": ["package[extra]"],
    }
    args = ("test_example.py::test_example", "-k", "one and not two", "$HOME")
    suite = runner.parse({"suite": [entry]})[0]
    run = runner.runs(suite, extras=True, pytest_args=args)[0]
    expected = expected_argv(entry, "3.13", extras=True, pytest_args=args)
    assert run.shell() == (
        f"cd {shlex.quote(entry['dir'])} && {shlex.join(expected)}"
    )
    words = shlex.split(run.shell())
    assert words[:3] == ["cd", entry["dir"], "&&"]
    assert tuple(words[3:]) == expected


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 2
def test_hooks_has_two_separate_shell_forms_in_interpreter_order():
    entry = fixture_data()["suite"][2]
    suite = runner.parse({"suite": [entry]})[0]
    runs = runner.runs(suite)
    assert [run.shell() for run in runs] == [
        "cd hooks && " + shlex.join(expected_argv(entry, python))
        for python in ("3.13", "/usr/bin/python3")
    ]


# spec: "R3.3 **`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
@pytest.mark.parametrize("names", [[], ["hooks", "build"]])
def test_list_shows_requested_suites_commands_extras_and_notes(
    tmp_path, capsys, names
):
    data = fixture_data()
    materialize(tmp_path, data)
    assert invoke(["--list", *names], tmp_path) == 0
    output = capsys.readouterr().out
    selected = [
        entry for entry in data["suite"]
        if not names or entry["name"] in names
    ]
    for entry in selected:
        assert entry["name"] in output
        assert entry["dir"] in output
        for dep in entry.get("extras", []):
            assert dep in output
        for note in entry.get("notes", []):
            assert note in output
        for python in entry.get("pythons", ["3.13"]):
            command = "cd " + shlex.quote(entry["dir"]) + " && "
            command += shlex.join(expected_argv(entry, python))
            assert command in output
    if names:
        excluded = next(
            entry for entry in data["suite"] if entry["name"] not in names
        )
        assert f"cd {excluded['dir']} && " not in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_applies_extras_and_pytest_arguments(tmp_path, capsys):
    data = fixture_data()
    materialize(tmp_path, data)
    args = ("-k", "one and not two", "-s", "-rs")
    assert invoke(
        ["--list", "build", "--extras", "--", *args], tmp_path
    ) == 0
    entry = data["suite"][0]
    expected = "cd build && " + shlex.join(
        expected_argv(entry, "3.13", extras=True, pytest_args=args)
    )
    assert expected in capsys.readouterr().out


# spec: "R3.4 **`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_suites_and_their_interpreters_run_in_requested_order(tmp_path):
    materialize(tmp_path, fixture_data())
    calls = []

    def run_one(root, run):
        calls.append((root, run.suite.name, run.python))
        return 0

    assert invoke(["hooks", "build", "cc-guide"], tmp_path, run_one) == 0
    assert calls == [
        (tmp_path, "hooks", "3.13"),
        (tmp_path, "hooks", "/usr/bin/python3"),
        (tmp_path, "build", "3.13"),
        (tmp_path, "cc-guide", "3.13"),
    ]


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_cli_forwards_extras_and_pytest_arguments_to_all_runs(tmp_path):
    data = fixture_data()
    materialize(tmp_path, data)
    calls = []
    args = ("test_example.py::test_example", "-k", "one or two", "-s", "-rs")

    def run_one(root, run):
        calls.append(run)
        return 0

    assert invoke(
        ["build", "hooks", "--extras", "--", *args], tmp_path, run_one
    ) == 0
    entries = {entry["name"]: entry for entry in data["suite"]}
    assert [run.argv for run in calls] == [
        expected_argv(entries[name], python, extras=True, pytest_args=args)
        for name, python in [
            ("build", "3.13"),
            ("hooks", "3.13"),
            ("hooks", "/usr/bin/python3"),
        ]
    ]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_print_before_execution_and_notes_print_once(
    tmp_path, capsys
):
    data = fixture_data()
    materialize(tmp_path, data)
    hooks = next(
        suite for suite in runner.parse(data) if suite.name == "hooks"
    )
    snapshots = []

    def run_one(root, run):
        snapshots.append(capsys.readouterr().out)
        return 0

    assert runner.execute(
        tmp_path, [hooks], False, (), run_one
    ) == 0
    assert snapshots[0].splitlines()[0] == "== hooks (3.13)"
    for note in hooks.notes:
        assert note in snapshots[0]
        assert snapshots[0].index(note) > snapshots[0].index("== hooks (3.13)")
        assert note not in snapshots[1]
    assert snapshots[1].splitlines()[0] == "== hooks (/usr/bin/python3)"


# spec: "A failed run does not stop the next one."
# task: 4
@pytest.mark.parametrize("failed_status", [1, 5, 87])
def test_execution_continues_through_every_run_after_failure(
    tmp_path, failed_status
):
    suites = runner.parse(fixture_data())
    ordered = [suites[2], suites[0], suites[1]]
    calls = []

    def run_one(root, run):
        calls.append((run.suite.name, run.python))
        return failed_status if len(calls) == 1 else 0

    assert runner.execute(
        tmp_path, ordered, False, (), run_one
    ) == 1
    assert calls == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("build", "3.13"),
        ("cc-guide", "3.13"),
    ]


# spec: "R3.7 **Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize(
    ("statuses", "expected_status"),
    [
        ([0, 0], 0),
        ([1, 0], 1),
        ([0, 1], 1),
        ([5, 0], 1),
        ([0, 5], 1),
        ([5, 5], 1),
    ],
)
def test_cli_aggregates_child_exit_statuses(tmp_path, statuses, expected_status):
    materialize(tmp_path, fixture_data())
    remaining = iter(statuses)

    def run_one(root, run):
        return next(remaining)

    assert invoke(["hooks"], tmp_path, run_one) == expected_status
    assert list(remaining) == []


# spec: "The last line names the failed runs, or says that every run passed."
# task: 4
def test_failure_summary_names_each_failed_run(tmp_path, capsys):
    materialize(tmp_path, fixture_data())
    statuses = iter([5, 0, 1])

    def run_one(root, run):
        return next(statuses)

    assert invoke(["hooks", "build"], tmp_path, run_one) == 1
    output = capsys.readouterr()
    last_line = (output.out + output.err).strip().splitlines()[-1]
    assert "hooks (3.13)" in last_line
    assert "build (3.13)" in last_line
    assert "hooks (/usr/bin/python3)" not in last_line


# spec: "The last line names the failed runs, or says that every run passed."
# task: 4
def test_success_summary_says_every_run_passed(tmp_path, capsys):
    materialize(tmp_path, fixture_data())
    assert invoke(["hooks", "build"], tmp_path, lambda root, run: 0) == 0
    output = capsys.readouterr()
    last_line = (output.out + output.err).strip().splitlines()[-1].lower()
    assert "pass" in last_line
    assert not re.search(r"\bfail(?:ed|ure|ures)?\b", last_line)


# spec: "R3.7 **Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize(
    "argv",
    [
        ["not-a-registered-suite"],
        ["--list", "not-a-registered-suite"],
        ["--not-a-runner-option"],
    ],
)
def test_unknown_suite_and_usage_errors_exit_two(tmp_path, capsys, argv):
    materialize(tmp_path, fixture_data())
    assert invoke(argv, tmp_path) == 2
    output = capsys.readouterr()
    assert (output.out + output.err).strip()


# spec: "R3.6 **`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_uses_directory_ancestry_and_does_not_contain_itself():
    data = fixture_data()
    data["suite"].append({
        "name": "writing-plans",
        "dir": "build-extra",
        "with": ["pytest"],
    })
    suites = runner.parse(data)
    by_name = {suite.name: suite for suite in suites}
    assert runner.container(by_name["cc-guide"], suites) == by_name["build"]
    assert runner.container(by_name["build"], suites) is None
    assert runner.container(by_name["hooks"], suites) is None
    assert runner.container(by_name["writing-plans"], suites) is None


# spec: "R3.6 **`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_skips_nested_suites_using_paths_not_suite_names(tmp_path, capsys):
    data = fixture_data()
    data["suite"].extend([
        {
            "name": "brainstorming",
            "dir": "hooks/nested",
            "with": ["pytest"],
        },
        {
            "name": "writing-plans",
            "dir": "build-extra",
            "with": ["pytest"],
        },
    ])
    materialize(tmp_path, data)
    calls = []

    def run_one(root, run):
        calls.append((run.suite.name, run.python))
        return 0

    assert invoke(["--all"], tmp_path, run_one) == 0
    assert sorted(calls) == sorted([
        ("build", "3.13"),
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("writing-plans", "3.13"),
    ])
    output = capsys.readouterr().out
    for name, directory in [
        ("cc-guide", "build/cc_guide"),
        ("brainstorming", "hooks/nested"),
    ]:
        matching_lines = [
            line for line in output.splitlines()
            if name in line and directory in line
        ]
        assert len(matching_lines) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_named_nested_suite_runs(tmp_path):
    materialize(tmp_path, fixture_data())
    calls = []

    def run_one(root, run):
        calls.append((run.suite.name, run.python))
        return 0

    assert invoke(["cc-guide"], tmp_path, run_one) == 0
    assert calls == [("cc-guide", "3.13")]


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 4
def test_subprocess_uses_suite_directory_and_streams_output(
    tmp_path, monkeypatch
):
    entry = fixture_data()["suite"][0]
    run = runner.runs(runner.parse({"suite": [entry]})[0])[0]
    calls = []

    def fake_subprocess(argv, *args, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(runner.subprocess, "run", fake_subprocess)
    assert runner.run_subprocess(tmp_path, run) == 0
    assert len(calls) == 1
    argv, kwargs = calls[0]
    assert tuple(argv) == expected_argv(entry, "3.13")
    assert Path(kwargs["cwd"]) == tmp_path / entry["dir"]
    assert not kwargs.get("capture_output", False)
    assert kwargs.get("stdout") is None
    assert kwargs.get("stderr") is None
    assert not kwargs.get("shell", False)


# spec: "R3.8 The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_inherits_the_environment_unchanged(tmp_path, monkeypatch):
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("LLM_WIKI_ROOT", str(tmp_path / "wiki"))
    before = dict(os.environ)
    observed = []
    suite = runner.parse(fixture_data())[2]

    def fake_subprocess(argv, *args, **kwargs):
        env = kwargs.get("env")
        observed.append(dict(os.environ) if env is None else dict(env))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(runner.subprocess, "run", fake_subprocess)
    for run in runner.runs(suite):
        assert runner.run_subprocess(tmp_path, run) == 0
    assert observed == [before, before]
    assert dict(os.environ) == before


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_is_a_failure_and_does_not_stop_later_runs(
    tmp_path, capsys, monkeypatch
):
    materialize(tmp_path, fixture_data())
    calls = []

    def fake_subprocess(argv, *args, **kwargs):
        calls.append(tuple(argv))
        if len(calls) == 1:
            raise FileNotFoundError("uv")
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(runner.subprocess, "run", fake_subprocess)
    assert invoke(["hooks"], tmp_path, runner.run_subprocess) == 1
    assert len(calls) == 2
    output = capsys.readouterr()
    last_line = (output.out + output.err).strip().splitlines()[-1]
    assert "hooks (3.13)" in last_line
    assert "hooks (/usr/bin/python3)" not in last_line


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_listing_from_an_unrelated_working_directory_uses_the_real_registry(
    tmp_path
):
    assert runner.REPO == ROOT
    assert runner.REGISTRY == "build/suites.toml"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "build/run_suites.py"),
            "--list",
            "brainstorming",
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "skills/brainstorming/scripts" in result.stdout
    assert (
        "cd skills/brainstorming/scripts && "
        "uv run --python 3.13 --with pytest python -m pytest -q"
    ) in result.stdout


# spec: "R4.1 `--check` reports two kinds of findings:"
# task: 3
@pytest.mark.parametrize("kind", ["missing-directory", "directory-without-tests"])
def test_check_rejects_missing_or_testless_registered_directory(tmp_path, kind):
    git_root(tmp_path)
    data = minimal_data()
    write_registry(tmp_path, data)
    directory = data["suite"][0]["dir"]
    if kind == "directory-without-tests":
        write_file(tmp_path, f"{directory}/support.py", "VALUE = 1\n")
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert directory in findings[0]
    assert "\n" not in findings[0]


# spec: "R4.1 `--check` reports two kinds of findings:"
# task: 3
@pytest.mark.parametrize("tracked", [False, True])
def test_check_reports_unregistered_tracked_and_untracked_test_directories(
    tmp_path, tracked
):
    git_root(tmp_path)
    data = minimal_data()
    materialize(tmp_path, data)
    uncovered = "skills/writing-plans/scripts"
    write_file(tmp_path, f"{uncovered}/test_new.py")
    if tracked:
        git(tmp_path, "add", ".")
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert uncovered in findings[0]


# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize(
    ("filename", "is_test"),
    [
        ("test_new.py", True),
        ("new_test.py", True),
        ("test_.py", True),
        ("_test.py", True),
        ("test.py", False),
        ("testing.py", False),
        ("new_tests.py", False),
        ("test_new.txt", False),
    ],
)
def test_coverage_uses_both_pytest_default_filename_patterns(
    tmp_path, filename, is_test
):
    git_root(tmp_path)
    data = minimal_data()
    materialize(tmp_path, data)
    write_file(tmp_path, f"new-suite/{filename}")
    findings = runner.check(tmp_path, data)
    assert len(findings) == int(is_test)
    if is_test:
        assert "new-suite" in findings[0]


# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_registered_directory_covers_tests_in_descendants(tmp_path):
    git_root(tmp_path)
    data = {"suite": [{"name": "build", "dir": "build", "with": ["pytest"]}]}
    write_registry(tmp_path, data)
    write_file(tmp_path, "build/cc_guide/nested/test_new.py")
    assert runner.check(tmp_path, data) == []


# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_coverage_does_not_treat_a_shared_path_prefix_as_containment(tmp_path):
    git_root(tmp_path)
    data = {"suite": [{"name": "build", "dir": "build", "with": ["pytest"]}]}
    materialize(tmp_path, data)
    write_file(tmp_path, "build-extra/test_new.py")
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert "build-extra" in findings[0]


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_ignored_test_trees_do_not_create_findings(tmp_path):
    git_root(tmp_path)
    data = minimal_data()
    materialize(tmp_path, data)
    write_file(
        tmp_path,
        ".gitignore",
        ".claude/worktrees/\nbuild/.scratch/\nignored-suite/\n",
    )
    for directory in (
        ".claude/worktrees/session",
        "build/.scratch/probe",
        "ignored-suite",
    ):
        write_file(tmp_path, f"{directory}/test_new.py")
    assert runner.check(tmp_path, data) == []


# spec: "The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root."
# task: 3
def test_pytest_directory_inventory_includes_cached_and_untracked_files(
    tmp_path, monkeypatch
):
    git_root(tmp_path)
    write_file(tmp_path, "tracked/test_one.py")
    git(tmp_path, "add", "tracked/test_one.py")
    write_file(tmp_path, "untracked/two_test.py")
    write_file(tmp_path, ".gitignore", "ignored/\n")
    write_file(tmp_path, "ignored/test_three.py")
    actual_run = subprocess.run
    calls = []

    def record(argv, *args, **kwargs):
        calls.append((tuple(argv), kwargs))
        return actual_run(argv, *args, **kwargs)

    monkeypatch.setattr(runner.subprocess, "run", record)
    assert runner.pytest_dirs(tmp_path) == {"tracked", "untracked"}
    git_calls = [
        (argv, kwargs)
        for argv, kwargs in calls
        if argv[:2] == ("git", "ls-files")
    ]
    assert len(git_calls) == 1
    argv, kwargs = git_calls[0]
    assert {"--cached", "--others", "--exclude-standard"} <= set(argv)
    assert Path(kwargs["cwd"]) == tmp_path


# spec: "If git fails, `--check` fails."
# task: 4
@pytest.mark.parametrize("cannot_start", [False, True])
def test_git_failure_makes_check_fail(
    tmp_path, capsys, monkeypatch, cannot_start
):
    materialize(tmp_path, minimal_data())

    def failed_git(argv, *args, **kwargs):
        if cannot_start:
            raise FileNotFoundError("git")
        return subprocess.CompletedProcess(
            argv, 128, stdout="", stderr="git failed"
        )

    monkeypatch.setattr(runner.subprocess, "run", failed_git)
    assert invoke(["--check"], tmp_path) == 1
    output = capsys.readouterr()
    assert (output.out + output.err).strip()
    assert "suite registry ok" not in output.out + output.err


# spec: "R4.3 Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_clean_check_prints_the_required_success_line(tmp_path, capsys):
    git_root(tmp_path)
    materialize(tmp_path, fixture_data())
    assert invoke(["--check"], tmp_path) == 0
    output = capsys.readouterr()
    assert output.out.strip() == "suite registry ok"
    assert output.err == ""


# spec: "R4.3 Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_prints_one_line_for_each_finding(tmp_path, capsys):
    git_root(tmp_path)
    data = minimal_data()
    materialize(tmp_path, data)
    directories = ["new-suite-one", "new-suite-two"]
    for directory in directories:
        write_file(tmp_path, f"{directory}/test_new.py")
    assert invoke(["--check"], tmp_path) == 1
    output = capsys.readouterr()
    lines = (output.out + output.err).strip().splitlines()
    assert len(lines) == 2
    for directory in directories:
        assert sum(directory in line for line in lines) == 1


# spec: "R2.1 One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_has_unique_sorted_suite_tables():
    data = tomllib.loads(
        (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    )
    assert runner.validate(data) == []
    entries = data["suite"]
    names = [entry["name"] for entry in entries]
    directories = [entry["dir"] for entry in entries]
    assert names == sorted(names)
    assert len(names) == len(set(names))
    assert len(directories) == len(set(directories))


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_documents_keys_sorting_and_ninth_lint():
    text = (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    header = text.split("[[suite]]", 1)[0]
    comments = "\n".join(
        line.lstrip()[1:] for line in header.splitlines()
        if line.lstrip().startswith("#")
    )
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert re.search(rf"\b{key}\b", comments)
    assert re.search(r"sort", comments, re.IGNORECASE)
    assert re.search(r"\b(?:ninth|nine|9th|9)\b", comments, re.IGNORECASE)
    assert re.search(r"commit", comments, re.IGNORECASE)
    assert re.search(r"lint", comments, re.IGNORECASE)


# spec: "R2.3 The entries carry the text of today's commands and comments."
# task: 5
@pytest.mark.parametrize("name", list(EXPECTED))
def test_real_registry_preserves_the_specified_suite_inventory(name):
    data = tomllib.loads(
        (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    )
    suites = {suite.name: suite for suite in runner.parse(data)}
    assert name in suites
    suite = suites[name]
    directory, deps, extras, pythons = EXPECTED[name]
    assert suite.dir == directory
    assert suite.deps == deps
    assert suite.extras == extras
    assert suite.pythons == pythons


# spec: "The notes carry the rest of each comment."
# task: 5
def test_real_registry_retains_the_explicitly_named_note_details():
    data = tomllib.loads(
        (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    )
    notes = {
        suite.name: "\n".join(suite.notes)
        for suite in runner.parse(data)
    }
    for name, token in [
        ("build", ".scratch/"),
        ("bayesian-workflow", "CALIBRATION_SWEEP=1"),
        ("bayesian-workflow", "arviz"),
        ("llm-wiki", "@needs_pilot"),
        ("llm-wiki", "$LLM_WIKI_ROOT"),
        ("brainstorming", "node"),
        ("tune-hyperparameters", "--with sklearn"),
        ("hooks", "3.9"),
        ("hooks", "launchd"),
        ("hooks", "PATH"),
        ("hooks", "Gate B"),
    ]:
        assert token.lower() in notes[name].lower()
    assert "warn" in notes["bayesian-workflow"].lower()
    assert notes["track-model-experiments"].strip()


# spec: "1. `build/suites.toml` registers every directory suite (R2.3) and `--check` passes."
# task: 5
def test_real_registry_passes_coverage_check(capsys):
    data = tomllib.loads(
        (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    )
    assert runner.check(ROOT, data) == []
    assert invoke(["--check"], ROOT) == 0
    output = capsys.readouterr()
    assert output.out.strip() == "suite registry ok"
    assert output.err == ""


# spec: "R4.4 `build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_suite_registry_is_the_ninth_literal_commit_lint():
    text = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    commands = lint_commands(text)
    assert len(commands) == 9
    name, command = commands[-1]
    assert name == "suite_registry"
    assert shlex.split(command) == [
        "uv", "run", "--python", "3.13", "python",
        "build/run_suites.py", "--check",
    ]
    assert sum(name == "suite_registry" for name, _ in commands) == 1
    comments = "\n".join(
        line for line in text.splitlines() if line.lstrip().startswith("#")
    )
    assert re.search(r"\bnine\b", comments, re.IGNORECASE)


# spec: "R6.2 `build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_check_inventory_includes_suite_registry():
    tree = ast.parse(
        (ROOT / "build/test_commit_lints.py").read_text(encoding="utf-8")
    )
    assignments = [
        node for node in ast.walk(tree)
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "CHECKS"
                for target in node.targets
            )
        ) or (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "CHECKS"
        )
    ]
    assert assignments
    assert any(
        isinstance(node, ast.Constant) and node.value == "suite_registry"
        for assignment in assignments
        for node in ast.walk(assignment.value)
    )
    assert any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "test_unregistered_suite_is_refused"
        for node in ast.walk(tree)
    )


# spec: "R6.2 `build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_committed_unregistered_suite_fails_only_the_registry_lint(tmp_path):
    clone = clone_repo(tmp_path)
    new_file = "skills/acceptance-unregistered/scripts/test_new.py"
    write_file(clone, new_file)
    git(clone, "add", new_file)
    git(
        clone,
        "-c", "user.name=Acceptance Test",
        "-c", "user.email=acceptance@example.invalid",
        "-c", "commit.gpgSign=false",
        "-c", f"core.hooksPath={os.devnull}",
        "commit", "--quiet", "-m", "Add an unregistered test suite",
    )
    commands = lint_commands(
        (clone / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    )
    assert len(commands) == 9
    results = {}
    for name, command in commands:
        results[name] = subprocess.run(
            ["bash", "-c", command],
            cwd=clone,
            env=git_environment(),
            text=True,
            capture_output=True,
        )
    failures = {
        name: result.stdout + result.stderr
        for name, result in results.items()
        if result.returncode != 0
    }
    assert set(failures) == {"suite_registry"}, failures
    assert results["suite_registry"].returncode == 1
    assert "skills/acceptance-unregistered/scripts" in failures["suite_registry"]


# spec: "R5.3 `build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_documentation_describes_the_ninth_registry_lint():
    text = (ROOT / "build/CLAUDE.md").read_text(encoding="utf-8")
    assert "the eight commit lints" not in text
    assert "the nine commit lints" in text
    paragraphs = re.split(r"\n\s*\n", text)
    assert any(
        all(token in paragraph for token in (
            "suites.toml", "run_suites.py", "--check", "commit lint"
        ))
        for paragraph in paragraphs
    )


# spec: "The file ends at about 145 lines."
# task: 7
def test_root_claude_md_stays_under_the_200_line_limit():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_runner_documentation_does_not_claim_a_suite_or_test_count():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    runner_lines = [
        line for line in text.splitlines()
        if "suites.toml" in line or "run_suites.py" in line
    ]
    assert runner_lines
    for line in runner_lines:
        assert not re.search(r"\b\d+\s+(?:suites?|tests?)\b", line)


# spec: "Rewrite the intro paragraph."
# task: 7
def test_root_commands_intro_retains_the_required_guidance():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    lines = [
        line for line in text.splitlines()
        if "test_build.py" in line
        and "suites.toml" in line
        and "run_suites.py" in line
    ]
    assert len(lines) == 1
    intro = lines[0]
    assert "uv" in intro
    assert "3.13" in intro
    assert re.search(r"director", intro, re.IGNORECASE)
    assert re.search(r"collis", intro, re.IGNORECASE)
    assert re.search(r"notes?", intro, re.IGNORECASE)
    assert re.search(r"before", intro, re.IGNORECASE)
    assert "There is no root test runner" not in text


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_commands_block_contains_the_four_runner_commands_in_order():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    prefix = "uv run --python 3.13 python build/run_suites.py"
    expected = [
        f"{prefix} --list",
        f"{prefix} <name> [--extras] [-- <pytest args>]",
        f"{prefix} --all",
        f"{prefix} --check",
    ]
    start = lines.index(expected[0])
    assert lines[start - 1].startswith("#")
    assert lines[start:start + len(expected)] == expected


# spec: "4. `CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_documentation_has_no_literal_directory_suite_command():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    for directory, deps, extras, pythons in EXPECTED.values():
        entry = {"dir": directory, "with": list(deps)}
        for python in pythons:
            old_command = (
                "cd " + shlex.quote(directory) + " && "
                + shlex.join(expected_argv(entry, python))
            )
            assert old_command not in text


# spec: "R1.2 These commands **stay literal in `CLAUDE.md`**."
# task: 7
@pytest.mark.parametrize(
    "token",
    [
        "test_runtime_support.py",
        "test_commit_lints.py",
        "-k declared_dependencies",
        "-k test_real_skill",
        "test_check_jax_examples.py",
        "verify_citations.py",
        "extract_structure.py",
        "cli.py lint",
        "cli.py check",
    ],
)
def test_named_selection_and_tool_commands_remain_literal(token):
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    command_lines = [
        line.strip()
        for line in text.replace("\\\n", " ").splitlines()
        if line.lstrip().startswith(("uv ", "python ", "bash ", "cd "))
    ]
    assert any(token in line for line in command_lines)


# spec: "The commit-lint comment names the suite-registry check and says \"nine\"."
# task: 7
def test_root_commit_lint_comment_names_the_ninth_check():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    comments = [
        line for line in text.splitlines() if line.lstrip().startswith("#")
    ]
    assert any(
        re.search(r"\bnine\b", line, re.IGNORECASE)
        and (
            "suite_registry" in line
            or re.search(r"suite[- ]registry", line, re.IGNORECASE)
        )
        for line in comments
    )


# spec: "The comment names the suite `run_suites.py cc-guide` instead of \"its suite\"."
# task: 7
def test_cc_guide_comment_uses_the_specified_public_suite_name():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert any(
        "run_suites.py cc-guide" in line
        for line in text.splitlines()
        if line.lstrip().startswith("#")
    )


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_accepts_a_changed_stamp_version(tmp_path):
    clone = clone_repo(tmp_path)
    path = clone / "CLAUDE.md"
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    match = re.fullmatch(
        r"(<!-- cc-guide: .* @)([^\s]+)( -->)(\r?\n)?",
        lines[0],
    )
    assert match is not None
    version = match.group(2)
    replacement = "0" if version[-1] != "0" else "1"
    changed_version = version[:-1] + replacement
    lines[0] = (
        match.group(1)
        + changed_version
        + match.group(3)
        + (match.group(4) or "")
    )
    path.write_text("".join(lines), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            (
                "build/test_check_conformance.py::"
                "test_claude_md_import_resolves_passes_on_the_repo"
            ),
        ],
        cwd=clone,
        env=git_environment(),
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


# spec: "5. `bash build/run_commit_lints.sh` prints `commit lints passed`."
# task: 6
def test_complete_commit_lint_gate_passes():
    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "commit lints passed" in result.stdout
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>the base facts that Tasks 5 and 7 check against, and a spec that names the suite `cc_guide`.</plan></flag>
<flag task="2"><spec>Default `['3.13']`.</spec><plan>DEFAULT_PYTHONS = ('3.12',)</plan></flag>
<flag task="5"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>`cc_guide`</plan></flag>
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
Worktree-isolated sessions and their subagents have refused compound shell such as `cd X && Y` (seen on 2026-10-12).
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
"This work lands whole, registry and CLAUDE.md shrink, ahead of plan 52's Task 6.
Task 6 then adds one build/suites.toml entry instead of editing Commands.
Plan 52's planning session amends its plan to match and records Q4 as (c)."
An `@`-imported document was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
**Design section 1** (the registry keys and the runner's behaviour) was approved as presented.
**Design section 2** (the guard, the file edits, the tests and the couplings) was approved as presented.
R1.3 `build/run_commit_lints.sh` keeps its literal commands.
Every command, dependency and note survives; the only change is the form.
Examples: `build`'s missing `build/.scratch/` in a fresh clone or worktree; `bayesian-workflow`'s `CALIBRATION_SWEEP=1` sweep and its expected arviz warnings; `llm-wiki`'s `@needs_pilot` tests and `$LLM_WIKI_ROOT`; `brainstorming`'s node skip; `tune-hyperparameters`' "`--with sklearn` fails"; `track-model-experiments`' run time; the guard's 3.9 floor, its launchd-PATH skips and its Gate B probe for `hooks`.
With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character.
Same number of lines.
Line 133 is not touched (plan 53's Task 7 edits it).
R5.2 The deletion of lines 66–125 is bounded by two lines that no other plan edits: the `# Full build-directory tests` comment and the `cd hooks && …` command.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
R5.5 No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
The new files are the owner's original tooling.
The register's deviation `claude-md-serves-codex-gemini` still holds as written: a condensed Commands block stays in the root file, and the registry is a plain file that every runtime can read.
R6.3 Write each test before its code and see it fail first (red, then green).
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
**R6's tests** run red first, then green.
Run it before the `CLAUDE.md` deletion.
It extracts every `cd <dir> && uv run …` command from lines 66–125 and 145, splitting the hooks `&&` chain into one command per run.
It asserts that the set equals the set of default shell forms that `--list` prints: nothing is missing on either side.
It also checks each comment's skip-unlocking deps against that suite's `extras`.
Run `hooks`, `build` and `bayesian-workflow` once directly and once through the runner, in the same checkout.
Their pytest summary lines match.
Then run `--all` once, and record each run's result beside the direct result.
The build suite passes (where the missing `build/.scratch/` lets it).
3. The Stage 2 audit passes, and the behaviour runs match.
6. The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
It would need node, a 3.9 `/usr/bin/python3` and `build/.scratch/`.
Revisit if: the owner wants suites in CI.
Revisit if: `--all` gets slow or a tool needs to parse its results.
Revisit if: `CLAUDE.md` nears its limit again.
</untestable>