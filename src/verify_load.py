"""
Verifies that MySQL row counts and sums match data/processed/clean_events.csv.

Usage:
    python -m src.verify_load

Exits non-zero if any check fails.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

CLEAN_CSV = Path("data/processed/clean_events.csv")


def _get_engine():
    load_dotenv()
    host = os.environ["DB_HOST"]
    port = os.environ.get("DB_PORT", "3306")
    name = os.environ["DB_NAME"]
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"
    return create_engine(url, echo=False)


def verify() -> None:
    if not CLEAN_CSV.exists():
        sys.exit(
            f"ERROR: '{CLEAN_CSV}' not found. Run the pipeline before verifying."
        )

    df = pd.read_csv(CLEAN_CSV)
    csv_rows = len(df)
    csv_sum_prepared = int(df["Quantity of Food"].sum())
    csv_sum_wastage = int(df["Wastage Food Amount"].sum())

    engine = _get_engine()
    with engine.connect() as conn:
        db_rows = conn.execute(
            text("SELECT COUNT(*) FROM event_records")
        ).scalar()
        db_sum_prepared = conn.execute(
            text("SELECT SUM(qty_prepared) FROM event_records")
        ).scalar()
        db_sum_wastage = conn.execute(
            text("SELECT SUM(wastage_amount) FROM event_records")
        ).scalar()

    failures: list[str] = []

    if db_rows != csv_rows:
        failures.append(
            f"Row count mismatch: CSV has {csv_rows}, MySQL has {db_rows}."
        )
    if int(db_sum_prepared) != csv_sum_prepared:
        failures.append(
            f"qty_prepared sum mismatch: CSV {csv_sum_prepared}, MySQL {db_sum_prepared}."
        )
    if int(db_sum_wastage) != csv_sum_wastage:
        failures.append(
            f"wastage_amount sum mismatch: CSV {csv_sum_wastage}, MySQL {db_sum_wastage}."
        )

    if failures:
        for msg in failures:
            print(f"FAIL: {msg}")
        sys.exit(1)

    print(f"Verification passed: {db_rows} rows, "
          f"qty_prepared sum {db_sum_prepared}, wastage sum {db_sum_wastage}.")


if __name__ == "__main__":
    verify()
