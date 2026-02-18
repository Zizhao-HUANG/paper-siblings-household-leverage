"""
Data Explorer page — interactive filtering and browsing.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from src.webapp.components.charts import scatter, histogram


def render(df: pd.DataFrame, settings: dict) -> None:
    """Render the data explorer page."""
    st.markdown("# Data Explorer")
    st.markdown(
        '<p style="color: #94a3b8;">'
        "Filter and explore the analysis dataset interactively."
        "</p>",
        unsafe_allow_html=True,
    )

    # ---- Filters ----
    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            if "head_age" in df.columns:
                age_range = st.slider(
                    "Head Age",
                    min_value=int(df["head_age"].min()),
                    max_value=int(df["head_age"].max()),
                    value=(16, 100),
                )
            else:
                age_range = (0, 200)

        with col2:
            if "head_is_male" in df.columns:
                gender = st.selectbox(
                    "Gender",
                    options=["All", "Male", "Female"],
                )
            else:
                gender = "All"

        with col3:
            if "has_business" in df.columns:
                business = st.selectbox(
                    "Business Owner",
                    options=["All", "Yes", "No"],
                )
            else:
                business = "All"

    # Apply filters
    filtered = df.copy()
    if "head_age" in filtered.columns:
        filtered = filtered[
            (filtered["head_age"] >= age_range[0])
            & (filtered["head_age"] <= age_range[1])
        ]
    if gender != "All" and "head_is_male" in filtered.columns:
        filtered = filtered[filtered["head_is_male"] == (1.0 if gender == "Male" else 0.0)]
    if business != "All" and "has_business" in filtered.columns:
        filtered = filtered[filtered["has_business"] == (1.0 if business == "Yes" else 0.0)]

    st.markdown(f"**Showing {len(filtered):,} of {len(df):,} households**")
    st.markdown("---")

    # ---- Scatter plot ----
    st.markdown("### Scatter Analysis")
    col_a, col_b = st.columns(2)
    numeric_cols = filtered.select_dtypes(include="number").columns.tolist()

    with col_a:
        x_var = st.selectbox("X-axis", options=numeric_cols, index=0)
    with col_b:
        default_y = (
            numeric_cols.index("debt_ratio_winsorized")
            if "debt_ratio_winsorized" in numeric_cols
            else min(1, len(numeric_cols) - 1)
        )
        y_var = st.selectbox("Y-axis", options=numeric_cols, index=default_y)

    if x_var and y_var:
        sample = filtered[[x_var, y_var]].dropna()
        if len(sample) > 5000:
            sample = sample.sample(5000, random_state=42)
        fig = scatter(sample, x_var, y_var, title=f"{y_var} vs {x_var}")
        st.plotly_chart(fig, use_container_width=True)

    # ---- Distribution of selected variable ----
    st.markdown("### Variable Distribution")
    dist_var = st.selectbox("Variable", options=numeric_cols, index=0, key="dist_var")
    if dist_var:
        fig = histogram(
            filtered.dropna(subset=[dist_var]),
            dist_var,
            title=f"Distribution of {dist_var}",
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Descriptive stats ----
    st.markdown("### Summary Statistics")
    st.dataframe(
        filtered[numeric_cols].describe().T.style.format("{:.4f}"),
        use_container_width=True,
    )
