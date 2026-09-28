"""
All data access for the API.

Reads from data/processed/clean_events.csv. No SQL in routers or services.
Exclusion-flagged rows are filtered out before any aggregate is computed.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from backend.app.core.config import settings
from src.utils import compute_wastage_pct

EXCLUSION_FLAGS = [
    "flag_duplicate", "flag_negative_qty",
    "flag_zero_prepared", "flag_wastage_exceeds_prepared",
]

HIGH_WASTE_THRESHOLD = 10.0


@lru_cache(maxsize=1)
def _load_df() -> pd.DataFrame:
    """
    Loads and caches the processed dataset.

    The cache is intentional: the CSV does not change during a server run.
    Call _load_df.cache_clear() in tests to reset.
    """
    path = Path(settings.clean_csv_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at '{path}'. "
            "Run python -m src.pipeline first."
        )
    df = pd.read_csv(path)
    present_excl = [c for c in EXCLUSION_FLAGS if c in df.columns]
    if present_excl:
        df = df[~df[present_excl].any(axis=1)].copy()
    df["wastage_pct"] = compute_wastage_pct(df)
    df = df[df["wastage_pct"].notna()].copy()
    return df


def _apply_filters(
    df: pd.DataFrame,
    food_type: str | None,
    event_type: str | None,
    pricing: str | None,
    geographical_location: str | None,
) -> pd.DataFrame:
    if food_type:
        df = df[df["Type of Food"] == food_type]
    if event_type:
        df = df[df["Event Type"] == event_type]
    if pricing:
        df = df[df["Pricing"] == pricing]
    if geographical_location:
        df = df[df["Geographical Location"] == geographical_location]
    return df


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

def get_overview(
    food_type: str | None = None,
    event_type: str | None = None,
    pricing: str | None = None,
    geographical_location: str | None = None,
) -> dict:
    df = _apply_filters(_load_df(), food_type, event_type, pricing, geographical_location)
    if df.empty:
        return {}
    return {
        "total_events": int(len(df)),
        "total_qty_prepared": int(df["Quantity of Food"].sum()),
        "total_wastage_units": int(df["Wastage Food Amount"].sum()),
        "overall_wastage_pct": round(float(df["wastage_pct"].mean()), 2),
        "median_wastage_pct": round(float(df["wastage_pct"].median()), 2),
        "unique_food_types": int(df["Type of Food"].nunique()),
        "unique_event_types": int(df["Event Type"].nunique()),
    }


# ---------------------------------------------------------------------------
# Waste summaries
# ---------------------------------------------------------------------------

def get_waste_by_group(
    group_col: str,
    food_type: str | None = None,
    event_type: str | None = None,
    pricing: str | None = None,
    geographical_location: str | None = None,
) -> list[dict]:
    df = _apply_filters(_load_df(), food_type, event_type, pricing, geographical_location)
    if df.empty:
        return []
    grp = (
        df.groupby(group_col)["wastage_pct"]
        .agg(n="count", mean_wastage_pct="mean", median_wastage_pct="median", std="std")
        .reset_index()
    )
    grp["high_waste_share_pct"] = (
        df[df["wastage_pct"] > HIGH_WASTE_THRESHOLD]
        .groupby(group_col).size()
        .reindex(grp[group_col], fill_value=0)
        .values
        / grp["n"] * 100
    )
    grp = grp.sort_values("mean_wastage_pct", ascending=False)
    return grp.round(2).to_dict(orient="records")


def get_waste_summary(
    food_type: str | None = None,
    event_type: str | None = None,
    pricing: str | None = None,
    geographical_location: str | None = None,
) -> dict:
    df = _apply_filters(_load_df(), food_type, event_type, pricing, geographical_location)
    if df.empty:
        return {}
    pct = df["wastage_pct"]
    return {
        "n": int(len(df)),
        "mean_wastage_pct": round(float(pct.mean()), 2),
        "median_wastage_pct": round(float(pct.median()), 2),
        "std_wastage_pct": round(float(pct.std()), 2),
        "min_wastage_pct": round(float(pct.min()), 2),
        "max_wastage_pct": round(float(pct.max()), 2),
        "total_units_prepared": int(df["Quantity of Food"].sum()),
        "total_units_wasted": int(df["Wastage Food Amount"].sum()),
        "high_waste_event_count": int((pct > HIGH_WASTE_THRESHOLD).sum()),
    }


def get_wastage_heatmap() -> list[dict]:
    df = _load_df()
    MIN_OBS = 10
    heatmap = (
        df.groupby(["Type of Food", "Event Type"])["wastage_pct"]
        .agg(n="count", mean_wastage_pct="mean")
        .reset_index()
    )
    heatmap = heatmap[heatmap["n"] >= MIN_OBS].round(2)
    return heatmap.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Demand / guest analysis
# ---------------------------------------------------------------------------

def get_demand_by_weekday() -> list[dict]:
    """
    There is no weekday column. Returns guest-band breakdown as a proxy
    for volume segmentation. Clearly labelled in the response.
    """
    df = _load_df()
    df["guest_band"] = pd.qcut(
        df["Number of Guests"], q=4,
        labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]
    )
    grp = (
        df.groupby("guest_band", observed=True)
        .agg(
            n=("wastage_pct", "count"),
            mean_wastage_pct=("wastage_pct", "mean"),
            mean_guests=("Number of Guests", "mean"),
            mean_qty_prepared=("Quantity of Food", "mean"),
        )
        .reset_index()
    )
    return grp.round(2).to_dict(orient="records")


def get_demand_by_weather() -> list[dict]:
    """
    There is no weather column. Returns by seasonality as the closest proxy.
    """
    df = _load_df()
    grp = (
        df.groupby("Seasonality")
        .agg(
            n=("wastage_pct", "count"),
            mean_wastage_pct=("wastage_pct", "mean"),
            mean_qty_prepared=("Quantity of Food", "mean"),
        )
        .reset_index()
    )
    return grp.round(2).to_dict(orient="records")


def get_demand_trends() -> list[dict]:
    """
    Returns preparation and wastage breakdown by preparation method and event type.
    No date column — time trends are not available.
    """
    df = _load_df()
    grp = (
        df.groupby(["Preparation Method", "Event Type"])
        .agg(
            n=("wastage_pct", "count"),
            mean_wastage_pct=("wastage_pct", "mean"),
            mean_qty_prepared=("Quantity of Food", "mean"),
            mean_guests=("Number of Guests", "mean"),
        )
        .reset_index()
    )
    return grp.round(2).to_dict(orient="records")


# ---------------------------------------------------------------------------
# Promotions and events
# ---------------------------------------------------------------------------

def get_promotions_impact() -> list[dict]:
    """
    Uses Pricing as the promotion proxy (High = premium events, Low = budget).
    """
    return get_waste_by_group("Pricing")


def get_events_impact() -> list[dict]:
    """
    Event Type as the special-event proxy. Seasonality breakdown also included.
    """
    df = _load_df()
    event_grp = (
        df.groupby("Event Type")["wastage_pct"]
        .agg(n="count", mean_wastage_pct="mean", std="std")
        .reset_index()
    )
    season_grp = (
        df.groupby("Seasonality")["wastage_pct"]
        .agg(n="count", mean_wastage_pct="mean", std="std")
        .reset_index()
    )
    return {
        "by_event_type": event_grp.round(2).to_dict(orient="records"),
        "by_seasonality": season_grp.round(2).to_dict(orient="records"),
    }


# ---------------------------------------------------------------------------
# Recommendations (stored results)
# ---------------------------------------------------------------------------

def get_recommendations(
    food_type: str | None = None,
    event_type: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    df = _load_df()
    if food_type:
        df = df[df["Type of Food"] == food_type]
    if event_type:
        df = df[df["Event Type"] == event_type]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]

    records = page_df[[
        "Type of Food", "Event Type", "Number of Guests",
        "Quantity of Food", "Wastage Food Amount", "wastage_pct",
        "Preparation Method", "Geographical Location", "Pricing",
    ]].round(2).to_dict(orient="records")

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": records,
    }
