"""YNAB API client for making authenticated requests."""

import httpx


class YNABClient:
    """Client for interacting with the YNAB API."""

    def __init__(self, api_token: str):
        """Initialize the YNAB API client.

        Args:
            api_token: Bearer token for YNAB API authentication
        """
        self.api_token = api_token
        self.base_url = "https://api.ynab.com/v1"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=10.0,
        )

    async def get_budgets(self) -> list[dict]:
        """Retrieve all budgets for the authenticated user.

        Returns:
            List of budget dictionaries containing budget summary information

        Raises:
            httpx.HTTPStatusError: If the API returns an error status code
            httpx.RequestError: If there's a network or connection error
        """
        response = await self.client.get(f"{self.base_url}/budgets")
        response.raise_for_status()
        data = response.json()
        return data["data"]["budgets"]

    async def get_accounts(self, budget_id: str) -> list[dict]:
        """Retrieve all accounts for a specific budget.

        Args:
            budget_id: The ID of the budget to get accounts from

        Returns:
            List of account dictionaries containing account information

        Raises:
            httpx.HTTPStatusError: If the API returns an error status code
            httpx.RequestError: If there's a network or connection error
        """
        response = await self.client.get(f"{self.base_url}/budgets/{budget_id}/accounts")
        response.raise_for_status()
        data = response.json()
        return data["data"]["accounts"]

    async def close(self):
        """Close the HTTP client and cleanup resources."""
        await self.client.aclose()
