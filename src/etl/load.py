"""Data Loading Module"""
import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import log
from utils.config_loader import config

class DataLoader:
    def __init__(self):
        self.processed_dir = Path(config.get('data.processed_dir'))
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self, df: pd.DataFrame, filename: str = 'processed_data') -> Path:
        log.info(f"💾 Loading data to Parquet")
        output_file = self.processed_dir / f"{filename}.parquet"
        
        df.to_parquet(output_file, index=False, compression='snappy')
        size_mb = output_file.stat().st_size / (1024 ** 2)
        
        log.info(f"✅ Saved {len(df):,} records ({size_mb:.2f} MB)")
        return output_file

if __name__ == "__main__":
    from extract import DataExtractor
    from transform import DataTransformer
    
    extractor = DataExtractor()
    transformer = DataTransformer()
    loader = DataLoader()
    
    df = extractor.extract()
    df_clean = transformer.transform(df)
    loader.load(df_clean)
