from __future__ import annotations
from fastapi import APIRouter
from backend.app.repositories import event_repo

router = APIRouter(prefix="/api/demand", tags=["demand"])


@router.get("/trends")
def demand_trends() -> list[dict]:
    return event_repo.get_demand_trends()


@router.get("/by-weather")
def demand_by_weather() -> list[dict]:
    """
    No weather column in source data. Returns by seasonality as the closest proxy.
    The response field is named 'Seasonality' and the caveat is in the API docs.
    """
    return event_repo.get_demand_by_weather()


@router.get("/by-weekday")
def demand_by_weekday() -> list[dict]:
    """
    No date or weekday column in source data. Returns by guest-count band
    as a volume segmentation proxy. Caveat is noted in the response label.
    """
    return event_repo.get_demand_by_weekday()
