<tests>
import datetime as dt
import importlib
import os
from pathlib import Path
import re
import sys
import textwrap
import tomllib

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))

SAMPLE = """\
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


@pytest.fixture
def versions():
    return importlib.import_module("versions")


@pytest.fixture
def versions_check():
    return importlib.import_module("versions_check")


def sample_repo(root, versions):
    (root / "build").mkdir(parents=True)
    (root / "skills").mkdir()
    (root / "build/versions.toml").write_text(SAMPLE)
    versions.sync(root)
    return root


def seed_skill(root, body="Verified on Polars 2.0.0.", floor="3.11"):
    skill = root / "skills/explore-data/SKILL.md"
    script = root / "skills/explore-data/scripts/profile.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text(
        "---\n"
        "name: explore-data\n"
        "description: Dataset profiling.\n"
        f"compatibility: Python {floor}+\n"
        "---\n"
        f"{body}\n"
    )
    script.write_text(
        "# /// script\n"
        f'# requires-python = ">={floor}"\n'
        '# dependencies = ["polars>=2.0"]\n'
        "# ///\n"
    )
    return skill, script


def stub_uv(root, monkeypatch, compile_rc=0, run_rc=0):
    executable = root / "uv"
    executable.write_text(
        textwrap.dedent(
            r"""#!/usr/bin/env python3
import os
from pathlib import Path
import sys

with Path(os.environ["UV_STUB_LOG"]).open("a") as log:
    log.write(" ".join(sys.argv[1:]) + "\n")

if "compile" in sys.argv:
    if int(os.environ["UV_STUB_COMPILE_RC"]):
        print("joint resolve failed", file=sys.stderr)
        sys.exit(1)
    result = "jax==0.12.0\nnumpyro==0.22.0\nnumpy==2.5.3\n"
    for option in ("-o", "--output-file"):
        if option in sys.argv:
            Path(sys.argv[sys.argv.index(option) + 1]).write_text(result)
    print(result, end="")
    sys.exit(0)

sys.exit(int(os.environ["UV_STUB_RUN_RC"]))
"""
        )
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", f"{root}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("UV_STUB_LOG", str(root / "uv.log"))
    monkeypatch.setenv("UV_STUB_COMPILE_RC", str(compile_rc))
    monkeypatch.setenv("UV_STUB_RUN_RC", str(run_rc))


# spec: "Record the results in `specs/verification/`."
# task: 1
def test_uv_reprobe_has_a_record_and_executable_probe():
    probe = ROOT / "specs/verification/66-uv-probe.py"
    record = ROOT / "specs/verification/66-uv-probe.md"
    assert probe.is_file()
    assert record.is_file()
    text = record.read_text().lower()
    for subject in ("script", "symlink", "uv.toml", ".python-version", "worktree"):
        assert subject in text


# spec: "A missing or invalid file names the key."
# task: 2
def test_schema_errors_name_the_missing_key(versions):
    with pytest.raises(versions.VersionsError, match="python"):
        versions.parse(SAMPLE.replace("[python]\ndev = '3.13'\n\n", ""))


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
def test_unknown_gate_and_override_packages_are_rejected(versions):
    bad_gate = SAMPLE.replace(
        "jax-cpu = ['jax', 'jaxlib'",
        "jax-cpu = ['pytest', 'jaxlib'",
    )
    with pytest.raises(versions.VersionsError, match="pytest"):
        versions.parse(bad_gate)

    bad_override = SAMPLE + (
        "\n[[override]]\n"
        "gate = 'jax-cpu'\n"
        "package = 'plotly'\n"
        "version = '6.8'\n"
        "reason = 'The JAX CPU examples must pass on it.'\n"
    )
    with pytest.raises(versions.VersionsError, match="plotly"):
        versions.parse(bad_override)


# spec: "An invalid date names the value."
# task: 2
def test_invalid_freeze_date_names_its_value(versions):
    bad = SAMPLE.replace("date = 2026-10-19", "date = 'not-a-date'")
    with pytest.raises(versions.VersionsError, match="not-a-date"):
        versions.parse(bad)


# spec: "Polars is in `[packages]` by the second case: the suites install it, and three headers floor it."
# task: 4
def test_real_versions_file_includes_polars(versions):
    data = tomllib.loads((ROOT / "build/versions.toml").read_text())
    assert "polars" in data["packages"]
    assert versions.version_tuple(data["packages"]["polars"]) >= (2, 0)


# spec: "Other packages (pytest, pyyaml, scipy, tensorstore and the rest) get no entry, and the freeze date fixes them."
# task: 4
def test_floating_packages_have_no_exact_entry():
    data = tomllib.loads((ROOT / "build/versions.toml").read_text())
    assert {"pytest", "pyyaml", "scipy", "tensorstore"}.isdisjoint(
        data["packages"]
    )
    assert isinstance(data["freeze"]["date"], dt.date)


# spec: "A package gets a `[cited]` entry when skill prose cites a version for it and no check runs it."
# task: 4
def test_cited_packages_are_separate_from_gate_packages():
    data = tomllib.loads((ROOT / "build/versions.toml").read_text())
    gate_names = {name for gate in data["gates"].values() for name in gate}
    assert gate_names <= data["packages"].keys()
    assert gate_names.isdisjoint(data["cited"])
    assert {"altair", "plotly", "optuna", "great-docs"} <= data["cited"].keys()


# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_stack_uses_one_pin_except_for_a_named_override(versions):
    base = versions.parse(SAMPLE)
    assert base.stack("snippets").count("jax==0.12.0") == 1
    assert "jax==0.12.0" in base.stack("jax-cpu")

    overridden = versions.parse(
        SAMPLE
        + "\n[[override]]\n"
        "gate = 'jax-cpu'\n"
        "package = 'jax'\n"
        "version = '0.11.2'\n"
        "reason = 'The JAX CPU examples must pass on it.'\n"
    )
    assert "jax==0.11.2" in overridden.stack("jax-cpu")
    assert "jax==0.12.0" in overridden.stack("snippets")

    with pytest.raises(versions.VersionsError, match="reason"):
        versions.parse(
            SAMPLE
            + "\n[[override]]\n"
            "gate = 'jax-cpu'\n"
            "package = 'jax'\n"
            "version = '0.11.2'\n"
        )


# spec: "The file does not hold the script floors (`requires-python`, `compatibility:`) or the 3.9 floor of `install.py` and the read-only agent guard."
# task: 4
def test_versions_file_contains_only_the_defined_roles():
    data = tomllib.loads((ROOT / "build/versions.toml").read_text())
    assert set(data) <= {
        "python", "freeze", "packages", "cited", "gates", "override"
    }
    assert "requires-python" not in data["python"]
    assert "compatibility" not in data["python"]


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_writes_exactly_its_declared_outputs(tmp_path, versions):
    sample_repo(tmp_path, versions)
    expected = versions.outputs(versions.load(tmp_path))
    assert set(expected) == {".python-version", "uv.toml", "skills/uv.toml"}
    for relative, content in expected.items():
        assert (tmp_path / relative).read_text() == content
    assert (tmp_path / ".python-version").read_text().strip() == "3.13"
    assert tomllib.loads((tmp_path / "uv.toml").read_text())[
        "exclude-newer"
    ] == "2026-10-20T00:00:00Z"
    shadow = (tmp_path / "skills/uv.toml").read_text()
    assert tomllib.loads(shadow) == {}
    assert "build/versions.toml" in shadow


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_check_detects_each_divergent_output(tmp_path, versions):
    sample_repo(tmp_path, versions)
    for relative in (".python-version", "uv.toml", "skills/uv.toml"):
        target = tmp_path / relative
        original = target.read_text()
        target.write_text(original + "\n# stale\n")
        assert versions.main(["sync", "--check"], root=tmp_path) != 0
        target.write_text(original)
    assert versions.main(["sync", "--check"], root=tmp_path) == 0


# spec: "With `cutoff=None` it runs `uv --no-config` so the repo's `uv.toml` does not apply)."
# task: 3
def test_unfrozen_joint_resolve_ignores_repo_uv_configuration(
    tmp_path, monkeypatch, versions
):
    stub_uv(tmp_path, monkeypatch)
    resolved = versions.resolve(
        ["jax==0.12.0", "numpyro==0.22.0"], "3.13", None
    )
    assert resolved["jax"] == "0.12.0"
    assert resolved["numpyro"] == "0.22.0"
    assert resolved["numpy"] == "2.5.3"
    assert "--no-config" in (tmp_path / "uv.log").read_text()


# spec: "With `--only`, the other entries stay at their pins in the joint resolve."
# task: 3
def test_bump_only_resolves_jointly_and_preserves_other_pins_and_citations(
    tmp_path, versions
):
    sample_repo(tmp_path, versions)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((requirements, python_version, cutoff))
        result = dict(versions.load(tmp_path).packages)
        result["jax"] = "0.12.0.1"
        return result

    before = tomllib.loads((tmp_path / "build/versions.toml").read_text())
    versions.bump(
        tmp_path, dt.date(2026, 10, 21), only=("jax",), resolver=resolver
    )
    after = tomllib.loads((tmp_path / "build/versions.toml").read_text())

    assert len(calls) == 1
    requirements, python_version, cutoff = calls[0]
    assert python_version == "3.13"
    assert cutoff == "2026-10-22T00:00:00Z"
    assert not any(item.startswith("jax==") for item in requirements)
    assert "numpyro==0.22.0" in requirements
    assert after["packages"]["jax"] == "0.12.0.1"
    assert after["packages"]["numpyro"] == before["packages"]["numpyro"]
    assert after["cited"] == before["cited"]
    assert after["freeze"]["date"] == dt.date(2026, 10, 21)
    assert versions.main(["sync", "--check"], root=tmp_path) == 0


# spec: "Runs `<cmd>` under `uv run` with the gate's stack and the freeze date"
# task: 5
def test_run_argv_uses_the_gate_stack_and_freeze(versions):
    v = versions.parse(SAMPLE)
    argv = versions.uv_run_argv(
        v, "snippets", ["python", "build/check_snippets.py", "--run"]
    )
    text = " ".join(argv)
    assert argv[:2] == ["uv", "run"]
    assert "arviz==1.3.0" in text
    assert "numpyro==0.22.0" in text
    assert "jax==0.12.0" in text
    assert "2026-10-20T00:00:00Z" in text
    assert argv[-3:] == ["python", "build/check_snippets.py", "--run"]


# spec: "`--pin` changes one package for one run and never edits the file."
# task: 5
def test_pin_changes_only_the_invocation(tmp_path, monkeypatch, versions):
    sample_repo(tmp_path, versions)
    original = (tmp_path / "build/versions.toml").read_bytes()
    monkeypatch.setattr(versions, "late_pins", lambda *args, **kwargs: [])
    observed = []

    def runner(argv, root, env):
        observed.append(argv)
        return 0

    monkeypatch.setattr(versions, "run_process", runner)
    assert versions.main(
        [
            "run", "snippets", "--pin", "jax==0.11.2",
            "--", "python", "build/check_snippets.py",
        ],
        root=tmp_path,
    ) == 0
    assert "jax==0.11.2" in " ".join(observed[0])
    assert "jax==0.12.0" not in " ".join(observed[0])
    assert (tmp_path / "build/versions.toml").read_bytes() == original


# spec: "A pin uploaded after the freeze date names the package and the date."
# task: 5
def test_late_pin_is_detected_at_the_utc_cutoff(versions):
    v = versions.parse(SAMPLE)

    def fetch(_url):
        release = {
            "upload_time": "2026-10-21T00:00:00",
            "upload_time_iso_8601": "2026-10-21T00:00:00Z",
        }
        return {
            "urls": [release],
            "releases": {"0.12.0.1": [release]},
        }

    assert versions.late_pins(
        v, ["jax==0.12.0.1"], fetch=fetch
    ) == ["jax==0.12.0.1"]


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 6
def test_snippet_api_remediation_does_not_pin_named_packages():
    snippets = importlib.import_module("check_snippets")
    preamble = importlib.import_module("snippet_preamble")
    assert not hasattr(preamble, "PINNED")
    assert "--api" in snippets.API_REMEDIATION
    assert "==" not in snippets.API_REMEDIATION
    assert "build/versions.py run" in snippets.RUN_REMEDIATION


# spec: "A `with` or `extras` package that `[packages]` names gets its pin."
# task: 7
def test_suite_pins_come_from_versions_file(versions):
    run_suites = importlib.import_module("run_suites")
    v = versions.parse(SAMPLE)
    pins = run_suites.Pins.from_versions(v)
    assert pins.python == "3.13"
    assert pins.cutoff == "2026-10-20T00:00:00Z"
    assert pins.spec("jax") == "jax==0.12.0"
    assert pins.spec("pytest") == "pytest"


# spec: "The `hooks` suite keeps its explicit `/usr/bin/python3` run."
# task: 7
def test_hooks_suite_retains_system_python():
    text = (ROOT / "build/suites.toml").read_text()
    assert "/usr/bin/python3" in text
    assert "dev" in text


# spec: "Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`"
# task: 8
def test_verify_has_all_four_required_steps(versions):
    steps = versions.verify_steps(versions.parse(SAMPLE))
    assert [step.label for step in steps] == [
        "tier 2 (--api)",
        "tier 3 (--run)",
        "jax cpu examples",
        "suites",
    ]
    commands = [" ".join(step.argv) for step in steps]
    assert "--api" in commands[0]
    assert "==" not in commands[0]
    assert "jax==0.12.0" in commands[1]
    assert "jax==0.12.0" in commands[2]
    assert "run_suites.py" in commands[3]
    assert "--all" in commands[3]
    assert "--extras" in commands[3]


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
def test_verify_returns_failure_from_stub_uv(
    tmp_path, monkeypatch, versions
):
    sample_repo(tmp_path, versions)
    stub_uv(tmp_path, monkeypatch, run_rc=1)
    assert versions.main(["verify"], root=tmp_path) != 0


# spec: "`bump` exits 2 on a network or resolve failure and names the step."
# task: 3
def test_bump_resolve_failure_has_exit_code_two(
    tmp_path, monkeypatch, capsys, versions
):
    sample_repo(tmp_path, versions)
    stub_uv(tmp_path, monkeypatch, compile_rc=1)
    assert versions.main(
        ["bump", "--date", "2026-10-21"], root=tmp_path
    ) == 2
    output = capsys.readouterr()
    assert "resolve" in (output.out + output.err).lower()


# spec: "It then runs the re-verify set on each pass's versions and reports each gate's result for each pass"
# task: 8
def test_drift_reports_both_python_passes_and_gate_results(
    tmp_path, versions
):
    sample_repo(tmp_path, versions)
    v = versions.load(tmp_path)
    all_versions = {**v.packages, **v.cited}

    class NewestPython(str):
        def __call__(self):
            return str(self)

    def resolver(requirements, python_version, cutoff):
        assert cutoff is None
        return dict(v.packages)

    def fetch(url):
        name = next(
            (name for name in all_versions if name in url.split("/")),
            "jax",
        )
        newest = "0.12.0.1" if name == "jax" else all_versions[name]
        release = {"upload_time_iso_8601": "2026-10-21T00:00:00Z"}
        return {
            "info": {"version": newest},
            "releases": {newest: [release]},
            "urls": [release],
        }

    for runner_code, expected_exit in ((0, 0), (1, 1)):
        code, report = versions.drift(
            tmp_path,
            fetch=fetch,
            resolver=resolver,
            newest_python=NewestPython("3.14"),
            runner=lambda *args, **kwargs: runner_code,
        )
        assert code == expected_exit
        assert "3.13" in report
        assert "3.14" in report
        assert "jax" in report.lower()
        assert "snippets" in report.lower()
        assert "jax-cpu" in report.lower()
        assert versions.DRIFT_LIMIT in report


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_resolve_failure_has_exit_code_two(tmp_path, versions):
    sample_repo(tmp_path, versions)

    def cannot_resolve(*args, **kwargs):
        raise versions.VersionsError("jax and numpyro conflict")

    code, report = versions.drift(
        tmp_path,
        resolver=cannot_resolve,
        newest_python=lambda: "3.14",
        fetch=lambda _url: {},
        runner=lambda *args, **kwargs: 0,
    )
    assert code == 2
    assert "jax" in report
    assert "numpyro" in report


# spec: "**Equality** ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision."
# task: 9
def test_equality_citation_accepts_current_value_and_finds_stale_value(
    tmp_path, versions, versions_check
):
    sample_repo(tmp_path, versions)
    skill, _ = seed_skill(tmp_path)
    assert versions_check.check(tmp_path, historical={}) == []
    skill.write_text(skill.read_text().replace("Polars 2.0.0", "Polars 1.42"))
    findings = versions_check.check(tmp_path, historical={})
    assert any("Polars 1.42" in finding for finding in findings)


# spec: "**Range** (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file's value."
# task: 9
def test_range_citation_finds_a_range_excluding_the_pin(
    tmp_path, versions, versions_check
):
    sample_repo(tmp_path, versions)
    skill, _ = seed_skill(tmp_path, body="Requires polars>=2.0.")
    assert versions_check.check(tmp_path, historical={}) == []
    skill.write_text(skill.read_text().replace("polars>=2.0", "polars<2.0"))
    assert any(
        "polars<2.0" in finding
        for finding in versions_check.check(tmp_path, historical={})
    )


# spec: "`HISTORICAL` is keyed by the literal phrase, not by file and line, and each entry gives its reason."
# task: 9
def test_history_allowlist_follows_the_phrase_across_files(
    tmp_path, versions, versions_check
):
    sample_repo(tmp_path, versions)
    skill, _ = seed_skill(
        tmp_path, body="ArviZ 0.23 as the classic stack."
    )
    assert versions_check.check(tmp_path, historical={})
    allowed = {"ArviZ 0.23": "History, by design"}
    assert versions_check.check(tmp_path, historical=allowed) == []
    second = tmp_path / "skills/explore-data/references/history.md"
    second.parent.mkdir()
    second.write_text("ArviZ 0.23 as the classic stack.\n")
    assert versions_check.check(tmp_path, historical=allowed) == []
    assert skill.is_file()


# spec: "A live file spells `--python 3.<n>`."
# task: 9
def test_interpreter_literal_finding_has_a_seeded_positive_control(
    tmp_path, versions, versions_check
):
    sample_repo(tmp_path, versions)
    seed_skill(tmp_path)
    guide = tmp_path / "CLAUDE.md"
    guide.write_text("Use /usr/bin/python3.\n")
    assert versions_check.check(tmp_path, historical={}) == []
    guide.write_text("uv run --python 3.13 python build/check_snippets.py\n")
    assert any(
        "--python 3.13" in finding
        for finding in versions_check.check(tmp_path, historical={})
    )


# spec: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
def test_script_floor_must_match_skill_floor(
    tmp_path, versions, versions_check
):
    sample_repo(tmp_path, versions)
    _, script = seed_skill(tmp_path)
    assert versions_check.check(tmp_path, historical={}) == []
    script.write_text(
        script.read_text().replace(
            'requires-python = ">=3.11"',
            'requires-python = ">=3.12"',
        )
    )
    assert any(
        "3.12" in finding
        for finding in versions_check.check(tmp_path, historical={})
    )


# spec: "The dev Python must satisfy each floor."
# task: 9
def test_dev_python_below_a_floor_is_a_finding(
    tmp_path, versions, versions_check
):
    sample_repo(tmp_path, versions)
    seed_skill(tmp_path, floor="3.14")
    assert any(
        "3.14" in finding
        for finding in versions_check.check(tmp_path, historical={})
    )


# spec: "`check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures."
# task: 9
def test_check_ignores_dated_records_and_data(
    tmp_path, versions, versions_check
):
    sample_repo(tmp_path, versions)
    seed_skill(tmp_path)
    for relative in (
        "specs/deferred_items.md",
        "LICENSE-example",
        "data/example.md",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("Verified on Polars 1.42.\n")
    assert versions_check.check(tmp_path, historical={}) == []


# spec: "`versions.py check` runs offline."
# task: 9
def test_check_does_not_call_network_or_uv(
    tmp_path, monkeypatch, versions
):
    sample_repo(tmp_path, versions)
    seed_skill(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("check attempted a network or uv operation")

    monkeypatch.setattr(versions, "fetch_json", forbidden)
    monkeypatch.setattr(versions, "resolve", forbidden)
    monkeypatch.setattr(versions, "run_process", forbidden)
    assert versions.main(["check"], root=tmp_path) == 0


# spec: "Documented commands spell no interpreter or package version."
# task: 13
def test_documented_commands_use_the_runner_and_no_version_flag():
    docs = [ROOT / name for name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md")]
    for path in docs:
        text = path.read_text()
        assert not re.search(r"--python\s+3\.\d+", text)
    claude = docs[0].read_text()
    assert (
        "uv run python build/versions.py run snippets -- "
        "python build/check_snippets.py --run skills/bayesian-workflow/"
    ) in claude
    assert "run jax-cpu" in claude


# spec: "Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says "on the pinned 0.21.0"."
# task: 12
def test_open_gaussian_process_item_no_longer_claims_the_old_pin():
    text = (ROOT / "specs/deferred_items.md").read_text()
    assert "on the pinned 0.21.0" not in text


# spec: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`."
# task: 12
def test_old_jax_lock_paths_are_retired():
    assert not (ROOT / "specs/verification/32-jax-cpu.in").exists()
    assert not (ROOT / "specs/verification/32-jax-cpu.txt").exists()
    assert "32-jax-cpu.txt" not in (
        ROOT / "build/check_jax_examples.py"
    ).read_text()
    assert "32-jax-cpu.txt" not in (ROOT / "CLAUDE.md").read_text()


# spec: "Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python."
# task: 12
def test_clean_code_rule_points_to_versions_file():
    assert "build/versions.toml" in (
        ROOT / "rules/clean-code-python.md"
    ).read_text()


# spec: "`versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`."
# task: 14
def test_tenth_commit_lint_is_wired():
    runner = (ROOT / "build/run_commit_lints.sh").read_text()
    assert "versions_check" in runner
    assert "build/versions.py check" in runner
    assert "versions_check" in (
        ROOT / "build/test_commit_lints.py"
    ).read_text()
    assert "run_commit_lints" in (
        ROOT / "build/githooks/pre-commit"
    ).read_text()


# spec: "`setup-uv` takes the interpreter from `.python-version`."
# task: 15
def test_lints_workflow_has_no_interpreter_literal():
    text = (ROOT / ".github/workflows/lints.yml").read_text()
    assert "setup-uv" in text
    assert (ROOT / ".python-version").is_file()
    assert not re.search(r"python-version:\s*['\"]?3\.\d+", text)


# spec: "It writes the drift report to the job summary."
# task: 15
def test_weekly_drift_workflow_is_read_only_and_reports_to_summary():
    text = (ROOT / ".github/workflows/versions-drift.yml").read_text()
    assert re.search(r"(?m)^\s*schedule:\s*$", text)
    assert re.search(r"(?m)^\s*-\s*cron:", text)
    assert "workflow_dispatch:" in text
    assert re.search(r"(?m)^\s*contents:\s*read\s*$", text)
    assert "build/versions.py drift" in text
    assert "GITHUB_STEP_SUMMARY" in text
    uses = re.findall(r"(?m)^\s*(?:-\s*)?uses:\s*\S+@(\S+)", text)
    assert uses and all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in uses)
    assert not re.search(r"\bgh\s+(?:issue|pr)\b", text)
    assert not re.search(r"\bgit\s+(?:commit|push)\b", text)
    assert not re.search(r"(?m)^\s*contents:\s*write\s*$", text)

</tests>
<flags>
</flags>
<untestable>
`build/versions.toml` is the only file in which a person sets a package version or the dev interpreter.
The plan must re-check items 2 to 6 before it relies on them.
The plan confirms that Claude Code, Codex and Gemini also ignore a plain file in a skills directory.
A person changes a `[cited]` entry only after re-checking the cited behavior.
A bump follows these steps, in one change:
The job may go red, but it is not a required check.
Known limit: GitHub disables scheduled workflows in a public repository after 60 days with no activity.
If a behavior changed, stop and bring the change to the owner before going on.
Run `bump` and `verify` on the day of execution.
Never change a citation's version without a re-check.
The plan writes each test before its code (red, then green).
No third-party text enters the repo, so `NOTICE` and the license files do not change.
The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.
This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
The R6 prose fixes rebase onto them and re-take the line numbers.
</untestable>