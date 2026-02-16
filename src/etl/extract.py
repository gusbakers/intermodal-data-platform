"""Data Extraction Module"""
import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import log
from utils.config_loader import config

class DataExtractor:
    def __init__(self):
        self.raw_file = config.get('data.raw_file')
    
    def extract(self) -> pd.DataFrame:
        log.info(f"🔍 Extracting data from: {self.raw_file}")
        file_path = Path(self.raw_file)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path, low_memory=False)
        elif file_path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_path.suffix == '.parquet':
            df = pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_path.suffix}")
        
        log.info(f"✅ Extracted {len(df):,} records")
        return df

if __name__ == "__main__":
    extractor = DataExtractor()
    df = extractor.extract()
    print(df.head())
