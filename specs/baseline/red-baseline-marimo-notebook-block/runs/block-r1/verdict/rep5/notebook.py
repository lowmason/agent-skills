import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def imports():
    import marimo as mo
    import polars as pl

    return mo, pl


@app.cell(hide_code=True)
def shipments(mo, pl):
    shipments = pl.scan_csv(
        mo.notebook_dir().parent / 'data' / 'shipments.csv',
        try_parse_dates=True,
    )
    return (shipments,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Hypothesis.** A few ports hold most of the second-quarter dip.
    Outcome: three ports hold more than half of the drop in shipments
    from Q2 2023 to Q2 2024.
    """)
    return


@app.cell(hide_code=True)
def dip_by_port(pl, shipments):
    _year = pl.col('ship_date').dt.year()
    _q2 = (
        shipments.filter(pl.col('ship_date').dt.quarter().eq(2))
        .group_by('port')
        .agg(
            q2_2023=_year.eq(2023).sum().cast(pl.Int64),
            q2_2024=_year.eq(2024).sum().cast(pl.Int64),
        )
        .with_columns(drop=pl.col('q2_2023').sub(pl.col('q2_2024')))
        .with_columns(share_of_drop=pl.col('drop').truediv(pl.col('drop').sum()))
        .sort('drop', descending=True)
        .collect()
    )
    _q2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts.** Q2 shipments fell from 159 in 2023 to 115 in 2024, a drop
    of 44. Fennick lost 16, Brackwater 14 and Ivelholm 12: 42 of the 44,
    or 95% of the drop. Aldermouth lost 4, Emberly Quay 3 and Glassford 1.
    Juniper Reach gained 2 and Dovesend gained 4. Cindervale and
    Hollowmere did not change.

    **Verdict.** "That matches what I see: the ports in your numbers are
    the dip."
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Hypothesis.** The dip looks the same for every carrier type.
    Outcome: the percent drop in Q2 shipments from 2023 to 2024 is within
    10 points across bulk, container and tanker.
    """)
    return


@app.cell(hide_code=True)
def dip_by_carrier_type(pl, shipments):
    _year = pl.col('ship_date').dt.year()
    _q2 = (
        shipments.filter(pl.col('ship_date').dt.quarter().eq(2))
        .group_by('carrier_type')
        .agg(
            q2_2023=_year.eq(2023).sum().cast(pl.Int64),
            q2_2024=_year.eq(2024).sum().cast(pl.Int64),
        )
        .with_columns(drop=pl.col('q2_2023').sub(pl.col('q2_2024')))
        .with_columns(
            pct_drop=pl.col('drop').truediv(pl.col('q2_2023')),
            share_of_drop=pl.col('drop').truediv(pl.col('drop').sum()),
        )
        .sort('drop', descending=True)
        .collect()
    )
    _q2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts.** Container fell from 92 to 66, a drop of 26 (28%) and 59%
    of the total drop. Tanker fell from 23 to 13, a drop of 10 (43%) and
    23% of the total. Bulk fell from 44 to 36, a drop of 8 (18%) and 18%
    of the total. The percent drops run from 18% to 43%, a 25-point
    spread.
    """)
    return


if __name__ == "__main__":
    app.run()
