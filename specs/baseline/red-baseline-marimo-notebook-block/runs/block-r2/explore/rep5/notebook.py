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
    ## Hypothesis: a few ports drive the Q2 dip

    The drop in shipped TEU from Q1 to Q2 comes mostly from a few ports.
    **Outcome:** three ports account for more than half of the net Q1 → Q2 TEU drop (2023 and 2024 pooled).
    """)
    return


@app.cell(hide_code=True)
def q2_teu_change_by_port(mo, pl, shipments):
    import altair as alt

    _change = (
        shipments
        .with_columns(quarter=pl.col('ship_date').dt.quarter())
        .filter(pl.col('quarter').is_in([1, 2]))
        .group_by('port')
        .agg(
            q1_teu=pl.col('teu').filter(pl.col('quarter').eq(1)).sum(),
            q2_teu=pl.col('teu').filter(pl.col('quarter').eq(2)).sum(),
        )
        .with_columns(teu_change=pl.col('q2_teu').sub(pl.col('q1_teu')))
        .sort('teu_change')
        .collect()
    )

    q2_teu_change_by_port = mo.ui.altair_chart(
        alt.Chart(_change)
        .mark_bar()
        .encode(
            x=alt.X('teu_change:Q', title='TEU change, Q2 minus Q1 (2023 + 2024)'),
            y=alt.Y('port:N', sort=alt.EncodingSortField('teu_change', order='ascending'), title=None),
            color=alt.condition(alt.datum.teu_change < 0, alt.value('#c0392b'), alt.value('#2e86c1')),
            tooltip=['port', 'q1_teu', 'q2_teu', 'teu_change'],
        )
        .properties(title='Q1 → Q2 TEU change by port', height=300)
    )
    q2_teu_change_by_port
    return (q2_teu_change_by_port,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Facts**

    - Total TEU, Q1 → Q2: 2023 went from 14,050 to 13,036 (−1,014). 2024 went from 12,991 to 9,622 (−3,369). The pooled net change is −4,383.
    - 6 of 10 ports fell, for a combined drop of −5,828. 4 ports rose, for a combined gain of +1,445.
    - The three biggest drops were Ivelholm −1,916 (3,482 → 1,566), Fennick −1,604 (3,519 → 1,915) and Brackwater −1,092 (3,728 → 2,636). Together they lost −4,612, which is 105% of the net drop and 79% of the gross drop.
    - The next ones down were Hollowmere −607, Glassford −454 and Emberly Quay −155.
    - Four ports rose: Cindervale +861, Aldermouth +324, Dovesend +195 and Juniper Reach +65.
    """)
    return


if __name__ == "__main__":
    app.run()
