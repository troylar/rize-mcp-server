# MCP Tool Contracts

This directory contains JSON schema definitions for all MCP tools exposed by the Rize MCP Server.

## Tool Overview

### Schema Management Tools

- **`get_rize_schema`** ([tool-get-schema.json](./tool-get-schema.json))
  - Fetch complete GraphQL schema via introspection
  - Cached for 1 hour to improve performance
  - Supports force refresh and deprecated field inclusion

- **`introspect_type`** ([tool-introspect-type.json](./tool-introspect-type.json))
  - Get detailed information about a specific GraphQL type
  - Returns fields, descriptions, and type metadata
  - Useful for discovering what data you can query

### Query Execution Tools

- **`execute_custom_query`** ([tool-execute-query.json](./tool-execute-query.json))
  - Execute arbitrary GraphQL queries with variables
  - Supports filtering, pagination, and complex queries
  - Limited to 1000 records per query

## Error Handling

All tools may return these common errors:

- **`NETWORK_ERROR`**: Network connectivity issue (automatic retry with exponential backoff)
- **`RATE_LIMIT_ERROR`**: API rate limit exceeded (respects Retry-After header, max 60s wait)
- **`AUTH_ERROR`**: Invalid or expired API key
- **`GRAPHQL_ERROR`**: GraphQL query syntax or execution error

Tool-specific errors are documented in each contract file.

## Usage Example

```json
{
  "tool": "execute_custom_query",
  "arguments": {
    "query": "query GetCustomers($limit: Int!) { customers(first: $limit) { edges { node { id email } } } }",
    "variables": {
      "limit": 10
    },
    "operation_name": "GetCustomers"
  }
}
```

## Contract Validation

All contracts follow the MCP tool schema specification:
- `name`: Unique tool identifier
- `description`: Human-readable tool description for LLM context
- `inputSchema`: JSON Schema for tool parameters
- `outputSchema`: JSON Schema for tool response
- `errors`: List of possible error codes and descriptions

## Generation

These contracts are manually authored based on the data models defined in [data-model.md](../data-model.md). They are used to:

1. Document tool behavior for users and LLMs
2. Validate tool inputs at runtime (via Pydantic models)
3. Generate MCP protocol-compliant tool schemas
4. Guide test case development

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Rize API Documentation](https://docs.rize.io/)
