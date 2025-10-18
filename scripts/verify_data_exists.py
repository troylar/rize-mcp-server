#!/usr/bin/env python3
"""Verify Rize account has data and find when time entries exist."""

import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.time_tracking import (
    get_project_time_entries,
    get_task_time_entries,
    get_time_summary,
)


async def main() -> None:
    """Check for existing time data."""
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
    print("Checking for Rize Time Data")
    print("=" * 80)

    # Check time summary for last 90 days
    print("\nChecking time summary for last 90 days...")
    end_date = datetime.now(UTC).date().isoformat()
    start_date = (datetime.now(UTC) - timedelta(days=90)).date().isoformat()

    try:
        summary = await get_time_summary(
            start_date=start_date,
            end_date=end_date,
            bucket_size="day",
            api_url=api_url,
            api_key=api_key,
            timeout=30.0,
        )

        tracked_time = summary.get("trackedTime", 0)
        print(f"\nTotal tracked time in last 90 days: {tracked_time} seconds")
        print(f"That's {tracked_time / 3600:.2f} hours")

        buckets = summary.get("buckets", [])
        if buckets:
            print(f"\nFound {len(buckets)} days with data")
            days_with_time = [b for b in buckets if b.get("trackedTime", 0) > 0]
            print(f"Days with tracked time: {len(days_with_time)}")

            if days_with_time:
                print("\nMost recent days with tracked time:")
                for bucket in sorted(days_with_time, key=lambda x: x["date"], reverse=True)[:5]:
                    date = bucket["date"]
                    time_hours = bucket.get("trackedTime", 0) / 3600
                    print(f"  {date}: {time_hours:.2f} hours")

                # Try fetching time entries from the most recent active date
                latest_date = days_with_time[-1]["date"]
                print(f"\n\nTrying to fetch time entries around {latest_date}...")

                # Parse the date string properly - it includes timezone info
                # Format: "2025-10-18 01:00:00 -0400" -> "2025-10-18"
                date_only = latest_date.split()[0]  # Get just YYYY-MM-DD part
                start_time = f"{date_only}T00:00:00Z"
                end_dt = datetime.fromisoformat(date_only) + timedelta(days=1)
                end_time_dt = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

                task_entries = await get_task_time_entries(
                    start_time=start_time,
                    end_time=end_time_dt,
                    api_url=api_url,
                    api_key=api_key,
                    timeout=30.0,
                )

                project_entries = await get_project_time_entries(
                    start_time=start_time,
                    end_time=end_time_dt,
                    api_url=api_url,
                    api_key=api_key,
                    timeout=30.0,
                )

                print(f"\nTask time entries on {latest_date}: {len(task_entries)}")
                print(f"Project time entries on {latest_date}: {len(project_entries)}")

                if task_entries:
                    print("\nSample task entry:")
                    entry = task_entries[0]
                    print(f"  ID: {entry.get('id')}")
                    print(f"  Duration: {entry.get('duration')} seconds")
                    print(f"  Task: {entry.get('task', {}).get('name')}")

                if project_entries:
                    print("\nSample project entry:")
                    entry = project_entries[0]
                    print(f"  ID: {entry.get('id')}")
                    print(f"  Duration: {entry.get('duration')} seconds")
                    print(f"  Project: {entry.get('project', {}).get('name')}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
