<tests>
import ast
import copy
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tomllib

import pytest

import build.run_suites as runner


FIXTURE = """
[[suite]]
name = "brainstorming"
dir = "skills/brainstorming/scripts"
with = ["pytest"]
notes = ["node skip"]

[[suite]]
name = "build"
dir = "build"
with = ["pytest", "numpy", "polars", "pyyaml"]
extras = ["arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots", "numpyro", "jax", "matplotlib"]
notes = ["build/.scratch/"]

[[suite]]
name = "cc-guide"
dir = "build/cc_guide"
with = ["pytest"]

[[suite]]
name = "hooks"
dir = "hooks"
with = ["pytest"]
pythons = ["3.13", "/usr/bin/python3"]
notes = ["hook note"]
"""

HOOKS_REGISTRY = """
[[suite]]
name = "hooks"
dir = "hooks"
with = ["pytest"]
"""


def write_registry(root: Path, text: str = FIXTURE) -> None:
    (root / "build").mkdir(parents=True, exist_ok=True)
    (root / "build/suites.toml").write_text(text)


def fixture_root(tmp_path: Path) -> Path:
    write_registry(tmp_path)
    return tmp_path


def init_git(root: Path) -> None:
    subprocess.run(
        ["git", "init", "-q"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def covered_git_root(root: Path) -> Path:
    write_registry(root, HOOKS_REGISTRY)
    (root / "hooks").mkdir()
    (root / "hooks/test_ok.py").write_text("def test_ok():\n    assert True\n")
    init_git(root)
    subprocess.run(
        ["git", "add", "build/suites.toml", "hooks/test_ok.py"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return root


def baseline_file(path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"456e3fb:{path}"],
        cwd=runner.REPO,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_has_the_spec_inventory() -> None:
    data = tomllib.loads((runner.REPO / "build/suites.toml").read_text())
    entries = data["suite"]
    expected = {
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
    names = [entry["name"] for entry in entries]
    assert names == sorted(expected)
    assert len(names) == len(set(names))
    assert {
        entry["name"]: (
            entry["dir"],
            entry["with"],
            entry.get("extras", []),
            entry.get("pythons", ["3.13"]),
        )
        for entry in entries
    } == expected


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_explains_its_contract() -> None:
    header = (runner.REPO / "build/suites.toml").read_text().split("[[suite]]", 1)[0]
    assert header.strip()
    assert all(line.lstrip().startswith("#") for line in header.splitlines() if line.strip())
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert re.search(rf"\b{key}\b", header)
    assert re.search(r"sort", header, re.I)
    assert re.search(r"ninth|nine|9", header, re.I)
    assert re.search(r"commit lint", header, re.I)


# spec: "The notes carry the rest of each comment."
# task: 5
def test_registry_preserves_the_named_operational_notes() -> None:
    entries = tomllib.loads((runner.REPO / "build/suites.toml").read_text())["suite"]
    notes = {entry["name"]: " ".join(entry.get("notes", [])) for entry in entries}
    assert "build/.scratch/" in notes["build"]
    assert "CALIBRATION_SWEEP=1" in notes["bayesian-workflow"]
    assert "arviz" in notes["bayesian-workflow"].lower()
    assert "warn" in notes["bayesian-workflow"].lower()
    assert "@needs_pilot" in notes["llm-wiki"]
    assert "LLM_WIKI_ROOT" in notes["llm-wiki"]
    assert "node" in notes["brainstorming"].lower()
    assert "skip" in notes["brainstorming"].lower()
    assert "sklearn" in notes["tune-hyperparameters"]
    assert "fails" in notes["tune-hyperparameters"].lower()
    assert re.search(r"minute|second|runtime|run time|takes|slow", notes["track-model-experiments"], re.I)
    assert "3.9" in notes["hooks"]
    assert "launchd" in notes["hooks"].lower()
    assert "PATH" in notes["hooks"]
    assert "Gate B" in notes["hooks"]


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 4
def test_cli_starts_without_site_packages(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-S", str(Path(runner.__file__).resolve()), "--list", "brainstorming"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "brainstorming" in result.stdout


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_default_root_does_not_follow_the_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert runner.REPO == Path(runner.__file__).resolve().parents[1]
    monkeypatch.chdir(tmp_path)
    assert runner.main(["--list", "brainstorming"]) == 0
    assert "skills/brainstorming/scripts" in capsys.readouterr().out


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 4
def test_run_argv_cwd_and_inherited_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    suite = runner.Suite("brainstorming", "skills/brainstorming/scripts", ("pytest",))
    run = runner.runs(suite, pytest_args=("-s",))[0]
    assert run.argv == (
        "uv", "run", "--python", "3.13", "--with", "pytest",
        "python", "-m", "pytest", "-q", "-s",
    )

    suite_dir = tmp_path / suite.dir
    suite_dir.mkdir(parents=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_uv = bin_dir / "uv"
    fake_uv.write_text(
        '#!/bin/sh\nprintf "%s\\n" "$PWD" "$CALIBRATION_SWEEP" "$@" > "$RUN_CAPTURE"\n'
    )
    fake_uv.chmod(0o755)
    capture = tmp_path / "capture.txt"
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("RUN_CAPTURE", str(capture))

    assert runner.run_subprocess(tmp_path, run) == 0
    lines = capture.read_text().splitlines()
    assert lines[:2] == [str(suite_dir.resolve()), "1"]
    assert lines[2:] == list(run.argv[1:])


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_directory_dependencies_and_pytest_arguments() -> None:
    suite = runner.Suite(
        "build", "build/dir with spaces", ("pytest", "arviz>=1.0")
    )
    run = runner.runs(suite, pytest_args=("test case.py", "-k", "one or two"))[0]
    assert run.shell() == (
        "cd " + shlex.quote("build/dir with spaces")
        + " && uv run --python 3.13 --with pytest --with "
        + shlex.quote("arviz>=1.0")
        + " python -m pytest -q "
        + shlex.quote("test case.py")
        + " -k "
        + shlex.quote("one or two")
    )


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 2
def test_hooks_produces_two_independent_shell_forms() -> None:
    suite = runner.Suite(
        "hooks", "hooks", ("pytest",), pythons=("3.13", "/usr/bin/python3")
    )
    forms = [run.shell() for run in runner.runs(suite)]
    assert forms == [
        "cd hooks && uv run --python 3.13 --with pytest python -m pytest -q",
        "cd hooks && uv run --python /usr/bin/python3 --with pytest python -m pytest -q",
    ]


# spec: "`--extras` adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_follow_default_dependencies() -> None:
    suite = runner.Suite(
        "build", "build", ("pytest", "numpy", "polars", "pyyaml"),
        extras=("arviz>=1.0", "arviz-base"),
    )
    assert runner.runs(suite)[0].argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy", "--with", "polars",
        "--with", "pyyaml", "python", "-m", "pytest", "-q",
    )
    assert runner.runs(suite, extras=True)[0].argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest", "--with", "numpy", "--with", "polars",
        "--with", "pyyaml", "--with", "arviz>=1.0",
        "--with", "arviz-base", "python", "-m", "pytest", "-q",
    )


# spec: "`--list [NAME …]` prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_shows_all_suites_and_selected_suites(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = fixture_root(tmp_path)
    assert runner.main(["--list"], root=root) == 0
    output = capsys.readouterr().out
    for name in ("brainstorming", "build", "cc-guide", "hooks"):
        assert name in output
    assert "skills/brainstorming/scripts" in output
    assert "build/cc_guide" in output
    assert "arviz>=1.0" in output
    assert "node skip" in output
    assert "cd hooks && uv run --python 3.13" in output
    assert "cd hooks && uv run --python /usr/bin/python3" in output

    assert runner.main(["--list", "brainstorming"], root=root) == 0
    selected = capsys.readouterr().out
    assert "brainstorming" in selected
    assert "cc-guide" not in selected
    assert "hooks" not in selected


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_prints_the_command_with_extras_and_pytest_arguments(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = fixture_root(tmp_path)
    assert runner.main(
        ["--list", "build", "--extras", "--", "-k", "declared_dependencies"],
        root=root,
    ) == 0
    output = capsys.readouterr().out
    build = next(s for s in runner.parse(tomllib.loads(FIXTURE)) if s.name == "build")
    expected = runner.runs(
        build, extras=True, pytest_args=("-k", "declared_dependencies")
    )[0].shell()
    assert expected in output


# spec: "`NAME [NAME …]` runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_runs_follow_name_and_interpreter_order(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = fixture_root(tmp_path)
    seen = []

    def fake_run(root_arg: Path, run: runner.Run) -> int:
        seen.append(run.label)
        print(f"pytest output for {run.label}")
        return 5 if run.label == "hooks (3.13)" else 0

    assert runner.main(["hooks", "brainstorming"], root=root, run_one=fake_run) == 1
    assert seen == [
        "hooks (3.13)", "hooks (/usr/bin/python3)", "brainstorming (3.13)"
    ]
    captured = capsys.readouterr()
    output = captured.out
    assert output.index("== hooks (3.13)") < output.index("hook note")
    assert output.index("hook note") < output.index("pytest output for hooks (3.13)")
    assert output.index("pytest output for hooks (3.13)") < output.index(
        "== hooks (/usr/bin/python3)"
    )
    assert output.count("hook note") == 1
    assert "hooks (3.13)" in captured.out + captured.err


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_pytest_arguments_reach_every_interpreter(tmp_path: Path) -> None:
    root = fixture_root(tmp_path)
    seen = []

    def fake_run(root_arg: Path, run: runner.Run) -> int:
        seen.append(run.argv)
        return 0

    assert runner.main(
        ["hooks", "--", "test_new.py::test_one", "-k", "declared_dependencies", "-s", "-rs"],
        root=root,
        run_one=fake_run,
    ) == 0
    assert len(seen) == 2
    expected_tail = (
        "test_new.py::test_one", "-k", "declared_dependencies", "-s", "-rs"
    )
    assert all(argv[-len(expected_tail):] == expected_tail for argv in seen)


# spec: "`--all` runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_skips_nested_suite_once_but_named_nested_suite_runs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = fixture_root(tmp_path)
    seen = []

    def fake_run(root_arg: Path, run: runner.Run) -> int:
        seen.append(run.suite.name)
        return 0

    assert runner.main(["--all"], root=root, run_one=fake_run) == 0
    assert "cc-guide" not in seen
    assert seen.count("build") == 1
    assert seen.count("hooks") == 2
    skip_lines = [
        line for line in capsys.readouterr().out.splitlines()
        if "skip" in line.lower()
    ]
    assert len(skip_lines) == 1
    assert "cc-guide" in skip_lines[0]
    assert "build" in skip_lines[0]

    seen.clear()
    assert runner.main(["cc-guide"], root=root, run_one=fake_run) == 0
    assert seen == ["cc-guide"]


# spec: "Exit status: 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_run_and_usage_exit_statuses(tmp_path: Path) -> None:
    root = fixture_root(tmp_path)
    assert runner.main(
        ["brainstorming"], root=root, run_one=lambda root_arg, run: 0
    ) == 0
    assert runner.main(
        ["brainstorming"], root=root, run_one=lambda root_arg, run: 5
    ) == 1
    assert runner.main(["unknown"], root=root) == 2

    usage = subprocess.run(
        [sys.executable, str(Path(runner.__file__).resolve()), "--not-an-option"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert usage.returncode == 2


# spec: "The last line names the failed runs, or says that every run passed."
# task: 4
def test_final_summary_reports_success_or_failed_label(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = fixture_root(tmp_path)
    assert runner.main(
        ["brainstorming"], root=root, run_one=lambda root_arg, run: 0
    ) == 0
    passed = capsys.readouterr()
    assert "passed" in (passed.out + passed.err).splitlines()[-1].lower()

    assert runner.main(
        ["brainstorming"], root=root, run_one=lambda root_arg, run: 5
    ) == 1
    failed = capsys.readouterr()
    assert "brainstorming (3.13)" in (failed.out + failed.err).splitlines()[-1]


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_counts_as_a_failed_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = fixture_root(tmp_path)
    (root / "skills/brainstorming/scripts").mkdir(parents=True)
    empty_bin = root / "empty-bin"
    empty_bin.mkdir()
    monkeypatch.setenv("PATH", str(empty_bin))
    assert runner.main(
        ["brainstorming"], root=root, run_one=runner.run_subprocess
    ) == 1


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
def test_validate_rejects_every_listed_registry_error() -> None:
    base = {
        "suite": [{
            "name": "brainstorming",
            "dir": "skills/brainstorming/scripts",
            "with": ["pytest"],
        }]
    }
    bad = []
    for key in ("name", "dir", "with"):
        case = copy.deepcopy(base)
        del case["suite"][0][key]
        bad.append(case)
    case = copy.deepcopy(base)
    case["suite"][0]["wit"] = ["pytest"]
    bad.append(case)
    for key, value in (
        ("name", 1), ("dir", 1), ("with", "pytest"),
        ("extras", "numpy"), ("pythons", "3.13"), ("notes", "note"),
        ("with", ["pytest", 1]),
    ):
        case = copy.deepcopy(base)
        case["suite"][0][key] = value
        bad.append(case)
    case = copy.deepcopy(base)
    case["suite"].append({
        "name": "brainstorming", "dir": "hooks", "with": ["pytest"]
    })
    bad.append(case)
    case = copy.deepcopy(base)
    case["suite"].append({
        "name": "hooks", "dir": "skills/brainstorming/scripts",
        "with": ["pytest"],
    })
    bad.append(case)
    case = copy.deepcopy(base)
    case["suite"][0]["with"] = ["numpy"]
    bad.append(case)

    assert runner.validate(base) == []
    for case in bad:
        findings = runner.validate(case)
        assert findings
        assert all(isinstance(finding, str) for finding in findings)


# spec: "A misspelled key can therefore never run a suite without its deps."
# task: 4
def test_invalid_registry_blocks_every_run_mode(tmp_path: Path) -> None:
    bad_registry = """
[[suite]]
name = "brainstorming"
dir = "skills/brainstorming/scripts"
wit = ["pytest"]
"""
    write_registry(tmp_path, bad_registry)
    seen = []

    def fake_run(root_arg: Path, run: runner.Run) -> int:
        seen.append(run)
        return 0

    for args in (["--list"], ["brainstorming"], ["--all"]):
        assert runner.main(args, root=tmp_path, run_one=fake_run) == 2
    assert seen == []


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
def test_check_reports_registry_validation_problems(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = covered_git_root(tmp_path)
    bad_registry = """
[[suite]]
name = "hooks"
dir = "hooks"
wit = ["pytest"]
"""
    write_registry(root, bad_registry)
    data = tomllib.loads(bad_registry)
    findings = runner.check(root, data)
    assert findings
    assert all(isinstance(line, str) and "\n" not in line for line in findings)
    assert runner.main(["--check"], root=root) == 1
    output = capsys.readouterr()
    assert len((output.out + output.err).splitlines()) == len(findings)


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_reports_success_exactly(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = covered_git_root(tmp_path)
    assert runner.check(root, tomllib.loads(HOOKS_REGISTRY)) == []
    assert runner.main(["--check"], root=root) == 0
    output = capsys.readouterr()
    assert (output.out + output.err).strip() == "suite registry ok"


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_check_finds_an_untracked_test_directory(tmp_path: Path) -> None:
    root = covered_git_root(tmp_path)
    new_dir = root / "skills/write-with-asd-ste100/scripts"
    new_dir.mkdir(parents=True)
    (new_dir / "test_new.py").write_text("def test_new():\n    assert True\n")

    findings = runner.check(root, tomllib.loads(HOOKS_REGISTRY))
    assert len(findings) == 1
    assert "skills/write-with-asd-ste100/scripts" in findings[0]


# spec: "`--check` reports two kinds of findings:"
# task: 3
def test_check_finds_missing_and_testless_registered_directories(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"
    missing.mkdir()
    write_registry(missing, HOOKS_REGISTRY)
    init_git(missing)
    missing_findings = runner.check(missing, tomllib.loads(HOOKS_REGISTRY))
    assert len(missing_findings) == 1
    assert "hooks" in missing_findings[0]

    testless = tmp_path / "testless"
    testless.mkdir()
    write_registry(testless, HOOKS_REGISTRY)
    (testless / "hooks").mkdir()
    (testless / "hooks/README.md").write_text("No pytest files here.\n")
    init_git(testless)
    testless_findings = runner.check(testless, tomllib.loads(HOOKS_REGISTRY))
    assert len(testless_findings) == 1
    assert "hooks" in testless_findings[0]


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_check_ignores_git_ignored_test_trees(tmp_path: Path) -> None:
    root = covered_git_root(tmp_path)
    (root / ".gitignore").write_text("/.claude/worktrees/\n/build/.scratch/\n")
    for relative in (
        ".claude/worktrees/one/test_new.py",
        "build/.scratch/test_new.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True)
        path.write_text("def test_new():\n    assert True\n")
    assert runner.check(root, tomllib.loads(HOOKS_REGISTRY)) == []


# spec: "If git fails, `--check` fails."
# task: 3
def test_check_fails_outside_a_git_repository(tmp_path: Path) -> None:
    write_registry(tmp_path, HOOKS_REGISTRY)
    (tmp_path / "hooks").mkdir()
    (tmp_path / "hooks/test_ok.py").write_text("def test_ok():\n    assert True\n")
    assert runner.check(tmp_path, tomllib.loads(HOOKS_REGISTRY))
    assert runner.main(["--check"], root=tmp_path) == 1


# spec: "With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character."
# task: 5
def test_default_shell_forms_match_the_pre_deletion_commands() -> None:
    baseline = baseline_file("CLAUDE.md").splitlines()
    old_commands = []
    for line in baseline[65:125] + baseline[144:145]:
        command = line.strip()
        if not command.startswith("cd "):
            continue
        directory_command, separator, tail = command.partition(" && ")
        assert separator
        for part in re.split(r" && (?=uv run\b)", tail):
            old_commands.append(directory_command + " && " + part)

    data = tomllib.loads((runner.REPO / "build/suites.toml").read_text())
    current_commands = {
        run.shell()
        for suite in runner.parse(data)
        for run in runner.runs(suite)
    }
    assert len(old_commands) == 19
    assert set(old_commands) == current_commands


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_selected_non_suite_commands_remain_literal() -> None:
    before = baseline_file("CLAUDE.md")
    after = (runner.REPO / "CLAUDE.md").read_text()
    tokens = (
        "test_runtime_support.py",
        "test_commit_lints.py",
        "-k declared_dependencies",
        "-k test_real_skill",
        "test_check_jax_examples.py",
        "verify_citations.py",
        "extract_structure.py",
        "cli.py lint",
        "cli.py check",
    )
    for token in tokens:
        old_lines = [
            line.strip() for line in before.splitlines()
            if token in line and "uv run" in line
        ]
        assert old_lines, token
        assert all(line in after for line in old_lines), token
    assert "Single test" in after


# spec: "`build/run_commit_lints.sh` keeps its literal commands."
# task: 6
def test_prior_commit_lint_commands_remain_literal() -> None:
    before = baseline_file("build/run_commit_lints.sh")
    after = (runner.REPO / "build/run_commit_lints.sh").read_text()
    prior_runs = [
        line.strip() for line in before.splitlines()
        if line.strip().startswith("run ")
    ]
    assert prior_runs
    assert all(line in after.splitlines() for line in prior_runs)


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_ninth_lint_is_wired_to_check() -> None:
    script = (runner.REPO / "build/run_commit_lints.sh").read_text()
    run_lines = [
        line.strip() for line in script.splitlines()
        if line.strip().startswith("run ")
    ]
    assert len(run_lines) == 9
    assert run_lines[-1] == (
        "run suite_registry uv run --python 3.13 "
        "python build/run_suites.py --check"
    )
    assert re.search(r"nine", script.splitlines()[0], re.I)
    lint_tests = (runner.REPO / "build/test_commit_lints.py").read_text()
    assert "suite_registry" in lint_tests
    assert "def test_unregistered_suite_is_refused" in lint_tests


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_commands_block_uses_the_runner() -> None:
    text = (runner.REPO / "CLAUDE.md").read_text()
    lines = text.splitlines()
    assert len(lines) < 200
    intro = next(
        line for line in lines
        if "build/suites.toml" in line and "build/run_suites.py" in line
    )
    for value in ("uv", "3.13", "test_build.py", "notes"):
        assert value in intro
    assert "directory" in intro.lower()
    assert "There is no root test runner" not in text
    for option in ("--list", "--all", "--check"):
        assert f"uv run --python 3.13 python build/run_suites.py {option}" in text
    assert "<name> [--extras] [-- <pytest args>]" in text
    assert "run_suites.py cc-guide" in text

    registered_dirs = [
        entry["dir"]
        for entry in tomllib.loads((runner.REPO / "build/suites.toml").read_text())["suite"]
    ]
    for directory in registered_dirs:
        assert not any(
            re.match(rf"\s*cd\s+{re.escape(directory)}\s+&&\s+uv run\b", line)
            for line in lines
        ), directory


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_new_root_runner_text_has_no_suite_or_test_count() -> None:
    lines = (runner.REPO / "CLAUDE.md").read_text().splitlines()
    runner_lines = [
        line for line in lines
        if "run_suites.py" in line or "suites.toml" in line
    ]
    assert runner_lines
    assert not re.search(r"\b\d+\s+(?:suites|tests)\b", "\n".join(runner_lines), re.I)


# spec: "`build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_guide_describes_the_ninth_lint() -> None:
    text = (runner.REPO / "build/CLAUDE.md").read_text()
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    assert "suites.toml" in text
    assert "run_suites.py" in text
    assert "--check" in text
    assert "commit lint" in text


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_uses_the_versioned_stamp() -> None:
    first_line = (runner.REPO / "CLAUDE.md").read_text().splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .*@\S+ -->", first_line)

    source = (runner.REPO / "build/test_check_conformance.py").read_text()
    tree = ast.parse(source)
    test = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    test_source = ast.get_source_segment(source, test)
    assert test_source is not None
    assert "@needs_pilot" not in test_source


# spec: "Gates. `uv run --python 3.13 python build/run_suites.py --check` prints `suite registry ok`."
# task: 5
def test_real_registry_passes_check(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert runner.main(["--check"]) == 0
    output = capsys.readouterr()
    assert (output.out + output.err).strip() == "suite registry ok"
</tests>
<flags>
<flag task="1"><spec>The name that the runner takes. A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`.</plan></flag>
<flag task="2"><spec>Default `['3.13']`.</spec><plan>`DEFAULT_PYTHONS = ('3.12',)`</plan></flag>
<flag task="5"><spec>`cc-guide` | `build/cc_guide` | — | — | default</spec><plan>`cc_guide`</plan></flag>
</flags>
<untestable>
**Status:** Design approved in brainstorming on 2026-10-18.
Next step: an implementation plan from the writing-plans skill (`entry_check.py` reported plan id 54 as next free on 2026-10-18).
Three plans competed for the last lines on 2026-10-18.
Plan 50 (the superpowers upstream fixes, lowmason/agent-skills#56) took the file from 195 to 199.
Plan 52 (the write-with-asd-ste100 skill, not merged) needs two more lines.
Its open question Q4 asked where they come from: (a) fold seven suites under one comment, (b) record a size deviation, or (c) move the per-suite commands out of the root file first.
This spec is option (c).
Plan 38 fixed the same problem once.
In plan 38, Task 2 condensed `CLAUDE.md` from 224 lines to 170 and kept every command in place.
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
The file ends at about 145 lines.
The deletion of lines 66–125 is bounded by two lines that no other plan edits: the `# Full build-directory tests` comment and the `cd hooks && …` command.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
The new files are the owner's original tooling.
The register's deviation `claude-md-serves-codex-gemini` still holds as written: a condensed Commands block stays in the root file, and the registry is a plain file that every runtime can read.
Write each test before its code and see it fail first (red, then green).
A note in the session group's shared notes folder gives the exact entry.
If plan 52 lands first after all, R5.2's deletion still works, and this plan registers that suite itself.
None of the lines that R5.1 deletes carries one of its edit anchors.
Its Task 7 edits line 133, which stays.
Its own suite commands are written out in full in the plan, so they work without `CLAUDE.md`.
It edits one sentence of `build/CLAUDE.md`'s `cc_guide/` paragraph.
R5.3 edits the `run_commit_lints.sh` paragraph and adds a sentence.
If an edit block does not match, merge by hand.
Run it before the `CLAUDE.md` deletion.
Then run `--all` once, and record each run's result beside the direct result.
`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`.
The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
The commit hook runs one more fast, stdlib-only check.
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
CI running the suites (`--all` in `.github/workflows/lints.yml`).
Parallel runs, per-suite timeouts and machine-readable output.
Moving the lint, snippet, JAX, smoke, rebuild and citation commands into the runner.
</untestable>