# {{RIPER-5:
#   Action: "Modified"
#   Task_ID: "5bd0accf-48b9-42a7-ba37-2e87da1cce95"
#   Timestamp: "2025-08-05T20:12:54+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + 高内聚低耦合"
#   Quality_Check: "完整集成v2 SSHMCPServer，CLI解析，MCP工具注册，服务器启动，优雅错误处理"
# }}
# {{START_MODIFICATIONS}}
#!/usr/bin/env python3
"""
FastMCP SSH Server - Main Entry Point

This module provides the main entry point for the FastMCP SSH server.
It handles CLI argument parsing, server initialization, and startup.
Compatible with TypeScript version architecture.
"""

import asyncio
import sys
from typing import NoReturn

from . import SSHMCPServer, __version__
from .cli import app as cli_app
from .utils import Logger, setup_logger


def display_startup_banner(server_count: int) -> None:
    """
    Display startup banner with server information.

    Args:
        server_count: Number of configured SSH servers
    """
    print("\n" + "=" * 60)
    print("🚀 FastMCP SSH Server")
    print("=" * 60)
    print(f"📊 Version: {__version__}")
    print(f"🔧 SSH Connections: {server_count} configured")
    print("🛠️  MCP Tools: execute-command, upload, download, list-servers")
    print("🌐 Protocol: Model Context Protocol (MCP)")
    print("📡 Transport: stdin/stdout")
    print("=" * 60)
    print("✅ Server ready for MCP connections!")
    print("💡 Press Ctrl+C to shutdown gracefully")
    print()


async def start_server_with_config(ssh_configs):
    """
    Start the SSH MCP server with the given configuration.

    This function is called from the CLI command handler.

    Args:
        ssh_configs: SSH connection configuration map
    """
    ssh_server = None

    try:
        # Setup logging system
        setup_logger(level="info", enable_console=True)
        Logger.info(
            "FastMCP SSH Server starting",
            {"version": __version__, "servers": len(ssh_configs)},
        )

        # Display startup information
        display_startup_banner(len(ssh_configs))

        # Create SSH MCP server (unified implementation)
        server_name = "fastmcp-ssh-server"
        ssh_server = SSHMCPServer(server_name)
        Logger.info("SSH MCP Server instance created")
        print("🚀 Using unified SSH MCP tools implementation")

        # Initialize server with SSH configurations
        print("🔌 Initializing SSH connections...")
        Logger.info("Initializing SSH connections", {"server_count": len(ssh_configs)})
        await ssh_server.initialize(ssh_configs)
        print("✅ SSH connections initialized")
        Logger.info("SSH connections initialized successfully")

        print("🔧 Registering MCP tools...")
        Logger.info("MCP tools registration completed")
        print("✅ MCP tools registered")

        print("🚀 Starting FastMCP server...")
        Logger.info("Starting FastMCP server")

        # Start the FastMCP server (FastMCP handles signals internally)
        Logger.info("FastMCP server ready, starting main loop")
        await ssh_server.run()

    except KeyboardInterrupt:
        print("\n👋 Server shutdown requested")
        print("🔄 Cleaning up resources...")
        Logger.info("Server shutdown requested by user")

        # Graceful cleanup
        if ssh_server:
            try:
                Logger.info("Starting cleanup process")
                await ssh_server.cleanup()
                print("✅ Cleanup completed")
                Logger.info("Cleanup completed successfully")
            except Exception as cleanup_error:
                print(f"⚠️  Cleanup warning: {cleanup_error}")
                Logger.warning("Cleanup warning", {"error": str(cleanup_error)})

        print("👋 FastMCP SSH Server stopped gracefully")
        Logger.info("FastMCP SSH Server stopped gracefully")

        # Give a brief moment for final cleanup
        await asyncio.sleep(0.1)

    except Exception as e:
        print(f"\n❌ Server startup failed: {e}")
        Logger.handle_error(e, "Server startup failed", include_traceback=True)

        # Attempt cleanup on error
        if ssh_server:
            try:
                await ssh_server.cleanup()
                Logger.info("Error cleanup completed")
            except Exception as cleanup_error:
                Logger.debug(
                    "Error during error cleanup", {"error": str(cleanup_error)}
                )

        sys.exit(1)


def main() -> NoReturn:
    """
    Main entry point for the CLI application.

    This function is called when the package is executed as a script
    or when the 'fastmcp-ssh-server' command is run.

    Delegates to the Typer CLI application for argument parsing and execution.
    """
    try:
        # Run the Typer CLI application
        cli_app()
    except SystemExit as e:
        # Typer raises SystemExit on help, version, or other control flow
        sys.exit(e.code)
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        print("🔍 Please check your configuration and try again")
        # Try to log the fatal error if logging is set up
        try:
            Logger.critical("Fatal error in main", {"error": str(e)})
        except Exception:
            pass  # Logging may not be initialized yet
        sys.exit(1)

    # Should not reach here
    sys.exit(0)


if __name__ == "__main__":
    main()
# {{END_MODIFICATIONS}}
