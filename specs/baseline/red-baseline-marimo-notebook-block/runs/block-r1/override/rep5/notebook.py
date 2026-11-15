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
    ## Shipments per month

    **Hypothesis.** Shipment volume drops in the second quarter.
    **Outcome:** monthly shipment counts for April–June sit below the other months of the same year.
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
    **Facts.** 1,199 shipments, 2023-01-01 to 2024-12-31 (24 months).

    - Monthly counts range from 35 (Apr 2024) to 60 (Mar 2023).
    - 2023: Q2 months are 54, 55, 50. Q2 total is 159 vs. a 154.3 average for the other quarters (+3.0%).
    - 2024: Q2 months are 35, 41, 39. Q2 total is 115 vs. a 154.0 average for the other quarters (−25.3%).
    - Q4 2023 is also low: 45, 41, 42.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Second-quarter dip by port

    **Hypothesis.** The Q2 dip is concentrated in a few ports.
    **Outcome:** for each port and year, Q2 shipments compared with the average of the other three quarters. A few ports show a large negative gap and the rest stay near zero.
    """)
    return


@app.cell(hide_code=True)
def q2_dip_by_port(alt, mo, pl, shipments):
    _by_port = (
        shipments
        .with_columns(
            pl.col('ship_date').dt.year().alias('year'),
            pl.col('ship_date').dt.quarter().eq(2).alias('q2'),
        )
        .group_by('port', 'year')
        .agg(
            pl.col('q2').sum().alias('q2_shipments'),
            pl.col('q2').not_().sum().truediv(3).alias('other_quarter_avg'),
        )
        .with_columns(
            pl.col('q2_shipments')
            .truediv(pl.col('other_quarter_avg'))
            .sub(1)
            .alias('q2_vs_other'),
        )
        .sort('port', 'year')
        .collect()
    )
    q2_dip_by_port = mo.ui.altair_chart(
        alt.Chart(_by_port)
        .mark_bar()
        .encode(
            y=alt.Y('port:N', title='Port', sort='x'),
            x=alt.X('q2_vs_other:Q', title='Q2 vs. other-quarter average', axis=alt.Axis(format='%')),
            yOffset='year:N',
            color=alt.Color('year:N', title='Year'),
            tooltip=[
                'port:N',
                'year:N',
                'q2_shipments:Q',
                alt.Tooltip('other_quarter_avg:Q', format='.1f'),
                alt.Tooltip('q2_vs_other:Q', format='.1%'),
            ],
        )
        .properties(width='container', height=400)
    )
    q2_dip_by_port
    return (q2_dip_by_port,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts.** There are 10 ports. Each cell below is Q2 shipments vs. the other-quarter average, with the percentage gap.

    | Port | 2023 | 2024 |
    |---|---|---|
    | Fennick | 20 vs 17.3 (+15.4%) | 4 vs 19.7 (−79.7%) |
    | Ivelholm | 16 vs 17.0 (−5.9%) | 4 vs 18.0 (−77.8%) |
    | Brackwater | 21 vs 20.3 (+3.3%) | 7 vs 19.3 (−63.8%) |
    | Emberly Quay | 13 vs 11.3 (+14.7%) | 10 vs 12.3 (−18.9%) |
    | Aldermouth | 25 vs 18.7 (+33.9%) | 21 vs 22.0 (−4.5%) |
    | Dovesend | 11 vs 15.0 (−26.7%) | 15 vs 15.3 (−2.2%) |
    | Hollowmere | 12 vs 14.7 (−18.2%) | 12 vs 12.0 (0.0%) |
    | Cindervale | 17 vs 13.0 (+30.8%) | 17 vs 14.7 (+15.9%) |
    | Glassford | 13 vs 13.0 (0.0%) | 12 vs 10.3 (+16.1%) |
    | Juniper Reach | 11 vs 14.0 (−21.4%) | 13 vs 10.3 (+25.8%) |

    - Fennick, Ivelholm and Brackwater sum to 15 Q2 shipments in 2024, against 57 in 2023.
    - The per-port counts are small (4–25 per quarter).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Second-quarter dip by carrier type

    **Hypothesis.** The Q2 dip is concentrated in one carrier type.
    **Outcome:** for each carrier type and year, Q2 shipments compared with the average of the other three quarters. One carrier type shows a much larger negative gap than the others.
    """)
    return


@app.cell(hide_code=True)
def q2_dip_by_carrier_type(alt, mo, pl, shipments):
    _by_carrier = (
        shipments
        .with_columns(
            pl.col('ship_date').dt.year().alias('year'),
            pl.col('ship_date').dt.quarter().eq(2).alias('q2'),
        )
        .group_by('carrier_type', 'year')
        .agg(
            pl.col('q2').sum().alias('q2_shipments'),
            pl.col('q2').not_().sum().truediv(3).alias('other_quarter_avg'),
        )
        .with_columns(
            pl.col('q2_shipments')
            .truediv(pl.col('other_quarter_avg'))
            .sub(1)
            .alias('q2_vs_other'),
        )
        .sort('carrier_type', 'year')
        .collect()
    )
    q2_dip_by_carrier_type = mo.ui.altair_chart(
        alt.Chart(_by_carrier)
        .mark_bar()
        .encode(
            y=alt.Y('carrier_type:N', title='Carrier type'),
            x=alt.X('q2_vs_other:Q', title='Q2 vs. other-quarter average', axis=alt.Axis(format='%')),
            yOffset='year:N',
            color=alt.Color('year:N', title='Year'),
            tooltip=[
                'carrier_type:N',
                'year:N',
                'q2_shipments:Q',
                alt.Tooltip('other_quarter_avg:Q', format='.1f'),
                alt.Tooltip('q2_vs_other:Q', format='.1%'),
            ],
        )
        .properties(width='container', height=200)
    )
    q2_dip_by_carrier_type
    return (q2_dip_by_carrier_type,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts.** There are 3 carrier types. Each cell below is Q2 shipments vs. the other-quarter average, with the percentage gap.

    | Carrier type | 2023 | 2024 |
    |---|---|---|
    | container | 92 vs 90.7 (+1.5%) | 66 vs 92.3 (−28.5%) |
    | tanker | 23 vs 19.0 (+21.1%) | 13 vs 23.3 (−44.3%) |
    | bulk | 44 vs 44.7 (−1.5%) | 36 vs 38.3 (−6.1%) |

    - In 2024, container shipments are 26.3 below their other-quarter average, tanker 10.3 below and bulk 2.3 below.
    """)
    return


if __name__ == "__main__":
    app.run()
