"""
FastMCP SSH Tools v2 - Best Practices Implementation

This module contains the optimized implementation of SSH MCP tools using
FastMCP best practices including:
- Direct decorator pattern instead of registration functions
- Context dependency injection for logging and progress reporting
- Rich tool metadata with annotations, tags, and meta information
- Global state management through singleton pattern
- Enhanced error handling and structured logging

Available tools:
- execute-command: Execute SSH commands with progress reporting
- upload: Upload files via SFTP with structured logging
- download: Download files via SFTP with progress tracking
- list-servers: List SSH server configurations with status
"""

from .ssh_tools import initialize_server, mcp

__all__ = ["mcp", "initialize_server"]
