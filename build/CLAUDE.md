# Build tooling (`build/`)

This directory holds the repo's lints and commit gates (each `check_*.py`
documents itself in its docstring), the cross-runtime adapter generator, and a
citation-verification pipeline. The root `CLAUDE.md` lists their commands.

The pipeline keeps `recommend-probabilistic-model`'s PML §-refs and pyprobml
notebook links honest, through two gates:

- **Gate A (mechanical)** — `verify_citations.py` checks that every `PML1 §10.4` section number and `notebooks/book1/*.ipynb` path actually resolves against ground truth in `build/.scratch/`.
- **Gate B (adversarial)** — a human/agent reads the cited section to confirm it supports the claim; not automated.

`extract_structure.py` regenerates the ground truth in `build/.scratch/` from **local PDFs** (`~/Documents/Bayesian/Probabilistic Machine Learning/`) via `pdftotext`, plus the pyprobml file tree via `gh`. **`build/.scratch/` is gitignored and must never be committed** — it contains own-use extraction of CC-BY-NC-ND material.

`sync_runtime_assets.py` and `test_runtime_support.py` generate and verify
Codex/Gemini adapters and the cross-runtime installer. Their canonical inputs
are `../agents/*.md` and `../commands/*.md`; never edit `../runtimes/` by hand.
`test_runtime_support.py` also scans the agent-facing text of `../skills/**`
(not READMEs or install guides) against `../install.py`'s `DEPENDENCIES`, so a
skill edit can fail it.

`cc_guide/` holds two tools for `specs/guides/claude-code-customization-guide.md`.
`conformance.toml` is the register `check_conformance.py` reads. The rest is
the drift detector (`specs/claude-code-drift-automation.md`): `manifest.toml`
is the owner's configuration, `baseline.json` its state, written only by
`cli.py baseline`, and `cli.py --help` lists the subcommands. `check` fetches
the docs into `~/.cache/agent-skills/cc-guide/`, never into the repo, and
reads `main`'s commit unless given `--worktree`. After reviewing what it
reports, record the review in this order: `baseline accept`,
`baseline rebaseline`, `baseline advance` or `baseline audited`, then
`baseline stamp`; then run `cli.py lint` and `check_conformance.py`. A
missing page needs a `manifest.toml` edit first. A correction that resolves a
conformance gap removes its `[[exception]]` in the same change. Nothing is
committed for you. `cd build && pytest` collects this suite too, so module and
test basenames stay unique across `build/`.
