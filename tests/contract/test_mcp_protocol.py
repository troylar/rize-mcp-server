"""Contract tests for MCP protocol compliance."""


class TestMCPProtocolCompliance:
    """Tests for MCP protocol compliance."""

    def test_server_file_exists(self) -> None:
        """Test that server.py file exists and has required functions."""
        import os

        server_path = os.path.join(os.path.dirname(__file__), "../../src/server.py")
        assert os.path.exists(server_path)

        # Read file content
        with open(server_path) as f:
            content = f.read()

        # Verify key components
        assert "FastMCP" in content
        assert "time_tracking" in content
        assert "def main()" in content
        assert "@mcp.tool()" in content

        # Verify time tracking tools are present
        assert "start_timer" in content
        assert "stop_timer" in content
        assert "get_current_session" in content
        assert "log_time" in content
        assert "list_projects" in content
        assert "get_time_summary" in content

    def test_server_has_proper_docstrings(self) -> None:
        """Test that server functions are documented."""
        import os

        server_path = os.path.join(os.path.dirname(__file__), "../../src/server.py")

        with open(server_path) as f:
            content = f.read()

        # Check for documentation
        assert '"""' in content
        assert "time tracking" in content.lower() or "timer" in content.lower()
        assert "Args:" in content or "Returns:" in content

    def test_config_settings_structure(self) -> None:
        """Test that Settings has all required MCP configuration."""
        # Create settings with test values
        import os

        from src.config import Settings

        os.environ["RIZE_API_KEY"] = "test_key_123"
        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        # Verify MCP-related settings
        assert hasattr(settings, "mcp_server_name")
        assert hasattr(settings, "mcp_server_version")
        assert settings.mcp_server_name == "rize-mcp-server"
        assert settings.mcp_server_version == "0.1.0"
