"""
Tests for src/recommender.py — buffer logic, rounding, monotonicity, what-if.
"""

import math
from unittest.mock import MagicMock

import numpy as np
import pytest

from src.recommender import recommend, what_if


def _context() -> dict:
    return {
        "Type of Food": "Meat",
        "Number of Guests": 300,
        "Event Type": "Corporate",
        "Quantity of Food": 400,
        "Storage Conditions": "Refrigerated",
        "Purchase History": "Regular",
        "Seasonality": "Winter",
        "Preparation Method": "Buffet",
        "Geographical Location": "Urban",
        "Pricing": "High",
    }


def _mock_model(predicted: float = 25.0) -> MagicMock:
    model = MagicMock()
    model.predict.return_value = np.array([predicted])
    return model


def _metadata(val_residuals: list[float] | None = None) -> dict:
    residuals = val_residuals if val_residuals is not None else list(range(1, 21))
    return {"val_residuals": residuals}


class TestRecommend:
    def test_returns_integer_recommended_qty(self):
        result = recommend(_context(), _mock_model(), _metadata())
        assert isinstance(result["recommended_qty"], int)

    def test_recommended_qty_is_positive(self):
        result = recommend(_context(), _mock_model(), _metadata())
        assert result["recommended_qty"] >= 0

    def test_recommended_qty_is_ceil(self):
        # With known residuals [1..20] and service_level=0.90,
        # the 90th percentile of [1..20] is 18.1.
        # base_qty comes from per_guest_rate * num_guests.
        # recommended = ceil(base_qty + buffer) which should be an integer.
        result = recommend(_context(), _mock_model(), _metadata())
        qty = result["recommended_qty"]
        assert qty == math.ceil(result["base_qty"] + result["buffer_units"])

    def test_higher_service_level_never_lowers_recommendation(self):
        model = _mock_model(25.0)
        meta = _metadata(list(range(1, 51)))
        ctx = _context()
        result_90 = recommend(ctx, model, meta, service_level=0.90)
        result_95 = recommend(ctx, model, meta, service_level=0.95)
        assert result_95["recommended_qty"] >= result_90["recommended_qty"]

    def test_floor_at_zero(self):
        # If model predicts negative wastage (clipped to 0) and per_guest_rate
        # is near zero, result should be >= 0.
        model = _mock_model(-100.0)
        meta = _metadata([0.0] * 20)
        ctx = _context()
        ctx["Number of Guests"] = 1
        result = recommend(ctx, model, meta, service_level=0.50)
        assert result["recommended_qty"] >= 0

    def test_invalid_service_level_raises(self):
        with pytest.raises(ValueError, match="service_level"):
            recommend(_context(), _mock_model(), _metadata(), service_level=0.0)
        with pytest.raises(ValueError, match="service_level"):
            recommend(_context(), _mock_model(), _metadata(), service_level=1.5)

    def test_assumptions_list_present(self):
        result = recommend(_context(), _mock_model(), _metadata())
        assert isinstance(result["assumptions"], list)
        assert len(result["assumptions"]) > 0

    def test_no_val_residuals_gives_zero_buffer(self):
        meta = _metadata([])
        result = recommend(_context(), _mock_model(), meta)
        assert result["buffer_units"] == 0.0

    def test_estimated_wastage_pct_non_negative(self):
        result = recommend(_context(), _mock_model(), _metadata())
        if result["estimated_wastage_pct"] is not None:
            assert result["estimated_wastage_pct"] >= 0.0


class TestWhatIf:
    def test_reduced_qty_less_than_base(self):
        model = _mock_model(25.0)
        meta = _metadata()
        ctx = _context()
        result = what_if(ctx, 10.0, model, meta)
        assert result["reduced_scenario"]["reduced_qty"] <= result["base_recommendation"]["recommended_qty"]

    def test_higher_reduction_pct_gives_lower_qty(self):
        model = _mock_model(25.0)
        meta = _metadata()
        ctx = _context()
        r10 = what_if(ctx, 10.0, model, meta)
        r30 = what_if(ctx, 30.0, model, meta)
        assert r30["reduced_scenario"]["reduced_qty"] <= r10["reduced_scenario"]["reduced_qty"]

    def test_caveat_present(self):
        model = _mock_model(25.0)
        meta = _metadata()
        result = what_if(_context(), 20.0, model, meta)
        assert "caveat" in result
        assert len(result["caveat"]) > 20

    def test_invalid_reduce_pct_raises(self):
        model = _mock_model()
        meta = _metadata()
        with pytest.raises(ValueError, match="reduce_pct"):
            what_if(_context(), 0.0, model, meta)
        with pytest.raises(ValueError, match="reduce_pct"):
            what_if(_context(), 100.0, model, meta)

    def test_reduced_qty_floored_at_zero(self):
        model = _mock_model(1.0)
        meta = _metadata([0.0] * 20)
        ctx = _context()
        ctx["Number of Guests"] = 1
        result = what_if(ctx, 99.9, model, meta)
        assert result["reduced_scenario"]["reduced_qty"] >= 0
