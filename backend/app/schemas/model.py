from __future__ import annotations
from pydantic import BaseModel


class MetricsResponse(BaseModel):
    mae: float
    rmse: float
    r2: float
    wape: float
    train_rows: int
    test_rows: int
    split_strategy: str
    plain_language: dict[str, str]


class BaselineItem(BaseModel):
    name: str
    mae: float
    rmse: float
    r2: float
    wape: float


class FeaturesResponse(BaseModel):
    features: list[str]
    target: str
    excluded: list[str]
    best_params: dict


class ActualVsPredictedPoint(BaseModel):
    actual: float
    predicted: float


class InsightItem(BaseModel):
    number: int
    statement: str
    comparison_basis: str
    caveat: str | None
