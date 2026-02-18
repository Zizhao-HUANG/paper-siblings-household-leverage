"""
Diagnostics page — VIF analysis, residual plots, validation report.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.data.validator import ValidationReport
from src.models.diagnostics import calculate_vif, missing_value_audit
from src.models.spec import Estimator, ModelResult
from src.webapp.components.charts import histogram


_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=13, color="#f1f5f9"),
    margin=dict(l=40, r=20, t=40, b=40),
)


def render(
    df: pd.DataFrame,
    results: List[ModelResult],
    validation_report: Optional[ValidationReport],
    settings: dict,
) -> None:
    """Render the diagnostics page."""
    st.markdown("# Diagnostics")
    st.markdown(
        '<p style="color: #94a3b8;">'
        "Model diagnostics, multicollinearity checks, and data validation."
        "</p>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["VIF Analysis", "Residuals", "Validation Report"])

    # ---- Tab 1: VIF ----
    with tab1:
        st.markdown("### Variance Inflation Factors")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        # Exclude IDs and DVs
        exclude = {"hhid", "debt_ratio_winsorized", "log_debt_ratio_winsorized",
                    "total_debt", "total_assets"}
        vif_candidates = [c for c in numeric_cols if c not in exclude]

        if vif_candidates:
            clean = df[vif_candidates].dropna()
            if len(clean) > 10:
                vif_df = calculate_vif(clean, vif_candidates)

                # VIF bar chart
                colors = [
                    "#fb7185" if f else "#34d399"
                    for f in vif_df["flagged"]
                ]
                fig = go.Figure(go.Bar(
                    x=vif_df["VIF"].values,
                    y=vif_df["feature"].values,
                    orientation="h",
                    marker_color=colors,
                ))
                fig.add_vline(x=5, line_dash="dash", line_color="#fbbf24",
                              annotation_text="Threshold = 5")
                fig.update_layout(title="VIF by Variable", **_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(vif_df, use_container_width=True, hide_index=True)
            else:
                st.warning("Not enough complete observations for VIF.")
        else:
            st.info("No suitable columns for VIF analysis.")

    # ---- Tab 2: Residuals ----
    with tab2:
        st.markdown("### Residual Analysis")
        ols_results = [r for r in results
                       if r.spec.estimator == Estimator.OLS and r.raw_result is not None]

        if not ols_results:
            st.info("No OLS model results available for residual analysis.")
        else:
            selected_model = st.selectbox(
                "Select Model",
                options=[r.spec.name for r in ols_results],
            )
            result = next(r for r in ols_results if r.spec.name == selected_model)
            raw = result.raw_result

            residuals = raw.resid
            fitted = raw.fittedvalues

            col1, col2 = st.columns(2)
            with col1:
                # Residuals vs Fitted
                fig = go.Figure()
                sample_idx = (
                    np.random.choice(len(residuals), min(3000, len(residuals)), replace=False)
                    if len(residuals) > 3000 else np.arange(len(residuals))
                )
                fig.add_trace(go.Scatter(
                    x=fitted.iloc[sample_idx],
                    y=residuals.iloc[sample_idx],
                    mode="markers",
                    marker=dict(size=3, color="#60a5fa", opacity=0.4),
                ))
                fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
                fig.update_layout(
                    title="Residuals vs Fitted Values",
                    xaxis_title="Fitted Values",
                    yaxis_title="Residuals",
                    **_LAYOUT,
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Residual distribution
                fig = histogram(
                    pd.DataFrame({"Residuals": residuals}),
                    "Residuals",
                    title="Residual Distribution",
                    color="#a78bfa",
                )
                st.plotly_chart(fig, use_container_width=True)

    # ---- Tab 3: Validation Report ----
    with tab3:
        st.markdown("### Data Validation Report")

        if validation_report is None:
            st.info("No validation report available.")
        else:
            status_color = "#34d399" if validation_report.is_valid else "#fb7185"
            status_text = "PASSED" if validation_report.is_valid else "FAILED"
            st.markdown(
                f'<div class="glass-card">'
                f'<span style="color: {status_color}; font-size: 1.4rem; '
                f'font-weight: 700;">Status: {status_text}</span>'
                f'<br/><span style="color: #94a3b8;">'
                f'{validation_report.rows_checked:,} rows checked across '
                f'{validation_report.columns_checked} columns. '
                f'{validation_report.error_count} errors, '
                f'{validation_report.warning_count} warnings.</span></div>',
                unsafe_allow_html=True,
            )

            if validation_report.violations:
                violations_data = [{
                    "Column": v.column,
                    "Rule": v.rule,
                    "Detail": v.detail,
                    "Severity": v.severity,
                } for v in validation_report.violations]

                st.dataframe(
                    pd.DataFrame(violations_data),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.success("No violations detected.")

        # ---- Missing values ----
        st.markdown("### Missing Value Summary")
        audit = missing_value_audit(df, df.columns.tolist())
        if not audit.empty:
            st.dataframe(audit, use_container_width=True, hide_index=True)
        else:
            st.success("No missing values in the analysis dataset.")
