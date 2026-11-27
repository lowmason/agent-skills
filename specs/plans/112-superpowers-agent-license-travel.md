# Superpowers Agent License Travel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Each installed superpowers-derived agent, in every runtime, carries a one-line pointer to `LICENSE-superpowers`, and `install.py` installs that file beside it.

**Architecture:** The pointer is one `# license:` YAML comment in the canonical agent's frontmatter. `build/sync_runtime_assets.py` copies it verbatim into the generated Codex TOML and agy Markdown adapters. `install.py` reads the pointers of the agents it installs and installs each named root license file into the same agents directory. `build/check_provenance.py` gains an `AGENT_LICENSES` table and checks the pointer on all three surfaces.

**Tech Stack:** Python (the dev Python in `build/versions.toml`), PyYAML (generator only), pytest, `uv run`.

**Spec:** none. The requirement is the item "License travel for single-file agents" in `specs/deferred_items.md`, section `53-agent-skills-portability — 2026-10-20`, with its `→ progress 2026-11-17 (owner ruling)` note. Background: `specs/completed/agent-skills-portability-spec.md` R4 and "Out of scope", and `NOTICE`.

## Global Constraints

- Owner ruling, verbatim: "`install.py` installs `LICENSE-superpowers` beside the agents, and each superpowers-derived agent carries a one-line pointer to it."
- Superpowers-derived agents, per `NOTICE` ("Changes from upstream"): `agents/code-reviewer.md` and `agents/task-reviewer.md`, and only these. `debugger`, `docs-writer`, `explore`, `security-auditor` and `test-runner` are original (plan 17, "All prose is original work") and get no pointer.
- The pointer is exactly this line, the same in both agents (F1):
  `# license: MIT. Adapted from https://github.com/obra/superpowers, Copyright (c) 2025 Jesse Vincent. Full text: LICENSE-superpowers (repository root; install.py installs it beside this file).`
- The pointer sits inside the frontmatter, directly above the `# cc-guide:` line, which stays the last frontmatter line (`build/cc_guide/cli.py lint` enforces this). No parsed frontmatter field and no body byte changes.
- The pointer never reaches the model: not in a Claude agent body, not in a Codex `developer_instructions` string, not in an agy agent body.
- `install.py` installs no copy of a license under `agents/` or `runtimes/`: it links (or, with `--copy`, copies) the root file. The root files stay canonical.
- Never hand-edit `runtimes/`. Regenerate with `uv run --with pyyaml python build/sync_runtime_assets.py` and check with `--check`.
- Indentation: keep each file's own. `install.py`, `build/sync_runtime_assets.py` and `build/test_runtime_support.py` use 2 spaces. `build/check_provenance.py` and `build/test_check_provenance.py` use 4. Single quotes.
- `install.py` stays stdlib-only and standalone: it imports nothing from `build/`.
- `build/check_provenance.py` stays stdlib-only (its CLAUDE.md command has no `--with`).
- Files: tasks edit only `agents/code-reviewer.md`, `agents/task-reviewer.md`, `runtimes/` (generated), `build/sync_runtime_assets.py`, `build/check_provenance.py`, `build/test_check_provenance.py`, `build/test_runtime_support.py`, `install.py`, `NOTICE`, `README.md` (License section) and `CLAUDE.md` (the provenance paragraph). The completion protocol's own edits are allowed too. Any other file needs your human partner's yes first.
- Before each commit: `bash build/run_commit_lints.sh` passes. Also run `uv run python build/cc_guide/cli.py lint` after a change to a file that carries a `# cc-guide:` citation (both agents, `install.py`).

## Review Focus

1. agy or Codex meets `LICENSE-superpowers` in its agents folder → it must not load it as an agent or warn. All three guides document agent files only by suffix (`<name>.md`, `<name>/agent.md`, `<name>.toml`); nothing here was probed. Test: Task 3 `test_agent_license_name_matches_no_agent_file_pattern`.
2. Someone copies one agent file by hand, or a third-party installer takes it alone → the pointer still names the upstream, the copyright holder and the license file. Test: Task 1 `test_license_pointer_names_upstream_holder_and_file`.
3. The pointer leaks into what the model reads → it never does, so agent behavior and token cost do not change. Test: Task 1 `test_license_pointer_stays_out_of_the_model_input`.
4. A second `install.py all --companions` run → the license link reports `unchanged` and the run exits 0. Test: Task 3 `test_companion_install_links_the_agent_license_beside_the_agents` (two runs).
5. `~/.gemini/config/agents` is a symlink to `~/.claude/agents` → the existing agent-conflict refusal still fires first and writes nothing. Test: the existing `test_aliased_destinations_with_different_sources_write_nothing` must still pass unchanged in Task 3 Step 4.

## Decisions

Owner answers at plan review, 2026-11-27 (a `/deferred` pass):

- **D1.** The five other agents (`debugger`, `docs-writer`, `explore`, `security-auditor`, `test-runner`) are the owner's original work, so NOTICE may say so (F5).
- **D2.** The pointer line in Global Constraints is approved as written (F1).
- **D3.** The owner's own `LICENSE` does not travel with the two agents (F2, the 11-17 ruling).
- **D4.** The docs scope of F5 (NOTICE, README's License section, one CLAUDE.md sentence) is approved.
- **D5.** Review Focus 1 gets a live check on the owner's Mac, because neither `codex` nor `agy` is installed in the planning container. After Task 3, with `install.py all --companions` run on that machine, start `codex` and `agy` once each and confirm that neither loads `LICENSE-superpowers` as an agent nor warns about it. Record the result, with each CLI's version, in the completion report. The executing session asks the owner to run it, or attaches the owner's machine if the owner allows. It is a completion gate: the plan does not complete until it is recorded.
  **Result, run by the owner by hand before execution, 2026-11-27: PASS.** On the owner's Mac, with codex-cli 0.172.0 and agy 1.5.18, a copy of the root `LICENSE-superpowers` was placed in `~/.codex/agents/` and `~/.gemini/config/agents/` (both real folders, no symlink, each holding the 7 installed agents). `agy agents` printed the same list before and after (empty diff). Neither CLI printed a warning at startup, and `/agents` showed no `LICENSE-superpowers` entry in either. `codex exec` printed no line naming a license or the agents folder. The files were then removed. This meets D5's gate. The executing session records this result in the completion report and does not rerun the check, unless Task 3 changes where or how the license file is installed.

### Defaults for owner review

- **F1. Pointer wording and form.** A YAML comment, not a body line, so the model's input is unchanged (see "Micro-test" below). Wording as in Global Constraints. "Beside this file" is true once installed, and "repository root" is true in the repo.
- **F2. Only `LICENSE-superpowers` travels.** The root `LICENSE` (Lowell Mason's own notice) does not travel with any agent, as with the ruling. The pointer still says "MIT".
- **F3. Derived from the pointer.** `install.py` learns what to install from the pointer lines of the agents it installs, not from its own table. `check_provenance.py`'s `AGENT_LICENSES` is the one table, and a test in Task 3 checks that the two agree.
- **F4. Lint scope.** `check_provenance.py` checks the canonical agents and both generated adapters, because each adapter installs on its own.
- **F5. Docs.** NOTICE, README's License section and CLAUDE.md's provenance paragraph each record the rule, as R4.4 did for skills (Task 4 and Task 2). NOTICE also states that the five other agents are original works (Q1 in the report).

### Planning notes

- **Micro-test: not needed.** writing-skills micro-tests check wording that an agent reads. The pointer is a YAML comment in frontmatter. Claude Code parses the frontmatter and sends only the body as the system prompt. Codex sends `developer_instructions`, and the TOML comment is outside it. agy also parses its frontmatter. So the model's input is byte-identical before and after, which Task 1's test pins. A body-line pointer would change the input and would need the no-guidance control.
- **Conformance register.** `agents/*.md` is kind `agent`, `install.py` is kind `installer` and `CLAUDE.md` is kind `claude-md` in `build/cc_guide/conformance.toml`. `check_conformance.py` runs in the commit lints. No new deviation or gap is expected. The `claude-md-size` check keeps CLAUDE.md under 200 lines (183 now), and Task 2 adds no line.
- **Provenance.** No upstream text is added. The pointer and the new NOTICE text are original. The adapters already "inherit the attribution and license of its canonical source" (NOTICE, runtimes paragraph); this plan makes that visible in the installed file.

---

### Task 1: The pointer in the agents and their generated adapters

**Files:**
- Modify: `agents/code-reviewer.md` (frontmatter), `agents/task-reviewer.md` (frontmatter)
- Modify: `build/sync_runtime_assets.py` (`render_codex_agent`, `render_gemini_agent`, new `license_pointers`)
- Regenerate: `runtimes/codex/agents/code-reviewer.toml`, `runtimes/codex/agents/task-reviewer.toml`, `runtimes/gemini/agents/code-reviewer.md`, `runtimes/gemini/agents/task-reviewer.md`
- Test: `build/test_runtime_support.py`

**Interfaces:**
- Produces: `license_pointers(path: Path) -> list[str]` in `build/sync_runtime_assets.py`: the lines of the canonical file's frontmatter block that match `LICENSE_POINTER_RE = re.compile(r'^# license: .+$', re.M)`, in file order. The pointer line text of Global Constraints, which Tasks 2 and 3 match with the prefix `# license: `.

- [ ] **Step 1: Write the failing tests** in `build/test_runtime_support.py`

```python
POINTER = '# license: MIT. Adapted from upstream. Full text: LICENSE-x (beside this file).'

def pointed_source(tmp_path):
  source = tmp_path / 'lead.md'
  source.write_text(f'---\nname: lead\ndescription: Leads.\ntools: Read\n{POINTER}\n# cc-guide: x @1\n---\nbody\n')
  return source

def test_codex_agent_adapter_carries_the_license_pointer(tmp_path):
  rendered = load_sync_module().render_codex_agent(pointed_source(tmp_path))
  assert rendered.splitlines()[1] == POINTER
  assert tomllib.loads(rendered)['developer_instructions'] == 'body\n'

def test_gemini_agent_adapter_carries_the_license_pointer(tmp_path):
  sync = load_sync_module()
  rendered = sync.render_gemini_agent(pointed_source(tmp_path))
  head, _, body = rendered.partition('\n---\n\n')
  assert POINTER in head.splitlines() and body == 'body\n'
  adapter = tmp_path / 'adapter.md'
  adapter.write_text(rendered)
  assert 'license' not in sync.read_frontmatter(adapter)[0]

def test_agent_adapter_without_a_pointer_has_none(tmp_path):
  # a canonical file with no pointer renders no '# license:' line in either adapter

def test_license_pointer_names_upstream_holder_and_file():
  for name in ('code-reviewer', 'task-reviewer'):
    (line,) = load_sync_module().license_pointers(REPO / 'agents' / f'{name}.md')
    assert 'https://github.com/obra/superpowers' in line
    assert 'Jesse Vincent' in line and 'LICENSE-superpowers' in line

def test_license_pointer_stays_out_of_the_model_input():
  # for both agents: '# license:' not in read_frontmatter(...)[1] of agents/<n>.md
  # and of runtimes/gemini/agents/<n>.md, nor in the parsed developer_instructions
  # of runtimes/codex/agents/<n>.toml; and the pointer line is in each of the three files
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k 'license_pointer or without_a_pointer'`
Expected: FAIL. `license_pointers` is not defined, and the adapters carry no pointer.

- [ ] **Step 3: Implement `license_pointers(path: Path) -> list[str]` and emit it**

Reuse the frontmatter regex that `read_frontmatter` already applies, so only frontmatter lines count. In `render_codex_agent`, put each pointer line right after `GENERATED_COMMENT`. In `render_gemini_agent`, append each pointer line to `yaml_text` after the dumped keys and before the "Claude-only tools dropped" note.

- [ ] **Step 4: Add the pointer to both canonical agents**

Insert the Global Constraints pointer line in `agents/code-reviewer.md` and `agents/task-reviewer.md`, directly above the `# cc-guide:` line. Regenerate with `uv run --with pyyaml python build/sync_runtime_assets.py`.

- [ ] **Step 5: Run the checks**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py`
Expected: all pass.
Run: `uv run --with pyyaml python build/sync_runtime_assets.py --check` and `uv run python build/cc_guide/cli.py lint` and `uv run python build/check_reviewer_block.py`
Expected: each exits 0. `git diff --stat runtimes/` shows exactly the four adapters of the two agents, each with one added line.

- [ ] **Step 6: Commit**

```bash
git add agents/code-reviewer.md agents/task-reviewer.md build/sync_runtime_assets.py build/test_runtime_support.py runtimes/
git commit -m 'feat(agents): point the superpowers-derived agents and their adapters at LICENSE-superpowers'
```

### Task 2: The provenance lint enforces the pointer

**Files:**
- Modify: `build/check_provenance.py` (new `AGENT_LICENSES`, `agent_license_violations`, call in `main`, docstring)
- Modify: `CLAUDE.md` (the provenance paragraph sentence that names `BUNDLED_LICENSES`)
- Test: `build/test_check_provenance.py`

**Interfaces:**
- Consumes: the pointer prefix `# license: ` (Task 1).
- Produces: `AGENT_LICENSES: dict[str, tuple[str, ...]] = {'LICENSE-superpowers': ('code-reviewer', 'task-reviewer')}` and `agent_license_violations(repo: Path, table: dict[str, tuple[str, ...]]) -> list[str]` in `build/check_provenance.py`. Task 3's agreement test imports `AGENT_LICENSES`.

The three surfaces of an agent `<n>` are `agents/<n>.md`, `runtimes/codex/agents/<n>.toml` and `runtimes/gemini/agents/<n>.md`. In a `.md` surface, only a pointer line inside the frontmatter counts. In a `.toml` surface, any line that starts with `# license: ` is a comment, because the generator writes each string on one line. A pointer's license names are its `LICENSE-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*` matches.

- [ ] **Step 1: Write the failing tests** in `build/test_check_provenance.py`, with a helper `_agent_tree(tmp_path, pointed)` that writes the root `LICENSE-x`, and for agents `adapted` and `own` all three surfaces, with the pointer `# license: MIT. Full text: LICENSE-x.` on the surfaces listed in `pointed`

```python
AGENT_TABLE = {'LICENSE-x': ('adapted',)}
ADAPTED_SURFACES = ('agents/adapted.md', 'runtimes/codex/agents/adapted.toml', 'runtimes/gemini/agents/adapted.md')

def test_agent_licenses_clean_when_every_surface_points(tmp_path):
    repo = _agent_tree(tmp_path, pointed=ADAPTED_SURFACES)
    assert agent_license_violations(repo, AGENT_TABLE) == []

def test_agent_licenses_report_a_missing_pointer(tmp_path):
    # pointer absent from runtimes/codex/agents/adapted.toml only
    assert agent_license_violations(repo, AGENT_TABLE) == [
        'runtimes/codex/agents/adapted.toml: no license pointer naming LICENSE-x, '
        'which AGENT_LICENSES maps to adapted']

def test_agent_licenses_report_an_unmapped_pointer(tmp_path):
    # agents/own.md also carries the pointer
    assert agent_license_violations(repo, AGENT_TABLE) == [
        'agents/own.md: license pointer names LICENSE-x, which AGENT_LICENSES does not map to own']

def test_agent_licenses_report_a_pointer_in_the_body(tmp_path):
    # agents/adapted.md has the pointer below the closing '---' and not in the frontmatter
    assert agent_license_violations(repo, AGENT_TABLE) == [
        'agents/adapted.md: license pointer outside the frontmatter, where the model reads it',
        'agents/adapted.md: no license pointer naming LICENSE-x, which AGENT_LICENSES maps to adapted']

def test_agent_licenses_report_a_bad_table(tmp_path):
    assert agent_license_violations(repo, {'LICENSE-y': ('ghost',)}) == [
        'AGENT_LICENSES: LICENSE-y is not a root license file',
        'AGENT_LICENSES: LICENSE-y names ghost, which is not an agent in agents/']

def test_agent_licenses_table_matches_notice():
    notice = (REPO / 'NOTICE').read_text()
    distilled = re.findall(r'agents/([a-z-]+)\.md is a read-only agent definition distilled', notice)
    assert sorted(distilled) == sorted(AGENT_LICENSES['LICENSE-superpowers'])
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd build && uv run --with pytest python -m pytest -q test_check_provenance.py -k agent_licenses`
Expected: FAIL with an ImportError on `agent_license_violations`.

- [ ] **Step 3: Implement `agent_license_violations` and call it in `main`**

Order the messages as the tests do: table errors first, then per agent in sorted order, per surface in the order listed above. Add one line to the module docstring naming the agent check.

- [ ] **Step 4: Update CLAUDE.md**

In the provenance paragraph, append this sentence after "so edit a root license file and its copies together.":
"Each superpowers-derived agent carries a `# license:` pointer to `LICENSE-superpowers`, which `install.py` installs beside it, and the same lint's `AGENT_LICENSES` checks the pointers."
Keep it on the existing line, so CLAUDE.md gains no line.

- [ ] **Step 5: Run the checks**

Run: `cd build && uv run --with pytest python -m pytest -q test_check_provenance.py`
Expected: all pass.
Run: `uv run python build/check_provenance.py`
Expected: exit 0 on the repo (Task 1 put the pointers in place).
Mutation check: delete the pointer from `runtimes/gemini/agents/task-reviewer.md` in the working tree, run the lint, expect exit 1 with that file's `no license pointer` line, then `git checkout runtimes/gemini/agents/task-reviewer.md`.

- [ ] **Step 6: Commit**

```bash
git add build/check_provenance.py build/test_check_provenance.py CLAUDE.md
git commit -m 'feat(build): check_provenance checks the agent license pointers (AGENT_LICENSES)'
```

### Task 3: `install.py` installs the pointed-to license beside the agents

**Files:**
- Modify: `install.py` (new `LICENSE_POINTER_RE`, `LICENSE_NAME_RE`, `pointed_licenses`, `agent_license_items`, a call in `runtime_items`, module docstring)
- Test: `build/test_runtime_support.py`

**Interfaces:**
- Consumes: the pointer lines (Task 1). `AGENT_LICENSES` from `check_provenance` (Task 2), in the agreement test only.
- Produces: `pointed_licenses(source: Path) -> list[str]` (the license names on the file's `# license: ` lines, in order, without repeats) and `agent_license_items(agent_items: list[InstallItem], destination_dir: Path) -> list[InstallItem]` (one `InstallItem(REPO / name, destination_dir / name)` per distinct name across the agents; raises `InstallError` when `REPO / name` is not a file).

`runtime_items` adds the license items right after `agent_items`, in the same `companions` branch, so an install without companions installs no license. The destination directory is the runtime's agents directory: `~/.claude/agents`, `~/.codex/agents` or `~/.gemini/config/agents`.

- [ ] **Step 1: Write the failing tests** in `build/test_runtime_support.py`

```python
AGENT_DIRS = {'claude': '.claude/agents', 'codex': '.codex/agents', 'gemini': '.gemini/config/agents'}

@pytest.mark.parametrize('runtime', sorted(AGENT_DIRS))
def test_companion_install_links_the_agent_license_beside_the_agents(tmp_path, runtime):
  for _ in range(2):
    result = run_install(tmp_path, runtime, '--companions')
    assert result.returncode == 0, result.stdout + result.stderr
  link = tmp_path / AGENT_DIRS[runtime] / 'LICENSE-superpowers'
  assert link.is_symlink() and link.resolve() == REPO / 'LICENSE-superpowers'
  assert f'unchanged {link}' in result.stdout

def test_copy_install_copies_the_agent_license(tmp_path):
  # run_install(tmp_path, 'all', '--companions', '--copy'): in each of the three
  # agent dirs, LICENSE-superpowers is a regular file, byte-identical to the root file

def test_install_without_companions_installs_no_agent_license(tmp_path):
  # run_install(tmp_path, 'claude', '--no-companions'): no LICENSE-superpowers under .claude/

def test_agent_licenses_match_the_provenance_table():
  # for each runtime's agent sources (agents/*.md, runtimes/codex/agents/*.toml,
  # runtimes/gemini/agents/*.md): {(stem, name) for name in install.pointed_licenses(src)}
  # == {(agent, name) for name, agents in AGENT_LICENSES.items() for agent in agents}

def test_agent_license_name_matches_no_agent_file_pattern():
  # every installed license name has no '.md' or '.toml' suffix and is a regular
  # file at the repo root, so no runtime's documented agent pattern matches it

def test_agent_pointer_to_a_missing_root_license_refuses(tmp_path, monkeypatch):
  # fake repo (make_skill + agents/x.md whose frontmatter has
  # '# license: MIT. Full text: LICENSE-gone.'), install.main(['claude', '--home', home])
  # returns nonzero, stderr holds
  # 'agents/x.md: license pointer names LICENSE-gone, which is not a file at the repository root',
  # and home stays empty
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k 'agent_license'`
Expected: FAIL. No `LICENSE-superpowers` is installed, and `pointed_licenses` is not defined.

- [ ] **Step 3: Implement `pointed_licenses` and `agent_license_items`, and call them in `runtime_items`**

`LICENSE_POINTER_RE = re.compile(r'^# license: .*$', re.M)` and `LICENSE_NAME_RE = re.compile(r'\bLICENSE-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*')`. The `InstallError` message is the one the test pins, with the path relative to `REPO`. In the module docstring, add one sentence after "A full install also includes each runtime's companion agents and commands": "With the agents it installs the license files their `# license:` lines name, such as LICENSE-superpowers, in the same directory."

- [ ] **Step 4: Run the checks**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py`
Expected: all pass, the aliased-agent-directory refusal test included, with no change to it.
Run: `uv run python install.py all --companions --dry-run --home "$(mktemp -d)"`
Expected: three `would link .../LICENSE-superpowers -> ...` lines, one per agents directory.
Run: `uv run python build/cc_guide/cli.py lint`
Expected: exit 0.

- [ ] **Step 5: Commit**

```bash
git add install.py build/test_runtime_support.py
git commit -m 'feat(install): install the license an agent points to beside the agents'
```

### Task 4: Record the rule in NOTICE and README

**Files:**
- Modify: `NOTICE` (a new paragraph after the "Each skill directory carries copies" paragraph, one sentence in the runtimes paragraph, one bullet in the superpowers "Changes from upstream" list)
- Modify: `README.md` (License section, the last paragraph)

**Interfaces:**
- Consumes: the behavior of Tasks 1 to 3. `test_agent_licenses_table_matches_notice` (Task 2) reads the two "distilled" bullets, which this task leaves unchanged.

Exact copy (F5, approved at plan review):

- NOTICE, new paragraph after the skills paragraph:
  "Two agent definitions are adapted from superpowers: agents/code-reviewer.md and agents/task-reviewer.md. An agent installs as a single file. So each of the two, and each of its generated adapters under runtimes/, carries one `# license:` comment line that points to LICENSE-superpowers. When install.py installs the agents, it puts LICENSE-superpowers in the same agents directory. build/check_provenance.py checks the pointers (AGENT_LICENSES). The other agents under agents/ are original works by Lowell Mason under this repository's MIT license."
- NOTICE, runtimes paragraph, after "each adapter inherits the attribution and license of its canonical source.":
  "An adapter of a superpowers-derived agent also carries its source's `# license:` line."
- NOTICE, superpowers "Changes from upstream", a new bullet after the `# cc-guide:` bullet:
  "agents/code-reviewer.md and agents/task-reviewer.md gained one `# license:` YAML comment above the `# cc-guide:` line on <execution date> (plan 112). It points to LICENSE-superpowers, which install.py now installs beside the agents. No parsed field and no body text changed."
- README, the paragraph that starts "Each skill directory also carries copies", append:
  "The two agents adapted from superpowers point to `LICENSE-superpowers`, and `install.py` installs that file beside them."

- [ ] **Step 1: Make the three NOTICE edits and the README edit**
- [ ] **Step 2: Run the checks**

Run: `cd build && uv run --with pytest python -m pytest -q test_check_provenance.py` and `bash build/run_commit_lints.sh`
Expected: all pass, exit 0.

- [ ] **Step 3: Commit**

```bash
git add NOTICE README.md
git commit -m 'docs(notice): record license travel for the superpowers-derived agents'
```
