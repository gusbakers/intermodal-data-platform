"""Read the repository shipment dataset without depending on the working directory."""

from pathlib import Path

import pandas as pd

from src.utils.config_loader import ConfigLoader
from src.utils.logger import log


class DataExtractor:
    def __init__(self, config: ConfigLoader | None = None):
        self.config = config or ConfigLoader()
        self.raw_file = self.config.path("data.raw_file")

    def extract(self) -> pd.DataFrame:
        path = Path(self.raw_file)
        if not path.is_file():
            raise FileNotFoundError(f"Data file not found: {path}")
        readers = {".csv": pd.read_csv, ".parquet": pd.read_parquet, ".xlsx": pd.read_excel}
        if path.suffix.lower() not in readers:
            raise ValueError(f"Unsupported input format: {path.suffix}")
        frame = readers[path.suffix.lower()](path)
        if frame.empty:
            raise ValueError("Input dataset is empty")
        log.info("Extracted %s shipment records from %s", len(frame), path.name)
        return frame
