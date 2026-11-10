<tests>
import datetime as dt
import re
import tomllib
from pathlib import Path

import pytest

from build import check_snippets, run_suites, snippet_preamble, versions, versions_check


ROOT = Path(versions.REPO)

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
numpy = '2.5.3'
matplotlib = '3.11.2'
flax = '0.12.10'
optax = '0.2.8'
orbax-checkpoint = '0.12.6'
equinox = '0.13.8'
diffrax = '0.7.2'
e3nn-jax = '0.21.0'
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


def seed_root(root):
    (root / "build").mkdir(parents=True, exist_ok=True)
    (root / "skills").mkdir(parents=True, exist_ok=True)
    (root / "build/versions.toml").write_text(SAMPLE)
    versions.sync(root)
    return root


def seed_skill(root, prose="", compatibility="Python 3.11+", requires=">=3.11", dependency="polars>=2.0"):
    folder = root / "skills/sample"
    (folder / "scripts").mkdir(parents=True, exist_ok=True)
    skill = folder / "SKILL.md"
    script = folder / "scripts/sample.py"
    skill.write_text(
        "---\nname: sample\ndescription: Sample skill\n"
        f"compatibility: {compatibility}\n---\n{prose}\n"
    )
    script.write_text(
        "# /// script\n"
        f'# requires-python = "{requires}"\n'
        f'# dependencies = ["{dependency}"]\n'
        "# ///\n"
    )
    return skill, script


class PythonChoice(str):
    def __call__(self):
        return str(self)


def stub_metadata(url):
    package = url.rstrip("/").split("/")[-2]
    latest = {
        "jax": "0.12.0.1",
        "polars": "2.0.0",
        "plotly": "7.1.0",
        "altair": "6.3.0",
    }.get(package, "1.3.0")
    return {
        "info": {"version": latest},
        "releases": {
            latest: [{"upload_time_iso_8601": "2026-10-21T00:00:00Z"}]
        },
    }


# spec: "Record the results in `specs/verification/`."
# task: 1
def test_uv_probe_has_recorded_results():
    record = ROOT / "specs/verification/66-uv-probe.md"
    assert record.is_file()
    text = record.read_text().lower()
    assert "script" in text
    assert "shadow" in text
    assert "worktree" in text


# spec: "A missing or invalid file names the key."
# task: 2
def test_missing_dev_names_key():
    with pytest.raises(versions.VersionsError, match="dev"):
        versions.parse(SAMPLE.replace("dev = '3.13'\n", ""))


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
def test_unknown_gate_package_names_package():
    invalid = SAMPLE.replace("snippets = [", "snippets = ['pytest', ", 1)
    with pytest.raises(versions.VersionsError, match="pytest"):
        versions.parse(invalid)


# spec: "An invalid date names the value."
# task: 2
def test_invalid_date_names_value():
    invalid = SAMPLE.replace(
        "date = 2026-10-19",
        "date = '2026-10-21T00:00:00Z'",
    )
    with pytest.raises(versions.VersionsError, match="2026-10-21T00:00:00Z"):
        versions.parse(invalid)


# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_override_requires_reason_and_changes_only_its_gate():
    incomplete = SAMPLE + """
[[override]]
gate = 'jax-cpu'
package = 'jax'
version = '0.11.2'
"""
    with pytest.raises(versions.VersionsError, match="reason"):
        versions.parse(incomplete)

    complete = incomplete + "reason = 'JAX CPU examples fail on 0.12.0'\n"
    parsed = versions.parse(complete)
    assert "jax==0.11.2" in parsed.stack("jax-cpu")
    assert "jax==0.12.0" in parsed.stack("snippets")


# spec: "Equality ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision."
# task: 2
def test_version_comparison_zero_pads_precision():
    assert versions.compare("6.8", "6.8.0") == 0
    assert versions.compare("1.42", "2.0.0") < 0


# spec: "Polars is in `[packages]` by the second case: the suites install it, and three headers floor it."
# task: 4
def test_real_package_selection():
    parsed = versions.load(ROOT)
    assert "polars" in parsed.packages
    assert {"pytest", "pyyaml", "scipy", "tensorstore"}.isdisjoint(parsed.packages)
    assert all(
        package in parsed.packages
        for gate in parsed.gates.values()
        for package in gate
    )


# spec: "A package gets a `[cited]` entry when skill prose cites a version for it and no check runs it."
# task: 4
def test_cited_packages_are_outside_gates():
    parsed = versions.load(ROOT)
    assert {"altair", "plotly", "optuna", "great-docs"} <= set(parsed.cited)
    gate_packages = {package for gate in parsed.gates.values() for package in gate}
    assert set(parsed.cited).isdisjoint(gate_packages)


# spec: "The file does not hold the script floors (`requires-python`, `compatibility:`) or the 3.9 floor of `install.py` and the read-only agent guard."
# task: 4
def test_versions_file_does_not_centralize_user_floors():
    text = (ROOT / "build/versions.toml").read_text()
    assert "requires-python" not in text
    assert "compatibility:" not in text
    assert "3.9" not in text


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_writes_exact_generated_text(tmp_path):
    parsed = versions.parse(SAMPLE)
    expected = versions.outputs(parsed)
    assert set(expected) == {".python-version", "uv.toml", "skills/uv.toml"}
    assert expected[".python-version"] == "3.13\n"
    assert tomllib.loads(expected["uv.toml"])["exclude-newer"] == "2026-10-20T00:00:00Z"
    assert tomllib.loads(expected["skills/uv.toml"]) == {}
    assert "build/versions.toml" in expected["skills/uv.toml"]

    root = seed_root(tmp_path)
    for path, content in expected.items():
        assert (root / path).read_text() == content


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_check_detects_a_stale_output(tmp_path):
    root = seed_root(tmp_path)
    assert versions.main(["sync", "--check"], root=root) == 0
    (root / ".python-version").write_text("3.12\n")
    assert versions.main(["sync", "--check"], root=root) != 0


# spec: "With `--only`, the other entries stay at their pins in the joint resolve."
# task: 3
def test_only_requirements_keep_other_packages_pinned():
    parsed = versions.parse(SAMPLE)
    requested = versions.requirements(parsed, only=("jax",))
    assert "jax" in requested
    assert "jax==0.12.0" not in requested
    assert "arviz==1.3.0" in requested
    assert "polars==2.0.0" in requested


# spec: "`bump` never changes `[cited]`."
# task: 3
def test_bump_changes_resolved_packages_and_syncs_but_keeps_cited(tmp_path):
    root = seed_root(tmp_path)
    before = versions.load(root)
    calls = []

    def resolve(requirements, python_version, cutoff):
        calls.append((requirements, python_version, cutoff))
        return {**before.packages, "jax": "0.12.0.1"}

    versions.bump(root, dt.date(2026, 10, 21), only=("jax",), resolver=resolve)
    after = versions.load(root)

    assert len(calls) == 1
    assert calls[0][1] == "3.13"
    assert after.freeze == dt.date(2026, 10, 21)
    assert after.packages["jax"] == "0.12.0.1"
    assert after.cited == before.cited
    assert (root / ".python-version").read_text() == versions.outputs(after)[".python-version"]
    assert (root / "uv.toml").read_text() == versions.outputs(after)["uv.toml"]


# spec: "`--pin` changes one package for one run and never edits the file."
# task: 5
def test_pin_changes_run_argv_without_changing_versions_file(tmp_path):
    root = seed_root(tmp_path)
    parsed = versions.load(root)
    original = (root / "build/versions.toml").read_text()

    argv = versions.uv_run_argv(
        parsed,
        "snippets",
        ["python", "build/check_snippets.py"],
        pins={"jax": "0.12.0.1"},
    )

    assert "jax==0.12.0.1" in argv
    assert "jax==0.12.0" not in argv
    assert "--exclude-newer" in argv
    assert parsed.cutoff in argv
    assert "--python" not in argv
    assert (root / "build/versions.toml").read_text() == original


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 5
def test_pin_rejects_package_outside_packages():
    parsed = versions.parse(SAMPLE)
    with pytest.raises(versions.VersionsError, match="pytest"):
        versions.parse_pins(parsed, ["pytest==1.0"])


# spec: "uv compares the date with the upload time of each file, not of the release."
# task: 5
def test_late_pin_checks_distribution_files():
    parsed = versions.parse(SAMPLE)

    def fetch(_url):
        return {
            "releases": {
                "0.12.0": [
                    {"upload_time_iso_8601": "2026-10-19T00:00:00Z"},
                    {"upload_time_iso_8601": "2026-10-20T00:00:00Z"},
                ]
            }
        }

    assert "jax==0.12.0" in versions.late_pins(
        parsed, ["jax==0.12.0"], fetch=fetch
    )


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 6
def test_api_remediation_does_not_select_pinned_snippets_gate():
    command = check_snippets.API_REMEDIATION
    assert "--api" in command
    assert "versions.py run snippets" not in command
    assert not re.search(r"\b(?:arviz|jax|numpyro)==\d", command)


# spec: "`build/check_snippets.py`: `PINNED` (moved out of `build/snippet_preamble.py`), `RUN_REMEDIATION` and `API_REMEDIATION`."
# task: 6
def test_snippet_preamble_no_longer_owns_pins():
    assert not hasattr(snippet_preamble, "PINNED")
    assert "versions.py run snippets" in check_snippets.RUN_REMEDIATION


# spec: "A `with` or `extras` package that `[packages]` names gets its pin."
# task: 7
def test_suite_dependencies_use_central_pins():
    parsed = versions.load(ROOT)
    pins = run_suites.Pins.from_versions(parsed)
    assert pins.spec("polars>=2.0") == f"polars=={parsed.packages['polars']}"
    assert pins.spec("pytest") == "pytest"
    assert pins.python == parsed.dev_python
    assert pins.cutoff == parsed.cutoff


# spec: "Each run passes `--exclude-newer <date>` explicitly, because suites under `skills/` sit below the shadow file."
# task: 7
def test_suite_runs_explicitly_pass_freeze_date():
    parsed = versions.load(ROOT)
    captured = []

    def run_one(*args, **kwargs):
        captured.append((args, kwargs))
        return 0

    assert run_suites.main(["--all", "--extras"], ROOT, run_one) == 0
    assert captured
    for args, kwargs in captured:
        command = " ".join(str(value) for value in (*args, *kwargs.values()))
        assert "--exclude-newer" in command
        assert parsed.cutoff in command


# spec: "The `hooks` suite keeps its explicit `/usr/bin/python3` run."
# task: 7
def test_suite_configuration_retains_system_python():
    text = (ROOT / "build/suites.toml").read_text()
    assert "/usr/bin/python3" in text
    assert re.search(r"""['"]dev['"]""", text)


# spec: "`verify [--pin pkg==X ...]` | yes | Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`"
# task: 8
def test_verify_steps_cover_all_four_gates():
    parsed = versions.parse(SAMPLE)
    steps = versions.verify_steps(parsed)
    assert [step.label for step in steps] == [
        "tier 2 (--api)",
        "tier 3 (--run)",
        "jax cpu examples",
        "suites",
    ]
    commands = {step.label: " ".join(step.argv) for step in steps}
    assert "--api" in commands["tier 2 (--api)"]
    assert "--run" in commands["tier 3 (--run)"]
    assert "32-jax-cpu.txt" not in commands["jax cpu examples"]
    assert "jax-cpu" in commands["jax cpu examples"] or "jax==0.12.0" in commands["jax cpu examples"]
    assert "--all" in commands["suites"]
    assert "--extras" in commands["suites"]


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
def test_run_and_verify_propagate_failed_process(tmp_path, monkeypatch):
    root = seed_root(tmp_path)
    monkeypatch.setattr(versions, "run_process", lambda *_args, **_kwargs: 1)
    monkeypatch.setattr(versions, "late_pins", lambda *_args, **_kwargs: [])

    assert versions.main(
        ["run", "snippets", "--", "python", "build/check_snippets.py"],
        root=root,
    ) != 0
    assert versions.main(["verify"], root=root) != 0


# spec: "`bump` exits 2 on a network or resolve failure and names the step."
# task: 3
def test_bump_resolve_failure_has_exit_two_and_step(tmp_path, monkeypatch, capsys):
    root = seed_root(tmp_path)

    def fail_resolve(*_args, **_kwargs):
        raise versions.VersionsError("joint resolve conflict: jax, jaxlib")

    monkeypatch.setattr(versions, "resolve", fail_resolve)
    assert versions.main(["bump", "--date", "2026-10-21"], root=root) == 2
    output = capsys.readouterr()
    assert "resolve" in (output.out + output.err).lower()
    assert "jax" in output.out + output.err


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_exit_codes_against_stubbed_uv(tmp_path):
    root = seed_root(tmp_path)
    parsed = versions.load(root)
    calls = []

    def resolve(_requirements, python_version, cutoff):
        calls.append((python_version, cutoff))
        return {**parsed.packages, **parsed.cited}

    def pass_run(_argv, _root, _env):
        return 0

    code, report = versions.drift(
        root,
        fetch=stub_metadata,
        resolver=resolve,
        newest_python=PythonChoice("3.14"),
        runner=pass_run,
    )
    assert code == 0
    assert ("3.13", None) in calls
    assert ("3.14", None) in calls
    assert "jax" in report
    assert "0.12.0.1" in report
    assert "2026-10-21" in report
    assert versions.DRIFT_LIMIT in report

    def fail_jax(argv, _root, _env):
        return 1 if "check_jax_examples.py" in " ".join(argv) else 0

    code, report = versions.drift(
        root,
        fetch=stub_metadata,
        resolver=resolve,
        newest_python=PythonChoice("3.14"),
        runner=fail_jax,
    )
    assert code == 1
    assert "jax cpu examples" in report.lower()

    def fail_resolve(*_args, **_kwargs):
        raise versions.VersionsError("joint resolve conflict: jax, jaxlib")

    code, report = versions.drift(
        root,
        fetch=stub_metadata,
        resolver=fail_resolve,
        newest_python=PythonChoice("3.14"),
        runner=pass_run,
    )
    assert code == 2
    assert "jax" in report


# spec: "`versions.py check` runs offline."
# task: 9
def test_check_does_not_open_network_connections(tmp_path, monkeypatch):
    import socket

    root = seed_root(tmp_path)
    seed_skill(root)

    def no_network(*_args, **_kwargs):
        raise AssertionError("check attempted network access")

    monkeypatch.setattr(socket, "create_connection", no_network)
    assert versions_check.check(root) == []


# spec: "Equality ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision."
# task: 9
def test_check_equality_has_stale_positive_control(tmp_path):
    root = seed_root(tmp_path)
    skill, _script = seed_skill(root, prose="Verified on Polars 1.42.")
    assert any("polars" in finding.lower() for finding in versions_check.check(root))

    skill.write_text(skill.read_text().replace("Polars 1.42", "Polars 2.0"))
    assert versions_check.check(root) == []


# spec: "Range (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file's value."
# task: 9
def test_check_range_has_stale_positive_control(tmp_path):
    root = seed_root(tmp_path)
    _skill, script = seed_skill(root, dependency="polars<2.0")
    assert any("polars" in finding.lower() for finding in versions_check.check(root))

    script.write_text(script.read_text().replace("polars<2.0", "polars>=2.0"))
    assert versions_check.check(root) == []


# spec: "History ("ArviZ 0.23", "and earlier") passes only through the `HISTORICAL` allowlist."
# task: 9
def test_check_history_requires_literal_phrase_allowlist(tmp_path):
    root = seed_root(tmp_path)
    seed_skill(root, prose="ArviZ 0.23 is the classic stack.")
    assert versions_check.check(root, historical={})
    assert versions_check.check(
        root,
        historical={"ArviZ 0.23": "classic stack history"},
    ) == []


# spec: "An interpreter path such as `/usr/bin/python3` is not a literal."
# task: 9
def test_interpreter_literal_fails_but_system_path_passes(tmp_path):
    root = seed_root(tmp_path)
    guide = root / "CLAUDE.md"
    guide.write_text("uv run --python 3.13 python build/check_snippets.py\n")
    assert versions_check.check(root)

    guide.write_text("uv run --python /usr/bin/python3 python build/check_snippets.py\n")
    assert versions_check.check(root) == []


# spec: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
def test_python_floor_mismatch_has_stale_positive_control(tmp_path):
    root = seed_root(tmp_path)
    skill, _script = seed_skill(root, compatibility="Python 3.11+", requires=">=3.12")
    assert versions_check.check(root)

    skill.write_text(skill.read_text().replace("Python 3.11+", "Python 3.12+"))
    assert versions_check.check(root) == []


# spec: "The dev Python must satisfy each floor."
# task: 9
def test_dev_python_below_matching_floor_fails(tmp_path):
    root = seed_root(tmp_path)
    seed_skill(root, compatibility="Python 3.14+", requires=">=3.14")
    assert versions_check.check(root)


# spec: "`check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures."
# task: 9
def test_check_skips_records_licenses_data_and_fixtures(tmp_path):
    root = seed_root(tmp_path)
    for relative in (
        "specs/deferred_items.md",
        "LICENSE",
        "data/example.md",
        "build/fixtures/example.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("uv run --python 3.12\nVerified on Polars 1.42.\n")
    assert versions_check.check(root) == []


# spec: "Known limit: `check` sees only the package names that the file lists."
# task: 9
def test_check_ignores_unlisted_package_names(tmp_path):
    root = seed_root(tmp_path)
    seed_skill(root, prose="Verified on pytest 1.0.")
    assert versions_check.check(root) == []


# spec: "Use one JAX version for both gates."
# task: 10
def test_real_jax_gates_share_pin_or_have_reasoned_override():
    parsed = versions.load(ROOT)
    snippets = dict(item.split("==", 1) for item in parsed.stack("snippets"))
    cpu = dict(item.split("==", 1) for item in parsed.stack("jax-cpu"))
    if snippets["jax"] != cpu["jax"]:
        assert any(
            item.gate == "jax-cpu"
            and item.package == "jax"
            and item.version == cpu["jax"]
            and item.reason
            for item in parsed.overrides
        )
        assert "jax-cpu" in (ROOT / "specs/deferred_items.md").read_text()
    else:
        assert snippets["jax"] == cpu["jax"]


# spec: "This keeps the `polars>=2.0` floors that the portability plan set on purpose (`specs/plans/completed/53-agent-skills-portability.md`, decision DF4)."
# task: 10
def test_real_polars_pin_satisfies_portability_floor():
    parsed = versions.load(ROOT)
    assert versions.compare(parsed.packages["polars"], "2.0") >= 0


# spec: "Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says "on the pinned 0.21.0"."
# task: 12
def test_gaussian_process_item_no_longer_calls_old_numpyro_pin_current():
    text = (ROOT / "specs/deferred_items.md").read_text()
    assert "on the pinned 0.21.0" not in text


# spec: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`."
# task: 12
def test_old_cpu_lock_is_retired_from_live_readers():
    assert not (ROOT / "specs/verification/32-jax-cpu.in").exists()
    assert not (ROOT / "specs/verification/32-jax-cpu.txt").exists()
    assert "32-jax-cpu.txt" not in (ROOT / "build/check_jax_examples.py").read_text()
    assert "32-jax-cpu.txt" not in (ROOT / "CLAUDE.md").read_text()


# spec: "Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python."
# task: 12
def test_clean_code_rule_points_to_versions_file():
    assert "build/versions.toml" in (ROOT / "rules/clean-code-python.md").read_text()


# spec: "Documented commands spell no interpreter or package version."
# task: 13
def test_documented_commands_have_no_hand_copied_versions():
    for relative in (
        "CLAUDE.md",
        "AGENTS.md",
        "GEMINI.md",
        "build/run_commit_lints.sh",
    ):
        for line in (ROOT / relative).read_text().splitlines():
            if "uv run" in line or re.search(r"\bpython\s+(?:build|hooks)/", line):
                assert not re.search(r"--python\s+3\.\d+", line), (relative, line)
                assert not re.search(r"\b[a-z][a-z0-9-]*==\d", line), (relative, line)


# spec: "`build/cc_guide/notice.sh:114` and `build/githooks/pre-commit:15`: they can run outside the repo's working directory, so they take the interpreter from the file and not from a literal."
# task: 13
def test_notice_reads_dev_python_instead_of_spelling_it():
    text = (ROOT / "build/cc_guide/notice.sh").read_text()
    assert not re.search(r"--python\s+3\.\d+", text)
    assert ".python-version" in text or "versions.toml" in text or "versions.py" in text


# spec: "`build/cc_guide/notice.sh:114` and `build/githooks/pre-commit:15`: they can run outside the repo's working directory, so they take the interpreter from the file and not from a literal."
# task: 14
def test_precommit_reads_dev_python_instead_of_spelling_it():
    text = (ROOT / "build/githooks/pre-commit").read_text()
    assert not re.search(r"--python\s+3\.\d+", text)
    assert ".python-version" in text or "versions.toml" in text or "versions.py" in text


# spec: "`versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`."
# task: 14
def test_tenth_commit_lint_is_wired():
    text = (ROOT / "build/run_commit_lints.sh").read_text()
    assert "versions_check" in text
    assert "uv run python build/versions.py check" in text
    assert versions_check.check(ROOT) == []


# spec: "`setup-uv` takes the interpreter from `.python-version`."
# task: 14
def test_lints_workflow_uses_python_version_file():
    text = (ROOT / ".github/workflows/lints.yml").read_text()
    assert "setup-uv" in text
    assert ".python-version" in text
    assert not re.search(r"python-version:\s*['\"]?3\.\d+", text)


# spec: "It has `permissions: contents: read`, and it pins its actions by SHA, as `lints.yml` does."
# task: 15
def test_drift_workflow_permissions_and_action_pins():
    text = (ROOT / ".github/workflows/versions-drift.yml").read_text()
    assert re.search(r"(?m)^\s*contents:\s*read\s*$", text)
    remote_actions = re.findall(r"(?m)^\s*-\s*uses:\s*(\S+)|^\s*uses:\s*(\S+)", text)
    for pair in remote_actions:
        action = pair[0] or pair[1]
        if action.startswith("./"):
            continue
        assert re.search(r"@[0-9a-f]{40}$", action), action


# spec: "It writes the drift report to the job summary."
# task: 15
def test_drift_workflow_reports_on_schedule_and_dispatch():
    text = (ROOT / ".github/workflows/versions-drift.yml").read_text()
    assert "schedule:" in text
    assert "cron:" in text
    assert "workflow_dispatch:" in text
    assert "versions.py drift" in text
    assert "GITHUB_STEP_SUMMARY" in text


# spec: "It never opens an issue or a PR, and it never commits."
# task: 15
def test_drift_workflow_has_no_repository_mutation():
    text = (ROOT / ".github/workflows/versions-drift.yml").read_text()
    assert not re.search(r"\bgh\s+(?:issue|pr)\s+create\b", text)
    assert not re.search(r"\bgit\s+(?:commit|push)\b", text)


# spec: "`CLAUDE.md` has 153 lines against a 200-line budget."
# task: 14
def test_claude_guide_stays_within_line_budget():
    assert len((ROOT / "CLAUDE.md").read_text().splitlines()) <= 200
</tests>
<flags>
<flag task="4"><spec>A package gets a `[packages]` entry in two cases.</spec><plan>The package list of Q2.</plan></flag>
<flag task="5"><spec>uv compares the date with the upload time of each file, not of the release.</spec><plan>`late_pins(v, specs, fetch=None) -> list[str]` (the specs whose release was first uploaded at or after the cutoff)</plan></flag>
<flag task="6"><spec>Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date.</spec><plan>`check_snippets.API_REMEDIATION` and `RUN_REMEDIATION` as runner commands.</plan></flag>
<flag task="12"><spec>`build/check_jax_examples.py` and its documented command: they install `stack('jax-cpu')` in place of `--with-requirements specs/verification/32-jax-cpu.txt`.</spec><plan>Produces: no file that names a lock file that no longer exists in its old place.</plan></flag>
<flag task="14"><spec>`setup-uv` takes the interpreter from `.python-version`.</spec><plan>Modify: `build/test_commit_lints.py`, `build/run_commit_lints.sh`, `build/githooks/pre-commit`, `CLAUDE.md`, `build/CLAUDE.md`</plan></flag>
</flags>
<untestable>
The repo fixes package versions by hand in many places, and nothing ties the copies together.
On 2026-10-21 the owner found NumPyro at 0.21.0 in one deferred item and at 0.22.0 in `PINNED`.
This work is not part of plan 64 (bayesian-workflow and recommend-probabilistic-model routing).
"Version" has four roles here.
They change for different reasons, so the design keeps them apart.
Conflict: the two gates pin different JAX releases.
The interpreter is not one value.
Three separate roles exist:
A floor states when an API appeared.
A new upstream release does not make it stale.
Conflict: the Polars citations disagree.
A floating gate would have changed today: jax 0.12.0.1 was uploaded on 2026-10-21.
The cause of the 1.44.2 result is unknown.
Every `uv run` in the repo uses the dev interpreter with no `--python` flag, from any subdirectory
Every `uv run` from the repo root resolves as of the freeze date, script headers included.
Files uploaded on the freeze date itself (UTC) are included.
CI and a local machine resolve alike, because uv reads a bare date in local time (Inventory, uv item 7)
It shadows the root date under `skills/`, so a skill script that a user runs floats within its floors (D8), whatever the path form
The plan confirms that Claude Code, Codex and Gemini also ignore a plain file in a skills directory.
A person changes a `[cited]` entry only after re-checking the cited behavior.
A bump follows these steps, in one change:
The report states which.
The job may go red, but it is not a required check.
Known limit: GitHub disables scheduled workflows in a public repository after 60 days with no activity.
The spec accepts this.
It does not work around it.
Re-probe the uv behaviors in the Inventory (items 2 to 6, the shadow file under `skills/`, and nested-worktree inheritance) on the uv version of the day.
If a behavior changed, stop and bring the change to the owner before going on.
Write `build/versions.toml`, then run `bump` and `verify` on the day of execution.
The JAX CPU examples must pass on it.
If they fail, add a temporary `[[override]]` for `jax-cpu` with its reason, and log a deferred item to remove it.
Pin Polars at the latest release (2.0.0 on 2026-10-21).
For each stale citation, either re-verify the cited behavior on the file's version and update the citation, or move it to `HISTORICAL` with the reason "verified on X, not re-checked on Y" and log a deferred item to re-check it.
Never change a citation's version without a re-check.
The plan writes each test before its code (red, then green).
No third-party text enters the repo, so `NOTICE` and the license files do not change.
The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.
It edits `build/run_commit_lints.sh`.
This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
They edit bayesian-workflow prose that holds Role 3 and Role 4 citations.
The R6 prose fixes rebase onto them and re-take the line numbers.
</untestable>