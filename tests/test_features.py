"""
Tests for src/features.py — feature construction and leakage guard.
"""

import pandas as pd
import pytest

from src.features import (
    ALL_FEATURE_COLS,
    FORBIDDEN_COLS,
    TARGET_COL,
    build_features,
    build_features_for_prediction,
)


def _base_row() -> dict:
    return {
        "Type of Food": "Meat",
        "Number of Guests": 300,
        "Event Type": "Corporate",
        "Quantity of Food": 400,
        "Storage Conditions": "Refrigerated",
        "Purchase History": "Regular",
        "Seasonality": "Winter",
        "Preparation Method": "Buffet",
        "Geographical Location": "Urban",
        "Pricing": "High",
        "Wastage Food Amount": 30,
    }


class TestBuildFeatures:
    def test_returns_correct_columns(self):
        df = pd.DataFrame([_base_row()])
        X, y = build_features(df)
        assert list(X.columns) == ALL_FEATURE_COLS

    def test_target_returned_when_present(self):
        df = pd.DataFrame([_base_row()])
        _, y = build_features(df)
        assert y is not None
        assert len(y) == 1
        assert y.iloc[0] == 30

    def test_target_none_when_absent(self):
        row = {k: v for k, v in _base_row().items() if k != "Wastage Food Amount"}
        df = pd.DataFrame([row])
        _, y = build_features(df)
        assert y is None

    def test_forbidden_cols_not_in_features(self):
        df = pd.DataFrame([_base_row()])
        X, _ = build_features(df)
        for col in FORBIDDEN_COLS:
            assert col not in X.columns, f"Forbidden column '{col}' found in features."

    def test_quantity_of_food_not_in_features(self):
        df = pd.DataFrame([_base_row()])
        X, _ = build_features(df)
        assert "Quantity of Food" not in X.columns

    def test_wastage_food_amount_not_in_features(self):
        df = pd.DataFrame([_base_row()])
        X, _ = build_features(df)
        assert "Wastage Food Amount" not in X.columns

    def test_numeric_guests_passes_through(self):
        df = pd.DataFrame([_base_row()])
        X, _ = build_features(df)
        assert X["Number of Guests"].iloc[0] == 300

    def test_unknown_category_does_not_raise(self):
        row = _base_row()
        row["Type of Food"] = "Fish"  # not in known categories
        df = pd.DataFrame([row])
        # Should not raise; OrdinalEncoder encodes as -1 for unknown values
        X, _ = build_features(df)
        assert "Type of Food" in X.columns

    def test_multiple_rows(self):
        rows = [_base_row() for _ in range(5)]
        df = pd.DataFrame(rows)
        X, y = build_features(df)
        assert len(X) == 5
        assert len(y) == 5


class TestLeakageGuard:
    def test_leakage_guard_is_called(self):
        """
        The leakage guard is embedded in build_features and runs on every call.
        If the feature list were ever changed to include a forbidden column,
        it would raise ValueError immediately.
        """
        # This test verifies the guard does not fire on a clean feature list.
        df = pd.DataFrame([_base_row()])
        # Should not raise
        build_features(df)

    def test_forbidden_cols_defined(self):
        assert "Quantity of Food" in FORBIDDEN_COLS
        assert "Wastage Food Amount" in FORBIDDEN_COLS
        assert "wastage_pct" in FORBIDDEN_COLS


class TestBuildFeaturesForPrediction:
    def test_returns_single_row_dataframe(self):
        record = {k: v for k, v in _base_row().items() if k != "Wastage Food Amount"}
        X = build_features_for_prediction(record)
        assert isinstance(X, pd.DataFrame)
        assert len(X) == 1

    def test_columns_match_training(self):
        record = {k: v for k, v in _base_row().items() if k != "Wastage Food Amount"}
        X = build_features_for_prediction(record)
        assert list(X.columns) == ALL_FEATURE_COLS
