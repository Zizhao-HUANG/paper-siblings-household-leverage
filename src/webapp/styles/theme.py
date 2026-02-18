"""
Premium dark theme for the Streamlit dashboard.

Injects custom CSS for a polished, publication-grade visual identity:
- Dark glassmorphism background
- Inter font family
- Gradient accents
- Smooth transitions
"""

from __future__ import annotations

import streamlit as st

# Colour palette
PALETTE = {
    "bg_primary": "#0e1117",
    "bg_card": "rgba(17, 25, 40, 0.75)",
    "bg_glass": "rgba(255, 255, 255, 0.05)",
    "accent_blue": "#60a5fa",
    "accent_purple": "#a78bfa",
    "accent_emerald": "#34d399",
    "accent_amber": "#fbbf24",
    "accent_rose": "#fb7185",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "border": "rgba(255, 255, 255, 0.08)",
    "gradient_start": "#3b82f6",
    "gradient_end": "#8b5cf6",
}


def inject_theme() -> None:
    """Inject the custom CSS theme into the Streamlit app."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global */
        html, body, .stApp {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: {PALETTE["bg_primary"]};
            color: {PALETTE["text_primary"]};
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
            border-right: 1px solid {PALETTE["border"]};
        }}

        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {{
            background: linear-gradient(135deg, {PALETTE["accent_blue"]}, {PALETTE["accent_purple"]});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        /* Metric cards */
        [data-testid="stMetric"] {{
            background: {PALETTE["bg_card"]};
            backdrop-filter: blur(16px);
            border: 1px solid {PALETTE["border"]};
            border-radius: 12px;
            padding: 16px 20px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        [data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(96, 165, 250, 0.15);
        }}

        [data-testid="stMetricValue"] {{
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, {PALETTE["accent_blue"]}, {PALETTE["accent_emerald"]});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        [data-testid="stMetricLabel"] {{
            font-size: 0.85rem;
            font-weight: 500;
            color: {PALETTE["text_secondary"]};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
            background: {PALETTE["bg_glass"]};
            border-radius: 10px;
            padding: 4px;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {PALETTE["gradient_start"]}, {PALETTE["gradient_end"]});
            color: white;
        }}

        /* DataFrames */
        .stDataFrame {{
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid {PALETTE["border"]};
        }}

        /* Headers */
        h1 {{
            font-weight: 700;
            letter-spacing: -0.5px;
        }}

        h2, h3 {{
            font-weight: 600;
            color: {PALETTE["text_primary"]};
        }}

        /* Expander */
        .streamlit-expanderHeader {{
            background: {PALETTE["bg_glass"]};
            border-radius: 8px;
            font-weight: 500;
        }}

        /* Divider */
        hr {{
            border-color: {PALETTE["border"]};
        }}

        /* Custom gradient text class */
        .gradient-text {{
            background: linear-gradient(135deg, {PALETTE["accent_blue"]}, {PALETTE["accent_purple"]});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }}

        .glass-card {{
            background: {PALETTE["bg_card"]};
            backdrop-filter: blur(16px);
            border: 1px solid {PALETTE["border"]};
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
