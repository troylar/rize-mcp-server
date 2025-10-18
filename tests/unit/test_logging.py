"""Unit tests for logging utilities."""

import json
import logging

import pytest

from src.utils.logging import JSONFormatter, redact_credentials, setup_logging


class TestJSONFormatter:
    """Tests for JSONFormatter class."""

    def test_json_formatter_basic_message(self) -> None:
        """Test JSONFormatter produces valid JSON output."""
        # Arrange
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"  # Explicitly set function name

        # Act
        output = formatter.format(record)
        data = json.loads(output)

        # Assert
        assert data["message"] == "Test message"
        assert data["level"] == "INFO"
        assert data["logger"] == "test_logger"
        assert data["file"] == "test.py"
        assert data["line"] == 10
        assert data["function"] == "test_function"
        assert "timestamp" in data

    def test_json_formatter_with_extra_fields(self) -> None:
        """Test JSONFormatter includes extra fields from LogRecord."""
        # Arrange
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=10,
            msg="Test with extras",
            args=(),
            exc_info=None,
        )
        record.user_id = "user_123"  # type: ignore[attr-defined]
        record.request_id = "req_456"  # type: ignore[attr-defined]

        # Act
        output = formatter.format(record)
        data = json.loads(output)

        # Assert
        assert data["user_id"] == "user_123"
        assert data["request_id"] == "req_456"

    def test_json_formatter_credential_redaction(self) -> None:
        """Test JSONFormatter redacts API keys and credentials."""
        # Arrange
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Processing with rize_api_key=secret123",
            args=(),
            exc_info=None,
        )
        record.api_key = "actual_secret_key"  # type: ignore[attr-defined]
        record.rize_api_key = "another_secret"  # type: ignore[attr-defined]
        record.Authorization = "Bearer token123"  # type: ignore[attr-defined]

        # Act
        output = formatter.format(record)
        data = json.loads(output)

        # Assert - credentials should be redacted
        assert "secret123" not in output
        assert "actual_secret_key" not in output
        assert "another_secret" not in output
        assert "token123" not in output
        assert "***REDACTED***" in output
        assert data["api_key"] == "***REDACTED***"
        assert data["rize_api_key"] == "***REDACTED***"
        assert data["Authorization"] == "***REDACTED***"

    def test_json_formatter_with_exception(self) -> None:
        """Test JSONFormatter includes exception information."""
        # Arrange
        formatter = JSONFormatter()
        try:
            msg = "Test exception message"
            raise ValueError(msg)
        except ValueError:
            exc_info = __import__("sys").exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=100,
            msg="An error occurred",
            args=(),
            exc_info=exc_info,
        )

        # Act
        output = formatter.format(record)
        data = json.loads(output)

        # Assert
        assert data["message"] == "An error occurred"
        assert "exception" in data
        assert "ValueError" in data["exception"]
        assert "Test exception message" in data["exception"]

    def test_json_formatter_redacts_non_string_values(self) -> None:
        """Test JSONFormatter handles non-string credential fields."""
        # Arrange
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.count = 42  # type: ignore[attr-defined]
        record.enabled = True  # type: ignore[attr-defined]
        record.password = "secret_password"  # type: ignore[attr-defined]

        # Act
        output = formatter.format(record)
        data = json.loads(output)

        # Assert
        assert data["count"] == 42
        assert data["enabled"] is True
        assert data["password"] == "***REDACTED***"  # password keyword should trigger redaction

    def test_json_formatter_with_minimal_record(self) -> None:
        """Test JSONFormatter with minimal LogRecord (no pathname, lineno, funcName)."""
        # Arrange
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",  # Empty pathname
            lineno=0,  # No line number
            msg="Minimal record",
            args=(),
            exc_info=None,
        )
        record.funcName = ""  # type: ignore[assignment]  # Empty function name

        # Act
        output = formatter.format(record)
        data = json.loads(output)

        # Assert
        assert data["message"] == "Minimal record"
        # These fields should not be present when empty/zero
        assert "file" not in data or data["file"] == ""
        assert "line" not in data or data["line"] == 0
        assert "function" not in data or data["function"] == ""


class TestRedactCredentials:
    """Tests for credential redaction function."""

    def test_redact_api_key_in_string(self) -> None:
        """Test redacting API keys in strings."""
        # Act
        result = redact_credentials("Using api_key=sk_test_123456")

        # Assert
        assert "sk_test_123456" not in result
        assert "***REDACTED***" in result

    def test_redact_bearer_token(self) -> None:
        """Test redacting Bearer tokens."""
        # Act
        result = redact_credentials("Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")

        # Assert
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result
        assert "***REDACTED***" in result

    def test_redact_rize_api_key_field(self) -> None:
        """Test redacting rize_api_key fields."""
        # Act
        result = redact_credentials("Config: rize_api_key=prod_key_xyz")

        # Assert
        assert "prod_key_xyz" not in result
        assert "***REDACTED***" in result

    def test_redact_preserves_other_content(self) -> None:
        """Test that non-sensitive content is preserved."""
        # Act
        result = redact_credentials("User test@example.com with api_key=secret")

        # Assert
        assert "test@example.com" in result
        assert "User" in result
        assert "with" in result
        assert "secret" not in result

    def test_redact_multiple_credentials(self) -> None:
        """Test redacting multiple credentials in one string."""
        # Act
        result = redact_credentials(
            "api_key=key1 and rize_api_key=key2 with Authorization: Bearer abc123"
        )

        # Assert
        assert "key1" not in result
        assert "key2" not in result
        assert "abc123" not in result
        # Should have 3 redactions (api_key, rize_api_key, Authorization)
        assert result.count("***REDACTED***") >= 3

    def test_redact_credentials_in_dict(self) -> None:
        """Test redacting credentials in dictionary values."""
        # Arrange
        data = {
            "user": "john",
            "api_key": "secret123",
            "rize_api_key": "another_secret",
            "metadata": {"token": "bearer_xyz"},
        }

        # Act
        result = redact_credentials(str(data))

        # Assert
        assert "secret123" not in result
        assert "another_secret" not in result
        assert "bearer_xyz" not in result


class TestSetupLogging:
    """Tests for logging setup function."""

    def test_setup_logging_configures_logger(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test setup_logging configures root logger correctly."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key_for_logging")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("LOG_FORMAT", "json")

        # Act
        logger = setup_logging()

        # Assert
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) > 0

    def test_setup_logging_uses_json_formatter(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test setup_logging uses JSONFormatter when log_format is json."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key_for_logging")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("LOG_FORMAT", "json")

        # Act
        logger = setup_logging()

        # Assert
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, JSONFormatter)

    def test_setup_logging_with_text_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test setup_logging uses standard formatter for text format."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key_for_logging")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        monkeypatch.setenv("LOG_FORMAT", "text")

        # Act
        logger = setup_logging()

        # Assert
        handler = logger.handlers[0]
        assert not isinstance(handler.formatter, JSONFormatter)
        assert isinstance(handler.formatter, logging.Formatter)
