"""Integration test for YNAB MCP server."""

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_budgets_resource():
    """Test the ynab://budgets resource."""
    # Ensure API token is set
    if not os.environ.get("YNAB_API_TOKEN"):
        raise ValueError(
            "YNAB_API_TOKEN must be set. "
            "Get your token from: https://app.ynab.com/settings/developer"
        )

    print("Starting YNAB MCP server...")

    # Start server as subprocess (run directly with Python, not mcp dev)
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "ynab_mcp.server"],
        env=os.environ.copy(),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("Initializing connection...")
            await session.initialize()

            print("\nListing available resources...")
            resources = await session.list_resources()
            print(f"Available resources: {[r.uri for r in resources.resources]}")

            print("\nReading budgets resource...")
            result = await session.read_resource("ynab://budgets")
            budgets_text = result.contents[0].text

            print(f"\nBudgets result:\n{budgets_text}\n")

            # Validate the response
            assert budgets_text and ("Name | ID" in budgets_text or "No budgets found" in budgets_text)
            print("✅ Integration test passed!")


if __name__ == "__main__":
    asyncio.run(test_budgets_resource())
