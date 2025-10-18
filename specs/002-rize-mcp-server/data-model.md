# Data Model: Rize MCP Server

**Date**: 2025-10-18
**Feature**: Rize MCP Server with GraphQL Support

## Overview

This document defines all Pydantic models used in the Rize MCP Server. All models enforce strict type safety (mypy --strict), provide validation, and generate JSON schemas for MCP tool contracts.

---

## Core Configuration

### Settings

**Location**: `src/config.py`

Application configuration loaded from environment variables.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown env vars
    )

    # Rize API Configuration
    rize_api_key: str  # Required - no default
    rize_api_url: str = "https://api.rize.io/api/v1/graphql"

    # MCP Server Configuration
    mcp_server_name: str = "rize-mcp-server"
    mcp_server_version: str = "0.1.0"

    # Performance & Timeouts
    http_timeout: float = 30.0
    max_records_per_query: int = 1000
    rate_limit_max_wait: int = 60  # seconds

    # Retry Configuration
    retry_max_attempts: int = 3
    retry_base_delay: float = 1.0  # seconds
    retry_max_delay: float = 4.0   # seconds

    # Schema Caching
    schema_cache_enabled: bool = True
    schema_cache_ttl: int = 3600  # 1 hour in seconds
    schema_cache_dir: str = "/tmp/rize-mcp-cache"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
```

**Validation Rules**:
- `rize_api_key`: Required, raises `ValidationError` if missing
- `http_timeout`: Must be > 0
- `max_records_per_query`: Must be > 0
- `log_level`: Must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## GraphQL Query Models

### QueryRequest

**Location**: `src/models/query.py`

Input model for GraphQL query execution.

```python
from pydantic import BaseModel, Field
from typing import Any

class QueryRequest(BaseModel):
    """Request parameters for executing a GraphQL query."""

    query: str = Field(
        ...,
        description="GraphQL query string",
        min_length=1,
        examples=[
            "query { customers { edges { node { id email } } } }"
        ],
    )

    variables: dict[str, Any] | None = Field(
        default=None,
        description="Optional variables for the GraphQL query",
        examples=[
            {"customerId": "cus_123", "limit": 10}
        ],
    )

    operation_name: str | None = Field(
        default=None,
        description="Optional operation name for the query",
        examples=["GetCustomers"],
    )
```

**Validation Rules**:
- `query`: Non-empty string, required
- `variables`: Optional dict with string keys and any JSON-serializable values
- `operation_name`: Optional string for named operations

### QueryResponse

**Location**: `src/models/query.py`

Output model for successful GraphQL query results.

```python
from pydantic import BaseModel, Field
from typing import Any

class QueryResponse(BaseModel):
    """Response from a successful GraphQL query."""

    data: dict[str, Any] = Field(
        ...,
        description="Query result data",
    )

    metadata: QueryMetadata = Field(
        ...,
        description="Query execution metadata",
    )

class QueryMetadata(BaseModel):
    """Metadata about query execution."""

    operation_name: str | None = Field(
        default=None,
        description="Name of the executed operation",
    )

    execution_time_ms: float = Field(
        ...,
        description="Query execution time in milliseconds",
        ge=0,
    )

    record_count: int | None = Field(
        default=None,
        description="Number of records returned (if applicable)",
        ge=0,
    )

    cached: bool = Field(
        default=False,
        description="Whether the result was served from cache",
    )
```

**Validation Rules**:
- `data`: Required dict with any structure
- `execution_time_ms`: Must be >= 0
- `record_count`: Optional, must be >= 0 if provided

---

## Schema Cache Models

### SchemaCache

**Location**: `src/models/schema.py`

Model for storing and managing the GraphQL schema cache.

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class SchemaCache(BaseModel):
    """GraphQL schema cache with metadata."""

    schema: dict[str, Any] = Field(
        ...,
        description="Complete GraphQL schema from introspection",
    )

    cached_at: datetime = Field(
        ...,
        description="Timestamp when schema was cached",
    )

    ttl_seconds: int = Field(
        ...,
        description="Time-to-live in seconds",
        gt=0,
    )

    source: str = Field(
        default="api",
        description="Cache source: 'api' or 'disk'",
    )

    def is_valid(self) -> bool:
        """Check if cache is still valid based on TTL."""
        age = (datetime.now() - self.cached_at).total_seconds()
        return age < self.ttl_seconds

    def remaining_ttl(self) -> int:
        """Get remaining TTL in seconds."""
        age = (datetime.now() - self.cached_at).total_seconds()
        remaining = self.ttl_seconds - age
        return max(0, int(remaining))
```

**Validation Rules**:
- `schema`: Required dict containing GraphQL schema
- `cached_at`: Required datetime
- `ttl_seconds`: Must be > 0
- `source`: String, typically "api" or "disk"

### GraphQLType

**Location**: `src/models/schema.py`

Model representing a GraphQL type from the schema.

```python
from pydantic import BaseModel, Field
from typing import Any

class GraphQLType(BaseModel):
    """Represents a GraphQL type from schema introspection."""

    name: str = Field(
        ...,
        description="Type name",
        min_length=1,
    )

    kind: str = Field(
        ...,
        description="Type kind (OBJECT, SCALAR, ENUM, etc.)",
    )

    description: str | None = Field(
        default=None,
        description="Type description from schema",
    )

    fields: list[GraphQLField] | None = Field(
        default=None,
        description="Fields for OBJECT types",
    )

class GraphQLField(BaseModel):
    """Represents a field on a GraphQL type."""

    name: str = Field(
        ...,
        description="Field name",
        min_length=1,
    )

    type_name: str = Field(
        ...,
        description="Field type name",
        min_length=1,
    )

    description: str | None = Field(
        default=None,
        description="Field description",
    )

    is_required: bool = Field(
        default=False,
        description="Whether field is non-null",
    )

    is_list: bool = Field(
        default=False,
        description="Whether field returns a list",
    )
```

**Validation Rules**:
- `name`: Non-empty string
- `kind`: String (OBJECT, SCALAR, ENUM, INPUT_OBJECT, etc.)
- `fields`: Optional list of GraphQLField objects

---

## Error Models

### RizeError

**Location**: `src/models/errors.py`

Base error model for Rize API errors.

```python
from pydantic import BaseModel, Field
from typing import Any

class RizeError(BaseModel):
    """Base error model for Rize API errors."""

    error_type: str = Field(
        ...,
        description="Error type (network, graphql, rate_limit, auth, validation)",
    )

    message: str = Field(
        ...,
        description="Human-readable error message",
        min_length=1,
    )

    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional error context",
    )

    retryable: bool = Field(
        default=False,
        description="Whether the error is retryable",
    )

    retry_after: int | None = Field(
        default=None,
        description="Seconds to wait before retrying (for rate limits)",
        ge=0,
    )
```

**Validation Rules**:
- `error_type`: Required string
- `message`: Non-empty string
- `retry_after`: Optional, must be >= 0 if provided

### GraphQLError

**Location**: `src/models/errors.py`

Error model for GraphQL-specific errors.

```python
from pydantic import BaseModel, Field
from typing import Any

class GraphQLError(RizeError):
    """Error from GraphQL query execution."""

    error_type: str = Field(default="graphql")

    locations: list[dict[str, int]] | None = Field(
        default=None,
        description="Error locations in query (line/column)",
    )

    path: list[str | int] | None = Field(
        default=None,
        description="Path to field that caused error",
    )

    extensions: dict[str, Any] | None = Field(
        default=None,
        description="GraphQL error extensions",
    )
```

**Validation Rules**:
- Inherits from `RizeError`
- `locations`: Optional list of dicts with line/column numbers
- `path`: Optional list representing field path

### RateLimitError

**Location**: `src/models/errors.py`

Error model for rate limit responses.

```python
from pydantic import BaseModel, Field

class RateLimitError(RizeError):
    """Error for API rate limit exceeded."""

    error_type: str = Field(default="rate_limit")
    retryable: bool = Field(default=True)

    retry_after: int = Field(
        ...,
        description="Seconds to wait before retrying",
        gt=0,
    )

    limit: int | None = Field(
        default=None,
        description="Rate limit ceiling",
        gt=0,
    )

    remaining: int | None = Field(
        default=None,
        description="Remaining requests in window",
        ge=0,
    )

    reset_at: int | None = Field(
        default=None,
        description="Unix timestamp when limit resets",
        gt=0,
    )
```

**Validation Rules**:
- Inherits from `RizeError`
- `retry_after`: Required, must be > 0
- `limit`, `remaining`, `reset_at`: Optional rate limit details

---

## MCP Tool Parameter Models

### GetSchemaParams

**Location**: `src/models/tools.py`

Parameters for the `get_rize_schema` tool.

```python
from pydantic import BaseModel, Field

class GetSchemaParams(BaseModel):
    """Parameters for fetching the Rize GraphQL schema."""

    force_refresh: bool = Field(
        default=False,
        description="Force schema refresh, bypassing cache",
    )

    include_deprecated: bool = Field(
        default=False,
        description="Include deprecated fields and types",
    )
```

### IntrospectTypeParams

**Location**: `src/models/tools.py`

Parameters for the `introspect_type` tool.

```python
from pydantic import BaseModel, Field

class IntrospectTypeParams(BaseModel):
    """Parameters for introspecting a specific GraphQL type."""

    type_name: str = Field(
        ...,
        description="Name of the GraphQL type to introspect",
        min_length=1,
        examples=["Customer", "Transaction", "Account"],
    )

    include_fields: bool = Field(
        default=True,
        description="Include field details",
    )

    include_deprecated: bool = Field(
        default=False,
        description="Include deprecated fields",
    )
```

**Validation Rules**:
- `type_name`: Non-empty string, required

---

## Retry Configuration Model

### RetryConfig

**Location**: `src/models/retry.py`

Configuration for retry logic behavior.

```python
from pydantic import BaseModel, Field

class RetryConfig(BaseModel):
    """Configuration for exponential backoff retry logic."""

    max_attempts: int = Field(
        default=3,
        description="Maximum number of retry attempts",
        ge=1,
        le=10,
    )

    base_delay: float = Field(
        default=1.0,
        description="Base delay in seconds for first retry",
        gt=0,
        le=10,
    )

    max_delay: float = Field(
        default=4.0,
        description="Maximum delay between retries",
        gt=0,
        le=60,
    )

    exponential_base: float = Field(
        default=2.0,
        description="Exponential backoff multiplier",
        gt=1,
        le=10,
    )
```

**Validation Rules**:
- `max_attempts`: Between 1 and 10
- `base_delay`: Between 0 and 10 seconds
- `max_delay`: Between 0 and 60 seconds
- `exponential_base`: Between 1 and 10

---

## Model Relationships

```
Settings
  └─> Used globally for all configuration

QueryRequest
  └─> Input to all query execution tools
      └─> Returns QueryResponse
          ├─> Contains QueryMetadata
          └─> May raise RizeError hierarchy
              ├─> GraphQLError
              └─> RateLimitError

SchemaCache
  ├─> Contains schema (dict)
  └─> Methods: is_valid(), remaining_ttl()

GraphQLType
  ├─> Contains name, kind, description
  └─> May contain list[GraphQLField]
      └─> Each field has name, type_name, is_required, is_list

RetryConfig
  └─> Used by retry decorators in utils/retry.py
```

---

## Validation Summary

All models enforce:

1. **Type Safety**: Full type hints for mypy --strict
2. **Required Fields**: No optional fields without defaults
3. **Constraints**: Field validators (min_length, gt, ge, le, etc.)
4. **Serialization**: All models JSON-serializable via .dict() / .json()
5. **Documentation**: Field descriptions for auto-generated tool schemas

---

## JSON Schema Generation

Each model can generate JSON schemas for MCP tool contracts:

```python
from src.models.query import QueryRequest

schema = QueryRequest.model_json_schema()
# Used in contracts/tool-execute-query.json
```

---

**Data Model Complete**: All Pydantic models defined with full type safety and validation. Ready for contract generation and implementation.
