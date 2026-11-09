<tests>
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import yaml

from build import check_frontmatter as frontmatter
from build import check_provenance as provenance


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "skills").is_dir())

SCRIPT_PATHS = {
    "skills/bayesian-workflow/scripts/calibration_check.py",
    "skills/bayesian-workflow/scripts/check_diagnostics.py",
    "skills/bayesian-workflow/scripts/diagnose_model.py",
    "skills/describe-critique-methodology/scripts/check_decoupling.py",
    "skills/design-architecture/scripts/new_adr.py",
    "skills/explore-data/scripts/profile.py",
    "skills/llm-wiki/scripts/bootstrap_wiki.py",
    "skills/llm-wiki/scripts/distill_sessions.py",
    "skills/llm-wiki/scripts/distill_specs.py",
    "skills/llm-wiki/scripts/lint_wiki.py",
    "skills/recommend-probabilistic-model/scripts/characterize.py",
    "skills/recommend-visualization/scripts/recommend.py",
    "skills/track-model-experiments/scripts/compare_experiments.py",
    "skills/writing-plans/scripts/deferred_stats.py",
    "skills/classification-codes/scripts/build.py",
    "skills/geographic-codes/scripts/build.py",
}

FALLBACK_SENTENCE = (
    "Without uv, run the same path with `python3` in an environment "
    "that has the dependencies listed in the script's header."
)


def skills():
    return sorted(path for path in (ROOT / "skills").iterdir() if (path / "SKILL.md").is_file())


def skill_frontmatter(skill_dir):
    lines = (skill_dir / "SKILL.md").read_text().splitlines()
    assert lines[0] == "---"
    closing = lines.index("---", 1)
    return yaml.safe_load("\n".join(lines[1:closing]))


def write_skill(skill_dir, fields, body="Body.\n"):
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n" + yaml.safe_dump(fields, sort_keys=False) + "---\n" + body
    )


def base_fields(name="example"):
    return {"name": name, "description": "Use when testing an example skill.", "license": "MIT"}


def run_command(*args, cwd=ROOT):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=180)


# spec: "Replace `ALLOWED_KEYS` with two named sets and allow their union in a `SKILL.md`:"
# task: 3
def test_frontmatter_key_sets():
    assert frontmatter.SPEC_KEYS == frozenset(
        {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    )
    assert frontmatter.HOST_KEYS == frozenset(
        {"when_to_use", "model", "effort", "context", "disable-model-invocation"}
    )
    assert not hasattr(frontmatter, "ALLOWED_KEYS")


# spec: "When present, a mapping whose keys and values are all strings."
# task: 3
def test_metadata_value_shape(tmp_path):
    sk = tmp_path / "SKILL.md"
    for value in ({}, {"author": "Someone"}, {"": ""}):
        assert not frontmatter._check_value_shapes(sk, {**base_fields(), "metadata": value})
    for value in ([], "author", {1: "Someone"}, {"author": 1}):
        assert frontmatter._check_value_shapes(sk, {**base_fields(), "metadata": value})


# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
def test_compatibility_value_shape(tmp_path):
    sk = tmp_path / "SKILL.md"
    for value in ("x", " " + "x" * 500 + " "):
        assert not frontmatter._check_value_shapes(sk, {**base_fields(), "compatibility": value})
    for value in ("", " \t ", "x" * 501, 500):
        assert frontmatter._check_value_shapes(sk, {**base_fields(), "compatibility": value})


# spec: "`name` and `description` contain no `<` or `>`."
# task: 3
def test_angle_brackets_are_rejected(tmp_path):
    sk = tmp_path / "SKILL.md"
    for field, value in (
        ("name", "verify<page>"),
        ("name", "verify>page"),
        ("description", "Use when verifying <page>."),
        ("description", "Use when verifying >page."),
    ):
        assert frontmatter._check_value_shapes(sk, {**base_fields(), field: value})


# spec: "Fix llm-wiki's trigger phrase `'verify <page>'` to `'verify a page'`."
# task: 3
def test_llm_wiki_trigger_phrase():
    description = skill_frontmatter(ROOT / "skills/llm-wiki")["description"]
    assert "verify a page" in description
    assert "verify <page>" not in description


# spec: "Required in every `SKILL.md`, a non-empty string (repo policy, beyond the spec)."
# task: 4
def test_license_is_required(tmp_path):
    sk = tmp_path / "SKILL.md"
    assert not frontmatter._check_license(sk, base_fields())
    for value in (None, "", "   ", 5):
        fields = base_fields()
        if value is None:
            del fields["license"]
        else:
            fields["license"] = value
        assert frontmatter._check_license(sk, fields)
    assert all(isinstance(skill_frontmatter(skill)["license"], str) for skill in skills())


# spec: "The 13 superpowers skills gain `license: MIT` and"
# task: 4
def test_superpowers_frontmatter():
    adapted = [
        skill_frontmatter(skill)
        for skill in skills()
        if skill_frontmatter(skill).get("metadata", {}).get("source")
        == "https://github.com/obra/superpowers"
    ]
    assert len(adapted) == 13
    for fields in adapted:
        assert fields["license"] == "MIT"
        assert fields["metadata"] == {
            "author": "Jesse Vincent",
            "adapted_by": "Lowell Mason",
            "source": "https://github.com/obra/superpowers",
        }


# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
def test_disable_model_invocation_is_boolean(tmp_path):
    skill_dir = tmp_path / "example"
    skill_dir.mkdir()
    for value in ("true", "false", 1, None):
        assert frontmatter._check_invocation_parity(
            skill_dir, {**base_fields(), "disable-model-invocation": value}
        )
    assert not frontmatter._check_invocation_parity(
        skill_dir, {**base_fields(), "disable-model-invocation": False}
    )


# spec: "A skill with `disable-model-invocation: true` must ship `agents/openai.yaml` that parses and sets `policy.allow_implicit_invocation: false`."
# task: 5
def test_true_disable_model_invocation_requires_codex_policy(tmp_path):
    skill_dir = tmp_path / "example"
    agents = skill_dir / "agents"
    agents.mkdir(parents=True)
    fields = {**base_fields(), "disable-model-invocation": True}
    assert frontmatter._check_invocation_parity(skill_dir, fields)
    policy = agents / "openai.yaml"
    policy.write_text("policy: [\n")
    assert frontmatter._check_invocation_parity(skill_dir, fields)
    policy.write_text("policy:\n  allow_implicit_invocation: true\n")
    assert frontmatter._check_invocation_parity(skill_dir, fields)
    policy.write_text("policy:\n  allow_implicit_invocation: false\n")
    assert not frontmatter._check_invocation_parity(skill_dir, fields)


# spec: "Conversely, a skill whose `agents/openai.yaml` sets that policy to `false` must set `disable-model-invocation: true`."
# task: 5
def test_false_codex_policy_requires_disable_model_invocation(tmp_path):
    skill_dir = tmp_path / "example"
    agents = skill_dir / "agents"
    agents.mkdir(parents=True)
    (agents / "openai.yaml").write_text("policy:\n  allow_implicit_invocation: false\n")
    assert frontmatter._check_invocation_parity(skill_dir, base_fields())
    assert frontmatter._check_invocation_parity(
        skill_dir, {**base_fields(), "disable-model-invocation": False}
    )
    assert not frontmatter._check_invocation_parity(
        skill_dir, {**base_fields(), "disable-model-invocation": True}
    )


# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
def test_body_length_boundary(tmp_path):
    skill_dir = tmp_path / "example"
    write_skill(skill_dir, base_fields(), "line\n" * 500)
    assert frontmatter.skill_body_warning(skill_dir) is None
    write_skill(skill_dir, base_fields(), "line\n" * 501)
    assert frontmatter.skill_body_warning(skill_dir) is not None


# spec: "When Stage A adds this warning, it also adds a `skill-body-size` `[[check]]` to `build/cc_guide/conformance.toml` that maps `skills.overview` to it, with `enforced_by = 'check_frontmatter'` (conformance R6 P3)."
# task: 6
def test_body_size_conformance_register():
    register = tomllib.loads((ROOT / "build/cc_guide/conformance.toml").read_text())
    assert any(
        "skill-body-size" in str(check)
        and "skills.overview" in str(check)
        and check.get("enforced_by") == "check_frontmatter"
        for check in register["check"]
    )


# spec: "Expected result today: exactly `bayesian-workflow`, `tune-hyperparameters`, and `tech-debt` fail."
# task: 7
def test_strict_profile_has_exact_current_failures():
    failing = {skill.name for skill in skills() if frontmatter.strict_violations(skill)}
    assert failing == {"bayesian-workflow", "tune-hyperparameters", "tech-debt"}


# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
def test_strict_profile_rejects_host_keys_and_reserved_names(tmp_path):
    for name in ("claude-helper", "anthropic-helper"):
        skill_dir = tmp_path / name
        write_skill(skill_dir, base_fields(name))
        assert frontmatter.strict_violations(skill_dir)
    skill_dir = tmp_path / "host-extension"
    write_skill(skill_dir, {**base_fields("host-extension"), "effort": "low"})
    assert frontmatter.strict_violations(skill_dir)


# spec: "The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, \"Conformance register\")."
# task: 7
def test_strict_profile_documentation():
    assert "--strict" in (frontmatter.__doc__ or "")
    claude = (ROOT / "CLAUDE.md").read_text()
    commands = re.search(
        r"(?ms)^#{1,6}\s+Commands\s*$([\s\S]*?)(?=^#{1,6}\s+|\Z)", claude
    )
    assert commands is not None
    assert re.search(r"check_frontmatter\.py[^\n]*--strict", commands.group(1))
    assert "claude.ai" in commands.group(1) or "spec-only" in commands.group(1)
    assert len(claude.splitlines()) <= 200


# spec: "Record the scenario, prompts, outputs, and verdicts in `specs/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house red-baseline format."
# task: 2
def test_red_baseline_artifact_exists():
    reports = sorted(
        (ROOT / "specs").glob("red-baseline-description-openings-????-??-??.md")
    )
    assert reports
    report = reports[-1].read_text()
    for term in ("scenario", "prompt", "output", "verdict"):
        assert re.search(rf"\b{term}s?\b", report, re.IGNORECASE)


# spec: "The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list)."
# task: 14
def test_writing_skills_has_measured_codex_note():
    text = (ROOT / "skills/writing-skills/SKILL.md").read_text()
    assert "Token Efficiency" in text
    section = text.split("Token Efficiency", 1)[1].split("\n## ", 1)[0]
    for term in ("Codex", "156", "164", "93", "0.154", "2026-10-03",
                 "codex debug prompt-input"):
        assert term in section
    assert re.search(r"outside (?:any |a )?repo", section, re.IGNORECASE)


# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
def test_runnable_script_inventory():
    found = {
        Path(path).resolve().relative_to(ROOT).as_posix()
        for skill in skills()
        for path in frontmatter.runnable_scripts(skill)
    }
    assert found == SCRIPT_PATHS
    library = ROOT / "skills/tune-hyperparameters/scripts/time_series_cv.py"
    assert "__main__" not in library.read_text()
    assert "# /// script" not in library.read_text()


# spec: "Line 1 is `#!/usr/bin/env python3`; add it where missing."
# task: 10
def test_runnable_script_shebangs():
    for relative in SCRIPT_PATHS:
        assert (ROOT / relative).read_text().splitlines()[0] == "#!/usr/bin/env python3"


# spec: "Then a `# /// script` block with single-quoted TOML strings, a `requires-python`, and a `dependencies` list (`[]` for stdlib-only scripts)."
# task: 10
def test_runnable_script_pep723_headers():
    for relative in SCRIPT_PATHS:
        text = (ROOT / relative).read_text()
        metadata = frontmatter.script_metadata(text)
        assert isinstance(metadata, dict), relative
        assert metadata["requires-python"] in {">=3.11", ">=3.12", ">=3.13"}
        assert isinstance(metadata["dependencies"], list)
        assert re.search(r"(?m)^# /// script$", text)
        assert re.search(r"(?m)^# requires-python = '>=[^']+'$", text)
        assert re.search(r"(?m)^# dependencies = \[", text)
        for dependency in metadata["dependencies"]:
            assert f"'{dependency}'" in text
            assert re.search(r">=\d+", dependency)
            assert not any(operator in dependency for operator in ("<", "==", "~="))


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_script_header_lint_passes_repository():
    assert all(not frontmatter.check_script_headers(skill) for skill in skills())


# spec: "Every third-party import, including function-level imports, is declared with a `>=` floor at the major version the suite currently resolves (e.g. `'polars>=1.0'`)."
# task: 10
def test_script_header_lint_finds_function_imports(tmp_path):
    skill_dir = tmp_path / "skills/example"
    scripts = skill_dir / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "helper.py").write_text("VALUE = 1\n")
    script = scripts / "run.py"
    source = (
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
        "# dependencies = []\n"
        "# ///\n"
        "def main():\n"
        "    import yaml\n"
        "    import helper\n"
        "    try:\n"
        "        import numpy\n"
        "    except ImportError:\n"
        "        pass\n"
        "if __name__ == '__main__':\n"
        "    main()\n"
    )
    script.write_text(source)
    assert frontmatter.check_script_headers(skill_dir)
    script.write_text(source.replace(
        "# dependencies = []", "# dependencies = ['pyyaml>=6.0']"
    ))
    assert not frontmatter.check_script_headers(skill_dir)


# spec: "No skill markdown invokes a resolving bundled-script path with bare `python` or `python3`, including line-continued forms (`python \\` followed by the path on the next line)."
# task: 11
def test_invocation_lint_detects_continued_bare_python(tmp_path):
    skill_dir = tmp_path / "skills/example"
    write_skill(skill_dir, base_fields())
    scripts = skill_dir / "scripts"
    scripts.mkdir()
    (scripts / "run.py").write_text("if __name__ == '__main__':\n    pass\n")
    example = skill_dir / "example.md"
    example.write_text("python \\\n<this-skill-dir>/scripts/run.py\n")
    assert frontmatter.check_invocations(skill_dir)
    example.write_text("uv run <this-skill-dir>/scripts/run.py\n")
    assert not frontmatter.check_invocations(skill_dir)


# spec: "A path that does not resolve to a bundled script, such as `writing-skills/anthropic-best-practices.md`'s teaching example `scripts/migrate.py`, is not flagged."
# task: 11
def test_invocation_lint_ignores_teaching_example(tmp_path):
    skill_dir = tmp_path / "skills/example"
    write_skill(skill_dir, base_fields())
    (skill_dir / "example.md").write_text("python scripts/migrate.py\n")
    assert not frontmatter.check_invocations(skill_dir)


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
def test_documented_bundled_invocations_use_uv_run():
    for skill in skills():
        assert not frontmatter.check_invocations(skill), skill.name
        for _, runner, _ in frontmatter.bundled_invocations(skill):
            assert runner == "uv run", skill.name


# spec: "Each skill with such an invocation gets this sentence once, near its first invocation: \"Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.\""
# task: 11
def test_each_invoking_skill_has_one_python_fallback_sentence():
    for skill in skills():
        if frontmatter.bundled_invocations(skill):
            text = "\n".join(path.read_text() for path in skill.rglob("*.md"))
            assert text.count(FALLBACK_SENTENCE) == 1, skill.name


# spec: "Every skill whose markdown runs a bundled script with `uv run` declares `compatibility: Requires uv to run bundled scripts (dependencies are declared inline); Python 3.X+.`"
# task: 12
def test_compatibility_matches_invoked_script_floor():
    invoking = set()
    for skill in skills():
        invocations = frontmatter.bundled_invocations(skill)
        if not invocations:
            continue
        invoking.add(skill.name)
        floors = []
        for _, runner, path in invocations:
            if runner != "uv run":
                continue
            resolved = frontmatter.resolve_bundled_script(path, skill)
            assert resolved is not None, (skill.name, path)
            floor = frontmatter.script_metadata(resolved.read_text())["requires-python"]
            floors.append(int(floor.rsplit(".", 1)[1]))
        assert floors, skill.name
        expected = (
            "Requires uv to run bundled scripts (dependencies are declared inline); "
            f"Python 3.{max(floors)}+."
        )
        assert skill_frontmatter(skill)["compatibility"] == expected
        assert not frontmatter._check_compatibility_names_uv(
            skill, skill_frontmatter(skill)
        )
    assert "finishing-a-development-branch" in invoking


# spec: "Prose floors that disagree with the header are aligned or removed (e.g. \"Python ≥ 3.9\" in `recommend-probabilistic-model` and `recommend-visualization`)."
# task: 12
def test_old_python_prose_floors_are_removed_or_aligned():
    for name in ("recommend-probabilistic-model", "recommend-visualization"):
        text = (ROOT / "skills" / name / "SKILL.md").read_text()
        assert "Python ≥ 3.9" not in text


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_bundled_license_copies_pass_provenance_lint():
    names = [skill.name for skill in skills()]
    assert provenance.PLAIN_LICENSE == "LICENSE"
    assert not provenance.bundled_license_violations(
        ROOT, names, provenance.BUNDLED_LICENSES
    )
    for skill in skills():
        copy = skill / "LICENSE"
        assert copy.is_file() and not copy.is_symlink()
        assert copy.read_bytes() == (ROOT / "LICENSE").read_bytes()


# spec: "No skill directory holds a `LICENSE*` file outside its mapping."
# task: 8
def test_bundled_license_lint_rejects_missing_changed_linked_and_extra_files(tmp_path):
    repo = tmp_path
    root_license = repo / "LICENSE"
    root_license.write_bytes(b"root license\n")
    extra_license = repo / "LICENSE-extra"
    extra_license.write_bytes(b"extra license\n")
    first = repo / "skills/first"
    second = repo / "skills/second"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    (first / "LICENSE").write_bytes(root_license.read_bytes())
    (second / "LICENSE").write_bytes(root_license.read_bytes())
    (first / "LICENSE-extra").write_bytes(extra_license.read_bytes())
    table = {"LICENSE-extra": ("first",)}

    def violations():
        return provenance.bundled_license_violations(
            repo, ["first", "second"], table
        )

    assert not violations()
    (second / "LICENSE").unlink()
    assert violations()
    (second / "LICENSE").write_bytes(b"changed\n")
    assert violations()
    (second / "LICENSE").unlink()
    (second / "LICENSE").symlink_to(root_license)
    assert violations()
    (second / "LICENSE").unlink()
    (second / "LICENSE").write_bytes(root_license.read_bytes())
    (second / "LICENSE-extra").write_bytes(extra_license.read_bytes())
    assert violations()


# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
def test_unmapped_root_license_is_rejected(tmp_path):
    repo = tmp_path
    (repo / "LICENSE").write_bytes(b"MIT\n")
    (repo / "LICENSE-unmapped").write_bytes(b"other\n")
    skill = repo / "skills/example"
    skill.mkdir(parents=True)
    (skill / "LICENSE").write_bytes(b"MIT\n")
    assert provenance.bundled_license_violations(repo, ["example"], {})


# spec: "`LICENSE-coding-skills` | `bayesian-workflow`, `clean-code` | NOTICE records *adapted* Mancuso Lab content (`references/jax-numerics.md`, `references/modules.md`). `tech-debt` took \"only the idea\" and gets no copy |"
# task: 8
def test_coding_skills_license_mapping():
    assert set(provenance.BUNDLED_LICENSES["LICENSE-coding-skills"]) == {
        "bayesian-workflow", "clean-code"
    }
    assert len(provenance.BUNDLED_LICENSES["LICENSE-superpowers"]) == 13


# spec: "`LICENSE-andorra` | `bayesian-workflow` | only if R4.5 finds an upstream notice |"
# task: 9
def test_andorra_license_copy_is_conditional():
    root = ROOT / "LICENSE-andorra"
    table = provenance.BUNDLED_LICENSES
    if root.exists():
        assert table["LICENSE-andorra"] == ("bayesian-workflow",)
        copy = ROOT / "skills/bayesian-workflow/LICENSE-andorra"
        assert copy.is_file() and not copy.is_symlink()
        assert copy.read_bytes() == root.read_bytes()
    else:
        assert "LICENSE-andorra" not in table
        assert not (ROOT / "skills/bayesian-workflow/LICENSE-andorra").exists()


# spec: "NOTICE gains one paragraph near the top: each skill directory carries copies of the license texts that apply to it, so a single-skill install (`install.py --copy --skill`, or a third-party installer) keeps the notice MIT requires."
# task: 8
def test_license_travel_is_documented():
    notice = (ROOT / "NOTICE").read_text()
    readme = (ROOT / "README.md").read_text()
    claude = (ROOT / "CLAUDE.md").read_text()
    assert "install.py --copy --skill" in notice
    assert "check_provenance.py" in notice
    assert "LICENSE" in readme.split("License", 1)[1]
    assert "check_provenance.py" in claude
    assert "license" in claude.lower()


# spec: "`check_frontmatter.py` (exit 0; the only `WARN` is `writing-skills`' body length)"
# task: 15
def test_default_frontmatter_gate_and_sole_warning():
    result = run_command(sys.executable, "build/check_frontmatter.py")
    assert result.returncode == 0, result.stdout + result.stderr
    warnings = [line for line in result.stderr.splitlines() if "WARN" in line]
    assert len(warnings) == 1
    assert "writing-skills" in warnings[0]


# spec: "`check_provenance.py`"
# task: 15
def test_provenance_gate():
    result = run_command(sys.executable, "build/check_provenance.py")
    assert result.returncode == 0, result.stdout + result.stderr


# spec: "`check_snippets.py skills/` (Tier 1)"
# task: 15
def test_snippet_gate():
    result = run_command(sys.executable, "build/check_snippets.py", "skills/")
    assert result.returncode == 0, result.stdout + result.stderr


# spec: "`sync_runtime_assets.py --check` (no adapter change is expected)"
# task: 15
def test_runtime_asset_sync_gate():
    result = run_command(sys.executable, "build/sync_runtime_assets.py", "--check")
    assert result.returncode == 0, result.stdout + result.stderr


# spec: "When Stage A or Stage D fixes a gap the register tracks to it, the same change removes or narrows that `[[exception]]` and runs `build/check_conformance.py` (R6 P2)."
# task: 15
def test_conformance_register_gate():
    result = run_command(sys.executable, "build/check_conformance.py")
    assert result.returncode == 0, result.stdout + result.stderr


# spec: "`check_frontmatter.py --strict` fails on exactly `bayesian-workflow`, `tune-hyperparameters`, and `tech-debt`."
# task: 15
def test_strict_cli_fails():
    result = run_command(sys.executable, "build/check_frontmatter.py", "--strict")
    assert result.returncode != 0
    output = result.stdout + result.stderr
    for name in ("bayesian-workflow", "tune-hyperparameters", "tech-debt"):
        assert name in output


# spec: "`gemini skills list --all` shows every skill under `skills/` as `[Enabled]`;"
# task: 15
def test_gemini_loads_every_skill_from_outside_a_repo():
    assert shutil.which("gemini"), "Gemini CLI is required for this acceptance check"
    with tempfile.TemporaryDirectory(prefix="portability-gemini-") as scratch:
        result = run_command("gemini", "skills", "list", "--all", cwd=scratch)
    assert result.returncode == 0, result.stdout + result.stderr
    lines = result.stdout.splitlines()
    for skill in skills():
        assert any(skill.name in line and "[Enabled]" in line for line in lines), skill.name


# spec: "`codex debug prompt-input` lists every skill under `skills/` by name."
# task: 15
def test_codex_loads_every_skill_from_outside_a_repo():
    assert shutil.which("codex"), "Codex CLI is required for this acceptance check"
    with tempfile.TemporaryDirectory(prefix="portability-codex-") as scratch:
        result = run_command("codex", "debug", "prompt-input", cwd=scratch)
    assert result.returncode == 0, result.stdout + result.stderr
    output = result.stdout + result.stderr
    for skill in skills():
        assert skill.name in output, skill.name
</tests>
<flags>
<flag task="1"><spec>**Status: APPROVED (2026-10-18).** The owner approved the design on 2026-10-03 and the written spec on 2026-10-18.</spec><plan>Produces: a spec whose counts and rules match Tasks 2–15.</plan></flag>
<flag task="7"><spec>CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").</spec><plan>Modify: `CLAUDE.md` (Commands: the frontmatter lint's comment names `--strict`; no line added, D7)</plan></flag>
<flag task="8"><spec>No skill directory holds a `LICENSE*` file outside its mapping.</spec><plan>Rename: `skills/recommend-causal-design/LICENSE` to `skills/recommend-causal-design/LICENSE-causal-design-sources`, and re-point its links in that skill's `SKILL.md`, `README.md` and `references/sources.md`</plan></flag>
<flag task="9"><spec>`LICENSE-andorra` | `bayesian-workflow` | only if R4.5 finds an upstream notice |</spec><plan>Create: `LICENSE-andorra` (upstream's text, verbatim) and its copy `skills/bayesian-workflow/LICENSE-andorra`</plan></flag>
<flag task="10"><spec>Fourteen gain a header:</spec><plan>Modify: the 15 header-less runnable scripts (helper script): a shebang where missing, then the header</plan></flag>
</flags>
<untestable>
All 32 descriptions pass as of 2026-10-03.
5 reps, each a fresh agent given the current `writing-skills` description guidance (the control: no new wording).
Run from a session whose cwd was never this repo.
A rep passes if the designated primary trigger lies within the first 150 characters.
The controller reads each output and records the verbatim 150-character prefix.
Use the lowest of `'>=3.11'`, `'>=3.12'`, `'>=3.13'` under which the test suite covering the script passes, run with `uv run --python 3.X` and that suite's CLAUDE.md dependencies.
Scripts covered by one suite share its floor, unless a failure is attributable to one script, which then alone takes the higher floor.
Runtime backends that the script never imports but needs to read its inputs (e.g. `h5netcdf` for NetCDF) are added when R3.8's fixture run shows them needed.
From an empty scratch directory (a subdirectory such as `/tmp/bwprobe/`, never `/tmp` itself), each of the 16 scripts runs `uv run <absolute-path>` on a minimal real input that exercises its main code path.
`--help` alone is enough only for a script with no input-reading path.
The three ArviZ-reading scripts (`diagnose_model.py`, `calibration_check.py`, `compare_experiments.py`) each read a small saved InferenceData fixture.
One script is also run from inside a directory holding an unrelated `pyproject.toml`.
The dependency-drift check still passes.
Locate Alexandre Andorra's original PyMC Bayesian-workflow skill and read its license.
Never compose a copyright line that is not quoted from the source.
Whichever branch merges second brings the other's skills into conformance in the same merge, or the new lints fail on arrival.
State test changes as +N deltas against the suite, never absolute totals.
Before allocating the plan id, check `specs/plans/` on every branch (`git ls-tree`); ids are allocated per branch and have collided.
</untestable>