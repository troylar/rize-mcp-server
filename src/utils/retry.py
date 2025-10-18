"""Retry logic with exponential backoff for network requests."""

import asyncio
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import httpx


logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 4.0,
    rate_limit_max_wait: int = 60,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for retrying async functions with exponential backoff.

    Retries on network errors (httpx.NetworkError) and rate limits (429 status).
    Uses exponential backoff with delays: base_delay * (2 ** attempt).

    Args:
        max_attempts: Maximum number of retry attempts (default: 3).
        base_delay: Base delay in seconds for first retry (default: 1.0).
        max_delay: Maximum delay between retries in seconds (default: 4.0).
        rate_limit_max_wait: Maximum wait time for rate limits in seconds (default: 60).

    Returns:
        Decorated async function with retry logic.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: PLR0912, ANN401
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except httpx.NetworkError as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        # Exponential backoff: 1s, 2s, 4s
                        delay = min(base_delay * (2**attempt), max_delay)
                        logger.warning(
                            "Network error on attempt %d/%d, retrying in %.1fs: %s",
                            attempt + 1,
                            max_attempts,
                            delay,
                            str(e),
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.exception(
                            "Network error on final attempt %d/%d",
                            attempt + 1,
                            max_attempts,
                        )
                except httpx.HTTPStatusError as e:
                    # Handle rate limiting (429 status)
                    if e.response.status_code == 429:  # noqa: PLR2004
                        last_exception = e
                        retry_after = e.response.headers.get("Retry-After")

                        if retry_after and attempt < max_attempts - 1:
                            try:
                                wait_time = int(retry_after)
                            except ValueError:
                                # If Retry-After is not an integer, use base_delay
                                wait_time = int(base_delay)

                            if wait_time <= rate_limit_max_wait:
                                logger.warning(
                                    "Rate limited (429), waiting %ds before retry (attempt %d/%d)",
                                    wait_time,
                                    attempt + 1,
                                    max_attempts,
                                )
                                await asyncio.sleep(wait_time)
                            else:
                                logger.exception(
                                    "Rate limit wait time (%ds) exceeds max (%ds)",
                                    wait_time,
                                    rate_limit_max_wait,
                                )
                                raise
                        else:
                            raise
                    else:
                        # Non-429 HTTP errors are not retried
                        raise
                except Exception:
                    # Non-network errors are not retried
                    raise

            # All retries exhausted
            if last_exception:
                raise last_exception
            msg = "Unexpected retry loop exit"  # pragma: no cover
            raise RuntimeError(msg)  # pragma: no cover

        return wrapper

    return decorator
