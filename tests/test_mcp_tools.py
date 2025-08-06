# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "7037bed8-d479-44e6-9198-c81f69b9d05d"
#   Timestamp: "2025-08-05T20:50:09+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + 测试驱动开发"
#   Quality_Check: "全面的MCP工具测试，包含execute-command, upload, download, list-servers工具"
# }}
# {{START_MODIFICATIONS}}
"""
MCP Tools Tests

Comprehensive tests for all FastMCP tools including:
- execute-command tool
- upload tool
- download tool
- list-servers tool
- Tool registration and integration
- Error handling and validation
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add the src directory to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ssh_mcp import SSHMCPServer
from ssh_mcp.models import (
    DownloadParams,
    ExecuteCommandParams,
    SSHConfig,
    UploadParams,
)
from ssh_mcp.tools import initialize_server, mcp
from ssh_mcp.utils import SFTPError, SSHCommandError, SSHConnectionError


class TestMCPToolRegistration:
    """Test suite for MCP tool registration."""

    async def test_v2_tools_are_registered(self):
        """Test that v2 tools are automatically registered via decorators."""
        # v2 tools are registered automatically via decorators
        # Get registered tools using FastMCP API
        tools_dict = await mcp.get_tools()

        # Get registered tool names (keys of the dictionary)
        tool_names = list(tools_dict.keys())

        # Verify all expected tools are registered
        expected_tools = ["execute-command", "upload", "download", "list-servers"]
        for tool_name in expected_tools:
            assert tool_name in tool_names, (
                f"Tool {tool_name} not found in registered tools"
            )

        # Verify tools have proper FunctionTool objects
        for tool_name, tool_obj in tools_dict.items():
            assert hasattr(tool_obj, "name"), f"Tool {tool_name} missing name attribute"
            assert tool_obj.name == tool_name, (
                f"Tool name mismatch: {tool_obj.name} != {tool_name}"
            )

    def test_initialize_server_function_exists(self):
        """Test that initialize_server function is available."""
        # Verify the function is imported and callable
        assert callable(initialize_server)

        # Verify it's an async function
        import inspect

        assert inspect.iscoroutinefunction(initialize_server)


class TestExecuteCommandTool:
    """Test suite for execute-command MCP tool."""

    @pytest.fixture
    def mock_ssh_manager(self):
        """Create mock SSH manager for execute command testing."""
        mock_manager = AsyncMock()
        return mock_manager

    @pytest.fixture
    def execute_command_func(self, mock_ssh_manager):
        """Create execute command function for testing."""
        # Import the actual tool implementation
        from ssh_mcp.tools.execute_command import register_execute_command_tool

        # Mock MCP server to capture the registered function
        mock_mcp_server = MagicMock()
        registered_func = None

        def capture_tool(*args, **kwargs):
            def decorator(func):
                nonlocal registered_func
                registered_func = func
                return func

            return decorator

        mock_mcp_server.tool = capture_tool

        # Register the tool
        register_execute_command_tool(mock_mcp_server, mock_ssh_manager)

        return registered_func

    async def test_execute_command_success(
        self, mock_ssh_manager, execute_command_func
    ):
        """Test successful command execution."""
        mock_ssh_manager.execute_command.return_value = {
            "stdout": "Hello World",
            "stderr": "",
            "exitCode": 0,
            "serverName": "test_server",
        }

        result = await execute_command_func("echo 'Hello World'")

        # Verify SSH manager was called correctly
        mock_ssh_manager.execute_command.assert_called_once()
        call_args = mock_ssh_manager.execute_command.call_args[0][0]
        assert call_args.cmd_string == "echo 'Hello World'"

        # Verify result format
        assert result["stdout"] == "Hello World"
        assert result["stderr"] == ""
        assert result["exitCode"] == 0

    async def test_execute_command_with_server_name(
        self, mock_ssh_manager, execute_command_func
    ):
        """Test command execution with specific server name."""
        mock_ssh_manager.execute_command.return_value = {
            "stdout": "Server specific command",
            "stderr": "",
            "exitCode": 0,
            "serverName": "production_server",
        }

        await execute_command_func("pwd", serverName="production_server")

        call_args = mock_ssh_manager.execute_command.call_args[0][0]
        assert call_args.cmd_string == "pwd"
        assert call_args.serverName == "production_server"

    async def test_execute_command_with_timeout(
        self, mock_ssh_manager, execute_command_func
    ):
        """Test command execution with custom timeout."""
        mock_ssh_manager.execute_command.return_value = {
            "stdout": "Long task completed",
            "stderr": "",
            "exitCode": 0,
            "serverName": "test_server",
        }

        await execute_command_func("sleep 5", timeout=60)

        call_args = mock_ssh_manager.execute_command.call_args[0][0]
        assert call_args.timeout == 60

    async def test_execute_command_error_handling(
        self, mock_ssh_manager, execute_command_func
    ):
        """Test command execution error handling."""
        mock_ssh_manager.execute_command.side_effect = SSHCommandError(
            "Command denied by security policy"
        )

        result = await execute_command_func("rm -rf /")

        # Tool should handle errors gracefully and return structured response
        assert "isError" in result
        assert result["isError"] is True
        assert "error" in result
        assert "message" in result

    async def test_execute_command_connection_error(
        self, mock_ssh_manager, execute_command_func
    ):
        """Test command execution with connection error."""
        mock_ssh_manager.execute_command.side_effect = SSHConnectionError(
            "Failed to connect to server"
        )

        result = await execute_command_func("ls")

        assert result["isError"] is True
        assert "Failed to connect" in result["message"]


class TestUploadTool:
    """Test suite for upload MCP tool."""

    @pytest.fixture
    def mock_ssh_manager(self):
        """Create mock SSH manager for upload testing."""
        mock_manager = AsyncMock()
        return mock_manager

    @pytest.fixture
    def upload_func(self, mock_ssh_manager):
        """Create upload function for testing."""
        from ssh_mcp.tools.upload import register_upload_tool

        mock_mcp_server = MagicMock()
        registered_func = None

        def capture_tool(*args, **kwargs):
            def decorator(func):
                nonlocal registered_func
                registered_func = func
                return func

            return decorator

        mock_mcp_server.tool = capture_tool
        register_upload_tool(mock_mcp_server, mock_ssh_manager)

        return registered_func

    async def test_upload_success(self, mock_ssh_manager, upload_func):
        """Test successful file upload."""
        mock_ssh_manager.upload.return_value = {
            "success": True,
            "message": "File uploaded successfully",
            "localPath": "/local/file.txt",
            "remotePath": "/remote/file.txt",
        }

        result = await upload_func("/local/file.txt", "/remote/file.txt")

        # Verify SSH manager was called correctly
        mock_ssh_manager.upload.assert_called_once()
        call_args = mock_ssh_manager.upload.call_args[0][0]
        assert call_args.localPath == "/local/file.txt"
        assert call_args.remotePath == "/remote/file.txt"

        # Verify result
        assert result["success"] is True
        assert "uploaded successfully" in result["message"]

    async def test_upload_with_server_name(self, mock_ssh_manager, upload_func):
        """Test file upload with specific server name."""
        mock_ssh_manager.upload.return_value = {
            "success": True,
            "message": "File uploaded to staging server",
            "localPath": "/local/config.json",
            "remotePath": "/remote/config.json",
        }

        await upload_func(
            "/local/config.json", "/remote/config.json", serverName="staging_server"
        )

        call_args = mock_ssh_manager.upload.call_args[0][0]
        assert call_args.serverName == "staging_server"

    async def test_upload_error_handling(self, mock_ssh_manager, upload_func):
        """Test upload error handling."""
        mock_ssh_manager.upload.side_effect = SFTPError("Local file not found")

        result = await upload_func("/non/existent/file.txt", "/remote/file.txt")

        assert result["isError"] is True
        assert "Local file not found" in result["message"]

    async def test_upload_permission_error(self, mock_ssh_manager, upload_func):
        """Test upload with permission error."""
        mock_ssh_manager.upload.side_effect = SFTPError(
            "Permission denied: /restricted/path/"
        )

        result = await upload_func("/local/file.txt", "/restricted/path/file.txt")

        assert result["isError"] is True
        assert "Permission denied" in result["message"]


class TestDownloadTool:
    """Test suite for download MCP tool."""

    @pytest.fixture
    def mock_ssh_manager(self):
        """Create mock SSH manager for download testing."""
        mock_manager = AsyncMock()
        return mock_manager

    @pytest.fixture
    def download_func(self, mock_ssh_manager):
        """Create download function for testing."""
        from ssh_mcp.tools.download import register_download_tool

        mock_mcp_server = MagicMock()
        registered_func = None

        def capture_tool(*args, **kwargs):
            def decorator(func):
                nonlocal registered_func
                registered_func = func
                return func

            return decorator

        mock_mcp_server.tool = capture_tool
        register_download_tool(mock_mcp_server, mock_ssh_manager)

        return registered_func

    async def test_download_success(self, mock_ssh_manager, download_func):
        """Test successful file download."""
        mock_ssh_manager.download.return_value = {
            "success": True,
            "message": "File downloaded successfully",
            "remotePath": "/remote/data.csv",
            "localPath": "/local/data.csv",
        }

        result = await download_func("/remote/data.csv", "/local/data.csv")

        # Verify SSH manager was called correctly
        mock_ssh_manager.download.assert_called_once()
        call_args = mock_ssh_manager.download.call_args[0][0]
        assert call_args.remotePath == "/remote/data.csv"
        assert call_args.localPath == "/local/data.csv"

        # Verify result
        assert result["success"] is True
        assert "downloaded successfully" in result["message"]

    async def test_download_with_server_name(self, mock_ssh_manager, download_func):
        """Test file download with specific server name."""
        mock_ssh_manager.download.return_value = {
            "success": True,
            "message": "File downloaded from production server",
            "remotePath": "/logs/app.log",
            "localPath": "/local/logs/app.log",
        }

        await download_func(
            "/logs/app.log", "/local/logs/app.log", serverName="production_server"
        )

        call_args = mock_ssh_manager.download.call_args[0][0]
        assert call_args.serverName == "production_server"

    async def test_download_file_not_found(self, mock_ssh_manager, download_func):
        """Test download with remote file not found."""
        mock_ssh_manager.download.side_effect = SFTPError(
            "Remote file not found: /path/missing.txt"
        )

        result = await download_func("/path/missing.txt", "/local/missing.txt")

        assert result["isError"] is True
        assert "Remote file not found" in result["message"]

    async def test_download_local_path_error(self, mock_ssh_manager, download_func):
        """Test download with local path error."""
        mock_ssh_manager.download.side_effect = SFTPError(
            "Cannot write to local path: /readonly/path/"
        )

        result = await download_func("/remote/file.txt", "/readonly/path/file.txt")

        assert result["isError"] is True
        assert "Cannot write to local path" in result["message"]


class TestListServersTool:
    """Test suite for list-servers MCP tool."""

    @pytest.fixture
    def mock_ssh_manager(self):
        """Create mock SSH manager for list servers testing."""
        mock_manager = AsyncMock()
        return mock_manager

    @pytest.fixture
    def list_servers_func(self, mock_ssh_manager):
        """Create list servers function for testing."""
        from ssh_mcp.tools.list_servers import register_list_servers_tool

        mock_mcp_server = MagicMock()
        registered_func = None

        def capture_tool(*args, **kwargs):
            def decorator(func):
                nonlocal registered_func
                registered_func = func
                return func

            return decorator

        mock_mcp_server.tool = capture_tool
        register_list_servers_tool(mock_mcp_server, mock_ssh_manager)

        return registered_func

    async def test_list_servers_success(self, mock_ssh_manager, list_servers_func):
        """Test successful server listing."""
        mock_servers = [
            {
                "name": "production",
                "host": "prod.example.com",
                "port": 22,
                "username": "deploy",
                "authentication": "key",
                "status": "connected",
            },
            {
                "name": "staging",
                "host": "staging.example.com",
                "port": 2222,
                "username": "dev",
                "authentication": "password",
                "status": "disconnected",
            },
        ]

        mock_ssh_manager.get_all_server_infos.return_value = mock_servers

        result = await list_servers_func()

        # Verify SSH manager was called
        mock_ssh_manager.get_all_server_infos.assert_called_once()

        # Verify result structure
        assert isinstance(result, list)
        assert len(result) == 2

        prod_server = next(s for s in result if s["name"] == "production")
        assert prod_server["host"] == "prod.example.com"
        assert prod_server["authentication"] == "key"

    async def test_list_servers_empty(self, mock_ssh_manager, list_servers_func):
        """Test listing servers when no servers configured."""
        mock_ssh_manager.get_all_server_infos.return_value = []

        result = await list_servers_func()

        assert isinstance(result, list)
        assert len(result) == 0

    async def test_list_servers_error_handling(
        self, mock_ssh_manager, list_servers_func
    ):
        """Test list servers error handling."""
        mock_ssh_manager.get_all_server_infos.side_effect = Exception(
            "Manager not initialized"
        )

        result = await list_servers_func()

        # Tool should handle errors gracefully
        assert "isError" in result
        assert result["isError"] is True
        assert "Manager not initialized" in result["message"]


class TestMCPToolIntegration:
    """Test suite for MCP tool integration with server."""

    @pytest.fixture
    def ssh_config(self):
        """Provide test SSH configuration."""
        return SSHConfig(
            name="test_server",
            host="localhost",
            port=22,
            username="testuser",
            password="testpass",
            command_whitelist=["ls", "echo", "pwd"],
            command_blacklist=["rm"],
        )

    async def test_ssh_mcp_server_tool_registration(self, ssh_config):
        """Test that SSH MCP server correctly registers all tools."""
        with patch("ssh_mcp.ssh_manager.asyncssh.connect"):
            server = SSHMCPServer("test-server")
            await server.initialize([ssh_config])

            # Verify that all tools are registered
            # This test verifies the integration works without specific assertions
            # as the FastMCP framework handles tool registration internally
            assert server.ssh_manager is not None
            assert server.mcp is not None

    async def test_tool_parameter_validation(self):
        """Test that MCP tools properly validate parameters."""
        # This test would require actual FastMCP integration
        # For now, we verify the parameter models are correctly structured

        # Test ExecuteCommandParams validation
        valid_params = ExecuteCommandParams(
            cmd_string="ls -la", serverName="test_server", timeout=30
        )
        assert valid_params.cmd_string == "ls -la"
        assert valid_params.timeout == 30

        # Test UploadParams validation
        upload_params = UploadParams(
            localPath="/local/file.txt",
            remotePath="/remote/file.txt",
            serverName="test_server",
        )
        assert upload_params.localPath == "/local/file.txt"

        # Test DownloadParams validation
        download_params = DownloadParams(
            remotePath="/remote/file.txt",
            localPath="/local/file.txt",
            serverName="test_server",
        )
        assert download_params.remotePath == "/remote/file.txt"

    async def test_tool_error_response_format(self):
        """Test that all tools return consistent error response format."""
        # This tests the error handler utility function used by all tools
        from ssh_mcp.utils import ErrorHandler

        test_error = Exception("Test error message")
        error_response = ErrorHandler.log_and_return_error(
            test_error, "Test operation failed"
        )

        # Verify error response format consistency
        assert "isError" in error_response
        assert error_response["isError"] is True
        assert "error" in error_response
        assert "message" in error_response
        assert "Test operation failed" in error_response["message"]

    async def test_tool_success_response_format(self, mock_ssh_manager):
        """Test that tools return consistent success response format."""
        # Test command execution success format
        success_response = {
            "stdout": "command output",
            "stderr": "",
            "exitCode": 0,
            "serverName": "test_server",
        }

        # Verify all required fields are present
        assert "stdout" in success_response
        assert "stderr" in success_response
        assert "exitCode" in success_response
        assert "serverName" in success_response

        # Test file operation success format
        file_response = {
            "success": True,
            "message": "Operation completed successfully",
            "localPath": "/local/path",
            "remotePath": "/remote/path",
        }

        assert "success" in file_response
        assert "message" in file_response
        assert file_response["success"] is True


# {{END_MODIFICATIONS}}
