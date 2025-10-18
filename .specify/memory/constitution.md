<!--
Sync Impact Report:
- Version change: 1.0.1 → 1.1.0
- Modified principles:
  * Python & FastMCP Standards: Added Task Automation section requiring invoke library
  * Code Quality Gates: Updated to reference invoke tasks
  * Pre-commit Requirements: Updated to use invoke commands
- Added sections:
  * Task Automation (new subsection under Python & FastMCP Standards)
- Removed sections: None
- Templates requiring updates:
  ✅ plan-template.md (may reference invoke tasks in constitution check)
  ✅ spec-template.md (no changes needed)
  ✅ tasks-template.md (no changes needed)
  ✅ agent-file-template.md (no changes needed)
  ✅ checklist-template.md (no changes needed)
- Follow-up TODOs:
  * Create tasks.py file with standard invoke tasks (test, lint, format, typecheck, etc.)
-->

# Rize MCP Server Constitution

## Core Principles

### I. FastMCP-First Architecture

Every feature MUST be designed as a FastMCP tool or resource following the FastMCP library patterns. Tools MUST be:
- Self-contained functions decorated with `@mcp.tool()`
- Independently testable without server initialization
- Documented with clear docstrings for LLM consumption
- Type-annotated with pydantic models for input validation

**Rationale**: FastMCP's decorator pattern ensures tools are discoverable, validatable, and provide automatic schema generation for LLM clients.

### II. Type Safety (NON-NEGOTIABLE)

All code MUST use Python type hints and pydantic models for data validation. Type checking with mypy MUST pass with strict mode enabled (`--strict`).

Requirements:
- All function signatures MUST have complete type annotations
- Pydantic BaseModel MUST be used for all structured data
- No use of `Any` type unless explicitly justified in complexity tracking
- Generic types MUST be properly parameterized (e.g., `list[str]` not `list`)

**Rationale**: Type safety prevents runtime errors, enables better IDE support, and ensures data contract integrity between the MCP server and clients.

### III. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory for all features. The development cycle is:
1. Write tests that define expected behavior
2. Get user approval of test coverage
3. Verify tests FAIL (red phase)
4. Implement minimum code to pass tests (green phase)
5. Refactor while keeping tests green

Test categories required:
- **Unit tests**: Test individual tools in isolation using pytest
- **Integration tests**: Test tool interactions with external APIs (Rize API)
- **Contract tests**: Validate MCP protocol compliance and schema correctness

**Rationale**: Test-first development catches bugs early, serves as living documentation, and ensures refactoring safety.

### IV. MCP Protocol Compliance

All server functionality MUST strictly adhere to the Model Context Protocol specification:
- Tools MUST return JSON-serializable results
- Resources MUST use proper URI schemes
- Prompts MUST follow MCP prompt template format
- Error responses MUST use MCP error codes and structures

**Rationale**: Protocol compliance ensures interoperability with all MCP clients (Claude Desktop, IDEs, custom clients).

### V. Async-First Implementation

All I/O operations MUST use async/await patterns:
- External API calls (Rize GraphQL API) MUST use httpx async client
- File operations MUST use aiofiles where appropriate
- Tool implementations SHOULD be async unless synchronous execution is required
- FastMCP server MUST run with async transport

**Rationale**: Async operations prevent blocking, enable concurrent request handling, and provide better resource utilization for I/O-bound MCP servers.

### VI. GraphQL Schema Introspection

The server MUST use GraphQL introspection to dynamically discover and expose Rize API capabilities:
- Schema MUST be fetched and cached on server initialization
- Tools SHOULD be generated or validated against live schema
- Breaking changes in upstream API MUST be detected and reported
- Schema cache MUST support invalidation and refresh

**Rationale**: Dynamic schema handling ensures the MCP server stays synchronized with the Rize API without manual updates.

### VII. Observability & Debugging

All operations MUST be observable and debuggable:
- Structured logging using Python's logging module with JSON formatter
- Request/response payloads MUST be logged at DEBUG level
- Error contexts MUST include full traceback and relevant state
- MCP server MUST support --log-level flag for runtime verbosity control
- Performance metrics (API latency, cache hit rates) SHOULD be logged

**Rationale**: Comprehensive logging enables rapid debugging of production issues and performance optimization.

## Python & FastMCP Standards

### Task Automation

All project operations MUST be defined as invoke tasks in `tasks.py`:
- Task definitions MUST be in root `tasks.py` file
- Tasks MUST have descriptive docstrings for `invoke --list`
- Common operations (test, lint, format, typecheck, build, deploy) MUST be standardized
- Complex multi-step operations MUST be orchestrated via invoke tasks
- CI/CD pipelines MUST use invoke tasks for consistency with local development

**Rationale**: Invoke provides a consistent, discoverable, and self-documenting interface for all project operations, ensuring developers and CI systems use identical commands.

### Code Quality Gates

All code MUST pass these checks before merge (run via invoke tasks):
- `invoke lint` (`ruff check .`) with zero errors
- `invoke format --check` (`ruff format --check .`) with zero differences
- `invoke typecheck` (`mypy --strict .`) with zero errors
- `invoke test` (`pytest -v --cov=src --cov-report=term-missing`) with 100% coverage (NON-NEGOTIABLE)

Convenience task for all checks:
- `invoke check` runs lint, format --check, typecheck, and test in sequence

### Dependency Management

- Use `uv` for fast, reliable dependency resolution
- Pin exact versions in `pyproject.toml` for production dependencies
- Separate `dev` dependencies (testing, linting, type checking, invoke)
- Include `invoke` as a dev dependency for task automation
- Document all dependencies with justification in project README

Required dev dependencies:
- `invoke` - Task automation and orchestration
- `pytest` + `pytest-cov` - Testing and coverage
- `ruff` - Linting and formatting
- `mypy` - Type checking
- `httpx` - Async HTTP client for API calls
- `pydantic` - Data validation

### Python Version

- Target Python 3.11+ for modern async features and performance
- Use `pyproject.toml` to specify `requires-python = ">=3.11"`
- Leverage new features: structural pattern matching, improved error messages, faster asyncio

### FastMCP Best Practices

- One tool per logical operation (avoid mega-tools)
- Use descriptive tool names following verb-noun pattern (e.g., `query_transactions`, `create_transfer`)
- Provide detailed tool descriptions for LLM context
- Group related tools using server context or namespacing
- Implement proper error handling with user-friendly messages

## Development Workflow

### Feature Implementation Flow

1. **Specification**: Create or update spec.md with user stories and acceptance criteria
2. **Planning**: Run `/speckit.plan` to generate technical design and architecture
3. **Constitution Check**: Verify compliance with all principles (automated gate)
4. **Task Generation**: Run `/speckit.tasks` to create dependency-ordered implementation tasks
5. **Test-First**: Write tests for each task before implementation
6. **Implementation**: Execute tasks in dependency order, marking complete in tasks.md
7. **Validation**: Run full test suite, linting, type checking before PR
8. **Review**: Code review verifies constitution compliance and test coverage

### Branch Strategy

- Main branch: `main` (protected, requires passing checks)
- Feature branches: `###-feature-name` where ### is incremental ID
- Commit messages: Follow conventional commits (feat:, fix:, docs:, test:, refactor:)

### Pre-commit Requirements

All commits MUST pass local validation via invoke tasks:
- `invoke format` - Apply code formatting (auto-fix)
- `invoke check` - Run all quality gates (lint, typecheck, test)

Alternatively, run individual checks:
- `invoke test` - Run test suite with coverage
- `invoke lint` - Check code quality
- `invoke typecheck` - Validate type annotations

**Note**: Use `invoke format` to auto-fix formatting before committing, then `invoke check` to verify all gates pass.

## Governance

### Amendment Process

1. Propose change with rationale in constitution issue/PR
2. Identify affected templates and artifacts (plan, spec, tasks templates)
3. Document version bump type (MAJOR/MINOR/PATCH)
4. Update constitution and all dependent templates
5. Migrate existing features if breaking change (MAJOR)
6. Require approval from project maintainer
7. Update Sync Impact Report with changes

### Versioning Policy

- **MAJOR (X.0.0)**: Backward incompatible principle changes requiring code refactoring
- **MINOR (x.Y.0)**: New principles added or sections expanded without breaking existing code
- **PATCH (x.y.Z)**: Clarifications, typo fixes, formatting improvements

### Compliance Verification

- All PRs MUST reference constitution compliance in review checklist
- `/speckit.plan` includes automated Constitution Check gate
- CI pipeline MUST enforce code quality gates (linting, types, tests)
- Complexity violations MUST be documented in plan.md Complexity Tracking table
- Quarterly constitution review to ensure principles remain relevant

### Living Document

This constitution is a living document that evolves with the project. All team members are encouraged to propose improvements while maintaining stability through the formal amendment process.

**Version**: 1.1.0 | **Ratified**: 2025-10-18 | **Last Amended**: 2025-10-18
