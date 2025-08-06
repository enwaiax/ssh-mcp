#!/usr/bin/env python3
"""
优化的SSH MCP工具实现
使用FastMCP最佳实践：Context依赖注入、工具元数据、直接装饰器
"""

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations

# 创建MCP服务器实例
mcp = FastMCP("SSH-MCP-Server-Optimized")

# 全局SSH管理器（在服务器初始化时设置）
_ssh_manager = None


def set_ssh_manager(ssh_manager):
    """设置全局SSH管理器实例"""
    global _ssh_manager
    _ssh_manager = ssh_manager


def get_ssh_manager():
    """获取SSH管理器实例"""
    return _ssh_manager


@mcp.tool(
    name="execute-command",
    description="Execute command on remote SSH server and return raw output",
    annotations=ToolAnnotations(
        title="SSH Command Executor",
        readOnlyHint=False,  # 命令可能修改环境
        destructiveHint=True,  # 命令可能具有破坏性
        idempotentHint=False,  # 命令重复执行可能有不同效果
        openWorldHint=True,  # 与外部SSH服务器交互
    ),
    tags={"ssh", "remote", "command"},
    meta={"version": "2.0", "category": "remote-execution"},
)
async def execute_command(
    cmdString: str,
    connectionName: str | None = None,
    ctx: Context = None,  # Context依赖注入
):
    """
    Execute command on connected SSH server and get output result.

    Returns raw command output exactly as if executed locally.

    Args:
        cmdString: Command to execute
        connectionName: SSH connection name (optional, default is 'default')
        ctx: FastMCP context for logging and progress reporting
    """
    # 使用Context进行日志记录
    if ctx:
        await ctx.info(
            f"Executing command: {cmdString}",
            extra={"connection": connectionName or "default", "command": cmdString},
        )

    try:
        ssh_manager = get_ssh_manager()
        if not ssh_manager:
            raise Exception("SSH manager not initialized")

        # 报告进度
        if ctx:
            await ctx.report_progress(0, 100, "Connecting to SSH server")

        result = await ssh_manager.execute_command(cmdString, connectionName)

        # 报告完成
        if ctx:
            await ctx.report_progress(100, 100, "Command executed successfully")
            await ctx.debug(f"Command output length: {len(result)} characters")

        return result.strip() if result else ""

    except Exception as error:
        error_msg = f"Error: {str(error)}"
        if ctx:
            await ctx.error(
                f"Command execution failed: {error_msg}",
                extra={
                    "connection": connectionName or "default",
                    "command": cmdString,
                    "error": str(error),
                },
            )
        return error_msg


@mcp.tool(
    name="upload",
    description="Upload file to remote SSH server using SFTP",
    annotations=ToolAnnotations(
        title="SFTP File Upload",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
    tags={"ssh", "sftp", "upload", "file-transfer"},
    meta={"version": "2.0", "category": "file-operations"},
)
async def upload_file(
    localPath: str,
    remotePath: str,
    connectionName: str | None = None,
    ctx: Context = None,
):
    """
    Upload file to connected SSH server using SFTP.

    Args:
        localPath: Local file path to upload
        remotePath: Remote destination path
        connectionName: SSH connection name (optional, default is 'default')
        ctx: FastMCP context for logging and progress reporting
    """
    if ctx:
        await ctx.info(
            f"Uploading {localPath} to {remotePath}",
            extra={
                "local_path": localPath,
                "remote_path": remotePath,
                "connection": connectionName or "default",
            },
        )

    try:
        ssh_manager = get_ssh_manager()
        if not ssh_manager:
            raise Exception("SSH manager not initialized")

        if ctx:
            await ctx.report_progress(0, 100, "Starting file upload")

        result = await ssh_manager.upload(localPath, remotePath, connectionName)

        if ctx:
            await ctx.report_progress(100, 100, "Upload completed")
            await ctx.info("File upload successful")

        return result.strip() if result else "Upload completed successfully"

    except Exception as error:
        error_msg = f"Upload error: {str(error)}"
        if ctx:
            await ctx.error(
                f"File upload failed: {error_msg}",
                extra={
                    "local_path": localPath,
                    "remote_path": remotePath,
                    "connection": connectionName or "default",
                    "error": str(error),
                },
            )
        return error_msg


@mcp.tool(
    name="download",
    description="Download file from remote SSH server using SFTP",
    annotations=ToolAnnotations(
        title="SFTP File Download",
        readOnlyHint=True,  # 下载不修改远程环境
        destructiveHint=False,
        idempotentHint=True,  # 重复下载相同文件应该幂等
        openWorldHint=True,
    ),
    tags={"ssh", "sftp", "download", "file-transfer"},
    meta={"version": "2.0", "category": "file-operations"},
)
async def download_file(
    remotePath: str,
    localPath: str,
    connectionName: str | None = None,
    ctx: Context = None,
):
    """
    Download file from connected SSH server using SFTP.

    Args:
        remotePath: Remote file path to download
        localPath: Local destination path
        connectionName: SSH connection name (optional, default is 'default')
        ctx: FastMCP context for logging and progress reporting
    """
    if ctx:
        await ctx.info(
            f"Downloading {remotePath} to {localPath}",
            extra={
                "remote_path": remotePath,
                "local_path": localPath,
                "connection": connectionName or "default",
            },
        )

    try:
        ssh_manager = get_ssh_manager()
        if not ssh_manager:
            raise Exception("SSH manager not initialized")

        if ctx:
            await ctx.report_progress(0, 100, "Starting file download")

        result = await ssh_manager.download(remotePath, localPath, connectionName)

        if ctx:
            await ctx.report_progress(100, 100, "Download completed")
            await ctx.info("File download successful")

        return result.strip() if result else "Download completed successfully"

    except Exception as error:
        error_msg = f"Download error: {str(error)}"
        if ctx:
            await ctx.error(
                f"File download failed: {error_msg}",
                extra={
                    "remote_path": remotePath,
                    "local_path": localPath,
                    "connection": connectionName or "default",
                    "error": str(error),
                },
            )
        return error_msg


@mcp.tool(
    name="list-servers",
    description="List all configured SSH server connections and their status",
    annotations=ToolAnnotations(
        title="SSH Server Status",
        readOnlyHint=True,  # 只读操作
        destructiveHint=False,
        idempotentHint=True,  # 幂等操作
        openWorldHint=False,  # 不与外部交互，只查询内部状态
    ),
    tags={"ssh", "status", "info"},
    meta={"version": "2.0", "category": "server-management"},
)
async def list_servers(ctx: Context = None):
    """
    List all available SSH server configurations and their connection status.

    Returns a human-readable list of configured SSH servers with their status.

    Args:
        ctx: FastMCP context for logging
    """
    if ctx:
        await ctx.debug("Listing SSH server configurations")

    try:
        ssh_manager = get_ssh_manager()
        if not ssh_manager:
            return "No SSH manager initialized"

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
                lines.append("")  # 空行分隔

            result = "\n".join(lines).rstrip()

        if ctx:
            await ctx.debug(f"Listed {len(servers)} SSH server configurations")

        return result

    except Exception as error:
        error_msg = f"Error: {str(error)}"
        if ctx:
            await ctx.error(f"Failed to list servers: {error_msg}")
        return error_msg


# 服务器初始化函数
async def initialize_server(ssh_configs):
    """
    初始化SSH MCP服务器

    Args:
        ssh_configs: SSH连接配置字典
    """
    from python_src.python_ssh_mcp.ssh_manager import SSHConnectionManager

    # 初始化SSH管理器
    ssh_manager = await SSHConnectionManager.get_instance()
    ssh_manager.set_config(ssh_configs)
    await ssh_manager.connect_all()

    # 设置全局SSH管理器
    set_ssh_manager(ssh_manager)

    return mcp


# 导出MCP实例和初始化函数
__all__ = ["mcp", "initialize_server"]
