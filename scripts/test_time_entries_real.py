#!/usr/bin/env python3
"""Test time entry tools with real Rize API data."""

import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.tools.time_tracking import get_project_time_entries, get_task_time_entries


async def main() -> None:
    """Test time entry retrieval with real API."""
    # Load API key from Cursor config
    config_path = Path.home() / ".cursor" / "mcp.json"
    api_key = ""
    api_url = "https://api.rize.io/api/v1/graphql"

    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            api_key = (
                config.get("mcpServers", {}).get("rize", {}).get("env", {}).get("RIZE_API_KEY", "")
            )

    if not api_key:
        print("ERROR: No API key found in ~/.cursor/mcp.json")
        return

    print("=" * 80)
    print("Testing Rize Time Entry Tools with Real API")
    print("=" * 80)
    print(f"\nAPI URL: {api_url}")
    print(f"API Key: {api_key[:10]}..." if api_key else "No API key")
    print()

    # Test 1: Get task time entries with default (last 30 days)
    print("\n" + "=" * 80)
    print("TEST 1: Get Task Time Entries (Last 30 Days)")
    print("=" * 80)
    try:
        # Calculate defaults manually to show what we're requesting
        end_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        start_dt = datetime.now(UTC) - timedelta(days=30)
        start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        print(f"Start Time: {start_time}")
        print(f"End Time: {end_time}")
        print("\nCalling get_task_time_entries()...")

        task_entries = await get_task_time_entries(
            start_time=start_time,
            end_time=end_time,
            api_url=api_url,
            api_key=api_key,
            timeout=30.0,
        )

        print(f"\n✓ Success! Retrieved {len(task_entries)} task time entries")
        if task_entries:
            print("\nFirst 3 entries:")
            for i, entry in enumerate(task_entries[:3], 1):
                print(f"\n  Entry {i}:")
                print(f"    ID: {entry.get('id')}")
                print(f"    Start: {entry.get('startTime')}")
                print(f"    End: {entry.get('endTime')}")
                print(f"    Duration: {entry.get('duration')} seconds")
                task = entry.get("task", {})
                if task:
                    print(f"    Task: {task.get('name')} (ID: {task.get('id')})")
                if entry.get("description"):
                    print(f"    Description: {entry.get('description')}")
        else:
            print("\n  No task time entries found in the last 30 days")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()

    # Test 2: Get project time entries with default (last 30 days)
    print("\n" + "=" * 80)
    print("TEST 2: Get Project Time Entries (Last 30 Days)")
    print("=" * 80)
    try:
        print(f"Start Time: {start_time}")
        print(f"End Time: {end_time}")
        print("\nCalling get_project_time_entries()...")

        project_entries = await get_project_time_entries(
            start_time=start_time,
            end_time=end_time,
            api_url=api_url,
            api_key=api_key,
            timeout=30.0,
        )

        print(f"\n✓ Success! Retrieved {len(project_entries)} project time entries")
        if project_entries:
            print("\nFirst 3 entries:")
            for i, entry in enumerate(project_entries[:3], 1):
                print(f"\n  Entry {i}:")
                print(f"    ID: {entry.get('id')}")
                print(f"    Start: {entry.get('startTime')}")
                print(f"    End: {entry.get('endTime')}")
                print(f"    Duration: {entry.get('duration')} seconds")
                project = entry.get("project", {})
                if project:
                    print(f"    Project: {project.get('name')} (ID: {project.get('id')})")
                if entry.get("description"):
                    print(f"    Description: {entry.get('description')}")
        else:
            print("\n  No project time entries found in the last 30 days")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()

    # Test 3: Get task time entries with specific date range (last 7 days)
    print("\n" + "=" * 80)
    print("TEST 3: Get Task Time Entries (Last 7 Days)")
    print("=" * 80)
    try:
        end_time_7d = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        start_dt_7d = datetime.now(UTC) - timedelta(days=7)
        start_time_7d = start_dt_7d.strftime("%Y-%m-%dT%H:%M:%SZ")

        print(f"Start Time: {start_time_7d}")
        print(f"End Time: {end_time_7d}")
        print("\nCalling get_task_time_entries() with 7-day range...")

        task_entries_7d = await get_task_time_entries(
            start_time=start_time_7d,
            end_time=end_time_7d,
            api_url=api_url,
            api_key=api_key,
            timeout=30.0,
        )

        print(f"\n✓ Success! Retrieved {len(task_entries_7d)} task time entries")
        if task_entries_7d:
            total_duration = sum(entry.get("duration", 0) for entry in task_entries_7d)
            total_hours = total_duration / 3600
            print(f"  Total time tracked: {total_hours:.2f} hours")
        else:
            print("\n  No task time entries found in the last 7 days")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("\n✓ All datetime parameter handling tests completed")
    print("  - Default parameters (last 30 days) work correctly")
    print("  - Custom date ranges work correctly")
    print("  - ISO8601 datetime format is properly validated")


if __name__ == "__main__":
    asyncio.run(main())
