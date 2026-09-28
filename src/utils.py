"""
Shared utility functions used across pipeline, EDA, and model modules.
"""

from __future__ import annotations

import pandas as pd


EXPECTED_COLUMNS = [
    "Type of Food",
    "Number of Guests",
    "Event Type",
    "Quantity of Food",
    "Storage Conditions",
    "Purchase History",
    "Seasonality",
    "Preparation Method",
    "Geographical Location",
    "Pricing",
    "Wastage Food Amount",
]

CATEGORICAL_COLUMNS = [
    "Type of Food",
    "Event Type",
    "Storage Conditions",
    "Purchase History",
    "Seasonality",
    "Preparation Method",
    "Geographical Location",
    "Pricing",
]

NUMERIC_COLUMNS = [
    "Number of Guests",
    "Quantity of Food",
    "Wastage Food Amount",
]

KNOWN_CATEGORIES: dict[str, set[str]] = {
    "Type of Food": {"Meat", "Baked Goods", "Dairy Products", "Fruits", "Vegetables"},
    "Event Type": {"Corporate", "Social Gathering", "Wedding", "Birthday"},
    "Storage Conditions": {"Refrigerated", "Room Temperature"},
    "Purchase History": {"Regular", "Occasional"},
    "Seasonality": {"Winter", "Summer", "All Seasons"},
    "Preparation Method": {"Sit-down Dinner", "Finger Food", "Buffet"},
    "Geographical Location": {"Suburban", "Urban", "Rural"},
    "Pricing": {"High", "Moderate", "Low"},
}

# Wastage % threshold for "high waste" classification in EDA
HIGH_WASTE_THRESHOLD_PCT = 10.0


def compute_wastage_pct(df: pd.DataFrame) -> pd.Series:
    """
    Derive wastage % from the two source columns.

    Returns NaN where Quantity of Food is zero rather than dividing
    by zero or producing infinity. This is the single authoritative
    computation; callers must not inline the formula.
    """
    prepared = df["Quantity of Food"].replace(0, float("nan"))
    return df["Wastage Food Amount"] / prepared * 100.0
