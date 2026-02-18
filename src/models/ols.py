"""
OLS estimation with heteroscedasticity-robust standard errors.

Supports HC0, HC1 (Stata default), HC2, and HC3 covariance types
via the ``ModelSpec.robust_se`` field.
"""

from __future__ import annotations

import logging
from typing import List

import pandas as pd
import statsmodels.api as sm

from src.models.spec import ModelResult, ModelSpec, RobustSE

logger = logging.getLogger(__name__)


def estimate_ols(
    df: pd.DataFrame,
    spec: ModelSpec,
) -> ModelResult:
    """
    Fit an OLS model and return a ``ModelResult``.

    Parameters
    ----------
    df : DataFrame
        Analysis-ready data (already cleaned of NaN for this model).
    spec : ModelSpec
        Declarative model definition.

    Returns
    -------
    ModelResult
    """
    y = df[spec.dep_var]
    x_cols: List[str] = [c for c in spec.indep_vars if c in df.columns]
    x = sm.add_constant(df[x_cols])

    model = sm.OLS(y, x)

    # Fit with robust standard errors if requested
    cov_type = spec.robust_se.value
    if spec.robust_se == RobustSE.NONE:
        results = model.fit()
    else:
        results = model.fit(cov_type=cov_type)

    logger.info(
        "[%s] OLS fitted: N=%d, R2=%.4f, cov_type=%s",
        spec.name, results.nobs, results.rsquared, cov_type,
    )

    return ModelResult(
        spec=spec,
        n_obs=int(results.nobs),
        coefficients=results.params,
        std_errors=results.bse,
        t_values=results.tvalues,
        p_values=results.pvalues,
        r_squared=results.rsquared,
        adj_r_squared=results.rsquared_adj,
        aic=results.aic,
        bic=results.bic,
        raw_result=results,
    )
