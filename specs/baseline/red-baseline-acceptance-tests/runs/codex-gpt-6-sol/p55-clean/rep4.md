<tests>
import ast
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tomllib

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "build/run_suites.py"
REGISTRY_PATH = ROOT / "build/suites.toml"

module_spec = importlib.util.spec_from_file_location("run_suites", RUNNER_PATH)
runner = importlib.util.module_from_spec(module_spec)
sys.modules[module_spec.name] = runner
module_spec.loader.exec_module(runner)

ONE_TEXT = """\
[[suite]]
name = "alpha"
dir = "skills/alpha/scripts"
with = ["pytest"]
"""

FIXTURE_TEXT = """\
[[suite]]
name = "alpha"
dir = "skills/alpha/scripts"
with = ["pytest", "numpy"]
extras = ["arviz>=1.0"]
pythons = ["3.13", "/usr/bin/python3"]
notes = ["Alpha needs CALIBRATION_SWEEP=1"]

[[suite]]
name = "build"
dir = "build"
with = ["pytest"]

[[suite]]
name = "cc-guide"
dir = "build/cc_guide"
with = ["pytest"]
"""

EXPECTED = [
    ("bayesian-workflow", "skills/bayesian-workflow/scripts", ["arviz", "arviz-stats", "numpy", "xarray"], ["matplotlib"], ["3.13"]),
    ("brainstorming", "skills/brainstorming/scripts", [], [], ["3.13"]),
    ("build", "build", ["numpy", "polars", "pyyaml"], ["arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots", "numpyro", "jax", "matplotlib"], ["3.13"]),
    ("cc-guide", "build/cc_guide", [], [], ["3.13"]),
    ("classification-codes", "skills/classification-codes/scripts", ["polars"], [], ["3.13"]),
    ("describe-critique-methodology", "skills/describe-critique-methodology/scripts", [], [], ["3.13"]),
    ("design-architecture", "skills/design-architecture/scripts", [], [], ["3.13"]),
    ("explore-data", "skills/explore-data/scripts", ["polars"], [], ["3.13"]),
    ("geographic-codes", "skills/geographic-codes/scripts", ["polars", "fastexcel"], [], ["3.13"]),
    ("hooks", "hooks", [], [], ["3.13", "/usr/bin/python3"]),
    ("llm-wiki", "skills/llm-wiki/scripts", [], [], ["3.13"]),
    ("recommend-probabilistic-model", "skills/recommend-probabilistic-model/scripts", ["numpy", "polars"], [], ["3.13"]),
    ("recommend-visualization", "skills/recommend-visualization/scripts", ["numpy", "polars"], [], ["3.13"]),
    ("subagent-driven-development", "skills/subagent-driven-development/scripts", [], [], ["3.13"]),
    ("systematic-debugging", "skills/systematic-debugging", [], [], ["3.13"]),
    ("track-model-experiments", "skills/track-model-experiments/scripts", ["numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"], [], ["3.13"]),
    ("tune-hyperparameters", "skills/tune-hyperparameters/scripts", ["numpy", "polars"], ["scikit-learn", "optuna"], ["3.13"]),
    ("writing-plans", "skills/writing-plans/scripts", [], [], ["3.13"]),
]


def fixture_root(tmp_path, registry_text=FIXTURE_TEXT):
    root = tmp_path / "repo"
    (root / "build").mkdir(parents=True)
    (root / "build/suites.toml").write_text(registry_text)
    return root


def git_root(tmp_path):
    root = fixture_root(tmp_path, ONE_TEXT)
    test_file = root / "skills/alpha/scripts/test_alpha.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_alpha(): pass\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    return root


def registry_data():
    return tomllib.loads(REGISTRY_PATH.read_text())["suite"]


def capture_runs():
    calls = []

    def run_one(root, run):
        calls.append((root, run))
        return 0

    return calls, run_one


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_and_order():
    text = REGISTRY_PATH.read_text()
    header = text.split("[[suite]]", 1)[0].lower()
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert key in header
    assert "sort" in header
    assert "ninth" in header or "9th" in header
    names = [entry["name"] for entry in registry_data()]
    assert names == sorted(names)


# spec: "On `main` at `456e3fb` there are 18: the 17 in `CLAUDE.md` lines 66–125, and `build/cc_guide`, whose command is line 145."
# task: 5
def test_registry_has_the_specified_eighteen_directory_suites():
    entries = registry_data()
    assert len(entries) == 18
    assert [(entry["name"], entry["dir"]) for entry in entries] == [
        (name, directory) for name, directory, _, _, _ in EXPECTED
    ]


# spec: "Every command, dependency and note survives; the only change is the form."
# task: 5
def test_registry_preserves_dependencies_extras_and_interpreters():
    entries = registry_data()
    for entry, (_, _, deps, extras, pythons) in zip(entries, EXPECTED, strict=True):
        assert entry["with"] == ["pytest", *deps]
        assert entry.get("extras", []) == extras
        assert entry.get("pythons", ["3.13"]) == pythons


# spec: "The notes carry the rest of each comment."
# task: 5
def test_registry_notes_preserve_named_operational_details():
    notes = {
        entry["name"]: " ".join(entry.get("notes", []))
        for entry in registry_data()
    }
    expected_terms = {
        "build": ("build/.scratch/",),
        "bayesian-workflow": ("CALIBRATION_SWEEP=1", "arviz"),
        "llm-wiki": ("@needs_pilot", "LLM_WIKI_ROOT"),
        "brainstorming": ("node",),
        "tune-hyperparameters": ("--with sklearn",),
        "track-model-experiments": ("run",),
        "hooks": ("3.9", "launchd", "Gate B"),
    }
    for name, terms in expected_terms.items():
        for term in terms:
            assert term.lower() in notes[name].lower()


# spec: "**One run** is one interpreter of one suite."
# task: 2
def test_default_interpreter_is_python_313():
    suite = runner.parse(tomllib.loads(ONE_TEXT))[0]
    assert [run.python for run in runner.runs(suite)] == ["3.13"]


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
def test_validation_rejects_each_specified_schema_failure():
    source = tomllib.loads(ONE_TEXT)
    cases = []

    data = copy.deepcopy(source)
    data["suite"][0]["misspelled"] = True
    cases.append(data)

    data = copy.deepcopy(source)
    data["unknown"] = True
    cases.append(data)

    for required in ("name", "dir", "with"):
        data = copy.deepcopy(source)
        del data["suite"][0][required]
        cases.append(data)

    wrong_types = (
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
    )
    for key, value in wrong_types:
        data = copy.deepcopy(source)
        data["suite"][0][key] = value
        cases.append(data)

    data = copy.deepcopy(source)
    data["suite"][0]["with"] = ["numpy"]
    cases.append(data)

    data = copy.deepcopy(source)
    data["suite"].append({"name": "alpha", "dir": "other", "with": ["pytest"]})
    cases.append(data)

    data = copy.deepcopy(source)
    data["suite"].append({
        "name": "other",
        "dir": "skills/alpha/scripts",
        "with": ["pytest"],
    })
    cases.append(data)

    for data in cases:
        assert runner.validate(data), data


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_invalid_registry_stops_every_run_mode_with_exit_two(tmp_path):
    root = fixture_root(tmp_path, ONE_TEXT + "misspelled = true\n")
    calls, run_one = capture_runs()
    for argv in (["--list"], ["alpha"], ["--all"]):
        assert runner.main(argv, root=root, run_one=run_one) == 2
    assert calls == []


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
def test_check_reports_registry_validation_as_a_finding(tmp_path, capsys):
    root = git_root(tmp_path)
    (root / "build/suites.toml").write_text(ONE_TEXT + "misspelled = true\n")
    assert runner.main(["--check"], root=root) == 1
    output = capsys.readouterr().out + capsys.readouterr().err
    assert "misspelled" in output or "unknown" in output


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_run_argv():
    suite = runner.Suite(
        name="alpha",
        dir="skills/alpha/scripts",
        deps=("pytest", "numpy"),
    )
    run = runner.runs(suite)[0]
    assert run.argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy",
        "python", "-m", "pytest", "-q",
    )


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_directory_dependency_and_pytest_argument():
    suite = runner.Suite(
        name="alpha",
        dir="skills/has spaces/scripts",
        deps=("pytest",),
        extras=("arviz>=1.0",),
    )
    run = runner.runs(
        suite,
        extras=True,
        pytest_args=("test case.py::test_example", "-k", "a or b"),
    )[0]
    assert run.shell() == (
        f"cd {shlex.quote(suite.dir)} && "
        + shlex.join(run.argv)
    )


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 2
def test_two_interpreters_produce_two_independent_shell_forms():
    suite = runner.Suite(
        name="hooks",
        dir="hooks",
        deps=("pytest",),
        pythons=("3.13", "/usr/bin/python3"),
    )
    runs = runner.runs(suite)
    assert [run.python for run in runs] == ["3.13", "/usr/bin/python3"]
    assert all(run.shell().startswith("cd hooks && uv run ") for run in runs)
    assert all(run.shell().count("cd hooks &&") == 1 for run in runs)


# spec: "`--extras` adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_follow_default_dependencies():
    suite = runner.Suite(
        name="alpha",
        dir="skills/alpha/scripts",
        deps=("pytest", "numpy"),
        extras=("arviz>=1.0", "matplotlib"),
    )
    run = runner.runs(suite, extras=True)[0]
    assert run.argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy",
        "--with", "arviz>=1.0", "--with", "matplotlib",
        "python", "-m", "pytest", "-q",
    )


# spec: "Today that is `cc-guide`: `cd build && pytest` collects `build/cc_guide` already."
# task: 2
def test_container_uses_directory_ancestry():
    outer = runner.Suite("build", "build", ("pytest",))
    nested = runner.Suite("cc-guide", "build/cc_guide", ("pytest",))
    sibling = runner.Suite("other", "build-tools", ("pytest",))
    assert runner.container(nested, [outer, nested, sibling]) == outer
    assert runner.container(sibling, [outer, nested, sibling]) is None


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_prints_all_fields_and_can_select_a_suite(tmp_path, capsys):
    root = fixture_root(tmp_path)
    assert runner.main(["--list"], root=root) == 0
    all_output = capsys.readouterr().out
    for name in ("alpha", "build", "cc-guide"):
        assert name in all_output
    assert "skills/alpha/scripts" in all_output
    assert "cd skills/alpha/scripts && uv run " in all_output
    assert "arviz>=1.0" in all_output
    assert "CALIBRATION_SWEEP=1" in all_output

    assert runner.main(["--list", "alpha"], root=root) == 0
    selected_output = capsys.readouterr().out
    assert "alpha" in selected_output
    assert "cc-guide" not in selected_output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_command_reflects_extras_and_pytest_arguments(tmp_path, capsys):
    root = fixture_root(tmp_path)
    assert runner.main(
        ["--list", "alpha", "--extras", "--", "-k", "a or b", "-s"],
        root=root,
    ) == 0
    output = capsys.readouterr().out
    suite = runner.parse(tomllib.loads(FIXTURE_TEXT))[0]
    for run in runner.runs(
        suite,
        extras=True,
        pytest_args=("-k", "a or b", "-s"),
    ):
        assert run.shell() in output


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_suites_run_in_requested_order(tmp_path):
    root = fixture_root(tmp_path)
    calls, run_one = capture_runs()
    assert runner.main(["build", "alpha"], root=root, run_one=run_one) == 0
    assert [(run.suite.name, run.python) for _, run in calls] == [
        ("build", "3.13"),
        ("alpha", "3.13"),
        ("alpha", "/usr/bin/python3"),
    ]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_precede_pytest_output_once(tmp_path, capsys):
    root = fixture_root(tmp_path)

    def run_one(_root, run):
        print(f"pytest output for {run.python}")
        return 0

    assert runner.main(["alpha"], root=root, run_one=run_one) == 0
    output = capsys.readouterr().out
    assert output.index("== alpha (3.13)") < output.index("CALIBRATION_SWEEP=1")
    assert output.index("CALIBRATION_SWEEP=1") < output.index("pytest output for 3.13")
    assert "== alpha (/usr/bin/python3)" in output
    assert output.count("CALIBRATION_SWEEP=1") == 1


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_skips_nested_suite_and_prints_one_skip_line(tmp_path, capsys):
    root = fixture_root(tmp_path)
    calls, run_one = capture_runs()
    assert runner.main(["--all"], root=root, run_one=run_one) == 0
    assert [run.suite.name for _, run in calls] == ["alpha", "alpha", "build"]
    output = capsys.readouterr().out
    skip_lines = [
        line for line in output.splitlines()
        if "cc-guide" in line and "skip" in line.lower()
    ]
    assert len(skip_lines) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_named_nested_suite_runs(tmp_path):
    root = fixture_root(tmp_path)
    calls, run_one = capture_runs()
    assert runner.main(["cc-guide"], root=root, run_one=run_one) == 0
    assert [run.suite.name for _, run in calls] == ["cc-guide"]


# spec: "A failed run does not stop the next one."
# task: 4
def test_failure_does_not_stop_later_runs(tmp_path, capsys):
    root = fixture_root(tmp_path)
    statuses = iter((1, 0, 0))
    calls = []

    def run_one(_root, run):
        calls.append(run.label)
        return next(statuses)

    assert runner.main(["alpha", "build"], root=root, run_one=run_one) == 1
    assert calls == ["alpha (3.13)", "alpha (/usr/bin/python3)", "build (3.13)"]
    output = capsys.readouterr()
    assert "alpha (3.13)" in (output.out + output.err).splitlines()[-1]


# spec: "1 when any run fails (pytest's exit 5, no tests collected, counts as a failure);"
# task: 4
def test_pytest_exit_five_counts_as_failure(tmp_path):
    root = fixture_root(tmp_path)
    assert runner.main(
        ["build"],
        root=root,
        run_one=lambda _root, _run: 5,
    ) == 1


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_counts_as_failed_run(tmp_path, monkeypatch):
    root = fixture_root(tmp_path)
    suite = runner.parse(tomllib.loads(ONE_TEXT))[0]
    run = runner.runs(suite)[0]

    def cannot_start(*_args, **_kwargs):
        raise FileNotFoundError("uv")

    monkeypatch.setattr(runner.subprocess, "run", cannot_start)
    assert runner.run_subprocess(root, run) != 0


# spec: "2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_usage_and_unknown_names_exit_two(tmp_path):
    root = fixture_root(tmp_path)
    calls, run_one = capture_runs()
    for argv in ([], ["unknown"], ["--list", "unknown"]):
        assert runner.main(argv, root=root, run_one=run_one) == 2
    assert calls == []


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_pytest_arguments_reach_every_run(tmp_path):
    root = fixture_root(tmp_path)
    calls, run_one = capture_runs()
    arguments = ("test_alpha.py::test_alpha", "-k", "alpha", "-s", "-rs")
    assert runner.main(
        ["alpha", "--", *arguments],
        root=root,
        run_one=run_one,
    ) == 0
    assert len(calls) == 2
    assert all(run.argv[-len(arguments):] == arguments for _, run in calls)


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_script_finds_registry_when_launched_elsewhere(tmp_path):
    root = fixture_root(tmp_path / "source", ONE_TEXT)
    shutil.copyfile(RUNNER_PATH, root / "build/run_suites.py")
    completed = subprocess.run(
        [sys.executable, str(root / "build/run_suites.py"), "--list", "alpha"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "skills/alpha/scripts" in completed.stdout


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_receives_parent_environment_and_suite_directory(tmp_path, monkeypatch):
    root = fixture_root(tmp_path, ONE_TEXT)
    suite_dir = root / "skills/alpha/scripts"
    suite_dir.mkdir(parents=True)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    report = tmp_path / "report.json"
    fake_uv = fake_bin / "uv"
    fake_uv.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os\n"
        "from pathlib import Path\n"
        "Path(os.environ['SUITE_CAPTURE']).write_text("
        "json.dumps({'cwd': os.getcwd(), 'env': dict(os.environ)}))\n"
    )
    fake_uv.chmod(0o755)
    monkeypatch.setenv("PATH", str(fake_bin) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("SUITE_CAPTURE", str(report))
    expected_environment = dict(os.environ)

    suite = runner.parse(tomllib.loads(ONE_TEXT))[0]
    assert runner.run_subprocess(root, runner.runs(suite)[0]) == 0
    observed = json.loads(report.read_text())
    assert observed["cwd"] == str(suite_dir)
    for key, value in expected_environment.items():
        if key != "_":
            assert observed["env"].get(key) == value


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_check_finds_untracked_unregistered_test_directory(tmp_path):
    root = git_root(tmp_path)
    new_test = root / "skills/new/scripts/test_new.py"
    new_test.parent.mkdir(parents=True)
    new_test.write_text("def test_new(): pass\n")
    findings = runner.check(root, tomllib.loads(ONE_TEXT))
    assert any("skills/new/scripts" in finding for finding in findings)


# spec: "The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root."
# task: 3
def test_check_finds_tracked_unregistered_test_directory(tmp_path):
    root = git_root(tmp_path)
    new_test = root / "skills/new/scripts/test_new.py"
    new_test.parent.mkdir(parents=True)
    new_test.write_text("def test_new(): pass\n")
    subprocess.run(
        ["git", "-C", str(root), "add", "skills/new/scripts/test_new.py"],
        check=True,
    )
    findings = runner.check(root, tomllib.loads(ONE_TEXT))
    assert any("skills/new/scripts" in finding for finding in findings)


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_check_ignores_gitignored_test_trees(tmp_path):
    root = git_root(tmp_path)
    (root / ".gitignore").write_text(".claude/worktrees/\nbuild/.scratch/\n")
    for relative in (
        ".claude/worktrees/temp/test_hidden.py",
        "build/.scratch/test_hidden.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_hidden(): pass\n")
    assert runner.check(root, tomllib.loads(ONE_TEXT)) == []


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_finds_missing_and_testless_registered_directories(tmp_path):
    root = git_root(tmp_path)
    missing = {"suite": [{"name": "missing", "dir": "skills/missing/scripts", "with": ["pytest"]}]}
    assert any("skills/missing/scripts" in finding for finding in runner.check(root, missing))

    (root / "skills/alpha/scripts/test_alpha.py").unlink()
    (root / "skills/alpha/scripts/conftest.py").write_text("")
    assert any("skills/alpha/scripts" in finding for finding in runner.check(root, tomllib.loads(ONE_TEXT)))


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_check_uses_both_pytest_filename_patterns_and_directory_containment(tmp_path):
    root = git_root(tmp_path)
    nested = root / "skills/alpha/scripts/nested/example_test.py"
    nested.parent.mkdir(parents=True)
    nested.write_text("def test_nested(): pass\n")
    outside = root / "skills/beta/scripts/example_test.py"
    outside.parent.mkdir(parents=True)
    outside.write_text("def test_outside(): pass\n")
    non_test = root / "skills/gamma/scripts/examples.py"
    non_test.parent.mkdir(parents=True)
    non_test.write_text("def test_not_collected(): pass\n")
    findings = runner.check(root, tomllib.loads(ONE_TEXT))
    assert any("skills/beta/scripts" in finding for finding in findings)
    assert not any("skills/alpha/scripts/nested" in finding for finding in findings)
    assert not any("skills/gamma/scripts" in finding for finding in findings)


# spec: "If git fails, `--check` fails."
# task: 4
def test_check_fails_outside_a_git_repository(tmp_path):
    root = fixture_root(tmp_path, ONE_TEXT)
    (root / "skills/alpha/scripts").mkdir(parents=True)
    (root / "skills/alpha/scripts/test_alpha.py").write_text("def test_alpha(): pass\n")
    assert runner.main(["--check"], root=root) == 1


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_success_and_one_line_per_finding(tmp_path, capsys):
    root = git_root(tmp_path)
    assert runner.main(["--check"], root=root) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"

    for name in ("beta", "gamma"):
        path = root / f"skills/{name}/scripts/test_new.py"
        path.parent.mkdir(parents=True)
        path.write_text("def test_new(): pass\n")
    assert runner.main(["--check"], root=root) == 1
    captured = capsys.readouterr()
    lines = (captured.out + captured.err).splitlines()
    assert len(lines) == 2
    assert any("skills/beta/scripts" in line for line in lines)
    assert any("skills/gamma/scripts" in line for line in lines)


# spec: "The real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_passes_check(capsys):
    assert runner.main(["--check"], root=ROOT) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"


# spec: "Its header says \"nine\"."
# task: 6
def test_commit_lint_script_has_the_ninth_suite_registry_command():
    script = (ROOT / "build/run_commit_lints.sh").read_text()
    assert "nine" in script.lower()
    assert re.search(
        r"(?m)^run suite_registry uv run --python 3\.13 python build/run_suites\.py --check$",
        script,
    )
    assert script.count("run_suites.py") == 1


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_test_module_registers_the_check_and_regression_test():
    path = ROOT / "build/test_commit_lints.py"
    specification = importlib.util.spec_from_file_location("test_commit_lints_acceptance", path)
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    assert "suite_registry" in repr(module.CHECKS)
    assert callable(module.test_unregistered_suite_is_refused)


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_guide_intro_retains_rules_and_points_to_registry():
    text = (ROOT / "CLAUDE.md").read_text()
    introduction = next(
        line for line in text.splitlines() if "build/suites.toml" in line
    )
    for term in ("uv", "3.13", "directory", "test_build.py", "build/run_suites.py", "note"):
        assert term in introduction
    assert "There is no root test runner" not in introduction


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_guide_has_runner_commands_and_no_directory_suite_command():
    text = (ROOT / "CLAUDE.md").read_text()
    for command in (
        "build/run_suites.py --list",
        "build/run_suites.py <name> [--extras] [-- <pytest args>]",
        "build/run_suites.py --all",
        "build/run_suites.py --check",
    ):
        assert command in text

    for line in text.splitlines():
        if re.match(r"^cd (?:skills/\S+|build(?:/cc_guide)?|hooks) &&", line):
            if "python -m pytest -q" in line:
                tail = line.split("python -m pytest -q", 1)[1].strip()
                assert tail, line


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_selected_tests_and_tools_remain_in_root_guide():
    text = (ROOT / "CLAUDE.md").read_text()
    for command_part in (
        "test_runtime_support.py",
        "test_commit_lints.py",
        "-k declared_dependencies",
        "-k test_real_skill",
        "test_check_jax_examples.py",
        "verify_citations.py",
        "extract_structure.py",
        "cli.py lint",
        "cli.py check",
    ):
        assert command_part in text
    assert text.count("build.py") >= 2


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_root_guide_has_no_suite_or_test_count_claim_and_is_under_limit():
    lines = (ROOT / "CLAUDE.md").read_text().splitlines()
    assert len(lines) < 200
    assert not re.search(
        r"\b\d+\s+(?:directory\s+)?(?:suites|tests)\b",
        "\n".join(lines),
        re.IGNORECASE,
    )


# spec: "`build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_guide_describes_nine_lints_and_registry():
    text = (ROOT / "build/CLAUDE.md").read_text()
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    assert "suites.toml" in text
    assert "run_suites.py" in text
    assert "--check" in text


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_uses_first_line_stamp():
    first_line = (ROOT / "CLAUDE.md").read_text().splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .+ @\S+ -->", first_line)

    source = (ROOT / "build/test_check_conformance.py").read_text()
    tree = ast.parse(source)
    function = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    function_source = ast.get_source_segment(source, function)
    assert "@needs_pilot" not in function_source
    assert "cc-guide" in function_source


# spec: "It asserts that the set equals the set of default shell forms that `--list` prints: nothing is missing on either side."
# task: 5
def test_default_list_shell_forms_equal_pre_shrink_commands(capsys):
    baseline = subprocess.run(
        ["git", "show", "456e3fb:CLAUDE.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    old_forms = set()
    for line in [*baseline[65:125], baseline[144]]:
        if re.match(r"^cd \S+ && uv run ", line):
            parts = line.split(" && ")
            old_forms.update(f"{parts[0]} && {part}" for part in parts[1:])

    assert runner.main(["--list"], root=ROOT) == 0
    listed_forms = {
        line for line in capsys.readouterr().out.splitlines()
        if line.startswith("cd ")
    }
    assert listed_forms == old_forms


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 4
def test_runner_imports_only_standard_library_modules():
    tree = ast.parse(RUNNER_PATH.read_text())
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert imported_roots <= sys.stdlib_module_names | {"__future__"}
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`.</plan></flag>
<flag task="5"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>`cc_guide`</plan></flag>
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
Matches conformance.toml and manifest.toml.
Rejected: a Python list inside the runner (every suite change becomes a code edit), and one manifest per suite directory (`install.py` copies skill directories, so the manifests would ship with installed skills).
An `@`-imported document was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
Design section 1 (the registry keys and the runner's behaviour) was approved as presented.
Design section 2 (the guard, the file edits, the tests and the couplings) was approved as presented.
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
Run it before the `CLAUDE.md` deletion.
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
It would need node, a 3.9 `/usr/bin/python3` and `build/.scratch/`.
Revisit if: the owner wants suites in CI.
Revisit if: `--all` gets slow or a tool needs to parse its results.
Revisit if: `CLAUDE.md` nears its limit again.
</untestable>