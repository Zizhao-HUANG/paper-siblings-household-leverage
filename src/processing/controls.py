"""
Control variable construction.

Derives binary indicators and transformations from raw survey codes:
- ``head_is_male``    : 1 if head_sex == 1
- ``head_is_married`` : 1 if head_marital in {2, 3, 7}
- ``has_business``    : 1 if b2000b == 1
- ``num_houses``      : count of houses owned (c2002)
- ``log_total_assets``: ln(total_assets + 1)
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def build_controls(df: pd.DataFrame) -> None:
    """Derive all control variables in place."""

    # ---- Gender ----
    if "head_sex" in df.columns:
        df["head_is_male"] = np.where(df["head_sex"] == 1, 1.0, 0.0)
        df.loc[df["head_sex"].isna(), "head_is_male"] = np.nan
    else:
        df["head_is_male"] = np.nan
        logger.warning("'head_sex' missing — 'head_is_male' set to NaN.")

    # ---- Marital status ----
    if "head_marital" in df.columns:
        df["head_is_married"] = np.where(
            df["head_marital"].isin([2, 3, 7]), 1.0, 0.0
        )
        df.loc[df["head_marital"].isna(), "head_is_married"] = np.nan
    else:
        df["head_is_married"] = np.nan
        logger.warning("'head_marital' missing — 'head_is_married' set to NaN.")

    # ---- Business ownership ----
    if "b2000b" in df.columns:
        df["has_business"] = np.where(df["b2000b"] == 1, 1.0, 0.0)
        df.loc[df["b2000b"].isna(), "has_business"] = np.nan
    else:
        df["has_business"] = np.nan
        logger.warning("'b2000b' missing — 'has_business' set to NaN.")

    # ---- Number of houses ----
    if "c2002" in df.columns:
        df["num_houses"] = df["c2002"].fillna(0)
    else:
        df["num_houses"] = 0.0
        logger.warning("'c2002' missing — 'num_houses' set to 0.")

    # ---- Log total assets ----
    if "total_assets" in df.columns:
        df["log_total_assets"] = np.log(df["total_assets"] + 1)
    else:
        df["log_total_assets"] = np.nan
        logger.warning("'total_assets' missing — cannot compute log_total_assets.")

    logger.info("Control variables constructed.")
