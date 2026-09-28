"""
FastAPI endpoint tests using TestClient.

These tests run against the real processed dataset and trained model,
so they require the pipeline and model to have been run first.
"""

from __future__ import annotations
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.repositories.event_repo import _load_df

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    # Reset the lru_cache before each test so filter state doesn't bleed
    _load_df.cache_clear()
    yield
    _load_df.cache_clear()


class TestHealth:
    def test_health_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestOverview:
    def test_overview_returns_200(self):
        r = client.get("/api/overview")
        assert r.status_code == 200

    def test_overview_has_required_fields(self):
        r = client.get("/api/overview")
        data = r.json()
        assert "total_events" in data
        assert "overall_wastage_pct" in data
        assert "total_qty_prepared" in data

    def test_overview_total_events_positive(self):
        r = client.get("/api/overview")
        assert r.json()["total_events"] > 0

    def test_overview_filter_by_food_type(self):
        r = client.get("/api/overview?food_type=Meat")
        assert r.status_code == 200
        assert r.json()["total_events"] > 0

    def test_overview_invalid_filter_returns_404(self):
        r = client.get("/api/overview?food_type=Nonexistent")
        assert r.status_code == 404


class TestWaste:
    def test_waste_summary_200(self):
        r = client.get("/api/waste/summary")
        assert r.status_code == 200

    def test_waste_summary_has_n(self):
        r = client.get("/api/waste/summary")
        assert "n" in r.json()

    def test_waste_by_food_type_is_list(self):
        r = client.get("/api/waste/by-food-type")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_waste_by_food_type_has_entries(self):
        r = client.get("/api/waste/by-food-type")
        assert len(r.json()) > 0

    def test_waste_by_event_type_is_list(self):
        r = client.get("/api/waste/by-event-type")
        assert isinstance(r.json(), list)

    def test_waste_by_pricing_is_list(self):
        r = client.get("/api/waste/by-pricing")
        assert isinstance(r.json(), list)

    def test_waste_heatmap_returns_list(self):
        r = client.get("/api/waste/heatmap")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestDemand:
    def test_demand_trends_200(self):
        r = client.get("/api/demand/trends")
        assert r.status_code == 200

    def test_demand_by_weather_200(self):
        r = client.get("/api/demand/by-weather")
        assert r.status_code == 200

    def test_demand_by_weekday_200(self):
        r = client.get("/api/demand/by-weekday")
        assert r.status_code == 200


class TestPromotionsEvents:
    def test_promotions_impact_200(self):
        r = client.get("/api/promotions/impact")
        assert r.status_code == 200

    def test_events_impact_200(self):
        r = client.get("/api/events/impact")
        assert r.status_code == 200

    def test_events_impact_has_both_keys(self):
        r = client.get("/api/events/impact")
        data = r.json()
        assert "by_event_type" in data
        assert "by_seasonality" in data


class TestModel:
    def test_model_metrics_200(self):
        r = client.get("/api/model/metrics")
        assert r.status_code == 200

    def test_model_metrics_has_mae(self):
        r = client.get("/api/model/metrics")
        assert "mae" in r.json()

    def test_model_features_200(self):
        r = client.get("/api/model/features")
        assert r.status_code == 200

    def test_model_features_has_features_list(self):
        r = client.get("/api/model/features")
        data = r.json()
        assert "features" in data
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0

    def test_model_importance_200(self):
        r = client.get("/api/model/importance")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestInsights:
    def test_insights_returns_list(self):
        r = client.get("/api/insights")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_insights_has_5_to_7_items(self):
        r = client.get("/api/insights")
        items = r.json()
        assert 5 <= len(items) <= 7

    def test_insights_each_has_required_fields(self):
        r = client.get("/api/insights")
        for item in r.json():
            assert "number" in item
            assert "statement" in item
            assert "comparison_basis" in item


class TestPrediction:
    _valid_body = {
        "Type of Food": "Meat",
        "Number of Guests": 300,
        "Event Type": "Corporate",
        "Storage Conditions": "Refrigerated",
        "Purchase History": "Regular",
        "Seasonality": "Winter",
        "Preparation Method": "Buffet",
        "Geographical Location": "Urban",
        "Pricing": "High",
        "service_level": 0.90,
    }

    def test_predict_demand_returns_200(self):
        r = client.post("/api/predict-demand", json=self._valid_body)
        assert r.status_code == 200

    def test_predict_demand_has_recommended_qty(self):
        r = client.post("/api/predict-demand", json=self._valid_body)
        data = r.json()
        assert "recommended_qty" in data
        assert isinstance(data["recommended_qty"], int)
        assert data["recommended_qty"] >= 0

    def test_predict_demand_has_assumptions(self):
        r = client.post("/api/predict-demand", json=self._valid_body)
        assert len(r.json()["assumptions"]) > 0

    def test_predict_demand_invalid_service_level(self):
        body = dict(self._valid_body)
        body["service_level"] = 1.5
        r = client.post("/api/predict-demand", json=body)
        assert r.status_code == 422

    def test_what_if_returns_200(self):
        r = client.post("/api/what-if", json={
            "context": self._valid_body,
            "reduce_pct": 20.0,
        })
        assert r.status_code == 200

    def test_what_if_has_caveat(self):
        r = client.post("/api/what-if", json={
            "context": self._valid_body,
            "reduce_pct": 20.0,
        })
        assert "caveat" in r.json()

    def test_recommendations_list_200(self):
        r = client.get("/api/recommendations")
        assert r.status_code == 200

    def test_recommendations_has_pagination(self):
        r = client.get("/api/recommendations")
        data = r.json()
        assert "total" in data
        assert "page" in data
        assert "results" in data
