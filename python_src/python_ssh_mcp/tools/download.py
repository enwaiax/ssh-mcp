# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "c43987f7-0900-49b3-b9ca-37ca452955d9"
#   Timestamp: "2025-08-05T20:00:30+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + FastMCP工具实现"
#   Quality_Check: "download工具实现，与TypeScript版本接口完全一致"
# }}
# {{START_MODIFICATIONS}}
"""
Download MCP Tool

This module implements the download MCP tool for SSH file download.
Compatible with TypeScript version interface.
"""

from fastmcp import FastMCP

from ..ssh_manager import SSHConnectionManager


def register_download_tool(mcp: FastMCP, ssh_manager: SSHConnectionManager) -> None:
    """
    Register download tool with FastMCP server.

    Args:
        mcp: FastMCP server instance
        ssh_manager: SSH connection manager instance
    """

    @mcp.tool()
    async def download(
        remotePath: str, localPath: str, connectionName: str | None = None
    ):
        """
        Download file from connected server.

        Args:
            remotePath: Remote path
            localPath: Local path
            connectionName: SSH connection name (optional, default is 'default')

        Returns:
            MCP response with download result or error message
        """
        try:
            result = await ssh_manager.download(remotePath, localPath, connectionName)
            return result.strip() if result else "Download completed successfully"
        except Exception as error:
            return f"Download error: {str(error)}"


__all__ = ["register_download_tool"]
# {{END_MODIFICATIONS}}
