# Running and troubleshooting

Start with `python run_full_pipeline.py`. Add `--with-database` only after PostgreSQL is running and local database environment variables are configured.

| Check | Where | Expected result for the included input |
|---|---|---|
| Input checksum and run status | `outputs/run_summary.json` | `status: success`, 20,000 accepted records |
| Database status | Manifest `database.status` | `skipped` for file-only mode; `loaded` for database mode |
| Quality rules | `outputs/data_quality_report.json` | Every rule checked; zero rejected rows |
| Rejected records | `data/rejected/rejected_records.csv` | Headers only for the included valid snapshot |
| Logs | `logs/pipeline.log` | Stage counts, duration and errors; rotated files |
| Database repeat load | Manifest `database.changed_records` | Zero for unchanged shipments |

## Quality failures

Missing columns fail schema validation. Row failures publish a quality report and quarantine CSV, then fail the default gate. Correct the source records and rerun. For a deliberately reviewed partial load, `--max-rejection-pct 1` accepts a rejection rate up to 1%; accepted rows alone enter downstream analysis. This option does not modify the source file.

## Database failures

Check `docker compose ps`, environment settings and the database log. A connection or SQL failure returns a nonzero process status and publishes no success manifest. Database changes roll back together. Retrying an unchanged load is safe because shipment IDs and content hashes prevent repeated fact inserts and unnecessary updates.

## Notebook execution

`python scripts/execute_notebooks.py` runs each notebook in a fresh in-process IPython namespace and saves outputs. It raises an error on a failed code cell. The notebooks can also be opened normally in Jupyter or VS Code.

## Stop resources

`docker compose down` stops the local database and keeps its named volume. A file-only pipeline starts no persistent service. If using GitHub Codespaces, stop the Codespace through GitHub after finishing. Deleting a Docker volume is a separate data-removal action.

## Scope of performance evidence

Each manifest records the duration of the phases requested for that run and the exact input checksum. File-only and PostgreSQL runs have different scopes. Do not present one as the timing of the other or extrapolate this snapshot's throughput to a larger production workload.
