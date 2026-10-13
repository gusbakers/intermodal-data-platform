import pandas as pd

from src.etl.load import DataLoader
from src.etl.transform import DataTransformer
from src.etl.validate import DataValidator


def test_parquet_round_trip_and_repeat_load(config, shipments):
    frame = DataTransformer().transform(DataValidator().validate(shipments).accepted)
    loader = DataLoader(config)
    first = loader.load(frame)
    second = loader.load(frame)
    assert first == second
    pd.testing.assert_frame_equal(frame, pd.read_parquet(second))
    assert list(loader.processed_dir.glob("*.parquet")) == [second]
