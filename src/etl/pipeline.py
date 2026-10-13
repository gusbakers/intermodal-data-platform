"""Orchestrate validation, processed storage, analytical outputs and an optional database load."""

from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import pandas as pd

from src.analytics import build_tables, kpis
from src.etl.extract import DataExtractor
from src.etl.load import DataLoader
from src.etl.transform import DataTransformer
from src.etl.validate import DataValidator
from src.utils.config_loader import ConfigLoader
from src.utils.logger import log, setup_logger


@dataclass
class PipelineResult:
    frame: pd.DataFrame
    parquet_path: Path
    summary: dict


class ETLPipeline:
    def __init__(self, config: ConfigLoader | None = None):
        self.config = config or ConfigLoader()
        self.extractor = DataExtractor(self.config)
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.loader = DataLoader(self.config)

    def run(
        self, *, with_database: bool = False, charts: bool = True, max_rejection_pct: float | None = None
    ) -> PipelineResult:
        setup_logger(self.config.path("logging.file"), self.config.get("logging.level", "INFO"))
        output = self.config.path("data.output_dir")
        output.mkdir(parents=True, exist_ok=True)
        # A failed run must not leave a previous success manifest looking current.
        (output / "run_summary.json").unlink(missing_ok=True)
        started = perf_counter()
        threshold = (
            self.config.get("quality.max_rejection_pct", 0.0)
            if max_rejection_pct is None
            else max_rejection_pct
        )
        if not 0 <= float(threshold) <= 100:
            raise ValueError("max_rejection_pct must be between 0 and 100")
        try:
            raw = self.extractor.extract()
            validated = self.validator.validate(raw)
            (output / "data_quality_report.json").write_text(
                json.dumps(validated.report, indent=2) + "\n", encoding="utf-8"
            )
            rejected_dir = self.config.path("data.rejected_dir")
            rejected_dir.mkdir(parents=True, exist_ok=True)
            validated.rejected.to_csv(rejected_dir / "rejected_records.csv", index=False)
            if validated.report["rejection_pct"] > float(threshold):
                raise ValueError(
                    f"Quality gate failed: {validated.report['rejected_records']} rejected records; inspect data/rejected/rejected_records.csv"
                )
            if validated.accepted.empty:
                raise ValueError("No accepted shipment records remain")
            frame = self.transformer.transform(validated.accepted)
            parquet = self.loader.load(frame)
            tables = build_tables(frame)
            table_dir = output / "tables"
            table_dir.mkdir(parents=True, exist_ok=True)
            for name, table in tables.items():
                table.to_csv(table_dir / f"{name}.csv", index=False, float_format="%.8f")
            metrics = kpis(frame)
            (output / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
            if charts:
                from src.visualization import create_charts

                create_charts(frame, tables, output / "figures")
            database = {"status": "skipped", "reason": "Run with --with-database to load PostgreSQL"}
            if with_database:
                from src.etl.load_to_database import DatabaseETL

                database = DatabaseETL(self.config).run(frame)
            summary = {
                "status": "success",
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "python_version": platform.python_version(),
                "source_file": str(self.extractor.raw_file.relative_to(self.config.root))
                if self.extractor.raw_file.is_relative_to(self.config.root)
                else self.extractor.raw_file.name,
                "source_sha256": hashlib.sha256(self.extractor.raw_file.read_bytes()).hexdigest(),
                "input_records": len(raw),
                "accepted_records": len(frame),
                "rejected_records": validated.report["rejected_records"],
                "elapsed_seconds": round(perf_counter() - started, 4),
                "database": database,
                "metrics": metrics,
            }
            (output / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
            log.info(
                "Pipeline completed: %s accepted, %s rejected, %.3fs",
                len(frame),
                len(validated.rejected),
                summary["elapsed_seconds"],
            )
            return PipelineResult(frame, parquet, summary)
        except Exception:
            log.exception("Pipeline failed; no success manifest published")
            raise
