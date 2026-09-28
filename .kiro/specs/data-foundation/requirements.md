# Spec 1: data-foundation — Requirements

## Dataset reality

The source file `data/raw/dataset.csv` contains 1,782 records of catering events. It does **not** match the originally described restaurant outlet/product schema. The actual columns are:

| Column | Type | Distinct values |
|---|---|---|
| Type of Food | categorical | Meat, Baked Goods, Dairy Products, Fruits, Vegetables |
| Number of Guests | integer | 207 – 491 |
| Event Type | categorical | Corporate, Social Gathering, Wedding, Birthday |
| Quantity of Food | integer | 280 – 500 (units prepared) |
| Storage Conditions | categorical | Refrigerated, Room Temperature |
| Purchase History | categorical | Regular, Occasional |
| Seasonality | categorical | Winter, Summer, All Seasons |
| Preparation Method | categorical | Sit-down Dinner, Finger Food, Buffet |
| Geographical Location | categorical | Suburban, Urban, Rural |
| Pricing | categorical | High, Moderate, Low |
| Wastage Food Amount | integer | 10 – 63 (units discarded) |

There is no Date, Outlet_ID, Product_ID, Quantity_Sold, Weather, Weekday, Holiday, Promotion, or Special_Event column. All requirements below are written against what actually exists. No requirement invents data that is not present.

---

## 1. Dataset inspection

**REQ-1.1**
WHEN the pipeline entry point is invoked, THE SYSTEM SHALL load `data/raw/dataset.csv`, report its shape (rows, columns), column names, inferred dtypes, and the min/max/mean/std of all numeric columns, and write this summary to `reports/data_quality_report.md`.

**REQ-1.2**
WHEN the dataset is loaded, THE SYSTEM SHALL compare the actual column names against the expected set defined in this spec and report any columns that are present but unexpected, or expected but absent, as named discrepancies in `reports/data_quality_report.md`.

**REQ-1.3**
WHEN the pipeline is run, THE SYSTEM SHALL report the count of distinct values for every categorical column (Type of Food, Event Type, Storage Conditions, Purchase History, Seasonality, Preparation Method, Geographical Location, Pricing) and list the distinct values explicitly.

**REQ-1.4**
WHEN `data/raw/dataset.csv` does not exist at pipeline start, THE SYSTEM SHALL halt immediately, print a specific error message stating the expected path, and exit with a non-zero code. It shall not create, invent, or substitute any data.

---

## 2. Data engineering pipeline

**REQ-2.1**
THE SYSTEM SHALL provide a single command-line entry point (`python -m src.pipeline`) that executes the full sequence: load raw → schema validation → constraint checks → cleaning → flag assignment → export processed dataset. Each stage shall be a separate function in a separate module.

**REQ-2.2**
WHEN schema validation runs, THE SYSTEM SHALL verify that all eleven expected columns are present and that each has an acceptable dtype (numeric for Number of Guests, Quantity of Food, Wastage Food Amount; string/object for all categoricals). Any column with the wrong dtype shall be reported by name with its actual dtype.

**REQ-2.3**
WHEN constraint checks run, THE SYSTEM SHALL check for and report each of the following independently:

- (a) Missing values in any column, reported as count and percentage per column.
- (b) Fully duplicate rows (all eleven columns identical), reported as count.
- (c) Negative values in Number of Guests, Quantity of Food, or Wastage Food Amount, reported as count and row indices.
- (d) Zero values in Quantity of Food (prepared quantity cannot be zero; wastage % is undefined), reported as count and row indices.
- (e) Rows where Wastage Food Amount exceeds Quantity of Food (discarded more than prepared), reported as count and row indices.
- (f) Rows where Wastage Food Amount equals zero (possible but notable; investigate whether systematic), reported as count.
- (g) Values in any categorical column not in the known distinct-value set established during inspection, reported by column and value.
- (h) Outliers in Number of Guests, Quantity of Food, and Wastage Food Amount, identified using the IQR method (below Q1 − 1.5×IQR or above Q3 + 1.5×IQR), flagged but not removed by default.

**REQ-2.4**
WHEN a problem row is identified, THE SYSTEM SHALL flag it with a boolean column (`flag_duplicate`, `flag_negative_qty`, `flag_zero_prepared`, `flag_wastage_exceeds_prepared`, `flag_outlier_guests`, `flag_outlier_qty_food`, `flag_outlier_wastage`, `flag_unknown_category`) rather than silently removing it. Each flag column shall be present in `data/processed/clean_events.csv` for every row, defaulting to False.

**REQ-2.5**
WHEN cleaning runs, THE SYSTEM SHALL apply the following documented treatments and record the reason for each in `reports/data_quality_report.md`:

- Duplicate rows: keep the first occurrence, exclude subsequent duplicates from analysis but retain them in `reports/flagged_rows.csv`.
- Zero Quantity of Food: exclude from all analyses that compute wastage % (division by zero); retain in the processed file with flag set.
- Wastage exceeds prepared: flag and retain; investigate in EDA; do not silently correct.
- Negative quantities: flag and exclude from model training; document count.
- Unknown category values: flag and retain; list in the quality report.
- Outliers: flag and retain; EDA notebook shall report whether they skew results.

**REQ-2.6**
WHEN the pipeline completes, THE SYSTEM SHALL write a row-count reconciliation to `reports/data_quality_report.md` stating: raw row count in, rows flagged by each flag type, rows excluded from model training, rows in `data/processed/clean_events.csv`.

**REQ-2.7**
WHEN the pipeline completes, THE SYSTEM SHALL write `reports/flagged_rows.csv` containing all rows that carry at least one True flag, with all original columns plus all flag columns.

**REQ-2.8**
WHEN wastage % is computed anywhere in the codebase, THE SYSTEM SHALL compute it as `Wastage_Food_Amount / Quantity_of_Food * 100` and handle zero Quantity_of_Food explicitly by returning NaN (not zero, not infinity). Wastage % shall never be stored as a column in the processed file; it shall always be derived on demand.

**REQ-2.9**
THE SYSTEM SHALL include Pytest tests covering: schema validation rejects a dataset missing a required column; constraint check detects a negative quantity; constraint check detects wastage exceeding prepared; cleaning produces the correct flag columns; wastage % returns NaN when Quantity of Food is zero; row-count reconciliation arithmetic is correct.

---

## 3. MySQL schema and loader

**REQ-3.1**
THE SYSTEM SHALL deliver `backend/db/schema.sql` containing idempotent `CREATE TABLE IF NOT EXISTS` statements for the following tables only — no tables are created for data that does not exist in the dataset:

- `food_categories (id, name)` — lookup for the five food types.
- `event_records (id, food_category_id FK, num_guests, event_type, qty_prepared, storage_conditions, purchase_history, seasonality, preparation_method, geographical_location, pricing, wastage_amount, flag_duplicate, flag_negative_qty, flag_zero_prepared, flag_wastage_exceeds_prepared, flag_outlier_guests, flag_outlier_qty_food, flag_outlier_wastage, flag_unknown_category)` — one row per catering event.
- `model_runs (id, run_timestamp, features_json, train_rows, test_rows, mae, rmse, r2, wape, library_versions_json)` — populated at training time.
- `predictions (id, model_run_id FK, event_record_id FK, predicted_wastage, created_at)` — populated by the API.
- `recommendations (id, event_record_id FK, predicted_wastage, recommended_qty, service_level, created_at)` — populated by the recommendation engine.

**REQ-3.2**
THE SYSTEM SHALL use appropriate MySQL column types: TINYINT UNSIGNED for flag columns; SMALLINT UNSIGNED for guest and quantity counts; DECIMAL(6,2) for metrics; VARCHAR with a stated max length for all categorical columns; TIMESTAMP for audit columns.

**REQ-3.3**
`event_records` SHALL have a primary key on `id` and an index on `food_category_id`, `event_type`, `geographical_location`, and `pricing` to support the filter patterns used in EDA queries.

**REQ-3.4**
THE SYSTEM SHALL deliver an idempotent loader script (`src/pipeline.py` or a dedicated `src/loader.py`) that reads `data/processed/clean_events.csv` and inserts all rows into MySQL using upsert semantics (INSERT … ON DUPLICATE KEY UPDATE), so it can be re-run without creating duplicate rows.

**REQ-3.5**
THE SYSTEM SHALL deliver a SQL view `v_wastage_pct` defined as:

```sql
SELECT
    id,
    food_category_id,
    event_type,
    qty_prepared,
    wastage_amount,
    CASE WHEN qty_prepared > 0
         THEN wastage_amount / qty_prepared * 100.0
         ELSE NULL
    END AS wastage_pct
FROM event_records;
```

**REQ-3.6**
THE SYSTEM SHALL deliver a verification script that queries MySQL after loading and confirms: total row count matches `data/processed/clean_events.csv`, sum of `qty_prepared` matches, sum of `wastage_amount` matches. Any mismatch shall cause the script to exit with a non-zero code and a specific message.

---

## 4. EDA (queried from MySQL, documented in notebooks)

All EDA queries run against MySQL. Notebooks import from `src/` for any shared logic. Charts are produced with Matplotlib/Seaborn, saved as PNGs to `outputs/`, and embedded in the notebook with a title that states what is shown and the units.

**REQ-4.1 — Overall wastage profile**
WHEN the EDA notebook runs, THE SYSTEM SHALL compute and display: total events, total units prepared, total units wasted, overall wastage % (derived, not stored), min/max/mean/median/std of wastage %, and the distribution of wastage % as a histogram.

**REQ-4.2 — Wastage by food type**
THE SYSTEM SHALL compute per food type: count of events, mean wastage %, median wastage %, standard deviation, and share of events where wastage % exceeds a stated threshold (10%). Ranking shall use mean wastage %, not total waste volume, because volume conflates high-waste rate with high frequency. The chart (bar chart, wastage % on y-axis, food type on x-axis, n per bar labelled) SHALL be saved to `outputs/waste_by_food_type.png`.

**REQ-4.3 — Wastage by event type**
THE SYSTEM SHALL compute per event type: count of events, mean wastage %, median wastage %, standard deviation. The chart SHALL be saved to `outputs/waste_by_event_type.png`.

**REQ-4.4 — Wastage by preparation method**
THE SYSTEM SHALL compute per preparation method: count of events, mean wastage %, median wastage %, standard deviation, and an effect size (Cohen's d or eta-squared) comparing the group with the highest mean to the group with the lowest. Sample sizes shall be stated alongside every comparison.

**REQ-4.5 — Wastage by storage conditions**
THE SYSTEM SHALL compare Refrigerated vs Room Temperature: count of events in each group, mean wastage %, 95% bootstrap confidence interval on the mean difference, and a note that storage conditions may be correlated with food type (confounding), investigated by a two-way breakdown of food type × storage conditions.

**REQ-4.6 — Wastage by pricing tier**
THE SYSTEM SHALL compute per pricing tier: count of events, mean wastage %, median wastage %, and a check for whether pricing is unevenly distributed across event types (which would confound a simple pricing effect). The chart (wastage % by pricing tier, n labelled) SHALL be saved to `outputs/waste_by_pricing.png`.

**REQ-4.7 — Wastage by geographical location**
THE SYSTEM SHALL compute per location: count of events, mean wastage %, median wastage %, standard deviation.

**REQ-4.8 — Wastage by seasonality**
THE SYSTEM SHALL compute per season: count of events, mean wastage %, median wastage %, standard deviation, and a note on the meaning of "All Seasons" as a category.

**REQ-4.9 — Wastage by guest count band**
THE SYSTEM SHALL bin Number of Guests into quartile-based bands, compute mean wastage % per band, and report whether higher guest counts are associated with lower or higher wastage % (with the Pearson correlation coefficient and its p-value, with a caveat on the linear assumption).

**REQ-4.10 — Consistently high-waste combinations**
THE SYSTEM SHALL identify food type × event type combinations with consistently high wastage using all of: count of events (minimum 10 observations), mean wastage %, coefficient of variation of wastage %, and share of events exceeding the 10% threshold. Rankings shall not use total waste volume alone. Results shall be presented as a heatmap (food type × event type, cell colour = mean wastage %) saved to `outputs/wastage_heatmap.png`.

**REQ-4.11 — Purchase history effect**
THE SYSTEM SHALL compare Regular vs Occasional purchase history: count of events, mean wastage %, and a bootstrap significance check. A note shall state whether Occasional events are concentrated in a particular food type or event type.

**REQ-4.12 — Confounding investigation**
THE SYSTEM SHALL produce a cross-tabulation of Preparation Method × Event Type and of Storage Conditions × Food Type to surface the main confounders. Each EDA comparison that has a plausible confounder shall call it out explicitly in the notebook markdown.

**REQ-4.13 — Required chart outputs**
The following four charts are required for the assignment and shall be produced, saved as PNGs in `outputs/`, and labelled with titles and units:

1. `outputs/waste_by_food_type.png` — mean wastage % by food type, n per bar labelled.
2. `outputs/waste_by_event_type.png` — mean wastage % by event type, n per bar labelled.
3. `outputs/waste_by_pricing.png` — mean wastage % by pricing tier, n per bar labelled.
4. `outputs/wastage_heatmap.png` — food type × event type mean wastage % heatmap.

---

## Open questions

The following items are noted for discussion before design is approved. They do not block writing this requirements file but must be resolved before tasks.md is written.

**Q1 — Quantity of Food as a feature.**
`Quantity of Food` (units prepared) is available in the dataset. It is excluded from model features in the tech steering file because it is itself a preparation decision. However, in the context of this dataset (which records historical events, not future plans), it may be a legitimate explanatory variable for EDA. Confirm: should it appear only in EDA (as a covariate) and never in model features, or should it be excluded from EDA comparisons as well?

**Q2 — Recommendation framing.**
Without a Quantity_Sold column, there is no observed demand to compare against. The recommendation engine can only suggest a preparation quantity based on predicted wastage relative to guests — it cannot compute a stockout rate. Confirm the framing: "given N guests and this event context, prepare X units, which historically produces approximately Y% wastage" — is that the right output, or do you want something different?

**Q3 — MySQL hosting.**
The tech steering requires MySQL 8+. Confirm whether a local MySQL instance is available, or whether the loader should also support a connection string that points to a remote host (already handled via .env, but confirm the assumption).

**Q4 — Notebook format.**
Confirm whether notebooks should be standard `.ipynb` Jupyter notebooks or Python scripts with `# %%` cell markers (compatible with VS Code's notebook renderer without requiring Jupyter server).
