<tests>
import ast
import copy
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "build/run_suites.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "suite_runner_under_test", RUNNER_PATH
)
runner = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = runner
MODULE_SPEC.loader.exec_module(runner)

# Dependencies below exclude pytest, which every entry must put first.
EXPECTED = {
    "bayesian-workflow": (
        "skills/bayesian-workflow/scripts",
        ["arviz", "arviz-stats", "numpy", "xarray"],
        ["matplotlib"],
        ["3.13"],
    ),
    "brainstorming": (
        "skills/brainstorming/scripts", [], [], ["3.13"]
    ),
    "build": (
        "build",
        ["numpy", "polars", "pyyaml"],
        [
            "arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots",
            "numpyro", "jax", "matplotlib",
        ],
        ["3.13"],
    ),
    "cc-guide": ("build/cc_guide", [], [], ["3.13"]),
    "classification-codes": (
        "skills/classification-codes/scripts", ["polars"], [], ["3.13"]
    ),
    "describe-critique-methodology": (
        "skills/describe-critique-methodology/scripts", [], [], ["3.13"]
    ),
    "design-architecture": (
        "skills/design-architecture/scripts", [], [], ["3.13"]
    ),
    "explore-data": (
        "skills/explore-data/scripts", ["polars"], [], ["3.13"]
    ),
    "geographic-codes": (
        "skills/geographic-codes/scripts",
        ["polars", "fastexcel"], [], ["3.13"],
    ),
    "hooks": ("hooks", [], [], ["3.13", "/usr/bin/python3"]),
    "llm-wiki": ("skills/llm-wiki/scripts", [], [], ["3.13"]),
    "recommend-probabilistic-model": (
        "skills/recommend-probabilistic-model/scripts",
        ["numpy", "polars"], [], ["3.13"],
    ),
    "recommend-visualization": (
        "skills/recommend-visualization/scripts",
        ["numpy", "polars"], [], ["3.13"],
    ),
    "subagent-driven-development": (
        "skills/subagent-driven-development/scripts", [], [], ["3.13"]
    ),
    "systematic-debugging": (
        "skills/systematic-debugging", [], [], ["3.13"]
    ),
    "track-model-experiments": (
        "skills/track-model-experiments/scripts",
        ["numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"],
        [],
        ["3.13"],
    ),
    "tune-hyperparameters": (
        "skills/tune-hyperparameters/scripts",
        ["numpy", "polars"], ["scikit-learn", "optuna"], ["3.13"],
    ),
    "writing-plans": (
        "skills/writing-plans/scripts", [], [], ["3.13"]
    ),
}


def entry(name="brainstorming", **changes):
    directory, deps, extras, pythons = EXPECTED[name]
    result = {
        "name": name,
        "dir": directory,
        "with": ["pytest", *deps],
        "extras": list(extras),
        "pythons": list(pythons),
        "notes": [],
    }
    result.update(changes)
    return result


def toml_value(value):
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{ " + ", ".join(
            f"{key} = {toml_value(item)}" for key, item in value.items()
        ) + " }"
    raise TypeError(type(value))


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
                    f"{field} = {toml_value(contents)}"
                    for field, contents in item.items()
                )
                lines.append("")
        else:
            lines.append(f"{key} = {toml_value(value)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def invoke(argv, root, run_one=None):
    if run_one is None:
        def run_one(*args):
            pytest.fail("This command must not start a suite")
    try:
        return runner.main(argv, root=root, run_one=run_one)
    except SystemExit as error:
        return error.code


def expected_argv(item, python, extras=False, pytest_args=()):
    deps = item["with"] + (item.get("extras", []) if extras else [])
    argv = ["uv", "run", "--python", python]
    for dep in deps:
        argv.extend(["--with", dep])
    return tuple(argv + ["python", "-m", "pytest", "-q", *pytest_args])


def expected_shell(directory, argv):
    return f"cd {shlex.quote(directory)} && {shlex.join(argv)}"


def git_environment():
    result = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    result["GIT_CONFIG_GLOBAL"] = os.devnull
    result["GIT_CONFIG_NOSYSTEM"] = "1"
    return result


def git(root, *args, check=True):
    return subprocess.run(
        ["git", *args],
        cwd=root,
        env=git_environment(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def make_repo(root, data=None, files=None):
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q")
    if data is None:
        data = {"suite": [entry()]}
    write_registry(root, data)
    if files is None:
        files = {
            "skills/brainstorming/scripts/test_registered.py":
                "def test_registered():\n    assert True\n"
        }
    for relative, contents in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    git(root, "add", ".")
    return root


def real_data():
    return tomllib.loads(
        (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    )


def historical_claude():
    result = git(ROOT, "show", "456e3fb:CLAUDE.md", check=False)
    if result.returncode:
        pytest.skip("The spec's historical commit 456e3fb is unavailable")
    return result.stdout


def original_suite_commands():
    lines = historical_claude().splitlines()
    selected = lines[65:125] + lines[144:145]
    commands = set()
    for line in selected:
        if not re.match(r"^\s*cd .+ && uv run ", line):
            continue
        directory, *runs = line.strip().split(" && ")
        for command in runs:
            assert command.startswith("uv run ")
            commands.add(f"{directory} && {command}")
    assert commands
    return commands


def invalid_registries():
    cases = []

    unknown_root = {"suite": [entry()], "unexpected": "value"}
    cases.append(unknown_root)
    cases.append({"suite": "not a list"})
    cases.append({"suite": [13]})

    unknown_field = entry()
    unknown_field["extra"] = ["matplotlib"]
    cases.append({"suite": [unknown_field]})

    for required in ("name", "dir", "with"):
        missing = entry()
        del missing[required]
        cases.append({"suite": [missing]})

    for key in ("name", "dir"):
        for value in (13, True, ["brainstorming"]):
            cases.append({"suite": [entry(**{key: value})]})

    for key in ("with", "extras", "pythons", "notes"):
        for value in ("pytest", 13, True, [13], ["pytest", False]):
            cases.append({"suite": [entry(**{key: value})]})

    cases.append({"suite": [entry(**{"with": []})]})
    cases.append({"suite": [entry(**{"with": ["numpy"]})]})
    cases.append({
        "suite": [
            entry(),
            entry(dir="another-directory"),
        ]
    })
    cases.append({
        "suite": [
            entry(),
            entry(name="another-suite"),
        ]
    })
    return cases


@pytest.fixture
def fixture_registry(tmp_path):
    data = {
        "suite": [
            entry("build", notes=["build/.scratch/"]),
            entry("cc-guide", notes=["directory suite"]),
            entry("hooks", notes=["3.9 floor", "Gate B"]),
        ]
    }
    write_registry(tmp_path, data)
    for item in data["suite"]:
        (tmp_path / item["dir"]).mkdir(parents=True, exist_ok=True)
    return tmp_path, data


@pytest.fixture
def fake_uv(tmp_path, monkeypatch):
    binary_dir = tmp_path / "fake-bin"
    binary_dir.mkdir()
    log = tmp_path / "fake-uv.jsonl"
    executable = binary_dir / "uv"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import hashlib, json, os, sys\n"
        "environment = json.dumps(dict(os.environ), sort_keys=True).encode()\n"
        "record = {\n"
        "    'argv': sys.argv[1:],\n"
        "    'cwd': os.getcwd(),\n"
        "    'environment': hashlib.sha256(environment).hexdigest(),\n"
        "}\n"
        "with open(os.environ['ACCEPTANCE_UV_LOG'], 'a') as stream:\n"
        "    stream.write(json.dumps(record) + '\\n')\n"
        "print('pytest stdout', flush=True)\n"
        "print('pytest stderr', file=sys.stderr, flush=True)\n"
        "sys.exit(int(os.environ.get('ACCEPTANCE_UV_STATUS', '0')))\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    monkeypatch.setenv(
        "PATH", str(binary_dir) + os.pathsep + os.environ.get("PATH", "")
    )
    monkeypatch.setenv("ACCEPTANCE_UV_LOG", str(log))
    return log


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_imports_only_the_standard_library():
    tree = ast.parse(RUNNER_PATH.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            imports.add(node.module.split(".")[0])
    assert imports <= sys.stdlib_module_names | {"__future__"}


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 2
def test_repo_constant_comes_from_the_runner_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert runner.REPO.resolve() == RUNNER_PATH.resolve().parents[1]
    assert runner.REGISTRY == "build/suites.toml"


# spec: "The interpreters, one run each, in order. Default `['3.13']`."
# task: 2
def test_missing_pythons_defaults_to_python_313():
    item = entry()
    del item["pythons"]
    suite, = runner.parse({"suite": [item]})
    assert suite.pythons == ("3.13",)
    assert [run.python for run in runner.runs(suite)] == ["3.13"]
    constructed = runner.Suite(
        name="brainstorming",
        dir="skills/brainstorming/scripts",
        deps=("pytest",),
    )
    assert constructed.pythons == ("3.13",)


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
@pytest.mark.parametrize("data", invalid_registries())
def test_invalid_registry_refuses_every_execution_mode(data, tmp_path):
    assert runner.validate(copy.deepcopy(data))
    write_registry(tmp_path, data)
    for argv in (["--list"], ["brainstorming"], ["--all"]):
        assert invoke(argv, tmp_path) == 2


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
@pytest.mark.parametrize("data", invalid_registries())
def test_check_reports_validation_failures(data, tmp_path):
    root = make_repo(tmp_path, data=data, files={})
    problems = runner.validate(copy.deepcopy(data))
    findings = runner.check(root, copy.deepcopy(data))
    assert problems
    assert all(
        any(problem in finding for finding in findings)
        for problem in problems
    )


# spec: "0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize(
    "argv",
    [[], ["unknown-suite"], ["--list", "unknown-suite"], ["--unknown-option"]],
)
def test_usage_errors_and_unknown_names_exit_two(argv, tmp_path):
    write_registry(tmp_path, {"suite": [entry()]})
    assert invoke(argv, tmp_path) == 2


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
@pytest.mark.parametrize("name", EXPECTED)
def test_default_argv_for_every_spec_suite(name):
    item = entry(name)
    suite, = runner.parse({"suite": [item]})
    runs = runner.runs(suite)
    assert [run.python for run in runs] == item["pythons"]
    assert [run.argv for run in runs] == [
        expected_argv(item, python) for python in item["pythons"]
    ]


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_directory_dependencies_and_pytest_arguments():
    item = entry(
        "build",
        dir="directory with spaces and 'quotes'",
        notes=[],
    )
    pytest_args = ("-k", "one or two", "test_file.py::test_name[one two]")
    suite, = runner.parse({"suite": [item]})
    run, = runner.runs(suite, extras=True, pytest_args=pytest_args)
    argv = expected_argv(item, "3.13", extras=True, pytest_args=pytest_args)
    assert run.shell() == expected_shell(item["dir"], argv)
    tokens = shlex.split(run.shell())
    assert tokens[:3] == ["cd", item["dir"], "&&"]
    assert tokens[3:] == list(argv)


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 2
def test_hooks_has_two_separate_shell_forms():
    item = entry("hooks")
    suite, = runner.parse({"suite": [item]})
    runs = runner.runs(suite)
    assert [run.shell() for run in runs] == [
        expected_shell("hooks", expected_argv(item, python))
        for python in ("3.13", "/usr/bin/python3")
    ]


# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_are_opt_in_and_follow_default_dependencies():
    item = entry("build")
    suite, = runner.parse({"suite": [item]})
    ordinary, = runner.runs(suite)
    expanded, = runner.runs(suite, extras=True)
    assert ordinary.argv == expected_argv(item, "3.13")
    assert expanded.argv == expected_argv(item, "3.13", extras=True)


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_separator_preserves_pytest_arguments_in_every_run(fixture_registry):
    root, data = fixture_registry
    pytest_args = (
        "test_example.py::test_example",
        "-k", "one or two", "-s", "-rs",
    )
    _, parsed_args = runner.parse_args(["hooks", "--", *pytest_args])
    assert parsed_args == pytest_args
    seen = []

    def run_one(actual_root, run):
        seen.append((actual_root, run))
        return 0

    assert invoke(["hooks", "--", *pytest_args], root, run_one) == 0
    hooks = next(item for item in data["suite"] if item["name"] == "hooks")
    assert [run.argv for _, run in seen] == [
        expected_argv(hooks, python, pytest_args=pytest_args)
        for python in hooks["pythons"]
    ]


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_prints_all_fixture_information_without_running(
    fixture_registry, capsys
):
    root, data = fixture_registry
    assert invoke(["--list"], root) == 0
    output = capsys.readouterr().out
    for item in data["suite"]:
        assert item["name"] in output
        assert item["dir"] in output
        for python in item["pythons"]:
            assert expected_shell(
                item["dir"], expected_argv(item, python)
            ) in output
        for extra in item["extras"]:
            assert extra in output
        for note in item["notes"]:
            assert note in output


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_can_select_more_than_one_suite(fixture_registry, capsys):
    root, _ = fixture_registry
    assert invoke(["--list", "hooks", "cc-guide"], root) == 0
    output = capsys.readouterr().out
    assert "hooks" in output
    assert "cc-guide" in output
    assert "build/.scratch/" not in output
    assert "arviz>=1.0" not in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_applies_extras_and_pytest_arguments(fixture_registry, capsys):
    root, data = fixture_registry
    args = ("-k", "one or two", "-rs")
    assert invoke(["--list", "build", "--extras", "--", *args], root) == 0
    output = capsys.readouterr().out
    item = data["suite"][0]
    assert expected_shell(
        item["dir"],
        expected_argv(item, "3.13", extras=True, pytest_args=args),
    ) in output


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_suites_and_interpreters_keep_requested_order(fixture_registry):
    root, _ = fixture_registry
    seen = []

    def run_one(actual_root, run):
        seen.append((actual_root, run.suite.name, run.python))
        return 0

    assert invoke(["hooks", "build"], root, run_one) == 0
    assert seen == [
        (root, "hooks", "3.13"),
        (root, "hooks", "/usr/bin/python3"),
        (root, "build", "3.13"),
    ]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_are_printed_before_the_injected_run(
    fixture_registry, capsys
):
    root, data = fixture_registry
    observations = []

    def run_one(actual_root, run):
        output = capsys.readouterr().out
        observations.append((run, output))
        assert f"== {run.suite.name} ({run.python})" in output
        return 0

    assert invoke(["hooks", "build"], root, run_one) == 0
    hooks_notes = data["suite"][2]["notes"]
    for note in hooks_notes:
        first = observations[0][1]
        assert first.index("== hooks (3.13)") < first.index(note)
        assert note not in observations[1][1]
    assert "build/.scratch/" in observations[2][1]


# spec: "A failed run does not stop the next one."
# task: 4
@pytest.mark.parametrize("first_status", [1, 5])
def test_failure_does_not_stop_later_interpreters_or_suites(
    fixture_registry, first_status
):
    root, _ = fixture_registry
    seen = []

    def run_one(actual_root, run):
        seen.append((run.suite.name, run.python))
        return first_status if len(seen) == 1 else 0

    assert invoke(["hooks", "build"], root, run_one) == 1
    assert seen == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("build", "3.13"),
    ]


# spec: "0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize(
    ("statuses", "expected_status"),
    [
        ((0, 0, 0), 0),
        ((1, 0, 0), 1),
        ((0, 5, 0), 1),
        ((1, 5, 1), 1),
    ],
)
def test_execute_aggregates_all_run_statuses(
    fixture_registry, statuses, expected_status
):
    root, data = fixture_registry
    suites = runner.parse(data)
    selected = [suites[2], suites[0]]
    answers = iter(statuses)
    seen = []

    def run_one(actual_root, run):
        seen.append(run)
        return next(answers)

    assert runner.execute(
        root, selected, False, (), run_one
    ) == expected_status
    assert len(seen) == len(statuses)


# spec: "The last line names the failed runs, or says that every run passed."
# task: 4
@pytest.mark.parametrize("failed", [False, True])
def test_final_summary_identifies_all_and_only_failed_runs(
    fixture_registry, capsys, failed
):
    root, _ = fixture_registry

    def run_one(actual_root, run):
        return 5 if failed and run.python == "/usr/bin/python3" else 0

    assert invoke(["hooks", "build"], root, run_one) == int(failed)
    captured = capsys.readouterr()
    last = (captured.out + captured.err).strip().splitlines()[-1]
    if failed:
        assert "hooks (/usr/bin/python3)" in last
        assert "hooks (3.13)" not in last
        assert "build (3.13)" not in last
    else:
        assert re.search(r"\bpass(?:ed)?\b", last, re.IGNORECASE)
        assert not re.search(r"\bfail(?:ed)?\b", last, re.IGNORECASE)


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_uses_directory_boundaries():
    outer = runner.Suite("build", "build", ("pytest",))
    nested = runner.Suite("cc-guide", "build/cc_guide", ("pytest",))
    sibling = runner.Suite("sibling", "build-other", ("pytest",))
    suites = [outer, nested, sibling]
    assert runner.container(nested, suites) == outer
    assert runner.container(outer, suites) is None
    assert runner.container(sibling, suites) is None


# spec: "`--all` prints one line for each suite that it skips."
# task: 4
def test_all_skips_nested_suite_and_explains_it(
    fixture_registry, capsys
):
    root, _ = fixture_registry
    seen = []

    def run_one(actual_root, run):
        seen.append((run.suite.name, run.python))
        return 0

    assert invoke(["--all"], root, run_one) == 0
    assert seen == [
        ("build", "3.13"),
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
    ]
    lines = capsys.readouterr().out.splitlines()
    explanations = [
        line for line in lines
        if "cc-guide" in line and "build/cc_guide" in line
    ]
    assert len(explanations) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_explicitly_named_nested_suite_runs(fixture_registry):
    root, _ = fixture_registry
    seen = []

    def run_one(actual_root, run):
        seen.append((run.suite.name, run.python))
        return 0

    assert invoke(["cc-guide"], root, run_one) == 0
    assert seen == [("cc-guide", "3.13")]


# spec: "The runner passes its environment to every run unchanged."
# task: 4
@pytest.mark.parametrize("child_status", [0, 5])
def test_subprocess_uses_suite_cwd_argv_and_unchanged_environment(
    tmp_path, monkeypatch, fake_uv, capfd, child_status
):
    item = entry("bayesian-workflow", notes=["CALIBRATION_SWEEP=1"])
    write_registry(tmp_path, {"suite": [item]})
    (tmp_path / item["dir"]).mkdir(parents=True)
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("ACCEPTANCE_UV_STATUS", str(child_status))
    environment_digest = hashlib.sha256(
        json.dumps(dict(os.environ), sort_keys=True).encode()
    ).hexdigest()

    status = invoke(
        ["bayesian-workflow", "--", "-s"],
        tmp_path,
        runner.run_subprocess,
    )

    assert status == (0 if child_status == 0 else 1)
    record, = [
        json.loads(line)
        for line in fake_uv.read_text(encoding="utf-8").splitlines()
    ]
    assert record["argv"] == list(
        expected_argv(item, "3.13", pytest_args=("-s",))
    )[1:]
    assert Path(record["cwd"]) == tmp_path / item["dir"]
    assert record["environment"] == environment_digest
    captured = capfd.readouterr()
    assert "pytest stdout" in captured.out
    assert "pytest stderr" in captured.err
    assert captured.out.index(
        "== bayesian-workflow (3.13)"
    ) < captured.out.index("pytest stdout")
    assert captured.out.index(
        "CALIBRATION_SWEEP=1"
    ) < captured.out.index("pytest stdout")


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_fails_both_interpreters_without_stopping(
    fixture_registry, monkeypatch, tmp_path, capsys
):
    root, _ = fixture_registry
    empty_path = tmp_path / "empty-path"
    empty_path.mkdir()
    monkeypatch.setenv("PATH", str(empty_path))
    assert invoke(["hooks"], root, runner.run_subprocess) == 1
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "== hooks (3.13)" in output
    assert "== hooks (/usr/bin/python3)" in output
    last = output.strip().splitlines()[-1]
    assert "hooks (3.13)" in last
    assert "hooks (/usr/bin/python3)" in last


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize("filename", ["test_new.py", "new_test.py"])
def test_unregistered_pytest_directory_is_a_coverage_finding(
    tmp_path, filename
):
    root = make_repo(tmp_path)
    directory = root / "skills/new-suite/scripts"
    directory.mkdir(parents=True)
    (directory / filename).write_text("", encoding="utf-8")
    findings = runner.check(root, {"suite": [entry()]})
    assert len(findings) == 1
    assert "skills/new-suite/scripts" in findings[0]


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize(
    "filename",
    ["contest_new.py", "test_new.py.bak", "new_tests.py", "test_new.txt"],
)
def test_non_pytest_filenames_do_not_create_coverage_findings(
    tmp_path, filename
):
    root = make_repo(tmp_path)
    directory = root / "skills/new-suite/scripts"
    directory.mkdir(parents=True)
    (directory / filename).write_text("", encoding="utf-8")
    assert runner.check(root, {"suite": [entry()]}) == []


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
@pytest.mark.parametrize("exists", [False, True])
def test_registered_directory_must_exist_and_have_pytest_files(
    tmp_path, exists
):
    data = {"suite": [entry()]}
    root = make_repo(tmp_path, data=data, files={})
    if exists:
        directory = root / entry()["dir"]
        directory.mkdir(parents=True)
        (directory / "README.md").write_text("No tests", encoding="utf-8")
    findings = runner.check(root, data)
    assert len(findings) == 1
    assert entry()["dir"] in findings[0]


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_registered_parent_covers_nested_tests_and_not_prefix_siblings(
    tmp_path
):
    data = {"suite": [entry("build")]}
    root = make_repo(
        tmp_path,
        data=data,
        files={"build/cc_guide/test_nested.py": ""},
    )
    assert runner.check(root, data) == []
    sibling = root / "build-other"
    sibling.mkdir()
    (sibling / "test_uncovered.py").write_text("", encoding="utf-8")
    findings = runner.check(root, data)
    assert len(findings) == 1
    assert "build-other" in findings[0]


# spec: "The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root."
# task: 3
def test_pytest_dirs_includes_indexed_and_untracked_files(tmp_path):
    root = make_repo(tmp_path)
    staged = root / "staged/test_staged.py"
    staged.parent.mkdir()
    staged.write_text("", encoding="utf-8")
    git(root, "add", str(staged.relative_to(root)))
    untracked = root / "untracked/untracked_test.py"
    untracked.parent.mkdir()
    untracked.write_text("", encoding="utf-8")
    assert runner.pytest_dirs(root) == {
        "skills/brainstorming/scripts",
        "staged",
        "untracked",
    }


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_ignored_test_trees_do_not_create_findings(tmp_path):
    root = make_repo(
        tmp_path,
        files={
            "skills/brainstorming/scripts/test_registered.py": "",
            ".gitignore":
                ".claude/worktrees/\nbuild/.scratch/\nignored-tests/\n",
        },
    )
    for relative in (
        ".claude/worktrees/session/test_hidden.py",
        "build/.scratch/test_hidden.py",
        "ignored-tests/hidden_test.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    assert runner.pytest_dirs(root) == {"skills/brainstorming/scripts"}
    assert runner.check(root, {"suite": [entry()]}) == []


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_untracked_suite_is_found_without_git_add(tmp_path):
    root = make_repo(tmp_path)
    relative = "skills/new-suite/scripts/test_new.py"
    path = root / relative
    path.parent.mkdir(parents=True)
    path.write_text("", encoding="utf-8")
    assert relative not in git(root, "ls-files", "--cached").stdout.splitlines()
    findings = runner.check(root, {"suite": [entry()]})
    assert len(findings) == 1
    assert "skills/new-suite/scripts" in findings[0]


# spec: "If git fails, `--check` fails."
# task: 4
def test_check_fails_outside_a_git_repository(tmp_path, capsys):
    write_registry(tmp_path, {"suite": [entry()]})
    path = tmp_path / entry()["dir"] / "test_registered.py"
    path.parent.mkdir(parents=True)
    path.write_text("", encoding="utf-8")
    assert runner.check(tmp_path, {"suite": [entry()]})
    assert invoke(["--check"], tmp_path) == 1
    captured = capsys.readouterr()
    assert "suite registry ok" not in captured.out + captured.err


# spec: "If git fails, `--check` fails."
# task: 4
def test_check_fails_when_git_cannot_start(tmp_path, monkeypatch):
    root = make_repo(tmp_path)
    empty_path = tmp_path / "empty-path"
    empty_path.mkdir()
    monkeypatch.setenv("PATH", str(empty_path))
    assert invoke(["--check"], root) == 1


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_success_has_the_required_output(tmp_path, capsys):
    root = make_repo(tmp_path)
    assert invoke(["--check"], root) == 0
    captured = capsys.readouterr()
    assert captured.out == "suite registry ok\n"
    assert captured.err == ""


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_prints_one_line_for_each_finding(tmp_path, capsys):
    root = make_repo(tmp_path)
    for directory in ("skills/new-one/scripts", "skills/new-two/scripts"):
        path = root / directory / "test_new.py"
        path.parent.mkdir(parents=True)
        path.write_text("", encoding="utf-8")
    findings = runner.check(root, {"suite": [entry()]})
    assert len(findings) == 2
    assert invoke(["--check"], root) == 1
    captured = capsys.readouterr()
    lines = [
        line for line in (captured.out + captured.err).splitlines()
        if line.strip()
    ]
    assert sorted(lines) == sorted(findings)


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_is_sorted_and_uses_suite_tables():
    text = (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    data = tomllib.loads(text)
    names = [item["name"] for item in data["suite"]]
    assert names == sorted(names)
    assert len(re.findall(r"(?m)^\s*\[\[suite\]\]\s*$", text)) == len(names)
    assert runner.validate(data) == []


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_real_registry_header_documents_its_contract():
    text = (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    header = text.split("[[suite]]", 1)[0]
    comment_text = "\n".join(
        line.lstrip()[1:]
        for line in header.splitlines()
        if line.lstrip().startswith("#")
    ).lower()
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert re.search(rf"\b{key}\b", comment_text)
    assert re.search(r"sort|alphabet", comment_text)
    assert "name" in comment_text
    assert "commit" in comment_text and "lint" in comment_text
    assert re.search(r"\bninth\b|\b9th\b|#?\s*\b9\b", comment_text)


# spec: "The entries carry the text of today's commands and comments."
# task: 5
def test_real_registry_matches_every_inventory_value():
    data = real_data()
    actual = {item["name"]: item for item in data["suite"]}
    assert EXPECTED.keys() <= actual.keys()
    for name, (directory, deps, extras, pythons) in EXPECTED.items():
        item = actual[name]
        assert item["dir"] == directory
        assert item["with"] == ["pytest", *deps]
        assert item.get("extras", []) == extras
        assert item.get("pythons", ["3.13"]) == pythons


# spec: "A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`."
# task: 5
def test_real_registry_uses_skill_names_and_the_three_other_names():
    for item in real_data()["suite"]:
        parts = Path(item["dir"]).parts
        if parts[0] == "skills":
            assert item["name"] == parts[1]
        else:
            assert item["name"] in {"build", "cc-guide", "hooks"}


# spec: "The notes carry the rest of each comment."
# task: 5
@pytest.mark.parametrize(
    ("name", "required_tokens"),
    [
        ("build", ("build/.scratch/",)),
        ("bayesian-workflow", ("CALIBRATION_SWEEP=1", "arviz")),
        ("llm-wiki", ("@needs_pilot", "$LLM_WIKI_ROOT")),
        ("brainstorming", ("node",)),
        ("tune-hyperparameters", ("--with sklearn",)),
        ("hooks", ("3.9", "launchd", "PATH", "Gate B")),
    ],
)
def test_real_registry_preserves_explicit_note_details(name, required_tokens):
    item = next(
        item for item in real_data()["suite"] if item["name"] == name
    )
    notes = "\n".join(item.get("notes", []))
    for token in required_tokens:
        assert token in notes


# spec: "With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character."
# task: 5
def test_default_shell_forms_match_the_spec_baseline_commands():
    suites = runner.parse(real_data())
    inventory_suites = [
        suite for suite in suites if suite.name in EXPECTED
    ]
    actual = {
        run.shell()
        for suite in inventory_suites
        for run in runner.runs(suite)
    }
    assert actual == original_suite_commands()


# spec: "the real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_passes_check(capsys):
    assert runner.check(ROOT, real_data()) == []
    assert invoke(["--check"], ROOT) == 0
    captured = capsys.readouterr()
    assert captured.out == "suite registry ok\n"
    assert captured.err == ""


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 5
def test_cli_lists_a_real_suite_from_an_unrelated_directory(tmp_path):
    result = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--list", "cc-guide"],
        cwd=tmp_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stderr
    assert "cc-guide" in result.stdout
    assert "build/cc_guide" in result.stdout
    item = entry("cc-guide")
    assert expected_shell(
        item["dir"], expected_argv(item, "3.13")
    ) in result.stdout


# spec: "Its header says \"nine\"."
# task: 6
def test_commit_lint_header_says_nine():
    text = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    header = []
    for line in text.splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            break
        header.append(line)
    assert re.search(r"\bnine\b", "\n".join(header), re.IGNORECASE)


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_registry_check_is_the_ninth_literal_lint():
    text = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    commands = re.findall(r"(?m)^[ \t]*run[ \t]+.+$", text)
    assert len(commands) == 9
    assert commands[-1].strip() == (
        "run suite_registry uv run --python 3.13 "
        "python build/run_suites.py --check"
    )
    assert sum("run_suites.py" in command for command in commands) == 1


# spec: "`build/run_commit_lints.sh` keeps its literal commands."
# task: 6
def test_existing_literal_lint_commands_are_preserved():
    before = git(
        ROOT, "show", "456e3fb:build/run_commit_lints.sh", check=False
    )
    if before.returncode:
        pytest.skip("The spec's historical commit 456e3fb is unavailable")
    after = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    pattern = r"(?m)^[ \t]*run[ \t]+.+$"
    old_commands = re.findall(pattern, before.stdout)
    new_commands = [
        command for command in re.findall(pattern, after)
        if not re.match(r"\s*run\s+suite_registry\s", command)
    ]
    assert new_commands == old_commands


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_tests_include_the_new_check_and_regression():
    path = ROOT / "build/test_commit_lints.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    checks = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "CHECKS"
            for target in targets
        ):
            checks.append(node.value)
    assert checks
    assert any(
        isinstance(node, ast.Constant) and node.value == "suite_registry"
        for value in checks for node in ast.walk(value)
    )
    assert any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "test_unregistered_suite_is_refused"
        for node in ast.walk(tree)
    )


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
@pytest.mark.skipif(
    shutil.which("uv") is None,
    reason="The commit-lint integration requires uv.",
)
def test_unregistered_suite_is_refused(tmp_path):
    clone = tmp_path / "clone"
    git(ROOT, "clone", "--no-hardlinks", str(ROOT), str(clone))

    relative = (
        f"skills/acceptance-{tmp_path.name}/scripts/test_new.py"
    )
    new_test = clone / relative
    new_test.parent.mkdir(parents=True)
    new_test.write_text(
        "def test_new():\n    assert True\n", encoding="utf-8"
    )
    git(clone, "add", relative)

    hooks = tmp_path / "hooks"
    hooks.mkdir()
    hook = hooks / "pre-commit"
    hook.write_text(
        "#!/bin/sh\nexec bash build/run_commit_lints.sh\n",
        encoding="utf-8",
    )
    hook.chmod(0o755)
    commit = git(
        clone,
        "-c", f"core.hooksPath={hooks}",
        "-c", "user.name=Acceptance Test",
        "-c", "user.email=acceptance@example.invalid",
        "commit", "-m", "Add an unregistered suite",
        check=False,
    )
    assert commit.returncode != 0
    assert "suite_registry" in commit.stdout + commit.stderr

    # Check the individual literal commands so this assertion does not depend
    # on an unspecified format for the shell script's failure summary.
    script = (clone / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    commands = re.findall(
        r"(?m)^[ \t]*run[ \t]+(\S+)[ \t]+(.+)$", script
    )
    assert len(commands) == 9
    failed = set()
    diagnostics = {}
    for name, command in commands:
        result = subprocess.run(
            ["bash", "-c", command],
            cwd=clone,
            env=git_environment(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode:
            failed.add(name)
            diagnostics[name] = result.stdout + result.stderr
    assert failed == {"suite_registry"}, diagnostics


# spec: "`build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_documentation_names_the_registry_and_ninth_lint():
    text = (ROOT / "build/CLAUDE.md").read_text(encoding="utf-8")
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    paragraphs = re.split(r"\n\s*\n", text)
    assert any(
        all(token in paragraph for token in (
            "suites.toml", "run_suites.py", "--check", "commit lint"
        ))
        for paragraph in paragraphs
    )


# spec: "`bash build/run_commit_lints.sh` prints `commit lints passed`."
# task: 6
@pytest.mark.skipif(
    shutil.which("uv") is None,
    reason="The commit-lint gate requires uv.",
)
def test_repository_commit_lints_pass():
    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=ROOT,
        env=git_environment(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "commit lints passed" in result.stdout + result.stderr


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_documentation_contains_the_four_runner_commands():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    prefix = "uv run --python 3.13 python build/run_suites.py"
    commands = [
        f"{prefix} --list",
        f"{prefix} <name> [--extras] [-- <pytest args>]",
        f"{prefix} --all",
        f"{prefix} --check",
    ]
    positions = [text.index(command) for command in commands]
    assert positions == sorted(positions)
    fences = re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
    assert any(
        all(command in block for command in commands)
        and any(line.lstrip().startswith("#") for line in block.splitlines())
        for block in fences
    )


# spec: "Name `build/suites.toml` and `build/run_suites.py`, and say that the runner prints a suite's notes before it runs."
# task: 7
def test_root_intro_references_both_files_on_one_line():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    lines = [
        line for line in text.splitlines()
        if "build/suites.toml" in line and "build/run_suites.py" in line
    ]
    assert len(lines) == 1
    line = lines[0]
    assert "uv" in line
    assert "3.13" in line
    assert "test_build.py" in line
    assert "director" in line.lower()
    assert "notes" in line.lower()
    assert "There is no root test runner" not in text


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_documentation_has_no_literal_directory_suite_command():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    suite_dirs = {item["dir"] for item in real_data()["suite"]}
    for line in text.splitlines():
        if not line.lstrip().startswith("cd "):
            continue
        tokens = shlex.split(line)
        if len(tokens) >= 3 and tokens[2] == "&&":
            assert tokens[1] not in suite_dirs


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_existing_selection_and_tool_commands_stay_literal():
    before = historical_claude().splitlines()
    after = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    protected = []
    command_start = re.compile(
        r"^(?:uv\s|python(?:3)?\s|bash\s|\./|cd\s|[A-Z_][A-Z_0-9]*=)"
    )
    for number, line in enumerate(before, 1):
        if 66 <= number <= 125 or number == 145:
            continue
        if command_start.match(line.lstrip()):
            protected.append(line)
    assert protected
    for line in protected:
        assert line in after


# spec: "Line 133 is not touched (plan 53's Task 7 edits it)."
# task: 7
def test_original_line_133_is_preserved():
    before = historical_claude().splitlines()
    after = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()
    assert before[132] in after


# spec: "The comment names the suite `run_suites.py cc-guide` instead of \"its suite\"."
# task: 7
def test_cc_guide_comment_uses_the_spec_suite_name():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "run_suites.py cc-guide" in text


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_root_first_line_is_a_versioned_cc_guide_stamp():
    first = (ROOT / "CLAUDE.md").read_text(
        encoding="utf-8"
    ).splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .+ @\S+ -->", first)


# spec: "`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`."
# task: 6
def test_runner_and_its_tests_are_committed():
    for relative in ("build/run_suites.py", "build/test_run_suites.py"):
        result = subprocess.run(
            ["git", "show", f"HEAD:{relative}"],
            cwd=ROOT,
            env=git_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert result.returncode == 0, result.stderr.decode()
        assert result.stdout == (ROOT / relative).read_bytes()
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`.</plan></flag>
<flag task="2"><spec>Default `['3.13']`.</spec><plan>DEFAULT_PYTHONS = ('3.12',)</plan></flag>
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
Worktree-isolated sessions and their subagents have refused compound shell such as `cd X && Y` (seen on 2026-10-12).
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
"This work lands whole, registry and CLAUDE.md shrink, ahead of plan 52's Task 6.
Task 6 then adds one build/suites.toml entry instead of editing Commands.
Plan 52's planning session amends its plan to match and records Q4 as (c)."
Rejected: a Python list inside the runner (every suite change becomes a code edit), and one manifest per suite directory (`install.py` copies skill directories, so the manifests would ship with installed skills).
An `@`-imported document was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
**Design section 1** (the registry keys and the runner's behaviour) was approved as presented.
It is R1–R3 below.
**Design section 2** (the guard, the file edits, the tests and the couplings) was approved as presented.
It is R4–R7 below.
They are selections or tools, not directory suites, and their comments say when to run them:
Every command, dependency and note survives; the only change is the form.
Examples: `build`'s missing `build/.scratch/` in a fresh clone or worktree; `bayesian-workflow`'s `CALIBRATION_SWEEP=1` sweep and its expected arviz warnings; `llm-wiki`'s `@needs_pilot` tests and `$LLM_WIKI_ROOT`; `brainstorming`'s node skip; `tune-hyperparameters`' "`--with sklearn` fails"; `track-model-experiments`' run time; the guard's 3.9 floor, its launchd-PATH skips and its Gate B probe for `hooks`.
`CALIBRATION_SWEEP=1 uv run --python 3.13 python build/run_suites.py bayesian-workflow -- -s` therefore runs the sweep.
Drop "There is no root test runner" and the sentence that comments name the skip-unlocking deps.
Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason.
The commit-lint comment names the suite-registry check and says "nine".
Same number of lines.
The file ends at about 145 lines.
The new text states no count of suites or tests (the `claude-md-count-claims` check).
The deletion of lines 66–125 is bounded by two lines that no other plan edits: the `# Full build-directory tests` comment and the `cd hooks && …` command.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
`build/test_check_conformance.py`: `test_claude_md_import_resolves_passes_on_the_repo` asserts `'@needs_pilot' in text` as its positive control, and that note moves to the registry.
A naive scan would flag the `@` in it, and the stamp keeps its form when its version changes.
No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
The new files are the owner's original tooling.
The register's deviation `claude-md-serves-codex-gemini` still holds as written: a condensed Commands block stays in the root file, and the registry is a plain file that every runtime can read.
`build/test_run_suites.py`, stdlib and pytest only, which the build suite collects.
Write each test before its code and see it fail first (red, then green).
Under decision 2, plan 52's Task 6 drops its `CLAUDE.md:commands-moved` and `CLAUDE.md:commands` edits and adds one `[[suite]]` entry for `skills/write-with-asd-ste100/scripts` instead.
Its expectations of 199 and 197 lines (Task 1, DF19, Q4, Coupling (e)) change with it.
Its `CLAUDE.md:sources` and `CLAUDE.md:bullet` edits are outside the Commands block and still apply.
A note in the session group's shared notes folder gives the exact entry.
Until plan 52 adds the entry, the ninth lint refuses its new suite directory.
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
It also checks each comment's skip-unlocking deps against that suite's `extras`.
Run `hooks`, `build` and `bayesian-workflow` once directly and once through the runner, in the same checkout.
Their pytest summary lines match.
Then run `--all` once, and record each run's result beside the direct result.
The build suite passes (where the missing `build/.scratch/` lets it).
The Stage 2 audit passes, and the behaviour runs match.
The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
The commit hook runs one more fast, stdlib-only check.
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
It would need node, a 3.9 `/usr/bin/python3` and `build/.scratch/`.
Revisit if: the owner wants suites in CI.
Parallel runs, per-suite timeouts and machine-readable output.
Revisit if: `--all` gets slow or a tool needs to parse its results.
Moving the lint, snippet, JAX, smoke, rebuild and citation commands into the runner.
Revisit if: `CLAUDE.md` nears its limit again.
</untestable>