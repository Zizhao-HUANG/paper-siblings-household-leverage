"""
Overview page — landing dashboard with key metrics and summary charts.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from src.webapp.components.charts import histogram, heatmap
from src.webapp.components.metric_cards import render_metric_row


def render(df: pd.DataFrame, settings: dict) -> None:
    """Render the overview page."""
    st.markdown("# Overview")
    st.markdown(
        '<p style="color: #94a3b8; font-size: 1.1rem;">'
        "Key metrics and distributional summaries from the CHFS 2017 analysis."
        "</p>",
        unsafe_allow_html=True,
    )

    # ---- Key metrics ----
    n_total = len(df)
    n_with_siblings = int(df["head_siblings"].notna().sum()) if "head_siblings" in df.columns else 0
    mean_debt_ratio = (
        df["debt_ratio_winsorized"].mean()
        if "debt_ratio_winsorized" in df.columns else 0
    )
    mean_assets = df["total_assets"].mean() if "total_assets" in df.columns else 0

    render_metric_row([
        {"label": "Total Households", "value": f"{n_total:,}"},
        {"label": "With Sibling Data", "value": f"{n_with_siblings:,}"},
        {
            "label": "Mean Debt Ratio",
            "value": f"{mean_debt_ratio:.4f}",
        },
        {
            "label": "Mean Total Assets",
            "value": f"¥{mean_assets:,.0f}",
        },
    ])

    st.markdown("---")

    # ---- Distribution charts ----
    col1, col2 = st.columns(2)

    with col1:
        if "debt_ratio_winsorized" in df.columns:
            fig = histogram(
                df.dropna(subset=["debt_ratio_winsorized"]),
                "debt_ratio_winsorized",
                title="Distribution of Debt Ratio (Winsorised)",
                color="#60a5fa",
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "head_siblings" in df.columns:
            fig = histogram(
                df.dropna(subset=["head_siblings"]),
                "head_siblings",
                title="Distribution of Number of Siblings",
                nbins=20,
                color="#a78bfa",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ---- Correlation heatmap ----
    st.markdown("### Correlation Matrix")
    numeric_cols = [
        "head_siblings", "debt_ratio_winsorized", "head_age",
        "head_educ", "head_health", "num_houses", "log_total_assets",
    ]
    available = [c for c in numeric_cols if c in df.columns]
    if len(available) >= 2:
        fig = heatmap(df[available].dropna(), title="")
        st.plotly_chart(fig, use_container_width=True)

    # ---- Raw data preview ----
    if settings.get("show_raw_data"):
        st.markdown("### Raw Data Preview")
        st.dataframe(df.head(100), use_container_width=True)
