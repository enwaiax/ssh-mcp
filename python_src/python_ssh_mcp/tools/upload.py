# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "c43987f7-0900-49b3-b9ca-37ca452955d9"
#   Timestamp: "2025-08-05T20:00:30+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + FastMCP工具实现"
#   Quality_Check: "upload工具实现，与TypeScript版本接口完全一致"
# }}
# {{START_MODIFICATIONS}}
"""
Upload MCP Tool

This module implements the upload MCP tool for SSH file upload.
Compatible with TypeScript version interface.
"""

from fastmcp import FastMCP

from ..ssh_manager import SSHConnectionManager


def register_upload_tool(mcp: FastMCP, ssh_manager: SSHConnectionManager) -> None:
    """
    Register upload tool with FastMCP server.

    Args:
        mcp: FastMCP server instance
        ssh_manager: SSH connection manager instance
    """

    @mcp.tool()
    async def upload(
        localPath: str, remotePath: str, connectionName: str | None = None
    ):
        """
        Upload file to connected server.

        Args:
            localPath: Local path
            remotePath: Remote path
            connectionName: SSH connection name (optional, default is 'default')

        Returns:
            MCP response with upload result or error message
        """
        try:
            result = await ssh_manager.upload(localPath, remotePath, connectionName)
            return result.strip() if result else "Upload completed successfully"
        except Exception as error:
            return f"Upload error: {str(error)}"


__all__ = ["register_upload_tool"]
# {{END_MODIFICATIONS}}
