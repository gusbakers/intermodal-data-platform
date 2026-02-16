# System Architecture

## Overview
Production-grade ETL pipeline with PostgreSQL integration.

## Components

### Data Layer
- Raw data storage (CSV/Excel)
- Processed data (Parquet)
- Database (PostgreSQL)

### Processing Layer
- Extract: Read from files
- Transform: Clean and validate
- Load: Save to Parquet and PostgreSQL

### Database Layer
- Star schema (fact + dimensions)
- Materialized views for KPIs
- Indexes for performance

## Technology Stack
- Python 3.11+
- PostgreSQL 14+
- Pandas/NumPy
- Parquet (PyArrow)
