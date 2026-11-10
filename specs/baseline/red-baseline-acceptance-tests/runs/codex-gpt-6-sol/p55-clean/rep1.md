<tests>
import ast
import copy
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tomllib

import pytest

from build import run_suites as runner


REPO = Path(runner.__file__).resolve().parents[1]

INVENTORY = {
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


def _row(name, directory, deps, *, extras=None, pythons=None, notes=None):
    row = {"name": name, "dir": directory, "with": deps}
    if extras is not None:
        row["extras"] = extras
    if pythons is not None:
        row["pythons"] = pythons
    if notes is not None:
        row["notes"] = notes
    return row


def _fixture():
    return {"suite": [
        _row("brainstorming", "skills/brainstorming/scripts", ["pytest"], notes=["node skip"]),
        _row(
            "build",
            "build",
            ["pytest", "numpy", "polars", "pyyaml"],
            extras=["arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots", "numpyro", "jax", "matplotlib"],
            notes=["build/.scratch/ is missing in a fresh worktree"],
        ),
        _row("cc-guide", "build/cc_guide", ["pytest"]),
        _row(
            "hooks",
            "hooks",
            ["pytest"],
            pythons=["3.13", "/usr/bin/python3"],
            notes=["3.9 floor", "launchd-PATH skips", "Gate B probe"],
        ),
    ]}


def _single():
    return {"suite": [_row("brainstorming", "skills/brainstorming/scripts", ["pytest"])]}


def _write(root, relative, content=""):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def _registry(root, data):
    lines = ["# name, dir, with, extras, pythons, notes; sorted by name; ninth commit lint checks this file"]
    for row in data["suite"]:
        lines.append("[[suite]]")
        for key, value in row.items():
            lines.append(f"{key} = {json.dumps(value)}")
    return _write(root, "build/suites.toml", "\n".join(lines) + "\n")


def _git(root):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True, text=True)


def _valid_git_root(root):
    _git(root)
    _registry(root, _single())
    _write(root, "skills/brainstorming/scripts/test_brainstorming.py")
    return root


BAD_CASES = (
    "unknown_key", "missing_name", "missing_dir", "missing_with",
    "wrong_name", "wrong_dir", "wrong_with", "wrong_with_item",
    "wrong_extras", "wrong_extras_item", "wrong_pythons",
    "wrong_pythons_item", "wrong_notes", "wrong_notes_item",
    "duplicate_name", "duplicate_dir", "missing_pytest",
)


def _bad(kind):
    data = copy.deepcopy(_single())
    row = data["suite"][0]
    if kind == "unknown_key":
        row["wit"] = ["pytest"]
    elif kind.startswith("missing_") and kind != "missing_pytest":
        del row[kind.removeprefix("missing_")]
    elif kind == "wrong_name":
        row["name"] = 313
    elif kind == "wrong_dir":
        row["dir"] = 313
    elif kind == "wrong_with":
        row["with"] = "pytest"
    elif kind == "wrong_with_item":
        row["with"] = ["pytest", 313]
    elif kind == "wrong_extras":
        row["extras"] = "matplotlib"
    elif kind == "wrong_extras_item":
        row["extras"] = [313]
    elif kind == "wrong_pythons":
        row["pythons"] = "3.13"
    elif kind == "wrong_pythons_item":
        row["pythons"] = [313]
    elif kind == "wrong_notes":
        row["notes"] = "node skip"
    elif kind == "wrong_notes_item":
        row["notes"] = [313]
    elif kind == "duplicate_name":
        data["suite"].append(_row("brainstorming", "hooks", ["pytest"]))
    elif kind == "duplicate_dir":
        data["suite"].append(_row("hooks", "skills/brainstorming/scripts", ["pytest"]))
    elif kind == "missing_pytest":
        row["with"] = ["numpy"]
    return data


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_has_the_spec_inventory():
    data = tomllib.loads((REPO / "build/suites.toml").read_text())
    rows = data["suite"]
    assert len(rows) == len(INVENTORY)
    assert [row["name"] for row in rows] == sorted(INVENTORY)
    for row in rows:
        directory, deps, extras, pythons = INVENTORY[row["name"]]
        assert row["dir"] == directory
        assert row["with"] == deps
        assert row.get("extras", []) == extras
        assert row.get("pythons", ["3.13"]) == pythons
        assert all(isinstance(note, str) for note in row.get("notes", []))


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_explains_its_contract():
    header = (REPO / "build/suites.toml").read_text().split("[[suite]]", 1)[0].lower()
    assert all(key in header for key in ("name", "dir", "with", "extras", "pythons", "notes"))
    assert "sort" in header
    assert re.search(r"ninth|nine|9th", header)
    assert "commit lint" in header
    assert "check" in header


# spec: "The notes carry the rest of each comment."
# task: 5
def test_registry_keeps_the_named_operational_notes():
    rows = tomllib.loads((REPO / "build/suites.toml").read_text())["suite"]
    notes = {row["name"]: " ".join(row.get("notes", [])) for row in rows}
    assert "build/.scratch/" in notes["build"]
    assert "CALIBRATION_SWEEP=1" in notes["bayesian-workflow"]
    assert "arviz" in notes["bayesian-workflow"].lower()
    assert "@needs_pilot" in notes["llm-wiki"]
    assert "$LLM_WIKI_ROOT" in notes["llm-wiki"]
    assert "node" in notes["brainstorming"].lower()
    assert "sklearn" in notes["tune-hyperparameters"]
    assert "3.9" in notes["hooks"]
    assert "launchd" in notes["hooks"].lower()
    assert "Gate B" in notes["hooks"]
    assert notes["track-model-experiments"]


# spec: "Default `['3.13']`."
# task: 2
def test_optional_registry_fields_have_spec_defaults():
    data = _single()
    assert runner.validate(data) == []
    suite = runner.parse(data)[0]
    assert suite.extras == ()
    assert suite.pythons == ("3.13",)
    assert suite.notes == ()


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
def test_validation_rejects_each_malformed_registry_case():
    for kind in BAD_CASES:
        assert runner.validate(_bad(kind)), kind


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_every_run_mode_fails_closed_on_malformed_registry(tmp_path, capsys):
    for kind in BAD_CASES:
        _registry(tmp_path, _bad(kind))
        for argv in (["--list"], ["brainstorming"], ["--all"]):
            assert runner.main(argv, root=tmp_path, run_one=lambda root, run: 0) == 2, (kind, argv)
            capsys.readouterr()


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_run_argv_and_working_directory():
    suite = runner.parse(_fixture())[0]
    run = runner.runs(suite)[0]
    assert run.suite.dir == "skills/brainstorming/scripts"
    assert run.python == "3.13"
    assert run.argv == ("uv", "run", "--python", "3.13", "--with", "pytest", "python", "-m", "pytest", "-q")
    assert run.shell() == "cd skills/brainstorming/scripts && uv run --python 3.13 --with pytest python -m pytest -q"


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_pytest_selection():
    build = next(s for s in runner.parse(_fixture()) if s.name == "build")
    run = runner.runs(build, pytest_args=("-k", "declared_dependencies or test_real_skill"))[0]
    assert run.shell().startswith("cd build && uv run ")
    assert run.shell().endswith("-k 'declared_dependencies or test_real_skill'")
    assert shlex.split(run.shell().split(" && ", 1)[1]) == list(run.argv)


# spec: "The interpreters, one run each, in order."
# task: 2
def test_hooks_have_two_ordered_runs():
    hooks = next(s for s in runner.parse(_fixture()) if s.name == "hooks")
    runs = runner.runs(hooks)
    assert [run.python for run in runs] == ["3.13", "/usr/bin/python3"]
    assert [run.shell() for run in runs] == [
        "cd hooks && uv run --python 3.13 --with pytest python -m pytest -q",
        "cd hooks && uv run --python /usr/bin/python3 --with pytest python -m pytest -q",
    ]


# spec: "`--extras` adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_are_opt_in_and_follow_default_dependencies():
    build = next(s for s in runner.parse(_fixture()) if s.name == "build")
    default = runner.runs(build)[0].argv
    expanded = runner.runs(build, extras=True)[0].argv
    assert default == ("uv", "run", "--python", "3.13", "--with", "pytest", "--with", "numpy", "--with", "polars", "--with", "pyyaml", "python", "-m", "pytest", "-q")
    assert expanded[:len(default) - 4] == default[:len(default) - 4]
    assert expanded[len(default) - 4:-4] == (
        "--with", "arviz>=1.0", "--with", "arviz-base", "--with", "arviz-stats",
        "--with", "arviz-plots", "--with", "numpyro", "--with", "jax",
        "--with", "matplotlib",
    )
    assert expanded[-4:] == ("python", "-m", "pytest", "-q")


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 2
def test_pytest_arguments_reach_each_interpreter():
    hooks = next(s for s in runner.parse(_fixture()) if s.name == "hooks")
    for run in runner.runs(hooks, pytest_args=("test_new.py::test_new", "-k", "test_real_skill", "-s", "-rs")):
        assert run.argv[-5:] == ("test_new.py::test_new", "-k", "test_real_skill", "-s", "-rs")


# spec: "`--all` runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_finds_the_outer_suite():
    suites = runner.parse(_fixture())
    build = next(s for s in suites if s.name == "build")
    cc_guide = next(s for s in suites if s.name == "cc-guide")
    assert runner.container(cc_guide, suites) == build
    assert runner.container(build, suites) is None


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_shows_selected_suite_commands_extras_and_notes(tmp_path, capsys):
    _registry(tmp_path, _fixture())
    assert runner.main(["--list", "build"], root=tmp_path) == 0
    output = capsys.readouterr().out
    assert "build" in output
    assert "cd build && uv run --python 3.13" in output
    assert "arviz>=1.0" in output
    assert "build/.scratch/" in output
    assert "brainstorming" not in output


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_defaults_to_every_suite(tmp_path, capsys):
    _registry(tmp_path, _fixture())
    assert runner.main(["--list"], root=tmp_path) == 0
    output = capsys.readouterr().out
    for row in _fixture()["suite"]:
        assert row["name"] in output
        assert row["dir"] in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_prints_the_effective_command(tmp_path, capsys):
    _registry(tmp_path, _fixture())
    assert runner.main(["--list", "build", "--extras", "--", "-k", "declared_dependencies or test_real_skill"], root=tmp_path) == 0
    output = capsys.readouterr().out
    build = next(s for s in runner.parse(_fixture()) if s.name == "build")
    expected = runner.runs(build, extras=True, pytest_args=("-k", "declared_dependencies or test_real_skill"))[0]
    assert expected.shell() in output


# spec: "A failed run does not stop the next one."
# task: 4
def test_named_runs_continue_after_pytest_exit_five(tmp_path, capsys):
    _registry(tmp_path, _fixture())
    seen = []

    def run_one(root, run):
        seen.append((run.label, capsys.readouterr().out))
        print(f"pytest output: {run.label}")
        return 5 if len(seen) == 1 else 0

    assert runner.main(["hooks", "brainstorming", "--", "-s"], root=tmp_path, run_one=run_one) == 1
    assert [label for label, _ in seen] == [
        "hooks (3.13)", "hooks (/usr/bin/python3)", "brainstorming (3.13)"
    ]
    assert all("-s" in run.argv for suite in runner.parse(_fixture()) for run in runner.runs(suite, pytest_args=("-s",)))
    first_output = seen[0][1]
    assert first_output.index("== hooks (3.13)") < first_output.index("note:")
    assert "note:" not in seen[1][1]
    tail = capsys.readouterr()
    assert "hooks (3.13)" in tail.out + tail.err


# spec: "Exit status: 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_run_exit_statuses_and_last_line(tmp_path, capsys):
    _registry(tmp_path, _single())
    for process_status, expected_status in ((0, 0), (1, 1), (5, 1)):
        result = runner.main(["brainstorming"], root=tmp_path, run_one=lambda root, run: process_status)
        output = capsys.readouterr()
        assert result == expected_status
        last_line = (output.out + output.err).strip().splitlines()[-1].lower()
        assert "passed" in last_line if expected_status == 0 else "brainstorming" in last_line


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_counts_as_a_failed_run(tmp_path, monkeypatch):
    _registry(tmp_path, _single())
    _write(tmp_path, "skills/brainstorming/scripts/test_brainstorming.py")
    monkeypatch.setenv("PATH", str(tmp_path / "empty-path"))
    assert runner.main(["brainstorming"], root=tmp_path) == 1


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_run_subprocess_inherits_opt_in_environment(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    fake_uv = _write(
        tmp_path,
        "bin/uv",
        "#!/usr/bin/env python3\n"
        "import os\nfrom pathlib import Path\n"
        "Path(os.environ['RUNNER_CAPTURE']).write_text("
        "os.environ['CALIBRATION_SWEEP'] + '\\n' + "
        "os.environ['RUNNER_ENV_SENTINEL'] + '\\n' + os.getcwd())\n",
    )
    fake_uv.chmod(0o755)
    capture = tmp_path / "capture.txt"
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setenv("RUNNER_CAPTURE", str(capture))
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("RUNNER_ENV_SENTINEL", "unchanged")
    _write(tmp_path, "skills/brainstorming/scripts/test_brainstorming.py")
    run = runner.runs(runner.parse(_single())[0])[0]
    assert runner.run_subprocess(tmp_path, run) == 0
    assert capture.read_text().splitlines() == [
        "1", "unchanged", str(tmp_path / "skills/brainstorming/scripts")
    ]


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_cli_lists_from_an_unrelated_working_directory(tmp_path):
    assert runner.REPO == REPO
    result = subprocess.run(
        [sys.executable, str(REPO / "build/run_suites.py"), "--list", "cc-guide"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "cc-guide" in result.stdout
    assert "build/cc_guide" in result.stdout


# spec: "Exit status: 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_cli_rejects_unknown_suite_and_bad_usage(tmp_path):
    script = str(REPO / "build/run_suites.py")
    for args in (["no-such-suite"], ["--no-such-option"]):
        result = subprocess.run([sys.executable, script, *args], cwd=tmp_path, capture_output=True, text=True)
        assert result.returncode == 2, (args, result.stdout, result.stderr)


# spec: "`--all` prints one line for each suite that it skips."
# task: 4
def test_all_skips_the_nested_cc_guide_once(tmp_path, capsys):
    _registry(tmp_path, _fixture())
    seen = []
    assert runner.main(["--all"], root=tmp_path, run_one=lambda root, run: seen.append(run.suite.name) or 0) == 0
    assert seen == ["brainstorming", "build", "hooks", "hooks"]
    output = capsys.readouterr().out
    assert len([line for line in output.splitlines() if "cc-guide" in line and "skip" in line.lower()]) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_named_nested_suite_runs(tmp_path):
    _registry(tmp_path, _fixture())
    seen = []
    assert runner.main(["cc-guide"], root=tmp_path, run_one=lambda root, run: seen.append(run.suite.name) or 0) == 0
    assert seen == ["cc-guide"]


# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_check_finds_both_unregistered_pytest_filename_patterns(tmp_path):
    _valid_git_root(tmp_path)
    for filename in ("test_new.py", "new_test.py"):
        path = _write(tmp_path, f"skills/tune-hyperparameters/scripts/{filename}")
        findings = runner.check(tmp_path, _single())
        assert any("skills/tune-hyperparameters/scripts" in finding for finding in findings)
        path.unlink()


# spec: "a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_finds_a_missing_registered_directory(tmp_path):
    _git(tmp_path)
    findings = runner.check(tmp_path, _single())
    assert any("skills/brainstorming/scripts" in finding for finding in findings)


# spec: "a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_finds_a_registered_directory_without_tests(tmp_path):
    _git(tmp_path)
    _write(tmp_path, "skills/brainstorming/scripts/README.md", "No tests here.")
    findings = runner.check(tmp_path, _single())
    assert any("skills/brainstorming/scripts" in finding for finding in findings)


# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_nested_test_directory_is_covered_by_its_outer_suite(tmp_path):
    _git(tmp_path)
    data = {"suite": [_row("build", "build", ["pytest"])]}
    _write(tmp_path, "build/cc_guide/test_docs.py")
    assert runner.check(tmp_path, data) == []


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_check_ignores_gitignored_worktrees_and_scratch(tmp_path):
    _valid_git_root(tmp_path)
    _write(tmp_path, ".gitignore", ".claude/worktrees/\nbuild/.scratch/\n")
    _write(tmp_path, ".claude/worktrees/example/test_new.py")
    _write(tmp_path, "build/.scratch/example/test_new.py")
    assert runner.check(tmp_path, _single()) == []


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_check_sees_untracked_new_suite_files(tmp_path):
    _valid_git_root(tmp_path)
    _write(tmp_path, "skills/tune-hyperparameters/scripts/test_new.py")
    assert any(
        "skills/tune-hyperparameters/scripts" in finding
        for finding in runner.check(tmp_path, _single())
    )


# spec: "If git fails, `--check` fails."
# task: 4
def test_check_fails_outside_a_git_repository(tmp_path):
    _registry(tmp_path, _single())
    _write(tmp_path, "skills/brainstorming/scripts/test_brainstorming.py")
    assert runner.main(["--check"], root=tmp_path) == 1


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_cli_success_and_single_coverage_finding(tmp_path, capsys):
    _valid_git_root(tmp_path)
    assert runner.main(["--check"], root=tmp_path) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"
    _write(tmp_path, "skills/tune-hyperparameters/scripts/test_new.py")
    assert runner.main(["--check"], root=tmp_path) == 1
    output = capsys.readouterr()
    lines = [line for line in (output.out + output.err).splitlines() if line.strip()]
    assert len(lines) == 1
    assert "skills/tune-hyperparameters/scripts" in lines[0]


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 4
def test_check_reports_registry_validation_as_a_finding(tmp_path, capsys):
    _valid_git_root(tmp_path)
    _registry(tmp_path, _bad("unknown_key"))
    assert runner.main(["--check"], root=tmp_path) == 1
    output = capsys.readouterr()
    assert "build/suites.toml" in output.out + output.err
    assert "suite registry ok" not in output.out + output.err


# spec: "The real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_passes_check(capsys):
    assert runner.main(["--check"], root=REPO) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_commit_lint_script_has_ninth_registry_check():
    text = (REPO / "build/run_commit_lints.sh").read_text()
    run_lines = re.findall(r"(?m)^\s*run\s+\S+.*$", text)
    assert len(run_lines) == 9
    assert run_lines[-1].strip() == (
        "run suite_registry uv run --python 3.13 python build/run_suites.py --check"
    )
    assert "nine" in "\n".join(text.splitlines()[:15]).lower()
    assert sum("build/run_suites.py" in line for line in run_lines) == 1


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_guide_intro_retains_rules_and_points_to_registry():
    lines = (REPO / "CLAUDE.md").read_text().splitlines()
    assert any(
        all(token in line for token in ("uv", "3.13", "test_build.py", "build/suites.toml", "build/run_suites.py", "notes"))
        and re.search(r"directory|directories", line, re.I)
        and re.search(r"basename|collid", line, re.I)
        for line in lines
    )
    assert "There is no root test runner" not in "\n".join(lines)


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_guide_has_four_runner_commands_in_order():
    lines = (REPO / "CLAUDE.md").read_text().splitlines()
    commands = [line for line in lines if "python build/run_suites.py" in line]
    assert len(commands) == 4
    for line, token in zip(commands, ("--list", "<name>", "--all", "--check"), strict=True):
        assert "uv run --python 3.13 python build/run_suites.py" in line
        assert token in line
    assert "--extras" in commands[1]
    assert "-- <pytest args>" in commands[1]


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_selected_tests_and_tools_remain_in_root_guide():
    text = (REPO / "CLAUDE.md").read_text()
    for token in (
        "test_runtime_support.py", "test_commit_lints.py", "declared_dependencies",
        "test_real_skill", "test_check_jax_examples.py", "Single test",
        "verify_citations.py", "extract_structure.py", "cli.py lint", "cli.py check",
    ):
        assert token in text


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_guide_has_no_whole_directory_pytest_command():
    lines = (REPO / "CLAUDE.md").read_text().splitlines()
    assert len(lines) < 200
    for line in lines:
        if line.lstrip().startswith("cd ") and "python -m pytest -q" in line:
            after_q = line.split("python -m pytest -q", 1)[1].strip()
            assert after_q and not after_q.startswith("&&"), line


# spec: "The comment names the suite `run_suites.py cc-guide` instead of \"its suite\"."
# task: 7
def test_cc_guide_comment_names_the_runner_suite():
    text = (REPO / "CLAUDE.md").read_text()
    assert "run_suites.py cc-guide" in text
    assert "cd build/cc_guide &&" not in text


# spec: "`build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_guide_documents_the_ninth_lint():
    text = (REPO / "build/CLAUDE.md").read_text()
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    assert all(token in text for token in ("suites.toml", "run_suites.py", "--check", "commit lint"))


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_cc_guide_stamp_and_conformance_positive_control():
    first_line = (REPO / "CLAUDE.md").read_text().splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .+ @[^ >]+ -->", first_line)
    source = (REPO / "build/test_check_conformance.py").read_text()
    tree = ast.parse(source)
    function = next(
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    body = ast.get_source_segment(source, function)
    assert "cc-guide" in body
    assert "@needs_pilot" not in body


# spec: "`build/test_run_suites.py`, stdlib and pytest only, which the build suite collects."
# task: 2
def test_runner_test_module_exists_without_third_party_dependencies():
    source = (REPO / "build/test_run_suites.py").read_text()
    tree = ast.parse(source)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
    assert set(imports) <= sys.stdlib_module_names | {"pytest", "build", "run_suites"}
    assert any(isinstance(node, ast.FunctionDef) and node.name.startswith("test_") for node in tree.body)


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_registry_and_clone_regression_test_exist():
    from build import test_commit_lints

    assert "suite_registry" in str(test_commit_lints.CHECKS)
    source = (REPO / "build/test_commit_lints.py").read_text()
    tree = ast.parse(source)
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_unregistered_suite_is_refused"
    )
    body = ast.get_source_segment(source, function)
    assert "test_new.py" in body
    assert "suite_registry" in body


# spec: "`bash build/run_commit_lints.sh` prints `commit lints passed`."
# task: 6
def test_commit_lint_gate_passes():
    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "commit lints passed" in output
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`</plan></flag>
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
Worktree-isolated sessions and their subagents have refused compound shell such as `cd X && Y` (seen on 2026-10-12).
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
Rejected: a Python list inside the runner (every suite change becomes a code edit), and one manifest per suite directory (`install.py` copies skill directories, so the manifests would ship with installed skills).
An `@`-imported document was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
Design section 1 (the registry keys and the runner's behaviour) was approved as presented.
Design section 2 (the guard, the file edits, the tests and the couplings) was approved as presented.
The entries carry the text of today's commands and comments.
Every command, dependency and note survives; the only change is the form.
With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character.
The deletion of lines 66–125 is bounded by two lines that no other plan edits: the `# Full build-directory tests` comment and the `cd hooks && …` command.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
The new files are the owner's original tooling.
The register's deviation `claude-md-serves-codex-gemini` still holds as written: a condensed Commands block stays in the root file, and the registry is a plain file that every runtime can read.
Write each test before its code and see it fail first (red, then green).
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
It extracts every `cd <dir> && uv run …` command from lines 66–125 and 145, splitting the hooks `&&` chain into one command per run.
It asserts that the set equals the set of default shell forms that `--list` prints: nothing is missing on either side.
It also checks each comment's skip-unlocking deps against that suite's `extras`.
Run `hooks`, `build` and `bayesian-workflow` once directly and once through the runner, in the same checkout.
Their pytest summary lines match.
Then run `--all` once, and record each run's result beside the direct result.
The Stage 2 audit passes, and the behaviour runs match.
The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
The commit hook runs one more fast, stdlib-only check.
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
</untestable>