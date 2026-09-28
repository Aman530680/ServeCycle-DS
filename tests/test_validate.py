"""
Tests for src/validate.py — schema and constraint checks.
"""

import pandas as pd
import pytest

from src.validate import validate_schema, validate_constraints
from src.utils import EXPECTED_COLUMNS


def _base_df() -> pd.DataFrame:
    """Minimal valid DataFrame with one clean row."""
    return pd.DataFrame([{
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
    }])


class TestValidateSchema:
    def test_valid_schema_passes(self):
        df = _base_df()
        ok, messages = validate_schema(df)
        assert ok is True
        assert messages == []

    def test_missing_column_fails(self):
        df = _base_df().drop(columns=["Wastage Food Amount"])
        ok, messages = validate_schema(df)
        assert ok is False
        assert any("Wastage Food Amount" in m for m in messages)

    def test_extra_column_does_not_fail_schema(self):
        df = _base_df()
        df["Extra Column"] = 1
        ok, messages = validate_schema(df)
        # Schema passes (expected columns are present); unexpected column is reported
        assert ok is True
        assert any("Unexpected" in m for m in messages)


class TestValidateConstraints:
    def test_clean_row_produces_no_issues(self):
        result = validate_constraints(_base_df())
        issue_names = [i.check_name for i in result.issues]
        # Clean row should have no constraint issues
        assert "negative_quantities" not in issue_names
        assert "zero_prepared" not in issue_names
        assert "wastage_exceeds_prepared" not in issue_names

    def test_negative_quantity_detected(self):
        df = _base_df()
        df.loc[0, "Quantity of Food"] = -10
        result = validate_constraints(df)
        names = [i.check_name for i in result.issues]
        assert "negative_quantities" in names

    def test_negative_guests_detected(self):
        df = _base_df()
        df.loc[0, "Number of Guests"] = -5
        result = validate_constraints(df)
        names = [i.check_name for i in result.issues]
        assert "negative_quantities" in names

    def test_zero_prepared_detected(self):
        df = _base_df()
        df.loc[0, "Quantity of Food"] = 0
        result = validate_constraints(df)
        names = [i.check_name for i in result.issues]
        assert "zero_prepared" in names

    def test_wastage_exceeds_prepared_detected(self):
        df = _base_df()
        df.loc[0, "Wastage Food Amount"] = 500
        df.loc[0, "Quantity of Food"] = 400
        result = validate_constraints(df)
        names = [i.check_name for i in result.issues]
        assert "wastage_exceeds_prepared" in names

    def test_duplicate_rows_detected(self):
        df = pd.concat([_base_df(), _base_df()], ignore_index=True)
        result = validate_constraints(df)
        names = [i.check_name for i in result.issues]
        assert "duplicate_rows" in names
        issue = next(i for i in result.issues if i.check_name == "duplicate_rows")
        assert issue.row_count == 1  # One duplicate (second occurrence)

    def test_unknown_category_detected(self):
        df = _base_df()
        df.loc[0, "Type of Food"] = "Insects"
        result = validate_constraints(df)
        names = [i.check_name for i in result.issues]
        assert any("unknown_category" in n for n in names)

    def test_row_indices_populated(self):
        df = _base_df()
        df.loc[0, "Wastage Food Amount"] = 999
        result = validate_constraints(df)
        issue = next(
            i for i in result.issues if i.check_name == "wastage_exceeds_prepared"
        )
        assert 0 in issue.row_indices
