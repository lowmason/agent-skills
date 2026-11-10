<tests>
import ast
import copy
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


ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "build" / "run_suites.py").is_file()
)
RUNNER_PATH = ROOT / "build" / "run_suites.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "acceptance_run_suites", RUNNER_PATH
)
RUNNER = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = RUNNER
MODULE_SPEC.loader.exec_module(RUNNER)

FIXTURE = """
[[suite]]
name = "build"
dir = "build"
with = ["pytest", "numpy", "polars", "pyyaml"]
extras = ["arviz>=1.0"]
notes = ["Build note."]

[[suite]]
name = "cc-guide"
dir = "build/cc_guide"
with = ["pytest"]
notes = ["Guide note."]

[[suite]]
name = "hooks"
dir = "hooks"
with = ["pytest"]
pythons = ["3.13", "/usr/bin/python3"]
notes = ["Hook note."]
"""

SINGLE = """
[[suite]]
name = "build"
dir = "build"
with = ["pytest"]
"""


def write(root, relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def fixture_root(tmp_path, registry=FIXTURE):
    root = tmp_path / "repo"
    root.mkdir()
    write(root, "build/suites.toml", registry)
    write(root, "build/test_build.py", "def test_build(): pass\n")
    write(root, "build/cc_guide/test_guide.py", "def test_guide(): pass\n")
    write(root, "hooks/test_hooks.py", "def test_hooks(): pass\n")
    return root


def git_root(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(
        ["git", "init", "--quiet"], cwd=root, check=True, capture_output=True
    )
    write(root, "build/suites.toml", SINGLE)
    write(root, "build/test_build.py", "def test_build(): pass\n")
    subprocess.run(
        ["git", "add", "build/suites.toml", "build/test_build.py"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return root


def status(argv, root, run_one=None):
    try:
        if run_one is None:
            return RUNNER.main(argv, root=root)
        return RUNNER.main(argv, root=root, run_one=run_one)
    except SystemExit as error:
        return error.code


def registry_data(root):
    return tomllib.loads((root / "build/suites.toml").read_text())


def all_output(capsys):
    captured = capsys.readouterr()
    return captured.out + captured.err


def invalid_registries():
    base = {"suite": [{"name": "build", "dir": "build", "with": ["pytest"]}]}
    cases = []

    for key in ("name", "dir", "with"):
        data = copy.deepcopy(base)
        del data["suite"][0][key]
        cases.append(data)

    for key, value in (
        ("name", 7),
        ("dir", 7),
        ("with", "pytest"),
        ("with", ["pytest", 7]),
        ("extras", "numpy"),
        ("extras", [7]),
        ("pythons", "3.13"),
        ("pythons", [7]),
        ("notes", "note"),
        ("notes", [7]),
    ):
        data = copy.deepcopy(base)
        data["suite"][0][key] = value
        cases.append(data)

    data = copy.deepcopy(base)
    data["suite"][0]["unexpected"] = True
    cases.append(data)

    data = copy.deepcopy(base)
    data["suite"][0]["with"] = ["numpy"]
    cases.append(data)

    data = copy.deepcopy(base)
    data["suite"].append(
        {"name": "build", "dir": "hooks", "with": ["pytest"]}
    )
    cases.append(data)

    data = copy.deepcopy(base)
    data["suite"].append(
        {"name": "hooks", "dir": "build", "with": ["pytest"]}
    )
    cases.append(data)

    return cases


# spec: "R2.1 One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_registry_names_are_sorted_and_unique():
    rows = tomllib.loads((ROOT / "build/suites.toml").read_text())["suite"]
    names = [row["name"] for row in rows]
    directories = [row["dir"] for row in rows]
    assert len(rows) == 18
    assert names == sorted(names)
    assert len(names) == len(set(names))
    assert len(directories) == len(set(directories))


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_explains_its_contract():
    header = (ROOT / "build/suites.toml").read_text().split("[[suite]]", 1)[0]
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert key in header
    assert "sort" in header.lower()
    assert "commit lint" in header.lower()
    assert "ninth" in header.lower() or "9th" in header.lower()


# spec: "R2.3 The entries carry the text of today's commands and comments."
# task: 5
def test_registry_has_the_specified_directory_suites_and_dependencies():
    expected = {
        "bayesian-workflow": (
            "skills/bayesian-workflow/scripts",
            ["pytest", "arviz", "arviz-stats", "numpy", "xarray"],
            ["matplotlib"],
            ["3.13"],
        ),
        "brainstorming": (
            "skills/brainstorming/scripts",
            ["pytest"],
            [],
            ["3.13"],
        ),
        "build": (
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
        "cc-guide": ("build/cc_guide", ["pytest"], [], ["3.13"]),
        "classification-codes": (
            "skills/classification-codes/scripts",
            ["pytest", "polars"],
            [],
            ["3.13"],
        ),
        "describe-critique-methodology": (
            "skills/describe-critique-methodology/scripts",
            ["pytest"],
            [],
            ["3.13"],
        ),
        "design-architecture": (
            "skills/design-architecture/scripts",
            ["pytest"],
            [],
            ["3.13"],
        ),
        "explore-data": (
            "skills/explore-data/scripts",
            ["pytest", "polars"],
            [],
            ["3.13"],
        ),
        "geographic-codes": (
            "skills/geographic-codes/scripts",
            ["pytest", "polars", "fastexcel"],
            [],
            ["3.13"],
        ),
        "hooks": ("hooks", ["pytest"], [], ["3.13", "/usr/bin/python3"]),
        "llm-wiki": ("skills/llm-wiki/scripts", ["pytest"], [], ["3.13"]),
        "recommend-probabilistic-model": (
            "skills/recommend-probabilistic-model/scripts",
            ["pytest", "numpy", "polars"],
            [],
            ["3.13"],
        ),
        "recommend-visualization": (
            "skills/recommend-visualization/scripts",
            ["pytest", "numpy", "polars"],
            [],
            ["3.13"],
        ),
        "subagent-driven-development": (
            "skills/subagent-driven-development/scripts",
            ["pytest"],
            [],
            ["3.13"],
        ),
        "systematic-debugging": (
            "skills/systematic-debugging",
            ["pytest"],
            [],
            ["3.13"],
        ),
        "track-model-experiments": (
            "skills/track-model-experiments/scripts",
            [
                "pytest",
                "numpy",
                "polars",
                "arviz",
                "numpyro",
                "h5netcdf",
                "h5py",
            ],
            [],
            ["3.13"],
        ),
        "tune-hyperparameters": (
            "skills/tune-hyperparameters/scripts",
            ["pytest", "numpy", "polars"],
            ["scikit-learn", "optuna"],
            ["3.13"],
        ),
        "writing-plans": (
            "skills/writing-plans/scripts",
            ["pytest"],
            [],
            ["3.13"],
        ),
    }
    rows = tomllib.loads((ROOT / "build/suites.toml").read_text())["suite"]
    actual = {
        row["name"]: (
            row["dir"],
            row["with"],
            row.get("extras", []),
            row.get("pythons", ["3.13"]),
        )
        for row in rows
    }
    assert actual == expected
    assert all(
        set(row) <= {"name", "dir", "with", "extras", "pythons", "notes"}
        for row in rows
    )


# spec: "The notes carry the rest of each comment."
# task: 5
def test_registry_preserves_the_named_operational_notes():
    rows = tomllib.loads((ROOT / "build/suites.toml").read_text())["suite"]
    notes = {
        row["name"]: " ".join(row.get("notes", []))
        for row in rows
    }
    assert "build/.scratch/" in notes["build"]
    assert "CALIBRATION_SWEEP=1" in notes["bayesian-workflow"]
    assert "arviz" in notes["bayesian-workflow"].lower()
    assert "warning" in notes["bayesian-workflow"].lower()
    assert "node" in notes["brainstorming"].lower()
    assert "@needs_pilot" in notes["llm-wiki"]
    assert "LLM_WIKI_ROOT" in notes["llm-wiki"]
    assert "--with sklearn" in notes["tune-hyperparameters"]
    assert any(
        word in notes["track-model-experiments"].lower()
        for word in ("time", "minute", "runtime")
    )
    for word in ("3.9", "launchd", "PATH", "Gate B"):
        assert word.lower() in notes["hooks"].lower()


# spec: "R3.1 Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 4
def test_runner_imports_only_stdlib_modules():
    tree = ast.parse(RUNNER_PATH.read_text())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    assert {"tomllib", "argparse", "subprocess", "shlex"} <= imports
    assert imports <= sys.stdlib_module_names | {"__future__"}


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 2
def test_repo_constant_is_script_relative(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert Path(RUNNER.REPO).resolve() == ROOT.resolve()


# spec: "Invoked as `uv run --python 3.13 python build/run_suites.py …` from any directory."
# task: 4
def test_runner_can_list_from_another_working_directory(tmp_path):
    result = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--list", "cc-guide"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert "cc-guide" in result.stdout
    assert "build/cc_guide" in result.stdout


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_run_argv_uses_every_dependency_in_order():
    suite = RUNNER.Suite(
        name="build",
        dir="build",
        deps=("pytest", "numpy", "polars", "pyyaml"),
    )
    run = RUNNER.runs(suite)[0]
    assert run.argv == (
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
    assert run.label == "build (3.13)"


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 5
def test_hooks_has_two_independent_shell_commands():
    suites = RUNNER.parse(tomllib.loads((ROOT / "build/suites.toml").read_text()))
    hooks = next(suite for suite in suites if suite.name == "hooks")
    commands = [run.shell() for run in RUNNER.runs(hooks)]
    assert commands == [
        "cd hooks && uv run --python 3.13 --with pytest python -m pytest -q",
        "cd hooks && uv run --python /usr/bin/python3 --with pytest python -m pytest -q",
    ]


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_directory_and_dependency_words():
    suite = RUNNER.Suite(
        name="build",
        dir="directory with spaces",
        deps=("pytest", "arviz>=1.0"),
    )
    run = RUNNER.runs(suite)[0]
    directory_part, command_part = run.shell().split(" && ", 1)
    assert shlex.split(directory_part) == ["cd", "directory with spaces"]
    assert shlex.split(command_part) == list(run.argv)
    assert "'arviz>=1.0'" in command_part


# spec: "R3.5 **`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_follow_default_dependencies():
    suite = RUNNER.Suite(
        name="build",
        dir="build",
        deps=("pytest", "numpy"),
        extras=("arviz>=1.0", "matplotlib"),
    )
    argv = RUNNER.runs(suite, extras=True)[0].argv
    assert argv == (
        "uv",
        "run",
        "--python",
        "3.13",
        "--with",
        "pytest",
        "--with",
        "numpy",
        "--with",
        "arviz>=1.0",
        "--with",
        "matplotlib",
        "python",
        "-m",
        "pytest",
        "-q",
    )


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_pytest_arguments_reach_every_interpreter(tmp_path):
    root = fixture_root(tmp_path)
    received = []

    def run_one(root, run):
        received.append(run.argv)
        return 0

    assert status(
        ["hooks", "--", "-k", "declared_dependencies", "-s", "-rs"],
        root,
        run_one,
    ) == 0
    assert len(received) == 2
    assert all(
        argv[-5:] == ("-k", "declared_dependencies", "-s", "-rs")[-5:]
        for argv in received
    )


# spec: "R3.3 **`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_defaults_to_all_suites_and_shows_their_details(tmp_path, capsys):
    root = fixture_root(tmp_path)
    assert status(["--list"], root) == 0
    output = capsys.readouterr().out
    for name, directory in (
        ("build", "build"),
        ("cc-guide", "build/cc_guide"),
        ("hooks", "hooks"),
    ):
        assert name in output
        assert directory in output
    assert "arviz>=1.0" in output
    assert "Build note." in output
    assert "Guide note." in output
    assert "Hook note." in output
    assert "cd build && uv run" in output
    assert "cd build/cc_guide && uv run" in output
    assert output.count("cd hooks && uv run") == 2


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_prints_the_command_with_extras_and_pytest_args(tmp_path, capsys):
    root = fixture_root(tmp_path)
    suite = next(
        suite
        for suite in RUNNER.parse(registry_data(root))
        if suite.name == "build"
    )
    expected = RUNNER.runs(
        suite,
        extras=True,
        pytest_args=("-k", "declared_dependencies"),
    )[0].shell()
    assert status(
        ["--list", "build", "--extras", "--", "-k", "declared_dependencies"],
        root,
    ) == 0
    output = capsys.readouterr().out
    assert expected in output
    assert "cc-guide" not in output
    assert "hooks" not in output


# spec: "R3.4 **`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_suites_run_in_requested_order(tmp_path):
    root = fixture_root(tmp_path)
    received = []

    def run_one(root, run):
        received.append((run.suite.name, run.python))
        return 0

    assert status(["hooks", "build"], root, run_one) == 0
    assert received == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("build", "3.13"),
    ]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_precede_pytest_output(tmp_path, capsys):
    root = fixture_root(tmp_path)

    def run_one(root, run):
        print("pytest output")
        return 0

    assert status(["hooks"], root, run_one) == 0
    output = capsys.readouterr().out
    assert output.index("== hooks (3.13)") < output.index("Hook note.")
    assert output.index("Hook note.") < output.index("pytest output")
    assert output.index("== hooks (/usr/bin/python3)") > output.index(
        "pytest output"
    )
    assert output.count("Hook note.") == 1
    assert output.count("pytest output") == 2


# spec: "A failed run does not stop the next one."
# task: 4
def test_failure_does_not_stop_later_runs(tmp_path):
    root = fixture_root(tmp_path)
    received = []

    def run_one(root, run):
        received.append(run.label)
        return 5 if run.label == "hooks (3.13)" else 0

    assert status(["hooks", "build"], root, run_one) == 1
    assert received == [
        "hooks (3.13)",
        "hooks (/usr/bin/python3)",
        "build (3.13)",
    ]


# spec: "R3.6 **`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_skips_the_nested_cc_guide_suite(tmp_path, capsys):
    root = fixture_root(tmp_path)
    received = []

    def run_one(root, run):
        received.append(run.suite.name)
        return 0

    assert status(["--all"], root, run_one) == 0
    output = all_output(capsys)
    assert received == ["build", "hooks"]
    skip_lines = [line for line in output.splitlines() if "cc-guide" in line]
    assert len(skip_lines) == 1
    assert "build" in skip_lines[0]


# spec: "A suite named on the command line always runs."
# task: 4
def test_named_nested_suite_runs(tmp_path):
    root = fixture_root(tmp_path)
    received = []

    def run_one(root, run):
        received.append(run.suite.name)
        return 0

    assert status(["cc-guide"], root, run_one) == 0
    assert received == ["cc-guide"]


# spec: "R3.7 **Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_run_exit_statuses_include_pytest_exit_five(tmp_path):
    root = fixture_root(tmp_path)
    assert status(["build"], root, lambda root, run: 0) == 0
    assert status(["build"], root, lambda root, run: 1) == 1
    assert status(["build"], root, lambda root, run: 5) == 1
    assert status([], root) == 2
    assert status(["unknown-suite"], root) == 2


# spec: "The last line names the failed runs, or says that every run passed."
# task: 4
def test_final_line_reports_success_or_failed_run_labels(tmp_path, capsys):
    root = fixture_root(tmp_path)
    assert status(["build"], root, lambda root, run: 0) == 0
    success = all_output(capsys).strip().splitlines()[-1].lower()
    assert "passed" in success

    assert status(["build"], root, lambda root, run: 5) == 1
    failure = all_output(capsys).strip().splitlines()[-1]
    assert "build (3.13)" in failure


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_counts_as_a_failed_run(tmp_path, monkeypatch):
    root = fixture_root(tmp_path)
    empty_path = tmp_path / "empty-path"
    empty_path.mkdir()
    monkeypatch.setenv("PATH", str(empty_path))
    suite = RUNNER.Suite(name="build", dir="build", deps=("pytest",))
    run = RUNNER.runs(suite)[0]
    assert RUNNER.run_subprocess(root, run) != 0


# spec: "R3.8 The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_receives_environment_and_suite_working_directory(
    tmp_path, monkeypatch
):
    root = fixture_root(tmp_path)
    binary_dir = tmp_path / "bin"
    binary_dir.mkdir()
    capture = tmp_path / "capture.json"
    stub = binary_dir / "uv"
    stub.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "with open(os.environ['RUNNER_CAPTURE'], 'w') as output:\n"
        "    json.dump({'argv': sys.argv[1:], 'cwd': os.getcwd(), "
        "'sweep': os.environ.get('CALIBRATION_SWEEP')}, output)\n"
    )
    stub.chmod(0o755)
    monkeypatch.setenv("PATH", str(binary_dir) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("RUNNER_CAPTURE", str(capture))
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    suite = RUNNER.Suite(name="build", dir="build", deps=("pytest",))
    run = RUNNER.runs(suite)[0]

    assert RUNNER.run_subprocess(root, run) == 0
    recorded = json.loads(capture.read_text())
    assert recorded["argv"] == list(run.argv[1:])
    assert Path(recorded["cwd"]) == root / "build"
    assert recorded["sweep"] == "1"


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
def test_validation_rejects_each_specified_registry_error():
    for data in invalid_registries():
        assert RUNNER.validate(data), data


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_invalid_registry_stops_every_execution_mode(tmp_path):
    invalid = """
[[suite]]
name = "build"
dir = "build"
with = ["numpy"]
"""
    root = fixture_root(tmp_path, invalid)
    for argv in (["--list"], ["build"], ["--all"]):
        assert status(argv, root, lambda root, run: pytest.fail("ran pytest")) == 2


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
def test_check_reports_registry_validation_problems(tmp_path):
    root = git_root(tmp_path)
    data = registry_data(root)
    data["suite"][0]["unexpected"] = True
    findings = RUNNER.check(root, data)
    assert findings
    assert any("unexpected" in finding for finding in findings)


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_check_finds_both_pytest_filename_patterns(tmp_path):
    root = git_root(tmp_path)
    write(root, "skills/brainstorming/scripts/test_new.py", "")
    write(root, "skills/llm-wiki/scripts/new_test.py", "")
    findings = RUNNER.check(root, registry_data(root))
    assert any("skills/brainstorming/scripts" in line for line in findings)
    assert any("skills/llm-wiki/scripts" in line for line in findings)


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_finds_missing_registered_directory(tmp_path):
    root = git_root(tmp_path)
    write(
        root,
        "build/suites.toml",
        SINGLE
        + """
[[suite]]
name = "hooks"
dir = "hooks"
with = ["pytest"]
""",
    )
    findings = RUNNER.check(root, registry_data(root))
    assert any("hooks" in line for line in findings)


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_finds_registered_directory_without_tests(tmp_path):
    root = git_root(tmp_path)
    write(root, "hooks/README.md", "No tests here.\n")
    write(
        root,
        "build/suites.toml",
        SINGLE
        + """
[[suite]]
name = "hooks"
dir = "hooks"
with = ["pytest"]
""",
    )
    findings = RUNNER.check(root, registry_data(root))
    assert any("hooks" in line for line in findings)


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_registered_parent_covers_nested_test_files(tmp_path):
    root = git_root(tmp_path)
    write(root, "build/cc_guide/test_guide.py", "")
    assert RUNNER.check(root, registry_data(root)) == []


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_check_ignores_gitignored_test_directories(tmp_path):
    root = git_root(tmp_path)
    write(
        root,
        ".gitignore",
        ".claude/worktrees/\nbuild/.scratch/\n",
    )
    write(root, ".claude/worktrees/example/test_hidden.py", "")
    write(root, "build/.scratch/test_hidden.py", "")
    assert RUNNER.check(root, registry_data(root)) == []


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_check_finds_untracked_new_suite(tmp_path):
    root = git_root(tmp_path)
    write(root, "skills/brainstorming/scripts/test_new.py", "")
    findings = RUNNER.check(root, registry_data(root))
    assert any("skills/brainstorming/scripts" in line for line in findings)


# spec: "If git fails, `--check` fails."
# task: 4
def test_check_fails_when_git_file_listing_fails(tmp_path):
    root = tmp_path / "not-a-git-repo"
    root.mkdir()
    write(root, "build/suites.toml", SINGLE)
    write(root, "build/test_build.py", "")
    assert status(["--check"], root) == 1


# spec: "R4.3 Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_success_and_finding_output(tmp_path, capsys):
    root = git_root(tmp_path)
    assert status(["--check"], root) == 0
    assert all_output(capsys).strip() == "suite registry ok"

    write(root, "skills/brainstorming/scripts/test_new.py", "")
    assert status(["--check"], root) == 1
    lines = [line for line in all_output(capsys).splitlines() if line.strip()]
    assert len(lines) == 1
    assert "skills/brainstorming/scripts" in lines[0]


# spec: "the real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_passes_check(capsys):
    assert status(["--check"], ROOT) == 0
    assert all_output(capsys).strip() == "suite registry ok"


# spec: "R4.4 `build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_commit_lint_script_runs_registry_check_ninth():
    script = (ROOT / "build/run_commit_lints.sh").read_text()
    runs = re.findall(r"(?m)^run\s+(\S+)\s+(.+)$", script)
    assert len(runs) == 9
    assert runs[-1] == (
        "suite_registry",
        "uv run --python 3.13 python build/run_suites.py --check",
    )
    assert "nine" in script.splitlines()[0].lower() or any(
        "nine" in line.lower() for line in script.splitlines()[:5]
    )


# spec: "It does not call the runner, except for the new `--check` lint (R4)."
# task: 6
def test_commit_lint_script_has_no_other_runner_invocation():
    script = (ROOT / "build/run_commit_lints.sh").read_text()
    runner_lines = [
        line for line in script.splitlines() if "run_suites.py" in line
    ]
    assert runner_lines == [
        "run suite_registry uv run --python 3.13 python build/run_suites.py --check"
    ]


# spec: "R6.2 `build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_regression_test_is_present():
    source = (ROOT / "build/test_commit_lints.py").read_text()
    tree = ast.parse(source)
    assert "suite_registry" in source
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_unregistered_suite_is_refused"
    )
    body = ast.get_source_segment(source, function)
    assert "test_new.py" in body
    assert "suite_registry" in body
    assert "commit" in body


# spec: "The root `CLAUDE.md` then replaces its per-suite commands with a short block that points at the runner."
# task: 7
def test_root_commands_block_points_at_the_runner():
    text = (ROOT / "CLAUDE.md").read_text()
    commands = [
        "build/run_suites.py --list",
        "build/run_suites.py <name>",
        "build/run_suites.py --all",
        "build/run_suites.py --check",
    ]
    positions = [text.index(command) for command in commands]
    assert positions == sorted(positions)
    assert "[--extras]" in text
    assert "[-- <pytest args>]" in text


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_selection_and_tool_commands_remain_in_root_claude_md():
    text = (ROOT / "CLAUDE.md").read_text()
    for token in (
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
        assert token in text
    assert sum(
        "build.py" in line and not line.lstrip().startswith("#")
        for line in text.splitlines()
    ) >= 2


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_intro_keeps_the_required_guidance():
    text = (ROOT / "CLAUDE.md").read_text()
    line = next(
        line
        for line in text.splitlines()
        if "build/suites.toml" in line and "build/run_suites.py" in line
    )
    for token in ("uv", "3.13", "director", "test_build.py", "notes"):
        assert token in line.lower() if token == "director" else token in line
    assert "There is no root test runner" not in text


# spec: "CLAUDE.md has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_claude_md_has_no_directory_suite_commands():
    text = (ROOT / "CLAUDE.md").read_text()
    rows = tomllib.loads((ROOT / "build/suites.toml").read_text())["suite"]
    assert len(text.splitlines()) < 200
    for row in rows:
        pattern = rf"(?m)^\s*cd\s+{re.escape(row['dir'])}\s*&&\s*uv run"
        assert re.search(pattern, text) is None


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_root_claude_md_does_not_claim_a_suite_or_test_count():
    text = (ROOT / "CLAUDE.md").read_text()
    assert re.search(r"\b\d+\s+(?:suites|tests)\b", text, re.I) is None


# spec: "The comment names the suite `run_suites.py cc-guide` instead of "its suite"."
# task: 7
def test_cc_guide_comment_names_the_suite():
    text = (ROOT / "CLAUDE.md").read_text()
    assert "run_suites.py cc-guide" in text


# spec: "R5.3 `build/CLAUDE.md`: "the eight commit lints" becomes "the nine commit lints", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_claude_md_describes_ninth_lint_and_registry():
    text = (ROOT / "build/CLAUDE.md").read_text()
    assert "the nine commit lints" in text
    assert "suites.toml" in text
    assert "run_suites.py" in text
    assert "--check" in text


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_uses_versioned_stamp():
    root_text = (ROOT / "CLAUDE.md").read_text()
    assert re.fullmatch(
        r"<!-- cc-guide: .+ @\S+ -->", root_text.splitlines()[0]
    )

    source = (ROOT / "build/test_check_conformance.py").read_text()
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    body = ast.get_source_segment(source, function)
    assert "@needs_pilot" not in body
    assert "cc-guide:" in body
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>cc_guide</plan></flag>
<flag task="5"><spec>`cc-guide` | `build/cc_guide` | — | — | default</spec><plan>cc_guide</plan></flag>
</flags>
<untestable>
Design approved in brainstorming on 2026-10-18.
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
This work lands whole, registry and CLAUDE.md shrink, ahead of plan 52's Task 6.
Task 6 then adds one build/suites.toml entry instead of editing Commands.
Plan 52's planning session amends its plan to match and records Q4 as (c).
Rejected: a Python list inside the runner (every suite change becomes a code edit), and one manifest per suite directory (`install.py` copies skill directories, so the manifests would ship with installed skills).
An `@`-imported document was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
Design section 1 (the registry keys and the runner's behaviour) was approved as presented.
Design section 2 (the guard, the file edits, the tests and the couplings) was approved as presented.
Every command, dependency and note survives; the only change is the form.
With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character.
On `main` at `456e3fb` there are 18: the 17 in `CLAUDE.md` lines 66–125, and `build/cc_guide`, whose command is line 145.
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
Until plan 52 adds the entry, the ninth lint refuses its new suite directory.
If plan 52 lands first after all, R5.2's deletion still works, and this plan registers that suite itself.
None of the lines that R5.1 deletes carries one of its edit anchors.
Its Task 7 edits line 133, which stays.
Its own suite commands are written out in full in the plan, so they work without `CLAUDE.md`.
It edits one sentence of `build/CLAUDE.md`'s `cc_guide/` paragraph.
R5.3 edits the `run_commit_lints.sh` paragraph and adds a sentence.
If an edit block does not match, merge by hand.
R6's tests run red first, then green.
Run it before the `CLAUDE.md` deletion.
It extracts every `cd <dir> && uv run …` command from lines 66–125 and 145, splitting the hooks `&&` chain into one command per run.
It asserts that the set equals the set of default shell forms that `--list` prints: nothing is missing on either side.
It also checks each comment's skip-unlocking deps against that suite's `extras`.
Run `hooks`, `build` and `bayesian-workflow` once directly and once through the runner, in the same checkout.
Their pytest summary lines match.
Then run `--all` once, and record each run's result beside the direct result.
`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`.
The Stage 2 audit passes, and the behaviour runs match.
The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
</untestable>