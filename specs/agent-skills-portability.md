# Agent-skills portability — Design Spec

**Status: DESIGN APPROVED (2026-10-03); written spec awaiting review.**
The owner approved all five design sections in a brainstorming pass over
`specs/completed/agent-skills-best-practices.md` (a September 2026 survey of
Agent Skills portability across Claude Code, Codex, Gemini CLI, Cursor, Copilot,
and others). This document is the handoff for implementation planning; nothing
here has been implemented. The survey is this spec's input and retires with it.

## Purpose and scope

Bring the repo to the parts of the survey that apply to it, in four themes the
owner selected:

1. **Frontmatter conformance** — the lint accepts every Agent Skills spec field,
   separates spec keys from host extensions, and checks the shapes the spec
   defines (R1).
2. **Codex-visible openings** — description openings work under Codex's
   per-description truncation, and `writing-skills` records the measured fact
   (R2).
3. **Self-contained scripts** — every runnable bundled script carries a PEP 723
   header and is invoked with `uv run` (R3).
4. **License travel** — each skill directory carries the license texts that
   apply to it, so a single-skill install keeps MIT's required notice (R4).

Most of the survey is already true here and needs no work: `name` matches its
directory and descriptions are within 1,024 characters (`build/check_frontmatter.py`);
`install.py` links `skills/` into `~/.claude/skills` and the cross-runtime
`~/.agents/skills`, with a `--copy` fallback; skill bodies name no runtime tool
(`TodoWrite`, Skill/Task/Agent tool) and use no `$ARGUMENTS` or `` !`cmd` ``
injection, and bundled paths use `<this-skill-dir>`; side-effect gates live in
skill bodies; every command is `disable-model-invocation: true`.

## Measured baseline (2026-10-03)

| Fact | Evidence |
|---|---|
| `ALLOWED_KEYS` lacks the spec field `compatibility`, so the lint rejects a spec-valid skill | `build/check_frontmatter.py` |
| Gemini CLI 0.46.0 loads the three skills carrying Claude host keys (`effort`: bayesian-workflow, tune-hyperparameters; `context`: tech-debt) as `[Enabled]` | `gemini skills list --all`, run from a neutral directory |
| Codex CLI 0.154.0 lists the same three skills | `codex debug prompt-input`, run from `/tmp/bwprobe/` |
| Codex shortens descriptions when its listing exceeds its budget. With 93 skills listed (66 from `~/.agents/skills`, the rest system and plugin skills), 31 of this repo's 32 descriptions were cut to 156–164 characters (median 158); only `test-driven-development` (79 characters) appeared whole. Measured at this one skill count only. That the cutoff moves with the number of skills sharing the budget is an inference from Codex's documented budget, not a measurement | same `codex debug prompt-input` render |
| All 32 descriptions lead with "Use when" and name their primary trigger within the first 150 characters | per-skill review of each description's opening (R2.1) |
| One description contains angle brackets: llm-wiki's `'verify <page>'` | YAML parse of every `SKILL.md` |
| Two of 16 runnable scripts carry PEP 723 headers (both `build.py`); others are invoked as `python`, `python3`, or `uv run --python 3.13 --with … python …` | grep of `skills/**` |
| The 13 superpowers skills have no `license` field; no skill directory contains a license file | YAML parse; `ls skills/*/LICENSE*` |
| NOTICE credits `bayesian-workflow` to Alexandre Andorra's MIT skill, but no copyright line or license text for it exists in the repo | `grep -i andorra NOTICE` and the repo tree |
| Only `writing-skills` has a body over 500 lines (696) | line count after the closing frontmatter `---` |

## Decisions and alternatives

1. **Keep `skills/` as the canonical tree.** Moving it to `.agents/skills/` has a
   large blast radius (installer, tests, CLAUDE.md, symlinks) and buys nothing:
   the installer already links into every runtime's discovery path, which is the
   survey's own alternative. *Rejected.*
2. **No in-repo `.claude/skills` symlink.** The skills already load user-level
   from the same checkout; a project-level link would list each one twice.
   *Rejected.*
3. **No manual-only conversion of side-effecting skills.**
   `disable-model-invocation: true` removes a skill from the model's reach,
   which would break bare-name handoffs (`finishing-a-development-branch`,
   `using-git-worktrees`, and the others are invoked by name from other skills).
   Their side effects are already gated in their bodies, the survey's portable
   pattern. *Rejected.*
4. **Keep the "Use when…" description convention.** The survey suggests "Does X.
   Use when Y". `writing-skills`, the governing meta-skill, requires trigger-only
   descriptions on tested evidence that a workflow summary in the description
   lets agents skip the body. "Use when" already front-loads the trigger.
   *Rejected.*
5. **No description rewrites in this spec.** R2.1's review found none needed,
   and no trigger evals exist to catch a regression. The one exception is the
   angle-bracket fix (R1.5), which is wording-equivalent.
6. **The strict profile is a report, not the gate.** Both measured non-Claude
   runtimes load skills with host keys; strictness matters only for claude.ai
   uploads and `skills-ref`-style validators (R1.8).
7. **No secondary-source numbers become lint caps.** The survey's 1,536-character
   truncation, Codex's 2% / 8,000-character budget, and Claude Code's listing
   fraction stay out of the lint; it keeps the spec's 1,024 cap. Claude Code
   listing behavior is documented in
   `specs/guides/claude-code-customization-guide.md`.
8. **House PEP 723 form, not `#!/usr/bin/env -S uv run --script`.** A plain
   `#!/usr/bin/env python3` shebang keeps the script runnable by bare `python3`
   where uv is absent; `uv run <path>` reads the header either way. The two
   existing `build.py` headers are the template.
9. **All runnable scripts become self-contained**, including the three that read
   saved model artifacts. No single work venv pairs NumPyro with ArviZ, so the
   project interpreter can lack the imports these scripts need, and work repos
   that install `hooks/uv-guard.sh` deny bare `python …` anyway.
10. **Every skill bundles license text**, not only those with third-party
    content: one uniform rule, enforced byte-for-byte, at no context cost (the
    files are never referenced, so never loaded).

## Requirements

### R1 — Frontmatter conformance (`build/check_frontmatter.py`)

R1.1 **Key sets.** Replace `ALLOWED_KEYS` with two named sets and allow their
union in a `SKILL.md`:
- `SPEC_KEYS = {name, description, license, compatibility, metadata, allowed-tools}`
- `HOST_KEYS = {when_to_use, model, effort, context, disable-model-invocation}`

R1.2 **`metadata`.** When present, a mapping whose keys and values are all
strings. All current values pass.

R1.3 **`compatibility`.** When present, a string of 1–500 characters after
stripping.

R1.4 **`license`.** Required in every `SKILL.md`, a non-empty string (repo
policy, beyond the spec). The 13 superpowers skills gain `license: MIT` and

```yaml
metadata:
  author: 'Jesse Vincent'
  adapted_by: 'Lowell Mason'
  source: 'https://github.com/obra/superpowers'
```

mirroring `bayesian-workflow`'s existing `author` / `adapted_by` pattern.

R1.5 **No angle brackets.** `name` and `description` contain no `<` or `>`.
Fix llm-wiki's trigger phrase `'verify <page>'` to `'verify a page'`.

R1.6 **Invocation parity with Codex.** For a `SKILL.md`, `disable-model-invocation`
must be a YAML boolean when present. A skill with `disable-model-invocation: true`
must ship `agents/openai.yaml` that parses and sets
`policy.allow_implicit_invocation: false`. Conversely, a skill whose
`agents/openai.yaml` sets that policy to `false` must set
`disable-model-invocation: true`. No skill trips this today; it exists so that
the first manual-only skill cannot auto-fire in Codex.

R1.7 **Body-length advisory.** A `SKILL.md` body (the lines after the closing
frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not
change the exit code. Today only `writing-skills` warns; splitting it is
deferred.

R1.8 **`--strict` profile.** `check_frontmatter.py --strict` additionally fails
on any `HOST_KEYS` key in a `SKILL.md`, and on a `name` containing `claude` or
`anthropic`. It is not part of the default gate. Expected result today: exactly
`bayesian-workflow`, `tune-hyperparameters`, and `tech-debt` fail. Agents and
commands are not Agent Skills and are unaffected.

R1.9 The module docstring describes the new rules and the `--strict` flag, and
CLAUDE.md's Commands section gains the `--strict` invocation with one line on
when to use it (preparing a claude.ai upload or a spec-only validator run).

### R2 — Codex-visible openings

R2.1 **Review verdict (recorded here, no rewrites).** Criterion: within its first
150 characters, a description names the skill's primary trigger, the task or
symptom it exists for, so an agent shown only that prefix would load it for its
canonical use. All 32 descriptions pass as of 2026-10-03. The closest calls are
`creative-thinking` (its quoted examples carry the "fuzzy target" trigger) and
the `clean-code` / `clean-coder` pair, whose openings both lead with editing
Python. Both pass, so neither is rewritten.

R2.2 **RED baseline micro-test for `writing-skills`.** Before any edit to
`writing-skills`, run a baseline:
- 5 reps, each a fresh agent given the current `writing-skills` description
  guidance (the control: no new wording). Each is asked to write a SKILL.md
  description for a synthetic skill that is not from this repo and has at least
  8 trigger conditions, one of them designated in the scenario as primary.
- Run from a session whose cwd was never this repo.
- A rep passes if the designated primary trigger lies within the first 150
  characters. The controller reads each output and records the verbatim
  150-character prefix.
- Record the scenario, prompts, outputs, and verdicts in
  `specs/red-baseline-description-openings-<YYYY-MM-DD>.md`, the house
  red-baseline format.

R2.3 **Edit by outcome.**
- **Baseline ≥ 4/5:** add only a factual note of 2–4 lines to `writing-skills`'
  "Token Efficiency" section. The note covers three points: Codex shortens every
  description when its listing exceeds its budget; the measured cut (156–164
  characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure
  (`codex debug prompt-input` from a directory outside any repo, reading the
  Skills list). No new rule.
- **Baseline ≤ 3/5:** also add one checklist line ("the primary trigger falls
  within the first ~150 characters") and GREEN-test it: 5 reps with the new
  wording, at least 4/5 passing, recorded in the same red-baseline file.

### R3 — Self-contained scripts

R3.1 **Inventory.** The runnable scripts are the `skills/*/scripts/*.py` files
with a `__main__` guard. There are 16. Fourteen gain a header:
- `bayesian-workflow`: `calibration_check.py`, `check_diagnostics.py`,
  `diagnose_model.py`
- `describe-critique-methodology`: `check_decoupling.py`
- `design-architecture`: `new_adr.py`
- `explore-data`: `profile.py`
- `llm-wiki`: `bootstrap_wiki.py`, `distill_sessions.py`, `distill_specs.py`,
  `lint_wiki.py`
- `recommend-probabilistic-model`: `characterize.py`
- `recommend-visualization`: `recommend.py`
- `track-model-experiments`: `compare_experiments.py`
- `writing-plans`: `deferred_stats.py`

The two `build.py` scripts (`classification-codes`, `geographic-codes`) already
conform. `tune-hyperparameters/scripts/time_series_cv.py` has no `__main__`
guard; it is a library imported into the user's code and stays header-less.
Bash scripts are out of scope.

R3.2 **Header form.** Follow the `build.py` template exactly:
- Line 1 is `#!/usr/bin/env python3`; add it where missing.
- Then a `# /// script` block with single-quoted TOML strings, a
  `requires-python`, and a `dependencies` list (`[]` for stdlib-only scripts).

R3.3 **`requires-python`.**
- Use the lowest of `'>=3.11'`, `'>=3.12'`, `'>=3.13'` under which the test suite
  covering the script passes, run with `uv run --python 3.X` and that suite's
  CLAUDE.md dependencies.
- Scripts covered by one suite share its floor, unless a failure is attributable
  to one script, which then alone takes the higher floor.
- Prose floors that disagree with the header are aligned or removed (e.g.
  "Python ≥ 3.9" in `recommend-probabilistic-model` and `recommend-visualization`).
  The header and the skill's `compatibility` field become the statement of
  record.

R3.4 **`dependencies`.**
- Every third-party import, including function-level imports, is declared with a
  `>=` floor at the major version the suite currently resolves (e.g.
  `'polars>=1.0'`). No upper pins.
- Imports inside a `try` whose handler catches `ImportError` or
  `ModuleNotFoundError` are optional and may be left undeclared.
- Runtime backends that the script never imports but needs to read its inputs
  (e.g. `h5netcdf` for NetCDF) are added when R3.8's fixture run shows them
  needed.

R3.5 **Invocations.**
- Every documented invocation in `skills/**/*.md` of a path that resolves to one
  of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`,
  `python3`, `uv run --no-project --python 3.13 python`, and
  `uv run --python 3.13 --with … python`.
- Path forms in use: `<this-skill-dir>/scripts/x.py`,
  `<this-skill-dir>/../<skill>/scripts/x.py`, `$LLM_WIKI_ROOT/scripts/x.py` (the
  installed copies), `~/Projects/agent-skills/skills/llm-wiki/scripts/x.py`
  (llm-wiki's INSTALL.md), and repo-relative `skills/<skill>/scripts/build.py`.
- Each skill with such an invocation gets this sentence once, near its first
  invocation: "Without uv, run the same path with `python3` in an environment
  that has the dependencies listed in the script's header."

R3.6 **`compatibility`.** Every skill whose markdown runs a bundled script with
`uv run` declares
`compatibility: Requires uv to run bundled scripts (dependencies are declared inline); Python 3.X+.`
Here 3.X is the highest `requires-python` floor among the scripts that skill
invokes. That set includes `finishing-a-development-branch`, which runs
`writing-plans`' `deferred_stats.py`.

R3.7 **Lint, in `check_frontmatter.py`.** Each rule gets a RED test first.
- A `skills/*/scripts/*.py` file with a `__main__` guard carries a PEP 723 block
  that parses with `tomllib` and has `requires-python` and `dependencies`.
- In such a script, every non-stdlib, non-local import is declared in
  `dependencies`:
  - stdlib is detected via `sys.stdlib_module_names`;
  - local means a sibling module file in the same directory;
  - import names map to distributions through a small alias table, e.g.
    `yaml` → `pyyaml`;
  - R3.4's optional-import exemption applies.
- No skill markdown invokes a resolving bundled-script path with bare `python` or
  `python3`, including line-continued forms (`python \` followed by the path on
  the next line). A path that does not resolve to a bundled script, such as
  `writing-skills/anthropic-best-practices.md`'s teaching example
  `scripts/migrate.py`, is not flagged.
- A skill whose markdown runs a bundled script via `uv run` declares a
  `compatibility` value containing `uv`.

R3.8 **Execution proof**, one time, recorded in the plan's completion notes.
- From an empty scratch directory (a subdirectory such as `/tmp/bwprobe/`, never
  `/tmp` itself), each of the 16 scripts runs `uv run <absolute-path>` on a
  minimal real input that exercises its main code path.
- `--help` alone is enough only for a script with no input-reading path.
- The three ArviZ-reading scripts (`diagnose_model.py`, `calibration_check.py`,
  `compare_experiments.py`) each read a small saved InferenceData fixture.
- One script is also run from inside a directory holding an unrelated
  `pyproject.toml`. This proves the header isolates it from the project
  environment.

R3.9 The dependency-drift check still passes. Invocation text changes, but no
cross-skill reference is added or dropped; finishing → `writing-plans`'
`deferred_stats.py` is an existing `DEPENDENCIES` edge.

### R4 — License text travels with each skill

R4.1 **Bundled copies.** Each skill directory carries regular files (never
symlinks, which `install.py --copy` refuses) that are byte-identical to the root
license files and carry the same names:

| File | Skills | Basis |
|---|---|---|
| `LICENSE` | every skill under `skills/` | every skill contains Lowell Mason's original work or modifications |
| `LICENSE-superpowers` | the 13 superpowers skills | adapted from obra/superpowers (NOTICE) |
| `LICENSE-coding-skills` | `bayesian-workflow`, `clean-code` | NOTICE records *adapted* Mancuso Lab content (`references/jax-numerics.md`, `references/modules.md`). `tech-debt` took "only the idea" and gets no copy |
| `LICENSE-andorra` | `bayesian-workflow` | only if R4.5 finds an upstream notice |

R4.2 **Provenance lint (`build/check_provenance.py`)**, driven by one
`BUNDLED_LICENSES` table (root file → skills; `LICENSE` implied for every skill).
RED tests first.
- Every required copy exists, is a regular file, and is byte-identical to its
  root file.
- No skill directory holds a `LICENSE*` file outside its mapping.
- Every root `LICENSE*` file is mapped to at least one skill.
- The script stays stdlib-only, so its CLAUDE.md command keeps no `--with`.

R4.3 **Frontmatter** carries the license fields per R1.4.

R4.4 **Documentation.**
- NOTICE gains one paragraph near the top: each skill directory carries copies
  of the license texts that apply to it, so a single-skill install
  (`install.py --copy --skill`, or a third-party installer) keeps the notice MIT
  requires. The root files are canonical, and `check_provenance.py` enforces
  the copies.
- README's License section gains one sentence to the same effect.
- CLAUDE.md's provenance section gains the invariant and names the enforcing
  lint.

R4.5 **Andorra lookup** (a plan task).
- Locate Alexandre Andorra's original PyMC Bayesian-workflow skill and read its
  license. There are three outcomes:
  1. **A notice exists.** Add the upstream license text verbatim as root
     `LICENSE-andorra`, map it to `bayesian-workflow`, and extend NOTICE's
     `bayesian-workflow/` block with the source URL and the quoted copyright line.
  2. **Upstream declares MIT but ships no notice.** NOTICE records that, in the
     form already used for the Fonnesbeck repository. Nothing is bundled.
  3. **Upstream cannot be located.** NOTICE is unchanged and a deferred item is
     logged with what was searched.
- Never compose a copyright line that is not quoted from the source.
- The 2026-08-26 intake review (`specs/completed/skill-intake-review-2026-08-26.md`)
  already found that Andorra appears nowhere in the history of
  pymc-labs/python-analytics-skills (only Fonnesbeck and Dean commit there), so
  start the search from his own publications rather than that repository.

## Sequencing and execution constraints

Stages, in order. D is independent of C and may run alongside it.

- **A — R1.** Lands together with the 13 superpowers frontmatter additions and
  the llm-wiki fix, so the new hard rules are green on arrival.
- **B — R4.** License files, `BUNDLED_LICENSES`, the documentation, and the
  Andorra lookup.
- **C — R3.** Headers, invocations, `compatibility`, the script lint, and R3.8's
  execution proof.
- **D — R2.** The baseline micro-test and the `writing-skills` edit.

Constraints:
- **Work in a worktree.** The plan edits skills the executing session loads
  (`writing-plans`, `finishing-a-development-branch`, `writing-skills`), and
  `~/.claude/skills` resolves to the main checkout. Commit from the worktree;
  the shared checkout's branch can change under a concurrent session.
- **Stage D's micro-test** runs from a session whose cwd was never this repo;
  inherited session context voids reps otherwise.
- **State test changes as +N deltas** against the suite, never absolute totals,
  and update CLAUDE.md's per-suite counts by the same deltas.
- **Before allocating the plan id**, check `specs/plans/` on every branch
  (`git ls-tree`); ids are allocated per branch and have collided.
- **Coordinate with the in-flight JAX spec.** `specs/jax-deep-learning-skills.md`
  is being implemented on `codex/jax-deep-learning-skills` and defines three
  skills (`skills/deep-learning` is on that branch as of 2026-10-03).
  R1.4's required `license`, R3's header and invocation rules, and R4's per-skill
  license copies apply to them too. Whichever branch merges second brings the
  other's skills into conformance in the same merge, or the new lints fail on
  arrival.

## Validation and acceptance

1. Every gate in CLAUDE.md's Commands passes:
   - `check_frontmatter.py` (exit 0; the only `WARN` is `writing-skills`' body
     length)
   - `check_provenance.py`
   - `check_snippets.py skills/` (Tier 1)
   - the dependency-drift test
   - the full `build/` suite, plus every script suite whose script gained a
     header
   - `sync_runtime_assets.py --check` (no adapter change is expected)
2. `check_frontmatter.py --strict` fails on exactly `bayesian-workflow`,
   `tune-hyperparameters`, and `tech-debt`.
3. Each new lint rule has a test that failed before its implementation and
   passes after.
4. R3.8's execution proof is recorded for all 16 scripts.
5. **Cross-runtime load check**, from a directory outside any repo:
   - `gemini skills list --all` shows every skill under `skills/` as `[Enabled]`;
   - `codex debug prompt-input` lists every skill under `skills/` by name.

   This shows the new `compatibility`, `license`, and `metadata` values and the
   bundled license files break loading in neither runtime.
6. R2.2's red-baseline file exists, and `writing-skills` changed only as R2.3's
   outcome branch allows.

## Out of scope (deferred; logged to `specs/deferred_items.md` at plan completion)

- **Trigger-eval suites** (about 20 labeled queries per skill, near-miss
  negatives, train/validation split), starting with the overlapping
  data-and-modeling skills. They are expensive and need isolated sessions. They
  are also the prerequisite for any future description rewrite.
- **Distribution channels**: a Claude Code `marketplace.json`, `npx skills`,
  `gh skill`, or a Codex plugin. These are outward-facing. Plugin namespacing
  (`/plugin:skill`) also conflicts with the bare-name cross-reference invariant.
- **Codex adapters for `/deferred`, `/fix-issue`, `/license-audit`**, as
  manual-only skills with `agents/openai.yaml`. R1.6 is the groundwork.
- **Tables of contents for long `references/` files** (Anthropic's partial-read
  guidance). This needs a reliable detector first; a crude grep was not one.
- **Splitting `writing-skills`** below 500 body lines (R1.7's warning).
- **A versioning policy**: CHANGELOG, git tags, and `metadata.version` bumps.
- **Skill security scanning** (e.g. Cisco's `skill-scanner`). The repo has no CI.
- **License travel for single-file agents.** `agents/code-reviewer.md` and
  `agents/task-reviewer.md` are distilled from superpowers and install as single
  files without `LICENSE-superpowers`: the same gap R4 closes for skills.

## Sources and verification notes

- `specs/completed/agent-skills-best-practices.md`: the survey. Its Claude Code
  numbers are secondary; `specs/guides/claude-code-customization-guide.md`
  governs Claude Code facts. Its 2026-10-03 re-verification against official
  docs (at 2.1.288) landed on main via lowmason/agent-skills#19 (merge
  `c33bc99`).
- [Agent Skills specification](https://agentskills.io/specification): the six
  frontmatter fields, the `compatibility` ≤ 500 limit, and `metadata` as a
  string-to-string map.
- [Codex skills docs](https://developers.openai.com/codex/skills): the
  `agents/openai.yaml` `policy.allow_implicit_invocation` key.
- uv documentation: a script with inline metadata runs in its own environment
  even inside a project. R3.8's pyproject run verifies this rather than
  assuming it.
- Runtime measurements in "Measured baseline" were taken on 2026-10-03 with
  Gemini CLI 0.46.0 and Codex CLI 0.154.0, on this machine's installed skill set
  (93 skills in Codex's listing).
