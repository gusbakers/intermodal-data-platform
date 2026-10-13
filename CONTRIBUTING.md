# Contributing

Run from a checkout with Python 3.11 or 3.12. Install `requirements-dev.txt`, then run Ruff, `scripts/verify_project.py`, behavioral tests and the pipeline before submitting changes.

If a metric definition changes, update its Python implementation, SQL view, dictionary and parity tests together. Regenerate charts and execute the notebooks so saved outputs match the source data.

PostgreSQL integration tests require a disposable `TEST_DATABASE_URL` and reset its `logistics` schema. Keep `.env`, processed Parquet, quarantine data and logs out of commits.
