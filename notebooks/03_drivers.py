# %% [markdown]
# # 03 — Wastage Drivers
#
# Examines preparation method, storage conditions, purchase history, and
# the main confounding relationships between variables.
#
# Every comparison reports: sample sizes, mean wastage %, an effect size,
# and a note on the most plausible confounder.

# %%
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

from src.utils import compute_wastage_pct, HIGH_WASTE_THRESHOLD_PCT

CLEAN_CSV = Path("data/processed/clean_events.csv")
assert CLEAN_CSV.exists(), "Run python -m src.pipeline first."

df_all = pd.read_csv(CLEAN_CSV)

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
print(f"Working rows: {len(df)}")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.alpha": 0.35,
})
WASTE_COLOR = "#c0392b"
PRIMARY_COLOR = "#2c6e8a"


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Cohen's d for two independent samples."""
    pooled_std = np.sqrt((np.std(a, ddof=1) ** 2 + np.std(b, ddof=1) ** 2) / 2)
    if pooled_std == 0:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled_std)


def eta_squared(groups: list[np.ndarray]) -> float:
    """Eta-squared from one-way ANOVA (proportion of variance explained)."""
    all_vals = np.concatenate(groups)
    grand_mean = all_vals.mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    ss_total = sum((v - grand_mean) ** 2 for v in all_vals)
    if ss_total == 0:
        return 0.0
    return float(ss_between / ss_total)


# %% [markdown]
# ## 1. Wastage % by preparation method
#
# Effect size: eta-squared (proportion of variance in wastage % explained
# by preparation method). Small = 0.01, medium = 0.06, large = 0.14.

# %%
grp_prep = (
    df.groupby("Preparation Method")["wastage_pct"]
    .agg(n="count", mean="mean", median="median", std="std")
    .reset_index()
    .sort_values("mean", ascending=False)
)
print(grp_prep.round(2).to_string(index=False))

groups_prep = [
    df[df["Preparation Method"] == m]["wastage_pct"].values
    for m in df["Preparation Method"].unique()
]
f_stat, p_val = stats.f_oneway(*groups_prep)
eta2 = eta_squared(groups_prep)
print(f"\nOne-way ANOVA: F={f_stat:.3f}, p={p_val:.4f}")
print(f"Eta-squared: {eta2:.4f} ({'small' if eta2 < 0.06 else 'medium' if eta2 < 0.14 else 'large'} effect)")

# Confounder check: is preparation method unevenly distributed across event types?
print("\nPreparation Method × Event Type distribution (row %):")
ct = pd.crosstab(df["Preparation Method"], df["Event Type"], normalize="index").round(2)
print(ct.to_string())

# %%
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(
    grp_prep["Preparation Method"], grp_prep["mean"],
    color=PRIMARY_COLOR, edgecolor="white", linewidth=0.5,
)
for patch, (_, row) in zip(ax.patches, grp_prep.iterrows()):
    h = patch.get_height()
    ax.text(patch.get_x() + patch.get_width() / 2, h + 0.1,
            f"{h:.1f}%", ha="center", va="bottom", fontsize=8)
ax.set_title(
    f"Mean wastage % by preparation method\n"
    f"(eta-squared = {eta2:.3f}, p = {p_val:.3f})",
    pad=10,
)
ax.set_xlabel("Preparation method")
ax.set_ylabel("Mean wastage %")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
for i, (_, row) in enumerate(grp_prep.iterrows()):
    ax.text(i, -0.6, f"n={int(row['n']):,}", ha="center", va="top",
            fontsize=8, color="#555", transform=ax.get_xaxis_transform())
plt.tight_layout()
plt.savefig(Path("outputs") / "waste_by_preparation_method.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 2. Wastage % by storage conditions
#
# Refrigerated vs Room Temperature. Effect size: Cohen's d.
# Confounder: storage conditions correlate with food type
# (perishables like Meat/Dairy are refrigerated; Baked Goods tend to be stored
# at room temperature). The two-way breakdown separates these effects.

# %%
grp_storage = (
    df.groupby("Storage Conditions")["wastage_pct"]
    .agg(n="count", mean="mean", median="median", std="std")
    .reset_index()
    .sort_values("mean", ascending=False)
)
print(grp_storage.round(2).to_string(index=False))

refrigerated = df[df["Storage Conditions"] == "Refrigerated"]["wastage_pct"].values
room_temp = df[df["Storage Conditions"] == "Room Temperature"]["wastage_pct"].values
d = cohens_d(refrigerated, room_temp)
t_stat, t_pval = stats.ttest_ind(refrigerated, room_temp)
print(f"\nCohen's d (Refrigerated vs Room Temperature): {d:.4f}")
print(f"Independent t-test: t={t_stat:.3f}, p={t_pval:.4f}")
if t_pval > 0.05:
    print("  No statistically significant difference in means (p > 0.05).")

# Bootstrap 95% CI on the mean difference
np.random.seed(42)
boot_diffs = [
    np.random.choice(refrigerated, len(refrigerated), replace=True).mean()
    - np.random.choice(room_temp, len(room_temp), replace=True).mean()
    for _ in range(5000)
]
ci_low, ci_high = np.percentile(boot_diffs, [2.5, 97.5])
mean_diff = refrigerated.mean() - room_temp.mean()
print(f"Mean difference (Refrigerated - Room Temp): {mean_diff:.3f}%")
print(f"95% bootstrap CI: [{ci_low:.3f}%, {ci_high:.3f}%]")

# Two-way breakdown: food type × storage conditions
print("\nFood type × Storage Conditions — mean wastage %:")
two_way = df.pivot_table(
    values="wastage_pct", index="Type of Food",
    columns="Storage Conditions", aggfunc=["mean", "count"],
)
print(two_way.round(2).to_string())
print("\nConfounder note: storage conditions are not randomly assigned across food types. "
      "Differences between storage groups partly reflect food-type composition.")

# %% [markdown]
# ## 3. Wastage % by purchase history
#
# Regular vs Occasional supplier. Occasional events have smaller samples;
# interpret with caution.

# %%
grp_purchase = (
    df.groupby("Purchase History")["wastage_pct"]
    .agg(n="count", mean="mean", median="median", std="std")
    .reset_index()
    .sort_values("mean", ascending=False)
)
print(grp_purchase.round(2).to_string(index=False))

regular = df[df["Purchase History"] == "Regular"]["wastage_pct"].values
occasional = df[df["Purchase History"] == "Occasional"]["wastage_pct"].values
d_purch = cohens_d(regular, occasional)
t_s, t_p = stats.ttest_ind(regular, occasional)
print(f"\nCohen's d (Regular vs Occasional): {d_purch:.4f}")
print(f"t-test: t={t_s:.3f}, p={t_p:.4f}")

# Are Occasional events concentrated in a specific food type or event type?
print("\nPurchase History × Food Type distribution (row %):")
print(pd.crosstab(df["Purchase History"], df["Type of Food"], normalize="index").round(2).to_string())
print("\nPurchase History × Event Type distribution (row %):")
print(pd.crosstab(df["Purchase History"], df["Event Type"], normalize="index").round(2).to_string())

# %% [markdown]
# ## 4. Confounder cross-tabulations
#
# These cross-tabs surface the main structural relationships between categorical
# variables. Each comparison in notebooks 02 and 03 should be read with these
# in mind before drawing conclusions about individual factors.

# %%
print("=" * 60)
print("Preparation Method × Event Type (count)")
print(pd.crosstab(df["Preparation Method"], df["Event Type"]).to_string())

print("\n" + "=" * 60)
print("Storage Conditions × Food Type (count)")
print(pd.crosstab(df["Storage Conditions"], df["Type of Food"]).to_string())

print("\n" + "=" * 60)
print("Seasonality × Event Type (count)")
print(pd.crosstab(df["Seasonality"], df["Event Type"]).to_string())

print("\n" + "=" * 60)
print("Pricing × Geographical Location (count)")
print(pd.crosstab(df["Pricing"], df["Geographical Location"]).to_string())

# %% [markdown]
# ## 5. Consistently high-waste food type × event type combinations
#
# Ranked by mean wastage %, with minimum 10 observations per cell.
# Coefficient of variation (CV = std / mean) indicates consistency:
# lower CV means wastage is more predictably high.

# %%
MIN_OBS = 10
combo = (
    df.groupby(["Type of Food", "Event Type"])["wastage_pct"]
    .agg(n="count", mean="mean", std="std", median="median")
    .reset_index()
)
combo["cv"] = combo["std"] / combo["mean"]
combo["high_waste_share_pct"] = (
    df[df["wastage_pct"] > HIGH_WASTE_THRESHOLD_PCT]
    .groupby(["Type of Food", "Event Type"])
    .size()
    .reindex(pd.MultiIndex.from_frame(combo[["Type of Food", "Event Type"]]), fill_value=0)
    .values
    / combo["n"]
    * 100
)
combo_filtered = combo[combo["n"] >= MIN_OBS].sort_values("mean", ascending=False)
print(f"Combinations with >= {MIN_OBS} observations, ranked by mean wastage %:")
print(combo_filtered.round(2).to_string(index=False))
