"""
End-to-end data processing pipeline.

Chains together: load → extract heads → merge → coalesce → totals →
debt ratio → controls → select → validate → output.

Usage
-----
    from src.processing.pipeline import run_pipeline
    result = run_pipeline(cfg)
    analysis_df = result.analysis_df
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.config import Settings
from src.data.loader import extract_heads, load_raw_data
from src.data.validator import ValidationReport, validate
from src.processing.controls import build_controls
from src.processing.features import coalesce_all, compute_debt_ratio, compute_totals
from src.processing.merge import merge_head_into_household

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Container for everything the pipeline produces."""

    analysis_df: pd.DataFrame
    validation_report: ValidationReport
    n_raw_households: int
    n_raw_individuals: int
    n_analysis_rows: int

    def summary(self) -> str:
        return (
            f"Pipeline complete: {self.n_raw_households} households, "
            f"{self.n_raw_individuals} individuals -> "
            f"{self.n_analysis_rows} analysis rows. "
            f"{self.validation_report.summary()}"
        )


def run_pipeline(
    cfg: Settings,
    hh_path: Path | None = None,
    ind_path: Path | None = None,
) -> PipelineResult:
    """
    Execute the full data processing pipeline.

    Parameters
    ----------
    cfg : Settings
        Runtime configuration.
    hh_path, ind_path : Path, optional
        Override data paths (for testing / Web UI uploads).

    Returns
    -------
    PipelineResult
        Contains the analysis-ready DataFrame, validation report, and counts.
    """
    logger.info("=== Pipeline started ===")

    # 1. Load raw data
    hh_df, ind_df = load_raw_data(cfg, hh_path, ind_path)
    n_hh = len(hh_df)
    n_ind = len(ind_df)

    # 2. Extract head info
    head_df = extract_heads(ind_df, cfg)

    # 3. Merge head info into household data
    hh_df = merge_head_into_household(hh_df, head_df)

    # 4. Coalesce exact / interval values
    debt_cols, asset_cols = coalesce_all(hh_df)

    # 5. Compute totals
    compute_totals(hh_df, debt_cols, asset_cols)

    # 6. Compute debt ratio (winsorised + log)
    compute_debt_ratio(hh_df, cfg)

    # 7. Build control variables
    build_controls(hh_df)

    # 8. Select analysis columns
    core_vars = [
        "hhid",
        "head_siblings",
        "debt_ratio_winsorized",
        "log_debt_ratio_winsorized",
        "total_debt",
        "total_assets",
    ]
    all_cols = core_vars + cfg.head_control_vars + cfg.hh_control_vars
    existing = [c for c in all_cols if c in hh_df.columns]
    missing = [c for c in all_cols if c not in hh_df.columns]
    if missing:
        logger.warning("Missing analysis columns (excluded): %s", missing)

    analysis_df = hh_df[existing].copy()
    logger.info(
        "Analysis DataFrame: %d rows x %d cols.", len(analysis_df), len(analysis_df.columns)
    )

    # 9. Validate
    report = validate(analysis_df)

    logger.info("=== Pipeline finished ===")
    return PipelineResult(
        analysis_df=analysis_df,
        validation_report=report,
        n_raw_households=n_hh,
        n_raw_individuals=n_ind,
        n_analysis_rows=len(analysis_df),
    )
