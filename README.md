# Rize MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that provides seamless integration with the [Rize](https://rize.io) time tracking and productivity API. Built with FastMCP, this server exposes Rize's powerful time tracking capabilities to AI assistants like Claude.

[![Tests](https://img.shields.io/badge/tests-109%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](htmlcov/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-latest-orange)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## Features

### 🎯 Time Tracking
- **Start/Stop Timer**: Control time tracking sessions for projects and tasks
- **Current Session**: Check active time tracking sessions
- **Manual Time Entry**: Log time retroactively with custom descriptions
- **Time Summaries**: Get detailed analytics with focus time, meeting time, and breakdowns

### 📊 Productivity Insights
- **Apps & Websites**: See which applications and websites you've used and for how long
- **Task Time Entries**: Retrieve time entries for specific tasks
- **Project Time Entries**: Get detailed project-level time tracking data
- **Categories**: Automatic categorization of activities (Development, Communication, etc.)

### 🏗️ Project Management
- **List Projects**: Browse all your Rize projects with client information
- **Project Details**: Access project metadata, status, and usage history

### 🛡️ Robust & Reliable
- **100% Test Coverage**: Comprehensive test suite with 109 passing tests
- **Automatic Retries**: Exponential backoff for failed requests
- **Rate Limiting**: Built-in rate limit handling
- **Error Recovery**: Graceful error handling with detailed logging
- **Input Validation**: Robust datetime parsing with automatic fallbacks

## Installation

### Prerequisites
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- A Rize account with API access

### Install from GitHub

```bash
# Clone the repository
git clone https://github.com/troylar/rize-mcp-server.git
cd rize-mcp-server

# Install dependencies
uv pip install -e .
```

## Configuration

### Get Your Rize API Key

1. Log in to your Rize account at [rize.io](https://rize.io)
2. Navigate to Settings → API
3. Generate a new API key
4. Copy the key for use in configuration

### Configure for Claude Desktop / Cursor

Add to your MCP configuration file:

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "rize": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/rize-mcp-server",
        "run",
        "rize-mcp"
      ],
      "env": {
        "RIZE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**For Cursor** (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "rize": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/rize-mcp-server",
        "run",
        "rize-mcp"
      ],
      "env": {
        "RIZE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RIZE_API_KEY` | ✅ Yes | - | Your Rize API authentication key |
| `RIZE_API_URL` | No | `https://api.rize.io/api/v1/graphql` | Rize GraphQL API endpoint |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | No | `json` | Log format (json or text) |
| `HTTP_TIMEOUT` | No | `30` | HTTP request timeout in seconds |
| `MAX_RECORDS_PER_QUERY` | No | `1000` | Maximum records per GraphQL query |

## Available Tools

### Timer Management

#### `start_timer`
Start a new time tracking session for a project or task.

```python
# Start timer for a project
start_timer(project_id="proj_abc123")

# Start timer for a specific task
start_timer(project_id="proj_abc123", task_id="task_xyz789")
```

#### `stop_timer`
Stop the currently running time tracking session.

```python
stop_timer()
```

#### `get_current_session`
Check if there's an active time tracking session.

```python
session = get_current_session()
if session:
    print(f"Currently tracking: {session['title']}")
```

### Manual Time Entry

#### `log_time`
Create a manual time entry for past work.

```python
# Log 3.5 hours for yesterday
log_time(
    project_id="proj_abc123",
    hours=3.5,
    entry_date="2024-01-15",
    description="Implemented login feature"
)
```

### Analytics & Reports

#### `get_time_summary`
Get comprehensive time tracking analytics for a date range.

```python
# Get this week's summary
summary = get_time_summary(
    start_date="2024-01-15",
    end_date="2024-01-21",
    bucket_size="day"  # Options: day, week, month
)

# Returns: tracked time, focus time, meeting time, break time, category breakdowns
```

#### `get_apps_and_websites`
See which apps and websites you've used and for how long.

```python
# Get last 30 days (default)
apps = get_apps_and_websites()

# Get specific date range
apps = get_apps_and_websites(
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-01-31T23:59:59Z"
)

# Returns structured response with:
# - entries: List of apps/websites with time spent
# - count: Number of entries
# - message: Human-readable status
```

#### `get_task_time_entries`
Retrieve detailed time entries for tasks.

```python
# Get task entries for last 30 days
entries = get_task_time_entries()

# Get specific date range
entries = get_task_time_entries(
    start_time="2024-01-15T00:00:00Z",
    end_time="2024-01-22T00:00:00Z"
)
```

#### `get_project_time_entries`
Retrieve detailed time entries for projects.

```python
# Get project entries for last 30 days
entries = get_project_time_entries()

# Get specific date range
entries = get_project_time_entries(
    start_time="2024-01-15T00:00:00Z",
    end_time="2024-01-22T00:00:00Z"
)
```

### Project Management

#### `list_projects`
Browse all your Rize projects.

```python
projects = list_projects()
# Returns: List of projects with IDs, names, status, client info, etc.
```

## Response Format

All time entry and analytics tools return structured responses:

```json
{
  "entries": [...],
  "count": 42,
  "start_time": "2024-01-15T00:00:00Z",
  "end_time": "2024-01-22T00:00:00Z",
  "message": "Found 42 task time entries"
}
```

This ensures AI assistants always receive meaningful responses, even when the entries list is empty.

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/troylar/rize-mcp-server.git
cd rize-mcp-server

# Install with development dependencies
uv pip install -e '.[dev]'

# Set up pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Run full test suite with coverage
invoke test

# Run specific test file
pytest tests/unit/test_time_tracking.py -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
invoke format

# Run linter
invoke lint

# Type checking
invoke typecheck

# Run all checks
invoke check
```

### Project Structure

```
rize-mcp-server/
├── src/
│   ├── config.py           # Configuration management
│   ├── server.py           # MCP server entry point
│   ├── models/             # Data models
│   │   ├── errors.py       # Error types
│   │   ├── query.py        # GraphQL query models
│   │   └── retry.py        # Retry configuration
│   ├── tools/              # MCP tool implementations
│   │   ├── query.py        # Custom GraphQL queries
│   │   └── time_tracking.py  # Time tracking operations
│   └── utils/              # Utility functions
│       ├── graphql.py      # GraphQL client
│       ├── logging.py      # JSON logging
│       └── retry.py        # Retry logic with backoff
├── tests/
│   ├── unit/               # Unit tests (100% coverage)
│   └── contract/           # MCP protocol compliance tests
└── scripts/                # Development scripts
```

## Architecture

### Technology Stack

- **FastMCP**: MCP server framework
- **httpx**: Async HTTP client for GraphQL
- **Pydantic**: Data validation and settings
- **pytest**: Testing framework
- **mypy**: Static type checking
- **ruff**: Fast Python linter and formatter

### Key Features

- **Async-first**: All I/O operations use async/await
- **Type-safe**: Full type hints with strict mypy checking
- **Tested**: 109 tests with 100% code coverage
- **Resilient**: Exponential backoff retry logic with rate limit handling
- **Observable**: Structured JSON logging with credential redaction
- **Configurable**: Environment-based configuration with validation

## Troubleshooting

### Common Issues

**"no result from tool" error in Cursor/Claude**

This was fixed in v1.0 by returning structured responses with metadata. Ensure you're running the latest version.

**Datetime parameter errors**

The server now includes robust datetime validation with automatic fallbacks. Empty or truncated datetime strings are automatically corrected to sensible defaults (last 30 days).

**Rate limit errors**

The server automatically handles rate limiting with exponential backoff. If you see persistent rate limit errors, check your API usage quota in your Rize account settings.

### Debugging

Enable debug logging to see detailed information:

```bash
export LOG_LEVEL=DEBUG
export LOG_FORMAT=text  # For human-readable logs
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`invoke check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Troy Larson**

- Email: [troy@troylarson.com](mailto:troy@troylarson.com)
- GitHub: [@troylar](https://github.com/troylar)

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) by Marvin AI
- Powered by [Rize](https://rize.io) time tracking API
- Follows the [Model Context Protocol](https://modelcontextprotocol.io) specification

## Support

For issues, questions, or contributions:

- 🐛 [Report a bug](https://github.com/troylar/rize-mcp-server/issues)
- 💡 [Request a feature](https://github.com/troylar/rize-mcp-server/issues)
- 📧 [Email support](mailto:troy@troylarson.com)

## Links

- [Rize API Documentation](https://docs.rize.io)
- [Rize GraphQL Explorer](https://api.rize.io/api/v1/graphiql)
- [Model Context Protocol Spec](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/troylar">Troy Larson</a>
</p>
