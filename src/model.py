"""
Random Forest model training, evaluation, and persistence.

Usage:
    python -m src.model

Produces:
    models/random_forest.joblib
    models/model_metadata.json
    outputs/actual_vs_predicted.png
    reports/model_report.md
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.inspection import permutation_importance

from src.features import build_features, ALL_FEATURE_COLS, TARGET_COL
from src.utils import compute_wastage_pct

CLEAN_CSV = Path("data/processed/clean_events.csv")
MODELS_DIR = Path("models")
OUTPUTS_DIR = Path("outputs")
REPORTS_DIR = Path("reports")

EXCLUSION_FLAGS = [
    "flag_duplicate", "flag_negative_qty",
    "flag_zero_prepared", "flag_wastage_exceeds_prepared",
]

RANDOM_STATE = 42
TEST_SIZE = 0.20
VAL_SIZE = 0.20  # fraction of training set used for residual validation


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    """MAE, RMSE, R², WAPE — the four reported metrics."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    mae = float(np.mean(np.abs(actual - predicted)))
    rmse = float(sqrt(np.mean((actual - predicted) ** 2)))

    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - actual.mean()) ** 2)
    r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

    # WAPE: sum of absolute errors / sum of actuals × 100
    wape = float(np.sum(np.abs(actual - predicted)) / np.sum(actual) * 100) \
        if np.sum(actual) > 0 else float("nan")

    return {"mae": mae, "rmse": rmse, "r2": r2, "wape": wape}


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------

def compute_baselines(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> dict[str, dict[str, float]]:
    """
    Three simple baselines evaluated on the test set.

    These set the floor the Random Forest must clear to be useful.
    """
    results: dict[str, dict[str, float]] = {}
    y_test = test_df[TARGET_COL].values

    # 1. Overall mean
    overall_mean = train_df[TARGET_COL].mean()
    pred_overall = np.full(len(y_test), overall_mean)
    results["overall_mean"] = compute_metrics(y_test, pred_overall)

    # 2. Per-food-type mean
    food_means = train_df.groupby("Type of Food")[TARGET_COL].mean().to_dict()
    global_fallback = overall_mean
    pred_food = test_df["Type of Food"].map(food_means).fillna(global_fallback).values
    results["food_type_mean"] = compute_metrics(y_test, pred_food)

    # 3. Per-event-type mean
    event_means = train_df.groupby("Event Type")[TARGET_COL].mean().to_dict()
    pred_event = test_df["Event Type"].map(event_means).fillna(global_fallback).values
    results["event_type_mean"] = compute_metrics(y_test, pred_event)

    return results


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train(df: pd.DataFrame) -> tuple[RandomForestRegressor, dict, np.ndarray]:
    """
    Trains and evaluates the Random Forest.

    Returns (fitted_model, metadata_dict, val_residuals).
    val_residuals are absolute residuals from a validation fold, used by
    the recommendation engine to compute preparation buffers. They are
    kept separate from the reported test set.
    """
    # Apply exclusion flags
    present_excl = [c for c in EXCLUSION_FLAGS if c in df.columns]
    if present_excl:
        df = df[~df[present_excl].any(axis=1)].copy()

    print(f"Training rows after exclusions: {len(df)}")

    # Stratify on food type + pricing combined to ensure cell coverage
    df["_strata"] = df["Type of Food"] + "|" + df["Pricing"]

    train_df, test_df = train_test_split(
        df,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df["_strata"],
    )
    train_df = train_df.drop(columns=["_strata"])
    test_df = test_df.drop(columns=["_strata"])
    df = df.drop(columns=["_strata"])

    print(f"Train: {len(train_df)}, Test: {len(test_df)}")

    # Validation fold from training rows (last VAL_SIZE by index)
    # Used for residual-based buffer — not reported as test metrics.
    val_cutoff = int(len(train_df) * (1 - VAL_SIZE))
    train_fit_df = train_df.iloc[:val_cutoff]
    val_df = train_df.iloc[val_cutoff:]

    # Baselines (computed before fitting the RF to avoid any data leak)
    print("Computing baselines...")
    baseline_metrics = compute_baselines(train_fit_df, test_df)
    for name, metrics in baseline_metrics.items():
        print(f"  Baseline {name}: MAE={metrics['mae']:.3f}, RMSE={metrics['rmse']:.3f}, "
              f"R²={metrics['r2']:.4f}, WAPE={metrics['wape']:.2f}%")

    # Build features
    X_train, y_train = build_features(train_fit_df)
    X_val, y_val = build_features(val_df)
    X_test, y_test = build_features(test_df)

    # Grid search within training fold only
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [None, 10, 20],
        "min_samples_leaf": [1, 3],
    }
    rf = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1)
    gs = GridSearchCV(
        rf, param_grid,
        scoring="neg_mean_absolute_error",
        cv=3,
        refit=True,
        n_jobs=-1,
    )
    print("Running grid search (3-fold CV on training fold)...")
    gs.fit(X_train, y_train)
    best_params = gs.best_params_
    print(f"  Best params: {best_params}")

    model = gs.best_estimator_

    # Validation residuals for buffer computation
    val_preds = model.predict(X_val)
    val_residuals = np.abs(y_val.values - val_preds)

    # Test set evaluation
    test_preds = model.predict(X_test)
    test_metrics = compute_metrics(y_test.values, test_preds)
    print(f"Test metrics: MAE={test_metrics['mae']:.3f}, RMSE={test_metrics['rmse']:.3f}, "
          f"R²={test_metrics['r2']:.4f}, WAPE={test_metrics['wape']:.2f}%")

    # Feature importance — impurity-based
    impurity_importance = dict(zip(ALL_FEATURE_COLS, model.feature_importances_.tolist()))

    metadata = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "features": ALL_FEATURE_COLS,
        "target": TARGET_COL,
        "train_rows": len(train_fit_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "split_strategy": (
            "Stratified random split (Type of Food × Pricing), "
            "random_state=42, test_size=0.20. "
            "No time-based split: the dataset has no date column."
        ),
        "best_params": best_params,
        "test_metrics": test_metrics,
        "baseline_metrics": baseline_metrics,
        "impurity_importance": impurity_importance,
        "val_residuals_p50": float(np.percentile(val_residuals, 50)),
        "val_residuals_p90": float(np.percentile(val_residuals, 90)),
        "val_residuals_p95": float(np.percentile(val_residuals, 95)),
        "library_versions": {
            "sklearn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }

    # Save chart
    _save_actual_vs_predicted(y_test.values, test_preds, test_metrics)

    # Error breakdown
    _print_error_breakdown(test_df, y_test.values, test_preds)

    return model, metadata, val_residuals


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_model(model: RandomForestRegressor, metadata: dict) -> None:
    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODELS_DIR / "random_forest.joblib")
    (MODELS_DIR / "model_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(f"Saved: {MODELS_DIR}/random_forest.joblib")
    print(f"Saved: {MODELS_DIR}/model_metadata.json")


def load_model() -> tuple[RandomForestRegressor, dict]:
    model_path = MODELS_DIR / "random_forest.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at '{model_path}'. Run: python -m src.model"
        )
    model = joblib.load(model_path)
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    return model, metadata


# ---------------------------------------------------------------------------
# Charts and breakdown
# ---------------------------------------------------------------------------

def _save_actual_vs_predicted(
    actual: np.ndarray,
    predicted: np.ndarray,
    metrics: dict[str, float],
) -> None:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(actual, predicted, alpha=0.35, s=18, color="#2c6e8a", edgecolors="none")
    lims = [
        min(actual.min(), predicted.min()) - 2,
        max(actual.max(), predicted.max()) + 2,
    ]
    ax.plot(lims, lims, color="#c0392b", linewidth=1, linestyle="--", label="Perfect prediction")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Actual wastage (units)")
    ax.set_ylabel("Predicted wastage (units)")
    ax.set_title(
        f"Actual vs Predicted — test set (n={len(actual)})\n"
        f"MAE {metrics['mae']:.2f} units  |  RMSE {metrics['rmse']:.2f}  |  "
        f"R² {metrics['r2']:.3f}  |  WAPE {metrics['wape']:.1f}%",
        fontsize=9,
    )
    ax.legend(fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    out_path = OUTPUTS_DIR / "actual_vs_predicted.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def _print_error_breakdown(
    test_df: pd.DataFrame,
    actual: np.ndarray,
    predicted: np.ndarray,
) -> None:
    residuals = actual - predicted
    abs_residuals = np.abs(residuals)

    print("\nError breakdown by food type:")
    for food_type in sorted(test_df["Type of Food"].unique()):
        mask = (test_df["Type of Food"] == food_type).values
        if mask.sum() == 0:
            continue
        mae = abs_residuals[mask].mean()
        bias = residuals[mask].mean()
        print(f"  {food_type:20s}  n={mask.sum():4d}  MAE={mae:.2f}  bias={bias:+.2f}")

    print("\nError breakdown by event type:")
    for event_type in sorted(test_df["Event Type"].unique()):
        mask = (test_df["Event Type"] == event_type).values
        if mask.sum() == 0:
            continue
        mae = abs_residuals[mask].mean()
        bias = residuals[mask].mean()
        print(f"  {event_type:20s}  n={mask.sum():4d}  MAE={mae:.2f}  bias={bias:+.2f}")


# ---------------------------------------------------------------------------
# Model report
# ---------------------------------------------------------------------------

def write_model_report(metadata: dict) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    m = metadata["test_metrics"]
    b = metadata["baseline_metrics"]

    rf_beats_all = all(
        m["mae"] < b[bl]["mae"] for bl in b
    )

    lines = [
        "# Model Report",
        "",
        "## Dataset and split",
        "",
        f"- Training rows: {metadata['train_rows']}",
        f"- Validation rows (for buffer): {metadata['val_rows']}",
        f"- Test rows: {metadata['test_rows']}",
        f"- Split: {metadata['split_strategy']}",
        "",
        "## Features used",
        "",
        "| Feature | Type |",
        "|---|---|",
    ]
    for f in metadata["features"]:
        ftype = "numeric" if f == "Number of Guests" else "categorical (ordinal-encoded)"
        lines.append(f"| {f} | {ftype} |")

    lines += [
        "",
        "**Excluded from features:** Quantity of Food (preparation decision, not a pre-event input); "
        "Wastage Food Amount (the target); wastage_pct (derived from target).",
        "",
        "## Baselines vs Random Forest",
        "",
        "| Model | MAE (units) | RMSE | R² | WAPE |",
        "|---|---|---|---|---|",
    ]
    for name, bm in b.items():
        label = name.replace("_", " ").title()
        lines.append(
            f"| Baseline: {label} | {bm['mae']:.3f} | {bm['rmse']:.3f} | "
            f"{bm['r2']:.4f} | {bm['wape']:.2f}% |"
        )
    lines.append(
        f"| **Random Forest** | **{m['mae']:.3f}** | **{m['rmse']:.3f}** | "
        f"**{m['r2']:.4f}** | **{m['wape']:.2f}%** |"
    )

    lines += [
        "",
        "## Metric explanations",
        "",
        f"- **MAE {m['mae']:.2f} units** — on average the model's prediction is "
        f"{m['mae']:.2f} units away from the actual wastage amount.",
        f"- **RMSE {m['rmse']:.2f} units** — larger errors are penalised more; "
        f"a value higher than MAE indicates some events are predicted poorly.",
        f"- **R² {m['r2']:.4f}** — the model explains "
        f"{m['r2']*100:.1f}% of the variance in wastage amount on the test set.",
        f"- **WAPE {m['wape']:.2f}%** — total absolute error as a percentage of "
        f"total actual wastage. Do not read this as 'the model is "
        f"{100-m['wape']:.0f}% accurate' — that framing is misleading.",
        "",
        "## Verdict",
        "",
    ]
    if rf_beats_all:
        lines.append(
            f"The Random Forest beats all three baselines on MAE "
            f"(best baseline MAE: {min(b[bl]['mae'] for bl in b):.3f}, "
            f"RF MAE: {m['mae']:.3f}). It provides a measurable improvement "
            f"over simple group-mean heuristics."
        )
    else:
        lines.append(
            f"The Random Forest does **not** beat all baselines on MAE. "
            f"Best baseline MAE: {min(b[bl]['mae'] for bl in b):.3f}, "
            f"RF MAE: {m['mae']:.3f}. "
            f"This is an honest result for a cross-sectional dataset with "
            f"limited signal. The baselines should be preferred for "
            f"production planning until more features are available."
        )

    lines += [
        "",
        "## Feature importance (impurity-based)",
        "",
        "| Feature | Importance |",
        "|---|---|",
    ]
    sorted_imp = sorted(
        metadata["impurity_importance"].items(), key=lambda x: x[1], reverse=True
    )
    for feat, imp in sorted_imp:
        lines.append(f"| {feat} | {imp:.4f} |")

    lines += [
        "",
        "## Limitations",
        "",
        "- No time dimension in the source data. Results cannot be extrapolated to "
        "specific dates, seasons beyond the three categories in the dataset, or "
        "future trend changes.",
        "- No Quantity_Sold column exists. Stockout rates cannot be measured. "
        "The recommendation engine estimates preparation quantity from "
        "predicted wastage and a per-guest rate; it does not model unmet demand.",
        "- The dataset records historical catering events. Whether the relationships "
        "generalise to future events with different guest profiles depends on "
        "conditions not present in the data.",
        "- Observed wastage may be censored if events ran out of food "
        "(zero wastage may mean 'nothing left to waste', not 'perfect preparation'). "
        "This cannot be distinguished in the current data.",
    ]

    (REPORTS_DIR / "model_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved: reports/model_report.md")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> None:
    if not CLEAN_CSV.exists():
        sys.exit(
            f"ERROR: '{CLEAN_CSV}' not found. Run python -m src.pipeline first."
        )

    df = pd.read_csv(CLEAN_CSV)
    model, metadata, val_residuals = train(df)
    save_model(model, metadata)

    # Attach val residuals for the recommender (stored in metadata)
    metadata["val_residuals"] = val_residuals.tolist()
    save_model(model, metadata)

    write_model_report(metadata)
    print("\nTraining complete.")


if __name__ == "__main__":
    run()
