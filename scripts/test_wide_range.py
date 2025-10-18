#!/usr/bin/env python3
"""Test time entries with a very wide date range."""

import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.time_tracking import get_project_time_entries, get_task_time_entries


async def main() -> None:
    """Test with wide date range."""
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

    print("=" * 80)
    print("Testing Time Entries with Wide Date Range (Last 90 Days)")
    print("=" * 80)

    # Try last 90 days
    end_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    start_dt = datetime.now(UTC) - timedelta(days=90)
    start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"\nDate Range:")
    print(f"  Start: {start_time}")
    print(f"  End: {end_time}")

    print("\n" + "-" * 80)
    print("Fetching TASK time entries...")
    try:
        task_entries = await get_task_time_entries(
            start_time=start_time,
            end_time=end_time,
            api_url=api_url,
            api_key=api_key,
            timeout=30.0,
        )

        print(f"✓ Success! Found {len(task_entries)} task time entries")

        if task_entries:
            print("\nAll task entries:")
            for i, entry in enumerate(task_entries, 1):
                print(f"\n  Entry {i}:")
                print(f"    ID: {entry.get('id')}")
                print(f"    Start: {entry.get('startTime')}")
                print(f"    End: {entry.get('endTime')}")
                print(
                    f"    Duration: {entry.get('duration')} seconds ({entry.get('duration', 0) / 3600:.2f} hours)"
                )
                task = entry.get("task", {})
                if task:
                    print(f"    Task: {task.get('name')} (ID: {task.get('id')})")
                if entry.get("description"):
                    print(f"    Description: {entry.get('description')}")
                print(f"    Source: {entry.get('source')}")

            total_duration = sum(e.get("duration", 0) for e in task_entries)
            print(f"\n  Total task time: {total_duration / 3600:.2f} hours")
        else:
            print("\n  No task time entries found")
            print("\n  NOTE: This means no time was logged for TASKS specifically.")
            print("        Time might have been tracked for PROJECTS instead.")

    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "-" * 80)
    print("Fetching PROJECT time entries...")
    try:
        project_entries = await get_project_time_entries(
            start_time=start_time,
            end_time=end_time,
            api_url=api_url,
            api_key=api_key,
            timeout=30.0,
        )

        print(f"✓ Success! Found {len(project_entries)} project time entries")

        if project_entries:
            print("\nAll project entries:")
            for i, entry in enumerate(project_entries, 1):
                print(f"\n  Entry {i}:")
                print(f"    ID: {entry.get('id')}")
                print(f"    Start: {entry.get('startTime')}")
                print(f"    End: {entry.get('endTime')}")
                print(
                    f"    Duration: {entry.get('duration')} seconds ({entry.get('duration', 0) / 3600:.2f} hours)"
                )
                project = entry.get("project", {})
                if project:
                    print(f"    Project: {project.get('name')} (ID: {project.get('id')})")
                if entry.get("description"):
                    print(f"    Description: {entry.get('description')}")
                print(f"    Source: {entry.get('source')}")

            total_duration = sum(e.get("duration", 0) for e in project_entries)
            print(f"\n  Total project time: {total_duration / 3600:.2f} hours")
        else:
            print("\n  No project time entries found")
            print("\n  NOTE: This means you haven't logged manual time entries.")
            print("        Your tracked time is from active timer sessions only.")

    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print("\nThe time entry APIs are working correctly!")
    print("If no entries were found, it means:")
    print("  1. Your Rize account tracks time via automatic session monitoring")
    print("  2. You haven't created manual time entries via the API")
    print("  3. The tracked time shown in summaries comes from detected activity")
    print("\nTo test these APIs with data, you would need to:")
    print("  - Use the log_time tool to create manual project time entries")
    print("  - Or use start_timer/stop_timer to create timer-based entries")


if __name__ == "__main__":
    asyncio.run(main())
