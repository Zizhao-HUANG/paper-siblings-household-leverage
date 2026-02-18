"""
Interval-to-midpoint encoding tables for CHFS 2017.

The CHFS questionnaire records many financial variables as *interval codes*
rather than exact yuan amounts.  This module contains the complete lookup
tables, transcribed from the 2017 codebook, and a single public function
:func:`get_midpoint` that resolves any (variable, code) pair.

Design note
-----------
Each mapping dict maps ``interval_code → midpoint_yuan``.  For open-ended
upper intervals (e.g. "10,000,000 and above") the codebook convention is
``1.5 × lower_bound``.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd


# ── Mapping tables ──────────────────────────────────────────────────────────
# Keys   = interval code as recorded in the .dta file
# Values = midpoint in CNY (or sqm where noted)

_MAP_1: Dict[int, float] = {
    1: 5_000, 2: 20_000, 3: 40_000, 4: 60_000, 5: 85_000,
    6: 200_000, 7: 400_000, 8: 750_000, 9: 3_000_000,
    10: 7_500_000, 11: 15_000_000,
}
_VARS_1 = frozenset([
    "b2003ait", "b2050it", "b2059it", "b2063it", "b2080it",
    "d3109it", "d3110it", "d4103it", "d5107it", "d5108it",
    "d6100ait", "d8104it", "d9103it", "d9110ait", "k2102cit", "c3019ait",
])

_MAP_2 = _MAP_1
_VARS_2 = frozenset(["b2003bit", "b2052it"])

_MAP_3: Dict[int, float] = {
    1: 5_000, 2: 15_000, 3: 35_000, 4: 75_000, 5: 150_000,
    6: 250_000, 7: 400_000, 8: 750_000, 9: 1_500_000,
    10: 3_500_000, 11: 7_500_000,
}
_VARS_3 = frozenset([
    "b2003eit", "b2055it", "a3136it", "d3117it", "b2046it",
    "b3004bit", "b3005bit", "b3005it", "b3006ait", "b3030dit",
    "b3030eit", "b3031ait", "b3045cit", "b3056ait", "c3017cait",
    "c3019cit", "c3019eit", "c7052bit", "c7060it", "c7061it",
    "c7062it", "c8007it", "d1105it", "d2104it", "d3103it",
    "d7106hit", "d7110ait", "e1006it", "e1022it", "e3003cit",
    "e4003it", "h2004it", "c2035ait",
])

_MAP_4: Dict[int, float] = {
    1: 2_500, 2: 7_500, 3: 15_000, 4: 35_000, 5: 75_000,
    6: 125_000, 7: 175_000, 8: 250_000, 9: 400_000,
    10: 750_000, 11: 1_500_000,
}
_VARS_4 = frozenset([
    "b2093it", "a3136ait", "a3136bit", "a3137it", "b2110it",
    "d5109it", "d7106jit", "d7112it", "d9105it", "d9108it",
    "d9110bit", "k1101it", "k2208it", "f1010it", "f1031it",
])

_MAP_5: Dict[int, float] = {
    1: 500, 2: 1_500, 3: 3_500, 4: 7_500, 5: 15_000,
    6: 35_000, 7: 75_000, 8: 150_000,
}
_VARS_5 = frozenset(["b3008fit"])

_MAP_6: Dict[int, float] = {  # unit: square metres
    1: 25, 2: 60.5, 3: 80.5, 4: 95.5, 5: 110.5,
    6: 132, 7: 172, 8: 300,
}
_VARS_6 = frozenset(["c1000bbit"])

_MAP_7: Dict[int, float] = {
    1: 50_000, 2: 200_000, 3: 400_000, 4: 600_000, 5: 850_000,
    6: 1_250_000, 7: 2_250_000, 8: 4_000_000, 9: 6_000_000,
    10: 8_500_000, 11: 12_500_000, 12: 17_500_000, 13: 30_000_000,
}
_VARS_7 = frozenset(["c1000bdit"])

_MAP_8: Dict[int, float] = {
    1: 5_000, 2: 15_000, 3: 35_000, 4: 75_000, 5: 150_000,
    6: 250_000, 7: 400_000, 8: 750_000, 9: 1_500_000,
    10: 3_500_000, 11: 6_000_000, 12: 8_500_000,
    13: 12_500_000, 14: 17_500_000, 15: 30_000_000,
}
_VARS_8 = frozenset(["c2000fit"])

_MAP_9: Dict[int, float] = {
    1: 5_000, 2: 20_000, 3: 40_000, 4: 60_000, 5: 85_000,
    6: 200_000, 7: 400_000, 8: 750_000, 9: 3_000_000,
    10: 7_500_000, 11: 12_500_000, 12: 17_500_000, 13: 30_000_000,
}
_VARS_9 = frozenset(["c2013it", "c2016it"])

_MAP_10: Dict[int, float] = {
    1: 50_000, 2: 150_000, 3: 350_000, 4: 650_000, 5: 900_000,
    6: 1_250_000, 7: 1_750_000, 8: 3_500_000, 9: 6_500_000,
    10: 9_000_000, 11: 15_000_000,
}
_VARS_10 = frozenset(["c2027dit", "c2032it", "c2064it"])

_MAP_11: Dict[int, float] = {
    1: 500, 2: 2_000, 3: 4_000, 4: 6_500, 5: 9_000,
    6: 12_500, 7: 17_500, 8: 25_000, 9: 40_000, 10: 75_000,
}
_VARS_11 = frozenset(["c2045it"])

_MAP_12: Dict[int, float] = {
    1: 25_000, 2: 75_000, 3: 150_000, 4: 250_000, 5: 400_000,
    6: 650_000, 7: 900_000, 8: 1_250_000, 9: 1_750_000,
    10: 3_500_000, 11: 7_500_000,
}
_VARS_12 = frozenset(["c3002it", "c3002ait"])

_MAP_13: Dict[int, float] = {
    1: 5_000, 2: 15_000, 3: 35_000, 4: 75_000, 5: 150_000,
    6: 250_000, 7: 400_000, 8: 750_000, 9: 1_500_000,
    10: 3_500_000, 11: 7_500_000,
}
_VARS_13 = frozenset(["c3024it", "c3025it", "d4111it", "d6116it"])

_MAP_14: Dict[int, float] = {
    1: 1_000, 2: 3_500, 3: 7_500, 4: 15_000, 5: 35_000,
    6: 75_000, 7: 125_000, 8: 175_000, 9: 250_000,
    10: 400_000, 11: 750_000,
}
_VARS_14 = frozenset([
    "c8002ait", "g1017it", "g1018it", "g1019it", "g1019ait",
    "g1020it", "c8005ait", "f2006it", "f4011it",
])

_MAP_15: Dict[int, float] = {
    1: 10_000, 2: 35_000, 3: 75_000, 4: 150_000, 5: 350_000,
    6: 750_000, 7: 1_500_000, 8: 3_500_000, 9: 7_500_000,
    10: 15_000_000, 11: 30_000_000,
}
_VARS_15 = frozenset(["d8106it"])

_MAP_16: Dict[int, float] = {
    1: 5_000, 2: 15_000, 3: 35_000, 4: 75_000, 5: 150_000,
    6: 250_000, 7: 400_000, 8: 750_000, 9: 1_500_000,
    10: 3_500_000, 11: 7_500_000,
}
_VARS_16 = frozenset(["e3005cit"])

_MAP_17: Dict[int, float] = {
    1: 25, 2: 75, 3: 125, 4: 225, 5: 400,
    6: 650, 7: 1_150, 8: 2_250, 9: 4_000,
    10: 7_500, 11: 15_000, 12: 25_000, 13: 40_000, 14: 75_000,
}
_VARS_17 = frozenset(["f1005it"])

_MAP_18: Dict[int, float] = {
    1: 100, 2: 250, 3: 400,
    5: 750, 6: 1_500, 7: 2_500, 8: 4_000,
    9: 6_500, 10: 11_500, 11: 17_500, 12: 30_000,
}
_VARS_18 = frozenset(["f4005it"])

_MAP_19: Dict[int, float] = {
    1: 500, 2: 2_000, 3: 4_000,
    5: 7_500, 6: 15_000, 7: 35_000, 8: 75_000,
    9: 125_000, 10: 175_000, 11: 250_000,
    12: 400_000, 13: 750_000, 14: 1_500_000,
}
_VARS_19 = frozenset(["f4008it"])

_MAP_20: Dict[int, float] = {
    1: 250, 2: 750, 3: 1_500, 4: 3_500, 5: 7_500, 6: 15_000, 7: 30_000,
}
_VARS_20 = frozenset(["h3351it"])

_MAP_21: Dict[int, float] = {
    1: 250, 2: 750, 3: 2_000, 4: 4_000, 5: 7_500,
    6: 15_000, 7: 35_000, 8: 75_000,
}
_VARS_21 = frozenset(["h3354it", "h3356it"])

_MAP_22: Dict[int, float] = {
    1: 50, 2: 300, 3: 750, 4: 3_000, 5: 7_500, 6: 30_000, 7: 75_000,
}
_VARS_22 = frozenset(["h3367it", "h3368it", "h3369it"])

_MAP_23: Dict[int, float] = {
    1: 150, 2: 450, 3: 800, 4: 1_250, 5: 2_250,
    6: 4_500, 7: 8_000, 8: 15_000, 9: 35_000,
    10: 75_000, 11: 150_000,
}
_VARS_23 = frozenset(["g1024it"])


# Pre-build a lookup for O(1) resolution
_REGISTRY: list[tuple[frozenset[str], Dict[int, float]]] = [
    (_VARS_1, _MAP_1), (_VARS_2, _MAP_2), (_VARS_3, _MAP_3),
    (_VARS_4, _MAP_4), (_VARS_5, _MAP_5), (_VARS_6, _MAP_6),
    (_VARS_7, _MAP_7), (_VARS_8, _MAP_8), (_VARS_9, _MAP_9),
    (_VARS_10, _MAP_10), (_VARS_11, _MAP_11), (_VARS_12, _MAP_12),
    (_VARS_13, _MAP_13), (_VARS_14, _MAP_14), (_VARS_15, _MAP_15),
    (_VARS_16, _MAP_16), (_VARS_17, _MAP_17), (_VARS_18, _MAP_18),
    (_VARS_19, _MAP_19), (_VARS_20, _MAP_20), (_VARS_21, _MAP_21),
    (_VARS_22, _MAP_22), (_VARS_23, _MAP_23),
]

# Flatten into {base_var_name: map_dict} for O(1) access
_VAR_TO_MAP: Dict[str, Dict[int, float]] = {}
for _vars, _mp in _REGISTRY:
    for _v in _vars:
        _VAR_TO_MAP[_v] = _mp


# ── Public API ──────────────────────────────────────────────────────────────

def _normalise_var_name(var_name: str) -> str:
    """Strip trailing _N suffix for indexed variables like ``c2016it_1``."""
    parts = var_name.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return var_name


def get_midpoint(interval_code: float, var_name: str) -> float:
    """
    Resolve an interval code to a yuan midpoint value.

    Parameters
    ----------
    interval_code : float or int
        Raw interval code from the .dta file.
    var_name : str
        CHFS variable name, e.g. ``"c2064it_3"``.

    Returns
    -------
    float
        Estimated midpoint in CNY (or sqm for area variables).
        ``np.nan`` if the code cannot be resolved.
    """
    if pd.isna(interval_code):
        return np.nan
    base = _normalise_var_name(var_name)
    mapping = _VAR_TO_MAP.get(base)
    if mapping is None:
        return np.nan
    return mapping.get(int(interval_code), np.nan)


def get_midpoint_series(
    series: pd.Series,
    var_name: str,
) -> pd.Series:
    """Vectorised wrapper – apply :func:`get_midpoint` to a whole column."""
    return series.apply(lambda x: get_midpoint(x, var_name))
