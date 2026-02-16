"""Data Transformation Module"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import log
from utils.config_loader import config

class DataTransformer:
    def __init__(self):
        self.validation_enabled = config.get('etl.validation_enabled', True)
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        log.info("🔧 Starting transformation")
        df_clean = df.copy()
        
        initial = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        log.info(f"Removed {initial - len(df_clean)} duplicates")
        
        date_cols = config.get('validation.date_columns', [])
        for col in date_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
        
        df_clean['processed_at'] = pd.Timestamp.now()
        
        log.info(f"✅ Transformation complete: {len(df_clean):,} records")
        return df_clean

if __name__ == "__main__":
    from extract import DataExtractor
    extractor = DataExtractor()
    df = extractor.extract()
    transformer = DataTransformer()
    df_clean = transformer.transform(df)
    print(df_clean.info())
