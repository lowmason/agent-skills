<tests>
```python
import datetime
import re
import tomllib
from pathlib import Path

import pytest

from build import check_snippets, run_suites, snippet_preamble, versions, versions_check


ROOT = Path(versions.REPO)

SAMPLE = """
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


def _root(tmp_path, source=SAMPLE):
    (tmp_path / "build").mkdir()
    (tmp_path / "skills").mkdir()
    (tmp_path / "build" / "versions.toml").write_text(source)
    versions.sync(tmp_path)
    return tmp_path


def _skill(root, body, name="example"):
    folder = root / "skills" / name
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "SKILL.md"
    path.write_text(body)
    return path


# spec: "An unknown package in `[gates]` or `[[override]]` names the package."
# task: 2
def test_unknown_gate_and_override_packages_name_the_package():
    bad_gate = SAMPLE.replace("snippets = [", "snippets = ['ghost-package', ")
    with pytest.raises(versions.VersionsError, match="ghost-package"):
        versions.parse(bad_gate)

    bad_override = SAMPLE + """
[[override]]
gate = 'jax-cpu'
package = 'ghost-package'
version = '0.11.2'
reason = 'CPU compatibility'
"""
    with pytest.raises(versions.VersionsError, match="ghost-package"):
        versions.parse(bad_override)


# spec: "An invalid date names the value."
# task: 2
def test_invalid_freeze_date_names_its_value():
    source = SAMPLE.replace("date = 2026-10-19", "date = 'not-a-date'")
    with pytest.raises(versions.VersionsError, match="not-a-date"):
        versions.parse(source)


# spec: "A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`."
# task: 2
def test_stack_uses_shared_pin_unless_a_reasoned_override_exists():
    ordinary = versions.parse(SAMPLE)
    assert "jax==0.12.0" in ordinary.stack("snippets")
    assert "jax==0.12.0" in ordinary.stack("jax-cpu")

    overridden = versions.parse(
        SAMPLE
        + """
[[override]]
gate = 'jax-cpu'
package = 'jax'
version = '0.11.2'
reason = 'CPU examples require the older release'
"""
    )
    assert "jax==0.12.0" in overridden.stack("snippets")
    assert "jax==0.11.2" in overridden.stack("jax-cpu")


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_writes_the_three_native_uv_files(tmp_path):
    root = _root(tmp_path)
    assert (root / ".python-version").read_text().strip() == "3.13"

    uv_text = (root / "uv.toml").read_text()
    assert "2026-10-20T00:00:00Z" in uv_text
    assert "exclude-newer" in tomllib.loads(uv_text)

    shadow = (root / "skills" / "uv.toml").read_text()
    assert "build/versions.toml" in shadow
    assert all(
        not line.strip() or line.lstrip().startswith("#")
        for line in shadow.splitlines()
    )


# spec: "`build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:"
# task: 2
def test_sync_check_detects_each_stale_output(tmp_path):
    root = _root(tmp_path)
    assert versions.main(["sync", "--check"], root=root) == 0

    for relative_path in (".python-version", "uv.toml", "skills/uv.toml"):
        path = root / relative_path
        original = path.read_text()
        path.write_text(original + "\n# stale\n")
        assert versions.main(["sync", "--check"], root=root) != 0
        path.write_text(original)


# spec: "Polars is in `[packages]` by the second case: the suites install it, and three headers floor it."
# task: 4
def test_real_versions_file_lists_gate_packages_and_polars():
    v = versions.load(ROOT)
    expected_gates = {
        "snippets": {
            "arviz", "arviz-base", "arviz-stats", "arviz-plots",
            "numpyro", "jax", "numpy", "matplotlib",
        },
        "jax-cpu": {
            "jax", "jaxlib", "flax", "optax", "orbax-checkpoint",
            "equinox", "diffrax", "e3nn-jax", "numpy",
        },
    }
    assert {name: set(packages) for name, packages in v.gates.items()} == expected_gates
    assert set().union(*expected_gates.values(), {"polars"}) <= set(v.packages)
    assert {"pytest", "pyyaml", "scipy", "tensorstore"}.isdisjoint(v.packages)
    assert {"altair", "plotly", "optuna", "great-docs"} <= set(v.cited)


# spec: "With `--only`, the other entries stay at their pins in the joint resolve"
# task: 3
def test_only_keeps_other_packages_pinned_in_joint_requirements():
    v = versions.parse(SAMPLE)
    requirements = versions.requirements(v, only=("polars",))
    assert "jax==0.12.0" in requirements
    assert any(item.startswith("polars") and item != "polars==2.0.0"
               for item in requirements)


# spec: "`bump` never changes `[cited]`."
# task: 3
def test_bump_updates_packages_and_sync_but_preserves_cited(tmp_path):
    initial = SAMPLE.replace("polars = '2.0.0'", "polars = '1.42'")
    root = _root(tmp_path, initial)
    before = versions.load(root)
    seen = []

    def resolver(requirements, python_version, cutoff):
        seen.append((requirements, python_version, cutoff))
        result = dict(before.packages)
        result["polars"] = "2.0.0"
        return result

    versions.bump(
        root,
        datetime.date(2026, 10, 21),
        only=("polars",),
        resolver=resolver,
    )
    after = versions.load(root)
    assert seen
    assert after.packages["polars"] == "2.0.0"
    assert after.cited == before.cited
    assert after.freeze == datetime.date(2026, 10, 21)
    assert "2026-10-22T00:00:00Z" in (root / "uv.toml").read_text()


# spec: "`bump` exits 2 on a network or resolve failure and names the step."
# task: 3
def test_bump_reports_resolve_failure_with_exit_two(tmp_path, monkeypatch, capsys):
    root = _root(tmp_path)

    def failed_resolve(*args, **kwargs):
        raise OSError("stub uv unavailable")

    monkeypatch.setattr(versions, "resolve", failed_resolve)
    assert versions.main(["bump", "--date", "2026-10-21"], root=root) == 2
    report = capsys.readouterr()
    assert re.search(r"resolv|uv unavailable", report.out + report.err, re.I)


# spec: "`run <gate> [--pin pkg==X ...] -- <cmd>` runs `<cmd>` under `uv run` with the gate's stack and the freeze date"
# task: 5
def test_run_argv_contains_the_gate_stack_and_utc_cutoff():
    v = versions.parse(SAMPLE)
    argv = versions.uv_run_argv(
        v, "snippets", ["python", "build/check_snippets.py", "--run"]
    )
    assert argv[0:2] == ["uv", "run"]
    assert "--exclude-newer" in argv
    assert v.cutoff in argv
    assert all(requirement in argv for requirement in v.stack("snippets"))


# spec: "`--pin` changes one package for one run and never edits the file."
# task: 5
def test_pin_changes_the_run_stack_without_editing_versions(tmp_path):
    root = _root(tmp_path)
    path = root / "build" / "versions.toml"
    before = path.read_bytes()
    v = versions.load(root)

    pins = versions.parse_pins(v, ["jax==0.11.2"])
    argv = versions.uv_run_argv(v, "snippets", ["python", "-c", "pass"], pins=pins)

    assert "jax==0.11.2" in argv
    assert "jax==0.12.0" not in argv
    assert path.read_bytes() == before
    with pytest.raises(versions.VersionsError, match="ghost-package"):
        versions.parse_pins(v, ["ghost-package==1.0"])


# spec: "A pin uploaded after the freeze date names the package and the date."
# task: 5
def test_late_pin_is_identified_from_upload_time():
    v = versions.parse(SAMPLE)
    upload = {"upload_time_iso_8601": "2026-10-21T00:00:00Z"}

    def fetch(_url):
        return {
            "urls": [upload],
            "releases": {"0.12.0.1": [upload]},
        }

    late = versions.late_pins(v, ["jax==0.12.0.1"], fetch=fetch)
    assert any("jax" in item for item in late)


# spec: "Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date."
# task: 6
def test_api_remediation_has_no_exact_package_pins():
    assert "--api" in check_snippets.API_REMEDIATION
    assert not re.search(r"\b[a-z][a-z0-9-]*==\d", check_snippets.API_REMEDIATION)
    assert "build/versions.py run snippets" in check_snippets.RUN_REMEDIATION
    assert not hasattr(snippet_preamble, "PINNED")


# spec: "`build/run_suites.py`: `DEFAULT_PYTHONS` comes from the dev Python."
# task: 7
def test_suite_pins_read_the_dev_python_and_named_packages():
    v = versions.parse(SAMPLE)
    pins = run_suites.Pins.from_versions(v)
    assert pins.python == v.dev_python
    assert pins.cutoff == v.cutoff
    assert pins.spec("polars") == "polars==2.0.0"
    assert pins.spec("pytest") == "pytest"


# spec: "The `hooks` suite keeps its explicit `/usr/bin/python3` run."
# task: 7
def test_hooks_suite_retains_system_python():
    source = (ROOT / "build" / "suites.toml").read_text()
    assert "/usr/bin/python3" in source


# spec: "Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras`"
# task: 8
def test_verify_steps_cover_all_four_gates():
    steps = versions.verify_steps(versions.parse(SAMPLE))
    assert [step.label for step in steps] == [
        "tier 2 (--api)",
        "tier 3 (--run)",
        "jax cpu examples",
        "suites",
    ]
    assert not any("32-jax-cpu.txt" in part
                   for step in steps for part in step.argv)
    assert "--all" in steps[-1].argv
    assert "--extras" in steps[-1].argv


# spec: "`run` and `verify` exit non-zero on any failure."
# task: 8
def test_verify_fails_when_a_stubbed_command_fails(tmp_path, monkeypatch):
    root = _root(tmp_path)
    monkeypatch.setattr(versions, "run_process", lambda *args, **kwargs: 1)
    monkeypatch.setattr(versions, "late_pins", lambda *args, **kwargs: [])
    assert versions.main(["verify"], root=root) != 0


# spec: "`drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network."
# task: 8
def test_drift_exit_codes_with_stubbed_network_and_commands(tmp_path):
    root = _root(tmp_path)
    v = versions.load(root)
    current = {**v.packages, **v.cited}

    def resolver(*args, **kwargs):
        return current

    def fetch(url):
        names = [name for name in current if f"/{name}/" in url]
        name = names[0] if names else "jax"
        release = current[name]
        return {
            "info": {"version": release},
            "releases": {
                release: [{"upload_time_iso_8601": "2026-10-19T00:00:00Z"}]
            },
        }

    common = {
        "fetch": fetch,
        "resolver": resolver,
        "newest_python": lambda: "3.14",
    }
    code, report = versions.drift(
        root, runner=lambda *args, **kwargs: 0, **common
    )
    assert code == 0
    assert "3.13" in report and "3.14" in report
    assert versions.DRIFT_LIMIT in report

    code, report = versions.drift(
        root, runner=lambda *args, **kwargs: 1, **common
    )
    assert code == 1
    assert re.search(r"fail", report, re.I)

    def failed_resolver(*args, **kwargs):
        raise OSError("stub network unavailable")

    code, report = versions.drift(
        root,
        fetch=fetch,
        resolver=failed_resolver,
        newest_python=lambda: "3.14",
        runner=lambda *args, **kwargs: 0,
    )
    assert code == 2
    assert re.search(r"network|resolv", report, re.I)


# spec: "**Equality** (\"verified on Polars 1.42\", `numpyro==0.22.0`, \"checked in the 0.22.0\") must equal the file's value at the cited precision."
# task: 9
def test_equality_citation_has_a_stale_positive_control(tmp_path):
    root = _root(tmp_path)
    path = _skill(root, "Verified on Polars 1.42.\n")
    assert any("Polars" in item or "polars" in item
               for item in versions_check.check(root))

    path.write_text("Verified on Polars 2.0.\n")
    assert versions_check.check(root) == []


# spec: "**Range** (`>=`, `≥`, `<`, `,<0.18`, \"3.11+\") must contain the file's value."
# task: 9
def test_range_citation_has_a_stale_positive_control(tmp_path):
    root = _root(tmp_path)
    path = _skill(root, "Requires polars>=2.0.\n")
    assert versions_check.check(root) == []

    source = (root / "build" / "versions.toml").read_text()
    (root / "build" / "versions.toml").write_text(
        source.replace("polars = '2.0.0'", "polars = '1.42'")
    )
    versions.sync(root)
    assert any("polars" in item.lower()
               for item in versions_check.check(root))


# spec: "**History** (\"ArviZ 0.23\", \"and earlier\") passes only through the `HISTORICAL` allowlist."
# task: 9
def test_history_requires_a_phrase_with_a_reason(tmp_path):
    root = _root(tmp_path)
    _skill(root, "ArviZ 0.23 was the classic stack.\n")
    assert "ArviZ 0.23" in versions_check.HISTORICAL
    assert versions_check.HISTORICAL["ArviZ 0.23"]
    assert versions_check.check(root) == []
    assert any("ArviZ 0.23" in item
               for item in versions_check.check(root, historical={}))


# spec: "A live file spells `--python 3.<n>`."
# task: 9
def test_interpreter_literal_fails_but_system_python_path_passes(tmp_path):
    root = _root(tmp_path)
    path = root / "CLAUDE.md"
    path.write_text("Run `uv run --python 3.13 python build/check_snippets.py`.\n")
    assert any("CLAUDE.md" in item for item in versions_check.check(root))

    path.write_text("Run `/usr/bin/python3 install.py`.\n")
    assert versions_check.check(root) == []


# spec: "Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line."
# task: 9
def test_script_and_skill_python_floors_must_match(tmp_path):
    root = _root(tmp_path)
    skill = _skill(
        root,
        "---\nname: example\ncompatibility: Python 3.11+\n---\n",
    )
    script = skill.parent / "scripts" / "example.py"
    script.parent.mkdir()
    script.write_text(
        '# /// script\n# requires-python = ">=3.12"\n# ///\n'
    )
    assert any("Python" in item or "python" in item
               for item in versions_check.check(root))

    skill.write_text(
        "---\nname: example\ncompatibility: Python 3.12+\n---\n"
    )
    assert versions_check.check(root) == []


# spec: "The dev Python must satisfy each floor."
# task: 9
def test_dev_python_below_a_matching_floor_fails(tmp_path):
    root = _root(tmp_path)
    skill = _skill(
        root,
        "---\nname: example\ncompatibility: Python 3.14+\n---\n",
    )
    script = skill.parent / "scripts" / "example.py"
    script.parent.mkdir()
    script.write_text(
        '# /// script\n# requires-python = ">=3.14"\n# ///\n'
    )
    assert any("3.13" in item or "3.14" in item
               for item in versions_check.check(root))


# spec: "`check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures."
# task: 9
def test_check_ignores_dated_records_license_and_data(tmp_path):
    root = _root(tmp_path)
    (root / "specs").mkdir()
    (root / "data").mkdir()
    (root / "specs" / "deferred_items.md").write_text(
        "Verified on Polars 1.42. Use --python 3.12.\n"
    )
    (root / "LICENSE-notes").write_text("Verified on Polars 1.42.\n")
    (root / "data" / "notes.md").write_text("Verified on Polars 1.42.\n")
    assert versions_check.check(root) == []


# spec: "Re-probe the uv behaviors in the Inventory (items 2 to 6, the shadow file under `skills/`, and nested-worktree inheritance) on the uv version of the day."
# task: 1
def test_uv_reprobe_has_a_script_and_recorded_results():
    script = ROOT / "specs" / "verification" / "66-uv-probe.py"
    report = ROOT / "specs" / "verification" / "66-uv-probe.md"
    assert script.is_file() and report.is_file()
    text = report.read_text().lower()
    for subject in (
        "uv version", "exclude-newer", "script", "symlink",
        "skills/uv.toml", ".python-version", "worktree",
    ):
        assert subject in text


# spec: "Use one JAX version for both gates."
# task: 10
def test_jax_gate_pins_agree_unless_reasoned_override_exists():
    v = versions.load(ROOT)
    snippets = next(item for item in v.stack("snippets")
                    if item.startswith("jax=="))
    cpu = next(item for item in v.stack("jax-cpu")
               if item.startswith("jax=="))
    if snippets != cpu:
        overrides = [
            item for item in v.overrides
            if item.gate == "jax-cpu" and item.package == "jax"
        ]
        assert len(overrides) == 1
        assert overrides[0].reason.strip()
        assert "jax-cpu" in (ROOT / "specs" / "deferred_items.md").read_text()


# spec: "This keeps the `polars>=2.0` floors that the portability plan set on purpose (`specs/plans/completed/53-agent-skills-portability.md`, decision DF4)."
# task: 10
def test_polars_pin_satisfies_the_intentional_floor():
    v = versions.load(ROOT)
    assert versions.compare(v.packages["polars"], "2.0.0") >= 0


# spec: "Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says \"on the pinned 0.21.0\"."
# task: 12
def test_gaussian_process_item_no_longer_calls_numpyro_021_pinned():
    text = (ROOT / "specs" / "deferred_items.md").read_text()
    assert "on the pinned 0.21.0" not in text


# spec: "Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`."
# task: 12
def test_active_jax_lock_is_retired_and_readers_name_versions_file():
    folder = ROOT / "specs" / "verification"
    assert not (folder / "32-jax-cpu.in").exists()
    assert not (folder / "32-jax-cpu.txt").exists()
    for name in ("32-deep-learning.md", "32-jax-integration.md"):
        assert "build/versions.toml" in (folder / name).read_text()


# spec: "Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python."
# task: 12
def test_python_rule_names_the_versions_source():
    text = (ROOT / "rules" / "clean-code-python.md").read_text()
    assert "build/versions.toml" in text


# spec: "Documented commands spell no interpreter or package version."
# task: 13
def test_documented_uv_commands_have_no_copied_versions():
    paths = [
        ROOT / "CLAUDE.md",
        ROOT / "AGENTS.md",
        ROOT / "GEMINI.md",
        ROOT / "build" / "run_commit_lints.sh",
        *(ROOT / "build").rglob("*.py"),
        *(ROOT / "hooks").rglob("*.md"),
        *(ROOT / "skills").rglob("*.md"),
    ]
    command_lines = [
        line
        for path in paths
        if path.is_file()
        for line in path.read_text(errors="replace").splitlines()
        if "uv run" in line
    ]
    text = "\n".join(command_lines)
    assert not re.search(r"--python\s+3\.\d+", text)
    assert not re.search(r"\b[a-z][a-z0-9-]*==\d", text)


# spec: "`build/cc_guide/notice.sh:114` and `build/githooks/pre-commit:15`: they can run outside the repo's working directory, so they take the interpreter from the file and not from a literal."
# task: 13
def test_hooks_and_notice_reference_the_versions_source():
    for relative_path in (
        "build/cc_guide/notice.sh",
        "build/githooks/pre-commit",
    ):
        text = (ROOT / relative_path).read_text()
        assert not re.search(r"--python\s+3\.\d+", text)
        assert any(name in text for name in (
            ".python-version", "versions.toml", "versions.py"
        ))


# spec: "`versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`."
# task: 14
def test_tenth_commit_lint_invokes_versions_check():
    script = (ROOT / "build" / "run_commit_lints.sh").read_text()
    assert "versions_check" in script
    assert "uv run python build/versions.py check" in script
    assert versions.main(["check"], root=ROOT) == 0


# spec: "`setup-uv` takes the interpreter from `.python-version`."
# task: 14
def test_lints_workflow_reads_python_version_file():
    text = (ROOT / ".github" / "workflows" / "lints.yml").read_text()
    assert "setup-uv" in text
    assert re.search(r"python-version-file:\s*['\"]?\.python-version", text)


# spec: "A new workflow, `.github/workflows/versions-drift.yml`, runs `versions.py drift` weekly on a cron schedule and on manual dispatch."
# task: 15
def test_drift_workflow_is_weekly_and_manually_dispatchable():
    text = (ROOT / ".github" / "workflows" / "versions-drift.yml").read_text()
    assert "workflow_dispatch:" in text
    assert re.search(r"cron:\s*['\"]?\d+\s+\d+\s+\*\s+\*\s+[0-7]", text)
    assert "versions.py drift" in text


# spec: "It has `permissions: contents: read`, and it pins its actions by SHA, as `lints.yml` does."
# task: 15
def test_drift_workflow_has_read_permission_and_sha_pinned_actions():
    text = (ROOT / ".github" / "workflows" / "versions-drift.yml").read_text()
    assert re.search(r"permissions:\s*\n\s+contents:\s*read", text)
    actions = re.findall(r"\buses:\s*[^@\s]+@([^\s#]+)", text)
    assert actions
    assert all(re.fullmatch(r"[0-9a-f]{40}", revision) for revision in actions)


# spec: "It writes the drift report to the job summary."
# task: 15
def test_drift_workflow_writes_the_job_summary():
    text = (ROOT / ".github" / "workflows" / "versions-drift.yml").read_text()
    assert "GITHUB_STEP_SUMMARY" in text


# spec: "It never opens an issue or a PR, and it never commits."
# task: 15
def test_drift_workflow_has_no_repository_writes():
    text = (ROOT / ".github" / "workflows" / "versions-drift.yml").read_text()
    assert not re.search(
        r"\bgh\s+(?:issue|pr)\s+create\b|\bgit\s+(?:commit|push)\b|contents:\s*write",
        text,
    )
```
</tests>
<flags>
<flag task="6"><spec>Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date.</spec><plan>`check_snippets.API_REMEDIATION` and `RUN_REMEDIATION` as runner commands.</plan></flag>
<flag task="12"><spec>Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`.</spec><plan>Move: `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt` to `specs/verification/completed/`</plan></flag>
<flag task="14"><spec>`setup-uv` takes the interpreter from `.python-version`.</spec><plan>Modify: `build/test_commit_lints.py`, `build/run_commit_lints.sh`, `build/githooks/pre-commit`, `CLAUDE.md`, `build/CLAUDE.md`</plan></flag>
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
The plan confirms that Claude Code, Codex and Gemini also ignore a plain file in a skills directory.
The values above are the 2026-10-21 state.
The plan sets the real values with `bump` (R3).
A person changes a `[cited]` entry only after re-checking the cited behavior.
Run `bump`.
Run `verify`.
Run `check`, which lists each prose citation that the bump made stale.
Re-verify or rewrite each stale citation (R5.5).
Commit.
If a behavior changed, stop and bring the change to the owner before going on.
The JAX CPU examples must pass on it.
If they fail, add a temporary `[[override]]` for `jax-cpu` with its reason, and log a deferred item to remove it.
Pin Polars at the latest release (2.0.0 on 2026-10-21).
For each stale citation, either re-verify the cited behavior on the file's version and update the citation, or move it to `HISTORICAL` with the reason "verified on X, not re-checked on Y" and log a deferred item to re-check it.
Never change a citation's version without a re-check.
The plan-32 verification records keep their old versions as history.
The job may go red, but it is not a required check.
Known limit: GitHub disables scheduled workflows in a public repository after 60 days with no activity.
The spec accepts this.
It does not work around it.
The plan writes each test before its code (red, then green).
No third-party text enters the repo, so `NOTICE` and the license files do not change.
The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.
This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
The R6 prose fixes rebase onto them and re-take the line numbers.
`CLAUDE.md` has 153 lines against a 200-line budget.
</untestable>