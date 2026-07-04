# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal collection of Claude Code user-level configuration, centered on [agent skills](https://code.claude.com/docs/en/skills). Skills live under `skills/` — each subdirectory is **one self-contained skill**: a `SKILL.md` plus optional `references/` (loaded on demand) and `scripts/` (executable helpers). Sibling top-level dirs hold the other config types: `agents/` (subagent definitions), `commands/` (slash commands), `hooks/` (hook scripts), `rules/` (rule files) — the latter three are scaffolding, currently empty. There is no application here to run — the "product" is the skill text and its bundled scripts.

Skills install into `~/.claude/skills/` (symlink or copy). This repo *is* the user's symlinked source: per-skill symlinks in `~/.claude/skills/` point at `skills/<name>` here (and `~/.claude/agents/` links into `agents/`), so edits here are live.

## Provenance is load-bearing — preserve it

Skills come from three sources with distinct attribution, all tracked in `NOTICE`. **Read `NOTICE` before moving, renaming, or substantially rewriting any skill**, and keep it in sync:

- **Lowell's originals** (MIT, `LICENSE`): `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `bls-data-context`, `recommend-probabilistic-model`, `recommend-visualization`.
- **`bayesian-workflow`** — adapted from Alexandre Andorra's PyMC skill, ported to NumPyro+JAX (MIT).
- **superpowers skills** (MIT, © 2025 Jesse Vincent, `LICENSE-superpowers`): the 13 process skills (`brainstorming`, `writing-plans`, `test-driven-development`, etc.). These were adapted from the upstream `superpowers` plugin.

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
- **Specs & plans**: design records live in `specs/` (retired ones in `specs/completed/`). Implementation plans go to `specs/plans/<id>-<spec-name>.md` where `<id>` is the next integer (max existing id across `specs/plans/` and `specs/plans/completed/`, +1); completed plans move to `specs/plans/completed/`.

## Build tooling (`build/`) — only for `recommend-probabilistic-model`

`build/` is a citation-verification pipeline, not a project build. It exists solely to keep that skill's PML §-refs and pyprobml notebook links honest. Two gates:

- **Gate A (mechanical)** — `verify_citations.py` checks that every `PML1 §10.4` section number and `notebooks/book1/*.ipynb` path actually resolves against ground truth in `build/.scratch/`.
- **Gate B (adversarial)** — a human/agent reads the cited section to confirm it supports the claim; not automated.

`extract_structure.py` regenerates the ground truth in `build/.scratch/` from **local PDFs** (`~/Documents/Bayesian/Probabilistic Machine Learning/`) via `pdftotext`, plus the pyprobml file tree via `gh`. **`build/.scratch/` is gitignored and must never be committed** — it contains own-use extraction of CC-BY-NC-ND material.

## Commands

There is no root test runner or repo-wide `pyproject`, and the scientific deps (numpy, polars, pytest) aren't installed into the interpreter directly. Run everything through `uv run` pinned to the Homebrew Python 3.13, supplying deps inline. Tests use **bare imports** and are **directory-scoped** — run pytest from inside the relevant directory, not the repo root:

```bash
# Build-tooling tests (citation verifier + lints) — 15 tests
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q

# recommend-probabilistic-model signal-extractor tests — 10 tests
cd skills/recommend-probabilistic-model/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# recommend-visualization router tests — 29 tests
cd skills/recommend-visualization/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# Frontmatter + provenance lints (run before committing skill changes)
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py

# Single test
cd build && uv run --python 3.13 --with pytest --with numpy --with polars \
  python -m pytest test_verify_citations.py::test_true_negative_flags_bad_refs

# End-to-end routing smoke test (no PDFs needed)
uv run --python 3.13 --with numpy --with polars python build/smoke_test.py

# Verify citations across the whole skill (Gate A; exit 0 = all resolve;
# chapter-fallback WARNs on stderr are non-fatal — confirm those via Gate B)
uv run --python 3.13 python build/verify_citations.py skills/recommend-probabilistic-model/

# Rebuild citation ground truth (needs local PDFs + gh; writes gitignored build/.scratch/)
uv run --python 3.13 python build/extract_structure.py
```
