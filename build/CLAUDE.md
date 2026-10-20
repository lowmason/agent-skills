# Build tooling (`build/`)

This directory holds the repo's lints and commit gates (each `check_*.py`
documents itself in its docstring), the cross-runtime adapter generator, the
Claude Code guide's drift detector (`cc_guide/`), and a citation-verification
pipeline. The root `CLAUDE.md` lists their commands.

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

`run_commit_lints.sh` runs the nine commit lints that the root `CLAUDE.md`
lists and fails closed. `githooks/pre-commit` runs it as a git hook, failing
open only when uv cannot run, and `../.github/workflows/lints.yml` runs it in
CI. `test_commit_lints.py` drives the runner and hook through throwaway
clones and checks the workflow's triggers and pins.

`suites.toml` registers every directory-scoped pytest suite, and
`run_suites.py` lists, runs and checks them; its docstring gives the options.
`run_suites.py --check` is a commit lint: it fails when a directory that holds
pytest files is not registered, so a new suite adds its `[[suite]]` entry in
the same change.

`cc_guide/` holds two tools for `specs/guides/claude-code-customization-guide.md`.
`conformance.toml` is the register `check_conformance.py` reads. The rest is
the drift detector (`specs/claude-code-drift-automation-spec.md`): `manifest.toml`
is the owner's configuration, `baseline.json` its state, written only by
`cli.py baseline`, and `cli.py --help` lists the subcommands. `check` fetches
the docs into `~/.cache/agent-skills/cc-guide/`, never into the repo, and
reads `main`'s commit unless given `--ref` or `--worktree`. After reviewing
what it reports, record the review in this order: `baseline accept`,
`baseline rebaseline`, `baseline advance`, `baseline audited` for an audited
group, then `baseline stamp`; then run `cli.py lint` and
`check_conformance.py`. A listed `rebaseline` refuses while an unlisted
baselined block on the same page has also changed or gone: list it too, or
rebaseline the whole page. `settle` prints each `rebaseline` with `--head`
and the packet's head, which refuses once a later `check` (a session start's
`refresh` included) has refetched the docs. A missing page needs a
`manifest.toml` edit first. When a merge brings in a `baseline.json` that the
parser before the spec's R3.2 MDX rewrite wrote, take that file and run
`baseline rehash`. A second run changes nothing.
A correction that resolves a conformance gap removes its `[[exception]]`, or
narrows its `artifacts`, in the same change. Files whose correctness rests
on a Claude Code fact carry a citation comment naming the guide sections
they rely on (the spec's R4.1 gives its form and place); `cli.py lint` checks
each one and prints `STALE` for a file reviewed before a cited section last
changed. After reviewing such a file, `cli.py baseline cite <file>` restamps
it. The `/cc-guide` skill in `../.claude/skills/` acts on what `check`
reports: `cli.py packets` writes the packets its verifier agent reads, under
the cache, and `cli.py settle` re-greps the verifier's quotes (`cli.py quotes`
checks single rows), applies the spec's fail-safe and discard rules, and
prints the corrections and the `baseline` commands that follow.
`notice.sh` is the session-start pair that `../.claude/settings.json` wires on
the `startup` matcher. `show` prints the notice `check --hook` last wrote, or
one of `refresh`'s own two error notices, once a day per notice. It prints in
the terminal; the Desktop app runs the hook and records its output but
displays nothing, and since `show` marks a notice shown when it prints, a
Desktop session that starts first on a day uses that day's showing up for the
terminal too. The async `refresh` runs `check --hook` once the last good check
is a day old, so while checks keep failing it retries at every session start.
It leaves an error notice when the check exits 2, crashes, cannot find `uv`,
or fails to finish three runs in a row; the first two unfinished runs, and a
cache that cannot be written, leave none. `notice.py` writes the notice, and
its docstring lists the cache files the shell and Python share. The notice
reads `main`, so it keeps naming work `/cc-guide` resolved until that work is
committed on `main` and the next daily check runs.
Nothing is committed for you.
`cd build && pytest` collects this suite too, so module and test basenames
stay unique across `build/`.
