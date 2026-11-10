<tests>
import ast
import copy
import hashlib
import io
import json
import os
import re
import runpy
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

import run_suites as runner


ROOT = Path(runner.__file__).resolve().parent.parent
REGISTRY_PATH = Path("build/suites.toml")

# name: (directory, dependencies after pytest, extras, interpreters)
INVENTORY = {
    "bayesian-workflow": (
        "skills/bayesian-workflow/scripts",
        ("arviz", "arviz-stats", "numpy", "xarray"),
        ("matplotlib",),
        ("3.13",),
    ),
    "brainstorming": (
        "skills/brainstorming/scripts", (), (), ("3.13",),
    ),
    "build": (
        "build",
        ("numpy", "polars", "pyyaml"),
        (
            "arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots",
            "numpyro", "jax", "matplotlib",
        ),
        ("3.13",),
    ),
    "cc-guide": ("build/cc_guide", (), (), ("3.13",)),
    "classification-codes": (
        "skills/classification-codes/scripts", ("polars",), (), ("3.13",),
    ),
    "describe-critique-methodology": (
        "skills/describe-critique-methodology/scripts", (), (), ("3.13",),
    ),
    "design-architecture": (
        "skills/design-architecture/scripts", (), (), ("3.13",),
    ),
    "explore-data": (
        "skills/explore-data/scripts", ("polars",), (), ("3.13",),
    ),
    "geographic-codes": (
        "skills/geographic-codes/scripts",
        ("polars", "fastexcel"), (), ("3.13",),
    ),
    "hooks": ("hooks", (), (), ("3.13", "/usr/bin/python3")),
    "llm-wiki": ("skills/llm-wiki/scripts", (), (), ("3.13",)),
    "recommend-probabilistic-model": (
        "skills/recommend-probabilistic-model/scripts",
        ("numpy", "polars"), (), ("3.13",),
    ),
    "recommend-visualization": (
        "skills/recommend-visualization/scripts",
        ("numpy", "polars"), (), ("3.13",),
    ),
    "subagent-driven-development": (
        "skills/subagent-driven-development/scripts", (), (), ("3.13",),
    ),
    "systematic-debugging": (
        "skills/systematic-debugging", (), (), ("3.13",),
    ),
    "track-model-experiments": (
        "skills/track-model-experiments/scripts",
        ("numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"),
        (),
        ("3.13",),
    ),
    "tune-hyperparameters": (
        "skills/tune-hyperparameters/scripts",
        ("numpy", "polars"), ("scikit-learn", "optuna"), ("3.13",),
    ),
    "writing-plans": (
        "skills/writing-plans/scripts", (), (), ("3.13",),
    ),
}


def suite_for(name):
    directory, dependencies, extras, pythons = INVENTORY[name]
    return runner.Suite(
        name=name,
        dir=directory,
        deps=("pytest", *dependencies),
        extras=extras,
        pythons=pythons,
    )


def fixture_data():
    return {
        "suite": [
            {
                "name": "build",
                "dir": "build",
                "with": ["pytest", "numpy", "polars", "pyyaml"],
                "extras": ["arviz>=1.0", "matplotlib"],
                "notes": ["build/.scratch/"],
            },
            {
                "name": "cc-guide",
                "dir": "build/cc_guide",
                "with": ["pytest"],
            },
            {
                "name": "hooks",
                "dir": "hooks",
                "with": ["pytest"],
                "pythons": ["3.13", "/usr/bin/python3"],
                "notes": ["3.9", "launchd-PATH", "Gate B"],
            },
        ],
    }


def write_registry(root, data):
    path = root / REGISTRY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in data.items():
        if (
            key == "suite"
            and isinstance(value, list)
            and all(isinstance(entry, dict) for entry in value)
        ):
            for entry in value:
                lines.append("[[suite]]")
                lines.extend(
                    f"{field} = {json.dumps(item)}"
                    for field, item in entry.items()
                )
                lines.append("")
        else:
            lines.append(f"{key} = {json.dumps(value)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def git(root, *arguments, check=True):
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=check,
        capture_output=True,
        text=True,
    )


def make_root(tmp_path, data=None, initialize_git=False):
    root = tmp_path / "repo"
    root.mkdir()
    for entry in fixture_data()["suite"]:
        directory = root / entry["dir"]
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "test_new.py").write_text(
            "def test_new():\n    assert True\n", encoding="utf-8",
        )
    write_registry(root, fixture_data() if data is None else data)
    if initialize_git:
        git(root, "init", "--quiet")
    return root


def expected_argv(python, dependencies, arguments=()):
    result = ["uv", "run", "--python", python]
    for dependency in dependencies:
        result.extend(("--with", dependency))
    result.extend(("python", "-m", "pytest", "-q"))
    result.extend(arguments)
    return tuple(result)


def forbid_run(root, run):
    pytest.fail(f"Unexpected suite execution: {run.label}")


def real_data():
    return tomllib.loads((ROOT / REGISTRY_PATH).read_text(encoding="utf-8"))


def lint_commands(text):
    logical_lines = text.replace("\\\n", " ").splitlines()
    result = []
    for line in logical_lines:
        words = shlex.split(line, comments=True)
        if words and words[0] == "run":
            result.append((words[1], words[2:]))
    return result


INVALID_CASES = (
    "missing:name",
    "missing:dir",
    "missing:with",
    "unknown:suite",
    "unknown:root",
    "wrong:name",
    "wrong:dir",
    "wrong:with",
    "wrong:with:item",
    "wrong:extras",
    "wrong:extras:item",
    "wrong:pythons",
    "wrong:pythons:item",
    "wrong:notes",
    "wrong:notes:item",
    "wrong:suite",
    "wrong:suite:item",
    "duplicate:name",
    "duplicate:dir",
    "without:pytest",
)


def invalid_data(case):
    data = copy.deepcopy(fixture_data())
    entry = data["suite"][0]
    operation, key, *suffix = case.split(":")
    if operation == "missing":
        del entry[key]
    elif operation == "unknown":
        if key == "root":
            data["withh"] = ["pytest"]
        else:
            entry["withh"] = ["pytest"]
    elif operation == "wrong":
        if key == "suite":
            data["suite"] = [3] if suffix else "build"
        elif key in {"name", "dir"}:
            entry[key] = 3
        else:
            entry[key] = [3] if suffix else "pytest"
    elif operation == "duplicate":
        data["suite"][1][key] = entry[key]
    elif operation == "without":
        entry["with"] = ["numpy"]
    return data


@pytest.fixture
def transcript(monkeypatch):
    stream = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stream)
    monkeypatch.setattr(sys, "stderr", stream)
    return stream


@pytest.fixture
def fake_uv(tmp_path, monkeypatch):
    directory = tmp_path / "bin"
    directory.mkdir()
    record = tmp_path / "uv-record.json"
    executable = directory / "uv"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import hashlib, json, os, sys\n"
        "from pathlib import Path\n"
        "environment = json.dumps(dict(os.environ), sort_keys=True).encode()\n"
        "result = {\n"
        "    'argv': sys.argv[1:],\n"
        "    'cwd': os.getcwd(),\n"
        "    'environment': hashlib.sha256(environment).hexdigest(),\n"
        "}\n"
        f"Path({str(record)!r}).write_text(json.dumps(result))\n"
        "os.write(1, b'pytest stdout\\n')\n"
        "os.write(2, b'pytest stderr\\n')\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(directory))
    return record


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 2
def test_repo_constant_comes_from_runner_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.REPO == ROOT


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_imports_only_standard_library_modules():
    tree = ast.parse(Path(runner.__file__).read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            imports.append((node.module or "").split(".")[0])
    assert set(imports) <= sys.stdlib_module_names


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
@pytest.mark.parametrize("case", INVALID_CASES)
def test_validation_rejects_each_schema_failure(case):
    findings = runner.validate(invalid_data(case))
    assert findings
    assert all(isinstance(finding, str) and finding for finding in findings)


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
@pytest.mark.parametrize("case", INVALID_CASES)
@pytest.mark.parametrize("arguments", [("--list",), ("build",), ("--all",)])
def test_invalid_registry_prevents_every_execution_mode(
    tmp_path, case, arguments,
):
    root = make_root(tmp_path, invalid_data(case))
    assert runner.main(
        list(arguments), root=root, run_one=forbid_run,
    ) == 2


# spec: "Validation fails closed."
# task: 4
@pytest.mark.parametrize(
    ("arguments", "status"),
    [
        (["--list"], 2),
        (["build"], 2),
        (["--all"], 2),
        (["--check"], 1),
    ],
)
def test_malformed_toml_never_runs_a_suite(tmp_path, arguments, status):
    root = make_root(tmp_path, initialize_git=True)
    (root / REGISTRY_PATH).write_text("[[suite]\n", encoding="utf-8")
    assert runner.main(arguments, root=root, run_one=forbid_run) == status


# spec: "The entries carry the text of today's commands and comments."
# task: 2
def test_parse_preserves_explicit_values_and_applies_optional_defaults():
    data = fixture_data()
    assert runner.validate(data) == []
    suites = runner.parse(data)
    assert [suite.name for suite in suites] == ["build", "cc-guide", "hooks"]

    build, guide, hooks = suites
    assert build.dir == "build"
    assert build.deps == ("pytest", "numpy", "polars", "pyyaml")
    assert build.extras == ("arviz>=1.0", "matplotlib")
    assert build.notes == ("build/.scratch/",)
    assert build.pythons == ("3.13",)

    assert guide.dir == "build/cc_guide"
    assert guide.deps == ("pytest",)
    assert guide.extras == ()
    assert guide.notes == ()
    assert guide.pythons == ("3.13",)

    assert hooks.pythons == ("3.13", "/usr/bin/python3")


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
@pytest.mark.parametrize("name", list(INVENTORY))
def test_default_commands_match_the_spec_inventory(name):
    suite = suite_for(name)
    runs = runner.runs(suite)
    assert [run.python for run in runs] == list(INVENTORY[name][3])
    assert [run.argv for run in runs] == [
        expected_argv(python, ("pytest", *INVENTORY[name][1]))
        for python in INVENTORY[name][3]
    ]
    for run in runs:
        assert run.shell() == (
            f"cd {shlex.quote(suite.dir)} && {shlex.join(run.argv)}"
        )


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 2
def test_hooks_has_two_separate_shell_forms():
    runs = runner.runs(suite_for("hooks"))
    assert [run.shell() for run in runs] == [
        "cd hooks && uv run --python 3.13 --with pytest python -m pytest -q",
        (
            "cd hooks && uv run --python /usr/bin/python3 "
            "--with pytest python -m pytest -q"
        ),
    ]


# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
@pytest.mark.parametrize("name", list(INVENTORY))
def test_extras_are_opt_in_and_follow_default_dependencies(name):
    suite = suite_for(name)
    default = runner.runs(suite)
    expanded = runner.runs(suite, extras=True)
    assert [run.argv for run in default] == [
        expected_argv(python, suite.deps) for python in suite.pythons
    ]
    assert [run.argv for run in expanded] == [
        expected_argv(python, (*suite.deps, *suite.extras))
        for python in suite.pythons
    ]


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_dependency_constraints_and_pytest_expressions():
    suite = suite_for("build")
    arguments = ("-k", "declared_dependencies or test_real_skill", "-s", "-rs")
    run = runner.runs(suite, extras=True, pytest_args=arguments)[0]
    expected = expected_argv(
        "3.13", (*suite.deps, *suite.extras), arguments,
    )
    assert run.argv == expected
    assert shlex.split(run.shell()) == ["cd", "build", "&&", *expected]
    assert "'arviz>=1.0'" in run.shell()
    assert "'declared_dependencies or test_real_skill'" in run.shell()


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_cli_forwards_pytest_arguments_to_every_interpreter(tmp_path):
    root = make_root(tmp_path)
    arguments = (
        "test_new.py::test_new",
        "-k", "declared_dependencies",
        "-s", "-rs",
    )
    seen = []

    def record(root, run):
        seen.append(run)
        return 0

    assert runner.main(
        ["hooks", "build", "--", *arguments],
        root=root,
        run_one=record,
    ) == 0
    assert len(seen) == 3
    for run in seen:
        assert run.argv[-len(arguments):] == arguments
        assert "--" not in run.argv


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_defaults_to_all_suites_without_running_them(
    tmp_path, capsys,
):
    root = make_root(tmp_path)
    assert runner.main(["--list"], root=root, run_one=forbid_run) == 0
    output = capsys.readouterr().out
    for suite in runner.parse(fixture_data()):
        assert suite.name in output
        assert suite.dir in output
        for run in runner.runs(suite):
            assert run.shell() in output
        for extra in suite.extras:
            assert extra in output
        for note in suite.notes:
            assert note in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
@pytest.mark.parametrize("extras", [False, True])
def test_list_named_suites_prints_the_requested_commands(
    tmp_path, capsys, extras,
):
    root = make_root(tmp_path)
    arguments = ("-k", "declared_dependencies", "-rs")
    cli = ["--list", "hooks", "build"]
    if extras:
        cli.append("--extras")
    cli.extend(("--", *arguments))
    assert runner.main(cli, root=root, run_one=forbid_run) == 0

    output = capsys.readouterr().out
    assert "cc-guide" not in output
    positions = []
    by_name = {suite.name: suite for suite in runner.parse(fixture_data())}
    for name in ("hooks", "build"):
        suite = by_name[name]
        for run in runner.runs(
            suite, extras=extras, pytest_args=arguments,
        ):
            positions.append(output.index(run.shell()))
    assert positions == sorted(positions)


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_suites_run_in_requested_order(tmp_path):
    root = make_root(tmp_path)
    seen = []

    def record(actual_root, run):
        assert actual_root == root
        seen.append((run.suite.name, run.python))
        return 0

    assert runner.main(
        ["hooks", "build"], root=root, run_one=record,
    ) == 0
    assert seen == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("build", "3.13"),
    ]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_are_visible_before_execution(
    tmp_path, transcript,
):
    root = make_root(tmp_path)
    suites = runner.parse(fixture_data())
    by_name = {suite.name: suite for suite in suites}
    seen = []

    def record(actual_root, run):
        output = transcript.getvalue()
        header = f"== {run.suite.name} ({run.python})"
        header_position = output.rfind(header)
        assert header_position >= 0
        previous = [
            item for item in seen if item[0] == run.suite.name
        ]
        if not previous:
            for note in run.suite.notes:
                assert output.find(note, header_position) > header_position
        else:
            for note in run.suite.notes:
                assert note not in output[header_position:]
        seen.append((run.suite.name, run.python))
        print("pytest output")
        return 0

    assert runner.execute(
        root, [by_name["hooks"], by_name["build"]], False, (), record,
    ) == 0
    output = transcript.getvalue()
    for suite in (by_name["hooks"], by_name["build"]):
        for note in suite.notes:
            assert output.count(note) == 1


# spec: "A failed run does not stop the next one."
# task: 4
def test_failures_do_not_prevent_later_runs(tmp_path, transcript):
    root = make_root(tmp_path)
    results = iter((5, 0, 1))
    seen = []

    def record(actual_root, run):
        seen.append((run.suite.name, run.python))
        return next(results)

    assert runner.main(
        ["hooks", "build"], root=root, run_one=record,
    ) == 1
    assert seen == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("build", "3.13"),
    ]
    last_line = transcript.getvalue().strip().splitlines()[-1]
    assert "hooks (3.13)" in last_line
    assert "build (3.13)" in last_line
    assert "hooks (/usr/bin/python3)" not in last_line


# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize(
    ("results", "expected_status"),
    [
        ((0, 0), 0),
        ((1, 0), 1),
        ((0, 1), 1),
        ((5, 0), 1),
        ((0, 5), 1),
    ],
)
def test_exit_status_aggregates_all_interpreters(
    tmp_path, results, expected_status, transcript,
):
    root = make_root(tmp_path)
    pending = iter(results)
    calls = []

    def record(actual_root, run):
        calls.append(run)
        return next(pending)

    assert runner.main(
        ["hooks"], root=root, run_one=record,
    ) == expected_status
    assert len(calls) == 2
    last_line = transcript.getvalue().strip().splitlines()[-1]
    if expected_status == 0:
        assert "pass" in last_line.lower()
        assert "fail" not in last_line.lower()
    else:
        for run, status in zip(calls, results):
            if status:
                assert f"hooks ({run.python})" in last_line


# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize(
    "arguments",
    [
        ["unknown-suite"],
        ["--list", "unknown-suite"],
        ["--unknown-option"],
    ],
)
def test_usage_and_unknown_suite_errors_have_status_two(
    tmp_path, arguments,
):
    root = make_root(tmp_path)
    assert runner.main(
        arguments, root=root, run_one=forbid_run,
    ) == 2


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_is_a_failed_run_and_does_not_abort_the_suite(
    tmp_path, monkeypatch, transcript,
):
    root = make_root(tmp_path)
    monkeypatch.setenv("PATH", str(tmp_path / "missing-bin"))
    assert runner.main(
        ["hooks"], root=root, run_one=runner.run_subprocess,
    ) == 1
    output = transcript.getvalue()
    assert "== hooks (3.13)" in output
    assert "== hooks (/usr/bin/python3)" in output
    last_line = output.strip().splitlines()[-1]
    assert "hooks (3.13)" in last_line
    assert "hooks (/usr/bin/python3)" in last_line


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 4
def test_subprocess_receives_exact_argv_and_suite_working_directory(
    tmp_path, fake_uv,
):
    root = make_root(tmp_path)
    run = runner.runs(
        suite_for("build"),
        extras=True,
        pytest_args=("-k", "declared_dependencies", "-rs"),
    )[0]
    assert runner.run_subprocess(root, run) == 0
    record = json.loads(fake_uv.read_text(encoding="utf-8"))
    assert record["argv"] == list(run.argv[1:])
    assert Path(record["cwd"]) == root / "build"


# spec: "Then pytest's output streams."
# task: 4
def test_subprocess_output_streams_to_the_callers_streams(
    tmp_path, fake_uv, capfd,
):
    root = make_root(tmp_path)
    run = runner.runs(suite_for("hooks"))[0]
    assert runner.run_subprocess(root, run) == 0
    output = capfd.readouterr()
    assert "pytest stdout" in output.out
    assert "pytest stderr" in output.err


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_inherits_the_complete_environment(
    tmp_path, fake_uv, monkeypatch,
):
    root = make_root(tmp_path)
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    before = dict(os.environ)
    expected_digest = hashlib.sha256(
        json.dumps(before, sort_keys=True).encode(),
    ).hexdigest()
    run = runner.runs(suite_for("hooks"))[0]
    assert runner.run_subprocess(root, run) == 0
    record = json.loads(fake_uv.read_text(encoding="utf-8"))
    assert record["environment"] == expected_digest
    assert dict(os.environ) == before


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_recognizes_directory_ancestry():
    build = suite_for("build")
    guide = suite_for("cc-guide")
    hooks = suite_for("hooks")
    suites = [build, guide, hooks]
    assert runner.container(guide, suites) == build
    assert runner.container(build, suites) is None
    assert runner.container(hooks, suites) is None


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_directory_containment_is_not_a_string_prefix():
    outer = runner.Suite("build", "build", ("pytest",))
    sibling = runner.Suite("hooks", "build-other", ("pytest",))
    assert runner.container(sibling, [outer, sibling]) is None


# spec: "`--all` prints one line for each suite that it skips."
# task: 4
def test_all_skips_nested_suite_and_reports_the_skip(
    tmp_path, capsys,
):
    root = make_root(tmp_path)
    seen = []

    def record(actual_root, run):
        seen.append((run.suite.name, run.python))
        return 0

    assert runner.main(["--all"], root=root, run_one=record) == 0
    assert seen == [
        ("build", "3.13"),
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
    ]
    lines = capsys.readouterr().out.splitlines()
    skip_lines = [
        line for line in lines
        if "skip" in line.lower() and "cc-guide" in line
    ]
    assert len(skip_lines) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_a_named_nested_suite_runs(tmp_path):
    root = make_root(tmp_path)
    seen = []

    def record(actual_root, run):
        seen.append(run.suite.name)
        return 0

    assert runner.main(
        ["cc-guide"], root=root, run_one=record,
    ) == 0
    assert seen == ["cc-guide"]


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
@pytest.mark.parametrize("case", INVALID_CASES)
def test_check_reports_invalid_registry_as_findings(tmp_path, case):
    data = invalid_data(case)
    root = make_root(tmp_path, data, initialize_git=True)
    findings = runner.check(root, data)
    assert findings
    assert all(isinstance(line, str) and line for line in findings)
    assert len(findings) >= len(runner.validate(data))


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
@pytest.mark.parametrize("case", INVALID_CASES)
def test_check_cli_uses_status_one_for_registry_findings(
    tmp_path, case, capsys,
):
    data = invalid_data(case)
    root = make_root(tmp_path, data, initialize_git=True)
    findings = runner.check(root, data)
    assert runner.main(
        ["--check"], root=root, run_one=forbid_run,
    ) == 1
    output = capsys.readouterr()
    lines = (output.out + output.err).splitlines()
    assert len(lines) == len(findings)
    assert all(line.strip() for line in lines)
    assert "suite registry ok" not in lines


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize("filename", ["test_new.py", "new_test.py"])
@pytest.mark.parametrize("tracked", [False, True])
def test_check_finds_unregistered_directories_for_both_pytest_patterns(
    tmp_path, filename, tracked,
):
    root = make_root(tmp_path, initialize_git=True)
    directory = Path("skills/writing-plans/scripts")
    path = root / directory / filename
    path.parent.mkdir(parents=True)
    path.write_text("def test_new():\n    assert True\n", encoding="utf-8")
    if tracked:
        git(root, "add", str(path.relative_to(root)))

    assert directory.as_posix() in runner.pytest_dirs(root)
    findings = runner.check(root, fixture_data())
    assert len(findings) == 1
    assert directory.as_posix() in findings[0]


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize(
    "filename", ["test_new.txt", "testnew.py", "new_tests.py"],
)
def test_check_does_not_treat_other_filenames_as_pytest_files(
    tmp_path, filename,
):
    root = make_root(tmp_path, initialize_git=True)
    path = root / "skills/writing-plans/scripts" / filename
    path.parent.mkdir(parents=True)
    path.write_text("", encoding="utf-8")
    assert runner.check(root, fixture_data()) == []


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_reports_a_missing_registered_directory(tmp_path):
    root = make_root(tmp_path, initialize_git=True)
    data = fixture_data()
    data["suite"].append({
        "name": "writing-plans",
        "dir": "skills/writing-plans/scripts",
        "with": ["pytest"],
    })
    findings = runner.check(root, data)
    assert len(findings) == 1
    assert "skills/writing-plans/scripts" in findings[0]


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_reports_a_registered_directory_without_tests(tmp_path):
    root = make_root(tmp_path, initialize_git=True)
    directory = root / "skills/writing-plans/scripts"
    directory.mkdir(parents=True)
    (directory / "run_suites.py").write_text("", encoding="utf-8")
    data = fixture_data()
    data["suite"].append({
        "name": "writing-plans",
        "dir": "skills/writing-plans/scripts",
        "with": ["pytest"],
    })
    findings = runner.check(root, data)
    assert len(findings) == 1
    assert "skills/writing-plans/scripts" in findings[0]


# spec: "Today that is `cc-guide`: `cd build && pytest` collects `build/cc_guide` already."
# task: 3
def test_tests_in_descendants_satisfy_a_registered_parent_suite(tmp_path):
    root = make_root(tmp_path, initialize_git=True)
    (root / "build/test_new.py").unlink()
    data = fixture_data()
    data["suite"] = [
        entry for entry in data["suite"] if entry["name"] != "cc-guide"
    ]
    assert runner.check(root, data) == []


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_coverage_uses_path_components_not_string_prefixes(tmp_path):
    root = make_root(tmp_path, initialize_git=True)
    path = root / "build-other/test_new.py"
    path.parent.mkdir()
    path.write_text("", encoding="utf-8")
    findings = runner.check(root, fixture_data())
    assert len(findings) == 1
    assert "build-other" in findings[0]


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_check_excludes_ignored_worktrees_and_scratch(tmp_path):
    root = make_root(tmp_path, initialize_git=True)
    (root / ".gitignore").write_text(
        ".claude/worktrees/\nbuild/.scratch/\n", encoding="utf-8",
    )
    for relative in (
        ".claude/worktrees/test_new.py",
        "build/.scratch/test_new.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    directories = runner.pytest_dirs(root)
    assert ".claude/worktrees" not in directories
    assert "build/.scratch" not in directories
    assert runner.check(root, fixture_data()) == []


# spec: "The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root."
# task: 3
def test_check_uses_the_supplied_root_despite_an_unrelated_cwd(
    tmp_path, monkeypatch,
):
    root = make_root(tmp_path, initialize_git=True)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert runner.check(root, fixture_data()) == []


# spec: "If git fails, `--check` fails."
# task: 4
def test_check_fails_when_git_cannot_start(tmp_path, monkeypatch):
    root = make_root(tmp_path, initialize_git=True)
    monkeypatch.setenv("PATH", str(tmp_path / "missing-bin"))
    assert runner.main(
        ["--check"], root=root, run_one=forbid_run,
    ) == 1


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_success_has_the_required_output(tmp_path, capsys):
    root = make_root(tmp_path, initialize_git=True)
    assert runner.main(
        ["--check"], root=root, run_one=forbid_run,
    ) == 0
    output = capsys.readouterr()
    assert output.out == "suite registry ok\n"
    assert output.err == ""


# spec: "Every command, dependency and note survives; the only change is the form."
# task: 5
def test_real_registry_contains_the_complete_spec_inventory():
    data = real_data()
    assert runner.validate(data) == []
    entries = {entry["name"]: entry for entry in data["suite"]}
    assert set(INVENTORY) <= set(entries)

    for name, (directory, dependencies, extras, pythons) in INVENTORY.items():
        entry = entries[name]
        assert entry["dir"] == directory
        assert entry["with"] == ["pytest", *dependencies]
        assert entry.get("extras", []) == list(extras)
        assert entry.get("pythons", ["3.13"]) == list(pythons)


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_is_sorted_by_name():
    names = [entry["name"] for entry in real_data()["suite"]]
    assert names == sorted(names)
    assert len(names) == len(set(names))


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_documents_the_schema_and_guard():
    text = (ROOT / REGISTRY_PATH).read_text(encoding="utf-8")
    header = text.split("[[suite]]", 1)[0]
    comments = "\n".join(
        line.lstrip()[1:].strip()
        for line in header.splitlines()
        if line.lstrip().startswith("#")
    )
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert re.search(rf"\b{key}\b", comments)
    assert "sort" in comments.lower()
    assert re.search(r"\b(?:ninth|nine|9th|9)\b", comments, re.IGNORECASE)
    assert "commit lint" in comments.lower()


# spec: "Examples: `build`'s missing `build/.scratch/` in a fresh clone or worktree; `bayesian-workflow`'s `CALIBRATION_SWEEP=1` sweep and its expected arviz warnings; `llm-wiki`'s `@needs_pilot` tests and `$LLM_WIKI_ROOT`; `brainstorming`'s node skip; `tune-hyperparameters`' \"`--with sklearn` fails\"; `track-model-experiments`' run time; the guard's 3.9 floor, its launchd-PATH skips and its Gate B probe for `hooks`."
# task: 5
def test_registry_preserves_the_explicitly_identified_note_content():
    suites = {suite.name: suite for suite in runner.parse(real_data())}
    notes = {
        name: "\n".join(suite.notes)
        for name, suite in suites.items()
    }
    assert "build/.scratch/" in notes["build"]
    assert re.search(r"clone|worktree", notes["build"], re.IGNORECASE)

    assert "CALIBRATION_SWEEP=1" in notes["bayesian-workflow"]
    assert "arviz" in notes["bayesian-workflow"].lower()
    assert "warn" in notes["bayesian-workflow"].lower()

    assert "@needs_pilot" in notes["llm-wiki"]
    assert "$LLM_WIKI_ROOT" in notes["llm-wiki"]

    assert "node" in notes["brainstorming"].lower()
    assert "skip" in notes["brainstorming"].lower()

    assert "--with sklearn" in notes["tune-hyperparameters"]
    assert "fail" in notes["tune-hyperparameters"].lower()

    assert "3.9" in notes["hooks"]
    assert "launchd" in notes["hooks"]
    assert "PATH" in notes["hooks"]
    assert "Gate B" in notes["hooks"]


# spec: "the real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_passes_check(capsys):
    assert runner.main(
        ["--check"], root=ROOT, run_one=forbid_run,
    ) == 0
    output = capsys.readouterr()
    assert output.out == "suite registry ok\n"
    assert output.err == ""


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_script_lists_the_real_registry_from_an_unrelated_directory(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "build/run_suites.py"),
            "--list",
            "hooks",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    for run in runner.runs(suite_for("hooks")):
        assert run.shell() in result.stdout


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_suite_registry_is_the_ninth_literal_commit_lint():
    text = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    commands = lint_commands(text)
    assert len(commands) == 9
    assert commands[-1] == (
        "suite_registry",
        [
            "uv", "run", "--python", "3.13",
            "python", "build/run_suites.py", "--check",
        ],
    )
    assert all(
        "build/run_suites.py" not in command
        for _, command in commands[:-1]
    )


# spec: "Its header says \"nine\"."
# task: 6
def test_commit_lint_header_says_nine():
    text = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    header = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            header.append(line)
        else:
            break
    assert re.search(r"\bnine\b", "\n".join(header), re.IGNORECASE)


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_tests_include_the_registry_check():
    namespace = runpy.run_path(str(ROOT / "build/test_commit_lints.py"))
    assert "suite_registry" in namespace["CHECKS"]
    assert callable(namespace["test_unregistered_suite_is_refused"])


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_committing_a_new_unregistered_suite_fails_only_suite_registry(tmp_path):
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "--quiet", "--no-local", str(ROOT), str(clone)],
        check=True,
        capture_output=True,
        text=True,
    )
    path = clone / "skills/acceptance-suite/scripts/test_new.py"
    path.parent.mkdir(parents=True)
    path.write_text("def test_new():\n    assert True\n", encoding="utf-8")
    git(clone, "add", str(path.relative_to(clone)))

    text = (clone / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    failures = []
    for name, command in lint_commands(text):
        result = subprocess.run(
            command, cwd=clone, capture_output=True, text=True,
        )
        if result.returncode:
            failures.append(name)
    assert failures == ["suite_registry"]

    hooks = tmp_path / "hooks"
    hooks.mkdir()
    hook = hooks / "pre-commit"
    hook.write_text(
        "#!/bin/sh\nexec bash build/run_commit_lints.sh\n",
        encoding="utf-8",
    )
    hook.chmod(0o755)
    before = git(clone, "rev-parse", "HEAD").stdout.strip()
    result = git(
        clone,
        "-c", f"core.hooksPath={hooks}",
        "-c", "user.name=Acceptance Test",
        "-c", "user.email=acceptance@example.invalid",
        "commit", "-m", "Add an unregistered test suite",
        check=False,
    )
    assert result.returncode != 0
    assert "suite_registry" in result.stdout + result.stderr
    assert git(clone, "rev-parse", "HEAD").stdout.strip() == before


# spec: "`build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_documentation_describes_the_ninth_lint():
    text = (ROOT / "build/CLAUDE.md").read_text(encoding="utf-8")
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    assert "suites.toml" in text
    assert "run_suites.py" in text
    assert "--check" in text
    assert "commit lint" in text


# spec: "Name `build/suites.toml` and `build/run_suites.py`, and say that the runner prints a suite's notes before it runs."
# task: 7
def test_root_intro_explains_the_registry_runner_and_notes_on_one_line():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "There is no root test runner" not in text
    introductions = [
        line for line in text.splitlines()
        if "build/suites.toml" in line and "build/run_suites.py" in line
    ]
    assert len(introductions) == 1
    intro = introductions[0]
    assert "uv" in intro
    assert "3.13" in intro
    assert "test_build.py" in intro
    assert re.search(r"director", intro, re.IGNORECASE)
    assert re.search(r"basename|collision", intro, re.IGNORECASE)
    assert "notes" in intro.lower()
    assert "before" in intro.lower()


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_documentation_has_the_four_runner_commands_in_order():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    prefix = "uv run --python 3.13 python build/run_suites.py "
    commands = [
        prefix + "--list",
        prefix + "<name> [--extras] [-- <pytest args>]",
        prefix + "--all",
        prefix + "--check",
    ]
    lines = text.splitlines()
    positions = [lines.index(command) for command in commands]
    assert positions == list(range(positions[0], positions[0] + 4))
    assert lines[positions[0] - 1].lstrip().startswith("#")


# spec: "The commit-lint comment names the suite-registry check and says \"nine\"."
# task: 7
def test_root_commit_lint_comment_names_nine_and_the_registry():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    comments = [
        line for line in text.splitlines()
        if line.lstrip().startswith("#")
    ]
    assert any(
        "nine" in line.lower()
        and re.search(r"suite[-_ ]registry", line, re.IGNORECASE)
        for line in comments
    )


# spec: "The comment names the suite `run_suites.py cc-guide` instead of \"its suite\"."
# task: 7
def test_root_cc_guide_comment_uses_the_required_suite_name():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert any(
        line.lstrip().startswith("#") and "run_suites.py cc-guide" in line
        for line in text.splitlines()
    )


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_documentation_is_under_limit_without_directory_suite_commands():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("cd "):
            continue
        words = shlex.split(stripped, comments=True)
        chunks = []
        start = 0
        for index, word in enumerate(words):
            if word == "&&":
                chunks.append(words[start:index])
                start = index + 1
        chunks.append(words[start:])
        if not chunks or chunks[0][:1] != ["cd"]:
            continue
        for command in chunks[1:]:
            assert command[-4:] != ["python", "-m", "pytest", "-q"]


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_root_first_line_is_the_version_independent_cc_guide_stamp():
    first_line = (ROOT / "CLAUDE.md").read_text(
        encoding="utf-8",
    ).splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .+ @\S+ -->", first_line)


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_old_needs_pilot_positive_control_has_been_removed():
    tree = ast.parse(
        (ROOT / "build/test_check_conformance.py").read_text(
            encoding="utf-8",
        ),
    )
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    for node in ast.walk(function):
        if isinstance(node, ast.Assert):
            assert not any(
                isinstance(value, ast.Constant)
                and value.value == "@needs_pilot"
                for value in ast.walk(node.test)
            )


# spec: "`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`."
# task: 6
def test_runner_and_its_tests_are_tracked():
    git(
        ROOT, "ls-files", "--error-unmatch",
        "build/run_suites.py", "build/test_run_suites.py",
    )


# spec: "`bash build/run_commit_lints.sh` prints `commit lints passed`."
# task: 6
def test_real_commit_lint_gate_passes():
    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "commit lints passed" in result.stdout
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
Worktree-isolated sessions and their subagents have refused compound shell such as `cd X && Y` (seen on 2026-10-12).
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
"This work lands whole, registry and CLAUDE.md shrink, ahead of plan 52's Task 6.
Task 6 then adds one build/suites.toml entry instead of editing Commands.
Plan 52's planning session amends its plan to match and records Q4 as (c)."
Rejected: a Python list inside the runner (every suite change becomes a code edit), and one manifest per suite directory (`install.py` copies skill directories, so the manifests would ship with installed skills).
An `@`-imported document was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
**Design section 1** (the registry keys and the runner's behaviour) was approved as presented.
**Design section 2** (the guard, the file edits, the tests and the couplings) was approved as presented.
On `main` at `456e3fb` there are 18: the 17 in `CLAUDE.md` lines 66–125, and `build/cc_guide`, whose command is line 145.
These commands **stay literal in `CLAUDE.md`**.
They are selections or tools, not directory suites, and their comments say when to run them:
`build/run_commit_lints.sh` keeps its literal commands.
With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character.
Same number of lines.
Line 133 is not touched (plan 53's Task 7 edits it).
The file ends at about 145 lines.
The new text states no count of suites or tests (the `claude-md-count-claims` check).
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
It extracts every `cd <dir> && uv run …` command from lines 66–125 and 145, splitting the hooks `&&` chain into one command per run.
It asserts that the set equals the set of default shell forms that `--list` prints: nothing is missing on either side.
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
CI running the suites (`--all` in `.github/workflows/lints.yml`).
It would need node, a 3.9 `/usr/bin/python3` and `build/.scratch/`.
Size: design.
Revisit if: the owner wants suites in CI.
Parallel runs, per-suite timeouts and machine-readable output.
Size: plan.
Revisit if: `--all` gets slow or a tool needs to parse its results.
Moving the lint, snippet, JAX, smoke, rebuild and citation commands into the runner.
Revisit if: `CLAUDE.md` nears its limit again.
</untestable>