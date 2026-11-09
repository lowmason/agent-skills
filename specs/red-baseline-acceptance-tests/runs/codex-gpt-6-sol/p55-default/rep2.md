<tests>
import ast
import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

from build import run_suites as runner


EXPECTED = {
    "bayesian-workflow": ("skills/bayesian-workflow/scripts", ("arviz", "arviz-stats", "numpy", "xarray"), ("matplotlib",), ("3.13",)),
    "brainstorming": ("skills/brainstorming/scripts", (), (), ("3.13",)),
    "build": ("build", ("numpy", "polars", "pyyaml"), ("arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots", "numpyro", "jax", "matplotlib"), ("3.13",)),
    "cc-guide": ("build/cc_guide", (), (), ("3.13",)),
    "classification-codes": ("skills/classification-codes/scripts", ("polars",), (), ("3.13",)),
    "describe-critique-methodology": ("skills/describe-critique-methodology/scripts", (), (), ("3.13",)),
    "design-architecture": ("skills/design-architecture/scripts", (), (), ("3.13",)),
    "explore-data": ("skills/explore-data/scripts", ("polars",), (), ("3.13",)),
    "geographic-codes": ("skills/geographic-codes/scripts", ("polars", "fastexcel"), (), ("3.13",)),
    "hooks": ("hooks", (), (), ("3.13", "/usr/bin/python3")),
    "llm-wiki": ("skills/llm-wiki/scripts", (), (), ("3.13",)),
    "recommend-probabilistic-model": ("skills/recommend-probabilistic-model/scripts", ("numpy", "polars"), (), ("3.13",)),
    "recommend-visualization": ("skills/recommend-visualization/scripts", ("numpy", "polars"), (), ("3.13",)),
    "subagent-driven-development": ("skills/subagent-driven-development/scripts", (), (), ("3.13",)),
    "systematic-debugging": ("skills/systematic-debugging", (), (), ("3.13",)),
    "track-model-experiments": ("skills/track-model-experiments/scripts", ("numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"), (), ("3.13",)),
    "tune-hyperparameters": ("skills/tune-hyperparameters/scripts", ("numpy", "polars"), ("scikit-learn", "optuna"), ("3.13",)),
    "writing-plans": ("skills/writing-plans/scripts", (), (), ("3.13",)),
}


def _fixture_entries():
    return [
        {
            "name": "build",
            "dir": "build",
            "with": ["pytest", "numpy", "polars", "pyyaml"],
            "extras": ["arviz>=1.0", "arviz-base", "arviz-stats", "arviz-plots", "numpyro", "jax", "matplotlib"],
            "notes": ["build/.scratch/ may be missing in a fresh clone"],
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
            "notes": ["3.9 floor; launchd-PATH skips; Gate B probe"],
        },
    ]


def _write(root, relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def _write_registry(root, entries):
    lines = []
    for entry in entries:
        lines.append("[[suite]]")
        for key, value in entry.items():
            lines.append(f"{key} = {json.dumps(value)}")
        lines.append("")
    _write(root, "build/suites.toml", "\n".join(lines))


def _data(root):
    return tomllib.loads((root / "build/suites.toml").read_text())


def _git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _workspace(root, *, tracked=False):
    _write_registry(root, _fixture_entries())
    _write(root, "build/test_build.py", "def test_build(): assert True\n")
    _write(root, "build/cc_guide/test_guide.py", "def test_guide(): assert True\n")
    _write(root, "hooks/test_hooks.py", "def test_hooks(): assert True\n")
    if tracked:
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
        _git(root, "add", ".")
    return root


def _real_data():
    return _data(runner.REPO)


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_has_exact_suite_inventory_and_order():
    rows = _real_data()["suite"]
    assert [row["name"] for row in rows] == sorted(EXPECTED)
    assert set(row["name"] for row in rows) == set(EXPECTED)
    for row in rows:
        directory, dependencies, extras, pythons = EXPECTED[row["name"]]
        assert row["dir"] == directory
        assert row["with"] == ["pytest", *dependencies]
        assert row.get("extras", []) == list(extras)
        assert row.get("pythons", ["3.13"]) == list(pythons)


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_explains_its_schema_and_guard():
    text = (runner.REPO / "build/suites.toml").read_text()
    header = text.split("[[suite]]", 1)[0]
    assert header.strip()
    assert all(line.lstrip().startswith("#") for line in header.splitlines() if line.strip())
    assert all(re.search(rf"\b{key}\b", header) for key in ("name", "dir", "with", "extras", "pythons", "notes"))
    assert "sort" in header.lower()
    assert re.search(r"\b(ninth|nine|9th)\b", header.lower())
    assert "commit lint" in header.lower()


# spec: "The notes carry the rest of each comment."
# task: 5
def test_registry_notes_include_specified_operational_details():
    notes = {
        row["name"]: " ".join(row.get("notes", [])).lower()
        for row in _real_data()["suite"]
    }
    for name, fragments in {
        "bayesian-workflow": ("calibration_sweep=1", "arviz", "warning"),
        "brainstorming": ("node", "skip"),
        "build": ("build/.scratch/",),
        "hooks": ("3.9", "launchd", "gate b"),
        "llm-wiki": ("@needs_pilot", "llm_wiki_root"),
        "tune-hyperparameters": ("--with sklearn", "fail"),
    }.items():
        assert all(fragment in notes[name] for fragment in fragments), name
    assert notes["track-model-experiments"]


# spec: "Default `['3.13']`."
# task: 2
def test_omitted_interpreters_default_to_python_313():
    assert runner.DEFAULT_PYTHONS == ("3.13",)
    suite = runner.parse({"suite": [{"name": "build", "dir": "build", "with": ["pytest"]}]})[0]
    assert suite.pythons == ("3.13",)


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_imports_only_standard_library_modules():
    tree = ast.parse((runner.REPO / "build/run_suites.py").read_text())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    assert imports <= sys.stdlib_module_names | {"__future__"}
    assert {"tomllib", "argparse", "subprocess", "shlex"} <= imports


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_runner_works_from_another_working_directory(tmp_path, monkeypatch, capsys):
    assert runner.REPO == Path(runner.__file__).resolve().parent.parent
    monkeypatch.chdir(tmp_path)
    assert runner.main(["--list", "build"]) == 0
    assert "build" in capsys.readouterr().out


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_invalid_registry_stops_every_non_check_mode(tmp_path, capsys):
    valid = {"name": "build", "dir": "build", "with": ["pytest"]}
    cases = [
        [{**valid, "wit": ["numpy"]}],
        [{key: value for key, value in valid.items() if key != missing}]
        for missing in ("name", "dir", "with")
    ]
    flat_cases = [cases[0], *cases[1]]
    for key, value in (
        ("name", 7),
        ("dir", 7),
        ("with", "pytest"),
        ("with", [7]),
        ("extras", "numpy"),
        ("extras", [7]),
        ("pythons", "3.13"),
        ("pythons", [7]),
        ("notes", "note"),
        ("notes", [7]),
    ):
        flat_cases.append([{**valid, key: value}])
    flat_cases.extend(
        [
            [{**valid, "with": ["numpy"]}],
            [valid, {**valid, "dir": "other"}],
            [valid, {**valid, "name": "other"}],
        ]
    )
    for entries in flat_cases:
        data = {"suite": entries}
        assert runner.validate(data), entries
        _write_registry(tmp_path, entries)
        for argv in (["--list"], ["build"], ["--all"]):
            assert runner.main(argv, root=tmp_path, run_one=lambda *_: 0) == 2, (entries, argv)
            capsys.readouterr()


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_runs_have_the_required_argv_in_registry_order():
    for suite in runner.parse(_real_data()):
        expected_pythons = EXPECTED[suite.name][3]
        actual = runner.runs(suite)
        assert [run.python for run in actual] == list(expected_pythons)
        for run in actual:
            expected = ["uv", "run", "--python", run.python]
            for dependency in ("pytest", *EXPECTED[suite.name][1]):
                expected.extend(("--with", dependency))
            expected.extend(("python", "-m", "pytest", "-q"))
            assert tuple(run.argv) == tuple(expected)
            assert run.label == f"{suite.name} ({run.python})"


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_form_quotes_directories_and_pytest_arguments():
    suite = runner.Suite("example", "dir with space", ("pytest",))
    run = runner.runs(suite, pytest_args=("test file.py::test_case[param]", "-k", "a or b"))[0]
    assert run.shell() == f"cd {shlex.quote(suite.dir)} && {shlex.join(run.argv)}"


# spec: "With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character."
# task: 5
def test_default_shell_forms_match_the_pinned_claude_commands():
    old = _git(runner.REPO, "show", "456e3fb:CLAUDE.md").stdout.splitlines()
    commands = set()
    for line in [*old[65:125], old[144]]:
        parts = line.strip().split(" && ")
        if not parts or not parts[0].startswith("cd "):
            continue
        for command in parts[1:]:
            if "uv run" in command and "python -m pytest -q" in command:
                commands.add(f"{parts[0]} && {command}")
    actual = {run.shell() for suite in runner.parse(_real_data()) for run in runner.runs(suite)}
    assert commands == actual


# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
def test_extras_follow_default_dependencies():
    suite = next(s for s in runner.parse(_real_data()) if s.name == "build")
    without = runner.runs(suite)[0].argv
    with_extras = runner.runs(suite, extras=True)[0].argv
    expected = ["uv", "run", "--python", "3.13"]
    for dependency in ("pytest", "numpy", "polars", "pyyaml", *EXPECTED["build"][2]):
        expected.extend(("--with", dependency))
    expected.extend(("python", "-m", "pytest", "-q"))
    assert tuple(with_extras) == tuple(expected)
    assert len(with_extras) > len(without)


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_pytest_arguments_reach_every_interpreter(tmp_path):
    root = _workspace(tmp_path)
    seen = []

    def record(_root, run):
        seen.append(run)
        return 0

    assert runner.main(["hooks", "--", "test_hooks.py::test_hooks", "-k", "hooks", "-s", "-rs"], root=root, run_one=record) == 0
    assert len(seen) == 2
    for run in seen:
        assert tuple(run.argv[-5:]) == ("test_hooks.py::test_hooks", "-k", "hooks", "-s", "-rs")


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_shows_all_suites_and_exact_selected_commands(tmp_path, capsys):
    root = _workspace(tmp_path)
    assert runner.main(["--list"], root=root) == 0
    output = capsys.readouterr().out
    for suite in runner.parse(_data(root)):
        assert suite.name in output
        assert suite.dir in output
        for run in runner.runs(suite):
            assert run.shell() in output
    assert "build/.scratch/" in output
    assert "matplotlib" in output

    assert runner.main(["--list", "build", "--extras", "--", "-k", "declared_dependencies"], root=root) == 0
    selected = capsys.readouterr().out
    build = next(s for s in runner.parse(_data(root)) if s.name == "build")
    assert runner.runs(build, extras=True, pytest_args=("-k", "declared_dependencies"))[0].shell() in selected
    assert "hooks" not in selected


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_skips_nested_suite_and_reports_it(tmp_path, capsys):
    root = _workspace(tmp_path)
    seen = []

    def record(_root, run):
        seen.append(run.label)
        return 0

    assert runner.main(["--all"], root=root, run_one=record) == 0
    output = capsys.readouterr().out
    assert seen == ["build (3.13)", "hooks (3.13)", "hooks (/usr/bin/python3)"]
    assert "skip cc-guide" in output
    assert "build" in output


# spec: "A suite named on the command line always runs."
# task: 4
def test_named_nested_suite_runs(tmp_path):
    root = _workspace(tmp_path)
    seen = []

    def record(_root, run):
        seen.append(run.label)
        return 0

    assert runner.main(["cc-guide"], root=root, run_one=record) == 0
    assert seen == ["cc-guide (3.13)"]


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_precede_streamed_output(tmp_path, capsys):
    root = _workspace(tmp_path)

    def record(_root, run):
        print(f"pytest output for {run.label}")
        return 0

    assert runner.main(["hooks"], root=root, run_one=record) == 0
    output = capsys.readouterr().out
    first = output.index("== hooks (3.13)")
    note = output.index("3.9 floor")
    pytest_output = output.index("pytest output for hooks (3.13)")
    second = output.index("== hooks (/usr/bin/python3)")
    assert first < note < pytest_output < second
    assert output.count("3.9 floor") == 1


# spec: "A failed run does not stop the next one."
# task: 4
def test_failed_run_does_not_stop_later_runs(tmp_path, capsys):
    root = _workspace(tmp_path)
    seen = []

    def record(_root, run):
        seen.append(run.label)
        return 5 if len(seen) == 1 else 0

    assert runner.main(["hooks", "build"], root=root, run_one=record) == 1
    assert seen == ["hooks (3.13)", "hooks (/usr/bin/python3)", "build (3.13)"]
    output = capsys.readouterr()
    assert "hooks (3.13)" in output.err
    assert "build (3.13)" not in output.err


# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
def test_exit_statuses_for_success_failure_and_usage(tmp_path, capsys):
    root = _workspace(tmp_path)
    assert runner.main(["build"], root=root, run_one=lambda *_: 0) == 0
    assert "passed" in capsys.readouterr().out.splitlines()[-1]
    assert runner.main(["build"], root=root, run_one=lambda *_: 5) == 1
    assert "build (3.13)" in capsys.readouterr().err.splitlines()[-1]
    assert runner.main(["unknown-suite"], root=root, run_one=lambda *_: 0) == 2
    capsys.readouterr()
    assert runner.main([], root=root, run_one=lambda *_: 0) == 2


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_unstartable_uv_is_a_failed_run(tmp_path, monkeypatch, capsys):
    root = _workspace(tmp_path)
    suite = runner.parse(_data(root))[0]
    monkeypatch.setenv("PATH", str(tmp_path / "no-executables"))
    assert runner.run_subprocess(root, runner.runs(suite)[0]) != 0
    assert runner.main(["build"], root=root) == 1
    assert "build (3.13)" in capsys.readouterr().err


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_inherits_the_environment_and_uses_suite_directory(tmp_path, monkeypatch):
    root = _workspace(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text(
        f"#!{sys.executable}\n"
        "import json, os\n"
        "from pathlib import Path\n"
        "Path(os.environ['CAPTURE_ENV']).write_text(json.dumps({'env': dict(os.environ), 'cwd': os.getcwd()}))\n"
    )
    uv.chmod(0o755)
    capture = tmp_path / "environment.json"
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("CAPTURE_ENV", str(capture))
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    expected_env = dict(os.environ)
    suite = runner.parse(_data(root))[0]

    assert runner.run_subprocess(root, runner.runs(suite)[0]) == 0
    observed = json.loads(capture.read_text())
    assert observed["env"] == expected_env
    assert observed["cwd"] == str(root / "build")


# spec: "a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_check_finds_both_pytest_filename_patterns_outside_registered_dirs(tmp_path):
    root = _workspace(tmp_path, tracked=True)
    _write(root, "skills/first/scripts/test_new.py", "def test_new(): assert True\n")
    _write(root, "skills/second/scripts/new_test.py", "def test_new(): assert True\n")
    _write(root, "build/deeper/test_covered.py", "def test_covered(): assert True\n")
    findings = runner.check(root, _data(root))
    assert any("skills/first/scripts" in finding for finding in findings)
    assert any("skills/second/scripts" in finding for finding in findings)
    assert not any("build/deeper" in finding for finding in findings)


# spec: "R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_finds_missing_and_empty_registered_directories(tmp_path):
    entries = [
        {"name": "build", "dir": "build", "with": ["pytest"]},
        {"name": "empty", "dir": "empty", "with": ["pytest"]},
        {"name": "gone", "dir": "gone", "with": ["pytest"]},
    ]
    _write_registry(tmp_path, entries)
    _write(tmp_path, "build/test_build.py", "def test_build(): assert True\n")
    _write(tmp_path, "empty/README.md", "No tests here.\n")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    _git(tmp_path, "add", ".")
    findings = runner.check(tmp_path, _data(tmp_path))
    assert any("empty" in finding for finding in findings)
    assert any("gone" in finding for finding in findings)


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_check_ignores_gitignored_trees(tmp_path):
    root = _workspace(tmp_path, tracked=True)
    _write(root, ".gitignore", "/.claude/worktrees/\n/build/.scratch/\n/ignored/\n")
    _git(root, "add", ".gitignore")
    for relative in (
        ".claude/worktrees/test_nested.py",
        "build/.scratch/test_scratch.py",
        "ignored/test_ignored.py",
    ):
        _write(root, relative, "def test_ignored(): assert True\n")
    assert runner.check(root, _data(root)) == []


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_check_finds_an_untracked_new_suite(tmp_path):
    root = _workspace(tmp_path, tracked=True)
    _write(root, "skills/new-skill/scripts/test_new.py", "def test_new(): assert True\n")
    assert "skills/new-skill/scripts/test_new.py" in _git(root, "ls-files", "--others", "--exclude-standard").stdout
    findings = runner.check(root, _data(root))
    assert any("skills/new-skill/scripts" in finding for finding in findings)


# spec: "If git fails, `--check` fails."
# task: 4
def test_check_fails_when_git_cannot_list_files(tmp_path):
    root = _workspace(tmp_path)
    assert runner.main(["--check"], root=root) == 1


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 4
def test_check_reports_schema_errors_as_findings(tmp_path, capsys):
    root = _workspace(tmp_path, tracked=True)
    entries = _fixture_entries()
    entries[0]["wit"] = entries[0].pop("with")
    _write_registry(root, entries)
    assert runner.main(["--check"], root=root) == 1
    output = capsys.readouterr()
    assert "build/suites.toml: " in output.out + output.err


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_check_output_and_exit_status(tmp_path, capsys):
    root = _workspace(tmp_path, tracked=True)
    assert runner.main(["--check"], root=root) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"

    _write(root, "skills/new-skill/scripts/test_new.py", "def test_new(): assert True\n")
    assert runner.main(["--check"], root=root) == 1
    lines = (capsys.readouterr().out).splitlines()
    assert len(lines) == 1
    assert "skills/new-skill/scripts" in lines[0]


# spec: "`build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`: `run suite_registry uv run --python 3.13 python build/run_suites.py --check`."
# task: 6
def test_ninth_commit_lint_is_wired_to_the_guard():
    script = (runner.REPO / "build/run_commit_lints.sh").read_text()
    assert re.search(
        r"(?m)^run suite_registry uv run --python 3\.13 python build/run_suites\.py --check$",
        script,
    )
    assert len(re.findall(r"(?m)^run\s+\w+", script)) == 9
    assert "nine" in script.lower()
    from build import test_commit_lints

    assert "suite_registry" in repr(test_commit_lints.CHECKS)


# spec: "`build/run_commit_lints.sh` keeps its literal commands."
# task: 6
def test_existing_commit_lint_commands_remain_literal():
    original = _git(runner.REPO, "show", "456e3fb:build/run_commit_lints.sh").stdout
    current = (runner.REPO / "build/run_commit_lints.sh").read_text()
    old_commands = re.findall(r"(?m)^run\s+\w+.*$", original)
    assert old_commands
    assert all(command in current for command in old_commands)


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_claude_md_has_the_runner_commands_and_no_directory_suite_commands():
    text = (runner.REPO / "CLAUDE.md").read_text()
    for suffix in (
        "--list",
        "<name> [--extras] [-- <pytest args>]",
        "--all",
        "--check",
    ):
        assert f"uv run --python 3.13 python build/run_suites.py {suffix}" in text
    for suite in runner.parse(_real_data()):
        for run in runner.runs(suite):
            assert run.shell() not in text
    assert "run_suites.py cc-guide" in text
    assert "cd build/cc_guide &&" not in text
    assert len(text.splitlines()) < 200


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_selected_tests_and_tools_remain_literal_in_root_claude_md():
    text = (runner.REPO / "CLAUDE.md").read_text()
    for command_fragment in (
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
        assert command_fragment in text


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_claude_md_intro_preserves_testing_rules():
    text = (runner.REPO / "CLAUDE.md").read_text()
    intro = next(
        line for line in text.splitlines()
        if "build/suites.toml" in line and "build/run_suites.py" in line
    )
    assert "uv" in intro
    assert "3.13" in intro
    assert "test_build.py" in intro
    assert "director" in intro.lower()
    assert "note" in intro.lower()
    assert "There is no root test runner" not in text


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
def test_conformance_positive_control_uses_the_first_line_stamp():
    source = (runner.REPO / "build/test_check_conformance.py").read_text()
    tree = ast.parse(source)
    function = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    body = ast.get_source_segment(source, function)
    assert "@needs_pilot" not in body
    assert "cc-guide:" in body
    first_line = (runner.REPO / "CLAUDE.md").read_text().splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .+ @\S+ -->", first_line)


# spec: "`uv run --python 3.13 python build/run_suites.py --check` prints `suite registry ok`."
# task: 5
def test_real_registry_passes_the_guard(capsys):
    assert runner.main(["--check"]) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>cc_guide</plan></flag>
<flag task="2"><spec>Default `['3.13']`.</spec><plan>DEFAULT_PYTHONS = ('3.12',)</plan></flag>
<flag task="5"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>cc_guide</plan></flag>
</flags>
<untestable>
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
This work lands whole, registry and CLAUDE.md shrink, ahead of plan 52's Task 6.
Plan 52's planning session amends its plan to match and records Q4 as (c).
The entries carry the text of today's commands and comments.
Every command, dependency and note survives; the only change is the form.
The file ends at about 145 lines.
The deletion of lines 66–125 is bounded by two lines that no other plan edits: the `# Full build-directory tests` comment and the `cd hooks && …` command.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
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
Run it before the `CLAUDE.md` deletion.
It also checks each comment's skip-unlocking deps against that suite's `extras`.
Run `hooks`, `build` and `bayesian-workflow` once directly and once through the runner, in the same checkout.
Their pytest summary lines match.
Then run `--all` once, and record each run's result beside the direct result.
`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`.
The Stage 2 audit passes, and the behaviour runs match.
The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
The commit hook runs one more fast, stdlib-only check.
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
</untestable>