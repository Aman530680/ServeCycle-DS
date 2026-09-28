# Spec 2: demand-model — Tasks

## T1 — src/features.py
Implement `build_features(df)` returning X (DataFrame) and y (Series).
Categorical encoding via OrdinalEncoder fitted on training data only and stored.
Single function shared by training (src/model.py) and API prediction.
Traces to: design feature table, leakage rules.

## T2 — Leakage check
Verify no feature uses Quantity of Food, Wastage Food Amount, or any derived column.
Confirmed by inspection and a unit test in tests/test_features.py.
Traces to: tech steering leakage rules.

--- REVIEW: features and leakage test ---

## T3 — Baselines in src/model.py
Implement three baseline predictors: overall mean, food-type mean, event-type mean.
Evaluate each on test set with MAE, RMSE, R², WAPE.
Traces to: design baseline section.

## T4 — Random Forest training
Implement train(), evaluate(), save_model() in src/model.py.
GridSearchCV with 3-fold CV, fixed random_state=42.
Save random_forest.joblib and model_metadata.json.
Write model_run row to MySQL (if DB available; skip gracefully if not).
Traces to: design model architecture, artefacts.

## T5 — Evaluation notebook
notebooks/04_model_eval.py: load model, compare baselines, feature importance
(impurity + permutation), error breakdown by food type and event type,
actual vs predicted chart → outputs/actual_vs_predicted.png.
Traces to: design metrics, notebook section.

--- REVIEW: model and evaluation ---

## T6 — src/recommender.py
Implement recommend(context, model, metadata, service_level=0.90).
Per-group per_guest_rate, buffer from val residuals, floor at zero, ceil.
what_if(context, reduce_pct, model, metadata) for reduction scenario.
Traces to: design recommendation engine.

## T7 — tests/test_features.py and tests/test_recommender.py
Leakage test: confirm no forbidden column in feature output.
Recommender tests: buffer logic, higher service level never lowers recommendation,
floor at zero, rounding always produces integer.
Traces to: tech steering test requirements.

--- REVIEW: recommendation engine and simulation ---
