"""
Tests for src/clean.py — flagging and exclusion logic.
"""

import pandas as pd
import pytest

from src.clean import assign_flags, apply_exclusions, ALL_FLAG_COLUMNS
from src.utils import compute_wastage_pct
from src.validate import validate_constraints


def _base_df() -> pd.DataFrame:
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


class TestAssignFlags:
    def test_clean_row_all_flags_false(self):
        df = _base_df()
        result = validate_constraints(df)
        flagged = assign_flags(df, result)
        for col in ALL_FLAG_COLUMNS:
            assert col in flagged.columns, f"Missing flag column: {col}"
            assert flagged[col].iloc[0] is False or flagged[col].iloc[0] == 0

    def test_duplicate_flag_set(self):
        df = pd.concat([_base_df(), _base_df()], ignore_index=True)
        result = validate_constraints(df)
        flagged = assign_flags(df, result)
        # First occurrence is clean; second is the duplicate
        assert flagged["flag_duplicate"].iloc[0] == False
        assert flagged["flag_duplicate"].iloc[1] == True

    def test_wastage_exceeds_prepared_flag_set(self):
        df = _base_df()
        df.loc[0, "Wastage Food Amount"] = 999
        result = validate_constraints(df)
        flagged = assign_flags(df, result)
        assert flagged["flag_wastage_exceeds_prepared"].iloc[0] == True

    def test_negative_qty_flag_set(self):
        df = _base_df()
        df.loc[0, "Quantity of Food"] = -1
        result = validate_constraints(df)
        flagged = assign_flags(df, result)
        assert flagged["flag_negative_qty"].iloc[0] == True

    def test_zero_prepared_flag_set(self):
        df = _base_df()
        df.loc[0, "Quantity of Food"] = 0
        result = validate_constraints(df)
        flagged = assign_flags(df, result)
        assert flagged["flag_zero_prepared"].iloc[0] == True

    def test_all_original_columns_preserved(self):
        df = _base_df()
        result = validate_constraints(df)
        flagged = assign_flags(df, result)
        for col in df.columns:
            assert col in flagged.columns


class TestApplyExclusions:
    def test_clean_row_not_excluded(self):
        df = _base_df()
        result = validate_constraints(df)
        flagged = assign_flags(df, result)
        clean_result = apply_exclusions(flagged)
        assert clean_result.reconciliation["rows_excluded_from_training"] == 0
        assert clean_result.reconciliation["rows_available_for_training"] == 1

    def test_duplicate_excluded(self):
        df = pd.concat([_base_df(), _base_df()], ignore_index=True)
        result = validate_constraints(df)
        flagged = assign_flags(df, result)
        clean_result = apply_exclusions(flagged)
        assert clean_result.reconciliation["rows_excluded_from_training"] == 1
        assert clean_result.reconciliation["rows_available_for_training"] == 1

    def test_reconciliation_arithmetic(self):
        df = pd.concat([_base_df(), _base_df()], ignore_index=True)
        result = validate_constraints(df)
        flagged = assign_flags(df, result)
        clean_result = apply_exclusions(flagged)
        rec = clean_result.reconciliation
        assert (
            rec["rows_excluded_from_training"] + rec["rows_available_for_training"]
            == rec["raw_in"]
        )

    def test_flagged_df_contains_all_rows(self):
        df = pd.concat([_base_df(), _base_df()], ignore_index=True)
        result = validate_constraints(df)
        flagged = assign_flags(df, result)
        clean_result = apply_exclusions(flagged)
        assert len(clean_result.flagged_df) == len(df)


class TestWastagePct:
    def test_normal_computation(self):
        df = _base_df()  # 30 / 400 * 100 = 7.5
        pct = compute_wastage_pct(df)
        assert abs(pct.iloc[0] - 7.5) < 0.001

    def test_zero_prepared_returns_nan(self):
        df = _base_df()
        df.loc[0, "Quantity of Food"] = 0
        pct = compute_wastage_pct(df)
        assert pd.isna(pct.iloc[0])

    def test_returns_series(self):
        df = _base_df()
        pct = compute_wastage_pct(df)
        assert isinstance(pct, pd.Series)
