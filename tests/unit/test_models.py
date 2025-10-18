"""Unit tests for data models."""

import pytest
from pydantic import ValidationError

from src.models.query import QueryMetadata, QueryRequest, QueryResponse


class TestQueryRequest:
    """Tests for QueryRequest model."""

    def test_query_request_with_required_fields(self) -> None:
        """Test QueryRequest with only required fields."""
        request = QueryRequest(query="query { customers { id } }")
        assert request.query == "query { customers { id } }"
        assert request.variables is None
        assert request.operation_name is None

    def test_query_request_with_all_fields(self) -> None:
        """Test QueryRequest with all fields."""
        request = QueryRequest(
            query="query GetCustomer($id: ID!) { customer(id: $id) { name } }",
            variables={"id": "123"},
            operation_name="GetCustomer",
        )
        assert request.query == "query GetCustomer($id: ID!) { customer(id: $id) { name } }"
        assert request.variables == {"id": "123"}
        assert request.operation_name == "GetCustomer"

    def test_query_request_validates_empty_query(self) -> None:
        """Test QueryRequest validation fails on empty query."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(query="")
        assert "query" in str(exc_info.value).lower()

    def test_query_request_requires_query_field(self) -> None:
        """Test QueryRequest requires query field."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest()  # type: ignore[call-arg]
        assert "query" in str(exc_info.value).lower()


class TestQueryMetadata:
    """Tests for QueryMetadata model."""

    def test_query_metadata_with_required_fields(self) -> None:
        """Test QueryMetadata with required fields."""
        metadata = QueryMetadata(execution_time_ms=123.45)
        assert metadata.execution_time_ms == 123.45
        assert metadata.operation_name is None
        assert metadata.record_count is None
        assert metadata.cached is False

    def test_query_metadata_with_all_fields(self) -> None:
        """Test QueryMetadata with all fields."""
        metadata = QueryMetadata(
            operation_name="GetCustomers",
            execution_time_ms=234.56,
            record_count=10,
            cached=True,
        )
        assert metadata.operation_name == "GetCustomers"
        assert metadata.execution_time_ms == 234.56
        assert metadata.record_count == 10
        assert metadata.cached is True

    def test_query_metadata_validates_execution_time_non_negative(self) -> None:
        """Test QueryMetadata validates execution_time_ms is non-negative."""
        with pytest.raises(ValidationError):
            QueryMetadata(execution_time_ms=-10)

    def test_query_metadata_validates_record_count_non_negative(self) -> None:
        """Test QueryMetadata validates record_count is non-negative."""
        with pytest.raises(ValidationError):
            QueryMetadata(execution_time_ms=100, record_count=-1)


class TestQueryResponse:
    """Tests for QueryResponse model."""

    def test_query_response_creation(self) -> None:
        """Test QueryResponse with data and metadata."""
        metadata = QueryMetadata(execution_time_ms=150.0, record_count=5)
        response = QueryResponse(
            data={"customers": [{"id": "1", "name": "Test"}]}, metadata=metadata
        )
        assert response.data == {"customers": [{"id": "1", "name": "Test"}]}
        assert response.metadata.execution_time_ms == 150.0
        assert response.metadata.record_count == 5

    def test_query_response_requires_all_fields(self) -> None:
        """Test QueryResponse requires both data and metadata fields."""
        with pytest.raises(ValidationError) as exc_info:
            QueryResponse(data={"test": "data"})  # type: ignore[call-arg]
        assert "metadata" in str(exc_info.value).lower()
