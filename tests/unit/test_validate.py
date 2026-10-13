import numpy as np
import pandas as pd
import pytest

from src.etl.validate import DataValidator


def test_valid_input_runs_every_rule(shipments):
    result = DataValidator().validate(shipments)
    assert len(result.accepted) == 6
    assert result.report["rejected_records"] == 0
    assert result.report["rules_evaluated"] >= 20
    assert all(rule["checked_records"] == 6 for rule in result.report["rules"].values())


def test_missing_columns_fail_instead_of_receiving_perfect_quality(shipments):
    with pytest.raises(ValueError, match="Required columns missing"):
        DataValidator().validate(shipments.drop(columns="total_fuel_cost_usd"))


@pytest.mark.parametrize(
    "column,value",
    [
        ("weight_tons", 0),
        ("total_distance_km", 0),
        ("total_fuel_cost_usd", -1),
        ("total_fuel_cost_usd", np.inf),
        ("total_fuel_cost_usd", "broken"),
        ("planned_duration_hours", 2.5),
        ("status", "Unknown"),
        ("vehicle_avg_maintenance_score", 1.5),
        ("origin_city", " "),
    ],
)
def test_bad_records_have_a_reason(shipments, column, value):
    shipments[column] = shipments[column].astype(object)
    shipments.loc[0, column] = value
    result = DataValidator().validate(shipments)
    assert len(result.accepted) == 5
    assert len(result.rejected) == 1
    assert result.rejected.loc[0, "rejection_reasons"]
    assert result.report["rejection_pct"] == pytest.approx(100 / 6, abs=1e-6)


def test_inconsistent_status_is_rejected(shipments):
    shipments.loc[0, "status"] = "On-Time"
    result = DataValidator().validate(shipments)
    assert result.report["rules"]["status_duration_mismatch"]["failed_records"] == 1


def test_identical_duplicates_keep_one_and_report_the_removed_row(shipments):
    result = DataValidator().validate(pd.concat([shipments, shipments.iloc[[0]]], ignore_index=True))
    assert len(result.accepted) == 6
    assert result.report["rules"]["exact_duplicate"]["failed_records"] == 1
    assert result.rejected.loc[0, "rejection_reasons"] == "exact_duplicate"


def test_empty_input_fails(shipments):
    with pytest.raises(ValueError, match="empty"):
        DataValidator().validate(shipments.iloc[:0])
