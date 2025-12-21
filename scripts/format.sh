#!/bin/bash
set -e

echo "✨ Formatting code..."
echo ""

echo "1️⃣  Running Black..."
black app/ load_data.py

echo ""
echo "2️⃣  Running isort..."
isort app/ load_data.py

echo ""
echo "3️⃣  Running Ruff auto-fix..."
ruff check --fix app/ load_data.py || true

echo ""
echo "✅ Code formatted successfully!"

