# ============================================================
# CHFS 2017 Siblings-Debt Analysis — Reproducible Environment
# ============================================================
# Build:  docker build -t chfs-analysis .
# Run:    docker run --rm -v $(pwd)/data:/app/data chfs-analysis
# Web UI: docker compose up webapp
# ============================================================

FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System dependencies (minimal)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[dev]"

# Copy source code
COPY src/ src/
COPY tests/ tests/
COPY Makefile ./
COPY README.md ./

# Create output directories
RUN mkdir -p data/raw outputs/tables outputs/figures outputs/reports

# Default: run the full analysis pipeline
CMD ["python", "-m", "src.cli"]

# ---- Web UI target ----
FROM base AS webapp
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1
CMD ["streamlit", "run", "src/webapp/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
