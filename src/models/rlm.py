"""
Robust Linear Model estimation (M-estimator with Huber-T norm).

Handles heavy-tailed error distributions and outliers more gracefully
than OLS.
"""

from __future__ import annotations

import logging
from typing import List

import pandas as pd
import statsmodels.api as sm

from src.models.spec import ModelResult, ModelSpec

logger = logging.getLogger(__name__)


def estimate_rlm(
    df: pd.DataFrame,
    spec: ModelSpec,
) -> ModelResult:
    """
    Fit a Robust Linear Model (Huber-T) and return a ``ModelResult``.

    Parameters
    ----------
    df : DataFrame
        Analysis-ready data.
    spec : ModelSpec
        Must have ``estimator == Estimator.RLM``.

    Returns
    -------
    ModelResult
    """
    y = df[spec.dep_var]
    x_cols: List[str] = [c for c in spec.indep_vars if c in df.columns]
    x = sm.add_constant(df[x_cols])

    norm = sm.robust.norms.HuberT()
    model = sm.RLM(y, x, M=norm)
    results = model.fit()

    # RLM does not provide R-squared directly; compute pseudo-R2
    ss_res = ((y - results.fittedvalues) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    pseudo_r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    logger.info(
        "[%s] RLM (HuberT) fitted: N=%d, pseudo-R2=%.4f",
        spec.name, int(results.nobs), pseudo_r2,
    )

    return ModelResult(
        spec=spec,
        n_obs=int(results.nobs),
        coefficients=results.params,
        std_errors=results.bse,
        t_values=results.tvalues,
        p_values=results.pvalues,
        r_squared=pseudo_r2,
        adj_r_squared=None,
        aic=None,
        bic=None,
        raw_result=results,
    )
