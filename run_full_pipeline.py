"""Run from the repository root: python run_full_pipeline.py [--with-database]."""

from __future__ import annotations

import argparse
import json
import sys

from dotenv import load_dotenv

from src.etl.pipeline import ETLPipeline
from src.utils.config_loader import PROJECT_ROOT, ConfigLoader


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate shipments and publish logistics KPIs")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument(
        "--with-database", action="store_true", help="Load PostgreSQL using DB_* environment variables"
    )
    parser.add_argument("--no-charts", action="store_true")
    parser.add_argument(
        "--max-rejection-pct",
        type=float,
        default=None,
        help="Maximum rejected-record percentage; default is 0",
    )
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    try:
        result = ETLPipeline(ConfigLoader(args.config)).run(
            with_database=args.with_database,
            charts=not args.no_charts,
            max_rejection_pct=args.max_rejection_pct,
        )
    except (ValueError, FileNotFoundError) as error:
        print(f"Pipeline failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result.summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
