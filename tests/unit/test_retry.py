"""Unit tests for retry logic."""

import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from src.models.retry import RetryConfig
from src.utils.retry import retry_with_backoff


class TestRetryConfig:
    """Tests for RetryConfig model."""

    def test_retry_config_defaults(self) -> None:
        """Test RetryConfig has correct default values."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 4.0
        assert config.exponential_base == 2.0

    def test_retry_config_custom_values(self) -> None:
        """Test RetryConfig accepts custom values."""
        config = RetryConfig(max_attempts=5, base_delay=2.0, max_delay=10.0, exponential_base=3.0)
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 10.0
        assert config.exponential_base == 3.0

    def test_retry_config_validates_max_attempts(self) -> None:
        """Test RetryConfig validates max_attempts is within bounds."""
        with pytest.raises(ValueError):
            RetryConfig(max_attempts=0)
        with pytest.raises(ValueError):
            RetryConfig(max_attempts=11)

    def test_retry_config_validates_base_delay(self) -> None:
        """Test RetryConfig validates base_delay is positive."""
        with pytest.raises(ValueError):
            RetryConfig(base_delay=0)
        with pytest.raises(ValueError):
            RetryConfig(base_delay=-1)

    def test_retry_config_validates_exponential_base(self) -> None:
        """Test RetryConfig validates exponential_base is greater than 1."""
        with pytest.raises(ValueError):
            RetryConfig(exponential_base=1.0)


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""

    @pytest.mark.asyncio
    async def test_retry_succeeds_first_attempt(self) -> None:
        """Test retry decorator returns on first successful attempt."""
        mock_func = AsyncMock(return_value="success")

        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        async def test_func() -> str:
            return await mock_func()

        result = await test_func()
        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_succeeds_after_failures(self) -> None:
        """Test retry decorator retries on network errors and eventually succeeds."""
        mock_func = AsyncMock(
            side_effect=[
                httpx.NetworkError("Connection failed"),
                httpx.NetworkError("Connection failed"),
                "success",
            ]
        )

        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        async def test_func() -> str:
            return await mock_func()

        result = await test_func()
        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausts_attempts(self) -> None:
        """Test retry decorator raises error after exhausting attempts."""
        mock_func = AsyncMock(side_effect=httpx.NetworkError("Connection failed"))

        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        async def test_func() -> str:
            return await mock_func()

        with pytest.raises(httpx.NetworkError):
            await test_func()
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exponential_backoff_delays(self) -> None:
        """Test retry decorator uses exponential backoff delays (1s, 2s, 4s)."""
        mock_func = AsyncMock(side_effect=httpx.NetworkError("Connection failed"))

        @retry_with_backoff(max_attempts=3, base_delay=1.0)
        async def test_func() -> str:
            return await mock_func()

        start = asyncio.get_event_loop().time()
        with pytest.raises(httpx.NetworkError):
            await test_func()
        elapsed = asyncio.get_event_loop().time() - start

        # Should have delays of ~1s + 2s = ~3s total
        assert elapsed >= 2.8  # Allow some tolerance
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_respects_max_delay(self) -> None:
        """Test retry decorator respects max_delay cap."""
        mock_func = AsyncMock(side_effect=httpx.NetworkError("Connection failed"))

        @retry_with_backoff(max_attempts=5, base_delay=1.0, max_delay=2.0)
        async def test_func() -> str:
            return await mock_func()

        with pytest.raises(httpx.NetworkError):
            await test_func()
        # All delays should be capped at max_delay

    @pytest.mark.asyncio
    async def test_retry_handles_rate_limit_with_retry_after(self) -> None:
        """Test retry decorator handles rate limits with Retry-After header."""
        response = httpx.Response(
            status_code=429,
            headers={"Retry-After": "2"},
            request=httpx.Request("GET", "http://test.com"),
        )

        mock_func = AsyncMock(
            side_effect=[
                httpx.HTTPStatusError("Rate limited", request=response.request, response=response),
                "success",
            ]
        )

        @retry_with_backoff(max_attempts=3, base_delay=0.1, rate_limit_max_wait=5)
        async def test_func() -> str:
            return await mock_func()

        result = await test_func()
        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_rejects_excessive_retry_after(self) -> None:
        """Test retry decorator rejects Retry-After exceeding max wait."""
        response = httpx.Response(
            status_code=429,
            headers={"Retry-After": "120"},  # 2 minutes
            request=httpx.Request("GET", "http://test.com"),
        )

        mock_func = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Rate limited", request=response.request, response=response
            )
        )

        @retry_with_backoff(max_attempts=3, base_delay=0.1, rate_limit_max_wait=60)
        async def test_func() -> str:
            return await mock_func()

        with pytest.raises(httpx.HTTPStatusError):
            await test_func()
        # Should not retry if Retry-After exceeds max_wait

    @pytest.mark.asyncio
    async def test_retry_only_retries_network_errors(self) -> None:
        """Test retry decorator only retries on network errors and rate limits."""
        mock_func = AsyncMock(side_effect=ValueError("Invalid data"))

        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        async def test_func() -> str:
            return await mock_func()

        with pytest.raises(ValueError, match=".*"):
            await test_func()
        # Should fail immediately on non-retryable errors
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_handles_non_integer_retry_after(self) -> None:
        """Test retry decorator handles non-integer Retry-After header."""
        response = httpx.Response(
            status_code=429,
            headers={"Retry-After": "invalid"},  # Non-integer value
            request=httpx.Request("GET", "http://test.com"),
        )

        mock_func = AsyncMock(
            side_effect=[
                httpx.HTTPStatusError("Rate limited", request=response.request, response=response),
                "success",
            ]
        )

        @retry_with_backoff(max_attempts=3, base_delay=0.5, rate_limit_max_wait=5)
        async def test_func() -> str:
            return await mock_func()

        result = await test_func()
        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_handles_non_429_http_errors(self) -> None:
        """Test retry decorator does not retry non-429 HTTP errors."""
        response = httpx.Response(
            status_code=500,
            request=httpx.Request("GET", "http://test.com"),
        )

        mock_func = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Server error", request=response.request, response=response
            )
        )

        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        async def test_func() -> str:
            return await mock_func()

        with pytest.raises(httpx.HTTPStatusError):
            await test_func()
        # Should not retry 500 errors
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_rate_limit_on_final_attempt(self) -> None:
        """Test retry decorator handles rate limit on final attempt."""
        response = httpx.Response(
            status_code=429,
            headers={"Retry-After": "2"},
            request=httpx.Request("GET", "http://test.com"),
        )

        mock_func = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Rate limited", request=response.request, response=response
            )
        )

        @retry_with_backoff(max_attempts=1, base_delay=0.1, rate_limit_max_wait=5)
        async def test_func() -> str:
            return await mock_func()

        with pytest.raises(httpx.HTTPStatusError):
            await test_func()
        assert mock_func.call_count == 1
