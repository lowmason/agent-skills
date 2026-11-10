<tests>
import datetime as dt
import importlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tomllib
from urllib.error import URLError

import pytest

import run_suites
import versions
import versions_check


REPO = Path(versions.__file__).resolve().parents[1]

BASE = """\
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


def put(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if (root / ".git").exists():
        subprocess.run(
            ["git", "-C", str(root), "add", "--", relative],
            check=True,
            capture_output=True,
        )
    return path


def options(argv, option):
    result = []
    for index, argument in enumerate(argv):
        if argument == option:
            result.append(argv[index + 1])
        elif argument.startswith(option + "="):
            result.append(argument.split("=", 1)[1])
    return result


def requirement_names(requirements):
    return {
        re.split(r"[<>=!~;\[\s]", requirement, maxsplit=1)[0]
        for requirement in requirements
    }


def skill(root, body="", floor="3.11"):
    return put(
        root,
        "skills/sample/SKILL.md",
        "---\n"
        "name: sample\n"
        "description: Acceptance fixture.\n"
        f"compatibility: Python {floor}+\n"
        "---\n\n"
        + body,
    )


def script(root, floor="3.11", dependencies="polars>=2.0", body=""):
    return put(
        root,
        "skills/sample/scripts/example.py",
        "# /// script\n"
        f'# requires-python = ">={floor}"\n'
        f'# dependencies = ["{dependencies}"]\n'
        "# ///\n"
        + body,
    )


def metadata_fetch(v, latest=None):
    current = {**v.packages, **v.cited}
    newest = {**current, **(latest or {})}

    def fetch(url):
        match = re.search(r"/pypi/([^/]+)(?:/([^/]+))?/json", url)
        assert match, url
        package, requested = match.groups()
        release_versions = {current[package], newest[package]}
        releases = {
            version: [
                {
                    "filename": f"{package}-{version}-py3-none-any.whl",
                    "packagetype": "bdist_wheel",
                    "requires_python": ">=3.11",
                    "yanked": False,
                    "upload_time": "2026-10-19T12:00:00",
                    "upload_time_iso_8601": "2026-10-19T12:00:00Z",
                }
            ]
            for version in release_versions | ({requested} if requested else set())
        }
        selected = requested or newest[package]
        return {
            "info": {"name": package, "version": selected},
            "releases": releases,
            "urls": releases[selected],
        }

    return fetch


@pytest.fixture
def root(tmp_path):
    subprocess.run(
        ["git", "init", "--quiet", str(tmp_path)],
        check=True,
        capture_output=True,
    )
    put(tmp_path, "build/versions.toml", BASE)
    versions.sync(tmp_path)
    return tmp_path


@pytest.fixture
def uv_stub(tmp_path, monkeypatch, root):
    directory = tmp_path / "stub-bin"
    directory.mkdir()
    executable = directory / "uv"
    executable.write_text(
        f"#!{sys.executable}\n"
        """
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
with open(os.environ["ACCEPT_UV_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps(args) + "\\n")

needle = os.environ.get("ACCEPT_UV_FAIL_ON", "")
if needle and needle in " ".join(args):
    print("joint resolve conflict: jax and numpyro; network or resolve failed",
          file=sys.stderr)
    raise SystemExit(int(os.environ.get("ACCEPT_UV_RC", "7")))

if "pip" in args and "compile" in args:
    pins = json.loads(os.environ["ACCEPT_UV_VERSIONS"])
    output = "".join(f"{name}=={version}\\n"
                     for name, version in sorted(pins.items()))
    for index, argument in enumerate(args):
        if argument in ("-o", "--output-file"):
            Path(args[index + 1]).write_text(output, encoding="utf-8")
        elif argument.startswith("--output-file="):
            Path(argument.split("=", 1)[1]).write_text(output, encoding="utf-8")
    print(output, end="")
""",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    log = tmp_path / "uv-calls.jsonl"
    v = versions.load(root)
    resolved = {**v.packages, "jax": "0.12.0.1", "scipy": "1.0"}
    monkeypatch.setenv("PATH", str(directory) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("ACCEPT_UV_LOG", str(log))
    monkeypatch.setenv("ACCEPT_UV_VERSIONS", json.dumps(resolved))
    monkeypatch.setattr(versions, "fetch_json", metadata_fetch(v))
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")

    def calls():
        if not log.exists():
            return []
        return [
            json.loads(line)
            for line in log.read_text(encoding="utf-8").splitlines()
        ]

    return calls


# spec: "A missing or invalid file names the key."
# task: 2
@pytest.mark.parametrize(
    ("old", "new", "key"),
    [
        ("dev = '3.13'", "", "dev"),
        ("dev = '3.13'", "dev = 3.13", "dev"),
        ("date = 2026-10-19", "", "date"),
        ("date = 2026-10-19", "date = '2026-10-19'", "date"),
        ("jax = '0.12.0'", "jax = '>=0.12.0'", "jax"),
        (
            "snippets = ['arviz', 'arviz-base', 'arviz-stats', 'arviz-plots', 'numpyro', 'jax', 'numpy', 'matplotlib']",
            "snippets = 'jax'",
            "snippets",
        ),
    ],
)
def test_schema_errors_identify_the_key(old, new, key):
    with pytest.raises(versions.VersionsError) as error:
        versions.parse(BASE.replace(old, new))
    assert key in str(error.value)


# spec: "A missing or invalid file names the key."
# task: 2
def test_missing_file_identifies_versions_file(tmp_path):
    with pytest.raises(versions.VersionsError) as error:
        versions.load(tmp_path)
    assert "versions.toml" in str(error.value)


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
@pytest.mark.parametrize(
    "text",
    [
        BASE.replace("'arviz', 'arviz-base'", "'tensorstore', 'arviz-base'"),
        BASE
        + """
[[override]]
gate = 'jax-cpu'
package = 'tensorstore'
version = '1.0'
reason = 'Acceptance fixture.'
""",
    ],
)
def test_unknown_package_errors_identify_package(text):
    with pytest.raises(versions.VersionsError) as error:
        versions.parse(text)
    assert "tensorstore" in str(error.value)


# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
@pytest.mark.parametrize("missing", ["gate", "package", "version", "reason"])
def test_override_requires_each_key(missing):
    fields = {
        "gate": "jax-cpu",
        "package": "jax",
        "version": "0.11.2",
        "reason": "The JAX CPU examples require this temporary override.",
    }
    text = BASE + "\n[[override]]\n" + "".join(
        f"{key} = {value!r}\n"
        for key, value in fields.items()
        if key != missing
    )
    with pytest.raises(versions.VersionsError) as error:
        versions.parse(text)
    assert missing in str(error.value)


# spec: "`build/versions.py` gives the other build scripts these values: the dev Python, the freeze date, and `stack(gate)`, the list of `pkg==version` strings for a gate after overrides."
# task: 2
def test_stack_without_override():
    v = versions.parse(BASE)
    assert v.dev_python == "3.13"
    assert v.freeze == dt.date(2026, 10, 19)
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


# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_override_changes_only_its_gate():
    v = versions.parse(
        BASE
        + """
[[override]]
gate = 'jax-cpu'
package = 'jax'
version = '0.11.2'
reason = 'The JAX CPU examples require this temporary override.'
"""
    )
    assert "jax==0.11.2" in v.stack("jax-cpu")
    assert "jax==0.12.0" in v.stack("snippets")
    assert v.packages["jax"] == "0.12.0"


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_synced_output_contents(root):
    v = versions.load(root)
    expected = versions.outputs(v)
    assert set(expected) == {".python-version", "uv.toml", "skills/uv.toml"}
    for relative, text in expected.items():
        assert (root / relative).read_text(encoding="utf-8") == text
    assert (root / ".python-version").read_text().strip() == "3.13"
    assert tomllib.loads((root / "uv.toml").read_text()) == {
        "exclude-newer": "2026-10-20T00:00:00Z"
    }
    shadow = (root / "skills/uv.toml").read_text()
    assert tomllib.loads(shadow) == {}
    assert any(
        line.lstrip().startswith("#") and "build/versions.toml" in line
        for line in shadow.splitlines()
    )


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
@pytest.mark.parametrize("relative", [".python-version", "uv.toml", "skills/uv.toml"])
def test_sync_check_fails_without_rewriting_a_stale_output(root, relative):
    path = root / relative
    path.write_text("# stale output\n", encoding="utf-8")
    before = path.read_bytes()
    assert versions.main(["sync", "--check"], root=root) != 0
    assert path.read_bytes() == before
    assert versions.main(["sync"], root=root) == 0
    assert versions.main(["sync", "--check"], root=root) == 0


# spec: "Files uploaded on the freeze date itself (UTC) are included."
# task: 2
@pytest.mark.parametrize(
    ("date", "cutoff"),
    [
        ("2026-10-19", "2026-10-20T00:00:00Z"),
        ("2026-10-21", "2026-10-22T00:00:00Z"),
    ],
)
def test_cutoff_is_next_day_utc(date, cutoff):
    v = versions.parse(BASE.replace("2026-10-19", date))
    assert v.cutoff == cutoff
    assert tomllib.loads(versions.outputs(v)["uv.toml"])["exclude-newer"] == cutoff


# spec: "An invalid date names the value."
# task: 3
def test_invalid_date_names_its_value():
    with pytest.raises(versions.VersionsError) as error:
        versions.parse_date("2026-10-32")
    assert "2026-10-32" in str(error.value)


# spec: "Sets the freeze date (default: today, UTC) and does one joint resolve, as of that date and on the dev Python, of every `[packages]` entry together."
# task: 3
def test_bump_jointly_resolves_every_package_on_dev_python(root):
    before = versions.load(root)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((list(requirements), python_version, cutoff))
        return {**before.packages, "jax": "0.12.0.1", "scipy": "1.0"}

    versions.bump(root, dt.date(2026, 10, 21), resolver=resolver)
    assert len(calls) == 1
    requirements, python_version, cutoff = calls[0]
    assert requirement_names(requirements) == set(before.packages)
    assert all("==" not in requirement for requirement in requirements)
    assert python_version == before.dev_python
    assert cutoff == "2026-10-22T00:00:00Z"
    after = versions.load(root)
    assert after.freeze == dt.date(2026, 10, 21)
    assert after.packages["jax"] == "0.12.0.1"
    assert "scipy" not in after.packages
    assert versions.main(["sync", "--check"], root=root) == 0


# spec: "With `--only`, the other entries stay at their pins in the joint resolve"
# task: 3
def test_bump_only_keeps_other_packages_pinned(root):
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
    assert "jax" in calls[0]
    for package, version in before.packages.items():
        if package != "jax":
            assert f"{package}=={version}" in calls[0]
    after = versions.load(root)
    assert after.packages == {**before.packages, "jax": "0.12.0.1"}


# spec: "`bump` never changes `[cited]`."
# task: 3
def test_bump_preserves_cited_versions(root):
    before = versions.load(root)

    def resolver(requirements, python_version, cutoff):
        return {**before.packages, **before.cited, "altair": "6.3.0"}

    versions.bump(root, dt.date(2026, 10, 21), resolver=resolver)
    assert versions.load(root).cited == before.cited


# spec: "Sets the freeze date (default: today, UTC) and does one joint resolve, as of that date and on the dev Python, of every `[packages]` entry together."
# task: 3
def test_bump_default_date_is_today_utc(root, uv_stub):
    first = dt.datetime.now(dt.timezone.utc).date()
    assert versions.main(["bump"], root=root) == 0
    last = dt.datetime.now(dt.timezone.utc).date()
    assert first <= versions.load(root).freeze <= last


# spec: "Other packages (pytest, pyyaml, scipy, tensorstore and the rest) get no entry, and the freeze date fixes them."
# task: 4
def test_real_package_inventory_excludes_the_named_floating_packages():
    v = versions.load(REPO)
    assert {"pytest", "pyyaml", "scipy", "tensorstore"}.isdisjoint(v.packages)
    assert "polars" in v.packages
    assert set().union(*(set(items) for items in v.gates.values())) <= set(v.packages)


# spec: "A package gets a `[cited]` entry when skill prose cites a version for it and no check runs it."
# task: 4
def test_real_cited_inventory_is_separate_from_gate_packages():
    v = versions.load(REPO)
    assert {"altair", "plotly", "optuna", "great-docs"} <= set(v.cited)
    assert set(v.cited).isdisjoint(v.packages)
    assert set(v.cited).isdisjoint(
        set().union(*(set(items) for items in v.gates.values()))
    )


# spec: "Runs `<cmd>` under `uv run` with the gate's stack and the freeze date"
# task: 5
def test_run_argv_uses_stack_and_freeze():
    v = versions.parse(BASE)
    command = ["python", "build/check_snippets.py", "--run", "skills/bayesian-workflow/"]
    argv = versions.uv_run_argv(v, "snippets", command)
    assert Path(argv[0]).name == "uv"
    assert "run" in argv
    assert argv[-len(command):] == command
    assert set(options(argv, "--with")) == set(v.stack("snippets"))
    assert options(argv, "--exclude-newer") == [v.cutoff]


# spec: "`--pin` changes one package for one run and never edits the file."
# task: 5
def test_run_pin_is_ephemeral(root, uv_stub):
    path = root / "build/versions.toml"
    before = path.read_bytes()
    assert versions.main(
        ["run", "snippets", "--pin", "jax==0.11.2", "--", "python", "-c", "pass"],
        root=root,
    ) == 0
    assert path.read_bytes() == before
    executed = uv_stub()[-1]
    installed = options(executed, "--with")
    assert "jax==0.11.2" in installed
    assert "jax==0.12.0" not in installed
    assert "numpyro==0.22.0" in installed


# spec: "A pin uploaded after the freeze date names the package and the date."
# task: 5
@pytest.mark.parametrize(
    ("uploaded", "late"),
    [
        ("2026-10-19T23:59:59Z", False),
        ("2026-10-20T00:00:00Z", True),
        ("2026-10-21T00:00:00Z", True),
    ],
)
def test_late_pin_boundary_uses_utc_cutoff(uploaded, late):
    v = versions.parse(BASE)
    files = [{"upload_time_iso_8601": uploaded, "yanked": False}]
    payload = {
        "info": {"name": "jax", "version": "0.12.0.1"},
        "urls": files,
        "releases": {"0.12.0.1": files},
    }
    result = versions.late_pins(
        v, ["jax==0.12.0.1"], fetch=lambda url: payload
    )
    assert result == (["jax==0.12.0.1"] if late else [])


# spec: "uv compares the date with the upload time of each file, not of the release."
# task: 5
def test_late_dev_python_wheel_is_not_hidden_by_an_earlier_release_file():
    v = versions.parse(BASE)
    files = [
        {
            "filename": "jaxlib-0.11.2-cp314-cp314-manylinux_2_17_x86_64.whl",
            "requires_python": ">=3.14",
            "upload_time_iso_8601": "2026-10-19T12:00:00Z",
            "yanked": False,
        },
        {
            "filename": "jaxlib-0.11.2-cp313-cp313-manylinux_2_17_x86_64.whl",
            "requires_python": ">=3.13",
            "upload_time_iso_8601": "2026-10-21T12:00:00Z",
            "yanked": False,
        },
    ]
    payload = {
        "info": {"name": "jaxlib", "version": "0.11.2"},
        "urls": files,
        "releases": {"0.11.2": files},
    }
    assert versions.late_pins(
        v, ["jaxlib==0.11.2"], fetch=lambda url: payload
    ) == ["jaxlib==0.11.2"]


# spec: "A pin uploaded after the freeze date names the package and the date."
# task: 5
def test_late_pin_error_identifies_package_and_date(root, monkeypatch, capsys):
    files = [{"upload_time_iso_8601": "2026-10-21T12:00:00Z", "yanked": False}]
    monkeypatch.setattr(
        versions,
        "fetch_json",
        lambda url: {
            "info": {"name": "jax", "version": "0.12.0.1"},
            "urls": files,
            "releases": {"0.12.0.1": files},
        },
    )
    assert versions.main(
        ["run", "snippets", "--pin", "jax==0.12.0.1", "--", "python", "-c", "pass"],
        root=root,
    ) != 0
    captured = capsys.readouterr()
    message = captured.out + captured.err
    assert "jax" in message
    assert "2026-10-19" in message or "2026-10-21" in message


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 5
def test_run_failure_exit_against_stub_uv(root, uv_stub, monkeypatch):
    monkeypatch.setenv("ACCEPT_UV_FAIL_ON", "acceptance-failure")
    assert versions.main(
        ["run", "snippets", "--", "python", "acceptance-failure"],
        root=root,
    ) != 0


# spec: "`build/check_snippets.py`: `PINNED` (moved out of `build/snippet_preamble.py`), `RUN_REMEDIATION` and `API_REMEDIATION`."
# task: 6
def test_snippet_pins_live_in_check_snippets_and_match_versions_file():
    checker = importlib.import_module("check_snippets")
    preamble = importlib.import_module("snippet_preamble")
    assert list(checker.PINNED) == versions.load(REPO).stack("snippets")
    assert not hasattr(preamble, "PINNED")


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 6
def test_api_remediation_does_not_install_exact_package_pins():
    checker = importlib.import_module("check_snippets")
    v = versions.load(REPO)
    argv = shlex.split(checker.API_REMEDIATION)
    installed = options(argv, "--with")
    for index, argument in enumerate(argv):
        if Path(argument).name == "versions.py":
            tail = argv[index + 1:]
            if tail and tail[0] == "run":
                installed.extend(v.stack(tail[1]))
    for package in v.packages:
        assert not any(
            requirement.startswith(package + "==")
            for requirement in installed
        )
    assert "--api" in argv


# spec: "A command that needs a pinned stack uses the runner (R3):"
# task: 6
def test_snippet_run_remediation_uses_documented_runner():
    checker = importlib.import_module("check_snippets")
    argv = shlex.split(checker.RUN_REMEDIATION)
    expected = shlex.split("uv run python build/versions.py run snippets --")
    assert argv[:len(expected)] == expected
    assert "--run" in argv


# spec: "A `with` or `extras` package that `[packages]` names gets its pin."
# task: 7
@pytest.mark.parametrize("dependency", ["polars", "polars>=2.0", "numpy>=2.0"])
def test_suite_dependencies_get_central_pins(dependency):
    v = versions.parse(BASE)
    pins = run_suites.Pins.from_versions(v)
    package = re.split(r"[<>=]", dependency, maxsplit=1)[0]
    assert pins.spec(dependency) == f"{package}=={v.packages[package]}"


# spec: "Other packages (pytest, pyyaml, scipy, tensorstore and the rest) get no entry, and the freeze date fixes them."
# task: 7
@pytest.mark.parametrize("dependency", ["pytest", "pyyaml", "scipy>=1.0", "tensorstore"])
def test_suite_dependencies_without_entries_keep_their_requirements(dependency):
    pins = run_suites.Pins.from_versions(versions.parse(BASE))
    assert pins.spec(dependency) == dependency


# spec: "`build/run_suites.py`: `DEFAULT_PYTHONS` comes from the dev Python."
# task: 7
@pytest.mark.parametrize("python", ["3.13", "3.14"])
def test_suite_pin_context_takes_python_from_versions(python):
    v = versions.parse(BASE.replace("dev = '3.13'", f"dev = '{python}'"))
    pins = run_suites.Pins.from_versions(v)
    assert pins.python == python
    assert pins.cutoff == v.cutoff


# spec: "Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`"
# task: 8
def test_verify_steps_cover_the_four_required_checks():
    v = versions.parse(BASE)
    steps = versions.verify_steps(v)
    assert len(steps) == 4

    def find(filename, flag=None):
        matches = [
            step for step in steps
            if any(Path(arg).name == filename for arg in step.argv)
            and (flag is None or flag in step.argv)
        ]
        assert len(matches) == 1
        return matches[0].argv

    tier2 = find("check_snippets.py", "--api")
    tier3 = find("check_snippets.py", "--run")
    jax = find("check_jax_examples.py")
    suites = find("run_suites.py")
    assert "--all" in suites and "--extras" in suites
    assert not any("==" in item for item in options(tier2, "--with"))
    assert set(options(tier3, "--with")) == set(v.stack("snippets"))
    assert set(options(jax, "--with")) == set(v.stack("jax-cpu"))
    for argv in (tier2, tier3, jax):
        assert options(argv, "--exclude-newer") == [v.cutoff]
    assert "--with-requirements" not in jax


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
@pytest.mark.parametrize(
    "failure",
    ["--api", "--run", "check_jax_examples.py", "run_suites.py"],
)
def test_verify_failure_exit_against_stub_uv(root, uv_stub, monkeypatch, failure):
    monkeypatch.setenv("ACCEPT_UV_FAIL_ON", failure)
    assert versions.main(["verify"], root=root) != 0


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
def test_verify_success_exit_against_stub_uv(root, uv_stub):
    assert versions.main(["verify"], root=root) == 0
    assert len(uv_stub()) == 4


# spec: "`bump` exits 2 on a network or resolve failure and names the step."
# task: 3
def test_bump_resolve_failure_exit_against_stub_uv(
    root, uv_stub, monkeypatch, capsys
):
    monkeypatch.setenv("ACCEPT_UV_FAIL_ON", "compile")
    assert versions.main(["bump", "--date", "2026-10-21"], root=root) == 2
    captured = capsys.readouterr()
    assert re.search(r"resolve|compile", captured.out + captured.err, re.I)


# spec: "A joint resolve that fails in `bump` or `drift` names the packages in conflict."
# task: 8
@pytest.mark.parametrize(
    "argv",
    [["bump", "--date", "2026-10-21"], ["drift"]],
)
def test_joint_resolve_error_names_conflicting_packages(
    root, uv_stub, monkeypatch, capsys, argv
):
    monkeypatch.setenv("ACCEPT_UV_FAIL_ON", "compile")
    assert versions.main(argv, root=root) == 2
    captured = capsys.readouterr()
    message = captured.out + captured.err
    assert "jax" in message
    assert "numpyro" in message


# spec: "Does the same joint resolve as `bump`, with no freeze date and no pins, in two passes: first on the dev Python, then on the newest stable Python."
# task: 8
def test_drift_jointly_resolves_both_python_passes_without_freeze_or_pins(
    root, monkeypatch
):
    v = versions.load(root)
    calls = []
    executed = []
    latest = {"jax": "0.12.0.1", "altair": "6.3.0", "plotly": "7.1.0"}

    def resolver(requirements, python_version, cutoff):
        calls.append((list(requirements), python_version, cutoff))
        return {**v.packages, **v.cited, **latest}

    def runner(argv, root, env):
        executed.append(list(argv))
        return 0

    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")
    code, report = versions.drift(
        root,
        fetch=metadata_fetch(v, latest),
        resolver=resolver,
        runner=runner,
    )
    assert code == 0
    assert [python for _, python, _ in calls] == ["3.13", "3.14"]
    for requirements, _, cutoff in calls:
        assert cutoff is None
        assert set(v.packages) <= requirement_names(requirements)
        assert all("==" not in requirement for requirement in requirements)
    assert len(executed) == 8
    assert all(not options(argv, "--exclude-newer") for argv in executed)
    assert "3.13" in report and "3.14" in report


# spec: "For each pass it reports, for each `[packages]` and `[cited]` entry, the pinned version, the resolved version, the newest release and its upload date."
# task: 8
def test_drift_report_includes_packages_cited_versions_and_upload_dates(
    root, monkeypatch
):
    v = versions.load(root)
    latest = {"jax": "0.12.0.1", "altair": "6.3.0", "plotly": "7.1.0"}
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")
    code, report = versions.drift(
        root,
        fetch=metadata_fetch(v, latest),
        resolver=lambda requirements, python_version, cutoff: {
            **v.packages, **v.cited, **latest
        },
        runner=lambda argv, root, env: 0,
    )
    assert code == 0
    for package, pinned in {**v.packages, **v.cited}.items():
        rows = [line for line in report.splitlines() if package in line]
        assert len(rows) >= 2
        assert any(pinned in line for line in rows)
        assert any(latest.get(package, pinned) in line for line in rows)
    assert "2026-10-19" in report


# spec: "It flags each package that resolves below its newest release."
# task: 8
def test_drift_flags_a_resolution_below_the_newest_release(root, monkeypatch):
    v = versions.load(root)
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")
    _, report = versions.drift(
        root,
        fetch=metadata_fetch(v, {"jax": "0.12.0.1"}),
        resolver=lambda requirements, python_version, cutoff: {
            **v.packages, **v.cited
        },
        runner=lambda argv, root, env: 0,
    )
    lines = [
        line for line in report.splitlines()
        if "jax" in line and "0.12.0" in line and "0.12.0.1" in line
    ]
    assert lines
    assert any(
        re.search(r"below|behind|lag|blocked|outdated|flag|[!⚠<]", line, re.I)
        for line in lines
    )


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
@pytest.mark.parametrize("gate_result, expected", [(0, 0), (7, 1)])
def test_drift_gate_exit_codes(root, monkeypatch, gate_result, expected):
    v = versions.load(root)
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")
    code, report = versions.drift(
        root,
        fetch=metadata_fetch(v),
        resolver=lambda requirements, python_version, cutoff: {
            **v.packages, **v.cited
        },
        runner=lambda argv, root, env: gate_result,
    )
    assert code == expected
    assert report.strip()


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_network_failure_is_reported_as_exit_two(root, monkeypatch):
    v = versions.load(root)
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")

    def offline(url):
        raise URLError("network unavailable")

    code, report = versions.drift(
        root,
        fetch=offline,
        resolver=lambda requirements, python_version, cutoff: {
            **v.packages, **v.cited
        },
        runner=lambda argv, root, env: 0,
    )
    assert code == 2
    assert re.search(r"network|unavailable|resolve", report, re.I)


# spec: "The `drift` report states this limit."
# task: 8
def test_drift_report_states_its_package_name_coverage_limit(root, monkeypatch):
    v = versions.load(root)
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")
    _, report = versions.drift(
        root,
        fetch=metadata_fetch(v),
        resolver=lambda requirements, python_version, cutoff: {
            **v.packages, **v.cited
        },
        runner=lambda argv, root, env: 0,
    )
    assert versions.DRIFT_LIMIT in report
    assert re.search(r"only|limit", versions.DRIFT_LIMIT, re.I)
    assert re.search(r"name|list|file", versions.DRIFT_LIMIT, re.I)


# spec: "`versions.py check` runs offline."
# task: 9
def test_check_does_not_use_network_or_resolve(root, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("offline check attempted a network operation")

    monkeypatch.setattr(versions, "fetch_json", forbidden)
    monkeypatch.setattr(versions, "resolve", forbidden)
    assert versions_check.check(root) == []
    assert versions.main(["check"], root=root) == 0


# spec: "**Sync.** An R2.1 output differs from the file."
# task: 9
@pytest.mark.parametrize("relative", [".python-version", "uv.toml", "skills/uv.toml"])
def test_check_reports_each_stale_synced_output(root, relative):
    path = root / relative
    original = path.read_bytes()
    path.write_text("# stale\n", encoding="utf-8")
    findings = versions_check.check(root)
    assert findings
    assert any(relative in finding for finding in findings)
    path.write_bytes(original)
    assert versions_check.check(root) == []


# spec: "A live file spells `--python 3.<n>`."
# task: 9
@pytest.mark.parametrize(
    "relative",
    [
        "CLAUDE.md",
        "AGENTS.md",
        "GEMINI.md",
        "build/example.py",
        "hooks/example.sh",
        "skills/sample/SKILL.md",
        ".claude/skills/sample/SKILL.md",
    ],
)
def test_interpreter_literal_has_a_seeded_failure_in_each_live_location(
    root, relative
):
    path = put(root, relative, "uv run --python 3.13 python example.py\n")
    findings = versions_check.check(root)
    assert findings
    assert any(relative in finding for finding in findings)
    path.write_text("uv run python example.py\n", encoding="utf-8")
    assert versions_check.check(root) == []


# spec: "An interpreter path such as `/usr/bin/python3` is not a literal."
# task: 9
def test_system_interpreter_path_is_allowed(root):
    put(root, "hooks/example.sh", "uv run --python /usr/bin/python3 python example.py\n")
    assert versions_check.check(root) == []


# spec: '**Equality** ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file\'s value at the cited precision.'
# task: 9
@pytest.mark.parametrize(
    "current, stale",
    [
        ("verified on Polars 2.0", "verified on Polars 1.42"),
        ("verified on Polars 2", "verified on Polars 1"),
        ("numpyro==0.22.0", "numpyro==0.21.0"),
        (
            "NumPyro source checked in the 0.22.0",
            "NumPyro source checked in the 0.21.0",
        ),
        ("verified on Altair 6.2", "verified on Altair 6.3"),
        ("Python 3.13", "Python 3.12"),
    ],
)
def test_equality_citations_have_current_and_seeded_stale_controls(
    root, current, stale
):
    path = skill(root, current + "\n")
    assert versions_check.check(root) == []
    path.write_text(path.read_text().replace(current, stale), encoding="utf-8")
    findings = versions_check.check(root)
    assert findings
    assert any("SKILL.md" in finding for finding in findings)


# spec: '**Range** (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file\'s value.'
# task: 9
@pytest.mark.parametrize(
    "containing, excluding",
    [
        ("polars>=2.0", "polars>=2.1"),
        ("NumPyro ≥ 0.22", "NumPyro ≥ 0.23"),
        ("arviz<2.0", "arviz<1.3.0"),
        ("great-docs>=0.17.0,<0.18", "great-docs>=0.17.0,<0.17.0"),
        ("Python 3.11+", "Python 3.14+"),
    ],
)
def test_ranges_have_containing_and_seeded_excluding_controls(
    root, containing, excluding
):
    path = skill(root, containing + "\n")
    assert versions_check.check(root) == []
    path.write_text(
        path.read_text().replace(containing, excluding), encoding="utf-8"
    )
    assert versions_check.check(root)


# spec: '**History** ("ArviZ 0.23", "and earlier") passes only through the `HISTORICAL` allowlist.'
# task: 9
def test_history_requires_a_phrase_allowlist_entry(root):
    phrase = "ArviZ 0.23 and earlier"
    skill(root, phrase + "\n")
    assert versions_check.check(root, historical={})
    assert versions_check.check(
        root,
        historical={phrase: "This describes the classic stack."},
    ) == []


# spec: "`HISTORICAL` is keyed by the literal phrase, not by file and line, and each entry gives its reason."
# task: 9
def test_historical_allowlist_survives_moving_the_phrase(root):
    phrase = "ArviZ 0.23"
    historical = {phrase: "This describes the classic stack."}
    skill(root)
    put(root, "skills/sample/references/earlier.md", phrase + "\n")
    assert versions_check.check(root, historical=historical) == []
    (root / "skills/sample/references/earlier.md").unlink()
    put(root, "skills/sample/references/later.md", "\n\n\n" + phrase + "\n")
    assert versions_check.check(root, historical=historical) == []
    assert all(
        isinstance(phrase, str)
        and phrase.strip()
        and isinstance(reason, str)
        and reason.strip()
        for phrase, reason in versions_check.HISTORICAL.items()
    )


# spec: "In `skills/**/*.md` and the script headers under `skills/*/scripts/`, `check` finds each version that stands next to a `[packages]` name, a `[cited]` name or \"Python\", and classifies it by form:"
# task: 9
def test_script_header_dependency_citation_has_a_seeded_failure(root):
    skill(root)
    path = script(root, dependencies="polars>=2.0")
    assert versions_check.check(root) == []
    path.write_text(
        path.read_text().replace("polars>=2.0", "polars>=2.1"),
        encoding="utf-8",
    )
    assert versions_check.check(root)


# spec: "In `skills/**/*.md` and the script headers under `skills/*/scripts/`, `check` finds each version that stands next to a `[packages]` name, a `[cited]` name or \"Python\", and classifies it by form:"
# task: 9
def test_script_body_is_not_treated_as_a_header_citation(root):
    skill(root)
    script(root, body='EXAMPLE = "verified on Polars 1.42"\n')
    assert versions_check.check(root) == []


# spec: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
@pytest.mark.parametrize("floor", ["3.11", "3.12"])
def test_matching_script_and_compatibility_floors_pass(root, floor):
    skill(root, floor=floor)
    script(root, floor=floor)
    assert versions_check.check(root) == []


# spec: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
def test_mismatched_floors_have_a_seeded_failure(root):
    skill(root, floor="3.11")
    script(root, floor="3.12")
    findings = versions_check.check(root)
    assert findings
    assert any(
        re.search(r"floor|compatibility|requires-python", finding, re.I)
        for finding in findings
    )


# spec: "The dev Python must satisfy each floor."
# task: 9
def test_matching_floors_above_dev_python_still_fail(root):
    skill(root, floor="3.14")
    script(root, floor="3.14")
    assert versions_check.check(root)


# spec: "`check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures."
# task: 9
@pytest.mark.parametrize(
    "relative",
    [
        "specs/example.md",
        "skills/sample/LICENSE.md",
        "skills/sample/data/example.md",
        "skills/sample/tests/fixtures/example.md",
        "build/fixtures/example.md",
    ],
)
def test_excluded_locations_do_not_create_findings(root, relative):
    put(
        root,
        relative,
        "verified on Polars 1.42\nuv run --python 3.13 python example.py\n",
    )
    assert versions_check.check(root) == []


# spec: "Known limit: `check` sees only the package names that the file lists."
# task: 9
def test_unlisted_package_citation_is_outside_lint_coverage(root):
    skill(root, "pytest 0.22.0\n")
    assert versions_check.check(root) == []


# spec: "The JAX CPU examples must pass on it."
# task: 10
def test_jax_cpu_examples_pass_under_the_configured_gate():
    assert versions.main(
        ["run", "jax-cpu", "--", "python", "build/check_jax_examples.py"],
        root=REPO,
    ) == 0


# spec: "For each stale citation, either re-verify the cited behavior on the file's version and update the citation, or move it to `HISTORICAL` with the reason \"verified on X, not re-checked on Y\" and log a deferred item to re-check it."
# task: 11
def test_migrated_tree_has_no_citation_findings():
    findings = versions_check.check(REPO)
    assert not [
        finding for finding in findings
        if re.search(r"citation|historical|verified on|checked in", finding, re.I)
    ]


# spec: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`."
# task: 12
def test_old_lock_paths_are_retired_and_live_commands_use_the_runner():
    assert not (REPO / "specs/verification/32-jax-cpu.in").exists()
    assert not (REPO / "specs/verification/32-jax-cpu.txt").exists()
    claude = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    assert "--with-requirements specs/verification/32-jax-cpu.txt" not in claude
    assert "build/versions.py run jax-cpu" in claude


# spec: "Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python."
# task: 12
def test_python_rule_names_the_versions_source():
    text = (REPO / "rules/clean-code-python.md").read_text(encoding="utf-8")
    assert "build/versions.toml" in text
    assert "agent-skills: 3.13" not in text


# spec: "Documented commands spell no interpreter or package version."
# task: 13
def test_documented_uv_commands_have_no_version_flags():
    v = versions.load(REPO)
    for relative in ("CLAUDE.md", "AGENTS.md", "GEMINI.md"):
        text = (REPO / relative).read_text(encoding="utf-8")
        logical_lines = re.sub(r"\\\r?\n\s*", " ", text).splitlines()
        for line in logical_lines:
            if "uv run" not in line:
                continue
            assert not re.search(r"--python(?:=|\s+)[\"']?3\.\d+", line), relative
            for package in {**v.packages, **v.cited}:
                assert not re.search(
                    rf"\b{re.escape(package)}\s*(?:==|>=|<=|~=|>|<)\s*\d",
                    line,
                    re.I,
                ), (relative, line)


# spec: "`versions.py check` runs offline."
# task: 13
def test_final_tree_passes_the_offline_check():
    assert versions_check.check(REPO) == []
    assert versions.main(["check"], root=REPO) == 0


# spec: "`versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`."
# task: 14
def test_commit_lint_runner_contains_the_versions_check():
    text = (REPO / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    assert "versions_check" in text
    assert re.search(r"uv\s+run\s+python\s+build/versions\.py\s+check", text)


# spec: "`CLAUDE.md`'s count of commit lints, `build/githooks/pre-commit` and `build/test_commit_lints.py` change with it."
# task: 14
def test_hook_and_commit_lint_tests_include_versions_check():
    for relative in ("build/githooks/pre-commit", "build/test_commit_lints.py"):
        text = (REPO / relative).read_text(encoding="utf-8")
        assert "versions_check" in text


# spec: "`setup-uv` takes the interpreter from `.python-version`."
# task: 15
def test_lints_workflow_references_python_version_file():
    text = (REPO / ".github/workflows/lints.yml").read_text(encoding="utf-8")
    assert "setup-uv@" in text
    assert ".python-version" in text
    assert not re.search(r"python-version:\s*[\"']?3\.\d+", text)


# spec: "It has `permissions: contents: read`, and it pins its actions by SHA, as `lints.yml` does."
# task: 15
def test_drift_workflow_has_read_permission_and_sha_pinned_actions():
    text = (REPO / ".github/workflows/versions-drift.yml").read_text(
        encoding="utf-8"
    )
    assert re.search(r"permissions:\s*(?:\{\s*)?contents:\s*read\b", text)
    assert not re.search(r"\b(?:write-all|contents:\s*write)\b", text)
    actions = re.findall(r"^\s*-\s*uses:\s*([^\s#]+)", text, re.M)
    assert actions
    assert all(re.fullmatch(r"[^@\s]+@[0-9a-fA-F]{40}", action) for action in actions)


# spec: "A new workflow, `.github/workflows/versions-drift.yml`, runs `versions.py drift` weekly on a cron schedule and on manual dispatch."
# task: 15
def test_drift_workflow_has_schedule_dispatch_and_drift_command():
    text = (REPO / ".github/workflows/versions-drift.yml").read_text(
        encoding="utf-8"
    )
    assert re.search(r"\bworkflow_dispatch\s*:", text)
    assert re.search(r"\bschedule\s*:", text)
    schedules = re.findall(r"\bcron:\s*['\"]([^'\"]+)['\"]", text)
    assert schedules
    assert all(len(schedule.split()) == 5 for schedule in schedules)
    assert re.search(r"build/versions\.py\s+drift\b", text)


# spec: "It writes the drift report to the job summary."
# task: 15
def test_drift_workflow_references_the_job_summary():
    text = (REPO / ".github/workflows/versions-drift.yml").read_text(
        encoding="utf-8"
    )
    assert "GITHUB_STEP_SUMMARY" in text
</tests>
<flags>
<flag task="5"><spec>uv compares the date with the upload time of each file, not of the release.</spec><plan>the specs whose release was first uploaded at or after the cutoff</plan></flag>
<flag task="6"><spec>Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date.</spec><plan>`check_snippets.API_REMEDIATION` and `RUN_REMEDIATION` as runner commands.</plan></flag>
</flags>
<untestable>
The repo fixes package versions by hand in many places, and nothing ties the copies together.
On 2026-10-21 the owner found NumPyro at 0.21.0 in one deferred item and at 0.22.0 in `PINNED`.
The owner wants one mechanism for every package that a skill names or runs, the Python interpreter included.
This work is not part of plan 64 (bayesian-workflow and recommend-probabilistic-model routing).
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
It reads a bare date (`2026-10-19`) in the machine's local time zone, and an RFC 3339 timestamp (`2026-10-20T00:00:00Z`) as written.
The plan must re-check items 2 to 6 before it relies on them.
Nested worktrees: this repo's worktrees live inside the main checkout, at `.claude/worktrees/<name>/`.
uv searches parent directories for `uv.toml` and `.python-version`.
So after the change merges, a worktree on a branch that lacks those files inherits the main checkout's freeze date and interpreter, with no sign of it.
Plan 63 (conformance gaps, branch `claude/plan-35-conformance-gaps-427f5e`) touches `build/run_commit_lints.sh`, `install.py` and `build/test_runtime_support.py`.
Plan 64 (bayesian-workflow and recommend-probabilistic-model routing) edits bayesian-workflow prose that holds Role 3 and Role 4 citations.
The model-lifecycle spec (PR #106) adds bayesian-workflow sections.
`CLAUDE.md` has 153 lines against a 200-line budget.
`build/versions.toml` is the only file in which a person sets a package version or the dev interpreter.
The values above are the 2026-10-21 state.
The plan sets the real values with `bump` (R3).
The file does not hold the script floors (`requires-python`, `compatibility:`) or the 3.9 floor of `install.py` and the read-only agent guard.
`skills/uv.toml` is a file, not a skill.
`install.py:97-101`, `build/check_frontmatter.py:574-575` and `build/check_provenance.py:40-44` read only directories that hold a `SKILL.md`, so they skip it.
The plan confirms that Claude Code, Codex and Gemini also ignore a plain file in a skills directory.
Each run passes `--exclude-newer <date>` explicitly, because suites under `skills/` sit below the shadow file.
The `hooks` suite keeps its explicit `/usr/bin/python3` run.
`build/cc_guide/notice.sh:114` and `build/githooks/pre-commit:15`: they can run outside the repo's working directory, so they take the interpreter from the file and not from a literal.
This covers `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `build/run_commit_lints.sh`, the usage docstrings in `build/`, `hooks/` and the skill test files, and the commands in skill text.
A person changes a `[cited]` entry only after re-checking the cited behavior.
A bump follows these steps, in one change:
Run `bump`.
Run `verify`.
Run `check`, which lists each prose citation that the bump made stale.
Re-verify or rewrite each stale citation (R5.5).
Commit.
The report states which.
It follows the model of `DOCUMENTED_ABSENT` in `build/check_snippets.py`.
Illustrative text, such as the run manifest at `skills/evaluate-deep-learning/references/experiments.md:86-87`, goes on `HISTORICAL` with a reason.
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
If they fail, add a temporary `[[override]]` for `jax-cpu` with its reason, and log a deferred item to remove it.
Pin Polars at the latest release (2.0.0 on 2026-10-21).
This keeps the `polars>=2.0` floors that the portability plan set on purpose (`specs/plans/completed/53-agent-skills-portability.md`, decision DF4).
Never change a citation's version without a re-check.
The known stale citations are the Polars, Altair and plotly lines, `skills/bayesian-workflow/references/model-comparison.md:130`, `references/model-criticism.md:196` and `skills/deep-learning/references/frameworks.md:94-95`.
Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says "on the pinned 0.21.0".
The plan-32 verification records keep their old versions as history.
The plan writes each test before its code (red, then green).
`build/test_run_suites.py` and `build/test_check_frontmatter.py:434` build their expected commands from the file, not from a `3.13` literal.
No third-party text enters the repo, so `NOTICE` and the license files do not change.
The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.
It edits `build/run_commit_lints.sh`.
This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
They edit bayesian-workflow prose that holds Role 3 and Role 4 citations.
The R6 prose fixes rebase onto them and re-take the line numbers.
R2.4 removes the version flags from the commands, so `CLAUDE.md` gets shorter.
</untestable>