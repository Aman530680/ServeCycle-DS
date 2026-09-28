"""
Thin service layer wrapping src/recommender.py for the API.

Handles model loading and caching so the model is loaded once at startup,
not on every request.
"""

from __future__ import annotations
from functools import lru_cache
from typing import Any

from src.model import load_model
from src.recommender import recommend, what_if


@lru_cache(maxsize=1)
def get_model():
    return load_model()


def predict(
    context: dict[str, Any],
    model,
    metadata: dict,
    service_level: float = 0.90,
) -> dict:
    return recommend(context, model, metadata, service_level)


def what_if_scenario(
    context: dict[str, Any],
    reduce_pct: float,
    model,
    metadata: dict,
    service_level: float = 0.90,
) -> dict:
    return what_if(context, reduce_pct, model, metadata, service_level)
