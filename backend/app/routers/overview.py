from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from backend.app.repositories import event_repo
from backend.app.schemas.waste import OverviewResponse

router = APIRouter(prefix="/api", tags=["overview"])


@router.get("/overview", response_model=OverviewResponse)
def get_overview(
    food_type: str | None = Query(None),
    event_type: str | None = Query(None),
    pricing: str | None = Query(None),
    geographical_location: str | None = Query(None),
) -> OverviewResponse:
    data = event_repo.get_overview(food_type, event_type, pricing, geographical_location)
    if not data:
        raise HTTPException(status_code=404, detail="No records match the applied filters.")
    return OverviewResponse(**data)
