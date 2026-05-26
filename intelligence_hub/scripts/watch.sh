#!/bin/bash
set -e

INTERVAL="${1:-300}"

cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Local Intelligence Hub - Watch Mode"
echo "=========================================="
echo "Interval: ${INTERVAL} seconds"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

python3 "$PROJECT_ROOT/src/main.py" watch --interval "$INTERVAL"
