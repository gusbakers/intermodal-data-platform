"""Main ETL Pipeline"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from extract import DataExtractor
from transform import DataTransformer
from load import DataLoader
from utils.logger import log
import time

class ETLPipeline:
    def __init__(self):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
    
    def run(self):
        log.info("=" * 70)
        log.info("🚀 STARTING ETL PIPELINE")
        log.info("=" * 70)
        
        start_time = time.time()
        
        try:
            df_raw = self.extractor.extract()
            df_clean = self.transformer.transform(df_raw)
            output_path = self.loader.load(df_clean, filename='shipments_processed')
            
            elapsed = time.time() - start_time
            log.info(f"✅ Pipeline complete in {elapsed:.2f}s")
            return df_clean
        except Exception as e:
            log.error(f"❌ Pipeline failed: {e}")
            raise

if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run()
