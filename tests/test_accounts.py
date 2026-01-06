"""Tests for the ynab://budgets/{budget_id}/accounts resource."""

import pytest

from conftest import get_budget_id, get_mcp_session


@pytest.mark.integration
async def test_accounts_resource_valid(server_params):
    """Test the accounts resource with valid budget_id."""
    async with get_mcp_session(server_params) as session:
        budget_id = await get_budget_id(session)

        result = await session.read_resource(
            f"ynab://budgets/{budget_id}/accounts"
        )
        accounts_text = result.contents[0].text

        assert accounts_text and (
            "Name | Type | Balance" in accounts_text or
            "No accounts found" in accounts_text
        )


@pytest.mark.integration
async def test_accounts_resource_invalid(server_params):
    """Test the accounts resource with invalid budget_id."""
    async with get_mcp_session(server_params) as session:
        error_result = await session.read_resource(
            "ynab://budgets/invalid-id-12345/accounts"
        )
        error_text = error_result.contents[0].text

        assert "Error" in error_text or "not found" in error_text.lower()
