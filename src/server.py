"""Main MCP server implementation for Rize time tracking API."""

from datetime import UTC, datetime, timedelta  # pragma: no cover

from fastmcp import FastMCP  # pragma: no cover

from src.config import Settings  # pragma: no cover
from src.tools import time_tracking  # pragma: no cover
from src.utils.logging import setup_logging  # pragma: no cover


# Initialize settings and logging
settings = Settings()  # type: ignore[call-arg]  # pragma: no cover
logger = setup_logging()  # pragma: no cover

# Initialize FastMCP server  # pragma: no cover
mcp = FastMCP(  # pragma: no cover
    name=settings.mcp_server_name,
    version=settings.mcp_server_version,
)


# Register MCP tools for time tracking
@mcp.tool()  # type: ignore[misc]  # pragma: no cover
async def start_timer(  # pragma: no cover
    project_id: str, task_id: str | None = None
) -> dict[str, object]:
    """
    Start a new time tracking session.

    Use this to begin tracking time for a project or specific task.
    Only one session can be active at a time.

    Args:
        project_id: ID of the project to track time for.
        task_id: Optional ID of the specific task within the project.

    Returns:
        Session details including session ID, project, task, and start time.

    Examples:
        Start timer for a project:
        >>> start_timer(project_id="proj_abc123")

        Start timer for a specific task:
        >>> start_timer(project_id="proj_abc123", task_id="task_xyz789")
    """
    return await time_tracking.start_timer(  # pragma: no cover
        project_id=project_id,
        task_id=task_id,
        api_url=settings.rize_api_url,
        api_key=settings.rize_api_key,
        timeout=settings.http_timeout,
    )


@mcp.tool()  # type: ignore[misc]  # pragma: no cover
async def stop_timer() -> dict[str, object]:  # pragma: no cover
    """
    Stop the currently running time tracking session.

    This completes the active session and saves the tracked time.

    Returns:
        Completed session details including total duration.

    Examples:
        >>> stop_timer()
    """
    return await time_tracking.stop_timer(  # pragma: no cover
        api_url=settings.rize_api_url,
        api_key=settings.rize_api_key,
        timeout=settings.http_timeout,
    )


@mcp.tool()  # type: ignore[misc]  # pragma: no cover
async def get_current_session() -> dict[str, object] | None:  # pragma: no cover
    """
    Check if there's a currently active time tracking session.

    Returns:
        Current session details if active, None otherwise.

    Examples:
        >>> session = get_current_session()
        >>> if session:
        ...     print(f"Active session: {session['title']}")
    """
    return await time_tracking.get_current_session(  # pragma: no cover
        api_url=settings.rize_api_url,
        api_key=settings.rize_api_key,
        timeout=settings.http_timeout,
    )


@mcp.tool()  # type: ignore[misc]  # pragma: no cover
async def log_time(  # pragma: no cover
    project_id: str,
    hours: float,
    entry_date: str,
    task_id: str | None = None,
    description: str | None = None,
) -> dict[str, object]:
    """
    Create a manual time entry for a project.

    Use this to log time after the fact, rather than using the timer.

    Args:
        project_id: ID of the project.
        hours: Number of hours to log (e.g., 2.5 for 2 hours 30 minutes).
        entry_date: Date of the work in YYYY-MM-DD format.
        task_id: Optional ID of the specific task.
        description: Optional description of the work performed.

    Returns:
        Created time entry with ID, project, hours, and date.

    Examples:
        Log 3.5 hours for yesterday:
        >>> log_time(
        ...     project_id="proj_abc123",
        ...     hours=3.5,
        ...     entry_date="2024-01-15",
        ...     description="Implemented login feature"
        ... )
    """
    return await time_tracking.create_time_entry(  # pragma: no cover
        project_id=project_id,
        hours=hours,
        entry_date=entry_date,
        task_id=task_id,
        description=description,
        api_url=settings.rize_api_url,
        api_key=settings.rize_api_key,
        timeout=settings.http_timeout,
    )


@mcp.tool()  # type: ignore[misc]  # pragma: no cover
async def list_projects() -> list[dict[str, object]]:  # pragma: no cover
    """
    List all projects.

    Returns:
        List of projects with their IDs, names, and client information.

    Examples:
        List all projects:
        >>> list_projects()
    """
    return await time_tracking.list_projects(  # pragma: no cover
        api_url=settings.rize_api_url,
        api_key=settings.rize_api_key,
        timeout=settings.http_timeout,
    )


@mcp.tool()  # type: ignore[misc]  # pragma: no cover
async def get_time_summary(  # pragma: no cover
    start_date: str, end_date: str, bucket_size: str = "day"
) -> dict[str, object]:
    """
    Get time tracking summary for a date range.

    Provides tracked time (in seconds), focus time, meeting time, break time,
    and breakdown by category.

    Args:
        start_date: Start of period in YYYY-MM-DD format.
        end_date: End of period in YYYY-MM-DD format.
        bucket_size: Time bucket size (day, week, month). Default: day.

    Returns:
        Summary with tracked time, work hours, focus time, meeting time,
        break time, and breakdowns by category and time buckets.

    Examples:
        Get this week's summary:
        >>> get_time_summary(
        ...     start_date="2024-01-15",
        ...     end_date="2024-01-21"
        ... )

        Get monthly summary:
        >>> get_time_summary(
        ...     start_date="2024-01-01",
        ...     end_date="2024-01-31",
        ...     bucket_size="week"
        ... )
    """
    return await time_tracking.get_time_summary(  # pragma: no cover
        start_date=start_date,
        end_date=end_date,
        bucket_size=bucket_size,
        api_url=settings.rize_api_url,
        api_key=settings.rize_api_key,
        timeout=settings.http_timeout,
    )


@mcp.tool()  # type: ignore[misc]  # pragma: no cover
async def get_task_time_entries(  # pragma: no cover
    start_time: str | None = None, end_time: str | None = None
) -> dict[str, object]:
    """
    Get task time entries for a date range.

    Returns all time entries logged for tasks within the specified time period.
    If no dates provided, returns entries from the last 30 days.

    Args:
        start_time: Start of period in ISO8601 datetime format (e.g., 2024-01-15T00:00:00Z).
                   Defaults to 30 days ago if not provided.
        end_time: End of period in ISO8601 datetime format (e.g., 2024-01-22T00:00:00Z).
                 Defaults to now if not provided.

    Returns:
        Dictionary with entries list, count, date range, and status message.

    Examples:
        Get task entries for last 30 days:
        >>> get_task_time_entries()

        Get task entries for specific date range:
        >>> get_task_time_entries(
        ...     start_time="2024-01-15T00:00:00Z",
        ...     end_time="2024-01-22T00:00:00Z"
        ... )
    """
    # Default to last 30 days if not provided or empty
    if not end_time:  # pragma: no cover
        end_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not start_time:  # pragma: no cover
        start_dt = datetime.now(UTC) - timedelta(days=30)
        start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Ensure datetime strings are valid (basic validation)
    if isinstance(start_time, str) and len(start_time) < 10:  # noqa: PLR2004  # pragma: no cover
        logger.warning("Invalid start_time received: %s", start_time)
        start_dt = datetime.now(UTC) - timedelta(days=30)
        start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(end_time, str) and len(end_time) < 10:  # noqa: PLR2004  # pragma: no cover
        logger.warning("Invalid end_time received: %s", end_time)
        end_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    entries = await time_tracking.get_task_time_entries(  # pragma: no cover
        start_time=start_time,
        end_time=end_time,
        api_url=settings.rize_api_url,
        api_key=settings.rize_api_key,
        timeout=settings.http_timeout,
    )

    # Return structured response with metadata
    return {  # pragma: no cover
        "entries": entries,
        "count": len(entries),
        "start_time": start_time,
        "end_time": end_time,
        "message": f"Found {len(entries)} task time entries"
        if entries
        else "No task time entries found for this period",
    }


@mcp.tool()  # type: ignore[misc]  # pragma: no cover
async def get_project_time_entries(  # pragma: no cover
    start_time: str | None = None, end_time: str | None = None
) -> dict[str, object]:
    """
    Get project time entries for a date range.

    Returns all time entries logged for projects within the specified time period.
    If no dates provided, returns entries from the last 30 days.

    Args:
        start_time: Start of period in ISO8601 datetime format (e.g., 2024-01-15T00:00:00Z).
                   Defaults to 30 days ago if not provided.
        end_time: End of period in ISO8601 datetime format (e.g., 2024-01-22T00:00:00Z).
                 Defaults to now if not provided.

    Returns:
        Dictionary with entries list, count, date range, and status message.

    Examples:
        Get project entries for last 30 days:
        >>> get_project_time_entries()

        Get project entries for specific date range:
        >>> get_project_time_entries(
        ...     start_time="2024-01-15T00:00:00Z",
        ...     end_time="2024-01-22T00:00:00Z"
        ... )
    """
    # Default to last 30 days if not provided or empty
    if not end_time:  # pragma: no cover
        end_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not start_time:  # pragma: no cover
        start_dt = datetime.now(UTC) - timedelta(days=30)
        start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Ensure datetime strings are valid (basic validation)
    if isinstance(start_time, str) and len(start_time) < 10:  # noqa: PLR2004  # pragma: no cover
        logger.warning("Invalid start_time received: %s", start_time)
        start_dt = datetime.now(UTC) - timedelta(days=30)
        start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(end_time, str) and len(end_time) < 10:  # noqa: PLR2004  # pragma: no cover
        logger.warning("Invalid end_time received: %s", end_time)
        end_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    entries = await time_tracking.get_project_time_entries(  # pragma: no cover
        start_time=start_time,
        end_time=end_time,
        api_url=settings.rize_api_url,
        api_key=settings.rize_api_key,
        timeout=settings.http_timeout,
    )

    # Return structured response with metadata
    return {  # pragma: no cover
        "entries": entries,
        "count": len(entries),
        "start_time": start_time,
        "end_time": end_time,
        "message": f"Found {len(entries)} project time entries"
        if entries
        else "No project time entries found for this period",
    }


@mcp.tool()  # type: ignore[misc]  # pragma: no cover
async def get_apps_and_websites(  # pragma: no cover
    start_time: str | None = None, end_time: str | None = None
) -> dict[str, object]:
    """
    Get apps and websites usage for a date range.

    Returns all apps and websites tracked within the specified time period,
    including time spent on each. If no dates provided, returns data from
    the last 30 days.

    Args:
        start_time: Start of period in ISO8601 datetime format (e.g., 2024-01-15T00:00:00Z).
                   Defaults to 30 days ago if not provided.
        end_time: End of period in ISO8601 datetime format (e.g., 2024-01-22T00:00:00Z).
                 Defaults to now if not provided.

    Returns:
        Dictionary with apps/websites list, count, date range, and status message.

    Examples:
        Get apps and websites for last 30 days:
        >>> get_apps_and_websites()

        Get apps and websites for specific date range:
        >>> get_apps_and_websites(
        ...     start_time="2024-01-15T00:00:00Z",
        ...     end_time="2024-01-22T00:00:00Z"
        ... )
    """
    # Default to last 30 days if not provided or empty
    if not end_time:  # pragma: no cover
        end_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not start_time:  # pragma: no cover
        start_dt = datetime.now(UTC) - timedelta(days=30)
        start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Ensure datetime strings are valid (basic validation)
    if isinstance(start_time, str) and len(start_time) < 10:  # noqa: PLR2004  # pragma: no cover
        logger.warning("Invalid start_time received: %s", start_time)
        start_dt = datetime.now(UTC) - timedelta(days=30)
        start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(end_time, str) and len(end_time) < 10:  # noqa: PLR2004  # pragma: no cover
        logger.warning("Invalid end_time received: %s", end_time)
        end_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    entries = await time_tracking.get_apps_and_websites(  # pragma: no cover
        start_time=start_time,
        end_time=end_time,
        api_url=settings.rize_api_url,
        api_key=settings.rize_api_key,
        timeout=settings.http_timeout,
    )

    # Return structured response with metadata
    return {  # pragma: no cover
        "entries": entries,
        "count": len(entries),
        "start_time": start_time,
        "end_time": end_time,
        "message": f"Found {len(entries)} apps and websites"
        if entries
        else "No apps and websites found for this period",
    }


def main() -> None:  # pragma: no cover
    """Main entry point for the MCP server."""
    logger.info("Starting %s v%s", settings.mcp_server_name, settings.mcp_server_version)
    logger.info("Rize API URL: %s", settings.rize_api_url)
    logger.info("Log level: %s", settings.log_level)
    logger.info("Max records per query: %d", settings.max_records_per_query)

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
