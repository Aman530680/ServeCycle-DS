# ServeCycle: Insights

Generated from 1,618 clean catering event records (1,782 raw minus 164 duplicate rows).
All percentages are wastage % = Wastage Food Amount / Quantity of Food × 100.
No figures in this document are hardcoded — each is derived from the processed dataset.

---

## Insight 1: Pricing tier is the strongest single predictor of wastage rate

High-pricing events waste **8.81%** of prepared food on average.
Low-pricing events waste **5.46%** on average.
The gap is **3.35 percentage points** across 1,618 events.

**Comparison basis:** High (n=612) vs Low (n=410) pricing tier, mean wastage %.

**Caveat:** Pricing tier is not a direct promotion or spend-control flag. It may proxy
event scale, menu richness, or guest expectations. The effect persists across all four
event types (cross-tabulation in notebook 03), so it is not explained by event-type
composition alone. Whether reducing pricing tier reduces waste depends on factors not
present in this dataset.

---

## Insight 2: Preparation method has a medium effect on wastage rate

Sit-down dinner service produces a mean wastage of **7.51%**.
Finger food produces **6.06%**.
Buffet sits between them at **7.02%**.

The difference is statistically significant (one-way ANOVA F=99.1, p<0.001).
Eta-squared = **0.109** — preparation method explains about 11% of the variance in
wastage rate, which is a medium effect by conventional thresholds (0.06–0.14).

**Comparison basis:** Three preparation methods, n=720 / 627 / 271 respectively.

**Caveat:** Preparation method is not randomly assigned. Sit-down dinners are concentrated
at weddings (36% of sit-down events are weddings vs 15% for buffet). The preparation
method effect and the event-type effect are partially confounded. Addressing preparation
method in isolation may not reduce waste if the underlying event mix does not change.

---

## Insight 3: Larger events waste a higher share of prepared food

Events in the top guest-count quartile (approximately 350–491 guests) waste **7.88%**
on average. Events in the bottom quartile (207–267 guests) waste **5.96%**.

Pearson correlation between guest count and wastage %: **r = 0.374** (p < 0.001).
This is a moderate positive association — larger events tend to over-prepare at a higher
rate relative to what they serve.

**Comparison basis:** Quartile bands across 1,618 events.

**Caveat:** Correlation does not establish causation. Larger events may default to
preparation methods (buffet, sit-down) that structurally produce more waste, or caterers
may apply more conservative safety margins for large gatherings. The guest-count effect
partially overlaps with the preparation-method effect.

---

## Insight 4: Storage conditions do not independently predict wastage rate

Refrigerated events waste **6.88%** on average.
Room-temperature events waste **6.86%**.
The difference of **0.027 percentage points** is not statistically significant
(independent t-test p = 0.797, 95% bootstrap CI: [−0.18%, +0.23%]).

**Comparison basis:** Refrigerated (n=582) vs Room Temperature (n=1,036).

**Caveat:** Storage conditions are not randomly assigned across food types. Meat is
predominantly refrigerated (308 of 398 events); Baked Goods are predominantly room
temperature (364 of 366 events). The apparent null effect on waste is consistent with
storage conditions being a consequence of food type, not an independent driver of waste.
Controlling for food type leaves no residual storage effect.

---

## Insight 5: The Random Forest model substantially outperforms simple baselines

On the held-out test set (n=324 events), the Random Forest achieves:

| Metric | Random Forest | Best baseline (food-type mean) |
|---|---|---|
| MAE | **2.28 units** | 8.76 units |
| RMSE | **3.49 units** | 10.64 units |
| R² | **0.893** | 0.002 |
| WAPE | **7.88%** | 30.34% |

The model explains **89.3%** of the variance in wastage amount on the test set and
reduces mean absolute error by 6.48 units per event compared to the best baseline.

**Comparison basis:** Stratified random split, 80/20, stratified on food type × pricing.
No time-based split is possible (the dataset has no date column).

**Caveat:** High R² on a cross-sectional dataset should be interpreted with caution.
The model captures strong within-sample patterns but has not been validated on held-out
time periods or different event populations. The absence of a date column means temporal
generalisation cannot be assessed.

---

## Insight 6: The highest-waste food × event combination is Fruits at Weddings

Mean wastage % = **7.22%** across 81 Wedding events serving Fruits.
Coefficient of variation = 0.27, indicating the high wastage is consistent rather than
driven by a few extreme events.

The top five highest-waste combinations (minimum 10 observations each):

| Food type | Event type | n | Mean wastage % |
|---|---|---|---|
| Fruits | Wedding | 81 | 7.22% |
| Dairy Products | Wedding | 75 | 7.14% |
| Fruits | Birthday | 64 | 7.10% |
| Baked Goods | Corporate | 89 | 7.01% |
| Fruits | Social Gathering | 75 | 6.98% |

**Comparison basis:** All food type × event type combinations with at least 10 observations.

**Caveat:** The range across combinations is narrow (6.62%–7.22%). No single combination
stands out dramatically. Targeted reduction in these combinations is possible but the
absolute savings per event are modest.

---

## Insight 7: Event type differences are small and partially confounded with preparation method

Weddings show the highest mean wastage at **6.96%**; Birthday events the lowest at **6.82%**.
The gap is **0.14 percentage points** — small in absolute terms.

Weddings are the most concentrated event type for sit-down dinner service (36% of
sit-down dinners are weddings), which is the highest-waste preparation method. When
preparation method is held constant, event-type differences shrink further.

**Comparison basis:** Four event types, n=406/461/463/332.

**Caveat:** One-way ANOVA across event types was not statistically significant at p<0.05.
Event type alone is not a reliable predictor of wastage rate once preparation method
is accounted for.
