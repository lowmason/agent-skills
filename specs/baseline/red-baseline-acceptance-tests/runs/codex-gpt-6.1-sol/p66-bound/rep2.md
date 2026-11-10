<tests>
import datetime as dt
import importlib
import json
import os
from pathlib import Path
import re
import shlex
import socket
import subprocess
import sys
import tomllib
from urllib.parse import urlsplit

import pytest

from build import versions


REPO = Path(versions.__file__).resolve().parents[1]
OUTPUT_PATHS = {".python-version", "uv.toml", "skills/uv.toml"}
SNIPPETS = [
    "arviz", "arviz-base", "arviz-stats", "arviz-plots",
    "numpyro", "jax", "numpy", "matplotlib",
]
JAX_CPU = [
    "jax", "jaxlib", "flax", "optax", "orbax-checkpoint",
    "equinox", "diffrax", "e3nn-jax", "numpy",
]
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
OVERRIDE = """
[[override]]
gate = 'jax-cpu'
package = 'jax'
version = '0.11.2'
reason = 'The JAX CPU examples must pass on it.'
"""

STUB_UV = r"""
import json
import os
from pathlib import Path
import sys

argv = sys.argv[1:]
with open(os.environ["ACCEPTANCE_UV_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps(argv) + "\n")

if "compile" in argv:
    status = int(os.environ.get("ACCEPTANCE_RESOLVE_STATUS", "0"))
    if status:
        print(
            "joint resolve conflict: jax==0.12.0 and numpyro==0.22.0",
            file=sys.stderr,
        )
        raise SystemExit(status)

    pins = json.loads(os.environ["ACCEPTANCE_RESOLVED"])
    text = "".join(f"{name}=={version}\n" for name, version in pins.items())
    for index, arg in enumerate(argv):
        if arg in ("-o", "--output-file"):
            Path(argv[index + 1]).write_text(text, encoding="utf-8")
        elif arg.startswith("--output-file="):
            Path(arg.split("=", 1)[1]).write_text(text, encoding="utf-8")
    print(text, end="")
    raise SystemExit(0)

raise SystemExit(int(os.environ.get("ACCEPTANCE_RUN_STATUS", "0")))
"""


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def option_values(argv, option):
    result = []
    for index, argument in enumerate(argv):
        if argument == option:
            result.append(argv[index + 1])
        elif argument.startswith(option + "="):
            result.append(argument.split("=", 1)[1])
    return result


def with_requirements(argv):
    return [
        dependency
        for value in option_values(argv, "--with")
        for dependency in value.split(",")
    ]


def snapshot(root):
    return {
        name: (root / name).read_bytes()
        for name in OUTPUT_PATHS | {"build/versions.toml"}
    }


def uv_calls(log):
    if not log.exists():
        return []
    return [
        json.loads(line)
        for line in log.read_text(encoding="utf-8").splitlines()
    ]


def all_output(capsys):
    captured = capsys.readouterr()
    return captured.out + captured.err


def make_skill(root, body="", floor="3.12", header_floor=None, dependency=None):
    write(
        root,
        "skills/bayesian-workflow/SKILL.md",
        "---\n"
        "name: bayesian-workflow\n"
        "description: Bayesian workflow.\n"
        f"compatibility: Python {floor}+\n"
        "---\n\n"
        + body,
    )
    if header_floor is not None:
        dependencies = [] if dependency is None else [dependency]
        write(
            root,
            "skills/bayesian-workflow/scripts/calibration_check.py",
            "# /// script\n"
            f'# requires-python = ">={header_floor}"\n'
            f"# dependencies = {json.dumps(dependencies)}\n"
            "# ///\n",
        )


@pytest.fixture
def root(tmp_path):
    write(tmp_path, "build/versions.toml", MANIFEST)
    versions.sync(tmp_path)
    return tmp_path


@pytest.fixture
def lint(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO / "build"))
    monkeypatch.setitem(sys.modules, "versions", versions)
    return importlib.import_module("build.versions_check")


@pytest.fixture
def findings(root, lint):
    subprocess.run(
        ["git", "init", "--quiet", str(root)],
        check=True,
        capture_output=True,
    )

    def collect(historical=None):
        subprocess.run(
            ["git", "-C", str(root), "add", "--all"],
            check=True,
            capture_output=True,
        )
        return lint.check(
            root=root,
            historical={} if historical is None else historical,
        )

    return collect


@pytest.fixture
def stub_uv(root, monkeypatch):
    v = versions.load(root)
    resolved = {**v.packages, **v.cited}
    resolved.update({
        "jax": "0.12.0.1",
        "altair": "6.3.0",
        "plotly": "7.1.0",
    })
    executable = write(
        root,
        "bin/uv",
        f"#!{sys.executable}\n" + STUB_UV,
    )
    executable.chmod(0o755)
    log = root / "uv-calls.jsonl"
    monkeypatch.setenv("PATH", str(executable.parent) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("ACCEPTANCE_UV_LOG", str(log))
    monkeypatch.setenv("ACCEPTANCE_RESOLVED", json.dumps(resolved))
    monkeypatch.setenv("ACCEPTANCE_RESOLVE_STATUS", "0")
    monkeypatch.setenv("ACCEPTANCE_RUN_STATUS", "0")
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")

    def fetch(url):
        parts = urlsplit(url).path.strip("/").split("/")
        name = versions.normalize(parts[parts.index("pypi") + 1])
        old = {**v.packages, **v.cited}[name]
        newest = resolved[name]
        releases = {
            old: [{
                "upload_time_iso_8601": "2026-10-19T00:00:00Z",
                "yanked": False,
            }],
        }
        releases[newest] = [{
            "upload_time_iso_8601": (
                "2026-10-21T00:00:00Z"
                if newest != old else "2026-10-19T00:00:00Z"
            ),
            "yanked": False,
        }]
        return {
            "info": {"name": name, "version": newest},
            "releases": releases,
            "urls": releases[old],
        }

    monkeypatch.setattr(versions, "fetch_json", fetch)
    return log


# spec: "Its tables:"
# task: 2
def test_parse_preserves_the_four_version_roles():
    v = versions.parse(MANIFEST)
    assert v.dev_python == "3.13"
    assert v.freeze == dt.date(2026, 10, 19)
    assert v.packages["numpyro"] == "0.22.0"
    assert v.packages["jax"] == "0.12.0"
    assert v.cited == {
        "altair": "6.2",
        "plotly": "6.8",
        "optuna": "5.0.0",
        "great-docs": "0.17.0",
    }
    assert v.gates["snippets"] == SNIPPETS
    assert v.gates["jax-cpu"] == JAX_CPU


@pytest.mark.parametrize(
    "text,key",
    [
        (MANIFEST.replace("dev = '3.13'\n", ""), "dev"),
        (MANIFEST.replace("date = 2026-10-19\n", ""), "date"),
        (
            MANIFEST.replace("arviz = '1.3.0'", "arviz = '>=1.0'"),
            "arviz",
        ),
        (
            MANIFEST.replace("date = 2026-10-19", "date = '2026-10-19'"),
            "date",
        ),
    ],
)
# spec: "A missing or invalid file names the key."
# task: 2
def test_invalid_schema_identifies_the_key(text, key):
    with pytest.raises(versions.VersionsError) as error:
        versions.parse(text)
    assert key in str(error.value)


@pytest.mark.parametrize(
    "text",
    [
        MANIFEST.replace("snippets = ['arviz',", "snippets = ['pytest',"),
        MANIFEST + OVERRIDE.replace("package = 'jax'", "package = 'pytest'"),
    ],
)
# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
def test_unknown_package_is_not_silently_accepted(text):
    with pytest.raises(versions.VersionsError) as error:
        versions.parse(text)
    assert "pytest" in str(error.value)


@pytest.mark.parametrize("missing", ["gate", "package", "version", "reason"])
# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_override_requires_each_of_its_four_keys(missing):
    lines = [
        line for line in OVERRIDE.splitlines()
        if not line.startswith(missing + " =")
    ]
    with pytest.raises(versions.VersionsError):
        versions.parse(MANIFEST + "\n".join(lines))


# spec: "`build/versions.py` gives the other build scripts these values: the dev Python, the freeze date, and `stack(gate)`, the list of `pkg==version` strings for a gate after overrides."
# task: 2
def test_stack_uses_the_shared_pins_and_scopes_an_override_to_its_gate():
    ordinary = versions.parse(MANIFEST)
    overridden = versions.parse(MANIFEST + OVERRIDE)
    assert set(ordinary.stack("snippets")) == {
        f"{name}=={ordinary.packages[name]}" for name in SNIPPETS
    }
    assert set(ordinary.stack("jax-cpu")) == {
        f"{name}=={ordinary.packages[name]}" for name in JAX_CPU
    }
    assert overridden.stack("snippets") == ordinary.stack("snippets")
    expected = set(ordinary.stack("jax-cpu"))
    expected.remove("jax==0.12.0")
    expected.add("jax==0.11.2")
    assert set(overridden.stack("jax-cpu")) == expected
    assert overridden.packages["jax"] == "0.12.0"


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_writes_only_the_three_declared_outputs(root):
    v = versions.load(root)
    generated = versions.outputs(v)
    assert set(generated) == OUTPUT_PATHS
    for relative, expected_text in generated.items():
        assert (root / relative).read_text(encoding="utf-8") == expected_text
    assert (root / ".python-version").read_text().strip() == "3.13"
    assert tomllib.loads((root / "uv.toml").read_text()) == {
        "exclude-newer": "2026-10-20T00:00:00Z",
    }
    shadow = (root / "skills/uv.toml").read_text()
    assert tomllib.loads(shadow) == {}
    assert any(
        line.lstrip().startswith("#") and "build/versions.toml" in line
        for line in shadow.splitlines()
    )


@pytest.mark.parametrize("relative", sorted(OUTPUT_PATHS))
# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_check_detects_each_stale_output_without_rewriting_it(root, relative):
    write(root, relative, "# stale\n")
    before = snapshot(root)
    assert versions.main(["sync", "--check"], root=root) != 0
    assert snapshot(root) == before
    versions.sync(root)
    assert versions.main(["sync", "--check"], root=root) == 0


# spec: "Files uploaded on the freeze date itself (UTC) are included."
# task: 2
def test_cutoff_is_the_following_midnight_in_utc():
    v = versions.parse(MANIFEST)
    assert v.cutoff == "2026-10-20T00:00:00Z"
    changed = versions.parse(
        MANIFEST.replace("date = 2026-10-19", "date = 2026-10-21")
    )
    assert changed.cutoff == "2026-10-22T00:00:00Z"


# spec: "`versions.py check` runs offline."
# task: 9
def test_sync_and_check_need_no_network(root, findings, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("An offline operation attempted network access")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(versions, "fetch_json", forbidden)
    monkeypatch.setattr(versions, "resolve", forbidden)
    versions.sync(root)
    assert versions.main(["sync", "--check"], root=root) == 0
    assert findings() == []


# spec: "With `--only`, the other entries stay at their pins in the joint resolve."
# task: 3
def test_only_releases_the_selected_package_in_the_joint_requirements():
    v = versions.parse(MANIFEST)
    requirements = set(versions.requirements(v, only=("jax",)))
    assert "jax" in requirements
    assert "jax==0.12.0" not in requirements
    assert requirements == {
        "jax",
        *(f"{name}=={value}" for name, value in v.packages.items() if name != "jax"),
    }


# spec: "Sets the freeze date (default: today, UTC) and does one joint resolve, as of that date and on the dev Python, of every `[packages]` entry together."
# task: 3
def test_bump_resolves_all_packages_together_and_syncs(root):
    original = versions.load(root)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((list(requirements), python_version, cutoff))
        return {
            **original.packages,
            "jax": "0.12.0.1",
            "scipy": "1.0",
        }

    versions.bump(root, dt.date(2026, 10, 21), resolver=resolver)
    assert len(calls) == 1
    requirements, python_version, cutoff = calls[0]
    assert set(requirements) == set(original.packages)
    assert python_version == "3.13"
    assert cutoff == "2026-10-22T00:00:00Z"
    current = versions.load(root)
    assert current.freeze == dt.date(2026, 10, 21)
    assert current.packages["jax"] == "0.12.0.1"
    assert "scipy" not in current.packages
    assert versions.main(["sync", "--check"], root=root) == 0


# spec: "Sets the freeze date (default: today, UTC) and does one joint resolve, as of that date and on the dev Python, of every `[packages]` entry together."
# task: 3
def test_bump_defaults_to_the_utc_date(root, monkeypatch):
    original = versions.load(root)
    monkeypatch.setattr(
        versions,
        "resolve",
        lambda requirements, python_version, cutoff: dict(original.packages),
    )
    before = dt.datetime.now(dt.timezone.utc).date()
    assert versions.main(["bump"], root=root) == 0
    after = dt.datetime.now(dt.timezone.utc).date()
    assert versions.load(root).freeze in {before, after}


# spec: "`bump` never changes `[cited]`."
# task: 3
def test_bump_leaves_cited_versions_unchanged(root):
    original = versions.load(root)

    def resolver(requirements, python_version, cutoff):
        return {
            **original.packages,
            **original.cited,
            "jax": "0.12.0.1",
            "altair": "6.3.0",
            "plotly": "7.1.0",
        }

    versions.bump(root, dt.date(2026, 10, 21), resolver=resolver)
    assert versions.load(root).cited == original.cited


# spec: "An invalid date names the value."
# task: 3
def test_invalid_date_identifies_its_value():
    invalid = "2026-10-32"
    with pytest.raises(versions.VersionsError) as error:
        versions.parse_date(invalid)
    assert invalid in str(error.value)


# spec: "Runs `<cmd>` under `uv run` with the gate's stack and the freeze date."
# task: 5
def test_run_argv_contains_the_gate_stack_cutoff_and_command():
    v = versions.parse(MANIFEST)
    command = ["python", "build/check_snippets.py", "--run", "skills/bayesian-workflow/"]
    argv = versions.uv_run_argv(v, "snippets", command)
    assert argv[0] == "uv"
    assert "run" in argv
    assert set(with_requirements(argv)) == set(v.stack("snippets"))
    assert option_values(argv, "--exclude-newer") == [v.cutoff]
    assert argv[-len(command):] == command


@pytest.mark.parametrize(
    "uploaded,expected",
    [
        ("2026-10-19T23:59:59Z", []),
        ("2026-10-20T00:00:00Z", ["numpyro==0.22.0"]),
    ],
)
# spec: "Files uploaded on the freeze date itself (UTC) are included."
# task: 5
def test_upload_check_uses_the_utc_boundary(uploaded, expected):
    def fetch(url):
        release = [{"upload_time_iso_8601": uploaded, "yanked": False}]
        return {
            "info": {"name": "numpyro", "version": "0.22.0"},
            "releases": {"0.22.0": release},
            "urls": release,
        }

    assert versions.late_pins(
        versions.parse(MANIFEST),
        ["numpyro==0.22.0"],
        fetch=fetch,
    ) == expected


@pytest.mark.parametrize("status", [0, 1])
# spec: "`--pin` changes one package for one run and never edits the file."
# task: 5
def test_run_pin_is_temporary_even_when_the_command_fails(
    root, stub_uv, monkeypatch, status,
):
    monkeypatch.setenv("ACCEPTANCE_RUN_STATUS", str(status))
    before = snapshot(root)
    result = versions.main(
        [
            "run", "snippets", "--pin", "jax==0.11.2", "--",
            "python", "build/check_snippets.py", "--run",
            "skills/bayesian-workflow/",
        ],
        root=root,
    )
    assert (result == 0) == (status == 0)
    commands = [argv for argv in uv_calls(stub_uv) if "run" in argv]
    assert commands
    dependencies = with_requirements(commands[-1])
    assert "jax==0.11.2" in dependencies
    assert "jax==0.12.0" not in dependencies
    assert snapshot(root) == before


# spec: "A pin uploaded after the freeze date names the package and the date."
# task: 5
def test_late_pin_error_names_package_and_date(root, stub_uv, capsys):
    result = versions.main(
        [
            "run", "snippets", "--pin", "jax==0.12.0.1", "--",
            "python", "build/check_snippets.py", "--run",
        ],
        root=root,
    )
    assert result != 0
    report = all_output(capsys)
    assert "jax" in report
    assert "2026-10-21" in report


# spec: "Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`."
# task: 8
def test_verify_contains_all_four_required_checks():
    v = versions.parse(MANIFEST)
    steps = versions.verify_steps(v)
    assert len(steps) == 4

    api = [step for step in steps if "--api" in step.argv]
    tier3 = [step for step in steps if "--run" in step.argv]
    jax = [
        step for step in steps
        if any(str(arg).endswith("check_jax_examples.py") for arg in step.argv)
    ]
    suites = [
        step for step in steps
        if any(str(arg).endswith("run_suites.py") for arg in step.argv)
    ]
    assert len(api) == len(tier3) == len(jax) == len(suites) == 1
    assert {"--all", "--extras"} <= set(suites[0].argv)
    assert set(v.stack("snippets")) <= set(with_requirements(tier3[0].argv))
    assert set(v.stack("jax-cpu")) <= set(with_requirements(jax[0].argv))
    assert "--with-requirements" not in jax[0].argv


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 8
def test_verify_tier_two_does_not_receive_the_exact_package_pins():
    v = versions.parse(MANIFEST)
    step = next(step for step in versions.verify_steps(v) if "--api" in step.argv)
    dependencies = with_requirements(step.argv)
    assert dependencies
    assert not any("==" in dependency for dependency in dependencies)
    assert option_values(step.argv, "--exclude-newer") == [v.cutoff]


@pytest.mark.parametrize("status", [0, 1])
# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
def test_verify_exit_status_against_stub_uv(root, stub_uv, monkeypatch, status):
    monkeypatch.setenv("ACCEPTANCE_RUN_STATUS", str(status))
    result = versions.main(["verify"], root=root)
    assert (result == 0) == (status == 0)


# spec: "`--pin` changes one package for one run and never edits the file."
# task: 8
def test_verify_pin_does_not_edit_any_source_or_synced_output(root, stub_uv):
    before = snapshot(root)
    assert versions.main(["verify", "--pin", "jax==0.11.2"], root=root) == 0
    assert snapshot(root) == before
    tier3 = next(argv for argv in uv_calls(stub_uv) if "--run" in argv)
    assert "jax==0.11.2" in with_requirements(tier3)


# spec: "Does the same joint resolve as `bump`, with no freeze date and no pins, in two passes: first on the dev Python, then on the newest stable Python."
# task: 8
def test_drift_resolves_without_pins_or_cutoff_on_both_interpreters(root):
    v = versions.load(root)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((list(requirements), python_version, cutoff))
        return {**v.packages, **v.cited}

    code, report = versions.drift(
        root,
        resolver=resolver,
        newest_python=lambda: "3.14",
        fetch=lambda url: {
            "info": {"version": "0.12.0"},
            "releases": {
                "0.12.0": [{"upload_time_iso_8601": "2026-10-19T00:00:00Z"}],
            },
        },
        runner=lambda argv, root, env: 0,
    )
    assert len(calls) == 2
    assert [python for _, python, _ in calls] == ["3.13", "3.14"]
    for requirements, python, cutoff in calls:
        assert set(v.packages) <= set(requirements)
        assert not any("==" in requirement for requirement in requirements)
        assert cutoff is None


# spec: "For each pass it reports, for each `[packages]` and `[cited]` entry, the pinned version, the resolved version, the newest release and its upload date."
# task: 8
def test_drift_reports_packages_and_citations_for_both_passes(root, stub_uv):
    before = snapshot(root)
    code, report = versions.drift(root)
    assert code == 0
    assert "3.13" in report
    assert "3.14" in report
    v = versions.load(root)
    for name, pinned in {**v.packages, **v.cited}.items():
        assert report.count(name) >= 2
        assert pinned in report
    assert "0.12.0.1" in report
    assert "6.3.0" in report
    assert "7.1.0" in report
    assert "2026-10-21" in report
    assert snapshot(root) == before


@pytest.mark.parametrize(
    "resolve_status,run_status,expected",
    [(0, 0, 0), (0, 1, 1), (1, 0, 2)],
)
# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_exit_codes_against_stub_uv(
    root, stub_uv, monkeypatch, capsys, resolve_status, run_status, expected,
):
    monkeypatch.setenv("ACCEPTANCE_RESOLVE_STATUS", str(resolve_status))
    monkeypatch.setenv("ACCEPTANCE_RUN_STATUS", str(run_status))
    assert versions.main(["drift"], root=root) == expected
    report = all_output(capsys)
    assert report.strip()
    if resolve_status:
        assert "resolv" in report.lower()
    elif run_status:
        assert re.search(r"fail|error", report, re.IGNORECASE)


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_network_failure_is_distinct_from_a_gate_failure(
    root, stub_uv, monkeypatch, capsys,
):
    def unavailable(url):
        raise OSError("network unavailable")

    monkeypatch.setattr(versions, "fetch_json", unavailable)
    assert versions.main(["drift"], root=root) == 2
    assert "network" in all_output(capsys).lower()


# spec: "`bump` exits 2 on a network or resolve failure and names the step."
# task: 3
def test_bump_resolve_failure_exit_code_against_stub_uv(
    root, stub_uv, monkeypatch, capsys,
):
    monkeypatch.setenv("ACCEPTANCE_RESOLVE_STATUS", "1")
    assert versions.main(["bump", "--date", "2026-10-21"], root=root) == 2
    report = all_output(capsys)
    assert "resolv" in report.lower()


# spec: "A joint resolve that fails in `bump` or `drift` names the packages in conflict."
# task: 8
def test_joint_resolve_failure_preserves_conflicting_package_names(
    root, stub_uv, monkeypatch, capsys,
):
    monkeypatch.setenv("ACCEPTANCE_RESOLVE_STATUS", "1")
    for command in [["bump", "--date", "2026-10-21"], ["drift"]]:
        assert versions.main(command, root=root) == 2
        report = all_output(capsys)
        assert "jax" in report
        assert "numpyro" in report


@pytest.mark.parametrize(
    "good,bad",
    [
        ("Verified on Polars 2.0.", "Verified on Polars 1.42."),
        ("NumPyro 0.22", "NumPyro 0.21"),
        (
            "NumPyro: checked in the 0.22.0 source.",
            "NumPyro: checked in the 0.21.0 source.",
        ),
        ("Verified on matplotlib 3.11.", "Verified on matplotlib 3.0."),
        ("Verified on Altair 6.2.", "Verified on Altair 6.3."),
        ("Verified on Python 3.13.", "Verified on Python 3.14."),
    ],
)
# spec: "**Equality** ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision."
# task: 9
def test_equality_citations_have_clean_and_seeded_stale_controls(
    root, findings, good, bad,
):
    make_skill(root, body=good)
    assert findings() == []
    make_skill(root, body=bad)
    assert findings()


# spec: "**Equality** ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision."
# task: 9
def test_script_header_equality_is_checked(root, findings):
    make_skill(
        root, header_floor="3.12", dependency="numpyro==0.22.0",
    )
    assert findings() == []
    make_skill(
        root, header_floor="3.12", dependency="numpyro==0.21.0",
    )
    assert findings()


@pytest.mark.parametrize(
    "good,bad",
    [
        ("polars>=2.0", "polars<2.0"),
        ("NumPyro ≥ 0.22", "NumPyro < 0.22"),
        ("Python 3.11+", "Python 3.14+"),
        ("great-docs>=0.17.0,<0.18", "great-docs>=0.17.0,<0.17.0"),
    ],
)
# spec: "**Range** (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file's value."
# task: 9
def test_range_citations_have_clean_and_seeded_stale_controls(
    root, findings, good, bad,
):
    make_skill(root, body=good)
    assert findings() == []
    make_skill(root, body=bad)
    assert findings()


# spec: "**Range** (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file's value."
# task: 9
def test_script_header_range_is_checked(root, findings):
    make_skill(root, header_floor="3.12", dependency="polars>=2.0")
    assert findings() == []
    make_skill(root, header_floor="3.12", dependency="polars<2.0")
    assert findings()


# spec: "**History** ("ArviZ 0.23", "and earlier") passes only through the `HISTORICAL` allowlist."
# task: 9
def test_history_requires_an_explicit_allowlist_entry(root, findings):
    make_skill(root, body="ArviZ 0.23")
    assert findings()
    assert findings({"ArviZ 0.23": "as the classic stack"}) == []


# spec: "`HISTORICAL` is keyed by the literal phrase, not by file and line, and each entry gives its reason."
# task: 9
def test_historical_allowance_survives_a_change_of_file_and_line(root, findings):
    phrase = "ArviZ 0.23"
    historical = {phrase: "as the classic stack"}
    make_skill(root, body=phrase)
    assert findings(historical) == []
    make_skill(root, body="")
    write(
        root,
        "skills/bayesian-workflow/references/diagnostics.md",
        "\n\n\n" + phrase,
    )
    assert findings(historical) == []
    assert findings()


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
# spec: "A live file spells `--python 3.<n>`."
# task: 9
def test_interpreter_literal_is_rejected_even_when_it_equals_dev_python(
    root, findings, relative,
):
    write(root, relative, "uv run python build/versions.py check\n")
    assert findings() == []
    write(root, relative, "uv run --python 3.13 python build/versions.py check\n")
    assert findings()


# spec: "An interpreter path such as `/usr/bin/python3` is not a literal."
# task: 9
def test_system_interpreter_path_is_allowed(root, findings):
    write(
        root,
        "build/run_commit_lints.sh",
        "uv run --python /usr/bin/python3 python build/versions.py check\n",
    )
    assert findings() == []


# spec: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
def test_floor_mismatch_has_a_matching_positive_control(root, findings):
    make_skill(root, floor="3.12", header_floor="3.12")
    assert findings() == []
    make_skill(root, floor="3.12", header_floor="3.11")
    assert findings()


# spec: "The dev Python must satisfy each floor."
# task: 9
def test_dev_python_below_a_matching_skill_and_script_floor_fails(root, findings):
    make_skill(root, floor="3.12", header_floor="3.12")
    assert findings() == []
    write(
        root,
        "build/versions.toml",
        MANIFEST.replace("dev = '3.13'", "dev = '3.11'"),
    )
    versions.sync(root)
    assert findings()


@pytest.mark.parametrize(
    "relative",
    [
        "specs/deferred_items.md",
        "specs/verification/66-uv-probe.md",
        "LICENSE",
        "LICENSE.md",
        "skills/bayesian-workflow/data/diagnostics.md",
        "skills/bayesian-workflow/tests/fixtures/diagnostics.md",
    ],
)
# spec: "`check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures."
# task: 9
def test_excluded_material_does_not_create_findings(root, findings, relative):
    write(
        root,
        relative,
        "Verified on NumPyro 0.21.0.\n"
        "uv run --python 3.14 python build/versions.py check\n",
    )
    assert findings() == []


# spec: "Known limit: `check` sees only the package names that the file lists."
# task: 9
def test_unlisted_package_does_not_become_a_citation_finding(root, findings):
    make_skill(root, body="scipy>=1.0")
    assert findings() == []
    make_skill(root, body="numpyro==0.21.0")
    assert findings()


@pytest.mark.parametrize("relative", sorted(OUTPUT_PATHS))
# spec: "An R2.1 output differs from the file."
# task: 9
def test_check_includes_sync_findings(root, findings, relative):
    assert findings() == []
    write(root, relative, "# stale\n")
    assert findings()


# spec: "Polars is in `[packages]` by the second case: the suites install it, and three headers floor it."
# task: 4
def test_repository_manifest_has_required_package_membership():
    v = versions.load(REPO)
    assert set(SNIPPETS + JAX_CPU + ["polars"]) <= set(v.packages)
    assert {"altair", "plotly", "optuna", "great-docs"} <= set(v.cited)
    assert not (set(v.packages) & set(v.cited))
    assert not ({"pytest", "pyyaml", "scipy", "tensorstore"} & set(v.packages))


# spec: "The file does not hold the script floors (`requires-python`, `compatibility:`) or the 3.9 floor of `install.py` and the read-only agent guard."
# task: 4
def test_manifest_python_table_contains_only_the_dev_interpreter():
    document = tomllib.loads((REPO / "build/versions.toml").read_text())
    assert set(document["python"]) == {"dev"}
    assert "requires-python" not in document
    assert "compatibility" not in document


# spec: "A `with` or `extras` package that `[packages]` names gets its pin."
# task: 7
def test_suite_commands_take_package_pins_and_interpreters_from_the_file(
    root, stub_uv,
):
    v = versions.load(REPO)
    completed = subprocess.run(
        [
            sys.executable,
            str(REPO / "build/run_suites.py"),
            "--all",
            "--extras",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    commands = [argv for argv in uv_calls(stub_uv) if "run" in argv]
    assert commands
    matched = set()
    interpreters = set()
    for argv in commands:
        interpreters.update(option_values(argv, "--python"))
        assert option_values(argv, "--exclude-newer") == [v.cutoff]
        for dependency in with_requirements(argv):
            name = versions.normalize(re.split(r"[<>=!~\[]", dependency, 1)[0])
            if name in v.packages:
                assert dependency == f"{name}=={v.packages[name]}"
                matched.add(name)
    assert matched
    assert v.dev_python in interpreters
    assert "/usr/bin/python3" in interpreters


# spec: "Documented commands spell no interpreter or package version."
# task: 13
def test_principal_documented_uv_commands_have_no_version_literals():
    for relative in ["CLAUDE.md", "AGENTS.md", "GEMINI.md", "build/run_commit_lints.sh"]:
        text = (REPO / relative).read_text()
        for line in text.splitlines():
            if "uv run" in line:
                assert not re.search(r"--python(?:=|\s+)3\.\d+", line), relative
                assert not re.search(r"\b[\w.-]+==\d", line), relative


# spec: "`versions.py check` exits 0."
# task: 13
def test_migrated_repository_passes_the_offline_check():
    assert versions.main(["check"], root=REPO) == 0


# spec: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`."
# task: 12
def test_old_cpu_lock_paths_are_retired_and_verify_uses_the_stack():
    assert not (REPO / "specs/verification/32-jax-cpu.in").exists()
    assert not (REPO / "specs/verification/32-jax-cpu.txt").exists()
    v = versions.load(REPO)
    step = next(
        step for step in versions.verify_steps(v)
        if any(str(arg).endswith("check_jax_examples.py") for arg in step.argv)
    )
    assert set(v.stack("jax-cpu")) <= set(with_requirements(step.argv))
    assert not any("32-jax-cpu" in str(arg) for arg in step.argv)


# spec: "Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python."
# task: 12
def test_python_rule_points_to_the_version_source():
    text = (REPO / "rules/clean-code-python.md").read_text()
    assert "build/versions.toml" in text
    assert "agent-skills: 3.13" not in text


# spec: "This keeps the `polars>=2.0` floors that the portability plan set on purpose (`specs/plans/completed/53-agent-skills-portability.md`, decision DF4)."
# task: 10
def test_migration_preserves_the_three_polars_floors():
    for relative in [
        "skills/explore-data/scripts/profile.py",
        "skills/recommend-visualization/scripts/recommend.py",
        "skills/recommend-probabilistic-model/scripts/characterize.py",
    ]:
        text = (REPO / relative).read_text()
        header = text.split("# ///", 2)[1]
        assert "polars>=2.0" in header
    assert versions.compare(versions.load(REPO).packages["polars"], "2.0.0") >= 0


# spec: "`versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`."
# task: 14
def test_commit_lint_registration_names_the_versions_check():
    text = (REPO / "build/run_commit_lints.sh").read_text()
    assert "versions_check" in text
    assert re.search(r"build/versions\.py\s+check\b", text)


# spec: "`setup-uv` takes the interpreter from `.python-version`."
# task: 14
def test_lints_workflow_does_not_supply_a_numeric_python_version():
    text = (REPO / ".github/workflows/lints.yml").read_text()
    assert "setup-uv" in text
    assert not re.search(
        r"""python-version:\s*['"]?3\.\d+""",
        text,
    )
    assert (REPO / ".python-version").read_text().strip() == versions.load(REPO).dev_python


# spec: "A new workflow, `.github/workflows/versions-drift.yml`, runs `versions.py drift` weekly on a cron schedule and on manual dispatch."
# task: 15
def test_drift_workflow_has_weekly_and_manual_triggers():
    text = (REPO / ".github/workflows/versions-drift.yml").read_text()
    assert re.search(r"\bworkflow_dispatch\s*:", text)
    crons = re.findall(r"""cron:\s*['"]([^'"]+)['"]""", text)
    assert crons
    weekly = []
    for cron in crons:
        fields = cron.split()
        if len(fields) == 5:
            minute, hour, day, month, weekday = fields
            weekly.append(
                minute.isdigit()
                and 0 <= int(minute) < 60
                and hour.isdigit()
                and 0 <= int(hour) < 24
                and day == month == "*"
                and re.fullmatch(
                    r"[0-7]|SUN|MON|TUE|WED|THU|FRI|SAT",
                    weekday,
                    re.IGNORECASE,
                ) is not None
            )
    assert any(weekly)
    assert re.search(r"versions\.py\s+drift\b", text)


# spec: "It has `permissions: contents: read`, and it pins its actions by SHA, as `lints.yml` does."
# task: 15
def test_drift_workflow_has_read_permissions_and_sha_pinned_actions():
    text = (REPO / ".github/workflows/versions-drift.yml").read_text()
    assert re.search(
        r"permissions:\s*(?:\{\s*contents:\s*read\s*\}|\n[ \t]+contents:\s*read\b)",
        text,
    )
    uses = re.findall(r"""^\s*-?\s*uses:\s*['"]?([^\s'"]+)""", text, re.MULTILINE)
    assert uses
    assert all(re.fullmatch(r".+@[0-9a-fA-F]{40}", action) for action in uses)


# spec: "It writes the drift report to the job summary."
# task: 15
def test_drift_workflow_targets_the_job_summary():
    text = (REPO / ".github/workflows/versions-drift.yml").read_text()
    assert "GITHUB_STEP_SUMMARY" in text
    assert re.search(r"versions\.py\s+drift\b", text)
</tests>
<flags>
</flags>
<untestable>
The plan must re-check items 2 to 6 before it relies on them.
The plan confirms that Claude Code, Codex and Gemini also ignore a plain file in a skills directory.
A person changes a `[cited]` entry only after re-checking the cited behavior.
A bump follows these steps, in one change:
It flags each package that resolves below its newest release.
The `drift` report states this limit.
`CLAUDE.md`'s count of commit lints, `build/githooks/pre-commit` and `build/test_commit_lints.py` change with it.
`.github/workflows/lints.yml` keeps its steps.
The job may go red, but it is not a required check.
It never opens an issue or a PR, and it never commits.
Known limit: GitHub disables scheduled workflows in a public repository after 60 days with no activity.
It does not work around it.
The first plan does these, in order:
Re-probe the uv behaviors in the Inventory (items 2 to 6, the shadow file under `skills/`, and nested-worktree inheritance) on the uv version of the day.
Record the results in `specs/verification/`.
If a behavior changed, stop and bring the change to the owner before going on.
Write `build/versions.toml`, then run `bump` and `verify` on the day of execution.
The JAX CPU examples must pass on it.
If they fail, add a temporary `[[override]]` for `jax-cpu` with its reason, and log a deferred item to remove it.
Pin Polars at the latest release (2.0.0 on 2026-10-21).
For each stale citation, either re-verify the cited behavior on the file's version and update the citation, or move it to `HISTORICAL` with the reason "verified on X, not re-checked on Y" and log a deferred item to re-check it.
Never change a citation's version without a re-check.
Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says "on the pinned 0.21.0".
The plan-32 verification records keep their old versions as history.
The plan writes each test before its code (red, then green).
`build/test_run_suites.py` and `build/test_check_frontmatter.py:434` build their expected commands from the file, not from a `3.13` literal.
No third-party text enters the repo, so `NOTICE` and the license files do not change.
The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.
This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
The R6 prose fixes rebase onto them and re-take the line numbers.
</untestable>