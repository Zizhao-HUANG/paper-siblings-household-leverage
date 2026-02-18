"""
Model runner: iterate over ``ModelSpec`` list, estimate, collect results.

This module is the single entry point for executing the model battery.
It handles data cleaning (listwise deletion per model), dispatches to
the correct estimator, and returns a list of ``ModelResult`` objects.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src.models.ols import estimate_ols
from src.models.ridge import estimate_ridge
from src.models.rlm import estimate_rlm
from src.models.spec import Estimator, ModelResult, ModelSpec

logger = logging.getLogger(__name__)

# Dispatch table
_ESTIMATORS = {
    Estimator.OLS: estimate_ols,
    Estimator.RIDGE: estimate_ridge,
    Estimator.RLM: estimate_rlm,
}


def _prepare_data(df: pd.DataFrame, spec: ModelSpec) -> pd.DataFrame:
    """Listwise deletion + finite-value filtering for one model."""
    cols_needed = [spec.dep_var] + [c for c in spec.indep_vars if c in df.columns]
    existing = [c for c in cols_needed if c in df.columns]
    clean = df[existing].dropna().copy()

    # Remove infinite values in DV
    if spec.dep_var in clean.columns:
        clean = clean[np.isfinite(clean[spec.dep_var])]

    return pd.DataFrame(clean)


def run_model(df: pd.DataFrame, spec: ModelSpec) -> ModelResult | None:
    """
    Estimate a single model from its spec.

    Returns ``None`` if there is insufficient data.
    """
    clean = _prepare_data(df, spec)
    min_obs = len(spec.indep_vars) + 2

    if len(clean) < min_obs:
        logger.error(
            "[%s] Insufficient observations: %d (need >= %d). Skipped.",
            spec.name,
            len(clean),
            min_obs,
        )
        return None

    estimator_fn = _ESTIMATORS.get(spec.estimator)
    if estimator_fn is None:
        logger.error("[%s] Unknown estimator: %s. Skipped.", spec.name, spec.estimator)
        return None

    try:
        result = estimator_fn(clean, spec)
        return result
    except Exception:
        logger.exception("[%s] Estimation failed.", spec.name)
        return None


def run_all(
    df: pd.DataFrame,
    specs: list[ModelSpec],
) -> list[ModelResult]:
    """
    Run all models in the spec list and return successful results.

    Parameters
    ----------
    df : DataFrame
        Analysis-ready DataFrame (before listwise deletion).
    specs : list[ModelSpec]
        Declarative model definitions.

    Returns
    -------
    list[ModelResult]
        One entry per successfully estimated model.
    """
    results: list[ModelResult] = []
    for spec in specs:
        logger.info("--- Running model: %s (%s) ---", spec.name, spec.label)
        result = run_model(df, spec)
        if result is not None:
            results.append(result)
    logger.info("Completed %d/%d models.", len(results), len(specs))
    return results
