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


REPO = Path(frontmatter.__file__).resolve().parent.parent

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
RUNNABLE_PATHS = {
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
FALLBACK = (
    "Without uv, run the same path with `python3` in an environment "
    "that has the dependencies listed in the script's header."
)


def write_skill(skill_dir, fm=None, body=""):
    skill_dir.mkdir(parents=True, exist_ok=True)
    if fm is None:
        fm = {
            "name": skill_dir.name,
            "description": "Use when editing Python.",
            "license": "MIT",
        }
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        + yaml.safe_dump(fm, sort_keys=False)
        + "---\n"
        + body,
        encoding="utf-8",
    )
    return skill_dir


def make_skill(tmp_path, name="example"):
    return write_skill(tmp_path / "skills" / name)


def read_skill(skill_dir):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(
        r"\A---[ \t]*\r?\n(.*?)^---[ \t]*(?:\r?\n|$)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"Missing frontmatter: {skill_dir}"
    return yaml.safe_load(match.group(1)), text[match.end():]


def skill_dirs():
    return sorted(
        path
        for path in (REPO / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def write_policy(skill_dir, text):
    path = skill_dir / "agents" / "openai.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def script_source(body=None, dependencies=(), floor=">=3.11"):
    if body is None:
        body = "if __name__ == '__main__':\n    pass\n"
    dependency_text = ", ".join(repr(value) for value in dependencies)
    return (
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        f"# requires-python = '{floor}'\n"
        f"# dependencies = [{dependency_text}]\n"
        "# ///\n"
        + body
    )


def write_script(skill_dir, filename="example.py", text=None):
    path = skill_dir / "scripts" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        script_source() if text is None else text,
        encoding="utf-8",
    )
    return path


def write_invocation(skill_dir, command, relative="README.md"):
    path = skill_dir / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"```bash\n{command}\n```\n", encoding="utf-8")
    return path


def metadata_block(text):
    lines = text.splitlines()
    start = lines.index("# /// script")
    end = lines.index("# ///", start + 1)
    block = []
    for line in lines[start + 1:end]:
        assert line.startswith("#"), line
        block.append(line[1:].removeprefix(" "))
    return "\n".join(block)


def scalar_values(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from scalar_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from scalar_values(item)
    else:
        yield value


def markdown_section(text, title):
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match and match.group(2) == title:
            level = len(match.group(1))
            end = len(lines)
            for next_index in range(index + 1, len(lines)):
                heading = re.match(r"^(#{1,6})\s+", lines[next_index])
                if heading and len(heading.group(1)) <= level:
                    end = next_index
                    break
            return "\n".join(lines[index + 1:end])
    pytest.fail(f"Missing section: {title}")


@pytest.fixture
def license_repo(tmp_path):
    skills = ["first", "second"]
    table = {"LICENSE-superpowers": ("first",)}
    contents = {
        "LICENSE": b"Root license\nCopyright Lowell Mason\n",
        "LICENSE-superpowers": b"Upstream license\nCopyright upstream\n",
    }
    for filename, content in contents.items():
        (tmp_path / filename).write_bytes(content)
    for skill in skills:
        directory = tmp_path / "skills" / skill
        directory.mkdir(parents=True)
        (directory / "LICENSE").write_bytes(contents["LICENSE"])
    (tmp_path / "skills/first/LICENSE-superpowers").write_bytes(
        contents["LICENSE-superpowers"]
    )
    return tmp_path, skills, table


# spec: "Replace `ALLOWED_KEYS` with two named sets and allow their union in a `SKILL.md`:"
# task: 3
def test_frontmatter_key_sets():
    assert set(frontmatter.SPEC_KEYS) == SPEC_KEYS
    assert set(frontmatter.HOST_KEYS) == HOST_KEYS
    assert set(frontmatter.SPEC_KEYS | frontmatter.HOST_KEYS) == (
        SPEC_KEYS | HOST_KEYS
    )


# spec: "When present, a mapping whose keys and values are all strings."
# task: 3
@pytest.mark.parametrize(
    "metadata",
    [{}, {"author": "Jesse Vincent"}, {"": ""}],
)
def test_metadata_accepts_string_mappings(tmp_path, metadata):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm["metadata"] = metadata
    assert frontmatter._check_value_shapes(skill / "SKILL.md", fm) == []


# spec: "When present, a mapping whose keys and values are all strings."
# task: 3
@pytest.mark.parametrize(
    "metadata",
    [None, [], "author", 1, True, {1: "author"}, {"author": 1}, {"author": None}],
)
def test_metadata_rejects_other_shapes(tmp_path, metadata):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm["metadata"] = metadata
    assert frontmatter._check_value_shapes(skill / "SKILL.md", fm)


# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
@pytest.mark.parametrize(
    "compatibility",
    ["x", "x" * 500, " \n" + "x" * 500 + "\t ", "é" * 500],
)
def test_compatibility_accepts_stripped_character_boundaries(
    tmp_path, compatibility
):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm["compatibility"] = compatibility
    assert frontmatter._check_value_shapes(skill / "SKILL.md", fm) == []


# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
@pytest.mark.parametrize(
    "compatibility",
    ["", " \n\t ", "x" * 501, None, False, 500, [], {}],
)
def test_compatibility_rejects_invalid_values(tmp_path, compatibility):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm["compatibility"] = compatibility
    assert frontmatter._check_value_shapes(skill / "SKILL.md", fm)


# spec: "`name` and `description` contain no `<` or `>`."
# task: 3
@pytest.mark.parametrize("field", ["name", "description"])
@pytest.mark.parametrize("value", ["<page", "page>", "verify <page>"])
def test_angle_brackets_are_rejected(tmp_path, field, value):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm[field] = value
    assert frontmatter._check_value_shapes(skill / "SKILL.md", fm)


# spec: "Fix llm-wiki's trigger phrase `'verify <page>'` to `'verify a page'`."
# task: 3
def test_llm_wiki_uses_the_replacement_trigger():
    fm, _ = read_skill(REPO / "skills/llm-wiki")
    assert "verify a page" in fm["description"]
    assert "verify <page>" not in fm["description"]


# spec: "Required in every `SKILL.md`, a non-empty string (repo policy, beyond the spec)."
# task: 4
@pytest.mark.parametrize("value", [None, "", False, 1, [], {}])
def test_license_rejects_empty_or_non_string_values(tmp_path, value):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm["license"] = value
    assert frontmatter._check_license(skill / "SKILL.md", fm)


# spec: "Required in every `SKILL.md`, a non-empty string (repo policy, beyond the spec)."
# task: 4
def test_license_is_required_and_mit_is_valid(tmp_path):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    assert frontmatter._check_license(skill / "SKILL.md", fm) == []
    del fm["license"]
    assert frontmatter._check_license(skill / "SKILL.md", fm)


# spec: "R4.3 **Frontmatter** carries the license fields per R1.4."
# task: 4
def test_repository_license_fields_and_superpowers_metadata():
    directories = {path.name: path for path in skill_dirs()}
    for directory in directories.values():
        fm, _ = read_skill(directory)
        assert isinstance(fm.get("license"), str), directory
        assert fm["license"], directory

    adapted = provenance.BUNDLED_LICENSES["LICENSE-superpowers"]
    assert len(adapted) == len(set(adapted)) == 13
    for name in adapted:
        fm, _ = read_skill(directories[name])
        assert fm["license"] == "MIT"
        assert fm["metadata"]["author"] == "Jesse Vincent"
        assert fm["metadata"]["adapted_by"] == "Lowell Mason"
        assert fm["metadata"]["source"] == "https://github.com/obra/superpowers"


# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
@pytest.mark.parametrize("value", ["true", "false", 0, 1, None, [], {}])
def test_invocation_policy_rejects_non_boolean_frontmatter(tmp_path, value):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm["disable-model-invocation"] = value
    assert frontmatter._check_invocation_parity(skill, fm)


# spec: "A skill with `disable-model-invocation: true` must ship `agents/openai.yaml` that parses and sets `policy.allow_implicit_invocation: false`."
# task: 5
def test_manual_only_skill_requires_codex_policy(tmp_path):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm["disable-model-invocation"] = True
    assert frontmatter._check_invocation_parity(skill, fm)

    write_policy(skill, "policy:\n  allow_implicit_invocation: false\n")
    assert frontmatter._check_invocation_parity(skill, fm) == []


# spec: "A skill with `disable-model-invocation: true` must ship `agents/openai.yaml` that parses and sets `policy.allow_implicit_invocation: false`."
# task: 5
@pytest.mark.parametrize(
    "policy",
    [
        "policy: [",
        "[]\n",
        "{}\n",
        "policy: null\n",
        "policy: {}\n",
        "policy:\n  allow_implicit_invocation: true\n",
        "policy:\n  allow_implicit_invocation: 'false'\n",
        "policy:\n  allow_implicit_invocation: null\n",
    ],
)
def test_manual_only_skill_rejects_invalid_codex_policy(tmp_path, policy):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm["disable-model-invocation"] = True
    write_policy(skill, policy)
    assert frontmatter._check_invocation_parity(skill, fm)


# spec: "Conversely, a skill whose `agents/openai.yaml` sets that policy to `false` must set `disable-model-invocation: true`."
# task: 5
@pytest.mark.parametrize("explicit_false", [False, True])
def test_codex_manual_only_policy_requires_matching_frontmatter(
    tmp_path, explicit_false
):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    if explicit_false:
        fm["disable-model-invocation"] = False
    write_policy(skill, "policy:\n  allow_implicit_invocation: false\n")
    assert frontmatter._check_invocation_parity(skill, fm)


# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
def test_automatic_skill_accepts_false_or_absent_boolean(tmp_path):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    assert frontmatter._check_invocation_parity(skill, fm) == []
    fm["disable-model-invocation"] = False
    assert frontmatter._check_invocation_parity(skill, fm) == []


# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
@pytest.mark.parametrize("body_lines, warns", [(499, False), (500, False), (501, True)])
def test_body_advisory_boundary(tmp_path, body_lines, warns):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm["metadata"] = {
        f"field-{index}": "value" for index in range(501)
    }
    write_skill(skill, fm, "body\n" * body_lines)
    warning = frontmatter.skill_body_warning(skill)
    assert (warning is not None) is warns


# spec: "When Stage A adds this warning, it also adds a `skill-body-size` `[[check]]` to `build/cc_guide/conformance.toml` that maps `skills.overview` to it, with `enforced_by = 'check_frontmatter'` (conformance R6 P3)."
# task: 6
def test_body_advisory_has_conformance_register_entry():
    register = tomllib.loads(
        (REPO / "build/cc_guide/conformance.toml").read_text(encoding="utf-8")
    )
    matches = [
        row
        for row in register["check"]
        if "skill-body-size" in list(scalar_values(row))
    ]
    assert len(matches) == 1
    assert matches[0]["enforced_by"] == "check_frontmatter"
    assert "skills.overview" in list(scalar_values(matches[0]))


# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
@pytest.mark.parametrize("key", sorted(HOST_KEYS))
def test_strict_rejects_each_host_key(tmp_path, key):
    skill = make_skill(tmp_path)
    fm, _ = read_skill(skill)
    fm[key] = False if key == "disable-model-invocation" else "example"
    write_skill(skill, fm)
    assert frontmatter.strict_violations(skill)


# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
@pytest.mark.parametrize(
    "name",
    ["claude-example", "example-claude", "anthropic-example", "exampleanthropic"],
)
def test_strict_rejects_reserved_name_substrings(tmp_path, name):
    skill = make_skill(tmp_path, name)
    assert frontmatter.strict_violations(skill)


# spec: "It is not part of the default gate."
# task: 7
def test_default_gate_passes_with_only_the_expected_advisory(capsys):
    assert frontmatter.main([]) == 0
    captured = capsys.readouterr()
    warnings = [
        line for line in captured.err.splitlines() if "WARN" in line
    ]
    assert len(warnings) == 1
    assert "writing-skills" in warnings[0]
    assert "WARN" not in captured.out


# spec: "`check_frontmatter.py --strict` fails on exactly `bayesian-workflow`, `tune-hyperparameters`, and `tech-debt`."
# task: 7
def test_repository_strict_failure_set(capsys):
    failures = {
        directory.name
        for directory in skill_dirs()
        if frontmatter.strict_violations(directory)
    }
    assert failures == {
        "bayesian-workflow",
        "tune-hyperparameters",
        "tech-debt",
    }
    assert frontmatter.main(["--strict"]) != 0
    capsys.readouterr()


# spec: "The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, \"Conformance register\")."
# task: 7
def test_strict_invocation_is_documented_and_claude_md_fits():
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 200
    assert re.search(r"check_frontmatter\.py[ \t]+--strict\b", text)
    assert "claude.ai" in text.lower()
    assert "validator" in text.lower()
    assert "--strict" in (frontmatter.__doc__ or "")


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_provenance_accepts_valid_license_copies(license_repo):
    repo, skills, table = license_repo
    assert provenance.bundled_license_violations(repo, skills, table) == []


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
@pytest.mark.parametrize(
    "relative",
    ["skills/first/LICENSE", "skills/first/LICENSE-superpowers"],
)
@pytest.mark.parametrize("damage", ["missing", "different", "directory", "symlink"])
def test_provenance_rejects_invalid_required_copy(
    license_repo, relative, damage
):
    repo, skills, table = license_repo
    copy = repo / relative
    copy.unlink()
    if damage == "different":
        copy.write_bytes(b"Different license\n")
    elif damage == "directory":
        copy.mkdir()
    elif damage == "symlink":
        copy.symlink_to(repo / copy.name)
    assert provenance.bundled_license_violations(repo, skills, table)


# spec: "No skill directory holds a `LICENSE*` file outside its mapping."
# task: 8
@pytest.mark.parametrize(
    "relative",
    [
        "skills/second/LICENSE-superpowers",
        "skills/first/LICENSE-extra",
        "skills/first/LICENSE-causal-design-sources",
    ],
)
def test_provenance_rejects_unmapped_skill_license(license_repo, relative):
    repo, skills, table = license_repo
    (repo / relative).write_bytes(b"Unmapped license\n")
    assert provenance.bundled_license_violations(repo, skills, table)


# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
def test_provenance_rejects_unmapped_root_license(license_repo):
    repo, skills, table = license_repo
    (repo / "LICENSE-extra").write_bytes(b"Root license\n")
    assert provenance.bundled_license_violations(repo, skills, table)


# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
def test_provenance_rejects_empty_root_license_mapping(license_repo):
    repo, skills, table = license_repo
    table["LICENSE-extra"] = ()
    (repo / "LICENSE-extra").write_bytes(b"Root license\n")
    assert provenance.bundled_license_violations(repo, skills, table)


# spec: "Each skill directory carries regular files (never symlinks, which `install.py --copy` refuses) that are byte-identical to the root license files and carry the same names:"
# task: 8
def test_repository_license_mapping_and_copies():
    directories = {directory.name: directory for directory in skill_dirs()}
    table = provenance.BUNDLED_LICENSES
    expected_roots = {"LICENSE-superpowers", "LICENSE-coding-skills"}
    if (REPO / "LICENSE-andorra").exists():
        expected_roots.add("LICENSE-andorra")
        assert set(table["LICENSE-andorra"]) == {"bayesian-workflow"}

    assert set(table) - {"LICENSE"} == expected_roots
    assert set(table["LICENSE-coding-skills"]) == {
        "bayesian-workflow",
        "clean-code",
    }
    assert len(table["LICENSE-superpowers"]) == 13

    for name, directory in directories.items():
        expected = {"LICENSE"} | {
            filename for filename, names in table.items() if name in names
        }
        actual = {
            path.name
            for path in directory.iterdir()
            if path.name.startswith("LICENSE")
        }
        assert actual == expected, name
        for filename in expected:
            copy = directory / filename
            assert copy.is_file() and not copy.is_symlink(), copy
            assert copy.read_bytes() == (REPO / filename).read_bytes(), copy

    for filename, names in table.items():
        assert names, filename
        assert set(names) <= set(directories), filename

    root_files = {
        path.name for path in REPO.glob("LICENSE*") if path.is_file()
    }
    assert root_files == {"LICENSE"} | set(table)
    assert provenance.bundled_license_violations(
        REPO, sorted(directories), table
    ) == []


# spec: "The script stays stdlib-only, so its CLAUDE.md command keeps no `--with`."
# task: 8
def test_provenance_uses_only_stdlib_and_needs_no_with_flag():
    tree = ast.parse(Path(provenance.__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.level == 0
            imported.add(node.module.split(".")[0])
    assert imported <= sys.stdlib_module_names

    commands = [
        line
        for line in (REPO / "CLAUDE.md").read_text(encoding="utf-8").splitlines()
        if "check_provenance.py" in line
    ]
    assert commands
    assert all("--with" not in line for line in commands)


# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
def test_runnable_inventory_matches_the_sixteen_named_scripts():
    actual = {
        path.relative_to(REPO / "skills").as_posix()
        for directory in skill_dirs()
        for path in frontmatter.runnable_scripts(directory)
    }
    assert actual == RUNNABLE_PATHS


# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
def test_inventory_excludes_libraries_and_mentions_of_guards(tmp_path):
    skill = make_skill(tmp_path)
    runnable = write_script(skill)
    write_script(skill, "library.py", "def example():\n    pass\n")
    write_script(
        skill,
        "mention.py",
        "NOTE = 'if __name__ == \"__main__\":'\n",
    )
    assert set(frontmatter.runnable_scripts(skill)) == {runnable}


# spec: "`tune-hyperparameters/scripts/time_series_cv.py` has no `__main__` guard; it is a library imported into the user's code and stays header-less."
# task: 10
def test_time_series_cv_stays_a_headerless_library():
    directory = REPO / "skills/tune-hyperparameters"
    path = directory / "scripts/time_series_cv.py"
    assert path not in frontmatter.runnable_scripts(directory)
    assert frontmatter.script_metadata(path.read_text(encoding="utf-8")) is None


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_script_metadata_parser():
    assert frontmatter.script_metadata(script_source()) == {
        "requires-python": ">=3.11",
        "dependencies": [],
    }
    assert frontmatter.script_metadata("print('no header')\n") is None
    with pytest.raises(tomllib.TOMLDecodeError):
        frontmatter.script_metadata(
            "# /// script\n"
            "# requires-python = [\n"
            "# ///\n"
        )


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
@pytest.mark.parametrize(
    "header",
    [
        "",
        "# /// script\n# dependencies = []\n# ///\n",
        "# /// script\n# requires-python = '>=3.11'\n# ///\n",
        "# /// script\n# dependencies = [\n# ///\n",
    ],
)
def test_header_lint_rejects_missing_incomplete_or_invalid_metadata(
    tmp_path, header
):
    skill = make_skill(tmp_path)
    write_script(
        skill,
        text=header + "if __name__ == '__main__':\n    pass\n",
    )
    assert frontmatter.check_script_headers(skill)


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_no_runnable_script_is_exempted_by_a_vendored_listing(tmp_path):
    skill = make_skill(tmp_path)
    path = write_script(
        skill,
        text="if __name__ == '__main__':\n    pass\n",
    )
    key = path.relative_to(tmp_path).as_posix()
    assert frontmatter.check_script_headers(
        skill, vendored=frozenset({key})
    )


# spec: "Every third-party import, including function-level imports, is declared with a `>=` floor at the major version the suite currently resolves (e.g. `'polars>=1.0'`)."
# task: 10
def test_required_imports_include_function_level_imports(tmp_path):
    tree = ast.parse(
        "import sys\n"
        "import json\n"
        "import helper\n"
        "def example():\n"
        "    import polars\n"
        "    from numpy.linalg import norm\n"
    )
    assert frontmatter.required_imports(tree, {"helper"}) == {
        "polars",
        "numpy",
    }


# spec: "Imports inside a `try` whose handler catches `ImportError` or `ModuleNotFoundError` are optional and may be left undeclared."
# task: 10
@pytest.mark.parametrize(
    "handler",
    ["ImportError", "ModuleNotFoundError", "(ImportError, ModuleNotFoundError)"],
)
def test_optional_imports_can_be_undeclared(tmp_path, handler):
    skill = make_skill(tmp_path)
    write_script(
        skill,
        text=script_source(
            f"try:\n"
            f"    import polars\n"
            f"except {handler}:\n"
            f"    pass\n"
            f"if __name__ == '__main__':\n"
            f"    pass\n"
        ),
    )
    assert frontmatter.check_script_headers(skill) == []


# spec: "In such a script, every non-stdlib, non-local import is declared in `dependencies`:"
# task: 10
def test_optional_try_does_not_exempt_handler_else_or_finally_imports():
    tree = ast.parse(
        "try:\n"
        "    import optional_package\n"
        "except ImportError:\n"
        "    import fallback_package\n"
        "else:\n"
        "    import success_package\n"
        "finally:\n"
        "    import final_package\n"
    )
    assert frontmatter.required_imports(tree, set()) == {
        "fallback_package",
        "success_package",
        "final_package",
    }


# spec: "In such a script, every non-stdlib, non-local import is declared in `dependencies`:"
# task: 10
def test_unrelated_exception_handler_does_not_exempt_imports():
    tree = ast.parse(
        "try:\n"
        "    import polars\n"
        "except ValueError:\n"
        "    pass\n"
    )
    assert frontmatter.required_imports(tree, set()) == {"polars"}


# spec: "import names map to distributions through a small alias table, e.g. `yaml` → `pyyaml`;"
# task: 10
def test_import_aliases_are_checked_against_distribution_names(tmp_path):
    skill = make_skill(tmp_path)
    body = (
        "def example():\n"
        "    import yaml\n"
        "if __name__ == '__main__':\n"
        "    example()\n"
    )
    write_script(skill, text=script_source(body))
    assert frontmatter.check_script_headers(skill)
    write_script(
        skill,
        text=script_source(body, dependencies=("pyyaml>=6.0",)),
    )
    assert frontmatter.check_script_headers(skill) == []


# spec: "local means a sibling module file in the same directory;"
# task: 10
def test_local_and_stdlib_imports_need_no_dependencies(tmp_path):
    skill = make_skill(tmp_path)
    write_script(skill, "helper.py", "VALUE = 1\n")
    write_script(
        skill,
        text=script_source(
            "import sys\n"
            "import pathlib\n"
            "import tomllib\n"
            "import helper\n"
            "if __name__ == '__main__':\n"
            "    pass\n"
        ),
    )
    assert frontmatter.check_script_headers(skill) == []


# spec: "Line 1 is `#!/usr/bin/env python3`; add it where missing."
# task: 10
def test_all_runnable_scripts_use_the_house_shebang():
    for relative in sorted(RUNNABLE_PATHS):
        path = REPO / "skills" / relative
        assert path.read_text(encoding="utf-8").splitlines()[0] == (
            "#!/usr/bin/env python3"
        ), relative


# spec: "Then a `# /// script` block with single-quoted TOML strings, a `requires-python`, and a `dependencies` list (`[]` for stdlib-only scripts)."
# task: 10
def test_repository_headers_use_single_quoted_metadata():
    for relative in sorted(RUNNABLE_PATHS):
        text = (REPO / "skills" / relative).read_text(encoding="utf-8")
        after_shebang = [
            line for line in text.splitlines()[1:] if line.strip()
        ]
        assert after_shebang[0] == "# /// script", relative
        block = metadata_block(text)
        metadata = tomllib.loads(block)
        assert frontmatter.script_metadata(text) == metadata
        assert metadata["requires-python"] in {
            ">=3.11",
            ">=3.12",
            ">=3.13",
        }, relative
        assert isinstance(metadata["dependencies"], list), relative
        assert re.search(
            r"(?m)^\s*requires-python\s*=\s*'[^'\n]+'\s*(?:#.*)?$",
            block,
        ), relative

        dependency_match = re.search(
            r"\bdependencies\s*=\s*\[(.*?)\]", block, re.DOTALL
        )
        assert dependency_match, relative
        remaining = re.sub(
            r"'[^'\n]*'", "", dependency_match.group(1)
        )
        remaining = re.sub(r"(?m)#.*$", "", remaining)
        assert not remaining.replace(",", "").strip(), relative

        for dependency in metadata["dependencies"]:
            assert isinstance(dependency, str), relative
            requirement = dependency.split(";", 1)[0].strip()
            assert re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9._-]*"
                r"(?:\[[A-Za-z0-9,._-]+\])?"
                r"\s*>=\s*\d+(?:\.\d+)*",
                requirement,
            ), (relative, dependency)

    for directory in skill_dirs():
        assert frontmatter.check_script_headers(directory) == [], directory


# spec: "Path forms in use: `<this-skill-dir>/scripts/x.py`, `<this-skill-dir>/../<skill>/scripts/x.py`, `$LLM_WIKI_ROOT/scripts/x.py` (the installed copies), `~/Projects/agent-skills/skills/llm-wiki/scripts/x.py` (llm-wiki's INSTALL.md), and repo-relative `skills/<skill>/scripts/build.py`."
# task: 11
@pytest.mark.parametrize(
    "documented, target",
    [
        ("<this-skill-dir>/scripts/example.py", "example/scripts/example.py"),
        (
            "<this-skill-dir>/../other/scripts/example.py",
            "other/scripts/example.py",
        ),
        (
            "$LLM_WIKI_ROOT/scripts/example.py",
            "llm-wiki/scripts/example.py",
        ),
        (
            "~/Projects/agent-skills/skills/llm-wiki/scripts/example.py",
            "llm-wiki/scripts/example.py",
        ),
        (
            "skills/geographic-codes/scripts/build.py",
            "geographic-codes/scripts/build.py",
        ),
    ],
)
def test_resolve_each_documented_path_form(tmp_path, documented, target):
    skill = make_skill(tmp_path)
    target_path = tmp_path / "skills" / target
    write_script(target_path.parent.parent, target_path.name)
    resolved = frontmatter.resolve_bundled_script(documented, skill)
    assert resolved is not None
    assert resolved.resolve() == target_path.resolve()


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
@pytest.mark.parametrize(
    "command",
    [
        "python <this-skill-dir>/scripts/example.py",
        "python3 <this-skill-dir>/scripts/example.py",
        "python \\\n  <this-skill-dir>/scripts/example.py",
        "python3 \\\n  <this-skill-dir>/scripts/example.py",
        (
            "uv run --no-project --python 3.13 python "
            "<this-skill-dir>/scripts/example.py"
        ),
        (
            "uv run --python 3.13 --with polars python "
            "<this-skill-dir>/scripts/example.py"
        ),
    ],
)
def test_invocation_lint_rejects_superseded_runners(tmp_path, command):
    skill = make_skill(tmp_path)
    write_script(skill)
    write_invocation(skill, command, "references/usage.md")
    assert frontmatter.check_invocations(skill)


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
def test_uv_invocations_are_reported_and_accepted(tmp_path):
    skill = make_skill(tmp_path)
    write_script(skill)
    documented_path = "<this-skill-dir>/scripts/example.py"
    markdown = write_invocation(
        skill, f"uv run {documented_path} --help", "references/usage.md"
    )
    assert (markdown, "uv run", documented_path) in (
        frontmatter.bundled_invocations(skill)
    )
    assert frontmatter.check_invocations(skill) == []


# spec: "A path that does not resolve to a bundled script, such as `writing-skills/anthropic-best-practices.md`'s teaching example `scripts/migrate.py`, is not flagged."
# task: 11
def test_unresolved_teaching_example_is_not_flagged(tmp_path):
    skill = make_skill(tmp_path, "writing-skills")
    write_invocation(
        skill,
        "python scripts/migrate.py",
        "anthropic-best-practices.md",
    )
    assert frontmatter.resolve_bundled_script("scripts/migrate.py", skill) is None
    assert frontmatter.check_invocations(skill) == []


# spec: "Each skill with such an invocation gets this sentence once, near its first invocation: \"Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.\""
# task: 11
def test_repository_invocations_have_one_fallback_sentence_per_skill():
    for directory in skill_dirs():
        invocations = frontmatter.bundled_invocations(directory)
        assert frontmatter.check_invocations(directory) == [], directory
        if not invocations:
            continue
        assert all(runner == "uv run" for _, runner, _ in invocations), directory
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in directory.rglob("*.md")
        )
        assert text.count(FALLBACK) == 1, directory


# spec: "A skill whose markdown runs a bundled script via `uv run` declares a `compatibility` value containing `uv`."
# task: 12
@pytest.mark.parametrize("value", [None, "", "Requires Python 3.11+."])
def test_uv_invocation_requires_uv_compatibility(tmp_path, value):
    skill = make_skill(tmp_path)
    write_script(skill)
    write_invocation(skill, "uv run <this-skill-dir>/scripts/example.py")
    fm, _ = read_skill(skill)
    if value is not None:
        fm["compatibility"] = value
    assert frontmatter._check_compatibility_names_uv(skill, fm)

    fm["compatibility"] = (
        "Requires uv to run bundled scripts "
        "(dependencies are declared inline); Python 3.11+."
    )
    assert frontmatter._check_compatibility_names_uv(skill, fm) == []


# spec: "Here 3.X is the highest `requires-python` floor among the scripts that skill invokes."
# task: 12
def test_repository_compatibility_matches_all_invoked_script_floors():
    for directory in skill_dirs():
        invocations = frontmatter.bundled_invocations(directory)
        if not invocations:
            continue
        floors = []
        for _, runner, documented_path in invocations:
            assert runner == "uv run"
            path = frontmatter.resolve_bundled_script(
                documented_path, directory
            )
            assert path is not None
            metadata = frontmatter.script_metadata(
                path.read_text(encoding="utf-8")
            )
            assert metadata is not None
            match = re.fullmatch(
                r">=3\.(11|12|13)", metadata["requires-python"]
            )
            assert match, path
            floors.append(int(match.group(1)))

        fm, _ = read_skill(directory)
        assert fm["compatibility"] == (
            "Requires uv to run bundled scripts "
            "(dependencies are declared inline); "
            f"Python 3.{max(floors)}+."
        ), directory


# spec: "That set includes `finishing-a-development-branch`, which runs `writing-plans`' `deferred_stats.py`."
# task: 12
def test_finishing_declares_compatibility_for_deferred_stats():
    directory = REPO / "skills/finishing-a-development-branch"
    expected = REPO / "skills/writing-plans/scripts/deferred_stats.py"
    resolved = {
        frontmatter.resolve_bundled_script(path, directory)
        for _, runner, path in frontmatter.bundled_invocations(directory)
        if runner == "uv run"
    }
    assert expected in resolved
    fm, _ = read_skill(directory)
    assert "uv" in fm["compatibility"]


# spec: "Record the scenario, prompts, outputs, and verdicts in `specs/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house red-baseline format."
# task: 2
def test_red_baseline_record_exists_with_a_valid_date():
    prefix = "red-baseline-description-openings-"
    records = list(
        (REPO / "specs").glob(f"{prefix}????-??-??.md")
    )
    assert records
    for record in records:
        date.fromisoformat(record.stem.removeprefix(prefix))
        assert record.read_text(encoding="utf-8").strip()


# spec: "The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list)."
# task: 14
def test_token_efficiency_note_preserves_the_spec_measurement():
    _, body = read_skill(REPO / "skills/writing-skills")
    section = markdown_section(body, "Token Efficiency")
    for fact in (
        "Codex",
        "156",
        "164",
        "93",
        "0.154",
        "2026-10-03",
        "codex debug prompt-input",
    ):
        assert fact in section
</tests>
<flags>
<flag task="3"><spec>R2.2's red-baseline file exists, and `writing-skills` changed only as R2.3's outcome branch allows.</spec><plan>`skills/writing-skills/SKILL.md` (the optional-keys bullet)</plan></flag>
<flag task="4"><spec>R2.2's red-baseline file exists, and `writing-skills` changed only as R2.3's outcome branch allows.</spec><plan>`skills/writing-skills/SKILL.md` (required fields, optional keys, template, checklist)</plan></flag>
<flag task="7"><spec>CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run)</spec><plan>`CLAUDE.md` (Commands: the frontmatter lint's comment names `--strict`; no line added, D7)</plan></flag>
<flag task="8"><spec>No skill directory holds a `LICENSE*` file outside its mapping.</spec><plan>Rename: `skills/recommend-causal-design/LICENSE` to `skills/recommend-causal-design/LICENSE-causal-design-sources`, and re-point its links in that skill's `SKILL.md`, `README.md` and `references/sources.md`</plan></flag>
<flag task="9"><spec>only if R4.5 finds an upstream notice</spec><plan>Create: `LICENSE-andorra` (upstream's text, verbatim) and its copy `skills/bayesian-workflow/LICENSE-andorra`</plan></flag>
<flag task="10"><spec>Fourteen gain a header:</spec><plan>Modify: the 15 header-less runnable scripts (helper script): a shebang where missing, then the header</plan></flag>
</flags>
<untestable>
Agents and commands are not Agent Skills and are unaffected.
The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").
Criterion: within its first 150 characters, a description names the skill's primary trigger, the task or symptom it exists for, so an agent shown only that prefix would load it for its canonical use.
All 32 descriptions pass as of 2026-10-03.
Both pass, so neither is rewritten.
Before any edit to `writing-skills`, run a baseline:
5 reps, each a fresh agent given the current `writing-skills` description guidance (the control: no new wording).
Each is asked to write a SKILL.md description for a synthetic skill that is not from this repo and has at least 8 trigger conditions, one of them designated in the scenario as primary.
Run from a session whose cwd was never this repo.
A rep passes if the designated primary trigger lies within the first 150 characters.
The controller reads each output and records the verbatim 150-character prefix.
Record the scenario, prompts, outputs, and verdicts in `specs/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house red-baseline format.
**Baseline ≥ 4/5:** add only a factual note of 2–4 lines to `writing-skills`' "Token Efficiency" section.
The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list).
No new rule.
**Baseline ≤ 3/5:** also add one checklist line ("the primary trigger falls within the first ~150 characters") and GREEN-test it: 5 reps with the new wording, at least 4/5 passing, recorded in the same red-baseline file.
Use the lowest of `'>=3.11'`, `'>=3.12'`, `'>=3.13'` under which the test suite covering the script passes, run with `uv run --python 3.X` and that suite's CLAUDE.md dependencies.
Scripts covered by one suite share its floor, unless a failure is attributable to one script, which then alone takes the higher floor.
Prose floors that disagree with the header are aligned or removed (e.g. "Python ≥ 3.9" in `recommend-probabilistic-model` and `recommend-visualization`).
Every third-party import, including function-level imports, is declared with a `>=` floor at the major version the suite currently resolves (e.g. `'polars>=1.0'`).
Runtime backends that the script never imports but needs to read its inputs (e.g. `h5netcdf` for NetCDF) are added when R3.8's fixture run shows them needed.
Each skill with such an invocation gets this sentence once, near its first invocation: "Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header."
Each rule gets a RED test first.
From an empty scratch directory (a subdirectory such as `/tmp/bwprobe/`, never `/tmp` itself), each of the 16 scripts runs `uv run <absolute-path>` on a minimal real input that exercises its main code path.
`--help` alone is enough only for a script with no input-reading path.
The three ArviZ-reading scripts (`diagnose_model.py`, `calibration_check.py`, `compare_experiments.py`) each read a small saved InferenceData fixture.
One script is also run from inside a directory holding an unrelated `pyproject.toml`.
This proves the header isolates it from the project environment.
R3.9 The dependency-drift check still passes.
Invocation text changes, but no cross-skill reference is added or dropped; finishing → `writing-plans`' `deferred_stats.py` is an existing `DEPENDENCIES` edge.
NOTICE gains one paragraph near the top: each skill directory carries copies of the license texts that apply to it, so a single-skill install (`install.py --copy --skill`, or a third-party installer) keeps the notice MIT requires.
The root files are canonical, and `check_provenance.py` enforces the copies.
README's License section gains one sentence to the same effect.
CLAUDE.md's provenance section gains the invariant and names the enforcing lint, under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").
Locate Alexandre Andorra's original PyMC Bayesian-workflow skill and read its license.
Add the upstream license text verbatim as root `LICENSE-andorra`, map it to `bayesian-workflow`, and extend NOTICE's `bayesian-workflow/` block with the source URL and the quoted copyright line.
NOTICE records that, in the form already used for the Fonnesbeck repository.
Nothing is bundled.
NOTICE is unchanged and a deferred item is logged with what was searched.
Never compose a copyright line that is not quoted from the source.
The 2026-08-26 intake review (`specs/completed/skill-intake-review-2026-08-26.md`) already found that Andorra appears nowhere in the history of pymc-labs/python-analytics-skills (only Fonnesbeck and Dean commit there), so start the search from his own publications rather than that repository.
Stages, in order.
D is independent of C and may run alongside it.
When Stage A or Stage D fixes a gap the register tracks to it, the same change removes or narrows that `[[exception]]` and runs `build/check_conformance.py` (R6 P2).
**Work in a worktree.**
Commit from the worktree; the shared checkout's branch can change under a concurrent session.
**Stage D's micro-test** runs from a session whose cwd was never this repo; inherited session context voids reps otherwise.
**State test changes as +N deltas** against the suite, never absolute totals.
**Before allocating the plan id**, check `specs/plans/` on every branch (`git ls-tree`); ids are allocated per branch and have collided.
**Coordinate with the in-flight JAX spec.**
Whichever branch merges second brings the other's skills into conformance in the same merge, or the new lints fail on arrival.
Every gate in CLAUDE.md's Commands passes:
Each new lint rule has a test that failed before its implementation and passes after.
R3.8's execution proof is recorded for all 16 scripts.
`gemini skills list --all` shows every skill under `skills/` as `[Enabled]`;
`codex debug prompt-input` lists every skill under `skills/` by name.
R2.2's red-baseline file exists, and `writing-skills` changed only as R2.3's outcome branch allows.
</untestable>