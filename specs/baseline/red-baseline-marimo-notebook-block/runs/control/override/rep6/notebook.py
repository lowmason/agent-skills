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


@app.cell
def monthly_totals(pl, shipments):
    monthly = (
        shipments.group_by(month=pl.col('ship_date').dt.truncate('1mo'))
        .agg(shipments=pl.len())
        .sort('month')
        .collect()
    )
    return (monthly,)


@app.cell
def monthly_chart(alt, mo, monthly):
    _chart = (
        alt.Chart(monthly)
        .mark_line(point=True)
        .encode(
            x=alt.X('month:T', title='Month'),
            y=alt.Y('shipments:Q', title='Shipments'),
            tooltip=[alt.Tooltip('month:T', format='%b %Y'), 'shipments:Q'],
        )
        .properties(title='Total shipments per month', width='container')
    )
    mo.vstack([mo.ui.altair_chart(_chart), monthly])
    return


@app.cell
def dip_helper(pl, shipments):
    # Q2 2024 is the dip. Compare it to the prior quarter (Q1 2024)
    # and to the same quarter a year earlier (Q2 2023).
    def q2_dip(by):
        _periods = {
            'q2_2023': (2023, 2),
            'q1_2024': (2024, 1),
            'q2_2024': (2024, 2),
        }
        _year = pl.col('ship_date').dt.year()
        _quarter = pl.col('ship_date').dt.quarter()
        return (
            shipments.group_by(by)
            .agg(
                [
                    ((_year == y) & (_quarter == q)).sum().cast(pl.Int64).alias(name)
                    for name, (y, q) in _periods.items()
                ]
            )
            .with_columns(
                change_vs_q1_2024=pl.col('q2_2024') - pl.col('q1_2024'),
                pct_vs_q1_2024=(pl.col('q2_2024') / pl.col('q1_2024') - 1) * 100,
                change_vs_q2_2023=pl.col('q2_2024') - pl.col('q2_2023'),
                pct_vs_q2_2023=(pl.col('q2_2024') / pl.col('q2_2023') - 1) * 100,
            )
            .with_columns(pl.selectors.starts_with('pct_').round(1))
            .sort('change_vs_q2_2023')
            .collect()
        )

    return (q2_dip,)


@app.cell
def dip_chart_helper(alt):
    def dip_chart(df, by, title):
        return (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X('change_vs_q2_2023:Q', title='Change in shipments, Q2 2024 vs Q2 2023'),
                y=alt.Y(f'{by}:N', sort='x', title=None),
                color=alt.condition(
                    alt.datum.change_vs_q2_2023 < 0,
                    alt.value('#c0392b'),
                    alt.value('#2e86c1'),
                ),
                tooltip=[by, 'q2_2023', 'q1_2024', 'q2_2024', 'pct_vs_q2_2023', 'pct_vs_q1_2024'],
            )
            .properties(title=title, width='container')
        )

    return (dip_chart,)


@app.cell
def dip_by_port(dip_chart, mo, q2_dip):
    dip_port = q2_dip('port')
    mo.vstack([
        mo.ui.altair_chart(dip_chart(dip_port, 'port', 'Q2 2024 dip by port')),
        dip_port,
    ])
    return (dip_port,)


@app.cell
def dip_by_carrier(dip_chart, mo, q2_dip):
    dip_carrier = q2_dip('carrier_type')
    mo.vstack([
        mo.ui.altair_chart(dip_chart(dip_carrier, 'carrier_type', 'Q2 2024 dip by carrier type')),
        dip_carrier,
    ])
    return (dip_carrier,)


if __name__ == "__main__":
    app.run()
