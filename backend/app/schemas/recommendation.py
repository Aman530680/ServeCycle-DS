from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field, field_validator


class PredictRequest(BaseModel):
    food_type: str = Field(..., alias="Type of Food")
    num_guests: int = Field(..., alias="Number of Guests", ge=1)
    event_type: str = Field(..., alias="Event Type")
    storage_conditions: str = Field(..., alias="Storage Conditions")
    purchase_history: str = Field(..., alias="Purchase History")
    seasonality: str = Field(..., alias="Seasonality")
    preparation_method: str = Field(..., alias="Preparation Method")
    geographical_location: str = Field(..., alias="Geographical Location")
    pricing: str = Field(..., alias="Pricing")
    service_level: float = Field(default=0.90, ge=0.01, le=1.0)

    model_config = {"populate_by_name": True}

    def to_context(self) -> dict[str, Any]:
        return {
            "Type of Food": self.food_type,
            "Number of Guests": self.num_guests,
            "Event Type": self.event_type,
            "Storage Conditions": self.storage_conditions,
            "Purchase History": self.purchase_history,
            "Seasonality": self.seasonality,
            "Preparation Method": self.preparation_method,
            "Geographical Location": self.geographical_location,
            "Pricing": self.pricing,
        }


class PredictResponse(BaseModel):
    recommended_qty: int
    predicted_wastage_units: float
    base_qty: float
    buffer_units: float
    service_level: float
    estimated_wastage_pct: float | None
    per_guest_rate: float
    assumptions: list[str]


class WhatIfRequest(BaseModel):
    context: PredictRequest
    reduce_pct: float = Field(..., gt=0, lt=100)


class WhatIfReducedScenario(BaseModel):
    reduce_pct: float
    reduced_qty: int
    est_waste_units: float
    est_waste_pct: float | None
    est_unmet_units: float
    est_waste_units_saved_vs_base: float


class WhatIfResponse(BaseModel):
    base_recommendation: PredictResponse
    reduced_scenario: WhatIfReducedScenario
    caveat: str


class RecommendationsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[dict[str, Any]]
