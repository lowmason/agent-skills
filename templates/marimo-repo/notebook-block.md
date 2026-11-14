<!-- marimo-repo:start -->
## Notebooks

Notebooks are marimo notebooks in `notebooks/`. marimo-pair drives a live session.
During a live session, change cells only through marimo-pair. This includes lint fixes.
Never use `Write` or `Edit` on a notebook file then.

### Exploration loop

Exploration means testing a hypothesis with a view. Converting, fixing lint, refactoring and tidying run normally.

1. The user names a hunch, or asks for candidates and picks one.
2. Restate the hunch as a hypothesis with an observable outcome, in the hypothesis cell.
3. In the same turn, build one view in one named code cell. Run it. Write the facts cell. End the turn.
4. The user reads the view and gives a verdict.
5. The user picks the next hypothesis or stops.

Until the user gives a verdict, build no second view, fit no model and state no conclusion. When the user asks outright for more, do what the user asks.

### Cells around a view

- The hypothesis cell is the markdown cell before the view. It holds the hypothesis and its observable outcome. Example: "A few plans cause most of the churn. Outcome: three plans hold more than half of it."
- The facts cell is the markdown cell after the view. It holds the numbers that the view shows, such as counts, shares and ranges. It does not say whether the outcome was met.
- After the user gives a verdict, add it to the facts cell in the user's words.

### Cell style

- **Cells.** Name each code cell for what it shows, for example `churn_by_plan`. Leave markdown cells unnamed. Keep `hide_code=True`.
- **Polars.** Use Polars, not pandas. Use method-style expressions: `pl.col('x').gt(0)`. Scan lazily. Each view cell collects its own small frame. Use single quotes in cell code. Leave the three lines that marimo writes as marimo writes them.
- **Charts.** Use `mo.ui.altair_chart` for interactive charts. The recommend-visualization skill picks the chart.
<!-- marimo-repo:end -->
