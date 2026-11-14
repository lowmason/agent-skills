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

    The Q2 dip in shipments is mostly a few ports.

    **Outcome:** comparing Q2 with Q1 TEU (2023 and 2024 pooled), three ports hold more than half of the net drop.
    """)
    return


@app.cell(hide_code=True)
def teu_change_q1_to_q2_by_port(alt, mo, pl, shipments):
    _change = (
        shipments
        .with_columns(pl.col('ship_date').dt.quarter().alias('quarter'))
        .filter(pl.col('quarter').is_in([1, 2]))
        .group_by('port')
        .agg(
            pl.col('teu').filter(pl.col('quarter').eq(1)).sum().alias('q1_teu'),
            pl.col('teu').filter(pl.col('quarter').eq(2)).sum().alias('q2_teu'),
        )
        .with_columns(pl.col('q2_teu').sub(pl.col('q1_teu')).alias('teu_change'))
        .sort('teu_change')
        .collect()
    )
    teu_change_q1_to_q2_by_port = mo.ui.altair_chart(
        alt.Chart(_change)
        .mark_bar()
        .encode(
            x=alt.X('teu_change:Q', title='TEU change, Q2 minus Q1'),
            y=alt.Y('port:N', sort='x', title=None),
            color=alt.condition(
                alt.datum.teu_change < 0, alt.value('#c0392b'), alt.value('#7f8c8d')
            ),
            tooltip=['port', 'q1_teu', 'q2_teu', 'teu_change'],
        )
        .properties(title='TEU change from Q1 to Q2 by port, 2023–2024 pooled')
    )
    teu_change_q1_to_q2_by_port
    return (teu_change_q1_to_q2_by_port,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Facts

    - Data: 1,199 shipments, 10 ports, 2023-01-01 to 2024-12-31.
    - Total TEU: Q1 27,041, Q2 22,658. Net drop 4,383 TEU (16.2%).
    - By year: 2023 Q1→Q2 fell 1,014 TEU; 2024 Q1→Q2 fell 3,369 TEU.
    - Largest drops: Ivelholm −1,916, Fennick −1,604, Brackwater −1,092. Together −4,612, which is 105% of the net drop.
    - Six ports fell (−5,828 combined): the three above plus Hollowmere −607, Glassford −454, Emberly Quay −155.
    - Four ports rose (+1,445 combined): Cindervale +861, Aldermouth +324, Dovesend +195, Juniper Reach +65.
    - Range of change: −1,916 (Ivelholm) to +861 (Cindervale).
    """)
    return


if __name__ == "__main__":
    app.run()
