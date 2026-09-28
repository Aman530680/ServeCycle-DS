"""
Feature engineering for the wastage prediction model.

This module is the single source of truth for feature construction.
It is used by both training (src/model.py) and the API prediction
endpoint — no separate feature-building path exists.

Target: Wastage Food Amount (units discarded).

Excluded from features:
- Quantity of Food: a preparation decision, not a pre-event input
- Wastage Food Amount: the target itself
- wastage_pct: derived from the target — using it would be circular
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

# The fixed ordering within each categorical column.
# Storing the order here ensures the encoder produces the same integer
# mapping whether called from training or the API.
CATEGORY_ORDERS: dict[str, list[str]] = {
    "Type of Food": ["Baked Goods", "Dairy Products", "Fruits", "Meat", "Vegetables"],
    "Event Type": ["Birthday", "Corporate", "Social Gathering", "Wedding"],
    "Storage Conditions": ["Refrigerated", "Room Temperature"],
    "Purchase History": ["Occasional", "Regular"],
    "Seasonality": ["All Seasons", "Summer", "Winter"],
    "Preparation Method": ["Buffet", "Finger Food", "Sit-down Dinner"],
    "Geographical Location": ["Rural", "Suburban", "Urban"],
    "Pricing": ["High", "Low", "Moderate"],
}

CATEGORICAL_FEATURE_COLS = list(CATEGORY_ORDERS.keys())

NUMERIC_FEATURE_COLS = ["Number of Guests"]

ALL_FEATURE_COLS = CATEGORICAL_FEATURE_COLS + NUMERIC_FEATURE_COLS

TARGET_COL = "Wastage Food Amount"

# Columns that must never appear as model features.
FORBIDDEN_COLS = {"Quantity of Food", "Wastage Food Amount", "wastage_pct"}


def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series | None]:
    """
    Constructs the feature matrix X and target vector y from a DataFrame.

    Returns (X, y) where y is None if the target column is not present
    (API prediction path).

    The encoder uses the fixed CATEGORY_ORDERS above, so the integer
    mapping is identical whether called from training or prediction.
    """
    _assert_no_leakage(df)

    encoder = OrdinalEncoder(
        categories=[CATEGORY_ORDERS[c] for c in CATEGORICAL_FEATURE_COLS],
        handle_unknown="use_encoded_value",
        unknown_value=-1,
    )

    cat_encoded = encoder.fit_transform(df[CATEGORICAL_FEATURE_COLS])
    cat_df = pd.DataFrame(
        cat_encoded,
        columns=CATEGORICAL_FEATURE_COLS,
        index=df.index,
    )

    numeric_df = df[NUMERIC_FEATURE_COLS].reset_index(drop=False).set_index("index") \
        if "index" not in df.columns else df[NUMERIC_FEATURE_COLS]
    # Simpler: just reindex to match
    numeric_df = df[NUMERIC_FEATURE_COLS].copy()

    X = pd.concat([cat_df, numeric_df], axis=1)

    y = df[TARGET_COL].copy() if TARGET_COL in df.columns else None

    return X, y


def build_features_for_prediction(record: dict[str, Any]) -> pd.DataFrame:
    """
    Builds a single-row feature DataFrame from an API request dict.

    Accepts the raw field names used in the dataset. Returns a DataFrame
    with the same columns as build_features() produces, ready for model.predict().
    """
    row = {col: record.get(col) for col in CATEGORICAL_FEATURE_COLS + NUMERIC_FEATURE_COLS}
    df = pd.DataFrame([row])
    X, _ = build_features(df)
    return X


def _assert_no_leakage(df: pd.DataFrame) -> None:
    """
    Raises ValueError if any forbidden column would enter the feature matrix.

    This runs every time build_features() is called so leakage cannot
    be introduced silently at runtime.
    """
    present_forbidden = FORBIDDEN_COLS & set(df.columns)
    # Forbidden columns may be present in df (e.g. the target during training)
    # but they must not appear in ALL_FEATURE_COLS.
    leaked = present_forbidden & set(ALL_FEATURE_COLS)
    if leaked:
        raise ValueError(
            f"Leakage detected: the following columns appear in both the "
            f"feature list and the forbidden set: {sorted(leaked)}. "
            f"Remove them from ALL_FEATURE_COLS in src/features.py."
        )
