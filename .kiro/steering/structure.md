# ServeCycle: Structure

```
ServeCycle/
├── data/
│   ├── raw/dataset.csv          (read-only in practice)
│   └── processed/               (clean_events.csv, flagged_rows.csv)
├── notebooks/                   (numbered: 01_data_overview, 02_waste_analysis, 03_drivers, 04_model_eval)
├── src/                         (importable package: pipeline, features, model, recommender)
│   ├── __init__.py
│   ├── pipeline.py              (entry point: raw -> validated -> cleaned -> processed)
│   ├── validate.py              (schema checks, type checks, constraint checks)
│   ├── clean.py                 (flagging and cleaning logic)
│   ├── features.py              (feature engineering, shared by training and API)
│   ├── model.py                 (train, evaluate, save)
│   └── recommender.py           (preparation quantity recommendation logic)
├── models/                      (random_forest.joblib, model_metadata.json)
├── reports/
│   ├── data_quality_report.md
│   ├── flagged_rows.csv
│   ├── model_report.md
│   ├── insights.md
│   └── action_plan.md
├── outputs/                     (exported chart PNGs)
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   └── core/               (config.py, db.py)
│   └── db/
│       └── schema.sql
├── frontend/
│   └── src/
│       ├── api/                 (typed client)
│       ├── components/          (StatCard, DataTable, ChartCard, FilterBar)
│       ├── pages/
│       ├── styles/              (design tokens as CSS variables)
│       └── hooks/
├── tests/
├── docs/
│   └── decisions.md
├── .env.example
├── requirements.txt
└── README.md
```

Build order: Dataset inspection, Data Engineering, MySQL, EDA, Feature Engineering, Random Forest, Evaluation, Recommendation Engine, FastAPI, React Dashboard, Testing, Documentation.

Frontend layout: src/api (typed client), src/components (StatCard, DataTable, ChartCard, FilterBar), src/pages, src/styles (design tokens as CSS variables), src/hooks.

Backend layout: app/routers, app/services, app/schemas, app/repositories, app/core (config, db).

## Frontend design

- No generic AI dashboard look: no purple-blue gradients, no glassmorphism everywhere, no oversized rounded cards with heavy shadows, no floating blobs, no neon on dark navy.
- One restrained palette as CSS variables: neutral base, one primary accent, one warning colour for waste (same on every page), one positive colour.
- One typeface family with a real fallback stack. Spacing scale and type scale defined as CSS variables.
- Tables: right-aligned numerics, tabular figures, sticky headers, sortable.
- Charts: clean axes, direct labels, formats like 12.4% and 1,240 units, no 3D, no rainbow palettes, titles state what is shown and units.
- Every data view has loading, empty and error states.
- Global filters live in the URL query string.
- Semantic HTML, labelled controls, keyboard accessible, good contrast, works down to tablet width.

## Adapted schema notes

There is no Date, Outlet_ID, Product_ID, or Quantity_Sold column in the dataset. The MySQL schema reflects what actually exists:

- `food_categories` — lookup for Type of Food
- `event_records` — one row per catering event (the core fact table)
- `model_runs` — metadata for each training run
- `predictions` — model output per event context
- `recommendations` — suggested preparation quantities

No daily_sales, outlets, or products tables. Do not create tables for data that does not exist.
