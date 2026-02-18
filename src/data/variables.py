"""
CHFS 2017 variable catalogues for debt and asset components.

This module centralises *every* survey variable used in the analysis so that
the data-loading and processing layers never hard-code column names.

Each catalogue entry is a ``VarSpec`` – a lightweight descriptor that bundles
the exact-value column name with its corresponding interval-value twin.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VarSpec:
    """One survey variable, optionally paired with an interval counterpart."""

    exact: str
    interval: str | None = None

    @property
    def coalesced_name(self) -> str:
        """Column name after exact / interval coalescing."""
        return f"{self.exact}_val"


# ---------------------------------------------------------------------------
# Debt variables
# ---------------------------------------------------------------------------

DEBT_BUSINESS_BANK: list[VarSpec] = [VarSpec("b3005b_2")]
DEBT_BUSINESS_PRIVATE: list[VarSpec] = [VarSpec("b3031a_2", "b3031ait_2")]

DEBT_HOUSE_BANK: list[VarSpec] = [VarSpec(f"c2064_{i}", f"c2064it_{i}") for i in range(1, 7)]
DEBT_HOUSE_OTHER: list[VarSpec] = [VarSpec(f"c3002a_{i}", f"c3002ait_{i}") for i in range(1, 7)]
DEBT_HOUSE_AGG_OTHER: list[VarSpec] = [VarSpec("c2023e", "c2023eit")]
DEBT_HOUSE_COLLATERAL: list[VarSpec] = [VarSpec("c3017ca", "c3017cait")]

DEBT_SHOP_BANK: list[VarSpec] = [VarSpec("c3019c", "c3019cit")]
DEBT_SHOP_OTHER: list[VarSpec] = [VarSpec("c3019e", "c3019eit")]

DEBT_CAR: list[VarSpec] = [VarSpec("c7060", "c7060it")]
DEBT_VEHICLE_OTHER: list[VarSpec] = [VarSpec("c7061", "c7061it")]

DEBT_DURABLE: list[VarSpec] = [VarSpec("c8007", "c8007it")]

DEBT_STOCK: list[VarSpec] = [VarSpec("d3116b")]
DEBT_FINANCE_OTHER: list[VarSpec] = [VarSpec("d9108", "d9108it")]

DEBT_EDU_BANK: list[VarSpec] = [VarSpec("e1006", "e1006it")]
DEBT_EDU_PRIVATE: list[VarSpec] = [VarSpec("e1022", "e1022it")]

DEBT_MEDICAL: list[VarSpec] = [VarSpec("e4003", "e4003it")]
DEBT_OTHER: list[VarSpec] = [VarSpec("e3003c", "e3003cit")]

ALL_DEBT_VARS: list[VarSpec] = (
    DEBT_BUSINESS_BANK
    + DEBT_BUSINESS_PRIVATE
    + DEBT_HOUSE_BANK
    + DEBT_HOUSE_OTHER
    + DEBT_HOUSE_AGG_OTHER
    + DEBT_HOUSE_COLLATERAL
    + DEBT_SHOP_BANK
    + DEBT_SHOP_OTHER
    + DEBT_CAR
    + DEBT_VEHICLE_OTHER
    + DEBT_DURABLE
    + DEBT_STOCK
    + DEBT_FINANCE_OTHER
    + DEBT_EDU_BANK
    + DEBT_EDU_PRIVATE
    + DEBT_MEDICAL
    + DEBT_OTHER
)


# ---------------------------------------------------------------------------
# Asset variables
# ---------------------------------------------------------------------------

ASSET_BUSINESS: list[VarSpec] = [VarSpec("b2003d", "b2003dit")]

ASSET_HOUSE: list[VarSpec] = [VarSpec(f"c2016_{i}", f"c2016it_{i}") for i in range(1, 7)]
ASSET_HOUSE_AGG_OTHER: list[VarSpec] = [VarSpec("c2023d", "c2023dit")]
ASSET_SHOP: list[VarSpec] = [VarSpec("c3019a", "c3019ait")]

ASSET_CAR: list[VarSpec] = [VarSpec("c7052b", "c7052bit")]
ASSET_VEHICLE_COMM: list[VarSpec] = [VarSpec("c7059")]
ASSET_VEHICLE_OTHER: list[VarSpec] = [VarSpec("c7058")]
ASSET_VEHICLE_IN_BUSINESS = VarSpec("c7062", "c7062it")

ASSET_DURABLE: list[VarSpec] = [VarSpec("c8002")]
ASSET_OTHER_NONFIN: list[VarSpec] = [VarSpec("c8005")]

ASSET_DEPOSIT_CHECKING: list[VarSpec] = [VarSpec("d1105", "d1105it")]
ASSET_DEPOSIT_SAVINGS: list[VarSpec] = [VarSpec("d2104", "d2104it")]

ASSET_STOCK_CASH: list[VarSpec] = [VarSpec("d3103", "d3103it")]
ASSET_STOCK_VALUE: list[VarSpec] = [VarSpec("d3109", "d3109it")]
ASSET_STOCK_NONPUBLIC: list[VarSpec] = [VarSpec("d3116", "d3116it")]

ASSET_FUND: list[VarSpec] = [VarSpec("d5107", "d5107it")]
ASSET_INTERNET_FINANCE: list[VarSpec] = [VarSpec("d7106h", "d7106hit")]
ASSET_OTHER_FINANCE_PROD: list[VarSpec] = [VarSpec("d7110a", "d7110ait")]

ASSET_BOND: list[VarSpec] = [VarSpec(f"d4103_{i}", f"d4103it_{i}") for i in range(1, 6)]

ASSET_DERIVATIVE: list[VarSpec] = [VarSpec("d6100a", "d6100ait")]
ASSET_NON_RMB: list[VarSpec] = [VarSpec("d8104", "d8104it")]
ASSET_GOLD: list[VarSpec] = [VarSpec("d9103", "d9103it")]
ASSET_OTHER_FIN: list[VarSpec] = [VarSpec("d9110a", "d9110ait")]

ASSET_CASH: list[VarSpec] = [VarSpec("k1101", "k1101it")]
ASSET_RECEIVABLE: list[VarSpec] = [VarSpec("k2102c", "k2102cit")]

ALL_ASSET_VARS: list[VarSpec] = (
    ASSET_BUSINESS
    + ASSET_HOUSE
    + ASSET_HOUSE_AGG_OTHER
    + ASSET_SHOP
    + ASSET_CAR
    + ASSET_VEHICLE_COMM
    + ASSET_VEHICLE_OTHER
    + ASSET_DURABLE
    + ASSET_OTHER_NONFIN
    + ASSET_DEPOSIT_CHECKING
    + ASSET_DEPOSIT_SAVINGS
    + ASSET_STOCK_CASH
    + ASSET_STOCK_VALUE
    + ASSET_STOCK_NONPUBLIC
    + ASSET_FUND
    + ASSET_INTERNET_FINANCE
    + ASSET_OTHER_FINANCE_PROD
    + ASSET_BOND
    + ASSET_DERIVATIVE
    + ASSET_NON_RMB
    + ASSET_GOLD
    + ASSET_OTHER_FIN
    + ASSET_CASH
    + ASSET_RECEIVABLE
)


# ---------------------------------------------------------------------------
# Head (respondent) variable mapping for individual → household merge
# ---------------------------------------------------------------------------

HEAD_COLS_MAP: dict[str, str] = {
    "hhid": "hhid",
    "head_age": "head_age",  # derived from a2005
    "a2003": "head_sex",  # Gender (1=Male, 2=Female)
    "a2012": "head_educ",  # Education level
    "a2024": "head_marital",  # Marital status
    "a2025b": "head_health",  # Health vs peers (1=Very Good … 5=Very Poor)
    "head_siblings": "head_siblings",
}
