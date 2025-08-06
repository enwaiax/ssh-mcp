#!/usr/bin/env python3
"""
FastMCP SSH Server v2 - Optimized Server Implementation

This module provides an optimized server implementation that supports
automatic registration of v2 best practice tools while maintaining
backward compatibility with the original SSHMCPServer interface.

Key improvements:
- Automatic tool registration using direct decorators
- Environment-based version switching (v1/v2)
- Enhanced logging with structured context
- Simplified initialization and lifecycle management
- Improved error handling and graceful shutdown

Author: AI Assistant
Version: 2.0.0
"""

from fastmcp import FastMCP

from ...models import SshConnectionConfigMap
from ...ssh_manager import SSHConnectionManager
from ...utils import Logger
from .ssh_tools import initialize_server as init_v2_server
from .ssh_tools import mcp as v2_mcp


class OptimizedSSHMCPServer:
    """
    Optimized SSH MCP Server with best practices implementation.

    This server automatically registers v2 tools using direct decorators
    and provides backward compatibility with the original server interface.
    Supports environment-based version switching for gradual migration.

    Features:
    - Automatic v2 tool registration
    - Context-aware logging and progress reporting
    - Rich tool metadata for better LLM interaction
    - Environment-based version control
    - Graceful shutdown and resource cleanup
    """

    def __init__(self, name: str = "ssh-mcp-server-v2"):
        """
        Initialize the optimized SSH MCP server.

        Args:
            name: Server name for MCP identification
        """
        # Initialize logger
        self.logger = Logger()

        # Use pre-configured v2 MCP instance with registered tools
        self.mcp = v2_mcp
        self.logger.info(
            f"Initialized optimized server with v2 tools (using '{self.mcp.name}')"
        )

        self._ssh_manager: SSHConnectionManager | None = None
        self._is_initialized = False

    async def initialize(self, ssh_configs: SshConnectionConfigMap) -> None:
        """
        Initialize SSH connections and configure tools.

        Args:
            ssh_configs: SSH connection configuration map

        Raises:
            RuntimeError: If initialization fails
        """
        try:
            self.logger.info(
                f"Initializing server with {len(ssh_configs)} SSH configurations"
            )

            # Initialize with v2 tools (unified implementation)
            await self._initialize_v2(ssh_configs)

            self._is_initialized = True
            self.logger.info("Server initialization completed successfully")

        except Exception as e:
            self.logger.error(f"Server initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize server: {e}") from e

    async def _initialize_v2(self, ssh_configs: SshConnectionConfigMap) -> None:
        """Initialize server with v2 best practices tools."""
        # Initialize SSH manager singleton
        self._ssh_manager = await SSHConnectionManager.get_instance()
        self._ssh_manager.set_config(ssh_configs)

        # Connect to all SSH servers
        await self._ssh_manager.connect_all()

        # Set global SSH manager for v2 tools access
        from .ssh_tools import set_ssh_manager

        set_ssh_manager(self._ssh_manager)

        self.logger.info("v2 tools automatically registered via decorators")

    async def run(self, **kwargs) -> None:
        """
        Start the FastMCP server.

        Args:
            **kwargs: Additional arguments passed to FastMCP.run_async()

        Raises:
            RuntimeError: If server is not initialized
        """
        if not self._is_initialized:
            raise RuntimeError("Server must be initialized before running")

        try:
            version_info = (
                "v2 (optimized)" if self._use_v2_tools else "v1 (compatibility)"
            )
            self.logger.info(f"Starting FastMCP server with {version_info} tools")

            # Start the FastMCP server using async method
            await self.mcp.run_async(**kwargs)

        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal (Ctrl+C)")
            await self.cleanup()
        except Exception as e:
            self.logger.error(f"Server runtime error: {e}")
            await self.cleanup()
            raise

    async def cleanup(self) -> None:
        """Cleanup resources when shutting down."""
        try:
            self.logger.info("Starting server cleanup")

            if self._ssh_manager:
                await self._ssh_manager.disconnect()
                self.logger.info("SSH connections closed")

            self._is_initialized = False
            self.logger.info("Server cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def get_server_info(self) -> dict[str, str | bool | int]:
        """
        Get server information for monitoring and debugging.

        Returns:
            Dictionary containing server status and configuration
        """
        return {
            "name": self.mcp.name,
            "version": "2.0.0",
            "tools_version": "v2" if self._use_v2_tools else "v1",
            "initialized": self._is_initialized,
            "ssh_manager_active": self._ssh_manager is not None,
            "tool_count": len(self.mcp._tools) if hasattr(self.mcp, "_tools") else 0,
        }


# Convenience function for backward compatibility
async def initialize_with_tools(
    ssh_configs: SshConnectionConfigMap,
) -> OptimizedSSHMCPServer:
    """
    Initialize optimized SSH MCP server with automatic tool registration.

    This is the recommended way to create and initialize the server
    with v2 best practices tools.

    Args:
        ssh_configs: SSH connection configuration dictionary

    Returns:
        Initialized and ready-to-run server instance

    Raises:
        RuntimeError: If initialization fails
    """
    server = OptimizedSSHMCPServer()
    await server.initialize(ssh_configs)
    return server


# Alternative initialization for direct v2 usage
async def create_v2_server(
    ssh_configs: SshConnectionConfigMap, name: str = "ssh-mcp-v2"
) -> FastMCP:
    """
    Create and configure a v2 FastMCP server directly.

    This function provides a more direct approach when you only need
    the v2 implementation without compatibility layers.

    Args:
        ssh_configs: SSH connection configuration dictionary
        name: Server name for identification

    Returns:
        Configured FastMCP server instance ready to run

    Raises:
        RuntimeError: If initialization fails
    """
    try:
        # Use the v2 initialization function
        server = await init_v2_server(ssh_configs)
        # Note: FastMCP name is read-only, using the pre-configured name
        return server
    except Exception as e:
        raise RuntimeError(f"Failed to create v2 server: {e}") from e


__all__ = ["OptimizedSSHMCPServer", "initialize_with_tools", "create_v2_server"]
