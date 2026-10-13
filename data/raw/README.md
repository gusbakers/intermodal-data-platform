# Source data

`intermodal_transport_full_dataset.csv` is the repository-provided shipment snapshot: 20,000 rows and 18 fields. It is versioned so the analyses are reproducible. Upstream provenance is not documented in the historical repository.

The pipeline reads this filename by default. Change `data.raw_file` in `config/config.yaml` to use another source that satisfies the documented contract. CSV and Parquet are supported directly; `.xlsx` additionally requires `openpyxl`.

See `docs/DATA_DICTIONARY.md` for field names, units and metric definitions.
