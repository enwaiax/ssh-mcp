# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "7037bed8-d479-44e6-9198-c81f69b9d05d"
#   Timestamp: "2025-08-05T20:50:09+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + 集成测试原则"
#   Quality_Check: "全面的集成测试，验证端到端功能和组件协作"
# }}
# {{START_MODIFICATIONS}}
"""
Integration Tests

End-to-end integration tests for the FastMCP SSH server including:
- Full server startup and initialization
- CLI to MCP tool pipeline
- SSH connection management integration
- Error handling across components
- Performance and reliability testing
"""

import asyncio
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Add the python_src directory to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "python_src"))

from python_ssh_mcp.cli import parse_cli_args
from python_ssh_mcp.models import SSHConfig
from python_ssh_mcp.server import SSHMCPServer
from python_ssh_mcp.utils import Logger, setup_logger


class TestFullServerIntegration:
    """Test suite for full server integration."""

    @pytest.fixture
    def ssh_configs(self):
        """Provide test SSH configurations for integration testing."""
        return [
            SSHConfig(
                name="test_server_1",
                host="localhost",
                port=22,
                username="testuser1",
                password="testpass1",
                command_whitelist=["ls", "echo", "pwd"],
                command_blacklist=["rm", "sudo"],
            ),
            SSHConfig(
                name="test_server_2",
                host="192.168.1.100",
                port=2222,
                username="testuser2",
                password="testpass2",  # Use password instead of non-existent key file
                command_whitelist=["*"],
                command_blacklist=["rm -rf"],
            ),
        ]

    @pytest.fixture
    async def ssh_server(self, ssh_configs):
        """Create and initialize SSH MCP server for integration testing."""
        server = SSHMCPServer("test-integration-server")

        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            mock_connection = AsyncMock()
            mock_connect.return_value = mock_connection

            await server.initialize(ssh_configs)
            yield server

            await server.cleanup()

    async def test_server_initialization_flow(self, ssh_configs):
        """Test complete server initialization flow."""
        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            mock_connection = AsyncMock()
            mock_connect.return_value = mock_connection

            # Create server
            server = SSHMCPServer("integration-test")
            assert server.mcp is not None
            assert server.ssh_manager is not None

            # Initialize with configs
            await server.initialize(ssh_configs)

            # Verify SSH manager is initialized
            assert server.ssh_manager._initialized is True
            assert len(server.ssh_manager._configs) == 2

            # Cleanup
            await server.cleanup()

    async def test_cli_to_mcp_pipeline(self):
        """Test CLI argument parsing to MCP server initialization."""
        test_args = [
            "--host",
            "integration.example.com",
            "--username",
            "integrationuser",
            "--password",
            "integrationpass",
            "--allow-commands",
            "ls,pwd,echo",
            "--deny-commands",
            "rm,sudo",
        ]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            mock_connection = AsyncMock()
            mock_connect.return_value = mock_connection

            server = SSHMCPServer("cli-integration-test")
            await server.initialize(configs)

            # Verify configuration was correctly processed
            assert len(server.ssh_manager._configs) == 1
            config = list(server.ssh_manager._configs.values())[0]
            assert config.host == "integration.example.com"
            assert config.username == "integrationuser"
            assert "ls" in config.command_whitelist

            await server.cleanup()

    async def test_multiple_ssh_connections_integration(self, ssh_configs):
        """Test integration with multiple SSH connections."""
        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            # Mock different connections for different servers
            mock_connection_1 = AsyncMock()
            mock_connection_2 = AsyncMock()
            mock_connect.side_effect = [mock_connection_1, mock_connection_2]

            server = SSHMCPServer("multi-connection-test")
            await server.initialize(ssh_configs)

            # Test that different servers can be accessed
            conn_1 = await server.ssh_manager._get_connection("test_server_1")
            conn_2 = await server.ssh_manager._get_connection("test_server_2")

            assert conn_1 == mock_connection_1
            assert conn_2 == mock_connection_2
            assert mock_connect.call_count == 2

            await server.cleanup()

    async def test_error_propagation_integration(self, ssh_configs):
        """Test error propagation through the entire stack."""
        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            # Simulate connection failure
            mock_connect.side_effect = Exception("Connection refused")

            server = SSHMCPServer("error-integration-test")
            await server.initialize(ssh_configs)

            # Test that connection errors are properly handled
            with pytest.raises(
                (OSError, RuntimeError, ValueError)
            ):  # Should be wrapped in SSH-specific exception
                await server.ssh_manager._get_connection("test_server_1")

            await server.cleanup()


class TestMCPToolsIntegration:
    """Test suite for MCP tools integration."""

    @pytest.fixture
    def ssh_config(self):
        """Provide single SSH config for tool testing."""
        return SSHConfig(
            name="tool_test_server",
            host="localhost",
            port=22,
            username="tooluser",
            password="toolpass",
            command_whitelist=["ls", "echo", "cat"],
            command_blacklist=["rm"],
        )

    @pytest.fixture
    async def server_with_mocked_ssh(self, ssh_config):
        """Create server with mocked SSH connections for tool testing."""
        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            mock_connection = AsyncMock()
            mock_connect.return_value = mock_connection

            server = SSHMCPServer("tool-integration-test")
            await server.initialize([ssh_config])

            yield server, mock_connection

            await server.cleanup()

    async def test_execute_command_tool_integration(self, server_with_mocked_ssh):
        """Test execute-command tool integration."""
        server, mock_connection = server_with_mocked_ssh

        # Mock SSH command execution
        mock_result = AsyncMock()
        mock_result.stdout = "integration test output"
        mock_result.stderr = ""
        mock_result.exit_status = 0
        mock_connection.run.return_value = mock_result

        # Test command execution through the full stack
        from python_ssh_mcp.models import ExecuteCommandParams

        params = ExecuteCommandParams(
            cmdString="echo 'integration test'", serverName="tool_test_server"
        )

        result = await server.ssh_manager.execute_command(params)

        assert result["stdout"] == "integration test output"
        assert result["exitCode"] == 0
        assert result["serverName"] == "tool_test_server"

    async def test_file_operations_integration(self, server_with_mocked_ssh):
        """Test file upload/download integration."""
        server, mock_connection = server_with_mocked_ssh

        # Mock SFTP client
        mock_sftp = AsyncMock()
        mock_connection.start_sftp_client.return_value.__aenter__.return_value = (
            mock_sftp
        )

        # Test file upload
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
            tmp_file.write("integration test content")
            tmp_file.flush()

            from python_ssh_mcp.models import UploadParams

            upload_params = UploadParams(
                localPath=tmp_file.name,
                remotePath="/remote/test.txt",
                serverName="tool_test_server",
            )

            upload_result = await server.ssh_manager.upload(upload_params)

            assert upload_result["success"] is True
            mock_sftp.put.assert_called_once()

            # Cleanup
            Path(tmp_file.name).unlink()

    async def test_security_validation_integration(self, server_with_mocked_ssh):
        """Test security validation integration across the stack."""
        server, mock_connection = server_with_mocked_ssh

        # Test denied command
        from python_ssh_mcp.models import ExecuteCommandParams
        from python_ssh_mcp.utils import SSHCommandError

        params = ExecuteCommandParams(
            cmdString="rm -rf /important/data", serverName="tool_test_server"
        )

        with pytest.raises(SSHCommandError, match="Command denied by security policy"):
            await server.ssh_manager.execute_command(params)

    async def test_server_listing_integration(self, server_with_mocked_ssh):
        """Test server listing integration."""
        server, mock_connection = server_with_mocked_ssh

        server_infos = await server.ssh_manager.get_all_server_infos()

        assert len(server_infos) == 1
        server_info = server_infos[0]
        assert server_info["name"] == "tool_test_server"
        assert server_info["host"] == "localhost"
        assert server_info["port"] == 22
        assert server_info["username"] == "tooluser"


class TestLoggingIntegration:
    """Test suite for logging system integration."""

    def test_logging_setup_integration(self):
        """Test logging system setup and integration."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", delete=False
        ) as log_file:
            log_path = log_file.name

        try:
            # Setup logger
            setup_logger(level="debug", log_file=log_path, enable_console=False)

            # Test logging through the system
            Logger.info(
                "Integration test message", {"component": "test", "test_id": 123}
            )
            Logger.error("Integration test error", {"error_code": 500})

            # Verify log file content
            log_content = Path(log_path).read_text()
            assert "Integration test message" in log_content
            assert "Integration test error" in log_content

        finally:
            # Cleanup
            Path(log_path).unlink()

    async def test_error_handling_with_logging_integration(self):
        """Test error handling with logging integration."""
        from python_ssh_mcp.utils import ErrorHandler, SSHConnectionError

        # Create test error
        test_error = SSHConnectionError("Integration test connection error")

        # Test error handling with logging
        error_response = ErrorHandler.log_and_return_error(
            test_error, "Integration test failed"
        )

        assert error_response["isError"] is True
        assert "Integration test failed" in error_response["message"]


class TestPerformanceIntegration:
    """Test suite for performance and reliability integration."""

    async def test_multiple_concurrent_commands(self):
        """Test handling multiple concurrent commands."""
        ssh_config = SSHConfig(
            name="performance_test",
            host="localhost",
            port=22,
            username="perfuser",
            password="perfpass",
            command_whitelist=["*"],
            command_blacklist=[],
        )

        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            mock_connection = AsyncMock()
            mock_result = AsyncMock()
            mock_result.stdout = "concurrent command output"
            mock_result.stderr = ""
            mock_result.exit_status = 0
            mock_connection.run.return_value = mock_result
            mock_connect.return_value = mock_connection

            server = SSHMCPServer("performance-test")
            await server.initialize([ssh_config])

            # Execute multiple commands concurrently
            from python_ssh_mcp.models import ExecuteCommandParams

            async def execute_test_command(cmd_id: int):
                params = ExecuteCommandParams(
                    cmdString=f"echo 'command {cmd_id}'", serverName="performance_test"
                )
                return await server.ssh_manager.execute_command(params)

            # Run 10 concurrent commands
            tasks = [execute_test_command(i) for i in range(10)]
            results = await asyncio.gather(*tasks)

            # Verify all commands completed successfully
            assert len(results) == 10
            for result in results:
                assert result["exitCode"] == 0
                assert "concurrent command output" in result["stdout"]

            await server.cleanup()

    async def test_connection_reuse_performance(self):
        """Test that connections are properly reused for performance."""
        ssh_config = SSHConfig(
            name="reuse_test",
            host="localhost",
            port=22,
            username="reuseuser",
            password="reusepass",
            command_whitelist=["*"],
            command_blacklist=[],
        )

        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            mock_connection = AsyncMock()
            mock_result = AsyncMock()
            mock_result.stdout = "reuse test output"
            mock_result.stderr = ""
            mock_result.exit_status = 0
            mock_connection.run.return_value = mock_result
            mock_connect.return_value = mock_connection

            server = SSHMCPServer("reuse-test")
            await server.initialize([ssh_config])

            # Execute multiple commands on same server
            from python_ssh_mcp.models import ExecuteCommandParams

            for i in range(5):
                params = ExecuteCommandParams(
                    cmdString=f"echo 'reuse test {i}'", serverName="reuse_test"
                )
                await server.ssh_manager.execute_command(params)

            # Connection should only be established once
            assert mock_connect.call_count == 1
            # But run should be called multiple times
            assert mock_connection.run.call_count == 5

            await server.cleanup()

    async def test_memory_cleanup_integration(self):
        """Test that resources are properly cleaned up."""
        ssh_config = SSHConfig(
            name="cleanup_test",
            host="localhost",
            port=22,
            username="cleanupuser",
            password="cleanuppass",
        )

        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            mock_connection = AsyncMock()
            mock_connect.return_value = mock_connection

            server = SSHMCPServer("cleanup-test")
            await server.initialize([ssh_config])

            # Establish connection
            await server.ssh_manager._get_connection("cleanup_test")

            # Verify connection exists
            assert "cleanup_test" in server.ssh_manager._connections

            # Cleanup
            await server.cleanup()

            # Verify connection was closed
            mock_connection.close.assert_called_once()


class TestErrorRecoveryIntegration:
    """Test suite for error recovery and resilience."""

    async def test_connection_failure_recovery(self):
        """Test recovery from connection failures."""
        ssh_config = SSHConfig(
            name="recovery_test",
            host="localhost",
            port=22,
            username="recoveryuser",
            password="recoverypass",
            command_whitelist=["*"],
            command_blacklist=[],
        )

        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            # First call fails, second succeeds
            mock_connection = AsyncMock()
            mock_connect.side_effect = [Exception("Connection failed"), mock_connection]

            server = SSHMCPServer("recovery-test")
            await server.initialize([ssh_config])

            # First connection attempt should fail
            with pytest.raises((OSError, RuntimeError, ValueError)):
                await server.ssh_manager._get_connection("recovery_test")

            # Reset the side effect for second attempt
            mock_connect.side_effect = None
            mock_connect.return_value = mock_connection

            # Second attempt should succeed
            connection = await server.ssh_manager._get_connection("recovery_test")
            assert connection == mock_connection

            await server.cleanup()

    async def test_partial_initialization_handling(self):
        """Test handling of partial initialization failures."""
        configs = [
            SSHConfig(
                name="good_server",
                host="good.example.com",
                port=22,
                username="gooduser",
                password="goodpass",
            ),
            SSHConfig(
                name="bad_server",
                host="bad.example.com",
                port=22,
                username="baduser",
                password="badpass",
            ),
        ]

        server = SSHMCPServer("partial-init-test")

        # Initialize should succeed even if some connections might fail later
        await server.initialize(configs)

        # Verify both configs are stored
        assert len(server.ssh_manager._configs) == 2
        assert "good_server" in server.ssh_manager._configs
        assert "bad_server" in server.ssh_manager._configs

        await server.cleanup()

    async def test_graceful_degradation(self):
        """Test graceful degradation when some services fail."""
        ssh_config = SSHConfig(
            name="degradation_test",
            host="localhost",
            port=22,
            username="degradeuser",
            password="degradepass",
            command_whitelist=["ls", "echo"],
            command_blacklist=[],
        )

        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            mock_connection = AsyncMock()
            mock_connect.return_value = mock_connection

            server = SSHMCPServer("degradation-test")
            await server.initialize([ssh_config])

            # Simulate SFTP failure but SSH success
            mock_connection.start_sftp_client.side_effect = Exception(
                "SFTP not available"
            )
            mock_result = AsyncMock()
            mock_result.stdout = "echo works"
            mock_result.stderr = ""
            mock_result.exit_status = 0
            mock_connection.run.return_value = mock_result

            # Command execution should still work
            from python_ssh_mcp.models import ExecuteCommandParams

            params = ExecuteCommandParams(
                cmdString="echo 'test'", serverName="degradation_test"
            )

            result = await server.ssh_manager.execute_command(params)
            assert result["exitCode"] == 0

            # But file operations should fail gracefully
            from python_ssh_mcp.models import UploadParams

            upload_params = UploadParams(
                localPath="/local/file.txt",
                remotePath="/remote/file.txt",
                serverName="degradation_test",
            )

            with pytest.raises(
                (OSError, RuntimeError, ValueError)
            ):  # Should be wrapped in SFTP-specific exception
                await server.ssh_manager.upload(upload_params)

            await server.cleanup()


# {{END_MODIFICATIONS}}
