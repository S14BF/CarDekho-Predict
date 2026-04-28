"""Theme and visual helper components for Streamlit."""

from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """Apply premium AutoVision AI visual system."""
    dark_mode = bool(st.session_state.get("dark_mode", False))

    if dark_mode:
        bg_start, bg_end = "#0B1220", "#111827"
        card_bg, border, text = "#111827dd", "#1f2937", "#f9fafb"
        sidebar_bg, sidebar_border, sidebar_text = "#0f172a", "#1f2937", "#f9fafb"
    else:
        bg_start, bg_end = "#F9FAFB", "#EEF2FF"
        card_bg, border, text = "#ffffffdd", "#e5e7eb", "#111827"
        sidebar_bg, sidebar_border, sidebar_text = "#ffffff", "#e5e7eb", "#111827"

    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            :root {{
                --vv-primary: #2563EB;
                --vv-secondary: #7C3AED;
                --vv-dark: #111827;
                --vv-light: #F9FAFB;
                --vv-accent: #10B981;
                --vv-bg-start: {bg_start};
                --vv-bg-end: {bg_end};
                --vv-card: {card_bg};
                --vv-border: {border};
                --vv-text: {text};
            }}

            html, body, [class*="css"], .stApp {{
                font-family: 'Inter', sans-serif !important;
            }}

            .stApp {{
                background: linear-gradient(135deg, var(--vv-bg-start) 0%, var(--vv-bg-end) 100%);
                color: var(--vv-text);
            }}

            [data-testid="stHeader"] {{
                background: transparent !important;
            }}

            section[data-testid="stSidebar"] {{
                background: {sidebar_bg};
                border-right: 1px solid {sidebar_border};
            }}

            section[data-testid="stSidebar"] * {{
                color: {sidebar_text} !important;
            }}

            .vv-topbar {{
                position: sticky;
                top: 0.5rem;
                z-index: 100;
                background: rgba(255, 255, 255, 0.86);
                backdrop-filter: blur(10px);
                border: 1px solid #e5e7eb;
                border-radius: 20px;
                min-height: 80px;
                display: flex;
                align-items: center;
                padding: 0.65rem 1.1rem;
                margin-bottom: 1rem;
                box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
                transition: all 0.3s ease;
            }}

            .vv-topbar-row {{
                display: flex;
                width: 100%;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                flex-wrap: wrap;
            }}

            .vv-brand-wrap {{
                display: flex;
                align-items: center;
                gap: 0.65rem;
            }}

            .vv-brand-icon {{
                width: 40px;
                height: 40px;
                border-radius: 999px;
                background: linear-gradient(135deg, var(--vv-primary), var(--vv-secondary));
                color: #fff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.15rem;
                font-weight: 700;
            }}

            .vv-brand {{
                color: var(--vv-dark);
                font-size: 1.22rem;
                font-weight: 800;
                letter-spacing: 0.15px;
            }}

            .vv-menu {{
                display: flex;
                gap: 1rem;
                flex-wrap: wrap;
                color: #374151;
                font-weight: 600;
                font-size: 0.92rem;
            }}

            .vv-menu span {{
                position: relative;
                cursor: default;
                transition: color 0.2s ease;
            }}

            .vv-menu span::after {{
                content: "";
                position: absolute;
                left: 0;
                bottom: -3px;
                width: 0%;
                height: 2px;
                background: linear-gradient(135deg, var(--vv-primary), var(--vv-secondary));
                transition: width 0.25s ease;
            }}

            .vv-menu span:hover::after {{
                width: 100%;
            }}

            .vv-top-actions {{
                display: flex;
                align-items: center;
                gap: 0.55rem;
            }}

            .vv-chip {{
                border: 1px solid #e5e7eb;
                border-radius: 999px;
                padding: 0.32rem 0.62rem;
                font-size: 0.86rem;
                background: #fff;
                color: #374151;
            }}

            .vv-chip.cta {{
                background: linear-gradient(135deg, var(--vv-primary), var(--vv-secondary));
                color: #fff;
                border: none;
                box-shadow: 0 6px 16px rgba(124, 58, 237, 0.25);
            }}

            .vv-hero {{
                border-radius: 24px;
                overflow: hidden;
                margin-bottom: 1rem;
                background-image:
                    linear-gradient(95deg, rgba(17, 24, 39, 0.85) 0%, rgba(37, 99, 235, 0.66) 50%, rgba(124, 58, 237, 0.5) 100%),
                    url("https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1600&q=80");
                background-size: cover;
                background-position: center;
                min-height: 360px;
                box-shadow: 0 24px 40px rgba(15, 23, 42, 0.2);
                animation: vvFadeIn 0.6s ease;
            }}

            .vv-hero-grid {{
                display: grid;
                grid-template-columns: 1.1fr 1fr;
                gap: 1rem;
                padding: 1.8rem;
                min-height: 360px;
            }}

            .vv-hero-copy {{
                color: #ffffff;
                align-self: center;
            }}

            .vv-hero-copy h1 {{
                margin: 0;
                font-size: clamp(2rem, 4vw, 3.5rem);
                line-height: 1.08;
                font-weight: 800;
                max-width: 700px;
            }}

            .vv-hero-copy p {{
                margin-top: 0.85rem;
                max-width: 700px;
                color: #e5e7eb;
                font-size: 1rem;
                line-height: 1.5;
            }}

            .vv-hero-cta {{
                margin-top: 1rem;
                display: flex;
                gap: 0.65rem;
                flex-wrap: wrap;
            }}

            .vv-hero-btn {{
                border-radius: 999px;
                padding: 0.52rem 1rem;
                font-weight: 600;
                font-size: 0.88rem;
            }}

            .vv-hero-btn.primary {{
                background: linear-gradient(135deg, var(--vv-primary), var(--vv-secondary));
                color: #fff;
            }}

            .vv-hero-btn.secondary {{
                border: 1px solid #d1d5db;
                color: #fff;
                background: rgba(255, 255, 255, 0.08);
            }}

            .vv-upload-card {{
                background: rgba(255, 255, 255, 0.92);
                border-radius: 24px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 14px 28px rgba(17, 24, 39, 0.16);
                padding: 1.2rem;
            }}

            .vv-upload-card h4 {{
                margin: 0 0 0.4rem 0;
                font-size: 1.2rem;
                color: #111827;
            }}

            .vv-upload-placeholder {{
                border: 2px dashed #c7d2fe;
                border-radius: 16px;
                background: #eef2ff;
                padding: 0.65rem;
                color: #3730a3;
                font-size: 0.85rem;
                text-align: center;
                margin-bottom: 0.45rem;
            }}

            .vv-header {{
                background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
                border-radius: 20px;
                color: #ffffff;
                padding: 1.05rem 1.2rem;
                margin-bottom: 0.7rem;
                box-shadow: 0 12px 26px rgba(37, 99, 235, 0.24);
                animation: vvFadeIn 0.45s ease;
            }}

            .vv-header h2 {{
                margin: 0;
                font-size: clamp(1.4rem, 2.3vw, 2rem);
                font-weight: 800;
                letter-spacing: 0.1px;
            }}

            .vv-header p {{
                margin: 0.35rem 0 0 0;
                opacity: 0.95;
                font-size: 0.96rem;
            }}

            .vv-auth-card {{
                background: linear-gradient(180deg, #dbeafe 0%, #bfdbfe 100%);
                border: 1px solid #93c5fd;
                border-radius: 22px;
                box-shadow: 0 16px 32px rgba(37, 99, 235, 0.2);
                padding: 0.8rem 0.9rem 0.6rem 0.9rem;
            }}

            .vv-auth-wrap {{
                max-width: 100%;
                margin: 0 auto;
            }}

            .vv-auth-card h3 {{
                font-size: 2rem;
                font-weight: 800;
                color: #1e3a8a;
                margin-bottom: 0.25rem;
            }}

            .vv-auth-card [data-baseweb="tab-list"] button {{
                font-size: 1rem !important;
                font-weight: 700 !important;
            }}

            .vv-auth-card label {{
                font-size: 1.02rem !important;
                font-weight: 600 !important;
                color: #1f2937 !important;
            }}

            div[data-testid="stForm"],
            div[data-testid="stExpander"],
            div[data-testid="stDataFrame"] {{
                border-radius: 20px !important;
            }}

            div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stMetric"]) {{
                background: var(--vv-card);
                border: 1px solid var(--vv-border);
                border-radius: 20px;
                padding: 0.35rem 0.7rem;
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                animation: vvFadeIn 0.55s ease;
            }}

            div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stMetric"]):hover {{
                transform: translateY(-2px);
                box-shadow: 0 14px 24px rgba(15, 23, 42, 0.11);
            }}

            div[data-testid="stButton"] > button {{
                border-radius: 999px !important;
                min-height: 44px;
                font-weight: 600;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}

            div[data-testid="stButton"] > button:hover {{
                transform: scale(1.015);
            }}

            div[data-testid="stButton"] > button[kind="primary"] {{
                background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
                border: none !important;
                color: #ffffff !important;
                box-shadow: 0 10px 20px rgba(37, 99, 235, 0.30) !important;
            }}

            /* Force Streamlit submit/login buttons to stay blue */
            button[data-testid="baseButton-primary"] {{
                background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
                border: none !important;
                color: #ffffff !important;
                box-shadow: 0 10px 20px rgba(37, 99, 235, 0.30) !important;
            }}

            button[data-testid="baseButton-primary"]:hover {{
                background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
            }}

            div[data-testid="stButton"] > button[kind="secondary"] {{
                border: 1px solid #cbd5e1 !important;
                background: #ffffff !important;
                color: #1f2937 !important;
            }}

            div[data-baseweb="input"] > div,
            div[data-baseweb="select"] > div {{
                border-radius: 14px !important;
                min-height: 58px !important;
                border: 1px solid #93c5fd !important;
                box-shadow: none !important;
                background: #ffffff !important;
            }}

            div[data-baseweb="input"] > div:focus-within,
            div[data-baseweb="select"] > div:focus-within {{
                border-color: #2563eb !important;
                box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.18) !important;
            }}

            input {{
                font-size: 1.02rem !important;
            }}

            .vv-footer {{
                margin-top: 1.2rem;
                border-radius: 22px;
                background: #111827;
                color: #f9fafb;
                padding: 1.2rem 1.3rem;
                box-shadow: 0 16px 34px rgba(15, 23, 42, 0.2);
            }}

            .vv-footer-grid {{
                display: grid;
                grid-template-columns: repeat(4, minmax(120px, 1fr));
                gap: 0.8rem;
            }}

            .vv-footer h5 {{
                margin: 0 0 0.4rem 0;
                font-size: 0.95rem;
                color: #f3f4f6;
            }}

            .vv-footer p {{
                margin: 0.2rem 0;
                color: #cbd5e1;
                font-size: 0.84rem;
            }}

            .vv-firstpage {{
                background: #ffffff;
                border-radius: 24px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
                padding: 1.4rem 1.5rem 1.2rem 1.5rem;
                margin-bottom: 1rem;
                animation: vvFadeIn 0.5s ease;
            }}

            .vv-firstpage-head {{
                text-align: center;
                max-width: 920px;
                margin: 0 auto 1rem auto;
            }}

            .vv-firstpage-head h1 {{
                margin: 0;
                font-size: clamp(2rem, 5vw, 3.3rem);
                line-height: 1.1;
                color: #111827;
                font-weight: 800;
            }}

            .vv-firstpage-head p {{
                margin: 0.65rem auto 0 auto;
                color: #4b5563;
                max-width: 760px;
                font-size: 1rem;
            }}

            .vv-firstpage-cta {{
                margin-top: 0.85rem;
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                padding: 0.58rem 1.05rem;
                border-radius: 999px;
                background: linear-gradient(135deg, #06b6d4, #2563eb);
                color: #ffffff;
                font-weight: 600;
                font-size: 0.9rem;
                box-shadow: 0 10px 18px rgba(14, 116, 144, 0.2);
            }}

            .vv-floating-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 0.75rem;
                align-items: end;
            }}

            .vv-float-card {{
                background: #f8fafc;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 10px 22px rgba(15, 23, 42, 0.08);
                overflow: hidden;
            }}

            .vv-float-card img {{
                width: 100%;
                height: 170px;
                object-fit: cover;
                display: block;
            }}

            .vv-brand-grid {{
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.7rem;
                margin-top: 0.35rem;
            }}

            .vv-brand-item {{
                background: #ffffff;
                border: 1px solid #dbeafe;
                border-radius: 14px;
                height: 112px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                box-shadow: 0 8px 18px rgba(37, 99, 235, 0.08);
                padding: 0.4rem;
            }}

            .vv-brand-item img {{
                width: 64px;
                height: 40px;
                object-fit: contain;
                margin-bottom: 0.2rem;
            }}

            .vv-brand-item span {{
                font-size: 0.78rem;
                font-weight: 600;
                color: #1e3a8a;
            }}

            @keyframes vvFadeIn {{
                from {{ opacity: 0; transform: translateY(4px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            @media (max-width: 900px) {{
                .vv-topbar {{
                    min-height: 64px;
                    border-radius: 14px;
                    top: 0.25rem;
                }}
                .vv-menu {{
                    display: none;
                }}
                .vv-hero-grid {{
                    grid-template-columns: 1fr;
                    padding: 1.1rem;
                }}
                .vv-footer-grid {{
                    grid-template-columns: 1fr 1fr;
                }}
                .vv-floating-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero_header(title: str, subtitle: str = "") -> None:
    """Render a consistent page title section."""
    st.markdown(
        f"""
        <div class="vv-header">
            <h2>{title}</h2>
            {"<p>" + subtitle + "</p>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_nav() -> None:
    """Render premium sticky navbar."""
    st.markdown(
        """
        <div class="vv-topbar">
            <div class="vv-topbar-row">
                <div class="vv-brand-wrap">
                    <div class="vv-brand-icon">🚘</div>
                    <div class="vv-brand">AutoVision AI</div>
                </div>
                <div class="vv-menu">
                    <span>Home</span>
                    <span>Analyze Car</span>
                    <span>Compare Cars</span>
                    <span>Reports</span>
                    <span>Saved</span>
                    <span>About</span>
                </div>
                <div class="vv-top-actions">
                    <span class="vv-chip">🔍</span>
                    <span class="vv-chip">🔔</span>
                    <span class="vv-chip">👤</span>
                    <span class="vv-chip cta">Login / Signup</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_landing_hero() -> None:
    """Render hero and upload teaser card."""
    st.markdown(
        """
        <div class="vv-hero">
            <div class="vv-hero-grid">
                <div class="vv-hero-copy">
                    <h1>AI Powered Car Analysis for Smarter Buying Decisions</h1>
                    <p>
                        Upload a car image or enter details to instantly get price prediction,
                        damage detection, resale value, and market comparison.
                    </p>
                    <div class="vv-hero-cta">
                        <span class="vv-hero-btn primary">Analyze Now</span>
                        <span class="vv-hero-btn secondary">View Demo</span>
                    </div>
                </div>
                <div class="vv-upload-card">
                    <h4>Quick Analysis Input</h4>
                    <div class="vv-upload-placeholder">Drag & drop car photo here</div>
                    <div class="vv-upload-placeholder">Model | Year | Fuel | Transmission</div>
                    <div class="vv-upload-placeholder">Mileage + AI condition scan</div>
                    <div class="vv-upload-placeholder">Premium report generated instantly</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render premium footer area."""
    st.markdown(
        """
        <div class="vv-footer">
            <div class="vv-footer-grid">
                <div>
                    <h5>Company</h5>
                    <p>About</p>
                    <p>Careers</p>
                    <p>Contact</p>
                </div>
                <div>
                    <h5>Features</h5>
                    <p>Analyze Car</p>
                    <p>Compare Cars</p>
                    <p>Saved Wishlist</p>
                </div>
                <div>
                    <h5>Resources</h5>
                    <p>Reports</p>
                    <p>Market Trends</p>
                    <p>Help Center</p>
                </div>
                <div>
                    <h5>Social</h5>
                    <p>Instagram • LinkedIn • YouTube</p>
                    <p>Newsletter: premium auto insights</p>
                    <p>support@autovision.ai</p>
                </div>
            </div>
            <p style="margin-top:0.9rem;color:#94a3b8;font-size:0.8rem;">
                © 2026 AutoVision AI. All rights reserved.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_first_page_showcase() -> None:
    """Render first page hero matching modern floating-card style."""
    st.markdown(
        """
        <div class="vv-firstpage">
            <div class="vv-firstpage-head">
                <h1>VahanValue: AI Powered Used Car Analysis and Pricing in India</h1>
                <p>
                    VahanValue helps you estimate fair market value, compare vehicles, detect pricing risk,
                    and make smarter buying or selling decisions with machine-learning insights.
                </p>
                <span class="vv-firstpage-cta">Start Smart Car Valuation</span>
            </div>
            <div class="vv-floating-grid">
                <div class="vv-float-card">
                    <img src="https://images.unsplash.com/photo-1550355291-bbee04a92027?auto=format&fit=crop&w=800&q=80" alt="car details"/>
                </div>
                <div class="vv-float-card">
                    <img src="https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=800&q=80" alt="car preview"/>
                </div>
                <div class="vv-float-card">
                    <img src="https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=800&q=80" alt="sports car"/>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
