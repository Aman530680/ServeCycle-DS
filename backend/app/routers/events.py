from __future__ import annotations
from fastapi import APIRouter
from backend.app.repositories import event_repo

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/impact")
def events_impact() -> dict:
    return event_repo.get_events_impact()
