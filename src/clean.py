"""
Applies flags and exclusion logic to the raw DataFrame.

Takes the raw DataFrame and a ValidationResult, adds boolean flag columns,
and separates rows excluded from model training. Does not remove any rows
from the processed output — the analyst sees everything.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.validate import ValidationResult


# Maps check_name prefixes from ValidationResult to flag column names.
# Checks with multiple sub-checks (e.g. per-column unknown categories)
# are consolidated into a single flag column.
_CHECK_TO_FLAG: dict[str, str] = {
    "missing_values": "flag_missing",
    "duplicate_rows": "flag_duplicate",
    "negative_quantities": "flag_negative_qty",
    "zero_prepared": "flag_zero_prepared",
    "wastage_exceeds_prepared": "flag_wastage_exceeds_prepared",
    "flag_outlier_guests": "flag_outlier_guests",
    "flag_outlier_qty_food": "flag_outlier_qty_food",
    "flag_outlier_wastage": "flag_outlier_wastage",
}

# Checks whose name starts with this prefix map to flag_unknown_category.
_UNKNOWN_CATEGORY_PREFIX = "unknown_category_"

# Flag columns that disqualify a row from model training.
_EXCLUSION_FLAGS = {
    "flag_missing",
    "flag_duplicate",
    "flag_negative_qty",
    "flag_zero_prepared",
    "flag_wastage_exceeds_prepared",
}

ALL_FLAG_COLUMNS = [
    "flag_missing",
    "flag_duplicate",
    "flag_negative_qty",
    "flag_zero_prepared",
    "flag_wastage_exceeds_prepared",
    "flag_outlier_guests",
    "flag_outlier_qty_food",
    "flag_outlier_wastage",
    "flag_unknown_category",
]


@dataclass
class CleanResult:
    flagged_df: pd.DataFrame      # All rows with flag columns added
    excluded_df: pd.DataFrame     # Rows excluded from model training
    reconciliation: dict[str, int]


def assign_flags(df: pd.DataFrame, result: ValidationResult) -> pd.DataFrame:
    """
    Adds boolean flag columns to the DataFrame based on ValidationResult.

    All flag columns default to False. Rows with issues are set to True
    for the relevant flag. The original columns are never modified.
    """
    out = df.copy()
    for col in ALL_FLAG_COLUMNS:
        out[col] = False

    for issue in result.issues:
        flag_col = _resolve_flag_column(issue.check_name)
        if flag_col is None:
            continue
        if issue.row_indices:
            out.loc[issue.row_indices, flag_col] = True

    return out


def apply_exclusions(flagged_df: pd.DataFrame) -> CleanResult:
    """
    Separates rows excluded from model training.

    Rows are excluded if any exclusion flag is True. All rows remain in
    flagged_df so the analyst can audit them.
    """
    present_exclusion_flags = [
        c for c in _EXCLUSION_FLAGS if c in flagged_df.columns
    ]
    if present_exclusion_flags:
        excluded_mask = flagged_df[present_exclusion_flags].any(axis=1)
    else:
        excluded_mask = pd.Series(False, index=flagged_df.index)

    excluded_df = flagged_df[excluded_mask].copy()

    any_flag_mask = flagged_df[ALL_FLAG_COLUMNS].any(axis=1)

    reconciliation = {
        "raw_in": len(flagged_df),
        "rows_with_any_flag": int(any_flag_mask.sum()),
        "rows_excluded_from_training": int(excluded_mask.sum()),
        "rows_available_for_training": int((~excluded_mask).sum()),
    }
    for col in ALL_FLAG_COLUMNS:
        reconciliation[col] = int(flagged_df[col].sum())

    return CleanResult(
        flagged_df=flagged_df,
        excluded_df=excluded_df,
        reconciliation=reconciliation,
    )


def _resolve_flag_column(check_name: str) -> str | None:
    if check_name in _CHECK_TO_FLAG:
        return _CHECK_TO_FLAG[check_name]
    if check_name.startswith(_UNKNOWN_CATEGORY_PREFIX):
        return "flag_unknown_category"
    # Outlier checks have their own check_name that matches the flag name directly.
    if check_name in ALL_FLAG_COLUMNS:
        return check_name
    return None
