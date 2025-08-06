# {{RIPER-5:
#   Action: "Modified"
#   Task_ID: "0c8ff7f7-b310-4a71-9e30-6719a9eda2b3"
#   Timestamp: "2025-08-05T20:41:07+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + DRY (不重复原则)"
#   Quality_Check: "重构为loguru实现，代码更简洁，功能更强大，保持TypeScript兼容性"
# }}
# {{START_MODIFICATIONS}}
"""
Logger Module (Loguru-based)

This module provides a unified logging system for the FastMCP SSH server.
Compatible with TypeScript version interface while leveraging loguru's powerful features.

Features:
- Structured logging with timestamps and levels (loguru-powered)
- Error handling with enhanced traceback support
- Automatic log rotation and retention
- Context information tracking with structured formatting
- Better performance and more intuitive API
- JSON serialization support for complex objects
"""

import sys
from pathlib import Path
from typing import Any

from loguru import logger

from ..models import LogLevel


class Logger:
    """
    Unified logger class providing structured logging and error handling.

    Now powered by loguru for better performance and developer experience.
    Compatible with TypeScript version interface while adding enhanced functionality.
    """

    _initialized = False
    _current_level = "INFO"

    @classmethod
    def setup_logging(
        cls,
        level: str | LogLevel = "info",
        format_string: str | None = None,
        log_file: str | Path | None = None,
        enable_console: bool = True,
    ) -> None:
        """
        Setup the logging system with loguru configuration.

        Args:
            level: Log level (info, debug, error, warning)
            format_string: Custom log format string (optional, loguru has great defaults)
            log_file: Optional file path for log output with automatic rotation
            enable_console: Whether to enable console output
        """
        # Convert level to uppercase for loguru
        level_map = {
            "debug": "DEBUG",
            "info": "INFO",
            "warning": "WARNING",
            "error": "ERROR",
            "critical": "CRITICAL",
        }

        if isinstance(level, str):
            cls._current_level = level_map.get(level.lower(), "INFO")
        else:
            cls._current_level = level_map.get(level, "INFO")

        # Remove all existing handlers
        logger.remove()

        # Default format - loguru's format is much more readable
        if format_string is None:
            format_string = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan> | "
                "<level>{message}</level>"
            )

        # Console handler
        if enable_console:
            logger.add(
                sys.stdout,
                format=format_string,
                level=cls._current_level,
                colorize=True,
                backtrace=True,
                diagnose=True,
            )

        # File handler with automatic rotation
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            logger.add(
                log_path,
                format=format_string,
                level=cls._current_level,
                rotation="100 MB",  # Automatic rotation
                retention="30 days",  # Keep logs for 30 days
                compression="zip",  # Compress old logs
                backtrace=True,
                diagnose=True,
                serialize=False,  # Can be set to True for JSON logs
            )

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str = "fastmcp-ssh-server"):
        """
        Get logger instance (simplified with loguru).

        Args:
            name: Logger name (used for context)

        Returns:
            Loguru logger bound with name context
        """
        if not cls._initialized:
            cls.setup_logging()

        # Return loguru logger bound with name context
        return logger.bind(name=name)

    @classmethod
    def log(
        cls,
        message: str,
        level: LogLevel = "info",
        context: dict[str, Any] | None = None,
        logger_name: str = "fastmcp-ssh-server",
    ) -> None:
        """
        Log a message with specified level.

        Compatible with TypeScript version interface but enhanced with loguru.

        Args:
            message: Log message (supports loguru's format strings)
            level: Log level (info, debug, error, warning)
            context: Additional context information (automatically structured)
            logger_name: Logger name for categorization
        """
        if not cls._initialized:
            cls.setup_logging()

        # Get logger with name binding
        bound_logger = logger.bind(name=logger_name)

        # If context is provided, bind it to the logger for structured logging
        if context:
            bound_logger = bound_logger.bind(**context)

        # Map LogLevel to loguru methods
        level_map = {
            "debug": bound_logger.debug,
            "info": bound_logger.info,
            "warning": bound_logger.warning,
            "error": bound_logger.error,
            "critical": bound_logger.critical,
        }

        # Get the log function and log the message
        log_func = level_map.get(level, bound_logger.info)
        log_func(message)

    @classmethod
    def handle_error(
        cls,
        error: Exception,
        prefix: str = "",
        exit_on_error: bool = False,
        include_traceback: bool = True,
        context: dict[str, Any] | None = None,
        logger_name: str = "fastmcp-ssh-server",
    ) -> str:
        """
        Handle error with logging and optional exit.

        Compatible with TypeScript version interface with loguru enhancements.

        Args:
            error: Exception to handle
            prefix: Error message prefix
            exit_on_error: Whether to exit the process
            include_traceback: Whether to include traceback (loguru handles this beautifully)
            context: Additional context information
            logger_name: Logger name for categorization

        Returns:
            Formatted error message
        """
        if not cls._initialized:
            cls.setup_logging()

        # Extract error information
        error_message = str(error)
        error_type = type(error).__name__

        # Build full message
        full_message = f"{prefix}: {error_message}" if prefix else error_message

        # Prepare context
        if context is None:
            context = {}
        context.update(
            {
                "error_type": error_type,
                "error_class": error.__class__.__module__
                + "."
                + error.__class__.__name__,
            }
        )

        # Get logger with enhanced context
        bound_logger = logger.bind(name=logger_name, **context)

        # Log the error with automatic traceback if requested
        if include_traceback and isinstance(error, Exception):
            # Loguru's exception logging is much better than standard library
            bound_logger.exception(full_message)
        else:
            bound_logger.error(full_message)

        # Exit if requested
        if exit_on_error:
            bound_logger.critical("Exiting due to critical error")
            sys.exit(1)

        return full_message

    @classmethod
    def debug(
        cls,
        message: str,
        context: dict[str, Any] | None = None,
        logger_name: str = "fastmcp-ssh-server",
    ) -> None:
        """Debug level logging."""
        cls.log(message, "debug", context, logger_name)

    @classmethod
    def info(
        cls,
        message: str,
        context: dict[str, Any] | None = None,
        logger_name: str = "fastmcp-ssh-server",
    ) -> None:
        """Info level logging."""
        cls.log(message, "info", context, logger_name)

    @classmethod
    def warning(
        cls,
        message: str,
        context: dict[str, Any] | None = None,
        logger_name: str = "fastmcp-ssh-server",
    ) -> None:
        """Warning level logging."""
        cls.log(message, "warning", context, logger_name)

    @classmethod
    def error(
        cls,
        message: str,
        context: dict[str, Any] | None = None,
        logger_name: str = "fastmcp-ssh-server",
    ) -> None:
        """Error level logging."""
        cls.log(message, "error", context, logger_name)

    @classmethod
    def critical(
        cls,
        message: str,
        context: dict[str, Any] | None = None,
        logger_name: str = "fastmcp-ssh-server",
    ) -> None:
        """Critical level logging."""
        cls.log(message, "critical", context, logger_name)


# Convenience functions for backward compatibility and ease of use
def setup_logger(
    level: str | LogLevel = "info",
    format_string: str | None = None,
    log_file: str | Path | None = None,
    enable_console: bool = True,
) -> None:
    """Setup the logging system - convenience function."""
    Logger.setup_logging(level, format_string, log_file, enable_console)


def get_logger(name: str = "fastmcp-ssh-server"):
    """Get logger instance - convenience function."""
    return Logger.get_logger(name)


# Export for easy imports
__all__ = [
    "Logger",
    "setup_logger",
    "get_logger",
]
# {{END_MODIFICATIONS}}
