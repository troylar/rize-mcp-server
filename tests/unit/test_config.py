"""Unit tests for configuration module."""

import pytest
from pydantic import ValidationError

from src.config import Settings


class TestSettings:
    """Tests for Settings pydantic model."""

    def test_settings_load_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that Settings loads values from environment variables."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_api_key_12345")
        monkeypatch.setenv("RIZE_API_URL", "https://custom.api.url/graphql")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("SCHEMA_CACHE_TTL", "7200")

        # Act
        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.rize_api_key == "test_api_key_12345"
        assert settings.rize_api_url == "https://custom.api.url/graphql"
        assert settings.log_level == "DEBUG"
        assert settings.schema_cache_ttl == 7200

    def test_settings_missing_required_field_raises_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that Settings raises ValidationError when required fields are missing."""
        # Arrange - clear environment
        monkeypatch.delenv("RIZE_API_KEY", raising=False)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)  # type: ignore[call-arg]

        assert "rize_api_key" in str(exc_info.value).lower()

    def test_settings_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that Settings applies correct default values."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key")

        # Act
        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        # Assert - verify defaults
        assert settings.rize_api_url == "https://api.rize.io/api/v1/graphql"
        assert settings.mcp_server_name == "rize-mcp-server"
        assert settings.mcp_server_version == "0.1.0"
        assert settings.log_level == "INFO"
        assert settings.schema_cache_enabled is True
        assert settings.schema_cache_ttl == 3600
        assert settings.http_timeout == 30.0
        assert settings.max_records_per_query == 1000
        assert settings.rate_limit_max_wait == 60

    def test_settings_type_coercion(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that Settings coerces string environment variables to correct types."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key")
        monkeypatch.setenv("SCHEMA_CACHE_ENABLED", "false")  # string boolean
        monkeypatch.setenv("SCHEMA_CACHE_TTL", "1800")  # string integer
        monkeypatch.setenv("HTTP_TIMEOUT", "45.5")  # string float

        # Act
        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.schema_cache_enabled is False
        assert settings.schema_cache_ttl == 1800
        assert settings.http_timeout == 45.5

    def test_settings_validates_numeric_constraints(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that Settings validates numeric field constraints."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key")
        monkeypatch.setenv("HTTP_TIMEOUT", "-5")  # Invalid negative timeout

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)  # type: ignore[call-arg]

        assert "http_timeout" in str(exc_info.value).lower()

    def test_settings_ignore_extra_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that Settings ignores unknown environment variables."""
        # Arrange
        monkeypatch.setenv("RIZE_API_KEY", "test_key")
        monkeypatch.setenv("UNKNOWN_VARIABLE", "should_be_ignored")
        monkeypatch.setenv("ANOTHER_RANDOM_VAR", "also_ignored")

        # Act - should not raise error
        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert not hasattr(settings, "unknown_variable")
        assert not hasattr(settings, "another_random_var")
