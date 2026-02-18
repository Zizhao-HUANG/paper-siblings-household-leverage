"""
Regression diagnostics: VIF, missing-value audit, descriptive statistics.
"""

from __future__ import annotations

import logging

import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

logger = logging.getLogger(__name__)


def calculate_vif(
    df: pd.DataFrame,
    cols: list[str],
    threshold: float = 5.0,
) -> pd.DataFrame:
    """
    Compute Variance Inflation Factors for the given columns.

    Parameters
    ----------
    df : DataFrame
        Must contain all columns in *cols* with no NaN.
    cols : list[str]
        Independent variable columns.
    threshold : float
        VIF above this is flagged.

    Returns
    -------
    DataFrame
        Columns: ``feature``, ``VIF``, ``flagged``.
    """
    x = sm.add_constant(df[cols], has_constant="add")
    vif_data = pd.DataFrame(
        {
            "feature": x.columns,
            "VIF": [variance_inflation_factor(x.values, i) for i in range(x.shape[1])],
        }
    )
    vif_data = vif_data[vif_data["feature"] != "const"].sort_values("VIF", ascending=False)
    vif_data["flagged"] = vif_data["VIF"] > threshold

    n_flagged = vif_data["flagged"].sum()
    if n_flagged:
        flagged_names = vif_data.loc[vif_data["flagged"], "feature"].tolist()
        logger.warning("VIF > %.1f for: %s", threshold, flagged_names)
    else:
        logger.info("No VIF exceeds %.1f.", threshold)

    return vif_data.reset_index(drop=True)


def missing_value_audit(
    df: pd.DataFrame,
    cols: list[str],
) -> pd.DataFrame:
    """
    Produce a missing-value summary for the specified columns.

    Returns
    -------
    DataFrame
        Columns: ``column``, ``missing_count``, ``missing_pct``.
        Only columns with at least one missing value are included.
    """
    existing = [c for c in cols if c in df.columns]
    counts = df[existing].isna().sum()
    pcts = (counts / len(df) * 100).round(2)
    result = pd.DataFrame(
        {
            "column": counts.index,
            "missing_count": counts.values,
            "missing_pct": pcts.values,
        }
    )
    result = (
        result[result["missing_count"] > 0]
        .sort_values("missing_count", ascending=False)
        .reset_index(drop=True)
    )
    return result


def descriptive_stats(
    df: pd.DataFrame,
    cols: list[str],
) -> pd.DataFrame:
    """
    Compute descriptive statistics for the given columns.

    Returns a transposed summary with mean, std, min, p25, p50, p75, max, N.
    """
    existing = [c for c in cols if c in df.columns]
    desc = df[existing].describe(percentiles=[0.25, 0.5, 0.75]).T
    desc = desc.rename(columns={"count": "N"})
    desc["N"] = desc["N"].astype(int)
    return desc
