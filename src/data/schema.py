"""
Declarative column-level schema for the CHFS analysis pipeline.

Every column that enters the regression receives a ``ColumnSchema`` that
specifies its expected dtype, nullability, value domain, and a human-readable
label.  The schema is used by :mod:`src.data.validator` to produce a typed
``ValidationReport`` before any estimation begins.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class DType(Enum):
    """Logical data types (mapped to pandas dtypes during validation)."""

    FLOAT = auto()
    INT = auto()
    CATEGORICAL = auto()
    BINARY = auto()


@dataclass(frozen=True)
class ColumnSchema:
    """Validation rules for a single DataFrame column."""

    name: str
    label: str
    dtype: DType
    nullable: bool = True
    min_value: float | None = None
    max_value: float | None = None
    allowed_values: set[float] | None = None

    def __post_init__(self) -> None:
        if (
            self.min_value is not None
            and self.max_value is not None
            and self.min_value > self.max_value
        ):
            raise ValueError(
                f"Column '{self.name}': min_value ({self.min_value}) "
                f"> max_value ({self.max_value})"
            )


# ---------------------------------------------------------------------------
# Schema definitions for the analysis-ready DataFrame
# ---------------------------------------------------------------------------

ANALYSIS_SCHEMA: list[ColumnSchema] = [
    # Identity
    ColumnSchema("hhid", "Household ID", DType.INT, nullable=False),
    # Core variables
    ColumnSchema(
        "head_siblings",
        "Number of siblings (head, age <= 40)",
        DType.FLOAT,
        nullable=True,
        min_value=0,
        max_value=30,
    ),
    ColumnSchema(
        "debt_ratio_winsorized",
        "Debt-to-asset ratio (winsorized 1%)",
        DType.FLOAT,
        nullable=True,
        min_value=0,
    ),
    ColumnSchema(
        "log_debt_ratio_winsorized",
        "Log debt-to-asset ratio",
        DType.FLOAT,
        nullable=True,
    ),
    ColumnSchema(
        "total_debt",
        "Total household debt (CNY)",
        DType.FLOAT,
        nullable=True,
        min_value=0,
    ),
    ColumnSchema(
        "total_assets",
        "Total household assets (CNY)",
        DType.FLOAT,
        nullable=True,
        min_value=0,
    ),
    # Head controls
    ColumnSchema(
        "head_age",
        "Head age (years)",
        DType.FLOAT,
        nullable=True,
        min_value=16,
        max_value=120,
    ),
    ColumnSchema(
        "head_is_male",
        "Head is male (1/0)",
        DType.BINARY,
        nullable=True,
        allowed_values={0.0, 1.0},
    ),
    ColumnSchema(
        "head_educ",
        "Head education level",
        DType.CATEGORICAL,
        nullable=True,
        min_value=1,
        max_value=9,
    ),
    ColumnSchema(
        "head_is_married",
        "Head is married (1/0)",
        DType.BINARY,
        nullable=True,
        allowed_values={0.0, 1.0},
    ),
    ColumnSchema(
        "head_health",
        "Head self-rated health (1=best .. 5=worst)",
        DType.CATEGORICAL,
        nullable=True,
        min_value=1,
        max_value=5,
    ),
    # Household controls
    ColumnSchema(
        "has_business",
        "Household owns a business (1/0)",
        DType.BINARY,
        nullable=True,
        allowed_values={0.0, 1.0},
    ),
    ColumnSchema(
        "num_houses",
        "Number of houses owned",
        DType.FLOAT,
        nullable=True,
        min_value=0,
    ),
    ColumnSchema(
        "log_total_assets",
        "Log(total_assets + 1)",
        DType.FLOAT,
        nullable=True,
        min_value=0,
    ),
]

# Quick lookup by column name
SCHEMA_MAP: dict[str, ColumnSchema] = {cs.name: cs for cs in ANALYSIS_SCHEMA}
