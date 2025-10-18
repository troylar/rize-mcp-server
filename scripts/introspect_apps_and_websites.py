#!/usr/bin/env python3
"""Introspect the AppsAndWebsites type to find correct fields."""

import asyncio
import json
from pathlib import Path

import httpx


async def main() -> None:
    """Introspect AppsAndWebsites type."""
    # Load API key
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
    print("Introspecting AppsAndWebsites Type")
    print("=" * 80)

    # Introspection query for AppsAndWebsites type
    query = """
        query IntrospectAppsAndWebsites {
            __type(name: "AppsAndWebsites") {
                name
                kind
                fields {
                    name
                    type {
                        name
                        kind
                        ofType {
                            name
                            kind
                        }
                    }
                }
            }
        }
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            api_url,
            json={"query": query},
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        result = response.json()

        if "errors" in result:
            print("\n✗ GraphQL Errors:")
            print(json.dumps(result["errors"], indent=2))
            return

        type_info = result.get("data", {}).get("__type")

        if not type_info:
            print("\n✗ Type 'AppsAndWebsites' not found")
            return

        print(f"\n✓ Type found: {type_info['name']}")
        print(f"  Kind: {type_info['kind']}")
        print(f"\n  Fields:")

        for field in type_info.get("fields", []):
            field_name = field["name"]
            field_type = field["type"]

            # Format the type
            if field_type.get("ofType"):
                type_str = f"{field_type['kind']}<{field_type['ofType']['name']}>"
            else:
                type_str = field_type.get("name", field_type["kind"])

            print(f"    - {field_name}: {type_str}")

        print("\n" + "=" * 80)
        print("Suggested GraphQL Query:")
        print("=" * 80)
        print("""
query GetAppsAndWebsites(
    $startTime: ISO8601DateTime
    $endTime: ISO8601DateTime
) {
    appsAndWebsites(startTime: $startTime, endTime: $endTime) {""")

        for field in type_info.get("fields", []):
            field_name = field["name"]
            print(f"        {field_name}")

        print("""    }
}
""")


if __name__ == "__main__":
    asyncio.run(main())
