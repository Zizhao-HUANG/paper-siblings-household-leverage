"""
CHFS 2017 Siblings-Debt Analysis — Interactive Dashboard

Main Streamlit entry point.  Routes to page modules based on sidebar
selection and manages the shared data/model state via ``st.session_state``.

Usage
-----
    streamlit run src/webapp/app.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import Settings
from src.data.validator import ValidationReport
from src.models.runner import run_all
from src.models.spec import ModelResult, get_default_specs
from src.processing.pipeline import run_pipeline
from src.utils.logging_config import setup_logging
from src.webapp.components.sidebar import render_sidebar
from src.webapp.pages import data_explorer, diagnostics, overview, regression
from src.webapp.styles.theme import inject_theme

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CHFS 2017 — Siblings & Debt Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
inject_theme()


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------


def _project_root() -> Path:
    """Resolve the project root directory (where pyproject.toml lives)."""
    # When launched via `streamlit run src/webapp/app.py`, __file__ is inside
    # src/webapp/, so project root is two levels up.
    root = Path(__file__).resolve().parent.parent.parent
    if (root / "pyproject.toml").exists():
        return root
    # Fallback: current working directory
    return Path.cwd()


def _load_data() -> tuple[pd.DataFrame, ValidationReport | None]:
    """Load analysis data — either from pipeline or uploaded CSV."""
    if "analysis_df" in st.session_state:
        return st.session_state["analysis_df"], st.session_state.get("validation_report")

    root = _project_root()

    # Try to load pre-processed CSV from outputs/
    csv_path = root / "outputs" / "processed_analysis_data.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        st.session_state["analysis_df"] = df
        st.session_state["validation_report"] = None
        logger.info("Loaded %d rows from %s", len(df), csv_path)
        return df, None

    return pd.DataFrame(), None


def _get_model_results(df: pd.DataFrame) -> list[ModelResult]:
    """Run or retrieve model results."""
    if "model_results" in st.session_state:
        return list(st.session_state["model_results"])

    if df.empty:
        return []

    cfg = Settings()
    specs = get_default_specs(cfg.independent_vars)
    results = run_all(df, specs)
    st.session_state["model_results"] = results
    return results


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
settings = render_sidebar()


# ---------------------------------------------------------------------------
# Data loading section (top of main area)
# ---------------------------------------------------------------------------
df, validation_report = _load_data()

if df.empty:
    st.markdown("# CHFS 2017 — Siblings & Debt Analysis")
    st.markdown("---")

    st.markdown(
        '<div class="glass-card">'
        "<h3>Getting Started</h3>"
        "<p>No analysis data found. Choose one of the following options:</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Option 1: Run the Full Pipeline")
        st.markdown("Place your `.dta` files in `data/raw/` and click **Run Pipeline**.")
        if st.button("Run Pipeline", type="primary"):
            with st.spinner("Running pipeline..."):
                try:
                    setup_logging()
                    cfg = Settings()
                    result = run_pipeline(cfg)
                    st.session_state["analysis_df"] = result.analysis_df
                    st.session_state["validation_report"] = result.validation_report
                    st.rerun()
                except Exception as e:
                    st.error(f"Pipeline error: {e}")

    with col2:
        st.markdown("#### Option 2: Upload Processed CSV")
        uploaded = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded is not None:
            df = pd.read_csv(uploaded, encoding="utf-8-sig")
            st.session_state["analysis_df"] = df
            st.session_state["validation_report"] = None
            st.rerun()

    st.stop()


# ---------------------------------------------------------------------------
# Page router
# ---------------------------------------------------------------------------
model_results = _get_model_results(df)

page = settings["page"]

if page == "Overview":
    overview.render(df, settings)
elif page == "Data Explorer":
    data_explorer.render(df, settings)
elif page == "Regression Results":
    regression.render(df, model_results, settings)
elif page == "Diagnostics":
    diagnostics.render(df, model_results, validation_report, settings)
