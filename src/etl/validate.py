"""Row-level contracts, explicit failure counts and a quarantine for rejected records."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

RAW_COLUMNS = [
    "shipment_id",
    "origin_city",
    "destination_city",
    "cargo_type",
    "weight_tons",
    "declared_value_usd",
    "priority_level",
    "planned_duration_hours",
    "status",
    "risk_flag",
    "actual_duration_hours",
    "weather_severity_avg",
    "total_legs",
    "total_distance_km",
    "total_fuel_cost_usd",
    "avg_leg_delay_minutes",
    "dominant_mode",
    "vehicle_avg_maintenance_score",
]
TEXT_COLUMNS = [
    "shipment_id",
    "origin_city",
    "destination_city",
    "cargo_type",
    "priority_level",
    "status",
    "dominant_mode",
]
NUMERIC_COLUMNS = [column for column in RAW_COLUMNS if column not in TEXT_COLUMNS]
INTEGER_COLUMNS = ["planned_duration_hours", "actual_duration_hours", "risk_flag", "total_legs"]


@dataclass
class ValidationResult:
    accepted: pd.DataFrame
    rejected: pd.DataFrame
    report: dict


class DataValidator:
    def validate(self, frame: pd.DataFrame) -> ValidationResult:
        missing = sorted(set(RAW_COLUMNS) - set(frame.columns))
        if missing:
            raise ValueError(f"Required columns missing: {', '.join(missing)}")
        if frame.empty:
            raise ValueError("Input dataset is empty")
        raw = frame[RAW_COLUMNS].reset_index(drop=True).copy()
        data = raw.copy()
        for column in TEXT_COLUMNS:
            data[column] = data[column].astype("string").str.strip()
        for column in NUMERIC_COLUMNS:
            data[column] = pd.to_numeric(data[column], errors="coerce")
        issues: dict[str, pd.Series] = {}

        def rule(name: str, invalid: pd.Series) -> None:
            if not isinstance(invalid, pd.Series):
                invalid = pd.Series(invalid, index=data.index)
            issues[name] = invalid.fillna(True).astype(bool)

        rule(
            "missing_or_empty_text",
            data[TEXT_COLUMNS].isna().any(axis=1) | data[TEXT_COLUMNS].eq("").any(axis=1),
        )
        rule(
            "invalid_or_nonfinite_numeric",
            ~np.isfinite(data[NUMERIC_COLUMNS].to_numpy(dtype=float)).all(axis=1),
        )
        for column in INTEGER_COLUMNS:
            rule(f"noninteger_{column}", data[column].isna() | data[column].mod(1).ne(0))
        for column in [
            "weight_tons",
            "total_distance_km",
            "planned_duration_hours",
            "actual_duration_hours",
            "total_legs",
        ]:
            rule(f"nonpositive_{column}", data[column].le(0) | data[column].isna())
        for column in [
            "declared_value_usd",
            "total_fuel_cost_usd",
            "avg_leg_delay_minutes",
            "weather_severity_avg",
        ]:
            rule(f"negative_{column}", data[column].lt(0) | data[column].isna())
        rule("invalid_maintenance_score", ~data.vehicle_avg_maintenance_score.between(0, 1))
        rule("invalid_risk_flag", ~data.risk_flag.isin([0, 1]))
        rule("invalid_transport_mode", ~data.dominant_mode.isin(["Rail", "Ship", "Truck"]))
        rule("invalid_status", ~data.status.isin(["On-Time", "Delayed"]))
        rule("invalid_priority", ~data.priority_level.isin(["Low", "Medium", "High"]))
        expected_status = np.where(
            data.actual_duration_hours.le(data.planned_duration_hours), "On-Time", "Delayed"
        )
        rule("status_duration_mismatch", data.status.ne(expected_status))

        exact_duplicate = data.duplicated(keep="first")
        rule("exact_duplicate", exact_duplicate)
        distinct = data.loc[~exact_duplicate]
        conflicting_ids = distinct.loc[distinct.shipment_id.duplicated(keep=False), "shipment_id"]
        rule("conflicting_shipment_id", data.shipment_id.isin(conflicting_ids))
        invalid = pd.DataFrame(issues).any(axis=1)
        accepted = data.loc[~invalid].copy()
        for column in INTEGER_COLUMNS:
            accepted[column] = accepted[column].astype("int64")
        rejected = raw.loc[invalid].copy()
        rejected["source_row"] = rejected.index + 2
        rejected["rejection_reasons"] = [
            ";".join(name for name, mask in issues.items() if bool(mask.loc[index]))
            for index in rejected.index
        ]
        report = {
            "schema_valid": True,
            "input_records": len(data),
            "accepted_records": len(accepted),
            "rejected_records": len(rejected),
            "rejection_pct": round(len(rejected) / len(data) * 100, 6),
            "rules_evaluated": len(issues),
            "rules": {
                name: {"failed_records": int(mask.sum()), "checked_records": len(data)}
                for name, mask in issues.items()
            },
            "note": "A record can fail several rules. Rejected-record counts count each record once.",
        }
        return ValidationResult(accepted.reset_index(drop=True), rejected.reset_index(drop=True), report)
