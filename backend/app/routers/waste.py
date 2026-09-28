from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from backend.app.repositories import event_repo
from backend.app.schemas.waste import WasteSummary

router = APIRouter(prefix="/api/waste", tags=["waste"])


@router.get("/summary", response_model=WasteSummary)
def waste_summary(
    food_type: str | None = Query(None),
    event_type: str | None = Query(None),
    pricing: str | None = Query(None),
    geographical_location: str | None = Query(None),
) -> WasteSummary:
    data = event_repo.get_waste_summary(food_type, event_type, pricing, geographical_location)
    if not data:
        raise HTTPException(status_code=404, detail="No records match the applied filters.")
    return WasteSummary(**data)


@router.get("/by-food-type")
def waste_by_food_type(
    event_type: str | None = Query(None),
    pricing: str | None = Query(None),
    geographical_location: str | None = Query(None),
) -> list[dict]:
    return event_repo.get_waste_by_group(
        "Type of Food", None, event_type, pricing, geographical_location
    )


@router.get("/by-event-type")
def waste_by_event_type(
    food_type: str | None = Query(None),
    pricing: str | None = Query(None),
    geographical_location: str | None = Query(None),
) -> list[dict]:
    return event_repo.get_waste_by_group(
        "Event Type", food_type, None, pricing, geographical_location
    )


@router.get("/by-pricing")
def waste_by_pricing(
    food_type: str | None = Query(None),
    event_type: str | None = Query(None),
    geographical_location: str | None = Query(None),
) -> list[dict]:
    return event_repo.get_waste_by_group(
        "Pricing", food_type, event_type, None, geographical_location
    )


@router.get("/by-location")
def waste_by_location(
    food_type: str | None = Query(None),
    event_type: str | None = Query(None),
    pricing: str | None = Query(None),
) -> list[dict]:
    return event_repo.get_waste_by_group(
        "Geographical Location", food_type, event_type, pricing, None
    )


@router.get("/by-preparation-method")
def waste_by_preparation_method(
    food_type: str | None = Query(None),
    event_type: str | None = Query(None),
    pricing: str | None = Query(None),
) -> list[dict]:
    return event_repo.get_waste_by_group(
        "Preparation Method", food_type, event_type, pricing, None
    )


@router.get("/heatmap")
def wastage_heatmap() -> list[dict]:
    return event_repo.get_wastage_heatmap()
