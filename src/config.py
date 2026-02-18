"""
Centralised configuration for the CHFS 2017 siblings–debt analysis.

All magic numbers, file paths, and tuneable parameters are collected here so
that every other module can import a single source of truth.

Usage
-----
    from src.config import Settings
    cfg = Settings()                       # default paths
    cfg = Settings(data_dir="/my/data")    # override at runtime
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root is resolved relative to *this* file (src/config.py → root)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    """Immutable run-time settings.  Override via constructor or env vars."""

    # ---- paths ----
    data_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("CHFS_DATA_DIR", str(_PROJECT_ROOT / "data" / "raw"))
        )
    )
    output_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("CHFS_OUTPUT_DIR", str(_PROJECT_ROOT / "outputs"))
        )
    )
    hh_filename: str = "chfs2017_hh_202206.dta"
    ind_filename: str = "chfs2017_ind_202206.dta"

    # ---- analysis parameters ----
    survey_year: int = 2017
    head_min_age: int = 16
    sibling_max_age: int = 40
    winsorize_limits: tuple[float, float] = (0.01, 0.01)
    ridge_alpha_range: tuple[float, float, int] = (-6.0, 6.0, 13)
    vif_threshold: float = 5.0
    epsilon: float = 1e-9
    log_dv_constant: float = 0.001

    # ---- variable groups ----
    head_control_vars: list[str] = field(
        default_factory=lambda: [
            "head_age",
            "head_is_male",
            "head_educ",
            "head_is_married",
            "head_health",
        ]
    )
    hh_control_vars: list[str] = field(
        default_factory=lambda: ["has_business", "num_houses", "log_total_assets"]
    )

    # ---- derived helpers ----
    @property
    def hh_filepath(self) -> Path:
        return self.data_dir / self.hh_filename

    @property
    def ind_filepath(self) -> Path:
        return self.data_dir / self.ind_filename

    @property
    def all_control_vars(self) -> list[str]:
        return self.head_control_vars + self.hh_control_vars

    @property
    def independent_vars(self) -> list[str]:
        return ["head_siblings"] + self.all_control_vars

    def ensure_dirs(self) -> None:
        """Create output directories if they do not exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "tables").mkdir(exist_ok=True)
        (self.output_dir / "figures").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
