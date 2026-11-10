<tests>
import ast
import copy
import os
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from build import run_suites as runner


FIXTURE = """
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
notes = ["the guard's 3.9 floor"]
"""


def fixture_data():
    return tomllib.loads(FIXTURE)


def fixture_root(root):
    registry = root / runner.REGISTRY
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(FIXTURE)
    for entry in fixture_data()["suite"]:
        (root / entry["dir"]).mkdir(parents=True, exist_ok=True)
    return root


def git_root(root):
    fixture_root(root)
    (root / ".gitignore").write_text(".claude/worktrees/\nbuild/.scratch/\n")
    for directory in ("build", "build/cc_guide", "hooks"):
        (root / directory / "test_existing.py").write_text("def test_existing(): pass\n")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    return root


def suite(name):
    return next(item for item in runner.parse(fixture_data()) if item.name == name)


def imported_roots(path):
    tree = ast.parse(path.read_text())
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
def test_validation_rejects_every_listed_schema_error():
    bad_data = []
    for key in ("name", "dir", "with"):
        data = fixture_data()
        del data["suite"][0][key]
        bad_data.append(data)

    for key, value in (
        ("name", 3),
        ("dir", 3),
        ("with", "pytest"),
        ("with", ["pytest", 3]),
        ("extras", "numpy"),
        ("pythons", [3.13]),
        ("notes", [3]),
    ):
        data = fixture_data()
        data["suite"][0][key] = value
        bad_data.append(data)

    data = fixture_data()
    data["suite"][0]["pthons"] = ["3.13"]
    bad_data.append(data)

    data = fixture_data()
    data["suite"][0]["with"] = ["numpy"]
    bad_data.append(data)

    data = fixture_data()
    data["suite"][1]["name"] = "build"
    bad_data.append(data)

    data = fixture_data()
    data["suite"][1]["dir"] = "build"
    bad_data.append(data)

    for data in bad_data:
        assert runner.validate(data), data


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_invalid_registry_stops_each_command_before_running(tmp_path):
    fixture_root(tmp_path)
    text = FIXTURE.replace('pythons = ["3.13", "/usr/bin/python3"]', 'pthons = ["3.13"]')
    (tmp_path / runner.REGISTRY).write_text(text)
    called = []

    def run_one(root, run):
        called.append(run)
        return 0

    for argv in (["--list"], ["build"], ["--all"]):
        assert runner.main(argv, root=tmp_path, run_one=run_one) == 2
    assert called == []


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_has_the_specified_directory_suites_in_name_order():
    with (runner.REPO / runner.REGISTRY).open("rb") as file:
        entries = tomllib.load(file)["suite"]

    expected = {
        "bayesian-workflow": ("skills/bayesian-workflow/scripts", ["arviz", "arviz-stats", "numpy", "xarray"], ["matplotlib"]),
        "brainstorming": ("skills/brainstorming/scripts", [], []),
        "build": ("build", ["numpy", "polars", "pyyaml"], ["arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots", "numpyro", "jax", "matplotlib"]),
        "cc-guide": ("build/cc_guide", [], []),
        "classification-codes": ("skills/classification-codes/scripts", ["polars"], []),
        "describe-critique-methodology": ("skills/describe-critique-methodology/scripts", [], []),
        "design-architecture": ("skills/design-architecture/scripts", [], []),
        "explore-data": ("skills/explore-data/scripts", ["polars"], []),
        "geographic-codes": ("skills/geographic-codes/scripts", ["polars", "fastexcel"], []),
        "hooks": ("hooks", [], []),
        "llm-wiki": ("skills/llm-wiki/scripts", [], []),
        "recommend-probabilistic-model": ("skills/recommend-probabilistic-model/scripts", ["numpy", "polars"], []),
        "recommend-visualization": ("skills/recommend-visualization/scripts", ["numpy", "polars"], []),
        "subagent-driven-development": ("skills/subagent-driven-development/scripts", [], []),
        "systematic-debugging": ("skills/systematic-debugging", [], []),
        "track-model-experiments": ("skills/track-model-experiments/scripts", ["numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"], []),
        "tune-hyperparameters": ("skills/tune-hyperparameters/scripts", ["numpy", "polars"], ["scikit-learn", "optuna"]),
        "writing-plans": ("skills/writing-plans/scripts", [], []),
    }
    names = [entry["name"] for entry in entries]
    assert names == sorted(names)
    assert set(expected) <= set(names)
    assert set(names) - set(expected) <= {"write-with-asd-ste100"}
    by_name = {entry["name"]: entry for entry in entries}
    for name, (directory, dependencies, extras) in expected.items():
        entry = by_name[name]
        assert entry["dir"] == directory
        assert entry["with"] == ["pytest", *dependencies]
        assert entry.get("extras", []) == extras
        assert entry.get("pythons", ["3.13"]) == (
            ["3.13", "/usr/bin/python3"] if name == "hooks" else ["3.13"]
        )


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_explains_its_schema_order_and_lint():
    text = (runner.REPO / runner.REGISTRY).read_text()
    header = text.split("[[suite]]", 1)[0]
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert re.search(rf"\b{key}\b", header)
    assert re.search(r"sort", header, re.IGNORECASE)
    assert re.search(r"\b(ninth|nine|9th)\b", header, re.IGNORECASE)
    assert re.search(r"commit lint", header, re.IGNORECASE)


# spec: "The notes carry the rest of each comment."
# task: 5
def test_registry_notes_include_the_specified_operational_details():
    with (runner.REPO / runner.REGISTRY).open("rb") as file:
        entries = {entry["name"]: entry for entry in tomllib.load(file)["suite"]}
    expected_fragments = {
        "build": ("build/.scratch/",),
        "bayesian-workflow": ("CALIBRATION_SWEEP=1", "arviz", "warn"),
        "llm-wiki": ("@needs_pilot", "LLM_WIKI_ROOT"),
        "brainstorming": ("node", "skip"),
        "tune-hyperparameters": ("sklearn", "fail"),
        "track-model-experiments": ("run time",),
        "hooks": ("3.9", "launchd", "Gate B"),
    }
    for name, fragments in expected_fragments.items():
        notes = " ".join(entries[name].get("notes", [])).lower()
        for fragment in fragments:
            assert fragment.lower() in notes, (name, fragment)


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_imports_only_standard_library_modules():
    roots = imported_roots(runner.REPO / "build/run_suites.py")
    assert roots <= sys.stdlib_module_names | {"__future__"}


# spec: "One run is one interpreter of one suite."
# task: 2
def test_default_runs_use_python_313_and_the_listed_dependencies():
    result = runner.runs(suite("build"))
    assert len(result) == 1
    assert result[0].python == "3.13"
    assert result[0].argv == (
        "uv", "run", "--python", "3.13",
        "--with", "pytest",
        "--with", "numpy",
        "--with", "polars",
        "--with", "pyyaml",
        "python", "-m", "pytest", "-q",
    )


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 2
def test_hooks_produces_two_independent_shell_commands():
    result = runner.runs(suite("hooks"))
    assert [run.python for run in result] == ["3.13", "/usr/bin/python3"]
    assert [run.shell() for run in result] == [
        "cd hooks && uv run --python 3.13 --with pytest python -m pytest -q",
        "cd hooks && uv run --python /usr/bin/python3 --with pytest python -m pytest -q",
    ]


# spec: "`--extras` adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_follow_default_dependencies_in_the_specified_order():
    default = runner.runs(suite("build"))[0].argv
    with_extras = runner.runs(suite("build"), extras=True)[0].argv
    assert with_extras[: len(default) - 4] == default[: len(default) - 4]
    assert with_extras[len(default) - 4 : -4] == (
        "--with", "arviz>=1.0",
        "--with", "arviz-base",
        "--with", "arviz-stats",
        "--with", "arviz-plots",
        "--with", "numpyro",
        "--with", "jax",
        "--with", "matplotlib",
    )
    assert with_extras[-4:] == default[-4:]


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_pytest_arguments_reach_every_interpreter(tmp_path):
    fixture_root(tmp_path)
    seen = []

    def run_one(root, run):
        seen.append(run.argv)
        return 0

    assert runner.main(
        ["hooks", "--", "test_hooks.py::test_one", "-k", "declared_dependencies", "-s", "-rs"],
        root=tmp_path,
        run_one=run_one,
    ) == 0
    assert len(seen) == 2
    for argv in seen:
        assert argv[-5:] == (
            "test_hooks.py::test_one", "-k", "declared_dependencies", "-s", "-rs"
        )


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_a_pytest_argument_containing_spaces():
    run = runner.runs(
        suite("build"), pytest_args=("test file.py::test case",)
    )[0]
    assert run.shell() == "cd build && " + shlex.join(run.argv)
    assert "'test file.py::test case'" in run.shell()


# spec: "`--list [NAME …]` prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_prints_selected_suite_commands_extras_and_notes(tmp_path, capsys):
    fixture_root(tmp_path)
    assert runner.main(
        ["--list", "build", "--extras", "--", "-s"], root=tmp_path
    ) == 0
    output = capsys.readouterr().out
    expected = runner.runs(suite("build"), extras=True, pytest_args=("-s",))[0]
    assert "build" in output
    assert expected.shell() in output
    assert "arviz>=1.0" in output
    assert "build/.scratch/" in output
    assert "cd hooks" not in output


# spec: "`--list [NAME …]` prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_without_names_includes_every_fixture_suite(tmp_path, capsys):
    fixture_root(tmp_path)
    assert runner.main(["--list"], root=tmp_path) == 0
    output = capsys.readouterr().out
    for directory in ("build", "build/cc_guide", "hooks"):
        assert f"cd {directory} &&" in output


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_precede_runs_and_notes_print_once(tmp_path, capsys):
    fixture_root(tmp_path)
    observed = []

    def run_one(root, run):
        observed.append((run.label, capsys.readouterr().out))
        return 0

    assert runner.main(["hooks"], root=tmp_path, run_one=run_one) == 0
    assert [label for label, _ in observed] == [
        "hooks (3.13)", "hooks (/usr/bin/python3)"
    ]
    assert "== hooks (3.13)" in observed[0][1]
    assert "3.9 floor" in observed[0][1]
    assert "== hooks (/usr/bin/python3)" in observed[1][1]
    assert "3.9 floor" not in observed[1][1]


# spec: "A failed run does not stop the next one."
# task: 4
def test_failure_does_not_stop_later_interpreters_or_suites(tmp_path, capsys):
    fixture_root(tmp_path)
    seen = []

    def run_one(root, run):
        seen.append(run.label)
        return 1 if run.label == "hooks (3.13)" else 0

    assert runner.main(["hooks", "build"], root=tmp_path, run_one=run_one) == 1
    assert seen == ["hooks (3.13)", "hooks (/usr/bin/python3)", "build (3.13)"]
    assert "hooks (3.13)" in capsys.readouterr().err.splitlines()[-1]


# spec: "`--all` runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_skips_nested_suite_and_prints_one_skip_line(tmp_path, capsys):
    fixture_root(tmp_path)
    seen = []

    def run_one(root, run):
        seen.append(run.label)
        return 0

    assert runner.main(["--all"], root=tmp_path, run_one=run_one) == 0
    assert seen == ["build (3.13)", "hooks (3.13)", "hooks (/usr/bin/python3)"]
    skip_lines = [
        line for line in capsys.readouterr().out.splitlines()
        if "skip" in line.lower() and "cc-guide" in line
    ]
    assert len(skip_lines) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_named_nested_suite_runs(tmp_path):
    fixture_root(tmp_path)
    seen = []

    def run_one(root, run):
        seen.append(run.label)
        return 0

    assert runner.main(["cc-guide"], root=tmp_path, run_one=run_one) == 0
    assert seen == ["cc-guide (3.13)"]


# spec: "Exit status: 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_exit_statuses_include_pytest_exit_five_and_unknown_name(tmp_path):
    fixture_root(tmp_path)
    assert runner.main(
        ["build"], root=tmp_path, run_one=lambda root, run: 0
    ) == 0
    assert runner.main(
        ["build"], root=tmp_path, run_one=lambda root, run: 5
    ) == 1
    assert runner.main(["not-a-suite"], root=tmp_path) == 2
    assert runner.main([], root=tmp_path) == 2


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_unstartable_uv_counts_as_a_failed_run(tmp_path):
    fixture_root(tmp_path)

    def cannot_start(root, run):
        raise FileNotFoundError("uv")

    assert runner.main(["build"], root=tmp_path, run_one=cannot_start) == 1


# spec: "The last line names the failed runs, or says that every run passed."
# task: 4
def test_final_summary_reports_passes_and_failed_run_labels(tmp_path, capsys):
    fixture_root(tmp_path)
    assert runner.main(
        ["build"], root=tmp_path, run_one=lambda root, run: 0
    ) == 0
    passed = capsys.readouterr()
    assert "passed" in passed.out.splitlines()[-1].lower()

    assert runner.main(
        ["build"], root=tmp_path, run_one=lambda root, run: 1
    ) == 1
    failed = capsys.readouterr()
    assert "build (3.13)" in failed.err.splitlines()[-1]


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_receives_environment_and_uses_suite_directory(tmp_path, monkeypatch):
    fixture_root(tmp_path)
    executable_dir = tmp_path / "bin"
    executable_dir.mkdir()
    uv = executable_dir / "uv"
    uv.write_text(
        "#!/bin/sh\n"
        "{ pwd; printf '%s\\n' \"$CALIBRATION_SWEEP\" \"$RUNNER_SENTINEL\"; } > \"$RUNNER_CAPTURE\"\n"
    )
    uv.chmod(0o755)
    capture = tmp_path / "captured.txt"
    monkeypatch.setenv("PATH", str(executable_dir) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("RUNNER_SENTINEL", "value with spaces")
    monkeypatch.setenv("RUNNER_CAPTURE", str(capture))

    assert runner.run_subprocess(tmp_path, runner.runs(suite("build"))[0]) == 0
    assert capture.read_text().splitlines() == [
        str(tmp_path / "build"), "1", "value with spaces"
    ]


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 2
def test_repo_root_is_derived_from_runner_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert runner.REPO == Path(runner.__file__).resolve().parents[1]


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_check_finds_both_pytest_filename_patterns(tmp_path):
    root = git_root(tmp_path)
    directory = root / "skills/new-suite/scripts"
    directory.mkdir(parents=True)
    for filename in ("test_new.py", "new_test.py"):
        path = directory / filename
        path.write_text("def test_new(): pass\n")
        assert (
            "skills/new-suite/scripts: holds pytest files, but no suite in build/suites.toml contains it"
            in runner.check(root, fixture_data())
        )
        path.unlink()


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_reports_missing_registered_directory(tmp_path):
    root = git_root(tmp_path)
    data = fixture_data()
    data["suite"].append({
        "name": "writing-plans",
        "dir": "skills/writing-plans/scripts",
        "with": ["pytest"],
    })
    assert any(
        "skills/writing-plans/scripts" in line for line in runner.check(root, data)
    )


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_reports_registered_directory_without_tests(tmp_path):
    root = git_root(tmp_path)
    (root / "skills/writing-plans/scripts").mkdir(parents=True)
    data = fixture_data()
    data["suite"].append({
        "name": "writing-plans",
        "dir": "skills/writing-plans/scripts",
        "with": ["pytest"],
    })
    assert any(
        "skills/writing-plans/scripts" in line for line in runner.check(root, data)
    )


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_check_ignores_tests_in_git_ignored_trees(tmp_path):
    root = tmp_path
    (root / "build").mkdir()
    (root / "hooks").mkdir()
    (root / "build/suites.toml").write_text(
        '[[suite]]\nname = "hooks"\ndir = "hooks"\nwith = ["pytest"]\n'
    )
    (root / "hooks/test_existing.py").write_text("def test_existing(): pass\n")
    (root / ".gitignore").write_text(".claude/worktrees/\nbuild/.scratch/\n")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    for directory in (".claude/worktrees/one", "build/.scratch/one"):
        path = root / directory / "test_ignored.py"
        path.parent.mkdir(parents=True)
        path.write_text("def test_ignored(): pass\n")

    with (root / "build/suites.toml").open("rb") as file:
        data = tomllib.load(file)
    assert runner.check(root, data) == []


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_check_finds_an_untracked_new_suite(tmp_path):
    root = git_root(tmp_path)
    path = root / "skills/new-suite/scripts/test_new.py"
    path.parent.mkdir(parents=True)
    path.write_text("def test_new(): pass\n")
    status = subprocess.run(
        ["git", "status", "--short", "--", str(path.relative_to(root))],
        cwd=root, check=True, capture_output=True, text=True,
    )
    assert status.stdout.startswith("??")
    assert any(
        "skills/new-suite/scripts" in line
        for line in runner.check(root, fixture_data())
    )


# spec: "If git fails, `--check` fails."
# task: 4
def test_check_fails_outside_a_git_repository(tmp_path):
    fixture_root(tmp_path)
    assert runner.main(["--check"], root=tmp_path) == 1


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_prints_success_or_each_finding(tmp_path, capsys):
    root = git_root(tmp_path)
    assert runner.main(["--check"], root=root) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"

    path = root / "skills/new-suite/scripts/test_new.py"
    path.parent.mkdir(parents=True)
    path.write_text("def test_new(): pass\n")
    assert runner.main(["--check"], root=root) == 1
    output = capsys.readouterr()
    assert "skills/new-suite/scripts" in output.out + output.err


# spec: "The real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_passes_check(capsys):
    assert runner.main(["--check"], root=runner.REPO) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_commit_lint_script_has_nine_runs_and_suite_registry_last():
    text = (runner.REPO / "build/run_commit_lints.sh").read_text()
    commands = re.findall(r"(?m)^run [^\n]+$", text)
    assert len(commands) == 9
    assert commands[-1] == (
        "run suite_registry uv run --python 3.13 "
        "python build/run_suites.py --check"
    )
    assert sum("run_suites.py" in command for command in commands) == 1
    assert re.search(r"\bnine\b", text.split("\n", 5)[0] + "\n" + text.split("\n", 5)[1], re.IGNORECASE)


# spec: "`build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_unregistered_committed_suite_fails_only_suite_registry_lint(tmp_path):
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "--no-hardlinks", "-q", str(runner.REPO), str(clone)],
        check=True,
    )
    test_file = clone / "skills/new-suite/scripts/test_new.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_new(): pass\n")
    subprocess.run(["git", "add", str(test_file.relative_to(clone))], cwd=clone, check=True)
    subprocess.run(
        [
            "git", "-c", "user.name=Acceptance Test",
            "-c", "user.email=acceptance@example.invalid",
            "commit", "-qm", "Add an unregistered suite",
        ],
        cwd=clone, check=True,
    )

    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=clone, capture_output=True, text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert "skills/new-suite/scripts" in output
    assert "suite_registry" in output
    script = (clone / "build/run_commit_lints.sh").read_text()
    lint_names = re.findall(r"(?m)^run ([a-z_][a-z_0-9]*)\b", script)
    for line in output.splitlines():
        if re.search(r"\bfail(?:ed|ure)?\b", line, re.IGNORECASE):
            named = [name for name in lint_names if re.search(rf"\b{name}\b", line)]
            assert not named or named == ["suite_registry"]


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_claude_md_is_short_and_has_no_directory_suite_command():
    text = (runner.REPO / "CLAUDE.md").read_text()
    assert len(text.splitlines()) < 200
    with (runner.REPO / runner.REGISTRY).open("rb") as file:
        suites = runner.parse(tomllib.load(file))
    for item in suites:
        for run in runner.runs(item):
            assert run.shell() not in text


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_selected_tests_and_other_tools_stay_in_root_claude_md():
    text = (runner.REPO / "CLAUDE.md").read_text()
    for fragment in (
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
        assert fragment in text


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_claude_md_shows_all_four_runner_forms():
    text = (runner.REPO / "CLAUDE.md").read_text()
    for fragment in (
        "build/run_suites.py --list",
        "build/run_suites.py <name> [--extras] [-- <pytest args>]",
        "build/run_suites.py --all",
        "build/run_suites.py --check",
    ):
        assert fragment in text


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_claude_md_intro_retains_execution_and_collision_guidance():
    text = (runner.REPO / "CLAUDE.md").read_text()
    intro_lines = [line for line in text.splitlines() if "test_build.py" in line]
    assert len(intro_lines) == 1
    intro = intro_lines[0]
    for fragment in ("uv", "3.13", "directory", "build/suites.toml", "build/run_suites.py"):
        assert fragment in intro
    assert re.search(r"collision|same basename", intro, re.IGNORECASE)
    assert "There is no root test runner" not in text


# spec: "The comment names the suite `run_suites.py cc-guide` instead of "its suite"."
# task: 7
def test_cc_guide_comment_names_the_runner_suite():
    text = (runner.REPO / "CLAUDE.md").read_text()
    assert "run_suites.py cc-guide" in text
    assert "cd build/cc_guide &&" not in text


# spec: "`build/CLAUDE.md`: "the eight commit lints" becomes "the nine commit lints", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_claude_md_describes_the_ninth_lint():
    text = (runner.REPO / "build/CLAUDE.md").read_text()
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    assert "suites.toml" in text
    assert "run_suites.py" in text
    assert "--check" in text


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_root_stamp_is_first_line_and_old_positive_control_is_gone():
    first_line = (runner.REPO / "CLAUDE.md").read_text().splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .+ @[^ >]+ -->", first_line)
    source = (runner.REPO / "build/test_check_conformance.py").read_text()
    marker = "def test_claude_md_import_resolves_passes_on_the_repo"
    assert marker in source
    function_source = source.split(marker, 1)[1].split("\ndef ", 1)[0]
    assert "'@needs_pilot' in text" not in function_source
    assert "@needs_pilot" not in (runner.REPO / "CLAUDE.md").read_text()


# spec: "`build/test_run_suites.py`, stdlib and pytest only, which the build suite collects."
# task: 2
def test_planned_runner_tests_are_collectable_and_use_only_allowed_imports():
    path = runner.REPO / "build/test_run_suites.py"
    assert path.is_file()
    assert imported_roots(path) <= sys.stdlib_module_names | {
        "__future__", "pytest", "build", "run_suites"
    }


# spec: "`bash build/run_commit_lints.sh` prints `commit lints passed`."
# task: 6
def test_commit_lint_gate_passes_on_the_repo():
    result = subprocess.run(
        ["bash", "build/run_commit_lints.sh"],
        cwd=runner.REPO, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "commit lints passed" in result.stdout + result.stderr
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`</plan></flag>
<flag task="2"><spec>Default `['3.13']`.</spec><plan>DEFAULT_PYTHONS = ('3.12',)</plan></flag>
<flag task="5"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>`cc_guide`</plan></flag>
</flags>
<untestable>
`CLAUDE.md` had 199 on `main` at `456e3fb`.
Its Commands block spends lines 66–125, 60 lines, on one `cd <dir> && uv run … python -m pytest -q` command and comment per suite.
Each new suite costs two or three more lines.
Plan 50 (the superpowers upstream fixes, lowmason/agent-skills#56) took the file from 195 to 199.
Plan 52 (the write-with-asd-ste100 skill, not merged) needs two more lines.
In plan 38, Task 2 condensed `CLAUDE.md` from 224 lines to 170 and kept every command in place.
The file then grew back to 199 by 2026-10-18.
Worktree-isolated sessions and their subagents have refused compound shell such as `cd X && Y` (seen on 2026-10-12).
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
Every command, dependency and note survives; the only change is the form.
With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character.
The file ends at about 145 lines.
Same number of lines.
Line 133 is not touched (plan 53's Task 7 edits it).
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
The new files are the owner's original tooling.
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
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
</untestable>