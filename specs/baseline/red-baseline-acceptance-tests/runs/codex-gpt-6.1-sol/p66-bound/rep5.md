<tests>
import datetime as dt
import importlib
import json
import os
import re
import shlex
import subprocess
import sys
import textwrap
import urllib.error
from pathlib import Path
from types import SimpleNamespace

import pytest


MANIFEST = """\
[python]
dev = '3.13'

[freeze]
date = 2026-10-19

[packages]
arviz = '1.3.0'
arviz-base = '1.3.1'
arviz-stats = '1.3.3'
arviz-plots = '1.3.2'
numpyro = '0.22.0'
jax = '0.12.0'
jaxlib = '0.11.2'
flax = '0.12.10'
optax = '0.2.8'
orbax-checkpoint = '0.12.6'
equinox = '0.13.8'
diffrax = '0.7.2'
e3nn-jax = '0.21.0'
numpy = '2.5.3'
matplotlib = '3.11.2'
polars = '2.0.0'

[cited]
altair = '6.2'
plotly = '6.8'
optuna = '5.0.0'
great-docs = '0.17.0'

[gates]
snippets = ['arviz', 'arviz-base', 'arviz-stats', 'arviz-plots', 'numpyro', 'jax', 'numpy', 'matplotlib']
jax-cpu = ['jax', 'jaxlib', 'flax', 'optax', 'orbax-checkpoint', 'equinox', 'diffrax', 'e3nn-jax', 'numpy']
"""

SKILL = """\
---
name: bayesian-workflow
description: Bayesian workflow.
compatibility: Python 3.12+
---
"""

SCRIPT = """\
# /// script
# requires-python = ">=3.12"
# dependencies = ["arviz>=1.0"]
# ///
"""


@pytest.fixture
def project(pytestconfig):
    return Path(pytestconfig.rootpath)


@pytest.fixture
def versions(project, monkeypatch):
    monkeypatch.syspath_prepend(str(project / "build"))
    return importlib.import_module("versions")


@pytest.fixture
def checker(versions):
    return importlib.import_module("versions_check")


@pytest.fixture
def suites(versions):
    return importlib.import_module("run_suites")


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def track(root):
    subprocess.run(
        ["git", "-C", str(root), "add", "--all"],
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def root(tmp_path, versions):
    subprocess.run(
        ["git", "init", "--quiet", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    write(tmp_path, "build/versions.toml", MANIFEST)
    write(tmp_path, "CLAUDE.md", "")
    write(tmp_path, "AGENTS.md", "")
    write(tmp_path, "GEMINI.md", "")
    write(tmp_path, "skills/bayesian-workflow/SKILL.md", SKILL)
    write(
        tmp_path,
        "skills/bayesian-workflow/scripts/diagnose_model.py",
        SCRIPT,
    )
    versions.sync(tmp_path)
    track(tmp_path)
    return tmp_path


def findings(checker, root, historical=None):
    track(root)
    return checker.check(root=root, historical=historical)


def option(argv, name):
    for index, value in enumerate(argv):
        if value == name:
            return argv[index + 1]
        if value.startswith(name + "="):
            return value.split("=", 1)[1]
    return None


def with_specs(argv):
    result = []
    for index, value in enumerate(argv):
        if value == "--with":
            result.extend(argv[index + 1].split(","))
        elif value.startswith("--with="):
            result.extend(value.split("=", 1)[1].split(","))
    return result


def output(capsys):
    captured = capsys.readouterr()
    return captured.out + captured.err


def metadata(v, url):
    parts = url.rstrip("/").split("/")
    name = parts[parts.index("pypi") + 1]
    latest = dict(v.packages)
    latest.update(v.cited)
    latest.update(
        {
            "jax": "0.12.0.1",
            "altair": "6.3.0",
            "plotly": "7.1.0",
        }
    )
    current = {**v.packages, **v.cited}[name]
    releases = {}
    for version in {current, latest[name]}:
        day = "2026-10-21" if version == "0.12.0.1" else "2026-09-18"
        releases[version] = [
            {
                "filename": f"{name}-{version}-py3-none-any.whl",
                "upload_time_iso_8601": day + "T00:00:00Z",
                "upload_time": day + "T00:00:00",
                "yanked": False,
                "requires_python": None,
            }
        ]
    return {
        "info": {"name": name, "version": latest[name]},
        "releases": releases,
        "urls": releases[current],
    }


@pytest.fixture
def stub_uv(tmp_path, root, versions, monkeypatch):
    directory = tmp_path / "bin"
    directory.mkdir()
    log = tmp_path / "uv.jsonl"
    executable = directory / "uv"
    executable.write_text(
        "#!" + sys.executable + "\n" + textwrap.dedent(
            """\
            import json
            import os
            import sys
            from pathlib import Path

            args = sys.argv[1:]
            with open(os.environ["ACCEPTANCE_UV_LOG"], "a", encoding="utf-8") as stream:
                stream.write(json.dumps(args) + "\\n")

            failure = os.environ.get("ACCEPTANCE_UV_FAILURE", "")
            compiling = "pip" in args and "compile" in args

            if compiling and failure == "resolve":
                print("joint resolve conflict: jax numpyro", file=sys.stderr)
                raise SystemExit(1)

            if compiling:
                pins = json.loads(os.environ["ACCEPTANCE_UV_PINS"])
                content = "".join(
                    name + "==" + version + "\\n"
                    for name, version in sorted(pins.items())
                )
                destination = None
                for index, value in enumerate(args):
                    if value in ("-o", "--output-file"):
                        destination = args[index + 1]
                    elif value.startswith("--output-file="):
                        destination = value.split("=", 1)[1]
                if destination and destination != "-":
                    Path(destination).write_text(content, encoding="utf-8")
                else:
                    print(content, end="")
                raise SystemExit(0)

            if failure == "run" and "run" in args:
                print("gate failed", file=sys.stderr)
                raise SystemExit(1)

            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    executable.chmod(0o755)
    v = versions.load(root)
    monkeypatch.setenv("PATH", str(directory) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("ACCEPTANCE_UV_LOG", str(log))
    monkeypatch.setenv("ACCEPTANCE_UV_PINS", json.dumps(v.packages))
    monkeypatch.setenv("ACCEPTANCE_UV_FAILURE", "")
    return SimpleNamespace(
        log=log,
        calls=lambda: [
            json.loads(line)
            for line in log.read_text(encoding="utf-8").splitlines()
        ] if log.exists() else [],
    )


# spec: "R1.1. `build/versions.toml` is the only file in which a person sets a package version or the dev interpreter."
# task: 2
def test_parse_preserves_the_manifest_values(versions):
    v = versions.parse(MANIFEST)
    assert v.dev_python == "3.13"
    assert v.freeze == dt.date(2026, 10, 19)
    assert v.packages["numpyro"] == "0.22.0"
    assert v.packages["jax"] == "0.12.0"
    assert v.cited["altair"] == "6.2"


@pytest.mark.parametrize(
    ("before", "after", "key"),
    [
        ("dev = '3.13'", "", "dev"),
        ("date = 2026-10-19", "", "date"),
        ("dev = '3.13'", "dev = 3.13", "dev"),
        ("date = 2026-10-19", "date = '2026-10-19'", "date"),
        ("arviz = '1.3.0'", "arviz = '>=1.0'", "arviz"),
    ],
)
# spec: "A missing or invalid file names the key."
# task: 2
def test_schema_errors_identify_the_key(versions, before, after, key):
    with pytest.raises(versions.VersionsError) as caught:
        versions.parse(MANIFEST.replace(before, after))
    assert key in str(caught.value)


@pytest.mark.parametrize("location", ["gate", "override"])
# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
def test_unknown_packages_are_rejected_by_name(versions, location):
    text = MANIFEST
    if location == "gate":
        text = text.replace(
            "snippets = ['arviz',",
            "snippets = ['pytest', 'arviz',",
        )
    else:
        text += """
[[override]]
gate = 'snippets'
package = 'pytest'
version = '1.3.0'
reason = 'The JAX CPU examples must pass on it.'
"""
    with pytest.raises(versions.VersionsError) as caught:
        versions.parse(text)
    assert "pytest" in str(caught.value)


@pytest.mark.parametrize("missing", ["gate", "package", "version", "reason"])
# spec: "R1.4. A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_overrides_require_all_four_keys(versions, missing):
    entries = {
        "gate": "'jax-cpu'",
        "package": "'jax'",
        "version": "'0.11.2'",
        "reason": "'The JAX CPU examples must pass on it.'",
    }
    text = MANIFEST + "\n[[override]]\n" + "\n".join(
        f"{key} = {value}"
        for key, value in entries.items()
        if key != missing
    )
    with pytest.raises(versions.VersionsError) as caught:
        versions.parse(text)
    assert missing in str(caught.value)


# spec: "R2.2. `build/versions.py` gives the other build scripts these values: the dev Python, the freeze date, and `stack(gate)`, the list of `pkg==version` strings for a gate after overrides."
# task: 2
def test_stack_uses_manifest_pins_in_gate_order(versions):
    v = versions.parse(MANIFEST)
    assert v.stack("snippets") == [
        "arviz==1.3.0",
        "arviz-base==1.3.1",
        "arviz-stats==1.3.3",
        "arviz-plots==1.3.2",
        "numpyro==0.22.0",
        "jax==0.12.0",
        "numpy==2.5.3",
        "matplotlib==3.11.2",
    ]


# spec: "R1.4. A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_override_affects_only_its_gate(versions):
    v = versions.parse(
        MANIFEST + """
[[override]]
gate = 'jax-cpu'
package = 'jax'
version = '0.11.2'
reason = 'The JAX CPU examples must pass on it.'
"""
    )
    assert "jax==0.11.2" in v.stack("jax-cpu")
    assert "jax==0.12.0" in v.stack("snippets")
    assert v.packages["jax"] == "0.12.0"


# spec: "Polars is in `[packages]` by the second case: the suites install it, and three headers floor it."
# task: 4
def test_real_manifest_includes_polars(project, versions):
    assert "polars" in versions.load(project).packages


# spec: "Other packages (pytest, pyyaml, scipy, tensorstore and the rest) get no entry, and the freeze date fixes them."
# task: 4
def test_real_manifest_does_not_pin_the_named_floating_packages(project, versions):
    packages = versions.load(project).packages
    assert {"pytest", "pyyaml", "scipy", "tensorstore"}.isdisjoint(packages)


# spec: "R1.5. The file does not hold the script floors (`requires-python`, `compatibility:`) or the 3.9 floor of `install.py` and the read-only agent guard."
# task: 4
def test_manifest_python_table_contains_only_the_dev_interpreter(project):
    import tomllib

    data = tomllib.loads(
        (project / "build/versions.toml").read_text(encoding="utf-8")
    )
    assert set(data["python"]) == {"dev"}
    assert "requires-python" not in data
    assert "compatibility" not in data


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_writes_only_the_three_specified_outputs(root, versions):
    expected = versions.outputs(versions.load(root))
    assert set(expected) == {".python-version", "uv.toml", "skills/uv.toml"}
    for relative, text in expected.items():
        assert (root / relative).read_text(encoding="utf-8") == text


# spec: "Every `uv run` in the repo uses the dev interpreter with no `--python` flag, from any subdirectory"
# task: 2
def test_python_version_output_is_the_dev_value(root):
    assert (root / ".python-version").read_text(encoding="utf-8") == "3.13\n"


# spec: "Files uploaded on the freeze date itself (UTC) are included."
# task: 2
def test_cutoff_is_midnight_utc_after_the_freeze_date(root, versions):
    import tomllib

    v = versions.load(root)
    assert v.cutoff == "2026-10-20T00:00:00Z"
    data = tomllib.loads((root / "uv.toml").read_text(encoding="utf-8"))
    assert data["exclude-newer"] == "2026-10-20T00:00:00Z"


# spec: "It shadows the root date under `skills/`, so a skill script that a user runs floats within its floors (D8), whatever the path form"
# task: 2
def test_skills_shadow_has_no_settings_and_names_the_source(root):
    import tomllib

    text = (root / "skills/uv.toml").read_text(encoding="utf-8")
    assert tomllib.loads(text) == {}
    assert any(
        line.lstrip().startswith("#") and "build/versions.toml" in line
        for line in text.splitlines()
    )


@pytest.mark.parametrize(
    "relative",
    [".python-version", "uv.toml", "skills/uv.toml"],
)
# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_check_detects_even_semantically_equivalent_edits(
    root, versions, relative
):
    path = root / relative
    stale = path.read_text(encoding="utf-8") + "\n"
    path.write_text(stale, encoding="utf-8")
    assert versions.main(["sync", "--check"], root=root) != 0
    assert path.read_text(encoding="utf-8") == stale
    assert versions.main(["sync"], root=root) == 0
    assert versions.main(["sync", "--check"], root=root) == 0


# spec: "Sets the freeze date (default: today, UTC) and does one joint resolve, as of that date and on the dev Python, of every `[packages]` entry together."
# task: 3
def test_bump_resolves_all_packages_together_on_the_dev_python(root, versions):
    before = versions.load(root)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((list(requirements), python_version, cutoff))
        return {**before.packages, "jax": "0.12.0.1"}

    versions.bump(
        root,
        dt.date(2026, 10, 21),
        resolver=resolver,
    )
    after = versions.load(root)
    assert len(calls) == 1
    requirements, python_version, cutoff = calls[0]
    assert set(requirements) == set(before.packages)
    assert python_version == before.dev_python
    assert cutoff in {
        dt.date(2026, 10, 21),
        "2026-10-21",
        "2026-10-22T00:00:00Z",
    }
    assert after.freeze == dt.date(2026, 10, 21)
    assert after.packages["jax"] == "0.12.0.1"
    assert versions.main(["sync", "--check"], root=root) == 0


# spec: "With `--only`, the other entries stay at their pins in the joint resolve."
# task: 3
def test_bump_only_preserves_other_pins_in_the_joint_resolve(root, versions):
    before = versions.load(root)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append(list(requirements))
        return {**before.packages, "jax": "0.12.0.1"}

    versions.bump(
        root,
        dt.date(2026, 10, 21),
        only=("jax",),
        resolver=resolver,
    )
    assert len(calls) == 1
    assert set(calls[0]) == {"jax"} | {
        f"{name}=={version}"
        for name, version in before.packages.items()
        if name != "jax"
    }
    after = versions.load(root)
    for name, version in before.packages.items():
        assert after.packages[name] == (
            "0.12.0.1" if name == "jax" else version
        )


# spec: "R3.2. `bump` never changes `[cited]`."
# task: 3
def test_bump_preserves_cited_entries(root, versions):
    before = versions.load(root)

    def resolver(requirements, python_version, cutoff):
        return {**before.packages, "jax": "0.12.0.1"}

    versions.bump(root, dt.date(2026, 10, 21), resolver=resolver)
    assert versions.load(root).cited == before.cited


# spec: "Sets the freeze date (default: today, UTC) and does one joint resolve, as of that date and on the dev Python, of every `[packages]` entry together."
# task: 3
def test_bump_default_date_is_today_in_utc(root, versions, stub_uv):
    before = dt.datetime.now(dt.timezone.utc).date()
    assert versions.main(["bump"], root=root) == 0
    after = dt.datetime.now(dt.timezone.utc).date()
    assert versions.load(root).freeze in {before, after}


# spec: "An invalid date names the value."
# task: 3
def test_invalid_date_identifies_the_rejected_value(root, versions, capsys):
    assert versions.main(["bump", "--date", "3.13"], root=root) != 0
    assert "3.13" in output(capsys)


# spec: "Runs `<cmd>` under `uv run` with the gate's stack and the freeze date"
# task: 5
def test_run_argv_contains_the_stack_freeze_and_unchanged_command(
    root, versions
):
    v = versions.load(root)
    tail = [
        "python",
        "build/check_snippets.py",
        "--run",
        "skills/bayesian-workflow/",
    ]
    argv = versions.uv_run_argv(v, "snippets", tail)
    assert argv[0] == "uv"
    assert "run" in argv
    assert with_specs(argv) == v.stack("snippets")
    assert option(argv, "--exclude-newer") in {
        v.freeze.isoformat(),
        v.cutoff,
    }
    assert argv[-len(tail):] == tail


# spec: "R3.3. `--pin` changes one package for one run and never edits the file."
# task: 5
def test_run_pin_is_temporary(root, versions, stub_uv, monkeypatch):
    before = {
        path: (root / path).read_bytes()
        for path in [
            "build/versions.toml",
            ".python-version",
            "uv.toml",
            "skills/uv.toml",
        ]
    }
    monkeypatch.setattr(versions, "late_pins", lambda *args, **kwargs: [])
    assert versions.main(
        [
            "run",
            "snippets",
            "--pin",
            "jax==0.11.2",
            "--",
            "python",
            "build/check_snippets.py",
            "--run",
            "skills/bayesian-workflow/",
        ],
        root=root,
    ) == 0
    specs = with_specs(stub_uv.calls()[-1])
    assert "jax==0.11.2" in specs
    assert "jax==0.12.0" not in specs
    assert all((root / path).read_bytes() == data for path, data in before.items())


# spec: "A pin uploaded after the freeze date names the package and the date."
# task: 5
def test_run_rejects_a_pin_uploaded_after_the_freeze_date(
    root, versions, stub_uv, monkeypatch, capsys
):
    v = versions.load(root)
    monkeypatch.setattr(
        versions,
        "fetch_json",
        lambda url: metadata(v, url),
    )
    assert versions.main(
        [
            "run",
            "snippets",
            "--pin",
            "jax==0.12.0.1",
            "--",
            "python",
            "build/check_snippets.py",
            "--run",
            "skills/bayesian-workflow/",
        ],
        root=root,
    ) != 0
    message = output(capsys)
    assert "jax" in message
    assert "2026-10-21" in message or "2026-10-19" in message
    assert not any("run" in call for call in stub_uv.calls())


# spec: "Files uploaded on the freeze date itself (UTC) are included."
# task: 5
def test_upload_on_the_freeze_day_is_not_late(root, versions):
    v = versions.load(root)

    def fetch(url):
        files = [
            {
                "filename": "jax-0.12.0-py3-none-any.whl",
                "upload_time_iso_8601": "2026-10-19T23:59:59Z",
                "upload_time": "2026-10-19T23:59:59",
                "yanked": False,
            }
        ]
        return {
            "info": {"name": "jax", "version": "0.12.0"},
            "releases": {"0.12.0": files},
            "urls": files,
        }

    assert versions.late_pins(v, ["jax==0.12.0"], fetch=fetch) == []


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 5
def test_run_propagates_a_failed_command(
    root, versions, stub_uv, monkeypatch
):
    monkeypatch.setattr(versions, "late_pins", lambda *args, **kwargs: [])
    monkeypatch.setenv("ACCEPTANCE_UV_FAILURE", "run")
    assert versions.main(
        [
            "run",
            "snippets",
            "--",
            "python",
            "build/check_snippets.py",
            "--run",
            "skills/bayesian-workflow/",
        ],
        root=root,
    ) != 0


# spec: "A command that needs a pinned stack uses the runner (R3):"
# task: 5
def test_documented_runner_form_matches_the_spec_example(versions):
    command = versions.runner_command(
        "snippets",
        "python build/check_snippets.py --run skills/bayesian-workflow/",
    )
    assert shlex.split(command) == [
        "uv",
        "run",
        "python",
        "build/versions.py",
        "run",
        "snippets",
        "--",
        "python",
        "build/check_snippets.py",
        "--run",
        "skills/bayesian-workflow/",
    ]


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 8
def test_verify_tier_two_is_unpinned_and_frozen(root, versions):
    v = versions.load(root)
    steps = versions.verify_steps(v)
    tier_two = [step for step in steps if "--api" in step.argv]
    assert len(tier_two) == 1
    argv = tier_two[0].argv
    assert not any("==" in spec for spec in with_specs(argv))
    assert option(argv, "--exclude-newer") in {
        v.freeze.isoformat(),
        v.cutoff,
    }


# spec: "Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`"
# task: 8
def test_verify_contains_all_four_required_checks(root, versions):
    v = versions.load(root)
    steps = versions.verify_steps(v)
    assert len(steps) == 4
    assert sum("--api" in step.argv for step in steps) == 1
    tier_three = [step for step in steps if "--run" in step.argv]
    assert len(tier_three) == 1
    assert with_specs(tier_three[0].argv) == v.stack("snippets")
    jax = [
        step
        for step in steps
        if any(Path(arg).name == "check_jax_examples.py" for arg in step.argv)
    ]
    assert len(jax) == 1
    assert with_specs(jax[0].argv) == v.stack("jax-cpu")
    suite_steps = [
        step
        for step in steps
        if any(Path(arg).name == "run_suites.py" for arg in step.argv)
    ]
    assert len(suite_steps) == 1
    assert "--all" in suite_steps[0].argv
    assert "--extras" in suite_steps[0].argv
    assert not any(
        "32-jax-cpu.txt" in arg
        for step in steps
        for arg in step.argv
    )


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
def test_verify_fails_against_a_failing_stub_uv(
    root, versions, stub_uv, monkeypatch
):
    monkeypatch.setattr(versions, "late_pins", lambda *args, **kwargs: [])
    monkeypatch.setenv("ACCEPTANCE_UV_FAILURE", "run")
    assert versions.main(["verify"], root=root) != 0
    assert any("run" in call for call in stub_uv.calls())


# spec: "Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`"
# task: 8
def test_verify_succeeds_against_a_successful_stub_uv(
    root, versions, stub_uv, monkeypatch
):
    monkeypatch.setattr(versions, "late_pins", lambda *args, **kwargs: [])
    assert versions.main(["verify"], root=root) == 0
    assert len([call for call in stub_uv.calls() if "run" in call]) == 4


# spec: "Does the same joint resolve as `bump`, with no freeze date and no pins, in two passes: first on the dev Python, then on the newest stable Python."
# task: 8
def test_drift_resolves_twice_without_pins_or_cutoff(
    root, versions, monkeypatch
):
    v = versions.load(root)
    calls = []
    executions = []
    latest = {**v.packages, **v.cited, "jax": "0.12.0.1"}
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")

    def resolver(requirements, python_version, cutoff):
        calls.append((list(requirements), python_version, cutoff))
        return latest

    def runner(argv, root, env):
        executions.append(list(argv))
        return 0

    status, report = versions.drift(
        root,
        fetch=lambda url: metadata(v, url),
        resolver=resolver,
        runner=runner,
    )
    assert status == 0
    assert [call[1] for call in calls] == [v.dev_python, "3.14"]
    for requirements, python_version, cutoff in calls:
        assert cutoff is None
        assert set(v.packages).issubset(requirements)
        assert all("==" not in requirement for requirement in requirements)
    assert len(executions) == 8
    assert v.dev_python in report
    assert "3.14" in report


# spec: "For each pass it reports, for each `[packages]` and `[cited]` entry, the pinned version, the resolved version, the newest release and its upload date."
# task: 8
def test_drift_reports_packages_citations_versions_and_upload_dates(
    root, versions, monkeypatch
):
    v = versions.load(root)
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")
    latest = {
        **v.packages,
        **v.cited,
        "jax": "0.12.0.1",
        "altair": "6.3.0",
        "plotly": "7.1.0",
    }

    def resolver(requirements, python_version, cutoff):
        return latest

    status, report = versions.drift(
        root,
        fetch=lambda url: metadata(v, url),
        resolver=resolver,
        runner=lambda argv, root, env: 0,
    )
    assert status == 0
    for name, pinned in {**v.packages, **v.cited}.items():
        assert name in report
        assert pinned in report
        assert latest[name] in report
    assert "2026-10-21" in report
    assert "2026-09-18" in report


@pytest.mark.parametrize(
    ("failure", "expected"),
    [("", 0), ("run", 1), ("resolve", 2), ("network", 2)],
)
# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_exit_codes_against_stub_uv(
    root, versions, stub_uv, monkeypatch, capsys, failure, expected
):
    v = versions.load(root)
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")
    monkeypatch.setenv("ACCEPTANCE_UV_FAILURE", failure)

    def fetch(url):
        if failure == "network":
            raise urllib.error.URLError("network")
        return metadata(v, url)

    monkeypatch.setattr(versions, "fetch_json", fetch)
    monkeypatch.setattr(versions, "late_pins", lambda *args, **kwargs: [])
    assert versions.main(["drift"], root=root) == expected
    report = output(capsys).lower()
    if failure:
        assert re.search(r"fail|error|conflict|network|resolv", report)


# spec: "`bump` exits 2 on a network or resolve failure and names the step."
# task: 3
def test_bump_resolve_failure_exit_code_and_step(
    root, versions, stub_uv, monkeypatch, capsys
):
    monkeypatch.setenv("ACCEPTANCE_UV_FAILURE", "resolve")
    assert versions.main(
        ["bump", "--date", "2026-10-21"], root=root
    ) == 2
    message = output(capsys).lower()
    assert "resolv" in message


# spec: "A joint resolve that fails in `bump` or `drift` names the packages in conflict."
# task: 3
def test_bump_preserves_conflicting_package_names_from_uv(
    root, versions, stub_uv, monkeypatch, capsys
):
    monkeypatch.setenv("ACCEPTANCE_UV_FAILURE", "resolve")
    assert versions.main(
        ["bump", "--date", "2026-10-21"], root=root
    ) == 2
    message = output(capsys)
    assert "jax" in message
    assert "numpyro" in message


# spec: "A `with` or `extras` package that `[packages]` names gets its pin."
# task: 7
def test_suite_dependency_pins_come_from_the_manifest(root, versions, suites):
    v = versions.load(root)
    pins = suites.Pins.from_versions(v)
    assert pins.spec("polars") == "polars==2.0.0"
    assert pins.spec("arviz>=1.0") == "arviz==1.3.0"
    assert pins.spec("pytest") == "pytest"
    assert pins.spec("scipy") == "scipy"


# spec: "`DEFAULT_PYTHONS` comes from the dev Python."
# task: 7
def test_suite_python_changes_with_the_manifest(root, versions, suites):
    text = MANIFEST.replace("dev = '3.13'", "dev = '3.12'")
    write(root, "build/versions.toml", text)
    v = versions.load(root)
    pins = suites.Pins.from_versions(v)
    assert pins.python == "3.12"


# spec: "Each run passes `--exclude-newer <date>` explicitly, because suites under `skills/` sit below the shadow file."
# task: 7
def test_suite_runs_pass_an_explicit_cutoff(
    project, versions, stub_uv
):
    result = subprocess.run(
        [
            sys.executable,
            str(project / "build/run_suites.py"),
            "--all",
            "--extras",
        ],
        cwd=project,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    v = versions.load(project)
    calls = [call for call in stub_uv.calls() if "run" in call]
    assert calls
    for argv in calls:
        assert option(argv, "--exclude-newer") in {
            v.freeze.isoformat(),
            v.cutoff,
        }


# spec: "The `hooks` suite keeps its explicit `/usr/bin/python3` run."
# task: 7
def test_hooks_suite_keeps_the_system_python_run(project, stub_uv):
    result = subprocess.run(
        [
            sys.executable,
            str(project / "build/run_suites.py"),
            "--all",
            "--extras",
        ],
        cwd=project,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert any(
        "/usr/bin/python3" in argv
        for argv in stub_uv.calls()
    )


# spec: "R4.1. `versions.py check` runs offline."
# task: 9
def test_check_does_not_fetch_or_invoke_uv(
    root, versions, checker, stub_uv, monkeypatch
):
    def forbidden(*args, **kwargs):
        raise AssertionError("offline check attempted network or resolution")

    monkeypatch.setattr(versions, "fetch_json", forbidden)
    monkeypatch.setattr(versions, "resolve", forbidden)
    assert findings(checker, root) == []
    assert versions.main(["check"], root=root) == 0
    assert stub_uv.calls() == []


# spec: "**Sync.** An R2.1 output differs from the file."
# task: 9
def test_check_has_a_seeded_sync_failure(root, checker):
    write(root, ".python-version", "3.12\n")
    result = findings(checker, root)
    assert result
    assert any(".python-version" in line for line in result)


@pytest.mark.parametrize(
    "relative",
    [
        "CLAUDE.md",
        "AGENTS.md",
        "GEMINI.md",
        "build/run_commit_lints.sh",
        "hooks/README.md",
        "skills/bayesian-workflow/SKILL.md",
        ".claude/skills/cc-guide/SKILL.md",
    ],
)
# spec: "**Interpreter literals.** A live file spells `--python 3.<n>`."
# task: 9
def test_each_live_location_has_a_seeded_interpreter_failure(
    root, checker, relative
):
    path = root / relative
    previous = path.read_text(encoding="utf-8") if path.exists() else ""
    write(root, relative, previous + "\nuv run --python 3.13 python\n")
    result = findings(checker, root)
    assert result
    assert any(relative in line for line in result)


# spec: "An interpreter path such as `/usr/bin/python3` is not a literal."
# task: 9
def test_system_interpreter_path_is_allowed(root, checker):
    write(
        root,
        "hooks/README.md",
        "uv run --python /usr/bin/python3 python\n",
    )
    assert findings(checker, root) == []


@pytest.mark.parametrize(
    ("current", "stale"),
    [
        ("Verified on Polars 2.0", "Verified on Polars 1.42"),
        ("numpyro==0.22.0", "numpyro==0.21.0"),
        (
            'NumPyro "checked in the 0.22.0" source',
            'NumPyro "checked in the 0.21.0" source',
        ),
        ("Verified on Altair 6.2", "Verified on Altair 6.3"),
    ],
)
# spec: "**Equality** ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision."
# task: 9
def test_equality_citations_have_matching_and_seeded_stale_controls(
    root, checker, current, stale
):
    relative = "skills/bayesian-workflow/references/diagnostics.md"
    write(root, relative, current + "\n")
    assert findings(checker, root) == []
    write(root, relative, stale + "\n")
    result = findings(checker, root)
    assert result
    assert any(relative in line for line in result)


# spec: "**Equality** ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision."
# task: 9
def test_equality_uses_citation_precision_without_equating_distinct_patches(
    root, checker
):
    relative = "skills/bayesian-workflow/references/diagnostics.md"
    write(root, relative, "Verified on arviz-stats 1.3\n")
    assert findings(checker, root) == []
    write(root, relative, "Verified on arviz-stats 1.3.1\n")
    assert findings(checker, root)


@pytest.mark.parametrize(
    ("current", "stale"),
    [
        ("Polars >=2.0", "Polars <2.0"),
        ("NumPyro ≥0.22", "NumPyro ≥0.23"),
        (
            "great-docs>=0.17.0,<0.18",
            "great-docs>=0.18",
        ),
        ("Python 3.11+", "Python 3.14+"),
    ],
)
# spec: "**Range** (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file's value."
# task: 9
def test_ranges_have_passing_and_seeded_failing_controls(
    root, checker, current, stale
):
    relative = "skills/bayesian-workflow/references/diagnostics.md"
    write(root, relative, current + "\n")
    assert findings(checker, root) == []
    write(root, relative, stale + "\n")
    assert findings(checker, root)


# spec: "In `skills/**/*.md` and the script headers under `skills/*/scripts/`, `check` finds each version that stands next to a `[packages]` name, a `[cited]` name or "Python", and classifies it by form:"
# task: 9
def test_script_header_dependency_ranges_are_checked(root, checker):
    relative = "skills/bayesian-workflow/scripts/diagnose_model.py"
    write(root, relative, SCRIPT)
    assert findings(checker, root) == []
    write(
        root,
        relative,
        SCRIPT.replace("arviz>=1.0", "arviz>=2.0"),
    )
    result = findings(checker, root)
    assert result
    assert any(relative in line for line in result)


# spec: "**History** ("ArviZ 0.23", "and earlier") passes only through the `HISTORICAL` allowlist."
# task: 9
def test_history_requires_an_allowlist_entry(root, checker):
    write(
        root,
        "skills/bayesian-workflow/references/model-comparison.md",
        "ArviZ 0.23 and earlier\n",
    )
    assert findings(checker, root, historical={})
    assert findings(
        checker,
        root,
        historical={"ArviZ 0.23 and earlier": "History, by design"},
    ) == []


# spec: "R4.2. `HISTORICAL` is keyed by the literal phrase, not by file and line, and each entry gives its reason."
# task: 9
def test_historical_allowance_survives_a_file_and_line_move(root, checker):
    phrase = "ArviZ 0.23 and earlier"
    allowed = {phrase: "History, by design"}
    first = write(
        root,
        "skills/bayesian-workflow/references/model-comparison.md",
        phrase + "\n",
    )
    assert findings(checker, root, historical=allowed) == []
    first.unlink()
    write(
        root,
        "skills/bayesian-workflow/references/diagnostics.md",
        "\n\n" + phrase + "\n",
    )
    assert findings(checker, root, historical=allowed) == []


# spec: "**Floors.** Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
def test_floor_mismatch_has_a_seeded_failing_control(root, checker):
    assert findings(checker, root) == []
    relative = "skills/bayesian-workflow/scripts/diagnose_model.py"
    write(root, relative, SCRIPT.replace(">=3.12", ">=3.11"))
    result = findings(checker, root)
    assert result
    assert any("bayesian-workflow" in line for line in result)


# spec: "The dev Python must satisfy each floor."
# task: 9
def test_dev_python_below_a_script_floor_is_rejected(root, versions, checker):
    write(
        root,
        "build/versions.toml",
        MANIFEST.replace("dev = '3.13'", "dev = '3.11'"),
    )
    versions.sync(root)
    result = findings(checker, root)
    assert result
    assert any("3.11" in line or "3.12" in line for line in result)


@pytest.mark.parametrize(
    "relative",
    [
        "specs/deferred_items.md",
        "specs/plans/completed/package-versions.md",
        "specs/completed/package-versions.md",
        "specs/verification/66-uv-probe.md",
        "LICENSE",
        "LICENSE.md",
        "skills/bayesian-workflow/data/diagnostics.md",
        "build/fixtures/diagnostics.md",
    ],
)
# spec: "R4.3. `check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures."
# task: 9
def test_excluded_locations_do_not_produce_findings(root, checker, relative):
    write(
        root,
        relative,
        "uv run --python 3.13 python\nVerified on Polars 1.42\n",
    )
    assert findings(checker, root) == []


# spec: "R4.4. Known limit: `check` sees only the package names that the file lists."
# task: 9
def test_unlisted_package_versions_are_outside_the_citation_lint(root, checker):
    write(
        root,
        "skills/bayesian-workflow/references/diagnostics.md",
        "Verified on pytest 1.3.0\n",
    )
    assert findings(checker, root) == []


# spec: "R2.4. Documented commands spell no interpreter or package version."
# task: 13
def test_live_uv_command_lines_have_no_literal_version_flags(
    project, checker
):
    interpreter = re.compile(r"--python(?:=|\s+)['\"]?3\.\d+")
    package_version = re.compile(
        r"(?:==|>=|<=|~=|≥|≤)\s*\d+(?:\.\d+)+"
    )
    for item in checker.live_files(project):
        path = Path(item)
        if not path.is_absolute():
            path = project / path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        in_command = False
        for line in text.splitlines():
            command_line = "uv run " in line or in_command
            if command_line:
                assert not interpreter.search(line), (path, line)
                assert not package_version.search(line), (path, line)
            in_command = command_line and line.rstrip().endswith("\\")


# spec: "R5.1. `versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`."
# task: 14
def test_versions_check_is_wired_into_the_commit_lint_runner(project):
    text = (project / "build/run_commit_lints.sh").read_text(
        encoding="utf-8"
    )
    assert "versions_check" in text
    assert re.search(
        r"uv\s+run\s+python\s+build/versions\.py\s+check\b",
        text,
    )


# spec: "`setup-uv` takes the interpreter from `.python-version`."
# task: 14
def test_lints_setup_uv_references_the_generated_python_file(project):
    text = (project / ".github/workflows/lints.yml").read_text(
        encoding="utf-8"
    )
    blocks = re.split(r"(?m)^\s*-\s+(?:name|uses):", text)
    assert any(
        "setup-uv" in block and ".python-version" in block
        for block in blocks
    )


# spec: "A new workflow, `.github/workflows/versions-drift.yml`, runs `versions.py drift` weekly on a cron schedule and on manual dispatch."
# task: 15
def test_drift_workflow_has_weekly_and_manual_triggers(project):
    text = (project / ".github/workflows/versions-drift.yml").read_text(
        encoding="utf-8"
    )
    assert re.search(r"\bworkflow_dispatch\s*:", text)
    assert re.search(r"\bschedule\s*:", text)
    match = re.search(
        r"\bcron\s*:\s*(?:'([^']+)'|\"([^\"]+)\"|([^#\n]+))",
        text,
    )
    assert match
    fields = next(value for value in match.groups() if value is not None).split()
    assert len(fields) == 5
    assert fields[0].isdigit() and 0 <= int(fields[0]) < 60
    assert fields[1].isdigit() and 0 <= int(fields[1]) < 24
    assert fields[2:4] == ["*", "*"]
    assert re.fullmatch(
        r"[0-7]|SUN|MON|TUE|WED|THU|FRI|SAT",
        fields[4],
        re.IGNORECASE,
    )
    assert re.search(r"versions\.py\s+drift\b", text)


# spec: "It has `permissions: contents: read`, and it pins its actions by SHA, as `lints.yml` does."
# task: 15
def test_drift_workflow_permissions_and_action_pins(project):
    text = (project / ".github/workflows/versions-drift.yml").read_text(
        encoding="utf-8"
    )
    assert re.search(
        r"permissions\s*:\s*(?:\{\s*contents\s*:\s*read\s*\}|\n\s+contents\s*:\s*read\b)",
        text,
    )
    assert not re.search(r"\b(?:write-all|write)\b\s*(?:#.*)?$", text, re.MULTILINE)
    actions = re.findall(r"\buses\s*:\s*([^\s#]+)", text)
    assert actions
    for action in actions:
        assert re.fullmatch(r"[^@\s]+@[0-9a-fA-F]{40}", action), action


# spec: "It writes the drift report to the job summary."
# task: 15
def test_drift_workflow_writes_the_job_summary(project):
    text = (project / ".github/workflows/versions-drift.yml").read_text(
        encoding="utf-8"
    )
    assert "GITHUB_STEP_SUMMARY" in text
    assert re.search(r"versions\.py\s+drift\b", text)


# spec: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`."
# task: 12
def test_old_cpu_lock_paths_are_retired(project):
    assert not (project / "specs/verification/32-jax-cpu.in").exists()
    assert not (project / "specs/verification/32-jax-cpu.txt").exists()


# spec: "Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python."
# task: 12
def test_python_target_guidance_names_the_manifest(project):
    text = (project / "rules/clean-code-python.md").read_text(
        encoding="utf-8"
    )
    assert "build/versions.toml" in text


# spec: "The dev Python must satisfy each floor."
# task: 13
def test_completed_tree_has_no_versions_findings(project, checker):
    assert checker.check(root=project) == []
</tests>
<flags>
<flag task="5"><spec>uv compares the date with the upload time of each file, not of the release.</spec><plan>`late_pins(v, specs, fetch=None) -> list[str]` (the specs whose release was first uploaded at or after the cutoff)</plan></flag>
</flags>
<untestable>
The repo fixes package versions by hand in many places, and nothing ties the copies together.
On 2026-10-21 the owner found NumPyro at 0.21.0 in one deferred item and at 0.22.0 in `PINNED`.
This work is not part of plan 64 (bayesian-workflow and recommend-probabilistic-model routing).
"Version" has four roles here.
They change for different reasons, so the design keeps them apart.
Conflict: the two gates pin different JAX releases.
The CPU lock has 0.11.2 and `PINNED` has 0.12.0.
The interpreter is not one value.
Three separate roles exist:
A floor states when an API appeared.
A new upstream release does not make it stale.
Conflict: the Polars citations disagree.
explore-data says 1.38, recommend-visualization says 1.42, and three script headers require `polars>=2.0`.
`specs/deferred_items.md`, `specs/plans/completed/`, `specs/completed/` and `specs/verification/*.md` are dated records.
They keep the versions of their day.
One open deferred item is stale in a way that misleads: the Gaussian-process item at `specs/deferred_items.md:4492` says "on the pinned 0.21.0".
`skills/evaluate-deep-learning/references/experiments.md:86-87` is an illustrative run manifest, and the `build/test_check_frontmatter.py` header strings are test data.
A floating gate would have changed today: jax 0.12.0.1 was uploaded on 2026-10-21.
`uv run --exclude-newer <date> --with jax` respects the cutoff.
With 2026-10-20 it gave jax 0.12.0, not 0.12.0.1.
For a PEP 723 script (`uv run script.py`), the command-line `--exclude-newer` and `UV_EXCLUDE_NEWER` did not limit the header's dependencies.
With a 2026-10-01 cutoff it still installed polars 2.0.0 (uploaded 2026-10-06).
A `[tool.uv] exclude-newer = "..."` table inside the script header did limit them (polars 1.44.2).
With no `--python`, uv picked Python 3.14 for a script, and a bare `polars` header resolved to 1.44.2, not 2.0.0.
Under `--python 3.13` it resolved to 2.0.0.
But `uv run --python 3.14 --with 'polars>=2.0'` also resolved to 2.0.0, so the three `polars>=2.0` scripts work on 3.14.
The cause of the 1.44.2 result is unknown.
A `uv.toml` with `exclude-newer` at the repo root reached `--with` deps and script headers in every subdirectory.
`constraint-dependencies` and `override-dependencies` in `uv.toml` did not affect `uv run --with`, and neither did `UV_CONSTRAINT`.
A command-line `--exclude-newer` or `UV_EXCLUDE_NEWER` overrode the `uv.toml` date.
A `--with 'polars==X'` on a script run overrode the script header's range.
A script run by its real path inside the repo picked up the repo's `uv.toml`, even from another working directory.
The same script run through a symlink, which is how `~/.claude/skills` reaches this repo, did not.
A `.python-version` file was found from subdirectories, also with `--no-project`.
uv compares the date with the upload time of each file, not of the release.
It reads a bare date (`2026-10-19`) in the machine's local time zone, and an RFC 3339 timestamp (`2026-10-20T00:00:00Z`) as written.
The plan must re-check items 2 to 6 before it relies on them.
Nested worktrees: this repo's worktrees live inside the main checkout, at `.claude/worktrees/<name>/`.
uv searches parent directories for `uv.toml` and `.python-version`.
So after the change merges, a worktree on a branch that lacks those files inherits the main checkout's freeze date and interpreter, with no sign of it.
`CLAUDE.md` has 153 lines against a 200-line budget.
The values above are the 2026-10-21 state.
The plan sets the real values with `bump` (R3).
A package gets a `[cited]` entry when skill prose cites a version for it and no check runs it.
The plan confirms that Claude Code, Codex and Gemini also ignore a plain file in a skills directory.
`build/cc_guide/notice.sh:114` and `build/githooks/pre-commit:15`: they can run outside the repo's working directory, so they take the interpreter from the file and not from a literal.
A person changes a `[cited]` entry only after re-checking the cited behavior.
A bump follows these steps, in one change:
Run `bump`.
Run `verify`.
Run `check`, which lists each prose citation that the bump made stale.
Re-verify or rewrite each stale citation (R5.5).
Commit.
It flags each package that resolves below its newest release.
It then runs the re-verify set on each pass's versions and reports each gate's result for each pass.
The `drift` report states this limit.
`CLAUDE.md`'s count of commit lints, `build/githooks/pre-commit` and `build/test_commit_lints.py` change with it.
`.github/workflows/lints.yml` keeps its steps.
The job may go red, but it is not a required check.
It never opens an issue or a PR, and it never commits.
Known limit: GitHub disables scheduled workflows in a public repository after 60 days with no activity.
The spec accepts this.
It does not work around it.
The first plan does these, in order:
Re-probe the uv behaviors in the Inventory (items 2 to 6, the shadow file under `skills/`, and nested-worktree inheritance) on the uv version of the day.
Record the results in `specs/verification/`.
If a behavior changed, stop and bring the change to the owner before going on.
Write `build/versions.toml`, then run `bump` and `verify` on the day of execution.
Use one JAX version for both gates.
The JAX CPU examples must pass on it.
If they fail, add a temporary `[[override]]` for `jax-cpu` with its reason, and log a deferred item to remove it.
Pin Polars at the latest release (2.0.0 on 2026-10-21).
This keeps the `polars>=2.0` floors that the portability plan set on purpose (`specs/plans/completed/53-agent-skills-portability.md`, decision DF4).
For each stale citation, either re-verify the cited behavior on the file's version and update the citation, or move it to `HISTORICAL` with the reason "verified on X, not re-checked on Y" and log a deferred item to re-check it.
Never change a citation's version without a re-check.
The known stale citations are the Polars, Altair and plotly lines, `skills/bayesian-workflow/references/model-comparison.md:130`, `references/model-criticism.md:196` and `skills/deep-learning/references/frameworks.md:94-95`.
Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says "on the pinned 0.21.0".
The plan-32 verification records keep their old versions as history.
The plan writes each test before its code (red, then green).
**`versions.py` units.** Cover schema validation, `stack()` with and without an override, and the exact text that `sync` writes.
**`check` findings.** Cover each form (equality, range, history), the interpreter-literal rule and the floors rule.
Each finding has a positive control: a seeded stale literal that must fail.
**`run_suites.py` tests.** `build/test_run_suites.py` and `build/test_check_frontmatter.py:434` build their expected commands from the file, not from a `3.13` literal.
**Exit codes.** Test the `drift`, `verify` and `bump` exit codes against a stub uv, as `hooks/test_project_hooks.py` does.
No third-party text enters the repo, so `NOTICE` and the license files do not change.
The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.
**Plan 63.** It edits `build/run_commit_lints.sh`.
This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
**Plan 64 and the model-lifecycle spec.** They edit bayesian-workflow prose that holds Role 3 and Role 4 citations.
The R6 prose fixes rebase onto them and re-take the line numbers.
**`CLAUDE.md` line budget.** R2.4 removes the version flags from the commands, so `CLAUDE.md` gets shorter.
</untestable>