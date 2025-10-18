"""Unit tests for GraphQL utilities."""

import pytest
from pytest_mock import MockerFixture

from src.utils.graphql import build_introspection_query, execute_graphql, validate_graphql_query


class TestValidateGraphQLQuery:
    """Tests for GraphQL query validation."""

    def test_validate_simple_query(self) -> None:
        """Test validation of simple GraphQL query."""
        query = "query { customers { id name } }"
        assert validate_graphql_query(query) is True

    def test_validate_query_with_variables(self) -> None:
        """Test validation of query with variables."""
        query = "query GetCustomer($id: ID!) { customer(id: $id) { name } }"
        assert validate_graphql_query(query) is True

    def test_validate_mutation(self) -> None:
        """Test validation of GraphQL mutation."""
        query = 'mutation { createCustomer(input: {name: "Test"}) { id } }'
        assert validate_graphql_query(query) is True

    def test_validate_query_with_fragments(self) -> None:
        """Test validation of query with fragments."""
        query = """
        query {
            customer(id: "123") {
                ...customerFields
            }
        }
        fragment customerFields on Customer {
            id
            name
        }
        """
        assert validate_graphql_query(query) is True

    def test_validate_invalid_query_missing_braces(self) -> None:
        """Test validation fails on query missing braces."""
        query = "query customers id name"  # No braces at all
        assert validate_graphql_query(query) is False

    def test_validate_empty_query(self) -> None:
        """Test validation fails on empty query."""
        assert validate_graphql_query("") is False
        assert validate_graphql_query("   ") is False

    def test_validate_query_with_comments(self) -> None:
        """Test validation accepts queries with comments."""
        query = """
        # This is a comment
        query {
            customers {
                id
            }
        }
        """
        assert validate_graphql_query(query) is True


class TestBuildIntrospectionQuery:
    """Tests for introspection query builder."""

    def test_build_basic_introspection_query(self) -> None:
        """Test building basic introspection query."""
        query = build_introspection_query()
        assert "IntrospectionQuery" in query
        assert "__schema" in query
        assert "queryType" in query
        assert "types" in query

    def test_build_introspection_query_includes_deprecated(self) -> None:
        """Test introspection query includes deprecated fields option."""
        query = build_introspection_query(include_deprecated=True)
        assert "includeDeprecated: true" in query

    def test_build_introspection_query_excludes_deprecated(self) -> None:
        """Test introspection query can exclude deprecated fields."""
        query = build_introspection_query(include_deprecated=False)
        assert "includeDeprecated: false" in query

    def test_introspection_query_has_fragments(self) -> None:
        """Test introspection query includes necessary fragments."""
        query = build_introspection_query()
        assert "fragment FullType" in query
        assert "fragment InputValue" in query
        assert "fragment TypeRef" in query


class TestExecuteGraphQL:
    """Tests for GraphQL execution function."""

    @pytest.mark.asyncio
    async def test_execute_successful_query(self, mocker: MockerFixture) -> None:
        """Test successful GraphQL query execution."""
        # Arrange
        mock_post = mocker.patch("httpx.AsyncClient.post")
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {"data": {"customers": [{"id": "1", "name": "Test"}]}}
        mock_response.raise_for_status = mocker.MagicMock()
        mock_post.return_value = mock_response

        # Act
        result = await execute_graphql(
            "query { customers { id name } }",
            api_url="https://api.test.com/graphql",
            api_key="test_key",
        )

        # Assert
        assert result == {"customers": [{"id": "1", "name": "Test"}]}
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_with_variables(self, mocker: MockerFixture) -> None:
        """Test GraphQL query execution with variables."""
        # Arrange
        mock_post = mocker.patch("httpx.AsyncClient.post")
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {"data": {"customer": {"id": "1"}}}
        mock_response.raise_for_status = mocker.MagicMock()
        mock_post.return_value = mock_response

        # Act
        result = await execute_graphql(
            "query GetCustomer($id: ID!) { customer(id: $id) { id } }",
            variables={"id": "1"},
            api_url="https://api.test.com/graphql",
            api_key="test_key",
        )

        # Assert
        assert result == {"customer": {"id": "1"}}
        call_args = mock_post.call_args
        assert call_args[1]["json"]["variables"] == {"id": "1"}

    @pytest.mark.asyncio
    async def test_execute_query_handles_graphql_errors(self, mocker: MockerFixture) -> None:
        """Test GraphQL query execution handles GraphQL errors."""
        # Arrange
        mock_post = mocker.patch("httpx.AsyncClient.post")
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {"errors": [{"message": "Field 'invalid' doesn't exist"}]}
        mock_response.raise_for_status = mocker.MagicMock()
        mock_post.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await execute_graphql(
                "query { invalid }",
                api_url="https://api.test.com/graphql",
                api_key="test_key",
            )
        assert "GraphQL errors" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_query_includes_operation_name(self, mocker: MockerFixture) -> None:
        """Test GraphQL query execution includes operation name."""
        # Arrange
        mock_post = mocker.patch("httpx.AsyncClient.post")
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {"data": {"customers": []}}
        mock_response.raise_for_status = mocker.MagicMock()
        mock_post.return_value = mock_response

        # Act
        await execute_graphql(
            "query GetCustomers { customers { id } }",
            operation_name="GetCustomers",
            api_url="https://api.test.com/graphql",
            api_key="test_key",
        )

        # Assert
        call_args = mock_post.call_args
        assert call_args[1]["json"]["operationName"] == "GetCustomers"

    @pytest.mark.asyncio
    async def test_execute_query_sets_proper_headers(self, mocker: MockerFixture) -> None:
        """Test GraphQL query execution sets proper headers."""
        # Arrange
        mock_post = mocker.patch("httpx.AsyncClient.post")
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = mocker.MagicMock()
        mock_post.return_value = mock_response

        # Act
        await execute_graphql(
            "query { test }",
            api_url="https://api.test.com/graphql",
            api_key="my_secret_key",
        )

        # Assert
        call_args = mock_post.call_args
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer my_secret_key"
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_execute_query_respects_timeout(self, mocker: MockerFixture) -> None:
        """Test GraphQL query execution respects timeout setting."""
        # Arrange
        mock_post = mocker.patch("httpx.AsyncClient.post")
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = mocker.MagicMock()
        mock_post.return_value = mock_response

        # Act
        await execute_graphql(
            "query { test }",
            api_url="https://api.test.com/graphql",
            api_key="test_key",
            timeout=45.0,
        )

        # Assert
        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 45.0
