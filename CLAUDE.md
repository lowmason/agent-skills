<!-- cc-guide: skills.locations @2.1.288 -->
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

Skills come from six sources with distinct attribution, and a seventh contributes to three skills, all tracked in `NOTICE`. **Read `NOTICE` before moving, renaming, or substantially rewriting any skill**, and keep it in sync:

- **Lowell's originals** (MIT, `LICENSE`): `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `bls-data-context`, `recommend-probabilistic-model`, `recommend-visualization`, `track-model-experiments`, `tune-hyperparameters`, `creative-thinking`, `llm-wiki`, `describe-critique-methodology`, `derive-roadmap`, `classification-codes`, `geographic-codes`, `deep-learning`, `evaluate-deep-learning`, `optimize-jax`, `prepare-handoff`, `document-python-package`. (21 originals — keep in sync with `NOTICE`, which is authoritative.)
- **`bayesian-workflow`** — adapted from Alexandre Andorra's PyMC skill, ported to NumPyro+JAX (MIT; upstream notice in `LICENSE-andorra`).
- **`recommend-causal-design`** — planning workflow selectively adapted from Robson Tigre's `causal-planner` and Alexandre Andorra's `causal-inference` (MIT); newly written method references and memo contract, with both source notices in `LICENSE-causal-design-sources`.
- **`write-with-asd-ste100`** and `rules/write-with-asd-ste100.md` — adapted from danyuchn's `asd-ste100-skill` and prithivrajmu's `asd-ste100` (MIT), with both notices in `LICENSE-write-with-asd-ste100-sources`; `scripts/ste-lint.py` is danyuchn's linter, copied unchanged, the one file exempt from the repo's Python style.
- **superpowers skills** (MIT, © 2025 Jesse Vincent, `LICENSE-superpowers`): the 13 process skills (`brainstorming`, `writing-plans`, `test-driven-development`, etc.). These were adapted from the upstream `superpowers` plugin.
- **clean-code family** — `clean-coder`, `clean-code`, and `rules/clean-code-python.md` adapt Robert C. Martin's *Clean Code* rule catalog (2008), cited by rule code only, no book prose; `clean-coder` also cites Beck's *Tidy First?*, Fowler's opportunistic refactoring, and Ousterhout's *APOSD* by idea only.
- **Mancuso Lab's `coding-skills`** (MIT, © 2026 Mancuso Lab, `LICENSE-coding-skills`) — contributes to three skills: `bayesian-workflow`'s `references/jax-numerics.md` and `clean-code`'s Modules rules (M1–M4, `references/modules.md`) adapt its rules, and `tech-debt`'s "Unguarded join cardinality" signal takes only the idea of one.

Two invariants from that adaptation that must not silently regress:
- **Cross-skill references use bare skill names** (`use the writing-plans skill`), never the upstream `superpowers:` plugin namespace.
- `recommend-probabilistic-model` **cites** Murphy's PML books (CC-BY-NC-ND) and pyprobml/dynamax (MIT) but **redistributes no book prose and bundles no PDFs**. Keep summaries in original wording with §-number citations only.

The user is meticulous about attribution and licensing — surface provenance/license implications proactively rather than assuming. Each skill directory carries byte-identical copies of the root license files that apply to it (`LICENSE` in every skill, the rest per `BUNDLED_LICENSES` in `build/check_provenance.py`, which enforces the copies), so edit a root license file and its copies together.

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

There is no repo-wide `pyproject`, and the scientific deps (numpy, polars, pytest) aren't installed into the interpreter directly. Run everything through `uv run` pinned to the Homebrew Python 3.13, supplying deps inline. Tests use **bare imports** and are **directory-scoped** — each suite runs pytest from inside its own directory with its own inline deps, never from the repo root: a repo-root collection fails outright, since `geographic-codes` and `classification-codes` both ship a `test_build.py` whose basenames collide under pytest's prepend import mode with no `__init__.py`. `build/suites.toml` registers each suite (its directory, its `--with` deps, the extras that unlock its skips, and its notes), and `build/run_suites.py` runs them, printing a suite's notes before its output; pytest's summary line gives the counts.

```bash
# Cross-runtime adapters, installer, and DEPENDENCIES drift
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py

# Directory suites (build/suites.toml): --list prints each suite's exact command, extras and notes; name one or more
# suites to run them (--extras adds the deps that unlock skips; arguments after -- go to pytest, e.g. a test node ID),
# or --all for every suite. --check, a commit lint, fails when a directory holding tests is not registered
uv run --python 3.13 python build/run_suites.py --list
uv run --python 3.13 python build/run_suites.py <name> [--extras] [-- <pytest args>]
uv run --python 3.13 python build/run_suites.py --all
uv run --python 3.13 python build/run_suites.py --check

# Commit lints: these three, the suite-registry check (run_suites.py --check, above), the dependency-drift test,
# snippet Tier 1, sync_runtime_assets.py --check, the drift lint (cli.py lint, below) and the placement tests (below)
# make nine. build/run_commit_lints.sh runs all nine; build/githooks/pre-commit runs it on each commit once enabled
# (an owner step: git config core.hooksPath build/githooks writes repo config every worktree reads); the hook lints
# the working tree, untracked drafts included except by the drift lint, which reads tracked files only.
# .github/workflows/lints.yml runs them on PRs and main as an advisory check; the hook is the gate.
# Frontmatter, provenance and guide-conformance lints (run before committing any Claude Code artifact); add --strict to the first, a report and not a gate, when preparing a claude.ai upload or a spec-only validator run
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 --with pyyaml python build/check_conformance.py

# Commit-lint runner, hook and workflow tests: the clean and refusal tests run the full lint set in clones (about 15 s warm)
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py

# Claude Code guide drift detector (build/cc_guide/): suite cc_guide; lint, run before committing a change to the guide, to
# build/cc_guide/ or to a file carrying a citation (its STALE lines never fail it); check, which fetches the docs and
# reports what is due (exit 1 = due; reads main unless --worktree); /cc-guide acts on what it reports; a SessionStart
# hook (build/cc_guide/notice.sh) runs check --hook once the last good check is a day old; its notice shows in terminal sessions only
uv run --python 3.13 python build/cc_guide/cli.py lint
uv run --python 3.13 python build/cc_guide/cli.py check

# Live probes (spec R10): binaries lists the claude binaries installed; probes runs the due probes against the one named
# (about $0.05-0.30 each), appends rows to build/cc_guide/PROBES.md and commits nothing; /cc-guide probes drives both
uv run --python 3.13 python build/cc_guide/cli.py binaries
uv run --python 3.13 python build/cc_guide/cli.py probes --claude <path>

# Dependency drift: skill and command text vs install.py's DEPENDENCIES (run before committing a skill
# change that adds or drops a cross-skill or /command reference)
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies

# Critical-section placement: compaction-window exceptions waive per file, heading findings included, so these tests
# pin the critical sections of two skills (CRITICAL_SPANS) and the late headings the owner accepted in writing-skills
# (ACKNOWLEDGED_LATE), both in test_check_conformance.py. Removing an exception removes its files' rows; when the last
# compaction-window exception goes, retire this lint and these tests with it
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill

# Snippet gate: three tiers, cheapest first, run as three separate commands. Every command runs the parse check, but
# --run does not run the --api checks, so a full check runs all three. Tier 1 covers all of skills/; Tiers 2 and 3
# only skills/bayesian-workflow, whose stack they import. build/check_snippets.py documents the fence markers (norun,
# noparse, fixture=<name>); named fixtures live in build/snippet_preamble.py's NAMED_FIXTURES. If a block raises
# under Tier 3, fix it: norun is for blocks that cannot run by design.
# Tier 1 (parse-only, stdlib, instant) — run before committing any skill edit:
uv run --python 3.13 python build/check_snippets.py skills/
# Tier 2 (--api: also resolve dotted library chains from code and backticked prose; imports the stack, ~30s):
uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax python build/check_snippets.py --api skills/bayesian-workflow/
# Tier 3 (--run: also execute the harnessed subset, without the Tier 2 checks; minutes; the pins match build/snippet_preamble.py's PINNED, refresh deliberately):
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.3' --with 'arviz-plots==1.3.2' --with 'numpyro==0.22.0' --with 'jax==0.12.0' --with numpy --with matplotlib python build/check_snippets.py --run skills/bayesian-workflow/

# CPU-example process-contract tests (stdlib + pytest only). The JAX run itself is the pinned command
# below; it skips norun and noparse blocks and does not validate the surrounding prose
cd build && uv run --python 3.13 --with pytest python -m pytest -q test_check_jax_examples.py

# Verified deep-learning CPU examples (canonical Markdown blocks, no preamble), pinned by specs/verification/32-jax-cpu.in
# -> 32-jax-cpu.txt: refresh deliberately, then rerun. Hardware and checkpoint recipes in references state their own limits
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/

# Single test
cd build && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest test_verify_citations.py::test_missing_scratch_exits_2_with_actionable_message

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
