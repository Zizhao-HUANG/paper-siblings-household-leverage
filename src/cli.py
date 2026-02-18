"""
Command-line entry point for the CHFS 2017 siblings-debt analysis.

Usage:
    python -m src.cli                 # default settings
    python -m src.cli --data-dir /x   # override data directory
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.config import Settings
from src.export.latex import save_latex_table
from src.export.manifest import generate_manifest, save_manifest
from src.export.tables import export_descriptive_stats, export_missing_audit, export_vif
from src.models.runner import run_all
from src.models.spec import get_default_specs
from src.processing.pipeline import run_pipeline
from src.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="chfs-analyze",
        description="CHFS 2017 Siblings-Debt Econometric Analysis Pipeline",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing .dta files (default: data/raw/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for output artifacts (default: outputs/)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the full analysis pipeline and export all artifacts."""
    args = parse_args(argv)
    setup_logging(logging.DEBUG if args.verbose else logging.INFO)

    # Build settings with overrides
    kwargs: dict = {}
    if args.data_dir:
        kwargs["data_dir"] = args.data_dir
    if args.output_dir:
        kwargs["output_dir"] = args.output_dir
    cfg = Settings(**kwargs)
    cfg.ensure_dirs()

    logger.info("=== CHFS 2017 Siblings-Debt Analysis v2.0.0 ===")
    logger.info("Data dir:   %s", cfg.data_dir)
    logger.info("Output dir: %s", cfg.output_dir)

    # ---- 1. Pipeline ----
    result = run_pipeline(cfg)
    logger.info(result.summary())

    if not result.validation_report.is_valid:
        logger.warning(
            "Validation errors detected. Proceeding with caution — "
            "check outputs/reports/ for details."
        )

    df = result.analysis_df

    # ---- 2. Export descriptive stats & diagnostics ----
    tables_dir = cfg.output_dir / "tables"
    all_vars = [cfg.independent_vars[0]] + cfg.all_control_vars
    export_descriptive_stats(df, [result.analysis_df.columns.tolist()[2]] + all_vars, tables_dir)
    export_missing_audit(df, df.columns.tolist(), tables_dir)

    # VIF (on the clean subset)
    reg_vars = [v for v in cfg.independent_vars if v in df.columns]
    export_vif(df, reg_vars, tables_dir, threshold=cfg.vif_threshold)

    # ---- 3. Run models ----
    specs = get_default_specs(cfg.independent_vars)
    model_results = run_all(df, specs)

    # ---- 4. Export regression table (LaTeX) ----
    if model_results:
        save_latex_table(
            model_results,
            output_path=tables_dir / "regression_results.tex",
            caption=("Effect of Number of Siblings on Household Debt Ratio (CHFS 2017)"),
            label="tab:regression",
            note=(
                "Standard errors in parentheses. HC1 robust standard errors used for OLS models."
            ),
        )

    # ---- 5. Save processed data ----
    csv_path = cfg.output_dir / "processed_analysis_data.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    logger.info("Processed data saved to %s", csv_path)

    # ---- 6. Reproducibility manifest ----
    manifest = generate_manifest(
        data_files=[cfg.hh_filepath, cfg.ind_filepath],
        seed=args.seed,
        extra={
            "n_models_estimated": len(model_results),
            "n_analysis_rows": result.n_analysis_rows,
            "validation_status": "PASS" if result.validation_report.is_valid else "FAIL",
        },
    )
    save_manifest(manifest, cfg.output_dir / "reports" / "reproducibility_manifest.json")

    logger.info("=== Analysis complete. All artifacts in: %s ===", cfg.output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
