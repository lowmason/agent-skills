<tests>
import datetime as dt
import json
import os
import re
import shlex
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from build import check_snippets, run_suites, snippet_preamble, versions, versions_check


REPO = Path(versions.__file__).resolve().parent.parent

SOURCE = """
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
""".lstrip()

OVERRIDE = """
[[override]]
gate = 'jax-cpu'
package = 'jax'
version = '0.11.2'
reason = 'The JAX CPU examples need a temporary override.'
"""

STATE = tomllib.loads(SOURCE)
CUTOFF = "2026-10-20T00:00:00Z"
OUTPUT_PATHS = (".python-version", "uv.toml", "skills/uv.toml")


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def seed(root, source=SOURCE):
    write(root, "build/versions.toml", source)
    versions.sync(root)
    return root


def track(root):
    subprocess.run(
        ["git", "init", "-q", str(root)],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "add", "--all"],
        check=True,
        capture_output=True,
        text=True,
    )


def findings(root, historical=None):
    track(root)
    return versions_check.check(root=root, historical=historical)


def snapshot(root):
    return {
        relative: (root / relative).read_bytes()
        for relative in ("build/versions.toml", *OUTPUT_PATHS)
    }


def with_values(root, *, packages=None, date=None):
    path = root / "build/versions.toml"
    text = versions.rewrite(
        path.read_text(encoding="utf-8"),
        packages=packages,
        date=date,
    )
    path.write_text(text, encoding="utf-8")
    versions.sync(root)


def with_markdown(root, text, relative="skills/explore-data/SKILL.md"):
    write(root, relative, text)
    return relative


def skill_and_script(root, *, compatibility="3.11", requires="3.11",
                     dependency="polars>=2.0"):
    write(
        root,
        "skills/explore-data/SKILL.md",
        "---\n"
        "name: explore-data\n"
        "description: Profile a dataset.\n"
        f"compatibility: Python {compatibility}+\n"
        "---\n",
    )
    return write(
        root,
        "skills/explore-data/scripts/profile.py",
        "# /// script\n"
        f'# requires-python = ">={requires}"\n'
        f'# dependencies = ["{dependency}"]\n'
        "# ///\n",
    )


def with_args(argv):
    result = []
    for index, token in enumerate(argv):
        if token == "--with":
            result.append(argv[index + 1])
        elif token.startswith("--with="):
            result.append(token.partition("=")[2])
    return result


def package_name(requirement):
    return re.split(r"[\s\[<>=!~;]", requirement, maxsplit=1)[0].lower().replace("_", "-")


def upload(timestamp):
    return {
        "upload_time_iso_8601": timestamp,
        "upload_time": timestamp.removesuffix("Z"),
        "filename": "package.whl",
        "packagetype": "bdist_wheel",
        "yanked": False,
        "requires_python": None,
    }


def metadata_fetch(name, version, files):
    def fetch(url):
        return {
            "info": {"name": name, "version": version},
            "releases": {version: files},
            "urls": files,
        }
    return fetch


def drift_fetch(url):
    parts = [unquote(part) for part in urlsplit(url).path.split("/") if part]
    assert "pypi" in parts, f"Unexpected metadata request: {url}"
    name = parts[parts.index("pypi") + 1].lower().replace("_", "-")
    current = {**STATE["packages"], **STATE["cited"]}[name]
    newest = "0.12.0.1" if name == "jax" else current
    releases = {current: [upload("2026-10-19T00:00:00Z")]}
    releases[newest] = [
        upload("2026-10-21T00:00:00Z" if name == "jax"
               else "2026-10-19T00:00:00Z")
    ]
    return {
        "info": {"name": name, "version": newest},
        "releases": releases,
        "urls": releases[newest],
    }


@pytest.fixture
def root(tmp_path):
    return seed(tmp_path)


@pytest.fixture
def uv_stub(tmp_path, monkeypatch):
    directory = tmp_path / "bin"
    directory.mkdir()
    log = tmp_path / "uv-calls.jsonl"
    script = directory / "uv"
    script.write_text(
        f"#!{sys.executable}\n"
        + textwrap.dedent(
            """
            import json
            import os
            import pathlib
            import sys

            argv = sys.argv[1:]
            with open(os.environ["VERSIONS_TEST_LOG"], "a", encoding="utf-8") as stream:
                stream.write(json.dumps(argv) + "\\n")

            mode = os.environ.get("VERSIONS_TEST_MODE", "pass")
            compiling = "compile" in argv

            if compiling and mode == "resolve":
                print("No solution found: jax conflicts with numpyro", file=sys.stderr)
                raise SystemExit(1)

            if compiling and mode == "network":
                print("Network failure while resolving jax", file=sys.stderr)
                raise SystemExit(2)

            if not compiling and mode == "gate":
                print("Gate failed", file=sys.stderr)
                raise SystemExit(1)

            if compiling:
                pins = json.loads(os.environ["VERSIONS_TEST_PINS"])
                result = "".join(
                    f"{name}=={version}\\n" for name, version in sorted(pins.items())
                )
                for index, token in enumerate(argv):
                    if token in ("-o", "--output-file"):
                        pathlib.Path(argv[index + 1]).write_text(result, encoding="utf-8")
                    elif token.startswith("--output-file="):
                        pathlib.Path(token.split("=", 1)[1]).write_text(
                            result, encoding="utf-8"
                        )
                print(result, end="")
            """
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", str(directory) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("VERSIONS_TEST_LOG", str(log))
    monkeypatch.setenv("VERSIONS_TEST_PINS", json.dumps(STATE["packages"]))
    monkeypatch.setenv("VERSIONS_TEST_MODE", "pass")
    monkeypatch.setattr(versions, "fetch_json", drift_fetch)
    monkeypatch.setattr(versions, "newest_stable_python", lambda: "3.14")
    return log


def uv_calls(log):
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


# spec: "A missing or invalid file names the key."
# task: 2
def test_missing_required_keys_are_diagnosed():
    for original, key in (
        ("dev = '3.13'\n", "dev"),
        ("date = 2026-10-19\n", "date"),
    ):
        with pytest.raises(versions.VersionsError) as error:
            versions.parse(SOURCE.replace(original, ""))
        assert key in str(error.value).lower()


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
def test_unknown_gate_package_is_diagnosed():
    source = SOURCE.replace(
        "snippets = ['arviz',",
        "snippets = ['pytest', 'arviz',",
    )
    with pytest.raises(versions.VersionsError, match="pytest"):
        versions.parse(source)


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
def test_unknown_override_package_is_diagnosed():
    source = SOURCE + OVERRIDE.replace("package = 'jax'", "package = 'pytest'")
    with pytest.raises(versions.VersionsError, match="pytest"):
        versions.parse(source)


@pytest.mark.parametrize("key", ["gate", "package", "version", "reason"])
# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_each_override_key_is_required(key):
    override = "\n".join(
        line for line in OVERRIDE.splitlines()
        if not line.startswith(f"{key} =")
    )
    with pytest.raises(versions.VersionsError) as error:
        versions.parse(SOURCE + override)
    assert key in str(error.value).lower()


# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_override_is_scoped_to_its_gate():
    value = versions.parse(SOURCE + OVERRIDE)
    assert "jax==0.11.2" in value.stack("jax-cpu")
    assert "jax==0.12.0" in value.stack("snippets")
    assert "jax==0.11.2" not in value.stack("snippets")


# spec: "`build/versions.py` gives the other build scripts these values: the dev Python, the freeze date, and `stack(gate)`, the list of `pkg==version` strings for a gate after overrides."
# task: 2
def test_stack_without_overrides_uses_every_gate_package():
    value = versions.parse(SOURCE)
    assert value.dev_python == "3.13"
    assert value.freeze == dt.date(2026, 10, 19)
    for gate, names in STATE["gates"].items():
        assert sorted(value.stack(gate)) == sorted(
            f"{name}=={STATE['packages'][name]}" for name in names
        )


# spec: "An invalid date names the value."
# task: 3
def test_invalid_date_is_diagnosed():
    invalid = "2026-10-20T00:00:00Z"
    with pytest.raises(versions.VersionsError) as error:
        versions.parse_date(invalid)
    assert invalid in str(error.value)


# spec: "date = 2026-10-19            # a TOML date; every check resolves as of this date"
# task: 2
def test_freeze_requires_a_toml_date():
    with pytest.raises(versions.VersionsError) as error:
        versions.parse(SOURCE.replace(
            "date = 2026-10-19", "date = '2026-10-19'"
        ))
    assert "date" in str(error.value).lower()


# spec: "`.python-version` (repo root)"
# task: 2
def test_python_output_contains_only_the_dev_interpreter():
    output = versions.outputs(versions.parse(SOURCE))[".python-version"]
    assert output.strip() == "3.13"
    assert len(output.splitlines()) == 1


# spec: "Files uploaded on the freeze date itself (UTC) are included."
# task: 2
def test_uv_output_uses_next_day_midnight_utc():
    value = versions.parse(SOURCE)
    assert value.cutoff == CUTOFF
    output = versions.outputs(value)
    assert tomllib.loads(output["uv.toml"])["exclude-newer"] == CUTOFF


# spec: "no settings, and a comment that names `build/versions.toml`"
# task: 2
def test_skills_shadow_has_no_settings_and_names_the_source():
    output = versions.outputs(versions.parse(SOURCE))["skills/uv.toml"]
    assert tomllib.loads(output) == {}
    assert any(
        line.lstrip().startswith("#") and "build/versions.toml" in line
        for line in output.splitlines()
    )


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_writes_exactly_its_generated_outputs(root):
    expected = versions.outputs(versions.load(root))
    assert set(expected) == set(OUTPUT_PATHS)
    for relative, text in expected.items():
        assert (root / relative).read_bytes() == text.encode("utf-8")
    before = snapshot(root)
    assert versions.main(["sync", "--check"], root=root) == 0
    assert snapshot(root) == before


@pytest.mark.parametrize("relative", OUTPUT_PATHS)
# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_check_rejects_each_changed_output_without_repairing_it(root, relative):
    path = root / relative
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    before = snapshot(root)
    assert versions.main(["sync", "--check"], root=root) != 0
    assert snapshot(root) == before
    assert versions.main(["sync"], root=root) == 0
    assert versions.main(["sync", "--check"], root=root) == 0


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_follows_changed_source_values(root):
    path = root / "build/versions.toml"
    path.write_text(
        SOURCE.replace("dev = '3.13'", "dev = '3.12'"),
        encoding="utf-8",
    )
    with_values(root, date=dt.date(2026, 10, 20))
    assert (root / ".python-version").read_text(encoding="utf-8").strip() == "3.12"
    assert tomllib.loads((root / "uv.toml").read_text(encoding="utf-8"))[
        "exclude-newer"
    ] == "2026-10-21T00:00:00Z"


# spec: "With `--only`, the other entries stay at their pins in the joint resolve."
# task: 3
def test_only_unpins_the_selected_packages():
    value = versions.parse(SOURCE)
    requirements = versions.requirements(value, only=("jax",))
    by_name = {package_name(item): item for item in requirements}
    assert set(by_name) == set(STATE["packages"])
    assert "==" not in by_name["jax"]
    for name, version in STATE["packages"].items():
        if name != "jax":
            assert by_name[name] == f"{name}=={version}"


# spec: "Sets the freeze date (default: today, UTC) and does one joint resolve, as of that date and on the dev Python, of every `[packages]` entry together."
# task: 3
def test_bump_resolves_all_packages_together_on_dev_python(root):
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((list(requirements), python_version, cutoff))
        return dict(STATE["packages"])

    versions.bump(root, dt.date(2026, 10, 19), resolver=resolver)
    assert len(calls) == 1
    requirements, python_version, cutoff = calls[0]
    assert {package_name(item) for item in requirements} == set(STATE["packages"])
    assert all("==" not in item for item in requirements)
    assert python_version == "3.13"
    assert cutoff == CUTOFF


# spec: "Sets the freeze date (default: today, UTC) and does one joint resolve, as of that date and on the dev Python, of every `[packages]` entry together."
# task: 3
def test_bump_defaults_to_today_in_utc(root):
    before = dt.datetime.now(dt.timezone.utc).date()

    def resolver(requirements, python_version, cutoff):
        return dict(STATE["packages"])

    versions.bump(root, None, resolver=resolver)
    after = dt.datetime.now(dt.timezone.utc).date()
    assert versions.load(root).freeze in {before, after}


# spec: "It rewrites `[packages]` from the result and runs `sync`."
# task: 3
def test_bump_updates_direct_packages_and_syncs_without_promoting_transitives(root):
    resolved = dict(STATE["packages"], jax="0.12.0.1", scipy="1.0")

    def resolver(requirements, python_version, cutoff):
        return resolved

    versions.bump(root, dt.date(2026, 10, 21), resolver=resolver)
    value = versions.load(root)
    assert value.packages["jax"] == "0.12.0.1"
    assert "scipy" not in value.packages
    assert value.freeze == dt.date(2026, 10, 21)
    assert versions.main(["sync", "--check"], root=root) == 0


# spec: "`bump` never changes `[cited]`."
# task: 3
def test_bump_preserves_every_cited_entry(root):
    before = dict(versions.load(root).cited)
    versions.bump(
        root,
        dt.date(2026, 10, 21),
        resolver=lambda requirements, python_version, cutoff: dict(
            STATE["packages"], jax="0.12.0.1"
        ),
    )
    assert versions.load(root).cited == before


# spec: "Polars is in `[packages]` by the second case: the suites install it, and three headers floor it."
# task: 4
def test_repository_packages_include_polars():
    assert "polars" in versions.load(REPO).packages


# spec: "Other packages (pytest, pyyaml, scipy, tensorstore and the rest) get no entry, and the freeze date fixes them."
# task: 4
def test_repository_does_not_promote_the_named_floating_dependencies():
    value = versions.load(REPO)
    for name in ("pytest", "pyyaml", "scipy", "tensorstore"):
        assert name not in value.packages
        assert name not in value.cited


# spec: "The first is when a `[gates]` list names it."
# task: 4
def test_every_repository_gate_package_has_one_central_pin():
    value = versions.load(REPO)
    for names in value.gates.values():
        assert set(names) <= set(value.packages)
    assert not set(value.packages) & set(value.cited)


# spec: "The file does not hold the script floors (`requires-python`, `compatibility:`) or the 3.9 floor of `install.py` and the read-only agent guard."
# task: 4
def test_central_python_table_contains_only_the_dev_role():
    data = tomllib.loads((REPO / "build/versions.toml").read_text(encoding="utf-8"))
    assert set(data["python"]) == {"dev"}
    assert "requires-python" not in data
    assert "compatibility" not in data


# spec: "Runs `<cmd>` under `uv run` with the gate's stack and the freeze date."
# task: 5
def test_run_argv_uses_the_gate_stack_interpreter_and_cutoff():
    value = versions.parse(SOURCE + OVERRIDE)
    command = ["python", "build/check_jax_examples.py"]
    argv = versions.uv_run_argv(value, "jax-cpu", command)
    assert argv[:2] == ["uv", "run"]
    assert sorted(with_args(argv)) == sorted(value.stack("jax-cpu"))
    assert argv[argv.index("--python") + 1] == value.dev_python
    assert argv[argv.index("--exclude-newer") + 1] == CUTOFF
    assert argv[-len(command):] == command


# spec: "`--pin` changes one package for one run and never edits the file."
# task: 5
def test_temporary_run_pin_does_not_change_other_packages_or_files(root, uv_stub):
    before = snapshot(root)
    value = versions.load(root)
    pins = versions.parse_pins(value, ["jax==0.11.2"])
    argv = versions.uv_run_argv(
        value, "snippets", ["python", "build/check_snippets.py", "--run"], pins=pins
    )
    actual = set(with_args(argv))
    assert "jax==0.11.2" in actual
    assert "jax==0.12.0" not in actual
    assert actual - {"jax==0.11.2"} == set(value.stack("snippets")) - {
        "jax==0.12.0"
    }
    assert snapshot(root) == before


# spec: "A pin uploaded after the freeze date names the package and the date."
# task: 5
def test_run_rejects_a_pin_unavailable_at_the_freeze(root, uv_stub, capfd):
    status = versions.main(
        [
            "run", "snippets", "--pin", "jax==0.12.0.1", "--",
            "python", "build/check_snippets.py", "--run",
        ],
        root=root,
    )
    captured = capfd.readouterr()
    message = captured.out + captured.err
    assert status != 0
    assert "jax" in message.lower()
    assert "2026-10-19" in message or "2026-10-21" in message


@pytest.mark.parametrize(
    ("timestamp", "late"),
    [
        ("2026-10-19T00:00:00Z", False),
        ("2026-10-20T00:00:00Z", True),
    ],
)
# spec: "Files uploaded on the freeze date itself (UTC) are included."
# task: 5
def test_upload_cutoff_includes_the_freeze_day_but_excludes_next_midnight(timestamp, late):
    value = versions.parse(SOURCE)
    spec = "jax==0.12.0"
    result = versions.late_pins(
        value,
        [spec],
        fetch=metadata_fetch("jax", "0.12.0", [upload(timestamp)]),
    )
    assert (spec in result) is late


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 5
def test_run_propagates_a_failed_uv_process(root, uv_stub, monkeypatch):
    monkeypatch.setenv("VERSIONS_TEST_MODE", "gate")
    assert versions.main(
        ["run", "snippets", "--", "python", "build/check_snippets.py", "--run"],
        root=root,
    ) != 0


# spec: "`build/check_snippets.py`: `PINNED` (moved out of `build/snippet_preamble.py`), `RUN_REMEDIATION` and `API_REMEDIATION`."
# task: 6
def test_snippet_pin_ownership_moves_to_the_checker():
    assert not hasattr(snippet_preamble, "PINNED")
    assert hasattr(check_snippets, "PINNED")
    representation = repr(check_snippets.PINNED)
    for spec in versions.load(REPO).stack("snippets"):
        assert spec in representation


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 6
def test_api_remediation_does_not_enter_the_pinned_gate_runner():
    argv = shlex.split(check_snippets.API_REMEDIATION)
    assert "--api" in argv
    assert not any("==" in item for item in with_args(argv))
    assert not (
        "run" in argv and any(item.endswith("build/versions.py") for item in argv)
    )
    value = versions.load(REPO)
    assert "--exclude-newer" in argv
    assert argv[argv.index("--exclude-newer") + 1] == value.cutoff


# spec: "A command that needs a pinned stack uses the runner (R3):"
# task: 6
def test_run_remediation_uses_the_named_snippets_runner():
    argv = shlex.split(check_snippets.RUN_REMEDIATION)
    runner_index = next(
        index for index, token in enumerate(argv)
        if token.endswith("build/versions.py")
    )
    assert argv[runner_index + 1:runner_index + 3] == ["run", "snippets"]
    assert "--run" in argv
    assert not any("==" in token for token in argv)


# spec: "A `with` or `extras` package that `[packages]` names gets its pin."
# task: 7
def test_suite_dependency_specs_take_the_central_pin():
    value = versions.parse(SOURCE)
    pins = run_suites.Pins.from_versions(value)
    assert pins.spec("arviz>=1.0") == "arviz==1.3.0"
    assert pins.spec("polars") == "polars==2.0.0"
    assert pins.spec("pytest") == "pytest"
    assert pins.spec("scipy") == "scipy"


# spec: "`build/run_suites.py`: `DEFAULT_PYTHONS` comes from the dev Python."
# task: 7
def test_suite_default_python_follows_a_changed_dev_value():
    value = versions.parse(SOURCE.replace("dev = '3.13'", "dev = '3.12'"))
    pins = run_suites.Pins.from_versions(value)
    assert pins.python == "3.12"


# spec: "Each run passes `--exclude-newer <date>` explicitly, because suites under `skills/` sit below the shadow file."
# task: 7
def test_all_suite_runs_carry_an_explicit_cutoff():
    value = versions.parse(SOURCE)
    pins = run_suites.Pins.from_versions(value)
    observed = []

    def run_one(*args, **kwargs):
        observed.append(repr((args, kwargs)))
        return 0

    assert run_suites.main(
        ["--all", "--extras"],
        root=REPO,
        run_one=run_one,
        pins=pins,
    ) == 0
    assert observed
    for call in observed:
        assert "--exclude-newer" in call
        assert value.cutoff in call


# spec: "The `hooks` suite keeps its explicit `/usr/bin/python3` run."
# task: 7
def test_all_suites_still_include_system_python():
    observed = []

    def run_one(*args, **kwargs):
        observed.append(repr((args, kwargs)))
        return 0

    assert run_suites.main(
        ["--all", "--extras"],
        root=REPO,
        run_one=run_one,
        pins=run_suites.Pins.from_versions(versions.load(REPO)),
    ) == 0
    assert any("/usr/bin/python3" in call for call in observed)


# spec: "Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`."
# task: 8
def test_verify_steps_cover_the_complete_reverify_set():
    value = versions.parse(SOURCE)
    steps = versions.verify_steps(value)
    assert len(steps) == 4
    commands = [step.argv for step in steps]
    assert sum("--api" in argv for argv in commands) == 1
    assert sum("--run" in argv for argv in commands) == 1
    assert sum(
        any(token.endswith("build/check_jax_examples.py") for token in argv)
        for argv in commands
    ) == 1
    suites = next(
        argv for argv in commands
        if any(token.endswith("build/run_suites.py") for token in argv)
    )
    assert "--all" in suites
    assert "--extras" in suites


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 8
def test_verify_keeps_tier_two_unpinned():
    value = versions.parse(SOURCE)
    step = next(step for step in versions.verify_steps(value) if "--api" in step.argv)
    assert not any("==" in item for item in with_args(step.argv))
    assert "--exclude-newer" in step.argv
    assert step.argv[step.argv.index("--exclude-newer") + 1] == CUTOFF


# spec: "they install `stack('jax-cpu')` in place of `--with-requirements specs/verification/32-jax-cpu.txt`."
# task: 8
def test_verify_jax_examples_use_the_central_stack():
    value = versions.parse(SOURCE + OVERRIDE)
    step = next(
        step for step in versions.verify_steps(value)
        if any(token.endswith("build/check_jax_examples.py") for token in step.argv)
    )
    assert set(with_args(step.argv)) == set(value.stack("jax-cpu"))
    assert "--with-requirements" not in step.argv
    assert not any("32-jax-cpu.txt" in token for token in step.argv)


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
def test_verify_failure_exit_against_stub_uv(root, uv_stub, monkeypatch):
    monkeypatch.setenv("VERSIONS_TEST_MODE", "gate")
    assert versions.main(["verify"], root=root) != 0


# spec: "Does the same joint resolve as `bump`, with no freeze date and no pins, in two passes: first on the dev Python, then on the newest stable Python."
# task: 8
def test_drift_resolves_both_interpreters_without_file_pins_or_freeze(root):
    observed = []

    def resolver(requirements, python_version, cutoff):
        observed.append((list(requirements), python_version, cutoff))
        return dict(STATE["packages"], jax="0.12.0.1")

    code, report = versions.drift(
        root,
        fetch=drift_fetch,
        resolver=resolver,
        newest_python=lambda: "3.14",
        runner=lambda *args, **kwargs: 0,
    )
    assert code == 0
    assert [call[1] for call in observed] == ["3.13", "3.14"]
    for requirements, python_version, cutoff in observed:
        assert cutoff is None
        assert set(STATE["packages"]) <= {
            package_name(item) for item in requirements
        }
        assert all("==" not in item for item in requirements)


# spec: "For each pass it reports, for each `[packages]` and `[cited]` entry, the pinned version, the resolved version, the newest release and its upload date."
# task: 8
def test_drift_report_includes_packages_citations_and_release_metadata(root):
    code, report = versions.drift(
        root,
        fetch=drift_fetch,
        resolver=lambda requirements, python_version, cutoff: {
            **STATE["packages"], **STATE["cited"], "jax": "0.12.0.1"
        },
        newest_python=lambda: "3.14",
        runner=lambda *args, **kwargs: 0,
    )
    assert code == 0
    assert "3.13" in report
    assert "3.14" in report
    for name, pinned in {**STATE["packages"], **STATE["cited"]}.items():
        assert name in report.lower()
        assert pinned in report
    assert "0.12.0.1" in report
    assert "2026-10-21" in report


# spec: "It then runs the re-verify set on each pass's versions and reports each gate's result for each pass."
# task: 8
def test_drift_reverifies_both_resolved_stacks(root):
    observed = []

    def runner(argv, *args, **kwargs):
        observed.append(list(argv))
        return 0

    code, report = versions.drift(
        root,
        fetch=drift_fetch,
        resolver=lambda requirements, python_version, cutoff: dict(
            STATE["packages"], jax="0.12.0.1"
        ),
        newest_python=lambda: "3.14",
        runner=runner,
    )
    assert code == 0
    assert len(observed) == 8
    for python_version in ("3.13", "3.14"):
        commands = [
            argv for argv in observed
            if python_version in argv
        ]
        assert len(commands) == 4
        assert any("--api" in argv for argv in commands)
        assert any("--run" in argv for argv in commands)
        assert any(
            any(token.endswith("build/check_jax_examples.py") for token in argv)
            for argv in commands
        )
        assert any(
            any(token.endswith("build/run_suites.py") for token in argv)
            for argv in commands
        )
        for argv in commands:
            assert "--exclude-newer" not in argv
        for argv in commands:
            if "--run" in argv:
                assert "jax==0.12.0.1" in with_args(argv)


@pytest.mark.parametrize(("mode", "expected"), [("pass", 0), ("gate", 1)])
# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_gate_exit_codes_against_stub_uv(root, uv_stub, monkeypatch, mode, expected):
    monkeypatch.setenv("VERSIONS_TEST_MODE", mode)
    monkeypatch.setenv(
        "VERSIONS_TEST_PINS",
        json.dumps(dict(STATE["packages"], jax="0.12.0.1")),
    )
    assert versions.main(["drift"], root=root) == expected


@pytest.mark.parametrize("mode", ["resolve", "network"])
# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_infrastructure_exit_codes_against_stub_uv(root, uv_stub, monkeypatch, mode):
    monkeypatch.setenv("VERSIONS_TEST_MODE", mode)
    assert versions.main(["drift"], root=root) == 2


@pytest.mark.parametrize("mode", ["resolve", "network"])
# spec: "`bump` exits 2 on a network or resolve failure and names the step."
# task: 3
def test_bump_failure_exit_and_step_against_stub_uv(
    root, uv_stub, monkeypatch, capfd, mode
):
    monkeypatch.setenv("VERSIONS_TEST_MODE", mode)
    assert versions.main(["bump", "--date", "2026-10-19"], root=root) == 2
    captured = capfd.readouterr()
    report = (captured.out + captured.err).lower()
    assert "resolve" in report or "resolving" in report
    if mode == "network":
        assert "network" in report


# spec: "A joint resolve that fails in `bump` or `drift` names the packages in conflict."
# task: 8
def test_joint_conflicts_name_both_packages(root, uv_stub, monkeypatch, capfd):
    monkeypatch.setenv("VERSIONS_TEST_MODE", "resolve")
    for command in (["bump", "--date", "2026-10-19"], ["drift"]):
        assert versions.main(command, root=root) == 2
        captured = capfd.readouterr()
        report = (captured.out + captured.err).lower()
        assert "jax" in report
        assert "numpyro" in report


# spec: "Does the same joint resolve as `bump`, with no freeze date and no pins, in two passes: first on the dev Python, then on the newest stable Python."
# task: 3
def test_unfrozen_resolve_does_not_inherit_repository_configuration(root, uv_stub, monkeypatch):
    monkeypatch.chdir(root)
    versions.resolve(list(STATE["packages"]), "3.13", None)
    compile_calls = [argv for argv in uv_calls(uv_stub) if "compile" in argv]
    assert len(compile_calls) == 1
    assert "--no-config" in compile_calls[0]
    assert "--exclude-newer" not in compile_calls[0]


# spec: "`--pin` changes one package for one run and never edits the file."
# task: 8
def test_verify_and_drift_with_temporary_pins_preserve_all_version_files(
    root, uv_stub, monkeypatch
):
    before = snapshot(root)
    assert versions.main(
        ["verify", "--pin", "jax==0.11.2"], root=root
    ) == 0
    assert snapshot(root) == before
    monkeypatch.setenv(
        "VERSIONS_TEST_PINS",
        json.dumps(dict(STATE["packages"], jax="0.11.2")),
    )
    assert versions.main(
        ["drift", "--pin", "jax==0.11.2"], root=root
    ) == 0
    assert snapshot(root) == before


# spec: "`versions.py check` runs offline."
# task: 9
def test_check_does_not_fetch_or_start_uv(root, uv_stub, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Offline check attempted a network operation")

    monkeypatch.setattr(versions, "fetch_json", forbidden)
    assert versions.main(["check"], root=root) == 0
    assert uv_calls(uv_stub) == []


@pytest.mark.parametrize("relative", OUTPUT_PATHS)
# spec: "**Sync.** An R2.1 output differs from the file."
# task: 9
def test_check_finds_each_stale_generated_output(root, relative):
    assert findings(root) == []
    path = root / relative
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    result = findings(root)
    assert result
    assert any(relative in message for message in result)


@pytest.mark.parametrize(
    "relative",
    [
        "CLAUDE.md",
        "AGENTS.md",
        "GEMINI.md",
        "build/run_commit_lints.sh",
        "hooks/README.md",
        "skills/explore-data/SKILL.md",
        ".claude/skills/cc-guide/SKILL.md",
    ],
)
# spec: "A live file spells `--python 3.<n>`."
# task: 9
def test_interpreter_literals_fail_in_every_live_location(root, relative):
    write(root, relative, "uv run python build/versions.py check\n")
    assert findings(root) == []
    write(root, relative, "uv run --python 3.13 python build/versions.py check\n")
    result = findings(root)
    assert result
    assert any(relative in message for message in result)


# spec: "An interpreter path such as `/usr/bin/python3` is not a literal."
# task: 9
def test_system_python_path_is_allowed(root):
    write(root, "hooks/README.md", "uv run --python /usr/bin/python3 python\n")
    assert findings(root) == []


@pytest.mark.parametrize(
    ("good", "stale"),
    [
        ("verified on Polars 2.0", "verified on Polars 1.42"),
        ("numpyro==0.22.0", "numpyro==0.21.0"),
        (
            "NumPyro checked in the 0.22.0 source",
            "NumPyro checked in the 0.21.0 source",
        ),
        ("verified on arviz-stats 1.3", "verified on arviz-stats 1.3.1"),
        ("verified on Altair 6.2", "verified on Altair 6.3.0"),
        ("verified on plotly 6.8", "verified on plotly 7.1.0"),
        ("Python 3.13", "Python 3.12"),
    ],
)
# spec: "**Equality** ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision."
# task: 9
def test_equality_has_a_matching_control_and_a_seeded_stale_control(root, good, stale):
    relative = with_markdown(root, good + "\n")
    assert findings(root) == []
    with_markdown(root, stale + "\n")
    result = findings(root)
    assert result
    assert any(relative in message for message in result)


# spec: "**Equality** ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision."
# task: 9
def test_each_package_in_a_shared_citation_is_checked(root):
    relative = with_markdown(
        root, "verified on arviz 1.3.0 / arviz-stats 1.3.3\n"
    )
    assert findings(root) == []
    with_markdown(root, "verified on arviz 1.3.0 / arviz-stats 1.3.1\n")
    result = findings(root)
    assert any(relative in message and "arviz-stats" in message.lower()
               for message in result)


@pytest.mark.parametrize(
    ("text", "changed_packages"),
    [
        ("polars>=2.0", {"polars": "1.42"}),
        ("NumPyro ≥ 0.22", {"numpyro": "0.21.0"}),
        ("arviz-stats >= 1.0.0", {"arviz-stats": "0.23"}),
        ("great-docs>=0.17.0,<0.18", {"great-docs": "0.18"}),
    ],
)
# spec: "**Range** (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file's value."
# task: 9
def test_ranges_have_containing_and_noncontaining_controls(root, text, changed_packages):
    relative = with_markdown(root, text + "\n")
    assert findings(root) == []
    path = root / "build/versions.toml"
    changed = path.read_text(encoding="utf-8")
    for name, version in changed_packages.items():
        old = {**STATE["packages"], **STATE["cited"]}[name]
        changed = changed.replace(f"{name} = '{old}'", f"{name} = '{version}'")
    path.write_text(changed, encoding="utf-8")
    versions.sync(root)
    result = findings(root)
    assert result
    assert any(relative in message for message in result)


# spec: "**Range** (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file's value."
# task: 9
def test_python_plus_range_is_not_equality(root):
    with_markdown(root, "Python 3.11+\nPython 3.12+\n")
    assert findings(root) == []
    path = root / "build/versions.toml"
    path.write_text(
        SOURCE.replace("dev = '3.13'", "dev = '3.11'"), encoding="utf-8"
    )
    versions.sync(root)
    assert findings(root)


# spec: "**History** ("ArviZ 0.23", "and earlier") passes only through the `HISTORICAL` allowlist."
# task: 9
def test_history_requires_an_allowlisted_phrase(root):
    phrase = "ArviZ 0.23"
    with_markdown(root, phrase + "\n")
    assert findings(root, historical={})
    assert findings(
        root, historical={phrase: "The classic stack is described as history."}
    ) == []


# spec: "`HISTORICAL` is keyed by the literal phrase, not by file and line, and each entry gives its reason."
# task: 9
def test_historical_permission_follows_the_phrase_when_it_moves(root):
    phrase = "ArviZ 0.23"
    allowed = {phrase: "The classic stack is described as history."}
    with_markdown(root, phrase + "\n")
    with_markdown(
        root,
        "\n\n" + phrase + "\n",
        "skills/bayesian-workflow/references/diagnostics.md",
    )
    assert findings(root, historical=allowed) == []


# spec: "`HISTORICAL` is keyed by the literal phrase, not by file and line, and each entry gives its reason."
# task: 9
def test_repository_historical_entries_have_reasons():
    assert isinstance(versions_check.HISTORICAL, dict)
    for phrase, reason in versions_check.HISTORICAL.items():
        assert isinstance(phrase, str) and phrase.strip()
        assert isinstance(reason, str) and reason.strip()


# spec: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
def test_floor_mismatch_has_a_matching_control(root):
    skill_and_script(root, compatibility="3.11", requires="3.11")
    assert findings(root) == []
    skill_and_script(root, compatibility="3.11", requires="3.12")
    result = findings(root)
    assert result
    assert any(
        "skills/explore-data" in message and
        ("floor" in message.lower() or "requires-python" in message.lower())
        for message in result
    )


# spec: "The dev Python must satisfy each floor."
# task: 9
def test_dev_python_below_a_user_floor_fails(root):
    skill_and_script(root, compatibility="3.12", requires="3.12")
    assert findings(root) == []
    path = root / "build/versions.toml"
    path.write_text(
        SOURCE.replace("dev = '3.13'", "dev = '3.11'"), encoding="utf-8"
    )
    versions.sync(root)
    assert findings(root)


# spec: "In `skills/**/*.md` and the script headers under `skills/*/scripts/`, `check` finds each version that stands next to a `[packages]` name, a `[cited]` name or "Python", and classifies it by form:"
# task: 9
def test_script_header_dependency_ranges_are_checked(root):
    skill_and_script(root, dependency="polars>=2.0")
    assert findings(root) == []
    skill_and_script(root, dependency="polars<2.0")
    result = findings(root)
    assert result
    assert any("scripts/profile.py" in message for message in result)


@pytest.mark.parametrize(
    "relative",
    [
        "specs/deferred_items.md",
        "specs/plans/completed/record.md",
        "specs/completed/record.md",
        "specs/verification/record.md",
        "LICENSE",
        "skills/explore-data/LICENSE.md",
        "skills/explore-data/data/record.md",
        "skills/explore-data/tests/fixtures/record.md",
    ],
)
# spec: "`check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures."
# task: 9
def test_excluded_material_does_not_create_findings(root, relative):
    with_markdown(root, "verified on Polars 2.0\n")
    write(
        root,
        relative,
        "verified on Polars 1.42\nuv run --python 3.13 python\n",
    )
    assert findings(root) == []
    with_markdown(root, "verified on Polars 1.42\n")
    assert findings(root)


# spec: "Known limit: `check` sees only the package names that the file lists."
# task: 9
def test_unlisted_package_version_is_outside_the_citation_lint(root):
    with_markdown(root, "scipy>=1.0\n")
    assert findings(root) == []


# spec: "The `drift` report states this limit."
# task: 8
def test_drift_report_includes_its_declared_coverage_limit(root):
    code, report = versions.drift(
        root,
        fetch=drift_fetch,
        resolver=lambda requirements, python_version, cutoff: dict(
            STATE["packages"], jax="0.12.0.1"
        ),
        newest_python=lambda: "3.14",
        runner=lambda *args, **kwargs: 0,
    )
    assert code == 0
    assert versions.DRIFT_LIMIT.strip()
    assert versions.DRIFT_LIMIT in report


# spec: "Use one JAX version for both gates."
# task: 10
def test_repository_jax_stacks_share_a_pin_or_have_a_reasoned_override():
    value = versions.load(REPO)
    snippet_jax = next(
        item for item in value.stack("snippets") if item.startswith("jax==")
    )
    cpu_jax = next(
        item for item in value.stack("jax-cpu") if item.startswith("jax==")
    )
    if snippet_jax != cpu_jax:
        overrides = [
            item for item in value.overrides
            if item.gate == "jax-cpu" and item.package == "jax"
        ]
        assert len(overrides) == 1
        assert overrides[0].reason.strip()
        deferred = (REPO / "specs/deferred_items.md").read_text(encoding="utf-8")
        assert "jax-cpu" in deferred


# spec: "This keeps the `polars>=2.0` floors that the portability plan set on purpose (`specs/plans/completed/53-agent-skills-portability.md`, decision DF4)."
# task: 10
def test_repository_polars_pin_still_satisfies_the_portability_floor():
    assert versions.compare(versions.load(REPO).packages["polars"], "2.0") >= 0


# spec: "Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says "on the pinned 0.21.0"."
# task: 12
def test_stale_gaussian_process_pin_claim_is_removed():
    text = (REPO / "specs/deferred_items.md").read_text(encoding="utf-8")
    assert "on the pinned 0.21.0" not in text


# spec: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`."
# task: 12
def test_old_cpu_lock_paths_are_retired():
    assert not (REPO / "specs/verification/32-jax-cpu.in").exists()
    assert not (REPO / "specs/verification/32-jax-cpu.txt").exists()
    for relative in ("CLAUDE.md", "build/check_jax_examples.py"):
        text = (REPO / relative).read_text(encoding="utf-8")
        assert "specs/verification/32-jax-cpu.in" not in text
        assert "specs/verification/32-jax-cpu.txt" not in text


# spec: "Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python."
# task: 12
def test_clean_code_rule_names_the_central_interpreter_source():
    text = (REPO / "rules/clean-code-python.md").read_text(encoding="utf-8")
    assert "build/versions.toml" in text
    assert "agent-skills: 3.13" not in text


# spec: "`versions.py check` runs offline."
# task: 13
def test_completed_repository_passes_the_offline_acceptance_lint():
    assert versions_check.check(root=REPO) == []


# spec: "`versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`."
# task: 14
def test_commit_lint_runner_wires_versions_check():
    text = (REPO / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    assert "versions_check" in text
    assert re.search(r"uv\s+run\s+python\s+build/versions\.py\s+check", text)


# spec: "`setup-uv` takes the interpreter from `.python-version`."
# task: 14
def test_lint_workflow_references_the_generated_interpreter_file():
    text = (REPO / ".github/workflows/lints.yml").read_text(encoding="utf-8")
    assert "setup-uv" in text
    assert ".python-version" in text
    assert not re.search(
        r"python-version\s*:\s*['\"]?3\.\d+(?:\.\d+)?['\"]?\s*$",
        text,
        re.MULTILINE,
    )


# spec: "A new workflow, `.github/workflows/versions-drift.yml`, runs `versions.py drift` weekly on a cron schedule and on manual dispatch."
# task: 15
def test_drift_workflow_has_manual_and_weekly_triggers():
    text = (REPO / ".github/workflows/versions-drift.yml").read_text(encoding="utf-8")
    assert re.search(r"\bworkflow_dispatch\s*:", text)
    assert re.search(r"\bschedule\s*:", text)
    expressions = re.findall(r"\bcron:\s*['\"]([^'\"]+)['\"]", text)
    assert expressions
    weekdays = r"(?:[0-7]|SUN|MON|TUE|WED|THU|FRI|SAT)"
    assert any(
        re.fullmatch(rf"\d+\s+\d+\s+\*\s+\*\s+{weekdays}", expression, re.I)
        for expression in expressions
    )
    assert re.search(r"build/versions\.py\s+drift\b", text)


# spec: "It has `permissions: contents: read`, and it pins its actions by SHA, as `lints.yml` does."
# task: 15
def test_drift_workflow_permissions_and_action_pins():
    text = (REPO / ".github/workflows/versions-drift.yml").read_text(encoding="utf-8")
    assert re.search(r"\bcontents\s*:\s*read\b", text)
    assert not re.search(r"\b(?:contents|issues|pull-requests)\s*:\s*write\b", text)
    uses = re.findall(r"\buses:\s*['\"]?([^'\"\s#]+)", text)
    assert uses
    for action in uses:
        if not action.startswith("./"):
            assert re.fullmatch(r"[^@\s]+@[0-9a-fA-F]{40}", action)


# spec: "It writes the drift report to the job summary."
# task: 15
def test_drift_workflow_writes_a_job_summary():
    text = (REPO / ".github/workflows/versions-drift.yml").read_text(encoding="utf-8")
    assert "GITHUB_STEP_SUMMARY" in text
    assert re.search(r"build/versions\.py\s+drift\b", text)


# spec: "It never opens an issue or a PR, and it never commits."
# task: 15
def test_drift_workflow_has_no_direct_publish_commands():
    text = (REPO / ".github/workflows/versions-drift.yml").read_text(encoding="utf-8")
    assert not re.search(r"\bgh\s+(?:issue|pr)\s+create\b", text)
    assert not re.search(r"\bgit\s+(?:commit|push)\b", text)
</tests>
<flags>
<flag task="5"><spec>uv compares the date with the upload time of each file, not of the release.</spec><plan>`late_pins(v, specs, fetch=None) -> list[str]` (the specs whose release was first uploaded at or after the cutoff)</plan></flag>
<flag task="6"><spec>Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date.</spec><plan>`check_snippets.API_REMEDIATION` and `RUN_REMEDIATION` as runner commands.</plan></flag>
</flags>
<untestable>
The repo fixes package versions by hand in many places, and nothing ties the copies together.
On 2026-10-21 the owner found NumPyro at 0.21.0 in one deferred item and at 0.22.0 in `PINNED`.
This work is not part of plan 64 (bayesian-workflow and recommend-probabilistic-model routing).
They change for different reasons, so the design keeps them apart.
A floor states when an API appeared.
A new upstream release does not make it stale.
They keep the versions of their day.
A floating gate would have changed today: jax 0.12.0.1 was uploaded on 2026-10-21.
The plan must re-check items 2 to 6 before it relies on them.
So after the change merges, a worktree on a branch that lacks those files inherits the main checkout's freeze date and interpreter, with no sign of it.
`build/versions.toml` is the only file in which a person sets a package version or the dev interpreter.
The values above are the 2026-10-21 state.
The plan sets the real values with `bump` (R3).
The second is when a check installs it and skill text or a script header states a version for it.
A package gets a `[cited]` entry when skill prose cites a version for it and no check runs it.
Every `uv run` in the repo uses the dev interpreter with no `--python` flag, from any subdirectory
Every `uv run` from the repo root resolves as of the freeze date, script headers included.
CI and a local machine resolve alike, because uv reads a bare date in local time (Inventory, uv item 7)
It shadows the root date under `skills/`, so a skill script that a user runs floats within its floors (D8), whatever the path form
`skills/uv.toml` is a file, not a skill.
`install.py:97-101`, `build/check_frontmatter.py:574-575` and `build/check_provenance.py:40-44` read only directories that hold a `SKILL.md`, so they skip it.
The plan confirms that Claude Code, Codex and Gemini also ignore a plain file in a skills directory.
These readers take their versions from R2.2 and from no literal:
`build/cc_guide/notice.sh:114` and `build/githooks/pre-commit:15`: they can run outside the repo's working directory, so they take the interpreter from the file and not from a literal.
Documented commands spell no interpreter or package version.
This covers `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `build/run_commit_lints.sh`, the usage docstrings in `build/`, `hooks/` and the skill test files, and the commands in skill text.
It flags each package that resolves below its newest release.
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
Pin Polars at the latest release (2.0.0 on 2026-10-21).
For each stale citation, either re-verify the cited behavior on the file's version and update the citation, or move it to `HISTORICAL` with the reason "verified on X, not re-checked on Y" and log a deferred item to re-check it.
Never change a citation's version without a re-check.
The known stale citations are the Polars, Altair and plotly lines, `skills/bayesian-workflow/references/model-comparison.md:130`, `references/model-criticism.md:196` and `skills/deep-learning/references/frameworks.md:94-95`.
The plan-32 verification records keep their old versions as history.
The plan writes each test before its code (red, then green).
**`versions.py` units.** Cover schema validation, `stack()` with and without an override, and the exact text that `sync` writes.
**`run_suites.py` tests.** `build/test_run_suites.py` and `build/test_check_frontmatter.py:434` build their expected commands from the file, not from a `3.13` literal.
No third-party text enters the repo, so `NOTICE` and the license files do not change.
The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.
This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
The R6 prose fixes rebase onto them and re-take the line numbers.
R2.4 removes the version flags from the commands, so `CLAUDE.md` gets shorter.
</untestable>