"""Unit tests for error models."""

import pytest
from pydantic import ValidationError

from src.models.errors import GraphQLError, RateLimitError, RizeError


class TestRizeError:
    """Tests for RizeError base model."""

    def test_rize_error_creation(self) -> None:
        """Test RizeError model can be created with required fields."""
        # Act
        error = RizeError(
            error_type="network",
            message="Connection failed",
        )

        # Assert
        assert error.error_type == "network"
        assert error.message == "Connection failed"
        assert error.details is None
        assert error.retryable is False
        assert error.retry_after is None

    def test_rize_error_with_details(self) -> None:
        """Test RizeError with optional details field."""
        # Act
        error = RizeError(
            error_type="validation",
            message="Invalid input",
            details={"field": "email", "issue": "invalid format"},
            retryable=False,
        )

        # Assert
        assert error.details == {"field": "email", "issue": "invalid format"}

    def test_rize_error_requires_message(self) -> None:
        """Test RizeError validation fails without message."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RizeError(error_type="test")  # type: ignore[call-arg]

        assert "message" in str(exc_info.value).lower()

    def test_rize_error_message_min_length(self) -> None:
        """Test RizeError validation fails with empty message."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RizeError(error_type="test", message="")

        assert "message" in str(exc_info.value).lower()

    def test_rize_error_retry_after_validation(self) -> None:
        """Test RizeError validates retry_after is non-negative."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RizeError(
                error_type="rate_limit",
                message="Rate limit exceeded",
                retry_after=-5,
            )

        assert "retry_after" in str(exc_info.value).lower()


class TestGraphQLError:
    """Tests for GraphQLError model."""

    def test_graphql_error_creation(self) -> None:
        """Test GraphQLError inherits from RizeError."""
        # Act
        error = GraphQLError(
            message="Syntax error in query",
        )

        # Assert
        assert isinstance(error, RizeError)
        assert error.error_type == "graphql"
        assert error.message == "Syntax error in query"
        assert error.locations is None
        assert error.path is None
        assert error.extensions is None

    def test_graphql_error_with_location(self) -> None:
        """Test GraphQLError with location information."""
        # Act
        error = GraphQLError(
            message="Field not found",
            locations=[{"line": 5, "column": 12}],
            path=["customers", 0, "email"],
        )

        # Assert
        assert error.locations == [{"line": 5, "column": 12}]
        assert error.path == ["customers", 0, "email"]

    def test_graphql_error_with_extensions(self) -> None:
        """Test GraphQLError with extension metadata."""
        # Act
        error = GraphQLError(
            message="Authorization failed",
            extensions={"code": "UNAUTHENTICATED", "timestamp": "2024-01-01T00:00:00Z"},
        )

        # Assert
        assert error.extensions == {
            "code": "UNAUTHENTICATED",
            "timestamp": "2024-01-01T00:00:00Z",
        }

    def test_graphql_error_default_type(self) -> None:
        """Test GraphQLError has default error_type of 'graphql'."""
        # Act
        error = GraphQLError(message="Test error")

        # Assert
        assert error.error_type == "graphql"


class TestRateLimitError:
    """Tests for RateLimitError model."""

    def test_rate_limit_error_creation(self) -> None:
        """Test RateLimitError inherits from RizeError."""
        # Act
        error = RateLimitError(
            message="Too many requests",
            retry_after=60,
        )

        # Assert
        assert isinstance(error, RizeError)
        assert error.error_type == "rate_limit"
        assert error.message == "Too many requests"
        assert error.retryable is True
        assert error.retry_after == 60

    def test_rate_limit_error_requires_retry_after(self) -> None:
        """Test RateLimitError requires retry_after field."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RateLimitError(message="Rate limit exceeded")  # type: ignore[call-arg]

        assert "retry_after" in str(exc_info.value).lower()

    def test_rate_limit_error_retry_after_validation(self) -> None:
        """Test RateLimitError validates retry_after is positive."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RateLimitError(
                message="Rate limit exceeded",
                retry_after=0,  # Must be > 0
            )

        assert "retry_after" in str(exc_info.value).lower()

    def test_rate_limit_error_with_metadata(self) -> None:
        """Test RateLimitError with optional rate limit metadata."""
        # Act
        error = RateLimitError(
            message="Rate limit exceeded",
            retry_after=30,
            limit=100,
            remaining=0,
            reset_at=1704067200,
        )

        # Assert
        assert error.limit == 100
        assert error.remaining == 0
        assert error.reset_at == 1704067200

    def test_rate_limit_error_default_retryable(self) -> None:
        """Test RateLimitError has default retryable=True."""
        # Act
        error = RateLimitError(
            message="Rate limit exceeded",
            retry_after=45,
        )

        # Assert
        assert error.retryable is True

    def test_rate_limit_error_validates_positive_values(self) -> None:
        """Test RateLimitError validates limit, remaining, and reset_at are positive."""
        # limit must be positive
        with pytest.raises(ValidationError):
            RateLimitError(
                message="Test",
                retry_after=10,
                limit=0,
            )

        # remaining must be non-negative
        with pytest.raises(ValidationError):
            RateLimitError(
                message="Test",
                retry_after=10,
                remaining=-1,
            )

        # reset_at must be positive
        with pytest.raises(ValidationError):
            RateLimitError(
                message="Test",
                retry_after=10,
                reset_at=0,
            )
