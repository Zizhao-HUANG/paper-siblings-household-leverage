"""Tests for the merge step of the processing pipeline."""

from __future__ import annotations

import pandas as pd
import pytest

from src.processing.merge import merge_head_into_household


class TestMerge:
    def test_basic_merge(self):
        hh = pd.DataFrame({"hhid": [1, 2, 3], "income": [100, 200, 300]})
        head = pd.DataFrame({"hhid": [1, 2, 3], "head_age": [30, 40, 50]})
        result = merge_head_into_household(hh, head)
        assert len(result) == 3
        assert "head_age" in result.columns

    def test_unmatched_households(self):
        hh = pd.DataFrame({"hhid": [1, 2, 3], "income": [100, 200, 300]})
        head = pd.DataFrame({"hhid": [1, 2], "head_age": [30, 40]})
        result = merge_head_into_household(hh, head)
        assert len(result) == 3
        assert pd.isna(result.loc[result["hhid"] == 3, "head_age"].iloc[0])

    def test_row_count_guard(self):
        """Duplicate keys in head should raise ValueError."""
        hh = pd.DataFrame({"hhid": [1, 2], "income": [100, 200]})
        head = pd.DataFrame({"hhid": [1, 1, 2], "head_age": [30, 31, 40]})
        with pytest.raises(ValueError, match="row count"):
            merge_head_into_household(hh, head)
