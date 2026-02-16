"""Tests for extraction"""
import pytest
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.etl.extract import DataExtractor

def test_extractor_initialization():
    extractor = DataExtractor()
    assert extractor.raw_file is not None
