# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal collection of Claude Code user-level configuration, centered on [agent skills](https://code.claude.com/docs/en/skills). Skills live under `skills/` — each subdirectory is **one self-contained skill**: a `SKILL.md` plus optional `references/` (loaded on demand) and `scripts/` (executable helpers). Sibling top-level dirs hold the other config types: `agents/` (subagent definitions — the two reviewers plus `security-auditor`, the Haiku-pinned `Explore` override, `test-runner`, `debugger`, `docs-writer`), `commands/` (slash commands — `/deferred`, `/fix-issue`, `/license-audit`), `hooks/` (two categories: per-repo ruff/uv gate templates for the user's *work* repos, not wired into this repo; and `readonly-agent-guard.py`, a globally-installed `PreToolUse` hook enforcing the five read-only agents' Bash contract — see `hooks/README.md`), `rules/` (path-scoped rule files — `clean-code-python.md` loads on `**/*.py` edits via the committed `.claude/rules/` symlink). There is no application here to run — the "product" is the skill text and its bundled scripts.

Skills install into `~/.claude/skills/` (symlink or copy). This repo *is* the user's symlinked source: per-skill symlinks in `~/.claude/skills/` point at `skills/<name>` here (and `~/.claude/agents/` links into `agents/`), so edits here are live.

## Provenance is load-bearing — preserve it

Skills come from three sources with distinct attribution, all tracked in `NOTICE`. **Read `NOTICE` before moving, renaming, or substantially rewriting any skill**, and keep it in sync:

- **Lowell's originals** (MIT, `LICENSE`): `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `bls-data-context`, `recommend-probabilistic-model`, `recommend-visualization`, `track-model-experiments`, `tune-hyperparameters`, `creative-thinking`, `derive-roadmap`, `llm-wiki`, `describe-critique-methodology`, `classification-codes`, `geographic-codes`. (Sixteen — keep in sync with `NOTICE`, which is authoritative.)
- **`bayesian-workflow`** — adapted from Alexandre Andorra's PyMC skill, ported to NumPyro+JAX (MIT).
- **superpowers skills** (MIT, © 2025 Jesse Vincent, `LICENSE-superpowers`): the 13 process skills (`brainstorming`, `writing-plans`, `test-driven-development`, etc.). These were adapted from the upstream `superpowers` plugin.
- **clean-code family** — `clean-coder`, `clean-code`, and `rules/clean-code-python.md` adapt Robert C. Martin's *Clean Code* rule catalog (2008), cited by rule code only, no book prose; `clean-coder` also cites Beck's *Tidy First?*, Fowler's opportunistic refactoring, and Ousterhout's *APOSD* by idea only.

Two invariants from that adaptation that must not silently regress:
- **Cross-skill references use bare skill names** (`use the writing-plans skill`), never the upstream `superpowers:` plugin namespace.
- `recommend-probabilistic-model` **cites** Murphy's PML books (CC-BY-NC-ND) and pyprobml/dynamax (MIT) but **redistributes no book prose and bundles no PDFs**. Keep summaries in original wording with §-number citations only.

The user is meticulous about attribution and licensing — surface provenance/license implications proactively rather than assuming.

## Editing skills

When creating or editing a skill, **follow the `writing-skills` skill** — it's the meta-skill governing this repo. Key points it enforces:
- Frontmatter needs `name` + `description`; the description starts with "Use when…", is third-person, and is dense with concrete triggers (this is what drives auto-loading, so wording is functional, not decorative).
- Discipline/behavior skills are pressure-tested and their wording micro-tested against a no-guidance control before deployment; pure reference skills are not.

## Conventions

- **Python style**: Polars over pandas; single quotes over double; NumPyro + JAX (not PyMC) for Bayesian code; target Python 3.13.
- **Specs & plans**: design records live in `specs/` (retired ones in `specs/completed/`). Implementation plans go to `specs/plans/<id>-<spec-name>.md` where `<id>` is the next integer (max existing id across `specs/plans/` and `specs/plans/completed/`, +1). At completion, the plan-completion protocol (writing-plans § Plan Completion Protocol) gates leftovers past the user, marks up the plan, appends consciously-deferred work to `specs/deferred_items.md`, and retires the plan (and, when no other live plan shares it, the spec) to the `completed/` dirs.

## Build tooling (`build/`) — only for `recommend-probabilistic-model`

`build/` is a citation-verification pipeline, not a project build; see `build/CLAUDE.md` for its two gates and how the ground truth is regenerated. **`build/.scratch/` is gitignored and must never be committed** — it contains own-use extraction of CC-BY-NC-ND material.

## Commands

There is no root test runner or repo-wide `pyproject`, and the scientific deps (numpy, polars, pytest) aren't installed into the interpreter directly. Run everything through `uv run` pinned to the Homebrew Python 3.13, supplying deps inline. Tests use **bare imports** and are **directory-scoped** — run pytest from inside the relevant directory, not the repo root: each suite pins its own inline deps, and a repo-root collection fails outright anyway, since `geographic-codes` and `classification-codes` both ship a `test_build.py` whose basenames collide under pytest's prepend import mode with no `__init__.py`.

```bash
# Build-tooling tests (citation verifier + lints) — 43 tests
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q

# recommend-probabilistic-model signal-extractor tests — 10 tests
cd skills/recommend-probabilistic-model/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# recommend-visualization router tests — 29 tests
cd skills/recommend-visualization/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# tune-hyperparameters CV-splitter tests — 6 passed, 2 skipped
# (the 2 skips are optional-dep guards: add --with scikit-learn --with optuna to run all 8;
# the PyPI name is scikit-learn, not sklearn — --with sklearn fails to install)
cd skills/tune-hyperparameters/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# track-model-experiments ledger/compare tests — 11 tests (~20–50 s depending on the uv cache; needs the full
# numpyro + NetCDF-writer chain, since the tests round-trip InferenceData to .nc)
cd skills/track-model-experiments/scripts && uv run --python 3.13 --with pytest --with numpy --with polars --with arviz --with numpyro --with h5netcdf --with h5py python -m pytest -q

# bayesian-workflow script tests (MCSE precision block + divergence-gate next steps) — 11 tests
# (4 arviz RuntimeWarnings — "invalid value encountered in scalar divide" on the constant-parameter
# fixture — are expected and not silenced)
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q

# llm-wiki bundled wiki-script tests (bootstrap + lint + session + specs distillers) —
# 243 tests (stdlib only; these are the scripts the bootstrap installs to a wiki)
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# describe-critique-methodology decoupling-check tests — 18 tests
cd skills/describe-critique-methodology/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# geographic-codes build tests (interval synthesizer, readers, referential check) — 42 tests
# (the 7 per-vintage workbook tests need sources/, which is committed)
cd skills/geographic-codes/scripts && uv run --python 3.13 --with pytest --with polars --with fastexcel python -m pytest -q

# classification-codes build tests (NAICS/SOC/Census-OCC workbook parsers, concordance link
# types, referential checks, BLS contact-email fetch guard) — 51 tests
# (fixtures are in-memory frames, so no workbook reader is needed)
cd skills/classification-codes/scripts && uv run --python 3.13 --with pytest --with polars python -m pytest -q

# explore-data profile.py tests (--json handoff contract, duplicate + quality flags) — 7 tests
# (the --json contract is recommend-visualization's input; profile.py shadows the stdlib
# `profile` module, but that's not why this cd's in — see the repo-wide reason above)
cd skills/explore-data/scripts && uv run --python 3.13 --with pytest --with polars python -m pytest -q

# design-architecture ADR-scaffolder tests (numbering, slugify, no-clobber) — 9 tests (stdlib only)
cd skills/design-architecture/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# subagent-driven-development dispatch-script tests (workspace, task-brief fences and exit
# codes, review-package, and both scripts' default-workspace output paths) — 22 tests
# (stdlib only; drives the three bash scripts as subprocesses)
cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# read-only agent guard tests (Gate A: classifier units + payload contract) — 40 tests
# (stdlib only; the contract tests run the hook through its own shebang, which is the
# system python3 — that is also the regression test for it staying 3.9-compatible.
# Gate B is the live probe: ./hooks/probe-readonly-guard.sh, which spawns claude -p)
cd hooks && uv run --python 3.13 --with pytest python -m pytest -q

# Frontmatter + provenance lints (run before committing skill changes)
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py

# Single test
cd build && uv run --python 3.13 --with pytest --with numpy --with polars \
  python -m pytest test_verify_citations.py::test_true_negative_flags_bad_refs

# End-to-end routing smoke test (no PDFs needed)
uv run --python 3.13 --with numpy --with polars python build/smoke_test.py

# Rebuild geographic-codes data/ from the pinned Census/OMB sources (network) or the sources/ cache
uv run skills/geographic-codes/scripts/build.py
uv run skills/geographic-codes/scripts/build.py --offline

# Rebuild classification-codes data/ from the pinned Census/BLS sources (network; the bls.gov
# workbooks need BLS_CONTACT_EMAIL exported) or the sources/ cache
uv run skills/classification-codes/scripts/build.py
uv run skills/classification-codes/scripts/build.py --offline

# Verify citations across the whole skill (Gate A; exit 0 = all resolve;
# chapter-fallback WARNs on stderr are non-fatal — confirm those via Gate B)
uv run --python 3.13 python build/verify_citations.py skills/recommend-probabilistic-model/

# Rebuild citation ground truth (needs local PDFs + gh; writes gitignored build/.scratch/)
uv run --python 3.13 python build/extract_structure.py
```
