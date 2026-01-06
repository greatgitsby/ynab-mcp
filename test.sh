#!/usr/bin/env bash
set -euo pipefail

# Load .env if exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Check for API token
if [ -z "${YNAB_API_TOKEN:-}" ]; then
    echo "Error: YNAB_API_TOKEN not set"
    echo "Get token: https://app.ynab.com/settings/developer"
    exit 1
fi

# Run pytest with parallel execution
# Each test manages its own server subprocess, so parallel execution is safe
echo "Running integration tests..."
if uv run pytest tests/ -n auto --tb=short -v; then
    echo "✓ All tests passed"
    exit 0
else
    echo "✗ Tests failed"
    exit 1
fi
