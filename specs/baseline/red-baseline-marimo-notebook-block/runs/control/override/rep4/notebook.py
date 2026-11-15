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
def monthly_view(alt, mo, pl, shipments):
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
    mo.ui.altair_chart(monthly_chart)
    return


@app.cell
def q2_dip_helper(pl, shipments):
    def q2_dip(by):
        """Q2 shipments vs. the mean of the other three quarters, per year and group."""
        quarterly = (
            shipments.group_by(
                by,
                year=pl.col("ship_date").dt.year(),
                quarter=pl.col("ship_date").dt.quarter(),
            )
            .agg(shipments=pl.len())
            .collect()
        )
        return (
            quarterly.group_by(by, "year")
            .agg(
                q2=pl.col("shipments").filter(pl.col("quarter") == 2).sum(),
                other_q_mean=pl.col("shipments").filter(pl.col("quarter") != 2).mean(),
            )
            .with_columns(
                dip_pct=((pl.col("q2") / pl.col("other_q_mean") - 1) * 100).round(1)
            )
            .sort("year", "dip_pct")
        )

    return (q2_dip,)


@app.cell
def q2_dip_by_port(alt, mo, q2_dip):
    dip_by_port = q2_dip("port")
    port_chart = (
        alt.Chart(dip_by_port)
        .mark_bar()
        .encode(
            x=alt.X("dip_pct:Q", title="Q2 vs. other-quarter mean (%)"),
            y=alt.Y("port:N", sort="x", title=None),
            color=alt.condition("datum.dip_pct < 0", alt.value("#d62728"), alt.value("#2ca02c")),
            row=alt.Row("year:O", title=None),
            tooltip=["port", "year", "q2", alt.Tooltip("other_q_mean:Q", format=".1f"), "dip_pct"],
        )
        .properties(title="Second-quarter dip by port")
    )
    mo.vstack([mo.ui.altair_chart(port_chart), dip_by_port])
    return


@app.cell
def q2_dip_by_carrier(alt, mo, q2_dip):
    dip_by_carrier = q2_dip("carrier_type")
    carrier_chart = (
        alt.Chart(dip_by_carrier)
        .mark_bar()
        .encode(
            x=alt.X("dip_pct:Q", title="Q2 vs. other-quarter mean (%)"),
            y=alt.Y("carrier_type:N", sort="x", title=None),
            color=alt.condition("datum.dip_pct < 0", alt.value("#d62728"), alt.value("#2ca02c")),
            row=alt.Row("year:O", title=None),
            tooltip=["carrier_type", "year", "q2", alt.Tooltip("other_q_mean:Q", format=".1f"), "dip_pct"],
        )
        .properties(title="Second-quarter dip by carrier type")
    )
    mo.vstack([mo.ui.altair_chart(carrier_chart), dip_by_carrier])
    return


if __name__ == "__main__":
    app.run()
