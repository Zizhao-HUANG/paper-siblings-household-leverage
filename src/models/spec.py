"""
Declarative model specification.

Every regression estimated in the paper is described by a single ``ModelSpec``
instance.  The runner (:mod:`src.models.runner`) iterates over a list of specs
and produces ``ModelResult`` objects — no estimation logic lives here.

This separation means new models can be added by appending a dataclass
instance, not by writing new estimation code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Estimator(Enum):
    """Supported estimation methods."""
    OLS = auto()
    RIDGE = auto()
    RLM = auto()


class RobustSE(Enum):
    """Heteroscedasticity-consistent covariance estimators."""
    NONE = "nonrobust"
    HC0 = "HC0"
    HC1 = "HC1"   # Stata default
    HC2 = "HC2"
    HC3 = "HC3"   # Most conservative


# ---------------------------------------------------------------------------
# ModelSpec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ModelSpec:
    """
    Declarative definition of a single regression model.

    Attributes
    ----------
    name : str
        Short identifier shown in tables (e.g. ``"M1"``).
    label : str
        Human-readable description for reports.
    estimator : Estimator
        Statistical method.
    dep_var : str
        Dependent variable column name.
    indep_vars : list[str]
        Independent variable column names (excluding the constant).
    robust_se : RobustSE
        Covariance type for OLS.  Ignored by Ridge/RLM.
    scale_features : bool
        If True, standardise independent variables before estimation
        (relevant for Ridge).
    extra : dict
        Pass-through kwargs for the estimator (e.g. ``{"M": "HuberT"}``
        for RLM, or ``{"alphas": [...]}`` for RidgeCV).
    """
    name: str
    label: str
    estimator: Estimator
    dep_var: str
    indep_vars: List[str]
    robust_se: RobustSE = RobustSE.HC1
    scale_features: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# ModelResult — returned by estimation
# ---------------------------------------------------------------------------


@dataclass
class ModelResult:
    """Container for one estimated model's outputs."""
    spec: ModelSpec
    n_obs: int
    coefficients: pd.Series           # variable -> coef
    std_errors: pd.Series             # variable -> SE
    t_values: pd.Series               # variable -> t-stat
    p_values: pd.Series               # variable -> p-value
    r_squared: float
    adj_r_squared: Optional[float]    # None for Ridge
    aic: Optional[float]
    bic: Optional[float]
    raw_result: Any = None            # statsmodels RegressionResultsWrapper

    @property
    def significant_vars(self) -> List[str]:
        """Variables significant at the 5% level."""
        return self.p_values[self.p_values < 0.05].index.tolist()


# ---------------------------------------------------------------------------
# Default model battery
# ---------------------------------------------------------------------------

def get_default_specs(indep_vars: List[str]) -> List[ModelSpec]:
    """
    Return the five standard models used in the paper.

    Parameters
    ----------
    indep_vars : list[str]
        Independent variables list (usually ``cfg.independent_vars``).
    """
    return [
        ModelSpec(
            name="M1",
            label="OLS — Debt Ratio (HC1 robust SE)",
            estimator=Estimator.OLS,
            dep_var="debt_ratio_winsorized",
            indep_vars=indep_vars,
            robust_se=RobustSE.HC1,
        ),
        ModelSpec(
            name="M2",
            label="OLS — Log Debt Ratio (HC1 robust SE)",
            estimator=Estimator.OLS,
            dep_var="log_debt_ratio_winsorized",
            indep_vars=indep_vars,
            robust_se=RobustSE.HC1,
        ),
        ModelSpec(
            name="M3",
            label="RidgeCV — Debt Ratio (standardised)",
            estimator=Estimator.RIDGE,
            dep_var="debt_ratio_winsorized",
            indep_vars=indep_vars,
            scale_features=True,
        ),
        ModelSpec(
            name="M4",
            label="RidgeCV — Log Debt Ratio (standardised)",
            estimator=Estimator.RIDGE,
            dep_var="log_debt_ratio_winsorized",
            indep_vars=indep_vars,
            scale_features=True,
        ),
        ModelSpec(
            name="M5",
            label="Robust LM (Huber-T) — Debt Ratio",
            estimator=Estimator.RLM,
            dep_var="debt_ratio_winsorized",
            indep_vars=indep_vars,
            extra={"M": "HuberT"},
        ),
    ]
