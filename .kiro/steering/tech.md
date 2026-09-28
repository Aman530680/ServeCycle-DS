# ServeCycle: Tech

## Stack

Python, Pandas, NumPy; Matplotlib and Seaborn for EDA; scikit-learn RandomForestRegressor and Joblib; MySQL 8+; FastAPI, SQLAlchemy, Pydantic, Uvicorn; React, TypeScript (strict), Vite, Recharts; Pytest, Vitest, React Testing Library; Git.

## Hard constraints

- MySQL 8+ is the source of truth. No SQLite, MongoDB, or JSON files acting as a database.
- No fake data, mock arrays, or hardcoded dashboard numbers or insights.
- No Docker.
- Never modify data/raw/dataset.csv. Cleaning writes to data/processed/.
- If the dataset is missing, stop and ask. Never invent one.
- Never silently delete problem rows. Flag, investigate, document.
- Do not tune data or splits to flatter the model.
- Config through .env; provide .env.example; never commit secrets.

## Adapted data science rules

The dataset contains Quantity of Food (prepared) and Wastage Food Amount (discarded). There is no Quantity_Sold column.

- Wastage % = Wastage_Food_Amount / Quantity_of_Food * 100, with zero prepared handled explicitly. Derived, never stored as a drifting copy.
- Target for the model is Wastage_Food_Amount. Quantity_of_Food is excluded from the main model features because it is itself a preparation decision, not a context input known before planning.
- There is no time dimension. Train/test split is a random stratified split (stratified by food type and event type) with a fixed random_state. State the absence of a time dimension clearly in the model report.
- Baselines first: mean wastage by food type, mean wastage by event type, overall mean. The Random Forest must be compared against all three.
- Metrics: MAE, RMSE, R2, WAPE (or MAPE with zero handling). Never say "X% accurate".
- Training and API prediction share one feature-building code path.
- Recommended preparation = (Number_of_Guests * per_guest_rate) adjusted upward by the model's predicted wastage, floored at zero, rounded up. Always report the waste and shortfall trade-off next to any recommendation.
- Do not invent unit costs.

## Code style

- Small, purposeful functions. Comments explain why, never what.
- No emojis anywhere (code, logs, commits, docs, UI).
- No placeholder names, dead code, commented-out blocks, unused imports, TODO stubs.
- snake_case in Python; camelCase variables and PascalCase components in TypeScript.
- Specific error messages. Never `except Exception: pass`.
- Prefer boring, readable solutions.

## Writing style

- Plain and direct, like an analyst briefing a manager.
- Do not use: leverage, seamless, robust solution, cutting-edge, unlock, delve, empower, revolutionize, harness the power of, game-changer, "in today's fast-paced world".
- No inflated claims. Numbers carry units, period and comparison.
