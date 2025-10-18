"""MCP tools for GraphQL query execution."""

import logging
import time
from typing import Any

from src.config import Settings
from src.models.query import QueryMetadata, QueryRequest, QueryResponse
from src.utils.graphql import execute_graphql, validate_graphql_query


logger = logging.getLogger(__name__)


def _get_settings() -> Settings:
    """Get Settings instance (lazy initialization for testing)."""
    import os  # noqa: PLC0415

    return Settings(_env_file=None if os.environ.get("RIZE_API_KEY") else ".env")  # type: ignore[call-arg]


async def execute_custom_query(
    query: str, variables: dict[str, Any] | None = None, operation_name: str | None = None
) -> dict[str, Any]:
    """
    Execute a custom GraphQL query against the Rize API.

    Supports variables, filtering, and pagination. Query results are limited
    to 1000 records maximum.

    Args:
        query: GraphQL query string.
        variables: Optional variables for the GraphQL query.
        operation_name: Optional operation name for the query.

    Returns:
        Dictionary containing query data and execution metadata.

    Raises:
        ValueError: If query is invalid or exceeds record limit.
    """
    # Validate query syntax
    if not validate_graphql_query(query):
        msg = "Invalid GraphQL query syntax - must contain braces"
        logger.error(msg)
        raise ValueError(msg)

    # Create request model for validation
    request = QueryRequest(query=query, variables=variables, operation_name=operation_name)
    logger.info(
        "Executing GraphQL query",
        extra={"operation_name": request.operation_name, "has_variables": bool(request.variables)},
    )

    # Execute query with timing
    settings = _get_settings()
    start_time = time.time()
    try:
        data = await execute_graphql(
            query=request.query,
            variables=request.variables,
            operation_name=request.operation_name,
            api_url=settings.rize_api_url,
            api_key=settings.rize_api_key,
            timeout=settings.http_timeout,
        )
    except Exception:
        logger.exception("GraphQL query execution failed")
        raise

    execution_time_ms = (time.time() - start_time) * 1000

    # Check for record limit (approximate check on response size)
    record_count = _estimate_record_count(data)
    if record_count and record_count > settings.max_records_per_query:
        msg = (
            f"Query result exceeds maximum of {settings.max_records_per_query} records. "
            f"Please use pagination with 'first' parameter."
        )
        logger.warning(msg, extra={"record_count": record_count})
        raise ValueError(msg)

    # Build response with metadata
    metadata = QueryMetadata(
        operation_name=request.operation_name,
        execution_time_ms=execution_time_ms,
        record_count=record_count,
        cached=False,
    )

    response = QueryResponse(data=data, metadata=metadata)

    logger.info(
        "Query executed successfully",
        extra={
            "execution_time_ms": execution_time_ms,
            "record_count": record_count,
        },
    )

    return response.model_dump()


def _estimate_record_count(data: dict[str, Any]) -> int | None:
    """
    Estimate the number of records in a GraphQL response.

    Looks for common GraphQL pagination patterns (edges, nodes, lists).

    Args:
        data: GraphQL response data.

    Returns:
        Estimated record count or None if unable to determine.
    """
    count = 0

    def count_records(obj: Any) -> None:  # noqa: ANN401
        nonlocal count
        if isinstance(obj, dict):
            # Check for GraphQL connection pattern
            if "edges" in obj and isinstance(obj["edges"], list):
                count += len(obj["edges"])
            else:
                for value in obj.values():
                    count_records(value)
        elif isinstance(obj, list) and obj and isinstance(obj[0], dict):
            # Direct list of items
            count += len(obj)

    count_records(data)
    return count if count > 0 else None
