# Utility scripts

Read this after sampling, before you write report.md.

Run these in order — each script's output feeds the next. They operate on the saved
`inference_data.nc` (backend-agnostic), so they are identical for native-NUTS and BlackJAX runs.

```bash
# 1. Run convergence + LOO + PPC checks (writes diagnostics.json)
uv run <this-skill-dir>/scripts/diagnose_model.py --idata <slug>/inference_data.nc --output <slug>/diagnostics.json

# 2. Run calibration check (writes calibration.json + pit_ecdf.png + pit_coverage.png;
#    with --loo-pit the figures are loo_pit_ecdf.png + loo_pit_coverage.png instead)
uv run <this-skill-dir>/scripts/calibration_check.py --idata <slug>/inference_data.nc --output <slug>/calibration.json --save-plots --plot-dir <slug>/

# 3. Interpret the JSON outputs into qualitative ratings + suggested next steps
uv run <this-skill-dir>/scripts/check_diagnostics.py --diagnostics <slug>/diagnostics.json --calibration <slug>/calibration.json --output <slug>/check_report.json
```

Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.

Step 3 is what powers the `report.md` Assessment lines and Suggested Next Steps section — never hand-roll those interpretations from raw R-hat / ESS / pareto-k numbers when the harness can produce them consistently.

See [scripts/](scripts/) for all available utilities.
