"""
Metric card components with gradient styling.
"""

from __future__ import annotations

import streamlit as st


def render_metric_row(metrics: list[dict]) -> None:
    """
    Render a row of metric cards.

    Parameters
    ----------
    metrics : list[dict]
        Each dict has keys ``label``, ``value``, ``delta`` (optional),
        ``delta_color`` (optional, "normal" | "inverse" | "off").
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.metric(
                label=m["label"],
                value=m["value"],
                delta=m.get("delta"),
                delta_color=m.get("delta_color", "normal"),
            )
