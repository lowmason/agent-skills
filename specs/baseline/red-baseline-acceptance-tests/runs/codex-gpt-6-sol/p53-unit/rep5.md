<tests>
import ast
import re
import tomllib
from pathlib import Path

import pytest
import yaml

from build import check_frontmatter as frontmatter
from build import check_provenance as provenance


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
FALLBACK = (
    "Without uv, run the same path with `python3` in an environment "
    "that has the dependencies listed in the script's header."
)
RUNNABLE = {
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


def skill_dirs():
    return sorted(path for path in SKILLS.iterdir() if (path / "SKILL.md").is_file())


def skill_frontmatter(skill_dir):
    parts = (skill_dir / "SKILL.md").read_text().split("---", 2)
    assert len(parts) == 3
    return yaml.safe_load(parts[1])


def make_skill(parent, name="example", frontmatter=None, body=""):
    skill_dir = parent / name
    skill_dir.mkdir(parents=True)
    data = frontmatter or {
        "name": name,
        "description": "Use when checking an example.",
        "license": "MIT",
    }
    (skill_dir / "SKILL.md").write_text(
        "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body
    )
    return skill_dir


def all_invocations():
    return {
        skill.name: frontmatter.bundled_invocations(skill)
        for skill in skill_dirs()
    }


# spec: "Replace `ALLOWED_KEYS` with two named sets and allow their union in a `SKILL.md`:"
# task: 3
def test_frontmatter_key_sets():
    assert frontmatter.SPEC_KEYS == frozenset({
        "name", "description", "license", "compatibility",
        "metadata", "allowed-tools",
    })
    assert frontmatter.HOST_KEYS == frozenset({
        "when_to_use", "model", "effort", "context",
        "disable-model-invocation",
    })
    assert not hasattr(frontmatter, "ALLOWED_KEYS")


# spec: "When present, a mapping whose keys and values are all strings."
# task: 3
def test_metadata_shape(tmp_path):
    sk = tmp_path / "SKILL.md"
    base = {"name": "example", "description": "Use when needed."}
    assert not frontmatter._check_value_shapes(
        sk, {**base, "metadata": {"author": "A", "source": "https://example.org"}}
    )
    for invalid in ([], "author", {1: "A"}, {"author": 1}):
        assert frontmatter._check_value_shapes(
            sk, {**base, "metadata": invalid}
        )


# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
def test_compatibility_shape(tmp_path):
    sk = tmp_path / "SKILL.md"
    base = {"name": "example", "description": "Use when needed."}
    assert frontmatter.COMPATIBILITY_CAP == 500
    for valid in ("x", " " + "x" * 500 + " "):
        assert not frontmatter._check_value_shapes(
            sk, {**base, "compatibility": valid}
        )
    for invalid in (" ", "x" * 501, 500):
        assert frontmatter._check_value_shapes(
            sk, {**base, "compatibility": invalid}
        )


# spec: "`name` and `description` contain no `<` or `>`."
# task: 3
def test_angle_brackets_and_llm_wiki_phrase(tmp_path):
    sk = tmp_path / "SKILL.md"
    base = {"name": "example", "description": "Use when needed."}
    for key, value in (
        ("name", "exam<ple"),
        ("name", "exam>ple"),
        ("description", "Use when verifying <page>."),
        ("description", "Use when verifying >page."),
    ):
        assert frontmatter._check_value_shapes(sk, {**base, key: value})
    description = skill_frontmatter(SKILLS / "llm-wiki")["description"]
    assert "verify a page" in description
    assert "verify <page>" not in description


# spec: "Required in every `SKILL.md`, a non-empty string (repo policy, beyond the spec)."
# task: 4
def test_license_required_and_nonempty(tmp_path):
    sk = tmp_path / "SKILL.md"
    assert not frontmatter._check_license(sk, {"license": "MIT"})
    for invalid in ({}, {"license": ""}, {"license": 3}):
        assert frontmatter._check_license(sk, invalid)


# spec: "The 13 superpowers skills gain `license: MIT` and"
# task: 4
def test_superpowers_metadata_and_all_skill_licenses():
    superpowers = []
    for skill in skill_dirs():
        data = skill_frontmatter(skill)
        assert isinstance(data.get("license"), str) and data["license"]
        metadata = data.get("metadata") or {}
        if metadata.get("source") == "https://github.com/obra/superpowers":
            superpowers.append(skill.name)
            assert data["license"] == "MIT"
            assert metadata == {
                "author": "Jesse Vincent",
                "adapted_by": "Lowell Mason",
                "source": "https://github.com/obra/superpowers",
            }
    assert len(superpowers) == 13


# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
def test_disable_model_invocation_boolean(tmp_path):
    skill = make_skill(tmp_path)
    assert frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": "true"}
    )
    assert not frontmatter._check_invocation_parity(skill, {})


# spec: "A skill with `disable-model-invocation: true` must ship `agents/openai.yaml` that parses and sets `policy.allow_implicit_invocation: false`."
# task: 5
def test_codex_policy_required_for_manual_skill(tmp_path):
    skill = make_skill(tmp_path)
    assert frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": True}
    )
    agents = skill / "agents"
    agents.mkdir()
    policy = agents / "openai.yaml"
    policy.write_text("policy: [invalid\n")
    assert frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": True}
    )
    policy.write_text("policy:\n  allow_implicit_invocation: true\n")
    assert frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": True}
    )
    policy.write_text("policy:\n  allow_implicit_invocation: false\n")
    assert not frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": True}
    )


# spec: "Conversely, a skill whose `agents/openai.yaml` sets that policy to `false` must set `disable-model-invocation: true`."
# task: 5
def test_codex_policy_false_requires_manual_skill(tmp_path):
    skill = make_skill(tmp_path)
    agents = skill / "agents"
    agents.mkdir()
    (agents / "openai.yaml").write_text(
        "policy:\n  allow_implicit_invocation: false\n"
    )
    assert frontmatter._check_invocation_parity(skill, {})
    assert frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": False}
    )
    assert not frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": True}
    )


# spec: "No skill trips this today; it exists so that the first manual-only skill cannot auto-fire in Codex."
# task: 5
def test_current_skills_have_invocation_parity():
    for skill in skill_dirs():
        assert frontmatter._check_invocation_parity(
            skill, skill_frontmatter(skill)
        ) == []


# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
def test_body_warning_boundary_and_default_exit(tmp_path, capsys):
    skill = make_skill(tmp_path, body="line\n" * 500)
    assert frontmatter.skill_body_warning(skill) is None
    (skill / "SKILL.md").write_text(
        (skill / "SKILL.md").read_text() + "line\n"
    )
    warning = frontmatter.skill_body_warning(skill)
    assert warning is not None
    assert warning.count("WARN") == 1
    assert frontmatter.main([]) == 0
    err = capsys.readouterr().err
    assert len([line for line in err.splitlines() if "WARN" in line]) == 1


# spec: "Today only `writing-skills` warns; splitting it is deferred."
# task: 6
def test_only_writing_skills_has_body_warning():
    warned = [
        skill.name for skill in skill_dirs()
        if frontmatter.skill_body_warning(skill) is not None
    ]
    assert warned == ["writing-skills"]


# spec: "When Stage A adds this warning, it also adds a `skill-body-size` `[[check]]` to `build/cc_guide/conformance.toml` that maps `skills.overview` to it, with `enforced_by = 'check_frontmatter'` (conformance R6 P3)."
# task: 6
def test_body_size_conformance_registration():
    text = (ROOT / "build/cc_guide/conformance.toml").read_text()
    tomllib.loads(text)
    blocks = re.split(r"(?m)^\[\[check\]\]\s*$", text)
    assert any(
        all(term in block for term in (
            "skill-body-size", "skills.overview", "check_frontmatter"
        ))
        for block in blocks
    )


# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
def test_strict_host_keys_and_reserved_names(tmp_path):
    for key in frontmatter.HOST_KEYS:
        skill = make_skill(
            tmp_path / key,
            frontmatter={
                "name": "example",
                "description": "Use when needed.",
                "license": "MIT",
                key: True if key == "disable-model-invocation" else "value",
            },
        )
        assert frontmatter.strict_violations(skill)
    for name in ("claude-helper", "anthropic-helper"):
        skill = make_skill(
            tmp_path / name,
            frontmatter={
                "name": name,
                "description": "Use when needed.",
                "license": "MIT",
            },
        )
        assert frontmatter.strict_violations(skill)


# spec: "Expected result today: exactly `bayesian-workflow`, `tune-hyperparameters`, and `tech-debt` fail."
# task: 7
def test_strict_profile_failing_skill_set():
    failures = {
        skill.name for skill in skill_dirs()
        if frontmatter.strict_violations(skill)
    }
    assert failures == {
        "bayesian-workflow", "tune-hyperparameters", "tech-debt"
    }


# spec: "The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, \"Conformance register\")."
# task: 7
def test_strict_documentation_and_claude_md_limit():
    doc = frontmatter.__doc__ or ""
    assert "--strict" in doc
    assert "compatibility" in doc
    claude = (ROOT / "CLAUDE.md").read_text()
    assert len(claude.splitlines()) <= 200
    commands = claude.split("Commands", 1)[1]
    assert any(
        "check_frontmatter.py --strict" in line
        and ("uv run" in line or "python" in line)
        and not line.lstrip().startswith("#")
        for line in commands.splitlines()
    )
    assert "claude.ai" in commands or "spec-only validator" in commands


# spec: "Record the scenario, prompts, outputs, and verdicts in `specs/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house red-baseline format."
# task: 2
def test_red_baseline_record_exists():
    records = [
        path for path in (ROOT / "specs").glob(
            "red-baseline-description-openings-*.md"
        )
        if re.fullmatch(
            r"red-baseline-description-openings-\d{4}-\d{2}-\d{2}\.md",
            path.name,
        )
    ]
    assert records
    text = max(records).read_text().lower()
    for term in ("scenario", "prompt", "output", "verdict", "150"):
        assert term in text


# spec: "The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list)."
# task: 14
def test_writing_skills_measured_note():
    text = (SKILLS / "writing-skills/SKILL.md").read_text()
    section = text.split("Token Efficiency", 1)[1]
    assert "Codex" in section
    assert re.search(r"156\s*[–-]\s*164", section)
    for term in (
        "93", "0.154", "2026-10-03", "codex debug prompt-input",
        "outside", "Skills",
    ):
        assert term in section


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_bundled_license_mapping_and_copies():
    table = provenance.BUNDLED_LICENSES
    assert provenance.PLAIN_LICENSE == "LICENSE"
    names = [skill.name for skill in skill_dirs()]
    superpowers = {
        skill.name for skill in skill_dirs()
        if (skill_frontmatter(skill).get("metadata") or {}).get("source")
        == "https://github.com/obra/superpowers"
    }
    assert set(table["LICENSE-superpowers"]) == superpowers
    assert set(table["LICENSE-coding-skills"]) == {
        "bayesian-workflow", "clean-code"
    }
    for name in names:
        required = {"LICENSE"} | {
            root_name for root_name, members in table.items()
            if name in members
        }
        for root_name in required:
            root_file = ROOT / root_name
            copy = SKILLS / name / root_name
            assert root_file.is_file() and not root_file.is_symlink()
            assert copy.is_file() and not copy.is_symlink()
            assert copy.read_bytes() == root_file.read_bytes()
        actual = {
            path.name for path in (SKILLS / name).glob("LICENSE*")
        }
        assert actual == required
    assert provenance.bundled_license_violations(
        ROOT, names, table
    ) == []


# spec: "No skill directory holds a `LICENSE*` file outside its mapping."
# task: 8
def test_provenance_lint_rejects_missing_changed_symlink_and_extra(tmp_path):
    repo = tmp_path
    skill = repo / "skills/example"
    skill.mkdir(parents=True)
    (repo / "LICENSE").write_bytes(b"canonical\n")
    copy = skill / "LICENSE"
    copy.write_bytes(b"canonical\n")
    assert provenance.bundled_license_violations(repo, ["example"], {}) == []
    copy.unlink()
    assert provenance.bundled_license_violations(repo, ["example"], {})
    copy.write_bytes(b"changed\n")
    assert provenance.bundled_license_violations(repo, ["example"], {})
    copy.unlink()
    copy.symlink_to(repo / "LICENSE")
    assert provenance.bundled_license_violations(repo, ["example"], {})
    copy.unlink()
    copy.write_bytes(b"canonical\n")
    (skill / "LICENSE-extra").write_bytes(b"extra\n")
    assert provenance.bundled_license_violations(repo, ["example"], {})


# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
def test_provenance_lint_rejects_unmapped_root_license(tmp_path):
    skill = tmp_path / "skills/example"
    skill.mkdir(parents=True)
    (tmp_path / "LICENSE").write_bytes(b"canonical\n")
    (skill / "LICENSE").write_bytes(b"canonical\n")
    (tmp_path / "LICENSE-extra").write_bytes(b"extra\n")
    assert provenance.bundled_license_violations(
        tmp_path, ["example"], {}
    )


# spec: "NOTICE gains one paragraph near the top: each skill directory carries copies of the license texts that apply to it, so a single-skill install (`install.py --copy --skill`, or a third-party installer) keeps the notice MIT requires."
# task: 8
def test_license_travel_documentation():
    notice = (ROOT / "NOTICE").read_text()
    assert "install.py --copy --skill" in notice[:2000]
    assert "check_provenance.py" in notice
    readme = (ROOT / "README.md").read_text()
    license_section = readme.split("License", 1)[1]
    assert "skill" in license_section.lower()
    claude = (ROOT / "CLAUDE.md").read_text()
    assert "check_provenance.py" in claude
    assert "LICENSE" in claude
    assert len(claude.splitlines()) <= 200


# spec: "`LICENSE-andorra` | `bayesian-workflow` | only if R4.5 finds an upstream notice"
# task: 9
def test_andorra_license_branch_is_consistent():
    root_file = ROOT / "LICENSE-andorra"
    members = provenance.BUNDLED_LICENSES.get("LICENSE-andorra")
    copy = SKILLS / "bayesian-workflow/LICENSE-andorra"
    if root_file.exists():
        assert members == ("bayesian-workflow",)
        assert copy.is_file() and not copy.is_symlink()
        assert copy.read_bytes() == root_file.read_bytes()
        notice = (ROOT / "NOTICE").read_text()
        block = notice.split("bayesian-workflow/", 1)[1]
        assert "http" in block
        assert "copyright" in block.lower()
    else:
        assert members is None
        assert not copy.exists()


# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
def test_runnable_script_inventory():
    found = {
        str(path.resolve().relative_to(SKILLS.resolve()))
        for skill in skill_dirs()
        for path in frontmatter.runnable_scripts(skill)
    }
    assert found == RUNNABLE
    assert "tune-hyperparameters/scripts/time_series_cv.py" not in found


# spec: "Then a `# /// script` block with single-quoted TOML strings, a `requires-python`, and a `dependencies` list (`[]` for stdlib-only scripts)."
# task: 10
def test_every_runnable_script_has_house_pep723_header():
    for relative in RUNNABLE:
        path = SKILLS / relative
        text = path.read_text()
        lines = text.splitlines()
        assert lines[0] == "#!/usr/bin/env python3", relative
        start = lines.index("# /// script")
        end = lines.index("# ///", start + 1)
        assert start in (1, 2), relative
        header = "\n".join(lines[start:end + 1])
        assert '"' not in header, relative
        metadata = frontmatter.script_metadata(text)
        assert metadata["requires-python"] in {
            ">=3.11", ">=3.12", ">=3.13"
        }
        assert isinstance(metadata["dependencies"], list)


# spec: "Every third-party import, including function-level imports, is declared with a `>=` floor at the major version the suite currently resolves (e.g. `'polars>=1.0'`)."
# task: 10
def test_runnable_script_imports_are_declared():
    for relative in RUNNABLE:
        path = SKILLS / relative
        metadata = frontmatter.script_metadata(path.read_text())
        siblings = {item.stem for item in path.parent.glob("*.py")}
        required = frontmatter.required_imports(
            ast.parse(path.read_text()), siblings
        )
        dependencies = metadata["dependencies"]
        assert all(
            isinstance(dep, str) and ">=" in dep and "<" not in dep
            for dep in dependencies
        ), relative
        declared = {
            re.split(r"[<>=!~\[]", dep, maxsplit=1)[0]
            .lower().replace("_", "-")
            for dep in dependencies
        }
        assert required <= declared, (relative, required - declared)
        if not required:
            assert dependencies == [] or all(
                isinstance(dep, str) for dep in dependencies
            )


# spec: "Imports inside a `try` whose handler catches `ImportError` or `ModuleNotFoundError` are optional and may be left undeclared."
# task: 10
def test_required_imports_excludes_stdlib_local_and_optional():
    tree = ast.parse(
        "import os\n"
        "import helper\n"
        "import yaml\n"
        "def load():\n"
        "    from polars import DataFrame\n"
        "try:\n"
        "    import optional_package\n"
        "except (ImportError, ModuleNotFoundError):\n"
        "    pass\n"
    )
    assert frontmatter.required_imports(tree, {"helper"}) == {
        "pyyaml", "polars"
    }


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_header_lint_rejects_missing_invalid_and_incomplete_metadata(tmp_path):
    skill = make_skill(tmp_path)
    scripts = skill / "scripts"
    scripts.mkdir()
    script = scripts / "run.py"
    main = "\nif __name__ == '__main__':\n    pass\n"
    script.write_text(main)
    assert frontmatter.check_script_headers(skill)
    script.write_text(
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
        "# dependencies = [\n"
        "# ///\n" + main
    )
    assert frontmatter.check_script_headers(skill)
    script.write_text(
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
        "# ///\n" + main
    )
    assert frontmatter.check_script_headers(skill)
    script.write_text(
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
        "# dependencies = []\n"
        "# ///\n" + main
    )
    assert frontmatter.check_script_headers(skill) == []


# spec: "In such a script, every non-stdlib, non-local import is declared in `dependencies`:"
# task: 10
def test_header_lint_uses_distribution_aliases(tmp_path):
    skill = make_skill(tmp_path)
    scripts = skill / "scripts"
    scripts.mkdir()
    script = scripts / "run.py"
    prefix = (
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
    )
    suffix = (
        "# ///\n"
        "import yaml\n"
        "if __name__ == '__main__':\n"
        "    pass\n"
    )
    script.write_text(prefix + "# dependencies = []\n" + suffix)
    assert frontmatter.check_script_headers(skill)
    script.write_text(
        prefix + "# dependencies = ['pyyaml>=6.0']\n" + suffix
    )
    assert frontmatter.check_script_headers(skill) == []


# spec: "Path forms in use: `<this-skill-dir>/scripts/x.py`, `<this-skill-dir>/../<skill>/scripts/x.py`, `$LLM_WIKI_ROOT/scripts/x.py` (the installed copies), `~/Projects/agent-skills/skills/llm-wiki/scripts/x.py` (llm-wiki's INSTALL.md), and repo-relative `skills/<skill>/scripts/build.py`."
# task: 11
def test_bundled_script_resolution_for_local_and_cross_skill_paths(tmp_path):
    skills = tmp_path / "skills"
    first = make_skill(skills, "first")
    second = make_skill(skills, "second")
    for skill in (first, second):
        scripts = skill / "scripts"
        scripts.mkdir()
        (scripts / "x.py").write_text(
            "if __name__ == '__main__':\n    pass\n"
        )
    assert frontmatter.resolve_bundled_script(
        "<this-skill-dir>/scripts/x.py", first
    ) == first / "scripts/x.py"
    assert frontmatter.resolve_bundled_script(
        "<this-skill-dir>/../second/scripts/x.py", first
    ) == second / "scripts/x.py"
    assert frontmatter.resolve_bundled_script(
        "scripts/migrate.py", first
    ) is None


# spec: "No skill markdown invokes a resolving bundled-script path with bare `python` or `python3`, including line-continued forms (`python \\` followed by the path on the next line)."
# task: 11
def test_invocation_lint_catches_continued_python_command(tmp_path):
    skill = make_skill(tmp_path)
    scripts = skill / "scripts"
    scripts.mkdir()
    (scripts / "run.py").write_text(
        "if __name__ == '__main__':\n    pass\n"
    )
    readme = skill / "README.md"
    readme.write_text("python \\\n  <this-skill-dir>/scripts/run.py\n")
    invocations = frontmatter.bundled_invocations(skill)
    assert any(runner == "python" for _, runner, _ in invocations)
    assert frontmatter.check_invocations(skill)
    readme.write_text("uv run <this-skill-dir>/scripts/run.py\n")
    assert frontmatter.check_invocations(skill) == []


# spec: "A path that does not resolve to a bundled script, such as `writing-skills/anthropic-best-practices.md`'s teaching example `scripts/migrate.py`, is not flagged."
# task: 11
def test_invocation_lint_ignores_unresolved_teaching_example(tmp_path):
    skill = make_skill(tmp_path)
    (skill / "README.md").write_text("python scripts/migrate.py\n")
    assert frontmatter.bundled_invocations(skill) == []
    assert frontmatter.check_invocations(skill) == []


# spec: "Each skill with such an invocation gets this sentence once, near its first invocation: \"Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.\""
# task: 11
def test_all_documented_bundled_invocations_use_uv_and_have_fallback():
    seen = set()
    for skill in skill_dirs():
        invocations = frontmatter.bundled_invocations(skill)
        assert frontmatter.check_invocations(skill) == []
        if not invocations:
            continue
        seen.add(skill.name)
        assert all(runner == "uv run" for _, runner, _ in invocations)
        markdown = "\n".join(
            path.read_text() for path in skill.rglob("*.md")
        )
        assert markdown.count(FALLBACK) == 1, skill.name
    assert "finishing-a-development-branch" in seen


# spec: "A skill whose markdown runs a bundled script via `uv run` declares a `compatibility` value containing `uv`."
# task: 12
def test_compatibility_lint_requires_uv(tmp_path):
    skill = make_skill(tmp_path)
    scripts = skill / "scripts"
    scripts.mkdir()
    (scripts / "run.py").write_text(
        "if __name__ == '__main__':\n    pass\n"
    )
    (skill / "README.md").write_text(
        "uv run <this-skill-dir>/scripts/run.py\n"
    )
    assert frontmatter._check_compatibility_names_uv(skill, {})
    assert frontmatter._check_compatibility_names_uv(
        skill, {"compatibility": "Requires Python."}
    )
    assert frontmatter._check_compatibility_names_uv(
        skill, {"compatibility": "Requires uv."}
    ) == []


# spec: "Here 3.X is the highest `requires-python` floor among the scripts that skill invokes."
# task: 12
def test_compatibility_text_matches_highest_invoked_script_floor():
    seen = set()
    for skill in skill_dirs():
        paths = [
            frontmatter.resolve_bundled_script(path, skill)
            for _, runner, path in frontmatter.bundled_invocations(skill)
            if runner == "uv run"
        ]
        if not paths:
            continue
        assert all(path is not None for path in paths)
        seen.add(skill.name)
        floors = [
            frontmatter.script_metadata(path.read_text())["requires-python"]
            for path in paths
        ]
        highest = max(floors, key=lambda floor: int(floor.split(".")[1]))
        expected = (
            "Requires uv to run bundled scripts "
            "(dependencies are declared inline); "
            f"Python {highest.removeprefix('>=')}+."
        )
        assert skill_frontmatter(skill)["compatibility"] == expected
    assert "finishing-a-development-branch" in seen


# spec: "Prose floors that disagree with the header are aligned or removed (e.g. \"Python ≥ 3.9\" in `recommend-probabilistic-model` and `recommend-visualization`)."
# task: 12
def test_old_prose_python_floors_are_removed_or_aligned():
    for name in (
        "recommend-probabilistic-model", "recommend-visualization"
    ):
        skill = SKILLS / name
        compatibility = skill_frontmatter(skill)["compatibility"]
        expected = re.search(r"Python 3\.(\d+)\+", compatibility).group(1)
        prose = "\n".join(path.read_text() for path in skill.rglob("*.md"))
        for floor in re.findall(
            r"Python\s*(?:≥|>=)\s*3\.(\d+)", prose
        ):
            assert floor == expected
        assert "Python ≥ 3.9" not in prose
</tests>
<flags>
<flag task="1"><spec>**Status: APPROVED (2026-10-18).** The owner approved the design on 2026-10-03 and the written spec on 2026-10-18. Next step: an implementation plan from the writing-plans skill.</spec><plan>Produces: a spec whose counts and rules match Tasks 2–15.</plan></flag>
<flag task="7"><spec>CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").</spec><plan>Modify: `CLAUDE.md` (Commands: the frontmatter lint's comment names `--strict`; no line added, D7)</plan></flag>
<flag task="8"><spec>No skill directory holds a `LICENSE*` file outside its mapping.</spec><plan>Rename: `skills/recommend-causal-design/LICENSE` to `skills/recommend-causal-design/LICENSE-causal-design-sources`, and re-point its links in that skill's `SKILL.md`, `README.md` and `references/sources.md`</plan></flag>
<flag task="9"><spec>| `LICENSE-andorra` | `bayesian-workflow` | only if R4.5 finds an upstream notice |</spec><plan>Create: `LICENSE-andorra` (upstream's text, verbatim) and its copy `skills/bayesian-workflow/LICENSE-andorra`</plan></flag>
<flag task="10"><spec>Fourteen gain a header:</spec><plan>Modify: the 15 header-less runnable scripts (helper script): a shebang where missing, then the header</plan></flag>
</flags>
<untestable>
Criterion: within its first 150 characters, a description names the skill's primary trigger, the task or symptom it exists for, so an agent shown only that prefix would load it for its canonical use.
Before any edit to `writing-skills`, run a baseline:
5 reps, each a fresh agent given the current `writing-skills` description guidance (the control: no new wording).
Each is asked to write a SKILL.md description for a synthetic skill that is not from this repo and has at least 8 trigger conditions, one of them designated in the scenario as primary.
Run from a session whose cwd was never this repo.
A rep passes if the designated primary trigger lies within the first 150 characters.
The controller reads each output and records the verbatim 150-character prefix.
Baseline ≥ 4/5: add only a factual note of 2–4 lines to `writing-skills`' "Token Efficiency" section.
No new rule.
Baseline ≤ 3/5: also add one checklist line ("the primary trigger falls within the first ~150 characters") and GREEN-test it: 5 reps with the new wording, at least 4/5 passing, recorded in the same red-baseline file.
Use the lowest of `'>=3.11'`, `'>=3.12'`, `'>=3.13'` under which the test suite covering the script passes, run with `uv run --python 3.X` and that suite's CLAUDE.md dependencies.
Scripts covered by one suite share its floor, unless a failure is attributable to one script, which then alone takes the higher floor.
Runtime backends that the script never imports but needs to read its inputs (e.g. `h5netcdf` for NetCDF) are added when R3.8's fixture run shows them needed.
From an empty scratch directory (a subdirectory such as `/tmp/bwprobe/`, never `/tmp` itself), each of the 16 scripts runs `uv run <absolute-path>` on a minimal real input that exercises its main code path.
`--help` alone is enough only for a script with no input-reading path.
The three ArviZ-reading scripts (`diagnose_model.py`, `calibration_check.py`, `compare_experiments.py`) each read a small saved InferenceData fixture.
One script is also run from inside a directory holding an unrelated `pyproject.toml`.
The dependency-drift check still passes.
Locate Alexandre Andorra's original PyMC Bayesian-workflow skill and read its license.
Add the upstream license text verbatim as root `LICENSE-andorra`, map it to `bayesian-workflow`, and extend NOTICE's `bayesian-workflow/` block with the source URL and the quoted copyright line.
Never compose a copyright line that is not quoted from the source.
The 2026-08-26 intake review (`specs/completed/skill-intake-review-2026-08-26.md`) already found that Andorra appears nowhere in the history of pymc-labs/python-analytics-skills (only Fonnesbeck and Dean commit there), so start the search from his own publications rather than that repository.
Stages, in order.
D is independent of C and may run alongside it.
When Stage A or Stage D fixes a gap the register tracks to it, the same change removes or narrows that `[[exception]]` and runs `build/check_conformance.py` (R6 P2).
Work in a worktree.
Commit from the worktree; the shared checkout's branch can change under a concurrent session.
State test changes as +N deltas against the suite, never absolute totals.
Before allocating the plan id, check `specs/plans/` on every branch (`git ls-tree`); ids are allocated per branch and have collided.
Whichever branch merges second brings the other's skills into conformance in the same merge, or the new lints fail on arrival.
Each new lint rule has a test that failed before its implementation and passes after.
Cross-runtime load check, from a directory outside any repo:
`gemini skills list --all` shows every skill under `skills/` as `[Enabled]`;
`codex debug prompt-input` lists every skill under `skills/` by name.
</untestable>