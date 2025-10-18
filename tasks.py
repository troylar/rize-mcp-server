"""
Invoke tasks for Rize MCP Server project.

Run `invoke --list` to see all available tasks.
Run `invoke <task> --help` for detailed help on a specific task.
"""

from pathlib import Path

from invoke import task


# Project paths
ROOT = Path(__file__).parent
SRC = ROOT / "src"
TESTS = ROOT / "tests"


@task
def install(ctx):
    """Install project dependencies using uv."""
    print("📦 Installing dependencies with uv...")
    ctx.run("uv pip install -e '.[dev]'", pty=True)
    print("✅ Dependencies installed successfully")


@task
def format(ctx, check=False):
    """
    Format code using ruff.

    Args:
        check: Only check formatting without making changes (default: False)
    """
    mode = "--check" if check else ""
    print(f"🎨 {'Checking' if check else 'Applying'} code formatting...")
    result = ctx.run(f"ruff format {mode} .", warn=True, pty=True)

    if result.ok:
        print(f"✅ Code formatting {'check passed' if check else 'applied'}")
    else:
        print(f"❌ Code formatting {'check failed' if check else 'failed'}")
        raise SystemExit(1)


@task
def lint(ctx, fix=False):
    """
    Run ruff linting.

    Args:
        fix: Automatically fix issues where possible (default: False)
    """
    mode = "--fix" if fix else ""
    print("🔍 Running ruff linter...")
    result = ctx.run(f"ruff check {mode} .", warn=True, pty=True)

    if result.ok:
        print("✅ Linting passed")
    else:
        print("❌ Linting failed")
        raise SystemExit(1)


@task
def typecheck(ctx):
    """Run mypy type checking in strict mode."""
    print("🔎 Running mypy type checker (strict mode)...")
    result = ctx.run("mypy --strict src/", warn=True, pty=True)

    if result.ok:
        print("✅ Type checking passed")
    else:
        print("❌ Type checking failed")
        raise SystemExit(1)


@task
def test(ctx, verbose=False, coverage=True, failfast=False):
    """
    Run pytest test suite.

    Args:
        verbose: Show verbose test output (default: False)
        coverage: Generate coverage report (default: True)
        failfast: Stop on first test failure (default: False)
    """
    print("🧪 Running test suite...")

    flags = []
    if verbose:
        flags.append("-vv")
    else:
        flags.append("-v")

    if coverage:
        flags.extend(
            ["--cov=src", "--cov-report=term-missing", "--cov-report=html", "--cov-fail-under=100"]
        )

    if failfast:
        flags.append("-x")

    flags_str = " ".join(flags)
    result = ctx.run(f"pytest {flags_str}", warn=True, pty=True)

    if result.ok:
        print("✅ All tests passed")
        if coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ Tests failed")
        raise SystemExit(1)


@task
def test_unit(ctx):
    """Run only unit tests."""
    print("🧪 Running unit tests...")
    result = ctx.run("pytest tests/unit/ -v", warn=True, pty=True)

    if result.ok:
        print("✅ Unit tests passed")
    else:
        print("❌ Unit tests failed")
        raise SystemExit(1)


@task
def test_integration(ctx):
    """Run only integration tests."""
    print("🧪 Running integration tests...")
    result = ctx.run("pytest tests/integration/ -v", warn=True, pty=True)

    if result.ok:
        print("✅ Integration tests passed")
    else:
        print("❌ Integration tests failed")
        raise SystemExit(1)


@task
def test_contract(ctx):
    """Run only contract tests (MCP protocol compliance)."""
    print("🧪 Running contract tests...")
    result = ctx.run("pytest tests/contract/ -v", warn=True, pty=True)

    if result.ok:
        print("✅ Contract tests passed")
    else:
        print("❌ Contract tests failed")
        raise SystemExit(1)


@task(pre=[format, lint, typecheck, test])
def check(ctx):
    """
    Run all quality checks (format, lint, typecheck, test).

    This is the main pre-commit validation task.
    Runs: format --check, lint, typecheck, test
    """
    print("\n" + "=" * 60)
    print("🎉 All quality checks passed!")
    print("=" * 60)
    print("✅ Code formatting")
    print("✅ Linting")
    print("✅ Type checking")
    print("✅ Tests (100% coverage)")
    print("=" * 60)


@task
def clean(ctx):
    """Clean build artifacts, cache files, and coverage reports."""
    print("🧹 Cleaning build artifacts...")

    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.egg-info",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "htmlcov",
        ".coverage",
        "dist",
        "build",
    ]

    for pattern in patterns:
        ctx.run(f"rm -rf {pattern}", warn=True)

    print("✅ Cleanup complete")


@task
def build(ctx):
    """Build the package distribution."""
    print("📦 Building package...")
    ctx.run("python -m build", pty=True)
    print("✅ Build complete - check dist/ directory")


@task
def dev(ctx):
    """Run the MCP server in development mode."""
    print("🚀 Starting Rize MCP Server in development mode...")
    print("Press Ctrl+C to stop")
    ctx.run("python -m src.server", pty=True)


@task
def schema(ctx):
    """Fetch and display the Rize GraphQL schema."""
    print("📋 Fetching Rize GraphQL schema...")
    ctx.run("python -m src.tools.schema_introspection", pty=True)


@task
def validate_mcp(ctx):
    """Validate MCP protocol compliance."""
    print("🔍 Validating MCP protocol compliance...")
    # This would run MCP-specific validation tools
    # For now, we'll rely on contract tests
    ctx.run("pytest tests/contract/ -v", pty=True)
    print("✅ MCP protocol compliance validated")


@task
def docs(ctx):
    """Generate project documentation."""
    print("📚 Generating documentation...")
    # Add documentation generation here (e.g., sphinx, mkdocs)
    print("⚠️  Documentation generation not yet implemented")


@task
def pre_commit(ctx):
    """
    Run pre-commit checks (auto-fix formatting, then validate).

    This is the recommended workflow before committing:
    1. Auto-fix formatting
    2. Run all quality checks
    """
    print("🔧 Running pre-commit workflow...\n")

    # Step 1: Auto-fix formatting
    print("Step 1: Auto-fixing code formatting...")
    format(ctx, check=False)

    # Step 2: Run all checks
    print("\nStep 2: Running all quality checks...")
    check(ctx)

    print("\n" + "=" * 60)
    print("✅ Pre-commit checks complete - ready to commit!")
    print("=" * 60)


@task
def init_project(ctx):
    """Initialize project structure (src/, tests/ directories)."""
    print("🏗️  Initializing project structure...")

    directories = [
        "src",
        "src/tools",
        "src/resources",
        "src/prompts",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/contract",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists():
            init_file.touch()

    print("✅ Project structure initialized")
    print("\nCreated directories:")
    for directory in directories:
        print(f"  - {directory}/")
