"""YNAB API client for making authenticated requests."""

from typing import Literal

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

    async def get_transactions(
        self,
        budget_id: str,
        transaction_type: Literal["uncategorized", "unapproved"] | None = None
    ) -> list[dict]:
        """Retrieve transactions for a specific budget.

        Args:
            budget_id: The ID of the budget (supports "last-used" or "default")
            transaction_type: Optional filter - "uncategorized" or "unapproved"

        Returns:
            List of transaction dictionaries containing transaction details

        Raises:
            httpx.HTTPStatusError: If the API returns an error status code
            httpx.RequestError: If there's a network or connection error
        """
        url = f"{self.base_url}/budgets/{budget_id}/transactions"

        # Build query parameters
        params = {}
        if transaction_type is not None:
            params["type"] = transaction_type

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data["data"]["transactions"]

    async def get_categories(self, budget_id: str) -> list[dict]:
        """Retrieve all categories for a specific budget.

        Categories are returned flattened from their category groups, with
        the group name attached to each category.

        Args:
            budget_id: The ID of the budget to get categories from

        Returns:
            List of category dictionaries with category_group_name added

        Raises:
            httpx.HTTPStatusError: If the API returns an error status code
            httpx.RequestError: If there's a network or connection error
        """
        response = await self.client.get(f"{self.base_url}/budgets/{budget_id}/categories")
        response.raise_for_status()
        data = response.json()

        # Flatten category groups into a flat list with group name on each category
        categories = []
        for group in data["data"]["category_groups"]:
            for category in group.get("categories", []):
                category["category_group_name"] = group["name"]
                categories.append(category)
        return categories

    async def close(self):
        """Close the HTTP client and cleanup resources."""
        await self.client.aclose()
