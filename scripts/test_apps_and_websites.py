#!/usr/bin/env python3
"""Test apps and websites query with real Rize API."""

import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.time_tracking import get_apps_and_websites


async def main() -> None:
    """Test apps and websites query."""
    # Load API key from Cursor config
    config_path = Path.home() / ".cursor" / "mcp.json"
    api_key = ""
    api_url = "https://api.rize.io/api/v1/graphql"

    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            api_key = (
                config.get("mcpServers", {})
                .get("rize", {})
                .get("env", {})
                .get("RIZE_API_KEY", "")
            )

    print("=" * 80)
    print("Testing Apps and Websites Query with Real Rize API")
    print("=" * 80)

    # Test with last 7 days
    end_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    start_dt = datetime.now(UTC) - timedelta(days=7)
    start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"\nDate Range:")
    print(f"  Start: {start_time}")
    print(f"  End: {end_time}")
    print("\nCalling get_apps_and_websites()...")

    try:
        result = await get_apps_and_websites(
            start_time=start_time,
            end_time=end_time,
            api_url=api_url,
            api_key=api_key,
            timeout=30.0,
        )

        print(f"\n✓ Success! Retrieved {len(result)} apps and websites")

        if result:
            # Group by type
            apps = [item for item in result if item.get("type") == "app"]
            websites = [item for item in result if item.get("type") == "website"]

            print(f"\n  Apps: {len(apps)}")
            print(f"  Websites: {len(websites)}")

            # Show top 10 by time spent
            sorted_by_time = sorted(result, key=lambda x: x.get("timeSpent", 0), reverse=True)

            print(f"\n  Top 10 by Time Spent:")
            for i, item in enumerate(sorted_by_time[:10], 1):
                title = item.get("title", "Untitled")
                app_name = item.get("appName")
                url_host = item.get("urlHost")
                time_spent = item.get("timeSpent", 0)
                hours = time_spent / 3600
                category = item.get("timeCategory", {}).get("name", "Uncategorized")
                item_type = item.get("type", "unknown")
                source = item.get("source", "unknown")

                # Determine display name
                if app_name:
                    display_name = f"{app_name} (app)"
                elif url_host:
                    display_name = f"{url_host} (website)"
                else:
                    display_name = title

                print(f"\n    {i}. {display_name}")
                print(f"       Type: {item_type} | Source: {source}")
                print(f"       Time: {hours:.2f} hours ({time_spent} seconds)")
                print(f"       Category: {category}")

            # Calculate total time
            total_time = sum(item.get("timeSpent", 0) for item in result)
            total_hours = total_time / 3600
            print(f"\n  Total Time: {total_hours:.2f} hours")

        else:
            print("\n  No apps and websites found")
            print("\n  This could mean:")
            print("    - No activity tracked in this period")
            print("    - The query fields might need adjustment")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print(f"Error type: {type(e).__name__}")

        # Check if it's a GraphQL field error
        if "GraphQL errors" in str(e):
            print("\n  This might be a field mismatch.")
            print("  The AppsAndWebsites type might have different fields.")
            print("  Try using GraphQL introspection to see actual fields.")

        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
