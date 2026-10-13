import pandas as pd
import pytest

from src.etl.transform import DataTransformer
from src.etl.validate import DataValidator


def test_features_use_hours_tonnes_and_weighted_denominators(shipments):
    clean = DataValidator().validate(shipments).accepted
    result = DataTransformer().transform(clean)
    assert result.loc[0, "delay_hours"] == 8
    assert not result.loc[0, "is_on_time"]
    assert result.loc[0, "fuel_cost_per_ton_km"] == pytest.approx(
        clean.loc[0, "total_fuel_cost_usd"]
        / (clean.loc[0, "weight_tons"] * clean.loc[0, "total_distance_km"])
    )
    assert str(result.processed_at.dt.tz) == "UTC"
    assert "processed_at" not in shipments.columns


def test_early_arrival_has_zero_delay(shipments):
    shipments.loc[0, "actual_duration_hours"] = shipments.loc[0, "planned_duration_hours"] - 2
    shipments.loc[0, "status"] = "On-Time"
    result = DataTransformer().transform(DataValidator().validate(shipments).accepted)
    assert result.loc[0, "delay_hours"] == 0
    assert result.loc[0, "is_on_time"]


def test_conflicting_duplicate_ids_are_quarantined(shipments):
    duplicate = shipments.iloc[[0]].copy()
    duplicate["total_fuel_cost_usd"] += 1
    result = DataValidator().validate(pd.concat([shipments, duplicate], ignore_index=True))
    assert len(result.accepted) == 5
    assert len(result.rejected) == 2
    assert result.report["rules"]["conflicting_shipment_id"]["failed_records"] == 2
