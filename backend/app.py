import os
import json
import logging
import hashlib
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("car-price-api")

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "cardekho.csv"
DB_PATH = BASE_DIR / "app.db"

CATEGORICAL_COLS = ["brand", "model", "seller_type", "fuel_type", "transmission_type"]
NUMERIC_COLS = ["vehicle_age", "km_driven", "mileage", "engine", "max_power", "seats"]
TARGET_COL = "selling_price"


# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            created_at TEXT NOT NULL,
            car_label TEXT NOT NULL,
            predicted_price REAL NOT NULL,
            price_low REAL,
            price_high REAL,
            inputs_json TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_predictions_user
            ON predictions(username, created_at DESC);
        """
    )
    db.commit()
    db.close()


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# ML model
# --------------------------------------------------------------------------- #

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
init_db()


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


# --------------------------------------------------------------------------- #
# Flask app
# --------------------------------------------------------------------------- #

app = Flask(__name__)
CORS(app)


@app.get("/")
def index():
    return jsonify(
        {
            "service": "Used Car Price Prediction API",
            "endpoints": [
                "/health", "/options", "/predict", "/insights", "/similar",
                "/auth/register", "/auth/login",
                "/history (GET, POST)", "/history/<id> (DELETE)",
                "/history/clear (POST)",
            ],
            "metrics": STATE["metrics"],
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok", "metrics": STATE["metrics"]})


@app.get("/options")
def options():
    return jsonify(
        {
            "options": STATE["options"],
            "brand_models": STATE["brand_models"],
            "numeric_fields": NUMERIC_COLS,
            "categorical_fields": CATEGORICAL_COLS,
        }
    )


@app.get("/insights")
def insights():
    df = STATE["dataset"]
    by_brand = (
        df.groupby("brand")[TARGET_COL]
        .agg(["mean", "count"])
        .sort_values("mean", ascending=False)
    )
    by_fuel = df.groupby("fuel_type")[TARGET_COL].mean().sort_values(ascending=False)
    by_year = df.groupby("vehicle_age")[TARGET_COL].mean().sort_index()
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


@app.post("/similar")
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


@app.post("/predict")
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


# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #

@app.post("/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400

    db = get_db()
    existing = db.execute(
        "SELECT username FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        db.close()
        return jsonify({"error": "Username already taken"}), 409

    salt = secrets.token_hex(16)
    pw_hash = hash_password(password, salt)
    db.execute(
        "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
        (username, pw_hash, salt, datetime.utcnow().isoformat()),
    )
    db.commit()
    db.close()
    return jsonify({"success": True, "username": username})


@app.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    db = get_db()
    row = db.execute(
        "SELECT password_hash, salt FROM users WHERE username = ?", (username,)
    ).fetchone()
    db.close()
    if not row:
        return jsonify({"error": "Invalid username or password"}), 401
    if hash_password(password, row["salt"]) != row["password_hash"]:
        return jsonify({"error": "Invalid username or password"}), 401
    return jsonify({"success": True, "username": username})


# --------------------------------------------------------------------------- #
# History
# --------------------------------------------------------------------------- #

@app.get("/history")
def history_list():
    username = request.args.get("username", "").strip()
    if not username:
        return jsonify({"error": "username query param required"}), 400
    db = get_db()
    rows = db.execute(
        """SELECT id, created_at, car_label, predicted_price, price_low, price_high, inputs_json
           FROM predictions WHERE username = ? ORDER BY created_at DESC""",
        (username,),
    ).fetchall()
    db.close()
    return jsonify(
        {
            "items": [
                {
                    "id": r["id"],
                    "created_at": r["created_at"],
                    "car_label": r["car_label"],
                    "predicted_price": r["predicted_price"],
                    "price_low": r["price_low"],
                    "price_high": r["price_high"],
                    "inputs": json.loads(r["inputs_json"]),
                }
                for r in rows
            ]
        }
    )


@app.post("/history")
def history_save():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    car_label = payload.get("car_label") or ""
    predicted_price = payload.get("predicted_price")
    price_low = payload.get("price_low")
    price_high = payload.get("price_high")
    inputs = payload.get("inputs") or {}
    if not username or not car_label or predicted_price is None:
        return jsonify({"error": "Missing required fields"}), 400
    db = get_db()
    cur = db.execute(
        """INSERT INTO predictions
           (username, created_at, car_label, predicted_price, price_low, price_high, inputs_json)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            username,
            datetime.utcnow().isoformat(),
            car_label,
            float(predicted_price),
            float(price_low) if price_low is not None else None,
            float(price_high) if price_high is not None else None,
            json.dumps(inputs),
        ),
    )
    db.commit()
    new_id = cur.lastrowid
    db.close()
    return jsonify({"success": True, "id": new_id})


@app.delete("/history/<int:entry_id>")
def history_delete(entry_id: int):
    username = request.args.get("username", "").strip()
    if not username:
        return jsonify({"error": "username query param required"}), 400
    db = get_db()
    db.execute(
        "DELETE FROM predictions WHERE id = ? AND username = ?", (entry_id, username)
    )
    db.commit()
    db.close()
    return jsonify({"success": True})


@app.post("/history/clear")
def history_clear():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    if not username:
        return jsonify({"error": "username required"}), 400
    db = get_db()
    db.execute("DELETE FROM predictions WHERE username = ?", (username,))
    db.commit()
    db.close()
    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
