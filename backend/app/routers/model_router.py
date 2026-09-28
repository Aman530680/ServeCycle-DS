from __future__ import annotations
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.app.schemas.model import (
    MetricsResponse,
    FeaturesResponse,
    ActualVsPredictedPoint,
    BaselineItem,
)
from backend.app.core.config import settings

router = APIRouter(prefix="/api/model", tags=["model"])


def _load_metadata() -> dict:
    path = Path(settings.model_metadata_path)
    if not path.exists():
        raise HTTPException(
            status_code=503,
            detail="Model metadata not found. Run python -m src.model first.",
        )
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/metrics", response_model=MetricsResponse)
def model_metrics() -> MetricsResponse:
    meta = _load_metadata()
    m = meta["test_metrics"]
    return MetricsResponse(
        mae=round(m["mae"], 4),
        rmse=round(m["rmse"], 4),
        r2=round(m["r2"], 4),
        wape=round(m["wape"], 4),
        train_rows=meta["train_rows"],
        test_rows=meta["test_rows"],
        split_strategy=meta["split_strategy"],
        plain_language={
            "mae": (
                f"On average the model's prediction is {m['mae']:.2f} units away "
                "from the actual wastage amount."
            ),
            "rmse": (
                f"Root mean squared error is {m['rmse']:.2f} units. "
                "Higher than MAE means some events are predicted with larger errors."
            ),
            "r2": (
                f"The model explains {m['r2']*100:.1f}% of the variance in "
                "wastage amount on the test set."
            ),
            "wape": (
                f"Total absolute error is {m['wape']:.1f}% of total actual wastage. "
                "Do not read this as an accuracy percentage."
            ),
        },
    )


@router.get("/baselines")
def model_baselines() -> list[BaselineItem]:
    meta = _load_metadata()
    items = []
    for name, m in meta["baseline_metrics"].items():
        items.append(BaselineItem(
            name=name.replace("_", " ").title(),
            mae=round(m["mae"], 4),
            rmse=round(m["rmse"], 4),
            r2=round(m["r2"], 4),
            wape=round(m["wape"], 4),
        ))
    return items


@router.get("/features", response_model=FeaturesResponse)
def model_features() -> FeaturesResponse:
    meta = _load_metadata()
    return FeaturesResponse(
        features=meta["features"],
        target=meta["target"],
        excluded=["Quantity of Food", "Wastage Food Amount", "wastage_pct"],
        best_params=meta["best_params"],
    )


@router.get("/actual-vs-predicted")
def actual_vs_predicted() -> list[dict]:
    """
    The actual vs predicted chart PNG is at outputs/actual_vs_predicted.png.
    This endpoint returns the image path for the frontend to serve directly.
    """
    path = Path("outputs/actual_vs_predicted.png")
    return [{"chart_path": str(path), "exists": path.exists()}]


@router.get("/importance")
def feature_importance() -> list[dict]:
    meta = _load_metadata()
    imp = meta.get("impurity_importance", {})
    return sorted(
        [{"feature": k, "importance": round(v, 6)} for k, v in imp.items()],
        key=lambda x: x["importance"],
        reverse=True,
    )
