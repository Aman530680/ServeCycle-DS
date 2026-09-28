"""
Loads data/processed/clean_events.csv into MySQL.

Uses upsert semantics so it is safe to re-run. Requires the schema
to already exist (run backend/db/schema.sql first).

Usage:
    python -m src.loader
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


def load() -> None:
    if not CLEAN_CSV.exists():
        sys.exit(
            f"ERROR: Processed dataset not found at '{CLEAN_CSV}'. "
            "Run the pipeline first: python -m src.pipeline"
        )

    df = pd.read_csv(CLEAN_CSV)
    print(f"Loaded {len(df)} rows from {CLEAN_CSV}")

    engine = _get_engine()

    with engine.begin() as conn:
        # Upsert food categories
        food_types = df["Type of Food"].unique().tolist()
        for name in food_types:
            conn.execute(
                text("INSERT IGNORE INTO food_categories (name) VALUES (:name)"),
                {"name": name},
            )
        print(f"  Upserted {len(food_types)} food categories.")

        # Fetch category name → id mapping
        rows = conn.execute(text("SELECT id, name FROM food_categories")).fetchall()
        cat_map: dict[str, int] = {row.name: row.id for row in rows}

        # Upsert event records
        inserted = 0
        for _, row in df.iterrows():
            conn.execute(
                text(
                    """
                    INSERT INTO event_records (
                        food_category_id, num_guests, event_type,
                        qty_prepared, storage_conditions, purchase_history,
                        seasonality, preparation_method, geographical_location,
                        pricing, wastage_amount,
                        flag_missing, flag_duplicate, flag_negative_qty,
                        flag_zero_prepared, flag_wastage_exceeds_prepared,
                        flag_outlier_guests, flag_outlier_qty_food,
                        flag_outlier_wastage, flag_unknown_category
                    ) VALUES (
                        :food_category_id, :num_guests, :event_type,
                        :qty_prepared, :storage_conditions, :purchase_history,
                        :seasonality, :preparation_method, :geographical_location,
                        :pricing, :wastage_amount,
                        :flag_missing, :flag_duplicate, :flag_negative_qty,
                        :flag_zero_prepared, :flag_wastage_exceeds_prepared,
                        :flag_outlier_guests, :flag_outlier_qty_food,
                        :flag_outlier_wastage, :flag_unknown_category
                    )
                    ON DUPLICATE KEY UPDATE
                        num_guests = VALUES(num_guests)
                    """
                ),
                {
                    "food_category_id": cat_map[row["Type of Food"]],
                    "num_guests": int(row["Number of Guests"]),
                    "event_type": row["Event Type"],
                    "qty_prepared": int(row["Quantity of Food"]),
                    "storage_conditions": row["Storage Conditions"],
                    "purchase_history": row["Purchase History"],
                    "seasonality": row["Seasonality"],
                    "preparation_method": row["Preparation Method"],
                    "geographical_location": row["Geographical Location"],
                    "pricing": row["Pricing"],
                    "wastage_amount": int(row["Wastage Food Amount"]),
                    "flag_missing": int(row.get("flag_missing", False)),
                    "flag_duplicate": int(row.get("flag_duplicate", False)),
                    "flag_negative_qty": int(row.get("flag_negative_qty", False)),
                    "flag_zero_prepared": int(row.get("flag_zero_prepared", False)),
                    "flag_wastage_exceeds_prepared": int(row.get("flag_wastage_exceeds_prepared", False)),
                    "flag_outlier_guests": int(row.get("flag_outlier_guests", False)),
                    "flag_outlier_qty_food": int(row.get("flag_outlier_qty_food", False)),
                    "flag_outlier_wastage": int(row.get("flag_outlier_wastage", False)),
                    "flag_unknown_category": int(row.get("flag_unknown_category", False)),
                },
            )
            inserted += 1

    print(f"  Upserted {inserted} event records.")
    print("Load complete.")


if __name__ == "__main__":
    load()
