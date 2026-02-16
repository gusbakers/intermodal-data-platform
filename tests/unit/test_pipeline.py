"""Tests for pipeline"""
import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.etl.pipeline import ETLPipeline

def test_pipeline_initialization():
    pipeline = ETLPipeline()
    assert pipeline.extractor is not None
