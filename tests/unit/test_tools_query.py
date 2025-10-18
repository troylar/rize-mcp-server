"""Unit tests for query MCP tools."""

import pytest
from pytest_mock import MockerFixture

from src.tools.query import _estimate_record_count, execute_custom_query


class TestExecuteCustomQuery:
    """Tests for execute_custom_query tool."""

    @pytest.mark.asyncio
    async def test_execute_simple_query(
        self, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test executing a simple GraphQL query."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key")
        mock_execute = mocker.patch("src.tools.query.execute_graphql")
        mock_execute.return_value = {"customers": [{"id": "1", "name": "Test"}]}

        # Act
        result = await execute_custom_query("query { customers { id name } }")

        # Assert
        assert "data" in result
        assert "metadata" in result
        assert result["data"] == {"customers": [{"id": "1", "name": "Test"}]}
        assert result["metadata"]["record_count"] == 1
        assert result["metadata"]["execution_time_ms"] >= 0

    @pytest.mark.asyncio
    async def test_execute_query_with_variables(
        self, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test executing query with variables."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key")
        mock_execute = mocker.patch("src.tools.query.execute_graphql")
        mock_execute.return_value = {"customer": {"id": "123", "name": "Test"}}

        # Act
        result = await execute_custom_query(
            "query GetCustomer($id: ID!) { customer(id: $id) { id name } }",
            variables={"id": "123"},
            operation_name="GetCustomer",
        )

        # Assert
        assert result["data"] == {"customer": {"id": "123", "name": "Test"}}
        assert result["metadata"]["operation_name"] == "GetCustomer"
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert call_args[1]["variables"] == {"id": "123"}

    @pytest.mark.asyncio
    async def test_execute_query_validates_syntax(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test query syntax validation."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key")

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid GraphQL query"):
            await execute_custom_query("invalid query without braces")

    @pytest.mark.asyncio
    async def test_execute_query_enforces_record_limit(
        self, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test query enforces 1000 record limit."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key")
        monkeypatch.setenv("MAX_RECORDS_PER_QUERY", "10")

        # Create response with > 10 records
        large_response = {"customers": {"edges": [{"node": {"id": str(i)}} for i in range(15)]}}
        mock_execute = mocker.patch("src.tools.query.execute_graphql")
        mock_execute.return_value = large_response

        # Act & Assert
        with pytest.raises(ValueError, match="exceeds maximum.*pagination"):
            await execute_custom_query("query { customers { edges { node { id } } } }")

    @pytest.mark.asyncio
    async def test_execute_query_handles_errors(
        self, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test query execution error handling."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key")
        mock_execute = mocker.patch("src.tools.query.execute_graphql")
        mock_execute.side_effect = ValueError("GraphQL errors: Field not found")

        # Act & Assert
        with pytest.raises(ValueError, match="GraphQL errors"):
            await execute_custom_query("query { invalidField }")


class TestEstimateRecordCount:
    """Tests for record count estimation."""

    def test_estimate_count_with_edges_pattern(self) -> None:
        """Test counting records in GraphQL connection pattern."""
        data = {
            "customers": {
                "edges": [
                    {"node": {"id": "1"}},
                    {"node": {"id": "2"}},
                    {"node": {"id": "3"}},
                ]
            }
        }
        count = _estimate_record_count(data)
        assert count == 3

    def test_estimate_count_with_direct_list(self) -> None:
        """Test counting records in direct list."""
        data = {"customers": [{"id": "1"}, {"id": "2"}]}
        count = _estimate_record_count(data)
        assert count == 2

    def test_estimate_count_with_nested_edges(self) -> None:
        """Test counting records with nested connection patterns."""
        data = {
            "customers": {
                "edges": [
                    {"node": {"id": "1", "orders": {"edges": [{"node": {"id": "o1"}}]}}},
                    {"node": {"id": "2"}},
                ]
            }
        }
        count = _estimate_record_count(data)
        # Counts top-level edges first (2), then nested edges (1)
        # But only counts the first level that matches
        assert count == 2  # Counts customers edges only

    def test_estimate_count_empty_data(self) -> None:
        """Test counting records with empty data."""
        assert _estimate_record_count({}) is None
        assert _estimate_record_count({"customers": []}) is None

    def test_estimate_count_no_list_data(self) -> None:
        """Test counting records with no list structures."""
        data = {"customer": {"id": "1", "name": "Test"}}
        assert _estimate_record_count(data) is None
