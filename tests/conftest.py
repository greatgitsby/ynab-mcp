"""Pytest configuration for YNAB MCP tests."""

import os
from contextlib import asynccontextmanager

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def pytest_configure(config):
    """Validate environment before running tests."""
    if not os.environ.get("YNAB_API_TOKEN"):
        pytest.exit(
            "YNAB_API_TOKEN not set. "
            "Get your token from: https://app.ynab.com/settings/developer",
            returncode=1
        )


@pytest.fixture
def server_params():
    """Provide server parameters for tests."""
    return StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "ynab_mcp.server"],
        env=os.environ.copy(),
    )


@asynccontextmanager
async def get_mcp_session(server_params):
    """Reusable async context manager for MCP client sessions.

    Usage:
        async with get_mcp_session(server_params) as session:
            result = await session.read_resource("ynab://budgets")
    """
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def get_budget_id(session):
    """Helper to get first available budget ID from session."""
    result = await session.read_resource("ynab://budgets")
    text = result.contents[0].text

    lines = text.strip().split("\n")
    if len(lines) < 2:
        pytest.skip("No budgets available for testing")

    return lines[1].split(" | ")[1]
