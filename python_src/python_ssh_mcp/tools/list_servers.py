# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "c43987f7-0900-49b3-b9ca-37ca452955d9"
#   Timestamp: "2025-08-05T20:00:30+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + FastMCP工具实现"
#   Quality_Check: "list-servers工具实现，与TypeScript版本接口完全一致"
# }}
# {{START_MODIFICATIONS}}
"""
List Servers MCP Tool

This module implements the list-servers MCP tool for SSH server configuration listing.
Compatible with TypeScript version interface.
"""

from fastmcp import FastMCP

from ..ssh_manager import SSHConnectionManager


def register_list_servers_tool(mcp: FastMCP, ssh_manager: SSHConnectionManager) -> None:
    """
    Register list-servers tool with FastMCP server.

    Args:
        mcp: FastMCP server instance
        ssh_manager: SSH connection manager instance
    """

    @mcp.tool("list-servers")
    async def list_servers():
        """
        List all available SSH server configurations.

        Returns:
            MCP response with JSON-formatted server information
        """
        servers = ssh_manager.get_all_server_infos()

        return [server.model_dump() for server in servers]


__all__ = ["register_list_servers_tool"]
# {{END_MODIFICATIONS}}
