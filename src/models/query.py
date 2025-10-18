"""Query request and response models."""

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request parameters for executing a GraphQL query."""

    query: str = Field(
        ...,
        min_length=1,
        description="GraphQL query string",
        examples=["query { customers { id } }"],
    )
    variables: dict[str, Any] | None = Field(
        default=None, description="Optional variables for the GraphQL query"
    )
    operation_name: str | None = Field(
        default=None, description="Optional operation name for the query"
    )


class QueryMetadata(BaseModel):
    """Metadata about query execution."""

    operation_name: str | None = Field(default=None, description="Name of the executed operation")
    execution_time_ms: float = Field(..., ge=0, description="Query execution time in milliseconds")
    record_count: int | None = Field(
        default=None, ge=0, description="Number of records returned (if applicable)"
    )
    cached: bool = Field(default=False, description="Whether the result was served from cache")


class QueryResponse(BaseModel):
    """Response from a successful GraphQL query."""

    data: dict[str, Any] = Field(..., description="Query result data")
    metadata: QueryMetadata = Field(..., description="Query execution metadata")
