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
    ## Hypothesis: shipments dip in the second quarter

    Outcome: in both 2023 and 2024, the April–June monthly shipment counts sit below the counts of the other months.
    """)
    return


@app.cell(hide_code=True)
def shipments_per_month(mo, pl, shipments):
    import altair as alt

    _monthly = (
        shipments
        .group_by(pl.col('ship_date').dt.truncate('1mo').alias('month'))
        .agg(pl.len().alias('shipments'))
        .with_columns(pl.col('month').dt.quarter().eq(2).alias('q2'))
        .sort('month')
        .collect()
    )
    shipments_per_month = mo.ui.altair_chart(
        alt.Chart(_monthly)
        .mark_bar()
        .encode(
            x=alt.X('yearmonth(month):T', title='Month'),
            y=alt.Y('shipments:Q', title='Shipments'),
            color=alt.Color('q2:N', title='Q2', scale=alt.Scale(domain=[False, True], range=['#9aa5b1', '#d9534f'])),
            tooltip=[alt.Tooltip('yearmonth(month):T', title='Month'), 'shipments:Q'],
        )
        .properties(width='container', height=300)
    )
    shipments_per_month
    return alt, shipments_per_month


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts**

    - 1,199 shipments over 24 months (Jan 2023 – Dec 2024); monthly counts range from 35 (Apr 2024) to 60 (Mar 2023).
    - 2023 Q2: 54, 55, 50 (mean 53.0). 2023 other months: mean 51.4, range 41–60.
    - 2024 Q2: 35, 41, 39 (mean 38.3). 2024 other months: mean 51.3, range 43–59.
    - Both years: Q2 mean 45.7 per month, other months mean 51.4.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Hypothesis: a few ports drive the Q2 dip

    Outcome: three or fewer ports show a Q2 monthly average well below (more than 25% under) their average in other months, while the rest stay close to flat.
    """)
    return


@app.cell(hide_code=True)
def q2_dip_by_port(alt, mo, pl, shipments):
    _by_port = (
        shipments
        .with_columns(pl.col('ship_date').dt.quarter().eq(2).alias('q2'))
        .group_by('port')
        .agg(
            pl.col('q2').filter(pl.col('q2')).len().truediv(6).alias('q2_per_month'),
            pl.col('q2').filter(pl.col('q2').not_()).len().truediv(18).alias('other_per_month'),
        )
        .with_columns(pl.col('q2_per_month').truediv(pl.col('other_per_month')).sub(1).alias('q2_change'))
        .sort('q2_change')
        .collect()
    )
    q2_dip_by_port = mo.ui.altair_chart(
        alt.Chart(_by_port)
        .mark_bar()
        .encode(
            x=alt.X('q2_change:Q', title='Q2 vs other months, shipments per month', axis=alt.Axis(format='%')),
            y=alt.Y('port:N', title='Port', sort='x'),
            color=alt.condition(alt.datum.q2_change < 0, alt.value('#d9534f'), alt.value('#5b8def')),
            tooltip=[
                'port:N',
                alt.Tooltip('q2_per_month:Q', format='.2f', title='Q2 per month'),
                alt.Tooltip('other_per_month:Q', format='.2f', title='Other per month'),
                alt.Tooltip('q2_change:Q', format='.1%', title='Change'),
            ],
        )
        .properties(width='container', height=300)
    )
    q2_dip_by_port
    return (q2_dip_by_port,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts** (Q2 shipments per month vs other months, 2023–2024 combined)

    - Ivelholm −43% (3.33 vs 5.83), Fennick −35% (4.00 vs 6.17), Brackwater −29% (4.67 vs 6.61).
    - Dovesend −14%, Hollowmere −10%, Emberly Quay −3%, Juniper Reach −1%.
    - Glassford +7%, Aldermouth +13%, Cindervale +23%.
    - 7 of 10 ports are below their other-month average in Q2; 3 are above.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Hypothesis: the Q2 dip is concentrated in one carrier type

    Outcome: one carrier type's Q2 monthly average falls more than twice as far, in percent, below its other-month average as either of the other two types.
    """)
    return


@app.cell(hide_code=True)
def q2_dip_by_carrier_type(alt, mo, pl, shipments):
    _by_carrier = (
        shipments
        .with_columns(pl.col('ship_date').dt.quarter().eq(2).alias('q2'))
        .group_by('carrier_type')
        .agg(
            pl.col('q2').filter(pl.col('q2')).len().truediv(6).alias('q2_per_month'),
            pl.col('q2').filter(pl.col('q2').not_()).len().truediv(18).alias('other_per_month'),
        )
        .with_columns(pl.col('q2_per_month').truediv(pl.col('other_per_month')).sub(1).alias('q2_change'))
        .sort('q2_change')
        .collect()
    )
    q2_dip_by_carrier_type = mo.ui.altair_chart(
        alt.Chart(_by_carrier)
        .mark_bar()
        .encode(
            x=alt.X('q2_change:Q', title='Q2 vs other months, shipments per month', axis=alt.Axis(format='%')),
            y=alt.Y('carrier_type:N', title='Carrier type', sort='x'),
            color=alt.condition(alt.datum.q2_change < 0, alt.value('#d9534f'), alt.value('#5b8def')),
            tooltip=[
                'carrier_type:N',
                alt.Tooltip('q2_per_month:Q', format='.2f', title='Q2 per month'),
                alt.Tooltip('other_per_month:Q', format='.2f', title='Other per month'),
                alt.Tooltip('q2_change:Q', format='.1%', title='Change'),
            ],
        )
        .properties(width='container', height=160)
    )
    q2_dip_by_carrier_type
    return (q2_dip_by_carrier_type,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts** (Q2 shipments per month vs other months, 2023–2024 combined)

    - Tanker −15% (6.00 vs 7.06).
    - Container −14% (26.33 vs 30.50).
    - Bulk −4% (13.33 vs 13.83).
    """)
    return


if __name__ == "__main__":
    app.run()
