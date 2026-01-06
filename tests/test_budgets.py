"""Tests for the ynab://budgets resource."""

import pytest

from conftest import get_mcp_session


@pytest.mark.integration
async def test_budgets_resource(server_params):
    """Test the ynab://budgets resource."""
    async with get_mcp_session(server_params) as session:
        result = await session.read_resource("ynab://budgets")
        budgets_text = result.contents[0].text

        assert budgets_text and (
            "Name | ID" in budgets_text or
            "No budgets found" in budgets_text
        )
