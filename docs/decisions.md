# Architecture Decision Log

Decisions made during the build of ServeCycle, in the order they were made.
Each entry states what was decided, why, and what the alternative was.

---

## D01 — Adapt spec to real dataset schema (not invent data)

**Date:** Session start
**Decision:** Rewrite all specs, steering files, and requirements to fit the actual
dataset columns rather than the originally described restaurant outlet/product schema.

**Why:** The source dataset contains no Date, Outlet_ID, Product_ID, Quantity_Sold,
Weather, Weekday, Holiday, or Promotion columns. The tech steering rule is explicit:
"If the dataset is missing, stop and ask. Never invent one." The same principle extends
to inventing columns. Proceeding with the original spec would have required fabricating
data, which produces a dishonest submission.

**Alternative rejected:** Synthetically extending the dataset by adding a Date column
and deriving Quantity_Sold = Quantity_Prepared − Wastage_Food_Amount. Rejected because
the resulting sold quantity would be circular (it shares a direct arithmetic relationship
with the target) and the time dimension would be artificial, producing misleading
time-series results.

**Consequence:** The project is genuinely answerable from the data. The core assignment
question ("what is causing food wastage?") is answered through EDA and a predictive
model. Time-series analysis, lag features, and outlet-level recommendations are not
included because the data does not support them. This is stated wherever relevant.

---

## D02 — Target is Wastage Food Amount, not Quantity_Sold

**Decision:** Train the Random Forest to predict Wastage Food Amount (units discarded)
rather than a demand proxy.

**Why:** There is no Quantity_Sold column. The closest demand proxy would be
Quantity_Prepared − Wastage_Food_Amount, but this is circular: it shares a direct
arithmetic relationship with both input features and the "target." Predicting wastage
directly from pre-event context is the honest formulation given the data available.

**Consequence:** The recommendation engine estimates preparation as
(guests × per-guest-rate) + predicted wastage + buffer. It cannot quantify stockout
risk. This limitation is stated in every output that touches recommendations.

---

## D03 — Quantity of Food excluded from model features

**Decision:** Exclude Quantity of Food (the preparation quantity) from model features.

**Why:** Quantity of Food is a preparation decision, not an input known before
preparation is decided. Including it would mean the model needs to know the answer
(how much to prepare) to produce the answer. It would also severely inflate apparent
model performance on the training set because preparation quantity and wastage are
correlated in the historical data.

**Alternative rejected:** Including Quantity of Food as a feature with a note that it
represents a "planning estimate." Rejected because the API cannot know the preparation
quantity at prediction time — that is what the user is asking us to determine.

---

## D04 — Stratified random split, not time-based split

**Decision:** Use a stratified random split (80/20, stratified on food type × pricing)
rather than a time-based split.

**Why:** The dataset has no date column. A time-based split is not possible. This is
stated explicitly in the model report, model metadata JSON, and the API's plain-language
metric explanations.

**Consequence:** The train/test split does not reflect temporal generalisation. The
model's performance on future events (which the random split assumes are similar to
training events) may differ from the reported test metrics if event patterns shift over
time. This is a genuine limitation of the dataset, not a modelling choice.

---

## D05 — OrdinalEncoder over OneHotEncoder for categorical features

**Decision:** Use sklearn's OrdinalEncoder with a fixed category order rather than
OneHotEncoder.

**Why:** Random Forest handles ordinal-encoded categoricals correctly and does not
require one-hot expansion. OrdinalEncoder keeps the feature space compact (9 features
instead of up to 30+ with one-hot), which speeds up grid search and makes feature
importance scores easier to interpret (one score per original feature rather than one
per dummy variable). The fixed category order is stored in model_metadata.json so the
API reproduces the same mapping at prediction time.

**Alternative rejected:** OneHotEncoder. Would work correctly but produces a wider
feature matrix with no accuracy benefit for tree-based models, and splits feature
importance across multiple columns for the same original variable.

---

## D06 — API reads from CSV, not MySQL directly

**Decision:** The FastAPI backend reads from data/processed/clean_events.csv via
pandas rather than querying MySQL on every request.

**Why:** MySQL requires a running database server. Reading from a CSV file in a
lru_cache makes the API functional without any database setup, which is critical for
portfolio and academic contexts where reviewers may not have MySQL installed. The MySQL
schema, loader, and verification scripts are still fully implemented and tested.

**Alternative rejected:** Requiring MySQL for all API calls. This would make the
development and review experience significantly harder and adds no analytical value
for the read endpoints.

**Consequence:** The lru_cache means the API serves stale data if the pipeline is
re-run while the server is running. For this use case (analysis of a static dataset)
that is acceptable. A production deployment would use database queries directly.

---

## D07 — Validation residuals from a separate fold, not the test set

**Decision:** The buffer added to preparation recommendations is derived from the
90th percentile of absolute residuals on a validation fold (last 20% of training rows
by index), not the reported test set.

**Why:** Using test-set residuals for the buffer would contaminate the test set
evaluation. The buffer is a deployment parameter, not a training metric — it should
be calibrated on a separate window that does not affect the reported MAE/RMSE/R²/WAPE
figures.

**Consequence:** The reported test metrics are conservative (they do not benefit from
any test-set-specific tuning). The buffer is an honest estimate of prediction error
in deployment.

---

## D08 — No Docker

**Decision:** No Docker or container orchestration.

**Why:** The tech steering file explicitly prohibits Docker. All services (API, pipeline,
model training) run as plain Python processes. The frontend runs via Vite's dev server.
This keeps the setup reproducible on any machine with Python 3.12+ and Node 18+.

---

## D09 — Insights generated programmatically, not hardcoded

**Decision:** The /api/insights endpoint computes all 7 insight statements at request
time from the processed dataset, with numbers, comparison bases, and caveats derived
from actual aggregations.

**Why:** The product steering file is explicit: "Insights are generated from data,
never hardcoded." Hardcoding insight text would produce a submission that appears to
show analytical work but actually bypasses it.

**Consequence:** Insights change if the underlying data changes. Numbers in the
insight text always match the numbers in the EDA notebooks because they use the same
computation path.

---

## D10 — CSS custom properties for all design tokens, no CSS-in-JS

**Decision:** All colours, spacing, and typography values live in tokens.css as CSS
custom properties. Components reference them via var(--token-name).

**Why:** CSS custom properties are inherited, inspectable in browser devtools, and
require no runtime overhead. They produce consistent values across all components
without a build-time dependency on a CSS-in-JS library.

**Alternative rejected:** Tailwind CSS. Would require an additional build step and
configuration file. The design system for this project is small enough that hand-written
tokens are easier to audit and modify.
