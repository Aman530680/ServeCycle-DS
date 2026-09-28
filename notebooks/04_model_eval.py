# %% [markdown]
# # 04 — Model Evaluation
#
# Loads the trained Random Forest, compares it against baselines, and
# examines feature importance and error patterns.
#
# The actual-vs-predicted chart is saved to `outputs/actual_vs_predicted.png`.
# All numbers come from the saved model_metadata.json — no re-training here.

# %%
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

from src.model import load_model, compute_metrics, compute_baselines
from src.features import build_features, ALL_FEATURE_COLS
from src.utils import compute_wastage_pct

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

OUTPUTS = Path("outputs")
OUTPUTS.mkdir(exist_ok=True)

model, metadata = load_model()
print(f"Model trained at: {metadata['trained_at']}")
print(f"Train: {metadata['train_rows']} rows, Val: {metadata['val_rows']} rows, Test: {metadata['test_rows']} rows")

# %% [markdown]
# ## 1. Baseline comparison

# %%
baselines = metadata["baseline_metrics"]
test_m = metadata["test_metrics"]

rows = []
for name, m in baselines.items():
    rows.append({"Model": name.replace("_", " ").title(), **m})
rows.append({"Model": "Random Forest", **test_m})
comparison = pd.DataFrame(rows).set_index("Model")
print(comparison.round(3).to_string())

# %% [markdown]
# ## 2. Feature importance — impurity-based

# %%
imp = metadata["impurity_importance"]
imp_series = pd.Series(imp).sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(imp_series.index, imp_series.values, color="#2c6e8a", edgecolor="white")
ax.set_title("Feature importance (impurity-based)\nHigher = more predictive of wastage amount", pad=10)
ax.set_xlabel("Mean decrease in impurity")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(OUTPUTS / "feature_importance.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: outputs/feature_importance.png")

# %% [markdown]
# ## 3. Actual vs Predicted (reproduced from training artefact)
#
# Chart already saved to outputs/actual_vs_predicted.png during training.
# Displaying the saved image here for notebook completeness.

# %%
from IPython.display import Image
img_path = OUTPUTS / "actual_vs_predicted.png"
if img_path.exists():
    print(f"Chart at: {img_path}")
else:
    print("Run python -m src.model to generate the chart.")

# %% [markdown]
# ## 4. Validation residuals — buffer percentiles

# %%
val_res = np.array(metadata.get("val_residuals", []))
if len(val_res) > 0:
    for pct in [50, 75, 90, 95]:
        print(f"  {pct}th percentile of |val_residuals|: {np.percentile(val_res, pct):.2f} units")
    print(f"\nAt 90% service level, the buffer added to recommended preparation is "
          f"{np.percentile(val_res, 90):.2f} units.")

# %% [markdown]
# ## 5. Model verdict
#
# The Random Forest MAE vs best baseline MAE, plain language.

# %%
best_baseline_mae = min(v["mae"] for v in baselines.values())
rf_mae = test_m["mae"]
if rf_mae < best_baseline_mae:
    improvement = best_baseline_mae - rf_mae
    print(f"The Random Forest (MAE {rf_mae:.3f}) beats the best baseline "
          f"(MAE {best_baseline_mae:.3f}) by {improvement:.3f} units on average.")
    print(f"R² = {test_m['r2']:.4f}: the model explains "
          f"{test_m['r2']*100:.1f}% of the variance in wastage amount.")
else:
    print(f"The Random Forest (MAE {rf_mae:.3f}) does not beat the best baseline "
          f"(MAE {best_baseline_mae:.3f}). Use baselines for planning.")
