"""
Global sidebar controls for the Streamlit dashboard.
"""

from __future__ import annotations

import streamlit as st


def render_sidebar() -> dict:
    """
    Render the sidebar and return user selections.

    Returns
    -------
    dict
        Keys: ``page``, ``show_raw_data``, ``significance_level``.
    """
    with st.sidebar:
        st.markdown("## CHFS 2017 Analysis")
        st.markdown("---")

        page = st.radio(
            "Navigate",
            options=[
                "Overview",
                "Data Explorer",
                "Regression Results",
                "Diagnostics",
            ],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("### Settings")

        sig_level = st.select_slider(
            "Significance Level",
            options=[0.01, 0.05, 0.10],
            value=0.05,
        )

        show_raw = st.checkbox("Show raw data tables", value=False)

        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; opacity: 0.5; font-size: 0.75rem;'>"
            "v2.0.0 &middot; Zizhao HUANG"
            "</div>",
            unsafe_allow_html=True,
        )

    return {
        "page": page,
        "show_raw_data": show_raw,
        "significance_level": sig_level,
    }
