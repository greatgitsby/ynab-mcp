"""Integration test for YNAB MCP server."""

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_budgets_resource():
    """Test the ynab://budgets resource."""
    if not os.environ.get("YNAB_API_TOKEN"):
        raise ValueError(
            "YNAB_API_TOKEN must be set. "
            "Get your token from: https://app.ynab.com/settings/developer"
        )

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "ynab_mcp.server"],
        env=os.environ.copy(),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.read_resource("ynab://budgets")
            budgets_text = result.contents[0].text

            # Validate the response
            assert budgets_text and ("Name | ID" in budgets_text or "No budgets found" in budgets_text)


async def test_accounts_resource():
    """Test the ynab://budgets/{budget_id}/accounts resource."""
    if not os.environ.get("YNAB_API_TOKEN"):
        raise ValueError(
            "YNAB_API_TOKEN must be set. "
            "Get your token from: https://app.ynab.com/settings/developer"
        )

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "ynab_mcp.server"],
        env=os.environ.copy(),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get a valid budget_id
            budgets_result = await session.read_resource("ynab://budgets")
            budgets_text = budgets_result.contents[0].text

            # Extract first budget ID from the response
            lines = budgets_text.strip().split("\n")
            if len(lines) < 2:
                print("⏭️  No budgets, skipping")
                return

            budget_id = lines[1].split(" | ")[1]

            # Test valid budget_id
            result = await session.read_resource(f"ynab://budgets/{budget_id}/accounts")
            accounts_text = result.contents[0].text
            assert accounts_text and (
                "Name | Type | Balance" in accounts_text or
                "No accounts found" in accounts_text
            )

            # Test invalid budget_id
            error_result = await session.read_resource("ynab://budgets/invalid-id-12345/accounts")
            error_text = error_result.contents[0].text
            assert "Error" in error_text or "not found" in error_text.lower()


if __name__ == "__main__":
    asyncio.run(test_budgets_resource())
    asyncio.run(test_accounts_resource())
