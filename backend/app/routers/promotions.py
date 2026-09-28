from __future__ import annotations
from fastapi import APIRouter
from backend.app.repositories import event_repo

router = APIRouter(prefix="/api/promotions", tags=["promotions"])


@router.get("/impact")
def promotions_impact() -> list[dict]:
    """
    No promotion flag in source data. Uses Pricing tier as a proxy:
    High = premium/high-spend events, Low = budget events.
    The caveat is noted in the response label.
    """
    return event_repo.get_promotions_impact()
