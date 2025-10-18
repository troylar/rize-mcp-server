"""Configuration management for Rize MCP Server."""

from pydantic import Field
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
    rize_api_key: str = Field(..., description="Rize API key")
    rize_api_url: str = Field(
        default="https://api.rize.io/api/v1/graphql",
        description="Rize GraphQL API endpoint URL",
    )

    # MCP Server Configuration
    mcp_server_name: str = Field(default="rize-mcp-server", description="MCP server name")
    mcp_server_version: str = Field(default="0.1.0", description="MCP server version")

    # Performance & Timeouts
    http_timeout: float = Field(default=30.0, gt=0, description="HTTP request timeout in seconds")
    max_records_per_query: int = Field(default=1000, gt=0, description="Maximum records per query")
    rate_limit_max_wait: int = Field(
        default=60, gt=0, description="Maximum wait time for rate limits in seconds"
    )

    # Retry Configuration
    retry_max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    retry_base_delay: float = Field(
        default=1.0, gt=0, le=10, description="Base delay for first retry in seconds"
    )
    retry_max_delay: float = Field(
        default=4.0, gt=0, le=60, description="Maximum delay between retries in seconds"
    )

    # Schema Caching
    schema_cache_enabled: bool = Field(default=True, description="Enable schema caching")
    schema_cache_ttl: int = Field(default=3600, gt=0, description="Schema cache TTL in seconds")
    schema_cache_dir: str = Field(
        default="/tmp/rize-mcp-cache",  # noqa: S108
        description="Directory for schema cache files",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
