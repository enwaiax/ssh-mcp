# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "c43987f7-0900-49b3-b9ca-37ca452955d9"
#   Timestamp: "2025-08-05T20:00:30+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + FastMCP工具实现"
#   Quality_Check: "execute-command工具实现，与TypeScript版本接口完全一致"
# }}
# {{START_MODIFICATIONS}}
"""
Execute Command MCP Tool

This module implements the execute-command MCP tool for SSH command execution.
Compatible with TypeScript version interface.
"""

from fastmcp import FastMCP

from ..ssh_manager import SSHConnectionManager


def register_execute_command_tool(
    mcp: FastMCP, ssh_manager: SSHConnectionManager
) -> None:
    """
    Register execute-command tool with FastMCP server.

    Args:
        mcp: FastMCP server instance
        ssh_manager: SSH connection manager instance
    """

    @mcp.tool("execute-command")
    async def execute_command(cmdString: str, connectionName: str | None = None):
        """
        Execute command on connected server and get output result.

        Args:
            cmdString: Command to execute
            connectionName: SSH connection name (optional, default is 'default')

        Returns:
            MCP response with command output or error message
        """
        try:
            result = await ssh_manager.execute_command(cmdString, connectionName)
            return result.strip() if result else ""
        except Exception as error:
            return f"Error: {str(error)}"


__all__ = ["register_execute_command_tool"]
# {{END_MODIFICATIONS}}
