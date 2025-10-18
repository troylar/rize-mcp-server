"""Logging utilities with JSON formatting and credential redaction."""

import json
import logging
import re
from datetime import UTC, datetime
from typing import Any


# Patterns for credential redaction
CREDENTIAL_PATTERNS = [
    (
        re.compile(r"api_key['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]+)", re.IGNORECASE),
        r"api_key=***REDACTED***",
    ),
    (
        re.compile(r"rize_api_key['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]+)", re.IGNORECASE),
        r"rize_api_key=***REDACTED***",
    ),
    (re.compile(r"Bearer\s+([a-zA-Z0-9_\-\.]+)", re.IGNORECASE), r"Bearer ***REDACTED***"),
    (
        re.compile(r"Authorization['\"]?\s*[:=]\s*['\"]?([^\s'\"]+)", re.IGNORECASE),
        r"Authorization: ***REDACTED***",
    ),
    (
        re.compile(r"token['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]+)", re.IGNORECASE),
        r"token=***REDACTED***",
    ),
]


def redact_credentials(text: str) -> str:
    """
    Redact sensitive credentials from text.

    Args:
        text: Text that may contain credentials.

    Returns:
        Text with credentials redacted.
    """
    result = text
    for pattern, replacement in CREDENTIAL_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


class JSONFormatter(logging.Formatter):
    """JSON log formatter with credential redaction."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON with credential redaction.

        Args:
            record: Log record to format.

        Returns:
            JSON-formatted log string.
        """
        # Build base log entry
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_credentials(record.getMessage()),
        }

        # Add standard fields
        if record.pathname:
            log_data["file"] = record.pathname
        if record.lineno:
            log_data["line"] = record.lineno
        if record.funcName:
            log_data["function"] = record.funcName

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record (with credential redaction)
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "taskName",
            }:
                # Redact if field name suggests it's a credential
                if any(
                    cred in key.lower() for cred in ["key", "token", "password", "secret", "auth"]
                ):
                    log_data[key] = "***REDACTED***"
                # Still redact value if it looks like a credential
                elif isinstance(value, str):
                    log_data[key] = redact_credentials(value)
                else:
                    log_data[key] = value

        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """
    Setup logging with JSON formatter and credential redaction.

    Returns:
        Configured logger instance.
    """
    from src.config import Settings  # noqa: PLC0415

    settings = Settings(_env_file=None if "RIZE_API_KEY" in __import__("os").environ else ".env")  # type: ignore[call-arg]

    # Get root logger
    logger = logging.getLogger()

    # Clear existing handlers
    logger.handlers.clear()

    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Set formatter based on log format
    if settings.log_format.lower() == "json":
        formatter: logging.Formatter = JSONFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
