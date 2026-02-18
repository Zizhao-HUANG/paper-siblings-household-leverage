"""
Data loading utilities for CHFS 2017 Stata files.

Responsible for:
1. Reading ``.dta`` files into DataFrames.
2. Basic validation (file existence, required columns).
3. Extracting household-head (respondent proxy) records from the
   individual-level file.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import Settings
from src.data.variables import HEAD_COLS_MAP

logger = logging.getLogger(__name__)


class DataLoadError(Exception):
    """Raised when required data files cannot be loaded."""


def load_stata(path: Path) -> pd.DataFrame:
    """Load a Stata ``.dta`` file with all variables kept numeric."""
    if not path.exists():
        raise DataLoadError(f"File not found: {path}")
    df = pd.read_stata(path, convert_categoricals=False)
    logger.info("Loaded %s  → %d rows × %d cols", path.name, len(df), len(df.columns))
    return df


def load_raw_data(
    cfg: Settings,
    hh_path: Path | None = None,
    ind_path: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load household and individual data.

    Parameters
    ----------
    cfg : Settings
        Runtime configuration (provides default paths).
    hh_path, ind_path : Path, optional
        Override paths (useful for testing or the Web UI file uploader).

    Returns
    -------
    hh_df, ind_df : tuple[DataFrame, DataFrame]
    """
    hh_df = load_stata(hh_path or cfg.hh_filepath)
    ind_df = load_stata(ind_path or cfg.ind_filepath)
    return hh_df, ind_df


def extract_heads(
    ind_df: pd.DataFrame,
    cfg: Settings,
) -> pd.DataFrame:
    """
    Identify household heads (questionnaire respondent proxies) and compute
    derived variables: age, sibling count.

    Returns a de-duplicated DataFrame keyed on ``hhid``.
    """
    head_var = "a2001"
    if head_var not in ind_df.columns:
        raise DataLoadError(
            f"Cannot identify heads: column '{head_var}' missing from individual data."
        )

    heads = ind_df[ind_df[head_var] == 1].copy()
    logger.info("Identified %d household heads.", len(heads))

    # ── Age ──
    if "a2005" not in heads.columns:
        raise DataLoadError("Birth-year column 'a2005' missing.")
    heads["head_age"] = cfg.survey_year - heads["a2005"]

    # Age filter
    before = len(heads)
    heads = heads[heads["head_age"] >= cfg.head_min_age].copy()
    dropped = before - len(heads)
    if dropped:
        logger.warning("Dropped %d heads aged < %d.", dropped, cfg.head_min_age)

    # ── Siblings ──
    for col in ("a2028", "a2029"):
        if col not in heads.columns:
            heads[col] = 0
    heads["head_siblings_raw"] = heads["a2028"].fillna(0) + heads["a2029"].fillna(0)
    heads["head_siblings"] = np.where(
        heads["head_age"] <= cfg.sibling_max_age,
        heads["head_siblings_raw"],
        np.nan,
    )

    # ── Select & rename ──
    cols_present = [c for c in HEAD_COLS_MAP if c in heads.columns]
    rename_map = {k: v for k, v in HEAD_COLS_MAP.items() if k in cols_present}
    result = heads[cols_present].rename(columns=rename_map)
    result = result.drop_duplicates(subset=["hhid"], keep="first")
    logger.info("Prepared %d head records for merge.", len(result))
    return result
