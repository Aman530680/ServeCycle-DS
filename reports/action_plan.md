# ServeCycle: Action Plan

These recommendations are derived from the data analysis in this project.
All preparation quantities are estimates based on historical patterns.
There is no sold-quantity column in the source data, so stockout risk cannot be
quantified. Do not present projected savings as measured outcomes.

---

## How to read this plan

Each action is linked to a specific driver identified in the EDA or model.
The format is:

- **Context** — which combination of factors applies
- **Current pattern** — what the historical data shows
- **Recommended action** — what to change
- **Projected effect** — estimated impact based on historical wastage rates (labelled as estimates)
- **Confidence** — how reliably the pattern holds (based on sample size and effect size)

---

## Action 1: Review preparation quantities for high-pricing events

**Context:** All high-pricing events regardless of food type or preparation method.

**Current pattern:** High-pricing events waste 8.81% of prepared food on average
(n=612). Low-pricing events waste 5.46% (n=410). The gap is 3.35 percentage points.

**Recommended action:** For high-pricing events, apply the model recommendation
endpoint to get a context-specific preparation quantity before each event. The model
predicts wastage from pre-event inputs (food type, guests, method, pricing, location,
season) with a test-set MAE of 2.28 units.

As a starting point: if a high-pricing event currently prepares at the historical
median of approximately 400 units, reducing preparation toward the model recommendation
(which accounts for guest count and preparation method) is likely to reduce waste
without increasing the risk of running short at the stated 90% service level.

**Projected effect:** Bringing high-pricing events to the mean wastage rate of
moderate-pricing events (5.84%) would represent an estimated reduction of approximately
2.97 percentage points. On an event preparing 400 units that is approximately 12 units
per event. This is an estimate based on historical means, not a controlled trial.

**Confidence:** High sample size (n=612). The pricing effect persists across event
types. Medium confidence.

---

## Action 2: Consider finger food service for events where it is operationally viable

**Context:** Any event where sit-down dinner or buffet service is currently used but
the event format would also suit finger food.

**Current pattern:** Sit-down dinner service produces mean wastage of 7.51% (n=720).
Finger food produces 6.06% (n=627). Buffet is 7.02% (n=271). Preparation method
explains approximately 11% of the variance in wastage rate (eta-squared = 0.109).

**Recommended action:** Where the event format permits, prefer finger food service
over sit-down dinner or buffet. This is most applicable to Corporate events and Birthday
events, where finger food already accounts for 32% and 24% of events respectively.
For Weddings, the operational and guest-expectation constraints on service style are
likely to outweigh the waste reduction benefit.

**Projected effect:** Switching a sit-down dinner event to finger food service is
associated with approximately 1.45 percentage points lower wastage on average. On an
event preparing 400 units that is approximately 6 units. This is an estimate.

**Confidence:** Medium. Effect size is medium (eta-squared = 0.109, F=99.1, p<0.001).
Preparation method is partially confounded with event type. Caution required.

---

## Action 3: Apply tighter preparation scaling for large events

**Context:** Events with 350 or more guests (top quartile, n=405).

**Current pattern:** Events in the top guest-count quartile waste 7.88% on average.
Events in the bottom quartile (207–267 guests) waste 5.96%. The Pearson correlation
between guest count and wastage % is r = 0.374 (p < 0.001).

**Recommended action:** For events with 350+ guests, use the model recommendation
endpoint before finalising preparation quantities. The per-guest preparation rate used
by the model is calibrated per (food type, preparation method) group from historical
data. Large events tend to have been over-prepared historically; the model adjusts for
this by predicting the likely wastage and setting the buffer at the 90th percentile of
validation residuals (approximately 5.3 units).

**Projected effect:** Bringing top-quartile events to the overall mean wastage rate of
6.87% would represent a reduction of approximately 1.01 percentage points for those
events. On an average large event preparing around 430 units that is approximately
4 units per event. Estimate only.

**Confidence:** Moderate. Correlation is statistically significant with r = 0.374 but
causation is not established. The effect may partly reflect preparation method
composition at large events.

---

## Action 4: No action needed on storage conditions

**Context:** Decisions about whether to refrigerate or store at room temperature.

**Current pattern:** Refrigerated and room-temperature events show no statistically
significant difference in wastage rate (p = 0.797, difference = 0.027 percentage
points). After accounting for food type, there is no residual storage effect.

**Recommended action:** Storage decisions should continue to be driven by food safety
requirements (Meat and Dairy require refrigeration regardless of any waste-reduction
consideration). There is no evidence in this dataset that changing storage conditions
would reduce wastage.

**Confidence:** High. The null result is backed by a sufficient sample (n=582 vs 1,036)
and a tight bootstrap confidence interval (−0.18%, +0.23%).

---

## Action 5: Use the prediction endpoint for event planning

**Context:** Any new event before preparation quantities are finalised.

**Recommended workflow:**
1. Identify the event's food type, guest count, event type, preparation method,
   storage conditions, seasonality, location, and pricing tier.
2. Call `POST /api/predict-demand` with these inputs and `service_level=0.90`.
3. The response includes `recommended_qty` (integer, ready to use), `predicted_wastage_units`,
   `base_qty` (guests × per-guest rate), `buffer_units` (90th percentile of validation
   residuals), and `estimated_wastage_pct`.
4. Review the `assumptions` list in the response — it states the per-guest rate source,
   the buffer derivation, and the data limitations.
5. Use the `POST /api/what-if` endpoint to see the estimated effect of reducing
   preparation by a chosen percentage before committing.

**Caveat:** The model was trained on 1,618 events. For event contexts that are rare in
the training data (e.g. Occasional purchase history, which accounts for only 12% of
records), predictions are less reliable. The response includes the per-guest rate source
which indicates whether a group-specific or global fallback rate was used.

---

## What this plan does not cover

- **Unit costs.** The dataset contains no cost or revenue information. Projected savings
  are in units, not currency. Do not attach financial values to these estimates without
  independent cost data.
- **Outlet-level recommendations.** The dataset has three geographic categories
  (Suburban, Urban, Rural), not individual outlet identifiers. Outlet-specific targets
  cannot be set from this data.
- **Demand forecasting.** There is no sold-quantity column. The model predicts wastage,
  not demand. The distinction matters: reducing preparation reduces waste but the effect
  on unmet demand cannot be measured from this data.
- **Causal claims.** All associations in this plan are observational. None of the
  recommended actions have been tested in a controlled setting.
