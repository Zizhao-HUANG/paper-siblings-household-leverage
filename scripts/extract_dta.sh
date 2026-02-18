#!/usr/bin/env bash
# Extract CHFS 2017 data files from compressed archives into data/raw/
#
# Supports .7z and .zip formats.  Requires 7z or unzip to be installed.
#
# Usage:
#   bash scripts/extract_dta.sh [source_directory]
#
# If source_directory is omitted, looks in the project root.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SOURCE_DIR="${1:-$PROJECT_ROOT}"
TARGET_DIR="$PROJECT_ROOT/data/raw"

mkdir -p "$TARGET_DIR"

echo "Source: $SOURCE_DIR"
echo "Target: $TARGET_DIR"

for archive in "$SOURCE_DIR"/*.7z; do
    [ -f "$archive" ] || continue
    echo "Extracting: $(basename "$archive")"
    if command -v 7z &> /dev/null; then
        7z x -o"$TARGET_DIR" -y "$archive"
    else
        echo "ERROR: 7z not found. Install with: brew install p7zip"
        exit 1
    fi
done

for archive in "$SOURCE_DIR"/*.zip; do
    [ -f "$archive" ] || continue
    echo "Extracting: $(basename "$archive")"
    unzip -o "$archive" -d "$TARGET_DIR"
done

echo "Done. Files in $TARGET_DIR:"
ls -lh "$TARGET_DIR"/*.dta 2>/dev/null || echo "(no .dta files found)"
