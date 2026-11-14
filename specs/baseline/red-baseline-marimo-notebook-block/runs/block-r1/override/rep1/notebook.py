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
    **Hypothesis.** Shipment volume drops in the second quarter.
    Outcome: monthly shipment counts for April to June sit below the months around them.
    """)
    return


@app.cell(hide_code=True)
def shipments_per_month(mo, pl, shipments):
    import altair as alt

    _monthly = (
        shipments
        .group_by(pl.col('ship_date').dt.truncate('1mo').alias('month'))
        .agg(pl.len().alias('shipments'))
        .sort('month')
        .collect()
    )
    shipments_per_month = mo.ui.altair_chart(
        alt.Chart(_monthly)
        .mark_line(point=True)
        .encode(
            x=alt.X('month:T', title='Month'),
            y=alt.Y('shipments:Q', title='Shipments'),
            tooltip=['month:T', 'shipments:Q'],
        )
        .properties(width='container', height=300)
    )
    shipments_per_month
    return alt, shipments_per_month


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts.**

    - 24 months, Jan 2023 to Dec 2024; 1,199 shipments in total.
    - Monthly range: 35 (Apr 2024) to 60 (Mar 2023).
    - Q2 2023 (Apr–Jun): 54, 55, 50 — 159 shipments. Q1 2023: 171. Q3 2023: 164.
    - Q2 2024 (Apr–Jun): 35, 41, 39 — 115 shipments. Q1 2024: 156. Q3 2024: 157.
    - Q4 2023 (Oct–Dec): 45, 41, 42 — 128 shipments.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Hypothesis.** The second-quarter dip comes from a few ports.
    Outcome: Q2 shipments fall well below the average of the other quarters at three or fewer ports, and sit near or above it at the rest.
    """)
    return


@app.cell(hide_code=True)
def q2_dip_by_port(alt, mo, pl, shipments):
    _by_port = (
        shipments
        .with_columns(pl.col('ship_date').dt.quarter().alias('quarter'))
        .group_by('port')
        .agg(
            pl.col('quarter').eq(2).sum().alias('q2_shipments'),
            pl.col('quarter').ne(2).sum().truediv(3).alias('other_quarter_avg'),
        )
        .with_columns(
            pl.col('q2_shipments').truediv(pl.col('other_quarter_avg')).sub(1).alias('q2_change')
        )
        .sort('q2_change')
        .collect()
    )
    q2_dip_by_port = mo.ui.altair_chart(
        alt.Chart(_by_port)
        .mark_bar()
        .encode(
            x=alt.X('q2_change:Q', title='Q2 vs average of other quarters', axis=alt.Axis(format='%')),
            y=alt.Y('port:N', title='Port', sort='x'),
            color=alt.condition(alt.datum.q2_change < 0, alt.value('#c0392b'), alt.value('#7f8c8d')),
            tooltip=['port:N', 'q2_shipments:Q', alt.Tooltip('other_quarter_avg:Q', format='.1f'), alt.Tooltip('q2_change:Q', format='.1%')],
        )
        .properties(width='container', height=300)
    )
    q2_dip_by_port
    return (q2_dip_by_port,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts.** Q2 shipments against the average of Q1, Q3 and Q4, both years pooled. Overall: 274 in Q2 against an average of 308.3, or −11.1%.

    | Port | Q2 shipments | Other-quarter average | Change |
    |---|---|---|---|
    | Ivelholm | 20 | 35.0 | −42.9% |
    | Fennick | 24 | 37.0 | −35.1% |
    | Brackwater | 28 | 39.7 | −29.4% |
    | Dovesend | 26 | 30.3 | −14.3% |
    | Hollowmere | 24 | 26.7 | −10.0% |
    | Emberly Quay | 23 | 23.7 | −2.8% |
    | Juniper Reach | 24 | 24.3 | −1.4% |
    | Glassford | 25 | 23.3 | +7.1% |
    | Aldermouth | 46 | 40.7 | +13.1% |
    | Cindervale | 34 | 27.7 | +22.9% |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Hypothesis.** The second-quarter dip is specific to one carrier type.
    Outcome: one carrier type shows a much larger Q2 drop against its other-quarter average than the other two.
    """)
    return


@app.cell(hide_code=True)
def q2_dip_by_carrier_type(alt, mo, pl, shipments):
    _by_carrier = (
        shipments
        .with_columns(pl.col('ship_date').dt.quarter().alias('quarter'))
        .group_by('carrier_type')
        .agg(
            pl.col('quarter').eq(2).sum().alias('q2_shipments'),
            pl.col('quarter').ne(2).sum().truediv(3).alias('other_quarter_avg'),
        )
        .with_columns(
            pl.col('q2_shipments').truediv(pl.col('other_quarter_avg')).sub(1).alias('q2_change')
        )
        .sort('q2_change')
        .collect()
    )
    q2_dip_by_carrier_type = mo.ui.altair_chart(
        alt.Chart(_by_carrier)
        .mark_bar()
        .encode(
            x=alt.X('q2_change:Q', title='Q2 vs average of other quarters', axis=alt.Axis(format='%')),
            y=alt.Y('carrier_type:N', title='Carrier type', sort='x'),
            color=alt.condition(alt.datum.q2_change < 0, alt.value('#c0392b'), alt.value('#7f8c8d')),
            tooltip=['carrier_type:N', 'q2_shipments:Q', alt.Tooltip('other_quarter_avg:Q', format='.1f'), alt.Tooltip('q2_change:Q', format='.1%')],
        )
        .properties(width='container', height=160)
    )
    q2_dip_by_carrier_type
    return (q2_dip_by_carrier_type,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts.** Q2 shipments against the average of Q1, Q3 and Q4, both years pooled.

    | Carrier type | Total shipments | Q2 shipments | Other-quarter average | Change |
    |---|---|---|---|---|
    | tanker | 163 | 36 | 42.3 | −15.0% |
    | container | 707 | 158 | 183.0 | −13.7% |
    | bulk | 329 | 80 | 83.0 | −3.6% |
    """)
    return


if __name__ == "__main__":
    app.run()
