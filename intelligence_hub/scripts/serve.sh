#!/bin/bash

cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Local Intelligence Hub - Dashboard Server"
echo "=========================================="
echo "Starting dashboard at http://127.0.0.1:8765"
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

python3 "$PROJECT_ROOT/src/main.py" serve
