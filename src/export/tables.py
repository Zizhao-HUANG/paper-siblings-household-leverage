"""
Summary statistics and VIF table export (CSV + LaTeX).

Generates publication-ready descriptive statistics tables and VIF
diagnostics tables in both CSV and LaTeX formats.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import pandas as pd

from src.models.diagnostics import calculate_vif, descriptive_stats, missing_value_audit

logger = logging.getLogger(__name__)


def export_descriptive_stats(
    df: pd.DataFrame,
    cols: List[str],
    output_dir: Path,
    filename_stem: str = "descriptive_stats",
) -> tuple[Path, Path]:
    """
    Export descriptive statistics as CSV and LaTeX.

    Returns
    -------
    csv_path, tex_path : tuple[Path, Path]
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    stats = descriptive_stats(df, cols)

    csv_path = output_dir / f"{filename_stem}.csv"
    stats.to_csv(csv_path, float_format="%.4f")

    tex_path = output_dir / f"{filename_stem}.tex"
    tex_content = _df_to_latex(
        stats.reset_index().rename(columns={"index": "Variable"}),
        caption="Descriptive Statistics",
        label="tab:desc_stats",
    )
    tex_path.write_text(tex_content, encoding="utf-8")

    logger.info("Descriptive statistics saved: %s, %s", csv_path, tex_path)
    return csv_path, tex_path


def export_missing_audit(
    df: pd.DataFrame,
    cols: List[str],
    output_dir: Path,
    filename_stem: str = "missing_values",
) -> Path:
    """Export missing-value audit as CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    audit = missing_value_audit(df, cols)
    csv_path = output_dir / f"{filename_stem}.csv"
    audit.to_csv(csv_path, index=False, float_format="%.2f")
    logger.info("Missing-value audit saved: %s", csv_path)
    return csv_path


def export_vif(
    df: pd.DataFrame,
    cols: List[str],
    output_dir: Path,
    threshold: float = 5.0,
    filename_stem: str = "vif_diagnostics",
) -> tuple[Path, Path]:
    """
    Export VIF diagnostics as CSV and LaTeX.

    Returns
    -------
    csv_path, tex_path : tuple[Path, Path]
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Need clean data for VIF
    clean = df[cols].dropna()
    if clean.empty:
        logger.warning("Cannot compute VIF — no complete observations.")
        empty_path = output_dir / f"{filename_stem}.csv"
        empty_path.write_text("# No data available for VIF computation.\n", encoding="utf-8")
        return empty_path, empty_path

    vif = calculate_vif(clean, cols, threshold)

    csv_path = output_dir / f"{filename_stem}.csv"
    vif.to_csv(csv_path, index=False, float_format="%.2f")

    tex_path = output_dir / f"{filename_stem}.tex"
    tex_content = _df_to_latex(
        vif,
        caption="Variance Inflation Factors",
        label="tab:vif",
    )
    tex_path.write_text(tex_content, encoding="utf-8")

    logger.info("VIF diagnostics saved: %s, %s", csv_path, tex_path)
    return csv_path, tex_path


def _df_to_latex(
    df: pd.DataFrame,
    caption: str,
    label: str,
) -> str:
    """Convert a DataFrame to a simple LaTeX table."""
    col_spec = "l" + "r" * (len(df.columns) - 1)
    lines: list[str] = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(f"\\caption{{{caption}}}")
    lines.append(f"\\label{{{label}}}")
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append(r"\hline\hline")

    # Header
    header = " & ".join(str(c).replace("_", r"\_") for c in df.columns) + r" \\"
    lines.append(header)
    lines.append(r"\hline")

    # Rows
    for _, row in df.iterrows():
        cells = []
        for val in row:
            if isinstance(val, float):
                cells.append(f"{val:.4f}")
            elif isinstance(val, bool):
                cells.append("Yes" if val else "")
            else:
                cells.append(str(val).replace("_", r"\_"))
        lines.append(" & ".join(cells) + r" \\")

    lines.append(r"\hline\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    return "\n".join(lines)
