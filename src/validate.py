"""
Schema and constraint validation for the raw catering events dataset.

All functions are pure: they read the DataFrame and return results without
mutating it. Each check is independent so failures do not mask others.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.utils import (
    CATEGORICAL_COLUMNS,
    EXPECTED_COLUMNS,
    KNOWN_CATEGORIES,
    NUMERIC_COLUMNS,
)


@dataclass
class Issue:
    check_name: str
    row_count: int
    row_indices: list[int]
    detail: str
    treatment: str


@dataclass
class ValidationResult:
    schema_ok: bool
    issues: list[Issue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def summary(self) -> str:
        lines = [f"Schema valid: {self.schema_ok}"]
        if not self.issues:
            lines.append("No constraint issues found.")
        for issue in self.issues:
            lines.append(
                f"  [{issue.check_name}] {issue.row_count} rows — {issue.detail}"
            )
        return "\n".join(lines)


def validate_schema(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Check that all expected columns are present.

    Returns (ok, messages) where messages lists missing and unexpected columns.
    Does not check dtypes — that is handled in validate_constraints.
    """
    actual = set(df.columns.tolist())
    expected = set(EXPECTED_COLUMNS)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)

    messages: list[str] = []
    if missing:
        messages.append(f"Missing columns: {missing}")
    if unexpected:
        messages.append(f"Unexpected columns (not in spec): {unexpected}")

    return len(missing) == 0, messages


def validate_constraints(df: pd.DataFrame) -> ValidationResult:
    """
    Run all constraint checks against the DataFrame.

    Each check is isolated. A failure in one does not skip the others.
    """
    result = ValidationResult(schema_ok=True)
    _check_missing_values(df, result)
    _check_duplicate_rows(df, result)
    _check_negative_quantities(df, result)
    _check_zero_prepared(df, result)
    _check_wastage_exceeds_prepared(df, result)
    _check_zero_wastage(df, result)
    _check_unknown_categories(df, result)
    _check_outliers(df, result)
    return result


def _check_missing_values(df: pd.DataFrame, result: ValidationResult) -> None:
    counts = df.isnull().sum()
    cols_with_nulls = counts[counts > 0]
    if cols_with_nulls.empty:
        return
    detail_parts = [f"{col}: {n}" for col, n in cols_with_nulls.items()]
    indices = df[df.isnull().any(axis=1)].index.tolist()
    result.issues.append(
        Issue(
            check_name="missing_values",
            row_count=len(indices),
            row_indices=indices,
            detail="Null values found — " + ", ".join(detail_parts),
            treatment="Flag with flag_missing; exclude from model training.",
        )
    )


def _check_duplicate_rows(df: pd.DataFrame, result: ValidationResult) -> None:
    # Identifies all rows after the first occurrence of each duplicate group.
    dupe_mask = df.duplicated(keep="first")
    indices = df[dupe_mask].index.tolist()
    if not indices:
        return
    result.issues.append(
        Issue(
            check_name="duplicate_rows",
            row_count=len(indices),
            row_indices=indices,
            detail="Fully duplicate rows (all 11 columns identical).",
            treatment="Keep first occurrence. Exclude subsequent duplicates from analysis. Retain in flagged_rows.csv.",
        )
    )


def _check_negative_quantities(df: pd.DataFrame, result: ValidationResult) -> None:
    mask = (
        (df["Number of Guests"] < 0)
        | (df["Quantity of Food"] < 0)
        | (df["Wastage Food Amount"] < 0)
    )
    indices = df[mask].index.tolist()
    if not indices:
        return
    result.issues.append(
        Issue(
            check_name="negative_quantities",
            row_count=len(indices),
            row_indices=indices,
            detail="One or more of Number of Guests, Quantity of Food, Wastage Food Amount is negative.",
            treatment="Flag with flag_negative_qty; exclude from model training.",
        )
    )


def _check_zero_prepared(df: pd.DataFrame, result: ValidationResult) -> None:
    mask = df["Quantity of Food"] == 0
    indices = df[mask].index.tolist()
    if not indices:
        return
    result.issues.append(
        Issue(
            check_name="zero_prepared",
            row_count=len(indices),
            row_indices=indices,
            detail="Quantity of Food is zero — wastage % is undefined for these rows.",
            treatment="Flag with flag_zero_prepared; exclude from wastage % computations and model training.",
        )
    )


def _check_wastage_exceeds_prepared(df: pd.DataFrame, result: ValidationResult) -> None:
    mask = df["Wastage Food Amount"] > df["Quantity of Food"]
    indices = df[mask].index.tolist()
    if not indices:
        return
    result.issues.append(
        Issue(
            check_name="wastage_exceeds_prepared",
            row_count=len(indices),
            row_indices=indices,
            detail="Wastage Food Amount > Quantity of Food — physically impossible.",
            treatment="Flag with flag_wastage_exceeds_prepared; retain in dataset for investigation; exclude from model training.",
        )
    )


def _check_zero_wastage(df: pd.DataFrame, result: ValidationResult) -> None:
    mask = df["Wastage Food Amount"] == 0
    indices = df[mask].index.tolist()
    if not indices:
        return
    result.issues.append(
        Issue(
            check_name="zero_wastage",
            row_count=len(indices),
            row_indices=indices,
            detail="Wastage Food Amount is zero — notable; investigate whether systematic.",
            treatment="Retain; flag informally in EDA. Not flagged as invalid.",
        )
    )


def _check_unknown_categories(df: pd.DataFrame, result: ValidationResult) -> None:
    for col, known in KNOWN_CATEGORIES.items():
        if col not in df.columns:
            continue
        unknown_mask = ~df[col].isin(known)
        unknown_values = df.loc[unknown_mask, col].unique().tolist()
        if not unknown_values:
            continue
        indices = df[unknown_mask].index.tolist()
        result.issues.append(
            Issue(
                check_name=f"unknown_category_{col.lower().replace(' ', '_')}",
                row_count=len(indices),
                row_indices=indices,
                detail=f"Column '{col}' has values not in known set: {unknown_values}",
                treatment="Flag with flag_unknown_category; retain; list in quality report.",
            )
        )


def _check_outliers(df: pd.DataFrame, result: ValidationResult) -> None:
    flag_map = {
        "Number of Guests": "flag_outlier_guests",
        "Quantity of Food": "flag_outlier_qty_food",
        "Wastage Food Amount": "flag_outlier_wastage",
    }
    for col, flag_name in flag_map.items():
        if col not in df.columns:
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (df[col] < lower) | (df[col] > upper)
        indices = df[mask].index.tolist()
        if not indices:
            continue
        result.issues.append(
            Issue(
                check_name=flag_name,
                row_count=len(indices),
                row_indices=indices,
                detail=(
                    f"'{col}' outliers by IQR method "
                    f"(bounds: [{lower:.1f}, {upper:.1f}])."
                ),
                treatment="Flag; retain by default. EDA notebook reports whether they skew results.",
            )
        )
