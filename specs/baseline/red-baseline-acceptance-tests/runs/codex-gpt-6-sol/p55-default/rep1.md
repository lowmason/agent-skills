<tests>
import ast
import copy
import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

import run_suites as sut
import test_commit_lints as commit_tests


ROOT = Path(__file__).resolve().parents[1]

SAMPLE = """
[[suite]]
name = "build"
dir = "build"
with = ["pytest", "numpy", "polars", "pyyaml"]
extras = ["arviz>=1.0"]
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
notes = ["Gate B probe"]
"""


def sample_data():
    return tomllib.loads(SAMPLE)


def write_registry(root, text=SAMPLE):
    path = root / "build/suites.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def put(root, relative, text="def test_example():\n    pass\n"):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def init_git(root):
    subprocess.run(
        ["git", "init", "-q", str(root)],
        check=True,
        capture_output=True,
        text=True,
    )


def stage_all(root):
    subprocess.run(
        ["git", "add", "-A"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_and_sort_order():
    text = (ROOT / "build/suites.toml").read_text()
    header = text.split("[[suite]]", 1)[0].lower()
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert key in header
    assert "sort" in header
    assert "ninth" in header or "nine" in header or "9th" in header
    assert "--check" in header or "suite_registry" in header

    names = [row["name"] for row in tomllib.loads(text)["suite"]]
    assert names == sorted(names)
    assert len(names) == len(set(names))


# spec: "On `main` at `456e3fb` there are 18: the 17 in `CLAUDE.md` lines 66–125, and `build/cc_guide`, whose command is line 145."
# task: 5
def test_registry_contains_the_specified_suite_inventory():
    expected = {
        "bayesian-workflow": (
            "skills/bayesian-workflow/scripts",
            ["pytest", "arviz", "arviz-stats", "numpy", "xarray"],
            ["matplotlib"],
            ["3.13"],
        ),
        "brainstorming": ("skills/brainstorming/scripts", ["pytest"], [], ["3.13"]),
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
            ["pytest", "numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"],
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
    rows = {
        row["name"]: row
        for row in tomllib.loads((ROOT / "build/suites.toml").read_text())["suite"]
    }
    assert expected.keys() <= rows.keys()
    for name, (directory, deps, extras, pythons) in expected.items():
        row = rows[name]
        assert row["dir"] == directory
        assert row["with"] == deps
        assert row.get("extras", []) == extras
        assert row.get("pythons", ["3.13"]) == pythons


# spec: "The notes carry the rest of each comment."
# task: 5
def test_registry_retains_the_named_operational_notes():
    rows = {
        row["name"]: " ".join(row.get("notes", []))
        for row in tomllib.loads((ROOT / "build/suites.toml").read_text())["suite"]
    }
    for name, terms in {
        "build": ("build/.scratch/",),
        "bayesian-workflow": ("CALIBRATION_SWEEP=1", "arviz"),
        "llm-wiki": ("@needs_pilot", "LLM_WIKI_ROOT"),
        "brainstorming": ("node",),
        "tune-hyperparameters": ("--with sklearn",),
        "hooks": ("3.9", "launchd", "Gate B"),
    }.items():
        for term in terms:
            assert term.lower() in rows[name].lower()


# spec: "R3.1 Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 2
def test_runner_imports_only_standard_library_modules():
    tree = ast.parse((ROOT / "build/run_suites.py").read_text())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    assert {"tomllib", "argparse", "subprocess", "shlex"} <= imports
    assert imports <= sys.stdlib_module_names | {"__future__"}


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
def test_validation_rejects_every_listed_schema_failure():
    good = sample_data()
    assert sut.validate(good) == []

    bad = []
    for key in ("name", "dir", "with"):
        data = copy.deepcopy(good)
        del data["suite"][0][key]
        bad.append(data)
    for key, value in (
        ("name", 1),
        ("dir", 1),
        ("with", "pytest"),
        ("extras", "arviz"),
        ("pythons", "3.13"),
        ("notes", "note"),
        ("with", ["pytest", 1]),
        ("extras", [1]),
        ("pythons", [1]),
        ("notes", [1]),
    ):
        data = copy.deepcopy(good)
        data["suite"][0][key] = value
        bad.append(data)

    data = copy.deepcopy(good)
    data["suite"][0]["wth"] = ["pytest"]
    bad.append(data)

    data = copy.deepcopy(good)
    data["suite"][0]["with"] = ["numpy"]
    bad.append(data)

    data = copy.deepcopy(good)
    data["suite"][1]["name"] = data["suite"][0]["name"]
    bad.append(data)

    data = copy.deepcopy(good)
    data["suite"][1]["dir"] = data["suite"][0]["dir"]
    bad.append(data)

    for data in bad:
        assert sut.validate(data)


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
def test_default_run_argv_and_shell_form():
    suite = next(s for s in sut.parse(sample_data()) if s.name == "build")
    (run,) = sut.runs(suite)
    assert run.label == "build (3.13)"
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
    assert run.shell() == (
        "cd build && uv run --python 3.13 --with pytest --with numpy "
        "--with polars --with pyyaml python -m pytest -q"
    )


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 2
def test_hooks_has_two_independent_shell_forms():
    suite = next(s for s in sut.parse(sample_data()) if s.name == "hooks")
    runs = sut.runs(suite)
    assert [run.python for run in runs] == ["3.13", "/usr/bin/python3"]
    assert [run.shell() for run in runs] == [
        "cd hooks && uv run --python 3.13 --with pytest python -m pytest -q",
        "cd hooks && uv run --python /usr/bin/python3 --with pytest python -m pytest -q",
    ]


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_extras_and_pytest_arguments_are_ordered_and_shell_quoted():
    suite = next(s for s in sut.parse(sample_data()) if s.name == "build")
    args = ("test_file.py::test_case[a b]", "-k", "fast and not slow")
    (run,) = sut.runs(suite, extras=True, pytest_args=args)
    assert run.argv[14:16] == ("--with", "arviz>=1.0")
    assert run.argv[-3:] == args
    assert run.shell() == "cd build && " + shlex.join(run.argv)


# spec: "R3.6 **`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_identifies_the_nested_suite():
    suites = sut.parse(sample_data())
    by_name = {suite.name: suite for suite in suites}
    assert sut.container(by_name["cc-guide"], suites) == by_name["build"]
    assert sut.container(by_name["build"], suites) is None
    assert sut.container(by_name["hooks"], suites) is None


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_cli_lists_from_an_unrelated_working_directory(tmp_path):
    assert sut.REPO == ROOT
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "build/run_suites.py"),
            "--list",
            "brainstorming",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "brainstorming" in result.stdout
    assert "skills/brainstorming/scripts" in result.stdout


# spec: "R3.3 **`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_prints_all_sample_suites_and_their_metadata(tmp_path, capsys):
    write_registry(tmp_path)
    assert sut.main(["--list"], root=tmp_path) == 0
    output = capsys.readouterr().out
    for name, directory in (
        ("build", "build"),
        ("cc-guide", "build/cc_guide"),
        ("hooks", "hooks"),
    ):
        assert name in output
        assert directory in output
    assert "arviz>=1.0" in output
    assert "build/.scratch/" in output
    assert "Gate B probe" in output
    assert "cd hooks && uv run --python 3.13" in output
    assert "cd hooks && uv run --python /usr/bin/python3" in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_prints_the_exact_extras_command(tmp_path, capsys):
    write_registry(tmp_path)
    assert sut.main(
        ["--list", "build", "--extras", "--", "test_file.py::test_case[a b]", "-s"],
        root=tmp_path,
    ) == 0
    output = capsys.readouterr().out
    expected = (
        "cd build && "
        + shlex.join(
            [
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
                "--with",
                "arviz>=1.0",
                "python",
                "-m",
                "pytest",
                "-q",
                "test_file.py::test_case[a b]",
                "-s",
            ]
        )
    )
    assert expected in output


# spec: "A failed run does not stop the next one."
# task: 4
def test_named_runs_continue_after_failure_and_print_notes_once(tmp_path, capsys):
    write_registry(tmp_path)
    calls = []
    statuses = iter((5, 0, 0))

    def run_one(root, run):
        calls.append((root, run.label))
        print(f"pytest output: {run.label}")
        return next(statuses)

    status = sut.main(["hooks", "build"], root=tmp_path, run_one=run_one)
    output = capsys.readouterr()
    assert status == 1
    assert calls == [
        (tmp_path, "hooks (3.13)"),
        (tmp_path, "hooks (/usr/bin/python3)"),
        (tmp_path, "build (3.13)"),
    ]
    assert output.out.index("== hooks (3.13)") < output.out.index("note: Gate B probe")
    assert output.out.index("note: Gate B probe") < output.out.index(
        "pytest output: hooks (3.13)"
    )
    assert output.out.count("note: Gate B probe") == 1
    assert output.out.index("== hooks (/usr/bin/python3)") < output.out.index(
        "== build (3.13)"
    )
    assert output.err.strip().splitlines()[-1].endswith("hooks (3.13)")


# spec: "The last line names the failed runs, or says that every run passed."
# task: 4
def test_success_status_and_final_summary(tmp_path, capsys):
    write_registry(tmp_path)
    assert sut.main(
        ["cc-guide"], root=tmp_path, run_one=lambda root, run: 0
    ) == 0
    assert capsys.readouterr().out.strip().splitlines()[-1] == "suite runs passed"


# spec: "A suite named on the command line always runs."
# task: 4
def test_all_skips_nested_suite_but_named_suite_runs(tmp_path, capsys):
    write_registry(tmp_path)
    calls = []

    def run_one(root, run):
        calls.append(run.suite.name)
        return 0

    assert sut.main(["--all"], root=tmp_path, run_one=run_one) == 0
    output = capsys.readouterr().out
    assert calls == ["build", "hooks", "hooks"]
    assert "skip cc-guide: the build suite collects build/cc_guide" in output

    calls.clear()
    assert sut.main(["cc-guide"], root=tmp_path, run_one=run_one) == 0
    assert calls == ["cc-guide"]


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_pytest_arguments_reach_each_interpreter_run(tmp_path):
    write_registry(tmp_path)
    argvs = []

    def run_one(root, run):
        argvs.append(run.argv)
        return 0

    assert sut.main(
        ["hooks", "--", "test_file.py::test_one", "-k", "declared_dependencies", "-s", "-rs"],
        root=tmp_path,
        run_one=run_one,
    ) == 0
    assert len(argvs) == 2
    for argv in argvs:
        assert argv[-5:] == (
            "test_file.py::test_one",
            "-k",
            "declared_dependencies",
            "-s",
            "-rs",
        )


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
def test_usage_unknown_name_and_invalid_registry_exit_two(tmp_path):
    write_registry(tmp_path)
    assert sut.main(["--not-an-option"], root=tmp_path) == 2
    assert sut.main(["not-a-suite"], root=tmp_path) == 2

    write_registry(tmp_path, SAMPLE.replace('with = ["pytest"]', 'wth = ["pytest"]'))
    calls = []

    def run_one(root, run):
        calls.append(run)
        return 0

    for argv in (["--list"], ["hooks"], ["--all"]):
        assert sut.main(argv, root=tmp_path, run_one=run_one) == 2
    assert calls == []


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_failed_process_start_counts_as_a_failed_run(tmp_path, capsys):
    write_registry(tmp_path)

    def cannot_start(root, run):
        raise FileNotFoundError("uv")

    assert sut.main(
        ["cc-guide"], root=tmp_path, run_one=cannot_start
    ) == 1
    assert "cc-guide (3.13)" in capsys.readouterr().err


# spec: "R3.8 The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_receives_environment_and_suite_working_directory(
    tmp_path, monkeypatch
):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_uv = bin_dir / "uv"
    fake_uv.write_text(
        "#!/bin/sh\n"
        'printf "%s|%s" "$CALIBRATION_SWEEP" "$CUSTOM_TEST_ENV" > "$ENV_CAPTURE"\n'
        'pwd > "$CWD_CAPTURE"\n'
    )
    fake_uv.chmod(0o755)
    env_capture = tmp_path / "env.txt"
    cwd_capture = tmp_path / "cwd.txt"
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("CUSTOM_TEST_ENV", "sentinel")
    monkeypatch.setenv("ENV_CAPTURE", str(env_capture))
    monkeypatch.setenv("CWD_CAPTURE", str(cwd_capture))

    suite = next(s for s in sut.parse(sample_data()) if s.name == "build")
    (run,) = sut.runs(suite)
    assert sut.run_subprocess(ROOT, run) == 0
    assert env_capture.read_text() == "1|sentinel"
    assert Path(cwd_capture.read_text().strip()) == ROOT / "build"


# spec: "R4.2 The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root."
# task: 3
def test_check_reports_tracked_uncovered_pytest_directories(tmp_path):
    init_git(tmp_path)
    put(tmp_path, "build/test_registered.py")
    put(tmp_path, "skills/explore-data/scripts/test_new.py")
    put(tmp_path, "skills/writing-plans/scripts/example_test.py")
    stage_all(tmp_path)
    data = {"suite": [{"name": "build", "dir": "build", "with": ["pytest"]}]}

    assert set(sut.check(tmp_path, data)) == {
        "skills/explore-data/scripts: holds pytest files, but no suite in build/suites.toml contains it",
        "skills/writing-plans/scripts: holds pytest files, but no suite in build/suites.toml contains it",
    }


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_check_counts_untracked_tests_and_excludes_ignored_trees(tmp_path):
    init_git(tmp_path)
    put(tmp_path, "build/test_registered.py")
    put(
        tmp_path,
        ".gitignore",
        ".claude/worktrees/\nbuild/.scratch/\n",
    )
    stage_all(tmp_path)
    put(tmp_path, ".claude/worktrees/draft/test_ignored.py")
    put(tmp_path, "build/.scratch/test_ignored.py")
    put(tmp_path, "skills/brainstorming/scripts/test_new.py")
    data = {"suite": [{"name": "build", "dir": "build", "with": ["pytest"]}]}

    assert sut.check(tmp_path, data) == [
        "skills/brainstorming/scripts: holds pytest files, but no suite in build/suites.toml contains it"
    ]


# spec: "R4.1 `--check` reports two kinds of findings:"
# task: 3
def test_check_finds_missing_and_testless_registered_directories(tmp_path):
    init_git(tmp_path)
    put(tmp_path, "hooks/README.md", "No tests here.\n")
    stage_all(tmp_path)
    data = {
        "suite": [
            {"name": "build", "dir": "build", "with": ["pytest"]},
            {"name": "hooks", "dir": "hooks", "with": ["pytest"]},
        ]
    }

    findings = sut.check(tmp_path, data)
    assert len(findings) == 2
    assert all(line.startswith("build/suites.toml: ") for line in findings)
    assert any("build" in line for line in findings)
    assert any("hooks" in line for line in findings)


# spec: "If git fails, `--check` fails."
# task: 3
def test_check_fails_when_git_cannot_list_files(tmp_path):
    put(tmp_path, "build/test_registered.py")
    data = {"suite": [{"name": "build", "dir": "build", "with": ["pytest"]}]}
    write_registry(
        tmp_path,
        '[[suite]]\nname = "build"\ndir = "build"\nwith = ["pytest"]\n',
    )

    assert sut.check(tmp_path, data)
    assert sut.main(["--check"], root=tmp_path) == 1


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
def test_check_reports_schema_problems_as_findings(tmp_path, capsys):
    init_git(tmp_path)
    put(tmp_path, "build/test_registered.py")
    stage_all(tmp_path)
    invalid = (
        '[[suite]]\nname = "build"\ndir = "build"\n'
        'with = ["pytest"]\nmisspelled = true\n'
    )
    write_registry(tmp_path, invalid)

    findings = sut.check(tmp_path, tomllib.loads(invalid))
    assert findings
    assert all(line.startswith("build/suites.toml: ") for line in findings)
    assert sut.main(["--check"], root=tmp_path) == 1
    output = capsys.readouterr()
    printed = output.out.splitlines() + output.err.splitlines()
    assert all(line in printed for line in findings)


# spec: "R4.3 Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 5
def test_real_registry_passes_check(capsys):
    data = tomllib.loads((ROOT / "build/suites.toml").read_text())
    assert sut.check(ROOT, data) == []
    assert sut.main(["--check"], root=ROOT) == 0
    assert capsys.readouterr().out.strip() == "suite registry ok"


# spec: "With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character."
# task: 5
def test_default_shell_forms_match_the_named_baseline_commands(capsys):
    baseline = subprocess.run(
        ["git", "show", "456e3fb:CLAUDE.md"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    expected = set()
    for raw in baseline[65:125] + [baseline[144]]:
        line = raw.strip()
        if not line.startswith("cd ") or "uv run" not in line:
            continue
        if line.startswith("cd hooks && "):
            expected.update(
                "cd hooks && " + part
                for part in line.split(" && ")[1:]
                if "uv run" in part
            )
        else:
            expected.add(line)

    assert sut.main(["--list"], root=ROOT) == 0
    reported = set()
    for line in capsys.readouterr().out.splitlines():
        if "cd " in line and " && uv run" in line:
            reported.add(line[line.index("cd ") :].strip())
    assert expected <= reported


# spec: "R4.4 `build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`:"
# task: 6
def test_ninth_commit_lint_is_wired_to_check():
    script = (ROOT / "build/run_commit_lints.sh").read_text()
    assert "nine" in script.splitlines()[0].lower() or "nine" in "\n".join(
        script.splitlines()[:5]
    ).lower()
    assert len(re.findall(r"(?m)^\s*run\s+\w+", script)) == 9
    assert (
        "run suite_registry uv run --python 3.13 "
        "python build/run_suites.py --check"
    ) in script
    assert "suite_registry" in repr(commit_tests.CHECKS)
    assert hasattr(commit_tests, "test_unregistered_suite_is_refused")


# spec: "The file ends at about 145 lines."
# task: 7
def test_root_claude_md_is_short_and_names_the_runner():
    lines = (ROOT / "CLAUDE.md").read_text().splitlines()
    assert len(lines) < 200
    intro = lines[59]
    for term in (
        "uv",
        "3.13",
        "directory",
        "test_build.py",
        "build/suites.toml",
        "build/run_suites.py",
        "notes",
    ):
        assert term in intro
    text = "\n".join(lines)
    for command in (
        "python build/run_suites.py --list",
        "python build/run_suites.py <name>",
        "python build/run_suites.py --all",
        "python build/run_suites.py --check",
    ):
        assert command in text
    assert "run_suites.py cc-guide" in text
    assert "suite_registry" in text or "suite-registry" in text


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_claude_md_has_no_whole_directory_suite_command():
    text = (ROOT / "CLAUDE.md").read_text()
    rows = tomllib.loads((ROOT / "build/suites.toml").read_text())["suite"]
    for row in rows:
        pattern = (
            rf"(?m)^\s*cd {re.escape(row['dir'])} && "
            r"uv run .* python -m pytest -q(?:\s*&&.*)?\s*$"
        )
        assert re.search(pattern, text) is None, row["name"]


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_selected_tests_and_tools_remain_in_root_claude_md():
    text = (ROOT / "CLAUDE.md").read_text()
    for term in (
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
        assert term in text
    assert text.count("build.py") >= 2


# spec: "R5.3 `build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_claude_md_documents_the_ninth_lint():
    text = (ROOT / "build/CLAUDE.md").read_text()
    assert "the nine commit lints" in text
    assert "the eight commit lints" not in text
    for term in ("suites.toml", "run_suites.py", "--check", "commit lint"):
        assert term in text


# spec: "The control becomes a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp."
# task: 7
def test_conformance_positive_control_uses_version_agnostic_stamp():
    first_line = (ROOT / "CLAUDE.md").read_text().splitlines()[0]
    assert re.fullmatch(r"<!-- cc-guide: .+ @[^ ]+ -->", first_line)

    source = (ROOT / "build/test_check_conformance.py").read_text()
    tree = ast.parse(source)
    function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_claude_md_import_resolves_passes_on_the_repo"
    )
    function_source = ast.get_source_segment(source, function)
    assert "@needs_pilot" not in function_source
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>`cc_guide`</plan></flag>
<flag task="2"><spec>Default `['3.13']`.</spec><plan>`DEFAULT_PYTHONS = ('3.12',)`</plan></flag>
<flag task="5"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>`cc_guide`</plan></flag>
</flags>
<untestable>
**Status:** Design approved in brainstorming on 2026-10-18.
Next step: an implementation plan from the writing-plans skill (`entry_check.py` reported plan id 54 as next free on 2026-10-18).
`CLAUDE.md` had 199 on `main` at `456e3fb`.
Each new suite costs two or three more lines.
Plan 50 (the superpowers upstream fixes, lowmason/agent-skills#56) took the file from 195 to 199.
Plan 52 (the write-with-asd-ste100 skill, not merged) needs two more lines.
Its open question Q4 asked where they come from: (a) fold seven suites under one comment, (b) record a size deviation, or (c) move the per-suite commands out of the root file first.
In plan 38, Task 2 condensed `CLAUDE.md` from 224 lines to 170 and kept every command in place.
The file then grew back to 199 by 2026-10-18.
Worktree-isolated sessions and their subagents have refused compound shell such as `cd X && Y` (seen on 2026-10-12).
The owner took these decisions on 2026-10-18.
Design section 1 (the registry keys and the runner's behaviour) was approved as presented.
Design section 2 (the guard, the file edits, the tests and the couplings) was approved as presented.
Every command, dependency and note survives; the only change is the form.
Whatever lies between them goes, so the edit works in either landing order with plan 52 (R7.1).
No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`.
The new files are the owner's original tooling.
The register's deviation `claude-md-serves-codex-gemini` still holds as written: a condensed Commands block stays in the root file, and the registry is a plain file that every runtime can read.
R6.3 Write each test before its code and see it fail first (red, then green).
Its expectations of 199 and 197 lines (Task 1, DF19, Q4, Coupling (e)) change with it.
A note in the session group's shared notes folder gives the exact entry.
If plan 52 lands first after all, R5.2's deletion still works, and this plan registers that suite itself.
None of the lines that R5.1 deletes carries one of its edit anchors.
Its Task 7 edits line 133, which stays.
Its own suite commands are written out in full in the plan, so they work without `CLAUDE.md`.
It edits one sentence of `build/CLAUDE.md`'s `cc_guide/` paragraph.
If an edit block does not match, merge by hand.
Run it before the `CLAUDE.md` deletion.
Then run `--all` once, and record each run's result beside the direct result.
The Stage 2 audit passes, and the behaviour runs match.
The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
The commit hook runs one more fast, stdlib-only check.
Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.
</untestable>