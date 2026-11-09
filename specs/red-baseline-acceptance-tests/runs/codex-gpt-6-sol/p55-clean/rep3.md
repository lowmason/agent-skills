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

ROOT = Path(__file__).resolve().parents[1]

FIXTURE = """
[[suite]]
name = "alpha"
dir = "skills/alpha/scripts"
with = ["pytest", "numpy"]
extras = ["hypothesis"]
pythons = ["3.13", "/usr/bin/python3"]
notes = ["alpha note", "second note"]

[[suite]]
name = "build"
dir = "build"
with = ["pytest"]

[[suite]]
name = "cc-guide"
dir = "build/cc_guide"
with = ["pytest"]
"""

COVERED = """
[[suite]]
name = "covered"
dir = "covered"
with = ["pytest"]
"""

EXPECTED = {
    "bayesian-workflow": ("skills/bayesian-workflow/scripts", ["pytest", "arviz", "arviz-stats", "numpy", "xarray"], ["matplotlib"], ["3.13"]),
    "brainstorming": ("skills/brainstorming/scripts", ["pytest"], [], ["3.13"]),
    "build": ("build", ["pytest", "numpy", "polars", "pyyaml"], ["arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots", "numpyro", "jax", "matplotlib"], ["3.13"]),
    "cc-guide": ("build/cc_guide", ["pytest"], [], ["3.13"]),
    "classification-codes": ("skills/classification-codes/scripts", ["pytest", "polars"], [], ["3.13"]),
    "describe-critique-methodology": ("skills/describe-critique-methodology/scripts", ["pytest"], [], ["3.13"]),
    "design-architecture": ("skills/design-architecture/scripts", ["pytest"], [], ["3.13"]),
    "explore-data": ("skills/explore-data/scripts", ["pytest", "polars"], [], ["3.13"]),
    "geographic-codes": ("skills/geographic-codes/scripts", ["pytest", "polars", "fastexcel"], [], ["3.13"]),
    "hooks": ("hooks", ["pytest"], [], ["3.13", "/usr/bin/python3"]),
    "llm-wiki": ("skills/llm-wiki/scripts", ["pytest"], [], ["3.13"]),
    "recommend-probabilistic-model": ("skills/recommend-probabilistic-model/scripts", ["pytest", "numpy", "polars"], [], ["3.13"]),
    "recommend-visualization": ("skills/recommend-visualization/scripts", ["pytest", "numpy", "polars"], [], ["3.13"]),
    "subagent-driven-development": ("skills/subagent-driven-development/scripts", ["pytest"], [], ["3.13"]),
    "systematic-debugging": ("skills/systematic-debugging", ["pytest"], [], ["3.13"]),
    "track-model-experiments": ("skills/track-model-experiments/scripts", ["pytest", "numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"], [], ["3.13"]),
    "tune-hyperparameters": ("skills/tune-hyperparameters/scripts", ["pytest", "numpy", "polars"], ["scikit-learn", "optuna"], ["3.13"]),
    "writing-plans": ("skills/writing-plans/scripts", ["pytest"], [], ["3.13"]),
}


def _runner():
    module_name = "_suite_registry_acceptance_runner"
    if module_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            module_name, ROOT / "build/run_suites.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return sys.modules[module_name]


def _write_registry(root, text=FIXTURE, make_dirs=True):
    path = root / "build/suites.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if make_dirs:
        for row in tomllib.loads(text)["suite"]:
            (root / row["dir"]).mkdir(parents=True, exist_ok=True)
    return root


def _git_init(root):
    subprocess.run(
        ["git", "init", "-q", str(root)],
        check=True,
        capture_output=True,
        text=True,
    )


def _covered_repo(root):
    _write_registry(root, COVERED)
    (root / "covered/test_existing.py").write_text("")
    _git_init(root)
    return root


def _expected_command(directory, deps, python):
    words = ["uv", "run", "--python", python]
    for dep in deps:
        words.extend(["--with", dep])
    words.extend(["python", "-m", "pytest", "-q"])
    return f"cd {directory} && {' '.join(words)}"


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 2
def test_model_parses_required_and_default_fields():
    runner = _runner()
    suites = runner.parse(tomllib.loads(COVERED))
    assert len(suites) == 1
    suite = suites[0]
    assert suite.name == "covered"
    assert suite.dir == "covered"
    assert suite.deps == ("pytest",)
    assert suite.extras == ()
    assert suite.pythons == ("3.13",)
    assert suite.notes == ()


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
def test_validation_rejects_every_listed_registry_fault():
    runner = _runner()
    base = {"suite": [{"name": "alpha", "dir": "alpha", "with": ["pytest"]}]}
    invalid = []

    for key in ("name", "dir", "with"):
        case = copy.deepcopy(base)
        del case["suite"][0][key]
        invalid.append(case)

    for key, value in (
        ("name", 12),
        ("dir", 12),
        ("with", "pytest"),
        ("with", ["pytest", 12]),
        ("extras", "numpy"),
        ("extras", [12]),
        ("pythons", "3.13"),
        ("pythons", [12]),
        ("notes", "note"),
        ("notes", [12]),
    ):
        case = copy.deepcopy(base)
        case["suite"][0][key] = value
        invalid.append(case)

    case = copy.deepcopy(base)
    case["suite"][0]["misspelled"] = True
    invalid.append(case)

    case = copy.deepcopy(base)
    case["unexpected"] = True
    invalid.append(case)

    case = copy.deepcopy(base)
    case["suite"][0]["with"] = ["numpy"]
    invalid.append(case)

    case = copy.deepcopy(base)
    case["suite"].append({"name": "alpha", "dir": "other", "with": ["pytest"]})
    invalid.append(case)

    case = copy.deepcopy(base)
    case["suite"].append({"name": "other", "dir": "alpha", "with": ["pytest"]})
    invalid.append(case)

    assert runner.validate(base) == []
    for case in invalid:
        assert runner.validate(case), case


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_run_argv_and_label():
    runner = _runner()
    suite = runner.Suite("alpha", "skills/alpha/scripts", ("pytest", "numpy"))
    run = runner.runs(suite)[0]
    assert run.argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy",
        "python", "-m", "pytest", "-q",
    )
    assert run.label == "alpha (3.13)"
    assert run.shell() == (
        "cd skills/alpha/scripts && uv run --python 3.13 "
        "--with pytest --with numpy python -m pytest -q"
    )


# spec: "One run is one interpreter of one suite."
# task: 2
def test_one_run_per_interpreter_in_order():
    runner = _runner()
    suite = runner.Suite(
        "hooks", "hooks", ("pytest",),
        pythons=("3.13", "/usr/bin/python3"),
    )
    runs = runner.runs(suite)
    assert [run.python for run in runs] == ["3.13", "/usr/bin/python3"]
    assert [run.label for run in runs] == [
        "hooks (3.13)", "hooks (/usr/bin/python3)"
    ]


# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_follow_default_dependencies():
    runner = _runner()
    suite = runner.Suite(
        "alpha", "alpha", ("pytest", "numpy"),
        extras=("matplotlib", "scikit-learn"),
    )
    assert runner.runs(suite)[0].argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy",
        "python", "-m", "pytest", "-q",
    )
    assert runner.runs(suite, extras=True)[0].argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy",
        "--with", "matplotlib", "--with", "scikit-learn",
        "python", "-m", "pytest", "-q",
    )


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_pytest_arguments():
    runner = _runner()
    suite = runner.Suite("alpha", "alpha", ("pytest",))
    run = runner.runs(
        suite, pytest_args=("-k", "slow or fast", "test file.py::case")
    )[0]
    assert run.shell().startswith("cd alpha && ")
    assert shlex.split(run.shell().split(" && ", 1)[1]) == list(run.argv)
    assert run.argv[-3:] == ("-k", "slow or fast", "test file.py::case")


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_uses_directory_boundaries():
    runner = _runner()
    outer = runner.Suite("build", "build", ("pytest",))
    nested = runner.Suite("cc-guide", "build/cc_guide", ("pytest",))
    sibling = runner.Suite("building", "building", ("pytest",))
    assert runner.container(nested, [outer, nested, sibling]) == outer
    assert runner.container(sibling, [outer, nested, sibling]) is None


# spec: "- **coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_pytest_file_patterns_include_both_default_forms(tmp_path):
    runner = _runner()
    root = _covered_repo(tmp_path)
    (root / "first").mkdir()
    (root / "first/test_one.py").write_text("")
    (root / "second").mkdir()
    (root / "second/two_test.py").write_text("")
    (root / "third").mkdir()
    (root / "third/helper.py").write_text("")
    found = runner.pytest_dirs(root)
    assert {"covered", "first", "second"} <= found
    assert "third" not in found


# spec: "- **coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_check_reports_unregistered_test_directory(tmp_path):
    runner = _runner()
    root = _covered_repo(tmp_path)
    (root / "new_suite").mkdir()
    (root / "new_suite/test_new.py").write_text("")
    findings = runner.check(root, tomllib.loads(COVERED))
    assert (
        "new_suite: holds pytest files, but no suite in "
        "build/suites.toml contains it"
    ) in findings


# spec: "- **registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_reports_missing_registered_directory(tmp_path):
    runner = _runner()
    root = _write_registry(tmp_path, COVERED, make_dirs=False)
    _git_init(root)
    findings = runner.check(root, tomllib.loads(COVERED))
    assert any(
        line.startswith("build/suites.toml: ") and "covered" in line
        for line in findings
    )


# spec: "- **registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_reports_registered_directory_without_tests(tmp_path):
    runner = _runner()
    root = _write_registry(tmp_path, COVERED)
    (root / "covered/helper.py").write_text("")
    _git_init(root)
    findings = runner.check(root, tomllib.loads(COVERED))
    assert any(
        line.startswith("build/suites.toml: ") and "covered" in line
        for line in findings
    )


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_check_ignores_git_excluded_test_directories(tmp_path):
    runner = _runner()
    root = _covered_repo(tmp_path)
    (root / ".gitignore").write_text(
        "ignored/\n.claude/worktrees/\nbuild/.scratch/\n"
    )
    for directory in (
        root / "ignored",
        root / ".claude/worktrees/example",
        root / "build/.scratch/example",
    ):
        directory.mkdir(parents=True)
        (directory / "test_hidden.py").write_text("")
    assert runner.check(root, tomllib.loads(COVERED)) == []


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_check_counts_untracked_test_directory(tmp_path):
    runner = _runner()
    root = _covered_repo(tmp_path)
    (root / "draft").mkdir()
    (root / "draft/test_new.py").write_text("")
    assert "draft" not in subprocess.run(
        ["git", "-C", str(root), "ls-files"],
        check=True, capture_output=True, text=True,
    ).stdout
    assert any(
        line.startswith("draft: holds pytest files")
        for line in runner.check(root, tomllib.loads(COVERED))
    )


# spec: "If git fails, `--check` fails."
# task: 3
def test_check_fails_when_git_file_listing_fails(tmp_path, capsys):
    runner = _runner()
    root = _write_registry(tmp_path, COVERED)
    (root / "covered/test_existing.py").write_text("")
    assert runner.main(["--check"], root=root) == 1
    assert capsys.readouterr().out != "suite registry ok\n"


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 3
def test_check_output_and_status(tmp_path, capsys):
    runner = _runner()
    root = _covered_repo(tmp_path)
    assert runner.main(["--check"], root=root) == 0
    assert capsys.readouterr().out == "suite registry ok\n"
    (root / "new_suite").mkdir()
    (root / "new_suite/test_new.py").write_text("")
    assert runner.main(["--check"], root=root) == 1
    lines = capsys.readouterr().out.splitlines()
    assert lines == [
        "new_suite: holds pytest files, but no suite in "
        "build/suites.toml contains it"
    ]


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
def test_check_reports_validation_fault_as_registry_finding(tmp_path, capsys):
    runner = _runner()
    invalid = COVERED.replace(
        'name = "covered"', 'name = "covered"\nmisspelled = true'
    )
    root = _write_registry(tmp_path, invalid)
    (root / "covered/test_existing.py").write_text("")
    _git_init(root)
    assert runner.main(["--check"], root=root) == 1
    assert "build/suites.toml: " in capsys.readouterr().out


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_defaults_to_all_suites_and_shows_details(tmp_path, capsys):
    runner = _runner()
    root = _write_registry(tmp_path)
    assert runner.main(["--list"], root=root) == 0
    output = capsys.readouterr().out
    for name, directory in (
        ("alpha", "skills/alpha/scripts"),
        ("build", "build"),
        ("cc-guide", "build/cc_guide"),
    ):
        assert name in output
        assert directory in output
    assert "alpha note" in output
    assert "second note" in output
    assert "hypothesis" in output
    assert _expected_command(
        "skills/alpha/scripts", ["pytest", "numpy"], "3.13"
    ) in output
    assert _expected_command(
        "skills/alpha/scripts", ["pytest", "numpy"], "/usr/bin/python3"
    ) in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_shows_extras_and_forwarded_arguments(tmp_path, capsys):
    runner = _runner()
    root = _write_registry(tmp_path)
    assert runner.main(
        ["--list", "alpha", "--extras", "--", "-k", "slow or fast"],
        root=root,
    ) == 0
    output = capsys.readouterr().out
    expected = runner.runs(
        runner.parse(tomllib.loads(FIXTURE))[0],
        extras=True,
        pytest_args=("-k", "slow or fast"),
    )
    assert all(run.shell() in output for run in expected)
    assert "cc-guide" not in output


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_runs_follow_name_and_interpreter_order(tmp_path):
    runner = _runner()
    root = _write_registry(tmp_path)
    seen = []

    def run_one(run_root, run):
        seen.append((run_root, run.label))
        return 0

    assert runner.main(
        ["build", "alpha"], root=root, run_one=run_one
    ) == 0
    assert seen == [
        (root, "build (3.13)"),
        (root, "alpha (3.13)"),
        (root, "alpha (/usr/bin/python3)"),
    ]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_notes_print_once_after_first_header(tmp_path, capsys):
    runner = _runner()
    root = _write_registry(tmp_path)

    def run_one(_root, run):
        print(f"pytest output for {run.label}")
        return 0

    assert runner.main(["alpha"], root=root, run_one=run_one) == 0
    output = capsys.readouterr().out
    first = output.index("== alpha (3.13)")
    note = output.index("note: alpha note")
    streamed = output.index("pytest output for alpha (3.13)")
    second = output.index("== alpha (/usr/bin/python3)")
    assert first < note < streamed < second
    assert output.count("note: alpha note") == 1
    assert output.count("note: second note") == 1


# spec: "A failed run does not stop the next one."
# task: 4
def test_failure_does_not_stop_later_runs(tmp_path, capsys):
    runner = _runner()
    root = _write_registry(tmp_path)
    seen = []

    def run_one(_root, run):
        seen.append(run.label)
        return 5 if len(seen) == 1 else 0

    assert runner.main(
        ["alpha", "build"], root=root, run_one=run_one
    ) == 1
    assert seen == [
        "alpha (3.13)",
        "alpha (/usr/bin/python3)",
        "build (3.13)",
    ]
    assert "alpha (3.13)" in capsys.readouterr().err


# spec: "0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_run_exit_status_and_final_line(tmp_path, capsys):
    runner = _runner()
    root = _write_registry(tmp_path)
    assert runner.main(
        ["build"], root=root, run_one=lambda _root, _run: 0
    ) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "suite runs passed"
    assert runner.main(
        ["build"], root=root, run_one=lambda _root, _run: 5
    ) == 1
    assert "build (3.13)" in capsys.readouterr().err.splitlines()[-1]


# spec: "0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_usage_error_and_unknown_name_exit_two(tmp_path):
    runner = _runner()
    root = _write_registry(tmp_path)
    assert runner.main([], root=root) == 2
    assert runner.main(["unknown"], root=root) == 2
    assert runner.main(["--list", "unknown"], root=root) == 2


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_invalid_registry_stops_every_noncheck_mode(tmp_path):
    runner = _runner()
    invalid = FIXTURE.replace(
        'name = "alpha"', 'name = "alpha"\nmisspelled = true'
    )
    root = _write_registry(tmp_path, invalid)
    for argv in (["--list"], ["alpha"], ["--all"]):
        assert runner.main(
            argv, root=root, run_one=lambda _root, _run: 0
        ) == 2


# spec: "`--all` prints one line for each suite that it skips."
# task: 4
def test_all_skips_nested_suite_once(tmp_path, capsys):
    runner = _runner()
    root = _write_registry(tmp_path)
    seen = []

    def run_one(_root, run):
        seen.append(run.label)
        return 0

    assert runner.main(["--all"], root=root, run_one=run_one) == 0
    assert seen == [
        "alpha (3.13)",
        "alpha (/usr/bin/python3)",
        "build (3.13)",
    ]
    output = capsys.readouterr().out
    assert output.count("skip cc-guide:") == 1
    assert "build/cc_guide" in output


# spec: "A suite named on the command line always runs."
# task: 4
def test_named_nested_suite_runs(tmp_path):
    runner = _runner()
    root = _write_registry(tmp_path)
    seen = []

    def run_one(_root, run):
        seen.append(run.label)
        return 0

    assert runner.main(
        ["cc-guide"], root=root, run_one=run_one
    ) == 0
    assert seen == ["cc-guide (3.13)"]


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_pytest_arguments_reach_every_run(tmp_path):
    runner = _runner()
    root = _write_registry(tmp_path)
    seen = []

    def run_one(_root, run):
        seen.append(run.argv[-4:])
        return 0

    assert runner.main(
        ["alpha", "--", "test_one.py::case", "-k", "fast", "-rs"],
        root=root,
        run_one=run_one,
    ) == 0
    assert seen == [
        ("test_one.py::case", "-k", "fast", "-rs"),
        ("test_one.py::case", "-k", "fast", "-rs"),
    ]


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_inherits_environment_and_uses_suite_directory(
    tmp_path, monkeypatch
):
    runner = _runner()
    root = tmp_path
    (root / "alpha").mkdir()
    bin_dir = root / "bin"
    bin_dir.mkdir()
    capture = root / "capture.json"
    fake_uv = bin_dir / "uv"
    fake_uv.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, pathlib, sys\n"
        "pathlib.Path(os.environ['CAPTURE_PATH']).write_text(json.dumps({"
        "'argv': sys.argv[1:], 'cwd': os.getcwd(), "
        "'sweep': os.environ.get('CALIBRATION_SWEEP'), "
        "'marker': os.environ.get('ACCEPTANCE_MARKER')}))\n"
    )
    fake_uv.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("CAPTURE_PATH", str(capture))
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("ACCEPTANCE_MARKER", "retained")
    run = runner.runs(
        runner.Suite("alpha", "alpha", ("pytest",)),
        pytest_args=("-s",),
    )[0]
    assert runner.run_subprocess(root, run) == 0
    result = json.loads(capture.read_text())
    assert result["cwd"] == str(root / "alpha")
    assert result["sweep"] == "1"
    assert result["marker"] == "retained"
    assert result["argv"] == list(run.argv[1:])


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_is_a_failed_run(tmp_path, monkeypatch):
    runner = _runner()
    (tmp_path / "alpha").mkdir()
    monkeypatch.setenv("PATH", str(tmp_path / "empty_bin"))
    run = runner.runs(runner.Suite("alpha", "alpha", ("pytest",)))[0]
    assert runner.run_subprocess(tmp_path, run) != 0


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_runner_finds_registry_when_launched_elsewhere(tmp_path):
    runner = _runner()
    assert runner.REPO == ROOT
    result = subprocess.run(
        [sys.executable, str(ROOT / "build/run_suites.py"), "--list", "build"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "cd build && " in result.stdout


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 4
def test_runner_imports_only_standard_library_modules():
    tree = ast.parse((ROOT / "build/run_suites.py").read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".", 1)[0])
    assert imported <= sys.stdlib_module_names


# spec: "The registry holds every **directory suite**: a directory where pytest runs as a whole, with no selection argument."
# task: 5
def test_real_registry_contains_the_spec_inventory():
    rows = tomllib.loads((ROOT / "build/suites.toml").read_text())["suite"]
    by_name = {row["name"]: row for row in rows}
    assert set(EXPECTED) <= set(by_name)
    assert len(rows) == len(by_name)
    assert [row["name"] for row in rows] == sorted(by_name)
    for name, (directory, deps, extras, pythons) in EXPECTED.items():
        row = by_name[name]
        assert row["dir"] == directory
        assert row["with"] == deps
        assert row.get("extras", []) == extras
        assert row.get("pythons", ["3.13"]) == pythons
        assert isinstance(row.get("notes", []), list)


# spec: "The notes carry the rest of each comment."
# task: 5
def test_registry_retains_named_operational_notes():
    rows = tomllib.loads((ROOT / "build/suites.toml").read_text())["suite"]
    notes = {
        row["name"]: "\n".join(row.get("notes", []))
        for row in rows
    }
    expected_fragments = {
        "bayesian-workflow": ("CALIBRATION_SWEEP=1", "arviz"),
        "brainstorming": ("node",),
        "build": ("build/.scratch/",),
        "hooks": ("3.9", "launchd", "Gate B"),
        "llm-wiki": ("@needs_pilot", "LLM_WIKI_ROOT"),
        "track-model-experiments": ("run",),
        "tune-hyperparameters": ("--with sklearn",),
    }
    for name, fragments in expected_fragments.items():
        for fragment in fragments:
            assert fragment.lower() in notes[name].lower(), (name, fragment)


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_explains_its_contract():
    header = (ROOT / "build/suites.toml").read_text().split("[[suite]]", 1)[0]
    assert header.strip()
    assert all(
        key in header for key in ("name", "dir", "with", "extras", "pythons", "notes")
    )
    lower = header.lower()
    assert "sort" in lower
    assert "commit lint" in lower
    assert any(word in lower for word in ("ninth", "nine", "9th"))


# spec: "With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character."
# task: 5
def test_all_inventory_default_shell_forms():
    runner = _runner()
    suites = {
        suite.name: suite
        for suite in runner.parse(
            tomllib.loads((ROOT / "build/suites.toml").read_text())
        )
    }
    for name, (directory, deps, _extras, pythons) in EXPECTED.items():
        assert [run.shell() for run in runner.runs(suites[name])] == [
            _expected_command(directory, deps, python) for python in pythons
        ]


# spec: "- the real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_passes_coverage_check(capsys):
    runner = _runner()
    assert runner.main(["--check"], root=ROOT) == 0
    assert capsys.readouterr().out == "suite registry ok\n"


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_ninth_lint_has_the_required_command():
    text = (ROOT / "build/run_commit_lints.sh").read_text()
    lines = text.splitlines()
    runs = [
        line.strip() for line in lines
        if re.match(r"^\s*run\s+\S+", line)
    ]
    required = (
        "run suite_registry uv run --python 3.13 "
        "python build/run_suites.py --check"
    )
    assert len(runs) == 9
    assert runs[-1] == required
    assert [line for line in lines if "run_suites.py" in line] == [required]
    assert "nine" in "\n".join(lines[:12]).lower()


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_tests_register_the_new_check():
    text = (ROOT / "build/test_commit_lints.py").read_text()
    tree = ast.parse(text)
    checks = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and any(
            isinstance(target, ast.Name) and target.id == "CHECKS"
            for target in (
                node.targets if isinstance(node, ast.Assign) else [node.target]
            )
        )
    ]
    assert checks
    assert "suite_registry" in ast.get_source_segment(text, checks[0])
    assert any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "test_unregistered_suite_is_refused"
        for node in ast.walk(tree)
    )


# spec: "`build/CLAUDE.md`: "the eight commit lints" becomes "the nine commit lints", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_guide_describes_ninth_lint_and_registry():
    text = (ROOT / "build/CLAUDE.md").read_text()
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    assert "suites.toml" in text
    assert "run_suites.py" in text
    assert "--check" in text


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_guide_intro_preserves_rules_and_names_runner():
    lines = (ROOT / "CLAUDE.md").read_text().splitlines()
    intro = [
        line for line in lines
        if "build/suites.toml" in line and "build/run_suites.py" in line
    ]
    assert len(intro) == 1
    assert "uv" in intro[0]
    assert "3.13" in intro[0]
    assert "director" in intro[0].lower()
    assert "test_build.py" in intro[0]
    assert any(word in intro[0].lower() for word in ("basename", "collision"))
    assert "notes" in intro[0].lower()
    assert "There is no root test runner" not in "\n".join(lines)


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_guide_lists_the_four_runner_forms():
    text = (ROOT / "CLAUDE.md").read_text()
    for form in (
        "python build/run_suites.py --list",
        "python build/run_suites.py <name> [--extras] [-- <pytest args>]",
        "python build/run_suites.py --all",
        "python build/run_suites.py --check",
    ):
        assert form in text


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_root_guide_keeps_selected_tests_and_tools():
    text = (ROOT / "CLAUDE.md").read_text()
    for fragment in (
        "test_runtime_support.py",
        "test_commit_lints.py",
        "-k declared_dependencies",
        "-k test_real_skill",
        "test_check_jax_examples.py",
        "Single test",
        "run_commit_lints.sh",
        "verify_citations.py",
        "extract_structure.py",
        "cli.py lint",
        "cli.py check",
    ):
        assert fragment in text
    assert sum("build.py" in line for line in text.splitlines()) >= 2
    assert "snippet" in text.lower()
    assert "smoke" in text.lower()


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_guide_has_no_directory_suite_command_and_is_under_limit():
    text = (ROOT / "CLAUDE.md").read_text()
    assert len(text.splitlines()) < 200
    suite_dirs = {row[0] for row in EXPECTED.values()}
    for line in text.splitlines():
        stripped = line.strip()
        for directory in suite_dirs - {"build"}:
            assert not (
                stripped.startswith(f"cd {directory} &&")
                and "python -m pytest -q" in stripped
            ), stripped
        assert not re.fullmatch(
            r"cd build && .*python -m pytest -q", stripped
        ), stripped


# spec: "The comment names the suite `run_suites.py cc-guide` instead of "its suite"."
# task: 7
def test_cc_guide_comment_names_the_runner_suite():
    lines = (ROOT / "CLAUDE.md").read_text().splitlines()
    assert any(
        "run_suites.py cc-guide" in line and line.lstrip().startswith("#")
        for line in lines
    )


# spec: "The commit-lint comment names the suite-registry check and says "nine"."
# task: 7
def test_root_commit_lint_comment_names_ninth_check():
    lines = (ROOT / "CLAUDE.md").read_text().splitlines()
    comments = "\n".join(
        line for line in lines if line.lstrip().startswith("#")
    ).lower()
    assert "nine" in comments
    assert "suite" in comments and "registry" in comments


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_uses_stamp():
    text = (ROOT / "build/test_check_conformance.py").read_text()
    tree = ast.parse(text)
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    source = ast.get_source_segment(text, function)
    assert "@needs_pilot" not in source
    assert "cc-guide" in source
    assert "@" in source
    assert re.fullmatch(
        r"<!-- cc-guide: .* @\S+ -->",
        (ROOT / "CLAUDE.md").read_text().splitlines()[0],
    )


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_root_guide_has_no_numeric_suite_or_test_count_claim():
    text = (ROOT / "CLAUDE.md").read_text()
    assert not re.search(r"\b\d+\s+(?:directory\s+)?(?:suites|tests)\b", text, re.I)


# spec: "`build/test_run_suites.py`, stdlib and pytest only, which the build suite collects."
# task: 2
def test_project_runner_tests_are_collectable_and_use_allowed_imports():
    path = ROOT / "build/test_run_suites.py"
    assert path.is_file()
    tree = ast.parse(path.read_text())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    assert imports <= sys.stdlib_module_names | {
        "pytest", "run_suites", "build"
    }


# spec: "`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`."
# task: 6
def test_runner_and_its_tests_are_in_head_commit():
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    committed = set(result.stdout.splitlines())
    assert {"build/run_suites.py", "build/test_run_suites.py"} <= committed


# spec: "`bash build/run_commit_lints.sh` prints `commit lints passed`."
# task: 6
def test_commit_lint_gate_passes():
    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "commit lints passed" in result.stdout + result.stderr
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>cc_guide</plan></flag>
<flag task="5"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>cc_guide</plan></flag>
</flags>
<untestable>
On `main` at `456e3fb` there are 18: the 17 in `CLAUDE.md` lines 66–125, and `build/cc_guide`, whose command is line 145.
Every command, dependency and note survives; the only change is the form.
No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
Write each test before its code and see it fail first (red, then green).
Run it before the `CLAUDE.md` deletion.
It extracts every `cd <dir> && uv run …` command from lines 66–125 and 145, splitting the hooks `&&` chain into one command per run.
It asserts that the set equals the set of default shell forms that `--list` prints: nothing is missing on either side.
It also checks each comment's skip-unlocking deps against that suite's `extras`.
Run `hooks`, `build` and `bayesian-workflow` once directly and once through the runner, in the same checkout.
Their pytest summary lines match.
Then run `--all` once, and record each run's result beside the direct result.
The build suite passes (where the missing `build/.scratch/` lets it).
A note in the session group's shared notes folder gives the exact entry.
Plan 52's planning session amends its plan to match and records Q4 as (c).
Its `CLAUDE.md:sources` and `CLAUDE.md:bullet` edits are outside the Commands block and still apply.
None of the lines that R5.1 deletes carries one of its edit anchors.
Its own suite commands are written out in full in the plan, so they work without `CLAUDE.md`.
It edits one sentence of `build/CLAUDE.md`'s `cc_guide/` paragraph.
If an edit block does not match, merge by hand.
The Stage 2 audit passes, and the behaviour runs match.
The shared note for plan 52 (R7.1) is written.
</untestable>