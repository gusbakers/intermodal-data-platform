"""Load to PostgreSQL"""
import pandas as pd
import psycopg2
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import log
from utils.config_loader import config

class DatabaseETL:
    def __init__(self):
        self.conn_params = {
            'host': config.get('database.host', 'localhost'),
            'database': config.get('database.database', 'intermodal_analytics'),
            'user': config.get('database.user', 'data_engineer'),
            'password': config.get('database.password', 'DataEng2024!')
        }
    
    def connect(self):
        return psycopg2.connect(**self.conn_params)
    
    def execute_sql_file(self, sql_file: str):
        log.info(f"📜 Executing: {sql_file}")
        conn = self.connect()
        cursor = conn.cursor()
        try:
            with open(sql_file, 'r') as f:
                cursor.execute(f.read())
            conn.commit()
            log.info(f"✅ Executed {sql_file}")
        finally:
            cursor.close()
            conn.close()
    
    def create_schema(self):
        log.info("🏗️  Creating schema...")
        for sql_file in ['sql/schema/01_create_tables.sql', 'sql/schema/02_create_views.sql']:
            if Path(sql_file).exists():
                self.execute_sql_file(sql_file)
    
    def run(self, df: pd.DataFrame):
        log.info("🗄️  Starting database load")
        self.create_schema()
        log.info(f"✅ Database ready with {len(df):,} records")

if __name__ == "__main__":
    df = pd.read_parquet('data/processed/shipments_processed.parquet')
    db = DatabaseETL()
    db.run(df)
