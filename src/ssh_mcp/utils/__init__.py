# {{RIPER-5:
#   Action: "Modified"
#   Task_ID: "0c8ff7f7-b310-4a71-9e30-6719a9eda2b3"
#   Timestamp: "2025-08-05T20:30:51+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + 高内聚低耦合"
#   Quality_Check: "完整导出日志系统和错误处理工具，提供统一接口"
# }}
# {{START_MODIFICATIONS}}
"""
Utilities Module

This module contains utility functions and classes used throughout the application.
Includes logging, error handling, and other common functionality.

Available utilities:
- Logger: Unified logging system with structured logging
- Error handling: Standardized error processing and reporting
- Setup functions: Configuration and initialization utilities
"""

# Import all utility functions and classes
from .error_handling import (
    ConfigurationError,
    ErrorHandler,
    MCPToolError,
    SFTPError,
    SSHAuthenticationError,
    SSHCommandError,
    SSHConnectionError,
    SSHMCPError,
    handle_errors,
    safe_execute,
)
from .logger import Logger, get_logger, setup_logger

__all__ = [
    # Logging utilities
    "Logger",
    "get_logger",
    "setup_logger",
    # Error handling utilities
    "ErrorHandler",
    "SSHMCPError",
    "SSHConnectionError",
    "SSHAuthenticationError",
    "SSHCommandError",
    "SFTPError",
    "ConfigurationError",
    "MCPToolError",
    "handle_errors",
    "safe_execute",
]
# {{END_MODIFICATIONS}}
