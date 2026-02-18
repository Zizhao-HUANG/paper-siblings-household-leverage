"""Tests for the model layer (spec, runner, individual estimators)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.models.spec import (
    Estimator,
    ModelResult,
    ModelSpec,
    RobustSE,
    get_default_specs,
)
from src.models.runner import run_model, _prepare_data


class TestModelSpec:
    def test_default_specs_count(self):
        specs = get_default_specs(["head_siblings", "head_age"])
        assert len(specs) == 5

    def test_model_names_unique(self):
        specs = get_default_specs(["head_siblings"])
        names = [s.name for s in specs]
        assert len(names) == len(set(names))

    def test_robust_se_default(self):
        spec = ModelSpec(
            name="test", label="test", estimator=Estimator.OLS,
            dep_var="y", indep_vars=["x"],
        )
        assert spec.robust_se == RobustSE.HC1

    def test_frozen_spec(self):
        spec = get_default_specs(["x"])[0]
        with pytest.raises(AttributeError):
            spec.name = "changed"


class TestPrepareData:
    def test_listwise_deletion(self):
        df = pd.DataFrame({
            "y": [1.0, 2.0, np.nan, 4.0],
            "x1": [1, 2, 3, 4],
            "x2": [10, np.nan, 30, 40],
        })
        spec = ModelSpec(
            name="T", label="T", estimator=Estimator.OLS,
            dep_var="y", indep_vars=["x1", "x2"],
        )
        clean = _prepare_data(df, spec)
        assert len(clean) == 2  # rows 0 and 3

    def test_infinite_values_removed(self):
        df = pd.DataFrame({
            "y": [1.0, np.inf, 3.0],
            "x": [1, 2, 3],
        })
        spec = ModelSpec(
            name="T", label="T", estimator=Estimator.OLS,
            dep_var="y", indep_vars=["x"],
        )
        clean = _prepare_data(df, spec)
        assert len(clean) == 2


class TestRunModel:
    def test_ols_basic(self, sample_analysis_df):
        spec = ModelSpec(
            name="T1", label="Test OLS", estimator=Estimator.OLS,
            dep_var="debt_ratio_winsorized",
            indep_vars=["head_age", "head_is_male"],
            robust_se=RobustSE.HC1,
        )
        result = run_model(sample_analysis_df, spec)
        assert result is not None
        assert result.n_obs > 0
        assert 0 <= result.r_squared <= 1

    def test_ridge_basic(self, sample_analysis_df):
        spec = ModelSpec(
            name="T2", label="Test Ridge", estimator=Estimator.RIDGE,
            dep_var="debt_ratio_winsorized",
            indep_vars=["head_age", "head_is_male"],
            scale_features=True,
        )
        result = run_model(sample_analysis_df, spec)
        assert result is not None
        assert result.adj_r_squared is None  # Ridge does not compute adj R2

    def test_rlm_basic(self, sample_analysis_df):
        spec = ModelSpec(
            name="T3", label="Test RLM", estimator=Estimator.RLM,
            dep_var="debt_ratio_winsorized",
            indep_vars=["head_age", "head_is_male"],
        )
        result = run_model(sample_analysis_df, spec)
        assert result is not None

    def test_insufficient_data(self):
        df = pd.DataFrame({"y": [1.0], "x": [2.0]})
        spec = ModelSpec(
            name="T", label="T", estimator=Estimator.OLS,
            dep_var="y", indep_vars=["x"],
        )
        result = run_model(df, spec)
        assert result is None
