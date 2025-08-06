# {{RIPER-5:
#   Action: "Modified"
#   Task_ID: "71577b93-1fcd-4cf4-95d9-c78745b3b9bb"
#   Timestamp: "2025-08-06T22:40:08+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + v2架构统一"
#   Quality_Check: "移除v1导入，指向v2实现，简化架构"
# }}
# {{START_MODIFICATIONS}}
"""
SSH MCP Tools Module

This module provides the unified v2 implementation of SSH MCP tools using
FastMCP best practices including:
- Direct decorator pattern with automatic registration
- Context dependency injection for logging and progress reporting
- Rich tool metadata with annotations, tags, and meta information
- Enhanced error handling and structured logging

Available tools:
- execute-command: Execute SSH commands with progress reporting
- upload: Upload files via SFTP with structured logging
- download: Download files via SFTP with progress tracking
- list-servers: List SSH server configurations with status

The v2 implementation is now the unified standard, providing enhanced
features while maintaining 100% API compatibility.
"""

# Import v2 tools implementation
from .v2 import initialize_server, mcp

__all__ = ["mcp", "initialize_server"]
# {{END_MODIFICATIONS}}
