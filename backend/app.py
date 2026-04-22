import os
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("car-price-api")

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "cardekho.csv"

CATEGORICAL_COLS = ["brand", "model", "seller_type", "fuel_type", "transmission_type"]
NUMERIC_COLS = ["vehicle_age", "km_driven", "mileage", "engine", "max_power", "seats"]
TARGET_COL = "selling_price"


def load_dataset() -> pd.DataFrame:
    log.info("Loading dataset from %s", DATA_PATH)
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=[TARGET_COL] + CATEGORICAL_COLS + NUMERIC_COLS).copy()
    for col in CATEGORICAL_COLS:
        df[col] = df[col].astype(str).str.strip()
    log.info("Dataset loaded: %d rows", len(df))
    return df


def build_category_maps(df: pd.DataFrame) -> dict:
    maps = {}
    for col in CATEGORICAL_COLS:
        categories = sorted(df[col].unique().tolist())
        maps[col] = {value: idx for idx, value in enumerate(categories)}
    return maps


def encode_dataframe(df: pd.DataFrame, category_maps: dict) -> pd.DataFrame:
    encoded = df.copy()
    for col, mapping in category_maps.items():
        encoded[col] = encoded[col].map(mapping).astype(int)
    return encoded


def train_model():
    df = load_dataset()
    category_maps = build_category_maps(df)
    encoded = encode_dataframe(df, category_maps)

    feature_cols = CATEGORICAL_COLS + NUMERIC_COLS
    X = encoded[feature_cols].values
    y = encoded[TARGET_COL].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    log.info("Training RandomForestRegressor on %d samples", len(X_train))
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    metrics = {
        "r2": float(r2_score(y_test, preds)),
        "mae": float(mean_absolute_error(y_test, preds)),
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }
    log.info("Model trained. R2=%.4f MAE=%.0f", metrics["r2"], metrics["mae"])

    options = {col: sorted(category_maps[col].keys()) for col in CATEGORICAL_COLS}
    brand_models = (
        df.groupby("brand")["model"]
        .apply(lambda s: sorted(s.unique().tolist()))
        .to_dict()
    )

    return {
        "model": model,
        "category_maps": category_maps,
        "feature_cols": feature_cols,
        "metrics": metrics,
        "options": options,
        "brand_models": brand_models,
        "dataset": df,
    }


STATE = train_model()


def encode_input(payload: dict) -> np.ndarray:
    row = []
    for col in CATEGORICAL_COLS:
        raw = payload.get(col)
        if raw is None:
            raise ValueError(f"Missing field '{col}'")
        mapping = STATE["category_maps"][col]
        value = str(raw).strip()
        if value not in mapping:
            raise ValueError(
                f"Unknown {col} '{value}'. Try one of the supported options."
            )
        row.append(mapping[value])
    for col in NUMERIC_COLS:
        raw = payload.get(col)
        if raw is None or raw == "":
            raise ValueError(f"Missing field '{col}'")
        try:
            row.append(float(raw))
        except (TypeError, ValueError):
            raise ValueError(f"Field '{col}' must be a number")
    return np.array([row])


app = Flask(__name__)
CORS(app)

from flask import Blueprint

api = Blueprint("api", __name__)


@api.get("/")
def index():
    return jsonify(
        {
            "service": "Used Car Price Prediction API",
            "endpoints": ["/health", "/options", "/predict", "/insights", "/similar"],
            "metrics": STATE["metrics"],
        }
    )


@api.get("/health")
def health():
    return jsonify({"status": "ok", "metrics": STATE["metrics"]})


@api.get("/options")
def options():
    return jsonify(
        {
            "options": STATE["options"],
            "brand_models": STATE["brand_models"],
            "numeric_fields": NUMERIC_COLS,
            "categorical_fields": CATEGORICAL_COLS,
        }
    )


@api.get("/insights")
def insights():
    df = STATE["dataset"]
    by_brand = (
        df.groupby("brand")[TARGET_COL]
        .agg(["mean", "count"])
        .sort_values("mean", ascending=False)
    )
    by_fuel = df.groupby("fuel_type")[TARGET_COL].mean().sort_values(ascending=False)
    by_year = (
        df.groupby("vehicle_age")[TARGET_COL]
        .mean()
        .sort_index()
    )
    by_transmission = df.groupby("transmission_type")[TARGET_COL].mean().to_dict()

    most_popular_brand = df["brand"].value_counts().idxmax()

    return jsonify(
        {
            "totals": {
                "rows": int(len(df)),
                "average_price": float(df[TARGET_COL].mean()),
                "median_price": float(df[TARGET_COL].median()),
                "most_popular_brand": str(most_popular_brand),
            },
            "by_brand": [
                {"brand": str(b), "average_price": float(r["mean"]), "count": int(r["count"])}
                for b, r in by_brand.iterrows()
            ],
            "by_fuel": [
                {"fuel_type": str(k), "average_price": float(v)} for k, v in by_fuel.items()
            ],
            "by_age": [
                {"vehicle_age": int(k), "average_price": float(v)} for k, v in by_year.items()
            ],
            "by_transmission": [
                {"transmission_type": str(k), "average_price": float(v)}
                for k, v in by_transmission.items()
            ],
        }
    )


@api.post("/similar")
def similar():
    payload = request.get_json(silent=True) or {}
    target_price = float(payload.get("target_price", 0))
    if target_price <= 0:
        return jsonify({"error": "target_price must be > 0"}), 400
    tolerance = float(payload.get("tolerance", 0.15))
    df = STATE["dataset"]
    low = target_price * (1 - tolerance)
    high = target_price * (1 + tolerance)
    matches = df[(df[TARGET_COL] >= low) & (df[TARGET_COL] <= high)].copy()
    matches["price_diff"] = (matches[TARGET_COL] - target_price).abs()
    matches = matches.sort_values("price_diff").head(10)
    return jsonify(
        {
            "items": [
                {
                    "car_name": str(row["car_name"]),
                    "brand": str(row["brand"]),
                    "model": str(row["model"]),
                    "vehicle_age": int(row["vehicle_age"]),
                    "km_driven": int(row["km_driven"]),
                    "fuel_type": str(row["fuel_type"]),
                    "transmission_type": str(row["transmission_type"]),
                    "selling_price": float(row[TARGET_COL]),
                }
                for _, row in matches.iterrows()
            ]
        }
    )


@api.post("/predict")
def predict():
    payload = request.get_json(silent=True) or {}
    try:
        features = encode_input(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    prediction = float(STATE["model"].predict(features)[0])

    tree_preds = np.array(
        [tree.predict(features)[0] for tree in STATE["model"].estimators_]
    )
    low = float(np.percentile(tree_preds, 10))
    high = float(np.percentile(tree_preds, 90))

    return jsonify(
        {
            "predicted_price": round(prediction, 2),
            "price_range": {"low": round(low, 2), "high": round(high, 2)},
            "currency": "INR",
            "model_metrics": STATE["metrics"],
        }
    )


app.register_blueprint(api, url_prefix="/pyapi")
app.register_blueprint(api, url_prefix="", name="api_root")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
