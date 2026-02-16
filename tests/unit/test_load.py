"""Tests for loading"""
import pytest
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.etl.load import DataLoader

def test_loader_initialization():
    loader = DataLoader()
    assert loader.processed_dir.exists()
