# Spec 1: data-foundation — Tasks

## T1 — src/ package scaffold
Create `src/__init__.py`. Confirm the package is importable as `from src.validate import validate_schema`.
Traces to: REQ-2.1

## T2 — validate.py
Implement `validate_schema(df)` and `validate_constraints(df)`. Return a `ValidationResult` dataclass.
Checks: column presence, dtypes, missing values, duplicates, negatives, zeros, wastage > prepared, unknown categories, outliers (IQR method).
Traces to: REQ-2.2, REQ-2.3

## T3 — clean.py
Implement `assign_flags(df, result)` and `apply_exclusions(df)`. Return a `CleanResult` dataclass with `flagged_df`, `excluded_df`, `reconciliation`.
Traces to: REQ-2.4, REQ-2.5, REQ-2.6, REQ-2.7

## T4 — Wastage % utility
Implement `compute_wastage_pct(df)` in `src/utils.py`. Returns a Series; returns NaN where qty_prepared == 0.
Traces to: REQ-2.8

## T5 — pipeline.py CLI
Implement `python -m src.pipeline` entry point. Orchestrates: load raw → validate → clean → write `data/processed/clean_events.csv` → write `reports/data_quality_report.md` → write `reports/flagged_rows.csv`.
Traces to: REQ-1.1, REQ-1.2, REQ-1.3, REQ-1.4, REQ-2.1, REQ-2.6, REQ-2.7

--- REVIEW: pipeline and data quality report complete ---

## T6 — backend/db/schema.sql
Write idempotent CREATE TABLE IF NOT EXISTS for: food_categories, event_records (with all flag columns), model_runs, predictions, recommendations. Add the v_wastage_pct view.
Traces to: REQ-3.1, REQ-3.2, REQ-3.3, REQ-3.5

## T7 — src/loader.py
Implement idempotent CSV → MySQL loader using SQLAlchemy Core. Upsert food_categories then event_records.
Traces to: REQ-3.4

## T8 — Verification script
Implement `src/verify_load.py`. Queries MySQL, compares row count and sums vs CSV. Exits non-zero on mismatch.
Traces to: REQ-3.6

--- REVIEW: MySQL loaded and verified ---

## T9 — 01_data_overview.ipynb
Notebook: load from MySQL, report shape, dtypes, distributions, flag summary. Save no charts (overview only).
Traces to: REQ-4.1

## T10 — 02_waste_analysis.ipynb
Notebook: wastage % by food type (save `outputs/waste_by_food_type.png`), by event type (save `outputs/waste_by_event_type.png`), by pricing (save `outputs/waste_by_pricing.png`), by location, by seasonality, by guest band, heatmap (save `outputs/wastage_heatmap.png`).
Traces to: REQ-4.2, REQ-4.3, REQ-4.6, REQ-4.7, REQ-4.8, REQ-4.9, REQ-4.10, REQ-4.13

## T11 — 03_drivers.ipynb
Notebook: preparation method (REQ-4.4), storage conditions with confounding check (REQ-4.5), purchase history (REQ-4.11), cross-tabulation confounders (REQ-4.12).
Traces to: REQ-4.4, REQ-4.5, REQ-4.11, REQ-4.12

## T12 — Pytest tests
Write tests in `tests/test_validate.py` and `tests/test_clean.py` covering all REQ-2.9 cases.
Traces to: REQ-2.9

--- REVIEW: EDA complete ---
