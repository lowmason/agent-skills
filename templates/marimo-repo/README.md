# marimo repo kit

This kit is for a work repo that adopts marimo notebooks. marimo is a Python notebook tool. It stores each notebook as a plain `.py` file.

[marimo-pair](https://github.com/marimo-team/marimo-pair) lets a coding agent drive a live notebook. This kit adds the setup on the repo side.

You read the kit here and copy it by hand. `install.py` does not install it.

## Install

1. Create `notebooks/` at the repo root. Use the root only. Ruff reads the ignore's `notebooks/**` pattern from the folder that holds the ruff config, and that folder is the repo root. A marimo notebook in any other folder counts as scratch. Scratch is throwaway exploration work.
2. Install marimo-pair for the repo. Follow the commands in its [README](https://github.com/marimo-team/marimo-pair). This kit copies none of them.
3. Add [the ruff ignore](#the-ruff-ignore).
4. Paste the notebook block. The block is not written yet, so skip this step for now.
5. Run the tech-debt skill on each scratch `.ipynb` file. An `.ipynb` file is a Jupyter notebook. The skill's convert outcome turns a notebook worth keeping into a marimo notebook under `notebooks/`. The skill hardens or deletes the rest.

## The ruff ignore

Ruff is the Python linter. Add this table to the repo's `pyproject.toml`:

```toml
[tool.ruff.lint.per-file-ignores]
'notebooks/**' = ['B018']
```

- Add `B018` when the repo selects the B rules. marimo shows the last expression of a cell as output. Ruff reads each of those lines as a useless expression.
- Add `Q000` when the repo selects the Q rules with single inline quotes. marimo writes three lines in double quotes. They are `__generated_with = "…"`, `app = marimo.App(…)` and `if __name__ == "__main__":`. marimo writes them back on every save, so a fix never holds.
- Every other rule stays on, `I001` included. `I001` is the import-order rule. The agent fixes those findings through marimo-pair.
- The ignore matters wherever ruff runs over `notebooks/`. That means the Stop hook (`ruff-check.sh`, see [hooks/README.md](../../hooks/README.md)), pre-commit and CI. A pre-commit hook can pin a ruff version other than the one in the lockfile.
- If the table already exists, merge the line into it. A second copy of the header is invalid TOML. An older config may keep the table as `[tool.ruff.per-file-ignores]`. In `ruff.toml` it is a top-level `[per-file-ignores]` table. Merge the line into that table. A new `lint` table replaces it, and its other ignores stop working.
- In `ruff.toml` or `.ruff.toml`, the table is `[lint.per-file-ignores]`.
- Write the line in the repo's quote style.
- The ignore covers `ruff check` only. `per-file-ignores` does not reach `ruff format`.
- A formatter set to `quote-style = 'single'` rewrites marimo's three lines. marimo then writes them back on every save. Such a repo needs two more settings:
  1. Add `'notebooks/**'` to the `exclude` list under `[tool.ruff.format]`. In `ruff.toml` the table is `[format]`. Create the list if there is none. A second `exclude` key is invalid TOML. Replacing the list drops its other entries.
  2. Set `force-exclude = true` under `[tool.ruff]`. In `ruff.toml` it goes at the top level. Without `force-exclude`, ruff ignores the exclude for a file named on its command line. `ruff-fix.sh` and pre-commit name files that way.
- With both settings, `ruff format` leaves notebook files alone, cell code included.

## During a live session

Fix lint through marimo-pair. Never edit the file directly. marimo-pair changes cells through the running notebook server. A `Write` or `Edit` on the file goes around it.

## Credits

The kit is an original work by Lowell Mason under the MIT license (see [NOTICE](../../NOTICE)).

It takes ideas, and no text, from two posts by Eric Ma:

- [Agent-assisted data science with marimo](https://ericmjl.github.io/blog/2026/10/14/agent-assisted-data-science-with-marimo/)
- [How to do agentic data science](https://ericmjl.github.io/blog/2026/2/1/how-to-do-agentic-data-science/)

The kit pairs with marimo-pair (Apache-2.0). It links to marimo-pair and copies none of its text.
