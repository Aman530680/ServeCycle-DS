# Data Quality Report

## 1. Dataset summary

- Source: `data\raw\dataset.csv`
- Rows: 1782
- Columns: 11

### Column names and dtypes

| Column | Dtype |
|---|---|
| Type of Food | str |
| Number of Guests | int64 |
| Event Type | str |
| Quantity of Food | int64 |
| Storage Conditions | str |
| Purchase History | str |
| Seasonality | str |
| Preparation Method | str |
| Geographical Location | str |
| Pricing | str |
| Wastage Food Amount | int64 |

### Numeric column summary

| Column | Min | Max | Mean | Std |
|---|---|---|---|---|
| Number of Guests | 207.0 | 491.0 | 317.80 | 67.83 |
| Quantity of Food | 280.0 | 500.0 | 411.13 | 65.20 |
| Wastage Food Amount | 10.0 | 63.0 | 28.54 | 10.46 |

## 2. Column comparison (expected vs actual)

All expected columns are present.

## 3. Distinct values per categorical column

**Type of Food** (5 distinct): ['Baked Goods', 'Dairy Products', 'Fruits', 'Meat', 'Vegetables']

**Event Type** (4 distinct): ['Birthday', 'Corporate', 'Social Gathering', 'Wedding']

**Storage Conditions** (2 distinct): ['Refrigerated', 'Room Temperature']

**Purchase History** (2 distinct): ['Occasional', 'Regular']

**Seasonality** (3 distinct): ['All Seasons', 'Summer', 'Winter']

**Preparation Method** (3 distinct): ['Buffet', 'Finger Food', 'Sit-down Dinner']

**Geographical Location** (3 distinct): ['Rural', 'Suburban', 'Urban']

**Pricing** (3 distinct): ['High', 'Low', 'Moderate']

## 4. Constraint check results

### duplicate_rows
- Rows affected: 164
- Detail: Fully duplicate rows (all 11 columns identical).
- Treatment: Keep first occurrence. Exclude subsequent duplicates from analysis. Retain in flagged_rows.csv.

### flag_outlier_guests
- Rows affected: 35
- Detail: 'Number of Guests' outliers by IQR method (bounds: [142.5, 474.5]).
- Treatment: Flag; retain by default. EDA notebook reports whether they skew results.

### flag_outlier_wastage
- Rows affected: 10
- Detail: 'Wastage Food Amount' outliers by IQR method (bounds: [-2.5, 57.5]).
- Treatment: Flag; retain by default. EDA notebook reports whether they skew results.

## 5. Row-count reconciliation

| Metric | Count |
|---|---|
| Raw rows in | 1782 |
| Rows with any flag | 196 |
| flag_missing | 0 |
| flag_duplicate | 164 |
| flag_negative_qty | 0 |
| flag_zero_prepared | 0 |
| flag_wastage_exceeds_prepared | 0 |
| flag_outlier_guests | 35 |
| flag_outlier_qty_food | 0 |
| flag_outlier_wastage | 10 |
| flag_unknown_category | 0 |
| Rows excluded from training | 164 |
| Rows available for training | 1618 |
