# VahanValue — Used Car Price Predictor (Pure Python)

College PSDL project. Predicts resale prices for used cars in India using
machine learning. **100% Python** — Streamlit UI, Flask REST backend, SQLite
database, scikit-learn RandomForestRegressor.

## Architecture
```
+-------------------+         +---------------------+
|  Streamlit (UI)   | -- HTTP-> |  Flask backend      |
|  app.py :8081     |         |  backend/app.py:8000|
+-------------------+         |  - RandomForest ML  |
                              |  - SQLite (app.db)  |
                              |  - Auth + History   |
                              +---------------------+
                                       |
                                  cardekho.csv
                                  (15,411 rows)
```

## Files
- `app.py` — Streamlit multi-page UI (Login, Dashboard, Predict, Compare, Analysis, History).
- `backend/app.py` — Flask API (ML model + SQLite persistence).
- `backend/cardekho.csv` — Training dataset (~1.4 MB).
- `backend/app.db` — SQLite database, auto-created on first run (users + predictions).
- `.streamlit/config.toml` — Streamlit server config.

## Project size
Total source code + dataset is **under 2 MB**. The heavy ML libraries
(pandas, scikit-learn, scipy, numpy, plotly, streamlit, flask) live in
`.pythonlibs/` and are installed automatically — they're dependencies, not
project files.

## REST API (Flask, port 8000)
- `GET  /health`               Model metrics + status
- `GET  /options`              Brand/model dropdown lists from dataset
- `GET  /insights`             Aggregated stats (by brand, fuel, age, transmission)
- `POST /predict`              Predict price for a single car
- `POST /similar`              Listings near a target price
- `POST /auth/register`        Create a user (SHA-256 + per-user salt)
- `POST /auth/login`           Authenticate
- `GET  /history?username=X`   Past predictions for a user
- `POST /history`              Save a prediction
- `DELETE /history/<id>?username=X`  Delete one entry
- `POST /history/clear`        Clear all history for a user

## Run locally
Both workflows auto-start under the `Project` parent workflow:
- Flask Backend (`python backend/app.py` on port 8000)
- Streamlit App (`streamlit run app.py --server.port 8081`)

The Streamlit app is the one served on the dev URL root.
