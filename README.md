# Number of Siblings and Household Debt Ratio in China: An Empirical Analysis Based on CHFS 2017 Data

## Motivation

Household leverage in China has risen sharply over the past decade, yet microeconomic determinants — particularly those rooted in family structure — remain under-explored. While existing literature examines the effect of household size and intergenerational transfers on financial decisions, the specific role of the *sibling network* as a channel for risk-sharing, social comparison, and resource competition has received limited attention.

## Research Question

Does the number of siblings of the household head predict the household debt-to-asset ratio, after controlling for standard socio-demographic and wealth covariates?

## Data

China Household Finance Survey (CHFS), 2017 wave. The dataset provides nationally representative micro-data on household balance sheets, demographics, and family structure. Interval-coded financial variables are converted to midpoint estimates following CHFS documentation.

## Empirical Strategy

- **Dependent variable** — household debt ratio (total liabilities / total assets), winsorised at the 1st and 99th percentiles. A log-transformed specification is used as a robustness check.
- **Key regressor** — total number of siblings of the household head.
- **Controls** — age, gender, years of education, marital status, self-reported health, business ownership, number of real-estate properties, log total assets.
- **Estimators** — OLS with heteroskedasticity-consistent (HC1) standard errors; RidgeCV for regularisation; Robust Linear Model with Huber weights for outlier resistance.

## Main Finding

Across all specifications, the sibling count is positively and significantly associated with the household debt ratio. The point estimate from the baseline OLS model implies that each additional sibling corresponds to an increase of approximately **4.8 percentage points** in the winsorised debt ratio, *ceteris paribus*. The result is robust to regularisation (Ridge) and to M-estimation (RLM), and holds under the log-transformed dependent variable.

## Repository Structure

```
src/
├── data/          # Schema validation, variable construction
├── processing/    # Sample merging, feature engineering
├── models/        # OLS, Ridge, RLM specifications
├── export/        # LaTeX regression tables, summary statistics
└── webapp/        # Interactive Streamlit dashboard
```

## Replication

```bash
pip install -e ".[dev]"
python -m src.cli
```

## License

MIT
