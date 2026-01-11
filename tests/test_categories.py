"""Tests for the ynab://budgets/{budget_id}/categories resource."""

import pytest

from conftest import get_budget_id, get_mcp_session


@pytest.mark.integration
async def test_categories_resource_valid(server_params):
    """Test the categories resource with valid budget_id."""
    async with get_mcp_session(server_params) as session:
        budget_id = await get_budget_id(session)

        result = await session.read_resource(
            f"ynab://budgets/{budget_id}/categories"
        )
        categories_text = result.contents[0].text

        assert categories_text and (
            "Category Group | Category | Assigned" in categories_text or
            "No categories found" in categories_text
        )


@pytest.mark.integration
async def test_categories_resource_invalid(server_params):
    """Test the categories resource with invalid budget_id."""
    async with get_mcp_session(server_params) as session:
        error_result = await session.read_resource(
            "ynab://budgets/invalid-id-12345/categories"
        )
        error_text = error_result.contents[0].text

        assert "Error" in error_text or "not found" in error_text.lower()
