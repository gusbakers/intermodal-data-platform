# Intermodal Transportation Analytics Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

-----

I got tired of building toy projects with Titanic data or Iris flowers.

So I picked something I actually find interesting — logistics. The kind of operations problem where a wrong decision costs a company thousands of dollars: which route do you use, which carrier do you trust, why is this shipment two weeks late. Real questions with real stakes.

This is a full ETL pipeline I built from scratch. It processes raw shipment data across 4 transport modes (maritime, air, rail, road), loads it into a PostgreSQL database with a proper star schema, and generates the kind of KPIs an operations team would actually use — on-time delivery rates, cost efficiency by carrier, route profitability.

-----

## Why I built this specific thing

I was looking at a lot of data engineering job descriptions and they all mentioned the same stuff: ETL pipelines, SQL, data modeling, maybe some Python. But most portfolio projects I found online were just Jupyter notebooks with pandas. Nothing that looked like actual production code.

I wanted something with real structure — separate modules, proper error handling, logging that actually helps when things break, tests that run. Not just a script that works on my machine.

The logistics domain made sense because the data is naturally interesting. You have routes, carriers, cargo types, time series, cost vs speed tradeoffs. You can ask real business questions and get meaningful answers.

-----

## What it does

Takes messy CSV data with shipment records → cleans and validates it → loads it into PostgreSQL → refreshes 6 pre-built analytical views so you can immediately query KPIs like this:

```sql
SELECT * FROM mv_carrier_scorecard ORDER BY performance_score DESC;
```

```
 carrier_name | total_shipments | on_time_% | performance_score | rank
--------------+-----------------+-----------+-------------------+------
 Carrier_3    |           5,234 |      97.2 |              92.5 |    1
 Carrier_7    |           4,892 |      95.8 |              89.3 |    2
 Carrier_1    |           5,123 |      93.1 |              85.7 |    3
```

The pipeline processes ~50K records in under a minute. Here’s what a real run looks like:

```
🚀 INTERMODAL ANALYTICS — PIPELINE STARTING
============================================================

📦 PHASE 1: File ETL
  ✅ Extracted    50,000 records
  ✅ Transformed  49,477 records  (removed 523 duplicates)
  ✅ Saved to     data/processed/shipments_processed.parquet

🗄️  PHASE 2: Database
  ✅ Schema created
  ✅ Dimensions loaded (modes, routes, carriers, cargo types)
  ✅ 49,477 shipments loaded to fact table
  ✅ 6 materialized views refreshed

📊 PHASE 3: KPIs
  on_time_delivery_rate  →  94.5%
  avg_cost_per_shipment  →  $8,234
  avg_transit_days       →  12.3
  delay_rate             →  5.5%

⏱️  Done in 58.2 seconds
```

-----

## Project structure

```
intermodal-data-platform/
│
├── src/
│   ├── etl/
│   │   ├── extract.py           # reads CSV/Excel, validates it exists and has the right columns
│   │   ├── transform.py         # deduplication, null handling, date parsing, feature engineering
│   │   ├── load.py              # saves to Parquet
│   │   ├── pipeline.py          # runs extract → transform → load in order
│   │   └── load_to_database.py  # loads to PostgreSQL (dimensions first, then facts)
│   └── utils/
│       ├── logger.py            # loguru setup with file rotation
│       └── config_loader.py     # reads config.yaml so nothing is hardcoded
│
├── sql/
│   ├── schema/
│   │   ├── 01_create_tables.sql   # star schema DDL
│   │   └── 02_create_views.sql    # 6 materialized views
│   └── kpis/
│       └── business_kpis.sql      # analytical queries
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_quality_report.ipynb
│   └── 03_kpi_dashboard.ipynb
│
├── tests/unit/
├── config/config.yaml
└── run_full_pipeline.py
```

-----

## Getting it running

Prerequisites: Python 3.11, PostgreSQL 14

```bash
git clone https://github.com/gusbakers/intermodal-data-platform.git
cd intermodal-data-platform
pip install -r requirements.txt
```

Set up the database:

```bash
sudo service postgresql start

sudo -u postgres psql << EOF
CREATE DATABASE intermodal_analytics;
CREATE USER data_engineer WITH PASSWORD 'DataEng2024!';
GRANT ALL PRIVILEGES ON DATABASE intermodal_analytics TO data_engineer;
\c intermodal_analytics
GRANT ALL ON SCHEMA public TO data_engineer;
EOF
```

Add your data file to `data/raw/` and update the path in `config/config.yaml`, then:

```bash
python run_full_pipeline.py
```

That’s it. The schema gets created automatically on first run.

-----

## The database design

Star schema — one fact table with shipment transactions, four dimension tables with descriptive attributes (transport modes, routes, carriers, cargo types), and a date dimension for time-based analysis.

```
dim_transport_modes     dim_carriers
        |                    |
        +──→ fact_shipments ←─+
                  |
           dim_routes    dim_cargo_types
                  |
              dim_date
```

I chose star schema over a flat denormalized table because the queries here are analytical. When you’re aggregating 50K rows by carrier and month, you want pre-joined structures with proper indexes — not scanning a wide table with repeated strings.

The 6 materialized views pre-calculate the most common aggregations:

|View                  |What it’s for                                     |
|----------------------|--------------------------------------------------|
|`mv_kpi_dashboard`    |top-level overview metrics                        |
|`mv_mode_performance` |maritime vs air vs rail vs road breakdown         |
|`mv_route_performance`|volume and delay rates by route                   |
|`mv_carrier_scorecard`|ranked carriers with composite score              |
|`mv_monthly_trends`   |MoM and YoY growth using window functions         |
|`mv_cost_optimization`|shipments running significantly above mode average|

They refresh automatically at the end of each pipeline run.

-----

## Some decisions I made and why

**Parquet for the processed layer, not CSV**

After the ETL runs, I save to Parquet instead of writing a new CSV. It compresses to about 30% of the original size and loads much faster for downstream reads because it’s columnar — if a query only needs three columns out of twenty, it doesn’t read the rest. CSV doesn’t do that.

**Loguru instead of print statements**

I started with print() everywhere. Got annoying fast — no timestamps, no log levels, nothing persisted after the terminal closed. Loguru was a clean upgrade: structured output, automatic file rotation, easy to set to DEBUG when I’m troubleshooting.

**Config in YAML**

Database host, passwords, file paths — none of that is hardcoded in the source files. It lives in `config/config.yaml`. Means I can run this locally against localhost and in a different environment against a real server without touching Python code.

**Batch inserts to PostgreSQL**

First version was doing one INSERT per row. With 50K rows that was painfully slow. Switched to `psycopg2.extras.execute_values` which batches 1,000 rows per trip to the database. Much better.

-----

## Things that didn’t go well the first time

The date parsing broke on me twice. Different carriers in the sample data used different formats — some used `2024-01-15`, others `15/01/2024`, a few had timestamps with timezone offsets. I eventually had to write a proper multi-format parser with fallbacks instead of just calling `pd.to_datetime()` and hoping.

The first version of the dimension loading also had a bug where I was inserting routes before checking if the carrier existed, which caused FK constraint violations that were annoying to debug. Fixed it by explicitly ordering: modes → carriers → routes → facts.

-----

## Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

-----

## What I want to add next

Airflow for scheduling — right now you have to run it manually which is fine for a portfolio project but wouldn’t scale. dbt for the SQL transformation layer would also be cleaner than raw SQL files. And honestly a Streamlit dashboard would make the KPIs accessible to people who don’t want to open Jupyter.

-----

## Connect

Master's in Data Science 
Data Engineer · ML Engineer · AI Engineer

If you have feedback on the approach or just want to talk about data engineering, feel free to reach out.

📧 gaft-2727@outlook.com
