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


@app.cell
def monthly_totals(pl, shipments):
    # One row = one shipment; also carry TEU for context.
    monthly = (
        shipments.group_by(month=pl.col('ship_date').dt.truncate('1mo'))
        .agg(shipments=pl.len(), teu=pl.col('teu').sum())
        .sort('month')
        .collect()
    )
    return (monthly,)


@app.cell
def monthly_chart(alt, mo, monthly):
    mo.vstack([
        mo.md('## Total shipments per month'),
        alt.Chart(monthly)
        .mark_line(point=True)
        .encode(
            x=alt.X('month:T', title='Month'),
            y=alt.Y('shipments:Q', title='Shipments'),
            tooltip=['month:T', 'shipments:Q', 'teu:Q'],
        )
        .properties(width='container', height=300),
    ])
    return


@app.cell
def q2_dip_fn(pl, shipments):
    def q2_dip(by: str) -> pl.DataFrame:
        """Q2 shipments vs. the mean of Q1 and Q3, per year and `by` group.

        dip_pct < 0 means Q2 ran below its neighbouring quarters.
        """
        return (
            shipments.with_columns(
                year=pl.col('ship_date').dt.year(),
                quarter=pl.col('ship_date').dt.quarter(),
            )
            .filter(pl.col('quarter') <= 3)
            .group_by(by, 'year', 'quarter')
            .agg(n=pl.len())
            .collect()
            .pivot('quarter', index=[by, 'year'], values='n')
            .rename({'1': 'q1', '2': 'q2', '3': 'q3'})
            .fill_null(0)
            .with_columns(baseline=(pl.col('q1') + pl.col('q3')) / 2)
            .with_columns(
                dip_pct=((pl.col('q2') / pl.col('baseline') - 1) * 100).round(1)
            )
            .sort(by, 'year')
        )

    return (q2_dip,)


@app.cell
def imports_alt():
    import altair as alt

    return (alt,)


@app.cell
def q2_dip_by_port(alt, mo, q2_dip):
    dip_port = q2_dip('port')
    mo.vstack([
        mo.md('## Q2 dip by port\n\nQ2 shipments vs. average of Q1 and Q3, % change.'),
        alt.Chart(dip_port)
        .mark_bar()
        .encode(
            y=alt.Y('port:N', title=None),
            x=alt.X('dip_pct:Q', title='Q2 vs Q1/Q3 avg (%)'),
            yOffset='year:N',
            color='year:N',
            tooltip=['port', 'year', 'q1', 'q2', 'q3', 'dip_pct'],
        )
        .properties(width='container'),
        dip_port,
    ])
    return (dip_port,)


@app.cell
def q2_dip_by_carrier(alt, mo, q2_dip):
    dip_carrier = q2_dip('carrier_type')
    mo.vstack([
        mo.md('## Q2 dip by carrier type\n\nQ2 shipments vs. average of Q1 and Q3, % change.'),
        alt.Chart(dip_carrier)
        .mark_bar()
        .encode(
            y=alt.Y('carrier_type:N', title=None),
            x=alt.X('dip_pct:Q', title='Q2 vs Q1/Q3 avg (%)'),
            yOffset='year:N',
            color='year:N',
            tooltip=['carrier_type', 'year', 'q1', 'q2', 'q3', 'dip_pct'],
        )
        .properties(width='container'),
        dip_carrier,
    ])
    return (dip_carrier,)


if __name__ == "__main__":
    app.run()
