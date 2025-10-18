"""MCP tools for Rize time tracking operations."""

import logging
from datetime import date
from typing import Any

from src.utils.graphql import execute_graphql


logger = logging.getLogger(__name__)


async def start_timer(
    project_id: str,
    task_id: str | None = None,
    api_url: str = "",
    api_key: str = "",
    timeout: float = 30.0,  # noqa: ASYNC109
) -> dict[str, Any]:
    """
    Start a new time tracking session.

    Args:
        project_id: ID of the project to track time for.
        task_id: Optional ID of the specific task.
        api_url: Rize GraphQL API endpoint.
        api_key: Rize API key.
        timeout: Request timeout in seconds.

    Returns:
        Session details including session ID and start time.

    Examples:
        Start timer for a project:
        >>> await start_timer(project_id="proj_123")

        Start timer for a specific task:
        >>> await start_timer(project_id="proj_123", task_id="task_456")
    """
    query = """
        mutation StartTimer($input: StartSessionTimePayload!) {
            startSessionTime(input: $input) {
                id
                project {
                    id
                    name
                }
                task {
                    id
                    name
                }
                startedAt
            }
        }
    """

    variables = {"input": {"projectId": project_id}}
    if task_id:
        variables["input"]["taskId"] = task_id

    result = await execute_graphql(
        query=query,
        variables=variables,
        operation_name="StartTimer",
        api_url=api_url,
        api_key=api_key,
        timeout=timeout,
    )

    session: dict[str, Any] = result.get("startSessionTime", {})
    return session


async def stop_timer(
    api_url: str = "",
    api_key: str = "",
    timeout: float = 30.0,  # noqa: ASYNC109
) -> dict[str, Any]:
    """
    Stop the currently running time tracking session.

    Args:
        api_url: Rize GraphQL API endpoint.
        api_key: Rize API key.
        timeout: Request timeout in seconds.

    Returns:
        Completed session details including duration.

    Examples:
        >>> await stop_timer()
    """
    query = """
        mutation StopTimer($input: StopSessionTimePayload!) {
            stopSessionTime(input: $input) {
                id
                project {
                    id
                    name
                }
                task {
                    id
                    name
                }
                startedAt
                stoppedAt
                duration
            }
        }
    """

    variables: dict[str, dict[str, object]] = {"input": {}}

    result = await execute_graphql(
        query=query,
        variables=variables,
        operation_name="StopTimer",
        api_url=api_url,
        api_key=api_key,
        timeout=timeout,
    )

    session: dict[str, Any] = result.get("stopSessionTime", {})
    return session


async def get_current_session(
    api_url: str = "",
    api_key: str = "",
    timeout: float = 30.0,  # noqa: ASYNC109
) -> dict[str, Any] | None:
    """
    Get the currently active time tracking session, if any.

    Args:
        api_url: Rize GraphQL API endpoint.
        api_key: Rize API key.
        timeout: Request timeout in seconds.

    Returns:
        Current session details or None if no session is active.

    Examples:
        >>> session = await get_current_session()
        >>> if session:
        ...     print(f"Active session: {session['title']}")
    """
    query = """
        query GetCurrentSession {
            currentSession {
                id
                title
                description
                type
                source
                startTime
                endTime
            }
        }
    """

    result = await execute_graphql(
        query=query,
        operation_name="GetCurrentSession",
        api_url=api_url,
        api_key=api_key,
        timeout=timeout,
    )

    session: dict[str, Any] | None = result.get("currentSession")
    return session


async def create_time_entry(  # noqa: PLR0913
    project_id: str,
    hours: float,
    entry_date: date | str,
    task_id: str | None = None,
    description: str | None = None,
    api_url: str = "",
    api_key: str = "",
    timeout: float = 30.0,  # noqa: ASYNC109
) -> dict[str, Any]:
    """
    Create a manual time entry for a project.

    Args:
        project_id: ID of the project.
        hours: Number of hours to log.
        entry_date: Date of the time entry (YYYY-MM-DD or date object).
        task_id: Optional ID of the specific task.
        description: Optional description of the work done.
        api_url: Rize GraphQL API endpoint.
        api_key: Rize API key.
        timeout: Request timeout in seconds.

    Returns:
        Created time entry details.

    Examples:
        Log 3 hours for a project:
        >>> await create_time_entry(
        ...     project_id="proj_123",
        ...     hours=3.5,
        ...     entry_date="2024-01-15",
        ...     description="Implemented new feature"
        ... )
    """
    query = """
        mutation CreateTimeEntry($input: CreateProjectTimeEntryPayload!) {
            createProjectTimeEntry(input: $input) {
                id
                project {
                    id
                    name
                }
                task {
                    id
                    name
                }
                date
                hours
                description
            }
        }
    """

    # Convert date to string if needed
    if isinstance(entry_date, date):
        entry_date = entry_date.isoformat()

    variables = {
        "input": {
            "projectId": project_id,
            "hours": hours,
            "date": entry_date,
        }
    }

    if task_id:
        variables["input"]["taskId"] = task_id
    if description:
        variables["input"]["description"] = description

    result = await execute_graphql(
        query=query,
        variables=variables,
        operation_name="CreateTimeEntry",
        api_url=api_url,
        api_key=api_key,
        timeout=timeout,
    )

    entry: dict[str, Any] = result.get("createProjectTimeEntry", {})
    return entry


async def list_projects(
    api_url: str = "",
    api_key: str = "",
    timeout: float = 30.0,  # noqa: ASYNC109
) -> list[dict[str, Any]]:
    """
    List all projects.

    Args:
        api_url: Rize GraphQL API endpoint.
        api_key: Rize API key.
        timeout: Request timeout in seconds.

    Returns:
        List of projects with their details.

    Examples:
        List all projects:
        >>> projects = await list_projects()
    """
    query = """
        query ListProjects {
            projects {
                edges {
                    node {
                        id
                        name
                        status
                        color
                        emoji
                        client {
                            id
                            name
                        }
                        createdAt
                        updatedAt
                        lastUsedAt
                    }
                }
            }
        }
    """

    result = await execute_graphql(
        query=query,
        operation_name="ListProjects",
        api_url=api_url,
        api_key=api_key,
        timeout=timeout,
    )

    edges = result.get("projects", {}).get("edges", [])
    return [edge["node"] for edge in edges]


async def get_time_summary(  # noqa: PLR0913
    start_date: date | str,
    end_date: date | str,
    bucket_size: str = "day",
    api_url: str = "",
    api_key: str = "",
    timeout: float = 30.0,  # noqa: ASYNC109
) -> dict[str, Any]:
    """
    Get time tracking summary for a date range.

    Args:
        start_date: Start date of the period (YYYY-MM-DD or date object).
        end_date: End date of the period (YYYY-MM-DD or date object).
        bucket_size: Time bucket size (day, week, month). Default: day.
        api_url: Rize GraphQL API endpoint.
        api_key: Rize API key.
        timeout: Request timeout in seconds.

    Returns:
        Summary with tracked time (in seconds), focus time, meeting time,
        break time, and breakdown by categories.

    Examples:
        Get weekly summary:
        >>> summary = await get_time_summary(
        ...     start_date="2024-01-15",
        ...     end_date="2024-01-21",
        ...     bucket_size="day"
        ... )
    """
    query = """
        query GetTimeSummary(
            $startDate: ISO8601Date!
            $endDate: ISO8601Date!
            $bucketSize: String!
        ) {
            summaries(
                startDate: $startDate
                endDate: $endDate
                bucketSize: $bucketSize
                includeCategories: true
            ) {
                trackedTime
                workHours
                focusTime
                meetingTime
                breakTime
                trackedTimeAverage
                workHoursAverage
                focusTimeAverage
                meetingTimeAverage
                breakTimeAverage
                categories {
                    category {
                        name
                    }
                    timeSpent
                }
                buckets {
                    date
                    trackedTime
                    workHours
                    focusTime
                    meetingTime
                    breakTime
                }
            }
        }
    """

    # Convert dates to strings if needed
    if isinstance(start_date, date):
        start_date = start_date.isoformat()
    if isinstance(end_date, date):
        end_date = end_date.isoformat()

    variables = {
        "startDate": start_date,
        "endDate": end_date,
        "bucketSize": bucket_size,
    }

    result = await execute_graphql(
        query=query,
        variables=variables,
        operation_name="GetTimeSummary",
        api_url=api_url,
        api_key=api_key,
        timeout=timeout,
    )

    summaries: dict[str, Any] = result.get("summaries", {})
    return summaries


async def get_task_time_entries(
    start_time: str,
    end_time: str,
    api_url: str = "",
    api_key: str = "",
    timeout: float = 30.0,  # noqa: ASYNC109
) -> list[dict[str, Any]]:
    """
    Get task time entries for a date range.

    Args:
        start_time: Start of period in ISO8601 datetime format.
        end_time: End of period in ISO8601 datetime format.
        api_url: Rize GraphQL API endpoint.
        api_key: Rize API key.
        timeout: Request timeout in seconds.

    Returns:
        List of task time entries with details.

    Examples:
        Get task time entries for the last week:
        >>> entries = await get_task_time_entries(
        ...     start_time="2024-01-15T00:00:00Z",
        ...     end_time="2024-01-22T00:00:00Z"
        ... )
    """
    query = """
        query GetTaskTimeEntries(
            $startTime: ISO8601DateTime
            $endTime: ISO8601DateTime
        ) {
            taskTimeEntries(startTime: $startTime, endTime: $endTime) {
                id
                startTime
                endTime
                duration
                description
                source
                task {
                    id
                    name
                }
                createdAt
                updatedAt
            }
        }
    """

    variables = {
        "startTime": start_time,
        "endTime": end_time,
    }

    result = await execute_graphql(
        query=query,
        variables=variables,
        operation_name="GetTaskTimeEntries",
        api_url=api_url,
        api_key=api_key,
        timeout=timeout,
    )

    entries: list[dict[str, Any]] = result.get("taskTimeEntries", [])
    return entries


async def get_project_time_entries(
    start_time: str,
    end_time: str,
    api_url: str = "",
    api_key: str = "",
    timeout: float = 30.0,  # noqa: ASYNC109
) -> list[dict[str, Any]]:
    """
    Get project time entries for a date range.

    Args:
        start_time: Start of period in ISO8601 datetime format.
        end_time: End of period in ISO8601 datetime format.
        api_url: Rize GraphQL API endpoint.
        api_key: Rize API key.
        timeout: Request timeout in seconds.

    Returns:
        List of project time entries with details.

    Examples:
        Get project time entries for the last week:
        >>> entries = await get_project_time_entries(
        ...     start_time="2024-01-15T00:00:00Z",
        ...     end_time="2024-01-22T00:00:00Z"
        ... )
    """
    query = """
        query GetProjectTimeEntries(
            $startTime: ISO8601DateTime
            $endTime: ISO8601DateTime
        ) {
            projectTimeEntries(startTime: $startTime, endTime: $endTime) {
                id
                startTime
                endTime
                duration
                description
                source
                project {
                    id
                    name
                }
                createdAt
                updatedAt
            }
        }
    """

    variables = {
        "startTime": start_time,
        "endTime": end_time,
    }

    result = await execute_graphql(
        query=query,
        variables=variables,
        operation_name="GetProjectTimeEntries",
        api_url=api_url,
        api_key=api_key,
        timeout=timeout,
    )

    entries: list[dict[str, Any]] = result.get("projectTimeEntries", [])
    return entries


async def get_apps_and_websites(
    start_time: str,
    end_time: str,
    api_url: str = "",
    api_key: str = "",
    timeout: float = 30.0,  # noqa: ASYNC109
) -> list[dict[str, Any]]:
    """
    Get apps and websites usage for a date range.

    Args:
        start_time: Start of period in ISO8601 datetime format.
        end_time: End of period in ISO8601 datetime format.
        api_url: Rize GraphQL API endpoint.
        api_key: Rize API key.
        timeout: Request timeout in seconds.

    Returns:
        List of apps and websites with usage details.

    Examples:
        Get apps and websites for the last week:
        >>> entries = await get_apps_and_websites(
        ...     start_time="2024-01-15T00:00:00Z",
        ...     end_time="2024-01-22T00:00:00Z"
        ... )
    """
    query = """
        query GetAppsAndWebsites(
            $startTime: ISO8601DateTime
            $endTime: ISO8601DateTime
        ) {
            appsAndWebsites(startTime: $startTime, endTime: $endTime) {
                id
                title
                appName
                url
                urlHost
                timeSpent
                type
                source
                timeCategory {
                    name
                }
                trueTimeCategory {
                    name
                }
            }
        }
    """

    variables = {
        "startTime": start_time,
        "endTime": end_time,
    }

    result = await execute_graphql(
        query=query,
        variables=variables,
        operation_name="GetAppsAndWebsites",
        api_url=api_url,
        api_key=api_key,
        timeout=timeout,
    )

    entries: list[dict[str, Any]] = result.get("appsAndWebsites", [])
    return entries
