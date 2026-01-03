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

# Run integration test
echo "Running integration test..."
if uv run python tests/integration_test.py; then
    echo "✓ All tests passed"
    exit 0
else
    echo "✗ Tests failed"
    exit 1
fi
