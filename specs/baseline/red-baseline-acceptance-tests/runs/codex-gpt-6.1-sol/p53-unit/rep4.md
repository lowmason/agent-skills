<tests>
import ast
import importlib.util
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

import pytest
import yaml


SPEC_KEYS = {
    "name", "description", "license", "compatibility", "metadata", "allowed-tools",
}
HOST_KEYS = {
    "when_to_use", "model", "effort", "context", "disable-model-invocation",
}
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
FALLBACK = (
    "Without uv, run the same path with `python3` in an environment "
    "that has the dependencies listed in the script's header."
)
SUPERPOWERS_SOURCE = "https://github.com/obra/superpowers"
ABSENT = object()


@pytest.fixture(scope="session")
def repo(pytestconfig):
    root = Path(pytestconfig.rootpath)
    assert (root / "build/check_frontmatter.py").is_file()
    return root


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def frontmatter(repo):
    return _load_module(
        "portability_acceptance_frontmatter",
        repo / "build/check_frontmatter.py",
    )


@pytest.fixture(scope="session")
def provenance(repo):
    return _load_module(
        "portability_acceptance_provenance",
        repo / "build/check_provenance.py",
    )


def _skills(root):
    return sorted(path.parent for path in (root / "skills").glob("*/SKILL.md"))


def _read_frontmatter(skill):
    text = (skill / "SKILL.md").read_text()
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    assert match, skill
    return yaml.safe_load(match.group(1))


def _write_frontmatter(skill, data, body=""):
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body
    )


def _make_skill(root, name="example", changes=None, omit=(), body=""):
    skill = root / "skills" / name
    data = {
        "name": name,
        "description": "Use when editing Python.",
        "license": "MIT",
    }
    data.update(changes or {})
    for key in omit:
        data.pop(key, None)
    _write_frontmatter(skill, data, body)
    return skill, data


def _script_text(dependencies=(), floor=">=3.11", body=""):
    dependencies = ", ".join(repr(item) for item in dependencies)
    return (
        "#!/usr/bin/env python3\n"
        "# /// script\n"
        f"# requires-python = '{floor}'\n"
        f"# dependencies = [{dependencies}]\n"
        "# ///\n"
        f"{body}\n"
        "if __name__ == '__main__':\n"
        "    pass\n"
    )


def _write_script(skill, name="profile.py", text=None):
    path = skill / "scripts" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_script_text() if text is None else text)
    return path


def _has_main_guard(text):
    tree = ast.parse(text)
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not (
            isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and len(test.comparators) == 1
        ):
            continue
        left, right = test.left, test.comparators[0]
        for name, value in ((left, right), (right, left)):
            if (
                isinstance(name, ast.Name)
                and name.id == "__name__"
                and isinstance(value, ast.Constant)
                and value.value == "__main__"
            ):
                return True
    return False


def _metadata_block(text):
    match = re.search(
        r"(?ms)^# /// script[ \t]*\r?\n(.*?)^# ///[ \t]*(?:\r?\n|\Z)",
        text,
    )
    assert match
    lines = match.group(1).splitlines()
    assert all(line.startswith("#") for line in lines)
    return "\n".join(
        line[2:] if line.startswith("# ") else line[1:] for line in lines
    )


def _isolated_lint(root, source_repo, *args):
    target = root / "build/check_frontmatter.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_repo / "build/check_frontmatter.py", target)
    return subprocess.run(
        [sys.executable, str(target), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def _section(text, title):
    heading = re.search(
        rf"(?m)^(#{{1,6}})[ \t]+{re.escape(title)}[ \t]*$",
        text,
    )
    assert heading, title
    remainder = text[heading.end():]
    next_heading = re.search(
        rf"(?m)^#{{1,{len(heading.group(1))}}}[ \t]+",
        remainder,
    )
    return remainder[:next_heading.start()] if next_heading else remainder


def _scalars(value):
    if isinstance(value, dict):
        return [item for child in value.values() for item in _scalars(child)]
    if isinstance(value, list):
        return [item for child in value for item in _scalars(child)]
    return [value]


def _invoked_scripts(frontmatter, skill):
    result = set()
    for markdown, runner, path in frontmatter.bundled_invocations(skill):
        assert markdown.is_file()
        assert runner in {"python", "python3", "uv run"}
        resolved = frontmatter.resolve_bundled_script(path, skill)
        assert resolved is not None, (markdown, path)
        result.add(resolved.resolve())
    return result


def _highest_floor(frontmatter, scripts):
    floors = []
    for script in scripts:
        metadata = frontmatter.script_metadata(script.read_text())
        assert metadata is not None, script
        match = re.fullmatch(r">=(3)\.(11|12|13)", metadata["requires-python"])
        assert match, script
        floors.append(tuple(map(int, match.groups())))
    return max(floors)


def _expected_compatibility(floor):
    major, minor = floor
    return (
        "Requires uv to run bundled scripts "
        "(dependencies are declared inline); "
        f"Python {major}.{minor}+."
    )


# spec: "Replace `ALLOWED_KEYS` with two named sets and allow their union in a `SKILL.md`:"
# task: 3
def test_frontmatter_key_sets(frontmatter):
    assert set(frontmatter.SPEC_KEYS) == SPEC_KEYS
    assert set(frontmatter.HOST_KEYS) == HOST_KEYS
    assert set(frontmatter.SPEC_KEYS) & set(frontmatter.HOST_KEYS) == set()


@pytest.mark.parametrize(
    "value, valid",
    [
        ({}, True),
        ({"author": "Jesse Vincent", "adapted_by": "Lowell Mason"}, True),
        ({1: "Lowell Mason"}, False),
        ({"author": 1}, False),
        ({"author": False}, False),
        ({"author": None}, False),
        ({"author": {"source": SUPERPOWERS_SOURCE}}, False),
        ([], False),
        ("MIT", False),
        (None, False),
    ],
)
# spec: "When present, a mapping whose keys and values are all strings."
# task: 3
def test_metadata_shape(tmp_path, frontmatter, value, valid):
    skill, data = _make_skill(tmp_path, changes={"metadata": value})
    errors = frontmatter._check_value_shapes(skill / "SKILL.md", data)
    assert (errors == []) is valid, errors


@pytest.mark.parametrize(
    "value, valid",
    [
        ("x", True),
        ("x" * 500, True),
        (" \n" + "x" * 500 + "\t ", True),
        ("", False),
        (" \n\t ", False),
        ("x" * 501, False),
        (None, False),
        (500, False),
        (True, False),
        ([], False),
    ],
)
# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
def test_compatibility_shape(tmp_path, frontmatter, value, valid):
    skill, data = _make_skill(tmp_path, changes={"compatibility": value})
    errors = frontmatter._check_value_shapes(skill / "SKILL.md", data)
    assert (errors == []) is valid, errors


# spec: "When present, a string of 1–500 characters after stripping."
# task: 3
def test_optional_shape_fields_may_be_absent(tmp_path, frontmatter):
    skill, data = _make_skill(tmp_path)
    assert frontmatter._check_value_shapes(skill / "SKILL.md", data) == []


@pytest.mark.parametrize("field", ["name", "description"])
@pytest.mark.parametrize("bracket", ["<", ">"])
# spec: "`name` and `description` contain no `<` or `>`."
# task: 3
def test_angle_brackets_rejected(tmp_path, frontmatter, field, bracket):
    skill, data = _make_skill(tmp_path, changes={field: "example" + bracket})
    assert frontmatter._check_value_shapes(skill / "SKILL.md", data)


# spec: "Fix llm-wiki's trigger phrase `'verify <page>'` to `'verify a page'`."
# task: 3
def test_llm_wiki_trigger_wording(repo):
    description = _read_frontmatter(repo / "skills/llm-wiki")["description"]
    assert "verify a page" in description
    assert "verify <page>" not in description


@pytest.mark.parametrize(
    "value, valid",
    [
        (ABSENT, False),
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
def test_license_shape(tmp_path, frontmatter, value, valid):
    changes = {} if value is ABSENT else {"license": value}
    omit = ("license",) if value is ABSENT else ()
    skill, data = _make_skill(tmp_path, changes=changes, omit=omit)
    errors = frontmatter._check_license(skill / "SKILL.md", data)
    assert (errors == []) is valid, errors


# spec: "**Frontmatter** carries the license fields per R1.4."
# task: 4
def test_superpowers_frontmatter(repo):
    adapted = [
        skill
        for skill in _skills(repo)
        if _read_frontmatter(skill).get("metadata", {}).get("source")
        == SUPERPOWERS_SOURCE
    ]
    assert len(adapted) == 13
    for skill in adapted:
        data = _read_frontmatter(skill)
        assert data["license"] == "MIT", skill
        assert data["metadata"]["author"] == "Jesse Vincent", skill
        assert data["metadata"]["adapted_by"] == "Lowell Mason", skill


@pytest.mark.parametrize(
    "value, valid",
    [
        (True, True),
        (False, True),
        ("true", False),
        ("false", False),
        ("yes", False),
        (0, False),
        (1, False),
        (None, False),
        ([], False),
        ({}, False),
    ],
)
# spec: "For a `SKILL.md`, `disable-model-invocation` must be a YAML boolean when present."
# task: 5
def test_disable_model_invocation_is_boolean(
    tmp_path, frontmatter, value, valid
):
    skill, data = _make_skill(
        tmp_path, changes={"disable-model-invocation": value}
    )
    policy = {"policy": {"allow_implicit_invocation": value is not True}}
    adapter = skill / "agents/openai.yaml"
    adapter.parent.mkdir()
    adapter.write_text(yaml.safe_dump(policy))
    errors = frontmatter._check_invocation_parity(skill, data)
    assert (errors == []) is valid, errors


@pytest.mark.parametrize(
    "policy, valid",
    [
        (ABSENT, False),
        ({"policy": {"allow_implicit_invocation": False}}, True),
        ({"policy": {"allow_implicit_invocation": True}}, False),
        ({"policy": {"allow_implicit_invocation": "false"}}, False),
        ({"policy": {"allow_implicit_invocation": 0}}, False),
        ({"policy": {}}, False),
        ({}, False),
        (None, False),
        ("policy: [", False),
    ],
)
# spec: "A skill with `disable-model-invocation: true` must ship `agents/openai.yaml` that parses and sets `policy.allow_implicit_invocation: false`."
# task: 5
def test_manual_skill_requires_codex_policy(
    tmp_path, frontmatter, policy, valid
):
    skill, data = _make_skill(
        tmp_path, changes={"disable-model-invocation": True}
    )
    if policy is not ABSENT:
        adapter = skill / "agents/openai.yaml"
        adapter.parent.mkdir()
        adapter.write_text(
            policy if isinstance(policy, str) else yaml.safe_dump(policy)
        )
    errors = frontmatter._check_invocation_parity(skill, data)
    assert (errors == []) is valid, errors


@pytest.mark.parametrize("value", [ABSENT, False])
# spec: "Conversely, a skill whose `agents/openai.yaml` sets that policy to `false` must set `disable-model-invocation: true`."
# task: 5
def test_codex_manual_policy_requires_frontmatter(
    tmp_path, frontmatter, value
):
    changes = {} if value is ABSENT else {"disable-model-invocation": value}
    skill, data = _make_skill(tmp_path, changes=changes)
    adapter = skill / "agents/openai.yaml"
    adapter.parent.mkdir()
    adapter.write_text("policy:\n  allow_implicit_invocation: false\n")
    assert frontmatter._check_invocation_parity(skill, data)


@pytest.mark.parametrize("count", [499, 500, 501])
# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
def test_body_warning_boundary(tmp_path, frontmatter, count):
    skill, _ = _make_skill(tmp_path, body="body line\n" * count)
    warning = frontmatter.skill_body_warning(skill)
    assert (warning is not None) is (count > 500)


# spec: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
# task: 6
def test_body_warning_cli_is_advisory(tmp_path, repo):
    _make_skill(tmp_path, body="body line\n" * 501)
    result = _isolated_lint(tmp_path, repo)
    assert result.returncode == 0, result.stdout + result.stderr
    warnings = [
        line for line in result.stderr.splitlines()
        if re.search(r"\bWARN\b", line)
    ]
    assert len(warnings) == 1
    assert "example" in warnings[0]
    assert not re.search(r"\bWARN\b", result.stdout)


# spec: "When Stage A adds this warning, it also adds a `skill-body-size` `[[check]]` to `build/cc_guide/conformance.toml` that maps `skills.overview` to it, with `enforced_by = 'check_frontmatter'` (conformance R6 P3)."
# task: 6
def test_body_warning_conformance_registration(repo):
    register = tomllib.loads(
        (repo / "build/cc_guide/conformance.toml").read_text()
    )
    rows = [
        row for row in register["check"]
        if "skill-body-size" in _scalars(row)
    ]
    assert len(rows) == 1
    assert "skills.overview" in _scalars(rows[0])
    assert rows[0]["enforced_by"] == "check_frontmatter"


@pytest.mark.parametrize("key", sorted(HOST_KEYS))
# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
def test_strict_rejects_each_host_key(tmp_path, frontmatter, key):
    skill, _ = _make_skill(tmp_path, changes={key: False})
    assert frontmatter.strict_violations(skill)


@pytest.mark.parametrize(
    "name, rejected",
    [
        ("claude", True),
        ("example-claude", True),
        ("anthropic", True),
        ("example-anthropic-example", True),
        ("bayesian-workflow", False),
    ],
)
# spec: "`check_frontmatter.py --strict` additionally fails on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or `anthropic`."
# task: 7
def test_strict_reserved_name_substrings(
    tmp_path, frontmatter, name, rejected
):
    skill, _ = _make_skill(tmp_path, name=name)
    assert bool(frontmatter.strict_violations(skill)) is rejected


# spec: "It is not part of the default gate."
# task: 7
def test_strict_is_opt_in(tmp_path, repo):
    _make_skill(tmp_path, changes={"effort": "high"})
    default = _isolated_lint(tmp_path, repo)
    strict = _isolated_lint(tmp_path, repo, "--strict")
    assert default.returncode == 0, default.stdout + default.stderr
    assert strict.returncode != 0


# spec: "Agents and commands are not Agent Skills and are unaffected."
# task: 7
def test_strict_does_not_apply_skill_rules_to_agents_or_commands(
    tmp_path, repo
):
    _make_skill(tmp_path)
    for directory, name in (
        ("agents", "claude"),
        ("commands", "anthropic"),
    ):
        path = tmp_path / directory / f"{name}.md"
        path.parent.mkdir()
        data = {"name": name, "description": "Use when editing Python."}
        if directory == "commands":
            data["disable-model-invocation"] = True
        path.write_text(
            "---\n" + yaml.safe_dump(data) + "---\nBody.\n"
        )
    default = _isolated_lint(tmp_path, repo)
    strict = _isolated_lint(tmp_path, repo, "--strict")
    assert default.returncode == 0, default.stdout + default.stderr
    assert strict.returncode == 0, strict.stdout + strict.stderr


# spec: "`check_frontmatter.py --strict` fails on exactly `bayesian-workflow`, `tune-hyperparameters`, and `tech-debt`."
# task: 7
def test_repository_strict_failures(repo, frontmatter):
    failures = {
        skill.name
        for skill in _skills(repo)
        if frontmatter.strict_violations(skill)
    }
    assert failures == {
        "bayesian-workflow", "tune-hyperparameters", "tech-debt",
    }
    result = subprocess.run(
        [
            sys.executable,
            str(repo / "build/check_frontmatter.py"),
            "--strict",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0


# spec: "The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, \"Conformance register\")."
# task: 7
def test_strict_has_a_documented_command(repo, frontmatter):
    assert "--strict" in (frontmatter.__doc__ or "")
    commands = _section((repo / "CLAUDE.md").read_text(), "Commands")
    commands = re.sub(r"\\\r?\n", " ", commands)
    invocations = []
    for line in commands.splitlines():
        tokens = shlex.split(line, comments=True)
        if any(token.endswith("check_frontmatter.py") for token in tokens):
            invocations.append(tokens)
    assert any("--strict" in tokens for tokens in invocations)


# spec: "The CLAUDE.md lines from R1.9 and R4.4 stay under the `claude-md-size` check's 200-line limit in `build/cc_guide/conformance.toml`."
# task: 8
def test_claude_md_stays_within_200_lines(repo):
    assert len((repo / "CLAUDE.md").read_text().splitlines()) <= 200


# spec: "`check_frontmatter.py` (exit 0; the only `WARN` is `writing-skills`' body length)"
# task: 6
def test_repository_default_frontmatter_gate(repo):
    result = subprocess.run(
        [sys.executable, str(repo / "build/check_frontmatter.py")],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    warnings = [
        line for line in result.stderr.splitlines()
        if re.search(r"\bWARN\b", line)
    ]
    assert len(warnings) == 1
    assert "writing-skills" in warnings[0]


@pytest.mark.parametrize(
    "guard",
    [
        "if __name__ == '__main__':\n    pass\n",
        'if __name__ == "__main__":\n    pass\n',
        "if '__main__' == __name__:\n    pass\n",
        "if (\n    __name__ == '__main__'\n):\n    pass\n",
    ],
)
# spec: "The runnable scripts are the `skills/*/scripts/*.py` files with a `__main__` guard."
# task: 10
def test_runnable_script_discovery(tmp_path, frontmatter, guard):
    skill, _ = _make_skill(tmp_path)
    runnable = _write_script(skill, "profile.py", guard)
    _write_script(skill, "time_series_cv.py", "def split():\n    pass\n")
    _write_script(
        skill, "comment.py", "# if __name__ == '__main__':\n"
    )
    _write_script(
        skill,
        "literal.py",
        'EXAMPLE = "if __name__ == \'__main__\':"\n',
    )
    _write_script(skill, "nested/profile.py", guard)
    assert set(frontmatter.runnable_scripts(skill)) == {runnable}


# spec: "There are 16."
# task: 10
def test_repository_runnable_inventory(repo, frontmatter):
    discovered = {
        path.relative_to(repo).as_posix()
        for skill in _skills(repo)
        for path in frontmatter.runnable_scripts(skill)
    }
    independently_discovered = {
        path.relative_to(repo).as_posix()
        for path in (repo / "skills").glob("*/scripts/*.py")
        if _has_main_guard(path.read_text())
    }
    assert discovered == independently_discovered == RUNNABLE_SCRIPTS


# spec: "`tune-hyperparameters/scripts/time_series_cv.py` has no `__main__` guard; it is a library imported into the user's code and stays header-less."
# task: 10
def test_time_series_cv_remains_a_library(repo, frontmatter):
    path = repo / "skills/tune-hyperparameters/scripts/time_series_cv.py"
    text = path.read_text()
    assert not _has_main_guard(text)
    assert frontmatter.script_metadata(text) is None
    assert path not in frontmatter.runnable_scripts(path.parent.parent)


@pytest.mark.parametrize(
    "text",
    [
        "if __name__ == '__main__':\n    pass\n",
        (
            "# /// script\n"
            "# dependencies = []\n"
            "# ///\n"
            "if __name__ == '__main__':\n    pass\n"
        ),
        (
            "# /// script\n"
            "# requires-python = '>=3.11'\n"
            "# ///\n"
            "if __name__ == '__main__':\n    pass\n"
        ),
        (
            "# /// script\n"
            "# requires-python = '>=3.11'\n"
            "# dependencies = [\n"
            "# ///\n"
            "if __name__ == '__main__':\n    pass\n"
        ),
    ],
)
# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_missing_or_malformed_script_metadata_is_rejected(
    tmp_path, frontmatter, text
):
    skill, _ = _make_skill(tmp_path)
    _write_script(skill, text=text)
    assert frontmatter.check_script_headers(skill)


# spec: "A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block that parses with `tomllib` and has `requires-python` and `dependencies`."
# task: 10
def test_valid_script_metadata_is_accepted(tmp_path, frontmatter):
    skill, _ = _make_skill(tmp_path)
    text = _script_text()
    _write_script(skill, text=text)
    assert frontmatter.script_metadata(text) == {
        "requires-python": ">=3.11",
        "dependencies": [],
    }
    assert frontmatter.check_script_headers(skill) == []


# spec: "Line 1 is `#!/usr/bin/env python3`; add it where missing."
# task: 10
def test_every_runnable_script_has_the_house_shebang(repo):
    for relative in RUNNABLE_SCRIPTS:
        assert (repo / relative).read_text().splitlines()[0] == (
            "#!/usr/bin/env python3"
        )


# spec: "Then a `# /// script` block with single-quoted TOML strings, a `requires-python`, and a `dependencies` list (`[]` for stdlib-only scripts)."
# task: 10
def test_repository_pep723_house_form(repo):
    for relative in RUNNABLE_SCRIPTS:
        text = (repo / relative).read_text()
        assert text.splitlines()[1:].copy()
        assert next(
            line for line in text.splitlines()[1:] if line.strip()
        ) == "# /// script"
        block = _metadata_block(text)
        metadata = tomllib.loads(block)
        assert re.search(
            r"(?m)^requires-python\s*=\s*'[^']+'\s*$", block
        ), relative
        assert isinstance(metadata["dependencies"], list), relative
        for dependency in metadata["dependencies"]:
            assert isinstance(dependency, str), relative
            assert f"'{dependency}'" in block, relative


# spec: "Use the lowest of `'>=3.11'`, `'>=3.12'`, `'>=3.13'` under which the test suite covering the script passes, run with `uv run --python 3.X` and that suite's CLAUDE.md dependencies."
# task: 10
def test_repository_python_floors_are_from_the_spec(repo, frontmatter):
    for relative in RUNNABLE_SCRIPTS:
        metadata = frontmatter.script_metadata((repo / relative).read_text())
        assert metadata["requires-python"] in {
            ">=3.11", ">=3.12", ">=3.13",
        }, relative


# spec: "Every third-party import, including function-level imports, is declared with a `>=` floor at the major version the suite currently resolves (e.g. `'polars>=1.0'`)."
# task: 10
def test_repository_dependencies_use_lower_bounds_without_upper_pins(
    repo, frontmatter
):
    requirement = re.compile(
        r"[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?"
        r"\s*>=\s*\d+(?:\.\d+)*"
    )
    for relative in RUNNABLE_SCRIPTS:
        metadata = frontmatter.script_metadata((repo / relative).read_text())
        for dependency in metadata["dependencies"]:
            assert requirement.fullmatch(dependency), (relative, dependency)


# spec: "stdlib is detected via `sys.stdlib_module_names`;"
# task: 10
def test_stdlib_imports_are_not_dependencies(frontmatter):
    source = "\n".join(
        f"import {name}"
        for name in sorted(sys.stdlib_module_names)
        if name.isidentifier()
    )
    assert frontmatter.required_imports(ast.parse(source), set()) == set()


# spec: "local means a sibling module file in the same directory;"
# task: 10
def test_sibling_imports_are_not_dependencies(frontmatter):
    tree = ast.parse(
        "import deferred_stats\n"
        "from deferred_stats import main\n"
    )
    assert frontmatter.required_imports(tree, {"deferred_stats"}) == set()
    assert frontmatter.required_imports(tree, set())


# spec: "import names map to distributions through a small alias table, e.g. `yaml` → `pyyaml`;"
# task: 10
def test_yaml_distribution_alias(tmp_path, frontmatter):
    assert frontmatter.IMPORT_DISTRIBUTIONS["yaml"] == "pyyaml"
    skill, _ = _make_skill(tmp_path)
    major = yaml.__version__.split(".")[0]
    _write_script(
        skill,
        text=_script_text(
            dependencies=[f"pyyaml>={major}.0"],
            body="import yaml",
        ),
    )
    assert frontmatter.check_script_headers(skill) == []


@pytest.mark.parametrize(
    "handler",
    [
        "ImportError",
        "ModuleNotFoundError",
        "(ImportError, ValueError)",
        "(ValueError, ModuleNotFoundError)",
    ],
)
# spec: "Imports inside a `try` whose handler catches `ImportError` or `ModuleNotFoundError` are optional and may be left undeclared."
# task: 10
def test_optional_import_exemption(tmp_path, frontmatter, handler):
    source = (
        "try:\n"
        "    import polars\n"
        f"except {handler}:\n"
        "    pass\n"
    )
    assert frontmatter.required_imports(ast.parse(source), set()) == set()
    skill, _ = _make_skill(tmp_path)
    _write_script(skill, text=_script_text(body=source))
    assert frontmatter.check_script_headers(skill) == []


@pytest.mark.parametrize(
    "source",
    [
        "import polars\n",
        "def main():\n    import polars\n",
        "try:\n    import polars\nexcept ValueError:\n    pass\n",
        (
            "try:\n    import polars\nexcept ImportError:\n    pass\n"
            "def main():\n    import polars\n"
        ),
    ],
)
# spec: "Every third-party import, including function-level imports, is declared with a `>=` floor at the major version the suite currently resolves (e.g. `'polars>=1.0'`)."
# task: 10
def test_required_imports_must_be_declared(
    tmp_path, frontmatter, source
):
    assert frontmatter.required_imports(ast.parse(source), set()) == {
        "polars",
    }
    skill, _ = _make_skill(tmp_path)
    script = _write_script(skill, text=_script_text(body=source))
    assert frontmatter.check_script_headers(skill)
    script.write_text(
        _script_text(dependencies=["polars>=1.0"], body=source)
    )
    assert frontmatter.check_script_headers(skill) == []


# spec: "In such a script, every non-stdlib, non-local import is declared in `dependencies`:"
# task: 10
def test_repository_script_headers_pass_import_lint(repo, frontmatter):
    for skill in _skills(repo):
        assert frontmatter.check_script_headers(skill) == [], skill


@pytest.mark.parametrize(
    "runner",
    ["python", "python3", "python \\\n", "python3 \\\n"],
)
@pytest.mark.parametrize("document", ["SKILL.md", "references/examples.md"])
# spec: "No skill markdown invokes a resolving bundled-script path with bare `python` or `python3`, including line-continued forms (`python \\` followed by the path on the next line)."
# task: 11
def test_bare_python_invocations_are_rejected(
    tmp_path, frontmatter, runner, document
):
    skill, data = _make_skill(tmp_path)
    _write_script(skill)
    invocation = f"{runner} <this-skill-dir>/scripts/profile.py\n"
    if document == "SKILL.md":
        _write_frontmatter(skill, data, invocation)
    else:
        path = skill / document
        path.parent.mkdir(parents=True)
        path.write_text(invocation)
    assert frontmatter.check_invocations(skill)


# spec: "A path that does not resolve to a bundled script, such as `writing-skills/anthropic-best-practices.md`'s teaching example `scripts/migrate.py`, is not flagged."
# task: 11
def test_unresolved_teaching_example_is_not_flagged(tmp_path, frontmatter):
    skill, _ = _make_skill(
        tmp_path, body="python scripts/migrate.py\n"
    )
    assert frontmatter.resolve_bundled_script(
        "scripts/migrate.py", skill
    ) is None
    assert frontmatter.check_invocations(skill) == []


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
def test_canonical_uv_invocation_is_accepted(tmp_path, frontmatter):
    skill, _ = _make_skill(
        tmp_path,
        body="uv run <this-skill-dir>/scripts/profile.py\n",
    )
    script = _write_script(skill)
    assert frontmatter.check_invocations(skill) == []
    invocations = frontmatter.bundled_invocations(skill)
    assert (
        skill / "SKILL.md",
        "uv run",
        "<this-skill-dir>/scripts/profile.py",
    ) in invocations
    assert frontmatter.resolve_bundled_script(
        "<this-skill-dir>/scripts/profile.py", skill
    ).resolve() == script.resolve()


# spec: "Path forms in use: `<this-skill-dir>/scripts/x.py`, `<this-skill-dir>/../<skill>/scripts/x.py`, `$LLM_WIKI_ROOT/scripts/x.py` (the installed copies), `~/Projects/agent-skills/skills/llm-wiki/scripts/x.py` (llm-wiki's INSTALL.md), and repo-relative `skills/<skill>/scripts/build.py`."
# task: 11
def test_all_documented_path_forms_resolve(
    tmp_path, repo, frontmatter, monkeypatch
):
    wiki = repo / "skills/llm-wiki"
    wiki_root = tmp_path / "wiki"
    installed = wiki_root / "scripts/lint_wiki.py"
    installed.parent.mkdir(parents=True)
    shutil.copyfile(wiki / "scripts/lint_wiki.py", installed)
    monkeypatch.setenv("LLM_WIKI_ROOT", str(wiki_root))

    task_home = tmp_path / "home"
    legacy = (
        task_home
        / "Projects/agent-skills/skills/llm-wiki/scripts/lint_wiki.py"
    )
    legacy.parent.mkdir(parents=True)
    shutil.copyfile(wiki / "scripts/lint_wiki.py", legacy)
    monkeypatch.setenv("HOME", str(task_home))

    cases = [
        (wiki, "<this-skill-dir>/scripts/lint_wiki.py"),
        (
            repo / "skills/finishing-a-development-branch",
            "<this-skill-dir>/../writing-plans/scripts/deferred_stats.py",
        ),
        (wiki, "$LLM_WIKI_ROOT/scripts/lint_wiki.py"),
        (
            wiki,
            "~/Projects/agent-skills/skills/llm-wiki/scripts/lint_wiki.py",
        ),
        (
            repo / "skills/classification-codes",
            "skills/classification-codes/scripts/build.py",
        ),
    ]
    for skill, path in cases:
        resolved = frontmatter.resolve_bundled_script(path, skill)
        assert resolved is not None, path
        assert resolved.is_file(), path
        assert _has_main_guard(resolved.read_text()), path


# spec: "Every documented invocation in `skills/**/*.md` of a path that resolves to one of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`, `python3`, `uv run --no-project --python 3.13 python`, and `uv run --python 3.13 --with … python`."
# task: 11
def test_repository_invocations_have_no_obsolete_runner_prefixes(
    repo, frontmatter
):
    path_pattern = (
        r"(?:<this-skill-dir>/|\$LLM_WIKI_ROOT/|"
        r"~/Projects/agent-skills/|skills/)"
        r"""[^\s`'"]+\.py"""
    )
    command = re.compile(
        r"\b(?P<runner>uv[ \t]+run|python3?)[ \t]+"
        r"(?P<between>[^`\n]*?)(?P<path>" + path_pattern + r")"
    )
    for skill in _skills(repo):
        assert frontmatter.check_invocations(skill) == [], skill
        for markdown in skill.rglob("*.md"):
            text = re.sub(r"\\\r?\n", " ", markdown.read_text())
            for match in command.finditer(text):
                path = match.group("path")
                resolved = frontmatter.resolve_bundled_script(path, skill)
                if resolved is None:
                    continue
                assert match.group("runner").split() == ["uv", "run"], (
                    markdown, match.group(0)
                )
                assert match.group("between").strip() in {"", "'", '"'}, (
                    markdown, match.group(0)
                )


# spec: "Each skill with such an invocation gets this sentence once, near its first invocation: \"Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.\""
# task: 11
def test_fallback_sentence_occurs_once_per_invoking_skill(
    repo, frontmatter
):
    for skill in _skills(repo):
        if frontmatter.bundled_invocations(skill):
            count = sum(
                markdown.read_text().count(FALLBACK)
                for markdown in skill.rglob("*.md")
            )
            assert count == 1, skill


@pytest.mark.parametrize(
    "compatibility, valid",
    [
        (ABSENT, False),
        ("Python 3.11+.", False),
        (_expected_compatibility((3, 11)), True),
    ],
)
# spec: "A skill whose markdown runs a bundled script via `uv run` declares a `compatibility` value containing `uv`."
# task: 12
def test_uv_invocation_requires_uv_compatibility(
    tmp_path, frontmatter, compatibility, valid
):
    changes = (
        {} if compatibility is ABSENT else {"compatibility": compatibility}
    )
    skill, data = _make_skill(
        tmp_path,
        changes=changes,
        body="uv run <this-skill-dir>/scripts/profile.py\n",
    )
    _write_script(skill)
    errors = frontmatter._check_compatibility_names_uv(skill, data)
    assert (errors == []) is valid, errors


# spec: "Here 3.X is the highest `requires-python` floor among the scripts that skill invokes."
# task: 12
def test_repository_compatibility_uses_highest_invoked_floor(
    repo, frontmatter
):
    for skill in _skills(repo):
        scripts = _invoked_scripts(frontmatter, skill)
        if scripts:
            floor = _highest_floor(frontmatter, scripts)
            assert _read_frontmatter(skill)["compatibility"] == (
                _expected_compatibility(floor)
            ), skill


# spec: "That set includes `finishing-a-development-branch`, which runs `writing-plans`' `deferred_stats.py`."
# task: 12
def test_finishing_includes_its_cross_skill_script(repo, frontmatter):
    skill = repo / "skills/finishing-a-development-branch"
    scripts = _invoked_scripts(frontmatter, skill)
    deferred = (
        repo / "skills/writing-plans/scripts/deferred_stats.py"
    ).resolve()
    assert deferred in scripts
    assert _read_frontmatter(skill)["compatibility"] == (
        _expected_compatibility(_highest_floor(frontmatter, scripts))
    )


# spec: "Prose floors that disagree with the header are aligned or removed (e.g. \"Python ≥ 3.9\" in `recommend-probabilistic-model` and `recommend-visualization`)."
# task: 12
def test_named_skills_have_no_conflicting_prose_floors(repo, frontmatter):
    pattern = re.compile(
        r"\bPython\s*(?:(?:≥|>=)\s*(3\.\d+)|(3\.\d+)\+)"
    )
    for name in (
        "recommend-probabilistic-model",
        "recommend-visualization",
    ):
        skill = repo / "skills" / name
        scripts = _invoked_scripts(frontmatter, skill)
        assert scripts, skill
        floor = ".".join(map(str, _highest_floor(frontmatter, scripts)))
        for first, second in pattern.findall(
            (skill / "SKILL.md").read_text()
        ):
            assert (first or second) == floor, skill


@pytest.fixture
def license_repository(tmp_path):
    skill, _ = _make_skill(tmp_path)
    texts = {
        "LICENSE": b"MIT\n",
        "LICENSE-superpowers": b"MIT\n\n",
    }
    for filename, text in texts.items():
        (tmp_path / filename).write_bytes(text)
        (skill / filename).write_bytes(text)
    return (
        tmp_path,
        skill,
        ["example"],
        {"LICENSE-superpowers": ("example",)},
    )


# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_correct_license_copies_are_accepted(
    license_repository, provenance
):
    root, _, skills, table = license_repository
    assert provenance.bundled_license_violations(root, skills, table) == []


@pytest.mark.parametrize("filename", ["LICENSE", "LICENSE-superpowers"])
@pytest.mark.parametrize(
    "damage", ["missing", "different_bytes", "symlink", "directory"]
)
# spec: "Every required copy exists, is a regular file, and is byte-identical to its root file."
# task: 8
def test_invalid_license_copies_are_rejected(
    license_repository, provenance, filename, damage
):
    root, skill, skills, table = license_repository
    copy = skill / filename
    copy.unlink()
    if damage == "different_bytes":
        copy.write_bytes((root / filename).read_bytes().replace(b"\n", b"\r\n"))
    elif damage == "symlink":
        copy.symlink_to(root / filename)
    elif damage == "directory":
        copy.mkdir()
    assert provenance.bundled_license_violations(root, skills, table)


# spec: "No skill directory holds a `LICENSE*` file outside its mapping."
# task: 8
def test_unmapped_skill_license_is_rejected(
    license_repository, provenance
):
    root, skill, skills, table = license_repository
    (skill / "LICENSE-unmapped").write_bytes(b"MIT\n")
    assert provenance.bundled_license_violations(root, skills, table)


@pytest.mark.parametrize("empty_mapping", [False, True])
# spec: "Every root `LICENSE*` file is mapped to at least one skill."
# task: 8
def test_unmapped_root_license_is_rejected(
    license_repository, provenance, empty_mapping
):
    root, _, skills, table = license_repository
    (root / "LICENSE-andorra").write_bytes(b"MIT\n")
    if empty_mapping:
        table["LICENSE-andorra"] = ()
    assert provenance.bundled_license_violations(root, skills, table)


# spec: "Each skill directory carries regular files (never symlinks, which `install.py --copy` refuses) that are byte-identical to the root license files and carry the same names:"
# task: 8
def test_repository_license_mapping_and_copies(repo, provenance):
    skills = _skills(repo)
    names = [skill.name for skill in skills]
    superpowers = {
        skill.name
        for skill in skills
        if _read_frontmatter(skill).get("metadata", {}).get("source")
        == SUPERPOWERS_SOURCE
    }
    assert len(superpowers) == 13

    expected = {
        "LICENSE-superpowers": superpowers,
        "LICENSE-coding-skills": {"bayesian-workflow", "clean-code"},
    }
    if (repo / "LICENSE-andorra").exists():
        expected["LICENSE-andorra"] = {"bayesian-workflow"}

    actual = {
        filename: set(mapped_skills)
        for filename, mapped_skills in provenance.BUNDLED_LICENSES.items()
    }
    assert provenance.PLAIN_LICENSE == "LICENSE"
    assert actual == expected
    assert {
        path.name for path in repo.glob("LICENSE*")
    } == {"LICENSE", *expected}

    for skill in skills:
        required = {"LICENSE"} | {
            filename
            for filename, mapped_skills in expected.items()
            if skill.name in mapped_skills
        }
        assert {path.name for path in skill.glob("LICENSE*")} == required, skill
        for filename in required:
            copy = skill / filename
            assert copy.is_file() and not copy.is_symlink(), copy
            assert copy.read_bytes() == (repo / filename).read_bytes(), copy

    assert provenance.bundled_license_violations(
        repo, names, provenance.BUNDLED_LICENSES
    ) == []


# spec: "The script stays stdlib-only, so its CLAUDE.md command keeps no `--with`."
# task: 8
def test_provenance_has_only_stdlib_imports_and_no_with_command(repo):
    tree = ast.parse((repo / "build/check_provenance.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            modules = [node.module.split(".")[0]]
        else:
            continue
        assert set(modules) <= sys.stdlib_module_names, modules

    commands = _section((repo / "CLAUDE.md").read_text(), "Commands")
    found = False
    for line in re.sub(r"\\\r?\n", " ", commands).splitlines():
        tokens = shlex.split(line, comments=True)
        if any(token.endswith("check_provenance.py") for token in tokens):
            found = True
            assert not any(
                token == "--with" or token.startswith("--with=")
                for token in tokens
            )
    assert found


# spec: "R2.2's red-baseline file exists, and `writing-skills` changed only as R2.3's outcome branch allows."
# task: 2
def test_description_openings_baseline_file_exists(repo):
    records = list(
        (repo / "specs").glob("red-baseline-description-openings-*.md")
    )
    assert records
    for record in records:
        run_date = record.stem.removeprefix(
            "red-baseline-description-openings-"
        )
        assert date.fromisoformat(run_date).isoformat() == run_date
        assert record.read_text().strip()


# spec: "The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list)."
# task: 14
def test_token_efficiency_note_records_measurement_and_command(repo):
    text = (repo / "skills/writing-skills/SKILL.md").read_text()
    section = _section(text, "Token Efficiency")
    assert re.search(r"156\s*[–-]\s*164", section)
    assert re.search(r"\b93\b", section)
    assert re.search(r"\b0\.154(?:\.0)?\b", section)
    assert "2026-10-03" in section
    assert "codex debug prompt-input" in section
</tests>
<flags>
<flag task="7"><spec>The module docstring describes the new rules and the `--strict` flag, and CLAUDE.md's Commands section gains the `--strict` invocation with one line on when to use it (preparing a claude.ai upload or a spec-only validator run), under the `claude-md-size` check's 200-line limit (Sequencing, "Conformance register").</spec><plan>Modify: `CLAUDE.md` (Commands: the frontmatter lint's comment names `--strict`; no line added, D7)</plan></flag>
<flag task="8"><spec>No skill directory holds a `LICENSE*` file outside its mapping.</spec><plan>Rename: `skills/recommend-causal-design/LICENSE` to `skills/recommend-causal-design/LICENSE-causal-design-sources`, and re-point its links in that skill's `SKILL.md`, `README.md` and `references/sources.md`</plan></flag>
<flag task="10"><spec>Fourteen gain a header:</spec><plan>Modify: the 15 header-less runnable scripts (helper script): a shebang where missing, then the header</plan></flag>
</flags>
<untestable>
The owner approved the design on 2026-10-03 and the written spec on 2026-10-18.
The owner approved all five design sections in a brainstorming pass over `specs/completed/agent-skills-best-practices.md` (a September 2026 survey of Agent Skills portability across Claude Code, Codex, Gemini CLI, Cursor, Copilot, and others).
This document is the handoff for implementation planning.
One piece has landed since: a 2026-10-15 quick fix made `build/check_frontmatter.py` accept `compatibility`, and R1.3's check of its value is still to do.
The survey is this spec's input; it was retired ahead of the spec, to `specs/completed/` in `79ad04f` (2026-10-03).
Measured at this one skill count only.
That the cutoff moves with the number of skills sharing the budget is an inference from Codex's documented budget, not a measurement
Moving it to `.agents/skills/` has a large blast radius (installer, tests, CLAUDE.md, symlinks) and buys nothing: the installer already links into every runtime's discovery path, which is the survey's own alternative.
The skills already load user-level from the same checkout; a project-level link would list each one twice.
`disable-model-invocation: true` removes a skill from the model's reach, which would break bare-name handoffs (`finishing-a-development-branch`, `using-git-worktrees`, and the others are invoked by name from other skills).
Their side effects are already gated in their bodies, the survey's portable pattern.
`writing-skills`, the governing meta-skill, requires trigger-only descriptions on tested evidence that a workflow summary in the description lets agents skip the body.
"Use when" already front-loads the trigger.
**No description rewrites in this spec.**
R2.1's review found none needed, and no trigger evals exist to catch a regression.
The one exception is the angle-bracket fix (R1.5), which is wording-equivalent.
Both measured non-Claude runtimes load skills with host keys; strictness matters only for claude.ai uploads and `skills-ref`-style validators (R1.8).
The survey's 1,536-character truncation, Codex's 2% / 8,000-character budget, and Claude Code's listing fraction stay out of the lint; it keeps the spec's 1,024 cap.
Claude Code listing behavior is documented in `specs/guides/claude-code-customization-guide.md`.
A plain `#!/usr/bin/env python3` shebang keeps the script runnable by bare `python3` where uv is absent; `uv run <path>` reads the header either way.
The two existing `build.py` headers are the template.
No single work venv pairs NumPyro with ArviZ, so the project interpreter can lack the imports these scripts need, and work repos that install `hooks/uv-guard.sh` deny bare `python …` anyway.
No skill trips this today; it exists so that the first manual-only skill cannot auto-fire in Codex.
Today only `writing-skills` warns; splitting it is deferred.
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
The note covers three points: Codex shortens every description when its listing exceeds its budget; the measured cut (156–164 characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure (`codex debug prompt-input` from a directory outside any repo, reading the Skills list).
No new rule.
**Baseline ≤ 3/5:** also add one checklist line ("the primary trigger falls within the first ~150 characters") and GREEN-test it: 5 reps with the new wording, at least 4/5 passing, recorded in the same red-baseline file.
The two `build.py` scripts (`classification-codes`, `geographic-codes`) already conform.
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
No ceiling remains to raise: a change whose lines would breach the limit trims CLAUDE.md elsewhere (R6 P1, whose ceiling option drift spec R12.7 removed).
When Stage A or Stage D fixes a gap the register tracks to it, the same change removes or narrows that `[[exception]]` and runs `build/check_conformance.py` (R6 P2).
The plan edits skills the executing session loads (`writing-plans`, `finishing-a-development-branch`, `writing-skills`), and `~/.claude/skills` resolves to the main checkout.
Commit from the worktree; the shared checkout's branch can change under a concurrent session.
**Stage D's micro-test** runs from a session whose cwd was never this repo; inherited session context voids reps otherwise.
**State test changes as +N deltas** against the suite, never absolute totals.
**Before allocating the plan id**, check `specs/plans/` on every branch (`git ls-tree`); ids are allocated per branch and have collided.
`specs/jax-deep-learning-skills.md` is being implemented on `codex/jax-deep-learning-skills` and defines three skills (`skills/deep-learning` is on that branch as of 2026-10-03).
R1.4's required `license`, R3's header and invocation rules, and R4's per-skill license copies apply to them too.
Whichever branch merges second brings the other's skills into conformance in the same merge, or the new lints fail on arrival.
Every gate in CLAUDE.md's Commands passes:
Each new lint rule has a test that failed before its implementation and passes after.
R3.8's execution proof is recorded for all 16 scripts.
**Cross-runtime load check**, from a directory outside any repo:
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