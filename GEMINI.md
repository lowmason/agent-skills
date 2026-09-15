# Gemini CLI repository instructions

@./CLAUDE.md

Runtime adapters under `runtimes/` are generated artifacts. Edit the canonical
definitions in `agents/` or `commands/`, then run
`uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py`.
Never hand-edit generated adapter files.
