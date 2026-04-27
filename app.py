"""VahanValue - Used Car Price Predictor (Streamlit UI)."""
from __future__ import annotations

import os
from datetime import datetime

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
# API helpers
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


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #

def fmt_inr(value: float | int | None) -> str:
    if value is None:
        return "—"
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
        return "—"
    return f"₹{int(round(float(value))):,}"


# --------------------------------------------------------------------------- #
# Cached data loaders
# --------------------------------------------------------------------------- #

@st.cache_data(ttl=300, show_spinner=False)
def load_options() -> dict:
    return api_get("/options")


@st.cache_data(ttl=300, show_spinner=False)
def load_insights() -> dict:
    return api_get("/insights")


@st.cache_data(ttl=300, show_spinner=False)
def load_health() -> dict:
    return api_get("/health")


# --------------------------------------------------------------------------- #
# Session
# --------------------------------------------------------------------------- #

def init_state() -> None:
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("last_prediction", None)


def require_login() -> bool:
    return st.session_state.get("user") is not None


def logout() -> None:
    for k in ("user", "last_prediction"):
        st.session_state[k] = None
    st.session_state.page = "Dashboard"
    st.rerun()


# --------------------------------------------------------------------------- #
# Auth screen
# --------------------------------------------------------------------------- #

def render_auth() -> None:
    left, mid, right = st.columns([1, 2, 1])
    with mid:
        st.markdown("## VahanValue")
        st.caption("Used car price predictions powered by machine learning.")
        st.write("")

        with st.container(border=True):
            tab_login, tab_register, tab_forgot = st.tabs(
                ["Sign in", "Create account", "Forgot password"]
            )

            with tab_login:
                with st.form("login_form", clear_on_submit=False):
                    u = st.text_input("Username", key="login_user")
                    p = st.text_input("Password", type="password", key="login_pw")
                    submitted = st.form_submit_button(
                        "Sign in", use_container_width=True, type="primary"
                    )
                if submitted:
                    if not u or not p:
                        st.warning("Enter username and password.")
                    else:
                        ok, data = api_post(
                            "/auth/login", {"username": u.strip(), "password": p}
                        )
                        if ok:
                            st.session_state.user = data["username"]
                            st.session_state.page = "Dashboard"
                            st.rerun()
                        else:
                            st.error(data.get("error", "Login failed"))

            with tab_register:
                with st.form("register_form", clear_on_submit=False):
                    u = st.text_input("Choose a username", key="reg_user")
                    p = st.text_input(
                        "Choose a password (4+ characters)",
                        type="password", key="reg_pw",
                    )
                    p2 = st.text_input(
                        "Confirm password", type="password", key="reg_pw2"
                    )
                    submitted = st.form_submit_button(
                        "Create account", use_container_width=True, type="primary"
                    )
                if submitted:
                    if not u or not p:
                        st.warning("Enter username and password.")
                    elif p != p2:
                        st.error("Passwords do not match.")
                    else:
                        ok, data = api_post(
                            "/auth/register",
                            {"username": u.strip(), "password": p},
                        )
                        if ok:
                            st.session_state.user = data["username"]
                            st.session_state.page = "Dashboard"
                            st.rerun()
                        else:
                            st.error(data.get("error", "Registration failed"))

            with tab_forgot:
                st.info(
                    "Password reset is not implemented in this demo. "
                    "Please register a new account if you have forgotten your password."
                )


# --------------------------------------------------------------------------- #
# Sidebar / layout
# --------------------------------------------------------------------------- #

PAGES = ["Dashboard", "Predict", "Compare", "Analysis", "History"]


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### VahanValue")
        st.caption(f"Signed in as **{st.session_state.user}**")
        st.write("")
        for p in PAGES:
            is_active = st.session_state.page == p
            if st.button(
                p,
                use_container_width=True,
                type=("primary" if is_active else "secondary"),
                key=f"nav_{p}",
            ):
                st.session_state.page = p
                st.rerun()
        st.write("")
        st.divider()
        if st.button("Sign out", use_container_width=True):
            logout()
        st.caption("RandomForest model on the CarDekho dataset")


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)
    st.write("")


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #

def render_dashboard() -> None:
    page_header(
        f"Welcome back, {st.session_state.user}",
        "Market overview from the latest CarDekho dataset.",
    )

    try:
        insights = load_insights()
    except Exception as e:
        st.error(f"Could not load market insights: {e}")
        return

    totals = insights["totals"]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.caption("Cars analysed")
            st.subheader(f"{totals['rows']:,}")
    with c2:
        with st.container(border=True):
            st.caption("Average price")
            st.subheader(fmt_inr(totals["average_price"]))
    with c3:
        with st.container(border=True):
            st.caption("Median price")
            st.subheader(fmt_inr(totals["median_price"]))
    with c4:
        with st.container(border=True):
            st.caption("Most popular brand")
            st.subheader(totals["most_popular_brand"])

    st.write("")

    try:
        health = load_health()
        m = health.get("metrics", {})
        with st.container(border=True):
            st.markdown("**Model accuracy**")
            a, b, c, d = st.columns(4)
            a.metric("R² score", f"{m.get('r2', 0):.3f}",
                     help="1.0 is perfect. Above 0.9 is considered very good.")
            b.metric("Mean abs. error", fmt_inr(m.get("mae")),
                     help="Average rupee difference between predicted and actual price.")
            c.metric("Training rows", f"{m.get('training_rows', 0):,}")
            d.metric("Test rows", f"{m.get('test_rows', 0):,}")
            st.caption(
                "The model is evaluated on 20% of the dataset that was never seen during training."
            )
    except Exception:
        pass

    st.write("")
    st.markdown("**Quick actions**")
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("Predict a car price", use_container_width=True, type="primary"):
        st.session_state.page = "Predict"; st.rerun()
    if col2.button("Compare two cars", use_container_width=True):
        st.session_state.page = "Compare"; st.rerun()
    if col3.button("Market analysis", use_container_width=True):
        st.session_state.page = "Analysis"; st.rerun()
    if col4.button("My history", use_container_width=True):
        st.session_state.page = "History"; st.rerun()


# --------------------------------------------------------------------------- #
# Predict
# --------------------------------------------------------------------------- #

def car_form(prefix: str, options: dict) -> dict:
    opts = options["options"]
    brand_models = options["brand_models"]
    col1, col2 = st.columns(2)
    with col1:
        brand = st.selectbox("Brand", opts["brand"], key=f"{prefix}_brand")
        models_for_brand = brand_models.get(brand, []) or ["—"]
        model = st.selectbox("Model", models_for_brand, key=f"{prefix}_model")
        fuel_type = st.selectbox("Fuel type", opts["fuel_type"], key=f"{prefix}_fuel")
        transmission_type = st.selectbox(
            "Transmission", opts["transmission_type"], key=f"{prefix}_trans"
        )
        seller_type = st.selectbox(
            "Seller type", opts["seller_type"], key=f"{prefix}_seller"
        )
    with col2:
        vehicle_age = st.number_input("Vehicle age (years)", 0, 40, 5, key=f"{prefix}_age")
        km_driven = st.number_input(
            "Kilometres driven", 0, 1_000_000, 50_000, step=1000, key=f"{prefix}_km"
        )
        mileage = st.number_input(
            "Mileage (kmpl)", 0.0, 50.0, 18.0, step=0.5, key=f"{prefix}_mileage"
        )
        engine = st.number_input(
            "Engine (cc)", 500, 6000, 1200, step=50, key=f"{prefix}_engine"
        )
        max_power = st.number_input(
            "Max power (bhp)", 20.0, 800.0, 85.0, step=1.0, key=f"{prefix}_bhp"
        )
        seats = st.number_input("Seats", 2, 10, 5, key=f"{prefix}_seats")
    return {
        "brand": brand, "model": model, "fuel_type": fuel_type,
        "transmission_type": transmission_type, "seller_type": seller_type,
        "vehicle_age": int(vehicle_age), "km_driven": int(km_driven),
        "mileage": float(mileage), "engine": float(engine),
        "max_power": float(max_power), "seats": int(seats),
    }


def render_predict() -> None:
    page_header(
        "Predict a car price",
        "Enter the car details to get a market-value estimate.",
    )

    try:
        options = load_options()
    except Exception as e:
        st.error(f"Could not load form options: {e}")
        return

    with st.container(border=True):
        inputs = car_form("p", options)
        st.write("")
        c1, c2, _ = st.columns([1, 1, 4])
        predict_clicked = c1.button("Predict price", type="primary", use_container_width=True)
        if c2.button("Reset", use_container_width=True):
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
        st.write("")
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.metric("Estimated market price", fmt_inr_full(result["predicted_price"]))
            c2.metric("Lower bound", fmt_inr_full(result["price_range"]["low"]))
            c3.metric("Upper bound", fmt_inr_full(result["price_range"]["high"]))
            metrics = result.get("model_metrics", {})
            if metrics:
                st.caption(
                    f"Model R² = {metrics.get('r2', 0):.3f}, "
                    f"average error ≈ {fmt_inr(metrics.get('mae'))}. "
                    "The lower/upper bounds reflect the spread across the 200 trees in the forest."
                )

        st.write("")
        st.markdown("**Similar listings in the dataset**")
        sok, sim = api_post("/similar", {"target_price": result["predicted_price"]})
        if sok and sim.get("items"):
            df = pd.DataFrame(sim["items"]).rename(columns={
                "car_name": "Car", "brand": "Brand", "model": "Model",
                "vehicle_age": "Age (yr)", "km_driven": "Km driven",
                "fuel_type": "Fuel", "transmission_type": "Trans.",
                "selling_price": "Listed price",
            })
            df["Listed price"] = df["Listed price"].apply(fmt_inr_full)
            st.dataframe(df, hide_index=True, use_container_width=True)
            st.caption(
                "These real listings were sold near the predicted price — "
                "a reality check for how close the estimate is."
            )
        else:
            st.info("No similar listings found in the dataset.")


# --------------------------------------------------------------------------- #
# Compare
# --------------------------------------------------------------------------- #

def render_compare() -> None:
    page_header(
        "Compare two cars",
        "Fill in details for both cars to see the predicted prices side by side.",
    )
    try:
        options = load_options()
    except Exception as e:
        st.error(f"Could not load form options: {e}")
        return

    colA, colB = st.columns(2)
    with colA:
        with st.container(border=True):
            st.markdown("**Car A**")
            a = car_form("a", options)
    with colB:
        with st.container(border=True):
            st.markdown("**Car B**")
            b = car_form("b", options)

    if st.button("Compare", type="primary"):
        ok_a, res_a = api_post("/predict", a)
        ok_b, res_b = api_post("/predict", b)
        if not ok_a or not ok_b:
            st.error("Could not get predictions for both cars.")
            return

        st.write("")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            c1.metric(
                f"{a['brand']} {a['model']}", fmt_inr_full(res_a["predicted_price"])
            )
            c2.metric(
                f"{b['brand']} {b['model']}", fmt_inr_full(res_b["predicted_price"])
            )
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
            ("Predicted price",
             fmt_inr_full(res_a["predicted_price"]),
             fmt_inr_full(res_b["predicted_price"])),
            ("Lower bound",
             fmt_inr_full(res_a["price_range"]["low"]),
             fmt_inr_full(res_b["price_range"]["low"])),
            ("Upper bound",
             fmt_inr_full(res_a["price_range"]["high"]),
             fmt_inr_full(res_b["price_range"]["high"])),
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


# --------------------------------------------------------------------------- #
# Analysis
# --------------------------------------------------------------------------- #

def render_analysis() -> None:
    page_header(
        "Market analysis",
        "Aggregated insights drawn from the entire CarDekho dataset.",
    )
    try:
        ins = load_insights()
    except Exception as e:
        st.error(f"Could not load insights: {e}")
        return

    by_brand = pd.DataFrame(ins["by_brand"])
    by_fuel = pd.DataFrame(ins["by_fuel"])
    by_age = pd.DataFrame(ins["by_age"])
    by_trans = pd.DataFrame(ins["by_transmission"])

    brand_filter = st.multiselect(
        "Filter brands (leave empty to view top 10)",
        sorted(by_brand["brand"].tolist()),
        default=[],
    )
    bb = (by_brand[by_brand["brand"].isin(brand_filter)]
          if brand_filter else by_brand.head(10))

    chart_layout = dict(
        height=360, margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(color="#0F172A"),
    )

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("**Average price by brand**")
            fig = px.bar(
                bb, x="brand", y="average_price",
                labels={"brand": "Brand", "average_price": "Avg price (INR)"},
                color_discrete_sequence=["#0F766E"],
            )
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        with st.container(border=True):
            st.markdown("**Average price by fuel type**")
            fig = px.bar(
                by_fuel, x="fuel_type", y="average_price",
                labels={"fuel_type": "Fuel", "average_price": "Avg price (INR)"},
                color_discrete_sequence=["#0F766E"],
            )
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        with st.container(border=True):
            st.markdown("**Depreciation by vehicle age**")
            fig = px.line(
                by_age.sort_values("vehicle_age"),
                x="vehicle_age", y="average_price",
                labels={"vehicle_age": "Age (years)", "average_price": "Avg price (INR)"},
                markers=True, color_discrete_sequence=["#0F766E"],
            )
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)
    with c4:
        with st.container(border=True):
            st.markdown("**Average price by transmission**")
            fig = px.bar(
                by_trans, x="transmission_type", y="average_price",
                labels={"transmission_type": "Transmission",
                        "average_price": "Avg price (INR)"},
                color_discrete_sequence=["#0F766E"],
            )
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)

    st.write("")
    with st.container(border=True):
        st.markdown("**All brands**")
        table = by_brand.assign(
            average_price=by_brand["average_price"].apply(fmt_inr_full)
        ).rename(columns={
            "brand": "Brand", "average_price": "Avg price", "count": "Listings"
        })
        st.dataframe(table, hide_index=True, use_container_width=True)


# --------------------------------------------------------------------------- #
# History
# --------------------------------------------------------------------------- #

def render_history() -> None:
    page_header(
        "Prediction history",
        "Every prediction you've made, stored in the database.",
    )

    try:
        data = api_get("/history", params={"username": st.session_state.user})
    except Exception as e:
        st.error(f"Could not load history: {e}")
        return

    items = data.get("items", [])
    if not items:
        st.info("You haven't saved any predictions yet. Try the Predict page.")
        return

    c1, _ = st.columns([1, 5])
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
            top[1].metric(
                "Predicted", fmt_inr_full(it["predicted_price"]),
                label_visibility="collapsed",
            )
            range_text = f"{fmt_inr(it['price_low'])} – {fmt_inr(it['price_high'])}"
            top[2].markdown(f"Range\n\n{range_text}")
            if top[3].button("Delete", key=f"del_{it['id']}"):
                api_delete(
                    f"/history/{it['id']}",
                    params={"username": st.session_state.user},
                )
                st.rerun()
            with st.expander("View inputs"):
                st.json(it["inputs"], expanded=False)


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
