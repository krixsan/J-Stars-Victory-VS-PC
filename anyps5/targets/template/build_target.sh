#!/usr/bin/env bash
# anyPS4 Target Build Script Template
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Building anyPS4 Target: $(basename "$SCRIPT_DIR") ==="
cd "$ROOT_DIR"
./tools/win_build.sh
echo "=== Build finished ==="
