#!/usr/bin/env bash
# Launch Catalog + Data agents gateway. Must be run with catalog repo root on PYTHONPATH.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"
PYTHONPATH="${REPO_ROOT}" python3.14 -m agents --rebuild --port 8080 "$@"
