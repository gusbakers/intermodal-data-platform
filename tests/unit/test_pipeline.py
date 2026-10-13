import json

import pandas as pd
import pytest

from src.etl.pipeline import ETLPipeline


def test_pipeline_produces_real_metrics_and_manifest(config):
    result = ETLPipeline(config).run(charts=False)
    assert result.summary["accepted_records"] == 6
    assert result.summary["database"]["status"] == "skipped"
    assert result.parquet_path.exists()
    metrics = json.loads((config.path("data.output_dir") / "metrics.json").read_text())
    assert metrics["total_shipments"] == 6
    assert metrics["delayed_shipments"] == 1
    assert len(list((config.path("data.output_dir") / "tables").glob("*.csv"))) == 6


def test_failed_quality_gate_publishes_quarantine_and_removes_success_manifest(config):
    pipeline = ETLPipeline(config)
    pipeline.run(charts=False)
    frame = pd.read_csv(config.path("data.raw_file"))
    frame.loc[0, "weight_tons"] = 0
    frame.to_csv(config.path("data.raw_file"), index=False)
    with pytest.raises(ValueError, match="Quality gate failed"):
        pipeline.run(charts=False)
    assert not (config.path("data.output_dir") / "run_summary.json").exists()
    assert len(pd.read_csv(config.path("data.rejected_dir") / "rejected_records.csv")) == 1


def test_explicit_rejection_threshold_retains_only_valid_rows(config):
    frame = pd.read_csv(config.path("data.raw_file"))
    frame.loc[0, "weight_tons"] = 0
    frame.to_csv(config.path("data.raw_file"), index=False)
    result = ETLPipeline(config).run(charts=False, max_rejection_pct=20)
    assert result.summary["accepted_records"] == 5
    assert result.summary["rejected_records"] == 1
