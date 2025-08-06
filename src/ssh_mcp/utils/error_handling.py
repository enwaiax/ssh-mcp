# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "0c8ff7f7-b310-4a71-9e30-6719a9eda2b3"
#   Timestamp: "2025-08-05T20:30:51+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + DRY (不重复原则)"
#   Quality_Check: "统一错误处理机制，结构化错误信息，便于调试和监控"
# }}
# {{START_MODIFICATIONS}}
"""
Error Handling Module

This module provides standardized error handling utilities for the FastMCP SSH server.
Includes custom exceptions, error formatters, and recovery mechanisms.

Features:
- Custom exception hierarchy
- Error context tracking
- Standardized error responses
- Integration with logging system
"""

import functools
import traceback
from collections.abc import Callable
from typing import Any, TypeVar

from .logger import Logger

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])


class SSHMCPError(Exception):
    """Base exception for SSH MCP server errors."""

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.context = context or {}
        self.cause = cause

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for structured logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }


class SSHConnectionError(SSHMCPError):
    """SSH connection related errors."""

    pass


class SSHAuthenticationError(SSHMCPError):
    """SSH authentication related errors."""

    pass


class SSHCommandError(SSHMCPError):
    """SSH command execution related errors."""

    pass


class SFTPError(SSHMCPError):
    """SFTP operation related errors."""

    pass


class ConfigurationError(SSHMCPError):
    """Configuration related errors."""

    pass


class MCPToolError(SSHMCPError):
    """MCP tool operation related errors."""

    pass


class ErrorHandler:
    """
    Centralized error handling utilities.

    Provides methods for error formatting, logging, and recovery.
    """

    @staticmethod
    def format_error(
        error: Exception, include_traceback: bool = False, include_context: bool = True
    ) -> dict[str, Any]:
        """
        Format error for structured output.

        Args:
            error: Exception to format
            include_traceback: Whether to include full traceback
            include_context: Whether to include error context

        Returns:
            Formatted error dictionary
        """
        error_dict = {
            "error_type": type(error).__name__,
            "message": str(error),
            "timestamp": Logger.get_logger().handlers[0].formatter.formatTime(None)
            if Logger.get_logger().handlers
            else None,
        }

        # Add context if available and requested
        if include_context and isinstance(error, SSHMCPError):
            error_dict.update(error.to_dict())

        # Add traceback if requested
        if include_traceback:
            error_dict["traceback"] = traceback.format_exception(
                type(error), error, error.__traceback__
            )

        return error_dict

    @staticmethod
    def log_and_return_error(
        error: Exception,
        prefix: str = "",
        log_level: str = "error",
        include_traceback: bool = True,
    ) -> dict[str, Any]:
        """
        Log error and return formatted response.

        Args:
            error: Exception to handle
            prefix: Error message prefix
            log_level: Logging level to use
            include_traceback: Whether to include traceback

        Returns:
            Formatted error response
        """
        # Log the error
        Logger.handle_error(error, prefix=prefix, include_traceback=include_traceback)

        # Return formatted error for responses
        return {
            "isError": True,
            "error": ErrorHandler.format_error(error, include_traceback=False),
            "message": f"{prefix}: {str(error)}" if prefix else str(error),
        }

    @staticmethod
    def wrap_ssh_errors(error: Exception, operation: str) -> SSHMCPError:
        """
        Wrap generic exceptions into SSH-specific errors.

        Args:
            error: Original exception
            operation: Operation that failed

        Returns:
            SSH-specific exception
        """
        context = {"operation": operation}

        # Map common exceptions to SSH-specific ones
        if "connection" in str(error).lower() or "refused" in str(error).lower():
            return SSHConnectionError(
                f"SSH connection failed during {operation}", context, error
            )
        elif "auth" in str(error).lower() or "permission" in str(error).lower():
            return SSHAuthenticationError(
                f"SSH authentication failed during {operation}", context, error
            )
        elif "command" in str(error).lower() or "exec" in str(error).lower():
            return SSHCommandError(
                f"SSH command failed during {operation}", context, error
            )
        elif "sftp" in str(error).lower() or "file" in str(error).lower():
            return SFTPError(
                f"SFTP operation failed during {operation}", context, error
            )
        else:
            return SSHMCPError(
                f"SSH operation failed during {operation}", context, error
            )


def handle_errors(
    error_types: type[Exception] | tuple = Exception,
    default_response: dict[str, Any] | None = None,
    log_errors: bool = True,
    reraise: bool = False,
) -> Callable[[F], F]:
    """
    Decorator for automatic error handling.

    Args:
        error_types: Exception types to catch
        default_response: Default response on error
        log_errors: Whether to log caught errors
        reraise: Whether to reraise after handling

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except error_types as e:
                if log_errors:
                    Logger.handle_error(e, f"Error in {func.__name__}")

                if reraise:
                    raise

                return default_response or ErrorHandler.log_and_return_error(e)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_types as e:
                if log_errors:
                    Logger.handle_error(e, f"Error in {func.__name__}")

                if reraise:
                    raise

                return default_response or ErrorHandler.log_and_return_error(e)

        # Return appropriate wrapper based on function type
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def safe_execute(
    func: Callable, *args, default_value: Any = None, log_errors: bool = True, **kwargs
) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        *args: Function arguments
        default_value: Value to return on error
        log_errors: Whether to log errors
        **kwargs: Function keyword arguments

    Returns:
        Function result or default value on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            Logger.handle_error(e, f"Error in safe_execute of {func.__name__}")
        return default_value


# Export all error handling utilities
__all__ = [
    # Custom exceptions
    "SSHMCPError",
    "SSHConnectionError",
    "SSHAuthenticationError",
    "SSHCommandError",
    "SFTPError",
    "ConfigurationError",
    "MCPToolError",
    # Error handling utilities
    "ErrorHandler",
    # Decorators and functions
    "handle_errors",
    "safe_execute",
]
# {{END_MODIFICATIONS}}
