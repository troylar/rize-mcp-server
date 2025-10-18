# Implementation Plan: Rize MCP Server with GraphQL Support

**Branch**: `002-rize-mcp-server` | **Date**: 2025-10-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-rize-mcp-server/spec.md`

## Summary

Build a Model Context Protocol (MCP) server that exposes the Rize GraphQL API to LLM agents (primarily Claude Desktop). The server will support schema introspection, query execution with variables/filtering/pagination, and comprehensive error handling with retry logic. All functionality will be exposed through FastMCP tools with full type safety, async operations, and 100% test coverage.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: fastmcp, httpx (async), pydantic, pydantic-settings
**Storage**: In-memory + disk cache for GraphQL schema (temporary files)
**Testing**: pytest, pytest-asyncio, pytest-cov, pytest-mock
**Target Platform**: Cross-platform (macOS, Linux, Windows) - runs as MCP server process
**Project Type**: Single project (MCP server)
**Performance Goals**: <3s query response (95th percentile), <10s schema introspection (cold), <1s cached schema access
**Constraints**: 30s HTTP timeout, 60s max rate limit wait, 1000 record limit per query, 100% test coverage, mypy strict mode
**Scale/Scope**: ~6 MCP tools, support for all Rize GraphQL operations, 10+ concurrent queries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: FastMCP-First Architecture
- ✅ **PASS**: All functionality exposed as `@mcp.tool()` decorated functions
- ✅ **PASS**: Tools independently testable (unit tests for each tool)
- ✅ **PASS**: Tools documented with docstrings for LLM consumption
- ✅ **PASS**: Pydantic models for input validation (GraphQL query params, variables)

### Principle II: Type Safety (NON-NEGOTIABLE)
- ✅ **PASS**: All functions type-annotated (mypy --strict enforced)
- ✅ **PASS**: Pydantic BaseModel for structured data (Settings, QueryRequest, QueryResponse, SchemaCache)
- ✅ **PASS**: No `Any` type usage (all generics properly parameterized)
- ✅ **PASS**: Generic types parameterized (dict[str, Any], list[str])

### Principle III: Test-First Development (NON-NEGOTIABLE)
- ✅ **PASS**: TDD workflow required (tests → approval → fail → implement → pass)
- ✅ **PASS**: Unit tests for all tools in isolation
- ✅ **PASS**: Integration tests for Rize API interactions
- ✅ **PASS**: Contract tests for MCP protocol compliance
- ✅ **PASS**: 100% coverage enforced via pytest-cov

### Principle IV: MCP Protocol Compliance
- ✅ **PASS**: Tools return JSON-serializable results (pydantic .dict())
- ✅ **PASS**: Error responses use MCP error structures
- ⚠️  **DEFERRED**: Resources/Prompts not required for MVP (focus on tools first)

### Principle V: Async-First Implementation
- ✅ **PASS**: httpx AsyncClient for all Rize API calls
- ✅ **PASS**: aiofiles for disk cache I/O
- ✅ **PASS**: All tools async (await-based)
- ✅ **PASS**: FastMCP async transport

### Principle VI: GraphQL Schema Introspection
- ✅ **PASS**: Schema fetched on server init
- ✅ **PASS**: Schema cached (in-memory + disk)
- ✅ **PASS**: Cache invalidation/refresh supported
- ✅ **PASS**: Tools validated against schema

### Principle VII: Observability & Debugging
- ✅ **PASS**: Structured JSON logging
- ✅ **PASS**: DEBUG level for full payloads, INFO for metadata
- ✅ **PASS**: Credential redaction enforced
- ✅ **PASS**: --log-level flag support
- ✅ **PASS**: Performance metrics logged (latency, cache hits)

### Task Automation
- ✅ **PASS**: invoke tasks.py already created (test, lint, format, typecheck, check)
- ✅ **PASS**: Descriptive docstrings in tasks
- ✅ **PASS**: CI/CD will use invoke tasks

### Code Quality Gates
- ✅ **PASS**: invoke lint (ruff check)
- ✅ **PASS**: invoke format (ruff format)
- ✅ **PASS**: invoke typecheck (mypy --strict)
- ✅ **PASS**: invoke test (pytest 100% coverage)

**Constitution Check Result**: ✅ **ALL GATES PASS** - No violations, no complexity tracking needed.

## Project Structure

### Documentation (this feature)

```
specs/002-rize-mcp-server/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (completed)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (entities and cache structures)
├── quickstart.md        # Phase 1 output (user setup guide)
├── contracts/           # Phase 1 output (MCP tool schemas)
│   ├── tool-query-rize.json
│   ├── tool-get-schema.json
│   ├── tool-introspect-type.json
│   └── tool-execute-query.json
└── checklists/
    └── requirements.md  # Specification quality checklist (completed)
```

### Source Code (repository root)

```
src/
├── __init__.py          # Package init with version
├── server.py            # Main FastMCP server entry point
├── config.py            # Pydantic settings (RIZE_API_KEY, etc.)
├── tools/               # MCP tools
│   ├── __init__.py
│   ├── schema.py        # get_schema, introspect_type tools
│   ├── query.py         # query_rize, execute_custom_query tools
│   └── cache.py         # Schema cache management
├── models/              # Pydantic models
│   ├── __init__.py
│   ├── query.py         # QueryRequest, QueryResponse models
│   ├── schema.py        # SchemaCache, GraphQLType models
│   └── errors.py        # RizeError, RateLimitError models
└── utils/               # Utilities
    ├── __init__.py
    ├── graphql.py       # GraphQL query builder/validator
    ├── retry.py         # Exponential backoff retry logic
    └── logging.py       # Structured JSON logger setup

tests/
├── unit/                # Unit tests (fast, isolated)
│   ├── test_tools_schema.py
│   ├── test_tools_query.py
│   ├── test_cache.py
│   ├── test_retry.py
│   └── test_graphql.py
├── integration/         # Integration tests (Rize API calls)
│   ├── test_rize_api.py
│   └── test_schema_introspection.py
└── contract/            # MCP protocol compliance tests
    └── test_mcp_protocol.py
```

**Structure Decision**: Single project structure selected. This is an MCP server (not a web app or mobile app), so we use the standard `src/` and `tests/` layout at the repository root. The codebase is organized by functionality (tools, models, utils) rather than layers, following FastMCP best practices.

## Complexity Tracking

*No complexity tracking required - all constitution checks pass without violations.*

---

## Phase 0: Research & Technology Decisions

### Research Areas

1. **FastMCP Best Practices** - Tool design patterns, error handling, async operations
2. **GraphQL Client Patterns** - httpx-based GraphQL queries, introspection queries
3. **Schema Caching Strategy** - In-memory + disk persistence, TTL management, aiofiles usage
4. **Retry Logic Implementation** - Exponential backoff with asyncio, Retry-After header handling
5. **Structured Logging** - JSON logging with Python logging module, credential redaction

### Output

See [research.md](./research.md) for detailed findings.

---

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions.

Key entities:
- **Settings**: Pydantic settings from environment (API key, URL, timeouts, cache TTL)
- **QueryRequest**: GraphQL query with variables and operation name
- **QueryResponse**: Success data or error details
- **SchemaCache**: In-memory + disk schema storage with TTL
- **GraphQLType**: Schema type metadata (name, fields, kind)
- **RetryConfig**: Exponential backoff configuration

### MCP Tool Contracts

See [contracts/](./contracts/) directory for JSON schemas.

Tools to implement:
1. `get_rize_schema` - Fetch complete GraphQL schema (cached)
2. `introspect_type` - Get fields/types for specific GraphQL type
3. `query_customers` - Query customer data (common operation)
4. `query_transactions` - Query transaction data (common operation)
5. `query_accounts` - Query account data (common operation)
6. `execute_custom_query` - Execute arbitrary GraphQL query with variables

### Quickstart Guide

See [quickstart.md](./quickstart.md) for user setup instructions.

---

## Next Steps

After this plan is complete:
1. Run `/speckit.tasks` to generate dependency-ordered implementation tasks
2. Implement tasks in TDD fashion (tests first, then code)
3. Validate with `invoke check` before each commit
4. Create PR when feature complete

---

**Phase 0 & Phase 1 artifacts will be generated next.**
