from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class WasteGroupItem(BaseModel):
    n: int
    mean_wastage_pct: float
    median_wastage_pct: float
    std: float
    high_waste_share_pct: float


class WasteSummary(BaseModel):
    n: int
    mean_wastage_pct: float
    median_wastage_pct: float
    std_wastage_pct: float
    min_wastage_pct: float
    max_wastage_pct: float
    total_units_prepared: int
    total_units_wasted: int
    high_waste_event_count: int


class OverviewResponse(BaseModel):
    total_events: int
    total_qty_prepared: int
    total_wastage_units: int
    overall_wastage_pct: float
    median_wastage_pct: float
    unique_food_types: int
    unique_event_types: int


class HeatmapItem(BaseModel):
    food_type: str
    event_type: str
    n: int
    mean_wastage_pct: float
