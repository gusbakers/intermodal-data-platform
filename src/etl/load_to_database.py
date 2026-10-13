"""Transactional dimension loads, change-aware fact upserts and materialized-view refreshes."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor, execute_values

from src.etl.validate import RAW_COLUMNS
from src.utils.config_loader import ConfigLoader
from src.utils.logger import log

VIEWS = [
    "kpi_dashboard",
    "mode_performance",
    "route_performance",
    "cargo_performance",
    "priority_performance",
    "fuel_efficiency",
]
MEASURES = [
    column
    for column in RAW_COLUMNS
    if column
    not in ["shipment_id", "origin_city", "destination_city", "cargo_type", "priority_level", "dominant_mode"]
]
FACT_COLUMNS = ["shipment_id", "mode_id", "route_id", "cargo_id", "priority_id", *MEASURES, "source_hash"]


class DatabaseETL:
    def __init__(self, config: ConfigLoader | None = None):
        self.config = config or ConfigLoader()

    def connect(self):
        return psycopg2.connect(**self.config.database_parameters())

    def create_schema(self, cursor) -> None:
        for filename in ["01_create_tables.sql", "02_create_views.sql"]:
            cursor.execute((self.config.root / "sql/schema" / filename).read_text(encoding="utf-8"))

    def _dimension(self, cursor, table: str, key: str, columns: list[str], frame: pd.DataFrame) -> dict:
        rows = list(frame[columns].drop_duplicates().itertuples(index=False, name=None))
        statement = (
            sql.SQL("INSERT INTO logistics.{} ({}) VALUES %s ON CONFLICT DO NOTHING")
            .format(
                sql.Identifier(table),
                sql.SQL(", ").join(map(sql.Identifier, columns)),
            )
            .as_string(cursor)
        )
        execute_values(cursor, statement, rows, page_size=self.config.get("db_load.batch_size", 1000))
        cursor.execute(
            sql.SQL("SELECT {}, {} FROM logistics.{}").format(
                sql.Identifier(key),
                sql.SQL(", ").join(map(sql.Identifier, columns)),
                sql.Identifier(table),
            )
        )
        return {tuple(row[1:]): row[0] for row in cursor.fetchall()}

    def run(self, frame: pd.DataFrame) -> dict:
        if frame.empty:
            raise ValueError("Cannot load an empty shipment dataset")
        connection = self.connect()
        try:
            with connection:
                with connection.cursor() as cursor:
                    # Serialize this application's loads and refreshes within the transaction.
                    cursor.execute("SELECT pg_advisory_xact_lock(172903)")
                    self.create_schema(cursor)
                    modes = self._dimension(
                        cursor, "dim_transport_modes", "mode_id", ["dominant_mode"], frame
                    )
                    routes = self._dimension(
                        cursor, "dim_routes", "route_id", ["origin_city", "destination_city"], frame
                    )
                    cargo = self._dimension(cursor, "dim_cargo_types", "cargo_id", ["cargo_type"], frame)
                    priorities = self._dimension(
                        cursor, "dim_priorities", "priority_id", ["priority_level"], frame
                    )
                    records = frame[RAW_COLUMNS].to_dict("records")
                    rows = []
                    for record in records:
                        content_hash = hashlib.sha256(
                            json.dumps(record, sort_keys=True, allow_nan=False).encode()
                        ).hexdigest()
                        rows.append(
                            (
                                record["shipment_id"],
                                modes[(record["dominant_mode"],)],
                                routes[(record["origin_city"], record["destination_city"])],
                                cargo[(record["cargo_type"],)],
                                priorities[(record["priority_level"],)],
                                *(record[column] for column in MEASURES),
                                content_hash,
                            )
                        )
                    names = sql.SQL(", ").join(map(sql.Identifier, FACT_COLUMNS))
                    assignments = sql.SQL(", ").join(
                        sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(column), sql.Identifier(column))
                        for column in FACT_COLUMNS
                        if column != "shipment_id"
                    )
                    statement = (
                        sql.SQL(
                            "INSERT INTO logistics.fact_shipments ({}) VALUES %s "
                            "ON CONFLICT (shipment_id) DO UPDATE SET {}, loaded_at = CURRENT_TIMESTAMP "
                            "WHERE fact_shipments.source_hash IS DISTINCT FROM EXCLUDED.source_hash RETURNING shipment_id"
                        )
                        .format(names, assignments)
                        .as_string(cursor)
                    )
                    changed = execute_values(
                        cursor,
                        statement,
                        rows,
                        page_size=self.config.get("db_load.batch_size", 1000),
                        fetch=True,
                    )
                    for name in VIEWS:
                        cursor.execute(
                            sql.SQL("REFRESH MATERIALIZED VIEW logistics.{}").format(
                                sql.Identifier(f"mv_{name}")
                            )
                        )
                    cursor.execute("SELECT COUNT(*) FROM logistics.fact_shipments")
                    stored = cursor.fetchone()[0]
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT * FROM logistics.mv_kpi_dashboard")
                    dashboard = {
                        key: float(value) if isinstance(value, Decimal) else value
                        for key, value in dict(cursor.fetchone()).items()
                    }
            log.info(
                "PostgreSQL committed: %s processed, %s inserted/updated, %s stored",
                len(frame),
                len(changed),
                stored,
            )
            return {
                "status": "loaded",
                "processed_records": len(frame),
                "changed_records": len(changed),
                "stored_shipments": stored,
                "materialized_views_refreshed": len(VIEWS),
                "metrics": dashboard,
            }
        finally:
            connection.close()
