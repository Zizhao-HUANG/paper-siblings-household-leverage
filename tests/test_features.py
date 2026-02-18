"""Tests for feature engineering."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.processing.controls import build_controls


class TestBuildControls:
    def test_gender_derivation(self):
        df = pd.DataFrame({"head_sex": [1, 2, np.nan], "total_assets": [100, 200, 300]})
        build_controls(df)
        assert df["head_is_male"].tolist()[:2] == [1.0, 0.0]
        assert pd.isna(df["head_is_male"].iloc[2])

    def test_marital_status(self):
        df = pd.DataFrame(
            {
                "head_marital": [2, 3, 7, 1, 5, np.nan],
                "total_assets": [1] * 6,
            }
        )
        build_controls(df)
        assert df["head_is_married"].tolist()[:5] == [1.0, 1.0, 1.0, 0.0, 0.0]
        assert pd.isna(df["head_is_married"].iloc[5])

    def test_business_ownership(self):
        df = pd.DataFrame(
            {
                "b2000b": [1, 0, np.nan],
                "total_assets": [1, 2, 3],
            }
        )
        build_controls(df)
        assert df["has_business"].tolist()[:2] == [1.0, 0.0]

    def test_log_assets(self):
        df = pd.DataFrame({"total_assets": [0, 100, 1000]})
        build_controls(df)
        assert np.isclose(df["log_total_assets"].iloc[0], 0.0)
        assert df["log_total_assets"].iloc[2] > df["log_total_assets"].iloc[1]

    def test_missing_columns_handled(self):
        """All controls should be created as NaN/0 when source columns are missing."""
        df = pd.DataFrame({"total_assets": [100]})
        build_controls(df)
        assert "head_is_male" in df.columns
        assert "head_is_married" in df.columns
        assert "has_business" in df.columns
        assert "num_houses" in df.columns
