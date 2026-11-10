<tests>
import argparse
import ast
import copy
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from build import run_suites as runner
from build import test_commit_lints as commit_lint_tests


DEFAULT_PYTHONS = ("3.13",)
INVENTORY = {
    "bayesian-workflow": (
        "skills/bayesian-workflow/scripts",
        ("pytest", "arviz", "arviz-stats", "numpy", "xarray"),
        ("matplotlib",),
        DEFAULT_PYTHONS,
    ),
    "brainstorming": (
        "skills/brainstorming/scripts", ("pytest",), (), DEFAULT_PYTHONS,
    ),
    "build": (
        "build",
        ("pytest", "numpy", "polars", "pyyaml"),
        (
            "arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots",
            "numpyro", "jax", "matplotlib",
        ),
        DEFAULT_PYTHONS,
    ),
    "cc-guide": ("build/cc_guide", ("pytest",), (), DEFAULT_PYTHONS),
    "classification-codes": (
        "skills/classification-codes/scripts",
        ("pytest", "polars"), (), DEFAULT_PYTHONS,
    ),
    "describe-critique-methodology": (
        "skills/describe-critique-methodology/scripts",
        ("pytest",), (), DEFAULT_PYTHONS,
    ),
    "design-architecture": (
        "skills/design-architecture/scripts", ("pytest",), (), DEFAULT_PYTHONS,
    ),
    "explore-data": (
        "skills/explore-data/scripts",
        ("pytest", "polars"), (), DEFAULT_PYTHONS,
    ),
    "geographic-codes": (
        "skills/geographic-codes/scripts",
        ("pytest", "polars", "fastexcel"), (), DEFAULT_PYTHONS,
    ),
    "hooks": ("hooks", ("pytest",), (), ("3.13", "/usr/bin/python3")),
    "llm-wiki": (
        "skills/llm-wiki/scripts", ("pytest",), (), DEFAULT_PYTHONS,
    ),
    "recommend-probabilistic-model": (
        "skills/recommend-probabilistic-model/scripts",
        ("pytest", "numpy", "polars"), (), DEFAULT_PYTHONS,
    ),
    "recommend-visualization": (
        "skills/recommend-visualization/scripts",
        ("pytest", "numpy", "polars"), (), DEFAULT_PYTHONS,
    ),
    "subagent-driven-development": (
        "skills/subagent-driven-development/scripts",
        ("pytest",), (), DEFAULT_PYTHONS,
    ),
    "systematic-debugging": (
        "skills/systematic-debugging", ("pytest",), (), DEFAULT_PYTHONS,
    ),
    "track-model-experiments": (
        "skills/track-model-experiments/scripts",
        ("pytest", "numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"),
        (),
        DEFAULT_PYTHONS,
    ),
    "tune-hyperparameters": (
        "skills/tune-hyperparameters/scripts",
        ("pytest", "numpy", "polars"),
        ("scikit-learn", "optuna"),
        DEFAULT_PYTHONS,
    ),
    "writing-plans": (
        "skills/writing-plans/scripts", ("pytest",), (), DEFAULT_PYTHONS,
    ),
}
PYTEST_ARGS = (
    "test_runtime_support.py", "-k", "declared_dependencies", "-s", "-rs",
)


def _row(name):
    directory, deps, extras, pythons = INVENTORY[name]
    row = {"name": name, "dir": directory, "with": list(deps)}
    if extras:
        row["extras"] = list(extras)
    if pythons != DEFAULT_PYTHONS:
        row["pythons"] = list(pythons)
    return row


def _fixture_data():
    data = {"suite": [_row(name) for name in ("build", "cc-guide", "hooks")]}
    data["suite"][0]["notes"] = ["build/.scratch/"]
    data["suite"][2]["notes"] = ["Gate B"]
    return data


def _write_registry(root, data):
    lines = [
        f"{key} = {json.dumps(value)}"
        for key, value in data.items()
        if key != "suite"
    ]
    for row in data["suite"]:
        lines.append("[[suite]]")
        lines.extend(
            f"{key} = {json.dumps(value)}"
            for key, value in row.items()
        )
        lines.append("")
    path = root / "build/suites.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _put(root, relative, content=""):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _git(root, *args):
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    return subprocess.run(
        ["git", "-C", str(root), *args],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )


def _unexpected_run(root, run):
    pytest.fail(f"Unexpected suite execution: {run.label}")


def _invoke(root, args, run_one=_unexpected_run):
    try:
        return runner.main(args, root=root, run_one=run_one)
    except SystemExit as exc:
        return int(exc.code or 0)


def _invalid_data():
    cases = []
    for key in ("name", "dir", "with"):
        data = {"suite": [_row("build")]}
        del data["suite"][0][key]
        cases.append(pytest.param(data, id=f"missing-{key}"))

    wrong_types = {
        "name": (1, ["build"]),
        "dir": (1, ["build"]),
        "with": ("pytest", ["pytest", 1]),
        "extras": ("matplotlib", [1]),
        "pythons": ("3.13", [3.13]),
        "notes": ("Gate B", [1]),
    }
    for key, values in wrong_types.items():
        for index, value in enumerate(values):
            data = {"suite": [_row("build")]}
            data["suite"][0][key] = value
            cases.append(
                pytest.param(data, id=f"wrong-type-{key}-{index}")
            )

    data = {"suite": [_row("build")]}
    data["suite"][0]["extrsa"] = ["matplotlib"]
    cases.append(pytest.param(data, id="unknown-suite-key"))

    data = {"suite": [_row("build")], "unexpected": "pytest"}
    cases.append(pytest.param(data, id="unknown-top-level-key"))

    for deps in ([], ["numpy"]):
        data = {"suite": [_row("build")]}
        data["suite"][0]["with"] = deps
        cases.append(
            pytest.param(data, id=f"without-pytest-{len(deps)}")
        )

    data = {"suite": [_row("build"), _row("hooks")]}
    data["suite"][1]["name"] = "build"
    cases.append(pytest.param(data, id="duplicate-name"))

    data = {"suite": [_row("build"), _row("hooks")]}
    data["suite"][1]["dir"] = "build"
    cases.append(pytest.param(data, id="duplicate-directory"))
    return cases


INVALID_DATA = _invalid_data()


def _expected_argv(name, python, extras=False, pytest_args=()):
    _, deps, extra_deps, _ = INVENTORY[name]
    dependencies = deps + (extra_deps if extras else ())
    dep_args = tuple(
        word for dependency in dependencies for word in ("--with", dependency)
    )
    return (
        "uv", "run", "--python", python,
        *dep_args, "python", "-m", "pytest", "-q", *pytest_args,
    )


def _real_data():
    return tomllib.loads(
        (runner.REPO / "build/suites.toml").read_text(encoding="utf-8")
    )


def _historical(path):
    return _git(runner.REPO, "show", f"456e3fb:{path}").stdout


def _lint_commands(text):
    commands = []
    for line in text.splitlines():
        if re.match(r"^\s*run\s+", line):
            words = shlex.split(line, comments=True)
            commands.append((words[1], words[2:]))
    return commands


def _import_roots(path):
    roots = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


@pytest.fixture
def registry_repo(tmp_path):
    _git(tmp_path, "init", "-q")
    data = _fixture_data()
    for row in data["suite"]:
        _put(tmp_path, f"{row['dir']}/test_new.py")
    _write_registry(tmp_path, data)
    return tmp_path, data


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_uses_only_stdlib():
    imports = _import_roots(Path(runner.__file__))
    assert imports <= sys.stdlib_module_names
    assert "tomllib" in imports


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 2
def test_repo_root_and_spec_constants():
    assert runner.REPO.resolve() == Path(runner.__file__).resolve().parent.parent
    assert runner.REGISTRY == "build/suites.toml"
    assert runner.DEFAULT_PYTHONS == ("3.13",)
    assert set(runner.TEST_FILE_PATTERNS) == {"test_*.py", "*_test.py"}


# spec: "Invoked as `uv run --python 3.13 python build/run_suites.py …` from any directory."
# task: 4
def test_script_lists_from_an_unrelated_working_directory(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(Path(runner.__file__).resolve()),
            "--list",
            "brainstorming",
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "brainstorming" in result.stdout
    assert "skills/brainstorming/scripts" in result.stdout
    assert (
        "cd skills/brainstorming/scripts && "
        "uv run --python 3.13 --with pytest python -m pytest -q"
    ) in result.stdout


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
@pytest.mark.parametrize("data", INVALID_DATA)
def test_validator_rejects_every_specified_failure(data):
    findings = runner.validate(copy.deepcopy(data))
    assert isinstance(findings, list)
    assert findings
    assert all(isinstance(finding, str) and finding for finding in findings)


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
@pytest.mark.parametrize("data", INVALID_DATA)
@pytest.mark.parametrize("args", [("--list",), ("build",), ("--all",)])
def test_invalid_registry_blocks_every_execution_mode(tmp_path, data, args):
    _write_registry(tmp_path, data)
    assert _invoke(tmp_path, list(args)) == 2


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 4
@pytest.mark.parametrize("data", INVALID_DATA)
def test_check_reports_validation_failures(registry_repo, data, capsys):
    root, _ = registry_repo
    _write_registry(root, data)
    findings = runner.check(root, data)
    assert findings
    assert all("\n" not in finding for finding in findings)
    assert _invoke(root, ["--check"]) == 1
    captured = capsys.readouterr()
    lines = (captured.out + captured.err).splitlines()
    assert sorted(line for line in lines if line.strip()) == sorted(findings)


# spec: "| `pythons` | list of strings | no | The interpreters, one run each, in order. Default `['3.13']`. |"
# task: 2
def test_parsing_applies_defaults_and_preserves_explicit_order():
    data = {"suite": [_row("brainstorming"), _row("hooks")]}
    assert runner.validate(data) == []
    ordinary, hooks = runner.parse(data)
    assert ordinary.name == "brainstorming"
    assert ordinary.dir == "skills/brainstorming/scripts"
    assert ordinary.deps == ("pytest",)
    assert ordinary.extras == ()
    assert ordinary.pythons == ("3.13",)
    assert ordinary.notes == ()
    assert hooks.pythons == ("3.13", "/usr/bin/python3")


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
@pytest.mark.parametrize("name", list(INVENTORY))
def test_default_commands_follow_the_inventory(name):
    suite = runner.parse({"suite": [_row(name)]})[0]
    actual = runner.runs(suite)
    expected_pythons = INVENTORY[name][3]
    assert [run.python for run in actual] == list(expected_pythons)
    for run, python in zip(actual, expected_pythons):
        expected = _expected_argv(name, python)
        assert run.suite == suite
        assert run.argv == expected
        assert run.label == f"{name} ({python})"
        assert run.shell() == f"cd {suite.dir} && {' '.join(expected)}"


# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
@pytest.mark.parametrize(
    "name", ["bayesian-workflow", "build", "tune-hyperparameters", "hooks"]
)
def test_extras_are_opt_in_and_follow_default_dependencies(name):
    suite = runner.parse({"suite": [_row(name)]})[0]
    for extras in (False, True):
        actual = runner.runs(suite, extras=extras)
        for run in actual:
            assert run.argv == _expected_argv(name, run.python, extras=extras)


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_cli_forwards_pytest_arguments_to_every_run(registry_repo):
    root, _ = registry_repo
    seen = []

    def record(root_arg, run):
        seen.append((root_arg, run))
        return 0

    args = ["hooks", "build", "--extras", "--", *PYTEST_ARGS]
    assert _invoke(root, args, record) == 0
    assert len(seen) == 3
    for root_arg, run in seen:
        assert root_arg == root
        assert run.argv == _expected_argv(
            run.suite.name, run.python, extras=True, pytest_args=PYTEST_ARGS
        )


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_argument_parser_preserves_the_separator_tail():
    options, tail = runner.parse_args(
        ["--list", "build", "--extras", "--", *PYTEST_ARGS]
    )
    assert isinstance(options, argparse.Namespace)
    assert tail == PYTEST_ARGS


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_metacharacters_and_multiword_arguments():
    suite = runner.parse({"suite": [_row("build")]})[0]
    pytest_args = ("-k", "declared_dependencies or test_real_skill")
    run = runner.runs(
        suite, extras=True, pytest_args=pytest_args
    )[0]
    lexer = shlex.shlex(run.shell(), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    assert list(lexer) == ["cd", suite.dir, "&&", *run.argv]
    assert "arviz>=1.0" in run.argv


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
@pytest.mark.parametrize("selected", [None, ["hooks", "build"]])
@pytest.mark.parametrize("extras", [False, True])
def test_list_shows_requested_suites_and_exact_effective_commands(
    registry_repo, capsys, selected, extras
):
    root, data = registry_repo
    args = ["--list", *(selected or [])]
    if extras:
        args.append("--extras")
    args.extend(["--", *PYTEST_ARGS])
    assert _invoke(root, args) == 0
    output = capsys.readouterr().out
    suites = runner.parse(data)
    by_name = {suite.name: suite for suite in suites}
    wanted = selected or [suite.name for suite in suites]
    positions = []

    for name in wanted:
        suite = by_name[name]
        positions.append(output.index(name))
        assert suite.dir in output
        for run in runner.runs(
            suite, extras=extras, pytest_args=PYTEST_ARGS
        ):
            assert run.shell() in output
        for extra in suite.extras:
            assert extra in output
        for note in suite.notes:
            assert note in output

    assert positions == sorted(positions)
    for name in set(by_name) - set(wanted):
        assert name not in output


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_order_and_interpreter_order(registry_repo):
    root, _ = registry_repo
    seen = []

    def record(root_arg, run):
        seen.append((run.suite.name, run.python))
        return 0

    assert _invoke(root, ["hooks", "cc-guide", "build"], record) == 0
    assert seen == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("cc-guide", "3.13"),
        ("build", "3.13"),
    ]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_are_visible_before_execution(
    registry_repo, capsys
):
    root, data = registry_repo
    hooks = next(
        suite for suite in runner.parse(data) if suite.name == "hooks"
    )
    before_runs = []

    def record(root_arg, run):
        before_runs.append(capsys.readouterr().out)
        return 0

    assert runner.execute(
        root, [hooks], False, (), record
    ) == 0
    assert len(before_runs) == 2
    first, second = before_runs
    header = "== hooks (3.13)"
    assert header in first
    for note in hooks.notes:
        assert first.index(header) < first.index(note)
        assert note not in second
    assert "== hooks (/usr/bin/python3)" in second


# spec: "A failed run does not stop the next one."
# task: 4
@pytest.mark.parametrize(
    "statuses",
    [(0, 0, 0), (5, 0, 0), (0, 1, 0), (0, 0, 5), (5, 1, 0)],
)
def test_failures_do_not_stop_runs_and_summary_names_failed_runs(
    registry_repo, capsys, statuses
):
    root, _ = registry_repo
    seen = []

    def record(root_arg, run):
        seen.append(run.label)
        return statuses[len(seen) - 1]

    result = _invoke(root, ["hooks", "build"], record)
    expected_labels = [
        "hooks (3.13)", "hooks (/usr/bin/python3)", "build (3.13)"
    ]
    assert seen == expected_labels
    assert result == (1 if any(statuses) else 0)

    captured = capsys.readouterr()
    lines = [
        line for line in (captured.out + captured.err).splitlines()
        if line.strip()
    ]
    last = lines[-1]
    if any(statuses):
        for label, status in zip(expected_labels, statuses):
            if status:
                assert label in last
            else:
                assert label not in last
    else:
        assert "passed" in last.lower()


# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize(
    "args",
    [
        ["--not-a-runner-option"],
        ["unknown-suite"],
        ["--list", "unknown-suite"],
    ],
)
def test_usage_errors_and_unknown_names_exit_two(registry_repo, args):
    root, _ = registry_repo
    assert _invoke(root, args) == 2


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_uses_directory_ancestry_and_excludes_self():
    suites = runner.parse(_fixture_data())
    by_name = {suite.name: suite for suite in suites}
    assert runner.container(by_name["cc-guide"], suites) == by_name["build"]
    assert runner.container(by_name["build"], suites) is None
    assert runner.container(by_name["hooks"], suites) is None

    partial_prefix = runner.Suite(
        name="build", dir="build/cc", deps=("pytest",)
    )
    assert runner.container(
        by_name["cc-guide"], [partial_prefix, by_name["cc-guide"]]
    ) is None


# spec: "`--all` prints one line for each suite that it skips."
# task: 4
def test_all_skips_nested_suite_and_reports_it_once(registry_repo, capsys):
    root, _ = registry_repo
    seen = []

    def record(root_arg, run):
        seen.append((run.suite.name, run.python))
        return 0

    assert _invoke(root, ["--all"], record) == 0
    assert sorted(seen) == sorted([
        ("build", "3.13"),
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
    ])
    captured = capsys.readouterr()
    skipped_lines = [
        line
        for line in (captured.out + captured.err).splitlines()
        if "cc-guide" in line
    ]
    assert len(skipped_lines) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_explicitly_named_nested_suite_runs(registry_repo):
    root, _ = registry_repo
    seen = []

    def record(root_arg, run):
        seen.append(run.suite.name)
        return 0

    assert _invoke(root, ["cc-guide"], record) == 0
    assert seen == ["cc-guide"]


# spec: "The runner passes its environment to every run unchanged."
# task: 4
@pytest.mark.parametrize("child_status", [0, 5])
def test_subprocess_gets_exact_environment_cwd_and_argv(
    tmp_path, monkeypatch, capfd, child_status
):
    data = {"suite": [_row("bayesian-workflow")]}
    _write_registry(tmp_path, data)
    (tmp_path / "skills/bayesian-workflow/scripts").mkdir(parents=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    payload_path = tmp_path / "payload.json"
    fake_uv = bin_dir / "uv"
    fake_uv.write_text(
        f"""#!{sys.executable}
import hashlib
import json
import os
import sys
from pathlib import Path
payload = {{
    "argv": sys.argv[1:],
    "cwd": os.getcwd(),
    "environment": hashlib.sha256(
        json.dumps(dict(os.environ), sort_keys=True).encode()
    ).hexdigest(),
}}
Path({str(payload_path)!r}).write_text(json.dumps(payload))
print("pytest stdout", flush=True)
print("pytest stderr", file=sys.stderr, flush=True)
raise SystemExit({child_status})
""",
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)
    monkeypatch.setenv(
        "PATH", str(bin_dir) + os.pathsep + os.environ.get("PATH", "")
    )
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    expected_environment = hashlib.sha256(
        json.dumps(dict(os.environ), sort_keys=True).encode()
    ).hexdigest()

    result = _invoke(
        tmp_path,
        ["bayesian-workflow", "--", "-s"],
        runner.run_subprocess,
    )

    assert result == (0 if child_status == 0 else 1)
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    assert payload["environment"] == expected_environment
    assert payload["cwd"] == str(
        tmp_path / "skills/bayesian-workflow/scripts"
    )
    assert payload["argv"] == list(
        _expected_argv("bayesian-workflow", "3.13", pytest_args=("-s",))[1:]
    )
    captured = capfd.readouterr()
    assert "pytest stdout" in captured.out
    assert "pytest stderr" in captured.err


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_unstartable_uv_is_a_failed_run(registry_repo, monkeypatch, capsys):
    root, _ = registry_repo
    empty_path = root / "empty-path"
    empty_path.mkdir()
    monkeypatch.setenv("PATH", str(empty_path))
    assert _invoke(root, ["hooks"], runner.run_subprocess) == 1
    captured = capsys.readouterr()
    last = (captured.out + captured.err).strip().splitlines()[-1]
    assert "hooks (3.13)" in last
    assert "hooks (/usr/bin/python3)" in last


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize(
    "relative",
    [
        "skills/brainstorming/scripts/test_new.py",
        "skills/brainstorming/scripts/new_test.py",
        "test_new.py",
        "skills/write-with-asd-ste100/scripts/test_new.py",
    ],
)
@pytest.mark.parametrize("tracked", [False, True])
def test_uncovered_pytest_directories_are_findings(
    registry_repo, relative, tracked
):
    root, data = registry_repo
    _put(root, relative)
    if tracked:
        _git(root, "add", "--", relative)
    directory = Path(relative).parent.as_posix()
    assert directory in runner.pytest_dirs(root)
    findings = runner.check(root, data)
    assert len(findings) == 1
    assert directory in findings[0]
    assert "\n" not in findings[0]


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize(
    "filename", ["test.py", "new.py", "test_new.txt", "test_new.pyc"]
)
def test_non_pytest_filenames_do_not_create_coverage_findings(
    registry_repo, filename
):
    root, data = registry_repo
    _put(root, f"skills/brainstorming/scripts/{filename}")
    assert runner.check(root, data) == []


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
@pytest.mark.parametrize("directory_exists", [False, True])
def test_missing_or_testless_registered_directory_is_a_finding(
    registry_repo, directory_exists
):
    root, data = registry_repo
    row = _row("brainstorming")
    data["suite"].append(row)
    if directory_exists:
        (root / row["dir"]).mkdir(parents=True)
    findings = runner.check(root, data)
    assert len(findings) == 1
    assert row["dir"] in findings[0]


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_registered_parent_covers_nested_tests(registry_repo):
    root, data = registry_repo
    data["suite"] = [
        row for row in data["suite"] if row["name"] != "cc-guide"
    ]
    (root / "build/test_new.py").unlink()
    assert "build/cc_guide" in runner.pytest_dirs(root)
    assert runner.check(root, data) == []


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_git_ignored_trees_are_excluded(registry_repo):
    root, data = registry_repo
    _put(root, ".gitignore", ".claude/worktrees/\nbuild/.scratch/\n")
    ignored = [
        ".claude/worktrees/skills/brainstorming/scripts/test_new.py",
        "build/.scratch/test_new.py",
    ]
    for relative in ignored:
        _put(root, relative)
    directories = runner.pytest_dirs(root)
    assert directories is not None
    for relative in ignored:
        assert Path(relative).parent.as_posix() not in directories
    assert runner.check(root, data) == []


# spec: "If git fails, `--check` fails."
# task: 4
def test_git_failure_cannot_be_reported_as_success(
    registry_repo, monkeypatch, capsys
):
    root, data = registry_repo
    bin_dir = root / "bin"
    bin_dir.mkdir()
    fake_git = bin_dir / "git"
    fake_git.write_text(
        f"#!{sys.executable}\nraise SystemExit(1)\n", encoding="utf-8"
    )
    fake_git.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir))
    assert runner.pytest_dirs(root) is None
    assert runner.check(root, data)
    assert _invoke(root, ["--check"]) == 1
    captured = capsys.readouterr()
    assert "suite registry ok" not in captured.out + captured.err


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_success_and_coverage_failure_output(registry_repo, capsys):
    root, _ = registry_repo
    assert _invoke(root, ["--check"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "suite registry ok"
    assert captured.err == ""

    _put(root, "skills/brainstorming/scripts/test_new.py")
    assert _invoke(root, ["--check"]) == 1
    captured = capsys.readouterr()
    lines = [
        line for line in (captured.out + captured.err).splitlines()
        if line.strip()
    ]
    assert len(lines) == 1
    assert "skills/brainstorming/scripts" in lines[0]


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_is_sorted_and_contains_the_required_inventory():
    data = _real_data()
    rows = data["suite"]
    names = [row["name"] for row in rows]
    assert names == sorted(names)
    assert len(names) == len(set(names))
    assert len({row["dir"] for row in rows}) == len(rows)
    assert set(INVENTORY) <= set(names)

    by_name = {row["name"]: row for row in rows}
    for name, (directory, deps, extras, pythons) in INVENTORY.items():
        row = by_name[name]
        assert row["dir"] == directory
        assert row["with"] == list(deps)
        assert row.get("extras", []) == list(extras)
        assert row.get("pythons", ["3.13"]) == list(pythons)

    if "write-with-asd-ste100" in by_name:
        assert by_name["write-with-asd-ste100"]["dir"] == (
            "skills/write-with-asd-ste100/scripts"
        )


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_documents_schema_order_and_guard():
    text = (runner.REPO / "build/suites.toml").read_text(encoding="utf-8")
    header = text.split("[[suite]]", 1)[0]
    comments = "\n".join(
        line for line in header.splitlines()
        if line.lstrip().startswith("#")
    ).lower()
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert re.search(rf"\b{key}\b", comments)
    assert "sort" in comments
    assert re.search(r"\b(?:ninth|9th)\b", comments)
    assert "commit" in comments
    assert "lint" in comments
    assert "check" in comments


# spec: "The notes carry the rest of each comment."
# task: 5
@pytest.mark.parametrize(
    "name,tokens",
    [
        ("build", ("build/.scratch/",)),
        ("bayesian-workflow", ("CALIBRATION_SWEEP=1", "arviz", "warn")),
        ("llm-wiki", ("@needs_pilot", "$LLM_WIKI_ROOT")),
        ("brainstorming", ("node", "skip")),
        ("tune-hyperparameters", ("--with sklearn", "fail")),
        ("hooks", ("3.9", "launchd", "PATH", "Gate B")),
    ],
)
def test_registry_retains_explicitly_named_note_details(name, tokens):
    by_name = {row["name"]: row for row in _real_data()["suite"]}
    notes = "\n".join(by_name[name].get("notes", [])).casefold()
    for token in tokens:
        assert token.casefold() in notes


# spec: "With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character."
# task: 5
def test_default_shell_forms_match_the_spec_baseline_commands():
    lines = _historical("CLAUDE.md").splitlines()
    original_forms = set()
    for line in [*lines[65:125], lines[144]]:
        if not line.lstrip().startswith("cd "):
            continue
        pieces = line.strip().split(" && ")
        assert pieces[0].startswith("cd ")
        for command in pieces[1:]:
            assert command.startswith("uv run ")
            original_forms.add(f"{pieces[0]} && {command}")

    suites = runner.parse(_real_data())
    actual_forms = {
        run.shell()
        for suite in suites
        if suite.name in INVENTORY
        for run in runner.runs(suite)
    }
    assert original_forms
    assert actual_forms == original_forms


# spec: "the real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_check_passes(capsys):
    assert runner.check(runner.REPO, _real_data()) == []
    assert _invoke(runner.REPO, ["--check"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "suite registry ok"
    assert captured.err == ""


# spec: "`build/test_run_suites.py`, stdlib and pytest only, which the build suite collects."
# task: 2
def test_runner_test_module_exists_and_has_no_external_test_dependencies():
    path = runner.REPO / "build/test_run_suites.py"
    assert path.is_file()
    allowed = sys.stdlib_module_names | {"pytest", "run_suites", "build"}
    assert _import_roots(path) <= allowed


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_guard_is_the_ninth_literal_commit_lint():
    text = (runner.REPO / "build/run_commit_lints.sh").read_text(
        encoding="utf-8"
    )
    commands = _lint_commands(text)
    assert len(commands) == 9
    assert commands[-1] == (
        "suite_registry",
        [
            "uv", "run", "--python", "3.13",
            "python", "build/run_suites.py", "--check",
        ],
    )
    assert commands[:-1] == _lint_commands(
        _historical("build/run_commit_lints.sh")
    )
    assert re.search(r"(?m)^\s*#[^\n]*\bnine\b", text, re.IGNORECASE)


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_check_inventory_includes_registry():
    assert "suite_registry" in commit_lint_tests.CHECKS
    assert len(commit_lint_tests.CHECKS) == 9


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_committed_new_suite_fails_only_the_registry_lint(tmp_path):
    clone = tmp_path / "clone"
    _git(
        tmp_path,
        "clone", "--quiet", "--no-hardlinks", str(runner.REPO), str(clone),
    )
    relative = "skills/acceptance-new-suite/scripts/test_new.py"
    _put(clone, relative, "def test_new():\n    assert True\n")
    _git(clone, "add", "--", relative)
    _git(
        clone,
        "-c", "user.name=pytest",
        "-c", "user.email=pytest@example.invalid",
        "-c", "core.hooksPath=/dev/null",
        "commit", "--quiet", "-m", "Add an unregistered suite",
    )

    commands = _lint_commands(
        (clone / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    )
    assert len(commands) == 9
    failed = []
    diagnostics = {}
    for name, argv in commands:
        result = subprocess.run(
            argv, cwd=clone, text=True, capture_output=True, check=False
        )
        if result.returncode:
            failed.append(name)
            diagnostics[name] = result.stdout + result.stderr
    assert failed == ["suite_registry"], diagnostics


# spec: "`build/CLAUDE.md`: "the eight commit lints" becomes "the nine commit lints", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_documentation_describes_the_ninth_lint():
    text = (runner.REPO / "build/CLAUDE.md").read_text(encoding="utf-8")
    assert "the eight commit lints" not in text
    assert "the nine commit lints" in text
    sentences = re.split(r"(?<=[.!?])\s+", text)
    assert any(
        all(
            token in sentence
            for token in ("suites.toml", "run_suites.py", "--check")
        )
        and "commit" in sentence.lower()
        and "lint" in sentence.lower()
        for sentence in sentences
    )


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_documentation_contains_the_four_runner_commands():
    text = (runner.REPO / "CLAUDE.md").read_text(encoding="utf-8")
    prefix = "uv run --python 3.13 python build/run_suites.py "
    for suffix in (
        "--list",
        "<name> [--extras] [-- <pytest args>]",
        "--all",
        "--check",
    ):
        assert prefix + suffix in text


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_intro_retains_required_rules_and_explains_notes():
    text = (runner.REPO / "CLAUDE.md").read_text(encoding="utf-8")
    intro_lines = [
        line for line in text.splitlines()
        if "build/suites.toml" in line and "build/run_suites.py" in line
    ]
    assert len(intro_lines) == 1
    intro = intro_lines[0]
    for token in ("uv", "3.13", "test_build.py", "notes"):
        assert token in intro
    assert "director" in intro.lower()
    assert "collision" in intro.lower()
    assert "before" in intro.lower()
    assert "There is no root test runner" not in text


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_file_is_under_limit_and_has_no_directory_suite_commands():
    text = (runner.REPO / "CLAUDE.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    directories = {row["dir"] for row in _real_data()["suite"]}

    for line in text.splitlines():
        if not line.lstrip().startswith("cd "):
            continue
        words = shlex.split(line, comments=True)
        if len(words) < 3 or words[1] not in directories or words[2] != "&&":
            continue
        commands = []
        command = []
        for word in words[3:]:
            if word == "&&":
                commands.append(command)
                command = []
            else:
                command.append(word)
        commands.append(command)
        for command in commands:
            for index in range(len(command) - 2):
                if command[index:index + 3] == ["python", "-m", "pytest"]:
                    assert command[index + 3:] != ["-q"], line


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_root_documentation_has_no_numeric_suite_or_test_count_claims():
    text = (runner.REPO / "CLAUDE.md").read_text(encoding="utf-8")
    count = (
        r"(?:\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen)"
    )
    assert not re.search(
        rf"\b{count}\s+(?:suites|tests)\b", text, re.IGNORECASE
    )


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_original_commands_outside_the_removed_suite_block_stay_literal():
    original = _historical("CLAUDE.md").splitlines()
    current_lines = {
        line.strip()
        for line in (runner.REPO / "CLAUDE.md").read_text(
            encoding="utf-8"
        ).splitlines()
    }
    in_fence = False
    for number, line in enumerate(original, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence or not stripped or stripped.startswith("#"):
            continue
        if 66 <= number <= 125 or number in (133, 145):
            continue
        assert stripped in current_lines


# spec: "The comment names the suite `run_suites.py cc-guide` instead of "its suite"."
# task: 7
def test_cc_guide_comment_uses_the_specified_suite_name():
    text = (runner.REPO / "CLAUDE.md").read_text(encoding="utf-8")
    assert "run_suites.py cc-guide" in text


# spec: "`bash build/run_commit_lints.sh` prints `commit lints passed`."
# task: 6
def test_complete_commit_lint_gate():
    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=runner.REPO,
        text=True,
        capture_output=True,
        check=False,
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
Every command, dependency and note survives; the only change is the form.
Examples: `build`'s missing `build/.scratch/` in a fresh clone or worktree; `bayesian-workflow`'s `CALIBRATION_SWEEP=1` sweep and its expected arviz warnings; `llm-wiki`'s `@needs_pilot` tests and `$LLM_WIKI_ROOT`; `brainstorming`'s node skip; `tune-hyperparameters`' "`--with sklearn` fails"; `track-model-experiments`' run time; the guard's 3.9 floor, its launchd-PATH skips and its Gate B probe for `hooks`.
Then pytest's output streams.
A misspelled key can therefore never run a suite without its deps.
The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root.
Same number of lines.
Line 133 is not touched (plan 53's Task 7 edits it).
The file ends at about 145 lines.
The deletion of lines 66–125 is bounded by two lines that no other plan edits: the `# Full build-directory tests` comment and the `cd hooks && …` command.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
`build/test_check_conformance.py`: `test_claude_md_import_resolves_passes_on_the_repo` asserts `'@needs_pilot' in text` as its positive control, and that note moves to the registry.
The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp.
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