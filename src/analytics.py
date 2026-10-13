"""Reproducible KPI tables using the same definitions as the PostgreSQL views."""

from __future__ import annotations

import pandas as pd


def kpis(frame: pd.DataFrame) -> dict:
    if frame.empty:
        raise ValueError("Cannot compute KPIs from an empty dataset")
    delayed = frame.loc[~frame.is_on_time]
    return {
        "total_shipments": int(len(frame)),
        "on_time_shipments": int(frame.is_on_time.sum()),
        "delayed_shipments": int((~frame.is_on_time).sum()),
        "on_time_pct": float(frame.is_on_time.mean() * 100),
        "avg_planned_duration_hours": float(frame.planned_duration_hours.mean()),
        "avg_actual_duration_hours": float(frame.actual_duration_hours.mean()),
        "avg_delay_hours_delayed": float(delayed.delay_hours.mean()) if len(delayed) else None,
        "total_fuel_cost_usd": float(frame.total_fuel_cost_usd.sum()),
        "avg_fuel_cost_usd": float(frame.total_fuel_cost_usd.mean()),
        "fuel_cost_per_km": float(frame.total_fuel_cost_usd.sum() / frame.total_distance_km.sum()),
        "fuel_cost_per_ton_km": float(
            frame.total_fuel_cost_usd.sum() / (frame.weight_tons * frame.total_distance_km).sum()
        ),
    }


def grouped_kpis(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    records = []
    for key, group in frame.groupby(columns, observed=True, sort=True):
        values = key if isinstance(key, tuple) else (key,)
        records.append(dict(zip(columns, values, strict=True)) | kpis(group))
    return pd.DataFrame(records)


def build_tables(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    mode = grouped_kpis(frame, ["dominant_mode"])
    return {
        "kpi_dashboard": pd.DataFrame([kpis(frame)]),
        "mode_performance": mode,
        "route_performance": grouped_kpis(frame, ["origin_city", "destination_city"]),
        "cargo_performance": grouped_kpis(frame, ["cargo_type"]),
        "priority_performance": grouped_kpis(frame, ["priority_level"]),
        "fuel_efficiency": mode[
            [
                "dominant_mode",
                "total_shipments",
                "total_fuel_cost_usd",
                "fuel_cost_per_km",
                "fuel_cost_per_ton_km",
            ]
        ].copy(),
    }
