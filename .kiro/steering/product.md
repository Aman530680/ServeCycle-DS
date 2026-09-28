# ServeCycle: Product

Food waste analysis platform for catering and event operations — portfolio and academic submission (assignment DS_Day01_18: "Restaurant: What is causing food wastage?").

Core question: which combinations of food type, event context, preparation method, storage conditions, location, and pricing drive the highest wastage, and what preparation quantity should be planned for a given event to minimise waste without running short?

## Dataset reality

The source dataset does not contain Date, Outlet_ID, Product_ID, Quantity_Sold, Weather, Weekday, Holiday, or Promotion columns. It contains 1,782 records of catering events with the following actual columns:

| Column | Role |
|---|---|
| Type of Food | Food category (Meat, Baked Goods, Dairy Products, Fruits, Vegetables) |
| Number of Guests | Planned attendance |
| Event Type | Corporate, Social Gathering, Wedding, Birthday |
| Quantity of Food | Units prepared (equivalent to Quantity_Prepared) |
| Storage Conditions | Refrigerated or Room Temperature |
| Purchase History | Regular or Occasional supplier |
| Seasonality | Winter, Summer, All Seasons |
| Preparation Method | Sit-down Dinner, Finger Food, Buffet |
| Geographical Location | Suburban, Urban, Rural |
| Pricing | High, Moderate, Low |
| Wastage Food Amount | Units discarded (equivalent to Quantity_Discarded) |

There is no time dimension, no sold quantity, and no outlet-level granularity. All analysis, modelling, and recommendations are adapted to this schema. Any reference to time-series analysis, lag features, rolling windows, or sold-quantity forecasting from the original spec brief does not apply and must not be invented.

## Adapted project scope

- Data cleaning and validation of the real columns
- EDA: wastage % by food type, event type, location, storage, preparation method, pricing, seasonality, and guest count bands
- Wastage driver analysis: which factors explain high wastage, with effect sizes and sample sizes
- Random Forest regression to predict Wastage Food Amount (or wastage %) from event context features known before preparation
- Model evaluation: MAE, RMSE, R2, WAPE against baselines; feature importance
- Recommendation engine: given an event's context, estimate expected wastage and suggest an adjusted preparation quantity
- FastAPI backend serving all computed results and the prediction endpoint
- React dashboard visualising the analysis

## Users

Operations managers planning catering for events. The product is an internal tool: calm, clear, numbers-first.

## Assignment coverage

Data cleaning and validation, EDA, wastage %, consistently high-waste food types and event contexts, event type analysis (proxy for promotion/special event), storage and preparation method analysis, geographical and seasonal effects, whether a model improves preparation planning, Random Forest, proper evaluation, 5 to 7 insights, 4 visualisations, practical action plan.

## Principles

- Honesty over impressiveness. If the model is weak or a hypothesis is not supported, say so and investigate.
- Insights are generated from data, never hardcoded.
- Simulated savings are estimates, not proof. Label them everywhere.
- The absence of time, sold quantity, and outlet columns is stated explicitly in the README, model report, and action plan. Never paper over it.
