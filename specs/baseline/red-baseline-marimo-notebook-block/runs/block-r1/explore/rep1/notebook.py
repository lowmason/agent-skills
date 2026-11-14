import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def imports():
    import marimo as mo
    import polars as pl
    import altair as alt

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
    ## Hypothesis: a few ports drive the Q2 dip

    A few ports cause most of the second-quarter dip in shipments.
    Shortfall per port = mean quarterly TEU in Q1, Q3 and Q4, minus Q2 TEU, pooled over 2023–2024.

    **Outcome:** three ports hold more than half of the total Q2 TEU shortfall.
    """)
    return


@app.cell(hide_code=True)
def q2_shortfall_by_port(alt, mo, pl, shipments):
    _quarterly = (
        shipments
        .with_columns(pl.col('ship_date').dt.quarter().alias('quarter'))
        .group_by('port', 'quarter')
        .agg(pl.col('teu').sum().alias('teu'))
    )
    q2_shortfall = (
        _quarterly
        .group_by('port')
        .agg(
            pl.col('teu').filter(pl.col('quarter').eq(2)).sum().alias('q2_teu'),
            pl.col('teu').filter(pl.col('quarter').ne(2)).mean().alias('other_q_mean_teu'),
        )
        .with_columns(pl.col('other_q_mean_teu').sub(pl.col('q2_teu')).alias('shortfall_teu'))
        .with_columns(
            pl.col('shortfall_teu').truediv(pl.col('shortfall_teu').sum()).alias('share_of_shortfall'),
        )
        .sort('shortfall_teu', descending=True)
        .collect()
    )
    _chart = (
        alt.Chart(q2_shortfall)
        .mark_bar()
        .encode(
            x=alt.X('shortfall_teu:Q', title='Q2 shortfall (TEU, vs mean of other quarters)'),
            y=alt.Y('port:N', sort='-x', title=None),
            tooltip=[
                'port',
                alt.Tooltip('q2_teu:Q', format=',.0f'),
                alt.Tooltip('other_q_mean_teu:Q', format=',.0f'),
                alt.Tooltip('shortfall_teu:Q', format=',.0f'),
                alt.Tooltip('share_of_shortfall:Q', format='.1%'),
            ],
        )
    )
    mo.ui.altair_chart(_chart)
    return (q2_shortfall,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Facts

    - Total Q2 TEU across all ports: 22,658. Mean of Q1, Q3 and Q4: 26,158. Net shortfall: 3,500 TEU.
    - 8 of 10 ports are below their other-quarter mean in Q2. 2 are above: Cindervale (+1,022 TEU) and Aldermouth (+708 TEU).
    - Largest shortfalls: Ivelholm 1,785 TEU (51% of net), Fennick 1,476 (42%), Brackwater 880 (25%).
    - Top three combined: 4,141 TEU. That is 118% of the net shortfall and 79% of the gross shortfall (5,230 TEU, summed over the 8 ports that fell).
    - The other five ports that fell range from 90 TEU (Emberly Quay) to 435 TEU (Hollowmere).
    - Shares are of the net shortfall, so the two ports that rose make the shares add up to more than 100%.
    """)
    return


if __name__ == "__main__":
    app.run()
