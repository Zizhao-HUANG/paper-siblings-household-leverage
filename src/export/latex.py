"""
LaTeX regression table generator (stargazer-style).

Produces publication-ready multi-model regression tables that can be
``\\input{}``-ed directly into a LaTeX manuscript.

Features
--------
- Side-by-side model comparison with aligned coefficients.
- Significance stars (*, **, ***).
- Standard errors in parentheses.
- Goodness-of-fit footer (N, R-squared, Adj. R-squared, AIC, BIC).
- Robust SE indicator row.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.models.spec import ModelResult

logger = logging.getLogger(__name__)


def _star(p: float) -> str:
    """Return significance stars based on p-value."""
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def _fmt(value: float | None, decimals: int = 4) -> str:
    """Format a number for display, or return empty string for None/NaN."""
    if value is None or pd.isna(value):
        return ""
    return f"{value:.{decimals}f}"


def build_regression_table(
    results: list[ModelResult],
    caption: str = "Regression Results",
    label: str = "tab:regression",
    note: str = "",
) -> str:
    """
    Build a stargazer-style LaTeX table from multiple ModelResult objects.

    Parameters
    ----------
    results : list[ModelResult]
        Estimated model results (in column order).
    caption : str
        LaTeX table caption.
    label : str
        LaTeX label for cross-referencing.
    note : str
        Footnote text appended below the table.

    Returns
    -------
    str
        Complete LaTeX ``tabular`` environment as a string.
    """
    if not results:
        return "% No results to display."

    # Collect all unique variables (union across models)
    all_vars: list[str] = []
    seen = set()
    for r in results:
        for v in r.coefficients.index:
            if v not in seen:
                all_vars.append(v)
                seen.add(v)

    n_models = len(results)
    col_spec = "l" + "c" * n_models

    lines: list[str] = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(f"\\caption{{{caption}}}")
    lines.append(f"\\label{{{label}}}")
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append(r"\hline\hline")

    # Header row
    header = " & ".join([""] + [r.spec.name for r in results]) + r" \\"
    lines.append(header)

    # Dependent variable row
    dv_row = (
        " & ".join(["Dep. Variable"] + [r.spec.dep_var.replace("_", r"\_") for r in results])
        + r" \\"
    )
    lines.append(dv_row)
    lines.append(r"\hline")

    # Coefficient rows (coef + SE on alternating lines)
    for var in all_vars:
        coef_cells = []
        se_cells = []
        for r in results:
            if var in r.coefficients.index:
                coef_val = r.coefficients[var]
                p_val = r.p_values.get(var, float("nan"))
                se_val = r.std_errors.get(var, float("nan"))
                coef_cells.append(f"{_fmt(coef_val)}{_star(p_val)}")
                se_cells.append(f"({_fmt(se_val)})" if not pd.isna(se_val) else "")
            else:
                coef_cells.append("")
                se_cells.append("")

        var_label = var.replace("_", r"\_")
        lines.append(" & ".join([var_label] + coef_cells) + r" \\")
        lines.append(" & ".join([""] + se_cells) + r" \\[3pt]")

    lines.append(r"\hline")

    # Footer: goodness-of-fit statistics
    # N
    n_row = " & ".join(["N"] + [str(r.n_obs) for r in results]) + r" \\"
    lines.append(n_row)

    # R-squared
    r2_row = " & ".join(["$R^2$"] + [_fmt(r.r_squared) for r in results]) + r" \\"
    lines.append(r2_row)

    # Adj R-squared
    adj_r2_row = " & ".join(["Adj. $R^2$"] + [_fmt(r.adj_r_squared) for r in results]) + r" \\"
    lines.append(adj_r2_row)

    # Robust SE indicator
    se_type_row = " & ".join(["Robust SE"] + [r.spec.robust_se.value for r in results]) + r" \\"
    lines.append(se_type_row)

    lines.append(r"\hline\hline")

    # Note
    if note:
        lines.append(f"\\multicolumn{{{n_models + 1}}}{{l}}{{\\footnotesize {note}}}")

    lines.append(
        f"\\multicolumn{{{n_models + 1}}}{{l}}"
        r"{\footnotesize $^{***}p<0.01$; $^{**}p<0.05$; $^{*}p<0.10$}"
    )

    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def save_latex_table(
    results: list[ModelResult],
    output_path: Path,
    caption: str = "Regression Results",
    label: str = "tab:regression",
    note: str = "",
) -> Path:
    """Build and write a LaTeX regression table to disk."""
    tex = build_regression_table(results, caption, label, note)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(tex, encoding="utf-8")
    logger.info("LaTeX table saved to %s", output_path)
    return output_path
