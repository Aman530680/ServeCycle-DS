# Spec 3: analytics-api — Design

## Layer structure

```
backend/app/
├── main.py              FastAPI app factory, CORS, lifespan
├── routers/
│   ├── overview.py      GET /api/overview
│   ├── waste.py         GET /api/waste/*
│   ├── demand.py        GET /api/demand/*
│   ├── promotions.py    GET /api/promotions/impact (pricing as proxy)
│   ├── events.py        GET /api/events/impact (event type + seasonality)
│   ├── model.py         GET /api/model/*
│   ├── insights.py      GET /api/insights
│   ├── recommendations.py GET /api/recommendations, POST /api/predict-demand, POST /api/what-if
│   └── health.py        GET /health
├── services/
│   ├── waste_service.py
│   ├── model_service.py
│   └── recommendation_service.py
├── schemas/
│   ├── waste.py
│   ├── model.py
│   └── recommendation.py
├── repositories/
│   └── event_repo.py    all SQL queries; no SQL in routers or services
└── core/
    ├── config.py        Settings from .env via pydantic-settings
    └── db.py            SQLAlchemy engine + session factory
```

## Data source

All read endpoints query `data/processed/clean_events.csv` via pandas (MySQL optional
at this stage — the API works without a running DB, reading the CSV directly).
Prediction and what-if endpoints load the model from `models/`.

## Filter contract

All list and aggregate endpoints accept optional query params:
- `food_type` — one of the five food type values
- `event_type` — one of the four event type values
- `pricing` — High | Moderate | Low
- `geographical_location` — Suburban | Urban | Rural
- `page` (int, default 1) and `page_size` (int, default 50, max 200)

Filters are applied before aggregation. Empty filter = all data.

## Insights generation

`GET /api/insights` computes 5–7 statements programmatically from the processed data:
1. Top wastage food type vs overall mean (with n and difference)
2. Pricing tier effect (High vs Low wastage %, with n)
3. Preparation method with highest wastage % (with eta-squared)
4. Guest count correlation (Pearson r, direction)
5. Model vs best baseline MAE comparison
6. Highest-waste food × event combination (with n guard ≥ 10)
7. Storage conditions finding (significant or not, with p-value)

Each statement includes: the number, the computed finding, comparison basis, and
a caveat where sample is small or confounding is likely.

## Error format

All errors return:
```json
{"detail": "specific message describing what went wrong"}
```

No stack traces. HTTP 422 for validation errors (FastAPI default). HTTP 404 when
a filtered subset returns no rows. HTTP 500 with a generic message logged server-side.
