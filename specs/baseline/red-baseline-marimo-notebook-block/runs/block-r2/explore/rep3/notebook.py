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
    ## Hypothesis: a few ports cause the Q2 dip

    In 2024, Q2 had 115 shipments. Q1 had 156 and Q3 had 157. The baseline for each port is the mean of its Q1 and Q3 2024 shipment counts. Its shortfall is that baseline minus its Q2 count.

    **Outcome:** three ports hold more than half of the total Q2 2024 shortfall.
    """)
    return


@app.cell(hide_code=True)
def q2_shortfall_by_port(mo, pl, shipments):
    _quarter = pl.col('ship_date').dt.quarter()
    q2_shortfall = (
        shipments
        .filter(pl.col('ship_date').dt.year().eq(2024), _quarter.is_in([1, 2, 3]))
        .group_by('port')
        .agg(
            _quarter.eq(2).sum().alias('q2_shipments'),
            _quarter.is_in([1, 3]).sum().truediv(2).alias('baseline'),
        )
        .with_columns(pl.col('baseline').sub(pl.col('q2_shipments')).alias('shortfall'))
        .with_columns(pl.col('shortfall').truediv(pl.col('shortfall').sum()).alias('share_of_net'))
        .sort('shortfall', descending=True)
        .collect()
    )

    import altair as alt

    _chart = (
        alt.Chart(q2_shortfall)
        .mark_bar()
        .encode(
            x=alt.X('shortfall:Q', title='Q2 2024 shortfall (shipments below Q1/Q3 mean)'),
            y=alt.Y('port:N', sort='-x', title=None),
            color=alt.condition(alt.datum.shortfall > 0, alt.value('#c0392b'), alt.value('#7f8c8d')),
            tooltip=['port', 'q2_shipments', 'baseline', 'shortfall', alt.Tooltip('share_of_net:Q', format='.0%')],
        )
        .properties(height=280)
    )
    mo.ui.altair_chart(_chart)
    return (q2_shortfall,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts**

    - Net shortfall across all 10 ports: 41.5 shipments (baseline 156.5, Q2 actual 115).
    - Fennick: 4 vs a baseline of 21 (−17). Ivelholm: 4 vs 19 (−15). Brackwater: 7 vs 21 (−14).
    - Those three add up to 46 shipments, which is 111% of the net shortfall.
    - Emberly Quay: −3.5. Aldermouth and Hollowmere: −0.5 each.
    - Four ports were above their baseline: Dovesend +1, Glassford +2.5, Cindervale +2.5, Juniper Reach +3. Together that is +9.
    """)
    return


if __name__ == "__main__":
    app.run()
