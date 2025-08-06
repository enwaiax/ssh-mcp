# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "7037bed8-d479-44e6-9198-c81f69b9d05d"
#   Timestamp: "2025-08-05T20:50:09+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + 测试驱动开发"
#   Quality_Check: "全面的SSH连接管理器测试，包含连接、错误处理、安全验证等"
# }}
# {{START_MODIFICATIONS}}
"""
SSH Connection Manager Tests

Comprehensive tests for the SSH connection manager functionality including:
- Connection establishment and management
- Security validation
- Error handling
- Connection pooling
- Authentication methods
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Add the python_src directory to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "python_src"))

from ssh_mcp.models import (
    DownloadParams,
    ExecuteCommandParams,
    SSHConfig,
    UploadParams,
)
from ssh_mcp.ssh_manager import SSHConnectionManager
from ssh_mcp.utils import (
    SFTPError,
    SSHCommandError,
    SSHConnectionError,
)


class TestSSHConnectionManager:
    """Test suite for SSH Connection Manager."""

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
            command_blacklist=["rm", "sudo"],
        )

    @pytest.fixture
    def ssh_config_with_key(self):
        """Provide test SSH configuration with private key."""
        # Create a temporary private key file for testing
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as f:
            f.write("-----BEGIN PRIVATE KEY-----\n")
            f.write("test_key_content_for_testing\n")
            f.write("-----END PRIVATE KEY-----\n")
            temp_key_path = f.name

        return SSHConfig(
            name="test_key_server",
            host="192.168.1.100",
            port=2222,
            username="keyuser",
            private_key=temp_key_path,
            command_whitelist=["*"],
            command_blacklist=[],
        )

    @pytest.fixture
    async def manager(self):
        """Create SSH manager instance for testing."""
        # Reset singleton state before getting instance
        SSHConnectionManager._instance = None
        manager = await SSHConnectionManager.get_instance()
        # Reset state for clean tests
        manager._connections = {}
        manager._configs = {}
        manager._connected = {}
        manager._default_name = "default"
        return manager

    async def test_singleton_pattern(self):
        """Test that SSHConnectionManager follows singleton pattern."""
        manager1 = await SSHConnectionManager.get_instance()
        manager2 = await SSHConnectionManager.get_instance()

        assert manager1 is manager2
        assert id(manager1) == id(manager2)

    async def test_initialize_with_single_config(self, manager, ssh_config):
        """Test initialization with single SSH configuration."""
        configs = {"test_server": ssh_config}

        manager.set_config(configs)

        assert "test_server" in manager._configs
        assert manager._configs["test_server"] == ssh_config
        assert manager._default_name == "test_server"

    async def test_initialize_with_multiple_configs(
        self, manager, ssh_config, ssh_config_with_key
    ):
        """Test initialization with multiple SSH configurations."""
        configs = {"test_server": ssh_config, "test_key_server": ssh_config_with_key}

        manager.set_config(configs)

        assert len(manager._configs) == 2
        assert "test_server" in manager._configs
        assert "test_key_server" in manager._configs

    async def test_initialize_empty_configs(self, manager):
        """Test initialization with empty configurations."""
        with pytest.raises(
            ValueError, match="At least one SSH configuration is required"
        ):
            manager.set_config([])

    async def test_double_initialization_error(self, manager, ssh_config):
        """Test that double initialization raises error."""
        manager.set_config([ssh_config])

        with pytest.raises(RuntimeError, match="SSH manager is already initialized"):
            manager.set_config([ssh_config])

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_get_connection_success(self, mock_connect, manager, ssh_config):
        """Test successful SSH connection establishment."""
        mock_connection = AsyncMock()
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config])
        connection = await manager._get_connection("test_server")

        assert connection == mock_connection
        assert "test_server" in manager._connections
        mock_connect.assert_called_once_with(
            host="localhost", port=22, username="testuser", password="testpass"
        )

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_get_connection_with_private_key(
        self, mock_connect, manager, ssh_config_with_key
    ):
        """Test SSH connection with private key authentication."""
        mock_connection = AsyncMock()
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config_with_key])
        connection = await manager._get_connection("test_key_server")

        assert connection == mock_connection
        mock_connect.assert_called_once_with(
            host="192.168.1.100",
            port=2222,
            username="keyuser",
            client_keys=["test_key_content"],
        )

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_get_connection_failure(self, mock_connect, manager, ssh_config):
        """Test SSH connection failure handling."""
        mock_connect.side_effect = Exception("Connection refused")

        manager.set_config([ssh_config])

        with pytest.raises(
            SSHConnectionError, match="Failed to connect to test_server"
        ):
            await manager._get_connection("test_server")

    async def test_get_connection_invalid_server(self, manager, ssh_config):
        """Test getting connection for invalid server name."""
        manager.set_config([ssh_config])

        with pytest.raises(SSHConnectionError, match="Unknown server: invalid_server"):
            await manager._get_connection("invalid_server")

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_connection_reuse(self, mock_connect, manager, ssh_config):
        """Test that existing connections are reused."""
        mock_connection = AsyncMock()
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config])

        # First call should create connection
        connection1 = await manager._get_connection("test_server")

        # Second call should reuse existing connection
        connection2 = await manager._get_connection("test_server")

        assert connection1 == connection2
        assert mock_connect.call_count == 1

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_execute_command_success(self, mock_connect, manager, ssh_config):
        """Test successful command execution."""
        mock_connection = AsyncMock()
        mock_result = AsyncMock()
        mock_result.stdout = "Hello World"
        mock_result.stderr = ""
        mock_result.exit_status = 0

        mock_connection.run.return_value = mock_result
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config])

        params = ExecuteCommandParams(
            cmd_string="echo 'Hello World'", serverName="test_server"
        )

        result = await manager.execute_command(params)

        assert result["stdout"] == "Hello World"
        assert result["stderr"] == ""
        assert result["exitCode"] == 0
        assert result["serverName"] == "test_server"

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_execute_command_with_timeout(
        self, mock_connect, manager, ssh_config
    ):
        """Test command execution with custom timeout."""
        mock_connection = AsyncMock()
        mock_result = AsyncMock()
        mock_result.stdout = "Long running task completed"
        mock_result.stderr = ""
        mock_result.exit_status = 0

        mock_connection.run.return_value = mock_result
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config])

        params = ExecuteCommandParams(
            cmd_string="sleep 5 && echo 'Long running task completed'",
            serverName="test_server",
            timeout=60,
        )

        result = await manager.execute_command(params)

        assert result["stdout"] == "Long running task completed"
        mock_connection.run.assert_called_once_with(
            "sleep 5 && echo 'Long running task completed'", timeout=60, check=False
        )

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_execute_command_denied(self, mock_connect, manager, ssh_config):
        """Test command execution with denied command."""
        mock_connection = AsyncMock()
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config])

        params = ExecuteCommandParams(
            cmd_string="rm -rf /important/data", serverName="test_server"
        )

        with pytest.raises(SSHCommandError, match="Command denied by security policy"):
            await manager.execute_command(params)

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_execute_command_not_allowed(self, mock_connect, manager, ssh_config):
        """Test command execution with command not in allow list."""
        mock_connection = AsyncMock()
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config])

        params = ExecuteCommandParams(
            cmd_string="cat /etc/passwd", serverName="test_server"
        )

        with pytest.raises(SSHCommandError, match="Command not in allowed list"):
            await manager.execute_command(params)

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_upload_file_success(self, mock_connect, manager, ssh_config):
        """Test successful file upload."""
        mock_connection = AsyncMock()
        mock_sftp = AsyncMock()
        mock_connection.start_sftp_client.return_value.__aenter__.return_value = (
            mock_sftp
        )
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config])

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
            tmp_file.write("Test content")
            tmp_file.flush()

            params = UploadParams(
                localPath=tmp_file.name,
                remotePath="/remote/path/test.txt",
                serverName="test_server",
            )

            result = await manager.upload(params)

            assert result["success"] is True
            assert "uploaded successfully" in result["message"]
            mock_sftp.put.assert_called_once_with(
                tmp_file.name, "/remote/path/test.txt"
            )

            # Cleanup
            Path(tmp_file.name).unlink()

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_upload_file_not_found(self, mock_connect, manager, ssh_config):
        """Test file upload with non-existent local file."""
        mock_connection = AsyncMock()
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config])

        params = UploadParams(
            localPath="/non/existent/file.txt",
            remotePath="/remote/path/test.txt",
            serverName="test_server",
        )

        with pytest.raises(SFTPError, match="Local file not found"):
            await manager.upload(params)

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_download_file_success(self, mock_connect, manager, ssh_config):
        """Test successful file download."""
        mock_connection = AsyncMock()
        mock_sftp = AsyncMock()
        mock_connection.start_sftp_client.return_value.__aenter__.return_value = (
            mock_sftp
        )
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config])

        with tempfile.TemporaryDirectory() as tmp_dir:
            local_path = Path(tmp_dir) / "downloaded_file.txt"

            params = DownloadParams(
                remotePath="/remote/path/file.txt",
                localPath=str(local_path),
                serverName="test_server",
            )

            result = await manager.download(params)

            assert result["success"] is True
            assert "downloaded successfully" in result["message"]
            mock_sftp.get.assert_called_once_with(
                "/remote/path/file.txt", str(local_path)
            )

    @patch("python_ssh_mcp.ssh_manager.asyncssh.connect")
    async def test_sftp_operation_failure(self, mock_connect, manager, ssh_config):
        """Test SFTP operation failure handling."""
        mock_connection = AsyncMock()
        mock_sftp = AsyncMock()
        mock_sftp.get.side_effect = Exception("SFTP error")
        mock_connection.start_sftp_client.return_value.__aenter__.return_value = (
            mock_sftp
        )
        mock_connect.return_value = mock_connection

        manager.set_config([ssh_config])

        params = DownloadParams(
            remotePath="/remote/path/file.txt",
            localPath="/local/path/file.txt",
            serverName="test_server",
        )

        with pytest.raises(SFTPError, match="SFTP operation failed"):
            await manager.download(params)

    async def test_get_all_server_infos(self, manager, ssh_config, ssh_config_with_key):
        """Test getting all server information."""
        configs = [ssh_config, ssh_config_with_key]
        manager.set_config(configs)

        server_infos = await manager.get_all_server_infos()

        assert len(server_infos) == 2
        assert any(info["name"] == "test_server" for info in server_infos)
        assert any(info["name"] == "test_key_server" for info in server_infos)

        # Check structure of server info
        test_server_info = next(
            info for info in server_infos if info["name"] == "test_server"
        )
        assert "host" in test_server_info
        assert "port" in test_server_info
        assert "username" in test_server_info
        assert "authentication" in test_server_info

    async def test_cleanup(self, manager, ssh_config):
        """Test cleanup functionality."""
        with patch("python_ssh_mcp.ssh_manager.asyncssh.connect") as mock_connect:
            mock_connection = AsyncMock()
            mock_connect.return_value = mock_connection

            manager.set_config([ssh_config])
            await manager._get_connection("test_server")

            # Ensure connection exists
            assert "test_server" in manager._connections

            # Cleanup
            await manager.cleanup()

            # Verify connection was closed
            mock_connection.close.assert_called_once()

    async def test_not_initialized_error(self, manager):
        """Test operations on non-initialized manager."""
        params = ExecuteCommandParams(cmd_string="echo test", serverName="test_server")

        with pytest.raises(RuntimeError, match="SSH manager not initialized"):
            await manager.execute_command(params)


class TestSecurityValidation:
    """Test suite for SSH Manager security validation."""

    @pytest.fixture
    async def manager_with_whitelist(self):
        """Create SSH manager with whitelist configuration."""
        config = SSHConfig(
            name="whitelist_server",
            host="localhost",
            port=22,
            username="testuser",
            password="testpass",
            command_whitelist=["ls", "echo", "pwd"],
        )
        manager = await SSHConnectionManager.get_instance()
        manager._configs = {"whitelist_server": config}
        manager._default_name = "whitelist_server"
        return manager

    @pytest.fixture
    async def manager_with_blacklist(self):
        """Create SSH manager with blacklist configuration."""
        config = SSHConfig(
            name="blacklist_server",
            host="localhost",
            port=22,
            username="testuser",
            password="testpass",
            command_whitelist=["*"],
            command_blacklist=["rm", "sudo"],
        )
        manager = await SSHConnectionManager.get_instance()
        manager._configs = {"blacklist_server": config}
        manager._default_name = "blacklist_server"
        return manager

    async def test_validate_allowed_command(self, manager_with_whitelist):
        """Test validation of allowed command."""
        manager = await manager_with_whitelist
        # Should pass validation
        is_allowed, reason = manager.validate_command("ls -la")
        assert is_allowed is True
        assert reason is None

        is_allowed, reason = manager.validate_command("echo 'hello'")
        assert is_allowed is True
        assert reason is None

        is_allowed, reason = manager.validate_command("pwd")
        assert is_allowed is True
        assert reason is None

    async def test_validate_denied_command(self, manager_with_blacklist):
        """Test validation of denied command."""
        manager = await manager_with_blacklist
        is_allowed, reason = manager.validate_command("rm -rf /")
        assert is_allowed is False
        assert "blacklist" in reason.lower()

        is_allowed, reason = manager.validate_command("sudo rm file")
        assert is_allowed is False
        assert "blacklist" in reason.lower()

    async def test_validate_command_not_in_whitelist(self, manager_with_whitelist):
        """Test validation of command not in whitelist."""
        manager = await manager_with_whitelist
        is_allowed, reason = manager.validate_command("cat /etc/passwd")
        assert is_allowed is False
        assert "whitelist" in reason.lower()

    async def test_wildcard_whitelist_commands(self, manager_with_blacklist):
        """Test wildcard in whitelist commands."""
        manager = await manager_with_blacklist
        # Should allow any command except denied ones
        is_allowed, reason = manager.validate_command("ls -la")
        assert is_allowed is True

        is_allowed, reason = manager.validate_command("cat file.txt")
        assert is_allowed is True

        is_allowed, reason = manager.validate_command("echo 'test'")
        assert is_allowed is True

        # But should deny explicitly denied commands
        is_allowed, reason = manager.validate_command("rm file.txt")
        assert is_allowed is False


# {{END_MODIFICATIONS}}
