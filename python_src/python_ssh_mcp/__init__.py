# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "ec47c2ec-fcf4-4fba-9582-ee4c0dba3d77"
#   Timestamp: "2025-08-05T17:01:20+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则)"
#   Quality_Check: "包初始化清晰，版本信息明确，导出接口清楚"
# }}
# {{START_MODIFICATIONS}}
"""
FastMCP SSH Server - Python Implementation

A Model Context Protocol (MCP) server for SSH operations using FastMCP framework.
This is a Python reimplementation of the TypeScript ssh-mcp-server project,
providing complete API compatibility while leveraging Python's ecosystem advantages.

Features:
- SSH command execution with security controls (whitelist/blacklist)
- File upload/download via SFTP
- Multi-server connection management
- FastMCP integration for seamless AI tool integration
- Full compatibility with TypeScript version API
"""

__version__ = "0.1.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"

# Core modules for public API
from . import cli, models, server, ssh_manager, tools

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "models",
    "server",
    "ssh_manager",
    "cli",
    "tools",
]
# {{END_MODIFICATIONS}}
