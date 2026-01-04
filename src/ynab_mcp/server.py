"""YNAB MCP server implementation."""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from mcp.server.fastmcp import FastMCP
from ynab_mcp.client import YNABClient

# Suppress noisy logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("mcp").setLevel(logging.WARNING)

# Global client instance
ynab_client: YNABClient | None = None


@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    """Manage the YNAB client lifecycle."""
    global ynab_client

    # Startup: Initialize YNAB client
    api_token = os.environ.get("YNAB_API_TOKEN")
    if not api_token:
        raise ValueError(
            "YNAB_API_TOKEN environment variable is required. "
            "Get your token from: https://app.ynab.com/settings/developer"
        )

    ynab_client = YNABClient(api_token)

    try:
        yield
    finally:
        # Cleanup: Close the HTTP client
        if ynab_client:
            await ynab_client.close()


# Initialize FastMCP server with lifespan management
mcp = FastMCP("ynab-mcp", lifespan=lifespan)


def format_budgets(budgets: list[dict]) -> str:
    """Format budget list as readable text.

    Args:
        budgets: List of budget dictionaries from YNAB API

    Returns:
        Formatted string representation of budgets
    """
    if not budgets:
        return "No budgets found."

    output = ["Name | ID | Modified | Currency"]

    for budget in budgets:
        parts = [
            budget["name"],
            budget["id"],
            budget.get("last_modified_on", ""),
        ]

        if currency := budget.get("currency_format"):
            symbol = currency.get("currency_symbol", "")
            code = currency.get("iso_code", "")
            parts.append(f"{symbol}{code}")
        else:
            parts.append("")

        output.append(" | ".join(parts))

    return "\n".join(output)


def format_accounts(accounts: list[dict]) -> str:
    """Format account list as readable text.

    Args:
        accounts: List of account dictionaries from YNAB API

    Returns:
        Formatted string representation of accounts
    """
    if not accounts:
        return "No accounts found."

    output = ["Name | Type | Balance | On Budget | Closed"]

    for account in accounts:
        # Convert milliunits to currency (YNAB stores as milliunits: 1000 milliunits = $1.00)
        balance = account.get("balance", 0) / 1000.0

        parts = [
            account.get("name", "Unknown"),
            account.get("type", "Unknown"),
            f"${balance:,.2f}",
            "Yes" if account.get("on_budget", False) else "No",
            "Yes" if account.get("closed", False) else "No"
        ]

        output.append(" | ".join(parts))

    return "\n".join(output)


@mcp.resource("ynab://budgets")
async def get_budgets() -> str:
    """List all YNAB budgets for the user.

    Returns:
        Formatted string containing all budget information

    Raises:
        Returns error message string if request fails
    """
    if ynab_client is None:
        return "Error: YNAB API client not initialized"

    try:
        budgets = await ynab_client.get_budgets()
        return format_budgets(budgets)
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        if status_code == 401:
            return "Error: Invalid YNAB API token. Please check your YNAB_API_TOKEN environment variable."
        elif status_code == 429:
            return "Error: YNAB API rate limit exceeded. Please try again later."
        else:
            return f"Error: YNAB API returned status code {status_code}"
    except httpx.RequestError as e:
        return f"Error: Failed to connect to YNAB API - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.resource("ynab://budgets/{budget_id}/accounts")
async def get_accounts(budget_id: str) -> str:
    """List all accounts for a specific YNAB budget.

    Args:
        budget_id: The ID of the budget to get accounts from

    Returns:
        Formatted string containing account information
    """
    if ynab_client is None:
        return "Error: YNAB API client not initialized"

    try:
        accounts = await ynab_client.get_accounts(budget_id)
        return format_accounts(accounts)
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        if status_code == 401:
            return "Error: Invalid YNAB API token. Please check your YNAB_API_TOKEN environment variable."
        elif status_code == 404:
            return f"Error: Budget '{budget_id}' not found. Please check the budget ID."
        elif status_code == 429:
            return "Error: YNAB API rate limit exceeded. Please try again later."
        else:
            return f"Error: YNAB API returned status code {status_code}"
    except httpx.RequestError as e:
        return f"Error: Failed to connect to YNAB API - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Run the server using stdio transport
    mcp.run()
