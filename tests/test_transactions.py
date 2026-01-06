"""Tests for the get_transactions MCP tool."""

import pytest

from conftest import get_budget_id, get_mcp_session


@pytest.mark.integration
async def test_transactions_all(server_params):
    """Test getting all transactions for a budget."""
    async with get_mcp_session(server_params) as session:
        budget_id = await get_budget_id(session)

        result = await session.call_tool(
            "get_transactions",
            arguments={"budget_id": budget_id}
        )
        transactions_text = result.content[0].text

        assert transactions_text and (
            "Date | Payee | Category" in transactions_text or
            "No transactions found" in transactions_text
        )


@pytest.mark.integration
async def test_transactions_uncategorized(server_params):
    """Test getting uncategorized transactions."""
    async with get_mcp_session(server_params) as session:
        budget_id = await get_budget_id(session)

        result = await session.call_tool(
            "get_transactions",
            arguments={
                "budget_id": budget_id,
                "transaction_type": "uncategorized"
            }
        )
        uncategorized_text = result.content[0].text

        # Validate we got a response (may be empty if no uncategorized transactions)
        assert uncategorized_text


@pytest.mark.integration
async def test_transactions_unapproved(server_params):
    """Test getting unapproved transactions."""
    async with get_mcp_session(server_params) as session:
        budget_id = await get_budget_id(session)

        result = await session.call_tool(
            "get_transactions",
            arguments={
                "budget_id": budget_id,
                "transaction_type": "unapproved"
            }
        )
        unapproved_text = result.content[0].text

        # Validate we got a response (may be empty if no unapproved transactions)
        assert unapproved_text


@pytest.mark.integration
async def test_transactions_invalid_type(server_params):
    """Test error handling for invalid transaction_type."""
    async with get_mcp_session(server_params) as session:
        budget_id = await get_budget_id(session)

        result = await session.call_tool(
            "get_transactions",
            arguments={
                "budget_id": budget_id,
                "transaction_type": "invalid_type"
            }
        )
        invalid_text = result.content[0].text

        assert "Error" in invalid_text


@pytest.mark.integration
async def test_transactions_invalid_budget(server_params):
    """Test error handling for invalid budget_id."""
    async with get_mcp_session(server_params) as session:
        result = await session.call_tool(
            "get_transactions",
            arguments={"budget_id": "invalid-budget-12345"}
        )
        error_text = result.content[0].text

        assert "Error" in error_text or "not found" in error_text.lower()
