# Spec 3: analytics-api — Tasks

## T1 — Core infrastructure
backend/app/core/config.py (Settings), core/db.py (engine + session),
main.py (app factory, CORS, lifespan loading model), health router.
Traces to: design layer structure, filter contract.

## T2 — Repository layer
backend/app/repositories/event_repo.py — all data access functions reading
from clean_events.csv. No SQL in routers. Applies filters.
Traces to: design data source, filter contract.

## T3 — Schemas
Pydantic response models for all endpoints. No bare dicts returned.
Traces to: design layer structure.

## T4 — Read endpoints (waste + overview)
GET /api/overview, /api/waste/summary, /api/waste/by-food-type,
/api/waste/by-event-type, /api/waste/by-pricing, /api/waste/by-location,
/api/waste/trends (aggregated by seasonality + guest band).
Traces to: requirements read endpoints.

--- REVIEW: read endpoints ---

## T5 — Read endpoints (model + insights)
GET /api/model/metrics, /api/model/features, /api/model/actual-vs-predicted,
/api/insights (programmatic, 5-7 statements).
Traces to: requirements model + insights endpoints.

## T6 — Prediction and recommendation endpoints
POST /api/predict-demand, POST /api/what-if, GET /api/recommendations.
Reuses src/features.py feature building path.
Traces to: requirements prediction endpoints.

--- REVIEW: predict, what-if and insights ---

## T7 — Endpoint tests
tests/test_api.py — TestClient tests for all read endpoints, predict-demand,
what-if, insights, health. Verify response shape and status codes.
Traces to: requirements endpoint tests.
