import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def imports():
    import polars as pl
    import marimo as mo

    return mo, pl


@app.cell(hide_code=True)
def _(mo, pl):
    shipments = pl.scan_csv(
        mo.notebook_dir().parent / 'data' / 'shipments.csv',
        try_parse_dates=True,
    )
    return (shipments,)


if __name__ == "__main__":
    app.run()
