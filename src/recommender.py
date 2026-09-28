"""
Recommendation engine for preparation quantity planning.

Given an event context (food type, preparation method, number of guests, etc.),
this module estimates expected wastage and recommends how many units to prepare.

The recommendation is an estimate based on historical patterns, not a guarantee.
It cannot account for actual demand because the dataset contains no sold-quantity
column. All outputs should be labelled as estimates.

Formula:
    base_qty          = num_guests × per_guest_rate(food_type, preparation_method)
    predicted_wastage = model.predict(context_features)
    buffer            = quantile(val_residuals, service_level)
    recommended_qty   = ceil(base_qty + buffer)
    recommended_qty   = max(0, recommended_qty)

per_guest_rate is the median of (Quantity of Food / Number of Guests) computed
per (Type of Food, Preparation Method) group in the training data, with a minimum
of 10 observations per group. Falls back to the global median if a group is small.

val_residuals come from a validation fold separate from the reported test set.
They represent how much the model's prediction can be off in practice and drive
the safety buffer at a chosen service level.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from src.features import build_features_for_prediction, ALL_FEATURE_COLS, TARGET_COL

CLEAN_CSV = Path("data/processed/clean_events.csv")
MIN_GROUP_OBS = 10
EXCLUSION_FLAGS = [
    "flag_duplicate", "flag_negative_qty",
    "flag_zero_prepared", "flag_wastage_exceeds_prepared",
]


def _load_training_data() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_CSV)
    present_excl = [c for c in EXCLUSION_FLAGS if c in df.columns]
    if present_excl:
        df = df[~df[present_excl].any(axis=1)].copy()
    return df


def compute_per_guest_rates(df: pd.DataFrame) -> dict[tuple[str, str], float]:
    """
    Computes median units-per-guest for each (food_type, preparation_method) group.

    Groups with fewer than MIN_GROUP_OBS observations fall back to the global median.
    This rate represents how many food units are typically prepared per guest in
    historical data — it is not a normative target.
    """
    df = df.copy()
    df["per_guest"] = df["Quantity of Food"] / df["Number of Guests"]
    global_median = float(df["per_guest"].median())

    rates: dict[tuple[str, str], float] = {}
    for (food_type, prep_method), grp in df.groupby(["Type of Food", "Preparation Method"]):
        if len(grp) >= MIN_GROUP_OBS:
            rates[(food_type, prep_method)] = float(grp["per_guest"].median())
        else:
            rates[(food_type, prep_method)] = global_median

    return rates


def recommend(
    context: dict[str, Any],
    model: RandomForestRegressor,
    metadata: dict,
    service_level: float = 0.90,
) -> dict[str, Any]:
    """
    Returns a preparation quantity recommendation for one event context.

    Parameters
    ----------
    context:
        Dict with keys matching dataset column names. Must include at least:
        Type of Food, Event Type, Number of Guests, Storage Conditions,
        Purchase History, Seasonality, Preparation Method,
        Geographical Location, Pricing.
    model:
        Fitted RandomForestRegressor from src/model.py.
    metadata:
        Model metadata dict containing val_residuals.
    service_level:
        Quantile of validation residuals added as a safety buffer.
        0.90 means the recommendation covers 90% of historical residual errors.

    Returns
    -------
    dict with:
        recommended_qty          int
        predicted_wastage_units  float
        base_qty                 float
        buffer_units             float
        service_level            float
        estimated_wastage_pct    float | None
        per_guest_rate           float
        assumptions              list[str]
    """
    if not (0.0 < service_level <= 1.0):
        raise ValueError(
            f"service_level must be in (0, 1], got {service_level}."
        )

    X = build_features_for_prediction(context)
    predicted_wastage = float(model.predict(X)[0])
    predicted_wastage = max(0.0, predicted_wastage)

    num_guests = int(context["Number of Guests"])
    food_type = context["Type of Food"]
    prep_method = context["Preparation Method"]

    train_df = _load_training_data()
    rates = compute_per_guest_rates(train_df)
    per_guest_rate = rates.get((food_type, prep_method))
    fallback_used = per_guest_rate is None
    if per_guest_rate is None:
        per_guest_rate = float(
            (train_df["Quantity of Food"] / train_df["Number of Guests"]).median()
        )

    base_qty = num_guests * per_guest_rate

    val_residuals = np.array(metadata.get("val_residuals", []))
    if len(val_residuals) > 0:
        buffer = float(np.quantile(val_residuals, service_level))
    else:
        buffer = 0.0

    raw_qty = base_qty + buffer
    recommended_qty = max(0, math.ceil(raw_qty))

    estimated_wastage_pct = (
        predicted_wastage / recommended_qty * 100
        if recommended_qty > 0
        else None
    )

    assumptions = [
        f"Per-guest rate ({per_guest_rate:.3f} units/guest) derived from "
        f"{'global median (group too small)' if fallback_used else f'{food_type} × {prep_method} historical median'}.",
        f"Predicted wastage ({predicted_wastage:.1f} units) from Random Forest on "
        f"pre-event context features only.",
        f"Buffer ({buffer:.1f} units) = {service_level*100:.0f}th percentile of "
        f"validation-fold absolute residuals ({len(val_residuals)} observations).",
        "No sold-quantity data exists. Stockout risk cannot be quantified from this dataset.",
        "Result is an estimate based on historical patterns. Actual wastage will vary.",
    ]

    return {
        "recommended_qty": recommended_qty,
        "predicted_wastage_units": round(predicted_wastage, 2),
        "base_qty": round(base_qty, 2),
        "buffer_units": round(buffer, 2),
        "service_level": service_level,
        "estimated_wastage_pct": round(estimated_wastage_pct, 2) if estimated_wastage_pct is not None else None,
        "per_guest_rate": round(per_guest_rate, 4),
        "assumptions": assumptions,
    }


def what_if(
    context: dict[str, Any],
    reduce_pct: float,
    model: RandomForestRegressor,
    metadata: dict,
    service_level: float = 0.90,
) -> dict[str, Any]:
    """
    Estimates the effect of reducing preparation by reduce_pct percent.

    Returns the base recommendation alongside the reduced scenario,
    with estimated change in waste units and estimated unmet demand
    (based on the gap between reduced qty and the base recommendation —
    not actual demand, which is unobservable).

    Both outputs are labelled as estimates.
    """
    if not (0.0 < reduce_pct < 100.0):
        raise ValueError(f"reduce_pct must be in (0, 100), got {reduce_pct}.")

    base = recommend(context, model, metadata, service_level)
    base_qty = base["recommended_qty"]
    reduced_qty = max(0, math.ceil(base_qty * (1 - reduce_pct / 100)))

    predicted_wastage = base["predicted_wastage_units"]

    # Estimated sold = min(estimated demand proxy, qty prepared)
    # Demand proxy = base_qty (historical preparation rate × guests)
    demand_proxy = base["base_qty"]
    est_sold_base = min(demand_proxy, base_qty)
    est_waste_base = max(base_qty - est_sold_base, 0)

    est_sold_reduced = min(demand_proxy, reduced_qty)
    est_waste_reduced = max(reduced_qty - est_sold_reduced, 0)
    est_unmet_reduced = max(demand_proxy - reduced_qty, 0)

    waste_units_saved = est_waste_base - est_waste_reduced
    waste_pct_base = est_waste_base / base_qty * 100 if base_qty > 0 else None
    waste_pct_reduced = est_waste_reduced / reduced_qty * 100 if reduced_qty > 0 else None

    return {
        "base_recommendation": base,
        "reduced_scenario": {
            "reduce_pct": reduce_pct,
            "reduced_qty": reduced_qty,
            "est_waste_units": round(est_waste_reduced, 2),
            "est_waste_pct": round(waste_pct_reduced, 2) if waste_pct_reduced is not None else None,
            "est_unmet_units": round(est_unmet_reduced, 2),
            "est_waste_units_saved_vs_base": round(waste_units_saved, 2),
        },
        "caveat": (
            "These figures are simulation estimates based on historical per-guest rates. "
            "Actual demand is unobservable in this dataset (no sold-quantity column). "
            "Unmet demand is the gap between the reduced quantity and the historical "
            "preparation rate, not actual stockouts. Do not present these as measured outcomes."
        ),
    }
