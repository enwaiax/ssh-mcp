# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "c43987f7-0900-49b3-b9ca-37ca452955d9"
#   Timestamp: "2025-08-05T20:00:30+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + FastMCP工具注册"
#   Quality_Check: "FastMCP服务器实例创建和工具注册，与TypeScript版本完全兼容"
# }}
# {{START_MODIFICATIONS}}
"""
FastMCP Server Module

This module creates and configures the FastMCP server instance,
and registers all SSH-related MCP tools.
Compatible with TypeScript version interface.
"""

from fastmcp import FastMCP

from .models import SshConnectionConfigMap
from .ssh_manager import SSHConnectionManager


class SSHMCPServer:
    """
    SSH MCP Server using FastMCP framework.

    Manages SSH connections and provides MCP tools for:
    - Command execution
    - File upload/download
    - Server listing
    """

    def __init__(self, name: str = "ssh-mcp-server"):
        """
        Initialize SSH MCP Server.

        Args:
            name: Server name for MCP identification
        """
        # Create FastMCP server instance
        self.mcp = FastMCP(name)
        self._ssh_manager: SSHConnectionManager | None = None

    async def initialize(self, ssh_configs: SshConnectionConfigMap) -> None:
        """
        Initialize SSH connections and register tools.

        Args:
            ssh_configs: SSH connection configuration map
        """
        # Initialize SSH manager
        self._ssh_manager = await SSHConnectionManager.get_instance()
        self._ssh_manager.set_config(ssh_configs)

        # Connect to all configured SSH servers
        await self._ssh_manager.connect_all()

        # Register all MCP tools
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all MCP tools with FastMCP server."""
        # Import tool registration functions
        from .tools import (
            register_download_tool,
            register_execute_command_tool,
            register_list_servers_tool,
            register_upload_tool,
        )

        # Register tools with the MCP server
        register_execute_command_tool(self.mcp, self._ssh_manager)
        register_upload_tool(self.mcp, self._ssh_manager)
        register_download_tool(self.mcp, self._ssh_manager)
        register_list_servers_tool(self.mcp, self._ssh_manager)

    async def run(self, **kwargs) -> None:
        """
        Start the FastMCP server.

        Args:
            **kwargs: Additional arguments passed to FastMCP.run_async()
        """
        # Start the FastMCP server using async method
        await self.mcp.run_async(**kwargs)

    async def cleanup(self) -> None:
        """Cleanup resources when shutting down."""
        if self._ssh_manager:
            await self._ssh_manager.disconnect()


__all__ = ["SSHMCPServer"]
# {{END_MODIFICATIONS}}
