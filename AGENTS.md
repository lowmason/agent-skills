# Codex repository instructions

Read [`CLAUDE.md`](CLAUDE.md) completely before changing this repository. It is
the canonical maintainer guide despite its legacy runtime-specific filename;
its provenance, testing, skill-authoring, and spec-lifecycle requirements apply
equally when working in Codex.

Runtime adapters under `runtimes/` are generated artifacts. Edit the canonical
definitions in `agents/` or `commands/`, then run:

```bash
uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py
```

Never hand-edit generated adapter files. Verify them with the same command plus
`--check`.
