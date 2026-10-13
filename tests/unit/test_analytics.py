import pytest

from src.analytics import build_tables, kpis
from src.etl.transform import DataTransformer
from src.etl.validate import DataValidator


def test_kpis_use_ratio_of_totals(shipments):
    frame = DataTransformer().transform(DataValidator().validate(shipments).accepted)
    metrics = kpis(frame)
    assert metrics["on_time_pct"] == pytest.approx(100 * 5 / 6)
    assert metrics["avg_delay_hours_delayed"] == 8
    assert metrics["fuel_cost_per_km"] == pytest.approx(
        frame.total_fuel_cost_usd.sum() / frame.total_distance_km.sum()
    )
    tables = build_tables(frame)
    assert len(tables) == 6
    assert tables["mode_performance"].total_shipments.sum() == 6
