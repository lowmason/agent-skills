<tests>
import ast
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
from copy import deepcopy
from pathlib import Path

import pytest

from build import run_suites as runner


REPO = Path(runner.__file__).resolve().parent.parent
REGISTRY = "build/suites.toml"
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
    "cc-guide": (
        "build/cc_guide", (), (), ("3.13",),
    ),
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
        "skills/geographic-codes/scripts", ("polars", "fastexcel"), (), ("3.13",),
    ),
    "hooks": (
        "hooks", (), (), ("3.13", "/usr/bin/python3"),
    ),
    "llm-wiki": (
        "skills/llm-wiki/scripts", (), (), ("3.13",),
    ),
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
        ("numpy", "polars"),
        ("scikit-learn", "optuna"),
        ("3.13",),
    ),
    "writing-plans": (
        "skills/writing-plans/scripts", (), (), ("3.13",),
    ),
}
NOTES = {
    "bayesian-workflow": [
        "CALIBRATION_SWEEP=1",
        "expected arviz warnings",
    ],
    "build": [
        "missing build/.scratch/ in a fresh clone or worktree",
    ],
    "hooks": [
        "3.9",
        "launchd-PATH",
        "Gate B",
    ],
}


def _entry(name):
    directory, deps, extras, pythons = INVENTORY[name]
    return {
        "name": name,
        "dir": directory,
        "with": ["pytest", *deps],
        "extras": list(extras),
        "pythons": list(pythons),
        "notes": list(NOTES.get(name, ())),
    }


def _data(*names):
    return {"suite": [_entry(name) for name in names]}


def _write_registry(root, data):
    path = root / REGISTRY
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"{key} = {json.dumps(value)}"
        for key, value in data.items()
        if key != "suite"
    ]
    tables = data.get("suite", [])
    if isinstance(tables, list):
        for table in tables:
            lines.append("[[suite]]")
            lines.extend(
                f"{key} = {json.dumps(value)}"
                for key, value in table.items()
            )
    else:
        lines.append(f"suite = {json.dumps(tables)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write(root, relative, text=""):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _git(root, *args, check=True):
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
        check=check,
    )


def _forbid_run(root, run):
    pytest.fail(f"unexpected run: {run.label}")


def _main(args, root, run_one=_forbid_run):
    try:
        return runner.main(args, root=root, run_one=run_one)
    except SystemExit as exc:
        return exc.code


def _expected_argv(name, python, extras=False, pytest_args=()):
    _, deps, extra_deps, _ = INVENTORY[name]
    dependencies = ("pytest", *deps, *(extra_deps if extras else ()))
    argv = ["uv", "run", "--python", python]
    for dependency in dependencies:
        argv.extend(("--with", dependency))
    return (*argv, "python", "-m", "pytest", "-q", *pytest_args)


def _shell_tokens(shell):
    lexer = shlex.shlex(shell, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer)


def _invalid_cases():
    cases = []

    for key in ("name", "dir", "with"):
        data = _data("build")
        del data["suite"][0][key]
        cases.append((f"missing-{key}", data))

    wrong_values = (
        ("name", 3.13),
        ("dir", ["build"]),
        ("with", "pytest"),
        ("with", ["pytest", 3.13]),
        ("extras", "matplotlib"),
        ("extras", [3.13]),
        ("pythons", "3.13"),
        ("pythons", [3.13]),
        ("notes", "CALIBRATION_SWEEP=1"),
        ("notes", [3.13]),
    )
    for index, (key, value) in enumerate(wrong_values):
        data = _data("build")
        data["suite"][0][key] = value
        cases.append((f"wrong-type-{key}-{index}", data))

    data = _data("build")
    data["suite"][0]["python"] = "3.13"
    cases.append(("unknown-suite-key", data))

    data = _data("build")
    data["suites"] = []
    cases.append(("unknown-top-level-key", data))

    cases.append(("wrong-suite-container-type", {"suite": "build"}))

    data = _data("build", "hooks")
    data["suite"][1]["name"] = "build"
    cases.append(("duplicate-name", data))

    data = _data("build", "hooks")
    data["suite"][1]["dir"] = "build"
    cases.append(("duplicate-directory", data))

    for dependencies in ([], ["numpy", "polars", "pyyaml"]):
        data = _data("build")
        data["suite"][0]["with"] = dependencies
        cases.append((f"without-pytest-{len(dependencies)}", data))

    return cases


INVALID_CASES = _invalid_cases()


def _lint_commands(text):
    logical_text = text.replace("\\\n", " ")
    return [
        (match.group(1), match.group(2))
        for match in re.finditer(
            r"^\s*run\s+([A-Za-z0-9_-]+)\s+(.+)$",
            logical_text,
            re.MULTILINE,
        )
    ]


@pytest.fixture
def registry_root(tmp_path):
    data = _data("bayesian-workflow", "build", "cc-guide", "hooks")
    _write_registry(tmp_path, data)
    for table in data["suite"]:
        _write(tmp_path, f"{table['dir']}/test_new.py", "def test_new(): pass\n")
    return tmp_path


@pytest.fixture
def git_root(tmp_path):
    _git(tmp_path, "init", "--quiet")
    _write_registry(tmp_path, _data("hooks"))
    _write(tmp_path, "hooks/test_new.py", "def test_new(): pass\n")
    _git(tmp_path, "add", ".")
    return tmp_path


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 2
def test_repo_and_registry_constants():
    assert runner.REPO == REPO
    assert runner.REGISTRY == REGISTRY


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_imports_only_the_standard_library():
    tree = ast.parse(Path(runner.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            names = [(node.module or "").split(".")[0]]
        else:
            continue
        assert set(names) <= sys.stdlib_module_names


# spec: "Default `['3.13']`."
# task: 2
def test_optional_fields_default_without_adding_extras():
    data = {
        "suite": [{
            "name": "bayesian-workflow",
            "dir": "skills/bayesian-workflow/scripts",
            "with": ["pytest", "arviz", "arviz-stats", "numpy", "xarray"],
        }]
    }
    assert runner.validate(data) == []
    suite, = runner.parse(data)
    assert suite.pythons == ("3.13",)
    assert suite.extras == ()
    assert suite.notes == ()
    assert runner.DEFAULT_PYTHONS == ("3.13",)


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
@pytest.mark.parametrize(
    "case,data", INVALID_CASES, ids=[case for case, _ in INVALID_CASES]
)
def test_validation_rejects_each_invalid_registry(case, data):
    findings = runner.validate(deepcopy(data))
    assert isinstance(findings, list)
    assert findings
    assert all(isinstance(finding, str) for finding in findings)


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
@pytest.mark.parametrize(
    "case,data", INVALID_CASES, ids=[case for case, _ in INVALID_CASES]
)
@pytest.mark.parametrize("args", [("--list",), ("build",), ("--all",)])
def test_invalid_registry_stops_every_normal_mode(tmp_path, case, data, args):
    _write_registry(tmp_path, deepcopy(data))
    assert _main(list(args), tmp_path) == 2


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 4
@pytest.mark.parametrize(
    "case,data", INVALID_CASES, ids=[case for case, _ in INVALID_CASES]
)
def test_check_reports_validation_failures(tmp_path, capsys, case, data):
    _git(tmp_path, "init", "--quiet")
    _write_registry(tmp_path, deepcopy(data))
    assert _main(["--check"], tmp_path) == 1
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert output.strip()
    assert "suite registry ok" not in output


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_build_command():
    suite, = runner.parse(_data("build"))
    run, = runner.runs(suite)
    assert run.suite == suite
    assert run.python == "3.13"
    assert run.argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest",
        "--with", "numpy",
        "--with", "polars",
        "--with", "pyyaml",
        "python", "-m", "pytest", "-q",
    )
    assert run.shell() == (
        "cd build && uv run --python 3.13 --with pytest --with numpy "
        "--with polars --with pyyaml python -m pytest -q"
    )


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 2
def test_hooks_has_two_separate_shell_forms_in_interpreter_order():
    suite, = runner.parse(_data("hooks"))
    runs = runner.runs(suite)
    assert [run.python for run in runs] == ["3.13", "/usr/bin/python3"]
    assert [run.shell() for run in runs] == [
        "cd hooks && uv run --python 3.13 --with pytest python -m pytest -q",
        "cd hooks && uv run --python /usr/bin/python3 --with pytest python -m pytest -q",
    ]


# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_are_opt_in_and_follow_default_dependencies():
    suite, = runner.parse(_data("build"))
    default_run, = runner.runs(suite)
    extras_run, = runner.runs(suite, extras=True)
    assert default_run.argv == _expected_argv("build", "3.13")
    assert extras_run.argv == _expected_argv("build", "3.13", extras=True)
    assert "arviz>=1.0" not in default_run.argv


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_pytest_arguments_reach_every_interpreter(registry_root):
    arguments = (
        "test_runtime_support.py", "-k", "declared_dependencies", "-s", "-rs",
    )
    observed = []

    def record(root, run):
        observed.append(run)
        return 0

    assert _main(
        ["hooks", "--", *arguments], registry_root, record
    ) == 0
    assert len(observed) == 2
    for run in observed:
        assert run.argv == _expected_argv("hooks", run.python, pytest_args=arguments)


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_quoting_preserves_arguments_and_shell_metacharacters():
    suite, = runner.parse(_data("build"))
    arguments = ("-k", "declared_dependencies or test_real_skill")
    run, = runner.runs(suite, extras=True, pytest_args=arguments)
    assert _shell_tokens(run.shell()) == [
        "cd", "build", "&&",
        *_expected_argv("build", "3.13", extras=True, pytest_args=arguments),
    ]


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_includes_all_fixture_suites_and_their_metadata(
    registry_root, capsys
):
    assert _main(["--list"], registry_root) == 0
    output = capsys.readouterr().out
    for name in ("bayesian-workflow", "build", "cc-guide", "hooks"):
        directory, _, extras, pythons = INVENTORY[name]
        assert name in output
        assert directory in output
        for python in pythons:
            expected = f"cd {directory} && {shlex.join(_expected_argv(name, python))}"
            assert expected in output
        for dependency in extras:
            assert dependency in output
        for note in NOTES.get(name, ()):
            assert note in output


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_can_select_only_named_suites(registry_root, capsys):
    assert _main(["--list", "hooks"], registry_root) == 0
    output = capsys.readouterr().out
    assert "hooks" in output
    assert "cd hooks &&" in output
    assert "cd build &&" not in output
    assert "cd skills/bayesian-workflow/scripts &&" not in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_matches_the_runs_it_describes(registry_root, capsys):
    arguments = ("-k", "declared_dependencies or test_real_skill", "-rs")
    assert _main(
        ["--list", "build", "--extras", "--", *arguments], registry_root
    ) == 0
    output = capsys.readouterr().out
    printed_shells = [
        line.strip() for line in output.splitlines()
        if line.strip().startswith("cd ")
    ]
    assert len(printed_shells) == 1
    assert _shell_tokens(printed_shells[0]) == [
        "cd", "build", "&&",
        *_expected_argv("build", "3.13", extras=True, pytest_args=arguments),
    ]

    observed = []

    def record(root, run):
        observed.append(run)
        return 0

    assert _main(
        ["build", "--extras", "--", *arguments], registry_root, record
    ) == 0
    assert [run.shell() for run in observed] == printed_shells


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_suite_and_interpreter_order(registry_root):
    observed = []

    def record(root, run):
        assert root == registry_root
        observed.append((run.suite.name, run.python))
        return 0

    assert _main(
        ["hooks", "bayesian-workflow", "build"], registry_root, record
    ) == 0
    assert observed == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("bayesian-workflow", "3.13"),
        ("build", "3.13"),
    ]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_precede_execution_and_notes_print_once(
    registry_root, capsys
):
    snapshots = []

    def record(root, run):
        output = capsys.readouterr().out
        header = f"== {run.suite.name} ({run.python})"
        assert header in output
        if run.python == "3.13":
            for note in NOTES[run.suite.name]:
                assert output.index(header) < output.index(note)
        else:
            for note in NOTES[run.suite.name]:
                assert note not in output
        snapshots.append(output)
        return 0

    assert _main(
        ["hooks", "bayesian-workflow"], registry_root, record
    ) == 0
    output = "".join(snapshots) + capsys.readouterr().out
    for name in ("hooks", "bayesian-workflow"):
        for note in NOTES[name]:
            assert output.count(note) == 1


# spec: "A failed run does not stop the next one."
# task: 4
@pytest.mark.parametrize(
    "statuses,expected",
    [
        ((0, 0, 0), 0),
        ((1, 0, 0), 1),
        ((5, 0, 0), 1),
        ((0, 0, 2), 1),
        ((1, 5, 0), 1),
    ],
)
def test_every_run_happens_after_failures(
    registry_root, capsys, statuses, expected
):
    observed = []

    def record(root, run):
        observed.append(run.label)
        return statuses[len(observed) - 1]

    assert _main(
        ["hooks", "bayesian-workflow"], registry_root, record
    ) == expected
    assert observed == [
        "hooks (3.13)",
        "hooks (/usr/bin/python3)",
        "bayesian-workflow (3.13)",
    ]


# spec: "The last line names the failed runs, or says that every run passed."
# task: 4
@pytest.mark.parametrize("statuses", [(0, 0), (5, 0), (1, 5)])
def test_final_summary_identifies_exactly_the_failed_runs(
    registry_root, capsys, statuses
):
    observed = []

    def record(root, run):
        observed.append(run.label)
        return statuses[len(observed) - 1]

    assert _main(["hooks"], registry_root, record) == int(any(statuses))
    captured = capsys.readouterr()
    summary = (captured.out + captured.err).strip().splitlines()[-1]
    if any(statuses):
        for label, status in zip(observed, statuses):
            if status:
                assert label in summary
            else:
                assert label not in summary
    else:
        assert "passed" in summary.casefold()


# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize(
    "args",
    [
        ["--unknown-option"],
        ["unknown-suite"],
        ["--list", "unknown-suite"],
        ["hooks", "unknown-suite"],
    ],
)
def test_usage_errors_and_unknown_suites_start_no_runs(registry_root, args):
    assert _main(args, registry_root) == 2


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_uses_directory_ancestry():
    suites = runner.parse(_data("build", "cc-guide", "hooks"))
    by_name = {suite.name: suite for suite in suites}
    assert runner.container(by_name["cc-guide"], suites) == by_name["build"]
    assert runner.container(by_name["build"], suites) is None
    assert runner.container(by_name["hooks"], suites) is None


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_omits_nested_suite_but_runs_every_other_interpreter(
    registry_root, capsys
):
    observed = []

    def record(root, run):
        observed.append((run.suite.name, run.python))
        return 0

    assert _main(["--all"], registry_root, record) == 0
    assert set(observed) == {
        ("bayesian-workflow", "3.13"),
        ("build", "3.13"),
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
    }
    assert len(observed) == 4
    output = capsys.readouterr().out
    assert len([
        line for line in output.splitlines()
        if "cc-guide" in line
    ]) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_explicitly_named_nested_suite_runs(registry_root):
    observed = []

    def record(root, run):
        observed.append((run.suite.name, run.python))
        return 0

    assert _main(["cc-guide"], registry_root, record) == 0
    assert observed == [("cc-guide", "3.13")]


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_receives_unchanged_environment_and_suite_cwd(
    registry_root, tmp_path, monkeypatch, capfd
):
    binary_dir = tmp_path / "bin"
    binary_dir.mkdir()
    snapshot = tmp_path / "snapshot.json"
    uv = binary_dir / "uv"
    uv.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "Path(os.environ['SUITE_ACCEPTANCE_SNAPSHOT']).write_text("
        "json.dumps({'env': dict(os.environ), 'cwd': os.getcwd(), "
        "'argv': sys.argv[1:]}))\n"
        "print('pytest output', flush=True)\n",
        encoding="utf-8",
    )
    uv.chmod(0o755)
    monkeypatch.setenv(
        "PATH", str(binary_dir) + os.pathsep + os.environ.get("PATH", "")
    )
    monkeypatch.setenv("SUITE_ACCEPTANCE_SNAPSHOT", str(snapshot))
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("PYTHONCOERCECLOCALE", "0")
    expected_environment = dict(os.environ)

    assert _main(
        ["bayesian-workflow", "--", "-s"],
        registry_root,
        runner.run_subprocess,
    ) == 0

    observed = json.loads(snapshot.read_text(encoding="utf-8"))
    assert observed["env"] == expected_environment
    assert Path(observed["cwd"]) == (
        registry_root / "skills/bayesian-workflow/scripts"
    )
    assert observed["argv"] == list(
        _expected_argv("bayesian-workflow", "3.13", pytest_args=("-s",))[1:]
    )
    assert "pytest output" in capfd.readouterr().out


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_is_a_failed_run_and_does_not_abort_remaining_runs(
    registry_root, tmp_path, monkeypatch, capsys
):
    empty_path = tmp_path / "empty-path"
    empty_path.mkdir()
    monkeypatch.setenv("PATH", str(empty_path))
    assert _main(
        ["hooks"], registry_root, runner.run_subprocess
    ) == 1
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "== hooks (3.13)" in output
    assert "== hooks (/usr/bin/python3)" in output
    summary = output.strip().splitlines()[-1]
    assert "hooks (3.13)" in summary
    assert "hooks (/usr/bin/python3)" in summary


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_cli_works_from_an_unrelated_working_directory(tmp_path):
    result = subprocess.run(
        [sys.executable, str(REPO / "build/run_suites.py"), "--list", "build"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (
        "cd build && uv run --python 3.13 --with pytest --with numpy "
        "--with polars --with pyyaml python -m pytest -q"
    ) in result.stdout


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize("filename", ["test_new.py", "new_test.py"])
def test_both_pytest_filename_patterns_require_registration(
    git_root, filename
):
    directory = "skills/write-with-asd-ste100/scripts"
    _write(git_root, f"{directory}/{filename}", "def test_new(): pass\n")
    findings = runner.check(git_root, _data("hooks"))
    assert len(findings) == 1
    assert directory in findings[0]


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_non_pytest_files_do_not_create_coverage_findings(git_root):
    _write(git_root, "skills/write-with-asd-ste100/scripts/runtime_support.py")
    _write(git_root, "skills/write-with-asd-ste100/scripts/test_new.txt")
    assert runner.check(git_root, _data("hooks")) == []


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_one_coverage_finding_per_unregistered_directory(git_root):
    directory = "skills/write-with-asd-ste100/scripts"
    _write(git_root, f"{directory}/test_new.py")
    _write(git_root, f"{directory}/new_test.py")
    findings = runner.check(git_root, _data("hooks"))
    assert len(findings) == 1
    assert directory in findings[0]


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
@pytest.mark.parametrize("create_directory", [False, True])
def test_registered_directory_must_exist_and_hold_tests(
    tmp_path, create_directory
):
    _git(tmp_path, "init", "--quiet")
    data = _data("hooks")
    _write_registry(tmp_path, data)
    if create_directory:
        (tmp_path / "hooks").mkdir()
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert "hooks" in findings[0]


# spec: "Today that is `cc-guide`: `cd build && pytest` collects `build/cc_guide` already."
# task: 3
def test_registered_parent_covers_pytest_files_in_descendants(tmp_path):
    _git(tmp_path, "init", "--quiet")
    data = _data("build")
    _write_registry(tmp_path, data)
    _write(tmp_path, "build/cc_guide/test_new.py")
    assert runner.check(tmp_path, data) == []


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
@pytest.mark.parametrize("tracked", [False, True])
def test_tracked_and_untracked_new_suites_both_count(git_root, tracked):
    relative = "skills/write-with-asd-ste100/scripts/test_new.py"
    _write(git_root, relative)
    if tracked:
        _git(git_root, "add", relative)
    assert "skills/write-with-asd-ste100/scripts" in runner.pytest_dirs(git_root)
    findings = runner.check(git_root, _data("hooks"))
    assert len(findings) == 1
    assert "skills/write-with-asd-ste100/scripts" in findings[0]


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_ignored_worktrees_and_scratch_are_excluded(git_root):
    _write(git_root, ".gitignore", ".claude/worktrees/\nbuild/.scratch/\n")
    _write(git_root, ".claude/worktrees/hooks/test_new.py")
    _write(git_root, "build/.scratch/test_new.py")
    directories = runner.pytest_dirs(git_root)
    assert directories == {"hooks"}
    assert runner.check(git_root, _data("hooks")) == []


# spec: "The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root."
# task: 3
def test_git_inventory_uses_required_flags_at_the_repo_root(
    git_root, tmp_path, monkeypatch
):
    real_git = shutil.which("git")
    assert real_git
    binary_dir = tmp_path / "git-bin"
    binary_dir.mkdir()
    record_path = tmp_path / "git-calls.jsonl"
    git = binary_dir / "git"
    git.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "with open(os.environ['SUITE_ACCEPTANCE_GIT_CALLS'], 'a') as stream:\n"
        "    stream.write(json.dumps({'argv': sys.argv[1:], "
        "'cwd': os.getcwd()}) + '\\n')\n"
        f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n",
        encoding="utf-8",
    )
    git.chmod(0o755)
    monkeypatch.setenv(
        "PATH", str(binary_dir) + os.pathsep + os.environ.get("PATH", "")
    )
    monkeypatch.setenv("SUITE_ACCEPTANCE_GIT_CALLS", str(record_path))

    assert runner.pytest_dirs(git_root) == {"hooks"}
    calls = [
        json.loads(line)
        for line in record_path.read_text(encoding="utf-8").splitlines()
    ]
    inventories = [call for call in calls if "ls-files" in call["argv"]]
    assert len(inventories) == 1
    inventory = inventories[0]
    assert Path(inventory["cwd"]) == git_root
    assert {
        "ls-files", "--cached", "--others", "--exclude-standard"
    } <= set(inventory["argv"])


# spec: "If git fails, `--check` fails."
# task: 4
def test_check_fails_outside_a_git_repository(tmp_path, capsys):
    _write_registry(tmp_path, _data("hooks"))
    _write(tmp_path, "hooks/test_new.py")
    assert runner.pytest_dirs(tmp_path) is None
    assert _main(["--check"], tmp_path) == 1
    captured = capsys.readouterr()
    assert "suite registry ok" not in captured.out + captured.err


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_success_output(git_root, capsys):
    assert _main(["--check"], git_root) == 0
    captured = capsys.readouterr()
    assert captured.out == "suite registry ok\n"
    assert captured.err == ""


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_prints_each_finding_on_its_own_line(git_root, capsys):
    _write(git_root, "skills/write-with-asd-ste100/scripts/test_new.py")
    _write(git_root, "skills/brainstorming/scripts/test_new.py")
    expected = runner.check(git_root, _data("hooks"))
    assert len(expected) == 2
    assert _main(["--check"], git_root) == 1
    captured = capsys.readouterr()
    lines = (captured.out + captured.err).splitlines()
    assert sorted(lines) == sorted(expected)


# spec: "Until plan 52 adds the entry, the ninth lint refuses its new suite directory."
# task: 3
def test_plan_52_suite_requires_its_own_registry_entry(git_root):
    directory = "skills/write-with-asd-ste100/scripts"
    _write(git_root, f"{directory}/test_new.py")
    assert runner.check(git_root, _data("hooks"))

    data = _data("hooks")
    data["suite"].append({
        "name": "write-with-asd-ste100",
        "dir": directory,
        "with": ["pytest"],
    })
    _write_registry(git_root, data)
    assert runner.check(git_root, data) == []


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_is_sorted_and_has_unique_names_and_directories():
    data = tomllib.loads((REPO / REGISTRY).read_text(encoding="utf-8"))
    assert runner.validate(data) == []
    names = [table["name"] for table in data["suite"]]
    directories = [table["dir"] for table in data["suite"]]
    assert names == sorted(names)
    assert len(names) == len(set(names))
    assert len(directories) == len(set(directories))


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_documents_schema_sorting_and_lint():
    text = (REPO / REGISTRY).read_text(encoding="utf-8")
    header = text.split("[[suite]]", 1)[0]
    comments = "\n".join(
        line for line in header.splitlines() if line.lstrip().startswith("#")
    ).casefold()
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert re.search(rf"\b{key}\b", comments)
    assert re.search(r"\bsort(?:ed|ing)?\b", comments)
    assert re.search(r"\b(?:nine|ninth|9|9th)\b", comments)
    assert "lint" in comments


# spec: "The inventory, from `CLAUDE.md` at `456e3fb`:"
# task: 5
@pytest.mark.parametrize("name", list(INVENTORY))
def test_real_registry_preserves_specified_inventory(name):
    data = tomllib.loads((REPO / REGISTRY).read_text(encoding="utf-8"))
    tables = {table["name"]: table for table in data["suite"]}
    assert name in tables
    directory, dependencies, extras, pythons = INVENTORY[name]
    table = tables[name]
    assert table["dir"] == directory
    assert table["with"] == ["pytest", *dependencies]
    assert table.get("extras", []) == list(extras)
    assert table.get("pythons", ["3.13"]) == list(pythons)


# spec: "A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`."
# task: 5
def test_real_registry_suite_names_match_the_spec():
    data = tomllib.loads((REPO / REGISTRY).read_text(encoding="utf-8"))
    for table in data["suite"]:
        directory = Path(table["dir"])
        if directory.parts[0] == "skills":
            assert table["name"] == directory.parts[1]
        else:
            expected = {
                "build": "build",
                "build/cc_guide": "cc-guide",
                "hooks": "hooks",
            }
            assert table["name"] == expected[table["dir"]]


# spec: "Examples: `build`'s missing `build/.scratch/` in a fresh clone or worktree; `bayesian-workflow`'s `CALIBRATION_SWEEP=1` sweep and its expected arviz warnings; `llm-wiki`'s `@needs_pilot` tests and `$LLM_WIKI_ROOT`; `brainstorming`'s node skip; `tune-hyperparameters`' \"`--with sklearn` fails\"; `track-model-experiments`' run time; the guard's 3.9 floor, its launchd-PATH skips and its Gate B probe for `hooks`."
# task: 5
@pytest.mark.parametrize(
    "name,topics",
    [
        ("build", ("build/.scratch/",)),
        ("bayesian-workflow", ("CALIBRATION_SWEEP=1", "arviz", "warn")),
        ("llm-wiki", ("@needs_pilot", "$LLM_WIKI_ROOT")),
        ("brainstorming", ("node", "skip")),
        ("tune-hyperparameters", ("--with sklearn", "fail")),
        ("hooks", ("3.9", "launchd", "PATH", "Gate B")),
    ],
)
def test_real_registry_preserves_explicit_note_topics(name, topics):
    data = tomllib.loads((REPO / REGISTRY).read_text(encoding="utf-8"))
    tables = {table["name"]: table for table in data["suite"]}
    notes = "\n".join(tables[name].get("notes", [])).casefold()
    for topic in topics:
        assert topic.casefold() in notes


# spec: "`build/suites.toml` registers every directory suite (R2.3) and `--check` passes."
# task: 5
def test_real_registry_check_passes(capsys):
    assert _main(["--check"], REPO) == 0
    captured = capsys.readouterr()
    assert captured.out == "suite registry ok\n"
    assert captured.err == ""


# spec: "R4.4 `build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_suite_registry_is_the_ninth_and_last_commit_lint():
    text = (REPO / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    commands = _lint_commands(text)
    assert len(commands) == 9
    name, command = commands[-1]
    assert name == "suite_registry"
    assert shlex.split(command) == [
        "uv", "run", "--python", "3.13",
        "python", "build/run_suites.py", "--check",
    ]
    comments = "\n".join(
        line for line in text.splitlines()
        if line.lstrip().startswith("#")
    )
    assert re.search(r"\bnine\b", comments, re.IGNORECASE)


# spec: "It does not call the runner, except for the new `--check` lint (R4)."
# task: 6
def test_other_commit_lints_do_not_call_the_suite_runner():
    text = (REPO / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    runner_commands = [
        (name, command)
        for name, command in _lint_commands(text)
        if "run_suites.py" in command
    ]
    assert len(runner_commands) == 1
    assert runner_commands[0][0] == "suite_registry"
    assert shlex.split(runner_commands[0][1])[-1] == "--check"


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_unregistered_suite_is_refused(tmp_path):
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "--quiet", "--no-hardlinks", str(REPO), str(clone)],
        check=True,
        text=True,
        capture_output=True,
    )
    relative = "skills/suite-registry-acceptance-unregistered/scripts/test_new.py"
    assert not (clone / relative).exists()
    _write(clone, relative, "def test_new(): pass\n")
    _git(clone, "add", relative)
    _git(
        clone,
        "-c", "core.hooksPath=/dev/null",
        "-c", "commit.gpgsign=false",
        "-c", "user.name=Acceptance",
        "-c", "user.email=acceptance@example.invalid",
        "commit", "--quiet", "-m", "Add an unregistered test suite",
    )

    script = (clone / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    commands = _lint_commands(script)
    assert len(commands) == 9
    results = {
        name: subprocess.run(
            ["bash", "-c", command],
            cwd=clone,
            text=True,
            capture_output=True,
        )
        for name, command in commands
    }
    failed = {
        name: result.stdout + result.stderr
        for name, result in results.items()
        if result.returncode
    }
    assert set(failed) == {"suite_registry"}, failed

    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=clone,
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0


# spec: "`build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_documentation_describes_the_ninth_lint():
    text = (REPO / "build/CLAUDE.md").read_text(encoding="utf-8")
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    paragraphs = re.split(r"\n\s*\n", text)
    assert any(
        all(word in paragraph for word in (
            "suites.toml", "run_suites.py", "--check", "commit lint",
        ))
        for paragraph in paragraphs
    )


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_intro_keeps_execution_rules_and_names_the_registry():
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    intro_lines = [
        line for line in text.splitlines()
        if all(word in line for word in (
            "build/suites.toml", "build/run_suites.py", "test_build.py",
        ))
    ]
    assert len(intro_lines) == 1
    intro = intro_lines[0]
    assert "uv" in intro
    assert "3.13" in intro
    assert "director" in intro.casefold()
    assert "colli" in intro.casefold()
    assert "notes" in intro.casefold()
    assert "before" in intro.casefold()
    assert "There is no root test runner" not in text


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_commands_document_all_four_runner_invocations():
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    prefix = "uv run --python 3.13 python build/run_suites.py"
    for suffix in (
        "--list",
        "<name> [--extras] [-- <pytest args>]",
        "--all",
        "--check",
    ):
        assert f"{prefix} {suffix}" in text
    assert re.search(r"\bnine\b", text, re.IGNORECASE)
    assert re.search(r"suite[-_]registry|suite registry", text, re.IGNORECASE)


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_named_selection_and_tool_commands_remain_literal():
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    code = "\n".join(re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL))
    for fragment in (
        "test_runtime_support.py",
        "test_commit_lints.py",
        "declared_dependencies",
        "test_real_skill",
        "test_check_jax_examples.py",
        "run_commit_lints.sh",
        "verify_citations.py",
        "extract_structure.py",
        "cli.py lint",
        "cli.py check",
    ):
        assert fragment in code
    assert "Single test" in text


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_file_is_under_limit_and_has_no_whole_directory_pytest_commands():
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    registry = tomllib.loads((REPO / REGISTRY).read_text(encoding="utf-8"))
    directories = {table["dir"] for table in registry["suite"]}

    for line in text.splitlines():
        if not line.strip().startswith("cd "):
            continue
        tokens = shlex.split(line, comments=True)
        if len(tokens) < 3 or tokens[0] != "cd" or tokens[1] not in directories:
            continue
        chunks = []
        chunk = []
        for token in tokens[3:]:
            if token == "&&":
                chunks.append(chunk)
                chunk = []
            else:
                chunk.append(token)
        chunks.append(chunk)
        for command in chunks:
            for index in range(len(command) - 1):
                if command[index:index + 2] == ["-m", "pytest"]:
                    pytest_arguments = command[index + 2:]
                    assert pytest_arguments != ["-q"], line
                    assert pytest_arguments, line


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_root_documentation_has_no_numeric_suite_or_test_count_claim():
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    assert not re.search(r"\b\d+\s+(?:suites?|tests?)\b", text, re.IGNORECASE)


# spec: "The comment names the suite `run_suites.py cc-guide` instead of \"its suite\"."
# task: 7
def test_cc_guide_comment_uses_the_specified_suite_name():
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    assert "run_suites.py cc-guide" in text


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_uses_the_stamp_instead_of_pilot_note():
    first_line = (REPO / "CLAUDE.md").read_text(
        encoding="utf-8"
    ).splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .+ @\S+ -->", first_line)

    source = (REPO / "build/test_check_conformance.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    function = next(
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    for assertion in ast.walk(function):
        if isinstance(assertion, ast.Assert):
            assert not any(
                isinstance(node, ast.Constant) and node.value == "@needs_pilot"
                for node in ast.walk(assertion.test)
            )


# spec: "`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`."
# task: 6
@pytest.mark.parametrize(
    "relative", ["build/run_suites.py", "build/test_run_suites.py"]
)
def test_runner_and_tests_are_committed(relative):
    committed = subprocess.run(
        ["git", "-C", str(REPO), "show", f"HEAD:{relative}"],
        capture_output=True,
        check=True,
    )
    assert committed.stdout == (REPO / relative).read_bytes()


# spec: "**The Stage 2 audit** (one time, a scratch script that is never committed, as in plan 38's Task 2)."
# task: 5
def test_command_audit_scratch_script_is_not_committed():
    result = _git(
        REPO,
        "cat-file", "-e",
        "HEAD:.sdd/55-test-suite-registry/audit_commands.py",
        check=False,
    )
    assert result.returncode != 0


# spec: "`bash build/run_commit_lints.sh` prints `commit lints passed`."
# task: 6
def test_clean_repository_passes_the_commit_lint_gate():
    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "commit lints passed" in result.stdout + result.stderr
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`.</plan></flag>
<flag task="5"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>`cc_guide`</plan></flag>
</flags>
<untestable>
Design approved in brainstorming on 2026-10-18.
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
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
"This work lands whole, registry and CLAUDE.md shrink, ahead of plan 52's Task 6.
Task 6 then adds one build/suites.toml entry instead of editing Commands.
Plan 52's planning session amends its plan to match and records Q4 as (c)."
Matches conformance.toml and manifest.toml.
Rejected: a Python list inside the runner (every suite change becomes a code edit), and one manifest per suite directory (`install.py` copies skill directories, so the manifests would ship with installed skills).
An `@`-imported document was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
**Design section 1** (the registry keys and the runner's behaviour) was approved as presented.
**Design section 2** (the guard, the file edits, the tests and the couplings) was approved as presented.
On `main` at `456e3fb` there are 18: the 17 in `CLAUDE.md` lines 66–125, and `build/cc_guide`, whose command is line 145.
They are selections or tools, not directory suites, and their comments say when to run them:
`build/run_commit_lints.sh` keeps its literal commands.
The entries carry the text of today's commands and comments.
Every command, dependency and note survives; the only change is the form.
The notes carry the rest of each comment.
With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character.
Same number of lines.
Line 133 is not touched (plan 53's Task 7 edits it).
The file ends at about 145 lines.
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
It would need node, a 3.9 `/usr/bin/python3` and `build/.scratch/`.
</untestable>