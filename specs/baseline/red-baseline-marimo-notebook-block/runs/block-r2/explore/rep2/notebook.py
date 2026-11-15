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
    ## Hypothesis: the Q2 dip is mostly a few ports

    The drop in shipment count in Q2 comes from a few ports, not from all of them.
    The baseline for each port is the mean of its Q1 and Q3 shipment counts, and the shortfall is baseline minus Q2, summed over 2023 and 2024.

    **Outcome:** three ports hold more than half of the total Q2 shortfall.
    """)
    return


@app.cell(hide_code=True)
def q2_shortfall_by_port(mo, pl, shipments):
    _by_quarter = (
        shipments
        .with_columns(pl.col('ship_date').dt.quarter().alias('quarter'))
        .group_by('port')
        .agg(
            pl.col('quarter').eq(1).sum().alias('q1'),
            pl.col('quarter').eq(2).sum().alias('q2'),
            pl.col('quarter').eq(3).sum().alias('q3'),
        )
        .with_columns(
            pl.col('q1').add(pl.col('q3')).truediv(2).alias('baseline'),
        )
        .with_columns(
            pl.col('baseline').sub(pl.col('q2')).alias('shortfall'),
        )
        .with_columns(
            pl.col('shortfall').truediv(pl.col('shortfall').sum()).alias('share'),
        )
        .sort('shortfall', descending=True)
        .collect()
    )

    import altair as alt

    _chart = (
        alt.Chart(_by_quarter)
        .mark_bar()
        .encode(
            x=alt.X('shortfall:Q', title='Q2 shortfall vs mean of Q1 and Q3 (shipments)'),
            y=alt.Y('port:N', sort='-x', title=None),
            color=alt.condition(
                alt.datum.shortfall > 0,
                alt.value('#c0392b'),
                alt.value('#95a5a6'),
            ),
            tooltip=[
                'port',
                'q1',
                'q2',
                'q3',
                'baseline',
                'shortfall',
                alt.Tooltip('share:Q', format='.0%'),
            ],
        )
        .properties(title='Q2 shipment shortfall by port, 2023 and 2024 combined')
    )

    q2_shortfall_by_port = mo.ui.altair_chart(_chart)
    q2_shortfall_by_port
    return (q2_shortfall_by_port,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Facts

    - There were 1,199 shipments across 10 ports, 2023–2024. Q1 had 327, Q2 had 274 and Q3 had 321. The baseline is 324, so the total Q2 shortfall is 50 shipments.
    - Ivelholm is short 17.0 (34%): 37.0 baseline, 20 in Q2.
    - Fennick is short 16.5 (33%): 40.5 baseline, 24 in Q2.
    - Brackwater is short 16.0 (32%): 44.0 baseline, 28 in Q2.
    - Together, the top three are short 49.5 of 50 (99%).
    - Dovesend and Hollowmere are short 4.5 each (9% each). Emberly Quay is short 2.0 (4%). Juniper Reach is flat at 0.
    - Three ports have more shipments in Q2 than their baseline: Glassford +0.5, Aldermouth +4.5 and Cindervale +5.5.
    """)
    return


if __name__ == "__main__":
    app.run()
