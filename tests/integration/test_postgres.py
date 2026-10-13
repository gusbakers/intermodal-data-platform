"""Only run against a disposable TEST_DATABASE_URL; the logistics schema is reset."""

import os

import pandas as pd
import psycopg2
import pytest

from src.analytics import build_tables
from src.etl.load_to_database import DatabaseETL
from src.etl.transform import DataTransformer
from src.etl.validate import DataValidator
from src.utils.config_loader import ConfigLoader

pytestmark = pytest.mark.integration


@pytest.fixture
def database(monkeypatch):
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to a disposable PostgreSQL database")
    monkeypatch.setenv("DATABASE_URL", url)
    connection = psycopg2.connect(url)
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("DROP SCHEMA IF EXISTS logistics CASCADE")
    yield DatabaseETL(ConfigLoader()), connection
    with connection.cursor() as cursor:
        cursor.execute("DROP SCHEMA IF EXISTS logistics CASCADE")
    connection.close()


def test_postgres_repeat_load_and_changed_record(database, shipments):
    loader, connection = database
    frame = DataTransformer().transform(DataValidator().validate(shipments).accepted)
    first = loader.run(frame)
    second = loader.run(frame)
    assert first["changed_records"] == 6
    assert second["changed_records"] == 0
    assert second["stored_shipments"] == 6
    frame.loc[0, "total_fuel_cost_usd"] += 123
    third = loader.run(frame)
    assert third["changed_records"] == 1
    assert third["stored_shipments"] == 6
    assert third["materialized_views_refreshed"] == 6
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM logistics.dim_routes")
        assert cursor.fetchone()[0] == len(frame[["origin_city", "destination_city"]].drop_duplicates())


def test_all_six_sql_views_match_python_kpis(database, shipments):
    loader, connection = database
    frame = DataTransformer().transform(DataValidator().validate(shipments).accepted)
    loader.run(frame)
    for name, expected in build_tables(frame).items():
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM logistics.mv_{name}")
            columns = [column.name for column in cursor.description]
            actual = [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
        sort_keys = [
            column
            for column in expected.columns
            if column in ["dominant_mode", "origin_city", "destination_city", "cargo_type", "priority_level"]
        ]
        expected_rows = expected.to_dict("records")
        if sort_keys:
            actual.sort(key=lambda row: tuple(row[key] for key in sort_keys))
            expected_rows.sort(key=lambda row: tuple(row[key] for key in sort_keys))
        assert len(actual) == len(expected_rows)
        for sql_row, python_row in zip(actual, expected_rows, strict=True):
            for key, value in python_row.items():
                if value is None or (not isinstance(value, str) and pd.isna(value)):
                    assert sql_row[key] is None
                elif isinstance(value, str):
                    assert sql_row[key] == value
                else:
                    assert float(sql_row[key]) == pytest.approx(value, rel=1e-8, abs=1e-8)


def test_failed_load_rolls_back(database, shipments):
    loader, connection = database
    frame = DataTransformer().transform(DataValidator().validate(shipments).accepted)
    loader.run(frame)
    broken = frame.iloc[[0]].copy()
    broken["shipment_id"] = "failed-new-shipment"
    broken["weight_tons"] = -1
    with pytest.raises(psycopg2.errors.CheckViolation):
        loader.run(broken)
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM logistics.fact_shipments")
        assert cursor.fetchone()[0] == 6
