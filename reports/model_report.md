# Model Report

## Dataset and split

- Training rows: 1035
- Validation rows (for buffer): 259
- Test rows: 324
- Split: Stratified random split (Type of Food × Pricing), random_state=42, test_size=0.20. No time-based split: the dataset has no date column.

## Features used

| Feature | Type |
|---|---|
| Type of Food | categorical (ordinal-encoded) |
| Event Type | categorical (ordinal-encoded) |
| Storage Conditions | categorical (ordinal-encoded) |
| Purchase History | categorical (ordinal-encoded) |
| Seasonality | categorical (ordinal-encoded) |
| Preparation Method | categorical (ordinal-encoded) |
| Geographical Location | categorical (ordinal-encoded) |
| Pricing | categorical (ordinal-encoded) |
| Number of Guests | numeric |

**Excluded from features:** Quantity of Food (preparation decision, not a pre-event input); Wastage Food Amount (the target); wastage_pct (derived from target).

## Baselines vs Random Forest

| Model | MAE (units) | RMSE | R² | WAPE |
|---|---|---|---|---|
| Baseline: Overall Mean | 8.778 | 10.656 | -0.0004 | 30.39% |
| Baseline: Food Type Mean | 8.762 | 10.641 | 0.0023 | 30.34% |
| Baseline: Event Type Mean | 8.811 | 10.719 | -0.0123 | 30.51% |
| **Random Forest** | **2.276** | **3.492** | **0.8926** | **7.88%** |

## Metric explanations

- **MAE 2.28 units** — on average the model's prediction is 2.28 units away from the actual wastage amount.
- **RMSE 3.49 units** — larger errors are penalised more; a value higher than MAE indicates some events are predicted poorly.
- **R² 0.8926** — the model explains 89.3% of the variance in wastage amount on the test set.
- **WAPE 7.88%** — total absolute error as a percentage of total actual wastage. Do not read this as 'the model is 92% accurate' — that framing is misleading.

## Verdict

The Random Forest beats all three baselines on MAE (best baseline MAE: 8.762, RF MAE: 2.276). It provides a measurable improvement over simple group-mean heuristics.

## Feature importance (impurity-based)

| Feature | Importance |
|---|---|
| Pricing | 0.6303 |
| Number of Guests | 0.2697 |
| Preparation Method | 0.0487 |
| Type of Food | 0.0128 |
| Event Type | 0.0126 |
| Geographical Location | 0.0118 |
| Seasonality | 0.0083 |
| Storage Conditions | 0.0032 |
| Purchase History | 0.0026 |

## Limitations

- No time dimension in the source data. Results cannot be extrapolated to specific dates, seasons beyond the three categories in the dataset, or future trend changes.
- No Quantity_Sold column exists. Stockout rates cannot be measured. The recommendation engine estimates preparation quantity from predicted wastage and a per-guest rate; it does not model unmet demand.
- The dataset records historical catering events. Whether the relationships generalise to future events with different guest profiles depends on conditions not present in the data.
- Observed wastage may be censored if events ran out of food (zero wastage may mean 'nothing left to waste', not 'perfect preparation'). This cannot be distinguished in the current data.
