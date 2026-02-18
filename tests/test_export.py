"""Tests for the export engine (LaTeX, tables, manifest)."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from src.export.latex import _star, build_regression_table
from src.export.manifest import generate_manifest, save_manifest
from src.export.tables import export_descriptive_stats
from src.models.spec import Estimator, ModelResult, ModelSpec, RobustSE


@pytest.fixture()
def mock_model_result():
    """A minimal ModelResult for testing."""
    spec = ModelSpec(
        name="M1",
        label="Test OLS",
        estimator=Estimator.OLS,
        dep_var="debt_ratio_winsorized",
        indep_vars=["head_siblings", "head_age"],
        robust_se=RobustSE.HC1,
    )
    return ModelResult(
        spec=spec,
        n_obs=1000,
        coefficients=pd.Series({"const": 0.5, "head_siblings": -0.02, "head_age": 0.001}),
        std_errors=pd.Series({"const": 0.1, "head_siblings": 0.005, "head_age": 0.0003}),
        t_values=pd.Series({"const": 5.0, "head_siblings": -4.0, "head_age": 3.33}),
        p_values=pd.Series({"const": 0.001, "head_siblings": 0.001, "head_age": 0.02}),
        r_squared=0.15,
        adj_r_squared=0.148,
        aic=500.0,
        bic=510.0,
    )


class TestStar:
    def test_three_stars(self):
        assert _star(0.001) == "***"

    def test_two_stars(self):
        assert _star(0.03) == "**"

    def test_one_star(self):
        assert _star(0.08) == "*"

    def test_no_star(self):
        assert _star(0.15) == ""

    def test_nan(self):
        assert _star(float("nan")) == ""


class TestBuildRegressionTable:
    def test_generates_latex(self, mock_model_result):
        tex = build_regression_table([mock_model_result])
        assert r"\begin{table}" in tex
        assert r"\end{table}" in tex
        assert "M1" in tex
        assert "head\\_siblings" in tex

    def test_empty_results(self):
        tex = build_regression_table([])
        assert "No results" in tex

    def test_multiple_models(self, mock_model_result):
        tex = build_regression_table([mock_model_result, mock_model_result])
        assert tex.count("M1") >= 2


class TestManifest:
    def test_generate(self, tmp_path):
        manifest = generate_manifest(data_files=[], seed=42)
        assert manifest["random_seed"] == 42
        assert "python_version" in manifest
        assert "git_commit" in manifest
        assert "timestamp_utc" in manifest

    def test_data_checksums(self, tmp_path):
        f = tmp_path / "test.dta"
        f.write_bytes(b"fake data")
        manifest = generate_manifest(data_files=[f])
        assert manifest["data_checksums"]["test.dta"] != "FILE_NOT_FOUND"

    def test_missing_file(self, tmp_path):
        f = tmp_path / "nonexistent.dta"
        manifest = generate_manifest(data_files=[f])
        assert manifest["data_checksums"]["nonexistent.dta"] == "FILE_NOT_FOUND"

    def test_save(self, tmp_path):
        manifest = generate_manifest(data_files=[], seed=42)
        path = save_manifest(manifest, tmp_path / "manifest.json")
        assert path.exists()
        loaded = json.loads(path.read_text())
        assert loaded["random_seed"] == 42


class TestDescriptiveStats:
    def test_export(self, tmp_path, sample_analysis_df):
        csv_path, tex_path = export_descriptive_stats(
            sample_analysis_df,
            cols=["head_age", "debt_ratio_winsorized"],
            output_dir=tmp_path,
        )
        assert csv_path.exists()
        assert tex_path.exists()
        assert r"\begin{table}" in tex_path.read_text()
