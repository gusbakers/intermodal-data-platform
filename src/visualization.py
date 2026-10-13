"""Four exportable figures derived from the included shipment dataset."""

from math import ceil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

NAVY, BLUE, TEAL, AMBER = "#132b45", "#247bd1", "#0d9488", "#e89729"


def _canvas(title: str, subtitle: str, *, size=(11, 6)):
    figure, axis = plt.subplots(figsize=size)
    figure.patch.set_facecolor("#f8fafc")
    axis.set_facecolor("#f8fafc")
    for side in ["top", "right", "left"]:
        axis.spines[side].set_visible(False)
    axis.spines["bottom"].set_color("#cbd5e1")
    axis.tick_params(colors=NAVY, length=0, labelsize=11)
    axis.set_axisbelow(True)
    axis.grid(axis="x", alpha=0.15)
    figure.suptitle(title, x=0.1, y=0.96, ha="left", fontsize=21, fontweight="bold", color=NAVY)
    figure.text(0.1, 0.88, subtitle, fontsize=11, color="#526579")
    figure.subplots_adjust(left=0.1, right=0.94, top=0.8, bottom=0.15)
    return figure, axis


def _save(figure, directory: Path, name: str) -> None:
    figure.savefig(directory / name, dpi=160, facecolor=figure.get_facecolor())
    plt.close(figure)


def create_charts(frame: pd.DataFrame, tables: dict[str, pd.DataFrame], directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    mode = tables["mode_performance"].sort_values("dominant_mode")
    figure, axis = _canvas(
        "Delivery reliability by transport mode", "On-time = actual duration does not exceed planned duration"
    )
    bars = axis.barh(mode.dominant_mode, mode.on_time_pct, color=[BLUE, TEAL, NAVY])
    axis.set_xlim(0, 110)
    axis.xaxis.set_major_formatter(PercentFormatter(100))
    axis.set_xlabel("On-time shipments (%)", color=NAVY, labelpad=10)
    for bar, (_, row) in zip(bars, mode.iterrows(), strict=True):
        axis.text(
            bar.get_width() + 2,
            bar.get_y() + bar.get_height() / 2,
            f"{row.on_time_pct:.1f}%  |  n={int(row.total_shipments):,}",
            va="center",
            color=NAVY,
            fontsize=11,
        )
    _save(figure, directory, "01_on_time_by_mode.png")

    figure, axis = _canvas(
        "Planned versus actual transport duration",
        f"{len(frame):,} shipments in 10-hour bins; bins with fewer than 20 shipments are hidden",
    )
    maximum = ceil(max(frame.actual_duration_hours.max(), frame.planned_duration_hours.max()) / 10) * 10
    bins = list(range(0, maximum + 10, 10))
    histogram = axis.hist2d(
        frame.planned_duration_hours,
        frame.actual_duration_hours,
        bins=[bins, bins],
        cmin=20,
        cmap="Blues",
    )
    figure.colorbar(histogram[3], ax=axis, label="Shipments per 10-hour bin", pad=0.03)
    axis.plot(
        [0, maximum], [0, maximum], color=NAVY, linestyle="--", linewidth=1.5, label="On-schedule reference"
    )
    axis.set_xlim(0, maximum)
    axis.set_ylim(0, maximum)
    axis.set_xlabel("Planned duration (hours)", color=NAVY)
    axis.set_ylabel("Actual duration (hours)", color=NAVY)
    axis.legend(frameon=False, loc="upper left")
    _save(figure, directory, "02_planned_vs_actual.png")

    figure, axis = _canvas(
        "Fuel cost per kilometre",
        "Weighted metric: total fuel cost / total distance | fuel only, not total operating cost",
    )
    bars = axis.barh(mode.dominant_mode, mode.fuel_cost_per_km, color=[BLUE, TEAL, NAVY])
    axis.set_xlim(0, mode.fuel_cost_per_km.max() * 1.3)
    axis.set_xlabel("USD per kilometre", color=NAVY, labelpad=10)
    for bar, (_, row) in zip(bars, mode.iterrows(), strict=True):
        axis.text(
            bar.get_width() + 0.025,
            bar.get_y() + bar.get_height() / 2,
            f"${row.fuel_cost_per_km:.3f}",
            color=NAVY,
            va="center",
            fontsize=12,
        )
    _save(figure, directory, "03_fuel_cost_per_km.png")

    routes = (
        tables["route_performance"]
        .query("total_shipments >= 100")
        .nlargest(8, "total_shipments")
        .sort_values("total_shipments")
    )
    figure, axis = _canvas(
        "Busiest routes: volume and delayed share",
        "Top eight routes by shipment volume; each has at least 100 observations",
        size=(12, 7),
    )
    if not routes.empty:
        labels = routes.origin_city + " → " + routes.destination_city
        axis.barh(labels, routes.on_time_shipments, color=TEAL, label="On time")
        axis.barh(
            labels, routes.delayed_shipments, left=routes.on_time_shipments, color=AMBER, label="Delayed"
        )
        axis.set_xlim(0, routes.total_shipments.max() * 1.32)
        for position, (_, row) in enumerate(routes.iterrows()):
            axis.text(
                row.total_shipments + 20,
                position,
                f"{int(row.total_shipments):,}  |  {100 - row.on_time_pct:.1f}% delayed",
                va="center",
                fontsize=10,
                color=NAVY,
            )
        figure.subplots_adjust(left=0.26)
        axis.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.01), ncol=2)
    else:
        axis.text(0.5, 0.5, "No routes meet the 100-shipment minimum", ha="center", transform=axis.transAxes)
    axis.set_xlabel("Number of shipments", color=NAVY, labelpad=10)
    _save(figure, directory, "04_route_volume_and_delays.png")
    return sorted(directory.glob("*.png"))
