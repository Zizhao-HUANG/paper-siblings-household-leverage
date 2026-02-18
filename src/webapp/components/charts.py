"""
Plotly chart factory functions for the dashboard.

All charts use a consistent dark theme matching the Streamlit CSS.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

_LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=13, color="#f1f5f9"),
    margin=dict(l=40, r=20, t=40, b=40),
)


def histogram(
    df: pd.DataFrame,
    column: str,
    title: str = "",
    nbins: int = 50,
    color: str = "#60a5fa",
) -> go.Figure:
    """Create a styled histogram."""
    fig = px.histogram(df, x=column, nbins=nbins, title=title)
    fig.update_traces(marker_color=color, marker_line_width=0, opacity=0.85)
    fig.update_layout(**_LAYOUT_DEFAULTS)
    return fig


def scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: str | None = None,
    trendline: str = "ols",
) -> go.Figure:
    """Create a styled scatter plot with optional trendline."""
    fig = px.scatter(
        df,
        x=x,
        y=y,
        title=title,
        color=color,
        trendline=trendline,
        opacity=0.5,
    )
    fig.update_layout(**_LAYOUT_DEFAULTS)
    return fig


def bar_chart(
    labels: list[str],
    values: list[float],
    title: str = "",
    color: str = "#a78bfa",
    horizontal: bool = False,
) -> go.Figure:
    """Create a styled bar chart."""
    if horizontal:
        fig = go.Figure(go.Bar(y=labels, x=values, orientation="h", marker_color=color))
    else:
        fig = go.Figure(go.Bar(x=labels, y=values, marker_color=color))
    fig.update_layout(title=title, **_LAYOUT_DEFAULTS)
    return fig


def coefficient_plot(
    coefs: pd.Series,
    errors: pd.Series,
    title: str = "Coefficient Plot",
) -> go.Figure:
    """Create a coefficient plot with error bars."""
    # Remove constant
    coefs = coefs.drop("const", errors="ignore")
    errors = errors.drop("const", errors="ignore")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=coefs.values,
            y=coefs.index,
            mode="markers",
            marker=dict(size=10, color="#60a5fa"),
            error_x=dict(
                type="data",
                array=errors.values * 1.96,
                visible=True,
                color="#94a3b8",
                thickness=1.5,
            ),
            name="Coefficient",
        )
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8", opacity=0.5)
    fig.update_layout(
        title=title,
        xaxis_title="Coefficient",
        yaxis_title="",
        **_LAYOUT_DEFAULTS,
    )
    return fig


def heatmap(
    df: pd.DataFrame,
    title: str = "Correlation Matrix",
) -> go.Figure:
    """Create a correlation heatmap."""
    corr = df.select_dtypes(include="number").corr()
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="RdBu_r",
            zmin=-1,
            zmax=1,
            text=corr.round(2).values,
            texttemplate="%{text}",
            textfont=dict(size=10),
        )
    )
    fig.update_layout(title=title, **_LAYOUT_DEFAULTS)
    return fig
