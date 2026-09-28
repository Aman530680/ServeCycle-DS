"""
Entry point for the data pipeline.

Usage:
    python -m src.pipeline

Sequence:
    1. Load data/raw/dataset.csv
    2. Validate schema — halt if required columns are missing
    3. Run constraint checks
    4. Assign flag columns
    5. Apply exclusions
    6. Write data/processed/clean_events.csv
    7. Write reports/flagged_rows.csv
    8. Write reports/data_quality_report.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from src.clean import assign_flags, apply_exclusions, ALL_FLAG_COLUMNS
from src.utils import (
    EXPECTED_COLUMNS,
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    KNOWN_CATEGORIES,
    compute_wastage_pct,
)
from src.validate import validate_schema, validate_constraints

RAW_PATH = Path("data/raw/dataset.csv")
PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")
CLEAN_CSV = PROCESSED_DIR / "clean_events.csv"
FLAGGED_CSV = REPORTS_DIR / "flagged_rows.csv"
QUALITY_REPORT = REPORTS_DIR / "data_quality_report.md"


def load_raw() -> pd.DataFrame:
    if not RAW_PATH.exists():
        sys.exit(
            f"ERROR: Dataset not found at '{RAW_PATH}'. "
            "Place the source file at data/raw/dataset.csv before running the pipeline."
        )
    return pd.read_csv(RAW_PATH)


def _build_quality_report(
    df_raw: pd.DataFrame,
    schema_ok: bool,
    schema_messages: list[str],
    val_result,
    clean_result,
) -> str:
    lines: list[str] = []

    lines += [
        "# Data Quality Report",
        "",
        "## 1. Dataset summary",
        "",
        f"- Source: `{RAW_PATH}`",
        f"- Rows: {df_raw.shape[0]}",
        f"- Columns: {df_raw.shape[1]}",
        "",
        "### Column names and dtypes",
        "",
        "| Column | Dtype |",
        "|---|---|",
    ]
    for col in df_raw.columns:
        lines.append(f"| {col} | {df_raw[col].dtype} |")

    lines += [
        "",
        "### Numeric column summary",
        "",
        "| Column | Min | Max | Mean | Std |",
        "|---|---|---|---|---|",
    ]
    for col in NUMERIC_COLUMNS:
        if col in df_raw.columns:
            s = df_raw[col]
            lines.append(
                f"| {col} | {s.min():.1f} | {s.max():.1f} | {s.mean():.2f} | {s.std():.2f} |"
            )

    lines += [
        "",
        "## 2. Column comparison (expected vs actual)",
        "",
    ]
    actual_cols = set(df_raw.columns)
    expected_cols = set(EXPECTED_COLUMNS)
    missing_cols = sorted(expected_cols - actual_cols)
    unexpected_cols = sorted(actual_cols - expected_cols)

    if schema_ok:
        lines.append("All expected columns are present.")
    else:
        for msg in schema_messages:
            lines.append(f"- {msg}")

    if unexpected_cols:
        lines.append(f"- Unexpected columns present: {unexpected_cols}")

    lines += [
        "",
        "## 3. Distinct values per categorical column",
        "",
    ]
    for col in CATEGORICAL_COLUMNS:
        if col not in df_raw.columns:
            continue
        vals = sorted(df_raw[col].dropna().unique().tolist())
        lines.append(f"**{col}** ({len(vals)} distinct): {vals}")
        lines.append("")

    lines += [
        "## 4. Constraint check results",
        "",
    ]
    if not val_result.issues:
        lines.append("No constraint issues found.")
    else:
        for issue in val_result.issues:
            lines += [
                f"### {issue.check_name}",
                f"- Rows affected: {issue.row_count}",
                f"- Detail: {issue.detail}",
                f"- Treatment: {issue.treatment}",
                "",
            ]

    lines += [
        "## 5. Row-count reconciliation",
        "",
        "| Metric | Count |",
        "|---|---|",
    ]
    rec = clean_result.reconciliation
    lines.append(f"| Raw rows in | {rec['raw_in']} |")
    lines.append(f"| Rows with any flag | {rec['rows_with_any_flag']} |")
    for col in ALL_FLAG_COLUMNS:
        lines.append(f"| {col} | {rec.get(col, 0)} |")
    lines.append(f"| Rows excluded from training | {rec['rows_excluded_from_training']} |")
    lines.append(f"| Rows available for training | {rec['rows_available_for_training']} |")

    return "\n".join(lines) + "\n"


def run() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading raw dataset...")
    df_raw = load_raw()
    print(f"  {len(df_raw)} rows, {len(df_raw.columns)} columns")

    print("Validating schema...")
    schema_ok, schema_messages = validate_schema(df_raw)
    if not schema_ok:
        for msg in schema_messages:
            print(f"  SCHEMA ERROR: {msg}")
        sys.exit(
            "Pipeline halted: required columns are missing. "
            "Check the error messages above and verify the source file."
        )
    print("  Schema valid.")

    print("Running constraint checks...")
    val_result = validate_constraints(df_raw)
    if val_result.has_issues:
        print(f"  {len(val_result.issues)} issue type(s) found:")
        for issue in val_result.issues:
            print(f"    [{issue.check_name}] {issue.row_count} rows")
    else:
        print("  No constraint issues found.")

    print("Assigning flags...")
    flagged_df = assign_flags(df_raw, val_result)

    print("Applying exclusions...")
    clean_result = apply_exclusions(flagged_df)
    rec = clean_result.reconciliation
    print(f"  {rec['raw_in']} raw rows in")
    print(f"  {rec['rows_with_any_flag']} rows with at least one flag")
    print(f"  {rec['rows_excluded_from_training']} rows excluded from training")
    print(f"  {rec['rows_available_for_training']} rows available for training")

    print(f"Writing {CLEAN_CSV}...")
    clean_result.flagged_df.to_csv(CLEAN_CSV, index=False)

    if len(clean_result.excluded_df) > 0:
        print(f"Writing {FLAGGED_CSV}...")
        clean_result.excluded_df.to_csv(FLAGGED_CSV, index=False)
    else:
        print("  No excluded rows — flagged_rows.csv not written.")

    print(f"Writing {QUALITY_REPORT}...")
    report_text = _build_quality_report(
        df_raw, schema_ok, schema_messages, val_result, clean_result
    )
    QUALITY_REPORT.write_text(report_text, encoding="utf-8")

    print("Pipeline complete.")


if __name__ == "__main__":
    run()
