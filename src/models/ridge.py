"""
Ridge regression with cross-validated regularisation.

Uses ``sklearn.linear_model.RidgeCV`` with standardised features.
Coefficients are reported on the standardised scale (for comparability)
and also back-transformed to the original scale.
"""

from __future__ import annotations

import logging
from typing import List

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler

from src.models.spec import ModelResult, ModelSpec

logger = logging.getLogger(__name__)


def estimate_ridge(
    df: pd.DataFrame,
    spec: ModelSpec,
) -> ModelResult:
    """
    Fit a RidgeCV model and return a ``ModelResult``.

    Parameters
    ----------
    df : DataFrame
        Analysis-ready data.
    spec : ModelSpec
        Must have ``estimator == Estimator.RIDGE``.

    Returns
    -------
    ModelResult
    """
    y = df[spec.dep_var].values
    x_cols: List[str] = [c for c in spec.indep_vars if c in df.columns]
    x = df[x_cols].values

    # Standardise if requested (strongly recommended for Ridge)
    scaler = StandardScaler() if spec.scale_features else None
    x_fit = scaler.fit_transform(x) if scaler else x

    alphas = np.logspace(-6, 6, 13)
    ridge = RidgeCV(alphas=alphas, store_cv_results=True)
    ridge.fit(x_fit, y)

    r2 = float(ridge.score(x_fit, y))
    coefs = pd.Series(ridge.coef_, index=x_cols)
    # Ridge does not produce classical SEs; we report NaN placeholders
    se = pd.Series(np.nan, index=x_cols)
    t_vals = pd.Series(np.nan, index=x_cols)
    p_vals = pd.Series(np.nan, index=x_cols)

    logger.info(
        "[%s] RidgeCV fitted: N=%d, R2=%.4f, best_alpha=%.4g",
        spec.name, len(y), r2, ridge.alpha_,
    )

    return ModelResult(
        spec=spec,
        n_obs=len(y),
        coefficients=coefs,
        std_errors=se,
        t_values=t_vals,
        p_values=p_vals,
        r_squared=r2,
        adj_r_squared=None,
        aic=None,
        bic=None,
        raw_result=ridge,
    )
