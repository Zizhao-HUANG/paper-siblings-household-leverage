"""Tests for midpoint encoding tables."""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.data.midpoint_tables import get_midpoint, _normalise_var_name


class TestNormaliseVarName:
    def test_indexed_suffix(self):
        assert _normalise_var_name("c2016it_1") == "c2016it"
        assert _normalise_var_name("c2064it_6") == "c2064it"

    def test_no_suffix(self):
        assert _normalise_var_name("d1105it") == "d1105it"
        assert _normalise_var_name("b2003ait") == "b2003ait"

    def test_non_numeric_suffix(self):
        assert _normalise_var_name("c3019ait") == "c3019ait"


class TestGetMidpoint:
    def test_nan_input(self):
        assert math.isnan(get_midpoint(np.nan, "d1105it"))

    def test_map1_variable(self):
        assert get_midpoint(1, "b2003ait") == 5_000
        assert get_midpoint(11, "d3109it") == 15_000_000

    def test_map3_variable(self):
        assert get_midpoint(1, "d1105it") == 5_000
        assert get_midpoint(5, "c7060it") == 150_000

    def test_indexed_variable(self):
        assert get_midpoint(1, "c2064it_3") == 50_000
        assert get_midpoint(11, "c2064it_6") == 15_000_000

    def test_unknown_variable(self):
        result = get_midpoint(1, "nonexistent_var")
        assert math.isnan(result)

    def test_unknown_code(self):
        result = get_midpoint(999, "d1105it")
        assert math.isnan(result)

    def test_map6_sqm(self):
        """Map 6 uses square metres, not CNY."""
        assert get_midpoint(1, "c1000bbit") == 25
        assert get_midpoint(4, "c1000bbit") == 95.5
