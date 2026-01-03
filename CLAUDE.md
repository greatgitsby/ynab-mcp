# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that exposes YNAB (You Need A Budget) API data to LLMs. It uses the FastMCP framework to provide a resource-based interface where LLMs can query budget information.

## Architecture

### Three-Layer Design

1. **MCP Server Layer** (`src/ynab_mcp/server.py`)
   - FastMCP server instance with lifespan management
   - Resources decorated with `@mcp.resource()` that return formatted strings
   - Global `ynab_client` instance initialized during server startup via `lifespan()` context manager
   - Error handling returns error messages as strings (not exceptions) for LLM consumption

2. **API Client Layer** (`src/ynab_mcp/client.py`)
   - `YNABClient` class wraps YNAB API calls using async httpx
   - Initialized with Bearer token authentication
   - Returns parsed JSON data structures (not formatted text)
   - Raises httpx exceptions for error handling

3. **Package Initialization** (`src/ynab_mcp/__init__.py`)
   - Exports the `mcp` server instance
   - Uses absolute imports (`from ynab_mcp.client` not `from .client`) to support both module execution and MCP CLI loading

### Key Pattern: Lifespan Management

The server uses FastMCP's lifespan context manager to initialize the YNAB client once at startup and clean up on shutdown. The lifespan function **must accept an `app` parameter** even if unused (FastMCP requirement).

```python
@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    global ynab_client
    ynab_client = YNABClient(os.environ["YNAB_API_TOKEN"])
    try:
        yield
    finally:
        await ynab_client.close()

mcp = FastMCP("ynab-mcp", lifespan=lifespan)
```

### Resource vs Tool Design Decision

This server uses **resources** (not tools) because:
- YNAB API calls are read-only data fetches (GET requests)
- No side effects or mutations
- MCP resources are semantically appropriate for "context data" that LLMs can read

Use `@mcp.resource("ynab://budgets")` for new endpoints unless they perform writes/mutations.

## Development Commands

### Testing

```bash
# Quick test (loads .env automatically)
./test.sh

# Manual integration test
uv run python tests/integration_test.py

# Run server in dev mode (starts MCP inspector)
uv run mcp dev src/ynab_mcp/server.py
```

### Installation

```bash
# Install to Claude Code
uv run mcp install src/ynab_mcp/server.py --name "YNAB"
```

### Running Server Directly

```bash
# Run as Python module (for integration tests)
uv run python -m ynab_mcp.server
```

## Environment Configuration

**Required:** `YNAB_API_TOKEN` must be set before running the server.

```bash
# Option 1: .env file (recommended for development)
cp .env.example .env
# Edit .env to add token

# Option 2: Export directly
export YNAB_API_TOKEN="your_token_here"
```

Get token from: https://app.ynab.com/settings/developer

## Adding New YNAB Endpoints

1. **Add API method to `YNABClient`** (src/ynab_mcp/client.py)
   - Use async httpx calls
   - Return parsed JSON data (e.g., `data["data"]["transactions"]`)
   - Let httpx exceptions propagate

2. **Add resource handler to server** (src/ynab_mcp/server.py)
   - Decorate with `@mcp.resource("ynab://resource-name")`
   - Call `ynab_client.method()` inside try/except
   - Format output as readable text for LLM consumption
   - Catch `httpx.HTTPStatusError` for specific status codes (401, 429)
   - Return error messages as strings (not raise exceptions)

3. **Update integration test** (tests/integration_test.py)
   - Add resource read test
   - Validate response format

## Integration Test Architecture

The integration test uses MCP's stdio client/server pattern:

```python
# Server runs as subprocess
server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", "-m", "ynab_mcp.server"],
    env=os.environ.copy()
)

# Client connects via stdio streams
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.read_resource("ynab://budgets")
```

**Important:** Use `python -m ynab_mcp.server` (not `mcp dev`) in tests because `mcp dev` launches an inspector that interferes with stdio communication.

## Common Gotchas

1. **Absolute imports required**: Use `from ynab_mcp.client import YNABClient` (not `from .client`) because the server module is loaded both as a package and directly by MCP CLI.

2. **Lifespan signature**: FastMCP requires `async def lifespan(app)` with the `app` parameter, even if unused.

3. **Error handling in resources**: Resources should return error message strings (not raise exceptions) so LLMs receive readable error information.

4. **YNAB API response structure**: All YNAB API responses wrap data in `{"data": {...}}`. Always access `response["data"]` first.
