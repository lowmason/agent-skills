<tests>
import ast
import datetime
import importlib.util
import re
import shlex
import sys
import tomllib
from pathlib import Path

import pytest
import yaml


SPEC_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
HOST_KEYS = {
    "when_to_use",
    "model",
    "effort",
    "context",
    "disable-model-invocation",
}
SCRIPT_INVENTORY = {
    "bayesian-workflow": (
        "calibration_check.py",
        "check_diagnostics.py",
        "diagnose_model.py",
    ),
    "describe-critique-methodology": ("check_decoupling.py",),
    "design-architecture": ("new_adr.py",),
    "explore-data": ("profile.py",),
    "llm-wiki": (
        "bootstrap_wiki.py",
        "distill_sessions.py",
        "distill_specs.py",
        "lint_wiki.py",
    ),
    "recommend-probabilistic-model": ("characterize.py",),
    "recommend-visualization": ("recommend.py",),
    "track-model-experiments": ("compare_experiments.py",),
    "writing-plans": ("deferred_stats.py",),
    "classification-codes": ("build.py",),
    "geographic-codes": ("build.py",),
}
FALLBACK = (
    "Without uv, run the same path with `python3` in an environment "
    "that has the dependencies listed in the script's header."
)


@pytest.fixture
def repo(pytestconfig):
    return Path(pytestconfig.rootpath)


def _load_module(repo, relative_path, monkeypatch):
    path = repo / relative_path
    monkeypatch.syspath_prepend(str(path.parent))
    name = "_acceptance_" + path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def frontmatter(repo, monkeypatch):
    return _load_module(repo, "build/check_frontmatter.py", monkeypatch)


@pytest.fixture
def provenance(repo, monkeypatch):
    return _load_module(repo, "build/check_provenance.py", monkeypatch)


def _make_skill(root, name="example-skill", *, fields=None, body=""):
    skill = root / "skills" / name
    skill.mkdir(parents=True, exist_ok=True)
    data = {
        "name": name,
        "description": "Use when checking bundled scripts.",
        "license": "MIT",
    }
    if fields:
        data.update(fields)
    text = "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body
    (skill / "SKILL.md").write_text(text, encoding="utf-8")
    return skill


def _write_script(skill, filename="probe.py", *, imports="", dependencies=()):
    path = skill / "scripts" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    dependencies_text = ", ".join(repr(item) for item in dependencies)
    path.write_text(
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        "# requires-python = '>=3.11'\n"
        f"# dependencies = [{dependencies_text}]\n"
        "# ///\n"
        f"{imports}\n"
        "if __name__ == '__main__':\n"
        "    pass\n",
        encoding="utf-8",
    )
    return path


def _read_frontmatter(skill):
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    assert match, f"Missing frontmatter: {skill}"
    return yaml.safe_load(match.group(1))


def _skills(repo):
    return sorted(
        path for path in (repo / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def _inline_metadata(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    start = lines.index("# /// script")
    end = lines.index("# ///", start + 1)
    block = lines[start + 1:end]
    assert all(line.startswith("#") for line in block)
    payload = "\n".join(
        line[2:] if line.startswith("# ") else line[1:]
        for line in block
    )
    return tomllib.loads(payload), payload


def _set_policy(skill, value):
    adapter = skill / "agents" / "openai.yaml"
    adapter.parent.mkdir(parents=True, exist_ok=True)
    adapter.write_text(
        yaml.safe_dump({"policy": {"allow_implicit_invocation": value}}),
        encoding="utf-8",
    )
    return adapter


def _values(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _values(item)
    else:
        yield value


def _section(text, title):
    match = re.search(
        rf"(?im)^(#{{1,6}})\s+{re.escape(title)}\s*$", text
    )
    assert match, f"Missing section: {title}"
    rest = text[match.end():]
    following = re.search(
        rf"(?m)^#{{1,{len(match.group(1))}}}\s+", rest
    )
    return rest[:following.start()] if following else rest


def _command_tokens(text):
    text = re.sub(r"\\\r?\n", " ", text)
    candidates = text.splitlines() + re.findall(r"`([^`\n]+)`", text)
    commands = []
    for candidate in candidates:
        try:
            commands.append(shlex.split(candidate.strip(), comments=True))
        except ValueError:
            continue
    return commands


@pytest.fixture
def license_repo(tmp_path):
    names = ["bayesian-workflow", "clean-code", "tech-debt"]
    table = {
        "LICENSE-coding-skills": ("bayesian-workflow", "clean-code"),
    }
    root_texts = {
        "LICENSE": b"Canonical original-work license\n",
        "LICENSE-coding-skills": b"Canonical upstream license\n",
    }
    for filename, content in root_texts.items():
        (tmp_path / filename).write_bytes(content)
    for name in names:
        skill = _make_skill(tmp_path, name)
        (skill / "LICENSE").write_bytes(root_texts["LICENSE"])
        if name in table["LICENSE-coding-skills"]:
            (skill / "LICENSE-coding-skills").write_bytes(
                root_texts["LICENSE-coding-skills"]
            )
    return tmp_path, names, table


# spec: "Replace `ALLOWED_KEYS` with two named sets and allow their union in a `SKILL.md`:"
# task: 3
def test_frontmatter_key_sets(frontmatter):
    assert frontmatter.SPEC_KEYS == frozenset(SPEC_KEYS)
    assert frontmatter.HOST_KEYS == frozenset(HOST_KEYS)
    assert frontmatter.SPEC_KEYS.isdisjoint(frontmatter.HOST_KEYS)


# spec: "When present, a mapping whose keys and values are all strings."
# task: 3
@pytest.mark.parametrize(
    "value, valid",
    [
        ({}, True),
        ({"author": "Jesse Vincent", "adapted_by": "Lowell Mason"}, True),
        ([], False),
        ("author", False),
        (None, False),
        ({1: "author"}, False),
        ({"author": 1}, False),
        ({"author": False}, False),
        ({"author": None}, False),
        ({"author": {"name": "Jesse Vincent"}}, False),
    ],
)
def test_metadata_shape(frontmatter, tmp_path, value, valid):
    skill = _make_skill(tmp_path)
    errors = frontmatter._check_value_shapes(
        skill / "SKILL.md", {"metadata": value}
    )
    assert bool(errors) is not valid


# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
@pytest.mark.parametrize(
    "value, valid",
    [
        ("x", True),
        ("x" * 500, True),
        (" \t" + "x" * 500 + "\n", True),
        ("", False),
        (" \t\n", False),
        ("x" * 501, False),
        (None, False),
        (500, False),
        (True, False),
        ([], False),
        ({}, False),
    ],
)
def test_compatibility_shape(frontmatter, tmp_path, value, valid):
    skill = _make_skill(tmp_path)
    assert frontmatter.COMPATIBILITY_CAP == 500
    errors = frontmatter._check_value_shapes(
        skill / "SKILL.md", {"compatibility": value}
    )
    assert bool(errors) is not valid


# spec: "`name` and `description` contain no `<` or `>`."
# task: 3
@pytest.mark.parametrize("field", ["name", "description"])
@pytest.mark.parametrize("bracket", ["<", ">"])
def test_angle_brackets_rejected(frontmatter, tmp_path, field, bracket):
    skill = _make_skill(tmp_path)
    assert frontmatter._check_value_shapes(
        skill / "SKILL.md", {field: f"before{bracket}after"}
    )


# spec: "Fix llm-wiki's trigger phrase `'verify <page>'` to `'verify a page'`."
# task: 3
def test_llm_wiki_trigger_phrase(repo):
    description = _read_frontmatter(repo / "skills" / "llm-wiki")["description"]
    assert "verify a page" in description
    assert "verify <page>" not in description
    assert "<" not in description and ">" not in description


# spec: "Required in every `SKILL.md`, a non-empty string (repo policy, beyond the spec)."
# task: 4
@pytest.mark.parametrize("value", [None, "", False, 1, [], {}])
def test_invalid_license_rejected(frontmatter, tmp_path, value):
    skill = _make_skill(tmp_path)
    assert frontmatter._check_license(
        skill / "SKILL.md", {"license": value}
    )


# spec: "Required in every `SKILL.md`, a non-empty string (repo policy, beyond the spec)."
# task: 4
def test_license_required_and_valid_license_accepted(frontmatter, tmp_path):
    skill = _make_skill(tmp_path)
    assert frontmatter._check_license(skill / "SKILL.md", {})
    assert not frontmatter._check_license(
        skill / "SKILL.md", {"license": "MIT"}
    )


# spec: "The 13 superpowers skills gain `license: MIT` and ```yaml metadata: author: 'Jesse Vincent' adapted_by: 'Lowell Mason' source: 'https://github.com/obra/superpowers' ``` mirroring `bayesian-workflow`'s existing `author` / `adapted_by` pattern."
# task: 4
def test_superpowers_frontmatter(repo):
    adapted = [
        _read_frontmatter(skill)
        for skill in _skills(repo)
        if _read_frontmatter(skill).get("metadata", {}).get("source")
        == "https://github.com/obra/superpowers"
    ]
    assert len(adapted) == 13
    for data in adapted:
        assert data["license"] == "MIT"
        assert data["metadata"]["author"] == "Jesse Vincent"
        assert data["metadata"]["adapted_by"] == "Lowell Mason"


# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
@pytest.mark.parametrize("value", ["true", "false", 0, 1, None, [], {}])
def test_invocation_flag_requires_boolean(frontmatter, tmp_path, value):
    skill = _make_skill(tmp_path)
    _set_policy(skill, False)
    assert frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": value}
    )


# spec: "A skill with `disable-model-invocation: true` must ship `agents/openai.yaml` that parses and sets `policy.allow_implicit_invocation: false`."
# task: 5
def test_manual_only_requires_adapter(frontmatter, tmp_path):
    skill = _make_skill(tmp_path)
    data = {"disable-model-invocation": True}
    assert frontmatter.CODEX_POLICY == Path("agents") / "openai.yaml"
    assert frontmatter._check_invocation_parity(skill, data)
    _set_policy(skill, False)
    assert not frontmatter._check_invocation_parity(skill, data)


# spec: "A skill with `disable-model-invocation: true` must ship `agents/openai.yaml` that parses and sets `policy.allow_implicit_invocation: false`."
# task: 5
@pytest.mark.parametrize(
    "adapter_text",
    [
        "policy: [",
        "",
        "[]",
        "policy: {}\n",
        "policy:\n  allow_implicit_invocation: true\n",
        "policy:\n  allow_implicit_invocation: 'false'\n",
        "policy:\n  allow_implicit_invocation: 0\n",
    ],
)
def test_manual_only_rejects_invalid_adapter(
    frontmatter, tmp_path, adapter_text
):
    skill = _make_skill(tmp_path)
    adapter = _set_policy(skill, False)
    adapter.write_text(adapter_text, encoding="utf-8")
    assert frontmatter._check_invocation_parity(
        skill, {"disable-model-invocation": True}
    )


# spec: "Conversely, a skill whose `agents/openai.yaml` sets that policy to `false` must set `disable-model-invocation: true`."
# task: 5
@pytest.mark.parametrize(
    "data",
    [{}, {"disable-model-invocation": False}],
)
def test_codex_manual_only_requires_matching_frontmatter(
    frontmatter, tmp_path, data
):
    skill = _make_skill(tmp_path)
    _set_policy(skill, False)
    assert frontmatter._check_invocation_parity(skill, data)


# spec: "Conversely, a skill whose `agents/openai.yaml` sets that policy to `false` must set `disable-model-invocation: true`."
# task: 5
@pytest.mark.parametrize(
    "data",
    [{}, {"disable-model-invocation": False}],
)
def test_implicit_invocation_remains_valid(frontmatter, tmp_path, data):
    skill = _make_skill(tmp_path)
    assert not frontmatter._check_invocation_parity(skill, data)
    _set_policy(skill, True)
    assert not frontmatter._check_invocation_parity(skill, data)


# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
@pytest.mark.parametrize("lines, warns", [(499, False), (500, False), (501, True)])
def test_body_length_boundary(frontmatter, tmp_path, lines, warns):
    skill = _make_skill(tmp_path, body="body line\n" * lines)
    warning = frontmatter.skill_body_warning(skill)
    assert (warning is not None) is warns


# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
def test_frontmatter_lines_do_not_count_toward_body(frontmatter, tmp_path):
    skill = _make_skill(tmp_path, body="body line\n" * 500)
    path = skill / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace("---\n", "---\n" + "# frontmatter comment\n" * 501, 1),
        encoding="utf-8",
    )
    assert frontmatter.skill_body_warning(skill) is None


# spec: "When Stage A adds this warning, it also adds a `skill-body-size` `[[check]]` to `build/cc_guide/conformance.toml` that maps `skills.overview` to it, with `enforced_by = 'check_frontmatter'` (conformance R6 P3)."
# task: 6
def test_body_warning_registered(repo):
    config = tomllib.loads(
        (repo / "build/cc_guide/conformance.toml").read_text(encoding="utf-8")
    )
    checks = [
        check for check in config["check"]
        if "skill-body-size" in set(_values(check))
    ]
    assert len(checks) == 1
    assert checks[0]["enforced_by"] == "check_frontmatter"
    assert "skills.overview" in set(_values(checks[0]))


# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
@pytest.mark.parametrize("key", sorted(HOST_KEYS))
def test_strict_rejects_every_host_key(frontmatter, tmp_path, key):
    values = {
        "when_to_use": "Use when editing Python.",
        "model": "example",
        "effort": "high",
        "context": "fork",
        "disable-model-invocation": False,
    }
    skill = _make_skill(tmp_path, fields={key: values[key]})
    assert frontmatter.strict_violations(skill)


# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
@pytest.mark.parametrize(
    "name",
    ["claude", "anthropic", "before-claude-after", "before-anthropic-after"],
)
def test_strict_rejects_reserved_name_substrings(frontmatter, tmp_path, name):
    skill = _make_skill(tmp_path, fields={"name": name})
    assert frontmatter.strict_violations(skill)


# spec: "It is not part of the default gate."
# task: 7
def test_strict_allows_spec_only_frontmatter(frontmatter, tmp_path):
    skill = _make_skill(
        tmp_path,
        fields={
            "compatibility": "Requires uv.",
            "metadata": {"author": "Lowell Mason"},
            "allowed-tools": "Read",
        },
    )
    assert not frontmatter.strict_violations(skill)


# spec: "Expected result today: exactly `bayesian-workflow`, `tune-hyperparameters`, and `tech-debt` fail."
# task: 7
def test_repository_strict_failures(frontmatter, repo, capsys):
    failing = {
        skill.name for skill in _skills(repo)
        if frontmatter.strict_violations(skill)
    }
    assert failing == {
        "bayesian-workflow", "tune-hyperparameters", "tech-debt"
    }
    assert frontmatter.main(["--strict"]) != 0
    capsys.readouterr()


# spec: "The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, \"Conformance register\")."
# task: 7
def test_strict_command_documented_as_an_invocation(repo, frontmatter):
    text = (repo / "CLAUDE.md").read_text(encoding="utf-8")
    commands = _section(text, "Commands")
    assert any(
        "--strict" in tokens
        and any(token.endswith("build/check_frontmatter.py") for token in tokens)
        for tokens in _command_tokens(commands)
    )
    assert "claude.ai" in commands.lower()
    assert "upload" in commands.lower()
    assert "validator" in commands.lower()
    assert "--strict" in (frontmatter.__doc__ or "")
    assert len(text.splitlines()) <= 200


# spec: "`check_frontmatter.py` (exit 0; the only `WARN` is `writing-skills`' body length)"
# task: 7
def test_repository_default_gate_and_warning(frontmatter, capsys):
    assert frontmatter.main([]) == 0
    captured = capsys.readouterr()
    warnings = [
        line for line in captured.err.splitlines()
        if re.search(r"\bWARN\b", line)
    ]
    assert len(warnings) == 1
    assert "writing-skills" in warnings[0]
    assert not re.search(r"\bWARN\b", captured.out)


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_valid_bundled_licenses(provenance, license_repo):
    root, names, table = license_repo
    assert not provenance.bundled_license_violations(root, names, table)


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
@pytest.mark.parametrize("filename", ["LICENSE", "LICENSE-coding-skills"])
@pytest.mark.parametrize("defect", ["missing", "directory", "symlink", "different"])
def test_bundled_license_defects(
    provenance, license_repo, filename, defect
):
    root, names, table = license_repo
    copy = root / "skills" / "bayesian-workflow" / filename
    copy.unlink()
    if defect == "directory":
        copy.mkdir()
    elif defect == "symlink":
        copy.symlink_to(root / filename)
    elif defect == "different":
        copy.write_bytes((root / filename).read_bytes() + b"\n")
    assert provenance.bundled_license_violations(root, names, table)


# spec: "No skill directory holds a `LICENSE*` file outside its mapping."
# task: 8
@pytest.mark.parametrize(
    "skill, filename",
    [
        ("tech-debt", "LICENSE-coding-skills"),
        ("clean-code", "LICENSE-causal-design-sources"),
    ],
)
def test_unmapped_bundled_license_rejected(
    provenance, license_repo, skill, filename
):
    root, names, table = license_repo
    (root / "skills" / skill / filename).write_text(
        "Unmapped notice\n", encoding="utf-8"
    )
    assert provenance.bundled_license_violations(root, names, table)


# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
@pytest.mark.parametrize("empty_mapping", [False, True])
def test_unassigned_root_license_rejected(
    provenance, license_repo, empty_mapping
):
    root, names, table = license_repo
    (root / "LICENSE-andorra").write_text("Upstream notice\n", encoding="utf-8")
    if empty_mapping:
        table = {**table, "LICENSE-andorra": ()}
    assert provenance.bundled_license_violations(root, names, table)


# spec: "Each skill directory carries regular files (never symlinks, which `install.py --copy` refuses) that are byte-identical to the root license files and carry the same names:"
# task: 8
def test_repository_bundled_license_mapping_and_bytes(repo, provenance):
    skills = _skills(repo)
    names = {skill.name for skill in skills}
    superpowers = {
        skill.name for skill in skills
        if _read_frontmatter(skill).get("metadata", {}).get("source")
        == "https://github.com/obra/superpowers"
    }
    table = provenance.BUNDLED_LICENSES
    expected_keys = {"LICENSE-superpowers", "LICENSE-coding-skills"}
    if (repo / "LICENSE-andorra").exists():
        expected_keys.add("LICENSE-andorra")
    assert provenance.PLAIN_LICENSE == "LICENSE"
    assert set(table) == expected_keys
    assert len(superpowers) == 13
    assert set(table["LICENSE-superpowers"]) == superpowers
    assert set(table["LICENSE-coding-skills"]) == {
        "bayesian-workflow", "clean-code"
    }
    if "LICENSE-andorra" in table:
        assert set(table["LICENSE-andorra"]) == {"bayesian-workflow"}
    for root_name, mapped_skills in table.items():
        assert mapped_skills
        assert set(mapped_skills) <= names
        assert (repo / root_name).is_file()
    assert {p.name for p in repo.glob("LICENSE*")} == {"LICENSE", *table}
    for skill in skills:
        expected = {"LICENSE"} | {
            filename for filename, mapped in table.items()
            if skill.name in mapped
        }
        assert {p.name for p in skill.glob("LICENSE*")} == expected
        for filename in expected:
            copy = skill / filename
            assert copy.is_file() and not copy.is_symlink()
            assert copy.read_bytes() == (repo / filename).read_bytes()
    assert not provenance.bundled_license_violations(
        repo, sorted(names), table
    )


# spec: "The script stays stdlib-only, so its CLAUDE.md command keeps no `--with`."
# task: 8
def test_provenance_stays_stdlib_only(repo):
    source = (repo / "build/check_provenance.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            assert not node.level
            roots = [(node.module or "").split(".")[0]]
        else:
            continue
        assert set(roots) <= sys.stdlib_module_names
    commands = _command_tokens(
        _section((repo / "CLAUDE.md").read_text(encoding="utf-8"), "Commands")
    )
    matching = [
        tokens for tokens in commands
        if any(token.endswith("build/check_provenance.py") for token in tokens)
    ]
    assert matching
    assert all(
        not any(token == "--with" or token.startswith("--with=") for token in tokens)
        for tokens in matching
    )


# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
@pytest.mark.parametrize(
    "guard",
    [
        'if __name__ == "__main__":',
        "if __name__ == '__main__':",
        "if '__main__' == __name__:",
    ],
)
def test_runnable_script_discovery(frontmatter, tmp_path, guard):
    skill = _make_skill(tmp_path)
    runnable = _write_script(skill)
    runnable.write_text(guard + "\n    pass\n", encoding="utf-8")
    (runnable.parent / "library.py").write_text(
        "def run():\n    pass\n", encoding="utf-8"
    )
    (runnable.parent / "example.py").write_text(
        '# if __name__ == "__main__":\n'
        'EXAMPLE = \'if __name__ == "__main__":\'\n',
        encoding="utf-8",
    )
    assert set(frontmatter.runnable_scripts(skill)) == {runnable}


# spec: "There are 16."
# task: 10
def test_repository_runnable_inventory(repo, frontmatter):
    expected = {
        f"skills/{skill}/scripts/{filename}"
        for skill, filenames in SCRIPT_INVENTORY.items()
        for filename in filenames
    }
    actual = {
        path.relative_to(repo).as_posix()
        for skill in _skills(repo)
        for path in frontmatter.runnable_scripts(skill)
    }
    assert len(expected) == 16
    assert actual == expected


# spec: "`tune-hyperparameters/scripts/time_series_cv.py` has no `__main__` guard; it is a library imported into the user's code and stays header-less."
# task: 10
def test_time_series_cv_stays_headerless(repo, frontmatter):
    skill = repo / "skills/tune-hyperparameters"
    path = skill / "scripts/time_series_cv.py"
    assert path not in frontmatter.runnable_scripts(skill)
    assert frontmatter.script_metadata(path.read_text(encoding="utf-8")) is None


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_valid_header_parses(frontmatter, tmp_path):
    skill = _make_skill(tmp_path)
    script = _write_script(skill)
    assert frontmatter.script_metadata(
        script.read_text(encoding="utf-8")
    ) == {"requires-python": ">=3.11", "dependencies": []}
    assert not frontmatter.check_script_headers(skill)


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
@pytest.mark.parametrize(
    "defect",
    ["no-block", "invalid-toml", "missing-python", "missing-dependencies"],
)
def test_invalid_headers_rejected(frontmatter, tmp_path, defect):
    skill = _make_skill(tmp_path)
    script = _write_script(skill)
    text = script.read_text(encoding="utf-8")
    if defect == "no-block":
        text = "#!/usr/bin/env python3\nif __name__ == '__main__':\n    pass\n"
    elif defect == "invalid-toml":
        text = text.replace("# dependencies = []", "# dependencies = [")
    elif defect == "missing-python":
        text = text.replace("# requires-python = '>=3.11'\n", "")
    else:
        text = text.replace("# dependencies = []\n", "")
    script.write_text(text, encoding="utf-8")
    assert frontmatter.check_script_headers(skill)


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_runnable_scripts_have_no_exemption(frontmatter, tmp_path):
    skill = _make_skill(tmp_path, "bayesian-workflow")
    path = _write_script(skill, "diagnose_model.py")
    path.write_text(
        "if __name__ == '__main__':\n    pass\n", encoding="utf-8"
    )
    key = "skills/bayesian-workflow/scripts/diagnose_model.py"
    assert frontmatter.check_script_headers(skill, vendored=frozenset({key}))


# spec: "Line 1 is `#!/usr/bin/env python3`; add it where missing."
# task: 10
def test_repository_house_headers(repo):
    for skill, filenames in SCRIPT_INVENTORY.items():
        for filename in filenames:
            path = repo / "skills" / skill / "scripts" / filename
            text = path.read_text(encoding="utf-8")
            assert text.splitlines()[0] == "#!/usr/bin/env python3", path
            metadata, payload = _inline_metadata(path)
            assert metadata["requires-python"] in {
                ">=3.11", ">=3.12", ">=3.13"
            }, path
            assert isinstance(metadata["dependencies"], list), path
            assert all(isinstance(item, str) for item in metadata["dependencies"])
            assert re.search(
                r"(?m)^requires-python\s*=\s*'>=3\.(?:11|12|13)'\s*$",
                payload,
            ), path
            assert '"' not in payload, path
            for dependency in metadata["dependencies"]:
                assert re.fullmatch(
                    r"[A-Za-z0-9][A-Za-z0-9_.-]*(?:\[[^]]+\])?"
                    r">=\d+(?:\.\d+)*(?:\s*;.*)?",
                    dependency,
                ), (path, dependency)


# spec: "In such a script, every non-stdlib, non-local import is declared in `dependencies`:"
# task: 10
@pytest.mark.parametrize(
    "imports, dependencies, valid",
    [
        ("import pathlib\nimport sys\nimport tomllib", (), True),
        ("import sibling", (), True),
        ("import numpy", (), False),
        ("import numpy", ("numpy>=1.0",), True),
        ("def run():\n    import numpy", (), False),
        ("def run():\n    import numpy", ("numpy>=1.0",), True),
        ("from yaml import safe_load", (), False),
        ("from yaml import safe_load", ("pyyaml>=6.0",), True),
    ],
)
def test_import_dependencies(
    frontmatter, tmp_path, imports, dependencies, valid
):
    skill = _make_skill(tmp_path)
    script = _write_script(skill, imports=imports, dependencies=dependencies)
    (script.parent / "sibling.py").write_text("VALUE = 1\n", encoding="utf-8")
    assert bool(frontmatter.check_script_headers(skill)) is not valid


# spec: "Imports inside a `try` whose handler catches `ImportError` or `ModuleNotFoundError` are optional and may be left undeclared."
# task: 10
@pytest.mark.parametrize(
    "handler, valid",
    [
        ("ImportError", True),
        ("ModuleNotFoundError", True),
        ("(ImportError, ModuleNotFoundError)", True),
        ("ValueError", False),
    ],
)
def test_optional_import_exemption(frontmatter, tmp_path, handler, valid):
    skill = _make_skill(tmp_path)
    _write_script(
        skill,
        imports=f"try:\n    import numpy\nexcept {handler}:\n    pass",
    )
    assert bool(frontmatter.check_script_headers(skill)) is not valid


# spec: "Imports inside a `try` whose handler catches `ImportError` or `ModuleNotFoundError` are optional and may be left undeclared."
# task: 10
def test_optional_import_does_not_exempt_unprotected_import(
    frontmatter, tmp_path
):
    skill = _make_skill(tmp_path)
    _write_script(
        skill,
        imports=(
            "try:\n"
            "    import numpy\n"
            "except ImportError:\n"
            "    pass\n"
            "def run():\n"
            "    import numpy\n"
        ),
    )
    assert frontmatter.check_script_headers(skill)


# spec: "No skill markdown invokes a resolving bundled-script path with bare `python` or `python3`, including line-continued forms (`python \\` followed by the path on the next line)."
# task: 11
@pytest.mark.parametrize(
    "runner",
    [
        "python ",
        "python3 ",
        "python \\\n    ",
        "python3 \\\n    ",
        "uv run --no-project --python 3.13 python ",
        "uv run --python 3.13 --with numpy python ",
    ],
)
@pytest.mark.parametrize("markdown", ["SKILL.md", "README.md", "references/run.md"])
def test_old_invocations_rejected(frontmatter, tmp_path, runner, markdown):
    skill = _make_skill(tmp_path)
    _write_script(skill)
    document = skill / markdown
    document.parent.mkdir(parents=True, exist_ok=True)
    with document.open("a", encoding="utf-8") as stream:
        stream.write(
            "\n```bash\n"
            + runner
            + "<this-skill-dir>/scripts/probe.py\n```\n"
        )
    assert frontmatter.check_invocations(skill)


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
def test_uv_run_invocation_accepted(frontmatter, tmp_path):
    skill = _make_skill(
        tmp_path,
        body="```bash\nuv run <this-skill-dir>/scripts/probe.py --help\n```\n",
    )
    _write_script(skill)
    assert not frontmatter.check_invocations(skill)
    assert (
        skill / "SKILL.md", "uv run", "<this-skill-dir>/scripts/probe.py"
    ) in frontmatter.bundled_invocations(skill)


# spec: "Path forms in use: `<this-skill-dir>/scripts/x.py`, `<this-skill-dir>/../<skill>/scripts/x.py`, `$LLM_WIKI_ROOT/scripts/x.py` (the installed copies), `~/Projects/agent-skills/skills/llm-wiki/scripts/x.py` (llm-wiki's INSTALL.md), and repo-relative `skills/<skill>/scripts/build.py`."
# task: 11
@pytest.mark.parametrize(
    "source_path, target_skill, filename",
    [
        (
            "<this-skill-dir>/scripts/diagnose_model.py",
            "bayesian-workflow",
            "diagnose_model.py",
        ),
        (
            "<this-skill-dir>/../writing-plans/scripts/deferred_stats.py",
            "writing-plans",
            "deferred_stats.py",
        ),
        ("$LLM_WIKI_ROOT/scripts/lint_wiki.py", "llm-wiki", "lint_wiki.py"),
        (
            "~/Projects/agent-skills/skills/llm-wiki/scripts/lint_wiki.py",
            "llm-wiki",
            "lint_wiki.py",
        ),
        (
            "skills/classification-codes/scripts/build.py",
            "classification-codes",
            "build.py",
        ),
    ],
)
def test_documented_path_forms_resolve(
    frontmatter, tmp_path, source_path, target_skill, filename
):
    caller = _make_skill(tmp_path, "bayesian-workflow")
    target = _make_skill(tmp_path, target_skill)
    script = _write_script(target, filename)
    resolved = frontmatter.resolve_bundled_script(source_path, caller)
    assert resolved is not None
    assert resolved.resolve() == script.resolve()


# spec: "A path that does not resolve to a bundled script, such as `writing-skills/anthropic-best-practices.md`'s teaching example `scripts/migrate.py`, is not flagged."
# task: 11
def test_unresolved_teaching_example_is_not_flagged(frontmatter, tmp_path):
    skill = _make_skill(tmp_path, "writing-skills")
    (skill / "anthropic-best-practices.md").write_text(
        "```bash\npython scripts/migrate.py\n```\n", encoding="utf-8"
    )
    assert frontmatter.resolve_bundled_script("scripts/migrate.py", skill) is None
    assert not frontmatter.check_invocations(skill)


# spec: "A skill whose markdown runs a bundled script via `uv run` declares a `compatibility` value containing `uv`."
# task: 12
@pytest.mark.parametrize(
    "compatibility, valid",
    [
        (None, False),
        ("Requires Python 3.11+.", False),
        (
            "Requires uv to run bundled scripts "
            "(dependencies are declared inline); Python 3.11+.",
            True,
        ),
    ],
)
def test_uv_invocation_requires_compatibility(
    frontmatter, tmp_path, compatibility, valid
):
    skill = _make_skill(
        tmp_path,
        body="```bash\nuv run <this-skill-dir>/scripts/probe.py\n```\n",
    )
    _write_script(skill)
    data = {} if compatibility is None else {"compatibility": compatibility}
    assert bool(
        frontmatter._check_compatibility_names_uv(skill, data)
    ) is not valid


# spec: "A skill whose markdown runs a bundled script via `uv run` declares a `compatibility` value containing `uv`."
# task: 12
def test_no_uv_invocation_does_not_require_compatibility(frontmatter, tmp_path):
    skill = _make_skill(tmp_path)
    assert not frontmatter._check_compatibility_names_uv(skill, {})


# spec: "Each skill with such an invocation gets this sentence once, near its first invocation: \"Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.\""
# task: 11
def test_repository_invocations_and_fallback_sentence(repo, frontmatter):
    for skill in _skills(repo):
        invocations = frontmatter.bundled_invocations(skill)
        assert not frontmatter.check_invocations(skill)
        if not invocations:
            continue
        assert all(runner == "uv run" for _, runner, _ in invocations)
        markdown = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(skill.rglob("*.md"))
        )
        assert markdown.count(FALLBACK) == 1, skill


# spec: "Here 3.X is the highest `requires-python` floor among the scripts that skill invokes."
# task: 12
def test_repository_compatibility_matches_highest_invoked_floor(
    repo, frontmatter
):
    invoking = set()
    for skill in _skills(repo):
        invocations = frontmatter.bundled_invocations(skill)
        if not invocations:
            continue
        invoking.add(skill.name)
        floors = []
        for _, runner, script_path in invocations:
            assert runner == "uv run"
            script = frontmatter.resolve_bundled_script(script_path, skill)
            assert script is not None, (skill, script_path)
            metadata, _ = _inline_metadata(script)
            floor = re.fullmatch(r">=(3)\.(11|12|13)", metadata["requires-python"])
            assert floor
            floors.append(tuple(map(int, floor.groups())))
        major, minor = max(floors)
        expected = (
            "Requires uv to run bundled scripts "
            f"(dependencies are declared inline); Python {major}.{minor}+."
        )
        assert _read_frontmatter(skill)["compatibility"] == expected, skill
    assert "finishing-a-development-branch" in invoking
    finishing = repo / "skills/finishing-a-development-branch"
    targets = {
        frontmatter.resolve_bundled_script(path, finishing).resolve()
        for _, _, path in frontmatter.bundled_invocations(finishing)
    }
    assert (
        repo / "skills/writing-plans/scripts/deferred_stats.py"
    ).resolve() in targets


# spec: "Prose floors that disagree with the header are aligned or removed (e.g. \"Python ≥ 3.9\" in `recommend-probabilistic-model` and `recommend-visualization`)."
# task: 12
@pytest.mark.parametrize(
    "skill_name",
    ["recommend-probabilistic-model", "recommend-visualization"],
)
def test_prose_python_floors_agree_with_headers(
    repo, frontmatter, skill_name
):
    skill = repo / "skills" / skill_name
    floors = []
    for _, _, path in frontmatter.bundled_invocations(skill):
        script = frontmatter.resolve_bundled_script(path, skill)
        metadata, _ = _inline_metadata(script)
        floors.append(tuple(map(int, metadata["requires-python"][2:].split("."))))
    assert floors
    expected = ".".join(map(str, max(floors)))
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    stated = re.findall(
        r"Python\s*(?:≥|>=)\s*(3\.\d+)|Python\s+(3\.\d+)\+", text
    )
    assert all((left or right) == expected for left, right in stated)


# spec: "R2.2's red-baseline file exists, and `writing-skills` changed only as R2.3's outcome branch allows."
# task: 2
def test_description_baseline_record_exists(repo):
    records = list(
        (repo / "specs").glob("red-baseline-description-openings-*.md")
    )
    assert records
    for record in records:
        date_text = record.stem.removeprefix(
            "red-baseline-description-openings-"
        )
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text)
        datetime.date.fromisoformat(date_text)
        assert record.is_file()
        assert record.read_text(encoding="utf-8").strip()


# spec: "The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list)."
# task: 14
def test_token_efficiency_note_records_measurement_and_command(repo):
    text = (repo / "skills/writing-skills/SKILL.md").read_text(encoding="utf-8")
    section = _section(text, "Token Efficiency")
    for fact in (
        "Codex", "156", "164", "93", "0.154", "2026-10-03",
        "codex debug prompt-input",
    ):
        assert fact in section
    assert "budget" in section.lower()
    assert re.search(r"shorten|truncat|cut", section, re.I)
    assert re.search(r"outside.*repo", section, re.I | re.S)
    assert re.search(r"skills\s+list", section, re.I)
</tests>
<flags>
<flag task="3"><spec>**Baseline ≥ 4/5:** add only a factual note of 2–4 lines to `writing-skills`' "Token Efficiency" section.</spec><plan>Modify: `skills/llm-wiki/SKILL.md` (its description), `skills/writing-skills/SKILL.md` (the optional-keys bullet), `build/cc_guide/conformance.toml` (two comments)</plan></flag>
<flag task="4"><spec>**Baseline ≤ 3/5:** also add one checklist line ("the primary trigger falls within the first ~150 characters") and GREEN-test it: 5 reps with the new wording, at least 4/5 passing, recorded in the same red-baseline file.</spec><plan>Modify: the 13 superpowers `SKILL.md` files (helper script), `skills/writing-skills/SKILL.md` (required fields, optional keys, template, checklist), `NOTICE` (one entry)</plan></flag>
<flag task="7"><spec>The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").</spec><plan>Modify: `CLAUDE.md` (Commands: the frontmatter lint's comment names `--strict`; no line added, D7)</plan></flag>
<flag task="8"><spec>No skill directory holds a `LICENSE*` file outside its mapping.</spec><plan>Rename: `skills/recommend-causal-design/LICENSE` to `skills/recommend-causal-design/LICENSE-causal-design-sources`, and re-point its links in that skill's `SKILL.md`, `README.md` and `references/sources.md`</plan></flag>
<flag task="9"><spec>| `LICENSE-andorra` | `bayesian-workflow` | only if R4.5 finds an upstream notice |</spec><plan>Create: `LICENSE-andorra` (upstream's text, verbatim) and its copy `skills/bayesian-workflow/LICENSE-andorra`</plan></flag>
<flag task="10"><spec>Fourteen gain a header:</spec><plan>Modify: the 15 header-less runnable scripts (helper script): a shebang where missing, then the header</plan></flag>
</flags>
<untestable>
**Status: APPROVED (2026-10-18).**
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
The survey suggests "Does X. Use when Y".
`writing-skills`, the governing meta-skill, requires trigger-only descriptions on tested evidence that a workflow summary in the description lets agents skip the body.
"Use when" already front-loads the trigger.
**No description rewrites in this spec.**
R2.1's review found none needed, and no trigger evals exist to catch a regression.
The one exception is the angle-bracket fix (R1.5), which is wording-equivalent.
Both measured non-Claude runtimes load skills with host keys; strictness matters only for claude.ai uploads and `skills-ref`-style validators (R1.8).
The survey's 1,536-character truncation, Codex's 2% / 8,000-character budget, and Claude Code's listing fraction stay out of the lint; it keeps the spec's 1,024 cap.
Claude Code listing behavior is documented in `specs/guides/claude-code-customization-guide.md`.
A plain `#!/usr/bin/env python3` shebang keeps the script runnable by bare `python3` where uv is absent; `uv run <path>` reads the header either way.
No single work venv pairs NumPyro with ArviZ, so the project interpreter can lack the imports these scripts need, and work repos that install `hooks/uv-guard.sh` deny bare `python …` anyway.
All current values pass.
No skill trips this today; it exists so that the first manual-only skill cannot auto-fire in Codex.
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
Bash scripts are out of scope.
Use the lowest of `'>=3.11'`, `'>=3.12'`, `'>=3.13'` under which the test suite covering the script passes, run with `uv run --python 3.X` and that suite's CLAUDE.md dependencies.
Scripts covered by one suite share its floor, unless a failure is attributable to one script, which then alone takes the higher floor.
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
RED tests first.
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
R1.4's required `license`, R3's header and invocation rules, and R4's per-skill license copies apply to them too.
Whichever branch merges second brings the other's skills into conformance in the same merge, or the new lints fail on arrival.
Every gate in CLAUDE.md's Commands passes:
Each new lint rule has a test that failed before its implementation and passes after.
R3.8's execution proof is recorded for all 16 scripts.
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
Runtime measurements in "Measured baseline" were taken on 2026-10-03 with Gemini CLI 0.46.0 and Codex CLI 0.154.0, on this machine's installed skill set (93 skills in Codex's listing).
</untestable>