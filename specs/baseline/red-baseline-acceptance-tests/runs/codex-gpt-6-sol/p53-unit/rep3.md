<tests>
import ast
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import pytest
import yaml

from build import check_frontmatter as frontmatter
from build import check_provenance as provenance


ROOT = Path.cwd().resolve()
SKILLS = ROOT / "skills"
FALLBACK = (
    "Without uv, run the same path with `python3` in an environment "
    "that has the dependencies listed in the script's header."
)
EXPECTED_SCRIPTS = {
    "skills/bayesian-workflow/scripts/calibration_check.py",
    "skills/bayesian-workflow/scripts/check_diagnostics.py",
    "skills/bayesian-workflow/scripts/diagnose_model.py",
    "skills/classification-codes/scripts/build.py",
    "skills/describe-critique-methodology/scripts/check_decoupling.py",
    "skills/design-architecture/scripts/new_adr.py",
    "skills/explore-data/scripts/profile.py",
    "skills/geographic-codes/scripts/build.py",
    "skills/llm-wiki/scripts/bootstrap_wiki.py",
    "skills/llm-wiki/scripts/distill_sessions.py",
    "skills/llm-wiki/scripts/distill_specs.py",
    "skills/llm-wiki/scripts/lint_wiki.py",
    "skills/recommend-probabilistic-model/scripts/characterize.py",
    "skills/recommend-visualization/scripts/recommend.py",
    "skills/track-model-experiments/scripts/compare_experiments.py",
    "skills/writing-plans/scripts/deferred_stats.py",
}


def skill_dirs():
    return sorted(
        path for path in SKILLS.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def skill_frontmatter(path):
    text = path.read_text()
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    assert match, path
    return yaml.safe_load(match.group(1)) or {}


def make_skill(tmp_path, name="example", fields=None, body="Body\n"):
    skill = tmp_path / "skills" / name
    skill.mkdir(parents=True)
    data = {
        "name": name,
        "description": "Use when testing a synthetic skill.",
        "license": "MIT",
    }
    data.update(fields or {})
    (skill / "SKILL.md").write_text(
        "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body
    )
    return skill


def make_script(skill, dependencies="[]", body=None):
    scripts = skill / "scripts"
    scripts.mkdir(exist_ok=True)
    script = scripts / "run.py"
    if body is None:
        body = "if __name__ == '__main__':\n    print('ok')\n"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
        f"# dependencies = {dependencies}\n"
        "# ///\n\n"
        + body
    )
    return script


def license_fixture(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "LICENSE").write_bytes(b"plain license\n")
    (repo / "LICENSE-coding-skills").write_bytes(b"coding license\n")
    for name in ("alpha", "beta"):
        skill = repo / "skills" / name
        skill.mkdir(parents=True)
        (skill / "LICENSE").write_bytes(b"plain license\n")
    (repo / "skills" / "alpha" / "LICENSE-coding-skills").write_bytes(
        b"coding license\n"
    )
    table = {"LICENSE-coding-skills": ("alpha",)}
    return repo, table


# spec: "Replace `ALLOWED_KEYS` with two named sets and allow their union in a `SKILL.md`:"
# task: 3
def test_frontmatter_key_sets():
    assert frontmatter.SPEC_KEYS == frozenset({
        "name", "description", "license", "compatibility", "metadata",
        "allowed-tools",
    })
    assert frontmatter.HOST_KEYS == frozenset({
        "when_to_use", "model", "effort", "context",
        "disable-model-invocation",
    })
    assert not hasattr(frontmatter, "ALLOWED_KEYS")


# spec: "When present, a mapping whose keys and values are all strings."
# task: 3
def test_metadata_shape(tmp_path):
    path = tmp_path / "SKILL.md"
    valid = {"name": "example", "description": "Use when testing.",
             "metadata": {"author": "Someone"}}
    assert frontmatter._check_value_shapes(path, valid) == []
    for invalid in ([], {"author": 1}, {1: "Someone"}):
        assert frontmatter._check_value_shapes(
            path, {**valid, "metadata": invalid}
        )


# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
def test_compatibility_shape(tmp_path):
    path = tmp_path / "SKILL.md"
    for value in ("uv", " x" * 250):
        assert frontmatter._check_value_shapes(
            path, {"name": "example", "description": "Use when testing.",
                   "compatibility": value}
        ) == []
    for value in (" ", "x" * 501, 3):
        assert frontmatter._check_value_shapes(
            path, {"name": "example", "description": "Use when testing.",
                   "compatibility": value}
        )


# spec: "Required in every `SKILL.md`, a non-empty string (repo policy, beyond the spec)."
# task: 4
def test_license_frontmatter(tmp_path):
    path = tmp_path / "SKILL.md"
    assert frontmatter._check_license(path, {"license": "MIT"}) == []
    for fields in ({}, {"license": ""}, {"license": 7}):
        assert frontmatter._check_license(path, fields)
    for skill in skill_dirs():
        assert isinstance(skill_frontmatter(skill / "SKILL.md").get("license"), str)
        assert skill_frontmatter(skill / "SKILL.md")["license"]


# spec: "The 13 superpowers skills gain `license: MIT` and"
# task: 4
def test_superpowers_frontmatter():
    found = []
    for skill in skill_dirs():
        data = skill_frontmatter(skill / "SKILL.md")
        metadata = data.get("metadata") or {}
        if metadata.get("source") == "https://github.com/obra/superpowers":
            found.append(skill.name)
            assert data["license"] == "MIT"
            assert metadata["author"] == "Jesse Vincent"
            assert metadata["adapted_by"] == "Lowell Mason"
    assert len(found) == 13


# spec: "`name` and `description` contain no `<` or `>`."
# task: 3
def test_no_angle_brackets():
    for skill in skill_dirs():
        data = skill_frontmatter(skill / "SKILL.md")
        assert not any(char in data[key] for key in ("name", "description")
                       for char in "<>")


# spec: "Fix llm-wiki's trigger phrase `'verify <page>'` to `'verify a page'`."
# task: 3
def test_llm_wiki_trigger_phrase():
    description = skill_frontmatter(
        SKILLS / "llm-wiki" / "SKILL.md"
    )["description"]
    assert "'verify a page'" in description
    assert "'verify <page>'" not in description


# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
def test_disable_model_invocation_is_boolean(tmp_path):
    skill = make_skill(tmp_path)
    for value in ("true", 1, None):
        assert frontmatter._check_invocation_parity(
            skill, {"disable-model-invocation": value}
        )
    assert frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": False}
    ) == []


# spec: "A skill with `disable-model-invocation: true` must ship `agents/openai.yaml` that parses and sets `policy.allow_implicit_invocation: false`."
# task: 5
def test_true_disable_requires_codex_policy(tmp_path):
    skill = make_skill(tmp_path)
    fields = {"disable-model-invocation": True}
    assert frontmatter._check_invocation_parity(skill, fields)
    agents = skill / "agents"
    agents.mkdir()
    policy = agents / "openai.yaml"
    policy.write_text("policy:\n  allow_implicit_invocation: true\n")
    assert frontmatter._check_invocation_parity(skill, fields)
    policy.write_text("policy:\n  allow_implicit_invocation: false\n")
    assert frontmatter._check_invocation_parity(skill, fields) == []
    policy.write_text("policy: [\n")
    assert frontmatter._check_invocation_parity(skill, fields)


# spec: "Conversely, a skill whose `agents/openai.yaml` sets that policy to `false` must set `disable-model-invocation: true`."
# task: 5
def test_codex_policy_requires_true_disable(tmp_path):
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
    assert frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": True}
    ) == []


# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
def test_body_length_boundary_and_default_gate(tmp_path, capsys):
    skill = make_skill(tmp_path, body="line\n" * 500)
    assert frontmatter.skill_body_warning(skill) is None
    (skill / "SKILL.md").write_text(
        (skill / "SKILL.md").read_text() + "line\n"
    )
    warning = frontmatter.skill_body_warning(skill)
    assert warning is not None and "WARN" in warning
    assert len(warning.splitlines()) == 1
    assert frontmatter.main([]) == 0
    warn_lines = [
        line for line in capsys.readouterr().err.splitlines()
        if "WARN" in line
    ]
    assert len(warn_lines) == 1
    assert "writing-skills" in warn_lines[0]


# spec: "When Stage A adds this warning, it also adds a `skill-body-size` `[[check]]` to `build/cc_guide/conformance.toml` that maps `skills.overview` to it, with `enforced_by = 'check_frontmatter'` (conformance R6 P3)."
# task: 6
def test_body_size_conformance_register():
    data = tomllib.loads(
        (ROOT / "build/cc_guide/conformance.toml").read_text()
    )
    assert any(
        "skill-body-size" in str(row)
        and "skills.overview" in str(row)
        and row.get("enforced_by") == "check_frontmatter"
        for row in data["check"]
    )


# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
def test_strict_profile_rejects_host_keys_and_reserved_names(tmp_path):
    clean = make_skill(tmp_path / "clean")
    assert frontmatter.strict_violations(clean) == []
    for key in frontmatter.HOST_KEYS:
        value = False if key == "disable-model-invocation" else "x"
        skill = make_skill(tmp_path / key.replace("-", "_"),
                           fields={key: value})
        assert frontmatter.strict_violations(skill)
    for word in ("claude", "anthropic"):
        skill = make_skill(tmp_path / word, name=f"{word}-example")
        assert frontmatter.strict_violations(skill)


# spec: "Expected result today: exactly `bayesian-workflow`, `tune-hyperparameters`, and `tech-debt` fail."
# task: 7
def test_strict_profile_actual_failures():
    failures = {
        skill.name for skill in skill_dirs()
        if frontmatter.strict_violations(skill)
    }
    assert failures == {
        "bayesian-workflow", "tune-hyperparameters", "tech-debt"
    }
    assert frontmatter.main(["--strict"]) != 0


# spec: "The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register")."
# task: 7
def test_frontmatter_documentation():
    docstring = frontmatter.__doc__ or ""
    for term in ("--strict", "compatibility", "metadata", "license"):
        assert term in docstring
    claude = (ROOT / "CLAUDE.md").read_text()
    commands = re.search(
        r"(?ms)^#{1,6}\s+Commands\b(.*?)(?=^#{1,6}\s+|\Z)",
        claude,
    )
    assert commands
    assert "check_frontmatter.py --strict" in commands.group(1)
    assert "claude.ai" in commands.group(1)
    assert "spec-only validator" in commands.group(1)
    assert len(claude.splitlines()) <= 200


# spec: "Record the scenario, prompts, outputs, and verdicts in `specs/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house red-baseline format."
# task: 2
def test_red_baseline_artifact_exists():
    files = list(
        (ROOT / "specs").glob(
            "red-baseline-description-openings-????-??-??.md"
        )
    )
    assert len(files) == 1
    text = files[0].read_text().lower()
    for term in ("scenario", "prompt", "output", "verdict", "150"):
        assert term in text


# spec: "The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list)."
# task: 14
def test_writing_skills_measured_note():
    text = (SKILLS / "writing-skills" / "SKILL.md").read_text()
    section = re.search(
        r"(?ms)^#{1,6}\s+Token Efficiency\s*\n"
        r"(.*?)(?=^#{1,6}\s+|\Z)",
        text,
    )
    assert section
    note = next(
        paragraph for paragraph in re.split(r"\n\s*\n", section.group(1))
        if "Codex" in paragraph and "156" in paragraph
    )
    assert 2 <= len(note.splitlines()) <= 4
    for term in ("164", "93", "0.154", "2026-10-03",
                 "codex debug prompt-input", "Skills"):
        assert term in note


# spec: "There are 16."
# task: 10
def test_runnable_script_inventory():
    actual = {
        path.resolve().relative_to(ROOT).as_posix()
        for skill in skill_dirs()
        for path in frontmatter.runnable_scripts(skill)
    }
    assert actual == EXPECTED_SCRIPTS


# spec: "`tune-hyperparameters/scripts/time_series_cv.py` has no `__main__` guard; it is a library imported into the user's code and stays header-less."
# task: 10
def test_time_series_cv_is_headerless_library():
    path = SKILLS / "tune-hyperparameters/scripts/time_series_cv.py"
    text = path.read_text()
    assert "# /// script" not in text
    assert not any(
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
        for node in ast.walk(ast.parse(text))
    )


# spec: "Then a `# /// script` block with single-quoted TOML strings, a `requires-python`, and a `dependencies` list (`[]` for stdlib-only scripts)."
# task: 10
def test_all_runnable_script_headers():
    for relative in EXPECTED_SCRIPTS:
        path = ROOT / relative
        lines = path.read_text().splitlines()
        assert lines[0] == "#!/usr/bin/env python3", path
        assert lines[1] == "# /// script", path
        end = lines.index("# ///", 2)
        block = lines[2:end]
        assert all(line.startswith("# ") for line in block), path
        assert not any('"' in line for line in block), path
        parsed = tomllib.loads("\n".join(line[2:] for line in block))
        assert frontmatter.script_metadata(path.read_text()) == parsed
        assert parsed["requires-python"] in {
            ">=3.11", ">=3.12", ">=3.13"
        }
        assert isinstance(parsed["dependencies"], list)
        for dependency in parsed["dependencies"]:
            assert re.fullmatch(
                r"[A-Za-z0-9_.-]+(?:\[[^\]]+\])?>=\d+(?:\.\d+)*",
                dependency,
            ), (path, dependency)


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_header_lint_rejects_missing_and_invalid_metadata(tmp_path):
    skill = make_skill(tmp_path)
    script = make_script(skill)
    assert frontmatter.check_script_headers(
        skill, vendored=frozenset()
    ) == []
    script.write_text(
        "#!/usr/bin/env python3\n# /// script\n"
        "# dependencies = []\n# ///\n"
        "if __name__ == '__main__':\n    pass\n"
    )
    assert frontmatter.check_script_headers(
        skill, vendored=frozenset()
    )
    script.write_text(
        "#!/usr/bin/env python3\n# /// script\n"
        "# requires-python = '>=3.11'\n# ///\n"
        "if __name__ == '__main__':\n    pass\n"
    )
    assert frontmatter.check_script_headers(
        skill, vendored=frozenset()
    )
    with pytest.raises(tomllib.TOMLDecodeError):
        frontmatter.script_metadata(
            "# /// script\n# dependencies = [\n# ///\n"
        )


# spec: "In such a script, every non-stdlib, non-local import is declared in `dependencies`:"
# task: 10
def test_import_lint_includes_function_imports_and_exempts_optional_and_local(tmp_path):
    skill = make_skill(tmp_path)
    (skill / "scripts").mkdir()
    (skill / "scripts/helper.py").write_text("def helper(): pass\n")
    body = (
        "import os\n"
        "from helper import helper\n"
        "try:\n"
        "    import optional_one\n"
        "except ImportError:\n"
        "    pass\n"
        "try:\n"
        "    import optional_two\n"
        "except ModuleNotFoundError:\n"
        "    pass\n"
        "def run():\n"
        "    import yaml\n"
        "if __name__ == '__main__':\n"
        "    run()\n"
    )
    script = make_script(skill, "['pyyaml>=6.0']", body)
    assert frontmatter.check_script_headers(
        skill, vendored=frozenset()
    ) == []
    script.write_text(script.read_text().replace(
        "['pyyaml>=6.0']", "[]"
    ))
    assert frontmatter.check_script_headers(
        skill, vendored=frozenset()
    )


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
def test_documented_invocations_use_uv():
    for skill in skill_dirs():
        assert frontmatter.check_invocations(skill) == []
        for markdown, runner, path in frontmatter.bundled_invocations(skill):
            assert markdown.suffix == ".md"
            assert runner == "uv run", (markdown, runner, path)
            assert frontmatter.resolve_bundled_script(path, skill)


# spec: "No skill markdown invokes a resolving bundled-script path with bare `python` or `python3`, including line-continued forms (`python \` followed by the path on the next line)."
# task: 11
def test_invocation_lint_catches_line_continuation_and_ignores_unresolved_example(tmp_path):
    skill = make_skill(tmp_path)
    make_script(skill)
    path = skill / "SKILL.md"
    original = path.read_text()
    path.write_text(
        original + "python \\\n<this-skill-dir>/scripts/run.py\n"
    )
    assert frontmatter.check_invocations(skill)
    path.write_text(
        original + "python3 <this-skill-dir>/scripts/run.py\n"
    )
    assert frontmatter.check_invocations(skill)
    path.write_text(original + "python scripts/migrate.py\n")
    assert frontmatter.check_invocations(skill) == []


# spec: "Each skill with such an invocation gets this sentence once, near its first invocation: "Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.""
# task: 11
def test_fallback_sentence_once_per_invoking_skill():
    invoking = set()
    for skill in skill_dirs():
        invocations = frontmatter.bundled_invocations(skill)
        if not invocations:
            continue
        invoking.add(skill.name)
        texts = [path.read_text() for path in skill.rglob("*.md")]
        assert sum(text.count(FALLBACK) for text in texts) == 1, skill
    assert "finishing-a-development-branch" in invoking


# spec: "Every skill whose markdown runs a bundled script with `uv run` declares `compatibility: Requires uv to run bundled scripts (dependencies are declared inline); Python 3.X+.`"
# task: 12
def test_compatibility_matches_highest_invoked_python_floor():
    for skill in skill_dirs():
        invocations = [
            path for _, runner, path
            in frontmatter.bundled_invocations(skill)
            if runner == "uv run"
        ]
        if not invocations:
            continue
        floors = []
        for invoked_path in invocations:
            script = frontmatter.resolve_bundled_script(
                invoked_path, skill
            )
            assert script is not None
            metadata = frontmatter.script_metadata(script.read_text())
            floors.append(tuple(map(
                int, metadata["requires-python"][2:].split(".")
            )))
        major, minor = max(floors)
        expected = (
            "Requires uv to run bundled scripts "
            "(dependencies are declared inline); "
            f"Python {major}.{minor}+."
        )
        data = skill_frontmatter(skill / "SKILL.md")
        assert data.get("compatibility") == expected, skill
        assert frontmatter._check_compatibility_names_uv(
            skill, data
        ) == []


# spec: "A skill whose markdown runs a bundled script via `uv run` declares a `compatibility` value containing `uv`."
# task: 12
def test_compatibility_lint_rejects_missing_uv(tmp_path):
    skill = make_skill(tmp_path)
    make_script(skill)
    (skill / "SKILL.md").write_text(
        (skill / "SKILL.md").read_text()
        + "uv run <this-skill-dir>/scripts/run.py\n"
    )
    assert frontmatter._check_compatibility_names_uv(skill, {})
    assert frontmatter._check_compatibility_names_uv(
        skill, {"compatibility": "Python 3.11+"}
    )
    assert frontmatter._check_compatibility_names_uv(
        skill, {"compatibility": "Requires uv; Python 3.11+"}
    ) == []


# spec: "Prose floors that disagree with the header are aligned or removed (e.g. "Python ≥ 3.9" in `recommend-probabilistic-model` and `recommend-visualization`)."
# task: 12
def test_obsolete_prose_floors_removed():
    for name in (
        "recommend-probabilistic-model", "recommend-visualization"
    ):
        text = (SKILLS / name / "SKILL.md").read_text()
        assert not re.search(
            r"Python\s*(?:≥|>=)\s*3\.9\b", text
        )


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_real_bundled_licenses_match_roots():
    names = [skill.name for skill in skill_dirs()]
    assert provenance.bundled_license_violations(
        ROOT, names, provenance.BUNDLED_LICENSES
    ) == []
    for skill in skill_dirs():
        copy = skill / "LICENSE"
        assert copy.is_file() and not copy.is_symlink()
        assert copy.read_bytes() == (ROOT / "LICENSE").read_bytes()


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_provenance_lint_rejects_missing_changed_and_symlink_copies(tmp_path):
    for variant in ("missing", "changed", "symlink"):
        repo, table = license_fixture(tmp_path / variant)
        copy = repo / "skills" / "alpha" / "LICENSE"
        if variant == "missing":
            copy.unlink()
        elif variant == "changed":
            copy.write_bytes(b"different\n")
        else:
            copy.unlink()
            copy.symlink_to(repo / "LICENSE")
        assert provenance.bundled_license_violations(
            repo, ["alpha", "beta"], table
        ), variant


# spec: "No skill directory holds a `LICENSE*` file outside its mapping."
# task: 8
def test_provenance_lint_rejects_unmapped_skill_license(tmp_path):
    repo, table = license_fixture(tmp_path)
    (repo / "skills" / "beta" / "LICENSE-surprise").write_bytes(
        b"unmapped\n"
    )
    assert provenance.bundled_license_violations(
        repo, ["alpha", "beta"], table
    )


# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
def test_provenance_lint_rejects_unmapped_root_license(tmp_path):
    repo, table = license_fixture(tmp_path)
    (repo / "LICENSE-new").write_bytes(b"new\n")
    assert provenance.bundled_license_violations(
        repo, ["alpha", "beta"], table
    )


# spec: "The script stays stdlib-only, so its CLAUDE.md command keeps no `--with`."
# task: 8
def test_provenance_lint_uses_stdlib_only():
    source = (ROOT / "build/check_provenance.py").read_text()
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(
                alias.name.split(".")[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= sys.stdlib_module_names | {"__future__"}
    claude = (ROOT / "CLAUDE.md").read_text()
    command_lines = [
        line for line in claude.splitlines()
        if "check_provenance.py" in line
    ]
    assert command_lines
    assert all("--with" not in line for line in command_lines)


# spec: "NOTICE gains one paragraph near the top: each skill directory carries copies of the license texts that apply to it, so a single-skill install (`install.py --copy --skill`, or a third-party installer) keeps the notice MIT requires."
# task: 8
def test_notice_explains_license_travel():
    notice = (ROOT / "NOTICE").read_text()
    opening = notice[: min(len(notice), 2500)]
    for term in (
        "skill directory", "license", "install.py --copy --skill",
        "third-party installer", "MIT",
    ):
        assert term in opening


# spec: "README's License section gains one sentence to the same effect."
# task: 8
def test_readme_license_section_explains_copies():
    readme = (ROOT / "README.md").read_text()
    section = re.search(
        r"(?ms)^#{1,6}\s+License\b(.*?)(?=^#{1,6}\s+|\Z)",
        readme,
    )
    assert section
    assert "skill" in section.group(1).lower()
    assert "cop" in section.group(1).lower()
    assert "license" in section.group(1).lower()


# spec: "CLAUDE.md's provenance section gains the invariant and names the enforcing lint, under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register")."
# task: 8
def test_claude_provenance_documents_invariant():
    text = (ROOT / "CLAUDE.md").read_text()
    section = re.search(
        r"(?ms)^#{1,6}\s+Provenance\b(.*?)(?=^#{1,6}\s+|\Z)",
        text,
    )
    assert section
    assert "LICENSE" in section.group(1)
    assert "check_provenance.py" in section.group(1)
    assert len(text.splitlines()) <= 200


# spec: "The root files are canonical, and `check_provenance.py` enforces the copies."
# task: 8
def test_license_mapping_matches_spec():
    table = provenance.BUNDLED_LICENSES
    assert set(table["LICENSE-coding-skills"]) == {
        "bayesian-workflow", "clean-code"
    }
    superpowers = {
        skill.name for skill in skill_dirs()
        if (skill_frontmatter(skill / "SKILL.md").get("metadata") or {})
        .get("source") == "https://github.com/obra/superpowers"
    }
    assert len(superpowers) == 13
    assert set(table["LICENSE-superpowers"]) == superpowers
    allowed = {
        "LICENSE", "LICENSE-superpowers",
        "LICENSE-coding-skills", "LICENSE-andorra",
    }
    assert set(table) <= allowed
    assert (ROOT / "LICENSE-andorra").exists() == (
        "LICENSE-andorra" in table
    )


# spec: "Every gate in CLAUDE.md's Commands passes:"
# task: 15
def test_named_command_gates_pass():
    commands = (
        ["build/check_frontmatter.py"],
        ["build/check_provenance.py"],
        ["build/check_snippets.py", "skills/"],
        ["build/check_conformance.py"],
        ["build/sync_runtime_assets.py", "--check"],
    )
    for command in commands:
        result = subprocess.run(
            [sys.executable, *command],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert result.returncode == 0, (
            command, result.stdout, result.stderr
        )


# spec: "`gemini skills list --all` shows every skill under `skills/` as `[Enabled]`;"
# task: 15
def test_gemini_loads_every_skill():
    with tempfile.TemporaryDirectory(prefix="portability-gemini-") as scratch:
        assert not Path(scratch).resolve().is_relative_to(ROOT)
        result = subprocess.run(
            ["gemini", "skills", "list", "--all"],
            cwd=scratch,
            capture_output=True,
            text=True,
            timeout=180,
        )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    for skill in skill_dirs():
        assert any(
            skill.name in line and "[Enabled]" in line
            for line in lines
        ), skill.name


# spec: "`codex debug prompt-input` lists every skill under `skills/` by name."
# task: 15
def test_codex_lists_every_skill():
    with tempfile.TemporaryDirectory(prefix="portability-codex-") as scratch:
        assert not Path(scratch).resolve().is_relative_to(ROOT)
        result = subprocess.run(
            ["codex", "debug", "prompt-input"],
            cwd=scratch,
            capture_output=True,
            text=True,
            timeout=180,
        )
    assert result.returncode == 0, result.stderr
    output = result.stdout + result.stderr
    for skill in skill_dirs():
        assert skill.name in output, skill.name
</tests>
<flags>
<flag task="1"><spec>The owner approved the design on 2026-10-03 and the written spec on 2026-10-18.</spec><plan>Produces: a spec whose counts and rules match Tasks 2–15.</plan></flag>
<flag task="7"><spec>The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").</spec><plan>Modify: `CLAUDE.md` (Commands: the frontmatter lint's comment names `--strict`; no line added, D7)</plan></flag>
<flag task="8"><spec>No skill directory holds a `LICENSE*` file outside its mapping.</spec><plan>Rename: `skills/recommend-causal-design/LICENSE` to `skills/recommend-causal-design/LICENSE-causal-design-sources`, and re-point its links in that skill's `SKILL.md`, `README.md` and `references/sources.md`</plan></flag>
<flag task="9"><spec>Nothing is bundled.</spec><plan>Create: `LICENSE-andorra` (upstream's text, verbatim) and its copy `skills/bayesian-workflow/LICENSE-andorra`</plan></flag>
<flag task="9"><spec>NOTICE is unchanged and a deferred item is logged with what was searched.</spec><plan>Modify: `build/check_provenance.py` (one `BUNDLED_LICENSES` row), `NOTICE` (`bayesian-workflow/` block), `README.md`, `CLAUDE.md`</plan></flag>
<flag task="10"><spec>Fourteen gain a header:</spec><plan>Modify: the 15 header-less runnable scripts (helper script): a shebang where missing, then the header</plan></flag>
</flags>
<untestable>
All 32 descriptions pass as of 2026-10-03.
Both pass, so neither is rewritten.
No description rewrites in this spec.
5 reps, each a fresh agent given the current `writing-skills` description guidance (the control: no new wording).
Each is asked to write a SKILL.md description for a synthetic skill that is not from this repo and has at least 8 trigger conditions, one of them designated in the scenario as primary.
Run from a session whose cwd was never this repo.
The controller reads each output and records the verbatim 150-character prefix.
Baseline ≤ 3/5: also add one checklist line ("the primary trigger falls within the first ~150 characters") and GREEN-test it: 5 reps with the new wording, at least 4/5 passing, recorded in the same red-baseline file.
Use the lowest of `'>=3.11'`, `'>=3.12'`, `'>=3.13'` under which the test suite covering the script passes, run with `uv run --python 3.X` and that suite's CLAUDE.md dependencies.
Scripts covered by one suite share its floor, unless a failure is attributable to one script, which then alone takes the higher floor.
Runtime backends that the script never imports but needs to read its inputs (e.g. `h5netcdf` for NetCDF) are added when R3.8's fixture run shows them needed.
From an empty scratch directory (a subdirectory such as `/tmp/bwprobe/`, never `/tmp` itself), each of the 16 scripts runs `uv run <absolute-path>` on a minimal real input that exercises its main code path.
`--help` alone is enough only for a script with no input-reading path.
The three ArviZ-reading scripts (`diagnose_model.py`, `calibration_check.py`, `compare_experiments.py`) each read a small saved InferenceData fixture.
One script is also run from inside a directory holding an unrelated `pyproject.toml`.
Locate Alexandre Andorra's original PyMC Bayesian-workflow skill and read its license.
Never compose a copyright line that is not quoted from the source.
When Stage A or Stage D fixes a gap the register tracks to it, the same change removes or narrows that `[[exception]]` and runs `build/check_conformance.py` (R6 P2).
Work in a worktree.
Commit from the worktree; the shared checkout's branch can change under a concurrent session.
State test changes as +N deltas against the suite, never absolute totals.
Before allocating the plan id, check `specs/plans/` on every branch (`git ls-tree`); ids are allocated per branch and have collided.
Whichever branch merges second brings the other's skills into conformance in the same merge, or the new lints fail on arrival.
Each new lint rule has a test that failed before its implementation and passes after.
R3.8's execution proof is recorded for all 16 scripts.
</untestable>