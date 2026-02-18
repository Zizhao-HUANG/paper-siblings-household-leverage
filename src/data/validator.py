"""
Data validation engine.

Enforces the column-level schema defined in :mod:`src.data.schema` against
a concrete DataFrame and produces a structured ``ValidationReport``.

Usage
-----
    from src.data.validator import validate
    report = validate(df)
    if not report.is_valid:
        for v in report.violations:
            print(v)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd

from src.data.schema import ANALYSIS_SCHEMA, ColumnSchema, DType

logger = logging.getLogger(__name__)


@dataclass
class Violation:
    """A single schema violation."""
    column: str
    rule: str
    detail: str
    severity: str = "ERROR"  # ERROR | WARNING

    def __str__(self) -> str:
        return f"[{self.severity}] {self.column}: {self.rule} — {self.detail}"


@dataclass
class ValidationReport:
    """Aggregated validation results."""
    violations: List[Violation] = field(default_factory=list)
    rows_checked: int = 0
    columns_checked: int = 0

    @property
    def is_valid(self) -> bool:
        return not any(v.severity == "ERROR" for v in self.violations)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "WARNING")

    def summary(self) -> str:
        status = "PASS" if self.is_valid else "FAIL"
        return (
            f"Validation {status}: {self.rows_checked} rows, "
            f"{self.columns_checked} columns checked. "
            f"{self.error_count} errors, {self.warning_count} warnings."
        )


def _check_column(
    df: pd.DataFrame,
    schema: ColumnSchema,
) -> List[Violation]:
    """Validate one column against its schema."""
    violations: List[Violation] = []
    col = schema.name

    # --- Existence ---
    if col not in df.columns:
        violations.append(Violation(col, "MISSING_COLUMN", "Column not found in DataFrame."))
        return violations

    series = df[col]

    # --- Nullability ---
    null_count = int(series.isna().sum())
    if null_count > 0:
        pct = null_count / len(series) * 100
        if not schema.nullable:
            violations.append(Violation(
                col, "NOT_NULLABLE",
                f"{null_count} null values ({pct:.1f}%) in non-nullable column.",
            ))
        elif pct > 80:
            violations.append(Violation(
                col, "HIGH_MISSING",
                f"{null_count} null values ({pct:.1f}%) — may compromise analysis.",
                severity="WARNING",
            ))

    non_null = series.dropna()
    if non_null.empty:
        return violations

    # --- Range checks ---
    if schema.min_value is not None:
        below = (non_null < schema.min_value).sum()
        if below > 0:
            violations.append(Violation(
                col, "BELOW_MIN",
                f"{below} values below minimum {schema.min_value}. "
                f"Actual min = {non_null.min()}.",
            ))

    if schema.max_value is not None:
        above = (non_null > schema.max_value).sum()
        if above > 0:
            violations.append(Violation(
                col, "ABOVE_MAX",
                f"{above} values above maximum {schema.max_value}. "
                f"Actual max = {non_null.max()}.",
            ))

    # --- Allowed values (for binary / categorical) ---
    if schema.allowed_values is not None:
        invalid = ~non_null.isin(schema.allowed_values)
        n_invalid = int(invalid.sum())
        if n_invalid > 0:
            bad_vals = sorted(non_null[invalid].unique()[:5])
            violations.append(Violation(
                col, "INVALID_VALUES",
                f"{n_invalid} values outside allowed set "
                f"{sorted(schema.allowed_values)}. Examples: {bad_vals}.",
            ))

    # --- Infinity check ---
    if np.issubdtype(non_null.dtype, np.floating):
        inf_count = int(np.isinf(non_null).sum())
        if inf_count > 0:
            violations.append(Violation(
                col, "INFINITE_VALUES",
                f"{inf_count} infinite values detected.",
            ))

    return violations


def validate(
    df: pd.DataFrame,
    schema: List[ColumnSchema] | None = None,
) -> ValidationReport:
    """
    Validate a DataFrame against the analysis schema.

    Parameters
    ----------
    df : DataFrame
        The analysis-ready DataFrame to validate.
    schema : list[ColumnSchema], optional
        Custom schema; defaults to ``ANALYSIS_SCHEMA``.

    Returns
    -------
    ValidationReport
    """
    if schema is None:
        schema = ANALYSIS_SCHEMA

    report = ValidationReport(rows_checked=len(df), columns_checked=len(schema))

    for col_schema in schema:
        violations = _check_column(df, col_schema)
        report.violations.extend(violations)

    # Log summary
    if report.is_valid:
        logger.info(report.summary())
    else:
        logger.warning(report.summary())
        for v in report.violations:
            if v.severity == "ERROR":
                logger.error(str(v))
            else:
                logger.warning(str(v))

    return report
