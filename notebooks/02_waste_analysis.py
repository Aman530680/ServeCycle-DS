# %% [markdown]
# # 02 — Waste Analysis
#
# Examines wastage % across food type, event type, pricing, location,
# seasonality, preparation method, and guest count bands.
#
# All four required output charts are produced here and saved to `outputs/`.
# Every comparison states sample sizes and an effect measure.
#
# **Wastage % = Wastage Food Amount / Quantity of Food × 100.**
# Rows where Quantity of Food is zero are excluded from wastage % calculations.

# %%
from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

from src.utils import compute_wastage_pct, HIGH_WASTE_THRESHOLD_PCT

CLEAN_CSV = Path("data/processed/clean_events.csv")
OUTPUTS = Path("outputs")
OUTPUTS.mkdir(exist_ok=True)

assert CLEAN_CSV.exists(), "Run python -m src.pipeline first."
df_all = pd.read_csv(CLEAN_CSV)

# Working set: exclude rows flagged for exclusion from training
# (duplicates, zero prepared, negatives, wastage > prepared)
EXCLUSION_FLAGS = [
    "flag_duplicate", "flag_negative_qty",
    "flag_zero_prepared", "flag_wastage_exceeds_prepared",
]
present_excl = [c for c in EXCLUSION_FLAGS if c in df_all.columns]
if present_excl:
    df = df_all[~df_all[present_excl].any(axis=1)].copy()
else:
    df = df_all.copy()

df["wastage_pct"] = compute_wastage_pct(df)
df = df[df["wastage_pct"].notna()].copy()

print(f"Working rows (exclusions removed, wastage% defined): {len(df)}")
print(f"Overall wastage %: mean {df['wastage_pct'].mean():.2f}%, "
      f"median {df['wastage_pct'].median():.2f}%, "
      f"std {df['wastage_pct'].std():.2f}%")
print(f"Total units prepared: {df['Quantity of Food'].sum():,}")
print(f"Total units wasted:   {df['Wastage Food Amount'].sum():,}")

# %%
# Shared chart style — applied consistently across all figures
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.alpha": 0.35,
    "grid.linewidth": 0.6,
})
WASTE_COLOR = "#c0392b"
PRIMARY_COLOR = "#2c6e8a"
BAR_EDGE = "white"


def annotate_bars(ax, fmt="{:.1f}%", fontsize=8):
    """Add value labels on top of bars."""
    for patch in ax.patches:
        h = patch.get_height()
        if math.isnan(h):
            continue
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            h + 0.1,
            fmt.format(h),
            ha="center", va="bottom", fontsize=fontsize, color="#333333",
        )


def add_n_labels(ax, counts, y_offset=-0.8, fontsize=8):
    """Add n= labels below x-axis ticks."""
    for i, n in enumerate(counts):
        ax.text(
            i, y_offset, f"n={n:,}",
            ha="center", va="top", fontsize=fontsize, color="#666666",
            transform=ax.get_xaxis_transform(),
        )


# %% [markdown]
# ## 1. Wastage % by food type
#
# Ranked by mean wastage %. Volume alone is a misleading rank because a high-volume
# category can dominate totals even with a moderate rate.

# %%
grp_food = (
    df.groupby("Type of Food")["wastage_pct"]
    .agg(n="count", mean="mean", median="median", std="std")
    .reset_index()
)
grp_food["high_waste_share"] = (
    df[df["wastage_pct"] > HIGH_WASTE_THRESHOLD_PCT]
    .groupby("Type of Food")
    .size()
    .reindex(grp_food["Type of Food"], fill_value=0)
    .values
    / grp_food["n"]
    * 100
)
grp_food = grp_food.sort_values("mean", ascending=False)
print(grp_food.round(2).to_string(index=False))

# %%
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(
    grp_food["Type of Food"], grp_food["mean"],
    color=WASTE_COLOR, edgecolor=BAR_EDGE, linewidth=0.5,
)
annotate_bars(ax)
ax.set_title("Mean wastage % by food type\n(% of units prepared that were discarded)", pad=10)
ax.set_xlabel("Food type")
ax.set_ylabel("Mean wastage %")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
for i, (_, row) in enumerate(grp_food.iterrows()):
    ax.text(i, -0.6, f"n={int(row['n']):,}", ha="center", va="top",
            fontsize=8, color="#555555", transform=ax.get_xaxis_transform())
plt.tight_layout()
plt.savefig(OUTPUTS / "waste_by_food_type.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"Saved: outputs/waste_by_food_type.png")

# %% [markdown]
# ## 2. Wastage % by event type

# %%
grp_event = (
    df.groupby("Event Type")["wastage_pct"]
    .agg(n="count", mean="mean", median="median", std="std")
    .reset_index()
    .sort_values("mean", ascending=False)
)
print(grp_event.round(2).to_string(index=False))

# %%
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(
    grp_event["Event Type"], grp_event["mean"],
    color=PRIMARY_COLOR, edgecolor=BAR_EDGE, linewidth=0.5,
)
annotate_bars(ax)
ax.set_title("Mean wastage % by event type\n(% of units prepared that were discarded)", pad=10)
ax.set_xlabel("Event type")
ax.set_ylabel("Mean wastage %")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
for i, (_, row) in enumerate(grp_event.iterrows()):
    ax.text(i, -0.6, f"n={int(row['n']):,}", ha="center", va="top",
            fontsize=8, color="#555555", transform=ax.get_xaxis_transform())
plt.tight_layout()
plt.savefig(OUTPUTS / "waste_by_event_type.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"Saved: outputs/waste_by_event_type.png")

# %% [markdown]
# ## 3. Wastage % by pricing tier
#
# Note: pricing may proxy event scale (higher-priced events may serve richer menus
# with different preparation ratios). Cross-tab with event type below.

# %%
grp_pricing = (
    df.groupby("Pricing")["wastage_pct"]
    .agg(n="count", mean="mean", median="median", std="std")
    .reset_index()
    .sort_values("mean", ascending=False)
)
print(grp_pricing.round(2).to_string(index=False))

# Check for confounding: is pricing unevenly distributed across event types?
pricing_event_crosstab = pd.crosstab(df["Pricing"], df["Event Type"], normalize="index").round(2)
print("\nPricing × Event Type distribution (row %):")
print(pricing_event_crosstab.to_string())

# %%
fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(
    grp_pricing["Pricing"], grp_pricing["mean"],
    color="#e67e22", edgecolor=BAR_EDGE, linewidth=0.5,
)
annotate_bars(ax)
ax.set_title("Mean wastage % by pricing tier\n(% of units prepared that were discarded)", pad=10)
ax.set_xlabel("Pricing tier")
ax.set_ylabel("Mean wastage %")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
for i, (_, row) in enumerate(grp_pricing.iterrows()):
    ax.text(i, -0.6, f"n={int(row['n']):,}", ha="center", va="top",
            fontsize=8, color="#555555", transform=ax.get_xaxis_transform())
plt.tight_layout()
plt.savefig(OUTPUTS / "waste_by_pricing.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"Saved: outputs/waste_by_pricing.png")

# %% [markdown]
# ## 4. Wastage heatmap — food type × event type
#
# Cells show mean wastage %. Minimum 10 observations per cell required;
# cells below this threshold are masked.

# %%
MIN_OBS = 10
heatmap_mean = df.pivot_table(
    values="wastage_pct", index="Type of Food",
    columns="Event Type", aggfunc="mean",
)
heatmap_count = df.pivot_table(
    values="wastage_pct", index="Type of Food",
    columns="Event Type", aggfunc="count",
)
# Mask cells with fewer than MIN_OBS observations
heatmap_masked = heatmap_mean.where(heatmap_count >= MIN_OBS)

print("Mean wastage % (food type × event type):")
print(heatmap_mean.round(2).to_string())
print(f"\nCell counts (masked if < {MIN_OBS}):")
print(heatmap_count.to_string())

# %%
fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(
    heatmap_masked,
    annot=True, fmt=".1f", linewidths=0.5,
    cmap="YlOrRd", ax=ax,
    cbar_kws={"label": "Mean wastage %"},
    annot_kws={"size": 10},
)
ax.set_title(
    f"Mean wastage % by food type and event type\n"
    f"(cells with fewer than {MIN_OBS} observations are blank)",
    pad=10,
)
ax.set_xlabel("Event type")
ax.set_ylabel("Food type")
plt.tight_layout()
plt.savefig(OUTPUTS / "wastage_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"Saved: outputs/wastage_heatmap.png")

# %% [markdown]
# ## 5. Wastage % by geographical location

# %%
grp_loc = (
    df.groupby("Geographical Location")["wastage_pct"]
    .agg(n="count", mean="mean", median="median", std="std")
    .reset_index()
    .sort_values("mean", ascending=False)
)
print(grp_loc.round(2).to_string(index=False))

# One-way ANOVA across locations
groups_loc = [
    df[df["Geographical Location"] == loc]["wastage_pct"].values
    for loc in df["Geographical Location"].unique()
]
f_stat, p_val = stats.f_oneway(*groups_loc)
print(f"\nOne-way ANOVA across locations: F={f_stat:.3f}, p={p_val:.4f}")
if p_val > 0.05:
    print("  No statistically significant difference in wastage % across locations (p > 0.05).")
else:
    print("  Statistically significant difference detected (p <= 0.05).")

# %% [markdown]
# ## 6. Wastage % by seasonality

# %%
grp_season = (
    df.groupby("Seasonality")["wastage_pct"]
    .agg(n="count", mean="mean", median="median", std="std")
    .reset_index()
    .sort_values("mean", ascending=False)
)
print(grp_season.round(2).to_string(index=False))
print("\nNote: 'All Seasons' indicates events not tied to a specific season, "
      "not a fourth season.")

# %% [markdown]
# ## 7. Wastage % by guest count band
#
# Guests are binned into quartiles. The Pearson correlation coefficient
# measures the linear association between guest count and wastage %.
# A significant correlation does not imply causation.

# %%
df["guest_band"] = pd.qcut(
    df["Number of Guests"], q=4,
    labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]
)
grp_guests = (
    df.groupby("guest_band", observed=True)["wastage_pct"]
    .agg(n="count", mean="mean", median="median", std="std")
    .reset_index()
)
print(grp_guests.round(2).to_string(index=False))

r, p = stats.pearsonr(df["Number of Guests"], df["wastage_pct"])
print(f"\nPearson r (Number of Guests vs wastage %): {r:.4f}, p={p:.4f}")
if abs(r) < 0.1:
    print("  Negligible linear association.")
elif abs(r) < 0.3:
    print("  Weak linear association.")
else:
    print("  Moderate or stronger linear association.")
print("  Caveat: Pearson r assumes a linear relationship; "
      "the true relationship may be non-linear.")
