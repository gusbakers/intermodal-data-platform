# Processed data

The pipeline creates `shipments_processed.parquet` from accepted, validated shipment records. Source fields are retained alongside duration, on-time and fuel-efficiency features and a UTC processing timestamp.

Generated Parquet files are ignored by Git and are recreated with `python run_full_pipeline.py`.
