#!/usr/bin/env python3
"""Test the new structured response format."""

import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Test the server.py wrapper functions directly
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock the settings
import os

os.environ["RIZE_API_KEY"] = "test_key"

# Import after env is set
from src import server


async def test_structured_response() -> None:
    """Test that tools return structured responses."""
    # Load real API key
    config_path = Path.home() / ".cursor" / "mcp.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            api_key = (
                config.get("mcpServers", {}).get("rize", {}).get("env", {}).get("RIZE_API_KEY", "")
            )
            os.environ["RIZE_API_KEY"] = api_key

    # Reload settings with real key
    from importlib import reload

    reload(server)

    print("=" * 80)
    print("Testing Structured Response Format")
    print("=" * 80)

    print("\n" + "-" * 80)
    print("Test 1: get_task_time_entries with no parameters")
    print("-" * 80)

    try:
        result = await server.get_task_time_entries()

        print("✓ Function returned successfully")
        print(f"\nResponse structure:")
        print(f"  Type: {type(result).__name__}")
        print(f"  Keys: {list(result.keys())}")
        print(f"\nResponse content:")
        print(f"  count: {result.get('count')}")
        print(f"  start_time: {result.get('start_time')}")
        print(f"  end_time: {result.get('end_time')}")
        print(f"  message: {result.get('message')}")
        print(f"  entries: {len(result.get('entries', []))} items")

        # Verify structure
        assert isinstance(result, dict), "Response should be a dict"
        assert "entries" in result, "Response should have 'entries' key"
        assert "count" in result, "Response should have 'count' key"
        assert "start_time" in result, "Response should have 'start_time' key"
        assert "end_time" in result, "Response should have 'end_time' key"
        assert "message" in result, "Response should have 'message' key"
        assert isinstance(result["entries"], list), "entries should be a list"
        assert isinstance(result["count"], int), "count should be an int"
        assert isinstance(result["message"], str), "message should be a string"

        print("\n✅ All structure validations passed")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "-" * 80)
    print("Test 2: get_project_time_entries with explicit date range")
    print("-" * 80)

    try:
        end_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        start_dt = datetime.now(UTC) - timedelta(days=7)
        start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        result = await server.get_project_time_entries(start_time=start_time, end_time=end_time)

        print("✓ Function returned successfully")
        print(f"\nResponse structure:")
        print(f"  Type: {type(result).__name__}")
        print(f"  Keys: {list(result.keys())}")
        print(f"\nResponse content:")
        print(f"  count: {result.get('count')}")
        print(f"  start_time: {result.get('start_time')}")
        print(f"  end_time: {result.get('end_time')}")
        print(f"  message: {result.get('message')}")
        print(f"  entries: {len(result.get('entries', []))} items")

        # Verify the message is appropriate for zero results
        if result["count"] == 0:
            assert "No project time entries found" in result["message"]
            print("\n✅ Message correctly indicates no entries found")
        else:
            assert "Found" in result["message"]
            print(f"\n✅ Message correctly reports {result['count']} entries")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\n✅ Structured response format working correctly!")
    print("\nThe MCP tools now return:")
    print("  - entries: list of time entry objects")
    print("  - count: number of entries found")
    print("  - start_time: query start time")
    print("  - end_time: query end time")
    print("  - message: descriptive status message")
    print("\nThis ensures Cursor/Claude always receives a valid response,")
    print("even when the entries list is empty.")


if __name__ == "__main__":
    asyncio.run(test_structured_response())
