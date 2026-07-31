# Build tooling (`build/`) — only for `recommend-probabilistic-model`

`build/` is a citation-verification pipeline, not a project build. It exists solely to keep that skill's PML §-refs and pyprobml notebook links honest. Two gates:

- **Gate A (mechanical)** — `verify_citations.py` checks that every `PML1 §10.4` section number and `notebooks/book1/*.ipynb` path actually resolves against ground truth in `build/.scratch/`.
- **Gate B (adversarial)** — a human/agent reads the cited section to confirm it supports the claim; not automated.

`extract_structure.py` regenerates the ground truth in `build/.scratch/` from **local PDFs** (`~/Documents/Bayesian/Probabilistic Machine Learning/`) via `pdftotext`, plus the pyprobml file tree via `gh`. **`build/.scratch/` is gitignored and must never be committed** — it contains own-use extraction of CC-BY-NC-ND material.
