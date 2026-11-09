<tests>
import ast
import datetime as dt
import importlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import textwrap
import tomllib
import urllib.error
import urllib.parse

import pytest


# Save this module as build/test_versions_acceptance.py.
REPO = Path(__file__).resolve().parents[1]

SOURCE = """\
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

OVERRIDE = """\
[[override]]
gate = 'jax-cpu'
package = 'jax'
version = '0.11.2'
reason = 'The JAX CPU examples must pass on it.'
"""


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def option_values(argv, option):
    values = []
    for index, arg in enumerate(argv):
        if arg == option:
            values.append(argv[index + 1])
        elif arg.startswith(option + "="):
            values.append(arg.split("=", 1)[1])
    return values


def package_name(requirement):
    return re.split(r"[\s<>=!~;\[]", requirement, maxsplit=1)[0].lower().replace("_", "-")


def track(root):
    subprocess.run(
        ["git", "-C", str(root), "add", "--all"],
        check=True,
        capture_output=True,
    )


def findings(checker, root, historical=None):
    track(root)
    return checker.check(root=root, historical=historical)


def metadata(v):
    latest = dict(v.packages)
    latest.update(v.cited)
    latest.update(jax="0.12.0.1", altair="6.3.0", plotly="7.1.0")
    result = {}
    for name, newest in latest.items():
        pinned = {**v.packages, **v.cited}[name]
        releases = {}
        for version in {pinned, newest}:
            uploaded = (
                "2026-10-21T00:00:00Z"
                if name == "jax" and version == "0.12.0.1"
                else "2026-10-19T00:00:00Z"
            )
            releases[version] = [{
                "upload_time_iso_8601": uploaded,
                "upload_time": uploaded.removesuffix("Z"),
                "yanked": False,
                "requires_python": None,
            }]
        result[name] = {
            "info": {"name": name, "version": newest},
            "releases": releases,
        }
    return result


def metadata_fetch(data):
    def fetch(url):
        parts = urllib.parse.urlparse(url).path.strip("/").split("/")
        name = parts[parts.index("pypi") + 1].lower().replace("_", "-")
        return data[name]
    return fetch


def uv_calls(log):
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text().splitlines()]


def skill(root, floor="3.11", requires="3.11", dependency="polars>=2.0"):
    write(
        root,
        "skills/explore-data/SKILL.md",
        f"---\nname: explore-data\n"
        f"description: Profile data.\ncompatibility: Python {floor}+\n---\n",
    )
    write(
        root,
        "skills/explore-data/scripts/profile.py",
        f'# /// script\n# requires-python = ">={requires}"\n'
        f'# dependencies = ["{dependency}"]\n# ///\n',
    )


def expand_remediation(api, v, text):
    argv = shlex.split(text)
    positions = [
        index for index, arg in enumerate(argv)
        if arg.replace("\\", "/").endswith("build/versions.py")
    ]
    if not positions:
        return argv
    index = positions[0]
    assert argv[index + 1] == "run"
    separator = argv.index("--", index + 2)
    return api.uv_run_argv(
        v,
        argv[index + 2],
        argv[separator + 1:],
    )


@pytest.fixture
def api(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO / "build"))
    return importlib.import_module("versions")


@pytest.fixture
def checker(api):
    return importlib.import_module("versions_check")


@pytest.fixture
def root(tmp_path, api):
    directory = tmp_path / "repo"
    directory.mkdir()
    write(directory, "build/versions.toml", SOURCE)
    subprocess.run(
        ["git", "init", "-q", str(directory)],
        check=True,
        capture_output=True,
    )
    api.sync(directory)
    return directory


@pytest.fixture
def fake_uv(tmp_path, monkeypatch):
    directory = tmp_path / "bin"
    directory.mkdir()
    log = tmp_path / "uv.jsonl"
    executable = directory / "uv"
    executable.write_text(
        f"#!{sys.executable}\n" + textwrap.dedent("""\
            import json
            import os
            from pathlib import Path
            import sys

            argv = sys.argv[1:]
            with open(os.environ["ACCEPTANCE_UV_LOG"], "a") as stream:
                stream.write(json.dumps(argv) + "\\n")

            status = int(os.environ.get("ACCEPTANCE_UV_STATUS", "0"))
            if status:
                print(
                    os.environ.get(
                        "ACCEPTANCE_UV_ERROR",
                        "joint resolve conflict: jax and numpyro",
                    ),
                    file=sys.stderr,
                )
                sys.exit(status)

            if "compile" in argv:
                pins = json.loads(os.environ.get("ACCEPTANCE_UV_PINS", "{}"))
                output = "".join(
                    f"{name}=={version}\\n"
                    for name, version in sorted(pins.items())
                )
                for index, arg in enumerate(argv):
                    if arg in ("-o", "--output-file"):
                        Path(argv[index + 1]).write_text(output)
                    elif arg.startswith("--output-file="):
                        Path(arg.split("=", 1)[1]).write_text(output)
                print(output, end="")
            sys.exit(0)
        """),
        encoding="utf-8",
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(directory) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("ACCEPTANCE_UV_LOG", str(log))
    monkeypatch.setenv("ACCEPTANCE_UV_STATUS", "0")
    return log


# spec: "Its tables:"
# task: 2
def test_parse_the_spec_schema(api):
    v = api.parse(SOURCE)
    assert v.dev_python == "3.13"
    assert v.freeze == dt.date(2026, 10, 19)
    assert v.packages["numpyro"] == "0.22.0"
    assert v.cited["great-docs"] == "0.17.0"
    assert v.overrides == [] or v.overrides == ()


# spec: "A missing or invalid file names the key."
# task: 2
@pytest.mark.parametrize(
    ("old", "new", "key"),
    [
        ("dev = '3.13'", "", "dev"),
        ("dev = '3.13'", "dev = 313", "dev"),
        ("date = 2026-10-19", "", "date"),
        ("date = 2026-10-19", "date = 'not-a-date'", "date"),
        ("arviz = '1.3.0'", "arviz = ['1.3.0']", "arviz"),
        ("arviz = '1.3.0'", "arviz = '>=1.0'", "arviz"),
    ],
)
def test_schema_errors_identify_the_key(api, old, new, key):
    with pytest.raises(api.VersionsError) as caught:
        api.parse(SOURCE.replace(old, new))
    assert key in str(caught.value)


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
@pytest.mark.parametrize(
    "source",
    [
        SOURCE.replace("jax = '0.12.0'\n", ""),
        SOURCE + OVERRIDE.replace("package = 'jax'", "package = 'scipy'"),
    ],
)
def test_unknown_packages_are_named(api, source):
    expected = "scipy" if "package = 'scipy'" in source else "jax"
    with pytest.raises(api.VersionsError) as caught:
        api.parse(source)
    assert expected in str(caught.value)


# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
@pytest.mark.parametrize("key", ["gate", "package", "version", "reason"])
def test_override_requires_each_key(api, key):
    lines = [
        line for line in OVERRIDE.splitlines()
        if not line.startswith(key + " =")
    ]
    with pytest.raises(api.VersionsError) as caught:
        api.parse(SOURCE + "\n".join(lines))
    assert key in str(caught.value)


# spec: "One version per package for the whole repo."
# task: 2
def test_both_stacks_use_the_same_package_pin(api):
    v = api.parse(SOURCE)
    for gate, names in v.gates.items():
        assert v.stack(gate) == [
            f"{name}=={v.packages[name]}" for name in names
        ]
    assert "jax==0.12.0" in v.stack("snippets")
    assert "jax==0.12.0" in v.stack("jax-cpu")


# spec: "A check differs only through a named override with a reason"
# task: 2
def test_override_is_scoped_to_its_gate(api):
    v = api.parse(SOURCE + OVERRIDE)
    assert "jax==0.11.2" in v.stack("jax-cpu")
    assert "jax==0.12.0" in v.stack("snippets")
    assert v.packages["jax"] == "0.12.0"


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_outputs_have_the_required_contents(api):
    v = api.parse(SOURCE)
    output = api.outputs(v)
    assert set(output) == {".python-version", "uv.toml", "skills/uv.toml"}
    assert output[".python-version"].strip() == "3.13"
    assert tomllib.loads(output["uv.toml"]) == {
        "exclude-newer": "2026-10-20T00:00:00Z",
    }
    assert tomllib.loads(output["skills/uv.toml"]) == {}
    assert any(
        line.lstrip().startswith("#") and "build/versions.toml" in line
        for line in output["skills/uv.toml"].splitlines()
    )


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
@pytest.mark.parametrize("relative", [".python-version", "uv.toml", "skills/uv.toml"])
def test_sync_check_detects_changes_without_repairing_them(api, root, relative):
    assert api.main(["sync", "--check"], root=root) == 0
    path = root / relative
    path.write_text(path.read_text() + "\n# changed\n")
    changed = path.read_bytes()
    assert api.main(["sync", "--check"], root=root) != 0
    assert path.read_bytes() == changed
    api.sync(root)
    assert path.read_text() == api.outputs(api.load(root))[relative]
    assert api.main(["sync", "--check"], root=root) == 0


# spec: "Other packages (pytest, pyyaml, scipy, tensorstore and the rest) get no entry, and the freeze date fixes them."
# task: 4
def test_real_manifest_has_the_required_pin_scope(api):
    v = api.load(REPO)
    assert {"snippets", "jax-cpu"} <= set(v.gates)
    assert {name for names in v.gates.values() for name in names} <= set(v.packages)
    assert "polars" in v.packages
    assert not {"pytest", "pyyaml", "scipy", "tensorstore"} & set(v.packages)
    assert {"altair", "plotly", "optuna", "great-docs"} <= set(v.cited)
    assert not set(v.cited) & set(v.packages)
    assert all(
        isinstance(version, str) and not re.search(r"[<>=!~]", version)
        for version in v.packages.values()
    )


# spec: "With `--only`, the other entries stay at their pins in the joint resolve"
# task: 3
def test_only_keeps_other_packages_in_the_joint_requirements(api):
    v = api.parse(SOURCE)
    full = api.requirements(v)
    assert {package_name(item) for item in full} == set(v.packages)
    assert all("==" not in item for item in full)

    restricted = api.requirements(v, only=("jax",))
    assert {package_name(item) for item in restricted} == set(v.packages)
    assert "jax" in restricted
    for name, version in v.packages.items():
        if name != "jax":
            assert f"{name}=={version}" in restricted


# spec: "It rewrites `[packages]` from the result and runs `sync`."
# task: 3
def test_bump_uses_one_joint_resolve_and_syncs(api, root):
    before = api.load(root)
    calls = []
    resolved = dict(before.packages, jax="0.12.0.1", scipy="1.0")

    def resolver(requirements, python_version, cutoff):
        calls.append((requirements, python_version, cutoff))
        return resolved

    api.bump(root, dt.date(2026, 10, 21), resolver=resolver)
    after = api.load(root)
    assert len(calls) == 1
    requirements, python_version, cutoff = calls[0]
    assert {package_name(item) for item in requirements} == set(before.packages)
    assert all("==" not in item for item in requirements)
    assert python_version == before.dev_python
    assert cutoff == "2026-10-22T00:00:00Z"
    assert after.freeze == dt.date(2026, 10, 21)
    assert after.packages == {
        name: resolved[name] for name in before.packages
    }
    assert api.main(["sync", "--check"], root=root) == 0


# spec: "`bump` never changes `[cited]`."
# task: 3
def test_bump_preserves_cited_versions(api, root):
    before = api.load(root)
    api.bump(
        root,
        dt.date(2026, 10, 21),
        resolver=lambda requirements, python_version, cutoff: dict(
            before.packages, jax="0.12.0.1"
        ),
    )
    assert api.load(root).cited == before.cited


# spec: "Sets the freeze date (default: today, UTC) and does one joint resolve, as of that date and on the dev Python, of every `[packages]` entry together."
# task: 3
def test_bump_defaults_to_today_in_utc(api, root, monkeypatch):
    v = api.load(root)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((python_version, cutoff))
        return dict(v.packages)

    monkeypatch.setattr(api, "resolve", resolver)
    before = dt.datetime.now(dt.timezone.utc).date()
    assert api.main(["bump"], root=root) == 0
    after = dt.datetime.now(dt.timezone.utc).date()
    bumped = api.load(root)
    assert before <= bumped.freeze <= after
    assert calls == [(v.dev_python, bumped.cutoff)]


# spec: "An invalid date names the value."
# task: 3
def test_invalid_date_names_its_input(api):
    value = "2026-10-32"
    with pytest.raises(api.VersionsError) as caught:
        api.parse_date(value)
    assert value in str(caught.value)


# spec: "Runs `<cmd>` under `uv run` with the gate's stack and the freeze date"
# task: 5
def test_run_argv_contains_the_gate_stack_and_utc_cutoff(api):
    v = api.parse(SOURCE)
    command = ["python", "build/check_snippets.py", "--run", "skills/bayesian-workflow/"]
    argv = api.uv_run_argv(v, "snippets", command)
    assert Path(argv[0]).name == "uv"
    assert "run" in argv
    assert set(option_values(argv, "--with")) == set(v.stack("snippets"))
    assert option_values(argv, "--exclude-newer") == ["2026-10-20T00:00:00Z"]
    assert argv[-len(command):] == command


# spec: "`--pin` changes one package for one run and never edits the file."
# task: 5
def test_temporary_pin_changes_only_the_requested_package(api, root):
    original = (root / "build/versions.toml").read_bytes()
    v = api.load(root)
    pins = api.parse_pins(v, ["numpyro==0.21.0"])
    argv = api.uv_run_argv(v, "snippets", ["python"], pins=pins)
    installed = set(option_values(argv, "--with"))
    assert installed == (
        set(v.stack("snippets")) - {"numpyro==0.22.0"}
    ) | {"numpyro==0.21.0"}
    assert (root / "build/versions.toml").read_bytes() == original


# spec: "Files uploaded on the freeze date itself (UTC) are included."
# task: 5
@pytest.mark.parametrize(
    ("uploaded", "late"),
    [
        ("2026-10-19T00:00:00Z", False),
        ("2026-10-19T23:59:59Z", False),
        ("2026-10-20T00:00:00Z", True),
        ("2026-10-21T00:00:00Z", True),
    ],
)
def test_upload_cutoff_includes_the_whole_freeze_day(api, uploaded, late):
    v = api.parse(SOURCE)
    data = {
        "info": {"name": "jax", "version": "0.12.0"},
        "releases": {
            "0.12.0": [{"upload_time_iso_8601": uploaded, "yanked": False}],
        },
    }
    assert bool(api.late_pins(
        v, ["jax==0.12.0"], fetch=lambda url: data
    )) is late


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 5
@pytest.mark.parametrize("status", [0, 1])
def test_run_propagates_uv_failure(api, root, fake_uv, monkeypatch, status):
    monkeypatch.setattr(api, "fetch_json", metadata_fetch(metadata(api.load(root))))
    monkeypatch.setenv("ACCEPTANCE_UV_STATUS", str(status))
    code = api.main(["run", "snippets", "--", "python"], root=root)
    assert (code == 0) is (status == 0)
    assert uv_calls(fake_uv)


# spec: "Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`"
# task: 8
def test_verify_builds_all_four_required_checks(api):
    v = api.parse(SOURCE)
    steps = api.verify_steps(v)
    assert len(steps) == 4

    tier2 = [step for step in steps if "--api" in step.argv]
    tier3 = [step for step in steps if "--run" in step.argv]
    jax = [
        step for step in steps
        if any(str(arg).endswith("check_jax_examples.py") for arg in step.argv)
    ]
    suites = [
        step for step in steps
        if any(str(arg).endswith("run_suites.py") for arg in step.argv)
    ]
    assert len(tier2) == len(tier3) == len(jax) == len(suites) == 1
    assert not any(
        "==" in dep and package_name(dep) in v.packages
        for dep in option_values(tier2[0].argv, "--with")
    )
    assert set(v.stack("snippets")) <= set(
        option_values(tier3[0].argv, "--with")
    )
    assert set(v.stack("jax-cpu")) <= set(
        option_values(jax[0].argv, "--with")
    )
    assert "--all" in suites[0].argv
    assert "--extras" in suites[0].argv


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
@pytest.mark.parametrize("status", [0, 1])
def test_verify_exit_codes_against_stub_uv(
    api, root, fake_uv, monkeypatch, status
):
    monkeypatch.setattr(api, "fetch_json", metadata_fetch(metadata(api.load(root))))
    monkeypatch.setenv("ACCEPTANCE_UV_STATUS", str(status))
    code = api.main(["verify"], root=root)
    assert (code == 0) is (status == 0)
    if status == 0:
        assert len(uv_calls(fake_uv)) == 4


# spec: "`bump` exits 2 on a network or resolve failure and names the step."
# task: 3
def test_bump_resolve_failure_against_stub_uv(
    api, root, fake_uv, monkeypatch, capsys
):
    monkeypatch.setenv("ACCEPTANCE_UV_STATUS", "1")
    monkeypatch.setenv(
        "ACCEPTANCE_UV_ERROR", "joint resolve conflict: jax and numpyro"
    )
    assert api.main(["bump", "--date", "2026-10-21"], root=root) == 2
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "resolve" in output.lower()
    assert "jax" in output
    assert "numpyro" in output
    assert uv_calls(fake_uv)


# spec: "Does the same joint resolve as `bump`, with no freeze date and no pins, in two passes: first on the dev Python, then on the newest stable Python."
# task: 8
def test_drift_resolves_both_interpreters_without_pins_or_cutoff(api, root):
    v = api.load(root)
    data = metadata(v)
    calls = []
    executed = []

    def resolver(requirements, python_version, cutoff):
        calls.append((list(requirements), python_version, cutoff))
        return {
            name: data[name]["info"]["version"] for name in v.packages
        }

    def runner(*args, **kwargs):
        executed.append((args, kwargs))
        return 0

    code, report = api.drift(
        root,
        fetch=metadata_fetch(data),
        resolver=resolver,
        newest_python=lambda: "3.14",
        runner=runner,
    )
    assert code == 0
    assert [call[1] for call in calls] == [v.dev_python, "3.14"]
    for requirements, python_version, cutoff in calls:
        assert {package_name(item) for item in requirements} == set(v.packages)
        assert all("==" not in item for item in requirements)
        assert cutoff is None
    assert len(executed) == 8
    assert v.dev_python in report
    assert "3.14" in report


# spec: "For each pass it reports, for each `[packages]` and `[cited]` entry, the pinned version, the resolved version, the newest release and its upload date."
# task: 8
def test_drift_report_includes_packages_citations_versions_and_upload_dates(
    api, root
):
    v = api.load(root)
    data = metadata(v)
    resolved = {
        name: data[name]["info"]["version"] for name in v.packages
    }
    code, report = api.drift(
        root,
        fetch=metadata_fetch(data),
        resolver=lambda requirements, python_version, cutoff: resolved,
        newest_python=lambda: "3.14",
        runner=lambda *args, **kwargs: 0,
    )
    assert code == 0
    for name, pinned in {**v.packages, **v.cited}.items():
        assert name in report
        assert pinned in report
        assert data[name]["info"]["version"] in report
    assert "2026-10-21" in report


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
@pytest.mark.parametrize(("uv_status", "expected"), [(0, 0), (1, 1)])
def test_drift_gate_exit_codes_against_stub_uv(
    api, root, fake_uv, monkeypatch, capsys, uv_status, expected
):
    v = api.load(root)
    data = metadata(v)
    monkeypatch.setattr(api, "fetch_json", metadata_fetch(data))
    monkeypatch.setattr(api, "newest_stable_python", lambda: "3.14")
    monkeypatch.setattr(
        api,
        "resolve",
        lambda requirements, python_version, cutoff: {
            name: data[name]["info"]["version"] for name in v.packages
        },
    )
    monkeypatch.setenv("ACCEPTANCE_UV_STATUS", str(uv_status))
    assert api.main(["drift"], root=root) == expected
    captured = capsys.readouterr()
    assert captured.out or captured.err
    assert uv_calls(fake_uv)


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_resolve_failure_against_stub_uv(
    api, root, fake_uv, monkeypatch, capsys
):
    monkeypatch.setattr(api, "fetch_json", metadata_fetch(metadata(api.load(root))))
    monkeypatch.setattr(api, "newest_stable_python", lambda: "3.14")
    monkeypatch.setenv("ACCEPTANCE_UV_STATUS", "1")
    assert api.main(["drift"], root=root) == 2
    captured = capsys.readouterr()
    assert "resolve" in (captured.out + captured.err).lower()
    assert uv_calls(fake_uv)


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_network_failure_is_distinguished(api, root):
    v = api.load(root)

    def unavailable(url):
        raise urllib.error.URLError("network unavailable")

    code, report = api.drift(
        root,
        fetch=unavailable,
        resolver=lambda requirements, python_version, cutoff: dict(v.packages),
        newest_python=lambda: "3.14",
        runner=lambda *args, **kwargs: 0,
    )
    assert code == 2
    assert re.search(r"network|unavailable|reach", report, re.IGNORECASE)


# spec: "A `with` or `extras` package that `[packages]` names gets its pin."
# task: 7
@pytest.mark.parametrize(
    ("dependency", "expected"),
    [
        ("polars", "polars==2.0.0"),
        ("arviz>=1.0", "arviz==1.3.0"),
        ("matplotlib>=3.0", "matplotlib==3.11.2"),
        ("pytest", "pytest"),
        ("scipy>=1.0", "scipy>=1.0"),
    ],
)
def test_suite_dependency_pins_come_from_the_file(api, dependency, expected):
    suites = importlib.import_module("run_suites")
    pins = suites.Pins.from_versions(api.parse(SOURCE))
    assert pins.python == "3.13"
    assert pins.cutoff == "2026-10-20T00:00:00Z"
    assert pins.spec(dependency) == expected


# spec: "Each run passes `--exclude-newer <date>` explicitly, because suites under `skills/` sit below the shadow file."
# task: 7
def test_all_suite_runs_pass_cutoff_and_keep_system_python(api, fake_uv):
    v = api.load(REPO)
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
    calls = uv_calls(fake_uv)
    assert calls
    for argv in calls:
        assert option_values(argv, "--exclude-newer") == [v.cutoff]
        assert "dev" not in option_values(argv, "--python")
        for dependency in option_values(argv, "--with"):
            name = package_name(dependency)
            if name in v.packages:
                assert dependency == f"{name}=={v.packages[name]}"
    assert any(
        "/usr/bin/python3" in option_values(argv, "--python")
        for argv in calls
    )


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 6
def test_api_remediation_is_unpinned_and_frozen(api):
    snippets = importlib.import_module("check_snippets")
    v = api.load(REPO)
    argv = expand_remediation(api, v, snippets.API_REMEDIATION)
    assert "--api" in argv
    assert option_values(argv, "--exclude-newer") == [v.cutoff]
    assert not any(
        "==" in dependency and package_name(dependency) in v.packages
        for dependency in option_values(argv, "--with")
    )


# spec: "`build/check_snippets.py`: `PINNED` (moved out of `build/snippet_preamble.py`), `RUN_REMEDIATION` and `API_REMEDIATION`."
# task: 6
def test_snippet_pins_and_run_remediation_read_the_manifest(api):
    snippets = importlib.import_module("check_snippets")
    preamble = importlib.import_module("snippet_preamble")
    v = api.load(REPO)
    assert not hasattr(preamble, "PINNED")
    assert set(snippets.PINNED) == set(v.stack("snippets"))
    argv = expand_remediation(api, v, snippets.RUN_REMEDIATION)
    assert set(v.stack("snippets")) <= set(option_values(argv, "--with"))


# spec: "`versions.py check` runs offline."
# task: 9
def test_check_needs_no_network_or_resolver(api, checker, root, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("The offline lint attempted resolution or network access")

    monkeypatch.setattr(api, "fetch_json", forbidden)
    monkeypatch.setattr(api, "resolve", forbidden)
    monkeypatch.setattr(api, "run_process", forbidden)
    assert findings(checker, root) == []
    assert api.main(["check"], root=root) == 0


# spec: "**Equality** ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision."
# task: 9
@pytest.mark.parametrize(
    ("valid", "stale"),
    [
        ("verified on Polars 2.0", "verified on Polars 1.42"),
        ("verified on arviz-stats 1.3", "verified on arviz-stats 1.1"),
        ("numpyro==0.22.0", "numpyro==0.21.0"),
        (
            "NumPyro: checked in the 0.22.0 source",
            "NumPyro: checked in the 0.21.0 source",
        ),
        ("verified on Python 3.13", "verified on Python 3.14"),
    ],
)
def test_equality_citations_have_stale_positive_controls(
    checker, root, valid, stale
):
    relative = "skills/bayesian-workflow/references/diagnostics.md"
    write(root, relative, valid + "\n")
    assert findings(checker, root) == []
    write(root, relative, stale + "\n")
    assert findings(checker, root)


# spec: "**Range** (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file's value."
# task: 9
@pytest.mark.parametrize(
    ("valid", "stale"),
    [
        ("NumPyro ≥ 0.22", "NumPyro ≥ 1.0"),
        ("Python 3.11+", "Python 3.14+"),
        ("great-docs>=0.17.0,<0.18", "great-docs>=0.17.0,<0.17.0"),
        ("great-docs<0.18", "great-docs<0.17.0"),
    ],
)
def test_prose_ranges_have_stale_positive_controls(
    checker, root, valid, stale
):
    relative = "skills/recommend-probabilistic-model/SKILL.md"
    write(root, relative, valid + "\n")
    assert findings(checker, root) == []
    write(root, relative, stale + "\n")
    assert findings(checker, root)


# spec: "**Range** (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file's value."
# task: 9
def test_script_header_floor_is_compared_with_the_pin(api, checker, root):
    skill(root)
    assert findings(checker, root) == []
    path = root / "build/versions.toml"
    path.write_text(path.read_text().replace("polars = '2.0.0'", "polars = '1.42'"))
    api.sync(root)
    assert findings(checker, root)


# spec: "`HISTORICAL` is keyed by the literal phrase, not by file and line, and each entry gives its reason."
# task: 9
def test_history_allowlist_follows_the_phrase_when_it_moves(checker, root):
    phrase = "ArviZ 0.23"
    first = "skills/bayesian-workflow/references/diagnostics.md"
    second = "skills/bayesian-workflow/references/model-comparison.md"
    write(root, first, phrase + "\n")
    assert findings(checker, root, historical={})
    allowed = {phrase: "History, by design"}
    assert findings(checker, root, historical=allowed) == []
    (root / first).unlink()
    write(root, second, "\n\n" + phrase + "\n")
    assert findings(checker, root, historical=allowed) == []
    assert findings(checker, root, historical={})


# spec: "`HISTORICAL` is keyed by the literal phrase, not by file and line, and each entry gives its reason."
# task: 9
def test_history_entries_have_literal_keys_and_reasons(checker):
    assert checker.HISTORICAL
    assert all(
        isinstance(phrase, str) and phrase.strip()
        and isinstance(reason, str) and reason.strip()
        for phrase, reason in checker.HISTORICAL.items()
    )


# spec: "A live file spells `--python 3.<n>`."
# task: 9
@pytest.mark.parametrize(
    "relative",
    [
        "CLAUDE.md",
        "AGENTS.md",
        "GEMINI.md",
        "build/cc_guide/lint.py",
        "hooks/README.md",
        "skills/explore-data/SKILL.md",
        ".claude/skills/cc-guide/SKILL.md",
    ],
)
def test_interpreter_literals_fail_even_when_they_match_dev(
    checker, root, relative
):
    write(root, relative, "uv run --python /usr/bin/python3 python\n")
    assert findings(checker, root) == []
    write(root, relative, "uv run --python 3.13 python\n")
    assert findings(checker, root)


# spec: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
def test_script_and_skill_floors_must_match(checker, root):
    skill(root, floor="3.11", requires="3.11")
    assert findings(checker, root) == []
    skill(root, floor="3.11", requires="3.12")
    assert findings(checker, root)


# spec: "The dev Python must satisfy each floor."
# task: 9
def test_matching_floors_can_still_exceed_dev_python(checker, root):
    skill(root, floor="3.11", requires="3.11")
    assert findings(checker, root) == []
    skill(root, floor="3.14", requires="3.14")
    assert findings(checker, root)


# spec: "`check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures."
# task: 9
@pytest.mark.parametrize(
    "relative",
    [
        "specs/deferred_items.md",
        "specs/verification/66-uv-probe.md",
        "LICENSE",
        "LICENSE.md",
        "data/example.md",
        "skills/explore-data/data/example.md",
        "build/fixtures/example.md",
    ],
)
def test_excluded_locations_do_not_generate_findings(checker, root, relative):
    write(root, relative, "uv run --python 3.13 python\nverified on Polars 1.38\n")
    assert findings(checker, root) == []


# spec: "Known limit: `check` sees only the package names that the file lists."
# task: 9
def test_an_unlisted_package_is_outside_citation_checking(checker, root):
    write(
        root,
        "skills/explore-data/SKILL.md",
        "verified on scipy 0.21.0\n",
    )
    assert findings(checker, root) == []


# spec: "The `drift` report states this limit."
# task: 8
def test_drift_discloses_its_package_inventory_limit(api, root):
    v = api.load(root)
    data = metadata(v)
    code, report = api.drift(
        root,
        fetch=metadata_fetch(data),
        resolver=lambda requirements, python_version, cutoff: {
            name: data[name]["info"]["version"] for name in v.packages
        },
        newest_python=lambda: "3.14",
        runner=lambda *args, **kwargs: 0,
    )
    assert code == 0
    assert re.search(
        r"(only|limit)[^\n]*(package|list|name)|"
        r"(package|list|name)[^\n]*(only|limit)",
        report,
        re.IGNORECASE,
    )


# spec: "Documented commands spell no interpreter or package version."
# task: 13
def test_documented_uv_commands_have_no_version_literals():
    paths = {
        REPO / "CLAUDE.md",
        REPO / "AGENTS.md",
        REPO / "GEMINI.md",
        REPO / "build/run_commit_lints.sh",
    }
    for directory in ("build", "hooks", "skills", ".claude/skills"):
        base = REPO / directory
        if base.exists():
            paths.update(
                path for path in base.rglob("*")
                if path.is_file() and path.suffix in {".py", ".md", ".sh"}
                and not {"data", "fixtures", "__pycache__"} & set(path.parts)
            )

    checked = 0
    for path in sorted(paths):
        source = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            source = ast.get_docstring(ast.parse(source)) or ""
        source = re.sub(r"\\\r?\n\s*", " ", source)
        for line in source.splitlines():
            if not re.search(r"\buv\s+run\b", line):
                continue
            checked += 1
            assert not re.search(r"--python(?:=|\s+)['\"]?3\.\d+", line), (
                path, line
            )
            assert not re.search(
                r"\b[A-Za-z][\w.-]*(?:==|>=|<=|~=|>|<)\s*\d", line
            ), (path, line)
    assert checked


# spec: "The file does not hold the script floors (`requires-python`, `compatibility:`) or the 3.9 floor of `install.py` and the read-only agent guard."
# task: 4
def test_manifest_contains_only_the_dev_interpreter_role(api):
    raw = tomllib.loads((REPO / "build/versions.toml").read_text())
    assert set(raw["python"]) == {"dev"}
    assert not {"requires-python", "compatibility", "floor"} & set(raw)


# spec: "Script floors (3.11, 3.12) and the 3.9 floor stay user promises in their own files"
# task: 13
@pytest.mark.parametrize(
    ("relative", "floor"),
    [
        ("skills/explore-data/scripts/profile.py", "3.11"),
        ("skills/recommend-visualization/scripts/recommend.py", "3.11"),
        ("skills/recommend-probabilistic-model/scripts/characterize.py", "3.11"),
        ("skills/geographic-codes/scripts/build.py", "3.11"),
        ("skills/classification-codes/scripts/build.py", "3.11"),
        ("skills/bayesian-workflow/scripts/diagnose_model.py", "3.12"),
        ("skills/bayesian-workflow/scripts/calibration_check.py", "3.12"),
        ("skills/track-model-experiments/scripts/compare_experiments.py", "3.12"),
    ],
)
def test_migration_preserves_known_script_floors(relative, floor):
    source = (REPO / relative).read_text()
    match = re.search(
        r"(?m)^#\s*requires-python\s*=\s*['\"]([^'\"]+)['\"]", source
    )
    assert match
    assert match.group(1) == f">={floor}"


# spec: "Pin Polars at the latest release (2.0.0 on 2026-10-21)."
# task: 10
def test_polars_pin_preserves_the_required_api_floor(api):
    version = api.load(REPO).packages["polars"]
    release = tuple(int(part) for part in version.split("."))
    assert release >= (2, 0, 0)


# spec: "`versions.py check` exits 0."
# task: 13
def test_migrated_tree_passes_the_complete_lint(api, checker):
    assert checker.check(root=REPO) == []
    assert api.main(["check"], root=REPO) == 0


# spec: "`versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`."
# task: 14
def test_versions_lint_is_wired_and_the_documented_count_is_ten():
    runner = (REPO / "build/run_commit_lints.sh").read_text()
    hook = (REPO / "build/githooks/pre-commit").read_text()
    guide = (REPO / "CLAUDE.md").read_text()
    assert "versions_check" in runner
    assert re.search(
        r"uv\s+run\s+python\s+build/versions\.py\s+check", runner
    )
    assert "run_commit_lints.sh" in hook or "versions_check" in hook
    assert re.search(
        r"(?:\b10\b|\bten\b)[^\n]*commit lints|"
        r"commit lints[^\n]*(?:\b10\b|\bten\b)",
        guide,
        re.IGNORECASE,
    )


# spec: "`setup-uv` takes the interpreter from `.python-version`."
# task: 14
def test_lints_setup_uv_does_not_select_a_literal_interpreter():
    workflow = (REPO / ".github/workflows/lints.yml").read_text()
    assert "setup-uv@" in workflow
    assert (REPO / ".python-version").is_file()
    assert not re.search(
        r"(?m)^\s*python-version\s*:\s*['\"]?3\.\d+", workflow
    )


# spec: "A new workflow, `.github/workflows/versions-drift.yml`, runs `versions.py drift` weekly on a cron schedule and on manual dispatch."
# task: 15
def test_drift_workflow_has_a_weekly_schedule_and_manual_dispatch():
    workflow = (REPO / ".github/workflows/versions-drift.yml").read_text()
    assert re.search(r"(?m)^\s*workflow_dispatch\s*:", workflow)
    schedules = re.findall(
        r"(?m)^\s*-\s*cron\s*:\s*['\"]([^'\"]+)['\"]", workflow
    )
    assert schedules
    assert any(
        re.fullmatch(
            r"\d{1,2}\s+\d{1,2}\s+\*\s+\*\s+"
            r"(?:[0-6]|SUN|MON|TUE|WED|THU|FRI|SAT)",
            schedule.upper(),
        )
        for schedule in schedules
    )
    assert re.search(r"versions\.py\s+drift\b", workflow)


# spec: "It has `permissions: contents: read`, and it pins its actions by SHA, as `lints.yml` does."
# task: 15
def test_drift_workflow_permissions_and_action_pins():
    workflow = (REPO / ".github/workflows/versions-drift.yml").read_text()
    assert (
        re.search(r"permissions\s*:\s*\{\s*contents\s*:\s*read\s*\}", workflow)
        or re.search(
            r"(?m)^\s*permissions\s*:\s*\n\s+contents\s*:\s*read\s*$",
            workflow,
        )
    )
    assert not re.search(r"(?m)^\s*[\w-]+\s*:\s*write\s*$", workflow)
    actions = re.findall(r"\buses\s*:\s*['\"]?([^'\"\s#]+)", workflow)
    assert actions
    for action in actions:
        assert re.search(r"@[0-9a-fA-F]{40}$", action), action


# spec: "It writes the drift report to the job summary."
# task: 15
def test_drift_workflow_routes_output_to_the_summary():
    workflow = (REPO / ".github/workflows/versions-drift.yml").read_text()
    assert "GITHUB_STEP_SUMMARY" in workflow
    assert re.search(r"versions\.py\s+drift\b", workflow)


# spec: "It never opens an issue or a PR, and it never commits."
# task: 15
def test_drift_workflow_has_no_issue_pr_or_commit_commands():
    workflow = (REPO / ".github/workflows/versions-drift.yml").read_text()
    assert not re.search(
        r"\bgh\s+(?:issue|pr)\s+create\b|"
        r"\bgit\s+(?:commit|push)\b|"
        r"create-pull-request|"
        r"(?:issues|pulls)\.create\b",
        workflow,
        re.IGNORECASE,
    )


# spec: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`."
# task: 12
def test_old_lock_paths_are_retired():
    assert not (REPO / "specs/verification/32-jax-cpu.in").exists()
    assert not (REPO / "specs/verification/32-jax-cpu.txt").exists()
    for relative in ("CLAUDE.md", "build/check_jax_examples.py"):
        text = (REPO / relative).read_text()
        assert "specs/verification/32-jax-cpu.in" not in text
        assert "specs/verification/32-jax-cpu.txt" not in text


# spec: "Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python."
# task: 12
def test_python_target_rule_names_the_versions_file():
    text = (REPO / "rules/clean-code-python.md").read_text()
    assert "build/versions.toml" in text
    assert "agent-skills: 3.13" not in text
</tests>
<flags>
</flags>
<untestable>
On 2026-10-21 the owner found NumPyro at 0.21.0 in one deferred item and at 0.22.0 in `PINNED`.
This work is not part of plan 64 (bayesian-workflow and recommend-probabilistic-model routing).
A floor states when an API appeared.
A new upstream release does not make it stale.
A floating gate would have changed today: jax 0.12.0.1 was uploaded on 2026-10-21.
The plan must re-check items 2 to 6 before it relies on them.
The values above are the 2026-10-21 state.
The plan sets the real values with `bump` (R3).
The plan confirms that Claude Code, Codex and Gemini also ignore a plain file in a skills directory.
Every `uv run` in the repo uses the dev interpreter with no `--python` flag, from any subdirectory
Every `uv run` from the repo root resolves as of the freeze date, script headers included.
CI and a local machine resolve alike, because uv reads a bare date in local time (Inventory, uv item 7)
It shadows the root date under `skills/`, so a skill script that a user runs floats within its floors (D8), whatever the path form
`build/cc_guide/notice.sh:114` and `build/githooks/pre-commit:15`: they can run outside the repo's working directory, so they take the interpreter from the file and not from a literal.
A person changes a `[cited]` entry only after re-checking the cited behavior.
A bump follows these steps, in one change:
It flags each package that resolves below its newest release.
A pin uploaded after the freeze date names the package and the date.
`HISTORICAL` is keyed by the literal phrase, not by file and line, and each entry gives its reason.
It follows the model of `DOCUMENTED_ABSENT` in `build/check_snippets.py`.
Illustrative text, such as the run manifest at `skills/evaluate-deep-learning/references/experiments.md:86-87`, goes on `HISTORICAL` with a reason.
`CLAUDE.md`'s count of commit lints, `build/githooks/pre-commit` and `build/test_commit_lints.py` change with it.
`.github/workflows/lints.yml` keeps its steps.
The job may go red, but it is not a required check.
Known limit: GitHub disables scheduled workflows in a public repository after 60 days with no activity.
The spec accepts this.
It does not work around it.
Re-probe the uv behaviors in the Inventory (items 2 to 6, the shadow file under `skills/`, and nested-worktree inheritance) on the uv version of the day.
Record the results in `specs/verification/`.
If a behavior changed, stop and bring the change to the owner before going on.
Write `build/versions.toml`, then run `bump` and `verify` on the day of execution.
The JAX CPU examples must pass on it.
If they fail, add a temporary `[[override]]` for `jax-cpu` with its reason, and log a deferred item to remove it.
For each stale citation, either re-verify the cited behavior on the file's version and update the citation, or move it to `HISTORICAL` with the reason "verified on X, not re-checked on Y" and log a deferred item to re-check it.
Never change a citation's version without a re-check.
Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says "on the pinned 0.21.0".
The plan-32 verification records keep their old versions as history.
The plan writes each test before its code (red, then green).
Cover schema validation, `stack()` with and without an override, and the exact text that `sync` writes.
`build/test_run_suites.py` and `build/test_check_frontmatter.py:434` build their expected commands from the file, not from a `3.13` literal.
No third-party text enters the repo, so `NOTICE` and the license files do not change.
The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.
This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
The R6 prose fixes rebase onto them and re-take the line numbers.
R2.4 removes the version flags from the commands, so `CLAUDE.md` gets shorter.
</untestable>