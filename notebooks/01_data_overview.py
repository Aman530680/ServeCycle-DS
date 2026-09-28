# %% [markdown]
# # 01 — Data Overview
#
# Loads `data/processed/clean_events.csv` and documents the dataset's shape,
# column types, distributions, and flag summary. This notebook does not produce
# charts for the final report — those are in 02 and 03.
#
# **Dataset:** 1,782 catering event records. No Date, Outlet_ID, Quantity_Sold
# or time dimension exists in the source data. All analysis is cross-sectional.

# %%
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.utils import compute_wastage_pct, CATEGORICAL_COLUMNS, ALL_FLAG_COLUMNS if False else None

# resolve flag columns without importing the clean module at top level
FLAG_COLUMNS = [
    "flag_missing", "flag_duplicate", "flag_negative_qty",
    "flag_zero_prepared", "flag_wastage_exceeds_prepared",
    "flag_outlier_guests", "flag_outlier_qty_food",
    "flag_outlier_wastage", "flag_unknown_category",
]

CLEAN_CSV = Path("data/processed/clean_events.csv")
assert CLEAN_CSV.exists(), f"Run the pipeline first: python -m src.pipeline"
df = pd.read_csv(CLEAN_CSV)
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")

# %% [markdown]
# ## 1. Shape and columns

# %%
print(df.dtypes.to_string())

# %% [markdown]
# ## 2. Numeric column distributions

# %%
numeric_cols = ["Number of Guests", "Quantity of Food", "Wastage Food Amount"]
print(df[numeric_cols].describe().round(2).to_string())

# %%
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, col in zip(axes, numeric_cols):
    ax.hist(df[col], bins=30, color="#4a7c9e", edgecolor="white", linewidth=0.4)
    ax.set_title(col)
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")
    ax.tick_params(labelsize=9)
fig.suptitle("Numeric column distributions (all 1,782 rows)", y=1.01, fontsize=11)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 3. Derived wastage %

# %%
wastage_pct = compute_wastage_pct(df)
print(wastage_pct.describe().round(3).to_string())
print(f"\nRows with zero Quantity of Food (wastage % undefined): {wastage_pct.isna().sum()}")

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(wastage_pct.dropna(), bins=40, color="#c0392b", edgecolor="white", linewidth=0.4)
ax.set_title("Distribution of wastage % (Wastage / Prepared × 100)")
ax.set_xlabel("Wastage %")
ax.set_ylabel("Count")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 4. Categorical columns — distinct value counts

# %%
cat_cols = [c for c in CATEGORICAL_COLUMNS if c in df.columns]
for col in cat_cols:
    counts = df[col].value_counts()
    print(f"\n{col}:")
    print(counts.to_string())

# %% [markdown]
# ## 5. Flag column summary
#
# Rows are flagged but not removed. Only rows with exclusion flags
# (duplicate, negative qty, zero prepared, wastage > prepared) are
# excluded from model training.

# %%
present_flags = [c for c in FLAG_COLUMNS if c in df.columns]
flag_summary = df[present_flags].sum().rename("flagged_rows")
print(flag_summary.to_string())
print(f"\nRows with at least one flag: {df[present_flags].any(axis=1).sum()}")
print(f"Rows with no flags (clean): {(~df[present_flags].any(axis=1)).sum()}")

# %% [markdown]
# ## 6. Missing values

# %%
null_counts = df.isnull().sum()
if null_counts.sum() == 0:
    print("No missing values in any column.")
else:
    print(null_counts[null_counts > 0].to_string())
