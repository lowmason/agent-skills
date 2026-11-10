<tests>
import ast
import copy
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from build import run_suites as runner


EXPECTED = {
    "bayesian-workflow": (
        "skills/bayesian-workflow/scripts",
        ("pytest", "arviz", "arviz-stats", "numpy", "xarray"),
        ("matplotlib",),
        ("3.13",),
    ),
    "brainstorming": (
        "skills/brainstorming/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "build": (
        "build",
        ("pytest", "numpy", "polars", "pyyaml"),
        (
            "arviz>=1.0",
            "arviz-base",
            "arviz-stats",
            "arviz-plots",
            "numpyro",
            "jax",
            "matplotlib",
        ),
        ("3.13",),
    ),
    "cc-guide": (
        "build/cc_guide",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "classification-codes": (
        "skills/classification-codes/scripts",
        ("pytest", "polars"),
        (),
        ("3.13",),
    ),
    "describe-critique-methodology": (
        "skills/describe-critique-methodology/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "design-architecture": (
        "skills/design-architecture/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "explore-data": (
        "skills/explore-data/scripts",
        ("pytest", "polars"),
        (),
        ("3.13",),
    ),
    "geographic-codes": (
        "skills/geographic-codes/scripts",
        ("pytest", "polars", "fastexcel"),
        (),
        ("3.13",),
    ),
    "hooks": (
        "hooks",
        ("pytest",),
        (),
        ("3.13", "/usr/bin/python3"),
    ),
    "llm-wiki": (
        "skills/llm-wiki/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "recommend-probabilistic-model": (
        "skills/recommend-probabilistic-model/scripts",
        ("pytest", "numpy", "polars"),
        (),
        ("3.13",),
    ),
    "recommend-visualization": (
        "skills/recommend-visualization/scripts",
        ("pytest", "numpy", "polars"),
        (),
        ("3.13",),
    ),
    "subagent-driven-development": (
        "skills/subagent-driven-development/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "systematic-debugging": (
        "skills/systematic-debugging",
        ("pytest",),
        (),
        ("3.13",),
    ),
    "track-model-experiments": (
        "skills/track-model-experiments/scripts",
        ("pytest", "numpy", "polars", "arviz", "numpyro", "h5netcdf", "h5py"),
        (),
        ("3.13",),
    ),
    "tune-hyperparameters": (
        "skills/tune-hyperparameters/scripts",
        ("pytest", "numpy", "polars"),
        ("scikit-learn", "optuna"),
        ("3.13",),
    ),
    "writing-plans": (
        "skills/writing-plans/scripts",
        ("pytest",),
        (),
        ("3.13",),
    ),
}

ROOT = Path(runner.REPO)
RUNNER_FILE = Path(runner.__file__).resolve()


def _row(name):
    directory, deps, extras, pythons = EXPECTED[name]
    row = {"name": name, "dir": directory, "with": list(deps)}
    if extras:
        row["extras"] = list(extras)
    if pythons != ("3.13",):
        row["pythons"] = list(pythons)
    return row


def _suite(name):
    directory, deps, extras, pythons = EXPECTED[name]
    return runner.Suite(
        name=name,
        dir=directory,
        deps=deps,
        extras=extras,
        pythons=pythons,
    )


def _argv(name, python, extras=False, pytest_args=()):
    _, deps, extra_deps, _ = EXPECTED[name]
    result = ["uv", "run", "--python", python]
    for dep in deps + (extra_deps if extras else ()):
        result.extend(("--with", dep))
    result.extend(("python", "-m", "pytest", "-q"))
    result.extend(pytest_args)
    return tuple(result)


def _shell_words(text):
    lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def _write_data(root, data):
    path = root / "build/suites.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in data.items():
        if key == "suite" and isinstance(value, list):
            continue
        lines.append(f"{json.dumps(key)} = {json.dumps(value)}")
    if isinstance(data.get("suite"), list):
        for row in data["suite"]:
            lines.append("[[suite]]")
            for key, value in row.items():
                lines.append(f"{json.dumps(key)} = {json.dumps(value)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _make_root(root, rows=None):
    if rows is None:
        rows = [_row("build"), _row("cc-guide"), _row("hooks")]
        rows[0]["notes"] = ["build/.scratch/"]
        rows[2]["notes"] = ["3.9 floor", "launchd-PATH skips", "Gate B probe"]
    data = {"suite": copy.deepcopy(rows)}
    _write_data(root, data)
    for row in rows:
        directory = root / row["dir"]
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "test_new.py").write_text(
            "def test_new():\n    pass\n", encoding="utf-8"
        )
    return data


def _no_run(root, run):
    pytest.fail(f"Unexpected execution: {run.label}")


def _invoke(argv, root, run_one=_no_run):
    try:
        return runner.main(argv=argv, root=root, run_one=run_one)
    except SystemExit as exc:
        return exc.code


def _git(root, *args):
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(root), *args],
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )


def _make_git_root(root, rows=None):
    data = _make_root(root, rows)
    _git(root, "init", "-q")
    return data


def _read_real_registry():
    return tomllib.loads((ROOT / "build/suites.toml").read_text(encoding="utf-8"))


def _historical(path):
    return _git(ROOT, "show", f"456e3fb:{path}").stdout


def _directory_commands(lines):
    commands = []
    for line in lines:
        pieces = line.strip().split(" && ")
        if len(pieces) < 2:
            continue
        prefix = shlex.split(pieces[0])
        if len(prefix) != 2 or prefix[0] != "cd":
            continue
        for command in pieces[1:]:
            words = shlex.split(command)
            if (
                words[:2] == ["uv", "run"]
                and words[-4:] == ["python", "-m", "pytest", "-q"]
            ):
                commands.append(f"{pieces[0]} && {command}")
    return commands


def _invalid_cases():
    base = {"suite": [_row("brainstorming"), _row("llm-wiki")]}
    cases = []

    data = copy.deepcopy(base)
    data["suite"][0]["exrtas"] = ["matplotlib"]
    cases.append(("unknown-suite-key", data))

    data = copy.deepcopy(base)
    data["unknown"] = []
    cases.append(("unknown-root-key", data))

    for field in ("name", "dir", "with"):
        data = copy.deepcopy(base)
        del data["suite"][0][field]
        cases.append((f"missing-{field}", data))

    wrong_values = {
        "name": [1, True, []],
        "dir": [1, True, []],
        "with": ["pytest", [1], [True]],
        "extras": ["matplotlib", [1], [True]],
        "pythons": ["3.13", [1], [True]],
        "notes": ["Gate B", [1], [True]],
    }
    for field, values in wrong_values.items():
        for index, value in enumerate(values):
            data = copy.deepcopy(base)
            data["suite"][0][field] = value
            cases.append((f"wrong-{field}-{index}", data))

    data = copy.deepcopy(base)
    data["suite"][1]["name"] = data["suite"][0]["name"]
    cases.append(("duplicate-name", data))

    data = copy.deepcopy(base)
    data["suite"][1]["dir"] = data["suite"][0]["dir"]
    cases.append(("duplicate-directory", data))

    for deps in ([], ["numpy"]):
        data = copy.deepcopy(base)
        data["suite"][0]["with"] = deps
        cases.append((f"missing-pytest-{len(deps)}", data))

    return cases


INVALID_CASES = [
    pytest.param(data, id=name) for name, data in _invalid_cases()
]


@pytest.fixture
def fixture_root(tmp_path):
    data = _make_root(tmp_path)
    return tmp_path, data


@pytest.fixture
def fake_uv(tmp_path, monkeypatch):
    binary_dir = tmp_path / "fake-bin"
    binary_dir.mkdir()
    record = tmp_path / "uv-records.jsonl"
    executable = binary_dir / "uv"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "record = {'argv': sys.argv[1:], 'cwd': os.getcwd(), "
        "'env': dict(os.environ)}\n"
        "with open(os.environ['SUITE_PROBE_FILE'], 'a', encoding='utf-8') as f:\n"
        "    f.write(json.dumps(record) + '\\n')\n"
        "print('pytest output streams', flush=True)\n"
        "print('pytest stderr streams', file=sys.stderr, flush=True)\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(binary_dir) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("SUITE_PROBE_FILE", str(record))
    monkeypatch.setenv("CALIBRATION_SWEEP", "1")
    monkeypatch.setenv("PYTHONCOERCECLOCALE", "0")
    return record


# spec: "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13."
# task: 4
def test_runner_has_only_standard_library_imports():
    tree = ast.parse(RUNNER_FILE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            modules = [node.module or ""]
        else:
            continue
        for module in modules:
            assert module.split(".")[0] in sys.stdlib_module_names


# spec: "Default `['3.13']`."
# task: 2
def test_default_interpreter_is_python_313():
    assert runner.DEFAULT_PYTHONS == ("3.13",)
    suite = runner.Suite(
        name="brainstorming",
        dir="skills/brainstorming/scripts",
        deps=("pytest",),
    )
    assert suite.pythons == ("3.13",)
    parsed = runner.parse({"suite": [_row("brainstorming")]})
    assert parsed[0].pythons == ("3.13",)


# spec: "The default `--with` deps, in the order the current command gives them."
# task: 2
def test_parse_preserves_dependencies_and_optional_lists():
    row = _row("build")
    row["notes"] = ["build/.scratch/", "CALIBRATION_SWEEP=1"]
    assert runner.validate({"suite": [row]}) == []
    suite = runner.parse({"suite": [row]})[0]
    assert suite.name == "build"
    assert suite.dir == "build"
    assert suite.deps == EXPECTED["build"][1]
    assert suite.extras == EXPECTED["build"][2]
    assert suite.notes == tuple(row["notes"])


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 2
@pytest.mark.parametrize("data", INVALID_CASES)
def test_validate_rejects_every_invalid_registry_category(data):
    findings = runner.validate(data)
    assert findings
    assert all(isinstance(finding, str) and finding for finding in findings)


# spec: "An unknown key, a missing required key, a wrong type, a duplicate name or directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2."
# task: 4
@pytest.mark.parametrize("data", INVALID_CASES)
@pytest.mark.parametrize("argv", [["--list"], ["brainstorming"], ["--all"]])
def test_invalid_registry_prevents_listing_and_execution(tmp_path, data, argv):
    _make_root(tmp_path)
    _write_data(tmp_path, data)
    assert _invoke(argv, tmp_path) == 2


# spec: "`--check` reports the same failures as findings (R4.3)."
# task: 3
@pytest.mark.parametrize("data", INVALID_CASES)
def test_check_reports_invalid_registry_as_findings(tmp_path, data):
    _make_git_root(tmp_path)
    _write_data(tmp_path, data)
    findings = runner.check(tmp_path, data)
    assert findings
    assert all(isinstance(line, str) and len(line.splitlines()) == 1
               for line in findings)
    assert _invoke(["--check"], tmp_path) == 1


# spec: "The entries carry the text of today's commands and comments."
# task: 5
@pytest.mark.parametrize("name", EXPECTED)
def test_real_registry_contains_each_specified_suite_with_its_values(name):
    suites = {suite.name: suite for suite in runner.parse(_read_real_registry())}
    assert name in suites
    suite = suites[name]
    directory, deps, extras, pythons = EXPECTED[name]
    assert suite.dir == directory
    assert suite.deps == deps
    assert suite.extras == extras
    assert suite.pythons == pythons


# spec: "One `[[suite]]` table per directory suite, sorted by `name`."
# task: 5
def test_real_registry_is_sorted_and_has_no_duplicate_names_or_directories():
    data = _read_real_registry()
    rows = data["suite"]
    names = [row["name"] for row in rows]
    directories = [row["dir"] for row in rows]
    assert names == sorted(names)
    assert len(names) == len(set(names))
    assert len(directories) == len(set(directories))
    assert runner.validate(data) == []


# spec: "A header comment states the keys, the sort order, and that the ninth commit lint checks the file."
# task: 5
def test_registry_header_documents_schema_sorting_and_lint():
    text = (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    header = text.split("[[suite]]", 1)[0]
    comments = "\n".join(
        line.lstrip()[1:] for line in header.splitlines()
        if line.lstrip().startswith("#")
    )
    for key in ("name", "dir", "with", "extras", "pythons", "notes"):
        assert re.search(rf"\b{key}\b", comments)
    assert "sort" in comments.lower()
    assert "name" in comments.lower()
    assert "commit" in comments.lower()
    assert "lint" in comments.lower()
    assert re.search(r"\b(?:ninth|nine|9th|9)\b", comments.lower())


# spec: "Examples: `build`'s missing `build/.scratch/` in a fresh clone or worktree; `bayesian-workflow`'s `CALIBRATION_SWEEP=1` sweep and its expected arviz warnings; `llm-wiki`'s `@needs_pilot` tests and `$LLM_WIKI_ROOT`; `brainstorming`'s node skip; `tune-hyperparameters`' \"`--with sklearn` fails\"; `track-model-experiments`' run time; the guard's 3.9 floor, its launchd-PATH skips and its Gate B probe for `hooks`."
# task: 5
def test_real_registry_preserves_the_specified_operational_notes():
    notes = {
        suite.name: "\n".join(suite.notes)
        for suite in runner.parse(_read_real_registry())
    }
    required = {
        "build": ("build/.scratch/",),
        "bayesian-workflow": ("CALIBRATION_SWEEP=1", "arviz", "warn"),
        "llm-wiki": ("@needs_pilot", "$LLM_WIKI_ROOT"),
        "brainstorming": ("node", "skip"),
        "tune-hyperparameters": ("--with sklearn", "fail"),
        "hooks": ("3.9", "launchd", "PATH", "Gate B"),
    }
    for name, fragments in required.items():
        for fragment in fragments:
            assert fragment.lower() in notes[name].lower()
    assert re.search(
        r"\b(?:seconds?|minutes?|secs?|mins?|runtime)\b"
        r"|run time|\d+(?:\.\d+)?\s*(?:ms|s|m)\b",
        notes["track-model-experiments"].lower(),
    )


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 2
@pytest.mark.parametrize("name", EXPECTED)
def test_default_run_argv_matches_the_spec_inventory(name):
    runs = runner.runs(_suite(name))
    assert len(runs) == len(EXPECTED[name][3])
    for run, python in zip(runs, EXPECTED[name][3], strict=True):
        assert run.python == python
        assert run.argv == _argv(name, python)
        assert _shell_words(run.shell()) == [
            "cd", EXPECTED[name][0], "&&", *_argv(name, python)
        ]


# spec: "For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A` and `cd hooks && B`."
# task: 2
def test_hooks_has_two_separate_ordered_shell_commands():
    runs = runner.runs(_suite("hooks"))
    assert [run.python for run in runs] == ["3.13", "/usr/bin/python3"]
    for run, python in zip(runs, EXPECTED["hooks"][3], strict=True):
        assert run.shell() == "cd hooks && " + shlex.join(_argv("hooks", python))
        assert run.shell().count("&&") == 1


# spec: "**`--extras`** adds each suite's `extras` after its `with` deps."
# task: 2
@pytest.mark.parametrize("name", EXPECTED)
def test_extras_are_opt_in_and_follow_default_dependencies(name):
    default_runs = runner.runs(_suite(name), extras=False)
    extra_runs = runner.runs(_suite(name), extras=True)
    for default, extra, python in zip(
        default_runs, extra_runs, EXPECTED[name][3], strict=True
    ):
        assert default.argv == _argv(name, python, extras=False)
        assert extra.argv == _argv(name, python, extras=True)


# spec: "Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it."
# task: 2
def test_shell_quotes_dependency_operators_and_pytest_expressions():
    args = ("-k", "declared_dependencies or test_real_skill", "-s", "-rs")
    run = runner.runs(_suite("build"), extras=True, pytest_args=args)[0]
    expected = _argv("build", "3.13", extras=True, pytest_args=args)
    assert run.argv == expected
    assert _shell_words(run.shell()) == ["cd", "build", "&&", *expected]


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
@pytest.mark.parametrize(
    "args",
    [
        ("test_runtime_support.py::test_real_skill",),
        ("-k", "declared_dependencies"),
        ("-s", "-rs"),
    ],
)
def test_parse_args_preserves_pytest_arguments(args):
    namespace, pytest_args = runner.parse_args(["hooks", "--", *args])
    assert namespace is not None
    assert pytest_args == args


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_defaults_to_every_fixture_suite(fixture_root, capsys):
    root, data = fixture_root
    assert _invoke(["--list"], root) == 0
    output = capsys.readouterr().out
    for row in data["suite"]:
        name = row["name"]
        assert name in output
        assert row["dir"] in output
        for python in EXPECTED[name][3]:
            shell = f"cd {row['dir']} && " + shlex.join(_argv(name, python))
            assert shell in output
        for extra in row.get("extras", []):
            assert extra in output
        for note in row.get("notes", []):
            assert note in output


# spec: "**`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell form of each run, its extras, and its notes."
# task: 4
def test_list_limits_output_to_named_suites(fixture_root, capsys):
    root, _ = fixture_root
    assert _invoke(["--list", "hooks"], root) == 0
    output = capsys.readouterr().out
    for python in EXPECTED["hooks"][3]:
        assert "cd hooks && " + shlex.join(_argv("hooks", python)) in output
    assert "cd build &&" not in output
    assert "cd build/cc_guide &&" not in output
    assert "build/.scratch/" not in output


# spec: "`--extras` and the `--` arguments apply here too, so `--list` prints the exact command that a run would use."
# task: 4
def test_list_applies_extras_and_forwarded_pytest_arguments(fixture_root, capsys):
    root, _ = fixture_root
    args = ("-k", "declared_dependencies or test_real_skill", "-s", "-rs")
    assert _invoke(["--list", "build", "--extras", "--", *args], root) == 0
    output = capsys.readouterr().out
    shells = [
        line[line.index("cd "):]
        for line in output.splitlines()
        if "cd build && " in line
    ]
    assert len(shells) == 1
    assert _shell_words(shells[0]) == [
        "cd", "build", "&&",
        *_argv("build", "3.13", extras=True, pytest_args=args),
    ]


# spec: "**`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`."
# task: 4
def test_named_suites_run_in_requested_order_with_each_interpreter(fixture_root):
    root, _ = fixture_root
    seen = []

    def run_one(repo, run):
        assert repo == root
        seen.append((run.suite.name, run.python))
        return 0

    assert _invoke(["hooks", "build"], root, run_one) == 0
    assert seen == [
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
        ("build", "3.13"),
    ]


# spec: "Arguments after **`--`** go to pytest (a test node ID, `-k`, `-s`, `-rs`) in every run."
# task: 4
def test_cli_forwards_pytest_arguments_to_every_run(fixture_root):
    root, _ = fixture_root
    args = ("-k", "declared_dependencies", "-s", "-rs")
    seen = []

    def run_one(repo, run):
        seen.append(run)
        return 0

    assert _invoke(
        ["hooks", "build", "--extras", "--", *args], root, run_one
    ) == 0
    assert len(seen) == 3
    for run in seen:
        assert run.argv == _argv(
            run.suite.name, run.python, extras=True, pytest_args=args
        )


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_recognizes_directory_containment():
    build = _suite("build")
    nested = _suite("cc-guide")
    hooks = _suite("hooks")
    suites = [build, nested, hooks]
    assert runner.container(nested, suites) == build
    assert runner.container(build, suites) is None
    assert runner.container(hooks, suites) is None


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 2
def test_container_uses_path_components_instead_of_string_prefixes():
    build = _suite("build")
    sibling = runner.Suite(
        name="hooks", dir="build-other", deps=("pytest",)
    )
    assert runner.container(sibling, [build, sibling]) is None


# spec: "**`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`."
# task: 4
def test_all_skips_nested_suite_but_keeps_other_runs(fixture_root, capsys):
    root, _ = fixture_root
    seen = []

    def run_one(repo, run):
        seen.append((run.suite.name, run.python))
        return 0

    assert _invoke(["--all"], root, run_one) == 0
    assert seen == [
        ("build", "3.13"),
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
    ]
    output = capsys.readouterr().out
    skip_lines = [
        line for line in output.splitlines()
        if "cc-guide" in line and not line.startswith("== ")
    ]
    assert len(skip_lines) == 1


# spec: "A suite named on the command line always runs."
# task: 4
def test_explicitly_named_nested_suite_runs(fixture_root):
    root, _ = fixture_root
    seen = []

    def run_one(repo, run):
        seen.append((run.suite.name, run.python))
        return 0

    assert _invoke(["cc-guide"], root, run_one) == 0
    assert seen == [("cc-guide", "3.13")]


# spec: "A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`."
# task: 5
def test_real_cc_guide_suite_uses_the_hyphenated_public_name():
    seen = []

    def run_one(repo, run):
        seen.append((run.suite.name, run.suite.dir, run.python))
        return 0

    assert _invoke(["cc-guide"], ROOT, run_one) == 0
    assert seen == [("cc-guide", "build/cc_guide", "3.13")]
    assert _invoke(["cc_guide"], ROOT) == 2


# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize("argv", [["--unknown-option"], ["unknown-suite"]])
def test_usage_errors_and_unknown_suite_names_exit_two(fixture_root, argv):
    root, _ = fixture_root
    assert _invoke(argv, root) == 2


# spec: "**Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
# task: 4
@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        ((0, 0, 0), 0),
        ((1, 0, 0), 1),
        ((0, 5, 0), 1),
        ((0, 0, 2), 1),
    ],
)
def test_execute_aggregates_run_statuses_without_stopping(
    tmp_path, statuses, expected
):
    suites = [_suite("build"), _suite("hooks")]
    seen = []

    def run_one(repo, run):
        index = len(seen)
        seen.append((run.suite.name, run.python))
        return statuses[index]

    assert runner.execute(tmp_path, suites, False, (), run_one) == expected
    assert seen == [
        ("build", "3.13"),
        ("hooks", "3.13"),
        ("hooks", "/usr/bin/python3"),
    ]


# spec: "The last line names the failed runs, or says that every run passed."
# task: 4
@pytest.mark.parametrize("statuses", [(0, 0, 0), (1, 0, 5)])
def test_final_summary_reports_the_actual_failed_runs(tmp_path, statuses):
    seen = []
    output = io.StringIO()

    def run_one(repo, run):
        status = statuses[len(seen)]
        seen.append((run.suite.name, run.python))
        print(f"pytest output: {run.suite.name} ({run.python})")
        return status

    with redirect_stdout(output), redirect_stderr(output):
        runner.execute(
            tmp_path, [_suite("build"), _suite("hooks")], False, (), run_one
        )

    last = output.getvalue().splitlines()[-1]
    if all(status == 0 for status in statuses):
        assert re.search(r"\b(?:pass|passed)\b", last, re.IGNORECASE)
        assert not re.search(r"\b(?:fail|failed)\b", last, re.IGNORECASE)
    else:
        for (name, python), status in zip(seen, statuses, strict=True):
            label = f"{name} ({python})"
            if status:
                assert label in last
            else:
                assert label not in last


# spec: "Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header."
# task: 4
def test_headers_and_notes_precede_pytest_output(tmp_path):
    suite = runner.Suite(
        name="hooks",
        dir="hooks",
        deps=("pytest",),
        pythons=("3.13", "/usr/bin/python3"),
        notes=("3.9 floor", "launchd-PATH skips", "Gate B probe"),
    )
    output = io.StringIO()

    def run_one(repo, run):
        print(f"pytest output for {run.python}")
        return 0

    with redirect_stdout(output), redirect_stderr(output):
        assert runner.execute(tmp_path, [suite], False, (), run_one) == 0

    text = output.getvalue()
    first_header = text.index("== hooks (3.13)")
    first_output = text.index("pytest output for 3.13")
    second_header = text.index("== hooks (/usr/bin/python3)")
    second_output = text.index("pytest output for /usr/bin/python3")
    assert first_header < first_output < second_header < second_output
    for note in suite.notes:
        assert text.count(note) == 1
        assert first_header < text.index(note) < first_output


# spec: "A run whose `uv` cannot start counts as failed."
# task: 4
def test_missing_uv_is_a_failed_run_and_does_not_stop_later_runs(
    fixture_root, tmp_path, monkeypatch, capsys
):
    root, _ = fixture_root
    empty_path = tmp_path / "empty-path"
    empty_path.mkdir()
    monkeypatch.setenv("PATH", str(empty_path))
    assert _invoke(["hooks"], root, runner.run_subprocess) == 1
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "== hooks (3.13)" in combined
    assert "== hooks (/usr/bin/python3)" in combined
    assert "hooks (3.13)" in combined
    assert "hooks (/usr/bin/python3)" in combined


# spec: "The runner passes its environment to every run unchanged."
# task: 4
def test_subprocess_receives_unchanged_environment_for_every_run(
    fixture_root, fake_uv
):
    root, _ = fixture_root
    expected_environment = dict(os.environ)
    assert _invoke(["hooks", "build"], root, runner.run_subprocess) == 0
    records = [
        json.loads(line)
        for line in fake_uv.read_text(encoding="utf-8").splitlines()
    ]
    assert len(records) == 3
    for record in records:
        assert record["env"] == expected_environment
        assert record["env"]["CALIBRATION_SWEEP"] == "1"


# spec: "Its command is `uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its working directory."
# task: 4
def test_subprocess_uses_suite_directory_and_exact_argv(
    fixture_root, fake_uv
):
    root, _ = fixture_root
    args = ("-k", "declared_dependencies", "-s", "-rs")
    assert _invoke(
        ["build", "--extras", "--", *args], root, runner.run_subprocess
    ) == 0
    records = [
        json.loads(line)
        for line in fake_uv.read_text(encoding="utf-8").splitlines()
    ]
    assert len(records) == 1
    assert records[0]["cwd"] == str((root / "build").resolve())
    assert records[0]["argv"] == list(
        _argv("build", "3.13", extras=True, pytest_args=args)[1:]
    )


# spec: "Then pytest's output streams."
# task: 4
def test_subprocess_output_reaches_the_callers_streams(
    fixture_root, fake_uv, capfd
):
    root, _ = fixture_root
    run = runner.runs(_suite("build"))[0]
    assert runner.run_subprocess(root, run) == 0
    captured = capfd.readouterr()
    assert "pytest output streams" in captured.out
    assert "pytest stderr streams" in captured.err


# spec: "It finds the repo root from its own path, never from the working directory."
# task: 4
def test_default_root_and_script_listing_work_from_another_directory(tmp_path):
    assert ROOT.resolve() == RUNNER_FILE.parent.parent
    result = subprocess.run(
        [sys.executable, str(RUNNER_FILE), "--list", "hooks"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    for python in EXPECTED["hooks"][3]:
        assert "cd hooks && " + shlex.join(_argv("hooks", python)) in result.stdout


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_reports_a_missing_registered_directory(tmp_path):
    row = _row("brainstorming")
    data = {"suite": [row]}
    _write_data(tmp_path, data)
    _git(tmp_path, "init", "-q")
    findings = runner.check(tmp_path, data)
    assert findings
    assert any(row["dir"] in finding for finding in findings)


# spec: "**registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;"
# task: 3
def test_check_reports_a_registered_directory_without_pytest_files(tmp_path):
    row = _row("brainstorming")
    data = {"suite": [row]}
    _write_data(tmp_path, data)
    directory = tmp_path / row["dir"]
    directory.mkdir(parents=True)
    (directory / "runner.py").write_text("pass\n", encoding="utf-8")
    _git(tmp_path, "init", "-q")
    findings = runner.check(tmp_path, data)
    assert findings
    assert any(row["dir"] in finding for finding in findings)


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize("filename", ["test_new.py", "new_test.py"])
def test_check_reports_each_default_pytest_filename_pattern(tmp_path, filename):
    data = _make_git_root(tmp_path, [_row("brainstorming")])
    directory = tmp_path / "skills/write-with-asd-ste100/scripts"
    directory.mkdir(parents=True)
    (directory / filename).write_text("pass\n", encoding="utf-8")
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert "skills/write-with-asd-ste100/scripts" in findings[0]


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
@pytest.mark.parametrize(
    "filename", ["test.py", "test_new.txt", "contest_new.py", "new_test.py.bak"]
)
def test_non_pytest_filenames_do_not_create_coverage_findings(tmp_path, filename):
    data = _make_git_root(tmp_path, [_row("brainstorming")])
    directory = tmp_path / "skills/write-with-asd-ste100/scripts"
    directory.mkdir(parents=True)
    (directory / filename).write_text("pass\n", encoding="utf-8")
    assert runner.check(tmp_path, data) == []


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_registered_parent_covers_nested_test_directories(tmp_path):
    data = _make_git_root(tmp_path, [_row("build")])
    nested = tmp_path / "build/cc_guide"
    nested.mkdir()
    (nested / "test_new.py").write_text("pass\n", encoding="utf-8")
    assert runner.check(tmp_path, data) == []


# spec: "**coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default patterns) and does not lie inside any registered `dir`."
# task: 3
def test_coverage_containment_respects_directory_boundaries(tmp_path):
    data = _make_git_root(tmp_path, [_row("build")])
    sibling = tmp_path / "build-other"
    sibling.mkdir()
    (sibling / "test_new.py").write_text("pass\n", encoding="utf-8")
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert "build-other" in findings[0]


# spec: "Ignored trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out."
# task: 3
def test_ignored_worktrees_scratch_and_other_trees_are_excluded(tmp_path):
    data = _make_git_root(tmp_path, [_row("brainstorming")])
    (tmp_path / ".gitignore").write_text(
        ".claude/worktrees/\nbuild/.scratch/\nignored/\n", encoding="utf-8"
    )
    for relative in (
        ".claude/worktrees/new-suite",
        "build/.scratch/new-suite",
        "ignored/new-suite",
    ):
        directory = tmp_path / relative
        directory.mkdir(parents=True)
        (directory / "test_new.py").write_text("pass\n", encoding="utf-8")
    assert runner.check(tmp_path, data) == []


# spec: "Untracked new suites count, as the hook's other lints read untracked drafts too."
# task: 3
def test_untracked_test_directory_is_reported(tmp_path):
    data = _make_git_root(tmp_path, [_row("brainstorming")])
    relative = "skills/write-with-asd-ste100/scripts/test_new.py"
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text("pass\n", encoding="utf-8")
    assert _git(tmp_path, "ls-files", "--", relative).stdout == ""
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert str(Path(relative).parent) in findings[0]


# spec: "The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root."
# task: 3
def test_cached_files_are_checked_even_after_their_tree_becomes_ignored(tmp_path):
    data = _make_git_root(tmp_path, [_row("brainstorming")])
    relative = "skills/write-with-asd-ste100/scripts/test_new.py"
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text("pass\n", encoding="utf-8")
    _git(tmp_path, "add", "--", relative)
    (tmp_path / ".gitignore").write_text(
        "skills/write-with-asd-ste100/\n", encoding="utf-8"
    )
    findings = runner.check(tmp_path, data)
    assert len(findings) == 1
    assert str(Path(relative).parent) in findings[0]


# spec: "The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root."
# task: 3
def test_git_discovery_is_independent_of_callers_working_directory(
    tmp_path, monkeypatch
):
    root = tmp_path / "repo"
    root.mkdir()
    data = _make_git_root(root, [_row("brainstorming")])
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert runner.check(root, data) == []


# spec: "If git fails, `--check` fails."
# task: 3
def test_git_failure_is_a_finding_and_a_failed_check(
    fixture_root, tmp_path, monkeypatch
):
    root, data = fixture_root
    binary_dir = tmp_path / "failing-git"
    binary_dir.mkdir()
    executable = binary_dir / "git"
    executable.write_text(
        f"#!{sys.executable}\nimport sys\nsys.exit(1)\n", encoding="utf-8"
    )
    executable.chmod(0o755)
    monkeypatch.setenv(
        "PATH", str(binary_dir) + os.pathsep + os.environ["PATH"]
    )
    assert runner.check(root, data)
    assert _invoke(["--check"], root) == 1


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_successful_check_prints_the_specified_success_line(tmp_path, capsys):
    _make_git_root(tmp_path)
    assert _invoke(["--check"], tmp_path) == 0
    captured = capsys.readouterr()
    assert captured.out == "suite registry ok\n"
    assert captured.err == ""


# spec: "Output: `suite registry ok` and exit 0, or one line per finding and exit 1."
# task: 4
def test_failed_check_prints_exactly_one_line_per_finding(tmp_path):
    data = _make_git_root(tmp_path, [_row("brainstorming")])
    for relative in ("hooks", "skills/write-with-asd-ste100/scripts"):
        directory = tmp_path / relative
        directory.mkdir(parents=True)
        (directory / "test_new.py").write_text("pass\n", encoding="utf-8")
    expected = runner.check(tmp_path, data)
    assert len(expected) == 2
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        assert _invoke(["--check"], tmp_path) == 1
    assert sorted(output.getvalue().splitlines()) == sorted(expected)


# spec: "the real registry: `--check` passes on the repo."
# task: 5
def test_real_registry_check_passes(capsys):
    assert runner.check(ROOT, _read_real_registry()) == []
    assert _invoke(["--check"], ROOT) == 0
    captured = capsys.readouterr()
    assert captured.out == "suite registry ok\n"
    assert captured.err == ""


# spec: "With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character."
# task: 5
def test_default_commands_match_the_specified_historical_commands():
    original = _historical("CLAUDE.md").splitlines()
    command_lines = original[65:125] + original[144:145]
    original_commands = _directory_commands(command_lines)
    actual_commands = [
        run.shell()
        for suite in runner.parse(_read_real_registry())
        if suite.name in EXPECTED
        for run in runner.runs(suite)
    ]
    assert original_commands
    assert len(original_commands) == len(actual_commands)
    assert set(original_commands) == set(actual_commands)


# spec: "Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason."
# task: 7
def test_root_intro_retains_execution_rules_and_collision_reason():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    paragraphs = text.split("\n\n")
    candidates = [
        paragraph for paragraph in paragraphs
        if "test_build.py" in paragraph
        and "build/suites.toml" in paragraph
        and "build/run_suites.py" in paragraph
    ]
    assert len(candidates) == 1
    intro = candidates[0]
    assert len(intro.splitlines()) == 1
    assert "uv" in intro
    assert "3.13" in intro
    assert "director" in intro.lower()
    assert re.search(
        r"basename|colli(?:de|sion)|same[- ]name", intro, re.IGNORECASE
    )


# spec: "Name `build/suites.toml` and `build/run_suites.py`, and say that the runner prints a suite's notes before it runs."
# task: 7
def test_root_intro_explains_when_notes_are_printed():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    intro = next(
        paragraph for paragraph in text.split("\n\n")
        if "test_build.py" in paragraph and "build/run_suites.py" in paragraph
    )
    assert "build/suites.toml" in intro
    assert "notes" in intro.lower()
    assert "before" in intro.lower()
    assert "There is no root test runner" not in intro


# spec: "Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands."
# task: 7
def test_root_commands_block_contains_the_four_runner_commands():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    prefix = "uv run --python 3.13 python build/run_suites.py "
    for suffix in (
        "--list",
        "<name> [--extras] [-- <pytest args>]",
        "--all",
        "--check",
    ):
        assert prefix + suffix in text


# spec: "`CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines."
# task: 7
def test_root_doc_has_no_literal_directory_suite_commands_and_is_under_limit():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert _directory_commands(text.splitlines()) == []


# spec: "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
# task: 7
def test_root_doc_does_not_claim_suite_or_test_counts():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    numbers = (
        r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
        r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen"
    )
    assert not re.search(
        rf"\b(?:{numbers})\s+(?:directory\s+)?(?:suites?|tests?)\b",
        text,
        re.IGNORECASE,
    )


# spec: "These commands **stay literal in `CLAUDE.md`**."
# task: 7
def test_historical_non_suite_command_lines_remain_literal():
    original = _historical("CLAUDE.md").splitlines()
    current = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()
    literal_lines = []
    for line in original:
        stripped = line.strip()
        if not re.match(r"^(?:uv run |cd \S+ && |bash |python )", stripped):
            continue
        if not _directory_commands([line]):
            literal_lines.append(line)
    assert literal_lines
    for line in literal_lines:
        assert line in current


# spec: "`build/run_commit_lints.sh` keeps its literal commands."
# task: 6
def test_existing_commit_lint_commands_are_unchanged_and_ninth_is_appended():
    original = _historical("build/run_commit_lints.sh")
    current = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    original_runs = [
        line.strip() for line in original.splitlines()
        if line.lstrip().startswith("run ")
    ]
    current_runs = [
        line.strip() for line in current.splitlines()
        if line.lstrip().startswith("run ")
    ]
    assert current_runs[:-1] == original_runs
    assert len(current_runs) == 9
    assert current_runs[-1] == (
        "run suite_registry uv run --python 3.13 "
        "python build/run_suites.py --check"
    )
    runner_calls = [line for line in current_runs if "run_suites.py" in line]
    assert runner_calls == [current_runs[-1]]


# spec: "Its header says \"nine\"."
# task: 6
def test_commit_lint_script_header_says_nine():
    text = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    header = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            header.append(line)
        else:
            break
    assert re.search(r"\bnine\b", "\n".join(header), re.IGNORECASE)


# spec: "`suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint."
# task: 6
def test_commit_lint_test_inventory_includes_suite_registry():
    path = ROOT / "build/test_commit_lints.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assignments = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == "CHECKS"
                for target in node.targets
            ):
                assignments.append(node.value)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "CHECKS":
                assignments.append(node.value)
    assert assignments
    assert any(
        isinstance(node, ast.Constant) and node.value == "suite_registry"
        for value in assignments
        for node in ast.walk(value)
    )
    assert any(
        isinstance(node, ast.FunctionDef)
        and node.name == "test_unregistered_suite_is_refused"
        for node in ast.walk(tree)
    )


# spec: "`build/CLAUDE.md`: \"the eight commit lints\" becomes \"the nine commit lints\", and one sentence names `suites.toml` and `run_suites.py` and says that `--check` is a commit lint."
# task: 6
def test_build_doc_describes_registry_and_ninth_commit_lint():
    text = (ROOT / "build/CLAUDE.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "the eight commit lints" not in normalized
    assert "the nine commit lints" in normalized
    paragraphs = [" ".join(paragraph.split()) for paragraph in text.split("\n\n")]
    assert any(
        all(fragment in paragraph for fragment in (
            "suites.toml", "run_suites.py", "--check", "commit lint"
        ))
        for paragraph in paragraphs
    )


# spec: "The commit-lint comment names the suite-registry check and says \"nine\"."
# task: 7
def test_root_commit_lint_comment_names_the_new_check_and_count():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    comment_groups = re.findall(r"(?:^[ \t]*#.*(?:\n|$))+", text, re.MULTILINE)
    assert any(
        re.search(r"\bnine\b", group, re.IGNORECASE)
        and re.search(r"suite[-_ ]registry", group, re.IGNORECASE)
        for group in comment_groups
    )


# spec: "The comment names the suite `run_suites.py cc-guide` instead of \"its suite\"."
# task: 7
def test_cc_guide_comment_uses_the_specified_runner_suite_name():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    comments = [
        line for line in text.splitlines()
        if line.lstrip().startswith("#")
    ]
    assert any("run_suites.py cc-guide" in line for line in comments)
</tests>
<flags>
<flag task="1"><spec>A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`.</spec><plan>a spec that names the suite `cc_guide`.</plan></flag>
<flag task="2"><spec>Default `['3.13']`.</spec><plan>DEFAULT_PYTHONS = ('3.12',)</plan></flag>
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
A registry removes the per-suite growth.
Worktree-isolated sessions and their subagents have refused compound shell such as `cd X && Y` (seen on 2026-10-12).
The owner took these decisions on 2026-10-18.
Each records the option that the owner chose.
"`run_suites.py --check` joins build/run_commit_lints.sh, so the pre-commit hook and CI run it."
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
They are selections or tools, not directory suites, and their comments say when to run them:
Every command, dependency and note survives; the only change is the form.
The notes carry the rest of each comment.
A misspelled key can therefore never run a suite without its deps.
Drop "There is no root test runner" and the sentence that comments name the skip-unlocking deps.
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
`suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused` commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only failed lint.
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
It also checks each comment's skip-unlocking deps against that suite's `extras`.
Run `hooks`, `build` and `bayesian-workflow` once directly and once through the runner, in the same checkout.
Their pytest summary lines match.
Then run `--all` once, and record each run's result beside the direct result.
The build suite passes (where the missing `build/.scratch/` lets it).
`bash build/run_commit_lints.sh` prints `commit lints passed`.
`build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`.
The Stage 2 audit passes, and the behaviour runs match.
The shared note for plan 52 (R7.1) is written.
Agents no longer see each suite's notes at session start.
No commit can add a test directory without a registry entry, plan 52's new suite included.
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