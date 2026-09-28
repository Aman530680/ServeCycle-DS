# Spec 2: demand-model — Design

## Target and allowed features

**Target:** `Wastage Food Amount` (units discarded per event).

**Features allowed** — all are known before the event and before preparation:

| Feature | Source column | Encoding |
|---|---|---|
| food_type | Type of Food | OrdinalEncoder (consistent label→int mapping) |
| event_type | Event Type | OrdinalEncoder |
| num_guests | Number of Guests | numeric, as-is |
| storage_conditions | Storage Conditions | OrdinalEncoder |
| purchase_history | Purchase History | OrdinalEncoder |
| seasonality | Seasonality | OrdinalEncoder |
| preparation_method | Preparation Method | OrdinalEncoder |
| geographical_location | Geographical Location | OrdinalEncoder |
| pricing | Pricing | OrdinalEncoder |

**Excluded from model features:**
- `Quantity of Food` — this is a preparation decision, not an input available before planning
- `wastage_pct` — derived from the target; using it would be circular

OrdinalEncoder is used (not OneHotEncoder) because Random Forest handles ordinal-encoded categoricals correctly and the feature space stays compact. Category ordering within each encoder is fixed at fit time and stored in model_metadata.json so the API reproduces the same encoding.

## Train/test split

Stratified random split: 80% train, 20% test. Stratified on `Type of Food` × `Pricing` combined strata to ensure each cell is represented in both sets. Fixed `random_state=42`.

No time-based split because the dataset has no date column. This is stated explicitly in the model report.

## Baselines

Three baselines computed on the test set:
1. **Overall mean** — predict the training set mean for every test row
2. **Food-type mean** — predict the per-food-type training mean
3. **Event-type mean** — predict the per-event-type training mean

The Random Forest must beat all three on MAE and RMSE to be considered useful.

## Model architecture

`sklearn.ensemble.RandomForestRegressor` with a small grid search using 3-fold cross-validation on the training set only:

```
n_estimators: [100, 200]
max_depth:    [None, 10, 20]
min_samples_leaf: [1, 3]
```

`random_state=42` fixed. Best parameters selected by mean MAE across folds.

## Metrics

Evaluated on the held-out test set:
- **MAE** — mean absolute error in units
- **RMSE** — root mean squared error in units
- **R²** — proportion of variance explained
- **WAPE** — weighted absolute percentage error = sum(|actual - predicted|) / sum(actual) × 100

Never report "X% accurate". Each metric is reported with a plain-language sentence.

## Artefacts

- `models/random_forest.joblib` — fitted pipeline (encoder + model)
- `models/model_metadata.json` — feature list, category mappings, train/test sizes, all metrics, library versions, split strategy

## Recommendation engine

```
predicted_wastage = model.predict(context_features)
recommended_qty   = ceil(num_guests × per_guest_rate + predicted_wastage)
                  = max(0, recommended_qty)
```

`per_guest_rate` is the training-set median of `Quantity of Food / Number of Guests`. This is a per-event-context scalar, not a global constant — it is computed per (food_type, preparation_method) group where n ≥ 10, falling back to the global median.

The recommendation also returns:
- `predicted_wastage_units` — the model's prediction
- `estimated_wastage_pct` — predicted / recommended × 100
- `service_level` — parameter (default 0.90), used to add a buffer from validation residuals

**Buffer from residuals:**
```
buffer = quantile(abs(val_residuals), service_level)
recommended_qty = ceil(base_qty + buffer)
```

Val residuals come from a validation fold (last 20% of training rows by index, not reported as test), separate from the reported test set.

## Notebook

`notebooks/04_model_eval.py` — training run summary, baseline comparison, feature importance, actual vs predicted chart (saved to `outputs/actual_vs_predicted.png`), error breakdown by food type and event type.
