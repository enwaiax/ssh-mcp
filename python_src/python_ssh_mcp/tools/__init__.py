# {{RIPER-5:
#   Action: "Modified"
#   Task_ID: "c43987f7-0900-49b3-b9ca-37ca452955d9"
#   Timestamp: "2025-08-05T20:00:30+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + FastMCP工具注册"
#   Quality_Check: "完整导入所有MCP工具注册函数，提供统一接口"
# }}
# {{START_MODIFICATIONS}}
"""
MCP Tools Module

This module contains the implementation of all MCP tools for SSH operations.
Each tool is implemented as a separate module following the FastMCP patterns.

Available tools:
- execute_command: Execute SSH commands on remote servers
- upload: Upload files to remote servers via SFTP
- download: Download files from remote servers via SFTP
- list_servers: List all configured SSH server connections
"""

# Import all tool registration functions
from .download import register_download_tool
from .execute_command import register_execute_command_tool
from .list_servers import register_list_servers_tool
from .upload import register_upload_tool

__all__ = [
    "register_execute_command_tool",
    "register_upload_tool",
    "register_download_tool",
    "register_list_servers_tool",
]
# {{END_MODIFICATIONS}}
