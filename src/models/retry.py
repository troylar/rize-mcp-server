"""Retry configuration model."""

from pydantic import BaseModel, Field


class RetryConfig(BaseModel):
    """Configuration for exponential backoff retry logic."""

    max_attempts: int = Field(
        default=3, ge=1, le=10, description="Maximum number of retry attempts"
    )
    base_delay: float = Field(
        default=1.0, gt=0, le=10, description="Base delay in seconds for first retry"
    )
    max_delay: float = Field(
        default=4.0, gt=0, le=60, description="Maximum delay between retries in seconds"
    )
    exponential_base: float = Field(
        default=2.0, gt=1, le=10, description="Exponential backoff multiplier"
    )
