"""Atomic publication of the processed Parquet layer."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd

from src.utils.config_loader import ConfigLoader


class DataLoader:
    def __init__(self, config: ConfigLoader | None = None):
        self.config = config or ConfigLoader()
        self.processed_dir = self.config.path("data.processed_dir")

    def load(self, frame: pd.DataFrame, filename: str = "shipments_processed") -> Path:
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        destination = self.processed_dir / f"{filename}.parquet"
        with NamedTemporaryFile(dir=self.processed_dir, suffix=".parquet", delete=False) as handle:
            temporary = Path(handle.name)
        try:
            frame.to_parquet(temporary, index=False, compression="snappy")
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
        return destination
