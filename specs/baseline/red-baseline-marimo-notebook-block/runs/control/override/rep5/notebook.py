import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def imports():
    import marimo as mo
    import altair as alt
    import polars as pl

    return alt, mo, pl


@app.cell(hide_code=True)
def shipments(mo, pl):
    shipments = pl.scan_csv(
        mo.notebook_dir().parent / 'data' / 'shipments.csv',
        try_parse_dates=True,
    )
    return (shipments,)


@app.cell
def monthly(alt, mo, pl, shipments):
    monthly = (
        shipments.group_by(month=pl.col("ship_date").dt.truncate("1mo"))
        .agg(shipments=pl.len())
        .sort("month")
        .collect()
    )
    monthly_chart = (
        alt.Chart(monthly)
        .mark_line(point=True)
        .encode(
            x=alt.X("month:T", title="Month"),
            y=alt.Y("shipments:Q", title="Shipments"),
            tooltip=[alt.Tooltip("month:T", format="%b %Y"), "shipments:Q"],
        )
        .properties(title="Total shipments per month", width="container")
    )
    mo.vstack([mo.md("## Total shipments per month"), monthly_chart])
    return (monthly,)


@app.cell
def q2_dip_helper(pl, shipments):
    def q2_dip(by: str) -> pl.DataFrame:
        """Q2 shipment count vs. the mean of Q1 and Q3 in the same year, per `by` group."""
        counts = (
            shipments.with_columns(
                year=pl.col("ship_date").dt.year(),
                quarter=pl.col("ship_date").dt.quarter(),
            )
            .group_by(by, "year", "quarter")
            .agg(n=pl.len())
            .collect()
            .pivot(on="quarter", index=[by, "year"], values="n", sort_columns=True)
            .fill_null(0)
        )
        return (
            counts.select(
                by,
                "year",
                q2=pl.col("2"),
                baseline=(pl.col("1") + pl.col("3")) / 2,
            )
            .with_columns(change=pl.col("q2") - pl.col("baseline"))
            .with_columns(pct_change=(pl.col("change") / pl.col("baseline")).round(3))
            .sort("year", "pct_change")
        )

    return (q2_dip,)


@app.cell
def dip_by_port(alt, mo, q2_dip):
    dip_by_port = q2_dip("port")
    dip_by_port_chart = (
        alt.Chart(dip_by_port)
        .mark_bar()
        .encode(
            x=alt.X("pct_change:Q", title="Q2 vs. avg(Q1, Q3)", axis=alt.Axis(format="%")),
            y=alt.Y("port:N", sort="x", title=None),
            color=alt.condition("datum.pct_change < 0", alt.value("#c0392b"), alt.value("#7f8c8d")),
            row=alt.Row("year:O", title=None),
            tooltip=["port", "year", "q2", "baseline", "change", alt.Tooltip("pct_change:Q", format=".1%")],
        )
        .properties(title="Second-quarter dip by port")
    )
    mo.vstack([mo.md("## Second-quarter dip by port"), dip_by_port_chart, dip_by_port])
    return (dip_by_port,)


@app.cell
def dip_by_carrier(alt, mo, q2_dip):
    dip_by_carrier = q2_dip("carrier_type")
    dip_by_carrier_chart = (
        alt.Chart(dip_by_carrier)
        .mark_bar()
        .encode(
            x=alt.X("pct_change:Q", title="Q2 vs. avg(Q1, Q3)", axis=alt.Axis(format="%")),
            y=alt.Y("carrier_type:N", sort="x", title=None),
            color=alt.condition("datum.pct_change < 0", alt.value("#c0392b"), alt.value("#7f8c8d")),
            row=alt.Row("year:O", title=None),
            tooltip=["carrier_type", "year", "q2", "baseline", "change", alt.Tooltip("pct_change:Q", format=".1%")],
        )
        .properties(title="Second-quarter dip by carrier type")
    )
    mo.vstack([mo.md("## Second-quarter dip by carrier type"), dip_by_carrier_chart, dip_by_carrier])
    return (dip_by_carrier,)


if __name__ == "__main__":
    app.run()
