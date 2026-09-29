# ServeCycle

Food waste analysis and preparation planning for catering operations.

Academic submission: DS_Day01_18 — "Restaurant: What is causing food wastage?"

---

## What it is

ServeCycle analyses 1,782 historical catering event records to answer one question: which combinations of food type, event context, preparation method, storage conditions, location, and pricing drive the highest wastage, and how many units should be prepared for a given event to keep waste low without running short?

It covers data cleaning, exploratory analysis, a Random Forest regression model, a preparation recommendation engine, a FastAPI backend, and a React dashboard.

## Dataset reality

The source dataset does not contain Date, Outlet_ID, Product_ID, Quantity_Sold, Weather, Weekday, Holiday, or Promotion columns. The original spec assumed a restaurant outlet/product schema; the actual data is event-level catering records. All analysis is adapted to what the data actually contains. No columns were invented.

This means:

- There is no time dimension. Time-series analysis, lag features, and rolling windows are not applicable.
- There is no sold quantity. Stockout rates cannot be measured. Recommendations are based on predicted wastage and historical per-guest preparation rates.
- "Outlets" are three geographic categories (Suburban, Urban, Rural), not individual restaurant identifiers.

These limitations are stated wherever they are relevant throughout the codebase and reports.

---

## Quick start

### 1. Prerequisites

- Python 3.12+
- Node 18+ and npm
- MySQL 8+ (optional — the API and pipeline work without it; MySQL is used for the loader and verification script)
- Git

### 2. Clone and install Python dependencies

```bash
git clone https://github.com/Aman530680/ServeCycle-DS.git
cd ServeCycle
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
```

### 4. Run the data pipeline

```bash
python -m src.pipeline
```

Produces:
- `data/processed/clean_events.csv` — cleaned data with flag columns
- `reports/data_quality_report.md` — full quality report
- `reports/flagged_rows.csv` — rows with at least one issue flag

### 5. Load MySQL (optional)

```bash
# Apply the schema first:
mysql -u root -p servecycle < backend/db/schema.sql

# Load the processed CSV:
python -m src.loader

# Verify the load:
python -m src.verify_load
```

### 6. Train the model

```bash
python -m src.model
```

Produces:
- `models/random_forest.joblib`
- `models/model_metadata.json`
- `outputs/actual_vs_predicted.png`
- `reports/model_report.md`

### 7. Run the EDA notebooks

Open any of the following in VS Code (rendered as interactive notebooks via `# %%` cell markers) or convert to `.ipynb` with `jupytext`:

```
notebooks/01_data_overview.py
notebooks/02_waste_analysis.py
notebooks/03_drivers.py
notebooks/04_model_eval.py
```

Required chart outputs (saved to `outputs/` automatically when notebooks are run):
- `outputs/waste_by_food_type.png`
- `outputs/waste_by_event_type.png`
- `outputs/waste_by_pricing.png`
- `outputs/wastage_heatmap.png`
- `outputs/actual_vs_predicted.png`

### 8. Run the backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### 9. Run the frontend

```bash
cd frontend
cp .env.example .env   # set VITE_API_URL=http://localhost:8000
npm install
npm run dev
```

Dashboard at `http://localhost:5173`

---

## Project structure

```
ServeCycle/
├── data/
│   ├── raw/dataset.csv          read-only source file
│   └── processed/               pipeline outputs
├── notebooks/                   01–04 analysis notebooks
├── src/                         importable Python package
│   ├── pipeline.py              CLI entry point
│   ├── validate.py              schema and constraint checks
│   ├── clean.py                 flagging and exclusion logic
│   ├── features.py              feature engineering (training + API)
│   ├── model.py                 Random Forest training and evaluation
│   ├── recommender.py           preparation quantity recommendation
│   ├── loader.py                CSV → MySQL loader
│   ├── verify_load.py           post-load verification
│   └── utils.py                 shared constants and wastage % formula
├── models/                      trained model and metadata
├── reports/                     quality report, model report, insights, action plan
├── outputs/                     chart PNGs
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI app
│   │   ├── routers/             one file per endpoint group
│   │   ├── services/            business logic
│   │   ├── schemas/             Pydantic response models
│   │   ├── repositories/        all data access
│   │   └── core/                config and db
│   └── db/schema.sql            MySQL schema (idempotent)
├── frontend/
│   └── src/
│       ├── api/                 typed fetch client and endpoint functions
│       ├── components/          StatCard, DataTable, ChartCard, FilterBar, etc.
│       ├── hooks/               useApi, useFilters
│       ├── pages/               6 pages
│       └── styles/              CSS design tokens
├── tests/                       Pytest and Vitest tests
├── docs/decisions.md            architecture decision log
├── .env.example
├── requirements.txt
└── README.md
```

---

## Running tests

### Backend (Python)

```bash
pytest tests/ -v
```

Covers: schema validation, constraint checks, flag assignment, exclusion logic, wastage % formula, feature leakage guard, recommender buffer logic, all API endpoints.

### Frontend (TypeScript)

```bash
cd frontend
npm run test
```

Covers: StatCard, LoadingSpinner, EmptyState, ErrorState, ChartCard (loading/empty/error states), FilterBar, DataTable, InsightCard.

---

## Key findings

Full findings are in `reports/insights.md`. Summary:

1. **Pricing drives the largest wastage gap.** High-pricing events waste 8.8% of prepared food on average versus 5.5% for low-pricing events — a 3.3 percentage point gap across 1,618 clean event records.

2. **Preparation method has a medium effect.** Sit-down dinner service produces 7.5% mean wastage against 6.1% for finger food (eta-squared = 0.109). This is the strongest controllable factor.

3. **Larger events waste proportionally more.** Pearson r = 0.374 between guest count and wastage %. Events in the top guest-count quartile (350+ guests) waste 7.9% on average versus 6.0% for the lowest quartile.

4. **Storage conditions show no significant difference** in wastage rate after accounting for food type (p = 0.797). The apparent refrigeration effect is a food-type composition effect.

5. **The Random Forest outperforms all baselines.** Test-set MAE = 2.28 units versus best baseline MAE = 8.76 units. R² = 0.893 on the test set.

6. **No single food type dominates wastage rate.** Fruits lead at 7.0% mean wastage but the range across food types is only 0.24 percentage points — small in absolute terms.

7. **Weddings show the highest mean wastage** (7.0%) and are concentrated in sit-down dinner service, which is the highest-waste preparation method. The two factors are confounded.

---

## Limitations

- **No time dimension.** The dataset has no Date column. Seasonal trends, week-over-week comparisons, and time-based train/test splits are not possible. The train/test split is stratified random, which is stated throughout.
- **No sold quantity.** Demand cannot be observed. Stockout rates are unmeasurable. Recommendations are estimates based on predicted wastage and historical per-guest preparation rates, not actual demand forecasts.
- **Censored wastage.** Events where all food was consumed show zero wastage, which may mean either perfect preparation or that the event ran out of food. These cases cannot be distinguished.
- **Weather as forecast proxy.** There is no weather column in this dataset. Seasonality (Winter/Summer/All Seasons) is used as the closest proxy. It is not equivalent to same-day weather data.
- **Simulation figures are estimates.** Recommended preparation quantities and projected waste savings are based on historical patterns, not controlled experiments. Do not present them as measured outcomes.
- **Results are specific to this dataset.** The model was trained on 1,618 event records from one data source. Generalisation to events with different guest profiles, menu types, or operating contexts is not demonstrated.
