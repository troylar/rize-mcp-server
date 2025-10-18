"""GraphQL query utilities and helpers."""

import re
from typing import Any

import httpx

from src.utils.retry import retry_with_backoff


def validate_graphql_query(query: str) -> bool:
    """
    Validate basic GraphQL query syntax.

    Args:
        query: GraphQL query string to validate.

    Returns:
        True if query appears syntactically valid, False otherwise.
    """
    if not query or not query.strip():
        return False

    # Basic validation: check for common GraphQL patterns
    query = query.strip()

    # Remove comments
    query_no_comments = re.sub(r"#.*$", "", query, flags=re.MULTILINE)

    # Check for basic structure (must have braces, optionally with keyword)
    return "{" in query_no_comments and "}" in query_no_comments


def build_introspection_query(include_deprecated: bool = False) -> str:
    """
    Build a GraphQL introspection query.

    Args:
        include_deprecated: Whether to include deprecated fields and types.

    Returns:
        Complete introspection query string.
    """
    deprecated_arg = "true" if include_deprecated else "false"

    return f"""
    query IntrospectionQuery {{
      __schema {{
        queryType {{ name }}
        mutationType {{ name }}
        subscriptionType {{ name }}
        types {{
          ...FullType
        }}
        directives {{
          name
          description
          locations
          args {{
            ...InputValue
          }}
        }}
      }}
    }}

    fragment FullType on __Type {{
      kind
      name
      description
      fields(includeDeprecated: {deprecated_arg}) {{
        name
        description
        args {{
          ...InputValue
        }}
        type {{
          ...TypeRef
        }}
        isDeprecated
        deprecationReason
      }}
      inputFields {{
        ...InputValue
      }}
      interfaces {{
        ...TypeRef
      }}
      enumValues(includeDeprecated: {deprecated_arg}) {{
        name
        description
        isDeprecated
        deprecationReason
      }}
      possibleTypes {{
        ...TypeRef
      }}
    }}

    fragment InputValue on __InputValue {{
      name
      description
      type {{ ...TypeRef }}
      defaultValue
    }}

    fragment TypeRef on __Type {{
      kind
      name
      ofType {{
        kind
        name
        ofType {{
          kind
          name
          ofType {{
            kind
            name
            ofType {{
              kind
              name
              ofType {{
                kind
                name
                ofType {{
                  kind
                  name
                  ofType {{
                    kind
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """


@retry_with_backoff(max_attempts=3, base_delay=1.0, max_delay=4.0)
async def execute_graphql(  # noqa: PLR0913
    query: str,
    variables: dict[str, Any] | None = None,
    operation_name: str | None = None,
    api_url: str = "",
    api_key: str = "",
    timeout: float = 30.0,  # noqa: ASYNC109
) -> dict[str, Any]:
    """
    Execute a GraphQL query against the Rize API with retry logic.

    Args:
        query: GraphQL query string.
        variables: Optional query variables.
        operation_name: Optional operation name.
        api_url: GraphQL API endpoint URL.
        api_key: API authentication key.
        timeout: Request timeout in seconds.

    Returns:
        Query result data dictionary.

    Raises:
        ValueError: If GraphQL errors are returned.
        httpx.HTTPError: On network or HTTP errors.
    """
    payload: dict[str, Any] = {"query": query}

    if variables:
        payload["variables"] = variables

    if operation_name:
        payload["operationName"] = operation_name

    async with httpx.AsyncClient() as client:
        response = await client.post(
            api_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            error_msg = f"GraphQL errors: {data['errors']}"
            raise ValueError(error_msg)

        result: dict[str, Any] = data.get("data", {})
        return result
