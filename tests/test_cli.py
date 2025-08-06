# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "7037bed8-d479-44e6-9198-c81f69b9d05d"
#   Timestamp: "2025-08-05T20:50:09+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + 测试驱动开发"
#   Quality_Check: "全面的CLI解析器测试，包含单连接、多连接、参数验证等"
# }}
# {{START_MODIFICATIONS}}
"""
CLI Parser Tests

Comprehensive tests for CLI argument parsing including:
- Single connection mode
- Multiple connection mode
- SSH connection string parsing
- Security configuration parsing
- Error handling and validation
- Typer integration
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the python_src directory to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "python_src"))

from python_ssh_mcp.cli import CLIParser, parse_cli_args
from python_ssh_mcp.models import SSHConfig
from python_ssh_mcp.utils import ConfigurationError


class TestSSHConnectionStringParsing:
    """Test suite for SSH connection string parsing."""

    def test_parse_basic_connection_string(self):
        """Test parsing basic SSH connection string."""
        conn_str = "user@host"
        result = CLIParser.parse_ssh_string(conn_str)

        assert result["username"] == "user"
        assert result["host"] == "host"
        assert result["port"] == 22  # default port

    def test_parse_connection_string_with_port(self):
        """Test parsing SSH connection string with port."""
        conn_str = "user@host:2222"
        result = CLIParser.parse_ssh_string(conn_str)

        assert result["username"] == "user"
        assert result["host"] == "host"
        assert result["port"] == 2222

    def test_parse_connection_string_host_only(self):
        """Test parsing SSH connection string with host only."""
        conn_str = "example.com"
        result = CLIParser.parse_ssh_string(conn_str)

        assert result["username"] is None
        assert result["host"] == "example.com"
        assert result["port"] == 22

    def test_parse_connection_string_host_with_port(self):
        """Test parsing host with port but no username."""
        conn_str = "example.com:2222"
        result = CLIParser.parse_ssh_string(conn_str)

        assert result["username"] is None
        assert result["host"] == "example.com"
        assert result["port"] == 2222

    def test_parse_connection_string_ipv4(self):
        """Test parsing IPv4 address."""
        conn_str = "deploy@192.168.1.100:22"
        result = CLIParser.parse_ssh_string(conn_str)

        assert result["username"] == "deploy"
        assert result["host"] == "192.168.1.100"
        assert result["port"] == 22

    def test_parse_connection_string_ipv6(self):
        """Test parsing IPv6 address."""
        conn_str = "user@[2001:db8::1]:22"
        result = CLIParser.parse_ssh_string(conn_str)

        assert result["username"] == "user"
        assert result["host"] == "[2001:db8::1]"
        assert result["port"] == 22

    def test_parse_invalid_connection_string(self):
        """Test parsing invalid connection string."""
        with pytest.raises(ConfigurationError, match="Invalid SSH connection format"):
            CLIParser.parse_ssh_string("")

        with pytest.raises(ConfigurationError, match="Invalid SSH connection format"):
            CLIParser.parse_ssh_string("   ")

    def test_parse_connection_string_invalid_port(self):
        """Test parsing connection string with invalid port."""
        with pytest.raises(ConfigurationError, match="Invalid port number"):
            CLIParser.parse_ssh_string("user@host:abc")

        with pytest.raises(ConfigurationError, match="Invalid port number"):
            CLIParser.parse_ssh_string("user@host:99999")


class TestCLIArgumentParsing:
    """Test suite for CLI argument parsing."""

    def test_single_connection_minimal_args(self):
        """Test parsing minimal single connection arguments."""
        test_args = [
            "--host",
            "example.com",
            "--username",
            "testuser",
            "--password",
            "testpass",
        ]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        assert len(configs) == 1
        config = configs[0]
        assert config.name == "default"
        assert config.host == "example.com"
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.port == 22  # default

    def test_single_connection_full_args(self):
        """Test parsing full single connection arguments."""
        test_args = [
            "--host",
            "prod.example.com",
            "--port",
            "2222",
            "--username",
            "deploy",
            "--password",
            "secret123",
            "--name",
            "production",
            "--whitelist",
            "ls,pwd,echo",
            "--blacklist",
            "rm,sudo",
        ]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        assert len(configs) == 1
        config = configs[0]
        assert config.name == "production"
        assert config.host == "prod.example.com"
        assert config.port == 2222
        assert config.username == "deploy"
        assert config.password == "secret123"
        assert config.command_whitelist == ["ls", "pwd", "echo"]
        assert config.command_blacklist == ["rm", "sudo"]

    def test_single_connection_with_private_key(self):
        """Test parsing single connection with private key."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pem", delete=False
        ) as key_file:
            key_file.write(
                "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----"
            )
            key_path = key_file.name

        test_args = [
            "--host",
            "secure.example.com",
            "--username",
            "keyuser",
            "--private-key",
            key_path,
        ]

        try:
            with patch("sys.argv", ["script"] + test_args):
                configs = parse_cli_args()

            assert len(configs) == 1
            config = configs[0]
            assert config.private_key_path == key_path
            assert config.password is None
        finally:
            Path(key_path).unlink()

    def test_multiple_connections_ssh_format(self):
        """Test parsing multiple connections in SSH format."""
        test_args = ["user1@server1.com:22", "user2@server2.com:2222", "server3.com"]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        assert len(configs) == 3

        # First connection
        assert configs[0].name == "server1_com"
        assert configs[0].host == "server1.com"
        assert configs[0].username == "user1"
        assert configs[0].port == 22

        # Second connection
        assert configs[1].name == "server2_com"
        assert configs[1].host == "server2.com"
        assert configs[1].username == "user2"
        assert configs[1].port == 2222

        # Third connection (host only)
        assert configs[2].name == "server3_com"
        assert configs[2].host == "server3.com"
        assert configs[2].username is None
        assert configs[2].port == 22

    def test_multiple_connections_with_global_options(self):
        """Test multiple connections with global security options."""
        test_args = [
            "--whitelist",
            "ls,pwd,cat",
            "--blacklist",
            "rm,mv",
            "admin@web1.example.com:22",
            "admin@web2.example.com:22",
        ]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        assert len(configs) == 2

        # Verify global options applied to all connections
        for config in configs:
            assert config.command_whitelist == ["ls", "pwd", "cat"]
            assert config.command_blacklist == ["rm", "mv"]

    def test_mixed_connection_formats(self):
        """Test mixing different connection formats."""
        test_args = ["192.168.1.10", "deploy@staging.example.com:2222"]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        assert len(configs) == 2
        assert configs[0].host == "192.168.1.10"
        assert configs[1].host == "staging.example.com"
        assert configs[1].username == "deploy"

    def test_no_connections_error(self):
        """Test error when no connections provided."""
        test_args = []

        with patch("sys.argv", ["script"] + test_args):
            with pytest.raises(SystemExit):
                parse_cli_args()

    def test_invalid_private_key_path(self):
        """Test error with invalid private key path."""
        test_args = [
            "--host",
            "example.com",
            "--username",
            "user",
            "--private-key",
            "/non/existent/key.pem",
        ]

        with patch("sys.argv", ["script"] + test_args):
            with pytest.raises(ConfigurationError, match="Private key file not found"):
                parse_cli_args()

    def test_conflicting_authentication_methods(self):
        """Test error with both password and private key."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pem", delete=False
        ) as key_file:
            key_file.write("test key")
            key_path = key_file.name

        test_args = [
            "--host",
            "example.com",
            "--username",
            "user",
            "--password",
            "pass123",
            "--private-key",
            key_path,
        ]

        try:
            with patch("sys.argv", ["script"] + test_args):
                with pytest.raises(
                    ConfigurationError,
                    match="Cannot specify both password and private key",
                ):
                    parse_cli_args()
        finally:
            Path(key_path).unlink()

    def test_missing_required_fields_single_mode(self):
        """Test error when required fields missing in single connection mode."""
        test_args = [
            "--host",
            "example.com",
            # Missing username and authentication
        ]

        with patch("sys.argv", ["script"] + test_args):
            with pytest.raises(ConfigurationError, match="Username is required"):
                parse_cli_args()

    def test_security_commands_parsing(self):
        """Test parsing of security command lists."""
        test_args = [
            "--host",
            "example.com",
            "--username",
            "user",
            "--password",
            "pass",
            "--whitelist",
            "git pull,git status,npm install",
            "--blacklist",
            "git push --force,rm -rf",
        ]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        config = configs[0]
        assert config.command_whitelist == ["git pull", "git status", "npm install"]
        assert config.command_blacklist == ["git push --force", "rm -rf"]

    def test_empty_security_commands(self):
        """Test handling of empty security command lists."""
        test_args = [
            "--host",
            "example.com",
            "--username",
            "user",
            "--password",
            "pass",
            "--whitelist",
            "",
            "--blacklist",
            "",
        ]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        config = configs[0]
        assert config.command_whitelist == []
        assert config.command_blacklist == []

    def test_wildcard_command_whitelist(self):
        """Test wildcard in allow commands."""
        test_args = [
            "--host",
            "example.com",
            "--username",
            "user",
            "--password",
            "pass",
            "--whitelist",
            "*",
            "--blacklist",
            "rm,sudo",
        ]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        config = configs[0]
        assert config.command_whitelist == ["*"]
        assert config.command_blacklist == ["rm", "sudo"]


class TestCLIErrorHandling:
    """Test suite for CLI error handling."""

    def test_invalid_port_range(self):
        """Test error with port out of valid range."""
        test_args = [
            "--host",
            "example.com",
            "--port",
            "99999",
            "--username",
            "user",
            "--password",
            "pass",
        ]

        with patch("sys.argv", ["script"] + test_args):
            with pytest.raises(SystemExit):  # Typer validation error
                parse_cli_args()

    def test_invalid_host_format(self):
        """Test handling of various host formats."""
        # Test with spaces (should be handled gracefully)
        test_args = ["user@host with spaces.com"]

        with patch("sys.argv", ["script"] + test_args):
            # Should not raise error, but create config with the host as-is
            configs = parse_cli_args()
            assert configs[0].host == "host with spaces.com"

    def test_special_characters_in_commands(self):
        """Test handling of special characters in command lists."""
        test_args = [
            "--host",
            "example.com",
            "--username",
            "user",
            "--password",
            "pass",
            "--whitelist",
            "echo 'hello world',ls -la | grep test",
            "--blacklist",
            "rm -rf /*,sudo su -",
        ]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        config = configs[0]
        assert "echo 'hello world'" in config.command_whitelist
        assert "ls -la | grep test" in config.command_whitelist
        assert "rm -rf /*" in config.command_blacklist
        assert "sudo su -" in config.command_blacklist


class TestCLIConfigGeneration:
    """Test suite for SSH config generation from CLI args."""

    def test_config_name_generation(self):
        """Test automatic config name generation."""
        test_args = [
            "user@web-server-01.prod.example.com:22",
            "backup@db-server.staging.example.com:2222",
        ]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        # Test name sanitization
        assert configs[0].name == "web_server_01_prod_example_com"
        assert configs[1].name == "db_server_staging_example_com"

    def test_config_name_collision_handling(self):
        """Test handling of potential config name collisions."""
        test_args = ["server.example.com:22", "server.example.com:2222"]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        # Both should have unique names despite same host
        assert len(configs) == 2
        assert configs[0].name != configs[1].name

    def test_config_defaults(self):
        """Test that config objects have correct defaults."""
        test_args = ["user@example.com"]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        config = configs[0]
        assert config.port == 22
        assert config.command_whitelist == []
        assert config.command_blacklist == []
        assert config.password is None
        assert config.private_key_path is None

    def test_config_validation(self):
        """Test that generated configs pass validation."""
        test_args = [
            "--host",
            "valid.example.com",
            "--username",
            "validuser",
            "--password",
            "validpass",
            "--port",
            "22",
            "--whitelist",
            "ls,pwd",
            "--blacklist",
            "rm",
        ]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        # Config should be valid SSHConfig object
        config = configs[0]
        assert isinstance(config, SSHConfig)

        # Test that all fields are properly set
        assert config.host == "valid.example.com"
        assert config.username == "validuser"
        assert config.password == "validpass"
        assert config.port == 22
        assert isinstance(config.command_whitelist, list)
        assert isinstance(config.command_blacklist, list)


class TestTyperIntegration:
    """Test suite for Typer CLI framework integration."""

    def test_help_output(self):
        """Test that help output is generated correctly."""
        test_args = ["--help"]

        with patch("sys.argv", ["script"] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_cli_args()

            # Help should exit with code 0
            assert exc_info.value.code == 0

    def test_version_output(self):
        """Test that version output works."""
        test_args = ["--version"]

        with patch("sys.argv", ["script"] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_cli_args()

            # Version should exit with code 0
            assert exc_info.value.code == 0

    def test_command_completion(self):
        """Test that command completion setup works."""
        # This would test shell completion setup
        # Implementation depends on specific Typer completion setup
        pass

    def test_error_formatting(self):
        """Test that Typer error messages are properly formatted."""
        test_args = ["--port", "invalid_port", "--host", "example.com"]

        with patch("sys.argv", ["script"] + test_args):
            with pytest.raises(SystemExit):
                # Typer should handle invalid port gracefully
                parse_cli_args()

    def test_argument_parsing_edge_cases(self):
        """Test edge cases in argument parsing."""
        # Test with equals sign syntax
        test_args = ["--host=example.com", "--username=user", "--password=pass"]

        with patch("sys.argv", ["script"] + test_args):
            configs = parse_cli_args()

        config = configs[0]
        assert config.host == "example.com"
        assert config.username == "user"
        assert config.password == "pass"

    def test_boolean_flag_handling(self):
        """Test boolean flag handling if any are added."""
        # This test is prepared for future boolean flags
        # like --verbose, --quiet, --debug, etc.
        pass


# {{END_MODIFICATIONS}}
