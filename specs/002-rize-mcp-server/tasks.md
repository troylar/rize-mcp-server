# Tasks: Rize MCP Server with GraphQL Support

**Input**: Design documents from `/specs/002-rize-mcp-server/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Test-First Development (TDD) is REQUIRED per constitution (Principle III). All test tasks MUST be completed and FAILING before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root (per plan.md structure)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Verify pyproject.toml exists with correct dependencies (fastmcp, httpx, pydantic, pydantic-settings)
- [X] T002 Verify tasks.py exists with all required invoke tasks (test, lint, format, typecheck, check)
- [X] T003 Create src/ directory structure per plan.md (tools/, models/, utils/)
- [X] T004 Create tests/ directory structure (unit/, integration/, contract/)
- [X] T005 [P] Create src/__init__.py with version = "0.1.0"
- [X] T006 [P] Create src/tools/__init__.py
- [X] T007 [P] Create src/models/__init__.py
- [X] T008 [P] Create src/utils/__init__.py
- [X] T009 [P] Create tests/unit/__init__.py
- [X] T010 [P] Create tests/integration/__init__.py
- [X] T011 [P] Create tests/contract/__init__.py
- [X] T012 Verify .env.example exists with all required environment variables
- [X] T013 Run invoke format to ensure code formatting is configured
- [X] T014 Run invoke lint to verify linting configuration
- [X] T015 Run invoke typecheck to verify mypy strict mode configuration

**Checkpoint**: Project structure initialized, quality gates verified

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Configuration & Settings (Blocking)

- [X] T016 [P] Create src/config.py with Settings pydantic model per data-model.md
- [X] T017 [P] Create tests/unit/test_config.py with Settings validation tests
- [X] T018 Write failing test for Settings loading from environment variables in tests/unit/test_config.py
- [X] T019 Write failing test for Settings validation (missing required fields) in tests/unit/test_config.py
- [X] T020 Implement Settings class in src/config.py to pass tests (loads RIZE_API_KEY, etc.)
- [X] T021 Run invoke test to verify Settings tests pass with 100% coverage

### Error Models (Blocking)

- [X] T022 [P] Create src/models/errors.py with RizeError base class per data-model.md
- [X] T023 [P] Create tests/unit/test_errors.py
- [X] T024 Write failing test for RizeError model validation in tests/unit/test_errors.py
- [X] T025 Write failing test for GraphQLError model with locations/path in tests/unit/test_errors.py
- [X] T026 Write failing test for RateLimitError model with retry_after in tests/unit/test_errors.py
- [X] T027 Implement RizeError, GraphQLError, RateLimitError in src/models/errors.py to pass tests
- [X] T028 Run invoke test to verify error model tests pass

### Logging Infrastructure (Blocking)

- [X] T029 [P] Create src/utils/logging.py with JSONFormatter per research.md
- [X] T030 [P] Create tests/unit/test_logging.py
- [X] T031 Write failing test for JSONFormatter credential redaction in tests/unit/test_logging.py
- [X] T032 Write failing test for structured JSON log output in tests/unit/test_logging.py
- [X] T033 Implement JSONFormatter and setup_logging() in src/utils/logging.py to pass tests
- [X] T034 Run invoke test to verify logging tests pass

### Retry Logic (Blocking)

- [X] T035 [P] Create src/models/retry.py with RetryConfig model per data-model.md
- [X] T036 [P] Create src/utils/retry.py with retry_with_backoff decorator per research.md
- [X] T037 [P] Create tests/unit/test_retry.py
- [X] T038 Write failing test for exponential backoff delays (1s, 2s, 4s) in tests/unit/test_retry.py
- [X] T039 Write failing test for Retry-After header handling in tests/unit/test_retry.py
- [X] T040 Write failing test for max retry attempts enforcement in tests/unit/test_retry.py
- [X] T041 Implement RetryConfig model in src/models/retry.py
- [X] T042 Implement retry_with_backoff decorator in src/utils/retry.py to pass tests
- [X] T043 Run invoke test to verify retry logic tests pass

### GraphQL Utilities (Blocking)

- [X] T044 [P] Create src/utils/graphql.py with GraphQL query utilities
- [X] T045 [P] Create tests/unit/test_graphql.py
- [X] T046 Write failing test for GraphQL query validation in tests/unit/test_graphql.py
- [X] T047 Write failing test for GraphQL introspection query generation in tests/unit/test_graphql.py
- [X] T048 Implement execute_graphql() async function in src/utils/graphql.py with retry logic
- [X] T049 Implement build_introspection_query() in src/utils/graphql.py
- [X] T050 Run invoke test to verify GraphQL utility tests pass

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Query Rize Financial Data (Priority: P1) 🎯 MVP

**Goal**: Enable LLM agents to query Rize financial data (customers, transactions, accounts, transfers) through MCP tools

**Independent Test**: Configure MCP server in Claude Desktop, ask "Show me my Rize customers", receive properly formatted customer list

### Tests for User Story 1 (TDD - Write FIRST, ensure FAIL)

- [ ] T051 [P] [US1] Create tests/unit/test_tools_query.py
- [ ] T052 [P] [US1] Create tests/integration/test_rize_api.py
- [ ] T053 [P] [US1] Create tests/contract/test_mcp_protocol.py
- [ ] T054 [US1] Write failing unit test for execute_custom_query tool in tests/unit/test_tools_query.py
- [ ] T055 [US1] Write failing unit test for query parameter validation in tests/unit/test_tools_query.py
- [ ] T056 [US1] Write failing unit test for 1000 record limit enforcement in tests/unit/test_tools_query.py
- [ ] T057 [US1] Write failing integration test for Rize API customer query in tests/integration/test_rize_api.py
- [ ] T058 [US1] Write failing integration test for error handling (invalid credentials) in tests/integration/test_rize_api.py
- [ ] T059 [US1] Write failing contract test for MCP tool schema compliance in tests/contract/test_mcp_protocol.py
- [ ] T060 [US1] Run invoke test to verify all US1 tests FAIL (red phase)

### Data Models for User Story 1

- [ ] T061 [P] [US1] Create src/models/query.py with QueryRequest model per data-model.md
- [ ] T062 [P] [US1] Add QueryResponse model to src/models/query.py
- [ ] T063 [P] [US1] Add QueryMetadata model to src/models/query.py
- [ ] T064 [US1] Add unit tests for query models to tests/unit/test_models.py
- [ ] T065 [US1] Run invoke test to verify query model tests pass

### MCP Tools for User Story 1

- [ ] T066 [US1] Create src/tools/query.py
- [ ] T067 [US1] Implement execute_custom_query() tool with @mcp.tool() decorator in src/tools/query.py
- [ ] T068 [US1] Add QueryRequest validation and error handling to execute_custom_query()
- [ ] T069 [US1] Add 1000 record limit check to execute_custom_query()
- [ ] T070 [US1] Add logging (INFO metadata, DEBUG full payloads) to execute_custom_query()
- [ ] T071 [US1] Add retry logic integration (network errors, rate limits) to execute_custom_query()
- [ ] T072 [US1] Run invoke test to verify execute_custom_query tests pass (green phase)

### Server Integration for User Story 1

- [ ] T073 [US1] Update src/server.py to import and register execute_custom_query tool
- [ ] T074 [US1] Add FastMCP initialization with server name and version in src/server.py
- [ ] T075 [US1] Add main() function with logging setup and mcp.run() in src/server.py
- [ ] T076 [US1] Run invoke test to verify MCP protocol compliance tests pass
- [ ] T077 [US1] Run invoke check to verify 100% coverage and all quality gates pass

**Checkpoint**: User Story 1 complete and independently testable. MVP ready for deployment and demo.

---

## Phase 4: User Story 2 - Discover Available Rize Operations (Priority: P2)

**Goal**: Enable developers to discover available Rize API operations through schema introspection

**Independent Test**: Ask Claude "What Rize operations are available?", receive complete list of queryable entities with fields

### Tests for User Story 2 (TDD - Write FIRST, ensure FAIL)

- [ ] T078 [P] [US2] Create tests/unit/test_tools_schema.py
- [ ] T079 [P] [US2] Create tests/integration/test_schema_introspection.py
- [ ] T080 [US2] Write failing unit test for get_rize_schema tool in tests/unit/test_tools_schema.py
- [ ] T081 [US2] Write failing unit test for schema cache hit/miss logic in tests/unit/test_tools_schema.py
- [ ] T082 [US2] Write failing unit test for force_refresh parameter in tests/unit/test_tools_schema.py
- [ ] T083 [US2] Write failing unit test for introspect_type tool in tests/unit/test_tools_schema.py
- [ ] T084 [US2] Write failing integration test for schema introspection from Rize API in tests/integration/test_schema_introspection.py
- [ ] T085 [US2] Write failing integration test for schema cache persistence to disk in tests/integration/test_schema_introspection.py
- [ ] T086 [US2] Run invoke test to verify all US2 tests FAIL (red phase)

### Data Models for User Story 2

- [ ] T087 [P] [US2] Create src/models/schema.py with SchemaCache model per data-model.md
- [ ] T088 [P] [US2] Add GraphQLType model to src/models/schema.py
- [ ] T089 [P] [US2] Add GraphQLField model to src/models/schema.py
- [ ] T090 [P] [US2] Add GetSchemaParams model to src/models/tools.py (create file)
- [ ] T091 [P] [US2] Add IntrospectTypeParams model to src/models/tools.py
- [ ] T092 [US2] Add unit tests for schema models to tests/unit/test_models.py
- [ ] T093 [US2] Run invoke test to verify schema model tests pass

### Schema Cache Implementation

- [ ] T094 [P] [US2] Create tests/unit/test_cache.py
- [ ] T095 [US2] Write failing test for in-memory cache operations in tests/unit/test_cache.py
- [ ] T096 [US2] Write failing test for disk cache persistence with aiofiles in tests/unit/test_cache.py
- [ ] T097 [US2] Write failing test for TTL expiration logic in tests/unit/test_cache.py
- [ ] T098 [US2] Create src/tools/cache.py with SchemaCache class
- [ ] T099 [US2] Implement get() method in SchemaCache (check memory, then disk)
- [ ] T100 [US2] Implement set() method in SchemaCache (write to memory and disk with aiofiles)
- [ ] T101 [US2] Implement is_valid() and remaining_ttl() methods in SchemaCache
- [ ] T102 [US2] Run invoke test to verify cache tests pass (green phase)

### MCP Tools for User Story 2

- [ ] T103 [US2] Create src/tools/schema.py
- [ ] T104 [US2] Implement get_rize_schema() tool with @mcp.tool() decorator in src/tools/schema.py
- [ ] T105 [US2] Add schema cache integration to get_rize_schema()
- [ ] T106 [US2] Add force_refresh logic to bypass cache in get_rize_schema()
- [ ] T107 [US2] Add error handling for schema fetch failures in get_rize_schema()
- [ ] T108 [US2] Implement introspect_type() tool with @mcp.tool() decorator in src/tools/schema.py
- [ ] T109 [US2] Add type lookup logic from cached schema in introspect_type()
- [ ] T110 [US2] Add field extraction and formatting in introspect_type()
- [ ] T111 [US2] Add logging for schema operations (cache hits, fetch times)
- [ ] T112 [US2] Run invoke test to verify schema tool tests pass (green phase)

### Server Integration for User Story 2

- [ ] T113 [US2] Update src/server.py to import and register get_rize_schema tool
- [ ] T114 [US2] Update src/server.py to import and register introspect_type tool
- [ ] T115 [US2] Add schema cache initialization in server startup
- [ ] T116 [US2] Run invoke test to verify schema integration tests pass
- [ ] T117 [US2] Run invoke check to verify 100% coverage maintained

**Checkpoint**: User Story 2 complete and independently testable. Schema discovery functional.

---

## Phase 5: User Story 3 - Execute Complex GraphQL Queries (Priority: P3)

**Goal**: Enable advanced users to execute custom GraphQL queries with variables, filtering, and pagination

**Independent Test**: Provide custom GraphQL query with variables (filter transactions by date range), verify correct filtered results returned

### Tests for User Story 3 (TDD - Write FIRST, ensure FAIL)

- [ ] T118 [P] [US3] Add tests for query with variables to tests/unit/test_tools_query.py
- [ ] T119 [P] [US3] Add tests for pagination handling to tests/unit/test_tools_query.py
- [ ] T120 [US3] Write failing test for GraphQL query syntax validation in tests/unit/test_tools_query.py
- [ ] T121 [US3] Write failing test for variable substitution in tests/unit/test_tools_query.py
- [ ] T122 [US3] Write failing test for cursor-based pagination in tests/unit/test_tools_query.py
- [ ] T123 [US3] Write failing integration test for complex query with filters in tests/integration/test_rize_api.py
- [ ] T124 [US3] Write failing integration test for pagination (first N, then next N) in tests/integration/test_rize_api.py
- [ ] T125 [US3] Run invoke test to verify all US3 tests FAIL (red phase)

### GraphQL Query Enhancement

- [ ] T126 [US3] Add validate_graphql_syntax() function to src/utils/graphql.py
- [ ] T127 [US3] Add build_paginated_query() helper to src/utils/graphql.py
- [ ] T128 [US3] Add extract_pagination_info() helper to src/utils/graphql.py
- [ ] T129 [US3] Add tests for new GraphQL utilities to tests/unit/test_graphql.py
- [ ] T130 [US3] Run invoke test to verify GraphQL utility enhancements pass

### MCP Tools Enhancement for User Story 3

- [ ] T131 [US3] Add GraphQL syntax validation to execute_custom_query() in src/tools/query.py
- [ ] T132 [US3] Add variable validation and type checking to execute_custom_query()
- [ ] T133 [US3] Add pagination cursor extraction and response metadata to execute_custom_query()
- [ ] T134 [US3] Enhance error messages for invalid queries with specific guidance
- [ ] T135 [US3] Add examples to tool docstrings showing variables and pagination usage
- [ ] T136 [US3] Run invoke test to verify enhanced query tool tests pass (green phase)

### Server Integration for User Story 3

- [ ] T137 [US3] Update execute_custom_query tool registration with enhanced schema
- [ ] T138 [US3] Run invoke test to verify all User Story 3 tests pass
- [ ] T139 [US3] Run invoke check to verify 100% coverage maintained

**Checkpoint**: User Story 3 complete and independently testable. Advanced query features functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T140 [P] Add performance logging for all MCP tools (track execution time, API latency)
- [ ] T141 [P] Add cache metrics logging (hit rate, TTL remaining) to schema operations
- [ ] T142 [P] Review and enhance error messages across all tools for clarity
- [ ] T143 [P] Add examples to all tool docstrings for LLM context
- [ ] T144 Update README.md with quickstart guide content from quickstart.md
- [ ] T145 Create CLAUDE.md with updated project context (already done by script)
- [ ] T146 [P] Add .env.example validation in tests/unit/test_config.py
- [ ] T147 [P] Add integration test for complete user workflow (query + schema discovery)
- [ ] T148 Test MCP server with actual Claude Desktop configuration
- [ ] T149 Run invoke check final validation (100% coverage, all quality gates)
- [ ] T150 Run quickstart.md validation (follow guide step-by-step, verify all commands work)

**Checkpoint**: All polish tasks complete, project ready for release

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) OR sequentially in priority order
  - Each story is independently testable
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (but shares some models)
- **User Story 3 (P3)**: Can start after User Story 1 is complete - Enhances execute_custom_query from US1

### Within Each User Story

1. Tests MUST be written and FAIL before implementation (TDD red-green-refactor)
2. Data models before tools (pydantic models used for validation)
3. Tools before server integration
4. All tests passing before moving to next story

### Parallel Opportunities

- **Setup tasks (T005-T011)**: All [P] tasks can run in parallel
- **Foundational tasks**: Config (T016-T017), Errors (T022-T023), Logging (T029-T030), Retry (T035-T037), GraphQL (T044-T045) can all start in parallel
- **User Story tests**: Tests within a story marked [P] (T051-T053, T078-T079) can run in parallel
- **User Story models**: Models within a story marked [P] can run in parallel
- **Different user stories**: If team has capacity, US1 and US2 can be worked on in parallel after Foundational phase

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD red phase):
Task T051: Create tests/unit/test_tools_query.py
Task T052: Create tests/integration/test_rize_api.py
Task T053: Create tests/contract/test_mcp_protocol.py

# Then write failing tests:
Task T054-T059: Write all failing tests in parallel

# Launch all models for User Story 1 together:
Task T061: Create QueryRequest model
Task T062: Create QueryResponse model
Task T063: Create QueryMetadata model

# Implement tool:
Task T067-T072: Implement execute_custom_query (sequential, depends on models)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T015)
2. Complete Phase 2: Foundational (T016-T050) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T051-T077)
4. **STOP and VALIDATE**: Test User Story 1 independently with Claude Desktop
5. Deploy MVP / Demo capability

**MVP Deliverable**: Execute custom GraphQL queries against Rize API through Claude Desktop

### Incremental Delivery

1. Setup + Foundational (T001-T050) → Foundation ready
2. Add User Story 1 (T051-T077) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (T078-T117) → Test independently → Deploy/Demo (Schema discovery)
4. Add User Story 3 (T118-T139) → Test independently → Deploy/Demo (Advanced queries)
5. Polish (T140-T150) → Final release quality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T050)
2. Once Foundational is done:
   - Developer A: User Story 1 (T051-T077)
   - Developer B: User Story 2 (T078-T117) in parallel
   - Developer C: Can help with Foundational or start on models
3. User Story 3 starts after US1 complete (enhances same tool)
4. All developers collaborate on Polish phase

---

## TDD Workflow Reminder

**CRITICAL**: Constitution Principle III requires Test-First Development

For EVERY task marked as a test task:

1. **Write test FIRST** (before any implementation code exists)
2. **Verify test FAILS** (red phase) - run `invoke test` and confirm failure
3. **Get user approval** of test coverage (review test scenarios)
4. **Implement minimum code** to make test pass (green phase)
5. **Verify test PASSES** - run `invoke test` and confirm success
6. **Refactor** while keeping tests green
7. **Verify 100% coverage** - run `invoke test` and check coverage report

**Never skip the red phase** - if a test passes immediately, it's not testing the right thing.

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label (US1, US2, US3) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests MUST fail before implementing (red-green-refactor cycle)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Run `invoke check` before every commit (format, lint, typecheck, test with 100% coverage)
- Run `invoke pre-commit` for full validation workflow (auto-format + all checks)

---

## Total Task Count: 150 tasks

- **Setup**: 15 tasks (T001-T015)
- **Foundational**: 35 tasks (T016-T050)
- **User Story 1 (P1)**: 27 tasks (T051-T077) - MVP
- **User Story 2 (P2)**: 40 tasks (T078-T117)
- **User Story 3 (P3)**: 22 tasks (T118-T139)
- **Polish**: 11 tasks (T140-T150)

**Parallel Opportunities**: 47 tasks marked with [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Query Rize data through Claude Desktop and get results
- US2: Discover schema and introspect types
- US3: Execute complex queries with variables and pagination

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 77 tasks
