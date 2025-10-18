# Quickstart Guide: Rize MCP Server

**Last Updated**: 2025-10-18

## Overview

The Rize MCP Server exposes the Rize GraphQL API to LLM agents (like Claude Desktop) through the Model Context Protocol. This guide will help you set up and use the server in under 5 minutes.

## Prerequisites

- **Python 3.11 or higher** ([download](https://www.python.org/downloads/))
- **Rize API Key** ([get one here](https://dashboard.rize.io/settings/api-keys))
- **Claude Desktop** (for MCP client) or another MCP-compatible client

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
# Install with uv (recommended)
uv pip install rize-mcp-server

# Or with pip
pip install rize-mcp-server
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/troylar/rize-mcp-server.git
cd rize-mcp-server

# Install dependencies
uv pip install -e '.[dev]'
```

## Configuration

### 1. Create Environment File

Create a `.env` file in your project directory:

```bash
# Copy the example environment file
cp .env.example .env
```

### 2. Add Your Rize API Key

Edit `.env` and add your Rize API key:

```env
# Required
RIZE_API_KEY=your_rize_api_key_here

# Optional (defaults shown)
RIZE_API_URL=https://api.rize.io/api/v1/graphql
LOG_LEVEL=INFO
SCHEMA_CACHE_ENABLED=true
SCHEMA_CACHE_TTL=3600
```

**Security Note**: Never commit your `.env` file to version control. It's already in `.gitignore`.

## Usage

### Running the Server

#### Standalone Mode

```bash
# Run the MCP server
python -m src.server

# Or use the installed command
rize-mcp

# With custom log level
rize-mcp --log-level=DEBUG
```

#### With Claude Desktop

Add to your Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "rize": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/rize-mcp-server",
        "run",
        "rize-mcp"
      ],
      "env": {
        "RIZE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Note**: Replace `/path/to/rize-mcp-server` with the actual path to your installation.

#### With Other MCP Clients

Consult your MCP client's documentation for configuration. The server follows the standard MCP protocol.

## Available Tools

Once connected, you'll have access to these tools:

### 1. Get Rize Schema

Fetch the complete GraphQL schema:

```
"What operations are available in the Rize API?"
```

Claude will call `get_rize_schema` and show you all available queries, mutations, and types.

### 2. Introspect Types

Get detailed information about a specific type:

```
"What fields are available on the Customer type?"
```

Claude will call `introspect_type` with `type_name: "Customer"`.

### 3. Execute Queries

Query Rize data naturally:

```
"Show me my first 10 customers"
```

Claude will construct and execute an appropriate GraphQL query.

### 4. Custom Queries

Execute custom GraphQL queries with variables:

```
"Execute this query: { customers(first: 5) { edges { node { id email } } } }"
```

Claude will call `execute_custom_query` with your query string.

## Example Interactions

### List Customers

**User**: "Show me my Rize customers"

**Claude**: Calls `execute_custom_query` with:
```graphql
query {
  customers(first: 10) {
    edges {
      node {
        id
        email
        firstName
        lastName
      }
    }
  }
}
```

**Result**: Displays customer list with IDs, emails, and names.

### Query Transactions

**User**: "Show me transactions from January 2024"

**Claude**: Calls `execute_custom_query` with:
```graphql
query {
  transactions(filter: { createdAt: { gte: "2024-01-01", lt: "2024-02-01" } }, first: 20) {
    edges {
      node {
        id
        amount
        description
        createdAt
      }
    }
  }
}
```

**Result**: Displays filtered transaction list.

### Discover Schema

**User**: "What data can I query from Rize?"

**Claude**: Calls `get_rize_schema`, then summarizes available types and queries.

**Result**: Lists all queryable entities (Customer, Transaction, Account, Transfer, etc.).

## Performance

- **Query Response**: <3 seconds for 95% of requests
- **Schema Introspection (cold)**: ~5-8 seconds (first time)
- **Schema Introspection (cached)**: <1 second (subsequent calls)
- **Cache Duration**: 1 hour (configurable via `SCHEMA_CACHE_TTL`)

## Error Handling

The server automatically handles common errors:

- **Network Failures**: Automatic retry with exponential backoff (3 attempts: 1s, 2s, 4s delays)
- **Rate Limits**: Respects `Retry-After` header, waits up to 60 seconds before retrying
- **Large Results**: Limits responses to 1000 records, provides pagination guidance
- **Invalid Queries**: Returns detailed GraphQL error messages

## Troubleshooting

### "API Key Not Found" Error

**Problem**: Server can't find your Rize API key.

**Solution**:
1. Check that `.env` file exists in the correct directory
2. Verify `RIZE_API_KEY=your_key_here` is set correctly
3. Restart the server after updating `.env`

### "Connection Refused" Error

**Problem**: Can't connect to Rize API.

**Solution**:
1. Check your internet connection
2. Verify `RIZE_API_URL` is correct in `.env`
3. Check if Rize API is accessible: `curl https://api.rize.io/api/v1/graphql`

### "Schema Not Loaded" Error

**Problem**: Schema hasn't been fetched yet.

**Solution**: Ask Claude "What operations are available?" to trigger schema fetch.

### High Latency

**Problem**: Queries taking longer than expected.

**Solution**:
1. Check your network connection speed
2. Reduce query complexity (fewer fields, smaller limits)
3. Use pagination for large datasets
4. Enable schema caching (should be on by default)

### Rate Limit Errors

**Problem**: "Rate limit exceeded" errors.

**Solution**:
- Server automatically handles rate limits by waiting
- Reduce query frequency if hitting limits repeatedly
- Contact Rize support to increase your rate limit

## Advanced Configuration

### Environment Variables

All available configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `RIZE_API_KEY` | Your Rize API key (required) | None |
| `RIZE_API_URL` | Rize GraphQL endpoint | `https://api.rize.io/api/v1/graphql` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `HTTP_TIMEOUT` | Request timeout in seconds | `30.0` |
| `MAX_RECORDS_PER_QUERY` | Max records per query | `1000` |
| `RATE_LIMIT_MAX_WAIT` | Max wait for rate limits (seconds) | `60` |
| `SCHEMA_CACHE_ENABLED` | Enable schema caching | `true` |
| `SCHEMA_CACHE_TTL` | Cache duration (seconds) | `3600` (1 hour) |
| `SCHEMA_CACHE_DIR` | Cache directory path | `/tmp/rize-mcp-cache` |

### Logging

Control logging detail:

```bash
# Minimal logging
LOG_LEVEL=WARNING rize-mcp

# Standard logging (default)
LOG_LEVEL=INFO rize-mcp

# Detailed logging (includes full request/response payloads)
LOG_LEVEL=DEBUG rize-mcp
```

**Note**: DEBUG level logs full payloads but automatically redacts API keys for security.

### Cache Management

Clear the schema cache:

```bash
# Remove cache directory
rm -rf /tmp/rize-mcp-cache

# Or disable caching entirely
SCHEMA_CACHE_ENABLED=false rize-mcp
```

Force schema refresh:

```
"Refresh the Rize schema, ignoring cache"
```

Claude will call `get_rize_schema` with `force_refresh: true`.

## Development

### Running Tests

```bash
# Run all tests
invoke test

# Run specific test types
invoke test-unit          # Unit tests only
invoke test-integration   # Integration tests only
invoke test-contract      # MCP protocol tests only

# Run with coverage
invoke test --coverage
```

### Code Quality

```bash
# Run all quality checks
invoke check

# Individual checks
invoke lint        # Linting
invoke format      # Auto-format code
invoke typecheck   # Type checking
```

### Pre-commit Workflow

```bash
# Before committing
invoke pre-commit

# This runs:
# 1. Auto-format code
# 2. All quality checks (lint, types, tests)
```

## Support

- **Issues**: [GitHub Issues](https://github.com/troylar/rize-mcp-server/issues)
- **Documentation**: [README](../../README.md)
- **Rize API Docs**: [https://docs.rize.io](https://docs.rize.io)
- **MCP Specification**: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)

## Next Steps

1. ✅ Install the server
2. ✅ Configure your API key
3. ✅ Connect to Claude Desktop
4. 🎉 Start querying your Rize data!

**Tip**: Try asking Claude "What can I do with Rize data?" to see example queries and workflows.

---

**Note**: This server is open source and community-maintained. Contributions welcome!
