"""VahanValue - Used Car Price Predictor (Streamlit UI)."""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="VahanValue - Used Car Price Predictor",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def api_get(path: str, params: dict | None = None) -> dict:
    r = requests.get(f"{API_BASE}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def api_post(path: str, payload: dict) -> tuple[bool, dict]:
    r = requests.post(f"{API_BASE}{path}", json=payload, timeout=30)
    try:
        data = r.json()
    except Exception:
        data = {"error": r.text or "Unknown error"}
    return r.ok, data


def api_delete(path: str, params: dict | None = None) -> bool:
    r = requests.delete(f"{API_BASE}{path}", params=params, timeout=30)
    return r.ok


def fmt_inr(value: float | int | None) -> str:
    if value is None:
        return "-"
    value = float(value)
    if value >= 10_000_000:
        return f"₹{value / 10_000_000:.2f} Cr"
    if value >= 100_000:
        return f"₹{value / 100_000:.2f} L"
    if value >= 1_000:
        return f"₹{value / 1_000:.1f}K"
    return f"₹{value:,.0f}"


def fmt_inr_full(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"₹{int(round(float(value))):,}"


@st.cache_data(ttl=300, show_spinner=False)
def load_options() -> dict:
    return api_get("/options")


@st.cache_data(ttl=300, show_spinner=False)
def load_insights() -> dict:
    return api_get("/insights")


def init_state() -> None:
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("last_prediction", None)


def require_login() -> bool:
    return st.session_state.get("user") is not None


def logout() -> None:
    st.session_state.user = None
    st.session_state.page = "Dashboard"
    st.session_state.last_prediction = None
    st.rerun()


# --------------------------------------------------------------------------- #
# Auth screen
# --------------------------------------------------------------------------- #

def render_auth() -> None:
    st.markdown(
        """
        <div style="text-align:center;padding:2rem 0 1rem;">
            <div style="font-size:3rem;">🚗</div>
            <h1 style="margin:.25rem 0;">VahanValue</h1>
            <p style="color:#64748b;margin:0;">Predict used car prices with machine learning</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, mid, right = st.columns([1, 2, 1])
    with mid:
        tab_login, tab_register, tab_forgot = st.tabs(["Login", "Register", "Forgot Password"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input("Username", key="login_user")
                p = st.text_input("Password", type="password", key="login_pw")
                submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
            if submitted:
                if not u or not p:
                    st.warning("Enter username and password.")
                else:
                    ok, data = api_post("/auth/login", {"username": u.strip(), "password": p})
                    if ok:
                        st.session_state.user = data["username"]
                        st.session_state.page = "Dashboard"
                        st.success(f"Welcome back, {data['username']}!")
                        st.rerun()
                    else:
                        st.error(data.get("error", "Login failed"))

        with tab_register:
            with st.form("register_form", clear_on_submit=False):
                u = st.text_input("Choose a username", key="reg_user")
                p = st.text_input("Choose a password (4+ chars)", type="password", key="reg_pw")
                p2 = st.text_input("Confirm password", type="password", key="reg_pw2")
                submitted = st.form_submit_button("Create account", use_container_width=True, type="primary")
            if submitted:
                if not u or not p:
                    st.warning("Enter username and password.")
                elif p != p2:
                    st.error("Passwords do not match.")
                else:
                    ok, data = api_post("/auth/register", {"username": u.strip(), "password": p})
                    if ok:
                        st.session_state.user = data["username"]
                        st.session_state.page = "Dashboard"
                        st.success(f"Account created. Welcome, {data['username']}!")
                        st.rerun()
                    else:
                        st.error(data.get("error", "Registration failed"))

        with tab_forgot:
            st.info(
                "This is a demo project. Password reset is not implemented — "
                "please register a new account if you forgot your password."
            )


# --------------------------------------------------------------------------- #
# Layout
# --------------------------------------------------------------------------- #

PAGES = ["Dashboard", "Predict", "Compare", "Analysis", "History"]


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🚗 VahanValue")
        st.caption(f"Signed in as **{st.session_state.user}**")
        st.divider()
        for p in PAGES:
            if st.button(p, use_container_width=True,
                         type=("primary" if st.session_state.page == p else "secondary"),
                         key=f"nav_{p}"):
                st.session_state.page = p
                st.rerun()
        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()
        st.caption("Powered by RandomForest + CarDekho dataset")


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #

def render_dashboard() -> None:
    st.title("Dashboard")
    st.write(f"Welcome back, **{st.session_state.user}**.")

    try:
        insights = load_insights()
    except Exception as e:
        st.error(f"Could not load market insights: {e}")
        return

    totals = insights["totals"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cars in dataset", f"{totals['rows']:,}")
    c2.metric("Average price", fmt_inr(totals["average_price"]))
    c3.metric("Median price", fmt_inr(totals["median_price"]))
    c4.metric("Most popular brand", totals["most_popular_brand"])

    st.divider()

    try:
        health = api_get("/health")
        m = health.get("metrics", {})
        st.markdown("#### Model performance")
        a, b, c = st.columns(3)
        a.metric("R² score", f"{m.get('r2', 0):.3f}")
        b.metric("Mean abs error", fmt_inr(m.get("mae")))
        c.metric("Training rows", f"{m.get('training_rows', 0):,}")
    except Exception:
        pass

    st.divider()
    st.markdown("#### Quick actions")
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("Predict a car price", use_container_width=True, type="primary"):
        st.session_state.page = "Predict"; st.rerun()
    if col2.button("Compare two cars", use_container_width=True):
        st.session_state.page = "Compare"; st.rerun()
    if col3.button("Market analysis", use_container_width=True):
        st.session_state.page = "Analysis"; st.rerun()
    if col4.button("My history", use_container_width=True):
        st.session_state.page = "History"; st.rerun()


def car_form(prefix: str, options: dict) -> dict:
    opts = options["options"]
    brand_models = options["brand_models"]
    col1, col2 = st.columns(2)
    with col1:
        brand = st.selectbox("Brand", opts["brand"], key=f"{prefix}_brand")
        models_for_brand = brand_models.get(brand, [])
        model_default_index = 0 if models_for_brand else 0
        model = st.selectbox("Model", models_for_brand or ["-"], key=f"{prefix}_model",
                             index=model_default_index)
        fuel_type = st.selectbox("Fuel type", opts["fuel_type"], key=f"{prefix}_fuel")
        transmission_type = st.selectbox("Transmission", opts["transmission_type"], key=f"{prefix}_trans")
        seller_type = st.selectbox("Seller type", opts["seller_type"], key=f"{prefix}_seller")
    with col2:
        vehicle_age = st.number_input("Vehicle age (years)", 0, 40, 5, key=f"{prefix}_age")
        km_driven = st.number_input("Km driven", 0, 1_000_000, 50_000, step=1000, key=f"{prefix}_km")
        mileage = st.number_input("Mileage (kmpl)", 0.0, 50.0, 18.0, step=0.5, key=f"{prefix}_mileage")
        engine = st.number_input("Engine (cc)", 500, 6000, 1200, step=50, key=f"{prefix}_engine")
        max_power = st.number_input("Max power (bhp)", 20.0, 800.0, 85.0, step=1.0, key=f"{prefix}_bhp")
        seats = st.number_input("Seats", 2, 10, 5, key=f"{prefix}_seats")
    return {
        "brand": brand, "model": model, "fuel_type": fuel_type,
        "transmission_type": transmission_type, "seller_type": seller_type,
        "vehicle_age": int(vehicle_age), "km_driven": int(km_driven),
        "mileage": float(mileage), "engine": float(engine),
        "max_power": float(max_power), "seats": int(seats),
    }


def render_predict() -> None:
    st.title("Predict a car price")
    st.caption("Enter the car details below to get a market-value estimate.")

    try:
        options = load_options()
    except Exception as e:
        st.error(f"Could not load form options: {e}")
        return

    inputs = car_form("p", options)

    c1, c2 = st.columns([1, 5])
    predict_clicked = c1.button("Predict price", type="primary")
    if c2.button("Reset"):
        for k in list(st.session_state.keys()):
            if k.startswith("p_"):
                del st.session_state[k]
        st.session_state.last_prediction = None
        st.rerun()

    if predict_clicked:
        ok, data = api_post("/predict", inputs)
        if not ok:
            st.error(data.get("error", "Prediction failed"))
            return
        st.session_state.last_prediction = {"inputs": inputs, "result": data}
        # Save to DB
        car_label = f"{inputs['brand']} {inputs['model']} ({inputs['vehicle_age']}y)"
        api_post("/history", {
            "username": st.session_state.user,
            "car_label": car_label,
            "predicted_price": data["predicted_price"],
            "price_low": data["price_range"]["low"],
            "price_high": data["price_range"]["high"],
            "inputs": inputs,
        })

    pred = st.session_state.get("last_prediction")
    if pred:
        result = pred["result"]
        st.divider()
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.metric("Estimated market price", fmt_inr_full(result["predicted_price"]))
        c2.metric("Lower bound", fmt_inr_full(result["price_range"]["low"]))
        c3.metric("Upper bound", fmt_inr_full(result["price_range"]["high"]))

        st.markdown("#### Similar listings in the dataset")
        sok, sim = api_post("/similar", {"target_price": result["predicted_price"]})
        if sok and sim.get("items"):
            df = pd.DataFrame(sim["items"])
            df = df.rename(columns={
                "car_name": "Car", "brand": "Brand", "model": "Model",
                "vehicle_age": "Age (yr)", "km_driven": "Km driven",
                "fuel_type": "Fuel", "transmission_type": "Trans.",
                "selling_price": "Listed price",
            })
            df["Listed price"] = df["Listed price"].apply(fmt_inr_full)
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info("No similar listings found in the dataset.")


def render_compare() -> None:
    st.title("Compare two cars")
    st.caption("Fill in details for both cars, then compare their estimated prices side-by-side.")
    try:
        options = load_options()
    except Exception as e:
        st.error(f"Could not load form options: {e}")
        return

    colA, colB = st.columns(2)
    with colA:
        st.markdown("### Car A")
        a = car_form("a", options)
    with colB:
        st.markdown("### Car B")
        b = car_form("b", options)

    if st.button("Compare", type="primary"):
        ok_a, res_a = api_post("/predict", a)
        ok_b, res_b = api_post("/predict", b)
        if not ok_a or not ok_b:
            st.error("Could not get predictions for both cars.")
            return

        st.divider()
        c1, c2 = st.columns(2)
        c1.metric(f"{a['brand']} {a['model']}", fmt_inr_full(res_a["predicted_price"]))
        c2.metric(f"{b['brand']} {b['model']}", fmt_inr_full(res_b["predicted_price"]))

        diff = res_a["predicted_price"] - res_b["predicted_price"]
        if abs(diff) < 1:
            st.info("Both cars have essentially the same predicted value.")
        elif diff < 0:
            st.success(
                f"Car A is **{fmt_inr_full(abs(diff))}** cheaper than Car B "
                f"({abs(diff) / res_b['predicted_price'] * 100:.1f}% less)."
            )
        else:
            st.success(
                f"Car B is **{fmt_inr_full(abs(diff))}** cheaper than Car A "
                f"({abs(diff) / res_a['predicted_price'] * 100:.1f}% less)."
            )

        rows = [
            ("Predicted price", fmt_inr_full(res_a["predicted_price"]), fmt_inr_full(res_b["predicted_price"])),
            ("Price range low", fmt_inr_full(res_a["price_range"]["low"]), fmt_inr_full(res_b["price_range"]["low"])),
            ("Price range high", fmt_inr_full(res_a["price_range"]["high"]), fmt_inr_full(res_b["price_range"]["high"])),
            ("Brand", a["brand"], b["brand"]),
            ("Model", a["model"], b["model"]),
            ("Fuel", a["fuel_type"], b["fuel_type"]),
            ("Transmission", a["transmission_type"], b["transmission_type"]),
            ("Vehicle age", f"{a['vehicle_age']} yr", f"{b['vehicle_age']} yr"),
            ("Km driven", f"{a['km_driven']:,}", f"{b['km_driven']:,}"),
            ("Mileage", f"{a['mileage']} kmpl", f"{b['mileage']} kmpl"),
            ("Engine", f"{a['engine']} cc", f"{b['engine']} cc"),
            ("Max power", f"{a['max_power']} bhp", f"{b['max_power']} bhp"),
            ("Seats", a["seats"], b["seats"]),
        ]
        st.dataframe(
            pd.DataFrame(rows, columns=["Field", "Car A", "Car B"]),
            hide_index=True, use_container_width=True,
        )


def render_analysis() -> None:
    st.title("Market analysis")
    st.caption("Aggregated insights from the CarDekho dataset.")
    try:
        ins = load_insights()
    except Exception as e:
        st.error(f"Could not load insights: {e}")
        return

    by_brand = pd.DataFrame(ins["by_brand"])
    by_fuel = pd.DataFrame(ins["by_fuel"])
    by_age = pd.DataFrame(ins["by_age"])
    by_trans = pd.DataFrame(ins["by_transmission"])

    # filter
    brand_filter = st.multiselect(
        "Filter brands (optional)",
        sorted(by_brand["brand"].tolist()),
        default=[],
        help="Leave empty to view top 10 brands by average price.",
    )
    if brand_filter:
        bb = by_brand[by_brand["brand"].isin(brand_filter)]
    else:
        bb = by_brand.head(10)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Average price by brand")
        fig = px.bar(bb, x="brand", y="average_price",
                     labels={"brand": "Brand", "average_price": "Avg price (INR)"},
                     color="average_price", color_continuous_scale="Tealgrn")
        fig.update_layout(showlegend=False, height=380, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Average price by fuel type")
        fig = px.bar(by_fuel, x="fuel_type", y="average_price",
                     labels={"fuel_type": "Fuel", "average_price": "Avg price (INR)"},
                     color="fuel_type")
        fig.update_layout(showlegend=False, height=380, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Depreciation by vehicle age")
        fig = px.line(by_age.sort_values("vehicle_age"),
                      x="vehicle_age", y="average_price",
                      labels={"vehicle_age": "Age (years)", "average_price": "Avg price (INR)"},
                      markers=True)
        fig.update_layout(height=380, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        st.subheader("Average price by transmission")
        fig = px.bar(by_trans, x="transmission_type", y="average_price",
                     labels={"transmission_type": "Transmission", "average_price": "Avg price (INR)"},
                     color="transmission_type")
        fig.update_layout(showlegend=False, height=380, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Top brands table")
    st.dataframe(
        by_brand.assign(average_price=by_brand["average_price"].apply(fmt_inr_full)),
        hide_index=True, use_container_width=True,
    )


def render_history() -> None:
    st.title("Prediction history")
    st.caption("All your past price predictions, saved in the database.")

    try:
        data = api_get("/history", params={"username": st.session_state.user})
    except Exception as e:
        st.error(f"Could not load history: {e}")
        return

    items = data.get("items", [])
    if not items:
        st.info("You haven't saved any predictions yet. Try the Predict page.")
        return

    c1, c2 = st.columns([1, 5])
    if c1.button("Clear all", type="secondary"):
        api_post("/history/clear", {"username": st.session_state.user})
        st.rerun()

    for it in items:
        with st.container(border=True):
            top = st.columns([3, 2, 2, 1])
            top[0].markdown(f"**{it['car_label']}**")
            ts = it["created_at"]
            try:
                ts = datetime.fromisoformat(ts).strftime("%d %b %Y, %H:%M")
            except Exception:
                pass
            top[0].caption(ts)
            top[1].metric("Predicted", fmt_inr_full(it["predicted_price"]),
                          label_visibility="collapsed")
            range_text = f"{fmt_inr(it['price_low'])} – {fmt_inr(it['price_high'])}"
            top[2].markdown(f"Range\n\n{range_text}")
            if top[3].button("Delete", key=f"del_{it['id']}"):
                api_delete(f"/history/{it['id']}",
                           params={"username": st.session_state.user})
                st.rerun()
            with st.expander("View inputs"):
                inp = it["inputs"]
                st.json(inp, expanded=False)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    init_state()
    if not require_login():
        render_auth()
        return

    render_sidebar()

    page = st.session_state.page
    if page == "Dashboard":
        render_dashboard()
    elif page == "Predict":
        render_predict()
    elif page == "Compare":
        render_compare()
    elif page == "Analysis":
        render_analysis()
    elif page == "History":
        render_history()


if __name__ == "__main__":
    main()
