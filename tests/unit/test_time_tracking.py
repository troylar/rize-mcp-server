"""Unit tests for time tracking MCP tools."""

from datetime import date

import pytest
from pytest_mock import MockerFixture

from src.tools.time_tracking import (
    create_time_entry,
    get_apps_and_websites,
    get_current_session,
    get_project_time_entries,
    get_task_time_entries,
    get_time_summary,
    list_projects,
    start_timer,
    stop_timer,
)


class TestStartTimer:
    """Tests for start_timer tool."""

    @pytest.mark.asyncio
    async def test_start_timer_project_only(self, mocker: MockerFixture) -> None:
        """Test starting timer for a project."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "startSessionTime": {
                "id": "session_123",
                "project": {"id": "proj_abc", "name": "Test Project"},
                "task": None,
                "startedAt": "2024-01-15T10:00:00Z",
            }
        }

        # Act
        result = await start_timer(
            project_id="proj_abc", api_url="https://api.test", api_key="key_test"
        )

        # Assert
        assert result["id"] == "session_123"
        assert result["project"]["id"] == "proj_abc"
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert call_args[1]["variables"]["input"]["projectId"] == "proj_abc"

    @pytest.mark.asyncio
    async def test_start_timer_with_task(self, mocker: MockerFixture) -> None:
        """Test starting timer for a project and task."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "startSessionTime": {
                "id": "session_123",
                "project": {"id": "proj_abc", "name": "Test Project"},
                "task": {"id": "task_xyz", "name": "Test Task"},
                "startedAt": "2024-01-15T10:00:00Z",
            }
        }

        # Act
        result = await start_timer(
            project_id="proj_abc",
            task_id="task_xyz",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert result["task"]["id"] == "task_xyz"
        call_args = mock_execute.call_args
        assert call_args[1]["variables"]["input"]["taskId"] == "task_xyz"


class TestStopTimer:
    """Tests for stop_timer tool."""

    @pytest.mark.asyncio
    async def test_stop_timer(self, mocker: MockerFixture) -> None:
        """Test stopping the current timer."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "stopSessionTime": {
                "id": "session_123",
                "project": {"id": "proj_abc", "name": "Test Project"},
                "task": None,
                "startedAt": "2024-01-15T10:00:00Z",
                "stoppedAt": "2024-01-15T12:30:00Z",
                "duration": 9000,
            }
        }

        # Act
        result = await stop_timer(api_url="https://api.test", api_key="key_test")

        # Assert
        assert result["id"] == "session_123"
        assert result["duration"] == 9000
        assert result["stoppedAt"] is not None
        mock_execute.assert_called_once()


class TestGetCurrentSession:
    """Tests for get_current_session tool."""

    @pytest.mark.asyncio
    async def test_get_current_session_active(self, mocker: MockerFixture) -> None:
        """Test getting an active session."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "currentSession": {
                "id": "session_123",
                "title": "Working on feature",
                "description": None,
                "type": "manual",
                "source": "web",
                "startTime": "2024-01-15T10:00:00Z",
                "endTime": "2024-01-15T11:00:00Z",
            }
        }

        # Act
        result = await get_current_session(api_url="https://api.test", api_key="key_test")

        # Assert
        assert result is not None
        assert result["id"] == "session_123"
        assert result["startTime"] == "2024-01-15T10:00:00Z"
        assert result["title"] == "Working on feature"

    @pytest.mark.asyncio
    async def test_get_current_session_none(self, mocker: MockerFixture) -> None:
        """Test when no session is active."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {"currentSession": None}

        # Act
        result = await get_current_session(api_url="https://api.test", api_key="key_test")

        # Assert
        assert result is None


class TestCreateTimeEntry:
    """Tests for create_time_entry tool."""

    @pytest.mark.asyncio
    async def test_create_time_entry_basic(self, mocker: MockerFixture) -> None:
        """Test creating a basic time entry."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "createProjectTimeEntry": {
                "id": "entry_123",
                "project": {"id": "proj_abc", "name": "Test Project"},
                "task": None,
                "date": "2024-01-15",
                "hours": 3.5,
                "description": None,
            }
        }

        # Act
        result = await create_time_entry(
            project_id="proj_abc",
            hours=3.5,
            entry_date="2024-01-15",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert result["id"] == "entry_123"
        assert result["hours"] == 3.5
        call_args = mock_execute.call_args
        assert call_args[1]["variables"]["input"]["hours"] == 3.5
        assert call_args[1]["variables"]["input"]["date"] == "2024-01-15"

    @pytest.mark.asyncio
    async def test_create_time_entry_with_task_and_description(self, mocker: MockerFixture) -> None:
        """Test creating a time entry with task and description."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "createProjectTimeEntry": {
                "id": "entry_123",
                "project": {"id": "proj_abc", "name": "Test Project"},
                "task": {"id": "task_xyz", "name": "Test Task"},
                "date": "2024-01-15",
                "hours": 2.0,
                "description": "Implemented feature X",
            }
        }

        # Act
        result = await create_time_entry(
            project_id="proj_abc",
            hours=2.0,
            entry_date="2024-01-15",
            task_id="task_xyz",
            description="Implemented feature X",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert result["task"]["id"] == "task_xyz"
        assert result["description"] == "Implemented feature X"

    @pytest.mark.asyncio
    async def test_create_time_entry_with_date_object(self, mocker: MockerFixture) -> None:
        """Test creating a time entry with a date object."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "createProjectTimeEntry": {
                "id": "entry_123",
                "project": {"id": "proj_abc", "name": "Test Project"},
                "task": None,
                "date": "2024-01-15",
                "hours": 1.5,
                "description": None,
            }
        }

        # Act
        result = await create_time_entry(
            project_id="proj_abc",
            hours=1.5,
            entry_date=date(2024, 1, 15),
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert result["date"] == "2024-01-15"
        call_args = mock_execute.call_args
        assert call_args[1]["variables"]["input"]["date"] == "2024-01-15"


class TestListProjects:
    """Tests for list_projects tool."""

    @pytest.mark.asyncio
    async def test_list_all_projects(self, mocker: MockerFixture) -> None:
        """Test listing all projects."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "projects": {
                "edges": [
                    {
                        "node": {
                            "id": "proj_1",
                            "name": "Project 1",
                            "status": "active",
                            "color": "#ff0000",
                            "emoji": "🚀",
                            "client": {"id": "client_a", "name": "Client A"},
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-10T00:00:00Z",
                            "lastUsedAt": "2024-01-15T00:00:00Z",
                        }
                    },
                    {
                        "node": {
                            "id": "proj_2",
                            "name": "Project 2",
                            "status": "active",
                            "color": "#00ff00",
                            "emoji": "💡",
                            "client": {"id": "client_b", "name": "Client B"},
                            "createdAt": "2024-01-05T00:00:00Z",
                            "updatedAt": "2024-01-12T00:00:00Z",
                            "lastUsedAt": "2024-01-16T00:00:00Z",
                        }
                    },
                ]
            }
        }

        # Act
        result = await list_projects(api_url="https://api.test", api_key="key_test")

        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "proj_1"
        assert result[1]["id"] == "proj_2"


class TestGetTimeSummary:
    """Tests for get_time_summary tool."""

    @pytest.mark.asyncio
    async def test_get_time_summary_date_range(self, mocker: MockerFixture) -> None:
        """Test getting time summary for a date range."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "summaries": {
                "trackedTime": 145800,  # 40.5 hours in seconds
                "workHours": 145800,
                "focusTime": 108000,  # 30 hours
                "meetingTime": 37800,  # 10.5 hours
                "breakTime": 0,
                "trackedTimeAverage": 20828.57,
                "workHoursAverage": 20828.57,
                "focusTimeAverage": 15428.57,
                "meetingTimeAverage": 5400.0,
                "breakTimeAverage": 0.0,
                "categories": [
                    {"category": {"name": "Development"}, "timeSpent": 108000},
                    {"category": {"name": "Meetings"}, "timeSpent": 37800},
                ],
                "buckets": [
                    {
                        "date": "2024-01-01",
                        "trackedTime": 28800,
                        "workHours": 28800,
                        "focusTime": 21600,
                        "meetingTime": 7200,
                        "breakTime": 0,
                    },
                ],
            }
        }

        # Act
        result = await get_time_summary(
            start_date="2024-01-01",
            end_date="2024-01-07",
            bucket_size="day",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert result["trackedTime"] == 145800
        assert len(result["categories"]) == 2
        assert len(result["buckets"]) == 1

    @pytest.mark.asyncio
    async def test_get_time_summary_with_date_objects(self, mocker: MockerFixture) -> None:
        """Test getting time summary with date objects."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "summaries": {
                "trackedTime": 36000,
                "workHours": 36000,
                "focusTime": 36000,
                "meetingTime": 0,
                "breakTime": 0,
                "trackedTimeAverage": 36000.0,
                "workHoursAverage": 36000.0,
                "focusTimeAverage": 36000.0,
                "meetingTimeAverage": 0.0,
                "breakTimeAverage": 0.0,
                "categories": [],
                "buckets": [],
            }
        }

        # Act
        await get_time_summary(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
            bucket_size="day",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        call_args = mock_execute.call_args
        assert call_args[1]["variables"]["startDate"] == "2024-01-01"
        assert call_args[1]["variables"]["endDate"] == "2024-01-07"
        assert call_args[1]["variables"]["bucketSize"] == "day"


class TestGetTaskTimeEntries:
    """Tests for get_task_time_entries tool."""

    @pytest.mark.asyncio
    async def test_get_task_time_entries(self, mocker: MockerFixture) -> None:
        """Test getting task time entries for a date range."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "taskTimeEntries": [
                {
                    "id": "entry_1",
                    "startTime": "2024-01-15T10:00:00Z",
                    "endTime": "2024-01-15T12:00:00Z",
                    "duration": 7200,
                    "description": "Worked on feature X",
                    "source": "timer",
                    "task": {"id": "task_123", "name": "Feature X"},
                    "createdAt": "2024-01-15T10:00:00Z",
                    "updatedAt": "2024-01-15T12:00:00Z",
                },
                {
                    "id": "entry_2",
                    "startTime": "2024-01-16T14:00:00Z",
                    "endTime": "2024-01-16T16:30:00Z",
                    "duration": 9000,
                    "description": None,
                    "source": "manual",
                    "task": {"id": "task_456", "name": "Feature Y"},
                    "createdAt": "2024-01-16T14:00:00Z",
                    "updatedAt": "2024-01-16T16:30:00Z",
                },
            ]
        }

        # Act
        result = await get_task_time_entries(
            start_time="2024-01-15T00:00:00Z",
            end_time="2024-01-22T00:00:00Z",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "entry_1"
        assert result[0]["duration"] == 7200
        assert result[0]["task"]["name"] == "Feature X"
        assert result[1]["id"] == "entry_2"
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert call_args[1]["variables"]["startTime"] == "2024-01-15T00:00:00Z"
        assert call_args[1]["variables"]["endTime"] == "2024-01-22T00:00:00Z"

    @pytest.mark.asyncio
    async def test_get_task_time_entries_empty(self, mocker: MockerFixture) -> None:
        """Test getting task time entries when none exist."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {"taskTimeEntries": []}

        # Act
        result = await get_task_time_entries(
            start_time="2024-01-15T00:00:00Z",
            end_time="2024-01-22T00:00:00Z",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert len(result) == 0


class TestGetProjectTimeEntries:
    """Tests for get_project_time_entries tool."""

    @pytest.mark.asyncio
    async def test_get_project_time_entries(self, mocker: MockerFixture) -> None:
        """Test getting project time entries for a date range."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "projectTimeEntries": [
                {
                    "id": "entry_1",
                    "startTime": "2024-01-15T10:00:00Z",
                    "endTime": "2024-01-15T12:00:00Z",
                    "duration": 7200,
                    "description": "Development work",
                    "source": "timer",
                    "project": {"id": "proj_abc", "name": "Test Project"},
                    "createdAt": "2024-01-15T10:00:00Z",
                    "updatedAt": "2024-01-15T12:00:00Z",
                },
                {
                    "id": "entry_2",
                    "startTime": "2024-01-16T14:00:00Z",
                    "endTime": "2024-01-16T16:30:00Z",
                    "duration": 9000,
                    "description": "Code review",
                    "source": "manual",
                    "project": {"id": "proj_xyz", "name": "Another Project"},
                    "createdAt": "2024-01-16T14:00:00Z",
                    "updatedAt": "2024-01-16T16:30:00Z",
                },
            ]
        }

        # Act
        result = await get_project_time_entries(
            start_time="2024-01-15T00:00:00Z",
            end_time="2024-01-22T00:00:00Z",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "entry_1"
        assert result[0]["duration"] == 7200
        assert result[0]["project"]["name"] == "Test Project"
        assert result[1]["id"] == "entry_2"
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert call_args[1]["variables"]["startTime"] == "2024-01-15T00:00:00Z"
        assert call_args[1]["variables"]["endTime"] == "2024-01-22T00:00:00Z"

    @pytest.mark.asyncio
    async def test_get_project_time_entries_empty(self, mocker: MockerFixture) -> None:
        """Test getting project time entries when none exist."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {"projectTimeEntries": []}

        # Act
        result = await get_project_time_entries(
            start_time="2024-01-15T00:00:00Z",
            end_time="2024-01-22T00:00:00Z",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert len(result) == 0


class TestGetAppsAndWebsites:
    """Tests for get_apps_and_websites tool."""

    @pytest.mark.asyncio
    async def test_get_apps_and_websites(self, mocker: MockerFixture) -> None:
        """Test getting apps and websites for a date range."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {
            "appsAndWebsites": [
                {
                    "id": "aw_1",
                    "title": "Visual Studio Code",
                    "appName": "Visual Studio Code",
                    "url": None,
                    "urlHost": None,
                    "timeSpent": 7200,
                    "type": "app",
                    "source": "desktop",
                    "timeCategory": {"name": "Development"},
                    "trueTimeCategory": {"name": "Development"},
                },
                {
                    "id": "aw_2",
                    "title": "GitHub",
                    "appName": None,
                    "url": "https://github.com",
                    "urlHost": "github.com",
                    "timeSpent": 3600,
                    "type": "website",
                    "source": "browser",
                    "timeCategory": {"name": "Development"},
                    "trueTimeCategory": {"name": "Development"},
                },
                {
                    "id": "aw_3",
                    "title": "Slack",
                    "appName": "Slack",
                    "url": None,
                    "urlHost": None,
                    "timeSpent": 1800,
                    "type": "app",
                    "source": "desktop",
                    "timeCategory": {"name": "Communication"},
                    "trueTimeCategory": {"name": "Communication"},
                },
            ]
        }

        # Act
        result = await get_apps_and_websites(
            start_time="2024-01-15T00:00:00Z",
            end_time="2024-01-22T00:00:00Z",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert len(result) == 3
        assert result[0]["id"] == "aw_1"
        assert result[0]["title"] == "Visual Studio Code"
        assert result[0]["timeSpent"] == 7200
        assert result[0]["type"] == "app"
        assert result[0]["timeCategory"]["name"] == "Development"
        assert result[1]["id"] == "aw_2"
        assert result[1]["title"] == "GitHub"
        assert result[1]["type"] == "website"
        assert result[1]["urlHost"] == "github.com"
        assert result[2]["id"] == "aw_3"
        assert result[2]["title"] == "Slack"
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert call_args[1]["variables"]["startTime"] == "2024-01-15T00:00:00Z"
        assert call_args[1]["variables"]["endTime"] == "2024-01-22T00:00:00Z"

    @pytest.mark.asyncio
    async def test_get_apps_and_websites_empty(self, mocker: MockerFixture) -> None:
        """Test getting apps and websites when none exist."""
        # Arrange
        mock_execute = mocker.patch("src.tools.time_tracking.execute_graphql")
        mock_execute.return_value = {"appsAndWebsites": []}

        # Act
        result = await get_apps_and_websites(
            start_time="2024-01-15T00:00:00Z",
            end_time="2024-01-22T00:00:00Z",
            api_url="https://api.test",
            api_key="key_test",
        )

        # Assert
        assert len(result) == 0
