#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python scripts/verify_project.py
python -m pytest -m 'not integration'
python run_full_pipeline.py --no-charts
