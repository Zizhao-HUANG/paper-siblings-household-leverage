"""Tests for data schema validation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.data.schema import ColumnSchema, DType
from src.data.validator import ValidationReport, Violation, validate


class TestColumnSchema:
    def test_valid_construction(self):
        cs = ColumnSchema("test", "Test Column", DType.FLOAT, min_value=0, max_value=100)
        assert cs.name == "test"

    def test_invalid_range(self):
        with pytest.raises(ValueError, match="min_value"):
            ColumnSchema("test", "Test", DType.FLOAT, min_value=100, max_value=0)


class TestValidateNullability:
    def test_non_nullable_violation(self):
        schema = [ColumnSchema("id", "ID", DType.INT, nullable=False)]
        df = pd.DataFrame({"id": [1, np.nan, 3]})
        report = validate(df, schema)
        assert not report.is_valid
        assert any(v.rule == "NOT_NULLABLE" for v in report.violations)

    def test_nullable_passes(self):
        schema = [ColumnSchema("val", "Value", DType.FLOAT, nullable=True)]
        df = pd.DataFrame({"val": [1.0, np.nan, 3.0]})
        report = validate(df, schema)
        assert report.is_valid


class TestValidateRange:
    def test_below_min(self):
        schema = [ColumnSchema("age", "Age", DType.FLOAT, min_value=16)]
        df = pd.DataFrame({"age": [10, 20, 30]})
        report = validate(df, schema)
        assert any(v.rule == "BELOW_MIN" for v in report.violations)

    def test_above_max(self):
        schema = [ColumnSchema("health", "Health", DType.FLOAT, max_value=5)]
        df = pd.DataFrame({"health": [1, 3, 8]})
        report = validate(df, schema)
        assert any(v.rule == "ABOVE_MAX" for v in report.violations)


class TestValidateAllowedValues:
    def test_invalid_binary(self):
        schema = [ColumnSchema("flag", "Flag", DType.BINARY, allowed_values={0.0, 1.0})]
        df = pd.DataFrame({"flag": [0.0, 1.0, 2.0]})
        report = validate(df, schema)
        assert any(v.rule == "INVALID_VALUES" for v in report.violations)

    def test_valid_binary(self):
        schema = [ColumnSchema("flag", "Flag", DType.BINARY, allowed_values={0.0, 1.0})]
        df = pd.DataFrame({"flag": [0.0, 1.0, 1.0]})
        report = validate(df, schema)
        assert report.is_valid


class TestValidateMissingColumn:
    def test_missing_column(self):
        schema = [ColumnSchema("nonexistent", "Missing", DType.FLOAT)]
        df = pd.DataFrame({"other": [1, 2, 3]})
        report = validate(df, schema)
        assert any(v.rule == "MISSING_COLUMN" for v in report.violations)


class TestValidationReport:
    def test_summary(self):
        report = ValidationReport(rows_checked=100, columns_checked=5)
        assert "PASS" in report.summary()
        assert report.is_valid

    def test_with_errors(self):
        report = ValidationReport(
            violations=[Violation("col", "RULE", "detail", "ERROR")],
            rows_checked=100,
            columns_checked=5,
        )
        assert not report.is_valid
        assert report.error_count == 1
