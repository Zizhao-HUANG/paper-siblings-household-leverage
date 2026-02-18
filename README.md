# CHFS 2017 — Siblings & Household Debt Analysis

**Number of Siblings and Household Debt Ratio in China: An Empirical
Analysis Based on CHFS 2017 Data**

A production-grade econometric analysis pipeline with an interactive
Streamlit dashboard, publication-quality LaTeX export, and full
reproducibility infrastructure.

---

## Architecture

```
src/
├── config.py              # Centralised settings
├── cli.py                 # Command-line entry point
├── data/                  # Data loading, schema, validation
├── processing/            # Merge, feature engineering, pipeline
├── models/                # OLS (robust SE), Ridge, RLM + ModelSpec
├── export/                # LaTeX tables, CSV, reproducibility manifest
├── utils/                 # Logging
└── webapp/                # Streamlit dashboard (4 pages)
```

## Quick Start

### 1. Install

```bash
pip install -e ".[dev]"
```

### 2. Prepare Data

Place CHFS 2017 `.dta` files in `data/raw/`, or extract from archives:

```bash
bash scripts/extract_dta.sh
```

### 3. Run Analysis

```bash
python -m src.cli
# or
make run
```

### 4. Launch Dashboard

```bash
streamlit run src/webapp/app.py
# or
make webapp
```

### 5. Docker (full reproducibility)

```bash
docker compose up --build
```

The dashboard will be available at `http://localhost:8501`.

---

## Models

All models are defined declaratively via `ModelSpec` and executed by a
unified runner:

| ID | Estimator | Dependent Variable | Standard Errors |
|----|-----------|-------------------|-----------------|
| M1 | OLS | `debt_ratio_winsorized` | HC1 (robust) |
| M2 | OLS | `log_debt_ratio_winsorized` | HC1 (robust) |
| M3 | RidgeCV | `debt_ratio_winsorized` | — (regularised) |
| M4 | RidgeCV | `log_debt_ratio_winsorized` | — (regularised) |
| M5 | RLM | `debt_ratio_winsorized` | Huber weights |

## Data Validation

A declarative schema (`src/data/schema.py`) enforces:
- Column existence and dtype
- Nullability constraints
- Value ranges and allowed sets
- Infinity and outlier detection

The `ValidationReport` is generated before every estimation run.

## Export Engine

- **LaTeX**: Stargazer-style multi-model regression tables
- **CSV**: Descriptive statistics, VIF, missing-value audits
- **Manifest**: Git hash, data SHA-256 checksums, package versions, seed

All outputs are written to `outputs/`.

## Development

```bash
make lint       # ruff check + format
make typecheck  # mypy
make test       # pytest with coverage
make clean      # remove generated files
```

## CI Pipeline

On every push/PR to `main`:
1. **Lint** — `ruff check` + `ruff format --check`
2. **Type Check** — `mypy --ignore-missing-imports`
3. **Test** — `pytest --cov --cov-fail-under=60`

## License

MIT — see [LICENSE](LICENSE).
