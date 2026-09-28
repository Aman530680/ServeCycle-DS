# Spec 1: data-foundation — Design

## Module boundaries

```
src/
├── __init__.py
├── pipeline.py      CLI entry point; orchestrates validate → clean → load
├── validate.py      Schema and constraint checks; returns a ValidationResult
├── clean.py         Applies flags and exclusions; returns a CleanResult
└── loader.py        Reads processed CSV, upserts into MySQL
```

Each module exposes pure functions that accept a DataFrame and return a result object. No module imports another's result type — data flows as DataFrames with added flag columns.

## Validation flow

```
raw DataFrame
    │
    ▼
validate_schema()       checks columns present, dtypes correct
    │
    ▼
validate_constraints()  checks negatives, zeros, wastage > prepared,
                        unknown categories, duplicate rows, outliers
    │
    ▼
ValidationResult        named fields: schema_ok, issues (list of Issue)
                        each Issue has: check_name, row_count, row_indices, treatment
```

`validate_constraints` is deterministic: same input always produces same output. It never mutates the DataFrame.

## Cleaning and flagging flow

```
raw DataFrame + ValidationResult
    │
    ▼
assign_flags()          adds boolean flag columns from ValidationResult
    │
    ▼
apply_exclusions()      marks rows excluded from model training
    │
    ▼
CleanResult             flagged_df (all rows + flag columns)
                        excluded_df (rows excluded from training)
                        reconciliation dict (raw_in, flagged_n, excluded_n, clean_out)
```

`clean_events.csv` contains all rows — flagged and unflagged — so the analyst can inspect everything. Model training reads only rows where no exclusion flag is set.

## MySQL schema (ER diagram)

```mermaid
erDiagram
    food_categories {
        TINYINT id PK
        VARCHAR(50) name UK
    }
    event_records {
        INT id PK
        TINYINT food_category_id FK
        SMALLINT num_guests
        VARCHAR(30) event_type
        SMALLINT qty_prepared
        VARCHAR(20) storage_conditions
        VARCHAR(15) purchase_history
        VARCHAR(15) seasonality
        VARCHAR(20) preparation_method
        VARCHAR(15) geographical_location
        VARCHAR(10) pricing
        SMALLINT wastage_amount
        TINYINT flag_duplicate
        TINYINT flag_negative_qty
        TINYINT flag_zero_prepared
        TINYINT flag_wastage_exceeds_prepared
        TINYINT flag_outlier_guests
        TINYINT flag_outlier_qty_food
        TINYINT flag_outlier_wastage
        TINYINT flag_unknown_category
    }
    model_runs {
        INT id PK
        TIMESTAMP run_timestamp
        JSON features_json
        INT train_rows
        INT test_rows
        DECIMAL mae
        DECIMAL rmse
        DECIMAL r2
        DECIMAL wape
        JSON library_versions_json
    }
    predictions {
        INT id PK
        INT model_run_id FK
        INT event_record_id FK
        DECIMAL predicted_wastage
        TIMESTAMP created_at
    }
    recommendations {
        INT id PK
        INT event_record_id FK
        DECIMAL predicted_wastage
        SMALLINT recommended_qty
        DECIMAL service_level
        TIMESTAMP created_at
    }

    food_categories ||--o{ event_records : "categorises"
    model_runs ||--o{ predictions : "produces"
    event_records ||--o{ predictions : "receives"
    event_records ||--o{ recommendations : "receives"
```

## Loader flow

```
data/processed/clean_events.csv
    │
    ▼
read_csv()
    │
    ▼
upsert food_categories (INSERT IGNORE)
    │
    ▼
bulk upsert event_records (INSERT … ON DUPLICATE KEY UPDATE)
    │
    ▼
verify_load()   queries MySQL, compares row count + sums vs CSV
                exits non-zero on mismatch
```

The loader uses SQLAlchemy Core (not ORM) for the bulk upsert to keep the insert path fast and the SQL visible.

## EDA notebook structure

| Notebook | Contents |
|---|---|
| `01_data_overview.ipynb` | Shape, dtypes, missing values, distributions, flag summary |
| `02_waste_analysis.ipynb` | Wastage % by food type, event type, pricing, location, seasonality, guest bands, heatmap |
| `03_drivers.ipynb` | Preparation method, storage conditions, purchase history, confounding cross-tabs, effect sizes |

Each notebook queries MySQL via SQLAlchemy. Charts are produced with Matplotlib/Seaborn, saved to `outputs/` via `plt.savefig`, and displayed inline.

## Data quality report structure

`reports/data_quality_report.md` sections:
1. Dataset summary (shape, columns, dtypes)
2. Column comparison (expected vs actual)
3. Distinct values per categorical
4. Constraint check results (one subsection per check)
5. Treatments applied (one row per treatment with reason)
6. Row-count reconciliation table
