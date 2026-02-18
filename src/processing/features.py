"""
Feature engineering: asset/debt coalescing, totals, ratios, winsorisation.

Core transformations
--------------------
1. **Coalesce** exact and interval values for every debt/asset variable.
2. **Sum** coalesced values into ``total_debt`` and ``total_assets``.
3. **Adjust** assets for vehicle-in-business double-counting.
4. **Compute** ``debt_ratio`` = total_debt / total_assets.
5. **Winsorise** the debt ratio at configurable percentiles.
6. **Log-transform** the debt ratio for robustness models.
"""

from __future__ import annotations

import logging
from typing import List

import numpy as np
import pandas as pd
from scipy.stats.mstats import winsorize

from src.config import Settings
from src.data.midpoint_tables import get_midpoint_series
from src.data.variables import ALL_ASSET_VARS, ALL_DEBT_VARS, ASSET_VEHICLE_IN_BUSINESS, VarSpec

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_columns(df: pd.DataFrame, specs: List[VarSpec]) -> int:
    """Create missing columns as NaN; return count of columns created."""
    created = 0
    for spec in specs:
        for col in (spec.exact, spec.interval):
            if col is not None and col not in df.columns:
                df[col] = np.nan
                created += 1
    return created


def _coalesce_var(
    df: pd.DataFrame,
    spec: VarSpec,
) -> pd.Series:
    """
    Return a single Series that prefers the exact value and falls back
    to the interval midpoint.
    """
    exact_series = df.get(spec.exact, pd.Series(np.nan, index=df.index))
    if spec.interval and spec.interval in df.columns:
        midpoint_series = get_midpoint_series(df[spec.interval], spec.interval)
        return exact_series.combine_first(midpoint_series)
    return exact_series


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def coalesce_all(df: pd.DataFrame) -> tuple[List[str], List[str]]:
    """
    Coalesce exact/interval pairs for every debt and asset variable.

    Adds columns named ``<exact_var>_val`` to *df* in place.

    Returns
    -------
    debt_cols, asset_cols : tuple[list[str], list[str]]
        Names of the newly created coalesced columns.
    """
    _ensure_columns(df, ALL_DEBT_VARS)
    _ensure_columns(df, ALL_ASSET_VARS)
    # Also ensure vehicle-in-business
    for col in (ASSET_VEHICLE_IN_BUSINESS.exact, ASSET_VEHICLE_IN_BUSINESS.interval):
        if col is not None and col not in df.columns:
            df[col] = np.nan

    debt_cols: List[str] = []
    for spec in ALL_DEBT_VARS:
        name = spec.coalesced_name
        df[name] = _coalesce_var(df, spec)
        debt_cols.append(name)

    asset_cols: List[str] = []
    for spec in ALL_ASSET_VARS:
        name = spec.coalesced_name
        df[name] = _coalesce_var(df, spec)
        asset_cols.append(name)

    logger.info("Coalesced %d debt + %d asset variables.", len(debt_cols), len(asset_cols))
    return debt_cols, asset_cols


def compute_totals(
    df: pd.DataFrame,
    debt_cols: List[str],
    asset_cols: List[str],
) -> None:
    """Compute ``total_debt``, ``total_assets`` (with vehicle adjustment)."""
    df["total_debt"] = df[debt_cols].fillna(0).sum(axis=1)
    df["total_assets_raw"] = df[asset_cols].fillna(0).sum(axis=1)

    # Vehicle-in-business adjustment
    vib = _coalesce_var(df, ASSET_VEHICLE_IN_BUSINESS).fillna(0)
    df["total_assets"] = (df["total_assets_raw"] - vib).clip(lower=0)
    logger.info("Computed total_debt and total_assets.")


def compute_debt_ratio(df: pd.DataFrame, cfg: Settings) -> None:
    """Compute raw and winsorised debt ratio + log transform."""
    eps = cfg.epsilon

    # Raw ratio
    df["debt_ratio"] = df["total_debt"] / (df["total_assets"] + eps)
    df.loc[(df["total_debt"] == 0) & (df["total_assets"] == 0), "debt_ratio"] = 0.0
    df.loc[(df["total_debt"] > 0) & (df["total_assets"] == 0), "debt_ratio"] = np.nan

    # Winsorise
    clean = df["debt_ratio"].replace([np.inf, -np.inf], np.nan).dropna()
    if not clean.empty:
        win_vals = winsorize(clean, limits=list(cfg.winsorize_limits))
        df["debt_ratio_winsorized"] = pd.Series(win_vals, index=clean.index)
        logger.info(
            "Winsorised debt_ratio at %s limits. N = %d.",
            cfg.winsorize_limits, len(clean),
        )
    else:
        df["debt_ratio_winsorized"] = np.nan
        logger.warning("debt_ratio column is empty after cleaning — cannot winsorise.")

    # Log transform
    c = cfg.log_dv_constant
    if "debt_ratio_winsorized" in df.columns:
        log_input = df["debt_ratio_winsorized"] + c
        df["log_debt_ratio_winsorized"] = np.log(log_input.where(log_input > 0))
    else:
        df["log_debt_ratio_winsorized"] = np.nan

    logger.info("Debt ratio (raw, winsorised, log) computed.")
