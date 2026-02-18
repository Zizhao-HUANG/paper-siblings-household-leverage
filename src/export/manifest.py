"""
Reproducibility manifest generator.

Writes a JSON manifest that uniquely identifies the exact conditions under
which the analysis was run:

- Git commit hash (or ``"dirty"`` / ``"not-a-repo"``)
- Random seed used (if any)
- SHA-256 checksums of every input data file
- Python version and key package versions
- Timestamp (UTC)
- Platform info
"""

from __future__ import annotations

import hashlib
import json
import logging
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_KEY_PACKAGES = [
    "pandas", "numpy", "statsmodels", "scipy",
    "scikit-learn", "streamlit", "plotly",
]


def _get_git_hash() -> str:
    """Return the short git hash, 'dirty', or 'not-a-repo'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return "not-a-repo"
        commit = result.stdout.strip()

        # Check for uncommitted changes
        dirty_check = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
        )
        if dirty_check.stdout.strip():
            return f"{commit}-dirty"
        return commit
    except Exception:
        return "not-a-repo"


def _sha256(filepath: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _get_package_versions() -> Dict[str, str]:
    """Return version strings for key packages."""
    versions: Dict[str, str] = {}
    for pkg in _KEY_PACKAGES:
        try:
            mod = __import__(pkg)
            versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            versions[pkg] = "not-installed"
    return versions


def generate_manifest(
    data_files: List[Path],
    seed: int | None = None,
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Build a reproducibility manifest as a dictionary.

    Parameters
    ----------
    data_files : list[Path]
        Input data files to checksum.
    seed : int or None
        Random seed used in the analysis (None if not set).
    extra : dict, optional
        Additional key-value pairs to include.

    Returns
    -------
    dict
        The manifest dictionary.
    """
    manifest: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _get_git_hash(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "random_seed": seed,
        "package_versions": _get_package_versions(),
        "data_checksums": {},
    }

    for fp in data_files:
        if fp.exists():
            manifest["data_checksums"][fp.name] = _sha256(fp)
        else:
            manifest["data_checksums"][fp.name] = "FILE_NOT_FOUND"

    if extra:
        manifest.update(extra)

    return manifest


def save_manifest(
    manifest: Dict[str, Any],
    output_path: Path,
) -> Path:
    """Write the manifest to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Reproducibility manifest saved to %s", output_path)
    return output_path
