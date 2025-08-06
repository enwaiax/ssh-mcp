# {{RIPER-5:
#   Action: "Modified"
#   Task_ID: "b7d05403-c627-41fd-a274-63ba6be6b32d"
#   Timestamp: "2025-08-05T19:52:32+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + Typer现代CLI框架"
#   Quality_Check: "重构为Typer框架，提供类型安全的CLI，与FastMCP技术栈统一"
# }}
# {{START_MODIFICATIONS}}
"""
CLI Module

This module contains CLI argument parsing functionality using Typer.
Supports both single connection and multiple connection modes,
fully compatible with TypeScript version parameters.
Modern type-safe implementation using Python 3.12+ features.
"""

from typing import Annotated

import typer

from .models import SSHConfig, SshConnectionConfigMap

# Try to get version from package metadata
try:
    import importlib.metadata

    __version__ = importlib.metadata.version("fastmcp-ssh-server")
except (importlib.metadata.PackageNotFoundError, Exception):
    __version__ = "0.1.0"  # Fallback version


# Version callback
def version_callback(value: bool):
    if value:
        typer.echo(f"SSH MCP Server v{__version__}")
        raise typer.Exit()


# Create Typer app
app = typer.Typer(
    name="ssh-mcp-server",
    help="SSH MCP Server - Python implementation using FastMCP",
    add_completion=False,
)


class CLIParser:
    """
    Command line argument parser class.

    Supports:
    - Multiple connections via --ssh parameter
    - Single connection via individual parameters
    - Legacy positional arguments
    - Command whitelist/blacklist configuration
    - Unified SSH MCP tools implementation
    """

    @staticmethod
    def parse_ssh_string(ssh_string: str) -> SSHConfig:
        """
        Parse SSH connection string format.

        Format: name=dev,host=1.2.3.4,port=22,user=alice,password=xxx

        Args:
            ssh_string: SSH connection configuration string

        Returns:
            SSHConfig: Parsed SSH configuration

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        parts = ssh_string.split(",")
        config_dict = {}

        for part in parts:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            if key and value:
                config_dict[key.strip()] = value.strip()

        # Validate required parameters
        required_fields = ["name", "host", "port", "user"]
        missing_fields = [
            field for field in required_fields if field not in config_dict
        ]

        if missing_fields:
            raise ValueError(
                f"Each --ssh must include {', '.join(required_fields)}. Missing: {', '.join(missing_fields)}"
            )

        # Validate port number
        try:
            port = int(config_dict["port"])
        except ValueError as e:
            raise ValueError(
                "Port for connection {config_dict['name']} must be a valid number"
            ) from e

        # Check authentication method
        if not config_dict.get("password") and not config_dict.get("privateKey"):
            raise ValueError(
                f"Connection {config_dict['name']} must have either password or privateKey"
            )

        # Parse whitelist/blacklist
        whitelist = None
        if config_dict.get("whitelist"):
            whitelist = [
                pattern.strip()
                for pattern in config_dict["whitelist"].split("|")
                if pattern.strip()
            ]

        blacklist = None
        if config_dict.get("blacklist"):
            blacklist = [
                pattern.strip()
                for pattern in config_dict["blacklist"].split("|")
                if pattern.strip()
            ]

        return SSHConfig(
            name=config_dict["name"],
            host=config_dict["host"],
            port=port,
            username=config_dict["user"],
            password=config_dict.get("password"),
            private_key=config_dict.get("privateKey"),
            passphrase=config_dict.get("passphrase"),
            command_whitelist=whitelist,
            command_blacklist=blacklist,
        )

    @staticmethod
    def create_single_connection_config(
        host: str | None,
        port: str | None,
        username: str | None,
        password: str | None,
        private_key: str | None,
        passphrase: str | None,
        whitelist: str | None,
        blacklist: str | None,
        positionals: tuple[str, ...] = (),
    ) -> SSHConfig:
        """
        Create SSH config from single connection parameters.

        Args:
            host: SSH hostname
            port: SSH port
            username: SSH username
            password: SSH password
            private_key: SSH private key path
            passphrase: Private key passphrase
            whitelist: Command whitelist patterns (comma-separated)
            blacklist: Command blacklist patterns (comma-separated)
            positionals: Positional arguments as fallback

        Returns:
            SSHConfig: SSH configuration

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Use positional arguments as fallback
        if not host and len(positionals) > 0:
            host = positionals[0]
        if not port and len(positionals) > 1:
            port = positionals[1]
        if not username and len(positionals) > 2:
            username = positionals[2]
        if not password and len(positionals) > 3:
            password = positionals[3]

        # Set default port if not provided
        if not port:
            port = "22"

        # Validate required parameters
        if not host or not username:
            raise ValueError("Missing required parameters: need host, username")

        if not password and not private_key:
            raise ValueError("Missing authentication: need password or private key")

        # Validate port number
        try:
            port_num = int(port)
        except ValueError as e:
            raise ValueError("Port must be a valid number") from e

        # Parse whitelist/blacklist
        whitelist_patterns = None
        if whitelist:
            whitelist_patterns = [
                pattern.strip() for pattern in whitelist.split(",") if pattern.strip()
            ]

        blacklist_patterns = None
        if blacklist:
            blacklist_patterns = [
                pattern.strip() for pattern in blacklist.split(",") if pattern.strip()
            ]

        return SSHConfig(
            name="default",
            host=host,
            port=port_num,
            username=username,
            password=password,
            private_key=private_key,
            passphrase=passphrase,
            command_whitelist=whitelist_patterns,
            command_blacklist=blacklist_patterns,
        )


@app.command()
def main(
    ssh: Annotated[
        list[str],
        typer.Option(
            help="SSH connection string: name=dev,host=1.2.3.4,port=22,user=alice,password=xxx"
        ),
    ] = None,
    host: Annotated[
        str | None,
        typer.Option("--host", "-h", help="SSH hostname (single connection mode)"),
    ] = None,
    port: Annotated[
        str | None,
        typer.Option("--port", "-p", help="SSH port (single connection mode)"),
    ] = None,
    username: Annotated[
        str | None,
        typer.Option("--username", "-u", help="SSH username (single connection mode)"),
    ] = None,
    password: Annotated[
        str | None,
        typer.Option("--password", "-w", help="SSH password (single connection mode)"),
    ] = None,
    private_key: Annotated[
        str | None,
        typer.Option(
            "--private-key",
            "-k",
            help="SSH private key file path (single connection mode)",
        ),
    ] = None,
    passphrase: Annotated[
        str | None,
        typer.Option(
            "--passphrase",
            "-P",
            help="SSH private key passphrase (single connection mode)",
        ),
    ] = None,
    whitelist: Annotated[
        str | None,
        typer.Option(
            "--whitelist", "-W", help="Command whitelist patterns (comma-separated)"
        ),
    ] = None,
    blacklist: Annotated[
        str | None,
        typer.Option(
            "--blacklist", "-B", help="Command blacklist patterns (comma-separated)"
        ),
    ] = None,
    positionals: Annotated[
        list[str] | None,
        typer.Argument(help="Positional arguments: host port username password"),
    ] = None,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
):
    """
    SSH MCP Server - Python implementation using FastMCP.

    Multiple connection mode:
        --ssh name=dev,host=1.2.3.4,port=22,user=alice,password=xxx
        --ssh name=prod,host=5.6.7.8,port=22,user=bob,privateKey=/path/to/key

    Single connection mode:
        --host 1.2.3.4 --port 22 --username alice --password xxx
        Or: python main.py 1.2.3.4 22 alice xxx

    The server uses the unified SSH MCP tools implementation with enhanced
    features including FastMCP best practices, Context support, and improved
    error handling.
    """
    import asyncio

    try:
        config_map = parse_cli_args(
            tuple(ssh) if ssh else (),
            host,
            port,
            username,
            password,
            private_key,
            passphrase,
            whitelist,
            blacklist,
            tuple(positionals) if positionals else (),
        )

        # Import the server startup function
        from .main import start_server_with_config

        # Start the server
        asyncio.run(start_server_with_config(config_map))

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1) from e


def parse_cli_args(
    ssh_params: tuple[str, ...] = (),
    host: str | None = None,
    port: str | None = None,
    username: str | None = None,
    password: str | None = None,
    private_key: str | None = None,
    passphrase: str | None = None,
    whitelist: str | None = None,
    blacklist: str | None = None,
    positionals: tuple[str, ...] = (),
) -> SshConnectionConfigMap:
    """
    Parse CLI arguments and return SSH connection configuration map.

    Args:
        ssh_params: Multiple SSH connection strings
        host: Single connection hostname
        port: Single connection port
        username: Single connection username
        password: Single connection password
        private_key: Single connection private key path
        passphrase: Private key passphrase
        whitelist: Command whitelist patterns
        blacklist: Command blacklist patterns
        positionals: Positional arguments

    Returns:
        SshConnectionConfigMap: Dictionary of connection configurations

    Raises:
        ValueError: If parameters are invalid or missing
    """
    config_map: SshConnectionConfigMap = {}

    # Parse multiple SSH connection strings
    for ssh_string in ssh_params:
        try:
            ssh_config = CLIParser.parse_ssh_string(ssh_string)
            config_map[ssh_config.name] = ssh_config
        except Exception as e:
            raise ValueError(f"Failed to parse SSH string '{ssh_string}': {e}") from e

    # If no multi-connection configs, try single connection mode
    if not config_map:
        try:
            single_config = CLIParser.create_single_connection_config(
                host,
                port,
                username,
                password,
                private_key,
                passphrase,
                whitelist,
                blacklist,
                positionals,
            )
            config_map["default"] = single_config
        except Exception as e:
            raise ValueError(
                f"Failed to parse single connection parameters: {e}"
            ) from e

    return config_map


# Convenience function for running the app
def run_cli() -> None:
    """Run the Typer CLI application."""
    app()


__all__ = ["CLIParser", "parse_cli_args", "main", "app", "run_cli"]
# {{END_MODIFICATIONS}}
