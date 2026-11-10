<tests>
import argparse
import ast
import copy
import json
import os
import re
import runpy
import shlex
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

try:
    import run_suites as runner
except ModuleNotFoundError as exc:
    if exc.name != "run_suites":
        raise
    from build import run_suites as runner


ROOT = Path(runner.__file__).resolve().parent.parent

# name, directory, dependencies after pytest, extras, interpreters
INVENTORY = (
    (
        "bayesian-workflow",
        "skills/bayesian-workflow/scripts",
        ("arviz", "arviz-stats", "numpy", "xarray"),
        ("matplotlib",),
        ("3.13",),
    ),
    ("brainstorming", "skills/brainstorming/scripts", (), (), ("3.13",)),
    (
        "build",
        "build",
        ("numpy", "polars", "pyyaml"),
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
    ("cc-guide", "build/cc_guide", (), (), ("3.13",)),
    (
        "classification-codes",
        "skills/classification-codes/scripts",
        ("polars",),
        (),
        ("3.13",),
    ),
    (
        "describe-critique-methodology",
        "skills/describe-critique-methodology/scripts",
        (),
        (),
        ("3.13",),
    ),
    (
        "design-architecture",
        "skills/design-architecture/scripts",
        (),
        (),
        ("3.13",),
    ),
    ("explore-data", "skills/explore-data/scripts", ("polars",), (), ("3.13",)),
    (
        "geographic-codes",
        "skills/geographic-codes/scripts",
        ("polars", "fastexcel"),
        (),
        ("3.13",),
    ),
    ("hooks", "hooks", (), (), ("3.13", "/usr/bin/python3")),
    ("llm-wiki", "skills/llm-wiki/scripts", (), (), ("3.13",)),
    (
        "recommend-probabilistic-model",
        "skills/recommend-probabilistic-model/scripts",
        ("numpy", "polars"),
        (),
        ("3.13",),
    ),
    (
        "recommend-visualization",
        "skills/recommend-visualization/scripts",
        ("numpy", "polars"),
        (),
        ("3.13",),
    ),
    (
        "subagent-driven-development",
        "skills/subagent-driven-development/scripts",
        (),
        (),
        ("3.13",),
    ),
    (
        "systematic-debugging",
        "skills/systematic-debugging",
        (),
        (),
        ("3.13",),
    ),
    (
        "track-model-experiments",
        "skills/track-model-experiments/scripts",
        ("numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"),
        (),
        ("3.13",),
    ),
    (
        "tune-hyperparameters",
        "skills/tune-hyperparameters/scripts",
        ("numpy", "polars"),
        ("scikit-learn", "optuna"),
        ("3.13",),
    ),
    ("writing-plans", "skills/writing-plans/scripts", (), (), ("3.13",)),
)
ROWS = {row[0]: row for row in INVENTORY}


def registry_data(names=("build", "cc-guide", "hooks")):
    entries = []
    for name in names:
        _, directory, deps, extras, pythons = ROWS[name]
        entry = {
            "name": name,
            "dir": directory,
            "with": ["pytest", *deps],
        }
        if extras:
            entry["extras"] = list(extras)
        if pythons != ("3.13",):
            entry["pythons"] = list(pythons)
        if name == "build":
            entry["notes"] = ["build/.scratch/"]
        elif name == "hooks":
            entry["notes"] = ["3.9", "launchd-PATH", "Gate B"]
        entries.append(entry)
    return {"suite": entries}


def toml_value(value):
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{ " + ", ".join(
            f"{key} = {toml_value(item)}" for key, item in value.items()
        ) + " }"
    raise TypeError(value)


def write_registry(root, data):
    root.mkdir(parents=True, exist_ok=True)
    path = root / "build/suites.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(f"{key} = {toml_value(value)}" for key, value in data.items())
        + "\n",
        encoding="utf-8",
    )
    return path


def main_status(root, argv, run_one):
    try:
        return runner.main(argv, root=root, run_one=run_one)
    except SystemExit as exc:
        return exc.code


def forbid_run(root, run):
    pytest.fail(f"Unexpected suite execution: {run.label}")


def expected_argv(entry, python, extras=False, pytest_args=()):
    argv = ["uv", "run", "--python", python]
    deps = entry["with"] + (entry.get("extras", []) if extras else [])
    for dep in deps:
        argv.extend(("--with", dep))
    argv.extend(("python", "-m", "pytest", "-q"))
    argv.extend(pytest_args)
    return tuple(argv)


def expected_shell(entry, python, extras=False, pytest_args=()):
    return (
        f"cd {shlex.quote(entry['dir'])} && "
        + shlex.join(expected_argv(entry, python, extras, pytest_args))
    )


def invalid_registries():
    cases = []

    data = registry_data()
    data["suite"][0]["extra"] = ["matplotlib"]
    cases.append(("unknown-suite-key", data))

    data = registry_data()
    data["suiet"] = []
    cases.append(("unknown-top-level-key", data))

    for key in ("name", "dir", "with"):
        data = registry_data()
        del data["suite"][0][key]
        cases.append((f"missing-{key}", data))

    for key, value in (
        ("name", 13),
        ("dir", False),
        ("with", "pytest"),
        ("with", ["pytest", 13]),
        ("extras", "matplotlib"),
        ("extras", [False]),
        ("pythons", "3.13"),
        ("pythons", [3.13]),
        ("notes", "build/.scratch/"),
        ("notes", [13]),
    ):
        data = registry_data()
        data["suite"][0][key] = value
        cases.append((f"wrong-type-{key}-{len(cases)}", data))

    for value in ("hooks", {}):
        data = registry_data()
        data["suite"] = value
        cases.append((f"wrong-suite-container-{len(cases)}", data))

    data = registry_data()
    data["suite"][2]["name"] = data["suite"][0]["name"]
    cases.append(("duplicate-name", data))

    data = registry_data()
    data["suite"][2]["dir"] = data["suite"][0]["dir"]
    cases.append(("duplicate-directory", data))

    data = registry_data()
    data["suite"][0]["with"] = ["numpy", "polars", "pyyaml"]
    cases.append(("missing-pytest", data))
    return cases


INVALID = invalid_registries()


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def git_repo(root, data=None, files=None):
    if data is None:
        data = registry_data()
    write_registry(root, data)
    if files is None:
        files = {
            "build/test_new.py": "",
            "build/cc_guide/test_new.py": "",
            "hooks/test_new.py": "",
        }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git(root, "init", "-q")
    git(root, "config", "user.name", "Acceptance tests")
    git(root, "config", "user.email", "acceptance@example.invalid")
    git(root, "add", ".")
    return data


def last_line(captured):
    return (captured.out + captured.err).strip().splitlines()[-1]


def lint_commands(script):
    commands = []
    for line in script.replace("\\\n", " ").splitlines():
        if line.lstrip().startswith("run "):
            words = shlex.split(line, comments=True)
            commands.append((words[1], words[2:]))
    return commands


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 2
def test_repo_and_registry_locations():
    assert runner.REPO == ROOT
    assert runner.REGISTRY == "build/suites.toml"


# spec: "The interpreters, one run each, in order."
# task: 2
def test_optional_fields_default_to_empty_and_python_313():
    data = {
        "suite": [{
            "name": "brainstorming",
            "dir": "skills/brainstorming/scripts",
            "with": ["pytest"],
        }]
    }
    assert runner.validate(data) == []
    suite, = runner.parse(data)
    assert suite.deps == ("pytest",)
    assert suite.extras == ()
    assert suite.pythons == ("3.13",)
    assert suite.notes == ()
    assert runner.DEFAULT_PYTHONS == ("3.13",)


@pytest.mark.parametrize("case,data", INVALID, ids=[case for case, _ in INVALID])
@pytest.mark.parametrize("argv", [["--list"], ["build"], ["--all"]])
# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_invalid_registry_stops_every_execution_mode(tmp_path, case, data, argv):
    data = copy.deepcopy(data)
    assert runner.validate(data)
    write_registry(tmp_path, data)
    assert main_status(tmp_path, argv, forbid_run) == 2


@pytest.mark.parametrize("case,data", INVALID, ids=[case for case, _ in INVALID])
# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 4
def test_invalid_registry_is_a_check_finding(tmp_path, capsys, case, data):
    data = copy.deepcopy(data)
    git_repo(tmp_path, data)
    findings = runner.check(tmp_path, data)
    assert findings
    assert len(findings) >= len(runner.validate(data))
    assert all(line and "\n" not in line for line in findings)
    assert main_status(tmp_path, ["--check"], forbid_run) == 1
    captured = capsys.readouterr()
    assert "suite registry ok" not in captured.out
    assert (captured.out + captured.err).strip()


@pytest.mark.parametrize(
    "argv,expected",
    [
        (["--list"], 2),
        (["build"], 2),
        (["--all"], 2),
        (["--check"], 1),
    ],
)
# spec: "Validation fails closed."
# task: 4
def test_malformed_toml_is_refused(tmp_path, argv, expected):
    path = write_registry(tmp_path, registry_data())
    path.write_text("[[suite]\n", encoding="utf-8")
    assert main_status(tmp_path, argv, forbid_run) == expected


@pytest.mark.parametrize("row", INVENTORY, ids=[row[0] for row in INVENTORY])
# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_commands_and_shell_forms(row):
    name, _, _, _, pythons = row
    entry = registry_data((name,))["suite"][0]
    suite, = runner.parse({"suite": [entry]})
    runs = runner.runs(suite)
    assert len(runs) == len(pythons)
    for run, python in zip(runs, pythons):
        assert run.suite == suite
        assert run.python == python
        assert run.argv == expected_argv(entry, python)
        assert run.shell() == expected_shell(entry, python)
        assert run.label == f"{name} ({python})"


@pytest.mark.parametrize("extras", [False, True])
# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_follow_default_dependencies_and_pytest_arguments_follow_q(extras):
    entry = registry_data(("build",))["suite"][0]
    suite, = runner.parse({"suite": [entry]})
    args = ("test_new.py", "-k", "declared_dependencies", "-s", "-rs")
    run, = runner.runs(suite, extras=extras, pytest_args=args)
    assert run.argv == expected_argv(entry, "3.13", extras, args)
    assert run.shell() == expected_shell(entry, "3.13", extras, args)


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_quotes_directories_dependencies_and_arguments():
    suite = runner.Suite(
        name="build",
        dir="build with spaces",
        deps=("pytest",),
        extras=("arviz>=1.0",),
    )
    args = ("-k", "declared_dependencies or test_real_skill", "test_new.py")
    entry = {
        "dir": suite.dir,
        "with": ["pytest"],
        "extras": ["arviz>=1.0"],
    }
    run, = runner.runs(suite, extras=True, pytest_args=args)
    assert run.shell() == expected_shell(entry, "3.13", True, args)
    assert "'build with spaces'" in run.shell()
    assert "'arviz>=1.0'" in run.shell()
    assert "'declared_dependencies or test_real_skill'" in run.shell()


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_parse_args_preserves_pytest_tail():
    tail = ("test_new.py::test_new", "-k", "declared_dependencies", "-s", "-rs")
    namespace, pytest_args = runner.parse_args(["hooks", "--", *tail])
    assert isinstance(namespace, argparse.Namespace)
    assert pytest_args == tail


@pytest.mark.parametrize("selected", [(), ("hooks", "build")])
# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_prints_suite_details_without_running(tmp_path, capsys, selected):
    data = registry_data()
    write_registry(tmp_path, data)
    assert main_status(tmp_path, ["--list", *selected], forbid_run) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    entries = {entry["name"]: entry for entry in data["suite"]}
    for name in selected or tuple(entries):
        entry = entries[name]
        assert name in captured.out
        assert entry["dir"] in captured.out
        for python in entry.get("pythons", ["3.13"]):
            assert expected_shell(entry, python) in captured.out
        for extra in entry.get("extras", []):
            assert extra in captured.out
        for note in entry.get("notes", []):
            assert note in captured.out
    if selected:
        assert "cc-guide" not in captured.out


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_shows_commands_with_extras_and_pytest_arguments(tmp_path, capsys):
    data = registry_data()
    write_registry(tmp_path, data)
    args = ("-k", "declared_dependencies or test_real_skill", "-s", "-rs")
    assert main_status(
        tmp_path,
        ["--list", "hooks", "build", "--extras", "--", *args],
        forbid_run,
    ) == 0
    output = capsys.readouterr().out
    for entry in data["suite"]:
        if entry["name"] not in {"hooks", "build"}:
            continue
        for python in entry.get("pythons", ["3.13"]):
            assert expected_shell(entry, python, True, args) in output


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_suites_preserve_requested_order_and_forward_arguments(tmp_path):
    data = registry_data()
    write_registry(tmp_path, data)
    calls = []

    def run_one(root, run):
        calls.append((root, run))
        return 0

    args = ("test_new.py", "-s", "-rs")
    assert main_status(
        tmp_path,
        ["hooks", "cc-guide", "build", "--extras", "--", *args],
        run_one,
    ) == 0
    assert [(run.suite.name, run.python) for _, run in calls] == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("cc-guide", "3.13"),
        ("build", "3.13"),
    ]
    entries = {entry["name"]: entry for entry in data["suite"]}
    for root, run in calls:
        assert root == tmp_path
        assert run.argv == expected_argv(
            entries[run.suite.name], run.python, True, args
        )


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_are_visible_before_execution(tmp_path, capsys):
    data = registry_data(("hooks",))
    write_registry(tmp_path, data)
    observed = []

    def run_one(root, run):
        observed.append(capsys.readouterr())
        return 0

    assert main_status(tmp_path, ["hooks"], run_one) == 0
    assert observed[0].out.splitlines()[0] == "== hooks (3.13)"
    for note in data["suite"][0]["notes"]:
        assert note in observed[0].out
        assert note not in observed[1].out
    assert observed[1].out.splitlines()[0] == "== hooks (/usr/bin/python3)"
    assert observed[0].err == observed[1].err == ""


@pytest.mark.parametrize(
    "statuses",
    [(0, 0, 0), (1, 0, 0), (0, 5, 0), (0, 0, 1), (1, 5, 1)],
)
# spec: "0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_execution_continues_and_reports_failed_runs(tmp_path, capsys, statuses):
    suites = runner.parse(registry_data(("hooks", "build")))
    calls = []

    def run_one(root, run):
        status = statuses[len(calls)]
        calls.append(run)
        return status

    status = runner.execute(
        tmp_path, suites, False, (), run_one
    )
    assert [(run.suite.name, run.python) for run in calls] == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("build", "3.13"),
    ]
    assert status == int(any(statuses))
    summary = last_line(capsys.readouterr())
    if any(statuses):
        for run, result in zip(calls, statuses):
            if result:
                assert run.label in summary
            else:
                assert run.label not in summary
    else:
        assert re.search(r"\bpass(?:ed)?\b", summary, re.IGNORECASE)


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["--unknown-option"],
        ["not-a-registered-suite"],
        ["--list", "not-a-registered-suite"],
        ["hooks", "not-a-registered-suite"],
    ],
)
# spec: "0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_usage_errors_and_unknown_names_do_not_run_suites(tmp_path, argv):
    write_registry(tmp_path, registry_data())
    assert main_status(tmp_path, argv, forbid_run) == 2


@pytest.mark.parametrize("returncode", [0, 1, 5])
# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_uses_suite_directory_inherits_environment_and_streams_output(
    tmp_path, monkeypatch, capfd, returncode
):
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    suite = runner.Suite("hooks", "hooks", ("pytest",))
    directory = tmp_path / suite.dir
    directory.mkdir()
    child = (
        "import json, os, sys; "
        "print(json.dumps({'cwd': os.getcwd(), 'env': dict(os.environ)}), "
        "flush=True); "
        "print('pytest stderr', file=sys.stderr, flush=True); "
        "sys.exit(int(sys.argv[1]))"
    )
    run = runner.Run(
        suite,
        "3.13",
        (sys.executable, "-c", child, str(returncode)),
    )
    environment = dict(os.environ)
    assert runner.run_subprocess(tmp_path, run) == returncode
    captured = capfd.readouterr()
    result = json.loads(captured.out)
    assert Path(result["cwd"]) == directory.resolve()
    assert result["env"] == environment
    assert result["env"]["CALIBRATION_SWEEP"] == "1"
    assert "pytest stderr" in captured.err


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_fails_both_interpreters_without_stopping(
    tmp_path, monkeypatch, capsys
):
    write_registry(tmp_path, registry_data(("hooks",)))
    monkeypatch.setenv("PATH", str(tmp_path / "empty-path"))
    calls = []

    def run_one(root, run):
        calls.append(run)
        return runner.run_subprocess(root, run)

    assert main_status(tmp_path, ["hooks"], run_one) == 1
    assert len(calls) == 2
    summary = last_line(capsys.readouterr())
    assert "hooks (3.13)" in summary
    assert "hooks (/usr/bin/python3)" in summary


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_uses_directory_boundaries():
    outer = runner.Suite("build", "build", ("pytest",))
    nested = runner.Suite("cc-guide", "build/cc_guide", ("pytest",))
    sibling = runner.Suite("hooks", "build-other", ("pytest",))
    suites = [outer, nested, sibling]
    assert runner.container(nested, suites) == outer
    assert runner.container(outer, suites) is None
    assert runner.container(sibling, suites) is None


# spec: "`--all` prints one line for each suite that it skips."
# task: 4
def test_all_skips_nested_suite_and_explains_it_once(tmp_path, capsys):
    write_registry(tmp_path, registry_data())
    calls = []

    def run_one(root, run):
        calls.append(run)
        return 0

    assert main_status(tmp_path, ["--all"], run_one) == 0
    assert [(run.suite.name, run.python) for run in calls] == [
        ("build", "3.13"),
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
    ]
    lines = [
        line for line in capsys.readouterr().out.splitlines()
        if "cc-guide" in line
    ]
    assert len(lines) == 1
    assert "build/cc_guide" in lines[0]
    assert "build" in lines[0]


# spec: "A suite named on the command line always runs."
# task: 4
def test_explicitly_named_nested_suite_runs(tmp_path):
    write_registry(tmp_path, registry_data())
    calls = []

    def run_one(root, run):
        calls.append(run.suite.name)
        return 0

    assert main_status(tmp_path, ["build", "cc-guide"], run_one) == 0
    assert calls == ["build", "cc-guide"]


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_script_lists_real_suite_from_an_unrelated_directory(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "build/run_suites.py"),
            "--list",
            "cc-guide",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    entry = registry_data(("cc-guide",))["suite"][0]
    assert expected_shell(entry, "3.13") in result.stdout


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_pytest_directory_discovery_uses_both_default_patterns(tmp_path):
    git_repo(
        tmp_path,
        files={
            "build/test_new.py": "",
            "build/cc_guide/new_test.py": "",
            "hooks/test_new.py": "",
            "skills/brainstorming/scripts/test_new.py": "",
            "skills/writing-plans/scripts/new_test.py": "",
            "skills/explore-data/scripts/test.py": "",
            "skills/geographic-codes/scripts/new_tests.py": "",
            "skills/tune-hyperparameters/scripts/test_new.txt": "",
        },
    )
    assert set(runner.TEST_FILE_PATTERNS) == {"test_*.py", "*_test.py"}
    assert runner.pytest_dirs(tmp_path) == {
        "build",
        "build/cc_guide",
        "hooks",
        "skills/brainstorming/scripts",
        "skills/writing-plans/scripts",
    }


@pytest.mark.parametrize("tracked", [False, True])
@pytest.mark.parametrize("filename", ["test_new.py", "new_test.py"])
# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_unregistered_test_directory_is_reported(tmp_path, tracked, filename):
    data = git_repo(tmp_path)
    directory = "skills/brainstorming/scripts"
    path = tmp_path / directory / filename
    path.parent.mkdir(parents=True)
    path.write_text("", encoding="utf-8")
    if tracked:
        git(tmp_path, "add", str(path.relative_to(tmp_path)))
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert directory in findings[0]
    assert "\n" not in findings[0]


@pytest.mark.parametrize(
    "relative",
    [
        ".claude/worktrees/new-suite/test_new.py",
        "build/.scratch/new-suite/test_new.py",
    ],
)
# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_ignored_test_directories_do_not_enter_discovery(tmp_path, relative):
    data = git_repo(tmp_path)
    (tmp_path / ".gitignore").write_text(
        ".claude/worktrees/\nbuild/.scratch/\n", encoding="utf-8"
    )
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text("", encoding="utf-8")
    assert str(path.parent.relative_to(tmp_path)) not in runner.pytest_dirs(tmp_path)
    assert runner.check(tmp_path, data) == []


@pytest.mark.parametrize("exists", [False, True])
# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_registered_directory_must_exist_and_contain_tests(tmp_path, exists):
    data = registry_data(("hooks",))
    files = {"hooks/README": ""} if exists else {}
    git_repo(tmp_path, data, files)
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert "hooks" in findings[0]


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_registered_parent_covers_descendants_and_collects_their_tests(tmp_path):
    data = registry_data(("build",))
    git_repo(
        tmp_path,
        data,
        {"build/cc_guide/test_new.py": ""},
    )
    assert runner.check(tmp_path, data) == []


# spec: "If git fails, `--check` fails."
# task: 4
def test_git_failure_cannot_produce_a_successful_check(
    tmp_path, monkeypatch, capsys
):
    write_registry(tmp_path, registry_data())
    monkeypatch.setenv("PATH", str(tmp_path / "empty-path"))
    assert main_status(tmp_path, ["--check"], forbid_run) == 1
    captured = capsys.readouterr()
    assert "suite registry ok" not in captured.out
    assert (captured.out + captured.err).strip()


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_success_message_and_status(tmp_path, capsys):
    git_repo(tmp_path)
    assert main_status(tmp_path, ["--check"], forbid_run) == 0
    captured = capsys.readouterr()
    assert captured.out == "suite registry ok\n"
    assert captured.err == ""


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_prints_each_finding_once(tmp_path, capsys):
    data = git_repo(tmp_path)
    for name in ("brainstorming", "writing-plans"):
        path = tmp_path / f"skills/{name}/scripts/test_new.py"
        path.parent.mkdir(parents=True)
        path.write_text("", encoding="utf-8")
    expected = runner.check(tmp_path, data)
    assert len(expected) == 2
    assert main_status(tmp_path, ["--check"], forbid_run) == 1
    captured = capsys.readouterr()
    lines = (captured.out + captured.err).splitlines()
    assert sorted(lines) == sorted(expected)


# spec: "Until plan 52 adds the entry, the ninth lint refuses its new suite directory."
# task: 4
def test_plan52_directory_requires_its_own_entry(tmp_path):
    data = git_repo(tmp_path)
    directory = "skills/write-with-asd-ste100/scripts"
    path = tmp_path / directory / "test_new.py"
    path.parent.mkdir(parents=True)
    path.write_text("", encoding="utf-8")
    assert main_status(tmp_path, ["--check"], forbid_run) == 1
    data["suite"].append({
        "name": "write-with-asd-ste100",
        "dir": directory,
        "with": ["pytest"],
    })
    write_registry(tmp_path, data)
    assert main_status(tmp_path, ["--check"], forbid_run) == 0


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 4
def test_runner_imports_only_standard_library_modules():
    tree = ast.parse((ROOT / "build/run_suites.py").read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            imported.add(node.module.split(".")[0])
    assert imported <= sys.stdlib_module_names


# spec: "The entries carry the text of today's commands and comments."
# task: 5
def test_real_registry_matches_the_spec_inventory():
    data = tomllib.loads((ROOT / "build/suites.toml").read_text(encoding="utf-8"))
    assert runner.validate(data) == []
    entries = {entry["name"]: entry for entry in data["suite"]}
    assert set(ROWS) <= set(entries)
    assert set(entries) - set(ROWS) <= {"write-with-asd-ste100"}
    for name, directory, deps, extras, pythons in INVENTORY:
        entry = entries[name]
        assert entry["dir"] == directory
        assert entry["with"] == ["pytest", *deps]
        assert entry.get("extras", []) == list(extras)
        assert entry.get("pythons", ["3.13"]) == list(pythons)
    if "write-with-asd-ste100" in entries:
        assert (
            entries["write-with-asd-ste100"]["dir"]
            == "skills/write-with-asd-ste100/scripts"
        )


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_tables_are_sorted_and_unique():
    text = (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    entries = tomllib.loads(text)["suite"]
    names = [entry["name"] for entry in entries]
    directories = [entry["dir"] for entry in entries]
    assert names == sorted(names)
    assert len(names) == len(set(names))
    assert len(directories) == len(set(directories))
    assert len(re.findall(r"(?m)^\s*\[\[suite\]\]\s*(?:#.*)?$", text)) == len(entries)


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_documents_keys_order_and_lint():
    lines = (ROOT / "build/suites.toml").read_text(encoding="utf-8").splitlines()
    header = []
    for line in lines:
        if line.strip() and not line.lstrip().startswith("#"):
            break
        header.append(line)
    text = "\n".join(header).lower()
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert re.search(rf"\b{key}\b", text)
    assert "sort" in text and "name" in text
    assert "commit" in text and "lint" in text
    assert re.search(r"\b(?:ninth|9th|nine|9)\b", text)


@pytest.mark.parametrize(
    "name,tokens",
    [
        ("build", ("build/.scratch/",)),
        ("bayesian-workflow", ("CALIBRATION_SWEEP=1", "arviz", "warn")),
        ("llm-wiki", ("@needs_pilot", "$LLM_WIKI_ROOT")),
        ("brainstorming", ("node",)),
        ("tune-hyperparameters", ("--with sklearn", "fail")),
        ("hooks", ("3.9", "launchd", "Gate B")),
    ],
)
# spec: "The notes carry the rest of each comment."
# task: 5
def test_real_notes_retain_the_explicitly_identified_information(name, tokens):
    data = tomllib.loads((ROOT / "build/suites.toml").read_text(encoding="utf-8"))
    entries = {entry["name"]: entry for entry in data["suite"]}
    notes = "\n".join(entries[name].get("notes", [])).casefold()
    for token in tokens:
        assert token.casefold() in notes


# spec: "- the real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_check_passes(capsys):
    data = tomllib.loads((ROOT / "build/suites.toml").read_text(encoding="utf-8"))
    assert runner.check(ROOT, data) == []
    assert main_status(ROOT, ["--check"], forbid_run) == 0
    captured = capsys.readouterr()
    assert captured.out == "suite registry ok\n"
    assert captured.err == ""


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_registry_check_is_the_ninth_literal_lint():
    script = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    commands = lint_commands(script)
    assert len(commands) == 9
    assert commands[-1] == (
        "suite_registry",
        [
            "uv",
            "run",
            "--python",
            "3.13",
            "python",
            "build/run_suites.py",
            "--check",
        ],
    )
    assert [
        name
        for name, argv in commands
        if "build/run_suites.py" in argv
    ] == ["suite_registry"]
    comments = "\n".join(
        line for line in script.splitlines() if line.lstrip().startswith("#")
    ).lower()
    assert "nine" in comments


# spec: "`suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_test_inventory_includes_the_registry(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "build"))
    namespace = runpy.run_path(str(ROOT / "build/test_commit_lints.py"))
    assert "suite_registry" in namespace["CHECKS"]
    assert callable(namespace["test_unregistered_suite_is_refused"])


# spec: "`suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_committed_new_suite_fails_only_the_registry_lint(tmp_path):
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(clone)],
        check=True,
        capture_output=True,
        text=True,
    )
    changed_paths = (
        "build/run_suites.py",
        "build/suites.toml",
        "build/run_commit_lints.sh",
        "build/test_run_suites.py",
        "build/test_commit_lints.py",
        "build/test_check_conformance.py",
        "build/CLAUDE.md",
        "CLAUDE.md",
    )
    for relative in changed_paths:
        destination = clone / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    git(clone, "config", "user.name", "Acceptance tests")
    git(clone, "config", "user.email", "acceptance@example.invalid")
    git(clone, "add", "--", *changed_paths)
    git(
        clone,
        "-c", "core.hooksPath=/dev/null",
        "commit", "--allow-empty", "-qm", "Acceptance baseline",
    )

    baseline = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=clone,
        capture_output=True,
        text=True,
    )
    assert baseline.returncode == 0, baseline.stdout + baseline.stderr
    assert "commit lints passed" in baseline.stdout

    relative = "skills/acceptance-unregistered/scripts/test_new.py"
    path = clone / relative
    path.parent.mkdir(parents=True)
    path.write_text("def test_new():\n    pass\n", encoding="utf-8")
    git(clone, "add", "--", relative)
    git(
        clone,
        "-c", "core.hooksPath=/dev/null",
        "commit", "-qm", "Add an unregistered suite",
    )

    script = (clone / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    results = {}
    for name, argv in lint_commands(script):
        results[name] = subprocess.run(
            argv,
            cwd=clone,
            capture_output=True,
            text=True,
        )
    failures = {
        name: (result.returncode, result.stdout, result.stderr)
        for name, result in results.items()
        if result.returncode
    }
    assert set(failures) == {"suite_registry"}, failures
    result = results["suite_registry"]
    assert result.returncode == 1
    assert str(Path(relative).parent) in result.stdout + result.stderr


# spec: "`build/CLAUDE.md`: "the eight commit lints" becomes "the nine commit lints", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_documentation_describes_the_registry_lint():
    text = (ROOT / "build/CLAUDE.md").read_text(encoding="utf-8")
    assert "the eight commit lints" not in text
    assert "the nine commit lints" in text
    assert any(
        all(token in paragraph for token in (
            "suites.toml", "run_suites.py", "--check", "commit lint"
        ))
        for paragraph in text.split("\n\n")
    )


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_intro_retains_execution_rules_and_names_the_runner():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    introductions = [
        line for line in text.splitlines()
        if "build/suites.toml" in line and "build/run_suites.py" in line
    ]
    assert len(introductions) == 1
    intro = introductions[0]
    assert "uv" in intro
    assert "3.13" in intro
    assert "director" in intro.lower()
    assert "test_build.py" in intro
    assert "colli" in intro.lower()
    assert "notes" in intro.lower()
    assert re.search(r"\b(?:before|first)\b", intro, re.IGNORECASE)
    assert "There is no root test runner" not in text


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_documents_the_four_runner_commands_in_one_block():
    lines = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()
    prefix = "uv run --python 3.13 python build/run_suites.py "
    expected = [
        prefix + "--list",
        prefix + "<name> [--extras] [-- <pytest args>]",
        prefix + "--all",
        prefix + "--check",
    ]
    start = lines.index(expected[0])
    assert lines[start:start + 4] == expected
    assert lines[start - 1].lstrip().startswith("#")


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_has_no_literal_directory_suite_runs_and_is_under_200_lines():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    directories = {row[1] for row in INVENTORY}
    directories.add("skills/write-with-asd-ste100/scripts")
    for line in text.splitlines():
        if not re.match(r"^\s*cd\s", line):
            continue
        words = shlex.split(line, comments=True)
        if len(words) < 3 or words[1] not in directories:
            continue
        segments = []
        segment = []
        for word in words:
            if word == "&&":
                segments.append(segment)
                segment = []
            else:
                segment.append(word)
        segments.append(segment)
        for command in segments[1:]:
            assert command[-4:] != ["python", "-m", "pytest", "-q"], line


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_root_does_not_introduce_suite_or_test_count_claims():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert not re.search(
        r"\b(?:\d+|eighteen|nineteen)\s+"
        r"(?:(?:directory|directory-scoped)\s+)?(?:suites|tests)\b",
        text,
        re.IGNORECASE,
    )


# spec: "The commit-lint comment names the suite-registry check and says "nine"."
# task: 7
def test_root_commit_lint_comment_names_the_ninth_check():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert any(
        line.lstrip().startswith("#")
        and "nine" in line.lower()
        and re.search(r"suite[-_ ]registry", line, re.IGNORECASE)
        for line in text.splitlines()
    )


# spec: "The comment names the suite `run_suites.py cc-guide` instead of "its suite"."
# task: 7
def test_cc_guide_comment_names_the_runner_suite():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert any(
        line.lstrip().startswith("#") and "run_suites.py cc-guide" in line
        for line in text.splitlines()
    )


@pytest.mark.parametrize(
    "literal",
    [
        "test_runtime_support.py",
        "test_commit_lints.py",
        "declared_dependencies",
        "test_real_skill",
        "test_check_jax_examples.py",
        "Single test",
        "verify_citations.py",
        "extract_structure.py",
        "cli.py lint",
        "cli.py check",
    ],
)
# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_named_selections_and_tools_remain_in_root_documentation(literal):
    assert literal in (ROOT / "CLAUDE.md").read_text(encoding="utf-8")


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_stamp_is_present_and_the_conformance_positive_control_passes():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert re.fullmatch(r"<!-- cc-guide: .+ @\S+ -->", text.splitlines()[0])
    assert "@needs_pilot" not in text
    result = subprocess.run(
        [
            sys.executable,
            "-m", "pytest", "-q",
            "build/test_check_conformance.py"
            "::test_claude_md_import_resolves_passes_on_the_repo",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`.</plan></flag>
<flag task="5"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>`cc_guide`</plan></flag>
</flags>
<untestable>
**Status:** Design approved in brainstorming on 2026-10-18.
Next step: an implementation plan from the writing-plans skill (`entry_check.py` reported plan id 54 as next free on 2026-10-18).
The `claude-md-size` check (a commit lint, through `build/check_conformance.py`) fails at 200 lines.
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
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
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
Same number of lines.
Line 133 is not touched (plan 53's Task 7 edits it).
The file ends at about 145 lines.
The deletion of lines 66–125 is bounded by two lines that no other plan edits: the `# Full build-directory tests` comment and the `cd hooks && …` command.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
`build/test_check_conformance.py`: `test_claude_md_import_resolves_passes_on_the_repo` asserts `'@needs_pilot' in text` as its positive control, and that note moves to the registry.
A naive scan would flag the `@` in it, and the stamp keeps its form when its version changes.
No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
The new files are the owner's original tooling.
The register's deviation `claude-md-serves-codex-gemini` still holds as written: a condensed Commands block stays in the root file, and the registry is a plain file that every runtime can read.
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
R5.3 edits the `run_commit_lints.sh` paragraph and adds a sentence.
If an edit block does not match, merge by hand.
**R6's tests** run red first, then green.
**The Stage 2 audit** (one time, a scratch script that is never committed, as in plan 38's Task 2).
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
CI running the suites (`--all` in `.github/workflows/lints.yml`).
It would need node, a 3.9 `/usr/bin/python3` and `build/.scratch/`.
Revisit if: the owner wants suites in CI.
Parallel runs, per-suite timeouts and machine-readable output.
Revisit if: `--all` gets slow or a tool needs to parse its results.
Moving the lint, snippet, JAX, smoke, rebuild and citation commands into the runner.
Revisit if: `CLAUDE.md` nears its limit again.
</untestable>