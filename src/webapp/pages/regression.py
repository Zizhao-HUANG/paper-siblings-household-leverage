"""
Regression Results page — model comparison dashboard.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.models.spec import ModelResult
from src.webapp.components.charts import bar_chart, coefficient_plot


def render(
    df: pd.DataFrame,
    results: list[ModelResult],
    settings: dict,
) -> None:
    """Render the regression results page."""
    st.markdown("# Regression Results")
    st.markdown(
        '<p style="color: #94a3b8;">Side-by-side comparison of all estimated models.</p>',
        unsafe_allow_html=True,
    )

    if not results:
        st.warning("No model results available. Run the analysis pipeline first.")
        return

    # ---- Model selector ----
    model_names = [r.spec.name for r in results]
    selected = st.multiselect(
        "Select models to compare",
        options=model_names,
        default=model_names,
    )
    selected_results = [r for r in results if r.spec.name in selected]

    if not selected_results:
        st.info("Select at least one model to display.")
        return

    # ---- Summary table ----
    st.markdown("### Model Summary")
    summary_data = []
    for r in selected_results:
        summary_data.append(
            {
                "Model": r.spec.name,
                "Estimator": r.spec.estimator.name,
                "Dep. Variable": r.spec.dep_var,
                "N": r.n_obs,
                "R-squared": f"{r.r_squared:.4f}",
                "Adj. R-sq.": f"{r.adj_r_squared:.4f}" if r.adj_r_squared is not None else "—",
                "Robust SE": r.spec.robust_se.value,
            }
        )

    st.dataframe(
        pd.DataFrame(summary_data),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # ---- Coefficient comparison ----
    st.markdown("### Coefficient Comparison")
    tabs = st.tabs([r.spec.name for r in selected_results])
    for tab, r in zip(tabs, selected_results, strict=False):
        with tab:
            st.markdown(f"**{r.spec.label}**")
            col1, col2 = st.columns([2, 1])

            with col1:
                fig = coefficient_plot(
                    r.coefficients,
                    r.std_errors,
                    title=f"{r.spec.name}: Coefficient Plot (95% CI)",
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                coef_df = pd.DataFrame(
                    {
                        "Coef.": r.coefficients,
                        "Std.Err.": r.std_errors,
                        "t-stat": r.t_values,
                        "p-value": r.p_values,
                    }
                ).drop("const", errors="ignore")

                coef_df["Sig."] = coef_df["p-value"].apply(
                    lambda p: (
                        "***"
                        if p < 0.01
                        else "**"
                        if p < 0.05
                        else "*"
                        if p < 0.10
                        else ""
                        if pd.notna(p)
                        else ""
                    )
                )

                st.dataframe(
                    coef_df.style.format(
                        {
                            "Coef.": "{:.6f}",
                            "Std.Err.": "{:.6f}",
                            "t-stat": "{:.3f}",
                            "p-value": "{:.4f}",
                        }
                    ),
                    use_container_width=True,
                )

    # ---- R-squared comparison bar chart ----
    st.markdown("### Goodness of Fit")
    fig = bar_chart(
        labels=[r.spec.name for r in selected_results],
        values=[r.r_squared for r in selected_results],
        title="R-squared by Model",
        color="#34d399",
    )
    st.plotly_chart(fig, use_container_width=True)
