<tests>
import ast
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

from build import check_frontmatter as frontmatter
from build import check_provenance as provenance


ROOT = Path(frontmatter.__file__).resolve().parents[1]
FALLBACK = (
    "Without uv, run the same path with `python3` in an environment "
    "that has the dependencies listed in the script's header."
)


def skill_dirs():
    return sorted(
        path for path in (ROOT / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def read_frontmatter(skill_dir):
    text = (skill_dir / "SKILL.md").read_text()
    assert text.startswith("---\n")
    return yaml.safe_load(text[4:].split("\n---", 1)[0])


def scratch_skill(tmp_path, name="example", extra=None, body="Body\n"):
    skill_dir = tmp_path / "skills" / name
    skill_dir.mkdir(parents=True)
    fields = {
        "name": name,
        "description": "Use when exercising a temporary skill.",
        "license": "MIT",
    }
    fields.update(extra or {})
    (skill_dir / "SKILL.md").write_text(
        "---\n" + yaml.safe_dump(fields, sort_keys=False) + "---\n" + body
    )
    return skill_dir


def runnable_paths():
    return {
        path.resolve()
        for skill_dir in skill_dirs()
        for path in frontmatter.runnable_scripts(skill_dir)
    }


def run_gate(*args):
    result = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr


# spec: "Replace `ALLOWED_KEYS` with two named sets and allow their union in a `SKILL.md`:"
# task: 3
def test_frontmatter_key_sets():
    assert frontmatter.SPEC_KEYS == {
        "name", "description", "license", "compatibility",
        "metadata", "allowed-tools",
    }
    assert frontmatter.HOST_KEYS == {
        "when_to_use", "model", "effort", "context",
        "disable-model-invocation",
    }
    assert not hasattr(frontmatter, "ALLOWED_KEYS")


# spec: "When present, a mapping whose keys and values are all strings."
# task: 3
def test_metadata_shape(tmp_path):
    skill = scratch_skill(tmp_path) / "SKILL.md"
    check = frontmatter._check_value_shapes
    assert check(skill, {"metadata": {"author": "Jesse Vincent"}}) == []
    for value in (None, [], "author", {1: "author"}, {"author": 1}):
        assert check(skill, {"metadata": value})


# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
def test_compatibility_shape(tmp_path):
    skill = scratch_skill(tmp_path) / "SKILL.md"
    check = frontmatter._check_value_shapes
    assert frontmatter.COMPATIBILITY_CAP == 500
    assert check(skill, {"compatibility": " " + "x" * 500 + " "}) == []
    for value in ("", " \t ", "x" * 501, 123, ["uv"]):
        assert check(skill, {"compatibility": value})


# spec: "`name` and `description` contain no `<` or `>`."
# task: 3
def test_angle_brackets_and_llm_wiki_wording(tmp_path):
    skill = scratch_skill(tmp_path) / "SKILL.md"
    for field in ("name", "description"):
        for bracket in ("<", ">"):
            assert frontmatter._check_value_shapes(skill, {field: f"a{bracket}b"})
    llm_wiki = (ROOT / "skills/llm-wiki/SKILL.md").read_text()
    assert "'verify <page>'" not in llm_wiki
    assert "'verify a page'" in llm_wiki


# spec: "Required in every `SKILL.md`, a non-empty string (repo policy, beyond the spec)."
# task: 4
def test_license_field(tmp_path):
    skill = scratch_skill(tmp_path) / "SKILL.md"
    assert frontmatter._check_license(skill, {"license": "MIT"}) == []
    for fields in ({}, {"license": ""}, {"license": None}, {"license": 1}):
        assert frontmatter._check_license(skill, fields)
    for skill_dir in skill_dirs():
        value = read_frontmatter(skill_dir).get("license")
        assert isinstance(value, str) and value


# spec: "The 13 superpowers skills gain `license: MIT` and metadata: author: 'Jesse Vincent' adapted_by: 'Lowell Mason' source: 'https://github.com/obra/superpowers' mirroring `bayesian-workflow`'s existing `author` / `adapted_by` pattern."
# task: 4
def test_superpowers_frontmatter():
    superpowers = [
        skill_dir for skill_dir in skill_dirs()
        if (skill_dir / "LICENSE-superpowers").exists()
    ]
    assert len(superpowers) == 13
    for skill_dir in superpowers:
        fields = read_frontmatter(skill_dir)
        assert fields["license"] == "MIT"
        assert fields["metadata"] == {
            "author": "Jesse Vincent",
            "adapted_by": "Lowell Mason",
            "source": "https://github.com/obra/superpowers",
        }


# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
def test_invocation_parity_and_boolean_shape(tmp_path):
    skill_dir = scratch_skill(tmp_path)
    check = frontmatter._check_invocation_parity
    assert check(skill_dir, {"disable-model-invocation": "true"})
    assert check(skill_dir, {"disable-model-invocation": True})
    policy = skill_dir / frontmatter.CODEX_POLICY
    policy.parent.mkdir(parents=True)
    policy.write_text("policy:\n  allow_implicit_invocation: false\n")
    assert check(skill_dir, {"disable-model-invocation": True}) == []
    assert check(skill_dir, {"disable-model-invocation": False})
    assert check(skill_dir, {})
    policy.write_text("policy: [\n")
    assert check(skill_dir, {"disable-model-invocation": True})


# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
def test_body_length_advisory(tmp_path, capsys):
    skill_dir = scratch_skill(tmp_path, body="x\n" * 500)
    assert frontmatter.skill_body_warning(skill_dir) is None
    (skill_dir / "SKILL.md").write_text(
        (skill_dir / "SKILL.md").read_text() + "x\n"
    )
    assert "WARN" in frontmatter.skill_body_warning(skill_dir)
    assert frontmatter.main([]) == 0
    warnings = [
        line for line in capsys.readouterr().err.splitlines()
        if "WARN" in line
    ]
    assert len(warnings) == 1
    assert "writing-skills" in warnings[0]


# spec: "When Stage A adds this warning, it also adds a `skill-body-size` `[[check]]` to `build/cc_guide/conformance.toml` that maps `skills.overview` to it, with `enforced_by = 'check_frontmatter'` (conformance R6 P3)."
# task: 6
def test_body_size_conformance_register():
    register = tomllib.loads(
        (ROOT / "build/cc_guide/conformance.toml").read_text()
    )
    matches = [
        row for row in register["check"]
        if "skill-body-size" in str(row)
    ]
    assert len(matches) == 1
    assert "skills.overview" in str(matches[0])
    assert matches[0]["enforced_by"] == "check_frontmatter"


# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
def test_strict_profile(tmp_path):
    for name in ("claude-example", "anthropic-example"):
        assert frontmatter.strict_violations(scratch_skill(tmp_path, name))
    assert frontmatter.strict_violations(
        scratch_skill(tmp_path, "host-example", {"effort": "high"})
    )
    offenders = {
        skill_dir.name for skill_dir in skill_dirs()
        if frontmatter.strict_violations(skill_dir)
    }
    assert offenders == {
        "bayesian-workflow", "tune-hyperparameters", "tech-debt",
    }
    assert frontmatter.main(["--strict"]) != 0


# spec: "The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, \"Conformance register\")."
# task: 7
def test_strict_documentation_and_claude_size():
    assert "--strict" in frontmatter.__doc__
    claude = (ROOT / "CLAUDE.md").read_text()
    commands = claude.split("## Commands", 1)[1].split("\n## ", 1)[0]
    assert "check_frontmatter.py --strict" in commands
    assert "claude.ai" in commands
    assert "spec-only" in commands
    assert len(claude.splitlines()) <= 200


# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
def test_runnable_script_inventory():
    expected = {
        "bayesian-workflow/scripts/calibration_check.py",
        "bayesian-workflow/scripts/check_diagnostics.py",
        "bayesian-workflow/scripts/diagnose_model.py",
        "describe-critique-methodology/scripts/check_decoupling.py",
        "design-architecture/scripts/new_adr.py",
        "explore-data/scripts/profile.py",
        "llm-wiki/scripts/bootstrap_wiki.py",
        "llm-wiki/scripts/distill_sessions.py",
        "llm-wiki/scripts/distill_specs.py",
        "llm-wiki/scripts/lint_wiki.py",
        "recommend-probabilistic-model/scripts/characterize.py",
        "recommend-visualization/scripts/recommend.py",
        "track-model-experiments/scripts/compare_experiments.py",
        "writing-plans/scripts/deferred_stats.py",
        "classification-codes/scripts/build.py",
        "geographic-codes/scripts/build.py",
    }
    actual = {
        path.relative_to(ROOT / "skills").as_posix()
        for path in runnable_paths()
    }
    assert actual == expected
    library = ROOT / "skills/tune-hyperparameters/scripts/time_series_cv.py"
    assert not frontmatter.MAIN_GUARD_RE.search(library.read_text())


# spec: "Line 1 is `#!/usr/bin/env python3`; add it where missing."
# task: 10
def test_runnable_script_header_form():
    for path in runnable_paths():
        text = path.read_text()
        assert text.splitlines()[0] == "#!/usr/bin/env python3"
        assert re.search(r"^# /// script$", text, re.MULTILINE)
        metadata = frontmatter.script_metadata(text)
        assert metadata is not None
        assert metadata["requires-python"] in {
            ">=3.11", ">=3.12", ">=3.13",
        }
        assert isinstance(metadata["dependencies"], list)
        block = text.split("# /// script", 1)[1].split("# ///", 1)[0]
        assert '"' not in block
        for dependency in metadata["dependencies"]:
            assert isinstance(dependency, str)
            assert ">=" in dependency
            assert not re.search(r"(?<!>)<|==|!=", dependency)


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_script_header_lint_rejects_missing_and_invalid_metadata(tmp_path):
    skill_dir = scratch_skill(tmp_path)
    scripts = skill_dir / "scripts"
    scripts.mkdir()
    script = scripts / "demo.py"
    main = 'if __name__ == "__main__":\n    print("ok")\n'
    script.write_text(main)
    assert frontmatter.check_script_headers(skill_dir)

    invalid = (
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
        "# dependencies = ['broken'\n"
        "# ///\n" + main
    )
    with pytest.raises(tomllib.TOMLDecodeError):
        frontmatter.script_metadata(invalid)
    script.write_text(invalid)
    assert frontmatter.check_script_headers(skill_dir)

    valid = (
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
        "# dependencies = []\n"
        "# ///\n" + main
    )
    script.write_text(valid)
    assert frontmatter.check_script_headers(skill_dir) == []


# spec: "In such a script, every non-stdlib, non-local import is declared in `dependencies`:"
# task: 10
def test_import_lint_includes_nested_imports_and_exempts_optional_imports():
    tree = ast.parse(
        "import pathlib\n"
        "from json import loads\n"
        "from local_module import helper\n"
        "def run():\n"
        "    import yaml\n"
        "    try:\n"
        "        import polars\n"
        "    except (ImportError, ModuleNotFoundError):\n"
        "        pass\n"
    )
    assert frontmatter.required_imports(tree, {"local_module"}) == {"pyyaml"}


# spec: "A path that does not resolve to a bundled script, such as `writing-skills/anthropic-best-practices.md`'s teaching example `scripts/migrate.py`, is not flagged."
# task: 11
def test_bundled_script_path_resolution():
    llm_wiki = ROOT / "skills/llm-wiki"
    lint = (llm_wiki / "scripts/lint_wiki.py").resolve()
    assert frontmatter.resolve_bundled_script(
        "<this-skill-dir>/scripts/lint_wiki.py", llm_wiki
    ) == lint
    assert frontmatter.resolve_bundled_script(
        "$LLM_WIKI_ROOT/scripts/lint_wiki.py", llm_wiki
    ) == lint
    assert frontmatter.resolve_bundled_script(
        "~/Projects/agent-skills/skills/llm-wiki/scripts/lint_wiki.py",
        llm_wiki,
    ) == lint
    finishing = ROOT / "skills/finishing-a-development-branch"
    assert frontmatter.resolve_bundled_script(
        "<this-skill-dir>/../writing-plans/scripts/deferred_stats.py",
        finishing,
    ) == (ROOT / "skills/writing-plans/scripts/deferred_stats.py").resolve()
    assert frontmatter.resolve_bundled_script(
        "skills/classification-codes/scripts/build.py",
        ROOT / "skills/classification-codes",
    ) == (ROOT / "skills/classification-codes/scripts/build.py").resolve()
    assert frontmatter.resolve_bundled_script(
        "scripts/migrate.py", ROOT / "skills/writing-skills"
    ) is None


# spec: "No skill markdown invokes a resolving bundled-script path with bare `python` or `python3`, including line-continued forms (`python \\` followed by the path on the next line)."
# task: 11
def test_invocation_lint_detects_bare_runners_and_continuations(tmp_path):
    skill_dir = scratch_skill(tmp_path)
    script = skill_dir / "scripts/demo.py"
    script.parent.mkdir()
    script.write_text('if __name__ == "__main__":\n    print("ok")\n')
    original = (skill_dir / "SKILL.md").read_text()
    (skill_dir / "SKILL.md").write_text(
        original
        + "\npython3 <this-skill-dir>/scripts/demo.py\n"
        + "python \\\n<this-skill-dir>/scripts/demo.py\n"
    )
    assert frontmatter.check_invocations(skill_dir)
    (skill_dir / "SKILL.md").write_text(
        original + "\npython scripts/migrate.py\n"
    )
    assert frontmatter.check_invocations(skill_dir) == []


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
def test_all_documented_bundled_invocations_and_fallbacks():
    invoking = set()
    for skill_dir in skill_dirs():
        invocations = frontmatter.bundled_invocations(skill_dir)
        assert frontmatter.check_invocations(skill_dir) == []
        if not invocations:
            continue
        invoking.add(skill_dir.name)
        assert all(runner == "uv run" for _, runner, _ in invocations)
        occurrences = sum(
            path.read_text().count(FALLBACK)
            for path in skill_dir.rglob("*.md")
        )
        assert occurrences == 1
    assert "finishing-a-development-branch" in invoking


# spec: "Every skill whose markdown runs a bundled script with `uv run` declares `compatibility: Requires uv to run bundled scripts (dependencies are declared inline); Python 3.X+.`"
# task: 12
def test_compatibility_matches_highest_invoked_python_floor():
    for skill_dir in skill_dirs():
        invocations = [
            item for item in frontmatter.bundled_invocations(skill_dir)
            if item[1] == "uv run"
        ]
        fields = read_frontmatter(skill_dir)
        assert frontmatter._check_compatibility_names_uv(
            skill_dir, fields
        ) == []
        if not invocations:
            continue
        floors = []
        for _, _, path_text in invocations:
            script = frontmatter.resolve_bundled_script(
                path_text, skill_dir
            )
            assert script is not None
            metadata = frontmatter.script_metadata(script.read_text())
            floors.append(metadata["requires-python"].removeprefix(">="))
        highest = max(floors, key=lambda value: tuple(map(int, value.split("."))))
        assert fields["compatibility"] == (
            "Requires uv to run bundled scripts "
            "(dependencies are declared inline); "
            f"Python {highest}+."
        )


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_bundled_license_copies_and_mapping():
    table = provenance.BUNDLED_LICENSES
    assert provenance.PLAIN_LICENSE == "LICENSE"
    assert set(table) in (
        {"LICENSE-superpowers", "LICENSE-coding-skills"},
        {"LICENSE-superpowers", "LICENSE-coding-skills", "LICENSE-andorra"},
    )
    assert set(table["LICENSE-coding-skills"]) == {
        "bayesian-workflow", "clean-code",
    }
    assert len(table["LICENSE-superpowers"]) == 13
    assert "tech-debt" not in table["LICENSE-coding-skills"]
    for skill_dir in skill_dirs():
        required = {"LICENSE"} | {
            root_name for root_name, names in table.items()
            if skill_dir.name in names
        }
        actual = {path.name for path in skill_dir.glob("LICENSE*")}
        assert actual == required
        for name in required:
            source = ROOT / name
            copy = skill_dir / name
            assert source.is_file() and not source.is_symlink()
            assert copy.is_file() and not copy.is_symlink()
            assert copy.read_bytes() == source.read_bytes()
    assert provenance.bundled_license_violations(
        ROOT, [path.name for path in skill_dirs()], table
    ) == []


# spec: "No skill directory holds a `LICENSE*` file outside its mapping."
# task: 8
def test_provenance_lint_rejects_extra_and_nonregular_copies(tmp_path):
    repo = tmp_path
    skill = repo / "skills/example"
    skill.mkdir(parents=True)
    (repo / "LICENSE").write_bytes(b"base\n")
    (repo / "LICENSE-extra").write_bytes(b"extra\n")
    (skill / "LICENSE").write_bytes(b"base\n")
    copy = skill / "LICENSE-extra"
    copy.write_bytes(b"extra\n")
    table = {"LICENSE-extra": ("example",)}
    check = provenance.bundled_license_violations
    assert check(repo, ["example"], table) == []

    copy.write_bytes(b"different\n")
    assert check(repo, ["example"], table)
    copy.unlink()
    assert check(repo, ["example"], table)
    copy.symlink_to(repo / "LICENSE-extra")
    assert check(repo, ["example"], table)
    copy.unlink()
    copy.write_bytes(b"extra\n")
    (skill / "LICENSE-unmapped").write_bytes(b"unmapped\n")
    assert check(repo, ["example"], table)


# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
def test_provenance_lint_rejects_unmapped_root_license(tmp_path):
    skill = tmp_path / "skills/example"
    skill.mkdir(parents=True)
    (tmp_path / "LICENSE").write_bytes(b"base\n")
    (skill / "LICENSE").write_bytes(b"base\n")
    (tmp_path / "LICENSE-orphan").write_bytes(b"orphan\n")
    assert provenance.bundled_license_violations(
        tmp_path, ["example"], {}
    )


# spec: "NOTICE gains one paragraph near the top: each skill directory carries copies of the license texts that apply to it, so a single-skill install (`install.py --copy --skill`, or a third-party installer) keeps the notice MIT requires."
# task: 8
def test_license_travel_documentation():
    notice = (ROOT / "NOTICE").read_text()
    readme = (ROOT / "README.md").read_text()
    claude = (ROOT / "CLAUDE.md").read_text()
    assert "install.py --copy --skill" in notice[:2500]
    assert "check_provenance.py" in notice
    license_section = readme.split("## License", 1)[1].split("\n## ", 1)[0]
    assert "skill" in license_section.lower()
    assert "license" in license_section.lower()
    assert "check_provenance.py" in claude
    assert len(claude.splitlines()) <= 200


# spec: "A notice exists. Add the upstream license text verbatim as root `LICENSE-andorra`, map it to `bayesian-workflow`, and extend NOTICE's `bayesian-workflow/` block with the source URL and the quoted copyright line."
# task: 9
def test_andorra_outcome_is_recorded():
    root_license = ROOT / "LICENSE-andorra"
    notice = (ROOT / "NOTICE").read_text()
    if root_license.exists():
        assert set(provenance.BUNDLED_LICENSES["LICENSE-andorra"]) == {
            "bayesian-workflow"
        }
        assert (
            ROOT / "skills/bayesian-workflow/LICENSE-andorra"
        ).read_bytes() == root_license.read_bytes()
        copyright_lines = [
            line.strip() for line in root_license.read_text().splitlines()
            if "copyright" in line.lower()
        ]
        assert copyright_lines
        assert any(line in notice for line in copyright_lines)
        assert "https://" in notice.split("bayesian-workflow/", 1)[1]
    else:
        deferred = (ROOT / "specs/deferred_items.md").read_text()
        assert (
            re.search(r"Andorra.*no .*notice", notice, re.IGNORECASE)
            or "Andorra" in deferred
        )


# spec: "Record the scenario, prompts, outputs, and verdicts in `specs/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house red-baseline format."
# task: 2
def test_red_baseline_record_exists():
    records = sorted(
        (ROOT / "specs").glob("red-baseline-description-openings-????-??-??.md")
    )
    assert records
    record = records[-1].read_text().lower()
    for word in ("scenario", "prompt", "output", "verdict", "150"):
        assert word in record


# spec: "The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list)."
# task: 14
def test_writing_skills_records_codex_measurement():
    text = (ROOT / "skills/writing-skills/SKILL.md").read_text()
    section = text.split("Token Efficiency", 1)[1].split("\n## ", 1)[0]
    for term in (
        "Codex", "budget", "description", "93", "0.154",
        "2026-10-03", "codex debug prompt-input",
    ):
        assert term in section
    assert re.search(r"156\s*[–-]\s*164", section)
    assert "outside" in section and "repo" in section


# spec: "The CLAUDE.md lines from R1.9 and R4.4 stay under the `claude-md-size` check's 200-line limit in `build/cc_guide/conformance.toml`."
# task: 15
def test_documentation_and_named_gates_pass():
    assert len((ROOT / "CLAUDE.md").read_text().splitlines()) <= 200
    for command in (
        ("build/check_frontmatter.py",),
        ("build/check_provenance.py",),
        ("build/check_snippets.py", "skills/"),
        ("build/check_conformance.py",),
        ("build/sync_runtime_assets.py", "--check"),
    ):
        run_gate(*command)


# spec: "`gemini skills list --all` shows every skill under `skills/` as `[Enabled]`;"
# task: 15
def test_gemini_loads_every_skill_from_outside_repo(tmp_path):
    assert ROOT != tmp_path and ROOT not in tmp_path.parents
    result = subprocess.run(
        ["gemini", "skills", "list", "--all"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    lines = (result.stdout + result.stderr).splitlines()
    for skill_dir in skill_dirs():
        assert any(
            skill_dir.name in line and "[Enabled]" in line
            for line in lines
        ), skill_dir.name


# spec: "`codex debug prompt-input` lists every skill under `skills/` by name."
# task: 15
def test_codex_loads_every_skill_from_outside_repo(tmp_path):
    assert ROOT != tmp_path and ROOT not in tmp_path.parents
    result = subprocess.run(
        ["codex", "debug", "prompt-input"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    listing = result.stdout + result.stderr
    for skill_dir in skill_dirs():
        assert skill_dir.name in listing


# spec: "Out of scope (deferred; logged to `specs/deferred_items.md` at plan completion)"
# task: 15
def test_deferred_scope_is_logged():
    text = (ROOT / "specs/deferred_items.md").read_text().lower()
    for term in (
        "trigger-eval", "marketplace.json", "/deferred",
        "tables of contents", "writing-skills", "versioning",
        "security scanning", "single-file agents",
    ):
        assert term in text
</tests>
<flags>
<flag task="7"><spec>CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run)</spec><plan>Modify: `CLAUDE.md` (Commands: the frontmatter lint's comment names `--strict`; no line added, D7)</plan></flag>
<flag task="8"><spec>No skill directory holds a `LICENSE*` file outside its mapping.</spec><plan>Rename: `skills/recommend-causal-design/LICENSE` to `skills/recommend-causal-design/LICENSE-causal-design-sources`, and re-point its links in that skill's `SKILL.md`, `README.md` and `references/sources.md`</plan></flag>
<flag task="9"><spec>`LICENSE-andorra` | `bayesian-workflow` | only if R4.5 finds an upstream notice</spec><plan>Create: `LICENSE-andorra` (upstream's text, verbatim) and its copy `skills/bayesian-workflow/LICENSE-andorra`</plan></flag>
<flag task="10"><spec>There are 16. Fourteen gain a header:</spec><plan>Modify: the 15 header-less runnable scripts (helper script): a shebang where missing, then the header</plan></flag>
</flags>
<untestable>
All 32 descriptions pass as of 2026-10-03.
No description rewrites in this spec.
5 reps, each a fresh agent given the current `writing-skills` description guidance (the control: no new wording).
Run from a session whose cwd was never this repo.
A rep passes if the designated primary trigger lies within the first 150 characters.
The controller reads each output and records the verbatim 150-character prefix.
Use the lowest of `'>=3.11'`, `'>=3.12'`, `'>=3.13'` under which the test suite covering the script passes, run with `uv run --python 3.X` and that suite's CLAUDE.md dependencies.
Scripts covered by one suite share its floor, unless a failure is attributable to one script, which then alone takes the higher floor.
Every third-party import, including function-level imports, is declared with a `>=` floor at the major version the suite currently resolves (e.g. `'polars>=1.0'`).
Runtime backends that the script never imports but needs to read its inputs (e.g. `h5netcdf` for NetCDF) are added when R3.8's fixture run shows them needed.
From an empty scratch directory (a subdirectory such as `/tmp/bwprobe/`, never `/tmp` itself), each of the 16 scripts runs `uv run <absolute-path>` on a minimal real input that exercises its main code path.
`--help` alone is enough only for a script with no input-reading path.
The three ArviZ-reading scripts (`diagnose_model.py`, `calibration_check.py`, `compare_experiments.py`) each read a small saved InferenceData fixture.
One script is also run from inside a directory holding an unrelated `pyproject.toml`.
The dependency-drift check still passes.
Locate Alexandre Andorra's original PyMC Bayesian-workflow skill and read its license.
Never compose a copyright line that is not quoted from the source.
Work in a worktree.
Commit from the worktree; the shared checkout's branch can change under a concurrent session.
State test changes as +N deltas against the suite, never absolute totals.
Before allocating the plan id, check `specs/plans/` on every branch (`git ls-tree`); ids are allocated per branch and have collided.
Whichever branch merges second brings the other's skills into conformance in the same merge, or the new lints fail on arrival.
Each new lint rule has a test that failed before its implementation and passes after.
</untestable>