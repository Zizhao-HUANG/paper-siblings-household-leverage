"""
CHFS 2017 Siblings-Debt Analysis
=================================

Production-grade econometric analysis of the relationship between number of
siblings and household debt ratio in China, based on the China Household
Finance Survey (CHFS) 2017 data.

Modules
-------
config      – Centralised paths, constants, and runtime settings.
data        – Data loading (Stata .dta) and variable catalogues.
processing  – Merging, feature engineering, and cleaning pipelines.
models      – OLS, Ridge, RLM estimation with diagnostics.
utils       – Reusable helpers (midpoint encoding, VIF, logging).
webapp      – Streamlit-based interactive dashboard.
"""

__version__ = "2.0.0"
