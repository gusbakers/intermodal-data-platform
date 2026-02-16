"""Tests for transformation"""
import pytest
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.etl.transform import DataTransformer

def test_transformer_initialization():
    transformer = DataTransformer()
    assert transformer.validation_enabled is not None
