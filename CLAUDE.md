# CLAUDE.md

This file is the canonical maintainer guide for Claude Code, Codex, and Gemini CLI when working in this repository. `AGENTS.md` points Codex here and `GEMINI.md` imports it.

## What this repo is

A personal collection of coding-agent configuration, centered on the portable [Agent Skills specification](https://agentskills.io/specification). Skills live under `skills/` — each subdirectory is **one self-contained skill**: a `SKILL.md` plus optional `references/` (loaded on demand) and `scripts/` (executable helpers). Sibling top-level dirs hold the other config types: `agents/` (canonical Claude-format subagent definitions), `commands/` (canonical Claude slash commands), `runtimes/` (generated Codex and Gemini adapters), `hooks/` (Claude Code hook templates and its read-only-agent guard), and `rules/` (Claude Code path-scoped rules). There is no application here to run — the "product" is the skill text, companion configuration, and bundled scripts.

`install.py` installs skills and companion assets for Claude, Codex, Gemini, or all three. Claude uses `~/.claude/skills/`; Codex and Gemini share `~/.agents/skills/`. This repo *is* the user's symlinked source, so edits here are live.

## Runtime adapters

`agents/*.md` and `commands/*.md` are canonical. Never hand-edit files under `runtimes/`. After changing a canonical agent or command, regenerate and check the adapters:

```bash
uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py
uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check
```

The generator translates manifest syntax and Gemini tool names only. Codex and Gemini agents inherit the active runtime model; Claude-specific model pins do not cross runtimes. Gemini gets TOML command adapters. Codex has no command adapter here; reusable Codex workflows are skills.

## Provenance is load-bearing — preserve it

Skills come from five sources with distinct attribution, all tracked in `NOTICE`. **Read `NOTICE` before moving, renaming, or substantially rewriting any skill**, and keep it in sync:

- **Lowell's originals** (MIT, `LICENSE`): `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `bls-data-context`, `recommend-probabilistic-model`, `recommend-visualization`, `track-model-experiments`, `tune-hyperparameters`, `creative-thinking`, `llm-wiki`, `describe-critique-methodology`, `derive-roadmap`, `classification-codes`, `geographic-codes`, `deep-learning`, `evaluate-deep-learning`, `optimize-jax`. (19 originals — keep in sync with `NOTICE`, which is authoritative.)
- **`bayesian-workflow`** — adapted from Alexandre Andorra's PyMC skill, ported to NumPyro+JAX (MIT).
- **`recommend-causal-design`** — planning workflow selectively adapted from Robson Tigre's `causal-planner` and Alexandre Andorra's `causal-inference` (MIT); newly written method references and memo contract, with both source notices in `LICENSE-causal-design-sources`.
- **superpowers skills** (MIT, © 2025 Jesse Vincent, `LICENSE-superpowers`): the 13 process skills (`brainstorming`, `writing-plans`, `test-driven-development`, etc.). These were adapted from the upstream `superpowers` plugin.
- **clean-code family** — `clean-coder`, `clean-code`, and `rules/clean-code-python.md` adapt Robert C. Martin's *Clean Code* rule catalog (2008), cited by rule code only, no book prose; `clean-coder` also cites Beck's *Tidy First?*, Fowler's opportunistic refactoring, and Ousterhout's *APOSD* by idea only.

Two invariants from that adaptation that must not silently regress:
- **Cross-skill references use bare skill names** (`use the writing-plans skill`), never the upstream `superpowers:` plugin namespace.
- `recommend-probabilistic-model` **cites** Murphy's PML books (CC-BY-NC-ND) and pyprobml/dynamax (MIT) but **redistributes no book prose and bundles no PDFs**. Keep summaries in original wording with §-number citations only.

The user is meticulous about attribution and licensing — surface provenance/license implications proactively rather than assuming.

## Editing skills and other Claude Code artifacts

Every Claude Code artifact — skill, agent, command, hook, rule, settings, installer (`install.py`), or CLAUDE.md — follows the guide sections its kind maps to in `build/cc_guide/conformance.toml`, the register for `specs/guides/claude-code-customization-guide.md`, whichever runtime does the editing. Record a departure there as a deviation or a gap only on the owner's decision, and run `check_conformance.py` (Commands) before committing.

When creating or editing a skill, **follow the `writing-skills` skill** — it's the meta-skill governing this repo. Key points it enforces:
- Frontmatter needs `name` + `description`; the description starts with "Use when…", is third-person, and is dense with concrete triggers (this is what drives auto-loading, so wording is functional, not decorative).
- Discipline/behavior skills are pressure-tested and their wording micro-tested against a no-guidance control before deployment; pure reference skills are not.

A skill's references into other skills and to commands are install dependencies; a handoff to a whole skill by name (`REQUIRED SUB-SKILL: Use …`) is not. Adding or dropping a `/command`, a `../<skill>/` or `<skill>/references/…` path, or a named section of another skill (`<skill>'s Model Selection`) must be mirrored in `install.py`'s `DEPENDENCIES` (hard: the skill cannot work without it) or in `build/test_runtime_support.py`'s `SOFT_REFERENCES` (soft, with a reason). The dependency-drift check in Commands fails on a mismatch.

## Conventions

- **Python style**: Polars over pandas; single quotes over double; NumPyro + JAX (not PyMC) for Bayesian code; target Python 3.13.
- **Specs & plans**: design records live in `specs/` (retired ones in `specs/completed/`). Implementation plans go to `specs/plans/<id>-<spec-name>.md` where `<id>` is the next integer (max existing id across `specs/plans/` and `specs/plans/completed/`, +1). At completion, the plan-completion protocol (writing-plans § Plan Completion Protocol) gates leftovers past the user, marks up the plan, appends consciously-deferred work to `specs/deferred_items.md`, and retires the plan (and, when no other live plan shares it, the spec) to the `completed/` dirs.

## Build tooling (`build/`)

`build/` holds the repo's lints and commit gates, the cross-runtime adapter generator (`sync_runtime_assets.py`), the Claude Code guide's drift detector (`cc_guide/`), and the citation-verification pipeline for `recommend-probabilistic-model`; `build/CLAUDE.md` describes each. **`build/.scratch/` is gitignored and must never be committed** — it contains own-use extraction of CC-BY-NC-ND material.

## Commands

There is no root test runner or repo-wide `pyproject`, and the scientific deps (numpy, polars, pytest) aren't installed into the interpreter directly. Run everything through `uv run` pinned to the Homebrew Python 3.13, supplying deps inline. Tests use **bare imports** and are **directory-scoped** — run pytest from inside the relevant directory, not the repo root: each suite pins its own inline deps, and a repo-root collection fails outright anyway, since `geographic-codes` and `classification-codes` both ship a `test_build.py` whose basenames collide under pytest's prepend import mode with no `__init__.py`. Comments name the extra `--with` deps that unlock a suite's skips; pytest's summary line gives the counts.

```bash
# Cross-runtime adapters, installer, and DEPENDENCIES drift
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py

# Full build-directory tests. The snippet tests that need the stack skip unless you add --with "arviz>=1.0"
# --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax --with matplotlib. A fresh clone
# or worktree lacks the gitignored build/.scratch/, so test_verify_citations.py's ground-truth tests fail or skip there
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q

# recommend-probabilistic-model signal-extractor tests
cd skills/recommend-probabilistic-model/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# recommend-visualization router tests
cd skills/recommend-visualization/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# tune-hyperparameters CV-splitter tests; its skips need --with scikit-learn --with optuna (--with sklearn fails)
cd skills/tune-hyperparameters/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# track-model-experiments ledger/compare tests (~20–50 s, depending on the uv cache). They round-trip
# InferenceData to .nc, so they need the full numpyro + NetCDF-writer chain
cd skills/track-model-experiments/scripts && uv run --python 3.13 --with pytest --with numpy --with polars --with arviz --with numpyro --with h5netcdf --with h5py python -m pytest -q

# bayesian-workflow script tests (MCSE precision, divergence-gate and calibration next steps and verdicts, figures,
# --ci-prob, --loo-pit group checks). --with matplotlib runs the figure test; CALIBRATION_SWEEP=1 runs the
# pre-registered acceptance sweep over both paths (seeds 0-99, about 1.5 min; -s prints its counts). arviz's
# "invalid value encountered in scalar divide" warnings on the constant-parameter fixture are expected, not silenced
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q

# llm-wiki bundled wiki-script tests (bootstrap, lint, session and specs distillers; stdlib only). The
# @needs_pilot tests read a pilot wiki at $LLM_WIKI_ROOT (default ~/research-wiki) and skip without one
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# describe-critique-methodology decoupling-check tests
cd skills/describe-critique-methodology/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# writing-plans deferred-backlog stats tests (stdlib only)
cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# geographic-codes build tests; the per-vintage workbook tests read the committed sources/
cd skills/geographic-codes/scripts && uv run --python 3.13 --with pytest --with polars --with fastexcel python -m pytest -q

# classification-codes build tests (fixtures are in-memory frames, so no workbook reader is needed)
cd skills/classification-codes/scripts && uv run --python 3.13 --with pytest --with polars python -m pytest -q

# explore-data profile.py tests (its --json contract is recommend-visualization's input). profile.py
# shadows the stdlib `profile` module, but the repo-wide reason above is why this cd's in
cd skills/explore-data/scripts && uv run --python 3.13 --with pytest --with polars python -m pytest -q

# design-architecture ADR-scaffolder tests (stdlib only)
cd skills/design-architecture/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# subagent-driven-development dispatch-script tests (stdlib only; they drive its bash scripts)
cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# read-only agent guard tests (Gate A: classifier units, payload contract). The guard is stdlib only and must stay
# 3.9-compatible, so run BOTH: the first runs each contract test through the hook's shebang on the test's PATH and on
# launchd's /usr/bin-first PATH (under uv run the shebang resolves to uv's pinned python); the second runs the whole
# suite under the 3.9 floor. Where /usr/bin/python3 is missing or not 3.9, the launchd-PATH runs skip (-rs shows why)
# and the floor goes untested. Gate B is the live probe, ./hooks/probe-readonly-guard.sh, which spawns claude -p
cd hooks && uv run --python 3.13 --with pytest python -m pytest -q && uv run --python /usr/bin/python3 --with pytest python -m pytest -q

# Frontmatter, provenance and guide-conformance lints (run before committing any Claude Code artifact)
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 --with pyyaml python build/check_conformance.py

# Claude Code guide drift detector (build/cc_guide/): its suite; lint, run before committing a change to the guide or
# build/cc_guide/; check, which fetches the docs and reports what is due (exit 1 = due; reads main unless --worktree)
cd build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q
uv run --python 3.13 python build/cc_guide/cli.py lint
uv run --python 3.13 python build/cc_guide/cli.py check

# Dependency drift: skill and command text vs install.py's DEPENDENCIES (run before committing a skill
# change that adds or drops a cross-skill or /command reference)
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies

# Snippet gate: three tiers, cheapest first, each including those above. Tier 1 covers all of skills/; Tiers 2 and 3
# only skills/bayesian-workflow, whose stack they import. build/check_snippets.py documents the fence markers (norun,
# noparse, fixture=<name>); named fixtures live in build/snippet_preamble.py's NAMED_FIXTURES. If a block raises
# under Tier 3, fix it: norun is for blocks that cannot run by design.
# Tier 1 (parse-only, stdlib, instant) — run before committing any skill edit:
uv run --python 3.13 python build/check_snippets.py skills/
# Tier 2 (+ resolve dotted library chains from code and backticked prose; imports the stack, ~30s):
uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax python build/check_snippets.py --api skills/bayesian-workflow/
# Tier 3 (+ execute the harnessed subset; minutes; the pins match build/snippet_preamble.py's PINNED, refresh deliberately):
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.2' --with 'arviz-plots==1.3.1' --with 'numpyro==0.21.0' --with 'jax==0.11.1' --with numpy --with matplotlib python build/check_snippets.py --run skills/bayesian-workflow/

# CPU-example process-contract tests (stdlib + pytest only). The JAX run itself is the pinned command
# below; it skips norun and noparse blocks and does not validate the surrounding prose
cd build && uv run --python 3.13 --with pytest python -m pytest -q test_check_jax_examples.py

# Verified deep-learning CPU examples (canonical Markdown blocks, no preamble), pinned by specs/verification/32-jax-cpu.in
# -> 32-jax-cpu.txt: refresh deliberately, then rerun. Hardware and checkpoint recipes in references state their own limits
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/

# Single test
cd build && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest test_verify_citations.py::test_true_negative_flags_bad_refs

# End-to-end routing smoke test (no PDFs needed)
uv run --python 3.13 --with numpy --with polars python build/smoke_test.py

# Rebuild geographic-codes data/ from the pinned Census/OMB sources (network) or the sources/ cache
uv run skills/geographic-codes/scripts/build.py
uv run skills/geographic-codes/scripts/build.py --offline

# Rebuild classification-codes data/ from the pinned Census/BLS sources (network; the bls.gov workbooks
# need BLS_CONTACT_EMAIL exported) or the sources/ cache
uv run skills/classification-codes/scripts/build.py
uv run skills/classification-codes/scripts/build.py --offline

# Verify citations across the whole skill (Gate A; exit 0 = all resolve; chapter-fallback WARNs on
# stderr are non-fatal — confirm those via Gate B)
uv run --python 3.13 python build/verify_citations.py skills/recommend-probabilistic-model/

# Rebuild citation ground truth (needs local PDFs + gh; writes gitignored build/.scratch/)
uv run --python 3.13 python build/extract_structure.py
```
