"""Error models for Rize API errors."""

from typing import Any

from pydantic import BaseModel, Field


class RizeError(BaseModel):
    """Base error model for Rize API errors."""

    error_type: str = Field(..., description="Error type classification")
    message: str = Field(..., min_length=1, description="Human-readable error message")
    details: dict[str, Any] | None = Field(default=None, description="Additional error context")
    retryable: bool = Field(default=False, description="Whether the error is retryable")
    retry_after: int | None = Field(
        default=None, ge=0, description="Seconds to wait before retrying (for rate limits)"
    )


class GraphQLError(RizeError):
    """Error from GraphQL query execution."""

    error_type: str = Field(default="graphql")
    locations: list[dict[str, int]] | None = Field(
        default=None, description="Error locations in query (line/column)"
    )
    path: list[str | int] | None = Field(
        default=None, description="Path to field that caused error"
    )
    extensions: dict[str, Any] | None = Field(default=None, description="GraphQL error extensions")


class RateLimitError(RizeError):
    """Error for API rate limit exceeded."""

    error_type: str = Field(default="rate_limit")
    retryable: bool = Field(default=True)
    retry_after: int = Field(..., gt=0, description="Seconds to wait before retrying")
    limit: int | None = Field(default=None, gt=0, description="Rate limit ceiling")
    remaining: int | None = Field(default=None, ge=0, description="Remaining requests in window")
    reset_at: int | None = Field(default=None, gt=0, description="Unix timestamp when limit resets")
