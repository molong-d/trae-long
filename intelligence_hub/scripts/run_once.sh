#!/bin/bash
set -e

cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Local Intelligence Hub - One-Time Run"
echo "=========================================="
echo ""

echo "[1/4] Initializing database..."
python3 "$PROJECT_ROOT/src/main.py" init-db

echo ""
echo "[2/4] Fetching data from all sources..."
python3 "$PROJECT_ROOT/src/main.py" fetch-once

echo ""
echo "[3/4] Generating digest..."
python3 "$PROJECT_ROOT/src/main.py" digest

echo ""
echo "[4/4] Current status..."
python3 "$PROJECT_ROOT/src/main.py" status

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="
