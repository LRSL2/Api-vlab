#!/bin/bash
set -e

echo "🔍 Running linters..."
echo ""

echo "1️⃣  Running Ruff..."
ruff check app/ load_data.py || true

echo ""
echo "2️⃣  Checking code formatting with Black..."
black --check app/ load_data.py || {
    echo "❌ Code is not formatted. Run 'make format' to fix."
    exit 1
}

echo ""
echo "3️⃣  Checking import order with isort..."
isort --check-only app/ load_data.py || {
    echo "❌ Imports are not sorted. Run 'make format' to fix."
    exit 1
}

echo ""
echo "✅ All linter checks passed!"

