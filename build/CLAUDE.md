# Build tooling (`build/`)

Most files here form a citation-verification pipeline, not a project build. It
exists to keep `recommend-probabilistic-model`'s PML §-refs and pyprobml
notebook links honest. Two gates:

- **Gate A (mechanical)** — `verify_citations.py` checks that every `PML1 §10.4` section number and `notebooks/book1/*.ipynb` path actually resolves against ground truth in `build/.scratch/`.
- **Gate B (adversarial)** — a human/agent reads the cited section to confirm it supports the claim; not automated.

`extract_structure.py` regenerates the ground truth in `build/.scratch/` from **local PDFs** (`~/Documents/Bayesian/Probabilistic Machine Learning/`) via `pdftotext`, plus the pyprobml file tree via `gh`. **`build/.scratch/` is gitignored and must never be committed** — it contains own-use extraction of CC-BY-NC-ND material.

The exception is `sync_runtime_assets.py` plus
`test_runtime_support.py`: these generate and verify Codex/Gemini adapters and
the cross-runtime installer. Their canonical inputs are `../agents/*.md` and
`../commands/*.md`; never edit `../runtimes/` by hand. `test_runtime_support.py`
also scans the agent-facing text of `../skills/**` (not READMEs or install
guides) against `../install.py`'s `DEPENDENCIES`, so a skill edit can fail it.
