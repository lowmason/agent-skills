<tests>
import ast
import re
import sys
import tomllib
from datetime import date
from pathlib import Path

import pytest
import yaml

from build import check_frontmatter as frontmatter
from build import check_provenance as provenance


ROOT = Path(frontmatter.__file__).resolve().parents[1]
MISSING = object()
SUPERPOWERS_SOURCE = "https://github.com/obra/superpowers"
FALLBACK = (
    "Without uv, run the same path with `python3` in an environment "
    "that has the dependencies listed in the script's header."
)
RUNNABLE_SCRIPTS = {
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


def _skill_dirs():
    return sorted(
        path for path in (ROOT / "skills").iterdir() if path.is_dir()
    )


def _read_frontmatter(skill_dir):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    assert match is not None, skill_dir
    data = yaml.safe_load(match.group(1))
    assert isinstance(data, dict), skill_dir
    return data


def _write_skill(skill_dir, data, body=""):
    skill_dir.mkdir(parents=True, exist_ok=True)
    text = "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body
    (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")


def _make_skill(root, name="example-skill", overrides=None, body=""):
    skill_dir = root / "skills" / name
    data = {
        "name": name,
        "description": "Use when testing an independent acceptance scenario.",
        "license": "MIT",
    }
    if overrides:
        data.update(overrides)
    _write_skill(skill_dir, data, body)
    return skill_dir


def _write_script(
    skill_dir,
    source="",
    dependencies=(),
    requires_python=">=3.11",
    filename="example.py",
):
    script = skill_dir / "scripts" / filename
    script.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        f"# requires-python = {requires_python!r}\n"
        f"# dependencies = {list(dependencies)!r}\n"
        "# ///\n"
    )
    script.write_text(
        header
        + source
        + "\nif __name__ == '__main__':\n    pass\n",
        encoding="utf-8",
    )
    return script


def _metadata_payload(text):
    lines = text.splitlines()
    assert lines.count("# /// script") == 1
    start = lines.index("# /// script")
    end = lines.index("# ///", start + 1)
    payload = []
    for line in lines[start + 1 : end]:
        assert line.startswith("#")
        payload.append(line[2:] if line.startswith("# ") else line[1:])
    return "\n".join(payload)


def _section(text, title):
    heading = re.search(
        rf"(?im)^(#+)[ \t]+{re.escape(title)}[ \t]*$",
        text,
    )
    assert heading is not None, title
    remainder = text[heading.end() :]
    following = re.search(
        rf"(?m)^#{{1,{len(heading.group(1))}}}[ \t]+\S",
        remainder,
    )
    return remainder[: following.start()] if following else remainder


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _strings(key)
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _invocation_fixture(root):
    skill_dir = _make_skill(root, name="llm-wiki")
    script = _write_script(skill_dir, filename="lint_wiki.py")
    return skill_dir, script


def _license_fixture(root):
    skills = ["bayesian-workflow", "clean-code"]
    table = {"LICENSE-coding-skills": tuple(skills)}
    (root / "LICENSE").write_bytes(b"canonical original-work license\n")
    (root / "LICENSE-coding-skills").write_bytes(
        b"canonical adapted-content license\n"
    )
    for name in skills:
        skill_dir = root / "skills" / name
        skill_dir.mkdir(parents=True)
        for filename in ("LICENSE", "LICENSE-coding-skills"):
            (skill_dir / filename).write_bytes((root / filename).read_bytes())
    return skills, table


# spec: "Replace `ALLOWED_KEYS` with two named sets and allow their union in a `SKILL.md`:"
# task: 3
def test_frontmatter_key_sets_match_the_spec():
    assert frontmatter.SPEC_KEYS == {
        "name",
        "description",
        "license",
        "compatibility",
        "metadata",
        "allowed-tools",
    }
    assert frontmatter.HOST_KEYS == {
        "when_to_use",
        "model",
        "effort",
        "context",
        "disable-model-invocation",
    }
    assert not hasattr(frontmatter, "ALLOWED_KEYS")


@pytest.mark.parametrize(
    ("value", "valid"),
    [
        ({}, True),
        ({"author": "Jesse Vincent", "adapted_by": "Lowell Mason"}, True),
        ({"author": ""}, True),
        (None, False),
        ("author", False),
        ([], False),
        ({1: "author"}, False),
        ({"author": 1}, False),
        ({"author": True}, False),
        ({"author": None}, False),
        ({"author": ["Jesse Vincent"]}, False),
        ({"author": {"name": "Jesse Vincent"}}, False),
    ],
)
# spec: "When present, a mapping whose keys and values are all strings."
# task: 3
def test_metadata_shape(tmp_path, value, valid):
    skill_dir = _make_skill(tmp_path, overrides={"metadata": value})
    errors = frontmatter._check_value_shapes(
        skill_dir / "SKILL.md", _read_frontmatter(skill_dir)
    )
    assert bool(errors) is not valid


@pytest.mark.parametrize(
    ("value", "valid"),
    [
        ("x", True),
        ("x" * 500, True),
        (" \n" + "x" * 500 + "\n ", True),
        ("", False),
        (" \n\t ", False),
        ("x" * 501, False),
        (None, False),
        (True, False),
        (500, False),
        ([], False),
    ],
)
# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
def test_compatibility_shape_and_boundaries(tmp_path, value, valid):
    skill_dir = _make_skill(tmp_path, overrides={"compatibility": value})
    errors = frontmatter._check_value_shapes(
        skill_dir / "SKILL.md", _read_frontmatter(skill_dir)
    )
    assert frontmatter.COMPATIBILITY_CAP == 500
    assert bool(errors) is not valid


@pytest.mark.parametrize("field", ["name", "description"])
@pytest.mark.parametrize("bracket", ["<", ">"])
# spec: "`name` and `description` contain no `<` or `>`."
# task: 3
def test_angle_brackets_are_rejected(tmp_path, field, bracket):
    skill_dir = _make_skill(tmp_path, overrides={field: f"example{bracket}"})
    assert frontmatter._check_value_shapes(
        skill_dir / "SKILL.md", _read_frontmatter(skill_dir)
    )


# spec: "Fix llm-wiki's trigger phrase `'verify <page>'` to `'verify a page'`."
# task: 3
def test_llm_wiki_uses_the_wording_equivalent_trigger():
    description = _read_frontmatter(ROOT / "skills" / "llm-wiki")["description"]
    assert "verify a page" in description
    assert "verify <page>" not in description


@pytest.mark.parametrize(
    ("value", "valid"),
    [
        (MISSING, False),
        ("", False),
        (None, False),
        (True, False),
        (1, False),
        ([], False),
        ({}, False),
        ("MIT", True),
    ],
)
# spec: "Required in every `SKILL.md`, a non-empty string (repo policy, beyond the spec)."
# task: 4
def test_license_is_a_required_nonempty_string(tmp_path, value, valid):
    skill_dir = _make_skill(tmp_path)
    data = _read_frontmatter(skill_dir)
    if value is MISSING:
        data.pop("license")
    else:
        data["license"] = value
    errors = frontmatter._check_license(skill_dir / "SKILL.md", data)
    assert bool(errors) is not valid


# spec: "**Frontmatter** carries the license fields per R1.4."
# task: 4
def test_repository_license_fields_and_superpowers_metadata():
    superpowers = []
    for skill_dir in _skill_dirs():
        data = _read_frontmatter(skill_dir)
        assert isinstance(data.get("license"), str), skill_dir
        assert data["license"], skill_dir
        metadata = data.get("metadata", {})
        if metadata.get("source") == SUPERPOWERS_SOURCE:
            superpowers.append(skill_dir.name)
            assert data["license"] == "MIT", skill_dir
            assert metadata["author"] == "Jesse Vincent", skill_dir
            assert metadata["adapted_by"] == "Lowell Mason", skill_dir
    assert len(superpowers) == 13


@pytest.mark.parametrize("value", ["true", "false", 0, 1, None, [], {}])
# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
def test_disable_model_invocation_rejects_non_booleans(tmp_path, value):
    skill_dir = _make_skill(
        tmp_path, overrides={"disable-model-invocation": value}
    )
    assert frontmatter._check_invocation_parity(
        skill_dir, _read_frontmatter(skill_dir)
    )


@pytest.mark.parametrize("value", [False, True])
# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
def test_disable_model_invocation_accepts_yaml_booleans(tmp_path, value):
    skill_dir = _make_skill(
        tmp_path, overrides={"disable-model-invocation": value}
    )
    if value:
        policy = skill_dir / "agents" / "openai.yaml"
        policy.parent.mkdir()
        policy.write_text(
            "policy:\n  allow_implicit_invocation: false\n", encoding="utf-8"
        )
    assert frontmatter._check_invocation_parity(
        skill_dir, _read_frontmatter(skill_dir)
    ) == []


@pytest.mark.parametrize(
    "policy_text",
    [
        None,
        "policy: [\n",
        "false\n",
        "[]\n",
        "{}\n",
        "policy: false\n",
        "policy: {}\n",
        "policy:\n  allow_implicit_invocation: true\n",
        "policy:\n  allow_implicit_invocation: 'false'\n",
        "policy:\n  allow_implicit_invocation: 0\n",
    ],
)
# spec: "A skill with `disable-model-invocation: true` must ship `agents/openai.yaml` that parses and sets `policy.allow_implicit_invocation: false`."
# task: 5
def test_manual_only_skill_requires_a_parsing_false_codex_policy(
    tmp_path, policy_text
):
    skill_dir = _make_skill(
        tmp_path, overrides={"disable-model-invocation": True}
    )
    if policy_text is not None:
        policy = skill_dir / "agents" / "openai.yaml"
        policy.parent.mkdir()
        policy.write_text(policy_text, encoding="utf-8")
    assert frontmatter._check_invocation_parity(
        skill_dir, _read_frontmatter(skill_dir)
    )


@pytest.mark.parametrize("value", [MISSING, False, "true"])
# spec: "Conversely, a skill whose `agents/openai.yaml` sets that policy to `false` must set `disable-model-invocation: true`."
# task: 5
def test_false_codex_policy_requires_true_claude_setting(tmp_path, value):
    skill_dir = _make_skill(tmp_path)
    data = _read_frontmatter(skill_dir)
    if value is not MISSING:
        data["disable-model-invocation"] = value
    policy = skill_dir / "agents" / "openai.yaml"
    policy.parent.mkdir()
    policy.write_text(
        "policy:\n  allow_implicit_invocation: false\n", encoding="utf-8"
    )
    assert frontmatter._check_invocation_parity(skill_dir, data)


@pytest.mark.parametrize(("lines", "warns"), [(0, False), (500, False), (501, True)])
# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
def test_body_advisory_boundary(tmp_path, lines, warns):
    skill_dir = _make_skill(tmp_path, body="body line\n" * lines)
    warning = frontmatter.skill_body_warning(skill_dir)
    assert (warning is not None) is warns


# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
def test_frontmatter_lines_do_not_count_toward_the_body(tmp_path):
    skill_dir = _make_skill(
        tmp_path,
        overrides={"metadata": {f"key-{i}": "value" for i in range(501)}},
        body="one body line\n",
    )
    assert frontmatter.skill_body_warning(skill_dir) is None


# spec: "`check_frontmatter.py` (exit 0; the only `WARN` is `writing-skills`' body length)"
# task: 7
def test_default_gate_succeeds_with_only_the_writing_skills_warning(capsys):
    assert frontmatter.main([]) == 0
    captured = capsys.readouterr()
    warnings = [
        line
        for line in captured.err.splitlines()
        if re.search(r"\bWARN\b", line)
    ]
    assert len(warnings) == 1
    assert "writing-skills" in warnings[0]
    for skill_dir in _skill_dirs():
        assert (frontmatter.skill_body_warning(skill_dir) is not None) is (
            skill_dir.name == "writing-skills"
        )


# spec: "When Stage A adds this warning, it also adds a `skill-body-size` `[[check]]` to `build/cc_guide/conformance.toml` that maps `skills.overview` to it, with `enforced_by = 'check_frontmatter'` (conformance R6 P3)."
# task: 6
def test_body_advisory_has_the_required_conformance_entry():
    config = tomllib.loads(
        (ROOT / "build" / "cc_guide" / "conformance.toml").read_text(
            encoding="utf-8"
        )
    )
    checks = [
        entry
        for entry in config["check"]
        if "skill-body-size" in set(_strings(entry))
    ]
    assert len(checks) == 1
    assert "skills.overview" in set(_strings(checks[0]))
    assert checks[0]["enforced_by"] == "check_frontmatter"


@pytest.mark.parametrize(
    "key",
    [
        "when_to_use",
        "model",
        "effort",
        "context",
        "disable-model-invocation",
    ],
)
# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
def test_strict_rejects_every_host_key_even_when_false(tmp_path, key):
    value = False if key == "disable-model-invocation" else "example"
    skill_dir = _make_skill(tmp_path, overrides={key: value})
    assert frontmatter.strict_violations(skill_dir)


@pytest.mark.parametrize(
    "name",
    [
        "claude-helper",
        "helper-claude",
        "myclaudetool",
        "anthropic-helper",
        "helper-anthropic",
        "myanthropictool",
    ],
)
# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
def test_strict_rejects_reserved_substrings(tmp_path, name):
    skill_dir = _make_skill(tmp_path, name=name)
    assert frontmatter.strict_violations(skill_dir)


# spec: "`check_frontmatter.py --strict` fails on exactly `bayesian-workflow`, `tune-hyperparameters`, and `tech-debt`."
# task: 7
def test_strict_repository_failures_are_exactly_the_three_named_skills(capsys):
    failures = {
        skill_dir.name
        for skill_dir in _skill_dirs()
        if frontmatter.strict_violations(skill_dir)
    }
    assert failures == {
        "bayesian-workflow",
        "tune-hyperparameters",
        "tech-debt",
    }
    assert frontmatter.main(["--strict"]) != 0
    capsys.readouterr()


# spec: "The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register")."
# task: 7
def test_commands_section_contains_the_strict_invocation():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    commands = _section(text, "Commands")
    assert re.search(r"check_frontmatter\.py[ \t]+--strict\b", commands)


# spec: "The CLAUDE.md lines from R1.9 and R4.4 stay under the `claude-md-size` check's 200-line limit in `build/cc_guide/conformance.toml`."
# task: 8
def test_claude_md_stays_within_200_lines():
    assert len(
        (ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()
    ) <= 200


# spec: "Record the scenario, prompts, outputs, and verdicts in `specs/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house red-baseline format."
# task: 2
def test_a_dated_description_baseline_artifact_exists():
    artifacts = sorted(
        (ROOT / "specs").glob(
            "red-baseline-description-openings-????-??-??.md"
        )
    )
    assert artifacts
    for artifact in artifacts:
        date.fromisoformat(
            artifact.stem.removeprefix("red-baseline-description-openings-")
        )
        assert artifact.read_text(encoding="utf-8").strip()


# spec: "The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list)."
# task: 14
def test_token_efficiency_records_the_measurement_and_remeasurement_command():
    text = (ROOT / "skills" / "writing-skills" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    section = _section(text, "Token Efficiency")
    assert "Codex" in section
    assert re.search(r"156\s*[–-]\s*164", section)
    assert re.search(r"\b93\b", section)
    assert "0.154" in section
    assert "2026-10-03" in section
    assert "codex debug prompt-input" in section


# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
def test_runnable_inventory_is_the_sixteen_scripts_named_by_the_spec():
    actual = {
        script.resolve()
        for skill_dir in _skill_dirs()
        for script in frontmatter.runnable_scripts(skill_dir)
    }
    assert actual == {(ROOT / name).resolve() for name in RUNNABLE_SCRIPTS}


@pytest.mark.parametrize(
    "guard",
    [
        'if __name__ == "__main__":\n    pass\n',
        "if '__main__' == __name__:\n    pass\n",
        "if (__name__ == '__main__'):\n    pass\n",
    ],
)
# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
def test_runnable_inventory_recognizes_main_guards(tmp_path, guard):
    skill_dir = _make_skill(tmp_path)
    script = skill_dir / "scripts" / "example.py"
    script.parent.mkdir()
    script.write_text(guard, encoding="utf-8")
    assert {
        path.resolve() for path in frontmatter.runnable_scripts(skill_dir)
    } == {script.resolve()}


@pytest.mark.parametrize(
    "source",
    [
        "def example():\n    return 1\n",
        "# if __name__ == '__main__':\n",
        'EXAMPLE = "if __name__ == \'__main__\':"\n',
    ],
)
# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
def test_non_runnable_library_files_are_not_inventoried(tmp_path, source):
    skill_dir = _make_skill(tmp_path)
    script = skill_dir / "scripts" / "example.py"
    script.parent.mkdir()
    script.write_text(source, encoding="utf-8")
    assert frontmatter.runnable_scripts(skill_dir) == []


# spec: "`tune-hyperparameters/scripts/time_series_cv.py` has no `__main__` guard; it is a library imported into the user's code and stays header-less."
# task: 10
def test_time_series_cv_remains_a_headerless_library():
    skill_dir = ROOT / "skills" / "tune-hyperparameters"
    script = skill_dir / "scripts" / "time_series_cv.py"
    assert script.resolve() not in {
        path.resolve() for path in frontmatter.runnable_scripts(skill_dir)
    }
    assert frontmatter.script_metadata(
        script.read_text(encoding="utf-8")
    ) is None


# spec: "Then a `# /// script` block with single-quoted TOML strings, a `requires-python`, and a `dependencies` list (`[]` for stdlib-only scripts)."
# task: 10
def test_script_metadata_parser_reads_the_required_fields():
    text = (
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
        "# dependencies = []\n"
        "# ///\n"
    )
    assert frontmatter.script_metadata(text) == {
        "requires-python": ">=3.11",
        "dependencies": [],
    }
    assert frontmatter.script_metadata("print('example')\n") is None


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_malformed_toml_is_reported_as_a_header_violation(tmp_path):
    skill_dir = _make_skill(tmp_path)
    script = _write_script(skill_dir)
    text = script.read_text(encoding="utf-8").replace(
        "# dependencies = []", "# dependencies = ["
    )
    script.write_text(text, encoding="utf-8")
    with pytest.raises(tomllib.TOMLDecodeError):
        frontmatter.script_metadata(text)
    assert frontmatter.check_script_headers(skill_dir, vendored=frozenset())


@pytest.mark.parametrize(
    "header",
    [
        "",
        "# /// script\n# dependencies = []\n# ///\n",
        "# /// script\n# requires-python = '>=3.11'\n# ///\n",
    ],
)
# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_missing_header_or_required_metadata_is_rejected(tmp_path, header):
    skill_dir = _make_skill(tmp_path)
    script = skill_dir / "scripts" / "example.py"
    script.parent.mkdir()
    script.write_text(
        "#!/usr/bin/env python3\n"
        + header
        + "if __name__ == '__main__':\n    pass\n",
        encoding="utf-8",
    )
    assert frontmatter.check_script_headers(skill_dir, vendored=frozenset())


# spec: "Line 1 is `#!/usr/bin/env python3`; add it where missing."
# task: 10
def test_every_runnable_script_has_the_required_shebang():
    for name in sorted(RUNNABLE_SCRIPTS):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert text.splitlines()[0] == "#!/usr/bin/env python3", name


# spec: "Then a `# /// script` block with single-quoted TOML strings, a `requires-python`, and a `dependencies` list (`[]` for stdlib-only scripts)."
# task: 10
def test_every_runnable_header_parses_and_uses_the_house_form():
    for name in sorted(RUNNABLE_SCRIPTS):
        text = (ROOT / name).read_text(encoding="utf-8")
        payload = _metadata_payload(text)
        metadata = tomllib.loads(payload)
        assert frontmatter.script_metadata(text) == metadata, name
        assert metadata["requires-python"] in {
            ">=3.11",
            ">=3.12",
            ">=3.13",
        }, name
        assert isinstance(metadata["dependencies"], list), name
        assert f"'{metadata['requires-python']}'" in payload, name
        for dependency in metadata["dependencies"]:
            assert isinstance(dependency, str), name
            assert f"'{dependency}'" in payload, name


# spec: "Every third-party import, including function-level imports, is declared with a `>=` floor at the major version the suite currently resolves (e.g. `'polars>=1.0'`)."
# task: 10
def test_repository_dependency_declarations_have_lower_bounds():
    for name in sorted(RUNNABLE_SCRIPTS):
        metadata = tomllib.loads(
            _metadata_payload((ROOT / name).read_text(encoding="utf-8"))
        )
        for dependency in metadata["dependencies"]:
            assert ">=" in dependency, (name, dependency)
            assert re.search(r">=\s*\d", dependency), (name, dependency)
            assert "<" not in dependency, (name, dependency)
            assert "==" not in dependency, (name, dependency)
            assert "~=" not in dependency, (name, dependency)


@pytest.mark.parametrize(
    "source",
    [
        "import polars\n",
        "from polars import DataFrame\n",
        "def example():\    import polars\n".replace("\\    ", "\n    "),
    ],
)
# spec: "Every third-party import, including function-level imports, is declared with a `>=` floor at the major version the suite currently resolves (e.g. `'polars>=1.0'`)."
# task: 10
def test_required_third_party_imports_need_a_dependency(tmp_path, source):
    skill_dir = _make_skill(tmp_path)
    _write_script(skill_dir, source=source)
    assert frontmatter.check_script_headers(skill_dir, vendored=frozenset())
    _write_script(
        skill_dir, source=source, dependencies=("polars>=1.0",)
    )
    assert frontmatter.check_script_headers(
        skill_dir, vendored=frozenset()
    ) == []


# spec: "import names map to distributions through a small alias table, e.g. `yaml` → `pyyaml`;"
# task: 10
def test_yaml_import_is_satisfied_by_the_pyyaml_distribution(tmp_path):
    skill_dir = _make_skill(tmp_path)
    _write_script(
        skill_dir,
        source="from yaml import safe_load\n",
        dependencies=("pyyaml>=1.0",),
    )
    assert frontmatter.check_script_headers(
        skill_dir, vendored=frozenset()
    ) == []


# spec: "In such a script, every non-stdlib, non-local import is declared in `dependencies`:"
# task: 10
def test_stdlib_and_sibling_imports_need_no_distribution(tmp_path):
    skill_dir = _make_skill(tmp_path)
    _write_script(
        skill_dir,
        source=(
            "import ast\nimport sys\nimport tomllib\n"
            "from pathlib import Path\nfrom sibling import example\n"
        ),
    )
    (skill_dir / "scripts" / "sibling.py").write_text(
        "def example():\n    return None\n", encoding="utf-8"
    )
    assert frontmatter.check_script_headers(
        skill_dir, vendored=frozenset()
    ) == []


@pytest.mark.parametrize(
    "handler",
    [
        "ImportError",
        "ModuleNotFoundError",
        "(ImportError, RuntimeError)",
        "(RuntimeError, ModuleNotFoundError)",
    ],
)
# spec: "Imports inside a `try` whose handler catches `ImportError` or `ModuleNotFoundError` are optional and may be left undeclared."
# task: 10
def test_optional_import_handlers_exempt_the_try_body(tmp_path, handler):
    skill_dir = _make_skill(tmp_path)
    _write_script(
        skill_dir,
        source=f"try:\n    import polars\nexcept {handler}:\n    pass\n",
    )
    assert frontmatter.check_script_headers(
        skill_dir, vendored=frozenset()
    ) == []


# spec: "Imports inside a `try` whose handler catches `ImportError` or `ModuleNotFoundError` are optional and may be left undeclared."
# task: 10
def test_unrelated_exception_handlers_do_not_exempt_imports(tmp_path):
    skill_dir = _make_skill(tmp_path)
    _write_script(
        skill_dir,
        source="try:\n    import polars\nexcept RuntimeError:\n    pass\n",
    )
    assert frontmatter.check_script_headers(skill_dir, vendored=frozenset())


@pytest.mark.parametrize(
    "source",
    [
        "try:\n    pass\nexcept ImportError:\n    import polars\n",
        "try:\n    pass\nexcept ImportError:\n    pass\nelse:\n    import polars\n",
        "try:\n    pass\nexcept ImportError:\n    pass\nfinally:\n    import polars\n",
    ],
)
# spec: "Imports inside a `try` whose handler catches `ImportError` or `ModuleNotFoundError` are optional and may be left undeclared."
# task: 10
def test_handler_else_and_finally_imports_are_not_exempt(tmp_path, source):
    skill_dir = _make_skill(tmp_path)
    _write_script(skill_dir, source=source)
    assert frontmatter.check_script_headers(skill_dir, vendored=frozenset())


# spec: "In such a script, every non-stdlib, non-local import is declared in `dependencies`:"
# task: 10
def test_repository_script_lint_passes_without_any_script_exemptions():
    for skill_dir in _skill_dirs():
        assert frontmatter.check_script_headers(
            skill_dir, vendored=frozenset()
        ) == [], skill_dir


@pytest.mark.parametrize(
    "path",
    [
        "<this-skill-dir>/scripts/lint_wiki.py",
        "<this-skill-dir>/../llm-wiki/scripts/lint_wiki.py",
        "$LLM_WIKI_ROOT/scripts/lint_wiki.py",
        "~/Projects/agent-skills/skills/llm-wiki/scripts/lint_wiki.py",
        "skills/llm-wiki/scripts/lint_wiki.py",
    ],
)
@pytest.mark.parametrize("runner", ["python", "python3"])
# spec: "No skill markdown invokes a resolving bundled-script path with bare `python` or `python3`, including line-continued forms (`python \` followed by the path on the next line)."
# task: 11
def test_bare_python_is_rejected_for_each_documented_path_form(
    tmp_path, path, runner
):
    skill_dir, script = _invocation_fixture(tmp_path)
    resolved = frontmatter.resolve_bundled_script(path, skill_dir)
    assert resolved is not None
    assert resolved.resolve() == script.resolve()
    _write_skill(
        skill_dir,
        _read_frontmatter(skill_dir),
        body=f"```sh\n{runner} {path}\n```\n",
    )
    assert frontmatter.check_invocations(skill_dir)


@pytest.mark.parametrize("runner", ["python", "python3"])
# spec: "No skill markdown invokes a resolving bundled-script path with bare `python` or `python3`, including line-continued forms (`python \` followed by the path on the next line)."
# task: 11
def test_line_continued_python_invocations_are_rejected(tmp_path, runner):
    skill_dir, _ = _invocation_fixture(tmp_path)
    _write_skill(
        skill_dir,
        _read_frontmatter(skill_dir),
        body=(
            f"```sh\n{runner} \\\n"
            "  <this-skill-dir>/scripts/lint_wiki.py\n```\n"
        ),
    )
    assert frontmatter.check_invocations(skill_dir)


# spec: "A path that does not resolve to a bundled script, such as `writing-skills/anthropic-best-practices.md`'s teaching example `scripts/migrate.py`, is not flagged."
# task: 11
def test_unresolved_teaching_example_is_ignored(tmp_path):
    skill_dir = _make_skill(
        tmp_path, body="```sh\npython scripts/migrate.py\n```\n"
    )
    assert frontmatter.resolve_bundled_script(
        "scripts/migrate.py", skill_dir
    ) is None
    assert frontmatter.check_invocations(skill_dir) == []


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
def test_uv_run_invocation_is_discovered_and_accepted(tmp_path):
    skill_dir, script = _invocation_fixture(tmp_path)
    path = "<this-skill-dir>/scripts/lint_wiki.py"
    _write_skill(
        skill_dir,
        _read_frontmatter(skill_dir),
        body=f"```sh\nuv run {path} --help\n```\n",
    )
    invocations = frontmatter.bundled_invocations(skill_dir)
    assert len(invocations) == 1
    markdown, runner, discovered_path = invocations[0]
    assert markdown.resolve() == (skill_dir / "SKILL.md").resolve()
    assert runner == "uv run"
    assert discovered_path == path
    assert frontmatter.resolve_bundled_script(
        discovered_path, skill_dir
    ).resolve() == script.resolve()
    assert frontmatter.check_invocations(skill_dir) == []


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
def test_repository_invocations_use_the_exact_uv_run_form():
    path_pattern = (
        r"(?:<this-skill-dir>/|\$LLM_WIKI_ROOT/|"
        r"~/Projects/agent-skills/|skills/|scripts/)"
        r"[A-Za-z0-9_./-]+\.py"
    )
    commands = re.compile(
        r"\b(?:python3?|uv[ \t]+run)\b[^\n`]*?"
        rf"(?P<path>{path_pattern})"
    )
    for skill_dir in _skill_dirs():
        assert frontmatter.check_invocations(skill_dir) == [], skill_dir
        for markdown in skill_dir.rglob("*.md"):
            text = re.sub(
                r"\\\r?\n[ \t]*",
                " ",
                markdown.read_text(encoding="utf-8"),
            )
            for match in commands.finditer(text):
                path = match.group("path")
                resolved = frontmatter.resolve_bundled_script(path, skill_dir)
                if resolved is None:
                    continue
                assert re.fullmatch(
                    r"uv[ \t]+run[ \t]+" + re.escape(path),
                    match.group(0),
                ), (markdown, match.group(0))


# spec: "Each skill with such an invocation gets this sentence once, near its first invocation: "Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.""
# task: 11
def test_each_invoking_skill_has_exactly_one_fallback_sentence():
    for skill_dir in _skill_dirs():
        if not frontmatter.bundled_invocations(skill_dir):
            continue
        text = "\n".join(
            markdown.read_text(encoding="utf-8")
            for markdown in sorted(skill_dir.rglob("*.md"))
        )
        assert text.count(FALLBACK) == 1, skill_dir


@pytest.mark.parametrize(
    ("value", "valid"),
    [
        (MISSING, False),
        ("Requires Python.", False),
        ("Requires uv.", True),
    ],
)
# spec: "A skill whose markdown runs a bundled script via `uv run` declares a `compatibility` value containing `uv`."
# task: 12
def test_uv_invocation_requires_compatibility_mentioning_uv(
    tmp_path, value, valid
):
    skill_dir, _ = _invocation_fixture(tmp_path)
    data = _read_frontmatter(skill_dir)
    if value is not MISSING:
        data["compatibility"] = value
    _write_skill(
        skill_dir,
        data,
        body="uv run <this-skill-dir>/scripts/lint_wiki.py\n",
    )
    errors = frontmatter._check_compatibility_names_uv(skill_dir, data)
    assert bool(errors) is not valid


# spec: "A skill whose markdown runs a bundled script via `uv run` declares a `compatibility` value containing `uv`."
# task: 12
def test_noninvoking_skill_does_not_require_uv_compatibility(tmp_path):
    skill_dir = _make_skill(tmp_path)
    assert frontmatter._check_compatibility_names_uv(
        skill_dir, _read_frontmatter(skill_dir)
    ) == []


# spec: "Here 3.X is the highest `requires-python` floor among the scripts that skill invokes."
# task: 12
def test_repository_compatibility_uses_the_highest_invoked_script_floor():
    for skill_dir in _skill_dirs():
        invocations = frontmatter.bundled_invocations(skill_dir)
        if not invocations:
            continue
        floors = []
        for _, runner, path in invocations:
            assert runner == "uv run", skill_dir
            script = frontmatter.resolve_bundled_script(path, skill_dir)
            assert script is not None, (skill_dir, path)
            metadata = tomllib.loads(
                _metadata_payload(script.read_text(encoding="utf-8"))
            )
            match = re.fullmatch(
                r">=3\.(11|12|13)", metadata["requires-python"]
            )
            assert match is not None, script
            floors.append(int(match.group(1)))
        expected = (
            "Requires uv to run bundled scripts "
            "(dependencies are declared inline); "
            f"Python 3.{max(floors)}+."
        )
        assert _read_frontmatter(skill_dir)["compatibility"] == expected


# spec: "That set includes `finishing-a-development-branch`, which runs `writing-plans`' `deferred_stats.py`."
# task: 12
def test_finishing_branch_retains_the_cross_skill_script_invocation():
    skill_dir = ROOT / "skills" / "finishing-a-development-branch"
    target = (
        ROOT / "skills" / "writing-plans" / "scripts" / "deferred_stats.py"
    ).resolve()
    resolved = {
        frontmatter.resolve_bundled_script(path, skill_dir).resolve()
        for _, runner, path in frontmatter.bundled_invocations(skill_dir)
        if runner == "uv run"
    }
    assert target in resolved
    assert "uv" in _read_frontmatter(skill_dir)["compatibility"]


# spec: "**Provenance lint (`build/check_provenance.py`)**, driven by one `BUNDLED_LICENSES` table (root file → skills; `LICENSE` implied for every skill)."
# task: 8
def test_repository_license_mapping_matches_the_spec():
    skills = _skill_dirs()
    names = {skill.name for skill in skills}
    superpowers = {
        skill.name
        for skill in skills
        if _read_frontmatter(skill).get("metadata", {}).get("source")
        == SUPERPOWERS_SOURCE
    }
    assert len(superpowers) == 13
    table = {
        filename: set(mapped_skills)
        for filename, mapped_skills in provenance.BUNDLED_LICENSES.items()
    }
    assert provenance.PLAIN_LICENSE == "LICENSE"
    if "LICENSE" in table:
        assert table.pop("LICENSE") == names
    expected = {
        "LICENSE-superpowers": superpowers,
        "LICENSE-coding-skills": {"bayesian-workflow", "clean-code"},
    }
    if (ROOT / "LICENSE-andorra").exists():
        expected["LICENSE-andorra"] = {"bayesian-workflow"}
    assert table == expected


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_provenance_accepts_correct_regular_copies(tmp_path):
    skills, table = _license_fixture(tmp_path)
    assert provenance.bundled_license_violations(
        tmp_path, skills, table
    ) == []


@pytest.mark.parametrize("filename", ["LICENSE", "LICENSE-coding-skills"])
# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_provenance_rejects_missing_required_copies(tmp_path, filename):
    skills, table = _license_fixture(tmp_path)
    (tmp_path / "skills" / "bayesian-workflow" / filename).unlink()
    assert provenance.bundled_license_violations(tmp_path, skills, table)


@pytest.mark.parametrize("filename", ["LICENSE", "LICENSE-coding-skills"])
# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_provenance_rejects_symlinks_even_to_identical_root_files(
    tmp_path, filename
):
    skills, table = _license_fixture(tmp_path)
    bundled = tmp_path / "skills" / "bayesian-workflow" / filename
    bundled.unlink()
    bundled.symlink_to(tmp_path / filename)
    assert provenance.bundled_license_violations(tmp_path, skills, table)


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_provenance_rejects_a_directory_in_place_of_a_license(tmp_path):
    skills, table = _license_fixture(tmp_path)
    bundled = tmp_path / "skills" / "bayesian-workflow" / "LICENSE"
    bundled.unlink()
    bundled.mkdir()
    assert provenance.bundled_license_violations(tmp_path, skills, table)


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_provenance_rejects_even_a_trailing_newline_difference(tmp_path):
    skills, table = _license_fixture(tmp_path)
    bundled = tmp_path / "skills" / "bayesian-workflow" / "LICENSE"
    bundled.write_bytes((tmp_path / "LICENSE").read_bytes().rstrip(b"\n"))
    assert provenance.bundled_license_violations(tmp_path, skills, table)


# spec: "No skill directory holds a `LICENSE*` file outside its mapping."
# task: 8
def test_provenance_rejects_an_unmapped_bundled_license(tmp_path):
    skills, table = _license_fixture(tmp_path)
    (tmp_path / "skills" / "clean-code" / "LICENSE-andorra").write_bytes(
        b"unmapped fixture\n"
    )
    assert provenance.bundled_license_violations(tmp_path, skills, table)


# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
def test_provenance_rejects_an_unmapped_root_license(tmp_path):
    skills, table = _license_fixture(tmp_path)
    (tmp_path / "LICENSE-superpowers").write_bytes(b"unmapped fixture\n")
    assert provenance.bundled_license_violations(tmp_path, skills, table)


# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
def test_provenance_rejects_an_empty_root_license_mapping(tmp_path):
    skills, table = _license_fixture(tmp_path)
    (tmp_path / "LICENSE-superpowers").write_bytes(b"unmapped fixture\n")
    table["LICENSE-superpowers"] = ()
    assert provenance.bundled_license_violations(tmp_path, skills, table)


# spec: "Each skill directory carries regular files (never symlinks, which `install.py --copy` refuses) that are byte-identical to the root license files and carry the same names:"
# task: 8
def test_repository_license_copies_are_exact_and_have_no_extra_names():
    skills = _skill_dirs()
    table = provenance.BUNDLED_LICENSES
    assert provenance.bundled_license_violations(
        ROOT, [skill.name for skill in skills], table
    ) == []
    for skill_dir in skills:
        expected = {"LICENSE"} | {
            filename
            for filename, mapped_skills in table.items()
            if skill_dir.name in mapped_skills
        }
        actual = {path.name for path in skill_dir.glob("LICENSE*")}
        assert actual == expected, skill_dir
        for filename in expected:
            bundled = skill_dir / filename
            assert bundled.is_file(), bundled
            assert not bundled.is_symlink(), bundled
            assert bundled.read_bytes() == (ROOT / filename).read_bytes()


# spec: "The script stays stdlib-only, so its CLAUDE.md command keeps no `--with`."
# task: 8
def test_provenance_imports_only_the_standard_library():
    tree = ast.parse(
        Path(provenance.__file__).read_text(encoding="utf-8")
    )
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            if node.module:
                imports.add(node.module.split(".")[0])
    assert imports <= set(sys.stdlib_module_names) | {"__future__"}


# spec: "The script stays stdlib-only, so its CLAUDE.md command keeps no `--with`."
# task: 8
def test_documented_provenance_command_needs_no_with_dependencies():
    commands = _section(
        (ROOT / "CLAUDE.md").read_text(encoding="utf-8"), "Commands"
    )
    commands = re.sub(r"\\\r?\n[ \t]*", " ", commands)
    invocations = [
        line
        for line in commands.splitlines()
        if "check_provenance.py" in line
        and re.search(r"\b(?:uv[ \t]+run|python3?)\b", line)
    ]
    assert invocations
    assert all("--with" not in line for line in invocations)
</tests>
<flags>
<flag task="3"><spec>R2.2's red-baseline file exists, and `writing-skills` changed only as R2.3's outcome branch allows.</spec><plan>Modify: `skills/llm-wiki/SKILL.md` (its description), `skills/writing-skills/SKILL.md` (the optional-keys bullet), `build/cc_guide/conformance.toml` (two comments)</plan></flag>
<flag task="4"><spec>R2.2's red-baseline file exists, and `writing-skills` changed only as R2.3's outcome branch allows.</spec><plan>Modify: the 13 superpowers `SKILL.md` files (helper script), `skills/writing-skills/SKILL.md` (required fields, optional keys, template, checklist), `NOTICE` (one entry)</plan></flag>
<flag task="7"><spec>The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").</spec><plan>Modify: `CLAUDE.md` (Commands: the frontmatter lint's comment names `--strict`; no line added, D7)</plan></flag>
<flag task="8"><spec>No skill directory holds a `LICENSE*` file outside its mapping.</spec><plan>Rename: `skills/recommend-causal-design/LICENSE` to `skills/recommend-causal-design/LICENSE-causal-design-sources`, and re-point its links in that skill's `SKILL.md`, `README.md` and `references/sources.md`</plan></flag>
<flag task="9"><spec>| `LICENSE-andorra` | `bayesian-workflow` | only if R4.5 finds an upstream notice |</spec><plan>Create: `LICENSE-andorra` (upstream's text, verbatim) and its copy `skills/bayesian-workflow/LICENSE-andorra`</plan></flag>
<flag task="10"><spec>There are 16. Fourteen gain a header:</spec><plan>Modify: the 15 header-less runnable scripts (helper script): a shebang where missing, then the header</plan></flag>
</flags>
<untestable>
The owner approved the design on 2026-10-03 and the written spec on 2026-10-18.
Next step: an implementation plan from the writing-plans skill.
The owner approved all five design sections in a brainstorming pass over `specs/completed/agent-skills-best-practices.md` (a September 2026 survey of Agent Skills portability across Claude Code, Codex, Gemini CLI, Cursor, Copilot, and others).
This document is the handoff for implementation planning.
One piece has landed since: a 2026-10-15 quick fix made `build/check_frontmatter.py` accept `compatibility`, and R1.3's check of its value is still to do.
The survey is this spec's input; it was retired ahead of the spec, to `specs/completed/` in `79ad04f` (2026-10-03).
Most of the survey is already true here and needs no work: `name` matches its directory and descriptions are within 1,024 characters (`build/check_frontmatter.py`); `install.py` links `skills/` into `~/.claude/skills` and the cross-runtime `~/.agents/skills`, with a `--copy` fallback; skill bodies name no runtime tool (`TodoWrite`, Skill/Task/Agent tool) and use no `$ARGUMENTS` or `` !`cmd` `` injection, and bundled paths use `<this-skill-dir>`; side-effect gates live in skill bodies; every command is `disable-model-invocation: true`.
Moving it to `.agents/skills/` has a large blast radius (installer, tests, CLAUDE.md, symlinks) and buys nothing: the installer already links into every runtime's discovery path, which is the survey's own alternative.
The skills already load user-level from the same checkout; a project-level link would list each one twice.
`disable-model-invocation: true` removes a skill from the model's reach, which would break bare-name handoffs (`finishing-a-development-branch`, `using-git-worktrees`, and the others are invoked by name from other skills).
Their side effects are already gated in their bodies, the survey's portable pattern.
`writing-skills`, the governing meta-skill, requires trigger-only descriptions on tested evidence that a workflow summary in the description lets agents skip the body.
"Use when" already front-loads the trigger.
**No description rewrites in this spec.**
R2.1's review found none needed, and no trigger evals exist to catch a regression.
Both measured non-Claude runtimes load skills with host keys; strictness matters only for claude.ai uploads and `skills-ref`-style validators (R1.8).
The survey's 1,536-character truncation, Codex's 2% / 8,000-character budget, and Claude Code's listing fraction stay out of the lint; it keeps the spec's 1,024 cap.
Claude Code listing behavior is documented in `specs/guides/claude-code-customization-guide.md`.
A plain `#!/usr/bin/env python3` shebang keeps the script runnable by bare `python3` where uv is absent; `uv run <path>` reads the header either way.
No single work venv pairs NumPyro with ArviZ, so the project interpreter can lack the imports these scripts need, and work repos that install `hooks/uv-guard.sh` deny bare `python …` anyway.
Today only `writing-skills` warns; splitting it is deferred.
Agents and commands are not Agent Skills and are unaffected.
The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").
Criterion: within its first 150 characters, a description names the skill's primary trigger, the task or symptom it exists for, so an agent shown only that prefix would load it for its canonical use.
All 32 descriptions pass as of 2026-10-03.
The closest calls are `creative-thinking` (its quoted examples carry the "fuzzy target" trigger) and the `clean-code` / `clean-coder` pair, whose openings both lead with editing Python.
Both pass, so neither is rewritten.
Before any edit to `writing-skills`, run a baseline:
5 reps, each a fresh agent given the current `writing-skills` description guidance (the control: no new wording).
Each is asked to write a SKILL.md description for a synthetic skill that is not from this repo and has at least 8 trigger conditions, one of them designated in the scenario as primary.
Run from a session whose cwd was never this repo.
A rep passes if the designated primary trigger lies within the first 150 characters.
The controller reads each output and records the verbatim 150-character prefix.
Record the scenario, prompts, outputs, and verdicts in `specs/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house red-baseline format.
**Baseline ≥ 4/5:** add only a factual note of 2–4 lines to `writing-skills`' "Token Efficiency" section.
No new rule.
**Baseline ≤ 3/5:** also add one checklist line ("the primary trigger falls within the first ~150 characters") and GREEN-test it: 5 reps with the new wording, at least 4/5 passing, recorded in the same red-baseline file.
Use the lowest of `'>=3.11'`, `'>=3.12'`, `'>=3.13'` under which the test suite covering the script passes, run with `uv run --python 3.X` and that suite's CLAUDE.md dependencies.
Scripts covered by one suite share its floor, unless a failure is attributable to one script, which then alone takes the higher floor.
Prose floors that disagree with the header are aligned or removed (e.g. "Python ≥ 3.9" in `recommend-probabilistic-model` and `recommend-visualization`).
The header and the skill's `compatibility` field become the statement of record.
Every third-party import, including function-level imports, is declared with a `>=` floor at the major version the suite currently resolves (e.g. `'polars>=1.0'`).
Runtime backends that the script never imports but needs to read its inputs (e.g. `h5netcdf` for NetCDF) are added when R3.8's fixture run shows them needed.
Each skill with such an invocation gets this sentence once, near its first invocation: "Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header."
Each rule gets a RED test first.
From an empty scratch directory (a subdirectory such as `/tmp/bwprobe/`, never `/tmp` itself), each of the 16 scripts runs `uv run <absolute-path>` on a minimal real input that exercises its main code path.
`--help` alone is enough only for a script with no input-reading path.
The three ArviZ-reading scripts (`diagnose_model.py`, `calibration_check.py`, `compare_experiments.py`) each read a small saved InferenceData fixture.
One script is also run from inside a directory holding an unrelated `pyproject.toml`.
This proves the header isolates it from the project environment.
The dependency-drift check still passes.
Invocation text changes, but no cross-skill reference is added or dropped; finishing → `writing-plans`' `deferred_stats.py` is an existing `DEPENDENCIES` edge.
NOTICE gains one paragraph near the top: each skill directory carries copies of the license texts that apply to it, so a single-skill install (`install.py --copy --skill`, or a third-party installer) keeps the notice MIT requires.
The root files are canonical, and `check_provenance.py` enforces the copies.
README's License section gains one sentence to the same effect.
CLAUDE.md's provenance section gains the invariant and names the enforcing lint, under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").
Locate Alexandre Andorra's original PyMC Bayesian-workflow skill and read its license.
**A notice exists.**
Add the upstream license text verbatim as root `LICENSE-andorra`, map it to `bayesian-workflow`, and extend NOTICE's `bayesian-workflow/` block with the source URL and the quoted copyright line.
**Upstream declares MIT but ships no notice.**
NOTICE records that, in the form already used for the Fonnesbeck repository.
Nothing is bundled.
**Upstream cannot be located.**
NOTICE is unchanged and a deferred item is logged with what was searched.
Never compose a copyright line that is not quoted from the source.
The 2026-08-26 intake review (`specs/completed/skill-intake-review-2026-08-26.md`) already found that Andorra appears nowhere in the history of pymc-labs/python-analytics-skills (only Fonnesbeck and Dean commit there), so start the search from his own publications rather than that repository.
Stages, in order.
D is independent of C and may run alongside it.
Lands together with the 13 superpowers frontmatter additions and the llm-wiki fix, so the new hard rules are green on arrival.
No ceiling remains to raise: a change whose lines would breach the limit trims CLAUDE.md elsewhere (R6 P1, whose ceiling option drift spec R12.7 removed).
When Stage A or Stage D fixes a gap the register tracks to it, the same change removes or narrows that `[[exception]]` and runs `build/check_conformance.py` (R6 P2).
**Work in a worktree.**
The plan edits skills the executing session loads (`writing-plans`, `finishing-a-development-branch`, `writing-skills`), and `~/.claude/skills` resolves to the main checkout.
Commit from the worktree; the shared checkout's branch can change under a concurrent session.
**Stage D's micro-test** runs from a session whose cwd was never this repo; inherited session context voids reps otherwise.
**State test changes as +N deltas** against the suite, never absolute totals.
**Before allocating the plan id**, check `specs/plans/` on every branch (`git ls-tree`); ids are allocated per branch and have collided.
**Coordinate with the in-flight JAX spec.**
`specs/jax-deep-learning-skills.md` is being implemented on `codex/jax-deep-learning-skills` and defines three skills (`skills/deep-learning` is on that branch as of 2026-10-03).
Whichever branch merges second brings the other's skills into conformance in the same merge, or the new lints fail on arrival.
Every gate in CLAUDE.md's Commands passes:
Each new lint rule has a test that failed before its implementation and passes after.
R3.8's execution proof is recorded for all 16 scripts.
`gemini skills list --all` shows every skill under `skills/` as `[Enabled]`;
`codex debug prompt-input` lists every skill under `skills/` by name.
This shows the new `compatibility`, `license`, and `metadata` values and the bundled license files break loading in neither runtime.
R2.2's red-baseline file exists, and `writing-skills` changed only as R2.3's outcome branch allows.
They are expensive and need isolated sessions.
They are also the prerequisite for any future description rewrite.
These are outward-facing.
Plugin namespacing (`/plugin:skill`) also conflicts with the bare-name cross-reference invariant.
R1.6 is the groundwork.
This needs a reliable detector first; a crude grep was not one.
The repo has no CI.
`agents/code-reviewer.md` and `agents/task-reviewer.md` are distilled from superpowers and install as single files without `LICENSE-superpowers`: the same gap R4 closes for skills.
Its Claude Code numbers are secondary; `specs/guides/claude-code-customization-guide.md` governs Claude Code facts.
Its 2026-10-03 re-verification against official docs (at 2.1.288) landed on main via lowmason/agent-skills#19 (merge `c33bc99`).
uv documentation: a script with inline metadata runs in its own environment even inside a project.
R3.8's pyproject run verifies this rather than assuming it.
Runtime measurements in "Measured baseline" were taken on 2026-10-03 with Gemini CLI 0.46.0 and Codex CLI 0.154.0, on this machine's installed skill set (93 skills in Codex's listing).
</untestable>