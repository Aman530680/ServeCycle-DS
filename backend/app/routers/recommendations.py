from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from backend.app.repositories import event_repo
from backend.app.schemas.recommendation import (
    PredictRequest,
    PredictResponse,
    WhatIfRequest,
    WhatIfResponse,
    WhatIfReducedScenario,
    RecommendationsResponse,
)
from backend.app.services.recommendation_service import get_model, predict, what_if_scenario

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.get("/recommendations", response_model=RecommendationsResponse)
def list_recommendations(
    food_type: str | None = Query(None),
    event_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> RecommendationsResponse:
    data = event_repo.get_recommendations(food_type, event_type, page, page_size)
    return RecommendationsResponse(**data)


@router.post("/predict-demand", response_model=PredictResponse)
def predict_demand(body: PredictRequest) -> PredictResponse:
    model, metadata = get_model()
    result = predict(body.to_context(), model, metadata, body.service_level)
    return PredictResponse(**result)


@router.post("/what-if", response_model=WhatIfResponse)
def what_if(body: WhatIfRequest) -> WhatIfResponse:
    model, metadata = get_model()
    result = what_if_scenario(
        body.context.to_context(), body.reduce_pct, model, metadata,
        body.context.service_level,
    )
    base = PredictResponse(**result["base_recommendation"])
    reduced = WhatIfReducedScenario(**result["reduced_scenario"])
    return WhatIfResponse(
        base_recommendation=base,
        reduced_scenario=reduced,
        caveat=result["caveat"],
    )
