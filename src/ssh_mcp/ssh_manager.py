# {{RIPER-5:
#   Action: "Modified"
#   Task_ID: "e4da4c91-385e-4709-8f0f-ddaa9cdb70c8"
#   Timestamp: "2025-08-05T19:38:10+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + SFTP异步文件传输"
#   Quality_Check: "增强SFTP文件传输功能，完善错误处理，与TypeScript版本完全兼容"
# }}
# {{START_MODIFICATIONS}}
"""
SSH Connection Manager Module

This module contains the SSH connection manager class for handling
multiple SSH connections using AsyncSSH. Implements singleton pattern
for centralized connection management.
"""

import asyncio
import re
from pathlib import Path
from typing import Any, Optional

import asyncssh

from .models import ServerInfo, SSHConfig, SshConnectionConfigMap
from .utils import Logger


class SSHConnectionManager:
    """
    SSH Connection Manager singleton class.

    Manages multiple SSH connections using AsyncSSH, providing:
    - Connection pooling and lifecycle management
    - Multiple authentication methods (password, private key)
    - Command validation (whitelist/blacklist)
    - Async file transfer operations
    - Connection state tracking
    """

    _instance: Optional["SSHConnectionManager"] = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        """Private constructor for singleton pattern."""
        if SSHConnectionManager._instance is not None:
            raise RuntimeError(
                "Use SSHConnectionManager.get_instance() to get the singleton instance"
            )

        self._connections: dict[str, asyncssh.SSHClientConnection] = {}
        self._configs: SshConnectionConfigMap = {}
        self._connected: dict[str, bool] = {}
        self._default_name: str = "default"

    @classmethod
    async def get_instance(cls) -> "SSHConnectionManager":
        """Get singleton instance (thread-safe)."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def set_config(
        self, configs: SshConnectionConfigMap, default_name: str | None = None
    ) -> None:
        """
        Set SSH configurations for multiple connections.

        Args:
            configs: Dictionary mapping connection names to SSH configurations
            default_name: Optional default connection name, if not specified uses first config
        """
        self._configs = configs

        if default_name and default_name in configs:
            self._default_name = default_name
        elif configs:
            self._default_name = next(iter(configs.keys()))

        # Update connection name in configs if not set
        for name, config in self._configs.items():
            if config.name is None:
                config.name = name

    def get_config(self, name: str | None = None) -> SSHConfig:
        """
        Get SSH configuration for specified connection.

        Args:
            name: Connection name, uses default if not specified

        Returns:
            SSH configuration

        Raises:
            ValueError: If configuration not found
        """
        key = name or self._default_name
        if key not in self._configs:
            raise ValueError(f"SSH configuration for '{key}' not found")
        return self._configs[key]

    async def connect_all(self) -> None:
        """Connect to all configured SSH servers."""
        tasks = []
        for name in self._configs.keys():
            tasks.append(self.connect(name))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def connect(self, name: str | None = None) -> None:
        """
        Connect to specified SSH server.

        Args:
            name: Connection name, uses default if not specified

        Raises:
            ConnectionError: If connection fails
            ValueError: If configuration not found or invalid
        """
        key = name or self._default_name

        # Return if already connected
        if self._connected.get(key) and key in self._connections:
            return

        config = self.get_config(key)

        try:
            # Prepare connection options
            connect_kwargs: dict[str, Any] = {
                "host": config.host,
                "port": config.port,
                "username": config.username,
                "known_hosts": None,  # Disable host key checking for now
            }

            # Set authentication method
            if config.private_key:
                # Use private key authentication
                key_path = Path(config.private_key).expanduser()
                if not key_path.exists():
                    raise ValueError(f"Private key file not found: {key_path}")

                connect_kwargs["client_keys"] = [str(key_path)]
                if config.passphrase:
                    connect_kwargs["passphrase"] = config.passphrase

                Logger.info(f"Using SSH private key authentication for [{key}]")

            elif config.password:
                # Use password authentication
                connect_kwargs["password"] = config.password
                Logger.info(f"Using password authentication for [{key}]")

            else:
                raise ValueError(f"No valid authentication method provided for [{key}]")

            # Establish connection
            connection = await asyncssh.connect(**connect_kwargs)

            # Store connection and update status
            self._connections[key] = connection
            self._connected[key] = True

            Logger.info(
                f"Successfully connected to SSH server [{key}] {config.host}:{config.port}"
            )

        except Exception as e:
            self._connected[key] = False
            raise ConnectionError(f"SSH connection [{key}] failed: {str(e)}") from e

    def get_connection(self, name: str | None = None) -> asyncssh.SSHClientConnection:
        """
        Get SSH connection for specified name.

        Args:
            name: Connection name, uses default if not specified

        Returns:
            AsyncSSH connection object

        Raises:
            RuntimeError: If connection not established
        """
        key = name or self._default_name
        if key not in self._connections:
            raise RuntimeError(f"SSH connection for '{key}' not established")
        return self._connections[key]

    async def ensure_connected(
        self, name: str | None = None
    ) -> asyncssh.SSHClientConnection:
        """
        Ensure SSH connection is established, connect if needed.

        Args:
            name: Connection name, uses default if not specified

        Returns:
            AsyncSSH connection object
        """
        key = name or self._default_name

        if not self._connected.get(key) or key not in self._connections:
            await self.connect(key)

        return self.get_connection(key)

    def validate_command(
        self, command: str, name: str | None = None
    ) -> tuple[bool, str | None]:
        """
        Validate command against whitelist/blacklist rules.

        Args:
            command: Command to validate
            name: Connection name for configuration lookup

        Returns:
            Tuple of (is_allowed, reason)
        """
        config = self.get_config(name)

        # Check whitelist (if configured, command must match one pattern)
        if config.command_whitelist:
            matches_whitelist = any(
                re.search(pattern, command) for pattern in config.command_whitelist
            )
            if not matches_whitelist:
                return False, "Command not in whitelist, execution forbidden"

        # Check blacklist (if command matches any pattern, forbidden)
        if config.command_blacklist:
            matches_blacklist = any(
                re.search(pattern, command) for pattern in config.command_blacklist
            )
            if matches_blacklist:
                return False, "Command matches blacklist, execution forbidden"

        return True, None

    async def execute_command(
        self, cmd_string: str, name: str | None = None, timeout: int = 30
    ) -> str:
        """
        Execute command on SSH server with timeout support.

        Args:
            cmd_string: Command to execute
            name: Connection name, uses default if not specified
            timeout: Command timeout in seconds (default: 30)

        Returns:
            Command output (stdout)

        Raises:
            Exception: For validation failures, execution errors, or timeouts
                      (maintains compatibility with TypeScript version)
        """
        # Validate command
        is_allowed, reason = self.validate_command(cmd_string, name)
        if not is_allowed:
            raise Exception(f"Command validation failed: {reason}")

        # Get connection and execute
        connection = await self.ensure_connected(name)

        try:
            # Execute command with timeout
            result = await asyncio.wait_for(connection.run(cmd_string), timeout=timeout)

            if result.exit_status != 0:
                error_msg = result.stderr.strip() if result.stderr else ""
                raise Exception(
                    f"Command execution failed, exit code: {result.exit_status}, error: {error_msg}"
                )

            return result.stdout

        except TimeoutError:
            raise Exception(
                f"Command execution timeout after {timeout} seconds"
            ) from None
        except Exception as e:
            if "Command execution failed" in str(
                e
            ) or "Command validation failed" in str(e):
                raise  # Re-raise our custom exceptions
            raise Exception(f"Command execution error: {str(e)}") from e

    async def upload(
        self, local_path: str, remote_path: str, name: str | None = None
    ) -> str:
        """
        Upload file to SSH server using SFTP.

        Args:
            local_path: Local file path
            remote_path: Remote file path
            name: Connection name, uses default if not specified

        Returns:
            Success message: "File uploaded successfully"

        Raises:
            Exception: For file not found, SFTP connection, or upload failures
                      (maintains compatibility with TypeScript version)
        """
        # Validate local file exists
        local_file = Path(local_path).expanduser()
        if not local_file.exists():
            raise Exception(f"File upload failed: Local file not found: {local_path}")

        if not local_file.is_file():
            raise Exception(f"File upload failed: Path is not a file: {local_path}")

        connection = await self.ensure_connected(name)

        try:
            async with connection.start_sftp_client() as sftp:
                await sftp.put(str(local_file), remote_path)
            return "File uploaded successfully"

        except Exception as e:
            if "File upload failed:" in str(e):
                raise  # Re-raise our custom exceptions
            raise Exception(f"File upload failed: {str(e)}") from e

    async def download(
        self, remote_path: str, local_path: str, name: str | None = None
    ) -> str:
        """
        Download file from SSH server using SFTP.

        Args:
            remote_path: Remote file path
            local_path: Local file path
            name: Connection name, uses default if not specified

        Returns:
            Success message: "File downloaded successfully"

        Raises:
            Exception: For SFTP connection, remote file access, or download failures
                      (maintains compatibility with TypeScript version)
        """
        # Ensure local directory exists and expand user path
        local_file = Path(local_path).expanduser()
        local_file.parent.mkdir(parents=True, exist_ok=True)

        connection = await self.ensure_connected(name)

        try:
            async with connection.start_sftp_client() as sftp:
                await sftp.get(remote_path, str(local_file))
            return "File downloaded successfully"

        except Exception as e:
            if "File download failed:" in str(e):
                raise  # Re-raise our custom exceptions
            # Handle specific SFTP errors with appropriate messages
            error_msg = str(e)
            if "not found" in error_msg.lower() or "no such file" in error_msg.lower():
                raise Exception(
                    f"File download failed: Remote file not found: {remote_path}"
                ) from e
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                raise Exception(
                    f"File download failed: Permission denied: {remote_path}"
                ) from e
            else:
                raise Exception(f"File download failed: {error_msg}") from e

    async def disconnect(self, name: str | None = None) -> None:
        """
        Disconnect SSH connection.

        Args:
            name: Connection name, disconnects all if not specified
        """
        if name:
            # Disconnect specific connection
            if name in self._connections:
                self._connections[name].close()
                await self._connections[name].wait_closed()
                del self._connections[name]
                self._connected[name] = False
        else:
            # Disconnect all connections
            for connection in self._connections.values():
                connection.close()
                await connection.wait_closed()
            self._connections.clear()
            self._connected.clear()

    def get_all_server_infos(self) -> list[ServerInfo]:
        """
        Get information about all configured servers.

        Returns:
            List of server information objects
        """
        servers = []
        for name, config in self._configs.items():
            server_info = ServerInfo(
                name=name,
                host=config.host,
                port=config.port,
                username=config.username,
                connected=self._connected.get(name, False),
            )
            servers.append(server_info)

        return servers

    async def __aenter__(self) -> "SSHConnectionManager":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()


__all__ = ["SSHConnectionManager"]
# {{END_MODIFICATIONS}}
