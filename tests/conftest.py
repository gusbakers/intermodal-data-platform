from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.utils.config_loader import PROJECT_ROOT, ConfigLoader


@pytest.fixture
def shipments():
    frame = pd.read_csv(PROJECT_ROOT / "data/raw/intermodal_transport_full_dataset.csv", nrows=6)
    frame["actual_duration_hours"] = frame["planned_duration_hours"]
    frame["status"] = "On-Time"
    frame.loc[0, "actual_duration_hours"] = frame.loc[0, "planned_duration_hours"] + 8
    frame.loc[0, "status"] = "Delayed"
    return frame


@pytest.fixture
def config(tmp_path: Path, shipments):
    settings = yaml.safe_load((PROJECT_ROOT / "config/config.yaml").read_text())
    settings["data"]["raw_file"] = "input.csv"
    shipments.to_csv(tmp_path / "input.csv", index=False)
    (tmp_path / "config.yaml").write_text(yaml.safe_dump(settings))
    return ConfigLoader("config.yaml", root=tmp_path)
