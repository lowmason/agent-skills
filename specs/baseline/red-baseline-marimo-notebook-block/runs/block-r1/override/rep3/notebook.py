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
    **Hypothesis.** Shipment volume drops in the second quarter.
    Outcome: April–June months sit below the other months in both 2023 and 2024.
    """)
    return


@app.cell(hide_code=True)
def shipments_per_month(alt, mo, pl, shipments):
    _monthly = (
        shipments.group_by(pl.col('ship_date').dt.truncate('1mo').alias('month'))
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
        .properties(title='Total shipments per month')
    )
    shipments_per_month
    return (shipments_per_month,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts.** 1,199 shipments over 24 months (Jan 2023 – Dec 2024).
    Monthly range 35 (Apr 2024) to 60 (Mar 2023).
    Q2 2023: 54, 55, 50 (159 total). Q2 2024: 35, 41, 39 (115 total).
    Quarter totals pooled over both years: Q1 327, Q2 274, Q3 321, Q4 277.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Hypothesis.** The second-quarter dip is concentrated in a few ports.
    Outcome: a few ports show a large Q2 drop while the rest are flat or up.

    *Dip* = Q2 shipments vs. the mean of Q1, Q3 and Q4 shipments, pooled over 2023–2024.
    """)
    return


@app.cell(hide_code=True)
def q2_dip_by_port(alt, mo, pl, shipments):
    _by_port = (
        shipments.with_columns(pl.col('ship_date').dt.quarter().alias('quarter'))
        .group_by('port', 'quarter')
        .agg(pl.len().alias('n'))
        .group_by('port')
        .agg(
            pl.col('n').filter(pl.col('quarter').eq(2)).sum().alias('q2'),
            pl.col('n').filter(pl.col('quarter').ne(2)).mean().alias('other_avg'),
        )
        .with_columns(
            pl.col('q2').truediv(pl.col('other_avg')).sub(1).mul(100).round(1).alias('dip_pct')
        )
        .sort('dip_pct')
        .collect()
    )
    q2_dip_by_port = mo.ui.altair_chart(
        alt.Chart(_by_port)
        .mark_bar()
        .encode(
            x=alt.X('dip_pct:Q', title='Q2 vs. other-quarter mean (%)'),
            y=alt.Y('port:N', sort='x', title='Port'),
            color=alt.condition(alt.datum.dip_pct < 0, alt.value('#c44e52'), alt.value('#4c72b0')),
            tooltip=['port:N', 'q2:Q', alt.Tooltip('other_avg:Q', format='.1f'), 'dip_pct:Q'],
        )
        .properties(title='Second-quarter dip by port')
    )
    q2_dip_by_port
    return (q2_dip_by_port,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts.** 10 ports. 7 are below their other-quarter mean in Q2, 3 are above.
    Largest drops: Ivelholm −42.9% (20 vs. 35.0), Fennick −35.1% (24 vs. 37.0), Brackwater −29.4% (28 vs. 39.7).
    Next: Dovesend −14.3%, Hollowmere −10.0%, Emberly Quay −2.8%, Juniper Reach −1.4%.
    Above: Glassford +7.1%, Aldermouth +13.1%, Cindervale +22.9%.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Hypothesis.** The second-quarter dip is driven by one carrier type.
    Outcome: one carrier type shows a much larger Q2 drop than the other two.

    *Dip* is defined as in the port view.
    """)
    return


@app.cell(hide_code=True)
def q2_dip_by_carrier_type(alt, mo, pl, shipments):
    _by_carrier = (
        shipments.with_columns(pl.col('ship_date').dt.quarter().alias('quarter'))
        .group_by('carrier_type', 'quarter')
        .agg(pl.len().alias('n'))
        .group_by('carrier_type')
        .agg(
            pl.col('n').filter(pl.col('quarter').eq(2)).sum().alias('q2'),
            pl.col('n').filter(pl.col('quarter').ne(2)).mean().alias('other_avg'),
        )
        .with_columns(
            pl.col('q2').truediv(pl.col('other_avg')).sub(1).mul(100).round(1).alias('dip_pct')
        )
        .sort('dip_pct')
        .collect()
    )
    q2_dip_by_carrier_type = mo.ui.altair_chart(
        alt.Chart(_by_carrier)
        .mark_bar()
        .encode(
            x=alt.X('dip_pct:Q', title='Q2 vs. other-quarter mean (%)'),
            y=alt.Y('carrier_type:N', sort='x', title='Carrier type'),
            color=alt.condition(alt.datum.dip_pct < 0, alt.value('#c44e52'), alt.value('#4c72b0')),
            tooltip=['carrier_type:N', 'q2:Q', alt.Tooltip('other_avg:Q', format='.1f'), 'dip_pct:Q'],
        )
        .properties(title='Second-quarter dip by carrier type')
    )
    q2_dip_by_carrier_type
    return (q2_dip_by_carrier_type,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts.** 3 carrier types, all below their other-quarter mean in Q2.
    Tanker −15.0% (36 vs. 42.3), container −13.7% (158 vs. 183.0), bulk −3.6% (80 vs. 83.0).
    Container makes up 158 of 274 Q2 shipments (58%).
    """)
    return


if __name__ == "__main__":
    app.run()
