# Portability, Lints and Skill Checks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close six deferred items from plans 53 and 58: the frontmatter and provenance review Minors, the lint's widening to `.claude/`, Codex adapters for the three commands, a table-of-contents lint for long `references/` files, a skill security scan, and a first trigger-eval suite.

**Architecture:** Three groups share `build/check_frontmatter.py` and run in a fixed order: the Minors (Tasks 1-3), then a skill-profile mechanism that widens the scan to `.claude/` (Task 4), then the Codex command adapters, which add a third profile (Tasks 5-6). The table-of-contents lint (Tasks 7-8) and the scanner (Tasks 9-10) are separate build tools. The trigger-eval suite (Tasks 11-13) is a kit under `specs/baseline/` copied from plan 111's trigger lane.

**Tech Stack:** Python 3.13 (dev Python, `build/versions.toml`), PyYAML, pytest, uv, bash, GitHub Actions; Cisco `skill-scanner` 2.3.2 (Task 9 onward, after the owner's download gate).

**Spec:** none. The six items in `specs/deferred_items.md` are the requirements: section `## 53-agent-skills-portability — 2026-10-20` items "Trigger-eval suites", "Codex adapters for `/deferred`, `/fix-issue` and `/license-audit`", "Tables of contents for long `references/` files", "Skill security scanning" (with its 2026-11-17 owner ruling) and "Review Minors from plan 53's task reviews and final review, unfixed"; section `## 58-claude-code-drift-automation — 2026-10-20` item "Widening `build/check_frontmatter.py` to `.claude/skills` and `.claude/agents`". Base: `8131b81`.

## Global Constraints

- Single quotes, f-strings, 4-space indentation in `build/*.py` (the existing files use 4 spaces; `build/sync_runtime_assets.py` and `install.py` use 2 — keep each file's own indentation).
- Never hand-edit `runtimes/`. Regenerate with `uv run --with pyyaml python build/sync_runtime_assets.py` and check with `--check`.
- Generated adapters translate the manifest layer only. A command body is copied unchanged; only the frontmatter and the appended invocation paragraph differ per runtime.
- Tests are directory-scoped. Run build tests from `build/`: `cd build && uv run --with pytest --with pyyaml python -m pytest -q <file>`.
- Every commit passes `bash build/run_commit_lints.sh`.
- Plans state test-count deltas (`+N`), never absolute pytest totals.
- No download, install or clone of the scanner before the owner's go-ahead at Task 9 Step 1 (owner ruling 2026-11-17).
- Model spend for Tasks 12-13 stays under the caps those tasks name; each rep runs under `skills/writing-skills/references/micro-tests.md` isolation, with the flags plan 111's kit uses.
- A trigger rep that loads the skill before its first void event counts as a load (owner ruling 2026-11-28, `specs/baseline/red-baseline-codes-description.md`, VOID rule).
- Leave "Distribution channels" (same deferred section) alone.

## Review Focus

1. **A Codex user runs `$fix-issue 123`.** The adapter must tell the model to take the argument after `$fix-issue`, and must never say `/fix-issue`, which Codex does not have. Pinned in Task 5 (`test_codex_command_skill_names_the_dollar_form`).
2. **A command is renamed or removed.** `sync_runtime_assets.py` must remove the old `runtimes/codex/skills/<old>/` folder whole, the nested `agents/openai.yaml` included, so no orphan skill installs. Pinned in Task 5 (`test_write_removes_a_stale_codex_command_skill_folder`).
3. **A `references/` file has `## ` lines inside a fenced code block** (shell comments, Markdown templates). The TOC lint must not count them as headings, and `--write` must not list them. Pinned in Task 7 (`test_headings_inside_fences_are_not_counted`).
4. **`--write` runs twice, or on a file with a banner or intro under the H1.** The second run changes nothing, and the block lands just before the first `## ` heading, so the banner stays first. Pinned in Task 7 (`test_write_is_idempotent_and_keeps_the_intro`).
5. **A `.claude/skills/<dir>` without a `SKILL.md`** (a scratch folder, or a dir mid-edit). The widened lint skips it and does not crash. Pinned in Task 4 (`test_a_project_skill_dir_without_skill_md_is_skipped`).

## Decisions

- **D1** (owner, brief, 2026-11-28): one plan, named for its theme (portability, lints and skill checks), takes all six items, items 1, 3 and 6 included ("Include as many items as possible in each."). An item that needs the owner's design call goes to plan review as a question. Applied in: Goal, Tasks 1-13.
- **D2** (owner, plan review, 2026-11-28): every default in Q1-Q10 below is approved ("Approve all defaults"). Under Q3's default, approving the plan does not approve the scanner download: Task 9 Step 1 still stops for its own go-ahead. Applied in: Tasks 1-13.

## Plan-review questions

The owner approved every default below at plan review (D2). Each line keeps its question so an executor can see what was decided.

- **Q1 (item 1, trigger-eval design).** Approved default skill set: the eight data-and-modeling skills whose descriptions route to one another — `explore-data`, `validate-data`, `develop-testing-strategy`, `recommend-probabilistic-model`, `bayesian-workflow`, `recommend-causal-design`, `track-model-experiments`, `tune-hyperparameters` (explore-data names four of the others as its downstream, recommend-probabilistic-model sends causal questions to recommend-causal-design, tune-hyperparameters sends revision leakage to develop-testing-strategy, and track-model-experiments excludes tune-hyperparameters by name). 20 queries each: 12 should-load and 8 near-miss negatives, where each negative is a should-load query of a named sibling or of a skill outside the set. Split per skill 14 train / 6 validation, stratified 8+6 / 4+2, fixed by a committed seed. Default baseline run (Task 13): all 160 queries, 1 rep each on Sonnet and Opus (320 reps), cap $60 (plan 111 spent about $0.14 a rep). Alternatives: build the suite only (Tasks 11-12, the item's done-when), or a smaller set.
- **Q2 (item 3, detector rule).** Default: a Markdown file under `skills/*/references/` (recursive, so `recommend-probabilistic-model/references/families/` counts) longer than 100 lines with 2 or more `## ` headings outside fences needs a `## Contents` section as its first `## ` heading, whose `- ` bullets equal the other `## ` headings, in order, text for text. 100 lines is the threshold Anthropic's guidance gives (`specs/completed/agent-skills-best-practices.md:53`). At `8131b81` about 60 files pass 100 lines; 14 have a `## Contents`; 12 of those match exactly and 2 have drifted (`bayesian-workflow/references/reporting.md`, `state-space.md`). The lint gets a `--write` mode that writes or refreshes the block in the existing bullet form. The two drifted files show that exact match is the "reliable detector" a crude grep was not.
- **Q3 (item 4, scanner and download gate).** Default scanner: Cisco AI Defense `skill-scanner` 2.3.2, released 2026-10-26, PyPI `cisco-ai-skill-scanner`, Apache-2.0, source https://github.com/cisco-ai-defense/skill-scanner, Python `>=3.11,<3.15`. Run: `skill-scanner scan-all skills --recursive --policy balanced --format summary --fail-on-severity high`, static analyzers only (offline, no API key, so no skill text leaves the machine). Where: a wrapper `build/skill_scan.sh` with one pin, run by a new advisory workflow `.github/workflows/skill-scan.yml`, not by `run_commit_lints.sh`, so no commit and no `test_commit_lints.py` clone downloads it. Not in `build/versions.toml`: `bump` re-pins all `[packages]` in one joint resolve, and the scanner's tree (litellm) would join the JAX and NumPyro resolve; the cost is that the weekly version drift does not watch the scanner, and the owner bumps it by hand. Not Cisco's reusable workflow: it is pinned by tag, needs `security-events: write`, and uploads SARIF. Facts to weigh: it depends on litellm (2.3.1 excluded a hijacked litellm 1.107.0); the project says its static rules alone catch about 8% of held-out malicious skills; nothing is vendored, so `NOTICE` needs no entry. Question: does approving this plan approve the download? Default: no — Task 9 Step 1 stops for a separate go-ahead, and only Tasks 9-10 wait.
- **Q4 (item 2, register rewrite).** The deviation `commands-stay-command-files` (`build/cc_guide/conformance.toml:747-756`) says Codex gets none of the three commands. Task 6 replaces its `reason` and `revisit` with the text in Task 6 Step 5. Approve that wording.
- **Q5 (item 2, `fix-issue`'s angle brackets).** `commands/fix-issue.md`'s description ends `Usage — /fix-issue <number|url>`, which `_check_value_shapes` rejects. The `<`/`>` rule is Anthropic's (claude.ai uploads, `specs/completed/agent-skills-best-practices.md:53`), not a Codex rule. Default: the adapter profile skips the angle-bracket check, and the canonical description stays. Alternative: reword the canonical description (`Usage — /fix-issue followed by an issue number or URL`), which changes Claude Code and agy too.
- **Q6 (item 6, project-local profile).** Default: `.claude/skills/*/SKILL.md` gets every skill check except `license` and Codex parity (these skills are Claude-only and never install), and `argument-hint` joins `HOST_KEYS` (a Claude Code skill key, which `cc-guide` uses). `.claude/agents/*.md` gets `check_agent_file`. The two roster checks stay on `agents/`: `cc-guide-verifier` pins `model: sonnet` and is not in `PINNED_AGENTS`, and `/cc-guide` names the model in its dispatch, so adding a project-local name to an installed hook's roster would be wrong.
- **Q7 (item 5, point (d)).** Task 1 closes the two small blind spots (`./scripts/` and `${LLM_WIKI_ROOT}`). No skill uses any of the four forms today. Default: the owner rules that `../scripts/` and a flag between the runner and the path stay open, as the item's done-when allows; Task 1 updates the comment above `RUNNER_RE` to name only those two.

- **Q8 (item 2, adapter location).** Default: `build/sync_runtime_assets.py` generates `runtimes/codex/skills/<command>/SKILL.md` and `agents/openai.yaml`, and `install.py` links them into `~/.agents/skills/`, as it links `runtimes/gemini/skills/` for agy. That turns on the existing `command:deferred` entries in `install.py`'s `DEPENDENCIES` for Codex. A hand-written adapter would drift from its command, and `--check` could not catch it.
- **Q9 (task order).** Default: Tasks 1-10 run in order. Tasks 1, 4 and 5 edit `build/check_frontmatter.py` (the Minors first, then the profiles, then the adapter profile). Tasks 6-10 share `CLAUDE.md`, `build/CLAUDE.md` and `build/test_commit_lints.py`. Tasks 11-13 touch none of those files and may run beside them. Tasks 9-10 wait on the download gate without blocking the rest.

- **Q10 (plan id and overlaps).** `entry_check.py` reported id 116 taken by three planning branches and 117 by a fourth, so this plan took 118. It also shares `CLAUDE.md`, `NOTICE`, `build/CLAUDE.md`, `build/cc_guide/conformance.toml` and `build/run_commit_lints.sh` with `116-sdd-and-reviewer-text-followups.md`, and `README.md` with `117-executing-plans-gates-and-tests.md`. Default: the executor merges `main` before Tasks 3, 6, 8 and 9 and re-reads those files' line numbers. The id collisions among the other three plans are theirs to settle.

## Notes from planning

- Every Minor, (a) to (m), still holds at `8131b81` (checked 2026-11-28; the `570afd2..8131b81` diff of `build/check_frontmatter.py` touched none of them). Two are wider than recorded: (b) — no read in the file catches `UnicodeDecodeError`, the SKILL.md reads included (lines 230, 249, 300, 340, 350, 387, 438, 464); (l) — four general paragraphs, not two, now sit between "by skill:" and the first entry.
- `check_skill` on a generated command skill fails three ways (trial run 2026-11-28 on `runtimes/gemini/skills/`): no `license`; bundled-path errors, because a command body names other skills' `references/` and `scripts/` paths; and `fix-issue`'s `<`/`>`. So the Codex adapters get their own profile (Task 5), and the Gemini adapters stay unscanned.
- `NOTICE` lines 23-29 already cover every file under `runtimes/` as a generated adapter that inherits its source's license, so the Codex skills need no `NOTICE` change. They carry `license: MIT` and no `LICENSE` copy, as the Gemini adapters do.

---

### Task 1: Frontmatter lint Minors (a)-(i)

**Files:**
- Modify: `build/check_frontmatter.py` (`_check_value_shapes` :195-210, `_check_invocation_parity` :213-244, `_catches_import_error` and its walker :262-290, `RUNNER_RE` comment :86-90, `PATH_ALIASES`, `resolve_bundled_script` :337, `bundled_invocations` :345-360, `check_invocations` :362-380, `_check_compatibility_names_uv`, `check_skill` :384, `_parse_frontmatter` :464)
- Test: `build/test_check_frontmatter.py`

**Interfaces:**
- Produces: `read_utf8(path: Path) -> tuple[str | None, list[str]]` — the text, or `None` and one error `f'{path}: is not valid UTF-8 (UnicodeDecodeError)'`. `bundled_invocations(skill_dir: Path) -> list[tuple[Path, str, str, Path | None]]` — `(md, runner, raw_path, resolved_script)`; `check_invocations(skill_dir, invocations)` and `_check_compatibility_names_uv(skill_dir, fm, invocations)` take the list `check_skill` computes once.

- [ ] **Step 1: Write the failing tests**

```python
def test_a_null_metadata_is_reported(tmp_path):      # (a)
    d = make_skill(tmp_path, extra='metadata:\n')
    assert check_skill(d) == [f"{d/'SKILL.md'}: metadata is null; remove the key or map strings to strings"]

@pytest.mark.parametrize('target', ['SKILL.md', 'agents/openai.yaml'])
def test_a_non_utf8_file_is_reported_not_raised(tmp_path, target):   # (b)
    # write b'\xff\xfe' to target; check_skill returns exactly one error ending '(UnicodeDecodeError)'

@pytest.mark.parametrize('handler', ['except:', 'except Exception:', 'except* ImportError:'])
def test_a_broad_except_makes_an_import_optional(handler):   # (c)
    assert required_imports(f'try:\n    import yaml\n{handler}\n    pass\n') == set()

@pytest.mark.parametrize('form', ['./scripts/tool.py', '${LLM_WIKI_ROOT}/scripts/lint.py'])
def test_closed_blind_spots_are_seen(tmp_path, form):   # (d)
    # a skill whose SKILL.md says `uv run <form>`; the resolved path is in bundled_invocations(d)

def test_a_hidden_directory_is_not_scanned(tmp_path):   # (e)
    # md at scripts/.pytest_cache/README.md runs `python scripts/tool.py`; bundled_invocations(d) == []

def test_a_skill_under_a_dot_folder_is_still_scanned(tmp_path):   # (e) guard
    # skill dir at tmp_path/'.claude'/'skills'/'x' whose SKILL.md runs `python scripts/tool.py`: one invocation reported

def test_a_module_not_found_guard_makes_an_import_optional():   # (f)
def test_a_relative_import_is_not_third_party():   # (f): 'from .pkg import y' with no pkg.py sibling → set()
```

(h): in `test_paths_resolve_across_skills_aliases_and_references`, replace `assert other.is_dir() and wiki.is_dir()` with `resolve_bundled_script(...) == other / 'scripts' / 'tool.py'` and the same for the llm-wiki path. (i): in the `--strict` subprocess test, derive `expected = [e for d in real_skills for e in strict_violations(d)]` and assert `strict.returncode == (1 if expected else 0)` and that each expected line is in stdout. (g): sort the `from check_frontmatter import (...)` list alphabetically, constants last (the repo has no isort config; this is the convention the review asked for). Unpack the 4-tuples at the existing `bundled_invocations` call sites (test lines 445, 451, 457, 478).

- [ ] **Step 2: Run to verify the new tests fail**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`
Expected: the new tests FAIL, except the dot-folder guard, which passes today; (b) with a `UnicodeDecodeError` traceback.

- [ ] **Step 3: Implement**

(a) `metadata` present with value `None` gets the message above; split the existing 105-character `append` over two string literals, message unchanged. (b) Every read site listed in the Notes calls `read_utf8`. (c) A bare handler, `Exception` or `BaseException` counts as catching `ImportError`, and the walker visits `(ast.Try, ast.TryStar)`. (d) An owner of `.` resolves as `THIS_SKILL`; `PATH_ALIASES` gains `${LLM_WIKI_ROOT}`; the comment above `RUNNER_RE` names only the two forms left open (Q7, approved). (e) `bundled_invocations` returns the 4-tuple, skips a file when any part of `md.relative_to(skill_dir).parts` starts with `.` (never the absolute path: this worktree and `.claude/skills/` sit under dot folders), and runs once per skill in `check_skill`.

- [ ] **Step 4: Run to verify they pass**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py && cd .. && uv run --with pyyaml python build/check_frontmatter.py`
Expected: all pass (+12 test items); the lint prints nothing and exits 0.

- [ ] **Step 5: Commit**

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py
git commit -m "fix(build): close plan 53's frontmatter lint Minors (a)-(i)"
```

### Task 2: Provenance lint Minors (j) and (k)

**Files:**
- Modify: `build/check_provenance.py:70-85` (the `BUNDLED_LICENSES` copy check), `:185-195` (`main`)
- Test: `build/test_check_provenance.py`

- [ ] **Step 1: Write the failing test**

`test_bundled_licenses_report_a_copy_of_a_name_that_is_no_root_file`: a fixture repo whose table is `{'LICENSE-gone': ('own',)}`, with `skills/own/LICENSE-gone` present and no root `LICENSE-gone`. Expected errors, exactly: `BUNDLED_LICENSES: LICENSE-gone is not a root license file` and `skills/own/LICENSE-gone: copies LICENSE-gone, which is not a root license file`. Today the second line wrongly says "not mapped to own".

- [ ] **Step 2: Run to verify it fails**

Run: `cd build && uv run --with pytest python -m pytest -q test_check_provenance.py -k no_root_file`
Expected: FAIL on the second line's wording.

- [ ] **Step 3: Implement** the reworded error for a mapped name with no root file, and bind `skills = skill_dirs()` once in `main` (k; `test_real_repo_is_clean` covers it).

- [ ] **Step 4: Run** `cd build && uv run --with pytest python -m pytest -q test_check_provenance.py && cd .. && uv run python build/check_provenance.py` — Expected: pass (+1), lint clean.

- [ ] **Step 5: Commit** — `git commit -m "fix(build): close plan 53's provenance lint Minors (j) and (k)"`

### Task 3: NOTICE Minors (l) and (m)

**Files:**
- Modify: `NOTICE:5`, `:42-43`, `:688-696` (no skill carries a copy of `NOTICE`)

- [ ] **Step 1:** (l) End line 5 at `one directory per skill.` Insert `Attribution and licensing, by skill:` and a blank line just before the first per-skill entry (`bayesian-workflow/`, line 43). (m) In the bullet at lines 688-696, move the sentence `Both SKILL.md files also gained a `compatibility` field naming uv (R3.6).` to directly after `(..., R3.5).`, and re-wrap at the file's width, so the bullet ends on its attribution sentence. Change no other words.
- [ ] **Step 2: Verify** — `git diff --word-diff NOTICE` shows only moved text; `uv run python build/check_provenance.py` exits 0.
- [ ] **Step 3: Commit** — `git commit -m "docs(notice): put the by-skill lead-in before the skill entries"`

### Task 4: Skill profiles; widen the lint to `.claude/`

**Files:**
- Modify: `build/check_frontmatter.py` (`HOST_KEYS` :61, `check_skill` :384, `main` :608-636, module docstring)
- Test: `build/test_check_frontmatter.py`

**Interfaces:**
- Produces: `@dataclass(frozen=True) class SkillProfile: license: bool; codex_parity: bool; bundled_paths: bool; angle_brackets: bool` with constants `SHIPPED = SkillProfile(True, True, True, True)` and `PROJECT_LOCAL = SkillProfile(False, False, True, True)`; `check_skill(skill_dir: Path, profile: SkillProfile = SHIPPED) -> list[str]`; `project_skill_dirs(root: Path) -> list[Path]` (dirs under `root/.claude/skills` holding a `SKILL.md`). `bundled_paths` gates the link and backticked-path scan, `check_script_headers`, `check_invocations` and the uv-compatibility rule. Task 5 adds a third constant.

- [ ] **Step 1: Write the failing tests**

`test_project_profile_skips_license_and_parity` (a skill with `disable-model-invocation: true`, no `license`, no `agents/openai.yaml`, and `argument-hint`: `check_skill(d, PROJECT_LOCAL) == []`, and `check_skill(d)` still reports license and parity). `test_project_profile_still_checks_name_and_paths` (a name mismatch and a missing `references/x.md` are both reported under `PROJECT_LOCAL`). `test_a_project_skill_dir_without_skill_md_is_skipped` (Review Focus 5: `project_skill_dirs` omits it). `test_main_scans_project_skills_and_agents` (monkeypatch `REPO` to a tree with a bad `.claude/skills/x/SKILL.md` name and a `.claude/agents/y.md` with unknown tools; `main([])` returns 1 and prints both).

- [ ] **Step 2: Run to verify they fail**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py -k "project or main_scans"`
Expected: FAIL (`SkillProfile` not defined).

- [ ] **Step 3: Implement** the profile, `argument-hint` in `HOST_KEYS`, and in `main`: `check_skill(d, PROJECT_LOCAL)` for each `project_skill_dirs(REPO)`, `check_agent_file` for each `.claude/agents/*.md`. The roster checks keep `agents/` (Q6). `--strict` and the body warning stay on `skills/` only. Update the docstring's opening to name the three scanned trees.

- [ ] **Step 4: Run** the suite, then `uv run --with pyyaml python build/check_frontmatter.py` on the real repo — Expected: all pass (+4); the lint exits 0 with `.claude/skills/cc-guide` and `.claude/agents/cc-guide-verifier.md` now in scope (`test_main_scans_project_skills_and_agents` proves the scan reaches them).

- [ ] **Step 5: Commit** — `git commit -m "feat(build): lint project-local skills and agents under .claude/"`

### Task 5: Generate Codex command skills

**Files:**
- Modify: `build/sync_runtime_assets.py` (constants :40-71, new renderers beside `render_gemini_command_skill` :167, `expected_assets` :181, `GENERATED_DIRS`)
- Modify: `build/check_frontmatter.py` (profile constant, `main`)
- Create (generated): `runtimes/codex/skills/{deferred,fix-issue,license-audit}/SKILL.md` and `.../agents/openai.yaml`
- Test: `build/test_runtime_support.py`, `build/test_check_frontmatter.py`

**Interfaces:**
- Consumes: `SkillProfile`, `check_skill(skill_dir, profile)` from Task 4.
- Produces: `CODEX_SKILLS = REPO / 'runtimes' / 'codex' / 'skills'` (in `GENERATED_DIRS`); `render_codex_command_skill(path: Path) -> str`; `render_codex_policy() -> str`; in `check_frontmatter.py`, `CODEX_ADAPTER = SkillProfile(license=True, codex_parity=True, bundled_paths=False, angle_brackets=False)` (Q5, approved) and `main` checks each `runtimes/codex/skills/*` with it.

- [ ] **Step 1: Write the failing tests** (in `test_runtime_support.py` unless noted)

- `test_codex_command_skill_keeps_manual_only_and_license`: for each `commands/*.md`, the rendered frontmatter is exactly `{'name': stem, 'description': ..., 'license': 'MIT', 'disable-model-invocation': True}`, and the body before the appended paragraph equals the canonical body.
- `test_codex_command_skill_names_the_dollar_form` (Review Focus 1): for `fix-issue`, the description contains `$fix-issue` and not `/fix-issue`, and the appended paragraph contains `` `$fix-issue` `` and `/skills` and does not contain `` `/fix-issue` ``.
- `test_codex_command_policy_forbids_implicit_invocation`: `yaml.safe_load(render_codex_policy()) == {'policy': {'allow_implicit_invocation': False}}` and the text starts with `GENERATED_COMMENT`.
- `test_codex_command_skill_refuses_a_model_invocable_command`: a source without `disable-model-invocation: true` raises `ValueError`.
- `test_write_removes_a_stale_codex_command_skill_folder` (Review Focus 2): with `CODEX_SKILLS` monkeypatched to `tmp_path`, an `old/SKILL.md` and `old/agents/openai.yaml` are removed and `old/` is gone after `write(...)`.
- In `test_check_frontmatter.py`, `test_codex_adapter_profile_passes_the_generated_skills`: `check_skill(d, CODEX_ADAPTER) == []` for each of the three, and removing `agents/openai.yaml` makes the parity error appear.

- [ ] **Step 2: Run to verify they fail** — `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py test_check_frontmatter.py -k "codex_command or codex_adapter"` — Expected: FAIL (names not defined).

- [ ] **Step 3: Implement.** The description replaces the command's own `/<stem>` token (not other slash tokens) with `$<stem>`. The appended paragraph is exact copy:

```python
CODEX_USER_ONLY_COMMAND = (
  "Run this only when the user's message invokes `${name}` or picks this skill from "
  "`/skills`, and take the argument from the text after `${name}`. If this skill "
  'loaded any other way, do not run it: tell the user it runs on `${name}`, and stop.'
)
```

`GENERATED_COMMENT` opens the YAML block, as in the Gemini skill. `remove_empty_folders` must climb out of `<cmd>/agents/` too. Update the module docstring, which says only agy gets command skills. No command body uses `$ARGUMENTS` or `$1` (checked at `8131b81`), so the body needs no translation.

- [ ] **Step 4: Regenerate and verify**

Run: `uv run --with pyyaml python build/sync_runtime_assets.py && uv run --with pyyaml python build/sync_runtime_assets.py --check && uv run --with pyyaml python build/check_frontmatter.py && cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py test_check_frontmatter.py`
Expected: six `wrote runtimes/codex/skills/...` lines, `--check` silent, lint exit 0, tests pass (+6).

- [ ] **Step 5: Commit** — `git add build/ runtimes/codex/skills && git commit -m "feat(runtimes): generate manual-only Codex skills for the three commands"`

### Task 6: Install the Codex command skills; update the record

**Files:**
- Modify: `install.py:250-254`, `build/test_runtime_support.py:389-393` (and `:241-246` if it asserts no Codex commands), `build/cc_guide/conformance.toml:747-756`, `CLAUDE.md:21`, `README.md:159-160`, `specs/guides/codex-customization-guide.md:658`

- [ ] **Step 1: Write the failing test.** Change the Codex `derive-roadmap` case at `test_runtime_support.py:389-393` to expect `.agents/skills/deferred` beside the two skills, with the comment `# Codex installs the generated command skills, so /deferred's dependency holds.` Add `test_codex_install_links_command_skills`: `run_install(tmp_path, 'codex', '--companions')` links `.agents/skills/{deferred,fix-issue,license-audit}` to `runtimes/codex/skills/<name>`.
- [ ] **Step 2: Run** `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py` — Expected: the two FAIL.
- [ ] **Step 3: Implement** `command_items = folder_items(runtimes / 'codex' / 'skills', skill_root)` for Codex, as for Gemini. Then the dependency-drift test: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies` — Expected: pass.
- [ ] **Step 4: Update the stale statements.** `CLAUDE.md:21`: replace `Codex has no command adapter here; reusable Codex workflows are skills.` with `For Codex, each command becomes a generated manual-only skill under `runtimes/codex/skills/`, which Codex runs as `$<name>` or from `/skills`.` `README.md:159-160`: replace `This repo has no command adapter for Codex. In Codex, you invoke the reusable workflows as skills.` with `For Codex, the generator writes the same three as skills under `runtimes/codex/skills/`, each with `agents/openai.yaml` setting `allow_implicit_invocation: false`. Run them as `$deferred`, `$fix-issue` and `$license-audit`.` Codex guide `:658`: replace `The repository does not generate Codex command adapters: reusable Codex workflows are skills.` with `The repository generates a manual-only Codex skill from each command under `runtimes/codex/skills/`.`
- [ ] **Step 5: Rewrite the register entry** (Q4, approved). `reason = 'The owner kept the three as command files. Claude Code loads them as commands. build/sync_runtime_assets.py generates a skill from each one for agy (runtimes/gemini/skills/), which agy loads as its slash command, and for Codex (runtimes/codex/skills/), which Codex runs as $<name> and keeps manual-only through agents/openai.yaml.'` `revisit = 'If Claude Code stops loading commands/*.md, or a runtime stops loading a generated command skill.'` Append to `evidence` `; plan 118 added the Codex skills (owner, plan review, 2026-11-28).`
- [ ] **Step 6: Verify** — `uv run --with pyyaml python build/check_conformance.py && bash build/run_commit_lints.sh` — Expected: `commit lints passed`.
- [ ] **Step 7: Commit** — `git commit -m "feat(install): install the Codex command skills; update the record"`

### Task 7: Table-of-contents lint for `references/`

**Files:**
- Create: `build/check_reference_tocs.py`, `build/test_check_reference_tocs.py`
- The runner, the refusal test and the docs wait for Task 8, because the repo fails the lint until Task 8 writes the tables.

**Interfaces:**
- Produces: `TOC_LINE_THRESHOLD = 100`, `MIN_HEADINGS = 2`; `headings(text: str) -> list[str]` (the `## ` headings outside fences, via `fences.strip_fenced_blocks`); `toc_entries(text: str) -> list[str] | None` (the bullets of a `## Contents` that is the first `## ` heading, else `None`); `needs_toc(text: str) -> bool`; `violations(root: Path) -> list[str]`; `render_toc(text: str) -> str` (the file with the block written or refreshed just before the first non-Contents `## `); CLI `check_reference_tocs.py [--write]` — exit 1 and one line per file without `--write`; with it, rewrite and print `wrote <path>`.

- [ ] **Step 1: Write the failing tests** — `test_short_file_needs_no_toc` (100 lines); `test_long_file_without_contents_is_reported` (101 lines, 2 headings: message `"<path>: 101 lines and 2 ## headings; add a ## Contents list (run build/check_reference_tocs.py --write)"`); `test_a_drifted_contents_is_reported` (bullets miss one heading: message names the first mismatch); `test_headings_inside_fences_are_not_counted` (Review Focus 3); `test_write_is_idempotent_and_keeps_the_intro` (Review Focus 4: an H1, a `> ⚠️` banner and a paragraph stay above the block; a second `render_toc` returns its input); `test_nested_references_are_scanned` (`references/families/x.md`).
- [ ] **Step 2: Run to verify they fail** — `cd build && uv run --with pytest python -m pytest -q test_check_reference_tocs.py` — Expected: FAIL (module missing).
- [ ] **Step 3: Implement** the module, stdlib only. It lives in `build/`, which is already a registered suite.
- [ ] **Step 4: Run** the new suite — Expected: pass (+6).
- [ ] **Step 5: Commit** — `git commit -m "feat(build): add the references/ table-of-contents lint"`

### Task 8: Write the tables of contents; turn the lint on

**Files:**
- Modify: every file `check_reference_tocs.py` lists (about 46, among them superpowers-derived `writing-skills/references/*`, `executing-plans/references/final-review.md`, `subagent-driven-development/references/mutants.md` and Andorra-derived `bayesian-workflow/references/*`), `build/run_commit_lints.sh`, `build/test_commit_lints.py`, `CLAUDE.md`, `build/CLAUDE.md`

- [ ] **Step 1:** `uv run python build/check_reference_tocs.py > /tmp/toc-before.txt; uv run python build/check_reference_tocs.py --write` — Expected: one `wrote` line per listed file.
- [ ] **Step 2: Review the diff by hand.** Each hunk adds or refreshes one `## Contents` block and nothing else (`git diff --stat` and `git diff -U0 skills/ | grep '^[-+]' | grep -v '^[-+]- \|^[-+]## Contents\|^[-+]$\|^[-+][-+][-+]'` prints nothing). For `reporting.md` and `state-space.md`, check that the refreshed bullets keep the old wording where a heading did not change.
- [ ] **Step 3: Verify the other lints still pass on the moved headings** — `uv run python build/check_links.py && uv run --with pyyaml python build/check_conformance.py && uv run python build/check_snippets.py skills/ && cd build && uv run --with pytest --with pyyaml python -m pytest -q test_check_conformance.py::test_waived_compaction_window_files_hide_no_late_heading test_runtime_support.py -k declared_dependencies`. Expected: all pass. A late-heading finding on a waived file means the block pushed a heading past the window: report it, do not shorten the block.
- [ ] **Step 4: Check `NOTICE` for the adapted files.** Where a touched file's skill has a `NOTICE` entry that lists its changes from upstream (superpowers skills, `bayesian-workflow`), add one line to that entry: `references/ files over 100 lines gained a ## Contents list (plan 118).` Where the entry only says "adapted", change nothing. Run `uv run python build/check_provenance.py` — Expected: exit 0.
- [ ] **Step 5: Commit the tables, lint still off** — `git commit -m "docs(skills): add tables of contents to long references files"`. `test_commit_lints.py` clones HEAD, so the tables must be committed before the runner line exists.
- [ ] **Step 6: Turn the lint on** — add `run reference_tocs uv run python build/check_reference_tocs.py` to `build/run_commit_lints.sh` after `helper_paths`, and `test_missing_reference_toc_is_refused(clone)` to `test_commit_lints.py` (a 120-line `references/` file with 3 headings and no Contents makes `failed_names(result) == {'reference_tocs'}`); add the Commands entry (`# Reference TOCs: a references/ file over 100 lines with 2+ ## headings starts with a ## Contents list of them; --write writes it`) and the `build/CLAUDE.md` paragraph (the fifteenth commit lint).
- [ ] **Step 7: Verify** — `bash build/run_commit_lints.sh && cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py` — Expected: `commit lints passed`; tests pass (+1).
- [ ] **Step 8: Commit** — `git commit -m "feat(build): run the references/ TOC lint as a commit lint"`

### Task 9: Skill scanner workflow (download gate)

**Files:**
- Create: `build/skill_scan.sh`, `.github/workflows/skill-scan.yml`
- Modify: `build/test_commit_lints.py` (workflow and wrapper tests), `CLAUDE.md` Commands, `build/CLAUDE.md`

**Interfaces:**
- Produces: `build/skill_scan.sh [scanner args...]` — runs `uv tool run --python 3.13 --from "cisco-ai-skill-scanner==${SCANNER_VERSION}" skill-scanner scan-all skills --recursive --policy balanced --fail-on-severity high "$@"` from the repo root, with `SCANNER_VERSION=2.3.2` as its one pin. The repo's `uv.toml` freeze date (`exclude-newer`) bounds the scanner's dependencies, litellm included. The scanner stays out of `build/versions.toml`: `versions.py bump` re-pins every `[packages]` entry by one joint resolve, so the scanner's tree would join the JAX and NumPyro resolve.

- [ ] **Step 1: STOP — owner gate.** Ask the owner in chat: "Task 9 will install Cisco `skill-scanner` 2.3.2 (PyPI `cisco-ai-skill-scanner`, Apache-2.0, https://github.com/cisco-ai-defense/skill-scanner) through `uv tool run`, and run it on `skills/` with static analyzers only. Go ahead?" Wait for a yes, unless the Q3 ruling already gave it. Until then, Tasks 9-10 wait and the other tasks proceed.
- [ ] **Step 2: Write the failing tests** in `test_commit_lints.py`, modeled on the drift-workflow tests: `test_skill_scan_workflow_triggers_and_permissions` (`pull_request` with `paths: ['skills/**', 'build/skill_scan.sh', '.github/workflows/skill-scan.yml']`, a weekly `schedule`, `workflow_dispatch`; `permissions: {contents: read}` only); `test_skill_scan_workflow_pins_actions_and_bounds_the_job` (every `uses:` is a 40-hex SHA with a `# v` comment, the same `actions/checkout` and `astral-sh/setup-uv` SHAs as `lints.yml`, `persist-credentials: false`, `timeout-minutes` set, and the run step is `bash build/skill_scan.sh --format summary`); `test_skill_scan_pins_one_version_and_static_analyzers_only` (the wrapper sets `SCANNER_VERSION=2.3.2` once, passes `--fail-on-severity high`, and contains none of `--use-llm`, `--use-virustotal`, `--use-aidefense`, `--enable-meta`, `--use-osv`, `--adjudicate`).
- [ ] **Step 3: Implement** the wrapper (executable, committed `100755`) and the workflow. Add the Commands entry (`# Skill scan (advisory, weekly CI; downloads cisco-ai-skill-scanner): bash build/skill_scan.sh`) and a `build/CLAUDE.md` paragraph that names the pin, the static-only rule and why the scanner is not a commit lint.
- [ ] **Step 4: Run** `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k skill_scan` — Expected: pass (+3).
- [ ] **Step 5: Commit** — `git commit -m "ci: add an advisory skill-scanner workflow (static analyzers, pinned 2.3.2)"`

### Task 10: First scan and triage

**Files:**
- Create: `specs/findings/skill-scan-2026-11.md`
- Modify: `specs/deferred_items.md` (only for findings deferred)

- [ ] **Step 1: Run the scan locally** — `bash build/skill_scan.sh --format json --output ~/.cache/agent-skills/scratch/plan118/scan.json; echo "exit $?"`, then `bash build/skill_scan.sh --format summary`. Record the scanner version it reports, the exit code and the counts by severity.
- [ ] **Step 2: Triage every finding at high or critical, and every finding class below** in the findings record: one row per finding (skill, file:line, rule id, severity, verdict `true positive` / `false positive` / `accepted`, reason). Expected classes in this repo: network fetches in the codes and BLS build scripts, `subprocess` in kit runners, and shell commands in skill prose.
- [ ] **Step 3: Act on the verdicts.** Fix a true positive whose fix is under about 20 lines in this task. Each other true positive becomes a `specs/deferred_items.md` item under this plan's section, with an `→ item:` marker in the record. False positives stay listed; do not add a suppression file in this plan.
- [ ] **Step 4: Verify** — `bash build/run_commit_lints.sh` → `commit lints passed`. If the workflow's `--fail-on-severity high` would fail on findings ruled `accepted` or `false positive`, say so in the record and ask the owner whether to lower it to `critical` or keep a failing advisory job.
- [ ] **Step 5: Commit** — `git commit -m "docs(findings): triage the first skill-scanner run"`

### Task 11: Trigger-eval suite and kit

**Files:**
- Create: `specs/baseline/trigger-evals-data-modeling.md` (the record, with a quarantine banner like plan 111's), `specs/baseline/trigger-evals-data-modeling/kit/` — copied from `specs/baseline/red-baseline-codes-description/kit/` (the newest committed trigger kit, 2026-11-26; the 2026-11-27 kits are case-rep kits), trigger lane only: `common.sh`, `run_trigger_reps.sh`, `rep_tools.py`, `audit.py`, `triggers.py`, `kit_identity.py`, `isolation_probe.txt` unchanged except for the edits Step 3 names; new `queries.py`, `split.py`, `test_te_kit.py`, `fixtures/trigger/repo/README.md`, `fixtures/trigger/listing.txt`
- Modify: `build/suites.toml` (suite `trigger-evals-kit`)

**Interfaces:**
- Produces: `queries.py` — `SKILLS: tuple[str, ...]` (Q1's eight), `QUERIES: dict[str, dict[str, Query]]`, `Query(text: str, target: str, label: Literal['load', 'near-miss'], sibling: str | None)`; `split.py` — `SEED = 118`, `assign() -> dict[str, Literal['train', 'validation']]` keyed by query text, deterministic, 8+6 / 4+2 per skill; `triggers.py tally <runs-root>` prints per skill: load recall, near-miss false-load rate, by split and model.

- [ ] **Step 1: Write the queries.** 12 should-load and 8 near-miss queries per skill, each a message a user would type, none naming a skill or quoting its description. Each near-miss names its `sibling` (the skill that should load instead, or `None` for out-of-set). Each query text appears once in the whole suite; the split is assigned per text. The record lists the queries; the kit file is the source.
- [ ] **Step 2: Write the failing kit tests** — `test_every_skill_has_12_loads_and_8_near_misses`; `test_split_is_stratified_and_stable` (two `assign` calls agree; counts 8+6 / 4+2 per skill); `test_each_query_text_appears_once` (no text is both one skill's near-miss and a sibling's should-load, so no text can sit in train for one skill and validation for another); `test_no_query_names_a_skill` (no query contains any name in `listing.txt`); `test_a_load_before_the_first_void_event_counts` (the 2026-11-28 ruling, with a stub stream); and plan 111's stub-`claude` runner tests, cut to the new names.
- [ ] **Step 3: Adapt the copies** — `cases.py`'s skill under test becomes the query's `target`; the root `/private/tmp/te118`; the scratch folder `~/.cache/agent-skills/scratch/plan118/triggers/`; `listing.txt` holds the eight names. Record each changed file in the record's Kit table, as plan 111's record does.
- [ ] **Step 4: Run** `uv run python build/run_suites.py trigger-evals-kit && uv run python build/run_suites.py --check` — Expected: pass.
- [ ] **Step 5: Commit** — `git commit -m "feat(baseline): add the data-and-modeling trigger-eval suite and kit"` (the commit registers the scoring rules before any rep runs).

### Task 12: Isolation probe and pilot

- [ ] **Step 1:** Run the isolation probe on Sonnet and Opus (`run_trigger_reps.sh <ref> new probe ...`), then one pilot rep of one train query per model. Spend cap for this task: $3. Record `claude --version`, each rep's cost and audit.
- [ ] **Step 2:** If a probe or pilot rep is VOID, stop and report the reason; do not change the rules after a rep is seen.
- [ ] **Step 3: Commit** the record update — `git commit -m "docs(baseline): record the trigger-eval probe and pilot"`

### Task 13: Baseline run (Q1, approved: $60 cap)

- [ ] **Step 1:** Run every query once per model under the Q1 cap (default $60), batch by skill, and before each batch check `running total + batch reps × $0.25 ≤ cap`; stop when it fails.
- [ ] **Step 2:** `triggers.py tally` per split; write the counts, the VOID reps and the spend table into the record. The validation split's counts are the baseline a later description rewrite is scored against; no description changes in this plan.
- [ ] **Step 3: Commit** — `git commit -m "docs(baseline): record the trigger-eval baseline run"`
