<tests>
import ast
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml

from build import check_frontmatter as frontmatter
from build import check_provenance as provenance


ROOT = Path(__file__).resolve().parent
if not (ROOT / "skills").is_dir():
    ROOT = ROOT.parent
SKILLS = ROOT / "skills"

RUNNABLE = {
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

UV_FALLBACK = (
    "Without uv, run the same path with `python3` in an environment "
    "that has the dependencies listed in the script's header."
)


def _skill_dirs():
    return sorted(path for path in SKILLS.iterdir() if (path / "SKILL.md").is_file())


def _frontmatter(path):
    match = re.match(
        r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)",
        path.read_text(),
        re.DOTALL,
    )
    assert match, path
    return yaml.safe_load(match.group(1))


def _write_skill(tmp_path, name="sample", fields=None, body="Body\n"):
    skill_dir = tmp_path / "skills" / name
    skill_dir.mkdir(parents=True)
    data = {
        "name": name,
        "description": "Use when checking a synthetic skill.",
        "license": "MIT",
    }
    if fields:
        data.update(fields)
    (skill_dir / "SKILL.md").write_text(
        "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body
    )
    return skill_dir


def _script_text(body, dependencies=()):
    deps = ", ".join(repr(dep) for dep in dependencies)
    return (
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
        f"# dependencies = [{deps}]\n"
        "# ///\n"
        f"{body}"
    )


def _write_script(skill_dir, name="run.py", text=None):
    script = skill_dir / "scripts" / name
    script.parent.mkdir(exist_ok=True)
    script.write_text(
        text
        if text is not None
        else _script_text("if __name__ == '__main__':\n    print('ok')\n")
    )
    return script


def _license_repo(tmp_path):
    (tmp_path / "LICENSE").write_bytes(b"MIT notice\n")
    (tmp_path / "LICENSE-superpowers").write_bytes(b"Superpowers notice\n")
    a = tmp_path / "skills" / "a"
    b = tmp_path / "skills" / "b"
    a.mkdir(parents=True)
    b.mkdir(parents=True)
    (a / "LICENSE").write_bytes(b"MIT notice\n")
    (a / "LICENSE-superpowers").write_bytes(b"Superpowers notice\n")
    (b / "LICENSE").write_bytes(b"MIT notice\n")
    return a, b, {"LICENSE-superpowers": ("a",)}


# spec: "Replace `ALLOWED_KEYS` with two named sets and allow their union in a `SKILL.md`:"
# task: 3
def test_frontmatter_key_sets():
    assert frontmatter.SPEC_KEYS == frozenset(
        {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    )
    assert frontmatter.HOST_KEYS == frozenset(
        {"when_to_use", "model", "effort", "context", "disable-model-invocation"}
    )
    assert frontmatter.SPEC_KEYS.isdisjoint(frontmatter.HOST_KEYS)


# spec: "When present, a mapping whose keys and values are all strings."
# task: 3
def test_metadata_requires_string_keys_and_values(tmp_path):
    path = _write_skill(tmp_path) / "SKILL.md"
    for value in ({"author": "Jesse Vincent"}, {}):
        assert not frontmatter._check_value_shapes(path, {"metadata": value})
    for value in ([], {"author": 1}, {1: "author"}):
        assert frontmatter._check_value_shapes(path, {"metadata": value})


# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
def test_compatibility_shape_and_trimmed_limit(tmp_path):
    path = _write_skill(tmp_path) / "SKILL.md"
    for value in (" x ", "x" * 500):
        assert not frontmatter._check_value_shapes(path, {"compatibility": value})
    for value in (" ", "", "x" * 501, 7):
        assert frontmatter._check_value_shapes(path, {"compatibility": value})


# spec: "`name` and `description` contain no `<` or `>`."
# task: 3
def test_angle_brackets_are_rejected_and_llm_wiki_is_fixed(tmp_path):
    path = _write_skill(tmp_path) / "SKILL.md"
    for field in ("name", "description"):
        for bracket in ("<", ">"):
            assert frontmatter._check_value_shapes(path, {field: f"bad{bracket}value"})
    for skill_dir in _skill_dirs():
        data = _frontmatter(skill_dir / "SKILL.md")
        assert not (set(data["name"]) | set(data["description"])) & {"<", ">"}
    assert "verify a page" in _frontmatter(SKILLS / "llm-wiki" / "SKILL.md")[
        "description"
    ]


# spec: "Required in every `SKILL.md`, a non-empty string (repo policy, beyond the spec)."
# task: 4
def test_license_field_is_required_and_nonempty(tmp_path):
    path = _write_skill(tmp_path) / "SKILL.md"
    assert not frontmatter._check_license(path, {"license": "MIT"})
    for data in ({}, {"license": ""}, {"license": "   "}, {"license": 3}):
        assert frontmatter._check_license(path, data)
    for skill_dir in _skill_dirs():
        value = _frontmatter(skill_dir / "SKILL.md").get("license")
        assert isinstance(value, str) and value.strip()


# spec: "The 13 superpowers skills gain `license: MIT` and"
# task: 4
def test_superpowers_frontmatter_provenance():
    matching = []
    for skill_dir in _skill_dirs():
        data = _frontmatter(skill_dir / "SKILL.md")
        if data.get("metadata", {}).get("source") == "https://github.com/obra/superpowers":
            matching.append(skill_dir.name)
            assert data["license"] == "MIT"
            assert data["metadata"]["author"] == "Jesse Vincent"
            assert data["metadata"]["adapted_by"] == "Lowell Mason"
    assert len(matching) == 13


# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
def test_disable_model_invocation_requires_boolean(tmp_path):
    skill_dir = _write_skill(tmp_path)
    assert not frontmatter._check_invocation_parity(
        skill_dir, {"disable-model-invocation": False}
    )
    assert frontmatter._check_invocation_parity(
        skill_dir, {"disable-model-invocation": "true"}
    )


# spec: "A skill with `disable-model-invocation: true` must ship `agents/openai.yaml` that parses and sets `policy.allow_implicit_invocation: false`."
# task: 5
def test_manual_only_skill_needs_codex_policy(tmp_path):
    skill_dir = _write_skill(tmp_path)
    assert frontmatter._check_invocation_parity(
        skill_dir, {"disable-model-invocation": True}
    )
    policy = skill_dir / "agents" / "openai.yaml"
    policy.parent.mkdir()
    policy.write_text("policy:\n  allow_implicit_invocation: true\n")
    assert frontmatter._check_invocation_parity(
        skill_dir, {"disable-model-invocation": True}
    )
    policy.write_text("policy:\n  allow_implicit_invocation: false\n")
    assert not frontmatter._check_invocation_parity(
        skill_dir, {"disable-model-invocation": True}
    )


# spec: "Conversely, a skill whose `agents/openai.yaml` sets that policy to `false` must set `disable-model-invocation: true`."
# task: 5
def test_codex_policy_requires_manual_only_frontmatter(tmp_path):
    skill_dir = _write_skill(tmp_path)
    policy = skill_dir / "agents" / "openai.yaml"
    policy.parent.mkdir()
    policy.write_text("policy:\n  allow_implicit_invocation: false\n")
    for data in ({}, {"disable-model-invocation": False}):
        assert frontmatter._check_invocation_parity(skill_dir, data)
    assert not frontmatter._check_invocation_parity(
        skill_dir, {"disable-model-invocation": True}
    )


# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
def test_body_warning_threshold(tmp_path):
    skill_dir = _write_skill(tmp_path, body="line\n" * 500)
    assert frontmatter.skill_body_warning(skill_dir) is None
    (skill_dir / "SKILL.md").write_text(
        (skill_dir / "SKILL.md").read_text() + "line\n"
    )
    assert frontmatter.skill_body_warning(skill_dir) is not None


# spec: "When Stage A adds this warning, it also adds a `skill-body-size` `[[check]]` to `build/cc_guide/conformance.toml` that maps `skills.overview` to it, with `enforced_by = 'check_frontmatter'` (conformance R6 P3)."
# task: 6
def test_body_size_conformance_register_entry():
    document = tomllib.loads(
        (ROOT / "build" / "cc_guide" / "conformance.toml").read_text()
    )
    entries = [entry for entry in document["check"] if "skill-body-size" in str(entry)]
    assert len(entries) == 1
    assert entries[0]["enforced_by"] == "check_frontmatter"
    assert "skills.overview" in str(entries[0])


# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
def test_strict_profile_rejects_host_keys_and_reserved_names(tmp_path):
    assert not frontmatter.strict_violations(_write_skill(tmp_path, "ordinary"))
    assert frontmatter.strict_violations(
        _write_skill(tmp_path, "host-key", {"effort": "high"})
    )
    assert frontmatter.strict_violations(_write_skill(tmp_path, "claude-helper"))
    assert frontmatter.strict_violations(_write_skill(tmp_path, "anthropic-helper"))


# spec: "The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, \"Conformance register\")."
# task: 7
def test_strict_documentation_and_claude_md_size():
    assert "--strict" in frontmatter.__doc__
    lines = (ROOT / "CLAUDE.md").read_text().splitlines()
    assert len(lines) <= 200
    commands = (ROOT / "CLAUDE.md").read_text().split("Commands", 1)[1]
    assert "check_frontmatter.py --strict" in commands
    assert "claude.ai" in commands
    assert "validator" in commands


# spec: "Record the scenario, prompts, outputs, and verdicts in `specs/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house red-baseline format."
# task: 2
def test_description_openings_baseline_record_exists():
    records = sorted(
        (ROOT / "specs").glob("red-baseline-description-openings-????-??-??.md")
    )
    assert records
    content = records[-1].read_text().lower()
    for required in ("scenario", "prompt", "output", "verdict", "150"):
        assert required in content
    assert re.search(r"\b[0-5]\s*(?:/|of)\s*5\b", content)


# spec: "The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list)."
# task: 14
def test_writing_skills_records_codex_measurement():
    text = (SKILLS / "writing-skills" / "SKILL.md").read_text()
    assert "Token Efficiency" in text
    section = text.split("Token Efficiency", 1)[1].split("\n## ", 1)[0]
    for required in (
        "Codex",
        "156",
        "164",
        "93",
        "0.154",
        "2026-10-03",
        "codex debug prompt-input",
    ):
        assert required in section


# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
def test_runnable_script_inventory():
    found = {
        str(path.relative_to(ROOT))
        for skill_dir in _skill_dirs()
        for path in frontmatter.runnable_scripts(skill_dir)
    }
    assert found == RUNNABLE
    assert not frontmatter.runnable_scripts(SKILLS / "tune-hyperparameters")


# spec: "Line 1 is `#!/usr/bin/env python3`; add it where missing."
# task: 10
def test_all_runnable_scripts_have_house_shebang():
    for relative in RUNNABLE:
        assert (ROOT / relative).read_text().splitlines()[0] == "#!/usr/bin/env python3"


# spec: "Then a `# /// script` block with single-quoted TOML strings, a `requires-python`, and a `dependencies` list (`[]` for stdlib-only scripts)."
# task: 10
def test_all_runnable_scripts_have_parseable_inline_metadata():
    for relative in RUNNABLE:
        text = (ROOT / relative).read_text()
        assert "# /// script\n" in text, relative
        block = text.split("# /// script\n", 1)[1].split("# ///\n", 1)[0]
        assert '"' not in block, relative
        metadata = frontmatter.script_metadata(text)
        assert metadata["requires-python"] in {">=3.11", ">=3.12", ">=3.13"}
        assert isinstance(metadata["dependencies"], list)
        for dependency in metadata["dependencies"]:
            assert isinstance(dependency, str)
            assert ">=" in dependency and "<" not in dependency


# spec: "Imports inside a `try` whose handler catches `ImportError` or `ModuleNotFoundError` are optional and may be left undeclared."
# task: 10
def test_import_analysis_exempts_optional_and_local_imports():
    tree = ast.parse(
        "import os\n"
        "import helper\n"
        "import yaml\n"
        "def run():\n"
        "    import numpy\n"
        "try:\n"
        "    import scipy\n"
        "except ImportError:\n"
        "    pass\n"
        "try:\n"
        "    import matplotlib\n"
        "except ModuleNotFoundError:\n"
        "    pass\n"
    )
    imports = frontmatter.required_imports(tree, {"helper"})
    assert "numpy" in imports
    assert "yaml" in imports or "pyyaml" in imports
    assert not imports & {"os", "helper", "scipy", "matplotlib"}


# spec: "In such a script, every non-stdlib, non-local import is declared in `dependencies`:"
# task: 10
def test_script_header_lint_detects_missing_header_and_dependency(tmp_path):
    skill_dir = _write_skill(tmp_path)
    script = _write_script(
        skill_dir,
        text="import yaml\nif __name__ == '__main__':\n    print(yaml.__name__)\n",
    )
    assert frontmatter.check_script_headers(skill_dir)
    script.write_text(
        _script_text(
            "import yaml\nif __name__ == '__main__':\n    print(yaml.__name__)\n"
        )
    )
    assert frontmatter.check_script_headers(skill_dir)
    script.write_text(
        _script_text(
            "import yaml\nif __name__ == '__main__':\n    print(yaml.__name__)\n",
            dependencies=("pyyaml>=6.0",),
        )
    )
    assert not frontmatter.check_script_headers(skill_dir)


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_script_header_lint_accepts_actual_inventory():
    for skill_dir in _skill_dirs():
        assert not frontmatter.check_script_headers(skill_dir), skill_dir


# spec: "No skill markdown invokes a resolving bundled-script path with bare `python` or `python3`, including line-continued forms (`python \\` followed by the path on the next line)."
# task: 11
def test_invocation_lint_catches_bare_and_continued_python(tmp_path):
    for command in (
        "python <this-skill-dir>/scripts/run.py",
        "python3 <this-skill-dir>/scripts/run.py",
        "python \\\n<this-skill-dir>/scripts/run.py",
    ):
        skill_dir = _write_skill(tmp_path / str(len(command)), body=f"```sh\n{command}\n```\n")
        _write_script(skill_dir)
        assert frontmatter.check_invocations(skill_dir), command


# spec: "A path that does not resolve to a bundled script, such as `writing-skills/anthropic-best-practices.md`'s teaching example `scripts/migrate.py`, is not flagged."
# task: 11
def test_invocation_lint_ignores_unresolved_teaching_example(tmp_path):
    skill_dir = _write_skill(
        tmp_path, body="```sh\npython scripts/migrate.py\n```\n"
    )
    assert not frontmatter.check_invocations(skill_dir)


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
def test_documented_bundled_invocations_use_uv_run():
    for skill_dir in _skill_dirs():
        assert not frontmatter.check_invocations(skill_dir), skill_dir
        for _, runner, path in frontmatter.bundled_invocations(skill_dir):
            assert runner == "uv run", (skill_dir, path)
            assert frontmatter.resolve_bundled_script(path, skill_dir) is not None


# spec: "Each skill with such an invocation gets this sentence once, near its first invocation: \"Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.\""
# task: 11
def test_uv_fallback_sentence_occurs_once_per_invoking_skill():
    for skill_dir in _skill_dirs():
        if frontmatter.bundled_invocations(skill_dir):
            markdown = "\n".join(
                path.read_text() for path in skill_dir.rglob("*.md")
            )
            assert markdown.count(UV_FALLBACK) == 1, skill_dir


# spec: "Prose floors that disagree with the header are aligned or removed (e.g. \"Python ≥ 3.9\" in `recommend-probabilistic-model` and `recommend-visualization`)."
# task: 12
def test_outdated_python_prose_floors_are_removed():
    for name in ("recommend-probabilistic-model", "recommend-visualization"):
        text = (SKILLS / name / "SKILL.md").read_text()
        assert "Python ≥ 3.9" not in text


# spec: "Every skill whose markdown runs a bundled script with `uv run` declares `compatibility: Requires uv to run bundled scripts (dependencies are declared inline); Python 3.X+.`"
# task: 12
def test_compatibility_matches_highest_invoked_script_floor():
    invoking = set()
    for skill_dir in _skill_dirs():
        invocations = frontmatter.bundled_invocations(skill_dir)
        if not invocations:
            continue
        invoking.add(skill_dir.name)
        floors = []
        for _, runner, path in invocations:
            assert runner == "uv run"
            script = frontmatter.resolve_bundled_script(path, skill_dir)
            assert script is not None
            floor = frontmatter.script_metadata(script.read_text())["requires-python"]
            assert re.fullmatch(r">=3\.(11|12|13)", floor)
            floors.append(int(floor.split(".")[1]))
        expected = (
            "Requires uv to run bundled scripts (dependencies are declared inline); "
            f"Python 3.{max(floors)}+."
        )
        assert _frontmatter(skill_dir / "SKILL.md")["compatibility"] == expected
    assert "finishing-a-development-branch" in invoking


# spec: "A skill whose markdown runs a bundled script via `uv run` declares a `compatibility` value containing `uv`."
# task: 12
def test_compatibility_lint_requires_uv(tmp_path):
    skill_dir = _write_skill(
        tmp_path, body="```sh\nuv run <this-skill-dir>/scripts/run.py\n```\n"
    )
    _write_script(skill_dir)
    assert frontmatter._check_compatibility_names_uv(skill_dir, {})
    assert frontmatter._check_compatibility_names_uv(
        skill_dir, {"compatibility": "Python 3.11+."}
    )
    assert not frontmatter._check_compatibility_names_uv(
        skill_dir, {"compatibility": "Requires uv; Python 3.11+."}
    )


# spec: "Each skill directory carries regular files (never symlinks, which `install.py --copy` refuses) that are byte-identical to the root license files and carry the same names:"
# task: 8
def test_actual_bundled_license_copies_and_mapping():
    table = provenance.BUNDLED_LICENSES
    assert provenance.PLAIN_LICENSE == "LICENSE"
    assert set(table["LICENSE-coding-skills"]) == {"bayesian-workflow", "clean-code"}
    superpowers = {
        skill_dir.name
        for skill_dir in _skill_dirs()
        if _frontmatter(skill_dir / "SKILL.md").get("metadata", {}).get("source")
        == "https://github.com/obra/superpowers"
    }
    assert set(table["LICENSE-superpowers"]) == superpowers
    for skill_dir in _skill_dirs():
        expected = {"LICENSE"} | {
            root_name
            for root_name, names in table.items()
            if skill_dir.name in names
        }
        assert {path.name for path in skill_dir.glob("LICENSE*")} == expected
        for root_name in expected:
            bundled = skill_dir / root_name
            assert bundled.is_file() and not bundled.is_symlink()
            assert bundled.read_bytes() == (ROOT / root_name).read_bytes()


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_provenance_lint_rejects_missing_and_changed_copy(tmp_path):
    a, _, table = _license_repo(tmp_path)
    assert not provenance.bundled_license_violations(tmp_path, ["a", "b"], table)
    copy = a / "LICENSE-superpowers"
    copy.unlink()
    assert provenance.bundled_license_violations(tmp_path, ["a", "b"], table)
    copy.write_bytes(b"changed\n")
    assert provenance.bundled_license_violations(tmp_path, ["a", "b"], table)


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_provenance_lint_rejects_symlink_copy(tmp_path):
    a, _, table = _license_repo(tmp_path)
    copy = a / "LICENSE-superpowers"
    copy.unlink()
    copy.symlink_to(tmp_path / "LICENSE-superpowers")
    assert provenance.bundled_license_violations(tmp_path, ["a", "b"], table)


# spec: "No skill directory holds a `LICENSE*` file outside its mapping."
# task: 8
def test_provenance_lint_rejects_unmapped_skill_license(tmp_path):
    _, b, table = _license_repo(tmp_path)
    (b / "LICENSE-extra").write_bytes(b"extra\n")
    assert provenance.bundled_license_violations(tmp_path, ["a", "b"], table)


# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
def test_provenance_lint_rejects_unmapped_root_license(tmp_path):
    _license_repo(tmp_path)
    (tmp_path / "LICENSE-extra").write_bytes(b"extra\n")
    assert provenance.bundled_license_violations(
        tmp_path, ["a", "b"], {"LICENSE-superpowers": ("a",)}
    )


# spec: "NOTICE gains one paragraph near the top: each skill directory carries copies of the license texts that apply to it, so a single-skill install (`install.py --copy --skill`, or a third-party installer) keeps the notice MIT requires."
# task: 8
def test_license_travel_documentation():
    notice = (ROOT / "NOTICE").read_text()
    readme = (ROOT / "README.md").read_text()
    claude = (ROOT / "CLAUDE.md").read_text()
    assert "install.py --copy --skill" in notice
    assert "check_provenance.py" in notice
    assert "license" in readme.lower() and "skill" in readme.lower()
    assert "check_provenance.py" in claude
    assert len(claude.splitlines()) <= 200


# spec: "Add the upstream license text verbatim as root `LICENSE-andorra`, map it to `bayesian-workflow`, and extend NOTICE's `bayesian-workflow/` block with the source URL and the quoted copyright line."
# task: 9
def test_andorra_notice_branch_is_consistent_if_present():
    root_license = ROOT / "LICENSE-andorra"
    mapped = provenance.BUNDLED_LICENSES.get("LICENSE-andorra")
    if not root_license.exists():
        assert mapped is None
        return
    assert set(mapped) == {"bayesian-workflow"}
    assert (SKILLS / "bayesian-workflow" / "LICENSE-andorra").read_bytes() == (
        root_license.read_bytes()
    )
    notice = (ROOT / "NOTICE").read_text()
    copyright_lines = [
        line.strip()
        for line in root_license.read_text().splitlines()
        if "copyright" in line.lower() and line.strip()
    ]
    assert copyright_lines
    assert any(line in notice for line in copyright_lines)


# spec: "Every gate in CLAUDE.md's Commands passes:"
# task: 15
def test_frontmatter_and_provenance_commands_pass():
    for script in ("check_frontmatter.py", "check_provenance.py"):
        result = subprocess.run(
            [sys.executable, str(ROOT / "build" / script)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, (script, result.stdout, result.stderr)
        if script == "check_frontmatter.py":
            warnings = [
                line for line in result.stderr.splitlines() if "WARN" in line
            ]
            assert len(warnings) == 1
            assert "writing-skills" in warnings[0]


# spec: "`check_frontmatter.py --strict` fails on exactly `bayesian-workflow`, `tune-hyperparameters`, and `tech-debt`."
# task: 15
def test_strict_failure_set_is_exact():
    failing = {
        skill_dir.name
        for skill_dir in _skill_dirs()
        if frontmatter.strict_violations(skill_dir)
    }
    assert failing == {"bayesian-workflow", "tune-hyperparameters", "tech-debt"}
    result = subprocess.run(
        [sys.executable, str(ROOT / "build" / "check_frontmatter.py"), "--strict"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
</tests>
<flags>
<flag task="1"><spec>**Status: APPROVED (2026-10-18).** The owner approved the design on 2026-10-03 and the written spec on 2026-10-18. Next step: an implementation plan from the writing-plans skill.</spec><plan>Modify: `specs/agent-skills-portability-spec.md` (R1.1, R2.1, R2.3, R3.1, R3.5, R3.7, R3.8, Sequencing, Validation 4 and 6, Out of scope)</plan></flag>
<flag task="7"><spec>CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").</spec><plan>Modify: `CLAUDE.md` (Commands: the frontmatter lint's comment names `--strict`; no line added, D7)</plan></flag>
<flag task="8"><spec>No skill directory holds a `LICENSE*` file outside its mapping.</spec><plan>Rename: `skills/recommend-causal-design/LICENSE` to `skills/recommend-causal-design/LICENSE-causal-design-sources`, and re-point its links in that skill's `SKILL.md`, `README.md` and `references/sources.md`</plan></flag>
<flag task="9"><spec>`LICENSE-andorra` | `bayesian-workflow` | only if R4.5 finds an upstream notice</spec><plan>Create: `LICENSE-andorra` (upstream's text, verbatim) and its copy `skills/bayesian-workflow/LICENSE-andorra`</plan></flag>
<flag task="10"><spec>There are 16. Fourteen gain a header:</spec><plan>Modify: the 15 header-less runnable scripts (helper script): a shebang where missing, then the header</plan></flag>
</flags>
<untestable>
Criterion: within its first 150 characters, a description names the skill's primary trigger, the task or symptom it exists for, so an agent shown only that prefix would load it for its canonical use.
All 32 descriptions pass as of 2026-10-03.
5 reps, each a fresh agent given the current `writing-skills` description guidance (the control: no new wording).
Each is asked to write a SKILL.md description for a synthetic skill that is not from this repo and has at least 8 trigger conditions, one of them designated in the scenario as primary.
Run from a session whose cwd was never this repo.
A rep passes if the designated primary trigger lies within the first 150 characters.
The controller reads each output and records the verbatim 150-character prefix.
Baseline ≥ 4/5: add only a factual note of 2–4 lines to `writing-skills`' "Token Efficiency" section.
Baseline ≤ 3/5: also add one checklist line ("the primary trigger falls within the first ~150 characters") and GREEN-test it: 5 reps with the new wording, at least 4/5 passing, recorded in the same red-baseline file.
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
The 2026-08-26 intake review (`specs/completed/skill-intake-review-2026-08-26.md`) already found that Andorra appears nowhere in the history of pymc-labs/python-analytics-skills (only Fonnesbeck and Dean commit there), so start the search from his own publications rather than that repository.
Work in a worktree.
Commit from the worktree; the shared checkout's branch can change under a concurrent session.
Stage D's micro-test runs from a session whose cwd was never this repo; inherited session context voids reps otherwise.
State test changes as +N deltas against the suite, never absolute totals.
Before allocating the plan id, check `specs/plans/` on every branch (`git ls-tree`); ids are allocated per branch and have collided.
Whichever branch merges second brings the other's skills into conformance in the same merge, or the new lints fail on arrival.
Each new lint rule has a test that failed before its implementation and passes after.
`gemini skills list --all` shows every skill under `skills/` as `[Enabled]`;
`codex debug prompt-input` lists every skill under `skills/` by name.
</untestable>