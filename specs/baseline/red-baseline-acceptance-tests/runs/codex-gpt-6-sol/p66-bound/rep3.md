<tests>
from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
import tomllib
from pathlib import Path

import pytest

from build import check_snippets, run_suites, snippet_preamble, versions, versions_check


ROOT = Path(__file__).resolve().parents[1]

SEED = """\
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


def seed_root(tmp_path: Path) -> Path:
    (tmp_path / "build").mkdir()
    (tmp_path / "build/versions.toml").write_text(SEED, encoding="utf-8")
    versions.sync(tmp_path)
    return tmp_path


def lint_root(tmp_path: Path) -> Path:
    root = seed_root(tmp_path)
    skill = root / "skills/bayesian-workflow"
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: bayesian-workflow\ncompatibility: Python 3.12+\n---\n",
        encoding="utf-8",
    )
    (skill / "scripts/calibration_check.py").write_text(
        '# /// script\n# requires-python = ">=3.12"\n'
        '# dependencies = ["numpy>=2.0"]\n# ///\n',
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root


def findings(root: Path, **kwargs: object) -> list[str]:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    return versions_check.check(root=root, **kwargs)


def stub_uv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, exit_code: int) -> None:
    directory = tmp_path / "bin"
    directory.mkdir(exist_ok=True)
    executable = directory / "uv"
    executable.write_text(f"#!/bin/sh\nexit {exit_code}\n", encoding="utf-8")
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", f"{directory}{os.pathsep}{os.environ['PATH']}")


def metadata(url: str) -> dict:
    pinned = {**versions.parse(SEED).packages, **versions.parse(SEED).cited}
    name = next(
        package
        for package in sorted(pinned, key=len, reverse=True)
        if package in str(url)
    )
    newest = {"jax": "0.12.0.1", "altair": "6.3.0", "plotly": "7.1.0"}
    release = newest.get(name, pinned[name])
    uploaded = "2026-10-21T00:00:00Z"
    file = {"upload_time_iso_8601": uploaded}
    return {
        "info": {"version": release},
        "releases": {release: [file]},
        "urls": [file],
    }


# spec: "Record the results in `specs/verification/`."
# task: 1
def test_uv_probe_record_exists() -> None:
    probe = ROOT / "specs/verification/66-uv-probe.md"
    script = ROOT / "specs/verification/66-uv-probe.py"
    assert probe.is_file()
    assert script.is_file()
    text = probe.read_text(encoding="utf-8")
    for subject in ("skills/uv.toml", "symlink", ".claude/worktrees", ".python-version"):
        assert subject in text


# spec: "Polars is in `[packages]` by the second case: the suites install it, and three headers floor it."
# task: 4
def test_polars_is_pinned() -> None:
    assert "polars" in versions.load(ROOT).packages


# spec: "Other packages (pytest, pyyaml, scipy, tensorstore and the rest) get no entry, and the freeze date fixes them."
# task: 4
def test_unlisted_packages_are_not_pinned() -> None:
    packages = versions.load(ROOT).packages
    assert {"pytest", "pyyaml", "scipy", "tensorstore"}.isdisjoint(packages)


# spec: "A package gets a `[cited]` entry when skill prose cites a version for it and no check runs it."
# task: 4
def test_cited_packages_are_separate_from_gate_pins() -> None:
    v = versions.load(ROOT)
    assert {"altair", "plotly", "optuna", "great-docs"} <= set(v.cited)
    assert set(v.cited).isdisjoint(v.packages)


# spec: "A missing or invalid file names the key."
# task: 2
def test_missing_schema_key_names_itself() -> None:
    missing = SEED.replace("dev = '3.13'\n", "")
    with pytest.raises(versions.VersionsError, match="dev"):
        versions.parse(missing)


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
def test_unknown_gate_package_names_itself() -> None:
    invalid = SEED.replace("'arviz-base',", "'pytest',")
    with pytest.raises(versions.VersionsError, match="pytest"):
        versions.parse(invalid)


# spec: "An invalid date names the value."
# task: 2
def test_invalid_freeze_date_names_itself() -> None:
    invalid = SEED.replace("date = 2026-10-19", "date = '2026-10-32'")
    with pytest.raises(versions.VersionsError, match="2026-10-32"):
        versions.parse(invalid)


# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_stack_applies_only_its_named_override() -> None:
    override = (
        "\n[[override]]\n"
        "gate = 'jax-cpu'\npackage = 'jax'\nversion = '0.11.2'\n"
        "reason = 'The JAX CPU examples must pass on it.'\n"
    )
    v = versions.parse(SEED + override)
    assert "jax==0.12.0" in v.stack("snippets")
    assert "jax==0.11.2" in v.stack("jax-cpu")
    assert "arviz==1.3.0" in v.stack("snippets")
    with pytest.raises(versions.VersionsError, match="reason"):
        versions.parse(SEED + override.replace("reason = 'The JAX CPU examples must pass on it.'\n", ""))


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_synced_output_text(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    output = versions.outputs(versions.load(root))
    assert set(output) == {".python-version", "uv.toml", "skills/uv.toml"}
    assert output[".python-version"] == "3.13\n"
    assert tomllib.loads(output["uv.toml"]) == {
        "exclude-newer": "2026-10-20T00:00:00Z"
    }
    assert tomllib.loads(output["skills/uv.toml"]) == {}
    assert "build/versions.toml" in output["skills/uv.toml"]
    for name, content in output.items():
        assert (root / name).read_text(encoding="utf-8") == content


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_check_detects_a_changed_output(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    assert versions.main(["sync", "--check"], root=root) == 0
    (root / ".python-version").write_text("3.12\n", encoding="utf-8")
    assert versions.main(["sync", "--check"], root=root) != 0


# spec: "With `--only`, the other entries stay at their pins in the joint resolve."
# task: 3
def test_bump_only_keeps_other_requirements_pinned() -> None:
    v = versions.parse(SEED)
    requirements = versions.requirements(v, only=("jax",))
    assert "arviz==1.3.0" in requirements
    assert "polars==2.0.0" in requirements
    assert any(item.startswith("jax") for item in requirements)
    assert "jax==0.12.0" not in requirements


# spec: "`bump` never changes `[cited]`."
# task: 3
def test_bump_jointly_resolves_packages_without_changing_citations(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    original = versions.load(root)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((requirements, python_version, cutoff))
        return {**original.packages, "jax": "0.12.0.1"}

    versions.bump(root, dt.date(2026, 10, 21), resolver=resolver)
    updated = versions.load(root)
    assert len(calls) == 1
    assert calls[0][1] == "3.13"
    assert updated.freeze == dt.date(2026, 10, 21)
    assert updated.packages["jax"] == "0.12.0.1"
    assert updated.cited == original.cited
    assert versions.main(["sync", "--check"], root=root) == 0


# spec: "`bump` exits 2 on a network or resolve failure and names the step."
# task: 3
def test_bump_resolve_failure_exit_code_with_stub_uv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = seed_root(tmp_path)
    stub_uv(tmp_path, monkeypatch, 2)
    assert versions.main(["bump", "--date", "2026-10-21"], root=root) == 2
    output = capsys.readouterr()
    assert "resolve" in (output.out + output.err).lower()


# spec: "`run <gate> [--pin pkg==X ...] -- <cmd>` runs `<cmd>` under `uv run` with the gate's stack and the freeze date."
# task: 5
def test_run_argv_uses_gate_stack_and_utc_cutoff() -> None:
    v = versions.parse(SEED)
    command = ["python", "build/check_snippets.py", "--run", "skills/bayesian-workflow/"]
    argv = versions.uv_run_argv(v, "snippets", command)
    assert argv[0:2] == ["uv", "run"]
    assert "arviz==1.3.0" in argv
    assert "jax==0.12.0" in argv
    assert "2026-10-20T00:00:00Z" in argv
    assert argv[-len(command):] == command


# spec: "`--pin` changes one package for one run and never edits the file."
# task: 5
def test_pin_is_ephemeral(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    path = root / "build/versions.toml"
    before = path.read_text(encoding="utf-8")
    v = versions.load(root)
    pins = versions.parse_pins(v, ["jax==0.11.2"])
    argv = versions.uv_run_argv(v, "jax-cpu", ["python", "build/check_jax_examples.py"], pins=pins)
    assert "jax==0.11.2" in argv
    assert "jax==0.12.0" in v.stack("jax-cpu")
    assert path.read_text(encoding="utf-8") == before
    with pytest.raises(versions.VersionsError, match="pytest"):
        versions.parse_pins(v, ["pytest==1.0"])


# spec: "A pin uploaded after the freeze date names the package and the date."
# task: 5
def test_late_pin_error_names_package_and_date(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = seed_root(tmp_path)
    monkeypatch.setattr(versions, "fetch_json", metadata)
    result = versions.main(
        ["run", "snippets", "--pin", "jax==0.12.0.1", "--", "python", "-c", "pass"],
        root=root,
    )
    output = capsys.readouterr()
    assert result != 0
    assert "jax" in output.out + output.err
    assert "2026-10-21" in output.out + output.err


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 6
def test_snippet_remediation_separates_tier_two_from_tier_three() -> None:
    assert not hasattr(snippet_preamble, "PINNED")
    assert "build/versions.py run snippets" in check_snippets.RUN_REMEDIATION
    assert "--api" in check_snippets.API_REMEDIATION
    assert "run snippets --" not in check_snippets.API_REMEDIATION
    assert not re.search(r"\b(?:arviz|numpyro|jax)==\d", check_snippets.API_REMEDIATION)


# spec: "`build/run_suites.py`: `DEFAULT_PYTHONS` comes from the dev Python."
# task: 7
def test_suite_defaults_come_from_versions_file() -> None:
    v = versions.load(ROOT)
    assert v.dev_python in run_suites.DEFAULT_PYTHONS
    pins = run_suites.Pins.from_versions(v)
    assert pins.python == v.dev_python
    assert pins.spec("polars") == f"polars=={v.packages['polars']}"


# spec: "Each run passes `--exclude-newer <date>` explicitly, because suites under `skills/` sit below the shadow file."
# task: 7
def test_suite_pins_carry_explicit_freeze_date() -> None:
    v = versions.parse(SEED)
    assert run_suites.Pins.from_versions(v).cutoff == "2026-10-20T00:00:00Z"
    assert run_suites.Pins.from_versions(v, freeze=False).cutoff is None
    assert "--exclude-newer" in (ROOT / "build/run_suites.py").read_text(encoding="utf-8")


# spec: "The `hooks` suite keeps its explicit `/usr/bin/python3` run."
# task: 7
def test_hooks_suite_keeps_system_python() -> None:
    text = (ROOT / "build/suites.toml").read_text(encoding="utf-8")
    assert "/usr/bin/python3" in text
    assert "dev" in text


# spec: "`verify [--pin pkg==X ...]` runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`."
# task: 8
def test_verify_has_all_four_gates() -> None:
    steps = versions.verify_steps(versions.parse(SEED))
    assert len(steps) == 4
    assert "--api" in steps[0].argv
    assert "arviz==1.3.0" not in steps[0].argv
    assert "--run" in steps[1].argv
    assert "jax-cpu" in " ".join(steps[2].argv)
    assert "--all" in steps[3].argv
    assert "--extras" in steps[3].argv


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
def test_verify_failure_exit_code_with_stub_uv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = seed_root(tmp_path)
    stub_uv(tmp_path, monkeypatch, 1)
    assert versions.main(["verify"], root=root) != 0


# spec: "For each pass it reports, for each `[packages]` and `[cited]` entry, the pinned version, the resolved version, the newest release and its upload date."
# task: 8
def test_drift_reports_both_python_passes_and_release_dates(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    v = versions.load(root)
    calls = []

    def resolver(requirements, python_version, cutoff):
        calls.append((python_version, cutoff))
        return dict(v.packages)

    status, report = versions.drift(
        root,
        fetch=metadata,
        resolver=resolver,
        newest_python=lambda: "3.14",
        runner=lambda *args: 0,
    )
    assert status == 0
    assert calls == [("3.13", None), ("3.14", None)]
    for item in ("jax", "0.12.0", "0.12.0.1", "2026-10-21", "altair", "plotly"):
        assert item in report
    assert versions.DRIFT_LIMIT in report


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_failure_exit_codes(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    pins = dict(versions.load(root).packages)

    failed_gate, gate_report = versions.drift(
        root,
        fetch=metadata,
        resolver=lambda *args: pins,
        newest_python=lambda: "3.14",
        runner=lambda *args: 1,
    )
    assert failed_gate == 1
    assert "fail" in gate_report.lower()

    def unresolved(*args):
        raise versions.VersionsError("jax conflicts with jaxlib")

    failed_resolve, resolve_report = versions.drift(
        root,
        fetch=metadata,
        resolver=unresolved,
        newest_python=lambda: "3.14",
        runner=lambda *args: 0,
    )
    assert failed_resolve == 2
    assert "jax" in resolve_report
    assert "jaxlib" in resolve_report


# spec: "Sync. An R2.1 output differs from the file."
# task: 9
def test_check_finds_unsynced_output(tmp_path: Path) -> None:
    root = lint_root(tmp_path)
    assert findings(root) == []
    (root / ".python-version").write_text("3.12\n", encoding="utf-8")
    assert any(".python-version" in item for item in findings(root))
    versions.sync(root)
    assert findings(root) == []


# spec: "Equality (\"verified on Polars 1.42\", `numpyro==0.22.0`, \"checked in the 0.22.0\") must equal the file's value at the cited precision."
# task: 9
def test_check_rejects_stale_equality_and_accepts_current_value(tmp_path: Path) -> None:
    root = lint_root(tmp_path)
    path = root / "skills/bayesian-workflow/references/model-comparison.md"
    path.parent.mkdir(parents=True)
    path.write_text("verified on arviz 1.3.0 / arviz-stats 1.3.1\n", encoding="utf-8")
    assert any("arviz-stats" in item for item in findings(root))
    path.write_text("verified on arviz 1.3.0 / arviz-stats 1.3.3\n", encoding="utf-8")
    assert findings(root) == []


# spec: "Range (`>=`, `≥`, `<`, `,<0.18`, \"3.11+\") must contain the file's value."
# task: 9
def test_check_rejects_range_excluding_current_version(tmp_path: Path) -> None:
    root = lint_root(tmp_path)
    path = root / "skills/bayesian-workflow/SKILL.md"
    path.write_text(path.read_text(encoding="utf-8") + "great-docs>=0.18\n", encoding="utf-8")
    assert any("great-docs" in item for item in findings(root))
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "great-docs>=0.18", "great-docs>=0.17.0,<0.18"
        ),
        encoding="utf-8",
    )
    assert findings(root) == []


# spec: "History (\"ArviZ 0.23\", \"and earlier\") passes only through the `HISTORICAL` allowlist."
# task: 9
def test_check_requires_phrase_level_historical_reason(tmp_path: Path) -> None:
    root = lint_root(tmp_path)
    path = root / "skills/bayesian-workflow/SKILL.md"
    path.write_text(path.read_text(encoding="utf-8") + "ArviZ 0.23\n", encoding="utf-8")
    assert any("ArviZ 0.23" in item for item in findings(root, historical={}))
    assert findings(root, historical={"ArviZ 0.23": "History, by design"}) == []


# spec: "Interpreter literals. A live file spells `--python 3.<n>`."
# task: 9
def test_check_rejects_literal_dev_interpreter(tmp_path: Path) -> None:
    root = lint_root(tmp_path)
    path = root / "CLAUDE.md"
    path.write_text("uv run --python 3.13 python build/check_snippets.py\n", encoding="utf-8")
    assert any("CLAUDE.md" in item for item in findings(root))
    path.write_text("uv run python build/check_snippets.py\n", encoding="utf-8")
    assert findings(root) == []


# spec: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
def test_check_rejects_script_and_skill_floor_mismatch(tmp_path: Path) -> None:
    root = lint_root(tmp_path)
    path = root / "skills/bayesian-workflow/scripts/calibration_check.py"
    path.write_text(path.read_text(encoding="utf-8").replace(">=3.12", ">=3.11"), encoding="utf-8")
    assert any("calibration_check.py" in item for item in findings(root))
    path.write_text(path.read_text(encoding="utf-8").replace(">=3.11", ">=3.12"), encoding="utf-8")
    assert findings(root) == []


# spec: "The dev Python must satisfy each floor."
# task: 9
def test_check_rejects_dev_python_below_skill_floor(tmp_path: Path) -> None:
    root = lint_root(tmp_path)
    path = root / "build/versions.toml"
    path.write_text(path.read_text(encoding="utf-8").replace("dev = '3.13'", "dev = '3.11'"), encoding="utf-8")
    versions.sync(root)
    assert any("3.12" in item for item in findings(root))


# spec: "`check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures."
# task: 9
def test_check_skips_dated_records_and_nonlive_files(tmp_path: Path) -> None:
    root = lint_root(tmp_path)
    for relative in (
        "specs/verification/32-deep-learning.md",
        "LICENSE",
        "data/example.md",
        "build/test_check_frontmatter.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Verified on Polars 1.42\n", encoding="utf-8")
    assert findings(root) == []


# spec: "`versions.py check` runs offline."
# task: 9
def test_check_needs_no_network(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = lint_root(tmp_path)

    def network_forbidden(*args, **kwargs):
        pytest.fail("check attempted network access")

    monkeypatch.setattr("urllib.request.urlopen", network_forbidden)
    assert findings(root) == []


# spec: "Use one JAX version for both gates."
# task: 10
def test_jax_gate_versions_match_or_have_documented_override() -> None:
    v = versions.load(ROOT)
    snippets = next(item for item in v.stack("snippets") if item.startswith("jax=="))
    cpu = next(item for item in v.stack("jax-cpu") if item.startswith("jax=="))
    if snippets != cpu:
        assert any(
            item.gate == "jax-cpu"
            and item.package == "jax"
            and item.reason
            for item in v.overrides
        )
        deferred = (ROOT / "specs/deferred_items.md").read_text(encoding="utf-8")
        assert "jax-cpu" in deferred


# spec: "Pin Polars at the latest release (2.0.0 on 2026-10-21)."
# task: 10
def test_polars_pin_preserves_two_point_zero_floor() -> None:
    assert versions.compare(versions.load(ROOT).packages["polars"], "2.0.0") >= 0


# spec: "For each stale citation, either re-verify the cited behavior on the file's version and update the citation, or move it to `HISTORICAL` with the reason \"verified on X, not re-checked on Y\" and log a deferred item to re-check it."
# task: 11
def test_final_tree_has_no_stale_citation_findings() -> None:
    assert versions_check.check(root=ROOT) == []


# spec: "Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says \"on the pinned 0.21.0\"."
# task: 12
def test_gaussian_process_deferred_item_is_corrected() -> None:
    text = (ROOT / "specs/deferred_items.md").read_text(encoding="utf-8")
    assert "on the pinned 0.21.0" not in text


# spec: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`."
# task: 12
def test_jax_cpu_reader_uses_versions_file() -> None:
    assert not (ROOT / "specs/verification/32-jax-cpu.in").exists()
    assert not (ROOT / "specs/verification/32-jax-cpu.txt").exists()
    reader = (ROOT / "build/check_jax_examples.py").read_text(encoding="utf-8")
    assert "32-jax-cpu.txt" not in reader
    assert "jax-cpu" in reader
    assert "32-jax-cpu.txt" not in (ROOT / "CLAUDE.md").read_text(encoding="utf-8")


# spec: "Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python."
# task: 12
def test_clean_code_rule_names_dev_python_source() -> None:
    assert "build/versions.toml" in (
        ROOT / "rules/clean-code-python.md"
    ).read_text(encoding="utf-8")


# spec: "Documented commands spell no interpreter or package version."
# task: 13
def test_documented_commands_have_no_copied_versions() -> None:
    for relative in ("CLAUDE.md", "AGENTS.md", "GEMINI.md", "build/run_commit_lints.sh"):
        for line in (ROOT / relative).read_text(encoding="utf-8").splitlines():
            if "uv run" in line:
                assert not re.search(r"--python\s+3\.\d+", line), (relative, line)
                assert not re.search(
                    r"\b(?:arviz|numpyro|jax|polars)(?:==|>=)\d", line
                ), (relative, line)


# spec: "`build/cc_guide/notice.sh:114` and `build/githooks/pre-commit:15`: they can run outside the repo's working directory, so they take the interpreter from the file and not from a literal."
# task: 13
def test_notice_and_hook_read_interpreter_source() -> None:
    for relative in ("build/cc_guide/notice.sh", "build/githooks/pre-commit"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert ".python-version" in text or "build/versions.toml" in text
        assert not re.search(r"--python\s+3\.\d+", text)


# spec: "`versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`."
# task: 14
def test_versions_check_is_tenth_commit_lint() -> None:
    runner = (ROOT / "build/run_commit_lints.sh").read_text(encoding="utf-8")
    assert "versions_check" in runner
    assert "build/versions.py check" in runner
    assert "versions_check" in (ROOT / "build/test_commit_lints.py").read_text(encoding="utf-8")
    assert "versions_check" in (ROOT / "build/githooks/pre-commit").read_text(encoding="utf-8")


# spec: "`.github/workflows/lints.yml` keeps its steps."
# task: 14
def test_lints_workflow_uses_synced_python_file() -> None:
    workflow = (ROOT / ".github/workflows/lints.yml").read_text(encoding="utf-8")
    assert "setup-uv" in workflow
    assert ".python-version" in workflow
    assert not re.search(r"python-version:\s*['\"]?3\.\d+", workflow)


# spec: "A new workflow, `.github/workflows/versions-drift.yml`, runs `versions.py drift` weekly on a cron schedule and on manual dispatch."
# task: 15
def test_advisory_drift_workflow_has_both_triggers() -> None:
    workflow = (ROOT / ".github/workflows/versions-drift.yml").read_text(encoding="utf-8")
    assert "schedule:" in workflow
    assert "cron:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "versions.py drift" in workflow


# spec: "It has `permissions: contents: read`, and it pins its actions by SHA, as `lints.yml` does."
# task: 15
def test_advisory_workflow_has_read_only_permissions_and_pinned_actions() -> None:
    workflow = (ROOT / ".github/workflows/versions-drift.yml").read_text(encoding="utf-8")
    assert re.search(r"permissions:\s*\n\s+contents:\s*read", workflow)
    uses = re.findall(r"^\s*uses:\s*([^\s#]+)", workflow, flags=re.MULTILINE)
    assert uses
    assert all(re.search(r"@[0-9a-f]{40}$", action) for action in uses)


# spec: "It writes the drift report to the job summary."
# task: 15
def test_advisory_workflow_reports_without_writing_to_repo() -> None:
    workflow = (ROOT / ".github/workflows/versions-drift.yml").read_text(encoding="utf-8")
    assert "GITHUB_STEP_SUMMARY" in workflow
    assert not re.search(r"\bgh\s+(?:issue|pr)\s+create\b", workflow)
    assert not re.search(r"\bgit\s+(?:commit|push)\b", workflow)
</tests>
<flags>
<flag task="5"><spec>uv compares the date with the upload time of each file, not of the release.</spec><plan>`late_pins(v, specs, fetch=None) -> list[str]` (the specs whose release was first uploaded at or after the cutoff)</plan></flag>
<flag task="12"><spec>Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`.</spec><plan>Move: `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt` to `specs/verification/completed/`</plan></flag>
</flags>
<untestable>
On 2026-10-21 the owner found NumPyro at 0.21.0 in one deferred item and at 0.22.0 in `PINNED`.
This work is not part of plan 64 (bayesian-workflow and recommend-probabilistic-model routing).
A floor states when an API appeared.
The cause of the 1.44.2 result is unknown.
The plan must re-check items 2 to 6 before it relies on them.
A person changes a `[cited]` entry only after re-checking the cited behavior.
If a behavior changed, stop and bring the change to the owner before going on.
The JAX CPU examples must pass on it.
Never change a citation's version without a re-check.
The job may go red, but it is not a required check.
Known limit: GitHub disables scheduled workflows in a public repository after 60 days with no activity.
The spec accepts this.
The plan writes each test before its code (red, then green).
No third-party text enters the repo, so `NOTICE` and the license files do not change.
The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.
This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
The R6 prose fixes rebase onto them and re-take the line numbers.
</untestable>