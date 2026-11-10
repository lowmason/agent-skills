<tests>
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tomllib

import pytest


# Place this module in build/, alongside run_suites.py.
RUNNER_PATH = Path(__file__).resolve().with_name("run_suites.py")
MODULE_SPEC = importlib.util.spec_from_file_location(
    "suite_registry_under_test", RUNNER_PATH
)
rs = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = rs
MODULE_SPEC.loader.exec_module(rs)
ROOT = RUNNER_PATH.parent.parent

INVENTORY = [
    (
        "bayesian-workflow",
        "skills/bayesian-workflow/scripts",
        ["pytest", "arviz", "arviz-stats", "numpy", "xarray"],
        ["matplotlib"],
        ["3.13"],
    ),
    (
        "brainstorming",
        "skills/brainstorming/scripts",
        ["pytest"],
        [],
        ["3.13"],
    ),
    (
        "build",
        "build",
        ["pytest", "numpy", "polars", "pyyaml"],
        [
            "arviz>=1.0",
            "arviz-base",
            "arviz-stats",
            "arviz-plots",
            "numpyro",
            "jax",
            "matplotlib",
        ],
        ["3.13"],
    ),
    ("cc-guide", "build/cc_guide", ["pytest"], [], ["3.13"]),
    (
        "classification-codes",
        "skills/classification-codes/scripts",
        ["pytest", "polars"],
        [],
        ["3.13"],
    ),
    (
        "describe-critique-methodology",
        "skills/describe-critique-methodology/scripts",
        ["pytest"],
        [],
        ["3.13"],
    ),
    (
        "design-architecture",
        "skills/design-architecture/scripts",
        ["pytest"],
        [],
        ["3.13"],
    ),
    (
        "explore-data",
        "skills/explore-data/scripts",
        ["pytest", "polars"],
        [],
        ["3.13"],
    ),
    (
        "geographic-codes",
        "skills/geographic-codes/scripts",
        ["pytest", "polars", "fastexcel"],
        [],
        ["3.13"],
    ),
    ("hooks", "hooks", ["pytest"], [], ["3.13", "/usr/bin/python3"]),
    ("llm-wiki", "skills/llm-wiki/scripts", ["pytest"], [], ["3.13"]),
    (
        "recommend-probabilistic-model",
        "skills/recommend-probabilistic-model/scripts",
        ["pytest", "numpy", "polars"],
        [],
        ["3.13"],
    ),
    (
        "recommend-visualization",
        "skills/recommend-visualization/scripts",
        ["pytest", "numpy", "polars"],
        [],
        ["3.13"],
    ),
    (
        "subagent-driven-development",
        "skills/subagent-driven-development/scripts",
        ["pytest"],
        [],
        ["3.13"],
    ),
    (
        "systematic-debugging",
        "skills/systematic-debugging",
        ["pytest"],
        [],
        ["3.13"],
    ),
    (
        "track-model-experiments",
        "skills/track-model-experiments/scripts",
        ["pytest", "numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"],
        [],
        ["3.13"],
    ),
    (
        "tune-hyperparameters",
        "skills/tune-hyperparameters/scripts",
        ["pytest", "numpy", "polars"],
        ["scikit-learn", "optuna"],
        ["3.13"],
    ),
    (
        "writing-plans",
        "skills/writing-plans/scripts",
        ["pytest"],
        [],
        ["3.13"],
    ),
]


def sample_data():
    return {
        "suite": [
            {
                "name": "build",
                "dir": "build",
                "with": ["pytest", "numpy", "polars", "pyyaml"],
                "extras": ["arviz>=1.0", "arviz-base"],
                "notes": ["build/.scratch/", "fresh clone or worktree"],
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
        ]
    }


def registry_text(data):
    lines = []
    for key, value in data.items():
        if key != "suite":
            lines.append(f"{key} = {json.dumps(value)}")
    for entry in data["suite"]:
        lines.append("[[suite]]")
        lines.extend(
            f"{key} = {json.dumps(value)}" for key, value in entry.items()
        )
    return "\n".join(lines) + "\n"


def write_registry(root, data):
    path = root / "build/suites.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(registry_text(data), encoding="utf-8")


def populate_suites(root, data):
    for entry in data["suite"]:
        directory = root / entry["dir"]
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "test_new.py").write_text(
            "def test_new():\n    pass\n", encoding="utf-8"
        )


def clean_git_env():
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }


def git(root, *args, check=True):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        env=clean_git_env(),
        text=True,
        capture_output=True,
        check=check,
    )


def git_repo(root, data=None):
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "--quiet")
    data = sample_data() if data is None else data
    write_registry(root, data)
    populate_suites(root, data)
    git(root, "add", ".")
    return data


def invoke(argv, root, run_one=None):
    kwargs = {"root": root}
    if run_one is not None:
        kwargs["run_one"] = run_one
    try:
        return rs.main(argv, **kwargs)
    except SystemExit as error:
        return error.code


def forbidden_run(root, run):
    pytest.fail(f"Unexpected execution: {run.label}")


def historical(path):
    result = git(ROOT, "show", f"456e3fb:{path}", check=False)
    assert result.returncode == 0, result.stderr
    return result.stdout


def lint_lines(text):
    logical = text.replace("\\\n", " ")
    return [
        line.strip()
        for line in logical.splitlines()
        if line.strip().startswith("run ")
    ]


def assigned_value(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == name
                for target in node.targets
            ):
                return node.value
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                return node.value
    raise AssertionError(f"Missing assignment: {name}")


def invalid_data(case):
    data = sample_data()
    entry = data["suite"][0]

    if case.startswith("missing:"):
        del entry[case.split(":", 1)[1]]
    elif case.startswith("wrong:"):
        key = case.split(":", 1)[1]
        entry[key] = 1 if key in {"name", "dir"} else "pytest"
    elif case.startswith("element:"):
        entry[case.split(":", 1)[1]] = [1]
    elif case == "unknown-suite-key":
        entry["extra"] = ["matplotlib"]
    elif case == "unknown-root-key":
        data["extra"] = []
    elif case == "duplicate-name":
        data["suite"][1]["name"] = entry["name"]
    elif case == "duplicate-directory":
        data["suite"][1]["dir"] = entry["dir"]
    elif case == "without-pytest":
        entry["with"] = ["numpy"]
    else:
        raise AssertionError(case)
    return data


INVALID_CASES = [
    "missing:name",
    "missing:dir",
    "missing:with",
    "wrong:name",
    "wrong:dir",
    "wrong:with",
    "wrong:extras",
    "wrong:pythons",
    "wrong:notes",
    "element:with",
    "element:extras",
    "element:pythons",
    "element:notes",
    "unknown-suite-key",
    "unknown-root-key",
    "duplicate-name",
    "duplicate-directory",
    "without-pytest",
]


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_imports_only_standard_library_modules():
    tree = ast.parse(RUNNER_PATH.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            if node.module:
                imported.add(node.module.split(".")[0])
    assert imported <= sys.stdlib_module_names


# spec: "Default `['3.13']`."
# task: 2
def test_omitted_optional_fields_use_the_spec_defaults():
    suites = rs.parse(
        {
            "suite": [
                {
                    "name": "brainstorming",
                    "dir": "skills/brainstorming/scripts",
                    "with": ["pytest"],
                }
            ]
        }
    )
    suite = suites[0]
    assert list(suite.pythons) == ["3.13"]
    assert list(suite.extras) == []
    assert list(suite.notes) == []
    assert rs.DEFAULT_PYTHONS == ("3.13",)


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
@pytest.mark.parametrize("case", INVALID_CASES)
@pytest.mark.parametrize("argv", [["--list"], ["build"], ["--all"]])
def test_invalid_registry_fails_closed(case, argv, tmp_path):
    data = invalid_data(case)
    assert rs.validate(data)
    write_registry(tmp_path, data)
    assert invoke(argv, tmp_path, forbidden_run) == 2


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
@pytest.mark.parametrize("case", INVALID_CASES)
def test_check_reports_validation_failures(case, tmp_path, capsys):
    git_repo(tmp_path)
    data = invalid_data(case)
    write_registry(tmp_path, data)
    assert rs.check(tmp_path, data)
    assert invoke(["--check"], tmp_path, forbidden_run) == 1
    output = capsys.readouterr()
    assert (output.out + output.err).strip()


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_argv_and_interpreter_order():
    suites = {suite.name: suite for suite in rs.parse(sample_data())}
    build_run = rs.runs(suites["build"])[0]
    assert build_run.argv == (
        "uv",
        "run",
        "--python",
        "3.13",
        "--with",
        "pytest",
        "--with",
        "numpy",
        "--with",
        "polars",
        "--with",
        "pyyaml",
        "python",
        "-m",
        "pytest",
        "-q",
    )
    hooks_runs = rs.runs(suites["hooks"])
    assert [run.python for run in hooks_runs] == [
        "3.13",
        "/usr/bin/python3",
    ]
    assert [run.argv for run in hooks_runs] == [
        (
            "uv", "run", "--python", python,
            "--with", "pytest", "python", "-m", "pytest", "-q",
        )
        for python in ["3.13", "/usr/bin/python3"]
    ]


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_and_quoting():
    suite = rs.parse(sample_data())[0]
    plain = rs.runs(suite)[0]
    assert plain.shell() == (
        "cd build && uv run --python 3.13 "
        "--with pytest --with numpy --with polars --with pyyaml "
        "python -m pytest -q"
    )

    expression = "declared_dependencies or test_real_skill"
    quoted = rs.runs(
        suite, extras=True, pytest_args=("-k", expression)
    )[0]
    assert shlex.split(quoted.shell()) == [
        "cd",
        "build",
        "&&",
        *quoted.argv,
    ]
    assert "--with 'arviz>=1.0'" in quoted.shell()
    assert f"-k {shlex.quote(expression)}" in quoted.shell()


# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_are_opt_in_and_follow_default_dependencies():
    suite = rs.parse(sample_data())[0]
    default = rs.runs(suite)[0]
    expanded = rs.runs(suite, extras=True)[0]
    assert "arviz>=1.0" not in default.argv
    assert expanded.argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest",
        "--with", "numpy",
        "--with", "polars",
        "--with", "pyyaml",
        "--with", "arviz>=1.0",
        "--with", "arviz-base",
        "python", "-m", "pytest", "-q",
    )


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
@pytest.mark.parametrize("argv", [["hooks", "build"], ["--all"]])
def test_pytest_arguments_reach_every_run(argv, tmp_path):
    write_registry(tmp_path, sample_data())
    calls = []
    forwarded = ["test_runtime_support.py", "-k", "test_real_skill", "-s", "-rs"]

    def run_one(root, run):
        calls.append(run)
        return 0

    assert invoke(
        [*argv, "--extras", "--", *forwarded], tmp_path, run_one
    ) == 0
    assert calls
    for run in calls:
        assert list(run.argv[-len(forwarded):]) == forwarded
        assert "--" not in run.argv
        if run.suite.name == "build":
            assert "arviz>=1.0" in run.argv


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
@pytest.mark.parametrize("names", [[], ["hooks"], ["hooks", "build"]])
def test_list_contents_and_selection(names, tmp_path, capsys):
    data = sample_data()
    write_registry(tmp_path, data)
    assert invoke(["--list", *names], tmp_path, forbidden_run) == 0
    output = capsys.readouterr().out
    selected = names or [entry["name"] for entry in data["suite"]]

    for suite in rs.parse(data):
        if suite.name in selected:
            assert suite.name in output
            assert suite.dir in output
            for run in rs.runs(suite):
                assert run.shell() in output
            for extra in suite.extras:
                assert extra in output
            for note in suite.notes:
                assert note in output
        else:
            for run in rs.runs(suite):
                assert run.shell() not in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_matches_the_commands_actually_executed(tmp_path, capsys):
    write_registry(tmp_path, sample_data())
    selection = [
        "hooks",
        "build",
        "--extras",
        "--",
        "-k",
        "declared_dependencies or test_real_skill",
        "-s",
    ]
    assert invoke(["--list", *selection], tmp_path, forbidden_run) == 0
    listed = capsys.readouterr().out
    executed = []

    def run_one(root, run):
        executed.append(run)
        return 0

    assert invoke(selection, tmp_path, run_one) == 0
    assert len(executed) == 3
    for run in executed:
        assert run.shell() in listed


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_order_headers_and_interpreter_order(tmp_path, capsys):
    write_registry(tmp_path, sample_data())
    calls = []

    def run_one(root, run):
        assert root == tmp_path
        calls.append((run.suite.name, run.python))
        return 0

    assert invoke(["hooks", "build", "cc-guide"], tmp_path, run_one) == 0
    assert calls == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("build", "3.13"),
        ("cc-guide", "3.13"),
    ]
    headers = [
        line
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("== ")
    ]
    assert headers == [
        "== hooks (3.13)",
        "== hooks (/usr/bin/python3)",
        "== build (3.13)",
        "== cc-guide (3.13)",
    ]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_notes_print_once_before_the_first_run(tmp_path, capsys):
    data = sample_data()
    write_registry(tmp_path, data)
    observations = []

    def run_one(root, run):
        observations.append(capsys.readouterr().out)
        print(run.python)
        return 0

    assert invoke(["hooks"], tmp_path, run_one) == 0
    first, second = observations
    assert "== hooks (3.13)" in first
    for note in data["suite"][2]["notes"]:
        assert first.index("== hooks (3.13)") < first.index(note)
        assert note not in second
    assert "== hooks (/usr/bin/python3)" in second


# spec: "A failed run does not stop the next one."
# task: 4
@pytest.mark.parametrize("failure", [1, 5])
def test_execution_continues_after_failure(failure, tmp_path, capsys):
    write_registry(tmp_path, sample_data())
    calls = []

    def run_one(root, run):
        calls.append(run.label)
        return failure if len(calls) == 1 else 0

    assert invoke(["hooks", "build"], tmp_path, run_one) == 1
    assert calls == [
        "hooks (3.13)",
        "hooks (/usr/bin/python3)",
        "build (3.13)",
    ]
    captured = capsys.readouterr()
    nonempty = [
        line for line in (captured.out + captured.err).splitlines() if line
    ]
    assert "hooks (3.13)" in nonempty[-1]


# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize(
    ("statuses", "expected"),
    [([0, 0], 0), ([0, 1], 1), ([5, 0], 1), ([1, 5], 1)],
)
def test_aggregate_exit_status_and_final_summary(
    statuses, expected, tmp_path, capsys
):
    write_registry(tmp_path, sample_data())
    remaining = iter(statuses)

    def run_one(root, run):
        return next(remaining)

    assert invoke(["hooks"], tmp_path, run_one) == expected
    captured = capsys.readouterr()
    lines = [
        line for line in (captured.out + captured.err).splitlines() if line
    ]
    last = lines[-1]
    if expected == 0:
        assert re.search(r"\bpass(?:ed)?\b", last, re.IGNORECASE)
    else:
        for python, status in zip(
            ["3.13", "/usr/bin/python3"], statuses, strict=True
        ):
            if status:
                assert f"hooks ({python})" in last


# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize("argv", [[], ["--extras"], ["not-a-suite"], ["--list", "not-a-suite"]])
def test_usage_and_unknown_names_return_two(argv, tmp_path):
    write_registry(tmp_path, sample_data())
    assert invoke(argv, tmp_path, forbidden_run) == 2


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_omits_nested_suites_and_reports_the_skip(tmp_path, capsys):
    write_registry(tmp_path, sample_data())
    calls = []

    def run_one(root, run):
        calls.append((run.suite.name, run.python))
        return 0

    assert invoke(["--all"], tmp_path, run_one) == 0
    assert calls == [
        ("build", "3.13"),
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
    ]
    lines = capsys.readouterr().out.splitlines()
    skipped = [
        line
        for line in lines
        if "cc-guide" in line and not line.startswith("== ")
    ]
    assert len(skipped) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_named_nested_suite_runs(tmp_path):
    write_registry(tmp_path, sample_data())
    calls = []

    def run_one(root, run):
        calls.append(run.suite.name)
        return 0

    assert invoke(["cc-guide"], tmp_path, run_one) == 0
    assert calls == ["cc-guide"]


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_containment_uses_directory_components():
    data = sample_data()
    data["suite"].append(
        {"name": "brainstorming", "dir": "build.py", "with": ["pytest"]}
    )
    suites = rs.parse(data)
    by_name = {suite.name: suite for suite in suites}
    assert rs.container(by_name["cc-guide"], suites) == by_name["build"]
    assert rs.container(by_name["build"], suites) is None
    assert rs.container(by_name["brainstorming"], suites) is None


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_script_finds_its_registry_from_another_directory(tmp_path):
    assert rs.REPO.resolve() == ROOT.resolve()
    result = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--list", "brainstorming"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "skills/brainstorming/scripts" in result.stdout
    assert (
        "cd skills/brainstorming/scripts && uv run --python 3.13 "
        "--with pytest python -m pytest -q"
    ) in result.stdout


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_cwd_argv_environment_and_output(
    tmp_path, monkeypatch, capfd
):
    data = sample_data()
    populate_suites(tmp_path, data)
    run = rs.runs(rs.parse(data)[0])[0]
    binary_dir = tmp_path / "bin"
    binary_dir.mkdir()
    record = tmp_path / "subprocess.json"
    fake_uv = binary_dir / "uv"
    fake_uv.write_text(
        f"#!{sys.executable}\n"
        "import hashlib, json, os, sys\n"
        "from pathlib import Path\n"
        "environment = json.dumps(dict(os.environ), sort_keys=True).encode()\n"
        f"Path({str(record)!r}).write_text(json.dumps({{\n"
        "    'argv': sys.argv[1:],\n"
        "    'cwd': os.getcwd(),\n"
        "    'environment': hashlib.sha256(environment).hexdigest(),\n"
        "}))\n"
        "print('test_runtime_support.py', flush=True)\n",
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)
    monkeypatch.setenv(
        "PATH", str(binary_dir) + os.pathsep + os.environ.get("PATH", "")
    )
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    expected_environment = hashlib.sha256(
        json.dumps(dict(os.environ), sort_keys=True).encode()
    ).hexdigest()

    assert rs.run_subprocess(tmp_path, run) == 0
    observed = json.loads(record.read_text(encoding="utf-8"))
    assert observed["argv"] == list(run.argv[1:])
    assert Path(observed["cwd"]) == tmp_path / "build"
    assert observed["environment"] == expected_environment
    assert "test_runtime_support.py" in capfd.readouterr().out


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_is_a_failed_run(tmp_path, monkeypatch, capsys):
    data = sample_data()
    write_registry(tmp_path, data)
    populate_suites(tmp_path, data)
    monkeypatch.setenv("PATH", str(tmp_path / "missing"))
    assert invoke(["hooks", "build"], tmp_path) == 1
    output = capsys.readouterr()
    combined = output.out + output.err
    assert "hooks (3.13)" in combined
    assert "hooks (/usr/bin/python3)" in combined
    assert "build (3.13)" in combined


# spec: "- **coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize("filename", ["test_new.py", "new_test.py"])
@pytest.mark.parametrize("tracked", [False, True])
def test_uncovered_pytest_files_are_findings(
    filename, tracked, tmp_path, capsys
):
    git_repo(tmp_path)
    directory = tmp_path / "skills/write-with-asd-ste100/scripts"
    directory.mkdir(parents=True)
    path = directory / filename
    path.write_text("def test_new():\n    pass\n", encoding="utf-8")
    if tracked:
        git(tmp_path, "add", str(path.relative_to(tmp_path)))

    assert "skills/write-with-asd-ste100/scripts" in rs.pytest_dirs(tmp_path)
    findings = rs.check(tmp_path, sample_data())
    assert any(
        "skills/write-with-asd-ste100/scripts" in finding
        for finding in findings
    )
    assert invoke(["--check"], tmp_path, forbidden_run) == 1
    output = capsys.readouterr()
    assert "skills/write-with-asd-ste100/scripts" in output.out + output.err


# spec: "- **registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
@pytest.mark.parametrize("exists", [False, True])
def test_registered_directory_must_exist_and_hold_tests(
    exists, tmp_path
):
    git(tmp_path, "init", "--quiet")
    data = {
        "suite": [
            {
                "name": "brainstorming",
                "dir": "skills/brainstorming/scripts",
                "with": ["pytest"],
            }
        ]
    }
    write_registry(tmp_path, data)
    if exists:
        directory = tmp_path / "skills/brainstorming/scripts"
        directory.mkdir(parents=True)
        (directory / "cli.py").write_text("", encoding="utf-8")
    git(tmp_path, "add", ".")
    findings = rs.check(tmp_path, data)
    assert findings
    assert any(
        "skills/brainstorming/scripts" in finding for finding in findings
    )


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_ignored_pytest_directories_do_not_count(tmp_path):
    data = {"suite": [sample_data()["suite"][2]]}
    git_repo(tmp_path, data)
    (tmp_path / ".gitignore").write_text(
        ".claude/worktrees/\nbuild/.scratch/\n",
        encoding="utf-8",
    )
    for directory in [".claude/worktrees/hooks", "build/.scratch"]:
        path = tmp_path / directory
        path.mkdir(parents=True)
        (path / "test_new.py").write_text("", encoding="utf-8")

    directories = rs.pytest_dirs(tmp_path)
    assert ".claude/worktrees/hooks" not in directories
    assert "build/.scratch" not in directories
    assert rs.check(tmp_path, data) == []


# spec: "- **coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_descendants_are_covered_and_nonpytest_names_are_ignored(tmp_path):
    data = {"suite": [sample_data()["suite"][0]]}
    git_repo(tmp_path, data)
    nested = tmp_path / "build/cc_guide"
    nested.mkdir(parents=True)
    (nested / "new_test.py").write_text("", encoding="utf-8")
    outside = tmp_path / "skills/writing-plans/scripts"
    outside.mkdir(parents=True)
    for filename in ["tests.py", "test_new.txt", "test_new.py.bak"]:
        (outside / filename).write_text("", encoding="utf-8")

    assert "build/cc_guide" in rs.pytest_dirs(tmp_path)
    assert "skills/writing-plans/scripts" not in rs.pytest_dirs(tmp_path)
    assert rs.check(tmp_path, data) == []


# spec: "If git fails, `--check` fails."
# task: 3
def test_check_fails_when_git_cannot_start(tmp_path, monkeypatch):
    git_repo(tmp_path)
    monkeypatch.setenv("PATH", str(tmp_path / "missing"))
    assert invoke(["--check"], tmp_path, forbidden_run) == 1


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_success_output(tmp_path, capsys):
    git_repo(tmp_path)
    assert invoke(["--check"], tmp_path, forbidden_run) == 0
    output = capsys.readouterr()
    assert output.out == "suite registry ok\n"
    assert output.err == ""


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_prints_one_line_per_finding(tmp_path, capsys):
    data = git_repo(tmp_path)
    for name in ["writing-plans", "tune-hyperparameters"]:
        path = tmp_path / "skills" / name / "scripts"
        path.mkdir(parents=True)
        (path / "test_new.py").write_text("", encoding="utf-8")

    findings = rs.check(tmp_path, data)
    assert len(findings) == 2
    assert all("\n" not in finding for finding in findings)
    assert invoke(["--check"], tmp_path, forbidden_run) == 1
    output = capsys.readouterr()
    lines = [
        line for line in (output.out + output.err).splitlines() if line
    ]
    assert sorted(lines) == sorted(findings)


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_inventory_and_order():
    data = tomllib.loads(
        (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    )
    entries = data["suite"]
    names = [entry["name"] for entry in entries]
    assert names == sorted(names)
    assert len(names) == len(set(names))
    by_name = {entry["name"]: entry for entry in entries}

    for name, directory, deps, extras, pythons in INVENTORY:
        assert name in by_name
        entry = by_name[name]
        assert entry["dir"] == directory
        assert entry["with"] == deps
        assert entry.get("extras", []) == extras
        assert entry.get("pythons", ["3.13"]) == pythons

    assert not rs.validate(data)


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_describes_schema_sort_and_lint():
    text = (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    header = text.split("[[suite]]", 1)[0]
    comments = "\n".join(
        line.lstrip()[1:].strip()
        for line in header.splitlines()
        if line.lstrip().startswith("#")
    )
    for key in ["name", "dir", "with", "extras", "pythons", "notes"]:
        assert re.search(rf"\b{key}\b", comments)
    assert "sort" in comments.lower()
    assert "name" in comments.lower()
    assert "ninth" in comments.lower()
    assert "commit lint" in comments.lower()


# spec: "Examples: `build`'s missing `build/.scratch/` in a fresh clone or worktree; `bayesian-workflow`'s `CALIBRATION_SWEEP=1` sweep and its expected arviz warnings; `llm-wiki`'s `@needs_pilot` tests and `$LLM_WIKI_ROOT`; `brainstorming`'s node skip; `tune-hyperparameters`' \"`--with sklearn` fails\"; `track-model-experiments`' run time; the guard's 3.9 floor, its launchd-PATH skips and its Gate B probe for `hooks`."
# task: 5
def test_required_note_subjects_survive():
    data = tomllib.loads(
        (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    )
    notes = {
        entry["name"]: "\n".join(entry.get("notes", []))
        for entry in data["suite"]
    }
    required = {
        "build": ["build/.scratch/"],
        "bayesian-workflow": ["CALIBRATION_SWEEP=1", "arviz", "warn"],
        "llm-wiki": ["@needs_pilot", "LLM_WIKI_ROOT"],
        "brainstorming": ["node", "skip"],
        "tune-hyperparameters": ["--with sklearn", "fail"],
        "hooks": ["3.9", "launchd", "PATH", "Gate B"],
    }
    for name, fragments in required.items():
        for fragment in fragments:
            assert fragment.casefold() in notes[name].casefold()
    assert re.search(r"fresh clone|worktree", notes["build"], re.IGNORECASE)
    assert re.search(
        r"run ?time|\b\d+(?:\.\d+)?\s*(?:s\b|seconds?\b|minutes?\b|mins?\b)",
        notes["track-model-experiments"],
        re.IGNORECASE,
    )


# spec: "With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character."
# task: 5
def test_default_shell_forms_match_the_spec_baseline(capsys):
    lines = historical("CLAUDE.md").splitlines()
    old_commands = set()
    directories = set()
    for line in [*lines[65:125], lines[144]]:
        if not line.startswith("cd "):
            continue
        parts = line.split(" && ")
        assert parts[0].startswith("cd ")
        directories.add(parts[0][3:])
        for command in parts[1:]:
            assert command.startswith("uv run ")
            old_commands.add(f"{parts[0]} && {command}")

    assert len(directories) == 18
    assert invoke(
        ["--list", *(entry[0] for entry in INVENTORY)],
        ROOT,
        forbidden_run,
    ) == 0
    output = capsys.readouterr().out
    printed_commands = {
        line.strip()
        for line in output.splitlines()
        if line.strip().startswith("cd ")
    }
    assert printed_commands == old_commands


# spec: "- the real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_check_passes(capsys):
    data = tomllib.loads(
        (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    )
    assert rs.check(ROOT, data) == []
    assert invoke(["--check"], ROOT, forbidden_run) == 0
    output = capsys.readouterr()
    assert output.out == "suite registry ok\n"
    assert output.err == ""


# spec: "Until plan 52 adds the entry, the ninth lint refuses its new suite directory."
# task: 5
def test_plan_52_suite_is_registered_when_present():
    directory = "skills/write-with-asd-ste100/scripts"
    if (ROOT / directory).is_dir():
        data = tomllib.loads(
            (ROOT / "build/suites.toml").read_text(encoding="utf-8")
        )
        entries = [
            entry
            for entry in data["suite"]
            if entry["name"] == "write-with-asd-ste100"
        ]
        assert len(entries) == 1
        assert entries[0]["dir"] == directory
        assert "pytest" in entries[0]["with"]


# spec: "`build/run_commit_lints.sh` keeps its literal commands."
# task: 6
def test_existing_commit_lint_commands_are_preserved():
    previous = lint_lines(historical("build/run_commit_lints.sh"))
    current = lint_lines(
        (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    )
    assert current[:-1] == previous


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_suite_registry_is_the_ninth_lint():
    text = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    commands = lint_lines(text)
    assert len(commands) == 9
    assert commands[-1] == (
        "run suite_registry uv run --python 3.13 "
        "python build/run_suites.py --check"
    )
    header = []
    for line in text.splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            break
        header.append(line)
    assert "nine" in "\n".join(header).lower()


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_tests_include_the_new_check():
    tree = ast.parse(
        (ROOT / "build/test_commit_lints.py").read_text(encoding="utf-8")
    )
    value = assigned_value(tree, "CHECKS")
    strings = {
        node.value
        for node in ast.walk(value)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert "suite_registry" in strings
    assert any(
        isinstance(node, ast.FunctionDef)
        and node.name == "test_unregistered_suite_is_refused"
        for node in tree.body
    )


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_committing_an_unregistered_suite_fails_only_suite_registry(tmp_path):
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(clone)],
        env=clean_git_env(),
        text=True,
        capture_output=True,
        check=True,
    )
    directory = clone / "skills/acceptance-suite-registry/scripts"
    directory.mkdir(parents=True)
    (directory / "test_new.py").write_text(
        "def test_new():\n    pass\n", encoding="utf-8"
    )
    git(clone, "add", "skills/acceptance-suite-registry/scripts/test_new.py")

    commands = lint_lines(
        (clone / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    )
    failures = {}
    for command in commands:
        words = shlex.split(command)
        result = subprocess.run(
            words[2:],
            cwd=clone,
            env=clean_git_env(),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            failures[words[1]] = result.stdout + result.stderr
    assert set(failures) == {"suite_registry"}, failures

    hooks = clone / ".git/hooks"
    hook = hooks / "pre-commit"
    hook.write_text(
        "#!/bin/sh\nexec bash build/run_commit_lints.sh\n",
        encoding="utf-8",
    )
    hook.chmod(0o755)
    result = git(
        clone,
        "-c", f"core.hooksPath={hooks}",
        "-c", "commit.gpgsign=false",
        "-c", "user.name=pytest",
        "-c", "user.email=pytest@example.invalid",
        "commit", "-m", "Add an unregistered suite",
        check=False,
    )
    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert "suite_registry" in output
    assert "commit lints passed" not in output


# spec: "`build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_documentation_explains_the_registry_lint():
    text = (ROOT / "build/CLAUDE.md").read_text(encoding="utf-8")
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    normalized = re.sub(r"\s+", " ", text)
    protected = normalized.replace("suites.toml", "SUITES_TOML").replace(
        "run_suites.py", "RUN_SUITES_PY"
    )
    sentences = re.split(r"(?<=[.!?])\s+", protected)
    assert any(
        all(
            fragment in sentence
            for fragment in [
                "SUITES_TOML",
                "RUN_SUITES_PY",
                "--check",
                "commit lint",
            ]
        )
        for sentence in sentences
    )


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_intro_retains_the_execution_rules_on_one_line():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    candidates = [
        line for line in text.splitlines()
        if "test_build.py" in line
        and "build/suites.toml" in line
        and "build/run_suites.py" in line
    ]
    assert len(candidates) == 1
    intro = candidates[0]
    assert "uv" in intro
    assert "3.13" in intro
    assert "director" in intro.lower()
    assert re.search(r"collid|collision", intro, re.IGNORECASE)
    assert "note" in intro.lower()
    assert "before" in intro.lower()
    assert "There is no root test runner" not in text


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_commands_document_all_four_runner_modes():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    prefix = "uv run --python 3.13 python build/run_suites.py "
    expected = [
        prefix + "--list",
        prefix + "<name> [--extras] [-- <pytest args>]",
        prefix + "--all",
        prefix + "--check",
    ]
    positions = [lines.index(command) for command in expected]
    assert positions == list(range(positions[0], positions[0] + 4))
    assert lines[positions[0] - 1].lstrip().startswith("#")


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_has_no_literal_directory_suite_commands_and_is_under_limit():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    directories = {entry[1] for entry in INVENTORY}
    directories.add("skills/write-with-asd-ste100/scripts")

    for line in text.splitlines():
        if not line.lstrip().startswith("cd "):
            continue
        words = shlex.split(line.strip())
        if len(words) < 3 or words[1] not in directories:
            continue
        segments = line.strip().split(" && ")[1:]
        for segment in segments:
            argv = shlex.split(segment)
            if ["python", "-m", "pytest"] == argv[-4:-1] and argv[-1] == "-q":
                pytest.fail(f"Literal directory-suite command remains: {line}")


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_new_root_text_does_not_claim_suite_or_test_counts():
    old_lines = set(historical("CLAUDE.md").splitlines())
    current = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    added = "\n".join(
        line for line in current.splitlines() if line not in old_lines
    )
    numbers = (
        r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
        r"seventeen|eighteen|nineteen|twenty"
    )
    assert not re.search(
        rf"\b(?:{numbers})\s+(?:directory\s+)?(?:suites|tests)\b",
        added,
        re.IGNORECASE,
    )


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_non_suite_commands_remain_literal():
    old_lines = historical("CLAUDE.md").splitlines()
    current_lines = (ROOT / "CLAUDE.md").read_text(
        encoding="utf-8"
    ).splitlines()
    for index, line in enumerate(old_lines):
        if 65 <= index < 125 or index == 144:
            continue
        if re.match(r"^(?:uv run |cd |bash |python |node )", line):
            assert line in current_lines


# spec: "Line 133 is not touched (plan 53's Task 7 edits it)."
# task: 7
def test_original_line_133_is_retained():
    original = historical("CLAUDE.md").splitlines()[132]
    current = (ROOT / "CLAUDE.md").read_text(
        encoding="utf-8"
    ).splitlines()
    assert original in current


# spec: "The commit-lint comment names the suite-registry check and says \"nine\"."
# task: 7
def test_root_commit_lint_comment_names_the_ninth_check():
    lines = (ROOT / "CLAUDE.md").read_text(
        encoding="utf-8"
    ).splitlines()
    comments = "\n".join(
        line for line in lines if line.lstrip().startswith("#")
    )
    assert re.search(r"\bnine\b", comments, re.IGNORECASE)
    assert re.search(
        r"suite_registry|suite[- ]registry", comments, re.IGNORECASE
    )


# spec: "The comment names the suite `run_suites.py cc-guide` instead of \"its suite\"."
# task: 7
def test_cc_guide_comment_uses_the_required_suite_name():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "run_suites.py cc-guide" in text
    assert "run_suites.py cc_guide" not in text


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_uses_the_stamp():
    first_line = (ROOT / "CLAUDE.md").read_text(
        encoding="utf-8"
    ).splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .+ @\S+ -->", first_line)

    tree = ast.parse(
        (ROOT / "build/test_check_conformance.py").read_text(
            encoding="utf-8"
        )
    )
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    assertions = [
        node for node in ast.walk(function) if isinstance(node, ast.Assert)
    ]
    assertion_strings = [
        child.value
        for assertion in assertions
        for child in ast.walk(assertion)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    ]
    assert "@needs_pilot" not in assertion_strings
    assert any("cc-guide:" in value for value in assertion_strings)
    assert any("@" in value for value in assertion_strings)
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>the base facts that Tasks 5 and 7 check against, and a spec that names the suite `cc_guide`.</plan></flag>
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
Matches conformance.toml and manifest.toml.
Rejected: a Python list inside the runner (every suite change becomes a code edit), and one manifest per suite directory (`install.py` copies skill directories, so the manifests would ship with installed skills).
An `@`-imported document was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
**Design section 1** (the registry keys and the runner's behaviour) was approved as presented.
It is R1–R3 below.
**Design section 2** (the guard, the file edits, the tests and the couplings) was approved as presented.
It is R4–R7 below.
Every command, dependency and note survives; the only change is the form.
The deletion of lines 66–125 is bounded by two lines that no other plan edits: the `# Full build-directory tests` comment and the `cd hooks && …` command.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
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