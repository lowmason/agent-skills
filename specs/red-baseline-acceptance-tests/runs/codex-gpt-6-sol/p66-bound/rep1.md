<tests>
import datetime as dt
import importlib
import os
import re
import sys
import tomllib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]

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


def _build(name):
    build_dir = str(ROOT / "build")
    if build_dir not in sys.path:
        sys.path.insert(0, build_dir)
    return importlib.import_module(name)


def _repo(tmp_path, text=SAMPLE):
    versions = _build("versions")
    (tmp_path / "build").mkdir()
    (tmp_path / "skills").mkdir()
    (tmp_path / "build" / "versions.toml").write_text(text)
    versions.sync(tmp_path)
    return tmp_path


def _findings(root, historical=None):
    return _build("versions_check").check(root, historical=historical)


# spec: "Re-probe the uv behaviors in the Inventory (items 2 to 6, the shadow file under `skills/`, and nested-worktree inheritance) on the uv version of the day."
# task: 1
def test_uv_probe_records_the_required_cases():
    probe = ROOT / "specs/verification/66-uv-probe.md"
    text = probe.read_text().lower()
    for term in ("uv version", "script", "exclude-newer", "symlink", "skills/uv.toml", "worktree"):
        assert term in text


# spec: "`build/versions.toml` is the only file in which a person sets a package version or the dev interpreter."
# task: 4
def test_versions_file_has_the_required_tables_and_types():
    data = tomllib.loads((ROOT / "build/versions.toml").read_text())
    assert isinstance(data["python"]["dev"], str)
    assert isinstance(data["freeze"]["date"], dt.date)
    assert isinstance(data["packages"], dict)
    assert isinstance(data["cited"], dict)
    assert isinstance(data["gates"], dict)
    assert {"snippets", "jax-cpu"} <= data["gates"].keys()


# spec: "Polars is in `[packages]` by the second case: the suites install it, and three headers floor it."
# task: 4
def test_polars_is_a_package_pin():
    assert "polars" in _build("versions").load(ROOT).packages


# spec: "Other packages (pytest, pyyaml, scipy, tensorstore and the rest) get no entry, and the freeze date fixes them."
# task: 4
def test_packages_without_a_required_pin_are_absent():
    packages = _build("versions").load(ROOT).packages
    assert {"pytest", "pyyaml", "scipy", "tensorstore"}.isdisjoint(packages)


# spec: "A package gets a `[cited]` entry when skill prose cites a version for it and no check runs it."
# task: 4
def test_cited_packages_are_separate_from_gate_packages():
    v = _build("versions").load(ROOT)
    assert {"altair", "plotly", "optuna", "great-docs"} <= v.cited.keys()
    assert set(v.cited).isdisjoint(v.packages)


# spec: "A missing or invalid file names the key."
# task: 2
def test_missing_dev_python_names_its_key():
    versions = _build("versions")
    text = SAMPLE.replace("dev = '3.13'\n", "")
    with pytest.raises(versions.VersionsError, match="dev"):
        versions.parse(text)


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
def test_unknown_gate_package_is_named():
    versions = _build("versions")
    text = SAMPLE.replace(
        "jax-cpu = [",
        "unknown = ['not-a-package']\njax-cpu = [",
    )
    with pytest.raises(versions.VersionsError, match="not-a-package"):
        versions.parse(text)


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
def test_unknown_override_package_is_named():
    versions = _build("versions")
    text = SAMPLE + """
[[override]]
gate = 'jax-cpu'
package = 'not-a-package'
version = '1.0'
reason = 'test'
"""
    with pytest.raises(versions.VersionsError, match="not-a-package"):
        versions.parse(text)


# spec: "An invalid date names the value."
# task: 2
def test_invalid_freeze_date_is_named():
    versions = _build("versions")
    with pytest.raises(versions.VersionsError, match="2026-99-99"):
        versions.parse(SAMPLE.replace("2026-10-19", "2026-99-99"))


# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_stack_uses_the_shared_pin_unless_a_reasoned_override_exists():
    versions = _build("versions")
    ordinary = versions.parse(SAMPLE)
    assert "jax==0.12.0" in ordinary.stack("snippets")
    assert "jax==0.12.0" in ordinary.stack("jax-cpu")

    overridden = versions.parse(SAMPLE + """
[[override]]
gate = 'jax-cpu'
package = 'jax'
version = '0.11.2'
reason = 'CPU examples require this release'
""")
    assert "jax==0.12.0" in overridden.stack("snippets")
    assert "jax==0.11.2" in overridden.stack("jax-cpu")


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_writes_exactly_the_rendered_outputs(tmp_path):
    versions = _build("versions")
    root = _repo(tmp_path)
    rendered = versions.outputs(versions.load(root))
    assert len(rendered) == 3
    for name, expected_text in rendered.items():
        path = Path(name)
        if not path.is_absolute():
            path = root / path
        assert path.read_text() == expected_text
    assert versions.sync(root, check=True) == []


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_check_detects_each_changed_output(tmp_path):
    versions = _build("versions")
    root = _repo(tmp_path)
    for relative in (".python-version", "uv.toml", "skills/uv.toml"):
        path = root / relative
        original = path.read_text()
        path.write_text(original + "\n# stale\n")
        assert versions.sync(root, check=True)
        path.write_text(original)
    assert versions.sync(root, check=True) == []


# spec: "Files uploaded on the freeze date itself (UTC) are included."
# task: 2
def test_sync_uses_midnight_utc_after_the_freeze_date(tmp_path):
    root = _repo(tmp_path)
    assert (root / ".python-version").read_text().strip() == "3.13"
    uv_settings = tomllib.loads((root / "uv.toml").read_text())
    assert uv_settings["exclude-newer"] == "2026-10-20T00:00:00Z"
    shadow = (root / "skills/uv.toml").read_text()
    assert tomllib.loads(shadow) == {}
    assert "build/versions.toml" in shadow


# spec: "With `--only`, the other entries stay at their pins in the joint resolve"
# task: 3
def test_bump_only_keeps_other_pins_in_the_joint_resolve(tmp_path):
    versions = _build("versions")
    root = _repo(tmp_path)
    before = versions.load(root)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((requirements, python_version, cutoff))
        return {**before.packages, "jax": "0.12.0.1"}

    versions.bump(root, dt.date(2026, 10, 21), only=("jax",), resolver=resolver)
    assert len(calls) == 1
    requirements, python_version, cutoff = calls[0]
    assert python_version == "3.13"
    assert "jax" in requirements
    assert "jax==0.12.0" not in requirements
    assert "numpyro==0.22.0" in requirements
    assert cutoff == "2026-10-22T00:00:00Z"
    assert versions.load(root).packages["jax"] == "0.12.0.1"
    assert versions.sync(root, check=True) == []


# spec: "`bump` never changes `[cited]`."
# task: 3
def test_bump_preserves_cited_versions(tmp_path):
    versions = _build("versions")
    root = _repo(tmp_path)
    before = versions.load(root)

    def resolver(requirements, python_version, cutoff):
        return {**before.packages, "jax": "0.12.0.1"}

    versions.bump(root, dt.date(2026, 10, 21), resolver=resolver)
    assert versions.load(root).cited == before.cited


# spec: "A joint resolve that fails in `bump` or `drift` names the packages in conflict."
# task: 3
def test_bump_surfaces_joint_resolve_conflicts(tmp_path):
    versions = _build("versions")
    root = _repo(tmp_path)

    def resolver(requirements, python_version, cutoff):
        raise versions.VersionsError("jax conflicts with numpyro")

    with pytest.raises(versions.VersionsError, match=r"jax.*numpyro"):
        versions.bump(root, dt.date(2026, 10, 21), resolver=resolver)


# spec: "`--pin` changes one package for one run and never edits the file."
# task: 5
def test_run_pin_changes_only_the_argv(tmp_path):
    versions = _build("versions")
    root = _repo(tmp_path)
    before = (root / "build/versions.toml").read_text()
    v = versions.load(root)
    pins = versions.parse_pins(v, ["jax==0.12.0.1"])
    argv = versions.uv_run_argv(v, "snippets", ["python", "-c", "pass"], pins=pins)
    command = " ".join(argv)
    assert "jax==0.12.0.1" in command
    assert "numpyro==0.22.0" in command
    assert v.cutoff in command
    assert (root / "build/versions.toml").read_text() == before


# spec: "A pin uploaded after the freeze date names the package and the date."
# task: 5
def test_late_pin_reports_its_package_and_upload_date():
    versions = _build("versions")
    v = versions.parse(SAMPLE)

    def fetch(url):
        uploaded = "2026-10-21T10:00:00Z"
        record = {"upload_time_iso_8601": uploaded}
        return {
            "info": {"version": "0.12.0.1"},
            "urls": [record],
            "releases": {"0.12.0.1": [record]},
        }

    findings = versions.late_pins(v, ["jax==0.12.0.1"], fetch=fetch)
    assert findings
    assert "jax" in str(findings)
    assert "2026-10-21" in str(findings)


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 5
def test_run_propagates_a_failing_uv_exit(tmp_path, monkeypatch):
    versions = _build("versions")
    root = _repo(tmp_path)
    monkeypatch.setattr(versions, "late_pins", lambda *args, **kwargs: [])
    monkeypatch.setattr(versions, "run_process", lambda argv, root, env: 17)
    assert versions.main(
        ["run", "snippets", "--", "python", "-c", "pass"], root=root
    ) != 0


# spec: "`build/check_snippets.py`: `PINNED` (moved out of `build/snippet_preamble.py`), `RUN_REMEDIATION` and `API_REMEDIATION`."
# task: 6
def test_snippet_pins_have_one_reader_and_no_preamble_copy():
    snippets = _build("check_snippets")
    preamble = _build("snippet_preamble")
    v = _build("versions").load(ROOT)
    assert not hasattr(preamble, "PINNED")
    assert hasattr(snippets, "PINNED")
    assert str(v.packages["numpyro"]) in str(snippets.PINNED)
    assert "versions.py run snippets" in str(snippets.RUN_REMEDIATION)


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 6
def test_tier_two_remediation_remains_unpinned():
    snippets = _build("check_snippets")
    command = str(snippets.API_REMEDIATION)
    assert "==" not in command
    assert "versions.py run snippets" not in command
    assert "exclude-newer" in command


# spec: "`build/check_jax_examples.py` and its documented command: they install `stack('jax-cpu')` in place of `--with-requirements specs/verification/32-jax-cpu.txt`."
# task: 6
def test_jax_example_reader_uses_the_gate_stack():
    source = (ROOT / "build/check_jax_examples.py").read_text()
    assert "32-jax-cpu.txt" not in source
    assert "jax-cpu" in source
    assert "32-jax-cpu.txt" not in (ROOT / "CLAUDE.md").read_text()


# spec: "A `with` or `extras` package that `[packages]` names gets its pin."
# task: 7
def test_suite_dependency_pins_follow_the_file():
    versions = _build("versions")
    suites = _build("run_suites")
    v = versions.parse(SAMPLE)
    pins = suites.Pins.from_versions(v)
    assert pins.python == v.dev_python
    assert pins.spec("polars>=2.0") == "polars==2.0.0"
    assert pins.spec("arviz>=1.0") == "arviz==1.3.0"
    assert pins.spec("pytest") == "pytest"


# spec: "Each run passes `--exclude-newer <date>` explicitly, because suites under `skills/` sit below the shadow file."
# task: 7
def test_suite_runs_use_an_explicit_freeze_date():
    suites = _build("run_suites")
    v = _build("versions").parse(SAMPLE)
    pins = suites.Pins.from_versions(v)
    assert pins.cutoff == v.cutoff
    assert suites.DEV == "dev"
    assert "dev" in (ROOT / "build/suites.toml").read_text()


# spec: "The `hooks` suite keeps its explicit `/usr/bin/python3` run."
# task: 7
def test_hooks_suite_retains_system_python():
    assert "/usr/bin/python3" in (ROOT / "build/suites.toml").read_text()


# spec: "`verify [--pin pkg==X ...]` | yes | Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`"
# task: 8
def test_verify_steps_cover_all_four_gates():
    versions = _build("versions")
    steps = versions.verify_steps(versions.parse(SAMPLE))
    assert [step.label for step in steps] == [
        "tier 2 (--api)",
        "tier 3 (--run)",
        "jax cpu examples",
        "suites",
    ]
    commands = [" ".join(map(str, step.argv)) for step in steps]
    assert "--api" in commands[0]
    assert "==" not in commands[0]
    assert "--run" in commands[1]
    assert "jax-cpu" in commands[2]
    assert "32-jax-cpu.txt" not in commands[2]
    assert "--all" in commands[3] and "--extras" in commands[3]


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
def test_verify_reports_a_failed_step(tmp_path):
    versions = _build("versions")
    steps = [
        versions.Step("passing gate", ["uv", "run", "pass"]),
        versions.Step("failing gate", ["uv", "run", "fail"]),
    ]

    def runner(argv, root, env):
        return 1 if argv[-1] == "fail" else 0

    assert versions.run_steps(steps, tmp_path, {}, runner) == ["failing gate"]


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_has_success_gate_failure_and_resolve_failure_codes(tmp_path):
    versions = _build("versions")
    root = _repo(tmp_path)
    v = versions.load(root)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((python_version, cutoff))
        return dict(v.packages)

    def fetch(url):
        match = re.search(r"/pypi/([^/]+)", str(url))
        package = match.group(1) if match else "jax"
        current = v.packages.get(package, v.cited.get(package, "1.0"))
        upload = {"upload_time_iso_8601": "2026-10-18T00:00:00Z"}
        return {
            "info": {"version": current},
            "urls": [upload],
            "releases": {current: [upload]},
        }

    common = {
        "fetch": fetch,
        "resolver": resolver,
        "newest_python": lambda: "3.14",
    }
    code, report = versions.drift(
        root, runner=lambda argv, root, env: 0, **common
    )
    assert code == 0
    assert ("3.13", None) in calls
    assert ("3.14", None) in calls
    assert "jax" in report and "altair" in report
    assert versions.DRIFT_LIMIT in report

    code, report = versions.drift(
        root, runner=lambda argv, root, env: 1, **common
    )
    assert code == 1
    assert report

    def unavailable(requirements, python_version, cutoff):
        raise OSError("stub network unavailable")

    code, report = versions.drift(
        root,
        runner=lambda argv, root, env: 0,
        fetch=fetch,
        resolver=unavailable,
        newest_python=lambda: "3.14",
    )
    assert code == 2
    assert "unavailable" in report


# spec: "**Equality** (\"verified on Polars 1.42\", `numpyro==0.22.0`, \"checked in the 0.22.0\") must equal the file's value at the cited precision."
# task: 9
def test_equality_citation_has_a_stale_positive_control(tmp_path):
    root = _repo(tmp_path)
    skill = root / "skills/demo/SKILL.md"
    skill.parent.mkdir()
    skill.write_text("Verified on Polars 1.42.\n")
    assert _findings(root, historical={})
    skill.write_text("Verified on Polars 2.0.\n")
    assert _findings(root, historical={}) == []


# spec: "**Range** (`>=`, `≥`, `<`, `,<0.18`, \"3.11+\") must contain the file's value."
# task: 9
def test_range_citation_has_a_stale_positive_control(tmp_path):
    root = _repo(tmp_path)
    skill = root / "skills/demo/SKILL.md"
    skill.parent.mkdir()
    skill.write_text("Requires polars>=2.1.\n")
    assert _findings(root, historical={})
    skill.write_text("Requires polars>=2.0.\n")
    assert _findings(root, historical={}) == []


# spec: "**History** (\"ArviZ 0.23\", \"and earlier\") passes only through the `HISTORICAL` allowlist."
# task: 9
def test_history_needs_a_phrase_and_a_reason(tmp_path):
    root = _repo(tmp_path)
    skill = root / "skills/demo/SKILL.md"
    skill.parent.mkdir()
    skill.write_text("ArviZ 0.23 was the classic stack.\n")
    assert _findings(root, historical={})
    assert _findings(
        root, historical={"ArviZ 0.23": "Historical classic-stack guidance"}
    ) == []


# spec: "A live file spells `--python 3.<n>`."
# task: 9
def test_interpreter_literal_has_a_stale_positive_control(tmp_path):
    root = _repo(tmp_path)
    guide = root / "CLAUDE.md"
    guide.write_text("uv run --python 3.12 python script.py\n")
    assert _findings(root, historical={})
    guide.write_text("uv run python script.py\n")
    assert _findings(root, historical={}) == []


# spec: "An interpreter path such as `/usr/bin/python3` is not a literal."
# task: 9
def test_system_python_path_is_allowed(tmp_path):
    root = _repo(tmp_path)
    (root / "CLAUDE.md").write_text("uv run --python /usr/bin/python3 script.py\n")
    assert _findings(root, historical={}) == []


# spec: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
def test_script_and_skill_python_floors_must_match(tmp_path):
    root = _repo(tmp_path)
    skill_dir = root / "skills/demo"
    script_dir = skill_dir / "scripts"
    script_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ncompatibility: Python 3.12+\n---\n"
    )
    script = script_dir / "example.py"
    script.write_text(
        '# /// script\n# requires-python = ">=3.11"\n# ///\n'
    )
    assert _findings(root, historical={})
    script.write_text(
        '# /// script\n# requires-python = ">=3.12"\n# ///\n'
    )
    assert _findings(root, historical={}) == []


# spec: "The dev Python must satisfy each floor."
# task: 9
def test_dev_python_below_a_script_floor_fails(tmp_path):
    root = _repo(tmp_path)
    skill_dir = root / "skills/demo"
    script_dir = skill_dir / "scripts"
    script_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ncompatibility: Python 3.14+\n---\n"
    )
    (script_dir / "example.py").write_text(
        '# /// script\n# requires-python = ">=3.14"\n# ///\n'
    )
    assert _findings(root, historical={})


# spec: "`check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures."
# task: 9
def test_check_skips_dated_records_and_excluded_paths(tmp_path):
    root = _repo(tmp_path)
    for relative in (
        "specs/old.md",
        "LICENSE",
        "data/old.md",
        "build/test_fixture.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Verified on Polars 1.42.\nuv run --python 3.12 x.py\n")
    assert _findings(root, historical={}) == []


# spec: "Use one JAX version for both gates."
# task: 10
def test_both_jax_gates_share_a_pin_or_have_a_reasoned_override():
    v = _build("versions").load(ROOT)
    snippets = next(x for x in v.stack("snippets") if x.startswith("jax=="))
    cpu = next(x for x in v.stack("jax-cpu") if x.startswith("jax=="))
    if snippets != cpu:
        assert any(
            item.gate == "jax-cpu"
            and item.package == "jax"
            and item.reason
            for item in v.overrides
        )
        assert "jax-cpu" in (ROOT / "specs/deferred_items.md").read_text()


# spec: "Pin Polars at the latest release (2.0.0 on 2026-10-21)."
# task: 10
def test_polars_pin_preserves_the_portability_floor():
    v = _build("versions").load(ROOT)
    assert _build("versions").compare(v.packages["polars"], "2.0.0") >= 0


# spec: "For each stale citation, either re-verify the cited behavior on the file's version and update the citation, or move it to `HISTORICAL` with the reason \"verified on X, not re-checked on Y\" and log a deferred item to re-check it."
# task: 11
def test_no_stale_skill_citation_remains():
    findings = _findings(ROOT)
    assert not [finding for finding in findings if "citation" in finding.lower()]


# spec: "Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says \"on the pinned 0.21.0\"."
# task: 12
def test_gaussian_process_deferred_item_no_longer_claims_old_pin():
    text = (ROOT / "specs/deferred_items.md").read_text()
    assert "on the pinned 0.21.0" not in text


# spec: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`."
# task: 12
def test_old_cpu_lock_paths_are_retired():
    assert not (ROOT / "specs/verification/32-jax-cpu.in").exists()
    assert not (ROOT / "specs/verification/32-jax-cpu.txt").exists()
    assert "32-jax-cpu.txt" not in (
        ROOT / "build/check_jax_examples.py"
    ).read_text()


# spec: "Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python."
# task: 12
def test_clean_code_rule_points_to_the_versions_file():
    assert "build/versions.toml" in (
        ROOT / "rules/clean-code-python.md"
    ).read_text()


# spec: "Documented commands spell no interpreter or package version."
# task: 13
def test_documented_uv_commands_have_no_hand_copied_versions():
    paths = [ROOT / name for name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md")]
    paths += list((ROOT / "build").rglob("*.py"))
    paths += list((ROOT / "hooks").rglob("*.md"))
    paths += list((ROOT / "skills").rglob("*.md"))
    for path in paths:
        for line in path.read_text().splitlines():
            if "uv run" not in line:
                continue
            assert not re.search(r"--python\s+3\.\d+", line), (path, line)
            assert not re.search(r"--with\s+['\"]?[\w-]+==\d", line), (
                path, line
            )


# spec: "`build/cc_guide/notice.sh:114` and `build/githooks/pre-commit:15`: they can run outside the repo's working directory, so they take the interpreter from the file and not from a literal."
# task: 13
def test_shell_readers_use_a_synced_interpreter_source():
    for relative in (
        "build/cc_guide/notice.sh",
        "build/githooks/pre-commit",
    ):
        text = (ROOT / relative).read_text()
        assert ".python-version" in text or "versions.toml" in text
        assert not re.search(r"--python\s+3\.\d+", text)


# spec: "`versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`."
# task: 14
def test_versions_check_is_in_commit_lints():
    text = (ROOT / "build/run_commit_lints.sh").read_text()
    assert "versions_check" in text
    assert "uv run python build/versions.py check" in text
    assert re.search(r"\b(?:10|ten)\s+(?:commit\s+)?lints\b", (
        ROOT / "CLAUDE.md"
    ).read_text(), re.IGNORECASE)


# spec: "`.github/workflows/lints.yml` keeps its steps."
# task: 14
def test_lints_workflow_uses_the_synced_python():
    text = (ROOT / ".github/workflows/lints.yml").read_text()
    assert "setup-uv" in text
    assert "run_commit_lints.sh" in text
    assert not re.search(r"python-version:\s*['\"]?3\.\d+", text)


# spec: "It writes the drift report to the job summary."
# task: 15
def test_weekly_drift_workflow_is_advisory_and_read_only():
    text = (ROOT / ".github/workflows/versions-drift.yml").read_text()
    assert "workflow_dispatch:" in text
    assert "schedule:" in text and "cron:" in text
    assert re.search(r"permissions:\s*\n\s+contents:\s*read", text)
    assert "versions.py drift" in text
    assert "GITHUB_STEP_SUMMARY" in text
    assert not re.search(r"contents:\s*write|issues:\s*write|pull-requests:\s*write", text)
    assert not re.search(r"\bgh\s+(?:issue|pr)\s+create\b|\bgit\s+(?:commit|push)\b", text)
    for action in re.findall(r"^\s*uses:\s*(\S+)", text, re.MULTILINE):
        if not action.startswith("./"):
            assert re.search(r"@[0-9a-f]{40}$", action)


# spec: "`CLAUDE.md` has 153 lines against a 200-line budget."
# task: 13
def test_claude_guide_stays_within_its_line_budget():
    assert len((ROOT / "CLAUDE.md").read_text().splitlines()) <= 200


# spec: "`versions.py check` runs offline."
# task: 16
def test_final_versions_check_is_clean_without_network(monkeypatch):
    versions = _build("versions")

    def forbidden(*args, **kwargs):
        raise AssertionError("check attempted a network or process call")

    monkeypatch.setattr(versions, "fetch_json", forbidden)
    monkeypatch.setattr(versions, "run_process", forbidden)
    assert versions.main(["check"], root=ROOT) == 0
    assert _findings(ROOT) == []

</tests>
<flags>
<flag task="6"><spec>Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date.</spec><plan>`check_snippets.API_REMEDIATION` and `RUN_REMEDIATION` as runner commands.</plan></flag>
<flag task="10"><spec>It rewrites `[packages]` from the result and runs `sync`.</spec><plan>Modify: `build/versions.toml` (only when the day changed or JAX needs an override)</plan></flag>
<flag task="12"><spec>Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`.</spec><plan>Move: `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt` to `specs/verification/completed/`</plan></flag>
</flags>
<untestable>
The repo fixes package versions by hand in many places, and nothing ties the copies together.
On 2026-10-21 the owner found NumPyro at 0.21.0 in one deferred item and at 0.22.0 in `PINNED`.
This work is not part of plan 64 (bayesian-workflow and recommend-probabilistic-model routing).
"Version" has four roles here.
They change for different reasons, so the design keeps them apart.
Conflict: the two gates pin different JAX releases.
The CPU lock has 0.11.2 and `PINNED` has 0.12.0.
A floor states when an API appeared.
Conflict: the Polars citations disagree.
explore-data says 1.38, recommend-visualization says 1.42, and three script headers require `polars>=2.0`.
A floating gate would have changed today: jax 0.12.0.1 was uploaded on 2026-10-21.
The cause of the 1.44.2 result is unknown.
The plan must re-check items 2 to 6 before it relies on them.
Nested worktrees: this repo's worktrees live inside the main checkout, at `.claude/worktrees/<name>/`.
So after the change merges, a worktree on a branch that lacks those files inherits the main checkout's freeze date and interpreter, with no sign of it.
A person changes a `[cited]` entry only after re-checking the cited behavior.
A bump follows these steps, in one change:
Run `bump`.
Run `verify`.
Run `check`, which lists each prose citation that the bump made stale.
Re-verify or rewrite each stale citation (R5.5).
Commit.
If a behavior changed, stop and bring the change to the owner before going on.
Write `build/versions.toml`, then run `bump` and `verify` on the day of execution.
The JAX CPU examples must pass on it.
Never change a citation's version without a re-check.
The plan-32 verification records keep their old versions as history.
The plan writes each test before its code (red, then green).
The job may go red, but it is not a required check.
Known limit: GitHub disables scheduled workflows in a public repository after 60 days with no activity.
The spec accepts this.
It does not work around it.
No third-party text enters the repo, so `NOTICE` and the license files do not change.
The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.
This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
The R6 prose fixes rebase onto them and re-take the line numbers.
</untestable>