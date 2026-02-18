"""
Merge individual-level head information into household-level data.

This module is responsible for a single, well-defined step: taking the
extracted head records (from ``src.data.loader.extract_heads``) and left-
joining them onto the household DataFrame on ``hhid``.
"""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def merge_head_into_household(
    hh_df: pd.DataFrame,
    head_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Left-join head-level controls onto the household DataFrame.

    Parameters
    ----------
    hh_df : DataFrame
        Household-level data (one row per household).
    head_df : DataFrame
        De-duplicated head information keyed on ``hhid``.

    Returns
    -------
    DataFrame
        ``hh_df`` enriched with head-level columns.

    Raises
    ------
    ValueError
        If the merge changes the row count (indicates a many-to-many key).
    """
    n_before = len(hh_df)
    merged = pd.merge(hh_df, head_df, on="hhid", how="left")
    n_after = len(merged)

    if n_after != n_before:
        raise ValueError(
            f"Merge changed row count from {n_before} to {n_after}. "
            "Check 'hhid' uniqueness in the head DataFrame."
        )

    matched = merged[head_df.columns.drop("hhid")[0]].notna().sum()
    logger.info(
        "Merged head info: %d/%d households matched (%.1f%%).",
        matched,
        n_after,
        matched / n_after * 100,
    )
    return merged
