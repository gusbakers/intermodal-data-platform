import pytest

from src.etl.extract import DataExtractor


def test_extract_included_columns(config, shipments):
    actual = DataExtractor(config).extract()
    assert len(actual) == len(shipments)
    assert list(actual.columns) == list(shipments.columns)


def test_missing_file_is_reported(config):
    config.path("data.raw_file").unlink()
    with pytest.raises(FileNotFoundError, match="Data file not found"):
        DataExtractor(config).extract()


def test_extraction_does_not_depend_on_working_directory(config, tmp_path, monkeypatch):
    directory = tmp_path / "elsewhere"
    directory.mkdir()
    monkeypatch.chdir(directory)
    assert len(DataExtractor(config).extract()) == 6
