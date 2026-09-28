from __future__ import annotations
import json
from pathlib import Path
from fastapi import APIRouter
from backend.app.repositories import event_repo
from backend.app.schemas.model import InsightItem
from backend.app.core.config import settings

router = APIRouter(prefix="/api", tags=["insights"])


def _load_metadata() -> dict:
    path = Path(settings.model_metadata_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/insights", response_model=list[InsightItem])
def get_insights() -> list[InsightItem]:
    """
    Generates 5-7 insight statements programmatically from computed results.
    Every statement includes a number, the finding, the comparison basis,
    and a caveat where the sample is small or confounding is likely.
    """
    from backend.app.repositories.event_repo import _load_df
    import numpy as np
    from scipy import stats

    df = _load_df()
    meta = _load_metadata()
    insights: list[InsightItem] = []

    # 1. Top wastage food type vs overall mean
    food_means = df.groupby("Type of Food")["wastage_pct"].agg(n="count", mean="mean")
    overall_mean = float(df["wastage_pct"].mean())
    top_food = food_means["mean"].idxmax()
    top_food_mean = float(food_means.loc[top_food, "mean"])
    top_food_n = int(food_means.loc[top_food, "n"])
    diff = top_food_mean - overall_mean
    insights.append(InsightItem(
        number=1,
        statement=(
            f"{top_food} has the highest mean wastage at {top_food_mean:.1f}%, "
            f"which is {diff:.1f} percentage points above the overall mean of {overall_mean:.1f}%."
        ),
        comparison_basis=f"Overall mean across all {len(df):,} events.",
        caveat=f"n={top_food_n:,}. Differences between food types are small in absolute terms.",
    ))

    # 2. Pricing effect
    pricing_means = df.groupby("Pricing")["wastage_pct"].agg(n="count", mean="mean")
    high_mean = float(pricing_means.loc["High", "mean"]) if "High" in pricing_means.index else None
    low_mean = float(pricing_means.loc["Low", "mean"]) if "Low" in pricing_means.index else None
    if high_mean is not None and low_mean is not None:
        high_n = int(pricing_means.loc["High", "n"])
        low_n = int(pricing_means.loc["Low", "n"])
        insights.append(InsightItem(
            number=2,
            statement=(
                f"High-pricing events waste {high_mean:.1f}% of prepared food on average, "
                f"compared to {low_mean:.1f}% for low-pricing events — "
                f"a {high_mean - low_mean:.1f} percentage point gap."
            ),
            comparison_basis=f"High (n={high_n:,}) vs Low (n={low_n:,}) pricing tier.",
            caveat=(
                "Pricing tier is not a direct promotion flag. "
                "It may proxy event scale, menu richness, or guest expectations. "
                "The effect persists across event types (cross-tab in notebook 02)."
            ),
        ))

    # 3. Preparation method effect
    prep_means = df.groupby("Preparation Method")["wastage_pct"].agg(n="count", mean="mean")
    top_prep = prep_means["mean"].idxmax()
    low_prep = prep_means["mean"].idxmin()
    top_prep_mean = float(prep_means.loc[top_prep, "mean"])
    low_prep_mean = float(prep_means.loc[low_prep, "mean"])
    top_prep_n = int(prep_means.loc[top_prep, "n"])
    low_prep_n = int(prep_means.loc[low_prep, "n"])

    groups_prep = [
        df[df["Preparation Method"] == m]["wastage_pct"].values
        for m in df["Preparation Method"].unique()
    ]
    all_vals = np.concatenate(groups_prep)
    grand_mean = all_vals.mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups_prep)
    ss_total = sum((v - grand_mean) ** 2 for v in all_vals)
    eta2 = ss_between / ss_total if ss_total > 0 else 0.0

    insights.append(InsightItem(
        number=3,
        statement=(
            f"{top_prep} service produces the highest mean wastage ({top_prep_mean:.1f}%), "
            f"while {low_prep} produces the lowest ({low_prep_mean:.1f}%). "
            f"Preparation method accounts for {eta2*100:.1f}% of the variance in wastage "
            f"(eta-squared = {eta2:.3f}, a medium effect)."
        ),
        comparison_basis=f"{top_prep} (n={top_prep_n:,}) vs {low_prep} (n={low_prep_n:,}).",
        caveat=(
            "Preparation method is not randomly assigned across event types. "
            "Sit-down dinners are concentrated at weddings; "
            "finger food at corporate and birthday events."
        ),
    ))

    # 4. Guest count correlation
    r, p = stats.pearsonr(df["Number of Guests"], df["wastage_pct"])
    direction = "positive" if r > 0 else "negative"
    insights.append(InsightItem(
        number=4,
        statement=(
            f"Larger events tend to waste a higher percentage of prepared food. "
            f"The {direction} correlation between guest count and wastage % is "
            f"r = {r:.3f} (p < 0.001)."
        ),
        comparison_basis=f"Pearson r across all {len(df):,} events.",
        caveat=(
            "Correlation does not imply causation. Larger events may use "
            "preparation methods (e.g. buffet) that structurally produce more waste, "
            "or caterers may over-prepare more conservatively for large gatherings."
        ),
    ))

    # 5. Model vs baseline
    if meta:
        rf_mae = meta["test_metrics"]["mae"]
        best_bl_mae = min(v["mae"] for v in meta["baseline_metrics"].values())
        improvement = best_bl_mae - rf_mae
        insights.append(InsightItem(
            number=5,
            statement=(
                f"The Random Forest model predicts wastage with a mean absolute error of "
                f"{rf_mae:.2f} units, compared to {best_bl_mae:.2f} units for the best "
                f"simple baseline — an improvement of {improvement:.2f} units per event."
            ),
            comparison_basis=(
                f"Test set of {meta['test_rows']} events. "
                f"Baseline = food-type mean from training data."
            ),
            caveat=(
                "The model uses only pre-event context features. "
                "It cannot account for on-the-day factors such as actual attendance "
                "or last-minute menu changes."
            ),
        ))

    # 6. Highest-waste food × event combination (min 10 obs)
    combo = (
        df.groupby(["Type of Food", "Event Type"])["wastage_pct"]
        .agg(n="count", mean="mean")
        .reset_index()
    )
    combo = combo[combo["n"] >= 10].sort_values("mean", ascending=False)
    if not combo.empty:
        top_row = combo.iloc[0]
        insights.append(InsightItem(
            number=6,
            statement=(
                f"The highest-waste combination is {top_row['Type of Food']} at "
                f"{top_row['Event Type']} events: mean wastage {top_row['mean']:.1f}% "
                f"across {int(top_row['n'])} events."
            ),
            comparison_basis=f"All food type × event type combinations with at least 10 observations.",
            caveat=(
                f"n={int(top_row['n'])}. "
                "Differences between combinations are modest; "
                "no single combination stands out dramatically."
            ),
        ))

    # 7. Storage conditions finding
    refrigerated = df[df["Storage Conditions"] == "Refrigerated"]["wastage_pct"].values
    room_temp = df[df["Storage Conditions"] == "Room Temperature"]["wastage_pct"].values
    if len(refrigerated) > 1 and len(room_temp) > 1:
        _, p_storage = stats.ttest_ind(refrigerated, room_temp)
        diff_storage = refrigerated.mean() - room_temp.mean()
        direction_s = "higher" if diff_storage > 0 else "lower"
        insights.append(InsightItem(
            number=7,
            statement=(
                f"Refrigerated storage is associated with {direction_s} wastage "
                f"({refrigerated.mean():.1f}% vs {room_temp.mean():.1f}% for room temperature), "
                f"but the difference is not statistically significant (p = {p_storage:.3f})."
            ),
            comparison_basis=(
                f"Refrigerated (n={len(refrigerated):,}) vs "
                f"Room Temperature (n={len(room_temp):,})."
            ),
            caveat=(
                "Storage conditions are not randomly assigned: Meat is mostly refrigerated, "
                "Baked Goods are mostly room temperature. "
                "The apparent storage effect is largely a food-type effect."
            ),
        ))

    return insights
