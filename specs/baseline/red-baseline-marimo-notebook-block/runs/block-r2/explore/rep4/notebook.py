import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def imports():
    import altair as alt
    import marimo as mo
    import polars as pl

    return alt, mo, pl


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
    ## Hypothesis

    The second-quarter dip in shipments comes mostly from a few ports.

    **Outcome:** each port's Q2 shortfall is its Q2 shipment count minus the average count of the other three quarters, with 2023 and 2024 pooled. Three ports hold more than half of the total Q2 shortfall.
    """)
    return


@app.cell(hide_code=True)
def q2_shortfall_by_port(alt, mo, pl, shipments):
    _by_port = (
        shipments.with_columns(pl.col('ship_date').dt.quarter().alias('quarter'))
        .group_by('port')
        .agg(
            pl.col('quarter').eq(2).sum().alias('q2_shipments'),
            pl.col('quarter').ne(2).sum().truediv(3).alias('other_quarter_avg'),
        )
        .with_columns(
            pl.col('other_quarter_avg').sub(pl.col('q2_shipments')).alias('q2_shortfall')
        )
        .sort('q2_shortfall', descending=True)
        .collect()
    )
    q2_shortfall_by_port = mo.ui.altair_chart(
        alt.Chart(_by_port)
        .mark_bar()
        .encode(
            x=alt.X('q2_shortfall:Q', title='Q2 shortfall (shipments below other-quarter average)'),
            y=alt.Y('port:N', sort='-x', title=None),
            color=alt.condition(
                alt.datum.q2_shortfall > 0, alt.value('#c0392b'), alt.value('#7f8c8d')
            ),
            tooltip=[
                'port',
                'q2_shipments',
                alt.Tooltip('other_quarter_avg:Q', format='.1f'),
                alt.Tooltip('q2_shortfall:Q', format='.1f'),
            ],
        )
        .properties(width=500, height=300)
    )
    q2_shortfall_by_port
    return (q2_shortfall_by_port,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Facts

    - Shipments per quarter, 2023–2024 pooled: Q1 327, Q2 274, Q3 321, Q4 277. The other-quarter average is 308.3, so the net Q2 shortfall is 34.3 shipments.
    - The three largest port shortfalls are Ivelholm 15.0 (20 in Q2 against an average of 35.0), Fennick 13.0 (24 against 37.0) and Brackwater 11.7 (28 against 39.7). Together they make 39.7, which is 116% of the net shortfall.
    - Dovesend 4.3, Hollowmere 2.7, Emberly Quay 0.7 and Juniper Reach 0.3 also fall short.
    - Three ports ship more in Q2 than their other-quarter average: Cindervale +6.3, Aldermouth +5.3 and Glassford +1.7.
    - Shortfalls run from −6.3 to +15.0 across the 10 ports.
    """)
    return


if __name__ == "__main__":
    app.run()
