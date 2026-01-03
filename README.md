# YNAB MCP Server

A Model Context Protocol (MCP) server that exposes YNAB (You Need A Budget) budget data to LLMs like Claude.

## Features

- List all YNAB budgets with details
- Secure authentication using YNAB API tokens
- Simple resource-based interface via MCP

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- A YNAB account with API access

## Setup

1. **Get your YNAB API Token**

   Visit [https://app.ynab.com/settings/developer](https://app.ynab.com/settings/developer) to generate a personal access token.

2. **Set the environment variable**

   ```bash
   export YNAB_API_TOKEN="your_token_here"
   ```

   Or create a `.env` file (see `.env.example`):
   ```bash
   cp .env.example .env
   # Edit .env and add your token
   ```

3. **Install dependencies**

   Dependencies are already configured in `pyproject.toml`. When you run the server with `uv`, it will automatically install them.

## Usage

### Running in Development Mode

```bash
export YNAB_API_TOKEN="your_token"
uv run mcp dev src/ynab_mcp/server.py
```

### Installing to Claude Code

```bash
uv run mcp install src/ynab_mcp/server.py --name "YNAB"
```

After installation, Claude Code will be able to access your YNAB budgets through the `ynab://budgets` resource.

## Testing

### Integration Test

Run the integration test to verify the server works correctly:

```bash
export YNAB_API_TOKEN="your_token"
uv run python tests/integration_test.py
```

This will:
1. Start the MCP server
2. Connect to it as a client
3. List available resources
4. Read the budgets resource
5. Validate the response

### Manual Testing with MCP Inspector

You can also test manually using the MCP inspector:

```bash
export YNAB_API_TOKEN="your_token"
uv run mcp dev src/ynab_mcp/server.py
```

## Available Resources

### `ynab://budgets`

Lists all budgets for the authenticated user.

**Returns:** Formatted text with budget details including:
- Budget name
- Budget ID
- Last modified date
- Currency information

## Project Structure

```
ynab-mcp/
├── src/
│   └── ynab_mcp/
│       ├── __init__.py     # Package initialization
│       ├── server.py       # MCP server with FastMCP
│       └── client.py       # YNAB API client
├── tests/
│   └── integration_test.py # Integration test
├── pyproject.toml          # Project configuration
├── README.md              # This file
├── .gitignore             # Git ignore patterns
└── .env.example           # Environment variable template
```

## Development

### Adding New Resources

To add more YNAB endpoints:

1. Add methods to `YNABClient` in `src/ynab_mcp/client.py`
2. Create new resource handlers in `src/ynab_mcp/server.py` using `@mcp.resource()`
3. Update tests to cover the new functionality

### Error Handling

The server handles common errors:
- Missing or invalid API token (401)
- Rate limiting (429)
- Network errors
- General API errors

## API Documentation

For more information about the YNAB API:
- [YNAB API Documentation](https://api.ynab.com/)
- [OpenAPI Specification](https://api.ynab.com/papi/open_api_spec.yaml)

## License

This project is provided as-is for use with YNAB and Claude Code.
