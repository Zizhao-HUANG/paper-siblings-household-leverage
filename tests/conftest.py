"""
Shared test fixtures.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.config import Settings


@pytest.fixture()
def cfg(tmp_path):
    """Settings pointed at a temporary directory."""
    return Settings(
        data_dir=tmp_path / "data",
        output_dir=tmp_path / "outputs",
    )


@pytest.fixture()
def sample_analysis_df() -> pd.DataFrame:
    """
    Minimal analysis DataFrame for unit tests.

    Contains 20 rows with realistic value ranges.
    """
    rng = np.random.default_rng(42)
    n = 20
    return pd.DataFrame({
        "hhid": range(1, n + 1),
        "head_siblings": rng.choice([0, 1, 2, 3, np.nan], size=n),
        "debt_ratio_winsorized": rng.uniform(0, 2, size=n),
        "log_debt_ratio_winsorized": rng.uniform(-7, 1, size=n),
        "total_debt": rng.uniform(0, 500000, size=n),
        "total_assets": rng.uniform(10000, 5000000, size=n),
        "head_age": rng.integers(20, 80, size=n).astype(float),
        "head_is_male": rng.choice([0.0, 1.0], size=n),
        "head_educ": rng.integers(1, 8, size=n).astype(float),
        "head_is_married": rng.choice([0.0, 1.0], size=n),
        "head_health": rng.integers(1, 5, size=n).astype(float),
        "has_business": rng.choice([0.0, 1.0], size=n),
        "num_houses": rng.integers(0, 5, size=n).astype(float),
        "log_total_assets": rng.uniform(8, 16, size=n),
    })
