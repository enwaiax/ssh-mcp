#!/usr/bin/env python3
"""
FastMCP SSH Tools v2 - Best Practices Implementation

This module implements SSH MCP tools using FastMCP best practices:
- Direct @mcp.tool decorators instead of registration functions
- Context dependency injection for logging, progress reporting, and state management
- Rich tool metadata with ToolAnnotations, tags, and meta information
- Global SSH manager access pattern
- Enhanced error handling with structured logging
- 100% API compatibility with v1 implementation

Tools implemented:
- execute-command: Execute SSH commands on remote servers
- upload: Upload files to remote servers via SFTP
- download: Download files from remote servers via SFTP
- list-servers: List all configured SSH server connections

Author: AI Assistant
Version: 2.0.0
"""

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations

from ...ssh_manager import SSHConnectionManager
from ...utils.error_handling import (
    MCPToolError,
    SFTPError,
    SSHConnectionError,
)

# Create MCP server instance with optimized configuration
mcp = FastMCP(
    name="ssh-mcp-server-v2",
    on_duplicate_tools="warn",  # Allow tool updates during development
    include_fastmcp_meta=True,  # Include FastMCP metadata for debugging
)

# Global SSH manager instance (set during server initialization)
_ssh_manager: SSHConnectionManager | None = None


def set_ssh_manager(ssh_manager: SSHConnectionManager) -> None:
    """
    Set the global SSH manager instance.

    Args:
        ssh_manager: SSH connection manager instance
    """
    global _ssh_manager
    _ssh_manager = ssh_manager


def get_ssh_manager() -> SSHConnectionManager:
    """
    Get the global SSH manager instance.

    Returns:
        SSH connection manager instance

    Raises:
        MCPToolError: If SSH manager is not initialized
    """
    if _ssh_manager is None:
        raise MCPToolError("SSH manager not initialized")
    return _ssh_manager


@mcp.tool(
    name="execute-command",
    description="Execute command on remote SSH server and return raw output exactly as if executed locally",
    annotations=ToolAnnotations(
        title="SSH Command Executor",
        readOnlyHint=False,  # Commands may modify the environment
        destructiveHint=True,  # Commands may be destructive
        idempotentHint=False,  # Commands may have different effects when repeated
        openWorldHint=True,  # Interacts with external SSH servers
    ),
    tags={"ssh", "remote", "command", "execution"},
    meta={
        "version": "2.0.0",
        "category": "remote-execution",
        "security_level": "high",
        "requires_connection": True,
    },
)
async def execute_command(
    cmdString: str,
    connectionName: str | None = None,
    ctx: Context | None = None,
) -> str:
    """
    Execute command on connected SSH server and get raw output.

    Returns command output exactly as if executed locally, preserving
    all formatting, whitespace, and special characters.

    Args:
        cmdString: Command to execute on the remote server
        connectionName: SSH connection name (optional, defaults to 'default')
        ctx: FastMCP context for logging and progress reporting

    Returns:
        Raw command output as string, or error message on failure

    Raises:
        SSHConnectionError: If connection fails or is not available
        MCPToolError: If SSH manager is not initialized
    """
    # Enhanced structured logging
    if ctx:
        await ctx.info(
            f"Executing SSH command: {cmdString}",
            extra={
                "connection": connectionName or "default",
                "command": cmdString,
                "command_length": len(cmdString),
                "operation": "execute-command",
            },
        )

    try:
        ssh_manager = get_ssh_manager()

        # Report progress: Starting connection
        if ctx:
            await ctx.report_progress(0, 100, "Connecting to SSH server")

        # Execute the command
        result = await ssh_manager.execute_command(cmdString, connectionName)

        # Report progress: Command completed
        if ctx:
            await ctx.report_progress(100, 100, "Command executed successfully")
            await ctx.debug(
                f"Command output received: {len(result)} characters",
                extra={
                    "output_length": len(result),
                    "output_preview": result[:100] if result else "",
                    "connection": connectionName or "default",
                },
            )

        # Return raw output exactly as received
        return result.strip() if result else ""

    except (SSHConnectionError, MCPToolError) as error:
        error_msg = f"Error: {str(error)}"
        if ctx:
            await ctx.error(
                f"SSH command execution failed: {error_msg}",
                extra={
                    "connection": connectionName or "default",
                    "command": cmdString,
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
            )
        return error_msg
    except Exception as error:
        error_msg = f"Error: {str(error)}"
        if ctx:
            await ctx.error(
                f"Unexpected error during command execution: {error_msg}",
                extra={
                    "connection": connectionName or "default",
                    "command": cmdString,
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
            )
        return error_msg


@mcp.tool(
    name="upload",
    description="Upload file to remote SSH server using SFTP with progress tracking",
    annotations=ToolAnnotations(
        title="SFTP File Upload",
        readOnlyHint=False,  # Upload modifies remote filesystem
        destructiveHint=False,  # Upload is generally safe
        idempotentHint=False,  # Repeated uploads may overwrite files
        openWorldHint=True,  # Interacts with external SSH servers
    ),
    tags={"ssh", "sftp", "upload", "file-transfer"},
    meta={
        "version": "2.0.0",
        "category": "file-operations",
        "security_level": "medium",
        "requires_connection": True,
    },
)
async def upload(
    localPath: str,
    remotePath: str,
    connectionName: str | None = None,
    ctx: Context | None = None,
) -> str:
    """
    Upload file to connected SSH server using SFTP.

    Args:
        localPath: Local file path to upload
        remotePath: Remote destination path
        connectionName: SSH connection name (optional, defaults to 'default')
        ctx: FastMCP context for logging and progress reporting

    Returns:
        Success message or error description

    Raises:
        SFTPError: If file transfer fails
        SSHConnectionError: If connection is not available
    """
    if ctx:
        await ctx.info(
            f"Starting file upload: {localPath} -> {remotePath}",
            extra={
                "local_path": localPath,
                "remote_path": remotePath,
                "connection": connectionName or "default",
                "operation": "upload",
            },
        )

    try:
        ssh_manager = get_ssh_manager()

        # Report progress: Starting upload
        if ctx:
            await ctx.report_progress(0, 100, "Starting file upload")

        # Perform the upload
        result = await ssh_manager.upload(localPath, remotePath, connectionName)

        # Report progress: Upload completed
        if ctx:
            await ctx.report_progress(100, 100, "Upload completed successfully")
            await ctx.info(
                "File upload completed successfully",
                extra={
                    "local_path": localPath,
                    "remote_path": remotePath,
                    "connection": connectionName or "default",
                    "result": result,
                },
            )

        return result.strip() if result else "Upload completed successfully"

    except (SFTPError, SSHConnectionError, MCPToolError) as error:
        error_msg = f"Upload error: {str(error)}"
        if ctx:
            await ctx.error(
                f"File upload failed: {error_msg}",
                extra={
                    "local_path": localPath,
                    "remote_path": remotePath,
                    "connection": connectionName or "default",
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
            )
        return error_msg
    except Exception as error:
        error_msg = f"Upload error: {str(error)}"
        if ctx:
            await ctx.error(
                f"Unexpected error during file upload: {error_msg}",
                extra={
                    "local_path": localPath,
                    "remote_path": remotePath,
                    "connection": connectionName or "default",
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
            )
        return error_msg


@mcp.tool(
    name="download",
    description="Download file from remote SSH server using SFTP with progress tracking",
    annotations=ToolAnnotations(
        title="SFTP File Download",
        readOnlyHint=True,  # Download doesn't modify remote environment
        destructiveHint=False,  # Download is safe operation
        idempotentHint=True,  # Repeated downloads should be idempotent
        openWorldHint=True,  # Interacts with external SSH servers
    ),
    tags={"ssh", "sftp", "download", "file-transfer"},
    meta={
        "version": "2.0.0",
        "category": "file-operations",
        "security_level": "low",
        "requires_connection": True,
    },
)
async def download(
    remotePath: str,
    localPath: str,
    connectionName: str | None = None,
    ctx: Context | None = None,
) -> str:
    """
    Download file from connected SSH server using SFTP.

    Args:
        remotePath: Remote file path to download
        localPath: Local destination path
        connectionName: SSH connection name (optional, defaults to 'default')
        ctx: FastMCP context for logging and progress reporting

    Returns:
        Success message or error description

    Raises:
        SFTPError: If file transfer fails
        SSHConnectionError: If connection is not available
    """
    if ctx:
        await ctx.info(
            f"Starting file download: {remotePath} -> {localPath}",
            extra={
                "remote_path": remotePath,
                "local_path": localPath,
                "connection": connectionName or "default",
                "operation": "download",
            },
        )

    try:
        ssh_manager = get_ssh_manager()

        # Report progress: Starting download
        if ctx:
            await ctx.report_progress(0, 100, "Starting file download")

        # Perform the download
        result = await ssh_manager.download(remotePath, localPath, connectionName)

        # Report progress: Download completed
        if ctx:
            await ctx.report_progress(100, 100, "Download completed successfully")
            await ctx.info(
                "File download completed successfully",
                extra={
                    "remote_path": remotePath,
                    "local_path": localPath,
                    "connection": connectionName or "default",
                    "result": result,
                },
            )

        return result.strip() if result else "Download completed successfully"

    except (SFTPError, SSHConnectionError, MCPToolError) as error:
        error_msg = f"Download error: {str(error)}"
        if ctx:
            await ctx.error(
                f"File download failed: {error_msg}",
                extra={
                    "remote_path": remotePath,
                    "local_path": localPath,
                    "connection": connectionName or "default",
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
            )
        return error_msg
    except Exception as error:
        error_msg = f"Download error: {str(error)}"
        if ctx:
            await ctx.error(
                f"Unexpected error during file download: {error_msg}",
                extra={
                    "remote_path": remotePath,
                    "local_path": localPath,
                    "connection": connectionName or "default",
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
            )
        return error_msg


@mcp.tool(
    name="list-servers",
    description="List all configured SSH server connections and their status",
    annotations=ToolAnnotations(
        title="SSH Server Status Monitor",
        readOnlyHint=True,  # Read-only operation
        destructiveHint=False,  # Safe operation
        idempotentHint=True,  # Idempotent operation
        openWorldHint=False,  # Doesn't interact with external systems, only queries internal state
    ),
    tags={"ssh", "status", "info", "monitoring"},
    meta={
        "version": "2.0.0",
        "category": "server-management",
        "security_level": "low",
        "requires_connection": False,
    },
)
async def list_servers(ctx: Context | None = None) -> str:
    """
    List all available SSH server configurations and their connection status.

    Returns a human-readable list of configured SSH servers with their status,
    formatted similar to command-line tools for consistency.

    Args:
        ctx: FastMCP context for logging

    Returns:
        Human-readable server status information

    Raises:
        MCPToolError: If SSH manager is not initialized
    """
    if ctx:
        await ctx.debug(
            "Listing SSH server configurations",
            extra={"operation": "list-servers"},
        )

    try:
        ssh_manager = get_ssh_manager()
        servers = ssh_manager.get_all_server_infos()

        if not servers:
            result = "No SSH servers configured."
        else:
            lines = ["SSH Server Configurations:"]
            lines.append("-" * 50)

            for server in servers:
                status = "🟢 Connected" if server.connected else "🔴 Disconnected"
                lines.append(f"Name: {server.name}")
                lines.append(f"Host: {server.host}:{server.port}")
                lines.append(f"User: {server.username}")
                lines.append(f"Status: {status}")
                lines.append("")  # Empty line separator

            result = "\n".join(lines).rstrip()

        if ctx:
            await ctx.debug(
                f"Listed {len(servers)} SSH server configurations",
                extra={
                    "server_count": len(servers),
                    "connected_count": sum(1 for s in servers if s.connected),
                    "operation": "list-servers",
                },
            )

        return result

    except MCPToolError as error:
        error_msg = f"Error: {str(error)}"
        if ctx:
            await ctx.error(
                f"Failed to list servers: {error_msg}",
                extra={
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "operation": "list-servers",
                },
            )
        return error_msg
    except Exception as error:
        error_msg = f"Error: {str(error)}"
        if ctx:
            await ctx.error(
                f"Unexpected error listing servers: {error_msg}",
                extra={
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "operation": "list-servers",
                },
            )
        return error_msg


async def initialize_server(ssh_configs) -> FastMCP:
    """
    Initialize SSH MCP server with best practices implementation.

    This function sets up the SSH connection manager and configures
    all SSH connections, then sets the global manager for tool access.

    Args:
        ssh_configs: SSH connection configuration dictionary

    Returns:
        Configured FastMCP server instance

    Raises:
        SSHConnectionError: If SSH initialization fails
    """
    # Initialize SSH connection manager
    ssh_manager = await SSHConnectionManager.get_instance()
    ssh_manager.set_config(ssh_configs)
    await ssh_manager.connect_all()

    # Set global SSH manager for tool access
    set_ssh_manager(ssh_manager)

    return mcp


# Export the MCP instance and initialization function
__all__ = ["mcp", "initialize_server"]
