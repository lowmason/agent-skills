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
    mo.vstack([mo.md("## Total shipments per month"), mo.ui.altair_chart(monthly_chart)])
    return


@app.cell(hide_code=True)
def q2_dip_helper(alt, pl, shipments):
    def q2_dip(by: str) -> pl.DataFrame:
        """Shipments in Q2 2024 vs Q2 2023 (year over year) and vs Q1 2024."""
        counts = (
            shipments.with_columns(
                period=pl.format(
                    "{}_Q{}",
                    pl.col("ship_date").dt.year(),
                    pl.col("ship_date").dt.quarter(),
                )
            )
            .filter(pl.col("period").is_in(["2023_Q2", "2024_Q1", "2024_Q2"]))
            .group_by(by, "period")
            .agg(n=pl.len().cast(pl.Int64))
            .collect()
            .pivot(on="period", index=by, values="n")
            .fill_null(0)
        )
        return counts.select(
            by,
            "2023_Q2",
            "2024_Q1",
            "2024_Q2",
            change_vs_2023_Q2=pl.col("2024_Q2") - pl.col("2023_Q2"),
            pct_vs_2023_Q2=(pl.col("2024_Q2") / pl.col("2023_Q2") - 1).round(3),
            change_vs_2024_Q1=pl.col("2024_Q2") - pl.col("2024_Q1"),
        ).sort("change_vs_2023_Q2")

    def dip_chart(df: pl.DataFrame, by: str, title: str):
        return (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("change_vs_2023_Q2:Q", title="Change in shipments, Q2 2024 vs Q2 2023"),
                y=alt.Y(f"{by}:N", sort="x", title=None),
                color=alt.condition(
                    alt.datum.change_vs_2023_Q2 < 0, alt.value("#c0392b"), alt.value("#2e86c1")
                ),
                tooltip=df.columns,
            )
            .properties(title=title, width="container")
        )

    return dip_chart, q2_dip


@app.cell(hide_code=True)
def q2_dip_by_port(dip_chart, mo, q2_dip):
    dip_port = q2_dip("port")
    mo.vstack(
        [
            mo.md("## Second-quarter dip by port"),
            mo.ui.altair_chart(dip_chart(dip_port, "port", "Q2 2024 vs Q2 2023 by port")),
            mo.ui.table(dip_port, selection=None),
        ]
    )
    return


@app.cell(hide_code=True)
def q2_dip_by_carrier(dip_chart, mo, q2_dip):
    dip_carrier = q2_dip("carrier_type")
    mo.vstack(
        [
            mo.md("## Second-quarter dip by carrier type"),
            mo.ui.altair_chart(
                dip_chart(dip_carrier, "carrier_type", "Q2 2024 vs Q2 2023 by carrier type")
            ),
            mo.ui.table(dip_carrier, selection=None),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
